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
class Network:
    name: str = ""
    firewall_policy: str = ""
    gateway_i_pv4: str = ""
    peerings: List[Any] = field(default_factory=list)
    network_firewall_policy_enforcement_order: str = ""
    description: str = ""
    subnetworks: List[Any] = field(default_factory=list)
    enable_ula_internal_ipv6: bool = False
    self_link_with_id: str = ""
    mtu: int = 0
    routing_config: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    internal_ipv6_range: str = ""
    network_profile: str = ""
    i_pv4_range: str = ""
    auto_create_subnetworks: bool = False
    id: str = ""

    # Internal dependency tracking — not in API response
    subnetwork_names: List[str] = field(default_factory=list)  # tracks Subnetwork children
    firewall_names: List[str] = field(default_factory=list)  # tracks Firewall children
    router_names: List[str] = field(default_factory=list)  # tracks Router children
    route_names: List[str] = field(default_factory=list)  # tracks Route children


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.firewall_policy is not None and self.firewall_policy != "":
            d["firewallPolicy"] = self.firewall_policy
        if self.gateway_i_pv4 is not None and self.gateway_i_pv4 != "":
            d["gatewayIPv4"] = self.gateway_i_pv4
        d["peerings"] = self.peerings
        if self.network_firewall_policy_enforcement_order is not None and self.network_firewall_policy_enforcement_order != "":
            d["networkFirewallPolicyEnforcementOrder"] = self.network_firewall_policy_enforcement_order
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["subnetworks"] = self.subnetworks
        d["enableUlaInternalIpv6"] = self.enable_ula_internal_ipv6
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.mtu is not None and self.mtu != 0:
            d["mtu"] = self.mtu
        d["routingConfig"] = self.routing_config
        d["params"] = self.params
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.internal_ipv6_range is not None and self.internal_ipv6_range != "":
            d["internalIpv6Range"] = self.internal_ipv6_range
        if self.network_profile is not None and self.network_profile != "":
            d["networkProfile"] = self.network_profile
        if self.i_pv4_range is not None and self.i_pv4_range != "":
            d["IPv4Range"] = self.i_pv4_range
        d["autoCreateSubnetworks"] = self.auto_create_subnetworks
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#network"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Network_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.networks  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "network") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_network_or_error(
        self,
        network_name: str,
        not_found_message: Optional[str] = None,
    ) -> Any:
        resource = self.resources.get(network_name)
        if resource:
            return resource
        message = not_found_message or f"The resource '{network_name}' was not found"
        return create_gcp_error(404, message, "NOT_FOUND")

    @staticmethod
    def _find_peering(network: Network, peering_name: str) -> Optional[Dict[str, Any]]:
        for peering in network.peerings:
            if peering.get("name") == peering_name:
                return peering
        return None

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a network in the specified project using the data included
in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("Network") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Network' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"The resource '{name}' already exists", "ALREADY_EXISTS")
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = Network(
            name=name,
            firewall_policy=body.get("firewallPolicy", ""),
            gateway_i_pv4=body.get("gatewayIPv4", ""),
            peerings=body.get("peerings", []),
            network_firewall_policy_enforcement_order=body.get("networkFirewallPolicyEnforcementOrder", ""),
            description=body.get("description", ""),
            subnetworks=body.get("subnetworks", []),
            enable_ula_internal_ipv6=body.get("enableUlaInternalIpv6", False),
            self_link_with_id=body.get("selfLinkWithId", ""),
            mtu=body.get("mtu", 0) or 0,
            routing_config=body.get("routingConfig", {}),
            params=body.get("params", {}),
            creation_timestamp=creation_timestamp,
            internal_ipv6_range=body.get("internalIpv6Range", ""),
            network_profile=body.get("networkProfile", ""),
            i_pv4_range=body.get("IPv4Range", ""),
            auto_create_subnetworks=body.get("autoCreateSubnetworks", False),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/networks/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified network."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of networks available to the specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        return {
            "kind": "compute#networkList",
            "id": f"projects/{project}/global/networks",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified network with the data included in the request.
Only routingConfig can be modified."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        body = params.get("Network") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Network' not specified", "INVALID_ARGUMENT")
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "Network name cannot be changed", "INVALID_ARGUMENT")
        if "routingConfig" in body:
            resource.routing_config = body.get("routingConfig") or {}
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/networks/{resource.name}",
            params=params,
        )

    def removePeering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes a peering from the specified network."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        body = params.get("NetworksRemovePeeringRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NetworksRemovePeeringRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        peering_name = body.get("name") or body.get("peeringName")
        if not peering_name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        peering = self._find_peering(resource, peering_name)
        if not peering:
            return create_gcp_error(404, f"Peering {peering_name!r} not found", "NOT_FOUND")
        resource.peerings = [
            item for item in resource.peerings if item.get("name") != peering_name
        ]
        return make_operation(
            operation_type="removePeering",
            resource_link=f"projects/{project}/global/networks/{resource.name}",
            params=params,
        )

    def updatePeering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified network peering with the data included in the
request. You can only modify the NetworkPeering.export_custom_routes field
and the NetworkPeering.import_custom_routes field."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        body = params.get("NetworksUpdatePeeringRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NetworksUpdatePeeringRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        network_peering = body.get("networkPeering") or {}
        peering_name = body.get("name") or body.get("peeringName") or network_peering.get("name")
        if not peering_name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        peering = self._find_peering(resource, peering_name)
        if not peering:
            return create_gcp_error(404, f"Peering {peering_name!r} not found", "NOT_FOUND")
        if "exportCustomRoutes" in network_peering:
            peering["exportCustomRoutes"] = network_peering.get("exportCustomRoutes")
        if "importCustomRoutes" in network_peering:
            peering["importCustomRoutes"] = network_peering.get("importCustomRoutes")
        if "exportCustomRoutes" in body:
            peering["exportCustomRoutes"] = body.get("exportCustomRoutes")
        if "importCustomRoutes" in body:
            peering["importCustomRoutes"] = body.get("importCustomRoutes")
        return make_operation(
            operation_type="updatePeering",
            resource_link=f"projects/{project}/global/networks/{resource.name}",
            params=params,
        )

    def requestRemovePeering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Requests to remove a peering from the specified network. Applicable only
for PeeringConnection with update_strategy=CONSENSUS."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        body = params.get("NetworksRequestRemovePeeringRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NetworksRequestRemovePeeringRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        peering_name = body.get("name") or body.get("peeringName")
        if not peering_name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        peering = self._find_peering(resource, peering_name)
        if not peering:
            return create_gcp_error(404, f"Peering {peering_name!r} not found", "NOT_FOUND")
        update_strategy = peering.get("updateStrategy")
        if update_strategy and update_strategy != "CONSENSUS":
            return create_gcp_error(
                400,
                "Peering update strategy must be CONSENSUS",
                "FAILED_PRECONDITION",
            )
        resource.peerings = [
            item for item in resource.peerings if item.get("name") != peering_name
        ]
        return make_operation(
            operation_type="requestRemovePeering",
            resource_link=f"projects/{project}/global/networks/{resource.name}",
            params=params,
        )

    def listPeeringRoutes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the peering routes exchanged over peering connection."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        peering_name = params.get("peeringName")
        if peering_name:
            peering = self._find_peering(resource, peering_name)
            if not peering:
                return create_gcp_error(404, f"Peering {peering_name!r} not found", "NOT_FOUND")
        return {
            "kind": "compute#exchangedPeeringRoutesList",
            "id": f"projects/{project}/global/networks/{network_name}/listPeeringRoutes",
            "items": [],
            "selfLink": "",
        }

    def switchToCustomMode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Switches the network mode from auto subnet mode to custom subnet mode."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        resource.auto_create_subnetworks = False
        return make_operation(
            operation_type="switchToCustomMode",
            resource_link=f"projects/{project}/global/networks/{resource.name}",
            params=params,
        )

    def getEffectiveFirewalls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the effective firewalls on a given network."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        firewalls = []
        for firewall_name in resource.firewall_names:
            firewall = self.state.firewalls.get(firewall_name)
            if firewall:
                firewalls.append({"firewall": firewall.to_dict()})
        return {
            "firewalls": firewalls,
        }

    def addPeering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds a peering to the specified network."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        body = params.get("NetworksAddPeeringRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NetworksAddPeeringRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        network_peering = body.get("networkPeering") or {}
        peering_name = network_peering.get("name")
        if not peering_name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if self._find_peering(resource, peering_name):
            return create_gcp_error(409, f"Peering {peering_name!r} already exists", "ALREADY_EXISTS")
        peer_network = network_peering.get("network")
        peer_name = peer_network.split("/")[-1] if peer_network else ""
        if peer_name and not self.state.networks.get(peer_name):
            return create_gcp_error(404, f"Network {peer_name!r} not found", "NOT_FOUND")
        resource.peerings.append(network_peering)
        return make_operation(
            operation_type="addPeering",
            resource_link=f"projects/{project}/global/networks/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified network."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        network_name = params.get("network")
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        resource = self._get_network_or_error(network_name)
        if is_error_response(resource):
            return resource
        if (
            resource.subnetwork_names
            or resource.firewall_names
            or resource.router_names
            or resource.route_names
            or resource.peerings
        ):
            return create_gcp_error(400, "Network is in use", "FAILED_PRECONDITION")
        self.resources.pop(network_name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/networks/{network_name}",
            params=params,
        )


class network_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': network_RequestParser._parse_get,
            'removePeering': network_RequestParser._parse_removePeering,
            'list': network_RequestParser._parse_list,
            'insert': network_RequestParser._parse_insert,
            'delete': network_RequestParser._parse_delete,
            'updatePeering': network_RequestParser._parse_updatePeering,
            'patch': network_RequestParser._parse_patch,
            'requestRemovePeering': network_RequestParser._parse_requestRemovePeering,
            'listPeeringRoutes': network_RequestParser._parse_listPeeringRoutes,
            'switchToCustomMode': network_RequestParser._parse_switchToCustomMode,
            'getEffectiveFirewalls': network_RequestParser._parse_getEffectiveFirewalls,
            'addPeering': network_RequestParser._parse_addPeering,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
    def _parse_removePeering(
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
        params['NetworksRemovePeeringRequest'] = body.get('NetworksRemovePeeringRequest')
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
        params['Network'] = body.get('Network')
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
    def _parse_updatePeering(
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
        params['NetworksUpdatePeeringRequest'] = body.get('NetworksUpdatePeeringRequest')
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
        params['Network'] = body.get('Network')
        return params

    @staticmethod
    def _parse_requestRemovePeering(
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
        params['NetworksRequestRemovePeeringRequest'] = body.get('NetworksRequestRemovePeeringRequest')
        return params

    @staticmethod
    def _parse_listPeeringRoutes(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'direction' in query_params:
            params['direction'] = query_params['direction']
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'peeringName' in query_params:
            params['peeringName'] = query_params['peeringName']
        if 'region' in query_params:
            params['region'] = query_params['region']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_switchToCustomMode(
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
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_getEffectiveFirewalls(
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
    def _parse_addPeering(
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
        params['NetworksAddPeeringRequest'] = body.get('NetworksAddPeeringRequest')
        return params


class network_ResponseSerializer:
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
            'get': network_ResponseSerializer._serialize_get,
            'removePeering': network_ResponseSerializer._serialize_removePeering,
            'list': network_ResponseSerializer._serialize_list,
            'insert': network_ResponseSerializer._serialize_insert,
            'delete': network_ResponseSerializer._serialize_delete,
            'updatePeering': network_ResponseSerializer._serialize_updatePeering,
            'patch': network_ResponseSerializer._serialize_patch,
            'requestRemovePeering': network_ResponseSerializer._serialize_requestRemovePeering,
            'listPeeringRoutes': network_ResponseSerializer._serialize_listPeeringRoutes,
            'switchToCustomMode': network_ResponseSerializer._serialize_switchToCustomMode,
            'getEffectiveFirewalls': network_ResponseSerializer._serialize_getEffectiveFirewalls,
            'addPeering': network_ResponseSerializer._serialize_addPeering,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removePeering(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_updatePeering(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_requestRemovePeering(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listPeeringRoutes(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_switchToCustomMode(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getEffectiveFirewalls(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addPeering(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

