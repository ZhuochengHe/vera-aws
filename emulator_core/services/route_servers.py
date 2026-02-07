from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class RouteServerAssociationState(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"


class RouteServerState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    MODIFYING = "modifying"
    DELETING = "deleting"
    DELETED = "deleted"


class PersistRoutesState(str, Enum):
    ENABLING = "enabling"
    ENABLED = "enabled"
    RESETTING = "resetting"
    DISABLING = "disabling"
    DISABLED = "disabled"
    MODIFYING = "modifying"


class RouteServerEndpointState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILING = "failing"
    FAILED = "failed"
    DELETE_FAILED = "delete-failed"


class RouteServerPeerState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILING = "failing"
    FAILED = "failed"


class BfdStatusState(str, Enum):
    UP = "up"
    DOWN = "down"


class BgpLivenessDetection(str, Enum):
    BFD = "bfd"
    BGP_KEEPALIVE = "bgp-keepalive"


class RouteInstallationStatus(str, Enum):
    INSTALLED = "installed"
    REJECTED = "rejected"


class RouteStatus(str, Enum):
    IN_RIB = "in-rib"
    IN_FIB = "in-fib"


class RouteServerPropagationState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"


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
class RouteServerAssociation:
    route_server_id: Optional[str] = None
    state: Optional[RouteServerAssociationState] = None
    vpc_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "routeServerId": self.route_server_id,
            "state": self.state.value if self.state else None,
            "vpcId": self.vpc_id,
        }


@dataclass
class RouteServer:
    amazon_side_asn: Optional[int] = None
    persist_routes_duration: Optional[int] = None
    persist_routes_state: Optional[PersistRoutesState] = None
    route_server_id: Optional[str] = None
    sns_notifications_enabled: Optional[bool] = None
    sns_topic_arn: Optional[str] = None
    state: Optional[RouteServerState] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amazonSideAsn": self.amazon_side_asn,
            "persistRoutesDuration": self.persist_routes_duration,
            "persistRoutesState": self.persist_routes_state.value if self.persist_routes_state else None,
            "routeServerId": self.route_server_id,
            "snsNotificationsEnabled": self.sns_notifications_enabled,
            "snsTopicArn": self.sns_topic_arn,
            "state": self.state.value if self.state else None,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
        }


@dataclass
class RouteServerEndpoint:
    eni_address: Optional[str] = None
    eni_id: Optional[str] = None
    failure_reason: Optional[str] = None
    route_server_endpoint_id: Optional[str] = None
    route_server_id: Optional[str] = None
    state: Optional[RouteServerEndpointState] = None
    subnet_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    vpc_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eniAddress": self.eni_address,
            "eniId": self.eni_id,
            "failureReason": self.failure_reason,
            "routeServerEndpointId": self.route_server_endpoint_id,
            "routeServerId": self.route_server_id,
            "state": self.state.value if self.state else None,
            "subnetId": self.subnet_id,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "vpcId": self.vpc_id,
        }


@dataclass
class RouteServerBgpOptionsRequest:
    peer_asn: int
    peer_liveness_detection: Optional[BgpLivenessDetection] = BgpLivenessDetection.BGP_KEEPALIVE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "PeerAsn": self.peer_asn,
            "PeerLivenessDetection": self.peer_liveness_detection.value if self.peer_liveness_detection else None,
        }


@dataclass
class RouteServerBfdStatus:
    status: Optional[BfdStatusState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value if self.status else None,
        }


@dataclass
class RouteServerBgpOptions:
    peer_asn: Optional[int] = None
    peer_liveness_detection: Optional[BgpLivenessDetection] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peerAsn": self.peer_asn,
            "peerLivenessDetection": self.peer_liveness_detection.value if self.peer_liveness_detection else None,
        }


@dataclass
class RouteServerBgpStatus:
    status: Optional[str] = None  # up | down

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
        }


@dataclass
class RouteServerPeer:
    bfd_status: Optional[RouteServerBfdStatus] = None
    bgp_options: Optional[RouteServerBgpOptions] = None
    bgp_status: Optional[RouteServerBgpStatus] = None
    endpoint_eni_address: Optional[str] = None
    endpoint_eni_id: Optional[str] = None
    failure_reason: Optional[str] = None
    peer_address: Optional[str] = None
    route_server_endpoint_id: Optional[str] = None
    route_server_id: Optional[str] = None
    route_server_peer_id: Optional[str] = None
    state: Optional[RouteServerPeerState] = None
    subnet_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    vpc_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bfdStatus": self.bfd_status.to_dict() if self.bfd_status else None,
            "bgpOptions": self.bgp_options.to_dict() if self.bgp_options else None,
            "bgpStatus": self.bgp_status.to_dict() if self.bgp_status else None,
            "endpointEniAddress": self.endpoint_eni_address,
            "endpointEniId": self.endpoint_eni_id,
            "failureReason": self.failure_reason,
            "peerAddress": self.peer_address,
            "routeServerEndpointId": self.route_server_endpoint_id,
            "routeServerId": self.route_server_id,
            "routeServerPeerId": self.route_server_peer_id,
            "state": self.state.value if self.state else None,
            "subnetId": self.subnet_id,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "vpcId": self.vpc_id,
        }


@dataclass
class RouteServerPropagation:
    route_server_id: Optional[str] = None
    route_table_id: Optional[str] = None
    state: Optional[RouteServerPropagationState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "routeServerId": self.route_server_id,
            "routeTableId": self.route_table_id,
            "state": self.state.value if self.state else None,
        }


@dataclass
class RouteServerRouteInstallationDetail:
    route_installation_status: Optional[RouteInstallationStatus] = None
    route_installation_status_reason: Optional[str] = None
    route_table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "routeInstallationStatus": self.route_installation_status.value if self.route_installation_status else None,
            "routeInstallationStatusReason": self.route_installation_status_reason,
            "routeTableId": self.route_table_id,
        }


@dataclass
class RouteServerRoute:
    as_path_set: List[str] = field(default_factory=list)
    med: Optional[int] = None
    next_hop_ip: Optional[str] = None
    prefix: Optional[str] = None
    route_installation_detail_set: List[RouteServerRouteInstallationDetail] = field(default_factory=list)
    route_server_endpoint_id: Optional[str] = None
    route_server_peer_id: Optional[str] = None
    route_status: Optional[RouteStatus] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asPathSet": self.as_path_set,
            "med": self.med,
            "nextHopIp": self.next_hop_ip,
            "prefix": self.prefix,
            "routeInstallationDetailSet": [detail.to_dict() for detail in self.route_installation_detail_set],
            "routeServerEndpointId": self.route_server_endpoint_id,
            "routeServerPeerId": self.route_server_peer_id,
            "routeStatus": self.route_status.value if self.route_status else None,
        }


class RouteserversBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for shared resources

    def associate_route_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        vpc_id = params.get("VpcId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": "DryRunOperation"}

        if not route_server_id:
            raise ValueError("RouteServerId is required")
        if not vpc_id:
            raise ValueError("VpcId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer {route_server_id} does not exist")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # Check if association already exists
        for assoc in self.state.route_server_associations.values():
            if assoc.route_server_id == route_server_id and assoc.vpc_id == vpc_id:
                # Already associated
                association = assoc
                break
        else:
            # Create new association
            association_id = self.generate_unique_id()
            association = RouteServerAssociation()
            association.route_server_id = route_server_id
            association.vpc_id = vpc_id
            association.state = RouteServerAssociationState.ASSOCIATED if hasattr(RouteServerAssociationState, "ASSOCIATED") else "associated"
            self.state.route_server_associations[association_id] = association

        response = {
            "requestId": self.generate_request_id(),
            "routeServerAssociation": {
                "routeServerId": association.route_server_id,
                "state": association.state.name if hasattr(association.state, "name") else association.state,
                "vpcId": association.vpc_id,
            },
        }
        return response


    def create_route_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        amazon_side_asn = params.get("AmazonSideAsn")
        client_token = params.get("ClientToken")
        dry_run = params.get("DryRun", False)
        persist_routes = params.get("PersistRoutes")
        persist_routes_duration = params.get("PersistRoutesDuration")
        sns_notifications_enabled = params.get("SnsNotificationsEnabled", False)
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            return {"Error": "DryRunOperation"}

        if amazon_side_asn is None:
            raise ValueError("AmazonSideAsn is required")
        if not (1 <= amazon_side_asn <= 4294967295):
            raise ValueError("AmazonSideAsn must be between 1 and 4294967295")

        # Validate persist_routes and duration
        persist_routes_state = None
        if persist_routes:
            persist_routes_lower = persist_routes.lower()
            valid_states = {"enable", "disable", "reset"}
            if persist_routes_lower not in valid_states:
                raise ValueError(f"PersistRoutes must be one of {valid_states}")
            if persist_routes_lower == "enable":
                if persist_routes_duration is None:
                    raise ValueError("PersistRoutesDuration is required when PersistRoutes is 'enable'")
                if not (1 <= persist_routes_duration <= 5):
                    raise ValueError("PersistRoutesDuration must be between 1 and 5")
                persist_routes_state = PersistRoutesState.ENABLED if hasattr(PersistRoutesState, "ENABLED") else "enabled"
            elif persist_routes_lower == "disable":
                persist_routes_state = PersistRoutesState.DISABLED if hasattr(PersistRoutesState, "DISABLED") else "disabled"
            elif persist_routes_lower == "reset":
                persist_routes_state = PersistRoutesState.RESETTING if hasattr(PersistRoutesState, "RESETTING") else "resetting"
        else:
            persist_routes_state = PersistRoutesState.DISABLED if hasattr(PersistRoutesState, "DISABLED") else "disabled"
            if persist_routes_duration is None:
                persist_routes_duration = 1

        # Create RouteServer object
        route_server_id = self.generate_unique_id()
        route_server = RouteServer()
        route_server.amazon_side_asn = amazon_side_asn
        route_server.persist_routes_duration = persist_routes_duration
        route_server.persist_routes_state = persist_routes_state
        route_server.route_server_id = route_server_id
        route_server.sns_notifications_enabled = sns_notifications_enabled
        route_server.sns_topic_arn = None
        route_server.state = RouteServerState.AVAILABLE if hasattr(RouteServerState, "AVAILABLE") else "available"
        route_server.tag_set = []

        # Process tags from tag_specifications
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag_dict in tags:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key and (not key.lower().startswith("aws:")):
                    tag = Tag()
                    tag.Key = key
                    tag.Value = value
                    route_server.tag_set.append(tag)

        self.state.route_servers[route_server_id] = route_server

        response = {
            "requestId": self.generate_request_id(),
            "routeServer": route_server.to_dict(),
        }
        return response


    def create_route_server_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        dry_run = params.get("DryRun", False)
        route_server_id = params.get("RouteServerId")
        subnet_id = params.get("SubnetId")
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            return {"Error": "DryRunOperation"}

        if not route_server_id:
            raise ValueError("RouteServerId is required")
        if not subnet_id:
            raise ValueError("SubnetId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer {route_server_id} does not exist")

        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            raise ValueError(f"Subnet {subnet_id} does not exist")

        # Create RouteServerEndpoint object
        route_server_endpoint_id = self.generate_unique_id()
        endpoint = RouteServerEndpoint()
        endpoint.route_server_endpoint_id = route_server_endpoint_id
        endpoint.route_server_id = route_server_id
        endpoint.subnet_id = subnet_id
        endpoint.vpc_id = subnet.vpc_id if hasattr(subnet, "vpc_id") else None
        endpoint.state = RouteServerEndpointState.PENDING if hasattr(RouteServerEndpointState, "PENDING") else "pending"
        endpoint.eni_id = None
        endpoint.eni_address = None
        endpoint.failure_reason = None
        endpoint.tag_set = []

        # Process tags from tag_specifications
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag_dict in tags:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key and (not key.lower().startswith("aws:")):
                    tag = Tag()
                    tag.Key = key
                    tag.Value = value
                    endpoint.tag_set.append(tag)

        self.state.route_server_endpoints[route_server_endpoint_id] = endpoint

        response = {
            "requestId": self.generate_request_id(),
            "routeServerEndpoint": endpoint.to_dict(),
        }
        return response


    def create_route_server_peer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        bgp_options_dict = params.get("BgpOptions")
        dry_run = params.get("DryRun", False)
        peer_address = params.get("PeerAddress")
        route_server_endpoint_id = params.get("RouteServerEndpointId")
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            return {"Error": "DryRunOperation"}

        if not bgp_options_dict:
            raise ValueError("BgpOptions is required")
        if not peer_address:
            raise ValueError("PeerAddress is required")
        if not route_server_endpoint_id:
            raise ValueError("RouteServerEndpointId is required")

        peer_asn = bgp_options_dict.get("PeerAsn")
        peer_liveness_detection = bgp_options_dict.get("PeerLivenessDetection")

        if peer_asn is None:
            raise ValueError("BgpOptions.PeerAsn is required")
        if not (1 <= peer_asn <= 4294967295):
            raise ValueError("PeerAsn must be between 1 and 4294967295")

        endpoint = self.state.route_server_endpoints.get(route_server_endpoint_id)
        if not endpoint:
            raise ValueError(f"RouteServerEndpoint {route_server_endpoint_id} does not exist")

        route_server_id = endpoint.route_server_id

        # Create RouteServerPeer object
        route_server_peer_id = self.generate_unique_id()
        peer = RouteServerPeer()
        peer.route_server_peer_id = route_server_peer_id
        peer.route_server_endpoint_id = route_server_endpoint_id
        peer.route_server_id = route_server_id
        peer.peer_address = peer_address
        peer.subnet_id = endpoint.subnet_id
        peer.vpc_id = endpoint.vpc_id
        peer.state = RouteServerPeerState.PENDING if hasattr(RouteServerPeerState, "PENDING") else "pending"
        peer.failure_reason = None
        peer.endpoint_eni_id = None
        peer.endpoint_eni_address = None
        peer.bfd_status = RouteServerBfdStatus()
        peer.bfd_status.status = BfdStatusState.DOWN if hasattr(BfdStatusState, "DOWN") else "down"
        peer.bgp_options = RouteServerBgpOptions()
        peer.bgp_options.peer_asn = peer_asn
        if peer_liveness_detection:
            # Validate liveness detection value
            valid_liveness = {"bfd", "bgp-keepalive"}
            if peer_liveness_detection not in valid_liveness:
                raise ValueError(f"PeerLivenessDetection must be one of {valid_liveness}")
            peer.bgp_options.peer_liveness_detection = BgpLivenessDetection()
            peer.bgp_options.peer_liveness_detection.value = peer_liveness_detection
        else:
            peer.bgp_options.peer_liveness_detection = None
        peer.bgp_status = RouteServerBgpStatus()
        peer.bgp_status.status = "down"

        peer.tag_set = []
        # Process tags from tag_specifications
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag_dict in tags:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key and (not key.lower().startswith("aws:")):
                    tag = Tag()
                    tag.Key = key
                    tag.Value = value
                    peer.tag_set.append(tag)

        self.state.route_server_peers[route_server_peer_id] = peer

        response = {
            "requestId": self.generate_request_id(),
            "routeServerPeer": peer.to_dict(),
        }
        return response


    def delete_route_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        route_server_id = params.get("RouteServerId")

        if dry_run:
            return {"Error": "DryRunOperation"}

        if not route_server_id:
            raise ValueError("RouteServerId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer {route_server_id} does not exist")

        # Mark route server as deleting
        route_server.state = RouteServerState.DELETING if hasattr(RouteServerState, "DELETING") else "deleting"

        # Remove associated endpoints
        endpoints_to_delete = [ep_id for ep_id, ep in self.state.route_server_endpoints.items() if ep.route_server_id == route_server_id]
        for ep_id in endpoints_to_delete:
            ep = self.state.route_server_endpoints[ep_id]
            ep.state = RouteServerEndpointState.DELETING if hasattr(RouteServerEndpointState, "DELETING") else "deleting"
            # Remove peers associated with this endpoint
            peers_to_delete = [peer_id for peer_id, peer in self.state.route_server_peers.items() if peer.route_server_endpoint_id == ep_id]
            for peer_id in peers_to_delete:
                peer = self.state.route_server_peers[peer_id]
                peer.state = RouteServerPeerState.DELETING if hasattr(RouteServerPeerState, "DELETING") else "deleting"
                del self.state.route_server_peers[peer_id]
            del self.state.route_server_endpoints[ep_id]

        # Remove associations
        associations_to_delete = [assoc_id for assoc_id, assoc in self.state.route_server_associations.items() if assoc.route_server_id == route_server_id]
        for assoc_id in associations_to_delete:
            del self.state.route_server_associations[assoc_id]

        # Finally remove route server
        route_server.state = RouteServerState.DELETED if hasattr(RouteServerState, "DELETED") else "deleted"
        del self.state.route_servers[route_server_id]

        response = {
            "requestId": self.generate_request_id(),
            "routeServer": route_server.to_dict(),
        }
        return response

    def delete_route_server_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_endpoint_id = params.get("RouteServerEndpointId")
        if not route_server_endpoint_id:
            raise ValueError("RouteServerEndpointId is required")

        # DryRun check
        if params.get("DryRun"):
            # In real AWS, this would check permissions and raise DryRunOperation or UnauthorizedOperation
            # Here we simulate success for DryRun
            return {"requestId": self.generate_request_id(), "DryRun": True}

        endpoint = self.state.route_server_endpoints.get(route_server_endpoint_id)
        if not endpoint:
            # In real AWS, this would raise an error like InvalidRouteServerEndpointId.NotFound
            raise ValueError(f"RouteServerEndpointId {route_server_endpoint_id} does not exist")

        # Mark endpoint as deleting
        endpoint.state = RouteServerEndpointState.DELETING

        # Simulate deletion by removing from state
        deleted_endpoint = self.state.route_server_endpoints.pop(route_server_endpoint_id)

        # Mark deleted state on returned object
        deleted_endpoint.state = RouteServerEndpointState.DELETED

        return {
            "requestId": self.generate_request_id(),
            "routeServerEndpoint": deleted_endpoint.to_dict(),
        }


    def delete_route_server_peer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_peer_id = params.get("RouteServerPeerId")
        if not route_server_peer_id:
            raise ValueError("RouteServerPeerId is required")

        # DryRun check
        if params.get("DryRun"):
            # Simulate DryRun success
            return {"requestId": self.generate_request_id(), "DryRun": True}

        peer = self.state.route_server_peers.get(route_server_peer_id)
        if not peer:
            raise ValueError(f"RouteServerPeerId {route_server_peer_id} does not exist")

        # Mark peer as deleting
        peer.state = RouteServerPeerState.DELETING

        # Remove from state to simulate deletion
        deleted_peer = self.state.route_server_peers.pop(route_server_peer_id)

        # Mark deleted state on returned object
        deleted_peer.state = RouteServerPeerState.DELETED

        return {
            "requestId": self.generate_request_id(),
            "routeServerPeer": deleted_peer.to_dict(),
        }


    def describe_route_server_endpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id(), "DryRun": True}

        # Filters and IDs
        filter_list = []
        # Collect filters from params keys like Filter.1.Name, Filter.1.Values.N
        for key, value in params.items():
            if key.startswith("Filter."):
                # parse filter index and field
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    field = parts[2]
                    # find or create filter dict
                    while len(filter_list) < int(idx):
                        filter_list.append({"Name": None, "Values": []})
                    filter = filter_list[int(idx) - 1]
                    if field == "Name":
                        filter["Name"] = value
                    elif field == "Values":
                        # Values can be multiple, but params likely have multiple keys for Values.N
                        # We'll handle Values.N keys below
                        pass
                    elif field.startswith("Values"):
                        # Values.N
                        filter["Values"].append(value)

        # RouteServerEndpointId.N
        endpoint_ids = []
        for key, value in params.items():
            if key.startswith("RouteServerEndpointId."):
                endpoint_ids.append(value)

        # MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Collect all endpoints
        endpoints = list(self.state.route_server_endpoints.values())

        # Filter by IDs if provided
        if endpoint_ids:
            endpoints = [ep for ep in endpoints if ep.route_server_endpoint_id in endpoint_ids]

        # Apply filters
        def matches_filter(ep, filter):
            name = filter.get("Name")
            values = filter.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to RouteServerEndpoint attributes or tags
            # Common filters might be: route-server-endpoint-id, route-server-id, state, subnet-id, vpc-id, tag:key
            if name == "route-server-endpoint-id":
                return ep.route_server_endpoint_id in values
            elif name == "route-server-id":
                return ep.route_server_id in values
            elif name == "state":
                return ep.state and ep.state.value in values
            elif name == "subnet-id":
                return ep.subnet_id in values
            elif name == "vpc-id":
                return ep.vpc_id in values
            elif name.startswith("tag:"):
                tag_key = name[4:]
                ep_tag_values = [tag.Value for tag in ep.tag_set if tag.Key == tag_key]
                return any(v in ep_tag_values for v in values)
            return True

        for f in filter_list:
            endpoints = [ep for ep in endpoints if matches_filter(ep, f)]

        # Pagination
        total = len(endpoints)
        if max_results is not None:
            endpoints_page = endpoints[start_index : start_index + max_results]
            next_token_out = str(start_index + max_results) if (start_index + max_results) < total else None
        else:
            endpoints_page = endpoints[start_index:]
            next_token_out = None

        return {
            "requestId": self.generate_request_id(),
            "routeServerEndpointSet": [ep.to_dict() for ep in endpoints_page],
            "nextToken": next_token_out,
        }


    def describe_route_server_peers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id(), "DryRun": True}

        # Filters
        filter_list = []
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    field = parts[2]
                    while len(filter_list) < int(idx):
                        filter_list.append({"Name": None, "Values": []})
                    filter = filter_list[int(idx) - 1]
                    if field == "Name":
                        filter["Name"] = value
                    elif field == "Values":
                        pass
                    elif field.startswith("Values"):
                        filter["Values"].append(value)

        # RouteServerPeerId.N
        peer_ids = []
        for key, value in params.items():
            if key.startswith("RouteServerPeerId."):
                peer_ids.append(value)

        # MaxResults and NextToken
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        peers = list(self.state.route_server_peers.values())

        # Filter by IDs if provided
        if peer_ids:
            peers = [p for p in peers if p.route_server_peer_id in peer_ids]

        # Apply filters
        def matches_filter(peer, filter):
            name = filter.get("Name")
            values = filter.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to RouteServerPeer attributes or tags
            # Common filters: route-server-peer-id, route-server-id, state, subnet-id, vpc-id, peer-address, tag:key
            if name == "route-server-peer-id":
                return peer.route_server_peer_id in values
            elif name == "route-server-id":
                return peer.route_server_id in values
            elif name == "state":
                return peer.state and peer.state.value in values
            elif name == "subnet-id":
                return peer.subnet_id in values
            elif name == "vpc-id":
                return peer.vpc_id in values
            elif name == "peer-address":
                return peer.peer_address in values
            elif name.startswith("tag:"):
                tag_key = name[4:]
                peer_tag_values = [tag.Value for tag in peer.tag_set if tag.Key == tag_key]
                return any(v in peer_tag_values for v in values)
            return True

        for f in filter_list:
            peers = [p for p in peers if matches_filter(p, f)]

        # Pagination
        total = len(peers)
        if max_results is not None:
            peers_page = peers[start_index : start_index + max_results]
            next_token_out = str(start_index + max_results) if (start_index + max_results) < total else None
        else:
            peers_page = peers[start_index:]
            next_token_out = None

        return {
            "requestId": self.generate_request_id(),
            "routeServerPeerSet": [p.to_dict() for p in peers_page],
            "nextToken": next_token_out,
        }


    def describe_route_servers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id(), "DryRun": True}

        # Filters
        filter_list = []
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    field = parts[2]
                    while len(filter_list) < int(idx):
                        filter_list.append({"Name": None, "Values": []})
                    filter = filter_list[int(idx) - 1]
                    if field == "Name":
                        filter["Name"] = value
                    elif field == "Values":
                        pass
                    elif field.startswith("Values"):
                        filter["Values"].append(value)

        # RouteServerId.N
        route_server_ids = []
        for key, value in params.items():
            if key.startswith("RouteServerId."):
                route_server_ids.append(value)

        # MaxResults and NextToken
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        route_servers = list(self.state.route_servers.values())

        # Filter by IDs if provided
        if route_server_ids:
            route_servers = [rs for rs in route_servers if rs.route_server_id in route_server_ids]

        # Apply filters
        def matches_filter(rs, filter):
            name = filter.get("Name")
            values = filter.get("Values", [])
            if not name or not values:
                return True
            # Common filters: route-server-id, state, persist-routes-state, sns-notifications-enabled, tag:key
            if name == "route-server-id":
                return rs.route_server_id in values
            elif name == "state":
                return rs.state and rs.state.value in values
            elif name == "persist-routes-state":
                return rs.persist_routes_state and rs.persist_routes_state.value in values
            elif name == "sns-notifications-enabled":
                # values are strings, convert to bool
                bool_values = []
                for v in values:
                    if v.lower() == "true":
                        bool_values.append(True)
                    elif v.lower() == "false":
                        bool_values.append(False)
                return rs.sns_notifications_enabled in bool_values
            elif name.startswith("tag:"):
                tag_key = name[4:]
                rs_tag_values = [tag.Value for tag in rs.tag_set if tag.Key == tag_key]
                return any(v in rs_tag_values for v in values)
            return True

        for f in filter_list:
            route_servers = [rs for rs in route_servers if matches_filter(rs, f)]

        # Pagination
        total = len(route_servers)
        if max_results is not None:
            rs_page = route_servers[start_index : start_index + max_results]
            next_token_out = str(start_index + max_results) if (start_index + max_results) < total else None
        else:
            rs_page = route_servers[start_index:]
            next_token_out = None

        return {
            "requestId": self.generate_request_id(),
            "routeServerSet": [rs.to_dict() for rs in rs_page],
            "nextToken": next_token_out,
        }

    def disable_route_server_propagation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        route_table_id = params.get("RouteTableId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Check permissions - for emulator, assume always allowed
            # Return DryRunOperation error if not allowed
            # Here, we assume allowed, so raise DryRunOperation error to simulate AWS behavior
            # But per instructions, just return error response if not allowed
            # We'll simulate allowed, so no error
            pass

        if not route_server_id:
            raise ValueError("RouteServerId is required")
        if not route_table_id:
            raise ValueError("RouteTableId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer {route_server_id} does not exist")

        # Find the propagation entry for this route_server_id and route_table_id
        propagation_key = (route_server_id, route_table_id)
        # We assume self.state.route_server_propagations is a dict keyed by (route_server_id, route_table_id)
        # If not present, create one with state 'available' to simulate existing propagation
        if not hasattr(self.state, "route_server_propagations"):
            self.state.route_server_propagations = {}

        propagation = self.state.route_server_propagations.get(propagation_key)
        if not propagation:
            # If no propagation exists, create one with state 'available' to disable
            propagation = RouteServerPropagation(
                route_server_id=route_server_id,
                route_table_id=route_table_id,
                state=RouteServerPropagationState.AVAILABLE,
            )
            self.state.route_server_propagations[propagation_key] = propagation

        # Change state to deleting to disable propagation
        propagation.state = RouteServerPropagationState.DELETING

        # For emulator, we can immediately remove or mark as deleted
        # But AWS likely keeps it in deleting state for some time
        # We'll keep it in deleting state

        return {
            "requestId": self.generate_request_id(),
            "routeServerPropagation": propagation.to_dict(),
        }


    def disassociate_route_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        vpc_id = params.get("VpcId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Assume permission granted for emulator
            pass

        if not route_server_id:
            raise ValueError("RouteServerId is required")
        if not vpc_id:
            raise ValueError("VpcId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer {route_server_id} does not exist")

        # Find the association for route_server_id and vpc_id
        # We assume self.state.route_server_associations is a dict keyed by (route_server_id, vpc_id)
        if not hasattr(self.state, "route_server_associations"):
            self.state.route_server_associations = {}

        association_key = (route_server_id, vpc_id)
        association = self.state.route_server_associations.get(association_key)
        if not association:
            # No association exists, create one with state 'associated' to disassociate
            association = RouteServerAssociation(
                route_server_id=route_server_id,
                vpc_id=vpc_id,
                state=RouteServerAssociationState.ASSOCIATED,
            )
            self.state.route_server_associations[association_key] = association

        # Change state to disassociating
        association.state = RouteServerAssociationState.DISASSOCIATING

        # For emulator, we can immediately remove or mark as disassociated
        # We'll mark as disassociating and then remove from dict to simulate disassociation
        del self.state.route_server_associations[association_key]

        # Return association with state disassociating
        association.state = RouteServerAssociationState.DISASSOCIATING

        return {
            "requestId": self.generate_request_id(),
            "routeServerAssociation": association.to_dict(),
        }


    def enable_route_server_propagation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        route_table_id = params.get("RouteTableId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Assume permission granted for emulator
            pass

        if not route_server_id:
            raise ValueError("RouteServerId is required")
        if not route_table_id:
            raise ValueError("RouteTableId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer {route_server_id} does not exist")

        if not hasattr(self.state, "route_server_propagations"):
            self.state.route_server_propagations = {}

        propagation_key = (route_server_id, route_table_id)
        propagation = self.state.route_server_propagations.get(propagation_key)
        if not propagation:
            # Create new propagation with state pending
            propagation = RouteServerPropagation(
                route_server_id=route_server_id,
                route_table_id=route_table_id,
                state=RouteServerPropagationState.PENDING,
            )
            self.state.route_server_propagations[propagation_key] = propagation
        else:
            # If exists, update state to pending
            propagation.state = RouteServerPropagationState.PENDING

        # For emulator, immediately set state to available
        propagation.state = RouteServerPropagationState.AVAILABLE

        return {
            "requestId": self.generate_request_id(),
            "routeServerPropagation": propagation.to_dict(),
        }


    def get_route_server_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Assume permission granted for emulator
            pass

        if not route_server_id:
            raise ValueError("RouteServerId is required")

        if not hasattr(self.state, "route_server_associations"):
            self.state.route_server_associations = {}

        associations = [
            assoc.to_dict()
            for (rs_id, _), assoc in self.state.route_server_associations.items()
            if rs_id == route_server_id
        ]

        return {
            "requestId": self.generate_request_id(),
            "routeServerAssociationSet": associations,
        }


    def get_route_server_propagations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        route_table_id = params.get("RouteTableId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Assume permission granted for emulator
            pass

        if not route_server_id:
            raise ValueError("RouteServerId is required")

        if not hasattr(self.state, "route_server_propagations"):
            self.state.route_server_propagations = {}

        propagations = []
        for (rs_id, rt_id), propagation in self.state.route_server_propagations.items():
            if rs_id != route_server_id:
                continue
            if route_table_id and rt_id != route_table_id:
                continue
            propagations.append(propagation.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "routeServerPropagationSet": propagations,
        }

    def get_route_server_routing_database(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        if not route_server_id:
            raise ValueError("RouteServerId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer with id {route_server_id} does not exist")

        # Filters processing
        filters = params.get("Filter", [])
        # Filters is expected to be a list of dicts with keys "Name" and "Values"
        # Supported filters are not explicitly documented here, so implement basic filtering on route attributes
        def route_matches_filters(route: RouteServerRoute) -> bool:
            if not filters:
                return True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue
                # Implement some common filters based on route attributes
                # Example filter names: "prefix", "route-server-endpoint-id", "route-server-peer-id", "route-status"
                if name == "prefix":
                    if route.prefix not in values:
                        return False
                elif name == "route-server-endpoint-id":
                    if route.route_server_endpoint_id not in values:
                        return False
                elif name == "route-server-peer-id":
                    if route.route_server_peer_id not in values:
                        return False
                elif name == "route-status":
                    if route.route_status not in values:
                        return False
                else:
                    # Unknown filter name, ignore or reject? Here ignore
                    pass
            return True

        # Pagination params
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise ValueError("MaxResults must be between 5 and 1000")
            except Exception:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        next_token = params.get("NextToken")
        # next_token is expected to be a string representing an integer index offset
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
                if start_index < 0:
                    start_index = 0
            except Exception:
                start_index = 0

        # Collect all routes from all endpoints and peers associated with this route server
        # The routes are stored in route_server.routes or similar? The current structure does not show where routes are stored.
        # We must assume routes are stored in self.state.route_server_routes keyed by route_server_id or similar.
        # Since no such attribute is shown, we will assume route_server has attribute route_set: List[RouteServerRoute]
        # If not present, return empty list

        route_set_all = getattr(route_server, "route_set", [])
        if not isinstance(route_set_all, list):
            route_set_all = []

        # Filter routes by filters
        filtered_routes = [r for r in route_set_all if route_matches_filters(r)]

        # Pagination slice
        paged_routes = filtered_routes[start_index:]
        if max_results is not None:
            paged_routes = paged_routes[:max_results]

        # Prepare next token
        new_next_token = None
        if max_results is not None and (start_index + max_results) < len(filtered_routes):
            new_next_token = str(start_index + max_results)

        # Build routeSet response list
        route_set_response = []
        for route in paged_routes:
            route_installation_detail_set = []
            for detail in getattr(route, "route_installation_detail_set", []):
                route_installation_detail_set.append({
                    "routeInstallationStatus": detail.route_installation_status.value if detail.route_installation_status else None,
                    "routeInstallationStatusReason": detail.route_installation_status_reason,
                    "routeTableId": detail.route_table_id,
                })
            route_set_response.append({
                "asPathSet": route.as_path_set if route.as_path_set else [],
                "med": route.med,
                "nextHopIp": route.next_hop_ip,
                "prefix": route.prefix,
                "routeInstallationDetailSet": route_installation_detail_set,
                "routeServerEndpointId": route.route_server_endpoint_id,
                "routeServerPeerId": route.route_server_peer_id,
                "routeStatus": route.route_status.value if route.route_status else None,
            })

        response = {
            "areRoutesPersisted": route_server.persist_routes_state == PersistRoutesState.ENABLED if route_server.persist_routes_state else False,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "routeSet": route_set_response,
        }
        return response


    def modify_route_server(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_server_id = params.get("RouteServerId")
        if not route_server_id:
            raise ValueError("RouteServerId is required")

        route_server = self.state.route_servers.get(route_server_id)
        if not route_server:
            raise ValueError(f"RouteServer with id {route_server_id} does not exist")

        persist_routes = params.get("PersistRoutes")
        persist_routes_duration = params.get("PersistRoutesDuration")
        sns_notifications_enabled = params.get("SnsNotificationsEnabled")

        # Validate PersistRoutes if provided
        valid_persist_routes_values = {"enable", "disable", "reset"}
        if persist_routes is not None:
            if persist_routes not in valid_persist_routes_values:
                raise ValueError(f"PersistRoutes must be one of {valid_persist_routes_values}")

        # Validate PersistRoutesDuration if provided
        if persist_routes_duration is not None:
            try:
                persist_routes_duration = int(persist_routes_duration)
            except Exception:
                raise ValueError("PersistRoutesDuration must be an integer")
            if persist_routes_duration < 1 or persist_routes_duration > 5:
                raise ValueError("PersistRoutesDuration must be between 1 and 5")

        # Update route_server attributes according to PersistRoutes
        # PersistRoutesState enum values: enabling, enabled, resetting, disabling, disabled, modifying
        # Map input persist_routes string to PersistRoutesState enum
        if persist_routes is not None:
            if persist_routes == "enable":
                route_server.persist_routes_state = PersistRoutesState.ENABLED
                # If duration provided, set it, else default 1
                if persist_routes_duration is not None:
                    route_server.persist_routes_duration = persist_routes_duration
                elif route_server.persist_routes_duration is None:
                    route_server.persist_routes_duration = 1
            elif persist_routes == "disable":
                route_server.persist_routes_state = PersistRoutesState.DISABLED
                route_server.persist_routes_duration = None
            elif persist_routes == "reset":
                route_server.persist_routes_state = PersistRoutesState.RESETTING
                # Reset means withdraw all routes and reset route server to empty FIB and RIB
                # We simulate by clearing route_set if exists
                if hasattr(route_server, "route_set"):
                    route_server.route_set.clear()
                route_server.persist_routes_duration = None

        # If PersistRoutesDuration is provided without PersistRoutes, only update duration if state is enabled
        if persist_routes_duration is not None and persist_routes is None:
            if route_server.persist_routes_state == PersistRoutesState.ENABLED:
                route_server.persist_routes_duration = persist_routes_duration
            else:
                # Ignore or raise error? AWS likely ignores or errors. Here we ignore.
                pass

        # Update SNS notifications enabled flag if provided
        if sns_notifications_enabled is not None:
            route_server.sns_notifications_enabled = bool(sns_notifications_enabled)

        # Update state to modifying if any changes
        route_server.state = RouteServerState.MODIFYING

        # After modification, simulate state change to available (in real AWS this is async)
        route_server.state = RouteServerState.AVAILABLE

        response = {
            "requestId": self.generate_request_id(),
            "routeServer": route_server.to_dict(),
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class RouteserversGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateRouteServer", self.associate_route_server)
        self.register_action("CreateRouteServer", self.create_route_server)
        self.register_action("CreateRouteServerEndpoint", self.create_route_server_endpoint)
        self.register_action("CreateRouteServerPeer", self.create_route_server_peer)
        self.register_action("DeleteRouteServer", self.delete_route_server)
        self.register_action("DeleteRouteServerEndpoint", self.delete_route_server_endpoint)
        self.register_action("DeleteRouteServerPeer", self.delete_route_server_peer)
        self.register_action("DescribeRouteServerEndpoints", self.describe_route_server_endpoints)
        self.register_action("DescribeRouteServerPeers", self.describe_route_server_peers)
        self.register_action("DescribeRouteServers", self.describe_route_servers)
        self.register_action("DisableRouteServerPropagation", self.disable_route_server_propagation)
        self.register_action("DisassociateRouteServer", self.disassociate_route_server)
        self.register_action("EnableRouteServerPropagation", self.enable_route_server_propagation)
        self.register_action("GetRouteServerAssociations", self.get_route_server_associations)
        self.register_action("GetRouteServerPropagations", self.get_route_server_propagations)
        self.register_action("GetRouteServerRoutingDatabase", self.get_route_server_routing_database)
        self.register_action("ModifyRouteServer", self.modify_route_server)

    def associate_route_server(self, params):
        return self.backend.associate_route_server(params)

    def create_route_server(self, params):
        return self.backend.create_route_server(params)

    def create_route_server_endpoint(self, params):
        return self.backend.create_route_server_endpoint(params)

    def create_route_server_peer(self, params):
        return self.backend.create_route_server_peer(params)

    def delete_route_server(self, params):
        return self.backend.delete_route_server(params)

    def delete_route_server_endpoint(self, params):
        return self.backend.delete_route_server_endpoint(params)

    def delete_route_server_peer(self, params):
        return self.backend.delete_route_server_peer(params)

    def describe_route_server_endpoints(self, params):
        return self.backend.describe_route_server_endpoints(params)

    def describe_route_server_peers(self, params):
        return self.backend.describe_route_server_peers(params)

    def describe_route_servers(self, params):
        return self.backend.describe_route_servers(params)

    def disable_route_server_propagation(self, params):
        return self.backend.disable_route_server_propagation(params)

    def disassociate_route_server(self, params):
        return self.backend.disassociate_route_server(params)

    def enable_route_server_propagation(self, params):
        return self.backend.enable_route_server_propagation(params)

    def get_route_server_associations(self, params):
        return self.backend.get_route_server_associations(params)

    def get_route_server_propagations(self, params):
        return self.backend.get_route_server_propagations(params)

    def get_route_server_routing_database(self, params):
        return self.backend.get_route_server_routing_database(params)

    def modify_route_server(self, params):
        return self.backend.modify_route_server(params)
