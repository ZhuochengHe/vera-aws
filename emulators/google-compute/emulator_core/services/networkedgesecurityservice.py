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
class NetworkEdgeSecurityService:
    self_link_with_id: str = ""
    description: str = ""
    name: str = ""
    region: str = ""
    creation_timestamp: str = ""
    fingerprint: str = ""
    security_policy: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.security_policy is not None and self.security_policy != "":
            d["securityPolicy"] = self.security_policy
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#networkedgesecurityservice"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class NetworkEdgeSecurityService_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.network_edge_security_services  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "network-edge-security-service") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new service in the specified project using the data included in
the request."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("NetworkEdgeSecurityService") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NetworkEdgeSecurityService' not specified",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(
                409,
                f"NetworkEdgeSecurityService {name!r} already exists",
                "ALREADY_EXISTS",
            )
        security_policy = body.get("securityPolicy") or ""
        if security_policy and not (
            self.state.security_policies.get(security_policy)
            or self.state.region_security_policies.get(security_policy)
        ):
            return create_gcp_error(
                404,
                f"Security policy {security_policy!r} not found",
                "NOT_FOUND",
            )
        creation_timestamp = body.get("creationTimestamp") or datetime.now(timezone.utc).isoformat()
        resource = NetworkEdgeSecurityService(
            self_link_with_id=body.get("selfLinkWithId", ""),
            description=body.get("description", ""),
            name=name,
            region=region,
            creation_timestamp=creation_timestamp,
            fingerprint=body.get("fingerprint", ""),
            security_policy=security_policy,
            id=self._generate_id(),
        )
        if not params.get("validateOnly"):
            self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/networkEdgeSecurityServices/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets a specified NetworkEdgeSecurityService."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("networkEdgeSecurityService")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEdgeSecurityService' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of all NetworkEdgeSecurityService resources available to
the specified project.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
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
        if not resources:
            scope_key = "regions/us-central1"
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items: Dict[str, Any] = {}
            for resource in resources:
                scope_key = f"regions/{resource.region}" if resource.region else "regions/us-central1"
                items.setdefault(scope_key, {"networkEdgeSecurityServices": []})
                items[scope_key]["networkEdgeSecurityServices"].append(resource.to_dict())
        return {
            "kind": "compute#networkedgesecurityserviceAggregatedList",
            "id": f"projects/{project}/aggregated/networkEdgeSecurityServices",
            "items": items,
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified policy with the data included in the request."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("networkEdgeSecurityService")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEdgeSecurityService' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("NetworkEdgeSecurityService") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NetworkEdgeSecurityService' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if "securityPolicy" in body:
            security_policy = body.get("securityPolicy") or ""
            if security_policy and not (
                self.state.security_policies.get(security_policy)
                or self.state.region_security_policies.get(security_policy)
            ):
                return create_gcp_error(
                    404,
                    f"Security policy {security_policy!r} not found",
                    "NOT_FOUND",
                )
            resource.security_policy = security_policy
        if "description" in body:
            resource.description = body.get("description") or ""
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "selfLinkWithId" in body:
            resource.self_link_with_id = body.get("selfLinkWithId") or ""
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/regions/{region}/networkEdgeSecurityServices/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified service."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("networkEdgeSecurityService")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEdgeSecurityService' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        del self.resources[name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/networkEdgeSecurityServices/{name}",
            params=params,
        )


class network_edge_security_service_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'patch': network_edge_security_service_RequestParser._parse_patch,
            'get': network_edge_security_service_RequestParser._parse_get,
            'insert': network_edge_security_service_RequestParser._parse_insert,
            'aggregatedList': network_edge_security_service_RequestParser._parse_aggregatedList,
            'delete': network_edge_security_service_RequestParser._parse_delete,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        if 'paths' in query_params:
            params['paths'] = query_params['paths']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['NetworkEdgeSecurityService'] = body.get('NetworkEdgeSecurityService')
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
        if 'validateOnly' in query_params:
            params['validateOnly'] = query_params['validateOnly']
        # Body params
        params['NetworkEdgeSecurityService'] = body.get('NetworkEdgeSecurityService')
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


class network_edge_security_service_ResponseSerializer:
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
            'patch': network_edge_security_service_ResponseSerializer._serialize_patch,
            'get': network_edge_security_service_ResponseSerializer._serialize_get,
            'insert': network_edge_security_service_ResponseSerializer._serialize_insert,
            'aggregatedList': network_edge_security_service_ResponseSerializer._serialize_aggregatedList,
            'delete': network_edge_security_service_ResponseSerializer._serialize_delete,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
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

