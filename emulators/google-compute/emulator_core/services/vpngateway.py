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
class VpnGateway:
    vpn_interfaces: List[Any] = field(default_factory=list)
    label_fingerprint: str = ""
    gateway_ip_version: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    network: str = ""
    creation_timestamp: str = ""
    description: str = ""
    region: str = ""
    stack_type: str = ""
    id: str = ""

    # Internal dependency tracking — not in API response
    network_name: str = ""  # parent Network name


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["vpnInterfaces"] = self.vpn_interfaces
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.gateway_ip_version is not None and self.gateway_ip_version != "":
            d["gatewayIpVersion"] = self.gateway_ip_version
        d["labels"] = self.labels
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.stack_type is not None and self.stack_type != "":
            d["stackType"] = self.stack_type
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#vpngateway"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class VpnGateway_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.vpn_gatewaies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "vpn-gateway") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, resource_name: str) -> Any:
        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource {resource_name!r} was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a VPN gateway in the specified project and region using
the data included in the request."""
        required_fields = ["project", "region", "VpnGateway"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(
                    400,
                    f"Required field '{field_name}' is missing",
                    "INVALID_ARGUMENT",
                )
        body = params.get("VpnGateway") or {}
        name = body.get("name") or self._generate_name()
        if name in self.resources:
            return create_gcp_error(409, f"VpnGateway {name!r} already exists", "ALREADY_EXISTS")
        network_ref = body.get("network") or ""
        network_name = ""
        if isinstance(network_ref, str) and network_ref:
            network_name = network_ref.split("/")[-1]
            network = self.state.networks.get(network_name)
            if not network:
                return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
        resource = VpnGateway(
            vpn_interfaces=body.get("vpnInterfaces") or [],
            label_fingerprint=str(uuid.uuid4())[:8],
            gateway_ip_version=body.get("gatewayIpVersion") or "",
            labels=body.get("labels", {}) or {},
            name=name,
            network=network_ref,
            creation_timestamp=body.get("creationTimestamp") or datetime.now(timezone.utc).isoformat(),
            description=body.get("description") or "",
            region=params.get("region", ""),
            stack_type=body.get("stackType") or "",
            id=self._generate_id(),
            network_name=network_name,
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=(
                f"projects/{params.get('project')}/regions/{params.get('region')}"
                f"/VpnGateways/{resource.name}"
            ),
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified VPN gateway."""
        required_fields = ["project", "region", "vpnGateway"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(
                    400,
                    f"Required field '{field_name}' is missing",
                    "INVALID_ARGUMENT",
                )
        resource_name = params.get("vpnGateway")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != params.get("region"):
            return create_gcp_error(404, f"The resource '{resource_name}' was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of VPN gateways available to the specified
project and region."""
        required_fields = ["project", "region"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(
                    400,
                    f"Required field '{field_name}' is missing",
                    "INVALID_ARGUMENT",
                )
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        region = params.get("region")
        if region:
            resources = [resource for resource in resources if resource.region == region]
        return {
            "kind": "compute#vpngatewayList",
            "id": f"projects/{params.get('project', '')}/regions/{params.get('region', '')}/vpnGateways",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of VPN gateways.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        scope_key = f"regions/{params.get('region', 'us-central1')}"
        if resources:
            items = {scope_key: {"VpnGateways": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#vpngatewayAggregatedList",
            "id": f"projects/{params.get('project', '')}/aggregated/VpnGateways",
            "items": items,
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a VpnGateway. To learn more about labels, read theLabeling
Resources documentation."""
        required_fields = ["project", "region", "resource", "RegionSetLabelsRequest"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != params.get("region"):
            return create_gcp_error(404, f"The resource '{resource_name}' was not found", "NOT_FOUND")
        body = params.get("RegionSetLabelsRequest") or {}
        resource.labels = body.get("labels", {}) or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        return make_operation(
            operation_type="setLabels",
            resource_link=(
                f"projects/{params.get('project')}/regions/{params.get('region')}"
                f"/VpnGateways/{resource.name}"
            ),
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        required_fields = ["project", "region", "resource", "TestPermissionsRequest"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != params.get("region"):
            return create_gcp_error(404, f"The resource '{resource_name}' was not found", "NOT_FOUND")
        body = params.get("TestPermissionsRequest") or {}
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": body.get("permissions", []) or [],
        }

    def getStatus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the status for the specified VPN gateway."""
        required_fields = ["project", "region", "vpnGateway"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource_name = params.get("vpnGateway")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != params.get("region"):
            return create_gcp_error(404, f"The resource '{resource_name}' was not found", "NOT_FOUND")
        return resource.to_dict()

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified VPN gateway."""
        required_fields = ["project", "region", "vpnGateway"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource_name = params.get("vpnGateway")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != params.get("region"):
            return create_gcp_error(404, f"The resource '{resource_name}' was not found", "NOT_FOUND")
        del self.resources[resource.name]
        return make_operation(
            operation_type="delete",
            resource_link=(
                f"projects/{params.get('project')}/regions/{params.get('region')}"
                f"/VpnGateways/{resource.name}"
            ),
            params=params,
        )


class vpn_gateway_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'delete': vpn_gateway_RequestParser._parse_delete,
            'testIamPermissions': vpn_gateway_RequestParser._parse_testIamPermissions,
            'insert': vpn_gateway_RequestParser._parse_insert,
            'setLabels': vpn_gateway_RequestParser._parse_setLabels,
            'list': vpn_gateway_RequestParser._parse_list,
            'get': vpn_gateway_RequestParser._parse_get,
            'aggregatedList': vpn_gateway_RequestParser._parse_aggregatedList,
            'getStatus': vpn_gateway_RequestParser._parse_getStatus,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['VpnGateway'] = body.get('VpnGateway')
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
    def _parse_getStatus(
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


class vpn_gateway_ResponseSerializer:
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
            'delete': vpn_gateway_ResponseSerializer._serialize_delete,
            'testIamPermissions': vpn_gateway_ResponseSerializer._serialize_testIamPermissions,
            'insert': vpn_gateway_ResponseSerializer._serialize_insert,
            'setLabels': vpn_gateway_ResponseSerializer._serialize_setLabels,
            'list': vpn_gateway_ResponseSerializer._serialize_list,
            'get': vpn_gateway_ResponseSerializer._serialize_get,
            'aggregatedList': vpn_gateway_ResponseSerializer._serialize_aggregatedList,
            'getStatus': vpn_gateway_ResponseSerializer._serialize_getStatus,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getStatus(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

