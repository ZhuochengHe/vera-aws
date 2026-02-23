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
class MachineImage:
    saved_disks: List[Any] = field(default_factory=list)
    satisfies_pzi: bool = False
    description: str = ""
    creation_timestamp: str = ""
    storage_locations: List[Any] = field(default_factory=list)
    name: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    guest_flush: bool = False
    source_disk_encryption_keys: List[Any] = field(default_factory=list)
    satisfies_pzs: bool = False
    total_storage_bytes: str = ""
    status: str = ""
    source_instance_properties: Dict[str, Any] = field(default_factory=dict)
    label_fingerprint: str = ""
    machine_image_encryption_key: Dict[str, Any] = field(default_factory=dict)
    source_instance: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    instance_properties: Dict[str, Any] = field(default_factory=dict)
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["savedDisks"] = self.saved_disks
        d["satisfiesPzi"] = self.satisfies_pzi
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["storageLocations"] = self.storage_locations
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["labels"] = self.labels
        d["guestFlush"] = self.guest_flush
        d["sourceDiskEncryptionKeys"] = self.source_disk_encryption_keys
        d["satisfiesPzs"] = self.satisfies_pzs
        if self.total_storage_bytes is not None and self.total_storage_bytes != "":
            d["totalStorageBytes"] = self.total_storage_bytes
        if self.status is not None and self.status != "":
            d["status"] = self.status
        d["sourceInstanceProperties"] = self.source_instance_properties
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        d["machineImageEncryptionKey"] = self.machine_image_encryption_key
        if self.source_instance is not None and self.source_instance != "":
            d["sourceInstance"] = self.source_instance
        d["params"] = self.params
        d["instanceProperties"] = self.instance_properties
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#machineimage"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class MachineImage_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.machine_images  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "machine-image") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_machine_image_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a machine image in the specified project using the
data that is included in the request. If you are creating a new machine
image to update an existing instance, your new machine image shoul..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("MachineImage") or {}
        if not body:
            return create_gcp_error(400, "Required field 'MachineImage' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"MachineImage {name!r} already exists", "ALREADY_EXISTS")

        source_instance_ref = body.get("sourceInstance") or params.get("sourceInstance") or ""
        source_instance_name = source_instance_ref.split("/")[-1] if source_instance_ref else ""
        if source_instance_name and source_instance_name not in self.state.instances:
            return create_gcp_error(
                404,
                f"Source instance '{source_instance_name}' not found",
                "NOT_FOUND",
            )

        labels = body.get("labels", {})
        label_fingerprint = str(uuid.uuid4())[:8] if labels is not None else ""
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = MachineImage(
            saved_disks=body.get("savedDisks") or [],
            satisfies_pzi=body.get("satisfiesPzi", False),
            description=body.get("description", ""),
            creation_timestamp=creation_timestamp,
            storage_locations=body.get("storageLocations") or [],
            name=name,
            labels=labels or {},
            guest_flush=body.get("guestFlush", False),
            source_disk_encryption_keys=body.get("sourceDiskEncryptionKeys") or [],
            satisfies_pzs=body.get("satisfiesPzs", False),
            total_storage_bytes=body.get("totalStorageBytes", ""),
            status=body.get("status", ""),
            source_instance_properties=body.get("sourceInstanceProperties") or {},
            label_fingerprint=label_fingerprint,
            machine_image_encryption_key=body.get("machineImageEncryptionKey") or {},
            source_instance=source_instance_ref,
            params=body.get("params") or {},
            instance_properties=body.get("instanceProperties") or {},
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/machineImages/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified machine image."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        machine_image_name = params.get("machineImage")
        if not machine_image_name:
            return create_gcp_error(400, "Required field 'machineImage' not specified", "INVALID_ARGUMENT")
        resource = self._get_machine_image_or_error(machine_image_name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of machine images that are contained within
the specified project."""
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
            "kind": "compute#machineimageList",
            "id": f"projects/{project}/global/machineImages",
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
        body = params.get("GlobalSetPolicyRequest")
        if not body:
            return create_gcp_error(
                400,
                "Required field 'GlobalSetPolicyRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_machine_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        resource.iam_policy = body.get("policy") or {}
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=f"projects/{project}/global/machineImages/{resource.name}",
            params=params,
        )

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a machine image. To learn more about labels, read theLabeling
Resources documentation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("GlobalSetLabelsRequest")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'GlobalSetLabelsRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_machine_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        resource.labels = body.get("labels", {}) or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        return make_operation(
            operation_type="setLabels",
            resource_link=f"projects/{project}/global/machineImages/{resource.name}",
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
        resource = self._get_machine_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

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
        resource = self._get_machine_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified machine image. Deleting a machine image is permanent
and cannot be undone."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        machine_image_name = params.get("machineImage")
        if not machine_image_name:
            return create_gcp_error(400, "Required field 'machineImage' not specified", "INVALID_ARGUMENT")
        resource = self._get_machine_image_or_error(machine_image_name)
        if is_error_response(resource):
            return resource
        del self.resources[machine_image_name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/machineImages/{machine_image_name}",
            params=params,
        )


class machine_image_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'getIamPolicy': machine_image_RequestParser._parse_getIamPolicy,
            'testIamPermissions': machine_image_RequestParser._parse_testIamPermissions,
            'setIamPolicy': machine_image_RequestParser._parse_setIamPolicy,
            'delete': machine_image_RequestParser._parse_delete,
            'list': machine_image_RequestParser._parse_list,
            'insert': machine_image_RequestParser._parse_insert,
            'get': machine_image_RequestParser._parse_get,
            'setLabels': machine_image_RequestParser._parse_setLabels,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        if 'sourceInstance' in query_params:
            params['sourceInstance'] = query_params['sourceInstance']
        # Body params
        params['MachineImage'] = body.get('MachineImage')
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
    def _parse_setLabels(
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
        params['GlobalSetLabelsRequest'] = body.get('GlobalSetLabelsRequest')
        return params


class machine_image_ResponseSerializer:
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
            'getIamPolicy': machine_image_ResponseSerializer._serialize_getIamPolicy,
            'testIamPermissions': machine_image_ResponseSerializer._serialize_testIamPermissions,
            'setIamPolicy': machine_image_ResponseSerializer._serialize_setIamPolicy,
            'delete': machine_image_ResponseSerializer._serialize_delete,
            'list': machine_image_ResponseSerializer._serialize_list,
            'insert': machine_image_ResponseSerializer._serialize_insert,
            'get': machine_image_ResponseSerializer._serialize_get,
            'setLabels': machine_image_ResponseSerializer._serialize_setLabels,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

