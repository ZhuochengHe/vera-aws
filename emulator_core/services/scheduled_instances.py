from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class Frequency(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


@dataclass
class ScheduledInstanceRecurrence:
    frequency: Optional[Frequency] = None
    interval: Optional[int] = None
    occurrence_day_set: Optional[List[int]] = None
    occurrence_relative_to_end: Optional[bool] = None
    occurrence_unit: Optional[str] = None

    @classmethod
    def from_request(cls, data: Dict[str, Any]) -> "ScheduledInstanceRecurrence":
        freq_str = data.get("Frequency")
        frequency = None
        if freq_str:
            try:
                frequency = Frequency(freq_str)
            except ValueError:
                raise ErrorCode("InvalidFrequency", f"Frequency must be one of {list(f.value for f in Frequency)}")

        interval = data.get("Interval")
        if interval is not None:
            if not isinstance(interval, int) or interval < 1:
                raise ErrorCode("InvalidInterval", "Interval must be a positive integer")

        occurrence_day_set = data.get("OccurrenceDays")
        if occurrence_day_set is not None:
            if not isinstance(occurrence_day_set, list) or not all(isinstance(d, int) for d in occurrence_day_set):
                raise ErrorCode("InvalidOccurrenceDays", "OccurrenceDays must be a list of integers")

        occurrence_relative_to_end = data.get("OccurrenceRelativeToEnd")
        if occurrence_relative_to_end is not None and not isinstance(occurrence_relative_to_end, bool):
            raise ErrorCode("InvalidOccurrenceRelativeToEnd", "OccurrenceRelativeToEnd must be a boolean")

        occurrence_unit = data.get("OccurrenceUnit")
        if occurrence_unit is not None and not isinstance(occurrence_unit, str):
            raise ErrorCode("InvalidOccurrenceUnit", "OccurrenceUnit must be a string")

        # Validate combinations:
        if frequency == Frequency.DAILY:
            if occurrence_day_set is not None:
                raise ErrorCode("InvalidParameterCombination", "OccurrenceDays cannot be specified with Daily frequency")
            if occurrence_relative_to_end is not None:
                raise ErrorCode("InvalidParameterCombination", "OccurrenceRelativeToEnd cannot be specified with Daily frequency")
            if occurrence_unit is not None:
                raise ErrorCode("InvalidParameterCombination", "OccurrenceUnit cannot be specified with Daily frequency")
        elif frequency == Frequency.WEEKLY:
            if occurrence_unit is not None:
                raise ErrorCode("InvalidParameterCombination", "OccurrenceUnit cannot be specified with Weekly frequency")
        elif frequency == Frequency.MONTHLY:
            if occurrence_day_set is None:
                raise ErrorCode("MissingParameter", "OccurrenceDays is required for Monthly frequency")
            if occurrence_unit is None:
                raise ErrorCode("MissingParameter", "OccurrenceUnit is required for Monthly frequency")

        return cls(
            frequency=frequency,
            interval=interval,
            occurrence_day_set=occurrence_day_set,
            occurrence_relative_to_end=occurrence_relative_to_end,
            occurrence_unit=occurrence_unit,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frequency": self.frequency.value if self.frequency else None,
            "interval": self.interval,
            "occurrenceDaySet": self.occurrence_day_set,
            "occurrenceRelativeToEnd": self.occurrence_relative_to_end,
            "occurrenceUnit": self.occurrence_unit,
        }


@dataclass
class ScheduledInstanceAvailability:
    availability_zone: Optional[str] = None
    available_instance_count: Optional[int] = None
    first_slot_start_time: Optional[datetime] = None
    hourly_price: Optional[str] = None
    instance_type: Optional[str] = None
    max_term_duration_in_days: Optional[int] = None
    min_term_duration_in_days: Optional[int] = None
    network_platform: Optional[str] = None
    platform: Optional[str] = None
    purchase_token: Optional[str] = None
    recurrence: Optional[ScheduledInstanceRecurrence] = None
    slot_duration_in_hours: Optional[int] = None
    total_scheduled_instance_hours: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "availableInstanceCount": self.available_instance_count,
            "firstSlotStartTime": self.first_slot_start_time.isoformat() if self.first_slot_start_time else None,
            "hourlyPrice": self.hourly_price,
            "instanceType": self.instance_type,
            "maxTermDurationInDays": self.max_term_duration_in_days,
            "minTermDurationInDays": self.min_term_duration_in_days,
            "networkPlatform": self.network_platform,
            "platform": self.platform,
            "purchaseToken": self.purchase_token,
            "recurrence": self.recurrence.to_dict() if self.recurrence else None,
            "slotDurationInHours": self.slot_duration_in_hours,
            "totalScheduledInstanceHours": self.total_scheduled_instance_hours,
        }


@dataclass
class ScheduledInstance:
    scheduled_instance_id: str
    availability_zone: Optional[str] = None
    create_date: Optional[datetime] = None
    hourly_price: Optional[str] = None
    instance_count: Optional[int] = None
    instance_type: Optional[str] = None
    network_platform: Optional[str] = None
    next_slot_start_time: Optional[datetime] = None
    platform: Optional[str] = None
    previous_slot_end_time: Optional[datetime] = None
    recurrence: Optional[ScheduledInstanceRecurrence] = None
    slot_duration_in_hours: Optional[int] = None
    term_end_date: Optional[datetime] = None
    term_start_date: Optional[datetime] = None
    total_scheduled_instance_hours: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "createDate": self.create_date.isoformat() if self.create_date else None,
            "hourlyPrice": self.hourly_price,
            "instanceCount": self.instance_count,
            "instanceType": self.instance_type,
            "networkPlatform": self.network_platform,
            "nextSlotStartTime": self.next_slot_start_time.isoformat() if self.next_slot_start_time else None,
            "platform": self.platform,
            "previousSlotEndTime": self.previous_slot_end_time.isoformat() if self.previous_slot_end_time else None,
            "recurrence": self.recurrence.to_dict() if self.recurrence else None,
            "scheduledInstanceId": self.scheduled_instance_id,
            "slotDurationInHours": self.slot_duration_in_hours,
            "termEndDate": self.term_end_date.isoformat() if self.term_end_date else None,
            "termStartDate": self.term_start_date.isoformat() if self.term_start_date else None,
            "totalScheduledInstanceHours": self.total_scheduled_instance_hours,
        }


class ScheduledInstancesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.scheduled_instances dict for storage

    def _validate_filters(self, filters: List[Dict[str, Any]]) -> None:
        # Validate filter structure and values
        if not isinstance(filters, list):
            raise ErrorCode("InvalidParameter", "Filter must be a list")
        for f in filters:
            if not isinstance(f, dict):
                raise ErrorCode("InvalidParameter", "Each filter must be a dict")
            if "Name" not in f or not isinstance(f["Name"], str):
                raise ErrorCode("InvalidParameter", "Filter Name must be a string")
            if "Values" not in f or not isinstance(f["Values"], list) or not all(isinstance(v, str) for v in f["Values"]):
                raise ErrorCode("InvalidParameter", "Filter Values must be a list of strings")

    def _apply_filters_to_availability(self, availabilities: List[ScheduledInstanceAvailability], filters: List[Dict[str, Any]]) -> List[ScheduledInstanceAvailability]:
        # Supported filters: availability-zone, instance-type, platform
        if not filters:
            return availabilities
        filtered = availabilities
        for f in filters:
            name = f["Name"]
            values = f["Values"]
            if name == "availability-zone":
                filtered = [a for a in filtered if a.availability_zone in values]
            elif name == "instance-type":
                filtered = [a for a in filtered if a.instance_type in values]
            elif name == "platform":
                filtered = [a for a in filtered if a.platform in values]
            else:
                # Unknown filter: ignore or raise? AWS ignores unknown filters silently.
                pass
        return filtered

    def _apply_filters_to_scheduled_instances(self, instances: List[ScheduledInstance], filters: List[Dict[str, Any]]) -> List[ScheduledInstance]:
        # Supported filters: availability-zone, instance-type, platform
        if not filters:
            return instances
        filtered = instances
        for f in filters:
            name = f["Name"]
            values = f["Values"]
            if name == "availability-zone":
                filtered = [i for i in filtered if i.availability_zone in values]
            elif name == "instance-type":
                filtered = [i for i in filtered if i.instance_type in values]
            elif name == "platform":
                filtered = [i for i in filtered if i.platform in values]
            else:
                # Unknown filter: ignore
                pass
        return filtered

    def DescribeScheduledInstanceAvailability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun
        if "DryRun" in params:
            if not isinstance(params["DryRun"], bool):
                raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")
            if params["DryRun"]:
                # We assume user has permission for simplicity
                raise ErrorCode("DryRunOperation", "DryRun successful")

        # Validate required FirstSlotStartTimeRange
        fst_range = params.get("FirstSlotStartTimeRange")
        if not fst_range or not isinstance(fst_range, dict):
            raise ErrorCode("MissingParameter", "FirstSlotStartTimeRange is required and must be a dict")
        earliest_time_str = fst_range.get("EarliestTime")
        latest_time_str = fst_range.get("LatestTime")
        if not earliest_time_str or not latest_time_str:
            raise ErrorCode("MissingParameter", "EarliestTime and LatestTime are required in FirstSlotStartTimeRange")
        try:
            earliest_time = datetime.fromisoformat(earliest_time_str)
            latest_time = datetime.fromisoformat(latest_time_str)
        except Exception:
            raise ErrorCode("InvalidParameterValue", "EarliestTime and LatestTime must be valid ISO8601 timestamps")
        if latest_time < earliest_time:
            raise ErrorCode("InvalidParameterValue", "LatestTime must be later than or equal to EarliestTime")
        if latest_time > datetime.utcnow() + timedelta(days=90):
            raise ErrorCode("InvalidParameterValue", "LatestTime must be at most three months in the future")

        # Validate optional filters
        filters = []
        # Filters come as Filter.N with N=1,2,... We collect all Filter.N keys
        filter_keys = [k for k in params if k.startswith("Filter.")]
        filter_indices = set()
        for k in filter_keys:
            try:
                idx = int(k.split(".")[1])
                filter_indices.add(idx)
            except Exception:
                raise ErrorCode("InvalidParameter", f"Invalid filter key {k}")
        for idx in sorted(filter_indices):
            f = params.get(f"Filter.{idx}")
            if not isinstance(f, list):
                raise ErrorCode("InvalidParameter", f"Filter.{idx} must be a list of filter dicts")
            for filter_obj in f:
                if not isinstance(filter_obj, dict):
                    raise ErrorCode("InvalidParameter", "Each filter must be a dict")
                if "Name" not in filter_obj or "Values" not in filter_obj:
                    raise ErrorCode("InvalidParameter", "Filter must have Name and Values")
                if not isinstance(filter_obj["Name"], str):
                    raise ErrorCode("InvalidParameter", "Filter Name must be a string")
                if not isinstance(filter_obj["Values"], list) or not all(isinstance(v, str) for v in filter_obj["Values"]):
                    raise ErrorCode("InvalidParameter", "Filter Values must be a list of strings")
                filters.append(filter_obj)

        # Validate MaxResults
        max_results = params.get("MaxResults", 300)
        if not isinstance(max_results, int) or max_results < 5 or max_results > 300:
            raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 300")

        # Validate MinSlotDurationInHours and MaxSlotDurationInHours
        min_slot_duration = params.get("MinSlotDurationInHours")
        max_slot_duration = params.get("MaxSlotDurationInHours")
        if min_slot_duration is not None:
            if not isinstance(min_slot_duration, int) or min_slot_duration < 4:
                raise ErrorCode("InvalidParameterValue", "MinSlotDurationInHours must be an integer >= 4")
        if max_slot_duration is not None:
            if not isinstance(max_slot_duration, int) or max_slot_duration <= (min_slot_duration or 0) or max_slot_duration >= 1720:
                raise ErrorCode("InvalidParameterValue", "MaxSlotDurationInHours must be > MinSlotDurationInHours and < 1720")

        # Validate Recurrence (required)
        recurrence_data = params.get("Recurrence")
        if not recurrence_data or not isinstance(recurrence_data, dict):
            raise ErrorCode("MissingParameter", "Recurrence is required and must be a dict")
        recurrence = ScheduledInstanceRecurrence.from_request(recurrence_data)

        # For demonstration, we simulate some available scheduled instances.
        # In real backend, this would query actual availability data.
        # We create a few dummy ScheduledInstanceAvailability objects matching filters and recurrence.

        # For simplicity, create 3 dummy availabilities with different zones, instance types, platforms
        dummy_availabilities = [
            ScheduledInstanceAvailability(
                availability_zone="us-west-2a",
                available_instance_count=10,
                first_slot_start_time=earliest_time + timedelta(hours=1),
                hourly_price="0.10",
                instance_type="c4.large",
                max_term_duration_in_days=365,
                min_term_duration_in_days=365,
                network_platform="EC2-Classic",
                platform="Linux/UNIX",
                purchase_token=self.generate_unique_id(),
                recurrence=recurrence,
                slot_duration_in_hours=min_slot_duration or 4,
                total_scheduled_instance_hours=1200,
            ),
            ScheduledInstanceAvailability(
                availability_zone="us-west-2b",
                available_instance_count=5,
                first_slot_start_time=earliest_time + timedelta(hours=2),
                hourly_price="0.20",
                instance_type="c3.large",
                max_term_duration_in_days=365,
                min_term_duration_in_days=365,
                network_platform="EC2-VPC",
                platform="Windows",
                purchase_token=self.generate_unique_id(),
                recurrence=recurrence,
                slot_duration_in_hours=min_slot_duration or 4,
                total_scheduled_instance_hours=1200,
            ),
            ScheduledInstanceAvailability(
                availability_zone="us-west-2c",
                available_instance_count=8,
                first_slot_start_time=earliest_time + timedelta(hours=3),
                hourly_price="0.15",
                instance_type="m4.large",
                max_term_duration_in_days=365,
                min_term_duration_in_days=365,
                network_platform="EC2-VPC",
                platform="Linux/UNIX",
                purchase_token=self.generate_unique_id(),
                recurrence=recurrence,
                slot_duration_in_hours=min_slot_duration or 4,
                total_scheduled_instance_hours=1200,
            ),
        ]

        # Apply filters
        filtered_availabilities = self._apply_filters_to_availability(dummy_availabilities, filters)

        # Pagination with NextToken is not implemented (always return all up to max_results)
        result_availabilities = filtered_availabilities[:max_results]

        return {
            "requestId": self.generate_request_id(),
            "nextToken": None,
            "scheduledInstanceAvailabilitySet": [a.to_dict() for a in result_availabilities],
        }

    def DescribeScheduledInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun
        if "DryRun" in params:
            if not isinstance(params["DryRun"], bool):
                raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")
            if params["DryRun"]:
                raise ErrorCode("DryRunOperation", "DryRun successful")

        # Validate filters
        filters = []
        filter_keys = [k for k in params if k.startswith("Filter.")]
        filter_indices = set()
        for k in filter_keys:
            try:
                idx = int(k.split(".")[1])
                filter_indices.add(idx)
            except Exception:
                raise ErrorCode("InvalidParameter", f"Invalid filter key {k}")
        for idx in sorted(filter_indices):
            f = params.get(f"Filter.{idx}")
            if not isinstance(f, list):
                raise ErrorCode("InvalidParameter", f"Filter.{idx} must be a list of filter dicts")
            for filter_obj in f:
                if not isinstance(filter_obj, dict):
                    raise ErrorCode("InvalidParameter", "Each filter must be a dict")
                if "Name" not in filter_obj or "Values" not in filter_obj:
                    raise ErrorCode("InvalidParameter", "Filter must have Name and Values")
                if not isinstance(filter_obj["Name"], str):
                    raise ErrorCode("InvalidParameter", "Filter Name must be a string")
                if not isinstance(filter_obj["Values"], list) or not all(isinstance(v, str) for v in filter_obj["Values"]):
                    raise ErrorCode("InvalidParameter", "Filter Values must be a list of strings")
                filters.append(filter_obj)

        # Validate MaxResults
        max_results = params.get("MaxResults", 100)
        if not isinstance(max_results, int) or max_results < 5 or max_results > 300:
            raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 300")

        # Validate ScheduledInstanceId.N
        scheduled_instance_ids = []
        for key in params:
            if key.startswith("ScheduledInstanceId."):
                val = params[key]
                if not isinstance(val, str):
                    raise ErrorCode("InvalidParameter", f"{key} must be a string")
                scheduled_instance_ids.append(val)

        # Validate SlotStartTimeRange if present
        slot_start_time_range = params.get("SlotStartTimeRange")
        earliest_time = None
        latest_time = None
        if slot_start_time_range:
            if not isinstance(slot_start_time_range, dict):
                raise ErrorCode("InvalidParameter", "SlotStartTimeRange must be a dict")
            earliest_time_str = slot_start_time_range.get("EarliestTime")
            latest_time_str = slot_start

from emulator_core.gateway.base import BaseGateway

class ScheduledInstancesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeScheduledInstanceAvailability", self.describe_scheduled_instance_availability)
        self.register_action("DescribeScheduledInstances", self.describe_scheduled_instances)
        self.register_action("PurchaseScheduledInstances", self.purchase_scheduled_instances)
        self.register_action("RunScheduledInstances", self.run_scheduled_instances)

    def describe_scheduled_instance_availability(self, params):
        return self.backend.describe_scheduled_instance_availability(params)

    def describe_scheduled_instances(self, params):
        return self.backend.describe_scheduled_instances(params)

    def purchase_scheduled_instances(self, params):
        return self.backend.purchase_scheduled_instances(params)

    def run_scheduled_instances(self, params):
        return self.backend.run_scheduled_instances(params)
