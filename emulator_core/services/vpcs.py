from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class CidrBlockStateCode(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"
    FAILING = "failing"
    FAILED = "failed"


class InstanceTenancy(str, Enum):
    DEFAULT = "default"
    DEDICATED = "dedicated"
    HOST = "host"


class InternetGatewayBlockMode(str, Enum):
    OFF = "off"
    BLOCK_BIDIRECTIONAL = "block-bidirectional"
    BLOCK_INGRESS = "block-ingress"


class IpSource(str, Enum):
    AMAZON = "amazon"
    BYOIP = "byoip"
    NONE = "none"


class Ipv6AddressAttribute(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class EncryptionControlMode(str, Enum):
    MONITOR = "monitor"
    ENFORCE = "enforce"


class EncryptionControlExclusion(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


@dataclass
class Tag:
    Key: str
    Value: str


@dataclass
class AttributeBooleanValue:
    Value: bool


@dataclass
class VpcCidrBlockState:
    state: Optional[CidrBlockStateCode] = None
    statusMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value if self.state else None,
            "statusMessage": self.statusMessage,
        }


@dataclass
class VpcCidrBlockAssociation:
    associationId: Optional[str] = None
    cidrBlock: Optional[str] = None
    cidrBlockState: Optional[VpcCidrBlockState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "associationId": self.associationId,
            "cidrBlock": self.cidrBlock,
            "cidrBlockState": self.cidrBlockState.to_dict() if self.cidrBlockState else None,
        }


@dataclass
class VpcIpv6CidrBlockAssociation:
    associationId: Optional[str] = None
    ipSource: Optional[IpSource] = None
    ipv6AddressAttribute: Optional[Ipv6AddressAttribute] = None
    ipv6CidrBlock: Optional[str] = None
    ipv6CidrBlockState: Optional[VpcCidrBlockState] = None
    ipv6Pool: Optional[str] = None
    networkBorderGroup: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "associationId": self.associationId,
            "ipSource": self.ipSource.value if self.ipSource else None,
            "ipv6AddressAttribute": self.ipv6AddressAttribute.value if self.ipv6AddressAttribute else None,
            "ipv6CidrBlock": self.ipv6CidrBlock,
            "ipv6CidrBlockState": self.ipv6CidrBlockState.to_dict() if self.ipv6CidrBlockState else None,
            "ipv6Pool": self.ipv6Pool,
            "networkBorderGroup": self.networkBorderGroup,
        }


@dataclass
class BlockPublicAccessStates:
    internetGatewayBlockMode: Optional[InternetGatewayBlockMode] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "internetGatewayBlockMode": self.internetGatewayBlockMode.value if self.internetGatewayBlockMode else None,
        }


@dataclass
class VpcEncryptionControlConfiguration:
    Mode: EncryptionControlMode
    EgressOnlyInternetGatewayExclusion: Optional[EncryptionControlExclusion] = None
    ElasticFileSystemExclusion: Optional[EncryptionControlExclusion] = None
    InternetGatewayExclusion: Optional[EncryptionControlExclusion] = None
    LambdaExclusion: Optional[EncryptionControlExclusion] = None
    NatGatewayExclusion: Optional[EncryptionControlExclusion] = None
    VirtualPrivateGatewayExclusion: Optional[EncryptionControlExclusion] = None
    VpcLatticeExclusion: Optional[EncryptionControlExclusion] = None
    VpcPeeringExclusion: Optional[EncryptionControlExclusion] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Mode": self.Mode.value,
            "EgressOnlyInternetGatewayExclusion": self.EgressOnlyInternetGatewayExclusion.value if self.EgressOnlyInternetGatewayExclusion else None,
            "ElasticFileSystemExclusion": self.ElasticFileSystemExclusion.value if self.ElasticFileSystemExclusion else None,
            "InternetGatewayExclusion": self.InternetGatewayExclusion.value if self.InternetGatewayExclusion else None,
            "LambdaExclusion": self.LambdaExclusion.value if self.LambdaExclusion else None,
            "NatGatewayExclusion": self.NatGatewayExclusion.value if self.NatGatewayExclusion else None,
            "VirtualPrivateGatewayExclusion": self.VirtualPrivateGatewayExclusion.value if self.VirtualPrivateGatewayExclusion else None,
            "VpcLatticeExclusion": self.VpcLatticeExclusion.value if self.VpcLatticeExclusion else None,
            "VpcPeeringExclusion": self.VpcPeeringExclusion.value if self.VpcPeeringExclusion else None,
        }


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.__dict__ for tag in self.Tags],
        }


@dataclass
class Vpc:
    vpcId: str
    cidrBlock: Optional[str] = None
    cidrBlockAssociationSet: List[VpcCidrBlockAssociation] = field(default_factory=list)
    dhcpOptionsId: Optional[str] = None
    instanceTenancy: Optional[InstanceTenancy] = None
    ipv6CidrBlockAssociationSet: List[VpcIpv6CidrBlockAssociation] = field(default_factory=list)
    isDefault: Optional[bool] = None
    ownerId: Optional[str] = None
    state: Optional[ResourceState] = None
    tagSet: List[Tag] = field(default_factory=list)
    blockPublicAccessStates: Optional[BlockPublicAccessStates] = None
    availabilityZone: Optional[str] = None
    encryptionControl: Optional[VpcEncryptionControlConfiguration] = None
    enableDnsSupport: bool = True
    enableDnsHostnames: bool = False
    enableNetworkAddressUsageMetrics: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vpcId": self.vpcId,
            "cidrBlock": self.cidrBlock,
            "cidrBlockAssociationSet": [assoc.to_dict() for assoc in self.cidrBlockAssociationSet],
            "dhcpOptionsId": self.dhcpOptionsId,
            "instanceTenancy": self.instanceTenancy.value if self.instanceTenancy else None,
            "ipv6CidrBlockAssociationSet": [assoc.to_dict() for assoc in self.ipv6CidrBlockAssociationSet],
            "isDefault": self.isDefault,
            "ownerId": self.ownerId,
            "state": self.state.value if self.state else None,
            "tagSet": [tag.__dict__ for tag in self.tagSet],
            "blockPublicAccessStates": self.blockPublicAccessStates.to_dict() if self.blockPublicAccessStates else None,
            "availabilityZone": self.availabilityZone,
            "encryptionControl": self.encryptionControl.to_dict() if self.encryptionControl else None,
            # Attributes are not returned in DescribeVpcs by default, but useful for debugging or if requested specifically?
            # AWS DescribeVpcs does NOT return these attributes in the main object. They are returned by DescribeVpcAttribute.
            # So we don't need to add them here for API compliance, but keeping them on the object is fine.
        }


class VPCsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.vpcs

    def _validate_cidr_block(self, cidr_block: str, min_prefix: int = 16, max_prefix: int = 28) -> bool:
        """Validate IPv4 CIDR block format and prefix length."""
        import re
        # Pattern for IPv4 CIDR
        cidr_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$'
        match = re.match(cidr_pattern, cidr_block)
        if not match:
            raise ValueError(f"InvalidParameterValue: Value ({cidr_block}) for parameter cidrBlock is invalid. This is not a valid CIDR block.")

        # Validate each octet
        octets = [int(match.group(i)) for i in range(1, 5)]
        for octet in octets:
            if octet < 0 or octet > 255:
                raise ValueError(f"InvalidParameterValue: Value ({cidr_block}) for parameter cidrBlock is invalid.")

        # Validate prefix length
        prefix_len = int(match.group(5))
        if prefix_len < min_prefix or prefix_len > max_prefix:
            raise ValueError(f"InvalidParameterValue: The CIDR block {cidr_block} has an invalid prefix length. The prefix length must be between /{min_prefix} and /{max_prefix}.")

        return True

    def associate_vpc_cidr_block(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_id = params.get("VpcId")
        if not vpc_id:
            raise ValueError("VpcId is required")
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # Extract parameters
        amazon_provided_ipv6 = params.get("AmazonProvidedIpv6CidrBlock", False)
        cidr_block = params.get("CidrBlock")
        ipv4_ipam_pool_id = params.get("Ipv4IpamPoolId")
        ipv4_netmask_length = params.get("Ipv4NetmaskLength")
        ipv6_cidr_block = params.get("Ipv6CidrBlock")
        ipv6_cidr_block_network_border_group = params.get("Ipv6CidrBlockNetworkBorderGroup")
        ipv6_ipam_pool_id = params.get("Ipv6IpamPoolId")
        ipv6_netmask_length = params.get("Ipv6NetmaskLength")
        ipv6_pool = params.get("Ipv6Pool")

        # Validate that exactly one of the following is specified:
        # - IPv4 CIDR block (CidrBlock or Ipv4IpamPoolId)
        # - AmazonProvidedIpv6CidrBlock
        # - IPv6 CIDR block (Ipv6CidrBlock or Ipv6Pool or Ipv6IpamPoolId)
        # According to AWS docs, you must specify one of these.

        # Determine if IPv4 or IPv6 association
        is_ipv4 = False
        is_ipv6 = False

        if cidr_block or ipv4_ipam_pool_id:
            is_ipv4 = True
        if amazon_provided_ipv6 or ipv6_cidr_block or ipv6_pool or ipv6_ipam_pool_id:
            is_ipv6 = True

        if is_ipv4 and is_ipv6:
            raise ValueError("Cannot associate both IPv4 and IPv6 CIDR blocks in the same request")
        if not (is_ipv4 or is_ipv6):
            raise ValueError("Must specify either an IPv4 CIDR block or an IPv6 CIDR block or AmazonProvidedIpv6CidrBlock")

        request_id = self.generate_request_id()

        if is_ipv4:
            # For IPv4 CIDR block association
            # Validate CIDR block format if provided
            if cidr_block:
                # Basic validation of CIDR format could be done here, but skipping complex validation
                pass
            # Generate association ID
            association_id = self.generate_unique_id(prefix="vpc-cidr-assoc-")
            cidr_block_state = VpcCidrBlockState(
                state=CidrBlockStateCode.ASSOCIATING,
                statusMessage=None,
            )
            cidr_block_association = VpcCidrBlockAssociation(
                associationId=association_id,
                cidrBlock=cidr_block,
                cidrBlockState=cidr_block_state,
            )
            # Add to VPC's cidrBlockAssociationSet
            vpc.cidrBlockAssociationSet.append(cidr_block_association)
            # If this is the first CIDR block association, set as primary cidrBlock
            if not vpc.cidrBlock:
                vpc.cidrBlock = cidr_block
            # Save updated VPC in state
            self.state.vpcs[vpc_id] = vpc

            return {
                "requestId": request_id,
                "vpcId": vpc_id,
                "cidrBlockAssociation": cidr_block_association.to_dict(),
            }

        else:
            # IPv6 CIDR block association
            association_id = self.generate_unique_id(prefix="vpc-cidr-assoc-")
            ipv6_cidr_block_state = VpcCidrBlockState(
                state=CidrBlockStateCode.ASSOCIATED,
                statusMessage=None,
            )
            # Determine ipSource and ipv6AddressAttribute
            ip_source = IpSource.AMAZON if amazon_provided_ipv6 else IpSource.BYOIP if ipv6_pool or ipv6_ipam_pool_id else IpSource.NONE
            ipv6_address_attribute = Ipv6AddressAttribute.PUBLIC if ip_source in (IpSource.AMAZON, IpSource.BYOIP) else Ipv6AddressAttribute.PRIVATE

            # Generate a fake IPv6 CIDR if amazon-provided and none specified
            resolved_ipv6_cidr = ipv6_cidr_block if ipv6_cidr_block else "2600:1f00::/56"

            ipv6_cidr_block_association = VpcIpv6CidrBlockAssociation(
                associationId=association_id,
                ipSource=ip_source,
                ipv6AddressAttribute=ipv6_address_attribute,
                ipv6CidrBlock=resolved_ipv6_cidr,
                ipv6CidrBlockState=ipv6_cidr_block_state,
                ipv6Pool=ipv6_pool,
                networkBorderGroup=ipv6_cidr_block_network_border_group,
            )
            vpc.ipv6CidrBlockAssociationSet.append(ipv6_cidr_block_association)
            # Save updated VPC in state
            self.state.vpcs[vpc_id] = vpc

            return {
                "requestId": request_id,
                "vpcId": vpc_id,
                "ipv6CidrBlockAssociation": ipv6_cidr_block_association.to_dict(),
            }


    def create_default_vpc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For dry run, raise DryRunOperation error if permissions are sufficient
            # Here we assume permissions are sufficient
            raise Exception("DryRunOperation")

        # Check if default VPC already exists in this region (state.vpcs)
        for vpc in self.state.vpcs.values():
            if vpc.isDefault:
                raise Exception("Default VPC already exists")

        # Create default VPC with /16 CIDR block 172.31.0.0/16
        vpc_id = self.generate_unique_id(prefix="vpc-")
        owner_id = self.get_owner_id()
        cidr_block = "172.31.0.0/16"
        cidr_block_state = VpcCidrBlockState(
            state=CidrBlockStateCode.ASSOCIATED,
            statusMessage=None,
        )
        cidr_block_association = VpcCidrBlockAssociation(
            associationId=self.generate_unique_id(prefix="vpc-cidr-assoc-"),
            cidrBlock=cidr_block,
            cidrBlockState=cidr_block_state,
        )
        vpc = Vpc(
            vpcId=vpc_id,
            cidrBlock=cidr_block,
            cidrBlockAssociationSet=[cidr_block_association],
            dhcpOptionsId=None,
            instanceTenancy=InstanceTenancy.DEFAULT,
            ipv6CidrBlockAssociationSet=[],
            isDefault=True,
            ownerId=owner_id,
            state=ResourceState.PENDING,
            tagSet=[],
            blockPublicAccessStates=None,
            availabilityZone=None,
            encryptionControl=None,
        )
        self.state.vpcs[vpc_id] = vpc

        return {
            "requestId": self.generate_request_id(),
            "vpc": vpc.to_dict(),
        }


    def create_vpc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For dry run, raise DryRunOperation error if permissions are sufficient
            # Here we assume permissions are sufficient
            raise Exception("DryRunOperation")

        cidr_block = params.get("CidrBlock")
        amazon_provided_ipv6 = params.get("AmazonProvidedIpv6CidrBlock", False)
        instance_tenancy_str = params.get("InstanceTenancy", "default")
        ipv4_ipam_pool_id = params.get("Ipv4IpamPoolId")
        ipv4_netmask_length = params.get("Ipv4NetmaskLength")
        ipv6_cidr_block = params.get("Ipv6CidrBlock")
        ipv6_cidr_block_network_border_group = params.get("Ipv6CidrBlockNetworkBorderGroup")
        ipv6_ipam_pool_id = params.get("Ipv6IpamPoolId")
        ipv6_netmask_length = params.get("Ipv6NetmaskLength")
        ipv6_pool = params.get("Ipv6Pool")
        tag_specifications = params.get("TagSpecification.N", [])
        vpc_encryption_control = params.get("VpcEncryptionControl")

        if not cidr_block and not ipv4_ipam_pool_id:
            raise ValueError("Either CidrBlock or Ipv4IpamPoolId must be specified")

        # Validate CIDR block format and prefix length (VPCs must be /16 to /28)
        if cidr_block:
            self._validate_cidr_block(cidr_block, min_prefix=16, max_prefix=28)

        # Validate instance tenancy
        try:
            instance_tenancy = InstanceTenancy(instance_tenancy_str)
        except ValueError:
            raise ValueError(f"Invalid InstanceTenancy value: {instance_tenancy_str}")

        vpc_id = self.generate_unique_id(prefix="vpc-")
        owner_id = self.get_owner_id()

        # Create primary IPv4 CIDR block association
        association_id = self.generate_unique_id(prefix="vpc-cidr-assoc-")
        cidr_block_state = VpcCidrBlockState(
            state=CidrBlockStateCode.ASSOCIATED,
            statusMessage=None,
        )
        cidr_block_association = VpcCidrBlockAssociation(
            associationId=association_id,
            cidrBlock=cidr_block,
            cidrBlockState=cidr_block_state,
        )

        # Create IPv6 CIDR block association if requested
        ipv6_cidr_block_association_set = []
        if amazon_provided_ipv6 or ipv6_cidr_block or ipv6_pool or ipv6_ipam_pool_id:
            ipv6_association_id = self.generate_unique_id(prefix="vpc-cidr-assoc-")
            ipv6_cidr_block_state = VpcCidrBlockState(
                state=CidrBlockStateCode.ASSOCIATED,
                statusMessage=None,
            )
            ip_source = IpSource.AMAZON if amazon_provided_ipv6 else IpSource.BYOIP if ipv6_pool or ipv6_ipam_pool_id else IpSource.NONE
            ipv6_address_attribute = Ipv6AddressAttribute.PUBLIC if ip_source in (IpSource.AMAZON, IpSource.BYOIP) else Ipv6AddressAttribute.PRIVATE
            # Generate a fake IPv6 CIDR if amazon-provided and none specified
            resolved_ipv6_cidr = ipv6_cidr_block if ipv6_cidr_block else "2600:1f00::/56"
            ipv6_cidr_block_association = VpcIpv6CidrBlockAssociation(
                associationId=ipv6_association_id,
                ipSource=ip_source,
                ipv6AddressAttribute=ipv6_address_attribute,
                ipv6CidrBlock=resolved_ipv6_cidr,
                ipv6CidrBlockState=ipv6_cidr_block_state,
                ipv6Pool=ipv6_pool,
                networkBorderGroup=ipv6_cidr_block_network_border_group,
            )
            ipv6_cidr_block_association_set.append(ipv6_cidr_block_association)

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with ResourceType and Tags keys
            if not isinstance(tag_spec, dict):
                continue
            if tag_spec.get("ResourceType") != "vpc":
                continue
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Parse encryption control configuration if provided
        encryption_control = None
        if vpc_encryption_control:
            mode_str = vpc_encryption_control.get("Mode")
            if not mode_str:
                raise ValueError("VpcEncryptionControl.Mode is required")
            try:
                mode = EncryptionControlMode(mode_str)
            except ValueError:
                raise ValueError(f"Invalid EncryptionControlMode: {mode_str}")

            encryption_control = VpcEncryptionControlConfiguration(
                Mode=mode,
                EgressOnlyInternetGatewayExclusion=EncryptionControlExclusion(vpc_encryption_control.get("EgressOnlyInternetGatewayExclusion")) if vpc_encryption_control.get("EgressOnlyInternetGatewayExclusion") else None,
                ElasticFileSystemExclusion=EncryptionControlExclusion(vpc_encryption_control.get("ElasticFileSystemExclusion")) if vpc_encryption_control.get("ElasticFileSystemExclusion") else None,
                InternetGatewayExclusion=EncryptionControlExclusion(vpc_encryption_control.get("InternetGatewayExclusion")) if vpc_encryption_control.get("InternetGatewayExclusion") else None,
                LambdaExclusion=EncryptionControlExclusion(vpc_encryption_control.get("LambdaExclusion")) if vpc_encryption_control.get("LambdaExclusion") else None,
                NatGatewayExclusion=EncryptionControlExclusion(vpc_encryption_control.get("NatGatewayExclusion")) if vpc_encryption_control.get("NatGatewayExclusion") else None,
                VirtualPrivateGatewayExclusion=EncryptionControlExclusion(vpc_encryption_control.get("VirtualPrivateGatewayExclusion")) if vpc_encryption_control.get("VirtualPrivateGatewayExclusion") else None,
                VpcLatticeExclusion=EncryptionControlExclusion(vpc_encryption_control.get("VpcLatticeExclusion")) if vpc_encryption_control.get("VpcLatticeExclusion") else None,
                VpcPeeringExclusion=EncryptionControlExclusion(vpc_encryption_control.get("VpcPeeringExclusion")) if vpc_encryption_control.get("VpcPeeringExclusion") else None,
            )

        vpc = Vpc(
            vpcId=vpc_id,
            cidrBlock=cidr_block,
            cidrBlockAssociationSet=[cidr_block_association],
            dhcpOptionsId=None,
            instanceTenancy=instance_tenancy,
            ipv6CidrBlockAssociationSet=ipv6_cidr_block_association_set,
            isDefault=False,
            ownerId=owner_id,
            state=ResourceState.PENDING,  # Start in pending per LocalStack pattern
            tagSet=tags,
            blockPublicAccessStates=None,
            availabilityZone=ipv6_cidr_block_network_border_group,
            encryptionControl=encryption_control,
        )

        # Initialize default attributes
        vpc.enableDnsSupport = True
        vpc.enableDnsHostnames = False
        vpc.enableNetworkAddressUsageMetrics = False

        self.state.vpcs[vpc_id] = vpc

        # LocalStack pattern: VPC transitions from pending -> available
        # For synchronous emulation, immediately transition to available
        # This allows CloudFormation polling to succeed on first describe
        vpc.state = ResourceState.AVAILABLE

        # Also update CIDR block association state to associated
        for assoc in vpc.cidrBlockAssociationSet:
            if assoc.cidrBlockState:
                assoc.cidrBlockState.state = CidrBlockStateCode.ASSOCIATED
        
        # Create Default Security Group
        # We need to access SecurityGroupsBackend logic, but we can't easily cross-call without a full service interface.
        # However, we can manipulate state directly or replicate basic logic.
        # Creating a basic default SG directly in state.
        try:
            from emulator_core.services.security_groups import SecurityGroup, SecurityGroupRule, IpPermission
            default_sg_id = self.generate_unique_id(prefix="sg-")
            default_sg = SecurityGroup(
                groupDescription="default VPC security group",
                groupId=default_sg_id,
                groupName="default",
                ownerId=owner_id,
                vpcId=vpc_id,
                ipPermissions=[
                    # Allow all traffic from itself
                    SecurityGroupRule(
                        ipProtocol="-1",
                        fromPort=None,
                        toPort=None,
                        userIdGroupPairs=[{"GroupId": default_sg_id, "UserId": owner_id}]
                    )
                ],
                ipPermissionsEgress=[
                    # Allow all outbound traffic
                    SecurityGroupRule(
                        ipProtocol="-1",
                        cidrIpv4="0.0.0.0/0"
                    )
                ],
                tagSet=[],
                securityGroupArn=f"arn:aws:ec2:us-east-1:{owner_id}:security-group/{default_sg_id}"
            )
            # Ensure security_groups dict exists
            if not hasattr(self.state, "security_groups"):
                self.state.security_groups = {}
            self.state.security_groups[default_sg_id] = default_sg
            self.state.resources[default_sg_id] = default_sg
        except ImportError:
            # Fallback if classes not available or circular import (should not happen in runtime if loaded)
            pass
        except Exception as e:
            print(f"Warning: Failed to create default security group for VPC {vpc_id}: {e}")

        # Create Default Network ACL
        try:
            from emulator_core.services.network_acls import NetworkAcl, NetworkAclEntry, NetworkAclAssociation
            default_nacl_id = self.generate_unique_id(prefix="acl-")
            default_nacl = NetworkAcl(
                networkAclId=default_nacl_id,
                vpcId=vpc_id,
                ownerId=owner_id,
                isDefault=True,
                entries=[
                    # Inbound Allow All
                    NetworkAclEntry(
                        ruleNumber=100, protocol="-1", ruleAction="allow", egress=False, cidrBlock="0.0.0.0/0"
                    ),
                    # Inbound Deny All (implicit * rule usually not stored but implied, strictly 32767)
                    NetworkAclEntry(
                        ruleNumber=32767, protocol="-1", ruleAction="deny", egress=False, cidrBlock="0.0.0.0/0"
                    ),
                    # Outbound Allow All
                    NetworkAclEntry(
                        ruleNumber=100, protocol="-1", ruleAction="allow", egress=True, cidrBlock="0.0.0.0/0"
                    ),
                    # Outbound Deny All
                    NetworkAclEntry(
                        ruleNumber=32767, protocol="-1", ruleAction="deny", egress=True, cidrBlock="0.0.0.0/0"
                    ),
                ],
                associations=[],
                tagSet=[]
            )
            # Ensure network_acls dict exists
            if not hasattr(self.state, "network_acls"):
                self.state.network_acls = {}
            self.state.network_acls[default_nacl_id] = default_nacl
            self.state.resources[default_nacl_id] = default_nacl
        except ImportError:
            pass
        except Exception as e:
            print(f"Warning: Failed to create default network ACL for VPC {vpc_id}: {e}")

        # Create Main Route Table (AWS auto-creates this with VPC)
        try:
            from emulator_core.services.route_tables import RouteTable, Route, RouteTableAssociation, RouteState, RouteOrigin, RouteTableAssociationState, RouteTableAssociationStateCode
            main_rt_id = self.generate_unique_id(prefix="rtb-")
            main_assoc_id = self.generate_unique_id(prefix="rtbassoc-")
            main_route_table = RouteTable(
                route_table_id=main_rt_id,
                vpc_id=vpc_id,
                owner_id=owner_id,
                route_set=[
                    # Local route for VPC CIDR
                    Route(
                        destination_cidr_block=cidr_block,
                        gateway_id="local",
                        state=RouteState.ACTIVE,
                        origin=RouteOrigin.CREATE_ROUTE_TABLE,
                    )
                ],
                association_set=[
                    # Main association (not associated with specific subnet)
                    RouteTableAssociation(
                        route_table_association_id=main_assoc_id,
                        route_table_id=main_rt_id,
                        main=True,
                        association_state=RouteTableAssociationState(
                            state=RouteTableAssociationStateCode.ASSOCIATED
                        ),
                    )
                ],
                tag_set=[],
            )
            if not hasattr(self.state, "route_tables"):
                self.state.route_tables = {}
            self.state.route_tables[main_rt_id] = main_route_table
            self.state.resources[main_rt_id] = main_route_table
        except ImportError:
            pass
        except Exception as e:
            print(f"Warning: Failed to create main route table for VPC {vpc_id}: {e}")

        return {
            "requestId": self.generate_request_id(),
            "vpc": vpc.to_dict(),
        }


    def delete_vpc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        DeleteVpc API - LocalStack compatible behavior.

        LocalStack pattern:
        1. Clean up non-main route tables and their associations first
        2. Then delete the VPC
        3. Handle dependency violations gracefully
        """
        dry_run = params.get("DryRun", False)
        vpc_id = params.get("VpcId")
        if not vpc_id:
            raise ValueError("VpcId is required")

        if dry_run:
            # For dry run, raise DryRunOperation error if permissions are sufficient
            # Here we assume permissions are sufficient
            raise Exception("DryRunOperation")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # Check if VPC has any associated resources that prevent deletion
        # Check subnets
        if hasattr(self.state, "subnets"):
            for subnet in self.state.subnets.values():
                if getattr(subnet, "vpc_id", None) == vpc_id:
                    raise Exception("DependencyViolation: The VPC contains one or more subnets")

        # Check security groups (excluding default)
        if hasattr(self.state, "security_groups"):
            for sg in self.state.security_groups.values():
                if getattr(sg, "vpcId", None) == vpc_id and getattr(sg, "groupName", None) != "default":
                    raise Exception("DependencyViolation: The VPC contains one or more security groups")

        # Check for attached Internet Gateways
        if hasattr(self.state, "internet_gateways"):
            for igw in self.state.internet_gateways.values():
                attachment_set = getattr(igw, "attachment_set", [])
                for attachment in attachment_set:
                    if getattr(attachment, "vpc_id", None) == vpc_id:
                        state = getattr(attachment, "state", None)
                        if state and str(state).lower() in ("attached", "attaching"):
                            raise Exception(f"DependencyViolation: The VPC has an attached Internet Gateway {getattr(igw, 'internet_gateway_id', 'unknown')}")

        # Check for NAT Gateways in the VPC
        if hasattr(self.state, "nat_gateways"):
            for nat_gw in self.state.nat_gateways.values():
                nat_vpc_id = getattr(nat_gw, "vpc_id", None)
                nat_state = getattr(nat_gw, "state", None)
                if nat_vpc_id == vpc_id and nat_state and str(nat_state).lower() not in ("deleted", "deleting", "failed"):
                    raise Exception(f"DependencyViolation: The VPC contains one or more NAT Gateways")

        # Check for VPC Endpoints
        if hasattr(self.state, "vpc_endpoints"):
            for vpce in self.state.vpc_endpoints.values():
                vpce_vpc_id = getattr(vpce, "vpcId", None)
                vpce_state = getattr(vpce, "state", None)
                if vpce_vpc_id == vpc_id and vpce_state and str(vpce_state).lower() not in ("deleted", "deleting"):
                    raise Exception(f"DependencyViolation: The VPC contains one or more VPC Endpoints")

        # LocalStack pattern: Clean up route tables before VPC deletion
        # Remove non-main route tables and their associations
        if hasattr(self.state, "route_tables"):
            route_tables_to_delete = []
            for rt_id, rt in self.state.route_tables.items():
                if getattr(rt, "vpc_id", None) == vpc_id:
                    # Check if this is the main route table
                    is_main = any(
                        getattr(assoc, "main", False)
                        for assoc in getattr(rt, "association_set", [])
                    )
                    if not is_main:
                        # Disassociate all subnet associations first
                        for assoc in getattr(rt, "association_set", [])[:]:
                            if not getattr(assoc, "main", False):
                                rt.association_set.remove(assoc)
                        route_tables_to_delete.append(rt_id)

            # Delete non-main route tables
            for rt_id in route_tables_to_delete:
                del self.state.route_tables[rt_id]
                if rt_id in self.state.resources:
                    del self.state.resources[rt_id]

        # Clean up default security group for the VPC
        if hasattr(self.state, "security_groups"):
            sgs_to_delete = [
                sg_id for sg_id, sg in self.state.security_groups.items()
                if getattr(sg, "vpcId", None) == vpc_id and getattr(sg, "groupName", None) == "default"
            ]
            for sg_id in sgs_to_delete:
                del self.state.security_groups[sg_id]
                if sg_id in self.state.resources:
                    del self.state.resources[sg_id]

        # Clean up default network ACL for the VPC
        if hasattr(self.state, "network_acls"):
            nacls_to_delete = [
                nacl_id for nacl_id, nacl in self.state.network_acls.items()
                if getattr(nacl, "vpcId", None) == vpc_id and getattr(nacl, "isDefault", False)
            ]
            for nacl_id in nacls_to_delete:
                del self.state.network_acls[nacl_id]
                if nacl_id in self.state.resources:
                    del self.state.resources[nacl_id]

        # Delete the VPC
        del self.state.vpcs[vpc_id]

        # Also clean up from resources
        if vpc_id in self.state.resources:
            del self.state.resources[vpc_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def describe_vpc_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attribute = params.get("Attribute")
        vpc_id = params.get("VpcId")
        if not attribute:
            raise ValueError("Attribute is required")
        if not vpc_id:
            raise ValueError("VpcId is required")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # Prepare response dictionary
        response = {
            "requestId": self.generate_request_id(),
            "vpcId": vpc_id,
        }

        # Attributes: enableDnsSupport, enableDnsHostnames, enableNetworkAddressUsageMetrics
        
        # Get attributes from VPC object if they exist, else default
        enable_dns_support = getattr(vpc, "enableDnsSupport", True)
        enable_dns_hostnames = getattr(vpc, "enableDnsHostnames", False)
        enable_network_address_usage_metrics = getattr(vpc, "enableNetworkAddressUsageMetrics", False)

        attr_value = AttributeBooleanValue(Value=True) # Placeholder, construct actual below

        if attribute == "enableDnsSupport":
            response["enableDnsSupport"] = AttributeBooleanValue(Value=enable_dns_support)
        elif attribute == "enableDnsHostnames":
            response["enableDnsHostnames"] = AttributeBooleanValue(Value=enable_dns_hostnames)
        elif attribute == "enableNetworkAddressUsageMetrics":
            response["enableNetworkAddressUsageMetrics"] = AttributeBooleanValue(Value=enable_network_address_usage_metrics)
        else:
            raise ValueError(f"Invalid Attribute value: {attribute}")

        # Convert AttributeBooleanValue objects to dicts
        for key in ["enableDnsSupport", "enableDnsHostnames", "enableNetworkAddressUsageMetrics"]:
            if key in response:
                response[key] = {"value": response[key].Value}

        return response

    def describe_vpcs(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        vpc_ids = []
        # VpcId.N keys can be like VpcId.1, VpcId.2, etc.
        for key, value in params.items():
            if key.lower().startswith("vpcid."):
                vpc_ids.append(value)

        # Validate DryRun if present
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Validate MaxResults if present
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ValueError("MaxResults must be an integer if specified")
            if max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be between 5 and 1000")

        # Validate NextToken if present
        if next_token is not None and not isinstance(next_token, str):
            raise ValueError("NextToken must be a string if specified")

        # Validate filters format: list of dicts with Name and Values keys
        if filters:
            if not isinstance(filters, list):
                raise ValueError("Filter must be a list if specified")
            for f in filters:
                if not isinstance(f, dict):
                    raise ValueError("Each filter must be a dict")
                if "Name" not in f or "Values" not in f:
                    raise ValueError("Each filter must have 'Name' and 'Values'")
                if not isinstance(f["Name"], str):
                    raise ValueError("Filter Name must be a string")
                if not isinstance(f["Values"], list):
                    raise ValueError("Filter Values must be a list of strings")
                for v in f["Values"]:
                    if not isinstance(v, str):
                        raise ValueError("Filter Values must be strings")

        # DryRun check: simulate permission check
        if dry_run:
            # For simplicity, assume permission granted
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Collect VPCs to describe
        vpcs_to_describe = []

        # If VpcId.N specified, filter by those IDs
        if vpc_ids:
            for vpc_id in vpc_ids:
                vpc = self.state.vpcs.get(vpc_id)
                if vpc:
                    vpcs_to_describe.append(vpc)
        else:
            # Otherwise, all VPCs
            vpcs_to_describe = list(self.state.vpcs.values())

        # Apply filters if any
        def vpc_matches_filter(vpc, filter_name, filter_values):
            # Filter names are case-sensitive
            # Implement all filters described:
            # cidr, cidr-block-association.cidr-block, cidr-block-association.association-id,
            # cidr-block-association.state, dhcp-options-id, ipv6-cidr-block-association.ipv6-cidr-block,
            # ipv6-cidr-block-association.ipv6-pool, ipv6-cidr-block-association.association-id,
            # ipv6-cidr-block-association.state, is-default, owner-id, state,
            # tag:<key>, tag-key, vpc-id

            if filter_name == "cidr":
                # primary IPv4 CIDR block exact match
                return vpc.cidrBlock in filter_values

            if filter_name == "cidr-block-association.cidr-block":
                for assoc in vpc.cidrBlockAssociationSet:
                    if assoc.cidrBlock in filter_values:
                        return True
                return False

            if filter_name == "cidr-block-association.association-id":
                for assoc in vpc.cidrBlockAssociationSet:
                    if assoc.associationId in filter_values:
                        return True
                return False

            if filter_name == "cidr-block-association.state":
                for assoc in vpc.cidrBlockAssociationSet:
                    if assoc.cidrBlockState and assoc.cidrBlockState.state and assoc.cidrBlockState.state.value in filter_values:
                        return True
                return False

            if filter_name == "dhcp-options-id":
                return vpc.dhcpOptionsId in filter_values

            if filter_name == "ipv6-cidr-block-association.ipv6-cidr-block":
                for assoc in vpc.ipv6CidrBlockAssociationSet:
                    if assoc.ipv6CidrBlock in filter_values:
                        return True
                return False

            if filter_name == "ipv6-cidr-block-association.ipv6-pool":
                for assoc in vpc.ipv6CidrBlockAssociationSet:
                    if assoc.ipv6Pool in filter_values:
                        return True
                return False

            if filter_name == "ipv6-cidr-block-association.association-id":
                for assoc in vpc.ipv6CidrBlockAssociationSet:
                    if assoc.associationId in filter_values:
                        return True
                return False

            if filter_name == "ipv6-cidr-block-association.state":
                for assoc in vpc.ipv6CidrBlockAssociationSet:
                    if assoc.ipv6CidrBlockState and assoc.ipv6CidrBlockState.state and assoc.ipv6CidrBlockState.state.value in filter_values:
                        return True
                return False

            if filter_name == "is-default":
                # filter_values are strings "true" or "false"
                # vpc.isDefault is bool or None
                val_strs = [v.lower() for v in filter_values]
                vpc_is_default_str = "true" if vpc.isDefault else "false"
                return vpc_is_default_str in val_strs

            if filter_name == "owner-id":
                return vpc.ownerId in filter_values

            if filter_name == "state":
                # vpc.state is Enum member, compare its value string
                return vpc.state and vpc.state.value in filter_values

            if filter_name.startswith("tag:"):
                # tag:<key> filter: match if any tag with key=<key> and value in filter_values
                tag_key = filter_name[4:]
                for tag in vpc.tagSet:
                    if tag.Key == tag_key and tag.Value in filter_values:
                        return True
                return False

            if filter_name == "tag-key":
                # match if any tag key in filter_values
                for tag in vpc.tagSet:
                    if tag.Key in filter_values:
                        return True
                return False

            if filter_name == "vpc-id":
                return vpc.vpcId in filter_values

            # Unknown filter: no match
            return False

        # Apply all filters: all filters must match (AND)
        if filters:
            filtered_vpcs = []
            for vpc in vpcs_to_describe:
                if all(vpc_matches_filter(vpc, f["Name"], f["Values"]) for f in filters):
                    filtered_vpcs.append(vpc)
            vpcs_to_describe = filtered_vpcs

        # Pagination: implement NextToken and MaxResults
        # For simplicity, NextToken is an integer index encoded as string
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000  # default max

        end_index = start_index + max_results
        paged_vpcs = vpcs_to_describe[start_index:end_index]

        # Prepare next token if more results
        new_next_token = None
        if end_index < len(vpcs_to_describe):
            new_next_token = str(end_index)

        # Build response
        response = {
            "requestId": self.generate_request_id(),
            "vpcSet": [vpc.to_dict() for vpc in paged_vpcs],
            "nextToken": new_next_token,
        }
        return response


    def disassociate_vpc_cidr_block(self, params: dict) -> dict:
        association_id = params.get("AssociationId")
        if not association_id or not isinstance(association_id, str):
            raise ValueError("AssociationId is required and must be a string")

        # Find the VPC and association with this association_id
        vpc_found = None
        cidr_assoc = None
        ipv6_assoc = None

        for vpc in self.state.vpcs.values():
            # Check IPv4 associations
            for assoc in vpc.cidrBlockAssociationSet:
                if assoc.associationId == association_id:
                    vpc_found = vpc
                    cidr_assoc = assoc
                    break
            if vpc_found:
                break
            # Check IPv6 associations
            for assoc in vpc.ipv6CidrBlockAssociationSet:
                if assoc.associationId == association_id:
                    vpc_found = vpc
                    ipv6_assoc = assoc
                    break
            if vpc_found:
                break

        if not vpc_found:
            # AssociationId not found
            raise ValueError(f"AssociationId {association_id} not found")

        # Cannot disassociate primary CIDR block (for IPv4)
        if cidr_assoc:
            # The primary CIDR block is the one in vpc.cidrBlock and its associationId
            if cidr_assoc.cidrBlock == vpc_found.cidrBlock:
                raise ValueError("Cannot disassociate the primary CIDR block")

            # Mark the association state as disassociating
            cidr_assoc.cidrBlockState = cidr_assoc.cidrBlockState or VpcCidrBlockState()
            cidr_assoc.cidrBlockState.state = CidrBlockStateCode.DISASSOCIATING
            cidr_assoc.cidrBlockState.statusMessage = "Disassociating CIDR block"

            # For emulator, remove association immediately
            vpc_found.cidrBlockAssociationSet = [a for a in vpc_found.cidrBlockAssociationSet if a.associationId != association_id]

            response = {
                "cidrBlockAssociation": cidr_assoc.to_dict(),
                "requestId": self.generate_request_id(),
                "vpcId": vpc_found.vpcId,
            }
            return response

        if ipv6_assoc:
            # Mark the association state as disassociating
            ipv6_assoc.ipv6CidrBlockState = ipv6_assoc.ipv6CidrBlockState or VpcCidrBlockState()
            ipv6_assoc.ipv6CidrBlockState.state = CidrBlockStateCode.DISASSOCIATING
            ipv6_assoc.ipv6CidrBlockState.statusMessage = "Disassociating IPv6 CIDR block"

            # For emulator, remove association immediately
            vpc_found.ipv6CidrBlockAssociationSet = [a for a in vpc_found.ipv6CidrBlockAssociationSet if a.associationId != association_id]

            response = {
                "ipv6CidrBlockAssociation": ipv6_assoc.to_dict(),
                "requestId": self.generate_request_id(),
                "vpcId": vpc_found.vpcId,
            }
            return response

        # Should not reach here
        raise ValueError("AssociationId not found in any CIDR block association")


    def modify_vpc_attribute(self, params: dict) -> dict:
        vpc_id = params.get("VpcId")
        if not vpc_id or not isinstance(vpc_id, str):
            raise ValueError("VpcId is required and must be a string")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} not found")

        enable_dns_hostnames = params.get("EnableDnsHostnames")
        enable_dns_support = params.get("EnableDnsSupport")
        enable_network_address_usage_metrics = params.get("EnableNetworkAddressUsageMetrics")

        # Validate that only one of EnableDnsHostnames and EnableDnsSupport is modified at once
        if enable_dns_hostnames is not None and enable_dns_support is not None:
            raise ValueError("Cannot modify EnableDnsHostnames and EnableDnsSupport in the same request")

        # Helper to extract boolean value from AttributeBooleanValue object
        def extract_bool(attr):
            if attr is None:
                return None
            if not isinstance(attr, dict):
                # If generated via tool, it might pass non-dict? Assume dict based on method signature
                # But params might come from gateway as dict
                if hasattr(attr, "get"):
                    return attr.get("Value")
                return None
            val = attr.get("Value")
            # val might be string "true"/"false" if not parsed
            if isinstance(val, str):
                return val.lower() == "true"
            if val is None:
                return None
            if not isinstance(val, bool):
                # Try converting
                return bool(val)
            return val

        dns_hostnames_val = extract_bool(enable_dns_hostnames)
        dns_support_val = extract_bool(enable_dns_support)
        network_metrics_val = extract_bool(enable_network_address_usage_metrics)

        # For emulator, store these attributes on the VPC object as attributes
        
        # Get current values
        current_dns_support = getattr(vpc, "enableDnsSupport", True)

        if dns_hostnames_val is not None:
            # Only enable if DNS support is enabled (current or new)
            new_dns_support = dns_support_val if dns_support_val is not None else current_dns_support
            if dns_hostnames_val and not new_dns_support:
                raise ValueError("Cannot enable DNS hostnames if DNS support is not enabled")
            vpc.enableDnsHostnames = dns_hostnames_val

        if dns_support_val is not None:
            vpc.enableDnsSupport = dns_support_val
            # If DNS support disabled, also disable DNS hostnames?
            # AWS docs say: "If you disable DNS support, you cannot enable DNS hostnames."
            # It doesn't explicitly say it disables hostnames if they were enabled, but logically it should or they become ineffective.
            if not dns_support_val:
                vpc.enableDnsHostnames = False

        if network_metrics_val is not None:
            vpc.enableNetworkAddressUsageMetrics = network_metrics_val

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def modify_vpc_tenancy(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        instance_tenancy = params.get("InstanceTenancy")
        vpc_id = params.get("VpcId")

        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        if not instance_tenancy or not isinstance(instance_tenancy, str):
            raise ValueError("InstanceTenancy is required and must be a string")

        if instance_tenancy != "default":
            raise ValueError("Only 'default' tenancy modification is supported")

        if not vpc_id or not isinstance(vpc_id, str):
            raise ValueError("VpcId is required and must be a string")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} not found")

        if dry_run:
            # For simplicity, assume permission granted
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Modify tenancy to default
        vpc.instanceTenancy = InstanceTenancy.DEFAULT

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_vpc_classic_link_dns_support(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """DescribeVpcClassicLinkDnsSupport operation."""
        # Parse VpcIds from VpcIds.N params
        vpc_ids = []
        for key, value in params.items():
            if key.startswith("VpcIds."):
                vpc_ids.append(value)

        # Parse pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
            except (ValueError, TypeError):
                max_results = None
        next_token = params.get("NextToken")

        # Get all VPCs
        all_vpcs = list(self.state.vpcs.values())

        # Filter by VPC IDs if provided
        if vpc_ids:
            all_vpcs = [vpc for vpc in all_vpcs if vpc.vpcId in vpc_ids]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (ValueError, TypeError):
                start_index = 0

        end_index = start_index + max_results if max_results else None
        paged_vpcs = all_vpcs[start_index:end_index]

        # Build response
        vpcs_list = []
        for vpc in paged_vpcs:
            # ClassicLinkDnsSupported is stored as an attribute, default to False
            classic_link_dns_supported = False
            if hasattr(vpc, 'classicLinkDnsSupported'):
                classic_link_dns_supported = vpc.classicLinkDnsSupported
            vpcs_list.append({
                "vpcId": vpc.vpcId,
                "classicLinkDnsSupported": classic_link_dns_supported,
            })

        # Prepare next token
        new_next_token = None
        if end_index is not None and end_index < len(all_vpcs):
            new_next_token = str(end_index)

        return {
            "requestId": self.generate_request_id(),
            "vpcs": vpcs_list,
            "nextToken": new_next_token,
        }


from emulator_core.gateway.base import BaseGateway

class VPCsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateVpcCidrBlock", self.associate_vpc_cidr_block)
        self.register_action("CreateDefaultVpc", self.create_default_vpc)
        self.register_action("CreateVpc", self.create_vpc)
        self.register_action("DeleteVpc", self.delete_vpc)
        self.register_action("DescribeVpcAttribute", self.describe_vpc_attribute)
        self.register_action("DescribeVpcClassicLinkDnsSupport", self.describe_vpc_classic_link_dns_support)
        self.register_action("DescribeVpcs", self.describe_vpcs)
        self.register_action("DisassociateVpcCidrBlock", self.disassociate_vpc_cidr_block)
        self.register_action("ModifyVpcAttribute", self.modify_vpc_attribute)
        self.register_action("ModifyVpcTenancy", self.modify_vpc_tenancy)

    def associate_vpc_cidr_block(self, params):
        return self.backend.associate_vpc_cidr_block(params)

    def create_default_vpc(self, params):
        return self.backend.create_default_vpc(params)

    def create_vpc(self, params):
        return self.backend.create_vpc(params)

    def delete_vpc(self, params):
        return self.backend.delete_vpc(params)

    def describe_vpc_attribute(self, params):
        return self.backend.describe_vpc_attribute(params)

    def describe_vpc_classic_link_dns_support(self, params):
        return self.backend.describe_vpc_classic_link_dns_support(params)

    def describe_vpcs(self, params):
        return self.backend.describe_vpcs(params)

    def disassociate_vpc_cidr_block(self, params):
        return self.backend.disassociate_vpc_cidr_block(params)

    def modify_vpc_attribute(self, params):
        return self.backend.modify_vpc_attribute(params)

    def modify_vpc_tenancy(self, params):
        return self.backend.modify_vpc_tenancy(params)
