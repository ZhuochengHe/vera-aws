from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re
from ..utils import (get_scalar, get_int, get_indexed_list, parse_filters, apply_filters,
                    parse_tags, str2bool, esc, create_error_response,
                    is_error_response, serialize_error_response)
from ..state import EC2State

class ResourceState(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    RUNNING = 'running'
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    NONEXISTENT = 'non-existent'
    FAILED = 'failed'
    SHUTTING_DOWN = 'shutting-down'
    STOPPING = 'stopping'
    STARTING = 'starting'
    REBOOTING = 'rebooting'
    ATTACHED = 'attached'
    IN_USE = 'in-use'
    CREATING = 'creating'

class ErrorCode(Enum):
    INVALID_PARAMETER_VALUE = 'InvalidParameterValue'
    RESOURCE_NOT_FOUND = 'ResourceNotFound'
    INVALID_STATE_TRANSITION = 'InvalidStateTransition'
    DEPENDENCY_VIOLATION = 'DependencyViolation'

@dataclass
class Volume:
    attachment_set: List[Any] = field(default_factory=list)
    availability_zone: str = ""
    availability_zone_id: str = ""
    create_time: str = ""
    encrypted: bool = False
    fast_restored: bool = False
    iops: int = 0
    kms_key_id: str = ""
    multi_attach_enabled: bool = False
    operator: Dict[str, Any] = field(default_factory=dict)
    outpost_arn: str = ""
    size: int = 0
    snapshot_id: str = ""
    source_volume_id: str = ""
    sse_type: str = ""
    status: str = ""
    tag_set: List[Any] = field(default_factory=list)
    throughput: int = 0
    volume_id: str = ""
    volume_initialization_rate: int = 0
    volume_type: str = ""

    # Internal dependency tracking — not in API response
    snapshot_ids: List[str] = field(default_factory=list)  # tracks Snapshot children

    auto_enable_io: bool = True
    product_codes: List[Dict[str, Any]] = field(default_factory=list)
    in_recycle_bin: bool = False
    recycle_bin_enter_time: str = ""
    recycle_bin_exit_time: str = ""
    last_volume_modification: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "attachmentSet": self.attachment_set,
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "createTime": self.create_time,
            "encrypted": self.encrypted,
            "fastRestored": self.fast_restored,
            "iops": self.iops,
            "kmsKeyId": self.kms_key_id,
            "multiAttachEnabled": self.multi_attach_enabled,
            "operator": self.operator,
            "outpostArn": self.outpost_arn,
            "size": self.size,
            "snapshotId": self.snapshot_id,
            "sourceVolumeId": self.source_volume_id,
            "sseType": self.sse_type,
            "status": self.status,
            "tagSet": self.tag_set,
            "throughput": self.throughput,
            "volumeId": self.volume_id,
            "volumeInitializationRate": self.volume_initialization_rate,
            "volumeType": self.volume_type,
        }

class Volume_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.volumes  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.fast_snapshot_restores.get(params['availability_zone_id']).volume_ids.append(new_id)
    #   Delete: self.state.fast_snapshot_restores.get(resource.availability_zone_id).volume_ids.remove(resource_id)
    #   Create: self.state.snapshots.get(params['snapshot_id']).volume_ids.append(new_id)
    #   Delete: self.state.snapshots.get(resource.snapshot_id).volume_ids.remove(resource_id)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(self, store: Dict[str, Any], resource_id: str, error_code: str, message: Optional[str] = None):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message or f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources = []
        for resource_id in resource_ids:
            resource = store.get(resource_id)
            if not resource:
                return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
            resources.append(resource)
        return resources, None

    def _get_volume_or_error(self, volume_id: str, error_code: str = "InvalidVolume.NotFound"):
        return self._get_resource_or_error(self.resources, volume_id, error_code, f"The ID '{volume_id}' does not exist")

    def _get_instance_or_error(self, instance_id: str, error_code: str = "InvalidInstanceID.NotFound"):
        return self._get_resource_or_error(self.state.instances, instance_id, error_code, f"The ID '{instance_id}' does not exist.")

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: str = "volume") -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def _paginate(self, resources: List[Any], max_results: int, next_token: Optional[str]):
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0
        page = resources[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(resources):
            new_next_token = str(start_index + max_results)
        return page, new_next_token

    def _get_replace_root_volume_tasks_store(self) -> Dict[str, Dict[str, Any]]:
        if not hasattr(self.state, "replace_root_volume_tasks"):
            setattr(self.state, "replace_root_volume_tasks", {})
        return self.state.replace_root_volume_tasks


    # - Filtering: _apply_filters(resources: List, filters: List) -> List
    # - Dependencies: _check_dependencies(resource_id: str) -> List[str]
    # - Transformations: _transform_tags(tag_specs: List) -> List[Dict]
    # - State management: _update_state(resource, new_state: str)
    # - Complex operations: _process_associations(params: Dict) -> Dict
    # Add any helper functions needed by the API methods below.
    # These helpers can be used by multiple API methods.

    def AttachVolume(self, params: Dict[str, Any]):
        """Attaches an Amazon EBS volume to arunningorstoppedinstance, and exposes it to the instance with the specified device name. The maximum number of Amazon EBS volumes that you can attach to an instance depends on the 
        instance type. If you exceed the volume attachment limit for an instance type"""

        error = self._require_params(params, ["Device", "InstanceId", "VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        instance_id = params.get("InstanceId")
        instance, error = self._get_instance_or_error(instance_id, "InvalidInstanceID.NotFound")
        if error:
            return error

        if volume.status != "available":
            return create_error_response(
                "InvalidVolume.State",
                f"Volume '{volume_id}' is not in the 'available' state",
            )

        device = params.get("Device")
        attach_time = self._utc_now()
        attachment = {
            "associatedResource": None,
            "attachTime": attach_time,
            "deleteOnTermination": False,
            "device": device,
            "instanceId": instance_id,
            "instanceOwningService": None,
            "status": "attached",
            "volumeId": volume_id,
        }

        volume.attachment_set.append(attachment)
        volume.status = "in-use"

        if hasattr(instance, "volume_ids"):
            if volume_id not in instance.volume_ids:
                instance.volume_ids.append(volume_id)

        return {
            "associatedResource": attachment["associatedResource"],
            "attachTime": attachment["attachTime"],
            "deleteOnTermination": attachment["deleteOnTermination"],
            "device": attachment["device"],
            "instanceId": attachment["instanceId"],
            "instanceOwningService": attachment["instanceOwningService"],
            "status": attachment["status"],
            "volumeId": attachment["volumeId"],
        }

    def CopyVolumes(self, params: Dict[str, Any]):
        """Creates a crash-consistent, point-in-time copy of an existing Amazon EBS volume within the same 
      Availability Zone. The volume copy can be attached to an Amazon EC2 instance once it reaches theavailablestate. For more information, seeCopy an Amazon EBS volume."""

        error = self._require_params(params, ["SourceVolumeId"])
        if error:
            return error

        source_volume_id = params.get("SourceVolumeId")
        source_volume, error = self._get_volume_or_error(source_volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        volume_id = self._generate_id("vol")
        now = self._utc_now()
        tag_set = self._extract_tags(params.get("TagSpecification.N", []))
        if not tag_set:
            tag_set = list(source_volume.tag_set)

        volume = Volume(
            attachment_set=[],
            availability_zone=source_volume.availability_zone,
            availability_zone_id=source_volume.availability_zone_id,
            create_time=now,
            encrypted=source_volume.encrypted,
            fast_restored=source_volume.fast_restored,
            iops=params.get("Iops") if params.get("Iops") is not None else source_volume.iops,
            kms_key_id=source_volume.kms_key_id,
            multi_attach_enabled=str2bool(params.get("MultiAttachEnabled")) if params.get("MultiAttachEnabled") is not None else source_volume.multi_attach_enabled,
            operator=dict(source_volume.operator),
            outpost_arn=source_volume.outpost_arn,
            size=params.get("Size") if params.get("Size") is not None else source_volume.size,
            snapshot_id=source_volume.snapshot_id,
            source_volume_id=source_volume_id,
            sse_type=source_volume.sse_type,
            status="available",
            tag_set=tag_set,
            throughput=params.get("Throughput") if params.get("Throughput") is not None else source_volume.throughput,
            volume_id=volume_id,
            volume_initialization_rate=source_volume.volume_initialization_rate,
            volume_type=params.get("VolumeType") or source_volume.volume_type,
        )

        self.resources[volume_id] = volume

        if volume.availability_zone_id:
            parent = self.state.fast_snapshot_restores.get(volume.availability_zone_id)
            if parent and hasattr(parent, "volume_ids"):
                parent.volume_ids.append(volume_id)

        if volume.snapshot_id:
            parent = self.state.snapshots.get(volume.snapshot_id)
            if parent and hasattr(parent, "volume_ids"):
                parent.volume_ids.append(volume_id)

        return {
            "volumeSet": [volume.to_dict()],
        }

    def CreateReplaceRootVolumeTask(self, params: Dict[str, Any]):
        """Replaces the EBS-backed root volume for arunninginstance with a new 
      volume that is restored to the original root volume's launch state, that is restored to a 
      specific snapshot taken from the original root volume, or that is restored from an AMI 
      that has the same key characterist"""

        error = self._require_params(params, ["InstanceId"])
        if error:
            return error

        instance_id = params.get("InstanceId")
        _, error = self._get_instance_or_error(instance_id)
        if error:
            return error

        snapshot_id = params.get("SnapshotId")
        if snapshot_id:
            _, error = self._get_resource_or_error(
                self.state.snapshots,
                snapshot_id,
                "InvalidSnapshot.NotFound",
                f"The ID '{snapshot_id}' does not exist",
            )
            if error:
                return error

        image_id = params.get("ImageId")
        if image_id and not self.state.amis.get(image_id):
            return create_error_response(
                "InvalidAMIID.NotFound",
                f"The ID '{image_id}' does not exist",
            )

        tag_set = self._extract_tags(params.get("TagSpecification.N", []), "replace-root-volume-task")
        start_time = self._utc_now()
        task_id = self._generate_id("rrt")
        delete_replaced = str2bool(params.get("DeleteReplacedRootVolume"))
        task = {
            "completeTime": start_time,
            "deleteReplacedRootVolume": delete_replaced,
            "imageId": image_id or "",
            "instanceId": instance_id,
            "replaceRootVolumeTaskId": task_id,
            "snapshotId": snapshot_id or "",
            "startTime": start_time,
            "tagSet": tag_set,
            "taskState": "completed",
        }

        tasks_store = self._get_replace_root_volume_tasks_store()
        tasks_store[task_id] = task

        return {
            "replaceRootVolumeTask": task,
        }

    def CreateVolume(self, params: Dict[str, Any]):
        """Creates an EBS volume that can be attached to an instance in the same Availability Zone. You can create a new empty volume or restore a volume from an EBS snapshot.
      Any AWS Marketplace product codes from the snapshot are propagated to the volume. You can create encrypted volumes. Encrypted vol"""

        snapshot_id = params.get("SnapshotId")
        snapshot = None
        if snapshot_id:
            snapshot, error = self._get_resource_or_error(
                self.state.snapshots,
                snapshot_id,
                "InvalidSnapshot.NotFound",
                f"The ID '{snapshot_id}' does not exist",
            )
            if error:
                return error

        availability_zone = params.get("AvailabilityZone") or ""
        availability_zone_id = params.get("AvailabilityZoneId") or ""
        size = params.get("Size")
        if size is None and snapshot:
            size = snapshot.volume_size
        size = size or 0

        encrypted_param = params.get("Encrypted")
        if encrypted_param is None:
            encrypted = snapshot.encrypted if snapshot else False
        else:
            encrypted = str2bool(encrypted_param)

        iops = params.get("Iops") or 0
        kms_key_id = params.get("KmsKeyId") or (snapshot.kms_key_id if snapshot else "")
        multi_attach_enabled = str2bool(params.get("MultiAttachEnabled"))
        outpost_arn = params.get("OutpostArn") or ""
        throughput = params.get("Throughput") or 0
        volume_initialization_rate = params.get("VolumeInitializationRate") or 0
        volume_type = params.get("VolumeType") or "gp2"

        operator_data = params.get("Operator")
        if not isinstance(operator_data, dict):
            operator_data = {}
        operator = {
            "managed": operator_data.get("managed"),
            "principal": operator_data.get("principal"),
        }

        tag_set = self._extract_tags(params.get("TagSpecification.N", []))
        volume_id = self._generate_id("vol")
        now = self._utc_now()

        volume = Volume(
            attachment_set=[],
            availability_zone=availability_zone,
            availability_zone_id=availability_zone_id,
            create_time=now,
            encrypted=encrypted,
            fast_restored=False,
            iops=iops,
            kms_key_id=kms_key_id,
            multi_attach_enabled=multi_attach_enabled,
            operator=operator,
            outpost_arn=outpost_arn,
            size=size,
            snapshot_id=snapshot_id or "",
            source_volume_id="",
            sse_type="",
            status="available",
            tag_set=tag_set,
            throughput=throughput,
            volume_id=volume_id,
            volume_initialization_rate=volume_initialization_rate,
            volume_type=volume_type,
        )

        self.resources[volume_id] = volume

        if availability_zone_id:
            parent = self.state.fast_snapshot_restores.get(availability_zone_id)
            if parent and hasattr(parent, "volume_ids"):
                parent.volume_ids.append(volume_id)

        if snapshot_id:
            parent = self.state.snapshots.get(snapshot_id)
            if parent and hasattr(parent, "volume_ids"):
                parent.volume_ids.append(volume_id)

        return {
            "attachmentSet": volume.attachment_set,
            "availabilityZone": volume.availability_zone,
            "availabilityZoneId": volume.availability_zone_id,
            "createTime": volume.create_time,
            "encrypted": volume.encrypted,
            "fastRestored": volume.fast_restored,
            "iops": volume.iops,
            "kmsKeyId": volume.kms_key_id,
            "multiAttachEnabled": volume.multi_attach_enabled,
            "operator": volume.operator,
            "outpostArn": volume.outpost_arn,
            "size": volume.size,
            "snapshotId": volume.snapshot_id,
            "sourceVolumeId": volume.source_volume_id,
            "sseType": volume.sse_type,
            "status": volume.status,
            "tagSet": volume.tag_set,
            "throughput": volume.throughput,
            "volumeId": volume.volume_id,
            "volumeInitializationRate": volume.volume_initialization_rate,
            "volumeType": volume.volume_type,
        }

    def DeleteVolume(self, params: Dict[str, Any]):
        """Deletes the specified EBS volume. The volume must be in theavailablestate
      (not attached to an instance). The volume can remain in thedeletingstate for several minutes. For more information, seeDelete an Amazon EBS volumein theAmazon EBS User Guide."""

        error = self._require_params(params, ["VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        if volume.status != "available":
            return create_error_response(
                "InvalidVolume.State",
                f"Volume '{volume_id}' is not in the 'available' state",
            )

        if getattr(volume, "snapshot_ids", []):
            return create_error_response(
                "DependencyViolation",
                "Volume has dependent Snapshot(s) and cannot be deleted.",
            )

        parent = self.state.fast_snapshot_restores.get(volume.availability_zone_id)
        if parent and hasattr(parent, "volume_ids") and volume_id in parent.volume_ids:
            parent.volume_ids.remove(volume_id)

        parent = self.state.snapshots.get(volume.snapshot_id)
        if parent and hasattr(parent, "volume_ids") and volume_id in parent.volume_ids:
            parent.volume_ids.remove(volume_id)

        self.resources.pop(volume_id, None)

        return {
            "return": True,
        }

    def DescribeReplaceRootVolumeTasks(self, params: Dict[str, Any]):
        """Describes a root volume replacement task. For more information, seeReplace a root volumein theAmazon EC2 User Guide."""

        tasks_store = self._get_replace_root_volume_tasks_store()
        task_ids = params.get("ReplaceRootVolumeTaskId.N", [])
        if task_ids:
            tasks, error = self._get_resources_by_ids(
                tasks_store,
                task_ids,
                "InvalidReplaceRootVolumeTaskId.NotFound",
            )
            if error:
                return error
        else:
            tasks = list(tasks_store.values())

        tasks = apply_filters(tasks, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        page, next_token = self._paginate(tasks, max_results, params.get("NextToken"))

        return {
            "nextToken": next_token,
            "replaceRootVolumeTaskSet": page,
        }

    def DescribeVolumeAttribute(self, params: Dict[str, Any]):
        """Describes the specified attribute of the specified volume. You can specify only one
      attribute at a time. For more information about EBS volumes, seeAmazon EBS volumesin theAmazon EBS User Guide."""

        error = self._require_params(params, ["Attribute", "VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        attribute = params.get("Attribute") or ""
        attribute_key = attribute.lower()
        auto_enable_value = None
        product_codes = None
        if attribute_key == "autoenableio":
            auto_enable_value = volume.auto_enable_io
        elif attribute_key == "productcodes":
            product_codes = volume.product_codes
        else:
            return create_error_response(
                "InvalidParameterValue",
                f"Invalid Attribute '{attribute}'",
            )

        return {
            "autoEnableIO": {
                "Value": auto_enable_value,
            },
            "productCodes": product_codes,
            "volumeId": volume.volume_id,
        }

    def DescribeVolumes(self, params: Dict[str, Any]):
        """Describes the specified EBS volumes or all of your EBS volumes. If you are describing a long list of volumes, we recommend that you paginate the output to make the list
      more manageable. For more information, seePagination. For more information about EBS volumes, seeAmazon EBS volumesin theAmaz"""

        volume_ids = params.get("VolumeId.N", [])
        if volume_ids:
            resources, error = self._get_resources_by_ids(self.resources, volume_ids, "InvalidVolume.NotFound")
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        page, next_token = self._paginate(resources, max_results, params.get("NextToken"))

        volume_set = [volume.to_dict() for volume in page]

        return {
            "nextToken": next_token,
            "volumeSet": volume_set,
        }

    def DescribeVolumesModifications(self, params: Dict[str, Any]):
        """Describes the most recent volume modification request for the specified EBS volumes. For more information, seeMonitor the progress of volume modificationsin theAmazon EBS User Guide."""

        volume_ids = params.get("VolumeId.N", [])
        if volume_ids:
            resources, error = self._get_resources_by_ids(self.resources, volume_ids, "InvalidVolume.NotFound")
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        page, next_token = self._paginate(resources, max_results, params.get("NextToken"))

        modification_set = []
        for volume in page:
            if volume.last_volume_modification:
                modification = dict(volume.last_volume_modification)
                modification["volumeId"] = volume.volume_id
            else:
                modification = {
                    "endTime": volume.create_time,
                    "modificationState": "completed",
                    "originalIops": volume.iops,
                    "originalMultiAttachEnabled": volume.multi_attach_enabled,
                    "originalSize": volume.size,
                    "originalThroughput": volume.throughput,
                    "originalVolumeType": volume.volume_type,
                    "progress": 100,
                    "startTime": volume.create_time,
                    "statusMessage": "",
                    "targetIops": volume.iops,
                    "targetMultiAttachEnabled": volume.multi_attach_enabled,
                    "targetSize": volume.size,
                    "targetThroughput": volume.throughput,
                    "targetVolumeType": volume.volume_type,
                    "volumeId": volume.volume_id,
                }
            modification_set.append(modification)

        return {
            "nextToken": next_token,
            "volumeModificationSet": modification_set,
        }

    def DescribeVolumeStatus(self, params: Dict[str, Any]):
        """Describes the status of the specified volumes. Volume status provides the result of the
      checks performed on your volumes to determine events that can impair the performance of your
      volumes. The performance of a volume can be affected if an issue occurs on the volume's
      underlying ho"""

        volume_ids = params.get("VolumeId.N", [])
        if volume_ids:
            resources, error = self._get_resources_by_ids(self.resources, volume_ids, "InvalidVolume.NotFound")
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        page, next_token = self._paginate(resources, max_results, params.get("NextToken"))

        volume_status_set = []
        for volume in page:
            attachment_statuses = []
            for attachment in volume.attachment_set or []:
                attachment_statuses.append({
                    "attachmentStatus": attachment.get("status", "attached") if isinstance(attachment, dict) else "attached",
                    "instanceId": attachment.get("instanceId") if isinstance(attachment, dict) else None,
                    "ioPerformance": "normal",
                })
            volume_status_set.append({
                "actionsSet": [],
                "attachmentStatuses": attachment_statuses,
                "availabilityZone": volume.availability_zone,
                "availabilityZoneId": volume.availability_zone_id,
                "eventsSet": [],
                "initializationStatusDetails": [],
                "outpostArn": volume.outpost_arn,
                "volumeId": volume.volume_id,
                "volumeStatus": {
                    "details": [{"name": "io-enabled", "status": "passed"}],
                    "status": "ok",
                },
            })

        return {
            "nextToken": next_token,
            "volumeStatusSet": volume_status_set,
        }

    def DetachVolume(self, params: Dict[str, Any]):
        """Detaches an EBS volume from an instance. Make sure to unmount any file systems on the
      device within your operating system before detaching the volume. Failure to do so can result
      in the volume becoming stuck in thebusystate while detaching. If this happens,
      detachment can be delaye"""

        error = self._require_params(params, ["VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        instance_id = params.get("InstanceId")
        device = params.get("Device")

        attachment = None
        for item in list(volume.attachment_set or []):
            if instance_id and item.get("instanceId") != instance_id:
                continue
            if device and item.get("device") != device:
                continue
            attachment = item
            volume.attachment_set.remove(item)
            break

        if not attachment:
            return create_error_response(
                "InvalidAttachment.NotFound",
                f"No attachment found for volume '{volume_id}'",
            )

        if instance_id:
            instance = self.state.instances.get(instance_id)
            if instance and hasattr(instance, "volume_ids") and volume_id in instance.volume_ids:
                instance.volume_ids.remove(volume_id)

        if not volume.attachment_set:
            volume.status = "available"

        attachment["status"] = "detached"

        return {
            "associatedResource": attachment.get("associatedResource"),
            "attachTime": attachment.get("attachTime"),
            "deleteOnTermination": attachment.get("deleteOnTermination"),
            "device": attachment.get("device"),
            "instanceId": attachment.get("instanceId"),
            "instanceOwningService": attachment.get("instanceOwningService"),
            "status": attachment.get("status"),
            "volumeId": attachment.get("volumeId"),
        }

    def EnableVolumeIO(self, params: Dict[str, Any]):
        """Enables I/O operations for a volume that had I/O operations disabled because the data on
      the volume was potentially inconsistent."""

        error = self._require_params(params, ["VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        volume.auto_enable_io = True

        return {
            "return": True,
        }

    def ModifyVolume(self, params: Dict[str, Any]):
        """You can modify several parameters of an existing EBS volume, including volume size, volume
      type, and IOPS capacity. If your EBS volume is attached to a current-generation EC2 instance
      type, you might be able to apply these changes without stopping the instance or detaching the
      volu"""

        error = self._require_params(params, ["VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        now = self._utc_now()
        modification = {
            "endTime": now,
            "modificationState": "completed",
            "originalIops": volume.iops,
            "originalMultiAttachEnabled": volume.multi_attach_enabled,
            "originalSize": volume.size,
            "originalThroughput": volume.throughput,
            "originalVolumeType": volume.volume_type,
            "progress": 100,
            "startTime": now,
            "statusMessage": "",
            "targetIops": params.get("Iops") if params.get("Iops") is not None else volume.iops,
            "targetMultiAttachEnabled": str2bool(params.get("MultiAttachEnabled")) if params.get("MultiAttachEnabled") is not None else volume.multi_attach_enabled,
            "targetSize": params.get("Size") if params.get("Size") is not None else volume.size,
            "targetThroughput": params.get("Throughput") if params.get("Throughput") is not None else volume.throughput,
            "targetVolumeType": params.get("VolumeType") or volume.volume_type,
            "volumeId": volume.volume_id,
        }

        volume.iops = modification["targetIops"]
        volume.multi_attach_enabled = modification["targetMultiAttachEnabled"]
        volume.size = modification["targetSize"]
        volume.throughput = modification["targetThroughput"]
        volume.volume_type = modification["targetVolumeType"]
        volume.last_volume_modification = dict(modification)

        return {
            "volumeModification": modification,
        }

    def ModifyVolumeAttribute(self, params: Dict[str, Any]):
        """Modifies a volume attribute. By default, all I/O operations for the volume are suspended when the data on the volume is
      determined to be potentially inconsistent, to prevent undetectable, latent data corruption.
      The I/O access to the volume can be resumed by first enabling I/O access and"""

        error = self._require_params(params, ["VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        auto_enable = params.get("AutoEnableIO")
        if auto_enable is not None:
            if isinstance(auto_enable, dict):
                value = auto_enable.get("Value")
                volume.auto_enable_io = str2bool(value)
            else:
                volume.auto_enable_io = str2bool(auto_enable)

        return {
            "return": True,
        }

    def ListVolumesInRecycleBin(self, params: Dict[str, Any]):
        """Lists one or more volumes that are currently in the Recycle Bin."""

        volume_ids = params.get("VolumeId.N", [])
        if volume_ids:
            resources, error = self._get_resources_by_ids(self.resources, volume_ids, "InvalidVolume.NotFound")
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = [volume for volume in resources if volume.in_recycle_bin]

        max_results = int(params.get("MaxResults") or 100)
        page, next_token = self._paginate(resources, max_results, params.get("NextToken"))

        volume_set = []
        for volume in page:
            volume_set.append({
                "availabilityZone": volume.availability_zone,
                "availabilityZoneId": volume.availability_zone_id,
                "createTime": volume.create_time,
                "iops": volume.iops,
                "operator": volume.operator,
                "outpostArn": volume.outpost_arn,
                "recycleBinEnterTime": volume.recycle_bin_enter_time,
                "recycleBinExitTime": volume.recycle_bin_exit_time,
                "size": volume.size,
                "snapshotId": volume.snapshot_id,
                "sourceVolumeId": volume.source_volume_id,
                "state": volume.status,
                "throughput": volume.throughput,
                "volumeId": volume.volume_id,
                "volumeType": volume.volume_type,
            })

        return {
            "nextToken": next_token,
            "volumeSet": volume_set,
        }

    def RestoreVolumeFromRecycleBin(self, params: Dict[str, Any]):
        """Restores a volume from the Recycle Bin. For more information, seeRestore 
      volumes from the Recycle Binin theAmazon EBS User Guide."""

        error = self._require_params(params, ["VolumeId"])
        if error:
            return error

        volume_id = params.get("VolumeId")
        volume, error = self._get_volume_or_error(volume_id, "InvalidVolume.NotFound")
        if error:
            return error

        if not volume.in_recycle_bin:
            return create_error_response(
                "InvalidVolume.NotFound",
                f"The ID '{volume_id}' does not exist",
            )

        volume.in_recycle_bin = False
        volume.recycle_bin_exit_time = self._utc_now()

        return {
            "return": True,
        }

    def _generate_id(self, prefix: str = 'vol') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class volume_RequestParser:
    @staticmethod
    def parse_attach_volume_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Device": get_scalar(md, "Device"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "VolumeId": get_scalar(md, "VolumeId"),
        }

    @staticmethod
    def parse_copy_volumes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Iops": get_int(md, "Iops"),
            "MultiAttachEnabled": get_scalar(md, "MultiAttachEnabled"),
            "Size": get_int(md, "Size"),
            "SourceVolumeId": get_scalar(md, "SourceVolumeId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Throughput": get_int(md, "Throughput"),
            "VolumeType": get_scalar(md, "VolumeType"),
        }

    @staticmethod
    def parse_create_replace_root_volume_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DeleteReplacedRootVolume": get_scalar(md, "DeleteReplacedRootVolume"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ImageId": get_scalar(md, "ImageId"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "SnapshotId": get_scalar(md, "SnapshotId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VolumeInitializationRate": get_int(md, "VolumeInitializationRate"),
        }

    @staticmethod
    def parse_create_volume_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Encrypted": get_scalar(md, "Encrypted"),
            "Iops": get_int(md, "Iops"),
            "KmsKeyId": get_scalar(md, "KmsKeyId"),
            "MultiAttachEnabled": get_scalar(md, "MultiAttachEnabled"),
            "Operator": get_scalar(md, "Operator"),
            "OutpostArn": get_scalar(md, "OutpostArn"),
            "Size": get_int(md, "Size"),
            "SnapshotId": get_scalar(md, "SnapshotId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Throughput": get_int(md, "Throughput"),
            "VolumeInitializationRate": get_int(md, "VolumeInitializationRate"),
            "VolumeType": get_scalar(md, "VolumeType"),
        }

    @staticmethod
    def parse_delete_volume_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VolumeId": get_scalar(md, "VolumeId"),
        }

    @staticmethod
    def parse_describe_replace_root_volume_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ReplaceRootVolumeTaskId.N": get_indexed_list(md, "ReplaceRootVolumeTaskId"),
        }

    @staticmethod
    def parse_describe_volume_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Attribute": get_scalar(md, "Attribute"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VolumeId": get_scalar(md, "VolumeId"),
        }

    @staticmethod
    def parse_describe_volumes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VolumeId.N": get_indexed_list(md, "VolumeId"),
        }

    @staticmethod
    def parse_describe_volumes_modifications_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VolumeId.N": get_indexed_list(md, "VolumeId"),
        }

    @staticmethod
    def parse_describe_volume_status_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VolumeId.N": get_indexed_list(md, "VolumeId"),
        }

    @staticmethod
    def parse_detach_volume_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Device": get_scalar(md, "Device"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Force": get_scalar(md, "Force"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "VolumeId": get_scalar(md, "VolumeId"),
        }

    @staticmethod
    def parse_enable_volume_i_o_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VolumeId": get_scalar(md, "VolumeId"),
        }

    @staticmethod
    def parse_modify_volume_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Iops": get_int(md, "Iops"),
            "MultiAttachEnabled": get_scalar(md, "MultiAttachEnabled"),
            "Size": get_int(md, "Size"),
            "Throughput": get_int(md, "Throughput"),
            "VolumeId": get_scalar(md, "VolumeId"),
            "VolumeType": get_scalar(md, "VolumeType"),
        }

    @staticmethod
    def parse_modify_volume_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AutoEnableIO": get_scalar(md, "AutoEnableIO"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VolumeId": get_scalar(md, "VolumeId"),
        }

    @staticmethod
    def parse_list_volumes_in_recycle_bin_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VolumeId.N": get_indexed_list(md, "VolumeId"),
        }

    @staticmethod
    def parse_restore_volume_from_recycle_bin_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VolumeId": get_scalar(md, "VolumeId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AttachVolume": volume_RequestParser.parse_attach_volume_request,
            "CopyVolumes": volume_RequestParser.parse_copy_volumes_request,
            "CreateReplaceRootVolumeTask": volume_RequestParser.parse_create_replace_root_volume_task_request,
            "CreateVolume": volume_RequestParser.parse_create_volume_request,
            "DeleteVolume": volume_RequestParser.parse_delete_volume_request,
            "DescribeReplaceRootVolumeTasks": volume_RequestParser.parse_describe_replace_root_volume_tasks_request,
            "DescribeVolumeAttribute": volume_RequestParser.parse_describe_volume_attribute_request,
            "DescribeVolumes": volume_RequestParser.parse_describe_volumes_request,
            "DescribeVolumesModifications": volume_RequestParser.parse_describe_volumes_modifications_request,
            "DescribeVolumeStatus": volume_RequestParser.parse_describe_volume_status_request,
            "DetachVolume": volume_RequestParser.parse_detach_volume_request,
            "EnableVolumeIO": volume_RequestParser.parse_enable_volume_i_o_request,
            "ModifyVolume": volume_RequestParser.parse_modify_volume_request,
            "ModifyVolumeAttribute": volume_RequestParser.parse_modify_volume_attribute_request,
            "ListVolumesInRecycleBin": volume_RequestParser.parse_list_volumes_in_recycle_bin_request,
            "RestoreVolumeFromRecycleBin": volume_RequestParser.parse_restore_volume_from_recycle_bin_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class volume_ResponseSerializer:
    @staticmethod
    def _serialize_dict_to_xml(d: Dict[str, Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a dictionary to XML elements."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(volume_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(volume_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def _serialize_list_to_xml(lst: List[Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a list to XML elements with <tagName> wrapper and <item> children."""
        xml_parts = []
        indent = '    ' * indent_level
        xml_parts.append(f'{indent}<{tag_name}>')
        for item in lst:
            if isinstance(item, dict):
                xml_parts.append(f'{indent}    <item>')
                xml_parts.extend(volume_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(volume_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
            else:
                xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
        xml_parts.append(f'{indent}</{tag_name}>')
        return xml_parts

    @staticmethod
    def _serialize_nested_fields(d: Dict[str, Any], indent_level: int) -> List[str]:
        """Serialize nested fields from a dictionary."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
                        xml_parts.append(f'{indent}    </item>')
                    else:
                        xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def serialize_attach_volume_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AttachVolumeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associatedResource
        _associatedResource_key = None
        if "associatedResource" in data:
            _associatedResource_key = "associatedResource"
        elif "AssociatedResource" in data:
            _associatedResource_key = "AssociatedResource"
        if _associatedResource_key:
            param_data = data[_associatedResource_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associatedResource>{esc(str(param_data))}</associatedResource>')
        # Serialize attachTime
        _attachTime_key = None
        if "attachTime" in data:
            _attachTime_key = "attachTime"
        elif "AttachTime" in data:
            _attachTime_key = "AttachTime"
        if _attachTime_key:
            param_data = data[_attachTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<attachTime>{esc(str(param_data))}</attachTime>')
        # Serialize deleteOnTermination
        _deleteOnTermination_key = None
        if "deleteOnTermination" in data:
            _deleteOnTermination_key = "deleteOnTermination"
        elif "DeleteOnTermination" in data:
            _deleteOnTermination_key = "DeleteOnTermination"
        if _deleteOnTermination_key:
            param_data = data[_deleteOnTermination_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<deleteOnTermination>{esc(str(param_data))}</deleteOnTermination>')
        # Serialize device
        _device_key = None
        if "device" in data:
            _device_key = "device"
        elif "Device" in data:
            _device_key = "Device"
        if _device_key:
            param_data = data[_device_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<device>{esc(str(param_data))}</device>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize instanceOwningService
        _instanceOwningService_key = None
        if "instanceOwningService" in data:
            _instanceOwningService_key = "instanceOwningService"
        elif "InstanceOwningService" in data:
            _instanceOwningService_key = "InstanceOwningService"
        if _instanceOwningService_key:
            param_data = data[_instanceOwningService_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceOwningService>{esc(str(param_data))}</instanceOwningService>')
        # Serialize status
        _status_key = None
        if "status" in data:
            _status_key = "status"
        elif "Status" in data:
            _status_key = "Status"
        if _status_key:
            param_data = data[_status_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        # Serialize volumeId
        _volumeId_key = None
        if "volumeId" in data:
            _volumeId_key = "volumeId"
        elif "VolumeId" in data:
            _volumeId_key = "VolumeId"
        if _volumeId_key:
            param_data = data[_volumeId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<volumeId>{esc(str(param_data))}</volumeId>')
        xml_parts.append(f'</AttachVolumeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_copy_volumes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CopyVolumesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize volumeSet
        _volumeSet_key = None
        if "volumeSet" in data:
            _volumeSet_key = "volumeSet"
        elif "VolumeSet" in data:
            _volumeSet_key = "VolumeSet"
        elif "Volumes" in data:
            _volumeSet_key = "Volumes"
        if _volumeSet_key:
            param_data = data[_volumeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<volumeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</volumeSet>')
            else:
                xml_parts.append(f'{indent_str}<volumeSet/>')
        xml_parts.append(f'</CopyVolumesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_replace_root_volume_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateReplaceRootVolumeTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize replaceRootVolumeTask
        _replaceRootVolumeTask_key = None
        if "replaceRootVolumeTask" in data:
            _replaceRootVolumeTask_key = "replaceRootVolumeTask"
        elif "ReplaceRootVolumeTask" in data:
            _replaceRootVolumeTask_key = "ReplaceRootVolumeTask"
        if _replaceRootVolumeTask_key:
            param_data = data[_replaceRootVolumeTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<replaceRootVolumeTask>')
            xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</replaceRootVolumeTask>')
        xml_parts.append(f'</CreateReplaceRootVolumeTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_volume_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVolumeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize attachmentSet
        _attachmentSet_key = None
        if "attachmentSet" in data:
            _attachmentSet_key = "attachmentSet"
        elif "AttachmentSet" in data:
            _attachmentSet_key = "AttachmentSet"
        elif "Attachments" in data:
            _attachmentSet_key = "Attachments"
        if _attachmentSet_key:
            param_data = data[_attachmentSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<attachmentSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</attachmentSet>')
            else:
                xml_parts.append(f'{indent_str}<attachmentSet/>')
        # Serialize availabilityZone
        _availabilityZone_key = None
        if "availabilityZone" in data:
            _availabilityZone_key = "availabilityZone"
        elif "AvailabilityZone" in data:
            _availabilityZone_key = "AvailabilityZone"
        if _availabilityZone_key:
            param_data = data[_availabilityZone_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<availabilityZone>{esc(str(param_data))}</availabilityZone>')
        # Serialize availabilityZoneId
        _availabilityZoneId_key = None
        if "availabilityZoneId" in data:
            _availabilityZoneId_key = "availabilityZoneId"
        elif "AvailabilityZoneId" in data:
            _availabilityZoneId_key = "AvailabilityZoneId"
        if _availabilityZoneId_key:
            param_data = data[_availabilityZoneId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<availabilityZoneId>{esc(str(param_data))}</availabilityZoneId>')
        # Serialize createTime
        _createTime_key = None
        if "createTime" in data:
            _createTime_key = "createTime"
        elif "CreateTime" in data:
            _createTime_key = "CreateTime"
        if _createTime_key:
            param_data = data[_createTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<createTime>{esc(str(param_data))}</createTime>')
        # Serialize encrypted
        _encrypted_key = None
        if "encrypted" in data:
            _encrypted_key = "encrypted"
        elif "Encrypted" in data:
            _encrypted_key = "Encrypted"
        if _encrypted_key:
            param_data = data[_encrypted_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<encrypted>{esc(str(param_data))}</encrypted>')
        # Serialize fastRestored
        _fastRestored_key = None
        if "fastRestored" in data:
            _fastRestored_key = "fastRestored"
        elif "FastRestored" in data:
            _fastRestored_key = "FastRestored"
        if _fastRestored_key:
            param_data = data[_fastRestored_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fastRestored>{esc(str(param_data))}</fastRestored>')
        # Serialize iops
        _iops_key = None
        if "iops" in data:
            _iops_key = "iops"
        elif "Iops" in data:
            _iops_key = "Iops"
        if _iops_key:
            param_data = data[_iops_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<iopsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</iopsSet>')
            else:
                xml_parts.append(f'{indent_str}<iopsSet/>')
        # Serialize kmsKeyId
        _kmsKeyId_key = None
        if "kmsKeyId" in data:
            _kmsKeyId_key = "kmsKeyId"
        elif "KmsKeyId" in data:
            _kmsKeyId_key = "KmsKeyId"
        if _kmsKeyId_key:
            param_data = data[_kmsKeyId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<kmsKeyId>{esc(str(param_data))}</kmsKeyId>')
        # Serialize multiAttachEnabled
        _multiAttachEnabled_key = None
        if "multiAttachEnabled" in data:
            _multiAttachEnabled_key = "multiAttachEnabled"
        elif "MultiAttachEnabled" in data:
            _multiAttachEnabled_key = "MultiAttachEnabled"
        if _multiAttachEnabled_key:
            param_data = data[_multiAttachEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<multiAttachEnabled>{esc(str(param_data))}</multiAttachEnabled>')
        # Serialize operator
        _operator_key = None
        if "operator" in data:
            _operator_key = "operator"
        elif "Operator" in data:
            _operator_key = "Operator"
        if _operator_key:
            param_data = data[_operator_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<operator>')
            xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</operator>')
        # Serialize outpostArn
        _outpostArn_key = None
        if "outpostArn" in data:
            _outpostArn_key = "outpostArn"
        elif "OutpostArn" in data:
            _outpostArn_key = "OutpostArn"
        if _outpostArn_key:
            param_data = data[_outpostArn_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<outpostArn>{esc(str(param_data))}</outpostArn>')
        # Serialize size
        _size_key = None
        if "size" in data:
            _size_key = "size"
        elif "Size" in data:
            _size_key = "Size"
        if _size_key:
            param_data = data[_size_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<size>{esc(str(param_data))}</size>')
        # Serialize snapshotId
        _snapshotId_key = None
        if "snapshotId" in data:
            _snapshotId_key = "snapshotId"
        elif "SnapshotId" in data:
            _snapshotId_key = "SnapshotId"
        if _snapshotId_key:
            param_data = data[_snapshotId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<snapshotId>{esc(str(param_data))}</snapshotId>')
        # Serialize sourceVolumeId
        _sourceVolumeId_key = None
        if "sourceVolumeId" in data:
            _sourceVolumeId_key = "sourceVolumeId"
        elif "SourceVolumeId" in data:
            _sourceVolumeId_key = "SourceVolumeId"
        if _sourceVolumeId_key:
            param_data = data[_sourceVolumeId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sourceVolumeId>{esc(str(param_data))}</sourceVolumeId>')
        # Serialize sseType
        _sseType_key = None
        if "sseType" in data:
            _sseType_key = "sseType"
        elif "SseType" in data:
            _sseType_key = "SseType"
        if _sseType_key:
            param_data = data[_sseType_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sseType>{esc(str(param_data))}</sseType>')
        # Serialize status
        _status_key = None
        if "status" in data:
            _status_key = "status"
        elif "Status" in data:
            _status_key = "Status"
        if _status_key:
            param_data = data[_status_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        # Serialize tagSet
        _tagSet_key = None
        if "tagSet" in data:
            _tagSet_key = "tagSet"
        elif "TagSet" in data:
            _tagSet_key = "TagSet"
        elif "Tags" in data:
            _tagSet_key = "Tags"
        if _tagSet_key:
            param_data = data[_tagSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<tagSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        # Serialize throughput
        _throughput_key = None
        if "throughput" in data:
            _throughput_key = "throughput"
        elif "Throughput" in data:
            _throughput_key = "Throughput"
        if _throughput_key:
            param_data = data[_throughput_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<throughput>{esc(str(param_data))}</throughput>')
        # Serialize volumeId
        _volumeId_key = None
        if "volumeId" in data:
            _volumeId_key = "volumeId"
        elif "VolumeId" in data:
            _volumeId_key = "VolumeId"
        if _volumeId_key:
            param_data = data[_volumeId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<volumeId>{esc(str(param_data))}</volumeId>')
        # Serialize volumeInitializationRate
        _volumeInitializationRate_key = None
        if "volumeInitializationRate" in data:
            _volumeInitializationRate_key = "volumeInitializationRate"
        elif "VolumeInitializationRate" in data:
            _volumeInitializationRate_key = "VolumeInitializationRate"
        if _volumeInitializationRate_key:
            param_data = data[_volumeInitializationRate_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<volumeInitializationRate>{esc(str(param_data))}</volumeInitializationRate>')
        # Serialize volumeType
        _volumeType_key = None
        if "volumeType" in data:
            _volumeType_key = "volumeType"
        elif "VolumeType" in data:
            _volumeType_key = "VolumeType"
        if _volumeType_key:
            param_data = data[_volumeType_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<volumeType>{esc(str(param_data))}</volumeType>')
        xml_parts.append(f'</CreateVolumeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_volume_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVolumeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</DeleteVolumeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_replace_root_volume_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeReplaceRootVolumeTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize replaceRootVolumeTaskSet
        _replaceRootVolumeTaskSet_key = None
        if "replaceRootVolumeTaskSet" in data:
            _replaceRootVolumeTaskSet_key = "replaceRootVolumeTaskSet"
        elif "ReplaceRootVolumeTaskSet" in data:
            _replaceRootVolumeTaskSet_key = "ReplaceRootVolumeTaskSet"
        elif "ReplaceRootVolumeTasks" in data:
            _replaceRootVolumeTaskSet_key = "ReplaceRootVolumeTasks"
        if _replaceRootVolumeTaskSet_key:
            param_data = data[_replaceRootVolumeTaskSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<replaceRootVolumeTaskSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</replaceRootVolumeTaskSet>')
            else:
                xml_parts.append(f'{indent_str}<replaceRootVolumeTaskSet/>')
        xml_parts.append(f'</DescribeReplaceRootVolumeTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_volume_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVolumeAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize autoEnableIO
        _autoEnableIO_key = None
        if "autoEnableIO" in data:
            _autoEnableIO_key = "autoEnableIO"
        elif "AutoEnableIO" in data:
            _autoEnableIO_key = "AutoEnableIO"
        if _autoEnableIO_key:
            param_data = data[_autoEnableIO_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<autoEnableIO>')
            xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</autoEnableIO>')
        # Serialize productCodes
        _productCodes_key = None
        if "productCodes" in data:
            _productCodes_key = "productCodes"
        elif "ProductCodes" in data:
            _productCodes_key = "ProductCodes"
        if _productCodes_key:
            param_data = data[_productCodes_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<productCodesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</productCodesSet>')
            else:
                xml_parts.append(f'{indent_str}<productCodesSet/>')
        # Serialize volumeId
        _volumeId_key = None
        if "volumeId" in data:
            _volumeId_key = "volumeId"
        elif "VolumeId" in data:
            _volumeId_key = "VolumeId"
        if _volumeId_key:
            param_data = data[_volumeId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<volumeId>{esc(str(param_data))}</volumeId>')
        xml_parts.append(f'</DescribeVolumeAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_volumes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVolumesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize volumeSet
        _volumeSet_key = None
        if "volumeSet" in data:
            _volumeSet_key = "volumeSet"
        elif "VolumeSet" in data:
            _volumeSet_key = "VolumeSet"
        elif "Volumes" in data:
            _volumeSet_key = "Volumes"
        if _volumeSet_key:
            param_data = data[_volumeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<volumeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</volumeSet>')
            else:
                xml_parts.append(f'{indent_str}<volumeSet/>')
        xml_parts.append(f'</DescribeVolumesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_volumes_modifications_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVolumesModificationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize volumeModificationSet
        _volumeModificationSet_key = None
        if "volumeModificationSet" in data:
            _volumeModificationSet_key = "volumeModificationSet"
        elif "VolumeModificationSet" in data:
            _volumeModificationSet_key = "VolumeModificationSet"
        elif "VolumeModifications" in data:
            _volumeModificationSet_key = "VolumeModifications"
        if _volumeModificationSet_key:
            param_data = data[_volumeModificationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<volumeModificationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</volumeModificationSet>')
            else:
                xml_parts.append(f'{indent_str}<volumeModificationSet/>')
        xml_parts.append(f'</DescribeVolumesModificationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_volume_status_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVolumeStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize volumeStatusSet
        _volumeStatusSet_key = None
        if "volumeStatusSet" in data:
            _volumeStatusSet_key = "volumeStatusSet"
        elif "VolumeStatusSet" in data:
            _volumeStatusSet_key = "VolumeStatusSet"
        elif "VolumeStatuss" in data:
            _volumeStatusSet_key = "VolumeStatuss"
        if _volumeStatusSet_key:
            param_data = data[_volumeStatusSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<volumeStatusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</volumeStatusSet>')
            else:
                xml_parts.append(f'{indent_str}<volumeStatusSet/>')
        xml_parts.append(f'</DescribeVolumeStatusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_detach_volume_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DetachVolumeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associatedResource
        _associatedResource_key = None
        if "associatedResource" in data:
            _associatedResource_key = "associatedResource"
        elif "AssociatedResource" in data:
            _associatedResource_key = "AssociatedResource"
        if _associatedResource_key:
            param_data = data[_associatedResource_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associatedResource>{esc(str(param_data))}</associatedResource>')
        # Serialize attachTime
        _attachTime_key = None
        if "attachTime" in data:
            _attachTime_key = "attachTime"
        elif "AttachTime" in data:
            _attachTime_key = "AttachTime"
        if _attachTime_key:
            param_data = data[_attachTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<attachTime>{esc(str(param_data))}</attachTime>')
        # Serialize deleteOnTermination
        _deleteOnTermination_key = None
        if "deleteOnTermination" in data:
            _deleteOnTermination_key = "deleteOnTermination"
        elif "DeleteOnTermination" in data:
            _deleteOnTermination_key = "DeleteOnTermination"
        if _deleteOnTermination_key:
            param_data = data[_deleteOnTermination_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<deleteOnTermination>{esc(str(param_data))}</deleteOnTermination>')
        # Serialize device
        _device_key = None
        if "device" in data:
            _device_key = "device"
        elif "Device" in data:
            _device_key = "Device"
        if _device_key:
            param_data = data[_device_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<device>{esc(str(param_data))}</device>')
        # Serialize instanceId
        _instanceId_key = None
        if "instanceId" in data:
            _instanceId_key = "instanceId"
        elif "InstanceId" in data:
            _instanceId_key = "InstanceId"
        if _instanceId_key:
            param_data = data[_instanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceId>{esc(str(param_data))}</instanceId>')
        # Serialize instanceOwningService
        _instanceOwningService_key = None
        if "instanceOwningService" in data:
            _instanceOwningService_key = "instanceOwningService"
        elif "InstanceOwningService" in data:
            _instanceOwningService_key = "InstanceOwningService"
        if _instanceOwningService_key:
            param_data = data[_instanceOwningService_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceOwningService>{esc(str(param_data))}</instanceOwningService>')
        # Serialize status
        _status_key = None
        if "status" in data:
            _status_key = "status"
        elif "Status" in data:
            _status_key = "Status"
        if _status_key:
            param_data = data[_status_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        # Serialize volumeId
        _volumeId_key = None
        if "volumeId" in data:
            _volumeId_key = "volumeId"
        elif "VolumeId" in data:
            _volumeId_key = "VolumeId"
        if _volumeId_key:
            param_data = data[_volumeId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<volumeId>{esc(str(param_data))}</volumeId>')
        xml_parts.append(f'</DetachVolumeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_volume_i_o_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableVolumeIOResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</EnableVolumeIOResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_volume_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVolumeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize volumeModification
        _volumeModification_key = None
        if "volumeModification" in data:
            _volumeModification_key = "volumeModification"
        elif "VolumeModification" in data:
            _volumeModification_key = "VolumeModification"
        if _volumeModification_key:
            param_data = data[_volumeModification_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<volumeModification>')
            xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</volumeModification>')
        xml_parts.append(f'</ModifyVolumeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_volume_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVolumeAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</ModifyVolumeAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_list_volumes_in_recycle_bin_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ListVolumesInRecycleBinResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize volumeSet
        _volumeSet_key = None
        if "volumeSet" in data:
            _volumeSet_key = "volumeSet"
        elif "VolumeSet" in data:
            _volumeSet_key = "VolumeSet"
        elif "Volumes" in data:
            _volumeSet_key = "Volumes"
        if _volumeSet_key:
            param_data = data[_volumeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<volumeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(volume_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</volumeSet>')
            else:
                xml_parts.append(f'{indent_str}<volumeSet/>')
        xml_parts.append(f'</ListVolumesInRecycleBinResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_restore_volume_from_recycle_bin_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RestoreVolumeFromRecycleBinResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</RestoreVolumeFromRecycleBinResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AttachVolume": volume_ResponseSerializer.serialize_attach_volume_response,
            "CopyVolumes": volume_ResponseSerializer.serialize_copy_volumes_response,
            "CreateReplaceRootVolumeTask": volume_ResponseSerializer.serialize_create_replace_root_volume_task_response,
            "CreateVolume": volume_ResponseSerializer.serialize_create_volume_response,
            "DeleteVolume": volume_ResponseSerializer.serialize_delete_volume_response,
            "DescribeReplaceRootVolumeTasks": volume_ResponseSerializer.serialize_describe_replace_root_volume_tasks_response,
            "DescribeVolumeAttribute": volume_ResponseSerializer.serialize_describe_volume_attribute_response,
            "DescribeVolumes": volume_ResponseSerializer.serialize_describe_volumes_response,
            "DescribeVolumesModifications": volume_ResponseSerializer.serialize_describe_volumes_modifications_response,
            "DescribeVolumeStatus": volume_ResponseSerializer.serialize_describe_volume_status_response,
            "DetachVolume": volume_ResponseSerializer.serialize_detach_volume_response,
            "EnableVolumeIO": volume_ResponseSerializer.serialize_enable_volume_i_o_response,
            "ModifyVolume": volume_ResponseSerializer.serialize_modify_volume_response,
            "ModifyVolumeAttribute": volume_ResponseSerializer.serialize_modify_volume_attribute_response,
            "ListVolumesInRecycleBin": volume_ResponseSerializer.serialize_list_volumes_in_recycle_bin_response,
            "RestoreVolumeFromRecycleBin": volume_ResponseSerializer.serialize_restore_volume_from_recycle_bin_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

