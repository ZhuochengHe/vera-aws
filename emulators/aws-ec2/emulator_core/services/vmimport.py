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
class VmImport:
    conversion_task_id: str = ""
    expiration_time: str = ""
    import_instance: Dict[str, Any] = field(default_factory=dict)
    import_volume: Dict[str, Any] = field(default_factory=dict)
    state: str = ""
    status_message: str = ""
    tag_set: List[Any] = field(default_factory=list)
    task_type: str = ""
    import_task_id: str = ""
    description: str = ""
    architecture: str = ""
    boot_mode: str = ""
    client_data: str = ""
    client_token: str = ""
    encrypted: Optional[bool] = None
    hypervisor: str = ""
    image_id: str = ""
    kms_key_id: str = ""
    license_specifications: List[Dict[str, Any]] = field(default_factory=list)
    license_type: str = ""
    platform: str = ""
    progress: str = ""
    snapshot_detail_set: List[Dict[str, Any]] = field(default_factory=list)
    snapshot_task_detail: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    usage_operation: str = ""
    previous_state: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversionTaskId": self.conversion_task_id,
            "expirationTime": self.expiration_time,
            "importInstance": self.import_instance,
            "importVolume": self.import_volume,
            "state": self.state,
            "statusMessage": self.status_message,
            "tagSet": self.tag_set,
            "taskType": self.task_type,
            "importTaskId": self.import_task_id,
            "description": self.description,
            "architecture": self.architecture,
            "bootMode": self.boot_mode,
            "clientData": self.client_data,
            "clientToken": self.client_token,
            "encrypted": self.encrypted,
            "hypervisor": self.hypervisor,
            "imageId": self.image_id,
            "kmsKeyId": self.kms_key_id,
            "licenseSpecifications": self.license_specifications,
            "licenseType": self.license_type,
            "platform": self.platform,
            "progress": self.progress,
            "snapshotDetailSet": self.snapshot_detail_set,
            "snapshotTaskDetail": self.snapshot_task_detail,
            "status": self.status,
            "usageOperation": self.usage_operation,
            "previousState": self.previous_state,
        }

class VmImport_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.vm_import  # alias to shared store

    def _require_param(self, params: Dict[str, Any], name: str):
        value = params.get(name)
        if value is None or value == "" or value == []:
            return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource(self, resource_id: str, error_code: str, message: Optional[str] = None):
        resource = self.resources.get(resource_id)
        if not resource:
            error_message = message or f"The ID '{resource_id}' does not exist"
            return None, create_error_response(error_code, error_message)
        return resource, None

    def CancelConversionTask(self, params: Dict[str, Any]):
        """Cancels an active conversion task. The task can be the import of an instance or volume. The action removes all
   artifacts of the conversion, including a partially uploaded volume or instance. If the conversion is complete or is
   in the process of transferring the final disk image, the command fa"""

        error = self._require_param(params, "ConversionTaskId")
        if error:
            return error

        conversion_task_id = params.get("ConversionTaskId")
        resource, error = self._get_resource(conversion_task_id, "InvalidConversionTaskId.NotFound")
        if error:
            return error

        resource.previous_state = resource.state
        resource.state = "cancelled"
        resource.status_message = params.get("ReasonMessage") or resource.status_message
        self.resources.pop(conversion_task_id, None)

        return {
            'return': True,
            }

    def CancelImportTask(self, params: Dict[str, Any]):
        """Cancels an in-process import virtual machine or import snapshot task."""

        import_task_id = params.get("ImportTaskId")
        if import_task_id:
            resource, error = self._get_resource(import_task_id, "InvalidImportTaskId.NotFound")
            if error:
                return error
        else:
            resource = next(iter(self.resources.values()), None)
            if not resource:
                return create_error_response("InvalidImportTaskId.NotFound", "The ID '' does not exist")

        previous_state = resource.state
        resource.previous_state = previous_state
        resource.state = "cancelled"
        resource.status_message = params.get("CancelReason") or resource.status_message
        self.resources.pop(resource.conversion_task_id, None)

        return {
            'importTaskId': resource.import_task_id or resource.conversion_task_id,
            'previousState': previous_state or None,
            'state': resource.state or None,
            }

    def DescribeConversionTasks(self, params: Dict[str, Any]):
        """Describes the specified conversion tasks or all your conversion tasks. For more information, see theVM Import/Export User Guide. For information about the import manifest referenced by this API action, seeVM Import Manifest."""

        conversion_task_ids = params.get("ConversionTaskId.N", []) or []
        if conversion_task_ids:
            resources: List[VmImport] = []
            for conversion_task_id in conversion_task_ids:
                resource, error = self._get_resource(conversion_task_id, "InvalidConversionTaskId.NotFound")
                if error:
                    return error
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        conversion_tasks = []
        for resource in resources:
            conversion_tasks.append({
                "conversionTaskId": resource.conversion_task_id,
                "expirationTime": resource.expiration_time,
                "importInstance": resource.import_instance,
                "importVolume": resource.import_volume,
                "state": resource.state,
                "statusMessage": resource.status_message,
                "tagSet": resource.tag_set,
            })

        return {
            'conversionTasks': conversion_tasks,
            }

    def DescribeImportImageTasks(self, params: Dict[str, Any]):
        """Displays details about an import virtual machine or import snapshot tasks that are already created."""

        import_task_ids = params.get("ImportTaskId.N", []) or []
        if import_task_ids:
            resources: List[VmImport] = []
            for import_task_id in import_task_ids:
                resource, error = self._get_resource(import_task_id, "InvalidImportTaskId.NotFound")
                if error:
                    return error
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = [resource for resource in resources if resource.task_type == "image"]
        filtered = apply_filters(resources, params.get("Filters.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except ValueError:
                start_index = 0
        paged = filtered[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(filtered):
            new_next_token = str(start_index + max_results)

        import_image_task_set = []
        for resource in paged:
            import_image_task_set.append({
                "architecture": resource.architecture,
                "bootMode": resource.boot_mode,
                "description": resource.description,
                "encrypted": resource.encrypted,
                "hypervisor": resource.hypervisor,
                "imageId": resource.image_id,
                "importTaskId": resource.import_task_id,
                "kmsKeyId": resource.kms_key_id,
                "licenseSpecifications": resource.license_specifications,
                "licenseType": resource.license_type,
                "platform": resource.platform,
                "progress": resource.progress,
                "snapshotDetailSet": resource.snapshot_detail_set,
                "status": resource.status,
                "statusMessage": resource.status_message,
                "tagSet": resource.tag_set,
                "usageOperation": resource.usage_operation,
            })

        return {
            'importImageTaskSet': import_image_task_set,
            'nextToken': new_next_token,
            }

    def DescribeImportSnapshotTasks(self, params: Dict[str, Any]):
        """Describes your import snapshot tasks."""

        import_task_ids = params.get("ImportTaskId.N", []) or []
        if import_task_ids:
            resources: List[VmImport] = []
            for import_task_id in import_task_ids:
                resource, error = self._get_resource(import_task_id, "InvalidImportTaskId.NotFound")
                if error:
                    return error
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = [resource for resource in resources if resource.task_type == "snapshot"]
        filtered = apply_filters(resources, params.get("Filters.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except ValueError:
                start_index = 0
        paged = filtered[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(filtered):
            new_next_token = str(start_index + max_results)

        import_snapshot_task_set = []
        for resource in paged:
            import_snapshot_task_set.append({
                "description": resource.description,
                "importTaskId": resource.import_task_id,
                "snapshotTaskDetail": resource.snapshot_task_detail,
                "tagSet": resource.tag_set,
            })

        return {
            'importSnapshotTaskSet': import_snapshot_task_set,
            'nextToken': new_next_token,
            }

    def ImportImage(self, params: Dict[str, Any]):
        """To import your virtual machines (VMs) with a console-based experience, you can use theImport virtual machine images to AWStemplate in theMigration Hub Orchestrator console. For more
    information, see theAWS Migration Hub Orchestrator User Guide. Import single or multi-volume disk images or EBS sn"""

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "image":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        import_task_id = self._generate_id("conversion")
        image_id = self._generate_id("ami")
        encrypted_value = None
        if params.get("Encrypted") is not None:
            encrypted_value = str2bool(params.get("Encrypted"))

        snapshot_detail_set: List[Dict[str, Any]] = []
        for container in params.get("DiskContainer.N", []) or []:
            snapshot_detail_set.append({
                "description": container.get("Description"),
                "deviceName": container.get("DeviceName"),
                "diskImageSize": container.get("DiskImageSize"),
                "format": container.get("Format"),
                "progress": "0",
                "snapshotId": self._generate_id("snap"),
                "status": "active",
                "statusMessage": "",
                "url": container.get("Url") or container.get("URL"),
                "userBucket": container.get("UserBucket") or {},
            })

        resource = VmImport(
            conversion_task_id=import_task_id,
            import_task_id=import_task_id,
            expiration_time="",
            import_instance={},
            import_volume={},
            state="active",
            status_message="",
            tag_set=tag_set,
        )
        resource.task_type = "image"
        resource.architecture = params.get("Architecture") or ""
        resource.boot_mode = params.get("BootMode") or ""
        resource.client_data = params.get("ClientData") or ""
        resource.client_token = params.get("ClientToken") or ""
        resource.description = params.get("Description") or ""
        resource.encrypted = encrypted_value
        resource.hypervisor = params.get("Hypervisor") or ""
        resource.image_id = image_id
        resource.kms_key_id = params.get("KmsKeyId") or ""
        resource.license_specifications = params.get("LicenseSpecifications.N", []) or []
        resource.license_type = params.get("LicenseType") or ""
        resource.platform = params.get("Platform") or ""
        resource.progress = "0"
        resource.snapshot_detail_set = snapshot_detail_set
        resource.status = "active"
        resource.usage_operation = params.get("UsageOperation") or ""

        self.resources[import_task_id] = resource

        return {
            'architecture': resource.architecture or None,
            'description': resource.description or None,
            'encrypted': resource.encrypted,
            'hypervisor': resource.hypervisor or None,
            'imageId': resource.image_id or None,
            'importTaskId': resource.import_task_id or None,
            'kmsKeyId': resource.kms_key_id or None,
            'licenseSpecifications': resource.license_specifications or [],
            'licenseType': resource.license_type or None,
            'platform': resource.platform or None,
            'progress': resource.progress or None,
            'snapshotDetailSet': resource.snapshot_detail_set or [],
            'status': resource.status or None,
            'statusMessage': resource.status_message or None,
            'tagSet': resource.tag_set or [],
            'usageOperation': resource.usage_operation or None,
            }

    def ImportInstance(self, params: Dict[str, Any]):
        """We recommend that you use theImportImageAPI instead. For more information, seeImporting a VM as an image using VM
     Import/Exportin theVM Import/Export User Guide. Creates an import instance task using metadata from the specified disk image. This API action supports only single-volume VMs. To imp"""

        error = self._require_param(params, "Platform")
        if error:
            return error

        conversion_task_id = self._generate_id("conversion")
        expiration_time = datetime.now(timezone.utc).isoformat()
        disk_images = params.get("DiskImage.N", []) or []

        volumes: List[Dict[str, Any]] = []
        for disk_image in disk_images:
            volume_info = {
                "id": self._generate_id("vol"),
                "size": disk_image.get("Size") or disk_image.get("size"),
            }
            volumes.append({
                "availabilityZone": disk_image.get("AvailabilityZone"),
                "availabilityZoneId": disk_image.get("AvailabilityZoneId"),
                "bytesConverted": disk_image.get("BytesConverted"),
                "description": disk_image.get("Description") or params.get("Description"),
                "image": disk_image.get("Image") or disk_image,
                "status": disk_image.get("Status") or "active",
                "statusMessage": disk_image.get("StatusMessage") or "",
                "volume": volume_info,
            })

        import_instance = {
            "description": params.get("Description") or "",
            "instanceId": self._generate_id("i"),
            "platform": params.get("Platform") or "",
            "volumes": volumes,
        }
        import_volume = {
            "availabilityZone": None,
            "availabilityZoneId": None,
            "bytesConverted": None,
            "description": None,
            "image": {
                "checksum": None,
                "format": None,
                "importManifestUrl": None,
                "size": None,
            },
            "volume": {
                "id": None,
                "size": None,
            },
        }

        resource = VmImport(
            conversion_task_id=conversion_task_id,
            expiration_time=expiration_time,
            import_instance=import_instance,
            import_volume=import_volume,
            state="active",
            status_message="",
            tag_set=[],
        )
        resource.task_type = "instance"
        resource.description = params.get("Description") or ""
        resource.platform = params.get("Platform") or ""

        self.resources[conversion_task_id] = resource

        return {
            'conversionTask': {
                'conversionTaskId': resource.conversion_task_id or None,
                'expirationTime': resource.expiration_time or None,
                'importInstance': {
                    'description': resource.import_instance.get("description") or None,
                    'instanceId': resource.import_instance.get("instanceId") or None,
                    'platform': resource.import_instance.get("platform") or None,
                    'volumes': resource.import_instance.get("volumes") or [],
                    },
                'importVolume': {
                    'availabilityZone': resource.import_volume.get("availabilityZone"),
                    'availabilityZoneId': resource.import_volume.get("availabilityZoneId"),
                    'bytesConverted': resource.import_volume.get("bytesConverted"),
                    'description': resource.import_volume.get("description"),
                    'image': {
                        'checksum': resource.import_volume.get("image", {}).get("checksum"),
                        'format': resource.import_volume.get("image", {}).get("format"),
                        'importManifestUrl': resource.import_volume.get("image", {}).get("importManifestUrl"),
                        'size': resource.import_volume.get("image", {}).get("size"),
                        },
                    'volume': {
                        'id': resource.import_volume.get("volume", {}).get("id"),
                        'size': resource.import_volume.get("volume", {}).get("size"),
                        },
                    },
                'state': resource.state or None,
                'statusMessage': resource.status_message or None,
                'tagSet': resource.tag_set or [],
                },
            }

    def ImportSnapshot(self, params: Dict[str, Any]):
        """Imports a disk into an EBS snapshot. For more information, seeImporting a disk as a snapshot using VM Import/Exportin theVM Import/Export User Guide."""

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "snapshot":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        import_task_id = self._generate_id("conversion")
        snapshot_id = self._generate_id("snap")
        disk_container = params.get("DiskContainer") or {}
        encrypted_value = None
        if params.get("Encrypted") is not None:
            encrypted_value = str2bool(params.get("Encrypted"))

        snapshot_task_detail = {
            "description": params.get("Description") or disk_container.get("Description"),
            "diskImageSize": disk_container.get("DiskImageSize"),
            "encrypted": encrypted_value,
            "format": disk_container.get("Format"),
            "kmsKeyId": params.get("KmsKeyId"),
            "progress": "0",
            "snapshotId": snapshot_id,
            "status": "active",
            "statusMessage": "",
            "url": disk_container.get("Url") or disk_container.get("URL"),
            "userBucket": disk_container.get("UserBucket") or {},
        }

        resource = VmImport(
            conversion_task_id=import_task_id,
            import_task_id=import_task_id,
            expiration_time="",
            import_instance={},
            import_volume={},
            state="active",
            status_message="",
            tag_set=tag_set,
        )
        resource.task_type = "snapshot"
        resource.description = params.get("Description") or ""
        resource.client_data = params.get("ClientData") or ""
        resource.client_token = params.get("ClientToken") or ""
        resource.encrypted = encrypted_value
        resource.kms_key_id = params.get("KmsKeyId") or ""
        resource.snapshot_task_detail = snapshot_task_detail
        resource.status = "active"
        resource.progress = "0"

        self.resources[import_task_id] = resource

        return {
            'description': resource.description or None,
            'importTaskId': resource.import_task_id or None,
            'snapshotTaskDetail': {
                'description': snapshot_task_detail.get("description"),
                'diskImageSize': snapshot_task_detail.get("diskImageSize"),
                'encrypted': snapshot_task_detail.get("encrypted"),
                'format': snapshot_task_detail.get("format"),
                'kmsKeyId': snapshot_task_detail.get("kmsKeyId"),
                'progress': snapshot_task_detail.get("progress"),
                'snapshotId': snapshot_task_detail.get("snapshotId"),
                'status': snapshot_task_detail.get("status"),
                'statusMessage': snapshot_task_detail.get("statusMessage"),
                'url': snapshot_task_detail.get("url"),
                'userBucket': snapshot_task_detail.get("userBucket") or {"s3Bucket": None, "s3Key": None},
                },
            'tagSet': resource.tag_set or [],
            }

    def ImportVolume(self, params: Dict[str, Any]):
        """This API action supports only single-volume VMs. To import multi-volume VMs, useImportImageinstead. To import a disk to a snapshot, useImportSnapshotinstead. Creates an import volume task using metadata from the specified disk image. For information about the import manifest referenced by this API a"""

        error = self._require_param(params, "Image")
        if error:
            return error
        error = self._require_param(params, "Volume")
        if error:
            return error

        conversion_task_id = self._generate_id("conversion")
        expiration_time = datetime.now(timezone.utc).isoformat()
        image = params.get("Image") or {}
        volume = params.get("Volume") or {}
        volume_id = self._generate_id("vol")

        import_instance = {
            "description": params.get("Description") or "",
            "instanceId": None,
            "platform": "",
            "volumes": [],
        }
        import_volume = {
            "availabilityZone": params.get("AvailabilityZone"),
            "availabilityZoneId": params.get("AvailabilityZoneId"),
            "bytesConverted": None,
            "description": params.get("Description") or "",
            "image": {
                "checksum": image.get("Checksum"),
                "format": image.get("Format"),
                "importManifestUrl": image.get("ImportManifestUrl") or image.get("ImportManifestURL"),
                "size": image.get("Size"),
            },
            "volume": {
                "id": volume_id,
                "size": volume.get("Size"),
            },
        }

        resource = VmImport(
            conversion_task_id=conversion_task_id,
            expiration_time=expiration_time,
            import_instance=import_instance,
            import_volume=import_volume,
            state="active",
            status_message="",
            tag_set=[],
        )
        resource.task_type = "volume"
        resource.description = params.get("Description") or ""
        resource.status = "active"

        self.resources[conversion_task_id] = resource

        return {
            'conversionTask': {
                'conversionTaskId': resource.conversion_task_id or None,
                'expirationTime': resource.expiration_time or None,
                'importInstance': {
                    'description': resource.import_instance.get("description") or None,
                    'instanceId': resource.import_instance.get("instanceId"),
                    'platform': resource.import_instance.get("platform") or None,
                    'volumes': resource.import_instance.get("volumes") or [],
                    },
                'importVolume': {
                    'availabilityZone': resource.import_volume.get("availabilityZone"),
                    'availabilityZoneId': resource.import_volume.get("availabilityZoneId"),
                    'bytesConverted': resource.import_volume.get("bytesConverted"),
                    'description': resource.import_volume.get("description"),
                    'image': {
                        'checksum': resource.import_volume.get("image", {}).get("checksum"),
                        'format': resource.import_volume.get("image", {}).get("format"),
                        'importManifestUrl': resource.import_volume.get("image", {}).get("importManifestUrl"),
                        'size': resource.import_volume.get("image", {}).get("size"),
                        },
                    'volume': {
                        'id': resource.import_volume.get("volume", {}).get("id"),
                        'size': resource.import_volume.get("volume", {}).get("size"),
                        },
                    },
                'state': resource.state or None,
                'statusMessage': resource.status_message or None,
                'tagSet': resource.tag_set or [],
                },
            }

    def _generate_id(self, prefix: str = 'conversion') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class vmimport_RequestParser:
    @staticmethod
    def parse_cancel_conversion_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ConversionTaskId": get_scalar(md, "ConversionTaskId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ReasonMessage": get_scalar(md, "ReasonMessage"),
        }

    @staticmethod
    def parse_cancel_import_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CancelReason": get_scalar(md, "CancelReason"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ImportTaskId": get_scalar(md, "ImportTaskId"),
        }

    @staticmethod
    def parse_describe_conversion_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ConversionTaskId.N": get_indexed_list(md, "ConversionTaskId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_import_image_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filters.N": parse_filters(md, "Filters"),
            "ImportTaskId.N": get_indexed_list(md, "ImportTaskId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_import_snapshot_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filters.N": parse_filters(md, "Filters"),
            "ImportTaskId.N": get_indexed_list(md, "ImportTaskId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_import_image_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Architecture": get_scalar(md, "Architecture"),
            "BootMode": get_scalar(md, "BootMode"),
            "ClientData": get_scalar(md, "ClientData"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DiskContainer.N": get_indexed_list(md, "DiskContainer"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Encrypted": get_scalar(md, "Encrypted"),
            "Hypervisor": get_scalar(md, "Hypervisor"),
            "KmsKeyId": get_scalar(md, "KmsKeyId"),
            "LicenseSpecifications.N": get_indexed_list(md, "LicenseSpecifications"),
            "LicenseType": get_scalar(md, "LicenseType"),
            "Platform": get_scalar(md, "Platform"),
            "RoleName": get_scalar(md, "RoleName"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "UsageOperation": get_scalar(md, "UsageOperation"),
        }

    @staticmethod
    def parse_import_instance_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "DiskImage.N": get_indexed_list(md, "DiskImage"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LaunchSpecification": get_scalar(md, "LaunchSpecification"),
            "Platform": get_scalar(md, "Platform"),
        }

    @staticmethod
    def parse_import_snapshot_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientData": get_scalar(md, "ClientData"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DiskContainer": get_scalar(md, "DiskContainer"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Encrypted": get_scalar(md, "Encrypted"),
            "KmsKeyId": get_scalar(md, "KmsKeyId"),
            "RoleName": get_scalar(md, "RoleName"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_import_volume_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Image": get_scalar(md, "Image"),
            "Volume": get_scalar(md, "Volume"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CancelConversionTask": vmimport_RequestParser.parse_cancel_conversion_task_request,
            "CancelImportTask": vmimport_RequestParser.parse_cancel_import_task_request,
            "DescribeConversionTasks": vmimport_RequestParser.parse_describe_conversion_tasks_request,
            "DescribeImportImageTasks": vmimport_RequestParser.parse_describe_import_image_tasks_request,
            "DescribeImportSnapshotTasks": vmimport_RequestParser.parse_describe_import_snapshot_tasks_request,
            "ImportImage": vmimport_RequestParser.parse_import_image_request,
            "ImportInstance": vmimport_RequestParser.parse_import_instance_request,
            "ImportSnapshot": vmimport_RequestParser.parse_import_snapshot_request,
            "ImportVolume": vmimport_RequestParser.parse_import_volume_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class vmimport_ResponseSerializer:
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
                xml_parts.extend(vmimport_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(vmimport_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(vmimport_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(vmimport_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_cancel_conversion_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelConversionTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CancelConversionTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_cancel_import_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelImportTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize importTaskId
        _importTaskId_key = None
        if "importTaskId" in data:
            _importTaskId_key = "importTaskId"
        elif "ImportTaskId" in data:
            _importTaskId_key = "ImportTaskId"
        if _importTaskId_key:
            param_data = data[_importTaskId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<importTaskId>{esc(str(param_data))}</importTaskId>')
        # Serialize previousState
        _previousState_key = None
        if "previousState" in data:
            _previousState_key = "previousState"
        elif "PreviousState" in data:
            _previousState_key = "PreviousState"
        if _previousState_key:
            param_data = data[_previousState_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<previousState>{esc(str(param_data))}</previousState>')
        # Serialize state
        _state_key = None
        if "state" in data:
            _state_key = "state"
        elif "State" in data:
            _state_key = "State"
        if _state_key:
            param_data = data[_state_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<state>{esc(str(param_data))}</state>')
        xml_parts.append(f'</CancelImportTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_conversion_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeConversionTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize conversionTasks
        _conversionTasks_key = None
        if "conversionTasks" in data:
            _conversionTasks_key = "conversionTasks"
        elif "ConversionTasks" in data:
            _conversionTasks_key = "ConversionTasks"
        if _conversionTasks_key:
            param_data = data[_conversionTasks_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<conversionTasksSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</conversionTasksSet>')
            else:
                xml_parts.append(f'{indent_str}<conversionTasksSet/>')
        xml_parts.append(f'</DescribeConversionTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_import_image_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeImportImageTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize importImageTaskSet
        _importImageTaskSet_key = None
        if "importImageTaskSet" in data:
            _importImageTaskSet_key = "importImageTaskSet"
        elif "ImportImageTaskSet" in data:
            _importImageTaskSet_key = "ImportImageTaskSet"
        elif "ImportImageTasks" in data:
            _importImageTaskSet_key = "ImportImageTasks"
        if _importImageTaskSet_key:
            param_data = data[_importImageTaskSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<importImageTaskSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</importImageTaskSet>')
            else:
                xml_parts.append(f'{indent_str}<importImageTaskSet/>')
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
        xml_parts.append(f'</DescribeImportImageTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_import_snapshot_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeImportSnapshotTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize importSnapshotTaskSet
        _importSnapshotTaskSet_key = None
        if "importSnapshotTaskSet" in data:
            _importSnapshotTaskSet_key = "importSnapshotTaskSet"
        elif "ImportSnapshotTaskSet" in data:
            _importSnapshotTaskSet_key = "ImportSnapshotTaskSet"
        elif "ImportSnapshotTasks" in data:
            _importSnapshotTaskSet_key = "ImportSnapshotTasks"
        if _importSnapshotTaskSet_key:
            param_data = data[_importSnapshotTaskSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<importSnapshotTaskSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</importSnapshotTaskSet>')
            else:
                xml_parts.append(f'{indent_str}<importSnapshotTaskSet/>')
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
        xml_parts.append(f'</DescribeImportSnapshotTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_import_image_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ImportImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize architecture
        _architecture_key = None
        if "architecture" in data:
            _architecture_key = "architecture"
        elif "Architecture" in data:
            _architecture_key = "Architecture"
        if _architecture_key:
            param_data = data[_architecture_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<architecture>{esc(str(param_data))}</architecture>')
        # Serialize description
        _description_key = None
        if "description" in data:
            _description_key = "description"
        elif "Description" in data:
            _description_key = "Description"
        if _description_key:
            param_data = data[_description_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<description>{esc(str(param_data))}</description>')
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
        # Serialize hypervisor
        _hypervisor_key = None
        if "hypervisor" in data:
            _hypervisor_key = "hypervisor"
        elif "Hypervisor" in data:
            _hypervisor_key = "Hypervisor"
        if _hypervisor_key:
            param_data = data[_hypervisor_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<hypervisor>{esc(str(param_data))}</hypervisor>')
        # Serialize imageId
        _imageId_key = None
        if "imageId" in data:
            _imageId_key = "imageId"
        elif "ImageId" in data:
            _imageId_key = "ImageId"
        if _imageId_key:
            param_data = data[_imageId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<imageId>{esc(str(param_data))}</imageId>')
        # Serialize importTaskId
        _importTaskId_key = None
        if "importTaskId" in data:
            _importTaskId_key = "importTaskId"
        elif "ImportTaskId" in data:
            _importTaskId_key = "ImportTaskId"
        if _importTaskId_key:
            param_data = data[_importTaskId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<importTaskId>{esc(str(param_data))}</importTaskId>')
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
        # Serialize licenseSpecifications
        _licenseSpecifications_key = None
        if "licenseSpecifications" in data:
            _licenseSpecifications_key = "licenseSpecifications"
        elif "LicenseSpecifications" in data:
            _licenseSpecifications_key = "LicenseSpecifications"
        if _licenseSpecifications_key:
            param_data = data[_licenseSpecifications_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<licenseSpecificationsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</licenseSpecificationsSet>')
            else:
                xml_parts.append(f'{indent_str}<licenseSpecificationsSet/>')
        # Serialize licenseType
        _licenseType_key = None
        if "licenseType" in data:
            _licenseType_key = "licenseType"
        elif "LicenseType" in data:
            _licenseType_key = "LicenseType"
        if _licenseType_key:
            param_data = data[_licenseType_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<licenseType>{esc(str(param_data))}</licenseType>')
        # Serialize platform
        _platform_key = None
        if "platform" in data:
            _platform_key = "platform"
        elif "Platform" in data:
            _platform_key = "Platform"
        if _platform_key:
            param_data = data[_platform_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<platform>{esc(str(param_data))}</platform>')
        # Serialize progress
        _progress_key = None
        if "progress" in data:
            _progress_key = "progress"
        elif "Progress" in data:
            _progress_key = "Progress"
        if _progress_key:
            param_data = data[_progress_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<progressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</progressSet>')
            else:
                xml_parts.append(f'{indent_str}<progressSet/>')
        # Serialize snapshotDetailSet
        _snapshotDetailSet_key = None
        if "snapshotDetailSet" in data:
            _snapshotDetailSet_key = "snapshotDetailSet"
        elif "SnapshotDetailSet" in data:
            _snapshotDetailSet_key = "SnapshotDetailSet"
        elif "SnapshotDetails" in data:
            _snapshotDetailSet_key = "SnapshotDetails"
        if _snapshotDetailSet_key:
            param_data = data[_snapshotDetailSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<snapshotDetailSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</snapshotDetailSet>')
            else:
                xml_parts.append(f'{indent_str}<snapshotDetailSet/>')
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
        # Serialize statusMessage
        _statusMessage_key = None
        if "statusMessage" in data:
            _statusMessage_key = "statusMessage"
        elif "StatusMessage" in data:
            _statusMessage_key = "StatusMessage"
        if _statusMessage_key:
            param_data = data[_statusMessage_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<statusMessage>{esc(str(param_data))}</statusMessage>')
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
                    xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        # Serialize usageOperation
        _usageOperation_key = None
        if "usageOperation" in data:
            _usageOperation_key = "usageOperation"
        elif "UsageOperation" in data:
            _usageOperation_key = "UsageOperation"
        if _usageOperation_key:
            param_data = data[_usageOperation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<usageOperation>{esc(str(param_data))}</usageOperation>')
        xml_parts.append(f'</ImportImageResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_import_instance_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ImportInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize conversionTask
        _conversionTask_key = None
        if "conversionTask" in data:
            _conversionTask_key = "conversionTask"
        elif "ConversionTask" in data:
            _conversionTask_key = "ConversionTask"
        if _conversionTask_key:
            param_data = data[_conversionTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<conversionTask>')
            xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</conversionTask>')
        xml_parts.append(f'</ImportInstanceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_import_snapshot_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ImportSnapshotResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize description
        _description_key = None
        if "description" in data:
            _description_key = "description"
        elif "Description" in data:
            _description_key = "Description"
        if _description_key:
            param_data = data[_description_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<description>{esc(str(param_data))}</description>')
        # Serialize importTaskId
        _importTaskId_key = None
        if "importTaskId" in data:
            _importTaskId_key = "importTaskId"
        elif "ImportTaskId" in data:
            _importTaskId_key = "ImportTaskId"
        if _importTaskId_key:
            param_data = data[_importTaskId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<importTaskId>{esc(str(param_data))}</importTaskId>')
        # Serialize snapshotTaskDetail
        _snapshotTaskDetail_key = None
        if "snapshotTaskDetail" in data:
            _snapshotTaskDetail_key = "snapshotTaskDetail"
        elif "SnapshotTaskDetail" in data:
            _snapshotTaskDetail_key = "SnapshotTaskDetail"
        if _snapshotTaskDetail_key:
            param_data = data[_snapshotTaskDetail_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<snapshotTaskDetail>')
            xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</snapshotTaskDetail>')
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
                    xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        xml_parts.append(f'</ImportSnapshotResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_import_volume_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ImportVolumeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize conversionTask
        _conversionTask_key = None
        if "conversionTask" in data:
            _conversionTask_key = "conversionTask"
        elif "ConversionTask" in data:
            _conversionTask_key = "ConversionTask"
        if _conversionTask_key:
            param_data = data[_conversionTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<conversionTask>')
            xml_parts.extend(vmimport_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</conversionTask>')
        xml_parts.append(f'</ImportVolumeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CancelConversionTask": vmimport_ResponseSerializer.serialize_cancel_conversion_task_response,
            "CancelImportTask": vmimport_ResponseSerializer.serialize_cancel_import_task_response,
            "DescribeConversionTasks": vmimport_ResponseSerializer.serialize_describe_conversion_tasks_response,
            "DescribeImportImageTasks": vmimport_ResponseSerializer.serialize_describe_import_image_tasks_response,
            "DescribeImportSnapshotTasks": vmimport_ResponseSerializer.serialize_describe_import_snapshot_tasks_response,
            "ImportImage": vmimport_ResponseSerializer.serialize_import_image_response,
            "ImportInstance": vmimport_ResponseSerializer.serialize_import_instance_response,
            "ImportSnapshot": vmimport_ResponseSerializer.serialize_import_snapshot_response,
            "ImportVolume": vmimport_ResponseSerializer.serialize_import_volume_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

