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
class ResourceID:
    deadline: str = ""
    resource: str = ""
    use_long_ids: bool = False
    principal_arn: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deadline": self.deadline,
            "resource": self.resource,
            "useLongIds": self.use_long_ids,
        }

class ResourceID_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.resource_ids  # alias to shared store

    def _filter_resources(self, principal_arn: Optional[str] = None, resources: Optional[List[str]] = None) -> List[ResourceID]:
        items = list(self.resources.values())
        if principal_arn is not None:
            items = [item for item in items if item.principal_arn == principal_arn]
        if resources:
            resource_set = set(resources)
            items = [item for item in items if item.resource in resource_set]
        return items

    def DescribeAggregateIdFormat(self, params: Dict[str, Any]):
        """Describes the longer ID format settings for all resource types in a specific
         Region. This request is useful for performing a quick audit to determine whether a
         specific Region is fully opted in for longer IDs (17-character IDs). This request only returns information about resource """

        status_items = self._filter_resources(principal_arn="")
        status_set = [item.to_dict() for item in status_items]
        use_long_ids_aggregated = bool(status_set) and all(item.use_long_ids for item in status_items)

        return {
            'statusSet': status_set,
            'useLongIdsAggregated': use_long_ids_aggregated,
            }

    def DescribeIdentityIdFormat(self, params: Dict[str, Any]):
        """Describes the ID format settings for resources for the specified IAM user, IAM role, or root
      user. For example, you can view the resource types that are enabled for longer IDs. This request only
      returns information about resource types whose ID formats can be modified; it does not return"""

        principal_arn = params.get("PrincipalArn")
        if not principal_arn:
            return create_error_response("MissingParameter", "The request must contain the parameter PrincipalArn")

        resource_filter = params.get("Resource")
        resources = [resource_filter] if resource_filter else None
        status_items = self._filter_resources(principal_arn=principal_arn, resources=resources)
        status_set = [item.to_dict() for item in status_items]

        return {
            'statusSet': status_set,
            }

    def DescribeIdFormat(self, params: Dict[str, Any]):
        """Describes the ID format settings for your resources on a per-Region basis, for example, to view which resource types are enabled for longer IDs. This request only returns information about resource types whose ID formats can be modified; it does not return information about other resource types. The"""

        resource_filter = params.get("Resource")
        resources = [resource_filter] if resource_filter else None
        status_items = self._filter_resources(principal_arn="", resources=resources)
        status_set = [item.to_dict() for item in status_items]

        return {
            'statusSet': status_set,
            }

    def DescribePrincipalIdFormat(self, params: Dict[str, Any]):
        """Describes the ID format settings for the root user and all IAM roles and IAM users
            that have explicitly specified a longer ID (17-character ID) preference. By default, all IAM roles and IAM users default to the same ID settings as the root user, unless they
            explicitly overrid"""

        resource_filters = params.get("Resource.N", [])
        resources = resource_filters or None
        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token) if next_token else 0
        except ValueError:
            start_index = 0

        principal_map: Dict[str, List[ResourceID]] = {}
        for item in self.resources.values():
            if resources and item.resource not in resources:
                continue
            principal_map.setdefault(item.principal_arn, []).append(item)

        principals = sorted(principal_map.keys())
        sliced = principals[start_index:start_index + max_results]
        principal_set = []
        for arn in sliced:
            status_set = [item.to_dict() for item in principal_map.get(arn, [])]
            principal_set.append({
                "arn": arn,
                "statusSet": status_set,
            })

        next_index = start_index + len(sliced)
        response_next_token = str(next_index) if next_index < len(principals) else None

        return {
            'nextToken': response_next_token,
            'principalSet': principal_set,
            }

    def ModifyIdentityIdFormat(self, params: Dict[str, Any]):
        """Modifies the ID format of a resource for a specified IAM user, IAM role, or the root
       user for an account; or all IAM users, IAM roles, and the root user for an account. You can
       specify that resources should receive longer IDs (17-character IDs) when they are created. This request can o"""

        principal_arn = params.get("PrincipalArn")
        if not principal_arn:
            return create_error_response("MissingParameter", "Missing required parameter: PrincipalArn")

        resource_name = params.get("Resource")
        if not resource_name:
            return create_error_response("MissingParameter", "Missing required parameter: Resource")

        if params.get("UseLongIds") is None:
            return create_error_response("MissingParameter", "Missing required parameter: UseLongIds")

        use_long_ids = str2bool(params.get("UseLongIds"))

        existing_items = self._filter_resources(principal_arn=principal_arn, resources=[resource_name])
        if existing_items:
            item = existing_items[0]
            item.use_long_ids = use_long_ids
        else:
            resource_id = self._generate_id("res")
            item = ResourceID(resource=resource_name, use_long_ids=use_long_ids, principal_arn=principal_arn)
            self.resources[resource_id] = item

        return {
            'return': True,
            }

    def ModifyIdFormat(self, params: Dict[str, Any]):
        """Modifies the ID format for the specified resource on a per-Region basis. You can
            specify that resources should receive longer IDs (17-character IDs) when they are
            created. This request can only be used to modify longer ID settings for resource types that
            are withi"""

        resource_name = params.get("Resource")
        if not resource_name:
            return create_error_response("MissingParameter", "Missing required parameter: Resource")

        if params.get("UseLongIds") is None:
            return create_error_response("MissingParameter", "Missing required parameter: UseLongIds")

        use_long_ids = str2bool(params.get("UseLongIds"))
        principal_arn = ""

        existing_items = self._filter_resources(principal_arn=principal_arn, resources=[resource_name])
        if existing_items:
            item = existing_items[0]
            item.use_long_ids = use_long_ids
        else:
            resource_id = self._generate_id("res")
            item = ResourceID(resource=resource_name, use_long_ids=use_long_ids, principal_arn=principal_arn)
            self.resources[resource_id] = item

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'res') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class resourceid_RequestParser:
    @staticmethod
    def parse_describe_aggregate_id_format_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_identity_id_format_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "PrincipalArn": get_scalar(md, "PrincipalArn"),
            "Resource": get_scalar(md, "Resource"),
        }

    @staticmethod
    def parse_describe_id_format_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Resource": get_scalar(md, "Resource"),
        }

    @staticmethod
    def parse_describe_principal_id_format_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "Resource.N": get_indexed_list(md, "Resource"),
        }

    @staticmethod
    def parse_modify_identity_id_format_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "PrincipalArn": get_scalar(md, "PrincipalArn"),
            "Resource": get_scalar(md, "Resource"),
            "UseLongIds": get_indexed_list(md, "UseLongIds"),
        }

    @staticmethod
    def parse_modify_id_format_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Resource": get_scalar(md, "Resource"),
            "UseLongIds": get_indexed_list(md, "UseLongIds"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeAggregateIdFormat": resourceid_RequestParser.parse_describe_aggregate_id_format_request,
            "DescribeIdentityIdFormat": resourceid_RequestParser.parse_describe_identity_id_format_request,
            "DescribeIdFormat": resourceid_RequestParser.parse_describe_id_format_request,
            "DescribePrincipalIdFormat": resourceid_RequestParser.parse_describe_principal_id_format_request,
            "ModifyIdentityIdFormat": resourceid_RequestParser.parse_modify_identity_id_format_request,
            "ModifyIdFormat": resourceid_RequestParser.parse_modify_id_format_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class resourceid_ResponseSerializer:
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
                xml_parts.extend(resourceid_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(resourceid_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(resourceid_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(resourceid_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(resourceid_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(resourceid_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_aggregate_id_format_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeAggregateIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize statusSet
        _statusSet_key = None
        if "statusSet" in data:
            _statusSet_key = "statusSet"
        elif "StatusSet" in data:
            _statusSet_key = "StatusSet"
        elif "Statuss" in data:
            _statusSet_key = "Statuss"
        if _statusSet_key:
            param_data = data[_statusSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourceid_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        # Serialize useLongIdsAggregated
        _useLongIdsAggregated_key = None
        if "useLongIdsAggregated" in data:
            _useLongIdsAggregated_key = "useLongIdsAggregated"
        elif "UseLongIdsAggregated" in data:
            _useLongIdsAggregated_key = "UseLongIdsAggregated"
        if _useLongIdsAggregated_key:
            param_data = data[_useLongIdsAggregated_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<useLongIdsAggregated>{esc(str(param_data))}</useLongIdsAggregated>')
        xml_parts.append(f'</DescribeAggregateIdFormatResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_identity_id_format_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIdentityIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize statusSet
        _statusSet_key = None
        if "statusSet" in data:
            _statusSet_key = "statusSet"
        elif "StatusSet" in data:
            _statusSet_key = "StatusSet"
        elif "Statuss" in data:
            _statusSet_key = "Statuss"
        if _statusSet_key:
            param_data = data[_statusSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourceid_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</DescribeIdentityIdFormatResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_id_format_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize statusSet
        _statusSet_key = None
        if "statusSet" in data:
            _statusSet_key = "statusSet"
        elif "StatusSet" in data:
            _statusSet_key = "StatusSet"
        elif "Statuss" in data:
            _statusSet_key = "Statuss"
        if _statusSet_key:
            param_data = data[_statusSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourceid_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</DescribeIdFormatResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_principal_id_format_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribePrincipalIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize principalSet
        _principalSet_key = None
        if "principalSet" in data:
            _principalSet_key = "principalSet"
        elif "PrincipalSet" in data:
            _principalSet_key = "PrincipalSet"
        elif "Principals" in data:
            _principalSet_key = "Principals"
        if _principalSet_key:
            param_data = data[_principalSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<principalSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourceid_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</principalSet>')
            else:
                xml_parts.append(f'{indent_str}<principalSet/>')
        xml_parts.append(f'</DescribePrincipalIdFormatResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_identity_id_format_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyIdentityIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyIdentityIdFormatResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_id_format_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyIdFormatResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyIdFormatResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeAggregateIdFormat": resourceid_ResponseSerializer.serialize_describe_aggregate_id_format_response,
            "DescribeIdentityIdFormat": resourceid_ResponseSerializer.serialize_describe_identity_id_format_response,
            "DescribeIdFormat": resourceid_ResponseSerializer.serialize_describe_id_format_response,
            "DescribePrincipalIdFormat": resourceid_ResponseSerializer.serialize_describe_principal_id_format_response,
            "ModifyIdentityIdFormat": resourceid_ResponseSerializer.serialize_modify_identity_id_format_response,
            "ModifyIdFormat": resourceid_ResponseSerializer.serialize_modify_id_format_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

