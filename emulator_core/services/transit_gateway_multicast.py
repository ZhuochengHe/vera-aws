from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class ResourceType(str, Enum):
    VPC = "vpc"
    VPN = "vpn"
    VPN_CONCENTRATOR = "vpn-concentrator"
    DIRECT_CONNECT_GATEWAY = "direct-connect-gateway"
    CONNECT = "connect"
    PEERING = "peering"
    TGW_PEERING = "tgw-peering"


class SubnetAssociationState(str, Enum):
    PENDING_ACCEPTANCE = "pendingAcceptance"
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"
    REJECTED = "rejected"
    FAILED = "failed"


class TransitGatewayMulticastDomainState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


class AutoAcceptSharedAssociations(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class Igmpv2Support(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class StaticSourcesSupport(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class MemberType(str, Enum):
    STATIC = "static"
    IGMP = "igmp"


class SourceType(str, Enum):
    STATIC = "static"
    IGMP = "igmp"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


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
class SubnetAssociation:
    state: Optional[SubnetAssociationState] = None
    subnetId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "State": self.state.value if self.state else None,
            "SubnetId": self.subnetId,
        }


@dataclass
class TransitGatewayMulticastDomainOptions:
    autoAcceptSharedAssociations: Optional[AutoAcceptSharedAssociations] = None
    igmpv2Support: Optional[Igmpv2Support] = None
    staticSourcesSupport: Optional[StaticSourcesSupport] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AutoAcceptSharedAssociations": self.autoAcceptSharedAssociations.value if self.autoAcceptSharedAssociations else None,
            "Igmpv2Support": self.igmpv2Support.value if self.igmpv2Support else None,
            "StaticSourcesSupport": self.staticSourcesSupport.value if self.staticSourcesSupport else None,
        }


@dataclass
class TransitGatewayMulticastDomain:
    creationTime: Optional[datetime] = None
    options: Optional[TransitGatewayMulticastDomainOptions] = None
    ownerId: Optional[str] = None
    state: Optional[TransitGatewayMulticastDomainState] = None
    tagSet: List[Tag] = field(default_factory=list)
    transitGatewayId: Optional[str] = None
    transitGatewayMulticastDomainArn: Optional[str] = None
    transitGatewayMulticastDomainId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CreationTime": self.creationTime.isoformat() if self.creationTime else None,
            "Options": self.options.to_dict() if self.options else None,
            "OwnerId": self.ownerId,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tagSet],
            "TransitGatewayId": self.transitGatewayId,
            "TransitGatewayMulticastDomainArn": self.transitGatewayMulticastDomainArn,
            "TransitGatewayMulticastDomainId": self.transitGatewayMulticastDomainId,
        }


@dataclass
class TransitGatewayMulticastDomainAssociations:
    resourceId: Optional[str] = None
    resourceOwnerId: Optional[str] = None
    resourceType: Optional[ResourceType] = None
    subnets: List[SubnetAssociation] = field(default_factory=list)
    transitGatewayAttachmentId: Optional[str] = None
    transitGatewayMulticastDomainId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resourceId,
            "ResourceOwnerId": self.resourceOwnerId,
            "ResourceType": self.resourceType.value if self.resourceType else None,
            "Subnets": [subnet.to_dict() for subnet in self.subnets],
            "TransitGatewayAttachmentId": self.transitGatewayAttachmentId,
            "TransitGatewayMulticastDomainId": self.transitGatewayMulticastDomainId,
        }


@dataclass
class TransitGatewayMulticastDomainAssociation:
    resourceId: Optional[str] = None
    resourceOwnerId: Optional[str] = None
    resourceType: Optional[ResourceType] = None
    subnet: Optional[SubnetAssociation] = None
    transitGatewayAttachmentId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resourceId,
            "ResourceOwnerId": self.resourceOwnerId,
            "ResourceType": self.resourceType.value if self.resourceType else None,
            "Subnet": self.subnet.to_dict() if self.subnet else None,
            "TransitGatewayAttachmentId": self.transitGatewayAttachmentId,
        }


@dataclass
class TransitGatewayMulticastDeregisteredGroupMembers:
    deregisteredNetworkInterfaceIds: List[str] = field(default_factory=list)
    groupIpAddress: Optional[str] = None
    transitGatewayMulticastDomainId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DeregisteredNetworkInterfaceIds": self.deregisteredNetworkInterfaceIds,
            "GroupIpAddress": self.groupIpAddress,
            "TransitGatewayMulticastDomainId": self.transitGatewayMulticastDomainId,
        }


@dataclass
class TransitGatewayMulticastDeregisteredGroupSources:
    deregisteredNetworkInterfaceIds: List[str] = field(default_factory=list)
    groupIpAddress: Optional[str] = None
    transitGatewayMulticastDomainId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DeregisteredNetworkInterfaceIds": self.deregisteredNetworkInterfaceIds,
            "GroupIpAddress": self.groupIpAddress,
            "TransitGatewayMulticastDomainId": self.transitGatewayMulticastDomainId,
        }


@dataclass
class TransitGatewayMulticastRegisteredGroupMembers:
    groupIpAddress: Optional[str] = None
    registeredNetworkInterfaceIds: List[str] = field(default_factory=list)
    transitGatewayMulticastDomainId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "GroupIpAddress": self.groupIpAddress,
            "RegisteredNetworkInterfaceIds": self.registeredNetworkInterfaceIds,
            "TransitGatewayMulticastDomainId": self.transitGatewayMulticastDomainId,
        }


@dataclass
class TransitGatewayMulticastRegisteredGroupSources:
    groupIpAddress: Optional[str] = None
    registeredNetworkInterfaceIds: List[str] = field(default_factory=list)
    transitGatewayMulticastDomainId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "GroupIpAddress": self.groupIpAddress,
            "RegisteredNetworkInterfaceIds": self.registeredNetworkInterfaceIds,
            "TransitGatewayMulticastDomainId": self.transitGatewayMulticastDomainId,
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
class TransitGatewayMulticastGroup:
    groupIpAddress: Optional[str] = None
    groupMember: Optional[bool] = None
    groupSource: Optional[bool] = None
    memberType: Optional[MemberType] = None
    networkInterfaceId: Optional[str] = None
    resourceId: Optional[str] = None
    resourceOwnerId: Optional[str] = None
    resourceType: Optional[ResourceType] = None
    sourceType: Optional[SourceType] = None
    subnetId: Optional[str] = None
    transitGatewayAttachmentId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "GroupIpAddress": self.groupIpAddress,
            "GroupMember": self.groupMember,
            "GroupSource": self.groupSource,
            "MemberType": self.memberType.value if self.memberType else None,
            "NetworkInterfaceId": self.networkInterfaceId,
            "ResourceId": self.resourceId,
            "ResourceOwnerId": self.resourceOwnerId,
            "ResourceType": self.resourceType.value if self.resourceType else None,
            "SourceType": self.sourceType.value if self.sourceType else None,
            "SubnetId": self.subnetId,
            "TransitGatewayAttachmentId": self.transitGatewayAttachmentId,
        }


@dataclass
class CreateTransitGatewayMulticastDomainRequestOptions:
    AutoAcceptSharedAssociations: Optional[AutoAcceptSharedAssociations] = None
    Igmpv2Support: Optional[Igmpv2Support] = None
    StaticSourcesSupport: Optional[StaticSourcesSupport] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AutoAcceptSharedAssociations": self.AutoAcceptSharedAssociations.value if self.AutoAcceptSharedAssociations else None,
            "Igmpv2Support": self.Igmpv2Support.value if self.Igmpv2Support else None,
            "StaticSourcesSupport": self.StaticSourcesSupport.value if self.StaticSourcesSupport else None,
        }


class TransitGatewayMulticastBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for shared resources

    def accept_transit_gateway_multicast_domain_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        subnet_ids = params.get("SubnetIds.N", [])
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")

        # Validate required parameters presence
        if not transit_gateway_multicast_domain_id:
            raise Exception("Missing required parameter TransitGatewayMulticastDomainId")

        # Get the multicast domain
        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomain {transit_gateway_multicast_domain_id} not found")

        # Find the association matching the attachment id and multicast domain id
        association = None
        for assoc in self.state.transit_gateway_multicast.values():
            # associations are stored in transit_gateway_multicast dict keyed by domain id, so we check subnets inside
            # but we do not have a separate associations store, so we must find association by attachment id and domain id
            # Actually, associations are not stored separately, so we create or update association here
            pass

        # We will create or update an association object for this attachment and multicast domain
        # The resourceId, resourceOwnerId, resourceType are unknown from params, so we leave them None
        # We update the subnets state to 'associated' for the given subnet ids

        # Check if an association already exists for this attachment and domain
        existing_association = None
        for assoc in self.state.transit_gateway_multicast.values():
            # The dict self.state.transit_gateway_multicast stores TransitGatewayMulticastDomain objects keyed by domain id
            # Associations are not stored there, so we need to store associations separately
            # But the instructions say to use self.state.transit_gateway_multicast (plural) dict for all multicast domains
            # We need to store associations somewhere, but no separate store is mentioned
            # We will create a new association object and store it in a new dict self.state.transit_gateway_multicast_associations keyed by (domain_id, attachment_id)
            # But since no such dict is mentioned, we will store associations inside the multicast domain object as a new attribute .associations (dict keyed by attachment id)
            # Let's check if multicast_domain has .associations attribute, if not create it
            if not hasattr(multicast_domain, "associations"):
                multicast_domain.associations = {}
            existing_association = multicast_domain.associations.get(transit_gateway_attachment_id)
            break

        if existing_association is None:
            # Create new association
            existing_association = TransitGatewayMulticastDomainAssociations()
            existing_association.resourceId = None
            existing_association.resourceOwnerId = None
            existing_association.resourceType = None
            existing_association.subnets = []
            existing_association.transitGatewayAttachmentId = transit_gateway_attachment_id
            existing_association.transitGatewayMulticastDomainId = transit_gateway_multicast_domain_id
            multicast_domain.associations[transit_gateway_attachment_id] = existing_association

        # Update subnets in association
        # For each subnet id in subnet_ids, find if it exists in association.subnets, if yes update state to associated, else add new SubnetAssociation with state associated
        for subnet_id in subnet_ids:
            found = False
            for subnet_assoc in existing_association.subnets:
                if subnet_assoc.subnetId == subnet_id:
                    subnet_assoc.state = SubnetAssociationState.associated
                    found = True
                    break
            if not found:
                new_subnet_assoc = SubnetAssociation()
                new_subnet_assoc.subnetId = subnet_id
                new_subnet_assoc.state = SubnetAssociationState.associated
                existing_association.subnets.append(new_subnet_assoc)

        # Prepare response dict
        response = {
            "associations": existing_association.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def associate_transit_gateway_multicast_domain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        subnet_ids = params.get("SubnetIds.N")
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")

        # Validate required parameters
        if subnet_ids is None:
            raise Exception("Missing required parameter SubnetIds.N")
        if transit_gateway_attachment_id is None:
            raise Exception("Missing required parameter TransitGatewayAttachmentId")
        if transit_gateway_multicast_domain_id is None:
            raise Exception("Missing required parameter TransitGatewayMulticastDomainId")

        # Get the multicast domain
        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomain {transit_gateway_multicast_domain_id} not found")

        # Similar to accept method, manage associations inside multicast_domain.associations dict keyed by attachment id
        if not hasattr(multicast_domain, "associations"):
            multicast_domain.associations = {}

        association = multicast_domain.associations.get(transit_gateway_attachment_id)
        if association is None:
            association = TransitGatewayMulticastDomainAssociations()
            association.resourceId = None
            association.resourceOwnerId = None
            association.resourceType = None
            association.subnets = []
            association.transitGatewayAttachmentId = transit_gateway_attachment_id
            association.transitGatewayMulticastDomainId = transit_gateway_multicast_domain_id
            multicast_domain.associations[transit_gateway_attachment_id] = association

        # For each subnet id, add or update subnet association with state associating
        for subnet_id in subnet_ids:
            found = False
            for subnet_assoc in association.subnets:
                if subnet_assoc.subnetId == subnet_id:
                    subnet_assoc.state = SubnetAssociationState.associating
                    found = True
                    break
            if not found:
                new_subnet_assoc = SubnetAssociation()
                new_subnet_assoc.subnetId = subnet_id
                new_subnet_assoc.state = SubnetAssociationState.associating
                association.subnets.append(new_subnet_assoc)

        response = {
            "associations": association.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def create_transit_gateway_multicast_domain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_id = params.get("TransitGatewayId")
        options_param = params.get("Options", {})
        tag_specifications = params.get("TagSpecification.N", [])

        if not transit_gateway_id:
            raise Exception("Missing required parameter TransitGatewayId")

        # Create options object
        options = TransitGatewayMulticastDomainOptions()
        if options_param:
            auto_accept = options_param.get("AutoAcceptSharedAssociations")
            if auto_accept:
                options.autoAcceptSharedAssociations = AutoAcceptSharedAssociations(auto_accept)
            igmpv2 = options_param.get("Igmpv2Support")
            if igmpv2:
                options.igmpv2Support = Igmpv2Support(igmpv2)
            static_sources = options_param.get("StaticSourcesSupport")
            if static_sources:
                options.staticSourcesSupport = StaticSourcesSupport(static_sources)

        # Create tags list
        tags = []
        for tag_spec in tag_specifications:
            # tag_spec is a dict with ResourceType and Tags list
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                tag = Tag()
                tag.Key = tag_dict.get("Key")
                tag.Value = tag_dict.get("Value")
                tags.append(tag)

        # Generate unique multicast domain id and arn
        multicast_domain_id = self.generate_unique_id(prefix="tgw-mcast-domain-")
        multicast_domain_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:transit-gateway-multicast-domain/{multicast_domain_id}"

        # Create multicast domain object
        multicast_domain = TransitGatewayMulticastDomain()
        multicast_domain.creationTime = datetime.utcnow()
        multicast_domain.options = options
        multicast_domain.ownerId = self.get_owner_id()
        multicast_domain.state = TransitGatewayMulticastDomainState.pending
        multicast_domain.tagSet = tags
        multicast_domain.transitGatewayId = transit_gateway_id
        multicast_domain.transitGatewayMulticastDomainArn = multicast_domain_arn
        multicast_domain.transitGatewayMulticastDomainId = multicast_domain_id

        # Store in state
        self.state.transit_gateway_multicast[multicast_domain_id] = multicast_domain

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayMulticastDomain": multicast_domain.to_dict(),
        }
        return response


    def delete_transit_gateway_multicast_domain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")
        if not transit_gateway_multicast_domain_id:
            raise Exception("Missing required parameter TransitGatewayMulticastDomainId")

        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomain {transit_gateway_multicast_domain_id} not found")

        # Mark state as deleting
        multicast_domain.state = TransitGatewayMulticastDomainState.deleting

        # In a real implementation, deletion would be asynchronous; here we simulate immediate deletion by removing from state
        # But to follow AWS behavior, we keep the object and mark state deleting, user can query state later
        # For this emulator, we keep it in state with deleting state

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayMulticastDomain": multicast_domain.to_dict(),
        }
        return response


    def deregister_transit_gateway_multicast_group_members(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_ip_address = params.get("GroupIpAddress")
        network_interface_ids = params.get("NetworkInterfaceIds.N", [])
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")

        # Validate multicast domain id
        if not transit_gateway_multicast_domain_id:
            raise Exception("Missing required parameter TransitGatewayMulticastDomainId")

        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomain {transit_gateway_multicast_domain_id} not found")

        # We need to deregister the specified network interfaces from the multicast group members
        # The state does not specify where group members are stored, so we assume multicast_domain has a dict attribute
        # registered_group_members keyed by group_ip_address with TransitGatewayMulticastRegisteredGroupMembers objects

        if not hasattr(multicast_domain, "registered_group_members"):
            multicast_domain.registered_group_members = {}

        registered_members = multicast_domain.registered_group_members.get(group_ip_address)
        if not registered_members:
            # No members registered for this group ip
            deregistered_ids = []
        else:
            # Remove the specified network interface ids from registeredNetworkInterfaceIds
            deregistered_ids = []
            for ni_id in network_interface_ids:
                if ni_id in registered_members.registeredNetworkInterfaceIds:
                    registered_members.registeredNetworkInterfaceIds.remove(ni_id)
                    deregistered_ids.append(ni_id)

        # Create deregistered group members object for response
        deregistered_group_members = TransitGatewayMulticastDeregisteredGroupMembers()
        deregistered_group_members.deregisteredNetworkInterfaceIds = deregistered_ids
        deregistered_group_members.groupIpAddress = group_ip_address
        deregistered_group_members.transitGatewayMulticastDomainId = transit_gateway_multicast_domain_id

        response = {
            "deregisteredMulticastGroupMembers": deregistered_group_members.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response

    def deregister_transit_gateway_multicast_group_sources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_ip_address = params.get("GroupIpAddress")
        network_interface_ids = params.get("NetworkInterfaceIds.N", [])
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")

        # Validate TransitGatewayMulticastDomainId presence and existence
        if not transit_gateway_multicast_domain_id:
            raise Exception("Missing required parameter TransitGatewayMulticastDomainId")
        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomainId {transit_gateway_multicast_domain_id} does not exist")

        # Validate network_interface_ids is a list if provided
        if network_interface_ids and not isinstance(network_interface_ids, list):
            raise Exception("NetworkInterfaceIds.N must be a list of strings")

        # Deregister the specified sources (network interfaces) from the multicast group
        # We assume multicast_domain has a dict or set attribute registered_group_sources keyed by network interface id
        # Since the data model is not fully specified, we simulate deregistration by removing from registered sources

        # For this emulation, we keep track of registered sources in multicast_domain.registered_group_sources: set of network interface ids
        # If attribute does not exist, initialize it
        if not hasattr(multicast_domain, "registered_group_sources"):
            multicast_domain.registered_group_sources = set()

        deregistered_network_interface_ids = []
        for ni_id in network_interface_ids:
            if ni_id in multicast_domain.registered_group_sources:
                multicast_domain.registered_group_sources.remove(ni_id)
                deregistered_network_interface_ids.append(ni_id)

        # Compose response object
        deregistered_group_sources = TransitGatewayMulticastDeregisteredGroupSources(
            deregisteredNetworkInterfaceIds=deregistered_network_interface_ids,
            groupIpAddress=group_ip_address,
            transitGatewayMulticastDomainId=transit_gateway_multicast_domain_id,
        )

        return {
            "requestId": self.generate_request_id(),
            "deregisteredMulticastGroupSources": deregistered_group_sources.to_dict(),
        }


    def describe_transit_gateway_multicast_domains(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = []
        # Filters can be passed as Filter.N.Name and Filter.N.Values
        # Collect filters from params keys
        # Example keys: Filter.1.Name, Filter.1.Values.1, Filter.1.Values.2, Filter.2.Name, ...
        # Parse filters
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    if filter_index not in filter_dict:
                        filter_dict[filter_index] = {"Name": None, "Values": []}
                    if filter_key == "Name":
                        filter_dict[filter_index]["Name"] = value
                    elif filter_key == "Values" and len(parts) == 4:
                        # Values.N
                        filter_dict[filter_index]["Values"].append(value)
        # Convert to list of Filter objects
        for f in filter_dict.values():
            if f["Name"]:
                filters.append(Filter(Name=f["Name"], Values=f["Values"]))

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise Exception("MaxResults must be between 5 and 1000")
            except Exception:
                raise Exception("MaxResults must be an integer between 5 and 1000")

        next_token = params.get("NextToken")
        transit_gateway_multicast_domain_ids = params.get("TransitGatewayMulticastDomainIds.N", [])

        # Filter the multicast domains from state
        all_domains = list(self.state.transit_gateway_multicast.values())

        # Filter by IDs if provided
        if transit_gateway_multicast_domain_ids:
            all_domains = [d for d in all_domains if d.transitGatewayMulticastDomainId in transit_gateway_multicast_domain_ids]

        # Apply filters
        def domain_matches_filters(domain: TransitGatewayMulticastDomain) -> bool:
            for f in filters:
                name = f.Name
                values = f.Values
                if name == "state":
                    if domain.state is None or domain.state.value not in values:
                        return False
                elif name == "transit-gateway-id":
                    if domain.transitGatewayId not in values:
                        return False
                elif name == "transit-gateway-multicast-domain-id":
                    if domain.transitGatewayMulticastDomainId not in values:
                        return False
                else:
                    # Unknown filter, ignore or exclude? AWS usually ignores unknown filters
                    pass
            return True

        filtered_domains = [d for d in all_domains if domain_matches_filters(d)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else len(filtered_domains)
        paged_domains = filtered_domains[start_index:end_index]

        # Prepare next token
        new_next_token = str(end_index) if end_index < len(filtered_domains) else None

        # Convert to dicts
        domains_dicts = [d.to_dict() for d in paged_domains]

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayMulticastDomains": domains_dicts,
            "nextToken": new_next_token,
        }


    def disassociate_transit_gateway_multicast_domain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        subnet_ids = params.get("SubnetIds.N")
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")

        # Validate required parameters
        if not subnet_ids or not isinstance(subnet_ids, list) or len(subnet_ids) == 0:
            raise Exception("SubnetIds.N is required and must be a non-empty list")
        if not transit_gateway_attachment_id:
            raise Exception("TransitGatewayAttachmentId is required")
        if not transit_gateway_multicast_domain_id:
            raise Exception("TransitGatewayMulticastDomainId is required")

        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomainId {transit_gateway_multicast_domain_id} does not exist")

        # Find the association matching the attachment id
        # We assume multicast_domain has attribute associations: dict keyed by attachment id to TransitGatewayMulticastDomainAssociations
        if not hasattr(multicast_domain, "associations"):
            multicast_domain.associations = {}

        association = multicast_domain.associations.get(transit_gateway_attachment_id)
        if not association:
            # Create a new association if not exists with empty subnets
            association = TransitGatewayMulticastDomainAssociations(
                resourceId=None,
                resourceOwnerId=None,
                resourceType=None,
                subnets=[],
                transitGatewayAttachmentId=transit_gateway_attachment_id,
                transitGatewayMulticastDomainId=transit_gateway_multicast_domain_id,
            )
            multicast_domain.associations[transit_gateway_attachment_id] = association

        # For each subnet id, find the subnet association and mark state as disassociating if currently associated or associating
        for subnet_id in subnet_ids:
            found = False
            for subnet_assoc in association.subnets:
                if subnet_assoc.subnetId == subnet_id:
                    found = True
                    # Only change state if currently associated or associating
                    if subnet_assoc.state in (SubnetAssociationState.ASSOCIATED, SubnetAssociationState.ASSOCIATING):
                        subnet_assoc.state = SubnetAssociationState.DISASSOCIATING
                    break
            if not found:
                # If subnet association not found, add it with state disassociating
                association.subnets.append(
                    SubnetAssociation(
                        state=SubnetAssociationState.DISASSOCIATING,
                        subnetId=subnet_id,
                    )
                )

        return {
            "requestId": self.generate_request_id(),
            "associations": association.to_dict(),
        }


    def get_transit_gateway_multicast_domain_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = []
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    if filter_index not in filter_dict:
                        filter_dict[filter_index] = {"Name": None, "Values": []}
                    if filter_key == "Name":
                        filter_dict[filter_index]["Name"] = value
                    elif filter_key == "Values" and len(parts) == 4:
                        filter_dict[filter_index]["Values"].append(value)
        for f in filter_dict.values():
            if f["Name"]:
                filters.append(Filter(Name=f["Name"], Values=f["Values"]))

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise Exception("MaxResults must be between 5 and 1000")
            except Exception:
                raise Exception("MaxResults must be an integer between 5 and 1000")

        next_token = params.get("NextToken")
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")
        if not transit_gateway_multicast_domain_id:
            raise Exception("TransitGatewayMulticastDomainId is required")

        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomainId {transit_gateway_multicast_domain_id} does not exist")

        # Collect all associations from multicast_domain.associations dict
        if not hasattr(multicast_domain, "associations"):
            multicast_domain.associations = {}

        all_associations = list(multicast_domain.associations.values())

        def association_matches_filters(assoc: TransitGatewayMulticastDomainAssociation) -> bool:
            for f in filters:
                name = f.Name
                values = f.Values
                if name == "resource-id":
                    if assoc.resourceId not in values:
                        return False
                elif name == "resource-type":
                    if assoc.resourceType is None or assoc.resourceType.value not in values:
                        return False
                elif name == "state":
                    if assoc.subnet is None or assoc.subnet.state is None or assoc.subnet.state.value not in values:
                        return False
                elif name == "subnet-id":
                    if assoc.subnet is None or assoc.subnet.subnetId not in values:
                        return False
                elif name == "transit-gateway-attachment-id":
                    if assoc.transitGatewayAttachmentId not in values:
                        return False
                else:
                    # Unknown filter ignored
                    pass
            return True

        filtered_associations = [a for a in all_associations if association_matches_filters(a)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else len(filtered_associations)
        paged_associations = filtered_associations[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(filtered_associations) else None

        associations_dicts = [a.to_dict() for a in paged_associations]

        return {
            "requestId": self.generate_request_id(),
            "multicastDomainAssociations": associations_dicts,
            "nextToken": new_next_token,
        }


    def register_transit_gateway_multicast_group_members(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_ip_address = params.get("GroupIpAddress")
        network_interface_ids = params.get("NetworkInterfaceIds.N")
        transit_gateway_multicast_domain_id = params.get("TransitGatewayMulticastDomainId")

        # Validate required parameters
        if not network_interface_ids or not isinstance(network_interface_ids, list) or len(network_interface_ids) == 0:
            raise Exception("NetworkInterfaceIds.N is required and must be a non-empty list")
        if not transit_gateway_multicast_domain_id:
            raise Exception("TransitGatewayMulticastDomainId is required")

        multicast_domain = self.state.transit_gateway_multicast.get(transit_gateway_multicast_domain_id)
        if not multicast_domain:
            raise Exception(f"TransitGatewayMulticastDomainId {transit_gateway_multicast_domain_id} does not exist")

        # We assume multicast_domain has attribute registered_group_members: set of network interface ids
        if not hasattr(multicast_domain, "registered_group_members"):
            multicast_domain.registered_group_members = set()

        for ni_id in network_interface_ids:
            multicast_domain.registered_group_members.add(ni_id)

        registered_group_members = TransitGatewayMulticastRegisteredGroupMembers(
            groupIpAddress=group_ip_address,
            registeredNetworkInterfaceIds=network_interface_ids,
            transitGatewayMulticastDomainId=transit_gateway_multicast_domain_id,
        )

        return {
            "requestId": self.generate_request_id(),
            "registeredMulticastGroupMembers": registered_group_members.to_dict(),
        }

    def register_transit_gateway_multicast_group_sources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        tg_mcast_domain_id = params.get("TransitGatewayMulticastDomainId")
        network_interface_ids = params.get("NetworkInterfaceIds")
        if not tg_mcast_domain_id:
            raise ValueError("TransitGatewayMulticastDomainId is required")
        if not network_interface_ids or not isinstance(network_interface_ids, list) or len(network_interface_ids) == 0:
            raise ValueError("NetworkInterfaceIds is required and must be a non-empty list")

        # DryRun check
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Get the multicast domain from state
        tg_mcast_domain = self.state.transit_gateway_multicast.get(tg_mcast_domain_id)
        if not tg_mcast_domain:
            raise ValueError(f"TransitGatewayMulticastDomainId {tg_mcast_domain_id} does not exist")

        group_ip_address = params.get("GroupIpAddress")

        # We will store registered sources in a dict keyed by group_ip_address
        # If group_ip_address is None, treat as empty string key
        group_key = group_ip_address if group_ip_address else ""

        # Initialize registered sources dict if not present
        if not hasattr(tg_mcast_domain, "registered_group_sources"):
            tg_mcast_domain.registered_group_sources = {}

        # Get or create the set of registered network interface ids for this group
        registered_nis = tg_mcast_domain.registered_group_sources.get(group_key, set())

        # Add new network interface ids
        for ni in network_interface_ids:
            registered_nis.add(ni)

        # Update the registered sources for this group
        tg_mcast_domain.registered_group_sources[group_key] = registered_nis

        # Prepare response object
        registered_sources_obj = TransitGatewayMulticastRegisteredGroupSources(
            groupIpAddress=group_ip_address,
            registeredNetworkInterfaceIds=list(registered_nis),
            transitGatewayMulticastDomainId=tg_mcast_domain_id,
        )

        response = {
            "registeredMulticastGroupSources": registered_sources_obj.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def reject_transit_gateway_multicast_domain_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        tg_mcast_domain_id = params.get("TransitGatewayMulticastDomainId")
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        subnet_ids = params.get("SubnetIds", [])

        # Validate that at least one of the identifiers is provided
        if not tg_mcast_domain_id and not transit_gateway_attachment_id and not subnet_ids:
            raise ValueError("At least one of TransitGatewayMulticastDomainId, TransitGatewayAttachmentId, or SubnetIds must be provided")

        # Find matching associations to reject
        # Associations are stored in self.state.transit_gateway_multicast_associations keyed by id or in the domain object?
        # We assume associations are stored in the domain object or in state.transit_gateway_multicast_associations dict keyed by some id
        # Since no id is given, we will iterate all associations and reject matching ones

        # For this implementation, we will iterate all associations in self.state.transit_gateway_multicast.values()
        # and find those matching the criteria

        associations_to_reject = []

        for assoc_id, assoc in self.state.transit_gateway_multicast.items():
            # assoc is a TransitGatewayMulticastDomain object
            # We want to find associations inside the domain matching the criteria
            # But the domain object does not have associations attribute in the given structure
            # Instead, we have TransitGatewayMulticastDomainAssociations class, but no direct mapping
            # We will assume self.state.transit_gateway_multicast_associations dict exists keyed by some id
            # But since no such dict is mentioned, we will scan all associations in self.state.transit_gateway_multicast_associations if exists
            # Since no such dict is mentioned, we will scan all associations in self.state.transit_gateway_multicast_associations if exists
            # The problem statement does not mention such a dict, so we will assume associations are stored in self.state.transit_gateway_multicast_associations dict

            # So we check if self.state has attribute transit_gateway_multicast_associations
            # If not, we create empty dict to avoid error
            if not hasattr(self.state, "transit_gateway_multicast_associations"):
                self.state.transit_gateway_multicast_associations = {}

            break  # break the outer loop to avoid confusion, we will iterate associations below

        rejected_associations = []

        for assoc_id, assoc in self.state.transit_gateway_multicast_associations.items():
            # assoc is TransitGatewayMulticastDomainAssociations
            if tg_mcast_domain_id and assoc.transitGatewayMulticastDomainId != tg_mcast_domain_id:
                continue
            if transit_gateway_attachment_id and assoc.transitGatewayAttachmentId != transit_gateway_attachment_id:
                continue
            if subnet_ids:
                # Check if any subnet in assoc.subnets matches subnet_ids
                if not any(subnet.subnetId in subnet_ids for subnet in assoc.subnets):
                    continue

            # Mark all subnets in this association as rejected
            for subnet in assoc.subnets:
                subnet.state = SubnetAssociationState.REJECTED

            rejected_associations.append(assoc)

        # For response, return the first matching association or empty if none
        associations_response = None
        if rejected_associations:
            # Return the first rejected association as response
            associations_response = rejected_associations[0].to_dict()
        else:
            # Return empty association object
            associations_response = TransitGatewayMulticastDomainAssociations(
                resourceId=None,
                resourceOwnerId=None,
                resourceType=None,
                subnets=[],
                transitGatewayAttachmentId=None,
                transitGatewayMulticastDomainId=None,
            ).to_dict()

        response = {
            "associations": associations_response,
            "requestId": self.generate_request_id(),
        }
        return response


    def search_transit_gateway_multicast_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tg_mcast_domain_id = params.get("TransitGatewayMulticastDomainId")
        if not tg_mcast_domain_id:
            raise ValueError("TransitGatewayMulticastDomainId is required")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate max_results if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Get the multicast domain
        tg_mcast_domain = self.state.transit_gateway_multicast.get(tg_mcast_domain_id)
        if not tg_mcast_domain:
            raise ValueError(f"TransitGatewayMulticastDomainId {tg_mcast_domain_id} does not exist")

        # We need to collect all multicast groups for this domain
        # Multicast groups are not explicitly stored in the domain object in the given structure
        # But we have registered group members and sources stored in domain attributes or state
        # We will assume domain has:
        # - registered_group_members: dict keyed by group_ip_address -> set of network interface ids
        # - registered_group_sources: dict keyed by group_ip_address -> set of network interface ids
        # If not present, treat as empty

        registered_group_members = getattr(tg_mcast_domain, "registered_group_members", {})
        registered_group_sources = getattr(tg_mcast_domain, "registered_group_sources", {})

        # We will build a list of TransitGatewayMulticastGroup objects representing all group memberships and sources

        groups = []

        # Add group members
        for group_ip, ni_set in registered_group_members.items():
            for ni in ni_set:
                # We need to get resource info for network interface id ni
                # We try to get resource from state
                resource = self.state.get_resource(ni)
                subnet_id = None
                transit_gateway_attachment_id = None
                resource_id = None
                resource_owner_id = None
                resource_type = None
                if resource:
                    subnet_id = getattr(resource, "subnetId", None)
                    transit_gateway_attachment_id = getattr(resource, "transitGatewayAttachmentId", None)
                    resource_id = getattr(resource, "resourceId", None)
                    resource_owner_id = getattr(resource, "ownerId", None)
                    resource_type = getattr(resource, "resourceType", None)

                group = TransitGatewayMulticastGroup(
                    groupIpAddress=group_ip if group_ip else None,
                    groupMember=True,
                    groupSource=False,
                    memberType=MemberType.STATIC,
                    networkInterfaceId=ni,
                    resourceId=resource_id,
                    resourceOwnerId=resource_owner_id,
                    resourceType=resource_type,
                    sourceType=None,
                    subnetId=subnet_id,
                    transitGatewayAttachmentId=transit_gateway_attachment_id,
                )
                groups.append(group)

        # Add group sources
        for group_ip, ni_set in registered_group_sources.items():
            for ni in ni_set:
                resource = self.state.get_resource(ni)
                subnet_id = None
                transit_gateway_attachment_id = None
                resource_id = None
                resource_owner_id = None
                resource_type = None
                if resource:
                    subnet_id = getattr(resource, "subnetId", None)
                    transit_gateway_attachment_id = getattr(resource, "transitGatewayAttachmentId", None)
                    resource_id = getattr(resource, "resourceId", None)
                    resource_owner_id = getattr(resource, "ownerId", None)
                    resource_type = getattr(resource, "resourceType", None)

                group = TransitGatewayMulticastGroup(
                    groupIpAddress=group_ip if group_ip else None,
                    groupMember=False,
                    groupSource=True,
                    memberType=None,
                    networkInterfaceId=ni,
                    resourceId=resource_id,
                    resourceOwnerId=resource_owner_id,
                    resourceType=resource_type,
                    sourceType=SourceType.STATIC,
                    subnetId=subnet_id,
                    transitGatewayAttachmentId=transit_gateway_attachment_id,
                )
                groups.append(group)

        # Apply filters if any
        def matches_filter(group: TransitGatewayMulticastGroup, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if not name or not values:
                return True
            # Map filter names to group attributes
            if name == "group-ip-address":
                return group.groupIpAddress in values
            elif name == "is-group-member":
                # values are "true" or "false" strings
                val = "true" if group.groupMember else "false"
                return val in values
            elif name == "is-group-source":
                val = "true" if group.groupSource else "false"
                return val in values
            elif name == "member-type":
                if group.memberType is None:
                    return False
                return group.memberType.value in values
            elif name == "resource-id":
                return group.resourceId in values
            elif name == "resource-type":
                if group.resourceType is None:
                    return False
                return group.resourceType.value in values
            elif name == "source-type":
                if group.sourceType is None:
                    return False
                return group.sourceType.value in values
            elif name == "subnet-id":
                return group.subnetId in values
            elif name == "transit-gateway-attachment-id":
                return group.transitGatewayAttachmentId in values
            else:
                # Unknown filter, ignore
                return True

        filtered_groups = groups
        if filters:
            # filters is a list of Filter objects or dicts
            # Convert dicts to Filter objects if needed
            filter_objs = []
            for f in filters:
                if isinstance(f, Filter):
                    filter_objs.append(f)
                elif isinstance(f, dict):
                    filter_objs.append(Filter(Name=f.get("Name"), Values=f.get("Values", [])))
            for f in filter_objs:
                filtered_groups = [g for g in filtered_groups if matches_filter(g, f)]

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(filtered_groups)
        if max_results:
            end_index = min(start_index + max_results, len(filtered_groups))

        paged_groups = filtered_groups[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(filtered_groups):
            new_next_token = str(end_index)

        response = {
            "multicastGroups": [g.to_dict() for g in paged_groups],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class TransitGatewayMulticastGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptTransitGatewayMulticastDomainAssociations", self.accept_transit_gateway_multicast_domain_associations)
        self.register_action("AssociateTransitGatewayMulticastDomain", self.associate_transit_gateway_multicast_domain)
        self.register_action("CreateTransitGatewayMulticastDomain", self.create_transit_gateway_multicast_domain)
        self.register_action("DeleteTransitGatewayMulticastDomain", self.delete_transit_gateway_multicast_domain)
        self.register_action("DeregisterTransitGatewayMulticastGroupMembers", self.deregister_transit_gateway_multicast_group_members)
        self.register_action("DeregisterTransitGatewayMulticastGroupSources", self.deregister_transit_gateway_multicast_group_sources)
        self.register_action("DescribeTransitGatewayMulticastDomains", self.describe_transit_gateway_multicast_domains)
        self.register_action("DisassociateTransitGatewayMulticastDomain", self.disassociate_transit_gateway_multicast_domain)
        self.register_action("GetTransitGatewayMulticastDomainAssociations", self.get_transit_gateway_multicast_domain_associations)
        self.register_action("RegisterTransitGatewayMulticastGroupMembers", self.register_transit_gateway_multicast_group_members)
        self.register_action("RegisterTransitGatewayMulticastGroupSources", self.register_transit_gateway_multicast_group_sources)
        self.register_action("RejectTransitGatewayMulticastDomainAssociations", self.reject_transit_gateway_multicast_domain_associations)
        self.register_action("SearchTransitGatewayMulticastGroups", self.search_transit_gateway_multicast_groups)

    def accept_transit_gateway_multicast_domain_associations(self, params):
        return self.backend.accept_transit_gateway_multicast_domain_associations(params)

    def associate_transit_gateway_multicast_domain(self, params):
        return self.backend.associate_transit_gateway_multicast_domain(params)

    def create_transit_gateway_multicast_domain(self, params):
        return self.backend.create_transit_gateway_multicast_domain(params)

    def delete_transit_gateway_multicast_domain(self, params):
        return self.backend.delete_transit_gateway_multicast_domain(params)

    def deregister_transit_gateway_multicast_group_members(self, params):
        return self.backend.deregister_transit_gateway_multicast_group_members(params)

    def deregister_transit_gateway_multicast_group_sources(self, params):
        return self.backend.deregister_transit_gateway_multicast_group_sources(params)

    def describe_transit_gateway_multicast_domains(self, params):
        return self.backend.describe_transit_gateway_multicast_domains(params)

    def disassociate_transit_gateway_multicast_domain(self, params):
        return self.backend.disassociate_transit_gateway_multicast_domain(params)

    def get_transit_gateway_multicast_domain_associations(self, params):
        return self.backend.get_transit_gateway_multicast_domain_associations(params)

    def register_transit_gateway_multicast_group_members(self, params):
        return self.backend.register_transit_gateway_multicast_group_members(params)

    def register_transit_gateway_multicast_group_sources(self, params):
        return self.backend.register_transit_gateway_multicast_group_sources(params)

    def reject_transit_gateway_multicast_domain_associations(self, params):
        return self.backend.reject_transit_gateway_multicast_domain_associations(params)

    def search_transit_gateway_multicast_groups(self, params):
        return self.backend.search_transit_gateway_multicast_groups(params)
