from __future__ import annotations
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid
import random
import json as _json

from ..utils import (
    create_gcp_error, is_error_response,
    make_operation, parse_labels, get_body_param,
)
from ..state import GCPState

@dataclass
class FirewallPolicie:
    self_link_with_id: str = ""
    display_name: str = ""
    name: str = ""
    rule_tuple_count: int = 0
    rules: List[Any] = field(default_factory=list)
    policy_type: str = ""
    creation_timestamp: str = ""
    associations: List[Any] = field(default_factory=list)
    region: str = ""
    short_name: str = ""
    description: str = ""
    parent: str = ""
    packet_mirroring_rules: List[Any] = field(default_factory=list)
    fingerprint: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.display_name is not None and self.display_name != "":
            d["displayName"] = self.display_name
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.rule_tuple_count is not None and self.rule_tuple_count != 0:
            d["ruleTupleCount"] = self.rule_tuple_count
        d["rules"] = self.rules
        if self.policy_type is not None and self.policy_type != "":
            d["policyType"] = self.policy_type
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["associations"] = self.associations
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.short_name is not None and self.short_name != "":
            d["shortName"] = self.short_name
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.parent is not None and self.parent != "":
            d["parent"] = self.parent
        d["packetMirroringRules"] = self.packet_mirroring_rules
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.id is not None and self.id != "":
            d["id"] = self.id
        if self.iam_policy:
            d["iamPolicy"] = self.iam_policy
        d["kind"] = "compute#firewallpolicie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class FirewallPolicie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.firewall_policies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "firewall-policie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_firewall_policy_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource 'firewallPolicies/{name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new policy in the specified project using the data included in
the request."""
        body = params.get("FirewallPolicy") or {}
        if not body:
            return create_gcp_error(400, "Required field 'FirewallPolicy' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"The resource '{name}' already exists", "ALREADY_EXISTS")
        creation_timestamp = body.get("creationTimestamp") or datetime.now(timezone.utc).isoformat()
        rules = body.get("rules", [])
        rule_tuple_count = body.get("ruleTupleCount")
        if rule_tuple_count is None:
            rule_tuple_count = len(rules)
        parent = body.get("parent") or params.get("parentId") or ""
        resource = FirewallPolicie(
            self_link_with_id=body.get("selfLinkWithId", ""),
            display_name=body.get("displayName", ""),
            name=name,
            rule_tuple_count=rule_tuple_count,
            rules=rules,
            policy_type=body.get("policyType", ""),
            creation_timestamp=creation_timestamp,
            associations=body.get("associations", []),
            region=body.get("region", ""),
            short_name=body.get("shortName", ""),
            description=body.get("description", ""),
            parent=parent,
            packet_mirroring_rules=body.get("packetMirroringRules", []),
            fingerprint=body.get("fingerprint", ""),
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy", {}),
        )
        self.resources[resource.name] = resource
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified firewall policy."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all the policies that have been configured for the specified
folder or organization."""
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        parent_id = params.get("parentId")
        if parent_id:
            resources = [r for r in resources if r.parent == parent_id]
        project = params.get("project", "")
        list_id = f"projects/{project}/global/firewallPolicies" if project else "global/firewallPolicies"
        return {
            "kind": "compute#firewallpolicieList",
            "id": list_id,
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("GlobalOrganizationSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'GlobalOrganizationSetPolicyRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_firewall_policy_or_error(resource_name)
        if is_error_response(resource):
            return resource
        resource.iam_policy = body.get("policy", body)
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=resource_link,
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified policy with the data included in the request."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        body = params.get("FirewallPolicy") or {}
        if not body:
            return create_gcp_error(400, "Required field 'FirewallPolicy' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        if "displayName" in body:
            resource.display_name = body.get("displayName") or ""
        if "name" in body:
            resource.name = body.get("name") or resource.name
        if "ruleTupleCount" in body:
            resource.rule_tuple_count = body.get("ruleTupleCount") or 0
        if "rules" in body:
            resource.rules = body.get("rules") or []
        if "policyType" in body:
            resource.policy_type = body.get("policyType") or ""
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or resource.creation_timestamp
        if "associations" in body:
            resource.associations = body.get("associations") or []
        if "region" in body:
            resource.region = body.get("region") or ""
        if "shortName" in body:
            resource.short_name = body.get("shortName") or ""
        if "description" in body:
            resource.description = body.get("description") or ""
        if "parent" in body:
            resource.parent = body.get("parent") or ""
        if "packetMirroringRules" in body:
            resource.packet_mirroring_rules = body.get("packetMirroringRules") or []
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "iamPolicy" in body:
            resource.iam_policy = body.get("iamPolicy") or {}
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
        )

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(resource_name)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

    def cloneRules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Copies rules to the specified firewall policy."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        source_policy_name = params.get("sourceFirewallPolicy")
        if not source_policy_name:
            return create_gcp_error(
                400,
                "Required field 'sourceFirewallPolicy' not specified",
                "INVALID_ARGUMENT",
            )
        target = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(target):
            return target
        source = self._get_firewall_policy_or_error(source_policy_name)
        if is_error_response(source):
            return source
        target.rules = list(source.rules)
        target.rule_tuple_count = len(target.rules)
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{target.name}"
            if project
            else f"global/firewallPolicies/{target.name}"
        )
        return make_operation(
            operation_type="cloneRules",
            resource_link=resource_link,
            params=params,
        )

    def getRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets a rule of the specified priority."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        priority = params.get("priority")
        if priority is None:
            return create_gcp_error(400, "Required field 'priority' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        for rule in resource.rules:
            if str(rule.get("priority")) == str(priority):
                return rule
        return create_gcp_error(404, f"Rule with priority {priority!r} was not found", "NOT_FOUND")

    def patchRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches a rule of the specified priority."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        body = params.get("FirewallPolicyRule") or {}
        if not body:
            return create_gcp_error(400, "Required field 'FirewallPolicyRule' not specified", "INVALID_ARGUMENT")
        priority = params.get("priority")
        if priority is None:
            priority = body.get("priority")
        if priority is None:
            return create_gcp_error(400, "Required field 'priority' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        for index, rule in enumerate(resource.rules):
            if str(rule.get("priority")) == str(priority):
                updated_rule = dict(rule)
                updated_rule.update(body)
                if "priority" not in updated_rule:
                    updated_rule["priority"] = priority
                resource.rules[index] = updated_rule
                resource.rule_tuple_count = len(resource.rules)
                project = params.get("project", "")
                resource_link = (
                    f"projects/{project}/global/firewallPolicies/{resource.name}"
                    if project
                    else f"global/firewallPolicies/{resource.name}"
                )
                return make_operation(
                    operation_type="patchRule",
                    resource_link=resource_link,
                    params=params,
                )
        return create_gcp_error(404, f"Rule with priority {priority!r} was not found", "NOT_FOUND")

    def removeAssociation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes an association for the specified firewall policy."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        assoc_name = params.get("name")
        if not assoc_name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        associations = resource.associations or []
        remaining = [assoc for assoc in associations if assoc.get("name") != assoc_name]
        if len(remaining) == len(associations):
            return create_gcp_error(404, f"Association {assoc_name!r} was not found", "NOT_FOUND")
        resource.associations = remaining
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="removeAssociation",
            resource_link=resource_link,
            params=params,
        )

    def listAssociations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists associations of a specified target, i.e., organization or folder."""
        target_resource = params.get("targetResource")
        associations: List[Any] = []
        for resource in self.resources.values():
            for assoc in resource.associations or []:
                if not target_resource or assoc.get("targetResource") == target_resource:
                    associations.append(assoc)
        return {
            "kind": "compute#firewallpolicieListAssociations",
            "items": associations,
        }

    def removeRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes a rule of the specified priority."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        priority = params.get("priority")
        if priority is None:
            return create_gcp_error(400, "Required field 'priority' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        original_rules = resource.rules or []
        remaining_rules = [rule for rule in original_rules if str(rule.get("priority")) != str(priority)]
        if len(remaining_rules) == len(original_rules):
            return create_gcp_error(404, f"Rule with priority {priority!r} was not found", "NOT_FOUND")
        resource.rules = remaining_rules
        resource.rule_tuple_count = len(remaining_rules)
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="removeRule",
            resource_link=resource_link,
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest")
        if body is None:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions", []) if isinstance(body, dict) else []
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def addAssociation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inserts an association for the specified firewall policy."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        body = params.get("FirewallPolicyAssociation") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'FirewallPolicyAssociation' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        assoc_name = body.get("name")
        if not assoc_name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        replace_existing = params.get("replaceExistingAssociation", False)
        associations = resource.associations or []
        existing_index = next((i for i, assoc in enumerate(associations) if assoc.get("name") == assoc_name), None)
        if existing_index is not None:
            if not replace_existing:
                return create_gcp_error(409, f"Association {assoc_name!r} already exists", "ALREADY_EXISTS")
            associations[existing_index] = body
        else:
            associations.append(body)
        resource.associations = associations
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="addAssociation",
            resource_link=resource_link,
            params=params,
        )

    def addRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inserts a rule into a firewall policy."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        body = params.get("FirewallPolicyRule") or {}
        if not body:
            return create_gcp_error(400, "Required field 'FirewallPolicyRule' not specified", "INVALID_ARGUMENT")
        priority = body.get("priority")
        if priority is None:
            return create_gcp_error(400, "Required field 'priority' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        for rule in resource.rules:
            if str(rule.get("priority")) == str(priority):
                return create_gcp_error(409, f"Rule with priority {priority!r} already exists", "ALREADY_EXISTS")
        resource.rules.append(body)
        resource.rule_tuple_count = len(resource.rules)
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="addRule",
            resource_link=resource_link,
            params=params,
        )

    def move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Moves the specified firewall policy."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        parent_id = params.get("parentId")
        if not parent_id:
            body = params.get("body") or {}
            parent_id = body.get("parentId") or body.get("parent")
        if not parent_id:
            return create_gcp_error(400, "Required field 'parentId' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        resource.parent = parent_id
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="move",
            resource_link=resource_link,
            params=params,
        )

    def getAssociation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets an association with the specified name."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        assoc_name = params.get("name")
        if not assoc_name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        for assoc in resource.associations or []:
            if assoc.get("name") == assoc_name:
                return assoc
        return create_gcp_error(404, f"Association {assoc_name!r} was not found", "NOT_FOUND")

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified policy."""
        firewall_policy = params.get("firewallPolicy")
        if not firewall_policy:
            return create_gcp_error(400, "Required field 'firewallPolicy' not specified", "INVALID_ARGUMENT")
        resource = self._get_firewall_policy_or_error(firewall_policy)
        if is_error_response(resource):
            return resource
        if resource.associations:
            return create_gcp_error(
                400,
                "Cannot delete firewall policy with existing associations",
                "FAILED_PRECONDITION",
            )
        del self.resources[resource.name]
        project = params.get("project", "")
        resource_link = (
            f"projects/{project}/global/firewallPolicies/{resource.name}"
            if project
            else f"global/firewallPolicies/{resource.name}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class firewall_policie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'delete': firewall_policie_RequestParser._parse_delete,
            'getIamPolicy': firewall_policie_RequestParser._parse_getIamPolicy,
            'insert': firewall_policie_RequestParser._parse_insert,
            'cloneRules': firewall_policie_RequestParser._parse_cloneRules,
            'getRule': firewall_policie_RequestParser._parse_getRule,
            'patchRule': firewall_policie_RequestParser._parse_patchRule,
            'removeAssociation': firewall_policie_RequestParser._parse_removeAssociation,
            'setIamPolicy': firewall_policie_RequestParser._parse_setIamPolicy,
            'listAssociations': firewall_policie_RequestParser._parse_listAssociations,
            'removeRule': firewall_policie_RequestParser._parse_removeRule,
            'testIamPermissions': firewall_policie_RequestParser._parse_testIamPermissions,
            'addAssociation': firewall_policie_RequestParser._parse_addAssociation,
            'patch': firewall_policie_RequestParser._parse_patch,
            'addRule': firewall_policie_RequestParser._parse_addRule,
            'move': firewall_policie_RequestParser._parse_move,
            'list': firewall_policie_RequestParser._parse_list,
            'getAssociation': firewall_policie_RequestParser._parse_getAssociation,
            'get': firewall_policie_RequestParser._parse_get,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_delete(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        return params

    @staticmethod
    def _parse_getIamPolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'optionsRequestedPolicyVersion' in query_params:
            params['optionsRequestedPolicyVersion'] = query_params['optionsRequestedPolicyVersion']
        return params

    @staticmethod
    def _parse_insert(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'parentId' in query_params:
            params['parentId'] = query_params['parentId']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['FirewallPolicy'] = body.get('FirewallPolicy')
        return params

    @staticmethod
    def _parse_cloneRules(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        if 'sourceFirewallPolicy' in query_params:
            params['sourceFirewallPolicy'] = query_params['sourceFirewallPolicy']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_getRule(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'priority' in query_params:
            params['priority'] = query_params['priority']
        return params

    @staticmethod
    def _parse_patchRule(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'priority' in query_params:
            params['priority'] = query_params['priority']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['FirewallPolicyRule'] = body.get('FirewallPolicyRule')
        return params

    @staticmethod
    def _parse_removeAssociation(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'name' in query_params:
            params['name'] = query_params['name']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_setIamPolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Body params
        params['GlobalOrganizationSetPolicyRequest'] = body.get('GlobalOrganizationSetPolicyRequest')
        return params

    @staticmethod
    def _parse_listAssociations(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'includeInheritedPolicies' in query_params:
            params['includeInheritedPolicies'] = query_params['includeInheritedPolicies']
        if 'targetResource' in query_params:
            params['targetResource'] = query_params['targetResource']
        return params

    @staticmethod
    def _parse_removeRule(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'priority' in query_params:
            params['priority'] = query_params['priority']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_testIamPermissions(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Body params
        params['TestPermissionsRequest'] = body.get('TestPermissionsRequest')
        return params

    @staticmethod
    def _parse_addAssociation(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'replaceExistingAssociation' in query_params:
            params['replaceExistingAssociation'] = query_params['replaceExistingAssociation']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['FirewallPolicyAssociation'] = body.get('FirewallPolicyAssociation')
        return params

    @staticmethod
    def _parse_patch(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['FirewallPolicy'] = body.get('FirewallPolicy')
        return params

    @staticmethod
    def _parse_addRule(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['FirewallPolicyRule'] = body.get('FirewallPolicyRule')
        return params

    @staticmethod
    def _parse_move(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'parentId' in query_params:
            params['parentId'] = query_params['parentId']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_list(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'parentId' in query_params:
            params['parentId'] = query_params['parentId']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_getAssociation(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'name' in query_params:
            params['name'] = query_params['name']
        return params

    @staticmethod
    def _parse_get(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        return params


class firewall_policie_ResponseSerializer:
    @staticmethod
    def serialize(
        method_name: str,
        data: Dict[str, Any],
        request_id: str,
    ) -> str:
        if is_error_response(data):
            from ..utils import serialize_gcp_error
            return serialize_gcp_error(data)
        serializers = {
            'delete': firewall_policie_ResponseSerializer._serialize_delete,
            'getIamPolicy': firewall_policie_ResponseSerializer._serialize_getIamPolicy,
            'insert': firewall_policie_ResponseSerializer._serialize_insert,
            'cloneRules': firewall_policie_ResponseSerializer._serialize_cloneRules,
            'getRule': firewall_policie_ResponseSerializer._serialize_getRule,
            'patchRule': firewall_policie_ResponseSerializer._serialize_patchRule,
            'removeAssociation': firewall_policie_ResponseSerializer._serialize_removeAssociation,
            'setIamPolicy': firewall_policie_ResponseSerializer._serialize_setIamPolicy,
            'listAssociations': firewall_policie_ResponseSerializer._serialize_listAssociations,
            'removeRule': firewall_policie_ResponseSerializer._serialize_removeRule,
            'testIamPermissions': firewall_policie_ResponseSerializer._serialize_testIamPermissions,
            'addAssociation': firewall_policie_ResponseSerializer._serialize_addAssociation,
            'patch': firewall_policie_ResponseSerializer._serialize_patch,
            'addRule': firewall_policie_ResponseSerializer._serialize_addRule,
            'move': firewall_policie_ResponseSerializer._serialize_move,
            'list': firewall_policie_ResponseSerializer._serialize_list,
            'getAssociation': firewall_policie_ResponseSerializer._serialize_getAssociation,
            'get': firewall_policie_ResponseSerializer._serialize_get,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_cloneRules(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patchRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeAssociation(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listAssociations(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addAssociation(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_move(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getAssociation(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

