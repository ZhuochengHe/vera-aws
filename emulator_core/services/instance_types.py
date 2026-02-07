from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


# We define dataclasses for the nested structures used in instance type info.
# For brevity, only fields used in responses are included, all optional as per spec.

@dataclass
class EbsOptimizedInfo:
    baseline_bandwidth_in_mbps: Optional[int] = None
    baseline_iops: Optional[int] = None
    baseline_throughput_in_mbps: Optional[float] = None
    maximum_bandwidth_in_mbps: Optional[int] = None
    maximum_iops: Optional[int] = None
    maximum_throughput_in_mbps: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.baseline_bandwidth_in_mbps is not None:
            d["baselineBandwidthInMbps"] = self.baseline_bandwidth_in_mbps
        if self.baseline_iops is not None:
            d["baselineIops"] = self.baseline_iops
        if self.baseline_throughput_in_mbps is not None:
            d["baselineThroughputInMBps"] = self.baseline_throughput_in_mbps
        if self.maximum_bandwidth_in_mbps is not None:
            d["maximumBandwidthInMbps"] = self.maximum_bandwidth_in_mbps
        if self.maximum_iops is not None:
            d["maximumIops"] = self.maximum_iops
        if self.maximum_throughput_in_mbps is not None:
            d["maximumThroughputInMBps"] = self.maximum_throughput_in_mbps
        return d


@dataclass
class EbsInfo:
    attachment_limit_type: Optional[str] = None  # shared | dedicated
    ebs_optimized_info: Optional[EbsOptimizedInfo] = None
    ebs_optimized_support: Optional[str] = None  # unsupported | supported | default
    encryption_support: Optional[str] = None  # unsupported | supported
    maximum_ebs_attachments: Optional[int] = None
    nvme_support: Optional[str] = None  # unsupported | supported | required

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.attachment_limit_type is not None:
            d["attachmentLimitType"] = self.attachment_limit_type
        if self.ebs_optimized_info is not None:
            d["ebsOptimizedInfo"] = self.ebs_optimized_info.to_dict()
        if self.ebs_optimized_support is not None:
            d["ebsOptimizedSupport"] = self.ebs_optimized_support
        if self.encryption_support is not None:
            d["encryptionSupport"] = self.encryption_support
        if self.maximum_ebs_attachments is not None:
            d["maximumEbsAttachments"] = self.maximum_ebs_attachments
        if self.nvme_support is not None:
            d["nvmeSupport"] = self.nvme_support
        return d


@dataclass
class DiskInfo:
    count: Optional[int] = None
    size_in_gb: Optional[int] = None
    type: Optional[str] = None  # hdd | ssd

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.count is not None:
            d["count"] = self.count
        if self.size_in_gb is not None:
            d["sizeInGB"] = self.size_in_gb
        if self.type is not None:
            d["type"] = self.type
        return d


@dataclass
class InstanceStorageInfo:
    disks: List[DiskInfo] = field(default_factory=list)
    encryption_support: Optional[str] = None  # unsupported | required
    nvme_support: Optional[str] = None  # unsupported | supported | required
    total_size_in_gb: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.disks:
            d["disks"] = [disk.to_dict() for disk in self.disks]
        if self.encryption_support is not None:
            d["encryptionSupport"] = self.encryption_support
        if self.nvme_support is not None:
            d["nvmeSupport"] = self.nvme_support
        if self.total_size_in_gb is not None:
            d["totalSizeInGB"] = self.total_size_in_gb
        return d


@dataclass
class VCpuInfo:
    default_cores: Optional[int] = None
    default_threads_per_core: Optional[int] = None
    default_vcpus: Optional[int] = None
    valid_cores: Optional[List[int]] = None
    valid_threads_per_core: Optional[List[int]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.default_cores is not None:
            d["defaultCores"] = self.default_cores
        if self.default_threads_per_core is not None:
            d["defaultThreadsPerCore"] = self.default_threads_per_core
        if self.default_vcpus is not None:
            d["defaultVCpus"] = self.default_vcpus
        if self.valid_cores is not None:
            d["validCores"] = self.valid_cores
        if self.valid_threads_per_core is not None:
            d["validThreadsPerCore"] = self.valid_threads_per_core
        return d


@dataclass
class InstanceTypeInfo:
    instance_type: str
    auto_recovery_supported: Optional[bool] = None
    bare_metal: Optional[bool] = None
    burstable_performance_supported: Optional[bool] = None
    current_generation: Optional[bool] = None
    dedicated_hosts_supported: Optional[bool] = None
    ebs_info: Optional[EbsInfo] = None
    free_tier_eligible: Optional[bool] = None
    hibernation_supported: Optional[bool] = None
    hypervisor: Optional[str] = None  # nitro | xen
    instance_storage_info: Optional[InstanceStorageInfo] = None
    instance_storage_supported: Optional[bool] = None
    vcpu_info: Optional[VCpuInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"instanceType": self.instance_type}
        if self.auto_recovery_supported is not None:
            d["autoRecoverySupported"] = self.auto_recovery_supported
        if self.bare_metal is not None:
            d["bareMetal"] = self.bare_metal
        if self.burstable_performance_supported is not None:
            d["burstablePerformanceSupported"] = self.burstable_performance_supported
        if self.current_generation is not None:
            d["currentGeneration"] = self.current_generation
        if self.dedicated_hosts_supported is not None:
            d["dedicatedHostsSupported"] = self.dedicated_hosts_supported
        if self.ebs_info is not None:
            d["ebsInfo"] = self.ebs_info.to_dict()
        if self.free_tier_eligible is not None:
            d["freeTierEligible"] = self.free_tier_eligible
        if self.hibernation_supported is not None:
            d["hibernationSupported"] = self.hibernation_supported
        if self.hypervisor is not None:
            d["hypervisor"] = self.hypervisor
        if self.instance_storage_info is not None:
            d["instanceStorageInfo"] = self.instance_storage_info.to_dict()
        if self.instance_storage_supported is not None:
            d["instanceStorageSupported"] = self.instance_storage_supported
        if self.vcpu_info is not None:
            d["vCpuInfo"] = self.vcpu_info.to_dict()
        return d


@dataclass
class InstanceTypeOffering:
    instance_type: str
    location: str
    location_type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instanceType": self.instance_type,
            "location": self.location,
            "locationType": self.location_type,
        }


@dataclass
class InstanceTypeInfoFromInstanceRequirements:
    instance_type: str

    def to_dict(self) -> Dict[str, Any]:
        return {"instanceType": self.instance_type}


class InstanceTypesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.instance_types dict for instance type info storage
        # For this emulator, we assume self.state.instance_types is pre-populated with InstanceTypeInfo objects keyed by instance_type string
        # If not, we can initialize it empty here
        if not hasattr(self.state, "instance_types"):
            self.state.instance_types = {}

    def _validate_dry_run(self, params: Dict[str, Any]) -> None:
        # DryRun parameter validation and error raising
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if specified")
        if dry_run:
            # For simplicity, assume user has permission; raise DryRunOperation error
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

    def _parse_filters(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Extract filters from params keys like Filter.1.Name, Filter.1.Values, Filter.2.Name, etc.
        filters = []
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
        for idx in sorted(filter_indices):
            name_key = f"Filter.{idx}.Name"
            values_key = f"Filter.{idx}.Values"
            name = params.get(name_key)
            values = params.get(values_key)
            if values is not None and not isinstance(values, list):
                raise ErrorCode("InvalidParameterValue", f"{values_key} must be a list of strings")
            filters.append({"Name": name, "Values": values})
        return filters

    def _filter_instance_type_offerings(
        self,
        offerings: List[InstanceTypeOffering],
        filters: List[Dict[str, Any]],
        location_type: Optional[str],
    ) -> List[InstanceTypeOffering]:
        # Apply filters and location_type filtering to offerings list
        filtered = offerings
        # Filter by location_type if specified
        if location_type is not None:
            if location_type not in ("region", "availability-zone", "availability-zone-id", "outpost"):
                raise ErrorCode("InvalidParameterValue", f"Invalid LocationType: {location_type}")
            filtered = [o for o in filtered if o.location_type == location_type]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values")
            if name is None or values is None:
                continue
            if name == "instance-type":
                filtered = [o for o in filtered if o.instance_type in values]
            elif name == "location":
                filtered = [o for o in filtered if o.location in values]
            else:
                # Unknown filter name
                raise ErrorCode("InvalidParameterValue", f"Unsupported filter name: {name}")
        return filtered

    def describe_instance_type_offerings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements DescribeInstanceTypeOfferings API.
        """
        self._validate_dry_run(params)

        filters = self._parse_filters(params)
        location_type = params.get("LocationType")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate MaxResults if specified
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 1000")

        # Gather all offerings from self.state.instance_types
        # For this emulator, we assume each instance type is offered in the current region only
        # We simulate location and location_type as "region" and region name "us-east-1" for example
        # In real implementation, this would be more complex
        region_name = self.state.region_name if hasattr(self.state, "region_name") else "us-east-1"
        all_offerings = []
        for instance_type in self.state.instance_types.keys():
            # For simplicity, location_type is "region" and location is region_name
            offering = InstanceTypeOffering(
                instance_type=instance_type,
                location=region_name,
                location_type="region",
            )
            all_offerings.append(offering)

        # Filter offerings by filters and location_type
        filtered_offerings = self._filter_instance_type_offerings(all_offerings, filters, location_type)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "Invalid NextToken")

        end_index = len(filtered_offerings)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_offerings))

        page_offerings = filtered_offerings[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(filtered_offerings):
            new_next_token = str(end_index)

        response = {
            "instanceTypeOfferingSet": [o.to_dict() for o in page_offerings],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response

    def _filter_instance_types(
        self,
        instance_types: List[InstanceTypeInfo],
        filters: List[Dict[str, Any]],
        instance_type_names: Optional[List[str]],
    ) -> List[InstanceTypeInfo]:
        filtered = instance_types

        # Filter by instance_type_names if specified
        if instance_type_names is not None:
            filtered = [it for it in filtered if it.instance_type in instance_type_names]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values")
            if name is None or values is None:
                continue

            # We implement a subset of filters for demonstration, as full filter support is very large
            # Filters supported: instance-type, bare-metal, current-generation, free-tier-eligible, hypervisor
            if name == "instance-type":
                filtered = [it for it in filtered if it.instance_type in values]
            elif name == "bare-metal":
                # values expected to be ["true"] or ["false"]
                bool_val = values[0].lower() == "true"
                filtered = [it for it in filtered if (it.bare_metal or False) == bool_val]
            elif name == "current-generation":
                bool_val = values[0].lower() == "true"
                filtered = [it for it in filtered if (it.current_generation or False) == bool_val]
            elif name == "free-tier-eligible":
                bool_val = values[0].lower() == "true"
                filtered = [it for it in filtered if (it.free_tier_eligible or False) == bool_val]
            elif name == "hypervisor":
                filtered = [it for it in filtered if it.hypervisor in values]
            else:
                # Unsupported filter for now
                raise ErrorCode("InvalidParameterValue", f"Unsupported filter name: {name}")

        return filtered

    def describe_instance_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements DescribeInstanceTypes API.
        """
        self._validate_dry_run(params)

        filters = self._parse_filters(params)
        instance_type_names = None
        # Extract InstanceType.N parameters (e.g. InstanceType.1, InstanceType.2, ...)
        instance_type_names = []
        for key in params.keys():
            if key.startswith("InstanceType."):
                val = params.get(key)
                if not isinstance(val, str):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                instance_type_names.append(val)
        if not instance_type_names:
            instance_type_names = None  # means all

        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate MaxResults if specified
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 5 or max_results > 100:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 100")

        # Get all instance types from state
        all_instance_types = list(self.state.instance_types.values())

        # Filter instance types by filters and instance_type_names
        filtered_instance_types = self._filter_instance_types(all_instance_types, filters, instance_type_names)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "Invalid NextToken")

        end_index = len(filtered_instance_types)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_instance_types))

        page_instance_types = filtered_instance_types[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(filtered_instance_types):
            new_next_token = str(end_index)

        response = {
            "instanceTypeSet": [it.to_dict() for it in page_instance_types],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response

    def get_instance_types_from_instance_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implements GetInstanceTypesFromInstanceRequirements API.
        """
        self._validate_dry_run(params)

        # Validate required parameters
        arch_types = params.get("ArchitectureType.N")
        if arch_types is None or not isinstance(arch_types, list) or len(arch_types) == 0:
            raise ErrorCode("MissingParameter", "ArchitectureType.N is required and must be a non-empty list")

        virtualization_types = params.get("VirtualizationType.N")
        if virtualization_types is None or not isinstance(virtualization_types, list) or len(virtualization_types) == 0:
            raise ErrorCode("MissingParameter", "VirtualizationType.N is required and must be a non-empty list")

        instance_requirements = params.get("InstanceRequirements")
        if instance_requirements is None or not isinstance(instance_requirements, dict):
            raise ErrorCode("MissingParameter", "InstanceRequirements is required and must be a dict")

        max_results = params.get("MaxResults")

from emulator_core.gateway.base import BaseGateway

class InstancetypesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeInstanceTypeOfferings", self.describe_instance_type_offerings)
        self.register_action("DescribeInstanceTypes", self.describe_instance_types)
        self.register_action("GetInstanceTypesFromInstanceRequirements", self.get_instance_types_from_instance_requirements)

    def describe_instance_type_offerings(self, params):
        return self.backend.describe_instance_type_offerings(params)

    def describe_instance_types(self, params):
        return self.backend.describe_instance_types(params)

    def get_instance_types_from_instance_requirements(self, params):
        return self.backend.get_instance_types_from_instance_requirements(params)
