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
class TargetTcpProxie:
    proxy_bind: bool = False
    name: str = ""
    description: str = ""
    creation_timestamp: str = ""
    service: str = ""
    proxy_header: str = ""
    region: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["proxyBind"] = self.proxy_bind
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.service is not None and self.service != "":
            d["service"] = self.service
        if self.proxy_header is not None and self.proxy_header != "":
            d["proxyHeader"] = self.proxy_header
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#targettcpproxie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class TargetTcpProxie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.target_tcp_proxies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "target-tcp-proxie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a TargetTcpProxy resource in the specified project using
the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("TargetTcpProxy") or {}
        if not body:
            return create_gcp_error(400, "Required field 'TargetTcpProxy' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"TargetTcpProxy '{name}' already exists", "ALREADY_EXISTS")
        service = body.get("service", "")
        if service:
            service_name = service.split("/")[-1]
            if not self.state.backend_services.get(service_name) and not self.state.backend_services.get(service):
                return create_gcp_error(404, f"BackendService '{service_name}' not found", "NOT_FOUND")
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = TargetTcpProxie(
            proxy_bind=body.get("proxyBind", False),
            name=name,
            description=body.get("description", ""),
            creation_timestamp=creation_timestamp,
            service=service or "",
            proxy_header=body.get("proxyHeader", ""),
            region=body.get("region") or params.get("region", "") or "",
            id=self._generate_id(),
        )
        self.resources[name] = resource
        resource_link = f"projects/{project}/global/targetTcpProxies/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified TargetTcpProxy resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        target_tcp_proxy = params.get("targetTcpProxy")
        if not target_tcp_proxy:
            return create_gcp_error(400, "Required field 'targetTcpProxy' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(target_tcp_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_tcp_proxy}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of all TargetTcpProxy resources, regional and global,
available to the specified project.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter..."""
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
        region = params.get("region")
        if region:
            resources = [resource for resource in resources if resource.region == region]
        zone = params.get("zone")
        if zone and hasattr(resources[0] if resources else object(), "zone"):
            resources = [resource for resource in resources if resource.zone == zone]

        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if resources:
            items = {scope_key: {"TargetTcpProxies": [r.to_dict() for r in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#targettcpproxieAggregatedList",
            "id": f"projects/{project}/aggregated/TargetTcpProxies",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of TargetTcpProxy resources
available to the specified project."""
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
        region = params.get("region")
        if region:
            resources = [resource for resource in resources if resource.region == region]
        zone = params.get("zone")
        if zone and hasattr(resources[0] if resources else object(), "zone"):
            resources = [resource for resource in resources if resource.zone == zone]

        return {
            "kind": "compute#targettcpproxieList",
            "id": f"projects/{project}/global/TargetTcpProxies",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setProxyHeader(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the ProxyHeaderType for TargetTcpProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        target_tcp_proxy = params.get("targetTcpProxy")
        if not target_tcp_proxy:
            return create_gcp_error(400, "Required field 'targetTcpProxy' not specified", "INVALID_ARGUMENT")
        body = params.get("TargetTcpProxiesSetProxyHeaderRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetTcpProxiesSetProxyHeaderRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(target_tcp_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_tcp_proxy}' was not found",
                "NOT_FOUND",
            )
        proxy_header = body.get("proxyHeader")
        if not proxy_header:
            return create_gcp_error(400, "Required field 'proxyHeader' not specified", "INVALID_ARGUMENT")
        resource.proxy_header = proxy_header
        resource_link = f"projects/{project}/global/targetTcpProxies/{resource.name}"
        return make_operation(
            operation_type="setProxyHeader",
            resource_link=resource_link,
            params=params,
        )

    def setBackendService(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the BackendService for TargetTcpProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        target_tcp_proxy = params.get("targetTcpProxy")
        if not target_tcp_proxy:
            return create_gcp_error(400, "Required field 'targetTcpProxy' not specified", "INVALID_ARGUMENT")
        body = params.get("TargetTcpProxiesSetBackendServiceRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetTcpProxiesSetBackendServiceRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(target_tcp_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_tcp_proxy}' was not found",
                "NOT_FOUND",
            )
        service = body.get("service") or ""
        if not service:
            return create_gcp_error(400, "Required field 'service' not specified", "INVALID_ARGUMENT")
        service_name = service.split("/")[-1]
        if not (
            self.state.backend_services.get(service_name)
            or self.state.backend_services.get(service)
            or self.state.region_backend_services.get(service_name)
            or self.state.region_backend_services.get(service)
        ):
            return create_gcp_error(404, f"BackendService '{service_name}' not found", "NOT_FOUND")
        resource.service = service
        resource_link = f"projects/{project}/global/targetTcpProxies/{resource.name}"
        return make_operation(
            operation_type="setBackendService",
            resource_link=resource_link,
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
        return {
            "permissions": body.get("permissions") or [],
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified TargetTcpProxy resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        target_tcp_proxy = params.get("targetTcpProxy")
        if not target_tcp_proxy:
            return create_gcp_error(400, "Required field 'targetTcpProxy' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(target_tcp_proxy)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{target_tcp_proxy}' was not found",
                "NOT_FOUND",
            )
        self.resources.pop(target_tcp_proxy, None)
        resource_link = f"projects/{project}/global/targetTcpProxies/{target_tcp_proxy}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class target_tcp_proxie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'aggregatedList': target_tcp_proxie_RequestParser._parse_aggregatedList,
            'setProxyHeader': target_tcp_proxie_RequestParser._parse_setProxyHeader,
            'get': target_tcp_proxie_RequestParser._parse_get,
            'list': target_tcp_proxie_RequestParser._parse_list,
            'delete': target_tcp_proxie_RequestParser._parse_delete,
            'setBackendService': target_tcp_proxie_RequestParser._parse_setBackendService,
            'insert': target_tcp_proxie_RequestParser._parse_insert,
            'testIamPermissions': target_tcp_proxie_RequestParser._parse_testIamPermissions,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
    def _parse_setProxyHeader(
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
        params['TargetTcpProxiesSetProxyHeaderRequest'] = body.get('TargetTcpProxiesSetProxyHeaderRequest')
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
    def _parse_setBackendService(
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
        params['TargetTcpProxiesSetBackendServiceRequest'] = body.get('TargetTcpProxiesSetBackendServiceRequest')
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
        params['TargetTcpProxy'] = body.get('TargetTcpProxy')
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


class target_tcp_proxie_ResponseSerializer:
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
            'aggregatedList': target_tcp_proxie_ResponseSerializer._serialize_aggregatedList,
            'setProxyHeader': target_tcp_proxie_ResponseSerializer._serialize_setProxyHeader,
            'get': target_tcp_proxie_ResponseSerializer._serialize_get,
            'list': target_tcp_proxie_ResponseSerializer._serialize_list,
            'delete': target_tcp_proxie_ResponseSerializer._serialize_delete,
            'setBackendService': target_tcp_proxie_ResponseSerializer._serialize_setBackendService,
            'insert': target_tcp_proxie_ResponseSerializer._serialize_insert,
            'testIamPermissions': target_tcp_proxie_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setProxyHeader(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setBackendService(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

