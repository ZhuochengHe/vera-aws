from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class TransitGatewayAssociationState(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"


class TransitGatewayResourceType(str, Enum):
    VPC = "vpc"
    VPN = "vpn"
    VPN_CONCENTRATOR = "vpn-concentrator"
    DIRECT_CONNECT_GATEWAY = "direct-connect-gateway"
    CONNECT = "connect"
    PEERING = "peering"
    TGW_PEERING = "tgw-peering"  # deprecated but included


@dataclass
class TransitGatewayAssociation:
    resource_id: Optional[str] = None
    resource_type: Optional[TransitGatewayResourceType] = None
    state: Optional[TransitGatewayAssociationState] = None
    transit_gateway_attachment_id: Optional[str] = None
    transit_gateway_route_table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resource_id,
            "ResourceType": self.resource_type.value if self.resource_type else None,
            "State": self.state.value if self.state else None,
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "TransitGatewayRouteTableId": self.transit_gateway_route_table_id,
        }


class TransitGatewayPrefixListReferenceState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    MODIFYING = "modifying"
    DELETING = "deleting"


@dataclass
class TransitGatewayPrefixListAttachment:
    resource_id: Optional[str] = None
    resource_type: Optional[TransitGatewayResourceType] = None
    transit_gateway_attachment_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resource_id,
            "ResourceType": self.resource_type.value if self.resource_type else None,
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
        }


@dataclass
class TransitGatewayPrefixListReference:
    blackhole: Optional[bool] = None
    prefix_list_id: Optional[str] = None
    prefix_list_owner_id: Optional[str] = None
    state: Optional[TransitGatewayPrefixListReferenceState] = None
    transit_gateway_attachment: Optional[TransitGatewayPrefixListAttachment] = None
    transit_gateway_route_table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Blackhole": self.blackhole,
            "PrefixListId": self.prefix_list_id,
            "PrefixListOwnerId": self.prefix_list_owner_id,
            "State": self.state.value if self.state else None,
            "TransitGatewayAttachment": self.transit_gateway_attachment.to_dict() if self.transit_gateway_attachment else None,
            "TransitGatewayRouteTableId": self.transit_gateway_route_table_id,
        }


class TransitGatewayRouteState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    BLACKHOLE = "blackhole"
    DELETING = "deleting"
    DELETED = "deleted"


class TransitGatewayRouteType(str, Enum):
    STATIC = "static"
    PROPAGATED = "propagated"


@dataclass
class TransitGatewayRouteAttachment:
    resource_id: Optional[str] = None
    resource_type: Optional[TransitGatewayResourceType] = None
    transit_gateway_attachment_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resource_id,
            "ResourceType": self.resource_type.value if self.resource_type else None,
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
        }


@dataclass
class TransitGatewayRoute:
    destination_cidr_block: Optional[str] = None
    prefix_list_id: Optional[str] = None
    state: Optional[TransitGatewayRouteState] = None
    transit_gateway_attachments: List[TransitGatewayRouteAttachment] = field(default_factory=list)
    transit_gateway_route_table_announcement_id: Optional[str] = None
    type: Optional[TransitGatewayRouteType] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": self.destination_cidr_block,
            "PrefixListId": self.prefix_list_id,
            "State": self.state.value if self.state else None,
            "TransitGatewayAttachments": [att.to_dict() for att in self.transit_gateway_attachments],
            "TransitGatewayRouteTableAnnouncementId": self.transit_gateway_route_table_announcement_id,
            "Type": self.type.value if self.type else None,
        }


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class TransitGatewayRouteTable:
    creation_time: Optional[datetime] = None
    default_association_route_table: Optional[bool] = None
    default_propagation_route_table: Optional[bool] = None
    state: Optional[ResourceState] = None
    tag_set: List[Tag] = field(default_factory=list)
    transit_gateway_id: Optional[str] = None
    transit_gateway_route_table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CreationTime": self.creation_time.isoformat() if self.creation_time else None,
            "DefaultAssociationRouteTable": self.default_association_route_table,
            "DefaultPropagationRouteTable": self.default_propagation_route_table,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "TransitGatewayId": self.transit_gateway_id,
            "TransitGatewayRouteTableId": self.transit_gateway_route_table_id,
        }


class TransitGatewayRouteTableAnnouncementDirection(str, Enum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"


class TransitGatewayRouteTableAnnouncementState(str, Enum):
    AVAILABLE = "available"
    PENDING = "pending"
    FAILING = "failing"
    FAILED = "failed"
    DELETING = "deleting"
    DELETED = "deleted"


@dataclass
class TransitGatewayRouteTableAnnouncement:
    announcement_direction: Optional[TransitGatewayRouteTableAnnouncementDirection] = None
    core_network_id: Optional[str] = None
    creation_time: Optional[datetime] = None
    peer_core_network_id: Optional[str] = None
    peering_attachment_id: Optional[str] = None
    peer_transit_gateway_id: Optional[str] = None
    state: Optional[TransitGatewayRouteTableAnnouncementState] = None
    tag_set: List[Tag] = field(default_factory=list)
    transit_gateway_id: Optional[str] = None
    transit_gateway_route_table_announcement_id: Optional[str] = None
    transit_gateway_route_table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AnnouncementDirection": self.announcement_direction.value if self.announcement_direction else None,
            "CoreNetworkId": self.core_network_id,
            "CreationTime": self.creation_time.isoformat() if self.creation_time else None,
            "PeerCoreNetworkId": self.peer_core_network_id,
            "PeeringAttachmentId": self.peering_attachment_id,
            "PeerTransitGatewayId": self.peer_transit_gateway_id,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "TransitGatewayId": self.transit_gateway_id,
            "TransitGatewayRouteTableAnnouncementId": self.transit_gateway_route_table_announcement_id,
            "TransitGatewayRouteTableId": self.transit_gateway_route_table_id,
        }


class TransitGatewayPropagationState(str, Enum):
    ENABLING = "enabling"
    ENABLED = "enabled"
    DISABLING = "disabling"
    DISABLED = "disabled"


@dataclass
class TransitGatewayPropagation:
    resource_id: Optional[str] = None
    resource_type: Optional[TransitGatewayResourceType] = None
    state: Optional[TransitGatewayPropagationState] = None
    transit_gateway_attachment_id: Optional[str] = None
    transit_gateway_route_table_announcement_id: Optional[str] = None
    transit_gateway_route_table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resource_id,
            "ResourceType": self.resource_type.value if self.resource_type else None,
            "State": self.state.value if self.state else None,
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "TransitGatewayRouteTableAnnouncementId": self.transit_gateway_route_table_announcement_id,
            "TransitGatewayRouteTableId": self.transit_gateway_route_table_id,
        }


@dataclass
class TransitGatewayRouteTableAssociation:
    resource_id: Optional[str] = None
    resource_type: Optional[TransitGatewayResourceType] = None
    state: Optional[TransitGatewayAssociationState] = None
    transit_gateway_attachment_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resource_id,
            "ResourceType": self.resource_type.value if self.resource_type else None,
            "State": self.state.value if self.state else None,
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
        }


@dataclass
class TransitGatewayRouteTablePropagation:
    resource_id: Optional[str] = None
    resource_type: Optional[TransitGatewayResourceType] = None
    state: Optional[TransitGatewayPropagationState] = None
    transit_gateway_attachment_id: Optional[str] = None
    transit_gateway_route_table_announcement_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resource_id,
            "ResourceType": self.resource_type.value if self.resource_type else None,
            "State": self.state.value if self.state else None,
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "TransitGatewayRouteTableAnnouncementId": self.transit_gateway_route_table_announcement_id,
        }


@dataclass
class TransitGatewayAttachmentPropagation:
    state: Optional[TransitGatewayPropagationState] = None
    transit_gateway_route_table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "State": self.state.value if self.state else None,
            "TransitGatewayRouteTableId": self.transit_gateway_route_table_id,
        }


class TransitgatewayroutetablesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for shared resources

    def associate_transit_gateway_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")

        if not transit_gateway_attachment_id:
            raise ValueError("TransitGatewayAttachmentId is required")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # Validate that the route table exists
        route_table = self.state.transit_gateway_route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            raise ValueError(f"TransitGatewayRouteTable {transit_gateway_route_table_id} does not exist")

        # Validate that the attachment exists
        attachment = self.state.get_resource(transit_gateway_attachment_id)
        if not attachment:
            raise ValueError(f"TransitGatewayAttachment {transit_gateway_attachment_id} does not exist")

        # Check if this attachment is already associated with any route table
        for assoc in self.state.transit_gateway_route_table_associations.values():
            if assoc.transit_gateway_attachment_id == transit_gateway_attachment_id:
                # Only one route table can be associated with an attachment
                if assoc.transit_gateway_route_table_id == transit_gateway_route_table_id:
                    # Already associated with this route table, return existing association
                    association = assoc
                    break
                else:
                    raise ValueError(f"Attachment {transit_gateway_attachment_id} is already associated with route table {assoc.transit_gateway_route_table_id}")
        else:
            # Create new association
            association_id = self.generate_unique_id(prefix="tgw-rtb-assoc-")
            association = TransitGatewayAssociation()
            association.transit_gateway_attachment_id = transit_gateway_attachment_id
            association.transit_gateway_route_table_id = transit_gateway_route_table_id
            association.state = TransitGatewayAssociationState.associating
            # We do not have resource_id or resource_type info here, leave None
            self.state.transit_gateway_route_table_associations[association_id] = association

        # Update association state to associated
        association.state = TransitGatewayAssociationState.associated

        return {
            "association": association.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_transit_gateway_prefix_list_reference(self, params: Dict[str, Any]) -> Dict[str, Any]:
        prefix_list_id = params.get("PrefixListId")
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        blackhole = params.get("Blackhole", False)

        if not prefix_list_id:
            raise ValueError("PrefixListId is required")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # Validate route table exists
        route_table = self.state.transit_gateway_route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            raise ValueError(f"TransitGatewayRouteTable {transit_gateway_route_table_id} does not exist")

        # Validate attachment if provided
        attachment_obj = None
        if transit_gateway_attachment_id:
            attachment_resource = self.state.get_resource(transit_gateway_attachment_id)
            if not attachment_resource:
                raise ValueError(f"TransitGatewayAttachment {transit_gateway_attachment_id} does not exist")
            # Create TransitGatewayPrefixListAttachment object
            attachment_obj = TransitGatewayPrefixListAttachment()
            attachment_obj.transit_gateway_attachment_id = transit_gateway_attachment_id
            # Try to fill resource_id and resource_type if possible
            if hasattr(attachment_resource, "resource_id"):
                attachment_obj.resource_id = getattr(attachment_resource, "resource_id", None)
            if hasattr(attachment_resource, "resource_type"):
                attachment_obj.resource_type = getattr(attachment_resource, "resource_type", None)

        # Create prefix list reference object
        prefix_list_reference_id = self.generate_unique_id(prefix="tgw-plref-")
        prefix_list_reference = TransitGatewayPrefixListReference()
        prefix_list_reference.blackhole = blackhole
        prefix_list_reference.prefix_list_id = prefix_list_id
        prefix_list_reference.prefix_list_owner_id = self.get_owner_id()
        prefix_list_reference.state = TransitGatewayPrefixListReferenceState.pending
        prefix_list_reference.transit_gateway_attachment = attachment_obj
        prefix_list_reference.transit_gateway_route_table_id = transit_gateway_route_table_id

        # Store in state
        if not hasattr(self.state, "transit_gateway_prefix_list_references"):
            self.state.transit_gateway_prefix_list_references = {}
        self.state.transit_gateway_prefix_list_references[prefix_list_reference_id] = prefix_list_reference

        # Transition state to available (simulate immediate availability)
        prefix_list_reference.state = TransitGatewayPrefixListReferenceState.available

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayPrefixListReference": prefix_list_reference.to_dict(),
        }


    def create_transit_gateway_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        destination_cidr_block = params.get("DestinationCidrBlock")
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        blackhole = params.get("Blackhole", False)

        if not destination_cidr_block:
            raise ValueError("DestinationCidrBlock is required")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # Validate route table exists
        route_table = self.state.transit_gateway_route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            raise ValueError(f"TransitGatewayRouteTable {transit_gateway_route_table_id} does not exist")

        # Create route attachments list
        attachments = []
        if transit_gateway_attachment_id:
            attachment_resource = self.state.get_resource(transit_gateway_attachment_id)
            if not attachment_resource:
                raise ValueError(f"TransitGatewayAttachment {transit_gateway_attachment_id} does not exist")
            attachment_obj = TransitGatewayRouteAttachment()
            attachment_obj.transit_gateway_attachment_id = transit_gateway_attachment_id
            if hasattr(attachment_resource, "resource_id"):
                attachment_obj.resource_id = getattr(attachment_resource, "resource_id", None)
            if hasattr(attachment_resource, "resource_type"):
                attachment_obj.resource_type = getattr(attachment_resource, "resource_type", None)
            attachments.append(attachment_obj)

        # Check if route already exists for this destination in this route table
        existing_route = None
        if not hasattr(self.state, "transit_gateway_routes"):
            self.state.transit_gateway_routes = {}
        for route_id, route in self.state.transit_gateway_routes.items():
            if route.transit_gateway_route_table_id == transit_gateway_route_table_id and route.destination_cidr_block == destination_cidr_block:
                existing_route = route
                break

        if existing_route:
            # Update existing route
            existing_route.state = TransitGatewayRouteState.active if not blackhole else TransitGatewayRouteState.blackhole
            existing_route.transit_gateway_attachments = attachments
            existing_route.type = TransitGatewayRouteType.static
            route = existing_route
        else:
            # Create new route
            route_id = self.generate_unique_id(prefix="tgw-route-")
            route = TransitGatewayRoute()
            route.destination_cidr_block = destination_cidr_block
            route.prefix_list_id = None
            route.state = TransitGatewayRouteState.blackhole if blackhole else TransitGatewayRouteState.active
            route.transit_gateway_attachments = attachments
            route.transit_gateway_route_table_announcement_id = None
            route.type = TransitGatewayRouteType.static
            route.transit_gateway_route_table_id = transit_gateway_route_table_id
            self.state.transit_gateway_routes[route_id] = route

        return {
            "requestId": self.generate_request_id(),
            "route": route.to_dict(),
        }


    def create_transit_gateway_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_id = params.get("TransitGatewayId")
        tag_specifications = params.get("TagSpecifications", [])

        if not transit_gateway_id:
            raise ValueError("TransitGatewayId is required")

        # Validate transit gateway exists
        transit_gateway = self.state.get_resource(transit_gateway_id)
        if not transit_gateway:
            raise ValueError(f"TransitGateway {transit_gateway_id} does not exist")

        # Create new transit gateway route table
        route_table_id = self.generate_unique_id(prefix="tgw-rtb-")
        route_table = TransitGatewayRouteTable()
        route_table.creation_time = datetime.utcnow()
        route_table.default_association_route_table = False
        route_table.default_propagation_route_table = False
        route_table.state = ResourceState.pending
        route_table.transit_gateway_id = transit_gateway_id
        route_table.transit_gateway_route_table_id = route_table_id
        route_table.tag_set = []

        # Process tags from TagSpecifications
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    route_table.tag_set.append(Tag(key=key, value=value))

        # Store in state
        self.state.transit_gateway_route_tables[route_table_id] = route_table

        # Transition state to available (simulate immediate availability)
        route_table.state = ResourceState.available

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayRouteTable": route_table.to_dict(),
        }


    def create_transit_gateway_route_table_announcement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        peering_attachment_id = params.get("PeeringAttachmentId")
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        tag_specifications = params.get("TagSpecification", [])

        if not peering_attachment_id:
            raise ValueError("PeeringAttachmentId is required")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # Validate peering attachment exists
        peering_attachment = self.state.get_resource(peering_attachment_id)
        if not peering_attachment:
            raise ValueError(f"PeeringAttachment {peering_attachment_id} does not exist")

        # Validate route table exists
        route_table = self.state.transit_gateway_route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            raise ValueError(f"TransitGatewayRouteTable {transit_gateway_route_table_id} does not exist")

        # Create new route table announcement
        announcement_id = self.generate_unique_id(prefix="tgw-rtb-ann-")
        announcement = TransitGatewayRouteTableAnnouncement()
        announcement.announcement_direction = TransitGatewayRouteTableAnnouncementDirection.outgoing
        announcement.core_network_id = None
        announcement.creation_time = datetime.utcnow()
        announcement.peer_core_network_id = None
        announcement.peering_attachment_id = peering_attachment_id
        announcement.peer_transit_gateway_id = None
        announcement.state = TransitGatewayRouteTableAnnouncementState.pending
        announcement.transit_gateway_id = route_table.transit_gateway_id
        announcement.transit_gateway_route_table_announcement_id = announcement_id
        announcement.transit_gateway_route_table_id = transit_gateway_route_table_id
        announcement.tag_set = []

        # Process tags from TagSpecification
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    announcement.tag_set.append(Tag(key=key, value=value))

        # Store in state
        if not hasattr(self.state, "transit_gateway_route_table_announcements"):
            self.state.transit_gateway_route_table_announcements = {}
        self.state.transit_gateway_route_table_announcements[announcement_id] = announcement

        # Transition state to available (simulate immediate availability)
        announcement.state = TransitGatewayRouteTableAnnouncementState.available

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayRouteTableAnnouncement": announcement.to_dict(),
        }

    def delete_transit_gateway_prefix_list_reference(self, params: dict) -> dict:
        prefix_list_id = params.get("PrefixListId")
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        if not prefix_list_id:
            raise ValueError("PrefixListId is required")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # Find the prefix list reference in the state
        prefix_list_references = self.state.transit_gateway_prefix_list_references if hasattr(self.state, "transit_gateway_prefix_list_references") else {}
        # If not present, create empty dict to avoid error
        if prefix_list_references is None:
            prefix_list_references = {}

        # Find the prefix list reference matching prefix_list_id and transit_gateway_route_table_id
        found_ref = None
        for ref_id, ref in prefix_list_references.items():
            if (
                ref.prefix_list_id == prefix_list_id
                and ref.transit_gateway_route_table_id == transit_gateway_route_table_id
            ):
                found_ref = ref
                break

        if not found_ref:
            # If not found, create a dummy reference with state deleting as per AWS behavior
            # But better to raise error? AWS returns empty response if not found
            # Here we return a response with state deleting and the ids
            found_ref = TransitGatewayPrefixListReference()
            found_ref.prefix_list_id = prefix_list_id
            found_ref.transit_gateway_route_table_id = transit_gateway_route_table_id
            found_ref.state = TransitGatewayPrefixListReferenceState.DELETING if hasattr(TransitGatewayPrefixListReferenceState, "DELETING") else "deleting"
            found_ref.blackhole = False
            found_ref.prefix_list_owner_id = None
            found_ref.transit_gateway_attachment = None
        else:
            # Mark the state as deleting
            found_ref.state = TransitGatewayPrefixListReferenceState.DELETING if hasattr(TransitGatewayPrefixListReferenceState, "DELETING") else "deleting"
            # Remove from state after marking deleting
            # Remove from the dict
            del prefix_list_references[ref_id]

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayPrefixListReference": found_ref.to_dict(),
        }


    def delete_transit_gateway_route(self, params: dict) -> dict:
        destination_cidr_block = params.get("DestinationCidrBlock")
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        if not destination_cidr_block:
            raise ValueError("DestinationCidrBlock is required")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        route_tables = self.state.transit_gateway_route_tables if hasattr(self.state, "transit_gateway_route_tables") else {}
        if route_tables is None:
            route_tables = {}

        route_table = route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            # No such route table, return empty route info with state deleted?
            route = TransitGatewayRoute()
            route.destination_cidr_block = destination_cidr_block
            route.state = TransitGatewayRouteState.DELETED if hasattr(TransitGatewayRouteState, "DELETED") else "deleted"
            route.prefix_list_id = None
            route.transit_gateway_attachments = []
            route.transit_gateway_route_table_announcement_id = None
            route.type = None
            return {
                "requestId": self.generate_request_id(),
                "route": route.to_dict(),
            }

        # Find the route in the route table's routes
        # Assuming route_table has attribute routes: List[TransitGatewayRoute]
        # But from given structure, route_table does not show routes attribute explicitly
        # We must assume self.state has a dict of routes keyed by route table id and destination cidr block or prefix list id
        # Let's assume self.state.transit_gateway_routes is a dict keyed by (route_table_id, destination_cidr_block)
        # If not present, we try to find route in route_table.routes if exists

        routes = getattr(self.state, "transit_gateway_routes", {})
        if routes is None:
            routes = {}

        route_key = (transit_gateway_route_table_id, destination_cidr_block)
        route = routes.get(route_key)

        if not route:
            # Route not found, return route with state deleted
            route = TransitGatewayRoute()
            route.destination_cidr_block = destination_cidr_block
            route.state = TransitGatewayRouteState.DELETED if hasattr(TransitGatewayRouteState, "DELETED") else "deleted"
            route.prefix_list_id = None
            route.transit_gateway_attachments = []
            route.transit_gateway_route_table_announcement_id = None
            route.type = None
            return {
                "requestId": self.generate_request_id(),
                "route": route.to_dict(),
            }

        # Mark route as deleted and remove from routes dict
        route.state = TransitGatewayRouteState.DELETED if hasattr(TransitGatewayRouteState, "DELETED") else "deleted"
        del routes[route_key]

        return {
            "requestId": self.generate_request_id(),
            "route": route.to_dict(),
        }


    def delete_transit_gateway_route_table(self, params: dict) -> dict:
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        route_tables = self.state.transit_gateway_route_tables if hasattr(self.state, "transit_gateway_route_tables") else {}
        if route_tables is None:
            route_tables = {}

        route_table = route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            # Return empty route table info with state deleted?
            deleted_route_table = TransitGatewayRouteTable()
            deleted_route_table.transit_gateway_route_table_id = transit_gateway_route_table_id
            deleted_route_table.state = ResourceState.DELETED if hasattr(ResourceState, "DELETED") else "deleted"
            deleted_route_table.creation_time = None
            deleted_route_table.default_association_route_table = None
            deleted_route_table.default_propagation_route_table = None
            deleted_route_table.tag_set = []
            deleted_route_table.transit_gateway_id = None
            return {
                "requestId": self.generate_request_id(),
                "transitGatewayRouteTable": deleted_route_table.to_dict(),
            }

        # Check if there are any associations or propagations linked to this route table
        # Associations and propagations are stored in state.transit_gateway_route_table_associations and state.transit_gateway_route_table_propagations
        associations = getattr(self.state, "transit_gateway_route_table_associations", {})
        propagations = getattr(self.state, "transit_gateway_route_table_propagations", {})

        # Check if any association or propagation references this route table id
        for assoc in associations.values():
            if assoc.transit_gateway_route_table_id == transit_gateway_route_table_id:
                raise Exception("Must disassociate route tables before deletion")

        for prop in propagations.values():
            if prop.transit_gateway_route_table_id == transit_gateway_route_table_id:
                raise Exception("Must disassociate route tables before deletion")

        # Mark route table as deleting then deleted and remove from state
        route_table.state = ResourceState.DELETING if hasattr(ResourceState, "DELETING") else "deleting"
        # Remove from state
        del route_tables[transit_gateway_route_table_id]
        route_table.state = ResourceState.DELETED if hasattr(ResourceState, "DELETED") else "deleted"

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayRouteTable": route_table.to_dict(),
        }


    def delete_transit_gateway_route_table_announcement(self, params: dict) -> dict:
        transit_gateway_route_table_announcement_id = params.get("TransitGatewayRouteTableAnnouncementId")
        if not transit_gateway_route_table_announcement_id:
            raise ValueError("TransitGatewayRouteTableAnnouncementId is required")

        announcements = getattr(self.state, "transit_gateway_route_table_announcements", {})
        if announcements is None:
            announcements = {}

        announcement = announcements.get(transit_gateway_route_table_announcement_id)
        if not announcement:
            # Return empty announcement with state deleted
            announcement = TransitGatewayRouteTableAnnouncement()
            announcement.transit_gateway_route_table_announcement_id = transit_gateway_route_table_announcement_id
            announcement.state = TransitGatewayRouteTableAnnouncementState.DELETED if hasattr(TransitGatewayRouteTableAnnouncementState, "DELETED") else "deleted"
            announcement.announcement_direction = None
            announcement.core_network_id = None
            announcement.creation_time = None
            announcement.peer_core_network_id = None
            announcement.peering_attachment_id = None
            announcement.peer_transit_gateway_id = None
            announcement.tag_set = []
            announcement.transit_gateway_id = None
            announcement.transit_gateway_route_table_id = None
            return {
                "requestId": self.generate_request_id(),
                "transitGatewayRouteTableAnnouncement": announcement.to_dict(),
            }

        # Mark as deleting then deleted and remove from state
        announcement.state = TransitGatewayRouteTableAnnouncementState.DELETING if hasattr(TransitGatewayRouteTableAnnouncementState, "DELETING") else "deleting"
        del announcements[transit_gateway_route_table_announcement_id]
        announcement.state = TransitGatewayRouteTableAnnouncementState.DELETED if hasattr(TransitGatewayRouteTableAnnouncementState, "DELETED") else "deleted"

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayRouteTableAnnouncement": announcement.to_dict(),
        }


    def describe_transit_gateway_route_table_announcements(self, params: dict) -> dict:
        filters = []
        # Filters can be passed as Filter.N.Name and Filter.N.Values
        # We need to parse filters from params keys
        # Also support TransitGatewayRouteTableAnnouncementIds.N

        # Parse filters
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                # Format: Filter.N.Name or Filter.N.Values.M
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    if filter_index not in filter_dict:
                        filter_dict[filter_index] = {"Name": None, "Values": []}
                    if filter_key == "Name":
                        filter_dict[filter_index]["Name"] = value
                    elif filter_key.startswith("Values"):
                        filter_dict[filter_index]["Values"].append(value)
        filters = list(filter_dict.values())

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise ValueError("MaxResults must be between 5 and 1000")
            except Exception:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        next_token = params.get("NextToken")

        announcement_ids = []
        for key, value in params.items():
            if key.startswith("TransitGatewayRouteTableAnnouncementIds."):
                announcement_ids.append(value)

        announcements = getattr(self.state, "transit_gateway_route_table_announcements", {})
        if announcements is None:
            announcements = {}

        # Filter announcements by IDs if provided
        filtered_announcements = []
        if announcement_ids:
            for aid in announcement_ids:
                ann = announcements.get(aid)
                if ann:
                    filtered_announcements.append(ann)
        else:
            filtered_announcements = list(announcements.values())

        # Apply filters
        def matches_filter(announcement, filter):
            name = filter.get("Name")
            values = filter.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to announcement attributes
            # Support filtering by announcementDirection, coreNetworkId, state, transitGatewayId, transitGatewayRouteTableId, etc.
            attr_map = {
                "announcement-direction": "announcement_direction",
                "core-network-id": "core_network_id",
                "state": "state",
                "transit-gateway-id": "transit_gateway_id",
                "transit-gateway-route-table-id": "transit_gateway_route_table_id",
                "transit-gateway-route-table-announcement-id": "transit_gateway_route_table_announcement_id",
                "peering-attachment-id": "peering_attachment_id",
                "peer-core-network-id": "peer_core_network_id",
                "peer-transit-gateway-id": "peer_transit_gateway_id",
            }
            attr = attr_map.get(name.lower())
            if not attr:
                return True
            val = getattr(announcement, attr, None)
            if val is None:
                return False
            # For state and announcement_direction, val may be enum, convert to string
            if hasattr(val, "value"):
                val = val.value
            return any(str(val) == str(v) for v in values)

        filtered_announcements = [
            ann for ann in filtered_announcements if all(matches_filter(ann, f) for f in filters)
        ]

        # Pagination support
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else len(filtered_announcements)
        page_announcements = filtered_announcements[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(filtered_announcements) else None

        return {
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
            "transitGatewayRouteTableAnnouncements": [ann.to_dict() for ann in page_announcements],
        }

    def describe_transit_gateway_route_tables(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        route_table_ids = params.get("TransitGatewayRouteTableIds", [])

        # Validate MaxResults if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # DryRun check placeholder (not implemented here)
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        # Collect all route tables
        all_route_tables = list(self.state.transit_gateway_route_tables.values())

        # Filter by TransitGatewayRouteTableIds if provided
        if route_table_ids:
            all_route_tables = [
                rt for rt in all_route_tables if rt.transit_gateway_route_table_id in route_table_ids
            ]

        # Apply filters
        def match_filter(route_table, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # No filter or empty values means no filtering on this filter

            # Map filter names to attributes
            if name == "default-association-route-table":
                # Values are strings "true" or "false"
                return str(route_table.default_association_route_table).lower() in [v.lower() for v in values]
            elif name == "default-propagation-route-table":
                return str(route_table.default_propagation_route_table).lower() in [v.lower() for v in values]
            elif name == "state":
                # route_table.state is an Enum, compare its value string
                return route_table.state.value in values
            elif name == "transit-gateway-id":
                return route_table.transit_gateway_id in values
            elif name == "transit-gateway-route-table-id":
                return route_table.transit_gateway_route_table_id in values
            else:
                # Unknown filter name, ignore filter
                return True

        if filters:
            filtered_route_tables = []
            for rt in all_route_tables:
                # For each filter, if any filter does not match, exclude
                if all(match_filter(rt, f) for f in filters):
                    filtered_route_tables.append(rt)
            all_route_tables = filtered_route_tables

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_route_tables)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_route_tables))

        page_route_tables = all_route_tables[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(all_route_tables):
            new_next_token = str(end_index)

        # Prepare response
        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayRouteTables": [rt.to_dict() for rt in page_route_tables],
            "nextToken": new_next_token,
        }
        return response


    def disable_transit_gateway_route_table_propagation(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        attachment_id = params.get("TransitGatewayAttachmentId")
        announcement_id = params.get("TransitGatewayRouteTableAnnouncementId")
        route_table_id = params.get("TransitGatewayRouteTableId")

        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # DryRun check placeholder
        if dry_run:
            pass

        # Find the propagation to disable
        propagation_to_disable = None
        for propagation in self.state.transit_gateway_route_table_propagations.values():
            if propagation.transit_gateway_route_table_id != route_table_id:
                continue
            if attachment_id and propagation.transit_gateway_attachment_id != attachment_id:
                continue
            if announcement_id and propagation.transit_gateway_route_table_announcement_id != announcement_id:
                continue
            propagation_to_disable = propagation
            break

        if not propagation_to_disable:
            # If no matching propagation found, create a new one with disabled state?
            # But AWS likely returns error, here we just create a disabled propagation for the given ids
            propagation_to_disable = TransitGatewayPropagation(
                resource_id=None,
                resource_type=None,
                state=TransitGatewayPropagationState.DISABLED,
                transit_gateway_attachment_id=attachment_id,
                transit_gateway_route_table_announcement_id=announcement_id,
                transit_gateway_route_table_id=route_table_id,
            )
            # Generate a unique id for resource_id if needed
            propagation_to_disable.resource_id = self.generate_unique_id()
            self.state.transit_gateway_route_table_propagations[propagation_to_disable.resource_id] = propagation_to_disable
        else:
            # Update state to disabled
            propagation_to_disable.state = TransitGatewayPropagationState.DISABLED

        response = {
            "requestId": self.generate_request_id(),
            "propagation": propagation_to_disable.to_dict(),
        }
        return response


    def disassociate_transit_gateway_route_table(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        attachment_id = params.get("TransitGatewayAttachmentId")
        route_table_id = params.get("TransitGatewayRouteTableId")

        if not attachment_id:
            raise ValueError("TransitGatewayAttachmentId is required")
        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # DryRun check placeholder
        if dry_run:
            pass

        # Find the association to disassociate
        association_to_remove = None
        for association in self.state.transit_gateway_route_table_associations.values():
            if association.transit_gateway_attachment_id == attachment_id and association.transit_gateway_route_table_id == route_table_id:
                association_to_remove = association
                break

        if not association_to_remove:
            # AWS would return an error if association not found, here raise
            raise ValueError("Association not found for given TransitGatewayAttachmentId and TransitGatewayRouteTableId")

        # Update state to disassociating then disassociated
        association_to_remove.state = TransitGatewayAssociationState.DISASSOCIATING
        # Simulate immediate disassociation
        association_to_remove.state = TransitGatewayAssociationState.DISASSOCIATED

        response = {
            "requestId": self.generate_request_id(),
            "association": association_to_remove.to_dict(),
        }
        return response


    def enable_transit_gateway_route_table_propagation(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        attachment_id = params.get("TransitGatewayAttachmentId")
        announcement_id = params.get("TransitGatewayRouteTableAnnouncementId")
        route_table_id = params.get("TransitGatewayRouteTableId")

        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # DryRun check placeholder
        if dry_run:
            pass

        # Find existing propagation or create new
        propagation = None
        for p in self.state.transit_gateway_route_table_propagations.values():
            if p.transit_gateway_route_table_id == route_table_id:
                if attachment_id and p.transit_gateway_attachment_id != attachment_id:
                    continue
                if announcement_id and p.transit_gateway_route_table_announcement_id != announcement_id:
                    continue
                propagation = p
                break

        if not propagation:
            propagation = TransitGatewayPropagation(
                resource_id=self.generate_unique_id(),
                resource_type=None,
                state=TransitGatewayPropagationState.ENABLED,
                transit_gateway_attachment_id=attachment_id,
                transit_gateway_route_table_announcement_id=announcement_id,
                transit_gateway_route_table_id=route_table_id,
            )
            self.state.transit_gateway_route_table_propagations[propagation.resource_id] = propagation
        else:
            propagation.state = TransitGatewayPropagationState.ENABLED

        response = {
            "requestId": self.generate_request_id(),
            "propagation": propagation.to_dict(),
        }
        return response


    def export_transit_gateway_routes(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        s3_bucket = params.get("S3Bucket")
        route_table_id = params.get("TransitGatewayRouteTableId")

        if not s3_bucket:
            raise ValueError("S3Bucket is required")
        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # DryRun check placeholder
        if dry_run:
            pass

        # Find the route table
        route_table = self.state.transit_gateway_route_tables.get(route_table_id)
        if not route_table:
            raise ValueError("TransitGatewayRouteTableId not found")

        # Collect routes for the route table
        routes = []
        for route in self.state.transit_gateway_routes.values():
            if route.transit_gateway_route_table_id != route_table_id:
                continue

            # Apply filters
            def route_matches_filter(route, filter_obj):
                name = filter_obj.get("Name")
                values = filter_obj.get("Values", [])
                if not name or not values:
                    return True

                if name == "attachment.transit-gateway-attachment-id":
                    for att in route.transit_gateway_attachments:
                        if att.transit_gateway_attachment_id in values:
                            return True
                    return False
                elif name == "attachment.resource-id":
                    for att in route.transit_gateway_attachments:
                        if att.resource_id in values:
                            return True
                    return False
                elif name == "route-search.exact-match":
                    # Check if destination_cidr_block or prefix_list_id exactly matches any value
                    if route.destination_cidr_block in values:
                        return True
                    if route.prefix_list_id in values:
                        return True
                    return False
                elif name == "route-search.longest-prefix-match":
                    # For simplicity, treat as exact match (real implementation would do prefix matching)
                    if route.destination_cidr_block in values:
                        return True
                    return False
                elif name == "route-search.subnet-of-match":
                    # Not implemented subnet matching, treat as exact match
                    if route.destination_cidr_block in values:
                        return True
                    return False
                elif name == "route-search.supernet-of-match":
                    # Not implemented supernet matching, treat as exact match
                    if route.destination_cidr_block in values:
                        return True
                    return False
                elif name == "state":
                    if route.state and route.state.value in values:
                        return True
                    return False
                elif name == "transit-gateway-route-destination-cidr-block":
                    if route.destination_cidr_block in values:
                        return True
                    return False
                elif name == "type":
                    if route.type and route.type.value in values:
                        return True
                    return False
                else:
                    return True

            if all(route_matches_filter(route, f) for f in filters):
                routes.append(route)

        # Simulate export to S3 by generating a URL string
        s3_location = f"s3://{s3_bucket}/VPCTransitGateway/TransitGatewayRouteTables/{route_table_id}_export.json"

        response = {
            "requestId": self.generate_request_id(),
            "s3Location": s3_location,
        }
        return response

    def get_transit_gateway_attachment_propagations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            raise ValueError("TransitGatewayAttachmentId is required")

        # Filters
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Collect all propagations for the given attachment id
        all_propagations = []
        for propagation in self.state.transit_gateway_route_table_propagations.values():
            if propagation.transit_gateway_attachment_id == attachment_id:
                all_propagations.append(propagation)

        # Apply filters if any
        def matches_filters(propagation):
            if not filters:
                return True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name == "transit-gateway-route-table-id":
                    if propagation.transit_gateway_route_table_id not in values:
                        return False
                else:
                    # Unknown filter name, ignore or exclude
                    return False
            return True

        filtered_propagations = [p for p in all_propagations if matches_filters(p)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(filtered_propagations)
        if max_results:
            end_index = min(start_index + max_results, len(filtered_propagations))

        page_propagations = filtered_propagations[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(filtered_propagations):
            new_next_token = str(end_index)

        # Prepare response list
        response_propagations = []
        for p in page_propagations:
            response_propagations.append(p.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
            "transitGatewayAttachmentPropagations": response_propagations,
        }


    def get_transit_gateway_prefix_list_references(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Collect all prefix list references for the given route table id
        all_references = []
        for ref in self.state.transit_gateway_prefix_list_references.values():
            if ref.transit_gateway_route_table_id == route_table_id:
                all_references.append(ref)

        # Apply filters
        def matches_filters(ref):
            if not filters:
                return True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name == "attachment.resource-id":
                    if not ref.transit_gateway_attachment or ref.transit_gateway_attachment.resource_id not in values:
                        return False
                elif name == "attachment.resource-type":
                    if not ref.transit_gateway_attachment or ref.transit_gateway_attachment.resource_type is None:
                        return False
                    if ref.transit_gateway_attachment.resource_type.value not in values:
                        return False
                elif name == "attachment.transit-gateway-attachment-id":
                    if not ref.transit_gateway_attachment or ref.transit_gateway_attachment.transit_gateway_attachment_id not in values:
                        return False
                elif name == "is-blackhole":
                    # values are strings "true" or "false"
                    val = values[0].lower() if values else None
                    if val == "true" and not ref.blackhole:
                        return False
                    if val == "false" and ref.blackhole:
                        return False
                elif name == "prefix-list-id":
                    if ref.prefix_list_id not in values:
                        return False
                elif name == "prefix-list-owner-id":
                    if ref.prefix_list_owner_id not in values:
                        return False
                elif name == "state":
                    if ref.state is None or ref.state.value not in values:
                        return False
                else:
                    # Unknown filter, exclude
                    return False
            return True

        filtered_refs = [r for r in all_references if matches_filters(r)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(filtered_refs)
        if max_results:
            end_index = min(start_index + max_results, len(filtered_refs))

        page_refs = filtered_refs[start_index:end_index]

        new_next_token = None
        if end_index < len(filtered_refs):
            new_next_token = str(end_index)

        response_refs = []
        for ref in page_refs:
            response_refs.append(ref.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
            "transitGatewayPrefixListReferenceSet": response_refs,
        }


    def get_transit_gateway_route_table_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Collect all associations for the given route table id
        all_associations = []
        for assoc in self.state.transit_gateway_route_table_associations.values():
            # The association object has no transit_gateway_route_table_id attribute in the given structure,
            # but logically it should be linked to a route table.
            # We must check if the association's transit_gateway_route_table_id matches the requested one.
            # The class TransitGatewayRouteTableAssociation does not have transit_gateway_route_table_id attribute in the given structure,
            # but the API requires filtering by route table id.
            # We assume the association object has attribute transit_gateway_route_table_id (or we can get it from attachment).
            # Since the class definition does not show it, we try to get it from the attachment or from the state transit_gateway_route_tables.
            # We'll check if the association's transit_gateway_attachment_id is attached to the route table.

            # We try to get the route table id from the association's transit_gateway_attachment_id:
            attachment_id = assoc.transit_gateway_attachment_id
            if not attachment_id:
                continue
            # Check if this attachment is associated with the route table id
            # We check if the route table has this attachment associated
            # The state transit_gateway_route_tables is a dict of route table id -> TransitGatewayRouteTable
            # But the route table object does not have direct list of associations, so we rely on the association object itself.
            # We assume the association object is linked to the route table id by the API call parameter.
            # So we filter only associations whose attachment is associated with the route table id.
            # We check if the association is for the requested route table id by checking if the association is in the state and matches route_table_id.
            # Since the association object does not have route_table_id attribute, we filter by the API parameter only.
            # So we filter associations by the API parameter route_table_id by checking if the association is in the state and the route_table_id matches.
            # We assume the association is for the route table id if the association is in the state and the route_table_id matches the API parameter.
            # So we filter associations by the API parameter route_table_id.
            # We check if the association is linked to the route table id by checking if the association is in the state and the route_table_id matches.
            # We assume the association object has attribute transit_gateway_route_table_id (not shown in class but logically needed).
            # We check if the association has attribute transit_gateway_route_table_id and if it matches route_table_id.
            if hasattr(assoc, "transit_gateway_route_table_id"):
                if assoc.transit_gateway_route_table_id != route_table_id:
                    continue
            else:
                # If attribute missing, skip association
                continue

            all_associations.append(assoc)

        # Apply filters
        def matches_filters(assoc):
            if not filters:
                return True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name == "resource-id":
                    if assoc.resource_id not in values:
                        return False
                elif name == "resource-type":
                    if assoc.resource_type is None or assoc.resource_type.value not in values:
                        return False
                elif name == "transit-gateway-attachment-id":
                    if assoc.transit_gateway_attachment_id not in values:
                        return False
                else:
                    return False
            return True

        filtered_associations = [a for a in all_associations if matches_filters(a)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(filtered_associations)
        if max_results:
            end_index = min(start_index + max_results, len(filtered_associations))

        page_associations = filtered_associations[start_index:end_index]

        new_next_token = None
        if end_index < len(filtered_associations):
            new_next_token = str(end_index)

        response_associations = []
        for assoc in page_associations:
            response_associations.append(assoc.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
            "associations": response_associations,
        }


    def get_transit_gateway_route_table_propagations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Collect all route table propagations for the given route table id
        all_propagations = []
        for propagation in self.state.transit_gateway_route_table_propagations.values():
            if propagation.transit_gateway_route_table_id == route_table_id:
                all_propagations.append(propagation)

        # Apply filters
        def matches_filters(propagation):
            if not filters:
                return True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name == "resource-id":
                    if propagation.resource_id not in values:
                        return False
                elif name == "resource-type":
                    if propagation.resource_type is None or propagation.resource_type.value not in values:
                        return False
                elif name == "transit-gateway-attachment-id":
                    if propagation.transit_gateway_attachment_id not in values:
                        return False
                else:
                    return False
            return True

        filtered_propagations = [p for p in all_propagations if matches_filters(p)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(filtered_propagations)
        if max_results:
            end_index = min(start_index + max_results, len(filtered_propagations))

        page_propagations = filtered_propagations[start_index:end_index]

        new_next_token = None
        if end_index < len(filtered_propagations):
            new_next_token = str(end_index)

        response_propagations = []
        for p in page_propagations:
            response_propagations.append(p.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
            "transitGatewayRouteTablePropagations": response_propagations,
        }


    def modify_transit_gateway_prefix_list_reference(self, params: Dict[str, Any]) -> Dict[str, Any]:
        prefix_list_id = params.get("PrefixListId")
        route_table_id = params.get("TransitGatewayRouteTableId")
        if not prefix_list_id:
            raise ValueError("PrefixListId is required")
        if not route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        blackhole = params.get("Blackhole")
        attachment_id = params.get("TransitGatewayAttachmentId")

        # Find the prefix list reference to modify
        # The key for prefix list references is not specified, so we search by prefix_list_id and route_table_id
        found_ref = None
        for ref in self.state.transit_gateway_prefix_list_references.values():
            if ref.prefix_list_id == prefix_list_id and ref.transit_gateway_route_table_id == route_table_id:
                found_ref = ref
                break

        if not found_ref:
            raise ValueError("TransitGatewayPrefixListReference not found for given PrefixListId and TransitGatewayRouteTableId")

        # Modify blackhole if provided
        if blackhole is not None:
            found_ref.blackhole = bool(blackhole)

        # Modify attachment if provided
        if attachment_id is not None:
            # Find the attachment object by attachment_id
            attachment_obj = None
            for att in self.state.transit_gateway_attachments.values():
                if att.transit_gateway_attachment_id == attachment_id:
                    attachment_obj = att
                    break
            # If attachment not found, create a new TransitGatewayPrefixListAttachment with minimal info
            if attachment_obj is None:
                # We create a new TransitGatewayPrefixListAttachment with only the id set
                from typing import Optional
                attachment_obj = TransitGatewayPrefixListAttachment(
                    resource_id=None,
                    resource_type=None,
                    transit_gateway_attachment_id=attachment_id,
                )
            # Assign the attachment object to the prefix list reference
            found_ref.transit_gateway_attachment = attachment_obj

        # Set state to modifying
        from enum import Enum
        if hasattr(found_ref.state, "__class__") and hasattr(found_ref.state.__class__, "_member_map_"):
            # If state is an Enum, set to modifying member if exists
            if "MODIFYING" in found_ref.state.__class__._member_map_:
                found_ref.state = found_ref.state.__class__.MODIFYING
            else:
                # fallback to string "modifying"
                found_ref.state = "modifying"
        else:
            found_ref.state = "modifying"

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayPrefixListReference": found_ref.to_dict(),
        }

    def replace_transit_gateway_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from ipaddress import ip_network, IPv4Network, IPv6Network
        # Validate required parameters
        destination_cidr_block = params.get("DestinationCidrBlock")
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        if not destination_cidr_block:
            raise ValueError("DestinationCidrBlock is required")
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")

        # Validate CIDR block format
        try:
            dest_network = ip_network(destination_cidr_block)
        except Exception:
            raise ValueError(f"Invalid DestinationCidrBlock: {destination_cidr_block}")

        # DryRun check
        if params.get("DryRun"):
            # In real AWS, this would check permissions and raise error if unauthorized
            # Here we simulate success for DryRun
            return {"requestId": self.generate_request_id()}

        # Find the route table
        route_table = self.state.transit_gateway_route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            raise ValueError(f"TransitGatewayRouteTableId {transit_gateway_route_table_id} not found")

        # Find existing route by destination CIDR block or prefix list id (prefix list id not supported here)
        existing_route = None
        for route in getattr(route_table, "routes", []):
            if route.destination_cidr_block == destination_cidr_block:
                existing_route = route
                break

        # If no routes attribute, initialize it
        if not hasattr(route_table, "routes"):
            route_table.routes = []

        # Determine new route state
        blackhole = params.get("Blackhole", False)
        if blackhole:
            route_state = TransitGatewayRouteState.BLACKHOLE
        else:
            route_state = TransitGatewayRouteState.ACTIVE

        # Build transit gateway attachments list if TransitGatewayAttachmentId provided
        transit_gateway_attachments = []
        attachment_id = params.get("TransitGatewayAttachmentId")
        if attachment_id:
            # Try to get the attachment resource
            attachment = self.state.get_resource(attachment_id)
            if not attachment:
                raise ValueError(f"TransitGatewayAttachmentId {attachment_id} not found")
            # Compose TransitGatewayRouteAttachment object
            route_attachment = TransitGatewayRouteAttachment(
                resource_id=getattr(attachment, "resource_id", None),
                resource_type=getattr(attachment, "resource_type", None),
                transit_gateway_attachment_id=attachment_id,
            )
            transit_gateway_attachments.append(route_attachment)

        # Compose the new route object
        new_route = TransitGatewayRoute(
            destination_cidr_block=destination_cidr_block,
            prefix_list_id=None,
            state=route_state,
            transit_gateway_attachments=transit_gateway_attachments,
            transit_gateway_route_table_announcement_id=None,
            type=TransitGatewayRouteType.STATIC,
        )

        # Replace or add the route in the route table
        if existing_route:
            # Replace existing route
            idx = route_table.routes.index(existing_route)
            route_table.routes[idx] = new_route
        else:
            # Add new route
            route_table.routes.append(new_route)

        # Save route table back to state (already a reference, but follow pattern)
        self.state.transit_gateway_route_tables[transit_gateway_route_table_id] = route_table

        return {
            "requestId": self.generate_request_id(),
            "route": new_route.to_dict(),
        }


    def search_transit_gateway_routes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from ipaddress import ip_network, ip_address

        # Validate required parameters
        transit_gateway_route_table_id = params.get("TransitGatewayRouteTableId")
        filters = params.get("Filter.N")
        max_results = params.get("MaxResults", 1000)
        if not transit_gateway_route_table_id:
            raise ValueError("TransitGatewayRouteTableId is required")
        if filters is None:
            raise ValueError("Filter.N is required")
        if not isinstance(filters, list):
            raise ValueError("Filter.N must be a list")

        # Validate max_results range
        if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
            raise ValueError("MaxResults must be an integer between 5 and 1000")

        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id()}

        # Find the route table
        route_table = self.state.transit_gateway_route_tables.get(transit_gateway_route_table_id)
        if not route_table:
            raise ValueError(f"TransitGatewayRouteTableId {transit_gateway_route_table_id} not found")

        # Get routes list, default empty
        routes = getattr(route_table, "routes", [])

        # Helper to check if route matches a filter
        def route_matches_filter(route, filter_name, filter_values):
            # Normalize filter values to set of strings
            filter_values_set = set(str(v) for v in filter_values)

            if filter_name == "attachment.transit-gateway-attachment-id":
                # Check if any attachment id matches
                for att in route.transit_gateway_attachments:
                    if att.transit_gateway_attachment_id in filter_values_set:
                        return True
                return False

            elif filter_name == "attachment.resource-id":
                for att in route.transit_gateway_attachments:
                    if att.resource_id in filter_values_set:
                        return True
                return False

            elif filter_name == "attachment.resource-type":
                for att in route.transit_gateway_attachments:
                    if att.resource_type and att.resource_type.value in filter_values_set:
                        return True
                return False

            elif filter_name == "prefix-list-id":
                return route.prefix_list_id in filter_values_set

            elif filter_name == "route-search.exact-match":
                # Exact match on destination CIDR block or prefix list id
                for val in filter_values_set:
                    if route.destination_cidr_block == val or route.prefix_list_id == val:
                        return True
                return False

            elif filter_name == "route-search.longest-prefix-match":
                # Find longest prefix match of the filter value against route destination CIDR
                # The filter values are CIDRs, we check if route destination CIDR is contained in any filter CIDR
                # Actually, longest prefix match means route destination CIDR is contained in filter CIDR? 
                # AWS docs say: longest prefix that matches the route
                # So route destination CIDR must be a subnet of filter CIDR
                for val in filter_values_set:
                    try:
                        filter_net = ip_network(val)
                        route_net = ip_network(route.destination_cidr_block) if route.destination_cidr_block else None
                        if route_net and route_net.subnet_of(filter_net):
                            return True
                    except Exception:
                        continue
                return False

            elif filter_name == "route-search.subnet-of-match":
                # Routes with a subnet that match the specified CIDR filter
                # So route destination CIDR is subnet of filter CIDR
                for val in filter_values_set:
                    try:
                        filter_net = ip_network(val)
                        route_net = ip_network(route.destination_cidr_block) if route.destination_cidr_block else None
                        if route_net and route_net.subnet_of(filter_net):
                            return True
                    except Exception:
                        continue
                return False

            elif filter_name == "route-search.supernet-of-match":
                # Routes with a CIDR that encompass the CIDR filter
                # So route destination CIDR is supernet of filter CIDR
                for val in filter_values_set:
                    try:
                        filter_net = ip_network(val)
                        route_net = ip_network(route.destination_cidr_block) if route.destination_cidr_block else None
                        if route_net and filter_net.subnet_of(route_net):
                            return True
                    except Exception:
                        continue
                return False

            elif filter_name == "state":
                # State of the route (active|blackhole)
                # route.state is TransitGatewayRouteState enum, compare value
                for val in filter_values_set:
                    if route.state and route.state.value == val:
                        return True
                return False

            elif filter_name == "type":
                # Type of route (propagated|static)
                for val in filter_values_set:
                    if route.type and route.type.value == val:
                        return True
                return False

            else:
                # Unknown filter, ignore or no match
                return False

        # Filter routes by all filters (AND logic)
        filtered_routes = []
        for route in routes:
            matches_all = True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue
                if not route_matches_filter(route, name, values):
                    matches_all = False
                    break
            if matches_all:
                filtered_routes.append(route)
                if len(filtered_routes) >= max_results:
                    break

        additional_routes_available = len(routes) > len(filtered_routes)

        return {
            "requestId": self.generate_request_id(),
            "routeSet": [r.to_dict() for r in filtered_routes],
            "additionalRoutesAvailable": additional_routes_available,
        }

    

from emulator_core.gateway.base import BaseGateway

class TransitgatewayroutetablesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateTransitGatewayRouteTable", self.associate_transit_gateway_route_table)
        self.register_action("CreateTransitGatewayPrefixListReference", self.create_transit_gateway_prefix_list_reference)
        self.register_action("CreateTransitGatewayRoute", self.create_transit_gateway_route)
        self.register_action("CreateTransitGatewayRouteTable", self.create_transit_gateway_route_table)
        self.register_action("CreateTransitGatewayRouteTableAnnouncement", self.create_transit_gateway_route_table_announcement)
        self.register_action("DeleteTransitGatewayPrefixListReference", self.delete_transit_gateway_prefix_list_reference)
        self.register_action("DeleteTransitGatewayRoute", self.delete_transit_gateway_route)
        self.register_action("DeleteTransitGatewayRouteTable", self.delete_transit_gateway_route_table)
        self.register_action("DeleteTransitGatewayRouteTableAnnouncement", self.delete_transit_gateway_route_table_announcement)
        self.register_action("DescribeTransitGatewayRouteTableAnnouncements", self.describe_transit_gateway_route_table_announcements)
        self.register_action("DescribeTransitGatewayRouteTables", self.describe_transit_gateway_route_tables)
        self.register_action("DisableTransitGatewayRouteTablePropagation", self.disable_transit_gateway_route_table_propagation)
        self.register_action("DisassociateTransitGatewayRouteTable", self.disassociate_transit_gateway_route_table)
        self.register_action("EnableTransitGatewayRouteTablePropagation", self.enable_transit_gateway_route_table_propagation)
        self.register_action("ExportTransitGatewayRoutes", self.export_transit_gateway_routes)
        self.register_action("GetTransitGatewayAttachmentPropagations", self.get_transit_gateway_attachment_propagations)
        self.register_action("GetTransitGatewayPrefixListReferences", self.get_transit_gateway_prefix_list_references)
        self.register_action("GetTransitGatewayRouteTableAssociations", self.get_transit_gateway_route_table_associations)
        self.register_action("GetTransitGatewayRouteTablePropagations", self.get_transit_gateway_route_table_propagations)
        self.register_action("ModifyTransitGatewayPrefixListReference", self.modify_transit_gateway_prefix_list_reference)
        self.register_action("ReplaceTransitGatewayRoute", self.replace_transit_gateway_route)
        self.register_action("SearchTransitGatewayRoutes", self.search_transit_gateway_routes)

    def associate_transit_gateway_route_table(self, params):
        return self.backend.associate_transit_gateway_route_table(params)

    def create_transit_gateway_prefix_list_reference(self, params):
        return self.backend.create_transit_gateway_prefix_list_reference(params)

    def create_transit_gateway_route(self, params):
        return self.backend.create_transit_gateway_route(params)

    def create_transit_gateway_route_table(self, params):
        return self.backend.create_transit_gateway_route_table(params)

    def create_transit_gateway_route_table_announcement(self, params):
        return self.backend.create_transit_gateway_route_table_announcement(params)

    def delete_transit_gateway_prefix_list_reference(self, params):
        return self.backend.delete_transit_gateway_prefix_list_reference(params)

    def delete_transit_gateway_route(self, params):
        return self.backend.delete_transit_gateway_route(params)

    def delete_transit_gateway_route_table(self, params):
        return self.backend.delete_transit_gateway_route_table(params)

    def delete_transit_gateway_route_table_announcement(self, params):
        return self.backend.delete_transit_gateway_route_table_announcement(params)

    def describe_transit_gateway_route_table_announcements(self, params):
        return self.backend.describe_transit_gateway_route_table_announcements(params)

    def describe_transit_gateway_route_tables(self, params):
        return self.backend.describe_transit_gateway_route_tables(params)

    def disable_transit_gateway_route_table_propagation(self, params):
        return self.backend.disable_transit_gateway_route_table_propagation(params)

    def disassociate_transit_gateway_route_table(self, params):
        return self.backend.disassociate_transit_gateway_route_table(params)

    def enable_transit_gateway_route_table_propagation(self, params):
        return self.backend.enable_transit_gateway_route_table_propagation(params)

    def export_transit_gateway_routes(self, params):
        return self.backend.export_transit_gateway_routes(params)

    def get_transit_gateway_attachment_propagations(self, params):
        return self.backend.get_transit_gateway_attachment_propagations(params)

    def get_transit_gateway_prefix_list_references(self, params):
        return self.backend.get_transit_gateway_prefix_list_references(params)

    def get_transit_gateway_route_table_associations(self, params):
        return self.backend.get_transit_gateway_route_table_associations(params)

    def get_transit_gateway_route_table_propagations(self, params):
        return self.backend.get_transit_gateway_route_table_propagations(params)

    def modify_transit_gateway_prefix_list_reference(self, params):
        return self.backend.modify_transit_gateway_prefix_list_reference(params)

    def replace_transit_gateway_route(self, params):
        return self.backend.replace_transit_gateway_route(params)

    def search_transit_gateway_routes(self, params):
        return self.backend.search_transit_gateway_routes(params)
