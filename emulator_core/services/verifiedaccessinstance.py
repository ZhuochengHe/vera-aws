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
class VerifiedAccessInstance:
    cidr_endpoints_custom_sub_domain: Dict[str, Any] = field(default_factory=dict)
    creation_time: str = ""
    description: str = ""
    fips_enabled: bool = False
    last_updated_time: str = ""
    tag_set: List[Any] = field(default_factory=list)
    verified_access_instance_id: str = ""
    verified_access_trust_provider_set: List[Any] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "cidrEndpointsCustomSubDomain": self.cidr_endpoints_custom_sub_domain,
            "creationTime": self.creation_time,
            "description": self.description,
            "fipsEnabled": self.fips_enabled,
            "lastUpdatedTime": self.last_updated_time,
            "tagSet": self.tag_set,
            "verifiedAccessInstanceId": self.verified_access_instance_id,
            "verifiedAccessTrustProviderSet": self.verified_access_trust_provider_set,
        }

class VerifiedAccessInstance_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.verified_access_instances  # alias to shared store

    def _get_instance_or_error(self, instance_id: str):
        resource = self.resources.get(instance_id)
        if not resource:
            return create_error_response(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The ID '{instance_id}' does not exist",
            )
        return resource

    def CreateVerifiedAccessInstance(self, params: Dict[str, Any]):
        """An AWS Verified Access instance is a regional entity that evaluates application requests and grants
         access only when your security requirements are met."""

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "verified-access-instance":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        now = datetime.now(timezone.utc).isoformat()
        cidr_sub_domain = params.get("CidrEndpointsCustomSubDomain")
        cidr_endpoints_custom_sub_domain: Dict[str, Any] = {}
        if cidr_sub_domain:
            cidr_endpoints_custom_sub_domain = {
                "subDomain": cidr_sub_domain,
                "nameserverSet": [],
            }

        fips_enabled_param = params.get("FIPSEnabled")
        fips_enabled = str2bool(fips_enabled_param) if fips_enabled_param is not None else False

        verified_access_instance_id = self._generate_id("verified")
        resource = VerifiedAccessInstance(
            cidr_endpoints_custom_sub_domain=cidr_endpoints_custom_sub_domain,
            creation_time=now,
            description=params.get("Description") or "",
            fips_enabled=fips_enabled,
            last_updated_time=now,
            tag_set=tag_set,
            verified_access_instance_id=verified_access_instance_id,
            verified_access_trust_provider_set=[],
        )
        self.resources[verified_access_instance_id] = resource

        return {
            'verifiedAccessInstance': resource.to_dict(),
            }

    def DeleteVerifiedAccessInstance(self, params: Dict[str, Any]):
        """Delete an AWS Verified Access instance."""

        if not params.get("VerifiedAccessInstanceId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessInstanceId",
            )

        verified_access_instance_id = params.get("VerifiedAccessInstanceId")
        resource = self._get_instance_or_error(verified_access_instance_id)
        if is_error_response(resource):
            return resource

        has_group_dependency = any(
            group.verified_access_instance_id == verified_access_instance_id
            for group in self.state.verified_access_groups.values()
        )
        if has_group_dependency:
            return create_error_response(
                "DependencyViolation",
                "VerifiedAccessInstance has dependent VerifiedAccessGroup(s) and cannot be deleted.",
            )

        has_endpoint_dependency = any(
            endpoint.verified_access_instance_id == verified_access_instance_id
            for endpoint in self.state.verified_access_endpoints.values()
        )
        if has_endpoint_dependency:
            return create_error_response(
                "DependencyViolation",
                "VerifiedAccessInstance has dependent VerifiedAccessEndpoint(s) and cannot be deleted.",
            )

        if verified_access_instance_id in self.state.verified_access_logs:
            del self.state.verified_access_logs[verified_access_instance_id]

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()
        del self.resources[verified_access_instance_id]

        return {
            'verifiedAccessInstance': resource.to_dict(),
            }

    def DescribeVerifiedAccessInstances(self, params: Dict[str, Any]):
        """Describes the specified AWS Verified Access instances."""

        instance_ids = params.get("VerifiedAccessInstanceId.N", []) or []
        if instance_ids:
            resources: List[VerifiedAccessInstance] = []
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

        max_results = int(params.get("MaxResults") or 100)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'verifiedAccessInstanceSet': [resource.to_dict() for resource in resources],
            }

    def ExportVerifiedAccessInstanceClientConfiguration(self, params: Dict[str, Any]):
        """Exports the client configuration for a Verified Access instance."""

        if not params.get("VerifiedAccessInstanceId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessInstanceId",
            )

        verified_access_instance_id = params.get("VerifiedAccessInstanceId")
        resource = self._get_instance_or_error(verified_access_instance_id)
        if is_error_response(resource):
            return resource

        trust_providers = [
            trust_provider
            for trust_provider in self.state.verified_access_trust_providers.values()
            if verified_access_instance_id in trust_provider.attached_verified_access_instance_ids
        ]

        device_trust_provider_set: List[str] = []
        user_trust_provider = {
            "authorizationEndpoint": None,
            "clientId": None,
            "clientSecret": None,
            "issuer": None,
            "pkceEnabled": None,
            "publicSigningKeyEndpoint": None,
            "scopes": None,
            "tokenEndpoint": None,
            "type": None,
            "userInfoEndpoint": None,
        }

        def normalize_oidc_options(options: Any) -> Dict[str, Any]:
            if isinstance(options, list) and options:
                first = options[0]
                return first if isinstance(first, dict) else {}
            if isinstance(options, dict):
                return options
            return {}

        for trust_provider in trust_providers:
            is_device = trust_provider.trust_provider_type == "device" or bool(trust_provider.device_trust_provider_type)
            is_user = trust_provider.trust_provider_type == "user" or bool(trust_provider.user_trust_provider_type)
            if is_device and trust_provider.verified_access_trust_provider_id not in device_trust_provider_set:
                device_trust_provider_set.append(trust_provider.verified_access_trust_provider_id)
            if is_user and user_trust_provider.get("type") is None:
                oidc_options = normalize_oidc_options(trust_provider.oidc_options)
                if not oidc_options:
                    oidc_options = normalize_oidc_options(trust_provider.native_application_oidc_options)
                user_trust_provider.update({
                    "authorizationEndpoint": oidc_options.get("authorizationEndpoint") or oidc_options.get("AuthorizationEndpoint"),
                    "clientId": oidc_options.get("clientId") or oidc_options.get("ClientId"),
                    "clientSecret": oidc_options.get("clientSecret") or oidc_options.get("ClientSecret"),
                    "issuer": oidc_options.get("issuer") or oidc_options.get("Issuer"),
                    "pkceEnabled": oidc_options.get("pkceEnabled")
                    if oidc_options.get("pkceEnabled") is not None
                    else oidc_options.get("PkceEnabled")
                    if oidc_options.get("PkceEnabled") is not None
                    else oidc_options.get("PKCEEnabled"),
                    "publicSigningKeyEndpoint": oidc_options.get("publicSigningKeyEndpoint")
                    or oidc_options.get("PublicSigningKeyEndpoint"),
                    "scopes": oidc_options.get("scopes") or oidc_options.get("Scopes")
                    or oidc_options.get("scope") or oidc_options.get("Scope"),
                    "tokenEndpoint": oidc_options.get("tokenEndpoint") or oidc_options.get("TokenEndpoint"),
                    "type": trust_provider.user_trust_provider_type or trust_provider.trust_provider_type or None,
                    "userInfoEndpoint": oidc_options.get("userInfoEndpoint") or oidc_options.get("UserInfoEndpoint"),
                })
                pkce_value = user_trust_provider.get("pkceEnabled")
                if isinstance(pkce_value, str):
                    user_trust_provider["pkceEnabled"] = str2bool(pkce_value)

        return {
            'deviceTrustProviderSet': device_trust_provider_set,
            'openVpnConfigurationSet': [],
            'region': "us-east-1",
            'userTrustProvider': user_trust_provider,
            'verifiedAccessInstanceId': verified_access_instance_id,
            'version': "1.0",
            }

    def ModifyVerifiedAccessInstance(self, params: Dict[str, Any]):
        """Modifies the configuration of the specified AWS Verified Access instance."""

        if not params.get("VerifiedAccessInstanceId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessInstanceId",
            )

        verified_access_instance_id = params.get("VerifiedAccessInstanceId")
        resource = self._get_instance_or_error(verified_access_instance_id)
        if is_error_response(resource):
            return resource

        if params.get("Description") is not None:
            resource.description = params.get("Description") or ""

        if params.get("CidrEndpointsCustomSubDomain") is not None:
            cidr_sub_domain = params.get("CidrEndpointsCustomSubDomain")
            if cidr_sub_domain:
                nameserver_set = resource.cidr_endpoints_custom_sub_domain.get("nameserverSet", [])
                resource.cidr_endpoints_custom_sub_domain = {
                    "subDomain": cidr_sub_domain,
                    "nameserverSet": nameserver_set,
                }
            else:
                resource.cidr_endpoints_custom_sub_domain = {}

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()

        return {
            'verifiedAccessInstance': resource.to_dict(),
            }

    def _generate_id(self, prefix: str = 'verified') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class verifiedaccessinstance_RequestParser:
    @staticmethod
    def parse_create_verified_access_instance_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CidrEndpointsCustomSubDomain": get_scalar(md, "CidrEndpointsCustomSubDomain"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FIPSEnabled": get_scalar(md, "FIPSEnabled"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_verified_access_instance_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_describe_verified_access_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VerifiedAccessInstanceId.N": get_indexed_list(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_export_verified_access_instance_client_configuration_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_modify_verified_access_instance_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CidrEndpointsCustomSubDomain": get_scalar(md, "CidrEndpointsCustomSubDomain"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateVerifiedAccessInstance": verifiedaccessinstance_RequestParser.parse_create_verified_access_instance_request,
            "DeleteVerifiedAccessInstance": verifiedaccessinstance_RequestParser.parse_delete_verified_access_instance_request,
            "DescribeVerifiedAccessInstances": verifiedaccessinstance_RequestParser.parse_describe_verified_access_instances_request,
            "ExportVerifiedAccessInstanceClientConfiguration": verifiedaccessinstance_RequestParser.parse_export_verified_access_instance_client_configuration_request,
            "ModifyVerifiedAccessInstance": verifiedaccessinstance_RequestParser.parse_modify_verified_access_instance_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class verifiedaccessinstance_ResponseSerializer:
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
                xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_verified_access_instance_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVerifiedAccessInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
            xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessInstance>')
        xml_parts.append(f'</CreateVerifiedAccessInstanceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_verified_access_instance_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVerifiedAccessInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
            xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessInstance>')
        xml_parts.append(f'</DeleteVerifiedAccessInstanceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_verified_access_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVerifiedAccessInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize verifiedAccessInstanceSet
        _verifiedAccessInstanceSet_key = None
        if "verifiedAccessInstanceSet" in data:
            _verifiedAccessInstanceSet_key = "verifiedAccessInstanceSet"
        elif "VerifiedAccessInstanceSet" in data:
            _verifiedAccessInstanceSet_key = "VerifiedAccessInstanceSet"
        elif "VerifiedAccessInstances" in data:
            _verifiedAccessInstanceSet_key = "VerifiedAccessInstances"
        if _verifiedAccessInstanceSet_key:
            param_data = data[_verifiedAccessInstanceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<verifiedAccessInstanceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</verifiedAccessInstanceSet>')
            else:
                xml_parts.append(f'{indent_str}<verifiedAccessInstanceSet/>')
        xml_parts.append(f'</DescribeVerifiedAccessInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_export_verified_access_instance_client_configuration_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ExportVerifiedAccessInstanceClientConfigurationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize deviceTrustProviderSet
        _deviceTrustProviderSet_key = None
        if "deviceTrustProviderSet" in data:
            _deviceTrustProviderSet_key = "deviceTrustProviderSet"
        elif "DeviceTrustProviderSet" in data:
            _deviceTrustProviderSet_key = "DeviceTrustProviderSet"
        elif "DeviceTrustProviders" in data:
            _deviceTrustProviderSet_key = "DeviceTrustProviders"
        if _deviceTrustProviderSet_key:
            param_data = data[_deviceTrustProviderSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<deviceTrustProviderSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</deviceTrustProviderSet>')
            else:
                xml_parts.append(f'{indent_str}<deviceTrustProviderSet/>')
        # Serialize openVpnConfigurationSet
        _openVpnConfigurationSet_key = None
        if "openVpnConfigurationSet" in data:
            _openVpnConfigurationSet_key = "openVpnConfigurationSet"
        elif "OpenVpnConfigurationSet" in data:
            _openVpnConfigurationSet_key = "OpenVpnConfigurationSet"
        elif "OpenVpnConfigurations" in data:
            _openVpnConfigurationSet_key = "OpenVpnConfigurations"
        if _openVpnConfigurationSet_key:
            param_data = data[_openVpnConfigurationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<openVpnConfigurationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</openVpnConfigurationSet>')
            else:
                xml_parts.append(f'{indent_str}<openVpnConfigurationSet/>')
        # Serialize region
        _region_key = None
        if "region" in data:
            _region_key = "region"
        elif "Region" in data:
            _region_key = "Region"
        if _region_key:
            param_data = data[_region_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<region>{esc(str(param_data))}</region>')
        # Serialize userTrustProvider
        _userTrustProvider_key = None
        if "userTrustProvider" in data:
            _userTrustProvider_key = "userTrustProvider"
        elif "UserTrustProvider" in data:
            _userTrustProvider_key = "UserTrustProvider"
        if _userTrustProvider_key:
            param_data = data[_userTrustProvider_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<userTrustProvider>')
            xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</userTrustProvider>')
        # Serialize verifiedAccessInstanceId
        _verifiedAccessInstanceId_key = None
        if "verifiedAccessInstanceId" in data:
            _verifiedAccessInstanceId_key = "verifiedAccessInstanceId"
        elif "VerifiedAccessInstanceId" in data:
            _verifiedAccessInstanceId_key = "VerifiedAccessInstanceId"
        if _verifiedAccessInstanceId_key:
            param_data = data[_verifiedAccessInstanceId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessInstanceId>{esc(str(param_data))}</verifiedAccessInstanceId>')
        # Serialize version
        _version_key = None
        if "version" in data:
            _version_key = "version"
        elif "Version" in data:
            _version_key = "Version"
        if _version_key:
            param_data = data[_version_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<version>{esc(str(param_data))}</version>')
        xml_parts.append(f'</ExportVerifiedAccessInstanceClientConfigurationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_verified_access_instance_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVerifiedAccessInstanceResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
            xml_parts.extend(verifiedaccessinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessInstance>')
        xml_parts.append(f'</ModifyVerifiedAccessInstanceResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateVerifiedAccessInstance": verifiedaccessinstance_ResponseSerializer.serialize_create_verified_access_instance_response,
            "DeleteVerifiedAccessInstance": verifiedaccessinstance_ResponseSerializer.serialize_delete_verified_access_instance_response,
            "DescribeVerifiedAccessInstances": verifiedaccessinstance_ResponseSerializer.serialize_describe_verified_access_instances_response,
            "ExportVerifiedAccessInstanceClientConfiguration": verifiedaccessinstance_ResponseSerializer.serialize_export_verified_access_instance_client_configuration_response,
            "ModifyVerifiedAccessInstance": verifiedaccessinstance_ResponseSerializer.serialize_modify_verified_access_instance_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

