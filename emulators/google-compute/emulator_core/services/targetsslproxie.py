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
class TargetSslProxie:
    ssl_certificates: List[Any] = field(default_factory=list)
    service: str = ""
    proxy_header: str = ""
    name: str = ""
    creation_timestamp: str = ""
    ssl_policy: str = ""
    description: str = ""
    certificate_map: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["sslCertificates"] = self.ssl_certificates
        if self.service is not None and self.service != "":
            d["service"] = self.service
        if self.proxy_header is not None and self.proxy_header != "":
            d["proxyHeader"] = self.proxy_header
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.ssl_policy is not None and self.ssl_policy != "":
            d["sslPolicy"] = self.ssl_policy
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.certificate_map is not None and self.certificate_map != "":
            d["certificateMap"] = self.certificate_map
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#targetsslproxie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class TargetSslProxie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.target_ssl_proxies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "target-ssl-proxie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a TargetSslProxy resource in the specified project using
the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetSslProxy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetSslProxy' not found",
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
                f"TargetSslProxy '{name}' already exists",
                "ALREADY_EXISTS",
            )

        service = body.get("service") or ""
        if service:
            service_name = service.split("/")[-1]
            if not (
                self.state.backend_services.get(service_name)
                or self.state.backend_services.get(service)
                or self.state.region_backend_services.get(service_name)
                or self.state.region_backend_services.get(service)
            ):
                return create_gcp_error(
                    404,
                    f"BackendService '{service_name}' not found",
                    "NOT_FOUND",
                )

        ssl_policy = body.get("sslPolicy") or ""
        if ssl_policy and not (
            self.state.ssl_policies.get(ssl_policy)
            or self.state.region_ssl_policies.get(ssl_policy)
        ):
            return create_gcp_error(
                404,
                f"SslPolicy '{ssl_policy}' not found",
                "NOT_FOUND",
            )
        ssl_certificates = body.get("sslCertificates") or []
        for certificate in ssl_certificates:
            if not (
                self.state.ssl_certificates.get(certificate)
                or self.state.region_ssl_certificates.get(certificate)
            ):
                return create_gcp_error(
                    404,
                    f"SslCertificate '{certificate}' not found",
                    "NOT_FOUND",
                )

        resource = TargetSslProxie(
            ssl_certificates=ssl_certificates,
            service=service,
            proxy_header=body.get("proxyHeader") or "",
            name=name,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            ssl_policy=ssl_policy,
            description=body.get("description") or "",
            certificate_map=body.get("certificateMap") or "",
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/global/targetSslProxies/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified TargetSslProxy resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_ssl_proxy = params.get("targetSslProxy")
        if not target_ssl_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetSslProxy' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(target_ssl_proxy)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of TargetSslProxy resources
available to the specified project."""
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
            "kind": "compute#targetsslproxieList",
            "id": f"projects/{project}/global/targetSslProxies",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setBackendService(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the BackendService for TargetSslProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_ssl_proxy = params.get("targetSslProxy")
        if not target_ssl_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetSslProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetSslProxiesSetBackendServiceRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetSslProxiesSetBackendServiceRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(target_ssl_proxy)
        if is_error_response(resource):
            return resource
        service = body.get("service") or ""
        if not service:
            return create_gcp_error(
                400,
                "Required field 'service' not found",
                "INVALID_ARGUMENT",
            )
        service_name = service.split("/")[-1]
        if not (
            self.state.backend_services.get(service_name)
            or self.state.backend_services.get(service)
            or self.state.region_backend_services.get(service_name)
            or self.state.region_backend_services.get(service)
        ):
            return create_gcp_error(
                404,
                f"BackendService '{service_name}' not found",
                "NOT_FOUND",
            )
        resource.service = service
        return make_operation(
            operation_type="setBackendService",
            resource_link=(
                f"projects/{project}/global/targetSslProxies/{resource.name}"
            ),
            params=params,
        )

    def setSslCertificates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes SslCertificates for TargetSslProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_ssl_proxy = params.get("targetSslProxy")
        if not target_ssl_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetSslProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetSslProxiesSetSslCertificatesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetSslProxiesSetSslCertificatesRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(target_ssl_proxy)
        if is_error_response(resource):
            return resource
        ssl_certificates = body.get("sslCertificates") or []
        for certificate in ssl_certificates:
            if not (
                self.state.ssl_certificates.get(certificate)
                or self.state.region_ssl_certificates.get(certificate)
            ):
                return create_gcp_error(
                    404,
                    f"SslCertificate '{certificate}' not found",
                    "NOT_FOUND",
                )
        resource.ssl_certificates = ssl_certificates
        return make_operation(
            operation_type="setSslCertificates",
            resource_link=(
                f"projects/{project}/global/targetSslProxies/{resource.name}"
            ),
            params=params,
        )

    def setCertificateMap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the Certificate Map for TargetSslProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_ssl_proxy = params.get("targetSslProxy")
        if not target_ssl_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetSslProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetSslProxiesSetCertificateMapRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetSslProxiesSetCertificateMapRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(target_ssl_proxy)
        if is_error_response(resource):
            return resource
        certificate_map = body.get("certificateMap") or body.get("certificateMapLink") or ""
        if not certificate_map:
            return create_gcp_error(
                400,
                "Required field 'certificateMap' not found",
                "INVALID_ARGUMENT",
            )
        resource.certificate_map = certificate_map
        return make_operation(
            operation_type="setCertificateMap",
            resource_link=(
                f"projects/{project}/global/targetSslProxies/{resource.name}"
            ),
            params=params,
        )

    def setSslPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the SSL policy for TargetSslProxy. The SSL policy specifies the
server-side support for SSL features. This affects connections between
clients and the load balancer. They do not affect the
con..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_ssl_proxy = params.get("targetSslProxy")
        if not target_ssl_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetSslProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SslPolicyReference") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SslPolicyReference' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(target_ssl_proxy)
        if is_error_response(resource):
            return resource
        ssl_policy = body.get("sslPolicy") or body.get("sslPolicyLink") or ""
        if not ssl_policy:
            return create_gcp_error(
                400,
                "Required field 'sslPolicy' not found",
                "INVALID_ARGUMENT",
            )
        if not (
            self.state.ssl_policies.get(ssl_policy)
            or self.state.region_ssl_policies.get(ssl_policy)
        ):
            return create_gcp_error(
                404,
                f"SslPolicy '{ssl_policy}' not found",
                "NOT_FOUND",
            )
        resource.ssl_policy = ssl_policy
        return make_operation(
            operation_type="setSslPolicy",
            resource_link=(
                f"projects/{project}/global/targetSslProxies/{resource.name}"
            ),
            params=params,
        )

    def setProxyHeader(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the ProxyHeaderType for TargetSslProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_ssl_proxy = params.get("targetSslProxy")
        if not target_ssl_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetSslProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetSslProxiesSetProxyHeaderRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetSslProxiesSetProxyHeaderRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(target_ssl_proxy)
        if is_error_response(resource):
            return resource
        proxy_header = body.get("proxyHeader") or ""
        if not proxy_header:
            return create_gcp_error(
                400,
                "Required field 'proxyHeader' not found",
                "INVALID_ARGUMENT",
            )
        resource.proxy_header = proxy_header
        return make_operation(
            operation_type="setProxyHeader",
            resource_link=(
                f"projects/{project}/global/targetSslProxies/{resource.name}"
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
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions", []) or []
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified TargetSslProxy resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_ssl_proxy = params.get("targetSslProxy")
        if not target_ssl_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetSslProxy' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(target_ssl_proxy)
        if is_error_response(resource):
            return resource
        self.resources.pop(resource.name, None)
        resource_link = f"projects/{project}/global/targetSslProxies/{resource.name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class target_ssl_proxie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setBackendService': target_ssl_proxie_RequestParser._parse_setBackendService,
            'setSslCertificates': target_ssl_proxie_RequestParser._parse_setSslCertificates,
            'setCertificateMap': target_ssl_proxie_RequestParser._parse_setCertificateMap,
            'delete': target_ssl_proxie_RequestParser._parse_delete,
            'insert': target_ssl_proxie_RequestParser._parse_insert,
            'setSslPolicy': target_ssl_proxie_RequestParser._parse_setSslPolicy,
            'setProxyHeader': target_ssl_proxie_RequestParser._parse_setProxyHeader,
            'list': target_ssl_proxie_RequestParser._parse_list,
            'get': target_ssl_proxie_RequestParser._parse_get,
            'testIamPermissions': target_ssl_proxie_RequestParser._parse_testIamPermissions,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['TargetSslProxiesSetBackendServiceRequest'] = body.get('TargetSslProxiesSetBackendServiceRequest')
        return params

    @staticmethod
    def _parse_setSslCertificates(
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
        params['TargetSslProxiesSetSslCertificatesRequest'] = body.get('TargetSslProxiesSetSslCertificatesRequest')
        return params

    @staticmethod
    def _parse_setCertificateMap(
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
        params['TargetSslProxiesSetCertificateMapRequest'] = body.get('TargetSslProxiesSetCertificateMapRequest')
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
        params['TargetSslProxy'] = body.get('TargetSslProxy')
        return params

    @staticmethod
    def _parse_setSslPolicy(
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
        params['SslPolicyReference'] = body.get('SslPolicyReference')
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
        params['TargetSslProxiesSetProxyHeaderRequest'] = body.get('TargetSslProxiesSetProxyHeaderRequest')
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


class target_ssl_proxie_ResponseSerializer:
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
            'setBackendService': target_ssl_proxie_ResponseSerializer._serialize_setBackendService,
            'setSslCertificates': target_ssl_proxie_ResponseSerializer._serialize_setSslCertificates,
            'setCertificateMap': target_ssl_proxie_ResponseSerializer._serialize_setCertificateMap,
            'delete': target_ssl_proxie_ResponseSerializer._serialize_delete,
            'insert': target_ssl_proxie_ResponseSerializer._serialize_insert,
            'setSslPolicy': target_ssl_proxie_ResponseSerializer._serialize_setSslPolicy,
            'setProxyHeader': target_ssl_proxie_ResponseSerializer._serialize_setProxyHeader,
            'list': target_ssl_proxie_ResponseSerializer._serialize_list,
            'get': target_ssl_proxie_ResponseSerializer._serialize_get,
            'testIamPermissions': target_ssl_proxie_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setBackendService(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setSslCertificates(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setCertificateMap(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setSslPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setProxyHeader(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

