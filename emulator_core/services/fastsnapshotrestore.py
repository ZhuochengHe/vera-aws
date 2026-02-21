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
class FastSnapshotRestore:
    availability_zone: str = ""
    availability_zone_id: str = ""
    disabled_time: str = ""
    disabling_time: str = ""
    enabled_time: str = ""
    enabling_time: str = ""
    optimizing_time: str = ""
    owner_alias: str = ""
    owner_id: str = ""
    snapshot_id: str = ""
    state: str = ""
    state_transition_reason: str = ""

    # Internal dependency tracking — not in API response
    capacity_reservation_ids: List[str] = field(default_factory=list)  # tracks CapacityReservation children
    reserved_instance_ids: List[str] = field(default_factory=list)  # tracks ReservedInstance children
    subnet_ids: List[str] = field(default_factory=list)  # tracks Subnet children
    volume_ids: List[str] = field(default_factory=list)  # tracks Volume children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "disabledTime": self.disabled_time,
            "disablingTime": self.disabling_time,
            "enabledTime": self.enabled_time,
            "enablingTime": self.enabling_time,
            "optimizingTime": self.optimizing_time,
            "ownerAlias": self.owner_alias,
            "ownerId": self.owner_id,
            "snapshotId": self.snapshot_id,
            "state": self.state,
            "stateTransitionReason": self.state_transition_reason,
        }

class FastSnapshotRestore_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.fast_snapshot_restores  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.snapshots.get(params['snapshot_id']).fast_snapshot_restore_ids.append(new_id)
    #   Delete: self.state.snapshots.get(resource.snapshot_id).fast_snapshot_restore_ids.remove(resource_id)

    def _utc_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _find_by_snapshot_zone(self, snapshot_id: str, availability_zone: str = "", availability_zone_id: str = "") -> Optional[str]:
        if not snapshot_id:
            return None
        for resource_id, resource in self.resources.items():
            if resource.snapshot_id != snapshot_id:
                continue
            if availability_zone and resource.availability_zone != availability_zone:
                continue
            if availability_zone_id and resource.availability_zone_id != availability_zone_id:
                continue
            return resource_id
        return None

    def _validate_snapshot_ids(self, snapshot_ids: List[str]) -> Optional[Dict[str, Any]]:
        for snapshot_id in snapshot_ids:
            if not snapshot_id:
                continue
            snapshot = self.state.snapshots.get(snapshot_id)
            if not snapshot:
                return create_error_response("InvalidSnapshotID.NotFound", f"The ID '{snapshot_id}' does not exist")
        return None

    def DescribeFastSnapshotRestores(self, params: Dict[str, Any]):
        """Describes the state of fast snapshot restores for your snapshots."""

        filters = params.get("Filter.N", [])
        resources = apply_filters(list(self.resources.values()), filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        page = resources[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(resources):
            new_next_token = str(start_index + max_results)

        return {
            'fastSnapshotRestoreSet': [resource.to_dict() for resource in page],
            'nextToken': new_next_token,
            }

    def DisableFastSnapshotRestores(self, params: Dict[str, Any]):
        """Disables fast snapshot restores for the specified snapshots in the specified Availability Zones."""

        snapshot_ids = params.get("SourceSnapshotId.N", [])
        if not snapshot_ids or any(not snapshot_id for snapshot_id in snapshot_ids):
            return create_error_response("MissingParameter", "SourceSnapshotId.N is required")

        error_response = self._validate_snapshot_ids(snapshot_ids)
        if error_response:
            return error_response

        availability_zones = params.get("AvailabilityZone.N", []) or []
        availability_zone_ids = params.get("AvailabilityZoneId.N", []) or []

        successful: List[Dict[str, Any]] = []
        unsuccessful: List[Dict[str, Any]] = []

        for snapshot_id in snapshot_ids:
            targets: List[Dict[str, str]] = []
            if availability_zones or availability_zone_ids:
                max_len = max(len(availability_zones), len(availability_zone_ids))
                for index in range(max_len):
                    targets.append({
                        "availability_zone": availability_zones[index] if index < len(availability_zones) else "",
                        "availability_zone_id": availability_zone_ids[index] if index < len(availability_zone_ids) else "",
                    })
            else:
                for resource in self.resources.values():
                    if resource.snapshot_id == snapshot_id:
                        targets.append({
                            "availability_zone": resource.availability_zone,
                            "availability_zone_id": resource.availability_zone_id,
                        })
                if not targets:
                    targets.append({"availability_zone": "", "availability_zone_id": ""})

            for target in targets:
                availability_zone = target["availability_zone"]
                availability_zone_id = target["availability_zone_id"]
                resource_id = self._find_by_snapshot_zone(snapshot_id, availability_zone, availability_zone_id)
                if resource_id:
                    resource = self.resources[resource_id]
                else:
                    resource_id = self._generate_id("availability")
                    resource = FastSnapshotRestore(
                        availability_zone=availability_zone,
                        availability_zone_id=availability_zone_id,
                        snapshot_id=snapshot_id,
                    )
                    self.resources[resource_id] = resource
                    parent = self.state.snapshots.get(snapshot_id)
                    if parent:
                        if not hasattr(parent, "fast_snapshot_restore_ids"):
                            setattr(parent, "fast_snapshot_restore_ids", [])
                        if resource_id not in parent.fast_snapshot_restore_ids:
                            parent.fast_snapshot_restore_ids.append(resource_id)

                timestamp = self._utc_timestamp()
                resource.state = "disabled"
                resource.disabling_time = timestamp
                resource.disabled_time = timestamp
                resource.state_transition_reason = "disabled"
                successful.append(resource.to_dict())

        return {
            'successful': successful,
            'unsuccessful': unsuccessful,
            }

    def EnableFastSnapshotRestores(self, params: Dict[str, Any]):
        """Enables fast snapshot restores for the specified snapshots in the specified Availability Zones. You get the full benefit of fast snapshot restores after they enter theenabledstate. To get the current state of fast snapshot restores, useDescribeFastSnapshotRestores.
      To disable fast snapshot res"""

        snapshot_ids = params.get("SourceSnapshotId.N", [])
        if not snapshot_ids or any(not snapshot_id for snapshot_id in snapshot_ids):
            return create_error_response("MissingParameter", "SourceSnapshotId.N is required")

        error_response = self._validate_snapshot_ids(snapshot_ids)
        if error_response:
            return error_response

        availability_zones = params.get("AvailabilityZone.N", []) or []
        availability_zone_ids = params.get("AvailabilityZoneId.N", []) or []

        successful: List[Dict[str, Any]] = []
        unsuccessful: List[Dict[str, Any]] = []

        for snapshot_id in snapshot_ids:
            targets: List[Dict[str, str]] = []
            if availability_zones or availability_zone_ids:
                max_len = max(len(availability_zones), len(availability_zone_ids))
                for index in range(max_len):
                    targets.append({
                        "availability_zone": availability_zones[index] if index < len(availability_zones) else "",
                        "availability_zone_id": availability_zone_ids[index] if index < len(availability_zone_ids) else "",
                    })
            else:
                for resource in self.resources.values():
                    if resource.snapshot_id == snapshot_id:
                        targets.append({
                            "availability_zone": resource.availability_zone,
                            "availability_zone_id": resource.availability_zone_id,
                        })
                if not targets:
                    targets.append({"availability_zone": "", "availability_zone_id": ""})

            for target in targets:
                availability_zone = target["availability_zone"]
                availability_zone_id = target["availability_zone_id"]
                resource_id = self._find_by_snapshot_zone(snapshot_id, availability_zone, availability_zone_id)
                if resource_id:
                    resource = self.resources[resource_id]
                else:
                    resource_id = self._generate_id("availability")
                    resource = FastSnapshotRestore(
                        availability_zone=availability_zone,
                        availability_zone_id=availability_zone_id,
                        snapshot_id=snapshot_id,
                    )
                    self.resources[resource_id] = resource
                    parent = self.state.snapshots.get(snapshot_id)
                    if parent:
                        if not hasattr(parent, "fast_snapshot_restore_ids"):
                            setattr(parent, "fast_snapshot_restore_ids", [])
                        if resource_id not in parent.fast_snapshot_restore_ids:
                            parent.fast_snapshot_restore_ids.append(resource_id)

                timestamp = self._utc_timestamp()
                resource.state = "enabled"
                resource.enabling_time = timestamp
                resource.enabled_time = timestamp
                resource.optimizing_time = timestamp
                resource.state_transition_reason = "enabled"
                successful.append(resource.to_dict())

        return {
            'successful': successful,
            'unsuccessful': unsuccessful,
            }

    def _generate_id(self, prefix: str = 'availability') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class fastsnapshotrestore_RequestParser:
    @staticmethod
    def parse_describe_fast_snapshot_restores_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disable_fast_snapshot_restores_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone.N": get_indexed_list(md, "AvailabilityZone"),
            "AvailabilityZoneId.N": get_indexed_list(md, "AvailabilityZoneId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SourceSnapshotId.N": get_indexed_list(md, "SourceSnapshotId"),
        }

    @staticmethod
    def parse_enable_fast_snapshot_restores_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone.N": get_indexed_list(md, "AvailabilityZone"),
            "AvailabilityZoneId.N": get_indexed_list(md, "AvailabilityZoneId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SourceSnapshotId.N": get_indexed_list(md, "SourceSnapshotId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeFastSnapshotRestores": fastsnapshotrestore_RequestParser.parse_describe_fast_snapshot_restores_request,
            "DisableFastSnapshotRestores": fastsnapshotrestore_RequestParser.parse_disable_fast_snapshot_restores_request,
            "EnableFastSnapshotRestores": fastsnapshotrestore_RequestParser.parse_enable_fast_snapshot_restores_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class fastsnapshotrestore_ResponseSerializer:
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
                xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_fast_snapshot_restores_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeFastSnapshotRestoresResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fastSnapshotRestoreSet
        _fastSnapshotRestoreSet_key = None
        if "fastSnapshotRestoreSet" in data:
            _fastSnapshotRestoreSet_key = "fastSnapshotRestoreSet"
        elif "FastSnapshotRestoreSet" in data:
            _fastSnapshotRestoreSet_key = "FastSnapshotRestoreSet"
        elif "FastSnapshotRestores" in data:
            _fastSnapshotRestoreSet_key = "FastSnapshotRestores"
        if _fastSnapshotRestoreSet_key:
            param_data = data[_fastSnapshotRestoreSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<fastSnapshotRestoreSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</fastSnapshotRestoreSet>')
            else:
                xml_parts.append(f'{indent_str}<fastSnapshotRestoreSet/>')
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
        xml_parts.append(f'</DescribeFastSnapshotRestoresResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disable_fast_snapshot_restores_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableFastSnapshotRestoresResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successful
        _successful_key = None
        if "successful" in data:
            _successful_key = "successful"
        elif "Successful" in data:
            _successful_key = "Successful"
        if _successful_key:
            param_data = data[_successful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</successfulSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulSet/>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</DisableFastSnapshotRestoresResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_fast_snapshot_restores_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableFastSnapshotRestoresResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successful
        _successful_key = None
        if "successful" in data:
            _successful_key = "successful"
        elif "Successful" in data:
            _successful_key = "Successful"
        if _successful_key:
            param_data = data[_successful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</successfulSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulSet/>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(fastsnapshotrestore_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</EnableFastSnapshotRestoresResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeFastSnapshotRestores": fastsnapshotrestore_ResponseSerializer.serialize_describe_fast_snapshot_restores_response,
            "DisableFastSnapshotRestores": fastsnapshotrestore_ResponseSerializer.serialize_disable_fast_snapshot_restores_response,
            "EnableFastSnapshotRestores": fastsnapshotrestore_ResponseSerializer.serialize_enable_fast_snapshot_restores_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

