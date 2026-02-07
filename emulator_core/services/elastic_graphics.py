from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class ElasticGpuHealth(Enum):
    OK = "OK"
    IMPAIRED = "IMPAIRED"


class ElasticGpuState(Enum):
    ATTACHED = "ATTACHED"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class ElasticGpu:
    elastic_gpu_id: str
    availability_zone: Optional[str] = None
    elastic_gpu_type: Optional[str] = None
    elastic_gpu_health: Optional[ElasticGpuHealth] = None
    elastic_gpu_state: Optional[ElasticGpuState] = None
    instance_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "elasticGpuId": self.elastic_gpu_id,
            "availabilityZone": self.availability_zone,
            "elasticGpuType": self.elastic_gpu_type,
            "elasticGpuHealth": self.elastic_gpu_health.value if self.elastic_gpu_health else None,
            "elasticGpuState": self.elastic_gpu_state.value if self.elastic_gpu_state else None,
            "instanceId": self.instance_id,
            "tagSet": [Tag(k, v).to_dict() for k, v in self.tags.items()],
        }


class ElasticGraphicsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.elastic_graphics dict for storage

    def describe_elastic_gpus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate parameters keys
        allowed_keys = {
            "DryRun",
            # ElasticGpuId.N keys are dynamic, handle separately
            # Filter.N keys are dynamic, handle separately
            "MaxResults",
            "NextToken",
        }
        # Validate keys and parse ElasticGpuId.N and Filter.N keys
        elastic_gpu_ids: List[str] = []
        filters: List[Dict[str, Any]] = []
        max_results: Optional[int] = None
        next_token: Optional[str] = None
        dry_run: Optional[bool] = None

        for key in params:
            if key == "DryRun":
                dry_run = params[key]
                if not isinstance(dry_run, bool):
                    raise ErrorCode("InvalidParameterValue", "DryRun must be a Boolean")
            elif key.startswith("ElasticGpuId."):
                # Expect keys like ElasticGpuId.1, ElasticGpuId.2, ...
                val = params[key]
                if not isinstance(val, str):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                elastic_gpu_ids.append(val)
            elif key.startswith("Filter."):
                # Filter.N.Name and Filter.N.Values.M
                # We need to parse filters by their index N
                # Collect filters by N
                # We'll parse all Filter.N.* keys and build filters list
                # First, collect all filter keys by N
                pass
            elif key == "MaxResults":
                max_results = params[key]
                if not isinstance(max_results, int):
                    raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
                if max_results < 10 or max_results > 1000:
                    raise ErrorCode("InvalidParameterValue", "MaxResults must be between 10 and 1000")
            elif key == "NextToken":
                next_token = params[key]
                if not isinstance(next_token, str):
                    raise ErrorCode("InvalidParameterValue", "NextToken must be a string")
            else:
                # Could be Filter.N.Name or Filter.N.Values.M keys
                if key.startswith("Filter."):
                    # We'll parse filters below
                    pass
                else:
                    raise ErrorCode("InvalidParameterValue", f"Unknown parameter {key}")

        # Parse filters from params keys
        # Filters are in the form Filter.N.Name and Filter.N.Values.M
        # We need to group by N, then build filter dicts
        filter_dict: Dict[int, Dict[str, Any]] = {}
        for key in params:
            if key.startswith("Filter."):
                # key example: Filter.1.Name, Filter.1.Values.1, Filter.1.Values.2
                parts = key.split(".")
                if len(parts) < 3:
                    raise ErrorCode("InvalidParameterValue", f"Invalid filter parameter {key}")
                try:
                    filter_index = int(parts[1])
                except Exception:
                    raise ErrorCode("InvalidParameterValue", f"Invalid filter index in {key}")
                if filter_index < 1:
                    raise ErrorCode("InvalidParameterValue", f"Filter index must be >= 1 in {key}")
                if filter_index not in filter_dict:
                    filter_dict[filter_index] = {"Name": None, "Values": []}
                if parts[2] == "Name":
                    val = params[key]
                    if not isinstance(val, str):
                        raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                    filter_dict[filter_index]["Name"] = val
                elif parts[2] == "Values":
                    if len(parts) != 4:
                        raise ErrorCode("InvalidParameterValue", f"Invalid filter value parameter {key}")
                    val = params[key]
                    if not isinstance(val, str):
                        raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                    filter_dict[filter_index]["Values"].append(val)
                else:
                    raise ErrorCode("InvalidParameterValue", f"Invalid filter parameter {key}")

        # Convert filter_dict to list, validate filter names and values
        for idx in sorted(filter_dict.keys()):
            f = filter_dict[idx]
            if f["Name"] is None:
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx}.Name is required")
            if not isinstance(f["Values"], list) or len(f["Values"]) == 0:
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx}.Values must be a non-empty list")
            filters.append(f)

        # DryRun check
        if dry_run is True:
            # Check permissions - for emulator, assume always allowed
            # Return DryRunOperation error code
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Gather all ElasticGpus from state
        all_egpus: List[ElasticGpu] = list(self.state.elastic_graphics.values())

        # Filter by ElasticGpuId if provided
        if elastic_gpu_ids:
            filtered_egpus = []
            for egpu_id in elastic_gpu_ids:
                egpu = self.state.get_resource(egpu_id)
                if egpu is None or not isinstance(egpu, ElasticGpu):
                    # According to AWS behavior, if an ID does not exist, it is ignored (no error)
                    continue
                filtered_egpus.append(egpu)
            all_egpus = filtered_egpus

        # Apply filters
        for f in filters:
            name = f["Name"]
            values = f["Values"]
            # Valid filter names:
            # availability-zone, elastic-gpu-health, elastic-gpu-state, elastic-gpu-type, instance-id
            if name not in {
                "availability-zone",
                "elastic-gpu-health",
                "elastic-gpu-state",
                "elastic-gpu-type",
                "instance-id",
            }:
                raise ErrorCode("InvalidParameterValue", f"Invalid filter name: {name}")

            def matches_filter(egpu: ElasticGpu) -> bool:
                if name == "availability-zone":
                    return egpu.availability_zone in values
                elif name == "elastic-gpu-health":
                    # values are strings like "OK" or "IMPAIRED"
                    if egpu.elastic_gpu_health is None:
                        return False
                    return egpu.elastic_gpu_health.value in values
                elif name == "elastic-gpu-state":
                    # values like "ATTACHED"
                    if egpu.elastic_gpu_state is None:
                        return False
                    return egpu.elastic_gpu_state.value in values
                elif name == "elastic-gpu-type":
                    return egpu.elastic_gpu_type in values
                elif name == "instance-id":
                    return egpu.instance_id in values
                else:
                    return False

            all_egpus = [eg for eg in all_egpus if matches_filter(eg)]

        # Pagination
        # NextToken is a string token representing the index offset as string
        start_index = 0
        if next_token is not None:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index > len(all_egpus):
                    raise ErrorCode("InvalidParameterValue", "Invalid NextToken value")
            except Exception:
                raise ErrorCode("InvalidParameterValue", "Invalid NextToken value")

        # Default max_results if not provided
        if max_results is None:
            max_results = 1000  # AWS default max page size

        # Slice results
        end_index = min(start_index + max_results, len(all_egpus))
        page_egpus = all_egpus[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(all_egpus):
            new_next_token = str(end_index)

        # Build response
        response = {
            "elasticGpuSet": [egpu.to_dict() for egpu in page_egpus],
            "maxResults": max_results,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

        return response

from emulator_core.gateway.base import BaseGateway

class ElasticGraphicsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeElasticGpus", self.describe_elastic_gpus)

    def describe_elastic_gpus(self, params):
        return self.backend.describe_elastic_gpus(params)
