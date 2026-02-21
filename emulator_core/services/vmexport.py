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
class VmExport:
    description: str = ""
    export_image_task_id: str = ""
    image_id: str = ""
    progress: str = ""
    s3_export_location: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    status_message: str = ""
    tag_set: List[Any] = field(default_factory=list)

    export_task_id: str = ""
    instance_id: str = ""
    target_environment: str = ""
    export_to_s3: Dict[str, Any] = field(default_factory=dict)
    disk_image_format: str = ""
    role_name: str = ""
    client_token: str = ""
    task_type: str = ""
    state: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "exportImageTaskId": self.export_image_task_id,
            "imageId": self.image_id,
            "progress": self.progress,
            "s3ExportLocation": self.s3_export_location,
            "status": self.status,
            "statusMessage": self.status_message,
            "tagSet": self.tag_set,
            "exportTaskId": self.export_task_id,
            "instanceId": self.instance_id,
            "targetEnvironment": self.target_environment,
            "exportToS3": self.export_to_s3,
            "diskImageFormat": self.disk_image_format,
            "roleName": self.role_name,
            "clientToken": self.client_token,
            "taskType": self.task_type,
            "state": self.state,
        }

class VmExport_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.vm_export  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.amis.get(params['image_id']).vm_export_ids.append(new_id)
    #   Delete: self.state.amis.get(resource.image_id).vm_export_ids.remove(resource_id)


    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            value = params.get(key)
            if value is None or value == "":
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _get_resource_or_error(self, store: Dict[str, Any], resource_id: str, error_code: str, message: str):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message)
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources = []
        for resource_id in resource_ids:
            resource = store.get(resource_id)
            if not resource:
                return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
            resources.append(resource)
        return resources, None

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if resource_type and spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def CancelExportTask(self, params: Dict[str, Any]):
        """Cancels an active export task. The request removes all artifacts of the export, including any partially-created
   Amazon S3 objects. If the export task is complete or is in the process of transferring the final disk image, the
   command fails and returns an error."""

        error = self._require_params(params, ["ExportTaskId"])
        if error:
            return error

        export_task_id = params.get("ExportTaskId")
        resource, error = self._get_resource_or_error(
            self.resources,
            export_task_id,
            "InvalidExportTaskId.NotFound",
            f"The ID '{export_task_id}' does not exist",
        )
        if error:
            return error

        del self.resources[export_task_id]

        return {
            'return': True,
            }

    def CreateInstanceExportTask(self, params: Dict[str, Any]):
        """Exports a running or stopped instance to an Amazon S3 bucket. For information about the prerequisites for your Amazon S3 bucket, supported operating systems,
   image formats, and known limitations for the types of instances you can export, seeExporting an instance as a VM Using VM
    Import/Export"""

        error = self._require_params(params, ["ExportToS3", "InstanceId", "TargetEnvironment"])
        if error:
            return error

        instance_id = params.get("InstanceId")
        instance = self.state.instances.get(instance_id)
        if not instance:
            return create_error_response("InvalidInstanceID.NotFound", f"Instance '{instance_id}' does not exist.")

        export_to_s3 = params.get("ExportToS3")
        if not isinstance(export_to_s3, dict):
            export_to_s3 = {}

        export_task_id = self._generate_id("export")
        description = params.get("Description") or ""
        target_environment = params.get("TargetEnvironment") or ""
        tag_set = self._extract_tags(params.get("TagSpecification.N", []))

        resource = VmExport(
            description=description,
            export_task_id=export_task_id,
            instance_id=instance_id,
            target_environment=target_environment,
            export_to_s3=export_to_s3,
            state="active",
            status_message="",
            tag_set=tag_set,
            task_type="instance",
        )
        self.resources[export_task_id] = resource

        return {
            'exportTask': {
                'description': resource.description,
                'exportTaskId': resource.export_task_id,
                'exportToS3': {
                    'containerFormat': export_to_s3.get("ContainerFormat") or export_to_s3.get("containerFormat"),
                    'diskImageFormat': export_to_s3.get("DiskImageFormat") or export_to_s3.get("diskImageFormat"),
                    's3Bucket': export_to_s3.get("S3Bucket") or export_to_s3.get("s3Bucket"),
                    's3Key': export_to_s3.get("S3Key") or export_to_s3.get("s3Key"),
                    },
                'instanceExport': {
                    'instanceId': resource.instance_id,
                    'targetEnvironment': resource.target_environment,
                    },
                'state': resource.state,
                'statusMessage': resource.status_message,
                'tagSet': resource.tag_set,
                },
            }

    def DescribeExportImageTasks(self, params: Dict[str, Any]):
        """Describes the specified export image tasks or all of your export image tasks."""

        export_image_task_ids = params.get("ExportImageTaskId.N", []) or []
        if export_image_task_ids:
            resources = []
            for task_id in export_image_task_ids:
                resource = self.resources.get(task_id)
                if not resource or resource.task_type != "image":
                    return create_error_response("InvalidExportImageTaskId.NotFound", f"The ID '{task_id}' does not exist")
                resources.append(resource)
        else:
            resources = [
                resource for resource in self.resources.values()
                if resource.task_type == "image"
            ]

        filtered = apply_filters(resources, params.get("Filter.N", []))
        export_image_tasks = [resource.to_dict() for resource in filtered]

        return {
            'exportImageTaskSet': export_image_tasks,
            'nextToken': None,
            }

    def DescribeExportTasks(self, params: Dict[str, Any]):
        """Describes the specified export instance tasks or all of your export instance tasks."""

        export_task_ids = params.get("ExportTaskId.N", []) or []
        if export_task_ids:
            resources = []
            for task_id in export_task_ids:
                resource = self.resources.get(task_id)
                if not resource or resource.task_type != "instance":
                    return create_error_response("InvalidExportTaskId.NotFound", f"The ID '{task_id}' does not exist")
                resources.append(resource)
        else:
            resources = [
                resource for resource in self.resources.values()
                if resource.task_type == "instance"
            ]

        filtered = apply_filters(resources, params.get("Filter.N", []))
        export_tasks = []
        for resource in filtered:
            export_to_s3 = resource.export_to_s3 or {}
            export_tasks.append({
                "description": resource.description,
                "exportTaskId": resource.export_task_id,
                "exportToS3": {
                    "containerFormat": export_to_s3.get("ContainerFormat") or export_to_s3.get("containerFormat"),
                    "diskImageFormat": export_to_s3.get("DiskImageFormat") or export_to_s3.get("diskImageFormat"),
                    "s3Bucket": export_to_s3.get("S3Bucket") or export_to_s3.get("s3Bucket"),
                    "s3Key": export_to_s3.get("S3Key") or export_to_s3.get("s3Key"),
                },
                "instanceExport": {
                    "instanceId": resource.instance_id,
                    "targetEnvironment": resource.target_environment,
                },
                "state": resource.state,
                "statusMessage": resource.status_message,
                "tagSet": resource.tag_set,
            })

        return {
            'exportTaskSet': export_tasks,
            }

    def ExportImage(self, params: Dict[str, Any]):
        """Exports an Amazon Machine Image (AMI) to a VM file. For more information, seeExporting a VM
    directly from an Amazon Machine Image (AMI)in theVM Import/Export User Guide."""

        error = self._require_params(params, ["DiskImageFormat", "ImageId", "S3ExportLocation"])
        if error:
            return error

        image_id = params.get("ImageId")
        image = self.state.amis.get(image_id)
        if not image:
            return create_error_response("InvalidAMIID.NotFound", f"The ID '{image_id}' does not exist")

        s3_export_location = params.get("S3ExportLocation")
        if not isinstance(s3_export_location, dict):
            s3_export_location = {}

        export_image_task_id = self._generate_id("export")
        description = params.get("Description") or ""
        disk_image_format = params.get("DiskImageFormat") or ""
        role_name = params.get("RoleName") or ""
        client_token = params.get("ClientToken") or ""
        tag_set = self._extract_tags(params.get("TagSpecification.N", []))

        resource = VmExport(
            description=description,
            export_image_task_id=export_image_task_id,
            image_id=image_id,
            progress="0",
            s3_export_location=s3_export_location,
            status="active",
            status_message="",
            tag_set=tag_set,
            disk_image_format=disk_image_format,
            role_name=role_name,
            client_token=client_token,
            task_type="image",
        )
        self.resources[export_image_task_id] = resource

        if image and hasattr(image, "vm_export_ids"):
            image.vm_export_ids.append(export_image_task_id)

        return {
            'description': resource.description,
            'diskImageFormat': resource.disk_image_format,
            'exportImageTaskId': resource.export_image_task_id,
            'imageId': resource.image_id,
            'progress': resource.progress,
            'roleName': resource.role_name,
            's3ExportLocation': {
                's3Bucket': s3_export_location.get("S3Bucket") or s3_export_location.get("s3Bucket"),
                's3Prefix': s3_export_location.get("S3Prefix") or s3_export_location.get("s3Prefix"),
                },
            'status': resource.status,
            'statusMessage': resource.status_message,
            'tagSet': resource.tag_set,
            }

    def _generate_id(self, prefix: str = 'export') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class vmexport_RequestParser:
    @staticmethod
    def parse_cancel_export_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ExportTaskId": get_scalar(md, "ExportTaskId"),
        }

    @staticmethod
    def parse_create_instance_export_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "ExportToS3": get_scalar(md, "ExportToS3"),
            "InstanceId": get_scalar(md, "InstanceId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TargetEnvironment": get_scalar(md, "TargetEnvironment"),
        }

    @staticmethod
    def parse_describe_export_image_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExportImageTaskId.N": get_indexed_list(md, "ExportImageTaskId"),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_export_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ExportTaskId.N": get_indexed_list(md, "ExportTaskId"),
            "Filter.N": parse_filters(md, "Filter"),
        }

    @staticmethod
    def parse_export_image_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DiskImageFormat": get_scalar(md, "DiskImageFormat"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ImageId": get_scalar(md, "ImageId"),
            "RoleName": get_scalar(md, "RoleName"),
            "S3ExportLocation": get_scalar(md, "S3ExportLocation"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CancelExportTask": vmexport_RequestParser.parse_cancel_export_task_request,
            "CreateInstanceExportTask": vmexport_RequestParser.parse_create_instance_export_task_request,
            "DescribeExportImageTasks": vmexport_RequestParser.parse_describe_export_image_tasks_request,
            "DescribeExportTasks": vmexport_RequestParser.parse_describe_export_tasks_request,
            "ExportImage": vmexport_RequestParser.parse_export_image_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class vmexport_ResponseSerializer:
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
                xml_parts.extend(vmexport_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(vmexport_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(vmexport_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(vmexport_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(vmexport_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(vmexport_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_cancel_export_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelExportTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CancelExportTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_instance_export_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateInstanceExportTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize exportTask
        _exportTask_key = None
        if "exportTask" in data:
            _exportTask_key = "exportTask"
        elif "ExportTask" in data:
            _exportTask_key = "ExportTask"
        if _exportTask_key:
            param_data = data[_exportTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<exportTask>')
            xml_parts.extend(vmexport_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</exportTask>')
        xml_parts.append(f'</CreateInstanceExportTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_export_image_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeExportImageTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize exportImageTaskSet
        _exportImageTaskSet_key = None
        if "exportImageTaskSet" in data:
            _exportImageTaskSet_key = "exportImageTaskSet"
        elif "ExportImageTaskSet" in data:
            _exportImageTaskSet_key = "ExportImageTaskSet"
        elif "ExportImageTasks" in data:
            _exportImageTaskSet_key = "ExportImageTasks"
        if _exportImageTaskSet_key:
            param_data = data[_exportImageTaskSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<exportImageTaskSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vmexport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</exportImageTaskSet>')
            else:
                xml_parts.append(f'{indent_str}<exportImageTaskSet/>')
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
        xml_parts.append(f'</DescribeExportImageTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_export_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeExportTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize exportTaskSet
        _exportTaskSet_key = None
        if "exportTaskSet" in data:
            _exportTaskSet_key = "exportTaskSet"
        elif "ExportTaskSet" in data:
            _exportTaskSet_key = "ExportTaskSet"
        elif "ExportTasks" in data:
            _exportTaskSet_key = "ExportTasks"
        if _exportTaskSet_key:
            param_data = data[_exportTaskSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<exportTaskSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vmexport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</exportTaskSet>')
            else:
                xml_parts.append(f'{indent_str}<exportTaskSet/>')
        xml_parts.append(f'</DescribeExportTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_export_image_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ExportImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize diskImageFormat
        _diskImageFormat_key = None
        if "diskImageFormat" in data:
            _diskImageFormat_key = "diskImageFormat"
        elif "DiskImageFormat" in data:
            _diskImageFormat_key = "DiskImageFormat"
        if _diskImageFormat_key:
            param_data = data[_diskImageFormat_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<diskImageFormat>{esc(str(param_data))}</diskImageFormat>')
        # Serialize exportImageTaskId
        _exportImageTaskId_key = None
        if "exportImageTaskId" in data:
            _exportImageTaskId_key = "exportImageTaskId"
        elif "ExportImageTaskId" in data:
            _exportImageTaskId_key = "ExportImageTaskId"
        if _exportImageTaskId_key:
            param_data = data[_exportImageTaskId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<exportImageTaskId>{esc(str(param_data))}</exportImageTaskId>')
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
        # Serialize roleName
        _roleName_key = None
        if "roleName" in data:
            _roleName_key = "roleName"
        elif "RoleName" in data:
            _roleName_key = "RoleName"
        if _roleName_key:
            param_data = data[_roleName_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<roleName>{esc(str(param_data))}</roleName>')
        # Serialize s3ExportLocation
        _s3ExportLocation_key = None
        if "s3ExportLocation" in data:
            _s3ExportLocation_key = "s3ExportLocation"
        elif "S3ExportLocation" in data:
            _s3ExportLocation_key = "S3ExportLocation"
        if _s3ExportLocation_key:
            param_data = data[_s3ExportLocation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<s3ExportLocation>')
            xml_parts.extend(vmexport_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</s3ExportLocation>')
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
                    xml_parts.extend(vmexport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        xml_parts.append(f'</ExportImageResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CancelExportTask": vmexport_ResponseSerializer.serialize_cancel_export_task_response,
            "CreateInstanceExportTask": vmexport_ResponseSerializer.serialize_create_instance_export_task_response,
            "DescribeExportImageTasks": vmexport_ResponseSerializer.serialize_describe_export_image_tasks_response,
            "DescribeExportTasks": vmexport_ResponseSerializer.serialize_describe_export_tasks_response,
            "ExportImage": vmexport_ResponseSerializer.serialize_export_image_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

