from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend


class AddressFamily(str, Enum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"


class AwsService(str, Enum):
    EC2 = "ec2"
    GLOBAL_SERVICES = "global-services"


class IpamPoolState(str, Enum):
    CREATE_IN_PROGRESS = "create-in-progress"
    CREATE_COMPLETE = "create-complete"
    CREATE_FAILED = "create-failed"
    MODIFY_IN_PROGRESS = "modify-in-progress"
    MODIFY_COMPLETE = "modify-complete"
    MODIFY_FAILED = "modify-failed"
    DELETE_IN_PROGRESS = "delete-in-progress"
    DELETE_COMPLETE = "delete-complete"
    DELETE_FAILED = "delete-failed"
    ISOLATE_IN_PROGRESS = "isolate-in-progress"
    ISOLATE_COMPLETE = "isolate-complete"
    RESTORE_IN_PROGRESS = "restore-in-progress"


class IpamScopeType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class ResourceType(str, Enum):
    IPAM_POOL = "ipam-pool"
    VPC = "vpc"
    EC2_PUBLIC_IPV4_POOL = "ec2-public-ipv4-pool"
    CUSTOM = "custom"
    SUBNET = "subnet"
    EIP = "eip"
    ANYCAST_IP_LIST = "anycast-ip-list"


class VerificationMethod(str, Enum):
    REMARKS_X509 = "remarks-x509"
    DNS_TOKEN = "dns-token"


class FailureCode(str, Enum):
    CIDR_NOT_AVAILABLE = "cidr-not-available"
    LIMIT_EXCEEDED = "limit-exceeded"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class RequestIpamResourceTag:
    Key: Optional[str] = None
    Value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.Key is not None:
            d["Key"] = self.Key
        if self.Value is not None:
            d["Value"] = self.Value
        return d


@dataclass
class IpamResourceTag:
    key: Optional[str] = None
    value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.key is not None:
            d["Key"] = self.key
        if self.value is not None:
            d["Value"] = self.value
        return d


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
class IpamPoolSourceResourceRequest:
    ResourceId: Optional[str] = None
    ResourceOwner: Optional[str] = None
    ResourceRegion: Optional[str] = None
    ResourceType: Optional[str] = None  # Valid Values: vpc

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.ResourceId is not None:
            d["ResourceId"] = self.ResourceId
        if self.ResourceOwner is not None:
            d["ResourceOwner"] = self.ResourceOwner
        if self.ResourceRegion is not None:
            d["ResourceRegion"] = self.ResourceRegion
        if self.ResourceType is not None:
            d["ResourceType"] = self.ResourceType
        return d


@dataclass
class IpamPoolSourceResource:
    resourceId: Optional[str] = None
    resourceOwner: Optional[str] = None
    resourceRegion: Optional[str] = None
    resourceType: Optional[str] = None  # Valid Values: vpc

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.resourceId is not None:
            d["resourceId"] = self.resourceId
        if self.resourceOwner is not None:
            d["resourceOwner"] = self.resourceOwner
        if self.resourceRegion is not None:
            d["resourceRegion"] = self.resourceRegion
        if self.resourceType is not None:
            d["resourceType"] = self.resourceType
        return d


@dataclass
class IpamCidrAuthorizationContext:
    Message: Optional[str] = None
    Signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.Message is not None:
            d["Message"] = self.Message
        if self.Signature is not None:
            d["Signature"] = self.Signature
        return d


@dataclass
class IpamPoolCidrFailureReason:
    code: Optional[str] = None  # Valid Values: cidr-not-available | limit-exceeded
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.code is not None:
            d["code"] = self.code
        if self.message is not None:
            d["message"] = self.message
        return d


@dataclass
class IpamPoolCidr:
    cidr: Optional[str] = None
    failureReason: Optional[IpamPoolCidrFailureReason] = None
    ipamPoolCidrId: Optional[str] = None
    netmaskLength: Optional[int] = None
    state: Optional[str] = None  # Valid Values: pending-provision | provisioned | failed-provision | pending-deprovision | deprovisioned | failed-deprovision | pending-import | failed-import

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.cidr is not None:
            d["cidr"] = self.cidr
        if self.failureReason is not None:
            d["failureReason"] = self.failureReason.to_dict()
        if self.ipamPoolCidrId is not None:
            d["ipamPoolCidrId"] = self.ipamPoolCidrId
        if self.netmaskLength is not None:
            d["netmaskLength"] = self.netmaskLength
        if self.state is not None:
            d["state"] = self.state
        return d


@dataclass
class IpamPoolAllocation:
    cidr: Optional[str] = None
    description: Optional[str] = None
    ipamPoolAllocationId: Optional[str] = None
    resourceId: Optional[str] = None
    resourceOwner: Optional[str] = None
    resourceRegion: Optional[str] = None
    resourceType: Optional[str] = None  # Valid Values: ipam-pool | vpc | ec2-public-ipv4-pool | custom | subnet | eip | anycast-ip-list

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.cidr is not None:
            d["cidr"] = self.cidr
        if self.description is not None:
            d["description"] = self.description
        if self.ipamPoolAllocationId is not None:
            d["ipamPoolAllocationId"] = self.ipamPoolAllocationId
        if self.resourceId is not None:
            d["resourceId"] = self.resourceId
        if self.resourceOwner is not None:
            d["resourceOwner"] = self.resourceOwner
        if self.resourceRegion is not None:
            d["resourceRegion"] = self.resourceRegion
        if self.resourceType is not None:
            d["resourceType"] = self.resourceType
        return d


@dataclass
class PublicIpv4PoolRange:
    addressCount: Optional[int] = None
    availableAddressCount: Optional[int] = None
    firstAddress: Optional[str] = None
    lastAddress: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.addressCount is not None:
            d["addressCount"] = self.addressCount
        if self.availableAddressCount is not None:
            d["availableAddressCount"] = self.availableAddressCount
        if self.firstAddress is not None:
            d["firstAddress"] = self.firstAddress
        if self.lastAddress is not None:
            d["lastAddress"] = self.lastAddress
        return d


@dataclass
class PublicIpv4Pool:
    description: Optional[str] = None
    networkBorderGroup: Optional[str] = None
    poolAddressRangeSet: List[PublicIpv4PoolRange] = field(default_factory=list)
    poolId: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    totalAddressCount: Optional[int] = None
    totalAvailableAddressCount: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "networkBorderGroup": self.networkBorderGroup,
            "poolAddressRangeSet": [r.to_dict() for r in self.poolAddressRangeSet],
            "poolId": self.poolId,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "totalAddressCount": self.totalAddressCount,
            "totalAvailableAddressCount": self.totalAvailableAddressCount,
        }


@dataclass
class IpamPool:
    addressFamily: Optional[str] = None  # Valid Values: ipv4 | ipv6
    allocationDefaultNetmaskLength: Optional[int] = None
    allocationMaxNetmaskLength: Optional[int] = None
    allocationMinNetmaskLength: Optional[int] = None
    allocationResourceTagSet: List[IpamResourceTag] = field(default_factory=list)
    autoImport: Optional[bool] = None
    awsService: Optional[str] = None  # Valid Values: ec2 | global-services
    description: Optional[str] = None
    ipamArn: Optional[str] = None
    ipamPoolArn: Optional[str] = None
    ipamPoolId: Optional[str] = None
    ipamRegion: Optional[str] = None
    ipamScopeArn: Optional[str] = None
    ipamScopeType: Optional[str] = None  # Valid Values: public | private
    locale: Optional[str] = None
    ownerId: Optional[str] = None
    poolDepth: Optional[int] = None
    publicIpSource: Optional[str] = None  # Valid Values: amazon | byoip
    publiclyAdvertisable: Optional[bool] = None
    sourceIpamPoolId: Optional[str] = None
    sourceResource: Optional[IpamPoolSourceResource] = None
    state: Optional[str] = None  # Valid Values: see IpamPoolState
    stateMessage: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "addressFamily": self.addressFamily,
            "allocationDefaultNetmaskLength": self.allocationDefaultNetmaskLength,
            "allocationMaxNetmaskLength": self.allocationMaxNetmaskLength,
            "allocationMinNetmaskLength": self.allocationMinNetmaskLength,
            "allocationResourceTagSet": [tag.to_dict() for tag in self.allocationResourceTagSet],
            "autoImport": self.autoImport,
            "awsService": self.awsService,
            "description": self.description,
            "ipamArn": self.ipamArn,
            "ipamPoolArn": self.ipamPoolArn,
            "ipamPoolId": self.ipamPoolId,
            "ipamRegion": self.ipamRegion,
            "ipamScopeArn": self.ipamScopeArn,
            "ipamScopeType": self.ipamScopeType,
            "locale": self.locale,
            "ownerId": self.ownerId,
            "poolDepth": self.poolDepth,
            "publicIpSource": self.publicIpSource,
            "publiclyAdvertisable": self.publiclyAdvertisable,
            "sourceIpamPoolId": self.sourceIpamPoolId,
            "state": self.state,
            "stateMessage": self.stateMessage,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
        }
        if self.sourceResource is not None:
            d["sourceResource"] = self.sourceResource.to_dict()
        return d


class PoolsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.pools or appropriate shared state dicts

    def allocate_ipam_pool_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ipam_pool_id = params.get("IpamPoolId")
        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")

        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            raise ValueError(f"IPAM Pool {ipam_pool_id} does not exist")

        # Validate DryRun parameter (not implemented here, just placeholder)
        dry_run = params.get("DryRun", False)
        if dry_run:
            # In real AWS, would check permissions and raise DryRunOperation or UnauthorizedOperation
            return {"requestId": self.generate_request_id()}

        # Extract parameters
        allowed_cidrs = params.get("AllowedCidr.N", [])
        disallowed_cidrs = params.get("DisallowedCidr.N", [])
        cidr = params.get("Cidr")
        netmask_length = params.get("NetmaskLength")
        description = params.get("Description")
        preview_next_cidr = params.get("PreviewNextCidr", False)
        client_token = params.get("ClientToken")

        # Validate that either cidr or netmask_length is specified if no default netmask length on pool
        default_netmask_length = ipam_pool.allocationDefaultNetmaskLength
        if default_netmask_length is None and cidr is None and netmask_length is None:
            raise ValueError("Either Cidr or NetmaskLength must be specified if no DefaultNetmaskLength is set on the pool")

        # Determine allocation CIDR
        # For simplicity, if cidr is specified, use it directly
        # Otherwise, allocate a CIDR from the pool's available space
        # This is a simplified allocation logic for the emulator

        # Check if preview_next_cidr is True, then just return the next available CIDR without allocation
        # For simplicity, we will just return a dummy CIDR for preview
        if preview_next_cidr:
            # Return a dummy next CIDR (in real implementation, would calculate next available)
            next_cidr = "10.0.0.0/24"
            allocation = IpamPoolAllocation(
                cidr=next_cidr,
                description=description,
                ipamPoolAllocationId=None,
                resourceId=None,
                resourceOwner=None,
                resourceRegion=None,
                resourceType=None,
            )
            return {
                "ipamPoolAllocation": allocation.to_dict(),
                "requestId": self.generate_request_id(),
            }

        # If cidr is specified, validate it is within the pool CIDRs (simplified)
        # For simplicity, assume pool has a list of IpamPoolCidr objects in ipam_pool.cidrSet (not defined in given classes)
        # We will skip detailed CIDR validation here

        # Generate allocation ID
        allocation_id = self.generate_unique_id()

        # Create allocation object
        allocation = IpamPoolAllocation(
            cidr=cidr if cidr else f"10.0.0.0/{netmask_length if netmask_length else default_netmask_length}",
            description=description,
            ipamPoolAllocationId=allocation_id,
            resourceId=None,
            resourceOwner=None,
            resourceRegion=None,
            resourceType=None,
        )

        # Store allocation in state
        if not hasattr(self.state, "ipam_pool_allocations"):
            self.state.ipam_pool_allocations = {}
        self.state.ipam_pool_allocations[allocation_id] = allocation

        return {
            "ipamPoolAllocation": allocation.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_ipam_pool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        address_family = params.get("AddressFamily")
        ipam_scope_id = params.get("IpamScopeId")
        if not address_family:
            raise ValueError("AddressFamily is required")
        if not ipam_scope_id:
            raise ValueError("IpamScopeId is required")

        # Validate DryRun parameter (not implemented here, just placeholder)
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"requestId": self.generate_request_id()}

        allocation_default_netmask_length = params.get("AllocationDefaultNetmaskLength")
        allocation_max_netmask_length = params.get("AllocationMaxNetmaskLength")
        allocation_min_netmask_length = params.get("AllocationMinNetmaskLength")
        allocation_resource_tag_list = params.get("AllocationResourceTag.N", [])
        auto_import = params.get("AutoImport")
        aws_service = params.get("AwsService")
        description = params.get("Description")
        client_token = params.get("ClientToken")
        locale = params.get("Locale")
        public_ip_source = params.get("PublicIpSource")
        publicly_advertisable = params.get("PubliclyAdvertisable")
        source_ipam_pool_id = params.get("SourceIpamPoolId")
        source_resource_params = params.get("SourceResource")
        tag_specifications = params.get("TagSpecification.N", [])

        # Validate address_family
        if address_family not in ("ipv4", "ipv6"):
            raise ValueError("AddressFamily must be 'ipv4' or 'ipv6'")

        # Validate netmask lengths if provided
        if allocation_min_netmask_length is not None and allocation_max_netmask_length is not None:
            if allocation_min_netmask_length > allocation_max_netmask_length:
                raise ValueError("AllocationMinNetmaskLength must be less than or equal to AllocationMaxNetmaskLength")

        # Convert allocation_resource_tag_list to list of IpamResourceTag
        allocation_resource_tags = []
        for tag_dict in allocation_resource_tag_list:
            key = tag_dict.get("Key")
            value = tag_dict.get("Value")
            allocation_resource_tags.append(IpamResourceTag(key=key, value=value))

        # Convert tag_specifications to list of Tag
        tags = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                tags.append(Tag(Key=key, Value=value))

        # Create source resource object if provided
        source_resource = None
        if source_resource_params:
            source_resource = IpamPoolSourceResource(
                resourceId=source_resource_params.get("ResourceId"),
                resourceOwner=source_resource_params.get("ResourceOwner"),
                resourceRegion=source_resource_params.get("ResourceRegion"),
                resourceType=source_resource_params.get("ResourceType"),
            )

        # Generate pool ID and ARNs
        pool_id = self.generate_unique_id()
        ipam_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:ipam/ipam-1234567890abcdef0"
        ipam_pool_arn = f"{ipam_arn}/pool/{pool_id}"
        ipam_scope_arn = f"{ipam_arn}/scope/{ipam_scope_id}"

        # Create IpamPool object
        ipam_pool = IpamPool(
            addressFamily=address_family,
            allocationDefaultNetmaskLength=allocation_default_netmask_length,
            allocationMaxNetmaskLength=allocation_max_netmask_length,
            allocationMinNetmaskLength=allocation_min_netmask_length,
            allocationResourceTagSet=allocation_resource_tags,
            autoImport=auto_import,
            awsService=aws_service,
            description=description,
            ipamArn=ipam_arn,
            ipamPoolArn=ipam_pool_arn,
            ipamPoolId=pool_id,
            ipamRegion=self.state.region,
            ipamScopeArn=ipam_scope_arn,
            ipamScopeType=None,  # Not provided in params
            locale=locale,
            ownerId=self.get_owner_id(),
            poolDepth=0,
            publicIpSource=public_ip_source,
            publiclyAdvertisable=publicly_advertisable,
            sourceIpamPoolId=source_ipam_pool_id,
            sourceResource=source_resource,
            state="create-complete",
            stateMessage=None,
            tagSet=tags,
        )

        # Store pool in state
        self.state.pools[pool_id] = ipam_pool

        return {
            "ipamPool": ipam_pool.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_public_ipv4_pool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"requestId": self.generate_request_id()}

        network_border_group = params.get("NetworkBorderGroup")
        tag_specifications = params.get("TagSpecification.N", [])

        # Convert tag_specifications to list of Tag
        tags = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                tags.append(Tag(Key=key, Value=value))

        # Generate pool ID
        pool_id = self.generate_unique_id()

        # Create PublicIpv4PoolRange dummy range for example
        pool_range = PublicIpv4PoolRange(
            addressCount=256,
            availableAddressCount=256,
            firstAddress="203.0.113.0",
            lastAddress="203.0.113.255",
        )

        # Create PublicIpv4Pool object
        public_ipv4_pool = PublicIpv4Pool(
            description=None,
            networkBorderGroup=network_border_group,
            poolAddressRangeSet=[pool_range],
            poolId=pool_id,
            tagSet=tags,
            totalAddressCount=256,
            totalAvailableAddressCount=256,
        )

        # Store public pool in state
        if not hasattr(self.state, "public_ipv4_pools"):
            self.state.public_ipv4_pools = {}
        self.state.public_ipv4_pools[pool_id] = public_ipv4_pool

        return {
            "poolId": pool_id,
            "requestId": self.generate_request_id(),
        }


    def delete_ipam_pool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ipam_pool_id = params.get("IpamPoolId")
        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")

        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"requestId": self.generate_request_id()}

        cascade = params.get("Cascade", False)

        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            raise ValueError(f"IPAM Pool {ipam_pool_id} does not exist")

        # Check if there are allocations or provisioned CIDRs in the pool
        # For simplicity, assume allocations are stored in self.state.ipam_pool_allocations
        allocations = getattr(self.state, "ipam_pool_allocations", {})
        allocations_in_pool = [
            alloc for alloc in allocations.values()
            if alloc.ipamPoolAllocationId and alloc.ipamPoolAllocationId.startswith(ipam_pool_id)
        ]

        if allocations_in_pool and not cascade:
            raise ValueError("Cannot delete IPAM pool with allocations unless Cascade is True")

        # If cascade is True, delete all allocations in the pool
        if cascade:
            for alloc in allocations_in_pool:
                del allocations[alloc.ipamPoolAllocationId]

        # Delete the pool
        del self.state.pools[ipam_pool_id]

        # Return the deleted pool info with state set to delete-complete
        ipam_pool.state = "delete-complete"
        ipam_pool.stateMessage = "Pool deleted successfully"

        return {
            "ipamPool": ipam_pool.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_public_ipv4_pool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pool_id = params.get("PoolId")
        if not pool_id:
            raise ValueError("PoolId is required")

        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"requestId": self.generate_request_id()}

        public_ipv4_pools = getattr(self.state, "public_ipv4_pools", {})
        if pool_id not in public_ipv4_pools:
            raise ValueError(f"Public IPv4 Pool {pool_id} does not exist")

        del public_ipv4_pools[pool_id]

        return {
            "requestId": self.generate_request_id(),
            "returnValue": True,
        }

    def deprovision_ipam_pool_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ipam_pool_id = params.get("IpamPoolId")
        cidr = params.get("Cidr")
        dry_run = params.get("DryRun", False)

        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")

        if dry_run:
            # For dry run, just return error if no permission, else DryRunOperation error
            # Here we assume permission granted for simplicity
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            raise ValueError(f"IPAM Pool with id {ipam_pool_id} not found")

        # Find the IpamPoolCidr to deprovision
        pool_cidr_to_deprovision = None
        for pool_cidr in getattr(ipam_pool, "cidrSet", []):
            if cidr is None or pool_cidr.cidr == cidr:
                pool_cidr_to_deprovision = pool_cidr
                break

        if not pool_cidr_to_deprovision:
            # If no matching CIDR found, return failure reason
            failure_reason = IpamPoolCidrFailureReason(
                code="cidr-not-available",
                message="The specified CIDR is not provisioned in the IPAM pool"
            )
            ipam_pool_cidr = IpamPoolCidr(
                cidr=cidr,
                failureReason=failure_reason,
                ipamPoolCidrId=None,
                netmaskLength=None,
                state=None
            )
            return {
                "ipamPoolCidr": ipam_pool_cidr.to_dict(),
                "requestId": self.generate_request_id(),
            }

        # Mark the CIDR as deprovisioned
        pool_cidr_to_deprovision.state = "deprovisioned"

        # If the pool has a source pool, recycle the CIDR back to the source pool
        source_pool_id = getattr(ipam_pool, "sourceIpamPoolId", None)
        if source_pool_id:
            source_pool = self.state.pools.get(source_pool_id)
            if source_pool:
                # Add the CIDR back to source pool's cidrSet
                if not hasattr(source_pool, "cidrSet"):
                    source_pool.cidrSet = []
                source_pool.cidrSet.append(pool_cidr_to_deprovision)

        return {
            "ipamPoolCidr": pool_cidr_to_deprovision.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def deprovision_public_ipv4_pool_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pool_id = params.get("PoolId")
        cidr = params.get("Cidr")
        dry_run = params.get("DryRun", False)

        if not pool_id:
            raise ValueError("PoolId is required")
        if not cidr:
            raise ValueError("Cidr is required")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        public_pool = self.state.pools.get(pool_id)
        if not public_pool or not isinstance(public_pool, PublicIpv4Pool):
            raise ValueError(f"Public IPv4 Pool with id {pool_id} not found")

        deprovisioned_addresses = []

        # Remove the CIDR from poolAddressRangeSet if present
        new_ranges = []
        for pool_range in public_pool.poolAddressRangeSet:
            if pool_range.firstAddress == cidr or pool_range.lastAddress == cidr or cidr in (pool_range.firstAddress, pool_range.lastAddress):
                deprovisioned_addresses.append(cidr)
                # Skip this range to deprovision it
                continue
            new_ranges.append(pool_range)
        public_pool.poolAddressRangeSet = new_ranges

        if not deprovisioned_addresses:
            # If no matching CIDR found, raise error or return empty list
            deprovisioned_addresses = []

        return {
            "deprovisionedAddressSet": deprovisioned_addresses,
            "poolId": pool_id,
            "requestId": self.generate_request_id(),
        }


    def describe_ipam_pools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter", [])
        ipam_pool_ids = params.get("IpamPoolId", [])
        max_results = params.get("MaxResults", 1000)
        next_token = params.get("NextToken")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate max_results range
        if max_results < 5:
            max_results = 5
        elif max_results > 1000:
            max_results = 1000

        # Collect pools to describe
        pools = list(self.state.pools.values())

        # Filter by IpamPoolId if provided
        if ipam_pool_ids:
            pools = [p for p in pools if getattr(p, "ipamPoolId", None) in ipam_pool_ids]

        # Apply filters if any
        def match_filter(pool, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            # Support tag:<key> and tag-key- filters
            if name.startswith("tag:"):
                tag_key = name[4:]
                pool_tags = {tag.Key: tag.Value for tag in getattr(pool, "tagSet", [])}
                return any(pool_tags.get(tag_key) == v for v in values)
            elif name == "tag-key":
                pool_tags = {tag.Key for tag in getattr(pool, "tagSet", [])}
                return any(v in pool_tags for v in values)
            else:
                # Generic attribute filter
                attr_val = getattr(pool, name, None)
                if attr_val is None:
                    return False
                if isinstance(attr_val, list):
                    return any(str(v) == str(attr_val) for v in values)
                return str(attr_val) in values

        for f in filters:
            pools = [p for p in pools if match_filter(p, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        paged_pools = pools[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(pools) else None

        return {
            "ipamPoolSet": [p.to_dict() for p in paged_pools],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_public_ipv4_pools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults", 10)
        next_token = params.get("NextToken")
        pool_ids = params.get("PoolId", [])

        # Validate max_results range
        if max_results < 1:
            max_results = 1
        elif max_results > 10:
            max_results = 10

        pools = [p for p in self.state.pools.values() if isinstance(p, PublicIpv4Pool)]

        # Filter by PoolId if provided
        if pool_ids:
            pools = [p for p in pools if getattr(p, "poolId", None) in pool_ids]

        # Apply filters
        def match_filter(pool, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name.startswith("tag:"):
                tag_key = name[4:]
                pool_tags = {tag.Key: tag.Value for tag in getattr(pool, "tagSet", [])}
                return any(pool_tags.get(tag_key) == v for v in values)
            elif name == "tag-key":
                pool_tags = {tag.Key for tag in getattr(pool, "tagSet", [])}
                return any(v in pool_tags for v in values)
            else:
                attr_val = getattr(pool, name, None)
                if attr_val is None:
                    return False
                if isinstance(attr_val, list):
                    return any(str(v) == str(attr_val) for v in values)
                return str(attr_val) in values

        for f in filters:
            pools = [p for p in pools if match_filter(p, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        paged_pools = pools[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(pools) else None

        return {
            "publicIpv4PoolSet": [p.to_dict() for p in paged_pools],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def get_ipam_pool_allocations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ipam_pool_id = params.get("IpamPoolId")
        ipam_pool_allocation_id = params.get("IpamPoolAllocationId")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults", 1000)
        next_token = params.get("NextToken")
        dry_run = params.get("DryRun", False)

        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate max_results range
        if max_results < 1000:
            max_results = 1000
        elif max_results > 100000:
            max_results = 100000

        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            raise ValueError(f"IPAM Pool with id {ipam_pool_id} not found")

        # Get allocations list from pool
        allocations = getattr(ipam_pool, "allocationSet", [])

        # Filter by allocation id if provided
        if ipam_pool_allocation_id:
            allocations = [a for a in allocations if getattr(a, "ipamPoolAllocationId", None) == ipam_pool_allocation_id]

        # Apply filters
        def match_filter(allocation, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            attr_val = getattr(allocation, name, None)
            if attr_val is None:
                return False
            if isinstance(attr_val, list):
                return any(str(v) == str(attr_val) for v in values)
            return str(attr_val) in values

        for f in filters:
            allocations = [a for a in allocations if match_filter(a, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        paged_allocations = allocations[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(allocations) else None

        return {
            "ipamPoolAllocationSet": [a.to_dict() for a in paged_allocations],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def get_ipam_pool_cidrs(self, params: dict) -> dict:
        ipam_pool_id = params.get("IpamPoolId")
        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")

        # Retrieve the IPAM pool from state
        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            # Return empty list if pool not found
            return {
                "ipamPoolCidrSet": [],
                "nextToken": None,
                "requestId": self.generate_request_id(),
            }

        # Filters are optional, but if provided, apply them
        filters = params.get("Filter", [])
        # Normalize filters to list of dicts if single dict provided
        if isinstance(filters, dict):
            filters = [filters]

        # Pagination params
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise ValueError()
            except Exception:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # ipamPoolCidrSet is a list of IpamPoolCidr objects on the pool
        cidr_list = getattr(ipam_pool, "ipamPoolCidrSet", [])
        if cidr_list is None:
            cidr_list = []

        # Apply filters if any
        def matches_filter(cidr_obj, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # no filter criteria, match all

            # Support filtering by fields of IpamPoolCidr
            # Possible filter names could be: cidr, ipamPoolCidrId, netmaskLength, state
            # Also support nested failureReason.code and failureReason.message
            if name == "cidr":
                return cidr_obj.cidr in values
            elif name == "ipam-pool-cidr-id" or name == "ipamPoolCidrId":
                return cidr_obj.ipamPoolCidrId in values
            elif name == "netmask-length" or name == "netmaskLength":
                return str(cidr_obj.netmaskLength) in [str(v) for v in values]
            elif name == "state":
                return cidr_obj.state in values
            elif name == "failure-reason-code":
                if cidr_obj.failureReason and cidr_obj.failureReason.code:
                    return cidr_obj.failureReason.code in values
                return False
            elif name == "failure-reason-message":
                if cidr_obj.failureReason and cidr_obj.failureReason.message:
                    return cidr_obj.failureReason.message in values
                return False
            else:
                # Unknown filter, ignore
                return True

        filtered_cidrs = []
        for cidr_obj in cidr_list:
            if all(matches_filter(cidr_obj, f) for f in filters):
                filtered_cidrs.append(cidr_obj)

        # Pagination slice
        end_index = len(filtered_cidrs)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_cidrs))

        paged_cidrs = filtered_cidrs[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(filtered_cidrs):
            new_next_token = str(end_index)

        # Convert to dicts
        ipam_pool_cidr_set = [cidr.to_dict() for cidr in paged_cidrs]

        return {
            "ipamPoolCidrSet": ipam_pool_cidr_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def modify_ipam_pool(self, params: dict) -> dict:
        ipam_pool_id = params.get("IpamPoolId")
        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")

        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            raise ValueError(f"IPAM pool {ipam_pool_id} not found")

        # Update allocation resource tags
        add_tags = params.get("AddAllocationResourceTag", [])
        if isinstance(add_tags, dict):
            add_tags = [add_tags]
        remove_tags = params.get("RemoveAllocationResourceTag", [])
        if isinstance(remove_tags, dict):
            remove_tags = [remove_tags]

        # Convert add_tags to IpamResourceTag objects
        for tag_dict in add_tags:
            key = tag_dict.get("Key")
            value = tag_dict.get("Value")
            if key is None:
                continue
            # Check if tag already exists, update or add
            found = False
            for existing_tag in ipam_pool.allocationResourceTagSet:
                if existing_tag.key == key:
                    existing_tag.value = value
                    found = True
                    break
            if not found:
                ipam_pool.allocationResourceTagSet.append(IpamResourceTag(key=key, value=value))

        # Remove tags
        for tag_dict in remove_tags:
            key = tag_dict.get("Key")
            value = tag_dict.get("Value")
            # Remove matching tags by key and optionally value
            ipam_pool.allocationResourceTagSet = [
                t for t in ipam_pool.allocationResourceTagSet
                if not (t.key == key and (value is None or t.value == value))
            ]

        # Update other fields if provided
        if "AllocationDefaultNetmaskLength" in params:
            val = params.get("AllocationDefaultNetmaskLength")
            if val is not None:
                ipam_pool.allocationDefaultNetmaskLength = int(val)
        if params.get("ClearAllocationDefaultNetmaskLength"):
            ipam_pool.allocationDefaultNetmaskLength = None
        if "AllocationMaxNetmaskLength" in params:
            val = params.get("AllocationMaxNetmaskLength")
            if val is not None:
                ipam_pool.allocationMaxNetmaskLength = int(val)
        if "AllocationMinNetmaskLength" in params:
            val = params.get("AllocationMinNetmaskLength")
            if val is not None:
                ipam_pool.allocationMinNetmaskLength = int(val)
        if "AutoImport" in params:
            val = params.get("AutoImport")
            if val is not None:
                ipam_pool.autoImport = bool(val)
        if "Description" in params:
            ipam_pool.description = params.get("Description")

        # Mark state as modify-in-progress then modify-complete (simulate)
        ipam_pool.state = "modify-in-progress"
        # For emulator, we immediately set to modify-complete
        ipam_pool.state = "modify-complete"

        return {
            "ipamPool": ipam_pool.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def provision_ipam_pool_cidr(self, params: dict) -> dict:
        ipam_pool_id = params.get("IpamPoolId")
        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")

        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            raise ValueError(f"IPAM pool {ipam_pool_id} not found")

        cidr = params.get("Cidr")
        netmask_length = params.get("NetmaskLength")

        if not cidr and netmask_length is None:
            raise ValueError("Either Cidr or NetmaskLength must be specified")

        # Generate a unique ID for the new pool CIDR
        ipam_pool_cidr_id = self.generate_unique_id(prefix="ipam-pool-cidr")

        # Create failure reason as None initially
        failure_reason = None

        # For simplicity, assume provisioning always succeeds in emulator
        state = "pending-provision"

        # Create IpamPoolCidr object
        ipam_pool_cidr = IpamPoolCidr(
            cidr=cidr,
            failureReason=failure_reason,
            ipamPoolCidrId=ipam_pool_cidr_id,
            netmaskLength=int(netmask_length) if netmask_length is not None else None,
            state=state,
        )

        # Add to pool's cidr list
        if not hasattr(ipam_pool, "ipamPoolCidrSet") or ipam_pool.ipamPoolCidrSet is None:
            ipam_pool.ipamPoolCidrSet = []
        ipam_pool.ipamPoolCidrSet.append(ipam_pool_cidr)

        # Simulate immediate provisioning success
        ipam_pool_cidr.state = "provisioned"
        if not ipam_pool_cidr.cidr and ipam_pool_cidr.netmaskLength is not None:
            # For emulator, generate a dummy CIDR string if only netmask length provided
            # Use a dummy base address for IPv4 or IPv6 depending on pool address family
            if ipam_pool.addressFamily == "ipv6":
                ipam_pool_cidr.cidr = f"2001:db8::{ipam_pool_cidr.netmaskLength}/{ipam_pool_cidr.netmaskLength}"
            else:
                ipam_pool_cidr.cidr = f"10.0.0.0/{ipam_pool_cidr.netmaskLength}"

        return {
            "ipamPoolCidr": ipam_pool_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def provision_public_ipv4_pool_cidr(self, params: dict) -> dict:
        ipam_pool_id = params.get("IpamPoolId")
        pool_id = params.get("PoolId")
        netmask_length = params.get("NetmaskLength")
        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")
        if not pool_id:
            raise ValueError("PoolId is required")
        if netmask_length is None:
            raise ValueError("NetmaskLength is required")

        # Validate netmask length minimum 24
        try:
            netmask_length = int(netmask_length)
        except Exception:
            raise ValueError("NetmaskLength must be an integer")
        if netmask_length < 24:
            raise ValueError("NetmaskLength must be at least 24")

        # Retrieve the public IPv4 pool
        public_pool = self.state.pools.get(pool_id)
        if not public_pool or not isinstance(public_pool, PublicIpv4Pool):
            raise ValueError(f"Public IPv4 pool {pool_id} not found")

        # For simplicity, allocate a dummy range for the requested netmask length
        # Calculate address count = 2^(32 - netmask_length)
        address_count = 2 ** (32 - netmask_length)

        # For emulator, create a dummy first and last address
        # Use a base address 192.0.2.0 for example
        first_address = "192.0.2.0"
        last_address = "192.0.2." + str(address_count - 1)

        pool_address_range = PublicIpv4PoolRange(
            addressCount=address_count,
            availableAddressCount=address_count,
            firstAddress=first_address,
            lastAddress=last_address,
        )

        # Add the new range to the pool's poolAddressRangeSet
        if not hasattr(public_pool, "poolAddressRangeSet") or public_pool.poolAddressRangeSet is None:
            public_pool.poolAddressRangeSet = []
        public_pool.poolAddressRangeSet.append(pool_address_range)

        # Update total counts
        if public_pool.totalAddressCount is None:
            public_pool.totalAddressCount = 0
        if public_pool.totalAvailableAddressCount is None:
            public_pool.totalAvailableAddressCount = 0
        public_pool.totalAddressCount += address_count
        public_pool.totalAvailableAddressCount += address_count

        return {
            "poolAddressRange": pool_address_range.to_dict(),
            "poolId": pool_id,
            "requestId": self.generate_request_id(),
        }


    def release_ipam_pool_allocation(self, params: dict) -> dict:
        ipam_pool_id = params.get("IpamPoolId")
        ipam_pool_allocation_id = params.get("IpamPoolAllocationId")
        cidr = params.get("Cidr")

        if not ipam_pool_id:
            raise ValueError("IpamPoolId is required")
        if not ipam_pool_allocation_id:
            raise ValueError("IpamPoolAllocationId is required")
        if not cidr:
            raise ValueError("Cidr is required")

        ipam_pool = self.state.pools.get(ipam_pool_id)
        if not ipam_pool:
            raise ValueError(f"IPAM pool {ipam_pool_id} not found")

        # ipamPoolAllocations is assumed to be a list attribute on the pool
        allocations = getattr(ipam_pool, "ipamPoolAllocations", [])
        if allocations is None:
            allocations = []

        # Find allocation by id and cidr
        allocation_to_remove = None
        for alloc in allocations:
            if alloc.ipamPoolAllocationId == ipam_pool_allocation_id and alloc.cidr == cidr:
                allocation_to_remove = alloc
                break

        if not allocation_to_remove:
            # Allocation not found, return success False
            return {
                "requestId": self.generate_request_id(),
                "success": False,
            }

        # Remove allocation from pool allocations
        ipam_pool.ipamPoolAllocations = [a for a in allocations if a != allocation_to_remove]

        return {
            "requestId": self.generate_request_id(),
            "success": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class PoolsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AllocateIpamPoolCidr", self.allocate_ipam_pool_cidr)
        self.register_action("CreateIpamPool", self.create_ipam_pool)
        self.register_action("CreatePublicIpv4Pool", self.create_public_ipv4_pool)
        self.register_action("DeleteIpamPool", self.delete_ipam_pool)
        self.register_action("DeletePublicIpv4Pool", self.delete_public_ipv4_pool)
        self.register_action("DeprovisionIpamPoolCidr", self.deprovision_ipam_pool_cidr)
        self.register_action("DeprovisionPublicIpv4PoolCidr", self.deprovision_public_ipv4_pool_cidr)
        self.register_action("DescribeIpamPools", self.describe_ipam_pools)
        self.register_action("DescribePublicIpv4Pools", self.describe_public_ipv4_pools)
        self.register_action("GetIpamPoolAllocations", self.get_ipam_pool_allocations)
        self.register_action("GetIpamPoolCidrs", self.get_ipam_pool_cidrs)
        self.register_action("ModifyIpamPool", self.modify_ipam_pool)
        self.register_action("ProvisionIpamPoolCidr", self.provision_ipam_pool_cidr)
        self.register_action("ProvisionPublicIpv4PoolCidr", self.provision_public_ipv4_pool_cidr)
        self.register_action("ReleaseIpamPoolAllocation", self.release_ipam_pool_allocation)

    def allocate_ipam_pool_cidr(self, params):
        return self.backend.allocate_ipam_pool_cidr(params)

    def create_ipam_pool(self, params):
        return self.backend.create_ipam_pool(params)

    def create_public_ipv4_pool(self, params):
        return self.backend.create_public_ipv4_pool(params)

    def delete_ipam_pool(self, params):
        return self.backend.delete_ipam_pool(params)

    def delete_public_ipv4_pool(self, params):
        return self.backend.delete_public_ipv4_pool(params)

    def deprovision_ipam_pool_cidr(self, params):
        return self.backend.deprovision_ipam_pool_cidr(params)

    def deprovision_public_ipv4_pool_cidr(self, params):
        return self.backend.deprovision_public_ipv4_pool_cidr(params)

    def describe_ipam_pools(self, params):
        return self.backend.describe_ipam_pools(params)

    def describe_public_ipv4_pools(self, params):
        return self.backend.describe_public_ipv4_pools(params)

    def get_ipam_pool_allocations(self, params):
        return self.backend.get_ipam_pool_allocations(params)

    def get_ipam_pool_cidrs(self, params):
        return self.backend.get_ipam_pool_cidrs(params)

    def modify_ipam_pool(self, params):
        return self.backend.modify_ipam_pool(params)

    def provision_ipam_pool_cidr(self, params):
        return self.backend.provision_ipam_pool_cidr(params)

    def provision_public_ipv4_pool_cidr(self, params):
        return self.backend.provision_public_ipv4_pool_cidr(params)

    def release_ipam_pool_allocation(self, params):
        return self.backend.release_ipam_pool_allocation(params)
