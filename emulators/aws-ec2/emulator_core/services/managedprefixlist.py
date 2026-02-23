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
class ManagedPrefixList:
    address_family: str = ""
    ipam_prefix_list_resolver_sync_enabled: bool = False
    ipam_prefix_list_resolver_target_id: str = ""
    max_entries: int = 0
    owner_id: str = ""
    prefix_list_arn: str = ""
    prefix_list_id: str = ""
    prefix_list_name: str = ""
    state: str = ""
    state_message: str = ""
    tag_set: List[Any] = field(default_factory=list)
    version: int = 0

    entries: List[Dict[str, Any]] = field(default_factory=list)
    entries_by_version: Dict[int, List[Dict[str, Any]]] = field(default_factory=dict)
    associations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "addressFamily": self.address_family,
            "ipamPrefixListResolverSyncEnabled": self.ipam_prefix_list_resolver_sync_enabled,
            "ipamPrefixListResolverTargetId": self.ipam_prefix_list_resolver_target_id,
            "maxEntries": self.max_entries,
            "ownerId": self.owner_id,
            "prefixListArn": self.prefix_list_arn,
            "prefixListId": self.prefix_list_id,
            "prefixListName": self.prefix_list_name,
            "state": self.state,
            "stateMessage": self.state_message,
            "tagSet": self.tag_set,
            "version": self.version,
        }

class ManagedPrefixList_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.managed_prefix_lists  # alias to shared store

    def _get_prefix_list_or_error(self, prefix_list_id: Optional[str]):
        if not prefix_list_id:
            return create_error_response("MissingParameter", "The request must contain the parameter PrefixListId")
        prefix_list = self.resources.get(prefix_list_id)
        if not prefix_list:
            return create_error_response("InvalidPrefixListId.NotFound", f"The prefix list '{prefix_list_id}' does not exist.")
        return prefix_list

    def _normalize_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for entry in entries or []:
            cidr = entry.get("Cidr") or entry.get("cidr")
            if not cidr:
                continue
            normalized_entry = {"Cidr": cidr}
            description = entry.get("Description") or entry.get("description")
            if description is not None:
                normalized_entry["Description"] = description
            normalized.append(normalized_entry)
        return normalized

    def CreateManagedPrefixList(self, params: Dict[str, Any]):
        """Creates a managed prefix list. You can specify entries for the prefix list. 
            Each entry consists of a CIDR block and an optional description."""

        if not params.get("AddressFamily"):
            return create_error_response("MissingParameter", "Missing required parameter: AddressFamily")
        if params.get("MaxEntries") is None:
            return create_error_response("MissingParameter", "Missing required parameter: MaxEntries")
        if not params.get("PrefixListName"):
            return create_error_response("MissingParameter", "Missing required parameter: PrefixListName")

        entries = self._normalize_entries(params.get("Entry.N", []) or [])
        max_entries = int(params.get("MaxEntries") or 0)
        if max_entries and len(entries) > max_entries:
            return create_error_response("InvalidParameterValue", "Number of entries exceeds MaxEntries")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        prefix_list_id = self._generate_id("pl")
        resource = ManagedPrefixList(
            address_family=params.get("AddressFamily") or "",
            max_entries=max_entries,
            owner_id="",
            prefix_list_arn="",
            prefix_list_id=prefix_list_id,
            prefix_list_name=params.get("PrefixListName") or "",
            state="create-complete",
            state_message="",
            tag_set=tag_set,
            version=1,
            entries=entries,
            entries_by_version={1: list(entries)},
        )
        self.resources[prefix_list_id] = resource

        return {
            'prefixList': resource.to_dict(),
            }

    def DeleteManagedPrefixList(self, params: Dict[str, Any]):
        """Deletes the specified managed prefix list. You must first remove all references to the prefix list in your resources."""

        prefix_list = self._get_prefix_list_or_error(params.get("PrefixListId"))
        if is_error_response(prefix_list):
            return prefix_list

        if prefix_list.associations:
            return create_error_response("DependencyViolation", "The prefix list has associations and cannot be deleted")

        del self.resources[prefix_list.prefix_list_id]

        return {
            'prefixList': prefix_list.to_dict(),
            }

    def DescribeManagedPrefixLists(self, params: Dict[str, Any]):
        """Describes your managed prefix lists and any AWS-managed prefix lists. To view the entries for your prefix list, useGetManagedPrefixListEntries."""

        prefix_list_ids = params.get("PrefixListId.N", []) or []
        if prefix_list_ids:
            for prefix_list_id in prefix_list_ids:
                if prefix_list_id not in self.resources:
                    return create_error_response("InvalidPrefixListId.NotFound", f"The prefix list '{prefix_list_id}' does not exist.")
            resources = [self.resources[prefix_list_id] for prefix_list_id in prefix_list_ids]
        else:
            resources = list(self.resources.values())

        filtered = apply_filters(resources, params.get("Filter.N", []) or [])
        return {
            'nextToken': None,
            'prefixListSet': [resource.to_dict() for resource in filtered],
            }

    def DescribePrefixLists(self, params: Dict[str, Any]):
        """Describes available AWS services in a prefix list format, which includes the prefix list
            name and prefix list ID of the service and the IP address range for the service. We recommend that you useDescribeManagedPrefixListsinstead."""

        prefix_list_ids = params.get("PrefixListId.N", []) or []
        if prefix_list_ids:
            for prefix_list_id in prefix_list_ids:
                if prefix_list_id not in self.resources:
                    return create_error_response("InvalidPrefixListId.NotFound", f"The prefix list '{prefix_list_id}' does not exist.")
            resources = [self.resources[prefix_list_id] for prefix_list_id in prefix_list_ids]
        else:
            resources = list(self.resources.values())

        filtered = apply_filters(resources, params.get("Filter.N", []) or [])
        prefix_list_set = []
        for resource in filtered:
            cidr_set = [{"cidr": entry.get("Cidr")} for entry in resource.entries]
            prefix_list_set.append({
                "cidrSet": cidr_set,
                "prefixListId": resource.prefix_list_id,
                "prefixListName": resource.prefix_list_name,
            })

        return {
            'nextToken': None,
            'prefixListSet': prefix_list_set,
            }

    def GetManagedPrefixListAssociations(self, params: Dict[str, Any]):
        """Gets information about the resources that are associated with the specified managed prefix list."""

        prefix_list = self._get_prefix_list_or_error(params.get("PrefixListId"))
        if is_error_response(prefix_list):
            return prefix_list

        return {
            'nextToken': None,
            'prefixListAssociationSet': list(prefix_list.associations),
            }

    def GetManagedPrefixListEntries(self, params: Dict[str, Any]):
        """Gets information about the entries for a specified managed prefix list."""

        prefix_list = self._get_prefix_list_or_error(params.get("PrefixListId"))
        if is_error_response(prefix_list):
            return prefix_list

        target_version = params.get("TargetVersion")
        if target_version is not None:
            entries = prefix_list.entries_by_version.get(int(target_version))
            if entries is None:
                return create_error_response("InvalidParameterValue", f"Target version '{target_version}' does not exist")
        else:
            entries = prefix_list.entries

        entry_set = []
        for entry in entries or []:
            entry_set.append({
                "cidr": entry.get("Cidr"),
                "description": entry.get("Description") or "",
            })

        return {
            'entrySet': entry_set,
            'nextToken': None,
            }

    def ModifyManagedPrefixList(self, params: Dict[str, Any]):
        """Modifies the specified managed prefix list. Adding or removing entries in a prefix list creates a new version of the prefix list.
            Changing the name of the prefix list does not affect the version. If you specify a current version number that does not match the true current version
       """

        prefix_list = self._get_prefix_list_or_error(params.get("PrefixListId"))
        if is_error_response(prefix_list):
            return prefix_list

        current_version = params.get("CurrentVersion")
        if current_version is not None and int(current_version) != prefix_list.version:
            return create_error_response("InvalidParameterValue", "CurrentVersion does not match")

        if params.get("PrefixListName"):
            prefix_list.prefix_list_name = params.get("PrefixListName") or prefix_list.prefix_list_name

        if params.get("MaxEntries") is not None:
            max_entries = int(params.get("MaxEntries") or 0)
            if max_entries and len(prefix_list.entries) > max_entries:
                return create_error_response("InvalidParameterValue", "MaxEntries cannot be less than existing entries")
            prefix_list.max_entries = max_entries

        if params.get("IpamPrefixListResolverSyncEnabled") is not None:
            prefix_list.ipam_prefix_list_resolver_sync_enabled = str2bool(params.get("IpamPrefixListResolverSyncEnabled"))

        add_entries = self._normalize_entries(params.get("AddEntry.N", []) or [])
        remove_entries = params.get("RemoveEntry.N", []) or []
        remove_cidrs = {entry.get("Cidr") or entry.get("cidr") for entry in remove_entries if entry.get("Cidr") or entry.get("cidr")}

        entries_by_cidr = {entry.get("Cidr"): dict(entry) for entry in prefix_list.entries}
        changed = False

        for entry in add_entries:
            cidr = entry.get("Cidr")
            if cidr:
                if entries_by_cidr.get(cidr) != entry:
                    changed = True
                entries_by_cidr[cidr] = entry

        for cidr in remove_cidrs:
            if cidr in entries_by_cidr:
                changed = True
                entries_by_cidr.pop(cidr, None)

        updated_entries = list(entries_by_cidr.values())
        if prefix_list.max_entries and len(updated_entries) > prefix_list.max_entries:
            return create_error_response("InvalidParameterValue", "Number of entries exceeds MaxEntries")

        if changed:
            prefix_list.entries = updated_entries
            prefix_list.version += 1
            prefix_list.entries_by_version[prefix_list.version] = list(updated_entries)

        return {
            'prefixList': prefix_list.to_dict(),
            }

    def RestoreManagedPrefixListVersion(self, params: Dict[str, Any]):
        """Restores the entries from a previous version of a managed prefix list to a new version of the prefix list."""

        if params.get("CurrentVersion") is None:
            return create_error_response("MissingParameter", "Missing required parameter: CurrentVersion")
        if not params.get("PrefixListId"):
            return create_error_response("MissingParameter", "Missing required parameter: PrefixListId")
        if params.get("PreviousVersion") is None:
            return create_error_response("MissingParameter", "Missing required parameter: PreviousVersion")

        prefix_list = self._get_prefix_list_or_error(params.get("PrefixListId"))
        if is_error_response(prefix_list):
            return prefix_list

        current_version = int(params.get("CurrentVersion"))
        previous_version = int(params.get("PreviousVersion"))
        if current_version != prefix_list.version:
            return create_error_response("InvalidParameterValue", "CurrentVersion does not match")

        previous_entries = prefix_list.entries_by_version.get(previous_version)
        if previous_entries is None:
            return create_error_response("InvalidParameterValue", "PreviousVersion does not exist")

        if prefix_list.max_entries and len(previous_entries) > prefix_list.max_entries:
            return create_error_response("InvalidParameterValue", "Number of entries exceeds MaxEntries")

        prefix_list.entries = list(previous_entries)
        prefix_list.version += 1
        prefix_list.entries_by_version[prefix_list.version] = list(previous_entries)

        return {
            'prefixList': prefix_list.to_dict(),
            }

    def _generate_id(self, prefix: str = 'ipam') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class managedprefixlist_RequestParser:
    @staticmethod
    def parse_create_managed_prefix_list_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddressFamily": get_scalar(md, "AddressFamily"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Entry.N": get_indexed_list(md, "Entry"),
            "MaxEntries": get_int(md, "MaxEntries"),
            "PrefixListName": get_scalar(md, "PrefixListName"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_managed_prefix_list_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PrefixListId": get_scalar(md, "PrefixListId"),
        }

    @staticmethod
    def parse_describe_managed_prefix_lists_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PrefixListId.N": get_indexed_list(md, "PrefixListId"),
        }

    @staticmethod
    def parse_describe_prefix_lists_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PrefixListId.N": get_indexed_list(md, "PrefixListId"),
        }

    @staticmethod
    def parse_get_managed_prefix_list_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PrefixListId": get_scalar(md, "PrefixListId"),
        }

    @staticmethod
    def parse_get_managed_prefix_list_entries_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PrefixListId": get_scalar(md, "PrefixListId"),
            "TargetVersion": get_int(md, "TargetVersion"),
        }

    @staticmethod
    def parse_modify_managed_prefix_list_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddEntry.N": get_indexed_list(md, "AddEntry"),
            "CurrentVersion": get_int(md, "CurrentVersion"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPrefixListResolverSyncEnabled": get_scalar(md, "IpamPrefixListResolverSyncEnabled"),
            "MaxEntries": get_int(md, "MaxEntries"),
            "PrefixListId": get_scalar(md, "PrefixListId"),
            "PrefixListName": get_scalar(md, "PrefixListName"),
            "RemoveEntry.N": get_indexed_list(md, "RemoveEntry"),
        }

    @staticmethod
    def parse_restore_managed_prefix_list_version_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CurrentVersion": get_int(md, "CurrentVersion"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PrefixListId": get_scalar(md, "PrefixListId"),
            "PreviousVersion": get_int(md, "PreviousVersion"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateManagedPrefixList": managedprefixlist_RequestParser.parse_create_managed_prefix_list_request,
            "DeleteManagedPrefixList": managedprefixlist_RequestParser.parse_delete_managed_prefix_list_request,
            "DescribeManagedPrefixLists": managedprefixlist_RequestParser.parse_describe_managed_prefix_lists_request,
            "DescribePrefixLists": managedprefixlist_RequestParser.parse_describe_prefix_lists_request,
            "GetManagedPrefixListAssociations": managedprefixlist_RequestParser.parse_get_managed_prefix_list_associations_request,
            "GetManagedPrefixListEntries": managedprefixlist_RequestParser.parse_get_managed_prefix_list_entries_request,
            "ModifyManagedPrefixList": managedprefixlist_RequestParser.parse_modify_managed_prefix_list_request,
            "RestoreManagedPrefixListVersion": managedprefixlist_RequestParser.parse_restore_managed_prefix_list_version_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class managedprefixlist_ResponseSerializer:
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
                xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_managed_prefix_list_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateManagedPrefixListResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize prefixList
        _prefixList_key = None
        if "prefixList" in data:
            _prefixList_key = "prefixList"
        elif "PrefixList" in data:
            _prefixList_key = "PrefixList"
        if _prefixList_key:
            param_data = data[_prefixList_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<prefixList>')
            xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</prefixList>')
        xml_parts.append(f'</CreateManagedPrefixListResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_managed_prefix_list_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteManagedPrefixListResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize prefixList
        _prefixList_key = None
        if "prefixList" in data:
            _prefixList_key = "prefixList"
        elif "PrefixList" in data:
            _prefixList_key = "PrefixList"
        if _prefixList_key:
            param_data = data[_prefixList_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<prefixList>')
            xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</prefixList>')
        xml_parts.append(f'</DeleteManagedPrefixListResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_managed_prefix_lists_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeManagedPrefixListsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize prefixListSet
        _prefixListSet_key = None
        if "prefixListSet" in data:
            _prefixListSet_key = "prefixListSet"
        elif "PrefixListSet" in data:
            _prefixListSet_key = "PrefixListSet"
        elif "PrefixLists" in data:
            _prefixListSet_key = "PrefixLists"
        if _prefixListSet_key:
            param_data = data[_prefixListSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<prefixListSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</prefixListSet>')
            else:
                xml_parts.append(f'{indent_str}<prefixListSet/>')
        xml_parts.append(f'</DescribeManagedPrefixListsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_prefix_lists_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribePrefixListsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize prefixListSet
        _prefixListSet_key = None
        if "prefixListSet" in data:
            _prefixListSet_key = "prefixListSet"
        elif "PrefixListSet" in data:
            _prefixListSet_key = "PrefixListSet"
        elif "PrefixLists" in data:
            _prefixListSet_key = "PrefixLists"
        if _prefixListSet_key:
            param_data = data[_prefixListSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<prefixListSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</prefixListSet>')
            else:
                xml_parts.append(f'{indent_str}<prefixListSet/>')
        xml_parts.append(f'</DescribePrefixListsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_managed_prefix_list_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetManagedPrefixListAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize prefixListAssociationSet
        _prefixListAssociationSet_key = None
        if "prefixListAssociationSet" in data:
            _prefixListAssociationSet_key = "prefixListAssociationSet"
        elif "PrefixListAssociationSet" in data:
            _prefixListAssociationSet_key = "PrefixListAssociationSet"
        elif "PrefixListAssociations" in data:
            _prefixListAssociationSet_key = "PrefixListAssociations"
        if _prefixListAssociationSet_key:
            param_data = data[_prefixListAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<prefixListAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</prefixListAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<prefixListAssociationSet/>')
        xml_parts.append(f'</GetManagedPrefixListAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_managed_prefix_list_entries_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetManagedPrefixListEntriesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize entrySet
        _entrySet_key = None
        if "entrySet" in data:
            _entrySet_key = "entrySet"
        elif "EntrySet" in data:
            _entrySet_key = "EntrySet"
        elif "Entrys" in data:
            _entrySet_key = "Entrys"
        if _entrySet_key:
            param_data = data[_entrySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<entrySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</entrySet>')
            else:
                xml_parts.append(f'{indent_str}<entrySet/>')
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
        xml_parts.append(f'</GetManagedPrefixListEntriesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_managed_prefix_list_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyManagedPrefixListResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize prefixList
        _prefixList_key = None
        if "prefixList" in data:
            _prefixList_key = "prefixList"
        elif "PrefixList" in data:
            _prefixList_key = "PrefixList"
        if _prefixList_key:
            param_data = data[_prefixList_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<prefixList>')
            xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</prefixList>')
        xml_parts.append(f'</ModifyManagedPrefixListResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_restore_managed_prefix_list_version_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RestoreManagedPrefixListVersionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize prefixList
        _prefixList_key = None
        if "prefixList" in data:
            _prefixList_key = "prefixList"
        elif "PrefixList" in data:
            _prefixList_key = "PrefixList"
        if _prefixList_key:
            param_data = data[_prefixList_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<prefixList>')
            xml_parts.extend(managedprefixlist_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</prefixList>')
        xml_parts.append(f'</RestoreManagedPrefixListVersionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateManagedPrefixList": managedprefixlist_ResponseSerializer.serialize_create_managed_prefix_list_response,
            "DeleteManagedPrefixList": managedprefixlist_ResponseSerializer.serialize_delete_managed_prefix_list_response,
            "DescribeManagedPrefixLists": managedprefixlist_ResponseSerializer.serialize_describe_managed_prefix_lists_response,
            "DescribePrefixLists": managedprefixlist_ResponseSerializer.serialize_describe_prefix_lists_response,
            "GetManagedPrefixListAssociations": managedprefixlist_ResponseSerializer.serialize_get_managed_prefix_list_associations_response,
            "GetManagedPrefixListEntries": managedprefixlist_ResponseSerializer.serialize_get_managed_prefix_list_entries_response,
            "ModifyManagedPrefixList": managedprefixlist_ResponseSerializer.serialize_modify_managed_prefix_list_response,
            "RestoreManagedPrefixListVersion": managedprefixlist_ResponseSerializer.serialize_restore_managed_prefix_list_version_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

