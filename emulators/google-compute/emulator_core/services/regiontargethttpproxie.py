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
class RegionTargetHttpProxie:
    proxy_bind: bool = False
    url_map: str = ""
    fingerprint: str = ""
    name: str = ""
    region: str = ""
    http_keep_alive_timeout_sec: int = 0
    creation_timestamp: str = ""
    description: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["proxyBind"] = self.proxy_bind
        if self.url_map is not None and self.url_map != "":
            d["urlMap"] = self.url_map
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.http_keep_alive_timeout_sec is not None and self.http_keep_alive_timeout_sec != 0:
            d["httpKeepAliveTimeoutSec"] = self.http_keep_alive_timeout_sec
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regiontargethttpproxie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionTargetHttpProxie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_target_http_proxies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-target-http-proxie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a TargetHttpProxy resource in the specified project and region
using the data included in the request."""
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
        body = params.get("TargetHttpProxy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetHttpProxy' not found",
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
                f"TargetHttpProxy '{name}' already exists",
                "ALREADY_EXISTS",
            )

        url_map = body.get("urlMap") or ""
        if url_map and not (
            self.state.region_url_maps.get(url_map)
            or self.state.url_maps.get(url_map)
        ):
            return create_gcp_error(
                404,
                f"UrlMap '{url_map}' not found",
                "NOT_FOUND",
            )

        resource = RegionTargetHttpProxie(
            proxy_bind=body.get("proxyBind") or False,
            url_map=url_map,
            fingerprint=body.get("fingerprint") or "",
            name=name,
            region=region,
            http_keep_alive_timeout_sec=body.get("httpKeepAliveTimeoutSec") or 0,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            description=body.get("description") or "",
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = (
            f"projects/{project}/regions/{region}/targetHttpProxies/{resource.name}"
        )
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified TargetHttpProxy resource in the specified region."""
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
        target_http_proxy = params.get("targetHttpProxy")
        if not target_http_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpProxy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(target_http_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_http_proxy}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{target_http_proxy}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of TargetHttpProxy resources available
to the specified project in the specified region."""
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
            "kind": "compute#regiontargethttpproxieList",
            "id": f"projects/{project}/regions/{region}/targetHttpProxies",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setUrlMap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the URL map for TargetHttpProxy."""
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
        target_http_proxy = params.get("targetHttpProxy")
        if not target_http_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("UrlMapReference") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'UrlMapReference' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(target_http_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_http_proxy}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{target_http_proxy}' was not found",
                "NOT_FOUND",
            )

        url_map = body.get("urlMap") or ""
        if url_map and not (
            self.state.region_url_maps.get(url_map)
            or self.state.url_maps.get(url_map)
        ):
            return create_gcp_error(
                404,
                f"UrlMap '{url_map}' not found",
                "NOT_FOUND",
            )
        resource.url_map = url_map

        resource_link = (
            f"projects/{project}/regions/{region}/targetHttpProxies/{resource.name}"
        )
        return make_operation(
            operation_type="setUrlMap",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified TargetHttpProxy resource."""
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
        target_http_proxy = params.get("targetHttpProxy")
        if not target_http_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpProxy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(target_http_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_http_proxy}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{target_http_proxy}' was not found",
                "NOT_FOUND",
            )

        self.resources.pop(target_http_proxy, None)
        resource_link = (
            f"projects/{project}/regions/{region}/targetHttpProxies/{target_http_proxy}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class region_target_http_proxie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'delete': region_target_http_proxie_RequestParser._parse_delete,
            'list': region_target_http_proxie_RequestParser._parse_list,
            'get': region_target_http_proxie_RequestParser._parse_get,
            'insert': region_target_http_proxie_RequestParser._parse_insert,
            'setUrlMap': region_target_http_proxie_RequestParser._parse_setUrlMap,
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
        params['TargetHttpProxy'] = body.get('TargetHttpProxy')
        return params

    @staticmethod
    def _parse_setUrlMap(
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
        params['UrlMapReference'] = body.get('UrlMapReference')
        return params


class region_target_http_proxie_ResponseSerializer:
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
            'delete': region_target_http_proxie_ResponseSerializer._serialize_delete,
            'list': region_target_http_proxie_ResponseSerializer._serialize_list,
            'get': region_target_http_proxie_ResponseSerializer._serialize_get,
            'insert': region_target_http_proxie_ResponseSerializer._serialize_insert,
            'setUrlMap': region_target_http_proxie_ResponseSerializer._serialize_setUrlMap,
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
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setUrlMap(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

