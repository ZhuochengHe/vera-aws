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
class RegionUrlMap:
    path_matchers: List[Any] = field(default_factory=list)
    header_action: Dict[str, Any] = field(default_factory=dict)
    tests: List[Any] = field(default_factory=list)
    default_service: str = ""
    default_custom_error_response_policy: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    name: str = ""
    host_rules: List[Any] = field(default_factory=list)
    default_url_redirect: Dict[str, Any] = field(default_factory=dict)
    region: str = ""
    description: str = ""
    default_route_action: Dict[str, Any] = field(default_factory=dict)
    fingerprint: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["pathMatchers"] = self.path_matchers
        d["headerAction"] = self.header_action
        d["tests"] = self.tests
        if self.default_service is not None and self.default_service != "":
            d["defaultService"] = self.default_service
        d["defaultCustomErrorResponsePolicy"] = self.default_custom_error_response_policy
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["hostRules"] = self.host_rules
        d["defaultUrlRedirect"] = self.default_url_redirect
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["defaultRouteAction"] = self.default_route_action
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regionurlmap"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionUrlMap_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_url_maps  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-url-map") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a UrlMap resource in the specified project using
the data included in the request."""
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
        body = params.get("UrlMap") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'UrlMap' not found",
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
                f"UrlMap '{name}' already exists",
                "ALREADY_EXISTS",
            )

        def service_exists(service_name: str) -> bool:
            return bool(
                self.state.region_backend_services.get(service_name)
                or self.state.backend_services.get(service_name)
                or self.state.backend_buckets.get(service_name)
            )

        default_service = body.get("defaultService") or ""
        if default_service and not service_exists(default_service):
            return create_gcp_error(
                404,
                f"Service '{default_service}' not found",
                "NOT_FOUND",
            )

        path_matchers = body.get("pathMatchers") or []
        for matcher in path_matchers:
            matcher_default_service = matcher.get("defaultService") or ""
            if matcher_default_service and not service_exists(matcher_default_service):
                return create_gcp_error(
                    404,
                    f"Service '{matcher_default_service}' not found",
                    "NOT_FOUND",
                )
            for rule in matcher.get("pathRules") or []:
                service = rule.get("service") or ""
                if service and not service_exists(service):
                    return create_gcp_error(
                        404,
                        f"Service '{service}' not found",
                        "NOT_FOUND",
                    )

        resource = RegionUrlMap(
            path_matchers=path_matchers,
            header_action=body.get("headerAction") or {},
            tests=body.get("tests") or [],
            default_service=default_service,
            default_custom_error_response_policy=body.get(
                "defaultCustomErrorResponsePolicy"
            )
            or {},
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            name=name,
            host_rules=body.get("hostRules") or [],
            default_url_redirect=body.get("defaultUrlRedirect") or {},
            region=region,
            description=body.get("description") or "",
            default_route_action=body.get("defaultRouteAction") or {},
            fingerprint=body.get("fingerprint") or "",
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/regions/{region}/urlMaps/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified UrlMap resource."""
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
        url_map_name = params.get("urlMap")
        if not url_map_name:
            return create_gcp_error(
                400,
                "Required field 'urlMap' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(url_map_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of UrlMap resources available to the specified
project in the specified region."""
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
                    resource
                    for resource in resources
                    if resource.name == match.group(1)
                ]
        resources = [resource for resource in resources if resource.region == region]

        return {
            "kind": "compute#regionurlmapList",
            "id": f"projects/{project}/regions/{region}/urlMaps",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified UrlMap resource with the data included in the
request. This method supportsPATCH
semantics and usesJSON merge
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
        url_map_name = params.get("urlMap")
        if not url_map_name:
            return create_gcp_error(
                400,
                "Required field 'urlMap' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("UrlMap") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'UrlMap' not found",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name")
        if body_name:
            url_map_name = body_name

        resource = self.resources.get(url_map_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )

        def service_exists(service_name: str) -> bool:
            return bool(
                self.state.region_backend_services.get(service_name)
                or self.state.backend_services.get(service_name)
                or self.state.backend_buckets.get(service_name)
            )

        if "defaultService" in body:
            default_service = body.get("defaultService") or ""
            if default_service and not service_exists(default_service):
                return create_gcp_error(
                    404,
                    f"Service '{default_service}' not found",
                    "NOT_FOUND",
                )
            resource.default_service = default_service

        if "pathMatchers" in body:
            path_matchers = body.get("pathMatchers") or []
            for matcher in path_matchers:
                matcher_default_service = matcher.get("defaultService") or ""
                if matcher_default_service and not service_exists(matcher_default_service):
                    return create_gcp_error(
                        404,
                        f"Service '{matcher_default_service}' not found",
                        "NOT_FOUND",
                    )
                for rule in matcher.get("pathRules") or []:
                    service = rule.get("service") or ""
                    if service and not service_exists(service):
                        return create_gcp_error(
                            404,
                            f"Service '{service}' not found",
                            "NOT_FOUND",
                        )
            resource.path_matchers = path_matchers

        if "headerAction" in body:
            resource.header_action = body.get("headerAction") or {}
        if "tests" in body:
            resource.tests = body.get("tests") or []
        if "defaultCustomErrorResponsePolicy" in body:
            resource.default_custom_error_response_policy = body.get(
                "defaultCustomErrorResponsePolicy"
            ) or {}
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "name" in body:
            resource.name = url_map_name
        if "hostRules" in body:
            resource.host_rules = body.get("hostRules") or []
        if "defaultUrlRedirect" in body:
            resource.default_url_redirect = body.get("defaultUrlRedirect") or {}
        if "region" in body:
            resource.region = body.get("region") or ""
        if "description" in body:
            resource.description = body.get("description") or ""
        if "defaultRouteAction" in body:
            resource.default_route_action = body.get("defaultRouteAction") or {}
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""

        if body_name and body_name != params.get("urlMap"):
            existing = self.resources.get(params.get("urlMap", ""))
            if existing is resource:
                self.resources.pop(params.get("urlMap"), None)
                self.resources[url_map_name] = resource

        resource_link = f"projects/{project}/regions/{region}/urlMaps/{resource.name}"
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
        )

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified UrlMap resource with the data included in the
request."""
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
        url_map_name = params.get("urlMap")
        if not url_map_name:
            return create_gcp_error(
                400,
                "Required field 'urlMap' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("UrlMap") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'UrlMap' not found",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name") or url_map_name

        resource = self.resources.get(url_map_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )
        if body_name != url_map_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"UrlMap '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        def service_exists(service_name: str) -> bool:
            return bool(
                self.state.region_backend_services.get(service_name)
                or self.state.backend_services.get(service_name)
                or self.state.backend_buckets.get(service_name)
            )

        default_service = body.get("defaultService") or ""
        if default_service and not service_exists(default_service):
            return create_gcp_error(
                404,
                f"Service '{default_service}' not found",
                "NOT_FOUND",
            )

        path_matchers = body.get("pathMatchers") or []
        for matcher in path_matchers:
            matcher_default_service = matcher.get("defaultService") or ""
            if matcher_default_service and not service_exists(matcher_default_service):
                return create_gcp_error(
                    404,
                    f"Service '{matcher_default_service}' not found",
                    "NOT_FOUND",
                )
            for rule in matcher.get("pathRules") or []:
                service = rule.get("service") or ""
                if service and not service_exists(service):
                    return create_gcp_error(
                        404,
                        f"Service '{service}' not found",
                        "NOT_FOUND",
                    )

        resource.path_matchers = path_matchers
        resource.header_action = body.get("headerAction") or {}
        resource.tests = body.get("tests") or []
        resource.default_service = default_service
        resource.default_custom_error_response_policy = body.get(
            "defaultCustomErrorResponsePolicy"
        ) or {}
        resource.creation_timestamp = body.get("creationTimestamp") or (
            resource.creation_timestamp or datetime.now(timezone.utc).isoformat()
        )
        resource.name = body_name
        resource.host_rules = body.get("hostRules") or []
        resource.default_url_redirect = body.get("defaultUrlRedirect") or {}
        resource.region = body.get("region") or region
        resource.description = body.get("description") or ""
        resource.default_route_action = body.get("defaultRouteAction") or {}
        resource.fingerprint = body.get("fingerprint") or ""

        if body_name != url_map_name:
            self.resources.pop(url_map_name, None)
            self.resources[body_name] = resource

        resource_link = f"projects/{project}/regions/{region}/urlMaps/{resource.name}"
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )

    def validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Runs static validation for the UrlMap. In particular, the tests of the
provided UrlMap will be run. Calling this method does NOT create the
UrlMap."""
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
        url_map_name = params.get("urlMap")
        if not url_map_name:
            return create_gcp_error(
                400,
                "Required field 'urlMap' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionUrlMapsValidateRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionUrlMapsValidateRequest' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(url_map_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )

        def service_exists(service_name: str) -> bool:
            return bool(
                self.state.region_backend_services.get(service_name)
                or self.state.backend_services.get(service_name)
                or self.state.backend_buckets.get(service_name)
            )

        candidate = body.get("resource") or body.get("UrlMap") or body.get("urlMap")
        if not candidate:
            candidate = resource.to_dict()

        default_service = candidate.get("defaultService") or ""
        if default_service and not service_exists(default_service):
            return create_gcp_error(
                404,
                f"Service '{default_service}' not found",
                "NOT_FOUND",
            )

        path_matchers = candidate.get("pathMatchers") or []
        for matcher in path_matchers:
            matcher_default_service = matcher.get("defaultService") or ""
            if matcher_default_service and not service_exists(matcher_default_service):
                return create_gcp_error(
                    404,
                    f"Service '{matcher_default_service}' not found",
                    "NOT_FOUND",
                )
            for rule in matcher.get("pathRules") or []:
                service = rule.get("service") or ""
                if service and not service_exists(service):
                    return create_gcp_error(
                        404,
                        f"Service '{service}' not found",
                        "NOT_FOUND",
                    )

        return {
            "kind": "compute#urlMapsValidateResponse",
            "result": {
                "loadErrors": [],
                "testFailures": [],
            },
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified UrlMap resource."""
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
        url_map_name = params.get("urlMap")
        if not url_map_name:
            return create_gcp_error(
                400,
                "Required field 'urlMap' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(url_map_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{url_map_name}' was not found",
                "NOT_FOUND",
            )

        self.resources.pop(url_map_name, None)
        resource_link = f"projects/{project}/regions/{region}/urlMaps/{url_map_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class region_url_map_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'validate': region_url_map_RequestParser._parse_validate,
            'list': region_url_map_RequestParser._parse_list,
            'patch': region_url_map_RequestParser._parse_patch,
            'delete': region_url_map_RequestParser._parse_delete,
            'insert': region_url_map_RequestParser._parse_insert,
            'get': region_url_map_RequestParser._parse_get,
            'update': region_url_map_RequestParser._parse_update,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_validate(
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
        params['RegionUrlMapsValidateRequest'] = body.get('RegionUrlMapsValidateRequest')
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
        params['UrlMap'] = body.get('UrlMap')
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
        params['UrlMap'] = body.get('UrlMap')
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
        params['UrlMap'] = body.get('UrlMap')
        return params


class region_url_map_ResponseSerializer:
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
            'validate': region_url_map_ResponseSerializer._serialize_validate,
            'list': region_url_map_ResponseSerializer._serialize_list,
            'patch': region_url_map_ResponseSerializer._serialize_patch,
            'delete': region_url_map_ResponseSerializer._serialize_delete,
            'insert': region_url_map_ResponseSerializer._serialize_insert,
            'get': region_url_map_ResponseSerializer._serialize_get,
            'update': region_url_map_ResponseSerializer._serialize_update,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_validate(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

