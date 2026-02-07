from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


# Enum for FastSnapshotRestoreState
class FastSnapshotRestoreState(str, Enum):
    ENABLING = "enabling"
    OPTIMIZING = "optimizing"
    ENABLED = "enabled"
    DISABLING = "disabling"
    DISABLED = "disabled"


@dataclass
class FastSnapshotRestoreStateError:
    code: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass
class FastSnapshotRestoreStateErrorItem:
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    error: Optional[FastSnapshotRestoreStateError] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.availability_zone is not None:
            d["availabilityZone"] = self.availability_zone
        if self.availability_zone_id is not None:
            d["availabilityZoneId"] = self.availability_zone_id
        if self.error is not None:
            d["error"] = self.error.to_dict()
        return d


@dataclass
class FastSnapshotRestore:
    # Unique ID for internal use
    id: str
    snapshot_id: str
    owner_id: str
    owner_alias: Optional[str] = None  # Intended for future use
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None

    state: FastSnapshotRestoreState = FastSnapshotRestoreState.DISABLED

    # Timestamps for state transitions (all optional)
    enabling_time: Optional[datetime] = None
    optimizing_time: Optional[datetime] = None
    enabled_time: Optional[datetime] = None
    disabling_time: Optional[datetime] = None
    disabled_time: Optional[datetime] = None

    # Reason for last state transition
    state_transition_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "snapshotId": self.snapshot_id,
            "ownerId": self.owner_id,
            "state": self.state.value,
        }
        if self.owner_alias is not None:
            d["ownerAlias"] = self.owner_alias
        if self.availability_zone is not None:
            d["availabilityZone"] = self.availability_zone
        if self.availability_zone_id is not None:
            d["availabilityZoneId"] = self.availability_zone_id
        if self.disabled_time is not None:
            d["disabledTime"] = self.disabled_time.isoformat()
        if self.disabling_time is not None:
            d["disablingTime"] = self.disabling_time.isoformat()
        if self.enabled_time is not None:
            d["enabledTime"] = self.enabled_time.isoformat()
        if self.enabling_time is not None:
            d["enablingTime"] = self.enabling_time.isoformat()
        if self.optimizing_time is not None:
            d["optimizingTime"] = self.optimizing_time.isoformat()
        if self.state_transition_reason is not None:
            d["stateTransitionReason"] = self.state_transition_reason
        return d


class FastSnapshotRestoreBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.fast_snapshot_restores dict for storage

    def _validate_az_params(self, params: Dict[str, Any]) -> (List[str], List[str]):
        """
        Validate that either AvailabilityZone.N or AvailabilityZoneId.N is specified, but not both.
        Return tuple of (availability_zones, availability_zone_ids)
        """
        azs = []
        az_ids = []

        # Extract AvailabilityZone.N and AvailabilityZoneId.N arrays
        # They come as AvailabilityZone.N keys or AvailabilityZoneId.N keys
        # We collect all keys starting with these prefixes and sort by N

        az_keys = sorted(
            (k for k in params if k.startswith("AvailabilityZone.")),
            key=lambda x: int(x.split(".")[1]),
        )
        az_id_keys = sorted(
            (k for k in params if k.startswith("AvailabilityZoneId.")),
            key=lambda x: int(x.split(".")[1]),
        )

        for k in az_keys:
            val = params.get(k)
            if not isinstance(val, str) or not val:
                raise ErrorCode("InvalidParameterValue", f"Invalid value for {k}")
            azs.append(val)

        for k in az_id_keys:
            val = params.get(k)
            if not isinstance(val, str) or not val:
                raise ErrorCode("InvalidParameterValue", f"Invalid value for {k}")
            az_ids.append(val)

        if azs and az_ids:
            raise ErrorCode(
                "InvalidParameterCombination",
                "Either AvailabilityZone or AvailabilityZoneId must be specified, but not both.",
            )
        if not azs and not az_ids:
            # For Enable/Disable APIs, one of these must be specified
            # For Describe, both optional
            pass

        return azs, az_ids

    def _get_fast_snapshot_restore_key(
        self, snapshot_id: str, availability_zone: Optional[str], availability_zone_id: Optional[str]
    ) -> str:
        # Compose a unique key for the fast snapshot restore entry
        # Use snapshot_id + availability_zone or availability_zone_id
        if availability_zone is not None:
            return f"{snapshot_id}:{availability_zone}"
        if availability_zone_id is not None:
            return f"{snapshot_id}:{availability_zone_id}"
        # Should not happen if validation done
        return f"{snapshot_id}:"

    def _get_current_time(self) -> datetime:
        # Helper to get current UTC time for timestamps
        return datetime.utcnow()

    def _get_snapshot_owner_id(self, snapshot_id: str) -> str:
        # Try to get snapshot resource and return owner id
        snapshot = self.state.get_resource(snapshot_id)
        if snapshot is None:
            raise ErrorCode("InvalidSnapshot.NotFound", f"Snapshot {snapshot_id} does not exist")
        # Assume snapshot has attribute owner_id
        if not hasattr(snapshot, "owner_id"):
            # Defensive fallback
            return self.get_owner_id()
        return snapshot.owner_id

    def _filter_fast_snapshot_restores(
        self,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[FastSnapshotRestore]:
        """
        Filter fast snapshot restores by filters.
        Filters supported:
          - availability-zone
          - availability-zone-id
          - owner-id
          - snapshot-id
          - state (enabling|optimizing|enabled|disabling|disabled)
        """
        results = list(self.state.fast_snapshot_restores.values())

        if not filters:
            return results

        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            name = name.lower()
            values_set = set(values)

            if name == "availability-zone":
                results = [
                    r for r in results if r.availability_zone is not None and r.availability_zone in values_set
                ]
            elif name == "availability-zone-id":
                results = [
                    r for r in results if r.availability_zone_id is not None and r.availability_zone_id in values_set
                ]
            elif name == "owner-id":
                results = [r for r in results if r.owner_id in values_set]
            elif name == "snapshot-id":
                results = [r for r in results if r.snapshot_id in values_set]
            elif name == "state":
                # Validate states
                valid_states = {s.value for s in FastSnapshotRestoreState}
                for v in values_set:
                    if v not in valid_states:
                        raise ErrorCode("InvalidParameterValue", f"Invalid state filter value: {v}")
                results = [r for r in results if r.state.value in values_set]
            else:
                # Unknown filter name: ignore per AWS behavior
                pass

        return results

    def describe_fast_snapshot_restores(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Validate Filters param
        filters = []
        # Filters come as Filter.N.Name and Filter.N.Values.M
        # Collect filters by N
        filter_indices = set()
        for k in params:
            if k.startswith("Filter."):
                parts = k.split(".")
                if len(parts) >= 3:
                    try:
                        idx = int(parts[1])
                        filter_indices.add(idx)
                    except Exception:
                        pass
        for idx in sorted(filter_indices):
            name_key = f"Filter.{idx}.Name"
            values_prefix = f"Filter.{idx}.Values."
            name = params.get(name_key)
            if name is None:
                continue
            values = []
            # Collect all Values.M for this filter
            values_keys = [k for k in params if k.startswith(values_prefix)]
            # Sort by M
            values_keys.sort(key=lambda x: int(x.split(".")[3]))
            for vk in values_keys:
                v = params.get(vk)
                if v is not None:
                    values.append(v)
            filters.append({"Name": name, "Values": values})

        # Validate MaxResults
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 0 or max_results > 200:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 0 and 200")

        # Validate NextToken
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string")

        # DryRun check
        if dry_run:
            # Check permissions - for emulator, assume always allowed
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Filter fast snapshot restores
        filtered = self._filter_fast_snapshot_restores(filters)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index > len(filtered):
                    raise ValueError()
            except Exception:
                raise ErrorCode("InvalidNextToken", "The provided NextToken is invalid")

        end_index = len(filtered)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered))

        page = filtered[start_index:end_index]

        # Prepare response list
        fast_snapshot_restore_set = [r.to_dict() for r in page]

        # NextToken for pagination
        new_next_token = None
        if end_index < len(filtered):
            new_next_token = str(end_index)

        return {
            "fastSnapshotRestoreSet": fast_snapshot_restore_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def _validate_source_snapshot_ids(self, params: Dict[str, Any]) -> List[str]:
        # Extract SourceSnapshotId.N array
        snapshot_ids = []
        keys = [k for k in params if k.startswith("SourceSnapshotId.")]
        if not keys:
            raise ErrorCode("MissingParameter", "SourceSnapshotId.N is required")
        # Sort keys by N
        keys.sort(key=lambda x: int(x.split(".")[1]))
        for k in keys:
            val = params.get(k)
            if not isinstance(val, str) or not val:
                raise ErrorCode("InvalidParameterValue", f"Invalid value for {k}")
            snapshot_ids.append(val)
        if not snapshot_ids:
            raise ErrorCode("MissingParameter", "At least one SourceSnapshotId must be specified")
        return snapshot_ids

    def enable_fast_snapshot_restores(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        azs, az_ids = self._validate_az_params(params)
        if not azs and not az_ids:
            raise ErrorCode(
                "MissingParameter",
                "Either AvailabilityZone.N or AvailabilityZoneId.N must be specified, but not both.",
            )

        snapshot_ids = self._validate_source_snapshot_ids(params)

        if dry_run:
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        successful = []
        unsuccessful = []

        now = self._get_current_time()

        # For each snapshot and each AZ or AZ ID, enable fast snapshot restore
        for snapshot_id in snapshot_ids:
            # Validate snapshot exists and get owner id
            try:
                owner_id = self._get_snapshot_owner_id(snapshot_id)
            except ErrorCode as e:
                # Snapshot not found: all AZs fail for this snapshot
                for az in azs:
                    unsuccessful.append(
                        {
                            "snapshotId": snapshot_id,
                            "fastSnapshotRestoreStateErrorSet": [
                                {
                                    "availabilityZone": az,
                                    "error": {"code": e.code, "message": str(e)},
                                }
                            ],
                        }
                    )
                for azid in az_ids:
                    unsuccessful.append(
                        {
                            "snapshotId": snapshot_id,
                            "fastSnapshotRestoreStateErrorSet": [
                                {
                                    "availabilityZoneId": azid,
                                    "error": {"code": e.code, "message": str(e)},
                                }
                            ],
                        }
                    )
                continue

            # Determine AZ list to iterate
            az_list = azs if azs else []
            azid_list = az_ids if az_ids else []

            # Enable for AZs
            for az in az_list:
                key = self._get_fast_snapshot_restore_key(snapshot_id, az, None)
                fsr = self.state.fast_snapshot_restores.get(key)
                if fsr is None:
                    # Create new entry
                    fsr = FastSnapshotRestore(
                        id=key,
                        snapshot_id=snapshot_id,
                        owner_id=owner_id,
                        availability_zone=az,
                        state=FastSnapshotRestoreState.ENABLING,
                        enabling_time=now,
                        state_transition_reason="Client.UserInitiated",
                    )
                    self.state.fast_snapshot_restores[key] = fsr
                    successful.append(fsr.to_dict())
                else:
                    # Already exists, check state
                    if fsr.state in (
                        FastSnapshotRestoreState.ENABLED,
                        FastSnapshotRestoreState.ENABLING,
                        FastSnapshotRestoreState.OPTIMIZING,
                    ):
                        # Already enabled or enabling, success
                        successful.append(fsr.to_dict())
                    elif fsr.state in (
                        FastSnapshotRestoreState.DISABLING,
                        FastSnapshotRestoreState.DISABLED,
                    ):
                        # Transition to enabling
                        fsr.state = FastSnapshotRestoreState.ENABLING
                        fsr.enabling_time = now
                        fsr.state_transition_reason = "Client.UserInitiated"
                        # Clear disabling/disabling times
                        fsr.disabling_time = None
                        fsr.disabled_time = None
                        successful.append(fsr.to_dict())
                    else:
                        # Unknown state, treat as error
                        unsuccessful.append(
                            {
                                "snapshotId": snapshot_id,
                                "fastSnapshotRestoreStateErrorSet": [
                                    {
                                        "availabilityZone": az,
                                        "error": {
                                            "code": "InvalidState",
                                            "message": f"Cannot enable fast snapshot restore in state {fsr.state.value}",
                                        },
                                    }
                                ],
                            }
                        )

            # Enable for AZ IDs
            for azid in azid_list:
                key = self._get_fast_snapshot_restore_key(snapshot_id, None, azid)
                fsr = self.state.fast_snapshot_restores.get(key)
                if fsr is None:
                    fsr = FastSnapshotRestore(
                        id=key,
                        snapshot_id=snapshot_id,
                        owner_id=owner_id,
                        availability_zone_id=azid,
                        state=FastSnapshotRestoreState.ENABLING,
                        enabling_time=now,
                        state_transition_reason="Client.UserInitiated",
                    )
                    self.state.fast_snapshot_restores[key] = fsr
                    successful.append(fsr.to_dict())
                else:
                    if fsr.state in (
                        FastSnapshotRestoreState.ENABLED,
                        FastSnapshotRestoreState.ENABLING,
                        FastSnapshotRestoreState.OPTIMIZING,
                    ):
                        successful.append(fsr.to_dict())
                    elif fsr.state in (
                        FastSnapshotRestoreState.DISABLING,
                        FastSnapshotRestoreState.DISABLED,
                    ):
                        fsr.state = FastSnapshotRestoreState.ENABLING
                        fsr.enabling_time = now
                        fsr.state_transition_reason = "Client.UserInitiated"
                        fsr.disabling_time = None
                        fsr.disabled_time = None
                        successful.append(fsr.to_dict())
                    else:
                        unsuccessful.append(
                            {
                                "snapshotId": snapshot_id,
                                "fastSnapshotRestoreStateErrorSet": [
                                    {
                                        "availabilityZoneId": azid,
                                        "error": {
                                            "code": "InvalidState",
                                            "message": f"Cannot enable fast snapshot restore in state {fsr.state.value}",
                                        },
                                    }
                                ],
                            }
                        )

        return {
            "requestId": self.generate_request_id(),
            "successful": successful,
            "unsuccessful": unsuccessful,
        }

    def disable_fast_snapshot_restores(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        azs, az_ids = self._validate_az_params(params)
        if not azs and not az_ids:
            raise ErrorCode(
                "MissingParameter",
                "Either AvailabilityZone.N or AvailabilityZoneId.N must be specified, but not both.",
            )

        snapshot_ids = self._validate_source_snapshot_ids(params)

        if dry_run:
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        successful = []
        unsuccessful = []

        now = self._get_current_time()

        for snapshot_id in snapshot_ids:
            try:
                owner_id = self._get_snapshot_owner_id(snapshot_id)
            except ErrorCode as e:
                for az in azs:
                    unsuccessful.append(
                        {
                            "snapshotId": snapshot_id,
                            "fastSnapshotRestoreStateErrorSet": [
                                {
                                    "availabilityZone": az,
                                    "error": {"code": e.code, "message": str(e)},
                                }
                            ],
                        }
                    )
                for azid in az_ids:
                    unsuccessful.append(
                        {
                            "snapshotId": snapshot_id,
                            "fastSnapshotRestoreStateErrorSet": [
                                {
                                    "availabilityZoneId": azid,
                                    "error": {"code": e.code, "message": str(e)},
                                }
                            ],
                        }
                    )
                continue

from emulator_core.gateway.base import BaseGateway

class FastSnapshotRestoresGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeFastSnapshotRestores", self.describe_fast_snapshot_restores)
        self.register_action("DisableFastSnapshotRestores", self.disable_fast_snapshot_restores)
        self.register_action("EnableFastSnapshotRestores", self.enable_fast_snapshot_restores)

    def describe_fast_snapshot_restores(self, params):
        return self.backend.describe_fast_snapshot_restores(params)

    def disable_fast_snapshot_restores(self, params):
        return self.backend.disable_fast_snapshot_restores(params)

    def enable_fast_snapshot_restores(self, params):
        return self.backend.enable_fast_snapshot_restores(params)
