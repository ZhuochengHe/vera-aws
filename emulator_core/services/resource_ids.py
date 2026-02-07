from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class IdFormat:
    deadline: Optional[datetime] = None
    resource: Optional[str] = None
    use_long_ids: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.deadline is not None:
            # ISO 8601 format with Z suffix for UTC
            result["Deadline"] = self.deadline.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"
        if self.resource is not None:
            result["Resource"] = self.resource
        if self.use_long_ids is not None:
            result["UseLongIds"] = self.use_long_ids
        return result


@dataclass
class PrincipalIdFormat:
    arn: Optional[str] = None
    status_set: List[IdFormat] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Arn": self.arn,
            "StatusSet": [status.to_dict() for status in self.status_set],
        }


class ResourceIDsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state for shared data

    from datetime import datetime
    from typing import Any, Dict, List, Optional

    class IdFormat:
        def __init__(self, resource: Optional[str] = None, use_long_ids: Optional[bool] = None, deadline: Optional[datetime] = None):
            self.resource = resource
            self.use_long_ids = use_long_ids
            self.deadline = deadline

        def to_dict(self):
            d = {}
            if self.resource is not None:
                d["resource"] = self.resource
            if self.use_long_ids is not None:
                d["useLongIds"] = self.use_long_ids
            if self.deadline is not None:
                # Format as ISO8601 with Z suffix
                d["deadline"] = self.deadline.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            return d

    class PrincipalIdFormat:
        def __init__(self, arn: Optional[str] = None, status_set: Optional[List[IdFormat]] = None):
            self.arn = arn
            self.status_set = status_set or []

        def to_dict(self):
            d = {}
            if self.arn is not None:
                d["arn"] = self.arn
            d["statusSet"] = [status.to_dict() for status in self.status_set]
            return d

    class ResourceIDsBackend:
        def __init__(self, state):
            self.state = state
            # Initialize resource_ids dict if not present
            if not hasattr(self.state, "resource_ids"):
                self.state.resource_ids = {}
            # The resource types that support longer IDs (from the docs)
            self.supported_resources = {
                "bundle", "conversion-task", "customer-gateway", "dhcp-options", "elastic-ip-allocation",
                "elastic-ip-association", "export-task", "flow-log", "image", "import-task", "instance",
                "internet-gateway", "network-acl", "network-acl-association", "network-interface",
                "network-interface-attachment", "prefix-list", "reservation", "route-table",
                "route-table-association", "security-group", "snapshot", "subnet",
                "subnet-cidr-block-association", "volume", "vpc", "vpc-cidr-block-association",
                "vpc-endpoint", "vpc-peering-connection", "vpn-connection", "vpn-gateway",
                # Some resources appear in examples but not in the list explicitly, add ipv6 cidr block associations
                "vpc-ipv6-cidr-block-association", "subnet-ipv6-cidr-block-association"
            }
            # Resources currently in opt-in period for ModifyIdentityIdFormat (subset)
            self.opt_in_resources = {
                "bundle", "conversion-task", "customer-gateway", "dhcp-options", "elastic-ip-allocation",
                "elastic-ip-association", "export-task", "flow-log", "image", "import-task",
                "internet-gateway", "network-acl", "network-acl-association", "network-interface",
                "network-interface-attachment", "prefix-list", "route-table", "route-table-association",
                "security-group", "subnet", "subnet-cidr-block-association", "vpc",
                "vpc-cidr-block-association", "vpc-endpoint", "vpc-peering-connection",
                "vpn-connection", "vpn-gateway"
            }

        def describe_aggregate_id_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
            # DryRun param is optional, ignore permission checks for emulator
            # Compose statusSet for all supported resources with their global settings
            status_set = []
            all_use_long_ids = True
            # Global settings stored under key "aggregate" in resource_ids dict
            aggregate_settings = self.state.resource_ids.get("aggregate", {})
            for resource in sorted(self.supported_resources):
                # Each resource has dict with keys: use_long_ids (bool), deadline (datetime or None)
                res_settings = aggregate_settings.get(resource, {})
                use_long_ids = res_settings.get("use_long_ids", False)
                deadline = res_settings.get("deadline")
                if not use_long_ids:
                    all_use_long_ids = False
                id_format = IdFormat(resource=resource, use_long_ids=use_long_ids, deadline=deadline)
                status_set.append(id_format)
            return {
                "requestId": self.generate_request_id(),
                "useLongIdsAggregated": all_use_long_ids,
                "statusSet": [item.to_dict() for item in status_set],
            }

        def describe_identity_id_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
            principal_arn = params.get("PrincipalArn")
            if not principal_arn or not isinstance(principal_arn, str):
                raise ValueError("PrincipalArn is required and must be a string")
            resource_filter = params.get("Resource")
            if resource_filter is not None and resource_filter not in self.supported_resources:
                raise ValueError(f"Resource '{resource_filter}' is not supported")

            # Identity settings stored under key principal_arn in resource_ids dict
            identity_settings = self.state.resource_ids.get(principal_arn, {})
            status_set = []
            for resource in sorted(self.supported_resources):
                if resource_filter and resource != resource_filter:
                    continue
                res_settings = identity_settings.get(resource, {})
                use_long_ids = res_settings.get("use_long_ids", False)
                deadline = res_settings.get("deadline")
                id_format = IdFormat(resource=resource, use_long_ids=use_long_ids, deadline=deadline)
                status_set.append(id_format)
            return {
                "requestId": self.generate_request_id(),
                "statusSet": [item.to_dict() for item in status_set],
            }

        def describe_id_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
            resource_filter = params.get("Resource")
            if resource_filter is not None and resource_filter not in self.supported_resources:
                raise ValueError(f"Resource '{resource_filter}' is not supported")

            # The caller's principal is the owner id (simulate)
            principal_arn = self.get_owner_id()
            # Use identity settings for the caller principal
            identity_settings = self.state.resource_ids.get(principal_arn, {})
            status_set = []
            for resource in sorted(self.supported_resources):
                if resource_filter and resource != resource_filter:
                    continue
                res_settings = identity_settings.get(resource, {})
                use_long_ids = res_settings.get("use_long_ids", False)
                deadline = res_settings.get("deadline")
                id_format = IdFormat(resource=resource, use_long_ids=use_long_ids, deadline=deadline)
                status_set.append(id_format)
            return {
                "requestId": self.generate_request_id(),
                "statusSet": [item.to_dict() for item in status_set],
            }

        def describe_principal_id_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
            # Optional params
            max_results = params.get("MaxResults")
            next_token = params.get("NextToken")
            resource_filters = []
            # Resource.N is an array of strings, keys like Resource.1, Resource.2, etc.
            # We collect all keys starting with "Resource." and get their values
            for key, value in params.items():
                if key.startswith("Resource.") and isinstance(value, str):
                    resource_filters.append(value)
            # Validate max_results if provided
            if max_results is not None:
                if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
                    raise ValueError("MaxResults must be an integer between 1 and 1000")

            # Filter principalSet from resource_ids keys except "aggregate"
            principal_keys = [k for k in self.state.resource_ids.keys() if k != "aggregate"]
            # Sort for consistent order
            principal_keys.sort()
            # Pagination handling
            start_index = 0
            if next_token:
                try:
                    start_index = int(next_token)
                except Exception:
                    start_index = 0
            end_index = start_index + max_results if max_results else len(principal_keys)
            paged_principals = principal_keys[start_index:end_index]

            principal_set = []
            for principal_arn in paged_principals:
                identity_settings = self.state.resource_ids.get(principal_arn, {})
                status_set = []
                for resource in sorted(self.supported_resources):
                    if resource_filters and resource not in resource_filters:
                        continue
                    res_settings = identity_settings.get(resource, {})
                    use_long_ids = res_settings.get("use_long_ids", False)
                    deadline = res_settings.get("deadline")
                    id_format = IdFormat(resource=resource, use_long_ids=use_long_ids, deadline=deadline)
                    status_set.append(id_format)
                principal_id_format = PrincipalIdFormat(arn=principal_arn, status_set=status_set)
                principal_set.append(principal_id_format)

            # Determine next token for pagination
            new_next_token = None
            if end_index < len(principal_keys):
                new_next_token = str(end_index)

            return {
                "requestId": self.generate_request_id(),
                "principalSet": [p.to_dict() for p in principal_set],
                "nextToken": new_next_token,
            }

        def modify_identity_id_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
            principal_arn = params.get("PrincipalArn")
            resource = params.get("Resource")
            use_long_ids = params.get("UseLongIds")

            if not principal_arn or not isinstance(principal_arn, str):
                raise ValueError("PrincipalArn is required and must be a string")
            if not resource or not isinstance(resource, str):
                raise ValueError("Resource is required and must be a string")
            if use_long_ids is None or not isinstance(use_long_ids, bool):
                raise ValueError("UseLongIds is required and must be a boolean")

            # Validate resource: can be 'all-current' or 'all' or a resource in opt_in_resources
            if resource == "all-current":
                # Modify all resources currently in opt-in period
                resources_to_modify = self.opt_in_resources
            elif resource == "all":
                # Modify all resources for the principal
                resources_to_modify = self.supported_resources
            else:
                if resource not in self.opt_in_resources:
                    raise ValueError(f"Resource '{resource}' is not currently in opt-in period and cannot be modified")
                resources_to_modify = {resource}

            # Get or create principal settings dict
            if principal_arn not in self.state.resource_ids:
                self.state.resource_ids[principal_arn] = {}
            principal_settings = self.state.resource_ids[principal_arn]

            # Update use_long_ids for each resource in resources_to_modify
            for res in resources_to_modify:
                if res not in principal_settings:
                    principal_settings[res] = {}
                principal_settings[res]["use_long_ids"] = use_long_ids
                # Deadline is not changed by this call

            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

    def modify_id_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        resource = params.get("Resource")
        use_long_ids = params.get("UseLongIds")

        # Validate required parameters
        if resource is None:
            raise ValueError("Missing required parameter 'Resource'")
        if use_long_ids is None:
            raise ValueError("Missing required parameter 'UseLongIds'")
        if not isinstance(use_long_ids, bool):
            raise ValueError("'UseLongIds' must be a boolean")

        # List of valid resource types currently in opt-in period for longer IDs
        valid_resources = {
            "bundle", "conversion-task", "customer-gateway", "dhcp-options",
            "elastic-ip-allocation", "elastic-ip-association", "export-task",
            "flow-log", "image", "import-task", "internet-gateway", "network-acl",
            "network-acl-association", "network-interface", "network-interface-attachment",
            "prefix-list", "route-table", "route-table-association", "security-group",
            "subnet", "subnet-cidr-block-association", "vpc", "vpc-cidr-block-association",
            "vpc-endpoint", "vpc-peering-connection", "vpn-connection", "vpn-gateway"
        }

        # If resource is "all-current", apply to all valid resources
        if resource == "all-current":
            for res in valid_resources:
                self.state.resource_ids[res] = use_long_ids
        else:
            if resource not in valid_resources:
                raise ValueError(f"Invalid resource type '{resource}' for ModifyIdFormat")
            self.state.resource_ids[resource] = use_long_ids

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class ResourceIDsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeAggregateIdFormat", self.describe_aggregate_id_format)
        self.register_action("DescribeIdentityIdFormat", self.describe_identity_id_format)
        self.register_action("DescribeIdFormat", self.describe_id_format)
        self.register_action("DescribePrincipalIdFormat", self.describe_principal_id_format)
        self.register_action("ModifyIdentityIdFormat", self.modify_identity_id_format)
        self.register_action("ModifyIdFormat", self.modify_id_format)

    def describe_aggregate_id_format(self, params):
        return self.backend.describe_aggregate_id_format(params)

    def describe_identity_id_format(self, params):
        return self.backend.describe_identity_id_format(params)

    def describe_id_format(self, params):
        return self.backend.describe_id_format(params)

    def describe_principal_id_format(self, params):
        return self.backend.describe_principal_id_format(params)

    def modify_identity_id_format(self, params):
        return self.backend.modify_identity_id_format(params)

    def modify_id_format(self, params):
        return self.backend.modify_id_format(params)
