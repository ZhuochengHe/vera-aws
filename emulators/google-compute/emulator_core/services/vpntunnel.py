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
class VpnTunnel:
    peer_external_gateway: str = ""
    vpn_gateway: str = ""
    local_traffic_selector: List[Any] = field(default_factory=list)
    peer_ip: str = ""
    region: str = ""
    detailed_status: str = ""
    shared_secret: str = ""
    cipher_suite: Dict[str, Any] = field(default_factory=dict)
    peer_external_gateway_interface: int = 0
    peer_gcp_gateway: str = ""
    vpn_gateway_interface: int = 0
    description: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    target_vpn_gateway: str = ""
    shared_secret_hash: str = ""
    remote_traffic_selector: List[Any] = field(default_factory=list)
    creation_timestamp: str = ""
    router: str = ""
    ike_version: int = 0
    status: str = ""
    name: str = ""
    label_fingerprint: str = ""
    id: str = ""

    # Internal dependency tracking — not in API response
    vpn_gateway_name: str = ""  # parent VpnGateway name


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.peer_external_gateway is not None and self.peer_external_gateway != "":
            d["peerExternalGateway"] = self.peer_external_gateway
        if self.vpn_gateway is not None and self.vpn_gateway != "":
            d["vpnGateway"] = self.vpn_gateway
        d["localTrafficSelector"] = self.local_traffic_selector
        if self.peer_ip is not None and self.peer_ip != "":
            d["peerIp"] = self.peer_ip
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.detailed_status is not None and self.detailed_status != "":
            d["detailedStatus"] = self.detailed_status
        if self.shared_secret is not None and self.shared_secret != "":
            d["sharedSecret"] = self.shared_secret
        d["cipherSuite"] = self.cipher_suite
        if self.peer_external_gateway_interface is not None and self.peer_external_gateway_interface != 0:
            d["peerExternalGatewayInterface"] = self.peer_external_gateway_interface
        if self.peer_gcp_gateway is not None and self.peer_gcp_gateway != "":
            d["peerGcpGateway"] = self.peer_gcp_gateway
        if self.vpn_gateway_interface is not None and self.vpn_gateway_interface != 0:
            d["vpnGatewayInterface"] = self.vpn_gateway_interface
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["labels"] = self.labels
        if self.target_vpn_gateway is not None and self.target_vpn_gateway != "":
            d["targetVpnGateway"] = self.target_vpn_gateway
        if self.shared_secret_hash is not None and self.shared_secret_hash != "":
            d["sharedSecretHash"] = self.shared_secret_hash
        d["remoteTrafficSelector"] = self.remote_traffic_selector
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.router is not None and self.router != "":
            d["router"] = self.router
        if self.ike_version is not None and self.ike_version != 0:
            d["ikeVersion"] = self.ike_version
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#vpntunnel"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class VpnTunnel_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.vpn_tunnels  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "vpn-tunnel") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a VpnTunnel resource in the specified project and region using
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
        body = params.get("VpnTunnel") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'VpnTunnel' not found",
                "INVALID_ARGUMENT",
            )
        name = body.get("name") or self._generate_name()
        if name in self.resources:
            return create_gcp_error(409, f"VpnTunnel {name!r} already exists", "ALREADY_EXISTS")

        def extract_name(ref: Any) -> str:
            if isinstance(ref, dict):
                ref = ref.get("name") or ref.get("selfLink") or ""
            if isinstance(ref, str) and ref:
                return ref.split("/")[-1]
            return ""

        vpn_gateway_ref = body.get("vpnGateway") or ""
        vpn_gateway_name = extract_name(vpn_gateway_ref)
        if vpn_gateway_name and not self.state.vpn_gatewaies.get(vpn_gateway_name):
            return create_gcp_error(404, f"VpnGateway {vpn_gateway_name!r} not found", "NOT_FOUND")
        target_vpn_gateway_ref = body.get("targetVpnGateway") or ""
        target_vpn_gateway_name = extract_name(target_vpn_gateway_ref)
        if target_vpn_gateway_name and not self.state.target_vpn_gatewaies.get(target_vpn_gateway_name):
            return create_gcp_error(
                404,
                f"TargetVpnGateway {target_vpn_gateway_name!r} not found",
                "NOT_FOUND",
            )
        peer_external_gateway_ref = body.get("peerExternalGateway") or ""
        peer_external_gateway_name = extract_name(peer_external_gateway_ref)
        if peer_external_gateway_name and not self.state.external_vpn_gatewaies.get(peer_external_gateway_name):
            return create_gcp_error(
                404,
                f"ExternalVpnGateway {peer_external_gateway_name!r} not found",
                "NOT_FOUND",
            )
        peer_gcp_gateway_ref = body.get("peerGcpGateway") or ""
        peer_gcp_gateway_name = extract_name(peer_gcp_gateway_ref)
        if peer_gcp_gateway_name and not self.state.vpn_gatewaies.get(peer_gcp_gateway_name):
            return create_gcp_error(
                404,
                f"VpnGateway {peer_gcp_gateway_name!r} not found",
                "NOT_FOUND",
            )
        router_ref = body.get("router") or ""
        router_name = extract_name(router_ref)
        if router_name and not self.state.routers.get(router_name):
            return create_gcp_error(404, f"Router {router_name!r} not found", "NOT_FOUND")

        resource = VpnTunnel(
            peer_external_gateway=peer_external_gateway_ref,
            vpn_gateway=vpn_gateway_ref,
            local_traffic_selector=body.get("localTrafficSelector") or [],
            peer_ip=body.get("peerIp") or "",
            region=region,
            detailed_status=body.get("detailedStatus") or "",
            shared_secret=body.get("sharedSecret") or "",
            cipher_suite=body.get("cipherSuite") or {},
            peer_external_gateway_interface=body.get("peerExternalGatewayInterface") or 0,
            peer_gcp_gateway=peer_gcp_gateway_ref,
            vpn_gateway_interface=body.get("vpnGatewayInterface") or 0,
            description=body.get("description") or "",
            labels=body.get("labels", {}) or {},
            target_vpn_gateway=target_vpn_gateway_ref,
            shared_secret_hash=body.get("sharedSecretHash") or "",
            remote_traffic_selector=body.get("remoteTrafficSelector") or [],
            creation_timestamp=body.get("creationTimestamp") or datetime.now(timezone.utc).isoformat(),
            router=router_ref,
            ike_version=body.get("ikeVersion") or 0,
            status=body.get("status") or "",
            name=name,
            label_fingerprint=str(uuid.uuid4())[:8],
            id=self._generate_id(),
            vpn_gateway_name=vpn_gateway_name,
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=(
                f"projects/{params.get('project')}/regions/{params.get('region')}"
                f"/VpnTunnels/{resource.name}"
            ),
            params=params,
        )

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of VpnTunnel resources contained in the specified
project and region."""
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
            "kind": "compute#vpntunnelList",
            "id": f"projects/{project}/regions/{region}/vpnTunnels",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of VPN tunnels.

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

        region = params.get("region")
        if region:
            resources = [r for r in resources if r.region == region]
        scope_key = f"regions/{region or 'us-central1'}"
        if not resources:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items = {scope_key: {"VpnTunnels": [r.to_dict() for r in resources]}}
        return {
            "kind": "compute#vpntunnelAggregatedList",
            "id": f"projects/{project}/aggregated/vpnTunnels",
            "items": items,
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a VpnTunnel. To learn more about labels, read theLabeling
Resources documentation."""
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
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionSetLabelsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionSetLabelsRequest' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/regions/{region}/vpnTunnels/{resource_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/regions/{region}/vpnTunnels/{resource_name}' was not found",
                "NOT_FOUND",
            )
        resource.labels = body.get("labels") or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        resource_link = f"projects/{project}/regions/{region}/vpnTunnels/{resource.name}"
        return make_operation(
            operation_type="setLabels",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified VpnTunnel resource."""
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
        vpn_tunnel = params.get("vpnTunnel")
        if not vpn_tunnel:
            return create_gcp_error(
                400,
                "Required field 'vpnTunnel' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(vpn_tunnel)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/regions/{region}/vpnTunnels/{vpn_tunnel}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/regions/{region}/vpnTunnels/{vpn_tunnel}' was not found",
                "NOT_FOUND",
            )
        del self.resources[vpn_tunnel]
        resource_link = f"projects/{project}/regions/{region}/vpnTunnels/{resource.name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class vpn_tunnel_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': vpn_tunnel_RequestParser._parse_get,
            'insert': vpn_tunnel_RequestParser._parse_insert,
            'list': vpn_tunnel_RequestParser._parse_list,
            'aggregatedList': vpn_tunnel_RequestParser._parse_aggregatedList,
            'delete': vpn_tunnel_RequestParser._parse_delete,
            'setLabels': vpn_tunnel_RequestParser._parse_setLabels,
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
        params['VpnTunnel'] = body.get('VpnTunnel')
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
    def _parse_setLabels(
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
        params['RegionSetLabelsRequest'] = body.get('RegionSetLabelsRequest')
        return params


class vpn_tunnel_ResponseSerializer:
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
            'get': vpn_tunnel_ResponseSerializer._serialize_get,
            'insert': vpn_tunnel_ResponseSerializer._serialize_insert,
            'list': vpn_tunnel_ResponseSerializer._serialize_list,
            'aggregatedList': vpn_tunnel_ResponseSerializer._serialize_aggregatedList,
            'delete': vpn_tunnel_ResponseSerializer._serialize_delete,
            'setLabels': vpn_tunnel_ResponseSerializer._serialize_setLabels,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

