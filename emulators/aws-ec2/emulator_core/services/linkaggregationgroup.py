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
class LinkAggregationGroup:
    local_gateway_virtual_interface_id_set: List[Any] = field(default_factory=list)
    outpost_arn: str = ""
    outpost_lag_id: str = ""
    owner_id: str = ""
    service_link_virtual_interface_id_set: List[Any] = field(default_factory=list)
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)

    # Internal dependency tracking — not in API response
    service_link_ids: List[str] = field(default_factory=list)  # tracks ServiceLink children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "localGatewayVirtualInterfaceIdSet": self.local_gateway_virtual_interface_id_set,
            "outpostArn": self.outpost_arn,
            "outpostLagId": self.outpost_lag_id,
            "ownerId": self.owner_id,
            "serviceLinkVirtualInterfaceIdSet": self.service_link_virtual_interface_id_set,
            "state": self.state,
            "tagSet": self.tag_set,
        }

class LinkAggregationGroup_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.link_aggregation_groups  # alias to shared store


    def DescribeOutpostLags(self, params: Dict[str, Any]):
        """Describes the Outposts link aggregation groups (LAGs). LAGs are only available for second-generation Outposts racks at this time."""

        outpost_lag_ids = params.get("OutpostLagId.N", []) or []
        if outpost_lag_ids:
            resources = []
            for outpost_lag_id in outpost_lag_ids:
                resource = self.resources.get(outpost_lag_id)
                if not resource:
                    return create_error_response(
                        "InvalidOutpostLagId.NotFound",
                        f"The ID '{outpost_lag_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        filters = params.get("Filter.N", []) or []
        if filters:
            resources = apply_filters(resources, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                return create_error_response(
                    "InvalidParameterValue",
                    f"Invalid NextToken '{next_token}'.",
                )

        paged_resources = resources[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(resources):
            new_next_token = str(start_index + max_results)

        return {
            "nextToken": new_next_token,
            "outpostLagSet": [resource.to_dict() for resource in paged_resources],
        }

    def _generate_id(self, prefix: str = 'outpost') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class linkaggregationgroup_RequestParser:
    @staticmethod
    def parse_describe_outpost_lags_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "OutpostLagId.N": get_indexed_list(md, "OutpostLagId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeOutpostLags": linkaggregationgroup_RequestParser.parse_describe_outpost_lags_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class linkaggregationgroup_ResponseSerializer:
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
                xml_parts.extend(linkaggregationgroup_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(linkaggregationgroup_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(linkaggregationgroup_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(linkaggregationgroup_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(linkaggregationgroup_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(linkaggregationgroup_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_outpost_lags_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeOutpostLagsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize outpostLagSet
        _outpostLagSet_key = None
        if "outpostLagSet" in data:
            _outpostLagSet_key = "outpostLagSet"
        elif "OutpostLagSet" in data:
            _outpostLagSet_key = "OutpostLagSet"
        elif "OutpostLags" in data:
            _outpostLagSet_key = "OutpostLags"
        if _outpostLagSet_key:
            param_data = data[_outpostLagSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<outpostLagSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(linkaggregationgroup_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</outpostLagSet>')
            else:
                xml_parts.append(f'{indent_str}<outpostLagSet/>')
        xml_parts.append(f'</DescribeOutpostLagsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeOutpostLags": linkaggregationgroup_ResponseSerializer.serialize_describe_outpost_lags_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

