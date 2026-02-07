from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


@dataclass
class InstanceTagNotificationAttribute:
    include_all_tags_of_instance: bool = False
    instance_tag_key_set: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "includeAllTagsOfInstance": self.include_all_tags_of_instance,
            "instanceTagKeySet": self.instance_tag_key_set.copy(),
        }


class EventNotificationsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Initialize shared state dictionary for event notifications if not present
        if not hasattr(self.state, "event_notifications"):
            self.state.event_notifications = {}

        # We store a single resource for instance event notification attributes keyed by owner_id
        # This simulates per-region, per-account settings
        # Structure: self.state.event_notifications[owner_id] = InstanceTagNotificationAttribute

    def _get_owner_attributes(self) -> InstanceTagNotificationAttribute:
        owner_id = self.get_owner_id()
        attr = self.state.event_notifications.get(owner_id)
        if attr is None:
            attr = InstanceTagNotificationAttribute()
            self.state.event_notifications[owner_id] = attr
        return attr

    def _validate_boolean(self, value: Any, field_name: str) -> bool:
        if not isinstance(value, bool):
            raise ErrorCode(f"InvalidParameterValue: {field_name} must be a Boolean")
        return value

    def _validate_string_list(self, value: Any, field_name: str) -> List[str]:
        if not isinstance(value, list):
            raise ErrorCode(f"InvalidParameterValue: {field_name} must be a list of strings")
        for i, item in enumerate(value):
            if not isinstance(item, str):
                raise ErrorCode(f"InvalidParameterValue: {field_name}[{i}] must be a string")
        return value

    def DeregisterInstanceEventNotificationAttributes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        dry_run = params.get("DryRun")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise ErrorCode("InvalidParameterValue: DryRun must be a Boolean")
            if dry_run:
                # Simulate permission check success
                raise ErrorCode("DryRunOperation")

        instance_tag_attribute = params.get("InstanceTagAttribute")
        if instance_tag_attribute is not None and not isinstance(instance_tag_attribute, dict):
            raise ErrorCode("InvalidParameterValue: InstanceTagAttribute must be an object")

        attr = self._get_owner_attributes()

        # If InstanceTagAttribute is None, do nothing and return current state
        if instance_tag_attribute is None:
            # Return current state
            return {
                "instanceTagAttribute": attr.to_dict(),
                "requestId": self.generate_request_id(),
            }

        # Parse IncludeAllTagsOfInstance
        include_all_tags = instance_tag_attribute.get("IncludeAllTagsOfInstance")
        if include_all_tags is not None:
            include_all_tags = self._validate_boolean(include_all_tags, "IncludeAllTagsOfInstance")

        # Parse InstanceTagKeys
        instance_tag_keys = instance_tag_attribute.get("InstanceTagKeys")
        if instance_tag_keys is not None:
            instance_tag_keys = self._validate_string_list(instance_tag_keys, "InstanceTagKeys")

        # Logic:
        # If IncludeAllTagsOfInstance is True, deregister all tags (set to False and clear keys)
        # If IncludeAllTagsOfInstance is False, deregister all tags (same as True)
        # If IncludeAllTagsOfInstance is None, deregister keys in InstanceTagKeys if provided
        # If InstanceTagKeys is None, no keys to deregister

        if include_all_tags is True:
            # Deregister all tags: set include_all_tags_of_instance to False and clear keys
            attr.include_all_tags_of_instance = False
            attr.instance_tag_key_set.clear()
        elif include_all_tags is False:
            # Deregister all tags: same as True
            attr.include_all_tags_of_instance = False
            attr.instance_tag_key_set.clear()
        else:
            # include_all_tags is None
            if instance_tag_keys is not None:
                # Remove keys from current set if present
                new_keys = [k for k in attr.instance_tag_key_set if k not in instance_tag_keys]
                attr.instance_tag_key_set = new_keys
            # else no keys to deregister, do nothing

        return {
            "instanceTagAttribute": attr.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def DescribeInstanceEventNotificationAttributes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        dry_run = params.get("DryRun")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise ErrorCode("InvalidParameterValue: DryRun must be a Boolean")
            if dry_run:
                # Simulate permission check success
                raise ErrorCode("DryRunOperation")

        attr = self._get_owner_attributes()

        return {
            "instanceTagAttribute": attr.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def RegisterInstanceEventNotificationAttributes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        dry_run = params.get("DryRun")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise ErrorCode("InvalidParameterValue: DryRun must be a Boolean")
            if dry_run:
                # Simulate permission check success
                raise ErrorCode("DryRunOperation")

        instance_tag_attribute = params.get("InstanceTagAttribute")
        if instance_tag_attribute is not None and not isinstance(instance_tag_attribute, dict):
            raise ErrorCode("InvalidParameterValue: InstanceTagAttribute must be an object")

        attr = self._get_owner_attributes()

        # If InstanceTagAttribute is None, do nothing and return current state
        if instance_tag_attribute is None:
            return {
                "instanceTagAttribute": attr.to_dict(),
                "requestId": self.generate_request_id(),
            }

        # Parse IncludeAllTagsOfInstance
        include_all_tags = instance_tag_attribute.get("IncludeAllTagsOfInstance")
        if include_all_tags is not None:
            include_all_tags = self._validate_boolean(include_all_tags, "IncludeAllTagsOfInstance")

        # Parse InstanceTagKeys
        instance_tag_keys = instance_tag_attribute.get("InstanceTagKeys")
        if instance_tag_keys is not None:
            instance_tag_keys = self._validate_string_list(instance_tag_keys, "InstanceTagKeys")

        # Logic:
        # If IncludeAllTagsOfInstance is True, register all tags (set to True and clear keys)
        # If IncludeAllTagsOfInstance is False, register no tags (set to False and clear keys)
        # If IncludeAllTagsOfInstance is None, add keys in InstanceTagKeys to current set (no duplicates)
        # If InstanceTagKeys is None, no keys to add

        if include_all_tags is True:
            attr.include_all_tags_of_instance = True
            attr.instance_tag_key_set.clear()
        elif include_all_tags is False:
            attr.include_all_tags_of_instance = False
            attr.instance_tag_key_set.clear()
        else:
            # include_all_tags is None
            if instance_tag_keys is not None:
                # Add keys to current set, avoid duplicates
                current_keys_set = set(attr.instance_tag_key_set)
                for key in instance_tag_keys:
                    if key not in current_keys_set:
                        attr.instance_tag_key_set.append(key)
                        current_keys_set.add(key)
            # else no keys to add, do nothing

        return {
            "instanceTagAttribute": attr.to_dict(),
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class EventnotificationsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DeregisterInstanceEventNotificationAttributes", self.deregister_instance_event_notification_attributes)
        self.register_action("DescribeInstanceEventNotificationAttributes", self.describe_instance_event_notification_attributes)
        self.register_action("RegisterInstanceEventNotificationAttributes", self.register_instance_event_notification_attributes)

    def deregister_instance_event_notification_attributes(self, params):
        return self.backend.deregister_instance_event_notification_attributes(params)

    def describe_instance_event_notification_attributes(self, params):
        return self.backend.describe_instance_event_notification_attributes(params)

    def register_instance_event_notification_attributes(self, params):
        return self.backend.register_instance_event_notification_attributes(params)
