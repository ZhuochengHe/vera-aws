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
class EventNotification:
    include_all_tags_of_instance: bool = False
    instance_tag_key_set: List[Any] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "includeAllTagsOfInstance": self.include_all_tags_of_instance,
            "instanceTagKeySet": self.instance_tag_key_set,
        }

class EventNotification_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.event_notifications  # alias to shared store


    def DeregisterInstanceEventNotificationAttributes(self, params: Dict[str, Any]):
        """Deregisters tag keys to prevent tags that have the specified tag keys from being
         included in scheduled event notifications for resources in the Region."""

        instance_tag_attribute = params.get("InstanceTagAttribute")
        include_all_tags_value = None
        instance_tag_keys: List[Any] = []

        if isinstance(instance_tag_attribute, dict):
            if "IncludeAllTagsOfInstance" in instance_tag_attribute or "includeAllTagsOfInstance" in instance_tag_attribute:
                include_all_tags_value = str2bool(
                    instance_tag_attribute.get("IncludeAllTagsOfInstance")
                    or instance_tag_attribute.get("includeAllTagsOfInstance")
                )
            tag_keys = (
                instance_tag_attribute.get("InstanceTagKeySet")
                or instance_tag_attribute.get("instanceTagKeySet")
                or instance_tag_attribute.get("InstanceTagKey")
                or instance_tag_attribute.get("instanceTagKey")
                or []
            )
            if isinstance(tag_keys, list):
                instance_tag_keys = tag_keys
            elif tag_keys is not None:
                instance_tag_keys = [tag_keys]
        elif isinstance(instance_tag_attribute, list):
            instance_tag_keys = instance_tag_attribute
        elif instance_tag_attribute is not None:
            instance_tag_keys = [instance_tag_attribute]

        resource = next(iter(self.resources.values()), None)
        if not resource:
            return {
                'instanceTagAttribute': {
                    'includeAllTagsOfInstance': False,
                    'instanceTagKeySet': [],
                    },
                }

        if include_all_tags_value:
            resource.include_all_tags_of_instance = False

        if instance_tag_keys:
            resource.instance_tag_key_set = [
                key for key in resource.instance_tag_key_set if key not in instance_tag_keys
            ]

        return {
            'instanceTagAttribute': resource.to_dict(),
            }

    def DescribeInstanceEventNotificationAttributes(self, params: Dict[str, Any]):
        """Describes the tag keys that are registered to appear in scheduled event notifications
         for resources in the current Region."""

        resource = next(iter(self.resources.values()), None)
        if resource:
            instance_tag_attribute = resource.to_dict()
        else:
            instance_tag_attribute = {
                "includeAllTagsOfInstance": False,
                "instanceTagKeySet": [],
            }

        return {
            'instanceTagAttribute': instance_tag_attribute,
            }

    def RegisterInstanceEventNotificationAttributes(self, params: Dict[str, Any]):
        """Registers a set of tag keys to include in scheduled event notifications for your
         resources. To remove tags, useDeregisterInstanceEventNotificationAttributes."""

        instance_tag_attribute = params.get("InstanceTagAttribute")
        include_all_tags_value = None
        instance_tag_keys: List[Any] = []

        if isinstance(instance_tag_attribute, dict):
            if "IncludeAllTagsOfInstance" in instance_tag_attribute or "includeAllTagsOfInstance" in instance_tag_attribute:
                include_all_tags_value = str2bool(
                    instance_tag_attribute.get("IncludeAllTagsOfInstance")
                    or instance_tag_attribute.get("includeAllTagsOfInstance")
                )
            tag_keys = (
                instance_tag_attribute.get("InstanceTagKeySet")
                or instance_tag_attribute.get("instanceTagKeySet")
                or instance_tag_attribute.get("InstanceTagKey")
                or instance_tag_attribute.get("instanceTagKey")
                or []
            )
            if isinstance(tag_keys, list):
                instance_tag_keys = tag_keys
            elif tag_keys is not None:
                instance_tag_keys = [tag_keys]
        elif isinstance(instance_tag_attribute, list):
            instance_tag_keys = instance_tag_attribute
        elif instance_tag_attribute is not None:
            instance_tag_keys = [instance_tag_attribute]

        resource = next(iter(self.resources.values()), None)
        if not resource:
            resource = EventNotification()
            resource_id = self._generate_id("eve")
            self.resources[resource_id] = resource

        if include_all_tags_value is not None:
            resource.include_all_tags_of_instance = include_all_tags_value

        for key in instance_tag_keys:
            if key not in resource.instance_tag_key_set:
                resource.instance_tag_key_set.append(key)

        return {
            'instanceTagAttribute': resource.to_dict(),
            }

    def _generate_id(self, prefix: str = 'eve') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class eventnotification_RequestParser:
    @staticmethod
    def parse_deregister_instance_event_notification_attributes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceTagAttribute": get_scalar(md, "InstanceTagAttribute"),
        }

    @staticmethod
    def parse_describe_instance_event_notification_attributes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_register_instance_event_notification_attributes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceTagAttribute": get_scalar(md, "InstanceTagAttribute"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DeregisterInstanceEventNotificationAttributes": eventnotification_RequestParser.parse_deregister_instance_event_notification_attributes_request,
            "DescribeInstanceEventNotificationAttributes": eventnotification_RequestParser.parse_describe_instance_event_notification_attributes_request,
            "RegisterInstanceEventNotificationAttributes": eventnotification_RequestParser.parse_register_instance_event_notification_attributes_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class eventnotification_ResponseSerializer:
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
                xml_parts.extend(eventnotification_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(eventnotification_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(eventnotification_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(eventnotification_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(eventnotification_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(eventnotification_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_deregister_instance_event_notification_attributes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeregisterInstanceEventNotificationAttributesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceTagAttribute
        _instanceTagAttribute_key = None
        if "instanceTagAttribute" in data:
            _instanceTagAttribute_key = "instanceTagAttribute"
        elif "InstanceTagAttribute" in data:
            _instanceTagAttribute_key = "InstanceTagAttribute"
        if _instanceTagAttribute_key:
            param_data = data[_instanceTagAttribute_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceTagAttribute>')
            xml_parts.extend(eventnotification_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceTagAttribute>')
        xml_parts.append(f'</DeregisterInstanceEventNotificationAttributesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_event_notification_attributes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceEventNotificationAttributesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceTagAttribute
        _instanceTagAttribute_key = None
        if "instanceTagAttribute" in data:
            _instanceTagAttribute_key = "instanceTagAttribute"
        elif "InstanceTagAttribute" in data:
            _instanceTagAttribute_key = "InstanceTagAttribute"
        if _instanceTagAttribute_key:
            param_data = data[_instanceTagAttribute_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceTagAttribute>')
            xml_parts.extend(eventnotification_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceTagAttribute>')
        xml_parts.append(f'</DescribeInstanceEventNotificationAttributesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_register_instance_event_notification_attributes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RegisterInstanceEventNotificationAttributesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceTagAttribute
        _instanceTagAttribute_key = None
        if "instanceTagAttribute" in data:
            _instanceTagAttribute_key = "instanceTagAttribute"
        elif "InstanceTagAttribute" in data:
            _instanceTagAttribute_key = "InstanceTagAttribute"
        if _instanceTagAttribute_key:
            param_data = data[_instanceTagAttribute_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceTagAttribute>')
            xml_parts.extend(eventnotification_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceTagAttribute>')
        xml_parts.append(f'</RegisterInstanceEventNotificationAttributesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DeregisterInstanceEventNotificationAttributes": eventnotification_ResponseSerializer.serialize_deregister_instance_event_notification_attributes_response,
            "DescribeInstanceEventNotificationAttributes": eventnotification_ResponseSerializer.serialize_describe_instance_event_notification_attributes_response,
            "RegisterInstanceEventNotificationAttributes": eventnotification_ResponseSerializer.serialize_register_instance_event_notification_attributes_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

