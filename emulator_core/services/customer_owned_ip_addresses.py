from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


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
    ResourceType: str
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class CoipCidr:
    cidr: Optional[str] = None
    coipPoolId: Optional[str] = None
    localGatewayRouteTableId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cidr": self.cidr,
            "coipPoolId": self.coipPoolId,
            "localGatewayRouteTableId": self.localGatewayRouteTableId,
        }


@dataclass
class CoipPool:
    localGatewayRouteTableId: Optional[str] = None
    poolArn: Optional[str] = None
    poolCidrSet: List[str] = field(default_factory=list)
    poolId: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "localGatewayRouteTableId": self.localGatewayRouteTableId,
            "poolArn": self.poolArn,
            "poolCidrSet": self.poolCidrSet,
            "poolId": self.poolId,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
        }


@dataclass
class Filter:
    Name: str
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Values": self.Values,
        }


@dataclass
class CoipAddressUsage:
    allocationId: Optional[str] = None
    awsAccountId: Optional[str] = None
    awsService: Optional[str] = None
    coIp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocationId": self.allocationId,
            "awsAccountId": self.awsAccountId,
            "awsService": self.awsService,
            "coIp": self.coIp,
        }


class CustomerOwnedIPaddressesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for persistence

    def create_coip_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cidr = params.get("Cidr")
        coip_pool_id = params.get("CoipPoolId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}

        if not cidr:
            raise ValueError("Cidr is required")
        if not coip_pool_id:
            raise ValueError("CoipPoolId is required")

        coip_pool = self.state.customer_owned_ip_addresses.get(coip_pool_id)
        if not coip_pool:
            raise ValueError(f"CoipPoolId {coip_pool_id} does not exist")

        # Check if cidr already exists in poolCidrSet
        if cidr in coip_pool.poolCidrSet:
            raise ValueError(f"Cidr {cidr} already exists in CoipPool {coip_pool_id}")

        # Add cidr to poolCidrSet
        coip_pool.poolCidrSet.append(cidr)

        # Create CoipCidr object
        coip_cidr = CoipCidr(
            cidr=cidr,
            coipPoolId=coip_pool_id,
            localGatewayRouteTableId=coip_pool.localGatewayRouteTableId,
        )

        # Store CoipCidr in state keyed by cidr+poolId for uniqueness
        coip_cidr_key = f"{coip_pool_id}:{cidr}"
        self.state.customer_owned_ip_addresses[coip_cidr_key] = coip_cidr

        return {
            "coipCidr": coip_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_coip_pool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}

        if not local_gateway_route_table_id:
            raise ValueError("LocalGatewayRouteTableId is required")

        # Generate poolId and poolArn
        pool_id = self.generate_unique_id()
        pool_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:coip-pool/{pool_id}"

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags
            # Only add tags if ResourceType is 'coip-pool' or not specified
            resource_type = tag_spec.get("ResourceType")
            if resource_type and resource_type != "coip-pool":
                continue
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(Key=key, Value=value))

        coip_pool = CoipPool(
            localGatewayRouteTableId=local_gateway_route_table_id,
            poolArn=pool_arn,
            poolCidrSet=[],
            poolId=pool_id,
            tagSet=tags,
        )

        self.state.customer_owned_ip_addresses[pool_id] = coip_pool

        return {
            "coipPool": coip_pool.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_coip_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cidr = params.get("Cidr")
        coip_pool_id = params.get("CoipPoolId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}

        if not cidr:
            raise ValueError("Cidr is required")
        if not coip_pool_id:
            raise ValueError("CoipPoolId is required")

        coip_pool = self.state.customer_owned_ip_addresses.get(coip_pool_id)
        if not coip_pool:
            raise ValueError(f"CoipPoolId {coip_pool_id} does not exist")

        coip_cidr_key = f"{coip_pool_id}:{cidr}"
        coip_cidr = self.state.customer_owned_ip_addresses.get(coip_cidr_key)
        if not coip_cidr:
            raise ValueError(f"Cidr {cidr} does not exist in CoipPool {coip_pool_id}")

        # Remove cidr from poolCidrSet
        if cidr in coip_pool.poolCidrSet:
            coip_pool.poolCidrSet.remove(cidr)

        # Remove CoipCidr object from state
        del self.state.customer_owned_ip_addresses[coip_cidr_key]

        return {
            "coipCidr": coip_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_coip_pool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        coip_pool_id = params.get("CoipPoolId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}

        if not coip_pool_id:
            raise ValueError("CoipPoolId is required")

        coip_pool = self.state.customer_owned_ip_addresses.get(coip_pool_id)
        if not coip_pool:
            raise ValueError(f"CoipPoolId {coip_pool_id} does not exist")

        # Remove all CoipCidr objects associated with this pool
        keys_to_delete = [key for key in self.state.customer_owned_ip_addresses if key.startswith(f"{coip_pool_id}:")]
        for key in keys_to_delete:
            del self.state.customer_owned_ip_addresses[key]

        # Remove the CoipPool itself
        del self.state.customer_owned_ip_addresses[coip_pool_id]

        return {
            "coipPool": coip_pool.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def describe_coip_pools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        pool_ids = params.get("PoolId.N", [])

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}

        # Collect all CoipPools
        all_pools = [
            obj for obj in self.state.customer_owned_ip_addresses.values()
            if isinstance(obj, CoipPool)
        ]

        # Filter by pool_ids if provided
        if pool_ids:
            pool_ids_set = set(pool_ids)
            all_pools = [pool for pool in all_pools if pool.poolId in pool_ids_set]

        # Apply filters
        for filter_obj in filters:
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                continue
            if name == "coip-pool.local-gateway-route-table-id":
                all_pools = [pool for pool in all_pools if pool.localGatewayRouteTableId in values]
            elif name == "coip-pool.pool-id":
                all_pools = [pool for pool in all_pools if pool.poolId in values]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(int(max_results), 1000))

        end_index = start_index + max_results
        paged_pools = all_pools[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(all_pools) else None

        return {
            "coipPoolSet": [pool.to_dict() for pool in paged_pools],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def get_coip_pool_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pool_id = params.get("PoolId")
        if not pool_id:
            raise ValueError("PoolId is required")

        # Validate MaxResults if provided
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        next_token = params.get("NextToken")
        filters = params.get("Filter", [])

        # Validate filters structure
        if not isinstance(filters, list):
            raise ValueError("Filter must be a list if provided")
        for f in filters:
            if not isinstance(f, dict):
                raise ValueError("Each filter must be a dict")
            if "Name" not in f or "Values" not in f:
                raise ValueError("Each filter must have 'Name' and 'Values'")
            if not isinstance(f["Values"], list):
                raise ValueError("Filter Values must be a list")

        # Retrieve the CoipPool from state
        coip_pool = self.state.customer_owned_ip_addresses.get(pool_id)
        if not coip_pool:
            # AWS returns empty results if pool not found, no error
            return {
                "coipAddressUsageSet": [],
                "coipPoolId": pool_id,
                "localGatewayRouteTableId": None,
                "nextToken": None,
                "requestId": self.generate_request_id(),
            }

        # coipAddressUsageSet is a list of CoipAddressUsage objects
        # We assume coip_pool has an attribute or dict key 'address_usage' which is a dict of allocationId -> CoipAddressUsage
        # If not present, treat as empty
        address_usage_dict = getattr(coip_pool, "address_usage", {})
        if not isinstance(address_usage_dict, dict):
            address_usage_dict = {}

        # Convert dict values to list
        address_usage_list = list(address_usage_dict.values())

        # Apply filters
        def matches_filter(usage: CoipAddressUsage, filter_obj: Dict[str, Any]) -> bool:
            name = filter_obj["Name"]
            values = filter_obj["Values"]
            # Map filter names to CoipAddressUsage attributes
            if name == "coip-address-usage.allocation-id":
                return usage.allocationId in values
            elif name == "coip-address-usage.aws-account-id":
                return usage.awsAccountId in values
            elif name == "coip-address-usage.aws-service":
                return usage.awsService in values
            elif name == "coip-address-usage.co-ip":
                return usage.coIp in values
            else:
                # Unknown filter name, ignore filter (AWS ignores unknown filters)
                return True

        # Filter address_usage_list by all filters (AND logic)
        filtered_usage = []
        for usage in address_usage_list:
            if all(matches_filter(usage, f) for f in filters):
                filtered_usage.append(usage)

        # Pagination logic
        # next_token is expected to be a string representing the index offset in the filtered list
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index >= len(filtered_usage):
                    start_index = 0
            except Exception:
                start_index = 0

        # Determine end index based on max_results
        end_index = len(filtered_usage)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_usage))

        page_of_usage = filtered_usage[start_index:end_index]

        # Prepare next token if more results remain
        new_next_token = None
        if end_index < len(filtered_usage):
            new_next_token = str(end_index)

        # Prepare response list of dicts
        coip_address_usage_set = []
        for usage in page_of_usage:
            coip_address_usage_set.append({
                "allocationId": usage.allocationId,
                "awsAccountId": usage.awsAccountId,
                "awsService": usage.awsService,
                "coIp": usage.coIp,
            })

        return {
            "coipAddressUsageSet": coip_address_usage_set,
            "coipPoolId": pool_id,
            "localGatewayRouteTableId": getattr(coip_pool, "localGatewayRouteTableId", None),
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class CustomerOwnedIPaddressesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateCoipCidr", self.create_coip_cidr)
        self.register_action("CreateCoipPool", self.create_coip_pool)
        self.register_action("DeleteCoipCidr", self.delete_coip_cidr)
        self.register_action("DeleteCoipPool", self.delete_coip_pool)
        self.register_action("DescribeCoipPools", self.describe_coip_pools)
        self.register_action("GetCoipPoolUsage", self.get_coip_pool_usage)

    def create_coip_cidr(self, params):
        return self.backend.create_coip_cidr(params)

    def create_coip_pool(self, params):
        return self.backend.create_coip_pool(params)

    def delete_coip_cidr(self, params):
        return self.backend.delete_coip_cidr(params)

    def delete_coip_pool(self, params):
        return self.backend.delete_coip_pool(params)

    def describe_coip_pools(self, params):
        return self.backend.describe_coip_pools(params)

    def get_coip_pool_usage(self, params):
        return self.backend.get_coip_pool_usage(params)
