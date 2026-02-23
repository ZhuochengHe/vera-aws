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
class HttpHealthCheck:
    unhealthy_threshold: int = 0
    healthy_threshold: int = 0
    request_path: str = ""
    timeout_sec: int = 0
    host: str = ""
    port: int = 0
    check_interval_sec: int = 0
    creation_timestamp: str = ""
    description: str = ""
    name: str = ""
    id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.unhealthy_threshold is not None and self.unhealthy_threshold != 0:
            d["unhealthyThreshold"] = self.unhealthy_threshold
        if self.healthy_threshold is not None and self.healthy_threshold != 0:
            d["healthyThreshold"] = self.healthy_threshold
        if self.request_path is not None and self.request_path != "":
            d["requestPath"] = self.request_path
        if self.timeout_sec is not None and self.timeout_sec != 0:
            d["timeoutSec"] = self.timeout_sec
        if self.host is not None and self.host != "":
            d["host"] = self.host
        if self.port is not None and self.port != 0:
            d["port"] = self.port
        if self.check_interval_sec is not None and self.check_interval_sec != 0:
            d["checkIntervalSec"] = self.check_interval_sec
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#httphealthcheck"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class HttpHealthCheck_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.http_health_checks  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "http-health-check") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a HttpHealthCheck resource in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("HttpHealthCheck")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'HttpHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'name' not specified",
                "INVALID_ARGUMENT",
            )
        if name in self.resources:
            return create_gcp_error(
                409,
                f"HttpHealthCheck '{name}' already exists",
                "ALREADY_EXISTS",
            )

        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = HttpHealthCheck(
            unhealthy_threshold=body.get("unhealthyThreshold", 0) or 0,
            healthy_threshold=body.get("healthyThreshold", 0) or 0,
            request_path=body.get("requestPath", ""),
            timeout_sec=body.get("timeoutSec", 0) or 0,
            host=body.get("host", ""),
            port=body.get("port", 0) or 0,
            check_interval_sec=body.get("checkIntervalSec", 0) or 0,
            creation_timestamp=creation_timestamp,
            description=body.get("description", ""),
            name=name,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/httpHealthChecks/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified HttpHealthCheck resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        http_health_check_name = params.get("httpHealthCheck")
        if not http_health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(http_health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{http_health_check_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of HttpHealthCheck resources available to the specified
project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        return {
            "kind": "compute#httphealthcheckList",
            "id": f"projects/{project}/global/httpHealthChecks",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a HttpHealthCheck resource in the specified project using the data
included in the request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        http_health_check_name = params.get("httpHealthCheck")
        if not http_health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("HttpHealthCheck") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HttpHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(http_health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{http_health_check_name}' was not found",
                "NOT_FOUND",
            )

        body_name = body.get("name") if "name" in body else http_health_check_name
        if body_name != http_health_check_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"HttpHealthCheck '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        if "unhealthyThreshold" in body:
            resource.unhealthy_threshold = body.get("unhealthyThreshold") or 0
        if "healthyThreshold" in body:
            resource.healthy_threshold = body.get("healthyThreshold") or 0
        if "requestPath" in body:
            resource.request_path = body.get("requestPath") or ""
        if "timeoutSec" in body:
            resource.timeout_sec = body.get("timeoutSec") or 0
        if "host" in body:
            resource.host = body.get("host") or ""
        if "port" in body:
            resource.port = body.get("port") or 0
        if "checkIntervalSec" in body:
            resource.check_interval_sec = body.get("checkIntervalSec") or 0
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or resource.creation_timestamp
        if "description" in body:
            resource.description = body.get("description") or ""
        if "name" in body:
            resource.name = body_name

        if body_name != http_health_check_name:
            self.resources.pop(http_health_check_name, None)
            self.resources[body_name] = resource

        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/httpHealthChecks/{resource.name}",
            params=params,
        )

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a HttpHealthCheck resource in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        http_health_check_name = params.get("httpHealthCheck")
        if not http_health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("HttpHealthCheck") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HttpHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name") or http_health_check_name

        resource = self.resources.get(http_health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{http_health_check_name}' was not found",
                "NOT_FOUND",
            )
        if body_name != http_health_check_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"HttpHealthCheck '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        resource.unhealthy_threshold = body.get("unhealthyThreshold", 0) or 0
        resource.healthy_threshold = body.get("healthyThreshold", 0) or 0
        resource.request_path = body.get("requestPath", "")
        resource.timeout_sec = body.get("timeoutSec", 0) or 0
        resource.host = body.get("host", "")
        resource.port = body.get("port", 0) or 0
        resource.check_interval_sec = body.get("checkIntervalSec", 0) or 0
        resource.creation_timestamp = body.get("creationTimestamp") or (
            resource.creation_timestamp or datetime.now(timezone.utc).isoformat()
        )
        resource.description = body.get("description", "")
        resource.name = body_name

        if body_name != http_health_check_name:
            self.resources.pop(http_health_check_name, None)
            self.resources[body_name] = resource

        return make_operation(
            operation_type="update",
            resource_link=f"projects/{project}/global/httpHealthChecks/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TestPermissionsRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified HttpHealthCheck resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        http_health_check_name = params.get("httpHealthCheck")
        if not http_health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(http_health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{http_health_check_name}' was not found",
                "NOT_FOUND",
            )

        self.resources.pop(http_health_check_name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/httpHealthChecks/{http_health_check_name}",
            params=params,
        )


class http_health_check_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'patch': http_health_check_RequestParser._parse_patch,
            'delete': http_health_check_RequestParser._parse_delete,
            'list': http_health_check_RequestParser._parse_list,
            'get': http_health_check_RequestParser._parse_get,
            'update': http_health_check_RequestParser._parse_update,
            'testIamPermissions': http_health_check_RequestParser._parse_testIamPermissions,
            'insert': http_health_check_RequestParser._parse_insert,
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
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['HttpHealthCheck'] = body.get('HttpHealthCheck')
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
        params['HttpHealthCheck'] = body.get('HttpHealthCheck')
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
        params['HttpHealthCheck'] = body.get('HttpHealthCheck')
        return params


class http_health_check_ResponseSerializer:
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
            'patch': http_health_check_ResponseSerializer._serialize_patch,
            'delete': http_health_check_ResponseSerializer._serialize_delete,
            'list': http_health_check_ResponseSerializer._serialize_list,
            'get': http_health_check_ResponseSerializer._serialize_get,
            'update': http_health_check_ResponseSerializer._serialize_update,
            'testIamPermissions': http_health_check_ResponseSerializer._serialize_testIamPermissions,
            'insert': http_health_check_ResponseSerializer._serialize_insert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
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

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

