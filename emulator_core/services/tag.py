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
class Tag:
    key: str = ""
    resource_id: str = ""
    resource_type: str = ""
    value: str = ""

    # Internal dependency tracking — not in API response
    transit_gateway_multicast_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayMulticast children
    vpc_flow_log_ids: List[str] = field(default_factory=list)  # tracks VpcFlowLog children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "resourceId": self.resource_id,
            "resourceType": self.resource_type,
            "value": self.value,
        }

class Tag_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.tags  # alias to shared store

    def _require_params(self, params: Dict[str, Any], names: List[str]):
        for name in names:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _iter_resource_stores(self) -> List[Dict[str, Any]]:
        stores: List[Dict[str, Any]] = []
        for name, value in self.state.__dict__.items():
            if not isinstance(value, dict):
                continue
            if name == "tags":
                continue
            stores.append(value)
        return stores

    def _resource_exists(self, resource_id: str) -> bool:
        for store in self._iter_resource_stores():
            if resource_id in store:
                return True
        return False

    def _get_resource_type(self, resource_id: str) -> str:
        store_type_map = {
            "vpcs": "vpc",
            "subnets": "subnet",
            "instances": "instance",
            "volumes": "volume",
            "snapshots": "snapshot",
            "security_groups": "security-group",
            "route_tables": "route-table",
            "internet_gateways": "internet-gateway",
            "nat_gateways": "natgateway",
            "network_acls": "network-acl",
            "vpc_peering": "vpc-peering-connection",
            "vpc_endpoints": "vpc-endpoint",
            "elastic_network_interfaces": "network-interface",
            "key_pairs": "key-pair",
            "placement_groups": "placement-group",
            "customer_gateways": "customer-gateway",
            "vpn_connections": "vpn-connection",
            "transit_gateways": "transit-gateway",
        }
        for name, store in self.state.__dict__.items():
            if not isinstance(store, dict) or name == "tags":
                continue
            if resource_id in store:
                mapped = store_type_map.get(name)
                if mapped:
                    return mapped
                return name.rstrip("s").replace("_", "-")
        return ""


    def CreateTags(self, params: Dict[str, Any]):
        """Adds or overwrites only the specified tags for the specified Amazon EC2 resource or
         resources. When you specify an existing tag key, the value is overwritten with
         the new value. Each resource can have a maximum of 50 tags. Each tag consists of a key and
         optional value. Tag"""

        error = self._require_params(params, ["ResourceId.N", "Tag.N"])
        if error:
            return error

        resource_ids = params.get("ResourceId.N", []) or []
        tag_entries = params.get("Tag.N", []) or []

        for resource_id in resource_ids:
            if not self._resource_exists(resource_id):
                return create_error_response("InvalidResourceID.NotFound", f"The ID '{resource_id}' does not exist")

        for resource_id in resource_ids:
            resource_type = self._get_resource_type(resource_id)
            for tag_entry in tag_entries:
                if isinstance(tag_entry, dict):
                    key = tag_entry.get("Key") or tag_entry.get("key")
                    value = tag_entry.get("Value") or tag_entry.get("value") or ""
                else:
                    key = str(tag_entry) if tag_entry is not None else ""
                    value = ""

                if not key:
                    continue

                updated = False
                for resource in self.resources.values():
                    if resource.resource_id == resource_id and resource.key == key:
                        resource.value = value
                        if resource_type:
                            resource.resource_type = resource_type
                        updated = True
                if not updated:
                    tag_id = self._generate_id("tag")
                    self.resources[tag_id] = Tag(
                        key=key,
                        resource_id=resource_id,
                        resource_type=resource_type,
                        value=value,
                    )

        return {
            'return': True,
            }

    def DeleteTags(self, params: Dict[str, Any]):
        """Deletes the specified set of tags from the specified set of resources. To list the current tags, useDescribeTags. For more information about
         tags, seeTag
            your Amazon EC2 resourcesin theAmazon Elastic Compute Cloud User
            Guide."""

        error = self._require_params(params, ["ResourceId.N"])
        if error:
            return error

        resource_ids = params.get("ResourceId.N", []) or []
        tag_entries = params.get("Tag.N", []) or []

        for resource_id in resource_ids:
            if not self._resource_exists(resource_id):
                return create_error_response("InvalidResourceID.NotFound", f"The ID '{resource_id}' does not exist")

        keys_to_delete = set()
        key_value_pairs = set()
        for tag_entry in tag_entries:
            if isinstance(tag_entry, dict):
                key = tag_entry.get("Key") or tag_entry.get("key")
                value = tag_entry.get("Value") or tag_entry.get("value")
            else:
                key = str(tag_entry) if tag_entry is not None else ""
                value = None
            if not key:
                continue
            if value is None:
                keys_to_delete.add(key)
            else:
                key_value_pairs.add((key, value))

        to_delete = []
        for tag_id, tag in self.resources.items():
            if tag.resource_id not in resource_ids:
                continue
            if tag_entries:
                if tag.key in keys_to_delete:
                    to_delete.append(tag_id)
                elif (tag.key, tag.value) in key_value_pairs:
                    to_delete.append(tag_id)
            else:
                to_delete.append(tag_id)

        for tag_id in to_delete:
            resource = self.resources.get(tag_id)
            if not resource:
                continue
            if getattr(resource, "transit_gateway_multicast_ids", []):
                return create_error_response(
                    "DependencyViolation",
                    "Tag has dependent TransitGatewayMulticast(s) and cannot be deleted.",
                )
            if getattr(resource, "vpc_flow_log_ids", []):
                return create_error_response(
                    "DependencyViolation",
                    "Tag has dependent VpcFlowLog(s) and cannot be deleted.",
                )

        for tag_id in to_delete:
            self.resources.pop(tag_id, None)

        return {
            'return': True,
            }

    def DescribeTags(self, params: Dict[str, Any]):
        """Describes the specified tags for your EC2 resources. For more information about tags, seeTag your Amazon EC2 resourcesin theAmazon Elastic Compute Cloud User Guide. We strongly recommend using only paginated requests. Unpaginated requests are
            susceptible to throttling and timeouts."""

        tags = list(self.resources.values())
        filters = params.get("Filter.N", []) or []
        if filters:
            tags = apply_filters(tags, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token or 0)
        except (TypeError, ValueError):
            start_index = 0

        paged_tags = tags[start_index:start_index + max_results]
        response_next_token = None
        if start_index + max_results < len(tags):
            response_next_token = str(start_index + max_results)

        return {
            'nextToken': response_next_token,
            'tagSet': [tag.to_dict() for tag in paged_tags],
            }

    def _generate_id(self, prefix: str = 'resource') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class tag_RequestParser:
    @staticmethod
    def parse_create_tags_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ResourceId.N": get_indexed_list(md, "ResourceId"),
            "Tag.N": get_indexed_list(md, "Tag"),
        }

    @staticmethod
    def parse_delete_tags_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ResourceId.N": get_indexed_list(md, "ResourceId"),
            "Tag.N": get_indexed_list(md, "Tag"),
        }

    @staticmethod
    def parse_describe_tags_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateTags": tag_RequestParser.parse_create_tags_request,
            "DeleteTags": tag_RequestParser.parse_delete_tags_request,
            "DescribeTags": tag_RequestParser.parse_describe_tags_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class tag_ResponseSerializer:
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
                xml_parts.extend(tag_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(tag_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(tag_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(tag_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(tag_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(tag_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_tags_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTagsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CreateTagsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_tags_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTagsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteTagsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_tags_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTagsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize tagSet
        _tagSet_key = None
        if "tagSet" in data:
            _tagSet_key = "tagSet"
        elif "TagSet" in data:
            _tagSet_key = "TagSet"
        elif "Tags" in data:
            _tagSet_key = "Tags"
        if _tagSet_key:
            param_data = data[_tagSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<tagSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(tag_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        xml_parts.append(f'</DescribeTagsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateTags": tag_ResponseSerializer.serialize_create_tags_response,
            "DeleteTags": tag_ResponseSerializer.serialize_delete_tags_response,
            "DescribeTags": tag_ResponseSerializer.serialize_describe_tags_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

