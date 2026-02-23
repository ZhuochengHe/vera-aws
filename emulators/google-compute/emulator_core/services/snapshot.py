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
class Snapshot:
    source_disk_for_recovery_checkpoint: str = ""
    storage_locations: List[Any] = field(default_factory=list)
    source_instant_snapshot_id: str = ""
    satisfies_pzs: bool = False
    source_disk_encryption_key: Dict[str, Any] = field(default_factory=dict)
    location_hint: str = ""
    creation_size_bytes: str = ""
    creation_timestamp: str = ""
    snapshot_encryption_key: Dict[str, Any] = field(default_factory=dict)
    source_instant_snapshot: str = ""
    chain_name: str = ""
    snapshot_type: str = ""
    auto_created: bool = False
    status: str = ""
    description: str = ""
    storage_bytes_status: str = ""
    license_codes: List[Any] = field(default_factory=list)
    storage_bytes: str = ""
    enable_confidential_compute: bool = False
    satisfies_pzi: bool = False
    source_instant_snapshot_encryption_key: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, Any] = field(default_factory=dict)
    licenses: List[Any] = field(default_factory=list)
    source_disk: str = ""
    guest_flush: bool = False
    label_fingerprint: str = ""
    name: str = ""
    download_bytes: str = ""
    guest_os_features: List[Any] = field(default_factory=list)
    source_snapshot_schedule_policy_id: str = ""
    architecture: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    disk_size_gb: str = ""
    source_disk_id: str = ""
    source_snapshot_schedule_policy: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.source_disk_for_recovery_checkpoint is not None and self.source_disk_for_recovery_checkpoint != "":
            d["sourceDiskForRecoveryCheckpoint"] = self.source_disk_for_recovery_checkpoint
        d["storageLocations"] = self.storage_locations
        if self.source_instant_snapshot_id is not None and self.source_instant_snapshot_id != "":
            d["sourceInstantSnapshotId"] = self.source_instant_snapshot_id
        d["satisfiesPzs"] = self.satisfies_pzs
        d["sourceDiskEncryptionKey"] = self.source_disk_encryption_key
        if self.location_hint is not None and self.location_hint != "":
            d["locationHint"] = self.location_hint
        if self.creation_size_bytes is not None and self.creation_size_bytes != "":
            d["creationSizeBytes"] = self.creation_size_bytes
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["snapshotEncryptionKey"] = self.snapshot_encryption_key
        if self.source_instant_snapshot is not None and self.source_instant_snapshot != "":
            d["sourceInstantSnapshot"] = self.source_instant_snapshot
        if self.chain_name is not None and self.chain_name != "":
            d["chainName"] = self.chain_name
        if self.snapshot_type is not None and self.snapshot_type != "":
            d["snapshotType"] = self.snapshot_type
        d["autoCreated"] = self.auto_created
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.storage_bytes_status is not None and self.storage_bytes_status != "":
            d["storageBytesStatus"] = self.storage_bytes_status
        d["licenseCodes"] = self.license_codes
        if self.storage_bytes is not None and self.storage_bytes != "":
            d["storageBytes"] = self.storage_bytes
        d["enableConfidentialCompute"] = self.enable_confidential_compute
        d["satisfiesPzi"] = self.satisfies_pzi
        d["sourceInstantSnapshotEncryptionKey"] = self.source_instant_snapshot_encryption_key
        d["labels"] = self.labels
        d["licenses"] = self.licenses
        if self.source_disk is not None and self.source_disk != "":
            d["sourceDisk"] = self.source_disk
        d["guestFlush"] = self.guest_flush
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.download_bytes is not None and self.download_bytes != "":
            d["downloadBytes"] = self.download_bytes
        d["guestOsFeatures"] = self.guest_os_features
        if self.source_snapshot_schedule_policy_id is not None and self.source_snapshot_schedule_policy_id != "":
            d["sourceSnapshotSchedulePolicyId"] = self.source_snapshot_schedule_policy_id
        if self.architecture is not None and self.architecture != "":
            d["architecture"] = self.architecture
        d["params"] = self.params
        if self.disk_size_gb is not None and self.disk_size_gb != "":
            d["diskSizeGb"] = self.disk_size_gb
        if self.source_disk_id is not None and self.source_disk_id != "":
            d["sourceDiskId"] = self.source_disk_id
        if self.source_snapshot_schedule_policy is not None and self.source_snapshot_schedule_policy != "":
            d["sourceSnapshotSchedulePolicy"] = self.source_snapshot_schedule_policy
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["iamPolicy"] = self.iam_policy
        d["kind"] = "compute#snapshot"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Snapshot_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.snapshots  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "snapshot") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_snapshot_or_error(self, snapshot_name: str) -> Any:
        snapshot = self.resources.get(snapshot_name)
        if snapshot is None:
            return create_gcp_error(
                404,
                f"The resource '{snapshot_name}' was not found",
                "NOT_FOUND",
            )
        return snapshot

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a snapshot in the specified project using the data included
in the request. For regular snapshot creation, consider using this method
instead of disks.createSnapshot,
as this method support..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Snapshot") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Snapshot' not found",
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
                f"Snapshot '{name}' already exists",
                "ALREADY_EXISTS",
            )

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
        source_instant_snapshot_ref = body.get("sourceInstantSnapshot") or ""
        source_instant_snapshot_name = normalize_name(source_instant_snapshot_ref)
        if (
            source_instant_snapshot_name
            and source_instant_snapshot_name not in self.state.instant_snapshots
        ):
            return create_gcp_error(
                404,
                f"Source instant snapshot '{source_instant_snapshot_name}' not found",
                "NOT_FOUND",
            )
        source_policy_ref = body.get("sourceSnapshotSchedulePolicy") or ""
        source_policy_name = normalize_name(source_policy_ref)
        if source_policy_name and source_policy_name not in self.state.resource_policies:
            return create_gcp_error(
                404,
                f"Resource policy '{source_policy_name}' not found",
                "NOT_FOUND",
            )

        labels = body.get("labels", {})
        label_fingerprint = str(uuid.uuid4())[:8] if labels is not None else ""
        disk_size_value = body.get("diskSizeGb")
        disk_size_gb = str(disk_size_value) if disk_size_value is not None else ""
        storage_bytes_value = body.get("storageBytes")
        storage_bytes = (
            str(storage_bytes_value) if storage_bytes_value is not None else ""
        )
        creation_size_value = body.get("creationSizeBytes")
        creation_size_bytes = (
            str(creation_size_value) if creation_size_value is not None else ""
        )
        download_bytes_value = body.get("downloadBytes")
        download_bytes = (
            str(download_bytes_value) if download_bytes_value is not None else ""
        )
        resource = Snapshot(
            source_disk_for_recovery_checkpoint=body.get(
                "sourceDiskForRecoveryCheckpoint"
            )
            or "",
            storage_locations=body.get("storageLocations") or [],
            source_instant_snapshot_id=body.get("sourceInstantSnapshotId") or "",
            satisfies_pzs=bool(body.get("satisfiesPzs"))
            if "satisfiesPzs" in body
            else False,
            source_disk_encryption_key=body.get("sourceDiskEncryptionKey") or {},
            location_hint=body.get("locationHint") or "",
            creation_size_bytes=creation_size_bytes,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            snapshot_encryption_key=body.get("snapshotEncryptionKey") or {},
            source_instant_snapshot=source_instant_snapshot_ref,
            chain_name=body.get("chainName") or "",
            snapshot_type=body.get("snapshotType") or "",
            auto_created=bool(body.get("autoCreated"))
            if "autoCreated" in body
            else False,
            status=body.get("status") or "",
            description=body.get("description") or "",
            storage_bytes_status=body.get("storageBytesStatus") or "",
            license_codes=body.get("licenseCodes") or [],
            storage_bytes=storage_bytes,
            enable_confidential_compute=bool(body.get("enableConfidentialCompute"))
            if "enableConfidentialCompute" in body
            else False,
            satisfies_pzi=bool(body.get("satisfiesPzi"))
            if "satisfiesPzi" in body
            else False,
            source_instant_snapshot_encryption_key=body.get(
                "sourceInstantSnapshotEncryptionKey"
            )
            or {},
            labels=labels or {},
            licenses=body.get("licenses") or [],
            source_disk=source_disk_ref,
            guest_flush=bool(body.get("guestFlush")) if "guestFlush" in body else False,
            label_fingerprint=label_fingerprint,
            name=name,
            download_bytes=download_bytes,
            guest_os_features=body.get("guestOsFeatures") or [],
            source_snapshot_schedule_policy_id=body.get(
                "sourceSnapshotSchedulePolicyId"
            )
            or "",
            architecture=body.get("architecture") or "",
            params=body.get("params") or {},
            disk_size_gb=disk_size_gb,
            source_disk_id=body.get("sourceDiskId") or "",
            source_snapshot_schedule_policy=source_policy_ref,
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/global/snapshots/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified Snapshot resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        snapshot_name = params.get("snapshot")
        if not snapshot_name:
            return create_gcp_error(
                400,
                "Required field 'snapshot' not found",
                "INVALID_ARGUMENT",
            )
        snapshot = self._get_snapshot_or_error(snapshot_name)
        if is_error_response(snapshot):
            return snapshot
        if isinstance(snapshot, Snapshot):
            return snapshot.to_dict()
        return snapshot

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of Snapshot resources contained within
the specified project."""
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
                    r
                    for r in resources
                    if (
                        r.name == match.group(1)
                        if isinstance(r, Snapshot)
                        else r.get("name") == match.group(1)
                    )
                ]

        def serialize(resource: Any) -> Dict[str, Any]:
            if isinstance(resource, Snapshot):
                return resource.to_dict()
            return resource

        return {
            "kind": "compute#snapshotList",
            "id": f"projects/{project}/global/snapshots",
            "items": [serialize(resource) for resource in resources],
            "selfLink": "",
        }

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
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
        body = params.get("GlobalSetPolicyRequest")
        if not body:
            return create_gcp_error(
                400,
                "Required field 'GlobalSetPolicyRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_snapshot_or_error(resource_name)
        if is_error_response(resource):
            return resource
        policy = body.get("policy") or {}
        if isinstance(resource, Snapshot):
            resource.iam_policy = policy
            resource_link = f"projects/{project}/global/snapshots/{resource.name}"
        else:
            resource["iamPolicy"] = policy
            resource_link = f"projects/{project}/global/snapshots/{resource_name}"
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=resource_link,
            params=params,
        )

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a snapshot. To learn more about labels, read theLabeling
Resources documentation."""
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
        body = params.get("GlobalSetLabelsRequest")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'GlobalSetLabelsRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_snapshot_or_error(resource_name)
        if is_error_response(resource):
            return resource
        labels = body.get("labels", {}) or {}
        label_fingerprint = str(uuid.uuid4())[:8]
        if isinstance(resource, Snapshot):
            resource.labels = labels
            resource.label_fingerprint = label_fingerprint
            resource_link = f"projects/{project}/global/snapshots/{resource.name}"
        else:
            resource["labels"] = labels
            resource["labelFingerprint"] = label_fingerprint
            resource_link = f"projects/{project}/global/snapshots/{resource_name}"
        return make_operation(
            operation_type="setLabels",
            resource_link=resource_link,
            params=params,
        )

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
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
        resource = self._get_snapshot_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if isinstance(resource, Snapshot):
            return resource.iam_policy or {}
        return resource.get("iamPolicy") or {}

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
        resource = self._get_snapshot_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified Snapshot resource. Keep in mind that deleting
a single snapshot might not necessarily delete all the data on that
snapshot. If any data on the snapshot that is marked for dele..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        snapshot_name = params.get("snapshot")
        if not snapshot_name:
            return create_gcp_error(
                400,
                "Required field 'snapshot' not found",
                "INVALID_ARGUMENT",
            )
        snapshot = self._get_snapshot_or_error(snapshot_name)
        if is_error_response(snapshot):
            return snapshot
        if isinstance(snapshot, Snapshot):
            del self.resources[snapshot.name]
        else:
            self.resources.pop(snapshot_name, None)
        resource_link = f"projects/{project}/global/snapshots/{snapshot_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class snapshot_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': snapshot_RequestParser._parse_get,
            'getIamPolicy': snapshot_RequestParser._parse_getIamPolicy,
            'testIamPermissions': snapshot_RequestParser._parse_testIamPermissions,
            'setIamPolicy': snapshot_RequestParser._parse_setIamPolicy,
            'delete': snapshot_RequestParser._parse_delete,
            'setLabels': snapshot_RequestParser._parse_setLabels,
            'insert': snapshot_RequestParser._parse_insert,
            'list': snapshot_RequestParser._parse_list,
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
        params['Snapshot'] = body.get('Snapshot')
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


class snapshot_ResponseSerializer:
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
            'get': snapshot_ResponseSerializer._serialize_get,
            'getIamPolicy': snapshot_ResponseSerializer._serialize_getIamPolicy,
            'testIamPermissions': snapshot_ResponseSerializer._serialize_testIamPermissions,
            'setIamPolicy': snapshot_ResponseSerializer._serialize_setIamPolicy,
            'delete': snapshot_ResponseSerializer._serialize_delete,
            'setLabels': snapshot_ResponseSerializer._serialize_setLabels,
            'insert': snapshot_ResponseSerializer._serialize_insert,
            'list': snapshot_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

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
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

