from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class ConversionTaskState(str, Enum):
    ACTIVE = "active"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class DiskImageFormat(str, Enum):
    VMDK = "VMDK"
    RAW = "RAW"
    VHD = "VHD"
    OVA = "OVA"
    VHDX = "VHDX"


class ImportInstancePlatform(str, Enum):
    WINDOWS = "Windows"


class ImportInstanceArchitecture(str, Enum):
    I386 = "i386"
    X86_64 = "x86_64"
    ARM64 = "arm64"
    X86_64_MAC = "x86_64_mac"
    ARM64_MAC = "arm64_mac"


class ImportInstanceShutdownBehavior(str, Enum):
    STOP = "stop"
    TERMINATE = "terminate"


class ImportInstanceTenancy(str, Enum):
    DEFAULT = "default"
    DEDICATED = "dedicated"
    HOST = "host"


class ImportImageArchitecture(str, Enum):
    I386 = "i386"
    X86_64 = "x86_64"
    ARM64 = "arm64"


class ImportImageBootMode(str, Enum):
    LEGACY_BIOS = "legacy-bios"
    UEFI = "uefi"
    UEFI_PREFERRED = "uefi-preferred"


class ImportImageHypervisor(str, Enum):
    XEN = "xen"


class ImportImagePlatform(str, Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"


@dataclass
class Tag:
    Key: str
    Value: str


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class UserBucket:
    S3Bucket: Optional[str] = None
    S3Key: Optional[str] = None


@dataclass
class UserBucketDetails:
    s3Bucket: Optional[str] = None
    s3Key: Optional[str] = None


@dataclass
class DiskImageVolumeDescription:
    id: Optional[str] = None
    size: Optional[int] = None  # GiB


@dataclass
class DiskImageDescription:
    checksum: Optional[str] = None
    format: Optional[DiskImageFormat] = None
    importManifestUrl: Optional[str] = None
    size: Optional[int] = None  # GiB


@dataclass
class ImportInstanceVolumeDetailItem:
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    bytesConverted: Optional[int] = None
    description: Optional[str] = None
    image: Optional[DiskImageDescription] = None
    status: Optional[str] = None
    statusMessage: Optional[str] = None
    volume: Optional[DiskImageVolumeDescription] = None


@dataclass
class ImportInstanceTaskDetails:
    description: Optional[str] = None
    instanceId: Optional[str] = None
    platform: Optional[ImportInstancePlatform] = None
    volumes: List[ImportInstanceVolumeDetailItem] = field(default_factory=list)


@dataclass
class ImportVolumeTaskDetails:
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    bytesConverted: Optional[int] = None
    description: Optional[str] = None
    image: Optional[DiskImageDescription] = None
    volume: Optional[DiskImageVolumeDescription] = None


@dataclass
class ConversionTask:
    conversionTaskId: Optional[str] = None
    expirationTime: Optional[str] = None  # ISO8601 string
    importInstance: Optional[ImportInstanceTaskDetails] = None
    importVolume: Optional[ImportVolumeTaskDetails] = None
    state: Optional[ConversionTaskState] = None
    statusMessage: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)


@dataclass
class SnapshotDetail:
    description: Optional[str] = None
    deviceName: Optional[str] = None
    diskImageSize: Optional[float] = None  # GiB
    format: Optional[str] = None
    progress: Optional[str] = None
    snapshotId: Optional[str] = None
    status: Optional[str] = None
    statusMessage: Optional[str] = None
    url: Optional[str] = None
    userBucket: Optional[UserBucketDetails] = None


@dataclass
class SnapshotTaskDetail:
    description: Optional[str] = None
    diskImageSize: Optional[float] = None  # GiB
    encrypted: Optional[bool] = None
    format: Optional[str] = None
    kmsKeyId: Optional[str] = None
    progress: Optional[str] = None
    snapshotId: Optional[str] = None
    status: Optional[str] = None
    statusMessage: Optional[str] = None
    url: Optional[str] = None
    userBucket: Optional[UserBucketDetails] = None


@dataclass
class ImportSnapshotTask:
    description: Optional[str] = None
    importTaskId: Optional[str] = None
    snapshotTaskDetail: Optional[SnapshotTaskDetail] = None
    tagSet: List[Tag] = field(default_factory=list)


@dataclass
class ImportImageLicenseConfigurationRequest:
    LicenseConfigurationArn: Optional[str] = None


@dataclass
class ImportImageLicenseConfigurationResponse:
    licenseConfigurationArn: Optional[str] = None


@dataclass
class SnapshotDiskContainer:
    Description: Optional[str] = None
    Format: Optional[str] = None
    Url: Optional[str] = None
    UserBucket: Optional[UserBucket] = None


@dataclass
class ImageDiskContainer:
    Description: Optional[str] = None
    DeviceName: Optional[str] = None
    Format: Optional[str] = None
    SnapshotId: Optional[str] = None
    Url: Optional[str] = None
    UserBucket: Optional[UserBucket] = None


@dataclass
class ClientData:
    Comment: Optional[str] = None
    UploadEnd: Optional[str] = None  # Timestamp ISO8601 string
    UploadSize: Optional[float] = None  # GiB
    UploadStart: Optional[str] = None  # Timestamp ISO8601 string


@dataclass
class DiskImageDetail:
    Bytes: int
    Format: DiskImageFormat
    ImportManifestUrl: str


@dataclass
class VolumeDetail:
    Size: int  # GiB


@dataclass
class DiskImage:
    Description: Optional[str] = None
    Image: DiskImageDetail = None
    Volume: Optional[VolumeDetail] = None


@dataclass
class Placement:
    Affinity: Optional[str] = None
    AvailabilityZone: Optional[str] = None
    AvailabilityZoneId: Optional[str] = None
    GroupId: Optional[str] = None
    GroupName: Optional[str] = None
    HostId: Optional[str] = None
    HostResourceGroupArn: Optional[str] = None
    PartitionNumber: Optional[int] = None
    SpreadDomain: Optional[str] = None
    Tenancy: Optional[ImportInstanceTenancy] = None


@dataclass
class UserData:
    Data: Optional[str] = None


@dataclass
class ImportInstanceLaunchSpecification:
    AdditionalInfo: Optional[str] = None
    Architecture: Optional[ImportInstanceArchitecture] = None
    GroupIds: List[str] = field(default_factory=list)
    GroupNames: List[str] = field(default_factory=list)
    InstanceInitiatedShutdownBehavior: Optional[ImportInstanceShutdownBehavior] = None
    InstanceType: Optional[str] = None
    Monitoring: Optional[bool] = None
    Placement: Optional[Placement] = None
    PrivateIpAddress: Optional[str] = None
    SubnetId: Optional[str] = None
    UserData: Optional[UserData] = None


@dataclass
class ImportImageLicenseConfigurationRequest:
    LicenseConfigurationArn: Optional[str] = None


@dataclass
class ImportImageTask:
    architecture: Optional[ImportImageArchitecture] = None
    bootMode: Optional[ImportImageBootMode] = None
    description: Optional[str] = None
    encrypted: Optional[bool] = None
    hypervisor: Optional[ImportImageHypervisor] = None
    imageId: Optional[str] = None
    importTaskId: Optional[str] = None
    kmsKeyId: Optional[str] = None
    licenseSpecifications: List[ImportImageLicenseConfigurationResponse] = field(default_factory=list)
    licenseType: Optional[str] = None
    platform: Optional[ImportImagePlatform] = None
    progress: Optional[str] = None
    snapshotDetailSet: List[SnapshotDetail] = field(default_factory=list)
    status: Optional[str] = None
    statusMessage: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    usageOperation: Optional[str] = None


class VMimportBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state for resources

    def cancel_conversion_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        conversion_task_id = params.get("ConversionTaskId")
        dry_run = params.get("DryRun", False)
        reason_message = params.get("ReasonMessage")

        if dry_run:
            # For dry run, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        if not conversion_task_id:
            # ConversionTaskId is required
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "MissingParameter",
                "message": "ConversionTaskId is required"
            }

        conversion_task = self.state.vm_import.get(conversion_task_id)
        if not conversion_task:
            # Task not found, return error
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "InvalidConversionTaskId.NotFound",
                "message": f"Conversion task {conversion_task_id} not found"
            }

        # Check if task is in a state that can be cancelled
        if conversion_task.state not in [ConversionTaskState.ACTIVE, ConversionTaskState.CANCELLING]:
            # If conversion is complete or transferring final disk image, fail
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "InvalidConversionTaskState",
                "message": f"Conversion task {conversion_task_id} cannot be cancelled in state {conversion_task.state}"
            }

        # Cancel the task: remove from state.vm_import
        del self.state.vm_import[conversion_task_id]

        # Also remove from resources if stored there
        if conversion_task_id in self.state.resources:
            del self.state.resources[conversion_task_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True
        }


    def cancel_import_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import_task_id = params.get("ImportTaskId")
        dry_run = params.get("DryRun", False)
        cancel_reason = params.get("CancelReason")

        if dry_run:
            # For dry run, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "importTaskId": import_task_id,
                "previousState": None,
                "state": None,
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        if not import_task_id:
            # ImportTaskId is optional but if not provided, no task to cancel
            return {
                "requestId": self.generate_request_id(),
                "importTaskId": None,
                "previousState": None,
                "state": None
            }

        import_task = self.state.vm_import.get(import_task_id)
        if not import_task:
            # Task not found, return error
            return {
                "requestId": self.generate_request_id(),
                "importTaskId": import_task_id,
                "previousState": None,
                "state": None,
                "__type": "InvalidImportTaskId.NotFound",
                "message": f"Import task {import_task_id} not found"
            }

        previous_state = import_task.status
        # Mark task as cancelled
        import_task.status = "cancelled"

        # Remove from vm_import dict
        del self.state.vm_import[import_task_id]

        # Also remove from resources if stored there
        if import_task_id in self.state.resources:
            del self.state.resources[import_task_id]

        return {
            "requestId": self.generate_request_id(),
            "importTaskId": import_task_id,
            "previousState": previous_state,
            "state": "cancelled"
        }


    def describe_conversion_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        conversion_task_ids = params.get("ConversionTaskId.N")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For dry run, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "conversionTasks": [],
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        tasks_to_describe = []
        if conversion_task_ids:
            # Filter tasks by provided IDs
            for task_id in conversion_task_ids:
                task = self.state.vm_import.get(task_id)
                if task:
                    tasks_to_describe.append(task)
        else:
            # Return all conversion tasks
            tasks_to_describe = list(self.state.vm_import.values())

        # Build response list
        conversion_tasks_response = []
        for task in tasks_to_describe:
            import_instance = None
            if task.importInstance:
                import_instance = {
                    "description": task.importInstance.description,
                    "instanceId": task.importInstance.instanceId,
                    "platform": task.importInstance.platform.name if task.importInstance.platform else None,
                    "volumes": []
                }
                for vol in task.importInstance.volumes:
                    image = None
                    if vol.image:
                        image = {
                            "checksum": vol.image.checksum,
                            "format": vol.image.format.name if vol.image.format else None,
                            "importManifestUrl": vol.image.importManifestUrl,
                            "size": vol.image.size
                        }
                    volume = None
                    if vol.volume:
                        volume = {
                            "id": vol.volume.id,
                            "size": vol.volume.size
                        }
                    import_instance["volumes"].append({
                        "availabilityZone": vol.availabilityZone,
                        "availabilityZoneId": vol.availabilityZoneId,
                        "bytesConverted": vol.bytesConverted,
                        "description": vol.description,
                        "image": image,
                        "status": vol.status,
                        "statusMessage": vol.statusMessage,
                        "volume": volume
                    })

            import_volume = None
            if task.importVolume:
                image = None
                if task.importVolume.image:
                    image = {
                        "checksum": task.importVolume.image.checksum,
                        "format": task.importVolume.image.format.name if task.importVolume.image.format else None,
                        "importManifestUrl": task.importVolume.image.importManifestUrl,
                        "size": task.importVolume.image.size
                    }
                volume = None
                if task.importVolume.volume:
                    volume = {
                        "id": task.importVolume.volume.id,
                        "size": task.importVolume.volume.size
                    }
                import_volume = {
                    "availabilityZone": task.importVolume.availabilityZone,
                    "availabilityZoneId": task.importVolume.availabilityZoneId,
                    "bytesConverted": task.importVolume.bytesConverted,
                    "description": task.importVolume.description,
                    "image": image,
                    "volume": volume
                }

            tag_set = []
            for tag in task.tagSet:
                tag_set.append({
                    "Key": tag.Key,
                    "Value": tag.Value
                })

            conversion_tasks_response.append({
                "conversionTaskId": task.conversionTaskId,
                "expirationTime": task.expirationTime,
                "importInstance": import_instance,
                "importVolume": import_volume,
                "state": task.state.name if task.state else None,
                "statusMessage": task.statusMessage,
                "tagSet": tag_set
            })

        return {
            "requestId": self.generate_request_id(),
            "conversionTasks": conversion_tasks_response
        }


    def describe_import_image_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filters.N", [])
        import_task_ids = params.get("ImportTaskId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "importImageTaskSet": [],
                "nextToken": None,
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        # Filter tasks by importTaskIds if provided
        tasks = []
        if import_task_ids:
            for task_id in import_task_ids:
                task = self.state.vm_import.get(task_id)
                if task and isinstance(task, ImportImageTask):
                    tasks.append(task)
        else:
            # Return all ImportImageTask instances in vm_import
            for task in self.state.vm_import.values():
                if isinstance(task, ImportImageTask):
                    tasks.append(task)

        # Apply filters if any
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if name == "task-state":
                tasks = [t for t in tasks if t.status in values]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(tasks)
        if max_results is not None:
            try:
                max_results_int = int(max_results)
                end_index = min(start_index + max_results_int, len(tasks))
            except Exception:
                max_results_int = None

        paged_tasks = tasks[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(tasks) else None

        import_image_task_set = []
        for task in paged_tasks:
            license_specs = []
            for lic in task.licenseSpecifications:
                license_specs.append({
                    "licenseConfigurationArn": lic.licenseConfigurationArn
                })

            snapshot_detail_set = []
            for snap in task.snapshotDetailSet:
                user_bucket = None
                if snap.userBucket:
                    user_bucket = {
                        "s3Bucket": snap.userBucket.s3Bucket,
                        "s3Key": snap.userBucket.s3Key
                    }
                snapshot_detail_set.append({
                    "description": snap.description,
                    "deviceName": snap.deviceName,
                    "diskImageSize": snap.diskImageSize,
                    "format": snap.format,
                    "progress": snap.progress,
                    "snapshotId": snap.snapshotId,
                    "status": snap.status,
                    "statusMessage": snap.statusMessage,
                    "url": snap.url,
                    "userBucket": user_bucket
                })

            tag_set = []
            for tag in task.tagSet:
                tag_set.append({
                    "Key": tag.Key,
                    "Value": tag.Value
                })

            import_image_task_set.append({
                "architecture": task.architecture.name if task.architecture else None,
                "bootMode": task.bootMode.name if task.bootMode else None,
                "description": task.description,
                "encrypted": task.encrypted,
                "hypervisor": task.hypervisor.name if task.hypervisor else None,
                "imageId": task.imageId,
                "importTaskId": task.importTaskId,
                "kmsKeyId": task.kmsKeyId,
                "licenseSpecifications": license_specs,
                "licenseType": task.licenseType,
                "platform": task.platform.name if task.platform else None,
                "progress": task.progress,
                "snapshotDetailSet": snapshot_detail_set,
                "status": task.status,
                "statusMessage": task.statusMessage,
                "tagSet": tag_set,
                "usageOperation": task.usageOperation
            })

        return {
            "requestId": self.generate_request_id(),
            "importImageTaskSet": import_image_task_set,
            "nextToken": new_next_token
        }


    def describe_import_snapshot_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filters.N", [])
        import_task_ids = params.get("ImportTaskId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "importSnapshotTaskSet": [],
                "nextToken": None,
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        # Filter tasks by importTaskIds if provided
        tasks = []
        if import_task_ids:
            for task_id in import_task_ids:
                task = self.state.vm_import.get(task_id)
                if task and isinstance(task, ImportSnapshotTask):
                    tasks.append(task)
        else:
            # Return all ImportSnapshotTask instances in vm_import
            for task in self.state.vm_import.values():
                if isinstance(task, ImportSnapshotTask):
                    tasks.append(task)

        # Apply filters if any
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if name:
                # No specific filter details given, so skip or implement basic filtering
                # For now, skip filtering as no details provided
                pass

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(tasks)
        if max_results is not None:
            try:
                max_results_int = int(max_results)
                end_index = min(start_index + max_results_int, len(tasks))
            except Exception:
                max_results_int = None

        paged_tasks = tasks[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(tasks) else None

        import_snapshot_task_set = []
        for task in paged_tasks:
            detail = task.snapshotTaskDetail
            user_bucket = None
            if detail and detail.userBucket:
                user_bucket = {
                    "s3Bucket": detail.userBucket.s3Bucket,
                    "s3Key": detail.userBucket.s3Key
                }
            tag_set = []
            for tag in task.tagSet:
                tag_set.append({
                    "Key": tag.Key,
                    "Value": tag.Value
                })

            import_snapshot_task_set.append({
                "description": task.description,
                "importTaskId": task.importTaskId,
                "snapshotTaskDetail": {
                    "description": detail.description if detail else None,
                    "diskImageSize": detail.diskImageSize if detail else None,
                    "encrypted": detail.encrypted if detail else None,
                    "format": detail.format if detail else None,
                    "kmsKeyId": detail.kmsKeyId if detail else None,
                    "progress": detail.progress if detail else None,
                    "snapshotId": detail.snapshotId if detail else None,
                    "status": detail.status if detail else None,
                    "statusMessage": detail.statusMessage if detail else None,
                    "url": detail.url if detail else None,
                    "userBucket": user_bucket
                },
                "tagSet": tag_set
            })

        return {
            "requestId": self.generate_request_id(),
            "importSnapshotTaskSet": import_snapshot_task_set,
            "nextToken": new_next_token
        }

    def import_image(self, params: dict) -> dict:
        # Validate and parse parameters
        architecture = params.get("Architecture")
        boot_mode = params.get("BootMode")
        client_data_params = params.get("ClientData")
        client_token = params.get("ClientToken")
        description = params.get("Description")
        disk_containers_params = []
        # DiskContainer.N keys are like DiskContainer.1, DiskContainer.2, etc.
        for key in params:
            if key.startswith("DiskContainer."):
                disk_containers_params.append(params[key])
        dry_run = params.get("DryRun", False)
        encrypted = params.get("Encrypted", False)
        hypervisor = params.get("Hypervisor")
        kms_key_id = params.get("KmsKeyId")
        license_specifications_params = []
        for key in params:
            if key.startswith("LicenseSpecifications."):
                license_specifications_params.append(params[key])
        license_type = params.get("LicenseType")
        platform = params.get("Platform")
        role_name = params.get("RoleName")
        tag_specifications_params = []
        for key in params:
            if key.startswith("TagSpecification."):
                tag_specifications_params.append(params[key])
        usage_operation = params.get("UsageOperation")

        # DryRun check (not implemented, just placeholder)
        if dry_run:
            # In real implementation, check permissions and raise error if unauthorized
            pass

        # Generate importTaskId and imageId
        import_task_id = self.generate_unique_id(prefix="import-")
        image_id = self.generate_unique_id(prefix="ami-")

        # Process license specifications
        license_specifications = []
        for lic_spec in license_specifications_params:
            arn = lic_spec.get("LicenseConfigurationArn")
            if arn:
                license_specifications.append(ImportImageLicenseConfigurationResponse(licenseConfigurationArn=arn))

        # Process tags from tag specifications
        tags = []
        for tag_spec in tag_specifications_params:
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Process disk containers into snapshotDetailSet
        snapshot_detail_set = []
        for disk_container in disk_containers_params:
            desc = disk_container.get("Description")
            device_name = disk_container.get("DeviceName")
            fmt = disk_container.get("Format")
            snapshot_id = disk_container.get("SnapshotId")
            url = disk_container.get("Url")
            user_bucket_params = disk_container.get("UserBucket")
            user_bucket = None
            if user_bucket_params:
                s3_bucket = user_bucket_params.get("S3Bucket")
                s3_key = user_bucket_params.get("S3Key")
                user_bucket = UserBucketDetails(s3Bucket=s3_bucket, s3Key=s3_key)
            # We do not have actual diskImageSize, progress, status, statusMessage, encrypted, kmsKeyId here
            snapshot_detail = SnapshotDetail(
                description=desc,
                deviceName=device_name,
                diskImageSize=None,
                format=fmt,
                progress=None,
                snapshotId=snapshot_id,
                status=None,
                statusMessage=None,
                url=url,
                userBucket=user_bucket,
            )
            snapshot_detail_set.append(snapshot_detail)

        # Process client data
        client_data = None
        if client_data_params:
            client_data = ClientData(
                Comment=client_data_params.get("Comment"),
                UploadEnd=client_data_params.get("UploadEnd"),
                UploadSize=client_data_params.get("UploadSize"),
                UploadStart=client_data_params.get("UploadStart"),
            )

        # Compose ImportImageTask object
        import_image_task = ImportImageTask(
            architecture=architecture,
            bootMode=boot_mode,
            description=description,
            encrypted=encrypted,
            hypervisor=hypervisor,
            imageId=image_id,
            importTaskId=import_task_id,
            kmsKeyId=kms_key_id,
            licenseSpecifications=license_specifications,
            licenseType=license_type,
            platform=platform,
            progress="0%",
            snapshotDetailSet=snapshot_detail_set,
            status="active",
            statusMessage=None,
            tagSet=tags,
            usageOperation=usage_operation,
        )

        # Store the import image task in state
        self.state.vm_import[import_task_id] = import_image_task

        # Compose response dictionary
        response = {
            "architecture": import_image_task.architecture,
            "description": import_image_task.description,
            "encrypted": import_image_task.encrypted,
            "hypervisor": import_image_task.hypervisor,
            "imageId": import_image_task.imageId,
            "importTaskId": import_image_task.importTaskId,
            "kmsKeyId": import_image_task.kmsKeyId,
            "licenseSpecifications": [
                {"licenseConfigurationArn": lic.licenseConfigurationArn} for lic in import_image_task.licenseSpecifications
            ],
            "licenseType": import_image_task.licenseType,
            "platform": import_image_task.platform,
            "progress": import_image_task.progress,
            "requestId": self.generate_request_id(),
            "snapshotDetailSet": [
                {
                    "description": snap.description,
                    "deviceName": snap.deviceName,
                    "diskImageSize": snap.diskImageSize,
                    "format": snap.format,
                    "progress": snap.progress,
                    "snapshotId": snap.snapshotId,
                    "status": snap.status,
                    "statusMessage": snap.statusMessage,
                    "url": snap.url,
                    "userBucket": {
                        "s3Bucket": snap.userBucket.s3Bucket if snap.userBucket else None,
                        "s3Key": snap.userBucket.s3Key if snap.userBucket else None,
                    } if snap.userBucket else None,
                }
                for snap in import_image_task.snapshotDetailSet
            ],
            "status": import_image_task.status,
            "statusMessage": import_image_task.statusMessage,
            "tagSet": [{"Key": tag.Key, "Value": tag.Value} for tag in import_image_task.tagSet],
            "usageOperation": import_image_task.usageOperation,
        }
        return response


    def import_instance(self, params: dict) -> dict:
        # Validate required parameters
        platform = params.get("Platform")
        if platform is None:
            raise ValueError("Platform parameter is required")

        description = params.get("Description")
        disk_images_params = []
        for key in params:
            if key.startswith("DiskImage."):
                disk_images_params.append(params[key])
        dry_run = params.get("DryRun", False)
        launch_spec_params = params.get("LaunchSpecification")
        # DryRun check (not implemented, just placeholder)
        if dry_run:
            pass

        # Generate conversionTaskId and instanceId
        conversion_task_id = self.generate_unique_id(prefix="import-")
        instance_id = self.generate_unique_id(prefix="i-")

        # Process disk images into ImportInstanceVolumeDetailItem list
        volumes = []
        for disk_image_param in disk_images_params:
            desc = disk_image_param.get("Description")
            image_params = disk_image_param.get("Image", {})
            volume_params = disk_image_param.get("Volume", {})

            image = DiskImageDescription(
                checksum=image_params.get("Checksum"),
                format=image_params.get("Format"),
                importManifestUrl=image_params.get("ImportManifestUrl"),
                size=image_params.get("Bytes"),
            )
            volume = DiskImageVolumeDescription(
                id=None,
                size=volume_params.get("Size"),
            )
            volume_detail_item = ImportInstanceVolumeDetailItem(
                availabilityZone=None,
                availabilityZoneId=None,
                bytesConverted=0,
                description=desc,
                image=image,
                status="active",
                statusMessage=None,
                volume=volume,
            )
            volumes.append(volume_detail_item)

        # Process launch specification
        launch_spec = None
        if launch_spec_params:
            # Extract fields from launch_spec_params
            additional_info = launch_spec_params.get("AdditionalInfo")
            architecture = launch_spec_params.get("Architecture")
            group_ids = launch_spec_params.get("GroupIds", [])
            group_names = launch_spec_params.get("GroupNames", [])
            instance_initiated_shutdown_behavior = launch_spec_params.get("InstanceInitiatedShutdownBehavior")
            instance_type = launch_spec_params.get("InstanceType")
            monitoring = launch_spec_params.get("Monitoring")
            placement_params = launch_spec_params.get("Placement")
            placement = None
            if placement_params:
                placement = Placement(
                    Affinity=placement_params.get("Affinity"),
                    AvailabilityZone=placement_params.get("AvailabilityZone"),
                    AvailabilityZoneId=placement_params.get("AvailabilityZoneId"),
                    GroupId=placement_params.get("GroupId"),
                    GroupName=placement_params.get("GroupName"),
                    HostId=placement_params.get("HostId"),
                    HostResourceGroupArn=placement_params.get("HostResourceGroupArn"),
                    PartitionNumber=placement_params.get("PartitionNumber"),
                    SpreadDomain=placement_params.get("SpreadDomain"),
                    Tenancy=placement_params.get("Tenancy"),
                )
            private_ip_address = launch_spec_params.get("PrivateIpAddress")
            subnet_id = launch_spec_params.get("SubnetId")
            user_data_params = launch_spec_params.get("UserData")
            user_data = None
            if user_data_params:
                user_data = UserData(Data=user_data_params.get("Data"))
            launch_spec = ImportInstanceLaunchSpecification(
                AdditionalInfo=additional_info,
                Architecture=architecture,
                GroupIds=group_ids,
                GroupNames=group_names,
                InstanceInitiatedShutdownBehavior=instance_initiated_shutdown_behavior,
                InstanceType=instance_type,
                Monitoring=monitoring,
                Placement=placement,
                PrivateIpAddress=private_ip_address,
                SubnetId=subnet_id,
                UserData=user_data,
            )

        # Compose ImportInstanceTaskDetails
        import_instance_task_details = ImportInstanceTaskDetails(
            description=description,
            instanceId=instance_id,
            platform=platform,
            volumes=volumes,
        )

        # Compose ConversionTask
        conversion_task = ConversionTask(
            conversionTaskId=conversion_task_id,
            expirationTime=None,
            importInstance=import_instance_task_details,
            importVolume=None,
            state=ConversionTaskState.ACTIVE if hasattr(ConversionTaskState, "ACTIVE") else "active",
            statusMessage=None,
            tagSet=[],
        )

        # Store the conversion task in state
        self.state.vm_import[conversion_task_id] = conversion_task

        # Compose response dictionary
        response = {
            "conversionTask": {
                "conversionTaskId": conversion_task.conversionTaskId,
                "expirationTime": conversion_task.expirationTime,
                "importInstance": {
                    "description": import_instance_task_details.description,
                    "instanceId": import_instance_task_details.instanceId,
                    "platform": import_instance_task_details.platform,
                    "volumes": [
                        {
                            "availabilityZone": vol.availabilityZone,
                            "availabilityZoneId": vol.availabilityZoneId,
                            "bytesConverted": vol.bytesConverted,
                            "description": vol.description,
                            "image": {
                                "checksum": vol.image.checksum,
                                "format": vol.image.format,
                                "importManifestUrl": vol.image.importManifestUrl,
                                "size": vol.image.size,
                            } if vol.image else None,
                            "status": vol.status,
                            "statusMessage": vol.statusMessage,
                            "volume": {
                                "id": vol.volume.id,
                                "size": vol.volume.size,
                            } if vol.volume else None,
                        }
                        for vol in import_instance_task_details.volumes
                    ],
                },
                "importVolume": None,
                "state": conversion_task.state,
                "statusMessage": conversion_task.statusMessage,
                "tagSet": [],
            },
            "requestId": self.generate_request_id(),
        }
        return response


    def import_snapshot(self, params: dict) -> dict:
        client_data_params = params.get("ClientData")
        client_token = params.get("ClientToken")
        description = params.get("Description")
        disk_container_params = params.get("DiskContainer")
        dry_run = params.get("DryRun", False)
        encrypted = params.get("Encrypted", False)
        kms_key_id = params.get("KmsKeyId")
        role_name = params.get("RoleName")
        tag_specifications_params = []
        for key in params:
            if key.startswith("TagSpecification."):
                tag_specifications_params.append(params[key])

        # DryRun check (not implemented)
        if dry_run:
            pass

        # Generate importTaskId
        import_task_id = self.generate_unique_id(prefix="import-")

        # Process tags from tag specifications
        tags = []
        for tag_spec in tag_specifications_params:
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Process client data
        client_data = None
        if client_data_params:
            client_data = ClientData(
                Comment=client_data_params.get("Comment"),
                UploadEnd=client_data_params.get("UploadEnd"),
                UploadSize=client_data_params.get("UploadSize"),
                UploadStart=client_data_params.get("UploadStart"),
            )

        # Process disk container
        snapshot_task_detail = None
        if disk_container_params:
            desc = disk_container_params.get("Description")
            fmt = disk_container_params.get("Format")
            url = disk_container_params.get("Url")
            user_bucket_params = disk_container_params.get("UserBucket")
            user_bucket = None
            if user_bucket_params:
                s3_bucket = user_bucket_params.get("S3Bucket")
                s3_key = user_bucket_params.get("S3Key")
                user_bucket = UserBucketDetails(s3Bucket=s3_bucket, s3Key=s3_key)
            snapshot_task_detail = SnapshotTaskDetail(
                description=desc,
                diskImageSize=None,
                encrypted=encrypted,
                format=fmt,
                kmsKeyId=kms_key_id,
                progress=None,
                snapshotId=None,
                status="active",
                statusMessage=None,
                url=url,
                userBucket=user_bucket,
            )

        # Compose ImportSnapshotTask
        import_snapshot_task = ImportSnapshotTask(
            description=description,
            importTaskId=import_task_id,
            snapshotTaskDetail=snapshot_task_detail,
            tagSet=tags,
        )

        # Store in state
        self.state.vm_import[import_task_id] = import_snapshot_task

        # Compose response dictionary
        response = {
            "description": import_snapshot_task.description,
            "importTaskId": import_snapshot_task.importTaskId,
            "requestId": self.generate_request_id(),
            "snapshotTaskDetail": {
                "description": snapshot_task_detail.description if snapshot_task_detail else None,
                "diskImageSize": snapshot_task_detail.diskImageSize if snapshot_task_detail else None,
                "encrypted": snapshot_task_detail.encrypted if snapshot_task_detail else None,
                "format": snapshot_task_detail.format if snapshot_task_detail else None,
                "kmsKeyId": snapshot_task_detail.kmsKeyId if snapshot_task_detail else None,
                "progress": snapshot_task_detail.progress if snapshot_task_detail else None,
                "snapshotId": snapshot_task_detail.snapshotId if snapshot_task_detail else None,
                "status": snapshot_task_detail.status if snapshot_task_detail else None,
                "statusMessage": snapshot_task_detail.statusMessage if snapshot_task_detail else None,
                "url": snapshot_task_detail.url if snapshot_task_detail else None,
                "userBucket": {
                    "s3Bucket": snapshot_task_detail.userBucket.s3Bucket if snapshot_task_detail and snapshot_task_detail.userBucket else None,
                    "s3Key": snapshot_task_detail.userBucket.s3Key if snapshot_task_detail and snapshot_task_detail.userBucket else None,
                } if snapshot_task_detail and snapshot_task_detail.userBucket else None,
            } if snapshot_task_detail else None,
            "tagSet": [{"Key": tag.Key, "Value": tag.Value} for tag in import_snapshot_task.tagSet],
        }
        return response


    def import_volume(self, params: dict) -> dict:
        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")
        description = params.get("Description")
        dry_run = params.get("DryRun", False)
        image_params = params.get("Image")
        volume_params = params.get("Volume")

        # Validate required parameters
        if image_params is None:
            raise ValueError("Image parameter is required")
        if volume_params is None:
            raise ValueError("Volume parameter is required")
        if (availability_zone is None and availability_zone_id is None) or (availability_zone and availability_zone_id):
            raise ValueError("Either AvailabilityZone or AvailabilityZoneId must be specified, but not both")

        # DryRun check (not implemented)
        if dry_run:
            pass

        # Generate conversionTaskId and volume id
        conversion_task_id = self.generate_unique_id(prefix="import-")
        volume_id = self.generate_unique_id(prefix="vol-")

        # Compose DiskImageDescription
        image = DiskImageDescription(
            checksum=image_params.get("Checksum"),
            format=image_params.get("Format"),
            importManifestUrl=image_params.get("ImportManifestUrl"),
            size=image_params.get("Bytes"),
        )

        # Compose DiskImageVolumeDescription
        volume = DiskImageVolumeDescription(
            id=volume_id,
            size=volume_params.get("Size"),
        )

        # Compose ImportVolumeTaskDetails
        import_volume_task_details = ImportVolumeTaskDetails(
            availabilityZone=availability_zone,
            availabilityZoneId=availability_zone_id,
            bytesConverted=0,
            description=description,
            image=image,
            volume=volume,
        )

        # Compose ConversionTask
        conversion_task = ConversionTask(
            conversionTaskId=conversion_task_id,
            expirationTime=None,
            importInstance=None,
            importVolume=import_volume_task_details,
            state=ConversionTaskState.ACTIVE if hasattr(ConversionTaskState, "ACTIVE") else "active",
            statusMessage=None,
            tagSet=[],
        )

        # Store in state
        self.state.vm_import[conversion_task_id] = conversion_task

        # Compose response dictionary
        response = {
            "conversionTask": {
                "conversionTaskId": conversion_task.conversionTaskId,
                "expirationTime": conversion_task.expirationTime,
                "importInstance": None,
                "importVolume": {
                    "availabilityZone": import_volume_task_details.availabilityZone,
                    "availabilityZoneId": import_volume_task_details.availabilityZoneId,
                    "bytesConverted": import_volume_task_details.bytesConverted,
                    "description": import_volume_task_details.description,
                    "image": {
                        "checksum": import_volume_task_details.image.checksum,
                        "format": import_volume_task_details.image.format,
                        "importManifestUrl": import_volume_task_details.image.importManifestUrl,
                        "size": import_volume_task_details.image.size,
                    } if import_volume_task_details.image else None,
                    "volume": {
                        "id": import_volume_task_details.volume.id,
                        "size": import_volume_task_details.volume.size,
                    } if import_volume_task_details.volume else None,
                },
                "state": conversion_task.state,
                "statusMessage": conversion_task.statusMessage,
                "tagSet": [],
            },
            "requestId": self.generate_request_id(),
        }
    

from emulator_core.gateway.base import BaseGateway

class VMimportGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CancelConversionTask", self.cancel_conversion_task)
        self.register_action("CancelImportTask", self.cancel_import_task)
        self.register_action("DescribeConversionTasks", self.describe_conversion_tasks)
        self.register_action("DescribeImportImageTasks", self.describe_import_image_tasks)
        self.register_action("DescribeImportSnapshotTasks", self.describe_import_snapshot_tasks)
        self.register_action("ImportImage", self.import_image)
        self.register_action("ImportInstance", self.import_instance)
        self.register_action("ImportSnapshot", self.import_snapshot)
        self.register_action("ImportVolume", self.import_volume)

    def cancel_conversion_task(self, params):
        return self.backend.cancel_conversion_task(params)

    def cancel_import_task(self, params):
        return self.backend.cancel_import_task(params)

    def describe_conversion_tasks(self, params):
        return self.backend.describe_conversion_tasks(params)

    def describe_import_image_tasks(self, params):
        return self.backend.describe_import_image_tasks(params)

    def describe_import_snapshot_tasks(self, params):
        return self.backend.describe_import_snapshot_tasks(params)

    def import_image(self, params):
        return self.backend.import_image(params)

    def import_instance(self, params):
        return self.backend.import_instance(params)

    def import_snapshot(self, params):
        return self.backend.import_snapshot(params)

    def import_volume(self, params):
        return self.backend.import_volume(params)
