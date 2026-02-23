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
class Route:
    params: Dict[str, Any] = field(default_factory=dict)
    next_hop_ilb: str = ""
    next_hop_peering: str = ""
    route_status: str = ""
    next_hop_hub: str = ""
    next_hop_med: int = 0
    next_hop_network: str = ""
    creation_timestamp: str = ""
    priority: int = 0
    route_type: str = ""
    tags: List[Any] = field(default_factory=list)
    description: str = ""
    next_hop_vpn_tunnel: str = ""
    next_hop_interconnect_attachment: str = ""
    name: str = ""
    dest_range: str = ""
    next_hop_inter_region_cost: int = 0
    next_hop_origin: str = ""
    warnings: List[Any] = field(default_factory=list)
    network: str = ""
    next_hop_ip: str = ""
    next_hop_instance: str = ""
    next_hop_gateway: str = ""
    as_paths: List[Any] = field(default_factory=list)
    id: str = ""

    # Internal dependency tracking — not in API response
    network_name: str = ""  # parent Network name


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["params"] = self.params
        if self.next_hop_ilb is not None and self.next_hop_ilb != "":
            d["nextHopIlb"] = self.next_hop_ilb
        if self.next_hop_peering is not None and self.next_hop_peering != "":
            d["nextHopPeering"] = self.next_hop_peering
        if self.route_status is not None and self.route_status != "":
            d["routeStatus"] = self.route_status
        if self.next_hop_hub is not None and self.next_hop_hub != "":
            d["nextHopHub"] = self.next_hop_hub
        if self.next_hop_med is not None and self.next_hop_med != 0:
            d["nextHopMed"] = self.next_hop_med
        if self.next_hop_network is not None and self.next_hop_network != "":
            d["nextHopNetwork"] = self.next_hop_network
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.priority is not None and self.priority != 0:
            d["priority"] = self.priority
        if self.route_type is not None and self.route_type != "":
            d["routeType"] = self.route_type
        d["tags"] = self.tags
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.next_hop_vpn_tunnel is not None and self.next_hop_vpn_tunnel != "":
            d["nextHopVpnTunnel"] = self.next_hop_vpn_tunnel
        if self.next_hop_interconnect_attachment is not None and self.next_hop_interconnect_attachment != "":
            d["nextHopInterconnectAttachment"] = self.next_hop_interconnect_attachment
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.dest_range is not None and self.dest_range != "":
            d["destRange"] = self.dest_range
        if self.next_hop_inter_region_cost is not None and self.next_hop_inter_region_cost != 0:
            d["nextHopInterRegionCost"] = self.next_hop_inter_region_cost
        if self.next_hop_origin is not None and self.next_hop_origin != "":
            d["nextHopOrigin"] = self.next_hop_origin
        d["warnings"] = self.warnings
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.next_hop_ip is not None and self.next_hop_ip != "":
            d["nextHopIp"] = self.next_hop_ip
        if self.next_hop_instance is not None and self.next_hop_instance != "":
            d["nextHopInstance"] = self.next_hop_instance
        if self.next_hop_gateway is not None and self.next_hop_gateway != "":
            d["nextHopGateway"] = self.next_hop_gateway
        d["asPaths"] = self.as_paths
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#route"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Route_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.routes  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "route") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_route_or_error(self, route_name: str) -> Any:
        route = self.resources.get(route_name)
        if not route:
            return create_gcp_error(
                404,
                f"The resource 'routes/{route_name}' was not found",
                "NOT_FOUND",
            )
        return route

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a Route resource in the specified project using the data included
in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("Route") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Route' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"The resource '{name}' already exists", "ALREADY_EXISTS")
        network = body.get("network", "")
        network_name = network.split("/")[-1] if network else ""
        if network_name:
            parent = self.state.networks.get(network_name)
            if not parent:
                return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
        next_hop_network = body.get("nextHopNetwork", "")
        if next_hop_network:
            next_hop_network_name = next_hop_network.split("/")[-1]
            if not self.state.networks.get(next_hop_network_name) and not self.state.networks.get(next_hop_network):
                return create_gcp_error(404, f"Network {next_hop_network_name!r} not found", "NOT_FOUND")
        next_hop_instance = body.get("nextHopInstance", "")
        if next_hop_instance:
            instance_name = next_hop_instance.split("/")[-1]
            instance_found = (
                self.state.instances.get(instance_name)
                or self.state.instances.get(next_hop_instance)
                or self.state.region_instances.get(instance_name)
                or self.state.region_instances.get(next_hop_instance)
            )
            if not instance_found:
                return create_gcp_error(404, f"Instance '{instance_name}' not found", "NOT_FOUND")
        next_hop_vpn_tunnel = body.get("nextHopVpnTunnel", "")
        if next_hop_vpn_tunnel:
            vpn_tunnel_name = next_hop_vpn_tunnel.split("/")[-1]
            if not self.state.vpn_tunnels.get(vpn_tunnel_name) and not self.state.vpn_tunnels.get(next_hop_vpn_tunnel):
                return create_gcp_error(404, f"VpnTunnel '{vpn_tunnel_name}' not found", "NOT_FOUND")
        next_hop_interconnect_attachment = body.get("nextHopInterconnectAttachment", "")
        if next_hop_interconnect_attachment:
            attachment_name = next_hop_interconnect_attachment.split("/")[-1]
            if not self.state.interconnect_attachments.get(attachment_name) and not self.state.interconnect_attachments.get(next_hop_interconnect_attachment):
                return create_gcp_error(404, f"InterconnectAttachment '{attachment_name}' not found", "NOT_FOUND")
        next_hop_ilb = body.get("nextHopIlb", "")
        if next_hop_ilb:
            ilb_name = next_hop_ilb.split("/")[-1]
            ilb_found = (
                self.state.forwarding_rules.get(ilb_name)
                or self.state.forwarding_rules.get(next_hop_ilb)
                or self.state.global_forwarding_rules.get(ilb_name)
                or self.state.global_forwarding_rules.get(next_hop_ilb)
            )
            if not ilb_found:
                return create_gcp_error(404, f"ForwardingRule '{ilb_name}' not found", "NOT_FOUND")
        next_hop_gateway = body.get("nextHopGateway", "")
        if next_hop_gateway:
            gateway_name = next_hop_gateway.split("/")[-1]
            if gateway_name != "default-internet-gateway":
                gateway_found = (
                    self.state.target_vpn_gatewaies.get(gateway_name)
                    or self.state.target_vpn_gatewaies.get(next_hop_gateway)
                    or self.state.vpn_gatewaies.get(gateway_name)
                    or self.state.vpn_gatewaies.get(next_hop_gateway)
                )
                if not gateway_found:
                    return create_gcp_error(404, f"Gateway '{gateway_name}' not found", "NOT_FOUND")
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = Route(
            params=body.get("params", {}),
            next_hop_ilb=next_hop_ilb,
            next_hop_peering=body.get("nextHopPeering", ""),
            route_status=body.get("routeStatus", ""),
            next_hop_hub=body.get("nextHopHub", ""),
            next_hop_med=body.get("nextHopMed", 0) or 0,
            next_hop_network=next_hop_network,
            creation_timestamp=creation_timestamp,
            priority=body.get("priority", 0) or 0,
            route_type=body.get("routeType", ""),
            tags=body.get("tags", []) or [],
            description=body.get("description", ""),
            next_hop_vpn_tunnel=next_hop_vpn_tunnel,
            next_hop_interconnect_attachment=next_hop_interconnect_attachment,
            name=name,
            dest_range=body.get("destRange", ""),
            next_hop_inter_region_cost=body.get("nextHopInterRegionCost", 0) or 0,
            next_hop_origin=body.get("nextHopOrigin", ""),
            warnings=body.get("warnings", []) or [],
            network=network,
            next_hop_ip=body.get("nextHopIp", ""),
            next_hop_instance=next_hop_instance,
            next_hop_gateway=next_hop_gateway,
            as_paths=body.get("asPaths", []) or [],
            id=self._generate_id(),
            network_name=network_name,
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/routes/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified Route resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        route_name = params.get("route")
        if not route_name:
            return create_gcp_error(400, "Required field 'route' not specified", "INVALID_ARGUMENT")
        resource = self._get_route_or_error(route_name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of Route resources available to the specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        return {
            "kind": "compute#routeList",
            "id": f"projects/{project}/global/routes",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        resource_name = params.get("resource")
        body = params.get("TestPermissionsRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_route_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions", []) or []
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified Route resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        route_name = params.get("route")
        if not route_name:
            return create_gcp_error(400, "Required field 'route' not specified", "INVALID_ARGUMENT")
        resource = self._get_route_or_error(route_name)
        if is_error_response(resource):
            return resource
        self.resources.pop(resource.name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/routes/{resource.name}",
            params=params,
        )


class route_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'testIamPermissions': route_RequestParser._parse_testIamPermissions,
            'get': route_RequestParser._parse_get,
            'delete': route_RequestParser._parse_delete,
            'insert': route_RequestParser._parse_insert,
            'list': route_RequestParser._parse_list,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_testIamPermissions(
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
        params['TestPermissionsRequest'] = body.get('TestPermissionsRequest')
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
        params['Route'] = body.get('Route')
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


class route_ResponseSerializer:
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
            'testIamPermissions': route_ResponseSerializer._serialize_testIamPermissions,
            'get': route_ResponseSerializer._serialize_get,
            'delete': route_ResponseSerializer._serialize_delete,
            'insert': route_ResponseSerializer._serialize_insert,
            'list': route_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

