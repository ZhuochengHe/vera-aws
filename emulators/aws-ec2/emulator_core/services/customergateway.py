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
class CustomerGateway:
    bgp_asn: str = ""
    bgp_asn_extended: str = ""
    certificate_arn: str = ""
    customer_gateway_id: str = ""
    device_name: str = ""
    ip_address: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    type: str = ""

    # Internal dependency tracking — not in API response
    vpn_connection_ids: List[str] = field(default_factory=list)  # tracks VpnConnection children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "bgpAsn": self.bgp_asn,
            "bgpAsnExtended": self.bgp_asn_extended,
            "certificateArn": self.certificate_arn,
            "customerGatewayId": self.customer_gateway_id,
            "deviceName": self.device_name,
            "ipAddress": self.ip_address,
            "state": self.state,
            "tagSet": self.tag_set,
            "type": self.type,
        }

class CustomerGateway_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.customer_gateways  # alias to shared store


    def CreateCustomerGateway(self, params: Dict[str, Any]):
        """Provides information to AWS about your customer gateway device. The
            customer gateway device is the appliance at your end of the VPN connection. You
            must provide the IP address of the customer gateway deviceâs external
            interface. The IP address must be static and"""

        gateway_type = params.get("Type")
        if not gateway_type:
            return create_error_response("MissingParameter", "Missing required parameter: Type")

        tag_set = []
        for spec in params.get("TagSpecification.N", []) or []:
            if spec.get("ResourceType") in (None, "", "customer-gateway"):
                tag_set.extend(spec.get("Tag", []) or [])

        customer_gateway_id = self._generate_id("cgw")
        ip_address = params.get("IpAddress") or params.get("PublicIp") or ""
        bgp_asn = params.get("BgpAsn")
        bgp_asn_extended = params.get("BgpAsnExtended")

        resource = CustomerGateway(
            bgp_asn="" if bgp_asn is None else str(bgp_asn),
            bgp_asn_extended="" if bgp_asn_extended is None else str(bgp_asn_extended),
            certificate_arn=params.get("CertificateArn") or "",
            customer_gateway_id=customer_gateway_id,
            device_name=params.get("DeviceName") or "",
            ip_address=ip_address,
            state="available",
            tag_set=tag_set,
            type=gateway_type,
        )
        self.resources[customer_gateway_id] = resource

        return {
            "customerGateway": resource.to_dict(),
        }

    def DeleteCustomerGateway(self, params: Dict[str, Any]):
        """Deletes the specified customer gateway. You must delete the VPN connection before you
            can delete the customer gateway."""

        customer_gateway_id = params.get("CustomerGatewayId")
        if not customer_gateway_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: CustomerGatewayId",
            )

        resource = self.resources.get(customer_gateway_id)
        if not resource:
            return create_error_response(
                "InvalidCustomerGatewayID.NotFound",
                f"The ID '{customer_gateway_id}' does not exist",
            )

        if getattr(resource, "vpn_connection_ids", []):
            return create_error_response(
                "DependencyViolation",
                "CustomerGateway has dependent VpnConnection(s) and cannot be deleted.",
            )

        self.resources.pop(customer_gateway_id, None)

        return {
            "return": True,
        }

    def DescribeCustomerGateways(self, params: Dict[str, Any]):
        """Describes one or more of your VPN customer gateways. For more information, seeAWS Site-to-Site VPNin theAWS Site-to-Site VPN
                User Guide."""

        gateway_ids = params.get("CustomerGatewayId.N", []) or []
        if gateway_ids:
            for gateway_id in gateway_ids:
                if gateway_id not in self.resources:
                    return create_error_response(
                        "InvalidCustomerGatewayID.NotFound",
                        f"The ID '{gateway_id}' does not exist",
                    )
            resources = [self.resources[gateway_id] for gateway_id in gateway_ids]
        else:
            resources = list(self.resources.values())

        filters = params.get("Filter.N", []) or []
        if filters:
            resources = apply_filters(resources, filters)

        return {
            "customerGatewaySet": [resource.to_dict() for resource in resources],
        }

    def _generate_id(self, prefix: str = 'cgw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class customergateway_RequestParser:
    @staticmethod
    def parse_create_customer_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "BgpAsn": get_int(md, "BgpAsn"),
            "BgpAsnExtended": get_int(md, "BgpAsnExtended"),
            "CertificateArn": get_scalar(md, "CertificateArn"),
            "DeviceName": get_scalar(md, "DeviceName"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpAddress": get_scalar(md, "IpAddress"),
            "PublicIp": get_scalar(md, "PublicIp"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Type": get_scalar(md, "Type"),
        }

    @staticmethod
    def parse_delete_customer_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CustomerGatewayId": get_scalar(md, "CustomerGatewayId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_customer_gateways_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CustomerGatewayId.N": get_indexed_list(md, "CustomerGatewayId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateCustomerGateway": customergateway_RequestParser.parse_create_customer_gateway_request,
            "DeleteCustomerGateway": customergateway_RequestParser.parse_delete_customer_gateway_request,
            "DescribeCustomerGateways": customergateway_RequestParser.parse_describe_customer_gateways_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class customergateway_ResponseSerializer:
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
                xml_parts.extend(customergateway_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(customergateway_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(customergateway_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(customergateway_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(customergateway_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(customergateway_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_customer_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateCustomerGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize customerGateway
        _customerGateway_key = None
        if "customerGateway" in data:
            _customerGateway_key = "customerGateway"
        elif "CustomerGateway" in data:
            _customerGateway_key = "CustomerGateway"
        if _customerGateway_key:
            param_data = data[_customerGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<customerGateway>')
            xml_parts.extend(customergateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</customerGateway>')
        xml_parts.append(f'</CreateCustomerGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_customer_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteCustomerGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteCustomerGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_customer_gateways_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCustomerGatewaysResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize customerGatewaySet
        _customerGatewaySet_key = None
        if "customerGatewaySet" in data:
            _customerGatewaySet_key = "customerGatewaySet"
        elif "CustomerGatewaySet" in data:
            _customerGatewaySet_key = "CustomerGatewaySet"
        elif "CustomerGateways" in data:
            _customerGatewaySet_key = "CustomerGateways"
        if _customerGatewaySet_key:
            param_data = data[_customerGatewaySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<customerGatewaySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(customergateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</customerGatewaySet>')
            else:
                xml_parts.append(f'{indent_str}<customerGatewaySet/>')
        xml_parts.append(f'</DescribeCustomerGatewaysResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateCustomerGateway": customergateway_ResponseSerializer.serialize_create_customer_gateway_response,
            "DeleteCustomerGateway": customergateway_ResponseSerializer.serialize_delete_customer_gateway_response,
            "DescribeCustomerGateways": customergateway_ResponseSerializer.serialize_describe_customer_gateways_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

