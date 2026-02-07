from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import re

from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class PlacementGroupState(Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


class PlacementGroupStrategy(Enum):
    CLUSTER = "cluster"
    SPREAD = "spread"
    PARTITION = "partition"


class PlacementGroupSpreadLevel(Enum):
    HOST = "host"
    RACK = "rack"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class PlacementGroup:
    group_id: str
    group_name: Optional[str] = None
    strategy: Optional[PlacementGroupStrategy] = None
    state: PlacementGroupState = PlacementGroupState.PENDING
    partition_count: Optional[int] = None
    spread_level: Optional[PlacementGroupSpreadLevel] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "groupId": self.group_id,
            "groupName": self.group_name,
            "strategy": self.strategy.value if self.strategy else None,
            "state": self.state.value,
            "tagSet": [{"Key": k, "Value": v} for k, v in self.tags.items()],
        }
        if self.partition_count is not None:
            d["partitionCount"] = self.partition_count
        if self.spread_level is not None:
            d["spreadLevel"] = self.spread_level.value
        # groupArn is optional and not specified how to generate, omit for now
        return {k: v for k, v in d.items() if v is not None}


class PlacementGroupBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.placement_groups dict for storage

    def _validate_tag_specifications(self, tag_specifications: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Validate TagSpecification.N parameters and return dict of tags.
        Only tags with ResourceType == 'placement-group' are accepted.
        """
        tags: Dict[str, str] = {}
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if resource_type != "placement-group":
                # According to AWS, tags for other resource types are ignored on placement group creation
                continue
            tag_list = tag_spec.get("Tags", [])
            if not isinstance(tag_list, list):
                raise ErrorCode("InvalidParameterValue", "Tags must be a list")
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None or not isinstance(key, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Key must be a string")
                if value is not None and not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Value must be a string or None")
                # Validate constraints on tag keys and values
                if key.lower().startswith("aws:"):
                    raise ErrorCode("InvalidParameterValue", "Tag keys may not begin with aws:")
                if len(key) > 127:
                    raise ErrorCode("InvalidParameterValue", "Tag keys accept a maximum of 127 Unicode characters")
                if value is not None and len(value) > 256:
                    raise ErrorCode("InvalidParameterValue", "Tag values accept a maximum of 256 Unicode characters")
                tags[key] = value if value is not None else ""
        return tags

    def _validate_group_name(self, group_name: Optional[str]) -> None:
        if group_name is None:
            return
        if not isinstance(group_name, str):
            raise ErrorCode("InvalidParameterValue", "GroupName must be a string")
        if len(group_name) > 255:
            raise ErrorCode("InvalidParameterValue", "GroupName must be up to 255 ASCII characters")
        # AWS allows ASCII characters, but no explicit regex given, so just check ASCII
        try:
            group_name.encode("ascii")
        except UnicodeEncodeError:
            raise ErrorCode("InvalidParameterValue", "GroupName must contain only ASCII characters")

    def _validate_strategy(self, strategy: Optional[str]) -> Optional[PlacementGroupStrategy]:
        if strategy is None:
            return None
        if not isinstance(strategy, str):
            raise ErrorCode("InvalidParameterValue", "Strategy must be a string")
        try:
            return PlacementGroupStrategy(strategy)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid Strategy value: {strategy}")

    def _validate_spread_level(self, spread_level: Optional[str]) -> Optional[PlacementGroupSpreadLevel]:
        if spread_level is None:
            return None
        if not isinstance(spread_level, str):
            raise ErrorCode("InvalidParameterValue", "SpreadLevel must be a string")
        try:
            return PlacementGroupSpreadLevel(spread_level)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid SpreadLevel value: {spread_level}")

    def _validate_partition_count(self, partition_count: Optional[int], strategy: Optional[PlacementGroupStrategy]) -> Optional[int]:
        if partition_count is None:
            return None
        if not isinstance(partition_count, int):
            raise ErrorCode("InvalidParameterValue", "PartitionCount must be an integer")
        if partition_count < 1:
            raise ErrorCode("InvalidParameterValue", "PartitionCount must be at least 1")
        if strategy != PlacementGroupStrategy.PARTITION:
            raise ErrorCode("InvalidParameterCombination", "PartitionCount is valid only when Strategy is partition")
        return partition_count

    def _check_group_name_unique(self, group_name: Optional[str]) -> None:
        if group_name is None:
            return
        # GroupName must be unique within the account and region
        for pg in self.state.placement_groups.values():
            if pg.group_name == group_name and pg.state != PlacementGroupState.DELETED:
                raise ErrorCode("InvalidParameterValue", f"Placement group with name {group_name} already exists")

    def _get_placement_group_by_name(self, group_name: str) -> Optional[PlacementGroup]:
        for pg in self.state.placement_groups.values():
            if pg.group_name == group_name and pg.state != PlacementGroupState.DELETED:
                return pg
        return None

    def _get_placement_group_by_id(self, group_id: str) -> Optional[PlacementGroup]:
        pg = self.state.placement_groups.get(group_id)
        if pg and pg.state != PlacementGroupState.DELETED:
            return pg
        return None

    def _filter_placement_groups(self, filters: List[Dict[str, Any]]) -> List[PlacementGroup]:
        """
        Filters is a list of dicts with keys "Name" and "Values" (list of strings).
        Supports filters:
          - group-name
          - group-arn (not implemented, no ARN generated, so no matches)
          - spread-level (host|rack)
          - state (pending|available|deleting|deleted)
          - strategy (cluster|spread|partition)
          - tag:<key>
          - tag-key
        """
        result = []
        for pg in self.state.placement_groups.values():
            if pg.state == PlacementGroupState.DELETED:
                continue
            match_all = True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue  # ignore empty filters
                # Support wildcard * in values for group-name
                if name == "group-name":
                    # Match if any value matches group_name (case sensitive)
                    matched = False
                    for val in values:
                        if val == pg.group_name:
                            matched = True
                            break
                        # Support * wildcard at start/end or both
                        if val.startswith("*") or val.endswith("*"):
                            pattern = "^" + re.escape(val).replace("\\*", ".*") + "$"
                            if pg.group_name and re.match(pattern, pg.group_name):
                                matched = True
                                break
                    if not matched:
                        match_all = False
                        break
                elif name == "group-arn":
                    # We do not generate ARNs, so no matches
                    match_all = False
                    break
                elif name == "spread-level":
                    if pg.spread_level is None or pg.spread_level.value not in values:
                        match_all = False
                        break
                elif name == "state":
                    if pg.state.value not in values:
                        match_all = False
                        break
                elif name == "strategy":
                    if pg.strategy is None or pg.strategy.value not in values:
                        match_all = False
                        break
                elif name.startswith("tag:"):
                    tag_key = name[4:]
                    tag_val_match = False
                    for val in values:
                        if pg.tags.get(tag_key) == val:
                            tag_val_match = True
                            break
                    if not tag_val_match:
                        match_all = False
                        break
                elif name == "tag-key":
                    tag_key_match = False
                    for val in values:
                        if val in pg.tags:
                            tag_key_match = True
                            break
                    if not tag_key_match:
                        match_all = False
                        break
                else:
                    # Unknown filter name, ignore (AWS ignores unknown filters)
                    pass
            if match_all:
                result.append(pg)
        return result

    def create_placement_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        group_name = params.get("GroupName")
        self._validate_group_name(group_name)
        self._check_group_name_unique(group_name)

        strategy_str = params.get("Strategy")
        strategy = self._validate_strategy(strategy_str)

        partition_count = params.get("PartitionCount")
        if partition_count is not None:
            # AWS expects integer, but params may be string, try convert
            if isinstance(partition_count, str):
                if not partition_count.isdigit():
                    raise ErrorCode("InvalidParameterValue", "PartitionCount must be an integer")
                partition_count = int(partition_count)
        partition_count = self._validate_partition_count(partition_count, strategy)

        spread_level_str = params.get("SpreadLevel")
        spread_level = self._validate_spread_level(spread_level_str)

        # Validate SpreadLevel usage: Only Outpost placement groups can be spread across hosts
        # We do not emulate Outpost, so just validate values and allow host/rack
        # No explicit error in docs for invalid combinations, so no error here

        # Validate TagSpecification.N
        tag_specifications = params.get("TagSpecification", [])
        if not isinstance(tag_specifications, list):
            # Sometimes TagSpecification.N is passed as dict if only one, normalize to list
            if isinstance(tag_specifications, dict):
                tag_specifications = [tag_specifications]
            else:
                raise ErrorCode("InvalidParameterValue", "TagSpecification must be a list or dict")
        tags = self._validate_tag_specifications(tag_specifications)

        # Generate unique group id
        group_id = f"pg-{self.generate_unique_id()}"

        # Create PlacementGroup object
        pg = PlacementGroup(
            group_id=group_id,
            group_name=group_name,
            strategy=strategy,
            state=PlacementGroupState.AVAILABLE,
            partition_count=partition_count,
            spread_level=spread_level,
            tags=tags,
        )

        # Store in shared state dict
        self.state.placement_groups[group_id] = pg
        self.state.resources[group_id] = pg

        return {
            "placementGroup": pg.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def delete_placement_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        group_name = params.get("GroupName")
        if group_name is None:
            raise ErrorCode("MissingParameter", "GroupName is required")

        if not isinstance(group_name, str):
            raise ErrorCode("InvalidParameterValue", "GroupName must be a string")

        pg = self._get_placement_group_by_name(group_name)
        if pg is None:
            raise ErrorCode("InvalidPlacementGroup.NotFound", f"Placement group {group_name} does not exist")

        # Check if any instances are running in the placement group
        # We do not emulate instances here, so assume no instances for now
        # If instances existed, would raise error per AWS docs

        # Mark placement group as deleted
        pg.state = PlacementGroupState.DELETED

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_placement_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # GroupId.N and GroupName.N are lists of strings
        group_ids = []
        group_names = []

        # Extract GroupId.N parameters
        for key, value in params.items():
            if key.startswith("GroupId."):
                if isinstance(value, str):
                    group_ids.append(value)
                elif isinstance(value, list):
                    group_ids.extend(value)
                else:
                    raise ErrorCode("InvalidParameterValue", "GroupId.N must be string or list of strings")

        # Extract GroupName.N parameters
        for key, value in params.items():
            if key.startswith("GroupName."):
                if isinstance(value, str):
                    group_names.append(value)
                elif isinstance(value, list):
                    group_names.extend(value)
                else:
                    raise ErrorCode("InvalidParameterValue", "GroupName.N must be string or list of strings")

        # Validate that if GroupName.N is specified, all groups must be owned by account (no shared groups)
        # We do not emulate shared groups, so no error here

        # Filters: Filter.N.Name and Filter.N.Value.M
        filters: List[Dict[str, Any]] = []
        # Collect filters by index
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                # key format: Filter.N.Name or Filter.N.Value.M
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                _, filter_index_str, rest = parts[0], parts[1], parts[2]
                if filter_index_str.isdigit():
                    filter_index = int(filter_index_str)
                    if filter_index not in filter_dict:
                        filter_dict[filter_index] = {"Name": None, "Values": []}
                    if rest == "Name":
                        filter_dict[filter_index]["Name"] = value
                    elif rest.startswith("Value"):
                        # Value.M
                        if isinstance(value, list):
                            filter_dict[filter_index]["Values"].extend(value)
                        else:
                            filter_dict[filter_index]["Values"].append(value)
        # Build filters list
        for idx in sorted(filter_dict.keys()):
            f = filter_dict[idx]
            if f["Name"] is not None:
                filters.append(f)

        # If both GroupId and GroupName specified, AWS returns error
        if group_ids and group_names:
            raise ErrorCode("InvalidParameterCombination", "Cannot specify both GroupId.N and GroupName.N")

        # Collect placement groups to return
        pgs_to_return: List[PlacementGroup] = []

        if group_ids:
            # Lookup by group ids
            for gid in group_ids:
                pg = self._get_placement_group_by_id(gid)
                if pg is None:
                    raise ErrorCode("InvalidPlacementGroup.NotFound", f"Placement group {gid} does not exist")
                pgs_to_return.append(pg)
        elif group_names:
            # Lookup by group names
            for gname in group_names:
                pg = self._get_placement_group_by_name(gname)
                if pg is None:
                    raise ErrorCode("InvalidPlacementGroup.NotFound", f"Placement group {gname} does not exist")
                pgs_to_return.append(pg)
        else:
            # No group ids or names specified, return all matching filters
            if filters:
                pgs_to_return = self._filter_placement_groups(filters)
            else:
                # Return all placement groups not deleted
                pgs_to_return = [pg for pg in self.state.placement_groups.values() if pg.state != PlacementGroupState.DELETED]

        # Compose response list
        placement_group_set = [pg.to_dict() for pg in pgs_to_return]

        return {
            "placementGroupSet": placement_group_set,
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class PlacementgroupsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreatePlacementGroup", self.create_placement_group)
        self.register_action("DeletePlacementGroup", self.delete_placement_group)
        self.register_action("DescribePlacementGroups", self.describe_placement_groups)

    def create_placement_group(self, params):
        return self.backend.create_placement_group(params)

    def delete_placement_group(self, params):
        return self.backend.delete_placement_group(params)

    def describe_placement_groups(self, params):
        return self.backend.describe_placement_groups(params)
