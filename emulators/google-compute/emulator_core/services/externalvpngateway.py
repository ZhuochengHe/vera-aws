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
class ExternalVpnGateway:
    interfaces: List[Any] = field(default_factory=list)
    redundancy_type: str = ""
    name: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    label_fingerprint: str = ""
    description: str = ""
    creation_timestamp: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["interfaces"] = self.interfaces
        if self.redundancy_type is not None and self.redundancy_type != "":
            d["redundancyType"] = self.redundancy_type
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["labels"] = self.labels
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#externalvpngateway"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class ExternalVpnGateway_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.external_vpn_gatewaies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "external-vpn-gateway") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a ExternalVpnGateway in the specified project using
the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("ExternalVpnGateway")
        if not body:
            return create_gcp_error(400, "Required field 'ExternalVpnGateway' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"ExternalVpnGateway {name!r} already exists", "ALREADY_EXISTS")
        resource = ExternalVpnGateway(
            name=name,
            id=self._generate_id(),
            interfaces=body.get("interfaces", []),
            redundancy_type=body.get("redundancyType", ""),
            labels=body.get("labels", {}),
            label_fingerprint=str(uuid.uuid4())[:8],
            description=body.get("description", ""),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/externalVpnGateways/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified externalVpnGateway. Get a list of available
externalVpnGateways by making a list() request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("externalVpnGateway")
        if not name:
            return create_gcp_error(400, "Required field 'externalVpnGateway' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of ExternalVpnGateway available to the specified
project."""
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
            "kind": "compute#externalvpngatewayList",
            "id": f"projects/{project}",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on an ExternalVpnGateway. To learn more about labels,
read the Labeling
Resources documentation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("GlobalSetLabelsRequest")
        if not body:
            return create_gcp_error(400, "Required field 'GlobalSetLabelsRequest' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        resource.labels = body.get("labels", {})
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        return make_operation(
            operation_type="setLabels",
            resource_link=f"projects/{project}/global/externalVpnGateways/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest")
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": body.get("permissions", []),
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified externalVpnGateway."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("externalVpnGateway")
        if not name:
            return create_gcp_error(400, "Required field 'externalVpnGateway' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        del self.resources[name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/externalVpnGateways/{name}",
            params=params,
        )


class external_vpn_gateway_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'delete': external_vpn_gateway_RequestParser._parse_delete,
            'insert': external_vpn_gateway_RequestParser._parse_insert,
            'setLabels': external_vpn_gateway_RequestParser._parse_setLabels,
            'list': external_vpn_gateway_RequestParser._parse_list,
            'get': external_vpn_gateway_RequestParser._parse_get,
            'testIamPermissions': external_vpn_gateway_RequestParser._parse_testIamPermissions,
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
        params['ExternalVpnGateway'] = body.get('ExternalVpnGateway')
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
        params.update(query_params)
        # Body params
        params['GlobalSetLabelsRequest'] = body.get('GlobalSetLabelsRequest')
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


class external_vpn_gateway_ResponseSerializer:
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
            'delete': external_vpn_gateway_ResponseSerializer._serialize_delete,
            'insert': external_vpn_gateway_ResponseSerializer._serialize_insert,
            'setLabels': external_vpn_gateway_ResponseSerializer._serialize_setLabels,
            'list': external_vpn_gateway_ResponseSerializer._serialize_list,
            'get': external_vpn_gateway_ResponseSerializer._serialize_get,
            'testIamPermissions': external_vpn_gateway_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
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
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

