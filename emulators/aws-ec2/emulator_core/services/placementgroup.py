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
class PlacementGroup:
    group_arn: str = ""
    group_id: str = ""
    group_name: str = ""
    partition_count: int = 0
    spread_level: str = ""
    state: str = ""
    strategy: str = ""
    tag_set: List[Any] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "groupArn": self.group_arn,
            "groupId": self.group_id,
            "groupName": self.group_name,
            "partitionCount": self.partition_count,
            "spreadLevel": self.spread_level,
            "state": self.state,
            "strategy": self.strategy,
            "tagSet": self.tag_set,
        }

class PlacementGroup_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.placement_groups  # alias to shared store


    def _get_group_by_name(self, group_name: str) -> Optional[PlacementGroup]:
        if not group_name:
            return None
        for group in self.resources.values():
            if group.group_name == group_name:
                return group
        return None

    def CreatePlacementGroup(self, params: Dict[str, Any]):
        """Creates a placement group in which to launch instances. The strategy of the placement
            group determines how the instances are organized within the group. Aclusterplacement group is a logical grouping of instances within a
            single Availability Zone that benefit from low network """

        group_name = params.get("GroupName") or ""
        if not group_name:
            return create_error_response("MissingParameter", "Missing required parameter: GroupName")

        if self._get_group_by_name(group_name):
            return create_error_response(
                "InvalidPlacementGroup.Duplicate",
                f"Placement group '{group_name}' already exists.",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "placement-group":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if isinstance(tag, dict):
                    tag_set.append({"Key": tag.get("Key"), "Value": tag.get("Value")})

        group_id = self._generate_id("pg")
        group_arn = f"arn:aws:ec2:::placement-group/{group_id}"
        resource = PlacementGroup(
            group_arn=group_arn,
            group_id=group_id,
            group_name=group_name,
            partition_count=int(params.get("PartitionCount") or 0),
            spread_level=params.get("SpreadLevel") or "",
            state=ResourceState.AVAILABLE.value,
            strategy=params.get("Strategy") or "",
            tag_set=tag_set,
        )
        self.resources[group_id] = resource

        return {
            'placementGroup': resource.to_dict(),
            }

    def DeletePlacementGroup(self, params: Dict[str, Any]):
        """Deletes the specified placement group. You must terminate all instances in the
            placement group before you can delete the placement group. For more information, seePlacement groupsin theAmazon EC2 User Guide."""

        group_name = params.get("GroupName") or ""
        if not group_name:
            return create_error_response("MissingParameter", "Missing required parameter: GroupName")

        resource = self._get_group_by_name(group_name)
        if not resource:
            return create_error_response(
                "InvalidPlacementGroup.NotFound",
                f"The ID '{group_name}' does not exist",
            )

        for instance in self.state.instances.values():
            placement = instance.placement or {}
            placement_group_name = placement.get("groupName") or placement.get("GroupName")
            placement_group_id = placement.get("groupId") or placement.get("GroupId")
            if placement_group_name == group_name or placement_group_id == resource.group_id:
                return create_error_response(
                    "DependencyViolation",
                    "Placement group is in use by existing instances.",
                )

        if resource.group_id in self.resources:
            del self.resources[resource.group_id]

        return {
            'return': True,
            }

    def DescribePlacementGroups(self, params: Dict[str, Any]):
        """Describes the specified placement groups or all of your placement groups. To describe a specific placement group that issharedwith
                your account, you must specify the ID of the placement group using theGroupIdparameter. Specifying the name of asharedplacement group using theGroupNames"""

        group_ids = params.get("GroupId.N", []) or []
        group_names = params.get("GroupName.N", []) or []

        resources: List[PlacementGroup] = []
        if group_ids or group_names:
            resource_map: Dict[str, PlacementGroup] = {}
            for group_id in group_ids:
                resource = self.resources.get(group_id)
                if not resource:
                    return create_error_response(
                        "InvalidPlacementGroup.NotFound",
                        f"The ID '{group_id}' does not exist",
                    )
                resource_map[group_id] = resource
            for group_name in group_names:
                resource = self._get_group_by_name(group_name)
                if not resource:
                    return create_error_response(
                        "InvalidPlacementGroup.NotFound",
                        f"The ID '{group_name}' does not exist",
                    )
                resource_map[resource.group_id] = resource
            resources = list(resource_map.values())
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        placement_group_set = [resource.to_dict() for resource in resources]

        return {
            'placementGroupSet': placement_group_set,
            }

    def _generate_id(self, prefix: str = 'sg') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class placementgroup_RequestParser:
    @staticmethod
    def parse_create_placement_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GroupName": get_scalar(md, "GroupName"),
            "PartitionCount": get_int(md, "PartitionCount"),
            "SpreadLevel": get_scalar(md, "SpreadLevel"),
            "Strategy": get_scalar(md, "Strategy"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_placement_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GroupName": get_scalar(md, "GroupName"),
        }

    @staticmethod
    def parse_describe_placement_groups_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "GroupId.N": get_indexed_list(md, "GroupId"),
            "GroupName.N": get_indexed_list(md, "GroupName"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreatePlacementGroup": placementgroup_RequestParser.parse_create_placement_group_request,
            "DeletePlacementGroup": placementgroup_RequestParser.parse_delete_placement_group_request,
            "DescribePlacementGroups": placementgroup_RequestParser.parse_describe_placement_groups_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class placementgroup_ResponseSerializer:
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
                xml_parts.extend(placementgroup_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(placementgroup_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(placementgroup_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(placementgroup_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(placementgroup_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(placementgroup_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_placement_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreatePlacementGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize placementGroup
        _placementGroup_key = None
        if "placementGroup" in data:
            _placementGroup_key = "placementGroup"
        elif "PlacementGroup" in data:
            _placementGroup_key = "PlacementGroup"
        if _placementGroup_key:
            param_data = data[_placementGroup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<placementGroup>')
            xml_parts.extend(placementgroup_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</placementGroup>')
        xml_parts.append(f'</CreatePlacementGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_placement_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeletePlacementGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeletePlacementGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_placement_groups_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribePlacementGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize placementGroupSet
        _placementGroupSet_key = None
        if "placementGroupSet" in data:
            _placementGroupSet_key = "placementGroupSet"
        elif "PlacementGroupSet" in data:
            _placementGroupSet_key = "PlacementGroupSet"
        elif "PlacementGroups" in data:
            _placementGroupSet_key = "PlacementGroups"
        if _placementGroupSet_key:
            param_data = data[_placementGroupSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<placementGroupSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(placementgroup_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</placementGroupSet>')
            else:
                xml_parts.append(f'{indent_str}<placementGroupSet/>')
        xml_parts.append(f'</DescribePlacementGroupsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreatePlacementGroup": placementgroup_ResponseSerializer.serialize_create_placement_group_response,
            "DeletePlacementGroup": placementgroup_ResponseSerializer.serialize_delete_placement_group_response,
            "DescribePlacementGroups": placementgroup_ResponseSerializer.serialize_describe_placement_groups_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

