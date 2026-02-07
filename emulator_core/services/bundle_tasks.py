from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class BundleTaskState(Enum):
    PENDING = "pending"
    WAITING_FOR_SHUTDOWN = "waiting-for-shutdown"
    BUNDLING = "bundling"
    STORING = "storing"
    CANCELLING = "cancelling"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class BundleTaskError:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.code is not None:
            d["code"] = self.code
        if self.message is not None:
            d["message"] = self.message
        return d


@dataclass
class S3Storage:
    AWSAccessKeyId: Optional[str] = None
    Bucket: Optional[str] = None
    Prefix: Optional[str] = None
    UploadPolicy: Optional[str] = None
    UploadPolicySignature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.AWSAccessKeyId is not None:
            d["AWSAccessKeyId"] = self.AWSAccessKeyId
        if self.Bucket is not None:
            d["bucket"] = self.Bucket
        if self.Prefix is not None:
            d["prefix"] = self.Prefix
        if self.UploadPolicy is not None:
            d["uploadPolicy"] = self.UploadPolicy
        if self.UploadPolicySignature is not None:
            d["uploadPolicySignature"] = self.UploadPolicySignature
        return d


@dataclass
class Storage:
    S3: Optional[S3Storage] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.S3 is not None:
            d["S3"] = self.S3.to_dict()
        return d


@dataclass
class BundleTask:
    bundleId: str
    instanceId: str
    state: BundleTaskState
    startTime: datetime
    updateTime: datetime
    progress: Optional[str] = None
    storage: Optional[Storage] = None
    error: Optional[BundleTaskError] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "bundleId": self.bundleId,
            "instanceId": self.instanceId,
            "state": self.state.value,
            "startTime": self.startTime.isoformat(timespec='milliseconds').replace("+00:00", "Z"),
            "updateTime": self.updateTime.isoformat(timespec='milliseconds').replace("+00:00", "Z"),
        }
        if self.progress is not None:
            d["progress"] = self.progress
        if self.storage is not None:
            d["storage"] = self.storage.to_dict()
        if self.error is not None:
            d["error"] = self.error.to_dict()
        return d


class BundleTasksBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.bundle_tasks dict for storage

    def _validate_dry_run(self, params: Dict[str, Any]) -> None:
        # DryRun is optional boolean
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

    def _validate_instance(self, instance_id: str) -> None:
        # Validate instance exists and is Windows instance store-backed
        instance = self.state.get_resource(instance_id)
        if instance is None:
            raise ErrorCode("InvalidInstanceID.NotFound", f"The instance ID '{instance_id}' does not exist")
        # Check instance platform and root device type
        platform = getattr(instance, "platform", None)
        root_device_type = getattr(instance, "root_device_type", None)
        if platform != "windows":
            raise ErrorCode("UnsupportedOperation", "BundleInstance is only supported for Windows instances")
        if root_device_type != "instance-store":
            raise ErrorCode("UnsupportedOperation", "BundleInstance is only supported for instance store-backed instances")

    def _parse_storage(self, storage_param: Dict[str, Any]) -> Storage:
        if not isinstance(storage_param, dict):
            raise ErrorCode("InvalidParameterValue", "Storage must be a dictionary")
        s3_param = storage_param.get("S3")
        s3_storage = None
        if s3_param is not None:
            if not isinstance(s3_param, dict):
                raise ErrorCode("InvalidParameterValue", "Storage.S3 must be a dictionary")
            # Extract fields, all optional except Bucket is recommended but not required
            AWSAccessKeyId = s3_param.get("AWSAccessKeyId")
            Bucket = s3_param.get("Bucket")
            Prefix = s3_param.get("Prefix")
            UploadPolicy = s3_param.get("UploadPolicy")
            UploadPolicySignature = s3_param.get("UploadPolicySignature")
            # Validate types if present
            if AWSAccessKeyId is not None and not isinstance(AWSAccessKeyId, str):
                raise ErrorCode("InvalidParameterValue", "Storage.S3.AWSAccessKeyId must be a string")
            if Bucket is not None and not isinstance(Bucket, str):
                raise ErrorCode("InvalidParameterValue", "Storage.S3.Bucket must be a string")
            if Prefix is not None and not isinstance(Prefix, str):
                raise ErrorCode("InvalidParameterValue", "Storage.S3.Prefix must be a string")
            if UploadPolicy is not None and not isinstance(UploadPolicy, str):
                raise ErrorCode("InvalidParameterValue", "Storage.S3.UploadPolicy must be a string")
            if UploadPolicySignature is not None and not isinstance(UploadPolicySignature, str):
                raise ErrorCode("InvalidParameterValue", "Storage.S3.UploadPolicySignature must be a string")
            s3_storage = S3Storage(
                AWSAccessKeyId=AWSAccessKeyId,
                Bucket=Bucket,
                Prefix=Prefix,
                UploadPolicy=UploadPolicy,
                UploadPolicySignature=UploadPolicySignature,
            )
        return Storage(S3=s3_storage)

    def bundle_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements BundleInstance API.
        """
        self._validate_dry_run(params)

        instance_id = params.get("InstanceId")
        if not instance_id or not isinstance(instance_id, str):
            raise ErrorCode("MissingParameter", "InstanceId is required and must be a string")

        storage_param = params.get("Storage")
        if storage_param is None:
            raise ErrorCode("MissingParameter", "Storage is required")
        storage = self._parse_storage(storage_param)

        # Validate instance existence and type
        self._validate_instance(instance_id)

        # Generate bundle task id
        bundle_id = f"bun-{self.generate_unique_id()}"

        now = datetime.now(timezone.utc)

        # Create BundleTask object with initial state pending
        bundle_task = BundleTask(
            bundleId=bundle_id,
            instanceId=instance_id,
            state=BundleTaskState.BUNDLING,  # According to docs, after start it is bundling
            startTime=now,
            updateTime=now,
            progress="0%",
            storage=storage,
            error=None,
        )

        # Store in shared state dict
        self.state.bundle_tasks[bundle_id] = bundle_task

        return {
            "bundleInstanceTask": bundle_task.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def cancel_bundle_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements CancelBundleTask API.
        """
        self._validate_dry_run(params)

        bundle_id = params.get("BundleId")
        if not bundle_id or not isinstance(bundle_id, str):
            raise ErrorCode("MissingParameter", "BundleId is required and must be a string")

        bundle_task = self.state.bundle_tasks.get(bundle_id)
        if bundle_task is None:
            raise ErrorCode("InvalidBundleId.NotFound", f"The bundle task ID '{bundle_id}' does not exist")

        # Only allow cancel if task is not complete or failed
        if bundle_task.state in (BundleTaskState.COMPLETE, BundleTaskState.FAILED):
            # Cannot cancel completed or failed tasks, just return current state
            pass
        else:
            # Update state to cancelling, progress to 20% as example, update updateTime
            bundle_task.state = BundleTaskState.CANCELLING
            bundle_task.progress = "20%"
            bundle_task.updateTime = datetime.now(timezone.utc)
            # Store updated task
            self.state.bundle_tasks[bundle_id] = bundle_task

        return {
            "bundleInstanceTask": bundle_task.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def describe_bundle_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements DescribeBundleTasks API.
        """
        self._validate_dry_run(params)

        # Extract BundleId.N parameters: keys like BundleId.1, BundleId.2, or BundleId.N as list
        # The input params dict may have keys like "BundleId.1", "BundleId.2", etc.
        # Collect all BundleId.* keys
        bundle_ids: List[str] = []
        for key, value in params.items():
            if key.startswith("BundleId."):
                if isinstance(value, str):
                    bundle_ids.append(value)
                else:
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")

        # Extract filters: Filter.N.Name and Filter.N.Value.M or Filter.N.Values
        # We'll parse filters into a dict: filter_name -> set of values
        filters: Dict[str, List[str]] = {}
        # Collect filter indices
        filter_indices = set()
        for key in params.keys():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    try:
                        idx = int(parts[1])
                        filter_indices.add(idx)
                    except Exception:
                        pass
        for idx in filter_indices:
            name_key = f"Filter.{idx}.Name"
            values_prefix = f"Filter.{idx}.Value"
            values_alt_prefix = f"Filter.{idx}.Values"
            filter_name = params.get(name_key)
            if filter_name is None:
                continue
            # Collect values
            values = []
            # Values can be multiple keys: Value.1, Value.2, ...
            for k, v in params.items():
                if k.startswith(values_prefix):
                    # e.g. Filter.1.Value.1
                    if isinstance(v, str):
                        values.append(v)
                    else:
                        raise ErrorCode("InvalidParameterValue", f"{k} must be a string")
            # Also check if Values is a list (some clients may send Filter.N.Values as list)
            if values_alt_prefix in params:
                alt_values = params[values_alt_prefix]
                if isinstance(alt_values, list):
                    for val in alt_values:
                        if not isinstance(val, str):
                            raise ErrorCode("InvalidParameterValue", f"Filter.{idx}.Values must be list of strings")
                    values.extend(alt_values)
                elif isinstance(alt_values, str):
                    values.append(alt_values)
                else:
                    raise ErrorCode("InvalidParameterValue", f"Filter.{idx}.Values must be string or list of strings")
            if values:
                filters[filter_name] = values

        # Filter bundle tasks by bundle_ids if provided
        tasks = []
        if bundle_ids:
            for bid in bundle_ids:
                task = self.state.bundle_tasks.get(bid)
                if task:
                    tasks.append(task)
        else:
            # No bundle_ids filter, get all tasks
            tasks = list(self.state.bundle_tasks.values())

        # Apply filters if any
        def task_matches_filter(task: BundleTask, filter_name: str, filter_values: List[str]) -> bool:
            # Map filter names to task attributes or nested attributes
            # Valid filter names:
            # bundle-id, error-code, error-message, instance-id, progress, s3-bucket, s3-prefix,
            # start-time, state, update-time
            if filter_name == "bundle-id":
                return task.bundleId in filter_values
            elif filter_name == "error-code":
                if task.error and task.error.code:
                    return task.error.code in filter_values
                return False
            elif filter_name == "error-message":
                if task.error and task.error.message:
                    return any(val in task.error.message for val in filter_values)
                return False
            elif filter_name == "instance-id":
                return task.instanceId in filter_values
            elif filter_name == "progress":
                if task.progress is None:
                    return False
                return any(val == task.progress for val in filter_values)
            elif filter_name == "s3-bucket":
                if task.storage and task.storage.S3 and task.storage.S3.Bucket:
                    return task.storage.S3.Bucket in filter_values
                return False
            elif filter_name == "s3-prefix":
                if task.storage and task.storage.S3 and task.storage.S3.Prefix:
                    return task.storage.S3.Prefix in filter_values
                return False
            elif filter_name == "start-time":
                # Filter values are timestamps, match exact string representation
                # We'll compare ISO8601 strings
                task_start = task.startTime.isoformat(timespec='milliseconds').replace("+00:00", "Z")
                return task_start in filter_values
            elif filter_name == "state":
                return task.state.value in filter_values
            elif filter_name == "update-time":
                task_update = task.updateTime.isoformat(timespec='milliseconds').replace("+00:00", "Z")
                return task_update in filter_values
            else:
                # Unknown filter, ignore
                return True

        if filters:
            filtered_tasks = []
            for task in tasks:
                # For each filter, task must match at least one value (OR within values)
                # All filters combined with AND
                if all(task_matches_filter(task, fname, fvals) for fname, fvals in filters.items()):
                    filtered_tasks.append(task)
            tasks = filtered_tasks

        # Compose response
        return {
            "bundleInstanceTasksSet": [task.to_dict() for task in tasks],
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class BundletasksGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("BundleInstance", self.bundle_instance)
        self.register_action("CancelBundleTask", self.cancel_bundle_task)
        self.register_action("DescribeBundleTasks", self.describe_bundle_tasks)

    def bundle_instance(self, params):
        return self.backend.bundle_instance(params)

    def cancel_bundle_task(self, params):
        return self.backend.cancel_bundle_task(params)

    def describe_bundle_tasks(self, params):
        return self.backend.describe_bundle_tasks(params)
