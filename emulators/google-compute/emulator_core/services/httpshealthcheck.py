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
class HttpsHealthCheck:
    request_path: str = ""
    healthy_threshold: int = 0
    creation_timestamp: str = ""
    name: str = ""
    unhealthy_threshold: int = 0
    host: str = ""
    description: str = ""
    port: int = 0
    timeout_sec: int = 0
    check_interval_sec: int = 0
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.request_path is not None and self.request_path != "":
            d["requestPath"] = self.request_path
        if self.healthy_threshold is not None and self.healthy_threshold != 0:
            d["healthyThreshold"] = self.healthy_threshold
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.unhealthy_threshold is not None and self.unhealthy_threshold != 0:
            d["unhealthyThreshold"] = self.unhealthy_threshold
        if self.host is not None and self.host != "":
            d["host"] = self.host
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.port is not None and self.port != 0:
            d["port"] = self.port
        if self.timeout_sec is not None and self.timeout_sec != 0:
            d["timeoutSec"] = self.timeout_sec
        if self.check_interval_sec is not None and self.check_interval_sec != 0:
            d["checkIntervalSec"] = self.check_interval_sec
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#httpshealthcheck"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class HttpsHealthCheck_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.https_health_checks  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "https-health-check") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a HttpsHealthCheck resource in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("HttpsHealthCheck")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'HttpsHealthCheck' not specified",
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
                f"HttpsHealthCheck '{name}' already exists",
                "ALREADY_EXISTS",
            )

        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = HttpsHealthCheck(
            request_path=body.get("requestPath", ""),
            healthy_threshold=body.get("healthyThreshold", 0) or 0,
            creation_timestamp=creation_timestamp,
            name=name,
            unhealthy_threshold=body.get("unhealthyThreshold", 0) or 0,
            host=body.get("host", ""),
            description=body.get("description", ""),
            port=body.get("port", 0) or 0,
            timeout_sec=body.get("timeoutSec", 0) or 0,
            check_interval_sec=body.get("checkIntervalSec", 0) or 0,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/httpsHealthChecks/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified HttpsHealthCheck resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        health_check_name = params.get("httpsHealthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpsHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of HttpsHealthCheck resources available to the specified
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
            "kind": "compute#httpshealthcheckList",
            "id": f"projects/{project}/global/httpsHealthChecks",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a HttpsHealthCheck resource in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        health_check_name = params.get("httpsHealthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpsHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("HttpsHealthCheck") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HttpsHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name") or health_check_name

        resource = self.resources.get(health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )
        if body_name != health_check_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"HttpsHealthCheck '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        resource.request_path = body.get("requestPath", "")
        resource.healthy_threshold = body.get("healthyThreshold", 0) or 0
        resource.creation_timestamp = body.get("creationTimestamp") or (
            resource.creation_timestamp or datetime.now(timezone.utc).isoformat()
        )
        resource.name = body_name
        resource.unhealthy_threshold = body.get("unhealthyThreshold", 0) or 0
        resource.host = body.get("host", "")
        resource.description = body.get("description", "")
        resource.port = body.get("port", 0) or 0
        resource.timeout_sec = body.get("timeoutSec", 0) or 0
        resource.check_interval_sec = body.get("checkIntervalSec", 0) or 0

        if body_name != health_check_name:
            self.resources.pop(health_check_name, None)
            self.resources[body_name] = resource

        return make_operation(
            operation_type="update",
            resource_link=f"projects/{project}/global/httpsHealthChecks/{resource.name}",
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a HttpsHealthCheck resource in the specified project using the data
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
        health_check_name = params.get("httpsHealthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpsHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("HttpsHealthCheck") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HttpsHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name")

        resource = self.resources.get(health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )
        if body_name and body_name != health_check_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"HttpsHealthCheck '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        if "requestPath" in body:
            resource.request_path = body.get("requestPath") or ""
        if "healthyThreshold" in body:
            resource.healthy_threshold = body.get("healthyThreshold") or 0
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "name" in body:
            resource.name = body_name or health_check_name
        if "unhealthyThreshold" in body:
            resource.unhealthy_threshold = body.get("unhealthyThreshold") or 0
        if "host" in body:
            resource.host = body.get("host") or ""
        if "description" in body:
            resource.description = body.get("description") or ""
        if "port" in body:
            resource.port = body.get("port") or 0
        if "timeoutSec" in body:
            resource.timeout_sec = body.get("timeoutSec") or 0
        if "checkIntervalSec" in body:
            resource.check_interval_sec = body.get("checkIntervalSec") or 0

        if body_name and body_name != health_check_name:
            self.resources.pop(health_check_name, None)
            self.resources[body_name] = resource

        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/httpsHealthChecks/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        resource_name = params.get("resource")
        body = params.get("TestPermissionsRequest")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not specified",
                "INVALID_ARGUMENT",
            )
        if body is None:
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
        permissions = body.get("permissions", []) if isinstance(body, dict) else []
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified HttpsHealthCheck resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        health_check_name = params.get("httpsHealthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'httpsHealthCheck' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(health_check_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )

        self.resources.pop(health_check_name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/httpsHealthChecks/{health_check_name}",
            params=params,
        )


class https_health_check_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'update': https_health_check_RequestParser._parse_update,
            'delete': https_health_check_RequestParser._parse_delete,
            'testIamPermissions': https_health_check_RequestParser._parse_testIamPermissions,
            'get': https_health_check_RequestParser._parse_get,
            'insert': https_health_check_RequestParser._parse_insert,
            'list': https_health_check_RequestParser._parse_list,
            'patch': https_health_check_RequestParser._parse_patch,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['HttpsHealthCheck'] = body.get('HttpsHealthCheck')
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
        params['HttpsHealthCheck'] = body.get('HttpsHealthCheck')
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
        params['HttpsHealthCheck'] = body.get('HttpsHealthCheck')
        return params


class https_health_check_ResponseSerializer:
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
            'update': https_health_check_ResponseSerializer._serialize_update,
            'delete': https_health_check_ResponseSerializer._serialize_delete,
            'testIamPermissions': https_health_check_ResponseSerializer._serialize_testIamPermissions,
            'get': https_health_check_ResponseSerializer._serialize_get,
            'insert': https_health_check_ResponseSerializer._serialize_insert,
            'list': https_health_check_ResponseSerializer._serialize_list,
            'patch': https_health_check_ResponseSerializer._serialize_patch,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

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
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

