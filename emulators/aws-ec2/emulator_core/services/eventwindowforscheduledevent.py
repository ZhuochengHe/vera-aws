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
class EventWindowForScheduledEvent:
    association_target: Dict[str, Any] = field(default_factory=dict)
    cron_expression: str = ""
    instance_event_window_id: str = ""
    name: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    time_range_set: List[Any] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "associationTarget": self.association_target,
            "cronExpression": self.cron_expression,
            "instanceEventWindowId": self.instance_event_window_id,
            "name": self.name,
            "state": self.state,
            "tagSet": self.tag_set,
            "timeRangeSet": self.time_range_set,
        }

class EventWindowForScheduledEvent_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.event_windows_for_scheduled_events  # alias to shared store

    def _get_event_window_or_error(self, event_window_id: str):
        event_window = self.resources.get(event_window_id)
        if not event_window:
            return create_error_response(
                "InvalidInstanceEventWindowID.NotFound",
                f"The ID '{event_window_id}' does not exist",
            )
        return event_window

    def AssociateInstanceEventWindow(self, params: Dict[str, Any]):
        """Associates one or more targets with an event window. Only one type of target (instance
         IDs, Dedicated Host IDs, or tags) can be specified with an event window. For more information, seeDefine event windows for scheduled
            eventsin theAmazon EC2 User Guide."""

        if not params.get("AssociationTarget"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: AssociationTarget",
            )
        if not params.get("InstanceEventWindowId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: InstanceEventWindowId",
            )

        event_window_id = params.get("InstanceEventWindowId")
        event_window = self._get_event_window_or_error(event_window_id)
        if is_error_response(event_window):
            return event_window

        association_target = params.get("AssociationTarget") or {}
        if not isinstance(association_target, dict):
            association_target = {}

        new_target = {
            "dedicatedHostIdSet": list(
                association_target.get("dedicatedHostIdSet")
                or association_target.get("DedicatedHostIdSet")
                or []
            ),
            "instanceIdSet": list(
                association_target.get("instanceIdSet")
                or association_target.get("InstanceIdSet")
                or []
            ),
            "tagSet": list(
                association_target.get("tagSet") or association_target.get("TagSet") or []
            ),
        }
        provided_types = [key for key, values in new_target.items() if values]
        if not provided_types:
            return create_error_response(
                "InvalidParameterValue",
                "AssociationTarget must specify a target set",
            )
        if len(provided_types) > 1:
            return create_error_response(
                "InvalidParameterValue",
                "Only one type of association target can be specified",
            )

        existing_target = event_window.association_target or {}
        for key in ["dedicatedHostIdSet", "instanceIdSet", "tagSet"]:
            existing_target.setdefault(key, [])

        existing_types = [
            key for key in ["dedicatedHostIdSet", "instanceIdSet", "tagSet"]
            if existing_target.get(key)
        ]
        if existing_types and provided_types and set(existing_types) != set(provided_types):
            return create_error_response(
                "InvalidParameterValue",
                "AssociationTarget type does not match existing associations",
            )

        if new_target["tagSet"]:
            for tag in new_target["tagSet"]:
                if tag not in existing_target["tagSet"]:
                    existing_target["tagSet"].append(tag)
        else:
            key = provided_types[0]
            for item in new_target[key]:
                if item not in existing_target[key]:
                    existing_target[key].append(item)

        event_window.association_target = existing_target

        return {
            'instanceEventWindow': event_window.to_dict(),
            }

    def CreateInstanceEventWindow(self, params: Dict[str, Any]):
        """Creates an event window in which scheduled events for the associated Amazon EC2 instances can
         run. You can define either a set of time ranges or a cron expression when creating the event
         window, but not both. All event window times are in UTC. You can create up to 200 event windows"""

        cron_expression = params.get("CronExpression") or ""
        time_ranges = params.get("TimeRange.N", []) or []
        if cron_expression and time_ranges:
            return create_error_response(
                "InvalidParameterValue",
                "CronExpression and TimeRange cannot both be specified",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        event_window_id = self._generate_id("iew")
        association_target = {
            "dedicatedHostIdSet": [],
            "instanceIdSet": [],
            "tagSet": [],
        }
        resource = EventWindowForScheduledEvent(
            association_target=association_target,
            cron_expression=cron_expression,
            instance_event_window_id=event_window_id,
            name=params.get("Name") or "",
            state="active",
            tag_set=tag_set,
            time_range_set=time_ranges,
        )
        self.resources[event_window_id] = resource

        return {
            'instanceEventWindow': resource.to_dict(),
            }

    def DeleteInstanceEventWindow(self, params: Dict[str, Any]):
        """Deletes the specified event window. For more information, seeDefine event windows for scheduled
            eventsin theAmazon EC2 User Guide."""

        if not params.get("InstanceEventWindowId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: InstanceEventWindowId",
            )

        event_window_id = params.get("InstanceEventWindowId")
        event_window = self._get_event_window_or_error(event_window_id)
        if is_error_response(event_window):
            return event_window

        event_window.state = "deleted"
        del self.resources[event_window_id]

        return {
            'instanceEventWindowState': {
                'instanceEventWindowId': event_window_id,
                'state': event_window.state,
                },
            }

    def DescribeInstanceEventWindows(self, params: Dict[str, Any]):
        """Describes the specified event windows or all event windows. If you specify event window IDs, the output includes information for only the specified
         event windows. If you specify filters, the output includes information for only those event
         windows that meet the filter criteria. If """

        event_window_ids = params.get("InstanceEventWindowId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if event_window_ids:
            resources = []
            for event_window_id in event_window_ids:
                event_window = self.resources.get(event_window_id)
                if not event_window:
                    return create_error_response(
                        "InvalidInstanceEventWindowID.NotFound",
                        f"The ID '{event_window_id}' does not exist",
                    )
                resources.append(event_window)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        event_windows = [event_window.to_dict() for event_window in resources[:max_results]]

        return {
            'instanceEventWindowSet': event_windows,
            'nextToken': None,
            }

    def DisassociateInstanceEventWindow(self, params: Dict[str, Any]):
        """Disassociates one or more targets from an event window. For more information, seeDefine event windows for scheduled
            eventsin theAmazon EC2 User Guide."""

        if not params.get("AssociationTarget"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: AssociationTarget",
            )
        if not params.get("InstanceEventWindowId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: InstanceEventWindowId",
            )

        event_window_id = params.get("InstanceEventWindowId")
        event_window = self._get_event_window_or_error(event_window_id)
        if is_error_response(event_window):
            return event_window

        association_target = params.get("AssociationTarget") or {}
        if not isinstance(association_target, dict):
            association_target = {}

        target_to_remove = {
            "dedicatedHostIdSet": list(
                association_target.get("dedicatedHostIdSet")
                or association_target.get("DedicatedHostIdSet")
                or []
            ),
            "instanceIdSet": list(
                association_target.get("instanceIdSet")
                or association_target.get("InstanceIdSet")
                or []
            ),
            "tagSet": list(
                association_target.get("tagSet") or association_target.get("TagSet") or []
            ),
        }
        provided_types = [key for key, values in target_to_remove.items() if values]
        if not provided_types:
            return create_error_response(
                "InvalidParameterValue",
                "AssociationTarget must specify a target set",
            )
        if len(provided_types) > 1:
            return create_error_response(
                "InvalidParameterValue",
                "Only one type of association target can be specified",
            )

        existing_target = event_window.association_target or {}
        for key in ["dedicatedHostIdSet", "instanceIdSet", "tagSet"]:
            existing_target.setdefault(key, [])

        if not existing_target.get(provided_types[0]):
            return create_error_response(
                "InvalidParameterValue",
                "AssociationTarget does not match existing associations",
            )

        if target_to_remove["tagSet"]:
            existing_target["tagSet"] = [
                tag for tag in existing_target["tagSet"] if tag not in target_to_remove["tagSet"]
            ]
        else:
            key = provided_types[0]
            existing_target[key] = [
                item for item in existing_target[key] if item not in target_to_remove[key]
            ]

        event_window.association_target = existing_target

        return {
            'instanceEventWindow': event_window.to_dict(),
            }

    def ModifyInstanceEventWindow(self, params: Dict[str, Any]):
        """Modifies the specified event window. You can define either a set of time ranges or a cron expression when modifying the event
         window, but not both. To modify the targets associated with the event window, use theAssociateInstanceEventWindowandDisassociateInstanceEventWindowAPI."""

        if not params.get("InstanceEventWindowId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: InstanceEventWindowId",
            )

        event_window_id = params.get("InstanceEventWindowId")
        event_window = self._get_event_window_or_error(event_window_id)
        if is_error_response(event_window):
            return event_window

        cron_expression = params.get("CronExpression")
        time_ranges = params.get("TimeRange.N", []) or []
        if cron_expression and time_ranges:
            return create_error_response(
                "InvalidParameterValue",
                "CronExpression and TimeRange cannot both be specified",
            )

        if params.get("Name") is not None:
            event_window.name = params.get("Name") or ""

        if cron_expression is not None:
            event_window.cron_expression = cron_expression or ""
            if cron_expression:
                event_window.time_range_set = []

        if time_ranges:
            event_window.time_range_set = time_ranges
            event_window.cron_expression = ""

        return {
            'instanceEventWindow': event_window.to_dict(),
            }

    def _generate_id(self, prefix: str = 'i') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class eventwindowforscheduledevent_RequestParser:
    @staticmethod
    def parse_associate_instance_event_window_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationTarget": get_scalar(md, "AssociationTarget"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceEventWindowId": get_scalar(md, "InstanceEventWindowId"),
        }

    @staticmethod
    def parse_create_instance_event_window_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CronExpression": get_scalar(md, "CronExpression"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Name": get_scalar(md, "Name"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TimeRange.N": get_indexed_list(md, "TimeRange"),
        }

    @staticmethod
    def parse_delete_instance_event_window_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ForceDelete": get_scalar(md, "ForceDelete"),
            "InstanceEventWindowId": get_scalar(md, "InstanceEventWindowId"),
        }

    @staticmethod
    def parse_describe_instance_event_windows_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "InstanceEventWindowId.N": get_indexed_list(md, "InstanceEventWindowId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disassociate_instance_event_window_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationTarget": get_scalar(md, "AssociationTarget"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceEventWindowId": get_scalar(md, "InstanceEventWindowId"),
        }

    @staticmethod
    def parse_modify_instance_event_window_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CronExpression": get_scalar(md, "CronExpression"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceEventWindowId": get_scalar(md, "InstanceEventWindowId"),
            "Name": get_scalar(md, "Name"),
            "TimeRange.N": get_indexed_list(md, "TimeRange"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateInstanceEventWindow": eventwindowforscheduledevent_RequestParser.parse_associate_instance_event_window_request,
            "CreateInstanceEventWindow": eventwindowforscheduledevent_RequestParser.parse_create_instance_event_window_request,
            "DeleteInstanceEventWindow": eventwindowforscheduledevent_RequestParser.parse_delete_instance_event_window_request,
            "DescribeInstanceEventWindows": eventwindowforscheduledevent_RequestParser.parse_describe_instance_event_windows_request,
            "DisassociateInstanceEventWindow": eventwindowforscheduledevent_RequestParser.parse_disassociate_instance_event_window_request,
            "ModifyInstanceEventWindow": eventwindowforscheduledevent_RequestParser.parse_modify_instance_event_window_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class eventwindowforscheduledevent_ResponseSerializer:
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
                xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_instance_event_window_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceEventWindow
        _instanceEventWindow_key = None
        if "instanceEventWindow" in data:
            _instanceEventWindow_key = "instanceEventWindow"
        elif "InstanceEventWindow" in data:
            _instanceEventWindow_key = "InstanceEventWindow"
        if _instanceEventWindow_key:
            param_data = data[_instanceEventWindow_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceEventWindow>')
            xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceEventWindow>')
        xml_parts.append(f'</AssociateInstanceEventWindowResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_instance_event_window_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceEventWindow
        _instanceEventWindow_key = None
        if "instanceEventWindow" in data:
            _instanceEventWindow_key = "instanceEventWindow"
        elif "InstanceEventWindow" in data:
            _instanceEventWindow_key = "InstanceEventWindow"
        if _instanceEventWindow_key:
            param_data = data[_instanceEventWindow_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceEventWindow>')
            xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceEventWindow>')
        xml_parts.append(f'</CreateInstanceEventWindowResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_instance_event_window_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceEventWindowState
        _instanceEventWindowState_key = None
        if "instanceEventWindowState" in data:
            _instanceEventWindowState_key = "instanceEventWindowState"
        elif "InstanceEventWindowState" in data:
            _instanceEventWindowState_key = "InstanceEventWindowState"
        if _instanceEventWindowState_key:
            param_data = data[_instanceEventWindowState_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceEventWindowState>')
            xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceEventWindowState>')
        xml_parts.append(f'</DeleteInstanceEventWindowResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_event_windows_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceEventWindowsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceEventWindowSet
        _instanceEventWindowSet_key = None
        if "instanceEventWindowSet" in data:
            _instanceEventWindowSet_key = "instanceEventWindowSet"
        elif "InstanceEventWindowSet" in data:
            _instanceEventWindowSet_key = "InstanceEventWindowSet"
        elif "InstanceEventWindows" in data:
            _instanceEventWindowSet_key = "InstanceEventWindows"
        if _instanceEventWindowSet_key:
            param_data = data[_instanceEventWindowSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceEventWindowSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceEventWindowSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceEventWindowSet/>')
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
        xml_parts.append(f'</DescribeInstanceEventWindowsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_instance_event_window_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceEventWindow
        _instanceEventWindow_key = None
        if "instanceEventWindow" in data:
            _instanceEventWindow_key = "instanceEventWindow"
        elif "InstanceEventWindow" in data:
            _instanceEventWindow_key = "InstanceEventWindow"
        if _instanceEventWindow_key:
            param_data = data[_instanceEventWindow_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceEventWindow>')
            xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceEventWindow>')
        xml_parts.append(f'</DisassociateInstanceEventWindowResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_event_window_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceEventWindowResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceEventWindow
        _instanceEventWindow_key = None
        if "instanceEventWindow" in data:
            _instanceEventWindow_key = "instanceEventWindow"
        elif "InstanceEventWindow" in data:
            _instanceEventWindow_key = "InstanceEventWindow"
        if _instanceEventWindow_key:
            param_data = data[_instanceEventWindow_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceEventWindow>')
            xml_parts.extend(eventwindowforscheduledevent_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceEventWindow>')
        xml_parts.append(f'</ModifyInstanceEventWindowResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateInstanceEventWindow": eventwindowforscheduledevent_ResponseSerializer.serialize_associate_instance_event_window_response,
            "CreateInstanceEventWindow": eventwindowforscheduledevent_ResponseSerializer.serialize_create_instance_event_window_response,
            "DeleteInstanceEventWindow": eventwindowforscheduledevent_ResponseSerializer.serialize_delete_instance_event_window_response,
            "DescribeInstanceEventWindows": eventwindowforscheduledevent_ResponseSerializer.serialize_describe_instance_event_windows_response,
            "DisassociateInstanceEventWindow": eventwindowforscheduledevent_ResponseSerializer.serialize_disassociate_instance_event_window_response,
            "ModifyInstanceEventWindow": eventwindowforscheduledevent_ResponseSerializer.serialize_modify_instance_event_window_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

