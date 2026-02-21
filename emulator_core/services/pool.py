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
class Pool:
    address_family: str = ""
    allocation_default_netmask_length: int = 0
    allocation_max_netmask_length: int = 0
    allocation_min_netmask_length: int = 0
    allocation_resource_tag_set: List[Any] = field(default_factory=list)
    auto_import: bool = False
    aws_service: str = ""
    description: str = ""
    ipam_arn: str = ""
    ipam_pool_arn: str = ""
    ipam_pool_id: str = ""
    ipam_region: str = ""
    ipam_scope_arn: str = ""
    ipam_scope_type: str = ""
    locale: str = ""
    owner_id: str = ""
    pool_depth: int = 0
    public_ip_source: str = ""
    publicly_advertisable: bool = False
    source_ipam_pool_id: str = ""
    source_resource: Dict[str, Any] = field(default_factory=dict)
    state: str = ""
    state_message: str = ""
    tag_set: List[Any] = field(default_factory=list)

    ipam_scope_id: str = ""
    pool_type: str = "ipam"
    ipam_pool_allocations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    ipam_pool_cidrs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    pool_id: str = ""
    network_border_group: str = ""
    pool_address_range_set: List[Dict[str, Any]] = field(default_factory=list)
    total_address_count: int = 0
    total_available_address_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "addressFamily": self.address_family,
            "allocationDefaultNetmaskLength": self.allocation_default_netmask_length,
            "allocationMaxNetmaskLength": self.allocation_max_netmask_length,
            "allocationMinNetmaskLength": self.allocation_min_netmask_length,
            "allocationResourceTagSet": self.allocation_resource_tag_set,
            "autoImport": self.auto_import,
            "awsService": self.aws_service,
            "description": self.description,
            "ipamArn": self.ipam_arn,
            "ipamPoolArn": self.ipam_pool_arn,
            "ipamPoolId": self.ipam_pool_id,
            "ipamRegion": self.ipam_region,
            "ipamScopeArn": self.ipam_scope_arn,
            "ipamScopeType": self.ipam_scope_type,
            "locale": self.locale,
            "ownerId": self.owner_id,
            "poolDepth": self.pool_depth,
            "publicIpSource": self.public_ip_source,
            "publiclyAdvertisable": self.publicly_advertisable,
            "sourceIpamPoolId": self.source_ipam_pool_id,
            "sourceResource": self.source_resource,
            "state": self.state,
            "stateMessage": self.state_message,
            "tagSet": self.tag_set,
        }

class Pool_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.pools  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            value = params.get(name)
            if value is None or value == "" or value == []:
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_pool_or_error(self, pool_id: str, error_code: str, message: str) -> Any:
        pool = self.resources.get(pool_id)
        if not pool:
            return create_error_response(error_code, message)
        return pool

    def _recalculate_public_pool_counts(self, pool: Pool) -> None:
        total = 0
        available = 0
        for address_range in pool.pool_address_range_set:
            total += int(address_range.get("addressCount") or 0)
            available += int(address_range.get("availableAddressCount") or 0)
        pool.total_address_count = total
        pool.total_available_address_count = available

    def AllocateIpamPoolCidr(self, params: Dict[str, Any]):
        """Allocate a CIDR from an IPAM pool. The Region you use should be the IPAM pool locale. The locale is the AWS Region where this IPAM pool is available for allocations. In IPAM, an allocation is a CIDR assignment from an IPAM pool to another IPAM pool or to a resource. For more information, seeAllocate"""

        error = self._require_params(params, ["IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        cidr = params.get("Cidr") or ""
        netmask_length = params.get("NetmaskLength")
        if not cidr:
            if netmask_length:
                cidr = f"0.0.0.0/{int(netmask_length)}"
            else:
                cidr = "0.0.0.0/0"

        for allocation in (pool.ipam_pool_allocations or {}).values():
            if allocation.get("cidr") == cidr:
                return create_error_response(
                    "InvalidParameterValue",
                    f"CIDR '{cidr}' is already allocated in pool '{pool_id}'",
                )

        allocation_id = self._generate_id("ipam-pool-alloc")
        allocation = {
            "cidr": cidr,
            "description": params.get("Description") or "",
            "ipamPoolAllocationId": allocation_id,
            "resourceId": "",
            "resourceOwner": pool.owner_id or "",
            "resourceRegion": pool.locale or pool.ipam_region or "",
            "resourceType": "manual",
        }

        if str2bool(params.get("PreviewNextCidr")):
            allocation = dict(allocation)
            allocation["ipamPoolAllocationId"] = ""
        else:
            pool.ipam_pool_allocations[allocation_id] = allocation

        return {
            'ipamPoolAllocation': allocation,
            }

    def CreateIpamPool(self, params: Dict[str, Any]):
        """Create an IP address pool for Amazon VPC IP Address Manager (IPAM). In IPAM, a pool is a collection of contiguous IP addresses CIDRs. Pools enable you to organize your IP addresses according to your routing and security needs. For example, if you have separate routing and security needs for developm"""

        error = self._require_params(params, ["AddressFamily", "IpamScopeId"])
        if error:
            return error

        ipam_scope_id = params.get("IpamScopeId")
        scope = self.state.scopes.get(ipam_scope_id)
        if not scope:
            return create_error_response(
                "InvalidIpamScopeId.NotFound",
                f"The ID '{ipam_scope_id}' does not exist",
            )

        def _scope_attr(scope_obj: Any, *keys: str) -> str:
            for key in keys:
                if isinstance(scope_obj, dict) and key in scope_obj:
                    return scope_obj.get(key) or ""
                value = getattr(scope_obj, key, None)
                if value:
                    return value
            return ""

        source_ipam_pool_id = params.get("SourceIpamPoolId") or ""
        if source_ipam_pool_id:
            source_pool = self.resources.get(source_ipam_pool_id)
            if not source_pool:
                return create_error_response(
                    "InvalidIpamPoolId.NotFound",
                    f"The ID '{source_ipam_pool_id}' does not exist",
                )
        else:
            source_pool = None

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            for tag in spec.get("Tags", []) or []:
                tag_set.append({"Key": tag.get("Key", ""), "Value": tag.get("Value", "")})

        allocation_resource_tag_set = params.get("AllocationResourceTag.N", []) or []
        ipam_pool_id = self._generate_id("ipam-pool")
        ipam_region = _scope_attr(scope, "ipam_region", "ipamRegion") or params.get("Locale") or ""
        ipam_scope_arn = _scope_attr(scope, "ipam_scope_arn", "ipamScopeArn")
        ipam_scope_type = _scope_attr(scope, "ipam_scope_type", "ipamScopeType")
        ipam_arn = _scope_attr(scope, "ipam_arn", "ipamArn")
        owner_id = _scope_attr(scope, "owner_id", "ownerId")
        pool_depth = (source_pool.pool_depth + 1) if source_pool else 1
        ipam_pool_arn = f"arn:aws:ec2:{ipam_region}::ipam-pool/{ipam_pool_id}" if ipam_region else f"arn:aws:ec2:::ipam-pool/{ipam_pool_id}"
        source_resource = params.get("SourceResource") if isinstance(params.get("SourceResource"), dict) else {}

        resource = Pool(
            address_family=params.get("AddressFamily") or "",
            allocation_default_netmask_length=params.get("AllocationDefaultNetmaskLength") or 0,
            allocation_max_netmask_length=params.get("AllocationMaxNetmaskLength") or 0,
            allocation_min_netmask_length=params.get("AllocationMinNetmaskLength") or 0,
            allocation_resource_tag_set=allocation_resource_tag_set,
            auto_import=str2bool(params.get("AutoImport")),
            aws_service=params.get("AwsService") or "",
            description=params.get("Description") or "",
            ipam_arn=ipam_arn,
            ipam_pool_arn=ipam_pool_arn,
            ipam_pool_id=ipam_pool_id,
            ipam_region=ipam_region,
            ipam_scope_arn=ipam_scope_arn,
            ipam_scope_type=ipam_scope_type,
            locale=params.get("Locale") or ipam_region,
            owner_id=owner_id,
            pool_depth=pool_depth,
            public_ip_source=params.get("PublicIpSource") or "",
            publicly_advertisable=str2bool(params.get("PubliclyAdvertisable")),
            source_ipam_pool_id=source_ipam_pool_id,
            source_resource=source_resource or {},
            state="create-complete",
            state_message="",
            tag_set=tag_set,
            ipam_scope_id=ipam_scope_id,
            pool_type="ipam",
        )
        self.resources[ipam_pool_id] = resource

        return {
            'ipamPool': resource.to_dict(),
            }

    def CreatePublicIpv4Pool(self, params: Dict[str, Any]):
        """Creates a public IPv4 address pool. A public IPv4 pool is an EC2 IP address pool required for the public IPv4 CIDRs that you own and bring to AWS to manage with IPAM. IPv6 addresses you bring to AWS, however, use IPAM pools only. To monitor the status of pool creation, useDescribePublicIpv4Pools."""

        tag_set: List[Dict[str, Any]] = []
        tag_specs = params.get("TagSpecification.N", []) or []
        if tag_specs:
            matching_tags = None
            for spec in tag_specs:
                if spec.get("ResourceType") == "public-ipv4-pool":
                    matching_tags = spec.get("Tags", [])
                    break
            if matching_tags is None:
                matching_tags = tag_specs[0].get("Tags", [])
            for tag in matching_tags or []:
                tag_set.append({"Key": tag.get("Key", ""), "Value": tag.get("Value", "")})

        pool_id = self._generate_id("ipv4pool")
        resource = Pool(
            description="",
            network_border_group=params.get("NetworkBorderGroup") or "",
            pool_id=pool_id,
            pool_type="public-ipv4",
            pool_address_range_set=[],
            total_address_count=0,
            total_available_address_count=0,
            tag_set=tag_set,
        )
        self.resources[pool_id] = resource

        return {
            'poolId': pool_id,
            }

    def DeleteIpamPool(self, params: Dict[str, Any]):
        """Delete an IPAM pool. You cannot delete an IPAM pool if there are allocations in it or CIDRs provisioned to it. To release 
         allocations, seeReleaseIpamPoolAllocation. To deprovision pool 
         CIDRs, seeDeprovisionIpamPoolCidr. For more information, seeDelete a poolin theAmazon VPC IPAM """

        error = self._require_params(params, ["IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        if pool.ipam_pool_allocations or pool.ipam_pool_cidrs:
            return create_error_response(
                "DependencyViolation",
                "IPAM pool has allocations or CIDRs and cannot be deleted.",
            )

        pool_data = pool.to_dict()
        del self.resources[pool_id]

        return {
            'ipamPool': pool_data,
            }

    def DeletePublicIpv4Pool(self, params: Dict[str, Any]):
        """Delete a public IPv4 pool. A public IPv4 pool is an EC2 IP address pool required for the public IPv4 CIDRs that you own and bring to AWS to manage with IPAM. IPv6 addresses you bring to AWS, however, use IPAM pools only."""

        error = self._require_params(params, ["PoolId"])
        if error:
            return error

        pool_id = params.get("PoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidPublicIpv4PoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "") != "public-ipv4":
            return create_error_response(
                "InvalidPublicIpv4PoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        if pool.pool_address_range_set:
            return create_error_response(
                "DependencyViolation",
                "Public IPv4 pool has address ranges and cannot be deleted.",
            )

        del self.resources[pool_id]

        return {
            'returnValue': True,
            }

    def DeprovisionIpamPoolCidr(self, params: Dict[str, Any]):
        """Deprovision a CIDR provisioned from an IPAM pool. If you deprovision a CIDR from a pool that has a source pool, the CIDR is recycled back into the source pool. For more information, seeDeprovision pool CIDRsin theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        cidr = params.get("Cidr")
        if not cidr:
            return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        cidr_id = None
        cidr_entry = None
        for entry_id, entry in (pool.ipam_pool_cidrs or {}).items():
            if entry.get("cidr") == cidr:
                cidr_id = entry_id
                cidr_entry = entry
                break

        if not cidr_entry:
            return create_error_response(
                "InvalidParameterValue",
                f"CIDR '{cidr}' does not exist in pool '{pool_id}'",
            )

        del pool.ipam_pool_cidrs[cidr_id]

        netmask_length = cidr_entry.get("netmaskLength")
        if netmask_length is None and "/" in cidr:
            try:
                netmask_length = int(cidr.split("/")[-1])
            except ValueError:
                netmask_length = None

        if pool.source_ipam_pool_id:
            source_pool = self.resources.get(pool.source_ipam_pool_id)
            if source_pool and getattr(source_pool, "pool_type", "ipam") == "ipam":
                if not any(item.get("cidr") == cidr for item in source_pool.ipam_pool_cidrs.values()):
                    source_entry_id = self._generate_id("ipam-pool-cidr")
                    source_pool.ipam_pool_cidrs[source_entry_id] = {
                        "cidr": cidr,
                        "failureReason": {},
                        "ipamPoolCidrId": source_entry_id,
                        "netmaskLength": netmask_length or 0,
                        "state": "provisioned",
                    }

        response_entry = {
            "cidr": cidr,
            "failureReason": cidr_entry.get("failureReason") or {},
            "ipamPoolCidrId": cidr_entry.get("ipamPoolCidrId") or cidr_id,
            "netmaskLength": netmask_length or 0,
            "state": "deprovisioned",
        }

        return {
            'ipamPoolCidr': response_entry,
            }

    def DeprovisionPublicIpv4PoolCidr(self, params: Dict[str, Any]):
        """Deprovision a CIDR from a public IPv4 pool."""

        error = self._require_params(params, ["Cidr", "PoolId"])
        if error:
            return error

        pool_id = params.get("PoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidPublicIpv4PoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "") != "public-ipv4":
            return create_error_response(
                "InvalidPublicIpv4PoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        cidr = params.get("Cidr")
        address_range = None
        for entry in pool.pool_address_range_set or []:
            if entry.get("cidr") == cidr:
                address_range = entry
                break

        if not address_range:
            return create_error_response(
                "InvalidParameterValue",
                f"CIDR '{cidr}' does not exist in pool '{pool_id}'",
            )

        pool.pool_address_range_set = [
            entry for entry in pool.pool_address_range_set
            if entry.get("cidr") != cidr
        ]
        self._recalculate_public_pool_counts(pool)

        return {
            'deprovisionedAddressSet': [cidr],
            'poolId': pool_id,
            }

    def DescribeIpamPools(self, params: Dict[str, Any]):
        """Get information about your IPAM pools."""

        ipam_pool_ids = params.get("IpamPoolId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if ipam_pool_ids:
            resources: List[Pool] = []
            for pool_id in ipam_pool_ids:
                pool = self.resources.get(pool_id)
                if not pool or getattr(pool, "pool_type", "ipam") != "ipam":
                    return create_error_response(
                        "InvalidIpamPoolId.NotFound",
                        f"The ID '{pool_id}' does not exist",
                    )
                resources.append(pool)
        else:
            resources = [
                pool for pool in self.resources.values()
                if getattr(pool, "pool_type", "ipam") == "ipam"
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))
        pool_entries = [pool.to_dict() for pool in resources[:max_results]]

        return {
            'ipamPoolSet': pool_entries,
            'nextToken': None,
            }

    def DescribePublicIpv4Pools(self, params: Dict[str, Any]):
        """Describes the specified IPv4 address pools."""

        pool_ids = params.get("PoolId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if pool_ids:
            resources: List[Pool] = []
            for pool_id in pool_ids:
                pool = self.resources.get(pool_id)
                if not pool or getattr(pool, "pool_type", "") != "public-ipv4":
                    return create_error_response(
                        "InvalidPublicIpv4PoolId.NotFound",
                        f"The ID '{pool_id}' does not exist",
                    )
                resources.append(pool)
        else:
            resources = [
                pool for pool in self.resources.values()
                if getattr(pool, "pool_type", "") == "public-ipv4"
            ]

        pool_entries: List[Dict[str, Any]] = []
        for pool in resources:
            self._recalculate_public_pool_counts(pool)
            pool_entries.append({
                "description": pool.description,
                "networkBorderGroup": pool.network_border_group,
                "poolAddressRangeSet": pool.pool_address_range_set,
                "poolId": pool.pool_id,
                "pool_id": pool.pool_id,
                "tagSet": pool.tag_set,
                "totalAddressCount": pool.total_address_count,
                "totalAvailableAddressCount": pool.total_available_address_count,
            })

        pool_entries = apply_filters(pool_entries, params.get("Filter.N", []))
        for entry in pool_entries:
            entry.pop("pool_id", None)

        return {
            'nextToken': None,
            'publicIpv4PoolSet': pool_entries[:max_results],
            }

    def GetIpamPoolAllocations(self, params: Dict[str, Any]):
        """Get a list of all the CIDR allocations in an IPAM pool. The Region you use should be the IPAM pool locale. The locale is the AWS Region where this IPAM pool is available for allocations. If you use this action afterAllocateIpamPoolCidrorReleaseIpamPoolAllocation, note that all EC2 API actions follow"""

        error = self._require_params(params, ["IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        max_results = int(params.get("MaxResults") or 100)
        allocations = list((pool.ipam_pool_allocations or {}).values())

        allocation_id = params.get("IpamPoolAllocationId")
        if allocation_id:
            allocations = [
                allocation for allocation in allocations
                if allocation.get("ipamPoolAllocationId") == allocation_id
            ]

        allocations = apply_filters(allocations, params.get("Filter.N", []))

        return {
            'ipamPoolAllocationSet': allocations[:max_results],
            'nextToken': None,
            }

    def GetIpamPoolCidrs(self, params: Dict[str, Any]):
        """Get the CIDRs provisioned to an IPAM pool."""

        error = self._require_params(params, ["IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        max_results = int(params.get("MaxResults") or 100)
        cidrs = list((pool.ipam_pool_cidrs or {}).values())
        cidrs = apply_filters(cidrs, params.get("Filter.N", []))

        return {
            'ipamPoolCidrSet': cidrs[:max_results],
            'nextToken': None,
            }

    def ModifyIpamPool(self, params: Dict[str, Any]):
        """Modify the configurations of an IPAM pool. For more information, seeModify a poolin theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        if params.get("Description") is not None:
            pool.description = params.get("Description") or ""

        if params.get("AutoImport") is not None:
            pool.auto_import = str2bool(params.get("AutoImport"))

        if params.get("AllocationDefaultNetmaskLength") is not None:
            pool.allocation_default_netmask_length = params.get("AllocationDefaultNetmaskLength") or 0
        elif str2bool(params.get("ClearAllocationDefaultNetmaskLength")):
            pool.allocation_default_netmask_length = 0

        if params.get("AllocationMaxNetmaskLength") is not None:
            pool.allocation_max_netmask_length = params.get("AllocationMaxNetmaskLength") or 0

        if params.get("AllocationMinNetmaskLength") is not None:
            pool.allocation_min_netmask_length = params.get("AllocationMinNetmaskLength") or 0

        allocation_tags = list(pool.allocation_resource_tag_set or [])
        add_tags = params.get("AddAllocationResourceTag.N", []) or []
        for tag in add_tags:
            key = tag.get("Key") if isinstance(tag, dict) else None
            if not key:
                continue
            allocation_tags = [item for item in allocation_tags if item.get("Key") != key]
            allocation_tags.append(tag)

        remove_tags = params.get("RemoveAllocationResourceTag.N", []) or []
        remove_keys = {
            tag.get("Key") for tag in remove_tags
            if isinstance(tag, dict) and tag.get("Key")
        }
        if remove_keys:
            allocation_tags = [item for item in allocation_tags if item.get("Key") not in remove_keys]

        pool.allocation_resource_tag_set = allocation_tags

        return {
            'ipamPool': pool.to_dict(),
            }

    def ProvisionIpamPoolCidr(self, params: Dict[str, Any]):
        """Provision a CIDR to an IPAM pool. You can use this action to provision new CIDRs to a top-level pool or to transfer a CIDR from a top-level pool to a pool within it. For more information, seeProvision CIDRs to poolsin theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        cidr = params.get("Cidr")
        netmask_length = params.get("NetmaskLength")
        if not cidr:
            if netmask_length:
                cidr = f"0.0.0.0/{int(netmask_length)}"
            else:
                return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        if any(entry.get("cidr") == cidr for entry in (pool.ipam_pool_cidrs or {}).values()):
            return create_error_response(
                "InvalidParameterValue",
                f"CIDR '{cidr}' already exists in pool '{pool_id}'",
            )

        cidr_id = self._generate_id("ipam-pool-cidr")
        if netmask_length is None and "/" in cidr:
            try:
                netmask_length = int(cidr.split("/")[-1])
            except ValueError:
                netmask_length = 0

        entry = {
            "cidr": cidr,
            "failureReason": {},
            "ipamPoolCidrId": cidr_id,
            "netmaskLength": int(netmask_length or 0),
            "state": "provisioned",
        }
        pool.ipam_pool_cidrs[cidr_id] = entry

        if pool.source_ipam_pool_id:
            source_pool = self.resources.get(pool.source_ipam_pool_id)
            if source_pool and getattr(source_pool, "pool_type", "ipam") == "ipam":
                source_pool.ipam_pool_cidrs = {
                    entry_id: item
                    for entry_id, item in source_pool.ipam_pool_cidrs.items()
                    if item.get("cidr") != cidr
                }

        return {
            'ipamPoolCidr': entry,
            }

    def ProvisionPublicIpv4PoolCidr(self, params: Dict[str, Any]):
        """Provision a CIDR to a public IPv4 pool. For more information about IPAM, seeWhat is IPAM?in theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["IpamPoolId", "NetmaskLength", "PoolId"])
        if error:
            return error

        ipam_pool_id = params.get("IpamPoolId")
        ipam_pool = self.resources.get(ipam_pool_id)
        if not ipam_pool or getattr(ipam_pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{ipam_pool_id}' does not exist",
            )

        pool_id = params.get("PoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidPublicIpv4PoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "") != "public-ipv4":
            return create_error_response(
                "InvalidPublicIpv4PoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        netmask_length = int(params.get("NetmaskLength") or 0)
        cidr = f"0.0.0.0/{netmask_length}"
        if any(entry.get("cidr") == cidr for entry in pool.pool_address_range_set):
            return create_error_response(
                "InvalidParameterValue",
                f"CIDR '{cidr}' already exists in pool '{pool_id}'",
            )

        address_range = {
            "cidr": cidr,
            "addressCount": 0,
            "availableAddressCount": 0,
            "firstAddress": "",
            "lastAddress": "",
        }
        pool.pool_address_range_set.append(address_range)
        self._recalculate_public_pool_counts(pool)

        return {
            'poolAddressRange': {
                'addressCount': address_range.get("addressCount"),
                'availableAddressCount': address_range.get("availableAddressCount"),
                'firstAddress': address_range.get("firstAddress"),
                'lastAddress': address_range.get("lastAddress"),
                },
            'poolId': pool_id,
            }

    def ReleaseIpamPoolAllocation(self, params: Dict[str, Any]):
        """Release an allocation within an IPAM pool. The Region you use should be the IPAM pool locale. The locale is the AWS Region where this IPAM pool is available for allocations. You can only use this action to release manual allocations. To remove an allocation for a resource without deleting the resour"""

        error = self._require_params(params, ["Cidr", "IpamPoolAllocationId", "IpamPoolId"])
        if error:
            return error

        pool_id = params.get("IpamPoolId")
        pool = self._get_pool_or_error(
            pool_id,
            "InvalidIpamPoolId.NotFound",
            f"The ID '{pool_id}' does not exist",
        )
        if is_error_response(pool):
            return pool

        if getattr(pool, "pool_type", "ipam") != "ipam":
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        allocation_id = params.get("IpamPoolAllocationId")
        allocation = (pool.ipam_pool_allocations or {}).get(allocation_id)
        if not allocation or allocation.get("cidr") != params.get("Cidr"):
            return create_error_response(
                "InvalidIpamPoolAllocationId.NotFound",
                f"The allocation '{allocation_id}' does not exist in pool '{pool_id}'",
            )

        del pool.ipam_pool_allocations[allocation_id]

        return {
            'success': [allocation_id],
            }

    def _generate_id(self, prefix: str = 'ipam') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class pool_RequestParser:
    @staticmethod
    def parse_allocate_ipam_pool_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllowedCidr.N": get_indexed_list(md, "AllowedCidr"),
            "Cidr": get_scalar(md, "Cidr"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DisallowedCidr.N": get_indexed_list(md, "DisallowedCidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "NetmaskLength": get_int(md, "NetmaskLength"),
            "PreviewNextCidr": get_scalar(md, "PreviewNextCidr"),
        }

    @staticmethod
    def parse_create_ipam_pool_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddressFamily": get_scalar(md, "AddressFamily"),
            "AllocationDefaultNetmaskLength": get_int(md, "AllocationDefaultNetmaskLength"),
            "AllocationMaxNetmaskLength": get_int(md, "AllocationMaxNetmaskLength"),
            "AllocationMinNetmaskLength": get_int(md, "AllocationMinNetmaskLength"),
            "AllocationResourceTag.N": get_indexed_list(md, "AllocationResourceTag"),
            "AutoImport": get_scalar(md, "AutoImport"),
            "AwsService": get_scalar(md, "AwsService"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamScopeId": get_scalar(md, "IpamScopeId"),
            "Locale": get_scalar(md, "Locale"),
            "PublicIpSource": get_scalar(md, "PublicIpSource"),
            "PubliclyAdvertisable": get_scalar(md, "PubliclyAdvertisable"),
            "SourceIpamPoolId": get_scalar(md, "SourceIpamPoolId"),
            "SourceResource": get_scalar(md, "SourceResource"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_public_ipv4_pool_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkBorderGroup": get_scalar(md, "NetworkBorderGroup"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_ipam_pool_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cascade": get_scalar(md, "Cascade"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
        }

    @staticmethod
    def parse_delete_public_ipv4_pool_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkBorderGroup": get_scalar(md, "NetworkBorderGroup"),
            "PoolId": get_scalar(md, "PoolId"),
        }

    @staticmethod
    def parse_deprovision_ipam_pool_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
        }

    @staticmethod
    def parse_deprovision_public_ipv4_pool_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PoolId": get_scalar(md, "PoolId"),
        }

    @staticmethod
    def parse_describe_ipam_pools_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamPoolId.N": get_indexed_list(md, "IpamPoolId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_public_ipv4_pools_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PoolId.N": get_indexed_list(md, "PoolId"),
        }

    @staticmethod
    def parse_get_ipam_pool_allocations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamPoolAllocationId": get_scalar(md, "IpamPoolAllocationId"),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_ipam_pool_cidrs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_modify_ipam_pool_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddAllocationResourceTag.N": get_indexed_list(md, "AddAllocationResourceTag"),
            "AllocationDefaultNetmaskLength": get_int(md, "AllocationDefaultNetmaskLength"),
            "AllocationMaxNetmaskLength": get_int(md, "AllocationMaxNetmaskLength"),
            "AllocationMinNetmaskLength": get_int(md, "AllocationMinNetmaskLength"),
            "AutoImport": get_scalar(md, "AutoImport"),
            "ClearAllocationDefaultNetmaskLength": get_scalar(md, "ClearAllocationDefaultNetmaskLength"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "RemoveAllocationResourceTag.N": get_indexed_list(md, "RemoveAllocationResourceTag"),
        }

    @staticmethod
    def parse_provision_ipam_pool_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "CidrAuthorizationContext": get_scalar(md, "CidrAuthorizationContext"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamExternalResourceVerificationTokenId": get_scalar(md, "IpamExternalResourceVerificationTokenId"),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "NetmaskLength": get_int(md, "NetmaskLength"),
            "VerificationMethod": get_scalar(md, "VerificationMethod"),
        }

    @staticmethod
    def parse_provision_public_ipv4_pool_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "NetmaskLength": get_int(md, "NetmaskLength"),
            "NetworkBorderGroup": get_scalar(md, "NetworkBorderGroup"),
            "PoolId": get_scalar(md, "PoolId"),
        }

    @staticmethod
    def parse_release_ipam_pool_allocation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolAllocationId": get_scalar(md, "IpamPoolAllocationId"),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AllocateIpamPoolCidr": pool_RequestParser.parse_allocate_ipam_pool_cidr_request,
            "CreateIpamPool": pool_RequestParser.parse_create_ipam_pool_request,
            "CreatePublicIpv4Pool": pool_RequestParser.parse_create_public_ipv4_pool_request,
            "DeleteIpamPool": pool_RequestParser.parse_delete_ipam_pool_request,
            "DeletePublicIpv4Pool": pool_RequestParser.parse_delete_public_ipv4_pool_request,
            "DeprovisionIpamPoolCidr": pool_RequestParser.parse_deprovision_ipam_pool_cidr_request,
            "DeprovisionPublicIpv4PoolCidr": pool_RequestParser.parse_deprovision_public_ipv4_pool_cidr_request,
            "DescribeIpamPools": pool_RequestParser.parse_describe_ipam_pools_request,
            "DescribePublicIpv4Pools": pool_RequestParser.parse_describe_public_ipv4_pools_request,
            "GetIpamPoolAllocations": pool_RequestParser.parse_get_ipam_pool_allocations_request,
            "GetIpamPoolCidrs": pool_RequestParser.parse_get_ipam_pool_cidrs_request,
            "ModifyIpamPool": pool_RequestParser.parse_modify_ipam_pool_request,
            "ProvisionIpamPoolCidr": pool_RequestParser.parse_provision_ipam_pool_cidr_request,
            "ProvisionPublicIpv4PoolCidr": pool_RequestParser.parse_provision_public_ipv4_pool_cidr_request,
            "ReleaseIpamPoolAllocation": pool_RequestParser.parse_release_ipam_pool_allocation_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class pool_ResponseSerializer:
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
                xml_parts.extend(pool_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(pool_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(pool_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(pool_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_allocate_ipam_pool_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AllocateIpamPoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPoolAllocation
        _ipamPoolAllocation_key = None
        if "ipamPoolAllocation" in data:
            _ipamPoolAllocation_key = "ipamPoolAllocation"
        elif "IpamPoolAllocation" in data:
            _ipamPoolAllocation_key = "IpamPoolAllocation"
        if _ipamPoolAllocation_key:
            param_data = data[_ipamPoolAllocation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamPoolAllocation>')
            xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamPoolAllocation>')
        xml_parts.append(f'</AllocateIpamPoolCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_ipam_pool_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateIpamPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPool
        _ipamPool_key = None
        if "ipamPool" in data:
            _ipamPool_key = "ipamPool"
        elif "IpamPool" in data:
            _ipamPool_key = "IpamPool"
        if _ipamPool_key:
            param_data = data[_ipamPool_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamPool>')
            xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamPool>')
        xml_parts.append(f'</CreateIpamPoolResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_public_ipv4_pool_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreatePublicIpv4PoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize poolId
        _poolId_key = None
        if "poolId" in data:
            _poolId_key = "poolId"
        elif "PoolId" in data:
            _poolId_key = "PoolId"
        if _poolId_key:
            param_data = data[_poolId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<poolId>{esc(str(param_data))}</poolId>')
        xml_parts.append(f'</CreatePublicIpv4PoolResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_ipam_pool_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteIpamPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPool
        _ipamPool_key = None
        if "ipamPool" in data:
            _ipamPool_key = "ipamPool"
        elif "IpamPool" in data:
            _ipamPool_key = "IpamPool"
        if _ipamPool_key:
            param_data = data[_ipamPool_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamPool>')
            xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamPool>')
        xml_parts.append(f'</DeleteIpamPoolResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_public_ipv4_pool_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeletePublicIpv4PoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize returnValue
        _returnValue_key = None
        if "returnValue" in data:
            _returnValue_key = "returnValue"
        elif "ReturnValue" in data:
            _returnValue_key = "ReturnValue"
        if _returnValue_key:
            param_data = data[_returnValue_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<returnValue>{esc(str(param_data))}</returnValue>')
        xml_parts.append(f'</DeletePublicIpv4PoolResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_deprovision_ipam_pool_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeprovisionIpamPoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPoolCidr
        _ipamPoolCidr_key = None
        if "ipamPoolCidr" in data:
            _ipamPoolCidr_key = "ipamPoolCidr"
        elif "IpamPoolCidr" in data:
            _ipamPoolCidr_key = "IpamPoolCidr"
        if _ipamPoolCidr_key:
            param_data = data[_ipamPoolCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamPoolCidr>')
            xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamPoolCidr>')
        xml_parts.append(f'</DeprovisionIpamPoolCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_deprovision_public_ipv4_pool_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeprovisionPublicIpv4PoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize deprovisionedAddressSet
        _deprovisionedAddressSet_key = None
        if "deprovisionedAddressSet" in data:
            _deprovisionedAddressSet_key = "deprovisionedAddressSet"
        elif "DeprovisionedAddressSet" in data:
            _deprovisionedAddressSet_key = "DeprovisionedAddressSet"
        elif "DeprovisionedAddresss" in data:
            _deprovisionedAddressSet_key = "DeprovisionedAddresss"
        if _deprovisionedAddressSet_key:
            param_data = data[_deprovisionedAddressSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<deprovisionedAddressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</deprovisionedAddressSet>')
            else:
                xml_parts.append(f'{indent_str}<deprovisionedAddressSet/>')
        # Serialize poolId
        _poolId_key = None
        if "poolId" in data:
            _poolId_key = "poolId"
        elif "PoolId" in data:
            _poolId_key = "PoolId"
        if _poolId_key:
            param_data = data[_poolId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<poolId>{esc(str(param_data))}</poolId>')
        xml_parts.append(f'</DeprovisionPublicIpv4PoolCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipam_pools_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpamPoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPoolSet
        _ipamPoolSet_key = None
        if "ipamPoolSet" in data:
            _ipamPoolSet_key = "ipamPoolSet"
        elif "IpamPoolSet" in data:
            _ipamPoolSet_key = "IpamPoolSet"
        elif "IpamPools" in data:
            _ipamPoolSet_key = "IpamPools"
        if _ipamPoolSet_key:
            param_data = data[_ipamPoolSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamPoolSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamPoolSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamPoolSet/>')
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
        xml_parts.append(f'</DescribeIpamPoolsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_public_ipv4_pools_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribePublicIpv4PoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize publicIpv4PoolSet
        _publicIpv4PoolSet_key = None
        if "publicIpv4PoolSet" in data:
            _publicIpv4PoolSet_key = "publicIpv4PoolSet"
        elif "PublicIpv4PoolSet" in data:
            _publicIpv4PoolSet_key = "PublicIpv4PoolSet"
        elif "PublicIpv4Pools" in data:
            _publicIpv4PoolSet_key = "PublicIpv4Pools"
        if _publicIpv4PoolSet_key:
            param_data = data[_publicIpv4PoolSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<publicIpv4PoolSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</publicIpv4PoolSet>')
            else:
                xml_parts.append(f'{indent_str}<publicIpv4PoolSet/>')
        xml_parts.append(f'</DescribePublicIpv4PoolsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ipam_pool_allocations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetIpamPoolAllocationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPoolAllocationSet
        _ipamPoolAllocationSet_key = None
        if "ipamPoolAllocationSet" in data:
            _ipamPoolAllocationSet_key = "ipamPoolAllocationSet"
        elif "IpamPoolAllocationSet" in data:
            _ipamPoolAllocationSet_key = "IpamPoolAllocationSet"
        elif "IpamPoolAllocations" in data:
            _ipamPoolAllocationSet_key = "IpamPoolAllocations"
        if _ipamPoolAllocationSet_key:
            param_data = data[_ipamPoolAllocationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamPoolAllocationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamPoolAllocationSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamPoolAllocationSet/>')
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
        xml_parts.append(f'</GetIpamPoolAllocationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ipam_pool_cidrs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetIpamPoolCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPoolCidrSet
        _ipamPoolCidrSet_key = None
        if "ipamPoolCidrSet" in data:
            _ipamPoolCidrSet_key = "ipamPoolCidrSet"
        elif "IpamPoolCidrSet" in data:
            _ipamPoolCidrSet_key = "IpamPoolCidrSet"
        elif "IpamPoolCidrs" in data:
            _ipamPoolCidrSet_key = "IpamPoolCidrs"
        if _ipamPoolCidrSet_key:
            param_data = data[_ipamPoolCidrSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamPoolCidrSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamPoolCidrSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamPoolCidrSet/>')
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
        xml_parts.append(f'</GetIpamPoolCidrsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_ipam_pool_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyIpamPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPool
        _ipamPool_key = None
        if "ipamPool" in data:
            _ipamPool_key = "ipamPool"
        elif "IpamPool" in data:
            _ipamPool_key = "IpamPool"
        if _ipamPool_key:
            param_data = data[_ipamPool_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamPool>')
            xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamPool>')
        xml_parts.append(f'</ModifyIpamPoolResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_provision_ipam_pool_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ProvisionIpamPoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamPoolCidr
        _ipamPoolCidr_key = None
        if "ipamPoolCidr" in data:
            _ipamPoolCidr_key = "ipamPoolCidr"
        elif "IpamPoolCidr" in data:
            _ipamPoolCidr_key = "IpamPoolCidr"
        if _ipamPoolCidr_key:
            param_data = data[_ipamPoolCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamPoolCidr>')
            xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamPoolCidr>')
        xml_parts.append(f'</ProvisionIpamPoolCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_provision_public_ipv4_pool_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ProvisionPublicIpv4PoolCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize poolAddressRange
        _poolAddressRange_key = None
        if "poolAddressRange" in data:
            _poolAddressRange_key = "poolAddressRange"
        elif "PoolAddressRange" in data:
            _poolAddressRange_key = "PoolAddressRange"
        if _poolAddressRange_key:
            param_data = data[_poolAddressRange_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<poolAddressRange>')
            xml_parts.extend(pool_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</poolAddressRange>')
        # Serialize poolId
        _poolId_key = None
        if "poolId" in data:
            _poolId_key = "poolId"
        elif "PoolId" in data:
            _poolId_key = "PoolId"
        if _poolId_key:
            param_data = data[_poolId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<poolId>{esc(str(param_data))}</poolId>')
        xml_parts.append(f'</ProvisionPublicIpv4PoolCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_release_ipam_pool_allocation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReleaseIpamPoolAllocationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize success
        _success_key = None
        if "success" in data:
            _success_key = "success"
        elif "Success" in data:
            _success_key = "Success"
        if _success_key:
            param_data = data[_success_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</successSet>')
            else:
                xml_parts.append(f'{indent_str}<successSet/>')
        xml_parts.append(f'</ReleaseIpamPoolAllocationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AllocateIpamPoolCidr": pool_ResponseSerializer.serialize_allocate_ipam_pool_cidr_response,
            "CreateIpamPool": pool_ResponseSerializer.serialize_create_ipam_pool_response,
            "CreatePublicIpv4Pool": pool_ResponseSerializer.serialize_create_public_ipv4_pool_response,
            "DeleteIpamPool": pool_ResponseSerializer.serialize_delete_ipam_pool_response,
            "DeletePublicIpv4Pool": pool_ResponseSerializer.serialize_delete_public_ipv4_pool_response,
            "DeprovisionIpamPoolCidr": pool_ResponseSerializer.serialize_deprovision_ipam_pool_cidr_response,
            "DeprovisionPublicIpv4PoolCidr": pool_ResponseSerializer.serialize_deprovision_public_ipv4_pool_cidr_response,
            "DescribeIpamPools": pool_ResponseSerializer.serialize_describe_ipam_pools_response,
            "DescribePublicIpv4Pools": pool_ResponseSerializer.serialize_describe_public_ipv4_pools_response,
            "GetIpamPoolAllocations": pool_ResponseSerializer.serialize_get_ipam_pool_allocations_response,
            "GetIpamPoolCidrs": pool_ResponseSerializer.serialize_get_ipam_pool_cidrs_response,
            "ModifyIpamPool": pool_ResponseSerializer.serialize_modify_ipam_pool_response,
            "ProvisionIpamPoolCidr": pool_ResponseSerializer.serialize_provision_ipam_pool_cidr_response,
            "ProvisionPublicIpv4PoolCidr": pool_ResponseSerializer.serialize_provision_public_ipv4_pool_cidr_response,
            "ReleaseIpamPoolAllocation": pool_ResponseSerializer.serialize_release_ipam_pool_allocation_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

