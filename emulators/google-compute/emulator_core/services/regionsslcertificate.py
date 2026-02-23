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
class RegionSslCertificate:
    managed: Dict[str, Any] = field(default_factory=dict)
    self_managed: Dict[str, Any] = field(default_factory=dict)
    type: str = ""
    expire_time: str = ""
    region: str = ""
    certificate: str = ""
    private_key: str = ""
    name: str = ""
    creation_timestamp: str = ""
    description: str = ""
    subject_alternative_names: List[Any] = field(default_factory=list)
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["managed"] = self.managed
        d["selfManaged"] = self.self_managed
        if self.type is not None and self.type != "":
            d["type"] = self.type
        if self.expire_time is not None and self.expire_time != "":
            d["expireTime"] = self.expire_time
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.certificate is not None and self.certificate != "":
            d["certificate"] = self.certificate
        if self.private_key is not None and self.private_key != "":
            d["privateKey"] = self.private_key
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["subjectAlternativeNames"] = self.subject_alternative_names
        d["kind"] = "compute#regionsslcertificate"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionSslCertificate_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_ssl_certificates  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-ssl-certificate") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a SslCertificate resource in the specified project and region using
the data included in the request"""
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
        body = params.get("SslCertificate") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SslCertificate' not found",
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
                f"SslCertificate '{name}' already exists",
                "ALREADY_EXISTS",
            )

        resource = RegionSslCertificate(
            managed=body.get("managed") or {},
            self_managed=body.get("selfManaged") or {},
            type=body.get("type") or "",
            expire_time=body.get("expireTime") or "",
            region=region,
            certificate=body.get("certificate") or "",
            private_key=body.get("privateKey") or "",
            name=name,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            description=body.get("description") or "",
            subject_alternative_names=body.get("subjectAlternativeNames") or [],
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/regions/{region}/RegionSslCertificates/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified SslCertificate resource in the specified region. Get
a list of available SSL certificates by making a list()
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
        certificate_name = params.get("sslCertificate")
        if not certificate_name:
            return create_gcp_error(
                400,
                "Required field 'sslCertificate' not found",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(certificate_name)
        if not resource:
            resource_path = (
                f"projects/{project}/regions/{region}/sslCertificates/{certificate_name}"
            )
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of SslCertificate resources available to the specified
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
                    resource for resource in resources if resource.name == match.group(1)
                ]
        resources = [resource for resource in resources if resource.region == region]

        return {
            "kind": "compute#regionsslcertificateList",
            "id": f"projects/{project}/regions/{region}/sslCertificates",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified SslCertificate resource in the region."""
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
        certificate_name = params.get("sslCertificate")
        if not certificate_name:
            return create_gcp_error(
                400,
                "Required field 'sslCertificate' not found",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(certificate_name)
        if not resource:
            resource_path = (
                f"projects/{project}/regions/{region}/sslCertificates/{certificate_name}"
            )
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        del self.resources[certificate_name]
        resource_link = f"projects/{project}/regions/{region}/RegionSslCertificates/{certificate_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class region_ssl_certificate_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'delete': region_ssl_certificate_RequestParser._parse_delete,
            'get': region_ssl_certificate_RequestParser._parse_get,
            'insert': region_ssl_certificate_RequestParser._parse_insert,
            'list': region_ssl_certificate_RequestParser._parse_list,
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
        params['SslCertificate'] = body.get('SslCertificate')
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


class region_ssl_certificate_ResponseSerializer:
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
            'delete': region_ssl_certificate_ResponseSerializer._serialize_delete,
            'get': region_ssl_certificate_ResponseSerializer._serialize_get,
            'insert': region_ssl_certificate_ResponseSerializer._serialize_insert,
            'list': region_ssl_certificate_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
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

