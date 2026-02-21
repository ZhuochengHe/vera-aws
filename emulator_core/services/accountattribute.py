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
class AccountAttribute:
    attribute_name: str = ""
    attribute_value_set: List[Any] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "attributeName": self.attribute_name,
            "attributeValueSet": self.attribute_value_set,
        }

class AccountAttribute_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.account_attributes  # alias to shared store


    def DescribeAccountAttributes(self, params: Dict[str, Any]):
        """Describes attributes of your AWS account. The following are the supported account attributes: default-vpc: The ID of the default VPC for your account, ornone. max-instances: This attribute is no longer supported. The returned
                    value does not reflect your actual vCPU limit for runn"""

        attribute_names = params.get("AttributeName.N", []) or []
        account_attributes: List[AccountAttribute] = []

        if attribute_names:
            for attribute_name in attribute_names:
                resource = None
                if attribute_name in self.resources:
                    resource = self.resources.get(attribute_name)
                else:
                    for candidate in self.resources.values():
                        if candidate.attribute_name == attribute_name:
                            resource = candidate
                            break
                if not resource:
                    return create_error_response(
                        "InvalidAccountAttribute.NotFound",
                        f"Attribute '{attribute_name}' does not exist",
                    )
                account_attributes.append(resource)
        else:
            account_attributes = list(self.resources.values())

        return {
            'accountAttributeSet': [attribute.to_dict() for attribute in account_attributes],
            }

    def _generate_id(self, prefix: str = 'acc') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class accountattribute_RequestParser:
    @staticmethod
    def parse_describe_account_attributes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AttributeName.N": get_indexed_list(md, "AttributeName"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeAccountAttributes": accountattribute_RequestParser.parse_describe_account_attributes_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class accountattribute_ResponseSerializer:
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
                xml_parts.extend(accountattribute_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(accountattribute_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(accountattribute_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(accountattribute_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(accountattribute_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(accountattribute_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_account_attributes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeAccountAttributesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize accountAttributeSet
        _accountAttributeSet_key = None
        if "accountAttributeSet" in data:
            _accountAttributeSet_key = "accountAttributeSet"
        elif "AccountAttributeSet" in data:
            _accountAttributeSet_key = "AccountAttributeSet"
        elif "AccountAttributes" in data:
            _accountAttributeSet_key = "AccountAttributes"
        if _accountAttributeSet_key:
            param_data = data[_accountAttributeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<accountAttributeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(accountattribute_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</accountAttributeSet>')
            else:
                xml_parts.append(f'{indent_str}<accountAttributeSet/>')
        xml_parts.append(f'</DescribeAccountAttributesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeAccountAttributes": accountattribute_ResponseSerializer.serialize_describe_account_attributes_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

