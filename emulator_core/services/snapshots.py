from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class SnapshotStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"
    RECOVERABLE = "recoverable"
    RECOVERING = "recovering"


class SnapshotStorageTier(str, Enum):
    ARCHIVE = "archive"
    STANDARD = "standard"


class SnapshotTransferType(str, Enum):
    TIME_BASED = "time-based"
    STANDARD = "standard"


class SnapshotLockState(str, Enum):
    COMPLIANCE = "compliance"
    GOVERNANCE = "governance"
    COMPLIANCE_COOL_OFF = "compliance-cooloff"
    EXPIRED = "expired"


class SnapshotLockMode(str, Enum):
    COMPLIANCE = "compliance"
    GOVERNANCE = "governance"


class SnapshotBlockPublicAccessState(str, Enum):
    BLOCK_ALL_SHARING = "block-all-sharing"
    BLOCK_NEW_SHARING = "block-new-sharing"
    UNBLOCKED = "unblocked"


class SnapshotTieringOperationStatus(str, Enum):
    ARCHIVAL_IN_PROGRESS = "archival-in-progress"
    ARCHIVAL_COMPLETED = "archival-completed"
    ARCHIVAL_FAILED = "archival-failed"
    TEMPORARY_RESTORE_IN_PROGRESS = "temporary-restore-in-progress"
    TEMPORARY_RESTORE_COMPLETED = "temporary-restore-completed"
    TEMPORARY_RESTORE_FAILED = "temporary-restore-failed"
    PERMANENT_RESTORE_IN_PROGRESS = "permanent-restore-in-progress"
    PERMANENT_RESTORE_COMPLETED = "permanent-restore-completed"
    PERMANENT_RESTORE_FAILED = "permanent-restore-failed"


class SseType(str, Enum):
    SSE_EBS = "sse-ebs"
    SSE_KMS = "sse-kms"
    NONE = "none"


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class TagSpecification:
    resource_type: str
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class CreateVolumePermission:
    group: Optional[str] = None  # e.g. "all"
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.group is not None:
            d["Group"] = self.group
        if self.user_id is not None:
            d["UserId"] = self.user_id
        return d


@dataclass
class CreateVolumePermissionModifications:
    add: List[CreateVolumePermission] = field(default_factory=list)
    remove: List[CreateVolumePermission] = field(default_factory=list)


@dataclass
class ProductCode:
    product_code: Optional[str] = None
    type: Optional[str] = None  # devpay | marketplace

    def to_dict(self) -> Dict[str, Any]:
        return {
            "productCode": self.product_code,
            "type": self.type,
        }


@dataclass
class Filter:
    name: str
    values: List[str] = field(default_factory=list)


@dataclass
class InstanceSpecification:
    instance_id: str
    exclude_boot_volume: Optional[bool] = None
    exclude_data_volume_ids: List[str] = field(default_factory=list)


@dataclass
class SnapshotInfo:
    availability_zone: Optional[str] = None
    description: Optional[str] = None
    encrypted: Optional[bool] = None
    outpost_arn: Optional[str] = None
    owner_id: Optional[str] = None
    progress: Optional[str] = None
    snapshot_id: Optional[str] = None
    sse_type: Optional[SseType] = None
    start_time: Optional[datetime] = None
    state: Optional[SnapshotStatus] = None
    tag_set: List[Tag] = field(default_factory=list)
    volume_id: Optional[str] = None
    volume_size: Optional[int] = None


@dataclass
class LockedSnapshotsInfo:
    cool_off_period: Optional[int] = None  # hours
    cool_off_period_expires_on: Optional[datetime] = None
    lock_created_on: Optional[datetime] = None
    lock_duration: Optional[int] = None  # days
    lock_duration_start_time: Optional[datetime] = None
    lock_expires_on: Optional[datetime] = None
    lock_state: Optional[SnapshotLockState] = None
    owner_id: Optional[str] = None
    snapshot_id: Optional[str] = None


@dataclass
class SnapshotRecycleBinInfo:
    description: Optional[str] = None
    recycle_bin_enter_time: Optional[datetime] = None
    recycle_bin_exit_time: Optional[datetime] = None
    snapshot_id: Optional[str] = None
    volume_id: Optional[str] = None


@dataclass
class SnapshotTierStatus:
    archival_complete_time: Optional[datetime] = None
    last_tiering_operation_status: Optional[SnapshotTieringOperationStatus] = None
    last_tiering_operation_status_detail: Optional[str] = None
    last_tiering_progress: Optional[int] = None  # percentage
    last_tiering_start_time: Optional[datetime] = None
    owner_id: Optional[str] = None
    restore_expiry_time: Optional[datetime] = None
    snapshot_id: Optional[str] = None
    status: Optional[SnapshotStatus] = None
    storage_tier: Optional[SnapshotStorageTier] = None
    tag_set: List[Tag] = field(default_factory=list)
    volume_id: Optional[str] = None


@dataclass
class Snapshot:
    snapshot_id: str
    volume_id: str
    status: SnapshotStatus = SnapshotStatus.PENDING
    start_time: Optional[datetime] = None
    progress: Optional[str] = None
    owner_id: Optional[str] = None
    volume_size: Optional[int] = None
    description: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    encrypted: Optional[bool] = False
    kms_key_id: Optional[str] = None
    storage_tier: SnapshotStorageTier = SnapshotStorageTier.STANDARD
    transfer_type: Optional[SnapshotTransferType] = None
    completion_time: Optional[datetime] = None
    full_snapshot_size_in_bytes: Optional[int] = None
    outpost_arn: Optional[str] = None
    owner_alias: Optional[str] = None
    restore_expiry_time: Optional[datetime] = None
    sse_type: Optional[SseType] = None
    status_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshotId": self.snapshot_id,
            "volumeId": self.volume_id,
            "status": self.status.value,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "progress": self.progress,
            "ownerId": self.owner_id,
            "volumeSize": self.volume_size,
            "description": self.description,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "encrypted": self.encrypted,
            "kmsKeyId": self.kms_key_id,
            "storageTier": self.storage_tier.value if self.storage_tier else None,
            "transferType": self.transfer_type.value if self.transfer_type else None,
            "completionTime": self.completion_time.isoformat() if self.completion_time else None,
            "fullSnapshotSizeInBytes": self.full_snapshot_size_in_bytes,
            "outpostArn": self.outpost_arn,
            "ownerAlias": self.owner_alias,
            "restoreExpiryTime": self.restore_expiry_time.isoformat() if self.restore_expiry_time else None,
            "sseType": self.sse_type.value if self.sse_type else None,
            "statusMessage": self.status_message,
        }


class SnapshotsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state.snapshots

    def copy_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import copy
        from datetime import datetime

        source_region = params.get("SourceRegion")
        source_snapshot_id = params.get("SourceSnapshotId")
        if not source_region:
            raise ValueError("SourceRegion is required")
        if not source_snapshot_id:
            raise ValueError("SourceSnapshotId is required")

        # Find source snapshot in state.snapshots by snapshot_id
        source_snapshot = self.state.snapshots.get(source_snapshot_id)
        if not source_snapshot:
            raise ValueError(f"Source snapshot {source_snapshot_id} not found")

        # Validate encryption parameters
        encrypted = params.get("Encrypted")
        kms_key_id = params.get("KmsKeyId")
        if kms_key_id and not encrypted:
            raise ValueError("Encrypted must be true if KmsKeyId is specified")
        if encrypted is False:
            raise ValueError("Encrypted cannot be set to false")

        # Create new snapshot id
        new_snapshot_id = self.generate_unique_id(prefix="snap-")

        # Copy tags from TagSpecification if provided
        tag_specifications = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") == "snapshot":
                for tag in tag_spec.get("Tags", []):
                    key = tag.get("Key")
                    value = tag.get("Value")
                    if key is not None and value is not None:
                        tags.append(Tag(key=key, value=value))

        # If no tags from TagSpecification, copy tags from source snapshot
        if not tags:
            tags = copy.deepcopy(source_snapshot.tag_set)

        # Description
        description = params.get("Description", source_snapshot.description)

        # Storage tier defaults to source snapshot's storage tier
        storage_tier = source_snapshot.storage_tier

        # Transfer type: standard or time-based
        transfer_type = None
        if params.get("CompletionDurationMinutes") is not None:
            transfer_type = SnapshotTransferType.TIME_BASED
        else:
            transfer_type = SnapshotTransferType.STANDARD

        # Create new snapshot object
        new_snapshot = Snapshot(
            snapshot_id=new_snapshot_id,
            volume_id=source_snapshot.volume_id,
            status=SnapshotStatus.PENDING,
            start_time=datetime.utcnow(),
            progress="0%",
            owner_id=self.get_owner_id(),
            volume_size=source_snapshot.volume_size,
            description=description,
            tag_set=tags,
            encrypted=encrypted if encrypted is not None else source_snapshot.encrypted,
            kms_key_id=kms_key_id if kms_key_id else source_snapshot.kms_key_id,
            storage_tier=storage_tier,
            transfer_type=transfer_type,
            completion_time=None,
            full_snapshot_size_in_bytes=source_snapshot.full_snapshot_size_in_bytes,
            outpost_arn=params.get("DestinationOutpostArn", source_snapshot.outpost_arn),
            owner_alias=None,
            restore_expiry_time=None,
            sse_type=source_snapshot.sse_type,
            status_message=None,
        )

        # Save new snapshot in state
        self.state.snapshots[new_snapshot_id] = new_snapshot
        self.state.resources[new_snapshot_id] = new_snapshot

        return {
            "requestId": self.generate_request_id(),
            "snapshotId": new_snapshot_id,
            "tagSet": [tag.to_dict() for tag in tags],
        }


    def create_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from datetime import datetime

        volume_id = params.get("VolumeId")
        if not volume_id:
            raise ValueError("VolumeId is required")

        # Validate volume exists
        volume = self.state.get_resource(volume_id)
        if not volume:
            raise ValueError(f"Volume {volume_id} not found")

        # Description
        description = params.get("Description")

        # Tags from TagSpecification
        tag_specifications = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") == "snapshot":
                for tag in tag_spec.get("Tags", []):
                    key = tag.get("Key")
                    value = tag.get("Value")
                    if key is not None and value is not None:
                        tags.append(Tag(key=key, value=value))

        # Create snapshot id
        snapshot_id = self.generate_unique_id(prefix="snap-")

        # Create snapshot object
        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            volume_id=volume_id,
            status=SnapshotStatus.PENDING,
            start_time=datetime.utcnow(),
            progress="0%",
            owner_id=self.get_owner_id(),
            volume_size=volume.size if hasattr(volume, "size") else None,
            description=description,
            tag_set=tags,
            encrypted=volume.encrypted if hasattr(volume, "encrypted") else False,
            kms_key_id=volume.kms_key_id if hasattr(volume, "kms_key_id") else None,
            storage_tier=SnapshotStorageTier.STANDARD,
            transfer_type=None,
            completion_time=None,
            full_snapshot_size_in_bytes=None,
            outpost_arn=params.get("OutpostArn"),
            owner_alias=None,
            restore_expiry_time=None,
            sse_type=None,
            status_message=None,
        )

        # Save snapshot in state
        self.state.snapshots[snapshot_id] = snapshot
        self.state.resources[snapshot_id] = snapshot

        return {
            "requestId": self.generate_request_id(),
            "snapshotId": snapshot_id,
            "volumeId": volume_id,
            "status": snapshot.status,
            "startTime": snapshot.start_time,
            "progress": snapshot.progress,
            "ownerId": snapshot.owner_id,
            "volumeSize": snapshot.volume_size,
            "description": snapshot.description,
        }


    def create_snapshots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from datetime import datetime

        instance_spec = params.get("InstanceSpecification")
        if not instance_spec:
            raise ValueError("InstanceSpecification is required")

        instance_id = instance_spec.get("InstanceId")
        if not instance_id:
            raise ValueError("InstanceId in InstanceSpecification is required")

        exclude_boot_volume = instance_spec.get("ExcludeBootVolume", False)
        exclude_data_volume_ids = instance_spec.get("ExcludeDataVolumeIds", [])

        # Validate instance exists
        instance = self.state.get_resource(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        # Get volumes attached to instance
        attached_volumes = []
        if hasattr(instance, "block_device_mappings"):
            for bdm in instance.block_device_mappings:
                vol_id = bdm.get("Ebs", {}).get("VolumeId")
                if vol_id:
                    attached_volumes.append(vol_id)

        # Determine volumes to snapshot
        volumes_to_snapshot = []
        for vol_id in attached_volumes:
            if exclude_boot_volume and vol_id == getattr(instance, "root_device_volume_id", None):
                continue
            if vol_id in exclude_data_volume_ids:
                continue
            volumes_to_snapshot.append(vol_id)

        # Description for all snapshots
        description = params.get("Description")

        # Tags from TagSpecification
        tag_specifications = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") == "snapshot":
                for tag in tag_spec.get("Tags", []):
                    key = tag.get("Key")
                    value = tag.get("Value")
                    if key is not None and value is not None:
                        tags.append(Tag(key=key, value=value))

        # CopyTagsFromSource
        copy_tags_from_source = params.get("CopyTagsFromSource")

        snapshot_set = []
        for vol_id in volumes_to_snapshot:
            volume = self.state.get_resource(vol_id)
            if not volume:
                continue  # skip missing volumes

            # Create snapshot id
            snapshot_id = self.generate_unique_id(prefix="snap-")

            # Determine tags for this snapshot
            snapshot_tags = []
            if copy_tags_from_source == "volume" and hasattr(volume, "tag_set"):
                snapshot_tags = [Tag(key=tag.key, value=tag.value) for tag in volume.tag_set]
            if tags:
                snapshot_tags.extend(tags)

            # Create snapshot object
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                volume_id=vol_id,
                status=SnapshotStatus.PENDING,
                start_time=datetime.utcnow(),
                progress="0%",
                owner_id=self.get_owner_id(),
                volume_size=volume.size if hasattr(volume, "size") else None,
                description=description,
                tag_set=snapshot_tags,
                encrypted=volume.encrypted if hasattr(volume, "encrypted") else False,
                kms_key_id=volume.kms_key_id if hasattr(volume, "kms_key_id") else None,
                storage_tier=SnapshotStorageTier.STANDARD,
                transfer_type=None,
                completion_time=None,
                full_snapshot_size_in_bytes=None,
                outpost_arn=params.get("OutpostArn"),
                owner_alias=None,
                restore_expiry_time=None,
                sse_type=None,
                status_message=None,
            )

            # Save snapshot in state
            self.state.snapshots[snapshot_id] = snapshot
            self.state.resources[snapshot_id] = snapshot

            # Prepare SnapshotInfo for response
            snapshot_info = SnapshotInfo(
                availability_zone=getattr(volume, "availability_zone", None),
                description=snapshot.description,
                encrypted=snapshot.encrypted,
                outpost_arn=snapshot.outpost_arn,
                owner_id=snapshot.owner_id,
                progress=snapshot.progress,
                snapshot_id=snapshot.snapshot_id,
                sse_type=snapshot.sse_type,
                start_time=snapshot.start_time,
                state=snapshot.status,
                tag_set=snapshot.tag_set,
                volume_id=snapshot.volume_id,
                volume_size=snapshot.volume_size,
            )
            snapshot_set.append(snapshot_info)

        return {
            "requestId": self.generate_request_id(),
            "snapshotSet": [snap.to_dict() for snap in snapshot_set],
        }


    def describe_locked_snapshots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = params.get("Filter.N", [])
        snapshot_ids = params.get("SnapshotId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Filter snapshots by snapshot_ids if provided
        locked_snapshots = []
        for snap_id, locked_info in self.state.locked_snapshots.items():
            if snapshot_ids and snap_id not in snapshot_ids:
                continue

            # Apply filters
            match = True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name == "lock-state":
                    if locked_info.lock_state is None or locked_info.lock_state.value not in values:
                        match = False
                        break
            if match:
                locked_snapshots.append(locked_info)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(int(max_results), 1000))

        end_index = start_index + max_results
        page_snapshots = locked_snapshots[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(locked_snapshots) else None

        return {
            "requestId": self.generate_request_id(),
            "snapshotSet": [snap.to_dict() for snap in page_snapshots],
            "nextToken": new_next_token,
        }


    def delete_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("SnapshotId")
        if not snapshot_id:
            raise ValueError("SnapshotId is required")

        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Check if snapshot is used by any registered AMI root device
        for ami in self.state.amis.values():
            if getattr(ami, "root_snapshot_id", None) == snapshot_id:
                raise ValueError("Cannot delete snapshot used by registered AMI")

        # Delete snapshot from state
        self.state.snapshots.pop(snapshot_id, None)
        self.state.resources.pop(snapshot_id, None)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_snapshot_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attribute = params.get("Attribute")
        snapshot_id = params.get("SnapshotId")
        dry_run = params.get("DryRun", False)

        if not attribute or attribute not in ("productCodes", "createVolumePermission"):
            raise ValueError("Invalid or missing Attribute parameter. Valid values: productCodes, createVolumePermission")
        if not snapshot_id:
            raise ValueError("Missing required parameter SnapshotId")

        # DryRun check (stub, no real permission check)
        if dry_run:
            # In real AWS, would check permissions and raise DryRunOperation or UnauthorizedOperation
            return {"Error": "DryRunOperation"}

        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        response = {
            "requestId": self.generate_request_id(),
            "snapshotId": snapshot_id,
        }

        if attribute == "createVolumePermission":
            # Return the create volume permissions for the snapshot
            # We assume snapshot has attribute create_volume_permissions: List[CreateVolumePermission]
            # If not present, return empty list
            create_volume_permissions = getattr(snapshot, "create_volume_permissions", [])
            response["createVolumePermission"] = [perm.to_dict() for perm in create_volume_permissions]
        elif attribute == "productCodes":
            # Return product codes associated with the snapshot
            # We assume snapshot has attribute product_codes: List[ProductCode]
            product_codes = getattr(snapshot, "product_codes", [])
            response["productCodes"] = [pc.to_dict() for pc in product_codes]

        return response


    def describe_snapshots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = []
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        owners = []
        restorable_by = []
        snapshot_ids = []

        # Parse filters
        # Filters are passed as Filter.N.Name and Filter.N.Value.M
        # Collect filters from params keys
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                # key format: Filter.N.Name or Filter.N.Value.M
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    if filter_index not in filter_dict:
                        filter_dict[filter_index] = {"Name": None, "Values": []}
                    if filter_key == "Name":
                        filter_dict[filter_index]["Name"] = value
                    elif filter_key == "Value" or filter_key == "Value.1":
                        # Value or Value.1 means first value
                        filter_dict[filter_index]["Values"].append(value)
                    elif filter_key.startswith("Value"):
                        # Value.M
                        filter_dict[filter_index]["Values"].append(value)
        filters = [Filter(name=f["Name"], values=f["Values"]) for f in filter_dict.values() if f["Name"]]

        # Parse Owner.N, RestorableBy.N, SnapshotId.N
        for key, value in params.items():
            if key.startswith("Owner."):
                owners.append(value)
            elif key.startswith("RestorableBy."):
                restorable_by.append(value)
            elif key.startswith("SnapshotId."):
                snapshot_ids.append(value)

        # DryRun check (stub)
        if dry_run:
            return {"Error": "DryRunOperation"}

        # Collect snapshots to consider
        snapshots = list(self.state.snapshots.values())

        # Filter by snapshot_ids if provided
        if snapshot_ids:
            snapshots = [snap for snap in snapshots if snap.snapshot_id in snapshot_ids]

        # Filter by owners if provided
        if owners:
            def owner_match(snap):
                for owner in owners:
                    if owner == "self":
                        if snap.owner_id == self.get_owner_id():
                            return True
                    elif owner == "amazon":
                        if getattr(snap, "owner_alias", None) == "amazon":
                            return True
                    else:
                        if snap.owner_id == owner:
                            return True
                return False
            snapshots = [snap for snap in snapshots if owner_match(snap)]

        # Filter by restorable_by if provided
        if restorable_by:
            # We assume snapshot has attribute create_volume_permissions: List[CreateVolumePermission]
            def restorable_match(snap):
                perms = getattr(snap, "create_volume_permissions", [])
                for account_id in restorable_by:
                    for perm in perms:
                        if perm.user_id == account_id or perm.group == "all":
                            return True
                return False
            snapshots = [snap for snap in snapshots if restorable_match(snap)]

        # Apply filters
        def matches_filter(snap: Snapshot, filter: Filter) -> bool:
            name = filter.name
            values = filter.values
            if name == "description":
                return any(snap.description and v == snap.description for v in values)
            elif name == "encrypted":
                # values are strings "true" or "false"
                return any((v.lower() == "true" and snap.encrypted) or (v.lower() == "false" and not snap.encrypted) for v in values)
            elif name == "owner-alias":
                return any(getattr(snap, "owner_alias", None) == v for v in values)
            elif name == "owner-id":
                return any(snap.owner_id == v for v in values)
            elif name == "progress":
                return any(snap.progress == v for v in values)
            elif name == "snapshot-id":
                return any(snap.snapshot_id == v for v in values)
            elif name == "start-time":
                # values are timestamps, compare string ISO format
                return any(snap.start_time and snap.start_time.isoformat() == v for v in values)
            elif name == "status":
                # values like "pending", "completed", "error"
                return any(snap.status.name.lower() == v.lower() for v in values)
            elif name == "storage-tier":
                return any(snap.storage_tier.name.lower() == v.lower() for v in values)
            elif name == "transfer-type":
                if snap.transfer_type is None:
                    return False
                return any(snap.transfer_type.name.lower() == v.lower() for v in values)
            elif name.startswith("tag:"):
                tag_key = name[4:]
                # Check if snapshot has tag with key=tag_key and value in values
                for tag in snap.tag_set:
                    if tag.key == tag_key and tag.value in values:
                        return True
                return False
            elif name == "tag-key":
                # Check if snapshot has tag with key in values
                for tag in snap.tag_set:
                    if tag.key in values:
                        return True
                return False
            elif name == "volume-id":
                return any(snap.volume_id == v for v in values)
            elif name == "volume-size":
                # values are strings, convert to int
                try:
                    int_values = [int(v) for v in values]
                except Exception:
                    return False
                return any(snap.volume_size == iv for iv in int_values)
            else:
                # Unknown filter, ignore
                return True

        for f in filters:
            snapshots = [snap for snap in snapshots if matches_filter(snap, f)]

        # Pagination
        # next_token is a string token representing the index offset
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # max_results default to 1000 if not specified (AWS default)
        max_results = int(max_results) if max_results else 1000

        end_index = start_index + max_results
        paged_snapshots = snapshots[start_index:end_index]

        # Prepare response snapshotSet
        snapshot_set = []
        for snap in paged_snapshots:
            snap_dict = {
                "snapshotId": snap.snapshot_id,
                "volumeId": snap.volume_id,
                "status": snap.status.name.lower() if snap.status else None,
                "startTime": snap.start_time.isoformat() if snap.start_time else None,
                "progress": snap.progress,
                "ownerId": snap.owner_id,
                "volumeSize": snap.volume_size,
                "description": snap.description,
                "tagSet": [{"Key": tag.key, "Value": tag.value} for tag in snap.tag_set],
                "encrypted": snap.encrypted,
                "kmsKeyId": snap.kms_key_id,
                "storageTier": snap.storage_tier.name.lower() if snap.storage_tier else None,
                "transferType": snap.transfer_type.name.lower() if snap.transfer_type else None,
                "completionTime": snap.completion_time.isoformat() if snap.completion_time else None,
                "fullSnapshotSizeInBytes": snap.full_snapshot_size_in_bytes,
                "outpostArn": snap.outpost_arn,
                "ownerAlias": snap.owner_alias,
                "restoreExpiryTime": snap.restore_expiry_time.isoformat() if snap.restore_expiry_time else None,
                "sseType": snap.sse_type.name if snap.sse_type else None,
                "statusMessage": snap.status_message,
            }
            # Remove keys with None values
            snap_dict = {k: v for k, v in snap_dict.items() if v is not None}
            snapshot_set.append(snap_dict)

        response = {
            "requestId": self.generate_request_id(),
            "snapshotSet": snapshot_set,
            "nextToken": str(end_index) if end_index < len(snapshots) else None,
        }
        return response


    def describe_snapshot_tier_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = []
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Parse filters
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    if filter_index not in filter_dict:
                        filter_dict[filter_index] = {"Name": None, "Values": []}
                    if filter_key == "Name":
                        filter_dict[filter_index]["Name"] = value
                    elif filter_key == "Value" or filter_key == "Value.1":
                        filter_dict[filter_index]["Values"].append(value)
                    elif filter_key.startswith("Value"):
                        filter_dict[filter_index]["Values"].append(value)
        filters = [Filter(name=f["Name"], values=f["Values"]) for f in filter_dict.values() if f["Name"]]

        # DryRun check (stub)
        if dry_run:
            return {"Error": "DryRunOperation"}

        # Collect snapshot tier status objects
        # We assume self.state.snapshots contains Snapshot objects with tier status info
        # We will create SnapshotTierStatus objects from snapshots that have tier status info
        tier_status_list = []
        for snap in self.state.snapshots.values():
            # We consider only snapshots that have storage_tier attribute set
            if not snap.storage_tier:
                continue
            tier_status = SnapshotTierStatus(
                archival_complete_time=getattr(snap, "archival_complete_time", None),
                last_tiering_operation_status=getattr(snap, "last_tiering_operation_status", None),
                last_tiering_operation_status_detail=getattr(snap, "last_tiering_operation_status_detail", None),
                last_tiering_progress=getattr(snap, "last_tiering_progress", None),
                last_tiering_start_time=getattr(snap, "last_tiering_start_time", None),
                owner_id=snap.owner_id,
                restore_expiry_time=snap.restore_expiry_time,
                snapshot_id=snap.snapshot_id,
                status=snap.status,
                storage_tier=snap.storage_tier,
                tag_set=snap.tag_set,
                volume_id=snap.volume_id,
            )
            tier_status_list.append(tier_status)

        # Apply filters
        def matches_filter(tier: SnapshotTierStatus, filter: Filter) -> bool:
            name = filter.name
            values = filter.values
            if name == "snapshot-id":
                return any(tier.snapshot_id == v for v in values)
            elif name == "volume-id":
                return any(tier.volume_id == v for v in values)
            elif name == "last-tiering-operation":
                # Compare last_tiering_operation_status string values
                if tier.last_tiering_operation_status is None:
                    return False
                return any(tier.last_tiering_operation_status.name.lower() == v.lower() for v in values)
            else:
                # Unknown filter, ignore
                return True

        for f in filters:
            tier_status_list = [t for t in tier_status_list if matches_filter(t, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results = int(max_results) if max_results else 1000
        end_index = start_index + max_results
        paged_tiers = tier_status_list[start_index:end_index]

        # Prepare response snapshotTierStatusSet
        tier_status_set = []
        for tier in paged_tiers:
            tier_dict = {
                "archivalCompleteTime": tier.archival_complete_time.isoformat() if tier.archival_complete_time else None,
                "lastTieringOperationStatus": tier.last_tiering_operation_status.name if tier.last_tiering_operation_status else None,
                "lastTieringOperationStatusDetail": tier.last_tiering_operation_status_detail,
                "lastTieringProgress": tier.last_tiering_progress,
                "lastTieringStartTime": tier.last_tiering_start_time.isoformat() if tier.last_tiering_start_time else None,
                "ownerId": tier.owner_id,
                "restoreExpiryTime": tier.restore_expiry_time.isoformat() if tier.restore_expiry_time else None,
                "snapshotId": tier.snapshot_id,
                "status": tier.status.name.lower() if tier.status else None,
                "storageTier": tier.storage_tier.name.lower() if tier.storage_tier else None,
                "tagSet": [{"Key": tag.key, "Value": tag.value} for tag in tier.tag_set],
                "volumeId": tier.volume_id,
            }
            tier_dict = {k: v for k, v in tier_dict.items() if v is not None}
            tier_status_set.append(tier_dict)

        response = {
            "requestId": self.generate_request_id(),
            "snapshotTierStatusSet": tier_status_set,
            "nextToken": str(end_index) if end_index < len(tier_status_list) else None,
        }
        return response


    def disable_snapshot_block_public_access(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)

        # DryRun check (stub)
        if dry_run:
            return {"Error": "DryRunOperation"}

        # We assume self.state has attribute snapshot_block_public_access_state per region
        # For simplicity, assume single region and store state in self.state.snapshot_block_public_access_state
        # Disable block public access means set state to "unblocked"
        self.state.snapshot_block_public_access_state = "unblocked"

        response = {
            "requestId": self.generate_request_id(),
            "state": "unblocked",
        }
        return response


    def enable_snapshot_block_public_access(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        state = params.get("State")

        if not state or state not in ("block-all-sharing", "block-new-sharing"):
            raise ValueError("Invalid or missing State parameter. Valid values: block-all-sharing, block-new-sharing")

        # DryRun check (stub)
        if dry_run:
            return {"Error": "DryRunOperation"}

        # Set the block public access state in self.state
        self.state.snapshot_block_public_access_state = state

        response = {
            "requestId": self.generate_request_id(),
            "state": state,
        }
        return response

    def get_snapshot_block_public_access_state(self, params: dict) -> dict:
        # DryRun parameter check
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For simplicity, assume permission is always granted in this emulator
            # Raise DryRunOperation error if permission granted
            # Here we just return the DryRunOperation error response format
            # In real AWS, this would be an error response, but here we simulate success
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id(),
            }

        # For this emulator, assume the state is managed by the account and unblocked
        managed_by = "account"
        state = "unblocked"

        return {
            "managedBy": managed_by,
            "state": state,
            "requestId": self.generate_request_id(),
        }


    def lock_snapshot(self, params: dict) -> dict:
        from datetime import datetime, timedelta, timezone

        snapshot_id = params.get("SnapshotId")
        if not snapshot_id:
            raise Exception("Missing required parameter SnapshotId")

        lock_mode = params.get("LockMode")
        if lock_mode not in ("compliance", "governance"):
            raise Exception("Invalid LockMode. Valid values: compliance | governance")

        cool_off_period = params.get("CoolOffPeriod")
        expiration_date = params.get("ExpirationDate")
        lock_duration = params.get("LockDuration")

        # Validate CoolOffPeriod if provided
        if cool_off_period is not None:
            if not isinstance(cool_off_period, int):
                raise Exception("CoolOffPeriod must be an integer")
            if cool_off_period < 1 or cool_off_period > 72:
                raise Exception("CoolOffPeriod must be between 1 and 72")

        # Validate LockDuration if provided
        if lock_duration is not None:
            if not isinstance(lock_duration, int):
                raise Exception("LockDuration must be an integer")
            if lock_duration < 1 or lock_duration > 36500:
                raise Exception("LockDuration must be between 1 and 36500")

        # Must specify either ExpirationDate or LockDuration, but not both
        if expiration_date and lock_duration:
            raise Exception("Specify either ExpirationDate or LockDuration, but not both")
        if not expiration_date and not lock_duration:
            # If neither specified, default LockDuration to 1 day
            lock_duration = 1

        # DryRun check
        dry_run = params.get("DryRun", False)
        if dry_run:
            # Assume permission granted
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id(),
            }

        # Retrieve snapshot from state
        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise Exception(f"Snapshot {snapshot_id} not found")

        now = datetime.now(timezone.utc)

        # Determine lockCreatedOn time
        lock_created_on = now

        # Determine lockDurationStartTime
        lock_duration_start_time = now

        # Determine lockExpiresOn
        if expiration_date:
            # Parse expiration_date string to datetime
            try:
                # AWS format: YYYY-MM-DDThh:mm:ss.sssZ (ISO8601 UTC)
                # Remove trailing Z and parse
                if expiration_date.endswith("Z"):
                    expiration_date = expiration_date[:-1]
                lock_expires_on = datetime.fromisoformat(expiration_date).replace(tzinfo=timezone.utc)
            except Exception:
                raise Exception("Invalid ExpirationDate format")
            # Calculate lockDuration from expiration date
            delta = lock_expires_on - now
            lock_duration_days = max(1, delta.days)
        else:
            # Use lock_duration in days
            lock_duration_days = lock_duration
            lock_expires_on = now + timedelta(days=lock_duration_days)

        # Determine coolOffPeriodExpiresOn if compliance mode and cool_off_period specified
        if lock_mode == "compliance":
            if cool_off_period is not None:
                cool_off_period_expires_on = lock_created_on + timedelta(hours=cool_off_period)
            else:
                # If no cool_off_period specified, cooling off period is zero (immediate compliance lock)
                cool_off_period = 0
                cool_off_period_expires_on = lock_created_on
        else:
            # Governance mode: no cool off period
            cool_off_period = None
            cool_off_period_expires_on = None

        # Determine lockState
        # Possible states: compliance-cooloff, governance, compliance, expired
        # For new lock, state depends on mode and cool off period
        if lock_mode == "governance":
            lock_state = "governance"
        elif lock_mode == "compliance":
            if cool_off_period and cool_off_period > 0:
                lock_state = "compliance-cooloff"
            else:
                lock_state = "compliance"
        else:
            lock_state = None  # Should not happen due to validation

        # Save lock info in snapshot's locked_snapshots_info attribute
        locked_info = LockedSnapshotsInfo(
            cool_off_period=cool_off_period,
            cool_off_period_expires_on=cool_off_period_expires_on,
            lock_created_on=lock_created_on,
            lock_duration=lock_duration_days,
            lock_duration_start_time=lock_duration_start_time,
            lock_expires_on=lock_expires_on,
            lock_state=lock_state,
            owner_id=snapshot.owner_id,
            snapshot_id=snapshot_id,
        )
        # Store locked info in snapshot object (add attribute if not present)
        snapshot.locked_snapshots_info = locked_info

        return {
            "coolOffPeriod": cool_off_period,
            "coolOffPeriodExpiresOn": cool_off_period_expires_on,
            "lockCreatedOn": lock_created_on,
            "lockDuration": lock_duration_days,
            "lockDurationStartTime": lock_duration_start_time,
            "lockExpiresOn": lock_expires_on,
            "lockState": lock_state,
            "snapshotId": snapshot_id,
            "requestId": self.generate_request_id(),
        }


    def modify_snapshot_attribute(self, params: dict) -> dict:
        snapshot_id = params.get("SnapshotId")
        if not snapshot_id:
            raise Exception("Missing required parameter SnapshotId")

        attribute = params.get("Attribute")
        create_volume_permission_modifications = params.get("CreateVolumePermission")
        operation_type = params.get("OperationType")
        dry_run = params.get("DryRun", False)

        # Also support UserGroup.N and UserId.N parameters for backward compatibility
        # They are lists of strings
        user_groups = []
        user_ids = []
        for key, value in params.items():
            if key.startswith("UserGroup."):
                user_groups.append(value)
            elif key.startswith("UserId."):
                user_ids.append(value)

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id(),
            }

        # Retrieve snapshot
        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise Exception(f"Snapshot {snapshot_id} not found")

        # Only attribute supported is createVolumePermission
        if attribute and attribute != "createVolumePermission":
            raise Exception("Only createVolumePermission attribute can be modified")

        # Initialize snapshot permissions if not present
        if not hasattr(snapshot, "create_volume_permissions"):
            # Store as list of CreateVolumePermission objects
            snapshot.create_volume_permissions = []

        # Helper to parse CreateVolumePermission objects from dicts
        def parse_create_volume_permission_list(lst):
            result = []
            if not lst:
                return result
            for item in lst:
                group = item.get("Group")
                user_id = item.get("UserId")
                if group is None and user_id is None:
                    continue
                perm = CreateVolumePermission(group=group, user_id=user_id)
                result.append(perm)
            return result

        # Parse Add and Remove lists if present
        add_list = []
        remove_list = []
        if create_volume_permission_modifications:
            add_list = parse_create_volume_permission_list(create_volume_permission_modifications.get("Add"))
            remove_list = parse_create_volume_permission_list(create_volume_permission_modifications.get("Remove"))

        # Also add UserGroup.N and UserId.N to add_list if operation_type is add
        if operation_type == "add":
            for group in user_groups:
                add_list.append(CreateVolumePermission(group=group, user_id=None))
            for user_id in user_ids:
                add_list.append(CreateVolumePermission(group=None, user_id=user_id))
        elif operation_type == "remove":
            for group in user_groups:
                remove_list.append(CreateVolumePermission(group=group, user_id=None))
            for user_id in user_ids:
                remove_list.append(CreateVolumePermission(group=None, user_id=user_id))

        # Cannot add and remove in same request
        if add_list and remove_list:
            raise Exception("Cannot add and remove permissions in the same request")

        # Modify permissions accordingly
        current_perms = snapshot.create_volume_permissions

        def perm_equal(p1, p2):
            return p1.group == p2.group and p1.user_id == p2.user_id

        if add_list:
            # Add permissions if not already present
            for perm_to_add in add_list:
                if not any(perm_equal(perm_to_add, existing) for existing in current_perms):
                    current_perms.append(perm_to_add)
        elif remove_list:
            # Remove permissions if present
            new_perms = []
            for existing in current_perms:
                if not any(perm_equal(existing, perm_to_remove) for perm_to_remove in remove_list):
                    new_perms.append(existing)
            snapshot.create_volume_permissions = new_perms

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def modify_snapshot_tier(self, params: dict) -> dict:
        from datetime import datetime, timezone

        snapshot_id = params.get("SnapshotId")
        if not snapshot_id:
            raise Exception("Missing required parameter SnapshotId")

        storage_tier = params.get("StorageTier")
        dry_run = params.get("DryRun", False)

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id(),
            }

        # Validate StorageTier if provided
        if storage_tier and storage_tier != "archive":
            raise Exception("StorageTier must be 'archive' if specified")

        # Retrieve snapshot
        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise Exception(f"Snapshot {snapshot_id} not found")

        # For this emulator, only support archiving snapshot to archive tier
        # Update snapshot storage_tier and record tiering start time
        from datetime import datetime

        tiering_start_time = datetime.now(timezone.utc)

        # Update snapshot storage tier enum member if possible
        # Assuming SnapshotStorageTier has member ARCHIVE
        # If not, fallback to string "archive"
        try:
            storage_tier_enum = SnapshotStorageTier.ARCHIVE
        except Exception:
            storage_tier_enum = "archive"

        snapshot.storage_tier = storage_tier_enum

        # Save tiering start time in snapshot attribute
        snapshot.tiering_start_time = tiering_start_time

        return {
            "requestId": self.generate_request_id(),
            "snapshotId": snapshot_id,
            "tieringStartTime": tiering_start_time,
        }


    def reset_snapshot_attribute(self, params: dict) -> dict:
        snapshot_id = params.get("SnapshotId")
        attribute = params.get("Attribute")
        dry_run = params.get("DryRun", False)

        if not snapshot_id:
            raise Exception("Missing required parameter SnapshotId")
        if not attribute:
            raise Exception("Missing required parameter Attribute")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id(),
            }

        # Retrieve snapshot
        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise Exception(f"Snapshot {snapshot_id} not found")

        # Only attribute supported is createVolumePermission
        if attribute != "createVolumePermission":
            raise Exception("Only createVolumePermission attribute can be reset")

        # Reset create volume permissions to empty list
        snapshot.create_volume_permissions = []

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def restore_snapshot_tier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("SnapshotId")
        if not snapshot_id:
            raise ValueError("SnapshotId is required")
        permanent_restore = params.get("PermanentRestore", False)
        temporary_restore_days = params.get("TemporaryRestoreDays")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # Simulate permission check
            # In real implementation, would check permissions and raise error if unauthorized
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Validate parameters according to AWS rules:
        # If PermanentRestore is True, TemporaryRestoreDays must be omitted
        if permanent_restore and temporary_restore_days is not None:
            raise ValueError("TemporaryRestoreDays must be omitted when PermanentRestore is true")
        # If PermanentRestore is False or omitted, TemporaryRestoreDays must be specified and > 0
        if not permanent_restore:
            if temporary_restore_days is None:
                raise ValueError("TemporaryRestoreDays is required for temporary restore")
            if not isinstance(temporary_restore_days, int) or temporary_restore_days <= 0:
                raise ValueError("TemporaryRestoreDays must be a positive integer")

        # Update snapshot restore state
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        if permanent_restore:
            snapshot.restore_expiry_time = None
        else:
            snapshot.restore_expiry_time = now + timedelta(days=temporary_restore_days)

        snapshot.status = SnapshotStatus.restoring if snapshot.status != SnapshotStatus.completed else snapshot.status
        snapshot.start_time = now

        # Compose response
        response = {
            "snapshotId": snapshot_id,
            "isPermanentRestore": permanent_restore,
            "restoreStartTime": now,
            "requestId": self.generate_request_id(),
        }
        if not permanent_restore:
            response["restoreDuration"] = temporary_restore_days

        return response


    def unlock_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("SnapshotId")
        if not snapshot_id:
            raise ValueError("SnapshotId is required")
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Check if snapshot is locked
        locked_info = self.state.locked_snapshots.get(snapshot_id)
        if not locked_info:
            # Snapshot is not locked, nothing to do
            pass
        else:
            # Check lock state and cooling off period
            from datetime import datetime

            now = datetime.utcnow()
            if locked_info.lock_state == SnapshotLockState.compliance:
                # If cooling off period expired, cannot unlock
                if locked_info.cool_off_period_expires_on and locked_info.cool_off_period_expires_on <= now:
                    raise ValueError("Cannot unlock snapshot locked in compliance mode after cooling-off period expired")
            # Unlock by removing locked snapshot info
            del self.state.locked_snapshots[snapshot_id]

        return {
            "snapshotId": snapshot_id,
            "requestId": self.generate_request_id(),
        }


    def list_snapshots_in_recycle_bin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        snapshot_ids = params.get("SnapshotId.N", [])

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Filter snapshots in recycle bin
        recycle_bin_snapshots = [
            snap for snap in self.state.recycle_bin_snapshots.values()
            if (not snapshot_ids or snap.snapshot_id in snapshot_ids)
        ]

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ValueError("Invalid NextToken")

        end_index = start_index + max_results if max_results else len(recycle_bin_snapshots)
        page_snapshots = recycle_bin_snapshots[start_index:end_index]

        # Prepare snapshotSet response
        snapshot_set = []
        for snap in page_snapshots:
            snapshot_set.append({
                "description": snap.description,
                "recycleBinEnterTime": snap.recycle_bin_enter_time,
                "recycleBinExitTime": snap.recycle_bin_exit_time,
                "snapshotId": snap.snapshot_id,
                "volumeId": snap.volume_id,
            })

        # Determine next token
        new_next_token = str(end_index) if end_index < len(recycle_bin_snapshots) else None

        return {
            "snapshotSet": snapshot_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def restore_snapshot_from_recycle_bin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        snapshot_id = params.get("SnapshotId")
        if not snapshot_id:
            raise ValueError("SnapshotId is required")
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        recycle_bin_snapshot = self.state.recycle_bin_snapshots.get(snapshot_id)
        if not recycle_bin_snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found in Recycle Bin")

        # Remove from recycle bin
        del self.state.recycle_bin_snapshots[snapshot_id]

        # Add snapshot back to snapshots if not present
        snapshot = self.state.snapshots.get(snapshot_id)
        if not snapshot:
            # Create a new Snapshot object from recycle_bin_snapshot info
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                volume_id=recycle_bin_snapshot.volume_id,
                status=SnapshotStatus.completed,
                start_time=recycle_bin_snapshot.recycle_bin_enter_time,
                progress="100%",
                owner_id=self.get_owner_id(),
                volume_size=None,
                description=recycle_bin_snapshot.description,
                tag_set=[],
                encrypted=None,
                kms_key_id=None,
                storage_tier=SnapshotStorageTier.standard,
                transfer_type=None,
                completion_time=None,
                full_snapshot_size_in_bytes=None,
                outpost_arn=recycle_bin_snapshot.outpost_arn if hasattr(recycle_bin_snapshot, "outpost_arn") else None,
                owner_alias=None,
                restore_expiry_time=None,
                sse_type=None,
                status_message=None,
            )
            self.state.snapshots[snapshot_id] = snapshot

        # Compose response
        response = {
            "snapshotId": snapshot.snapshot_id,
            "description": snapshot.description,
            "encrypted": snapshot.encrypted,
            "outpostArn": snapshot.outpost_arn,
            "ownerId": snapshot.owner_id,
            "progress": snapshot.progress,
            "requestId": self.generate_request_id(),
            "sseType": snapshot.sse_type.name if snapshot.sse_type else None,
            "startTime": snapshot.start_time,
            "status": snapshot.status.name if snapshot.status else None,
            "volumeId": snapshot.volume_id,
            "volumeSize": snapshot.volume_size,
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class SnapshotsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CopySnapshot", self.copy_snapshot)
        self.register_action("CreateSnapshot", self.create_snapshot)
        self.register_action("CreateSnapshots", self.create_snapshots)
        self.register_action("DescribeLockedSnapshots", self.describe_locked_snapshots)
        self.register_action("DeleteSnapshot", self.delete_snapshot)
        self.register_action("DescribeSnapshotAttribute", self.describe_snapshot_attribute)
        self.register_action("DescribeSnapshots", self.describe_snapshots)
        self.register_action("DescribeSnapshotTierStatus", self.describe_snapshot_tier_status)
        self.register_action("DisableSnapshotBlockPublicAccess", self.disable_snapshot_block_public_access)
        self.register_action("EnableSnapshotBlockPublicAccess", self.enable_snapshot_block_public_access)
        self.register_action("GetSnapshotBlockPublicAccessState", self.get_snapshot_block_public_access_state)
        self.register_action("LockSnapshot", self.lock_snapshot)
        self.register_action("ModifySnapshotAttribute", self.modify_snapshot_attribute)
        self.register_action("ModifySnapshotTier", self.modify_snapshot_tier)
        self.register_action("ResetSnapshotAttribute", self.reset_snapshot_attribute)
        self.register_action("RestoreSnapshotTier", self.restore_snapshot_tier)
        self.register_action("UnlockSnapshot", self.unlock_snapshot)
        self.register_action("ListSnapshotsInRecycleBin", self.list_snapshots_in_recycle_bin)
        self.register_action("RestoreSnapshotFromRecycleBin", self.restore_snapshot_from_recycle_bin)

    def copy_snapshot(self, params):
        return self.backend.copy_snapshot(params)

    def create_snapshot(self, params):
        return self.backend.create_snapshot(params)

    def create_snapshots(self, params):
        return self.backend.create_snapshots(params)

    def describe_locked_snapshots(self, params):
        return self.backend.describe_locked_snapshots(params)

    def delete_snapshot(self, params):
        return self.backend.delete_snapshot(params)

    def describe_snapshot_attribute(self, params):
        return self.backend.describe_snapshot_attribute(params)

    def describe_snapshots(self, params):
        return self.backend.describe_snapshots(params)

    def describe_snapshot_tier_status(self, params):
        return self.backend.describe_snapshot_tier_status(params)

    def disable_snapshot_block_public_access(self, params):
        return self.backend.disable_snapshot_block_public_access(params)

    def enable_snapshot_block_public_access(self, params):
        return self.backend.enable_snapshot_block_public_access(params)

    def get_snapshot_block_public_access_state(self, params):
        return self.backend.get_snapshot_block_public_access_state(params)

    def lock_snapshot(self, params):
        return self.backend.lock_snapshot(params)

    def modify_snapshot_attribute(self, params):
        return self.backend.modify_snapshot_attribute(params)

    def modify_snapshot_tier(self, params):
        return self.backend.modify_snapshot_tier(params)

    def reset_snapshot_attribute(self, params):
        return self.backend.reset_snapshot_attribute(params)

    def restore_snapshot_tier(self, params):
        return self.backend.restore_snapshot_tier(params)

    def unlock_snapshot(self, params):
        return self.backend.unlock_snapshot(params)

    def list_snapshots_in_recycle_bin(self, params):
        return self.backend.list_snapshots_in_recycle_bin(params)

    def restore_snapshot_from_recycle_bin(self, params):
        return self.backend.restore_snapshot_from_recycle_bin(params)
