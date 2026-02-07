from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend


class InstanceCountState(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    CANCELLED = "cancelled"
    PENDING = "pending"


class ReservedInstancesListingStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class InstanceTenancy(str, Enum):
    DEFAULT = "default"
    DEDICATED = "dedicated"
    HOST = "host"


class OfferingClass(str, Enum):
    STANDARD = "standard"
    CONVERTIBLE = "convertible"


class OfferingType(str, Enum):
    HEAVY_UTILIZATION = "Heavy Utilization"
    MEDIUM_UTILIZATION = "Medium Utilization"
    LIGHT_UTILIZATION = "Light Utilization"
    NO_UPFRONT = "No Upfront"
    PARTIAL_UPFRONT = "Partial Upfront"
    ALL_UPFRONT = "All Upfront"


class ReservedInstanceState(str, Enum):
    PAYMENT_PENDING = "payment-pending"
    ACTIVE = "active"
    PAYMENT_FAILED = "payment-failed"
    RETIRED = "retired"
    QUEUED = "queued"
    QUEUED_DELETED = "queued-deleted"


class ReservedInstanceModificationStatus(str, Enum):
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    FAILED = "failed"


class RecurringChargeFrequency(str, Enum):
    HOURLY = "Hourly"


class Scope(str, Enum):
    AVAILABILITY_ZONE = "Availability Zone"
    REGION = "Region"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class InstanceCount:
    instance_count: Optional[int] = None
    state: Optional[InstanceCountState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "InstanceCount": self.instance_count,
            "State": self.state.value if self.state else None,
        }


@dataclass
class PriceSchedule:
    active: Optional[bool] = None
    currency_code: Optional[str] = None  # Only USD supported
    price: Optional[float] = None
    term: Optional[int] = None  # months remaining

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Active": self.active,
            "CurrencyCode": self.currency_code,
            "Price": self.price,
            "Term": self.term,
        }


@dataclass
class ReservedInstancesListing:
    client_token: Optional[str] = None
    create_date: Optional[datetime] = None
    instance_counts: List[InstanceCount] = field(default_factory=list)
    price_schedules: List[PriceSchedule] = field(default_factory=list)
    reserved_instances_id: Optional[str] = None
    reserved_instances_listing_id: Optional[str] = None
    status: Optional[ReservedInstancesListingStatus] = None
    status_message: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    update_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ClientToken": self.client_token,
            "CreateDate": self.create_date.isoformat() if self.create_date else None,
            "InstanceCounts": [ic.to_dict() for ic in self.instance_counts],
            "PriceSchedules": [ps.to_dict() for ps in self.price_schedules],
            "ReservedInstancesId": self.reserved_instances_id,
            "ReservedInstancesListingId": self.reserved_instances_listing_id,
            "Status": self.status.value if self.status else None,
            "StatusMessage": self.status_message,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "UpdateDate": self.update_date.isoformat() if self.update_date else None,
        }


@dataclass
class PriceScheduleSpecification:
    currency_code: Optional[str] = None  # Only USD supported
    price: Optional[float] = None
    term: Optional[int] = None  # months remaining

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CurrencyCode": self.currency_code,
            "Price": self.price,
            "Term": self.term,
        }


@dataclass
class ReservedInstanceLimitPrice:
    Amount: Optional[float] = None
    CurrencyCode: Optional[str] = None  # Only USD supported

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Amount": self.Amount,
            "CurrencyCode": self.CurrencyCode,
        }


@dataclass
class RecurringCharge:
    amount: Optional[float] = None
    frequency: Optional[RecurringChargeFrequency] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Amount": self.amount,
            "Frequency": self.frequency.value if self.frequency else None,
        }


@dataclass
class PricingDetail:
    count: Optional[int] = None
    price: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Count": self.count,
            "Price": self.price,
        }


@dataclass
class ReservedInstancesOffering:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    currency_code: Optional[str] = None  # Only USD supported
    duration: Optional[int] = None  # seconds
    fixed_price: Optional[float] = None
    instance_tenancy: Optional[InstanceTenancy] = None
    instance_type: Optional[str] = None
    marketplace: Optional[bool] = None
    offering_class: Optional[OfferingClass] = None
    offering_type: Optional[OfferingType] = None
    pricing_details_set: List[PricingDetail] = field(default_factory=list)
    product_description: Optional[str] = None
    recurring_charges: List[RecurringCharge] = field(default_factory=list)
    reserved_instances_offering_id: Optional[str] = None
    scope: Optional[Scope] = None
    usage_price: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.availability_zone,
            "AvailabilityZoneId": self.availability_zone_id,
            "CurrencyCode": self.currency_code,
            "Duration": self.duration,
            "FixedPrice": self.fixed_price,
            "InstanceTenancy": self.instance_tenancy.value if self.instance_tenancy else None,
            "InstanceType": self.instance_type,
            "Marketplace": self.marketplace,
            "OfferingClass": self.offering_class.value if self.offering_class else None,
            "OfferingType": self.offering_type.value if self.offering_type else None,
            "PricingDetailsSet": [pd.to_dict() for pd in self.pricing_details_set],
            "ProductDescription": self.product_description,
            "RecurringCharges": [rc.to_dict() for rc in self.recurring_charges],
            "ReservedInstancesOfferingId": self.reserved_instances_offering_id,
            "Scope": self.scope.value if self.scope else None,
            "UsagePrice": self.usage_price,
        }


@dataclass
class ReservationValue:
    hourly_price: Optional[str] = None
    remaining_total_value: Optional[str] = None
    remaining_upfront_value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "HourlyPrice": self.hourly_price,
            "RemainingTotalValue": self.remaining_total_value,
            "RemainingUpfrontValue": self.remaining_upfront_value,
        }


@dataclass
class TargetConfiguration:
    instance_count: Optional[int] = None
    offering_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "InstanceCount": self.instance_count,
            "OfferingId": self.offering_id,
        }


@dataclass
class ReservedInstanceReservationValue:
    reservation_value: Optional[ReservationValue] = None
    reserved_instance_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ReservationValue": self.reservation_value.to_dict() if self.reservation_value else None,
            "ReservedInstanceId": self.reserved_instance_id,
        }


@dataclass
class TargetReservationValue:
    reservation_value: Optional[ReservationValue] = None
    target_configuration: Optional[TargetConfiguration] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ReservationValue": self.reservation_value.to_dict() if self.reservation_value else None,
            "TargetConfiguration": self.target_configuration.to_dict() if self.target_configuration else None,
        }


@dataclass
class ReservedInstancesConfiguration:
    AvailabilityZone: Optional[str] = None
    AvailabilityZoneId: Optional[str] = None
    InstanceCount: Optional[int] = None
    InstanceType: Optional[str] = None
    Platform: Optional[str] = None
    Scope: Optional[Scope] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.AvailabilityZone,
            "AvailabilityZoneId": self.AvailabilityZoneId,
            "InstanceCount": self.InstanceCount,
            "InstanceType": self.InstanceType,
            "Platform": self.Platform,
            "Scope": self.Scope.value if self.Scope else None,
        }


@dataclass
class ReservedInstancesModificationResult:
    reserved_instances_id: Optional[str] = None
    target_configuration: Optional[ReservedInstancesConfiguration] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ReservedInstancesId": self.reserved_instances_id,
            "TargetConfiguration": self.target_configuration.to_dict() if self.target_configuration else None,
        }


@dataclass
class ReservedInstancesModification:
    client_token: Optional[str] = None
    create_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    modification_result_set: List[ReservedInstancesModificationResult] = field(default_factory=list)
    reserved_instances_modification_id: Optional[str] = None
    reserved_instances_set: List[str] = field(default_factory=list)  # List of ReservedInstancesId strings
    status: Optional[ReservedInstanceModificationStatus] = None
    status_message: Optional[str] = None
    update_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ClientToken": self.client_token,
            "CreateDate": self.create_date.isoformat() if self.create_date else None,
            "EffectiveDate": self.effective_date.isoformat() if self.effective_date else None,
            "ModificationResultSet": [mr.to_dict() for mr in self.modification_result_set],
            "ReservedInstancesModificationId": self.reserved_instances_modification_id,
            "ReservedInstancesSet": self.reserved_instances_set,
            "Status": self.status.value if self.status else None,
            "StatusMessage": self.status_message,
            "UpdateDate": self.update_date.isoformat() if self.update_date else None,
        }


@dataclass
class FailedQueuedPurchaseDeletionError:
    code: Optional[str] = None  # reserved-instances-id-invalid | reserved-instances-not-in-queued-state | unexpected-error
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Code": self.code,
            "Message": self.message,
        }


@dataclass
class FailedQueuedPurchaseDeletion:
    error: Optional[FailedQueuedPurchaseDeletionError] = None
    reserved_instances_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Error": self.error.to_dict() if self.error else None,
            "ReservedInstancesId": self.reserved_instances_id,
        }


@dataclass
class SuccessfulQueuedPurchaseDeletion:
    reserved_instances_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ReservedInstancesId": self.reserved_instances_id,
        }


@dataclass
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Values": self.Values,
        }


class ReservedInstancesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for shared resources

    def accept_reserved_instances_exchange_quote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter ReservedInstanceId.N
        reserved_instance_ids = []
        for key, value in params.items():
            if key.startswith("ReservedInstanceId."):
                reserved_instance_ids.append(value)
        if not reserved_instance_ids:
            raise ValueError("Missing required parameter ReservedInstanceId.N")

        # TargetConfiguration.N is optional
        target_configurations = []
        for key, value in params.items():
            if key.startswith("TargetConfiguration."):
                # Extract index and field name
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                index = parts[1]
                field = parts[2]
                # Find or create target configuration dict for this index
                while len(target_configurations) < int(index):
                    target_configurations.append({})
                target_configurations[int(index) - 1][field] = value

        # Validate TargetConfiguration fields
        target_config_objs = []
        for tc in target_configurations:
            offering_id = tc.get("OfferingId")
            if not offering_id:
                raise ValueError("OfferingId is required in TargetConfiguration")
            instance_count = tc.get("InstanceCount")
            if instance_count is not None:
                try:
                    instance_count = int(instance_count)
                except Exception:
                    raise ValueError("InstanceCount must be an integer in TargetConfiguration")
            target_config_objs.append(TargetConfiguration(instance_count=instance_count, offering_id=offering_id))

        # For this emulator, we simulate accepting the exchange quote by generating an exchangeId
        exchange_id = self.generate_unique_id()

        return {
            "exchangeId": exchange_id,
            "requestId": self.generate_request_id(),
        }


    def cancel_reserved_instances_listing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        reserved_instances_listing_id = params.get("ReservedInstancesListingId")
        if not reserved_instances_listing_id:
            raise ValueError("Missing required parameter ReservedInstancesListingId")

        listing = self.state.reserved_instances_listings.get(reserved_instances_listing_id)
        if not listing:
            # If listing not found, return empty set with requestId
            return {
                "requestId": self.generate_request_id(),
                "reservedInstancesListingsSet": [],
            }

        # Update status to cancelled and status message
        listing.status = ReservedInstancesListingStatus.CANCELLED if hasattr(ReservedInstancesListingStatus, "CANCELLED") else "cancelled"
        listing.status_message = "CANCELLED"
        listing.update_date = datetime.utcnow()

        # Update instance counts to reflect cancellation: set Cancelled count to total instance count, others to 0
        total_instances = 0
        for ic in listing.instance_counts:
            if ic.instance_count:
                total_instances += ic.instance_count
        # Reset all counts to 0
        for ic in listing.instance_counts:
            ic.instance_count = 0
        # Set Cancelled count to total_instances
        # Find instance count with state Cancelled or cancelled (case insensitive)
        cancelled_state_found = False
        for ic in listing.instance_counts:
            if str(ic.state).lower() == "cancelled":
                ic.instance_count = total_instances
                cancelled_state_found = True
                break
        if not cancelled_state_found:
            # If no Cancelled state found, add one
            listing.instance_counts.append(InstanceCount(instance_count=total_instances, state=InstanceCountState.CANCELLED if hasattr(InstanceCountState, "CANCELLED") else "Cancelled"))

        return {
            "requestId": self.generate_request_id(),
            "reservedInstancesListingsSet": [listing.to_dict()],
        }


    def create_reserved_instances_listing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        if not client_token:
            raise ValueError("Missing required parameter ClientToken")

        instance_count = params.get("InstanceCount")
        if instance_count is None:
            raise ValueError("Missing required parameter InstanceCount")
        try:
            instance_count = int(instance_count)
            if instance_count <= 0:
                raise ValueError("InstanceCount must be positive")
        except Exception:
            raise ValueError("InstanceCount must be an integer")

        reserved_instances_id = params.get("ReservedInstancesId")
        if not reserved_instances_id:
            raise ValueError("Missing required parameter ReservedInstancesId")

        # Validate PriceSchedules.N
        price_schedules = []
        # Collect all PriceSchedules.N.* keys
        price_schedule_dict = {}
        for key, value in params.items():
            if key.startswith("PriceSchedules."):
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                index = parts[1]
                field = parts[2]
                if index not in price_schedule_dict:
                    price_schedule_dict[index] = {}
                price_schedule_dict[index][field] = value

        if not price_schedule_dict:
            raise ValueError("Missing required parameter PriceSchedules.N")

        # Convert to PriceScheduleSpecification objects
        for index in sorted(price_schedule_dict.keys(), key=lambda x: int(x)):
            ps = price_schedule_dict[index]
            currency_code = ps.get("CurrencyCode", "USD")
            price = ps.get("Price")
            term = ps.get("Term")
            if price is None or term is None:
                raise ValueError("Price and Term are required in PriceSchedules")
            try:
                price = float(price)
            except Exception:
                raise ValueError("Price must be a float in PriceSchedules")
            try:
                term = int(term)
            except Exception:
                raise ValueError("Term must be an integer in PriceSchedules")
            price_schedules.append(PriceScheduleSpecification(currency_code=currency_code, price=price, term=term))

        # Create ReservedInstancesListing object
        reserved_instances_listing_id = self.generate_unique_id()
        now = datetime.utcnow()

        # Create instance counts for states: Available, Sold, Cancelled, Pending
        instance_counts = [
            InstanceCount(instance_count=instance_count, state=InstanceCountState.AVAILABLE if hasattr(InstanceCountState, "AVAILABLE") else "Available"),
            InstanceCount(instance_count=0, state=InstanceCountState.SOLD if hasattr(InstanceCountState, "SOLD") else "Sold"),
            InstanceCount(instance_count=0, state=InstanceCountState.CANCELLED if hasattr(InstanceCountState, "CANCELLED") else "Cancelled"),
            InstanceCount(instance_count=0, state=InstanceCountState.PENDING if hasattr(InstanceCountState, "PENDING") else "Pending"),
        ]

        # Create PriceSchedule objects for the listing, with active flag
        # The active price schedule is the one with the highest term (max term)
        max_term = max(ps.term for ps in price_schedules)
        price_schedules_listing = []
        # We create price schedules for all months from max_term down to 1
        # For each month, find the price schedule with the highest term >= month
        for month in range(max_term, 0, -1):
            # Find price schedule with highest term >= month
            applicable_ps = None
            for ps in sorted(price_schedules, key=lambda x: x.term, reverse=True):
                if ps.term >= month:
                    applicable_ps = ps
                    break
            if not applicable_ps:
                # If none found, skip
                continue
            active = (month == max_term)
            price_schedules_listing.append(
                PriceSchedule(
                    active=active,
                    currency_code=applicable_ps.currency_code,
                    price=applicable_ps.price,
                    term=month,
                )
            )

        listing = ReservedInstancesListing(
            client_token=client_token,
            create_date=now,
            instance_counts=instance_counts,
            price_schedules=price_schedules_listing,
            reserved_instances_id=reserved_instances_id,
            reserved_instances_listing_id=reserved_instances_listing_id,
            status=ReservedInstancesListingStatus.ACTIVE if hasattr(ReservedInstancesListingStatus, "ACTIVE") else "active",
            status_message="ACTIVE",
            tag_set=[],
            update_date=now,
        )

        # Store the listing in state
        if not hasattr(self.state, "reserved_instances_listings"):
            self.state.reserved_instances_listings = {}
        self.state.reserved_instances_listings[reserved_instances_listing_id] = listing

        return {
            "requestId": self.generate_request_id(),
            "reservedInstancesListingsSet": [listing.to_dict()],
        }


    def delete_queued_reserved_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter ReservedInstancesId.N
        reserved_instance_ids = []
        for key, value in params.items():
            if key.startswith("ReservedInstancesId."):
                reserved_instance_ids.append(value)
        if not reserved_instance_ids:
            raise ValueError("Missing required parameter ReservedInstancesId.N")

        failed_deletions = []
        successful_deletions = []

        for rid in reserved_instance_ids:
            reserved_instance = self.state.reserved_instances.get(rid)
            if not reserved_instance:
                error = FailedQueuedPurchaseDeletionError(
                    code="reserved-instances-id-invalid",
                    message=f"Reserved Instance ID {rid} is invalid",
                )
                failed_deletions.append(FailedQueuedPurchaseDeletion(error=error, reserved_instances_id=rid))
                continue

            # Check if state is queued or queued-deleted
            if reserved_instance.state not in [ReservedInstanceState.QUEUED if hasattr(ReservedInstanceState, "QUEUED") else "queued",
                                               ReservedInstanceState.QUEUED_DELETED if hasattr(ReservedInstanceState, "QUEUED_DELETED") else "queued-deleted"]:
                error = FailedQueuedPurchaseDeletionError(
                    code="reserved-instances-not-in-queued-state",
                    message=f"Reserved Instance ID {rid} is not in queued state",
                )
                failed_deletions.append(FailedQueuedPurchaseDeletion(error=error, reserved_instances_id=rid))
                continue

            # Delete the queued purchase (simulate by removing from state)
            del self.state.reserved_instances[rid]
            successful_deletions.append(SuccessfulQueuedPurchaseDeletion(reserved_instances_id=rid))

        return {
            "failedQueuedPurchaseDeletionSet": [fd.to_dict() for fd in failed_deletions],
            "requestId": self.generate_request_id(),
            "successfulQueuedPurchaseDeletionSet": [sd.to_dict() for sd in successful_deletions],
        }


    def describe_reserved_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Optional filters
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    index = parts[1]
                    field = parts[2]
                    # Find or create filter dict for this index
                    while len(filters) < int(index):
                        filters.append(Filter(Name=None, Values=[]))
                    if field == "Name":
                        filters[int(index) - 1].Name = value
                    elif field.startswith("Value"):
                        filters[int(index) - 1].Values.append(value)

        offering_class = params.get("OfferingClass")
        offering_type = params.get("OfferingType")

        reserved_instances_ids = []
        for key, value in params.items():
            if key.startswith("ReservedInstancesId."):
                reserved_instances_ids.append(value)

        # Collect all reserved instances from state
        all_reserved_instances = list(self.state.reserved_instances.values())

        # Filter by ReservedInstancesId if specified
        if reserved_instances_ids:
            all_reserved_instances = [ri for ri in all_reserved_instances if ri.reserved_instances_id in reserved_instances_ids]

        # Filter by OfferingClass if specified
        if offering_class:
            all_reserved_instances = [ri for ri in all_reserved_instances if ri.offering_class and str(ri.offering_class).lower() == offering_class.lower()]

        # Filter by OfferingType if specified
        if offering_type:
            all_reserved_instances = [ri for ri in all_reserved_instances if ri.offering_type and str(ri.offering_type).lower() == offering_type.lower()]

        # Apply filters
        def matches_filter(ri: "ReservedInstances", flt: Filter) -> bool:
            if not flt.Name or not flt.Values:
                return True
            name = flt.Name.lower()
            values = [v.lower() for v in flt.Values]
            # Map filter names to ReservedInstances attributes
            if name == "availability-zone":
                return ri.availability_zone and ri.availability_zone.lower() in values
            if name == "availability-zone-id":
                return ri.availability_zone_id and ri.availability_zone_id.lower() in values
            if name == "duration":
                return ri.duration and str(ri.duration) in values
            if name == "end":
                # Compare ISO format string
                return ri.end and ri.end.isoformat() in values
            if name == "fixed-price":
                return ri.fixed_price and str(ri.fixed_price) in values
            if name == "instance-type":
                return ri.instance_type and ri.instance_type.lower() in values
            if name == "scope":
                return ri.scope and str(ri.scope).lower() in values
            if name == "product-description":
                return ri.product_description and ri.product_description.lower() in values
            if name == "reserved-instances-id":
                return ri.reserved_instances_id and ri.reserved_instances_id.lower() in values
            if name == "start":
                return ri.start and ri.start.isoformat() in values
            if name == "state":
                return ri.state and str(ri.state).lower() in values
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in ri.tag_set:
                    if tag.Key.lower() == tag_key and tag.Value.lower() in values:
                        return True
                return False
            if name == "tag-key":
                for tag in ri.tag_set:
                    if tag.Key.lower() in values:
                        return True
                return False
            if name == "usage-price":
                return ri.usage_price and str(ri.usage_price) in values
            return True

        filtered_reserved_instances = []
        for ri in all_reserved_instances:
            if all(matches_filter(ri, flt) for flt in filters):
                filtered_reserved_instances.append(ri)

        return {
            "requestId": self.generate_request_id(),
            "reservedInstancesSet": [ri.to_dict() for ri in filtered_reserved_instances],
        }

    def describe_reserved_instances_listings(self, params: dict) -> dict:
        """
        Describes your account's Reserved Instance listings in the Reserved Instance Marketplace.
        Supports filtering by reserved-instances-id, reserved-instances-listing-id, status, and status-message.
        """
        # Extract filters and parameters
        filters = params.get("Filter", [])
        reserved_instances_id = params.get("ReservedInstancesId")
        reserved_instances_listing_id = params.get("ReservedInstancesListingId")

        # Normalize filters: list of Filter objects or dicts with Name and Values
        # Convert filters to dict for easier matching
        filter_dict = {}
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if name:
                filter_dict[name] = values

        # Prepare result list
        listings = list(self.state.reserved_instances_listings.values()) if hasattr(self.state, "reserved_instances_listings") else []

        # Filter by ReservedInstancesId param if provided
        if reserved_instances_id:
            listings = [l for l in listings if l.reserved_instances_id == reserved_instances_id]

        # Filter by ReservedInstancesListingId param if provided
        if reserved_instances_listing_id:
            listings = [l for l in listings if l.reserved_instances_listing_id == reserved_instances_listing_id]

        # Apply filters
        def matches_filter(listing):
            for name, values in filter_dict.items():
                if name == "reserved-instances-id":
                    if listing.reserved_instances_id not in values:
                        return False
                elif name == "reserved-instances-listing-id":
                    if listing.reserved_instances_listing_id not in values:
                        return False
                elif name == "status":
                    # status is enum, convert to string for comparison
                    if listing.status is None or listing.status.value not in values:
                        return False
                elif name == "status-message":
                    # status_message can be None or string
                    if listing.status_message not in values:
                        return False
                else:
                    # Unknown filter, ignore or reject? AWS ignores unknown filters, so ignore
                    pass
            return True

        listings = [l for l in listings if matches_filter(l)]

        # Build response dict
        response = {
            "requestId": self.generate_request_id(),
            "reservedInstancesListingsSet": [listing.to_dict() for listing in listings],
        }
        return response


    def describe_reserved_instances_modifications(self, params: dict) -> dict:
        """
        Describes the modifications made to your Reserved Instances.
        Supports filtering by multiple filters, NextToken, and ReservedInstancesModificationId.N.
        """
        filters = params.get("Filter", [])
        next_token = params.get("NextToken")
        modification_ids = params.get("ReservedInstancesModificationId", [])

        # Normalize filters to dict of name -> set(values)
        filter_dict = {}
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if name:
                filter_dict[name] = set(values)

        # Get all modifications from state
        modifications = list(self.state.reserved_instances_modifications.values()) if hasattr(self.state, "reserved_instances_modifications") else []

        # Filter by modification IDs if provided
        if modification_ids:
            modifications = [m for m in modifications if m.reserved_instances_modification_id in modification_ids]

        # Helper to check if a modification matches filters
        def matches_filter(mod):
            for name, values in filter_dict.items():
                # Map filter names to attributes or nested attributes
                if name == "client-token":
                    if mod.client_token not in values:
                        return False
                elif name == "create-date":
                    # Filter by create_date string or datetime? Assume string in ISO8601
                    if mod.create_date is None or mod.create_date.isoformat() not in values:
                        return False
                elif name == "effective-date":
                    if mod.effective_date is None or mod.effective_date.isoformat() not in values:
                        return False
                elif name == "modification-result.reserved-instances-id":
                    # Check if any modification_result_set has reserved_instances_id in values
                    if not any(r.reserved_instances_id in values for r in mod.modification_result_set):
                        return False
                elif name == "modification-result.target-configuration.availability-zone":
                    if not any(r.target_configuration and r.target_configuration.AvailabilityZone in values for r in mod.modification_result_set):
                        return False
                elif name == "modification-result.target-configuration.availability-zone-id":
                    if not any(r.target_configuration and r.target_configuration.AvailabilityZoneId in values for r in mod.modification_result_set):
                        return False
                elif name == "modification-result.target-configuration.instance-count":
                    if not any(r.target_configuration and r.target_configuration.InstanceCount is not None and str(r.target_configuration.InstanceCount) in values for r in mod.modification_result_set):
                        return False
                elif name == "modification-result.target-configuration.instance-type":
                    if not any(r.target_configuration and r.target_configuration.InstanceType in values for r in mod.modification_result_set):
                        return False
                elif name == "reserved-instances-id":
                    # Check if any reserved_instances_set contains reserved_instances_id in values
                    if not any(rid in values for rid in mod.reserved_instances_set):
                        return False
                elif name == "reserved-instances-modification-id":
                    if mod.reserved_instances_modification_id not in values:
                        return False
                elif name == "status":
                    if mod.status is None or mod.status.value not in values:
                        return False
                elif name == "status-message":
                    if mod.status_message not in values:
                        return False
                elif name == "update-date":
                    if mod.update_date is None or mod.update_date.isoformat() not in values:
                        return False
                else:
                    # Unknown filter, ignore
                    pass
            return True

        modifications = [m for m in modifications if matches_filter(m)]

        # Pagination support: AWS uses NextToken for pagination, but no details on token format here.
        # For simplicity, ignore pagination or implement basic pagination if NextToken is provided.
        # Since no details, we return all results and nextToken as None.
        response = {
            "requestId": self.generate_request_id(),
            "reservedInstancesModificationsSet": [m.to_dict() for m in modifications],
            "nextToken": None,
        }
        return response


    def describe_reserved_instances_offerings(self, params: dict) -> dict:
        """
        Describes Reserved Instance offerings that are available for purchase.
        Supports filtering by many parameters and filters.
        Supports pagination with MaxResults and NextToken.
        """
        # Extract parameters
        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter", [])
        include_marketplace = params.get("IncludeMarketplace")
        instance_tenancy = params.get("InstanceTenancy")
        instance_type = params.get("InstanceType")
        max_duration = params.get("MaxDuration")
        max_instance_count = params.get("MaxInstanceCount")
        max_results = params.get("MaxResults", 100)
        min_duration = params.get("MinDuration")
        next_token = params.get("NextToken")
        offering_class = params.get("OfferingClass")
        offering_type = params.get("OfferingType")
        product_description = params.get("ProductDescription")
        reserved_instances_offering_ids = params.get("ReservedInstancesOfferingId", [])

        # Normalize filters to dict of name -> set(values)
        filter_dict = {}
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if name:
                filter_dict[name] = set(values)

        # Get all offerings from state
        offerings = list(self.state.reserved_instances_offerings.values()) if hasattr(self.state, "reserved_instances_offerings") else []

        # Filter by ReservedInstancesOfferingId param if provided
        if reserved_instances_offering_ids:
            offerings = [o for o in offerings if o.reserved_instances_offering_id in reserved_instances_offering_ids]

        # Filter by AvailabilityZone or AvailabilityZoneId (mutually exclusive)
        if availability_zone and availability_zone_id:
            # AWS returns error if both specified, but here just filter by none (empty)
            offerings = []
        elif availability_zone:
            offerings = [o for o in offerings if o.availability_zone == availability_zone]
        elif availability_zone_id:
            offerings = [o for o in offerings if o.availability_zone_id == availability_zone_id]

        # Filter by InstanceTenancy if provided
        if instance_tenancy:
            offerings = [o for o in offerings if o.instance_tenancy and o.instance_tenancy.value == instance_tenancy]

        # Filter by InstanceType if provided
        if instance_type:
            offerings = [o for o in offerings if o.instance_type == instance_type]

        # Filter by OfferingClass if provided
        if offering_class:
            offerings = [o for o in offerings if o.offering_class and o.offering_class.value == offering_class]

        # Filter by OfferingType if provided
        if offering_type:
            offerings = [o for o in offerings if o.offering_type and o.offering_type.value == offering_type]

        # Filter by ProductDescription if provided
        if product_description:
            offerings = [o for o in offerings if o.product_description == product_description]

        # Filter by IncludeMarketplace param if provided
        if include_marketplace is not None:
            # include_marketplace is boolean, filter offerings.marketplace accordingly
            offerings = [o for o in offerings if (o.marketplace is True) == include_marketplace]

        # Filter by MinDuration and MaxDuration if provided
        if min_duration is not None:
            offerings = [o for o in offerings if o.duration is not None and o.duration >= min_duration]
        if max_duration is not None:
            offerings = [o for o in offerings if o.duration is not None and o.duration <= max_duration]

        # Filter by MaxInstanceCount if provided
        # Note: ReservedInstancesOffering does not have instance count attribute directly,
        # so this filter might be ignored or implemented if pricing_details_set count is used.
        if max_instance_count is not None:
            # Filter offerings where sum of pricing_details_set counts <= max_instance_count
            def total_instance_count(o):
                return sum(pd.count or 0 for pd in o.pricing_details_set)
            offerings = [o for o in offerings if total_instance_count(o) <= max_instance_count]

        # Apply filters from Filter param
        def matches_filter(offer):
            for name, values in filter_dict.items():
                if name == "availability-zone":
                    if offer.availability_zone not in values:
                        return False
                elif name == "availability-zone-id":
                    if offer.availability_zone_id not in values:
                        return False
                elif name == "duration":
                    if offer.duration is None or str(offer.duration) not in values:
                        return False
                elif name == "fixed-price":
                    if offer.fixed_price is None or str(offer.fixed_price) not in values:
                        return False
                elif name == "instance-type":
                    if offer.instance_type not in values:
                        return False
                elif name == "marketplace":
                    # marketplace is boolean, values are strings "true"/"false"
                    val_str = "true" if offer.marketplace else "false"
                    if val_str not in values:
                        return False
                elif name == "product-description":
                    if offer.product_description not in values:
                        return False
                elif name == "reserved-instances-offering-id":
                    if offer.reserved_instances_offering_id not in values:
                        return False
                elif name == "scope":
                    if offer.scope is None or offer.scope.value not in values:
                        return False
                elif name == "usage-price":
                    if offer.usage_price is None or str(offer.usage_price) not in values:
                        return False
                else:
                    # Unknown filter, ignore
                    pass
            return True

        offerings = [o for o in offerings if matches_filter(o)]

        # Pagination: implement simple pagination using NextToken and MaxResults
        # For simplicity, NextToken is an integer offset encoded as string
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results = min(max_results, 100) if max_results else 100

        paged_offerings = offerings[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(offerings):
            new_next_token = str(start_index + max_results)

        response = {
            "requestId": self.generate_request_id(),
            "reservedInstancesOfferingsSet": [o.to_dict() for o in paged_offerings],
            "nextToken": new_next_token,
        }
        return response


    def get_reserved_instances_exchange_quote(self, params: dict) -> dict:
        """
        Returns a quote and exchange information for exchanging one or more specified Convertible Reserved Instances
        for a new Convertible Reserved Instance.
        """
        # Validate required parameter
        reserved_instance_ids = params.get("ReservedInstanceId")
        if not reserved_instance_ids or not isinstance(reserved_instance_ids, list) or len(reserved_instance_ids) == 0:
            raise ValueError("ReservedInstanceId.N is required and must be a non-empty list")

        target_configurations = params.get("TargetConfiguration", [])

        # Retrieve the Convertible Reserved Instances to exchange
        reserved_instances = []
        for rid in reserved_instance_ids:
            ri = self.state.reserved_instances.get(rid)
            if ri is None:
                raise ValueError(f"ReservedInstanceId {rid} not found")
            # Check if Convertible Reserved Instance (offering_class == convertible)
            if ri.offering_class != OfferingClass.CONVERTIBLE:
                raise ValueError(f"ReservedInstanceId {rid} is not Convertible")
            reserved_instances.append(ri)

        # Calculate total value of input reserved instances
        def calc_reservation_value(ri):
            # For simplicity, sum fixed_price and usage_price * duration (hours)
            # AWS uses more complex pricing, here simplified
            upfront = ri.fixed_price or 0.0
            hourly = ri.usage_price or 0.0
            duration_hours = (ri.duration or 0) / 3600
            total = upfront + hourly * duration_hours
            return total

        total_input_value = sum(calc_reservation_value(ri) for ri in reserved_instances)

        # Calculate total value of target configurations
        # For each target configuration, find offering by OfferingId
        target_value = 0.0
        target_value_rollup = ReservationValue(hourlyPrice="0", remainingTotalValue="0", remainingUpfrontValue="0")
        target_value_set = []
        for tc in target_configurations:
            offering_id = tc.get("OfferingId")
            instance_count = tc.get("InstanceCount", 1)
            offering = self.state.reserved_instances_offerings.get(offering_id)
            if offering is None:
                raise ValueError(f"OfferingId {offering_id} not found")
            # Calculate value for this target configuration
            upfront = offering.fixed_price or 0.0
            hourly = offering.usage_price or 0.0
            duration_hours = (offering.duration or 0) / 3600
            total = upfront + hourly * duration_hours
            total *= instance_count
            target_value += total
            # Compose TargetReservationValue object
            reservation_value = ReservationValue(
                hourlyPrice=str(hourly),
                remainingTotalValue=str(total),
                remainingUpfrontValue=str(upfront),
            )
            target_config_obj = TargetConfiguration(
                instance_count=instance_count,
                offering_id=offering_id,
            )
            target_value_set.append(TargetReservationValue(
                reservation_value=reservation_value,
                target_configuration=target_config_obj,
            ))

        # Compose reservedInstanceValueSet for input reserved instances
        reserved_instance_value_set = []
        for ri in reserved_instances:
            upfront = ri.fixed_price or 0.0
            hourly = ri.usage_price or 0.0
            duration_hours = (ri.duration or 0) / 3600
            total = upfront + hourly * duration_hours
            reservation_value = ReservationValue(
                hourlyPrice=str(hourly),
                remainingTotalValue=str(total),
                remainingUpfrontValue=str(upfront),
            )
            reserved_instance_value_set.append(ReservedInstanceReservationValue(
                reservation_value=reservation_value,
                reserved_instance_id=ri.reserved_instances_id,
            ))

        # Determine if exchange is valid: target_value >= total_input_value
        is_valid_exchange = target_value >= total_input_value

        # Calculate payment due: target_value - total_input_value
        payment_due = target_value - total_input_value

        # Compose reservation value rollups
        reserved_instance_value_rollup = ReservationValue(
            hourlyPrice="0", remainingTotalValue="0", remainingUpfrontValue="0"
        )
        target_configuration_value_rollup = ReservationValue(
            hourlyPrice="0", remainingTotalValue="0", remainingUpfrontValue="0"
        )
        # For simplicity, set rollups to string of sums
        reserved_instance_value_rollup.remainingTotalValue = str(total_input_value)
        reserved_instance_value_rollup.hourlyPrice = "0"
        reserved_instance_value_rollup.remainingUpfrontValue = "0"
        target_configuration_value_rollup.remainingTotalValue = str(target_value)
        target_configuration_value_rollup.hourlyPrice = "0"
        target_configuration_value_rollup.remainingUpfrontValue = "0"

        # Compose response
        response = {
            "requestId": self.generate_request_id(),
            "currencyCode": "USD",
            "isValidExchange": is_valid_exchange,
            "paymentDue": str(payment_due),
            "reservedInstanceValueRollup": reserved_instance_value_rollup.to_dict(),
            "reservedInstanceValueSet": [r.to_dict() for r in reserved_instance_value_set],
            "targetConfigurationValueRollup": target_configuration_value_rollup.to_dict(),
            "targetConfigurationValueSet": [t.to_dict() for t in target_value_set],
            "validationFailureReason": None if is_valid_exchange else "The target configuration value is less than the input",
            "outputReservedInstancesWillExpireAt": None,  # Not implemented, could be set to earliest expiration date
        }
        return response


    def modify_reserved_instances(self, params: dict) -> dict:
        """
        Modifies the configuration of your Reserved Instances.
        Requires ReservedInstancesConfigurationSetItemType.N and ReservedInstancesId.N.
        """
        client_token = params.get("ClientToken")
        configurations = params.get("ReservedInstancesConfigurationSetItemType", [])
        reserved_instance_ids = params.get("ReservedInstancesId", [])

        if not configurations or not isinstance(configurations, list) or len(configurations) == 0:
            raise ValueError("ReservedInstancesConfigurationSetItemType.N is required and must be a non-empty list")
        if not reserved_instance_ids or not isinstance(reserved_instance_ids, list) or len(reserved_instance_ids) == 0:
            raise ValueError("ReservedInstancesId.N is required and must be a non-empty list")

        #

    def purchase_reserved_instances_offering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        instance_count = params.get("InstanceCount")
        reserved_instances_offering_id = params.get("ReservedInstancesOfferingId")
        if instance_count is None:
            raise ValueError("InstanceCount is required")
        if reserved_instances_offering_id is None:
            raise ValueError("ReservedInstancesOfferingId is required")

        # Validate InstanceCount type and value
        if not isinstance(instance_count, int) or instance_count <= 0:
            raise ValueError("InstanceCount must be a positive integer")

        # Validate LimitPrice if provided
        limit_price_param = params.get("LimitPrice")
        limit_price = None
        if limit_price_param is not None:
            amount = limit_price_param.get("Amount")
            currency_code = limit_price_param.get("CurrencyCode")
            if amount is not None and (not isinstance(amount, (int, float)) or amount < 0):
                raise ValueError("LimitPrice.Amount must be a non-negative number")
            if currency_code is not None and currency_code != "USD":
                raise ValueError("LimitPrice.CurrencyCode must be 'USD' if specified")
            limit_price = ReservedInstanceLimitPrice(
                Amount=amount,
                CurrencyCode=currency_code,
            )

        # Validate PurchaseTime if provided
        purchase_time = params.get("PurchaseTime")
        if purchase_time is not None and not isinstance(purchase_time, (str,)):
            # We expect a string timestamp, but no strict parsing here
            raise ValueError("PurchaseTime must be a string timestamp if specified")

        # Check DryRun parameter
        dry_run = params.get("DryRun", False)
        if dry_run:
            # Here we would check permissions, but since this is an emulator, we simulate success
            # Raise an exception or return error if no permission, else raise DryRunOperation error
            # For now, simulate success by raising DryRunOperation error
            from botocore.exceptions import ClientError
            error_response = {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }
            raise ClientError(error_response, "PurchaseReservedInstancesOffering")

        # Find the offering in state
        offering = self.state.reserved_instances_offerings.get(reserved_instances_offering_id)
        if offering is None:
            raise ValueError(f"ReservedInstancesOfferingId {reserved_instances_offering_id} not found")

        # If offering is marketplace and limit_price is specified, check that total price <= limit price
        if offering.marketplace and limit_price is not None and limit_price.Amount is not None:
            total_price = instance_count * (offering.fixed_price or 0)
            if total_price > limit_price.Amount:
                raise ValueError("Total price exceeds the specified LimitPrice.Amount")

        # Generate reserved instance id
        reserved_instances_id = self.generate_unique_id()

        # Create ReservedInstance object and store in state
        # We do not have a ReservedInstance class defined in the snippet, so we create a minimal dict
        reserved_instance = {
            "reserved_instances_id": reserved_instances_id,
            "reserved_instances_offering_id": reserved_instances_offering_id,
            "instance_count": instance_count,
            "state": ReservedInstanceState.ACTIVE if hasattr(ReservedInstanceState, "ACTIVE") else "active",
            "purchase_time": purchase_time,
            "limit_price": limit_price,
            "owner_id": self.get_owner_id(),
            "marketplace": offering.marketplace,
            "fixed_price": offering.fixed_price,
            "duration": offering.duration,
            "instance_type": offering.instance_type,
            "scope": offering.scope,
            "offering_class": offering.offering_class,
            "product_description": offering.product_description,
        }
        self.state.reserved_instances[reserved_instances_id] = reserved_instance

        # Generate request id
        request_id = self.generate_request_id()

        return {
            "requestId": request_id,
            "reservedInstancesId": reserved_instances_id,
        }

    

from emulator_core.gateway.base import BaseGateway

class ReservedInstancesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptReservedInstancesExchangeQuote", self.accept_reserved_instances_exchange_quote)
        self.register_action("CancelReservedInstancesListing", self.cancel_reserved_instances_listing)
        self.register_action("CreateReservedInstancesListing", self.create_reserved_instances_listing)
        self.register_action("DeleteQueuedReservedInstances", self.delete_queued_reserved_instances)
        self.register_action("DescribeReservedInstances", self.describe_reserved_instances)
        self.register_action("DescribeReservedInstancesListings", self.describe_reserved_instances_listings)
        self.register_action("DescribeReservedInstancesModifications", self.describe_reserved_instances_modifications)
        self.register_action("DescribeReservedInstancesOfferings", self.describe_reserved_instances_offerings)
        self.register_action("GetReservedInstancesExchangeQuote", self.get_reserved_instances_exchange_quote)
        self.register_action("ModifyReservedInstances", self.modify_reserved_instances)
        self.register_action("PurchaseReservedInstancesOffering", self.purchase_reserved_instances_offering)

    def accept_reserved_instances_exchange_quote(self, params):
        return self.backend.accept_reserved_instances_exchange_quote(params)

    def cancel_reserved_instances_listing(self, params):
        return self.backend.cancel_reserved_instances_listing(params)

    def create_reserved_instances_listing(self, params):
        return self.backend.create_reserved_instances_listing(params)

    def delete_queued_reserved_instances(self, params):
        return self.backend.delete_queued_reserved_instances(params)

    def describe_reserved_instances(self, params):
        return self.backend.describe_reserved_instances(params)

    def describe_reserved_instances_listings(self, params):
        return self.backend.describe_reserved_instances_listings(params)

    def describe_reserved_instances_modifications(self, params):
        return self.backend.describe_reserved_instances_modifications(params)

    def describe_reserved_instances_offerings(self, params):
        return self.backend.describe_reserved_instances_offerings(params)

    def get_reserved_instances_exchange_quote(self, params):
        return self.backend.get_reserved_instances_exchange_quote(params)

    def modify_reserved_instances(self, params):
        return self.backend.modify_reserved_instances(params)

    def purchase_reserved_instances_offering(self, params):
        return self.backend.purchase_reserved_instances_offering(params)
