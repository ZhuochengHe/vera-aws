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
class RegionHealthCheckService:
    fingerprint: str = ""
    health_checks: List[Any] = field(default_factory=list)
    description: str = ""
    notification_endpoints: List[Any] = field(default_factory=list)
    name: str = ""
    network_endpoint_groups: List[Any] = field(default_factory=list)
    creation_timestamp: str = ""
    health_status_aggregation_policy: str = ""
    region: str = ""
    id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        d["healthChecks"] = self.health_checks
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["notificationEndpoints"] = self.notification_endpoints
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["networkEndpointGroups"] = self.network_endpoint_groups
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.health_status_aggregation_policy is not None and self.health_status_aggregation_policy != "":
            d["healthStatusAggregationPolicy"] = self.health_status_aggregation_policy
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regionhealthcheckservice"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionHealthCheckService_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_health_check_services  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-health-check-service") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a regional HealthCheckService resource in the
specified project and region using the data included in the request."""
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
        body = params.get("HealthCheckService") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HealthCheckService' not found",
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
                f"HealthCheckService '{name}' already exists",
                "ALREADY_EXISTS",
            )

        health_checks = body.get("healthChecks") or []
        for health_check in health_checks:
            if not (
                self.state.health_checks.get(health_check)
                or self.state.region_health_checks.get(health_check)
                or self.state.http_health_checks.get(health_check)
                or self.state.https_health_checks.get(health_check)
                or self.state.region_health_check_services.get(health_check)
            ):
                return create_gcp_error(
                    404,
                    f"Health check '{health_check}' not found",
                    "NOT_FOUND",
                )

        notification_endpoints = body.get("notificationEndpoints") or []
        for endpoint in notification_endpoints:
            if not self.state.region_notification_endpoints.get(endpoint):
                return create_gcp_error(
                    404,
                    f"Notification endpoint '{endpoint}' not found",
                    "NOT_FOUND",
                )

        network_endpoint_groups = body.get("networkEndpointGroups") or []
        for group in network_endpoint_groups:
            if not (
                self.state.network_endpoint_groups.get(group)
                or self.state.region_network_endpoint_groups.get(group)
                or self.state.global_network_endpoint_groups.get(group)
            ):
                return create_gcp_error(
                    404,
                    f"Network endpoint group '{group}' not found",
                    "NOT_FOUND",
                )

        resource = RegionHealthCheckService(
            fingerprint=body.get("fingerprint") or "",
            health_checks=health_checks,
            description=body.get("description") or "",
            notification_endpoints=notification_endpoints,
            name=name,
            network_endpoint_groups=network_endpoint_groups,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            health_status_aggregation_policy=body.get("healthStatusAggregationPolicy")
            or "",
            region=region,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = (
            f"projects/{project}/regions/{region}/healthCheckServices/{resource.name}"
        )
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified regional HealthCheckService resource."""
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
        health_check_service_name = params.get("healthCheckService")
        if not health_check_service_name:
            return create_gcp_error(
                400,
                "Required field 'healthCheckService' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(health_check_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{health_check_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{health_check_service_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all the HealthCheckService resources that have been
configured for the specified project in the given region."""
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
                resources = [
                    resource for resource in resources if resource.name == match.group(1)
                ]
        resources = [resource for resource in resources if resource.region == region]

        return {
            "kind": "compute#regionhealthcheckserviceList",
            "id": f"projects/{project}/regions/{region}/healthCheckServices",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified regional HealthCheckService resource
with the data included in the request.  This method supportsPATCH
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
        health_check_service_name = params.get("healthCheckService")
        if not health_check_service_name:
            return create_gcp_error(
                400,
                "Required field 'healthCheckService' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("HealthCheckService") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'HealthCheckService' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(health_check_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{health_check_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{health_check_service_name}' was not found",
                "NOT_FOUND",
            )

        if "healthChecks" in body:
            health_checks = body.get("healthChecks") or []
            for health_check in health_checks:
                if not (
                    self.state.health_checks.get(health_check)
                    or self.state.region_health_checks.get(health_check)
                    or self.state.http_health_checks.get(health_check)
                    or self.state.https_health_checks.get(health_check)
                    or self.state.region_health_check_services.get(health_check)
                ):
                    return create_gcp_error(
                        404,
                        f"Health check '{health_check}' not found",
                        "NOT_FOUND",
                    )
            resource.health_checks = health_checks

        if "notificationEndpoints" in body:
            notification_endpoints = body.get("notificationEndpoints") or []
            for endpoint in notification_endpoints:
                if not self.state.region_notification_endpoints.get(endpoint):
                    return create_gcp_error(
                        404,
                        f"Notification endpoint '{endpoint}' not found",
                        "NOT_FOUND",
                    )
            resource.notification_endpoints = notification_endpoints

        if "networkEndpointGroups" in body:
            network_endpoint_groups = body.get("networkEndpointGroups") or []
            for group in network_endpoint_groups:
                if not (
                    self.state.network_endpoint_groups.get(group)
                    or self.state.region_network_endpoint_groups.get(group)
                    or self.state.global_network_endpoint_groups.get(group)
                ):
                    return create_gcp_error(
                        404,
                        f"Network endpoint group '{group}' not found",
                        "NOT_FOUND",
                    )
            resource.network_endpoint_groups = network_endpoint_groups

        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "description" in body:
            resource.description = body.get("description") or ""
        if "healthStatusAggregationPolicy" in body:
            resource.health_status_aggregation_policy = (
                body.get("healthStatusAggregationPolicy") or ""
            )
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""

        resource_link = (
            f"projects/{project}/regions/{region}/healthCheckServices/{resource.name}"
        )
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
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
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )

        permissions = body.get("permissions") or []
        return {
            "kind": "compute#testIamPermissionsResponse",
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified regional HealthCheckService."""
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
        health_check_service_name = params.get("healthCheckService")
        if not health_check_service_name:
            return create_gcp_error(
                400,
                "Required field 'healthCheckService' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(health_check_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{health_check_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{health_check_service_name}' was not found",
                "NOT_FOUND",
            )

        del self.resources[health_check_service_name]
        resource_link = (
            f"projects/{project}/regions/{region}/healthCheckServices/{health_check_service_name}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class region_health_check_service_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'patch': region_health_check_service_RequestParser._parse_patch,
            'insert': region_health_check_service_RequestParser._parse_insert,
            'delete': region_health_check_service_RequestParser._parse_delete,
            'get': region_health_check_service_RequestParser._parse_get,
            'list': region_health_check_service_RequestParser._parse_list,
            'testIamPermissions': region_health_check_service_RequestParser._parse_testIamPermissions,
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
        params['HealthCheckService'] = body.get('HealthCheckService')
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
        params['HealthCheckService'] = body.get('HealthCheckService')
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


class region_health_check_service_ResponseSerializer:
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
            'patch': region_health_check_service_ResponseSerializer._serialize_patch,
            'insert': region_health_check_service_ResponseSerializer._serialize_insert,
            'delete': region_health_check_service_ResponseSerializer._serialize_delete,
            'get': region_health_check_service_ResponseSerializer._serialize_get,
            'list': region_health_check_service_ResponseSerializer._serialize_list,
            'testIamPermissions': region_health_check_service_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
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

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

