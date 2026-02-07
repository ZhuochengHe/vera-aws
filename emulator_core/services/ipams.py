from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class IpamState(str, Enum):
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


class ResourceComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NONCOMPLIANT = "noncompliant"
    UNMANAGED = "unmanaged"
    IGNORED = "ignored"


class ResourceOverlapStatus(str, Enum):
    OVERLAPPING = "overlapping"
    NONOVERLAPPING = "nonoverlapping"
    IGNORED = "ignored"


class ResourceType(str, Enum):
    EIP = "eip"
    VPC = "vpc"
    SUBNET = "subnet"
    NETWORK_INTERFACE = "network-interface"
    INSTANCE = "instance"


class AdvertisementType(str, Enum):
    UNICAST = "unicast"
    ANYCAST = "anycast"


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


class MeteredAccountType(str, Enum):
    IPAM_OWNER = "ipam-owner"
    RESOURCE_OWNER = "resource-owner"


class IpamTier(str, Enum):
    FREE = "free"
    ADVANCED = "advanced"


@dataclass
class Tag:
    Key: Optional[str] = None
    Value: Optional[str] = None

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
class AddIpamOperatingRegion:
    RegionName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RegionName": self.RegionName,
        }


@dataclass
class RemoveIpamOperatingRegion:
    RegionName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RegionName": self.RegionName,
        }


@dataclass
class IpamOperatingRegion:
    regionName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RegionName": self.regionName,
        }


@dataclass
class Ipam:
    defaultResourceDiscoveryAssociationId: Optional[str] = None
    defaultResourceDiscoveryId: Optional[str] = None
    description: Optional[str] = None
    enablePrivateGua: Optional[bool] = None
    ipamArn: Optional[str] = None
    ipamId: Optional[str] = None
    ipamRegion: Optional[str] = None
    meteredAccount: Optional[MeteredAccountType] = None
    operatingRegionSet: List[IpamOperatingRegion] = field(default_factory=list)
    ownerId: Optional[str] = None
    privateDefaultScopeId: Optional[str] = None
    publicDefaultScopeId: Optional[str] = None
    resourceDiscoveryAssociationCount: Optional[int] = None
    scopeCount: Optional[int] = None
    state: Optional[IpamState] = None
    stateMessage: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    tier: Optional[IpamTier] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DefaultResourceDiscoveryAssociationId": self.defaultResourceDiscoveryAssociationId,
            "DefaultResourceDiscoveryId": self.defaultResourceDiscoveryId,
            "Description": self.description,
            "EnablePrivateGua": self.enablePrivateGua,
            "IpamArn": self.ipamArn,
            "IpamId": self.ipamId,
            "IpamRegion": self.ipamRegion,
            "MeteredAccount": self.meteredAccount.value if self.meteredAccount else None,
            "OperatingRegionSet": [region.to_dict() for region in self.operatingRegionSet],
            "OwnerId": self.ownerId,
            "PrivateDefaultScopeId": self.privateDefaultScopeId,
            "PublicDefaultScopeId": self.publicDefaultScopeId,
            "ResourceDiscoveryAssociationCount": self.resourceDiscoveryAssociationCount,
            "ScopeCount": self.scopeCount,
            "State": self.state.value if self.state else None,
            "StateMessage": self.stateMessage,
            "TagSet": [tag.to_dict() for tag in self.tagSet],
            "Tier": self.tier.value if self.tier else None,
        }


@dataclass
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Values": self.Values,
        }


@dataclass
class IpamAddressHistoryRecord:
    resourceCidr: Optional[str] = None
    resourceComplianceStatus: Optional[ResourceComplianceStatus] = None
    resourceId: Optional[str] = None
    resourceName: Optional[str] = None
    resourceOverlapStatus: Optional[ResourceOverlapStatus] = None
    resourceOwnerId: Optional[str] = None
    resourceRegion: Optional[str] = None
    resourceType: Optional[ResourceType] = None
    sampledEndTime: Optional[datetime] = None
    sampledStartTime: Optional[datetime] = None
    vpcId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceCidr": self.resourceCidr,
            "ResourceComplianceStatus": self.resourceComplianceStatus.value if self.resourceComplianceStatus else None,
            "ResourceId": self.resourceId,
            "ResourceName": self.resourceName,
            "ResourceOverlapStatus": self.resourceOverlapStatus.value if self.resourceOverlapStatus else None,
            "ResourceOwnerId": self.resourceOwnerId,
            "ResourceRegion": self.resourceRegion,
            "ResourceType": self.resourceType.value if self.resourceType else None,
            "SampledEndTime": self.sampledEndTime.isoformat() if self.sampledEndTime else None,
            "SampledStartTime": self.sampledStartTime.isoformat() if self.sampledStartTime else None,
            "VpcId": self.vpcId,
        }


@dataclass
class AsnAssociation:
    asn: Optional[str] = None
    cidr: Optional[str] = None
    state: Optional[str] = None  # Could be Enum but not specified explicitly
    statusMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Asn": self.asn,
            "Cidr": self.cidr,
            "State": self.state,
            "StatusMessage": self.statusMessage,
        }


@dataclass
class ByoipCidr:
    advertisementType: Optional[AdvertisementType] = None
    asnAssociationSet: List[AsnAssociation] = field(default_factory=list)
    cidr: Optional[str] = None
    description: Optional[str] = None
    networkBorderGroup: Optional[str] = None
    state: Optional[ByoipCidrState] = None
    statusMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AdvertisementType": self.advertisementType.value if self.advertisementType else None,
            "AsnAssociationSet": [asn.to_dict() for asn in self.asnAssociationSet],
            "Cidr": self.cidr,
            "Description": self.description,
            "NetworkBorderGroup": self.networkBorderGroup,
            "State": self.state.value if self.state else None,
            "StatusMessage": self.statusMessage,
        }


class IPAMsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.ipams

    def create_ipam(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun parameter (not implemented here, just placeholder)
        dry_run = params.get("DryRun")
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        description = params.get("Description")
        enable_private_gua = params.get("EnablePrivateGua", False)
        metered_account_str = params.get("MeteredAccount")
        operating_regions_params = params.get("OperatingRegion.N", [])
        tag_specifications_params = params.get("TagSpecification.N", [])
        tier_str = params.get("Tier")

        # Validate metered_account
        metered_account = None
        if metered_account_str:
            if metered_account_str not in ("ipam-owner", "resource-owner"):
                raise ValueError(f"Invalid MeteredAccount value: {metered_account_str}")
            metered_account = MeteredAccountType(metered_account_str)

        # Validate tier
        tier = None
        if tier_str:
            if tier_str not in ("free", "advanced"):
                raise ValueError(f"Invalid Tier value: {tier_str}")
            tier = IpamTier(tier_str)

        # Parse operating regions
        operating_region_set = []
        for region_param in operating_regions_params:
            region_name = region_param.get("RegionName")
            operating_region_set.append(IpamOperatingRegion(regionName=region_name))

        # Parse tags from tag specifications
        tag_set = []
        for tag_spec in tag_specifications_params:
            tags = tag_spec.get("Tags", [])
            for tag_dict in tags:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                tag_set.append(Tag(Key=key, Value=value))

        # Generate unique IPAM ID and ARN
        ipam_id = self.generate_unique_id()
        ipam_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:ipam/{ipam_id}"

        # Create Ipam object with default values for counts and scopes
        ipam = Ipam(
            defaultResourceDiscoveryAssociationId=None,
            defaultResourceDiscoveryId=None,
            description=description,
            enablePrivateGua=enable_private_gua,
            ipamArn=ipam_arn,
            ipamId=ipam_id,
            ipamRegion=self.state.region,
            meteredAccount=metered_account,
            operatingRegionSet=operating_region_set,
            ownerId=self.get_owner_id(),
            privateDefaultScopeId=None,
            publicDefaultScopeId=None,
            resourceDiscoveryAssociationCount=0,
            scopeCount=0,
            state=IpamState.create_complete,
            stateMessage=None,
            tagSet=tag_set,
            tier=tier,
        )

        # Store the Ipam object in state
        self.state.ipams[ipam_id] = ipam

        return {
            "ipam": ipam.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_ipam(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        ipam_id = params.get("IpamId")
        if not ipam_id:
            raise ValueError("IpamId is required")

        cascade = params.get("Cascade", False)

        ipam = self.state.ipams.get(ipam_id)
        if not ipam:
            # In real implementation, raise an error for not found
            raise ValueError(f"IPAM with id {ipam_id} not found")

        # If cascade is True, simulate deletion of related resources (not implemented here)
        # For now, just remove the IPAM from state
        del self.state.ipams[ipam_id]

        # Return the deleted IPAM info with state set to delete-complete
        deleted_ipam = Ipam(
            defaultResourceDiscoveryAssociationId=ipam.defaultResourceDiscoveryAssociationId,
            defaultResourceDiscoveryId=ipam.defaultResourceDiscoveryId,
            description=ipam.description,
            enablePrivateGua=ipam.enablePrivateGua,
            ipamArn=ipam.ipamArn,
            ipamId=ipam.ipamId,
            ipamRegion=ipam.ipamRegion,
            meteredAccount=ipam.meteredAccount,
            operatingRegionSet=ipam.operatingRegionSet,
            ownerId=ipam.ownerId,
            privateDefaultScopeId=ipam.privateDefaultScopeId,
            publicDefaultScopeId=ipam.publicDefaultScopeId,
            resourceDiscoveryAssociationCount=ipam.resourceDiscoveryAssociationCount,
            scopeCount=ipam.scopeCount,
            state=IpamState.delete_complete,
            stateMessage=None,
            tagSet=ipam.tagSet,
            tier=ipam.tier,
        )

        return {
            "ipam": deleted_ipam.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def describe_ipams(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        filters_params = params.get("Filter.N", [])
        ipam_ids = params.get("IpamId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect all IPAMs
        ipams_list = list(self.state.ipams.values())

        # Filter by IPAM IDs if provided
        if ipam_ids:
            ipams_list = [ipam for ipam in ipams_list if ipam.ipamId in ipam_ids]

        # Apply filters
        def matches_filter(ipam: Ipam, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if not name or not values:
                return True
            # Support filtering by tag keys and values
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in ipam.tagSet:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False
            # Support filtering by state
            if name == "state":
                return ipam.state and ipam.state.value in values
            # Support filtering by ipam-id
            if name == "ipam-id":
                return ipam.ipamId in values
            # Support filtering by description
            if name == "description":
                return ipam.description in values if ipam.description else False
            # Support filtering by owner-id
            if name == "owner-id":
                return ipam.ownerId in values if ipam.ownerId else False
            # Add more filters as needed
            return True

        for filter_param in filters_params:
            filter_obj = Filter(
                Name=filter_param.get("Name"),
                Values=filter_param.get("Values", []),
            )
            ipams_list = [ipam for ipam in ipams_list if matches_filter(ipam, filter_obj)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except ValueError:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        end_index = start_index + max_results
        paged_ipams = ipams_list[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(ipams_list) else None

        return {
            "ipamSet": [ipam.to_dict() for ipam in paged_ipams],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def disable_ipam_organization_admin_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        delegated_admin_account_id = params.get("DelegatedAdminAccountId")
        if not delegated_admin_account_id:
            raise ValueError("DelegatedAdminAccountId is required")

        # Simulate disabling the IPAM organization admin account
        # For this emulator, just return success True
        success = True

        return {
            "requestId": self.generate_request_id(),
            "success": success,
        }


    def enable_ipam_organization_admin_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        delegated_admin_account_id = params.get("DelegatedAdminAccountId")
        if not delegated_admin_account_id:
            raise ValueError("DelegatedAdminAccountId is required")

        # Simulate enabling the IPAM organization admin account
        # For this emulator, just return success True
        success = True

        return {
            "requestId": self.generate_request_id(),
            "success": success,
        }

    def get_ipam_address_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        cidr = params.get("Cidr")
        ipam_scope_id = params.get("IpamScopeId")
        dry_run = params.get("DryRun", False)
        end_time = params.get("EndTime")
        start_time = params.get("StartTime")
        max_results = params.get("MaxResults", 100)
        next_token = params.get("NextToken")
        vpc_id = params.get("VpcId")

        # Validate required parameters
        if cidr is None:
            raise ValueError("Missing required parameter: Cidr")
        if ipam_scope_id is None:
            raise ValueError("Missing required parameter: IpamScopeId")

        # Validate max_results range
        if max_results is not None:
            if not (1 <= max_results <= 1000):
                raise ValueError("MaxResults must be between 1 and 1000")

        # DryRun check (simulate permission check)
        if dry_run:
            # For simplicity, assume permission granted
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Validate IPAM scope exists
        ipam_scope = self.state.resources.get(ipam_scope_id)
        if ipam_scope is None:
            # Return empty result if scope not found
            return {
                "historyRecordSet": [],
                "nextToken": None,
                "requestId": self.generate_request_id(),
            }

        # Default end_time to current time if not provided
        if end_time is None:
            end_time = datetime.datetime.utcnow()
        elif isinstance(end_time, str):
            end_time = datetime.datetime.fromisoformat(end_time)

        # Default start_time to end_time if not provided
        if start_time is None:
            start_time = end_time
        elif isinstance(start_time, str):
            start_time = datetime.datetime.fromisoformat(start_time)

        # Collect all IpamAddressHistoryRecord objects for the given cidr and scope
        # For this emulation, assume self.state.ipam_address_history_records is a dict keyed by ipam_scope_id
        # Each value is a list of IpamAddressHistoryRecord objects
        all_records = self.state.ipam_address_history_records.get(ipam_scope_id, [])

        # Filter records by cidr exact match (no subnets)
        filtered_records = [r for r in all_records if r.resourceCidr == cidr]

        # Filter by VpcId if provided
        if vpc_id:
            filtered_records = [r for r in filtered_records if r.vpcId == vpc_id]

        # Filter by time range: sampledStartTime and sampledEndTime must overlap with [start_time, end_time]
        def overlaps(record):
            if record.sampledStartTime is None or record.sampledEndTime is None:
                return False
            return not (record.sampledEndTime < start_time or record.sampledStartTime > end_time)

        filtered_records = [r for r in filtered_records if overlaps(r)]

        # Pagination logic
        # Use next_token as an index offset (string of int)
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page_records = filtered_records[start_index:end_index]

        # Prepare next token if more records exist
        new_next_token = None
        if end_index < len(filtered_records):
            new_next_token = str(end_index)

        # Convert records to dicts
        history_record_set = [r.to_dict() for r in page_records]

        return {
            "historyRecordSet": history_record_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def modify_ipam(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ipam_id = params.get("IpamId")
        dry_run = params.get("DryRun", False)
        description = params.get("Description")
        enable_private_gua = params.get("EnablePrivateGua")
        metered_account = params.get("MeteredAccount")
        tier = params.get("Tier")
        add_operating_regions = params.get("AddOperatingRegion.N", [])
        remove_operating_regions = params.get("RemoveOperatingRegion.N", [])

        # Validate required parameter
        if ipam_id is None:
            raise ValueError("Missing required parameter: IpamId")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Retrieve IPAM object
        ipam = self.state.ipams.get(ipam_id)
        if ipam is None:
            raise ValueError(f"IPAM with id {ipam_id} not found")

        # Update description if provided
        if description is not None:
            ipam.description = description

        # Update enablePrivateGua if provided
        if enable_private_gua is not None:
            ipam.enablePrivateGua = bool(enable_private_gua)

        # Update meteredAccount if provided and valid
        if metered_account is not None:
            valid_metered_accounts = {m.value for m in MeteredAccountType}
            if metered_account not in valid_metered_accounts:
                raise ValueError(f"Invalid MeteredAccount value: {metered_account}")
            ipam.meteredAccount = MeteredAccountType(metered_account)

        # Update tier if provided and valid
        if tier is not None:
            valid_tiers = {t.value for t in IpamTier}
            if tier not in valid_tiers:
                raise ValueError(f"Invalid Tier value: {tier}")
            ipam.tier = IpamTier(tier)

        # Add operating regions
        for region_dict in add_operating_regions:
            region_name = region_dict.get("RegionName")
            if region_name:
                # Check if region already exists
                exists = any(r.regionName == region_name for r in ipam.operatingRegionSet)
                if not exists:
                    ipam.operatingRegionSet.append(IpamOperatingRegion(regionName=region_name))

        # Remove operating regions
        for region_dict in remove_operating_regions:
            region_name = region_dict.get("RegionName")
            if region_name:
                ipam.operatingRegionSet = [r for r in ipam.operatingRegionSet if r.regionName != region_name]

        # Update state to modify-in-progress then modify-complete (simulate)
        ipam.state = IpamState.MODIFY_IN_PROGRESS
        # Simulate modification done immediately
        ipam.state = IpamState.MODIFY_COMPLETE

        return {
            "ipam": ipam.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def move_byoip_cidr_to_ipam(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cidr = params.get("Cidr")
        ipam_pool_id = params.get("IpamPoolId")
        ipam_pool_owner = params.get("IpamPoolOwner")
        dry_run = params.get("DryRun", False)

        # Validate required parameters
        if cidr is None:
            raise ValueError("Missing required parameter: Cidr")
        if ipam_pool_id is None:
            raise ValueError("Missing required parameter: IpamPoolId")
        if ipam_pool_owner is None:
            raise ValueError("Missing required parameter: IpamPoolOwner")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Validate that the CIDR is IPv4 (cannot move IPv6)
        import ipaddress
        try:
            network = ipaddress.ip_network(cidr)
        except Exception:
            raise ValueError(f"Invalid CIDR format: {cidr}")

        if network.version != 4:
            raise ValueError("Only IPv4 CIDRs can be moved to IPAM")

        # Validate that the ipam_pool_id exists in state
        ipam_pool = self.state.resources.get(ipam_pool_id)
        if ipam_pool is None:
            raise ValueError(f"IPAM pool with id {ipam_pool_id} not found")

        # Validate that the ipam_pool_owner matches owner id or is valid (for simplicity, accept any string)
        # In real AWS, this would be validated against account info

        # Find the BYOIP CIDR in state by cidr string
        byoip_cidr = None
        for cidr_obj in self.state.byoip_cidrs.values():
            if cidr_obj.cidr == cidr:
                byoip_cidr = cidr_obj
                break

        if byoip_cidr is None:
            raise ValueError(f"BYOIP CIDR {cidr} not found")

        # Move the BYOIP CIDR to IPAM pool
        # For emulation, set some attributes to reflect move
        byoip_cidr.state = ByoipCidrState.PROVISIONED
        byoip_cidr.statusMessage = f"Moved to IPAM pool {ipam_pool_id} owned by {ipam_pool_owner}"

        # Possibly associate the cidr with the ipam pool id (not specified in detail)
        # For emulation, add attribute ipamPoolId if not present
        setattr(byoip_cidr, "ipamPoolId", ipam_pool_id)
        setattr(byoip_cidr, "ipamPoolOwner", ipam_pool_owner)

        return {
            "byoipCidr": byoip_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class IPAMsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateIpam", self.create_ipam)
        self.register_action("DeleteIpam", self.delete_ipam)
        self.register_action("DescribeIpams", self.describe_ipams)
        self.register_action("DisableIpamOrganizationAdminAccount", self.disable_ipam_organization_admin_account)
        self.register_action("EnableIpamOrganizationAdminAccount", self.enable_ipam_organization_admin_account)
        self.register_action("GetIpamAddressHistory", self.get_ipam_address_history)
        self.register_action("ModifyIpam", self.modify_ipam)
        self.register_action("MoveByoipCidrToIpam", self.move_byoip_cidr_to_ipam)

    def create_ipam(self, params):
        return self.backend.create_ipam(params)

    def delete_ipam(self, params):
        return self.backend.delete_ipam(params)

    def describe_ipams(self, params):
        return self.backend.describe_ipams(params)

    def disable_ipam_organization_admin_account(self, params):
        return self.backend.disable_ipam_organization_admin_account(params)

    def enable_ipam_organization_admin_account(self, params):
        return self.backend.enable_ipam_organization_admin_account(params)

    def get_ipam_address_history(self, params):
        return self.backend.get_ipam_address_history(params)

    def modify_ipam(self, params):
        return self.backend.modify_ipam(params)

    def move_byoip_cidr_to_ipam(self, params):
        return self.backend.move_byoip_cidr_to_ipam(params)
