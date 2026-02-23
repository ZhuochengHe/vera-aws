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
class TargetHttpsProxie:
    description: str = ""
    ssl_policy: str = ""
    certificate_map: str = ""
    fingerprint: str = ""
    http_keep_alive_timeout_sec: int = 0
    url_map: str = ""
    tls_early_data: str = ""
    creation_timestamp: str = ""
    server_tls_policy: str = ""
    region: str = ""
    proxy_bind: bool = False
    ssl_certificates: List[Any] = field(default_factory=list)
    authorization_policy: str = ""
    name: str = ""
    quic_override: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.ssl_policy is not None and self.ssl_policy != "":
            d["sslPolicy"] = self.ssl_policy
        if self.certificate_map is not None and self.certificate_map != "":
            d["certificateMap"] = self.certificate_map
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.http_keep_alive_timeout_sec is not None and self.http_keep_alive_timeout_sec != 0:
            d["httpKeepAliveTimeoutSec"] = self.http_keep_alive_timeout_sec
        if self.url_map is not None and self.url_map != "":
            d["urlMap"] = self.url_map
        if self.tls_early_data is not None and self.tls_early_data != "":
            d["tlsEarlyData"] = self.tls_early_data
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.server_tls_policy is not None and self.server_tls_policy != "":
            d["serverTlsPolicy"] = self.server_tls_policy
        if self.region is not None and self.region != "":
            d["region"] = self.region
        d["proxyBind"] = self.proxy_bind
        d["sslCertificates"] = self.ssl_certificates
        if self.authorization_policy is not None and self.authorization_policy != "":
            d["authorizationPolicy"] = self.authorization_policy
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.quic_override is not None and self.quic_override != "":
            d["quicOverride"] = self.quic_override
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#targethttpsproxie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class TargetHttpsProxie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.target_https_proxies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "target-https-proxie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource 'targetHttpsProxies/{name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a TargetHttpsProxy resource in the specified
project using the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetHttpsProxy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetHttpsProxy' not found",
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
                f"TargetHttpsProxy '{name}' already exists",
                "ALREADY_EXISTS",
            )

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

        resource = TargetHttpsProxie(
            description=body.get("description") or "",
            ssl_policy=ssl_policy,
            certificate_map=body.get("certificateMap") or "",
            fingerprint=body.get("fingerprint") or "",
            http_keep_alive_timeout_sec=body.get("httpKeepAliveTimeoutSec") or 0,
            url_map=url_map,
            tls_early_data=body.get("tlsEarlyData") or "",
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            server_tls_policy=body.get("serverTlsPolicy") or "",
            region="",
            proxy_bind=body.get("proxyBind") or False,
            ssl_certificates=ssl_certificates,
            authorization_policy=body.get("authorizationPolicy") or "",
            name=name,
            quic_override=body.get("quicOverride") or "",
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/global/targetHttpsProxies/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified TargetHttpsProxy resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource(target_https_proxy)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of TargetHttpsProxy resources
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
                resources = [r for r in resources if r.name == match.group(1)]
        return {
            "kind": "compute#targethttpsproxieList",
            "id": f"projects/{project}/global/targetHttpsProxies",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of all TargetHttpsProxy resources, regional and global,
available to the specified project.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` paramet..."""
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
                resources = [r for r in resources if r.name == match.group(1)]
        scope_key = "global"
        if resources:
            items = {scope_key: {"TargetHttpsProxies": [r.to_dict() for r in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#targethttpsproxieAggregatedList",
            "id": f"projects/{project}/aggregated/targetHttpsProxies",
            "items": items,
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified TargetHttpsProxy resource with the data included in
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
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetHttpsProxy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource(target_https_proxy)
        if is_error_response(resource):
            return resource

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
        if "sslPolicy" in body:
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
            resource.ssl_policy = ssl_policy
        if "sslCertificates" in body:
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
        if "description" in body:
            resource.description = body.get("description") or ""
        if "certificateMap" in body:
            resource.certificate_map = body.get("certificateMap") or ""
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "httpKeepAliveTimeoutSec" in body:
            resource.http_keep_alive_timeout_sec = (
                body.get("httpKeepAliveTimeoutSec") or 0
            )
        if "tlsEarlyData" in body:
            resource.tls_early_data = body.get("tlsEarlyData") or ""
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "serverTlsPolicy" in body:
            resource.server_tls_policy = body.get("serverTlsPolicy") or ""
        if "proxyBind" in body:
            resource.proxy_bind = body.get("proxyBind") or False
        if "authorizationPolicy" in body:
            resource.authorization_policy = body.get("authorizationPolicy") or ""
        if "quicOverride" in body:
            resource.quic_override = body.get("quicOverride") or ""

        return make_operation(
            operation_type="patch",
            resource_link=(
                f"projects/{project}/global/targetHttpsProxies/{resource.name}"
            ),
            params=params,
        )

    def setSslPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the SSL policy for TargetHttpsProxy. The SSL policy specifies the
server-side support for SSL features. This affects connections between
clients and the HTTPS proxy load balancer. They do not ..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SslPolicyReference") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SslPolicyReference' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource(target_https_proxy)
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
                f"projects/{project}/global/targetHttpsProxies/{resource.name}"
            ),
            params=params,
        )

    def setQuicOverride(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the QUIC override policy for TargetHttpsProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetHttpsProxiesSetQuicOverrideRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetHttpsProxiesSetQuicOverrideRequest' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource(target_https_proxy)
        if is_error_response(resource):
            return resource

        quic_override = body.get("quicOverride") or ""
        if not quic_override:
            return create_gcp_error(
                400,
                "Required field 'quicOverride' not found",
                "INVALID_ARGUMENT",
            )
        resource.quic_override = quic_override
        return make_operation(
            operation_type="setQuicOverride",
            resource_link=(
                f"projects/{project}/global/targetHttpsProxies/{resource.name}"
            ),
            params=params,
        )

    def setSslCertificates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Replaces SslCertificates for TargetHttpsProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetHttpsProxiesSetSslCertificatesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetHttpsProxiesSetSslCertificatesRequest' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource(target_https_proxy)
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
                f"projects/{project}/global/targetHttpsProxies/{resource.name}"
            ),
            params=params,
        )

    def setCertificateMap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the Certificate Map for TargetHttpsProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TargetHttpsProxiesSetCertificateMapRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetHttpsProxiesSetCertificateMapRequest' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource(target_https_proxy)
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
                f"projects/{project}/global/targetHttpsProxies/{resource.name}"
            ),
            params=params,
        )

    def setUrlMap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the URL map for TargetHttpsProxy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("UrlMapReference") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'UrlMapReference' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource(target_https_proxy)
        if is_error_response(resource):
            return resource

        url_map = body.get("urlMap") or body.get("urlMapLink") or ""
        if not url_map:
            return create_gcp_error(
                400,
                "Required field 'urlMap' not found",
                "INVALID_ARGUMENT",
            )
        if not (
            self.state.url_maps.get(url_map)
            or self.state.region_url_maps.get(url_map)
        ):
            return create_gcp_error(
                404,
                f"UrlMap '{url_map}' not found",
                "NOT_FOUND",
            )
        resource.url_map = url_map
        return make_operation(
            operation_type="setUrlMap",
            resource_link=(
                f"projects/{project}/global/targetHttpsProxies/{resource.name}"
            ),
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified TargetHttpsProxy resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        target_https_proxy = params.get("targetHttpsProxy")
        if not target_https_proxy:
            return create_gcp_error(
                400,
                "Required field 'targetHttpsProxy' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource(target_https_proxy)
        if is_error_response(resource):
            return resource

        del self.resources[target_https_proxy]
        return make_operation(
            operation_type="delete",
            resource_link=(
                f"projects/{project}/global/targetHttpsProxies/{resource.name}"
            ),
            params=params,
        )


class target_https_proxie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setSslPolicy': target_https_proxie_RequestParser._parse_setSslPolicy,
            'get': target_https_proxie_RequestParser._parse_get,
            'setQuicOverride': target_https_proxie_RequestParser._parse_setQuicOverride,
            'setSslCertificates': target_https_proxie_RequestParser._parse_setSslCertificates,
            'list': target_https_proxie_RequestParser._parse_list,
            'setCertificateMap': target_https_proxie_RequestParser._parse_setCertificateMap,
            'delete': target_https_proxie_RequestParser._parse_delete,
            'aggregatedList': target_https_proxie_RequestParser._parse_aggregatedList,
            'setUrlMap': target_https_proxie_RequestParser._parse_setUrlMap,
            'patch': target_https_proxie_RequestParser._parse_patch,
            'insert': target_https_proxie_RequestParser._parse_insert,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
    def _parse_setQuicOverride(
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
        params['TargetHttpsProxiesSetQuicOverrideRequest'] = body.get('TargetHttpsProxiesSetQuicOverrideRequest')
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
        params['TargetHttpsProxiesSetSslCertificatesRequest'] = body.get('TargetHttpsProxiesSetSslCertificatesRequest')
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
        params['TargetHttpsProxiesSetCertificateMapRequest'] = body.get('TargetHttpsProxiesSetCertificateMapRequest')
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
        params['TargetHttpsProxy'] = body.get('TargetHttpsProxy')
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
        params['TargetHttpsProxy'] = body.get('TargetHttpsProxy')
        return params


class target_https_proxie_ResponseSerializer:
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
            'setSslPolicy': target_https_proxie_ResponseSerializer._serialize_setSslPolicy,
            'get': target_https_proxie_ResponseSerializer._serialize_get,
            'setQuicOverride': target_https_proxie_ResponseSerializer._serialize_setQuicOverride,
            'setSslCertificates': target_https_proxie_ResponseSerializer._serialize_setSslCertificates,
            'list': target_https_proxie_ResponseSerializer._serialize_list,
            'setCertificateMap': target_https_proxie_ResponseSerializer._serialize_setCertificateMap,
            'delete': target_https_proxie_ResponseSerializer._serialize_delete,
            'aggregatedList': target_https_proxie_ResponseSerializer._serialize_aggregatedList,
            'setUrlMap': target_https_proxie_ResponseSerializer._serialize_setUrlMap,
            'patch': target_https_proxie_ResponseSerializer._serialize_patch,
            'insert': target_https_proxie_ResponseSerializer._serialize_insert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setSslPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setQuicOverride(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setSslCertificates(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setCertificateMap(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setUrlMap(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

