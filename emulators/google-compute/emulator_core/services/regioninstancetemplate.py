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
class RegionInstanceTemplate:
    creation_timestamp: str = ""
    source_instance_params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    region: str = ""
    name: str = ""
    source_instance: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["sourceInstanceParams"] = self.source_instance_params
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.source_instance is not None and self.source_instance != "":
            d["sourceInstance"] = self.source_instance
        d["properties"] = self.properties
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regioninstancetemplate"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionInstanceTemplate_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_instance_templates  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-instance-template") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an instance template in the specified project and region using the
global instance template whose URL is included in the request."""
        project = params.get("project")
        region = params.get("region")
        body = params.get("InstanceTemplate") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' missing", "INVALID_ARGUMENT")
        if not params.get("InstanceTemplate"):
            return create_gcp_error(400, "Required field 'InstanceTemplate' missing", "INVALID_ARGUMENT")
        name = body.get("name") or self._generate_name()
        if name in self.resources:
            return create_gcp_error(
                409,
                f"RegionInstanceTemplate {name!r} already exists",
                "ALREADY_EXISTS",
            )
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = RegionInstanceTemplate(
            creation_timestamp=creation_timestamp,
            source_instance_params=body.get("sourceInstanceParams", {}),
            description=body.get("description", ""),
            region=region,
            name=name,
            source_instance=body.get("sourceInstance", ""),
            properties=body.get("properties", {}),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=(
                f"projects/{project}/regions/{region}/instanceTemplates/{resource.name}"
            ),
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified instance template."""
        project = params.get("project")
        region = params.get("region")
        instance_template = params.get("instanceTemplate")
        if not project:
            return create_gcp_error(400, "Required field 'project' missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' missing", "INVALID_ARGUMENT")
        if not instance_template:
            return create_gcp_error(
                400,
                "Required field 'instanceTemplate' missing",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(instance_template)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{instance_template}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of instance templates that are contained within the
specified project and region."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' missing", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]
        return {
            "kind": "compute#regioninstancetemplateList",
            "id": f"projects/{project}/regions/{region}/instanceTemplates",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified instance template. Deleting an instance template is
permanent and cannot be undone."""
        project = params.get("project")
        region = params.get("region")
        instance_template = params.get("instanceTemplate")
        if not project:
            return create_gcp_error(400, "Required field 'project' missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' missing", "INVALID_ARGUMENT")
        if not instance_template:
            return create_gcp_error(
                400,
                "Required field 'instanceTemplate' missing",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(instance_template)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{instance_template}' was not found",
                "NOT_FOUND",
            )
        del self.resources[instance_template]
        return make_operation(
            operation_type="delete",
            resource_link=(
                f"projects/{project}/regions/{region}/instanceTemplates/{instance_template}"
            ),
            params=params,
        )


class region_instance_template_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'list': region_instance_template_RequestParser._parse_list,
            'get': region_instance_template_RequestParser._parse_get,
            'insert': region_instance_template_RequestParser._parse_insert,
            'delete': region_instance_template_RequestParser._parse_delete,
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
        params['InstanceTemplate'] = body.get('InstanceTemplate')
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


class region_instance_template_ResponseSerializer:
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
            'list': region_instance_template_ResponseSerializer._serialize_list,
            'get': region_instance_template_ResponseSerializer._serialize_get,
            'insert': region_instance_template_ResponseSerializer._serialize_insert,
            'delete': region_instance_template_ResponseSerializer._serialize_delete,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

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
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

