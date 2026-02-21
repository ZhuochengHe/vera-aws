from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re
from ..utils import (get_scalar, get_int, get_indexed_list, parse_filters, apply_filters,
                    parse_tags, str2bool, esc, create_error_response,
                    is_error_response, serialize_error_response)
from ..state import EC2State

class ResourceState(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    RUNNING = 'running'
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    NONEXISTENT = 'non-existent'
    FAILED = 'failed'
    SHUTTING_DOWN = 'shutting-down'
    STOPPING = 'stopping'
    STARTING = 'starting'
    REBOOTING = 'rebooting'
    ATTACHED = 'attached'
    IN_USE = 'in-use'
    CREATING = 'creating'

class ErrorCode(Enum):
    INVALID_PARAMETER_VALUE = 'InvalidParameterValue'
    RESOURCE_NOT_FOUND = 'ResourceNotFound'
    INVALID_STATE_TRANSITION = 'InvalidStateTransition'
    DEPENDENCY_VIOLATION = 'DependencyViolation'

@dataclass
class VirtualPrivateGateway:
    amazon_side_asn: int = 0
    attachments: List[Any] = field(default_factory=list)
    availability_zone: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    type: str = ""
    vpn_gateway_id: str = ""

    # Internal dependency tracking — not in API response
    vpn_connection_ids: List[str] = field(default_factory=list)  # tracks VpnConnection children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "amazonSideAsn": self.amazon_side_asn,
            "attachments": self.attachments,
            "availabilityZone": self.availability_zone,
            "state": self.state,
            "tagSet": self.tag_set,
            "type": self.type,
            "vpnGatewayId": self.vpn_gateway_id,
        }

class VirtualPrivateGateway_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.virtual_private_gateways  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_gateway_or_error(self, vpn_gateway_id: str) -> (Optional[VirtualPrivateGateway], Optional[Dict[str, Any]]):
        resource = self.resources.get(vpn_gateway_id)
        if not resource:
            return None, create_error_response("InvalidVpnGatewayID.NotFound", f"The ID '{vpn_gateway_id}' does not exist")
        return resource, None

    def _get_vpc_or_error(self, vpc_id: str) -> (Optional[Any], Optional[Dict[str, Any]]):
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return None, create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")
        return vpc, None

    def _find_attachment(self, resource: VirtualPrivateGateway, vpc_id: str) -> Optional[Dict[str, Any]]:
        for attachment in resource.attachments:
            if attachment.get("vpcId") == vpc_id:
                return attachment
        return None


    def AttachVpnGateway(self, params: Dict[str, Any]):
        """Attaches an available virtual private gateway to a VPC. You can attach one virtual private
            gateway to one VPC at a time. For more information, seeAWS Site-to-Site VPNin theAWS Site-to-Site VPN
                User Guide."""

        error = self._require_params(params, ["VpcId", "VpnGatewayId"])
        if error:
            return error

        vpc_id = params.get("VpcId")
        vpc, error = self._get_vpc_or_error(vpc_id)
        if error:
            return error

        vpn_gateway_id = params.get("VpnGatewayId")
        resource, error = self._get_gateway_or_error(vpn_gateway_id)
        if error:
            return error

        attached_vpc_id = None
        for attachment in resource.attachments:
            if attachment.get("state") != "detached":
                attached_vpc_id = attachment.get("vpcId")
                break
        if attached_vpc_id and attached_vpc_id != vpc_id:
            return create_error_response(
                "DependencyViolation",
                "VpnGateway is already attached to another VPC.",
            )

        attachment = self._find_attachment(resource, vpc_id)
        if attachment:
            attachment["state"] = "available"
        else:
            attachment = {"state": "available", "vpcId": vpc_id}
            resource.attachments.append(attachment)

        return {
            'attachment': {
                'state': attachment.get("state"),
                'vpcId': attachment.get("vpcId"),
                },
            }

    def CreateVpnGateway(self, params: Dict[str, Any]):
        """Creates a virtual private gateway. A virtual private gateway is the endpoint on the
            VPC side of your VPN connection. You can create a virtual private gateway before
            creating the VPC itself. For more information, seeAWS Site-to-Site VPNin theAWS Site-to-Site VPN
              """

        error = self._require_params(params, ["Type"])
        if error:
            return error

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "vpn-gateway":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        vpn_gateway_id = self._generate_id("vpn")
        resource = VirtualPrivateGateway(
            amazon_side_asn=int(params.get("AmazonSideAsn") or 0),
            attachments=[],
            availability_zone=params.get("AvailabilityZone") or "",
            state="available",
            tag_set=tag_set,
            type=params.get("Type") or "",
            vpn_gateway_id=vpn_gateway_id,
        )
        self.resources[vpn_gateway_id] = resource

        return {
            'vpnGateway': resource.to_dict(),
            }

    def DeleteVpnGateway(self, params: Dict[str, Any]):
        """Deletes the specified virtual private gateway. You must first detach the virtual
            private gateway from the VPC. Note that you don't need to delete the virtual private
            gateway if you plan to delete and recreate the VPN connection between your VPC and your
            network."""

        error = self._require_params(params, ["VpnGatewayId"])
        if error:
            return error

        vpn_gateway_id = params.get("VpnGatewayId")
        resource, error = self._get_gateway_or_error(vpn_gateway_id)
        if error:
            return error

        if getattr(resource, "vpn_connection_ids", []):
            return create_error_response(
                "DependencyViolation",
                "VirtualPrivateGateway has dependent VpnConnection(s) and cannot be deleted.",
            )

        for attachment in resource.attachments:
            if attachment.get("state") != "detached":
                return create_error_response(
                    "DependencyViolation",
                    "VpnGateway must be detached before deletion.",
                )

        self.resources.pop(vpn_gateway_id, None)

        return {
            'return': True,
            }

    def DescribeVpnGateways(self, params: Dict[str, Any]):
        """Describes one or more of your virtual private gateways. For more information, seeAWS Site-to-Site VPNin theAWS Site-to-Site VPN
                User Guide."""

        vpn_gateway_ids = params.get("VpnGatewayId.N", []) or []
        if vpn_gateway_ids:
            resources: List[VirtualPrivateGateway] = []
            for vpn_gateway_id in vpn_gateway_ids:
                resource, error = self._get_gateway_or_error(vpn_gateway_id)
                if error:
                    return error
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []) or [])
        return {
            'vpnGatewaySet': [resource.to_dict() for resource in resources],
            }

    def DetachVpnGateway(self, params: Dict[str, Any]):
        """Detaches a virtual private gateway from a VPC. You do this if you're planning to turn
            off the VPC and not use it anymore. You can confirm a virtual private gateway has been
            completely detached from a VPC by describing the virtual private gateway (any
            attachments t"""

        error = self._require_params(params, ["VpcId", "VpnGatewayId"])
        if error:
            return error

        vpc_id = params.get("VpcId")
        vpc, error = self._get_vpc_or_error(vpc_id)
        if error:
            return error

        vpn_gateway_id = params.get("VpnGatewayId")
        resource, error = self._get_gateway_or_error(vpn_gateway_id)
        if error:
            return error

        attachment = self._find_attachment(resource, vpc_id)
        if not attachment or attachment.get("state") == "detached":
            return create_error_response(
                "DependencyViolation",
                "VpnGateway is not attached to the specified VPC.",
            )

        attachment["state"] = "detached"

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'vpn') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class virtualprivategateway_RequestParser:
    @staticmethod
    def parse_attach_vpn_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpcId": get_scalar(md, "VpcId"),
            "VpnGatewayId": get_scalar(md, "VpnGatewayId"),
        }

    @staticmethod
    def parse_create_vpn_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AmazonSideAsn": get_int(md, "AmazonSideAsn"),
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Type": get_scalar(md, "Type"),
        }

    @staticmethod
    def parse_delete_vpn_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpnGatewayId": get_scalar(md, "VpnGatewayId"),
        }

    @staticmethod
    def parse_describe_vpn_gateways_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "VpnGatewayId.N": get_indexed_list(md, "VpnGatewayId"),
        }

    @staticmethod
    def parse_detach_vpn_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpcId": get_scalar(md, "VpcId"),
            "VpnGatewayId": get_scalar(md, "VpnGatewayId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AttachVpnGateway": virtualprivategateway_RequestParser.parse_attach_vpn_gateway_request,
            "CreateVpnGateway": virtualprivategateway_RequestParser.parse_create_vpn_gateway_request,
            "DeleteVpnGateway": virtualprivategateway_RequestParser.parse_delete_vpn_gateway_request,
            "DescribeVpnGateways": virtualprivategateway_RequestParser.parse_describe_vpn_gateways_request,
            "DetachVpnGateway": virtualprivategateway_RequestParser.parse_detach_vpn_gateway_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class virtualprivategateway_ResponseSerializer:
    @staticmethod
    def _serialize_dict_to_xml(d: Dict[str, Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a dictionary to XML elements."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def _serialize_list_to_xml(lst: List[Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a list to XML elements with <tagName> wrapper and <item> children."""
        xml_parts = []
        indent = '    ' * indent_level
        xml_parts.append(f'{indent}<{tag_name}>')
        for item in lst:
            if isinstance(item, dict):
                xml_parts.append(f'{indent}    <item>')
                xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
            else:
                xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
        xml_parts.append(f'{indent}</{tag_name}>')
        return xml_parts

    @staticmethod
    def _serialize_nested_fields(d: Dict[str, Any], indent_level: int) -> List[str]:
        """Serialize nested fields from a dictionary."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
                        xml_parts.append(f'{indent}    </item>')
                    else:
                        xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def serialize_attach_vpn_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AttachVpnGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize attachment
        _attachment_key = None
        if "attachment" in data:
            _attachment_key = "attachment"
        elif "Attachment" in data:
            _attachment_key = "Attachment"
        if _attachment_key:
            param_data = data[_attachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<attachment>')
            xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</attachment>')
        xml_parts.append(f'</AttachVpnGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_vpn_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpnGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnGateway
        _vpnGateway_key = None
        if "vpnGateway" in data:
            _vpnGateway_key = "vpnGateway"
        elif "VpnGateway" in data:
            _vpnGateway_key = "VpnGateway"
        if _vpnGateway_key:
            param_data = data[_vpnGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnGateway>')
            xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpnGateway>')
        xml_parts.append(f'</CreateVpnGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpn_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpnGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</DeleteVpnGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpn_gateways_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpnGatewaysResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnGatewaySet
        _vpnGatewaySet_key = None
        if "vpnGatewaySet" in data:
            _vpnGatewaySet_key = "vpnGatewaySet"
        elif "VpnGatewaySet" in data:
            _vpnGatewaySet_key = "VpnGatewaySet"
        elif "VpnGateways" in data:
            _vpnGatewaySet_key = "VpnGateways"
        if _vpnGatewaySet_key:
            param_data = data[_vpnGatewaySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpnGatewaySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(virtualprivategateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpnGatewaySet>')
            else:
                xml_parts.append(f'{indent_str}<vpnGatewaySet/>')
        xml_parts.append(f'</DescribeVpnGatewaysResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_detach_vpn_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DetachVpnGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</DetachVpnGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AttachVpnGateway": virtualprivategateway_ResponseSerializer.serialize_attach_vpn_gateway_response,
            "CreateVpnGateway": virtualprivategateway_ResponseSerializer.serialize_create_vpn_gateway_response,
            "DeleteVpnGateway": virtualprivategateway_ResponseSerializer.serialize_delete_vpn_gateway_response,
            "DescribeVpnGateways": virtualprivategateway_ResponseSerializer.serialize_describe_vpn_gateways_response,
            "DetachVpnGateway": virtualprivategateway_ResponseSerializer.serialize_detach_vpn_gateway_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

