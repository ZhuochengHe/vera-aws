from __future__ import annotations
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid
import random
import json as _json

from ..utils import (
    create_gcp_error, is_error_response,
    make_operation, parse_labels, get_body_param,
)
from ..state import GCPState

@dataclass
class Router:
    interfaces: List[Any] = field(default_factory=list)
    region: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    name: str = ""
    nats: List[Any] = field(default_factory=list)
    encrypted_interconnect_router: bool = False
    description: str = ""
    md5_authentication_keys: List[Any] = field(default_factory=list)
    network: str = ""
    bgp: Dict[str, Any] = field(default_factory=dict)
    bgp_peers: List[Any] = field(default_factory=list)
    id: str = ""

    # Internal dependency tracking — not in API response
    network_name: str = ""  # parent Network name

    route_policies: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["interfaces"] = self.interfaces
        if self.region is not None and self.region != "":
            d["region"] = self.region
        d["params"] = self.params
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["nats"] = self.nats
        d["encryptedInterconnectRouter"] = self.encrypted_interconnect_router
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["md5AuthenticationKeys"] = self.md5_authentication_keys
        if self.network is not None and self.network != "":
            d["network"] = self.network
        d["bgp"] = self.bgp
        d["bgpPeers"] = self.bgp_peers
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#router"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Router_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.routers  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "router") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_router_or_error(self, router_name: str) -> Any:
        resource = self.resources.get(router_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{router_name}' was not found",
                "NOT_FOUND",
            )
        return resource

    @staticmethod
    def _get_route_policy_or_error(router: Router, policy_name: str) -> Any:
        policy = router.route_policies.get(policy_name)
        if not policy:
            return create_gcp_error(
                404,
                f"RoutePolicy {policy_name!r} not found",
                "NOT_FOUND",
            )
        return policy

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a Router resource in the specified project and region using
the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Router") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Router' not found",
                "INVALID_ARGUMENT",
            )
        name = body.get("name") or params.get("name")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )
        if name in self.resources:
            return create_gcp_error(
                409,
                f"Router {name!r} already exists",
                "ALREADY_EXISTS",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        network_ref = body.get("network") or ""
        network_name = normalize_name(network_ref)
        network = None
        if network_name:
            network = self.state.networks.get(network_name)
            if not network:
                return create_gcp_error(
                    404,
                    f"Network '{network_name}' not found",
                    "NOT_FOUND",
                )

        resource = Router(
            interfaces=body.get("interfaces") or [],
            region=region,
            params=body.get("params") or {},
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            name=name,
            nats=body.get("nats") or [],
            encrypted_interconnect_router=body.get("encryptedInterconnectRouter")
            or False,
            description=body.get("description") or "",
            md5_authentication_keys=body.get("md5AuthenticationKeys") or [],
            network=network_ref,
            bgp=body.get("bgp") or {},
            bgp_peers=body.get("bgpPeers") or [],
            id=self._generate_id(),
            network_name=network_name,
        )
        self.resources[resource.name] = resource
        if network and resource.name not in network.router_names:
            network.router_names.append(resource.name)
        resource_link = f"projects/{project}/regions/{region}/routers/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified Router resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of Router resources available to the specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]

        return {
            "kind": "compute#routerList",
            "id": f"projects/{project}/regions/{region}/routers",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of routers.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        scope_key = f"regions/{params.get('region', 'us-central1')}"
        if resources:
            items = {scope_key: {"routers": [r.to_dict() for r in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#routerAggregatedList",
            "id": f"projects/{project}/aggregated/routers",
            "items": items,
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified Router resource with the data included in the
request. This method supportsPATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Router") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(
                400,
                "Router name cannot be changed",
                "INVALID_ARGUMENT",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        if "network" in body:
            network_ref = body.get("network") or ""
            network_name = normalize_name(network_ref)
            new_network = None
            if network_name:
                new_network = self.state.networks.get(network_name)
                if not new_network:
                    return create_gcp_error(
                        404,
                        f"Network '{network_name}' not found",
                        "NOT_FOUND",
                    )
            old_network = None
            if resource.network_name:
                old_network = self.state.networks.get(resource.network_name)
            if old_network and resource.name in old_network.router_names:
                old_network.router_names.remove(resource.name)
            if new_network and resource.name not in new_network.router_names:
                new_network.router_names.append(resource.name)
            resource.network = network_ref
            resource.network_name = network_name
        if "interfaces" in body:
            resource.interfaces = body.get("interfaces") or []
        if "region" in body:
            resource.region = body.get("region") or ""
        if "params" in body:
            resource.params = body.get("params") or {}
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "nats" in body:
            resource.nats = body.get("nats") or []
        if "encryptedInterconnectRouter" in body:
            resource.encrypted_interconnect_router = bool(
                body.get("encryptedInterconnectRouter")
            )
        if "description" in body:
            resource.description = body.get("description") or ""
        if "md5AuthenticationKeys" in body:
            resource.md5_authentication_keys = body.get("md5AuthenticationKeys") or []
        if "bgp" in body:
            resource.bgp = body.get("bgp") or {}
        if "bgpPeers" in body:
            resource.bgp_peers = body.get("bgpPeers") or []

        resource_link = f"projects/{project}/regions/{region}/routers/{resource.name}"
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
        )

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified Router resource with the data included in the
request.  This method conforms toPUT semantics, which requests that the state of the
target resource be created or replaced with ..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Router") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(
                400,
                "Router name cannot be changed",
                "INVALID_ARGUMENT",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        network_ref = body.get("network") or ""
        network_name = normalize_name(network_ref)
        new_network = None
        if network_name:
            new_network = self.state.networks.get(network_name)
            if not new_network:
                return create_gcp_error(
                    404,
                    f"Network '{network_name}' not found",
                    "NOT_FOUND",
                )
        old_network = None
        if resource.network_name:
            old_network = self.state.networks.get(resource.network_name)
        if old_network and resource.name in old_network.router_names:
            old_network.router_names.remove(resource.name)
        if new_network and resource.name not in new_network.router_names:
            new_network.router_names.append(resource.name)

        resource.interfaces = body.get("interfaces") or []
        resource.region = body.get("region") or region
        resource.params = body.get("params") or {}
        resource.creation_timestamp = body.get("creationTimestamp") or (
            resource.creation_timestamp or datetime.now(timezone.utc).isoformat()
        )
        resource.name = body.get("name") or resource.name
        resource.nats = body.get("nats") or []
        resource.encrypted_interconnect_router = bool(
            body.get("encryptedInterconnectRouter")
        )
        resource.description = body.get("description") or ""
        resource.md5_authentication_keys = body.get("md5AuthenticationKeys") or []
        resource.network = network_ref
        resource.bgp = body.get("bgp") or {}
        resource.bgp_peers = body.get("bgpPeers") or []
        resource.network_name = network_name

        resource_link = f"projects/{project}/regions/{region}/routers/{resource.name}"
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )

    def listRoutePolicies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of router route policy subresources available to the
specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        policies = list(resource.route_policies.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                policies = [p for p in policies if p.get("name") == match.group(1)]

        return {
            "kind": "compute#routerRoutePolicyList",
            "id": f"projects/{project}/regions/{region}/routers/{router_name}/listRoutePolicies",
            "items": policies,
            "selfLink": "",
        }

    def getRoutePolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns specified Route Policy"""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        policy_name = params.get("policy") or ""
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'policy' not found",
                "INVALID_ARGUMENT",
            )

        policy = self._get_route_policy_or_error(resource, policy_name)
        if is_error_response(policy):
            return policy
        return policy

    def preview(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preview fields auto-generated during router create andupdate operations.
Calling this method does NOT create or update the router."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Router") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        preview_data = resource.to_dict()
        preview_data.update(body)
        if "name" in body:
            preview_data["name"] = resource.name

        return preview_data

    def getNatMappingInfo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves runtime Nat mapping information of VM endpoints."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        nat_name = params.get("natName") or ""
        if nat_name:
            nat_match = any((nat or {}).get("name") == nat_name for nat in resource.nats)
            if not nat_match:
                return create_gcp_error(
                    404,
                    f"NAT '{nat_name}' not found",
                    "NOT_FOUND",
                )

        return {
            "kind": "compute#vmEndpointNatMappingsList",
            "result": [],
            "selfLink": "",
        }

    def deleteRoutePolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes Route Policy"""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        policy_name = params.get("policy") or ""
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'policy' not found",
                "INVALID_ARGUMENT",
            )

        policy = self._get_route_policy_or_error(resource, policy_name)
        if is_error_response(policy):
            return policy
        resource.route_policies.pop(policy_name, None)

        resource_link = (
            f"projects/{project}/regions/{region}/routers/{router_name}/routePolicies/{policy_name}"
        )
        return make_operation(
            operation_type="deleteRoutePolicy",
            resource_link=resource_link,
            params=params,
        )

    def getRouterStatus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves runtime information of the specified router."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        return {
            "kind": "compute#routerStatusResponse",
            "result": {
                "network": resource.network,
                "bestRoutes": [],
                "bestRoutesForRouter": [],
                "bgpPeerStatus": [],
            },
        }

    def patchRoutePolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches Route Policy"""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RoutePolicy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RoutePolicy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        policy_name = body.get("name") or params.get("policy") or ""
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )

        policy = self._get_route_policy_or_error(resource, policy_name)
        if is_error_response(policy):
            return policy

        policy.update(body)
        resource.route_policies[policy_name] = policy
        resource_link = (
            f"projects/{project}/regions/{region}/routers/{router_name}/routePolicies/{policy_name}"
        )
        return make_operation(
            operation_type="patchRoutePolicy",
            resource_link=resource_link,
            params=params,
        )

    def getNatIpInfo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves runtime NAT IP information."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        nat_name = params.get("natName") or ""
        if nat_name:
            nat_match = any((nat or {}).get("name") == nat_name for nat in resource.nats)
            if not nat_match:
                return create_gcp_error(
                    404,
                    f"NAT '{nat_name}' not found",
                    "NOT_FOUND",
                )

        return {
            "kind": "compute#routerNatIpInfoList",
            "result": [],
            "selfLink": "",
        }

    def updateRoutePolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates or creates new Route Policy"""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RoutePolicy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RoutePolicy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        policy_name = body.get("name") or params.get("policy") or ""
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )

        policy = resource.route_policies.get(policy_name) or {"name": policy_name}
        policy.update(body)
        resource.route_policies[policy_name] = policy

        resource_link = (
            f"projects/{project}/regions/{region}/routers/{router_name}/routePolicies/{policy_name}"
        )
        return make_operation(
            operation_type="updateRoutePolicy",
            resource_link=resource_link,
            params=params,
        )

    def listBgpRoutes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of router bgp routes available to the specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        return {
            "kind": "compute#routerBgpRoutes",
            "routes": [],
            "selfLink": "",
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified Router resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        router_name = params.get("router")
        if not router_name:
            return create_gcp_error(
                400,
                "Required field 'router' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_router_or_error(router_name)
        if is_error_response(resource):
            return resource

        if resource.network_name:
            network = self.state.networks.get(resource.network_name)
            if network and resource.name in network.router_names:
                network.router_names.remove(resource.name)
        self.resources.pop(router_name, None)

        resource_link = f"projects/{project}/regions/{region}/routers/{router_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class router_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'listRoutePolicies': router_RequestParser._parse_listRoutePolicies,
            'getRoutePolicy': router_RequestParser._parse_getRoutePolicy,
            'preview': router_RequestParser._parse_preview,
            'list': router_RequestParser._parse_list,
            'patch': router_RequestParser._parse_patch,
            'getNatMappingInfo': router_RequestParser._parse_getNatMappingInfo,
            'delete': router_RequestParser._parse_delete,
            'get': router_RequestParser._parse_get,
            'deleteRoutePolicy': router_RequestParser._parse_deleteRoutePolicy,
            'getRouterStatus': router_RequestParser._parse_getRouterStatus,
            'patchRoutePolicy': router_RequestParser._parse_patchRoutePolicy,
            'getNatIpInfo': router_RequestParser._parse_getNatIpInfo,
            'updateRoutePolicy': router_RequestParser._parse_updateRoutePolicy,
            'listBgpRoutes': router_RequestParser._parse_listBgpRoutes,
            'aggregatedList': router_RequestParser._parse_aggregatedList,
            'insert': router_RequestParser._parse_insert,
            'update': router_RequestParser._parse_update,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_listRoutePolicies(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_getRoutePolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'policy' in query_params:
            params['policy'] = query_params['policy']
        return params

    @staticmethod
    def _parse_preview(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Body params
        params['Router'] = body.get('Router')
        return params

    @staticmethod
    def _parse_list(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_patch(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Router'] = body.get('Router')
        return params

    @staticmethod
    def _parse_getNatMappingInfo(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'natName' in query_params:
            params['natName'] = query_params['natName']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_delete(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        return params

    @staticmethod
    def _parse_get(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        return params

    @staticmethod
    def _parse_deleteRoutePolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'policy' in query_params:
            params['policy'] = query_params['policy']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_getRouterStatus(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        return params

    @staticmethod
    def _parse_patchRoutePolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['RoutePolicy'] = body.get('RoutePolicy')
        return params

    @staticmethod
    def _parse_getNatIpInfo(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'natName' in query_params:
            params['natName'] = query_params['natName']
        return params

    @staticmethod
    def _parse_updateRoutePolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['RoutePolicy'] = body.get('RoutePolicy')
        return params

    @staticmethod
    def _parse_listBgpRoutes(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'addressFamily' in query_params:
            params['addressFamily'] = query_params['addressFamily']
        if 'destinationPrefix' in query_params:
            params['destinationPrefix'] = query_params['destinationPrefix']
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'peer' in query_params:
            params['peer'] = query_params['peer']
        if 'policyApplied' in query_params:
            params['policyApplied'] = query_params['policyApplied']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        if 'routeType' in query_params:
            params['routeType'] = query_params['routeType']
        return params

    @staticmethod
    def _parse_aggregatedList(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'includeAllScopes' in query_params:
            params['includeAllScopes'] = query_params['includeAllScopes']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        if 'serviceProjectNumber' in query_params:
            params['serviceProjectNumber'] = query_params['serviceProjectNumber']
        return params

    @staticmethod
    def _parse_insert(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Router'] = body.get('Router')
        return params

    @staticmethod
    def _parse_update(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Router'] = body.get('Router')
        return params


class router_ResponseSerializer:
    @staticmethod
    def serialize(
        method_name: str,
        data: Dict[str, Any],
        request_id: str,
    ) -> str:
        if is_error_response(data):
            from ..utils import serialize_gcp_error
            return serialize_gcp_error(data)
        serializers = {
            'listRoutePolicies': router_ResponseSerializer._serialize_listRoutePolicies,
            'getRoutePolicy': router_ResponseSerializer._serialize_getRoutePolicy,
            'preview': router_ResponseSerializer._serialize_preview,
            'list': router_ResponseSerializer._serialize_list,
            'patch': router_ResponseSerializer._serialize_patch,
            'getNatMappingInfo': router_ResponseSerializer._serialize_getNatMappingInfo,
            'delete': router_ResponseSerializer._serialize_delete,
            'get': router_ResponseSerializer._serialize_get,
            'deleteRoutePolicy': router_ResponseSerializer._serialize_deleteRoutePolicy,
            'getRouterStatus': router_ResponseSerializer._serialize_getRouterStatus,
            'patchRoutePolicy': router_ResponseSerializer._serialize_patchRoutePolicy,
            'getNatIpInfo': router_ResponseSerializer._serialize_getNatIpInfo,
            'updateRoutePolicy': router_ResponseSerializer._serialize_updateRoutePolicy,
            'listBgpRoutes': router_ResponseSerializer._serialize_listBgpRoutes,
            'aggregatedList': router_ResponseSerializer._serialize_aggregatedList,
            'insert': router_ResponseSerializer._serialize_insert,
            'update': router_ResponseSerializer._serialize_update,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_listRoutePolicies(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getRoutePolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_preview(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getNatMappingInfo(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_deleteRoutePolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getRouterStatus(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patchRoutePolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getNatIpInfo(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_updateRoutePolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listBgpRoutes(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

