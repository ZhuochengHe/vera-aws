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
class RegionHealthCheck:
    grpc_tls_health_check: Dict[str, Any] = field(default_factory=dict)
    check_interval_sec: int = 0
    tcp_health_check: Dict[str, Any] = field(default_factory=dict)
    region: str = ""
    ssl_health_check: Dict[str, Any] = field(default_factory=dict)
    unhealthy_threshold: int = 0
    creation_timestamp: str = ""
    name: str = ""
    log_config: Dict[str, Any] = field(default_factory=dict)
    https_health_check: Dict[str, Any] = field(default_factory=dict)
    type: str = ""
    http2_health_check: Dict[str, Any] = field(default_factory=dict)
    source_regions: List[Any] = field(default_factory=list)
    description: str = ""
    grpc_health_check: Dict[str, Any] = field(default_factory=dict)
    http_health_check: Dict[str, Any] = field(default_factory=dict)
    healthy_threshold: int = 0
    timeout_sec: int = 0
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["grpcTlsHealthCheck"] = self.grpc_tls_health_check
        if self.check_interval_sec is not None and self.check_interval_sec != 0:
            d["checkIntervalSec"] = self.check_interval_sec
        d["tcpHealthCheck"] = self.tcp_health_check
        if self.region is not None and self.region != "":
            d["region"] = self.region
        d["sslHealthCheck"] = self.ssl_health_check
        if self.unhealthy_threshold is not None and self.unhealthy_threshold != 0:
            d["unhealthyThreshold"] = self.unhealthy_threshold
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["logConfig"] = self.log_config
        d["httpsHealthCheck"] = self.https_health_check
        if self.type is not None and self.type != "":
            d["type"] = self.type
        d["http2HealthCheck"] = self.http2_health_check
        d["sourceRegions"] = self.source_regions
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["grpcHealthCheck"] = self.grpc_health_check
        d["httpHealthCheck"] = self.http_health_check
        if self.healthy_threshold is not None and self.healthy_threshold != 0:
            d["healthyThreshold"] = self.healthy_threshold
        if self.timeout_sec is not None and self.timeout_sec != 0:
            d["timeoutSec"] = self.timeout_sec
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regionhealthcheck"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionHealthCheck_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_health_checks  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-health-check") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a HealthCheck resource in the specified project using the data
included in the request."""
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
        body = params.get("HealthCheck") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HealthCheck' not found",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )
        if name in self.resources:
            return create_gcp_error(
                409,
                f"HealthCheck '{name}' already exists",
                "ALREADY_EXISTS",
            )

        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = RegionHealthCheck(
            grpc_tls_health_check=body.get("grpcTlsHealthCheck", {}),
            check_interval_sec=body.get("checkIntervalSec", 0) or 0,
            tcp_health_check=body.get("tcpHealthCheck", {}),
            region=region,
            ssl_health_check=body.get("sslHealthCheck", {}),
            unhealthy_threshold=body.get("unhealthyThreshold", 0) or 0,
            creation_timestamp=creation_timestamp,
            name=name,
            log_config=body.get("logConfig", {}),
            https_health_check=body.get("httpsHealthCheck", {}),
            type=body.get("type", ""),
            http2_health_check=body.get("http2HealthCheck", {}),
            source_regions=body.get("sourceRegions", []) or [],
            description=body.get("description", ""),
            grpc_health_check=body.get("grpcHealthCheck", {}),
            http_health_check=body.get("httpHealthCheck", {}),
            healthy_threshold=body.get("healthyThreshold", 0) or 0,
            timeout_sec=body.get("timeoutSec", 0) or 0,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=(
                f"projects/{project}/regions/{region}/healthChecks/{resource.name}"
            ),
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified HealthCheck resource."""
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
        health_check_name = params.get("healthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'healthCheck' not found",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(health_check_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of HealthCheck resources available to the specified
project."""
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
            "kind": "compute#regionhealthcheckList",
            "id": f"projects/{project}/regions/{region}/healthChecks",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a HealthCheck resource in the specified project using the data
included in the request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules."""
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
        health_check_name = params.get("healthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'healthCheck' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("HealthCheck") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HealthCheck' not found",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name")

        resource = self.resources.get(health_check_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )
        if body_name and body_name != health_check_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"HealthCheck '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        if "grpcTlsHealthCheck" in body:
            resource.grpc_tls_health_check = body.get("grpcTlsHealthCheck") or {}
        if "checkIntervalSec" in body:
            resource.check_interval_sec = body.get("checkIntervalSec") or 0
        if "tcpHealthCheck" in body:
            resource.tcp_health_check = body.get("tcpHealthCheck") or {}
        if "region" in body:
            resource.region = body.get("region") or ""
        if "sslHealthCheck" in body:
            resource.ssl_health_check = body.get("sslHealthCheck") or {}
        if "unhealthyThreshold" in body:
            resource.unhealthy_threshold = body.get("unhealthyThreshold") or 0
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "name" in body:
            resource.name = body_name or health_check_name
        if "logConfig" in body:
            resource.log_config = body.get("logConfig") or {}
        if "httpsHealthCheck" in body:
            resource.https_health_check = body.get("httpsHealthCheck") or {}
        if "type" in body:
            resource.type = body.get("type") or ""
        if "http2HealthCheck" in body:
            resource.http2_health_check = body.get("http2HealthCheck") or {}
        if "sourceRegions" in body:
            resource.source_regions = body.get("sourceRegions") or []
        if "description" in body:
            resource.description = body.get("description") or ""
        if "grpcHealthCheck" in body:
            resource.grpc_health_check = body.get("grpcHealthCheck") or {}
        if "httpHealthCheck" in body:
            resource.http_health_check = body.get("httpHealthCheck") or {}
        if "healthyThreshold" in body:
            resource.healthy_threshold = body.get("healthyThreshold") or 0
        if "timeoutSec" in body:
            resource.timeout_sec = body.get("timeoutSec") or 0
        resource.region = region

        if body_name and body_name != health_check_name:
            self.resources.pop(health_check_name, None)
            self.resources[body_name] = resource

        return make_operation(
            operation_type="patch",
            resource_link=(
                f"projects/{project}/regions/{region}/healthChecks/{resource.name}"
            ),
            params=params,
        )

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a HealthCheck resource in the specified project using the data
included in the request."""
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
        health_check_name = params.get("healthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'healthCheck' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("HealthCheck") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HealthCheck' not found",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name") or health_check_name

        resource = self.resources.get(health_check_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )
        if body_name != health_check_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"HealthCheck '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        resource.grpc_tls_health_check = body.get("grpcTlsHealthCheck", {})
        resource.check_interval_sec = body.get("checkIntervalSec", 0) or 0
        resource.tcp_health_check = body.get("tcpHealthCheck", {})
        resource.region = region
        resource.ssl_health_check = body.get("sslHealthCheck", {})
        resource.unhealthy_threshold = body.get("unhealthyThreshold", 0) or 0
        resource.creation_timestamp = body.get("creationTimestamp") or (
            resource.creation_timestamp or datetime.now(timezone.utc).isoformat()
        )
        resource.name = body_name
        resource.log_config = body.get("logConfig", {})
        resource.https_health_check = body.get("httpsHealthCheck", {})
        resource.type = body.get("type", "")
        resource.http2_health_check = body.get("http2HealthCheck", {})
        resource.source_regions = body.get("sourceRegions", []) or []
        resource.description = body.get("description", "")
        resource.grpc_health_check = body.get("grpcHealthCheck", {})
        resource.http_health_check = body.get("httpHealthCheck", {})
        resource.healthy_threshold = body.get("healthyThreshold", 0) or 0
        resource.timeout_sec = body.get("timeoutSec", 0) or 0

        if body_name != health_check_name:
            self.resources.pop(health_check_name, None)
            self.resources[body_name] = resource

        return make_operation(
            operation_type="update",
            resource_link=(
                f"projects/{project}/regions/{region}/healthChecks/{resource.name}"
            ),
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
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
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TestPermissionsRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(resource_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        permissions = body.get("permissions") or []
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified HealthCheck resource."""
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
        health_check_name = params.get("healthCheck")
        if not health_check_name:
            return create_gcp_error(
                400,
                "Required field 'healthCheck' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(health_check_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{health_check_name}' was not found",
                "NOT_FOUND",
            )
        self.resources.pop(health_check_name, None)
        return make_operation(
            operation_type="delete",
            resource_link=(
                f"projects/{project}/regions/{region}/healthChecks/{health_check_name}"
            ),
            params=params,
        )


class region_health_check_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'list': region_health_check_RequestParser._parse_list,
            'delete': region_health_check_RequestParser._parse_delete,
            'patch': region_health_check_RequestParser._parse_patch,
            'update': region_health_check_RequestParser._parse_update,
            'testIamPermissions': region_health_check_RequestParser._parse_testIamPermissions,
            'get': region_health_check_RequestParser._parse_get,
            'insert': region_health_check_RequestParser._parse_insert,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['HealthCheck'] = body.get('HealthCheck')
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
        params['HealthCheck'] = body.get('HealthCheck')
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
        params['HealthCheck'] = body.get('HealthCheck')
        return params


class region_health_check_ResponseSerializer:
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
            'list': region_health_check_ResponseSerializer._serialize_list,
            'delete': region_health_check_ResponseSerializer._serialize_delete,
            'patch': region_health_check_ResponseSerializer._serialize_patch,
            'update': region_health_check_ResponseSerializer._serialize_update,
            'testIamPermissions': region_health_check_ResponseSerializer._serialize_testIamPermissions,
            'get': region_health_check_ResponseSerializer._serialize_get,
            'insert': region_health_check_ResponseSerializer._serialize_insert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
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

