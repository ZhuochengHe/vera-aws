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
class VerifiedAccessLog:
    access_logs: Dict[str, Any] = field(default_factory=dict)
    verified_access_instance_id: str = ""

    # Internal dependency tracking — not in API response
    verified_access_endpoint_ids: List[str] = field(default_factory=list)  # tracks VerifiedAccessEndpoint children
    verified_access_group_ids: List[str] = field(default_factory=list)  # tracks VerifiedAccessGroup children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessLogs": self.access_logs,
            "verifiedAccessInstanceId": self.verified_access_instance_id,
        }

class VerifiedAccessLog_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.verified_access_logs  # alias to shared store


    def DescribeVerifiedAccessInstanceLoggingConfigurations(self, params: Dict[str, Any]):
        """Describes the specified AWS Verified Access instances."""

        instance_ids = params.get("VerifiedAccessInstanceId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if instance_ids:
            resources: List[VerifiedAccessLog] = []
            for instance_id in instance_ids:
                resource = self.resources.get(instance_id)
                if not resource:
                    return create_error_response(
                        "InvalidVerifiedAccessInstanceId.NotFound",
                        f"The ID '{instance_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        logging_configuration_set = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'loggingConfigurationSet': logging_configuration_set,
            'nextToken': None,
            }

    def ModifyVerifiedAccessInstanceLoggingConfiguration(self, params: Dict[str, Any]):
        """Modifies the logging configuration for the specified AWS Verified Access instance."""

        if not params.get("AccessLogs"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: AccessLogs",
            )

        if not params.get("VerifiedAccessInstanceId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessInstanceId",
            )

        instance_id = params.get("VerifiedAccessInstanceId")
        if not self.state.verified_access_instances.get(instance_id):
            return create_error_response(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The ID '{instance_id}' does not exist",
            )

        access_logs = params.get("AccessLogs") or {}
        resource = self.resources.get(instance_id)
        if not resource:
            resource = VerifiedAccessLog(
                access_logs=access_logs,
                verified_access_instance_id=instance_id,
            )
            self.resources[instance_id] = resource
        else:
            resource.access_logs = access_logs

        return {
            'loggingConfiguration': {
                'accessLogs': resource.access_logs,
                'verifiedAccessInstanceId': resource.verified_access_instance_id,
                },
            }

    def _generate_id(self, prefix: str = 'verified') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class verifiedaccesslog_RequestParser:
    @staticmethod
    def parse_describe_verified_access_instance_logging_configurations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VerifiedAccessInstanceId.N": get_indexed_list(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_modify_verified_access_instance_logging_configuration_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AccessLogs": get_scalar(md, "AccessLogs"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeVerifiedAccessInstanceLoggingConfigurations": verifiedaccesslog_RequestParser.parse_describe_verified_access_instance_logging_configurations_request,
            "ModifyVerifiedAccessInstanceLoggingConfiguration": verifiedaccesslog_RequestParser.parse_modify_verified_access_instance_logging_configuration_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class verifiedaccesslog_ResponseSerializer:
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
                xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_verified_access_instance_logging_configurations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVerifiedAccessInstanceLoggingConfigurationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize loggingConfigurationSet
        _loggingConfigurationSet_key = None
        if "loggingConfigurationSet" in data:
            _loggingConfigurationSet_key = "loggingConfigurationSet"
        elif "LoggingConfigurationSet" in data:
            _loggingConfigurationSet_key = "LoggingConfigurationSet"
        elif "LoggingConfigurations" in data:
            _loggingConfigurationSet_key = "LoggingConfigurations"
        if _loggingConfigurationSet_key:
            param_data = data[_loggingConfigurationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<loggingConfigurationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</loggingConfigurationSet>')
            else:
                xml_parts.append(f'{indent_str}<loggingConfigurationSet/>')
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
        xml_parts.append(f'</DescribeVerifiedAccessInstanceLoggingConfigurationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_verified_access_instance_logging_configuration_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVerifiedAccessInstanceLoggingConfigurationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize loggingConfiguration
        _loggingConfiguration_key = None
        if "loggingConfiguration" in data:
            _loggingConfiguration_key = "loggingConfiguration"
        elif "LoggingConfiguration" in data:
            _loggingConfiguration_key = "LoggingConfiguration"
        if _loggingConfiguration_key:
            param_data = data[_loggingConfiguration_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<loggingConfiguration>')
            xml_parts.extend(verifiedaccesslog_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</loggingConfiguration>')
        xml_parts.append(f'</ModifyVerifiedAccessInstanceLoggingConfigurationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeVerifiedAccessInstanceLoggingConfigurations": verifiedaccesslog_ResponseSerializer.serialize_describe_verified_access_instance_logging_configurations_response,
            "ModifyVerifiedAccessInstanceLoggingConfiguration": verifiedaccesslog_ResponseSerializer.serialize_modify_verified_access_instance_logging_configuration_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

