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
class TargetVpnGateway:
    network: str = ""
    description: str = ""
    status: str = ""
    forwarding_rules: List[Any] = field(default_factory=list)
    region: str = ""
    creation_timestamp: str = ""
    label_fingerprint: str = ""
    tunnels: List[Any] = field(default_factory=list)
    name: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.status is not None and self.status != "":
            d["status"] = self.status
        d["forwardingRules"] = self.forwarding_rules
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        d["tunnels"] = self.tunnels
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["labels"] = self.labels
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#targetvpngateway"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class TargetVpnGateway_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.target_vpn_gatewaies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "target-vpn-gateway") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def _filter_resources(self, resources: List[TargetVpnGateway], params: Dict[str, Any]) -> List[TargetVpnGateway]:
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        region = params.get("region")
        if region:
            resources = [resource for resource in resources if resource.region == region]
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a target VPN gateway in the specified project and region using
the data included in the request."""
        required_fields = ["project", "region", "TargetVpnGateway"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("TargetVpnGateway") or {}
        name = body.get("name") or self._generate_name()
        if name in self.resources:
            return create_gcp_error(409, f"TargetVpnGateway '{name}' already exists", "ALREADY_EXISTS")
        network = body.get("network", "")
        if network:
            network_resource = self.state.networks.get(network)
            if not network_resource:
                return create_gcp_error(404, f"Network {network!r} not found", "NOT_FOUND")
        resource = TargetVpnGateway(
            network=network,
            description=body.get("description", ""),
            status=body.get("status", ""),
            forwarding_rules=body.get("forwardingRules", []) or [],
            region=params.get("region", ""),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            label_fingerprint=str(uuid.uuid4())[:8],
            tunnels=body.get("tunnels", []) or [],
            name=name,
            labels=body.get("labels", {}) or {},
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=(
                f"projects/{params.get('project')}/regions/{params.get('region')}"
                f"/TargetVpnGateways/{resource.name}"
            ),
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified target VPN gateway."""
        required_fields = ["project", "region", "targetVpnGateway"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource_name = params.get("targetVpnGateway")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != params.get("region"):
            return create_gcp_error(404, f"The resource '{resource_name}' was not found", "NOT_FOUND")
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of target VPN gateways.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        resources = self._filter_resources(resources, params)
        scope_key = f"regions/{params.get('region', 'us-central1')}"
        if resources:
            items = {scope_key: {"targetVpnGateways": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#targetvpngatewayAggregatedList",
            "id": f"projects/{params.get('project', '')}/aggregated/TargetVpnGateways",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of target VPN gateways available to the specified
project and region."""
        required_fields = ["project", "region"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        resources = self._filter_resources(resources, params)
        return {
            "kind": "compute#targetvpngatewayList",
            "id": f"projects/{params.get('project', '')}/regions/{params.get('region', '')}/targetVpnGateways",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a TargetVpnGateway. To learn more about labels, read theLabeling
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
                f"/TargetVpnGateways/{resource.name}"
            ),
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified target VPN gateway."""
        required_fields = ["project", "region", "targetVpnGateway"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource_name = params.get("targetVpnGateway")
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
                f"/TargetVpnGateways/{resource.name}"
            ),
            params=params,
        )


class target_vpn_gateway_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setLabels': target_vpn_gateway_RequestParser._parse_setLabels,
            'insert': target_vpn_gateway_RequestParser._parse_insert,
            'aggregatedList': target_vpn_gateway_RequestParser._parse_aggregatedList,
            'delete': target_vpn_gateway_RequestParser._parse_delete,
            'list': target_vpn_gateway_RequestParser._parse_list,
            'get': target_vpn_gateway_RequestParser._parse_get,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['TargetVpnGateway'] = body.get('TargetVpnGateway')
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


class target_vpn_gateway_ResponseSerializer:
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
            'setLabels': target_vpn_gateway_ResponseSerializer._serialize_setLabels,
            'insert': target_vpn_gateway_ResponseSerializer._serialize_insert,
            'aggregatedList': target_vpn_gateway_ResponseSerializer._serialize_aggregatedList,
            'delete': target_vpn_gateway_ResponseSerializer._serialize_delete,
            'list': target_vpn_gateway_ResponseSerializer._serialize_list,
            'get': target_vpn_gateway_ResponseSerializer._serialize_get,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

