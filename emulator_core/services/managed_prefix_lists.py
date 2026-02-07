from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend


class AddressFamily(str, Enum):
    IPv4 = "IPv4"
    IPv6 = "IPv6"


class ManagedPrefixListState(str, Enum):
    CREATE_IN_PROGRESS = "create-in-progress"
    CREATE_COMPLETE = "create-complete"
    CREATE_FAILED = "create-failed"
    MODIFY_IN_PROGRESS = "modify-in-progress"
    MODIFY_COMPLETE = "modify-complete"
    MODIFY_FAILED = "modify-failed"
    RESTORE_IN_PROGRESS = "restore-in-progress"
    RESTORE_COMPLETE = "restore-complete"
    RESTORE_FAILED = "restore-failed"
    DELETE_IN_PROGRESS = "delete-in-progress"
    DELETE_COMPLETE = "delete-complete"
    DELETE_FAILED = "delete-failed"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class AddPrefixListEntry:
    Cidr: str
    Description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"Cidr": self.Cidr}
        if self.Description is not None:
            d["Description"] = self.Description
        return d


@dataclass
class RemovePrefixListEntry:
    Cidr: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Cidr": self.Cidr}


@dataclass
class PrefixListEntry:
    cidr: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.cidr is not None:
            d["cidr"] = self.cidr
        if self.description is not None:
            d["description"] = self.description
        return d


@dataclass
class PrefixListAssociation:
    resourceId: Optional[str] = None
    resourceOwner: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.resourceId is not None:
            d["resourceId"] = self.resourceId
        if self.resourceOwner is not None:
            d["resourceOwner"] = self.resourceOwner
        return d


@dataclass
class ManagedPrefixList:
    addressFamily: Optional[AddressFamily] = None
    ipamPrefixListResolverSyncEnabled: Optional[bool] = None
    ipamPrefixListResolverTargetId: Optional[str] = None
    maxEntries: Optional[int] = None
    ownerId: Optional[str] = None
    prefixListArn: Optional[str] = None
    prefixListId: Optional[str] = None
    prefixListName: Optional[str] = None
    state: Optional[ManagedPrefixListState] = None
    stateMessage: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    version: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.addressFamily is not None:
            d["addressFamily"] = self.addressFamily.value
        if self.ipamPrefixListResolverSyncEnabled is not None:
            d["ipamPrefixListResolverSyncEnabled"] = self.ipamPrefixListResolverSyncEnabled
        if self.ipamPrefixListResolverTargetId is not None:
            d["ipamPrefixListResolverTargetId"] = self.ipamPrefixListResolverTargetId
        if self.maxEntries is not None:
            d["maxEntries"] = self.maxEntries
        if self.ownerId is not None:
            d["ownerId"] = self.ownerId
        if self.prefixListArn is not None:
            d["prefixListArn"] = self.prefixListArn
        if self.prefixListId is not None:
            d["prefixListId"] = self.prefixListId
        if self.prefixListName is not None:
            d["prefixListName"] = self.prefixListName
        if self.state is not None:
            d["state"] = self.state.value
        if self.stateMessage is not None:
            d["stateMessage"] = self.stateMessage
        d["tagSet"] = [tag.to_dict() for tag in self.tagSet]
        if self.version is not None:
            d["version"] = self.version
        return d


@dataclass
class PrefixList:
    cidrSet: List[str] = field(default_factory=list)
    prefixListId: Optional[str] = None
    prefixListName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["cidrSet"] = self.cidrSet
        if self.prefixListId is not None:
            d["prefixListId"] = self.prefixListId
        if self.prefixListName is not None:
            d["prefixListName"] = self.prefixListName
        return d


@dataclass
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.Name is not None:
            d["Name"] = self.Name
        d["Values"] = self.Values
        return d


class ManagedprefixlistsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.managed_prefix_lists or similar

    def create_managed_prefix_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        address_family = params.get("AddressFamily")
        if address_family not in ("IPv4", "IPv6"):
            raise ValueError("AddressFamily must be 'IPv4' or 'IPv6'")

        max_entries = params.get("MaxEntries")
        if max_entries is not None:
            try:
                max_entries = int(max_entries)
            except (ValueError, TypeError):
                raise ValueError("MaxEntries must be a positive integer")
        if not max_entries or max_entries <= 0:
            raise ValueError("MaxEntries must be a positive integer")

        prefix_list_name = params.get("PrefixListName")
        if not prefix_list_name or not isinstance(prefix_list_name, str):
            raise ValueError("PrefixListName is required and must be a string")
        if prefix_list_name.startswith("com.amazonaws"):
            raise ValueError("PrefixListName cannot start with 'com.amazonaws'")
        if len(prefix_list_name) > 255:
            raise ValueError("PrefixListName length must be up to 255 characters")

        # Optional parameters
        entries = []
        # Entries are passed as Entry.N.Cidr and Entry.N.Description
        # Collect all keys starting with "Entry."
        entry_keys = [k for k in params.keys() if k.startswith("Entry.")]
        # Extract entry indices
        entry_indices = set()
        for key in entry_keys:
            # key format: Entry.N.Cidr or Entry.N.Description
            parts = key.split(".")
            if len(parts) >= 3:
                try:
                    idx = int(parts[1])
                    entry_indices.add(idx)
                except Exception:
                    pass
        # For each index, build AddPrefixListEntry
        for idx in sorted(entry_indices):
            cidr = params.get(f"Entry.{idx}.Cidr")
            if not cidr:
                raise ValueError(f"Entry.{idx}.Cidr is required")
            description = params.get(f"Entry.{idx}.Description")
            entries.append(AddPrefixListEntry(Cidr=cidr, Description=description))

        if len(entries) > 100:
            raise ValueError("Maximum number of entries is 100")

        # TagSpecification.N
        tag_specifications = []
        tag_spec_keys = [k for k in params.keys() if k.startswith("TagSpecification.")]
        tag_spec_indices = set()
        for key in tag_spec_keys:
            parts = key.split(".")
            if len(parts) >= 2:
                try:
                    idx = int(parts[1])
                    tag_spec_indices.add(idx)
                except Exception:
                    pass
        for idx in sorted(tag_spec_indices):
            resource_type = params.get(f"TagSpecification.{idx}.ResourceType")
            # Tags are TagSpecification.N.Tags.M.Key and TagSpecification.N.Tags.M.Value
            tag_keys = [k for k in params.keys() if k.startswith(f"TagSpecification.{idx}.Tags.")]
            tag_indices = set()
            for k in tag_keys:
                parts = k.split(".")
                if len(parts) >= 4:
                    try:
                        tag_idx = int(parts[3])
                        tag_indices.add(tag_idx)
                    except Exception:
                        pass
            tags = []
            for tag_idx in sorted(tag_indices):
                key = params.get(f"TagSpecification.{idx}.Tags.{tag_idx}.Key")
                value = params.get(f"TagSpecification.{idx}.Tags.{tag_idx}.Value")
                if key is not None:
                    if key.startswith("aws:"):
                        raise ValueError("Tag keys may not begin with 'aws:'")
                    if len(key) > 127:
                        raise ValueError("Tag key length must be up to 127 characters")
                if value is not None and len(value) > 256:
                    raise ValueError("Tag value length must be up to 256 characters")
                tags.append(Tag(Key=key, Value=value))
            tag_specifications.append(TagSpecification(ResourceType=resource_type, Tags=tags))

        # Generate prefix list ID and ARN
        prefix_list_id = self.generate_unique_id(prefix="pl-")
        owner_id = self.get_owner_id()
        prefix_list_arn = f"arn:aws:ec2:region:{owner_id}:prefix-list/{prefix_list_id}"

        # Create ManagedPrefixList object
        mpl = ManagedPrefixList(
            addressFamily=AddressFamily(address_family),
            ipamPrefixListResolverSyncEnabled=None,
            ipamPrefixListResolverTargetId=None,
            maxEntries=max_entries,
            ownerId=owner_id,
            prefixListArn=prefix_list_arn,
            prefixListId=prefix_list_id,
            prefixListName=prefix_list_name,
            state=ManagedPrefixListState.CREATE_IN_PROGRESS,
            stateMessage=None,
            tagSet=[tag for spec in tag_specifications for tag in spec.Tags],
            version=1,
        )

        # Store in state
        self.state.managed_prefix_lists[prefix_list_id] = mpl
        self.state.resources[prefix_list_id] = mpl

        # Return response
        return {
            "prefixList": mpl.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_managed_prefix_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        prefix_list_id = params.get("PrefixListId")
        if not prefix_list_id:
            raise ValueError("PrefixListId is required")

        mpl = self.state.managed_prefix_lists.get(prefix_list_id)
        if not mpl:
            raise ValueError(f"ManagedPrefixList with id {prefix_list_id} not found")

        # Mark state as delete-in-progress
        mpl.state = ManagedPrefixListState.DELETE_IN_PROGRESS

        # We do not actually remove from state immediately to simulate AWS behavior
        # but for emulator, we can remove after marking state if needed.
        # Here, we keep it but mark state.

        return {
            "prefixList": mpl.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def describe_managed_prefix_lists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Optional filters
        filters = []
        filter_keys = [k for k in params.keys() if k.startswith("Filter.")]
        filter_indices = set()
        for key in filter_keys:
            parts = key.split(".")
            if len(parts) >= 2:
                try:
                    idx = int(parts[1])
                    filter_indices.add(idx)
                except Exception:
                    pass
        for idx in sorted(filter_indices):
            name = params.get(f"Filter.{idx}.Name")
            values = []
            value_keys = [k for k in params.keys() if k.startswith(f"Filter.{idx}.Value.")]
            value_indices = set()
            for vk in value_keys:
                parts = vk.split(".")
                if len(parts) >= 4:
                    try:
                        v_idx = int(parts[3])
                        value_indices.add(v_idx)
                    except Exception:
                        pass
            for v_idx in sorted(value_indices):
                val = params.get(f"Filter.{idx}.Value.{v_idx}")
                if val is not None:
                    values.append(val)
            filters.append(Filter(Name=name, Values=values))

        # Optional prefix list IDs filter
        prefix_list_ids = []
        prefix_list_id_keys = [k for k in params.keys() if k.startswith("PrefixListId.")]
        prefix_list_id_indices = set()
        for key in prefix_list_id_keys:
            parts = key.split(".")
            if len(parts) >= 2:
                try:
                    idx = int(parts[1])
                    prefix_list_id_indices.add(idx)
                except Exception:
                    pass
        for idx in sorted(prefix_list_id_indices):
            val = params.get(f"PrefixListId.{idx}")
            if val is not None:
                prefix_list_ids.append(val)

        # Filter managed prefix lists
        results = []
        for mpl in self.state.managed_prefix_lists.values():
            # Filter by prefix list IDs if provided
            if prefix_list_ids and mpl.prefixListId not in prefix_list_ids:
                continue

            # Apply filters
            match = True
            for f in filters:
                if f.Name == "owner-id":
                    if mpl.ownerId not in f.Values:
                        match = False
                        break
                elif f.Name == "prefix-list-id":
                    if mpl.prefixListId not in f.Values:
                        match = False
                        break
                elif f.Name == "prefix-list-name":
                    if mpl.prefixListName not in f.Values:
                        match = False
                        break
            if match:
                results.append(mpl)

        # Pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1 or max_results > 100:
                    max_results = 100
            except Exception:
                max_results = 100
        else:
            max_results = 100

        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page = results[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(results) else None

        return {
            "prefixListSet": [mpl.to_dict() for mpl in page],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_prefix_lists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # This API describes AWS service prefix lists (not managed prefix lists)
        # For emulator, we can return empty or some static data
        # We will support filters and pagination similarly

        # For simplicity, define some static prefix lists
        static_prefix_lists = [
            PrefixList(
                cidrSet=["54.123.456.7/19"],
                prefixListId="pl-12345678",
                prefixListName="com.amazonaws.us-west-2.s3",
            )
        ]

        # Optional filters
        filters = []
        filter_keys = [k for k in params.keys() if k.startswith("Filter.")]
        filter_indices = set()
        for key in filter_keys:
            parts = key.split(".")
            if len(parts) >= 2:
                try:
                    idx = int(parts[1])
                    filter_indices.add(idx)
                except Exception:
                    pass
        for idx in sorted(filter_indices):
            name = params.get(f"Filter.{idx}.Name")
            values = []
            value_keys = [k for k in params.keys() if k.startswith(f"Filter.{idx}.Value.")]
            value_indices = set()
            for vk in value_keys:
                parts = vk.split(".")
                if len(parts) >= 4:
                    try:
                        v_idx = int(parts[3])
                        value_indices.add(v_idx)
                    except Exception:
                        pass
            for v_idx in sorted(value_indices):
                val = params.get(f"Filter.{idx}.Value.{v_idx}")
                if val is not None:
                    values.append(val)
            filters.append(Filter(Name=name, Values=values))

        # Optional prefix list IDs filter
        prefix_list_ids = []
        prefix_list_id_keys = [k for k in params.keys() if k.startswith("PrefixListId.")]
        prefix_list_id_indices = set()
        for key in prefix_list_id_keys:
            parts = key.split(".")
            if len(parts) >= 2:
                try:
                    idx = int(parts[1])
                    prefix_list_id_indices.add(idx)
                except Exception:
                    pass
        for idx in sorted(prefix_list_id_indices):
            val = params.get(f"PrefixListId.{idx}")
            if val is not None:
                prefix_list_ids.append(val)

        # Filter static prefix lists
        results = []
        for pl in static_prefix_lists:
            if prefix_list_ids and pl.prefixListId not in prefix_list_ids:
                continue
            match = True
            for f in filters:
                if f.Name == "prefix-list-id":
                    if pl.prefixListId not in f.Values:
                        match = False
                        break
                elif f.Name == "prefix-list-name":
                    if pl.prefixListName not in f.Values:
                        match = False
                        break
            if match:
                results.append(pl)

        # Pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    max_results = 1
            except Exception:
                max_results = 1
        else:
            max_results = 1

        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page = results[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(results) else None

        return {
            "prefixListSet": [pl.to_dict() for pl in page],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def get_managed_prefix_list_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        prefix_list_id = params.get("PrefixListId")
        if not prefix_list_id:
            raise ValueError("PrefixListId is required")

        mpl = self.state.managed_prefix_lists.get(prefix_list_id)
        if not mpl:
            raise ValueError(f"ManagedPrefixList with id {prefix_list_id} not found")

        # For emulator, assume associations are stored in state.managed_prefix_list_associations dict keyed by prefix_list_id
        associations = getattr(self.state, "managed_prefix_list_associations", {}).get(prefix_list_id, [])

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5:
                    max_results = 5
                elif max_results > 255:
                    max_results = 255
            except Exception:
                max_results = 5
        else:
            max_results = 5

        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results
        page = associations[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(associations) else None

        return {
            "prefixListAssociationSet": [assoc.to_dict() for assoc in page],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def get_managed_prefix_list_entries(self, params: dict) -> dict:
        prefix_list_id = params.get("PrefixListId")
        if not prefix_list_id:
            raise ValueError("PrefixListId is required")

        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
                raise ValueError("MaxResults must be an integer between 1 and 100")

        next_token = params.get("NextToken")
        target_version = params.get("TargetVersion")

        prefix_list = self.state.managed_prefix_lists.get(prefix_list_id)
        if not prefix_list:
            raise ValueError(f"ManagedPrefixList with id {prefix_list_id} not found")

        # Determine which version to use
        version_to_use = target_version if target_version is not None else prefix_list.version
        if version_to_use is None:
            # If no version is set, default to 1
            version_to_use = 1

        # The prefix list entries are stored per version in prefix_list.entries_by_version (assumed)
        # But since the class structure is not fully detailed, we assume prefix_list has a dict attribute:
        # prefix_list.entries_by_version: Dict[int, List[PrefixListEntry]]
        # If not present, fallback to prefix_list.entries (current entries)
        entries_by_version = getattr(prefix_list, "entries_by_version", None)
        if entries_by_version and version_to_use in entries_by_version:
            entries = entries_by_version[version_to_use]
        else:
            # fallback to current entries if version not found
            entries = getattr(prefix_list, "entries", [])

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ValueError("Invalid NextToken")

        # Slice entries according to max_results
        if max_results is None:
            max_results = 100  # default max

        end_index = start_index + max_results
        paged_entries = entries[start_index:end_index]

        # Prepare next token if more entries exist
        new_next_token = str(end_index) if end_index < len(entries) else None

        # Convert entries to dict
        entry_set = [entry.to_dict() for entry in paged_entries]

        return {
            "entrySet": entry_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def modify_managed_prefix_list(self, params: dict) -> dict:
        prefix_list_id = params.get("PrefixListId")
        if not prefix_list_id:
            raise ValueError("PrefixListId is required")

        prefix_list = self.state.managed_prefix_lists.get(prefix_list_id)
        if not prefix_list:
            raise ValueError(f"ManagedPrefixList with id {prefix_list_id} not found")

        current_version = params.get("CurrentVersion")
        if current_version is not None and current_version != prefix_list.version:
            raise ValueError("CurrentVersion does not match the prefix list's current version")

        add_entries_raw = []
        remove_entries_raw = []

        # Extract AddEntry.N and RemoveEntry.N from params
        # The keys are like AddEntry.1.Cidr, AddEntry.1.Description, RemoveEntry.1.Cidr
        # We parse keys to collect entries
        for key, value in params.items():
            if key.startswith("AddEntry."):
                # Format: AddEntry.N.Field
                parts = key.split(".")
                if len(parts) == 3:
                    idx = int(parts[1]) - 1
                    field = parts[2]
                    while len(add_entries_raw) <= idx:
                        add_entries_raw.append({})
                    add_entries_raw[idx][field] = value
            elif key.startswith("RemoveEntry."):
                # Format: RemoveEntry.N.Cidr
                parts = key.split(".")
                if len(parts) == 3:
                    idx = int(parts[1]) - 1
                    field = parts[2]
                    while len(remove_entries_raw) <= idx:
                        remove_entries_raw.append({})
                    remove_entries_raw[idx][field] = value

        # Validate add entries
        add_entries = []
        for entry in add_entries_raw:
            cidr = entry.get("Cidr")
            if not cidr:
                raise ValueError("AddEntry.Cidr is required")
            description = entry.get("Description")
            add_entries.append(AddPrefixListEntry(Cidr=cidr, Description=description))

        # Validate remove entries
        remove_entries = []
        for entry in remove_entries_raw:
            cidr = entry.get("Cidr")
            if not cidr:
                raise ValueError("RemoveEntry.Cidr is required")
            remove_entries.append(RemovePrefixListEntry(Cidr=cidr))

        # Validate MaxEntries if provided
        max_entries = params.get("MaxEntries")
        if max_entries is not None:
            if not isinstance(max_entries, int) or max_entries < 1:
                raise ValueError("MaxEntries must be a positive integer")

        # Validate IpamPrefixListResolverSyncEnabled if provided
        ipam_sync_enabled = params.get("IpamPrefixListResolverSyncEnabled")
        if ipam_sync_enabled is not None and not isinstance(ipam_sync_enabled, bool):
            raise ValueError("IpamPrefixListResolverSyncEnabled must be a boolean")

        # Validate PrefixListName if provided
        prefix_list_name = params.get("PrefixListName")
        if prefix_list_name is not None and not isinstance(prefix_list_name, str):
            raise ValueError("PrefixListName must be a string")

        # Check if prefix list is IPAM managed and restrict direct CIDR modifications
        if prefix_list.ipamPrefixListResolverTargetId is not None:
            if add_entries or remove_entries:
                raise ValueError("Cannot modify entries of an IPAM managed prefix list")

        # Create new version of entries list by copying current version entries
        entries_by_version = getattr(prefix_list, "entries_by_version", None)
        if entries_by_version is None:
            # Initialize entries_by_version dict with current version entries
            entries_by_version = {prefix_list.version or 1: getattr(prefix_list, "entries", [])}
            prefix_list.entries_by_version = entries_by_version

        current_entries = entries_by_version.get(prefix_list.version, [])
        # Create a copy of current entries for modification
        new_entries = [PrefixListEntry(cidr=e.cidr, description=e.description) for e in current_entries]

        # Remove entries
        for rem_entry in remove_entries:
            new_entries = [e for e in new_entries if e.cidr != rem_entry.Cidr]

        # Add entries
        for add_entry in add_entries:
            # Check if CIDR already exists
            if any(e.cidr == add_entry.Cidr for e in new_entries):
                raise ValueError(f"Entry with CIDR {add_entry.Cidr} already exists")
            new_entries.append(PrefixListEntry(cidr=add_entry.Cidr, description=add_entry.Description))

        # Check max entries limit
        new_max_entries = max_entries if max_entries is not None else prefix_list.maxEntries
        if new_max_entries is not None and len(new_entries) > new_max_entries:
            raise ValueError("Number of entries exceeds MaxEntries")

        # Update prefix list name if provided
        if prefix_list_name is not None:
            prefix_list.prefixListName = prefix_list_name

        # Update maxEntries if provided
        if max_entries is not None:
            prefix_list.maxEntries = max_entries

        # Update IpamPrefixListResolverSyncEnabled if provided
        if ipam_sync_enabled is not None:
            prefix_list.ipamPrefixListResolverSyncEnabled = ipam_sync_enabled

        # Increment version
        new_version = (prefix_list.version or 1) + 1
        prefix_list.version = new_version

        # Save new entries under new version
        entries_by_version[new_version] = new_entries

        # Also update current entries attribute for convenience
        prefix_list.entries = new_entries

        # Update state to modify-in-progress
        prefix_list.state = ManagedPrefixListState.MODIFY_IN_PROGRESS

        return {
            "prefixList": prefix_list.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def restore_managed_prefix_list_version(self, params: dict) -> dict:
        prefix_list_id = params.get("PrefixListId")
        current_version = params.get("CurrentVersion")
        previous_version = params.get("PreviousVersion")

        if not prefix_list_id:
            raise ValueError("PrefixListId is required")
        if current_version is None:
            raise ValueError("CurrentVersion is required")
        if previous_version is None:
            raise ValueError("PreviousVersion is required")

        prefix_list = self.state.managed_prefix_lists.get(prefix_list_id)
        if not prefix_list:
            raise ValueError(f"ManagedPrefixList with id {prefix_list_id} not found")

        if current_version != prefix_list.version:
            raise ValueError("CurrentVersion does not match the prefix list's current version")

        entries_by_version = getattr(prefix_list, "entries_by_version", None)
        if entries_by_version is None or previous_version not in entries_by_version:
            raise ValueError(f"PreviousVersion {previous_version} not found")

        # Restore entries from previous version to a new version
        restored_entries = entries_by_version[previous_version]

        # Increment version
        new_version = current_version + 1
        prefix_list.version = new_version

        # Save restored entries under new version
        entries_by_version[new_version] = [PrefixListEntry(cidr=e.cidr, description=e.description) for e in restored_entries]

        # Update current entries attribute
        prefix_list.entries = entries_by_version[new_version]

        # Update state to restore-in-progress
        prefix_list.state = ManagedPrefixListState.RESTORE_IN_PROGRESS

        return {
            "prefixList": prefix_list.to_dict(),
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class ManagedprefixlistsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateManagedPrefixList", self.create_managed_prefix_list)
        self.register_action("DeleteManagedPrefixList", self.delete_managed_prefix_list)
        self.register_action("DescribeManagedPrefixLists", self.describe_managed_prefix_lists)
        self.register_action("DescribePrefixLists", self.describe_prefix_lists)
        self.register_action("GetManagedPrefixListAssociations", self.get_managed_prefix_list_associations)
        self.register_action("GetManagedPrefixListEntries", self.get_managed_prefix_list_entries)
        self.register_action("ModifyManagedPrefixList", self.modify_managed_prefix_list)
        self.register_action("RestoreManagedPrefixListVersion", self.restore_managed_prefix_list_version)

    def create_managed_prefix_list(self, params):
        return self.backend.create_managed_prefix_list(params)

    def delete_managed_prefix_list(self, params):
        return self.backend.delete_managed_prefix_list(params)

    def describe_managed_prefix_lists(self, params):
        return self.backend.describe_managed_prefix_lists(params)

    def describe_prefix_lists(self, params):
        return self.backend.describe_prefix_lists(params)

    def get_managed_prefix_list_associations(self, params):
        return self.backend.get_managed_prefix_list_associations(params)

    def get_managed_prefix_list_entries(self, params):
        return self.backend.get_managed_prefix_list_entries(params)

    def modify_managed_prefix_list(self, params):
        return self.backend.modify_managed_prefix_list(params)

    def restore_managed_prefix_list_version(self, params):
        return self.backend.restore_managed_prefix_list_version(params)
