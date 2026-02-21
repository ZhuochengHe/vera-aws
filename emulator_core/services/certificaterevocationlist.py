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
class CertificateRevocationList:
    certificate_revocation_list: str
    client_vpn_endpoint_id: str
    status: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CertificateRevocationList": self.certificate_revocation_list,
            "ClientVpnEndpointId": self.client_vpn_endpoint_id,
            "Status": self.status,
            "CreatedAt": self.created_at.isoformat(),
            "UpdatedAt": self.updated_at.isoformat(),
        }

class CertificateRevocationList_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.certificate_revocation_lists  # alias to shared store

    def _get_client_vpn_endpoint(self, client_vpn_endpoint_id: str):
        endpoint = self.state.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )
        return endpoint

    def _find_crl(self, client_vpn_endpoint_id: str) -> Optional[CertificateRevocationList]:
        return next(
            (
                resource
                for resource in self.resources.values()
                if resource.client_vpn_endpoint_id == client_vpn_endpoint_id
            ),
            None,
        )

    def ExportClientVpnClientCertificateRevocationList(self, params: Dict[str, Any]):
        """Downloads the client certificate revocation list for the specified Client VPN endpoint."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        resource = self._find_crl(client_vpn_endpoint_id)
        if not resource:
            return create_error_response(
                "ResourceNotFound",
                f"Certificate revocation list for Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )

        status = resource.status or [
            {"code": "active", "message": "Certificate revocation list active"}
        ]

        return {
            'certificateRevocationList': resource.certificate_revocation_list,
            'status': status,  # list of dicts, each with keys: code, message
            }

    def ImportClientVpnClientCertificateRevocationList(self, params: Dict[str, Any]):
        """Uploads a client certificate revocation list to the specified Client VPN endpoint. Uploading a client certificate revocation list overwrites the existing client certificate revocation list. Uploading a client certificate revocation list resets existing client connections."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        certificate_revocation_list = params.get("CertificateRevocationList")

        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")
        if not certificate_revocation_list:
            return create_error_response("MissingParameter", "CertificateRevocationList is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        status = [{"code": "active", "message": "Certificate revocation list imported"}]
        resource = self._find_crl(client_vpn_endpoint_id)
        now = datetime.now(timezone.utc)
        if resource:
            resource.certificate_revocation_list = certificate_revocation_list
            resource.status = status
            resource.updated_at = now
        else:
            resource_id = self._generate_id("cer")
            self.resources[resource_id] = CertificateRevocationList(
                certificate_revocation_list=certificate_revocation_list,
                client_vpn_endpoint_id=client_vpn_endpoint_id,
                status=status,
                created_at=now,
                updated_at=now,
            )

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'cer') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class certificaterevocationlist_RequestParser:
    @staticmethod
    def parse_export_client_vpn_client_certificate_revocation_list_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_import_client_vpn_client_certificate_revocation_list_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CertificateRevocationList": get_scalar(md, "CertificateRevocationList"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "ExportClientVpnClientCertificateRevocationList": certificaterevocationlist_RequestParser.parse_export_client_vpn_client_certificate_revocation_list_request,
            "ImportClientVpnClientCertificateRevocationList": certificaterevocationlist_RequestParser.parse_import_client_vpn_client_certificate_revocation_list_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class certificaterevocationlist_ResponseSerializer:
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
                xml_parts.extend(certificaterevocationlist_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(certificaterevocationlist_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(certificaterevocationlist_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(certificaterevocationlist_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(certificaterevocationlist_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(certificaterevocationlist_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_export_client_vpn_client_certificate_revocation_list_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ExportClientVpnClientCertificateRevocationListResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize certificateRevocationList
        _certificateRevocationList_key = None
        if "certificateRevocationList" in data:
            _certificateRevocationList_key = "certificateRevocationList"
        elif "CertificateRevocationList" in data:
            _certificateRevocationList_key = "CertificateRevocationList"
        if _certificateRevocationList_key:
            param_data = data[_certificateRevocationList_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<certificateRevocationList>{esc(str(param_data))}</certificateRevocationList>')
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
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(certificaterevocationlist_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</ExportClientVpnClientCertificateRevocationListResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_import_client_vpn_client_certificate_revocation_list_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ImportClientVpnClientCertificateRevocationListResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ImportClientVpnClientCertificateRevocationListResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "ExportClientVpnClientCertificateRevocationList": certificaterevocationlist_ResponseSerializer.serialize_export_client_vpn_client_certificate_revocation_list_response,
            "ImportClientVpnClientCertificateRevocationList": certificaterevocationlist_ResponseSerializer.serialize_import_client_vpn_client_certificate_revocation_list_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

