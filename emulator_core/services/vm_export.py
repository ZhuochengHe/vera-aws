from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class ExportTaskState(Enum):
    ACTIVE = "active"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ExportImageTaskState(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DELETING = "deleting"
    DELETED = "deleted"


class TargetEnvironment(Enum):
    CITRIX = "citrix"
    VMWARE = "vmware"
    MICROSOFT = "microsoft"


class DiskImageFormat(Enum):
    VMDK = "VMDK"
    RAW = "RAW"
    VHD = "VHD"


class ContainerFormat(Enum):
    OVA = "ova"


@dataclass
class Tag:
    Key: str
    Value: str


def validate_tags(tags: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Validate tags list and return dict of key->value.
    Raise ErrorCode if invalid.
    """
    tag_dict = {}
    for tag in tags:
        key = tag.get("Key")
        value = tag.get("Value")
        if key is None or not isinstance(key, str):
            raise ErrorCode("InvalidParameterValue", "Tag Key must be a string and not None")
        if key.lower().startswith("aws:"):
            raise ErrorCode("InvalidParameterValue", "Tag Key may not begin with 'aws:'")
        if len(key) > 127:
            raise ErrorCode("InvalidParameterValue", "Tag Key must be at most 127 Unicode characters")
        if value is not None and not isinstance(value, str):
            raise ErrorCode("InvalidParameterValue", "Tag Value must be a string if specified")
        if value is not None and len(value) > 256:
            raise ErrorCode("InvalidParameterValue", "Tag Value must be at most 256 Unicode characters")
        tag_dict[key] = value if value is not None else ""
    return tag_dict


@dataclass
class ExportToS3TaskSpecification:
    container_format: Optional[ContainerFormat] = None
    disk_image_format: Optional[DiskImageFormat] = None
    s3_bucket: Optional[str] = None
    s3_prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.container_format:
            d["containerFormat"] = self.container_format.value
        if self.disk_image_format:
            d["diskImageFormat"] = self.disk_image_format.value
        if self.s3_bucket:
            d["s3Bucket"] = self.s3_bucket
        if self.s3_prefix:
            d["s3Key"] = self.s3_prefix
        return d


@dataclass
class InstanceExportDetails:
    instance_id: str
    target_environment: TargetEnvironment

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instanceId": self.instance_id,
            "targetEnvironment": self.target_environment.value,
        }


@dataclass
class ExportTask:
    export_task_id: str
    description: Optional[str] = None
    export_to_s3: Optional[ExportToS3TaskSpecification] = None
    instance_export: Optional[InstanceExportDetails] = None
    state: ExportTaskState = ExportTaskState.ACTIVE
    status_message: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "exportTaskId": self.export_task_id,
            "state": self.state.value,
            "statusMessage": self.status_message or "",
            "tagSet": [{"Key": k, "Value": v} for k, v in self.tags.items()],
        }
        if self.description:
            d["description"] = self.description
        if self.export_to_s3:
            d["exportToS3"] = self.export_to_s3.to_dict()
        if self.instance_export:
            d["instanceExport"] = self.instance_export.to_dict()
        return d


@dataclass
class ExportTaskS3Location:
    s3_bucket: str
    s3_prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"s3Bucket": self.s3_bucket}
        if self.s3_prefix:
            d["s3Prefix"] = self.s3_prefix
        return d


@dataclass
class ExportImageTask:
    export_image_task_id: str
    description: Optional[str] = None
    disk_image_format: DiskImageFormat = None
    image_id: str = None
    progress: Optional[str] = None
    s3_export_location: Optional[ExportTaskS3Location] = None
    status: ExportImageTaskState = ExportImageTaskState.ACTIVE
    status_message: Optional[str] = None
    role_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "exportImageTaskId": self.export_image_task_id,
            "diskImageFormat": self.disk_image_format.value if self.disk_image_format else None,
            "imageId": self.image_id,
            "status": self.status.value,
            "progress": self.progress or "",
            "statusMessage": self.status_message or "",
            "tagSet": [{"Key": k, "Value": v} for k, v in self.tags.items()],
        }
        if self.description:
            d["description"] = self.description
        if self.s3_export_location:
            d["s3ExportLocation"] = self.s3_export_location.to_dict()
        if self.role_name:
            d["roleName"] = self.role_name
        return d


class VmExportBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.vm_export for export tasks
        # Use self.state.vm_export_image for export image tasks
        # Initialize dicts if not present
        if not hasattr(self.state, "vm_export"):
            self.state.vm_export = {}
        if not hasattr(self.state, "vm_export_image"):
            self.state.vm_export_image = {}

    def _parse_tags_from_tag_specifications(self, tag_specifications: Optional[List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Parses TagSpecification.N from params and returns dict of tags.
        Only tags with ResourceType 'export-instance-task' or 'export-image-task' are accepted.
        """
        tags = {}
        if not tag_specifications:
            return tags
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if resource_type not in ("export-instance-task", "export-image-task"):
                # According to AWS, tags with other resource types are ignored for export tasks
                continue
            tag_list = tag_spec.get("Tags", [])
            tags.update(validate_tags(tag_list))
        return tags

    def CancelExportTask(self, params: Dict[str, Any]) -> Dict[str, Any]:
        export_task_id = params.get("ExportTaskId")
        if not export_task_id or not isinstance(export_task_id, str):
            raise ErrorCode("MissingParameter", "ExportTaskId is required and must be a string")

        export_task: ExportTask = self.state.vm_export.get(export_task_id)
        if not export_task:
            # AWS returns an error if task does not exist
            raise ErrorCode("InvalidExportTaskId.NotFound", f"Export task {export_task_id} does not exist")

        # If task is completed or transferring final disk image (simulate as COMPLETED state), fail
        if export_task.state in (ExportTaskState.COMPLETED, ExportTaskState.CANCELLED):
            raise ErrorCode("IncorrectState", f"Cannot cancel export task in state {export_task.state.value}")

        # Cancel the task
        export_task.state = ExportTaskState.CANCELLED
        export_task.status_message = "Cancelled"
        # Remove all artifacts - simulate by removing from state
        del self.state.vm_export[export_task_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def CreateInstanceExportTask(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Required params: InstanceId, ExportToS3, TargetEnvironment
        instance_id = params.get("InstanceId")
        export_to_s3_params = params.get("ExportToS3")
        target_environment_str = params.get("TargetEnvironment")
        description = params.get("Description")
        tag_specifications = params.get("TagSpecification.N") or params.get("TagSpecification")

        if not instance_id or not isinstance(instance_id, str):
            raise ErrorCode("MissingParameter", "InstanceId is required and must be a string")

        if not export_to_s3_params or not isinstance(export_to_s3_params, dict):
            raise ErrorCode("MissingParameter", "ExportToS3 is required and must be an object")

        if not target_environment_str or not isinstance(target_environment_str, str):
            raise ErrorCode("MissingParameter", "TargetEnvironment is required and must be a string")

        # Validate target environment
        try:
            target_environment = TargetEnvironment(target_environment_str.lower())
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid TargetEnvironment: {target_environment_str}")

        # Validate ExportToS3 fields
        container_format_str = export_to_s3_params.get("ContainerFormat")
        disk_image_format_str = export_to_s3_params.get("DiskImageFormat")
        s3_bucket = export_to_s3_params.get("S3Bucket")
        s3_prefix = export_to_s3_params.get("S3Prefix")

        container_format = None
        if container_format_str:
            try:
                container_format = ContainerFormat(container_format_str.lower())
            except ValueError:
                raise ErrorCode("InvalidParameterValue", f"Invalid ContainerFormat: {container_format_str}")

        disk_image_format = None
        if disk_image_format_str:
            try:
                disk_image_format = DiskImageFormat(disk_image_format_str.upper())
            except ValueError:
                raise ErrorCode("InvalidParameterValue", f"Invalid DiskImageFormat: {disk_image_format_str}")

        # S3Bucket is optional but if provided must be string
        if s3_bucket is not None and not isinstance(s3_bucket, str):
            raise ErrorCode("InvalidParameterValue", "S3Bucket must be a string if specified")

        if s3_prefix is not None and not isinstance(s3_prefix, str):
            raise ErrorCode("InvalidParameterValue", "S3Prefix must be a string if specified")

        # Validate instance exists
        instance = self.state.get_resource(instance_id)
        if not instance:
            raise ErrorCode("InvalidInstanceID.NotFound", f"Instance {instance_id} does not exist")

        # Validate tags
        tags = self._parse_tags_from_tag_specifications(tag_specifications)

        # Generate export task id
        export_task_id = f"export-{self.generate_unique_id()}"

        # Compose s3Key: s3prefix + exportTaskId + '.' + diskImageFormat (lowercase)
        s3_key = None
        if s3_prefix:
            s3_key = f"{s3_prefix}{export_task_id}."
            if disk_image_format:
                s3_key += disk_image_format.value.lower()
            else:
                s3_key += "img"
        else:
            if disk_image_format:
                s3_key = f"{export_task_id}.{disk_image_format.value.lower()}"
            else:
                s3_key = f"{export_task_id}.img"

        export_to_s3 = ExportToS3TaskSpecification(
            container_format=container_format,
            disk_image_format=disk_image_format,
            s3_bucket=s3_bucket,
            s3_prefix=s3_key,
        )

        instance_export = InstanceExportDetails(
            instance_id=instance_id,
            target_environment=target_environment,
        )

        export_task = ExportTask(
            export_task_id=export_task_id,
            description=description,
            export_to_s3=export_to_s3,
            instance_export=instance_export,
            state=ExportTaskState.ACTIVE,
            status_message="Running",
            tags=tags,
        )

        self.state.vm_export[export_task_id] = export_task

        return {
            "requestId": self.generate_request_id(),
            "exportTask": export_task.to_dict(),
        }

    def DescribeExportTasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Optional params: ExportTaskId.N (list), Filter.N (list of filters)
        export_task_ids = params.get("ExportTaskId.N") or params.get("ExportTaskId") or []
        filters = params.get("Filter.N") or params.get("Filter") or []

        # Validate export_task_ids is list of strings if provided
        if export_task_ids and not isinstance(export_task_ids, list):
            raise ErrorCode("InvalidParameterValue", "ExportTaskId.N must be a list of strings")
        if export_task_ids:
            for etid in export_task_ids:
                if not isinstance(etid, str):
                    raise ErrorCode("InvalidParameterValue", "ExportTaskId.N must be a list of strings")

        # Validate filters
        # Filters can be on state, statusMessage, instanceId, targetEnvironment, etc.
        # We'll support filtering on state and instanceId for simplicity
        filter_map = {}
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not isinstance(name, str):
                raise ErrorCode("InvalidParameterValue", "Filter Name must be a string")
            if not isinstance(values, list):
                raise ErrorCode("InvalidParameterValue", "Filter Values must be a list of strings")
            filter_map[name] = values

        # Collect export tasks
        tasks = list(self.state.vm_export.values())

        # Filter by export_task_ids if provided
        if export_task_ids:
            tasks = [t for t in tasks if t.export_task_id in export_task_ids]

        # Apply filters
        def matches_filters(task: ExportTask) -> bool:
            for name, values in filter_map.items():
                if name == "task-state":
                    # values are like active, cancelling, cancelled, completed
                    if task.state.value not in values:
                        return False
                elif name == "instance-id":
                    if not task.instance_export or task.instance_export.instance_id not in values:
                        return False
                elif name == "target-environment":
                    if not task.instance_export or task.instance_export.target_environment.value not in values:
                        return False
                elif name == "export-task-id":
                    if task.export_task_id not in values:
                        return False
                # Other filters can be added here
            return True

        tasks = [t for t in tasks if matches_filters(t)]

        # Compose response
        export_task_set = [t.to_dict() for t in tasks]

        return {
            "requestId": self.generate_request_id(),
            "exportTaskSet": export_task_set,
        }

    def ExportImage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Required: DiskImageFormat, ImageId, S3ExportLocation
        disk_image_format_str = params.get("DiskImageFormat")
        image_id = params.get("ImageId")
        s3_export_location_params = params.get("S3ExportLocation")
        description = params.get("Description")
        client_token = params.get("ClientToken")
        role_name = params.get("RoleName")
        tag_specifications = params.get("TagSpecification.N") or params.get("TagSpecification")

        if not disk_image_format_str or not isinstance(disk_image_format_str, str):
            raise ErrorCode("MissingParameter", "DiskImageFormat is required and must be a string")

        if not image_id or not isinstance(image_id, str):
            raise ErrorCode("MissingParameter", "ImageId is required and must be a string")

        if not s3_export_location_params or not isinstance(s3_export_location_params, dict):
            raise ErrorCode("MissingParameter", "S3ExportLocation is required and must be an object")

        # Validate disk image format
        try:
            disk_image_format = DiskImageFormat(disk_image_format_str.upper())
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid DiskImageFormat: {disk_image_format_str}")

        # Validate S3ExportLocation fields
        s3_bucket = s3_export_location_params.get("S3Bucket")
        s3_prefix = s3_export_location_params.get("S3Prefix")

        if not s3_bucket or not isinstance(s3_bucket, str):
            raise ErrorCode("MissingParameter", "S3ExportLocation.S3Bucket is required and must be a string")

        if s3_prefix is not None and not isinstance(s3_prefix, str):
            raise ErrorCode("InvalidParameterValue", "S3ExportLocation.S3Prefix must be a string if specified")

        # Validate image exists
        image = self.state.get_resource(image_id)
        if not image:
            raise ErrorCode("InvalidAMIID.NotFound", f"Image {image_id} does not exist")

        # Validate tags
        tags = self._parse_tags_from_tag_specifications(tag_specifications)

        # Generate export image task id
        export_image_task_id = f"export-image-{self.generate_unique_id()}"

        s3_export_location = ExportTaskS3Location(
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
        )

        export_image_task = ExportImageTask(
            export_image_task_id=export_image_task_id,
            description=description,
            disk_image_format=disk_image_format,
            image_id=image_id,
            progress="0%",
            s3_export_location=s3_export_location,
            status=ExportImageTaskState.ACTIVE,
            status_message="In progress",
            role_name=role_name,
            tags=tags,
        )

        self.state.vm_export_image[export_image_task_id] = export_image_task

        return {
            "requestId": self.generate_request_id(),
            "exportImageTaskId": export_image_task.export_image_task_id,
            "description": export_image_task.description,
            "diskImageFormat": export_image_task.disk_image_format.value,
            "imageId": export_image_task.image_id,
            "progress": export_image_task.progress,
            "roleName": export_image_task.role_name,
            "status": export_image_task.status.value,
            "statusMessage": export_image_task.status_message,
            "s3ExportLocation": export_image_task.s3_export_location.to_dict(),
            "tagSet": [{"Key": k, "Value": v} for k, v in export_image_task.tags.items()],
        }

    def DescribeExportImageTasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Optional params: ExportImageTaskId.N (list), Filter.N (list of filters), MaxResults, NextToken, DryRun
        export_image_task_ids = params.get("ExportImageTaskId.N") or params.get("ExportImageTaskId") or []
        filters = params.get("Filter.N")

from emulator_core.gateway.base import BaseGateway

class VMexportGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CancelExportTask", self.cancel_export_task)
        self.register_action("CreateInstanceExportTask", self.create_instance_export_task)
        self.register_action("DescribeExportImageTasks", self.describe_export_image_tasks)
        self.register_action("DescribeExportTasks", self.describe_export_tasks)
        self.register_action("ExportImage", self.export_image)

    def cancel_export_task(self, params):
        return self.backend.cancel_export_task(params)

    def create_instance_export_task(self, params):
        return self.backend.create_instance_export_task(params)

    def describe_export_image_tasks(self, params):
        return self.backend.describe_export_image_tasks(params)

    def describe_export_tasks(self, params):
        return self.backend.describe_export_tasks(params)

    def export_image(self, params):
        return self.backend.export_image(params)
