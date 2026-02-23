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
class TransitGatewayRouteTable:
    creation_time: str = ""
    default_association_route_table: bool = False
    default_propagation_route_table: bool = False
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    transit_gateway_id: str = ""
    transit_gateway_route_table_id: str = ""

    associations: List[Dict[str, Any]] = field(default_factory=list)
    propagations: List[Dict[str, Any]] = field(default_factory=list)
    routes: List[Dict[str, Any]] = field(default_factory=list)
    prefix_list_references: List[Dict[str, Any]] = field(default_factory=list)
    route_table_announcements: List[Dict[str, Any]] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTime": self.creation_time,
            "defaultAssociationRouteTable": self.default_association_route_table,
            "defaultPropagationRouteTable": self.default_propagation_route_table,
            "state": self.state,
            "tagSet": self.tag_set,
            "transitGatewayId": self.transit_gateway_id,
            "transitGatewayRouteTableId": self.transit_gateway_route_table_id,
            "associations": self.associations,
            "propagations": self.propagations,
            "routes": self.routes,
            "prefixListReferences": self.prefix_list_references,
            "routeTableAnnouncements": self.route_table_announcements,
        }

class TransitGatewayRouteTable_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.transit_gateway_route_tables  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.transit_gateways.get(params['transit_gateway_id']).transit_gateway_route_table_ids.append(new_id)
    #   Delete: self.state.transit_gateways.get(resource.transit_gateway_id).transit_gateway_route_table_ids.remove(resource_id)

    def _get_route_table_or_error(self, route_table_id: str):
        resource = self.resources.get(route_table_id)
        if not resource:
            return None, create_error_response(
                "InvalidTransitGatewayRouteTableID.NotFound",
                f"The ID '{route_table_id}' does not exist",
            )
        return resource, None

    def _get_route_or_error(self, route_table: TransitGatewayRouteTable, destination_cidr_block: str):
        route = self._find_route(route_table, destination_cidr_block)
        if not route:
            return None, create_error_response(
                "InvalidRoute.NotFound",
                f"Route '{destination_cidr_block}' does not exist",
            )
        return route, None

    def _get_prefix_list_reference_or_error(self, route_table: TransitGatewayRouteTable, prefix_list_id: str):
        reference = self._find_prefix_list_reference(route_table, prefix_list_id)
        if not reference:
            return None, create_error_response(
                "InvalidPrefixListID.NotFound",
                f"The ID '{prefix_list_id}' does not exist",
            )
        return reference, None

    def _get_announcement_or_error(self, announcement_id: str):
        route_table, announcement = self._find_announcement(announcement_id)
        if not announcement:
            return None, None, create_error_response(
                "InvalidTransitGatewayRouteTableAnnouncementID.NotFound",
                f"The ID '{announcement_id}' does not exist",
            )
        return route_table, announcement, None

    def _find_association(self, route_table: TransitGatewayRouteTable, attachment_id: str) -> Optional[Dict[str, Any]]:
        for association in route_table.associations:
            if association.get("transitGatewayAttachmentId") == attachment_id:
                return association
        return None

    def _find_propagation(self, route_table: TransitGatewayRouteTable, attachment_id: str) -> Optional[Dict[str, Any]]:
        for propagation in route_table.propagations:
            if propagation.get("transitGatewayAttachmentId") == attachment_id:
                return propagation
        return None

    def _find_route(self, route_table: TransitGatewayRouteTable, destination_cidr_block: str) -> Optional[Dict[str, Any]]:
        for route in route_table.routes:
            if route.get("destinationCidrBlock") == destination_cidr_block:
                return route
        return None

    def _find_prefix_list_reference(self, route_table: TransitGatewayRouteTable, prefix_list_id: str) -> Optional[Dict[str, Any]]:
        for reference in route_table.prefix_list_references:
            if reference.get("prefixListId") == prefix_list_id:
                return reference
        return None

    def _find_announcement(self, announcement_id: str):
        for route_table in self.resources.values():
            for announcement in route_table.route_table_announcements:
                if announcement.get("transitGatewayRouteTableAnnouncementId") == announcement_id:
                    return route_table, announcement
        return None, None

    def _extract_tags(self, tag_specifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for specification in tag_specifications or []:
            for tag in specification.get("Tags", []) or []:
                if tag.get("Key"):
                    tags.append({"Key": tag.get("Key"), "Value": tag.get("Value")})
        return tags

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()



    def AssociateTransitGatewayRouteTable(self, params: Dict[str, Any]):
        """Associates the specified attachment with the specified transit gateway route table. You can 
        associate only one route table with an attachment."""

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        attachment = self.state.transit_gateway_connect.get(attachment_id)
        if not attachment:
            attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if not attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )

        for other_table in self.resources.values():
            if other_table is route_table:
                continue
            existing = self._find_association(other_table, attachment_id)
            if existing:
                existing.update({
                    "resourceId": attachment_id,
                    "resourceType": existing.get("resourceType") or "transit-gateway-attachment",
                    "state": "disassociated",
                    "transitGatewayAttachmentId": attachment_id,
                    "transitGatewayRouteTableId": other_table.transit_gateway_route_table_id,
                })

        association = self._find_association(route_table, attachment_id)
        payload = {
            "resourceId": attachment_id,
            "resourceType": "transit-gateway-attachment",
            "state": "associated",
            "transitGatewayAttachmentId": attachment_id,
            "transitGatewayRouteTableId": route_table_id,
        }
        if not association:
            association = payload
            route_table.associations.append(association)
        else:
            association.update(payload)

        return {
            'association': association,
            }

    def CreateTransitGatewayPrefixListReference(self, params: Dict[str, Any]):
        """Creates a reference (route) to a prefix list in a specified transit gateway route table."""

        prefix_list_id = params.get("PrefixListId")
        if not prefix_list_id:
            return create_error_response("MissingParameter", "Missing required parameter: PrefixListId")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        prefix_list = self.state.managed_prefix_lists.get(prefix_list_id)
        if not prefix_list:
            return create_error_response(
                "InvalidPrefixListID.NotFound",
                f"The ID '{prefix_list_id}' does not exist",
            )

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment = None
        if attachment_id:
            attachment = self.state.transit_gateway_connect.get(attachment_id)
            if not attachment:
                attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
            if not attachment:
                return create_error_response(
                    "InvalidTransitGatewayAttachmentID.NotFound",
                    f"The ID '{attachment_id}' does not exist",
                )

        prefix_list_owner_id = ""
        if isinstance(prefix_list, dict):
            prefix_list_owner_id = prefix_list.get("ownerId") or prefix_list.get("owner_id") or ""
        else:
            prefix_list_owner_id = getattr(prefix_list, "owner_id", "")

        blackhole = bool(params.get("Blackhole"))
        attachment_data = None
        if attachment_id and not blackhole:
            attachment_data = {
                "resourceId": attachment_id,
                "resourceType": "transit-gateway-attachment",
                "transitGatewayAttachmentId": attachment_id,
            }

        reference = self._find_prefix_list_reference(route_table, prefix_list_id)
        reference_payload = {
            "blackhole": blackhole,
            "prefixListId": prefix_list_id,
            "prefixListOwnerId": prefix_list_owner_id,
            "state": "blackhole" if blackhole else "active",
            "transitGatewayAttachment": attachment_data,
            "transitGatewayRouteTableId": route_table_id,
        }
        if not reference:
            reference = reference_payload
            route_table.prefix_list_references.append(reference)
        else:
            reference.update(reference_payload)

        return {
            'transitGatewayPrefixListReference': reference,
            }

    def CreateTransitGatewayRoute(self, params: Dict[str, Any]):
        """Creates a static route for the specified transit gateway route table."""

        destination_cidr_block = params.get("DestinationCidrBlock")
        if not destination_cidr_block:
            return create_error_response("MissingParameter", "Missing required parameter: DestinationCidrBlock")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment = None
        if attachment_id:
            attachment = self.state.transit_gateway_connect.get(attachment_id)
            if not attachment:
                attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
            if not attachment:
                return create_error_response(
                    "InvalidTransitGatewayAttachmentID.NotFound",
                    f"The ID '{attachment_id}' does not exist",
                )

        blackhole = bool(params.get("Blackhole"))
        attachment_entries: List[Dict[str, Any]] = []
        if attachment_id and not blackhole:
            attachment_entries.append({
                "resourceId": attachment_id,
                "resourceType": "transit-gateway-attachment",
                "transitGatewayAttachmentId": attachment_id,
            })

        route = self._find_route(route_table, destination_cidr_block)
        route_payload = {
            "destinationCidrBlock": destination_cidr_block,
            "prefixListId": None,
            "state": "blackhole" if blackhole else "active",
            "transitGatewayAttachments": attachment_entries,
            "transitGatewayRouteTableAnnouncementId": None,
            "type": "static",
        }
        if not route:
            route = route_payload
            route_table.routes.append(route)
        else:
            route.update(route_payload)

        return {
            'route': route,
            }

    def CreateTransitGatewayRouteTable(self, params: Dict[str, Any]):
        """Creates a route table for the specified transit gateway."""

        transit_gateway_id = params.get("TransitGatewayId")
        if not transit_gateway_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayId")

        parent = self.state.transit_gateways.get(transit_gateway_id)
        if not parent:
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"The ID '{transit_gateway_id}' does not exist",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecifications.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "transit-gateway-route-table":
                continue
            for tag in spec.get("Tags") or spec.get("Tag") or []:
                if tag:
                    tag_set.append(tag)

        route_table_id = self._generate_id("tgw-rtb")
        resource = TransitGatewayRouteTable(
            creation_time=self._now(),
            default_association_route_table=False,
            default_propagation_route_table=False,
            state="available",
            tag_set=tag_set,
            transit_gateway_id=transit_gateway_id,
            transit_gateway_route_table_id=route_table_id,
        )
        self.resources[route_table_id] = resource

        if hasattr(parent, "transit_gateway_route_table_ids"):
            parent.transit_gateway_route_table_ids.append(route_table_id)

        return {
            'transitGatewayRouteTable': resource.to_dict(),
            }

    def CreateTransitGatewayRouteTableAnnouncement(self, params: Dict[str, Any]):
        """Advertises a new transit gateway route table."""

        peering_attachment_id = params.get("PeeringAttachmentId")
        if not peering_attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: PeeringAttachmentId")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        peering_attachment = self.state.transit_gateway_peering_attachments.get(peering_attachment_id)
        if not peering_attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{peering_attachment_id}' does not exist",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "transit-gateway-route-table-announcement":
                continue
            for tag in spec.get("Tags") or spec.get("Tag") or []:
                if tag:
                    tag_set.append(tag)

        peer_transit_gateway_id = None
        accepter_info = getattr(peering_attachment, "accepter_tgw_info", {}) if not isinstance(peering_attachment, dict) else peering_attachment.get("accepterTgwInfo", {})
        requester_info = getattr(peering_attachment, "requester_tgw_info", {}) if not isinstance(peering_attachment, dict) else peering_attachment.get("requesterTgwInfo", {})
        if route_table.transit_gateway_id and accepter_info and accepter_info.get("transitGatewayId") == route_table.transit_gateway_id:
            peer_transit_gateway_id = requester_info.get("transitGatewayId")
        elif requester_info and requester_info.get("transitGatewayId") == route_table.transit_gateway_id:
            peer_transit_gateway_id = accepter_info.get("transitGatewayId")
        else:
            peer_transit_gateway_id = requester_info.get("transitGatewayId") or accepter_info.get("transitGatewayId")

        announcement_id = self._generate_id("tgw-rtb-announce")
        announcement = {
            "announcementDirection": "outgoing",
            "coreNetworkId": None,
            "creationTime": self._now(),
            "peerCoreNetworkId": None,
            "peeringAttachmentId": peering_attachment_id,
            "peerTransitGatewayId": peer_transit_gateway_id,
            "state": "available",
            "tagSet": tag_set,
            "transitGatewayId": route_table.transit_gateway_id,
            "transitGatewayRouteTableAnnouncementId": announcement_id,
            "transitGatewayRouteTableId": route_table_id,
        }
        route_table.route_table_announcements.append(announcement)

        return {
            'transitGatewayRouteTableAnnouncement': announcement,
            }

    def DeleteTransitGatewayPrefixListReference(self, params: Dict[str, Any]):
        """Deletes a reference (route) to a prefix list in a specified transit gateway route table."""

        prefix_list_id = params.get("PrefixListId")
        if not prefix_list_id:
            return create_error_response("MissingParameter", "Missing required parameter: PrefixListId")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        reference, error = self._get_prefix_list_reference_or_error(route_table, prefix_list_id)
        if error:
            return error

        route_table.prefix_list_references = [
            item for item in route_table.prefix_list_references if item is not reference
        ]

        return {
            'transitGatewayPrefixListReference': reference,
            }

    def DeleteTransitGatewayRoute(self, params: Dict[str, Any]):
        """Deletes the specified route from the specified transit gateway route table."""

        destination_cidr_block = params.get("DestinationCidrBlock")
        if not destination_cidr_block:
            return create_error_response("MissingParameter", "Missing required parameter: DestinationCidrBlock")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        route, error = self._get_route_or_error(route_table, destination_cidr_block)
        if error:
            return error

        route_table.routes = [item for item in route_table.routes if item is not route]

        return {
            'route': route,
            }

    def DeleteTransitGatewayRouteTable(self, params: Dict[str, Any]):
        """Deletes the specified transit gateway route table. If there are any route tables associated with
         the transit gateway route table, you must first runDisassociateRouteTablebefore you can delete the transit gateway route table. This removes any route tables associated with the transit gateway """

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        if route_table.associations:
            return create_error_response(
                "DependencyViolation",
                "The transit gateway route table has associations and cannot be deleted.",
            )

        parent = self.state.transit_gateways.get(route_table.transit_gateway_id)
        if parent and hasattr(parent, "transit_gateway_route_table_ids"):
            if route_table_id in parent.transit_gateway_route_table_ids:
                parent.transit_gateway_route_table_ids.remove(route_table_id)

        self.resources.pop(route_table_id, None)

        return {
            'transitGatewayRouteTable': route_table.to_dict(),
            }

    def DeleteTransitGatewayRouteTableAnnouncement(self, params: Dict[str, Any]):
        """Advertises to the transit gateway that a transit gateway route table is deleted."""

        announcement_id = params.get("TransitGatewayRouteTableAnnouncementId")
        if not announcement_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: TransitGatewayRouteTableAnnouncementId",
            )

        route_table, announcement, error = self._get_announcement_or_error(announcement_id)
        if error:
            return error

        if route_table:
            route_table.route_table_announcements = [
                item
                for item in route_table.route_table_announcements
                if item is not announcement
            ]

        return {
            'transitGatewayRouteTableAnnouncement': announcement,
            }

    def DescribeTransitGatewayRouteTableAnnouncements(self, params: Dict[str, Any]):
        """Describes one or more transit gateway route table advertisements."""

        announcement_ids = params.get("TransitGatewayRouteTableAnnouncementIds.N", []) or []
        filters = params.get("Filter.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        announcements: List[Dict[str, Any]] = []
        if announcement_ids:
            for announcement_id in announcement_ids:
                route_table, announcement = self._find_announcement(announcement_id)
                if not announcement:
                    return create_error_response(
                        "InvalidTransitGatewayRouteTableAnnouncementID.NotFound",
                        f"The ID '{announcement_id}' does not exist",
                    )
                announcements.append(announcement)
        else:
            for route_table in self.resources.values():
                announcements.extend(route_table.route_table_announcements)

        announcements = apply_filters(announcements, filters)
        if max_results:
            announcements = announcements[:max_results]

        return {
            'nextToken': None,
            'transitGatewayRouteTableAnnouncements': announcements,
            }

    def DescribeTransitGatewayRouteTables(self, params: Dict[str, Any]):
        """Describes one or more transit gateway route tables. By default, all transit gateway route tables are described.
         Alternatively, you can filter the results."""

        route_table_ids = params.get("TransitGatewayRouteTableIds.N", []) or []
        filters = params.get("Filter.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if route_table_ids:
            resources: List[TransitGatewayRouteTable] = []
            for route_table_id in route_table_ids:
                resource = self.resources.get(route_table_id)
                if not resource:
                    return create_error_response(
                        "InvalidTransitGatewayRouteTableID.NotFound",
                        f"The ID '{route_table_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, filters)
        if max_results:
            resources = resources[:max_results]

        return {
            'nextToken': None,
            'transitGatewayRouteTables': [resource.to_dict() for resource in resources],
            }

    def DisableTransitGatewayRouteTablePropagation(self, params: Dict[str, Any]):
        """Disables the specified resource attachment from propagating routes to the specified
         propagation route table."""

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        attachment = self.state.transit_gateway_connect.get(attachment_id)
        if not attachment:
            attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if not attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )

        announcement_id = params.get("TransitGatewayRouteTableAnnouncementId")
        if announcement_id:
            _, announcement = self._find_announcement(announcement_id)
            if not announcement:
                return create_error_response(
                    "InvalidTransitGatewayRouteTableAnnouncementID.NotFound",
                    f"The ID '{announcement_id}' does not exist",
                )

        propagation = self._find_propagation(route_table, attachment_id)
        payload = {
            "resourceId": attachment_id,
            "resourceType": "transit-gateway-attachment",
            "state": "disabled",
            "transitGatewayAttachmentId": attachment_id,
            "transitGatewayRouteTableAnnouncementId": announcement_id,
            "transitGatewayRouteTableId": route_table_id,
        }
        if not propagation:
            propagation = payload
            route_table.propagations.append(propagation)
        else:
            propagation.update(payload)

        return {
            'propagation': propagation,
            }

    def DisassociateTransitGatewayRouteTable(self, params: Dict[str, Any]):
        """Disassociates a resource attachment from a transit gateway route table."""

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        attachment = self.state.transit_gateway_connect.get(attachment_id)
        if not attachment:
            attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if not attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )

        association = self._find_association(route_table, attachment_id)
        if not association:
            association = {
                "resourceId": attachment_id,
                "resourceType": "transit-gateway-attachment",
                "state": "disassociated",
                "transitGatewayAttachmentId": attachment_id,
                "transitGatewayRouteTableId": route_table_id,
            }
            route_table.associations.append(association)
        else:
            association.update({
                "resourceId": attachment_id,
                "resourceType": association.get("resourceType") or "transit-gateway-attachment",
                "state": "disassociated",
                "transitGatewayAttachmentId": attachment_id,
                "transitGatewayRouteTableId": route_table_id,
            })

        return {
            'association': association,
            }

    def EnableTransitGatewayRouteTablePropagation(self, params: Dict[str, Any]):
        """Enables the specified attachment to propagate routes to the specified
         propagation route table."""

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        attachment = self.state.transit_gateway_connect.get(attachment_id)
        if not attachment:
            attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if not attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )

        announcement_id = params.get("TransitGatewayRouteTableAnnouncementId")
        if announcement_id:
            _, announcement = self._find_announcement(announcement_id)
            if not announcement:
                return create_error_response(
                    "InvalidTransitGatewayRouteTableAnnouncementID.NotFound",
                    f"The ID '{announcement_id}' does not exist",
                )

        propagation = self._find_propagation(route_table, attachment_id)
        payload = {
            "resourceId": attachment_id,
            "resourceType": "transit-gateway-attachment",
            "state": "enabled",
            "transitGatewayAttachmentId": attachment_id,
            "transitGatewayRouteTableAnnouncementId": announcement_id,
            "transitGatewayRouteTableId": route_table_id,
        }
        if not propagation:
            propagation = payload
            route_table.propagations.append(propagation)
        else:
            propagation.update(payload)

        return {
            'propagation': propagation,
            }

    def ExportTransitGatewayRoutes(self, params: Dict[str, Any]):
        """Exports routes from the specified transit gateway route table to the specified S3 bucket.
         By default, all routes are exported. Alternatively, you can filter by CIDR range. The routes are saved to the specified bucket in a JSON file. For more information, seeExport route tables
             """

        s3_bucket = params.get("S3Bucket")
        if not s3_bucket:
            return create_error_response("MissingParameter", "Missing required parameter: S3Bucket")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        filters = params.get("Filter.N", []) or []

        routes: List[Dict[str, Any]] = []
        for route in route_table.routes:
            entry = route.copy()
            entry["destination_cidr_block"] = entry.get("destinationCidrBlock")
            routes.append(entry)

        exported_routes = apply_filters(routes, filters)
        for entry in exported_routes:
            entry.pop("destination_cidr_block", None)

        export_id = self._generate_id("tgw-rt-export")
        s3_location = f"s3://{s3_bucket}/{route_table_id}/{export_id}.json"

        return {
            's3Location': s3_location,
            }

    def GetTransitGatewayAttachmentPropagations(self, params: Dict[str, Any]):
        """Lists the route tables to which the specified resource attachment propagates routes."""

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        attachment = self.state.transit_gateway_connect.get(attachment_id)
        if not attachment:
            attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if not attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )

        filters = params.get("Filter.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        propagations: List[Dict[str, Any]] = []
        for route_table in self.resources.values():
            for propagation in route_table.propagations:
                if propagation.get("transitGatewayAttachmentId") != attachment_id:
                    continue
                entry = {
                    "state": propagation.get("state"),
                    "transitGatewayRouteTableId": propagation.get("transitGatewayRouteTableId")
                    or route_table.transit_gateway_route_table_id,
                }
                entry["transit_gateway_route_table_id"] = entry["transitGatewayRouteTableId"]
                propagations.append(entry)

        propagations = apply_filters(propagations, filters)
        if max_results:
            propagations = propagations[:max_results]
        for entry in propagations:
            entry.pop("transit_gateway_route_table_id", None)

        return {
            'nextToken': None,
            'transitGatewayAttachmentPropagations': propagations,
            }

    def GetTransitGatewayPrefixListReferences(self, params: Dict[str, Any]):
        """Gets information about the prefix list references in a specified transit gateway route table."""

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        filters = params.get("Filter.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        references: List[Dict[str, Any]] = []
        for reference in route_table.prefix_list_references:
            entry = reference.copy()
            entry["prefix_list_id"] = entry.get("prefixListId")
            references.append(entry)

        references = apply_filters(references, filters)
        if max_results:
            references = references[:max_results]
        for entry in references:
            entry.pop("prefix_list_id", None)

        return {
            'nextToken': None,
            'transitGatewayPrefixListReferenceSet': references,
            }

    def GetTransitGatewayRouteTableAssociations(self, params: Dict[str, Any]):
        """Gets information about the associations for the specified transit gateway route table."""

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        filters = params.get("Filter.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        associations: List[Dict[str, Any]] = []
        for association in route_table.associations:
            entry = association.copy()
            entry["transit_gateway_attachment_id"] = entry.get("transitGatewayAttachmentId")
            associations.append(entry)

        associations = apply_filters(associations, filters)
        if max_results:
            associations = associations[:max_results]
        for entry in associations:
            entry.pop("transit_gateway_attachment_id", None)

        return {
            'associations': associations,
            'nextToken': None,
            }

    def GetTransitGatewayRouteTablePropagations(self, params: Dict[str, Any]):
        """Gets information about the route table propagations for the specified transit gateway route table."""

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        filters = params.get("Filter.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        propagations: List[Dict[str, Any]] = []
        for propagation in route_table.propagations:
            entry = propagation.copy()
            entry["transit_gateway_attachment_id"] = entry.get("transitGatewayAttachmentId")
            propagations.append(entry)

        propagations = apply_filters(propagations, filters)
        if max_results:
            propagations = propagations[:max_results]
        for entry in propagations:
            entry.pop("transit_gateway_attachment_id", None)

        return {
            'nextToken': None,
            'transitGatewayRouteTablePropagations': propagations,
            }

    def ModifyTransitGatewayPrefixListReference(self, params: Dict[str, Any]):
        """Modifies a reference (route) to a prefix list in a specified transit gateway route table."""

        prefix_list_id = params.get("PrefixListId")
        if not prefix_list_id:
            return create_error_response("MissingParameter", "Missing required parameter: PrefixListId")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        prefix_list = self.state.managed_prefix_lists.get(prefix_list_id)
        if not prefix_list:
            return create_error_response(
                "InvalidPrefixListID.NotFound",
                f"The ID '{prefix_list_id}' does not exist",
            )

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment = None
        if attachment_id:
            attachment = self.state.transit_gateway_connect.get(attachment_id)
            if not attachment:
                attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
            if not attachment:
                return create_error_response(
                    "InvalidTransitGatewayAttachmentID.NotFound",
                    f"The ID '{attachment_id}' does not exist",
                )

        prefix_list_owner_id = ""
        if isinstance(prefix_list, dict):
            prefix_list_owner_id = prefix_list.get("ownerId") or prefix_list.get("owner_id") or ""
        else:
            prefix_list_owner_id = getattr(prefix_list, "owner_id", "")

        reference, error = self._get_prefix_list_reference_or_error(route_table, prefix_list_id)
        if error:
            return error

        blackhole = bool(params.get("Blackhole"))
        attachment_data = None
        if attachment_id and not blackhole:
            attachment_data = {
                "resourceId": attachment_id,
                "resourceType": "transit-gateway-attachment",
                "transitGatewayAttachmentId": attachment_id,
            }

        reference.update({
            "blackhole": blackhole,
            "prefixListId": prefix_list_id,
            "prefixListOwnerId": prefix_list_owner_id,
            "state": "blackhole" if blackhole else "active",
            "transitGatewayAttachment": attachment_data,
            "transitGatewayRouteTableId": route_table_id,
        })

        return {
            'transitGatewayPrefixListReference': reference,
            }

    def ReplaceTransitGatewayRoute(self, params: Dict[str, Any]):
        """Replaces the specified route in the specified transit gateway route table."""

        destination_cidr_block = params.get("DestinationCidrBlock")
        if not destination_cidr_block:
            return create_error_response("MissingParameter", "Missing required parameter: DestinationCidrBlock")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment = None
        if attachment_id:
            attachment = self.state.transit_gateway_connect.get(attachment_id)
            if not attachment:
                attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
            if not attachment:
                return create_error_response(
                    "InvalidTransitGatewayAttachmentID.NotFound",
                    f"The ID '{attachment_id}' does not exist",
                )

        blackhole = bool(params.get("Blackhole"))
        attachment_entries: List[Dict[str, Any]] = []
        if attachment_id and not blackhole:
            attachment_entries.append({
                "resourceId": attachment_id,
                "resourceType": "transit-gateway-attachment",
                "transitGatewayAttachmentId": attachment_id,
            })

        route, error = self._get_route_or_error(route_table, destination_cidr_block)
        if error:
            return error

        route.update({
            "destinationCidrBlock": destination_cidr_block,
            "prefixListId": None,
            "state": "blackhole" if blackhole else "active",
            "transitGatewayAttachments": attachment_entries,
            "transitGatewayRouteTableAnnouncementId": None,
            "type": "static",
        })

        return {
            'route': route,
            }

    def SearchTransitGatewayRoutes(self, params: Dict[str, Any]):
        """Searches for routes in the specified transit gateway route table."""

        filters = params.get("Filter.N")
        if not filters:
            return create_error_response("MissingParameter", "Missing required parameter: Filter.N")

        route_table_id = params.get("TransitGatewayRouteTableId")
        if not route_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayRouteTableId")

        route_table, error = self._get_route_table_or_error(route_table_id)
        if error:
            return error

        max_results = int(params.get("MaxResults") or 100)

        routes: List[Dict[str, Any]] = []
        for route in route_table.routes:
            entry = route.copy()
            entry["destination_cidr_block"] = entry.get("destinationCidrBlock")
            entry["prefix_list_id"] = entry.get("prefixListId")
            if entry.get("transitGatewayAttachments"):
                entry["transit_gateway_attachment_id"] = entry["transitGatewayAttachments"][0].get("transitGatewayAttachmentId")
            routes.append(entry)

        filtered_routes = apply_filters(routes, filters)
        additional_routes_available = max_results and len(filtered_routes) > max_results
        if max_results:
            filtered_routes = filtered_routes[:max_results]
        for entry in filtered_routes:
            entry.pop("destination_cidr_block", None)
            entry.pop("prefix_list_id", None)
            entry.pop("transit_gateway_attachment_id", None)

        return {
            'additionalRoutesAvailable': bool(additional_routes_available),
            'routeSet': filtered_routes,
            }

    def _generate_id(self, prefix: str = 'tgw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class transitgatewayroutetable_RequestParser:
    @staticmethod
    def parse_associate_transit_gateway_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_create_transit_gateway_prefix_list_reference_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Blackhole": get_scalar(md, "Blackhole"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PrefixListId": get_scalar(md, "PrefixListId"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_create_transit_gateway_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Blackhole": get_scalar(md, "Blackhole"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_create_transit_gateway_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecifications.N": parse_tags(md, "TagSpecifications"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
        }

    @staticmethod
    def parse_create_transit_gateway_route_table_announcement_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PeeringAttachmentId": get_scalar(md, "PeeringAttachmentId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_prefix_list_reference_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PrefixListId": get_scalar(md, "PrefixListId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_route_table_announcement_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayRouteTableAnnouncementId": get_scalar(md, "TransitGatewayRouteTableAnnouncementId"),
        }

    @staticmethod
    def parse_describe_transit_gateway_route_table_announcements_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayRouteTableAnnouncementIds.N": get_indexed_list(md, "TransitGatewayRouteTableAnnouncementIds"),
        }

    @staticmethod
    def parse_describe_transit_gateway_route_tables_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayRouteTableIds.N": get_indexed_list(md, "TransitGatewayRouteTableIds"),
        }

    @staticmethod
    def parse_disable_transit_gateway_route_table_propagation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableAnnouncementId": get_scalar(md, "TransitGatewayRouteTableAnnouncementId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_disassociate_transit_gateway_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_enable_transit_gateway_route_table_propagation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableAnnouncementId": get_scalar(md, "TransitGatewayRouteTableAnnouncementId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_export_transit_gateway_routes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "S3Bucket": get_scalar(md, "S3Bucket"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_get_transit_gateway_attachment_propagations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_get_transit_gateway_prefix_list_references_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_get_transit_gateway_route_table_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_get_transit_gateway_route_table_propagations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_modify_transit_gateway_prefix_list_reference_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Blackhole": get_scalar(md, "Blackhole"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PrefixListId": get_scalar(md, "PrefixListId"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_replace_transit_gateway_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Blackhole": get_scalar(md, "Blackhole"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_search_transit_gateway_routes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "TransitGatewayRouteTableId": get_scalar(md, "TransitGatewayRouteTableId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateTransitGatewayRouteTable": transitgatewayroutetable_RequestParser.parse_associate_transit_gateway_route_table_request,
            "CreateTransitGatewayPrefixListReference": transitgatewayroutetable_RequestParser.parse_create_transit_gateway_prefix_list_reference_request,
            "CreateTransitGatewayRoute": transitgatewayroutetable_RequestParser.parse_create_transit_gateway_route_request,
            "CreateTransitGatewayRouteTable": transitgatewayroutetable_RequestParser.parse_create_transit_gateway_route_table_request,
            "CreateTransitGatewayRouteTableAnnouncement": transitgatewayroutetable_RequestParser.parse_create_transit_gateway_route_table_announcement_request,
            "DeleteTransitGatewayPrefixListReference": transitgatewayroutetable_RequestParser.parse_delete_transit_gateway_prefix_list_reference_request,
            "DeleteTransitGatewayRoute": transitgatewayroutetable_RequestParser.parse_delete_transit_gateway_route_request,
            "DeleteTransitGatewayRouteTable": transitgatewayroutetable_RequestParser.parse_delete_transit_gateway_route_table_request,
            "DeleteTransitGatewayRouteTableAnnouncement": transitgatewayroutetable_RequestParser.parse_delete_transit_gateway_route_table_announcement_request,
            "DescribeTransitGatewayRouteTableAnnouncements": transitgatewayroutetable_RequestParser.parse_describe_transit_gateway_route_table_announcements_request,
            "DescribeTransitGatewayRouteTables": transitgatewayroutetable_RequestParser.parse_describe_transit_gateway_route_tables_request,
            "DisableTransitGatewayRouteTablePropagation": transitgatewayroutetable_RequestParser.parse_disable_transit_gateway_route_table_propagation_request,
            "DisassociateTransitGatewayRouteTable": transitgatewayroutetable_RequestParser.parse_disassociate_transit_gateway_route_table_request,
            "EnableTransitGatewayRouteTablePropagation": transitgatewayroutetable_RequestParser.parse_enable_transit_gateway_route_table_propagation_request,
            "ExportTransitGatewayRoutes": transitgatewayroutetable_RequestParser.parse_export_transit_gateway_routes_request,
            "GetTransitGatewayAttachmentPropagations": transitgatewayroutetable_RequestParser.parse_get_transit_gateway_attachment_propagations_request,
            "GetTransitGatewayPrefixListReferences": transitgatewayroutetable_RequestParser.parse_get_transit_gateway_prefix_list_references_request,
            "GetTransitGatewayRouteTableAssociations": transitgatewayroutetable_RequestParser.parse_get_transit_gateway_route_table_associations_request,
            "GetTransitGatewayRouteTablePropagations": transitgatewayroutetable_RequestParser.parse_get_transit_gateway_route_table_propagations_request,
            "ModifyTransitGatewayPrefixListReference": transitgatewayroutetable_RequestParser.parse_modify_transit_gateway_prefix_list_reference_request,
            "ReplaceTransitGatewayRoute": transitgatewayroutetable_RequestParser.parse_replace_transit_gateway_route_request,
            "SearchTransitGatewayRoutes": transitgatewayroutetable_RequestParser.parse_search_transit_gateway_routes_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class transitgatewayroutetable_ResponseSerializer:
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
                xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_transit_gateway_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateTransitGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize association
        _association_key = None
        if "association" in data:
            _association_key = "association"
        elif "Association" in data:
            _association_key = "Association"
        if _association_key:
            param_data = data[_association_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<association>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</association>')
        xml_parts.append(f'</AssociateTransitGatewayRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_prefix_list_reference_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayPrefixListReferenceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPrefixListReference
        _transitGatewayPrefixListReference_key = None
        if "transitGatewayPrefixListReference" in data:
            _transitGatewayPrefixListReference_key = "transitGatewayPrefixListReference"
        elif "TransitGatewayPrefixListReference" in data:
            _transitGatewayPrefixListReference_key = "TransitGatewayPrefixListReference"
        if _transitGatewayPrefixListReference_key:
            param_data = data[_transitGatewayPrefixListReference_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPrefixListReference>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPrefixListReference>')
        xml_parts.append(f'</CreateTransitGatewayPrefixListReferenceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize route
        _route_key = None
        if "route" in data:
            _route_key = "route"
        elif "Route" in data:
            _route_key = "Route"
        if _route_key:
            param_data = data[_route_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<route>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</route>')
        xml_parts.append(f'</CreateTransitGatewayRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayRouteTable
        _transitGatewayRouteTable_key = None
        if "transitGatewayRouteTable" in data:
            _transitGatewayRouteTable_key = "transitGatewayRouteTable"
        elif "TransitGatewayRouteTable" in data:
            _transitGatewayRouteTable_key = "TransitGatewayRouteTable"
        if _transitGatewayRouteTable_key:
            param_data = data[_transitGatewayRouteTable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayRouteTable>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayRouteTable>')
        xml_parts.append(f'</CreateTransitGatewayRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_route_table_announcement_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayRouteTableAnnouncementResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayRouteTableAnnouncement
        _transitGatewayRouteTableAnnouncement_key = None
        if "transitGatewayRouteTableAnnouncement" in data:
            _transitGatewayRouteTableAnnouncement_key = "transitGatewayRouteTableAnnouncement"
        elif "TransitGatewayRouteTableAnnouncement" in data:
            _transitGatewayRouteTableAnnouncement_key = "TransitGatewayRouteTableAnnouncement"
        if _transitGatewayRouteTableAnnouncement_key:
            param_data = data[_transitGatewayRouteTableAnnouncement_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayRouteTableAnnouncement>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayRouteTableAnnouncement>')
        xml_parts.append(f'</CreateTransitGatewayRouteTableAnnouncementResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_prefix_list_reference_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayPrefixListReferenceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPrefixListReference
        _transitGatewayPrefixListReference_key = None
        if "transitGatewayPrefixListReference" in data:
            _transitGatewayPrefixListReference_key = "transitGatewayPrefixListReference"
        elif "TransitGatewayPrefixListReference" in data:
            _transitGatewayPrefixListReference_key = "TransitGatewayPrefixListReference"
        if _transitGatewayPrefixListReference_key:
            param_data = data[_transitGatewayPrefixListReference_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPrefixListReference>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPrefixListReference>')
        xml_parts.append(f'</DeleteTransitGatewayPrefixListReferenceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize route
        _route_key = None
        if "route" in data:
            _route_key = "route"
        elif "Route" in data:
            _route_key = "Route"
        if _route_key:
            param_data = data[_route_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<route>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</route>')
        xml_parts.append(f'</DeleteTransitGatewayRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayRouteTable
        _transitGatewayRouteTable_key = None
        if "transitGatewayRouteTable" in data:
            _transitGatewayRouteTable_key = "transitGatewayRouteTable"
        elif "TransitGatewayRouteTable" in data:
            _transitGatewayRouteTable_key = "TransitGatewayRouteTable"
        if _transitGatewayRouteTable_key:
            param_data = data[_transitGatewayRouteTable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayRouteTable>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayRouteTable>')
        xml_parts.append(f'</DeleteTransitGatewayRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_route_table_announcement_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayRouteTableAnnouncementResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayRouteTableAnnouncement
        _transitGatewayRouteTableAnnouncement_key = None
        if "transitGatewayRouteTableAnnouncement" in data:
            _transitGatewayRouteTableAnnouncement_key = "transitGatewayRouteTableAnnouncement"
        elif "TransitGatewayRouteTableAnnouncement" in data:
            _transitGatewayRouteTableAnnouncement_key = "TransitGatewayRouteTableAnnouncement"
        if _transitGatewayRouteTableAnnouncement_key:
            param_data = data[_transitGatewayRouteTableAnnouncement_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayRouteTableAnnouncement>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayRouteTableAnnouncement>')
        xml_parts.append(f'</DeleteTransitGatewayRouteTableAnnouncementResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_route_table_announcements_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayRouteTableAnnouncementsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayRouteTableAnnouncements
        _transitGatewayRouteTableAnnouncements_key = None
        if "transitGatewayRouteTableAnnouncements" in data:
            _transitGatewayRouteTableAnnouncements_key = "transitGatewayRouteTableAnnouncements"
        elif "TransitGatewayRouteTableAnnouncements" in data:
            _transitGatewayRouteTableAnnouncements_key = "TransitGatewayRouteTableAnnouncements"
        if _transitGatewayRouteTableAnnouncements_key:
            param_data = data[_transitGatewayRouteTableAnnouncements_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayRouteTableAnnouncementsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayRouteTableAnnouncementsSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayRouteTableAnnouncementsSet/>')
        xml_parts.append(f'</DescribeTransitGatewayRouteTableAnnouncementsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_route_tables_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayRouteTablesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayRouteTables
        _transitGatewayRouteTables_key = None
        if "transitGatewayRouteTables" in data:
            _transitGatewayRouteTables_key = "transitGatewayRouteTables"
        elif "TransitGatewayRouteTables" in data:
            _transitGatewayRouteTables_key = "TransitGatewayRouteTables"
        if _transitGatewayRouteTables_key:
            param_data = data[_transitGatewayRouteTables_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayRouteTablesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayRouteTablesSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayRouteTablesSet/>')
        xml_parts.append(f'</DescribeTransitGatewayRouteTablesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disable_transit_gateway_route_table_propagation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableTransitGatewayRouteTablePropagationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize propagation
        _propagation_key = None
        if "propagation" in data:
            _propagation_key = "propagation"
        elif "Propagation" in data:
            _propagation_key = "Propagation"
        if _propagation_key:
            param_data = data[_propagation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<propagation>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</propagation>')
        xml_parts.append(f'</DisableTransitGatewayRouteTablePropagationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_transit_gateway_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateTransitGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize association
        _association_key = None
        if "association" in data:
            _association_key = "association"
        elif "Association" in data:
            _association_key = "Association"
        if _association_key:
            param_data = data[_association_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<association>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</association>')
        xml_parts.append(f'</DisassociateTransitGatewayRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_transit_gateway_route_table_propagation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableTransitGatewayRouteTablePropagationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize propagation
        _propagation_key = None
        if "propagation" in data:
            _propagation_key = "propagation"
        elif "Propagation" in data:
            _propagation_key = "Propagation"
        if _propagation_key:
            param_data = data[_propagation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<propagation>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</propagation>')
        xml_parts.append(f'</EnableTransitGatewayRouteTablePropagationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_export_transit_gateway_routes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ExportTransitGatewayRoutesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize s3Location
        _s3Location_key = None
        if "s3Location" in data:
            _s3Location_key = "s3Location"
        elif "S3Location" in data:
            _s3Location_key = "S3Location"
        if _s3Location_key:
            param_data = data[_s3Location_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<s3Location>{esc(str(param_data))}</s3Location>')
        xml_parts.append(f'</ExportTransitGatewayRoutesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_transit_gateway_attachment_propagations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetTransitGatewayAttachmentPropagationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayAttachmentPropagations
        _transitGatewayAttachmentPropagations_key = None
        if "transitGatewayAttachmentPropagations" in data:
            _transitGatewayAttachmentPropagations_key = "transitGatewayAttachmentPropagations"
        elif "TransitGatewayAttachmentPropagations" in data:
            _transitGatewayAttachmentPropagations_key = "TransitGatewayAttachmentPropagations"
        if _transitGatewayAttachmentPropagations_key:
            param_data = data[_transitGatewayAttachmentPropagations_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayAttachmentPropagationsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayAttachmentPropagationsSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayAttachmentPropagationsSet/>')
        xml_parts.append(f'</GetTransitGatewayAttachmentPropagationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_transit_gateway_prefix_list_references_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetTransitGatewayPrefixListReferencesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayPrefixListReferenceSet
        _transitGatewayPrefixListReferenceSet_key = None
        if "transitGatewayPrefixListReferenceSet" in data:
            _transitGatewayPrefixListReferenceSet_key = "transitGatewayPrefixListReferenceSet"
        elif "TransitGatewayPrefixListReferenceSet" in data:
            _transitGatewayPrefixListReferenceSet_key = "TransitGatewayPrefixListReferenceSet"
        elif "TransitGatewayPrefixListReferences" in data:
            _transitGatewayPrefixListReferenceSet_key = "TransitGatewayPrefixListReferences"
        if _transitGatewayPrefixListReferenceSet_key:
            param_data = data[_transitGatewayPrefixListReferenceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayPrefixListReferenceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayPrefixListReferenceSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayPrefixListReferenceSet/>')
        xml_parts.append(f'</GetTransitGatewayPrefixListReferencesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_transit_gateway_route_table_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetTransitGatewayRouteTableAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associations
        _associations_key = None
        if "associations" in data:
            _associations_key = "associations"
        elif "Associations" in data:
            _associations_key = "Associations"
        if _associations_key:
            param_data = data[_associations_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<associationsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</associationsSet>')
            else:
                xml_parts.append(f'{indent_str}<associationsSet/>')
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
        xml_parts.append(f'</GetTransitGatewayRouteTableAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_transit_gateway_route_table_propagations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetTransitGatewayRouteTablePropagationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayRouteTablePropagations
        _transitGatewayRouteTablePropagations_key = None
        if "transitGatewayRouteTablePropagations" in data:
            _transitGatewayRouteTablePropagations_key = "transitGatewayRouteTablePropagations"
        elif "TransitGatewayRouteTablePropagations" in data:
            _transitGatewayRouteTablePropagations_key = "TransitGatewayRouteTablePropagations"
        if _transitGatewayRouteTablePropagations_key:
            param_data = data[_transitGatewayRouteTablePropagations_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayRouteTablePropagationsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayRouteTablePropagationsSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayRouteTablePropagationsSet/>')
        xml_parts.append(f'</GetTransitGatewayRouteTablePropagationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_transit_gateway_prefix_list_reference_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyTransitGatewayPrefixListReferenceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPrefixListReference
        _transitGatewayPrefixListReference_key = None
        if "transitGatewayPrefixListReference" in data:
            _transitGatewayPrefixListReference_key = "transitGatewayPrefixListReference"
        elif "TransitGatewayPrefixListReference" in data:
            _transitGatewayPrefixListReference_key = "TransitGatewayPrefixListReference"
        if _transitGatewayPrefixListReference_key:
            param_data = data[_transitGatewayPrefixListReference_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPrefixListReference>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPrefixListReference>')
        xml_parts.append(f'</ModifyTransitGatewayPrefixListReferenceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_replace_transit_gateway_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReplaceTransitGatewayRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize route
        _route_key = None
        if "route" in data:
            _route_key = "route"
        elif "Route" in data:
            _route_key = "Route"
        if _route_key:
            param_data = data[_route_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<route>')
            xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</route>')
        xml_parts.append(f'</ReplaceTransitGatewayRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_search_transit_gateway_routes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<SearchTransitGatewayRoutesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize additionalRoutesAvailable
        _additionalRoutesAvailable_key = None
        if "additionalRoutesAvailable" in data:
            _additionalRoutesAvailable_key = "additionalRoutesAvailable"
        elif "AdditionalRoutesAvailable" in data:
            _additionalRoutesAvailable_key = "AdditionalRoutesAvailable"
        if _additionalRoutesAvailable_key:
            param_data = data[_additionalRoutesAvailable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<additionalRoutesAvailable>{esc(str(param_data))}</additionalRoutesAvailable>')
        # Serialize routeSet
        _routeSet_key = None
        if "routeSet" in data:
            _routeSet_key = "routeSet"
        elif "RouteSet" in data:
            _routeSet_key = "RouteSet"
        elif "Routes" in data:
            _routeSet_key = "Routes"
        if _routeSet_key:
            param_data = data[_routeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayroutetable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeSet>')
            else:
                xml_parts.append(f'{indent_str}<routeSet/>')
        xml_parts.append(f'</SearchTransitGatewayRoutesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateTransitGatewayRouteTable": transitgatewayroutetable_ResponseSerializer.serialize_associate_transit_gateway_route_table_response,
            "CreateTransitGatewayPrefixListReference": transitgatewayroutetable_ResponseSerializer.serialize_create_transit_gateway_prefix_list_reference_response,
            "CreateTransitGatewayRoute": transitgatewayroutetable_ResponseSerializer.serialize_create_transit_gateway_route_response,
            "CreateTransitGatewayRouteTable": transitgatewayroutetable_ResponseSerializer.serialize_create_transit_gateway_route_table_response,
            "CreateTransitGatewayRouteTableAnnouncement": transitgatewayroutetable_ResponseSerializer.serialize_create_transit_gateway_route_table_announcement_response,
            "DeleteTransitGatewayPrefixListReference": transitgatewayroutetable_ResponseSerializer.serialize_delete_transit_gateway_prefix_list_reference_response,
            "DeleteTransitGatewayRoute": transitgatewayroutetable_ResponseSerializer.serialize_delete_transit_gateway_route_response,
            "DeleteTransitGatewayRouteTable": transitgatewayroutetable_ResponseSerializer.serialize_delete_transit_gateway_route_table_response,
            "DeleteTransitGatewayRouteTableAnnouncement": transitgatewayroutetable_ResponseSerializer.serialize_delete_transit_gateway_route_table_announcement_response,
            "DescribeTransitGatewayRouteTableAnnouncements": transitgatewayroutetable_ResponseSerializer.serialize_describe_transit_gateway_route_table_announcements_response,
            "DescribeTransitGatewayRouteTables": transitgatewayroutetable_ResponseSerializer.serialize_describe_transit_gateway_route_tables_response,
            "DisableTransitGatewayRouteTablePropagation": transitgatewayroutetable_ResponseSerializer.serialize_disable_transit_gateway_route_table_propagation_response,
            "DisassociateTransitGatewayRouteTable": transitgatewayroutetable_ResponseSerializer.serialize_disassociate_transit_gateway_route_table_response,
            "EnableTransitGatewayRouteTablePropagation": transitgatewayroutetable_ResponseSerializer.serialize_enable_transit_gateway_route_table_propagation_response,
            "ExportTransitGatewayRoutes": transitgatewayroutetable_ResponseSerializer.serialize_export_transit_gateway_routes_response,
            "GetTransitGatewayAttachmentPropagations": transitgatewayroutetable_ResponseSerializer.serialize_get_transit_gateway_attachment_propagations_response,
            "GetTransitGatewayPrefixListReferences": transitgatewayroutetable_ResponseSerializer.serialize_get_transit_gateway_prefix_list_references_response,
            "GetTransitGatewayRouteTableAssociations": transitgatewayroutetable_ResponseSerializer.serialize_get_transit_gateway_route_table_associations_response,
            "GetTransitGatewayRouteTablePropagations": transitgatewayroutetable_ResponseSerializer.serialize_get_transit_gateway_route_table_propagations_response,
            "ModifyTransitGatewayPrefixListReference": transitgatewayroutetable_ResponseSerializer.serialize_modify_transit_gateway_prefix_list_reference_response,
            "ReplaceTransitGatewayRoute": transitgatewayroutetable_ResponseSerializer.serialize_replace_transit_gateway_route_response,
            "SearchTransitGatewayRoutes": transitgatewayroutetable_ResponseSerializer.serialize_search_transit_gateway_routes_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

