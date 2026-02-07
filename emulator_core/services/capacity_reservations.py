from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend


class CapacityReservationState(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    PAYMENT_PENDING = "payment-pending"
    PAYMENT_FAILED = "payment-failed"
    ASSESSING = "assessing"
    DELAYED = "delayed"
    UNSUPPORTED = "unsupported"
    UNAVAILABLE = "unavailable"


class CapacityReservationEndDateType(str, Enum):
    UNLIMITED = "unlimited"
    LIMITED = "limited"


class CapacityReservationInstanceMatchCriteria(str, Enum):
    OPEN = "open"
    TARGETED = "targeted"


class CapacityReservationTenancy(str, Enum):
    DEFAULT = "default"
    DEDICATED = "dedicated"


class CapacityReservationFleetState(str, Enum):
    SUBMITTED = "submitted"
    MODIFYING = "modifying"
    ACTIVE = "active"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CapacityReservationFleetAllocationStrategy(str, Enum):
    PRIORITIZED = "prioritized"


class CapacityReservationFleetInstanceMatchCriteria(str, Enum):
    OPEN = "open"


class CapacityReservationFleetTenancy(str, Enum):
    DEFAULT = "default"
    DEDICATED = "dedicated"


class CapacityBlockState(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    UNAVAILABLE = "unavailable"
    CANCELLED = "cancelled"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    PAYMENT_PENDING = "payment-pending"
    PAYMENT_FAILED = "payment-failed"


class CapacityBlockOfferingTenancy(str, Enum):
    DEFAULT = "default"
    DEDICATED = "dedicated"


class CapacityBlockExtensionStatus(str, Enum):
    PAYMENT_PENDING = "payment-pending"
    PAYMENT_FAILED = "payment-failed"
    PAYMENT_SUCCEEDED = "payment-succeeded"


class CapacityReservationBillingRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REVOKED = "revoked"
    EXPIRED = "expired"


class CapacityReservationBillingRequestRole(str, Enum):
    ODCR_OWNER = "odcr-owner"
    UNUSED_RESERVATION_BILLING_OWNER = "unused-reservation-billing-owner"


class InterruptionType(str, Enum):
    ADHOC = "adhoc"


class InterruptibleCapacityAllocationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    UPDATING = "updating"
    CANCELING = "canceling"
    CANCELED = "canceled"
    FAILED = "failed"


class MacSystemIntegrityProtectionStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class MacModificationTaskState(str, Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    IN_PROGRESS = "in-progress"
    PENDING = "pending"


class MacModificationTaskType(str):
    SIP_MODIFICATION = "sip-modification"
    VOLUME_OWNERSHIP_DELEGATION = "volume-ownership-delegation"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class CapacityAllocation:
    allocation_type: Optional[str] = None  # e.g. "used"
    count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationType": self.allocation_type,
            "Count": self.count,
        }


@dataclass
class CapacityReservationCommitmentInfo:
    commitment_end_date: Optional[datetime] = None
    committed_instance_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CommitmentEndDate": self.commitment_end_date.isoformat() if self.commitment_end_date else None,
            "CommittedInstanceCount": self.committed_instance_count,
        }


@dataclass
class InterruptibleCapacityAllocation:
    instance_count: Optional[int] = None
    interruptible_capacity_reservation_id: Optional[str] = None
    interruption_type: Optional[InterruptionType] = None
    status: Optional[InterruptibleCapacityAllocationStatus] = None
    target_instance_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "InstanceCount": self.instance_count,
            "InterruptibleCapacityReservationId": self.interruptible_capacity_reservation_id,
            "InterruptionType": self.interruption_type.value if self.interruption_type else None,
            "Status": self.status.value if self.status else None,
            "TargetInstanceCount": self.target_instance_count,
        }


@dataclass
class InterruptionInfo:
    interruption_type: Optional[InterruptionType] = None
    source_capacity_reservation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "InterruptionType": self.interruption_type.value if self.interruption_type else None,
            "SourceCapacityReservationId": self.source_capacity_reservation_id,
        }


@dataclass
class CapacityReservation:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    available_instance_count: Optional[int] = None
    capacity_allocation_set: List[CapacityAllocation] = field(default_factory=list)
    capacity_block_id: Optional[str] = None
    capacity_reservation_arn: Optional[str] = None
    capacity_reservation_fleet_id: Optional[str] = None
    capacity_reservation_id: Optional[str] = None
    commitment_info: Optional[CapacityReservationCommitmentInfo] = None
    create_date: Optional[datetime] = None
    delivery_preference: Optional[str] = None  # fixed | incremental
    ebs_optimized: Optional[bool] = None
    end_date: Optional[datetime] = None
    end_date_type: Optional[CapacityReservationEndDateType] = None
    ephemeral_storage: Optional[bool] = None
    instance_match_criteria: Optional[CapacityReservationInstanceMatchCriteria] = None
    instance_platform: Optional[str] = None
    instance_type: Optional[str] = None
    interruptible: Optional[bool] = None
    interruptible_capacity_allocation: Optional[InterruptibleCapacityAllocation] = None
    interruption_info: Optional[InterruptionInfo] = None
    outpost_arn: Optional[str] = None
    owner_id: Optional[str] = None
    placement_group_arn: Optional[str] = None
    reservation_type: Optional[str] = None  # default | capacity-block
    start_date: Optional[datetime] = None
    state: Optional[CapacityReservationState] = None
    tag_set: List[Tag] = field(default_factory=list)
    tenancy: Optional[CapacityReservationTenancy] = None
    total_instance_count: Optional[int] = None
    unused_reservation_billing_owner_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "AvailabilityZoneId": self.availability_zone_id,
            "AvailableInstanceCount": self.available_instance_count,
            "CapacityAllocationSet": [alloc.to_dict() for alloc in self.capacity_allocation_set],
            "CapacityBlockId": self.capacity_block_id,
            "CapacityReservationArn": self.capacity_reservation_arn,
            "CapacityReservationFleetId": self.capacity_reservation_fleet_id,
            "CapacityReservationId": self.capacity_reservation_id,
            "CommitmentInfo": self.commitment_info.to_dict() if self.commitment_info else None,
            "CreateDate": self.create_date.isoformat() if self.create_date else None,
            "DeliveryPreference": self.delivery_preference,
            "EbsOptimized": self.ebs_optimized,
            "EndDate": self.end_date.isoformat() if self.end_date else None,
            "EndDateType": self.end_date_type.value if self.end_date_type else None,
            "EphemeralStorage": self.ephemeral_storage,
            "InstanceMatchCriteria": self.instance_match_criteria.value if self.instance_match_criteria else None,
            "InstancePlatform": self.instance_platform,
            "InstanceType": self.instance_type,
            "Interruptible": self.interruptible,
            "InterruptibleCapacityAllocation": self.interruptible_capacity_allocation.to_dict() if self.interruptible_capacity_allocation else None,
            "InterruptionInfo": self.interruption_info.to_dict() if self.interruption_info else None,
            "OutpostArn": self.outpost_arn,
            "OwnerId": self.owner_id,
            "PlacementGroupArn": self.placement_group_arn,
            "ReservationType": self.reservation_type,
            "StartDate": self.start_date.isoformat() if self.start_date else None,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "Tenancy": self.tenancy.value if self.tenancy else None,
            "TotalInstanceCount": self.total_instance_count,
            "UnusedReservationBillingOwnerId": self.unused_reservation_billing_owner_id,
        }


@dataclass
class FleetCapacityReservation:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    capacity_reservation_id: Optional[str] = None
    create_date: Optional[datetime] = None
    ebs_optimized: Optional[bool] = None
    fulfilled_capacity: Optional[float] = None
    instance_platform: Optional[str] = None
    instance_type: Optional[str] = None
    priority: Optional[int] = None
    total_instance_count: Optional[int] = None
    weight: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "AvailabilityZoneId": self.availability_zone_id,
            "CapacityReservationId": self.capacity_reservation_id,
            "CreateDate": self.create_date.isoformat() if self.create_date else None,
            "EbsOptimized": self.ebs_optimized,
            "FulfilledCapacity": self.fulfilled_capacity,
            "InstancePlatform": self.instance_platform,
            "InstanceType": self.instance_type,
            "Priority": self.priority,
            "TotalInstanceCount": self.total_instance_count,
            "Weight": self.weight,
        }


@dataclass
class CapacityReservationFleet:
    allocation_strategy: Optional[CapacityReservationFleetAllocationStrategy] = None
    capacity_reservation_fleet_arn: Optional[str] = None
    capacity_reservation_fleet_id: Optional[str] = None
    create_time: Optional[datetime] = None
    end_date: Optional[datetime] = None
    fleet_capacity_reservation_set: List[FleetCapacityReservation] = field(default_factory=list)
    instance_match_criteria: Optional[CapacityReservationFleetInstanceMatchCriteria] = None
    state: Optional[CapacityReservationFleetState] = None
    tag_set: List[Tag] = field(default_factory=list)
    tenancy: Optional[CapacityReservationFleetTenancy] = None
    total_fulfilled_capacity: Optional[float] = None
    total_target_capacity: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationStrategy": self.allocation_strategy.value if self.allocation_strategy else None,
            "CapacityReservationFleetArn": self.capacity_reservation_fleet_arn,
            "CapacityReservationFleetId": self.capacity_reservation_fleet_id,
            "CreateTime": self.create_time.isoformat() if self.create_time else None,
            "EndDate": self.end_date.isoformat() if self.end_date else None,
            "FleetCapacityReservationSet": [fcr.to_dict() for fcr in self.fleet_capacity_reservation_set],
            "InstanceMatchCriteria": self.instance_match_criteria.value if self.instance_match_criteria else None,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "Tenancy": self.tenancy.value if self.tenancy else None,
            "TotalFulfilledCapacity": self.total_fulfilled_capacity,
            "TotalTargetCapacity": self.total_target_capacity,
        }


@dataclass
class CapacityBlock:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    capacity_block_id: Optional[str] = None
    capacity_reservation_id_set: List[str] = field(default_factory=list)
    create_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    state: Optional[CapacityBlockState] = None
    tag_set: List[Tag] = field(default_factory=list)
    ultraserver_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "AvailabilityZoneId": self.availability_zone_id,
            "CapacityBlockId": self.capacity_block_id,
            "CapacityReservationIdSet": self.capacity_reservation_id_set,
            "CreateDate": self.create_date.isoformat() if self.create_date else None,
            "EndDate": self.end_date.isoformat() if self.end_date else None,
            "StartDate": self.start_date.isoformat() if self.start_date else None,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "UltraserverType": self.ultraserver_type,
        }


@dataclass
class CapacityBlockExtension:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    capacity_block_extension_duration_hours: Optional[int] = None
    capacity_block_extension_end_date: Optional[datetime] = None
    capacity_block_extension_offering_id: Optional[str] = None
    capacity_block_extension_purchase_date: Optional[datetime] = None
    capacity_block_extension_start_date: Optional[datetime] = None
    capacity_block_extension_status: Optional[CapacityBlockExtensionStatus] = None
    capacity_reservation_id: Optional[str] = None
    currency_code: Optional[str] = None
    instance_count: Optional[int] = None
    instance_type: Optional[str] = None
    upfront_fee: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "AvailabilityZoneId": self.availability_zone_id,
            "CapacityBlockExtensionDurationHours": self.capacity_block_extension_duration_hours,
            "CapacityBlockExtensionEndDate": self.capacity_block_extension_end_date.isoformat() if self.capacity_block_extension_end_date else None,
            "CapacityBlockExtensionOfferingId": self.capacity_block_extension_offering_id,
            "CapacityBlockExtensionPurchaseDate": self.capacity_block_extension_purchase_date.isoformat() if self.capacity_block_extension_purchase_date else None,
            "CapacityBlockExtensionStartDate": self.capacity_block_extension_start_date.isoformat() if self.capacity_block_extension_start_date else None,
            "CapacityBlockExtensionStatus": self.capacity_block_extension_status.value if self.capacity_block_extension_status else None,
            "CapacityReservationId": self.capacity_reservation_id,
            "CurrencyCode": self.currency_code,
            "InstanceCount": self.instance_count,
            "InstanceType": self.instance_type,
            "UpfrontFee": self.upfront_fee,
        }


@dataclass
class CapacityBlockExtensionOffering:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    capacity_block_extension_duration_hours: Optional[int] = None
    capacity_block_extension_end_date: Optional[datetime] = None
    capacity_block_extension_offering_id: Optional[str] = None
    capacity_block_extension_start_date: Optional[datetime] = None
    currency_code: Optional[str] = None
    instance_count: Optional[int] = None
    instance_type: Optional[str] = None
    start_date: Optional[datetime] = None
    tenancy: Optional[CapacityBlockOfferingTenancy] = None
    upfront_fee: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "AvailabilityZoneId": self.availability_zone_id,
            "CapacityBlockExtensionDurationHours": self.capacity_block_extension_duration_hours,
            "CapacityBlockExtensionEndDate": self.capacity_block_extension_end_date.isoformat() if self.capacity_block_extension_end_date else None,
            "CapacityBlockExtensionOfferingId": self.capacity_block_extension_offering_id,
            "CapacityBlockExtensionStartDate": self.capacity_block_extension_start_date.isoformat() if self.capacity_block_extension_start_date else None,
            "CurrencyCode": self.currency_code,
            "InstanceCount": self.instance_count,
            "InstanceType": self.instance_type,
            "StartDate": self.start_date.isoformat() if self.start_date else None,
            "Tenancy": self.tenancy.value if self.tenancy else None,
            "UpfrontFee": self.upfront_fee,
        }


@dataclass
class CapacityReservationInfo:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    instance_type: Optional[str] = None
    tenancy: Optional[CapacityReservationTenancy] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "AvailabilityZoneId": self.availability_zone_id,
            "InstanceType": self.instance_type,
            "Tenancy": self.tenancy.value if self.tenancy else None,
        }


@dataclass
class CapacityReservationBillingRequest:
    capacity_reservation_id: Optional[str] = None
    capacity_reservation_info: Optional[CapacityReservationInfo] = None
    last_update_time: Optional[datetime] = None
    requested_by: Optional[str] = None
    status: Optional[CapacityReservationBillingRequestStatus] = None
    status_message: Optional[str] = None
    unused_reservation_billing_owner_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CapacityReservationId": self.capacity_reservation_id,
            "CapacityReservationInfo": self.capacity_reservation_info.to_dict() if self.capacity_reservation_info else None,
            "LastUpdateTime": self.last_update_time.isoformat() if self.last_update_time else None,
            "RequestedBy": self.requested_by,
            "Status": self.status.value if self.status else None,
            "StatusMessage": self.status_message,
            "UnusedReservationBillingOwnerId": self.unused_reservation_billing_owner_id,
        }


class CapacityReservationsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)

    def accept_capacity_reservation_billing_ownership(self, params: dict) -> dict:
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Simulate permission check
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation"
            }

        if not capacity_reservation_id:
            raise Exception("Missing required parameter CapacityReservationId")

        capacity_reservation = self.state.capacity_reservations.get(capacity_reservation_id)
        if not capacity_reservation:
            raise Exception(f"CapacityReservationId {capacity_reservation_id} not found")

        # Accept billing ownership request: assign billing of available capacity to this account
        # For simplicity, assume billing ownership is assigned by setting owner id to current owner
        capacity_reservation["unusedReservationBillingOwnerId"] = self.get_owner_id()

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def associate_capacity_reservation_billing_owner(self, params: dict) -> dict:
        capacity_reservation_id = params.get("CapacityReservationId")
        unused_billing_owner_id = params.get("UnusedReservationBillingOwnerId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Simulate permission check
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation"
            }

        if not capacity_reservation_id:
            raise Exception("Missing required parameter CapacityReservationId")
        if not unused_billing_owner_id:
            raise Exception("Missing required parameter UnusedReservationBillingOwnerId")
        if not isinstance(unused_billing_owner_id, str) or len(unused_billing_owner_id) != 12 or not unused_billing_owner_id.isdigit():
            raise Exception("UnusedReservationBillingOwnerId must be a 12-digit string")

        capacity_reservation = self.state.capacity_reservations.get(capacity_reservation_id)
        if not capacity_reservation:
            raise Exception(f"CapacityReservationId {capacity_reservation_id} not found")

        # Assign billing of unused capacity to the specified consumer account
        capacity_reservation["unusedReservationBillingOwnerId"] = unused_billing_owner_id

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def cancel_capacity_reservation(self, params: dict) -> dict:
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Simulate permission check
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation"
            }

        if not capacity_reservation_id:
            raise Exception("Missing required parameter CapacityReservationId")

        capacity_reservation = self.state.capacity_reservations.get(capacity_reservation_id)
        if not capacity_reservation:
            raise Exception(f"CapacityReservationId {capacity_reservation_id} not found")

        # Only allow cancel if state is assessing or other allowed states
        current_state = capacity_reservation.get("state")
        allowed_cancel_states = {"assessing", "active", "pending", "scheduled", "delayed"}
        if current_state not in allowed_cancel_states:
            raise Exception(f"Cannot cancel Capacity Reservation in state {current_state}")

        # Change state to cancelled and release capacity
        capacity_reservation["state"] = "cancelled"
        capacity_reservation["availableInstanceCount"] = 0

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def cancel_capacity_reservation_fleets(self, params: dict) -> dict:
        fleet_ids = params.get("CapacityReservationFleetId.N")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Simulate permission check
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "failedFleetCancellationSet": [],
                "successfulFleetCancellationSet": [],
            }

        if not fleet_ids or not isinstance(fleet_ids, list):
            raise Exception("Missing or invalid required parameter CapacityReservationFleetId.N")

        failed_fleet_cancellations = []
        successful_fleet_cancellations = []

        for fleet_id in fleet_ids:
            fleet = self.state.capacity_reservation_fleets.get(fleet_id)
            if not fleet:
                failed_fleet_cancellations.append({
                    "capacityReservationFleetId": fleet_id,
                    "cancelCapacityReservationFleetError": {
                        "code": "InvalidCapacityReservationFleetId.NotFound",
                        "message": f"Capacity Reservation Fleet {fleet_id} not found"
                    }
                })
                continue

            # Cancel the fleet: change status to cancelled
            previous_state = fleet.get("state")
            fleet["state"] = "cancelled"

            # Cancel all individual capacity reservations in the fleet
            reservations = fleet.get("capacityReservations", [])
            for res_id in reservations:
                res = self.state.capacity_reservations.get(res_id)
                if res:
                    res["state"] = "cancelled"
                    res["availableInstanceCount"] = 0

            successful_fleet_cancellations.append({
                "capacityReservationFleetId": fleet_id,
                "currentFleetState": "cancelled",
                "previousFleetState": previous_state,
            })

        return {
            "requestId": self.generate_request_id(),
            "failedFleetCancellationSet": failed_fleet_cancellations,
            "successfulFleetCancellationSet": successful_fleet_cancellations,
        }


    def create_capacity_reservation(self, params: dict) -> dict:
        # Validate required parameters
        instance_count = params.get("InstanceCount")
        instance_platform = params.get("InstancePlatform")
        instance_type = params.get("InstanceType")

        if instance_count is None:
            raise Exception("Missing required parameter InstanceCount")
        if not isinstance(instance_count, int) or not (1 <= instance_count <= 1000):
            raise Exception("InstanceCount must be an integer between 1 and 1000")

        if not instance_platform:
            raise Exception("Missing required parameter InstancePlatform")
        if not instance_type:
            raise Exception("Missing required parameter InstanceType")

        # Optional parameters
        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")
        client_token = params.get("ClientToken")
        commitment_duration = params.get("CommitmentDuration")
        delivery_preference = params.get("DeliveryPreference")
        dry_run = params.get("DryRun", False)
        ebs_optimized = params.get("EbsOptimized")
        end_date = params.get("EndDate")
        end_date_type = params.get("EndDateType")
        ephemeral_storage = params.get("EphemeralStorage")
        instance_match_criteria = params.get("InstanceMatchCriteria", "open")
        outpost_arn = params.get("OutpostArn")
        placement_group_arn = params.get("PlacementGroupArn")
        start_date = params.get("StartDate")
        tag_specifications = params.get("TagSpecifications.N", [])
        tenancy = params.get("Tenancy")

        if dry_run:
            # Simulate permission check
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "capacityReservation": None,
                "__type": "DryRunOperation"
            }

        # Validate end_date_type and end_date
        if end_date_type == "limited" and not end_date:
            raise Exception("EndDate must be provided if EndDateType is limited")
        if end_date_type == "unlimited" and end_date:
            raise Exception("EndDate must not be provided if EndDateType is unlimited")

        # Validate delivery_preference if provided
        if delivery_preference and delivery_preference not in {"fixed", "incremental"}:
            raise Exception("DeliveryPreference must be 'fixed' or 'incremental'")

        # Validate instance_match_criteria
        if instance_match_criteria not in {"open", "targeted"}:
            raise Exception("InstanceMatchCriteria must be 'open' or 'targeted'")

        # Validate tenancy
        if tenancy and tenancy not in {"default", "dedicated"}:
            raise Exception("Tenancy must be 'default' or 'dedicated'")

        # Validate tags
        tags = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be dict with ResourceType and Tags
            if not isinstance(tag_spec, dict):
                continue
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tags.append({"Key": key, "Value": value})

        # Generate capacity reservation id
        capacity_reservation_id = self.generate_unique_id()

        # Compose capacity reservation object
        capacity_reservation = {
            "capacityReservationId": capacity_reservation_id,
            "availabilityZone": availability_zone,
            "availabilityZoneId": availability_zone_id,
            "availableInstanceCount": instance_count,
            "capacityAllocationSet": [],
            "capacityBlockId": None,
            "capacityReservationArn": f"arn:aws:ec2:::capacity-reservation/{capacity_reservation_id}",
            "capacityReservationFleetId": None,
            "commitmentInfo": None,
            "createDate": None,
            "deliveryPreference": delivery_preference,
            "ebsOptimized": ebs_optimized,
            "endDate": end_date,
            "endDateType": end_date_type,
            "ephemeralStorage": ephemeral_storage,
            "instanceMatchCriteria": instance_match_criteria,
            "instancePlatform": instance_platform,
            "instanceType": instance_type,
            "interruptible": False,
            "interruptibleCapacityAllocation": None,
            "interruptionInfo": None,
            "outpostArn": outpost_arn,
            "ownerId": self.get_owner_id(),
            "placementGroupArn": placement_group_arn,
            "reservationType": "default",
            "startDate": start_date,
            "state": "active",
            "tagSet": tags,
            "tenancy": tenancy,
            "totalInstanceCount": instance_count,
            "unusedReservationBillingOwnerId": None,
        }

        # Store in state
        self.state.capacity_reservations[capacity_reservation_id] = capacity_reservation

        return {
            "capacityReservation": capacity_reservation,
            "requestId": self.generate_request_id(),
        }

    def create_capacity_reservation_by_splitting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Capacity Reservation by splitting the capacity of the source Capacity Reservation.
        The new Capacity Reservation will have the same attributes as the source Capacity Reservation except for tags.
        The source Capacity Reservation must be active and owned by your AWS account.
        """
        # Validate required parameters
        instance_count = params.get("InstanceCount")
        source_cr_id = params.get("SourceCapacityReservationId")
        if instance_count is None:
            raise ValueError("InstanceCount is required")
        if not isinstance(instance_count, int) or instance_count <= 0:
            raise ValueError("InstanceCount must be a positive integer")
        if not source_cr_id:
            raise ValueError("SourceCapacityReservationId is required")

        # DryRun check
        if params.get("DryRun"):
            # Here we would check permissions, but for emulator just return DryRunOperation error
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        # Find source capacity reservation
        source_cr = self.state.capacity_reservations.get(source_cr_id)
        if source_cr is None:
            raise ValueError(f"Source Capacity Reservation {source_cr_id} not found")

        # Check ownership
        if source_cr.get("ownerId") != self.get_owner_id():
            raise ValueError("Source Capacity Reservation is not owned by your AWS account")

        # Check state active
        if source_cr.get("state") != "active":
            raise ValueError("Source Capacity Reservation must be active to split")

        # Check available capacity in source
        available = source_cr.get("availableInstanceCount", 0)
        if instance_count > available:
            raise ValueError("InstanceCount to split exceeds available capacity in source Capacity Reservation")

        # Generate new Capacity Reservation ID and request ID
        new_cr_id = self.generate_unique_id()
        request_id = self.generate_request_id()

        # Copy attributes from source except tags
        new_cr = source_cr.copy()
        new_cr["capacityReservationId"] = new_cr_id
        new_cr["availableInstanceCount"] = instance_count
        new_cr["totalInstanceCount"] = instance_count
        new_cr["tagSet"] = []  # tags are not copied

        # Apply tags if provided
        tag_specifications = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be dict with "Tags" key containing list of tags
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and not key.lower().startswith("aws:"):
                    tags.append({"Key": key, "Value": value})
        if tags:
            new_cr["tagSet"] = tags

        # Reduce available and total instance count in source
        source_cr["availableInstanceCount"] = source_cr.get("availableInstanceCount", 0) - instance_count
        source_cr["totalInstanceCount"] = source_cr.get("totalInstanceCount", 0) - instance_count

        # Save new capacity reservation
        self.state.capacity_reservations[new_cr_id] = new_cr

        # Prepare response
        response = {
            "destinationCapacityReservation": new_cr,
            "instanceCount": instance_count,
            "requestId": request_id,
            "sourceCapacityReservation": source_cr,
        }
        return response


    def create_capacity_reservation_fleet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a Capacity Reservation Fleet.
        """
        # Validate required parameters
        instance_type_specs = params.get("InstanceTypeSpecification.N")
        total_target_capacity = params.get("TotalTargetCapacity")
        if instance_type_specs is None or not isinstance(instance_type_specs, list) or len(instance_type_specs) == 0:
            raise ValueError("InstanceTypeSpecification.N is required and must be a non-empty list")
        if total_target_capacity is None:
            raise ValueError("TotalTargetCapacity is required")
        if not isinstance(total_target_capacity, int) or total_target_capacity <= 0:
            raise ValueError("TotalTargetCapacity must be a positive integer")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        # AllocationStrategy validation
        allocation_strategy = params.get("AllocationStrategy", "prioritized")
        if allocation_strategy != "prioritized":
            raise ValueError("Only 'prioritized' allocation strategy is supported")

        # InstanceMatchCriteria validation
        instance_match_criteria = params.get("InstanceMatchCriteria", "open")
        if instance_match_criteria != "open":
            raise ValueError("Only 'open' instance match criteria is supported")

        # Tenancy validation
        tenancy = params.get("Tenancy", "default")
        if tenancy != "default":
            raise ValueError("Only 'default' tenancy is supported")

        # Validate instance type specs: all must have same AvailabilityZone or AvailabilityZoneId
        az = None
        for spec in instance_type_specs:
            spec_az = spec.get("AvailabilityZone")
            spec_az_id = spec.get("AvailabilityZoneId")
            if az is None:
                az = spec_az or spec_az_id
            else:
                if (spec_az and spec_az != az) or (spec_az_id and spec_az_id != az):
                    raise ValueError("All instance type specifications must have the same Availability Zone or Availability Zone ID")

        # Generate Capacity Reservation Fleet ID and request ID
        cr_fleet_id = self.generate_unique_id()
        request_id = self.generate_request_id()

        # Create fleet capacity reservation set (simulate individual capacity reservations)
        fleet_capacity_reservations = []
        # For simplicity, create one capacity reservation per instance type spec
        for spec in instance_type_specs:
            cr_id = self.generate_unique_id()
            instance_type = spec.get("InstanceType")
            instance_platform = spec.get("InstancePlatform")
            ebs_optimized = spec.get("EbsOptimized", False)
            az_spec = spec.get("AvailabilityZone") or spec.get("AvailabilityZoneId")
            weight = spec.get("Weight", 1.0)
            priority = spec.get("Priority", 0)
            total_instance_count = int(total_target_capacity * weight) if weight else 0
            # Create capacity reservation object
            cr = {
                "capacityReservationId": cr_id,
                "availabilityZone": az_spec if az_spec else None,
                "availabilityZoneId": az_spec if az_spec else None,
                "instanceType": instance_type,
                "instancePlatform": instance_platform,
                "ebsOptimized": ebs_optimized,
                "totalInstanceCount": total_instance_count,
                "availableInstanceCount": total_instance_count,
                "priority": priority,
                "weight": weight,
                "createDate": None,  # Could set current timestamp if desired
            }
            # Save individual capacity reservation
            self.state.capacity_reservations[cr_id] = cr
            fleet_capacity_reservations.append(cr)

        # Create Capacity Reservation Fleet object
        cr_fleet = {
            "capacityReservationFleetId": cr_fleet_id,
            "allocationStrategy": allocation_strategy,
            "instanceMatchCriteria": instance_match_criteria,
            "tenancy": tenancy,
            "totalTargetCapacity": total_target_capacity,
            "totalFulfilledCapacity": sum(cr["totalInstanceCount"] for cr in fleet_capacity_reservations),
            "fleetCapacityReservationSet": fleet_capacity_reservations,
            "state": "submitted",
            "createTime": None,  # Could set current timestamp if desired
            "endDate": params.get("EndDate"),
            "tagSet": [],
        }

        # Apply tags if provided
        tag_specifications = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and not key.lower().startswith("aws:"):
                    tags.append({"Key": key, "Value": value})
        if tags:
            cr_fleet["tagSet"] = tags

        # Save Capacity Reservation Fleet in state resources
        self.state.resources[cr_fleet_id] = cr_fleet

        # Prepare response
        response = {
            "allocationStrategy": allocation_strategy,
            "capacityReservationFleetId": cr_fleet_id,
            "createTime": cr_fleet["createTime"],
            "endDate": cr_fleet["endDate"],
            "fleetCapacityReservationSet": fleet_capacity_reservations,
            "instanceMatchCriteria": instance_match_criteria,
            "requestId": request_id,
            "state": cr_fleet["state"],
            "tagSet": cr_fleet["tagSet"],
            "tenancy": tenancy,
            "totalFulfilledCapacity": cr_fleet["totalFulfilledCapacity"],
            "totalTargetCapacity": total_target_capacity,
        }
        return response


    def describe_capacity_block_extension_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Describes the events for the specified Capacity Block extension during the specified time.
        """
        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        # Extract filters and parameters
        capacity_reservation_ids = params.get("CapacityReservationId.N", [])
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults", 1000)
        next_token = params.get("NextToken")

        # Validate max_results
        if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
            raise ValueError("MaxResults must be an integer between 1 and 1000")

        # For this emulator, assume capacity block extensions are stored in self.state.capacity_block_extensions
        # which is a dict of extension_id -> extension object
        # If not present, empty dict
        capacity_block_extensions = getattr(self.state, "capacity_block_extensions", {})

        # Filter by CapacityReservationId if provided
        filtered_extensions = []
        for ext in capacity_block_extensions.values():
            if capacity_reservation_ids and ext.get("capacityReservationId") not in capacity_reservation_ids:
                continue
            # Apply filters
            match = True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue
                ext_value = ext.get(name)
                if ext_value is None:
                    # Try mapping filter names to keys if needed
                    # For example, filter name "capacity-block-extension-status" maps to "capacityBlockExtensionStatus"
                    # Normalize keys for matching
                    key_map = {
                        "availability-zone": "availabilityZone",
                        "availability-zone-id": "availabilityZoneId",
                        "capacity-block-extension-offering-id": "capacityBlockExtensionOfferingId",
                        "capacity-block-extension-status": "capacityBlockExtensionStatus",
                        "capacity-reservation-id": "capacityReservationId",
                        "instance-type": "instanceType",
                    }
                    mapped_key = key_map.get(name)
                    if mapped_key:
                        ext_value = ext.get(mapped_key)
                if ext_value is None or str(ext_value) not in values:
                    match = False
                    break
            if match:
                filtered_extensions.append(ext)

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = start_index + max_results
        page_extensions = filtered_extensions[start_index:end_index]

        # Prepare next token
        new_next_token = str(end_index) if end_index < len(filtered_extensions) else None

        # Prepare response
        response = {
            "capacityBlockExtensionSet": page_extensions,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_capacity_block_extension_offerings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Describes Capacity Block extension offerings available for purchase in the AWS Region.
        """
        # Validate required parameters
        duration_hours = params.get("CapacityBlockExtensionDurationHours")
        capacity_reservation_id = params.get("CapacityReservationId")
        if duration_hours is None or not isinstance(duration_hours, int) or duration_hours <= 0:
            raise ValueError("CapacityBlockExtensionDurationHours is required and must be a positive integer")
        if not capacity_reservation_id:
            raise ValueError("CapacityReservationId is required")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        # For this emulator, assume capacity block extension offerings are stored in self.state.capacity_block_extension_offerings
        # which is a dict of offering_id -> offering object
        capacity_block_extension_offerings = getattr(self.state, "capacity_block_extension_offerings", {})

        # Filter offerings by duration and capacity reservation id
        filtered_offerings = []
        for offering in capacity_block_extension_offerings.values():
            # Check duration matches
            if offering.get("capacityBlockExtensionDurationHours") != duration_hours:
                continue
            # Check capacity reservation id matches (assuming offering has a list or single id)
            # Since the API param is CapacityReservationId, we filter offerings related to that reservation
            # For emulator, assume offering has "capacityReservationId" field
            if offering.get("capacityReservationId") != capacity_reservation_id:
                continue
            filtered_offerings.append(offering)

        # Pagination parameters
        max_results = params.get("MaxResults", 1000)
        next_token = params.get("NextToken")
        if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
            raise ValueError("MaxResults must be an integer between 1 and 1000")

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = start_index + max_results
        page_offerings = filtered_offerings[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(filtered_offerings) else None

        # Prepare response
        response = {
            "capacityBlockExtensionOfferingSet": page_offerings,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_capacity_block_offerings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Describes Capacity Block offerings available for purchase in the AWS Region.
        """
        # Validate required parameters
        capacity_duration_hours = params.get("CapacityDurationHours")
        if capacity_duration_hours is None or not isinstance(capacity_duration_hours, int) or capacity_duration_hours <= 0:
            raise ValueError("CapacityDurationHours is required and must be a positive integer")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        # For this emulator, assume capacity block offerings are stored in self.state.capacity_block_offerings
        # which is a dict of offering_id -> offering object
        capacity_block_offerings = getattr(self.state, "capacity_block_offerings", {})

        # Filter offerings by parameters
        filtered_offerings = []
        for offering in capacity_block_offerings.values():
            # Filter by CapacityDurationHours
            if offering.get("capacityBlockDurationHours") != capacity_duration_hours:
                continue
            # Optional filters
            instance_count = params.get("InstanceCount")
            if instance_count is not None and offering.get("instanceCount") != instance_count:
                continue
            instance_type = params.get("InstanceType")
            if instance_type is not None and offering.get("instanceType") != instance_type:
                continue
            ultraserver_count = params.get("UltraserverCount")
            if ultraserver_count is not None and offering.get("ultraserverCount") != ultraserver_count:
                continue
            ultraserver_type = params.get("UltraserverType")
            if ultraserver_type is not None and offering.get("ultraserverType") != ultraserver_type:
                continue
            # Date range filters
            start_date_range = params.get("StartDateRange")
            if start_date_range is not None and offering.get("startDate") is not None:
                if offering.get("startDate") < start_date_range:
                    continue
            end_date_range = params.get("EndDateRange")
            if end_date_range is not None and offering.get("endDate") is not None:
                if offering.get("endDate") > end_date_range:
                    continue
            filtered_offerings.append(offering)

        # Pagination parameters
        max_results = params.get("MaxResults", 1000)
        next_token = params.get("NextToken")
        if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
            raise ValueError("MaxResults must be an integer between 1 and 1000")

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = start_index + max_results
        page_offerings = filtered_offerings[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(filtered_offerings) else None

        # Prepare response
        response = {
            "capacityBlockOfferingSet": page_offerings,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response

    def describe_capacity_blocks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_block_ids = params.get("CapacityBlockId.N", [])
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # DryRun check (simplified, assuming permission granted)
        if dry_run:
            # In real implementation, check permissions here
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Collect all capacity blocks from state
        all_blocks = list(self.state.capacity_blocks.values()) if hasattr(self.state, "capacity_blocks") else []

        # Filter by CapacityBlockId if provided
        if capacity_block_ids:
            all_blocks = [cb for cb in all_blocks if cb.get("capacityBlockId") in capacity_block_ids]

        # Apply filters
        def match_filter(cb, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to capacity block attributes
            # Support filters as per description
            if name == "capacity-block-id":
                return cb.get("capacityBlockId") in values
            elif name == "ultraserver-type":
                return cb.get("ultraserverType") in values
            elif name == "availability-zone":
                return cb.get("availabilityZone") in values
            elif name == "start-date":
                # Filter by startDate string matching any of values (ISO8601)
                return any(cb.get("startDate") and cb.get("startDate").startswith(v) for v in values)
            elif name == "end-date":
                return any(cb.get("endDate") and cb.get("endDate").startswith(v) for v in values)
            elif name == "create-date":
                return any(cb.get("createDate") and cb.get("createDate").startswith(v) for v in values)
            elif name == "state":
                return cb.get("state") in values
            elif name == "tags":
                # tags filter: check if any tag key or value matches any value
                tags = cb.get("tagSet", [])
                for tag in tags:
                    if tag.get("Key") in values or tag.get("Value") in values:
                        return True
                return False
            return True

        for f in filters:
            all_blocks = [cb for cb in all_blocks if match_filter(cb, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    max_results = 1
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = 1000
        else:
            max_results = 1000

        paged_blocks = all_blocks[start_index:start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_blocks) else None

        return {
            "capacityBlockSet": paged_blocks,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_capacity_block_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_block_ids = params.get("CapacityBlockId.N", [])
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # DryRun check (simplified)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Collect all capacity block statuses from state
        all_statuses = list(self.state.capacity_block_statuses.values()) if hasattr(self.state, "capacity_block_statuses") else []

        # Filter by CapacityBlockId if provided
        if capacity_block_ids:
            all_statuses = [status for status in all_statuses if status.get("capacityBlockId") in capacity_block_ids]

        # Apply filters
        def match_filter(status, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            if name == "interconnect-status":
                return status.get("interconnectStatus") in values
            return True

        for f in filters:
            all_statuses = [status for status in all_statuses if match_filter(status, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    max_results = 1
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = 1000
        else:
            max_results = 1000

        paged_statuses = all_statuses[start_index:start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_statuses) else None

        return {
            "capacityBlockStatusSet": paged_statuses,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_capacity_reservation_billing_requests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_reservation_ids = params.get("CapacityReservationId.N", [])
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        role = params.get("Role")

        # Validate required parameter Role
        if role not in ("odcr-owner", "unused-reservation-billing-owner"):
            raise ValueError("Role parameter is required and must be 'odcr-owner' or 'unused-reservation-billing-owner'")

        # DryRun check (simplified)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Collect all billing requests from state
        all_requests = list(self.state.capacity_reservation_billing_requests.values()) if hasattr(self.state, "capacity_reservation_billing_requests") else []

        # Filter by CapacityReservationId if provided
        if capacity_reservation_ids:
            all_requests = [req for req in all_requests if req.get("capacityReservationId") in capacity_reservation_ids]

        # Apply filters
        def match_filter(req, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            if name == "status":
                return req.get("status") in values
            elif name == "requested-by" and role == "odcr-owner":
                return req.get("requestedBy") in values
            elif name == "unused-reservation-billing-owner" and role == "unused-reservation-billing-owner":
                return req.get("unusedReservationBillingOwnerId") in values
            return True

        for f in filters:
            all_requests = [req for req in all_requests if match_filter(req, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    max_results = 1
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = 1000
        else:
            max_results = 1000

        paged_requests = all_requests[start_index:start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_requests) else None

        return {
            "capacityReservationBillingRequestSet": paged_requests,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_capacity_reservations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_reservation_ids = params.get("CapacityReservationId.N", [])
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # DryRun check (simplified)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Collect all capacity reservations from state
        all_reservations = list(self.state.capacity_reservations.values())

        # Filter by CapacityReservationId if provided
        if capacity_reservation_ids:
            all_reservations = [cr for cr in all_reservations if cr.get("capacityReservationId") in capacity_reservation_ids]

        # Apply filters
        def match_filter(cr, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to capacity reservation attributes
            if name == "instance-type":
                return cr.get("instanceType") in values
            elif name == "owner-id":
                return cr.get("ownerId") in values
            elif name == "instance-platform":
                return cr.get("instancePlatform") in values
            elif name == "availability-zone":
                return cr.get("availabilityZone") in values
            elif name == "tenancy":
                return cr.get("tenancy") in values
            elif name == "outpost-arn":
                return cr.get("outpostArn") in values
            elif name == "state":
                return cr.get("state") in values
            elif name == "start-date":
                return any(cr.get("startDate") and cr.get("startDate").startswith(v) for v in values)
            elif name == "end-date":
                return any(cr.get("endDate") and cr.get("endDate").startswith(v) for v in values)
            elif name == "end-date-type":
                return cr.get("endDateType") in values
            elif name == "instance-match-criteria":
                return cr.get("instanceMatchCriteria") in values
            elif name == "placement-group-arn":
                return cr.get("placementGroupArn") in values
            return True

        for f in filters:
            all_reservations = [cr for cr in all_reservations if match_filter(cr, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    max_results = 1
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = 1000
        else:
            max_results = 1000

        paged_reservations = all_reservations[start_index:start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_reservations) else None

        return {
            "capacityReservationSet": paged_reservations,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_capacity_reservation_fleets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_reservation_fleet_ids = params.get("CapacityReservationFleetId.N", [])
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # DryRun check (simplified)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Collect all capacity reservation fleets from state
        all_fleets = list(self.state.capacity_reservation_fleets.values()) if hasattr(self.state, "capacity_reservation_fleets") else []

        # Filter by CapacityReservationFleetId if provided
        if capacity_reservation_fleet_ids:
            all_fleets = [fleet for fleet in all_fleets if fleet.get("capacityReservationFleetId") in capacity_reservation_fleet_ids]

        # Apply filters
        def match_filter(fleet, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            if name == "state":
                return fleet.get("state") in values
            elif name == "instance-match-criteria":
                return fleet.get("instanceMatchCriteria") in values
            elif name == "tenancy":
                return fleet.get("tenancy") in values
            elif name == "allocation-strategy":
                return fleet.get("allocationStrategy") in values
            return True

        for f in filters:
            all_fleets = [fleet for fleet in all_fleets if match_filter(fleet, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    max_results = 1
                elif max_results > 100:
                    max_results = 100
            except Exception:
                max_results = 100
        else:
            max_results = 100

        paged_fleets = all_fleets[start_index:start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_fleets) else None

        return {
            "capacityReservationFleetSet": paged_fleets,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def describe_mac_modification_tasks(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        task_ids = params.get("MacModificationTaskId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # DryRun check
        if dry_run:
            # Assume permission granted for emulator
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 500:
                raise ValueError("MaxResults must be an integer between 5 and 500")

        # Collect all mac modification tasks from state
        all_tasks = []
        for task in self.state.mac_modification_tasks.values():
            all_tasks.append(task)

        # Filter by task ids if provided
        if task_ids:
            all_tasks = [t for t in all_tasks if t.get("macModificationTaskId") in task_ids]

        # Apply filters if provided
        def match_filter(task, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # no filter criteria, match all

            # Map filter names to task fields or nested fields
            if name == "instance-id":
                return task.get("instanceId") in values
            elif name == "task-state":
                return task.get("taskState") in values
            elif name == "mac-system-integrity-protection-configuration.sip-status":
                sip_config = task.get("macSystemIntegrityProtectionConfig", {})
                return sip_config.get("status") in values
            elif name == "start-time":
                # startTime is ISO8601 string, filter values are strings, match exact
                return task.get("startTime") in values
            elif name == "task-type":
                return task.get("taskType") in values
            else:
                # Unknown filter name, ignore filter
                return True

        if filters:
            # filters is a list of dicts with Name and Values keys
            filtered_tasks = []
            for task in all_tasks:
                # For each filter, task must match at least one value
                if all(match_filter(task, f) for f in filters):
                    filtered_tasks.append(task)
            all_tasks = filtered_tasks

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_tasks)
        if max_results:
            end_index = min(start_index + max_results, len(all_tasks))

        paged_tasks = all_tasks[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(all_tasks):
            new_next_token = str(end_index)

        # Compose response
        response = {
            "macModificationTaskSet": paged_tasks,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def disassociate_capacity_reservation_billing_owner(self, params: dict) -> dict:
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)
        unused_billing_owner_id = params.get("UnusedReservationBillingOwnerId")

        # Validate required parameters
        if not capacity_reservation_id:
            raise ValueError("CapacityReservationId is required")
        if not unused_billing_owner_id:
            raise ValueError("UnusedReservationBillingOwnerId is required")
        if not isinstance(unused_billing_owner_id, str) or len(unused_billing_owner_id) != 12 or not unused_billing_owner_id.isdigit():
            raise ValueError("UnusedReservationBillingOwnerId must be a 12-digit string")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Find capacity reservation
        cr = self.state.capacity_reservations.get(capacity_reservation_id)
        if not cr:
            raise ValueError(f"CapacityReservation {capacity_reservation_id} not found")

        # Check if there is a pending or accepted billing ownership request for this owner
        # We assume cr has a dict key 'billing_owners' mapping owner_id to status ('pending', 'accepted', etc)
        billing_owners = cr.get("billing_owners", {})
        if unused_billing_owner_id not in billing_owners:
            # No such billing owner request
            return {
                "requestId": self.generate_request_id(),
                "return": False,
            }

        # Remove the billing ownership request or revoke it
        # If status is pending or accepted, remove it
        del billing_owners[unused_billing_owner_id]
        cr["billing_owners"] = billing_owners

        # Save back to state
        self.state.capacity_reservations[capacity_reservation_id] = cr

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def get_capacity_reservation_usage(self, params: dict) -> dict:
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate required parameters
        if not capacity_reservation_id:
            raise ValueError("CapacityReservationId is required")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 1 and 1000")

        # Find capacity reservation
        cr = self.state.capacity_reservations.get(capacity_reservation_id)
        if not cr:
            raise ValueError(f"CapacityReservation {capacity_reservation_id} not found")

        # Compose instance usage set
        # If shared, usage info for owner and each AWS account using shared capacity
        # If not shared, only owner's usage
        instance_usage_set = []
        if cr.get("shared", False):
            # cr should have usage info per account in cr.get("usage_per_account", dict)
            usage_per_account = cr.get("usage_per_account", {})
            for account_id, used_count in usage_per_account.items():
                instance_usage_set.append({
                    "accountId": account_id,
                    "usedInstanceCount": used_count,
                })
        else:
            # Only owner usage
            owner_id = cr.get("ownerId", self.get_owner_id())
            used_count = cr.get("usedInstanceCount", 0)
            instance_usage_set.append({
                "accountId": owner_id,
                "usedInstanceCount": used_count,
            })

        # Pagination for instanceUsageSet
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(instance_usage_set)
        if max_results:
            end_index = min(start_index + max_results, len(instance_usage_set))

        paged_instance_usage = instance_usage_set[start_index:end_index]

        new_next_token = None
        if end_index < len(instance_usage_set):
            new_next_token = str(end_index)

        # Compose interruptibleCapacityAllocation info if present
        interruptible_allocation = cr.get("interruptibleCapacityAllocation")
        if interruptible_allocation is None:
            interruptible_allocation = {}

        # Compose interruptionInfo if present
        interruption_info = cr.get("interruptionInfo")
        if interruption_info is None:
            interruption_info = {}

        response = {
            "availableInstanceCount": cr.get("availableInstanceCount", 0),
            "capacityReservationId": capacity_reservation_id,
            "instanceType": cr.get("instanceType"),
            "instanceUsageSet": paged_instance_usage,
            "interruptible": cr.get("interruptible", False),
            "interruptibleCapacityAllocation": interruptible_allocation,
            "interruptionInfo": interruption_info,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "state": cr.get("state"),
            "totalInstanceCount": cr.get("totalInstanceCount", 0),
        }
        return response


    def get_groups_for_capacity_reservation(self, params: dict) -> dict:
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate required parameters
        if not capacity_reservation_id:
            raise ValueError("CapacityReservationId is required")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 1 and 1000")

        # Find capacity reservation
        cr = self.state.capacity_reservations.get(capacity_reservation_id)
        if not cr:
            raise ValueError(f"CapacityReservation {capacity_reservation_id} not found")

        # Get groups associated with this capacity reservation
        # Assume cr has a list of group dicts under key 'groups' with keys 'groupArn' and 'ownerId'
        groups = cr.get("groups", [])

        # If capacity reservation is shared with caller, return only groups owned by caller
        owner_id = self.get_owner_id()
        if cr.get("shared", False):
            groups = [g for g in groups if g.get("ownerId") == owner_id]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(groups)
        if max_results:
            end_index = min(start_index + max_results, len(groups))

        paged_groups = groups[start_index:end_index]

        new_next_token = None
        if end_index < len(groups):
            new_next_token = str(end_index)

        response = {
            "capacityReservationGroupSet": paged_groups,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def modify_capacity_reservation(self, params: dict) -> dict:
        accept = params.get("Accept")
        additional_info = params.get("AdditionalInfo")
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)
        end_date = params.get("EndDate")
        end_date_type = params.get("EndDateType")
        instance_count = params.get("InstanceCount")
        instance_match_criteria = params.get("InstanceMatchCriteria")

        # Validate required parameters
        if not capacity_reservation_id:
            raise ValueError("CapacityReservationId is required")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Find capacity reservation
        cr = self.state.capacity_reservations.get(capacity_reservation_id)
        if not cr:
            raise ValueError(f"CapacityReservation {capacity_reservation_id} not found")

        # Validate EndDateType and EndDate
        if end_date_type:
            if end_date_type not in ("unlimited", "limited"):
                raise ValueError("EndDateType must be 'unlimited' or 'limited'")
            if end_date_type == "limited" and not end_date:
                raise ValueError("EndDate must be provided if EndDateType is 'limited'")
            if end_date_type == "unlimited" and end_date:
                raise ValueError("EndDate must not be provided if EndDateType is 'unlimited'")

        # Validate instance_match_criteria
        if instance_match_criteria:
            if instance_match_criteria not in ("open", "targeted"):
                raise ValueError("InstanceMatchCriteria must be 'open' or 'targeted'")

        # Validate instance_count
        if instance_count is not None:
            if not isinstance(instance_count, int) or instance_count < 0:
                raise ValueError("InstanceCount must be a non-negative integer")
            # The number of instances can't be increased or decreased by more than 1000 in a single request
            current_count = cr.get("totalInstanceCount", 0)
            diff = abs(instance_count - current_count)
            if diff > 1000:
                raise ValueError("InstanceCount change cannot be more than 1000 in a single request")

        # Allowed modifications depend on state
        # If state is assessing or scheduled, only tags can be modified (tags not in params here)
        state = cr.get("state")
        if state in ("assessing", "scheduled"):
            # No modifications allowed except tags (not handled here)
            # So return success without changes
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Modify capacity reservation attributes
        if accept is not None:
            # Reserved, capacity reservations are accepted by default, ignore
            pass

        if additional_info is not None:
            # Reserved for future use, ignore
            pass

        if end_date_type:
            cr["endDateType"] = end_date_type
        if end_date:
            cr["endDate"] = end_date

        if instance_count is not None:
            cr["totalInstanceCount"] = instance_count
            # Adjust availableInstanceCount accordingly (simplified)
            used = cr.get("usedInstanceCount", 0)
            cr["availableInstanceCount"] = max(instance_count - used, 0)

        if instance_match_criteria:
            cr["instanceMatchCriteria"] = instance_match_criteria

        # Save back to state
        self.state.capacity_reservations[capacity_reservation_id] = cr

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def modify_capacity_reservation_fleet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_reservation_fleet_id = params.get("CapacityReservationFleetId")
        dry_run = params.get("DryRun", False)
        end_date = params.get("EndDate")
        remove_end_date = params.get("RemoveEndDate", False)
        total_target_capacity = params.get("TotalTargetCapacity")

        if not capacity_reservation_fleet_id:
            raise ValueError("CapacityReservationFleetId is required")

        # DryRun check
        if dry_run:
            # Here we assume permission is granted for simplicity
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation",
                "message": "DryRunOperation"
            }

        fleet = self.state.capacity_reservations.get(capacity_reservation_fleet_id)
        if not fleet:
            raise ValueError(f"CapacityReservationFleet {capacity_reservation_fleet_id} not found")

        # Validate mutually exclusive parameters
        if end_date and remove_end_date:
            raise ValueError("Cannot specify both EndDate and RemoveEndDate")

        # Modify end date
        if end_date:
            # Validate end_date format? Assume ISO8601 string or datetime object
            fleet["EndDate"] = end_date
            fleet["State"] = "active"  # Assuming setting end date keeps fleet active
            # Update all individual Capacity Reservations in the fleet
            for cr_id in fleet.get("CapacityReservationIds", []):
                cr = self.state.capacity_reservations.get(cr_id)
                if cr:
                    cr["EndDate"] = end_date
        elif remove_end_date:
            if "EndDate" in fleet:
                del fleet["EndDate"]
            # Update all individual Capacity Reservations in the fleet
            for cr_id in fleet.get("CapacityReservationIds", []):
                cr = self.state.capacity_reservations.get(cr_id)
                if cr and "EndDate" in cr:
                    del cr["EndDate"]

        # Modify total target capacity
        if total_target_capacity is not None:
            if not isinstance(total_target_capacity, int) or total_target_capacity < 0:
                raise ValueError("TotalTargetCapacity must be a non-negative integer")
            fleet["TotalTargetCapacity"] = total_target_capacity
            # Adjust individual Capacity Reservations accordingly
            # For simplicity, assume fleet has a dict of instance types and weights
            # and that total_target_capacity is sum of all reservations
            # Here we do a naive approach: if total_target_capacity > current sum, create new CRs
            # if less, cancel or reduce existing CRs
            current_total = 0
            for cr_id in fleet.get("CapacityReservationIds", []):
                cr = self.state.capacity_reservations.get(cr_id)
                if cr:
                    current_total += cr.get("TotalInstanceCount", 0)
            diff = total_target_capacity - current_total
            if diff > 0:
                # Create new Capacity Reservation(s) to meet new total target capacity
                new_cr_id = self.generate_unique_id()
                new_cr = {
                    "capacityReservationId": new_cr_id,
                    "capacityReservationFleetId": capacity_reservation_fleet_id,
                    "totalInstanceCount": diff,
                    "availableInstanceCount": diff,
                    "state": "active",
                    "createDate": "now",  # placeholder
                    "ownerId": self.get_owner_id(),
                }
                self.state.capacity_reservations[new_cr_id] = new_cr
                fleet.setdefault("CapacityReservationIds", []).append(new_cr_id)
            elif diff < 0:
                # Reduce or cancel existing Capacity Reservations to meet new total target capacity
                # Naive approach: cancel from last CRs until diff is met
                diff = -diff
                cr_ids = fleet.get("CapacityReservationIds", [])
                for cr_id in reversed(cr_ids):
                    cr = self.state.capacity_reservations.get(cr_id)
                    if not cr:
                        continue
                    cr_count = cr.get("totalInstanceCount", 0)
                    if cr_count <= diff:
                        # Cancel entire CR
                        cr["state"] = "cancelled"
                        diff -= cr_count
                    else:
                        # Reduce CR count
                        cr["totalInstanceCount"] = cr_count - diff
                        cr["availableInstanceCount"] = max(0, cr.get("availableInstanceCount", 0) - diff)
                        diff = 0
                    if diff == 0:
                        break

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def modify_instance_capacity_reservation_attributes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_reservation_spec = params.get("CapacityReservationSpecification")
        dry_run = params.get("DryRun", False)
        instance_id = params.get("InstanceId")

        if not capacity_reservation_spec:
            raise ValueError("CapacityReservationSpecification is required")
        if not instance_id:
            raise ValueError("InstanceId is required")

        # DryRun check
        if dry_run:
            # Assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation",
                "message": "DryRunOperation"
            }

        instance = self.state.get_resource(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        # Only stopped instances can be modified
        if instance.get("state", {}).get("Name") != "stopped":
            raise ValueError("Instance must be stopped to modify Capacity Reservation attributes")

        # Validate CapacityReservationPreference
        pref = capacity_reservation_spec.get("CapacityReservationPreference")
        valid_prefs = {"capacity-reservations-only", "open", "none"}
        if pref and pref not in valid_prefs:
            raise ValueError(f"Invalid CapacityReservationPreference: {pref}")

        # Validate CapacityReservationTarget if present
        target = capacity_reservation_spec.get("CapacityReservationTarget")
        if target:
            cr_id = target.get("CapacityReservationId")
            cr_rg_arn = target.get("CapacityReservationResourceGroupArn")
            if cr_id and cr_rg_arn:
                raise ValueError("Cannot specify both CapacityReservationId and CapacityReservationResourceGroupArn")
            if cr_id and cr_id not in self.state.capacity_reservations:
                raise ValueError(f"CapacityReservationId {cr_id} not found")
            # No validation for ResourceGroupArn here

        # Update instance attributes
        instance["CapacityReservationSpecification"] = capacity_reservation_spec

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def move_capacity_reservation_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        destination_id = params.get("DestinationCapacityReservationId")
        dry_run = params.get("DryRun", False)
        instance_count = params.get("InstanceCount")
        source_id = params.get("SourceCapacityReservationId")

        if not destination_id:
            raise ValueError("DestinationCapacityReservationId is required")
        if not instance_count or not isinstance(instance_count, int) or instance_count <= 0:
            raise ValueError("InstanceCount must be a positive integer")
        if not source_id:
            raise ValueError("SourceCapacityReservationId is required")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation",
                "message": "DryRunOperation"
            }

        source_cr = self.state.capacity_reservations.get(source_id)
        if not source_cr:
            raise ValueError(f"Source Capacity Reservation {source_id} not found")
        destination_cr = self.state.capacity_reservations.get(destination_id)
        if not destination_cr:
            raise ValueError(f"Destination Capacity Reservation {destination_id} not found")

        # Both must be active
        if source_cr.get("state") != "active":
            raise ValueError("Source Capacity Reservation must be active")
        if destination_cr.get("state") != "active":
            raise ValueError("Destination Capacity Reservation must be active")

        # Must be owned by same account
        owner_id = self.get_owner_id()
        if source_cr.get("ownerId") != owner_id or destination_cr.get("ownerId") != owner_id:
            raise ValueError("Both Capacity Reservations must be owned by your AWS account")

        # Must share instance type and platform
        if source_cr.get("instanceType") != destination_cr.get("instanceType"):
            raise ValueError("Instance types of source and destination Capacity Reservations must match")
        if source_cr.get("instancePlatform") != destination_cr.get("instancePlatform"):
            raise ValueError("Instance platforms of source and destination Capacity Reservations must match")

        # Check source has enough available capacity
        available_source = source_cr.get("availableInstanceCount", 0)
        if available_source < instance_count:
            raise ValueError("Source Capacity Reservation does not have enough available capacity")

        # Move capacity: reduce source available, increase destination available
        source_cr["availableInstanceCount"] = available_source - instance_count
        destination_cr["availableInstanceCount"] = destination_cr.get("availableInstanceCount", 0) + instance_count

        # Also adjust totalInstanceCount if needed? Usually totalInstanceCount is fixed reservation size
        # We assume only availableInstanceCount changes here

        return {
            "destinationCapacityReservation": destination_cr,
            "instanceCount": instance_count,
            "requestId": self.generate_request_id(),
            "sourceCapacityReservation": source_cr,
        }


    def purchase_capacity_block(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_block_offering_id = params.get("CapacityBlockOfferingId")
        dry_run = params.get("DryRun", False)
        instance_platform = params.get("InstancePlatform")
        tag_specifications = params.get("TagSpecification.N", [])

        if not capacity_block_offering_id:
            raise ValueError("CapacityBlockOfferingId is required")
        if not instance_platform:
            raise ValueError("InstancePlatform is required")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation",
                "message": "DryRunOperation"
            }

        # Create Capacity Block
        capacity_block_id = self.generate_unique_id()
        capacity_block = {
            "capacityBlockId": capacity_block_id,
            "availabilityZone": "us-east-1a",  # Example default
            "availabilityZoneId": "use1-az1",  # Example default
            "capacityReservationIdSet": [],
            "createDate": "now",  # placeholder
            "endDate": None,
            "startDate": "now",  # placeholder
            "state": "active",
            "tagSet": [],
            "ultraserverType": None,
        }

        # Apply tags if any
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and value:
                    capacity_block["tagSet"].append({"Key": key, "Value": value})

        # Store capacity block in state
        self.state.capacity_blocks = getattr(self.state, "capacity_blocks", {})
        self.state.capacity_blocks[capacity_block_id] = capacity_block

        # Create a Capacity Reservation associated with this block
        capacity_reservation_id = self.generate_unique_id()
        capacity_reservation = {
            "capacityReservationId": capacity_reservation_id,
            "capacityBlockId": capacity_block_id,
            "availabilityZone": capacity_block["availabilityZone"],
            "availabilityZoneId": capacity_block["availabilityZoneId"],
            "availableInstanceCount": 0,
            "capacityAllocationSet": [],
            "capacityReservationArn": None,
            "capacityReservationFleetId": None,
            "commitmentInfo": None,
            "createDate": "now",
            "deliveryPreference": None,
            "ebsOptimized": False,
            "endDate": None,
            "endDateType": "unlimited",
            "ephemeralStorage": False,
            "instanceMatchCriteria": "open",
            "instancePlatform": instance_platform,
            "instanceType": None,
            "interruptible": False,
            "interruptibleCapacityAllocation": None,
            "interruptionInfo": None,
            "ownerId": self.get_owner_id(),
            "placementGroupArn": None,
            "reservationType": "capacity-block",
            "startDate": "now",
            "state": "active",
            "tagSet": capacity_block["tagSet"],
            "tenancy": "default",
            "totalInstanceCount": 0,
            "unusedReservationBillingOwnerId": None,
        }
        self.state.capacity_reservations[capacity_reservation_id] = capacity_reservation
        capacity_block["capacityReservationIdSet"].append(capacity_reservation_id)

        return {
            "capacityBlockSet": [capacity_block],
            "capacityReservation": capacity_reservation,
            "requestId": self.generate_request_id(),
        }


    def purchase_capacity_block_extension(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_block_extension_offering_id = params.get("CapacityBlockExtensionOfferingId")
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)

        if not capacity_block_extension_offering_id:
            raise ValueError("CapacityBlockExtensionOfferingId is required")
        if not capacity_reservation_id:
            raise ValueError("CapacityReservationId is required")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation",
                "message": "DryRunOperation"
            }

        capacity_reservation = self.state.capacity_reservations.get(capacity_reservation_id)
        if not capacity_reservation:
            raise ValueError(f"CapacityReservation {capacity_reservation_id} not found")

        # Create Capacity Block Extension
        extension_id = self.generate_unique_id()
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        duration_hours = 24  # Example duration, could be from offering details
        start_date = now.isoformat() + "Z"
        end_date = (now + timedelta(hours=duration_hours)).isoformat() + "Z"

        capacity_block_extension = {
            "capacityBlockExtensionOfferingId": capacity_block_extension_offering_id,
            "capacityReservationId": capacity_reservation_id,
            "capacityBlockExtensionDurationHours": duration_hours,
            "capacityBlockExtensionEndDate": end_date,
            "capacityBlockExtensionPurchaseDate": start_date,
            "capacityBlockExtensionStartDate": start_date,
            "capacityBlockExtensionStatus": "payment-pending",
            "availabilityZone": capacity_reservation.get("availabilityZone"),
            "availabilityZoneId": capacity_reservation.get("availabilityZoneId"),
            "currencyCode": "USD",
            "instanceCount": capacity_reservation.get("totalInstanceCount", 0),
            "instanceType": capacity_reservation.get("instanceType"),
            "upfrontFee": "0.00",
        }

        self.state.capacity_block_extensions = getattr(self.state, "capacity_block_extensions", {})
        self.state.capacity_block_extensions[extension_id] = capacity_block_extension

        return {
            "capacityBlockExtensionSet": [capacity_block_extension],
            "requestId": self.generate_request_id(),
        }

    def reject_capacity_reservation_billing_ownership(self, params: Dict[str, Any]) -> Dict[str, Any]:
        capacity_reservation_id = params.get("CapacityReservationId")
        dry_run = params.get("DryRun", False)

        if not capacity_reservation_id:
            raise Exception("Missing required parameter CapacityReservationId")

        # DryRun check
        if dry_run:
            # Here we simulate permission check; assume always allowed for this emulator
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set."
            }

        capacity_reservation = self.state.capacity_reservations.get(capacity_reservation_id)
        if not capacity_reservation:
            raise Exception(f"CapacityReservationId {capacity_reservation_id} does not exist")

        # Check if there is a pending billing ownership request for this capacity reservation
        # We assume capacity_reservation has a dict or attribute 'billing_ownership_requests' keyed by owner id or a single request
        # Since no structure is given, we assume a single pending request attribute: 'pending_billing_ownership_request' with owner info
        pending_request = getattr(capacity_reservation, "pending_billing_ownership_request", None)
        if not pending_request:
            # No pending request to reject
            raise Exception(f"No pending billing ownership request for CapacityReservationId {capacity_reservation_id}")

        # The current account is rejecting the request, so only if the request is targeted to this account
        if pending_request.get("target_owner_id") != self.get_owner_id():
            raise Exception("No billing ownership request to reject for this account")

        # Reject the request by removing the pending request
        capacity_reservation.pending_billing_ownership_request = None

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class CapacityReservationsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptCapacityReservationBillingOwnership", self.accept_capacity_reservation_billing_ownership)
        self.register_action("AssociateCapacityReservationBillingOwner", self.associate_capacity_reservation_billing_owner)
        self.register_action("CancelCapacityReservation", self.cancel_capacity_reservation)
        self.register_action("CancelCapacityReservationFleets", self.cancel_capacity_reservation_fleets)
        self.register_action("CreateCapacityReservation", self.create_capacity_reservation)
        self.register_action("CreateCapacityReservationBySplitting", self.create_capacity_reservation_by_splitting)
        self.register_action("CreateCapacityReservationFleet", self.create_capacity_reservation_fleet)
        self.register_action("DescribeCapacityBlockExtensionHistory", self.describe_capacity_block_extension_history)
        self.register_action("DescribeCapacityBlockExtensionOfferings", self.describe_capacity_block_extension_offerings)
        self.register_action("DescribeCapacityBlockOfferings", self.describe_capacity_block_offerings)
        self.register_action("DescribeCapacityBlocks", self.describe_capacity_blocks)
        self.register_action("DescribeCapacityBlockStatus", self.describe_capacity_block_status)
        self.register_action("DescribeCapacityReservationBillingRequests", self.describe_capacity_reservation_billing_requests)
        self.register_action("DescribeCapacityReservations", self.describe_capacity_reservations)
        self.register_action("DescribeCapacityReservationFleets", self.describe_capacity_reservation_fleets)
        self.register_action("DescribeMacModificationTasks", self.describe_mac_modification_tasks)
        self.register_action("DisassociateCapacityReservationBillingOwner", self.disassociate_capacity_reservation_billing_owner)
        self.register_action("GetCapacityReservationUsage", self.get_capacity_reservation_usage)
        self.register_action("GetGroupsForCapacityReservation", self.get_groups_for_capacity_reservation)
        self.register_action("ModifyCapacityReservation", self.modify_capacity_reservation)
        self.register_action("ModifyCapacityReservationFleet", self.modify_capacity_reservation_fleet)
        self.register_action("ModifyInstanceCapacityReservationAttributes", self.modify_instance_capacity_reservation_attributes)
        self.register_action("MoveCapacityReservationInstances", self.move_capacity_reservation_instances)
        self.register_action("PurchaseCapacityBlock", self.purchase_capacity_block)
        self.register_action("PurchaseCapacityBlockExtension", self.purchase_capacity_block_extension)
        self.register_action("RejectCapacityReservationBillingOwnership", self.reject_capacity_reservation_billing_ownership)

    def accept_capacity_reservation_billing_ownership(self, params):
        return self.backend.accept_capacity_reservation_billing_ownership(params)

    def associate_capacity_reservation_billing_owner(self, params):
        return self.backend.associate_capacity_reservation_billing_owner(params)

    def cancel_capacity_reservation(self, params):
        return self.backend.cancel_capacity_reservation(params)

    def cancel_capacity_reservation_fleets(self, params):
        return self.backend.cancel_capacity_reservation_fleets(params)

    def create_capacity_reservation(self, params):
        return self.backend.create_capacity_reservation(params)

    def create_capacity_reservation_by_splitting(self, params):
        return self.backend.create_capacity_reservation_by_splitting(params)

    def create_capacity_reservation_fleet(self, params):
        return self.backend.create_capacity_reservation_fleet(params)

    def describe_capacity_block_extension_history(self, params):
        return self.backend.describe_capacity_block_extension_history(params)

    def describe_capacity_block_extension_offerings(self, params):
        return self.backend.describe_capacity_block_extension_offerings(params)

    def describe_capacity_block_offerings(self, params):
        return self.backend.describe_capacity_block_offerings(params)

    def describe_capacity_blocks(self, params):
        return self.backend.describe_capacity_blocks(params)

    def describe_capacity_block_status(self, params):
        return self.backend.describe_capacity_block_status(params)

    def describe_capacity_reservation_billing_requests(self, params):
        return self.backend.describe_capacity_reservation_billing_requests(params)

    def describe_capacity_reservations(self, params):
        return self.backend.describe_capacity_reservations(params)

    def describe_capacity_reservation_fleets(self, params):
        return self.backend.describe_capacity_reservation_fleets(params)

    def describe_mac_modification_tasks(self, params):
        return self.backend.describe_mac_modification_tasks(params)

    def disassociate_capacity_reservation_billing_owner(self, params):
        return self.backend.disassociate_capacity_reservation_billing_owner(params)

    def get_capacity_reservation_usage(self, params):
        return self.backend.get_capacity_reservation_usage(params)

    def get_groups_for_capacity_reservation(self, params):
        return self.backend.get_groups_for_capacity_reservation(params)

    def modify_capacity_reservation(self, params):
        return self.backend.modify_capacity_reservation(params)

    def modify_capacity_reservation_fleet(self, params):
        return self.backend.modify_capacity_reservation_fleet(params)

    def modify_instance_capacity_reservation_attributes(self, params):
        return self.backend.modify_instance_capacity_reservation_attributes(params)

    def move_capacity_reservation_instances(self, params):
        return self.backend.move_capacity_reservation_instances(params)

    def purchase_capacity_block(self, params):
        return self.backend.purchase_capacity_block(params)

    def purchase_capacity_block_extension(self, params):
        return self.backend.purchase_capacity_block_extension(params)

    def reject_capacity_reservation_billing_ownership(self, params):
        return self.backend.reject_capacity_reservation_billing_ownership(params)
