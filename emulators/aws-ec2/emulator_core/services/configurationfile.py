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
class ConfigurationFile:


    def to_dict(self) -> Dict[str, Any]:
        return {
        }

class ConfigurationFile_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.configuration_files  # alias to shared store


    def ExportClientVpnClientConfiguration(self, params: Dict[str, Any]):
        """Downloads the contents of the Client VPN endpoint configuration file for the specified Client VPN endpoint. The Client VPN endpoint configuration 
			file includes the Client VPN endpoint and certificate information clients need to establish a connection 
			with the Client VPN endpoint."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id:
            return create_error_response(
                "MissingParameter",
                "The request must contain the parameter ClientVpnEndpointId."
            )

        client_vpn_endpoints = getattr(self.state, "client_vpn_endpoints", None)
        if not client_vpn_endpoints or client_vpn_endpoint_id not in client_vpn_endpoints:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"The Client VPN endpoint '{client_vpn_endpoint_id}' does not exist."
            )

        endpoint = client_vpn_endpoints.get(client_vpn_endpoint_id)
        client_configuration = getattr(endpoint, "client_configuration", None)
        if not client_configuration:
            dns_name = getattr(endpoint, "dns_name", None) or f"{client_vpn_endpoint_id}.clientvpn.local"
            protocol = (getattr(endpoint, "transport_protocol", None) or "udp").lower()
            vpn_port = getattr(endpoint, "vpn_port", None) or 443
            client_configuration = (
                "client\n"
                "dev tun\n"
                f"proto {protocol}\n"
                f"remote {dns_name} {vpn_port}\n"
                "resolv-retry infinite\n"
                "nobind\n"
                "persist-key\n"
                "persist-tun\n"
                "remote-cert-tls server\n"
                "cipher AES-256-GCM\n"
                "verb 3\n"
            )

        return {
            'clientConfiguration': client_configuration,
            }

    def _generate_id(self, prefix: str = 'con') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class configurationfile_RequestParser:
    @staticmethod
    def parse_export_client_vpn_client_configuration_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "ExportClientVpnClientConfiguration": configurationfile_RequestParser.parse_export_client_vpn_client_configuration_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class configurationfile_ResponseSerializer:
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
                xml_parts.extend(configurationfile_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(configurationfile_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(configurationfile_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(configurationfile_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(configurationfile_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(configurationfile_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_export_client_vpn_client_configuration_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ExportClientVpnClientConfigurationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientConfiguration
        _clientConfiguration_key = None
        if "clientConfiguration" in data:
            _clientConfiguration_key = "clientConfiguration"
        elif "ClientConfiguration" in data:
            _clientConfiguration_key = "ClientConfiguration"
        if _clientConfiguration_key:
            param_data = data[_clientConfiguration_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientConfiguration>{esc(str(param_data))}</clientConfiguration>')
        xml_parts.append(f'</ExportClientVpnClientConfigurationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "ExportClientVpnClientConfiguration": configurationfile_ResponseSerializer.serialize_export_client_vpn_client_configuration_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

