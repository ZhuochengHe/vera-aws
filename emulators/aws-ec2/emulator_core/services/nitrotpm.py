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
class NitroTpm:
    instance_id: str = ""
    key_format: str = ""
    key_type: str = ""
    key_value: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instanceId": self.instance_id,
            "keyFormat": self.key_format,
            "keyType": self.key_type,
            "keyValue": self.key_value,
        }

class NitroTpm_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.nitro_tpm  # alias to shared store


    def GetInstanceTpmEkPub(self, params: Dict[str, Any]):
        """Gets the public endorsement key associated with the Nitro Trusted 
            Platform Module (NitroTPM) for the specified instance."""

        for name in ["InstanceId", "KeyFormat", "KeyType"]:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")

        instance_id = params.get("InstanceId") or ""
        instance = self.state.instances.get(instance_id)
        if not instance:
            return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")

        key_format = params.get("KeyFormat") or ""
        key_type = params.get("KeyType") or ""

        tpm = self.resources.get(instance_id)
        if not tpm:
            key_value = self._generate_id("nit")
            tpm = NitroTpm(
                instance_id=instance_id,
                key_format=key_format,
                key_type=key_type,
                key_value=key_value,
            )
            self.resources[instance_id] = tpm
        else:
            if tpm.key_format != key_format or tpm.key_type != key_type or not tpm.key_value:
                tpm.key_format = key_format
                tpm.key_type = key_type
                tpm.key_value = self._generate_id("nit")
            key_value = tpm.key_value

        return {
            'instanceId': instance_id,
            'keyFormat': key_format,
            'keyType': key_type,
            'keyValue': key_value,
            }

    def _generate_id(self, prefix: str = 'nit') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class nitrotpm_RequestParser:
    @staticmethod
    def parse_get_instance_tpm_ek_pub_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "KeyFormat": get_scalar(md, "KeyFormat"),
            "KeyType": get_scalar(md, "KeyType"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "GetInstanceTpmEkPub": nitrotpm_RequestParser.parse_get_instance_tpm_ek_pub_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class nitrotpm_ResponseSerializer:
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
                xml_parts.extend(nitrotpm_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(nitrotpm_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(nitrotpm_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(nitrotpm_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(nitrotpm_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(nitrotpm_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_get_instance_tpm_ek_pub_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetInstanceTpmEkPubResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize keyFormat
        _keyFormat_key = None
        if "keyFormat" in data:
            _keyFormat_key = "keyFormat"
        elif "KeyFormat" in data:
            _keyFormat_key = "KeyFormat"
        if _keyFormat_key:
            param_data = data[_keyFormat_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyFormat>{esc(str(param_data))}</keyFormat>')
        # Serialize keyType
        _keyType_key = None
        if "keyType" in data:
            _keyType_key = "keyType"
        elif "KeyType" in data:
            _keyType_key = "KeyType"
        if _keyType_key:
            param_data = data[_keyType_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyType>{esc(str(param_data))}</keyType>')
        # Serialize keyValue
        _keyValue_key = None
        if "keyValue" in data:
            _keyValue_key = "keyValue"
        elif "KeyValue" in data:
            _keyValue_key = "KeyValue"
        if _keyValue_key:
            param_data = data[_keyValue_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyValue>{esc(str(param_data))}</keyValue>')
        xml_parts.append(f'</GetInstanceTpmEkPubResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "GetInstanceTpmEkPub": nitrotpm_ResponseSerializer.serialize_get_instance_tpm_ek_pub_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

