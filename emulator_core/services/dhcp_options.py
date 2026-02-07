from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class AttributeValue:
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class DhcpConfiguration:
    key: Optional[str] = None
    valueSet: List[AttributeValue] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "valueSet": [v.to_dict() for v in self.valueSet],
        }


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class DhcpOptions:
    dhcp_options_id: str
    dhcp_configuration_set: List[DhcpConfiguration] = field(default_factory=list)
    owner_id: str = ""
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dhcpOptionsId": self.dhcp_options_id,
            "ownerId": self.owner_id,
            "dhcpConfigurationSet": [dc.to_dict() for dc in self.dhcp_configuration_set],
            "tagSet": [tag.to_dict() for tag in self.tag_set],
        }


class DhcpOptionsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.dhcp_options dict for storage

    def _parse_tags(self, params: Dict[str, Any]) -> List[Tag]:
        tags: List[Tag] = []
        # TagSpecification.N is an array of TagSpecification objects
        # Each TagSpecification has ResourceType and Tags (array of Tag objects)
        # We only accept tags for resource type "dhcp-options"
        # The param keys are like TagSpecification.1.ResourceType, TagSpecification.1.Tags.1.Key, TagSpecification.1.Tags.1.Value, etc.

        # Collect all TagSpecification.N indices
        tag_spec_indices = set()
        for key in params.keys():
            if key.startswith("TagSpecification."):
                parts = key.split(".")
                if len(parts) >= 2 and parts[1].isdigit():
                    tag_spec_indices.add(int(parts[1]))
        for idx in sorted(tag_spec_indices):
            resource_type_key = f"TagSpecification.{idx}.ResourceType"
            resource_type = params.get(resource_type_key)
            if resource_type != "dhcp-options":
                # Ignore tags for other resource types
                continue
            # Collect tags for this TagSpecification
            # Tags are under TagSpecification.N.Tags.M.Key and TagSpecification.N.Tags.M.Value
            tag_indices = set()
            prefix = f"TagSpecification.{idx}.Tags."
            for key in params.keys():
                if key.startswith(prefix):
                    parts = key.split(".")
                    if len(parts) >= 4 and parts[3].isdigit():
                        tag_indices.add(int(parts[3]))
            for tag_idx in sorted(tag_indices):
                key_key = f"TagSpecification.{idx}.Tags.{tag_idx}.Key"
                value_key = f"TagSpecification.{idx}.Tags.{tag_idx}.Value"
                tag_key = params.get(key_key)
                tag_value = params.get(value_key)
                if tag_key is None or tag_value is None:
                    continue  # skip incomplete tag
                # Validate tag key constraints
                if tag_key.lower().startswith("aws:"):
                    raise ErrorCode(
                        "InvalidParameterValue",
                        f"Tag key '{tag_key}' may not begin with 'aws:'.",
                    )
                if len(tag_key) > 127:
                    raise ErrorCode(
                        "InvalidParameterValue",
                        f"Tag key '{tag_key}' exceeds maximum length of 127 characters.",
                    )
                if len(tag_value) > 256:
                    raise ErrorCode(
                        "InvalidParameterValue",
                        f"Tag value for key '{tag_key}' exceeds maximum length of 256 characters.",
                    )
                tags.append(Tag(Key=tag_key, Value=tag_value))
        return tags

    def _parse_dhcp_configurations(
        self, params: Dict[str, Any]
    ) -> List[DhcpConfiguration]:
        # DhcpConfiguration.N.Key and DhcpConfiguration.N.Value.M
        # We need to parse all N indices, then for each N parse Key and Values
        dhcp_configurations: List[DhcpConfiguration] = []

        # Find all N indices for DhcpConfiguration
        dhcp_config_indices = set()
        for key in params.keys():
            if key.startswith("DhcpConfiguration."):
                parts = key.split(".")
                if len(parts) >= 2 and parts[1].isdigit():
                    dhcp_config_indices.add(int(parts[1]))

        for idx in sorted(dhcp_config_indices):
            key_key = f"DhcpConfiguration.{idx}.Key"
            key_value = params.get(key_key)
            # Key is optional per resource JSON, but usually present
            # Values are optional too
            # Parse Values: DhcpConfiguration.N.Value.M
            value_prefix = f"DhcpConfiguration.{idx}.Value."
            value_indices = set()
            for k in params.keys():
                if k.startswith(value_prefix):
                    parts = k.split(".")
                    if len(parts) >= 4 and parts[3].isdigit():
                        value_indices.add(int(parts[3]))
            values: List[AttributeValue] = []
            for v_idx in sorted(value_indices):
                val_key = f"DhcpConfiguration.{idx}.Value.{v_idx}"
                val = params.get(val_key)
                if val is not None:
                    # AWS allows comma separated values in a single Value string to preserve order
                    # We split by comma and strip spaces
                    split_vals = [v.strip() for v in val.split(",") if v.strip()]
                    for sv in split_vals:
                        values.append(AttributeValue(Value=sv))
            dhcp_configurations.append(
                DhcpConfiguration(key=key_value, valueSet=values)
            )
        return dhcp_configurations

    def create_dhcp_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if "DryRun" in params:
            dry_run = params["DryRun"]
            if not isinstance(dry_run, bool):
                raise ErrorCode(
                    "InvalidParameterValue", "DryRun must be a boolean if specified."
                )
            # DryRun logic is not implemented here, just placeholder
            # In real AWS, would check permissions and raise DryRunOperation or UnauthorizedOperation
            # We skip that here

        # DhcpConfiguration.N is required
        # Validate presence of at least one DhcpConfiguration.N.Key or DhcpConfiguration.N.Value.M
        dhcp_configurations = self._parse_dhcp_configurations(params)
        if not dhcp_configurations:
            raise ErrorCode(
                "MissingParameter",
                "At least one DhcpConfiguration.N must be specified with Key or Values.",
            )

        # Validate tags
        tags = self._parse_tags(params)

        # Generate unique ID
        dhcp_options_id = f"dopt-{self.generate_unique_id()}"

        # Owner ID
        owner_id = self.get_owner_id()

        dhcp_options = DhcpOptions(
            dhcp_options_id=dhcp_options_id,
            dhcp_configuration_set=dhcp_configurations,
            owner_id=owner_id,
            tag_set=tags,
        )

        # Store in shared state dict
        self.state.dhcp_options[dhcp_options_id] = dhcp_options

        return {
            "requestId": self.generate_request_id(),
            "dhcpOptions": dhcp_options.to_dict(),
        }

    def delete_dhcp_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if "DryRun" in params:
            dry_run = params["DryRun"]
            if not isinstance(dry_run, bool):
                raise ErrorCode(
                    "InvalidParameterValue", "DryRun must be a boolean if specified."
                )
            # DryRun logic placeholder

        dhcp_options_id = params.get("DhcpOptionsId")
        if not dhcp_options_id or not isinstance(dhcp_options_id, str):
            raise ErrorCode(
                "MissingParameter", "DhcpOptionsId parameter is required and must be a string."
            )

        # Validate existence - LocalStack compatibility: Return success if not found (idempotent delete)
        dhcp_options = self.state.dhcp_options.get(dhcp_options_id)
        if dhcp_options is None:
            return {"requestId": self.generate_request_id(), "return": True}

        # Check if DHCP options set is associated with any VPC
        # We must disassociate before deletion
        for vpc_id, vpc in self.state.vpcs.items():
            # VPC uses camelCase attribute name: dhcpOptionsId
            vpc_dhcp_options_id = getattr(vpc, "dhcpOptionsId", None)
            # If None or "default", it's using the default DHCP options set
            # Otherwise, check if it matches the one we're trying to delete
            if vpc_dhcp_options_id and vpc_dhcp_options_id == dhcp_options_id:
                raise ErrorCode(
                    "DependencyViolation",
                    f"Cannot delete DHCP options set {dhcp_options_id} because it is associated with VPC {vpc_id}.",
                )

        # Delete from state
        del self.state.dhcp_options[dhcp_options_id]

        return {"requestId": self.generate_request_id(), "return": True}

    def describe_dhcp_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if "DryRun" in params:
            dry_run = params["DryRun"]
            if not isinstance(dry_run, bool):
                raise ErrorCode(
                    "InvalidParameterValue", "DryRun must be a boolean if specified."
                )
            # DryRun logic placeholder

        # DhcpOptionsId.N is optional list of strings
        dhcp_options_ids: Optional[List[str]] = None
        # Collect DhcpOptionsId.N keys
        dhcp_options_id_indices = set()
        for key in params.keys():
            if key.startswith("DhcpOptionsId."):
                parts = key.split(".")
                if len(parts) == 2 and parts[1].isdigit():
                    dhcp_options_id_indices.add(int(parts[1]))
        if dhcp_options_id_indices:
            dhcp_options_ids = []
            for idx in sorted(dhcp_options_id_indices):
                val = params.get(f"DhcpOptionsId.{idx}")
                if val is not None:
                    dhcp_options_ids.append(val)

        # Filters: Filter.N.Name and Filter.N.Value.M
        filters = []
        filter_indices = set()
        for key in params.keys():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3 and parts[1].isdigit():
                    filter_indices.add(int(parts[1]))
        for idx in sorted(filter_indices):
            name_key = f"Filter.{idx}.Name"
            name = params.get(name_key)
            if not name:
                continue
            # Collect values
            values = []
            value_indices = set()
            prefix = f"Filter.{idx}.Value."
            for k in params.keys():
                if k.startswith(prefix):
                    parts = k.split(".")
                    if len(parts) == 4 and parts[3].isdigit():
                        value_indices.add(int(parts[3]))
            for v_idx in sorted(value_indices):
                val = params.get(f"Filter.{idx}.Value.{v_idx}")
                if val is not None:
                    values.append(val)
            filters.append({"Name": name, "Values": values})

        # MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode(
                    "InvalidParameterValue", "MaxResults must be an integer if specified."
                )
            if max_results < 5 or max_results > 1000:
                raise ErrorCode(
                    "InvalidParameterValue",
                    "MaxResults must be between 5 and 1000 inclusive.",
                )
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode(
                "InvalidParameterValue", "NextToken must be a string if specified."
            )

        # Collect DHCP options to describe
        dhcp_options_list: List[DhcpOptions] = []

        if dhcp_options_ids is not None:
            # Validate all IDs exist
            for dopt_id in dhcp_options_ids:
                dopt = self.state.dhcp_options.get(dopt_id)
                if dopt is None:
                    raise ErrorCode(
                        "InvalidDhcpOptionID.NotFound",
                        f"DHCP options set {dopt_id} does not exist.",
                    )
                dhcp_options_list.append(dopt)
        else:
            # All DHCP options
            dhcp_options_list = list(self.state.dhcp_options.values())

        # Apply filters
        def matches_filter(dopt: DhcpOptions, filter_: Dict[str, Any]) -> bool:
            name = filter_["Name"]
            values = filter_["Values"]
            if name == "dhcp-options-id":
                # Match dhcp_options_id against any value
                return any(dopt.dhcp_options_id == v for v in values)
            elif name == "key":
                # Match any dhcpConfigurationSet key against any value
                keys = [dc.key for dc in dopt.dhcp_configuration_set if dc.key]
                return any(v in keys for v in values)
            elif name == "value":
                # Match any dhcpConfigurationSet valueSet values against any value
                all_values = []
                for dc in dopt.dhcp_configuration_set:
                    all_values.extend(av.Value for av in dc.valueSet)
                # Support wildcard * in filter values (AWS supports it)
                for v in values:
                    if "*" in v:
                        # Convert wildcard to regex
                        import re

                        pattern = "^" + re.escape(v).replace("\\*", ".*") + "$"
                        if any(re.match(pattern, val) for val in all_values):
                            return True
                    else:
                        if v in all_values:
                            return True
                return False
            elif name == "owner-id":
                return any(dopt.owner_id == v for v in values)
            elif name.startswith("tag:"):
                # tag:key = value
                tag_key = name[4:]
                for tag in dopt.tag_set:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False
            elif name == "tag-key":
                # Match tag keys
                tag_keys = [tag.Key for tag in dopt.tag_set]
                return any(v in tag_keys for v in values)
            else:
                # Unknown filter name, no match
                return False

        # Filter dhcp_options_list by all filters (AND logic)
        for f in filters:
            dhcp_options_list = [d for d in dhcp_options_list if matches_filter(d, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode(
                    "InvalidParameterValue", "NextToken is invalid or malformed."
                )
            if start_index < 0 or start_index > len(dhcp_options_list):
                raise ErrorCode(
                    "InvalidParameterValue", "NextToken is invalid or out of range."
                )
        end_index = len(dhcp_options_list)
        if max_results is not None:
            end_index = min(start_index + max_results, len(dhcp_options_list))

        page = dhcp_options_list[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(dhcp_options_list) else None

        return {
            "requestId": self.generate_request_id(),
            "dhcpOptionsSet": [dopt.to_dict() for dopt in page],
            "nextToken": new_next_token,
        }

    def associate_dhcp_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if "DryRun" in params:
            dry_run = params["DryRun"]
            if not isinstance(dry_run, bool):
                raise ErrorCode(
                    "InvalidParameterValue", "DryRun must be a boolean if specified."
                )
            # DryRun logic placeholder

        dhcp_options_id = params.get("DhcpOptionsId")
        vpc_id = params.get("VpcId")

        if not vpc_id or not isinstance(vpc_id, str):
            raise ErrorCode(
                "MissingParameter", "VpcId parameter is required and must be a string."
            )
        if dhcp_options_id is None or not isinstance(dhcp_options_id, str):
            raise ErrorCode(
                "MissingParameter", "DhcpOptionsId parameter is required and must be a string."
            )

        # Validate VPC existence
        vpc = self.state.get_resource(vpc_id)
        if vpc is None:
            raise ErrorCode(
                "InvalidVpcID.NotFound", f"VPC {vpc_id} does not exist."
            )

        # Validate DHCP options id
        if dhcp_options_id != "default":
            dhcp_options = self.state.dhcp_options.get(dhcp_options_id)
            if dhcp_options is None:
                raise ErrorCode(
                    "InvalidDhcpOptionID.NotFound",
                    f"DHCP options set {dhcp_options_id} does not exist.",
                )
        else:
            # "default" means disassociate DHCP options from VPC (use default)
            dhcp_options = None

        # Associate DHCP options with VPC
        # We assume VPC object has attribute dhcp_options_id, if not, add it
        setattr(vpc, "dhcp_options_id", dhcp_options_id if dhcp_options_id != "default" else "default")

        return {"requestId": self.generate_request_id(), "return": True}

from emulator_core.gateway.base import BaseGateway

class DHCPoptionsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateDhcpOptions", self.associate_dhcp_options)
        self.register_action("CreateDhcpOptions", self.create_dhcp_options)
        self.register_action("DeleteDhcpOptions", self.delete_dhcp_options)
        self.register_action("DescribeDhcpOptions", self.describe_dhcp_options)

    def associate_dhcp_options(self, params):
        return self.backend.associate_dhcp_options(params)

    def create_dhcp_options(self, params):
        return self.backend.create_dhcp_options(params)

    def delete_dhcp_options(self, params):
        return self.backend.delete_dhcp_options(params)

    def describe_dhcp_options(self, params):
        return self.backend.describe_dhcp_options(params)
