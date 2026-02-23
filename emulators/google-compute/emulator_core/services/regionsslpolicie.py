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
class RegionSslPolicie:
    warnings: List[Any] = field(default_factory=list)
    creation_timestamp: str = ""
    name: str = ""
    region: str = ""
    min_tls_version: str = ""
    description: str = ""
    custom_features: List[Any] = field(default_factory=list)
    enabled_features: List[Any] = field(default_factory=list)
    fingerprint: str = ""
    profile: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["warnings"] = self.warnings
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.min_tls_version is not None and self.min_tls_version != "":
            d["minTlsVersion"] = self.min_tls_version
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["customFeatures"] = self.custom_features
        d["enabledFeatures"] = self.enabled_features
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.profile is not None and self.profile != "":
            d["profile"] = self.profile
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regionsslpolicie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionSslPolicie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_ssl_policies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-ssl-policie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new policy in the specified project and region using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("SslPolicy") or {}
        if not body:
            return create_gcp_error(400, "Required field 'SslPolicy' not specified", "INVALID_ARGUMENT")
        name = body.get("name") or params.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"RegionSslPolicie {name!r} already exists", "ALREADY_EXISTS")
        resource = RegionSslPolicie(
            warnings=body.get("warnings", []) or [],
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            name=name,
            region=region,
            min_tls_version=body.get("minTlsVersion", ""),
            description=body.get("description", ""),
            custom_features=body.get("customFeatures", []) or [],
            enabled_features=body.get("enabledFeatures", []) or [],
            fingerprint=body.get("fingerprint", ""),
            profile=body.get("profile", ""),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/sslPolicies/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all of the ordered rules present in a single specified policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        ssl_policy = params.get("sslPolicy")
        if not ssl_policy:
            return create_gcp_error(400, "Required field 'sslPolicy' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(ssl_policy)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{ssl_policy}' was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all the SSL policies that have been configured for the specified
project and region."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]
        return {
            "kind": "compute#regionsslpolicieList",
            "id": f"projects/{project}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified SSL policy with the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        ssl_policy = params.get("sslPolicy")
        if not ssl_policy:
            return create_gcp_error(400, "Required field 'sslPolicy' not specified", "INVALID_ARGUMENT")
        body = params.get("SslPolicy") or {}
        if not body:
            return create_gcp_error(400, "Required field 'SslPolicy' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(ssl_policy)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{ssl_policy}' was not found", "NOT_FOUND")
        if "warnings" in body:
            resource.warnings = body.get("warnings", []) or []
        if "minTlsVersion" in body:
            resource.min_tls_version = body.get("minTlsVersion", "")
        if "description" in body:
            resource.description = body.get("description", "")
        if "customFeatures" in body:
            resource.custom_features = body.get("customFeatures", []) or []
        if "enabledFeatures" in body:
            resource.enabled_features = body.get("enabledFeatures", []) or []
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint", "")
        if "profile" in body:
            resource.profile = body.get("profile", "")
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/regions/{region}/sslPolicies/{resource.name}",
            params=params,
        )

    def listAvailableFeatures(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all features that can be specified in the SSL policy when using
custom profile."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        features = [
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
            "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
        ]
        return {
            "kind": "compute#sslPoliciesListAvailableFeaturesResponse",
            "features": features,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified SSL policy. The SSL policy resource can be deleted
only if it is not in use by any TargetHttpsProxy or TargetSslProxy
resources."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        ssl_policy = params.get("sslPolicy")
        if not ssl_policy:
            return create_gcp_error(400, "Required field 'sslPolicy' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(ssl_policy)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{ssl_policy}' was not found", "NOT_FOUND")
        policy_ref = ssl_policy
        policy_suffix = f"/sslPolicies/{ssl_policy}"
        for store in (self.state.region_target_https_proxies, self.state.target_https_proxies):
            for proxy in store.values():
                proxy_policy = getattr(proxy, "ssl_policy", "")
                if not proxy_policy:
                    continue
                if proxy_policy == policy_ref or proxy_policy.endswith(policy_suffix) or proxy_policy.endswith(
                    f"/{ssl_policy}"
                ):
                    return create_gcp_error(
                        400,
                        f"The SSL policy '{ssl_policy}' is in use by '{proxy.name}'",
                        "FAILED_PRECONDITION",
                    )
        del self.resources[resource.name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/sslPolicies/{resource.name}",
            params=params,
        )


class region_ssl_policie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': region_ssl_policie_RequestParser._parse_get,
            'list': region_ssl_policie_RequestParser._parse_list,
            'patch': region_ssl_policie_RequestParser._parse_patch,
            'listAvailableFeatures': region_ssl_policie_RequestParser._parse_listAvailableFeatures,
            'delete': region_ssl_policie_RequestParser._parse_delete,
            'insert': region_ssl_policie_RequestParser._parse_insert,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['SslPolicy'] = body.get('SslPolicy')
        return params

    @staticmethod
    def _parse_listAvailableFeatures(
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
        params['SslPolicy'] = body.get('SslPolicy')
        return params


class region_ssl_policie_ResponseSerializer:
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
            'get': region_ssl_policie_ResponseSerializer._serialize_get,
            'list': region_ssl_policie_ResponseSerializer._serialize_list,
            'patch': region_ssl_policie_ResponseSerializer._serialize_patch,
            'listAvailableFeatures': region_ssl_policie_ResponseSerializer._serialize_listAvailableFeatures,
            'delete': region_ssl_policie_ResponseSerializer._serialize_delete,
            'insert': region_ssl_policie_ResponseSerializer._serialize_insert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listAvailableFeatures(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

