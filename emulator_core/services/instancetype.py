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
class InstanceType:
    auto_recovery_supported: bool = False
    bare_metal: bool = False
    burstable_performance_supported: bool = False
    current_generation: bool = False
    dedicated_hosts_supported: bool = False
    ebs_info: Dict[str, Any] = field(default_factory=dict)
    fpga_info: Dict[str, Any] = field(default_factory=dict)
    free_tier_eligible: bool = False
    gpu_info: Dict[str, Any] = field(default_factory=dict)
    hibernation_supported: bool = False
    hypervisor: str = ""
    inference_accelerator_info: Dict[str, Any] = field(default_factory=dict)
    instance_storage_info: Dict[str, Any] = field(default_factory=dict)
    instance_storage_supported: bool = False
    instance_type: str = ""
    media_accelerator_info: Dict[str, Any] = field(default_factory=dict)
    memory_info: Dict[str, Any] = field(default_factory=dict)
    network_info: Dict[str, Any] = field(default_factory=dict)
    neuron_info: Dict[str, Any] = field(default_factory=dict)
    nitro_enclaves_support: str = ""
    nitro_tpm_info: Dict[str, Any] = field(default_factory=dict)
    nitro_tpm_support: str = ""
    phc_support: str = ""
    placement_group_info: Dict[str, Any] = field(default_factory=dict)
    processor_info: Dict[str, Any] = field(default_factory=dict)
    reboot_migration_support: str = ""
    supported_boot_modes: List[Any] = field(default_factory=list)
    supported_root_device_types: List[Any] = field(default_factory=list)
    supported_usage_classes: List[Any] = field(default_factory=list)
    supported_virtualization_types: List[Any] = field(default_factory=list)
    v_cpu_info: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "autoRecoverySupported": self.auto_recovery_supported,
            "bareMetal": self.bare_metal,
            "burstablePerformanceSupported": self.burstable_performance_supported,
            "currentGeneration": self.current_generation,
            "dedicatedHostsSupported": self.dedicated_hosts_supported,
            "ebsInfo": self.ebs_info,
            "fpgaInfo": self.fpga_info,
            "freeTierEligible": self.free_tier_eligible,
            "gpuInfo": self.gpu_info,
            "hibernationSupported": self.hibernation_supported,
            "hypervisor": self.hypervisor,
            "inferenceAcceleratorInfo": self.inference_accelerator_info,
            "instanceStorageInfo": self.instance_storage_info,
            "instanceStorageSupported": self.instance_storage_supported,
            "instanceType": self.instance_type,
            "mediaAcceleratorInfo": self.media_accelerator_info,
            "memoryInfo": self.memory_info,
            "networkInfo": self.network_info,
            "neuronInfo": self.neuron_info,
            "nitroEnclavesSupport": self.nitro_enclaves_support,
            "nitroTpmInfo": self.nitro_tpm_info,
            "nitroTpmSupport": self.nitro_tpm_support,
            "phcSupport": self.phc_support,
            "placementGroupInfo": self.placement_group_info,
            "processorInfo": self.processor_info,
            "rebootMigrationSupport": self.reboot_migration_support,
            "supportedBootModes": self.supported_boot_modes,
            "supportedRootDeviceTypes": self.supported_root_device_types,
            "supportedUsageClasses": self.supported_usage_classes,
            "supportedVirtualizationTypes": self.supported_virtualization_types,
            "vCpuInfo": self.v_cpu_info,
        }

class InstanceType_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.instance_types  # alias to shared store


    def DescribeInstanceTypeOfferings(self, params: Dict[str, Any]):
        """Lists the instance types that are offered for the specified location. If no location is
   specified, the default is to list the instance types that are offered in the current
   Region."""

        filters = params.get("Filter.N", []) or []
        location_type = params.get("LocationType") or "region"

        locations = []
        for entry in filters:
            if entry.get("Name") == "location":
                locations = entry.get("Values") or []
                break
        if not locations:
            locations = ["us-east-1"]

        offerings = []
        for resource in self.resources.values():
            for location in locations:
                offerings.append({
                    "instance_type": resource.instance_type,
                    "location": location,
                    "location_type": location_type,
                })

        filtered = apply_filters(offerings, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None

        return {
            'instanceTypeOfferingSet': [
                {
                    "instanceType": item.get("instance_type"),
                    "location": item.get("location"),
                    "locationType": item.get("location_type"),
                }
                for item in page
            ],
            'nextToken': new_next_token,
            }

    def DescribeInstanceTypes(self, params: Dict[str, Any]):
        """Describes the specified instance types. By default, all instance types for the current
   Region are described. Alternatively, you can filter the results."""

        instance_type_names = params.get("InstanceType.N", []) or []
        if instance_type_names:
            resources: List[InstanceType] = []
            for instance_type in instance_type_names:
                resource = self.resources.get(instance_type)
                if not resource:
                    resource = next(
                        (entry for entry in self.resources.values() if entry.instance_type == instance_type),
                        None,
                    )
                if not resource:
                    return create_error_response(
                        "InvalidInstanceType.NotFound",
                        f"The ID '{instance_type}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        filtered = apply_filters(resources, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None

        return {
            'instanceTypeSet': [resource.to_dict() for resource in page],
            'nextToken': new_next_token,
            }

    def GetInstanceTypesFromInstanceRequirements(self, params: Dict[str, Any]):
        """Returns a list of instance types with the specified instance attributes. You can
         use the response to preview the instance types without launching instances. Note
         that the response does not consider capacity. When you specify multiple parameters, you get instance types that satisfy """

        required_params = ["ArchitectureType.N", "InstanceRequirements", "VirtualizationType.N"]
        for name in required_params:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")

        resources = list(self.resources.values())

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = resources[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(resources) else None

        return {
            'instanceTypeSet': [{"instanceType": resource.instance_type} for resource in page],
            'nextToken': new_next_token,
            }

    def _generate_id(self, prefix: str = 'ins') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class instancetype_RequestParser:
    @staticmethod
    def parse_describe_instance_type_offerings_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "LocationType": get_scalar(md, "LocationType"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_instance_types_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "InstanceType.N": get_indexed_list(md, "InstanceType"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_instance_types_from_instance_requirements_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ArchitectureType.N": get_indexed_list(md, "ArchitectureType"),
            "Context": get_scalar(md, "Context"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceRequirements": get_scalar(md, "InstanceRequirements"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VirtualizationType.N": get_indexed_list(md, "VirtualizationType"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeInstanceTypeOfferings": instancetype_RequestParser.parse_describe_instance_type_offerings_request,
            "DescribeInstanceTypes": instancetype_RequestParser.parse_describe_instance_types_request,
            "GetInstanceTypesFromInstanceRequirements": instancetype_RequestParser.parse_get_instance_types_from_instance_requirements_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class instancetype_ResponseSerializer:
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
                xml_parts.extend(instancetype_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(instancetype_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(instancetype_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(instancetype_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(instancetype_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(instancetype_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_instance_type_offerings_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceTypeOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceTypeOfferingSet
        _instanceTypeOfferingSet_key = None
        if "instanceTypeOfferingSet" in data:
            _instanceTypeOfferingSet_key = "instanceTypeOfferingSet"
        elif "InstanceTypeOfferingSet" in data:
            _instanceTypeOfferingSet_key = "InstanceTypeOfferingSet"
        elif "InstanceTypeOfferings" in data:
            _instanceTypeOfferingSet_key = "InstanceTypeOfferings"
        if _instanceTypeOfferingSet_key:
            param_data = data[_instanceTypeOfferingSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceTypeOfferingSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instancetype_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceTypeOfferingSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceTypeOfferingSet/>')
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
        xml_parts.append(f'</DescribeInstanceTypeOfferingsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_types_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceTypesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceTypeSet
        _instanceTypeSet_key = None
        if "instanceTypeSet" in data:
            _instanceTypeSet_key = "instanceTypeSet"
        elif "InstanceTypeSet" in data:
            _instanceTypeSet_key = "InstanceTypeSet"
        elif "InstanceTypes" in data:
            _instanceTypeSet_key = "InstanceTypes"
        if _instanceTypeSet_key:
            param_data = data[_instanceTypeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceTypeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instancetype_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceTypeSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceTypeSet/>')
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
        xml_parts.append(f'</DescribeInstanceTypesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_instance_types_from_instance_requirements_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetInstanceTypesFromInstanceRequirementsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceTypeSet
        _instanceTypeSet_key = None
        if "instanceTypeSet" in data:
            _instanceTypeSet_key = "instanceTypeSet"
        elif "InstanceTypeSet" in data:
            _instanceTypeSet_key = "InstanceTypeSet"
        elif "InstanceTypes" in data:
            _instanceTypeSet_key = "InstanceTypes"
        if _instanceTypeSet_key:
            param_data = data[_instanceTypeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceTypeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(instancetype_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceTypeSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceTypeSet/>')
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
        xml_parts.append(f'</GetInstanceTypesFromInstanceRequirementsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeInstanceTypeOfferings": instancetype_ResponseSerializer.serialize_describe_instance_type_offerings_response,
            "DescribeInstanceTypes": instancetype_ResponseSerializer.serialize_describe_instance_types_response,
            "GetInstanceTypesFromInstanceRequirements": instancetype_ResponseSerializer.serialize_get_instance_types_from_instance_requirements_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

