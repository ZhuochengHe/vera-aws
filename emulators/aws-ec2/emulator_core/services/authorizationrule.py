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
class AuthorizationRule:
    access_all: bool = False
    client_vpn_endpoint_id: str = ""
    description: str = ""
    destination_cidr: str = ""
    group_id: str = ""
    status: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessAll": self.access_all,
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "description": self.description,
            "destinationCidr": self.destination_cidr,
            "groupId": self.group_id,
            "status": self.status,
        }

class AuthorizationRule_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.authorization_rules  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.security_groups.get(params['group_id']).authorization_rule_ids.append(new_id)
    #   Delete: self.state.security_groups.get(resource.group_id).authorization_rule_ids.remove(resource_id)

    def _get_client_vpn_endpoint(self, client_vpn_endpoint_id: str):
        endpoint = self.state.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )
        return endpoint

    def _list_authorization_rules(self, client_vpn_endpoint_id: str) -> List[AuthorizationRule]:
        return [
            rule
            for rule in self.resources.values()
            if rule.client_vpn_endpoint_id == client_vpn_endpoint_id
        ]

    def AuthorizeClientVpnIngress(self, params: Dict[str, Any]):
        """Adds an ingress authorization rule to a Client VPN endpoint. Ingress authorization rules act as 
			firewall rules that grant access to networks. You must configure ingress authorization rules to 
			enable clients to access resources in AWS or on-premises networks."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        target_network_cidr = params.get("TargetNetworkCidr")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")
        if not target_network_cidr:
            return create_error_response("MissingParameter", "TargetNetworkCidr is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        authorize_all_groups = str2bool(params.get("AuthorizeAllGroups"))
        access_group_id = params.get("AccessGroupId")
        if not authorize_all_groups and not access_group_id:
            return create_error_response(
                "MissingParameter",
                "AccessGroupId is required when AuthorizeAllGroups is false.",
            )

        if access_group_id:
            parent_group = self.state.security_groups.get(access_group_id)
            if not parent_group:
                return create_error_response(
                    "InvalidGroup.NotFound",
                    f"Security group '{access_group_id}' does not exist.",
                )

        description = params.get("Description") or ""
        existing = next(
            (
                rule
                for rule in self._list_authorization_rules(client_vpn_endpoint_id)
                if rule.destination_cidr == target_network_cidr
                and rule.group_id == (access_group_id or "")
                and rule.access_all == authorize_all_groups
            ),
            None,
        )

        if existing:
            status = existing.status or {"code": "active", "message": "Authorization rule active"}
            return {
                'status': [status],
                }

        status = {"code": "active", "message": "Authorization rule active"}
        resource = AuthorizationRule(
            access_all=authorize_all_groups,
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            description=description,
            destination_cidr=target_network_cidr,
            group_id=access_group_id or "",
            status=status,
        )
        resource_id = self._generate_id("client")
        self.resources[resource_id] = resource
        if access_group_id:
            parent_group = self.state.security_groups.get(access_group_id)
            if parent_group and hasattr(parent_group, "authorization_rule_ids"):
                parent_group.authorization_rule_ids.append(resource_id)

        return {
            'status': [status],
            }

    def DescribeClientVpnAuthorizationRules(self, params: Dict[str, Any]):
        """Describes the authorization rules for a specified Client VPN endpoint."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        rules = self._list_authorization_rules(client_vpn_endpoint_id)
        filters = params.get("Filter.N") or []
        if filters:
            rules = apply_filters(rules, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = int(next_token or 0)
        paged_rules = rules[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(rules):
            new_next_token = str(start_index + max_results)

        return {
            'authorizationRule': [rule.to_dict() for rule in paged_rules],
            'nextToken': new_next_token,
            }

    def RevokeClientVpnIngress(self, params: Dict[str, Any]):
        """Removes an ingress authorization rule from a Client VPN endpoint."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        target_network_cidr = params.get("TargetNetworkCidr")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")
        if not target_network_cidr:
            return create_error_response("MissingParameter", "TargetNetworkCidr is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        revoke_all_groups = str2bool(params.get("RevokeAllGroups"))
        access_group_id = params.get("AccessGroupId")
        if not revoke_all_groups and not access_group_id:
            return create_error_response(
                "MissingParameter",
                "AccessGroupId is required when RevokeAllGroups is false.",
            )

        if access_group_id:
            parent_group = self.state.security_groups.get(access_group_id)
            if not parent_group:
                return create_error_response(
                    "InvalidGroup.NotFound",
                    f"Security group '{access_group_id}' does not exist.",
                )

        matching_ids = []
        for resource_id, rule in list(self.resources.items()):
            if rule.client_vpn_endpoint_id != client_vpn_endpoint_id:
                continue
            if rule.destination_cidr != target_network_cidr:
                continue
            if revoke_all_groups:
                if not rule.access_all:
                    continue
            else:
                if rule.group_id != (access_group_id or ""):
                    continue
            matching_ids.append(resource_id)

        if not matching_ids:
            return create_error_response(
                "InvalidClientVpnAuthorizationRule.NotFound",
                f"Authorization rule for '{target_network_cidr}' does not exist.",
            )

        for resource_id in matching_ids:
            rule = self.resources.pop(resource_id, None)
            if not rule:
                continue
            parent_group = self.state.security_groups.get(rule.group_id)
            if parent_group and hasattr(parent_group, "authorization_rule_ids"):
                if resource_id in parent_group.authorization_rule_ids:
                    parent_group.authorization_rule_ids.remove(resource_id)

        status = {"code": "revoking", "message": "Authorization rule revoked"}
        return {
            'status': [status],
            }

    def _generate_id(self, prefix: str = 'client') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class authorizationrule_RequestParser:
    @staticmethod
    def parse_authorize_client_vpn_ingress_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AccessGroupId": get_scalar(md, "AccessGroupId"),
            "AuthorizeAllGroups": get_scalar(md, "AuthorizeAllGroups"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TargetNetworkCidr": get_scalar(md, "TargetNetworkCidr"),
        }

    @staticmethod
    def parse_describe_client_vpn_authorization_rules_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_revoke_client_vpn_ingress_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AccessGroupId": get_scalar(md, "AccessGroupId"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RevokeAllGroups": get_scalar(md, "RevokeAllGroups"),
            "TargetNetworkCidr": get_scalar(md, "TargetNetworkCidr"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AuthorizeClientVpnIngress": authorizationrule_RequestParser.parse_authorize_client_vpn_ingress_request,
            "DescribeClientVpnAuthorizationRules": authorizationrule_RequestParser.parse_describe_client_vpn_authorization_rules_request,
            "RevokeClientVpnIngress": authorizationrule_RequestParser.parse_revoke_client_vpn_ingress_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class authorizationrule_ResponseSerializer:
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
                xml_parts.extend(authorizationrule_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(authorizationrule_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(authorizationrule_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(authorizationrule_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(authorizationrule_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(authorizationrule_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_authorize_client_vpn_ingress_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AuthorizeClientVpnIngressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
                    xml_parts.extend(authorizationrule_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</AuthorizeClientVpnIngressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_client_vpn_authorization_rules_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeClientVpnAuthorizationRulesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize authorizationRule
        _authorizationRule_key = None
        if "authorizationRule" in data:
            _authorizationRule_key = "authorizationRule"
        elif "AuthorizationRule" in data:
            _authorizationRule_key = "AuthorizationRule"
        if _authorizationRule_key:
            param_data = data[_authorizationRule_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<authorizationRuleSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(authorizationrule_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</authorizationRuleSet>')
            else:
                xml_parts.append(f'{indent_str}<authorizationRuleSet/>')
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
        xml_parts.append(f'</DescribeClientVpnAuthorizationRulesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_revoke_client_vpn_ingress_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RevokeClientVpnIngressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
                    xml_parts.extend(authorizationrule_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</RevokeClientVpnIngressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AuthorizeClientVpnIngress": authorizationrule_ResponseSerializer.serialize_authorize_client_vpn_ingress_response,
            "DescribeClientVpnAuthorizationRules": authorizationrule_ResponseSerializer.serialize_describe_client_vpn_authorization_rules_response,
            "RevokeClientVpnIngress": authorizationrule_ResponseSerializer.serialize_revoke_client_vpn_ingress_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

