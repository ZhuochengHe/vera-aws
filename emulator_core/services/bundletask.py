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
class BundleTask:
    bundle_id: str = ""
    error: Dict[str, Any] = field(default_factory=dict)
    instance_id: str = ""
    progress: str = ""
    start_time: str = ""
    state: str = ""
    storage: Dict[str, Any] = field(default_factory=dict)
    update_time: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundleId": self.bundle_id,
            "error": self.error,
            "instanceId": self.instance_id,
            "progress": self.progress,
            "startTime": self.start_time,
            "state": self.state,
            "storage": self.storage,
            "updateTime": self.update_time,
        }

class BundleTask_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.bundle_tasks  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.instances.get(params['instance_id']).bundle_task_ids.append(new_id)
    #   Delete: self.state.instances.get(resource.instance_id).bundle_task_ids.remove(resource_id)


    def BundleInstance(self, params: Dict[str, Any]):
        """Bundles an Amazon instance store-backed Windows instance. During bundling, only the root device volume (C:\) is bundled. Data on other instance
      store volumes is not preserved. This action is not applicable for Linux/Unix instances or Windows instances that are
        backed by Amazon EBS."""

        instance_id = params.get("InstanceId")
        if not instance_id:
            return create_error_response("MissingParameter", "The request must contain the parameter InstanceId")

        storage = params.get("Storage")
        if not storage:
            return create_error_response("MissingParameter", "The request must contain the parameter Storage")

        instance = self.state.instances.get(instance_id)
        if not instance:
            return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        bundle_id = self._generate_id("bundle")
        now = datetime.now(timezone.utc).isoformat()
        storage_value = storage if isinstance(storage, dict) else {"S3": storage}

        resource = BundleTask(
            bundle_id=bundle_id,
            error={},
            instance_id=instance_id,
            progress="0%",
            start_time=now,
            state="pending",
            storage=storage_value,
            update_time=now,
        )
        self.resources[bundle_id] = resource

        if not hasattr(instance, "bundle_task_ids"):
            instance.bundle_task_ids = []
        instance.bundle_task_ids.append(bundle_id)

        return {
            'bundleInstanceTask': resource.to_dict(),
            }

    def CancelBundleTask(self, params: Dict[str, Any]):
        """Cancels a bundling operation for an instance store-backed Windows instance."""

        bundle_id = params.get("BundleId")
        if not bundle_id:
            return create_error_response("MissingParameter", "The request must contain the parameter BundleId")

        resource = self.resources.get(bundle_id)
        if not resource:
            return create_error_response("InvalidBundleId.NotFound", f"The ID '{bundle_id}' does not exist")

        resource.state = "cancelled"
        resource.update_time = datetime.now(timezone.utc).isoformat()
        if not resource.error:
            resource.error = {
                "code": "Client.Cancelled",
                "message": "Bundle task cancelled",
            }

        return {
            'bundleInstanceTask': resource.to_dict(),
            }

    def DescribeBundleTasks(self, params: Dict[str, Any]):
        """Describes the specified bundle tasks or all of your bundle tasks. Completed bundle tasks are listed for only a limited time. If your bundle task is no
        longer in the list, you can still register an AMI from it. Just useRegisterImagewith the Amazon S3 bucket name and image manifest name you pr"""

        bundle_ids = params.get("BundleId.N", [])
        filters = params.get("Filter.N", [])

        if bundle_ids:
            for bundle_id in bundle_ids:
                if bundle_id not in self.resources:
                    return create_error_response("InvalidBundleId.NotFound", f"The ID '{bundle_id}' does not exist")
            resources = [self.resources[bundle_id] for bundle_id in bundle_ids]
        else:
            resources = list(self.resources.values())

        if filters:
            resources = apply_filters(resources, filters)

        return {
            'bundleInstanceTasksSet': [resource.to_dict() for resource in resources],
            }

    def _generate_id(self, prefix: str = 'bundle') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class bundletask_RequestParser:
    @staticmethod
    def parse_bundle_instance_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "Storage": get_scalar(md, "Storage"),
        }

    @staticmethod
    def parse_cancel_bundle_task_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "BundleId": get_scalar(md, "BundleId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_bundle_tasks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "BundleId.N": get_indexed_list(md, "BundleId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "BundleInstance": bundletask_RequestParser.parse_bundle_instance_request,
            "CancelBundleTask": bundletask_RequestParser.parse_cancel_bundle_task_request,
            "DescribeBundleTasks": bundletask_RequestParser.parse_describe_bundle_tasks_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class bundletask_ResponseSerializer:
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
                xml_parts.extend(bundletask_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(bundletask_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(bundletask_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(bundletask_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(bundletask_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(bundletask_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_bundle_instance_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<BundleInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize bundleInstanceTask
        _bundleInstanceTask_key = None
        if "bundleInstanceTask" in data:
            _bundleInstanceTask_key = "bundleInstanceTask"
        elif "BundleInstanceTask" in data:
            _bundleInstanceTask_key = "BundleInstanceTask"
        if _bundleInstanceTask_key:
            param_data = data[_bundleInstanceTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<bundleInstanceTask>')
            xml_parts.extend(bundletask_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</bundleInstanceTask>')
        xml_parts.append(f'</BundleInstanceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_cancel_bundle_task_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelBundleTaskResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize bundleInstanceTask
        _bundleInstanceTask_key = None
        if "bundleInstanceTask" in data:
            _bundleInstanceTask_key = "bundleInstanceTask"
        elif "BundleInstanceTask" in data:
            _bundleInstanceTask_key = "BundleInstanceTask"
        if _bundleInstanceTask_key:
            param_data = data[_bundleInstanceTask_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<bundleInstanceTask>')
            xml_parts.extend(bundletask_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</bundleInstanceTask>')
        xml_parts.append(f'</CancelBundleTaskResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_bundle_tasks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeBundleTasksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize bundleInstanceTasksSet
        _bundleInstanceTasksSet_key = None
        if "bundleInstanceTasksSet" in data:
            _bundleInstanceTasksSet_key = "bundleInstanceTasksSet"
        elif "BundleInstanceTasksSet" in data:
            _bundleInstanceTasksSet_key = "BundleInstanceTasksSet"
        elif "BundleInstanceTaskss" in data:
            _bundleInstanceTasksSet_key = "BundleInstanceTaskss"
        if _bundleInstanceTasksSet_key:
            param_data = data[_bundleInstanceTasksSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<bundleInstanceTasksSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(bundletask_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</bundleInstanceTasksSet>')
            else:
                xml_parts.append(f'{indent_str}<bundleInstanceTasksSet/>')
        xml_parts.append(f'</DescribeBundleTasksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "BundleInstance": bundletask_ResponseSerializer.serialize_bundle_instance_response,
            "CancelBundleTask": bundletask_ResponseSerializer.serialize_cancel_bundle_task_response,
            "DescribeBundleTasks": bundletask_ResponseSerializer.serialize_describe_bundle_tasks_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

