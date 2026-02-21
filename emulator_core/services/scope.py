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
class Scope:
    description: str = ""
    external_authority_configuration: Dict[str, Any] = field(default_factory=dict)
    ipam_arn: str = ""
    ipam_region: str = ""
    ipam_scope_arn: str = ""
    ipam_scope_id: str = ""
    ipam_scope_type: str = ""
    is_default: bool = False
    owner_id: str = ""
    pool_count: int = 0
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)

    ipam_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "externalAuthorityConfiguration": self.external_authority_configuration,
            "ipamArn": self.ipam_arn,
            "ipamId": self.ipam_id,
            "ipamRegion": self.ipam_region,
            "ipamScopeArn": self.ipam_scope_arn,
            "ipamScopeId": self.ipam_scope_id,
            "ipamScopeType": self.ipam_scope_type,
            "isDefault": self.is_default,
            "ownerId": self.owner_id,
            "poolCount": self.pool_count,
            "state": self.state,
            "tagSet": self.tag_set,
        }

class Scope_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.scopes  # alias to shared store

    def _get_scope_or_error(self, scope_id: str):
        scope = self.resources.get(scope_id)
        if not scope:
            return create_error_response("InvalidIpamScopeId.NotFound", f"The ID '{scope_id}' does not exist")
        return scope

    def CreateIpamScope(self, params: Dict[str, Any]):
        """Create an IPAM scope. In IPAM, a scope is the highest-level container within IPAM. An IPAM contains two default scopes. Each scope represents the IP space for a single network. The private scope is intended for all private IP address space. The public scope is intended for all public IP address spac"""

        if not params.get("IpamId"):
            return create_error_response("MissingParameter", "Missing required parameter: IpamId")

        ipam_id = params.get("IpamId")
        ipam = self.state.ipams.get(ipam_id)
        if not ipam:
            return create_error_response("InvalidIpamID.NotFound", f"IPAM '{ipam_id}' does not exist.")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            for tag in spec.get("Tags", []) or []:
                tag_set.append({"Key": tag.get("Key", ""), "Value": tag.get("Value", "")})

        external_config = params.get("ExternalAuthorityConfiguration")
        if not isinstance(external_config, dict):
            external_config = {}

        ipam_region = getattr(ipam, "ipam_region", "") or "us-east-1"
        ipam_arn = getattr(ipam, "ipam_arn", "")
        owner_id = getattr(ipam, "owner_id", "")
        ipam_scope_id = self._generate_id("ipam-scope")
        ipam_scope_arn = (
            f"arn:aws:ec2:{ipam_region}::ipam-scope/{ipam_scope_id}"
            if ipam_region
            else f"arn:aws:ec2:::ipam-scope/{ipam_scope_id}"
        )

        resource = Scope(
            description=params.get("Description") or "",
            external_authority_configuration=external_config,
            ipam_arn=ipam_arn,
            ipam_region=ipam_region,
            ipam_scope_arn=ipam_scope_arn,
            ipam_scope_id=ipam_scope_id,
            ipam_scope_type="private",
            is_default=False,
            owner_id=owner_id,
            pool_count=0,
            state="create-complete",
            tag_set=tag_set,
            ipam_id=ipam_id,
        )
        self.resources[ipam_scope_id] = resource
        ipam.scope_count = (ipam.scope_count or 0) + 1

        return {
            'ipamScope': resource.to_dict(),
            }


    def DeleteIpamScope(self, params: Dict[str, Any]):
        """Delete the scope for an IPAM. You cannot delete the default scopes. For more information, seeDelete a scopein theAmazon VPC IPAM User Guide."""

        if not params.get("IpamScopeId"):
            return create_error_response("MissingParameter", "Missing required parameter: IpamScopeId")

        ipam_scope_id = params.get("IpamScopeId")
        scope = self._get_scope_or_error(ipam_scope_id)
        if is_error_response(scope):
            return scope

        if scope.is_default:
            return create_error_response("DependencyViolation", "IPAM default scopes cannot be deleted.")

        dependent_pools = [
            pool for pool in self.state.pools.values()
            if getattr(pool, "ipam_scope_id", None) == ipam_scope_id
        ]
        if dependent_pools:
            return create_error_response(
                "DependencyViolation",
                "IPAM scope has dependent IPAM pools and cannot be deleted.",
            )

        ipam_data = scope.to_dict()
        ipam_id = scope.ipam_id
        if ipam_id:
            ipam = self.state.ipams.get(ipam_id)
            if ipam:
                ipam.scope_count = max(0, (ipam.scope_count or 0) - 1)

        del self.resources[ipam_scope_id]

        return {
            'ipamScope': ipam_data,
            }

    def DescribeIpamScopes(self, params: Dict[str, Any]):
        """Get information about your IPAM scopes."""

        ipam_scope_ids = params.get("IpamScopeId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if ipam_scope_ids:
            resources: List[Scope] = []
            for ipam_scope_id in ipam_scope_ids:
                scope = self.resources.get(ipam_scope_id)
                if not scope:
                    return create_error_response(
                        "InvalidIpamScopeId.NotFound",
                        f"The ID '{ipam_scope_id}' does not exist",
                    )
                resources.append(scope)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        scope_entries = [scope.to_dict() for scope in resources[:max_results]]

        return {
            'ipamScopeSet': scope_entries,
            'nextToken': None,
            }


    def ModifyIpamScope(self, params: Dict[str, Any]):
        """Modify an IPAM scope."""

        if not params.get("IpamScopeId"):
            return create_error_response("MissingParameter", "Missing required parameter: IpamScopeId")

        ipam_scope_id = params.get("IpamScopeId")
        scope = self._get_scope_or_error(ipam_scope_id)
        if is_error_response(scope):
            return scope

        if params.get("Description") is not None:
            scope.description = params.get("Description") or ""

        if str2bool(params.get("RemoveExternalAuthorityConfiguration")):
            scope.external_authority_configuration = {}

        if params.get("ExternalAuthorityConfiguration") is not None:
            config = params.get("ExternalAuthorityConfiguration")
            scope.external_authority_configuration = config if isinstance(config, dict) else {}

        return {
            'ipamScope': scope.to_dict(),
            }

    def _generate_id(self, prefix: str = 'ipam') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class scope_RequestParser:
    @staticmethod
    def parse_create_ipam_scope_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExternalAuthorityConfiguration": get_scalar(md, "ExternalAuthorityConfiguration"),
            "IpamId": get_scalar(md, "IpamId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_ipam_scope_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamScopeId": get_scalar(md, "IpamScopeId"),
        }

    @staticmethod
    def parse_describe_ipam_scopes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamScopeId.N": get_indexed_list(md, "IpamScopeId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_modify_ipam_scope_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExternalAuthorityConfiguration": get_scalar(md, "ExternalAuthorityConfiguration"),
            "IpamScopeId": get_scalar(md, "IpamScopeId"),
            "RemoveExternalAuthorityConfiguration": get_scalar(md, "RemoveExternalAuthorityConfiguration"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateIpamScope": scope_RequestParser.parse_create_ipam_scope_request,
            "DeleteIpamScope": scope_RequestParser.parse_delete_ipam_scope_request,
            "DescribeIpamScopes": scope_RequestParser.parse_describe_ipam_scopes_request,
            "ModifyIpamScope": scope_RequestParser.parse_modify_ipam_scope_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class scope_ResponseSerializer:
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
                xml_parts.extend(scope_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(scope_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(scope_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(scope_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(scope_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(scope_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_ipam_scope_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateIpamScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamScope
        _ipamScope_key = None
        if "ipamScope" in data:
            _ipamScope_key = "ipamScope"
        elif "IpamScope" in data:
            _ipamScope_key = "IpamScope"
        if _ipamScope_key:
            param_data = data[_ipamScope_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamScope>')
            xml_parts.extend(scope_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamScope>')
        xml_parts.append(f'</CreateIpamScopeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_ipam_scope_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteIpamScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamScope
        _ipamScope_key = None
        if "ipamScope" in data:
            _ipamScope_key = "ipamScope"
        elif "IpamScope" in data:
            _ipamScope_key = "IpamScope"
        if _ipamScope_key:
            param_data = data[_ipamScope_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamScope>')
            xml_parts.extend(scope_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamScope>')
        xml_parts.append(f'</DeleteIpamScopeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipam_scopes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpamScopesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamScopeSet
        _ipamScopeSet_key = None
        if "ipamScopeSet" in data:
            _ipamScopeSet_key = "ipamScopeSet"
        elif "IpamScopeSet" in data:
            _ipamScopeSet_key = "IpamScopeSet"
        elif "IpamScopes" in data:
            _ipamScopeSet_key = "IpamScopes"
        if _ipamScopeSet_key:
            param_data = data[_ipamScopeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamScopeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(scope_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamScopeSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamScopeSet/>')
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
        xml_parts.append(f'</DescribeIpamScopesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_ipam_scope_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyIpamScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamScope
        _ipamScope_key = None
        if "ipamScope" in data:
            _ipamScope_key = "ipamScope"
        elif "IpamScope" in data:
            _ipamScope_key = "IpamScope"
        if _ipamScope_key:
            param_data = data[_ipamScope_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamScope>')
            xml_parts.extend(scope_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamScope>')
        xml_parts.append(f'</ModifyIpamScopeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateIpamScope": scope_ResponseSerializer.serialize_create_ipam_scope_response,
            "DeleteIpamScope": scope_ResponseSerializer.serialize_delete_ipam_scope_response,
            "DescribeIpamScopes": scope_ResponseSerializer.serialize_describe_ipam_scopes_response,
            "ModifyIpamScope": scope_ResponseSerializer.serialize_modify_ipam_scope_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

