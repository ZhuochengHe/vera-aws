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
class TransitGatewayMulticast:
    group_ip_address: str = ""
    group_member: bool = False
    group_source: bool = False
    member_type: str = ""
    network_interface_id: str = ""
    resource_id: str = ""
    resource_owner_id: str = ""
    resource_type: str = ""
    source_type: str = ""
    subnet_id: str = ""
    transit_gateway_attachment_id: str = ""

    # Internal dependency tracking — not in API response
    elastic_ip_addresse_ids: List[str] = field(default_factory=list)  # tracks ElasticIpAddresse children
    route_table_ids: List[str] = field(default_factory=list)  # tracks RouteTable children

    creation_time: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    owner_id: str = ""
    state: str = ""
    tag_set: List[Dict[str, Any]] = field(default_factory=list)
    transit_gateway_id: str = ""
    transit_gateway_multicast_domain_arn: str = ""
    transit_gateway_multicast_domain_id: str = ""
    associations: List[Dict[str, Any]] = field(default_factory=list)
    multicast_group_members: List[Dict[str, Any]] = field(default_factory=list)
    multicast_group_sources: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "groupIpAddress": self.group_ip_address,
            "groupMember": self.group_member,
            "groupSource": self.group_source,
            "memberType": self.member_type,
            "networkInterfaceId": self.network_interface_id,
            "resourceId": self.resource_id,
            "resourceOwnerId": self.resource_owner_id,
            "resourceType": self.resource_type,
            "sourceType": self.source_type,
            "subnetId": self.subnet_id,
            "transitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "creationTime": self.creation_time,
            "options": self.options,
            "ownerId": self.owner_id,
            "state": self.state,
            "tagSet": self.tag_set,
            "transitGatewayId": self.transit_gateway_id,
            "transitGatewayMulticastDomainArn": self.transit_gateway_multicast_domain_arn,
            "transitGatewayMulticastDomainId": self.transit_gateway_multicast_domain_id,
        }

class TransitGatewayMulticast_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.transit_gateway_multicast  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.tags.get(params['resource_id']).transit_gateway_multicast_ids.append(new_id)
    #   Delete: self.state.tags.get(resource.resource_id).transit_gateway_multicast_ids.remove(resource_id)
    #   Create: self.state.subnets.get(params['subnet_id']).transit_gateway_multicast_ids.append(new_id)
    #   Delete: self.state.subnets.get(resource.subnet_id).transit_gateway_multicast_ids.remove(resource_id)
    #   Create: self.state.transit_gateway_connect.get(params['transit_gateway_attachment_id']).transit_gateway_multicast_ids.append(new_id)
    #   Delete: self.state.transit_gateway_connect.get(resource.transit_gateway_attachment_id).transit_gateway_multicast_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            value = params.get(key)
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _get_or_error(self, store: Dict[str, Any], resource_id: str, code: str, message: str):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(code, message)
        return resource, None

    def _association_entry(
        self,
        subnet_id: str,
        attachment_id: str,
        state: str,
        resource_id: str = "",
        resource_owner_id: str = "",
        resource_type: str = "subnet",
    ) -> Dict[str, Any]:
        return {
            "resourceId": resource_id or subnet_id,
            "resourceOwnerId": resource_owner_id,
            "resourceType": resource_type,
            "subnetId": subnet_id,
            "state": state,
            "transitGatewayAttachmentId": attachment_id,
        }

    def _find_association(self, domain: TransitGatewayMulticast, subnet_id: str) -> Optional[Dict[str, Any]]:
        for association in getattr(domain, "associations", []):
            if association.get("subnetId") == subnet_id:
                return association
        return None

    def AcceptTransitGatewayMulticastDomainAssociations(self, params: Dict[str, Any]):
        """Accepts a request to associate subnets with a transit gateway multicast domain."""

        domain_id = params.get("TransitGatewayMulticastDomainId")
        if not domain_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayMulticastDomainId")

        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        attachment, error = self._get_or_error(
            self.state.transit_gateway_connect,
            attachment_id,
            "InvalidTransitGatewayAttachmentID.NotFound",
            f"The ID '{attachment_id}' does not exist",
        )
        if error:
            return error

        subnet_ids = params.get("SubnetIds.N", []) or []
        for subnet_id in subnet_ids:
            if not self.state.subnets.get(subnet_id):
                return create_error_response(
                    "InvalidSubnetID.NotFound",
                    f"The ID '{subnet_id}' does not exist",
                )

        associations = getattr(domain, "associations", []) or []
        for subnet_id in subnet_ids:
            subnet = self.state.subnets.get(subnet_id)
            association = self._find_association(domain, subnet_id)
            if association:
                association["state"] = "associated"
                association["transitGatewayAttachmentId"] = attachment_id
            else:
                associations.append(
                    self._association_entry(
                        subnet_id=subnet_id,
                        attachment_id=attachment_id,
                        state="associated",
                        resource_owner_id=getattr(subnet, "owner_id", ""),
                        resource_type="subnet",
                    )
                )
        domain.associations = associations

        first_subnet = self.state.subnets.get(subnet_ids[0]) if subnet_ids else None
        return {
            'associations': {
                'resourceId': subnet_ids[0] if subnet_ids else "",
                'resourceOwnerId': getattr(first_subnet, "owner_id", "") if first_subnet else "",
                'resourceType': "subnet" if subnet_ids else "",
                'subnets': [{"state": "associated", "subnetId": subnet_id} for subnet_id in subnet_ids],
                'transitGatewayAttachmentId': attachment_id,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def AssociateTransitGatewayMulticastDomain(self, params: Dict[str, Any]):
        """Associates the specified subnets and transit gateway attachments with the specified transit gateway multicast domain. The transit gateway attachment must be in the available state before you can add a resource. UseDescribeTransitGatewayAttachmentsto see the state of the attachment."""

        error = self._require_params(
            params,
            ["SubnetIds.N", "TransitGatewayAttachmentId", "TransitGatewayMulticastDomainId"],
        )
        if error:
            return error

        domain_id = params.get("TransitGatewayMulticastDomainId")
        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment, error = self._get_or_error(
            self.state.transit_gateway_connect,
            attachment_id,
            "InvalidTransitGatewayAttachmentID.NotFound",
            f"The ID '{attachment_id}' does not exist",
        )
        if error:
            return error
        if getattr(attachment, "state", ResourceState.AVAILABLE.value) != ResourceState.AVAILABLE.value:
            return create_error_response(
                "InvalidStateTransition",
                "Transit gateway attachment must be in the available state before association.",
            )

        subnet_ids = params.get("SubnetIds.N", []) or []
        for subnet_id in subnet_ids:
            if not self.state.subnets.get(subnet_id):
                return create_error_response(
                    "InvalidSubnetID.NotFound",
                    f"The ID '{subnet_id}' does not exist",
                )

        associations = getattr(domain, "associations", []) or []
        for subnet_id in subnet_ids:
            subnet = self.state.subnets.get(subnet_id)
            association = self._find_association(domain, subnet_id)
            if association:
                association["state"] = "associated"
                association["transitGatewayAttachmentId"] = attachment_id
            else:
                associations.append(
                    self._association_entry(
                        subnet_id=subnet_id,
                        attachment_id=attachment_id,
                        state="associated",
                        resource_owner_id=getattr(subnet, "owner_id", ""),
                        resource_type="subnet",
                    )
                )
        domain.associations = associations

        first_subnet = self.state.subnets.get(subnet_ids[0]) if subnet_ids else None
        return {
            'associations': {
                'resourceId': subnet_ids[0] if subnet_ids else "",
                'resourceOwnerId': getattr(first_subnet, "owner_id", "") if first_subnet else "",
                'resourceType': "subnet" if subnet_ids else "",
                'subnets': [{"state": "associated", "subnetId": subnet_id} for subnet_id in subnet_ids],
                'transitGatewayAttachmentId': attachment_id,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def CreateTransitGatewayMulticastDomain(self, params: Dict[str, Any]):
        """Creates a multicast domain using the specified transit gateway. The transit gateway  must be in the available state before you create a domain. UseDescribeTransitGatewaysto see the state of transit gateway."""

        error = self._require_params(params, ["TransitGatewayId"])
        if error:
            return error

        transit_gateway_id = params.get("TransitGatewayId")
        transit_gateway, error = self._get_or_error(
            self.state.transit_gateways,
            transit_gateway_id,
            "InvalidTransitGatewayID.NotFound",
            f"The ID '{transit_gateway_id}' does not exist",
        )
        if error:
            return error
        if getattr(transit_gateway, "state", ResourceState.AVAILABLE.value) != ResourceState.AVAILABLE.value:
            return create_error_response(
                "InvalidStateTransition",
                "Transit gateway must be in the available state before creating a multicast domain.",
            )

        creation_time = datetime.now(timezone.utc).isoformat()
        options = params.get("Options") or {}
        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        multicast_domain_id = self._generate_id("tgw-mcast-domain")
        multicast_domain_arn = f"arn:aws:ec2:::transit-gateway-multicast-domain/{multicast_domain_id}"
        owner_id = getattr(transit_gateway, "owner_id", "")

        resource = TransitGatewayMulticast(
            creation_time=creation_time,
            options=options,
            owner_id=owner_id,
            state=ResourceState.AVAILABLE.value,
            tag_set=tag_set,
            transit_gateway_id=transit_gateway_id,
            transit_gateway_multicast_domain_arn=multicast_domain_arn,
            transit_gateway_multicast_domain_id=multicast_domain_id,
        )
        self.resources[multicast_domain_id] = resource

        return {
            'transitGatewayMulticastDomain': {
                'creationTime': resource.creation_time,
                'options': {
                    'autoAcceptSharedAssociations': resource.options.get('autoAcceptSharedAssociations'),
                    'igmpv2Support': resource.options.get('igmpv2Support'),
                    'staticSourcesSupport': resource.options.get('staticSourcesSupport'),
                    },
                'ownerId': resource.owner_id,
                'state': resource.state,
                'tagSet': resource.tag_set,
                'transitGatewayId': resource.transit_gateway_id,
                'transitGatewayMulticastDomainArn': resource.transit_gateway_multicast_domain_arn,
                'transitGatewayMulticastDomainId': resource.transit_gateway_multicast_domain_id,
                },
            }

    def DeleteTransitGatewayMulticastDomain(self, params: Dict[str, Any]):
        """Deletes the specified transit gateway multicast domain."""

        error = self._require_params(params, ["TransitGatewayMulticastDomainId"])
        if error:
            return error

        domain_id = params.get("TransitGatewayMulticastDomainId")
        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        if getattr(domain, "elastic_ip_addresse_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGatewayMulticastDomain has dependent ElasticIpAddresse(s) and cannot be deleted.",
            )
        if getattr(domain, "route_table_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGatewayMulticastDomain has dependent RouteTable(s) and cannot be deleted.",
            )

        parent = self.state.tags.get(domain.resource_id)
        if parent and hasattr(parent, "transit_gateway_multicast_ids") and domain_id in parent.transit_gateway_multicast_ids:
            parent.transit_gateway_multicast_ids.remove(domain_id)
        parent = self.state.subnets.get(domain.subnet_id)
        if parent and hasattr(parent, "transit_gateway_multicast_ids") and domain_id in parent.transit_gateway_multicast_ids:
            parent.transit_gateway_multicast_ids.remove(domain_id)
        parent = self.state.transit_gateway_connect.get(domain.transit_gateway_attachment_id)
        if parent and hasattr(parent, "transit_gateway_multicast_ids") and domain_id in parent.transit_gateway_multicast_ids:
            parent.transit_gateway_multicast_ids.remove(domain_id)

        self.resources.pop(domain_id, None)

        return {
            'transitGatewayMulticastDomain': {
                'creationTime': domain.creation_time,
                'options': {
                    'autoAcceptSharedAssociations': domain.options.get('autoAcceptSharedAssociations'),
                    'igmpv2Support': domain.options.get('igmpv2Support'),
                    'staticSourcesSupport': domain.options.get('staticSourcesSupport'),
                    },
                'ownerId': domain.owner_id,
                'state': domain.state,
                'tagSet': domain.tag_set,
                'transitGatewayId': domain.transit_gateway_id,
                'transitGatewayMulticastDomainArn': domain.transit_gateway_multicast_domain_arn,
                'transitGatewayMulticastDomainId': domain.transit_gateway_multicast_domain_id,
                },
            }

    def DeregisterTransitGatewayMulticastGroupMembers(self, params: Dict[str, Any]):
        """Deregisters the specified members (network interfaces) from the  transit gateway multicast group."""

        domain_id = params.get("TransitGatewayMulticastDomainId")
        if not domain_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayMulticastDomainId")

        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        network_interface_ids = params.get("NetworkInterfaceIds.N", []) or []
        for network_interface_id in network_interface_ids:
            if not self.state.elastic_network_interfaces.get(network_interface_id):
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        group_ip_address = params.get("GroupIpAddress") or ""
        remaining_members = []
        deregistered = []
        for member in getattr(domain, "multicast_group_members", []) or []:
            if member.get("networkInterfaceId") in network_interface_ids and member.get("groupIpAddress") == group_ip_address:
                deregistered.append(member.get("networkInterfaceId"))
                continue
            remaining_members.append(member)
        domain.multicast_group_members = remaining_members

        return {
            'deregisteredMulticastGroupMembers': {
                'deregisteredNetworkInterfaceIds': deregistered,
                'groupIpAddress': group_ip_address,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def DeregisterTransitGatewayMulticastGroupSources(self, params: Dict[str, Any]):
        """Deregisters the specified sources (network interfaces) from the  transit gateway multicast group."""

        domain_id = params.get("TransitGatewayMulticastDomainId")
        if not domain_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayMulticastDomainId")

        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        network_interface_ids = params.get("NetworkInterfaceIds.N", []) or []
        for network_interface_id in network_interface_ids:
            if not self.state.elastic_network_interfaces.get(network_interface_id):
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        group_ip_address = params.get("GroupIpAddress") or ""
        remaining_sources = []
        deregistered = []
        for source in getattr(domain, "multicast_group_sources", []) or []:
            if source.get("networkInterfaceId") in network_interface_ids and source.get("groupIpAddress") == group_ip_address:
                deregistered.append(source.get("networkInterfaceId"))
                continue
            remaining_sources.append(source)
        domain.multicast_group_sources = remaining_sources

        return {
            'deregisteredMulticastGroupSources': {
                'deregisteredNetworkInterfaceIds': deregistered,
                'groupIpAddress': group_ip_address,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def DescribeTransitGatewayMulticastDomains(self, params: Dict[str, Any]):
        """Describes one or more transit gateway multicast domains."""

        domain_ids = params.get("TransitGatewayMulticastDomainIds.N", []) or []
        if domain_ids:
            missing_id = next((domain_id for domain_id in domain_ids if domain_id not in self.resources), None)
            if missing_id:
                return create_error_response(
                    "InvalidTransitGatewayMulticastDomainId.NotFound",
                    f"The ID '{missing_id}' does not exist",
                )
            resources = [self.resources[domain_id] for domain_id in domain_ids]
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []) or [])

        max_results = int(params.get("MaxResults") or 100)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'transitGatewayMulticastDomains': [
                {
                    'creationTime': resource.creation_time,
                    'options': {
                        'autoAcceptSharedAssociations': resource.options.get('autoAcceptSharedAssociations'),
                        'igmpv2Support': resource.options.get('igmpv2Support'),
                        'staticSourcesSupport': resource.options.get('staticSourcesSupport'),
                        },
                    'ownerId': resource.owner_id,
                    'state': resource.state,
                    'tagSet': resource.tag_set,
                    'transitGatewayId': resource.transit_gateway_id,
                    'transitGatewayMulticastDomainArn': resource.transit_gateway_multicast_domain_arn,
                    'transitGatewayMulticastDomainId': resource.transit_gateway_multicast_domain_id,
                    }
                for resource in resources
            ],
            }

    def DisassociateTransitGatewayMulticastDomain(self, params: Dict[str, Any]):
        """Disassociates the specified subnets from the transit gateway multicast domain."""

        error = self._require_params(
            params,
            ["SubnetIds.N", "TransitGatewayAttachmentId", "TransitGatewayMulticastDomainId"],
        )
        if error:
            return error

        domain_id = params.get("TransitGatewayMulticastDomainId")
        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment, error = self._get_or_error(
            self.state.transit_gateway_connect,
            attachment_id,
            "InvalidTransitGatewayAttachmentID.NotFound",
            f"The ID '{attachment_id}' does not exist",
        )
        if error:
            return error

        subnet_ids = params.get("SubnetIds.N", []) or []
        for subnet_id in subnet_ids:
            if not self.state.subnets.get(subnet_id):
                return create_error_response(
                    "InvalidSubnetID.NotFound",
                    f"The ID '{subnet_id}' does not exist",
                )

        associations = getattr(domain, "associations", []) or []
        remaining = []
        for association in associations:
            if association.get("subnetId") not in subnet_ids:
                remaining.append(association)
        domain.associations = remaining

        first_subnet = self.state.subnets.get(subnet_ids[0]) if subnet_ids else None
        return {
            'associations': {
                'resourceId': subnet_ids[0] if subnet_ids else "",
                'resourceOwnerId': getattr(first_subnet, "owner_id", "") if first_subnet else "",
                'resourceType': "subnet" if subnet_ids else "",
                'subnets': [{"state": "disassociated", "subnetId": subnet_id} for subnet_id in subnet_ids],
                'transitGatewayAttachmentId': attachment_id,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def GetTransitGatewayMulticastDomainAssociations(self, params: Dict[str, Any]):
        """Gets information about the associations for the transit gateway multicast domain."""

        error = self._require_params(params, ["TransitGatewayMulticastDomainId"])
        if error:
            return error

        domain_id = params.get("TransitGatewayMulticastDomainId")
        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        associations = apply_filters(getattr(domain, "associations", []) or [], params.get("Filter.N", []) or [])
        max_results = int(params.get("MaxResults") or 100)
        associations = associations[:max_results]

        response_associations = []
        for association in associations:
            subnet_id = association.get("subnetId", "")
            response_associations.append(
                {
                    "resourceId": association.get("resourceId", subnet_id),
                    "resourceOwnerId": association.get("resourceOwnerId", ""),
                    "resourceType": association.get("resourceType", "subnet"),
                    "subnet": {
                        "subnetId": subnet_id,
                        "state": association.get("state", "")
                    },
                    "transitGatewayAttachmentId": association.get("transitGatewayAttachmentId", ""),
                }
            )

        return {
            'multicastDomainAssociations': response_associations,
            'nextToken': None,
            }

    def RegisterTransitGatewayMulticastGroupMembers(self, params: Dict[str, Any]):
        """Registers members (network interfaces) with the  transit gateway multicast group. A member is a network interface associated
            with a supported EC2 instance that receives multicast traffic. For more information, seeMulticast
                on transit gatewaysin theAWS Transit Gateways Gui"""

        error = self._require_params(params, ["NetworkInterfaceIds.N", "TransitGatewayMulticastDomainId"])
        if error:
            return error

        domain_id = params.get("TransitGatewayMulticastDomainId")
        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        network_interface_ids = params.get("NetworkInterfaceIds.N", []) or []
        for network_interface_id in network_interface_ids:
            if not self.state.elastic_network_interfaces.get(network_interface_id):
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        group_ip_address = params.get("GroupIpAddress") or ""
        registered_ids: List[str] = []
        existing_members = getattr(domain, "multicast_group_members", [])
        for network_interface_id in network_interface_ids:
            duplicate = False
            for member in existing_members:
                if (
                    member.get("networkInterfaceId") == network_interface_id
                    and member.get("groupIpAddress") == group_ip_address
                ):
                    duplicate = True
                    break
            if not duplicate:
                eni = self.state.elastic_network_interfaces.get(network_interface_id)
                member_entry = {
                    "groupIpAddress": group_ip_address,
                    "groupMember": True,
                    "groupSource": False,
                    "memberType": "network-interface",
                    "networkInterfaceId": network_interface_id,
                    "resourceId": network_interface_id,
                    "resourceOwnerId": getattr(eni, "owner_id", ""),
                    "resourceType": "network-interface",
                    "sourceType": "",
                    "subnetId": getattr(eni, "subnet_id", ""),
                    "transitGatewayAttachmentId": "",
                    "transitGatewayMulticastDomainId": domain_id,
                }
                existing_members.append(member_entry)
            registered_ids.append(network_interface_id)
        domain.multicast_group_members = existing_members

        return {
            'registeredMulticastGroupMembers': {
                'groupIpAddress': group_ip_address,
                'registeredNetworkInterfaceIds': registered_ids,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def RegisterTransitGatewayMulticastGroupSources(self, params: Dict[str, Any]):
        """Registers sources (network interfaces) with the specified  transit gateway multicast group. A multicast source is a network interface attached to a supported instance that sends
            multicast traffic. For more information about supported instances, seeMulticast
                on transit gat"""

        error = self._require_params(params, ["NetworkInterfaceIds.N", "TransitGatewayMulticastDomainId"])
        if error:
            return error

        domain_id = params.get("TransitGatewayMulticastDomainId")
        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        network_interface_ids = params.get("NetworkInterfaceIds.N", []) or []
        for network_interface_id in network_interface_ids:
            if not self.state.elastic_network_interfaces.get(network_interface_id):
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        group_ip_address = params.get("GroupIpAddress") or ""
        registered_ids: List[str] = []
        existing_sources = getattr(domain, "multicast_group_sources", [])
        for network_interface_id in network_interface_ids:
            duplicate = False
            for source in existing_sources:
                if (
                    source.get("networkInterfaceId") == network_interface_id
                    and source.get("groupIpAddress") == group_ip_address
                ):
                    duplicate = True
                    break
            if not duplicate:
                eni = self.state.elastic_network_interfaces.get(network_interface_id)
                source_entry = {
                    "groupIpAddress": group_ip_address,
                    "groupMember": False,
                    "groupSource": True,
                    "memberType": "network-interface",
                    "networkInterfaceId": network_interface_id,
                    "resourceId": network_interface_id,
                    "resourceOwnerId": getattr(eni, "owner_id", ""),
                    "resourceType": "network-interface",
                    "sourceType": "",
                    "subnetId": getattr(eni, "subnet_id", ""),
                    "transitGatewayAttachmentId": "",
                    "transitGatewayMulticastDomainId": domain_id,
                }
                existing_sources.append(source_entry)
            registered_ids.append(network_interface_id)
        domain.multicast_group_sources = existing_sources

        return {
            'registeredMulticastGroupSources': {
                'groupIpAddress': group_ip_address,
                'registeredNetworkInterfaceIds': registered_ids,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def RejectTransitGatewayMulticastDomainAssociations(self, params: Dict[str, Any]):
        """Rejects a request to associate cross-account subnets with a transit gateway multicast domain."""

        domain_id = params.get("TransitGatewayMulticastDomainId")
        if not domain_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayMulticastDomainId")

        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        attachment, error = self._get_or_error(
            self.state.transit_gateway_connect,
            attachment_id,
            "InvalidTransitGatewayAttachmentID.NotFound",
            f"The ID '{attachment_id}' does not exist",
        )
        if error:
            return error

        subnet_ids = params.get("SubnetIds.N", []) or []
        for subnet_id in subnet_ids:
            if not self.state.subnets.get(subnet_id):
                return create_error_response(
                    "InvalidSubnetID.NotFound",
                    f"The ID '{subnet_id}' does not exist",
                )

        associations = getattr(domain, "associations", []) or []
        remaining = []
        for association in associations:
            if association.get("subnetId") in subnet_ids:
                continue
            remaining.append(association)
        domain.associations = remaining

        first_subnet = self.state.subnets.get(subnet_ids[0]) if subnet_ids else None
        return {
            'associations': {
                'resourceId': subnet_ids[0] if subnet_ids else "",
                'resourceOwnerId': getattr(first_subnet, "owner_id", "") if first_subnet else "",
                'resourceType': "subnet" if subnet_ids else "",
                'subnets': [{"state": "rejected", "subnetId": subnet_id} for subnet_id in subnet_ids],
                'transitGatewayAttachmentId': attachment_id,
                'transitGatewayMulticastDomainId': domain_id,
                },
            }

    def SearchTransitGatewayMulticastGroups(self, params: Dict[str, Any]):
        """Searches one or more  transit gateway multicast groups and returns the group membership information."""

        error = self._require_params(params, ["TransitGatewayMulticastDomainId"])
        if error:
            return error

        domain_id = params.get("TransitGatewayMulticastDomainId")
        domain, error = self._get_or_error(
            self.resources,
            domain_id,
            "InvalidTransitGatewayMulticastDomainId.NotFound",
            f"The ID '{domain_id}' does not exist",
        )
        if error:
            return error

        multicast_groups = (getattr(domain, "multicast_group_members", []) or []) + (
            getattr(domain, "multicast_group_sources", []) or []
        )
        multicast_groups = apply_filters(multicast_groups, params.get("Filter.N", []) or [])

        max_results = int(params.get("MaxResults") or 100)
        multicast_groups = multicast_groups[:max_results]

        response_groups = []
        for group in multicast_groups:
            response_groups.append(
                {
                    "groupIpAddress": group.get("groupIpAddress", ""),
                    "groupMember": group.get("groupMember", False),
                    "groupSource": group.get("groupSource", False),
                    "memberType": group.get("memberType", ""),
                    "networkInterfaceId": group.get("networkInterfaceId", ""),
                    "resourceId": group.get("resourceId", ""),
                    "resourceOwnerId": group.get("resourceOwnerId", ""),
                    "resourceType": group.get("resourceType", ""),
                    "sourceType": group.get("sourceType", ""),
                    "subnetId": group.get("subnetId", ""),
                    "transitGatewayAttachmentId": group.get("transitGatewayAttachmentId", ""),
                }
            )

        return {
            'multicastGroups': response_groups,
            'nextToken': None,
            }

    def _generate_id(self, prefix: str = 'eni') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class transitgatewaymulticast_RequestParser:
    @staticmethod
    def parse_accept_transit_gateway_multicast_domain_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SubnetIds.N": get_indexed_list(md, "SubnetIds"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_associate_transit_gateway_multicast_domain_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SubnetIds.N": get_indexed_list(md, "SubnetIds"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_create_transit_gateway_multicast_domain_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_multicast_domain_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_deregister_transit_gateway_multicast_group_members_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GroupIpAddress": get_scalar(md, "GroupIpAddress"),
            "NetworkInterfaceIds.N": get_indexed_list(md, "NetworkInterfaceIds"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_deregister_transit_gateway_multicast_group_sources_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GroupIpAddress": get_scalar(md, "GroupIpAddress"),
            "NetworkInterfaceIds.N": get_indexed_list(md, "NetworkInterfaceIds"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_describe_transit_gateway_multicast_domains_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayMulticastDomainIds.N": get_indexed_list(md, "TransitGatewayMulticastDomainIds"),
        }

    @staticmethod
    def parse_disassociate_transit_gateway_multicast_domain_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SubnetIds.N": get_indexed_list(md, "SubnetIds"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_get_transit_gateway_multicast_domain_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_register_transit_gateway_multicast_group_members_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GroupIpAddress": get_scalar(md, "GroupIpAddress"),
            "NetworkInterfaceIds.N": get_indexed_list(md, "NetworkInterfaceIds"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_register_transit_gateway_multicast_group_sources_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GroupIpAddress": get_scalar(md, "GroupIpAddress"),
            "NetworkInterfaceIds.N": get_indexed_list(md, "NetworkInterfaceIds"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_reject_transit_gateway_multicast_domain_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SubnetIds.N": get_indexed_list(md, "SubnetIds"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_search_transit_gateway_multicast_groups_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayMulticastDomainId": get_scalar(md, "TransitGatewayMulticastDomainId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AcceptTransitGatewayMulticastDomainAssociations": transitgatewaymulticast_RequestParser.parse_accept_transit_gateway_multicast_domain_associations_request,
            "AssociateTransitGatewayMulticastDomain": transitgatewaymulticast_RequestParser.parse_associate_transit_gateway_multicast_domain_request,
            "CreateTransitGatewayMulticastDomain": transitgatewaymulticast_RequestParser.parse_create_transit_gateway_multicast_domain_request,
            "DeleteTransitGatewayMulticastDomain": transitgatewaymulticast_RequestParser.parse_delete_transit_gateway_multicast_domain_request,
            "DeregisterTransitGatewayMulticastGroupMembers": transitgatewaymulticast_RequestParser.parse_deregister_transit_gateway_multicast_group_members_request,
            "DeregisterTransitGatewayMulticastGroupSources": transitgatewaymulticast_RequestParser.parse_deregister_transit_gateway_multicast_group_sources_request,
            "DescribeTransitGatewayMulticastDomains": transitgatewaymulticast_RequestParser.parse_describe_transit_gateway_multicast_domains_request,
            "DisassociateTransitGatewayMulticastDomain": transitgatewaymulticast_RequestParser.parse_disassociate_transit_gateway_multicast_domain_request,
            "GetTransitGatewayMulticastDomainAssociations": transitgatewaymulticast_RequestParser.parse_get_transit_gateway_multicast_domain_associations_request,
            "RegisterTransitGatewayMulticastGroupMembers": transitgatewaymulticast_RequestParser.parse_register_transit_gateway_multicast_group_members_request,
            "RegisterTransitGatewayMulticastGroupSources": transitgatewaymulticast_RequestParser.parse_register_transit_gateway_multicast_group_sources_request,
            "RejectTransitGatewayMulticastDomainAssociations": transitgatewaymulticast_RequestParser.parse_reject_transit_gateway_multicast_domain_associations_request,
            "SearchTransitGatewayMulticastGroups": transitgatewaymulticast_RequestParser.parse_search_transit_gateway_multicast_groups_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class transitgatewaymulticast_ResponseSerializer:
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
                xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_accept_transit_gateway_multicast_domain_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AcceptTransitGatewayMulticastDomainAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</associationsSet>')
            else:
                xml_parts.append(f'{indent_str}<associationsSet/>')
        xml_parts.append(f'</AcceptTransitGatewayMulticastDomainAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_associate_transit_gateway_multicast_domain_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateTransitGatewayMulticastDomainResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</associationsSet>')
            else:
                xml_parts.append(f'{indent_str}<associationsSet/>')
        xml_parts.append(f'</AssociateTransitGatewayMulticastDomainResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_multicast_domain_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayMulticastDomainResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayMulticastDomain
        _transitGatewayMulticastDomain_key = None
        if "transitGatewayMulticastDomain" in data:
            _transitGatewayMulticastDomain_key = "transitGatewayMulticastDomain"
        elif "TransitGatewayMulticastDomain" in data:
            _transitGatewayMulticastDomain_key = "TransitGatewayMulticastDomain"
        if _transitGatewayMulticastDomain_key:
            param_data = data[_transitGatewayMulticastDomain_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayMulticastDomain>')
            xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayMulticastDomain>')
        xml_parts.append(f'</CreateTransitGatewayMulticastDomainResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_multicast_domain_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayMulticastDomainResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayMulticastDomain
        _transitGatewayMulticastDomain_key = None
        if "transitGatewayMulticastDomain" in data:
            _transitGatewayMulticastDomain_key = "transitGatewayMulticastDomain"
        elif "TransitGatewayMulticastDomain" in data:
            _transitGatewayMulticastDomain_key = "TransitGatewayMulticastDomain"
        if _transitGatewayMulticastDomain_key:
            param_data = data[_transitGatewayMulticastDomain_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayMulticastDomain>')
            xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayMulticastDomain>')
        xml_parts.append(f'</DeleteTransitGatewayMulticastDomainResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_deregister_transit_gateway_multicast_group_members_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeregisterTransitGatewayMulticastGroupMembersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize deregisteredMulticastGroupMembers
        _deregisteredMulticastGroupMembers_key = None
        if "deregisteredMulticastGroupMembers" in data:
            _deregisteredMulticastGroupMembers_key = "deregisteredMulticastGroupMembers"
        elif "DeregisteredMulticastGroupMembers" in data:
            _deregisteredMulticastGroupMembers_key = "DeregisteredMulticastGroupMembers"
        if _deregisteredMulticastGroupMembers_key:
            param_data = data[_deregisteredMulticastGroupMembers_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<deregisteredMulticastGroupMembersSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</deregisteredMulticastGroupMembersSet>')
            else:
                xml_parts.append(f'{indent_str}<deregisteredMulticastGroupMembersSet/>')
        xml_parts.append(f'</DeregisterTransitGatewayMulticastGroupMembersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_deregister_transit_gateway_multicast_group_sources_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeregisterTransitGatewayMulticastGroupSourcesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize deregisteredMulticastGroupSources
        _deregisteredMulticastGroupSources_key = None
        if "deregisteredMulticastGroupSources" in data:
            _deregisteredMulticastGroupSources_key = "deregisteredMulticastGroupSources"
        elif "DeregisteredMulticastGroupSources" in data:
            _deregisteredMulticastGroupSources_key = "DeregisteredMulticastGroupSources"
        if _deregisteredMulticastGroupSources_key:
            param_data = data[_deregisteredMulticastGroupSources_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<deregisteredMulticastGroupSourcesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</deregisteredMulticastGroupSourcesSet>')
            else:
                xml_parts.append(f'{indent_str}<deregisteredMulticastGroupSourcesSet/>')
        xml_parts.append(f'</DeregisterTransitGatewayMulticastGroupSourcesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_multicast_domains_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayMulticastDomainsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayMulticastDomains
        _transitGatewayMulticastDomains_key = None
        if "transitGatewayMulticastDomains" in data:
            _transitGatewayMulticastDomains_key = "transitGatewayMulticastDomains"
        elif "TransitGatewayMulticastDomains" in data:
            _transitGatewayMulticastDomains_key = "TransitGatewayMulticastDomains"
        if _transitGatewayMulticastDomains_key:
            param_data = data[_transitGatewayMulticastDomains_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayMulticastDomainsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayMulticastDomainsSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayMulticastDomainsSet/>')
        xml_parts.append(f'</DescribeTransitGatewayMulticastDomainsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_transit_gateway_multicast_domain_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateTransitGatewayMulticastDomainResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</associationsSet>')
            else:
                xml_parts.append(f'{indent_str}<associationsSet/>')
        xml_parts.append(f'</DisassociateTransitGatewayMulticastDomainResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_transit_gateway_multicast_domain_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetTransitGatewayMulticastDomainAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize multicastDomainAssociations
        _multicastDomainAssociations_key = None
        if "multicastDomainAssociations" in data:
            _multicastDomainAssociations_key = "multicastDomainAssociations"
        elif "MulticastDomainAssociations" in data:
            _multicastDomainAssociations_key = "MulticastDomainAssociations"
        if _multicastDomainAssociations_key:
            param_data = data[_multicastDomainAssociations_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<multicastDomainAssociationsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</multicastDomainAssociationsSet>')
            else:
                xml_parts.append(f'{indent_str}<multicastDomainAssociationsSet/>')
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
        xml_parts.append(f'</GetTransitGatewayMulticastDomainAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_register_transit_gateway_multicast_group_members_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RegisterTransitGatewayMulticastGroupMembersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize registeredMulticastGroupMembers
        _registeredMulticastGroupMembers_key = None
        if "registeredMulticastGroupMembers" in data:
            _registeredMulticastGroupMembers_key = "registeredMulticastGroupMembers"
        elif "RegisteredMulticastGroupMembers" in data:
            _registeredMulticastGroupMembers_key = "RegisteredMulticastGroupMembers"
        if _registeredMulticastGroupMembers_key:
            param_data = data[_registeredMulticastGroupMembers_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<registeredMulticastGroupMembersSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</registeredMulticastGroupMembersSet>')
            else:
                xml_parts.append(f'{indent_str}<registeredMulticastGroupMembersSet/>')
        xml_parts.append(f'</RegisterTransitGatewayMulticastGroupMembersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_register_transit_gateway_multicast_group_sources_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RegisterTransitGatewayMulticastGroupSourcesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize registeredMulticastGroupSources
        _registeredMulticastGroupSources_key = None
        if "registeredMulticastGroupSources" in data:
            _registeredMulticastGroupSources_key = "registeredMulticastGroupSources"
        elif "RegisteredMulticastGroupSources" in data:
            _registeredMulticastGroupSources_key = "RegisteredMulticastGroupSources"
        if _registeredMulticastGroupSources_key:
            param_data = data[_registeredMulticastGroupSources_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<registeredMulticastGroupSourcesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</registeredMulticastGroupSourcesSet>')
            else:
                xml_parts.append(f'{indent_str}<registeredMulticastGroupSourcesSet/>')
        xml_parts.append(f'</RegisterTransitGatewayMulticastGroupSourcesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reject_transit_gateway_multicast_domain_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RejectTransitGatewayMulticastDomainAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</associationsSet>')
            else:
                xml_parts.append(f'{indent_str}<associationsSet/>')
        xml_parts.append(f'</RejectTransitGatewayMulticastDomainAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_search_transit_gateway_multicast_groups_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<SearchTransitGatewayMulticastGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize multicastGroups
        _multicastGroups_key = None
        if "multicastGroups" in data:
            _multicastGroups_key = "multicastGroups"
        elif "MulticastGroups" in data:
            _multicastGroups_key = "MulticastGroups"
        if _multicastGroups_key:
            param_data = data[_multicastGroups_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<multicastGroupsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaymulticast_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</multicastGroupsSet>')
            else:
                xml_parts.append(f'{indent_str}<multicastGroupsSet/>')
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
        xml_parts.append(f'</SearchTransitGatewayMulticastGroupsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AcceptTransitGatewayMulticastDomainAssociations": transitgatewaymulticast_ResponseSerializer.serialize_accept_transit_gateway_multicast_domain_associations_response,
            "AssociateTransitGatewayMulticastDomain": transitgatewaymulticast_ResponseSerializer.serialize_associate_transit_gateway_multicast_domain_response,
            "CreateTransitGatewayMulticastDomain": transitgatewaymulticast_ResponseSerializer.serialize_create_transit_gateway_multicast_domain_response,
            "DeleteTransitGatewayMulticastDomain": transitgatewaymulticast_ResponseSerializer.serialize_delete_transit_gateway_multicast_domain_response,
            "DeregisterTransitGatewayMulticastGroupMembers": transitgatewaymulticast_ResponseSerializer.serialize_deregister_transit_gateway_multicast_group_members_response,
            "DeregisterTransitGatewayMulticastGroupSources": transitgatewaymulticast_ResponseSerializer.serialize_deregister_transit_gateway_multicast_group_sources_response,
            "DescribeTransitGatewayMulticastDomains": transitgatewaymulticast_ResponseSerializer.serialize_describe_transit_gateway_multicast_domains_response,
            "DisassociateTransitGatewayMulticastDomain": transitgatewaymulticast_ResponseSerializer.serialize_disassociate_transit_gateway_multicast_domain_response,
            "GetTransitGatewayMulticastDomainAssociations": transitgatewaymulticast_ResponseSerializer.serialize_get_transit_gateway_multicast_domain_associations_response,
            "RegisterTransitGatewayMulticastGroupMembers": transitgatewaymulticast_ResponseSerializer.serialize_register_transit_gateway_multicast_group_members_response,
            "RegisterTransitGatewayMulticastGroupSources": transitgatewaymulticast_ResponseSerializer.serialize_register_transit_gateway_multicast_group_sources_response,
            "RejectTransitGatewayMulticastDomainAssociations": transitgatewaymulticast_ResponseSerializer.serialize_reject_transit_gateway_multicast_domain_associations_response,
            "SearchTransitGatewayMulticastGroups": transitgatewaymulticast_ResponseSerializer.serialize_search_transit_gateway_multicast_groups_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

