from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class AuthorizationRuleState(Enum):
    AUTHORIZING = "authorizing"
    ACTIVE = "active"
    FAILED = "failed"
    REVOKING = "revoking"


@dataclass
class ClientVpnAuthorizationRuleStatus:
    code: AuthorizationRuleState
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"code": self.code.value}
        if self.message is not None:
            d["message"] = self.message
        return d


@dataclass
class AuthorizationRule:
    authorization_rule_id: str
    client_vpn_endpoint_id: str
    target_network_cidr: str
    access_group_id: Optional[str] = None
    authorize_all_groups: bool = False
    description: Optional[str] = None
    status: ClientVpnAuthorizationRuleStatus = field(
        default_factory=lambda: ClientVpnAuthorizationRuleStatus(AuthorizationRuleState.AUTHORIZING)
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessAll": self.authorize_all_groups,
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "description": self.description or "",
            "destinationCidr": self.target_network_cidr,
            "groupId": self.access_group_id or "",
            "status": self.status.to_dict(),
        }


class AuthorizationRulesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.authorization_rules dict for storage

    def _validate_client_vpn_endpoint_exists(self, client_vpn_endpoint_id: str):
        # Validate existence of ClientVpnEndpoint resource
        resource = self.state.get_resource(client_vpn_endpoint_id)
        if resource is None:
            raise ErrorCode(
                f"ClientVpnEndpoint {client_vpn_endpoint_id} does not exist",
                code="InvalidClientVpnEndpointId.NotFound",
            )

    def _validate_cidr(self, cidr: str):
        # Basic validation for CIDR format (very simple, can be improved)
        import ipaddress

        try:
            network = ipaddress.IPv4Network(cidr, strict=False)
        except Exception:
            raise ErrorCode(f"Invalid CIDR format: {cidr}", code="InvalidParameterValue")

    def _find_duplicate_rule(
        self,
        client_vpn_endpoint_id: str,
        target_network_cidr: str,
        access_group_id: Optional[str],
        authorize_all_groups: bool,
    ) -> Optional[AuthorizationRule]:
        # Check if a rule with same clientVpnEndpointId, targetNetworkCidr and group/all exists
        for rule in self.state.authorization_rules.values():
            if (
                rule.client_vpn_endpoint_id == client_vpn_endpoint_id
                and rule.target_network_cidr == target_network_cidr
                and rule.authorize_all_groups == authorize_all_groups
            ):
                if authorize_all_groups:
                    # If authorize_all_groups is True, access_group_id must be None
                    return rule
                else:
                    # If authorize_all_groups is False, access_group_id must match
                    if rule.access_group_id == access_group_id:
                        return rule
        return None

    def AuthorizeClientVpnIngress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        target_network_cidr = params.get("TargetNetworkCidr")
        if client_vpn_endpoint_id is None:
            raise ErrorCode("Missing required parameter ClientVpnEndpointId", code="MissingParameter")
        if target_network_cidr is None:
            raise ErrorCode("Missing required parameter TargetNetworkCidr", code="MissingParameter")

        # Validate types
        if not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode("ClientVpnEndpointId must be a string", code="InvalidParameterValue")
        if not isinstance(target_network_cidr, str):
            raise ErrorCode("TargetNetworkCidr must be a string", code="InvalidParameterValue")

        # Validate optional parameters
        access_group_id = params.get("AccessGroupId")
        authorize_all_groups = params.get("AuthorizeAllGroups")
        description = params.get("Description")
        dry_run = params.get("DryRun")

        # Validate types for optional params
        if access_group_id is not None and not isinstance(access_group_id, str):
            raise ErrorCode("AccessGroupId must be a string", code="InvalidParameterValue")
        if authorize_all_groups is not None and not isinstance(authorize_all_groups, bool):
            raise ErrorCode("AuthorizeAllGroups must be a boolean", code="InvalidParameterValue")
        if description is not None and not isinstance(description, str):
            raise ErrorCode("Description must be a string", code="InvalidParameterValue")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("DryRun must be a boolean", code="InvalidParameterValue")

        # Default authorize_all_groups to False if not specified
        if authorize_all_groups is None:
            authorize_all_groups = False

        # Validate that either AccessGroupId or AuthorizeAllGroups is set correctly
        if authorize_all_groups is False and not access_group_id:
            raise ErrorCode(
                "AccessGroupId is required if AuthorizeAllGroups is false or not specified",
                code="InvalidParameterCombination",
            )
        if authorize_all_groups is True and access_group_id is not None:
            raise ErrorCode(
                "AccessGroupId must not be specified if AuthorizeAllGroups is true",
                code="InvalidParameterCombination",
            )

        # Validate ClientVpnEndpoint exists
        self._validate_client_vpn_endpoint_exists(client_vpn_endpoint_id)

        # Validate TargetNetworkCidr format
        self._validate_cidr(target_network_cidr)

        # DryRun check (simulate permission check)
        if dry_run:
            # For simplicity, assume permission granted
            raise ErrorCode("DryRunOperation", code="DryRunOperation")

        # Check for duplicate rule
        duplicate_rule = self._find_duplicate_rule(
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            target_network_cidr=target_network_cidr,
            access_group_id=access_group_id,
            authorize_all_groups=authorize_all_groups,
        )
        if duplicate_rule:
            # According to AWS, duplicate authorization rules cause error
            raise ErrorCode(
                "Authorization rule already exists",
                code="ClientVpnAuthorizationRuleAlreadyExists",
            )

        # Create new AuthorizationRule
        authorization_rule_id = f"authr-{self.generate_unique_id()}"
        status = ClientVpnAuthorizationRuleStatus(AuthorizationRuleState.AUTHORIZING)
        rule = AuthorizationRule(
            authorization_rule_id=authorization_rule_id,
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            target_network_cidr=target_network_cidr,
            access_group_id=access_group_id,
            authorize_all_groups=authorize_all_groups,
            description=description,
            status=status,
        )

        # Store in shared state dict
        self.state.authorization_rules[authorization_rule_id] = rule

        # Return response
        return {
            "requestId": self.generate_request_id(),
            "status": status.to_dict(),
        }

    def DescribeClientVpnAuthorizationRules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if client_vpn_endpoint_id is None:
            raise ErrorCode("Missing required parameter ClientVpnEndpointId", code="MissingParameter")
        if not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode("ClientVpnEndpointId must be a string", code="InvalidParameterValue")

        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("DryRun must be a boolean", code="InvalidParameterValue")

        # Validate ClientVpnEndpoint exists
        self._validate_client_vpn_endpoint_exists(client_vpn_endpoint_id)

        # DryRun check
        if dry_run:
            raise ErrorCode("DryRunOperation", code="DryRunOperation")

        # Filters: Filter.N.Name and Filter.N.Values
        # AWS uses Filter.N syntax, but here we expect a list of dicts under "Filter.N"
        # We'll collect all filters from params keys starting with "Filter."
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                # key example: Filter.1.Name, Filter.1.Values.1
                # We need to parse filters properly
                # We'll collect filters by index
                # For simplicity, assume params["Filter.N"] is a list of dicts
                # But the spec says Filter.N is an array of Filter objects
                # So we expect params["Filter.N"] to be a list of dicts with Name and Values
                # We'll try to get "Filter.N" keys as list of dicts
                # But since params is flat dict, we expect "Filter.N" keys with dict values
                # So we try to parse filters from params.get("Filter.N")
                # We'll just check if "Filter.N" key exists and is list of dicts
                pass

        # Instead, check if "Filter.N" keys exist as list of dicts
        # We'll collect all filters from keys like "Filter.N" where N is int
        filter_list = []
        for key in params:
            if key.startswith("Filter."):
                # key example: Filter.1, Filter.2
                # We expect params[key] to be list of dicts with Name and Values
                val = params[key]
                if not isinstance(val, list):
                    raise ErrorCode(f"{key} must be a list of filter dicts", code="InvalidParameterValue")
                for f in val:
                    if not isinstance(f, dict):
                        raise ErrorCode(f"Filter elements must be dicts", code="InvalidParameterValue")
                    if "Name" not in f or "Values" not in f:
                        raise ErrorCode(f"Filter elements must have Name and Values", code="InvalidParameterValue")
                    if not isinstance(f["Name"], str):
                        raise ErrorCode(f"Filter Name must be string", code="InvalidParameterValue")
                    if not isinstance(f["Values"], list) or not all(isinstance(v, str) for v in f["Values"]):
                        raise ErrorCode(f"Filter Values must be list of strings", code="InvalidParameterValue")
                    filter_list.append(f)

        # Supported filter names:
        # description, destination-cidr, group-id
        # We'll filter rules accordingly
        def rule_matches_filter(rule: AuthorizationRule, filter_obj: Dict[str, Any]) -> bool:
            name = filter_obj["Name"]
            values = filter_obj["Values"]
            if name == "description":
                return any((rule.description or "") == v for v in values)
            elif name == "destination-cidr":
                return any(rule.target_network_cidr == v for v in values)
            elif name == "group-id":
                return any((rule.access_group_id or "") == v for v in values)
            else:
                # Unknown filter name: no match
                return False

        # Filter rules by clientVpnEndpointId first
        filtered_rules = [
            rule
            for rule in self.state.authorization_rules.values()
            if rule.client_vpn_endpoint_id == client_vpn_endpoint_id
        ]

        # Apply filters if any
        for f in filter_list:
            filtered_rules = [r for r in filtered_rules if rule_matches_filter(r, f)]

        # Pagination: MaxResults and NextToken
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("MaxResults must be an integer", code="InvalidParameterValue")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode("MaxResults must be between 5 and 1000", code="InvalidParameterValue")

        # next_token is a string token representing an index offset
        start_index = 0
        if next_token is not None:
            if not isinstance(next_token, str):
                raise ErrorCode("NextToken must be a string", code="InvalidParameterValue")
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("Invalid NextToken", code="InvalidParameterValue")

        # Paginate
        end_index = len(filtered_rules)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_rules))

        page_rules = filtered_rules[start_index:end_index]

        # Determine next token
        new_next_token = None
        if end_index < len(filtered_rules):
            new_next_token = str(end_index)

        # Build response
        return {
            "requestId": self.generate_request_id(),
            "authorizationRule": [rule.to_dict() for rule in page_rules],
            "nextToken": new_next_token,
        }

    def RevokeClientVpnIngress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        target_network_cidr = params.get("TargetNetworkCidr")
        if client_vpn_endpoint_id is None:
            raise ErrorCode("Missing required parameter ClientVpnEndpointId", code="MissingParameter")
        if target_network_cidr is None:
            raise ErrorCode("Missing required parameter TargetNetworkCidr", code="MissingParameter")

        if not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode("ClientVpnEndpointId must be a string", code="InvalidParameterValue")
        if not isinstance(target_network_cidr, str):
            raise ErrorCode("TargetNetworkCidr must be a string", code="InvalidParameterValue")

        access_group_id = params.get("AccessGroupId")
        revoke_all_groups = params.get("RevokeAllGroups")
        dry_run = params.get("DryRun")

        if access_group_id is not None and not isinstance(access_group_id, str):
            raise ErrorCode("AccessGroupId must be a string", code="InvalidParameterValue")
        if revoke_all_groups is not None and not isinstance(revoke_all_groups, bool):
            raise ErrorCode("RevokeAllGroups must be a boolean", code="InvalidParameterValue")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("DryRun must be a boolean", code="InvalidParameterValue")

        # Validate ClientVpnEndpoint exists
        self._validate_client_vpn_endpoint_exists(client_vpn_endpoint_id)

        # Validate TargetNetworkCidr format
        self._validate_cidr(target_network_cidr)

        # DryRun check
        if dry_run:
            raise ErrorCode("DryRunOperation", code="DryRunOperation")

        # Validate that either AccessGroupId or RevokeAllGroups is set correctly
        if revoke_all_groups is None:
            revoke_all_groups = False

        if revoke_all_groups is False and not access_group_id:
            raise ErrorCode(
                "AccessGroupId is required if RevokeAllGroups is false or not specified",
                code="InvalidParameterCombination",
            )
        if revoke_all_groups is True and access_group_id is not None:
            raise ErrorCode(
                "AccessGroupId must not be specified if RevokeAllGroups is true",
                code="InvalidParameterCombination",
            )

        # Find matching authorization rules to revoke
        to_revoke_ids = []
        for rule_id, rule in self.state.authorization_rules.items():
            if (
                rule.client_vpn_endpoint_id == client_vpn_endpoint_id
                and rule.target_network_cidr == target_network_cidr
            ):
                if revoke_all_groups:
                    if rule.authorize_all_groups:
                        to_revoke_ids.append(rule_id)
                else:
                    if not rule.authorize_all_groups and rule.access_group_id == access_group_id:
                        to_revoke_ids.append(rule_id)

        if not to_revoke_ids:
            # AWS returns success even if no matching rule found
            # But here we simulate success with status revoking
            status = ClientVpnAuthorizationRuleStatus(AuthorizationRuleState.REVOKING)
            return {
                "requestId": self.generate_request_id(),
                "status": status.to_dict(),
            }

        # Mark rules as revoking and remove them from state
        for rule_id in to_revoke_ids:
            rule = self.state.authorization_rules[rule_id]
            rule.status = ClientVpnAuthorizationRuleStatus(AuthorizationRuleState.REVOKING)
            # Remove from state to simulate revocation
            del self.state.authorization_rules[rule_id]

        # Return status of revoking
        status = ClientVpnAuthorizationRuleStatus(AuthorizationRuleState.REVOKING)
        return {
            "requestId": self.generate_request_id(),
            "status": status.to_dict(),
        }

from emulator_core.gateway.base import BaseGateway

class AuthorizationrulesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AuthorizeClientVpnIngress", self.authorize_client_vpn_ingress)
        self.register_action("DescribeClientVpnAuthorizationRules", self.describe_client_vpn_authorization_rules)
        self.register_action("RevokeClientVpnIngress", self.revoke_client_vpn_ingress)

    def authorize_client_vpn_ingress(self, params):
        return self.backend.authorize_client_vpn_ingress(params)

    def describe_client_vpn_authorization_rules(self, params):
        return self.backend.describe_client_vpn_authorization_rules(params)

    def revoke_client_vpn_ingress(self, params):
        return self.backend.revoke_client_vpn_ingress(params)
