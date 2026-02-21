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
class VerifiedAccessGroup:
    creation_time: str = ""
    deletion_time: str = ""
    description: str = ""
    last_updated_time: str = ""
    owner: str = ""
    sse_specification: Dict[str, Any] = field(default_factory=dict)
    tag_set: List[Any] = field(default_factory=list)
    verified_access_group_arn: str = ""
    verified_access_group_id: str = ""
    verified_access_instance_id: str = ""

    # Internal dependency tracking — not in API response
    verified_access_endpoint_ids: List[str] = field(default_factory=list)  # tracks VerifiedAccessEndpoint children

    policy_document: str = ""
    policy_enabled: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTime": self.creation_time,
            "deletionTime": self.deletion_time,
            "description": self.description,
            "lastUpdatedTime": self.last_updated_time,
            "owner": self.owner,
            "sseSpecification": self.sse_specification,
            "tagSet": self.tag_set,
            "verifiedAccessGroupArn": self.verified_access_group_arn,
            "verifiedAccessGroupId": self.verified_access_group_id,
            "verifiedAccessInstanceId": self.verified_access_instance_id,
        }

class VerifiedAccessGroup_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.verified_access_groups  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.verified_access_logs.get(params['verified_access_instance_id']).verified_access_group_ids.append(new_id)
    #   Delete: self.state.verified_access_logs.get(resource.verified_access_instance_id).verified_access_group_ids.remove(resource_id)


    def _get_group_or_error(self, group_id: str):
        resource = self.resources.get(group_id)
        if not resource:
            return None, create_error_response(
                "InvalidVerifiedAccessGroupId.NotFound",
                f"The ID '{group_id}' does not exist",
            )
        return resource, None

    # Add any helper functions needed by the API methods below.
    # These helpers can be used by multiple API methods.

    def CreateVerifiedAccessGroup(self, params: Dict[str, Any]):
        """An AWS Verified Access group is a collection of AWS Verified Access endpoints who's associated applications have
         similar security requirements. Each instance within a Verified Access group shares an Verified Access policy. For
         example, you can group all Verified Access instances as"""

        if not params.get("VerifiedAccessInstanceId"):
            return create_error_response("MissingParameter", "Missing required parameter: VerifiedAccessInstanceId")

        verified_access_instance_id = params.get("VerifiedAccessInstanceId")
        if verified_access_instance_id not in self.state.verified_access_instances:
            return create_error_response(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The ID '{verified_access_instance_id}' does not exist",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "verified-access-group":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        now = datetime.now(timezone.utc).isoformat()
        verified_access_group_id = self._generate_id("verified")
        resource = VerifiedAccessGroup(
            creation_time=now,
            deletion_time="",
            description=params.get("Description") or "",
            last_updated_time=now,
            owner="",
            sse_specification=params.get("SseSpecification") or {},
            tag_set=tag_set,
            verified_access_group_arn="",
            verified_access_group_id=verified_access_group_id,
            verified_access_instance_id=verified_access_instance_id,
            policy_document=params.get("PolicyDocument") or "",
            policy_enabled=None,
        )
        self.resources[verified_access_group_id] = resource

        parent = self.state.verified_access_logs.get(verified_access_instance_id)
        if parent and hasattr(parent, "verified_access_group_ids"):
            parent.verified_access_group_ids.append(verified_access_group_id)

        return {
            'verifiedAccessGroup': resource.to_dict(),
            }

    def DeleteVerifiedAccessGroup(self, params: Dict[str, Any]):
        """Delete an AWS Verified Access group."""

        if not params.get("VerifiedAccessGroupId"):
            return create_error_response("MissingParameter", "Missing required parameter: VerifiedAccessGroupId")

        verified_access_group_id = params.get("VerifiedAccessGroupId")
        resource, error = self._get_group_or_error(verified_access_group_id)
        if error:
            return error

        if getattr(resource, "verified_access_endpoint_ids", []):
            return create_error_response(
                "DependencyViolation",
                "VerifiedAccessGroup has dependent VerifiedAccessEndpoint(s) and cannot be deleted.",
            )

        parent = self.state.verified_access_logs.get(resource.verified_access_instance_id)
        if parent and hasattr(parent, "verified_access_group_ids"):
            if verified_access_group_id in parent.verified_access_group_ids:
                parent.verified_access_group_ids.remove(verified_access_group_id)

        resource.deletion_time = datetime.now(timezone.utc).isoformat()
        resource.last_updated_time = resource.deletion_time
        del self.resources[verified_access_group_id]

        return {
            'verifiedAccessGroup': resource.to_dict(),
            }

    def DescribeVerifiedAccessGroups(self, params: Dict[str, Any]):
        """Describes the specified Verified Access groups."""

        group_ids = params.get("VerifiedAccessGroupId.N", []) or []
        if group_ids:
            resources: List[VerifiedAccessGroup] = []
            for group_id in group_ids:
                resource = self.resources.get(group_id)
                if not resource:
                    return create_error_response(
                        "InvalidVerifiedAccessGroupId.NotFound",
                        f"The ID '{group_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        verified_access_instance_id = params.get("VerifiedAccessInstanceId")
        if verified_access_instance_id:
            resources = [
                resource for resource in resources
                if resource.verified_access_instance_id == verified_access_instance_id
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'verifiedAccessGroupSet': [resource.to_dict() for resource in resources],
            }

    def GetVerifiedAccessGroupPolicy(self, params: Dict[str, Any]):
        """Shows the contents of the Verified Access policy associated with the group."""

        if not params.get("VerifiedAccessGroupId"):
            return create_error_response("MissingParameter", "Missing required parameter: VerifiedAccessGroupId")

        verified_access_group_id = params.get("VerifiedAccessGroupId")
        resource, error = self._get_group_or_error(verified_access_group_id)
        if error:
            return error

        return {
            'policyDocument': resource.policy_document,
            'policyEnabled': resource.policy_enabled,
            }

    def ModifyVerifiedAccessGroup(self, params: Dict[str, Any]):
        """Modifies the specified AWS Verified Access group configuration."""

        if not params.get("VerifiedAccessGroupId"):
            return create_error_response("MissingParameter", "Missing required parameter: VerifiedAccessGroupId")

        verified_access_group_id = params.get("VerifiedAccessGroupId")
        resource, error = self._get_group_or_error(verified_access_group_id)
        if error:
            return error

        new_instance_id = params.get("VerifiedAccessInstanceId")
        if new_instance_id:
            if new_instance_id not in self.state.verified_access_instances:
                return create_error_response(
                    "InvalidVerifiedAccessInstanceId.NotFound",
                    f"The ID '{new_instance_id}' does not exist",
                )
            if new_instance_id != resource.verified_access_instance_id:
                old_parent = self.state.verified_access_logs.get(resource.verified_access_instance_id)
                if old_parent and hasattr(old_parent, "verified_access_group_ids"):
                    if verified_access_group_id in old_parent.verified_access_group_ids:
                        old_parent.verified_access_group_ids.remove(verified_access_group_id)
                new_parent = self.state.verified_access_logs.get(new_instance_id)
                if new_parent and hasattr(new_parent, "verified_access_group_ids"):
                    new_parent.verified_access_group_ids.append(verified_access_group_id)
                resource.verified_access_instance_id = new_instance_id

        if params.get("Description") is not None:
            resource.description = params.get("Description") or ""

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()

        return {
            'verifiedAccessGroup': resource.to_dict(),
            }

    def ModifyVerifiedAccessGroupPolicy(self, params: Dict[str, Any]):
        """Modifies the specified AWS Verified Access group policy."""

        if not params.get("VerifiedAccessGroupId"):
            return create_error_response("MissingParameter", "Missing required parameter: VerifiedAccessGroupId")

        verified_access_group_id = params.get("VerifiedAccessGroupId")
        resource, error = self._get_group_or_error(verified_access_group_id)
        if error:
            return error

        if params.get("PolicyDocument") is not None:
            resource.policy_document = params.get("PolicyDocument") or ""

        if params.get("PolicyEnabled") is not None:
            resource.policy_enabled = str2bool(params.get("PolicyEnabled"))

        if params.get("SseSpecification") is not None:
            resource.sse_specification = params.get("SseSpecification") or {}

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()

        return {
            'policyDocument': resource.policy_document,
            'policyEnabled': resource.policy_enabled,
            'sseSpecification': resource.sse_specification,
            }

    def _generate_id(self, prefix: str = 'verified') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class verifiedaccessgroup_RequestParser:
    @staticmethod
    def parse_create_verified_access_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PolicyDocument": get_scalar(md, "PolicyDocument"),
            "SseSpecification": get_scalar(md, "SseSpecification"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_delete_verified_access_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessGroupId": get_scalar(md, "VerifiedAccessGroupId"),
        }

    @staticmethod
    def parse_describe_verified_access_groups_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VerifiedAccessGroupId.N": get_indexed_list(md, "VerifiedAccessGroupId"),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_get_verified_access_group_policy_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessGroupId": get_scalar(md, "VerifiedAccessGroupId"),
        }

    @staticmethod
    def parse_modify_verified_access_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessGroupId": get_scalar(md, "VerifiedAccessGroupId"),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_modify_verified_access_group_policy_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PolicyDocument": get_scalar(md, "PolicyDocument"),
            "PolicyEnabled": get_scalar(md, "PolicyEnabled"),
            "SseSpecification": get_scalar(md, "SseSpecification"),
            "VerifiedAccessGroupId": get_scalar(md, "VerifiedAccessGroupId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateVerifiedAccessGroup": verifiedaccessgroup_RequestParser.parse_create_verified_access_group_request,
            "DeleteVerifiedAccessGroup": verifiedaccessgroup_RequestParser.parse_delete_verified_access_group_request,
            "DescribeVerifiedAccessGroups": verifiedaccessgroup_RequestParser.parse_describe_verified_access_groups_request,
            "GetVerifiedAccessGroupPolicy": verifiedaccessgroup_RequestParser.parse_get_verified_access_group_policy_request,
            "ModifyVerifiedAccessGroup": verifiedaccessgroup_RequestParser.parse_modify_verified_access_group_request,
            "ModifyVerifiedAccessGroupPolicy": verifiedaccessgroup_RequestParser.parse_modify_verified_access_group_policy_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class verifiedaccessgroup_ResponseSerializer:
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
                xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_verified_access_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVerifiedAccessGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessGroup
        _verifiedAccessGroup_key = None
        if "verifiedAccessGroup" in data:
            _verifiedAccessGroup_key = "verifiedAccessGroup"
        elif "VerifiedAccessGroup" in data:
            _verifiedAccessGroup_key = "VerifiedAccessGroup"
        if _verifiedAccessGroup_key:
            param_data = data[_verifiedAccessGroup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessGroup>')
            xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessGroup>')
        xml_parts.append(f'</CreateVerifiedAccessGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_verified_access_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVerifiedAccessGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessGroup
        _verifiedAccessGroup_key = None
        if "verifiedAccessGroup" in data:
            _verifiedAccessGroup_key = "verifiedAccessGroup"
        elif "VerifiedAccessGroup" in data:
            _verifiedAccessGroup_key = "VerifiedAccessGroup"
        if _verifiedAccessGroup_key:
            param_data = data[_verifiedAccessGroup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessGroup>')
            xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessGroup>')
        xml_parts.append(f'</DeleteVerifiedAccessGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_verified_access_groups_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVerifiedAccessGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize verifiedAccessGroupSet
        _verifiedAccessGroupSet_key = None
        if "verifiedAccessGroupSet" in data:
            _verifiedAccessGroupSet_key = "verifiedAccessGroupSet"
        elif "VerifiedAccessGroupSet" in data:
            _verifiedAccessGroupSet_key = "VerifiedAccessGroupSet"
        elif "VerifiedAccessGroups" in data:
            _verifiedAccessGroupSet_key = "VerifiedAccessGroups"
        if _verifiedAccessGroupSet_key:
            param_data = data[_verifiedAccessGroupSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<verifiedAccessGroupSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</verifiedAccessGroupSet>')
            else:
                xml_parts.append(f'{indent_str}<verifiedAccessGroupSet/>')
        xml_parts.append(f'</DescribeVerifiedAccessGroupsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_verified_access_group_policy_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetVerifiedAccessGroupPolicyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize policyDocument
        _policyDocument_key = None
        if "policyDocument" in data:
            _policyDocument_key = "policyDocument"
        elif "PolicyDocument" in data:
            _policyDocument_key = "PolicyDocument"
        if _policyDocument_key:
            param_data = data[_policyDocument_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyDocument>{esc(str(param_data))}</policyDocument>')
        # Serialize policyEnabled
        _policyEnabled_key = None
        if "policyEnabled" in data:
            _policyEnabled_key = "policyEnabled"
        elif "PolicyEnabled" in data:
            _policyEnabled_key = "PolicyEnabled"
        if _policyEnabled_key:
            param_data = data[_policyEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyEnabled>{esc(str(param_data))}</policyEnabled>')
        xml_parts.append(f'</GetVerifiedAccessGroupPolicyResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_verified_access_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVerifiedAccessGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessGroup
        _verifiedAccessGroup_key = None
        if "verifiedAccessGroup" in data:
            _verifiedAccessGroup_key = "verifiedAccessGroup"
        elif "VerifiedAccessGroup" in data:
            _verifiedAccessGroup_key = "VerifiedAccessGroup"
        if _verifiedAccessGroup_key:
            param_data = data[_verifiedAccessGroup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessGroup>')
            xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessGroup>')
        xml_parts.append(f'</ModifyVerifiedAccessGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_verified_access_group_policy_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVerifiedAccessGroupPolicyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize policyDocument
        _policyDocument_key = None
        if "policyDocument" in data:
            _policyDocument_key = "policyDocument"
        elif "PolicyDocument" in data:
            _policyDocument_key = "PolicyDocument"
        if _policyDocument_key:
            param_data = data[_policyDocument_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyDocument>{esc(str(param_data))}</policyDocument>')
        # Serialize policyEnabled
        _policyEnabled_key = None
        if "policyEnabled" in data:
            _policyEnabled_key = "policyEnabled"
        elif "PolicyEnabled" in data:
            _policyEnabled_key = "PolicyEnabled"
        if _policyEnabled_key:
            param_data = data[_policyEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyEnabled>{esc(str(param_data))}</policyEnabled>')
        # Serialize sseSpecification
        _sseSpecification_key = None
        if "sseSpecification" in data:
            _sseSpecification_key = "sseSpecification"
        elif "SseSpecification" in data:
            _sseSpecification_key = "SseSpecification"
        if _sseSpecification_key:
            param_data = data[_sseSpecification_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sseSpecification>')
            xml_parts.extend(verifiedaccessgroup_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</sseSpecification>')
        xml_parts.append(f'</ModifyVerifiedAccessGroupPolicyResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateVerifiedAccessGroup": verifiedaccessgroup_ResponseSerializer.serialize_create_verified_access_group_response,
            "DeleteVerifiedAccessGroup": verifiedaccessgroup_ResponseSerializer.serialize_delete_verified_access_group_response,
            "DescribeVerifiedAccessGroups": verifiedaccessgroup_ResponseSerializer.serialize_describe_verified_access_groups_response,
            "GetVerifiedAccessGroupPolicy": verifiedaccessgroup_ResponseSerializer.serialize_get_verified_access_group_policy_response,
            "ModifyVerifiedAccessGroup": verifiedaccessgroup_ResponseSerializer.serialize_modify_verified_access_group_response,
            "ModifyVerifiedAccessGroupPolicy": verifiedaccessgroup_ResponseSerializer.serialize_modify_verified_access_group_policy_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

