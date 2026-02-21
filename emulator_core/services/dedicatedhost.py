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
class DedicatedHost:
    currency_code: str = ""
    duration: int = 0
    hourly_price: str = ""
    instance_family: str = ""
    offering_id: str = ""
    payment_option: str = ""
    upfront_price: str = ""

    host_id: str = ""
    allocation_time: str = ""
    release_time: str = ""
    auto_placement: str = ""
    availability_zone: str = ""
    availability_zone_id: str = ""
    available_capacity: Dict[str, Any] = field(default_factory=dict)
    client_token: str = ""
    host_maintenance: str = ""
    host_recovery: str = ""
    host_properties: Dict[str, Any] = field(default_factory=dict)
    host_reservation_id: str = ""
    instances: List[str] = field(default_factory=list)
    member_of_service_linked_resource_group: str = ""
    outpost_arn: str = ""
    owner_id: str = ""
    state: str = ""
    tag_set: List[Dict[str, Any]] = field(default_factory=list)
    asset_id: str = ""
    allows_multiple_instance_types: bool = False
    mac_os_latest_supported_version_set: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "currencyCode": self.currency_code,
            "duration": self.duration,
            "hourlyPrice": self.hourly_price,
            "instanceFamily": self.instance_family,
            "offeringId": self.offering_id,
            "paymentOption": self.payment_option,
            "upfrontPrice": self.upfront_price,
            "hostId": self.host_id,
            "allocationTime": self.allocation_time,
            "releaseTime": self.release_time,
            "autoPlacement": self.auto_placement,
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "availableCapacity": self.available_capacity,
            "clientToken": self.client_token,
            "hostMaintenance": self.host_maintenance,
            "hostRecovery": self.host_recovery,
            "hostProperties": self.host_properties,
            "hostReservationId": self.host_reservation_id,
            "instances": self.instances,
            "memberOfServiceLinkedResourceGroup": self.member_of_service_linked_resource_group,
            "outpostArn": self.outpost_arn,
            "ownerId": self.owner_id,
            "state": self.state,
            "tagSet": self.tag_set,
            "assetId": self.asset_id,
            "allowsMultipleInstanceTypes": self.allows_multiple_instance_types,
            "macOSLatestSupportedVersionSet": self.mac_os_latest_supported_version_set,
        }

class DedicatedHost_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.dedicated_hosts  # alias to shared store

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _get_hosts_or_error(self, host_ids: List[str]) -> Any:
        missing = [host_id for host_id in host_ids if host_id not in self.resources]
        if missing:
            return create_error_response("InvalidHostID.NotFound", f"The ID '{missing[0]}' does not exist")
        return [self.resources[host_id] for host_id in host_ids]

    def _get_reservation_store(self) -> Dict[str, Dict[str, Any]]:
        if not hasattr(self.state, "host_reservations"):
            setattr(self.state, "host_reservations", {})
        return self.state.host_reservations

    def AllocateHosts(self, params: Dict[str, Any]):
        """Allocates a Dedicated Host to your account. At a minimum, specify the supported
            instance type or instance family, the Availability Zone in which to allocate the host,
            and the number of hosts to allocate."""

        quantity = int(params.get("Quantity") or 1)
        asset_ids = params.get("AssetId.N", [])
        tag_set: List[Dict[str, Any]] = []
        for tag_spec in params.get("TagSpecification.N", []):
            tag_set.extend(tag_spec.get("Tags", []) or [])

        host_ids: List[str] = []
        for index in range(quantity):
            host_id = self._generate_id("h")
            instance_family = params.get("InstanceFamily") or ""
            instance_type = params.get("InstanceType") or ""
            host = DedicatedHost(
                instance_family=instance_family or instance_type,
                offering_id=self._generate_id("offering"),
                auto_placement=params.get("AutoPlacement") or "",
                availability_zone=params.get("AvailabilityZone") or "",
                availability_zone_id=params.get("AvailabilityZoneId") or "",
                client_token=params.get("ClientToken") or "",
                host_maintenance=params.get("HostMaintenance") or "",
                host_recovery=params.get("HostRecovery") or "",
                outpost_arn=params.get("OutpostArn") or "",
                allocation_time=self._now(),
                state=ResourceState.AVAILABLE.value,
                tag_set=tag_set,
                asset_id=asset_ids[index] if index < len(asset_ids) else "",
            )
            host.host_id = host_id
            host.host_properties = {
                "instanceFamily": instance_family,
                "instanceType": instance_type,
            }
            self.resources[host_id] = host
            host_ids.append(host_id)

        return {
            'hostIdSet': host_ids,
            }

    def DescribeHostReservationOfferings(self, params: Dict[str, Any]):
        """Describes the Dedicated Host reservations that are available to purchase. The results describe all of the Dedicated Host reservation offerings, including
            offerings that might not match the instance family and Region of your Dedicated Hosts.
            When purchasing an offering, ensure"""

        offerings = [
            {
                "currencyCode": host.currency_code,
                "duration": host.duration,
                "hourlyPrice": host.hourly_price,
                "instanceFamily": host.instance_family,
                "offeringId": host.offering_id,
                "paymentOption": host.payment_option,
                "upfrontPrice": host.upfront_price,
            }
            for host in self.resources.values()
        ]

        offering_id = params.get("OfferingId")
        if offering_id and not any(item.get("offeringId") == offering_id for item in offerings):
            return create_error_response(
                "InvalidHostReservationOfferingID.NotFound",
                f"The offering ID '{offering_id}' does not exist",
            )

        if offering_id:
            offerings = [item for item in offerings if item.get("offeringId") == offering_id]

        min_duration = params.get("MinDuration")
        max_duration = params.get("MaxDuration")
        if min_duration is not None:
            offerings = [item for item in offerings if item.get("duration", 0) >= min_duration]
        if max_duration is not None:
            offerings = [item for item in offerings if item.get("duration", 0) <= max_duration]

        offerings = apply_filters(offerings, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or len(offerings) or 0)
        start_index = int(params.get("NextToken") or 0)
        paged = offerings[start_index:start_index + max_results]
        next_token = None
        if start_index + max_results < len(offerings):
            next_token = str(start_index + max_results)

        return {
            'nextToken': next_token,
            'offeringSet': paged,
            }

    def DescribeHostReservations(self, params: Dict[str, Any]):
        """Describes reservations that are associated with Dedicated Hosts in your
            account."""

        reservation_store = self._get_reservation_store()
        reservation_ids = params.get("HostReservationIdSet.N", [])
        if reservation_ids:
            missing = [rid for rid in reservation_ids if rid not in reservation_store]
            if missing:
                return create_error_response(
                    "InvalidHostReservationID.NotFound",
                    f"The host reservation ID '{missing[0]}' does not exist",
                )
            reservations = [reservation_store[rid] for rid in reservation_ids]
        else:
            reservations = list(reservation_store.values())

        reservations = apply_filters(reservations, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or len(reservations) or 0)
        start_index = int(params.get("NextToken") or 0)
        paged = reservations[start_index:start_index + max_results]
        next_token = None
        if start_index + max_results < len(reservations):
            next_token = str(start_index + max_results)

        return {
            'hostReservationSet': paged,
            'nextToken': next_token,
            }

    def DescribeHosts(self, params: Dict[str, Any]):
        """Describes the specified Dedicated Hosts or all your Dedicated Hosts. The results describe only the Dedicated Hosts in the Region you're currently using.
            All listed instances consume capacity on your Dedicated Host. Dedicated Hosts that have
            recently been released are listed w"""

        host_ids = params.get("HostId.N", [])
        if host_ids:
            hosts = self._get_hosts_or_error(host_ids)
            if is_error_response(hosts):
                return hosts
        else:
            hosts = list(self.resources.values())

        hosts = apply_filters(hosts, params.get("Filter.N", []))
        host_dicts = [host.to_dict() for host in hosts]

        max_results = int(params.get("MaxResults") or len(host_dicts) or 0)
        start_index = int(params.get("NextToken") or 0)
        paged = host_dicts[start_index:start_index + max_results]
        next_token = None
        if start_index + max_results < len(host_dicts):
            next_token = str(start_index + max_results)

        return {
            'hostSet': paged,
            'nextToken': next_token,
            }

    def DescribeMacHosts(self, params: Dict[str, Any]):
        """Describes the specified EC2 Mac Dedicated Host or all of your EC2 Mac Dedicated Hosts."""

        host_ids = params.get("HostId.N", [])
        if host_ids:
            hosts = self._get_hosts_or_error(host_ids)
            if is_error_response(hosts):
                return hosts
        else:
            hosts = list(self.resources.values())

        hosts = apply_filters(hosts, params.get("Filter.N", []))
        mac_hosts = [
            {
                "hostId": host.host_id,
                "macOSLatestSupportedVersionSet": host.mac_os_latest_supported_version_set,
            }
            for host in hosts
        ]

        max_results = int(params.get("MaxResults") or len(mac_hosts) or 0)
        start_index = int(params.get("NextToken") or 0)
        paged = mac_hosts[start_index:start_index + max_results]
        next_token = None
        if start_index + max_results < len(mac_hosts):
            next_token = str(start_index + max_results)

        return {
            'macHostSet': paged,
            'nextToken': next_token,
            }

    def GetHostReservationPurchasePreview(self, params: Dict[str, Any]):
        """Preview a reservation purchase with configurations that match those of your Dedicated
            Host. You must have active Dedicated Hosts in your account before you purchase a
            reservation. This is a preview of thePurchaseHostReservationaction and does not
            result in the off"""

        host_ids = params.get("HostIdSet.N", [])
        if not host_ids:
            return create_error_response("MissingParameter", "HostIdSet.N is required")
        offering_id = params.get("OfferingId")
        if not offering_id:
            return create_error_response("MissingParameter", "OfferingId is required")

        hosts = self._get_hosts_or_error(host_ids)
        if is_error_response(hosts):
            return hosts

        currency_code = hosts[0].currency_code if hosts else ""
        duration = hosts[0].duration if hosts else 0
        hourly_price = hosts[0].hourly_price if hosts else ""
        instance_family = hosts[0].instance_family if hosts else ""
        payment_option = hosts[0].payment_option if hosts else ""
        upfront_price = hosts[0].upfront_price if hosts else ""

        purchase = {
            "currencyCode": currency_code,
            "duration": duration,
            "hostIdSet": host_ids,
            "hostReservationId": "",
            "hourlyPrice": hourly_price,
            "instanceFamily": instance_family,
            "paymentOption": payment_option,
            "upfrontPrice": upfront_price,
        }

        return {
            'currencyCode': currency_code,
            'purchase': [purchase],
            'totalHourlyPrice': hourly_price,
            'totalUpfrontPrice': upfront_price,
            }

    def ModifyHosts(self, params: Dict[str, Any]):
        """Modify the auto-placement setting of a Dedicated Host. When auto-placement is enabled,
            any instances that you launch with a tenancy ofhostbut without a specific
            host ID are placed onto any available Dedicated Host in your account that has
            auto-placement enabled. W"""

        host_ids = params.get("HostId.N", [])
        if not host_ids:
            return create_error_response("MissingParameter", "HostId.N is required")

        hosts = self._get_hosts_or_error(host_ids)
        if is_error_response(hosts):
            return hosts

        successful: List[str] = []
        unsuccessful: List[Dict[str, Any]] = []
        for host in hosts:
            host.auto_placement = params.get("AutoPlacement") or host.auto_placement
            host.host_maintenance = params.get("HostMaintenance") or host.host_maintenance
            host.host_recovery = params.get("HostRecovery") or host.host_recovery
            instance_family = params.get("InstanceFamily")
            instance_type = params.get("InstanceType")
            if instance_family or instance_type:
                host.instance_family = instance_family or host.instance_family
                host.host_properties = {
                    "instanceFamily": host.instance_family,
                    "instanceType": instance_type or host.host_properties.get("instanceType", ""),
                }
            successful.append(host.host_id)

        return {
            'successful': successful,
            'unsuccessful': unsuccessful,
            }

    def ModifyInstancePlacement(self, params: Dict[str, Any]):
        """Modifies the placement attributes for a specified instance. You can do the
            following: Modify the affinity between an instance and aDedicated
                        Host. When affinity is set tohostand the instance is
                    not associated with a specific Dedicated Host, the"""

        instance_id = params.get("InstanceId")
        if not instance_id:
            return create_error_response("MissingParameter", "InstanceId is required")

        instance = self.state.instances.get(instance_id)
        if not instance:
            return create_error_response(
                "InvalidInstanceID.NotFound",
                f"The instance ID '{instance_id}' does not exist",
            )

        host_id = params.get("HostId")
        if host_id and host_id not in self.resources:
            return create_error_response(
                "InvalidHostID.NotFound",
                f"The host ID '{host_id}' does not exist",
            )

        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        if group_id and group_id not in self.state.placement_groups:
            return create_error_response(
                "InvalidPlacementGroup.NotFound",
                f"The placement group '{group_id}' does not exist",
            )
        if group_name:
            group_match = any(
                getattr(group, "group_name", None) == group_name
                for group in self.state.placement_groups.values()
            )
            if not group_match:
                return create_error_response(
                    "InvalidPlacementGroup.NotFound",
                    f"The placement group '{group_name}' does not exist",
                )

        placement_updates = {
            "affinity": params.get("Affinity"),
            "groupId": group_id,
            "groupName": group_name,
            "hostId": host_id,
            "hostResourceGroupArn": params.get("HostResourceGroupArn"),
            "partitionNumber": params.get("PartitionNumber"),
            "tenancy": params.get("Tenancy"),
        }

        if isinstance(instance, dict):
            placement = instance.get("placement", {})
            placement.update({k: v for k, v in placement_updates.items() if v is not None})
            instance["placement"] = placement
        else:
            placement = getattr(instance, "placement", {}) or {}
            placement.update({k: v for k, v in placement_updates.items() if v is not None})
            setattr(instance, "placement", placement)

        return {
            'return': True,
            }

    def PurchaseHostReservation(self, params: Dict[str, Any]):
        """Purchase a reservation with configurations that match those of your Dedicated Host.
            You must have active Dedicated Hosts in your account before you purchase a reservation.
            This action results in the specified reservation being purchased and charged to your
            account"""

        host_ids = params.get("HostIdSet.N", [])
        if not host_ids:
            return create_error_response("MissingParameter", "HostIdSet.N is required")
        offering_id = params.get("OfferingId")
        if not offering_id:
            return create_error_response("MissingParameter", "OfferingId is required")

        hosts = self._get_hosts_or_error(host_ids)
        if is_error_response(hosts):
            return hosts

        tag_set: List[Dict[str, Any]] = []
        for tag_spec in params.get("TagSpecification.N", []):
            tag_set.extend(tag_spec.get("Tags", []) or [])

        reservation_id = self._generate_id("hr")
        currency_code = params.get("CurrencyCode") or (hosts[0].currency_code if hosts else "")
        duration = hosts[0].duration if hosts else 0
        hourly_price = hosts[0].hourly_price if hosts else ""
        instance_family = hosts[0].instance_family if hosts else ""
        payment_option = hosts[0].payment_option if hosts else ""
        upfront_price = hosts[0].upfront_price if hosts else ""

        reservation = {
            "count": len(host_ids),
            "currencyCode": currency_code,
            "duration": duration,
            "end": "",
            "hostIdSet": host_ids,
            "hostReservationId": reservation_id,
            "hourlyPrice": hourly_price,
            "instanceFamily": instance_family,
            "offeringId": offering_id,
            "paymentOption": payment_option,
            "start": self._now(),
            "state": "active",
            "tagSet": tag_set,
            "upfrontPrice": upfront_price,
        }
        self._get_reservation_store()[reservation_id] = reservation
        for host in hosts:
            host.host_reservation_id = reservation_id

        purchase = {
            "currencyCode": currency_code,
            "duration": duration,
            "hostIdSet": host_ids,
            "hostReservationId": reservation_id,
            "hourlyPrice": hourly_price,
            "instanceFamily": instance_family,
            "paymentOption": payment_option,
            "upfrontPrice": upfront_price,
        }

        return {
            'clientToken': params.get("ClientToken") or "",
            'currencyCode': currency_code,
            'purchase': [purchase],
            'totalHourlyPrice': hourly_price,
            'totalUpfrontPrice': upfront_price,
            }

    def ReleaseHosts(self, params: Dict[str, Any]):
        """When you no longer want to use an On-Demand Dedicated Host it can be released.
            On-Demand billing is stopped and the host goes intoreleasedstate. The
            host ID of Dedicated Hosts that have been released can no longer be specified in another
            request, for example, to m"""

        host_ids = params.get("HostId.N", [])
        if not host_ids:
            return create_error_response("MissingParameter", "HostId.N is required")

        hosts = self._get_hosts_or_error(host_ids)
        if is_error_response(hosts):
            return hosts

        for host in hosts:
            if host.instances:
                return create_error_response(
                    "DependencyViolation",
                    f"The host '{host.host_id}' has active instances",
                )

        reservation_store = self._get_reservation_store()
        for host in hosts:
            host.release_time = self._now()
            host.state = "released"
            reservation_id = host.host_reservation_id
            if reservation_id and reservation_id in reservation_store:
                reservation = reservation_store[reservation_id]
                host_id_set = reservation.get("hostIdSet", [])
                if host.host_id in host_id_set:
                    host_id_set.remove(host.host_id)
                    reservation["hostIdSet"] = host_id_set
                    reservation["count"] = len(host_id_set)
            if host.host_id in self.resources:
                del self.resources[host.host_id]

        return {
            'successful': host_ids,
            'unsuccessful': [],
            }

    def _generate_id(self, prefix: str = 'offering') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class dedicatedhost_RequestParser:
    @staticmethod
    def parse_allocate_hosts_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssetId.N": get_indexed_list(md, "AssetId"),
            "AutoPlacement": get_scalar(md, "AutoPlacement"),
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "HostMaintenance": get_scalar(md, "HostMaintenance"),
            "HostRecovery": get_scalar(md, "HostRecovery"),
            "InstanceFamily": get_scalar(md, "InstanceFamily"),
            "InstanceType": get_scalar(md, "InstanceType"),
            "OutpostArn": get_scalar(md, "OutpostArn"),
            "Quantity": get_int(md, "Quantity"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_describe_host_reservation_offerings_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "MaxDuration": get_int(md, "MaxDuration"),
            "MaxResults": get_int(md, "MaxResults"),
            "MinDuration": get_int(md, "MinDuration"),
            "NextToken": get_scalar(md, "NextToken"),
            "OfferingId": get_scalar(md, "OfferingId"),
        }

    @staticmethod
    def parse_describe_host_reservations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "HostReservationIdSet.N": get_indexed_list(md, "HostReservationIdSet"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_hosts_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "HostId.N": get_indexed_list(md, "HostId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_mac_hosts_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "HostId.N": get_indexed_list(md, "HostId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_host_reservation_purchase_preview_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "HostIdSet.N": get_indexed_list(md, "HostIdSet"),
            "OfferingId": get_scalar(md, "OfferingId"),
        }

    @staticmethod
    def parse_modify_hosts_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AutoPlacement": get_scalar(md, "AutoPlacement"),
            "HostId.N": get_indexed_list(md, "HostId"),
            "HostMaintenance": get_scalar(md, "HostMaintenance"),
            "HostRecovery": get_scalar(md, "HostRecovery"),
            "InstanceFamily": get_scalar(md, "InstanceFamily"),
            "InstanceType": get_scalar(md, "InstanceType"),
        }

    @staticmethod
    def parse_modify_instance_placement_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Affinity": get_scalar(md, "Affinity"),
            "GroupId": get_scalar(md, "GroupId"),
            "GroupName": get_scalar(md, "GroupName"),
            "HostId": get_scalar(md, "HostId"),
            "HostResourceGroupArn": get_scalar(md, "HostResourceGroupArn"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "PartitionNumber": get_int(md, "PartitionNumber"),
            "Tenancy": get_scalar(md, "Tenancy"),
        }

    @staticmethod
    def parse_purchase_host_reservation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "CurrencyCode": get_scalar(md, "CurrencyCode"),
            "HostIdSet.N": get_indexed_list(md, "HostIdSet"),
            "LimitPrice": get_scalar(md, "LimitPrice"),
            "OfferingId": get_scalar(md, "OfferingId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_release_hosts_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "HostId.N": get_indexed_list(md, "HostId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AllocateHosts": dedicatedhost_RequestParser.parse_allocate_hosts_request,
            "DescribeHostReservationOfferings": dedicatedhost_RequestParser.parse_describe_host_reservation_offerings_request,
            "DescribeHostReservations": dedicatedhost_RequestParser.parse_describe_host_reservations_request,
            "DescribeHosts": dedicatedhost_RequestParser.parse_describe_hosts_request,
            "DescribeMacHosts": dedicatedhost_RequestParser.parse_describe_mac_hosts_request,
            "GetHostReservationPurchasePreview": dedicatedhost_RequestParser.parse_get_host_reservation_purchase_preview_request,
            "ModifyHosts": dedicatedhost_RequestParser.parse_modify_hosts_request,
            "ModifyInstancePlacement": dedicatedhost_RequestParser.parse_modify_instance_placement_request,
            "PurchaseHostReservation": dedicatedhost_RequestParser.parse_purchase_host_reservation_request,
            "ReleaseHosts": dedicatedhost_RequestParser.parse_release_hosts_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class dedicatedhost_ResponseSerializer:
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
                xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_allocate_hosts_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AllocateHostsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize hostIdSet
        _hostIdSet_key = None
        if "hostIdSet" in data:
            _hostIdSet_key = "hostIdSet"
        elif "HostIdSet" in data:
            _hostIdSet_key = "HostIdSet"
        elif "HostIds" in data:
            _hostIdSet_key = "HostIds"
        if _hostIdSet_key:
            param_data = data[_hostIdSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<hostIdSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</hostIdSet>')
            else:
                xml_parts.append(f'{indent_str}<hostIdSet/>')
        xml_parts.append(f'</AllocateHostsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_host_reservation_offerings_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeHostReservationOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize offeringSet
        _offeringSet_key = None
        if "offeringSet" in data:
            _offeringSet_key = "offeringSet"
        elif "OfferingSet" in data:
            _offeringSet_key = "OfferingSet"
        elif "Offerings" in data:
            _offeringSet_key = "Offerings"
        if _offeringSet_key:
            param_data = data[_offeringSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<offeringSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</offeringSet>')
            else:
                xml_parts.append(f'{indent_str}<offeringSet/>')
        xml_parts.append(f'</DescribeHostReservationOfferingsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_host_reservations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeHostReservationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize hostReservationSet
        _hostReservationSet_key = None
        if "hostReservationSet" in data:
            _hostReservationSet_key = "hostReservationSet"
        elif "HostReservationSet" in data:
            _hostReservationSet_key = "HostReservationSet"
        elif "HostReservations" in data:
            _hostReservationSet_key = "HostReservations"
        if _hostReservationSet_key:
            param_data = data[_hostReservationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<hostReservationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</hostReservationSet>')
            else:
                xml_parts.append(f'{indent_str}<hostReservationSet/>')
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
        xml_parts.append(f'</DescribeHostReservationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_hosts_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeHostsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize hostSet
        _hostSet_key = None
        if "hostSet" in data:
            _hostSet_key = "hostSet"
        elif "HostSet" in data:
            _hostSet_key = "HostSet"
        elif "Hosts" in data:
            _hostSet_key = "Hosts"
        if _hostSet_key:
            param_data = data[_hostSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<hostSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</hostSet>')
            else:
                xml_parts.append(f'{indent_str}<hostSet/>')
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
        xml_parts.append(f'</DescribeHostsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_mac_hosts_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeMacHostsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize macHostSet
        _macHostSet_key = None
        if "macHostSet" in data:
            _macHostSet_key = "macHostSet"
        elif "MacHostSet" in data:
            _macHostSet_key = "MacHostSet"
        elif "MacHosts" in data:
            _macHostSet_key = "MacHosts"
        if _macHostSet_key:
            param_data = data[_macHostSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<macHostSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</macHostSet>')
            else:
                xml_parts.append(f'{indent_str}<macHostSet/>')
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
        xml_parts.append(f'</DescribeMacHostsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_host_reservation_purchase_preview_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetHostReservationPurchasePreviewResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize currencyCode
        _currencyCode_key = None
        if "currencyCode" in data:
            _currencyCode_key = "currencyCode"
        elif "CurrencyCode" in data:
            _currencyCode_key = "CurrencyCode"
        if _currencyCode_key:
            param_data = data[_currencyCode_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<currencyCode>{esc(str(param_data))}</currencyCode>')
        # Serialize purchase
        _purchase_key = None
        if "purchase" in data:
            _purchase_key = "purchase"
        elif "Purchase" in data:
            _purchase_key = "Purchase"
        if _purchase_key:
            param_data = data[_purchase_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<purchaseSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</purchaseSet>')
            else:
                xml_parts.append(f'{indent_str}<purchaseSet/>')
        # Serialize totalHourlyPrice
        _totalHourlyPrice_key = None
        if "totalHourlyPrice" in data:
            _totalHourlyPrice_key = "totalHourlyPrice"
        elif "TotalHourlyPrice" in data:
            _totalHourlyPrice_key = "TotalHourlyPrice"
        if _totalHourlyPrice_key:
            param_data = data[_totalHourlyPrice_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<totalHourlyPrice>{esc(str(param_data))}</totalHourlyPrice>')
        # Serialize totalUpfrontPrice
        _totalUpfrontPrice_key = None
        if "totalUpfrontPrice" in data:
            _totalUpfrontPrice_key = "totalUpfrontPrice"
        elif "TotalUpfrontPrice" in data:
            _totalUpfrontPrice_key = "TotalUpfrontPrice"
        if _totalUpfrontPrice_key:
            param_data = data[_totalUpfrontPrice_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<totalUpfrontPrice>{esc(str(param_data))}</totalUpfrontPrice>')
        xml_parts.append(f'</GetHostReservationPurchasePreviewResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_hosts_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyHostsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successful
        _successful_key = None
        if "successful" in data:
            _successful_key = "successful"
        elif "Successful" in data:
            _successful_key = "Successful"
        if _successful_key:
            param_data = data[_successful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</successfulSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulSet/>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</ModifyHostsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_placement_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstancePlacementResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyInstancePlacementResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_purchase_host_reservation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<PurchaseHostReservationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize currencyCode
        _currencyCode_key = None
        if "currencyCode" in data:
            _currencyCode_key = "currencyCode"
        elif "CurrencyCode" in data:
            _currencyCode_key = "CurrencyCode"
        if _currencyCode_key:
            param_data = data[_currencyCode_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<currencyCode>{esc(str(param_data))}</currencyCode>')
        # Serialize purchase
        _purchase_key = None
        if "purchase" in data:
            _purchase_key = "purchase"
        elif "Purchase" in data:
            _purchase_key = "Purchase"
        if _purchase_key:
            param_data = data[_purchase_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<purchaseSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</purchaseSet>')
            else:
                xml_parts.append(f'{indent_str}<purchaseSet/>')
        # Serialize totalHourlyPrice
        _totalHourlyPrice_key = None
        if "totalHourlyPrice" in data:
            _totalHourlyPrice_key = "totalHourlyPrice"
        elif "TotalHourlyPrice" in data:
            _totalHourlyPrice_key = "TotalHourlyPrice"
        if _totalHourlyPrice_key:
            param_data = data[_totalHourlyPrice_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<totalHourlyPrice>{esc(str(param_data))}</totalHourlyPrice>')
        # Serialize totalUpfrontPrice
        _totalUpfrontPrice_key = None
        if "totalUpfrontPrice" in data:
            _totalUpfrontPrice_key = "totalUpfrontPrice"
        elif "TotalUpfrontPrice" in data:
            _totalUpfrontPrice_key = "TotalUpfrontPrice"
        if _totalUpfrontPrice_key:
            param_data = data[_totalUpfrontPrice_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<totalUpfrontPrice>{esc(str(param_data))}</totalUpfrontPrice>')
        xml_parts.append(f'</PurchaseHostReservationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_release_hosts_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReleaseHostsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successful
        _successful_key = None
        if "successful" in data:
            _successful_key = "successful"
        elif "Successful" in data:
            _successful_key = "Successful"
        if _successful_key:
            param_data = data[_successful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</successfulSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulSet/>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(dedicatedhost_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</ReleaseHostsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AllocateHosts": dedicatedhost_ResponseSerializer.serialize_allocate_hosts_response,
            "DescribeHostReservationOfferings": dedicatedhost_ResponseSerializer.serialize_describe_host_reservation_offerings_response,
            "DescribeHostReservations": dedicatedhost_ResponseSerializer.serialize_describe_host_reservations_response,
            "DescribeHosts": dedicatedhost_ResponseSerializer.serialize_describe_hosts_response,
            "DescribeMacHosts": dedicatedhost_ResponseSerializer.serialize_describe_mac_hosts_response,
            "GetHostReservationPurchasePreview": dedicatedhost_ResponseSerializer.serialize_get_host_reservation_purchase_preview_response,
            "ModifyHosts": dedicatedhost_ResponseSerializer.serialize_modify_hosts_response,
            "ModifyInstancePlacement": dedicatedhost_ResponseSerializer.serialize_modify_instance_placement_response,
            "PurchaseHostReservation": dedicatedhost_ResponseSerializer.serialize_purchase_host_reservation_response,
            "ReleaseHosts": dedicatedhost_ResponseSerializer.serialize_release_hosts_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

