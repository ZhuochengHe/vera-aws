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
class GlobalAddresse:
    subnetwork: str = ""
    description: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    address: str = ""
    users: List[Any] = field(default_factory=list)
    creation_timestamp: str = ""
    ip_collection: str = ""
    region: str = ""
    name: str = ""
    network: str = ""
    purpose: str = ""
    network_tier: str = ""
    ip_version: str = ""
    prefix_length: int = 0
    ipv6_endpoint_type: str = ""
    status: str = ""
    address_type: str = ""
    label_fingerprint: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.subnetwork is not None and self.subnetwork != "":
            d["subnetwork"] = self.subnetwork
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["labels"] = self.labels
        if self.address is not None and self.address != "":
            d["address"] = self.address
        d["users"] = self.users
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.ip_collection is not None and self.ip_collection != "":
            d["ipCollection"] = self.ip_collection
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.purpose is not None and self.purpose != "":
            d["purpose"] = self.purpose
        if self.network_tier is not None and self.network_tier != "":
            d["networkTier"] = self.network_tier
        if self.ip_version is not None and self.ip_version != "":
            d["ipVersion"] = self.ip_version
        if self.prefix_length is not None and self.prefix_length != 0:
            d["prefixLength"] = self.prefix_length
        if self.ipv6_endpoint_type is not None and self.ipv6_endpoint_type != "":
            d["ipv6EndpointType"] = self.ipv6_endpoint_type
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.address_type is not None and self.address_type != "":
            d["addressType"] = self.address_type
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#globaladdresse"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class GlobalAddresse_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.global_addresses  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "global-addresse") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an address resource in the specified project by using the data
included in the request."""
        project = params.get("project")
        body = params.get("Address")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'Address' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"Address '{name}' already exists", "ALREADY_EXISTS")
        network = body.get("network", "")
        if network:
            if not self.state.networks.get(network):
                return create_gcp_error(404, f"Network '{network}' not found", "NOT_FOUND")
        subnetwork = body.get("subnetwork", "")
        if subnetwork:
            if not self.state.subnetworks.get(subnetwork):
                return create_gcp_error(404, f"Subnetwork '{subnetwork}' not found", "NOT_FOUND")
        labels = body.get("labels", {})
        label_fingerprint = str(uuid.uuid4())[:8] if labels is not None else ""
        resource = GlobalAddresse(
            subnetwork=subnetwork or "",
            description=body.get("description", ""),
            labels=labels or {},
            address=body.get("address", ""),
            users=body.get("users", []) or [],
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            ip_collection=body.get("ipCollection", ""),
            region=body.get("region", ""),
            name=name,
            network=network or "",
            purpose=body.get("purpose", ""),
            network_tier=body.get("networkTier", ""),
            ip_version=body.get("ipVersion", ""),
            prefix_length=body.get("prefixLength", 0) or 0,
            ipv6_endpoint_type=body.get("ipv6EndpointType", ""),
            status=body.get("status", ""),
            address_type=body.get("addressType", ""),
            label_fingerprint=label_fingerprint,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/addresses/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified address resource."""
        project = params.get("project")
        address = params.get("address")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not address:
            return create_gcp_error(400, "Required field 'address' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(address)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of global addresses."""
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
            "kind": "compute#globaladdresseList",
            "id": f"projects/{project}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a GlobalAddress. To learn more about labels, read theLabeling
Resources documentation."""
        project = params.get("project")
        resource_name = params.get("resource")
        body = params.get("GlobalSetLabelsRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'GlobalSetLabelsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        labels = body.get("labels", {})
        resource.labels = labels or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        return make_operation(
            operation_type="setLabels",
            resource_link=f"projects/{project}/global/addresses/{resource.name}",
            params=params,
        )

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
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions", []) or []
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Moves the specified address resource from one project to another project."""
        project = params.get("project")
        address = params.get("address")
        body = params.get("GlobalAddressesMoveRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not address:
            return create_gcp_error(400, "Required field 'address' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'GlobalAddressesMoveRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(address)
        if is_error_response(resource):
            return resource
        return make_operation(
            operation_type="move",
            resource_link=f"projects/{project}/global/addresses/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified address resource."""
        project = params.get("project")
        address = params.get("address")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not address:
            return create_gcp_error(400, "Required field 'address' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(address)
        if is_error_response(resource):
            return resource
        del self.resources[address]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/addresses/{resource.name}",
            params=params,
        )


class global_addresse_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'testIamPermissions': global_addresse_RequestParser._parse_testIamPermissions,
            'setLabels': global_addresse_RequestParser._parse_setLabels,
            'list': global_addresse_RequestParser._parse_list,
            'move': global_addresse_RequestParser._parse_move,
            'insert': global_addresse_RequestParser._parse_insert,
            'delete': global_addresse_RequestParser._parse_delete,
            'get': global_addresse_RequestParser._parse_get,
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
    def _parse_move(
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
        params['GlobalAddressesMoveRequest'] = body.get('GlobalAddressesMoveRequest')
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
        params['Address'] = body.get('Address')
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


class global_addresse_ResponseSerializer:
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
            'testIamPermissions': global_addresse_ResponseSerializer._serialize_testIamPermissions,
            'setLabels': global_addresse_ResponseSerializer._serialize_setLabels,
            'list': global_addresse_ResponseSerializer._serialize_list,
            'move': global_addresse_ResponseSerializer._serialize_move,
            'insert': global_addresse_ResponseSerializer._serialize_insert,
            'delete': global_addresse_ResponseSerializer._serialize_delete,
            'get': global_addresse_ResponseSerializer._serialize_get,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_move(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

