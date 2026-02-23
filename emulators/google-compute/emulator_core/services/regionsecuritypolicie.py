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
class RegionSecurityPolicie:
    fingerprint: str = ""
    type: str = ""
    short_name: str = ""
    adaptive_protection_config: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    advanced_options_config: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    rules: List[Any] = field(default_factory=list)
    name: str = ""
    user_defined_fields: List[Any] = field(default_factory=list)
    region: str = ""
    parent: str = ""
    ddos_protection_config: Dict[str, Any] = field(default_factory=dict)
    label_fingerprint: str = ""
    associations: List[Any] = field(default_factory=list)
    labels: Dict[str, Any] = field(default_factory=dict)
    recaptcha_options_config: Dict[str, Any] = field(default_factory=dict)
    id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.type is not None and self.type != "":
            d["type"] = self.type
        if self.short_name is not None and self.short_name != "":
            d["shortName"] = self.short_name
        d["adaptiveProtectionConfig"] = self.adaptive_protection_config
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["advancedOptionsConfig"] = self.advanced_options_config
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["rules"] = self.rules
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["userDefinedFields"] = self.user_defined_fields
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.parent is not None and self.parent != "":
            d["parent"] = self.parent
        d["ddosProtectionConfig"] = self.ddos_protection_config
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        d["associations"] = self.associations
        d["labels"] = self.labels
        d["recaptchaOptionsConfig"] = self.recaptcha_options_config
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regionsecuritypolicie"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionSecurityPolicie_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_security_policies  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-security-policie") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_policy(self, name: str) -> Optional[RegionSecurityPolicie]:
        return self.resources.get(name)

    def _find_rule_index(self, policy: RegionSecurityPolicie, priority: Any) -> Optional[int]:
        if not policy:
            return None
        for idx, rule in enumerate(policy.rules):
            if not isinstance(rule, dict):
                continue
            rule_priority = rule.get("priority")
            if rule_priority == priority or str(rule_priority) == str(priority):
                return idx
        return None

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new policy in the specified project using the data included in
the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SecurityPolicy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SecurityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )
        if name in self.resources:
            return create_gcp_error(
                409,
                f"Security policy '{name}' already exists",
                "ALREADY_EXISTS",
            )

        resource = RegionSecurityPolicie(
            fingerprint=body.get("fingerprint") or "",
            type=body.get("type") or "",
            short_name=body.get("shortName") or "",
            adaptive_protection_config=body.get("adaptiveProtectionConfig") or {},
            description=body.get("description") or "",
            advanced_options_config=body.get("advancedOptionsConfig") or {},
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            rules=body.get("rules") or [],
            name=name,
            user_defined_fields=body.get("userDefinedFields") or [],
            region=region,
            parent=body.get("parent") or "",
            ddos_protection_config=body.get("ddosProtectionConfig") or {},
            label_fingerprint=body.get("labelFingerprint") or "",
            associations=body.get("associations") or [],
            labels=body.get("labels") or {},
            recaptcha_options_config=body.get("recaptchaOptionsConfig") or {},
            id=self._generate_id(),
        )
        if resource.labels and not resource.label_fingerprint:
            resource.label_fingerprint = str(uuid.uuid4())[:8]

        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/regions/{region}/RegionSecurityPolicies/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all of the ordered rules present in a single specified policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        policy_name = params.get("securityPolicy")
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'securityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(policy_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{policy_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all the policies that have been configured for the specified project
and region."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]

        return {
            "kind": "compute#regionsecuritypolicieList",
            "id": f"projects/{project}/regions/{region}/securityPolicies",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified policy with the data included in the request. To
clear fields in the policy, leave the fields empty and specify them in the
updateMask. This cannot be used to be update the ru..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        policy_name = params.get("securityPolicy")
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'securityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SecurityPolicy") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SecurityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(policy_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{policy_name}' was not found",
                "NOT_FOUND",
            )

        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "type" in body:
            resource.type = body.get("type") or ""
        if "shortName" in body:
            resource.short_name = body.get("shortName") or ""
        if "adaptiveProtectionConfig" in body:
            resource.adaptive_protection_config = body.get("adaptiveProtectionConfig") or {}
        if "description" in body:
            resource.description = body.get("description") or ""
        if "advancedOptionsConfig" in body:
            resource.advanced_options_config = body.get("advancedOptionsConfig") or {}
        if "rules" in body:
            resource.rules = body.get("rules") or []
        if "userDefinedFields" in body:
            resource.user_defined_fields = body.get("userDefinedFields") or []
        if "parent" in body:
            resource.parent = body.get("parent") or ""
        if "ddosProtectionConfig" in body:
            resource.ddos_protection_config = body.get("ddosProtectionConfig") or {}
        if "labelFingerprint" in body:
            resource.label_fingerprint = body.get("labelFingerprint") or ""
        if "associations" in body:
            resource.associations = body.get("associations") or []
        if "labels" in body:
            resource.labels = body.get("labels") or {}
            resource.label_fingerprint = str(uuid.uuid4())[:8]
        if "recaptchaOptionsConfig" in body:
            resource.recaptcha_options_config = body.get("recaptchaOptionsConfig") or {}

        resource_link = f"projects/{project}/regions/{region}/RegionSecurityPolicies/{resource.name}"
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
        )

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a security policy. To learn more about labels,
read the Labeling Resources
documentation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionSetLabelsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionSetLabelsRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(resource_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )

        resource.labels = body.get("labels") or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]

        resource_link = f"projects/{project}/regions/{region}/RegionSecurityPolicies/{resource.name}"
        return make_operation(
            operation_type="setLabels",
            resource_link=resource_link,
            params=params,
        )

    def removeRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes a rule at the specified priority."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        policy_name = params.get("securityPolicy")
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'securityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        priority = params.get("priority")
        if priority is None:
            return create_gcp_error(
                400,
                "Required field 'priority' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(policy_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{policy_name}' was not found",
                "NOT_FOUND",
            )

        rule_index = self._find_rule_index(resource, priority)
        if rule_index is None:
            return create_gcp_error(
                404,
                f"Rule with priority '{priority}' not found",
                "NOT_FOUND",
            )
        resource.rules.pop(rule_index)

        resource_link = f"projects/{project}/regions/{region}/RegionSecurityPolicies/{resource.name}"
        return make_operation(
            operation_type="removeRule",
            resource_link=resource_link,
            params=params,
        )

    def getRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets a rule at the specified priority."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        policy_name = params.get("securityPolicy")
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'securityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        priority = params.get("priority")
        if priority is None:
            return create_gcp_error(
                400,
                "Required field 'priority' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(policy_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{policy_name}' was not found",
                "NOT_FOUND",
            )

        rule_index = self._find_rule_index(resource, priority)
        if rule_index is None:
            return create_gcp_error(
                404,
                f"Rule with priority '{priority}' not found",
                "NOT_FOUND",
            )
        rule = resource.rules[rule_index]
        return rule if isinstance(rule, dict) else {"rule": rule}

    def addRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inserts a rule into a security policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        policy_name = params.get("securityPolicy")
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'securityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SecurityPolicyRule") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SecurityPolicyRule' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(policy_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{policy_name}' was not found",
                "NOT_FOUND",
            )

        priority = body.get("priority")
        if priority is None:
            return create_gcp_error(
                400,
                "Required field 'priority' not found",
                "INVALID_ARGUMENT",
            )
        if self._find_rule_index(resource, priority) is not None:
            return create_gcp_error(
                409,
                f"Rule with priority '{priority}' already exists",
                "ALREADY_EXISTS",
            )
        resource.rules.append(body)
        resource.rules.sort(
            key=lambda rule: rule.get("priority") if isinstance(rule, dict) else 0
        )

        resource_link = f"projects/{project}/regions/{region}/RegionSecurityPolicies/{resource.name}"
        return make_operation(
            operation_type="addRule",
            resource_link=resource_link,
            params=params,
        )

    def patchRule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches a rule at the specified priority. To clear fields in the rule,
leave the fields empty and specify them in the updateMask."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        policy_name = params.get("securityPolicy")
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'securityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SecurityPolicyRule") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SecurityPolicyRule' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(policy_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{policy_name}' was not found",
                "NOT_FOUND",
            )

        priority = params.get("priority")
        if priority is None:
            priority = body.get("priority")
        if priority is None:
            return create_gcp_error(
                400,
                "Required field 'priority' not found",
                "INVALID_ARGUMENT",
            )

        rule_index = self._find_rule_index(resource, priority)
        if rule_index is None:
            return create_gcp_error(
                404,
                f"Rule with priority '{priority}' not found",
                "NOT_FOUND",
            )
        existing_rule = resource.rules[rule_index]
        if not isinstance(existing_rule, dict):
            return create_gcp_error(
                400,
                "Stored rule is not a dict",
                "FAILED_PRECONDITION",
            )
        updated_rule = dict(existing_rule)
        updated_rule.update(body)
        updated_rule["priority"] = existing_rule.get("priority")
        resource.rules[rule_index] = updated_rule

        resource_link = f"projects/{project}/regions/{region}/RegionSecurityPolicies/{resource.name}"
        return make_operation(
            operation_type="patchRule",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        policy_name = params.get("securityPolicy")
        if not policy_name:
            return create_gcp_error(
                400,
                "Required field 'securityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_policy(policy_name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(
                404,
                f"The resource '{policy_name}' was not found",
                "NOT_FOUND",
            )

        del self.resources[resource.name]
        resource_link = f"projects/{project}/regions/{region}/RegionSecurityPolicies/{resource.name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class region_security_policie_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'list': region_security_policie_RequestParser._parse_list,
            'removeRule': region_security_policie_RequestParser._parse_removeRule,
            'insert': region_security_policie_RequestParser._parse_insert,
            'patch': region_security_policie_RequestParser._parse_patch,
            'getRule': region_security_policie_RequestParser._parse_getRule,
            'delete': region_security_policie_RequestParser._parse_delete,
            'addRule': region_security_policie_RequestParser._parse_addRule,
            'get': region_security_policie_RequestParser._parse_get,
            'setLabels': region_security_policie_RequestParser._parse_setLabels,
            'patchRule': region_security_policie_RequestParser._parse_patchRule,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
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
        # Full request body (resource representation)
        params["body"] = body
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
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        if 'validateOnly' in query_params:
            params['validateOnly'] = query_params['validateOnly']
        # Body params
        params['SecurityPolicy'] = body.get('SecurityPolicy')
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
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['SecurityPolicy'] = body.get('SecurityPolicy')
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
    def _parse_addRule(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'validateOnly' in query_params:
            params['validateOnly'] = query_params['validateOnly']
        # Body params
        params['SecurityPolicyRule'] = body.get('SecurityPolicyRule')
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

    @staticmethod
    def _parse_setLabels(
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
        params['RegionSetLabelsRequest'] = body.get('RegionSetLabelsRequest')
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
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        if 'validateOnly' in query_params:
            params['validateOnly'] = query_params['validateOnly']
        # Body params
        params['SecurityPolicyRule'] = body.get('SecurityPolicyRule')
        return params


class region_security_policie_ResponseSerializer:
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
            'list': region_security_policie_ResponseSerializer._serialize_list,
            'removeRule': region_security_policie_ResponseSerializer._serialize_removeRule,
            'insert': region_security_policie_ResponseSerializer._serialize_insert,
            'patch': region_security_policie_ResponseSerializer._serialize_patch,
            'getRule': region_security_policie_ResponseSerializer._serialize_getRule,
            'delete': region_security_policie_ResponseSerializer._serialize_delete,
            'addRule': region_security_policie_ResponseSerializer._serialize_addRule,
            'get': region_security_policie_ResponseSerializer._serialize_get,
            'setLabels': region_security_policie_ResponseSerializer._serialize_setLabels,
            'patchRule': region_security_policie_ResponseSerializer._serialize_patchRule,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patchRule(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

