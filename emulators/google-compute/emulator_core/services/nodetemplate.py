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
class NodeTemplate:
    status_message: str = ""
    node_affinity_labels: Dict[str, Any] = field(default_factory=dict)
    region: str = ""
    name: str = ""
    disks: List[Any] = field(default_factory=list)
    node_type: str = ""
    creation_timestamp: str = ""
    description: str = ""
    status: str = ""
    accelerators: List[Any] = field(default_factory=list)
    node_type_flexibility: Dict[str, Any] = field(default_factory=dict)
    cpu_overcommit_type: str = ""
    server_binding: Dict[str, Any] = field(default_factory=dict)
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.status_message is not None and self.status_message != "":
            d["statusMessage"] = self.status_message
        d["nodeAffinityLabels"] = self.node_affinity_labels
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["disks"] = self.disks
        if self.node_type is not None and self.node_type != "":
            d["nodeType"] = self.node_type
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.status is not None and self.status != "":
            d["status"] = self.status
        d["accelerators"] = self.accelerators
        d["nodeTypeFlexibility"] = self.node_type_flexibility
        if self.cpu_overcommit_type is not None and self.cpu_overcommit_type != "":
            d["cpuOvercommitType"] = self.cpu_overcommit_type
        d["serverBinding"] = self.server_binding
        d["kind"] = "compute#nodetemplate"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class NodeTemplate_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.node_templates  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "node-template") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Dict[str, Any] | NodeTemplate:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource

    def _filter_resources(self, params: Dict[str, Any]) -> List[NodeTemplate]:
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
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a NodeTemplate resource in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("NodeTemplate")
        if not body:
            return create_gcp_error(400, "Required field 'NodeTemplate' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"NodeTemplate {name!r} already exists", "ALREADY_EXISTS")
        resource = NodeTemplate(
            status_message=body.get("statusMessage", ""),
            node_affinity_labels=body.get("nodeAffinityLabels", {}),
            region=region,
            name=name,
            disks=body.get("disks", []),
            node_type=body.get("nodeType", ""),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            description=body.get("description", ""),
            status=body.get("status", ""),
            accelerators=body.get("accelerators", []),
            node_type_flexibility=body.get("nodeTypeFlexibility", {}),
            cpu_overcommit_type=body.get("cpuOvercommitType", ""),
            server_binding=body.get("serverBinding", {}),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/nodeTemplates/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified node template."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("nodeTemplate")
        if not name:
            return create_gcp_error(400, "Required field 'nodeTemplate' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource or resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of node templates available to the specified
project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        resources = self._filter_resources(params)
        return {
            "kind": "compute#nodetemplateList",
            "id": f"projects/{project}/regions/{region}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of node templates.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = self._filter_resources(params)
        scope_key = f"regions/{params.get('region', 'us-central1')}"
        items: Dict[str, Any]
        if not resources:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items = {scope_key: {"NodeTemplates": [resource.to_dict() for resource in resources]}}
        return {
            "kind": "compute#nodetemplateAggregatedList",
            "id": f"projects/{project}/aggregated/nodeTemplates",
            "items": items,
            "selfLink": "",
        }

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("RegionSetPolicyRequest")
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionSetPolicyRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(name)
        if not resource or resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        policy = body.get("policy", {})
        resource.iam_policy = policy
        return policy

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest")
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TestPermissionsRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(name)
        if not resource or resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        permissions = body.get("permissions", [])
        return {"permissions": permissions}

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource or resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.iam_policy or {}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified NodeTemplate resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("nodeTemplate")
        if not name:
            return create_gcp_error(400, "Required field 'nodeTemplate' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource or resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        del self.resources[name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/nodeTemplates/{name}",
            params=params,
        )


class node_template_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'list': node_template_RequestParser._parse_list,
            'insert': node_template_RequestParser._parse_insert,
            'delete': node_template_RequestParser._parse_delete,
            'setIamPolicy': node_template_RequestParser._parse_setIamPolicy,
            'testIamPermissions': node_template_RequestParser._parse_testIamPermissions,
            'get': node_template_RequestParser._parse_get,
            'aggregatedList': node_template_RequestParser._parse_aggregatedList,
            'getIamPolicy': node_template_RequestParser._parse_getIamPolicy,
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
        params['NodeTemplate'] = body.get('NodeTemplate')
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
        params['RegionSetPolicyRequest'] = body.get('RegionSetPolicyRequest')
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


class node_template_ResponseSerializer:
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
            'list': node_template_ResponseSerializer._serialize_list,
            'insert': node_template_ResponseSerializer._serialize_insert,
            'delete': node_template_ResponseSerializer._serialize_delete,
            'setIamPolicy': node_template_ResponseSerializer._serialize_setIamPolicy,
            'testIamPermissions': node_template_ResponseSerializer._serialize_testIamPermissions,
            'get': node_template_ResponseSerializer._serialize_get,
            'aggregatedList': node_template_ResponseSerializer._serialize_aggregatedList,
            'getIamPolicy': node_template_ResponseSerializer._serialize_getIamPolicy,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

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
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

