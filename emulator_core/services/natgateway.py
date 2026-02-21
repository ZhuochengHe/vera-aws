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
class NatGateway:
    attached_appliance_set: List[Any] = field(default_factory=list)
    auto_provision_zones: str = ""
    auto_scaling_ips: str = ""
    availability_mode: str = ""
    connectivity_type: str = ""
    create_time: str = ""
    delete_time: str = ""
    failure_code: str = ""
    failure_message: str = ""
    nat_gateway_address_set: List[Any] = field(default_factory=list)
    nat_gateway_id: str = ""
    provisioned_bandwidth: Dict[str, Any] = field(default_factory=dict)
    route_table_id: str = ""
    state: str = ""
    subnet_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    vpc_id: str = ""

    # Internal dependency tracking — not in API response
    route_table_ids: List[str] = field(default_factory=list)  # tracks RouteTable children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "attachedApplianceSet": self.attached_appliance_set,
            "autoProvisionZones": self.auto_provision_zones,
            "autoScalingIps": self.auto_scaling_ips,
            "availabilityMode": self.availability_mode,
            "connectivityType": self.connectivity_type,
            "createTime": self.create_time,
            "deleteTime": self.delete_time,
            "failureCode": self.failure_code,
            "failureMessage": self.failure_message,
            "natGatewayAddressSet": self.nat_gateway_address_set,
            "natGatewayId": self.nat_gateway_id,
            "provisionedBandwidth": self.provisioned_bandwidth,
            "routeTableId": self.route_table_id,
            "state": self.state,
            "subnetId": self.subnet_id,
            "tagSet": self.tag_set,
            "vpcId": self.vpc_id,
        }

class NatGateway_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.nat_gateways  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.subnets.get(params['subnet_id']).nat_gateway_ids.append(new_id)
    #   Delete: self.state.subnets.get(resource.subnet_id).nat_gateway_ids.remove(resource_id)
    #   Create: self.state.vpcs.get(params['vpc_id']).nat_gateway_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).nat_gateway_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], required: List[str]):
        for key in required:
            value = params.get(key)
            if value is None or (isinstance(value, str) and value == "") or (isinstance(value, list) and len(value) == 0):
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _get_nat_gateway(self, nat_gateway_id: str):
        resource = self.resources.get(nat_gateway_id)
        if not resource:
            return None, create_error_response("InvalidNatGatewayID.NotFound", f"The ID '{nat_gateway_id}' does not exist")
        return resource, None

    def _find_nat_gateway_address(self, nat_gateway: NatGateway, association_id: Optional[str] = None,
                                  allocation_id: Optional[str] = None, private_ip: Optional[str] = None):
        for address in nat_gateway.nat_gateway_address_set:
            if association_id and address.get("associationId") != association_id:
                continue
            if allocation_id and address.get("allocationId") != allocation_id:
                continue
            if private_ip and address.get("privateIp") != private_ip:
                continue
            return address
        return None

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # These helpers can be used by multiple API methods.

    def AssignPrivateNatGatewayAddress(self, params: Dict[str, Any]):
        """Assigns private IPv4 addresses to a private NAT gateway. For more information, seeWork with NAT gatewaysin theAmazon VPC User Guide."""

        error = self._require_params(params, ["NatGatewayId"])
        if error:
            return error

        nat_gateway_id = params.get("NatGatewayId")
        nat_gateway, error = self._get_nat_gateway(nat_gateway_id)
        if error:
            return error

        private_ips = list(params.get("PrivateIpAddress.N", []) or [])
        private_ip_count = int(params.get("PrivateIpAddressCount") or 0)
        if private_ip_count > len(private_ips):
            for index in range(private_ip_count - len(private_ips)):
                private_ips.append(f"10.0.1.{index + 10}")

        if not private_ips:
            return create_error_response("MissingParameter", "Missing required parameter: PrivateIpAddress.N")

        availability_zone = ""
        availability_zone_id = ""
        if nat_gateway.nat_gateway_address_set:
            availability_zone = nat_gateway.nat_gateway_address_set[0].get("availabilityZone", "")
            availability_zone_id = nat_gateway.nat_gateway_address_set[0].get("availabilityZoneId", "")

        for private_ip in private_ips:
            if self._find_nat_gateway_address(nat_gateway, private_ip=private_ip):
                continue
            nat_gateway.nat_gateway_address_set.append({
                "allocationId": "",
                "associationId": "",
                "availabilityZone": availability_zone,
                "availabilityZoneId": availability_zone_id,
                "failureMessage": "",
                "isPrimary": False,
                "networkInterfaceId": "",
                "privateIp": private_ip,
                "publicIp": "",
                "status": ResourceState.AVAILABLE.value,
            })

        return {
            'natGatewayAddressSet': nat_gateway.nat_gateway_address_set,
            'natGatewayId': nat_gateway.nat_gateway_id,
            }

    def AssociateNatGatewayAddress(self, params: Dict[str, Any]):
        """Associates Elastic IP addresses (EIPs) and private IPv4 addresses with a public NAT gateway. For more information, 
            seeWork with NAT gatewaysin theAmazon VPC User Guide. By default, you can associate up to 2 Elastic IP addresses per public NAT gateway. You can increase the limit by reque"""

        error = self._require_params(params, ["AllocationId.N", "NatGatewayId"])
        if error:
            return error

        nat_gateway_id = params.get("NatGatewayId")
        nat_gateway, error = self._get_nat_gateway(nat_gateway_id)
        if error:
            return error

        allocation_ids = list(params.get("AllocationId.N", []) or [])
        private_ips = list(params.get("PrivateIpAddress.N", []) or [])

        for allocation_id in allocation_ids:
            if allocation_id not in self.state.elastic_ip_addresses:
                return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")

        availability_zone = params.get("AvailabilityZone") or ""
        availability_zone_id = params.get("AvailabilityZoneId") or ""
        if not availability_zone and nat_gateway.nat_gateway_address_set:
            availability_zone = nat_gateway.nat_gateway_address_set[0].get("availabilityZone", "")
        if not availability_zone_id and nat_gateway.nat_gateway_address_set:
            availability_zone_id = nat_gateway.nat_gateway_address_set[0].get("availabilityZoneId", "")

        for index, allocation_id in enumerate(allocation_ids):
            if self._find_nat_gateway_address(nat_gateway, allocation_id=allocation_id):
                continue
            private_ip = private_ips[index] if index < len(private_ips) else ""
            if private_ip and self._find_nat_gateway_address(nat_gateway, private_ip=private_ip):
                private_ip = ""

            eip = self.state.elastic_ip_addresses.get(allocation_id)
            association_id = eip.association_id or self._generate_id("eipassoc")
            public_ip = eip.public_ip or ""
            if not eip.association_id:
                eip.association_id = association_id

            nat_gateway.nat_gateway_address_set.append({
                "allocationId": allocation_id,
                "associationId": association_id,
                "availabilityZone": availability_zone,
                "availabilityZoneId": availability_zone_id,
                "failureMessage": "",
                "isPrimary": False,
                "networkInterfaceId": "",
                "privateIp": private_ip,
                "publicIp": public_ip,
                "status": ResourceState.AVAILABLE.value,
            })

        return {
            'natGatewayAddressSet': nat_gateway.nat_gateway_address_set,
            'natGatewayId': nat_gateway.nat_gateway_id,
            }

    def CreateNatGateway(self, params: Dict[str, Any]):
        """Creates a NAT gateway in the specified subnet. This action creates a network interface
          in the specified subnet with a private IP address from the IP address range of the
          subnet. You can create either a public NAT gateway or a private NAT gateway. With a public NAT gateway, intern"""

        error = self._require_params(params, ["SubnetId"])
        if error:
            return error

        subnet_id = params.get("SubnetId")
        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")

        vpc_id = params.get("VpcId") or getattr(subnet, "vpc_id", "")
        if vpc_id:
            vpc = self.state.vpcs.get(vpc_id)
            if not vpc:
                return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        connectivity_type = params.get("ConnectivityType") or "public"
        allocation_id = params.get("AllocationId")
        if connectivity_type != "private" and not allocation_id:
            return create_error_response("MissingParameter", "Missing required parameter: AllocationId")

        if allocation_id and allocation_id not in self.state.elastic_ip_addresses:
            return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")

        secondary_allocation_ids = params.get("SecondaryAllocationId.N", []) or []
        for secondary_id in secondary_allocation_ids:
            if secondary_id not in self.state.elastic_ip_addresses:
                return create_error_response("InvalidAllocationID.NotFound", f"The ID '{secondary_id}' does not exist")

        private_ip_address = params.get("PrivateIpAddress") or ""
        secondary_private_ips = list(params.get("SecondaryPrivateIpAddress.N", []) or [])
        secondary_private_ip_count = int(params.get("SecondaryPrivateIpAddressCount") or 0)
        if secondary_private_ip_count > len(secondary_private_ips):
            for index in range(secondary_private_ip_count - len(secondary_private_ips)):
                secondary_private_ips.append(f"10.0.0.{index + 2}")

        if not private_ip_address:
            if secondary_private_ips:
                private_ip_address = secondary_private_ips.pop(0)
            else:
                private_ip_address = "10.0.0.1"

        availability_zone = getattr(subnet, "availability_zone", "") or getattr(subnet, "availabilityZone", "")
        availability_zone_id = getattr(subnet, "availability_zone_id", "") or getattr(subnet, "availabilityZoneId", "")

        def _build_address(allocation: Optional[str], private_ip: str, is_primary: bool) -> Dict[str, Any]:
            association_id = ""
            public_ip = ""
            if allocation:
                eip = self.state.elastic_ip_addresses.get(allocation)
                if eip:
                    public_ip = eip.public_ip or ""
                    association_id = eip.association_id or self._generate_id("eipassoc")
                    if not eip.association_id:
                        eip.association_id = association_id
            return {
                "allocationId": allocation or "",
                "associationId": association_id,
                "availabilityZone": availability_zone,
                "availabilityZoneId": availability_zone_id,
                "failureMessage": "",
                "isPrimary": is_primary,
                "networkInterfaceId": "",
                "privateIp": private_ip or "",
                "publicIp": public_ip,
                "status": ResourceState.AVAILABLE.value,
            }

        nat_gateway_address_set: List[Dict[str, Any]] = []
        nat_gateway_address_set.append(_build_address(allocation_id, private_ip_address, True))

        for index, secondary_id in enumerate(secondary_allocation_ids):
            private_ip = secondary_private_ips[index] if index < len(secondary_private_ips) else ""
            nat_gateway_address_set.append(_build_address(secondary_id, private_ip, False))

        for index in range(len(secondary_allocation_ids), len(secondary_private_ips)):
            nat_gateway_address_set.append(_build_address(None, secondary_private_ips[index], False))

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            resource_type = spec.get("ResourceType")
            if resource_type and resource_type not in {"natgateway", "nat-gateway"}:
                continue
            for tag in spec.get("Tags") or spec.get("Tag") or []:
                if tag:
                    tag_set.append(tag)

        nat_gateway_id = self._generate_id("nat")
        now = self._now_iso()
        resource = NatGateway(
            attached_appliance_set=[],
            auto_provision_zones="",
            auto_scaling_ips="",
            availability_mode=params.get("AvailabilityMode") or "",
            connectivity_type=connectivity_type,
            create_time=now,
            delete_time="",
            failure_code="",
            failure_message="",
            nat_gateway_address_set=nat_gateway_address_set,
            nat_gateway_id=nat_gateway_id,
            provisioned_bandwidth={},
            route_table_id="",
            state=ResourceState.AVAILABLE.value,
            subnet_id=subnet_id,
            tag_set=tag_set,
            vpc_id=vpc_id or "",
        )
        self.resources[nat_gateway_id] = resource

        parent = self.state.subnets.get(subnet_id)
        if parent and hasattr(parent, "nat_gateway_ids"):
            if nat_gateway_id not in parent.nat_gateway_ids:
                parent.nat_gateway_ids.append(nat_gateway_id)

        parent = self.state.vpcs.get(vpc_id) if vpc_id else None
        if parent and hasattr(parent, "nat_gateway_ids"):
            if nat_gateway_id not in parent.nat_gateway_ids:
                parent.nat_gateway_ids.append(nat_gateway_id)

        return {
            'clientToken': params.get("ClientToken") or "",
            'natGateway': resource.to_dict(),
            }

    def DeleteNatGateway(self, params: Dict[str, Any]):
        """Deletes the specified NAT gateway. Deleting a public NAT gateway disassociates its Elastic IP address, 
          but does not release the address from your account. Deleting a NAT gateway does not delete any NAT gateway 
          routes in your route tables."""

        error = self._require_params(params, ["NatGatewayId"])
        if error:
            return error

        nat_gateway_id = params.get("NatGatewayId")
        nat_gateway, error = self._get_nat_gateway(nat_gateway_id)
        if error:
            return error

        if getattr(nat_gateway, "route_table_ids", []):
            return create_error_response("DependencyViolation", "NatGateway has dependent RouteTable(s) and cannot be deleted.")

        for address in list(nat_gateway.nat_gateway_address_set):
            allocation_id = address.get("allocationId")
            association_id = address.get("associationId")
            if allocation_id:
                eip = self.state.elastic_ip_addresses.get(allocation_id)
                if eip and association_id and eip.association_id == association_id:
                    eip.association_id = ""

        nat_gateway.state = ResourceState.DELETED.value
        nat_gateway.delete_time = self._now_iso()

        parent = self.state.subnets.get(nat_gateway.subnet_id)
        if parent and hasattr(parent, "nat_gateway_ids") and nat_gateway_id in parent.nat_gateway_ids:
            parent.nat_gateway_ids.remove(nat_gateway_id)

        parent = self.state.vpcs.get(nat_gateway.vpc_id)
        if parent and hasattr(parent, "nat_gateway_ids") and nat_gateway_id in parent.nat_gateway_ids:
            parent.nat_gateway_ids.remove(nat_gateway_id)

        return {
            'natGatewayId': nat_gateway_id,
            }

    def DescribeNatGateways(self, params: Dict[str, Any]):
        """Describes your NAT gateways. The default is to describe all your NAT gateways. 
          Alternatively, you can specify specific NAT gateway IDs or filter the results to
          include only the NAT gateways that match specific criteria."""

        nat_gateway_ids = params.get("NatGatewayId.N", []) or []
        if nat_gateway_ids:
            missing = [ng_id for ng_id in nat_gateway_ids if ng_id not in self.resources]
            if missing:
                return create_error_response("InvalidNatGatewayID.NotFound", f"The ID '{missing[0]}' does not exist")
            resources = [self.resources[ng_id] for ng_id in nat_gateway_ids]
        else:
            resources = list(self.resources.values())

        filters = params.get("Filter.N", []) or []
        if filters:
            resources = apply_filters(resources, filters)

        max_results = int(params.get("MaxResults") or 100)
        resources = resources[:max_results]

        return {
            'natGatewaySet': [resource.to_dict() for resource in resources],
            'nextToken': None,
            }

    def DisassociateNatGatewayAddress(self, params: Dict[str, Any]):
        """Disassociates secondary Elastic IP addresses (EIPs) from a public NAT gateway. 
            You cannot disassociate your primary EIP. For more information, seeEdit secondary IP address associationsin theAmazon VPC User Guide. While disassociating is in progress, you cannot associate/disassociate add"""

        error = self._require_params(params, ["AssociationId.N", "NatGatewayId"])
        if error:
            return error

        nat_gateway_id = params.get("NatGatewayId")
        nat_gateway, error = self._get_nat_gateway(nat_gateway_id)
        if error:
            return error

        association_ids = list(params.get("AssociationId.N", []) or [])
        if not association_ids:
            return create_error_response("MissingParameter", "Missing required parameter: AssociationId.N")

        for association_id in association_ids:
            address = self._find_nat_gateway_address(nat_gateway, association_id=association_id)
            if not address:
                return create_error_response("InvalidAssociationID.NotFound", f"The ID '{association_id}' does not exist")
            if address.get("isPrimary"):
                return create_error_response("InvalidParameterValue", "Cannot disassociate primary NAT gateway address")

        for association_id in association_ids:
            address = self._find_nat_gateway_address(nat_gateway, association_id=association_id)
            if address:
                if address in nat_gateway.nat_gateway_address_set:
                    nat_gateway.nat_gateway_address_set.remove(address)
                allocation_id = address.get("allocationId")
                if allocation_id:
                    eip = self.state.elastic_ip_addresses.get(allocation_id)
                    if eip and eip.association_id == association_id:
                        eip.association_id = ""

        return {
            'natGatewayAddressSet': nat_gateway.nat_gateway_address_set,
            'natGatewayId': nat_gateway.nat_gateway_id,
            }

    def UnassignPrivateNatGatewayAddress(self, params: Dict[str, Any]):
        """Unassigns secondary private IPv4 addresses from a private NAT gateway. You cannot unassign your primary private IP. For more information, 
            seeEdit secondary IP address associationsin theAmazon VPC User Guide. While unassigning is in progress, you cannot assign/unassign additional IP addr"""

        error = self._require_params(params, ["NatGatewayId", "PrivateIpAddress.N"])
        if error:
            return error

        nat_gateway_id = params.get("NatGatewayId")
        nat_gateway, error = self._get_nat_gateway(nat_gateway_id)
        if error:
            return error

        private_ips = list(params.get("PrivateIpAddress.N", []) or [])
        if not private_ips:
            return create_error_response("MissingParameter", "Missing required parameter: PrivateIpAddress.N")

        for private_ip in private_ips:
            address = self._find_nat_gateway_address(nat_gateway, private_ip=private_ip)
            if not address:
                return create_error_response("InvalidParameterValue", f"Private IP '{private_ip}' not found")
            if address.get("isPrimary"):
                return create_error_response("InvalidParameterValue", "Cannot unassign primary NAT gateway private IP")

        for private_ip in private_ips:
            address = self._find_nat_gateway_address(nat_gateway, private_ip=private_ip)
            if address and address in nat_gateway.nat_gateway_address_set:
                nat_gateway.nat_gateway_address_set.remove(address)

        return {
            'natGatewayAddressSet': nat_gateway.nat_gateway_address_set,
            'natGatewayId': nat_gateway.nat_gateway_id,
            }

    def _generate_id(self, prefix: str = 'nat') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class natgateway_RequestParser:
    @staticmethod
    def parse_assign_private_nat_gateway_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NatGatewayId": get_scalar(md, "NatGatewayId"),
            "PrivateIpAddress.N": get_indexed_list(md, "PrivateIpAddress"),
            "PrivateIpAddressCount": get_int(md, "PrivateIpAddressCount"),
        }

    @staticmethod
    def parse_associate_nat_gateway_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId.N": get_indexed_list(md, "AllocationId"),
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NatGatewayId": get_scalar(md, "NatGatewayId"),
            "PrivateIpAddress.N": get_indexed_list(md, "PrivateIpAddress"),
        }

    @staticmethod
    def parse_create_nat_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId": get_scalar(md, "AllocationId"),
            "AvailabilityMode": get_scalar(md, "AvailabilityMode"),
            "AvailabilityZoneAddress.N": get_indexed_list(md, "AvailabilityZoneAddress"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "ConnectivityType": get_scalar(md, "ConnectivityType"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PrivateIpAddress": get_scalar(md, "PrivateIpAddress"),
            "SecondaryAllocationId.N": get_indexed_list(md, "SecondaryAllocationId"),
            "SecondaryPrivateIpAddress.N": get_indexed_list(md, "SecondaryPrivateIpAddress"),
            "SecondaryPrivateIpAddressCount": get_int(md, "SecondaryPrivateIpAddressCount"),
            "SubnetId": get_scalar(md, "SubnetId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_delete_nat_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NatGatewayId": get_scalar(md, "NatGatewayId"),
        }

    @staticmethod
    def parse_describe_nat_gateways_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NatGatewayId.N": get_indexed_list(md, "NatGatewayId"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disassociate_nat_gateway_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId.N": get_indexed_list(md, "AssociationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxDrainDurationSeconds": get_int(md, "MaxDrainDurationSeconds"),
            "NatGatewayId": get_scalar(md, "NatGatewayId"),
        }

    @staticmethod
    def parse_unassign_private_nat_gateway_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxDrainDurationSeconds": get_int(md, "MaxDrainDurationSeconds"),
            "NatGatewayId": get_scalar(md, "NatGatewayId"),
            "PrivateIpAddress.N": get_indexed_list(md, "PrivateIpAddress"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssignPrivateNatGatewayAddress": natgateway_RequestParser.parse_assign_private_nat_gateway_address_request,
            "AssociateNatGatewayAddress": natgateway_RequestParser.parse_associate_nat_gateway_address_request,
            "CreateNatGateway": natgateway_RequestParser.parse_create_nat_gateway_request,
            "DeleteNatGateway": natgateway_RequestParser.parse_delete_nat_gateway_request,
            "DescribeNatGateways": natgateway_RequestParser.parse_describe_nat_gateways_request,
            "DisassociateNatGatewayAddress": natgateway_RequestParser.parse_disassociate_nat_gateway_address_request,
            "UnassignPrivateNatGatewayAddress": natgateway_RequestParser.parse_unassign_private_nat_gateway_address_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class natgateway_ResponseSerializer:
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
                xml_parts.extend(natgateway_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(natgateway_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(natgateway_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(natgateway_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_assign_private_nat_gateway_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssignPrivateNatGatewayAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize natGatewayAddressSet
        _natGatewayAddressSet_key = None
        if "natGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "natGatewayAddressSet"
        elif "NatGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "NatGatewayAddressSet"
        elif "NatGatewayAddresss" in data:
            _natGatewayAddressSet_key = "NatGatewayAddresss"
        if _natGatewayAddressSet_key:
            param_data = data[_natGatewayAddressSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</natGatewayAddressSet>')
            else:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet/>')
        # Serialize natGatewayId
        _natGatewayId_key = None
        if "natGatewayId" in data:
            _natGatewayId_key = "natGatewayId"
        elif "NatGatewayId" in data:
            _natGatewayId_key = "NatGatewayId"
        if _natGatewayId_key:
            param_data = data[_natGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<natGatewayId>{esc(str(param_data))}</natGatewayId>')
        xml_parts.append(f'</AssignPrivateNatGatewayAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_associate_nat_gateway_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateNatGatewayAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize natGatewayAddressSet
        _natGatewayAddressSet_key = None
        if "natGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "natGatewayAddressSet"
        elif "NatGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "NatGatewayAddressSet"
        elif "NatGatewayAddresss" in data:
            _natGatewayAddressSet_key = "NatGatewayAddresss"
        if _natGatewayAddressSet_key:
            param_data = data[_natGatewayAddressSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</natGatewayAddressSet>')
            else:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet/>')
        # Serialize natGatewayId
        _natGatewayId_key = None
        if "natGatewayId" in data:
            _natGatewayId_key = "natGatewayId"
        elif "NatGatewayId" in data:
            _natGatewayId_key = "NatGatewayId"
        if _natGatewayId_key:
            param_data = data[_natGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<natGatewayId>{esc(str(param_data))}</natGatewayId>')
        xml_parts.append(f'</AssociateNatGatewayAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_nat_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateNatGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize natGateway
        _natGateway_key = None
        if "natGateway" in data:
            _natGateway_key = "natGateway"
        elif "NatGateway" in data:
            _natGateway_key = "NatGateway"
        if _natGateway_key:
            param_data = data[_natGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<natGateway>')
            xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</natGateway>')
        xml_parts.append(f'</CreateNatGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_nat_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteNatGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize natGatewayId
        _natGatewayId_key = None
        if "natGatewayId" in data:
            _natGatewayId_key = "natGatewayId"
        elif "NatGatewayId" in data:
            _natGatewayId_key = "NatGatewayId"
        if _natGatewayId_key:
            param_data = data[_natGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<natGatewayId>{esc(str(param_data))}</natGatewayId>')
        xml_parts.append(f'</DeleteNatGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_nat_gateways_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeNatGatewaysResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize natGatewaySet
        _natGatewaySet_key = None
        if "natGatewaySet" in data:
            _natGatewaySet_key = "natGatewaySet"
        elif "NatGatewaySet" in data:
            _natGatewaySet_key = "NatGatewaySet"
        elif "NatGateways" in data:
            _natGatewaySet_key = "NatGateways"
        if _natGatewaySet_key:
            param_data = data[_natGatewaySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<natGatewaySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</natGatewaySet>')
            else:
                xml_parts.append(f'{indent_str}<natGatewaySet/>')
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
        xml_parts.append(f'</DescribeNatGatewaysResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_nat_gateway_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateNatGatewayAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize natGatewayAddressSet
        _natGatewayAddressSet_key = None
        if "natGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "natGatewayAddressSet"
        elif "NatGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "NatGatewayAddressSet"
        elif "NatGatewayAddresss" in data:
            _natGatewayAddressSet_key = "NatGatewayAddresss"
        if _natGatewayAddressSet_key:
            param_data = data[_natGatewayAddressSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</natGatewayAddressSet>')
            else:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet/>')
        # Serialize natGatewayId
        _natGatewayId_key = None
        if "natGatewayId" in data:
            _natGatewayId_key = "natGatewayId"
        elif "NatGatewayId" in data:
            _natGatewayId_key = "NatGatewayId"
        if _natGatewayId_key:
            param_data = data[_natGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<natGatewayId>{esc(str(param_data))}</natGatewayId>')
        xml_parts.append(f'</DisassociateNatGatewayAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_unassign_private_nat_gateway_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<UnassignPrivateNatGatewayAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize natGatewayAddressSet
        _natGatewayAddressSet_key = None
        if "natGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "natGatewayAddressSet"
        elif "NatGatewayAddressSet" in data:
            _natGatewayAddressSet_key = "NatGatewayAddressSet"
        elif "NatGatewayAddresss" in data:
            _natGatewayAddressSet_key = "NatGatewayAddresss"
        if _natGatewayAddressSet_key:
            param_data = data[_natGatewayAddressSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(natgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</natGatewayAddressSet>')
            else:
                xml_parts.append(f'{indent_str}<natGatewayAddressSet/>')
        # Serialize natGatewayId
        _natGatewayId_key = None
        if "natGatewayId" in data:
            _natGatewayId_key = "natGatewayId"
        elif "NatGatewayId" in data:
            _natGatewayId_key = "NatGatewayId"
        if _natGatewayId_key:
            param_data = data[_natGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<natGatewayId>{esc(str(param_data))}</natGatewayId>')
        xml_parts.append(f'</UnassignPrivateNatGatewayAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssignPrivateNatGatewayAddress": natgateway_ResponseSerializer.serialize_assign_private_nat_gateway_address_response,
            "AssociateNatGatewayAddress": natgateway_ResponseSerializer.serialize_associate_nat_gateway_address_response,
            "CreateNatGateway": natgateway_ResponseSerializer.serialize_create_nat_gateway_response,
            "DeleteNatGateway": natgateway_ResponseSerializer.serialize_delete_nat_gateway_response,
            "DescribeNatGateways": natgateway_ResponseSerializer.serialize_describe_nat_gateways_response,
            "DisassociateNatGatewayAddress": natgateway_ResponseSerializer.serialize_disassociate_nat_gateway_address_response,
            "UnassignPrivateNatGatewayAddress": natgateway_ResponseSerializer.serialize_unassign_private_nat_gateway_address_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

