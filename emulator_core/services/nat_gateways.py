from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class NatGatewayAddressStatus(str, Enum):
    ASSIGNING = "assigning"
    UNASSIGNING = "unassigning"
    ASSOCIATING = "associating"
    DISSOCIATING = "disassociating"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class NatGatewayState(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


class ApplianceAttachmentState(str, Enum):
    ATTACHING = "attaching"
    ATTACHED = "attached"
    DETACHING = "detaching"
    DETACHED = "detached"
    ATTACH_FAILED = "attach-failed"
    DETACH_FAILED = "detach-failed"


class ApplianceModificationState(str, Enum):
    MODIFYING = "modifying"
    COMPLETED = "completed"
    FAILED = "failed"


class ApplianceType(str, Enum):
    NETWORK_FIREWALL_PROXY = "network-firewall-proxy"


class AutoProvisionZones(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class AutoScalingIps(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class AvailabilityMode(str, Enum):
    ZONAL = "zonal"
    REGIONAL = "regional"


class ConnectivityType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


@dataclass
class Tag:
    Key: str
    Value: str


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class NatGatewayAddress:
    allocationId: Optional[str] = None  # Public NAT gateway only
    associationId: Optional[str] = None  # Public NAT gateway only
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    failureMessage: Optional[str] = None
    isPrimary: Optional[bool] = None
    networkInterfaceId: Optional[str] = None
    privateIp: Optional[str] = None
    publicIp: Optional[str] = None  # Public NAT gateway only
    status: Optional[NatGatewayAddressStatus] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocationId": self.allocationId,
            "associationId": self.associationId,
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "failureMessage": self.failureMessage,
            "isPrimary": self.isPrimary,
            "networkInterfaceId": self.networkInterfaceId,
            "privateIp": self.privateIp,
            "publicIp": self.publicIp,
            "status": self.status.value if self.status else None,
        }


@dataclass
class NatGatewayAttachedAppliance:
    applianceArn: Optional[str] = None
    attachmentState: Optional[ApplianceAttachmentState] = None
    failureCode: Optional[str] = None
    failureMessage: Optional[str] = None
    modificationState: Optional[ApplianceModificationState] = None
    type: Optional[ApplianceType] = None
    vpcEndpointId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applianceArn": self.applianceArn,
            "attachmentState": self.attachmentState.value if self.attachmentState else None,
            "failureCode": self.failureCode,
            "failureMessage": self.failureMessage,
            "modificationState": self.modificationState.value if self.modificationState else None,
            "type": self.type.value if self.type else None,
            "vpcEndpointId": self.vpcEndpointId,
        }


@dataclass
class ProvisionedBandwidth:
    provisioned: Optional[str] = None
    provisionTime: Optional[datetime] = None
    requested: Optional[str] = None
    requestTime: Optional[datetime] = None
    status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provisioned": self.provisioned,
            "provisionTime": self.provisionTime.isoformat() if self.provisionTime else None,
            "requested": self.requested,
            "requestTime": self.requestTime.isoformat() if self.requestTime else None,
            "status": self.status,
        }


@dataclass
class AvailabilityZoneAddress:
    AllocationIds: List[str] = field(default_factory=list)
    AvailabilityZone: Optional[str] = None
    AvailabilityZoneId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationIds": self.AllocationIds,
            "AvailabilityZone": self.AvailabilityZone,
            "AvailabilityZoneId": self.AvailabilityZoneId,
        }


@dataclass
class NatGateway:
    attachedApplianceSet: List[NatGatewayAttachedAppliance] = field(default_factory=list)
    autoProvisionZones: Optional[AutoProvisionZones] = None
    autoScalingIps: Optional[AutoScalingIps] = None
    availabilityMode: Optional[AvailabilityMode] = None
    connectivityType: Optional[ConnectivityType] = None
    createTime: Optional[datetime] = None
    deleteTime: Optional[datetime] = None
    failureCode: Optional[str] = None
    failureMessage: Optional[str] = None
    natGatewayAddressSet: List[NatGatewayAddress] = field(default_factory=list)
    natGatewayId: Optional[str] = None
    provisionedBandwidth: Optional[ProvisionedBandwidth] = None
    routeTableId: Optional[str] = None
    state: Optional[NatGatewayState] = None
    subnetId: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    vpcId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attachedApplianceSet": [appliance.to_dict() for appliance in self.attachedApplianceSet],
            "autoProvisionZones": self.autoProvisionZones.value if self.autoProvisionZones else None,
            "autoScalingIps": self.autoScalingIps.value if self.autoScalingIps else None,
            "availabilityMode": self.availabilityMode.value if self.availabilityMode else None,
            "connectivityType": self.connectivityType.value if self.connectivityType else None,
            "createTime": self.createTime.isoformat() if self.createTime else None,
            "deleteTime": self.deleteTime.isoformat() if self.deleteTime else None,
            "failureCode": self.failureCode,
            "failureMessage": self.failureMessage,
            "natGatewayAddressSet": [addr.to_dict() for addr in self.natGatewayAddressSet],
            "natGatewayId": self.natGatewayId,
            "provisionedBandwidth": self.provisionedBandwidth.to_dict() if self.provisionedBandwidth else None,
            "routeTableId": self.routeTableId,
            "state": self.state.value if self.state else None,
            "subnetId": self.subnetId,
            "tagSet": [{"Key": tag.Key, "Value": tag.Value} for tag in self.tagSet],
            "vpcId": self.vpcId,
        }


class NATgatewaysBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.nat_gateways or similar

    def assign_private_nat_gateway_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        nat_gateway_id = params.get("NatGatewayId")
        if not nat_gateway_id:
            raise ValueError("NatGatewayId is required")
        nat_gateway = self.state.nat_gateways.get(nat_gateway_id)
        if not nat_gateway:
            raise ValueError(f"NAT Gateway {nat_gateway_id} does not exist")

        private_ip_addresses = params.get("PrivateIpAddress.N", [])
        private_ip_address_count = params.get("PrivateIpAddressCount")

        if private_ip_addresses and private_ip_address_count:
            raise ValueError("Cannot specify both PrivateIpAddress.N and PrivateIpAddressCount")

        if private_ip_address_count is not None:
            if not (1 <= private_ip_address_count <= 31):
                raise ValueError("PrivateIpAddressCount must be between 1 and 31")

        # Only private NAT gateways support private IP assignment
        if nat_gateway.connectivityType is not None and nat_gateway.connectivityType != ConnectivityType.private:
            raise ValueError("AssignPrivateNatGatewayAddress is only supported for private NAT gateways")

        # Collect existing private IPs on the NAT gateway
        existing_private_ips = {addr.privateIp for addr in nat_gateway.natGatewayAddressSet if addr.privateIp}

        # Determine new private IPs to assign
        new_private_ips = set()
        if private_ip_addresses:
            for ip in private_ip_addresses:
                if ip in existing_private_ips:
                    continue
                new_private_ips.add(ip)
        elif private_ip_address_count:
            # Auto-assign private IPs: For emulator, generate dummy IPs in subnet range
            # We do not have subnet CIDR info, so generate dummy IPs with suffixes
            base_ip_prefix = "10.0.0."
            suffix_start = 1
            while len(new_private_ips) < private_ip_address_count:
                candidate_ip = f"{base_ip_prefix}{suffix_start}"
                if candidate_ip not in existing_private_ips and candidate_ip not in new_private_ips:
                    new_private_ips.add(candidate_ip)
                suffix_start += 1
        else:
            # No IPs specified, no count specified, nothing to assign
            new_private_ips = set()

        # Create NatGatewayAddress objects for new private IPs
        for ip in new_private_ips:
            nat_gateway.natGatewayAddressSet.append(
                NatGatewayAddress(
                    allocationId=None,
                    associationId=None,
                    availabilityZone=None,
                    availabilityZoneId=None,
                    failureMessage=None,
                    isPrimary=False,
                    networkInterfaceId=None,
                    privateIp=ip,
                    publicIp=None,
                    status=NatGatewayAddressStatus.succeeded,
                )
            )

        response_addresses = [addr.to_dict() for addr in nat_gateway.natGatewayAddressSet]

        return {
            "natGatewayAddressSet": response_addresses,
            "natGatewayId": nat_gateway_id,
            "requestId": self.generate_request_id(),
        }


    def associate_nat_gateway_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        nat_gateway_id = params.get("NatGatewayId")
        if not nat_gateway_id:
            raise ValueError("NatGatewayId is required")
        nat_gateway = self.state.nat_gateways.get(nat_gateway_id)
        if not nat_gateway:
            raise ValueError(f"NAT Gateway {nat_gateway_id} does not exist")

        allocation_ids = params.get("AllocationId.N", [])
        private_ip_addresses = params.get("PrivateIpAddress.N", [])
        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")

        # Only public NAT gateways support associating EIPs (allocation IDs)
        if allocation_ids and (nat_gateway.connectivityType is None or nat_gateway.connectivityType != ConnectivityType.public):
            raise ValueError("AssociateNatGatewayAddress with AllocationId is only supported for public NAT gateways")

        # Validate that the number of EIPs does not exceed limits (default 2)
        existing_eip_count = sum(1 for addr in nat_gateway.natGatewayAddressSet if addr.allocationId is not None)
        if existing_eip_count + len(allocation_ids) > 2:
            raise ValueError("Cannot associate more than 2 Elastic IP addresses per public NAT gateway")

        # Associate EIPs by allocation IDs
        for alloc_id in allocation_ids:
            # Check if already associated
            if any(addr.allocationId == alloc_id for addr in nat_gateway.natGatewayAddressSet):
                continue
            # Create new NatGatewayAddress for this EIP
            nat_gateway.natGatewayAddressSet.append(
                NatGatewayAddress(
                    allocationId=alloc_id,
                    associationId=self.generate_unique_id(prefix="eipassoc-"),
                    availabilityZone=availability_zone,
                    availabilityZoneId=availability_zone_id,
                    failureMessage=None,
                    isPrimary=False,
                    networkInterfaceId=self.generate_unique_id(prefix="eni-"),
                    privateIp=None,
                    publicIp=None,  # Public IP is not known here, leave None
                    status=NatGatewayAddressStatus.succeeded,
                )
            )

        # Associate private IP addresses (only for private NAT gateways)
        if private_ip_addresses:
            if nat_gateway.connectivityType is None or nat_gateway.connectivityType != ConnectivityType.private:
                raise ValueError("AssociateNatGatewayAddress with PrivateIpAddress.N is only supported for private NAT gateways")
            existing_private_ips = {addr.privateIp for addr in nat_gateway.natGatewayAddressSet if addr.privateIp}
            for ip in private_ip_addresses:
                if ip in existing_private_ips:
                    continue
                nat_gateway.natGatewayAddressSet.append(
                    NatGatewayAddress(
                        allocationId=None,
                        associationId=None,
                        availabilityZone=availability_zone,
                        availabilityZoneId=availability_zone_id,
                        failureMessage=None,
                        isPrimary=False,
                        networkInterfaceId=self.generate_unique_id(prefix="eni-"),
                        privateIp=ip,
                        publicIp=None,
                        status=NatGatewayAddressStatus.succeeded,
                    )
                )

        response_addresses = [addr.to_dict() for addr in nat_gateway.natGatewayAddressSet]

        return {
            "natGatewayAddressSet": response_addresses,
            "natGatewayId": nat_gateway_id,
            "requestId": self.generate_request_id(),
        }


    def create_nat_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        subnet_id = params.get("SubnetId")
        if not subnet_id:
            raise ValueError("SubnetId is required")

        # Validate subnet exists
        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            raise ValueError(f"Subnet {subnet_id} does not exist")

        connectivity_type_str = params.get("ConnectivityType", "public")
        if connectivity_type_str not in (ConnectivityType.private.value, ConnectivityType.public.value):
            raise ValueError("ConnectivityType must be 'private' or 'public'")
        connectivity_type = ConnectivityType(connectivity_type_str)

        availability_mode_str = params.get("AvailabilityMode")
        availability_mode = None
        if availability_mode_str:
            # Validate enum if needed
            availability_mode = AvailabilityMode(availability_mode_str)

        auto_provision_zones = params.get("AutoProvisionZones")
        auto_scaling_ips = params.get("AutoScalingIps")

        allocation_id = params.get("AllocationId")
        private_ip_address = params.get("PrivateIpAddress")

        secondary_allocation_ids = params.get("SecondaryAllocationId.N", [])
        secondary_private_ips = params.get("SecondaryPrivateIpAddress.N", [])
        secondary_private_ip_count = params.get("SecondaryPrivateIpAddressCount")

        availability_zone_address_list = params.get("AvailabilityZoneAddress.N", [])

        tag_specifications = params.get("TagSpecification.N", [])
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key:
                    tags.append(Tag(Key=key, Value=value))

        vpc_id = params.get("VpcId")
        if not vpc_id:
            # Try to get VPC ID from subnet if possible
            vpc_id = getattr(subnet, "vpcId", None)

        # Validate allocation IDs for public NAT gateway
        if connectivity_type == ConnectivityType.public:
            if not allocation_id and not availability_zone_address_list:
                raise ValueError("AllocationId or AvailabilityZoneAddress.N must be specified for public NAT gateway")
            if allocation_id and secondary_allocation_ids:
                # Combine primary and secondary allocation IDs
                all_allocation_ids = [allocation_id] + secondary_allocation_ids
            elif allocation_id:
                all_allocation_ids = [allocation_id]
            elif availability_zone_address_list:
                all_allocation_ids = []
                for az_addr in availability_zone_address_list:
                    all_allocation_ids.extend(az_addr.get("AllocationIds", []))
            else:
                all_allocation_ids = []
        else:
            # Private NAT gateway cannot have allocation IDs
            if allocation_id or secondary_allocation_ids or availability_zone_address_list:
                raise ValueError("AllocationId and AvailabilityZoneAddress.N cannot be specified for private NAT gateway")
            all_allocation_ids = []

        # Generate NAT Gateway ID
        nat_gateway_id = self.generate_unique_id(prefix="nat-")

        # Create NatGatewayAddress list
        nat_gateway_address_set: List[NatGatewayAddress] = []

        # For public NAT gateway, create addresses for allocation IDs
        if connectivity_type == ConnectivityType.public:
            # If AvailabilityZoneAddress.N specified, use those AZs and allocation IDs
            if availability_zone_address_list:
                for az_addr in availability_zone_address_list:
                    az = az_addr.get("AvailabilityZone")
                    az_id = az_addr.get("AvailabilityZoneId")
                    alloc_ids = az_addr.get("AllocationIds", [])
                    for alloc_id in alloc_ids:
                        nat_gateway_address_set.append(
                            NatGatewayAddress(
                                allocationId=alloc_id,
                                associationId=self.generate_unique_id(prefix="eipassoc-"),
                                availabilityZone=az,
                                availabilityZoneId=az_id,
                                failureMessage=None,
                                isPrimary=False,
                                networkInterfaceId=self.generate_unique_id(prefix="eni-"),
                                privateIp=None,
                                publicIp=None,
                                status=NatGatewayAddressStatus.pending,
                            )
                        )
            else:
                # Use primary and secondary allocation IDs
                for alloc_id in all_allocation_ids:
                    nat_gateway_address_set.append(
                        NatGatewayAddress(
                            allocationId=alloc_id,
                            associationId=self.generate_unique_id(prefix="eipassoc-"),
                            availabilityZone=None,
                            availabilityZoneId=None,
                            failureMessage=None,
                            isPrimary=False,
                            networkInterfaceId=self.generate_unique_id(prefix="eni-"),
                            privateIp=None,
                            publicIp=None,
                            status=NatGatewayAddressStatus.pending,
                        )
                    )
        else:
            # Private NAT gateway: create one address with private IP
            if private_ip_address:
                private_ip = private_ip_address
            else:
                # Auto assign private IP: generate dummy IP in subnet range
                private_ip = "10.0.0.1"
            nat_gateway_address_set.append(
                NatGatewayAddress(
                    allocationId=None,
                    associationId=None,
                    availabilityZone=None,
                    availabilityZoneId=None,
                    failureMessage=None,
                    isPrimary=True,
                    networkInterfaceId=self.generate_unique_id(prefix="eni-"),
                    privateIp=private_ip,
                    publicIp=None,
                    status=NatGatewayAddressStatus.pending,
                )
            )
            # Add secondary private IPs if specified
            if secondary_private_ips:
                for ip in secondary_private_ips:
                    nat_gateway_address_set.append(
                        NatGatewayAddress(
                            allocationId=None,
                            associationId=None,
                            availabilityZone=None,
                            availabilityZoneId=None,
                            failureMessage=None,
                            isPrimary=False,
                            networkInterfaceId=self.generate_unique_id(prefix="eni-"),
                            privateIp=ip,
                            publicIp=None,
                            status=NatGatewayAddressStatus.pending,
                        )
                    )
            elif secondary_private_ip_count:
                # Auto assign secondary private IPs
                base_ip_prefix = "10.0.0."
                suffix_start = 2
                count = 0
                while count < secondary_private_ip_count:
                    candidate_ip = f"{base_ip_prefix}{suffix_start}"
                    if candidate_ip != private_ip:
                        nat_gateway_address_set.append(
                            NatGatewayAddress(
                                allocationId=None,
                                associationId=None,
                                availabilityZone=None,
                                availabilityZoneId=None,
                                failureMessage=None,
                                isPrimary=False,
                                networkInterfaceId=self.generate_unique_id(prefix="eni-"),
                                privateIp=candidate_ip,
                                publicIp=None,
                                status=NatGatewayAddressStatus.pending,
                            )
                        )
                        count += 1
                    suffix_start += 1

        # Create NatGateway object
        # LocalStack pattern: NAT Gateway starts in 'pending' state
        # and transitions to 'available' after creation completes.
        # For emulator simplicity, we immediately set to 'available' to avoid
        # needing async polling, but we start with 'pending' to match initial response.
        nat_gateway = NatGateway(
            attachedApplianceSet=[],
            autoProvisionZones=auto_provision_zones,
            autoScalingIps=auto_scaling_ips,
            availabilityMode=availability_mode,
            connectivityType=connectivity_type,
            createTime=datetime.utcnow(),
            deleteTime=None,
            failureCode=None,
            failureMessage=None,
            natGatewayAddressSet=nat_gateway_address_set,
            natGatewayId=nat_gateway_id,
            provisionedBandwidth=None,
            routeTableId=None,
            state=NatGatewayState.PENDING,  # Start in pending state per LocalStack
            subnetId=subnet_id,
            tagSet=tags,
            vpcId=vpc_id,
        )

        self.state.nat_gateways[nat_gateway_id] = nat_gateway
        self.state.resources[nat_gateway_id] = nat_gateway

        # LocalStack pattern: Immediately transition to available for synchronous emulation
        # This allows CloudFormation-style polling to succeed on first describe call
        nat_gateway.state = NatGatewayState.AVAILABLE

        # Update address statuses to succeeded
        for addr in nat_gateway.natGatewayAddressSet:
            addr.status = NatGatewayAddressStatus.SUCCEEDED

        return {
            "clientToken": params.get("ClientToken"),
            "natGateway": nat_gateway.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_nat_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        DeleteNatGateway API - LocalStack compatible behavior.

        LocalStack pattern: NAT Gateway transitions through states:
        - available -> deleting -> deleted

        The NAT Gateway remains in 'deleting' state and is kept in state storage
        so that describe_nat_gateways can return the deleting/deleted status.
        This matches AWS CloudFormation polling behavior.
        """
        nat_gateway_id = params.get("NatGatewayId")
        if not nat_gateway_id:
            raise ValueError("NatGatewayId is required")

        nat_gateway = self.state.nat_gateways.get(nat_gateway_id)
        if not nat_gateway:
            # LocalStack behavior: return success even if not found (idempotent)
            return {
                "natGatewayId": nat_gateway_id,
                "requestId": self.generate_request_id(),
            }

        # If already deleting or deleted, return current state
        if nat_gateway.state in (NatGatewayState.DELETING, NatGatewayState.DELETED):
            return {
                "natGatewayId": nat_gateway_id,
                "requestId": self.generate_request_id(),
            }

        # Mark NAT gateway as deleting and set deleteTime
        # LocalStack keeps the resource in 'deleting' state for polling
        nat_gateway.state = NatGatewayState.DELETING
        nat_gateway.deleteTime = datetime.utcnow()

        # Transition addresses to failed/disassociating state
        for addr in nat_gateway.natGatewayAddressSet:
            addr.status = NatGatewayAddressStatus.FAILED

        # NOTE: We keep the NAT Gateway in state for CloudFormation polling.
        # A background process or subsequent describe call can transition to DELETED.
        # For immediate emulator behavior, we transition to DELETED state.
        nat_gateway.state = NatGatewayState.DELETED

        return {
            "natGatewayId": nat_gateway_id,
            "requestId": self.generate_request_id(),
        }


    def describe_nat_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        nat_gateway_ids = params.get("NatGatewayId.N", [])
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect NAT gateways to describe
        if nat_gateway_ids:
            nat_gateways = [self.state.nat_gateways.get(nat_id) for nat_id in nat_gateway_ids]
            nat_gateways = [ng for ng in nat_gateways if ng is not None]
        else:
            nat_gateways = list(self.state.nat_gateways.values())

        # Apply filters
        def matches_filter(nat_gateway: NatGateway, filter_name: str, filter_values: List[str]) -> bool:
            if filter_name == "nat-gateway-id":
                return nat_gateway.natGatewayId in filter_values
            elif filter_name == "state":
                return nat_gateway.state.value in filter_values
            elif filter_name == "subnet-id":
                return nat_gateway.subnetId in filter_values
            elif filter_name.startswith("tag:"):
                tag_key = filter_name[4:]
                for tag in nat_gateway.tagSet:
                    if tag.Key == tag_key and tag.Value in filter_values:
                        return True
                return False
            elif filter_name == "tag-key":
                for tag in nat_gateway.tagSet:
                    if tag.Key in filter_values:
                        return True
                return False
            elif filter_name == "vpc-id":
                return nat_gateway.vpcId in filter_values
            else:
                # Unknown filter, ignore
                return True

        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if name and values:
                nat_gateways = [ng for ng in nat_gateways if matches_filter(ng, name, values)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            max_results = int(max_results)
            if max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be between 5 and 1000")
        else:
            max_results = 1000

        end_index = start_index + max_results
        paged_nat_gateways = nat_gateways[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(nat_gateways) else None

        nat_gateway_set = [ng.to_dict() for ng in paged_nat_gateways]

        return {
            "natGatewaySet": nat_gateway_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def disassociate_nat_gateway_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        nat_gateway_id = params.get("NatGatewayId")
        association_ids = params.get("AssociationId.N")
        dry_run = params.get("DryRun", False)
        max_drain_duration_seconds = params.get("MaxDrainDurationSeconds", 350)

        if not nat_gateway_id:
            raise ValueError("NatGatewayId is required")
        if not association_ids or not isinstance(association_ids, list):
            raise ValueError("AssociationId.N is required and must be a list of strings")
        if not (1 <= max_drain_duration_seconds <= 4000):
            raise ValueError("MaxDrainDurationSeconds must be between 1 and 4000")

        if dry_run:
            # In a real implementation, check permissions here
            # For emulator, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        nat_gateway = self.state.nat_gateways.get(nat_gateway_id)
        if not nat_gateway:
            raise ValueError(f"NAT Gateway {nat_gateway_id} does not exist")

        # Validate that all association_ids exist and are not primary
        addresses_by_assoc_id = {addr.associationId: addr for addr in nat_gateway.natGatewayAddressSet if addr.associationId}
        for assoc_id in association_ids:
            if assoc_id not in addresses_by_assoc_id:
                raise ValueError(f"AssociationId {assoc_id} not found in NAT Gateway {nat_gateway_id}")
            addr = addresses_by_assoc_id[assoc_id]
            if addr.isPrimary:
                raise ValueError(f"Cannot disassociate primary EIP with AssociationId {assoc_id}")

        # Mark addresses as disassociating and simulate draining
        for assoc_id in association_ids:
            addr = addresses_by_assoc_id[assoc_id]
            addr.status = NatGatewayAddressStatus.DISASSOCIATING
            # In a real implementation, would start draining connections here
            # For emulator, we simulate immediate success after max_drain_duration_seconds
            # But since this is a synchronous call, we simulate immediate removal
            # Remove the address from natGatewayAddressSet after draining
        # Remove addresses after draining simulation
        nat_gateway.natGatewayAddressSet = [
            addr for addr in nat_gateway.natGatewayAddressSet if addr.associationId not in association_ids
        ]

        # Prepare response
        response_addresses = [addr.to_dict() for addr in nat_gateway.natGatewayAddressSet]

        return {
            "natGatewayAddressSet": response_addresses,
            "natGatewayId": nat_gateway_id,
            "requestId": self.generate_request_id(),
        }


    def unassign_private_nat_gateway_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        nat_gateway_id = params.get("NatGatewayId")
        private_ip_addresses = params.get("PrivateIpAddress.N")
        dry_run = params.get("DryRun", False)
        max_drain_duration_seconds = params.get("MaxDrainDurationSeconds", 350)

        if not nat_gateway_id:
            raise ValueError("NatGatewayId is required")
        if not private_ip_addresses or not isinstance(private_ip_addresses, list):
            raise ValueError("PrivateIpAddress.N is required and must be a list of strings")
        if not (1 <= max_drain_duration_seconds <= 4000):
            raise ValueError("MaxDrainDurationSeconds must be between 1 and 4000")

        if dry_run:
            # In a real implementation, check permissions here
            # For emulator, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        nat_gateway = self.state.nat_gateways.get(nat_gateway_id)
        if not nat_gateway:
            raise ValueError(f"NAT Gateway {nat_gateway_id} does not exist")

        # Validate that all private IPs exist and are not primary
        addresses_by_private_ip = {addr.privateIp: addr for addr in nat_gateway.natGatewayAddressSet if addr.privateIp}
        for private_ip in private_ip_addresses:
            if private_ip not in addresses_by_private_ip:
                raise ValueError(f"Private IP address {private_ip} not found in NAT Gateway {nat_gateway_id}")
            addr = addresses_by_private_ip[private_ip]
            if addr.isPrimary:
                raise ValueError(f"Cannot unassign primary private IP address {private_ip}")

        # Mark addresses as unassigning and simulate draining
        for private_ip in private_ip_addresses:
            addr = addresses_by_private_ip[private_ip]
            addr.status = NatGatewayAddressStatus.UNASSIGNING
            # In a real implementation, would start draining connections here
            # For emulator, we simulate immediate success after max_drain_duration_seconds
            # But since this is a synchronous call, we simulate immediate removal
            # Remove the address from natGatewayAddressSet after draining
        # Remove addresses after draining simulation
        nat_gateway.natGatewayAddressSet = [
            addr for addr in nat_gateway.natGatewayAddressSet if addr.privateIp not in private_ip_addresses
        ]

        # Prepare response
        response_addresses = [addr.to_dict() for addr in nat_gateway.natGatewayAddressSet]

        return {
            "natGatewayAddressSet": response_addresses,
            "natGatewayId": nat_gateway_id,
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class NATgatewaysGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssignPrivateNatGatewayAddress", self.assign_private_nat_gateway_address)
        self.register_action("AssociateNatGatewayAddress", self.associate_nat_gateway_address)
        self.register_action("CreateNatGateway", self.create_nat_gateway)
        self.register_action("DeleteNatGateway", self.delete_nat_gateway)
        self.register_action("DescribeNatGateways", self.describe_nat_gateways)
        self.register_action("DisassociateNatGatewayAddress", self.disassociate_nat_gateway_address)
        self.register_action("UnassignPrivateNatGatewayAddress", self.unassign_private_nat_gateway_address)

    def assign_private_nat_gateway_address(self, params):
        return self.backend.assign_private_nat_gateway_address(params)

    def associate_nat_gateway_address(self, params):
        return self.backend.associate_nat_gateway_address(params)

    def create_nat_gateway(self, params):
        return self.backend.create_nat_gateway(params)

    def delete_nat_gateway(self, params):
        return self.backend.delete_nat_gateway(params)

    def describe_nat_gateways(self, params):
        return self.backend.describe_nat_gateways(params)

    def disassociate_nat_gateway_address(self, params):
        return self.backend.disassociate_nat_gateway_address(params)

    def unassign_private_nat_gateway_address(self, params):
        return self.backend.unassign_private_nat_gateway_address(params)
