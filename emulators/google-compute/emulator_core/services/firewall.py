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
class Firewall:
    target_tags: List[Any] = field(default_factory=list)
    name: str = ""
    source_tags: List[Any] = field(default_factory=list)
    description: str = ""
    source_ranges: List[Any] = field(default_factory=list)
    target_service_accounts: List[Any] = field(default_factory=list)
    source_service_accounts: List[Any] = field(default_factory=list)
    priority: int = 0
    disabled: bool = False
    creation_timestamp: str = ""
    direction: str = ""
    log_config: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    denied: List[Any] = field(default_factory=list)
    destination_ranges: List[Any] = field(default_factory=list)
    allowed: List[Any] = field(default_factory=list)
    network: str = ""
    id: str = ""

    # Internal dependency tracking — not in API response
    network_name: str = ""  # parent Network name

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["targetTags"] = self.target_tags
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["sourceTags"] = self.source_tags
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["sourceRanges"] = self.source_ranges
        d["targetServiceAccounts"] = self.target_service_accounts
        d["sourceServiceAccounts"] = self.source_service_accounts
        if self.priority is not None and self.priority != 0:
            d["priority"] = self.priority
        d["disabled"] = self.disabled
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.direction is not None and self.direction != "":
            d["direction"] = self.direction
        d["logConfig"] = self.log_config
        d["params"] = self.params
        d["denied"] = self.denied
        d["destinationRanges"] = self.destination_ranges
        d["allowed"] = self.allowed
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#firewall"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Firewall_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.firewalls  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "firewall") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_firewall_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a firewall rule in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("Firewall") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Firewall' not specified", "INVALID_ARGUMENT")
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
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = Firewall(
            target_tags=body.get("targetTags", []),
            name=name,
            source_tags=body.get("sourceTags", []),
            description=body.get("description", ""),
            source_ranges=body.get("sourceRanges", []),
            target_service_accounts=body.get("targetServiceAccounts", []),
            source_service_accounts=body.get("sourceServiceAccounts", []),
            priority=body.get("priority", 0) or 0,
            disabled=body.get("disabled", False),
            creation_timestamp=creation_timestamp,
            direction=body.get("direction", ""),
            log_config=body.get("logConfig", {}),
            params=body.get("params", {}),
            denied=body.get("denied", []),
            destination_ranges=body.get("destinationRanges", []),
            allowed=body.get("allowed", []),
            network=network,
            id=self._generate_id(),
            network_name=network_name,
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/firewalls/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified firewall."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        firewall_name = params.get("firewall")
        if not firewall_name:
            return create_gcp_error(400, "Required field 'firewall' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_or_error(firewall_name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of firewall rules available to the specified
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
            "kind": "compute#firewallList",
            "id": f"projects/{project}/global/firewalls",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified firewall rule with the data included in the
request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        firewall_name = params.get("firewall")
        if not firewall_name:
            return create_gcp_error(400, "Required field 'firewall' not specified", "INVALID_ARGUMENT")
        body = params.get("Firewall") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Firewall' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_or_error(firewall_name)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "Firewall name cannot be changed", "INVALID_ARGUMENT")
        if "network" in body:
            network = body.get("network") or ""
            network_name = network.split("/")[-1] if network else ""
            if network_name:
                parent = self.state.networks.get(network_name)
                if not parent:
                    return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
            resource.network = network
            resource.network_name = network_name
        if "targetTags" in body:
            resource.target_tags = body.get("targetTags") or []
        if "sourceTags" in body:
            resource.source_tags = body.get("sourceTags") or []
        if "description" in body:
            resource.description = body.get("description") or ""
        if "sourceRanges" in body:
            resource.source_ranges = body.get("sourceRanges") or []
        if "targetServiceAccounts" in body:
            resource.target_service_accounts = body.get("targetServiceAccounts") or []
        if "sourceServiceAccounts" in body:
            resource.source_service_accounts = body.get("sourceServiceAccounts") or []
        if "priority" in body:
            resource.priority = body.get("priority") or 0
        if "disabled" in body:
            resource.disabled = bool(body.get("disabled"))
        if "direction" in body:
            resource.direction = body.get("direction") or ""
        if "logConfig" in body:
            resource.log_config = body.get("logConfig") or {}
        if "params" in body:
            resource.params = body.get("params") or {}
        if "denied" in body:
            resource.denied = body.get("denied") or []
        if "destinationRanges" in body:
            resource.destination_ranges = body.get("destinationRanges") or []
        if "allowed" in body:
            resource.allowed = body.get("allowed") or []
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/firewalls/{resource.name}",
            params=params,
        )

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified firewall rule with the data included in the
request.
Note that all fields will be updated if using PUT, even fields that are not
specified. To update individual fields, please..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        firewall_name = params.get("firewall")
        if not firewall_name:
            return create_gcp_error(400, "Required field 'firewall' not specified", "INVALID_ARGUMENT")
        body = params.get("Firewall") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Firewall' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_or_error(firewall_name)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "Firewall name cannot be changed", "INVALID_ARGUMENT")
        network = body.get("network", "")
        network_name = network.split("/")[-1] if network else ""
        if network_name:
            parent = self.state.networks.get(network_name)
            if not parent:
                return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
        resource.target_tags = body.get("targetTags", [])
        resource.source_tags = body.get("sourceTags", [])
        resource.description = body.get("description", "")
        resource.source_ranges = body.get("sourceRanges", [])
        resource.target_service_accounts = body.get("targetServiceAccounts", [])
        resource.source_service_accounts = body.get("sourceServiceAccounts", [])
        resource.priority = body.get("priority", 0) or 0
        resource.disabled = body.get("disabled", False)
        resource.direction = body.get("direction", "")
        resource.log_config = body.get("logConfig", {})
        resource.params = body.get("params", {})
        resource.denied = body.get("denied", [])
        resource.destination_ranges = body.get("destinationRanges", [])
        resource.allowed = body.get("allowed", [])
        resource.network = network
        resource.network_name = network_name
        return make_operation(
            operation_type="update",
            resource_link=f"projects/{project}/global/firewalls/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions", [])
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified firewall."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        firewall_name = params.get("firewall")
        if not firewall_name:
            return create_gcp_error(400, "Required field 'firewall' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_or_error(firewall_name)
        if is_error_response(resource):
            return resource
        self.resources.pop(firewall_name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/firewalls/{firewall_name}",
            params=params,
        )


class firewall_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'delete': firewall_RequestParser._parse_delete,
            'list': firewall_RequestParser._parse_list,
            'patch': firewall_RequestParser._parse_patch,
            'insert': firewall_RequestParser._parse_insert,
            'update': firewall_RequestParser._parse_update,
            'get': firewall_RequestParser._parse_get,
            'testIamPermissions': firewall_RequestParser._parse_testIamPermissions,
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
        params['Firewall'] = body.get('Firewall')
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
        params['Firewall'] = body.get('Firewall')
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
        params['Firewall'] = body.get('Firewall')
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


class firewall_ResponseSerializer:
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
            'delete': firewall_ResponseSerializer._serialize_delete,
            'list': firewall_ResponseSerializer._serialize_list,
            'patch': firewall_ResponseSerializer._serialize_patch,
            'insert': firewall_ResponseSerializer._serialize_insert,
            'update': firewall_ResponseSerializer._serialize_update,
            'get': firewall_ResponseSerializer._serialize_get,
            'testIamPermissions': firewall_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

