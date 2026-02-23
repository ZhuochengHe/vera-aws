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
class TargetGrpcProxie:
    name: str = ""
    fingerprint: str = ""
    self_link_with_id: str = ""
    validate_for_proxyless: bool = False
    description: str = ""
    creation_timestamp: str = ""
    url_map: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        d["validateForProxyless"] = self.validate_for_proxyless
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.url_map is not None and self.url_map != "":
            d["urlMap"] = self.url_map
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#targetgrpcproxie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class TargetGrpcProxie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.target_grpc_proxies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "target-grpc-proxie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a TargetGrpcProxy in the specified project in the given scope
using the parameters that are included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetGrpcProxy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetGrpcProxy' not found",
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
                f"TargetGrpcProxy '{name}' already exists",
                "ALREADY_EXISTS",
            )

        url_map = body.get("urlMap") or ""
        if url_map and not (
            self.state.url_maps.get(url_map) or self.state.region_url_maps.get(url_map)
        ):
            return create_gcp_error(
                404,
                f"UrlMap '{url_map}' not found",
                "NOT_FOUND",
            )

        resource = TargetGrpcProxie(
            name=name,
            fingerprint=body.get("fingerprint") or "",
            self_link_with_id=body.get("selfLinkWithId") or "",
            validate_for_proxyless=body.get("validateForProxyless") or False,
            description=body.get("description") or "",
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            url_map=url_map,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/global/targetGrpcProxies/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified TargetGrpcProxy resource in the given scope."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_grpc_proxy = params.get("targetGrpcProxy")
        if not target_grpc_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetGrpcProxy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(target_grpc_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_grpc_proxy}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the TargetGrpcProxies for a project in the given scope."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
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
        return {
            "kind": "compute#targetgrpcproxieList",
            "id": f"projects/{project}/global/targetGrpcProxies",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified TargetGrpcProxy resource with the data included in
the request. This method supports PATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_grpc_proxy = params.get("targetGrpcProxy")
        if not target_grpc_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetGrpcProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetGrpcProxy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetGrpcProxy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(target_grpc_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_grpc_proxy}' was not found",
                "NOT_FOUND",
            )

        if "urlMap" in body:
            url_map = body.get("urlMap") or ""
            if url_map and not (
                self.state.url_maps.get(url_map)
                or self.state.region_url_maps.get(url_map)
            ):
                return create_gcp_error(
                    404,
                    f"UrlMap '{url_map}' not found",
                    "NOT_FOUND",
                )
            resource.url_map = url_map
        if "validateForProxyless" in body:
            resource.validate_for_proxyless = body.get("validateForProxyless") or False
        if "description" in body:
            resource.description = body.get("description") or ""
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "selfLinkWithId" in body:
            resource.self_link_with_id = body.get("selfLinkWithId") or ""
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""

        resource_link = f"projects/{project}/global/targetGrpcProxies/{resource.name}"
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified TargetGrpcProxy in the given scope"""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_grpc_proxy = params.get("targetGrpcProxy")
        if not target_grpc_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetGrpcProxy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(target_grpc_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_grpc_proxy}' was not found",
                "NOT_FOUND",
            )

        self.resources.pop(target_grpc_proxy, None)
        resource_link = f"projects/{project}/global/targetGrpcProxies/{target_grpc_proxy}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class target_grpc_proxie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'patch': target_grpc_proxie_RequestParser._parse_patch,
            'list': target_grpc_proxie_RequestParser._parse_list,
            'insert': target_grpc_proxie_RequestParser._parse_insert,
            'delete': target_grpc_proxie_RequestParser._parse_delete,
            'get': target_grpc_proxie_RequestParser._parse_get,
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
        params['TargetGrpcProxy'] = body.get('TargetGrpcProxy')
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
        params['TargetGrpcProxy'] = body.get('TargetGrpcProxy')
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


class target_grpc_proxie_ResponseSerializer:
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
            'patch': target_grpc_proxie_ResponseSerializer._serialize_patch,
            'list': target_grpc_proxie_ResponseSerializer._serialize_list,
            'insert': target_grpc_proxie_ResponseSerializer._serialize_insert,
            'delete': target_grpc_proxie_ResponseSerializer._serialize_delete,
            'get': target_grpc_proxie_ResponseSerializer._serialize_get,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
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

