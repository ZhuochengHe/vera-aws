from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class AutoPlacement(str, Enum):
    ON = "on"
    OFF = "off"


class HostMaintenance(str, Enum):
    ON = "on"
    OFF = "off"


class HostRecovery(str, Enum):
    ON = "on"
    OFF = "off"


class PaymentOption(str, Enum):
    ALL_UPFRONT = "AllUpfront"
    PARTIAL_UPFRONT = "PartialUpfront"
    NO_UPFRONT = "NoUpfront"


class HostReservationState(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"
    PENDING = "pending"
    FAILED = "failed"
    DELAYED = "delayed"
    UNSUPPORTED = "unsupported"
    PAYMENT_PENDING = "payment-pending"
    PAYMENT_FAILED = "payment-failed"
    RETIRED = "retired"


class HostState(str, Enum):
    AVAILABLE = "available"
    UNDER_ASSESSMENT = "under-assessment"
    PERMANENT_FAILURE = "permanent-failure"
    RELEASED = "released"
    RELEASED_PERMANENT_FAILURE = "released-permanent-failure"
    PENDING = "pending"


class Affinity(str, Enum):
    DEFAULT = "default"
    HOST = "host"


class Tenancy(str, Enum):
    DEFAULT = "default"
    DEDICATED = "dedicated"
    HOST = "host"


@dataclass
class Tag:
    Key: str
    Value: str


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class Filter:
    Name: str
    Values: List[str] = field(default_factory=list)


@dataclass
class InstanceCapacity:
    availableCapacity: Optional[int] = None
    instanceType: Optional[str] = None
    totalCapacity: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availableCapacity": self.availableCapacity,
            "instanceType": self.instanceType,
            "totalCapacity": self.totalCapacity,
        }


@dataclass
class AvailableCapacity:
    availableInstanceCapacity: List[InstanceCapacity] = field(default_factory=list)
    availableVCpus: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availableInstanceCapacity": [ic.to_dict() for ic in self.availableInstanceCapacity],
            "availableVCpus": self.availableVCpus,
        }


@dataclass
class HostProperties:
    cores: Optional[int] = None
    instanceFamily: Optional[str] = None
    instanceType: Optional[str] = None
    sockets: Optional[int] = None
    totalVCpus: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cores": self.cores,
            "instanceFamily": self.instanceFamily,
            "instanceType": self.instanceType,
            "sockets": self.sockets,
            "totalVCpus": self.totalVCpus,
        }


@dataclass
class HostInstance:
    instanceId: Optional[str] = None
    instanceType: Optional[str] = None
    ownerId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instanceId": self.instanceId,
            "instanceType": self.instanceType,
            "ownerId": self.ownerId,
        }


@dataclass
class UnsuccessfulItemError:
    code: Optional[str] = None
    message: Optional[str] = None


@dataclass
class UnsuccessfulItem:
    error: Optional[UnsuccessfulItemError] = None
    resourceId: Optional[str] = None


@dataclass
class HostOffering:
    currencyCode: Optional[str] = None
    duration: Optional[int] = None
    hourlyPrice: Optional[str] = None
    instanceFamily: Optional[str] = None
    offeringId: Optional[str] = None
    paymentOption: Optional[PaymentOption] = None
    upfrontPrice: Optional[str] = None


@dataclass
class HostReservation:
    count: Optional[int] = None
    currencyCode: Optional[str] = None
    duration: Optional[int] = None
    end: Optional[datetime] = None
    hostIdSet: List[str] = field(default_factory=list)
    hostReservationId: Optional[str] = None
    hourlyPrice: Optional[str] = None
    instanceFamily: Optional[str] = None
    offeringId: Optional[str] = None
    paymentOption: Optional[PaymentOption] = None
    start: Optional[datetime] = None
    state: Optional[HostReservationState] = None
    tagSet: List[Tag] = field(default_factory=list)
    upfrontPrice: Optional[str] = None


@dataclass
class Host:
    allocationTime: Optional[datetime] = None
    allowsMultipleInstanceTypes: Optional[AutoPlacement] = None  # on/off string but semantically similar to AutoPlacement
    assetId: Optional[str] = None
    autoPlacement: Optional[AutoPlacement] = None
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    availableCapacity: Optional[AvailableCapacity] = None
    clientToken: Optional[str] = None
    hostId: Optional[str] = None
    hostMaintenance: Optional[HostMaintenance] = None
    hostProperties: Optional[HostProperties] = None
    hostRecovery: Optional[HostRecovery] = None
    hostReservationId: Optional[str] = None
    instances: List[HostInstance] = field(default_factory=list)
    memberOfServiceLinkedResourceGroup: Optional[bool] = None
    outpostArn: Optional[str] = None
    ownerId: Optional[str] = None
    releaseTime: Optional[datetime] = None
    state: Optional[HostState] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocationTime": self.allocationTime.isoformat() if self.allocationTime else None,
            "allowsMultipleInstanceTypes": self.allowsMultipleInstanceTypes.value if self.allowsMultipleInstanceTypes else None,
            "assetId": self.assetId,
            "autoPlacement": self.autoPlacement.value if self.autoPlacement else None,
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "availableCapacity": self.availableCapacity.to_dict() if self.availableCapacity else None,
            "clientToken": self.clientToken,
            "hostId": self.hostId,
            "hostMaintenance": self.hostMaintenance.value if self.hostMaintenance else None,
            "hostProperties": self.hostProperties.to_dict() if self.hostProperties else None,
            "hostRecovery": self.hostRecovery.value if self.hostRecovery else None,
            "hostReservationId": self.hostReservationId,
            "instances": [inst.to_dict() for inst in self.instances],
            "memberOfServiceLinkedResourceGroup": self.memberOfServiceLinkedResourceGroup,
            "outpostArn": self.outpostArn,
            "ownerId": self.ownerId,
            "releaseTime": self.releaseTime.isoformat() if self.releaseTime else None,
            "state": self.state.value if self.state else None,
            "tagSet": [{"Key": tag.Key, "Value": tag.Value} for tag in self.tagSet],
        }


@dataclass
class MacHost:
    hostId: Optional[str] = None
    macOSLatestSupportedVersionSet: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hostId": self.hostId,
            "macOSLatestSupportedVersionSet": self.macOSLatestSupportedVersionSet,
        }


@dataclass
class Purchase:
    currencyCode: Optional[str] = None
    duration: Optional[int] = None
    hostIdSet: List[str] = field(default_factory=list)
    hostReservationId: Optional[str] = None
    hourlyPrice: Optional[str] = None
    instanceFamily: Optional[str] = None
    paymentOption: Optional[PaymentOption] = None
    upfrontPrice: Optional[str] = None


class DedicatedHostsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state.dedicated_hosts, self.state.host_reservations, etc.

    def allocate_hosts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime
        from enum import Enum

        # Validate mutually exclusive parameters InstanceFamily and InstanceType
        instance_family = params.get("InstanceFamily")
        instance_type = params.get("InstanceType")
        if instance_family and instance_type:
            raise ValueError("Cannot specify both InstanceFamily and InstanceType in the same request.")

        # Validate AssetId.N and Quantity
        asset_ids = []
        for key, value in params.items():
            if key.startswith("AssetId."):
                asset_ids.append(value)
        quantity = params.get("Quantity")
        if asset_ids and quantity is not None:
            if int(quantity) != len(asset_ids):
                raise ValueError("Quantity must be equal to the number of AssetIds specified.")

        # Determine number of hosts to allocate
        if asset_ids:
            num_hosts = len(asset_ids)
        else:
            num_hosts = int(quantity) if quantity is not None else 1

        # Validate AutoPlacement
        auto_placement_str = params.get("AutoPlacement", "off")
        if auto_placement_str not in ("on", "off"):
            raise ValueError("AutoPlacement must be 'on' or 'off' if specified.")
        auto_placement = AutoPlacement(auto_placement_str)

        # Validate HostMaintenance
        host_maintenance_str = params.get("HostMaintenance")
        if host_maintenance_str is not None and host_maintenance_str not in ("on", "off"):
            raise ValueError("HostMaintenance must be 'on' or 'off' if specified.")
        host_maintenance = HostMaintenance(host_maintenance_str) if host_maintenance_str else None

        # Validate HostRecovery
        host_recovery_str = params.get("HostRecovery", "off")
        if host_recovery_str not in ("on", "off"):
            raise ValueError("HostRecovery must be 'on' or 'off' if specified.")
        host_recovery = HostRecovery(host_recovery_str)

        # Validate AvailabilityZone and AvailabilityZoneId
        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")

        # Validate OutpostArn
        outpost_arn = params.get("OutpostArn")

        # Validate ClientToken
        client_token = params.get("ClientToken")

        # Parse TagSpecification.N
        tag_set = []
        tag_specifications = {}
        for key, value in params.items():
            if key.startswith("TagSpecification."):
                parts = key.split(".")
                if len(parts) >= 3:
                    tag_spec_index = parts[1]
                    tag_field = parts[2]
                    if tag_spec_index not in tag_specifications:
                        tag_specifications[tag_spec_index] = {"ResourceType": None, "Tags": []}
                    if tag_field == "ResourceType":
                        tag_specifications[tag_spec_index]["ResourceType"] = value
                    elif tag_field == "Tag":
                        # TagSpecification.N.Tag.M.Key or TagSpecification.N.Tag.M.Value
                        if len(parts) >= 5:
                            tag_index = parts[3]
                            tag_key_or_value = parts[4]
                            # Ensure tag list is large enough
                            tags_list = tag_specifications[tag_spec_index]["Tags"]
                            while len(tags_list) < int(tag_index):
                                tags_list.append(Tag(Key=None, Value=None))
                            tag_obj = tags_list[int(tag_index) - 1]
                            if tag_key_or_value == "Key":
                                tag_obj.Key = value
                            elif tag_key_or_value == "Value":
                                tag_obj.Value = value

        # Collect tags from tag_specifications where ResourceType is 'dedicated-host' or None
        for spec in tag_specifications.values():
            if spec["ResourceType"] is None or spec["ResourceType"] == "dedicated-host":
                for tag in spec["Tags"]:
                    if tag.Key is not None:
                        tag_set.append(tag)

        # Generate hosts
        host_ids = []
        now = datetime.datetime.utcnow()
        owner_id = self.get_owner_id()
        for i in range(num_hosts):
            host_id = self.generate_unique_id(prefix="h-")
            host_ids.append(host_id)

            # Determine instance family and instance type for host properties
            host_instance_family = instance_family
            host_instance_type = instance_type
            allows_multiple_instance_types = AutoPlacement.OFF
            if instance_family and not instance_type:
                allows_multiple_instance_types = AutoPlacement.ON
                host_instance_type = None
            elif instance_type:
                allows_multiple_instance_types = AutoPlacement.OFF
                host_instance_family = None

            # Create HostProperties
            host_properties = HostProperties(
                cores=None,
                instanceFamily=host_instance_family,
                instanceType=host_instance_type,
                sockets=None,
                totalVCpus=None,
            )

            # Create AvailableCapacity
            available_instance_capacity = []
            if instance_type:
                # For single instance type, total capacity is 1 (simplified)
                available_instance_capacity.append(
                    InstanceCapacity(
                        availableCapacity=1,
                        instanceType=instance_type,
                        totalCapacity=1,
                    )
                )
                available_vcpus = None
            elif instance_family:
                # For instance family, no specific instance type capacity (simplified)
                available_vcpus = None
            else:
                available_vcpus = None

            available_capacity = AvailableCapacity(
                availableInstanceCapacity=available_instance_capacity,
                availableVCpus=available_vcpus,
            )

            # Create Host object
            host = Host(
                allocationTime=now,
                allowsMultipleInstanceTypes=allows_multiple_instance_types,
                assetId=asset_ids[i] if i < len(asset_ids) else None,
                autoPlacement=auto_placement,
                availabilityZone=availability_zone,
                availabilityZoneId=availability_zone_id,
                availableCapacity=available_capacity,
                clientToken=client_token,
                hostId=host_id,
                hostMaintenance=host_maintenance,
                hostProperties=host_properties,
                hostRecovery=host_recovery,
                hostReservationId=None,
                instances=[],
                memberOfServiceLinkedResourceGroup=None,
                outpostArn=outpost_arn,
                ownerId=owner_id,
                releaseTime=None,
                state=HostState.AVAILABLE,
                tagSet=tag_set.copy(),
            )

            # Store host in state
            self.state.dedicated_hosts[host_id] = host
            self.state.resources[host_id] = host

        response = {
            "hostIdSet": host_ids,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_host_reservation_offerings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Prepare filters
        filters = params.get("Filter", [])
        if not isinstance(filters, list):
            filters = [filters]

        max_duration = params.get("MaxDuration")
        min_duration = params.get("MinDuration")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        offering_id = params.get("OfferingId")

        # Predefined offerings for simulation
        offerings = [
            HostOffering(
                currencyCode="USD",
                duration=94608000,
                hourlyPrice="0.000",
                instanceFamily="m4",
                offeringId="hro-0875903788203856fg",
                paymentOption=PaymentOption.AllUpfront,
                upfrontPrice="28396.000",
            ),
            HostOffering(
                currencyCode="USD",
                duration=31536000,
                hourlyPrice="0.000",
                instanceFamily="r3",
                offeringId="hro-08ddfitlb8990hhkmp",
                paymentOption=PaymentOption.AllUpfront,
                upfrontPrice="13603.000",
            ),
            HostOffering(
                currencyCode="USD",
                duration=94608000,
                hourlyPrice="2.183",
                instanceFamily="x1",
                offeringId="hro-0875903788207657fg",
                paymentOption=PaymentOption.PartialUpfront,
                upfrontPrice="57382.000",
            ),
            HostOffering(
                currencyCode="USD",
                duration=31536000,
                hourlyPrice="0.557",
                instanceFamily="c3",
                offeringId="hro-7890903788203856fg",
                paymentOption=PaymentOption.PartialUpfront,
                upfrontPrice="4879.000",
            ),
            HostOffering(
                currencyCode="USD",
                duration=94608000,
                hourlyPrice="0.000",
                instanceFamily="c4",
                offeringId="hro-1092903788203856fg",
                paymentOption=PaymentOption.AllUpfront,
                upfrontPrice="18892.000",
            ),
        ]

        # Filter offerings by filters
        def offering_matches_filter(offering: HostOffering, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if name == "instance-family":
                return offering.instanceFamily in values
            if name == "payment-option":
                return offering.paymentOption.value in values
            return True

        filtered_offerings = []
        for offering in offerings:
            if offering_id and offering.offeringId != offering_id:
                continue
            if max_duration and offering.duration and offering.duration > int(max_duration):
                continue
            if min_duration and offering.duration and offering.duration < int(min_duration):
                continue
            if filters:
                if not all(offering_matches_filter(offering, f) for f in filters):
                    continue
            filtered_offerings.append(offering)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results_int = int(max_results) if max_results else 100
        if max_results_int > 500:
            raise ValueError("MaxResults cannot be greater than 500.")

        paged_offerings = filtered_offerings[start_index : start_index + max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(filtered_offerings):
            new_next_token = str(start_index + max_results_int)

        response = {
            "offeringSet": paged_offerings,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_host_reservations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Extract filters and parameters
        filters = params.get("Filter", [])
        if not isinstance(filters, list):
            filters = [filters]
        host_reservation_id_set = []
        for key, value in params.items():
            if key.startswith("HostReservationIdSet."):
                host_reservation_id_set.append(value)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect all host reservations from state
        all_reservations = []
        for resource in self.state.resources.values():
            if isinstance(resource, HostReservation):
                all_reservations.append(resource)

        # Filter by HostReservationIdSet if provided
        if host_reservation_id_set:
            all_reservations = [r for r in all_reservations if r.hostReservationId in host_reservation_id_set]

        # Filter by filters
        def reservation_matches_filter(reservation: HostReservation, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if name == "instance-family":
                return reservation.instanceFamily in values
            if name == "payment-option":
                return reservation.paymentOption.value in values if reservation.paymentOption else False
            if name == "state":
                return reservation.state.value in values if reservation.state else False
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in reservation.tagSet:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False
            if name == "tag-key":
                for tag in reservation.tagSet:
                    if tag.Key in values:
                        return True
                return False
            return True

        filtered_reservations = []
        for reservation in all_reservations:
            if filters:
                if not all(reservation_matches_filter(reservation, f) for f in filters):
                    continue
            filtered_reservations.append(reservation)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results_int = int(max_results) if max_results else 100
        if max_results_int > 500:
            raise ValueError("MaxResults cannot be greater than 500.")

        paged_reservations = filtered_reservations[start_index : start_index + max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(filtered_reservations):
            new_next_token = str(start_index + max_results_int)

        response = {
            "hostReservationSet": paged_reservations,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_hosts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = params.get("Filter", [])
        if not isinstance(filters, list):
            filters = [filters]
        host_ids = []
        for key, value in params.items():
            if key.startswith("HostId."):
                host_ids.append(value)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate that MaxResults and HostId.N are not both specified
        if max_results is not None and host_ids:
            raise ValueError("Cannot specify both MaxResults and HostId.N in the same request.")

        # Collect hosts from state
        hosts = list(self.state.dedicated_hosts.values())

        # Filter by host_ids if specified
        if host_ids:
            hosts = [h for h in hosts if h.hostId in host_ids]

        # Filter by filters
        def host_matches_filter(host: Host, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if name == "auto-placement":
                return host.autoPlacement.value in values if host.autoPlacement else False
            if name == "availability-zone":
                return host.availabilityZone in values
            if name == "client-token":
                return host.clientToken in values
            if name == "host-reservation-id":
                return host.hostReservationId in values if host.hostReservationId else False
            if name == "instance-type":
                if host.hostProperties and host.hostProperties.instanceType:
                    return host.hostProperties.instanceType in values
                return False
            if name == "state":
                return host.state.value in values if host.state else False
            if name == "tag-key":
                for tag in host.tagSet:
                    if tag.Key in values:
                        return True
                return False
            return True

        filtered_hosts = []
        for host in hosts:
            if filters:
                if not all(host_matches_filter(host, f) for f in filters):
                    continue
            filtered_hosts.append(host)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results_int = int(max_results) if max_results else 100
        if max_results_int > 500:
            raise ValueError("MaxResults cannot be greater than 500.")

        paged_hosts = filtered_hosts[start_index : start_index + max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(filtered_hosts):
            new_next_token = str(start_index + max_results_int)

        response = {
            "hostSet": [host.to_dict() for host in paged_hosts],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_mac_hosts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = params.get("Filter", [])
        if not isinstance(filters, list):
            filters = [filters]
        host_ids = []
        for key, value in params.items():
            if key.startswith("HostId."):
                host_ids.append(value)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect mac hosts from state
        mac_hosts = []
        for resource in self.state.resources.values():
            if isinstance(resource, MacHost):
                mac_hosts.append(resource)

        # Filter by host_ids if specified
        if host_ids:
            mac_hosts = [h for h in mac_hosts if h.hostId in host_ids]

        # Filter by filters
        def mac_host_matches_filter(mac_host: MacHost, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if name == "availability-zone":
                # MacHost does not have availabilityZone attribute, so no match
                return False
            if name == "instance-type":
                # MacHost does not have instanceType attribute, so no match
                return False
            return True

        filtered_mac_hosts = []
        for mac_host in mac_hosts:
            if filters:
                if not all(mac_host_matches_filter(mac_host, f) for f in filters):
                    continue
            filtered_mac_hosts.append(mac_host)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results_int = int(max_results) if max_results else 100
        if max_results_int > 500:
            raise ValueError("MaxResults cannot be greater than 500.")

        paged_mac_hosts = filtered_mac_hosts[start_index : start_index + max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(filtered_mac_hosts):
            new_next_token = str(start_index + max_results_int)

        response = {
            "macHostSet": [mh.to_dict() for mh in paged_mac_hosts],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response

    def get_host_reservation_purchase_preview(self, params: dict) -> dict:
        offering_id = params.get("OfferingId")
        host_id_set = params.get("HostIdSet", [])
        if not offering_id or not host_id_set:
            raise ValueError("OfferingId and HostIdSet are required parameters")

        # Find the offering by offering_id
        offering = None
        for off in self.state.host_offerings.values():
            if off.offeringId == offering_id:
                offering = off
                break
        if not offering:
            raise ValueError(f"OfferingId {offering_id} not found")

        # Validate hosts exist and belong to owner
        owner_id = self.get_owner_id()
        valid_hosts = []
        for host_id in host_id_set:
            host = self.state.dedicated_hosts.get(host_id)
            if not host:
                raise ValueError(f"HostId {host_id} not found")
            if host.ownerId != owner_id:
                raise ValueError(f"HostId {host_id} does not belong to the current owner")
            valid_hosts.append(host_id)

        # Compose purchase preview
        purchase_item = Purchase(
            currencyCode=offering.currencyCode,
            duration=offering.duration,
            hostIdSet=valid_hosts,
            hostReservationId=None,
            hourlyPrice=offering.hourlyPrice,
            instanceFamily=offering.instanceFamily,
            paymentOption=offering.paymentOption,
            upfrontPrice=offering.upfrontPrice,
        )

        total_hourly_price = str(float(offering.hourlyPrice) * len(valid_hosts)) if offering.hourlyPrice else None
        total_upfront_price = str(float(offering.upfrontPrice) * len(valid_hosts)) if offering.upfrontPrice else None

        return {
            "requestId": self.generate_request_id(),
            "purchase": [purchase_item],
            "currencyCode": offering.currencyCode,
            "totalHourlyPrice": total_hourly_price,
            "totalUpfrontPrice": total_upfront_price,
        }


    def modify_hosts(self, params: dict) -> dict:
        host_ids = params.get("HostId", [])
        if not host_ids:
            raise ValueError("HostId is a required parameter")

        auto_placement = params.get("AutoPlacement")
        host_maintenance = params.get("HostMaintenance")
        host_recovery = params.get("HostRecovery")
        instance_family = params.get("InstanceFamily")
        instance_type = params.get("InstanceType")

        if instance_family and instance_type:
            raise ValueError("Cannot specify both InstanceFamily and InstanceType")

        successful = []
        unsuccessful = []

        for host_id in host_ids:
            host = self.state.dedicated_hosts.get(host_id)
            if not host:
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=UnsuccessfulItemError(
                            code="InvalidHostId.NotFound",
                            message=f"HostId {host_id} not found"
                        ),
                        resourceId=host_id
                    )
                )
                continue

            # Validate and apply AutoPlacement
            if auto_placement is not None:
                if auto_placement not in ("on", "off"):
                    unsuccessful.append(
                        UnsuccessfulItem(
                            error=UnsuccessfulItemError(
                                code="InvalidParameterValue",
                                message="AutoPlacement must be 'on' or 'off'"
                            ),
                            resourceId=host_id
                        )
                    )
                    continue
                host.autoPlacement = AutoPlacement(auto_placement)

            # Validate and apply HostMaintenance
            if host_maintenance is not None:
                if host_maintenance not in ("on", "off"):
                    unsuccessful.append(
                        UnsuccessfulItem(
                            error=UnsuccessfulItemError(
                                code="InvalidParameterValue",
                                message="HostMaintenance must be 'on' or 'off'"
                            ),
                            resourceId=host_id
                        )
                    )
                    continue
                host.hostMaintenance = HostMaintenance(host_maintenance)

            # Validate and apply HostRecovery
            if host_recovery is not None:
                if host_recovery not in ("on", "off"):
                    unsuccessful.append(
                        UnsuccessfulItem(
                            error=UnsuccessfulItemError(
                                code="InvalidParameterValue",
                                message="HostRecovery must be 'on' or 'off'"
                            ),
                            resourceId=host_id
                        )
                    )
                    continue
                host.hostRecovery = HostRecovery(host_recovery)

            # Validate and apply InstanceFamily or InstanceType
            if instance_family:
                # Modify hostProperties to support multiple instance types in the family
                if not host.hostProperties:
                    host.hostProperties = HostProperties()
                host.hostProperties.instanceFamily = instance_family
                host.hostProperties.instanceType = None
                host.allowsMultipleInstanceTypes = AutoPlacement("on")
            elif instance_type:
                if not host.hostProperties:
                    host.hostProperties = HostProperties()
                host.hostProperties.instanceType = instance_type
                host.hostProperties.instanceFamily = None
                host.allowsMultipleInstanceTypes = AutoPlacement("off")

            successful.append(host_id)

        return {
            "requestId": self.generate_request_id(),
            "successful": successful,
            "unsuccessful": unsuccessful,
        }


    def modify_instance_placement(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        if not instance_id:
            raise ValueError("InstanceId is a required parameter")

        affinity = params.get("Affinity")
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        host_id = params.get("HostId")
        host_resource_group_arn = params.get("HostResourceGroupArn")
        partition_number = params.get("PartitionNumber")
        tenancy = params.get("Tenancy")

        # Find the instance and its host
        instance = None
        host = None
        for h in self.state.dedicated_hosts.values():
            for inst in h.instances:
                if inst.instanceId == instance_id:
                    instance = inst
                    host = h
                    break
            if instance:
                break
        if not instance:
            raise ValueError(f"InstanceId {instance_id} not found")

        # Validate tenancy changes
        if tenancy:
            valid_tenancies = {"default", "dedicated", "host"}
            if tenancy not in valid_tenancies:
                raise ValueError(f"Invalid Tenancy value: {tenancy}")
            # For T3 instances, tenancy must be host to use host tenancy
            # We do not have instance type details here, so skip that check
            # Also, tenancy cannot be changed from host to dedicated or default
            if instance.instanceType and instance.instanceType.startswith("t3"):
                if tenancy != "host":
                    raise ValueError("Cannot change tenancy from host to dedicated or default for T3 instances")

        # Modify affinity
        if affinity:
            if affinity not in ("default", "host"):
                raise ValueError("Affinity must be 'default' or 'host'")
            # If affinity is host and instance is not associated with a host, associate it with the specified host
            if affinity == "host" and not host_id and not host:
                raise ValueError("HostId must be specified when setting affinity to 'host' and instance is not associated with a host")
            if affinity == "host" and host_id:
                # Move instance to new host
                new_host = self.state.dedicated_hosts.get(host_id)
                if not new_host:
                    raise ValueError(f"HostId {host_id} not found")
                # Remove instance from old host
                if host:
                    host.instances = [i for i in host.instances if i.instanceId != instance_id]
                # Add instance to new host
                new_host.instances.append(instance)
                host = new_host
            # If affinity is default, disassociate from host
            if affinity == "default" and host:
                host.instances = [i for i in host.instances if i.instanceId != instance_id]
                host = None

        # Modify placement group
        # We do not have placement group data structure here, so just accept parameters without effect

        # Modify host resource group ARN
        # We do not have host resource group data structure here, so just accept parameters without effect

        # Modify partition number
        # We do not have partition placement group data structure here, so just accept parameters without effect

        # Modify tenancy on instance
        # We do not have instance tenancy attribute here, so just accept parameters without effect

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def purchase_host_reservation(self, params: dict) -> dict:
        host_id_set = params.get("HostIdSet", [])
        offering_id = params.get("OfferingId")
        client_token = params.get("ClientToken")
        currency_code = params.get("CurrencyCode", "USD")
        limit_price = params.get("LimitPrice")
        tag_specifications = params.get("TagSpecification", [])

        if not host_id_set or not offering_id:
            raise ValueError("HostIdSet and OfferingId are required parameters")

        # Find offering
        offering = None
        for off in self.state.host_offerings.values():
            if off.offeringId == offering_id:
                offering = off
                break
        if not offering:
            raise ValueError(f"OfferingId {offering_id} not found")

        # Validate hosts exist and belong to owner
        owner_id = self.get_owner_id()
        valid_hosts = []
        for host_id in host_id_set:
            host = self.state.dedicated_hosts.get(host_id)
            if not host:
                raise ValueError(f"HostId {host_id} not found")
            if host.ownerId != owner_id:
                raise ValueError(f"HostId {host_id} does not belong to the current owner")
            valid_hosts.append(host_id)

        # Calculate total upfront price and check limit price
        total_upfront = float(offering.upfrontPrice) * len(valid_hosts) if offering.upfrontPrice else 0.0
        if limit_price is not None:
            try:
                limit_price_val = float(limit_price)
            except Exception:
                raise ValueError("LimitPrice must be a valid number")
            if total_upfront > limit_price_val:
                raise ValueError("Total upfront price exceeds the specified LimitPrice")

        # Create host reservation id
        host_reservation_id = self.generate_unique_id()

        # Create purchase object
        purchase_item = Purchase(
            currencyCode=offering.currencyCode,
            duration=offering.duration,
            hostIdSet=valid_hosts,
            hostReservationId=host_reservation_id,
            hourlyPrice=offering.hourlyPrice,
            instanceFamily=offering.instanceFamily,
            paymentOption=offering.paymentOption,
            upfrontPrice=offering.upfrontPrice,
        )

        # Create HostReservation object and store in state
        host_reservation = HostReservation(
            count=len(valid_hosts),
            currencyCode=offering.currencyCode,
            duration=offering.duration,
            end=None,
            hostIdSet=valid_hosts,
            hostReservationId=host_reservation_id,
            hourlyPrice=offering.hourlyPrice,
            instanceFamily=offering.instanceFamily,
            offeringId=offering_id,
            paymentOption=offering.paymentOption,
            start=None,
            state=None,
            tagSet=[],
            upfrontPrice=offering.upfrontPrice,
        )

        # Apply tags if any
        for tag_spec in tag_specifications:
            if tag_spec.ResourceType == "host-reservation":
                host_reservation.tagSet.extend(tag_spec.Tags)

        self.state.host_reservations[host_reservation_id] = host_reservation

        return {
            "requestId": self.generate_request_id(),
            "clientToken": client_token,
            "currencyCode": offering.currencyCode,
            "purchase": [purchase_item],
            "totalHourlyPrice": str(float(offering.hourlyPrice) * len(valid_hosts)) if offering.hourlyPrice else None,
            "totalUpfrontPrice": str(total_upfront),
        }


    def release_hosts(self, params: dict) -> dict:
        host_ids = params.get("HostId", [])
        if not host_ids:
            raise ValueError("HostId is a required parameter")

        successful = []
        unsuccessful = []

        for host_id in host_ids:
            host = self.state.dedicated_hosts.get(host_id)
            if not host:
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=UnsuccessfulItemError(
                            code="InvalidHostId.NotFound",
                            message=f"HostId {host_id} not found"
                        ),
                        resourceId=host_id
                    )
                )
                continue

            # Check if host has instances running
            if host.instances and len(host.instances) > 0:
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=UnsuccessfulItemError(
                            code="Client.InvalidHost.Occupied",
                            message=f"Dedicated host '{host_id}' cannot be released as it is occupied"
                        ),
                        resourceId=host_id
                    )
                )
                continue

            # Mark host as released
            host.state = HostState.RELEASED
            successful.append(host_id)

        return {
            "requestId": self.generate_request_id(),
            "successful": successful,
            "unsuccessful": unsuccessful,
        }

    

from emulator_core.gateway.base import BaseGateway

class DedicatedHostsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AllocateHosts", self.allocate_hosts)
        self.register_action("DescribeHostReservationOfferings", self.describe_host_reservation_offerings)
        self.register_action("DescribeHostReservations", self.describe_host_reservations)
        self.register_action("DescribeHosts", self.describe_hosts)
        self.register_action("DescribeMacHosts", self.describe_mac_hosts)
        self.register_action("GetHostReservationPurchasePreview", self.get_host_reservation_purchase_preview)
        self.register_action("ModifyHosts", self.modify_hosts)
        self.register_action("ModifyInstancePlacement", self.modify_instance_placement)
        self.register_action("PurchaseHostReservation", self.purchase_host_reservation)
        self.register_action("ReleaseHosts", self.release_hosts)

    def allocate_hosts(self, params):
        return self.backend.allocate_hosts(params)

    def describe_host_reservation_offerings(self, params):
        return self.backend.describe_host_reservation_offerings(params)

    def describe_host_reservations(self, params):
        return self.backend.describe_host_reservations(params)

    def describe_hosts(self, params):
        return self.backend.describe_hosts(params)

    def describe_mac_hosts(self, params):
        return self.backend.describe_mac_hosts(params)

    def get_host_reservation_purchase_preview(self, params):
        return self.backend.get_host_reservation_purchase_preview(params)

    def modify_hosts(self, params):
        return self.backend.modify_hosts(params)

    def modify_instance_placement(self, params):
        return self.backend.modify_instance_placement(params)

    def purchase_host_reservation(self, params):
        return self.backend.purchase_host_reservation(params)

    def release_hosts(self, params):
        return self.backend.release_hosts(params)
