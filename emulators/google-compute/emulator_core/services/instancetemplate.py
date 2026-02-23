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
class InstanceTemplate:
    creation_timestamp: str = ""
    source_instance_params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    region: str = ""
    name: str = ""
    source_instance: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

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
        d["kind"] = "compute#instancetemplate"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InstanceTemplate_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.instance_templates  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "instance-template") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource

    def _filter_resources(self, params: Dict[str, Any]) -> List[InstanceTemplate]:
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                name = match.group(1)
                resources = [resource for resource in resources if resource.name == name]
        zone = params.get("zone")
        region = params.get("region")
        if zone:
            resources = [resource for resource in resources if getattr(resource, "zone", None) == zone]
        if region:
            resources = [resource for resource in resources if getattr(resource, "region", None) == region]
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an instance template in the specified project using the
data that is included in the request. If you are creating a new template to
update an existing instance group, your new instance temp..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("InstanceTemplate")
        if not body:
            return create_gcp_error(400, "Required field 'InstanceTemplate' not specified", "INVALID_ARGUMENT")
        name = body.get("name") or params.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"InstanceTemplate {name!r} already exists", "ALREADY_EXISTS")
        source_instance = body.get("sourceInstance", "")
        if source_instance:
            instance_name = source_instance.split("/")[-1]
            if instance_name and not self.state.instances.get(instance_name):
                return create_gcp_error(404, f"Instance {instance_name!r} not found", "NOT_FOUND")
        resource = InstanceTemplate(
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            source_instance_params=body.get("sourceInstanceParams", {}),
            description=body.get("description", ""),
            region=body.get("region", ""),
            name=name,
            source_instance=source_instance,
            properties=body.get("properties", {}),
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/instanceTemplates/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified instance template."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("instanceTemplate")
        if not name:
            return create_gcp_error(400, "Required field 'instanceTemplate' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of all InstanceTemplates resources, regional and global,
available to the specified project.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parame..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = self._filter_resources(params)
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if resources:
            items = {scope_key: {"InstanceTemplates": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#instancetemplateAggregatedList",
            "id": f"projects/{project}/aggregated/InstanceTemplates",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of instance templates that are contained within
the specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = self._filter_resources(params)
        return {
            "kind": "compute#instancetemplateList",
            "id": f"projects/{project}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("GlobalSetPolicyRequest")
        if not body:
            return create_gcp_error(400, "Required field 'GlobalSetPolicyRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        policy = body.get("policy", {})
        resource.iam_policy = policy
        return policy

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest")
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions", [])
        return {
            "permissions": permissions,
        }

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified instance template. Deleting an instance template is
permanent and cannot be undone. It is not possible to delete templates
that are already in use by a managed instance group."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("instanceTemplate")
        if not name:
            return create_gcp_error(400, "Required field 'instanceTemplate' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        for manager in self.state.instance_group_managers.values():
            template_ref = getattr(manager, "instance_template", "")
            if template_ref and template_ref.split("/")[-1] == name:
                return create_gcp_error(400, "InstanceTemplate is in use", "FAILED_PRECONDITION")
        self.resources.pop(name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/instanceTemplates/{name}",
            params=params,
        )


class instance_template_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'aggregatedList': instance_template_RequestParser._parse_aggregatedList,
            'setIamPolicy': instance_template_RequestParser._parse_setIamPolicy,
            'get': instance_template_RequestParser._parse_get,
            'testIamPermissions': instance_template_RequestParser._parse_testIamPermissions,
            'delete': instance_template_RequestParser._parse_delete,
            'insert': instance_template_RequestParser._parse_insert,
            'getIamPolicy': instance_template_RequestParser._parse_getIamPolicy,
            'list': instance_template_RequestParser._parse_list,
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
    def _parse_setIamPolicy(
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
        params['GlobalSetPolicyRequest'] = body.get('GlobalSetPolicyRequest')
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
        params['InstanceTemplate'] = body.get('InstanceTemplate')
        return params

    @staticmethod
    def _parse_getIamPolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'optionsRequestedPolicyVersion' in query_params:
            params['optionsRequestedPolicyVersion'] = query_params['optionsRequestedPolicyVersion']
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


class instance_template_ResponseSerializer:
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
            'aggregatedList': instance_template_ResponseSerializer._serialize_aggregatedList,
            'setIamPolicy': instance_template_ResponseSerializer._serialize_setIamPolicy,
            'get': instance_template_ResponseSerializer._serialize_get,
            'testIamPermissions': instance_template_ResponseSerializer._serialize_testIamPermissions,
            'delete': instance_template_ResponseSerializer._serialize_delete,
            'insert': instance_template_ResponseSerializer._serialize_insert,
            'getIamPolicy': instance_template_ResponseSerializer._serialize_getIamPolicy,
            'list': instance_template_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

