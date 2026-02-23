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
class Image:
    source_type: str = ""
    deprecated: Dict[str, Any] = field(default_factory=dict)
    source_disk: str = ""
    satisfies_pzi: bool = False
    label_fingerprint: str = ""
    satisfies_pzs: bool = False
    licenses: List[Any] = field(default_factory=list)
    architecture: str = ""
    source_disk_id: str = ""
    name: str = ""
    raw_disk: Dict[str, Any] = field(default_factory=dict)
    image_encryption_key: Dict[str, Any] = field(default_factory=dict)
    enable_confidential_compute: bool = False
    description: str = ""
    license_codes: List[Any] = field(default_factory=list)
    shielded_instance_initial_state: Dict[str, Any] = field(default_factory=dict)
    source_snapshot: str = ""
    creation_timestamp: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, Any] = field(default_factory=dict)
    family: str = ""
    source_snapshot_encryption_key: Dict[str, Any] = field(default_factory=dict)
    storage_locations: List[Any] = field(default_factory=list)
    archive_size_bytes: str = ""
    source_snapshot_id: str = ""
    source_image_encryption_key: Dict[str, Any] = field(default_factory=dict)
    source_image: str = ""
    source_image_id: str = ""
    source_disk_encryption_key: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    guest_os_features: List[Any] = field(default_factory=list)
    disk_size_gb: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.source_type is not None and self.source_type != "":
            d["sourceType"] = self.source_type
        d["deprecated"] = self.deprecated
        if self.source_disk is not None and self.source_disk != "":
            d["sourceDisk"] = self.source_disk
        d["satisfiesPzi"] = self.satisfies_pzi
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        d["satisfiesPzs"] = self.satisfies_pzs
        d["licenses"] = self.licenses
        if self.architecture is not None and self.architecture != "":
            d["architecture"] = self.architecture
        if self.source_disk_id is not None and self.source_disk_id != "":
            d["sourceDiskId"] = self.source_disk_id
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["rawDisk"] = self.raw_disk
        d["imageEncryptionKey"] = self.image_encryption_key
        d["enableConfidentialCompute"] = self.enable_confidential_compute
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["licenseCodes"] = self.license_codes
        d["shieldedInstanceInitialState"] = self.shielded_instance_initial_state
        if self.source_snapshot is not None and self.source_snapshot != "":
            d["sourceSnapshot"] = self.source_snapshot
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["params"] = self.params
        d["labels"] = self.labels
        if self.family is not None and self.family != "":
            d["family"] = self.family
        d["sourceSnapshotEncryptionKey"] = self.source_snapshot_encryption_key
        d["storageLocations"] = self.storage_locations
        if self.archive_size_bytes is not None and self.archive_size_bytes != "":
            d["archiveSizeBytes"] = self.archive_size_bytes
        if self.source_snapshot_id is not None and self.source_snapshot_id != "":
            d["sourceSnapshotId"] = self.source_snapshot_id
        d["sourceImageEncryptionKey"] = self.source_image_encryption_key
        if self.source_image is not None and self.source_image != "":
            d["sourceImage"] = self.source_image
        if self.source_image_id is not None and self.source_image_id != "":
            d["sourceImageId"] = self.source_image_id
        d["sourceDiskEncryptionKey"] = self.source_disk_encryption_key
        if self.status is not None and self.status != "":
            d["status"] = self.status
        d["guestOsFeatures"] = self.guest_os_features
        if self.disk_size_gb is not None and self.disk_size_gb != "":
            d["diskSizeGb"] = self.disk_size_gb
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#image"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Image_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.images  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "image") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_image_or_error(self, image_name: str) -> Any:
        image = self.resources.get(image_name)
        if image is None:
            return create_gcp_error(
                404,
                f"The resource '{image_name}' was not found",
                "NOT_FOUND",
            )
        return image

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an image in the specified project using the data included
in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("Image") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Image' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"Image {name!r} already exists", "ALREADY_EXISTS")

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        source_disk_ref = body.get("sourceDisk") or ""
        source_disk_name = normalize_name(source_disk_ref)
        if source_disk_name and source_disk_name not in self.state.disks:
            return create_gcp_error(
                404,
                f"Source disk '{source_disk_name}' not found",
                "NOT_FOUND",
            )
        source_snapshot_ref = body.get("sourceSnapshot") or ""
        source_snapshot_name = normalize_name(source_snapshot_ref)
        if source_snapshot_name and source_snapshot_name not in self.state.snapshots:
            return create_gcp_error(
                404,
                f"Source snapshot '{source_snapshot_name}' not found",
                "NOT_FOUND",
            )
        source_image_ref = body.get("sourceImage") or ""
        source_image_name = normalize_name(source_image_ref)
        if source_image_name and source_image_name not in self.state.images:
            return create_gcp_error(
                404,
                f"Source image '{source_image_name}' not found",
                "NOT_FOUND",
            )

        labels = body.get("labels", {})
        label_fingerprint = str(uuid.uuid4())[:8] if labels is not None else ""
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = Image(
            source_type=body.get("sourceType", ""),
            deprecated=body.get("deprecated") or {},
            source_disk=source_disk_ref,
            satisfies_pzi=body.get("satisfiesPzi", False),
            label_fingerprint=label_fingerprint,
            satisfies_pzs=body.get("satisfiesPzs", False),
            licenses=body.get("licenses") or [],
            architecture=body.get("architecture", ""),
            source_disk_id=body.get("sourceDiskId", ""),
            name=name,
            raw_disk=body.get("rawDisk") or {},
            image_encryption_key=body.get("imageEncryptionKey") or {},
            enable_confidential_compute=body.get("enableConfidentialCompute", False),
            description=body.get("description", ""),
            license_codes=body.get("licenseCodes") or [],
            shielded_instance_initial_state=body.get("shieldedInstanceInitialState") or {},
            source_snapshot=source_snapshot_ref,
            creation_timestamp=creation_timestamp,
            params=body.get("params") or {},
            labels=labels or {},
            family=body.get("family", ""),
            source_snapshot_encryption_key=body.get("sourceSnapshotEncryptionKey") or {},
            storage_locations=body.get("storageLocations") or [],
            archive_size_bytes=body.get("archiveSizeBytes", ""),
            source_snapshot_id=body.get("sourceSnapshotId", ""),
            source_image_encryption_key=body.get("sourceImageEncryptionKey") or {},
            source_image=source_image_ref,
            source_image_id=body.get("sourceImageId", ""),
            source_disk_encryption_key=body.get("sourceDiskEncryptionKey") or {},
            status=body.get("status", ""),
            guest_os_features=body.get("guestOsFeatures") or [],
            disk_size_gb=body.get("diskSizeGb", ""),
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/images/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified image."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        image_name = params.get("image")
        if not image_name:
            return create_gcp_error(400, "Required field 'image' not specified", "INVALID_ARGUMENT")
        resource = self._get_image_or_error(image_name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of custom images
available to the specified project. Custom images are images you
create that belong to your project. This method does not
get any images that belong to other pro..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        return {
            "kind": "compute#imageList",
            "id": f"projects/{project}/global/images",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on an image. To learn more about labels, read theLabeling
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
        resource = self._get_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        resource.labels = body.get("labels", {}) or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        return make_operation(
            operation_type="setLabels",
            resource_link=f"projects/{project}/global/images/{resource.name}",
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified image with the data included in the request.
Only the following fields can be modified: family, description,
deprecation status."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        image_name = params.get("image")
        if not image_name:
            return create_gcp_error(400, "Required field 'image' not specified", "INVALID_ARGUMENT")
        body = params.get("Image") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Image' not specified", "INVALID_ARGUMENT")
        resource = self._get_image_or_error(image_name)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "Image name cannot be changed", "INVALID_ARGUMENT")
        if "family" in body:
            resource.family = body.get("family") or ""
        if "description" in body:
            resource.description = body.get("description") or ""
        if "deprecated" in body:
            resource.deprecated = body.get("deprecated") or {}
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/images/{resource.name}",
            params=params,
        )

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
        resource = self._get_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        resource.iam_policy = body.get("policy") or {}
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=f"projects/{project}/global/images/{resource.name}",
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
        resource = self._get_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def deprecate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the deprecation status of an image.

If an empty request body is given, clears the deprecation status instead."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        image_name = params.get("image")
        if not image_name:
            return create_gcp_error(400, "Required field 'image' not specified", "INVALID_ARGUMENT")
        body = params.get("DeprecationStatus")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'DeprecationStatus' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_image_or_error(image_name)
        if is_error_response(resource):
            return resource
        resource.deprecated = body or {}
        return make_operation(
            operation_type="deprecate",
            resource_link=f"projects/{project}/global/images/{resource.name}",
            params=params,
        )

    def getFromFamily(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the latest image that is part of an image family and is not
deprecated. For more information on image families, seePublic
image families documentation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        family = params.get("family")
        if not family:
            return create_gcp_error(400, "Required field 'family' not specified", "INVALID_ARGUMENT")
        resources = [
            resource
            for resource in self.resources.values()
            if resource.family == family
        ]
        if not resources:
            return create_gcp_error(404, f"The resource '{family}' was not found", "NOT_FOUND")
        def is_not_deprecated(resource: Image) -> bool:
            deprecated = resource.deprecated or {}
            state = deprecated.get("state") if isinstance(deprecated, dict) else None
            return not state or state.upper() == "ACTIVE"

        candidates = [resource for resource in resources if is_not_deprecated(resource)]
        if not candidates:
            return create_gcp_error(404, f"The resource '{family}' was not found", "NOT_FOUND")

        def parse_timestamp(value: str) -> datetime:
            if not value:
                return datetime.min.replace(tzinfo=timezone.utc)
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return datetime.min.replace(tzinfo=timezone.utc)

        latest = max(candidates, key=lambda resource: parse_timestamp(resource.creation_timestamp))
        return latest.to_dict()

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        resource = self._get_image_or_error(resource_name)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified image."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        image_name = params.get("image")
        if not image_name:
            return create_gcp_error(400, "Required field 'image' not specified", "INVALID_ARGUMENT")
        resource = self._get_image_or_error(image_name)
        if is_error_response(resource):
            return resource
        del self.resources[image_name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/images/{image_name}",
            params=params,
        )


class image_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setLabels': image_RequestParser._parse_setLabels,
            'testIamPermissions': image_RequestParser._parse_testIamPermissions,
            'patch': image_RequestParser._parse_patch,
            'list': image_RequestParser._parse_list,
            'setIamPolicy': image_RequestParser._parse_setIamPolicy,
            'insert': image_RequestParser._parse_insert,
            'deprecate': image_RequestParser._parse_deprecate,
            'get': image_RequestParser._parse_get,
            'delete': image_RequestParser._parse_delete,
            'getFromFamily': image_RequestParser._parse_getFromFamily,
            'getIamPolicy': image_RequestParser._parse_getIamPolicy,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['Image'] = body.get('Image')
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
    def _parse_insert(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'forceCreate' in query_params:
            params['forceCreate'] = query_params['forceCreate']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Image'] = body.get('Image')
        return params

    @staticmethod
    def _parse_deprecate(
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
        params['DeprecationStatus'] = body.get('DeprecationStatus')
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
    def _parse_getFromFamily(
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


class image_ResponseSerializer:
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
            'setLabels': image_ResponseSerializer._serialize_setLabels,
            'testIamPermissions': image_ResponseSerializer._serialize_testIamPermissions,
            'patch': image_ResponseSerializer._serialize_patch,
            'list': image_ResponseSerializer._serialize_list,
            'setIamPolicy': image_ResponseSerializer._serialize_setIamPolicy,
            'insert': image_ResponseSerializer._serialize_insert,
            'deprecate': image_ResponseSerializer._serialize_deprecate,
            'get': image_ResponseSerializer._serialize_get,
            'delete': image_ResponseSerializer._serialize_delete,
            'getFromFamily': image_ResponseSerializer._serialize_getFromFamily,
            'getIamPolicy': image_ResponseSerializer._serialize_getIamPolicy,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_deprecate(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getFromFamily(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

