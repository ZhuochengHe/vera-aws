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
class ServiceLink:
    configuration_state: str = ""
    local_address: str = ""
    outpost_arn: str = ""
    outpost_id: str = ""
    outpost_lag_id: str = ""
    owner_id: str = ""
    peer_address: str = ""
    peer_bgp_asn: int = 0
    service_link_virtual_interface_arn: str = ""
    service_link_virtual_interface_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    vlan: int = 0


    def to_dict(self) -> Dict[str, Any]:
        return {
            "configurationState": self.configuration_state,
            "localAddress": self.local_address,
            "outpostArn": self.outpost_arn,
            "outpostId": self.outpost_id,
            "outpostLagId": self.outpost_lag_id,
            "ownerId": self.owner_id,
            "peerAddress": self.peer_address,
            "peerBgpAsn": self.peer_bgp_asn,
            "serviceLinkVirtualInterfaceArn": self.service_link_virtual_interface_arn,
            "serviceLinkVirtualInterfaceId": self.service_link_virtual_interface_id,
            "tagSet": self.tag_set,
            "vlan": self.vlan,
        }

class ServiceLink_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.service_links  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.link_aggregation_groups.get(params['outpost_lag_id']).service_link_ids.append(new_id)
    #   Delete: self.state.link_aggregation_groups.get(resource.outpost_lag_id).service_link_ids.remove(resource_id)


    def DescribeServiceLinkVirtualInterfaces(self, params: Dict[str, Any]):
        """Describes the Outpost service link virtual interfaces."""

        interface_ids = params.get("ServiceLinkVirtualInterfaceId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if interface_ids:
            resources = []
            for interface_id in interface_ids:
                resource = self.resources.get(interface_id)
                if not resource:
                    return create_error_response(
                        "InvalidServiceLinkVirtualInterfaceId.NotFound",
                        f"The ID '{interface_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        service_links = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'nextToken': None,
            'serviceLinkVirtualInterfaceSet': service_links,
            }

    def _generate_id(self, prefix: str = 'service') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class servicelink_RequestParser:
    @staticmethod
    def parse_describe_service_link_virtual_interfaces_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ServiceLinkVirtualInterfaceId.N": get_indexed_list(md, "ServiceLinkVirtualInterfaceId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeServiceLinkVirtualInterfaces": servicelink_RequestParser.parse_describe_service_link_virtual_interfaces_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class servicelink_ResponseSerializer:
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
                xml_parts.extend(servicelink_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(servicelink_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(servicelink_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(servicelink_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(servicelink_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(servicelink_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_service_link_virtual_interfaces_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeServiceLinkVirtualInterfacesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize serviceLinkVirtualInterfaceSet
        _serviceLinkVirtualInterfaceSet_key = None
        if "serviceLinkVirtualInterfaceSet" in data:
            _serviceLinkVirtualInterfaceSet_key = "serviceLinkVirtualInterfaceSet"
        elif "ServiceLinkVirtualInterfaceSet" in data:
            _serviceLinkVirtualInterfaceSet_key = "ServiceLinkVirtualInterfaceSet"
        elif "ServiceLinkVirtualInterfaces" in data:
            _serviceLinkVirtualInterfaceSet_key = "ServiceLinkVirtualInterfaces"
        if _serviceLinkVirtualInterfaceSet_key:
            param_data = data[_serviceLinkVirtualInterfaceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<serviceLinkVirtualInterfaceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(servicelink_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</serviceLinkVirtualInterfaceSet>')
            else:
                xml_parts.append(f'{indent_str}<serviceLinkVirtualInterfaceSet/>')
        xml_parts.append(f'</DescribeServiceLinkVirtualInterfacesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeServiceLinkVirtualInterfaces": servicelink_ResponseSerializer.serialize_describe_service_link_virtual_interfaces_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

