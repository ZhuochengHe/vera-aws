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
class LocalGateway:
    local_gateway_id: str = ""
    outpost_arn: str = ""
    owner_id: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)

    # Internal dependency tracking — not in API response
    route_table_ids: List[str] = field(default_factory=list)  # tracks RouteTable children

    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "localGatewayId": self.local_gateway_id,
            "outpostArn": self.outpost_arn,
            "ownerId": self.owner_id,
            "state": self.state,
            "tagSet": self.tag_set,
        }

class LocalGateway_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.local_gateways  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            value = params.get(name)
            if value is None or value == "":
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_store(self, attr_name: str) -> Dict[str, Any]:
        store = getattr(self.state, attr_name, None)
        if store is None:
            store = {}
            setattr(self.state, attr_name, store)
        return store

    def _get_or_error(self, store: Dict[str, Any], resource_id: str, code: str, message: str):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(code, message)
        return resource, None

    def _extract_tag_set(self, tag_specs: List[Dict[str, Any]], resource_type: str):
        for spec in tag_specs or []:
            if spec.get("ResourceType") == resource_type:
                tags = spec.get("Tags", []) or []
                tag_map = {tag.get("Key"): tag.get("Value", "") for tag in tags if tag.get("Key")}
                return tags, tag_map
        return [], {}

    def CreateLocalGatewayRoute(self, params: Dict[str, Any]):
        """Creates a static route for the specified local gateway route table. You must specify one of the 
         following targets: LocalGatewayVirtualInterfaceGroupId NetworkInterfaceId"""

        error = self._require_params(params, ["LocalGatewayRouteTableId"])
        if error:
            return error

        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        route_table_store = self._get_store("local_gateway_route_tables")
        route_table = route_table_store.get(local_gateway_route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{local_gateway_route_table_id}' does not exist.",
            )

        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")
        if not destination_cidr_block and not destination_prefix_list_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: DestinationCidrBlock or DestinationPrefixListId",
            )

        local_gateway_virtual_interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        network_interface_id = params.get("NetworkInterfaceId")
        if not local_gateway_virtual_interface_group_id and not network_interface_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: LocalGatewayVirtualInterfaceGroupId or NetworkInterfaceId",
            )

        if local_gateway_virtual_interface_group_id:
            interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
            if local_gateway_virtual_interface_group_id not in interface_group_store:
                return create_error_response(
                    "InvalidLocalGatewayVirtualInterfaceGroupId.NotFound",
                    f"The ID '{local_gateway_virtual_interface_group_id}' does not exist",
                )

        if network_interface_id:
            network_interface = self.state.elastic_network_interfaces.get(network_interface_id)
            if not network_interface:
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        local_gateway_id = route_table.get("localGatewayId")
        local_gateway = self.resources.get(local_gateway_id) if local_gateway_id else None
        owner_id = route_table.get("ownerId") or (local_gateway.owner_id if local_gateway else "")
        route_table_arn = route_table.get("localGatewayRouteTableArn")

        route = {
            "coipPoolId": None,
            "destinationCidrBlock": destination_cidr_block,
            "destinationPrefixListId": destination_prefix_list_id,
            "localGatewayRouteTableArn": route_table_arn,
            "localGatewayRouteTableId": local_gateway_route_table_id,
            "localGatewayVirtualInterfaceGroupId": local_gateway_virtual_interface_group_id,
            "networkInterfaceId": network_interface_id,
            "ownerId": owner_id,
            "state": "active",
            "subnetId": None,
            "type": "static",
        }

        route_list = route_table.setdefault("route_set", [])
        route_list[:] = [
            existing
            for existing in route_list
            if not (
                existing.get("destinationCidrBlock") == destination_cidr_block
                and existing.get("destinationPrefixListId") == destination_prefix_list_id
            )
        ]
        route_list.append(route)

        return {
            'route': route,
            }

    def CreateLocalGatewayRouteTable(self, params: Dict[str, Any]):
        """Creates a local gateway route table."""

        error = self._require_params(params, ["LocalGatewayId"])
        if error:
            return error

        local_gateway_id = params.get("LocalGatewayId")
        local_gateway = self.resources.get(local_gateway_id)
        if not local_gateway:
            return create_error_response(
                "InvalidLocalGatewayId.NotFound",
                f"The ID '{local_gateway_id}' does not exist",
            )

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set, tag_map = self._extract_tag_set(tag_specs, "local-gateway-route-table")

        route_table_id = self._generate_id("rtb")
        route_table_arn = f"arn:aws:ec2:::local-gateway-route-table/{route_table_id}"
        mode = params.get("Mode") or "direct"
        route_table = {
            "localGatewayId": local_gateway_id,
            "localGatewayRouteTableArn": route_table_arn,
            "localGatewayRouteTableId": route_table_id,
            "mode": mode,
            "outpostArn": local_gateway.outpost_arn,
            "ownerId": local_gateway.owner_id,
            "state": "available",
            "stateReason": {"code": "", "message": ""},
            "tagSet": tag_set,
            "tag_map": tag_map,
            "route_set": [],
        }

        route_table_store = self._get_store("local_gateway_route_tables")
        route_table_store[route_table_id] = route_table
        if route_table_id not in local_gateway.route_table_ids:
            local_gateway.route_table_ids.append(route_table_id)

        return {
            'localGatewayRouteTable': {
                'localGatewayId': route_table["localGatewayId"],
                'localGatewayRouteTableArn': route_table["localGatewayRouteTableArn"],
                'localGatewayRouteTableId': route_table["localGatewayRouteTableId"],
                'mode': route_table["mode"],
                'outpostArn': route_table["outpostArn"],
                'ownerId': route_table["ownerId"],
                'state': route_table["state"],
                'stateReason': route_table["stateReason"],
                'tagSet': route_table["tagSet"],
                },
            }

    def CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociation(self, params: Dict[str, Any]):
        """Creates a local gateway route table virtual interface group association."""

        error = self._require_params(params, ["LocalGatewayRouteTableId", "LocalGatewayVirtualInterfaceGroupId"])
        if error:
            return error

        route_table_id = params.get("LocalGatewayRouteTableId")
        route_table_store = self._get_store("local_gateway_route_tables")
        route_table = route_table_store.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{route_table_id}' does not exist.",
            )

        interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
        interface_group = interface_group_store.get(interface_group_id)
        if not interface_group:
            return create_error_response(
                "InvalidLocalGatewayVirtualInterfaceGroupId.NotFound",
                f"The ID '{interface_group_id}' does not exist",
            )

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set, tag_map = self._extract_tag_set(
            tag_specs, "local-gateway-route-table-virtual-interface-group-association"
        )

        association_id = self._generate_id("lgw-vif-grp-assoc")
        association = {
            "localGatewayId": route_table.get("localGatewayId"),
            "localGatewayRouteTableArn": route_table.get("localGatewayRouteTableArn"),
            "localGatewayRouteTableId": route_table_id,
            "localGatewayRouteTableVirtualInterfaceGroupAssociationId": association_id,
            "localGatewayVirtualInterfaceGroupId": interface_group_id,
            "ownerId": route_table.get("ownerId"),
            "state": "associated",
            "tagSet": tag_set,
            "tag_map": tag_map,
        }

        association_store = self._get_store("local_gateway_route_table_virtual_interface_group_associations")
        association_store[association_id] = association
        association_ids = route_table.setdefault("virtual_interface_group_association_ids", [])
        if association_id not in association_ids:
            association_ids.append(association_id)

        return {
            'localGatewayRouteTableVirtualInterfaceGroupAssociation': {
                'localGatewayId': association["localGatewayId"],
                'localGatewayRouteTableArn': association["localGatewayRouteTableArn"],
                'localGatewayRouteTableId': association["localGatewayRouteTableId"],
                'localGatewayRouteTableVirtualInterfaceGroupAssociationId': association[
                    "localGatewayRouteTableVirtualInterfaceGroupAssociationId"
                ],
                'localGatewayVirtualInterfaceGroupId': association["localGatewayVirtualInterfaceGroupId"],
                'ownerId': association["ownerId"],
                'state': association["state"],
                'tagSet': association["tagSet"],
                },
            }

    def CreateLocalGatewayVirtualInterface(self, params: Dict[str, Any]):
        """Create a virtual interface for a local gateway."""

        error = self._require_params(
            params,
            [
                "LocalAddress",
                "LocalGatewayVirtualInterfaceGroupId",
                "OutpostLagId",
                "PeerAddress",
                "Vlan",
            ],
        )
        if error:
            return error

        interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
        interface_group = interface_group_store.get(interface_group_id)
        if not interface_group:
            return create_error_response(
                "InvalidLocalGatewayVirtualInterfaceGroupId.NotFound",
                f"The ID '{interface_group_id}' does not exist",
            )

        local_gateway_id = interface_group.get("localGatewayId")
        local_gateway = self.resources.get(local_gateway_id) if local_gateway_id else None
        if not local_gateway:
            return create_error_response(
                "InvalidLocalGatewayId.NotFound",
                f"The ID '{local_gateway_id}' does not exist",
            )

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set, tag_map = self._extract_tag_set(tag_specs, "local-gateway-virtual-interface")

        virtual_interface_id = self._generate_id("lgw-vif")
        virtual_interface_arn = f"arn:aws:ec2:::local-gateway-virtual-interface/{virtual_interface_id}"
        local_address = params.get("LocalAddress")
        peer_address = params.get("PeerAddress")
        outpost_lag_id = params.get("OutpostLagId")
        peer_bgp_asn = params.get("PeerBgpAsn")
        peer_bgp_asn_extended = params.get("PeerBgpAsnExtended")
        vlan = params.get("Vlan")

        virtual_interface = {
            "configurationState": "available",
            "localAddress": local_address,
            "localBgpAsn": interface_group.get("localBgpAsn"),
            "localGatewayId": local_gateway_id,
            "localGatewayVirtualInterfaceArn": virtual_interface_arn,
            "localGatewayVirtualInterfaceGroupId": interface_group_id,
            "localGatewayVirtualInterfaceId": virtual_interface_id,
            "outpostLagId": outpost_lag_id,
            "ownerId": local_gateway.owner_id,
            "peerAddress": peer_address,
            "peerBgpAsn": peer_bgp_asn,
            "peerBgpAsnExtended": peer_bgp_asn_extended,
            "tagSet": tag_set,
            "tag_map": tag_map,
            "vlan": int(vlan) if vlan is not None else None,
        }

        interface_store = self._get_store("local_gateway_virtual_interfaces")
        interface_store[virtual_interface_id] = virtual_interface

        interface_ids = interface_group.setdefault("localGatewayVirtualInterfaceIdSet", [])
        if virtual_interface_id not in interface_ids:
            interface_ids.append(virtual_interface_id)

        return {
            'localGatewayVirtualInterface': {
                'configurationState': virtual_interface["configurationState"],
                'localAddress': virtual_interface["localAddress"],
                'localBgpAsn': virtual_interface["localBgpAsn"],
                'localGatewayId': virtual_interface["localGatewayId"],
                'localGatewayVirtualInterfaceArn': virtual_interface["localGatewayVirtualInterfaceArn"],
                'localGatewayVirtualInterfaceGroupId': virtual_interface["localGatewayVirtualInterfaceGroupId"],
                'localGatewayVirtualInterfaceId': virtual_interface["localGatewayVirtualInterfaceId"],
                'outpostLagId': virtual_interface["outpostLagId"],
                'ownerId': virtual_interface["ownerId"],
                'peerAddress': virtual_interface["peerAddress"],
                'peerBgpAsn': virtual_interface["peerBgpAsn"],
                'peerBgpAsnExtended': virtual_interface["peerBgpAsnExtended"],
                'tagSet': virtual_interface["tagSet"],
                'vlan': virtual_interface["vlan"],
                },
            }

    def CreateLocalGatewayRouteTableVpcAssociation(self, params: Dict[str, Any]):
        """Associates the specified VPC with the specified local gateway route table."""

        error = self._require_params(params, ["LocalGatewayRouteTableId", "VpcId"])
        if error:
            return error

        route_table_id = params.get("LocalGatewayRouteTableId")
        route_table_store = self._get_store("local_gateway_route_tables")
        route_table = route_table_store.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{route_table_id}' does not exist.",
            )

        vpc_id = params.get("VpcId")
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set, tag_map = self._extract_tag_set(tag_specs, "local-gateway-route-table-vpc-association")

        association_id = self._generate_id("lgw-vpc-assoc")
        association = {
            "localGatewayId": route_table.get("localGatewayId"),
            "localGatewayRouteTableArn": route_table.get("localGatewayRouteTableArn"),
            "localGatewayRouteTableId": route_table_id,
            "localGatewayRouteTableVpcAssociationId": association_id,
            "ownerId": route_table.get("ownerId"),
            "state": "associated",
            "tagSet": tag_set,
            "tag_map": tag_map,
            "vpcId": vpc_id,
        }

        association_store = self._get_store("local_gateway_route_table_vpc_associations")
        association_store[association_id] = association
        association_ids = route_table.setdefault("vpc_association_ids", [])
        if association_id not in association_ids:
            association_ids.append(association_id)

        return {
            'localGatewayRouteTableVpcAssociation': {
                'localGatewayId': association["localGatewayId"],
                'localGatewayRouteTableArn': association["localGatewayRouteTableArn"],
                'localGatewayRouteTableId': association["localGatewayRouteTableId"],
                'localGatewayRouteTableVpcAssociationId': association[
                    "localGatewayRouteTableVpcAssociationId"
                ],
                'ownerId': association["ownerId"],
                'state': association["state"],
                'tagSet': association["tagSet"],
                'vpcId': association["vpcId"],
                },
            }

    def CreateLocalGatewayVirtualInterfaceGroup(self, params: Dict[str, Any]):
        """Create a local gateway virtual interface group."""

        error = self._require_params(params, ["LocalGatewayId"])
        if error:
            return error

        local_gateway_id = params.get("LocalGatewayId")
        local_gateway = self.resources.get(local_gateway_id)
        if not local_gateway:
            return create_error_response(
                "InvalidLocalGatewayId.NotFound",
                f"The ID '{local_gateway_id}' does not exist",
            )

        tag_specs = params.get("TagSpecification.N", []) or []
        tag_set, tag_map = self._extract_tag_set(tag_specs, "local-gateway-virtual-interface-group")

        interface_group_id = self._generate_id("lgw-vif-grp")
        interface_group_arn = f"arn:aws:ec2:::local-gateway-virtual-interface-group/{interface_group_id}"
        interface_group = {
            "configurationState": "available",
            "localBgpAsn": params.get("LocalBgpAsn"),
            "localBgpAsnExtended": params.get("LocalBgpAsnExtended"),
            "localGatewayId": local_gateway_id,
            "localGatewayVirtualInterfaceGroupArn": interface_group_arn,
            "localGatewayVirtualInterfaceGroupId": interface_group_id,
            "localGatewayVirtualInterfaceIdSet": [],
            "ownerId": local_gateway.owner_id,
            "tagSet": tag_set,
            "tag_map": tag_map,
        }

        interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
        interface_group_store[interface_group_id] = interface_group

        group_ids = local_gateway.tags.setdefault("virtual_interface_group_ids", [])
        if interface_group_id not in group_ids:
            group_ids.append(interface_group_id)

        return {
            'localGatewayVirtualInterfaceGroup': {
                'configurationState': interface_group["configurationState"],
                'localBgpAsn': interface_group["localBgpAsn"],
                'localBgpAsnExtended': interface_group["localBgpAsnExtended"],
                'localGatewayId': interface_group["localGatewayId"],
                'localGatewayVirtualInterfaceGroupArn': interface_group["localGatewayVirtualInterfaceGroupArn"],
                'localGatewayVirtualInterfaceGroupId': interface_group["localGatewayVirtualInterfaceGroupId"],
                'localGatewayVirtualInterfaceIdSet': interface_group["localGatewayVirtualInterfaceIdSet"],
                'ownerId': interface_group["ownerId"],
                'tagSet': interface_group["tagSet"],
                },
            }

    def DeleteLocalGatewayRoute(self, params: Dict[str, Any]):
        """Deletes the specified route from the specified local gateway route table."""

        error = self._require_params(params, ["LocalGatewayRouteTableId"])
        if error:
            return error

        route_table_id = params.get("LocalGatewayRouteTableId")
        route_table_store = self._get_store("local_gateway_route_tables")
        route_table = route_table_store.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{route_table_id}' does not exist.",
            )

        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")
        if not destination_cidr_block and not destination_prefix_list_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: DestinationCidrBlock or DestinationPrefixListId",
            )

        route_list = route_table.get("route_set", []) or []
        route = None
        for existing in route_list:
            if existing.get("destinationCidrBlock") == destination_cidr_block and existing.get(
                "destinationPrefixListId"
            ) == destination_prefix_list_id:
                route = existing
                break

        if not route:
            return create_error_response(
                "InvalidRoute.NotFound",
                "The specified route does not exist.",
            )

        route_list.remove(route)

        return {
            'route': {
                'coipPoolId': route.get("coipPoolId"),
                'destinationCidrBlock': route.get("destinationCidrBlock"),
                'destinationPrefixListId': route.get("destinationPrefixListId"),
                'localGatewayRouteTableArn': route.get("localGatewayRouteTableArn"),
                'localGatewayRouteTableId': route.get("localGatewayRouteTableId"),
                'localGatewayVirtualInterfaceGroupId': route.get("localGatewayVirtualInterfaceGroupId"),
                'networkInterfaceId': route.get("networkInterfaceId"),
                'ownerId': route.get("ownerId"),
                'state': route.get("state"),
                'subnetId': route.get("subnetId"),
                'type': route.get("type"),
                },
            }

    def DeleteLocalGatewayRouteTable(self, params: Dict[str, Any]):
        """Deletes a local gateway route table."""

        error = self._require_params(params, ["LocalGatewayRouteTableId"])
        if error:
            return error

        route_table_id = params.get("LocalGatewayRouteTableId")
        route_table_store = self._get_store("local_gateway_route_tables")
        route_table = route_table_store.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{route_table_id}' does not exist.",
            )

        if route_table.get("vpc_association_ids"):
            return create_error_response(
                "DependencyViolation",
                "LocalGatewayRouteTable has dependent VPC association(s) and cannot be deleted.",
            )

        if route_table.get("virtual_interface_group_association_ids"):
            return create_error_response(
                "DependencyViolation",
                "LocalGatewayRouteTable has dependent virtual interface group association(s) and cannot be deleted.",
            )

        local_gateway_id = route_table.get("localGatewayId")
        if local_gateway_id:
            local_gateway = self.resources.get(local_gateway_id)
            if local_gateway and route_table_id in local_gateway.route_table_ids:
                local_gateway.route_table_ids.remove(route_table_id)

        route_table_store.pop(route_table_id, None)

        return {
            'localGatewayRouteTable': {
                'localGatewayId': route_table.get("localGatewayId"),
                'localGatewayRouteTableArn': route_table.get("localGatewayRouteTableArn"),
                'localGatewayRouteTableId': route_table.get("localGatewayRouteTableId"),
                'mode': route_table.get("mode"),
                'outpostArn': route_table.get("outpostArn"),
                'ownerId': route_table.get("ownerId"),
                'state': route_table.get("state"),
                'stateReason': route_table.get("stateReason"),
                'tagSet': route_table.get("tagSet"),
                },
            }

    def DeleteLocalGatewayRouteTableVirtualInterfaceGroupAssociation(self, params: Dict[str, Any]):
        """Deletes a local gateway route table virtual interface group association."""

        error = self._require_params(params, ["LocalGatewayRouteTableVirtualInterfaceGroupAssociationId"])
        if error:
            return error

        association_id = params.get("LocalGatewayRouteTableVirtualInterfaceGroupAssociationId")
        association_store = self._get_store("local_gateway_route_table_virtual_interface_group_associations")
        association = association_store.get(association_id)
        if not association:
            return create_error_response(
                "InvalidLocalGatewayRouteTableVirtualInterfaceGroupAssociationId.NotFound",
                f"The ID '{association_id}' does not exist",
            )

        route_table_id = association.get("localGatewayRouteTableId")
        if route_table_id:
            route_table_store = self._get_store("local_gateway_route_tables")
            route_table = route_table_store.get(route_table_id)
            if route_table:
                association_ids = route_table.get("virtual_interface_group_association_ids", [])
                if association_id in association_ids:
                    association_ids.remove(association_id)

        association_store.pop(association_id, None)

        return {
            'localGatewayRouteTableVirtualInterfaceGroupAssociation': {
                'localGatewayId': association.get("localGatewayId"),
                'localGatewayRouteTableArn': association.get("localGatewayRouteTableArn"),
                'localGatewayRouteTableId': association.get("localGatewayRouteTableId"),
                'localGatewayRouteTableVirtualInterfaceGroupAssociationId': association.get(
                    "localGatewayRouteTableVirtualInterfaceGroupAssociationId"
                ),
                'localGatewayVirtualInterfaceGroupId': association.get("localGatewayVirtualInterfaceGroupId"),
                'ownerId': association.get("ownerId"),
                'state': association.get("state"),
                'tagSet': association.get("tagSet"),
                },
            }

    def DeleteLocalGatewayRouteTableVpcAssociation(self, params: Dict[str, Any]):
        """Deletes the specified association between a VPC and local gateway route table."""

        error = self._require_params(params, ["LocalGatewayRouteTableVpcAssociationId"])
        if error:
            return error

        association_id = params.get("LocalGatewayRouteTableVpcAssociationId")
        association_store = self._get_store("local_gateway_route_table_vpc_associations")
        association = association_store.get(association_id)
        if not association:
            return create_error_response(
                "InvalidLocalGatewayRouteTableVpcAssociationId.NotFound",
                f"The ID '{association_id}' does not exist",
            )

        route_table_id = association.get("localGatewayRouteTableId")
        if route_table_id:
            route_table_store = self._get_store("local_gateway_route_tables")
            route_table = route_table_store.get(route_table_id)
            if route_table:
                association_ids = route_table.get("vpc_association_ids", [])
                if association_id in association_ids:
                    association_ids.remove(association_id)

        association_store.pop(association_id, None)

        return {
            'localGatewayRouteTableVpcAssociation': {
                'localGatewayId': association.get("localGatewayId"),
                'localGatewayRouteTableArn': association.get("localGatewayRouteTableArn"),
                'localGatewayRouteTableId': association.get("localGatewayRouteTableId"),
                'localGatewayRouteTableVpcAssociationId': association.get(
                    "localGatewayRouteTableVpcAssociationId"
                ),
                'ownerId': association.get("ownerId"),
                'state': association.get("state"),
                'tagSet': association.get("tagSet"),
                'vpcId': association.get("vpcId"),
                },
            }

    def DeleteLocalGatewayVirtualInterface(self, params: Dict[str, Any]):
        """Deletes the specified local gateway virtual interface."""

        error = self._require_params(params, ["LocalGatewayVirtualInterfaceId"])
        if error:
            return error

        virtual_interface_id = params.get("LocalGatewayVirtualInterfaceId")
        interface_store = self._get_store("local_gateway_virtual_interfaces")
        interface = interface_store.get(virtual_interface_id)
        if not interface:
            return create_error_response(
                "InvalidLocalGatewayVirtualInterfaceId.NotFound",
                f"The ID '{virtual_interface_id}' does not exist",
            )

        interface_group_id = interface.get("localGatewayVirtualInterfaceGroupId")
        if interface_group_id:
            interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
            interface_group = interface_group_store.get(interface_group_id)
            if interface_group:
                interface_ids = interface_group.get("localGatewayVirtualInterfaceIdSet", [])
                if virtual_interface_id in interface_ids:
                    interface_ids.remove(virtual_interface_id)

        interface_store.pop(virtual_interface_id, None)

        return {
            'localGatewayVirtualInterface': {
                'configurationState': interface.get("configurationState"),
                'localAddress': interface.get("localAddress"),
                'localBgpAsn': interface.get("localBgpAsn"),
                'localGatewayId': interface.get("localGatewayId"),
                'localGatewayVirtualInterfaceArn': interface.get("localGatewayVirtualInterfaceArn"),
                'localGatewayVirtualInterfaceGroupId': interface.get("localGatewayVirtualInterfaceGroupId"),
                'localGatewayVirtualInterfaceId': interface.get("localGatewayVirtualInterfaceId"),
                'outpostLagId': interface.get("outpostLagId"),
                'ownerId': interface.get("ownerId"),
                'peerAddress': interface.get("peerAddress"),
                'peerBgpAsn': interface.get("peerBgpAsn"),
                'peerBgpAsnExtended': interface.get("peerBgpAsnExtended"),
                'tagSet': interface.get("tagSet"),
                'vlan': interface.get("vlan"),
                },
            }

    def DeleteLocalGatewayVirtualInterfaceGroup(self, params: Dict[str, Any]):
        """Delete the specified local gateway interface group."""

        error = self._require_params(params, ["LocalGatewayVirtualInterfaceGroupId"])
        if error:
            return error

        interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
        interface_group = interface_group_store.get(interface_group_id)
        if not interface_group:
            return create_error_response(
                "InvalidLocalGatewayVirtualInterfaceGroupId.NotFound",
                f"The ID '{interface_group_id}' does not exist",
            )

        if interface_group.get("localGatewayVirtualInterfaceIdSet"):
            return create_error_response(
                "DependencyViolation",
                "LocalGatewayVirtualInterfaceGroup has dependent virtual interface(s) and cannot be deleted.",
            )

        local_gateway_id = interface_group.get("localGatewayId")
        if local_gateway_id:
            local_gateway = self.resources.get(local_gateway_id)
            if local_gateway:
                group_ids = local_gateway.tags.get("virtual_interface_group_ids", [])
                if interface_group_id in group_ids:
                    group_ids.remove(interface_group_id)

        interface_group_store.pop(interface_group_id, None)

        return {
            'localGatewayVirtualInterfaceGroup': {
                'configurationState': interface_group.get("configurationState"),
                'localBgpAsn': interface_group.get("localBgpAsn"),
                'localBgpAsnExtended': interface_group.get("localBgpAsnExtended"),
                'localGatewayId': interface_group.get("localGatewayId"),
                'localGatewayVirtualInterfaceGroupArn': interface_group.get(
                    "localGatewayVirtualInterfaceGroupArn"
                ),
                'localGatewayVirtualInterfaceGroupId': interface_group.get(
                    "localGatewayVirtualInterfaceGroupId"
                ),
                'localGatewayVirtualInterfaceIdSet': interface_group.get(
                    "localGatewayVirtualInterfaceIdSet"
                ),
                'ownerId': interface_group.get("ownerId"),
                'tagSet': interface_group.get("tagSet"),
                },
            }

    def DescribeLocalGatewayRouteTables(self, params: Dict[str, Any]):
        """Describes one or more local gateway route tables. By default, all local gateway route tables are described.
         Alternatively, you can filter the results."""

        route_table_ids = params.get("LocalGatewayRouteTableId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        route_table_store = self._get_store("local_gateway_route_tables")
        if route_table_ids:
            resources = []
            for route_table_id in route_table_ids:
                resource = route_table_store.get(route_table_id)
                if not resource:
                    return create_error_response(
                        "InvalidLocalGatewayRouteTableId.NotFound",
                        f"The ID '{route_table_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(route_table_store.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        route_tables = []
        for resource in resources[:max_results]:
            route_tables.append(
                {
                    "localGatewayId": resource.get("localGatewayId"),
                    "localGatewayRouteTableArn": resource.get("localGatewayRouteTableArn"),
                    "localGatewayRouteTableId": resource.get("localGatewayRouteTableId"),
                    "mode": resource.get("mode"),
                    "outpostArn": resource.get("outpostArn"),
                    "ownerId": resource.get("ownerId"),
                    "state": resource.get("state"),
                    "stateReason": resource.get("stateReason"),
                    "tagSet": resource.get("tagSet"),
                }
            )

        return {
            'localGatewayRouteTableSet': route_tables,
            'nextToken': None,
            }

    def DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociations(self, params: Dict[str, Any]):
        """Describes the associations between virtual interface groups and local gateway route tables."""

        association_ids = params.get("LocalGatewayRouteTableVirtualInterfaceGroupAssociationId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        association_store = self._get_store("local_gateway_route_table_virtual_interface_group_associations")
        if association_ids:
            resources = []
            for association_id in association_ids:
                resource = association_store.get(association_id)
                if not resource:
                    return create_error_response(
                        "InvalidLocalGatewayRouteTableVirtualInterfaceGroupAssociationId.NotFound",
                        f"The ID '{association_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(association_store.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        associations = []
        for resource in resources[:max_results]:
            associations.append(
                {
                    "localGatewayId": resource.get("localGatewayId"),
                    "localGatewayRouteTableArn": resource.get("localGatewayRouteTableArn"),
                    "localGatewayRouteTableId": resource.get("localGatewayRouteTableId"),
                    "localGatewayRouteTableVirtualInterfaceGroupAssociationId": resource.get(
                        "localGatewayRouteTableVirtualInterfaceGroupAssociationId"
                    ),
                    "localGatewayVirtualInterfaceGroupId": resource.get("localGatewayVirtualInterfaceGroupId"),
                    "ownerId": resource.get("ownerId"),
                    "state": resource.get("state"),
                    "tagSet": resource.get("tagSet"),
                }
            )

        return {
            'localGatewayRouteTableVirtualInterfaceGroupAssociationSet': associations,
            'nextToken': None,
            }

    def DescribeLocalGatewayRouteTableVpcAssociations(self, params: Dict[str, Any]):
        """Describes the specified associations between VPCs and local gateway route tables."""

        association_ids = params.get("LocalGatewayRouteTableVpcAssociationId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        association_store = self._get_store("local_gateway_route_table_vpc_associations")
        if association_ids:
            resources = []
            for association_id in association_ids:
                resource = association_store.get(association_id)
                if not resource:
                    return create_error_response(
                        "InvalidLocalGatewayRouteTableVpcAssociationId.NotFound",
                        f"The ID '{association_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(association_store.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        associations = []
        for resource in resources[:max_results]:
            associations.append(
                {
                    "localGatewayId": resource.get("localGatewayId"),
                    "localGatewayRouteTableArn": resource.get("localGatewayRouteTableArn"),
                    "localGatewayRouteTableId": resource.get("localGatewayRouteTableId"),
                    "localGatewayRouteTableVpcAssociationId": resource.get(
                        "localGatewayRouteTableVpcAssociationId"
                    ),
                    "ownerId": resource.get("ownerId"),
                    "state": resource.get("state"),
                    "tagSet": resource.get("tagSet"),
                    "vpcId": resource.get("vpcId"),
                }
            )

        return {
            'localGatewayRouteTableVpcAssociationSet': associations,
            'nextToken': None,
            }

    def DescribeLocalGateways(self, params: Dict[str, Any]):
        """Describes one or more local gateways. By default, all local gateways are described. 
        Alternatively, you can filter the results."""

        local_gateway_ids = params.get("LocalGatewayId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if local_gateway_ids:
            resources = []
            for local_gateway_id in local_gateway_ids:
                resource = self.resources.get(local_gateway_id)
                if not resource:
                    return create_error_response(
                        "InvalidLocalGatewayId.NotFound",
                        f"The ID '{local_gateway_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        gateways = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'localGatewaySet': gateways,
            'nextToken': None,
            }

    def DescribeLocalGatewayVirtualInterfaceGroups(self, params: Dict[str, Any]):
        """Describes the specified local gateway virtual interface groups."""

        interface_group_ids = params.get("LocalGatewayVirtualInterfaceGroupId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
        if interface_group_ids:
            resources = []
            for interface_group_id in interface_group_ids:
                resource = interface_group_store.get(interface_group_id)
                if not resource:
                    return create_error_response(
                        "InvalidLocalGatewayVirtualInterfaceGroupId.NotFound",
                        f"The ID '{interface_group_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(interface_group_store.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        interface_groups = []
        for resource in resources[:max_results]:
            interface_groups.append(
                {
                    "configurationState": resource.get("configurationState"),
                    "localBgpAsn": resource.get("localBgpAsn"),
                    "localBgpAsnExtended": resource.get("localBgpAsnExtended"),
                    "localGatewayId": resource.get("localGatewayId"),
                    "localGatewayVirtualInterfaceGroupArn": resource.get(
                        "localGatewayVirtualInterfaceGroupArn"
                    ),
                    "localGatewayVirtualInterfaceGroupId": resource.get(
                        "localGatewayVirtualInterfaceGroupId"
                    ),
                    "localGatewayVirtualInterfaceIdSet": resource.get(
                        "localGatewayVirtualInterfaceIdSet"
                    ),
                    "ownerId": resource.get("ownerId"),
                    "tagSet": resource.get("tagSet"),
                }
            )

        return {
            'localGatewayVirtualInterfaceGroupSet': interface_groups,
            'nextToken': None,
            }

    def DescribeLocalGatewayVirtualInterfaces(self, params: Dict[str, Any]):
        """Describes the specified local gateway virtual interfaces."""

        virtual_interface_ids = params.get("LocalGatewayVirtualInterfaceId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        interface_store = self._get_store("local_gateway_virtual_interfaces")
        if virtual_interface_ids:
            resources = []
            for virtual_interface_id in virtual_interface_ids:
                resource = interface_store.get(virtual_interface_id)
                if not resource:
                    return create_error_response(
                        "InvalidLocalGatewayVirtualInterfaceId.NotFound",
                        f"The ID '{virtual_interface_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(interface_store.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        virtual_interfaces = []
        for resource in resources[:max_results]:
            virtual_interfaces.append(
                {
                    "configurationState": resource.get("configurationState"),
                    "localAddress": resource.get("localAddress"),
                    "localBgpAsn": resource.get("localBgpAsn"),
                    "localGatewayId": resource.get("localGatewayId"),
                    "localGatewayVirtualInterfaceArn": resource.get("localGatewayVirtualInterfaceArn"),
                    "localGatewayVirtualInterfaceGroupId": resource.get(
                        "localGatewayVirtualInterfaceGroupId"
                    ),
                    "localGatewayVirtualInterfaceId": resource.get("localGatewayVirtualInterfaceId"),
                    "outpostLagId": resource.get("outpostLagId"),
                    "ownerId": resource.get("ownerId"),
                    "peerAddress": resource.get("peerAddress"),
                    "peerBgpAsn": resource.get("peerBgpAsn"),
                    "peerBgpAsnExtended": resource.get("peerBgpAsnExtended"),
                    "tagSet": resource.get("tagSet"),
                    "vlan": resource.get("vlan"),
                }
            )

        return {
            'localGatewayVirtualInterfaceSet': virtual_interfaces,
            'nextToken': None,
            }

    def ModifyLocalGatewayRoute(self, params: Dict[str, Any]):
        """Modifies the specified local gateway route."""

        error = self._require_params(params, ["LocalGatewayRouteTableId"])
        if error:
            return error

        route_table_id = params.get("LocalGatewayRouteTableId")
        route_table_store = self._get_store("local_gateway_route_tables")
        route_table = route_table_store.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{route_table_id}' does not exist.",
            )

        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")
        if not destination_cidr_block and not destination_prefix_list_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: DestinationCidrBlock or DestinationPrefixListId",
            )

        local_gateway_virtual_interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        network_interface_id = params.get("NetworkInterfaceId")
        if local_gateway_virtual_interface_group_id:
            interface_group_store = self._get_store("local_gateway_virtual_interface_groups")
            if local_gateway_virtual_interface_group_id not in interface_group_store:
                return create_error_response(
                    "InvalidLocalGatewayVirtualInterfaceGroupId.NotFound",
                    f"The ID '{local_gateway_virtual_interface_group_id}' does not exist",
                )

        if network_interface_id:
            network_interface = self.state.elastic_network_interfaces.get(network_interface_id)
            if not network_interface:
                return create_error_response(
                    "InvalidNetworkInterfaceID.NotFound",
                    f"The ID '{network_interface_id}' does not exist",
                )

        route_list = route_table.setdefault("route_set", [])
        route = None
        for existing in route_list:
            if existing.get("destinationCidrBlock") == destination_cidr_block and existing.get(
                "destinationPrefixListId"
            ) == destination_prefix_list_id:
                route = existing
                break

        if not route:
            route = {
                "coipPoolId": None,
                "destinationCidrBlock": destination_cidr_block,
                "destinationPrefixListId": destination_prefix_list_id,
                "localGatewayRouteTableArn": route_table.get("localGatewayRouteTableArn"),
                "localGatewayRouteTableId": route_table_id,
                "localGatewayVirtualInterfaceGroupId": local_gateway_virtual_interface_group_id,
                "networkInterfaceId": network_interface_id,
                "ownerId": route_table.get("ownerId"),
                "state": "active",
                "subnetId": None,
                "type": "static",
            }
            route_list.append(route)
        else:
            if local_gateway_virtual_interface_group_id is not None:
                route["localGatewayVirtualInterfaceGroupId"] = local_gateway_virtual_interface_group_id
            if network_interface_id is not None:
                route["networkInterfaceId"] = network_interface_id
            route["state"] = route.get("state") or "active"

        return {
            'route': {
                'coipPoolId': route.get("coipPoolId"),
                'destinationCidrBlock': route.get("destinationCidrBlock"),
                'destinationPrefixListId': route.get("destinationPrefixListId"),
                'localGatewayRouteTableArn': route.get("localGatewayRouteTableArn"),
                'localGatewayRouteTableId': route.get("localGatewayRouteTableId"),
                'localGatewayVirtualInterfaceGroupId': route.get("localGatewayVirtualInterfaceGroupId"),
                'networkInterfaceId': route.get("networkInterfaceId"),
                'ownerId': route.get("ownerId"),
                'state': route.get("state"),
                'subnetId': route.get("subnetId"),
                'type': route.get("type"),
                },
            }

    def SearchLocalGatewayRoutes(self, params: Dict[str, Any]):
        """Searches for routes in the specified local gateway route table."""

        error = self._require_params(params, ["LocalGatewayRouteTableId"])
        if error:
            return error

        route_table_id = params.get("LocalGatewayRouteTableId")
        route_table_store = self._get_store("local_gateway_route_tables")
        route_table = route_table_store.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{route_table_id}' does not exist.",
            )

        max_results = int(params.get("MaxResults") or 100)
        routes = list(route_table.get("route_set", []) or [])
        routes = apply_filters(routes, params.get("Filter.N", []))

        return {
            'nextToken': None,
            'routeSet': routes[:max_results],
            }

    def _generate_id(self, prefix: str = 'lgw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class localgateway_RequestParser:
    @staticmethod
    def parse_create_local_gateway_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationPrefixListId": get_scalar(md, "DestinationPrefixListId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
            "LocalGatewayVirtualInterfaceGroupId": get_scalar(md, "LocalGatewayVirtualInterfaceGroupId"),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
        }

    @staticmethod
    def parse_create_local_gateway_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayId": get_scalar(md, "LocalGatewayId"),
            "Mode": get_scalar(md, "Mode"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_local_gateway_route_table_virtual_interface_group_association_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
            "LocalGatewayVirtualInterfaceGroupId": get_scalar(md, "LocalGatewayVirtualInterfaceGroupId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_local_gateway_virtual_interface_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalAddress": get_scalar(md, "LocalAddress"),
            "LocalGatewayVirtualInterfaceGroupId": get_scalar(md, "LocalGatewayVirtualInterfaceGroupId"),
            "OutpostLagId": get_scalar(md, "OutpostLagId"),
            "PeerAddress": get_scalar(md, "PeerAddress"),
            "PeerBgpAsn": get_int(md, "PeerBgpAsn"),
            "PeerBgpAsnExtended": get_int(md, "PeerBgpAsnExtended"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Vlan": get_int(md, "Vlan"),
        }

    @staticmethod
    def parse_create_local_gateway_route_table_vpc_association_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_create_local_gateway_virtual_interface_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalBgpAsn": get_int(md, "LocalBgpAsn"),
            "LocalBgpAsnExtended": get_int(md, "LocalBgpAsnExtended"),
            "LocalGatewayId": get_scalar(md, "LocalGatewayId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_local_gateway_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationPrefixListId": get_scalar(md, "DestinationPrefixListId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
        }

    @staticmethod
    def parse_delete_local_gateway_route_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
        }

    @staticmethod
    def parse_delete_local_gateway_route_table_virtual_interface_group_association_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableVirtualInterfaceGroupAssociationId": get_scalar(md, "LocalGatewayRouteTableVirtualInterfaceGroupAssociationId"),
        }

    @staticmethod
    def parse_delete_local_gateway_route_table_vpc_association_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableVpcAssociationId": get_scalar(md, "LocalGatewayRouteTableVpcAssociationId"),
        }

    @staticmethod
    def parse_delete_local_gateway_virtual_interface_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayVirtualInterfaceId": get_scalar(md, "LocalGatewayVirtualInterfaceId"),
        }

    @staticmethod
    def parse_delete_local_gateway_virtual_interface_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayVirtualInterfaceGroupId": get_scalar(md, "LocalGatewayVirtualInterfaceGroupId"),
        }

    @staticmethod
    def parse_describe_local_gateway_route_tables_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocalGatewayRouteTableId.N": get_indexed_list(md, "LocalGatewayRouteTableId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_local_gateway_route_table_virtual_interface_group_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocalGatewayRouteTableVirtualInterfaceGroupAssociationId.N": get_indexed_list(md, "LocalGatewayRouteTableVirtualInterfaceGroupAssociationId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_local_gateway_route_table_vpc_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocalGatewayRouteTableVpcAssociationId.N": get_indexed_list(md, "LocalGatewayRouteTableVpcAssociationId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_local_gateways_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocalGatewayId.N": get_indexed_list(md, "LocalGatewayId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_local_gateway_virtual_interface_groups_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocalGatewayVirtualInterfaceGroupId.N": get_indexed_list(md, "LocalGatewayVirtualInterfaceGroupId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_local_gateway_virtual_interfaces_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocalGatewayVirtualInterfaceId.N": get_indexed_list(md, "LocalGatewayVirtualInterfaceId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_modify_local_gateway_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationPrefixListId": get_scalar(md, "DestinationPrefixListId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
            "LocalGatewayVirtualInterfaceGroupId": get_scalar(md, "LocalGatewayVirtualInterfaceGroupId"),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
        }

    @staticmethod
    def parse_search_local_gateway_routes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateLocalGatewayRoute": localgateway_RequestParser.parse_create_local_gateway_route_request,
            "CreateLocalGatewayRouteTable": localgateway_RequestParser.parse_create_local_gateway_route_table_request,
            "CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociation": localgateway_RequestParser.parse_create_local_gateway_route_table_virtual_interface_group_association_request,
            "CreateLocalGatewayVirtualInterface": localgateway_RequestParser.parse_create_local_gateway_virtual_interface_request,
            "CreateLocalGatewayRouteTableVpcAssociation": localgateway_RequestParser.parse_create_local_gateway_route_table_vpc_association_request,
            "CreateLocalGatewayVirtualInterfaceGroup": localgateway_RequestParser.parse_create_local_gateway_virtual_interface_group_request,
            "DeleteLocalGatewayRoute": localgateway_RequestParser.parse_delete_local_gateway_route_request,
            "DeleteLocalGatewayRouteTable": localgateway_RequestParser.parse_delete_local_gateway_route_table_request,
            "DeleteLocalGatewayRouteTableVirtualInterfaceGroupAssociation": localgateway_RequestParser.parse_delete_local_gateway_route_table_virtual_interface_group_association_request,
            "DeleteLocalGatewayRouteTableVpcAssociation": localgateway_RequestParser.parse_delete_local_gateway_route_table_vpc_association_request,
            "DeleteLocalGatewayVirtualInterface": localgateway_RequestParser.parse_delete_local_gateway_virtual_interface_request,
            "DeleteLocalGatewayVirtualInterfaceGroup": localgateway_RequestParser.parse_delete_local_gateway_virtual_interface_group_request,
            "DescribeLocalGatewayRouteTables": localgateway_RequestParser.parse_describe_local_gateway_route_tables_request,
            "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociations": localgateway_RequestParser.parse_describe_local_gateway_route_table_virtual_interface_group_associations_request,
            "DescribeLocalGatewayRouteTableVpcAssociations": localgateway_RequestParser.parse_describe_local_gateway_route_table_vpc_associations_request,
            "DescribeLocalGateways": localgateway_RequestParser.parse_describe_local_gateways_request,
            "DescribeLocalGatewayVirtualInterfaceGroups": localgateway_RequestParser.parse_describe_local_gateway_virtual_interface_groups_request,
            "DescribeLocalGatewayVirtualInterfaces": localgateway_RequestParser.parse_describe_local_gateway_virtual_interfaces_request,
            "ModifyLocalGatewayRoute": localgateway_RequestParser.parse_modify_local_gateway_route_request,
            "SearchLocalGatewayRoutes": localgateway_RequestParser.parse_search_local_gateway_routes_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class localgateway_ResponseSerializer:
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
                xml_parts.extend(localgateway_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(localgateway_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(localgateway_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(localgateway_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_local_gateway_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateLocalGatewayRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</route>')
        xml_parts.append(f'</CreateLocalGatewayRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_local_gateway_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateLocalGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTable
        _localGatewayRouteTable_key = None
        if "localGatewayRouteTable" in data:
            _localGatewayRouteTable_key = "localGatewayRouteTable"
        elif "LocalGatewayRouteTable" in data:
            _localGatewayRouteTable_key = "LocalGatewayRouteTable"
        if _localGatewayRouteTable_key:
            param_data = data[_localGatewayRouteTable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayRouteTable>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayRouteTable>')
        xml_parts.append(f'</CreateLocalGatewayRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_local_gateway_route_table_virtual_interface_group_association_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTableVirtualInterfaceGroupAssociation
        _localGatewayRouteTableVirtualInterfaceGroupAssociation_key = None
        if "localGatewayRouteTableVirtualInterfaceGroupAssociation" in data:
            _localGatewayRouteTableVirtualInterfaceGroupAssociation_key = "localGatewayRouteTableVirtualInterfaceGroupAssociation"
        elif "LocalGatewayRouteTableVirtualInterfaceGroupAssociation" in data:
            _localGatewayRouteTableVirtualInterfaceGroupAssociation_key = "LocalGatewayRouteTableVirtualInterfaceGroupAssociation"
        if _localGatewayRouteTableVirtualInterfaceGroupAssociation_key:
            param_data = data[_localGatewayRouteTableVirtualInterfaceGroupAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayRouteTableVirtualInterfaceGroupAssociation>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayRouteTableVirtualInterfaceGroupAssociation>')
        xml_parts.append(f'</CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_local_gateway_virtual_interface_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateLocalGatewayVirtualInterfaceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayVirtualInterface
        _localGatewayVirtualInterface_key = None
        if "localGatewayVirtualInterface" in data:
            _localGatewayVirtualInterface_key = "localGatewayVirtualInterface"
        elif "LocalGatewayVirtualInterface" in data:
            _localGatewayVirtualInterface_key = "LocalGatewayVirtualInterface"
        if _localGatewayVirtualInterface_key:
            param_data = data[_localGatewayVirtualInterface_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayVirtualInterface>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayVirtualInterface>')
        xml_parts.append(f'</CreateLocalGatewayVirtualInterfaceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_local_gateway_route_table_vpc_association_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateLocalGatewayRouteTableVpcAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTableVpcAssociation
        _localGatewayRouteTableVpcAssociation_key = None
        if "localGatewayRouteTableVpcAssociation" in data:
            _localGatewayRouteTableVpcAssociation_key = "localGatewayRouteTableVpcAssociation"
        elif "LocalGatewayRouteTableVpcAssociation" in data:
            _localGatewayRouteTableVpcAssociation_key = "LocalGatewayRouteTableVpcAssociation"
        if _localGatewayRouteTableVpcAssociation_key:
            param_data = data[_localGatewayRouteTableVpcAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayRouteTableVpcAssociation>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayRouteTableVpcAssociation>')
        xml_parts.append(f'</CreateLocalGatewayRouteTableVpcAssociationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_local_gateway_virtual_interface_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateLocalGatewayVirtualInterfaceGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayVirtualInterfaceGroup
        _localGatewayVirtualInterfaceGroup_key = None
        if "localGatewayVirtualInterfaceGroup" in data:
            _localGatewayVirtualInterfaceGroup_key = "localGatewayVirtualInterfaceGroup"
        elif "LocalGatewayVirtualInterfaceGroup" in data:
            _localGatewayVirtualInterfaceGroup_key = "LocalGatewayVirtualInterfaceGroup"
        if _localGatewayVirtualInterfaceGroup_key:
            param_data = data[_localGatewayVirtualInterfaceGroup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayVirtualInterfaceGroup>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayVirtualInterfaceGroup>')
        xml_parts.append(f'</CreateLocalGatewayVirtualInterfaceGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_local_gateway_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteLocalGatewayRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</route>')
        xml_parts.append(f'</DeleteLocalGatewayRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_local_gateway_route_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteLocalGatewayRouteTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTable
        _localGatewayRouteTable_key = None
        if "localGatewayRouteTable" in data:
            _localGatewayRouteTable_key = "localGatewayRouteTable"
        elif "LocalGatewayRouteTable" in data:
            _localGatewayRouteTable_key = "LocalGatewayRouteTable"
        if _localGatewayRouteTable_key:
            param_data = data[_localGatewayRouteTable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayRouteTable>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayRouteTable>')
        xml_parts.append(f'</DeleteLocalGatewayRouteTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_local_gateway_route_table_virtual_interface_group_association_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteLocalGatewayRouteTableVirtualInterfaceGroupAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTableVirtualInterfaceGroupAssociation
        _localGatewayRouteTableVirtualInterfaceGroupAssociation_key = None
        if "localGatewayRouteTableVirtualInterfaceGroupAssociation" in data:
            _localGatewayRouteTableVirtualInterfaceGroupAssociation_key = "localGatewayRouteTableVirtualInterfaceGroupAssociation"
        elif "LocalGatewayRouteTableVirtualInterfaceGroupAssociation" in data:
            _localGatewayRouteTableVirtualInterfaceGroupAssociation_key = "LocalGatewayRouteTableVirtualInterfaceGroupAssociation"
        if _localGatewayRouteTableVirtualInterfaceGroupAssociation_key:
            param_data = data[_localGatewayRouteTableVirtualInterfaceGroupAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayRouteTableVirtualInterfaceGroupAssociation>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayRouteTableVirtualInterfaceGroupAssociation>')
        xml_parts.append(f'</DeleteLocalGatewayRouteTableVirtualInterfaceGroupAssociationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_local_gateway_route_table_vpc_association_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteLocalGatewayRouteTableVpcAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTableVpcAssociation
        _localGatewayRouteTableVpcAssociation_key = None
        if "localGatewayRouteTableVpcAssociation" in data:
            _localGatewayRouteTableVpcAssociation_key = "localGatewayRouteTableVpcAssociation"
        elif "LocalGatewayRouteTableVpcAssociation" in data:
            _localGatewayRouteTableVpcAssociation_key = "LocalGatewayRouteTableVpcAssociation"
        if _localGatewayRouteTableVpcAssociation_key:
            param_data = data[_localGatewayRouteTableVpcAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayRouteTableVpcAssociation>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayRouteTableVpcAssociation>')
        xml_parts.append(f'</DeleteLocalGatewayRouteTableVpcAssociationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_local_gateway_virtual_interface_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteLocalGatewayVirtualInterfaceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayVirtualInterface
        _localGatewayVirtualInterface_key = None
        if "localGatewayVirtualInterface" in data:
            _localGatewayVirtualInterface_key = "localGatewayVirtualInterface"
        elif "LocalGatewayVirtualInterface" in data:
            _localGatewayVirtualInterface_key = "LocalGatewayVirtualInterface"
        if _localGatewayVirtualInterface_key:
            param_data = data[_localGatewayVirtualInterface_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayVirtualInterface>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayVirtualInterface>')
        xml_parts.append(f'</DeleteLocalGatewayVirtualInterfaceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_local_gateway_virtual_interface_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteLocalGatewayVirtualInterfaceGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayVirtualInterfaceGroup
        _localGatewayVirtualInterfaceGroup_key = None
        if "localGatewayVirtualInterfaceGroup" in data:
            _localGatewayVirtualInterfaceGroup_key = "localGatewayVirtualInterfaceGroup"
        elif "LocalGatewayVirtualInterfaceGroup" in data:
            _localGatewayVirtualInterfaceGroup_key = "LocalGatewayVirtualInterfaceGroup"
        if _localGatewayVirtualInterfaceGroup_key:
            param_data = data[_localGatewayVirtualInterfaceGroup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayVirtualInterfaceGroup>')
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</localGatewayVirtualInterfaceGroup>')
        xml_parts.append(f'</DeleteLocalGatewayVirtualInterfaceGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_local_gateway_route_tables_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeLocalGatewayRouteTablesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTableSet
        _localGatewayRouteTableSet_key = None
        if "localGatewayRouteTableSet" in data:
            _localGatewayRouteTableSet_key = "localGatewayRouteTableSet"
        elif "LocalGatewayRouteTableSet" in data:
            _localGatewayRouteTableSet_key = "LocalGatewayRouteTableSet"
        elif "LocalGatewayRouteTables" in data:
            _localGatewayRouteTableSet_key = "LocalGatewayRouteTables"
        if _localGatewayRouteTableSet_key:
            param_data = data[_localGatewayRouteTableSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<localGatewayRouteTableSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</localGatewayRouteTableSet>')
            else:
                xml_parts.append(f'{indent_str}<localGatewayRouteTableSet/>')
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
        xml_parts.append(f'</DescribeLocalGatewayRouteTablesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_local_gateway_route_table_virtual_interface_group_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTableVirtualInterfaceGroupAssociationSet
        _localGatewayRouteTableVirtualInterfaceGroupAssociationSet_key = None
        if "localGatewayRouteTableVirtualInterfaceGroupAssociationSet" in data:
            _localGatewayRouteTableVirtualInterfaceGroupAssociationSet_key = "localGatewayRouteTableVirtualInterfaceGroupAssociationSet"
        elif "LocalGatewayRouteTableVirtualInterfaceGroupAssociationSet" in data:
            _localGatewayRouteTableVirtualInterfaceGroupAssociationSet_key = "LocalGatewayRouteTableVirtualInterfaceGroupAssociationSet"
        elif "LocalGatewayRouteTableVirtualInterfaceGroupAssociations" in data:
            _localGatewayRouteTableVirtualInterfaceGroupAssociationSet_key = "LocalGatewayRouteTableVirtualInterfaceGroupAssociations"
        if _localGatewayRouteTableVirtualInterfaceGroupAssociationSet_key:
            param_data = data[_localGatewayRouteTableVirtualInterfaceGroupAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<localGatewayRouteTableVirtualInterfaceGroupAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</localGatewayRouteTableVirtualInterfaceGroupAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<localGatewayRouteTableVirtualInterfaceGroupAssociationSet/>')
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
        xml_parts.append(f'</DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_local_gateway_route_table_vpc_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeLocalGatewayRouteTableVpcAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayRouteTableVpcAssociationSet
        _localGatewayRouteTableVpcAssociationSet_key = None
        if "localGatewayRouteTableVpcAssociationSet" in data:
            _localGatewayRouteTableVpcAssociationSet_key = "localGatewayRouteTableVpcAssociationSet"
        elif "LocalGatewayRouteTableVpcAssociationSet" in data:
            _localGatewayRouteTableVpcAssociationSet_key = "LocalGatewayRouteTableVpcAssociationSet"
        elif "LocalGatewayRouteTableVpcAssociations" in data:
            _localGatewayRouteTableVpcAssociationSet_key = "LocalGatewayRouteTableVpcAssociations"
        if _localGatewayRouteTableVpcAssociationSet_key:
            param_data = data[_localGatewayRouteTableVpcAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<localGatewayRouteTableVpcAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</localGatewayRouteTableVpcAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<localGatewayRouteTableVpcAssociationSet/>')
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
        xml_parts.append(f'</DescribeLocalGatewayRouteTableVpcAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_local_gateways_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeLocalGatewaysResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewaySet
        _localGatewaySet_key = None
        if "localGatewaySet" in data:
            _localGatewaySet_key = "localGatewaySet"
        elif "LocalGatewaySet" in data:
            _localGatewaySet_key = "LocalGatewaySet"
        elif "LocalGateways" in data:
            _localGatewaySet_key = "LocalGateways"
        if _localGatewaySet_key:
            param_data = data[_localGatewaySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<localGatewaySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</localGatewaySet>')
            else:
                xml_parts.append(f'{indent_str}<localGatewaySet/>')
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
        xml_parts.append(f'</DescribeLocalGatewaysResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_local_gateway_virtual_interface_groups_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeLocalGatewayVirtualInterfaceGroupsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayVirtualInterfaceGroupSet
        _localGatewayVirtualInterfaceGroupSet_key = None
        if "localGatewayVirtualInterfaceGroupSet" in data:
            _localGatewayVirtualInterfaceGroupSet_key = "localGatewayVirtualInterfaceGroupSet"
        elif "LocalGatewayVirtualInterfaceGroupSet" in data:
            _localGatewayVirtualInterfaceGroupSet_key = "LocalGatewayVirtualInterfaceGroupSet"
        elif "LocalGatewayVirtualInterfaceGroups" in data:
            _localGatewayVirtualInterfaceGroupSet_key = "LocalGatewayVirtualInterfaceGroups"
        if _localGatewayVirtualInterfaceGroupSet_key:
            param_data = data[_localGatewayVirtualInterfaceGroupSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<localGatewayVirtualInterfaceGroupSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</localGatewayVirtualInterfaceGroupSet>')
            else:
                xml_parts.append(f'{indent_str}<localGatewayVirtualInterfaceGroupSet/>')
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
        xml_parts.append(f'</DescribeLocalGatewayVirtualInterfaceGroupsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_local_gateway_virtual_interfaces_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeLocalGatewayVirtualInterfacesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize localGatewayVirtualInterfaceSet
        _localGatewayVirtualInterfaceSet_key = None
        if "localGatewayVirtualInterfaceSet" in data:
            _localGatewayVirtualInterfaceSet_key = "localGatewayVirtualInterfaceSet"
        elif "LocalGatewayVirtualInterfaceSet" in data:
            _localGatewayVirtualInterfaceSet_key = "LocalGatewayVirtualInterfaceSet"
        elif "LocalGatewayVirtualInterfaces" in data:
            _localGatewayVirtualInterfaceSet_key = "LocalGatewayVirtualInterfaces"
        if _localGatewayVirtualInterfaceSet_key:
            param_data = data[_localGatewayVirtualInterfaceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<localGatewayVirtualInterfaceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</localGatewayVirtualInterfaceSet>')
            else:
                xml_parts.append(f'{indent_str}<localGatewayVirtualInterfaceSet/>')
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
        xml_parts.append(f'</DescribeLocalGatewayVirtualInterfacesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_local_gateway_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyLocalGatewayRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
            xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</route>')
        xml_parts.append(f'</ModifyLocalGatewayRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_search_local_gateway_routes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<SearchLocalGatewayRoutesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(localgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeSet>')
            else:
                xml_parts.append(f'{indent_str}<routeSet/>')
        xml_parts.append(f'</SearchLocalGatewayRoutesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateLocalGatewayRoute": localgateway_ResponseSerializer.serialize_create_local_gateway_route_response,
            "CreateLocalGatewayRouteTable": localgateway_ResponseSerializer.serialize_create_local_gateway_route_table_response,
            "CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociation": localgateway_ResponseSerializer.serialize_create_local_gateway_route_table_virtual_interface_group_association_response,
            "CreateLocalGatewayVirtualInterface": localgateway_ResponseSerializer.serialize_create_local_gateway_virtual_interface_response,
            "CreateLocalGatewayRouteTableVpcAssociation": localgateway_ResponseSerializer.serialize_create_local_gateway_route_table_vpc_association_response,
            "CreateLocalGatewayVirtualInterfaceGroup": localgateway_ResponseSerializer.serialize_create_local_gateway_virtual_interface_group_response,
            "DeleteLocalGatewayRoute": localgateway_ResponseSerializer.serialize_delete_local_gateway_route_response,
            "DeleteLocalGatewayRouteTable": localgateway_ResponseSerializer.serialize_delete_local_gateway_route_table_response,
            "DeleteLocalGatewayRouteTableVirtualInterfaceGroupAssociation": localgateway_ResponseSerializer.serialize_delete_local_gateway_route_table_virtual_interface_group_association_response,
            "DeleteLocalGatewayRouteTableVpcAssociation": localgateway_ResponseSerializer.serialize_delete_local_gateway_route_table_vpc_association_response,
            "DeleteLocalGatewayVirtualInterface": localgateway_ResponseSerializer.serialize_delete_local_gateway_virtual_interface_response,
            "DeleteLocalGatewayVirtualInterfaceGroup": localgateway_ResponseSerializer.serialize_delete_local_gateway_virtual_interface_group_response,
            "DescribeLocalGatewayRouteTables": localgateway_ResponseSerializer.serialize_describe_local_gateway_route_tables_response,
            "DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociations": localgateway_ResponseSerializer.serialize_describe_local_gateway_route_table_virtual_interface_group_associations_response,
            "DescribeLocalGatewayRouteTableVpcAssociations": localgateway_ResponseSerializer.serialize_describe_local_gateway_route_table_vpc_associations_response,
            "DescribeLocalGateways": localgateway_ResponseSerializer.serialize_describe_local_gateways_response,
            "DescribeLocalGatewayVirtualInterfaceGroups": localgateway_ResponseSerializer.serialize_describe_local_gateway_virtual_interface_groups_response,
            "DescribeLocalGatewayVirtualInterfaces": localgateway_ResponseSerializer.serialize_describe_local_gateway_virtual_interfaces_response,
            "ModifyLocalGatewayRoute": localgateway_ResponseSerializer.serialize_modify_local_gateway_route_response,
            "SearchLocalGatewayRoutes": localgateway_ResponseSerializer.serialize_search_local_gateway_routes_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

