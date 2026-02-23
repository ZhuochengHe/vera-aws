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
class ElasticGraphic:
    availability_zone: str = ""
    elastic_gpu_health: Dict[str, Any] = field(default_factory=dict)
    elastic_gpu_id: str = ""
    elastic_gpu_state: str = ""
    elastic_gpu_type: str = ""
    instance_id: str = ""
    tag_set: List[Any] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "elasticGpuHealth": self.elastic_gpu_health,
            "elasticGpuId": self.elastic_gpu_id,
            "elasticGpuState": self.elastic_gpu_state,
            "elasticGpuType": self.elastic_gpu_type,
            "instanceId": self.instance_id,
            "tagSet": self.tag_set,
        }

class ElasticGraphic_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.elastic_graphics  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.instances.get(params['instance_id']).elastic_graphic_ids.append(new_id)
    #   Delete: self.state.instances.get(resource.instance_id).elastic_graphic_ids.remove(resource_id)


    def DescribeElasticGpus(self, params: Dict[str, Any]):
        """Amazon Elastic Graphics reached end of life on January 8, 2024. Describes the Elastic Graphics accelerator associated with your instances."""

        elastic_gpu_ids = params.get("ElasticGpuId.N", [])
        if elastic_gpu_ids:
            missing = [gpu_id for gpu_id in elastic_gpu_ids if gpu_id not in self.resources]
            if missing:
                return create_error_response(
                    "InvalidElasticGpuID.NotFound",
                    f"The ID '{missing[0]}' does not exist",
                )
            resources = [self.resources[gpu_id] for gpu_id in elastic_gpu_ids]
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))

        max_results_param = params.get("MaxResults")
        max_results = int(max_results_param or len(resources) or 0)
        start_index = int(params.get("NextToken") or 0)
        paged = resources[start_index:start_index + max_results]
        next_token = None
        if start_index + max_results < len(resources):
            next_token = str(start_index + max_results)

        max_results_response = [max_results] if max_results_param is not None or max_results else None

        return {
            'elasticGpuSet': [resource.to_dict() for resource in paged],
            'maxResults': max_results_response,
            'nextToken': next_token,
            }

    def _generate_id(self, prefix: str = 'elastic') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class elasticgraphic_RequestParser:
    @staticmethod
    def parse_describe_elastic_gpus_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ElasticGpuId.N": get_indexed_list(md, "ElasticGpuId"),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeElasticGpus": elasticgraphic_RequestParser.parse_describe_elastic_gpus_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class elasticgraphic_ResponseSerializer:
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
                xml_parts.extend(elasticgraphic_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(elasticgraphic_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(elasticgraphic_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(elasticgraphic_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(elasticgraphic_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(elasticgraphic_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_elastic_gpus_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeElasticGpusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize elasticGpuSet
        _elasticGpuSet_key = None
        if "elasticGpuSet" in data:
            _elasticGpuSet_key = "elasticGpuSet"
        elif "ElasticGpuSet" in data:
            _elasticGpuSet_key = "ElasticGpuSet"
        elif "ElasticGpus" in data:
            _elasticGpuSet_key = "ElasticGpus"
        if _elasticGpuSet_key:
            param_data = data[_elasticGpuSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<elasticGpuSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(elasticgraphic_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</elasticGpuSet>')
            else:
                xml_parts.append(f'{indent_str}<elasticGpuSet/>')
        # Serialize maxResults
        _maxResults_key = None
        if "maxResults" in data:
            _maxResults_key = "maxResults"
        elif "MaxResults" in data:
            _maxResults_key = "MaxResults"
        if _maxResults_key:
            param_data = data[_maxResults_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<maxResultsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</maxResultsSet>')
            else:
                xml_parts.append(f'{indent_str}<maxResultsSet/>')
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
        xml_parts.append(f'</DescribeElasticGpusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeElasticGpus": elasticgraphic_ResponseSerializer.serialize_describe_elastic_gpus_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

