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
class RegionDisk:
    resource_policies: List[Any] = field(default_factory=list)
    async_primary_disk: Dict[str, Any] = field(default_factory=dict)
    storage_pool: str = ""
    architecture: str = ""
    last_detach_timestamp: str = ""
    source_instant_snapshot: str = ""
    zone: str = ""
    guest_os_features: List[Any] = field(default_factory=list)
    source_snapshot: str = ""
    source_storage_object: str = ""
    type: str = ""
    options: str = ""
    users: List[Any] = field(default_factory=list)
    async_secondary_disks: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    disk_encryption_key: Dict[str, Any] = field(default_factory=dict)
    source_consistency_group_policy: str = ""
    source_image: str = ""
    size_gb: str = ""
    source_disk: str = ""
    replica_zones: List[Any] = field(default_factory=list)
    source_consistency_group_policy_id: str = ""
    region: str = ""
    last_attach_timestamp: str = ""
    satisfies_pzs: bool = False
    location_hint: str = ""
    provisioned_throughput: str = ""
    resource_status: Dict[str, Any] = field(default_factory=dict)
    source_snapshot_id: str = ""
    enable_confidential_compute: bool = False
    status: str = ""
    description: str = ""
    satisfies_pzi: bool = False
    creation_timestamp: str = ""
    licenses: List[Any] = field(default_factory=list)
    provisioned_iops: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    source_instant_snapshot_id: str = ""
    physical_block_size_bytes: str = ""
    license_codes: List[Any] = field(default_factory=list)
    source_image_encryption_key: Dict[str, Any] = field(default_factory=dict)
    source_snapshot_encryption_key: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    source_image_id: str = ""
    label_fingerprint: str = ""
    access_mode: str = ""
    source_disk_id: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["resourcePolicies"] = self.resource_policies
        d["asyncPrimaryDisk"] = self.async_primary_disk
        if self.storage_pool is not None and self.storage_pool != "":
            d["storagePool"] = self.storage_pool
        if self.architecture is not None and self.architecture != "":
            d["architecture"] = self.architecture
        if self.last_detach_timestamp is not None and self.last_detach_timestamp != "":
            d["lastDetachTimestamp"] = self.last_detach_timestamp
        if self.source_instant_snapshot is not None and self.source_instant_snapshot != "":
            d["sourceInstantSnapshot"] = self.source_instant_snapshot
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        d["guestOsFeatures"] = self.guest_os_features
        if self.source_snapshot is not None and self.source_snapshot != "":
            d["sourceSnapshot"] = self.source_snapshot
        if self.source_storage_object is not None and self.source_storage_object != "":
            d["sourceStorageObject"] = self.source_storage_object
        if self.type is not None and self.type != "":
            d["type"] = self.type
        if self.options is not None and self.options != "":
            d["options"] = self.options
        d["users"] = self.users
        d["asyncSecondaryDisks"] = self.async_secondary_disks
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["diskEncryptionKey"] = self.disk_encryption_key
        if self.source_consistency_group_policy is not None and self.source_consistency_group_policy != "":
            d["sourceConsistencyGroupPolicy"] = self.source_consistency_group_policy
        if self.source_image is not None and self.source_image != "":
            d["sourceImage"] = self.source_image
        if self.size_gb is not None and self.size_gb != "":
            d["sizeGb"] = self.size_gb
        if self.source_disk is not None and self.source_disk != "":
            d["sourceDisk"] = self.source_disk
        d["replicaZones"] = self.replica_zones
        if self.source_consistency_group_policy_id is not None and self.source_consistency_group_policy_id != "":
            d["sourceConsistencyGroupPolicyId"] = self.source_consistency_group_policy_id
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.last_attach_timestamp is not None and self.last_attach_timestamp != "":
            d["lastAttachTimestamp"] = self.last_attach_timestamp
        d["satisfiesPzs"] = self.satisfies_pzs
        if self.location_hint is not None and self.location_hint != "":
            d["locationHint"] = self.location_hint
        if self.provisioned_throughput is not None and self.provisioned_throughput != "":
            d["provisionedThroughput"] = self.provisioned_throughput
        d["resourceStatus"] = self.resource_status
        if self.source_snapshot_id is not None and self.source_snapshot_id != "":
            d["sourceSnapshotId"] = self.source_snapshot_id
        d["enableConfidentialCompute"] = self.enable_confidential_compute
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["satisfiesPzi"] = self.satisfies_pzi
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["licenses"] = self.licenses
        if self.provisioned_iops is not None and self.provisioned_iops != "":
            d["provisionedIops"] = self.provisioned_iops
        d["labels"] = self.labels
        if self.source_instant_snapshot_id is not None and self.source_instant_snapshot_id != "":
            d["sourceInstantSnapshotId"] = self.source_instant_snapshot_id
        if self.physical_block_size_bytes is not None and self.physical_block_size_bytes != "":
            d["physicalBlockSizeBytes"] = self.physical_block_size_bytes
        d["licenseCodes"] = self.license_codes
        d["sourceImageEncryptionKey"] = self.source_image_encryption_key
        d["sourceSnapshotEncryptionKey"] = self.source_snapshot_encryption_key
        d["params"] = self.params
        if self.source_image_id is not None and self.source_image_id != "":
            d["sourceImageId"] = self.source_image_id
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.access_mode is not None and self.access_mode != "":
            d["accessMode"] = self.access_mode
        if self.source_disk_id is not None and self.source_disk_id != "":
            d["sourceDiskId"] = self.source_disk_id
        d["kind"] = "compute#regiondisk"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionDisk_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_disks  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-disk") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_region_disk_or_error(self, params: Dict[str, Any], disk_name: str) -> Any:
        disk = self.resources.get(disk_name)
        if not disk:
            project = params.get("project", "")
            region = params.get("region", "")
            resource_path = f"projects/{project}/regions/{region}/disks/{disk_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return disk

    def _apply_labels(self, resource: RegionDisk, labels: Optional[Dict[str, Any]]) -> None:
        resource.labels = labels or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a persistent regional disk in the specified project using the data
included in the request."""
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
        body = params.get("Disk") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Disk' not found",
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
                f"Disk '{name}' already exists",
                "ALREADY_EXISTS",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        source_disk_ref = body.get("sourceDisk") or ""
        source_disk_name = normalize_name(source_disk_ref)
        if source_disk_name and source_disk_name not in self.resources:
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
        source_image_ref = body.get("sourceImage") or params.get("sourceImage") or ""
        source_image_name = normalize_name(source_image_ref)
        if source_image_name and source_image_name not in self.state.images:
            return create_gcp_error(
                404,
                f"Source image '{source_image_name}' not found",
                "NOT_FOUND",
            )
        storage_pool_ref = body.get("storagePool") or ""
        storage_pool_name = normalize_name(storage_pool_ref)
        if storage_pool_name and storage_pool_name not in self.state.storage_pools:
            return create_gcp_error(
                404,
                f"Storage pool '{storage_pool_name}' not found",
                "NOT_FOUND",
            )
        resource_policies = body.get("resourcePolicies") or []
        for policy in resource_policies:
            policy_name = normalize_name(policy)
            if policy_name and policy_name not in self.state.resource_policies:
                return create_gcp_error(
                    404,
                    f"Resource policy '{policy_name}' not found",
                    "NOT_FOUND",
                )

        size_value = body.get("sizeGb")
        size_gb = str(size_value) if size_value is not None else ""
        resource = RegionDisk(
            resource_policies=resource_policies,
            async_primary_disk=body.get("asyncPrimaryDisk") or {},
            storage_pool=body.get("storagePool") or "",
            architecture=body.get("architecture") or "",
            last_detach_timestamp=body.get("lastDetachTimestamp") or "",
            source_instant_snapshot=body.get("sourceInstantSnapshot") or "",
            zone=body.get("zone") or "",
            guest_os_features=body.get("guestOsFeatures") or [],
            source_snapshot=body.get("sourceSnapshot") or "",
            source_storage_object=body.get("sourceStorageObject") or "",
            type=body.get("type") or "",
            options=body.get("options") or "",
            users=body.get("users") or [],
            async_secondary_disks=body.get("asyncSecondaryDisks") or {},
            name=name,
            disk_encryption_key=body.get("diskEncryptionKey") or {},
            source_consistency_group_policy=body.get("sourceConsistencyGroupPolicy") or "",
            source_image=source_image_ref or "",
            size_gb=size_gb,
            source_disk=source_disk_ref,
            replica_zones=body.get("replicaZones") or [],
            source_consistency_group_policy_id=body.get("sourceConsistencyGroupPolicyId")
            or "",
            region=region,
            last_attach_timestamp=body.get("lastAttachTimestamp") or "",
            satisfies_pzs=bool(body.get("satisfiesPzs"))
            if "satisfiesPzs" in body
            else False,
            location_hint=body.get("locationHint") or "",
            provisioned_throughput=body.get("provisionedThroughput") or "",
            resource_status=body.get("resourceStatus") or {},
            source_snapshot_id=body.get("sourceSnapshotId") or "",
            enable_confidential_compute=bool(body.get("enableConfidentialCompute"))
            if "enableConfidentialCompute" in body
            else False,
            status=body.get("status") or "",
            description=body.get("description") or "",
            satisfies_pzi=bool(body.get("satisfiesPzi")) if "satisfiesPzi" in body else False,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            licenses=body.get("licenses") or [],
            provisioned_iops=body.get("provisionedIops") or "",
            labels=body.get("labels") or {},
            source_instant_snapshot_id=body.get("sourceInstantSnapshotId") or "",
            physical_block_size_bytes=body.get("physicalBlockSizeBytes") or "",
            license_codes=body.get("licenseCodes") or [],
            source_image_encryption_key=body.get("sourceImageEncryptionKey") or {},
            source_snapshot_encryption_key=body.get("sourceSnapshotEncryptionKey") or {},
            params=body.get("params") or {},
            source_image_id=body.get("sourceImageId") or "",
            label_fingerprint=body.get("labelFingerprint") or "",
            access_mode=body.get("accessMode") or "",
            source_disk_id=body.get("sourceDiskId") or "",
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self._apply_labels(resource, body.get("labels"))
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/regions/{region}/RegionDisks/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def bulkInsert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bulk create a set of disks."""
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
        body = params.get("BulkInsertDiskResource") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'BulkInsertDiskResource' not found",
                "INVALID_ARGUMENT",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        disks_payload = body.get("disks") or body.get("items") or []
        if isinstance(disks_payload, dict):
            disk_entries = list(disks_payload.items())
        elif isinstance(disks_payload, list):
            disk_entries = [(disk.get("name"), disk) for disk in disks_payload]
        else:
            disk_entries = []

        for key, disk_body in disk_entries:
            disk_body = disk_body or {}
            name = disk_body.get("name") or key
            if not name:
                return create_gcp_error(
                    400,
                    "Required field 'name' not found",
                    "INVALID_ARGUMENT",
                )
            if name in self.resources:
                return create_gcp_error(
                    409,
                    f"Disk '{name}' already exists",
                    "ALREADY_EXISTS",
                )
            source_disk_ref = disk_body.get("sourceDisk") or ""
            source_disk_name = normalize_name(source_disk_ref)
            if source_disk_name and source_disk_name not in self.resources:
                return create_gcp_error(
                    404,
                    f"Source disk '{source_disk_name}' not found",
                    "NOT_FOUND",
                )
            source_snapshot_ref = disk_body.get("sourceSnapshot") or ""
            source_snapshot_name = normalize_name(source_snapshot_ref)
            if source_snapshot_name and source_snapshot_name not in self.state.snapshots:
                return create_gcp_error(
                    404,
                    f"Source snapshot '{source_snapshot_name}' not found",
                    "NOT_FOUND",
                )
            source_image_ref = (
                disk_body.get("sourceImage")
                or body.get("sourceImage")
                or params.get("sourceImage")
                or ""
            )
            source_image_name = normalize_name(source_image_ref)
            if source_image_name and source_image_name not in self.state.images:
                return create_gcp_error(
                    404,
                    f"Source image '{source_image_name}' not found",
                    "NOT_FOUND",
                )
            storage_pool_ref = disk_body.get("storagePool") or ""
            storage_pool_name = normalize_name(storage_pool_ref)
            if storage_pool_name and storage_pool_name not in self.state.storage_pools:
                return create_gcp_error(
                    404,
                    f"Storage pool '{storage_pool_name}' not found",
                    "NOT_FOUND",
                )
            resource_policies = disk_body.get("resourcePolicies") or []
            for policy in resource_policies:
                policy_name = normalize_name(policy)
                if policy_name and policy_name not in self.state.resource_policies:
                    return create_gcp_error(
                        404,
                        f"Resource policy '{policy_name}' not found",
                        "NOT_FOUND",
                    )

            size_value = disk_body.get("sizeGb")
            size_gb = str(size_value) if size_value is not None else ""
            resource = RegionDisk(
                resource_policies=resource_policies,
                async_primary_disk=disk_body.get("asyncPrimaryDisk") or {},
                storage_pool=disk_body.get("storagePool") or "",
                architecture=disk_body.get("architecture") or "",
                last_detach_timestamp=disk_body.get("lastDetachTimestamp") or "",
                source_instant_snapshot=disk_body.get("sourceInstantSnapshot") or "",
                zone=disk_body.get("zone") or "",
                guest_os_features=disk_body.get("guestOsFeatures") or [],
                source_snapshot=disk_body.get("sourceSnapshot") or "",
                source_storage_object=disk_body.get("sourceStorageObject") or "",
                type=disk_body.get("type") or "",
                options=disk_body.get("options") or "",
                users=disk_body.get("users") or [],
                async_secondary_disks=disk_body.get("asyncSecondaryDisks") or {},
                name=name,
                disk_encryption_key=disk_body.get("diskEncryptionKey") or {},
                source_consistency_group_policy=disk_body.get(
                    "sourceConsistencyGroupPolicy"
                )
                or "",
                source_image=source_image_ref or "",
                size_gb=size_gb,
                source_disk=source_disk_ref,
                replica_zones=disk_body.get("replicaZones") or [],
                source_consistency_group_policy_id=disk_body.get(
                    "sourceConsistencyGroupPolicyId"
                )
                or "",
                region=region,
                last_attach_timestamp=disk_body.get("lastAttachTimestamp") or "",
                satisfies_pzs=bool(disk_body.get("satisfiesPzs"))
                if "satisfiesPzs" in disk_body
                else False,
                location_hint=disk_body.get("locationHint") or "",
                provisioned_throughput=disk_body.get("provisionedThroughput") or "",
                resource_status=disk_body.get("resourceStatus") or {},
                source_snapshot_id=disk_body.get("sourceSnapshotId") or "",
                enable_confidential_compute=bool(
                    disk_body.get("enableConfidentialCompute")
                )
                if "enableConfidentialCompute" in disk_body
                else False,
                status=disk_body.get("status") or "",
                description=disk_body.get("description") or "",
                satisfies_pzi=bool(disk_body.get("satisfiesPzi"))
                if "satisfiesPzi" in disk_body
                else False,
                creation_timestamp=disk_body.get("creationTimestamp")
                or datetime.now(timezone.utc).isoformat(),
                licenses=disk_body.get("licenses") or [],
                provisioned_iops=disk_body.get("provisionedIops") or "",
                labels=disk_body.get("labels") or {},
                source_instant_snapshot_id=disk_body.get("sourceInstantSnapshotId") or "",
                physical_block_size_bytes=disk_body.get("physicalBlockSizeBytes") or "",
                license_codes=disk_body.get("licenseCodes") or [],
                source_image_encryption_key=disk_body.get("sourceImageEncryptionKey") or {},
                source_snapshot_encryption_key=disk_body.get(
                    "sourceSnapshotEncryptionKey"
                )
                or {},
                params=disk_body.get("params") or {},
                source_image_id=disk_body.get("sourceImageId") or "",
                label_fingerprint=disk_body.get("labelFingerprint") or "",
                access_mode=disk_body.get("accessMode") or "",
                source_disk_id=disk_body.get("sourceDiskId") or "",
                id=self._generate_id(),
                iam_policy=disk_body.get("iamPolicy") or {},
            )
            self._apply_labels(resource, disk_body.get("labels"))
            self.resources[resource.name] = resource

        resource_link = f"projects/{project}/regions/{region}/disks"
        return make_operation(
            operation_type="bulkInsert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns a specified regional persistent disk."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of persistent disks contained within
the specified region."""
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
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]
        return {
            "kind": "compute#regiondiskList",
            "id": f"projects/{project}/regions/{region}/disks",
            "items": [r.to_dict() for r in resources],
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
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionSetPolicyRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, resource_name)
        if is_error_response(resource):
            return resource
        resource.iam_policy = body.get("policy") or {}
        return resource.to_dict()

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on the target regional disk."""
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
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionSetLabelsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionSetLabelsRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, resource_name)
        if is_error_response(resource):
            return resource
        labels = body.get("labels") if isinstance(body, dict) else {}
        self._apply_labels(resource, labels)
        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="setLabels",
            resource_link=resource_link,
            params=params,
        )

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update the specified disk with the data included in the request. Update is
performed only on selected fields included as part of update-mask. Only the
following fields can be modified: user_license."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Disk") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Disk' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource

        update_mask = params.get("updateMask") or params.get("paths") or ""
        fields = {part.strip() for part in update_mask.split(",") if part.strip()}
        if not fields:
            fields = {"labels", "description", "sizeGb", "resourcePolicies", "status"}

        if "labels" in fields and "labels" in body:
            self._apply_labels(resource, body.get("labels"))
        if "description" in fields and "description" in body:
            resource.description = body.get("description") or ""
        if "sizeGb" in fields and "sizeGb" in body:
            size_value = body.get("sizeGb")
            resource.size_gb = str(size_value) if size_value is not None else ""
        if "resourcePolicies" in fields and "resourcePolicies" in body:
            resource.resource_policies = body.get("resourcePolicies") or []
        if "status" in fields and "status" in body:
            resource.status = body.get("status") or ""

        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )

    def startAsyncReplication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Starts asynchronous replication.
Must be invoked on the primary disk."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionDisksStartAsyncReplicationRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionDisksStartAsyncReplicationRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource

        resource.async_primary_disk = body.get("asyncPrimaryDisk") or resource.async_primary_disk
        if body.get("secondaryDisk"):
            resource.async_secondary_disks = body.get("secondaryDisk") or resource.async_secondary_disks
        resource.status = body.get("status") or resource.status or "READY"

        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="startAsyncReplication",
            resource_link=resource_link,
            params=params,
        )

    def stopAsyncReplication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stops asynchronous replication.
Can be invoked either on the primary or on the secondary disk."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource

        resource.async_primary_disk = {}
        resource.async_secondary_disks = {}
        resource.status = "READY"

        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="stopAsyncReplication",
            resource_link=resource_link,
            params=params,
        )

    def createSnapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a snapshot of a specified persistent disk. For regular snapshot
creation, consider using snapshots.insert
instead, as that method supports more features, such as creating snapshots
in a pro..."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Snapshot") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Snapshot' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource
        snapshot_name = body.get("name")
        if not snapshot_name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )
        if snapshot_name in self.state.snapshots:
            return create_gcp_error(
                409,
                f"Snapshot '{snapshot_name}' already exists",
                "ALREADY_EXISTS",
            )

        snapshot = {
            "name": snapshot_name,
            "sourceDisk": resource.name,
            "creationTimestamp": body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            "labels": body.get("labels") or {},
            "description": body.get("description") or "",
            "diskSizeGb": body.get("diskSizeGb") or resource.size_gb,
        }
        self.state.snapshots[snapshot_name] = snapshot
        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="createSnapshot",
            resource_link=resource_link,
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
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
        resource = self._get_region_disk_or_error(params, resource_name)
        if is_error_response(resource):
            return resource

        permissions = body.get("permissions") or []
        allowed = [perm for perm in permissions if perm]
        return {"permissions": allowed}

    def removeResourcePolicies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes resource policies from a regional disk."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionDisksRemoveResourcePoliciesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionDisksRemoveResourcePoliciesRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource
        policies = body.get("resourcePolicies") or []
        if policies:
            resource.resource_policies = [
                policy
                for policy in resource.resource_policies
                if policy not in policies
            ]
        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="removeResourcePolicies",
            resource_link=resource_link,
            params=params,
        )

    def addResourcePolicies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds existing resource policies to a regional disk. You can only add one
policy which will be applied to this disk for scheduling snapshot
creation."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionDisksAddResourcePoliciesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionDisksAddResourcePoliciesRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource
        policies = body.get("resourcePolicies") or []
        if policies:
            for policy in policies:
                policy_name = policy.split("/")[-1] if isinstance(policy, str) else ""
                if policy_name and policy_name not in self.state.resource_policies:
                    return create_gcp_error(
                        404,
                        f"Resource policy '{policy_name}' not found",
                        "NOT_FOUND",
                    )
            for policy in policies:
                if policy not in resource.resource_policies:
                    resource.resource_policies.append(policy)
        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="addResourcePolicies",
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
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, resource_name)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

    def stopGroupAsyncReplication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stops asynchronous replication for a consistency group of disks.
Can be invoked either in the primary or secondary scope."""
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
        body = params.get("DisksStopGroupAsyncReplicationResource") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'DisksStopGroupAsyncReplicationResource' not found",
                "INVALID_ARGUMENT",
            )

        disk_names = body.get("disks") or body.get("diskNames") or []
        for disk_name in disk_names:
            disk = self.resources.get(disk_name)
            if not disk:
                return create_gcp_error(
                    404,
                    f"Disk '{disk_name}' not found",
                    "NOT_FOUND",
                )
            disk.async_primary_disk = {}
            disk.async_secondary_disks = {}
            disk.status = "READY"

        resource_link = f"projects/{project}/regions/{region}/disks"
        return make_operation(
            operation_type="stopGroupAsyncReplication",
            resource_link=resource_link,
            params=params,
        )

    def resize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resizes the specified regional persistent disk."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionDisksResizeRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionDisksResizeRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource
        if "sizeGb" not in body:
            return create_gcp_error(
                400,
                "Required field 'sizeGb' not found",
                "INVALID_ARGUMENT",
            )
        size_value = body.get("sizeGb")
        resource.size_gb = str(size_value) if size_value is not None else ""
        resource_link = f"projects/{project}/regions/{region}/disks/{resource.name}"
        return make_operation(
            operation_type="resize",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified regional persistent disk. Deleting a regional disk
removes all the replicas of its data permanently and is irreversible.
However, deleting a disk does not delete anysnapshots
..."""
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
        disk_name = params.get("disk")
        if not disk_name:
            return create_gcp_error(
                400,
                "Required field 'disk' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_region_disk_or_error(params, disk_name)
        if is_error_response(resource):
            return resource
        if resource.users:
            return create_gcp_error(
                400,
                "Disk is currently in use",
                "FAILED_PRECONDITION",
            )
        self.resources.pop(resource.name, None)
        resource_link = f"projects/{project}/regions/{region}/disks/{disk_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class region_disk_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setIamPolicy': region_disk_RequestParser._parse_setIamPolicy,
            'list': region_disk_RequestParser._parse_list,
            'startAsyncReplication': region_disk_RequestParser._parse_startAsyncReplication,
            'stopAsyncReplication': region_disk_RequestParser._parse_stopAsyncReplication,
            'insert': region_disk_RequestParser._parse_insert,
            'createSnapshot': region_disk_RequestParser._parse_createSnapshot,
            'testIamPermissions': region_disk_RequestParser._parse_testIamPermissions,
            'removeResourcePolicies': region_disk_RequestParser._parse_removeResourcePolicies,
            'delete': region_disk_RequestParser._parse_delete,
            'bulkInsert': region_disk_RequestParser._parse_bulkInsert,
            'addResourcePolicies': region_disk_RequestParser._parse_addResourcePolicies,
            'getIamPolicy': region_disk_RequestParser._parse_getIamPolicy,
            'get': region_disk_RequestParser._parse_get,
            'setLabels': region_disk_RequestParser._parse_setLabels,
            'update': region_disk_RequestParser._parse_update,
            'stopGroupAsyncReplication': region_disk_RequestParser._parse_stopGroupAsyncReplication,
            'resize': region_disk_RequestParser._parse_resize,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
    def _parse_startAsyncReplication(
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
        params['RegionDisksStartAsyncReplicationRequest'] = body.get('RegionDisksStartAsyncReplicationRequest')
        return params

    @staticmethod
    def _parse_stopAsyncReplication(
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
        # Full request body (resource representation)
        params["body"] = body
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
        if 'sourceImage' in query_params:
            params['sourceImage'] = query_params['sourceImage']
        # Body params
        params['Disk'] = body.get('Disk')
        return params

    @staticmethod
    def _parse_createSnapshot(
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
    def _parse_removeResourcePolicies(
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
        params['RegionDisksRemoveResourcePoliciesRequest'] = body.get('RegionDisksRemoveResourcePoliciesRequest')
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
    def _parse_bulkInsert(
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
        params['BulkInsertDiskResource'] = body.get('BulkInsertDiskResource')
        return params

    @staticmethod
    def _parse_addResourcePolicies(
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
        params['RegionDisksAddResourcePoliciesRequest'] = body.get('RegionDisksAddResourcePoliciesRequest')
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
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['RegionSetLabelsRequest'] = body.get('RegionSetLabelsRequest')
        return params

    @staticmethod
    def _parse_update(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'paths' in query_params:
            params['paths'] = query_params['paths']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['Disk'] = body.get('Disk')
        return params

    @staticmethod
    def _parse_stopGroupAsyncReplication(
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
        params['DisksStopGroupAsyncReplicationResource'] = body.get('DisksStopGroupAsyncReplicationResource')
        return params

    @staticmethod
    def _parse_resize(
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
        params['RegionDisksResizeRequest'] = body.get('RegionDisksResizeRequest')
        return params


class region_disk_ResponseSerializer:
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
            'setIamPolicy': region_disk_ResponseSerializer._serialize_setIamPolicy,
            'list': region_disk_ResponseSerializer._serialize_list,
            'startAsyncReplication': region_disk_ResponseSerializer._serialize_startAsyncReplication,
            'stopAsyncReplication': region_disk_ResponseSerializer._serialize_stopAsyncReplication,
            'insert': region_disk_ResponseSerializer._serialize_insert,
            'createSnapshot': region_disk_ResponseSerializer._serialize_createSnapshot,
            'testIamPermissions': region_disk_ResponseSerializer._serialize_testIamPermissions,
            'removeResourcePolicies': region_disk_ResponseSerializer._serialize_removeResourcePolicies,
            'delete': region_disk_ResponseSerializer._serialize_delete,
            'bulkInsert': region_disk_ResponseSerializer._serialize_bulkInsert,
            'addResourcePolicies': region_disk_ResponseSerializer._serialize_addResourcePolicies,
            'getIamPolicy': region_disk_ResponseSerializer._serialize_getIamPolicy,
            'get': region_disk_ResponseSerializer._serialize_get,
            'setLabels': region_disk_ResponseSerializer._serialize_setLabels,
            'update': region_disk_ResponseSerializer._serialize_update,
            'stopGroupAsyncReplication': region_disk_ResponseSerializer._serialize_stopGroupAsyncReplication,
            'resize': region_disk_ResponseSerializer._serialize_resize,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_startAsyncReplication(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_stopAsyncReplication(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_createSnapshot(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeResourcePolicies(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_bulkInsert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addResourcePolicies(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_stopGroupAsyncReplication(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_resize(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

