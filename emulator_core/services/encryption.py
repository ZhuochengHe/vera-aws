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
class Encryption:

    ebs_encryption_by_default: bool = False
    kms_key_id: Optional[str] = None
    sse_type: Optional[str] = "aws:kms"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ebsEncryptionByDefault": self.ebs_encryption_by_default,
            "kmsKeyId": self.kms_key_id,
            "sseType": self.sse_type,
        }

class Encryption_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.encryption  # alias to shared store

    def _get_settings(self) -> Encryption:
        settings = self.resources.get("default")
        if not settings:
            settings = Encryption()
            self.resources["default"] = settings
        return settings

    def _managed_kms_key_id(self) -> str:
        return "alias/aws/ebs"

    def DisableEbsEncryptionByDefault(self, params: Dict[str, Any]):
        """Disables EBS encryption by default for your account in the current Region. After you disable encryption by default, you can still create encrypted volumes by 
      enabling encryption when you create each volume. Disabling encryption by default does not change the encryption status of your
      ex"""

        settings = self._get_settings()
        settings.ebs_encryption_by_default = False

        return {
            'ebsEncryptionByDefault': settings.ebs_encryption_by_default,
            }

    def EnableEbsEncryptionByDefault(self, params: Dict[str, Any]):
        """Enables EBS encryption by default for your account in the current Region. After you enable encryption by default, the EBS volumes that you create are
    	always encrypted, either using the default KMS key or the KMS key that you specified
      when you created each volume. For more information, se"""

        settings = self._get_settings()
        settings.ebs_encryption_by_default = True
        if not settings.kms_key_id:
            settings.kms_key_id = self._managed_kms_key_id()

        return {
            'ebsEncryptionByDefault': settings.ebs_encryption_by_default,
            }

    def GetEbsDefaultKmsKeyId(self, params: Dict[str, Any]):
        """Describes the default AWS KMS key for EBS encryption by default for your account in this Region. For more information, seeAmazon EBS encryptionin theAmazon EBS User Guide."""

        settings = self._get_settings()
        kms_key_id = settings.kms_key_id or self._managed_kms_key_id()

        return {
            'kmsKeyId': kms_key_id,
            }

    def GetEbsEncryptionByDefault(self, params: Dict[str, Any]):
        """Describes whether EBS encryption by default is enabled for your account in the current
      Region. For more information, seeAmazon EBS encryptionin theAmazon EBS User Guide."""

        settings = self._get_settings()

        return {
            'ebsEncryptionByDefault': settings.ebs_encryption_by_default,
            'sseType': settings.sse_type,
            }

    def ModifyEbsDefaultKmsKeyId(self, params: Dict[str, Any]):
        """Changes the default AWS KMS key for EBS encryption by default for your account in this Region. AWS creates a unique AWS managed KMS key in each Region for use with encryption by default. If
      you change the default KMS key to a symmetric customer managed KMS key, it is used instead of the AWS
  """

        if not params.get("KmsKeyId"):
            return create_error_response("MissingParameter", "Missing required parameter: KmsKeyId")

        settings = self._get_settings()
        settings.kms_key_id = params.get("KmsKeyId")
        settings.sse_type = "aws:kms"

        return {
            'kmsKeyId': settings.kms_key_id,
            }

    def ResetEbsDefaultKmsKeyId(self, params: Dict[str, Any]):
        """Resets the default AWS KMS key for EBS encryption for your account in this Region 
      to the AWS managed KMS key for EBS. After resetting the default KMS key to the AWS managed KMS key, you can continue to encrypt by a 
      customer managed KMS key by specifying it when you create the volume. F"""

        settings = self._get_settings()
        settings.kms_key_id = self._managed_kms_key_id()
        settings.sse_type = "aws:kms"

        return {
            'kmsKeyId': settings.kms_key_id,
            }

    def _generate_id(self, prefix: str = 'enc') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class encryption_RequestParser:
    @staticmethod
    def parse_disable_ebs_encryption_by_default_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_enable_ebs_encryption_by_default_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_get_ebs_default_kms_key_id_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_get_ebs_encryption_by_default_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_modify_ebs_default_kms_key_id_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "KmsKeyId": get_scalar(md, "KmsKeyId"),
        }

    @staticmethod
    def parse_reset_ebs_default_kms_key_id_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DisableEbsEncryptionByDefault": encryption_RequestParser.parse_disable_ebs_encryption_by_default_request,
            "EnableEbsEncryptionByDefault": encryption_RequestParser.parse_enable_ebs_encryption_by_default_request,
            "GetEbsDefaultKmsKeyId": encryption_RequestParser.parse_get_ebs_default_kms_key_id_request,
            "GetEbsEncryptionByDefault": encryption_RequestParser.parse_get_ebs_encryption_by_default_request,
            "ModifyEbsDefaultKmsKeyId": encryption_RequestParser.parse_modify_ebs_default_kms_key_id_request,
            "ResetEbsDefaultKmsKeyId": encryption_RequestParser.parse_reset_ebs_default_kms_key_id_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class encryption_ResponseSerializer:
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
                xml_parts.extend(encryption_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(encryption_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(encryption_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(encryption_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(encryption_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(encryption_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_disable_ebs_encryption_by_default_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableEbsEncryptionByDefaultResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ebsEncryptionByDefault
        _ebsEncryptionByDefault_key = None
        if "ebsEncryptionByDefault" in data:
            _ebsEncryptionByDefault_key = "ebsEncryptionByDefault"
        elif "EbsEncryptionByDefault" in data:
            _ebsEncryptionByDefault_key = "EbsEncryptionByDefault"
        if _ebsEncryptionByDefault_key:
            param_data = data[_ebsEncryptionByDefault_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ebsEncryptionByDefault>{esc(str(param_data))}</ebsEncryptionByDefault>')
        xml_parts.append(f'</DisableEbsEncryptionByDefaultResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_ebs_encryption_by_default_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableEbsEncryptionByDefaultResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ebsEncryptionByDefault
        _ebsEncryptionByDefault_key = None
        if "ebsEncryptionByDefault" in data:
            _ebsEncryptionByDefault_key = "ebsEncryptionByDefault"
        elif "EbsEncryptionByDefault" in data:
            _ebsEncryptionByDefault_key = "EbsEncryptionByDefault"
        if _ebsEncryptionByDefault_key:
            param_data = data[_ebsEncryptionByDefault_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ebsEncryptionByDefault>{esc(str(param_data))}</ebsEncryptionByDefault>')
        xml_parts.append(f'</EnableEbsEncryptionByDefaultResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ebs_default_kms_key_id_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetEbsDefaultKmsKeyIdResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize kmsKeyId
        _kmsKeyId_key = None
        if "kmsKeyId" in data:
            _kmsKeyId_key = "kmsKeyId"
        elif "KmsKeyId" in data:
            _kmsKeyId_key = "KmsKeyId"
        if _kmsKeyId_key:
            param_data = data[_kmsKeyId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<kmsKeyId>{esc(str(param_data))}</kmsKeyId>')
        xml_parts.append(f'</GetEbsDefaultKmsKeyIdResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ebs_encryption_by_default_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetEbsEncryptionByDefaultResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ebsEncryptionByDefault
        _ebsEncryptionByDefault_key = None
        if "ebsEncryptionByDefault" in data:
            _ebsEncryptionByDefault_key = "ebsEncryptionByDefault"
        elif "EbsEncryptionByDefault" in data:
            _ebsEncryptionByDefault_key = "EbsEncryptionByDefault"
        if _ebsEncryptionByDefault_key:
            param_data = data[_ebsEncryptionByDefault_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ebsEncryptionByDefault>{esc(str(param_data))}</ebsEncryptionByDefault>')
        # Serialize sseType
        _sseType_key = None
        if "sseType" in data:
            _sseType_key = "sseType"
        elif "SseType" in data:
            _sseType_key = "SseType"
        if _sseType_key:
            param_data = data[_sseType_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sseType>{esc(str(param_data))}</sseType>')
        xml_parts.append(f'</GetEbsEncryptionByDefaultResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_ebs_default_kms_key_id_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyEbsDefaultKmsKeyIdResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize kmsKeyId
        _kmsKeyId_key = None
        if "kmsKeyId" in data:
            _kmsKeyId_key = "kmsKeyId"
        elif "KmsKeyId" in data:
            _kmsKeyId_key = "KmsKeyId"
        if _kmsKeyId_key:
            param_data = data[_kmsKeyId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<kmsKeyId>{esc(str(param_data))}</kmsKeyId>')
        xml_parts.append(f'</ModifyEbsDefaultKmsKeyIdResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reset_ebs_default_kms_key_id_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ResetEbsDefaultKmsKeyIdResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize kmsKeyId
        _kmsKeyId_key = None
        if "kmsKeyId" in data:
            _kmsKeyId_key = "kmsKeyId"
        elif "KmsKeyId" in data:
            _kmsKeyId_key = "KmsKeyId"
        if _kmsKeyId_key:
            param_data = data[_kmsKeyId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<kmsKeyId>{esc(str(param_data))}</kmsKeyId>')
        xml_parts.append(f'</ResetEbsDefaultKmsKeyIdResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DisableEbsEncryptionByDefault": encryption_ResponseSerializer.serialize_disable_ebs_encryption_by_default_response,
            "EnableEbsEncryptionByDefault": encryption_ResponseSerializer.serialize_enable_ebs_encryption_by_default_response,
            "GetEbsDefaultKmsKeyId": encryption_ResponseSerializer.serialize_get_ebs_default_kms_key_id_response,
            "GetEbsEncryptionByDefault": encryption_ResponseSerializer.serialize_get_ebs_encryption_by_default_response,
            "ModifyEbsDefaultKmsKeyId": encryption_ResponseSerializer.serialize_modify_ebs_default_kms_key_id_response,
            "ResetEbsDefaultKmsKeyId": encryption_ResponseSerializer.serialize_reset_ebs_default_kms_key_id_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

