from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class CapacityReservationTopology:
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    capacityBlockId: Optional[str] = None
    capacityReservationId: Optional[str] = None
    groupName: Optional[str] = None
    instanceType: Optional[str] = None
    networkNodeSet: Optional[List[str]] = field(default_factory=list)
    state: Optional[ResourceState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "capacityBlockId": self.capacityBlockId,
            "capacityReservationId": self.capacityReservationId,
            "groupName": self.groupName,
            "instanceType": self.instanceType,
            "networkNodeSet": self.networkNodeSet if self.networkNodeSet else None,
            "state": self.state.value if self.state else None,
        }


@dataclass
class InstanceTopology:
    availabilityZone: Optional[str] = None
    capacityBlockId: Optional[str] = None
    groupName: Optional[str] = None
    instanceId: Optional[str] = None
    instanceType: Optional[str] = None
    networkNodeSet: Optional[List[str]] = field(default_factory=list)
    zoneId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availabilityZone,
            "capacityBlockId": self.capacityBlockId,
            "groupName": self.groupName,
            "instanceId": self.instanceId,
            "instanceType": self.instanceType,
            "networkNodeSet": self.networkNodeSet if self.networkNodeSet else None,
            "zoneId": self.zoneId,
        }


class Ec2TopologyBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.ec2_topology dict for storage
        # Structure:
        # self.state.ec2_topology["capacity_reservations"][capacity_reservation_id] = CapacityReservationTopology(...)
        # self.state.ec2_topology["instances"][instance_id] = InstanceTopology(...)
        if not hasattr(self.state, "ec2_topology"):
            self.state.ec2_topology = {
                "capacity_reservations": {},
                "instances": {},
            }

    def _validate_filters(self, filters: List[Dict[str, Any]], allowed_filter_names: List[str]) -> None:
        if not isinstance(filters, list):
            raise ErrorCode.InvalidParameterValue("Filter.N must be a list")
        for f in filters:
            if not isinstance(f, dict):
                raise ErrorCode.InvalidParameterValue("Each filter must be a dict")
            name = f.get("Name")
            values = f.get("Values")
            if name is None or not isinstance(name, str):
                raise ErrorCode.InvalidParameterValue("Filter Name must be a string")
            if name not in allowed_filter_names:
                raise ErrorCode.InvalidParameterValue(f"Filter name '{name}' is not supported")
            if values is None or not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                raise ErrorCode.InvalidParameterValue("Filter Values must be a list of strings")

    def _filter_capacity_reservations(
        self,
        capacity_reservations: List[CapacityReservationTopology],
        filters: Optional[List[Dict[str, Any]]],
        capacity_reservation_ids: Optional[List[str]],
    ) -> List[CapacityReservationTopology]:
        # Filter by capacityReservationId if provided
        if capacity_reservation_ids is not None:
            capacity_reservations = [
                cr for cr in capacity_reservations if cr.capacityReservationId in capacity_reservation_ids
            ]

        if not filters:
            return capacity_reservations

        # Supported filters:
        # availability-zone, instance-type
        filtered = capacity_reservations
        for f in filters:
            name = f["Name"]
            values = f["Values"]
            if name == "availability-zone":
                filtered = [
                    cr for cr in filtered if cr.availabilityZone is not None and any(self._wildcard_match(cr.availabilityZone, v) for v in values)
                ]
            elif name == "instance-type":
                filtered = [
                    cr for cr in filtered if cr.instanceType is not None and any(self._wildcard_match(cr.instanceType, v) for v in values)
                ]
            else:
                # Should not happen due to validation
                pass
        return filtered

    def _filter_instances(
        self,
        instances: List[InstanceTopology],
        filters: Optional[List[Dict[str, Any]]],
        group_names: Optional[List[str]],
        instance_ids: Optional[List[str]],
    ) -> List[InstanceTopology]:
        # Filter by instanceId if provided
        if instance_ids is not None:
            instances = [inst for inst in instances if inst.instanceId in instance_ids]

        # Filter by groupName if provided
        if group_names is not None:
            instances = [inst for inst in instances if inst.groupName in group_names]

        if not filters:
            return instances

        # Supported filters:
        # availability-zone, instance-type, zone-id
        filtered = instances
        for f in filters:
            name = f["Name"]
            values = f["Values"]
            if name == "availability-zone":
                filtered = [
                    inst for inst in filtered if inst.availabilityZone is not None and any(self._wildcard_match(inst.availabilityZone, v) for v in values)
                ]
            elif name == "instance-type":
                filtered = [
                    inst for inst in filtered if inst.instanceType is not None and any(self._wildcard_match(inst.instanceType, v) for v in values)
                ]
            elif name == "zone-id":
                filtered = [
                    inst for inst in filtered if inst.zoneId is not None and any(self._wildcard_match(inst.zoneId, v) for v in values)
                ]
            else:
                # Should not happen due to validation
                pass
        return filtered

    def _wildcard_match(self, text: str, pattern: str) -> bool:
        # Support * and ? wildcards
        import fnmatch

        return fnmatch.fnmatch(text, pattern)

    def DescribeCapacityReservationTopology(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        # CapacityReservationId.N - list of strings, max 100
        capacity_reservation_ids = None
        for key in params:
            if key.startswith("CapacityReservationId."):
                if capacity_reservation_ids is None:
                    capacity_reservation_ids = []
                val = params[key]
                if not isinstance(val, str):
                    raise ErrorCode.InvalidParameterValue(f"{key} must be a string")
                capacity_reservation_ids.append(val)
        if capacity_reservation_ids is not None and len(capacity_reservation_ids) > 100:
            raise ErrorCode.InvalidParameterValue("Maximum 100 CapacityReservationId values allowed")

        # MaxResults - int between 1 and 10, default 10
        max_results = params.get("MaxResults", 10)
        if not isinstance(max_results, int) or not (1 <= max_results <= 10):
            raise ErrorCode.InvalidParameterValue("MaxResults must be an integer between 1 and 10")

        # NextToken - string or None
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode.InvalidParameterValue("NextToken must be a string")

        # Filter.N - list of Filter objects
        filters = []
        # Collect filters from params keys like Filter.1.Name, Filter.1.Values.1, etc.
        # We parse filters by index
        filter_indices = set()
        for key in params:
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    try:
                        idx = int(parts[1])
                        filter_indices.add(idx)
                    except Exception:
                        pass
        for idx in sorted(filter_indices):
            name_key = f"Filter.{idx}.Name"
            values_prefix = f"Filter.{idx}.Values."
            if name_key not in params:
                raise ErrorCode.InvalidParameterValue(f"Filter.{idx}.Name is required")
            name_val = params[name_key]
            if not isinstance(name_val, str):
                raise ErrorCode.InvalidParameterValue(f"Filter.{idx}.Name must be a string")
            # Collect values
            values = []
            for key in params:
                if key.startswith(values_prefix):
                    val = params[key]
                    if not isinstance(val, str):
                        raise ErrorCode.InvalidParameterValue(f"{key} must be a string")
                    values.append(val)
            if not values:
                raise ErrorCode.InvalidParameterValue(f"Filter.{idx}.Values must have at least one value")
            filters.append({"Name": name_val, "Values": values})

        # Validate filters names for capacity reservation
        allowed_filter_names = ["availability-zone", "instance-type"]
        self._validate_filters(filters, allowed_filter_names)

        # Cannot specify MaxResults and CapacityReservationId.N together
        if max_results != 10 and capacity_reservation_ids is not None:
            raise ErrorCode.InvalidParameterCombination("Cannot specify MaxResults and CapacityReservationId.N together")

        # Fetch all capacity reservations from state
        capacity_reservations_dict = self.state.ec2_topology.get("capacity_reservations", {})
        capacity_reservations = list(capacity_reservations_dict.values())

        # Filter capacity reservations
        filtered = self._filter_capacity_reservations(capacity_reservations, filters, capacity_reservation_ids)

        # Pagination with NextToken
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index > len(filtered):
                    raise ErrorCode.InvalidParameterValue("Invalid NextToken value")
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken value")

        end_index = start_index + max_results
        page = filtered[start_index:end_index]

        # Prepare response list
        capacity_reservation_set = [cr.to_dict() for cr in page]

        # NextToken for pagination
        new_next_token = str(end_index) if end_index < len(filtered) else None

        # Generate requestId
        request_id = self.generate_request_id()

        return {
            "capacityReservationSet": capacity_reservation_set,
            "nextToken": new_next_token,
            "requestId": request_id,
        }

    def DescribeInstanceTopology(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        # GroupName.N - list of strings max 100
        group_names = None
        for key in params:
            if key.startswith("GroupName."):
                if group_names is None:
                    group_names = []
                val = params[key]
                if not isinstance(val, str):
                    raise ErrorCode.InvalidParameterValue(f"{key} must be a string")
                group_names.append(val)
        if group_names is not None and len(group_names) > 100:
            raise ErrorCode.InvalidParameterValue("Maximum 100 GroupName values allowed")

        # InstanceId.N - list of strings max 100
        instance_ids = None
        for key in params:
            if key.startswith("InstanceId."):
                if instance_ids is None:
                    instance_ids = []
                val = params[key]
                if not isinstance(val, str):
                    raise ErrorCode.InvalidParameterValue(f"{key} must be a string")
                instance_ids.append(val)
        if instance_ids is not None and len(instance_ids) > 100:
            raise ErrorCode.InvalidParameterValue("Maximum 100 InstanceId values allowed")

        # MaxResults - int between 1 and 100, default 20
        max_results = params.get("MaxResults", 20)
        if not isinstance(max_results, int) or not (1 <= max_results <= 100):
            raise ErrorCode.InvalidParameterValue("MaxResults must be an integer between 1 and 100")

        # NextToken - string or None
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode.InvalidParameterValue("NextToken must be a string")

        # Filter.N - list of Filter objects
        filters = []
        filter_indices = set()
        for key in params:
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    try:
                        idx = int(parts[1])
                        filter_indices.add(idx)
                    except Exception:
                        pass
        for idx in sorted(filter_indices):
            name_key = f"Filter.{idx}.Name"
            values_prefix = f"Filter.{idx}.Values."
            if name_key not in params:
                raise ErrorCode.InvalidParameterValue(f"Filter.{idx}.Name is required")
            name_val = params[name_key]
            if not isinstance(name_val, str):
                raise ErrorCode.InvalidParameterValue(f"Filter.{idx}.Name must be a string")
            values = []
            for key in params:
                if key.startswith(values_prefix):
                    val = params[key]
                    if not isinstance(val, str):
                        raise ErrorCode.InvalidParameterValue(f"{key} must be a string")
                    values.append(val)
            if not values:
                raise ErrorCode.InvalidParameterValue(f"Filter.{idx}.Values must have at least one value")
            filters.append({"Name": name_val, "Values": values})

        # Validate filters names for instance topology
        allowed_filter_names = ["availability-zone", "instance-type", "zone-id"]
        self._validate_filters(filters, allowed_filter_names)

        # Cannot specify MaxResults and InstanceId.N together
        if max_results != 20 and instance_ids is not None:
            raise ErrorCode.InvalidParameterCombination("Cannot specify MaxResults and InstanceId.N together")

        # Fetch all instances from state
        instances_dict = self.state.ec2_topology.get("instances", {})
        instances = list(instances_dict.values())

        # Filter instances
        filtered = self._filter_instances(instances, filters, group_names, instance_ids)

        # Pagination with NextToken
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index > len(filtered):
                    raise ErrorCode.InvalidParameterValue("Invalid NextToken value")
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken value")

        end_index = start_index + max_results
        page = filtered[start_index:end_index]

        # Prepare response list
        instance_set = [inst.to_dict() for inst in page]

        # NextToken for pagination
        new_next_token = str(end_index) if end_index < len(filtered) else None

        # Generate requestId
        request_id = self.generate_request_id()

        return {
            "instanceSet": instance_set,
            "nextToken": new_next_token,
            "requestId": request_id,
        }

from emulator_core.gateway.base import BaseGateway

class EC2topologyGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeCapacityReservationTopology", self.describe_capacity_reservation_topology)
        self.register_action("DescribeInstanceTopology", self.describe_instance_topology)

    def describe_capacity_reservation_topology(self, params):
        return self.backend.describe_capacity_reservation_topology(params)

    def describe_instance_topology(self, params):
        return self.backend.describe_instance_topology(params)
