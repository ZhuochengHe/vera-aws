from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


@dataclass
class TagDescription:
    resource_id: str
    resource_type: str
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resourceId": self.resource_id,
            "resourceType": self.resource_type,
            "key": self.key,
            "value": self.value,
        }


class TagsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.tags: Dict[str, Dict[str, str]]
        # Structure: {resource_id: {key: value, ...}, ...}
        # Initialize if not present
        if not hasattr(self.state, "tags"):
            self.state.tags = {}

    def _validate_tag_key(self, key: str) -> None:
        if not isinstance(key, str):
            raise ErrorCode("InvalidParameterValue", f"Tag key must be a string, got {type(key)}")
        if len(key) > 127:
            raise ErrorCode("InvalidParameterValue", f"Tag key '{key}' exceeds maximum length of 127 characters")
        if key.lower().startswith("aws:"):
            raise ErrorCode("InvalidParameterValue", f"Tag key '{key}' may not begin with 'aws:'")

    def _validate_tag_value(self, value: Optional[str]) -> None:
        if value is None:
            return
        if not isinstance(value, str):
            raise ErrorCode("InvalidParameterValue", f"Tag value must be a string, got {type(value)}")
        if len(value) > 256:
            raise ErrorCode("InvalidParameterValue", f"Tag value '{value}' exceeds maximum length of 256 characters")

    def _get_resource_type(self, resource_id: str) -> str:
        # Use self.state.get_resource to get resource object
        resource = self.state.get_resource(resource_id)
        if resource is None:
            raise ErrorCode("InvalidResourceID.NotFound", f"Resource ID '{resource_id}' does not exist")
        # Resource type is the class name in lowercase with dashes instead of underscores
        # But AWS uses specific resource type strings, so we try to get resource_type attribute if exists
        # Otherwise fallback to class name lower
        resource_type = getattr(resource, "resource_type", None)
        if resource_type is None:
            # fallback: convert class name from CamelCase to lowercase with dashes
            # e.g. Vpc -> vpc, Subnet -> subnet, NetworkInterface -> network-interface
            import re

            name = resource.__class__.__name__
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
            resource_type = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()
        return resource_type

    def _parse_tags(self, params: Dict[str, Any]) -> List[Dict[str, str]]:
        # Extract Tag.N.Key and Tag.N.Value from params
        tags = []
        # Find all keys starting with "Tag."
        tag_keys = [k for k in params.keys() if k.startswith("Tag.")]
        # Extract indices
        indices = set()
        for k in tag_keys:
            # Format: Tag.N.Key or Tag.N.Value
            parts = k.split(".")
            if len(parts) >= 3:
                indices.add(parts[1])
        for idx in sorted(indices, key=int):
            key_key = f"Tag.{idx}.Key"
            value_key = f"Tag.{idx}.Value"
            if key_key not in params:
                # Key is required for each tag
                raise ErrorCode("MissingParameter", f"Missing parameter {key_key}")
            key = params[key_key]
            value = params.get(value_key, "")
            if value is None:
                value = ""
            self._validate_tag_key(key)
            self._validate_tag_value(value)
            tags.append({"Key": key, "Value": value})
        return tags

    def _parse_resource_ids(self, params: Dict[str, Any]) -> List[str]:
        # Extract ResourceId.N from params
        resource_ids = []
        resource_id_keys = [k for k in params.keys() if k.startswith("ResourceId.")]
        indices = set()
        for k in resource_id_keys:
            parts = k.split(".")
            if len(parts) == 2:
                indices.add(parts[1])
        for idx in sorted(indices, key=int):
            rid_key = f"ResourceId.{idx}"
            if rid_key not in params:
                raise ErrorCode("MissingParameter", f"Missing parameter {rid_key}")
            rid = params[rid_key]
            if not isinstance(rid, str) or not rid:
                raise ErrorCode("InvalidParameterValue", f"Invalid resource ID '{rid}'")
            resource_ids.append(rid)
        if not resource_ids:
            raise ErrorCode("MissingParameter", "At least one ResourceId.N parameter is required")
        if len(resource_ids) > 1000:
            raise ErrorCode("InvalidParameterValue", "Too many resource IDs specified; maximum is 1000")
        return resource_ids

    def _parse_filters(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Extract Filter.N.Name and Filter.N.Value.M from params
        filters = []
        filter_name_keys = [k for k in params.keys() if k.startswith("Filter.")]
        indices = set()
        for k in filter_name_keys:
            parts = k.split(".")
            if len(parts) >= 3 and parts[2] == "Name":
                indices.add(parts[1])
        for idx in sorted(indices, key=int):
            name_key = f"Filter.{idx}.Name"
            if name_key not in params:
                raise ErrorCode("MissingParameter", f"Missing parameter {name_key}")
            name = params[name_key]
            # Collect values
            values = []
            value_prefix = f"Filter.{idx}.Value."
            value_keys = [k for k in params.keys() if k.startswith(value_prefix)]
            value_indices = set()
            for vk in value_keys:
                parts = vk.split(".")
                if len(parts) == 4:
                    value_indices.add(parts[3])
            for vidx in sorted(value_indices, key=int):
                vkey = f"Filter.{idx}.Value.{vidx}"
                if vkey in params:
                    values.append(params[vkey])
            filters.append({"Name": name, "Values": values})
        return filters

    def _match_filter(self, tag: TagDescription, filter_: Dict[str, Any]) -> bool:
        name = filter_["Name"]
        values = filter_["Values"]
        # If no values, treat as no match
        if not values:
            return False
        # Support filter names:
        # key, resource-id, resource-type, tag:<key>, value
        if name == "key":
            # Match tag key with any of values (case-sensitive)
            for v in values:
                if self._wildcard_match(tag.key, v):
                    return True
            return False
        elif name == "resource-id":
            for v in values:
                if self._wildcard_match(tag.resource_id, v):
                    return True
            return False
        elif name == "resource-type":
            for v in values:
                if self._wildcard_match(tag.resource_type, v):
                    return True
            return False
        elif name.startswith("tag:"):
            # name is tag:<key>
            tag_key = name[4:]
            if tag.key != tag_key:
                return False
            for v in values:
                if self._wildcard_match(tag.value, v):
                    return True
            return False
        elif name == "value":
            for v in values:
                if self._wildcard_match(tag.value, v):
                    return True
            return False
        else:
            # Unknown filter name: no match
            return False

    def _wildcard_match(self, text: str, pattern: str) -> bool:
        # Support simple wildcard matching with ? and *
        # ? matches any single character
        # * matches zero or more characters
        # Case-sensitive
        import fnmatch

        return fnmatch.fnmatchcase(text, pattern)

    def create_tags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if "DryRun" in params:
            dry_run = params["DryRun"]
            if not isinstance(dry_run, bool):
                raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")
            if dry_run:
                # Check permissions - for emulator, just raise DryRunOperation error
                raise ErrorCode("DryRunOperation", "DryRunOperation")

        resource_ids = self._parse_resource_ids(params)
        tags = self._parse_tags(params)

        # Validate resource existence
        for rid in resource_ids:
            resource = self.state.get_resource(rid)
            if resource is None:
                raise ErrorCode("InvalidResourceID.NotFound", f"Resource ID '{rid}' does not exist")

        # For each resource, add or overwrite tags
        for rid in resource_ids:
            if rid not in self.state.tags:
                self.state.tags[rid] = {}
            for tag in tags:
                key = tag["Key"]
                value = tag["Value"]
                # Overwrite or add
                self.state.tags[rid][key] = value

            # Enforce max 50 tags per resource
            if len(self.state.tags[rid]) > 50:
                raise ErrorCode(
                    "TagLimitExceeded",
                    f"Resource {rid} has more than 50 tags after adding tags",
                )

        return {"requestId": self.generate_request_id(), "return": True}

    def delete_tags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if "DryRun" in params:
            dry_run = params["DryRun"]
            if not isinstance(dry_run, bool):
                raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")
            if dry_run:
                raise ErrorCode("DryRunOperation", "DryRunOperation")

        resource_ids = self._parse_resource_ids(params)

        # Tag.N is optional
        tags = []
        try:
            tags = self._parse_tags(params)
        except ErrorCode as e:
            # If no Tag.N parameters, _parse_tags raises MissingParameter, ignore it here
            # Only raise if some Tag.N parameters are present but invalid
            tag_keys = [k for k in params.keys() if k.startswith("Tag.")]
            if tag_keys:
                raise e

        # Validate resource existence
        for rid in resource_ids:
            resource = self.state.get_resource(rid)
            if resource is None:
                raise ErrorCode("InvalidResourceID.NotFound", f"Resource ID '{rid}' does not exist")

        # For each resource, delete tags
        for rid in resource_ids:
            if rid not in self.state.tags:
                # No tags to delete
                continue
            if not tags:
                # Delete all user-defined tags (not starting with aws:)
                keys_to_delete = [k for k in self.state.tags[rid].keys() if not k.lower().startswith("aws:")]
                for k in keys_to_delete:
                    del self.state.tags[rid][k]
            else:
                # Delete specified tags
                for tag in tags:
                    key = tag["Key"]
                    value = tag["Value"]
                    if key not in self.state.tags[rid]:
                        continue
                    if value == "":
                        # Delete tag only if value is empty string
                        if self.state.tags[rid][key] == "":
                            del self.state.tags[rid][key]
                    elif value is None:
                        # Delete any tag with this key regardless of value
                        del self.state.tags[rid][key]
                    else:
                        # Delete tag only if value matches
                        if self.state.tags[rid][key] == value:
                            del self.state.tags[rid][key]

        return {"requestId": self.generate_request_id(), "return": True}

    def describe_tags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if "DryRun" in params:
            dry_run = params["DryRun"]
            if not isinstance(dry_run, bool):
                raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")
            if dry_run:
                raise ErrorCode("DryRunOperation", "DryRunOperation")

        filters = self._parse_filters(params)
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string")

        # Collect all tags as TagDescription objects
        all_tags: List[TagDescription] = []
        # self.state.tags: {resource_id: {key: value}}
        for rid, tags_dict in self.state.tags.items():
            # Validate resource existence and get resource type
            resource = self.state.get_resource(rid)
            if resource is None:
                # Skip tags for non-existent resources
                continue
            resource_type = self._get_resource_type(rid)
            for key, value in tags_dict.items():
                all_tags.append(TagDescription(rid, resource_type, key, value))

        # Filter tags by filters
        if filters:
            filtered_tags = []
            for tag in all_tags:
                # A tag must match all filters (AND)
                if all(self._match_filter(tag, f) for f in filters):
                    filtered_tags.append(tag)
            all_tags = filtered_tags

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "Invalid NextToken value")

        end_index = len(all_tags)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_tags))

        page_tags = all_tags[start_index:end_index]

        new_next_token = None
        if end_index < len(all_tags):
            new_next_token = str(end_index)

        return {
            "requestId": self.generate_request_id(),
            "tagSet": [tag.to_dict() for tag in page_tags],
            "nextToken": new_next_token,
        }

from emulator_core.gateway.base import BaseGateway

class TagsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateTags", self.create_tags)
        self.register_action("DeleteTags", self.delete_tags)
        self.register_action("DescribeTags", self.describe_tags)

    def create_tags(self, params):
        return self.backend.create_tags(params)

    def delete_tags(self, params):
        return self.backend.delete_tags(params)

    def describe_tags(self, params):
        return self.backend.describe_tags(params)
