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
class InterconnectAttachmentGroup:
    description: str = ""
    interconnect_group: str = ""
    configured: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    intent: Dict[str, Any] = field(default_factory=dict)
    attachments: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    logical_structure: Dict[str, Any] = field(default_factory=dict)
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.interconnect_group is not None and self.interconnect_group != "":
            d["interconnectGroup"] = self.interconnect_group
        d["configured"] = self.configured
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["intent"] = self.intent
        d["attachments"] = self.attachments
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["logicalStructure"] = self.logical_structure
        d["kind"] = "compute#interconnectattachmentgroup"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InterconnectAttachmentGroup_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.interconnect_attachment_groups  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "interconnect-attachment-group") -> str:
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
        """Creates a InterconnectAttachmentGroup in the specified project in the given
scope using the parameters that are included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("InterconnectAttachmentGroup")
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InterconnectAttachmentGroup' not specified",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"InterconnectAttachmentGroup {name!r} already exists", "ALREADY_EXISTS")

        resource = InterconnectAttachmentGroup(
            description=body.get("description", ""),
            interconnect_group=body.get("interconnectGroup", ""),
            configured=body.get("configured", {}),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            intent=body.get("intent", {}),
            attachments=body.get("attachments", {}),
            name=name,
            logical_structure=body.get("logicalStructure", {}),
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/interconnectAttachmentGroups/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified InterconnectAttachmentGroup resource in the given
scope."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        interconnect_attachment_group = params.get("interconnectAttachmentGroup")
        if not interconnect_attachment_group:
            return create_gcp_error(
                400,
                "Required field 'interconnectAttachmentGroup' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(interconnect_attachment_group)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the InterconnectAttachmentGroups for a project in the given scope."""
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
        return {
            "kind": "compute#interconnectattachmentgroupList",
            "id": f"projects/{project}/global/interconnectAttachmentGroups",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("GlobalSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'GlobalSetPolicyRequest' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource

        resource.iam_policy = body.get("policy") or {}
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=f"projects/{project}/global/interconnectAttachmentGroups/{resource.name}",
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified InterconnectAttachmentGroup resource with the data
included in the request. This method supports PATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        interconnect_attachment_group = params.get("interconnectAttachmentGroup")
        if not interconnect_attachment_group:
            return create_gcp_error(
                400,
                "Required field 'interconnectAttachmentGroup' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("InterconnectAttachmentGroup") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InterconnectAttachmentGroup' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(interconnect_attachment_group)
        if is_error_response(resource):
            return resource

        if "description" in body:
            resource.description = body.get("description") or ""
        if "interconnectGroup" in body:
            resource.interconnect_group = body.get("interconnectGroup") or ""
        if "configured" in body:
            resource.configured = body.get("configured") or {}
        if "intent" in body:
            resource.intent = body.get("intent") or {}
        if "attachments" in body:
            resource.attachments = body.get("attachments") or {}
        if "logicalStructure" in body:
            resource.logical_structure = body.get("logicalStructure") or {}
        if "iamPolicy" in body:
            resource.iam_policy = body.get("iamPolicy") or {}

        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/interconnectAttachmentGroups/{resource.name}",
            params=params,
        )

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

    def getOperationalStatus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the InterconnectAttachmentStatuses for the specified
InterconnectAttachmentGroup resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        interconnect_attachment_group = params.get("interconnectAttachmentGroup")
        if not interconnect_attachment_group:
            return create_gcp_error(
                400,
                "Required field 'interconnectAttachmentGroup' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(interconnect_attachment_group)
        if is_error_response(resource):
            return resource

        return {
            "kind": "compute#interconnectAttachmentGroupOperationalStatus",
            "attachments": resource.attachments,
        }

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

        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource

        return {
            "permissions": body.get("permissions") or [],
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified InterconnectAttachmentGroup in the given scope"""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        interconnect_attachment_group = params.get("interconnectAttachmentGroup")
        if not interconnect_attachment_group:
            return create_gcp_error(
                400,
                "Required field 'interconnectAttachmentGroup' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(interconnect_attachment_group)
        if is_error_response(resource):
            return resource

        del self.resources[resource.name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/interconnectAttachmentGroups/{resource.name}",
            params=params,
        )


class interconnect_attachment_group_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'insert': interconnect_attachment_group_RequestParser._parse_insert,
            'setIamPolicy': interconnect_attachment_group_RequestParser._parse_setIamPolicy,
            'get': interconnect_attachment_group_RequestParser._parse_get,
            'getIamPolicy': interconnect_attachment_group_RequestParser._parse_getIamPolicy,
            'getOperationalStatus': interconnect_attachment_group_RequestParser._parse_getOperationalStatus,
            'delete': interconnect_attachment_group_RequestParser._parse_delete,
            'list': interconnect_attachment_group_RequestParser._parse_list,
            'patch': interconnect_attachment_group_RequestParser._parse_patch,
            'testIamPermissions': interconnect_attachment_group_RequestParser._parse_testIamPermissions,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['InterconnectAttachmentGroup'] = body.get('InterconnectAttachmentGroup')
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
    def _parse_getOperationalStatus(
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
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['InterconnectAttachmentGroup'] = body.get('InterconnectAttachmentGroup')
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


class interconnect_attachment_group_ResponseSerializer:
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
            'insert': interconnect_attachment_group_ResponseSerializer._serialize_insert,
            'setIamPolicy': interconnect_attachment_group_ResponseSerializer._serialize_setIamPolicy,
            'get': interconnect_attachment_group_ResponseSerializer._serialize_get,
            'getIamPolicy': interconnect_attachment_group_ResponseSerializer._serialize_getIamPolicy,
            'getOperationalStatus': interconnect_attachment_group_ResponseSerializer._serialize_getOperationalStatus,
            'delete': interconnect_attachment_group_ResponseSerializer._serialize_delete,
            'list': interconnect_attachment_group_ResponseSerializer._serialize_list,
            'patch': interconnect_attachment_group_ResponseSerializer._serialize_patch,
            'testIamPermissions': interconnect_attachment_group_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getOperationalStatus(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

