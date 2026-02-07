from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class SubnetCidrBlockStateCode(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"
    FAILING = "failing"
    FAILED = "failed"


@dataclass
class SubnetCidrBlockState:
    state: Optional[SubnetCidrBlockStateCode] = None
    status_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.state:
            d["State"] = self.state.value
        if self.status_message:
            d["StatusMessage"] = self.status_message
        return d


class IpSource(str, Enum):
    AMAZON = "amazon"
    BYOIP = "byoip"
    NONE = "none"


class Ipv6AddressAttribute(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class SubnetIpv6CidrBlockAssociation:
    association_id: Optional[str] = None
    ip_source: Optional[IpSource] = None
    ipv6_address_attribute: Optional[Ipv6AddressAttribute] = None
    ipv6_cidr_block: Optional[str] = None
    ipv6_cidr_block_state: Optional[SubnetCidrBlockState] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.association_id:
            d["AssociationId"] = self.association_id
        if self.ip_source:
            d["IpSource"] = self.ip_source.value
        if self.ipv6_address_attribute:
            d["Ipv6AddressAttribute"] = self.ipv6_address_attribute.value
        if self.ipv6_cidr_block:
            d["Ipv6CidrBlock"] = self.ipv6_cidr_block
        if self.ipv6_cidr_block_state:
            d["Ipv6CidrBlockState"] = self.ipv6_cidr_block_state.to_dict()
        return d


class BlockPublicAccessMode(str, Enum):
    OFF = "off"
    BLOCK_BIDIRECTIONAL = "block-bidirectional"
    BLOCK_INGRESS = "block-ingress"


@dataclass
class BlockPublicAccessStates:
    internet_gateway_block_mode: Optional[BlockPublicAccessMode] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.internet_gateway_block_mode:
            d["InternetGatewayBlockMode"] = self.internet_gateway_block_mode.value
        return d


class PrivateDnsHostnameType(str, Enum):
    IP_NAME = "ip-name"
    RESOURCE_NAME = "resource-name"


@dataclass
class PrivateDnsNameOptionsOnLaunch:
    enable_resource_name_dns_aaaa_record: Optional[bool] = None
    enable_resource_name_dns_a_record: Optional[bool] = None
    hostname_type: Optional[PrivateDnsHostnameType] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.enable_resource_name_dns_aaaa_record is not None:
            d["EnableResourceNameDnsAAAARecord"] = self.enable_resource_name_dns_aaaa_record
        if self.enable_resource_name_dns_a_record is not None:
            d["EnableResourceNameDnsARecord"] = self.enable_resource_name_dns_a_record
        if self.hostname_type:
            d["HostnameType"] = self.hostname_type.value
        return d


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class Subnet:
    subnet_id: Optional[str] = None
    subnet_arn: Optional[str] = None
    state: Optional[ResourceState] = None
    owner_id: Optional[str] = None
    vpc_id: Optional[str] = None
    cidr_block: Optional[str] = None
    ipv6_cidr_block_association_set: List[SubnetIpv6CidrBlockAssociation] = field(default_factory=list)
    available_ip_address_count: Optional[int] = None
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    default_for_az: Optional[bool] = None
    map_public_ip_on_launch: Optional[bool] = None
    assign_ipv6_address_on_creation: Optional[bool] = None
    block_public_access_states: Optional[BlockPublicAccessStates] = None
    customer_owned_ipv4_pool: Optional[str] = None
    enable_dns64: Optional[bool] = None
    enable_lni_at_device_index: Optional[int] = None
    ipv6_native: Optional[bool] = None
    map_customer_owned_ip_on_launch: Optional[bool] = None
    outpost_arn: Optional[str] = None
    private_dns_name_options_on_launch: Optional[PrivateDnsNameOptionsOnLaunch] = None
    tag_set: List[Tag] = field(default_factory=list)
    type: Optional[str] = None  # e.g. "Elastic VMware Service"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.assign_ipv6_address_on_creation is not None:
            d["AssignIpv6AddressOnCreation"] = self.assign_ipv6_address_on_creation
        if self.availability_zone is not None:
            d["AvailabilityZone"] = self.availability_zone
        if self.availability_zone_id is not None:
            d["AvailabilityZoneId"] = self.availability_zone_id
        if self.available_ip_address_count is not None:
            d["AvailableIpAddressCount"] = self.available_ip_address_count
        if self.block_public_access_states is not None:
            d["BlockPublicAccessStates"] = self.block_public_access_states.to_dict()
        if self.cidr_block is not None:
            d["CidrBlock"] = self.cidr_block
        if self.customer_owned_ipv4_pool is not None:
            d["CustomerOwnedIpv4Pool"] = self.customer_owned_ipv4_pool
        if self.default_for_az is not None:
            d["DefaultForAz"] = self.default_for_az
        if self.enable_dns64 is not None:
            d["EnableDns64"] = self.enable_dns64
        if self.enable_lni_at_device_index is not None:
            d["EnableLniAtDeviceIndex"] = self.enable_lni_at_device_index
        if self.ipv6_cidr_block_association_set:
            d["Ipv6CidrBlockAssociationSet"] = [assoc.to_dict() for assoc in self.ipv6_cidr_block_association_set]
        else:
            d["Ipv6CidrBlockAssociationSet"] = []
        if self.ipv6_native is not None:
            d["Ipv6Native"] = self.ipv6_native
        if self.map_customer_owned_ip_on_launch is not None:
            d["MapCustomerOwnedIpOnLaunch"] = self.map_customer_owned_ip_on_launch
        if self.map_public_ip_on_launch is not None:
            d["MapPublicIpOnLaunch"] = self.map_public_ip_on_launch
        if self.outpost_arn is not None:
            d["OutpostArn"] = self.outpost_arn
        if self.owner_id is not None:
            d["OwnerId"] = self.owner_id
        if self.private_dns_name_options_on_launch is not None:
            d["PrivateDnsNameOptionsOnLaunch"] = self.private_dns_name_options_on_launch.to_dict()
        if self.state is not None:
            d["State"] = self.state.value
        if self.subnet_arn is not None:
            d["SubnetArn"] = self.subnet_arn
        if self.subnet_id is not None:
            d["SubnetId"] = self.subnet_id
        if self.tag_set:
            d["TagSet"] = [tag.to_dict() for tag in self.tag_set]
        else:
            d["TagSet"] = []
        if self.type is not None:
            d["Type"] = self.type
        if self.vpc_id is not None:
            d["VpcId"] = self.vpc_id
        return d


class ReservationType(str, Enum):
    PREFIX = "prefix"
    EXPLICIT = "explicit"


@dataclass
class SubnetCidrReservation:
    cidr: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    reservation_type: Optional[ReservationType] = None
    subnet_cidr_reservation_id: Optional[str] = None
    subnet_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.cidr is not None:
            d["Cidr"] = self.cidr
        if self.description is not None:
            d["Description"] = self.description
        if self.owner_id is not None:
            d["OwnerId"] = self.owner_id
        if self.reservation_type is not None:
            d["ReservationType"] = self.reservation_type.value
        if self.subnet_cidr_reservation_id is not None:
            d["SubnetCidrReservationId"] = self.subnet_cidr_reservation_id
        if self.subnet_id is not None:
            d["SubnetId"] = self.subnet_id
        if self.tag_set:
            d["TagSet"] = [tag.to_dict() for tag in self.tag_set]
        else:
            d["TagSet"] = []
        return d


@dataclass
class AttributeBooleanValue:
    value: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.value} if self.value is not None else {}


class SubnetsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.subnets, self.state.subnet_cidr_reservations, etc.

    def _validate_cidr_block(self, cidr_block: str, min_prefix: int = 16, max_prefix: int = 28) -> bool:
        """Validate IPv4 CIDR block format and prefix length."""
        import re
        cidr_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$'
        match = re.match(cidr_pattern, cidr_block)
        if not match:
            raise ValueError(f"InvalidParameterValue: Value ({cidr_block}) for parameter cidrBlock is invalid.")

        octets = [int(match.group(i)) for i in range(1, 5)]
        for octet in octets:
            if octet < 0 or octet > 255:
                raise ValueError(f"InvalidParameterValue: Value ({cidr_block}) for parameter cidrBlock is invalid.")

        prefix_len = int(match.group(5))
        if prefix_len < min_prefix or prefix_len > max_prefix:
            raise ValueError(f"InvalidParameterValue: The CIDR block {cidr_block} has an invalid prefix length. Must be /{min_prefix} to /{max_prefix}.")

        return True

    def _cidr_contains(self, vpc_cidr: str, subnet_cidr: str) -> bool:
        """Check if subnet CIDR is within VPC CIDR range."""
        import ipaddress
        try:
            vpc_net = ipaddress.ip_network(vpc_cidr, strict=False)
            subnet_net = ipaddress.ip_network(subnet_cidr, strict=False)
            return subnet_net.subnet_of(vpc_net)
        except Exception:
            return False

    def associate_subnet_cidr_block(self, params: dict) -> dict:
        subnet_id = params.get("SubnetId")
        ipv6_cidr_block = params.get("Ipv6CidrBlock")
        ipv6_ipam_pool_id = params.get("Ipv6IpamPoolId")
        ipv6_netmask_length = params.get("Ipv6NetmaskLength")

        if not subnet_id:
            raise ValueError("SubnetId is required")

        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            raise ValueError(f"Subnet {subnet_id} does not exist")

        # Only one IPv6 CIDR block can be associated with a subnet
        if subnet.ipv6_cidr_block_association_set:
            raise ValueError("Subnet already has an associated IPv6 CIDR block")

        # Create association ID
        association_id = f"subnet-cidr-assoc-{self.generate_unique_id()}"

        # Determine ip_source and ipv6_address_attribute based on input
        ip_source = None
        if ipv6_ipam_pool_id:
            ip_source = IpSource.AMAZON  # Assuming IPAM pool means Amazon allocated
        elif ipv6_cidr_block:
            ip_source = IpSource.NONE  # Private space

        ipv6_address_attribute = None
        # For simplicity, assume public if ip_source is amazon, else private
        if ip_source == IpSource.AMAZON:
            ipv6_address_attribute = Ipv6AddressAttribute.PUBLIC
        elif ip_source == IpSource.NONE:
            ipv6_address_attribute = Ipv6AddressAttribute.PRIVATE

        # Create CIDR block state
        cidr_block_state = SubnetCidrBlockState(
            state=SubnetCidrBlockStateCode.ASSOCIATING,
            status_message=None,
        )

        association = SubnetIpv6CidrBlockAssociation(
            association_id=association_id,
            ip_source=ip_source,
            ipv6_address_attribute=ipv6_address_attribute,
            ipv6_cidr_block=ipv6_cidr_block,
            ipv6_cidr_block_state=cidr_block_state,
        )

        subnet.ipv6_cidr_block_association_set.append(association)

        # Return response dict
        return {
            "ipv6CidrBlockAssociation": association.to_dict(),
            "requestId": self.generate_request_id(),
            "subnetId": subnet_id,
        }


    def create_default_subnet(self, params: dict) -> dict:
        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")
        dry_run = params.get("DryRun", False)
        ipv6_native = params.get("Ipv6Native", False)

        # Validate that either AvailabilityZone or AvailabilityZoneId is specified, but not both
        if (availability_zone and availability_zone_id) or (not availability_zone and not availability_zone_id):
            raise ValueError("Either AvailabilityZone or AvailabilityZoneId must be specified, but not both")

        # DryRun check (not implemented, just raise error if dry_run True)
        if dry_run:
            # For simplicity, assume user has permission
            raise Exception("DryRunOperation")

        # Find default VPC
        default_vpc = None
        for vpc in self.state.vpcs.values():
            if getattr(vpc, "is_default", False):
                default_vpc = vpc
                break
        if not default_vpc:
            raise ValueError("No default VPC found")

        # Check if default subnet already exists in the AZ
        for subnet in self.state.subnets.values():
            if subnet.vpc_id == default_vpc.vpc_id:
                if availability_zone and subnet.availability_zone == availability_zone and getattr(subnet, "default_for_az", False):
                    raise ValueError(f"Default subnet already exists in Availability Zone {availability_zone}")
                if availability_zone_id and subnet.availability_zone_id == availability_zone_id and getattr(subnet, "default_for_az", False):
                    raise ValueError(f"Default subnet already exists in Availability Zone ID {availability_zone_id}")

        # Create subnet ID and ARN
        subnet_id = f"subnet-{self.generate_unique_id()}"
        subnet_arn = f"arn:aws:ec2:us-east-1:{self.get_owner_id()}:subnet/{subnet_id}"

        # Determine AZ and AZ ID
        az = availability_zone if availability_zone else None
        az_id = availability_zone_id if availability_zone_id else None

        # Create subnet with /20 CIDR block in default VPC
        # For simplicity, assign a dummy CIDR block (e.g. 172.31.32.0/20)
        cidr_block = "172.31.32.0/20"

        subnet = Subnet(
            subnet_id=subnet_id,
            subnet_arn=subnet_arn,
            state=ResourceState.AVAILABLE,
            owner_id=self.get_owner_id(),
            vpc_id=default_vpc.vpc_id,
            cidr_block=cidr_block,
            ipv6_cidr_block_association_set=[],
            available_ip_address_count=4091,  # 4096 - 5 reserved addresses
            availability_zone=az,
            availability_zone_id=az_id,
            default_for_az=True,
            map_public_ip_on_launch=True,
            assign_ipv6_address_on_creation=False,
            block_public_access_states=None,
            customer_owned_ipv4_pool=None,
            enable_dns64=None,
            enable_lni_at_device_index=None,
            ipv6_native=ipv6_native,
            map_customer_owned_ip_on_launch=None,
            outpost_arn=None,
            private_dns_name_options_on_launch=None,
            tag_set=[],
            type=None,
        )

        self.state.subnets[subnet_id] = subnet
        # self.state.resources[subnet_id] = subnet

        return {
            "requestId": self.generate_request_id(),
            "subnet": subnet.to_dict(),
        }


    def create_subnet(self, params: dict) -> dict:
        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")
        cidr_block = params.get("CidrBlock")
        dry_run = params.get("DryRun", False)
        ipv4_ipam_pool_id = params.get("Ipv4IpamPoolId")
        ipv4_netmask_length = params.get("Ipv4NetmaskLength")
        ipv6_cidr_block = params.get("Ipv6CidrBlock")
        ipv6_ipam_pool_id = params.get("Ipv6IpamPoolId")
        ipv6_native = params.get("Ipv6Native", False)
        ipv6_netmask_length = params.get("Ipv6NetmaskLength")
        outpost_arn = params.get("OutpostArn")
        tag_specifications = params.get("TagSpecification.N", [])
        vpc_id = params.get("VpcId")

        if not vpc_id:
            raise ValueError("VpcId is required")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # DryRun check (not implemented, just raise error if dry_run True)
        if dry_run:
            # For simplicity, assume user has permission
            raise Exception("DryRunOperation")

        # Validate that either AvailabilityZone or AvailabilityZoneId is specified, or neither
        if availability_zone and availability_zone_id:
            raise ValueError("Specify either AvailabilityZone or AvailabilityZoneId, not both")

        # Validate CIDR block presence for IPv4 or IPv6 (unless Ipv6Native is True)
        if not cidr_block and not ipv6_cidr_block and not ipv6_native:
            raise ValueError("At least one of CidrBlock, Ipv6CidrBlock, or Ipv6Native must be specified")

        # Validate CIDR block format (subnets can be /16 to /28)
        if cidr_block:
            self._validate_cidr_block(cidr_block, min_prefix=16, max_prefix=28)

            # Validate subnet CIDR is within VPC CIDR range
            vpc_cidr = getattr(vpc, "cidrBlock", None)
            if vpc_cidr and not self._cidr_contains(vpc_cidr, cidr_block):
                raise ValueError(f"InvalidSubnet.Conflict: The CIDR '{cidr_block}' is outside the VPC CIDR block '{vpc_cidr}'")

            # Check for CIDR overlap with existing subnets in the VPC
            for existing_subnet in self.state.subnets.values():
                if getattr(existing_subnet, "vpc_id", None) == vpc_id:
                    existing_cidr = getattr(existing_subnet, "cidr_block", None)
                    if existing_cidr:
                        import ipaddress
                        try:
                            new_net = ipaddress.ip_network(cidr_block, strict=False)
                            existing_net = ipaddress.ip_network(existing_cidr, strict=False)
                            if new_net.overlaps(existing_net):
                                raise ValueError(f"InvalidSubnet.Conflict: The CIDR '{cidr_block}' conflicts with another subnet's CIDR in the VPC")
                        except Exception:
                            pass

        # Create subnet ID and ARN
        subnet_id = f"subnet-{self.generate_unique_id()}"
        subnet_arn = f"arn:aws:ec2:us-east-1:{self.get_owner_id()}:subnet/{subnet_id}"

        # Prepare IPv6 CIDR block association set
        ipv6_cidr_block_association_set = []
        if ipv6_cidr_block:
            association_id = f"subnet-cidr-assoc-{self.generate_unique_id()}"
            cidr_block_state = SubnetCidrBlockState(
                state=SubnetCidrBlockStateCode.ASSOCIATED,
                status_message=None,
            )
            association = SubnetIpv6CidrBlockAssociation(
                association_id=association_id,
                ip_source="amazon" if ipv6_ipam_pool_id else "none",
                ipv6_address_attribute="public" if ipv6_ipam_pool_id else "private",
                ipv6_cidr_block=ipv6_cidr_block,
                ipv6_cidr_block_state=cidr_block_state,
            )
            ipv6_cidr_block_association_set.append(association)

        # Parse tags from tag_specifications
        tag_set = []
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and value:
                    tag_set.append(Tag(Key=key, Value=value))

        # Determine availability zone and id
        az = availability_zone if availability_zone else None
        az_id = availability_zone_id if availability_zone_id else None

        # Calculate available IP address count
        # For simplicity, assume /24 CIDR block if cidr_block is given, else 0
        available_ip_address_count = 251  # 256 - 5 reserved addresses for /24

        subnet = Subnet(
            subnet_id=subnet_id,
            subnet_arn=subnet_arn,
            state=ResourceState.AVAILABLE,  # LocalStack: Subnets are immediately available
            owner_id=self.get_owner_id(),
            vpc_id=vpc_id,
            cidr_block=cidr_block,
            ipv6_cidr_block_association_set=ipv6_cidr_block_association_set,
            available_ip_address_count=available_ip_address_count,
            availability_zone=az,
            availability_zone_id=az_id,
            default_for_az=False,
            map_public_ip_on_launch=False,
            assign_ipv6_address_on_creation=False,
            block_public_access_states=None,
            customer_owned_ipv4_pool=None,
            enable_dns64=False,  # LocalStack: EnableDns64 defaults to False
            enable_lni_at_device_index=None,
            ipv6_native=ipv6_native,
            map_customer_owned_ip_on_launch=None,
            outpost_arn=outpost_arn,
            private_dns_name_options_on_launch=PrivateDnsNameOptionsOnLaunch(
                hostname_type=PrivateDnsHostnameType.IP_NAME,
                enable_resource_name_dns_a_record=False,
                enable_resource_name_dns_aaaa_record=False,
            ),  # LocalStack: Default private DNS options
            tag_set=tag_set,
            type=None,
        )

        self.state.subnets[subnet_id] = subnet
        self.state.resources[subnet_id] = subnet

        # Associate subnet with default Network ACL for the VPC
        if hasattr(self.state, "network_acls"):
            for nacl_id, nacl in self.state.network_acls.items():
                nacl_vpc_id = getattr(nacl, "vpcId", None) or getattr(nacl, "vpc_id", None)
                is_default = getattr(nacl, "isDefault", False) or getattr(nacl, "default", False)
                if nacl_vpc_id == vpc_id and is_default:
                    # Create association
                    from emulator_core.services.network_acls import NetworkAclAssociation
                    assoc_id = f"aclassoc-{self.generate_unique_id()}"
                    association = NetworkAclAssociation(
                        network_acl_association_id=assoc_id,
                        network_acl_id=nacl_id,
                        subnet_id=subnet_id,
                    )
                    # Add to NACL's association set
                    if hasattr(nacl, "association_set"):
                        nacl.association_set.append(association)
                    elif hasattr(nacl, "associations"):
                        nacl.associations.append(association)
                    break

        return {
            "requestId": self.generate_request_id(),
            "subnet": subnet.to_dict(),
        }


    def create_subnet_cidr_reservation(self, params: dict) -> dict:
        cidr = params.get("Cidr")
        description = params.get("Description")
        dry_run = params.get("DryRun", False)
        reservation_type_str = params.get("ReservationType")
        subnet_id = params.get("SubnetId")
        tag_specifications = params.get("TagSpecification.N", [])

        if not cidr:
            raise ValueError("Cidr is required")
        if not reservation_type_str:
            raise ValueError("ReservationType is required")
        if not subnet_id:
            raise ValueError("SubnetId is required")

        # DryRun check (not implemented, just raise error if dry_run True)
        if dry_run:
            # For simplicity, assume user has permission
            raise Exception("DryRunOperation")

        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            raise ValueError(f"Subnet {subnet_id} does not exist")

        # Validate reservation type enum
        try:
            reservation_type = ReservationType[reservation_type_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid ReservationType: {reservation_type_str}")

        # Create subnet CIDR reservation ID
        subnet_cidr_reservation_id = f"subnet-cidr-reservation-{self.generate_unique_id()}"

        # Parse tags from tag_specifications
        tag_set = []
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and value:
                    tag_set.append(Tag(Key=key, Value=value))

        reservation = SubnetCidrReservation(
            cidr=cidr,
            description=description,
            owner_id=self.get_owner_id(),
            reservation_type=reservation_type,
            subnet_cidr_reservation_id=subnet_cidr_reservation_id,
            subnet_id=subnet_id,
            tag_set=tag_set,
        )

        # Store reservation in state resources keyed by reservation id
        self.state.resources[subnet_cidr_reservation_id] = reservation

        return {
            "requestId": self.generate_request_id(),
            "subnetCidrReservation": reservation.to_dict(),
        }


    def delete_subnet(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        subnet_id = params.get("SubnetId")

        if not subnet_id:
            raise ValueError("SubnetId is required")

        # DryRun check (not implemented, just raise error if dry_run True)
        if dry_run:
            # For simplicity, assume user has permission
            raise Exception("DryRunOperation")

        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            # According to AWS behavior, deleting a non-existent subnet returns success (idempotent)
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Check if subnet has running instances
        if hasattr(self.state, "instances"):
            for instance in self.state.instances.values():
                if hasattr(instance, "subnet_id") and instance.subnet_id == subnet_id:
                    instance_state = getattr(instance, "state", None)
                    if instance_state and instance_state.value not in ["terminated", "shutting-down"]:
                        raise ValueError(f"DependencyViolation: The subnet {subnet_id} has dependencies and cannot be deleted")

        # Check if subnet has network interfaces
        if hasattr(self.state, "network_interfaces"):
            for eni in self.state.network_interfaces.values():
                if hasattr(eni, "subnet_id") and eni.subnet_id == subnet_id:
                    eni_state = getattr(eni, "status", None)
                    if eni_state and eni_state.value not in ["available"]:  # Only available ENIs can be deleted
                        raise ValueError(f"DependencyViolation: The subnet {subnet_id} has dependencies and cannot be deleted")

        # Delete subnet from state
        del self.state.subnets[subnet_id]
        if subnet_id in self.state.resources:
            del self.state.resources[subnet_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def delete_subnet_cidr_reservation(self, params: dict) -> dict:
        subnet_cidr_reservation_id = params.get("SubnetCidrReservationId")
        if not subnet_cidr_reservation_id:
            raise ValueError("SubnetCidrReservationId is required")

        # Find the reservation in state
        reservation = self.state.subnet_cidr_reservations.get(subnet_cidr_reservation_id)
        if not reservation:
            # According to AWS behavior, deleting a non-existent reservation returns success with empty deletedSubnetCidrReservation
            deleted_reservation = None
        else:
            # Remove from state
            deleted_reservation = reservation
            del self.state.subnet_cidr_reservations[subnet_cidr_reservation_id]

        response = {
            "requestId": self.generate_request_id(),
            "deletedSubnetCidrReservation": deleted_reservation.to_dict() if deleted_reservation else {},
        }
        return response


    def describe_subnets(self, params: dict) -> dict:
        # Extract filters and subnet IDs
        filters = []
        # Filters come as Filter.N.Name and Filter.N.Value.M keys
        # Collect filters from params keys
        for key, value in params.items():
            if key.startswith("Filter."):
                # key format: Filter.N.Name or Filter.N.Value.M
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    # Find or create filter dict
                    while len(filters) < int(filter_index):
                        filters.append({"Name": None, "Values": []})
                    if filter_key == "Name":
                        filters[int(filter_index) - 1]["Name"] = value
                    elif filter_key == "Value":
                        filters[int(filter_index) - 1]["Values"].append(value)

        # SubnetId.N keys
        subnet_ids = []
        for key, value in params.items():
            if key.startswith("SubnetId."):
                subnet_ids.append(value)

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None

        next_token = params.get("NextToken")
        # For simplicity, we do not implement pagination token logic here, just ignore next_token

        # Start with all subnets
        subnets = list(self.state.subnets.values())

        # Filter by subnet IDs if provided
        if subnet_ids:
            subnets = [s for s in subnets if s.subnet_id in subnet_ids]

        # Apply filters
        def match_filter(subnet, filter_name, filter_values):
            # Normalize filter name to lower and remove dashes for matching
            name = filter_name.lower()
            vals = set(filter_values)
            # Map filter names to subnet attributes or special handling
            if name in ("availability-zone", "availabilityzone"):
                return subnet.availability_zone in vals
            if name in ("availability-zone-id", "availabilityzoneid"):
                return subnet.availability_zone_id in vals
            if name in ("available-ip-address-count",):
                # Convert to string for comparison
                return str(subnet.available_ip_address_count) in vals
            if name in ("cidr-block", "cidr", "cidrblock"):
                return subnet.cidr_block in vals
            if name == "customer-owned-ipv4-pool":
                return subnet.customer_owned_ipv4_pool in vals
            if name in ("default-for-az", "defaultforaz"):
                # Boolean filter, values are strings "true" or "false"
                return str(subnet.default_for_az).lower() in vals
            if name == "enable-dns64":
                return str(subnet.enable_dns64).lower() in vals
            if name == "enable-lni-at-device-index":
                return str(subnet.enable_lni_at_device_index) in vals
            if name == "ipv6-cidr-block-association.ipv6-cidr-block":
                # Check if any ipv6 cidr block association matches
                for assoc in subnet.ipv6_cidr_block_association_set:
                    if assoc.ipv6_cidr_block in vals:
                        return True
                return False
            if name == "ipv6-cidr-block-association.association-id":
                for assoc in subnet.ipv6_cidr_block_association_set:
                    if assoc.association_id in vals:
                        return True
                return False
            if name == "ipv6-cidr-block-association.state":
                for assoc in subnet.ipv6_cidr_block_association_set:
                    if assoc.ipv6_cidr_block_state and assoc.ipv6_cidr_block_state.state and assoc.ipv6_cidr_block_state.state.value in vals:
                        return True
                return False
            if name == "ipv6-native":
                return str(subnet.ipv6_native).lower() in vals
            if name == "map-customer-owned-ip-on-launch":
                return str(subnet.map_customer_owned_ip_on_launch).lower() in vals
            if name == "map-public-ip-on-launch":
                return str(subnet.map_public_ip_on_launch).lower() in vals
            if name == "outpost-arn":
                return subnet.outpost_arn in vals
            if name == "owner-id":
                return subnet.owner_id in vals
            if name == "private-dns-name-options-on-launch.hostname-type":
                if subnet.private_dns_name_options_on_launch and subnet.private_dns_name_options_on_launch.hostname_type:
                    return subnet.private_dns_name_options_on_launch.hostname_type.value in vals
                return False
            if name == "private-dns-name-options-on-launch.enable-resource-name-dns-a-record":
                if subnet.private_dns_name_options_on_launch and subnet.private_dns_name_options_on_launch.enable_resource_name_dns_a_record is not None:
                    return str(subnet.private_dns_name_options_on_launch.enable_resource_name_dns_a_record).lower() in vals
                return False
            if name == "private-dns-name-options-on-launch.enable-resource-name-dns-aaaa-record":
                if subnet.private_dns_name_options_on_launch and subnet.private_dns_name_options_on_launch.enable_resource_name_dns_aaaa_record is not None:
                    return str(subnet.private_dns_name_options_on_launch.enable_resource_name_dns_aaaa_record).lower() in vals
                return False
            if name == "state":
                return subnet.state.value in vals
            if name == "subnet-arn":
                return subnet.subnet_arn in vals
            if name == "subnet-id":
                return subnet.subnet_id in vals
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in subnet.tag_set:
                    if tag.Key == tag_key and tag.Value in vals:
                        return True
                return False
            if name == "tag-key":
                for tag in subnet.tag_set:
                    if tag.Key in vals:
                        return True
                return False
            if name == "vpc-id":
                return subnet.vpc_id in vals
            return False

        for f in filters:
            if f["Name"] is None:
                continue
            subnets = [s for s in subnets if match_filter(s, f["Name"], f["Values"])]

        # Pagination: slice results if max_results is set
        if max_results is not None:
            subnets = subnets[:max_results]

        response = {
            "requestId": self.generate_request_id(),
            "subnetSet": [subnet.to_dict() for subnet in subnets],
            "nextToken": None,
        }
        return response


    def disassociate_subnet_cidr_block(self, params: dict) -> dict:
        association_id = params.get("AssociationId")
        if not association_id:
            raise ValueError("AssociationId is required")

        # Find the subnet and association
        found_assoc = None
        found_subnet = None
        for subnet in self.state.subnets.values():
            for assoc in subnet.ipv6_cidr_block_association_set:
                if assoc.association_id == association_id:
                    found_assoc = assoc
                    found_subnet = subnet
                    break
            if found_assoc:
                break

        if not found_assoc:
            # According to AWS, if association not found, error or empty response? We'll raise error
            raise ValueError(f"AssociationId {association_id} not found")

        # Mark the association state as disassociating
        found_assoc.ipv6_cidr_block_state = SubnetCidrBlockState(state=SubnetCidrBlockStateCode.DISASSOCIATING, status_message=None)

        response = {
            "requestId": self.generate_request_id(),
            "subnetId": found_subnet.subnet_id,
            "ipv6CidrBlockAssociation": found_assoc.to_dict(),
        }
        return response


    def get_subnet_cidr_reservations(self, params: dict) -> dict:
        subnet_id = params.get("SubnetId")
        if not subnet_id:
            raise ValueError("SubnetId is required")

        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    while len(filters) < int(filter_index):
                        filters.append({"Name": None, "Values": []})
                    if filter_key == "Name":
                        filters[int(filter_index) - 1]["Name"] = value
                    elif filter_key == "Value":
                        filters[int(filter_index) - 1]["Values"].append(value)

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None

        next_token = params.get("NextToken")
        # For simplicity, ignore next_token pagination

        # Filter reservations by subnet_id
        reservations = [r for r in self.state.subnet_cidr_reservations.values() if r.subnet_id == subnet_id]

        def match_filter(reservation, filter_name, filter_values):
            name = filter_name.lower()
            vals = set(filter_values)
            if name == "reservationtype":
                if reservation.reservation_type:
                    return reservation.reservation_type.value in vals
                return False
            if name == "subnet-id":
                return reservation.subnet_id in vals
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in reservation.tag_set:
                    if tag.Key == tag_key and tag.Value in vals:
                        return True
                return False
            if name == "tag-key":
                for tag in reservation.tag_set:
                    if tag.Key in vals:
                        return True
                return False
            return False

        for f in filters:
            if f["Name"] is None:
                continue
            reservations = [r for r in reservations if match_filter(r, f["Name"], f["Values"])]

        if max_results is not None:
            reservations = reservations[:max_results]

        # Separate IPv4 and IPv6 reservations
        subnet_ipv4_reservations = [r for r in reservations if r.cidr and ":" not in r.cidr]
        subnet_ipv6_reservations = [r for r in reservations if r.cidr and ":" in r.cidr]

        response = {
            "requestId": self.generate_request_id(),
            "nextToken": None,
            "subnetIpv4CidrReservationSet": [r.to_dict() for r in subnet_ipv4_reservations],
            "subnetIpv6CidrReservationSet": [r.to_dict() for r in subnet_ipv6_reservations],
        }
        return response


    def modify_subnet_attribute(self, params: dict) -> dict:
        subnet_id = params.get("SubnetId")
        if not subnet_id:
            raise ValueError("SubnetId is required")

        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            raise ValueError(f"Subnet {subnet_id} not found")

        # Helper to extract boolean from AttributeBooleanValue object
        def get_bool(attr):
            if not attr:
                return None
            if isinstance(attr, dict):
                return attr.get("Value")
            if hasattr(attr, "value"):
                return attr.value
            return None

        # AssignIpv6AddressOnCreation
        assign_ipv6 = get_bool(params.get("AssignIpv6AddressOnCreation"))
        if assign_ipv6 is not None:
            # Validate that subnet has IPv6 CIDR block if enabling AssignIpv6AddressOnCreation
            if assign_ipv6 and not subnet.ipv6_cidr_block_association_set:
                raise ValueError("AssignIpv6AddressOnCreation can only be enabled if the subnet has an IPv6 CIDR block")
            subnet.assign_ipv6_address_on_creation = assign_ipv6

        # CustomerOwnedIpv4Pool
        customer_owned_pool = params.get("CustomerOwnedIpv4Pool")
        if customer_owned_pool is not None:
            subnet.customer_owned_ipv4_pool = customer_owned_pool

        # DisableLniAtDeviceIndex
        disable_lni = get_bool(params.get("DisableLniAtDeviceIndex"))
        if disable_lni is not None:
            # The param is boolean, but the attribute is int index or None
            # If true, disable local network interfaces at device index (set enable_lni_at_device_index to None)
            if disable_lni:
                subnet.enable_lni_at_device_index = None
            else:
                # If false, no change or set to 0? AWS doc unclear, so no change
                pass

        # EnableDns64
        enable_dns64 = get_bool(params.get("EnableDns64"))
        if enable_dns64 is not None:
            subnet.enable_dns64 = enable_dns64

        # EnableLniAtDeviceIndex (integer)
        enable_lni_index = params.get("EnableLniAtDeviceIndex")
        if enable_lni_index is not None:
            try:
                enable_lni_index_int = int(enable_lni_index)
                subnet.enable_lni_at_device_index = enable_lni_index_int
            except Exception:
                pass

        # EnableResourceNameDnsAAAARecordOnLaunch
        enable_aaaa = get_bool(params.get("EnableResourceNameDnsAAAARecordOnLaunch"))
        # EnableResourceNameDnsARecordOnLaunch
        enable_a = get_bool(params.get("EnableResourceNameDnsARecordOnLaunch"))

        # MapCustomerOwnedIpOnLaunch
        map_customer_owned = get_bool(params.get("MapCustomerOwnedIpOnLaunch"))
        if map_customer_owned is not None:
            subnet.map_customer_owned_ip_on_launch = map_customer_owned

        # MapPublicIpOnLaunch
        map_public_ip = get_bool(params.get("MapPublicIpOnLaunch"))
        if map_public_ip is not None:
            subnet.map_public_ip_on_launch = map_public_ip

        # PrivateDnsHostnameTypeOnLaunch
        private_dns_type = params.get("PrivateDnsHostnameTypeOnLaunch")
        if private_dns_type is not None:
            # Create or update private_dns_name_options_on_launch
            if subnet.private_dns_name_options_on_launch is None:
                subnet.private_dns_name_options_on_launch = PrivateDnsNameOptionsOnLaunch()
            # Assign enum if possible, else string
            # Assuming PrivateDnsHostnameType is an enum, try to assign enum member
            try:
                # If enum has member with this name
                enum_member = PrivateDnsHostnameType(private_dns_type)
                subnet.private_dns_name_options_on_launch.hostname_type = enum_member
            except Exception:
                subnet.private_dns_name_options_on_launch.hostname_type = private_dns_type

        # Update enable_resource_name_dns_aaaa_record and enable_resource_name_dns_a_record if provided
        if enable_aaaa is not None or enable_a is not None:
            if subnet.private_dns_name_options_on_launch is None:
                subnet.private_dns_name_options_on_launch = PrivateDnsNameOptionsOnLaunch()
            if enable_aaaa is not None:
                subnet.private_dns_name_options_on_launch.enable_resource_name_dns_aaaa_record = enable_aaaa
            if enable_a is not None:
                subnet.private_dns_name_options_on_launch.enable_resource_name_dns_a_record = enable_a

        response = {
            "requestId": self.generate_request_id(),
            "return": True,
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class SubnetsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateSubnetCidrBlock", self.associate_subnet_cidr_block)
        self.register_action("CreateDefaultSubnet", self.create_default_subnet)
        self.register_action("CreateSubnet", self.create_subnet)
        self.register_action("CreateSubnetCidrReservation", self.create_subnet_cidr_reservation)
        self.register_action("DeleteSubnet", self.delete_subnet)
        self.register_action("DeleteSubnetCidrReservation", self.delete_subnet_cidr_reservation)
        self.register_action("DescribeSubnets", self.describe_subnets)
        self.register_action("DisassociateSubnetCidrBlock", self.disassociate_subnet_cidr_block)
        self.register_action("GetSubnetCidrReservations", self.get_subnet_cidr_reservations)
        self.register_action("ModifySubnetAttribute", self.modify_subnet_attribute)

    def associate_subnet_cidr_block(self, params):
        return self.backend.associate_subnet_cidr_block(params)

    def create_default_subnet(self, params):
        return self.backend.create_default_subnet(params)

    def create_subnet(self, params):
        return self.backend.create_subnet(params)

    def create_subnet_cidr_reservation(self, params):
        return self.backend.create_subnet_cidr_reservation(params)

    def delete_subnet(self, params):
        return self.backend.delete_subnet(params)

    def delete_subnet_cidr_reservation(self, params):
        return self.backend.delete_subnet_cidr_reservation(params)

    def describe_subnets(self, params):
        return self.backend.describe_subnets(params)

    def disassociate_subnet_cidr_block(self, params):
        return self.backend.disassociate_subnet_cidr_block(params)

    def get_subnet_cidr_reservations(self, params):
        return self.backend.get_subnet_cidr_reservations(params)

    def modify_subnet_attribute(self, params):
        return self.backend.modify_subnet_attribute(params)
