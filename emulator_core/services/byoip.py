from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend


class ByoipCidrState(str, Enum):
    ADVERTISED = "advertised"
    DEPROVISIONED = "deprovisioned"
    FAILED_DEPROVISION = "failed-deprovision"
    FAILED_PROVISION = "failed-provision"
    PENDING_ADVERTISING = "pending-advertising"
    PENDING_DEPROVISION = "pending-deprovision"
    PENDING_PROVISION = "pending-provision"
    PENDING_WITHDRAWAL = "pending-withdrawal"
    PROVISIONED = "provisioned"
    PROVISIONED_NOT_PUBLICLY_ADVERTISABLE = "provisioned-not-publicly-advertisable"


class AsnAssociationState(str, Enum):
    DISASSOCIATED = "disassociated"
    FAILED_DISASSOCIATION = "failed-disassociation"
    FAILED_ASSOCIATION = "failed-association"
    PENDING_DISASSOCIATION = "pending-disassociation"
    PENDING_ASSOCIATION = "pending-association"
    ASSOCIATED = "associated"


class AdvertisementType(str, Enum):
    UNICAST = "unicast"
    ANYCAST = "anycast"


@dataclass
class AsnAssociation:
    asn: Optional[str] = None
    cidr: Optional[str] = None
    state: Optional[AsnAssociationState] = None
    status_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asn": self.asn,
            "cidr": self.cidr,
            "state": self.state.value if self.state else None,
            "statusMessage": self.status_message,
        }


@dataclass
class ByoipCidr:
    advertisement_type: Optional[AdvertisementType] = None
    asn_association_set: List[AsnAssociation] = field(default_factory=list)
    cidr: Optional[str] = None
    description: Optional[str] = None
    network_border_group: Optional[str] = None
    state: Optional[ByoipCidrState] = None
    status_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "advertisementType": self.advertisement_type.value if self.advertisement_type else None,
            "asnAssociationSet": [assoc.to_dict() for assoc in self.asn_association_set],
            "cidr": self.cidr,
            "description": self.description,
            "networkBorderGroup": self.network_border_group,
            "state": self.state.value if self.state else None,
            "statusMessage": self.status_message,
        }


@dataclass
class CidrAuthorizationContext:
    message: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Message": self.message,
            "Signature": self.signature,
        }


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Key": self.Key,
            "Value": self.Value,
        }


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
class PoolCidrBlock:
    pool_cidr_block: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "poolCidrBlock": self.pool_cidr_block,
        }


@dataclass
class Ipv6Pool:
    description: Optional[str] = None
    pool_cidr_block_set: List[PoolCidrBlock] = field(default_factory=list)
    pool_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "poolCidrBlockSet": [block.to_dict() for block in self.pool_cidr_block_set],
            "poolId": self.pool_id,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
        }


@dataclass
class PublicIpv4PoolRange:
    address_count: Optional[int] = None
    available_address_count: Optional[int] = None
    first_address: Optional[str] = None
    last_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "addressCount": self.address_count,
            "availableAddressCount": self.available_address_count,
            "firstAddress": self.first_address,
            "lastAddress": self.last_address,
        }


@dataclass
class PublicIpv4Pool:
    description: Optional[str] = None
    network_border_group: Optional[str] = None
    pool_address_range_set: List[PublicIpv4PoolRange] = field(default_factory=list)
    pool_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    total_address_count: Optional[int] = None
    total_available_address_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "networkBorderGroup": self.network_border_group,
            "poolAddressRangeSet": [range_.to_dict() for range_ in self.pool_address_range_set],
            "poolId": self.pool_id,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "totalAddressCount": self.total_address_count,
            "totalAvailableAddressCount": self.total_available_address_count,
        }


@dataclass
class Ipv6CidrAssociation:
    associated_resource: Optional[str] = None
    ipv6_cidr: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "associatedResource": self.associated_resource,
            "ipv6Cidr": self.ipv6_cidr,
        }


class BYOIPBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)

    def advertise_byoip_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cidr = params.get("Cidr")
        if not cidr:
            raise ValueError("Cidr is required")
        asn = params.get("Asn")
        dry_run = params.get("DryRun", False)
        network_border_group = params.get("NetworkBorderGroup")

        # DryRun check placeholder (permissions check)
        if dry_run:
            # In real implementation, check permissions here
            return {"Error": "DryRunOperation", "Message": "DryRun operation successful"}

        # Find the BYOIP CIDR in state
        byoip_cidr = self.state.byoip.get(cidr)
        if not byoip_cidr:
            # If not found, create a new ByoipCidr object with provisioned state
            byoip_cidr = ByoipCidr()
            byoip_cidr.cidr = cidr
            byoip_cidr.state = ByoipCidrState.PENDING_ADVERTISING if asn else ByoipCidrState.PENDING_ADVERTISING
            byoip_cidr.advertisement_type = AdvertisementType.UNICAST
            byoip_cidr.asn_association_set = []
            byoip_cidr.description = None
            byoip_cidr.network_border_group = network_border_group
            byoip_cidr.status_message = None
            self.state.byoip[cidr] = byoip_cidr
        else:
            # If found, update state to advertised
            byoip_cidr.state = ByoipCidrState.ADVERTISED
            byoip_cidr.network_border_group = network_border_group

        # Handle ASN association if ASN provided
        if asn:
            # Check if association already exists
            existing_assoc = None
            for assoc in byoip_cidr.asn_association_set:
                if assoc.asn == asn and assoc.cidr == cidr:
                    existing_assoc = assoc
                    break
            if not existing_assoc:
                assoc = AsnAssociation()
                assoc.asn = asn
                assoc.cidr = cidr
                assoc.state = AsnAssociationState.ASSOCIATED
                assoc.status_message = None
                byoip_cidr.asn_association_set.append(assoc)
            else:
                existing_assoc.state = AsnAssociationState.ASSOCIATED
                existing_assoc.status_message = None

        response = {
            "byoipCidr": byoip_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def deprovision_byoip_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cidr = params.get("Cidr")
        if not cidr:
            raise ValueError("Cidr is required")
        dry_run = params.get("DryRun", False)

        # DryRun check placeholder (permissions check)
        if dry_run:
            # In real implementation, check permissions here
            return {"Error": "DryRunOperation", "Message": "DryRun operation successful"}

        byoip_cidr = self.state.byoip.get(cidr)
        if not byoip_cidr:
            raise ValueError(f"BYOIP CIDR {cidr} not found")

        # Check if currently advertised
        if byoip_cidr.state == ByoipCidrState.ADVERTISED:
            # Must stop advertising before deprovisioning
            raise ValueError("Cannot deprovision an advertised BYOIP CIDR. Stop advertising first.")

        # Check if any IP addresses allocated from this range
        # Since no info about allocated IPs in current state, assume none allocated
        # In real implementation, check allocated IPs here

        # Set state to pending deprovision
        byoip_cidr.state = ByoipCidrState.PENDING_DEPROVISION
        byoip_cidr.status_message = None

        # Simulate deprovision success
        byoip_cidr.state = ByoipCidrState.DEPROVISIONED

        response = {
            "byoipCidr": byoip_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_byoip_cidrs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if max_results is None:
            raise ValueError("MaxResults is required")
        if not (1 <= max_results <= 100):
            raise ValueError("MaxResults must be between 1 and 100")

        # DryRun check placeholder (permissions check)
        if dry_run:
            # In real implementation, check permissions here
            return {"Error": "DryRunOperation", "Message": "DryRun operation successful"}

        # Get all BYOIP CIDRs sorted by CIDR string for consistent pagination
        all_cidrs = sorted(self.state.byoip.values(), key=lambda c: c.cidr or "")

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page_cidrs = all_cidrs[start_index:end_index]

        response_cidrs = [c.to_dict() for c in page_cidrs]

        new_next_token = str(end_index) if end_index < len(all_cidrs) else None

        response = {
            "byoipCidrSet": response_cidrs,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_ipv6_pools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        pool_ids = params.get("PoolId.N", [])

        if max_results is not None and not (1 <= max_results <= 1000):
            raise ValueError("MaxResults must be between 1 and 1000")

        # DryRun check placeholder (permissions check)
        if dry_run:
            # In real implementation, check permissions here
            return {"Error": "DryRunOperation", "Message": "DryRun operation successful"}

        # Filter pools by PoolId if provided
        pools = list(self.state.ipv6_pools.values()) if hasattr(self.state, "ipv6_pools") else []
        if pool_ids:
            pools = [p for p in pools if p.pool_id in pool_ids]

        # Apply filters if any
        def matches_filter(pool, filter_):
            name = filter_.get("Name")
            values = filter_.get("Values", [])
            if not name or not values:
                return True
            if name.startswith("tag:"):
                tag_key = name[4:]
                tag_values = [tag.Value for tag in pool.tag_set if tag.Key == tag_key]
                return any(v in tag_values for v in values)
            if name == "tag-key":
                tag_keys = [tag.Key for tag in pool.tag_set]
                return any(v in tag_keys for v in values)
            return True

        for f in filters:
            pools = [p for p in pools if matches_filter(p, f)]

        # Sort pools by pool_id for consistent pagination
        pools = sorted(pools, key=lambda p: p.pool_id or "")

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000

        end_index = start_index + max_results
        page_pools = pools[start_index:end_index]

        response_pools = [p.to_dict() for p in page_pools]

        new_next_token = str(end_index) if end_index < len(pools) else None

        response = {
            "ipv6PoolSet": response_pools,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_public_ipv4_pools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        pool_ids = params.get("PoolId.N", [])
        dry_run = params.get("DryRun", False)

        if max_results is not None and not (1 <= max_results <= 10):
            raise ValueError("MaxResults must be between 1 and 10")

        # DryRun check placeholder (permissions check)
        if dry_run:
            # In real implementation, check permissions here
            return {"Error": "DryRunOperation", "Message": "DryRun operation successful"}

        pools = list(self.state.public_ipv4_pools.values()) if hasattr(self.state, "public_ipv4_pools") else []
        if pool_ids:
            pools = [p for p in pools if p.pool_id in pool_ids]

        # Apply filters if any
        def matches_filter(pool, filter_):
            name = filter_.get("Name")
            values = filter_.get("Values", [])
            if not name or not values:
                return True
            if name.startswith("tag:"):
                tag_key = name[4:]
                tag_values = [tag.Value for tag in pool.tag_set if tag.Key == tag_key]
                return any(v in tag_values for v in values)
            if name == "tag-key":
                tag_keys = [tag.Key for tag in pool.tag_set]
                return any(v in tag_keys for v in values)
            return True

        for f in filters:
            pools = [p for p in pools if matches_filter(p, f)]

        # Sort pools by pool_id for consistent pagination
        pools = sorted(pools, key=lambda p: p.pool_id or "")

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 10

        end_index = start_index + max_results
        page_pools = pools[start_index:end_index]

        response_pools = [p.to_dict() for p in page_pools]

        new_next_token = str(end_index) if end_index < len(pools) else None

        response = {
            "publicIpv4PoolSet": response_pools,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response

    def get_associated_ipv6_pool_cidrs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pool_id = params.get("PoolId")
        if not pool_id:
            raise ValueError("PoolId is required")

        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate max_results if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 1 and 1000")

        # Retrieve the IPv6 pool from state
        ipv6_pool = self.state.byoip.get(pool_id)
        if ipv6_pool is None:
            # If not found in byoip, try in ipv6 pools
            ipv6_pool = self.state.ipv6_pools.get(pool_id)
        if ipv6_pool is None:
            # Return empty result if pool not found
            return {
                "ipv6CidrAssociationSet": [],
                "nextToken": None,
                "requestId": self.generate_request_id(),
            }

        # ipv6_pool is expected to be an Ipv6Pool instance
        # Gather all ipv6 cidr associations from pool_cidr_block_set
        all_associations = []
        for pool_cidr_block in getattr(ipv6_pool, "pool_cidr_block_set", []):
            # Each pool_cidr_block is a PoolCidrBlock instance
            # We do not have explicit associations in PoolCidrBlock, so we create one with ipv6_cidr = pool_cidr_block.pool_cidr_block
            if pool_cidr_block.pool_cidr_block:
                assoc = Ipv6CidrAssociation(
                    associated_resource=None,
                    ipv6_cidr=pool_cidr_block.pool_cidr_block,
                )
                all_associations.append(assoc)

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000

        paged_associations = all_associations[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(all_associations):
            new_next_token = str(start_index + max_results)

        return {
            "ipv6CidrAssociationSet": [assoc.to_dict() for assoc in paged_associations],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def provision_byoip_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cidr = params.get("Cidr")
        if not cidr:
            raise ValueError("Cidr is required")

        cidr_auth_context = params.get("CidrAuthorizationContext")
        description = params.get("Description")
        multi_region = params.get("MultiRegion", False)
        network_border_group = params.get("NetworkBorderGroup")
        pool_tag_specifications = []
        # PoolTagSpecification.N is a list of TagSpecification objects
        # The input param keys might be like "PoolTagSpecification.1", "PoolTagSpecification.2", etc.
        # We will collect all keys starting with "PoolTagSpecification." and parse them
        for key, value in params.items():
            if key.startswith("PoolTagSpecification"):
                # value is expected to be a dict with ResourceType and Tags
                if isinstance(value, dict):
                    resource_type = value.get("ResourceType")
                    tags_list = value.get("Tags", [])
                    tags = []
                    for tag_dict in tags_list:
                        if isinstance(tag_dict, dict):
                            key_tag = tag_dict.get("Key")
                            val_tag = tag_dict.get("Value")
                            if key_tag is not None and val_tag is not None:
                                tags.append(Tag(Key=key_tag, Value=val_tag))
                    pool_tag_specifications.append(TagSpecification(ResourceType=resource_type, Tags=tags))

        publicly_advertisable = params.get("PubliclyAdvertisable", True)

        # Validate that the cidr does not overlap with existing byoip cidrs
        for existing_cidr_obj in self.state.byoip.values():
            if existing_cidr_obj.cidr == cidr:
                raise ValueError(f"CIDR {cidr} already provisioned")

        # Create new ByoipCidr object
        byoip_cidr = ByoipCidr(
            advertisement_type=None,
            asn_association_set=[],
            cidr=cidr,
            description=description,
            network_border_group=network_border_group,
            state=ByoipCidrState.PENDING_PROVISION,
            status_message=None,
        )

        # Store in state with generated id
        cidr_id = self.generate_unique_id()
        self.state.byoip[cidr_id] = byoip_cidr

        return {
            "byoipCidr": byoip_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def withdraw_byoip_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cidr = params.get("Cidr")
        if not cidr:
            raise ValueError("Cidr is required")

        # Find the ByoipCidr object by cidr
        byoip_cidr_obj = None
        for cidr_obj in self.state.byoip.values():
            if cidr_obj.cidr == cidr:
                byoip_cidr_obj = cidr_obj
                break

        if byoip_cidr_obj is None:
            raise ValueError(f"BYOIP CIDR {cidr} not found")

        # Update state to pending withdrawal
        byoip_cidr_obj.state = ByoipCidrState.PENDING_WITHDRAWAL
        byoip_cidr_obj.status_message = "Withdrawal requested"

        return {
            "byoipCidr": byoip_cidr_obj.to_dict(),
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class BYOIPGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AdvertiseByoipCidr", self.advertise_byoip_cidr)
        self.register_action("DeprovisionByoipCidr", self.deprovision_byoip_cidr)
        self.register_action("DescribeByoipCidrs", self.describe_byoip_cidrs)
        self.register_action("DescribeIpv6Pools", self.describe_ipv6_pools)
        self.register_action("DescribePublicIpv4Pools", self.describe_public_ipv4_pools)
        self.register_action("GetAssociatedIpv6PoolCidrs", self.get_associated_ipv6_pool_cidrs)
        self.register_action("ProvisionByoipCidr", self.provision_byoip_cidr)
        self.register_action("WithdrawByoipCidr", self.withdraw_byoip_cidr)

    def advertise_byoip_cidr(self, params):
        return self.backend.advertise_byoip_cidr(params)

    def deprovision_byoip_cidr(self, params):
        return self.backend.deprovision_byoip_cidr(params)

    def describe_byoip_cidrs(self, params):
        return self.backend.describe_byoip_cidrs(params)

    def describe_ipv6_pools(self, params):
        return self.backend.describe_ipv6_pools(params)

    def describe_public_ipv4_pools(self, params):
        return self.backend.describe_public_ipv4_pools(params)

    def get_associated_ipv6_pool_cidrs(self, params):
        return self.backend.get_associated_ipv6_pool_cidrs(params)

    def provision_byoip_cidr(self, params):
        return self.backend.provision_byoip_cidr(params)

    def withdraw_byoip_cidr(self, params):
        return self.backend.withdraw_byoip_cidr(params)
