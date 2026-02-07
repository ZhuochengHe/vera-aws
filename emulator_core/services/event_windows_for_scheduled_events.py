from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class InstanceEventWindowState(str, Enum):
    CREATING = "creating"
    DELETING = "deleting"
    ACTIVE = "active"
    DELETED = "deleted"


class WeekDay(str, Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Key": self.key,
            "Value": self.value,
        }


@dataclass
class InstanceEventWindowAssociationTarget:
    dedicated_host_id_set: List[str] = field(default_factory=list)
    instance_id_set: List[str] = field(default_factory=list)
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DedicatedHostIdSet": self.dedicated_host_id_set,
            "InstanceIdSet": self.instance_id_set,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


@dataclass
class InstanceEventWindowDisassociationRequest:
    dedicated_host_ids: List[str] = field(default_factory=list)
    instance_ids: List[str] = field(default_factory=list)
    instance_tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DedicatedHostIds": self.dedicated_host_ids,
            "InstanceIds": self.instance_ids,
            "InstanceTags": [tag.to_dict() for tag in self.instance_tags],
        }


@dataclass
class InstanceEventWindowAssociationRequest:
    dedicated_host_ids: List[str] = field(default_factory=list)
    instance_ids: List[str] = field(default_factory=list)
    instance_tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DedicatedHostIds": self.dedicated_host_ids,
            "InstanceIds": self.instance_ids,
            "InstanceTags": [tag.to_dict() for tag in self.instance_tags],
        }


@dataclass
class InstanceEventWindowTimeRange:
    end_hour: Optional[int] = None
    end_week_day: Optional[WeekDay] = None
    start_hour: Optional[int] = None
    start_week_day: Optional[WeekDay] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EndHour": self.end_hour,
            "EndWeekDay": self.end_week_day.value if self.end_week_day else None,
            "StartHour": self.start_hour,
            "StartWeekDay": self.start_week_day.value if self.start_week_day else None,
        }


@dataclass
class InstanceEventWindowTimeRangeRequest:
    end_hour: Optional[int] = None
    end_week_day: Optional[WeekDay] = None
    start_hour: Optional[int] = None
    start_week_day: Optional[WeekDay] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EndHour": self.end_hour,
            "EndWeekDay": self.end_week_day.value if self.end_week_day else None,
            "StartHour": self.start_hour,
            "StartWeekDay": self.start_week_day.value if self.start_week_day else None,
        }


@dataclass
class TagSpecification:
    resource_type: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class InstanceEventWindow:
    association_target: Optional[InstanceEventWindowAssociationTarget] = None
    cron_expression: Optional[str] = None
    instance_event_window_id: Optional[str] = None
    name: Optional[str] = None
    state: Optional[InstanceEventWindowState] = None
    tag_set: List[Tag] = field(default_factory=list)
    time_range_set: List[InstanceEventWindowTimeRange] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AssociationTarget": self.association_target.to_dict() if self.association_target else None,
            "CronExpression": self.cron_expression,
            "InstanceEventWindowId": self.instance_event_window_id,
            "Name": self.name,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "TimeRangeSet": [tr.to_dict() for tr in self.time_range_set],
        }


@dataclass
class InstanceEventWindowStateChange:
    instance_event_window_id: Optional[str] = None
    state: Optional[InstanceEventWindowState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "InstanceEventWindowId": self.instance_event_window_id,
            "State": self.state.value if self.state else None,
        }


class EventwindowsforscheduledeventsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.instance_event_windows

    def associate_instance_event_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_event_window_id = params.get("InstanceEventWindowId")
        association_target_params = params.get("AssociationTarget")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not instance_event_window_id:
            raise ValueError("InstanceEventWindowId is required")

        if not association_target_params:
            raise ValueError("AssociationTarget is required")

        event_window = self.state.event_windows_for_scheduled_events.get(instance_event_window_id)
        if not event_window:
            raise ValueError(f"InstanceEventWindow {instance_event_window_id} not found")

        # Validate that only one type of target is specified
        dedicated_host_ids = association_target_params.get("DedicatedHostIds", [])
        instance_ids = association_target_params.get("InstanceIds", [])
        instance_tags_params = association_target_params.get("InstanceTags", [])

        count_targets = sum(bool(x) for x in [dedicated_host_ids, instance_ids, instance_tags_params])
        if count_targets == 0:
            raise ValueError("At least one target type must be specified in AssociationTarget")
        if count_targets > 1:
            raise ValueError("Only one type of target (DedicatedHostIds, InstanceIds, or InstanceTags) can be specified")

        # Convert instance_tags_params to Tag objects
        instance_tags = []
        for tag_dict in instance_tags_params:
            key = tag_dict.get("Key")
            value = tag_dict.get("Value")
            if key is None:
                raise ValueError("Tag Key cannot be None")
            # Validate tag key constraints: max 127 chars, not start with "aws:"
            if len(key) > 127:
                raise ValueError("Tag Key exceeds maximum length of 127 characters")
            if key.lower().startswith("aws:"):
                # AWS managed tags can be specified, so allow keys starting with "aws:" only if they exist already?
                # The doc says you can't create keys starting with aws:, but can specify existing AWS managed keys.
                # Here we allow specifying them.
                pass
            if value is not None and len(value) > 256:
                raise ValueError("Tag Value exceeds maximum length of 256 characters")
            instance_tags.append(Tag(key=key, value=value))

        # Update the event window's association target
        # If association_target is None, create new
        if event_window.association_target is None:
            event_window.association_target = InstanceEventWindowAssociationTarget(
                dedicated_host_id_set=[],
                instance_id_set=[],
                tag_set=[],
            )

        # Add the specified targets to the event window's association target
        if dedicated_host_ids:
            # Add new dedicated host ids, avoid duplicates
            for dh_id in dedicated_host_ids:
                if dh_id not in event_window.association_target.dedicated_host_id_set:
                    event_window.association_target.dedicated_host_id_set.append(dh_id)
        elif instance_ids:
            for inst_id in instance_ids:
                if inst_id not in event_window.association_target.instance_id_set:
                    event_window.association_target.instance_id_set.append(inst_id)
        elif instance_tags:
            # Add tags, avoid duplicates by key+value
            existing_tags = {(t.key, t.value) for t in event_window.association_target.tag_set}
            for tag in instance_tags:
                if (tag.key, tag.value) not in existing_tags:
                    event_window.association_target.tag_set.append(tag)

        # Save updated event window back to state
        self.state.event_windows_for_scheduled_events[instance_event_window_id] = event_window

        response = {
            "instanceEventWindow": event_window.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def create_instance_event_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cron_expression = params.get("CronExpression")
        name = params.get("Name")
        tag_specifications_params = params.get("TagSpecification.N", [])
        time_range_params_list = params.get("TimeRange.N", [])
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate that either cron_expression or time_range is specified, but not both
        if cron_expression and time_range_params_list:
            raise ValueError("Cannot specify both CronExpression and TimeRange")

        # Validate cron expression if specified
        if cron_expression:
            # Basic validation: only hour and day of week supported, minute/month/year must be '*'
            # For simplicity, we do not parse fully, just check string format roughly
            # AWS doc example: "* 0-4,20-23 * * 1,5"
            # We skip detailed validation here
            pass

        # Validate time ranges if specified
        time_ranges = []
        for tr_params in time_range_params_list:
            end_hour = tr_params.get("EndHour")
            end_week_day_str = tr_params.get("EndWeekDay")
            start_hour = tr_params.get("StartHour")
            start_week_day_str = tr_params.get("StartWeekDay")

            # Validate hours if specified
            if end_hour is not None and (end_hour < 0 or end_hour > 23):
                raise ValueError("EndHour must be between 0 and 23")
            if start_hour is not None and (start_hour < 0 or start_hour > 23):
                raise ValueError("StartHour must be between 0 and 23")

            # Convert week day strings to WeekDay enum if specified
            end_week_day = None
            start_week_day = None
            if end_week_day_str:
                try:
                    end_week_day = WeekDay[end_week_day_str.upper()]
                except KeyError:
                    raise ValueError(f"Invalid EndWeekDay value: {end_week_day_str}")
            if start_week_day_str:
                try:
                    start_week_day = WeekDay[start_week_day_str.upper()]
                except KeyError:
                    raise ValueError(f"Invalid StartWeekDay value: {start_week_day_str}")

            time_range = InstanceEventWindowTimeRangeRequest(
                end_hour=end_hour,
                end_week_day=end_week_day,
                start_hour=start_hour,
                start_week_day=start_week_day,
            )
            time_ranges.append(time_range)

        # Validate tags from tag_specifications_params
        tags = []
        for tag_spec in tag_specifications_params:
            # tag_spec is dict with ResourceType and Tags
            resource_type = tag_spec.get("ResourceType")
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is None:
                    raise ValueError("Tag Key cannot be None")
                if len(key) > 127:
                    raise ValueError("Tag Key exceeds maximum length of 127 characters")
                if key.lower().startswith("aws:"):
                    # Allow specifying existing AWS managed tag keys
                    pass
                if value is not None and len(value) > 256:
                    raise ValueError("Tag Value exceeds maximum length of 256 characters")
                tags.append(Tag(key=key, value=value))

        # Generate unique event window ID
        instance_event_window_id = self.generate_unique_id()

        # Create InstanceEventWindowTimeRange objects from requests
        time_range_objs = []
        for tr_req in time_ranges:
            time_range_obj = InstanceEventWindowTimeRange(
                end_hour=tr_req.end_hour,
                end_week_day=tr_req.end_week_day,
                start_hour=tr_req.start_hour,
                start_week_day=tr_req.start_week_day,
            )
            time_range_objs.append(time_range_obj)

        # Create the event window object
        event_window = InstanceEventWindow(
            association_target=None,
            cron_expression=cron_expression,
            instance_event_window_id=instance_event_window_id,
            name=name,
            state=InstanceEventWindowState.ACTIVE,
            tag_set=tags,
            time_range_set=time_range_objs,
        )

        # Store in state
        self.state.event_windows_for_scheduled_events[instance_event_window_id] = event_window

        response = {
            "instanceEventWindow": event_window.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_instance_event_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_event_window_id = params.get("InstanceEventWindowId")
        force_delete = params.get("ForceDelete", False)
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not instance_event_window_id:
            raise ValueError("InstanceEventWindowId is required")

        event_window = self.state.event_windows_for_scheduled_events.get(instance_event_window_id)
        if not event_window:
            raise ValueError(f"InstanceEventWindow {instance_event_window_id} not found")

        # Check if event window has associations and force_delete is False
        has_associations = False
        if event_window.association_target:
            if (event_window.association_target.dedicated_host_id_set or
                event_window.association_target.instance_id_set or
                event_window.association_target.tag_set):
                has_associations = True

        if has_associations and not force_delete:
            raise ValueError("Event window is associated with targets. Use ForceDelete to delete.")

        # Mark event window state as deleting
        event_window.state = InstanceEventWindowState.DELETING

        # Remove from state to simulate deletion
        del self.state.event_windows_for_scheduled_events[instance_event_window_id]

        # Return state change info
        state_change = InstanceEventWindowStateChange(
            instance_event_window_id=instance_event_window_id,
            state=InstanceEventWindowState.DELETED,
        )

        response = {
            "instanceEventWindowState": state_change.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_instance_event_windows(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        instance_event_window_ids = params.get("InstanceEventWindowId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate max_results if specified
        if max_results is not None:
            if not (20 <= max_results <= 500):
                raise ValueError("MaxResults must be between 20 and 500")

        # Validate that InstanceEventWindowId.N and filters are not used together with max_results
        if instance_event_window_ids and max_results is not None:
            raise ValueError("Cannot specify both InstanceEventWindowId.N and MaxResults in the same call")

        # Collect all event windows
        all_event_windows = list(self.state.event_windows_for_scheduled_events.values())

        # Filter by instance_event_window_ids if specified
        if instance_event_window_ids:
            filtered_event_windows = []
            for wid in instance_event_window_ids:
                ew = self.state.event_windows_for_scheduled_events.get(wid)
                if ew:
                    filtered_event_windows.append(ew)
        else:
            filtered_event_windows = all_event_windows

        # Apply filters if specified
        def matches_filter(event_window, filter_name, filter_values):
            # Filter names:
            # dedicated-host-id, event-window-name, instance-id,
            # instance-tag, instance-tag-key, instance-tag-value,
            # tag:<key>, tag-key, tag-value
            if filter_name == "dedicated-host-id":
                if not event_window.association_target:
                    return False
                return any(dh_id in filter_values for dh_id in event_window.association_target.dedicated_host_id_set)
            elif filter_name == "event-window-name":
                if event_window.name is None:
                    return False
                return event_window.name in filter_values
            elif filter_name == "instance-id":
                if not event_window.association_target:
                    return False
                return any(inst_id in filter_values for inst_id in event_window.association_target.instance_id_set)
            elif filter_name == "instance-tag":
                if not event_window.association_target:
                    return False
                # instance-tag filter is key=value pairs
                for val in filter_values:
                    if "=" not in val:
                        continue
                    key, value = val.split("=", 1)
                    for tag in event_window.association_target.tag_set:
                        if tag.key == key and tag.value == value:
                            return True
                return False
            elif filter_name == "instance-tag-key":
                if not event_window.association_target:
                    return False
                for key in filter_values:
                    for tag in event_window.association_target.tag_set:
                        if tag.key == key:
                            return True
                return False
            elif filter_name == "instance-tag-value":
                if not event_window.association_target:
                    return False
                for value in filter_values:
                    for tag in event_window.association_target.tag_set:
                        if tag.value == value:
                            return True
                return False
            elif filter_name.startswith("tag:"):
                # tag:<key> filter, filter_values are values for that key
                tag_key = filter_name[4:]
                for tag in event_window.tag_set:
                    if tag.key == tag_key and tag.value in filter_values:
                        return True
                return False
            elif filter_name == "tag-key":
                for key in filter_values:
                    for tag in event_window.tag_set:
                        if tag.key == key:
                            return True
                return False
            elif filter_name == "tag-value":
                for value in filter_values:
                    for tag in event_window.tag_set:
                        if tag.value == value:
                            return True
                return False
            else:
                # Unknown filter, ignore
                return True

        if filters:
            # filters is list of dicts with Name and Values
            filtered = []
            for ew in filtered_event_windows:
                match_all = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not matches_filter(ew, name, values):
                        match_all = False
                        break
                if match_all:
                    filtered.append(ew)
            filtered_event_windows = filtered

        # Pagination support
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 500  # default max

        end_index = start_index + max_results
        paged_event_windows = filtered_event_windows[start_index:end_index]

        new_next_token = None
        if end_index < len(filtered_event_windows):
            new_next_token = str(end_index)

        response = {
            "instanceEventWindowSet": [ew.to_dict() for ew in paged_event_windows],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def disassociate_instance_event_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_event_window_id = params.get("InstanceEventWindowId")
        association_target_params = params.get("AssociationTarget")
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not instance_event_window_id:
            raise ValueError("InstanceEventWindowId is required")

        if not association_target_params:
            raise ValueError("AssociationTarget is required")

        event_window = self.state.event_windows_for_scheduled_events.get(instance_event_window_id)
        if not event_window:
            raise ValueError(f"InstanceEventWindow {instance_event_window_id} not found")

        dedicated_host_ids = association_target_params.get("DedicatedHostIds", [])
        instance_ids = association_target_params.get("InstanceIds", [])
        instance_tags_params = association_target_params.get("InstanceTags", [])

        count_targets = sum(bool(x) for x in [dedicated_host_ids, instance_ids, instance_tags_params])
        if count_targets == 0:
            raise ValueError("At least one target type must be specified in AssociationTarget")
        if count_targets > 1:
            raise ValueError("Only one type of target (DedicatedHostIds, InstanceIds, or InstanceTags) can be specified")

        if event_window.association_target is None:
            # Nothing to disassociate
            # Return event window as is
            response = {
                "instanceEventWindow": event_window.to_dict(),
                "requestId": self.generate_request_id(),
            }
            return response

        if dedicated_host_ids:
            # Remove specified dedicated host ids if present
            event_window.association_target.dedicated_host_id_set = [
                dh_id for dh_id in event_window.association_target.dedicated_host_id_set if dh_id not in dedicated_host_ids
            ]
        elif instance_ids:
            event_window.association_target.instance_id_set = [
                inst_id for inst_id in event_window.association_target.instance_id_set if inst_id not in instance_ids
            ]
        elif instance_tags_params:
            # Convert instance_tags_params to Tag objects for comparison
            tags_to_remove = []
            for tag_dict in instance_tags_params:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is None:
                    raise ValueError("Tag Key cannot be None")
                tags_to_remove.append((key, value))

            # Remove tags matching key and value
            event_window.association_target.tag_set = [
                tag for tag in event_window.association_target.tag_set if (tag.key, tag.value) not in tags_to_remove
            ]

        # Save updated event window back to state
        self.state.event_windows_for_scheduled_events[instance_event_window_id] = event_window

        response = {
            "instanceEventWindow": event_window.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response

    def modify_instance_event_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_event_window_id = params.get("InstanceEventWindowId")
        if not instance_event_window_id:
            raise ValueError("InstanceEventWindowId is required")

        event_window = self.state.event_windows_for_scheduled_events.get(instance_event_window_id)
        if not event_window:
            raise ValueError(f"InstanceEventWindow with id {instance_event_window_id} does not exist")

        # Validate that either TimeRange or CronExpression is provided, but not both
        time_ranges_param = params.get("TimeRange")
        cron_expression_param = params.get("CronExpression")

        if time_ranges_param and cron_expression_param:
            raise ValueError("Cannot specify both TimeRange and CronExpression")

        # Update name if provided
        name_param = params.get("Name")
        if name_param is not None:
            event_window.name = name_param

        # Update cron expression if provided
        if cron_expression_param is not None:
            # Validate cron expression format (basic validation)
            # According to docs: only hour and day of week supported, minute/month/year must be '*'
            # Example: "* 0-4,20-23 * * 1,5"
            # We do minimal validation here: string type and non-empty
            if not isinstance(cron_expression_param, str) or not cron_expression_param.strip():
                raise ValueError("Invalid CronExpression")
            event_window.cron_expression = cron_expression_param
            # Clear time ranges if cron expression is set
            event_window.time_range_set = []

        # Update time ranges if provided
        if time_ranges_param is not None:
            if not isinstance(time_ranges_param, list):
                raise ValueError("TimeRange must be a list")
            new_time_ranges = []
            for tr in time_ranges_param:
                if not isinstance(tr, dict):
                    raise ValueError("Each TimeRange must be a dict")
                end_hour = tr.get("EndHour")
                end_week_day = tr.get("EndWeekDay")
                start_hour = tr.get("StartHour")
                start_week_day = tr.get("StartWeekDay")

                # Validate hours if provided
                if end_hour is not None:
                    if not isinstance(end_hour, int) or not (0 <= end_hour <= 23):
                        raise ValueError("EndHour must be integer between 0 and 23")
                if start_hour is not None:
                    if not isinstance(start_hour, int) or not (0 <= start_hour <= 23):
                        raise ValueError("StartHour must be integer between 0 and 23")

                # Validate week days if provided
                valid_week_days = {"sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"}
                if end_week_day is not None:
                    if not isinstance(end_week_day, str) or end_week_day.lower() not in valid_week_days:
                        raise ValueError("EndWeekDay must be one of sunday, monday, tuesday, wednesday, thursday, friday, saturday")
                    end_week_day_enum = WeekDay[end_week_day.upper()]
                else:
                    end_week_day_enum = None
                if start_week_day is not None:
                    if not isinstance(start_week_day, str) or start_week_day.lower() not in valid_week_days:
                        raise ValueError("StartWeekDay must be one of sunday, monday, tuesday, wednesday, thursday, friday, saturday")
                    start_week_day_enum = WeekDay[start_week_day.upper()]
                else:
                    start_week_day_enum = None

                time_range_obj = InstanceEventWindowTimeRange(
                    end_hour=end_hour,
                    end_week_day=end_week_day_enum,
                    start_hour=start_hour,
                    start_week_day=start_week_day_enum,
                )
                new_time_ranges.append(time_range_obj)
            event_window.time_range_set = new_time_ranges
            # Clear cron expression if time ranges are set
            event_window.cron_expression = None

        # Compose response
        response = {
            "instanceEventWindow": event_window.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class EventwindowsforscheduledeventsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateInstanceEventWindow", self.associate_instance_event_window)
        self.register_action("CreateInstanceEventWindow", self.create_instance_event_window)
        self.register_action("DeleteInstanceEventWindow", self.delete_instance_event_window)
        self.register_action("DescribeInstanceEventWindows", self.describe_instance_event_windows)
        self.register_action("DisassociateInstanceEventWindow", self.disassociate_instance_event_window)
        self.register_action("ModifyInstanceEventWindow", self.modify_instance_event_window)

    def associate_instance_event_window(self, params):
        return self.backend.associate_instance_event_window(params)

    def create_instance_event_window(self, params):
        return self.backend.create_instance_event_window(params)

    def delete_instance_event_window(self, params):
        return self.backend.delete_instance_event_window(params)

    def describe_instance_event_windows(self, params):
        return self.backend.describe_instance_event_windows(params)

    def disassociate_instance_event_window(self, params):
        return self.backend.disassociate_instance_event_window(params)

    def modify_instance_event_window(self, params):
        return self.backend.modify_instance_event_window(params)
