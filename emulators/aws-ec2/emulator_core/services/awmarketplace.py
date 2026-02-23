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
class AwMarketplace:


    def to_dict(self) -> Dict[str, Any]:
        return {
        }

class AwMarketplace_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.aws_marketplace  # alias to shared store


    def ConfirmProductInstance(self, params: Dict[str, Any]):
        """Determines whether a product code is associated with an instance. This action can only
            be used by the owner of the product code. It is useful when a product code owner must
            verify whether another user's instance is eligible for support."""

        instance_id = params.get("InstanceId")
        if not instance_id:
            return create_error_response(
                "MissingParameter",
                "The request must contain the parameter InstanceId",
            )

        product_code = params.get("ProductCode")
        if not product_code:
            return create_error_response(
                "MissingParameter",
                "The request must contain the parameter ProductCode",
            )

        instance = self.state.instances.get(instance_id)
        if not instance:
            return create_error_response(
                "InvalidInstanceID.NotFound",
                f"The instance ID '{instance_id}' does not exist.",
            )

        if isinstance(instance, dict):
            owner_id = (
                instance.get("owner_id")
                or instance.get("ownerId")
                or instance.get("OwnerId")
            )
            product_codes = (
                instance.get("product_codes")
                or instance.get("productCodes")
                or instance.get("ProductCodes")
            )
        else:
            owner_id = (
                getattr(instance, "owner_id", None)
                or getattr(instance, "ownerId", None)
                or getattr(instance, "OwnerId", None)
            )
            product_codes = (
                getattr(instance, "product_codes", None)
                or getattr(instance, "productCodes", None)
                or getattr(instance, "ProductCodes", None)
            )

        is_associated = False
        if product_codes:
            if isinstance(product_codes, list):
                for entry in product_codes:
                    if isinstance(entry, dict):
                        if (
                            entry.get("productCode") == product_code
                            or entry.get("ProductCode") == product_code
                        ):
                            is_associated = True
                            break
                    elif entry == product_code:
                        is_associated = True
                        break
            elif isinstance(product_codes, dict):
                if (
                    product_codes.get("productCode") == product_code
                    or product_codes.get("ProductCode") == product_code
                ):
                    is_associated = True

        return {
            "ownerId": owner_id or "unknown",
            "return": is_associated,
        }

    def _generate_id(self, prefix: str = 'awm') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class awmarketplace_RequestParser:
    @staticmethod
    def parse_confirm_product_instance_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "ProductCode": get_scalar(md, "ProductCode"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "ConfirmProductInstance": awmarketplace_RequestParser.parse_confirm_product_instance_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class awmarketplace_ResponseSerializer:
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
                xml_parts.extend(awmarketplace_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(awmarketplace_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(awmarketplace_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(awmarketplace_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(awmarketplace_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(awmarketplace_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_confirm_product_instance_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ConfirmProductInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ownerId
        _ownerId_key = None
        if "ownerId" in data:
            _ownerId_key = "ownerId"
        elif "OwnerId" in data:
            _ownerId_key = "OwnerId"
        if _ownerId_key:
            param_data = data[_ownerId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ownerId>{esc(str(param_data))}</ownerId>')
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
        xml_parts.append(f'</ConfirmProductInstanceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "ConfirmProductInstance": awmarketplace_ResponseSerializer.serialize_confirm_product_instance_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

