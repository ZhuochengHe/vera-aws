from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


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
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"Name": self.Name, "Values": self.Values}


@dataclass
class AddIpamOperatingRegion:
    RegionName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"RegionName": self.RegionName}


@dataclass
class RemoveIpamOperatingRegion:
    RegionName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"RegionName": self.RegionName}


@dataclass
class AddIpamOrganizationalUnitExclusion:
    OrganizationsEntityPath: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"OrganizationsEntityPath": self.OrganizationsEntityPath}


@dataclass
class RemoveIpamOrganizationalUnitExclusion:
    OrganizationsEntityPath: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"OrganizationsEntityPath": self.OrganizationsEntityPath}


@dataclass
class IpamOperatingRegion:
    regionName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"RegionName": self.regionName}


@dataclass
class IpamOrganizationalUnitExclusion:
    organizationsEntityPath: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"OrganizationsEntityPath": self.organizationsEntityPath}


class ResourceDiscoveryStatus(str, Enum):
    ACTIVE = "active"
    NOT_FOUND = "not-found"


class IpamResourceDiscoveryAssociationState(str, Enum):
    ASSOCIATE_IN_PROGRESS = "associate-in-progress"
    ASSOCIATE_COMPLETE = "associate-complete"
    ASSOCIATE_FAILED = "associate-failed"
    DISASSOCIATE_IN_PROGRESS = "disassociate-in-progress"
    DISASSOCIATE_COMPLETE = "disassociate-complete"
    DISASSOCIATE_FAILED = "disassociate-failed"
    ISOLATE_IN_PROGRESS = "isolate-in-progress"
    ISOLATE_COMPLETE = "isolate-complete"
    RESTORE_IN_PROGRESS = "restore-in-progress"


class IpamResourceDiscoveryState(str, Enum):
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


@dataclass
class IpamResourceDiscoveryAssociation:
    ipamArn: Optional[str] = None
    ipamId: Optional[str] = None
    ipamRegion: Optional[str] = None
    ipamResourceDiscoveryAssociationArn: Optional[str] = None
    ipamResourceDiscoveryAssociationId: Optional[str] = None
    ipamResourceDiscoveryId: Optional[str] = None
    isDefault: Optional[bool] = None
    ownerId: Optional[str] = None
    resourceDiscoveryStatus: Optional[ResourceDiscoveryStatus] = None
    state: Optional[IpamResourceDiscoveryAssociationState] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "IpamArn": self.ipamArn,
            "IpamId": self.ipamId,
            "IpamRegion": self.ipamRegion,
            "IpamResourceDiscoveryAssociationArn": self.ipamResourceDiscoveryAssociationArn,
            "IpamResourceDiscoveryAssociationId": self.ipamResourceDiscoveryAssociationId,
            "IpamResourceDiscoveryId": self.ipamResourceDiscoveryId,
            "IsDefault": self.isDefault,
            "OwnerId": self.ownerId,
            "ResourceDiscoveryStatus": self.resourceDiscoveryStatus.value if self.resourceDiscoveryStatus else None,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tagSet],
        }


@dataclass
class IpamResourceDiscovery:
    description: Optional[str] = None
    ipamResourceDiscoveryArn: Optional[str] = None
    ipamResourceDiscoveryId: Optional[str] = None
    ipamResourceDiscoveryRegion: Optional[str] = None
    isDefault: Optional[bool] = None
    operatingRegionSet: List[IpamOperatingRegion] = field(default_factory=list)
    organizationalUnitExclusionSet: List[IpamOrganizationalUnitExclusion] = field(default_factory=list)
    ownerId: Optional[str] = None
    state: Optional[IpamResourceDiscoveryState] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Description": self.description,
            "IpamResourceDiscoveryArn": self.ipamResourceDiscoveryArn,
            "IpamResourceDiscoveryId": self.ipamResourceDiscoveryId,
            "IpamResourceDiscoveryRegion": self.ipamResourceDiscoveryRegion,
            "IsDefault": self.isDefault,
            "OperatingRegionSet": [region.to_dict() for region in self.operatingRegionSet],
            "OrganizationalUnitExclusionSet": [ou.to_dict() for ou in self.organizationalUnitExclusionSet],
            "OwnerId": self.ownerId,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tagSet],
        }


class IpamDiscoveryFailureCode(str, Enum):
    ASSUME_ROLE_FAILURE = "assume-role-failure"
    THROTTLING_FAILURE = "throttling-failure"
    UNAUTHORIZED_FAILURE = "unauthorized-failure"


@dataclass
class IpamDiscoveryFailureReason:
    code: Optional[IpamDiscoveryFailureCode] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Code": self.code.value if self.code else None,
            "Message": self.message,
        }


@dataclass
class IpamDiscoveredAccount:
    accountId: Optional[str] = None
    discoveryRegion: Optional[str] = None
    failureReason: Optional[IpamDiscoveryFailureReason] = None
    lastAttemptedDiscoveryTime: Optional[datetime] = None
    lastSuccessfulDiscoveryTime: Optional[datetime] = None
    organizationalUnitId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AccountId": self.accountId,
            "DiscoveryRegion": self.discoveryRegion,
            "FailureReason": self.failureReason.to_dict() if self.failureReason else None,
            "LastAttemptedDiscoveryTime": self.lastAttemptedDiscoveryTime.isoformat() if self.lastAttemptedDiscoveryTime else None,
            "LastSuccessfulDiscoveryTime": self.lastSuccessfulDiscoveryTime.isoformat() if self.lastSuccessfulDiscoveryTime else None,
            "OrganizationalUnitId": self.organizationalUnitId,
        }


class IpamPublicAddressType(str, Enum):
    SERVICE_MANAGED_IP = "service-managed-ip"
    SERVICE_MANAGED_BYOIP = "service-managed-byoip"
    AMAZON_OWNED_EIP = "amazon-owned-eip"
    AMAZON_OWNED_CONTIG = "amazon-owned-contig"
    BYOIP = "byoip"
    EC2_PUBLIC_IP = "ec2-public-ip"
    ANYCAST_IP_LIST_IP = "anycast-ip-list-ip"


class IpamPublicAddressAssociationStatus(str, Enum):
    ASSOCIATED = "associated"
    DISASSOCIATED = "disassociated"


class IpamPublicAddressService(str, Enum):
    NAT_GATEWAY = "nat-gateway"
    DATABASE_MIGRATION_SERVICE = "database-migration-service"
    REDSHIFT = "redshift"
    ELASTIC_CONTAINER_SERVICE = "elastic-container-service"
    RELATIONAL_DATABASE_SERVICE = "relational-database-service"
    SITE_TO_SITE_VPN = "site-to-site-vpn"
    LOAD_BALANCER = "load-balancer"
    GLOBAL_ACCELERATOR = "global-accelerator"
    CLOUDFRONT = "cloudfront"
    OTHER = "other"


@dataclass
class IpamPublicAddressTag:
    key: Optional[str] = None
    value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class IpamPublicAddressTags:
    eipTagSet: List[IpamPublicAddressTag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"EipTagSet": [tag.to_dict() for tag in self.eipTagSet]}


@dataclass
class IpamPublicAddressSecurityGroup:
    groupId: Optional[str] = None
    groupName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"GroupId": self.groupId, "GroupName": self.groupName}


@dataclass
class IpamDiscoveredPublicAddress:
    address: Optional[str] = None
    addressAllocationId: Optional[str] = None
    addressOwnerId: Optional[str] = None
    addressRegion: Optional[str] = None
    addressType: Optional[IpamPublicAddressType] = None
    associationStatus: Optional[IpamPublicAddressAssociationStatus] = None
    instanceId: Optional[str] = None
    ipamResourceDiscoveryId: Optional[str] = None
    networkBorderGroup: Optional[str] = None
    networkInterfaceDescription: Optional[str] = None
    networkInterfaceId: Optional[str] = None
    publicIpv4PoolId: Optional[str] = None
    sampleTime: Optional[datetime] = None
    securityGroupSet: List[IpamPublicAddressSecurityGroup] = field(default_factory=list)
    service: Optional[IpamPublicAddressService] = None
    serviceResource: Optional[str] = None
    subnetId: Optional[str] = None
    tags: Optional[IpamPublicAddressTags] = None
    vpcId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Address": self.address,
            "AddressAllocationId": self.addressAllocationId,
            "AddressOwnerId": self.addressOwnerId,
            "AddressRegion": self.addressRegion,
            "AddressType": self.addressType.value if self.addressType else None,
            "AssociationStatus": self.associationStatus.value if self.associationStatus else None,
            "InstanceId": self.instanceId,
            "IpamResourceDiscoveryId": self.ipamResourceDiscoveryId,
            "NetworkBorderGroup": self.networkBorderGroup,
            "NetworkInterfaceDescription": self.networkInterfaceDescription,
            "NetworkInterfaceId": self.networkInterfaceId,
            "PublicIpv4PoolId": self.publicIpv4PoolId,
            "SampleTime": self.sampleTime.isoformat() if self.sampleTime else None,
            "SecurityGroupSet": [sg.to_dict() for sg in self.securityGroupSet],
            "Service": self.service.value if self.service else None,
            "ServiceResource": self.serviceResource,
            "SubnetId": self.subnetId,
            "Tags": self.tags.to_dict() if self.tags else None,
            "VpcId": self.vpcId,
        }


class IpamResourceCidrComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NONCOMPLIANT = "noncompliant"
    UNMANAGED = "unmanaged"
    IGNORED = "ignored"


class IpamResourceCidrManagementState(str, Enum):
    MANAGED = "managed"
    UNMANAGED = "unmanaged"
    IGNORED = "ignored"


class IpamResourceCidrOverlapStatus(str, Enum):
    OVERLAPPING = "overlapping"
    NONOVERLAPPING = "nonoverlapping"
    IGNORED = "ignored"


class IpamResourceType(str, Enum):
    VPC = "vpc"
    SUBNET = "subnet"
    EIP = "eip"
    PUBLIC_IPV4_POOL = "public-ipv4-pool"
    IPV6_POOL = "ipv6-pool"
    ENI = "eni"
    ANYCAST_IP_LIST = "anycast-ip-list"


class NetworkInterfaceAttachmentStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in-use"


@dataclass
class IpamResourceTag:
    key: Optional[str] = None
    value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class IpamDiscoveredResourceCidr:
    availabilityZoneId: Optional[str] = None
    ipamResourceDiscoveryId: Optional[str] = None
    ipSource: Optional[str] = None  # amazon | byoip | none
    ipUsage: Optional[float] = None
    networkInterfaceAttachmentStatus: Optional[NetworkInterfaceAttachmentStatus] = None
    resourceCidr: Optional[str] = None
    resourceId: Optional[str] = None
    resourceOwnerId: Optional[str] = None
    resourceRegion: Optional[str] = None
    resourceTagSet: List[IpamResourceTag] = field(default_factory=list)
    resourceType: Optional[IpamResourceType] = None
    sampleTime: Optional[datetime] = None
    subnetId: Optional[str] = None
    vpcId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZoneId": self.availabilityZoneId,
            "IpamResourceDiscoveryId": self.ipamResourceDiscoveryId,
            "IpSource": self.ipSource,
            "IpUsage": self.ipUsage,
            "NetworkInterfaceAttachmentStatus": self.networkInterfaceAttachmentStatus.value if self.networkInterfaceAttachmentStatus else None,
            "ResourceCidr": self.resourceCidr,
            "ResourceId": self.resourceId,
            "ResourceOwnerId": self.resourceOwnerId,
            "ResourceRegion": self.resourceRegion,
            "ResourceTagSet": [tag.to_dict() for tag in self.resourceTagSet],
            "ResourceType": self.resourceType.value if self.resourceType else None,
            "SampleTime": self.sampleTime.isoformat() if self.sampleTime else None,
            "SubnetId": self.subnetId,
            "VpcId": self.vpcId,
        }


@dataclass
class IpamResourceCidr:
    availabilityZoneId: Optional[str] = None
    complianceStatus: Optional[IpamResourceCidrComplianceStatus] = None
    ipamId: Optional[str] = None
    ipamPoolId: Optional[str] = None
    ipamScopeId: Optional[str] = None
    ipUsage: Optional[float] = None
    managementState: Optional[IpamResourceCidrManagementState] = None
    overlapStatus: Optional[IpamResourceCidrOverlapStatus] = None
    resourceCidr: Optional[str] = None
    resourceId: Optional[str] = None
    resourceName: Optional[str] = None
    resourceOwnerId: Optional[str] = None
    resourceRegion: Optional[str] = None
    resourceTagSet: List[IpamResourceTag] = field(default_factory=list)
    resourceType: Optional[IpamResourceType] = None
    vpcId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZoneId": self.availabilityZoneId,
            "ComplianceStatus": self.complianceStatus.value if self.complianceStatus else None,
            "IpamId": self.ipamId,
            "IpamPoolId": self.ipamPoolId,
            "IpamScopeId": self.ipamScopeId,
            "IpUsage": self.ipUsage,
            "ManagementState": self.managementState.value if self.managementState else None,
            "OverlapStatus": self.overlapStatus.value if self.overlapStatus else None,
            "ResourceCidr": self.resourceCidr,
            "ResourceId": self.resourceId,
            "ResourceName": self.resourceName,
            "ResourceOwnerId": self.resourceOwnerId,
            "ResourceRegion": self.resourceRegion,
            "ResourceTagSet": [tag.to_dict() for tag in self.resourceTagSet],
            "ResourceType": self.resourceType.value if self.resourceType else None,
            "VpcId": self.vpcId,
        }


@dataclass
class RequestIpamResourceTag:
    Key: Optional[str] = None
    Value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


class ResourceDiscoveryBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for shared resources

    def associate_ipam_resource_discovery(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ipam_id = params.get("IpamId")
        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        tag_specifications = params.get("TagSpecification.N", [])

        if not ipam_id:
            raise ValueError("IpamId is required")
        if not ipam_resource_discovery_id:
            raise ValueError("IpamResourceDiscoveryId is required")

        # Validate existence of IPAM resource discovery
        ipam_resource_discovery = self.state.resource_discoveries.get(ipam_resource_discovery_id)
        if not ipam_resource_discovery:
            raise ValueError(f"IPAM Resource Discovery {ipam_resource_discovery_id} does not exist")

        # Create a new association ID and ARN
        association_id = self.generate_unique_id(prefix="ipam-rd-assoc-")
        association_arn = f"arn:aws:ec2:{ipam_resource_discovery.ipamResourceDiscoveryRegion}:{self.get_owner_id()}:ipam-resource-discovery-association/{association_id}"

        # Compose tags from tag specifications
        tags = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Create the association object
        association = IpamResourceDiscoveryAssociation(
            ipamArn=f"arn:aws:ec2:{ipam_resource_discovery.ipamResourceDiscoveryRegion}:{self.get_owner_id()}:ipam/{ipam_id}",
            ipamId=ipam_id,
            ipamRegion=ipam_resource_discovery.ipamResourceDiscoveryRegion,
            ipamResourceDiscoveryAssociationArn=association_arn,
            ipamResourceDiscoveryAssociationId=association_id,
            ipamResourceDiscoveryId=ipam_resource_discovery_id,
            isDefault=False,
            ownerId=self.get_owner_id(),
            resourceDiscoveryStatus=ResourceDiscoveryStatus.ACTIVE if hasattr(ResourceDiscoveryStatus, "ACTIVE") else "active",
            state=IpamResourceDiscoveryAssociationState.ASSOCIATE_COMPLETE if hasattr(IpamResourceDiscoveryAssociationState, "ASSOCIATE_COMPLETE") else "associate-complete",
            tagSet=tags,
        )

        # Store the association in state
        self.state.resource_discoveries[association_id] = association

        return {
            "ipamResourceDiscoveryAssociation": association.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_ipam_resource_discovery(self, params: Dict[str, Any]) -> Dict[str, Any]:
        description = params.get("Description")
        operating_regions_params = params.get("OperatingRegion.N", [])
        tag_specifications = params.get("TagSpecification.N", [])

        # Generate IDs and ARNs
        resource_discovery_id = self.generate_unique_id(prefix="ipam-rd-")
        region = "us-east-1"  # Default region or could be derived from context
        resource_discovery_arn = f"arn:aws:ec2:{region}:{self.get_owner_id()}:ipam-resource-discovery/{resource_discovery_id}"

        # Parse operating regions
        operating_regions = []
        for op_region in operating_regions_params:
            region_name = op_region.get("RegionName")
            if region_name:
                operating_regions.append(IpamOperatingRegion(regionName=region_name))

        # Compose tags from tag specifications
        tags = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Create the resource discovery object
        resource_discovery = IpamResourceDiscovery(
            description=description,
            ipamResourceDiscoveryArn=resource_discovery_arn,
            ipamResourceDiscoveryId=resource_discovery_id,
            ipamResourceDiscoveryRegion=region,
            isDefault=False,
            operatingRegionSet=operating_regions,
            organizationalUnitExclusionSet=[],
            ownerId=self.get_owner_id(),
            state=IpamResourceDiscoveryState.CREATE_COMPLETE if hasattr(IpamResourceDiscoveryState, "CREATE_COMPLETE") else "create-complete",
            tagSet=tags,
        )

        # Store in state
        self.state.resource_discoveries[resource_discovery_id] = resource_discovery

        return {
            "ipamResourceDiscovery": resource_discovery.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_ipam_resource_discovery(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        if not ipam_resource_discovery_id:
            raise ValueError("IpamResourceDiscoveryId is required")

        resource_discovery = self.state.resource_discoveries.get(ipam_resource_discovery_id)
        if not resource_discovery:
            raise ValueError(f"IPAM Resource Discovery {ipam_resource_discovery_id} does not exist")

        # Mark the resource discovery as deleted
        resource_discovery.state = IpamResourceDiscoveryState.DELETE_COMPLETE if hasattr(IpamResourceDiscoveryState, "DELETE_COMPLETE") else "delete-complete"

        # Remove from state
        del self.state.resource_discoveries[ipam_resource_discovery_id]

        return {
            "ipamResourceDiscovery": resource_discovery.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def describe_ipam_resource_discoveries(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = params.get("Filter.N", [])
        resource_discovery_ids = params.get("IpamResourceDiscoveryId.N", [])
        max_results = params.get("MaxResults", 1000)
        next_token = params.get("NextToken")

        # Validate max_results range
        if max_results is not None:
            if not (5 <= max_results <= 1000):
                raise ValueError("MaxResults must be between 5 and 1000")

        # Filter resource discoveries by IDs if provided
        discoveries = list(self.state.resource_discoveries.values())
        if resource_discovery_ids:
            discoveries = [d for d in discoveries if d.ipamResourceDiscoveryId in resource_discovery_ids]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            filtered = []
            for d in discoveries:
                attr_value = getattr(d, name, None)
                if attr_value is None:
                    # Try lower case attribute name
                    attr_value = getattr(d, name[0].lower() + name[1:], None)
                if attr_value is None:
                    continue
                # If attribute is list, check if any value matches
                if isinstance(attr_value, list):
                    # For list of objects, check if any object's attribute matches any value
                    matched = False
                    for item in attr_value:
                        if hasattr(item, "to_dict"):
                            item_dict = item.to_dict()
                            if any(str(item_dict.get(name)) in values for name in values):
                                matched = True
                                break
                    if matched:
                        filtered.append(d)
                else:
                    if str(attr_value) in values:
                        filtered.append(d)
            discoveries = filtered

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page = discoveries[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(discoveries) else None

        return {
            "ipamResourceDiscoverySet": [d.to_dict() for d in page],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_ipam_resource_discovery_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = params.get("Filter.N", [])
        association_ids = params.get("IpamResourceDiscoveryAssociationId.N", [])
        max_results = params.get("MaxResults", 1000)
        next_token = params.get("NextToken")

        # Validate max_results range
        if max_results is not None:
            if not (5 <= max_results <= 1000):
                raise ValueError("MaxResults must be between 5 and 1000")

        # Filter associations by IDs if provided
        associations = [v for k, v in self.state.resource_discoveries.items() if isinstance(v, IpamResourceDiscoveryAssociation)]
        if association_ids:
            associations = [a for a in associations if a.ipamResourceDiscoveryAssociationId in association_ids]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            filtered = []
            for a in associations:
                attr_value = getattr(a, name, None)
                if attr_value is None:
                    # Try lower case attribute name
                    attr_value = getattr(a, name[0].lower() + name[1:], None)
                if attr_value is None:
                    continue
                # If attribute is list, check if any value matches
                if isinstance(attr_value, list):
                    # For list of objects, check if any object's attribute matches any value
                    matched = False
                    for item in attr_value:
                        if hasattr(item, "to_dict"):
                            item_dict = item.to_dict()
                            if any(str(item_dict.get(name)) in values for name in values):
                                matched = True
                                break
                    if matched:
                        filtered.append(a)
                else:
                    if str(attr_value) in values:
                        filtered.append(a)
            associations = filtered

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page = associations[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(associations) else None

        return {
            "ipamResourceDiscoveryAssociationSet": [a.to_dict() for a in page],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def disassociate_ipam_resource_discovery(self, params: dict) -> dict:
        ipam_resource_discovery_association_id = params.get("IpamResourceDiscoveryAssociationId")
        if not ipam_resource_discovery_association_id:
            raise ValueError("IpamResourceDiscoveryAssociationId is required")

        association = self.state.resource_discoveries.get(ipam_resource_discovery_association_id)
        if not association:
            # Return empty or raise error? AWS returns empty with no error if not found
            # But better to raise error for invalid id
            raise ValueError(f"Resource discovery association {ipam_resource_discovery_association_id} not found")

        # Update state to disassociate in progress
        association.state = IpamResourceDiscoveryAssociationState.DISASSOCIATE_IN_PROGRESS

        # Simulate disassociation process (immediate for emulator)
        association.state = IpamResourceDiscoveryAssociationState.DISASSOCIATE_COMPLETE

        # Remove association from state
        del self.state.resource_discoveries[ipam_resource_discovery_association_id]

        return {
            "ipamResourceDiscoveryAssociation": association.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def get_ipam_discovered_accounts(self, params: dict) -> dict:
        discovery_region = params.get("DiscoveryRegion")
        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        if not discovery_region:
            raise ValueError("DiscoveryRegion is required")
        if not ipam_resource_discovery_id:
            raise ValueError("IpamResourceDiscoveryId is required")

        max_results = params.get("MaxResults", 1000)
        if max_results < 5 or max_results > 1000:
            raise ValueError("MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        filters = params.get("Filter.N", [])

        # Get all discovered accounts for the given resource discovery and region
        all_accounts = []
        for account in self.state.ipam_discovered_accounts.values():
            if account.ipamResourceDiscoveryId != ipam_resource_discovery_id:
                continue
            if account.discoveryRegion != discovery_region:
                continue

            # Apply filters if any
            if filters:
                matched = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not name or not values:
                        continue
                    attr_val = getattr(account, name, None)
                    if attr_val is None or str(attr_val) not in values:
                        matched = False
                        break
                if not matched:
                    continue

            all_accounts.append(account)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page_accounts = all_accounts[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(all_accounts) else None

        return {
            "ipamDiscoveredAccountSet": [acc.to_dict() for acc in page_accounts],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def get_ipam_discovered_public_addresses(self, params: dict) -> dict:
        address_region = params.get("AddressRegion")
        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        if not address_region:
            raise ValueError("AddressRegion is required")
        if not ipam_resource_discovery_id:
            raise ValueError("IpamResourceDiscoveryId is required")

        max_results = params.get("MaxResults", 1000)
        if max_results < 5 or max_results > 1000:
            raise ValueError("MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        filters = params.get("Filter.N", [])

        all_addresses = []
        for addr in self.state.ipam_discovered_public_addresses.values():
            if addr.ipamResourceDiscoveryId != ipam_resource_discovery_id:
                continue
            if addr.addressRegion != address_region:
                continue

            # Apply filters if any
            if filters:
                matched = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not name or not values:
                        continue
                    attr_val = getattr(addr, name, None)
                    if attr_val is None or str(attr_val) not in values:
                        matched = False
                        break
                if not matched:
                    continue

            all_addresses.append(addr)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page_addresses = all_addresses[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(all_addresses) else None

        oldest_sample_time = None
        if page_addresses:
            oldest_sample_time = min(addr.sampleTime for addr in page_addresses if addr.sampleTime)

        return {
            "ipamDiscoveredPublicAddressSet": [addr.to_dict() for addr in page_addresses],
            "nextToken": new_next_token,
            "oldestSampleTime": oldest_sample_time,
            "requestId": self.generate_request_id(),
        }


    def get_ipam_discovered_resource_cidrs(self, params: dict) -> dict:
        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")
        resource_region = params.get("ResourceRegion")
        if not ipam_resource_discovery_id:
            raise ValueError("IpamResourceDiscoveryId is required")
        if not resource_region:
            raise ValueError("ResourceRegion is required")

        max_results = params.get("MaxResults", 1000)
        if max_results < 5 or max_results > 1000:
            raise ValueError("MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        filters = params.get("Filter.N", [])

        all_cidrs = []
        for cidr in self.state.ipam_discovered_resource_cidrs.values():
            if cidr.ipamResourceDiscoveryId != ipam_resource_discovery_id:
                continue
            if cidr.resourceRegion != resource_region:
                continue

            # Apply filters if any
            if filters:
                matched = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not name or not values:
                        continue
                    attr_val = getattr(cidr, name, None)
                    if attr_val is None or str(attr_val) not in values:
                        matched = False
                        break
                if not matched:
                    continue

            all_cidrs.append(cidr)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page_cidrs = all_cidrs[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(all_cidrs) else None

        return {
            "ipamDiscoveredResourceCidrSet": [cidr.to_dict() for cidr in page_cidrs],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def get_ipam_resource_cidrs(self, params: dict) -> dict:
        ipam_scope_id = params.get("IpamScopeId")
        if not ipam_scope_id:
            raise ValueError("IpamScopeId is required")

        max_results = params.get("MaxResults", 1000)
        if max_results < 5 or max_results > 1000:
            raise ValueError("MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        filters = params.get("Filter.N", [])
        ipam_pool_id = params.get("IpamPoolId")
        resource_id = params.get("ResourceId")
        resource_owner = params.get("ResourceOwner")
        resource_tag = params.get("ResourceTag")
        resource_type = params.get("ResourceType")

        all_cidrs = []
        for cidr in self.state.ipam_resource_cidrs.values():
            if cidr.ipamScopeId != ipam_scope_id:
                continue
            if ipam_pool_id and cidr.ipamPoolId != ipam_pool_id:
                continue
            if resource_id and cidr.resourceId != resource_id:
                continue
            if resource_owner and cidr.resourceOwnerId != resource_owner:
                continue
            if resource_type and cidr.resourceType != resource_type:
                continue

            # Filter by resource tag if provided
            if resource_tag:
                key = resource_tag.get("Key")
                value = resource_tag.get("Value")
                if key:
                    tag_match = False
                    for tag in cidr.resourceTagSet:
                        if tag.key == key and (value is None or tag.value == value):
                            tag_match = True
                            break
                    if not tag_match:
                        continue

            # Apply filters if any
            if filters:
                matched = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not name or not values:
                        continue
                    attr_val = getattr(cidr, name, None)
                    if attr_val is None or str(attr_val) not in values:
                        matched = False
                        break
                if not matched:
                    continue

            all_cidrs.append(cidr)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page_cidrs = all_cidrs[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(all_cidrs) else None

        return {
            "ipamResourceCidrSet": [cidr.to_dict() for cidr in page_cidrs],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def modify_ipam_resource_cidr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        current_scope_id = params.get("CurrentIpamScopeId")
        destination_scope_id = params.get("DestinationIpamScopeId")
        dry_run = params.get("DryRun", False)
        monitored = params.get("Monitored")
        resource_cidr = params.get("ResourceCidr")
        resource_id = params.get("ResourceId")
        resource_region = params.get("ResourceRegion")

        if current_scope_id is None:
            raise ValueError("CurrentIpamScopeId is required")
        if monitored is None:
            raise ValueError("Monitored is required")
        if resource_cidr is None:
            raise ValueError("ResourceCidr is required")
        if resource_id is None:
            raise ValueError("ResourceId is required")
        if resource_region is None:
            raise ValueError("ResourceRegion is required")

        if dry_run:
            # For dry run, we simulate permission check
            # Here we assume permission is granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Find the IpamResourceCidr in state matching current_scope_id, resource_cidr, resource_id, resource_region
        found_resource_cidr = None
        for ipam_resource_cidr in self.state.resource_cidrs.values():
            if (
                ipam_resource_cidr.ipamScopeId == current_scope_id and
                ipam_resource_cidr.resourceCidr == resource_cidr and
                ipam_resource_cidr.resourceId == resource_id and
                ipam_resource_cidr.resourceRegion == resource_region
            ):
                found_resource_cidr = ipam_resource_cidr
                break

        if not found_resource_cidr:
            # Resource CIDR not found
            raise ValueError("The specified resource CIDR was not found in the current scope")

        # Modify the resource CIDR according to parameters
        # Transfer scope if destination_scope_id is provided
        if destination_scope_id is not None:
            found_resource_cidr.ipamScopeId = destination_scope_id

        # Set monitored state: if monitored is False, resource is unmanaged/ignored
        # We interpret monitored True as managed, False as ignored
        if monitored:
            # Set managementState to managed
            found_resource_cidr.managementState = "managed"
        else:
            # Set managementState to ignored
            found_resource_cidr.managementState = "ignored"

        # Save back to state (already modified in place)

        response = {
            "ipamResourceCidr": found_resource_cidr.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def modify_ipam_resource_discovery(self, params: Dict[str, Any]) -> Dict[str, Any]:
        add_operating_regions = []
        remove_operating_regions = []
        add_ou_exclusions = []
        remove_ou_exclusions = []

        # Parse AddOperatingRegion.N
        for key, value in params.items():
            if key.startswith("AddOperatingRegion."):
                add_operating_regions.append(AddIpamOperatingRegion(RegionName=value.get("RegionName")))

        # Parse RemoveOperatingRegion.N
        for key, value in params.items():
            if key.startswith("RemoveOperatingRegion."):
                remove_operating_regions.append(RemoveIpamOperatingRegion(RegionName=value.get("RegionName")))

        # Parse AddOrganizationalUnitExclusion.N
        for key, value in params.items():
            if key.startswith("AddOrganizationalUnitExclusion."):
                add_ou_exclusions.append(AddIpamOrganizationalUnitExclusion(OrganizationsEntityPath=value.get("OrganizationsEntityPath")))

        # Parse RemoveOrganizationalUnitExclusion.N
        for key, value in params.items():
            if key.startswith("RemoveOrganizationalUnitExclusion."):
                remove_ou_exclusions.append(RemoveIpamOrganizationalUnitExclusion(OrganizationsEntityPath=value.get("OrganizationsEntityPath")))

        description = params.get("Description")
        dry_run = params.get("DryRun", False)
        ipam_resource_discovery_id = params.get("IpamResourceDiscoveryId")

        if ipam_resource_discovery_id is None:
            raise ValueError("IpamResourceDiscoveryId is required")

        if dry_run:
            # Simulate permission check
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Find the resource discovery by id
        resource_discovery = self.state.resource_discoveries.get(ipam_resource_discovery_id)
        if not resource_discovery:
            raise ValueError(f"Resource discovery with id {ipam_resource_discovery_id} not found")

        # Modify description if provided
        if description is not None:
            resource_discovery.description = description

        # Add operating regions
        for add_region in add_operating_regions:
            if add_region.RegionName:
                # Check if already present
                if not any(r.regionName == add_region.RegionName for r in resource_discovery.operatingRegionSet):
                    resource_discovery.operatingRegionSet.append(IpamOperatingRegion(regionName=add_region.RegionName))

        # Remove operating regions
        for remove_region in remove_operating_regions:
            if remove_region.RegionName:
                resource_discovery.operatingRegionSet = [
                    r for r in resource_discovery.operatingRegionSet if r.regionName != remove_region.RegionName
                ]

        # Add organizational unit exclusions
        for add_ou in add_ou_exclusions:
            if add_ou.OrganizationsEntityPath:
                if not any(ou.organizationsEntityPath == add_ou.OrganizationsEntityPath for ou in resource_discovery.organizationalUnitExclusionSet):
                    resource_discovery.organizationalUnitExclusionSet.append(
                        IpamOrganizationalUnitExclusion(organizationsEntityPath=add_ou.OrganizationsEntityPath)
                    )

        # Remove organizational unit exclusions
        for remove_ou in remove_ou_exclusions:
            if remove_ou.OrganizationsEntityPath:
                resource_discovery.organizationalUnitExclusionSet = [
                    ou for ou in resource_discovery.organizationalUnitExclusionSet if ou.organizationsEntityPath != remove_ou.OrganizationsEntityPath
                ]

        # Save back to state (already modified in place)

        response = {
            "ipamResourceDiscovery": resource_discovery.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class ResourcediscoveriesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateIpamResourceDiscovery", self.associate_ipam_resource_discovery)
        self.register_action("CreateIpamResourceDiscovery", self.create_ipam_resource_discovery)
        self.register_action("DeleteIpamResourceDiscovery", self.delete_ipam_resource_discovery)
        self.register_action("DescribeIpamResourceDiscoveries", self.describe_ipam_resource_discoveries)
        self.register_action("DescribeIpamResourceDiscoveryAssociations", self.describe_ipam_resource_discovery_associations)
        self.register_action("DisassociateIpamResourceDiscovery", self.disassociate_ipam_resource_discovery)
        self.register_action("GetIpamDiscoveredAccounts", self.get_ipam_discovered_accounts)
        self.register_action("GetIpamDiscoveredPublicAddresses", self.get_ipam_discovered_public_addresses)
        self.register_action("GetIpamDiscoveredResourceCidrs", self.get_ipam_discovered_resource_cidrs)
        self.register_action("GetIpamResourceCidrs", self.get_ipam_resource_cidrs)
        self.register_action("ModifyIpamResourceCidr", self.modify_ipam_resource_cidr)
        self.register_action("ModifyIpamResourceDiscovery", self.modify_ipam_resource_discovery)

    def associate_ipam_resource_discovery(self, params):
        return self.backend.associate_ipam_resource_discovery(params)

    def create_ipam_resource_discovery(self, params):
        return self.backend.create_ipam_resource_discovery(params)

    def delete_ipam_resource_discovery(self, params):
        return self.backend.delete_ipam_resource_discovery(params)

    def describe_ipam_resource_discoveries(self, params):
        return self.backend.describe_ipam_resource_discoveries(params)

    def describe_ipam_resource_discovery_associations(self, params):
        return self.backend.describe_ipam_resource_discovery_associations(params)

    def disassociate_ipam_resource_discovery(self, params):
        return self.backend.disassociate_ipam_resource_discovery(params)

    def get_ipam_discovered_accounts(self, params):
        return self.backend.get_ipam_discovered_accounts(params)

    def get_ipam_discovered_public_addresses(self, params):
        return self.backend.get_ipam_discovered_public_addresses(params)

    def get_ipam_discovered_resource_cidrs(self, params):
        return self.backend.get_ipam_discovered_resource_cidrs(params)

    def get_ipam_resource_cidrs(self, params):
        return self.backend.get_ipam_resource_cidrs(params)

    def modify_ipam_resource_cidr(self, params):
        return self.backend.modify_ipam_resource_cidr(params)

    def modify_ipam_resource_discovery(self, params):
        return self.backend.modify_ipam_resource_discovery(params)
