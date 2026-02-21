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
class SerialConsole:

    serial_console_access_enabled: bool = False
    managed_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "serialConsoleAccessEnabled": self.serial_console_access_enabled,
            "managedBy": self.managed_by,
        }

class SerialConsole_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.serial_console  # alias to shared store

    def _get_or_create_console(self) -> SerialConsole:
        resource = self.resources.get("account")
        if not resource:
            resource = SerialConsole()
            self.resources["account"] = resource
        return resource


    # - Complex operations: _process_associations(params: Dict) -> Dict
    # Add any helper functions needed by the API methods below.
    # These helpers can be used by multiple API methods.

    def DisableSerialConsoleAccess(self, params: Dict[str, Any]):
        """Disables access to the EC2 serial console of all instances for your account. By default,
			access to the EC2 serial console is disabled for your account. For more information, seeManage account access to the EC2 serial consolein theAmazon EC2
				User Guide."""

        resource = self._get_or_create_console()
        resource.serial_console_access_enabled = False

        return {
            "serialConsoleAccessEnabled": resource.serial_console_access_enabled,
        }

    def EnableSerialConsoleAccess(self, params: Dict[str, Any]):
        """Enables access to the EC2 serial console of all instances for your account. By default,
			access to the EC2 serial console is disabled for your account. For more information, seeManage account access to the EC2 serial consolein theAmazon EC2 User Guide."""

        resource = self._get_or_create_console()
        resource.serial_console_access_enabled = True

        return {
            "serialConsoleAccessEnabled": resource.serial_console_access_enabled,
        }

    def GetSerialConsoleAccessStatus(self, params: Dict[str, Any]):
        """Retrieves the access status of your account to the EC2 serial console of all instances. By
			default, access to the EC2 serial console is disabled for your account. For more
			information, seeManage account access to the EC2 serial consolein theAmazon EC2
				User Guide."""

        resource = self._get_or_create_console()

        return {
            "managedBy": resource.managed_by,
            "serialConsoleAccessEnabled": resource.serial_console_access_enabled,
        }

    def _generate_id(self, prefix: str = 'ser') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class serialconsole_RequestParser:
    @staticmethod
    def parse_disable_serial_console_access_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_enable_serial_console_access_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_get_serial_console_access_status_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DisableSerialConsoleAccess": serialconsole_RequestParser.parse_disable_serial_console_access_request,
            "EnableSerialConsoleAccess": serialconsole_RequestParser.parse_enable_serial_console_access_request,
            "GetSerialConsoleAccessStatus": serialconsole_RequestParser.parse_get_serial_console_access_status_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class serialconsole_ResponseSerializer:
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
                xml_parts.extend(serialconsole_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(serialconsole_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(serialconsole_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(serialconsole_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(serialconsole_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(serialconsole_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_disable_serial_console_access_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableSerialConsoleAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize serialConsoleAccessEnabled
        _serialConsoleAccessEnabled_key = None
        if "serialConsoleAccessEnabled" in data:
            _serialConsoleAccessEnabled_key = "serialConsoleAccessEnabled"
        elif "SerialConsoleAccessEnabled" in data:
            _serialConsoleAccessEnabled_key = "SerialConsoleAccessEnabled"
        if _serialConsoleAccessEnabled_key:
            param_data = data[_serialConsoleAccessEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<serialConsoleAccessEnabled>{esc(str(param_data))}</serialConsoleAccessEnabled>')
        xml_parts.append(f'</DisableSerialConsoleAccessResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_serial_console_access_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableSerialConsoleAccessResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize serialConsoleAccessEnabled
        _serialConsoleAccessEnabled_key = None
        if "serialConsoleAccessEnabled" in data:
            _serialConsoleAccessEnabled_key = "serialConsoleAccessEnabled"
        elif "SerialConsoleAccessEnabled" in data:
            _serialConsoleAccessEnabled_key = "SerialConsoleAccessEnabled"
        if _serialConsoleAccessEnabled_key:
            param_data = data[_serialConsoleAccessEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<serialConsoleAccessEnabled>{esc(str(param_data))}</serialConsoleAccessEnabled>')
        xml_parts.append(f'</EnableSerialConsoleAccessResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_serial_console_access_status_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetSerialConsoleAccessStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize managedBy
        _managedBy_key = None
        if "managedBy" in data:
            _managedBy_key = "managedBy"
        elif "ManagedBy" in data:
            _managedBy_key = "ManagedBy"
        if _managedBy_key:
            param_data = data[_managedBy_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<managedBy>{esc(str(param_data))}</managedBy>')
        # Serialize serialConsoleAccessEnabled
        _serialConsoleAccessEnabled_key = None
        if "serialConsoleAccessEnabled" in data:
            _serialConsoleAccessEnabled_key = "serialConsoleAccessEnabled"
        elif "SerialConsoleAccessEnabled" in data:
            _serialConsoleAccessEnabled_key = "SerialConsoleAccessEnabled"
        if _serialConsoleAccessEnabled_key:
            param_data = data[_serialConsoleAccessEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<serialConsoleAccessEnabled>{esc(str(param_data))}</serialConsoleAccessEnabled>')
        xml_parts.append(f'</GetSerialConsoleAccessStatusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DisableSerialConsoleAccess": serialconsole_ResponseSerializer.serialize_disable_serial_console_access_response,
            "EnableSerialConsoleAccess": serialconsole_ResponseSerializer.serialize_enable_serial_console_access_response,
            "GetSerialConsoleAccessStatus": serialconsole_ResponseSerializer.serialize_get_serial_console_access_status_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

