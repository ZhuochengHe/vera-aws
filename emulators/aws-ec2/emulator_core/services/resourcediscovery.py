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
class ResourceDiscovery:
    ipam_arn: str = ""
    ipam_id: str = ""
    ipam_region: str = ""
    ipam_resource_discovery_association_arn: str = ""
    ipam_resource_discovery_association_id: str = ""
    ipam_resource_discovery_id: str = ""
    is_default: bool = False
    owner_id: str = ""
    resource_discovery_status: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)

    description: str = ""
    ipam_resource_discovery_arn: str = ""
    ipam_resource_discovery_region: str = ""
    operating_region_set: List[Dict[str, Any]] = field(default_factory=list)
    organizational_unit_exclusion_set: List[Dict[str, Any]] = field(default_factory=list)
    discovered_accounts: List[Dict[str, Any]] = field(default_factory=list)
    discovered_public_addresses: List[Dict[str, Any]] = field(default_factory=list)
    discovered_resource_cidrs: List[Dict[str, Any]] = field(default_factory=list)
    resource_cidrs: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ipamArn": self.ipam_arn,
            "ipamId": self.ipam_id,
            "ipamRegion": self.ipam_region,
            "ipamResourceDiscoveryAssociationArn": self.ipam_resource_discovery_association_arn,
            "ipamResourceDiscoveryAssociationId": self.ipam_resource_discovery_association_id,
            "ipamResourceDiscoveryId": self.ipam_resource_discovery_id,
            "isDefault": self.is_default,
            "ownerId": self.owner_id,
            "resourceDiscoveryStatus": self.resource_discovery_status,
            "state": self.state,
            "tagSet": self.tag_set,
            "description": self.description,
            "ipamResourceDiscoveryArn": self.ipam_resource_discovery_arn,
            "ipamResourceDiscoveryRegion": self.ipam_resource_discovery_region,
            "operatingRegionSet": self.operating_region_set,
            "organizationalUnitExclusionSet": self.organizational_unit_exclusion_set,
            "discoveredAccounts": self.discovered_accounts,
            "discoveredPublicAddresses": self.discovered_public_addresses,
            "discoveredResourceCidrs": self.discovered_resource_cidrs,
            "resourceCidrs": self.resource_cidrs,
        }

class ResourceDiscovery_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.resource_discoveries  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.ipams.get(params['ipam_id']).resource_discovery_ids.append(new_id)
    #   Delete: self.state.ipams.get(resource.ipam_id).resource_discovery_ids.remove(resource_id)


    def _require_params(self, params: Dict[str, Any], names: List[str]):
        for name in names:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(self, store: Dict[str, Any], resource_id: str, error_code: str, message: Optional[str] = None):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message or f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources = []
        for resource_id in resource_ids:
            resource = store.get(resource_id)
            if not resource:
                return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
            resources.append(resource)
        return resources, None

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: str = "ipam-resource-discovery") -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def _paginate(self, items: List[Any], max_results: int, next_token: Optional[str]) -> Dict[str, Any]:
        start = int(next_token or 0)
        end = start + max_results
        sliced = items[start:end]
        new_token = str(end) if end < len(items) else None
        return {"items": sliced, "next_token": new_token}

    def _resource_discovery_to_dict(self, resource: ResourceDiscovery) -> Dict[str, Any]:
        return {
            "description": resource.description,
            "ipamResourceDiscoveryArn": resource.ipam_resource_discovery_arn,
            "ipamResourceDiscoveryId": resource.ipam_resource_discovery_id,
            "ipamResourceDiscoveryRegion": resource.ipam_resource_discovery_region,
            "isDefault": resource.is_default,
            "operatingRegionSet": resource.operating_region_set,
            "organizationalUnitExclusionSet": resource.organizational_unit_exclusion_set,
            "ownerId": resource.owner_id,
            "state": resource.state,
            "tagSet": resource.tag_set,
        }

    def _resource_discovery_association_to_dict(self, resource: ResourceDiscovery) -> Dict[str, Any]:
        return {
            "ipamArn": resource.ipam_arn,
            "ipamId": resource.ipam_id,
            "ipamRegion": resource.ipam_region,
            "ipamResourceDiscoveryAssociationArn": resource.ipam_resource_discovery_association_arn,
            "ipamResourceDiscoveryAssociationId": resource.ipam_resource_discovery_association_id,
            "ipamResourceDiscoveryId": resource.ipam_resource_discovery_id,
            "isDefault": resource.is_default,
            "ownerId": resource.owner_id,
            "resourceDiscoveryStatus": resource.resource_discovery_status,
            "state": resource.state,
            "tagSet": resource.tag_set,
        }

    def AssociateIpamResourceDiscovery(self, params: Dict[str, Any]):
        """Associates an IPAM resource discovery with an Amazon VPC IPAM. A resource discovery is an IPAM component that enables IPAM to manage and monitor resources that belong to the owning account."""

        error = self._require_params(params, ["IpamId", "IpamResourceDiscoveryId"])
        if error:
            return error

        ipam_id = params.get("IpamId")
        ipam = self.state.ipams.get(ipam_id)
        if not ipam:
            return create_error_response("InvalidIpamID.NotFound", f"IPAM '{ipam_id}' does not exist.")

        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        resource, error = self._get_resource_or_error(
            self.resources,
            ipam_resource_discovery_id,
            "InvalidIpamResourceDiscoveryId.NotFound",
        )
        if error:
            return error

        if not resource.ipam_resource_discovery_association_id:
            association_id = self._generate_id("ipam-rd-assoc")
        else:
            association_id = resource.ipam_resource_discovery_association_id
        ipam_region = ipam.ipam_region or "us-east-1"
        association_arn = (
            f"arn:aws:ec2:{ipam_region}::ipam-resource-discovery-association/{association_id}"
        )

        resource.ipam_id = ipam_id
        resource.ipam_arn = ipam.ipam_arn
        resource.ipam_region = ipam_region
        resource.ipam_resource_discovery_association_id = association_id
        resource.ipam_resource_discovery_association_arn = association_arn
        resource.resource_discovery_status = "associated"
        resource.state = "associated"

        tag_set = self._extract_tags(params.get("TagSpecification.N", []))
        if tag_set:
            resource.tag_set = tag_set

        if hasattr(ipam, "resource_discovery_ids"):
            if ipam_resource_discovery_id not in ipam.resource_discovery_ids:
                ipam.resource_discovery_ids.append(ipam_resource_discovery_id)
        if hasattr(ipam, "resource_discovery_association_count"):
            ipam.resource_discovery_association_count = len(getattr(ipam, "resource_discovery_ids", []))

        return {
            'ipamResourceDiscoveryAssociation': self._resource_discovery_association_to_dict(resource),
            }

    def CreateIpamResourceDiscovery(self, params: Dict[str, Any]):
        """Creates an IPAM resource discovery. A resource discovery is an IPAM component that enables IPAM to manage and monitor resources that belong to the owning account."""

        operating_region_set: List[Dict[str, Any]] = []
        for region in params.get("OperatingRegion.N", []) or []:
            if isinstance(region, dict):
                region_name = region.get("RegionName") or region.get("regionName") or region.get("Region")
            else:
                region_name = region
            if region_name:
                operating_region_set.append({"regionName": region_name})

        ipam_resource_discovery_id = self._generate_id("ipam-res-disco")
        ipam_resource_discovery_region = "us-east-1"
        if not operating_region_set:
            operating_region_set = [{"regionName": ipam_resource_discovery_region}]
        ipam_resource_discovery_arn = (
            f"arn:aws:ec2:{ipam_resource_discovery_region}::ipam-resource-discovery/{ipam_resource_discovery_id}"
        )
        tag_set = self._extract_tags(params.get("TagSpecification.N", []))

        resource = ResourceDiscovery(
            description=params.get("Description") or "",
            ipam_resource_discovery_arn=ipam_resource_discovery_arn,
            ipam_resource_discovery_id=ipam_resource_discovery_id,
            ipam_resource_discovery_region=ipam_resource_discovery_region,
            is_default=False,
            operating_region_set=operating_region_set,
            organizational_unit_exclusion_set=[],
            owner_id="",
            state="create-complete",
            tag_set=tag_set,
        )
        self.resources[ipam_resource_discovery_id] = resource

        return {
            'ipamResourceDiscovery': self._resource_discovery_to_dict(resource),
            }

    def DeleteIpamResourceDiscovery(self, params: Dict[str, Any]):
        """Deletes an IPAM resource discovery. A resource discovery is an IPAM component that enables IPAM to manage and monitor resources that belong to the owning account."""

        error = self._require_params(params, ["IpamResourceDiscoveryId"])
        if error:
            return error

        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        resource, error = self._get_resource_or_error(
            self.resources,
            ipam_resource_discovery_id,
            "InvalidIpamResourceDiscoveryId.NotFound",
        )
        if error:
            return error

        if resource.ipam_id:
            ipam = self.state.ipams.get(resource.ipam_id)
            if ipam and hasattr(ipam, "resource_discovery_ids"):
                if ipam_resource_discovery_id in ipam.resource_discovery_ids:
                    ipam.resource_discovery_ids.remove(ipam_resource_discovery_id)
            if ipam and hasattr(ipam, "resource_discovery_association_count"):
                ipam.resource_discovery_association_count = len(getattr(ipam, "resource_discovery_ids", []))

        resource_data = self._resource_discovery_to_dict(resource)
        del self.resources[ipam_resource_discovery_id]

        return {
            'ipamResourceDiscovery': resource_data,
            }

    def DescribeIpamResourceDiscoveries(self, params: Dict[str, Any]):
        """Describes IPAM resource discoveries. A resource discovery is an IPAM component that enables IPAM to manage and monitor resources that belong to the owning account."""

        ipam_resource_discovery_ids = params.get("IpamResourceDiscoveryId.N", []) or []
        if ipam_resource_discovery_ids:
            resources, error = self._get_resources_by_ids(
                self.resources,
                ipam_resource_discovery_ids,
                "InvalidIpamResourceDiscoveryId.NotFound",
            )
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        pagination = self._paginate(
            resources,
            int(params.get("MaxResults") or 100),
            params.get("NextToken"),
        )
        return {
            'ipamResourceDiscoverySet': [
                self._resource_discovery_to_dict(resource) for resource in pagination["items"]
            ],
            'nextToken': pagination["next_token"],
            }

    def DescribeIpamResourceDiscoveryAssociations(self, params: Dict[str, Any]):
        """Describes resource discovery association with an Amazon VPC IPAM. An associated resource discovery is a resource discovery that has been associated with an IPAM.."""

        association_ids = params.get("IpamResourceDiscoveryAssociationId.N", []) or []
        if association_ids:
            resources: List[ResourceDiscovery] = []
            for association_id in association_ids:
                match = None
                for resource in self.resources.values():
                    if resource.ipam_resource_discovery_association_id == association_id:
                        match = resource
                        break
                if not match:
                    return create_error_response(
                        "InvalidIpamResourceDiscoveryAssociationId.NotFound",
                        f"The ID '{association_id}' does not exist",
                    )
                resources.append(match)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        pagination = self._paginate(
            resources,
            int(params.get("MaxResults") or 100),
            params.get("NextToken"),
        )
        return {
            'ipamResourceDiscoveryAssociationSet': [
                self._resource_discovery_association_to_dict(resource)
                for resource in pagination["items"]
            ],
            'nextToken': pagination["next_token"],
            }

    def DisassociateIpamResourceDiscovery(self, params: Dict[str, Any]):
        """Disassociates a resource discovery from an Amazon VPC IPAM. A resource discovery is an IPAM component that enables IPAM to manage and monitor resources that belong to the owning account."""

        error = self._require_params(params, ["IpamResourceDiscoveryAssociationId"])
        if error:
            return error

        association_id = params.get("IpamResourceDiscoveryAssociationId")
        match = None
        for resource in self.resources.values():
            if resource.ipam_resource_discovery_association_id == association_id:
                match = resource
                break
        if not match:
            return create_error_response(
                "InvalidIpamResourceDiscoveryAssociationId.NotFound",
                f"The ID '{association_id}' does not exist",
            )

        ipam_id = match.ipam_id
        ipam = self.state.ipams.get(ipam_id) if ipam_id else None
        if ipam and hasattr(ipam, "resource_discovery_ids"):
            if match.ipam_resource_discovery_id in ipam.resource_discovery_ids:
                ipam.resource_discovery_ids.remove(match.ipam_resource_discovery_id)
        if ipam and hasattr(ipam, "resource_discovery_association_count"):
            ipam.resource_discovery_association_count = len(getattr(ipam, "resource_discovery_ids", []))

        match.ipam_id = ""
        match.ipam_arn = ""
        match.ipam_region = ""
        match.ipam_resource_discovery_association_arn = ""
        match.ipam_resource_discovery_association_id = ""
        match.resource_discovery_status = "disassociated"
        match.state = "disassociated"

        return {
            'ipamResourceDiscoveryAssociation': self._resource_discovery_association_to_dict(match),
            }

    def GetIpamDiscoveredAccounts(self, params: Dict[str, Any]):
        """Gets IPAM discovered accounts. A discovered account is an AWS account that is monitored under a resource discovery. If you have integrated IPAM with AWS Organizations, all accounts in the organization are discovered accounts. Only the IPAM account can get all discovered accounts in the organization."""

        error = self._require_params(params, ["DiscoveryRegion", "IpamResourceDiscoveryId"])
        if error:
            return error

        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        resource, error = self._get_resource_or_error(
            self.resources,
            ipam_resource_discovery_id,
            "InvalidIpamResourceDiscoveryId.NotFound",
        )
        if error:
            return error

        discovery_region = params.get("DiscoveryRegion")
        discovered_accounts = [
            account for account in resource.discovered_accounts
            if not discovery_region or account.get("discoveryRegion") == discovery_region
        ]
        discovered_accounts = apply_filters(discovered_accounts, params.get("Filter.N", []))
        pagination = self._paginate(
            discovered_accounts,
            int(params.get("MaxResults") or 100),
            params.get("NextToken"),
        )
        return {
            'ipamDiscoveredAccountSet': pagination["items"],
            'nextToken': pagination["next_token"],
            }

    def GetIpamDiscoveredPublicAddresses(self, params: Dict[str, Any]):
        """Gets the public IP addresses that have been discovered by IPAM."""

        error = self._require_params(params, ["AddressRegion", "IpamResourceDiscoveryId"])
        if error:
            return error

        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        resource, error = self._get_resource_or_error(
            self.resources,
            ipam_resource_discovery_id,
            "InvalidIpamResourceDiscoveryId.NotFound",
        )
        if error:
            return error

        address_region = params.get("AddressRegion")
        discovered_addresses = [
            address for address in resource.discovered_public_addresses
            if not address_region or address.get("addressRegion") == address_region
        ]
        discovered_addresses = apply_filters(discovered_addresses, params.get("Filter.N", []))
        oldest_sample_time = None
        for address in discovered_addresses:
            sample_time = address.get("sampleTime")
            if sample_time and (oldest_sample_time is None or sample_time < oldest_sample_time):
                oldest_sample_time = sample_time
        pagination = self._paginate(
            discovered_addresses,
            int(params.get("MaxResults") or 100),
            params.get("NextToken"),
        )
        return {
            'ipamDiscoveredPublicAddressSet': pagination["items"],
            'nextToken': pagination["next_token"],
            'oldestSampleTime': oldest_sample_time,
            }

    def GetIpamDiscoveredResourceCidrs(self, params: Dict[str, Any]):
        """Returns the resource CIDRs that are monitored as part of a resource discovery. A discovered resource is a resource CIDR monitored under a resource discovery. The following resources can be discovered: VPCs, Public IPv4 pools, VPC subnets, and Elastic IP addresses."""

        error = self._require_params(params, ["IpamResourceDiscoveryId", "ResourceRegion"])
        if error:
            return error

        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        resource, error = self._get_resource_or_error(
            self.resources,
            ipam_resource_discovery_id,
            "InvalidIpamResourceDiscoveryId.NotFound",
        )
        if error:
            return error

        resource_region = params.get("ResourceRegion")
        discovered_cidrs = [
            cidr for cidr in resource.discovered_resource_cidrs
            if not resource_region or cidr.get("resourceRegion") == resource_region
        ]
        discovered_cidrs = apply_filters(discovered_cidrs, params.get("Filter.N", []))
        pagination = self._paginate(
            discovered_cidrs,
            int(params.get("MaxResults") or 100),
            params.get("NextToken"),
        )
        return {
            'ipamDiscoveredResourceCidrSet': pagination["items"],
            'nextToken': pagination["next_token"],
            }

    def GetIpamResourceCidrs(self, params: Dict[str, Any]):
        """Returns resource CIDRs managed by IPAM in a given scope. If an IPAM is associated with more than one resource discovery, the resource CIDRs across all of the resource discoveries is returned. A resource discovery is an IPAM component that enables IPAM to manage and monitor resources that belong to t"""

        error = self._require_params(params, ["IpamScopeId"])
        if error:
            return error

        ipam_scope_id = params.get("IpamScopeId")
        scope = self.state.scopes.get(ipam_scope_id)
        if not scope:
            return create_error_response(
                "InvalidIpamScopeId.NotFound",
                f"The ID '{ipam_scope_id}' does not exist",
            )

        ipam_pool_id = params.get("IpamPoolId")
        resource_id = params.get("ResourceId")
        resource_owner = params.get("ResourceOwner")
        resource_type = params.get("ResourceType")
        resource_tag = params.get("ResourceTag") or {}
        tag_key = resource_tag.get("Key") or resource_tag.get("key")
        tag_value = resource_tag.get("Value") or resource_tag.get("value")

        resource_cidrs: List[Dict[str, Any]] = []
        for discovery in self.resources.values():
            for cidr in discovery.resource_cidrs:
                resource_cidrs.append(cidr)

        filtered_cidrs: List[Dict[str, Any]] = []
        for cidr in resource_cidrs:
            if ipam_scope_id and cidr.get("ipamScopeId") != ipam_scope_id:
                continue
            if ipam_pool_id and cidr.get("ipamPoolId") != ipam_pool_id:
                continue
            if resource_id and cidr.get("resourceId") != resource_id:
                continue
            if resource_owner and cidr.get("resourceOwnerId") != resource_owner:
                continue
            if resource_type and cidr.get("resourceType") != resource_type:
                continue
            if tag_key:
                tag_set = cidr.get("resourceTagSet") or []
                matched = False
                for tag in tag_set:
                    if tag.get("Key") == tag_key or tag.get("key") == tag_key:
                        if tag_value is None or tag.get("Value") == tag_value or tag.get("value") == tag_value:
                            matched = True
                            break
                if not matched:
                    continue
            filtered_cidrs.append(cidr)

        filtered_cidrs = apply_filters(filtered_cidrs, params.get("Filter.N", []))
        pagination = self._paginate(
            filtered_cidrs,
            int(params.get("MaxResults") or 100),
            params.get("NextToken"),
        )
        return {
            'ipamResourceCidrSet': pagination["items"],
            'nextToken': pagination["next_token"],
            }

    def ModifyIpamResourceCidr(self, params: Dict[str, Any]):
        """Modify a resource CIDR. You can use this action to transfer resource CIDRs between scopes and ignore resource CIDRs that you do not want to manage. If set to false, the resource will not be tracked for overlap, it cannot be auto-imported into a pool, and it will be removed from any pool it has an al"""

        error = self._require_params(
            params,
            [
                "CurrentIpamScopeId",
                "Monitored",
                "ResourceCidr",
                "ResourceId",
                "ResourceRegion",
            ],
        )
        if error:
            return error

        current_scope_id = params.get("CurrentIpamScopeId")
        if current_scope_id and not self.state.scopes.get(current_scope_id):
            return create_error_response(
                "InvalidIpamScopeId.NotFound",
                f"The ID '{current_scope_id}' does not exist",
            )

        resource_cidr = params.get("ResourceCidr")
        resource_id = params.get("ResourceId")
        resource_region = params.get("ResourceRegion")
        destination_scope_id = params.get("DestinationIpamScopeId")
        monitored = str2bool(params.get("Monitored"))

        target_cidr = None
        for discovery in self.resources.values():
            for cidr in discovery.resource_cidrs:
                if (
                    cidr.get("resourceCidr") == resource_cidr
                    and cidr.get("resourceId") == resource_id
                    and cidr.get("resourceRegion") == resource_region
                    and cidr.get("ipamScopeId") == current_scope_id
                ):
                    target_cidr = cidr
                    break
            if target_cidr:
                break

        if not target_cidr:
            return create_error_response(
                "InvalidIpamResourceCidr.NotFound",
                f"The ID '{resource_id}' does not exist",
            )

        if destination_scope_id:
            if not self.state.scopes.get(destination_scope_id):
                return create_error_response(
                    "InvalidIpamScopeId.NotFound",
                    f"The ID '{destination_scope_id}' does not exist",
                )
            target_cidr["ipamScopeId"] = destination_scope_id

        target_cidr["managementState"] = "managed" if monitored else "ignored"

        return {
            'ipamResourceCidr': {
                'availabilityZoneId': target_cidr.get("availabilityZoneId"),
                'complianceStatus': target_cidr.get("complianceStatus"),
                'ipamId': target_cidr.get("ipamId"),
                'ipamPoolId': target_cidr.get("ipamPoolId"),
                'ipamScopeId': target_cidr.get("ipamScopeId"),
                'ipUsage': target_cidr.get("ipUsage"),
                'managementState': target_cidr.get("managementState"),
                'overlapStatus': target_cidr.get("overlapStatus"),
                'resourceCidr': target_cidr.get("resourceCidr"),
                'resourceId': target_cidr.get("resourceId"),
                'resourceName': target_cidr.get("resourceName"),
                'resourceOwnerId': target_cidr.get("resourceOwnerId"),
                'resourceRegion': target_cidr.get("resourceRegion"),
                'resourceTagSet': target_cidr.get("resourceTagSet"),
                'resourceType': target_cidr.get("resourceType"),
                'vpcId': target_cidr.get("vpcId"),
                },
            }

    def ModifyIpamResourceDiscovery(self, params: Dict[str, Any]):
        """Modifies a resource discovery. A resource discovery is an IPAM component that enables IPAM to manage and monitor resources that belong to the owning account."""

        error = self._require_params(params, ["IpamResourceDiscoveryId"])
        if error:
            return error

        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        resource, error = self._get_resource_or_error(
            self.resources,
            ipam_resource_discovery_id,
            "InvalidIpamResourceDiscoveryId.NotFound",
        )
        if error:
            return error

        if params.get("Description") is not None:
            resource.description = params.get("Description") or ""

        add_regions = params.get("AddOperatingRegion.N", []) or []
        remove_regions = params.get("RemoveOperatingRegion.N", []) or []
        add_ous = params.get("AddOrganizationalUnitExclusion.N", []) or []
        remove_ous = params.get("RemoveOrganizationalUnitExclusion.N", []) or []

        existing_regions = {
            (region.get("regionName") or region.get("RegionName"))
            for region in resource.operating_region_set
            if isinstance(region, dict)
        }
        for region in add_regions:
            if isinstance(region, dict):
                region_name = region.get("RegionName") or region.get("regionName") or region.get("Region")
            else:
                region_name = region
            if region_name:
                existing_regions.add(region_name)
        for region in remove_regions:
            if isinstance(region, dict):
                region_name = region.get("RegionName") or region.get("regionName") or region.get("Region")
            else:
                region_name = region
            if region_name in existing_regions:
                existing_regions.remove(region_name)
        resource.operating_region_set = [{"regionName": name} for name in sorted(existing_regions)]

        existing_ous = {
            (ou.get("organizationsEntityPath") or ou.get("OrganizationsEntityPath"))
            for ou in resource.organizational_unit_exclusion_set
            if isinstance(ou, dict)
        }
        for ou in add_ous:
            if isinstance(ou, dict):
                ou_path = ou.get("OrganizationsEntityPath") or ou.get("organizationsEntityPath")
            else:
                ou_path = ou
            if ou_path:
                existing_ous.add(ou_path)
        for ou in remove_ous:
            if isinstance(ou, dict):
                ou_path = ou.get("OrganizationsEntityPath") or ou.get("organizationsEntityPath")
            else:
                ou_path = ou
            if ou_path in existing_ous:
                existing_ous.remove(ou_path)
        resource.organizational_unit_exclusion_set = [
            {"organizationsEntityPath": path} for path in sorted(existing_ous)
        ]

        return {
            'ipamResourceDiscovery': self._resource_discovery_to_dict(resource),
            }

    def _generate_id(self, prefix: str = 'ipam') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class resourcediscovery_RequestParser:
    @staticmethod
    def parse_associate_ipam_resource_discovery_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamId": get_scalar(md, "IpamId"),
            "IpamResourceDiscoveryId": get_scalar(md, "IpamResourceDiscoveryId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_ipam_resource_discovery_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "OperatingRegion.N": get_indexed_list(md, "OperatingRegion"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_ipam_resource_discovery_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamResourceDiscoveryId": get_scalar(md, "IpamResourceDiscoveryId"),
        }

    @staticmethod
    def parse_describe_ipam_resource_discoveries_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamResourceDiscoveryId.N": get_indexed_list(md, "IpamResourceDiscoveryId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_ipam_resource_discovery_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamResourceDiscoveryAssociationId.N": get_indexed_list(md, "IpamResourceDiscoveryAssociationId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disassociate_ipam_resource_discovery_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamResourceDiscoveryAssociationId": get_scalar(md, "IpamResourceDiscoveryAssociationId"),
        }

    @staticmethod
    def parse_get_ipam_discovered_accounts_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DiscoveryRegion": get_scalar(md, "DiscoveryRegion"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamResourceDiscoveryId": get_scalar(md, "IpamResourceDiscoveryId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_ipam_discovered_public_addresses_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddressRegion": get_scalar(md, "AddressRegion"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamResourceDiscoveryId": get_scalar(md, "IpamResourceDiscoveryId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_ipam_discovered_resource_cidrs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamResourceDiscoveryId": get_scalar(md, "IpamResourceDiscoveryId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ResourceRegion": get_scalar(md, "ResourceRegion"),
        }

    @staticmethod
    def parse_get_ipam_resource_cidrs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "IpamScopeId": get_scalar(md, "IpamScopeId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ResourceId": get_scalar(md, "ResourceId"),
            "ResourceOwner": get_scalar(md, "ResourceOwner"),
            "ResourceTag": get_scalar(md, "ResourceTag"),
            "ResourceType": get_scalar(md, "ResourceType"),
        }

    @staticmethod
    def parse_modify_ipam_resource_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CurrentIpamScopeId": get_scalar(md, "CurrentIpamScopeId"),
            "DestinationIpamScopeId": get_scalar(md, "DestinationIpamScopeId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Monitored": get_scalar(md, "Monitored"),
            "ResourceCidr": get_scalar(md, "ResourceCidr"),
            "ResourceId": get_scalar(md, "ResourceId"),
            "ResourceRegion": get_scalar(md, "ResourceRegion"),
        }

    @staticmethod
    def parse_modify_ipam_resource_discovery_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddOperatingRegion.N": get_indexed_list(md, "AddOperatingRegion"),
            "AddOrganizationalUnitExclusion.N": get_indexed_list(md, "AddOrganizationalUnitExclusion"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamResourceDiscoveryId": get_scalar(md, "IpamResourceDiscoveryId"),
            "RemoveOperatingRegion.N": get_indexed_list(md, "RemoveOperatingRegion"),
            "RemoveOrganizationalUnitExclusion.N": get_indexed_list(md, "RemoveOrganizationalUnitExclusion"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateIpamResourceDiscovery": resourcediscovery_RequestParser.parse_associate_ipam_resource_discovery_request,
            "CreateIpamResourceDiscovery": resourcediscovery_RequestParser.parse_create_ipam_resource_discovery_request,
            "DeleteIpamResourceDiscovery": resourcediscovery_RequestParser.parse_delete_ipam_resource_discovery_request,
            "DescribeIpamResourceDiscoveries": resourcediscovery_RequestParser.parse_describe_ipam_resource_discoveries_request,
            "DescribeIpamResourceDiscoveryAssociations": resourcediscovery_RequestParser.parse_describe_ipam_resource_discovery_associations_request,
            "DisassociateIpamResourceDiscovery": resourcediscovery_RequestParser.parse_disassociate_ipam_resource_discovery_request,
            "GetIpamDiscoveredAccounts": resourcediscovery_RequestParser.parse_get_ipam_discovered_accounts_request,
            "GetIpamDiscoveredPublicAddresses": resourcediscovery_RequestParser.parse_get_ipam_discovered_public_addresses_request,
            "GetIpamDiscoveredResourceCidrs": resourcediscovery_RequestParser.parse_get_ipam_discovered_resource_cidrs_request,
            "GetIpamResourceCidrs": resourcediscovery_RequestParser.parse_get_ipam_resource_cidrs_request,
            "ModifyIpamResourceCidr": resourcediscovery_RequestParser.parse_modify_ipam_resource_cidr_request,
            "ModifyIpamResourceDiscovery": resourcediscovery_RequestParser.parse_modify_ipam_resource_discovery_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class resourcediscovery_ResponseSerializer:
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
                xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_ipam_resource_discovery_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateIpamResourceDiscoveryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceDiscoveryAssociation
        _ipamResourceDiscoveryAssociation_key = None
        if "ipamResourceDiscoveryAssociation" in data:
            _ipamResourceDiscoveryAssociation_key = "ipamResourceDiscoveryAssociation"
        elif "IpamResourceDiscoveryAssociation" in data:
            _ipamResourceDiscoveryAssociation_key = "IpamResourceDiscoveryAssociation"
        if _ipamResourceDiscoveryAssociation_key:
            param_data = data[_ipamResourceDiscoveryAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamResourceDiscoveryAssociation>')
            xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamResourceDiscoveryAssociation>')
        xml_parts.append(f'</AssociateIpamResourceDiscoveryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_ipam_resource_discovery_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateIpamResourceDiscoveryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceDiscovery
        _ipamResourceDiscovery_key = None
        if "ipamResourceDiscovery" in data:
            _ipamResourceDiscovery_key = "ipamResourceDiscovery"
        elif "IpamResourceDiscovery" in data:
            _ipamResourceDiscovery_key = "IpamResourceDiscovery"
        if _ipamResourceDiscovery_key:
            param_data = data[_ipamResourceDiscovery_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamResourceDiscovery>')
            xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamResourceDiscovery>')
        xml_parts.append(f'</CreateIpamResourceDiscoveryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_ipam_resource_discovery_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteIpamResourceDiscoveryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceDiscovery
        _ipamResourceDiscovery_key = None
        if "ipamResourceDiscovery" in data:
            _ipamResourceDiscovery_key = "ipamResourceDiscovery"
        elif "IpamResourceDiscovery" in data:
            _ipamResourceDiscovery_key = "IpamResourceDiscovery"
        if _ipamResourceDiscovery_key:
            param_data = data[_ipamResourceDiscovery_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamResourceDiscovery>')
            xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamResourceDiscovery>')
        xml_parts.append(f'</DeleteIpamResourceDiscoveryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipam_resource_discoveries_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpamResourceDiscoveriesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceDiscoverySet
        _ipamResourceDiscoverySet_key = None
        if "ipamResourceDiscoverySet" in data:
            _ipamResourceDiscoverySet_key = "ipamResourceDiscoverySet"
        elif "IpamResourceDiscoverySet" in data:
            _ipamResourceDiscoverySet_key = "IpamResourceDiscoverySet"
        elif "IpamResourceDiscoverys" in data:
            _ipamResourceDiscoverySet_key = "IpamResourceDiscoverys"
        if _ipamResourceDiscoverySet_key:
            param_data = data[_ipamResourceDiscoverySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamResourceDiscoverySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamResourceDiscoverySet>')
            else:
                xml_parts.append(f'{indent_str}<ipamResourceDiscoverySet/>')
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
        xml_parts.append(f'</DescribeIpamResourceDiscoveriesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipam_resource_discovery_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpamResourceDiscoveryAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceDiscoveryAssociationSet
        _ipamResourceDiscoveryAssociationSet_key = None
        if "ipamResourceDiscoveryAssociationSet" in data:
            _ipamResourceDiscoveryAssociationSet_key = "ipamResourceDiscoveryAssociationSet"
        elif "IpamResourceDiscoveryAssociationSet" in data:
            _ipamResourceDiscoveryAssociationSet_key = "IpamResourceDiscoveryAssociationSet"
        elif "IpamResourceDiscoveryAssociations" in data:
            _ipamResourceDiscoveryAssociationSet_key = "IpamResourceDiscoveryAssociations"
        if _ipamResourceDiscoveryAssociationSet_key:
            param_data = data[_ipamResourceDiscoveryAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamResourceDiscoveryAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamResourceDiscoveryAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamResourceDiscoveryAssociationSet/>')
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
        xml_parts.append(f'</DescribeIpamResourceDiscoveryAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_ipam_resource_discovery_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateIpamResourceDiscoveryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceDiscoveryAssociation
        _ipamResourceDiscoveryAssociation_key = None
        if "ipamResourceDiscoveryAssociation" in data:
            _ipamResourceDiscoveryAssociation_key = "ipamResourceDiscoveryAssociation"
        elif "IpamResourceDiscoveryAssociation" in data:
            _ipamResourceDiscoveryAssociation_key = "IpamResourceDiscoveryAssociation"
        if _ipamResourceDiscoveryAssociation_key:
            param_data = data[_ipamResourceDiscoveryAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamResourceDiscoveryAssociation>')
            xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamResourceDiscoveryAssociation>')
        xml_parts.append(f'</DisassociateIpamResourceDiscoveryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ipam_discovered_accounts_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetIpamDiscoveredAccountsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamDiscoveredAccountSet
        _ipamDiscoveredAccountSet_key = None
        if "ipamDiscoveredAccountSet" in data:
            _ipamDiscoveredAccountSet_key = "ipamDiscoveredAccountSet"
        elif "IpamDiscoveredAccountSet" in data:
            _ipamDiscoveredAccountSet_key = "IpamDiscoveredAccountSet"
        elif "IpamDiscoveredAccounts" in data:
            _ipamDiscoveredAccountSet_key = "IpamDiscoveredAccounts"
        if _ipamDiscoveredAccountSet_key:
            param_data = data[_ipamDiscoveredAccountSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamDiscoveredAccountSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamDiscoveredAccountSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamDiscoveredAccountSet/>')
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
        xml_parts.append(f'</GetIpamDiscoveredAccountsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ipam_discovered_public_addresses_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetIpamDiscoveredPublicAddressesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamDiscoveredPublicAddressSet
        _ipamDiscoveredPublicAddressSet_key = None
        if "ipamDiscoveredPublicAddressSet" in data:
            _ipamDiscoveredPublicAddressSet_key = "ipamDiscoveredPublicAddressSet"
        elif "IpamDiscoveredPublicAddressSet" in data:
            _ipamDiscoveredPublicAddressSet_key = "IpamDiscoveredPublicAddressSet"
        elif "IpamDiscoveredPublicAddresss" in data:
            _ipamDiscoveredPublicAddressSet_key = "IpamDiscoveredPublicAddresss"
        if _ipamDiscoveredPublicAddressSet_key:
            param_data = data[_ipamDiscoveredPublicAddressSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamDiscoveredPublicAddressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamDiscoveredPublicAddressSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamDiscoveredPublicAddressSet/>')
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
        # Serialize oldestSampleTime
        _oldestSampleTime_key = None
        if "oldestSampleTime" in data:
            _oldestSampleTime_key = "oldestSampleTime"
        elif "OldestSampleTime" in data:
            _oldestSampleTime_key = "OldestSampleTime"
        if _oldestSampleTime_key:
            param_data = data[_oldestSampleTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<oldestSampleTime>{esc(str(param_data))}</oldestSampleTime>')
        xml_parts.append(f'</GetIpamDiscoveredPublicAddressesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ipam_discovered_resource_cidrs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetIpamDiscoveredResourceCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamDiscoveredResourceCidrSet
        _ipamDiscoveredResourceCidrSet_key = None
        if "ipamDiscoveredResourceCidrSet" in data:
            _ipamDiscoveredResourceCidrSet_key = "ipamDiscoveredResourceCidrSet"
        elif "IpamDiscoveredResourceCidrSet" in data:
            _ipamDiscoveredResourceCidrSet_key = "IpamDiscoveredResourceCidrSet"
        elif "IpamDiscoveredResourceCidrs" in data:
            _ipamDiscoveredResourceCidrSet_key = "IpamDiscoveredResourceCidrs"
        if _ipamDiscoveredResourceCidrSet_key:
            param_data = data[_ipamDiscoveredResourceCidrSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamDiscoveredResourceCidrSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamDiscoveredResourceCidrSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamDiscoveredResourceCidrSet/>')
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
        xml_parts.append(f'</GetIpamDiscoveredResourceCidrsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ipam_resource_cidrs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetIpamResourceCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceCidrSet
        _ipamResourceCidrSet_key = None
        if "ipamResourceCidrSet" in data:
            _ipamResourceCidrSet_key = "ipamResourceCidrSet"
        elif "IpamResourceCidrSet" in data:
            _ipamResourceCidrSet_key = "IpamResourceCidrSet"
        elif "IpamResourceCidrs" in data:
            _ipamResourceCidrSet_key = "IpamResourceCidrs"
        if _ipamResourceCidrSet_key:
            param_data = data[_ipamResourceCidrSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamResourceCidrSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamResourceCidrSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamResourceCidrSet/>')
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
        xml_parts.append(f'</GetIpamResourceCidrsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_ipam_resource_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyIpamResourceCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceCidr
        _ipamResourceCidr_key = None
        if "ipamResourceCidr" in data:
            _ipamResourceCidr_key = "ipamResourceCidr"
        elif "IpamResourceCidr" in data:
            _ipamResourceCidr_key = "IpamResourceCidr"
        if _ipamResourceCidr_key:
            param_data = data[_ipamResourceCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamResourceCidr>')
            xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamResourceCidr>')
        xml_parts.append(f'</ModifyIpamResourceCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_ipam_resource_discovery_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyIpamResourceDiscoveryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamResourceDiscovery
        _ipamResourceDiscovery_key = None
        if "ipamResourceDiscovery" in data:
            _ipamResourceDiscovery_key = "ipamResourceDiscovery"
        elif "IpamResourceDiscovery" in data:
            _ipamResourceDiscovery_key = "IpamResourceDiscovery"
        if _ipamResourceDiscovery_key:
            param_data = data[_ipamResourceDiscovery_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamResourceDiscovery>')
            xml_parts.extend(resourcediscovery_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamResourceDiscovery>')
        xml_parts.append(f'</ModifyIpamResourceDiscoveryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateIpamResourceDiscovery": resourcediscovery_ResponseSerializer.serialize_associate_ipam_resource_discovery_response,
            "CreateIpamResourceDiscovery": resourcediscovery_ResponseSerializer.serialize_create_ipam_resource_discovery_response,
            "DeleteIpamResourceDiscovery": resourcediscovery_ResponseSerializer.serialize_delete_ipam_resource_discovery_response,
            "DescribeIpamResourceDiscoveries": resourcediscovery_ResponseSerializer.serialize_describe_ipam_resource_discoveries_response,
            "DescribeIpamResourceDiscoveryAssociations": resourcediscovery_ResponseSerializer.serialize_describe_ipam_resource_discovery_associations_response,
            "DisassociateIpamResourceDiscovery": resourcediscovery_ResponseSerializer.serialize_disassociate_ipam_resource_discovery_response,
            "GetIpamDiscoveredAccounts": resourcediscovery_ResponseSerializer.serialize_get_ipam_discovered_accounts_response,
            "GetIpamDiscoveredPublicAddresses": resourcediscovery_ResponseSerializer.serialize_get_ipam_discovered_public_addresses_response,
            "GetIpamDiscoveredResourceCidrs": resourcediscovery_ResponseSerializer.serialize_get_ipam_discovered_resource_cidrs_response,
            "GetIpamResourceCidrs": resourcediscovery_ResponseSerializer.serialize_get_ipam_resource_cidrs_response,
            "ModifyIpamResourceCidr": resourcediscovery_ResponseSerializer.serialize_modify_ipam_resource_cidr_response,
            "ModifyIpamResourceDiscovery": resourcediscovery_ResponseSerializer.serialize_modify_ipam_resource_discovery_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

