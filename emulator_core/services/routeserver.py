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
class RouteServer:
    amazon_side_asn: int = 0
    persist_routes_duration: int = 0
    persist_routes_state: str = ""
    route_server_id: str = ""
    sns_notifications_enabled: bool = False
    sns_topic_arn: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)

    route_server_associations: List[Dict[str, Any]] = field(default_factory=list)
    route_server_propagations: List[Dict[str, Any]] = field(default_factory=list)
    route_server_endpoints: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    route_server_peers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    routing_database: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amazonSideAsn": self.amazon_side_asn,
            "persistRoutesDuration": self.persist_routes_duration,
            "persistRoutesState": self.persist_routes_state,
            "routeServerId": self.route_server_id,
            "snsNotificationsEnabled": self.sns_notifications_enabled,
            "snsTopicArn": self.sns_topic_arn,
            "state": self.state,
            "tagSet": self.tag_set,
        }

class RouteServer_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.route_servers  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            value = params.get(name)
            if value is None or value == "" or value == [] or value == {}:
                return create_error_response("MissingParameter", f"Missing required parameter '{name}'.")
        return None

    def _get_route_server_or_error(
        self,
        route_server_id: str,
        code: str = "InvalidRouteServerId.NotFound",
    ) -> (Optional[RouteServer], Optional[Dict[str, Any]]):
        resource = self.resources.get(route_server_id)
        if not resource:
            return None, create_error_response(code, f"RouteServer '{route_server_id}' does not exist.")
        return resource, None

    def _get_endpoint_or_error(
        self,
        endpoint_id: str,
        code: str = "InvalidRouteServerEndpointId.NotFound",
    ) -> (Optional[RouteServer], Optional[Dict[str, Any]], Optional[Dict[str, Any]]):
        for resource in self.resources.values():
            endpoint = resource.route_server_endpoints.get(endpoint_id)
            if endpoint:
                return resource, endpoint, None
        return None, None, create_error_response(code, f"RouteServerEndpoint '{endpoint_id}' does not exist.")

    def _get_peer_or_error(
        self,
        peer_id: str,
        code: str = "InvalidRouteServerPeerId.NotFound",
    ) -> (Optional[RouteServer], Optional[Dict[str, Any]], Optional[Dict[str, Any]]):
        for resource in self.resources.values():
            peer = resource.route_server_peers.get(peer_id)
            if peer:
                return resource, peer, None
        return None, None, create_error_response(code, f"RouteServerPeer '{peer_id}' does not exist.")

    def _collect_tags(self, tag_specs: List[Dict[str, Any]], resource_types: Optional[set] = None) -> List[Dict[str, Any]]:
        tag_set: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            resource_type = spec.get("ResourceType")
            if resource_types and resource_type and resource_type not in resource_types:
                continue
            for tag in spec.get("Tags") or spec.get("Tag") or []:
                if tag:
                    tag_set.append(tag)
        return tag_set

    def _find_association(self, route_server: RouteServer, vpc_id: str) -> Optional[Dict[str, Any]]:
        for association in route_server.route_server_associations:
            if association.get("vpcId") == vpc_id:
                return association
        return None

    def _find_propagation(self, route_server: RouteServer, route_table_id: str) -> Optional[Dict[str, Any]]:
        for propagation in route_server.route_server_propagations:
            if propagation.get("routeTableId") == route_table_id:
                return propagation
        return None

    def AssociateRouteServer(self, params: Dict[str, Any]):
        """Associates a route server with a VPC to enable dynamic route updates. A route server association is the connection established between a route server and a VPC. For more information seeDynamic routing in your VPC with VPC Route Serverin theAmazon VPC User Guide."""

        error = self._require_params(params, ["RouteServerId", "VpcId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        vpc_id = params.get("VpcId")

        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        association = self._find_association(route_server, vpc_id)
        if not association:
            association = {
                "routeServerId": route_server_id,
                "state": "associated",
                "vpcId": vpc_id,
            }
            route_server.route_server_associations.append(association)
        else:
            association["state"] = "associated"

        return {"routeServerAssociation": association}

    def CreateRouteServer(self, params: Dict[str, Any]):
        """Creates a new route server to manage dynamic routing in a VPC. Amazon VPC Route Server simplifies routing for traffic between workloads that are deployed within a VPC and its internet gateways. With this feature, 
VPC Route Server dynamically updates VPC and internet gateway route tables with your p"""

        error = self._require_params(params, ["AmazonSideAsn"])
        if error:
            return error

        amazon_side_asn = int(params.get("AmazonSideAsn") or 0)
        persist_routes_state = params.get("PersistRoutes") or "disabled"
        persist_routes_duration = int(params.get("PersistRoutesDuration") or 0)
        sns_notifications_enabled = str2bool(params.get("SnsNotificationsEnabled"))
        tag_set = self._collect_tags(params.get("TagSpecification.N", []))

        route_server_id = self._generate_id("route")
        resource = RouteServer(
            amazon_side_asn=amazon_side_asn,
            persist_routes_duration=persist_routes_duration,
            persist_routes_state=persist_routes_state,
            route_server_id=route_server_id,
            sns_notifications_enabled=sns_notifications_enabled,
            sns_topic_arn="",
            state=ResourceState.AVAILABLE.value,
            tag_set=tag_set,
        )
        self.resources[route_server_id] = resource

        return {"routeServer": resource.to_dict()}

    def CreateRouteServerEndpoint(self, params: Dict[str, Any]):
        """Creates a new endpoint for a route server in a specified subnet. A route server endpoint is an AWS-managed component inside a subnet that facilitatesBGP (Border Gateway Protocol)connections between your route server and your BGP peers. For more information seeDynamic routing in your VPC with VPC Rou"""

        error = self._require_params(params, ["RouteServerId", "SubnetId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        subnet_id = params.get("SubnetId")

        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")

        vpc_id = getattr(subnet, "vpc_id", "") or getattr(subnet, "vpcId", "")
        tag_set = self._collect_tags(params.get("TagSpecification.N", []))

        endpoint_id = self._generate_id("rse")
        eni_id = self._generate_id("eni")
        eni_address = f"10.0.0.{len(route_server.route_server_endpoints) + 10}"

        endpoint = {
            "eniAddress": eni_address,
            "eniId": eni_id,
            "failureReason": "",
            "routeServerEndpointId": endpoint_id,
            "routeServerId": route_server_id,
            "state": ResourceState.AVAILABLE.value,
            "subnetId": subnet_id,
            "tagSet": tag_set,
            "vpcId": vpc_id,
        }
        route_server.route_server_endpoints[endpoint_id] = endpoint

        return {"routeServerEndpoint": endpoint}

    def CreateRouteServerPeer(self, params: Dict[str, Any]):
        """Creates a new BGP peer for a specified route server endpoint. A route server peer is a session between a route server endpoint and the device deployed in AWS (such as a firewall appliance or other network security function running on an EC2 instance). The device must meet these requirements: Have an"""

        error = self._require_params(params, ["BgpOptions", "PeerAddress", "RouteServerEndpointId"])
        if error:
            return error

        endpoint_id = params.get("RouteServerEndpointId")
        route_server, endpoint, error = self._get_endpoint_or_error(endpoint_id)
        if error:
            return error

        bgp_options = params.get("BgpOptions") or {}
        if not isinstance(bgp_options, dict):
            bgp_options = {}

        peer_id = self._generate_id("rsp")
        tag_set = self._collect_tags(params.get("TagSpecification.N", []))

        peer = {
            "bfdStatus": {"status": ResourceState.AVAILABLE.value},
            "bgpOptions": {
                "peerAsn": bgp_options.get("PeerAsn"),
                "peerLivenessDetection": bgp_options.get("PeerLivenessDetection"),
            },
            "bgpStatus": {"status": ResourceState.AVAILABLE.value},
            "endpointEniAddress": endpoint.get("eniAddress"),
            "endpointEniId": endpoint.get("eniId"),
            "failureReason": "",
            "peerAddress": params.get("PeerAddress") or "",
            "routeServerEndpointId": endpoint_id,
            "routeServerId": endpoint.get("routeServerId"),
            "routeServerPeerId": peer_id,
            "state": ResourceState.AVAILABLE.value,
            "subnetId": endpoint.get("subnetId"),
            "tagSet": tag_set,
            "vpcId": endpoint.get("vpcId"),
        }

        route_server.route_server_peers[peer_id] = peer

        return {"routeServerPeer": peer}

    def DeleteRouteServer(self, params: Dict[str, Any]):
        """Deletes the specified route server. Amazon VPC Route Server simplifies routing for traffic between workloads that are deployed within a VPC and its internet gateways. With this feature, 
VPC Route Server dynamically updates VPC and internet gateway route tables with your preferred IPv4 or IPv6 route"""

        error = self._require_params(params, ["RouteServerId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        if route_server.route_server_endpoints or route_server.route_server_peers:
            return create_error_response(
                "DependencyViolation",
                "Route server has dependent endpoints or peers.",
            )

        resource_dict = route_server.to_dict()
        del self.resources[route_server_id]

        return {"routeServer": resource_dict}

    def DeleteRouteServerEndpoint(self, params: Dict[str, Any]):
        """Deletes the specified route server endpoint. A route server endpoint is an AWS-managed component inside a subnet that facilitatesBGP (Border Gateway Protocol)connections between your route server and your BGP peers."""

        error = self._require_params(params, ["RouteServerEndpointId"])
        if error:
            return error

        endpoint_id = params.get("RouteServerEndpointId")
        route_server, endpoint, error = self._get_endpoint_or_error(endpoint_id)
        if error:
            return error

        dependent_peers = [
            peer
            for peer in route_server.route_server_peers.values()
            if peer.get("routeServerEndpointId") == endpoint_id
        ]
        if dependent_peers:
            return create_error_response(
                "DependencyViolation",
                "Route server endpoint has dependent peers.",
            )

        del route_server.route_server_endpoints[endpoint_id]

        return {"routeServerEndpoint": endpoint}

    def DeleteRouteServerPeer(self, params: Dict[str, Any]):
        """Deletes the specified BGP peer from a route server. A route server peer is a session between a route server endpoint and the device deployed in AWS (such as a firewall appliance or other network security function running on an EC2 instance). The device must meet these requirements: Have an elastic n"""

        error = self._require_params(params, ["RouteServerPeerId"])
        if error:
            return error

        peer_id = params.get("RouteServerPeerId")
        route_server, peer, error = self._get_peer_or_error(peer_id)
        if error:
            return error

        del route_server.route_server_peers[peer_id]

        return {"routeServerPeer": peer}

    def DescribeRouteServerEndpoints(self, params: Dict[str, Any]):
        """Describes one or more route server endpoints. A route server endpoint is an AWS-managed component inside a subnet that facilitatesBGP (Border Gateway Protocol)connections between your route server and your BGP peers. For more information seeDynamic routing in your VPC with VPC Route Serverin theAmaz"""

        endpoint_ids = params.get("RouteServerEndpointId.N", []) or []
        if endpoint_ids:
            endpoints: List[Dict[str, Any]] = []
            for endpoint_id in endpoint_ids:
                _, endpoint, error = self._get_endpoint_or_error(endpoint_id)
                if error:
                    return create_error_response(
                        "InvalidRouteServerEndpointId.NotFound",
                        f"The ID '{endpoint_id}' does not exist",
                    )
                endpoints.append(endpoint)
        else:
            endpoints = []
            for resource in self.resources.values():
                endpoints.extend(resource.route_server_endpoints.values())

        filtered = apply_filters(endpoints, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None

        return {
            "nextToken": new_next_token,
            "routeServerEndpointSet": page,
        }

    def DescribeRouteServerPeers(self, params: Dict[str, Any]):
        """Describes one or more route server peers. A route server peer is a session between a route server endpoint and the device deployed in AWS (such as a firewall appliance or other network security function running on an EC2 instance). The device must meet these requirements: Have an elastic network int"""

        peer_ids = params.get("RouteServerPeerId.N", []) or []
        if peer_ids:
            peers: List[Dict[str, Any]] = []
            for peer_id in peer_ids:
                _, peer, error = self._get_peer_or_error(peer_id)
                if error:
                    return create_error_response(
                        "InvalidRouteServerPeerId.NotFound",
                        f"The ID '{peer_id}' does not exist",
                    )
                peers.append(peer)
        else:
            peers = []
            for resource in self.resources.values():
                peers.extend(resource.route_server_peers.values())

        filtered = apply_filters(peers, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None

        return {
            "nextToken": new_next_token,
            "routeServerPeerSet": page,
        }

    def DescribeRouteServers(self, params: Dict[str, Any]):
        """Describes one or more route servers. Amazon VPC Route Server simplifies routing for traffic between workloads that are deployed within a VPC and its internet gateways. With this feature, 
VPC Route Server dynamically updates VPC and internet gateway route tables with your preferred IPv4 or IPv6 rout"""

        route_server_ids = params.get("RouteServerId.N", []) or []
        if route_server_ids:
            resources: List[RouteServer] = []
            for route_server_id in route_server_ids:
                route_server, error = self._get_route_server_or_error(route_server_id)
                if error:
                    return create_error_response(
                        "InvalidRouteServerId.NotFound",
                        f"The ID '{route_server_id}' does not exist",
                    )
                resources.append(route_server)
        else:
            resources = list(self.resources.values())

        resource_dicts = [resource.to_dict() for resource in resources]
        filtered = apply_filters(resource_dicts, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None

        return {
            "nextToken": new_next_token,
            "routeServerSet": page,
        }

    def DisableRouteServerPropagation(self, params: Dict[str, Any]):
        """Disables route propagation from a route server to a specified route table. When enabled, route server propagation installs the routes in the FIB on the route table you've specified. Route server supports IPv4 and IPv6 route propagation. Amazon VPC Route Server simplifies routing for traffic between """

        error = self._require_params(params, ["RouteServerId", "RouteTableId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        route_table_id = params.get("RouteTableId")

        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidRouteTableID.NotFound",
                f"Route table '{route_table_id}' does not exist.",
            )

        propagation = self._find_propagation(route_server, route_table_id)
        if not propagation:
            propagation = {
                "routeServerId": route_server_id,
                "routeTableId": route_table_id,
                "state": "disabled",
            }
            route_server.route_server_propagations.append(propagation)
        else:
            propagation["state"] = "disabled"

        return {"routeServerPropagation": propagation}

    def DisassociateRouteServer(self, params: Dict[str, Any]):
        """Disassociates a route server from a VPC. A route server association is the connection established between a route server and a VPC. For more information seeDynamic routing in your VPC with VPC Route Serverin theAmazon VPC User Guide."""

        error = self._require_params(params, ["RouteServerId", "VpcId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        vpc_id = params.get("VpcId")

        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        association = self._find_association(route_server, vpc_id)
        if not association:
            association = {
                "routeServerId": route_server_id,
                "state": "disassociated",
                "vpcId": vpc_id,
            }
            route_server.route_server_associations.append(association)
        else:
            association["state"] = "disassociated"

        return {"routeServerAssociation": association}

    def EnableRouteServerPropagation(self, params: Dict[str, Any]):
        """Defines which route tables the route server can update with routes. When enabled, route server propagation installs the routes in the FIB on the route table you've specified. Route server supports IPv4 and IPv6 route propagation. For more information seeDynamic routing in your VPC with VPC Route Ser"""

        error = self._require_params(params, ["RouteServerId", "RouteTableId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        route_table_id = params.get("RouteTableId")

        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidRouteTableID.NotFound",
                f"Route table '{route_table_id}' does not exist.",
            )

        propagation = self._find_propagation(route_server, route_table_id)
        if not propagation:
            propagation = {
                "routeServerId": route_server_id,
                "routeTableId": route_table_id,
                "state": "enabled",
            }
            route_server.route_server_propagations.append(propagation)
        else:
            propagation["state"] = "enabled"

        return {"routeServerPropagation": propagation}

    def GetRouteServerAssociations(self, params: Dict[str, Any]):
        """Gets information about the associations for the specified route server. A route server association is the connection established between a route server and a VPC. For more information seeDynamic routing in your VPC with VPC Route Serverin theAmazon VPC User Guide."""

        error = self._require_params(params, ["RouteServerId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        return {
            "routeServerAssociationSet": list(route_server.route_server_associations),
        }

    def GetRouteServerPropagations(self, params: Dict[str, Any]):
        """Gets information about the route propagations for the specified route server. When enabled, route server propagation installs the routes in the FIB on the route table you've specified. Route server supports IPv4 and IPv6 route propagation. Amazon VPC Route Server simplifies routing for traffic betwe"""

        error = self._require_params(params, ["RouteServerId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        route_table_id = params.get("RouteTableId")
        propagations = list(route_server.route_server_propagations)
        if route_table_id:
            propagations = [
                propagation
                for propagation in propagations
                if propagation.get("routeTableId") == route_table_id
            ]

        return {
            "routeServerPropagationSet": propagations,
        }

    def GetRouteServerRoutingDatabase(self, params: Dict[str, Any]):
        """Gets the routing database for the specified route server. TheRouting Information Base (RIB)serves as a database that stores all the routing information and network topology data collected by a router or routing system, such as routes learned from BGP peers. The RIB is constantly updated as new routi"""

        error = self._require_params(params, ["RouteServerId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        routes = list(route_server.routing_database)
        filtered = apply_filters(routes, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None

        return {
            "areRoutesPersisted": route_server.persist_routes_state == "enabled",
            "nextToken": new_next_token,
            "routeSet": page,
        }

    def ModifyRouteServer(self, params: Dict[str, Any]):
        """Modifies the configuration of an existing route server. Amazon VPC Route Server simplifies routing for traffic between workloads that are deployed within a VPC and its internet gateways. With this feature, 
VPC Route Server dynamically updates VPC and internet gateway route tables with your preferre"""

        error = self._require_params(params, ["RouteServerId"])
        if error:
            return error

        route_server_id = params.get("RouteServerId")
        route_server, error = self._get_route_server_or_error(route_server_id)
        if error:
            return error

        persist_routes = params.get("PersistRoutes")
        if persist_routes is not None:
            route_server.persist_routes_state = persist_routes

        persist_routes_duration = params.get("PersistRoutesDuration")
        if persist_routes_duration is not None:
            route_server.persist_routes_duration = int(persist_routes_duration or 0)

        sns_notifications_enabled = params.get("SnsNotificationsEnabled")
        if sns_notifications_enabled is not None:
            route_server.sns_notifications_enabled = str2bool(sns_notifications_enabled)

        return {"routeServer": route_server.to_dict()}

    def _generate_id(self, prefix: str = 'route') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class routeserver_RequestParser:
    @staticmethod
    def parse_associate_route_server_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_create_route_server_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AmazonSideAsn": get_int(md, "AmazonSideAsn"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PersistRoutes": get_scalar(md, "PersistRoutes"),
            "PersistRoutesDuration": get_int(md, "PersistRoutesDuration"),
            "SnsNotificationsEnabled": get_scalar(md, "SnsNotificationsEnabled"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_route_server_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
            "SubnetId": get_scalar(md, "SubnetId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_route_server_peer_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "BgpOptions": get_scalar(md, "BgpOptions"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PeerAddress": get_scalar(md, "PeerAddress"),
            "RouteServerEndpointId": get_scalar(md, "RouteServerEndpointId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_route_server_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
        }

    @staticmethod
    def parse_delete_route_server_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerEndpointId": get_scalar(md, "RouteServerEndpointId"),
        }

    @staticmethod
    def parse_delete_route_server_peer_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerPeerId": get_scalar(md, "RouteServerPeerId"),
        }

    @staticmethod
    def parse_describe_route_server_endpoints_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "RouteServerEndpointId.N": get_indexed_list(md, "RouteServerEndpointId"),
        }

    @staticmethod
    def parse_describe_route_server_peers_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "RouteServerPeerId.N": get_indexed_list(md, "RouteServerPeerId"),
        }

    @staticmethod
    def parse_describe_route_servers_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "RouteServerId.N": get_indexed_list(md, "RouteServerId"),
        }

    @staticmethod
    def parse_disable_route_server_propagation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_disassociate_route_server_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_enable_route_server_propagation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_get_route_server_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
        }

    @staticmethod
    def parse_get_route_server_propagations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RouteServerId": get_scalar(md, "RouteServerId"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_get_route_server_routing_database_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "RouteServerId": get_scalar(md, "RouteServerId"),
        }

    @staticmethod
    def parse_modify_route_server_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PersistRoutes": get_scalar(md, "PersistRoutes"),
            "PersistRoutesDuration": get_int(md, "PersistRoutesDuration"),
            "RouteServerId": get_scalar(md, "RouteServerId"),
            "SnsNotificationsEnabled": get_scalar(md, "SnsNotificationsEnabled"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateRouteServer": routeserver_RequestParser.parse_associate_route_server_request,
            "CreateRouteServer": routeserver_RequestParser.parse_create_route_server_request,
            "CreateRouteServerEndpoint": routeserver_RequestParser.parse_create_route_server_endpoint_request,
            "CreateRouteServerPeer": routeserver_RequestParser.parse_create_route_server_peer_request,
            "DeleteRouteServer": routeserver_RequestParser.parse_delete_route_server_request,
            "DeleteRouteServerEndpoint": routeserver_RequestParser.parse_delete_route_server_endpoint_request,
            "DeleteRouteServerPeer": routeserver_RequestParser.parse_delete_route_server_peer_request,
            "DescribeRouteServerEndpoints": routeserver_RequestParser.parse_describe_route_server_endpoints_request,
            "DescribeRouteServerPeers": routeserver_RequestParser.parse_describe_route_server_peers_request,
            "DescribeRouteServers": routeserver_RequestParser.parse_describe_route_servers_request,
            "DisableRouteServerPropagation": routeserver_RequestParser.parse_disable_route_server_propagation_request,
            "DisassociateRouteServer": routeserver_RequestParser.parse_disassociate_route_server_request,
            "EnableRouteServerPropagation": routeserver_RequestParser.parse_enable_route_server_propagation_request,
            "GetRouteServerAssociations": routeserver_RequestParser.parse_get_route_server_associations_request,
            "GetRouteServerPropagations": routeserver_RequestParser.parse_get_route_server_propagations_request,
            "GetRouteServerRoutingDatabase": routeserver_RequestParser.parse_get_route_server_routing_database_request,
            "ModifyRouteServer": routeserver_RequestParser.parse_modify_route_server_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class routeserver_ResponseSerializer:
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
                xml_parts.extend(routeserver_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(routeserver_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(routeserver_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(routeserver_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_route_server_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateRouteServerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerAssociation
        _routeServerAssociation_key = None
        if "routeServerAssociation" in data:
            _routeServerAssociation_key = "routeServerAssociation"
        elif "RouteServerAssociation" in data:
            _routeServerAssociation_key = "RouteServerAssociation"
        if _routeServerAssociation_key:
            param_data = data[_routeServerAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerAssociation>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerAssociation>')
        xml_parts.append(f'</AssociateRouteServerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_route_server_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateRouteServerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServer
        _routeServer_key = None
        if "routeServer" in data:
            _routeServer_key = "routeServer"
        elif "RouteServer" in data:
            _routeServer_key = "RouteServer"
        if _routeServer_key:
            param_data = data[_routeServer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServer>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServer>')
        xml_parts.append(f'</CreateRouteServerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_route_server_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateRouteServerEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerEndpoint
        _routeServerEndpoint_key = None
        if "routeServerEndpoint" in data:
            _routeServerEndpoint_key = "routeServerEndpoint"
        elif "RouteServerEndpoint" in data:
            _routeServerEndpoint_key = "RouteServerEndpoint"
        if _routeServerEndpoint_key:
            param_data = data[_routeServerEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerEndpoint>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerEndpoint>')
        xml_parts.append(f'</CreateRouteServerEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_route_server_peer_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateRouteServerPeerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerPeer
        _routeServerPeer_key = None
        if "routeServerPeer" in data:
            _routeServerPeer_key = "routeServerPeer"
        elif "RouteServerPeer" in data:
            _routeServerPeer_key = "RouteServerPeer"
        if _routeServerPeer_key:
            param_data = data[_routeServerPeer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerPeer>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerPeer>')
        xml_parts.append(f'</CreateRouteServerPeerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_route_server_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteRouteServerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServer
        _routeServer_key = None
        if "routeServer" in data:
            _routeServer_key = "routeServer"
        elif "RouteServer" in data:
            _routeServer_key = "RouteServer"
        if _routeServer_key:
            param_data = data[_routeServer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServer>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServer>')
        xml_parts.append(f'</DeleteRouteServerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_route_server_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteRouteServerEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerEndpoint
        _routeServerEndpoint_key = None
        if "routeServerEndpoint" in data:
            _routeServerEndpoint_key = "routeServerEndpoint"
        elif "RouteServerEndpoint" in data:
            _routeServerEndpoint_key = "RouteServerEndpoint"
        if _routeServerEndpoint_key:
            param_data = data[_routeServerEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerEndpoint>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerEndpoint>')
        xml_parts.append(f'</DeleteRouteServerEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_route_server_peer_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteRouteServerPeerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerPeer
        _routeServerPeer_key = None
        if "routeServerPeer" in data:
            _routeServerPeer_key = "routeServerPeer"
        elif "RouteServerPeer" in data:
            _routeServerPeer_key = "RouteServerPeer"
        if _routeServerPeer_key:
            param_data = data[_routeServerPeer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerPeer>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerPeer>')
        xml_parts.append(f'</DeleteRouteServerPeerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_route_server_endpoints_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeRouteServerEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize routeServerEndpointSet
        _routeServerEndpointSet_key = None
        if "routeServerEndpointSet" in data:
            _routeServerEndpointSet_key = "routeServerEndpointSet"
        elif "RouteServerEndpointSet" in data:
            _routeServerEndpointSet_key = "RouteServerEndpointSet"
        elif "RouteServerEndpoints" in data:
            _routeServerEndpointSet_key = "RouteServerEndpoints"
        if _routeServerEndpointSet_key:
            param_data = data[_routeServerEndpointSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routeServerEndpointSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeServerEndpointSet>')
            else:
                xml_parts.append(f'{indent_str}<routeServerEndpointSet/>')
        xml_parts.append(f'</DescribeRouteServerEndpointsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_route_server_peers_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeRouteServerPeersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize routeServerPeerSet
        _routeServerPeerSet_key = None
        if "routeServerPeerSet" in data:
            _routeServerPeerSet_key = "routeServerPeerSet"
        elif "RouteServerPeerSet" in data:
            _routeServerPeerSet_key = "RouteServerPeerSet"
        elif "RouteServerPeers" in data:
            _routeServerPeerSet_key = "RouteServerPeers"
        if _routeServerPeerSet_key:
            param_data = data[_routeServerPeerSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routeServerPeerSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeServerPeerSet>')
            else:
                xml_parts.append(f'{indent_str}<routeServerPeerSet/>')
        xml_parts.append(f'</DescribeRouteServerPeersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_route_servers_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeRouteServersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize routeServerSet
        _routeServerSet_key = None
        if "routeServerSet" in data:
            _routeServerSet_key = "routeServerSet"
        elif "RouteServerSet" in data:
            _routeServerSet_key = "RouteServerSet"
        elif "RouteServers" in data:
            _routeServerSet_key = "RouteServers"
        if _routeServerSet_key:
            param_data = data[_routeServerSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routeServerSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeServerSet>')
            else:
                xml_parts.append(f'{indent_str}<routeServerSet/>')
        xml_parts.append(f'</DescribeRouteServersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disable_route_server_propagation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableRouteServerPropagationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerPropagation
        _routeServerPropagation_key = None
        if "routeServerPropagation" in data:
            _routeServerPropagation_key = "routeServerPropagation"
        elif "RouteServerPropagation" in data:
            _routeServerPropagation_key = "RouteServerPropagation"
        if _routeServerPropagation_key:
            param_data = data[_routeServerPropagation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerPropagation>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerPropagation>')
        xml_parts.append(f'</DisableRouteServerPropagationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_route_server_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateRouteServerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerAssociation
        _routeServerAssociation_key = None
        if "routeServerAssociation" in data:
            _routeServerAssociation_key = "routeServerAssociation"
        elif "RouteServerAssociation" in data:
            _routeServerAssociation_key = "RouteServerAssociation"
        if _routeServerAssociation_key:
            param_data = data[_routeServerAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerAssociation>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerAssociation>')
        xml_parts.append(f'</DisassociateRouteServerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_route_server_propagation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableRouteServerPropagationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerPropagation
        _routeServerPropagation_key = None
        if "routeServerPropagation" in data:
            _routeServerPropagation_key = "routeServerPropagation"
        elif "RouteServerPropagation" in data:
            _routeServerPropagation_key = "RouteServerPropagation"
        if _routeServerPropagation_key:
            param_data = data[_routeServerPropagation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServerPropagation>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServerPropagation>')
        xml_parts.append(f'</EnableRouteServerPropagationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_route_server_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetRouteServerAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerAssociationSet
        _routeServerAssociationSet_key = None
        if "routeServerAssociationSet" in data:
            _routeServerAssociationSet_key = "routeServerAssociationSet"
        elif "RouteServerAssociationSet" in data:
            _routeServerAssociationSet_key = "RouteServerAssociationSet"
        elif "RouteServerAssociations" in data:
            _routeServerAssociationSet_key = "RouteServerAssociations"
        if _routeServerAssociationSet_key:
            param_data = data[_routeServerAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routeServerAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeServerAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<routeServerAssociationSet/>')
        xml_parts.append(f'</GetRouteServerAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_route_server_propagations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetRouteServerPropagationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServerPropagationSet
        _routeServerPropagationSet_key = None
        if "routeServerPropagationSet" in data:
            _routeServerPropagationSet_key = "routeServerPropagationSet"
        elif "RouteServerPropagationSet" in data:
            _routeServerPropagationSet_key = "RouteServerPropagationSet"
        elif "RouteServerPropagations" in data:
            _routeServerPropagationSet_key = "RouteServerPropagations"
        if _routeServerPropagationSet_key:
            param_data = data[_routeServerPropagationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routeServerPropagationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeServerPropagationSet>')
            else:
                xml_parts.append(f'{indent_str}<routeServerPropagationSet/>')
        xml_parts.append(f'</GetRouteServerPropagationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_route_server_routing_database_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetRouteServerRoutingDatabaseResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize areRoutesPersisted
        _areRoutesPersisted_key = None
        if "areRoutesPersisted" in data:
            _areRoutesPersisted_key = "areRoutesPersisted"
        elif "AreRoutesPersisted" in data:
            _areRoutesPersisted_key = "AreRoutesPersisted"
        if _areRoutesPersisted_key:
            param_data = data[_areRoutesPersisted_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<areRoutesPersisted>{esc(str(param_data))}</areRoutesPersisted>')
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
                    xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routeSet>')
            else:
                xml_parts.append(f'{indent_str}<routeSet/>')
        xml_parts.append(f'</GetRouteServerRoutingDatabaseResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_route_server_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyRouteServerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize routeServer
        _routeServer_key = None
        if "routeServer" in data:
            _routeServer_key = "routeServer"
        elif "RouteServer" in data:
            _routeServer_key = "RouteServer"
        if _routeServer_key:
            param_data = data[_routeServer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<routeServer>')
            xml_parts.extend(routeserver_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</routeServer>')
        xml_parts.append(f'</ModifyRouteServerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateRouteServer": routeserver_ResponseSerializer.serialize_associate_route_server_response,
            "CreateRouteServer": routeserver_ResponseSerializer.serialize_create_route_server_response,
            "CreateRouteServerEndpoint": routeserver_ResponseSerializer.serialize_create_route_server_endpoint_response,
            "CreateRouteServerPeer": routeserver_ResponseSerializer.serialize_create_route_server_peer_response,
            "DeleteRouteServer": routeserver_ResponseSerializer.serialize_delete_route_server_response,
            "DeleteRouteServerEndpoint": routeserver_ResponseSerializer.serialize_delete_route_server_endpoint_response,
            "DeleteRouteServerPeer": routeserver_ResponseSerializer.serialize_delete_route_server_peer_response,
            "DescribeRouteServerEndpoints": routeserver_ResponseSerializer.serialize_describe_route_server_endpoints_response,
            "DescribeRouteServerPeers": routeserver_ResponseSerializer.serialize_describe_route_server_peers_response,
            "DescribeRouteServers": routeserver_ResponseSerializer.serialize_describe_route_servers_response,
            "DisableRouteServerPropagation": routeserver_ResponseSerializer.serialize_disable_route_server_propagation_response,
            "DisassociateRouteServer": routeserver_ResponseSerializer.serialize_disassociate_route_server_response,
            "EnableRouteServerPropagation": routeserver_ResponseSerializer.serialize_enable_route_server_propagation_response,
            "GetRouteServerAssociations": routeserver_ResponseSerializer.serialize_get_route_server_associations_response,
            "GetRouteServerPropagations": routeserver_ResponseSerializer.serialize_get_route_server_propagations_response,
            "GetRouteServerRoutingDatabase": routeserver_ResponseSerializer.serialize_get_route_server_routing_database_response,
            "ModifyRouteServer": routeserver_ResponseSerializer.serialize_modify_route_server_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

