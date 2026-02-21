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
class VpnConcentrator:
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    transit_gateway_attachment_id: str = ""
    transit_gateway_id: str = ""
    type: str = ""
    vpn_concentrator_id: str = ""

    # Internal dependency tracking — not in API response
    vpn_connection_ids: List[str] = field(default_factory=list)  # tracks VpnConnection children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "tagSet": self.tag_set,
            "transitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "transitGatewayId": self.transit_gateway_id,
            "type": self.type,
            "vpnConcentratorId": self.vpn_concentrator_id,
        }

class VpnConcentrator_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.vpn_concentrators  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.transit_gateway_connect.get(params['transit_gateway_attachment_id']).vpn_concentrator_ids.append(new_id)
    #   Delete: self.state.transit_gateway_connect.get(resource.transit_gateway_attachment_id).vpn_concentrator_ids.remove(resource_id)
    #   Create: self.state.transit_gateways.get(params['transit_gateway_id']).vpn_concentrator_ids.append(new_id)
    #   Delete: self.state.transit_gateways.get(resource.transit_gateway_id).vpn_concentrator_ids.remove(resource_id)

    def _require_param(self, params: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
        value = params.get(name)
        if not value:
            return create_error_response("MissingParameter", f"Missing required parameter '{name}'.")
        return None

    def _get_or_error(self, resource_id: str) -> (Optional[VpnConcentrator], Optional[Dict[str, Any]]):
        resource = self.resources.get(resource_id)
        if not resource:
            return None, create_error_response(
                "InvalidVpnConcentratorID.NotFound",
                f"The ID '{resource_id}' does not exist",
            )
        return resource, None

    def CreateVpnConcentrator(self, params: Dict[str, Any]):
        """Creates a VPN concentrator that aggregates multiple VPN connections to a transit gateway."""

        error = self._require_param(params, "Type")
        if error:
            return error

        transit_gateway_id = params.get("TransitGatewayId") or ""
        if transit_gateway_id and transit_gateway_id not in self.state.transit_gateways:
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"The ID '{transit_gateway_id}' does not exist",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            resource_type = spec.get("ResourceType")
            if resource_type and resource_type not in {"vpn-concentrator", "vpnconcentrator"}:
                continue
            for tag in spec.get("Tags") or spec.get("Tag") or []:
                if tag:
                    tag_set.append(tag)

        vpn_concentrator_id = self._generate_id("vpn")
        resource = VpnConcentrator(
            state=ResourceState.AVAILABLE.value,
            tag_set=tag_set,
            transit_gateway_attachment_id="",
            transit_gateway_id=transit_gateway_id,
            type=params.get("Type") or "",
            vpn_concentrator_id=vpn_concentrator_id,
        )
        self.resources[vpn_concentrator_id] = resource

        if transit_gateway_id:
            parent = self.state.transit_gateways.get(transit_gateway_id)
            if parent and hasattr(parent, "vpn_concentrator_ids"):
                parent.vpn_concentrator_ids.append(vpn_concentrator_id)

        return {
            'vpnConcentrator': resource.to_dict(),
            }

    def DeleteVpnConcentrator(self, params: Dict[str, Any]):
        """Deletes the specified VPN concentrator."""

        error = self._require_param(params, "VpnConcentratorId")
        if error:
            return error

        vpn_concentrator_id = params.get("VpnConcentratorId")
        resource, error = self._get_or_error(vpn_concentrator_id)
        if error:
            return error

        if getattr(resource, "vpn_connection_ids", []):
            return create_error_response(
                "DependencyViolation",
                "VpnConcentrator has dependent VpnConnection(s) and cannot be deleted.",
            )

        parent = self.state.transit_gateway_connect.get(resource.transit_gateway_attachment_id)
        if parent and hasattr(parent, "vpn_concentrator_ids") and vpn_concentrator_id in parent.vpn_concentrator_ids:
            parent.vpn_concentrator_ids.remove(vpn_concentrator_id)

        parent = self.state.transit_gateways.get(resource.transit_gateway_id)
        if parent and hasattr(parent, "vpn_concentrator_ids") and vpn_concentrator_id in parent.vpn_concentrator_ids:
            parent.vpn_concentrator_ids.remove(vpn_concentrator_id)

        if vpn_concentrator_id in self.resources:
            del self.resources[vpn_concentrator_id]

        return {
            'return': True,
            }

    def DescribeVpnConcentrators(self, params: Dict[str, Any]):
        """Describes one or more of your VPN concentrators."""

        vpn_concentrator_ids = params.get("VpnConcentratorId.N", []) or []
        if vpn_concentrator_ids:
            missing = [vc_id for vc_id in vpn_concentrator_ids if vc_id not in self.resources]
            if missing:
                return create_error_response(
                    "InvalidVpnConcentratorID.NotFound",
                    f"The ID '{missing[0]}' does not exist",
                )
            resources = [self.resources[vc_id] for vc_id in vpn_concentrator_ids]
        else:
            resources = list(self.resources.values())

        filters = params.get("Filter.N", []) or []
        if filters:
            resources = apply_filters(resources, filters)

        max_results = int(params.get("MaxResults") or 100)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'vpnConcentratorSet': [resource.to_dict() for resource in resources],
            }

    def _generate_id(self, prefix: str = 'vpn') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class vpnconcentrator_RequestParser:
    @staticmethod
    def parse_create_vpn_concentrator_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
            "Type": get_scalar(md, "Type"),
        }

    @staticmethod
    def parse_delete_vpn_concentrator_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpnConcentratorId": get_scalar(md, "VpnConcentratorId"),
        }

    @staticmethod
    def parse_describe_vpn_concentrators_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VpnConcentratorId.N": get_indexed_list(md, "VpnConcentratorId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateVpnConcentrator": vpnconcentrator_RequestParser.parse_create_vpn_concentrator_request,
            "DeleteVpnConcentrator": vpnconcentrator_RequestParser.parse_delete_vpn_concentrator_request,
            "DescribeVpnConcentrators": vpnconcentrator_RequestParser.parse_describe_vpn_concentrators_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class vpnconcentrator_ResponseSerializer:
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
                xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_vpn_concentrator_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpnConcentratorResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConcentrator
        _vpnConcentrator_key = None
        if "vpnConcentrator" in data:
            _vpnConcentrator_key = "vpnConcentrator"
        elif "VpnConcentrator" in data:
            _vpnConcentrator_key = "VpnConcentrator"
        if _vpnConcentrator_key:
            param_data = data[_vpnConcentrator_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConcentrator>')
            xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpnConcentrator>')
        xml_parts.append(f'</CreateVpnConcentratorResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpn_concentrator_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpnConcentratorResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteVpnConcentratorResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpn_concentrators_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpnConcentratorsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize vpnConcentratorSet
        _vpnConcentratorSet_key = None
        if "vpnConcentratorSet" in data:
            _vpnConcentratorSet_key = "vpnConcentratorSet"
        elif "VpnConcentratorSet" in data:
            _vpnConcentratorSet_key = "VpnConcentratorSet"
        elif "VpnConcentrators" in data:
            _vpnConcentratorSet_key = "VpnConcentrators"
        if _vpnConcentratorSet_key:
            param_data = data[_vpnConcentratorSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpnConcentratorSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpnconcentrator_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpnConcentratorSet>')
            else:
                xml_parts.append(f'{indent_str}<vpnConcentratorSet/>')
        xml_parts.append(f'</DescribeVpnConcentratorsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateVpnConcentrator": vpnconcentrator_ResponseSerializer.serialize_create_vpn_concentrator_response,
            "DeleteVpnConcentrator": vpnconcentrator_ResponseSerializer.serialize_delete_vpn_concentrator_response,
            "DescribeVpnConcentrators": vpnconcentrator_ResponseSerializer.serialize_describe_vpn_concentrators_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

