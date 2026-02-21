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
class VerifiedAccessTrustProvider:
    creation_time: str = ""
    description: str = ""
    device_options: Dict[str, Any] = field(default_factory=dict)
    device_trust_provider_type: str = ""
    last_updated_time: str = ""
    native_application_oidc_options: Dict[str, Any] = field(default_factory=dict)
    oidc_options: Dict[str, Any] = field(default_factory=dict)
    policy_reference_name: str = ""
    sse_specification: Dict[str, Any] = field(default_factory=dict)
    tag_set: List[Any] = field(default_factory=list)
    trust_provider_type: str = ""
    user_trust_provider_type: str = ""
    verified_access_trust_provider_id: str = ""

    attached_verified_access_instance_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTime": self.creation_time,
            "description": self.description,
            "deviceOptions": self.device_options,
            "deviceTrustProviderType": self.device_trust_provider_type,
            "lastUpdatedTime": self.last_updated_time,
            "nativeApplicationOidcOptions": self.native_application_oidc_options,
            "oidcOptions": self.oidc_options,
            "policyReferenceName": self.policy_reference_name,
            "sseSpecification": self.sse_specification,
            "tagSet": self.tag_set,
            "trustProviderType": self.trust_provider_type,
            "userTrustProviderType": self.user_trust_provider_type,
            "verifiedAccessTrustProviderId": self.verified_access_trust_provider_id,
        }

class VerifiedAccessTrustProvider_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.verified_access_trust_providers  # alias to shared store

    def _require_param(self, params: Dict[str, Any], key: str):
        value = params.get(key)
        if value is None or value == "":
            return create_error_response("MissingParameter", f"The request must contain the parameter {key}")
        return None

    def _get_trust_provider_or_error(self, trust_provider_id: str):
        resource = self.resources.get(trust_provider_id)
        if not resource:
            return create_error_response(
                "InvalidVerifiedAccessTrustProviderId.NotFound",
                f"The ID '{trust_provider_id}' does not exist",
            )
        return resource

    def _get_instance_or_error(self, instance_id: str):
        resource = self.state.verified_access_instances.get(instance_id)
        if not resource:
            return create_error_response(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The ID '{instance_id}' does not exist",
            )
        return resource

    def AttachVerifiedAccessTrustProvider(self, params: Dict[str, Any]):
        """Attaches the specified AWS Verified Access trust provider to the specified AWS Verified Access instance."""

        for name in ["VerifiedAccessInstanceId", "VerifiedAccessTrustProviderId"]:
            error = self._require_param(params, name)
            if error:
                return error

        instance_id = params.get("VerifiedAccessInstanceId")
        trust_provider_id = params.get("VerifiedAccessTrustProviderId")

        instance = self._get_instance_or_error(instance_id)
        if is_error_response(instance):
            return instance

        trust_provider = self._get_trust_provider_or_error(trust_provider_id)
        if is_error_response(trust_provider):
            return trust_provider

        trust_provider_entry = {
            "description": trust_provider.description,
            "deviceTrustProviderType": trust_provider.device_trust_provider_type,
            "trustProviderType": trust_provider.trust_provider_type,
            "userTrustProviderType": trust_provider.user_trust_provider_type,
            "verifiedAccessTrustProviderId": trust_provider.verified_access_trust_provider_id,
        }

        if instance_id not in trust_provider.attached_verified_access_instance_ids:
            trust_provider.attached_verified_access_instance_ids.append(instance_id)
        if trust_provider_entry not in instance.verified_access_trust_provider_set:
            instance.verified_access_trust_provider_set.append(trust_provider_entry)

        now = datetime.now(timezone.utc).isoformat()
        instance.last_updated_time = now
        trust_provider.last_updated_time = now

        return {
            'verifiedAccessInstance': instance.to_dict(),
            'verifiedAccessTrustProvider': trust_provider.to_dict(),
            }

    def CreateVerifiedAccessTrustProvider(self, params: Dict[str, Any]):
        """A trust provider is a third-party entity that creates, maintains, and manages identity
         information for users and devices. When an application request is made, the identity
         information sent by the trust provider is evaluated by Verified Access before allowing or
         denying the"""

        for name in ["PolicyReferenceName", "TrustProviderType"]:
            error = self._require_param(params, name)
            if error:
                return error

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "verified-access-trust-provider":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        now = datetime.now(timezone.utc).isoformat()
        trust_provider_id = self._generate_id("verified")
        resource = VerifiedAccessTrustProvider(
            creation_time=now,
            description=params.get("Description") or "",
            device_options=params.get("DeviceOptions") or {},
            device_trust_provider_type=params.get("DeviceTrustProviderType") or "",
            last_updated_time=now,
            native_application_oidc_options=params.get("NativeApplicationOidcOptions") or {},
            oidc_options=params.get("OidcOptions") or {},
            policy_reference_name=params.get("PolicyReferenceName") or "",
            sse_specification=params.get("SseSpecification") or {},
            tag_set=tag_set,
            trust_provider_type=params.get("TrustProviderType") or "",
            user_trust_provider_type=params.get("UserTrustProviderType") or "",
            verified_access_trust_provider_id=trust_provider_id,
        )
        self.resources[trust_provider_id] = resource

        return {
            'verifiedAccessTrustProvider': resource.to_dict(),
            }

    def DeleteVerifiedAccessTrustProvider(self, params: Dict[str, Any]):
        """Delete an AWS Verified Access trust provider."""

        error = self._require_param(params, "VerifiedAccessTrustProviderId")
        if error:
            return error

        trust_provider_id = params.get("VerifiedAccessTrustProviderId")
        resource = self._get_trust_provider_or_error(trust_provider_id)
        if is_error_response(resource):
            return resource

        if resource.attached_verified_access_instance_ids:
            return create_error_response(
                "DependencyViolation",
                "VerifiedAccessTrustProvider has dependent VerifiedAccessInstance(s) and cannot be deleted.",
            )

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()
        del self.resources[trust_provider_id]

        return {
            'verifiedAccessTrustProvider': resource.to_dict(),
            }

    def DescribeVerifiedAccessTrustProviders(self, params: Dict[str, Any]):
        """Describes the specified AWS Verified Access trust providers."""

        trust_provider_ids = params.get("VerifiedAccessTrustProviderId.N", []) or []
        if trust_provider_ids:
            resources: List[VerifiedAccessTrustProvider] = []
            for trust_provider_id in trust_provider_ids:
                resource = self.resources.get(trust_provider_id)
                if not resource:
                    return create_error_response(
                        "InvalidVerifiedAccessTrustProviderId.NotFound",
                        f"The ID '{trust_provider_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'verifiedAccessTrustProviderSet': [resource.to_dict() for resource in resources],
            }

    def DetachVerifiedAccessTrustProvider(self, params: Dict[str, Any]):
        """Detaches the specified AWS Verified Access trust provider from the specified AWS Verified Access instance."""

        for name in ["VerifiedAccessInstanceId", "VerifiedAccessTrustProviderId"]:
            error = self._require_param(params, name)
            if error:
                return error

        instance_id = params.get("VerifiedAccessInstanceId")
        trust_provider_id = params.get("VerifiedAccessTrustProviderId")

        instance = self._get_instance_or_error(instance_id)
        if is_error_response(instance):
            return instance

        trust_provider = self._get_trust_provider_or_error(trust_provider_id)
        if is_error_response(trust_provider):
            return trust_provider

        if instance_id in trust_provider.attached_verified_access_instance_ids:
            trust_provider.attached_verified_access_instance_ids.remove(instance_id)

        instance.verified_access_trust_provider_set = [
            entry for entry in instance.verified_access_trust_provider_set
            if entry.get("verifiedAccessTrustProviderId") != trust_provider_id
        ]

        now = datetime.now(timezone.utc).isoformat()
        instance.last_updated_time = now
        trust_provider.last_updated_time = now

        return {
            'verifiedAccessInstance': instance.to_dict(),
            'verifiedAccessTrustProvider': trust_provider.to_dict(),
            }

    def ModifyVerifiedAccessTrustProvider(self, params: Dict[str, Any]):
        """Modifies the configuration of the specified AWS Verified Access trust provider."""

        error = self._require_param(params, "VerifiedAccessTrustProviderId")
        if error:
            return error

        trust_provider_id = params.get("VerifiedAccessTrustProviderId")
        resource = self._get_trust_provider_or_error(trust_provider_id)
        if is_error_response(resource):
            return resource

        if params.get("Description") is not None:
            resource.description = params.get("Description") or ""
        if params.get("DeviceOptions") is not None:
            resource.device_options = params.get("DeviceOptions") or {}
        if params.get("NativeApplicationOidcOptions") is not None:
            resource.native_application_oidc_options = params.get("NativeApplicationOidcOptions") or {}
        if params.get("OidcOptions") is not None:
            resource.oidc_options = params.get("OidcOptions") or {}
        if params.get("SseSpecification") is not None:
            resource.sse_specification = params.get("SseSpecification") or {}

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()

        return {
            'verifiedAccessTrustProvider': resource.to_dict(),
            }

    def _generate_id(self, prefix: str = 'verified') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class verifiedaccesstrustprovider_RequestParser:
    @staticmethod
    def parse_attach_verified_access_trust_provider_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
            "VerifiedAccessTrustProviderId": get_scalar(md, "VerifiedAccessTrustProviderId"),
        }

    @staticmethod
    def parse_create_verified_access_trust_provider_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DeviceOptions": get_scalar(md, "DeviceOptions"),
            "DeviceTrustProviderType": get_scalar(md, "DeviceTrustProviderType"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NativeApplicationOidcOptions": get_indexed_list(md, "NativeApplicationOidcOptions"),
            "OidcOptions": get_indexed_list(md, "OidcOptions"),
            "PolicyReferenceName": get_scalar(md, "PolicyReferenceName"),
            "SseSpecification": get_scalar(md, "SseSpecification"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TrustProviderType": get_scalar(md, "TrustProviderType"),
            "UserTrustProviderType": get_scalar(md, "UserTrustProviderType"),
        }

    @staticmethod
    def parse_delete_verified_access_trust_provider_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessTrustProviderId": get_scalar(md, "VerifiedAccessTrustProviderId"),
        }

    @staticmethod
    def parse_describe_verified_access_trust_providers_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VerifiedAccessTrustProviderId.N": get_indexed_list(md, "VerifiedAccessTrustProviderId"),
        }

    @staticmethod
    def parse_detach_verified_access_trust_provider_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
            "VerifiedAccessTrustProviderId": get_scalar(md, "VerifiedAccessTrustProviderId"),
        }

    @staticmethod
    def parse_modify_verified_access_trust_provider_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DeviceOptions": get_scalar(md, "DeviceOptions"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NativeApplicationOidcOptions": get_indexed_list(md, "NativeApplicationOidcOptions"),
            "OidcOptions": get_indexed_list(md, "OidcOptions"),
            "SseSpecification": get_scalar(md, "SseSpecification"),
            "VerifiedAccessTrustProviderId": get_scalar(md, "VerifiedAccessTrustProviderId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AttachVerifiedAccessTrustProvider": verifiedaccesstrustprovider_RequestParser.parse_attach_verified_access_trust_provider_request,
            "CreateVerifiedAccessTrustProvider": verifiedaccesstrustprovider_RequestParser.parse_create_verified_access_trust_provider_request,
            "DeleteVerifiedAccessTrustProvider": verifiedaccesstrustprovider_RequestParser.parse_delete_verified_access_trust_provider_request,
            "DescribeVerifiedAccessTrustProviders": verifiedaccesstrustprovider_RequestParser.parse_describe_verified_access_trust_providers_request,
            "DetachVerifiedAccessTrustProvider": verifiedaccesstrustprovider_RequestParser.parse_detach_verified_access_trust_provider_request,
            "ModifyVerifiedAccessTrustProvider": verifiedaccesstrustprovider_RequestParser.parse_modify_verified_access_trust_provider_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class verifiedaccesstrustprovider_ResponseSerializer:
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
                xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_attach_verified_access_trust_provider_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AttachVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessInstance
        _verifiedAccessInstance_key = None
        if "verifiedAccessInstance" in data:
            _verifiedAccessInstance_key = "verifiedAccessInstance"
        elif "VerifiedAccessInstance" in data:
            _verifiedAccessInstance_key = "VerifiedAccessInstance"
        if _verifiedAccessInstance_key:
            param_data = data[_verifiedAccessInstance_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessInstance>')
            xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessInstance>')
        # Serialize verifiedAccessTrustProvider
        _verifiedAccessTrustProvider_key = None
        if "verifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "verifiedAccessTrustProvider"
        elif "VerifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "VerifiedAccessTrustProvider"
        if _verifiedAccessTrustProvider_key:
            param_data = data[_verifiedAccessTrustProvider_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessTrustProvider>')
            xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessTrustProvider>')
        xml_parts.append(f'</AttachVerifiedAccessTrustProviderResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_verified_access_trust_provider_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessTrustProvider
        _verifiedAccessTrustProvider_key = None
        if "verifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "verifiedAccessTrustProvider"
        elif "VerifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "VerifiedAccessTrustProvider"
        if _verifiedAccessTrustProvider_key:
            param_data = data[_verifiedAccessTrustProvider_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessTrustProvider>')
            xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessTrustProvider>')
        xml_parts.append(f'</CreateVerifiedAccessTrustProviderResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_verified_access_trust_provider_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessTrustProvider
        _verifiedAccessTrustProvider_key = None
        if "verifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "verifiedAccessTrustProvider"
        elif "VerifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "VerifiedAccessTrustProvider"
        if _verifiedAccessTrustProvider_key:
            param_data = data[_verifiedAccessTrustProvider_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessTrustProvider>')
            xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessTrustProvider>')
        xml_parts.append(f'</DeleteVerifiedAccessTrustProviderResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_verified_access_trust_providers_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVerifiedAccessTrustProvidersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize verifiedAccessTrustProviderSet
        _verifiedAccessTrustProviderSet_key = None
        if "verifiedAccessTrustProviderSet" in data:
            _verifiedAccessTrustProviderSet_key = "verifiedAccessTrustProviderSet"
        elif "VerifiedAccessTrustProviderSet" in data:
            _verifiedAccessTrustProviderSet_key = "VerifiedAccessTrustProviderSet"
        elif "VerifiedAccessTrustProviders" in data:
            _verifiedAccessTrustProviderSet_key = "VerifiedAccessTrustProviders"
        if _verifiedAccessTrustProviderSet_key:
            param_data = data[_verifiedAccessTrustProviderSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<verifiedAccessTrustProviderSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</verifiedAccessTrustProviderSet>')
            else:
                xml_parts.append(f'{indent_str}<verifiedAccessTrustProviderSet/>')
        xml_parts.append(f'</DescribeVerifiedAccessTrustProvidersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_detach_verified_access_trust_provider_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DetachVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessInstance
        _verifiedAccessInstance_key = None
        if "verifiedAccessInstance" in data:
            _verifiedAccessInstance_key = "verifiedAccessInstance"
        elif "VerifiedAccessInstance" in data:
            _verifiedAccessInstance_key = "VerifiedAccessInstance"
        if _verifiedAccessInstance_key:
            param_data = data[_verifiedAccessInstance_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessInstance>')
            xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessInstance>')
        # Serialize verifiedAccessTrustProvider
        _verifiedAccessTrustProvider_key = None
        if "verifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "verifiedAccessTrustProvider"
        elif "VerifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "VerifiedAccessTrustProvider"
        if _verifiedAccessTrustProvider_key:
            param_data = data[_verifiedAccessTrustProvider_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessTrustProvider>')
            xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessTrustProvider>')
        xml_parts.append(f'</DetachVerifiedAccessTrustProviderResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_verified_access_trust_provider_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVerifiedAccessTrustProviderResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessTrustProvider
        _verifiedAccessTrustProvider_key = None
        if "verifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "verifiedAccessTrustProvider"
        elif "VerifiedAccessTrustProvider" in data:
            _verifiedAccessTrustProvider_key = "VerifiedAccessTrustProvider"
        if _verifiedAccessTrustProvider_key:
            param_data = data[_verifiedAccessTrustProvider_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessTrustProvider>')
            xml_parts.extend(verifiedaccesstrustprovider_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessTrustProvider>')
        xml_parts.append(f'</ModifyVerifiedAccessTrustProviderResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AttachVerifiedAccessTrustProvider": verifiedaccesstrustprovider_ResponseSerializer.serialize_attach_verified_access_trust_provider_response,
            "CreateVerifiedAccessTrustProvider": verifiedaccesstrustprovider_ResponseSerializer.serialize_create_verified_access_trust_provider_response,
            "DeleteVerifiedAccessTrustProvider": verifiedaccesstrustprovider_ResponseSerializer.serialize_delete_verified_access_trust_provider_response,
            "DescribeVerifiedAccessTrustProviders": verifiedaccesstrustprovider_ResponseSerializer.serialize_describe_verified_access_trust_providers_response,
            "DetachVerifiedAccessTrustProvider": verifiedaccesstrustprovider_ResponseSerializer.serialize_detach_verified_access_trust_provider_response,
            "ModifyVerifiedAccessTrustProvider": verifiedaccesstrustprovider_ResponseSerializer.serialize_modify_verified_access_trust_provider_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

