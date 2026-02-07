from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class VolumeAttachmentState(str, Enum):
    ATTACHING = "attaching"
    ATTACHED = "attached"
    DETACHING = "detaching"
    DETACHED = "detached"
    BUSY = "busy"


class VolumeState(str, Enum):
    CREATING = "creating"
    AVAILABLE = "available"
    IN_USE = "in-use"
    DELETING = "deleting"
    DELETED = "deleted"
    ERROR = "error"


class VolumeModificationState(str, Enum):
    MODIFYING = "modifying"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReplaceRootVolumeTaskState(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    FAILING = "failing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    FAILING_DETACHED = "failing-detached"
    FAILED_DETACHED = "failed-detached"


class VolumeStatusStatus(str, Enum):
    OK = "ok"
    IMPAIRED = "impaired"
    INSUFFICIENT_DATA = "insufficient-data"
    WARNING = "warning"


class VolumeStatusDetailName(str, Enum):
    IO_ENABLED = "io-enabled"
    IO_PERFORMANCE = "io-performance"
    INITIALIZATION_STATE = "initialization-state"


class VolumeStatusDetailInitializationType(str, Enum):
    DEFAULT = "default"
    PROVISIONED_RATE = "provisioned-rate"
    VOLUME_COPY = "volume-copy"


class SseType(str, Enum):
    SSE_EBS = "sse-ebs"
    SSE_KMS = "sse-kms"
    NONE = "none"


class VolumeType(str, Enum):
    STANDARD = "standard"
    IO1 = "io1"
    IO2 = "io2"
    GP2 = "gp2"
    SC1 = "sc1"
    ST1 = "st1"
    GP3 = "gp3"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class OperatorRequest:
    Principal: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Principal": self.Principal}


@dataclass
class OperatorResponse:
    managed: Optional[bool] = None
    principal: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "managed": self.managed,
            "principal": self.principal,
        }


@dataclass
class VolumeAttachment:
    associatedResource: Optional[str] = None
    attachTime: Optional[datetime] = None
    deleteOnTermination: Optional[bool] = None
    device: Optional[str] = None
    instanceId: Optional[str] = None
    instanceOwningService: Optional[str] = None
    status: Optional[VolumeAttachmentState] = None
    volumeId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "associatedResource": self.associatedResource,
            "attachTime": self.attachTime.isoformat() if self.attachTime else None,
            "deleteOnTermination": self.deleteOnTermination,
            "device": self.device,
            "instanceId": self.instanceId,
            "instanceOwningService": self.instanceOwningService,
            "status": self.status.value if self.status else None,
            "volumeId": self.volumeId,
        }


@dataclass
class Volume:
    volumeId: str
    size: Optional[int] = None  # GiB
    snapshotId: Optional[str] = None
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    status: Optional[VolumeState] = None
    createTime: Optional[datetime] = None
    encrypted: Optional[bool] = None
    fastRestored: Optional[bool] = None
    iops: Optional[int] = None
    kmsKeyId: Optional[str] = None
    multiAttachEnabled: Optional[bool] = None
    operator: Optional[OperatorResponse] = None
    outpostArn: Optional[str] = None
    sourceVolumeId: Optional[str] = None
    sseType: Optional[SseType] = None
    tagSet: List[Tag] = field(default_factory=list)
    throughput: Optional[int] = None  # MiB/s
    volumeInitializationRate: Optional[int] = None  # MiB/s
    volumeType: Optional[VolumeType] = None
    attachmentSet: List[VolumeAttachment] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "volumeId": self.volumeId,
            "size": self.size,
            "snapshotId": self.snapshotId,
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "status": self.status.value if self.status else None,
            "createTime": self.createTime.isoformat() if self.createTime else None,
            "encrypted": self.encrypted,
            "fastRestored": self.fastRestored,
            "iops": self.iops,
            "kmsKeyId": self.kmsKeyId,
            "multiAttachEnabled": self.multiAttachEnabled,
            "operator": self.operator.to_dict() if self.operator else None,
            "outpostArn": self.outpostArn,
            "sourceVolumeId": self.sourceVolumeId,
            "sseType": self.sseType.value if self.sseType else None,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "throughput": self.throughput,
            "volumeInitializationRate": self.volumeInitializationRate,
            "volumeType": self.volumeType.value if self.volumeType else None,
            "attachmentSet": [att.to_dict() for att in self.attachmentSet],
        }


@dataclass
class ReplaceRootVolumeTask:
    completeTime: Optional[str] = None
    deleteReplacedRootVolume: Optional[bool] = None
    imageId: Optional[str] = None
    instanceId: Optional[str] = None
    replaceRootVolumeTaskId: Optional[str] = None
    snapshotId: Optional[str] = None
    startTime: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    taskState: Optional[ReplaceRootVolumeTaskState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "completeTime": self.completeTime,
            "deleteReplacedRootVolume": self.deleteReplacedRootVolume,
            "imageId": self.imageId,
            "instanceId": self.instanceId,
            "replaceRootVolumeTaskId": self.replaceRootVolumeTaskId,
            "snapshotId": self.snapshotId,
            "startTime": self.startTime,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "taskState": self.taskState.value if self.taskState else None,
        }


@dataclass
class AttributeBooleanValue:
    Value: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class ProductCode:
    productCode: Optional[str] = None
    type: Optional[str] = None  # devpay | marketplace

    def to_dict(self) -> Dict[str, Any]:
        return {
            "productCode": self.productCode,
            "type": self.type,
        }


@dataclass
class VolumeModification:
    endTime: Optional[datetime] = None
    modificationState: Optional[VolumeModificationState] = None
    originalIops: Optional[int] = None
    originalMultiAttachEnabled: Optional[bool] = None
    originalSize: Optional[int] = None
    originalThroughput: Optional[int] = None
    originalVolumeType: Optional[VolumeType] = None
    progress: Optional[int] = None  # 0-100
    startTime: Optional[datetime] = None
    statusMessage: Optional[str] = None
    targetIops: Optional[int] = None
    targetMultiAttachEnabled: Optional[bool] = None
    targetSize: Optional[int] = None
    targetThroughput: Optional[int] = None
    targetVolumeType: Optional[VolumeType] = None
    volumeId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "endTime": self.endTime.isoformat() if self.endTime else None,
            "modificationState": self.modificationState.value if self.modificationState else None,
            "originalIops": self.originalIops,
            "originalMultiAttachEnabled": self.originalMultiAttachEnabled,
            "originalSize": self.originalSize,
            "originalThroughput": self.originalThroughput,
            "originalVolumeType": self.originalVolumeType.value if self.originalVolumeType else None,
            "progress": self.progress,
            "startTime": self.startTime.isoformat() if self.startTime else None,
            "statusMessage": self.statusMessage,
            "targetIops": self.targetIops,
            "targetMultiAttachEnabled": self.targetMultiAttachEnabled,
            "targetSize": self.targetSize,
            "targetThroughput": self.targetThroughput,
            "targetVolumeType": self.targetVolumeType.value if self.targetVolumeType else None,
            "volumeId": self.volumeId,
        }


@dataclass
class VolumeStatusDetails:
    name: Optional[VolumeStatusDetailName] = None
    status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name.value if self.name else None,
            "status": self.status,
        }


@dataclass
class VolumeStatusInfo:
    details: List[VolumeStatusDetails] = field(default_factory=list)
    status: Optional[VolumeStatusStatus] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "details": [detail.to_dict() for detail in self.details],
            "status": self.status.value if self.status else None,
        }


@dataclass
class VolumeStatusEvent:
    description: Optional[str] = None
    eventId: Optional[str] = None
    eventType: Optional[str] = None
    instanceId: Optional[str] = None
    notAfter: Optional[datetime] = None
    notBefore: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "eventId": self.eventId,
            "eventType": self.eventType,
            "instanceId": self.instanceId,
            "notAfter": self.notAfter.isoformat() if self.notAfter else None,
            "notBefore": self.notBefore.isoformat() if self.notBefore else None,
        }


@dataclass
class VolumeStatusAction:
    code: Optional[str] = None
    description: Optional[str] = None
    eventId: Optional[str] = None
    eventType: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "description": self.description,
            "eventId": self.eventId,
            "eventType": self.eventType,
        }


@dataclass
class VolumeStatusAttachmentStatus:
    instanceId: Optional[str] = None
    ioPerformance: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instanceId": self.instanceId,
            "ioPerformance": self.ioPerformance,
        }


@dataclass
class InitializationStatusDetails:
    estimatedTimeToCompleteInSeconds: Optional[int] = None
    initializationType: Optional[VolumeStatusDetailInitializationType] = None
    progress: Optional[int] = None  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "estimatedTimeToCompleteInSeconds": self.estimatedTimeToCompleteInSeconds,
            "initializationType": self.initializationType.value if self.initializationType else None,
            "progress": self.progress,
        }


@dataclass
class VolumeStatusItem:
    actionsSet: List[VolumeStatusAction] = field(default_factory=list)
    attachmentStatuses: List[VolumeStatusAttachmentStatus] = field(default_factory=list)
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    eventsSet: List[VolumeStatusEvent] = field(default_factory=list)
    initializationStatusDetails: Optional[InitializationStatusDetails] = None
    outpostArn: Optional[str] = None
    volumeId: Optional[str] = None
    volumeStatus: Optional[VolumeStatusInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actionsSet": [action.to_dict() for action in self.actionsSet],
            "attachmentStatuses": [att.to_dict() for att in self.attachmentStatuses],
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "eventsSet": [event.to_dict() for event in self.eventsSet],
            "initializationStatusDetails": self.initializationStatusDetails.to_dict() if self.initializationStatusDetails else None,
            "outpostArn": self.outpostArn,
            "volumeId": self.volumeId,
            "volumeStatus": self.volumeStatus.to_dict() if self.volumeStatus else None,
        }


@dataclass
class VolumeRecycleBinInfo:
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    createTime: Optional[datetime] = None
    iops: Optional[int] = None
    operator: Optional[OperatorResponse] = None
    outpostArn: Optional[str] = None
    recycleBinEnterTime: Optional[datetime] = None
    recycleBinExitTime: Optional[datetime] = None
    size: Optional[int] = None
    snapshotId: Optional[str] = None
    sourceVolumeId: Optional[str] = None
    state: Optional[VolumeState] = None
    throughput: Optional[int] = None
    volumeId: Optional[str] = None
    volumeType: Optional[VolumeType] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "createTime": self.createTime.isoformat() if self.createTime else None,
            "iops": self.iops,
            "operator": self.operator.to_dict() if self.operator else None,
            "outpostArn": self.outpostArn,
            "recycleBinEnterTime": self.recycleBinEnterTime.isoformat() if self.recycleBinEnterTime else None,
            "recycleBinExitTime": self.recycleBinExitTime.isoformat() if self.recycleBinExitTime else None,
            "size": self.size,
            "snapshotId": self.snapshotId,
            "sourceVolumeId": self.sourceVolumeId,
            "state": self.state.value if self.state else None,
            "throughput": self.throughput,
            "volumeId": self.volumeId,
            "volumeType": self.volumeType.value if self.volumeType else None,
        }


class VolumesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.volumes or other relevant state dicts

    def attach_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        device = params.get("Device")
        instance_id = params.get("InstanceId")
        volume_id = params.get("VolumeId")
        dry_run = params.get("DryRun", False)

        # Validate required parameters
        if device is None:
            raise Exception("Missing required parameter Device")
        if instance_id is None:
            raise Exception("Missing required parameter InstanceId")
        if volume_id is None:
            raise Exception("Missing required parameter VolumeId")

        # DryRun check (not implemented fully, just simulate)
        if dry_run:
            # Here we would check permissions, but just simulate success
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Get the volume from state
        volume = self.state.volumes.get(volume_id)
        if volume is None:
            raise Exception(f"Volume {volume_id} does not exist")

        # Check volume state: must be available to attach
        if volume.status != VolumeState.AVAILABLE:
            raise Exception(f"Volume {volume_id} is not in available state")

        # Check instance existence
        instance = self.state.get_resource(instance_id)
        if instance is None:
            raise Exception(f"Instance {instance_id} does not exist")

        # Check availability zone match between volume and instance
        if volume.availabilityZone != getattr(instance, "availabilityZone", None):
            raise Exception("Volume and instance must be in the same Availability Zone")

        # Check if volume is already attached
        for attachment in volume.attachmentSet:
            if attachment.status in [VolumeAttachmentState.ATTACHING, VolumeAttachmentState.ATTACHED]:
                raise Exception(f"Volume {volume_id} is already attached or attaching")

        # Check instance attachment limit (simulate limit 20)
        attached_volumes_count = 0
        for vol in self.state.volumes.values():
            for att in vol.attachmentSet:
                if att.instanceId == instance_id and att.status in [VolumeAttachmentState.ATTACHING, VolumeAttachmentState.ATTACHED]:
                    attached_volumes_count += 1
        if attached_volumes_count >= 20:
            raise Exception("AttachmentLimitExceeded")

        # Create new attachment
        attach_time = datetime.utcnow()
        attachment = VolumeAttachment(
            associatedResource=None,
            attachTime=attach_time,
            deleteOnTermination=False,
            device=device,
            instanceId=instance_id,
            instanceOwningService=None,
            status=VolumeAttachmentState.ATTACHING,
            volumeId=volume_id,
        )
        volume.attachmentSet.append(attachment)
        volume.status = VolumeState.IN_USE

        # Prepare response
        response = {
            "requestId": self.generate_request_id(),
            "volumeId": volume_id,
            "instanceId": instance_id,
            "device": device,
            "status": VolumeAttachmentState.ATTACHING.value,
            "attachTime": attach_time,
            "associatedResource": None,
            "deleteOnTermination": False,
            "instanceOwningService": None,
        }
        return response


    def copy_volumes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        source_volume_id = params.get("SourceVolumeId")
        if source_volume_id is None:
            raise Exception("Missing required parameter SourceVolumeId")

        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        source_volume = self.state.volumes.get(source_volume_id)
        if source_volume is None:
            raise Exception(f"Source volume {source_volume_id} does not exist")

        # Determine size
        size = params.get("Size", source_volume.size)
        if size is None:
            raise Exception("Size must be specified or source volume must have size")

        if size < source_volume.size:
            raise Exception("Size must be equal or greater than source volume size")

        # VolumeType
        volume_type_str = params.get("VolumeType", source_volume.volumeType.value if source_volume.volumeType else "gp2")
        try:
            volume_type = VolumeType(volume_type_str)
        except Exception:
            raise Exception(f"Invalid VolumeType {volume_type_str}")

        # Iops
        iops = params.get("Iops")
        # Validate Iops for volume types io1, io2, gp3
        if volume_type in [VolumeType.IO1, VolumeType.IO2]:
            if iops is None:
                raise Exception(f"Iops is required for volume type {volume_type.value}")
        elif volume_type == VolumeType.GP3:
            # Iops optional for gp3
            pass
        else:
            if iops is not None:
                raise Exception(f"Iops is not valid for volume type {volume_type.value}")

        # MultiAttachEnabled
        multi_attach_enabled = params.get("MultiAttachEnabled", False)
        if multi_attach_enabled and volume_type not in [VolumeType.IO1, VolumeType.IO2]:
            raise Exception("MultiAttachEnabled is supported only for io1 and io2 volumes")

        # Throughput
        throughput = params.get("Throughput")
        if throughput is not None and volume_type != VolumeType.GP3:
            raise Exception("Throughput is supported only for gp3 volumes")

        # TagSpecification
        tag_specifications = params.get("TagSpecification.N", [])
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            if tag_spec.ResourceType and tag_spec.ResourceType != "volume":
                continue
            for tag in tag_spec.Tags:
                tags.append(Tag(Key=tag.Key, Value=tag.Value))

        # Create new volume id
        new_volume_id = self.generate_unique_id(prefix="vol-")

        # Create new volume object
        new_volume = Volume(
            volumeId=new_volume_id,
            size=size,
            snapshotId=None,
            availabilityZone=source_volume.availabilityZone,
            availabilityZoneId=source_volume.availabilityZoneId,
            status=VolumeState.CREATING,
            createTime=datetime.utcnow(),
            encrypted=source_volume.encrypted,
            fastRestored=False,
            iops=iops if iops is not None else source_volume.iops,
            kmsKeyId=source_volume.kmsKeyId,
            multiAttachEnabled=multi_attach_enabled,
            operator=None,
            outpostArn=source_volume.outpostArn,
            sourceVolumeId=source_volume_id,
            sseType=source_volume.sseType,
            tagSet=tags,
            throughput=throughput if throughput is not None else source_volume.throughput,
            volumeInitializationRate=None,
            volumeType=volume_type,
            attachmentSet=[],
        )

        # Add to state
        self.state.volumes[new_volume_id] = new_volume

        # Simulate volume becoming available immediately for simplicity
        new_volume.status = VolumeState.AVAILABLE

        response = {
            "requestId": self.generate_request_id(),
            "volumeSet": [new_volume.to_dict()],
        }
        return response


    def create_replace_root_volume_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        if instance_id is None:
            raise Exception("Missing required parameter InstanceId")

        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate instance exists
        instance = self.state.get_resource(instance_id)
        if instance is None:
            raise Exception(f"Instance {instance_id} does not exist")

        # Generate task id
        task_id = self.generate_unique_id(prefix="rrvt-")

        # Extract optional parameters
        delete_replaced_root_volume = params.get("DeleteReplacedRootVolume", False)
        image_id = params.get("ImageId")
        snapshot_id = params.get("SnapshotId")
        volume_init_rate = params.get("VolumeInitializationRate")
        tag_specifications = params.get("TagSpecification.N", [])
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            if tag_spec.ResourceType and tag_spec.ResourceType != "replace-root-volume-task":
                continue
            for tag in tag_spec.Tags:
                tags.append(Tag(Key=tag.Key, Value=tag.Value))

        start_time = datetime.utcnow().isoformat() + "Z"

        # Create ReplaceRootVolumeTask object
        task = ReplaceRootVolumeTask(
            completeTime=None,
            deleteReplacedRootVolume=delete_replaced_root_volume,
            imageId=image_id,
            instanceId=instance_id,
            replaceRootVolumeTaskId=task_id,
            snapshotId=snapshot_id,
            startTime=start_time,
            tagSet=tags,
            taskState=ReplaceRootVolumeTaskState.PENDING,
        )

        # Store task in state resources keyed by task id
        self.state.resources[task_id] = task

        response = {
            "requestId": self.generate_request_id(),
            "replaceRootVolumeTask": task.to_dict(),
        }
        return response


    def create_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")
        if (availability_zone is None and availability_zone_id is None) or (availability_zone is not None and availability_zone_id is not None):
            raise Exception("Either AvailabilityZone or AvailabilityZoneId must be specified, but not both")

        size = params.get("Size")
        snapshot_id = params.get("SnapshotId")
        if size is None and snapshot_id is None:
            raise Exception("Either Size or SnapshotId must be specified")

        # Determine size if snapshot specified and size not specified
        if snapshot_id is not None and size is None:
            snapshot = self.state.get_resource(snapshot_id)
            if snapshot is None:
                raise Exception(f"Snapshot {snapshot_id} does not exist")
            size = getattr(snapshot, "volumeSize", None)
            if size is None:
                raise Exception(f"Snapshot {snapshot_id} does not have volume size information")

        # VolumeType
        volume_type_str = params.get("VolumeType", "gp2")
        try:
            volume_type = VolumeType(volume_type_str)
        except Exception:
            raise Exception(f"Invalid VolumeType {volume_type_str}")

        # Iops
        iops = params.get("Iops")
        if volume_type in [VolumeType.IO1, VolumeType.IO2]:
            if iops is None:
                raise Exception(f"Iops is required for volume type {volume_type.value}")
        elif volume_type == VolumeType.GP3:
            # Iops optional for gp3
            pass
        else:
            if iops is not None:
                raise Exception(f"Iops is not valid for volume type {volume_type.value}")

        # Encrypted
        encrypted = params.get("Encrypted", False)

        # KmsKeyId
        kms_key_id = params.get("KmsKeyId")
        if kms_key_id is not None and not encrypted:
            raise Exception("KmsKeyId specified but Encrypted is not true")

        # MultiAttachEnabled
        multi_attach_enabled = params.get("MultiAttachEnabled", False)
        if multi_attach_enabled and volume_type not in [VolumeType.IO1, VolumeType.IO2]:
            raise Exception("MultiAttachEnabled is supported only for io1 and io2 volumes")

        # Operator
        operator_req = params.get("Operator")
        operator_resp = None
        if operator_req:
            principal = operator_req.get("Principal")
            operator_resp = OperatorResponse(managed=True if principal else False, principal=principal)

        # OutpostArn
        outpost_arn = params.get("OutpostArn")

        # TagSpecification
        tag_specifications = params.get("TagSpecification.N", [])
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            if tag_spec.ResourceType and tag_spec.ResourceType != "volume":
                continue
            for tag in tag_spec.Tags:
                tags.append(Tag(Key=tag.Key, Value=tag.Value))

        # Throughput
        throughput = params.get("Throughput")
        if throughput is not None and volume_type != VolumeType.GP3:
            raise Exception("Throughput is supported only for gp3 volumes")

        # VolumeInitializationRate
        volume_init_rate = params.get("VolumeInitializationRate")

        # Generate volume id
        volume_id = self.generate_unique_id(prefix="vol-")

        # Create volume object
        volume = Volume(
            volumeId=volume_id,
            size=size,
            snapshotId=snapshot_id,
            availabilityZone=availability_zone,
            availabilityZoneId=availability_zone_id,
            status=VolumeState.CREATING,
            createTime=datetime.utcnow(),
            encrypted=encrypted,
            fastRestored=False,
            iops=iops,
            kmsKeyId=kms_key_id,
            multiAttachEnabled=multi_attach_enabled,
            operator=operator_resp,
            outpostArn=outpost_arn,
            sourceVolumeId=None,
            sseType=None,
            tagSet=tags,
            throughput=throughput,
            volumeInitializationRate=volume_init_rate,
            volumeType=volume_type,
            attachmentSet=[],
        )

        # Add to state
        self.state.volumes[volume_id] = volume

        # Simulate volume becoming available immediately for simplicity
        volume.status = VolumeState.AVAILABLE

        response = {
            "requestId": self.generate_request_id(),
            "volumeId": volume_id,
            "size": size,
            "snapshotId": snapshot_id or "",
            "availabilityZone": availability_zone,
            "availabilityZoneId": availability_zone_id,
            "status": volume.status.value,
            "createTime": volume.createTime,
            "volumeType": volume_type.value,
            "iops": iops,
            "encrypted": encrypted,
            "kmsKeyId": kms_key_id,
            "tagSet": [tag.to_dict() for tag in tags],
            "multiAttachEnabled": multi_attach_enabled,
            "attachmentSet": [],
            "fastRestored": False,
            "operator": operator_resp.to_dict() if operator_resp else None,
            "outpostArn": outpost_arn,
            "throughput": throughput,
            "volumeInitializationRate": volume_init_rate,
            "sourceVolumeId": None,
            "sseType": None,
        }
        return response


    def delete_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        volume_id = params.get("VolumeId")
        dry_run = params.get("DryRun", False)

        if volume_id is None:
            raise Exception("Missing required parameter VolumeId")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        volume = self.state.volumes.get(volume_id)
        if volume is None:
            raise Exception(f"Volume {volume_id} does not exist")

        # Volume must be in available state to delete
        if volume.status != VolumeState.AVAILABLE:
            raise Exception(f"Volume {volume_id} is not in available state and cannot be deleted")

        # Mark volume as deleting
        volume.status = VolumeState.DELETING

        # Remove volume from state to simulate deletion
        del self.state.volumes[volume_id]

        response = {
            "requestId": self.generate_request_id(),
            "return": True,
        }
        return response

    def describe_replace_root_volume_tasks(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        task_ids = params.get("ReplaceRootVolumeTaskId", [])

        # DryRun check - not implemented here, assume always allowed

        # Collect all tasks
        all_tasks = list(self.state.replace_root_volume_tasks.values())

        # Filter by ReplaceRootVolumeTaskId if provided
        if task_ids:
            all_tasks = [t for t in all_tasks if t.replaceRootVolumeTaskId in task_ids]

        # Apply filters
        def match_filter(task, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "instance-id":
                return task.instanceId in values
            return True

        for f in filters:
            all_tasks = [t for t in all_tasks if match_filter(t, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 50
        else:
            max_results = max(1, min(int(max_results), 50))

        paged_tasks = all_tasks[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(all_tasks):
            new_next_token = str(start_index + max_results)

        response = {
            "replaceRootVolumeTaskSet": [t.to_dict() for t in paged_tasks],
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
        }
        return response


    def describe_volume_attribute(self, params: dict) -> dict:
        attribute = params.get("Attribute")
        volume_id = params.get("VolumeId")
        dry_run = params.get("DryRun")

        if not attribute:
            raise Exception("Missing required parameter Attribute")
        if not volume_id:
            raise Exception("Missing required parameter VolumeId")

        # DryRun check - not implemented here, assume always allowed

        volume = self.state.volumes.get(volume_id)
        if not volume:
            raise Exception(f"Volume {volume_id} not found")

        response = {
            "requestId": self.generate_request_id(),
            "volumeId": volume_id,
        }

        if attribute == "autoEnableIO":
            # We do not have autoEnableIO stored, assume False
            response["autoEnableIO"] = AttributeBooleanValue(Value=False).to_dict()
        elif attribute == "productCodes":
            # We do not have product codes stored, return empty list
            response["productCodes"] = []
        else:
            raise Exception(f"Invalid attribute {attribute}")

        return response


    def describe_volumes(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        volume_ids = params.get("VolumeId", [])

        # DryRun check - not implemented here, assume always allowed

        volumes = list(self.state.volumes.values())

        # Filter by volume IDs if provided
        if volume_ids:
            volumes = [v for v in volumes if v.volumeId in volume_ids]

        # Helper to match filters
        def match_filter(volume, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True

            # Support tag:<key> filter
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in volume.tagSet:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False

            # Support tag-key filter
            if name == "tag-key":
                for tag in volume.tagSet:
                    if tag.Key in values:
                        return True
                return False

            # Support other filters
            if name == "attachment.attach-time":
                for att in volume.attachmentSet:
                    if att.attachTime and str(att.attachTime) in values:
                        return True
                return False
            if name == "attachment.delete-on-termination":
                for att in volume.attachmentSet:
                    if att.deleteOnTermination is not None and str(att.deleteOnTermination).lower() in [v.lower() for v in values]:
                        return True
                return False
            if name == "attachment.device":
                for att in volume.attachmentSet:
                    if att.device in values:
                        return True
                return False
            if name == "attachment.instance-id":
                for att in volume.attachmentSet:
                    if att.instanceId in values:
                        return True
                return False
            if name == "attachment.status":
                for att in volume.attachmentSet:
                    if att.status and att.status.value in values:
                        return True
                return False
            if name == "availability-zone":
                return volume.availabilityZone in values
            if name == "availability-zone-id":
                return volume.availabilityZoneId in values
            if name == "create-time":
                if volume.createTime:
                    return str(volume.createTime) in values
                return False
            if name == "encrypted":
                if volume.encrypted is not None:
                    return str(volume.encrypted).lower() in [v.lower() for v in values]
                return False
            if name == "fast-restored":
                if volume.fastRestored is not None:
                    return str(volume.fastRestored).lower() in [v.lower() for v in values]
                return False
            if name == "multi-attach-enabled":
                if volume.multiAttachEnabled is not None:
                    return str(volume.multiAttachEnabled).lower() in [v.lower() for v in values]
                return False
            if name == "operator.managed":
                if volume.operator and volume.operator.managed is not None:
                    return str(volume.operator.managed).lower() in [v.lower() for v in values]
                return False
            if name == "operator.principal":
                if volume.operator and volume.operator.principal:
                    return volume.operator.principal in values
                return False
            if name == "size":
                if volume.size is not None:
                    return str(volume.size) in values
                return False
            if name == "snapshot-id":
                return volume.snapshotId in values
            if name == "status":
                if volume.status:
                    return volume.status.value in values
                return False
            if name == "volume-id":
                return volume.volumeId in values
            if name == "volume-type":
                if volume.volumeType:
                    return volume.volumeType.value in values
                return False

            return True

        for f in filters:
            volumes = [v for v in volumes if match_filter(v, f)]

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
            max_results = max(1, int(max_results))

        paged_volumes = volumes[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(volumes):
            new_next_token = str(start_index + max_results)

        response = {
            "volumeSet": [v.to_dict() for v in paged_volumes],
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
        }
        return response


    def describe_volumes_modifications(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        volume_ids = params.get("VolumeId", [])

        # DryRun check - not implemented here, assume always allowed

        modifications = list(self.state.volume_modifications.values())

        # Filter by volume IDs if provided
        if volume_ids:
            modifications = [m for m in modifications if m.volumeId in volume_ids]

        # Helper to match filters
        def match_filter(mod, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True

            if name == "modification-state":
                if mod.modificationState:
                    return mod.modificationState.value in values
                return False
            if name == "original-iops":
                if mod.originalIops is not None:
                    return str(mod.originalIops) in values
                return False
            if name == "original-size":
                if mod.originalSize is not None:
                    return str(mod.originalSize) in values
                return False
            if name == "original-volume-type":
                if mod.originalVolumeType:
                    return mod.originalVolumeType.value in values
                return False
            if name == "originalMultiAttachEnabled":
                if mod.originalMultiAttachEnabled is not None:
                    return str(mod.originalMultiAttachEnabled).lower() in [v.lower() for v in values]
                return False
            if name == "start-time":
                if mod.startTime:
                    return str(mod.startTime) in values
                return False
            if name == "target-iops":
                if mod.targetIops is not None:
                    return str(mod.targetIops) in values
                return False
            if name == "target-size":
                if mod.targetSize is not None:
                    return str(mod.targetSize) in values
                return False
            if name == "target-volume-type":
                if mod.targetVolumeType:
                    return mod.targetVolumeType.value in values
                return False
            if name == "targetMultiAttachEnabled":
                if mod.targetMultiAttachEnabled is not None:
                    return str(mod.targetMultiAttachEnabled).lower() in [v.lower() for v in values]
                return False
            if name == "volume-id":
                return mod.volumeId in values

            return True

        for f in filters:
            modifications = [m for m in modifications if match_filter(m, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 500
        else:
            max_results = max(1, int(max_results))

        paged_modifications = modifications[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(modifications):
            new_next_token = str(start_index + max_results)

        response = {
            "volumeModificationSet": [m.to_dict() for m in paged_modifications],
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
        }
        return response


    def describe_volume_status(self, params: dict) -> dict:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        volume_ids = params.get("VolumeId", [])

        # DryRun check - not implemented here, assume always allowed

        volumes = list(self.state.volumes.values())

        # Filter by volume IDs if provided
        if volume_ids:
            volumes = [v for v in volumes if v.volumeId in volume_ids]

        # Helper to match filters
        def match_filter(volume, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True

            # action.code, action.description, action.event-id
            if name.startswith("action."):
                # We do not have detailed action info, so no match
                return False

            # availability-zone
            if name == "availability-zone":
                return volume.availabilityZone in values

            # event.description, event.event-id, event.event-type, event.not-after, event.not-before
            if name.startswith("event."):
                # We do not have detailed event info, so no match
                return False

            # volume-status.details-name
            if name == "volume-status.details-name":
                if volume.status and volume.status.details:
                    for detail in volume.status.details:
                        if detail.name and detail.name.value in values:
                            return True
                return False

            # volume-status.details-status
            if name == "volume-status.details-status":
                if volume.status and volume.status.details:
                    for detail in volume.status.details:
                        if detail.status in values:
                            return True
                return False

            # volume-status.status
            if name == "volume-status.status":
                if volume.status and volume.status.status:
                    return volume.status.status.value in values
                return False

            return True

        for f in filters:
            volumes = [v for v in volumes if match_filter(v, f)]

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
            max_results = max(1, int(max_results))

        paged_volumes = volumes[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(volumes):
            new_next_token = str(start_index + max_results)

        response = {
            "volumeStatusSet": [v.to_dict() for v in paged_volumes],
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
        }
        return response

    def detach_volume(self, params: dict) -> dict:
        volume_id = params.get("VolumeId")
        if not volume_id:
            raise Exception("Missing required parameter VolumeId")
        device = params.get("Device")
        force = params.get("Force", False)
        instance_id = params.get("InstanceId")
        dry_run = params.get("DryRun", False)

        # DryRun check placeholder (not implemented)
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        volume = self.state.volumes.get(volume_id)
        if not volume:
            raise Exception(f"Volume {volume_id} does not exist")

        # Check if volume is attached to AWS-managed resource
        for attachment in volume.attachmentSet:
            if attachment.instanceOwningService:
                # Cannot detach volumes attached to AWS-managed resources
                raise Exception("UnsupportedOperationException: Cannot detach volumes attached to AWS-managed resources")

        # Find the attachment to detach
        attachment_to_detach = None
        if instance_id:
            # If instanceId specified, find attachment with that instanceId
            for attachment in volume.attachmentSet:
                if attachment.instanceId == instance_id:
                    attachment_to_detach = attachment
                    break
        elif device:
            # If device specified, find attachment with that device
            for attachment in volume.attachmentSet:
                if attachment.device == device:
                    attachment_to_detach = attachment
                    break
        else:
            # If neither instanceId nor device specified, detach first attachment if any
            if volume.attachmentSet:
                attachment_to_detach = volume.attachmentSet[0]

        if not attachment_to_detach:
            # No matching attachment found
            # If volume is not attached, return detached status
            return {
                "requestId": self.generate_request_id(),
                "volumeId": volume_id,
                "status": "detached",
            }

        # If volume is root device and instance is running, cannot detach
        # We do not have instance state here, so we skip this check

        # Update attachment status to detaching
        attachment_to_detach.status = VolumeAttachmentState.DETACHING
        attachment_to_detach.attachTime = None

        # Remove attachment from volume's attachmentSet
        volume.attachmentSet = [att for att in volume.attachmentSet if att != attachment_to_detach]

        # Update volume status if no attachments remain
        if not volume.attachmentSet:
            volume.status = VolumeState.AVAILABLE

        response = {
            "requestId": self.generate_request_id(),
            "volumeId": volume.volumeId,
            "instanceId": attachment_to_detach.instanceId,
            "device": attachment_to_detach.device,
            "status": "detaching",
            "attachTime": attachment_to_detach.attachTime,
            "deleteOnTermination": attachment_to_detach.deleteOnTermination,
            "associatedResource": attachment_to_detach.associatedResource,
            "instanceOwningService": attachment_to_detach.instanceOwningService,
        }
        return response


    def enable_volume_io(self, params: dict) -> dict:
        volume_id = params.get("VolumeId")
        if not volume_id:
            raise Exception("Missing required parameter VolumeId")
        dry_run = params.get("DryRun", False)

        # DryRun check placeholder (not implemented)
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        volume = self.state.volumes.get(volume_id)
        if not volume:
            raise Exception(f"Volume {volume_id} does not exist")

        # Enable I/O operations for the volume
        # We assume enabling I/O means setting some attribute; here we simulate by setting a flag
        # Since no explicit attribute for I/O enabled, we can assume encrypted or other flags are not related
        # So we just return success

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def modify_volume(self, params: dict) -> dict:
        volume_id = params.get("VolumeId")
        if not volume_id:
            raise Exception("Missing required parameter VolumeId")

        dry_run = params.get("DryRun", False)
        iops = params.get("Iops")
        multi_attach_enabled = params.get("MultiAttachEnabled")
        size = params.get("Size")
        throughput = params.get("Throughput")
        volume_type = params.get("VolumeType")

        # DryRun check placeholder (not implemented)
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        volume = self.state.volumes.get(volume_id)
        if not volume:
            raise Exception(f"Volume {volume_id} does not exist")

        # Validate size if provided
        if size is not None:
            if size < (volume.size or 0):
                raise Exception("New size must be greater than or equal to existing size")

        # Save original values
        original_iops = volume.iops
        original_multi_attach_enabled = volume.multiAttachEnabled
        original_size = volume.size
        original_throughput = volume.throughput
        original_volume_type = volume.volumeType

        # Update volume attributes if provided
        if iops is not None:
            volume.iops = iops
        if multi_attach_enabled is not None:
            volume.multiAttachEnabled = multi_attach_enabled
        if size is not None:
            volume.size = size
        if throughput is not None:
            volume.throughput = throughput
        if volume_type is not None:
            volume.volumeType = volume_type

        # Create VolumeModification object
        modification = VolumeModification()
        modification.volumeId = volume_id
        modification.originalIops = original_iops
        modification.originalMultiAttachEnabled = original_multi_attach_enabled
        modification.originalSize = original_size
        modification.originalThroughput = original_throughput
        modification.originalVolumeType = original_volume_type
        modification.targetIops = volume.iops
        modification.targetMultiAttachEnabled = volume.multiAttachEnabled
        modification.targetSize = volume.size
        modification.targetThroughput = volume.throughput
        modification.targetVolumeType = volume.volumeType
        modification.modificationState = VolumeModificationState.MODIFYING
        modification.progress = 0
        modification.startTime = datetime.utcnow()
        modification.statusMessage = "Modification in progress"

        # Store modification in state
        self.state.volume_modifications[volume_id] = modification

        return {
            "requestId": self.generate_request_id(),
            "volumeModification": modification.to_dict(),
        }


    def modify_volume_attribute(self, params: dict) -> dict:
        volume_id = params.get("VolumeId")
        if not volume_id:
            raise Exception("Missing required parameter VolumeId")

        dry_run = params.get("DryRun", False)
        auto_enable_io = params.get("AutoEnableIO")

        # DryRun check placeholder (not implemented)
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        volume = self.state.volumes.get(volume_id)
        if not volume:
            raise Exception(f"Volume {volume_id} does not exist")

        if auto_enable_io is not None:
            # auto_enable_io is an AttributeBooleanValue object with Value attribute
            value = None
            if isinstance(auto_enable_io, dict):
                value = auto_enable_io.get("Value")
            elif hasattr(auto_enable_io, "Value"):
                value = auto_enable_io.Value
            if value is not None:
                # We simulate enabling/disabling I/O by setting a flag on volume
                # Since no explicit attribute, we can store it in volume.encrypted as placeholder or add new attribute
                # Here we add attribute auto_enable_io_enabled
                setattr(volume, "auto_enable_io_enabled", value)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def list_volumes_in_recycle_bin(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        volume_ids = params.get("VolumeId.N", [])

        # DryRun check placeholder (not implemented)
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        # Filter volumes in recycle bin
        recycle_bin_volumes = []
        for volume in self.state.volumes.values():
            # We consider volumes with state in recycle bin states
            if hasattr(volume, "recycleBinEnterTime") and volume.recycleBinEnterTime is not None:
                if volume_ids and volume.volumeId not in volume_ids:
                    continue
                recycle_bin_volumes.append(volume)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(recycle_bin_volumes)
        if max_results is not None:
            max_results = max(5, min(max_results, 500))
            end_index = min(start_index + max_results, len(recycle_bin_volumes))

        paged_volumes = recycle_bin_volumes[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(recycle_bin_volumes):
            new_next_token = str(end_index)

        volume_set = [v.to_dict() for v in paged_volumes]

        return {
            "requestId": self.generate_request_id(),
            "volumeSet": volume_set,
            "nextToken": new_next_token,
        }

    def restore_volume_from_recycle_bin(self, params: dict) -> dict:
        volume_id = params.get("VolumeId")
        dry_run = params.get("DryRun", False)

        if not volume_id:
            raise ValueError("VolumeId is required")

        # DryRun check
        if dry_run:
            # Check permissions - for emulator, assume always allowed
            # Return DryRunOperation error if not allowed
            # Here, we simulate allowed
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        recycle_bin_volume = self.state.volumes.get(volume_id)
        if not recycle_bin_volume:
            # Volume not found in volumes, check recycle bin
            recycle_bin_info = self.state.recycle_bin_volumes.get(volume_id)
            if not recycle_bin_info:
                raise ValueError(f"Volume {volume_id} not found in recycle bin")

            # Restore volume from recycle bin
            # Remove from recycle bin dict
            del self.state.recycle_bin_volumes[volume_id]

            # Create a new Volume object from recycle_bin_info
            restored_volume = Volume(
                volumeId=volume_id,
                size=recycle_bin_info.size,
                snapshotId=recycle_bin_info.snapshotId,
                availabilityZone=recycle_bin_info.availabilityZone,
                availabilityZoneId=recycle_bin_info.availabilityZoneId,
                status=VolumeState.AVAILABLE,
                createTime=recycle_bin_info.createTime,
                encrypted=None,
                fastRestored=None,
                iops=recycle_bin_info.iops,
                kmsKeyId=None,
                multiAttachEnabled=None,
                operator=recycle_bin_info.operator,
                outpostArn=recycle_bin_info.outpostArn,
                sourceVolumeId=recycle_bin_info.sourceVolumeId,
                sseType=None,
                tagSet=[],
                throughput=recycle_bin_info.throughput,
                volumeInitializationRate=None,
                volumeType=recycle_bin_info.volumeType,
                attachmentSet=[],
            )
            self.state.volumes[volume_id] = restored_volume
        else:
            # Volume already exists in volumes, cannot restore
            raise ValueError(f"Volume {volume_id} is not in recycle bin")

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class VolumesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AttachVolume", self.attach_volume)
        self.register_action("CopyVolumes", self.copy_volumes)
        self.register_action("CreateReplaceRootVolumeTask", self.create_replace_root_volume_task)
        self.register_action("CreateVolume", self.create_volume)
        self.register_action("DeleteVolume", self.delete_volume)
        self.register_action("DescribeReplaceRootVolumeTasks", self.describe_replace_root_volume_tasks)
        self.register_action("DescribeVolumeAttribute", self.describe_volume_attribute)
        self.register_action("DescribeVolumes", self.describe_volumes)
        self.register_action("DescribeVolumesModifications", self.describe_volumes_modifications)
        self.register_action("DescribeVolumeStatus", self.describe_volume_status)
        self.register_action("DetachVolume", self.detach_volume)
        self.register_action("EnableVolumeIO", self.enable_volume_io)
        self.register_action("ModifyVolume", self.modify_volume)
        self.register_action("ModifyVolumeAttribute", self.modify_volume_attribute)
        self.register_action("ListVolumesInRecycleBin", self.list_volumes_in_recycle_bin)
        self.register_action("RestoreVolumeFromRecycleBin", self.restore_volume_from_recycle_bin)

    def attach_volume(self, params):
        return self.backend.attach_volume(params)

    def copy_volumes(self, params):
        return self.backend.copy_volumes(params)

    def create_replace_root_volume_task(self, params):
        return self.backend.create_replace_root_volume_task(params)

    def create_volume(self, params):
        return self.backend.create_volume(params)

    def delete_volume(self, params):
        return self.backend.delete_volume(params)

    def describe_replace_root_volume_tasks(self, params):
        return self.backend.describe_replace_root_volume_tasks(params)

    def describe_volume_attribute(self, params):
        return self.backend.describe_volume_attribute(params)

    def describe_volumes(self, params):
        return self.backend.describe_volumes(params)

    def describe_volumes_modifications(self, params):
        return self.backend.describe_volumes_modifications(params)

    def describe_volume_status(self, params):
        return self.backend.describe_volume_status(params)

    def detach_volume(self, params):
        return self.backend.detach_volume(params)

    def enable_volume_io(self, params):
        return self.backend.enable_volume_io(params)

    def modify_volume(self, params):
        return self.backend.modify_volume(params)

    def modify_volume_attribute(self, params):
        return self.backend.modify_volume_attribute(params)

    def list_volumes_in_recycle_bin(self, params):
        return self.backend.list_volumes_in_recycle_bin(params)

    def restore_volume_from_recycle_bin(self, params):
        return self.backend.restore_volume_from_recycle_bin(params)
