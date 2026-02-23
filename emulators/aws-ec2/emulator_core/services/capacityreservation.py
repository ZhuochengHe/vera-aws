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
class CapacityReservation:
    availability_zone: str = ""
    availability_zone_id: str = ""
    available_instance_count: int = 0
    capacity_allocation_set: List[Any] = field(default_factory=list)
    capacity_block_id: str = ""
    capacity_reservation_arn: str = ""
    capacity_reservation_fleet_id: str = ""
    capacity_reservation_id: str = ""
    commitment_info: Dict[str, Any] = field(default_factory=dict)
    create_date: str = ""
    delivery_preference: str = ""
    ebs_optimized: bool = False
    end_date: str = ""
    end_date_type: str = ""
    ephemeral_storage: bool = False
    instance_match_criteria: str = ""
    instance_platform: str = ""
    instance_type: str = ""
    interruptible: bool = False
    interruptible_capacity_allocation: Dict[str, Any] = field(default_factory=dict)
    interruption_info: Dict[str, Any] = field(default_factory=dict)
    outpost_arn: str = ""
    owner_id: str = ""
    placement_group_arn: str = ""
    reservation_type: str = ""
    start_date: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    tenancy: str = ""
    total_instance_count: int = 0
    unused_reservation_billing_owner_id: str = ""

    # Internal dependency tracking — not in API response
    ec2_topology_ids: List[str] = field(default_factory=list)  # tracks Ec2Topology children
    instance_ids: List[str] = field(default_factory=list)  # tracks Instance children

    billing_requests: List[Dict[str, Any]] = field(default_factory=list)
    group_arns: List[str] = field(default_factory=list)
    last_modified_date: str = ""
    client_token: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "availableInstanceCount": self.available_instance_count,
            "capacityAllocationSet": self.capacity_allocation_set,
            "capacityBlockId": self.capacity_block_id,
            "capacityReservationArn": self.capacity_reservation_arn,
            "capacityReservationFleetId": self.capacity_reservation_fleet_id,
            "capacityReservationId": self.capacity_reservation_id,
            "commitmentInfo": self.commitment_info,
            "createDate": self.create_date,
            "deliveryPreference": self.delivery_preference,
            "ebsOptimized": self.ebs_optimized,
            "endDate": self.end_date,
            "endDateType": self.end_date_type,
            "ephemeralStorage": self.ephemeral_storage,
            "instanceMatchCriteria": self.instance_match_criteria,
            "instancePlatform": self.instance_platform,
            "instanceType": self.instance_type,
            "interruptible": self.interruptible,
            "interruptibleCapacityAllocation": self.interruptible_capacity_allocation,
            "interruptionInfo": self.interruption_info,
            "outpostArn": self.outpost_arn,
            "ownerId": self.owner_id,
            "placementGroupArn": self.placement_group_arn,
            "reservationType": self.reservation_type,
            "startDate": self.start_date,
            "state": self.state,
            "tagSet": self.tag_set,
            "tenancy": self.tenancy,
            "totalInstanceCount": self.total_instance_count,
            "unusedReservationBillingOwnerId": self.unused_reservation_billing_owner_id,
        }

class CapacityReservation_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.capacity_reservations  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.fast_snapshot_restores.get(params['availability_zone_id']).capacity_reservation_ids.append(new_id)
    #   Delete: self.state.fast_snapshot_restores.get(resource.availability_zone_id).capacity_reservation_ids.remove(resource_id)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            if not params.get(key):
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _get_capacity_reservation_or_error(self, capacity_reservation_id: str, error_code: str = "InvalidCapacityReservationId.NotFound") -> Any:
        resource = self.resources.get(capacity_reservation_id)
        if not resource:
            return create_error_response(error_code, f"The ID '{capacity_reservation_id}' does not exist")
        return resource

    def _ensure_store(self, attr: str) -> Dict[str, Any]:
        if not hasattr(self.state, attr):
            setattr(self.state, attr, {})
        return getattr(self.state, attr)

    def _paginate(self, items: List[Any], max_results: int, next_token: Optional[str]) -> Dict[str, Any]:
        start = int(next_token or 0)
        end = start + max_results
        sliced = items[start:end]
        new_token = str(end) if end < len(items) else None
        return {"items": sliced, "next_token": new_token}


    # - Transformations: _transform_tags(tag_specs: List) -> List[Dict]
    # - State management: _update_state(resource, new_state: str)
    # - Complex operations: _process_associations(params: Dict) -> Dict
    # Add any helper functions needed by the API methods below.
    # These helpers can be used by multiple API methods.

    def AcceptCapacityReservationBillingOwnership(self, params: Dict[str, Any]):
        """Accepts a request to assign billing of the available capacity of a shared Capacity
			Reservation to your account. For more information, seeBilling assignment for shared
					Amazon EC2 Capacity Reservations."""

        error = self._require_params(params, ["CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        updated_requests: List[Dict[str, Any]] = []
        for request in resource.billing_requests:
            if request.get("capacityReservationId") == capacity_reservation_id:
                request["status"] = "accepted"
                request["statusMessage"] = "Request accepted"
                request["lastUpdateTime"] = self._now()
            updated_requests.append(request)
        resource.billing_requests = updated_requests

        return {
            'return': True,
            }

    def AssociateCapacityReservationBillingOwner(self, params: Dict[str, Any]):
        """Initiates a request to assign billing of the unused capacity of a shared Capacity
			Reservation to a consumer account that is consolidated under the same AWS
			organizations payer account. For more information, seeBilling assignment for shared
					Amazon EC2 Capacity Reservations."""

        error = self._require_params(params, ["CapacityReservationId", "UnusedReservationBillingOwnerId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        unused_owner_id = params.get("UnusedReservationBillingOwnerId") or ""
        resource.unused_reservation_billing_owner_id = unused_owner_id

        request = {
            "capacityReservationId": capacity_reservation_id,
            "capacityReservationInfo": resource.to_dict(),
            "lastUpdateTime": self._now(),
            "requestedBy": resource.owner_id or "",
            "status": "pending",
            "statusMessage": "",
            "unusedReservationBillingOwnerId": unused_owner_id,
        }
        resource.billing_requests.append(request)

        return {
            'return': True,
            }

    def CancelCapacityReservation(self, params: Dict[str, Any]):
        """Cancels the specified Capacity Reservation, releases the reserved capacity, and
			changes the Capacity Reservation's state tocancelled. You can cancel a Capacity Reservation that is in the following states: assessing"""

        error = self._require_params(params, ["CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        if getattr(resource, 'ec2_topology_ids', []):
            return create_error_response('DependencyViolation', 'CapacityReservation has dependent Ec2Topology(s) and cannot be deleted.')
        if getattr(resource, 'instance_ids', []):
            return create_error_response('DependencyViolation', 'CapacityReservation has dependent Instance(s) and cannot be deleted.')

        resource.state = "cancelled"
        resource.available_instance_count = 0
        resource.total_instance_count = 0
        resource.last_modified_date = self._now()

        parent = self.state.fast_snapshot_restores.get(resource.availability_zone_id)
        if parent and hasattr(parent, 'capacity_reservation_ids') and resource.capacity_reservation_id in parent.capacity_reservation_ids:
            parent.capacity_reservation_ids.remove(resource.capacity_reservation_id)

        return {
            'return': True,
            }

    def CancelCapacityReservationFleets(self, params: Dict[str, Any]):
        """Cancels one or more Capacity Reservation Fleets. When you cancel a Capacity
			Reservation Fleet, the following happens: The Capacity Reservation Fleet's status changes tocancelled. The individual Capacity Reservations in the Fleet are cancelled. Instances
					running in the Capacity Reservations a"""

        error = self._require_params(params, ["CapacityReservationFleetId.N"])
        if error:
            return error

        fleet_ids = params.get("CapacityReservationFleetId.N", []) or []
        if not fleet_ids:
            return create_error_response("MissingParameter", "Missing required parameter: CapacityReservationFleetId.N")

        fleet_store = self._ensure_store("capacity_reservation_fleets")
        successful: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []

        for fleet_id in fleet_ids:
            fleet = fleet_store.get(fleet_id)
            if not fleet:
                failed.append({
                    "capacityReservationFleetId": fleet_id,
                    "cancelCapacityReservationFleetError": {
                        "code": "InvalidCapacityReservationFleetId.NotFound",
                        "message": f"The ID '{fleet_id}' does not exist",
                    },
                })
                continue

            previous_state = fleet.get("state") or "active"
            fleet["state"] = "cancelled"

            for resource in self.resources.values():
                if resource.capacity_reservation_fleet_id == fleet_id and resource.state != "cancelled":
                    resource.state = "cancelled"
                    resource.available_instance_count = 0
                    resource.total_instance_count = 0
                    resource.last_modified_date = self._now()

            successful.append({
                "capacityReservationFleetId": fleet_id,
                "currentFleetState": "cancelled",
                "previousFleetState": previous_state,
            })

        return {
            'failedFleetCancellationSet': failed,
            'successfulFleetCancellationSet': successful,
            }

    def CreateCapacityReservation(self, params: Dict[str, Any]):
        """Creates a new Capacity Reservation with the specified attributes. Capacity
			Reservations enable you to reserve capacity for your Amazon EC2 instances in a specific
			Availability Zone for any duration. You can create a Capacity Reservation at any time, and you can choose when it starts.
			You ca"""

        error = self._require_params(params, ["InstanceCount", "InstancePlatform", "InstanceType"])
        if error:
            return error

        instance_count = int(params.get("InstanceCount") or 0)
        if instance_count <= 0:
            return create_error_response("InvalidParameterValue", "InstanceCount must be greater than 0")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecifications.N", []) or []:
            tags = spec.get("Tags") or spec.get("Tag") or spec.get("TagSet") or []
            for tag in tags:
                if isinstance(tag, dict):
                    tag_set.append({"Key": tag.get("Key"), "Value": tag.get("Value")})

        now = self._now()
        capacity_reservation_id = self._generate_id("cr")
        availability_zone_id = params.get("AvailabilityZoneId") or ""
        availability_zone = params.get("AvailabilityZone") or ""
        end_date = params.get("EndDate") or ""

        resource = CapacityReservation(
            availability_zone=availability_zone,
            availability_zone_id=availability_zone_id,
            available_instance_count=instance_count,
            capacity_reservation_arn=f"arn:aws:ec2:::capacity-reservation/{capacity_reservation_id}",
            capacity_reservation_id=capacity_reservation_id,
            commitment_info={
                "commitmentEndDate": end_date,
                "committedInstanceCount": instance_count,
            },
            create_date=now,
            delivery_preference=params.get("DeliveryPreference") or "",
            ebs_optimized=str2bool(params.get("EbsOptimized")),
            end_date=end_date,
            end_date_type=params.get("EndDateType") or "",
            ephemeral_storage=str2bool(params.get("EphemeralStorage")),
            instance_match_criteria=params.get("InstanceMatchCriteria") or "open",
            instance_platform=params.get("InstancePlatform") or "",
            instance_type=params.get("InstanceType") or "",
            outpost_arn=params.get("OutpostArn") or "",
            placement_group_arn=params.get("PlacementGroupArn") or "",
            reservation_type="standard",
            start_date=params.get("StartDate") or now,
            state="active",
            tag_set=tag_set,
            tenancy=params.get("Tenancy") or "default",
            total_instance_count=instance_count,
            unused_reservation_billing_owner_id="",
            client_token=params.get("ClientToken") or "",
            last_modified_date=now,
        )
        self.resources[capacity_reservation_id] = resource

        parent = self.state.fast_snapshot_restores.get(availability_zone_id)
        if parent and hasattr(parent, "capacity_reservation_ids"):
            parent.capacity_reservation_ids.append(capacity_reservation_id)

        return {
            'capacityReservation': resource.to_dict(),
            }

    def CreateCapacityReservationBySplitting(self, params: Dict[str, Any]):
        """Create a new Capacity Reservation by splitting the capacity of the source Capacity
			Reservation. The new Capacity Reservation will have the same attributes as the source
			Capacity Reservation except for tags. The source Capacity Reservation must beactiveand owned by your AWS account."""

        error = self._require_params(params, ["InstanceCount", "SourceCapacityReservationId"])
        if error:
            return error

        source_capacity_reservation_id = params.get("SourceCapacityReservationId") or ""
        source = self._get_capacity_reservation_or_error(source_capacity_reservation_id)
        if is_error_response(source):
            return source

        instance_count = int(params.get("InstanceCount") or 0)
        if instance_count <= 0:
            return create_error_response("InvalidParameterValue", "InstanceCount must be greater than 0")
        if instance_count > source.available_instance_count:
            return create_error_response("InvalidParameterValue", "InstanceCount exceeds available capacity")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tags = spec.get("Tags") or spec.get("Tag") or spec.get("TagSet") or []
            for tag in tags:
                if isinstance(tag, dict):
                    tag_set.append({"Key": tag.get("Key"), "Value": tag.get("Value")})

        now = self._now()
        capacity_reservation_id = self._generate_id("cr")
        commitment_end = source.commitment_info.get("commitmentEndDate") if source.commitment_info else ""

        destination = CapacityReservation(
            availability_zone=source.availability_zone,
            availability_zone_id=source.availability_zone_id,
            available_instance_count=instance_count,
            capacity_reservation_arn=f"arn:aws:ec2:::capacity-reservation/{capacity_reservation_id}",
            capacity_reservation_id=capacity_reservation_id,
            commitment_info={
                "commitmentEndDate": commitment_end,
                "committedInstanceCount": instance_count,
            },
            create_date=now,
            delivery_preference=source.delivery_preference,
            ebs_optimized=source.ebs_optimized,
            end_date=source.end_date,
            end_date_type=source.end_date_type,
            ephemeral_storage=source.ephemeral_storage,
            instance_match_criteria=source.instance_match_criteria,
            instance_platform=source.instance_platform,
            instance_type=source.instance_type,
            interruptible=source.interruptible,
            interruptible_capacity_allocation=dict(source.interruptible_capacity_allocation),
            interruption_info=dict(source.interruption_info),
            outpost_arn=source.outpost_arn,
            owner_id=source.owner_id,
            placement_group_arn=source.placement_group_arn,
            reservation_type=source.reservation_type,
            start_date=source.start_date,
            state=source.state or "active",
            tag_set=tag_set,
            tenancy=source.tenancy,
            total_instance_count=instance_count,
            unused_reservation_billing_owner_id=source.unused_reservation_billing_owner_id,
            client_token=params.get("ClientToken") or "",
            last_modified_date=now,
        )
        self.resources[capacity_reservation_id] = destination

        source.available_instance_count -= instance_count
        source.total_instance_count -= instance_count
        if source.commitment_info is not None:
            source.commitment_info["committedInstanceCount"] = source.total_instance_count
        source.last_modified_date = now

        parent = self.state.fast_snapshot_restores.get(source.availability_zone_id)
        if parent and hasattr(parent, "capacity_reservation_ids"):
            parent.capacity_reservation_ids.append(capacity_reservation_id)

        return {
            'destinationCapacityReservation': destination.to_dict(),
            'instanceCount': instance_count,
            'sourceCapacityReservation': source.to_dict(),
            }

    def CreateCapacityReservationFleet(self, params: Dict[str, Any]):
        """Creates a Capacity Reservation Fleet. For more information, seeCreate a
				Capacity Reservation Fleetin theAmazon EC2 User Guide."""

        error = self._require_params(params, ["InstanceTypeSpecification.N", "TotalTargetCapacity"])
        if error:
            return error

        specs = params.get("InstanceTypeSpecification.N", []) or []
        if not specs:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceTypeSpecification.N")

        total_target = int(params.get("TotalTargetCapacity") or 0)
        if total_target <= 0:
            return create_error_response("InvalidParameterValue", "TotalTargetCapacity must be greater than 0")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tags = spec.get("Tags") or spec.get("Tag") or spec.get("TagSet") or []
            for tag in tags:
                if isinstance(tag, dict):
                    tag_set.append({"Key": tag.get("Key"), "Value": tag.get("Value")})

        now = self._now()
        fleet_id = self._generate_id("crf")
        instance_match = params.get("InstanceMatchCriteria") or "open"
        allocation_strategy = params.get("AllocationStrategy") or "prioritized"
        tenancy = params.get("Tenancy") or "default"
        end_date = params.get("EndDate") or ""

        allocation_counts: List[int] = []
        remaining = total_target
        for index, _ in enumerate(specs):
            count = remaining // (len(specs) - index)
            allocation_counts.append(count)
            remaining -= count

        fleet_capacity_set: List[Dict[str, Any]] = []
        total_fulfilled = 0
        for spec, count in zip(specs, allocation_counts):
            if count <= 0:
                continue
            capacity_reservation_id = self._generate_id("cr")
            availability_zone = spec.get("AvailabilityZone") or ""
            availability_zone_id = spec.get("AvailabilityZoneId") or ""
            instance_type = spec.get("InstanceType") or ""
            instance_platform = spec.get("InstancePlatform") or params.get("InstancePlatform") or ""
            ebs_optimized = str2bool(spec.get("EbsOptimized"))
            weight = spec.get("Weight") or 1
            priority = spec.get("Priority") or 0

            resource = CapacityReservation(
                availability_zone=availability_zone,
                availability_zone_id=availability_zone_id,
                available_instance_count=count,
                capacity_reservation_arn=f"arn:aws:ec2:::capacity-reservation/{capacity_reservation_id}",
                capacity_reservation_fleet_id=fleet_id,
                capacity_reservation_id=capacity_reservation_id,
                commitment_info={
                    "commitmentEndDate": end_date,
                    "committedInstanceCount": count,
                },
                create_date=now,
                delivery_preference="",
                ebs_optimized=ebs_optimized,
                end_date=end_date,
                end_date_type="",
                ephemeral_storage=False,
                instance_match_criteria=instance_match,
                instance_platform=instance_platform,
                instance_type=instance_type,
                outpost_arn=spec.get("OutpostArn") or "",
                placement_group_arn=spec.get("PlacementGroupArn") or "",
                reservation_type="fleet",
                start_date=now,
                state="active",
                tag_set=list(tag_set),
                tenancy=tenancy,
                total_instance_count=count,
                client_token=params.get("ClientToken") or "",
                last_modified_date=now,
            )
            self.resources[capacity_reservation_id] = resource

            parent = self.state.fast_snapshot_restores.get(availability_zone_id)
            if parent and hasattr(parent, "capacity_reservation_ids"):
                parent.capacity_reservation_ids.append(capacity_reservation_id)

            total_fulfilled += count
            fleet_capacity_set.append({
                "availabilityZone": availability_zone,
                "availabilityZoneId": availability_zone_id,
                "capacityReservationId": capacity_reservation_id,
                "createDate": now,
                "ebsOptimized": ebs_optimized,
                "fulfilledCapacity": count,
                "instancePlatform": instance_platform,
                "instanceType": instance_type,
                "priority": priority,
                "totalInstanceCount": count,
                "weight": weight,
            })

        fleet_store = self._ensure_store("capacity_reservation_fleets")
        fleet_store[fleet_id] = {
            "allocationStrategy": allocation_strategy,
            "capacityReservationFleetId": fleet_id,
            "createTime": now,
            "endDate": end_date,
            "fleetCapacityReservationSet": fleet_capacity_set,
            "instanceMatchCriteria": instance_match,
            "state": "active",
            "tagSet": tag_set,
            "tenancy": tenancy,
            "totalFulfilledCapacity": total_fulfilled,
            "totalTargetCapacity": total_target,
        }

        return {
            'allocationStrategy': allocation_strategy,
            'capacityReservationFleetId': fleet_id,
            'createTime': now,
            'endDate': end_date,
            'fleetCapacityReservationSet': fleet_capacity_set,
            'instanceMatchCriteria': instance_match,
            'state': "active",
            'tagSet': tag_set,
            'tenancy': tenancy,
            'totalFulfilledCapacity': total_fulfilled,
            'totalTargetCapacity': total_target,
            }

    def DescribeCapacityBlockExtensionHistory(self, params: Dict[str, Any]):
        """Describes the events for the specified Capacity Block extension during the specified
			time."""

        reservation_ids = params.get("CapacityReservationId.N", []) or []
        for reservation_id in reservation_ids:
            if reservation_id and reservation_id not in self.resources:
                return create_error_response("InvalidCapacityReservationId.NotFound", f"The ID '{reservation_id}' does not exist")

        extensions_store = self._ensure_store("capacity_block_extensions")
        extensions = list(extensions_store.values())
        if reservation_ids:
            extensions = [ext for ext in extensions if ext.get("capacityReservationId") in reservation_ids]

        extensions = apply_filters(extensions, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(extensions, max_results, params.get("NextToken"))

        return {
            'capacityBlockExtensionSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DescribeCapacityBlockExtensionOfferings(self, params: Dict[str, Any]):
        """Describes Capacity Block extension offerings available for purchase in the AWS
			Region that you're currently using."""

        error = self._require_params(params, ["CapacityBlockExtensionDurationHours", "CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        duration_hours = int(params.get("CapacityBlockExtensionDurationHours") or 0)
        if duration_hours <= 0:
            return create_error_response("InvalidParameterValue", "CapacityBlockExtensionDurationHours must be greater than 0")

        now = self._now()
        offering = {
            "availabilityZone": resource.availability_zone,
            "availabilityZoneId": resource.availability_zone_id,
            "capacityBlockExtensionDurationHours": duration_hours,
            "capacityBlockExtensionEndDate": resource.end_date or "",
            "capacityBlockExtensionOfferingId": self._generate_id("cbeo"),
            "capacityBlockExtensionStartDate": now,
            "currencyCode": "USD",
            "instanceCount": resource.total_instance_count,
            "instanceType": resource.instance_type,
            "startDate": now,
            "tenancy": resource.tenancy,
            "upfrontFee": 0,
        }

        offerings = [offering]
        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(offerings, max_results, params.get("NextToken"))

        return {
            'capacityBlockExtensionOfferingSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DescribeCapacityBlockOfferings(self, params: Dict[str, Any]):
        """Describes Capacity Block offerings available for purchase in the AWS Region that you're currently using. With Capacity Blocks, you can 
			purchase a specific GPU instance type or EC2 UltraServer for a period of time. To search for an available Capacity Block offering, you specify a reservation dura"""

        error = self._require_params(params, ["CapacityDurationHours"])
        if error:
            return error

        duration_hours = int(params.get("CapacityDurationHours") or 0)
        if duration_hours <= 0:
            return create_error_response("InvalidParameterValue", "CapacityDurationHours must be greater than 0")

        now = self._now()
        start_date = params.get("StartDateRange") or now
        end_date = params.get("EndDateRange") or ""
        instance_type = params.get("InstanceType") or ""
        instance_count = int(params.get("InstanceCount") or 1)
        ultraserver_count = int(params.get("UltraserverCount") or 0)
        ultraserver_type = params.get("UltraserverType") or ""

        offering = {
            "availabilityZone": "",
            "capacityBlockDurationHours": duration_hours,
            "capacityBlockDurationMinutes": duration_hours * 60,
            "capacityBlockOfferingId": self._generate_id("cbo"),
            "currencyCode": "USD",
            "endDate": end_date,
            "instanceCount": instance_count,
            "instanceType": instance_type,
            "startDate": start_date,
            "tenancy": "default",
            "ultraserverCount": ultraserver_count,
            "ultraserverType": ultraserver_type,
            "upfrontFee": 0,
        }

        offerings = [offering]
        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(offerings, max_results, params.get("NextToken"))

        return {
            'capacityBlockOfferingSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DescribeCapacityBlocks(self, params: Dict[str, Any]):
        """Describes details about Capacity Blocks in the AWS Region that you're currently using."""

        block_ids = params.get("CapacityBlockId.N", []) or []
        capacity_blocks_store = self._ensure_store("capacity_blocks")

        for block_id in block_ids:
            if block_id and block_id not in capacity_blocks_store:
                return create_error_response("InvalidCapacityBlockId.NotFound", f"The ID '{block_id}' does not exist")

        blocks = list(capacity_blocks_store.values())
        if block_ids:
            blocks = [block for block in blocks if block.get("capacityBlockId") in block_ids]

        blocks = apply_filters(blocks, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(blocks, max_results, params.get("NextToken"))

        return {
            'capacityBlockSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DescribeCapacityBlockStatus(self, params: Dict[str, Any]):
        """Describes the availability of capacity for the specified Capacity blocks, or all of your Capacity Blocks."""

        block_ids = params.get("CapacityBlockId.N", []) or []
        capacity_blocks_store = self._ensure_store("capacity_blocks")

        for block_id in block_ids:
            if block_id and block_id not in capacity_blocks_store:
                return create_error_response("InvalidCapacityBlockId.NotFound", f"The ID '{block_id}' does not exist")

        blocks = list(capacity_blocks_store.values())
        if block_ids:
            blocks = [block for block in blocks if block.get("capacityBlockId") in block_ids]

        blocks = apply_filters(blocks, params.get("Filter.N", []))

        status_set: List[Dict[str, Any]] = []
        for block in blocks:
            reservation_ids = block.get("capacityReservationIdSet") or []
            total_capacity = len(reservation_ids)
            available = total_capacity
            status_set.append({
                "capacityBlockId": block.get("capacityBlockId"),
                "capacityReservationStatusSet": [
                    {"capacityReservationId": rid, "status": "active"} for rid in reservation_ids
                ],
                "interconnectStatus": "available",
                "totalAvailableCapacity": available,
                "totalCapacity": total_capacity,
                "totalUnavailableCapacity": total_capacity - available,
            })

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(status_set, max_results, params.get("NextToken"))

        return {
            'capacityBlockStatusSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DescribeCapacityReservationBillingRequests(self, params: Dict[str, Any]):
        """Describes a request to assign the billing of the unused capacity of a Capacity
			Reservation. For more information, seeBilling assignment for shared
					Amazon EC2 Capacity Reservations."""

        error = self._require_params(params, ["Role"])
        if error:
            return error

        reservation_ids = params.get("CapacityReservationId.N", []) or []
        for reservation_id in reservation_ids:
            if reservation_id and reservation_id not in self.resources:
                return create_error_response("InvalidCapacityReservationId.NotFound", f"The ID '{reservation_id}' does not exist")

        requests: List[Dict[str, Any]] = []
        for reservation in self.resources.values():
            if reservation_ids and reservation.capacity_reservation_id not in reservation_ids:
                continue
            for request in reservation.billing_requests:
                requests.append(request)

        requests = apply_filters(requests, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(requests, max_results, params.get("NextToken"))

        return {
            'capacityReservationBillingRequestSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DescribeCapacityReservations(self, params: Dict[str, Any]):
        """Describes one or more of your Capacity Reservations. The results describe only the
			Capacity Reservations in the AWS Region that you're currently
			using."""

        reservation_ids = params.get("CapacityReservationId.N", []) or []
        for reservation_id in reservation_ids:
            if reservation_id and reservation_id not in self.resources:
                return create_error_response("InvalidCapacityReservationId.NotFound", f"The ID '{reservation_id}' does not exist")

        reservations = list(self.resources.values())
        if reservation_ids:
            reservations = [res for res in reservations if res.capacity_reservation_id in reservation_ids]

        reservations = apply_filters(reservations, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(reservations, max_results, params.get("NextToken"))

        return {
            'capacityReservationSet': [res.to_dict() for res in paginated["items"]],
            'nextToken': paginated["next_token"],
            }

    def DescribeCapacityReservationFleets(self, params: Dict[str, Any]):
        """Describes one or more Capacity Reservation Fleets."""

        fleet_ids = params.get("CapacityReservationFleetId.N", []) or []
        fleet_store = self._ensure_store("capacity_reservation_fleets")

        for fleet_id in fleet_ids:
            if fleet_id and fleet_id not in fleet_store:
                return create_error_response("InvalidCapacityReservationFleetId.NotFound", f"The ID '{fleet_id}' does not exist")

        fleets = list(fleet_store.values())
        if fleet_ids:
            fleets = [fleet for fleet in fleets if fleet.get("capacityReservationFleetId") in fleet_ids]

        fleets = apply_filters(fleets, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(fleets, max_results, params.get("NextToken"))

        return {
            'capacityReservationFleetSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DescribeMacModificationTasks(self, params: Dict[str, Any]):
        """Describes a System Integrity Protection (SIP) modification task or volume ownership delegation 
         task for an Amazon EC2 Mac instance. For more information, seeConfigure 
            SIP for Amazon EC2 instancesin theAmazon EC2 User Guide."""

        task_ids = params.get("MacModificationTaskId.N", []) or []
        mac_tasks_store = self._ensure_store("mac_modification_tasks")

        for task_id in task_ids:
            if task_id and task_id not in mac_tasks_store:
                return create_error_response("InvalidMacModificationTaskId.NotFound", f"The ID '{task_id}' does not exist")

        tasks = list(mac_tasks_store.values())
        if task_ids:
            tasks = [task for task in tasks if task.get("macModificationTaskId") in task_ids]

        tasks = apply_filters(tasks, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(tasks, max_results, params.get("NextToken"))

        return {
            'macModificationTaskSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def DisassociateCapacityReservationBillingOwner(self, params: Dict[str, Any]):
        """Cancels a pending request to assign billing of the unused capacity of a Capacity
			Reservation to a consumer account, or revokes a request that has already been accepted.
			For more information, seeBilling assignment for shared
					Amazon EC2 Capacity Reservations."""

        error = self._require_params(params, ["CapacityReservationId", "UnusedReservationBillingOwnerId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        unused_owner_id = params.get("UnusedReservationBillingOwnerId") or ""
        resource.unused_reservation_billing_owner_id = ""

        updated_requests: List[Dict[str, Any]] = []
        for request in resource.billing_requests:
            if request.get("unusedReservationBillingOwnerId") == unused_owner_id:
                request["status"] = "revoked"
                request["statusMessage"] = "Request revoked"
                request["lastUpdateTime"] = self._now()
            updated_requests.append(request)
        resource.billing_requests = updated_requests

        return {
            'return': True,
            }

    def GetCapacityReservationUsage(self, params: Dict[str, Any]):
        """Gets usage information about a Capacity Reservation. If the Capacity Reservation is
			shared, it shows usage information for the Capacity Reservation owner and each AWS account that is currently using the shared capacity. If the Capacity
			Reservation is not shared, it shows only the Capacity Rese"""

        error = self._require_params(params, ["CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        used_count = max(resource.total_instance_count - resource.available_instance_count, 0)
        usage_set = [{"accountId": resource.owner_id or "", "usedInstanceCount": used_count}]

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(usage_set, max_results, params.get("NextToken"))

        return {
            'availableInstanceCount': resource.available_instance_count,
            'capacityReservationId': resource.capacity_reservation_id,
            'instanceType': resource.instance_type,
            'instanceUsageSet': paginated["items"],
            'interruptible': resource.interruptible,
            'interruptibleCapacityAllocation': resource.interruptible_capacity_allocation,
            'interruptionInfo': resource.interruption_info,
            'nextToken': paginated["next_token"],
            'state': resource.state,
            'totalInstanceCount': resource.total_instance_count,
            }

    def GetGroupsForCapacityReservation(self, params: Dict[str, Any]):
        """Lists the resource groups to which a Capacity Reservation has been added."""

        error = self._require_params(params, ["CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        groups = [{"groupArn": arn, "ownerId": resource.owner_id or ""} for arn in resource.group_arns]

        max_results = int(params.get("MaxResults") or 100)
        paginated = self._paginate(groups, max_results, params.get("NextToken"))

        return {
            'capacityReservationGroupSet': paginated["items"],
            'nextToken': paginated["next_token"],
            }

    def ModifyCapacityReservation(self, params: Dict[str, Any]):
        """Modifies a Capacity Reservation's capacity, instance eligibility, and the conditions
			under which it is to be released. You can't modify a Capacity Reservation's instance
			type, EBS optimization, platform, instance store settings, Availability Zone, or
			tenancy. If you need to modify any of th"""

        error = self._require_params(params, ["CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        if params.get("InstanceCount") is not None:
            instance_count = int(params.get("InstanceCount") or 0)
            if instance_count <= 0:
                return create_error_response("InvalidParameterValue", "InstanceCount must be greater than 0")
            used_instances = resource.total_instance_count - resource.available_instance_count
            if instance_count < used_instances:
                return create_error_response("InvalidParameterValue", "InstanceCount cannot be less than used instance count")
            resource.total_instance_count = instance_count
            resource.available_instance_count = instance_count - used_instances
            if resource.commitment_info is not None:
                resource.commitment_info["committedInstanceCount"] = instance_count

        if params.get("InstanceMatchCriteria") is not None:
            resource.instance_match_criteria = params.get("InstanceMatchCriteria") or resource.instance_match_criteria

        if params.get("EndDate") is not None:
            resource.end_date = params.get("EndDate") or ""
            if resource.commitment_info is not None:
                resource.commitment_info["commitmentEndDate"] = resource.end_date

        if params.get("EndDateType") is not None:
            resource.end_date_type = params.get("EndDateType") or ""

        resource.last_modified_date = self._now()

        return {
            'return': True,
            }

    def ModifyCapacityReservationFleet(self, params: Dict[str, Any]):
        """Modifies a Capacity Reservation Fleet. When you modify the total target capacity of a Capacity Reservation Fleet, the Fleet
			automatically creates new Capacity Reservations, or modifies or cancels existing
			Capacity Reservations in the Fleet to meet the new total target capacity. When you
			mod"""

        error = self._require_params(params, ["CapacityReservationFleetId"])
        if error:
            return error

        fleet_id = params.get("CapacityReservationFleetId") or ""
        fleet_store = self._ensure_store("capacity_reservation_fleets")
        fleet = fleet_store.get(fleet_id)
        if not fleet:
            return create_error_response("InvalidCapacityReservationFleetId.NotFound", f"The ID '{fleet_id}' does not exist")

        if params.get("TotalTargetCapacity") is not None:
            total_target = int(params.get("TotalTargetCapacity") or 0)
            if total_target <= 0:
                return create_error_response("InvalidParameterValue", "TotalTargetCapacity must be greater than 0")
            fleet["totalTargetCapacity"] = total_target
            fulfilled = fleet.get("totalFulfilledCapacity") or 0
            fleet["totalFulfilledCapacity"] = min(fulfilled, total_target)

        if str2bool(params.get("RemoveEndDate")):
            fleet["endDate"] = ""
        elif params.get("EndDate") is not None:
            fleet["endDate"] = params.get("EndDate") or ""

        return {
            'return': True,
            }

    def ModifyInstanceCapacityReservationAttributes(self, params: Dict[str, Any]):
        """Modifies the Capacity Reservation settings for a stopped instance. Use this action to
			configure an instance to target a specific Capacity Reservation, run in anyopenCapacity Reservation with matching attributes, run in On-Demand
			Instance capacity, or only run in a Capacity Reservation."""

        error = self._require_params(params, ["CapacityReservationSpecification", "InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId") or ""
        instance = self.state.instances.get(instance_id)
        if not instance:
            return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        instance_state = getattr(instance, "instance_state", {}) or {}
        if instance_state.get("name") != "stopped":
            return create_error_response("InvalidInstanceState", "Instance must be stopped to modify capacity reservation attributes")

        spec = params.get("CapacityReservationSpecification") or {}
        setattr(instance, "capacity_reservation_specification", spec)

        return {
            'return': True,
            }

    def MoveCapacityReservationInstances(self, params: Dict[str, Any]):
        """Move available capacity from a source Capacity Reservation to a destination Capacity
			Reservation. The source Capacity Reservation and the destination Capacity Reservation
			must beactive, owned by your AWS account, and share the following: Instance type Platform"""

        error = self._require_params(params, ["DestinationCapacityReservationId", "InstanceCount", "SourceCapacityReservationId"])
        if error:
            return error

        source_id = params.get("SourceCapacityReservationId") or ""
        destination_id = params.get("DestinationCapacityReservationId") or ""
        source = self._get_capacity_reservation_or_error(source_id)
        if is_error_response(source):
            return source
        destination = self._get_capacity_reservation_or_error(destination_id)
        if is_error_response(destination):
            return destination

        instance_count = int(params.get("InstanceCount") or 0)
        if instance_count <= 0:
            return create_error_response("InvalidParameterValue", "InstanceCount must be greater than 0")

        if source.state != "active" or destination.state != "active":
            return create_error_response("InvalidStateTransition", "Capacity Reservations must be active")
        if source.instance_type != destination.instance_type or source.instance_platform != destination.instance_platform:
            return create_error_response("InvalidParameterValue", "Source and destination must have matching instance type and platform")
        if instance_count > source.available_instance_count:
            return create_error_response("InvalidParameterValue", "InstanceCount exceeds available capacity")

        source.available_instance_count -= instance_count
        destination.available_instance_count += instance_count
        source.total_instance_count -= instance_count
        destination.total_instance_count += instance_count
        if source.commitment_info is not None:
            source.commitment_info["committedInstanceCount"] = source.total_instance_count
        if destination.commitment_info is not None:
            destination.commitment_info["committedInstanceCount"] = destination.total_instance_count
        now = self._now()
        source.last_modified_date = now
        destination.last_modified_date = now

        return {
            'destinationCapacityReservation': destination.to_dict(),
            'instanceCount': instance_count,
            'sourceCapacityReservation': source.to_dict(),
            }

    def PurchaseCapacityBlock(self, params: Dict[str, Any]):
        """Purchase the Capacity Block for use with your account. With Capacity Blocks you ensure
			GPU capacity is available for machine learning (ML) workloads. You must specify the ID
			of the Capacity Block offering you are purchasing."""

        error = self._require_params(params, ["CapacityBlockOfferingId", "InstancePlatform"])
        if error:
            return error

        offering_id = params.get("CapacityBlockOfferingId") or ""
        instance_platform = params.get("InstancePlatform") or ""

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tags = spec.get("Tags") or spec.get("Tag") or spec.get("TagSet") or []
            for tag in tags:
                if isinstance(tag, dict):
                    tag_set.append({"Key": tag.get("Key"), "Value": tag.get("Value")})

        now = self._now()
        capacity_block_id = self._generate_id("cb")
        capacity_reservation_id = self._generate_id("cr")

        resource = CapacityReservation(
            availability_zone="",
            availability_zone_id="",
            available_instance_count=1,
            capacity_block_id=capacity_block_id,
            capacity_reservation_arn=f"arn:aws:ec2:::capacity-reservation/{capacity_reservation_id}",
            capacity_reservation_id=capacity_reservation_id,
            commitment_info={
                "commitmentEndDate": "",
                "committedInstanceCount": 1,
            },
            create_date=now,
            delivery_preference="",
            ebs_optimized=False,
            end_date="",
            end_date_type="",
            ephemeral_storage=False,
            instance_match_criteria="open",
            instance_platform=instance_platform,
            instance_type="",
            outpost_arn="",
            placement_group_arn="",
            reservation_type="capacity-block",
            start_date=now,
            state="active",
            tag_set=tag_set,
            tenancy="default",
            total_instance_count=1,
            client_token="",
            last_modified_date=now,
        )
        self.resources[capacity_reservation_id] = resource

        capacity_blocks_store = self._ensure_store("capacity_blocks")
        block = {
            "availabilityZone": "",
            "availabilityZoneId": "",
            "capacityBlockId": capacity_block_id,
            "capacityReservationIdSet": [capacity_reservation_id],
            "createDate": now,
            "endDate": "",
            "startDate": now,
            "state": "active",
            "tagSet": tag_set,
            "ultraserverType": offering_id,
        }
        capacity_blocks_store[capacity_block_id] = block

        return {
            'capacityBlockSet': [block],
            'capacityReservation': resource.to_dict(),
            }

    def PurchaseCapacityBlockExtension(self, params: Dict[str, Any]):
        """Purchase the Capacity Block extension for use with your account. You must specify the
			ID of the Capacity Block extension offering you are purchasing."""

        error = self._require_params(params, ["CapacityBlockExtensionOfferingId", "CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        offering_id = params.get("CapacityBlockExtensionOfferingId") or ""
        now = self._now()

        extension = {
            "availabilityZone": resource.availability_zone,
            "availabilityZoneId": resource.availability_zone_id,
            "capacityBlockExtensionDurationHours": 0,
            "capacityBlockExtensionEndDate": resource.end_date or "",
            "capacityBlockExtensionOfferingId": offering_id,
            "capacityBlockExtensionPurchaseDate": now,
            "capacityBlockExtensionStartDate": now,
            "capacityBlockExtensionStatus": "active",
            "capacityReservationId": capacity_reservation_id,
            "currencyCode": "USD",
            "instanceCount": resource.total_instance_count,
            "instanceType": resource.instance_type,
            "upfrontFee": 0,
        }

        extensions_store = self._ensure_store("capacity_block_extensions")
        extension_id = self._generate_id("cbe")
        extensions_store[extension_id] = extension

        return {
            'capacityBlockExtensionSet': [extension],
            }

    def RejectCapacityReservationBillingOwnership(self, params: Dict[str, Any]):
        """Rejects a request to assign billing of the available capacity of a shared Capacity
			Reservation to your account. For more information, seeBilling assignment for shared
					Amazon EC2 Capacity Reservations."""

        error = self._require_params(params, ["CapacityReservationId"])
        if error:
            return error

        capacity_reservation_id = params.get("CapacityReservationId") or ""
        resource = self._get_capacity_reservation_or_error(capacity_reservation_id)
        if is_error_response(resource):
            return resource

        updated_requests: List[Dict[str, Any]] = []
        for request in resource.billing_requests:
            if request.get("capacityReservationId") == capacity_reservation_id:
                request["status"] = "rejected"
                request["statusMessage"] = "Request rejected"
                request["lastUpdateTime"] = self._now()
            updated_requests.append(request)
        resource.billing_requests = updated_requests

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'cr') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class capacityreservation_RequestParser:
    @staticmethod
    def parse_accept_capacity_reservation_billing_ownership_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_associate_capacity_reservation_billing_owner_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "UnusedReservationBillingOwnerId": get_scalar(md, "UnusedReservationBillingOwnerId"),
        }

    @staticmethod
    def parse_cancel_capacity_reservation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_cancel_capacity_reservation_fleets_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationFleetId.N": get_indexed_list(md, "CapacityReservationFleetId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_create_capacity_reservation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "CommitmentDuration": get_int(md, "CommitmentDuration"),
            "DeliveryPreference": get_scalar(md, "DeliveryPreference"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EbsOptimized": get_scalar(md, "EbsOptimized"),
            "EndDate": get_scalar(md, "EndDate"),
            "EndDateType": get_scalar(md, "EndDateType"),
            "EphemeralStorage": get_scalar(md, "EphemeralStorage"),
            "InstanceCount": get_int(md, "InstanceCount"),
            "InstanceMatchCriteria": get_scalar(md, "InstanceMatchCriteria"),
            "InstancePlatform": get_scalar(md, "InstancePlatform"),
            "InstanceType": get_scalar(md, "InstanceType"),
            "OutpostArn": get_scalar(md, "OutpostArn"),
            "PlacementGroupArn": get_scalar(md, "PlacementGroupArn"),
            "StartDate": get_scalar(md, "StartDate"),
            "TagSpecifications.N": parse_tags(md, "TagSpecifications"),
            "Tenancy": get_scalar(md, "Tenancy"),
        }

    @staticmethod
    def parse_create_capacity_reservation_by_splitting_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceCount": get_int(md, "InstanceCount"),
            "SourceCapacityReservationId": get_scalar(md, "SourceCapacityReservationId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_capacity_reservation_fleet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationStrategy": get_scalar(md, "AllocationStrategy"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndDate": get_scalar(md, "EndDate"),
            "InstanceMatchCriteria": get_scalar(md, "InstanceMatchCriteria"),
            "InstanceTypeSpecification.N": get_indexed_list(md, "InstanceTypeSpecification"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Tenancy": get_scalar(md, "Tenancy"),
            "TotalTargetCapacity": get_int(md, "TotalTargetCapacity"),
        }

    @staticmethod
    def parse_describe_capacity_block_extension_history_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId.N": get_indexed_list(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_capacity_block_extension_offerings_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityBlockExtensionDurationHours": get_int(md, "CapacityBlockExtensionDurationHours"),
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_capacity_block_offerings_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityDurationHours": get_int(md, "CapacityDurationHours"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndDateRange": get_scalar(md, "EndDateRange"),
            "InstanceCount": get_int(md, "InstanceCount"),
            "InstanceType": get_scalar(md, "InstanceType"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "StartDateRange": get_scalar(md, "StartDateRange"),
            "UltraserverCount": get_int(md, "UltraserverCount"),
            "UltraserverType": get_scalar(md, "UltraserverType"),
        }

    @staticmethod
    def parse_describe_capacity_blocks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityBlockId.N": get_indexed_list(md, "CapacityBlockId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_capacity_block_status_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityBlockId.N": get_indexed_list(md, "CapacityBlockId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_capacity_reservation_billing_requests_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId.N": get_indexed_list(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "Role": get_scalar(md, "Role"),
        }

    @staticmethod
    def parse_describe_capacity_reservations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId.N": get_indexed_list(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_capacity_reservation_fleets_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationFleetId.N": get_indexed_list(md, "CapacityReservationFleetId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_mac_modification_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MacModificationTaskId.N": get_indexed_list(md, "MacModificationTaskId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disassociate_capacity_reservation_billing_owner_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "UnusedReservationBillingOwnerId": get_scalar(md, "UnusedReservationBillingOwnerId"),
        }

    @staticmethod
    def parse_get_capacity_reservation_usage_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_groups_for_capacity_reservation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_modify_capacity_reservation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Accept": get_scalar(md, "Accept"),
            "AdditionalInfo": get_scalar(md, "AdditionalInfo"),
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndDate": get_scalar(md, "EndDate"),
            "EndDateType": get_scalar(md, "EndDateType"),
            "InstanceCount": get_int(md, "InstanceCount"),
            "InstanceMatchCriteria": get_scalar(md, "InstanceMatchCriteria"),
        }

    @staticmethod
    def parse_modify_capacity_reservation_fleet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationFleetId": get_scalar(md, "CapacityReservationFleetId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndDate": get_scalar(md, "EndDate"),
            "RemoveEndDate": get_scalar(md, "RemoveEndDate"),
            "TotalTargetCapacity": get_int(md, "TotalTargetCapacity"),
        }

    @staticmethod
    def parse_modify_instance_capacity_reservation_attributes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationSpecification": get_scalar(md, "CapacityReservationSpecification"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
        }

    @staticmethod
    def parse_move_capacity_reservation_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DestinationCapacityReservationId": get_scalar(md, "DestinationCapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceCount": get_int(md, "InstanceCount"),
            "SourceCapacityReservationId": get_scalar(md, "SourceCapacityReservationId"),
        }

    @staticmethod
    def parse_purchase_capacity_block_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityBlockOfferingId": get_scalar(md, "CapacityBlockOfferingId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstancePlatform": get_scalar(md, "InstancePlatform"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_purchase_capacity_block_extension_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityBlockExtensionOfferingId": get_scalar(md, "CapacityBlockExtensionOfferingId"),
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_reject_capacity_reservation_billing_ownership_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId": get_scalar(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AcceptCapacityReservationBillingOwnership": capacityreservation_RequestParser.parse_accept_capacity_reservation_billing_ownership_request,
            "AssociateCapacityReservationBillingOwner": capacityreservation_RequestParser.parse_associate_capacity_reservation_billing_owner_request,
            "CancelCapacityReservation": capacityreservation_RequestParser.parse_cancel_capacity_reservation_request,
            "CancelCapacityReservationFleets": capacityreservation_RequestParser.parse_cancel_capacity_reservation_fleets_request,
            "CreateCapacityReservation": capacityreservation_RequestParser.parse_create_capacity_reservation_request,
            "CreateCapacityReservationBySplitting": capacityreservation_RequestParser.parse_create_capacity_reservation_by_splitting_request,
            "CreateCapacityReservationFleet": capacityreservation_RequestParser.parse_create_capacity_reservation_fleet_request,
            "DescribeCapacityBlockExtensionHistory": capacityreservation_RequestParser.parse_describe_capacity_block_extension_history_request,
            "DescribeCapacityBlockExtensionOfferings": capacityreservation_RequestParser.parse_describe_capacity_block_extension_offerings_request,
            "DescribeCapacityBlockOfferings": capacityreservation_RequestParser.parse_describe_capacity_block_offerings_request,
            "DescribeCapacityBlocks": capacityreservation_RequestParser.parse_describe_capacity_blocks_request,
            "DescribeCapacityBlockStatus": capacityreservation_RequestParser.parse_describe_capacity_block_status_request,
            "DescribeCapacityReservationBillingRequests": capacityreservation_RequestParser.parse_describe_capacity_reservation_billing_requests_request,
            "DescribeCapacityReservations": capacityreservation_RequestParser.parse_describe_capacity_reservations_request,
            "DescribeCapacityReservationFleets": capacityreservation_RequestParser.parse_describe_capacity_reservation_fleets_request,
            "DescribeMacModificationTasks": capacityreservation_RequestParser.parse_describe_mac_modification_tasks_request,
            "DisassociateCapacityReservationBillingOwner": capacityreservation_RequestParser.parse_disassociate_capacity_reservation_billing_owner_request,
            "GetCapacityReservationUsage": capacityreservation_RequestParser.parse_get_capacity_reservation_usage_request,
            "GetGroupsForCapacityReservation": capacityreservation_RequestParser.parse_get_groups_for_capacity_reservation_request,
            "ModifyCapacityReservation": capacityreservation_RequestParser.parse_modify_capacity_reservation_request,
            "ModifyCapacityReservationFleet": capacityreservation_RequestParser.parse_modify_capacity_reservation_fleet_request,
            "ModifyInstanceCapacityReservationAttributes": capacityreservation_RequestParser.parse_modify_instance_capacity_reservation_attributes_request,
            "MoveCapacityReservationInstances": capacityreservation_RequestParser.parse_move_capacity_reservation_instances_request,
            "PurchaseCapacityBlock": capacityreservation_RequestParser.parse_purchase_capacity_block_request,
            "PurchaseCapacityBlockExtension": capacityreservation_RequestParser.parse_purchase_capacity_block_extension_request,
            "RejectCapacityReservationBillingOwnership": capacityreservation_RequestParser.parse_reject_capacity_reservation_billing_ownership_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class capacityreservation_ResponseSerializer:
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
                xml_parts.extend(capacityreservation_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(capacityreservation_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(capacityreservation_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(capacityreservation_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_accept_capacity_reservation_billing_ownership_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AcceptCapacityReservationBillingOwnershipResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</AcceptCapacityReservationBillingOwnershipResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_associate_capacity_reservation_billing_owner_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateCapacityReservationBillingOwnerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</AssociateCapacityReservationBillingOwnerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_cancel_capacity_reservation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelCapacityReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CancelCapacityReservationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_cancel_capacity_reservation_fleets_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelCapacityReservationFleetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize failedFleetCancellationSet
        _failedFleetCancellationSet_key = None
        if "failedFleetCancellationSet" in data:
            _failedFleetCancellationSet_key = "failedFleetCancellationSet"
        elif "FailedFleetCancellationSet" in data:
            _failedFleetCancellationSet_key = "FailedFleetCancellationSet"
        elif "FailedFleetCancellations" in data:
            _failedFleetCancellationSet_key = "FailedFleetCancellations"
        if _failedFleetCancellationSet_key:
            param_data = data[_failedFleetCancellationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<failedFleetCancellationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</failedFleetCancellationSet>')
            else:
                xml_parts.append(f'{indent_str}<failedFleetCancellationSet/>')
        # Serialize successfulFleetCancellationSet
        _successfulFleetCancellationSet_key = None
        if "successfulFleetCancellationSet" in data:
            _successfulFleetCancellationSet_key = "successfulFleetCancellationSet"
        elif "SuccessfulFleetCancellationSet" in data:
            _successfulFleetCancellationSet_key = "SuccessfulFleetCancellationSet"
        elif "SuccessfulFleetCancellations" in data:
            _successfulFleetCancellationSet_key = "SuccessfulFleetCancellations"
        if _successfulFleetCancellationSet_key:
            param_data = data[_successfulFleetCancellationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulFleetCancellationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</successfulFleetCancellationSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulFleetCancellationSet/>')
        xml_parts.append(f'</CancelCapacityReservationFleetsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_capacity_reservation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateCapacityReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityReservation
        _capacityReservation_key = None
        if "capacityReservation" in data:
            _capacityReservation_key = "capacityReservation"
        elif "CapacityReservation" in data:
            _capacityReservation_key = "CapacityReservation"
        if _capacityReservation_key:
            param_data = data[_capacityReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<capacityReservation>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</capacityReservation>')
        xml_parts.append(f'</CreateCapacityReservationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_capacity_reservation_by_splitting_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateCapacityReservationBySplittingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize destinationCapacityReservation
        _destinationCapacityReservation_key = None
        if "destinationCapacityReservation" in data:
            _destinationCapacityReservation_key = "destinationCapacityReservation"
        elif "DestinationCapacityReservation" in data:
            _destinationCapacityReservation_key = "DestinationCapacityReservation"
        if _destinationCapacityReservation_key:
            param_data = data[_destinationCapacityReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<destinationCapacityReservation>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</destinationCapacityReservation>')
        # Serialize instanceCount
        _instanceCount_key = None
        if "instanceCount" in data:
            _instanceCount_key = "instanceCount"
        elif "InstanceCount" in data:
            _instanceCount_key = "InstanceCount"
        if _instanceCount_key:
            param_data = data[_instanceCount_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceCount>{esc(str(param_data))}</instanceCount>')
        # Serialize sourceCapacityReservation
        _sourceCapacityReservation_key = None
        if "sourceCapacityReservation" in data:
            _sourceCapacityReservation_key = "sourceCapacityReservation"
        elif "SourceCapacityReservation" in data:
            _sourceCapacityReservation_key = "SourceCapacityReservation"
        if _sourceCapacityReservation_key:
            param_data = data[_sourceCapacityReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sourceCapacityReservation>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</sourceCapacityReservation>')
        xml_parts.append(f'</CreateCapacityReservationBySplittingResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_capacity_reservation_fleet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateCapacityReservationFleetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize allocationStrategy
        _allocationStrategy_key = None
        if "allocationStrategy" in data:
            _allocationStrategy_key = "allocationStrategy"
        elif "AllocationStrategy" in data:
            _allocationStrategy_key = "AllocationStrategy"
        if _allocationStrategy_key:
            param_data = data[_allocationStrategy_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<allocationStrategy>{esc(str(param_data))}</allocationStrategy>')
        # Serialize capacityReservationFleetId
        _capacityReservationFleetId_key = None
        if "capacityReservationFleetId" in data:
            _capacityReservationFleetId_key = "capacityReservationFleetId"
        elif "CapacityReservationFleetId" in data:
            _capacityReservationFleetId_key = "CapacityReservationFleetId"
        if _capacityReservationFleetId_key:
            param_data = data[_capacityReservationFleetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<capacityReservationFleetId>{esc(str(param_data))}</capacityReservationFleetId>')
        # Serialize createTime
        _createTime_key = None
        if "createTime" in data:
            _createTime_key = "createTime"
        elif "CreateTime" in data:
            _createTime_key = "CreateTime"
        if _createTime_key:
            param_data = data[_createTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<createTime>{esc(str(param_data))}</createTime>')
        # Serialize endDate
        _endDate_key = None
        if "endDate" in data:
            _endDate_key = "endDate"
        elif "EndDate" in data:
            _endDate_key = "EndDate"
        if _endDate_key:
            param_data = data[_endDate_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<endDate>{esc(str(param_data))}</endDate>')
        # Serialize fleetCapacityReservationSet
        _fleetCapacityReservationSet_key = None
        if "fleetCapacityReservationSet" in data:
            _fleetCapacityReservationSet_key = "fleetCapacityReservationSet"
        elif "FleetCapacityReservationSet" in data:
            _fleetCapacityReservationSet_key = "FleetCapacityReservationSet"
        elif "FleetCapacityReservations" in data:
            _fleetCapacityReservationSet_key = "FleetCapacityReservations"
        if _fleetCapacityReservationSet_key:
            param_data = data[_fleetCapacityReservationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<fleetCapacityReservationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</fleetCapacityReservationSet>')
            else:
                xml_parts.append(f'{indent_str}<fleetCapacityReservationSet/>')
        # Serialize instanceMatchCriteria
        _instanceMatchCriteria_key = None
        if "instanceMatchCriteria" in data:
            _instanceMatchCriteria_key = "instanceMatchCriteria"
        elif "InstanceMatchCriteria" in data:
            _instanceMatchCriteria_key = "InstanceMatchCriteria"
        if _instanceMatchCriteria_key:
            param_data = data[_instanceMatchCriteria_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceMatchCriteria>{esc(str(param_data))}</instanceMatchCriteria>')
        # Serialize state
        _state_key = None
        if "state" in data:
            _state_key = "state"
        elif "State" in data:
            _state_key = "State"
        if _state_key:
            param_data = data[_state_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<state>{esc(str(param_data))}</state>')
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
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        # Serialize tenancy
        _tenancy_key = None
        if "tenancy" in data:
            _tenancy_key = "tenancy"
        elif "Tenancy" in data:
            _tenancy_key = "Tenancy"
        if _tenancy_key:
            param_data = data[_tenancy_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<tenancy>{esc(str(param_data))}</tenancy>')
        # Serialize totalFulfilledCapacity
        _totalFulfilledCapacity_key = None
        if "totalFulfilledCapacity" in data:
            _totalFulfilledCapacity_key = "totalFulfilledCapacity"
        elif "TotalFulfilledCapacity" in data:
            _totalFulfilledCapacity_key = "TotalFulfilledCapacity"
        if _totalFulfilledCapacity_key:
            param_data = data[_totalFulfilledCapacity_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<totalFulfilledCapacity>{esc(str(param_data))}</totalFulfilledCapacity>')
        # Serialize totalTargetCapacity
        _totalTargetCapacity_key = None
        if "totalTargetCapacity" in data:
            _totalTargetCapacity_key = "totalTargetCapacity"
        elif "TotalTargetCapacity" in data:
            _totalTargetCapacity_key = "TotalTargetCapacity"
        if _totalTargetCapacity_key:
            param_data = data[_totalTargetCapacity_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<totalTargetCapacity>{esc(str(param_data))}</totalTargetCapacity>')
        xml_parts.append(f'</CreateCapacityReservationFleetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_block_extension_history_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityBlockExtensionHistoryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityBlockExtensionSet
        _capacityBlockExtensionSet_key = None
        if "capacityBlockExtensionSet" in data:
            _capacityBlockExtensionSet_key = "capacityBlockExtensionSet"
        elif "CapacityBlockExtensionSet" in data:
            _capacityBlockExtensionSet_key = "CapacityBlockExtensionSet"
        elif "CapacityBlockExtensions" in data:
            _capacityBlockExtensionSet_key = "CapacityBlockExtensions"
        if _capacityBlockExtensionSet_key:
            param_data = data[_capacityBlockExtensionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityBlockExtensionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityBlockExtensionSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityBlockExtensionSet/>')
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
        xml_parts.append(f'</DescribeCapacityBlockExtensionHistoryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_block_extension_offerings_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityBlockExtensionOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityBlockExtensionOfferingSet
        _capacityBlockExtensionOfferingSet_key = None
        if "capacityBlockExtensionOfferingSet" in data:
            _capacityBlockExtensionOfferingSet_key = "capacityBlockExtensionOfferingSet"
        elif "CapacityBlockExtensionOfferingSet" in data:
            _capacityBlockExtensionOfferingSet_key = "CapacityBlockExtensionOfferingSet"
        elif "CapacityBlockExtensionOfferings" in data:
            _capacityBlockExtensionOfferingSet_key = "CapacityBlockExtensionOfferings"
        if _capacityBlockExtensionOfferingSet_key:
            param_data = data[_capacityBlockExtensionOfferingSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityBlockExtensionOfferingSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityBlockExtensionOfferingSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityBlockExtensionOfferingSet/>')
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
        xml_parts.append(f'</DescribeCapacityBlockExtensionOfferingsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_block_offerings_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityBlockOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityBlockOfferingSet
        _capacityBlockOfferingSet_key = None
        if "capacityBlockOfferingSet" in data:
            _capacityBlockOfferingSet_key = "capacityBlockOfferingSet"
        elif "CapacityBlockOfferingSet" in data:
            _capacityBlockOfferingSet_key = "CapacityBlockOfferingSet"
        elif "CapacityBlockOfferings" in data:
            _capacityBlockOfferingSet_key = "CapacityBlockOfferings"
        if _capacityBlockOfferingSet_key:
            param_data = data[_capacityBlockOfferingSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityBlockOfferingSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityBlockOfferingSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityBlockOfferingSet/>')
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
        xml_parts.append(f'</DescribeCapacityBlockOfferingsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_blocks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityBlocksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityBlockSet
        _capacityBlockSet_key = None
        if "capacityBlockSet" in data:
            _capacityBlockSet_key = "capacityBlockSet"
        elif "CapacityBlockSet" in data:
            _capacityBlockSet_key = "CapacityBlockSet"
        elif "CapacityBlocks" in data:
            _capacityBlockSet_key = "CapacityBlocks"
        if _capacityBlockSet_key:
            param_data = data[_capacityBlockSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityBlockSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityBlockSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityBlockSet/>')
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
        xml_parts.append(f'</DescribeCapacityBlocksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_block_status_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityBlockStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityBlockStatusSet
        _capacityBlockStatusSet_key = None
        if "capacityBlockStatusSet" in data:
            _capacityBlockStatusSet_key = "capacityBlockStatusSet"
        elif "CapacityBlockStatusSet" in data:
            _capacityBlockStatusSet_key = "CapacityBlockStatusSet"
        elif "CapacityBlockStatuss" in data:
            _capacityBlockStatusSet_key = "CapacityBlockStatuss"
        if _capacityBlockStatusSet_key:
            param_data = data[_capacityBlockStatusSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityBlockStatusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityBlockStatusSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityBlockStatusSet/>')
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
        xml_parts.append(f'</DescribeCapacityBlockStatusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_reservation_billing_requests_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityReservationBillingRequestsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityReservationBillingRequestSet
        _capacityReservationBillingRequestSet_key = None
        if "capacityReservationBillingRequestSet" in data:
            _capacityReservationBillingRequestSet_key = "capacityReservationBillingRequestSet"
        elif "CapacityReservationBillingRequestSet" in data:
            _capacityReservationBillingRequestSet_key = "CapacityReservationBillingRequestSet"
        elif "CapacityReservationBillingRequests" in data:
            _capacityReservationBillingRequestSet_key = "CapacityReservationBillingRequests"
        if _capacityReservationBillingRequestSet_key:
            param_data = data[_capacityReservationBillingRequestSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityReservationBillingRequestSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityReservationBillingRequestSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityReservationBillingRequestSet/>')
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
        xml_parts.append(f'</DescribeCapacityReservationBillingRequestsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_reservations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityReservationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityReservationSet
        _capacityReservationSet_key = None
        if "capacityReservationSet" in data:
            _capacityReservationSet_key = "capacityReservationSet"
        elif "CapacityReservationSet" in data:
            _capacityReservationSet_key = "CapacityReservationSet"
        elif "CapacityReservations" in data:
            _capacityReservationSet_key = "CapacityReservations"
        if _capacityReservationSet_key:
            param_data = data[_capacityReservationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityReservationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityReservationSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityReservationSet/>')
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
        xml_parts.append(f'</DescribeCapacityReservationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_capacity_reservation_fleets_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityReservationFleetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityReservationFleetSet
        _capacityReservationFleetSet_key = None
        if "capacityReservationFleetSet" in data:
            _capacityReservationFleetSet_key = "capacityReservationFleetSet"
        elif "CapacityReservationFleetSet" in data:
            _capacityReservationFleetSet_key = "CapacityReservationFleetSet"
        elif "CapacityReservationFleets" in data:
            _capacityReservationFleetSet_key = "CapacityReservationFleets"
        if _capacityReservationFleetSet_key:
            param_data = data[_capacityReservationFleetSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityReservationFleetSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityReservationFleetSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityReservationFleetSet/>')
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
        xml_parts.append(f'</DescribeCapacityReservationFleetsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_mac_modification_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeMacModificationTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize macModificationTaskSet
        _macModificationTaskSet_key = None
        if "macModificationTaskSet" in data:
            _macModificationTaskSet_key = "macModificationTaskSet"
        elif "MacModificationTaskSet" in data:
            _macModificationTaskSet_key = "MacModificationTaskSet"
        elif "MacModificationTasks" in data:
            _macModificationTaskSet_key = "MacModificationTasks"
        if _macModificationTaskSet_key:
            param_data = data[_macModificationTaskSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<macModificationTaskSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</macModificationTaskSet>')
            else:
                xml_parts.append(f'{indent_str}<macModificationTaskSet/>')
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
        xml_parts.append(f'</DescribeMacModificationTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_capacity_reservation_billing_owner_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateCapacityReservationBillingOwnerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DisassociateCapacityReservationBillingOwnerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_capacity_reservation_usage_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetCapacityReservationUsageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize availableInstanceCount
        _availableInstanceCount_key = None
        if "availableInstanceCount" in data:
            _availableInstanceCount_key = "availableInstanceCount"
        elif "AvailableInstanceCount" in data:
            _availableInstanceCount_key = "AvailableInstanceCount"
        if _availableInstanceCount_key:
            param_data = data[_availableInstanceCount_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<availableInstanceCount>{esc(str(param_data))}</availableInstanceCount>')
        # Serialize capacityReservationId
        _capacityReservationId_key = None
        if "capacityReservationId" in data:
            _capacityReservationId_key = "capacityReservationId"
        elif "CapacityReservationId" in data:
            _capacityReservationId_key = "CapacityReservationId"
        if _capacityReservationId_key:
            param_data = data[_capacityReservationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<capacityReservationId>{esc(str(param_data))}</capacityReservationId>')
        # Serialize instanceType
        _instanceType_key = None
        if "instanceType" in data:
            _instanceType_key = "instanceType"
        elif "InstanceType" in data:
            _instanceType_key = "InstanceType"
        if _instanceType_key:
            param_data = data[_instanceType_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceType>{esc(str(param_data))}</instanceType>')
        # Serialize instanceUsageSet
        _instanceUsageSet_key = None
        if "instanceUsageSet" in data:
            _instanceUsageSet_key = "instanceUsageSet"
        elif "InstanceUsageSet" in data:
            _instanceUsageSet_key = "InstanceUsageSet"
        elif "InstanceUsages" in data:
            _instanceUsageSet_key = "InstanceUsages"
        if _instanceUsageSet_key:
            param_data = data[_instanceUsageSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceUsageSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceUsageSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceUsageSet/>')
        # Serialize interruptible
        _interruptible_key = None
        if "interruptible" in data:
            _interruptible_key = "interruptible"
        elif "Interruptible" in data:
            _interruptible_key = "Interruptible"
        if _interruptible_key:
            param_data = data[_interruptible_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<interruptible>{esc(str(param_data))}</interruptible>')
        # Serialize interruptibleCapacityAllocation
        _interruptibleCapacityAllocation_key = None
        if "interruptibleCapacityAllocation" in data:
            _interruptibleCapacityAllocation_key = "interruptibleCapacityAllocation"
        elif "InterruptibleCapacityAllocation" in data:
            _interruptibleCapacityAllocation_key = "InterruptibleCapacityAllocation"
        if _interruptibleCapacityAllocation_key:
            param_data = data[_interruptibleCapacityAllocation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<interruptibleCapacityAllocation>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</interruptibleCapacityAllocation>')
        # Serialize interruptionInfo
        _interruptionInfo_key = None
        if "interruptionInfo" in data:
            _interruptionInfo_key = "interruptionInfo"
        elif "InterruptionInfo" in data:
            _interruptionInfo_key = "InterruptionInfo"
        if _interruptionInfo_key:
            param_data = data[_interruptionInfo_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<interruptionInfo>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</interruptionInfo>')
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
        # Serialize state
        _state_key = None
        if "state" in data:
            _state_key = "state"
        elif "State" in data:
            _state_key = "State"
        if _state_key:
            param_data = data[_state_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<state>{esc(str(param_data))}</state>')
        # Serialize totalInstanceCount
        _totalInstanceCount_key = None
        if "totalInstanceCount" in data:
            _totalInstanceCount_key = "totalInstanceCount"
        elif "TotalInstanceCount" in data:
            _totalInstanceCount_key = "TotalInstanceCount"
        if _totalInstanceCount_key:
            param_data = data[_totalInstanceCount_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<totalInstanceCount>{esc(str(param_data))}</totalInstanceCount>')
        xml_parts.append(f'</GetCapacityReservationUsageResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_groups_for_capacity_reservation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetGroupsForCapacityReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityReservationGroupSet
        _capacityReservationGroupSet_key = None
        if "capacityReservationGroupSet" in data:
            _capacityReservationGroupSet_key = "capacityReservationGroupSet"
        elif "CapacityReservationGroupSet" in data:
            _capacityReservationGroupSet_key = "CapacityReservationGroupSet"
        elif "CapacityReservationGroups" in data:
            _capacityReservationGroupSet_key = "CapacityReservationGroups"
        if _capacityReservationGroupSet_key:
            param_data = data[_capacityReservationGroupSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityReservationGroupSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityReservationGroupSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityReservationGroupSet/>')
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
        xml_parts.append(f'</GetGroupsForCapacityReservationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_capacity_reservation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyCapacityReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyCapacityReservationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_capacity_reservation_fleet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyCapacityReservationFleetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyCapacityReservationFleetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_capacity_reservation_attributes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceCapacityReservationAttributesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyInstanceCapacityReservationAttributesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_move_capacity_reservation_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<MoveCapacityReservationInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize destinationCapacityReservation
        _destinationCapacityReservation_key = None
        if "destinationCapacityReservation" in data:
            _destinationCapacityReservation_key = "destinationCapacityReservation"
        elif "DestinationCapacityReservation" in data:
            _destinationCapacityReservation_key = "DestinationCapacityReservation"
        if _destinationCapacityReservation_key:
            param_data = data[_destinationCapacityReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<destinationCapacityReservation>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</destinationCapacityReservation>')
        # Serialize instanceCount
        _instanceCount_key = None
        if "instanceCount" in data:
            _instanceCount_key = "instanceCount"
        elif "InstanceCount" in data:
            _instanceCount_key = "InstanceCount"
        if _instanceCount_key:
            param_data = data[_instanceCount_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceCount>{esc(str(param_data))}</instanceCount>')
        # Serialize sourceCapacityReservation
        _sourceCapacityReservation_key = None
        if "sourceCapacityReservation" in data:
            _sourceCapacityReservation_key = "sourceCapacityReservation"
        elif "SourceCapacityReservation" in data:
            _sourceCapacityReservation_key = "SourceCapacityReservation"
        if _sourceCapacityReservation_key:
            param_data = data[_sourceCapacityReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sourceCapacityReservation>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</sourceCapacityReservation>')
        xml_parts.append(f'</MoveCapacityReservationInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_purchase_capacity_block_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<PurchaseCapacityBlockResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityBlockSet
        _capacityBlockSet_key = None
        if "capacityBlockSet" in data:
            _capacityBlockSet_key = "capacityBlockSet"
        elif "CapacityBlockSet" in data:
            _capacityBlockSet_key = "CapacityBlockSet"
        elif "CapacityBlocks" in data:
            _capacityBlockSet_key = "CapacityBlocks"
        if _capacityBlockSet_key:
            param_data = data[_capacityBlockSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityBlockSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityBlockSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityBlockSet/>')
        # Serialize capacityReservation
        _capacityReservation_key = None
        if "capacityReservation" in data:
            _capacityReservation_key = "capacityReservation"
        elif "CapacityReservation" in data:
            _capacityReservation_key = "CapacityReservation"
        if _capacityReservation_key:
            param_data = data[_capacityReservation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<capacityReservation>')
            xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</capacityReservation>')
        xml_parts.append(f'</PurchaseCapacityBlockResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_purchase_capacity_block_extension_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<PurchaseCapacityBlockExtensionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityBlockExtensionSet
        _capacityBlockExtensionSet_key = None
        if "capacityBlockExtensionSet" in data:
            _capacityBlockExtensionSet_key = "capacityBlockExtensionSet"
        elif "CapacityBlockExtensionSet" in data:
            _capacityBlockExtensionSet_key = "CapacityBlockExtensionSet"
        elif "CapacityBlockExtensions" in data:
            _capacityBlockExtensionSet_key = "CapacityBlockExtensions"
        if _capacityBlockExtensionSet_key:
            param_data = data[_capacityBlockExtensionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityBlockExtensionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(capacityreservation_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityBlockExtensionSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityBlockExtensionSet/>')
        xml_parts.append(f'</PurchaseCapacityBlockExtensionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reject_capacity_reservation_billing_ownership_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RejectCapacityReservationBillingOwnershipResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</RejectCapacityReservationBillingOwnershipResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AcceptCapacityReservationBillingOwnership": capacityreservation_ResponseSerializer.serialize_accept_capacity_reservation_billing_ownership_response,
            "AssociateCapacityReservationBillingOwner": capacityreservation_ResponseSerializer.serialize_associate_capacity_reservation_billing_owner_response,
            "CancelCapacityReservation": capacityreservation_ResponseSerializer.serialize_cancel_capacity_reservation_response,
            "CancelCapacityReservationFleets": capacityreservation_ResponseSerializer.serialize_cancel_capacity_reservation_fleets_response,
            "CreateCapacityReservation": capacityreservation_ResponseSerializer.serialize_create_capacity_reservation_response,
            "CreateCapacityReservationBySplitting": capacityreservation_ResponseSerializer.serialize_create_capacity_reservation_by_splitting_response,
            "CreateCapacityReservationFleet": capacityreservation_ResponseSerializer.serialize_create_capacity_reservation_fleet_response,
            "DescribeCapacityBlockExtensionHistory": capacityreservation_ResponseSerializer.serialize_describe_capacity_block_extension_history_response,
            "DescribeCapacityBlockExtensionOfferings": capacityreservation_ResponseSerializer.serialize_describe_capacity_block_extension_offerings_response,
            "DescribeCapacityBlockOfferings": capacityreservation_ResponseSerializer.serialize_describe_capacity_block_offerings_response,
            "DescribeCapacityBlocks": capacityreservation_ResponseSerializer.serialize_describe_capacity_blocks_response,
            "DescribeCapacityBlockStatus": capacityreservation_ResponseSerializer.serialize_describe_capacity_block_status_response,
            "DescribeCapacityReservationBillingRequests": capacityreservation_ResponseSerializer.serialize_describe_capacity_reservation_billing_requests_response,
            "DescribeCapacityReservations": capacityreservation_ResponseSerializer.serialize_describe_capacity_reservations_response,
            "DescribeCapacityReservationFleets": capacityreservation_ResponseSerializer.serialize_describe_capacity_reservation_fleets_response,
            "DescribeMacModificationTasks": capacityreservation_ResponseSerializer.serialize_describe_mac_modification_tasks_response,
            "DisassociateCapacityReservationBillingOwner": capacityreservation_ResponseSerializer.serialize_disassociate_capacity_reservation_billing_owner_response,
            "GetCapacityReservationUsage": capacityreservation_ResponseSerializer.serialize_get_capacity_reservation_usage_response,
            "GetGroupsForCapacityReservation": capacityreservation_ResponseSerializer.serialize_get_groups_for_capacity_reservation_response,
            "ModifyCapacityReservation": capacityreservation_ResponseSerializer.serialize_modify_capacity_reservation_response,
            "ModifyCapacityReservationFleet": capacityreservation_ResponseSerializer.serialize_modify_capacity_reservation_fleet_response,
            "ModifyInstanceCapacityReservationAttributes": capacityreservation_ResponseSerializer.serialize_modify_instance_capacity_reservation_attributes_response,
            "MoveCapacityReservationInstances": capacityreservation_ResponseSerializer.serialize_move_capacity_reservation_instances_response,
            "PurchaseCapacityBlock": capacityreservation_ResponseSerializer.serialize_purchase_capacity_block_response,
            "PurchaseCapacityBlockExtension": capacityreservation_ResponseSerializer.serialize_purchase_capacity_block_extension_response,
            "RejectCapacityReservationBillingOwnership": capacityreservation_ResponseSerializer.serialize_reject_capacity_reservation_billing_ownership_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

