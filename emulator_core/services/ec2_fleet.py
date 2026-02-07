from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


# Enums for various string fields with limited valid values

class ExcessCapacityTerminationPolicy(str, Enum):
    NO_TERMINATION = "no-termination"
    TERMINATION = "termination"


class FleetType(str, Enum):
    REQUEST = "request"
    MAINTAIN = "maintain"
    INSTANT = "instant"


class OnDemandAllocationStrategy(str, Enum):
    LOWEST_PRICE = "lowest-price"
    PRIORITIZED = "prioritized"


class UsageStrategy(str, Enum):
    USE_CAPACITY_RESERVATIONS_FIRST = "use-capacity-reservations-first"


class SpotAllocationStrategy(str, Enum):
    LOWEST_PRICE = "lowest-price"
    DIVERSIFIED = "diversified"
    CAPACITY_OPTIMIZED = "capacity-optimized"
    CAPACITY_OPTIMIZED_PRIORITIZED = "capacity-optimized-prioritized"
    PRICE_CAPACITY_OPTIMIZED = "price-capacity-optimized"


class InstanceInterruptionBehavior(str, Enum):
    HIBERNATE = "hibernate"
    STOP = "stop"
    TERMINATE = "terminate"


class ReplacementStrategy(str, Enum):
    LAUNCH = "launch"
    LAUNCH_BEFORE_TERMINATE = "launch-before-terminate"


class Lifecycle(str, Enum):
    SPOT = "spot"
    ON_DEMAND = "on-demand"


class Platform(str, Enum):
    WINDOWS = "Windows"


class ActivityStatus(str, Enum):
    ERROR = "error"
    PENDING_FULFILLMENT = "pending_fulfillment"
    PENDING_TERMINATION = "pending_termination"
    FULFILLED = "fulfilled"


class FleetState(str, Enum):
    SUBMITTED = "submitted"
    ACTIVE = "active"
    DELETED = "deleted"
    FAILED = "failed"
    DELETED_RUNNING = "deleted_running"
    DELETED_TERMINATING = "deleted_terminating"
    MODIFYING = "modifying"


class EventType(str, Enum):
    INSTANCE_CHANGE = "instance-change"
    FLEET_CHANGE = "fleet-change"
    SERVICE_ERROR = "service-error"


class EventSubType(str, Enum):
    IAM_FLEET_ROLE_INVALID = "iamFleetRoleInvalid"
    ALL_LAUNCH_SPECS_TEMP_BLACKLISTED = "allLaunchSpecsTemporarilyBlacklisted"
    SPOT_INSTANCE_COUNT_LIMIT_EXCEEDED = "spotInstanceCountLimitExceeded"
    SPOT_FLEET_REQUEST_CONFIGURATION_INVALID = "spotFleetRequestConfigurationInvalid"
    ACTIVE = "active"
    DELETED = "deleted"
    DELETED_RUNNING = "deleted_running"
    DELETED_TERMINATING = "deleted_terminating"
    EXPIRED = "expired"
    MODIFY_IN_PROGRESS = "modify_in_progress"
    MODIFY_SUCCEEDED = "modify_succeeded"
    SUBMITTED = "submitted"
    PROGRESS = "progress"
    LAUNCHED = "launched"
    TERMINATED = "terminated"
    TERMINATION_NOTIFIED = "termination_notified"
    FLEET_PROGRESS_HALTED = "fleetProgressHalted"
    LAUNCH_SPEC_TEMP_BLACKLISTED = "launchSpecTemporarilyBlacklisted"
    LAUNCH_SPEC_UNUSABLE = "launchSpecUnusable"
    REGISTER_WITH_LOAD_BALANCERS_FAILED = "registerWithLoadBalancersFailed"


class CpuPerformanceFactor(str, Enum):
    # Placeholder for CPU performance factor values if any
    pass


class BaselineEbsBandwidthMbpsRequestobject:
    # Placeholder for baseline EBS bandwidth Mbps request object
    pass


class BaselinePerformanceFactorsRequestobject:
    # Placeholder for baseline performance factors request object
    pass


class CpuPerformanceFactorRequestobject:
    # Placeholder for CPU performance factor request object
    pass


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
class FleetEbsBlockDeviceRequest:
    DeleteOnTermination: Optional[bool] = None
    Encrypted: Optional[bool] = None
    Iops: Optional[int] = None
    KmsKeyId: Optional[str] = None
    SnapshotId: Optional[str] = None
    Throughput: Optional[int] = None
    VolumeSize: Optional[int] = None
    VolumeType: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DeleteOnTermination": self.DeleteOnTermination,
            "Encrypted": self.Encrypted,
            "Iops": self.Iops,
            "KmsKeyId": self.KmsKeyId,
            "SnapshotId": self.SnapshotId,
            "Throughput": self.Throughput,
            "VolumeSize": self.VolumeSize,
            "VolumeType": self.VolumeType,
        }


@dataclass
class FleetBlockDeviceMappingRequest:
    DeviceName: Optional[str] = None
    Ebs: Optional[FleetEbsBlockDeviceRequest] = None
    NoDevice: Optional[str] = None
    VirtualName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DeviceName": self.DeviceName,
            "Ebs": self.Ebs.to_dict() if self.Ebs else None,
            "NoDevice": self.NoDevice,
            "VirtualName": self.VirtualName,
        }


@dataclass
class FleetLaunchTemplateSpecificationRequest:
    LaunchTemplateId: Optional[str] = None
    LaunchTemplateName: Optional[str] = None
    Version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "LaunchTemplateId": self.LaunchTemplateId,
            "LaunchTemplateName": self.LaunchTemplateName,
            "Version": self.Version,
        }


@dataclass
class MemoryMiBRequest:
    Min: int
    Max: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Min": self.Min, "Max": self.Max}


@dataclass
class VCpuCountRangeRequest:
    Min: int
    Max: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Min": self.Min, "Max": self.Max}


@dataclass
class AcceleratorCountRequest:
    Max: Optional[int] = None
    Min: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Max": self.Max, "Min": self.Min}


@dataclass
class AcceleratorTotalMemoryMiBRequest:
    Max: Optional[int] = None
    Min: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Max": self.Max, "Min": self.Min}


@dataclass
class MemoryGiBPerVCpuRequest:
    Max: Optional[float] = None
    Min: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Max": self.Max, "Min": self.Min}


@dataclass
class NetworkBandwidthGbpsRequest:
    Max: Optional[float] = None
    Min: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Max": self.Max, "Min": self.Min}


@dataclass
class NetworkInterfaceCountRequest:
    Max: Optional[int] = None
    Min: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Max": self.Max, "Min": self.Min}


@dataclass
class BaselineEbsBandwidthMbps:
    Max: Optional[int] = None
    Min: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Max": self.Max, "Min": self.Min}


@dataclass
class BaselinePerformanceFactors:
    Cpu: Optional[CpuPerformanceFactor] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Cpu": self.Cpu.value if self.Cpu else None}


@dataclass
class CpuPerformanceFactor:
    # Placeholder for actual CPU performance factor values
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return self.value


@dataclass
class InstanceRequirementsRequest:
    MemoryMiB: MemoryMiBRequest
    VCpuCount: VCpuCountRangeRequest
    AcceleratorCount: Optional[AcceleratorCountRequest] = None
    AcceleratorManufacturers: Optional[List[str]] = None
    AcceleratorNames: Optional[List[str]] = None
    AcceleratorTotalMemoryMiB: Optional[AcceleratorTotalMemoryMiBRequest] = None
    AcceleratorTypes: Optional[List[str]] = None
    AllowedInstanceTypes: Optional[List[str]] = None
    BareMetal: Optional[str] = None
    BaselineEbsBandwidthMbps: Optional[BaselineEbsBandwidthMbps] = None
    BaselinePerformanceFactors: Optional[BaselinePerformanceFactors] = None
    BurstablePerformance: Optional[str] = None
    CpuManufacturers: Optional[List[str]] = None
    ExcludedInstanceTypes: Optional[List[str]] = None
    InstanceGenerations: Optional[List[str]] = None
    LocalStorage: Optional[str] = None
    LocalStorageTypes: Optional[List[str]] = None
    MaxSpotPriceAsPercentageOfOptimalOnDemandPrice: Optional[int] = None
    MemoryGiBPerVCpu: Optional[MemoryGiBPerVCpuRequest] = None
    NetworkBandwidthGbps: Optional[NetworkBandwidthGbpsRequest] = None
    NetworkInterfaceCount: Optional[NetworkInterfaceCountRequest] = None
    OnDemandMaxPricePercentageOverLowestPrice: Optional[int] = None
    RequireEncryptionInTransit: Optional[bool] = None
    RequireHibernateSupport: Optional[bool] = None
    SpotMaxPricePercentageOverLowestPrice: Optional[int] = None
    TotalLocalStorageGB: Optional[MemoryGiBPerVCpuRequest] = None  # Reusing MemoryGiBPerVCpuRequest for Min/Max double values

    def to_dict(self) -> Dict[str, Any]:
        return {
            "MemoryMiB": self.MemoryMiB.to_dict(),
            "VCpuCount": self.VCpuCount.to_dict(),
            "AcceleratorCount": self.AcceleratorCount.to_dict() if self.AcceleratorCount else None,
            "AcceleratorManufacturers": self.AcceleratorManufacturers,
            "AcceleratorNames": self.AcceleratorNames,
            "AcceleratorTotalMemoryMiB": self.AcceleratorTotalMemoryMiB.to_dict() if self.AcceleratorTotalMemoryMiB else None,
            "AcceleratorTypes": self.AcceleratorTypes,
            "AllowedInstanceTypes": self.AllowedInstanceTypes,
            "BareMetal": self.BareMetal,
            "BaselineEbsBandwidthMbps": self.BaselineEbsBandwidthMbps.to_dict() if self.BaselineEbsBandwidthMbps else None,
            "BaselinePerformanceFactors": self.BaselinePerformanceFactors.to_dict() if self.BaselinePerformanceFactors else None,
            "BurstablePerformance": self.BurstablePerformance,
            "CpuManufacturers": self.CpuManufacturers,
            "ExcludedInstanceTypes": self.ExcludedInstanceTypes,
            "InstanceGenerations": self.InstanceGenerations,
            "LocalStorage": self.LocalStorage,
            "LocalStorageTypes": self.LocalStorageTypes,
            "MaxSpotPriceAsPercentageOfOptimalOnDemandPrice": self.MaxSpotPriceAsPercentageOfOptimalOnDemandPrice,
            "MemoryGiBPerVCpu": self.MemoryGiBPerVCpu.to_dict() if self.MemoryGiBPerVCpu else None,
            "NetworkBandwidthGbps": self.NetworkBandwidthGbps.to_dict() if self.NetworkBandwidthGbps else None,
            "NetworkInterfaceCount": self.NetworkInterfaceCount.to_dict() if self.NetworkInterfaceCount else None,
            "OnDemandMaxPricePercentageOverLowestPrice": self.OnDemandMaxPricePercentageOverLowestPrice,
            "RequireEncryptionInTransit": self.RequireEncryptionInTransit,
            "RequireHibernateSupport": self.RequireHibernateSupport,
            "SpotMaxPricePercentageOverLowestPrice": self.SpotMaxPricePercentageOverLowestPrice,
            "TotalLocalStorageGB": self.TotalLocalStorageGB.to_dict() if self.TotalLocalStorageGB else None,
        }


@dataclass
class FleetLaunchTemplateOverridesRequest:
    AvailabilityZone: Optional[str] = None
    BlockDeviceMappings: List[FleetBlockDeviceMappingRequest] = field(default_factory=list)
    ImageId: Optional[str] = None
    InstanceRequirements: Optional[InstanceRequirementsRequest] = None
    InstanceType: Optional[str] = None
    MaxPrice: Optional[str] = None
    Placement: Optional["Placement"] = None
    Priority: Optional[float] = None
    SubnetId: Optional[str] = None
    WeightedCapacity: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.AvailabilityZone,
            "BlockDeviceMappings": [bdm.to_dict() for bdm in self.BlockDeviceMappings] if self.BlockDeviceMappings else None,
            "ImageId": self.ImageId,
            "InstanceRequirements": self.InstanceRequirements.to_dict() if self.InstanceRequirements else None,
            "InstanceType": self.InstanceType,
            "MaxPrice": self.MaxPrice,
            "Placement": self.Placement.to_dict() if self.Placement else None,
            "Priority": self.Priority,
            "SubnetId": self.SubnetId,
            "WeightedCapacity": self.WeightedCapacity,
        }


@dataclass
class FleetLaunchTemplateConfigRequest:
    LaunchTemplateSpecification: Optional[FleetLaunchTemplateSpecificationRequest] = None
    Overrides: List[FleetLaunchTemplateOverridesRequest] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "LaunchTemplateSpecification": self.LaunchTemplateSpecification.to_dict() if self.LaunchTemplateSpecification else None,
            "Overrides": [override.to_dict() for override in self.Overrides] if self.Overrides else None,
        }


@dataclass
class CapacityReservationOptionsRequest:
    UsageStrategy: Optional[UsageStrategy] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "UsageStrategy": self.UsageStrategy.value if self.UsageStrategy else None,
        }


@dataclass
class OnDemandOptionsRequest:
    AllocationStrategy: Optional[OnDemandAllocationStrategy] = None
    CapacityReservationOptions: Optional[CapacityReservationOptionsRequest] = None
    MaxTotalPrice: Optional[str] = None
    MinTargetCapacity: Optional[int] = None
    SingleAvailabilityZone: Optional[bool] = None
    SingleInstanceType: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationStrategy": self.AllocationStrategy.value if self.AllocationStrategy else None,
            "CapacityReservationOptions": self.CapacityReservationOptions.to_dict() if self.CapacityReservationOptions else None,
            "MaxTotalPrice": self.MaxTotalPrice,
            "MinTargetCapacity": self.MinTargetCapacity,
            "SingleAvailabilityZone": self.SingleAvailabilityZone,
            "SingleInstanceType": self.SingleInstanceType,
        }


@dataclass
class FleetSpotCapacityRebalanceRequest:
    ReplacementStrategy: Optional[ReplacementStrategy] = None
    TerminationDelay: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ReplacementStrategy": self.ReplacementStrategy.value if self.ReplacementStrategy else None,
            "TerminationDelay": self.TerminationDelay,
        }


@dataclass
class FleetSpotMaintenanceStrategiesRequest:
    CapacityRebalance: Optional[FleetSpotCapacityRebalanceRequest] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CapacityRebalance": self.CapacityRebalance.to_dict() if self.CapacityRebalance else None,
        }


@dataclass
class SpotOptionsRequest:
    AllocationStrategy: Optional[SpotAllocationStrategy] = None
    InstanceInterruptionBehavior: Optional[InstanceInterruptionBehavior] = None
    InstancePoolsToUseCount: Optional[int] = None
    MaintenanceStrategies: Optional[FleetSpotMaintenanceStrategiesRequest] = None
    MaxTotalPrice: Optional[str] = None
    MinTargetCapacity: Optional[int] = None
    SingleAvailabilityZone: Optional[bool] = None
    SingleInstanceType: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationStrategy": self.AllocationStrategy.value if self.AllocationStrategy else None,
            "InstanceInterruptionBehavior": self.InstanceInterruptionBehavior.value if self.InstanceInterruptionBehavior else None,
            "InstancePoolsToUseCount": self.InstancePoolsToUseCount,
            "MaintenanceStrategies": self.MaintenanceStrategies.to_dict() if self.MaintenanceStrategies else None,
            "MaxTotalPrice": self.MaxTotalPrice,
            "MinTargetCapacity": self.MinTargetCapacity,
            "SingleAvailabilityZone": self.SingleAvailabilityZone,
            "SingleInstanceType": self.SingleInstanceType,
        }


@dataclass
class TargetCapacitySpecificationRequest:
    TotalTargetCapacity: int
    DefaultTargetCapacityType: Optional[str] = None  # spot | on-demand | capacity-block
    OnDemandTargetCapacity: Optional[int] = None
    SpotTargetCapacity: Optional[int] = None
    TargetCapacityUnitType: Optional[str] = None  # vcpu | memory-mib | units

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TotalTargetCapacity": self.TotalTargetCapacity,
            "DefaultTargetCapacityType": self.DefaultTargetCapacityType,
            "OnDemandTargetCapacity": self.OnDemandTargetCapacity,
            "SpotTargetCapacity": self.SpotTargetCapacity,
            "TargetCapacityUnitType": self.TargetCapacityUnitType,
        }


@dataclass
class Placement:
    Affinity: Optional[str] = None
    AvailabilityZone: Optional[str] = None
    AvailabilityZoneId: Optional[str] = None
    GroupId: Optional[str] = None
    GroupName: Optional[str] = None
    HostId: Optional[str] = None
    HostResourceGroupArn: Optional[str] = None
    PartitionNumber: Optional[int] = None
    SpreadDomain: Optional[str] = None
    Tenancy: Optional[str] = None  # default | dedicated | host

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Affinity": self.Affinity,
            "AvailabilityZone": self.AvailabilityZone,
            "AvailabilityZoneId": self.AvailabilityZoneId,
            "GroupId": self.GroupId,
            "GroupName": self.GroupName,
            "HostId": self.HostId,
            "HostResourceGroupArn": self.HostResourceGroupArn,
            "PartitionNumber": self.PartitionNumber,
            "SpreadDomain": self.SpreadDomain,
            "Tenancy": self.Tenancy,
        }

    def create_fleet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Validate required parameters
        launch_template_configs = params.get("LaunchTemplateConfigs.N")
        target_capacity_spec = params.get("TargetCapacitySpecification")
        if not launch_template_configs:
            raise ValueError("LaunchTemplateConfigs.N is required")
        if not target_capacity_spec:
            raise ValueError("TargetCapacitySpecification is required")
        total_target_capacity = target_capacity_spec.get("TotalTargetCapacity")
        if total_target_capacity is None:
            raise ValueError("TargetCapacitySpecification.TotalTargetCapacity is required")

        # Generate fleet ID and request ID
        fleet_id = self.generate_unique_id(prefix="fleet-")
        request_id = self.generate_request_id()

        # Extract optional parameters
        client_token = params.get("ClientToken")
        context = params.get("Context")
        dry_run = params.get("DryRun", False)
        excess_capacity_termination_policy = params.get("ExcessCapacityTerminationPolicy")
        on_demand_options = params.get("OnDemandOptions")
        replace_unhealthy_instances = params.get("ReplaceUnhealthyInstances", False)
        spot_options = params.get("SpotOptions")
        tag_specifications = params.get("TagSpecification.N", [])
        terminate_instances_with_expiration = params.get("TerminateInstancesWithExpiration", False)
        fleet_type = params.get("Type", "maintain")
        valid_from = params.get("ValidFrom")
        valid_until = params.get("ValidUntil")

        # Validate fleet_type
        valid_fleet_types = {"request", "maintain", "instant"}
        if fleet_type and fleet_type not in valid_fleet_types:
            raise ValueError(f"Invalid Type value: {fleet_type}")

        # Validate ExcessCapacityTerminationPolicy only for maintain type
        if excess_capacity_termination_policy and fleet_type != "maintain":
            raise ValueError("ExcessCapacityTerminationPolicy is supported only for fleets of type 'maintain'")

        # Validate ReplaceUnhealthyInstances only for maintain type
        if replace_unhealthy_instances and fleet_type != "maintain":
            raise ValueError("ReplaceUnhealthyInstances is supported only for fleets of type 'maintain'")

        # Validate TagSpecification resource types
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if fleet_type == "instant":
                if resource_type not in ("fleet", "instance"):
                    raise ValueError("For instant fleets, ResourceType must be 'fleet' or 'instance'")
            elif fleet_type in ("maintain", "request"):
                if resource_type != "fleet":
                    raise ValueError("For maintain or request fleets, ResourceType must be 'fleet'")

        # Prepare tags dictionary from tag_specifications
        tags = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None:
                    tags.append({"Key": key, "Value": value})

        # Store fleet data in state
        fleet_data = {
            "FleetId": fleet_id,
            "ClientToken": client_token,
            "Context": context,
            "ExcessCapacityTerminationPolicy": excess_capacity_termination_policy,
            "LaunchTemplateConfigs": launch_template_configs,
            "OnDemandOptions": on_demand_options,
            "ReplaceUnhealthyInstances": replace_unhealthy_instances,
            "SpotOptions": spot_options,
            "TagSpecifications": tag_specifications,
            "Tags": tags,
            "TargetCapacitySpecification": target_capacity_spec,
            "TerminateInstancesWithExpiration": terminate_instances_with_expiration,
            "Type": fleet_type,
            "ValidFrom": valid_from,
            "ValidUntil": valid_until,
            "CreateTime": datetime.datetime.utcnow().isoformat() + "Z",
            "State": "active",
            "RequestId": request_id,
            "Instances": [],  # List of launched instances (simulate)
            "Errors": [],  # List of errors for instant fleets
        }

        # Save fleet data in shared state dictionary
        self.state.ec2_fleet[fleet_id] = fleet_data
        self.state.resources[fleet_id] = fleet_data

        # Simulate instance launching for instant and maintain fleets
        # For instant, launch immediately and report errors if any
        # For maintain, just mark as active, no immediate launch simulation here
        error_set = []
        fleet_instance_set = []

        if fleet_type in ("instant", "maintain", "request"):
            # For simplicity, simulate instance launching for instant and maintain fleets
            # We will create dummy instance IDs for the total target capacity
            # In real implementation, would consider launch templates, overrides, etc.
            instance_count = total_target_capacity
            for i in range(instance_count):
                instance_id = self.generate_unique_id(prefix="i-")
                instance_type = None
                # Try to get instance type from first launch template override if available
                first_lt_config = launch_template_configs[0] if launch_template_configs else None
                if first_lt_config:
                    overrides = first_lt_config.get("Overrides", [])
                    if overrides:
                        instance_type = overrides[0].get("InstanceType")
                    else:
                        # If no overrides, instance type might be in launch template (not implemented here)
                        instance_type = None
                instance_info = {
                    "InstanceId": instance_id,
                    "InstanceType": instance_type,
                    "Lifecycle": "on-demand" if fleet_type != "instant" else "spot",
                    "Platform": "",  # Could be "windows" if specified, else blank
                }
                fleet_instance_set.append(instance_info)
                fleet_data["Instances"].append(instance_info)

        # Prepare response
        response = {
            "FleetId": fleet_id,
            "RequestId": request_id,
            "ErrorSet": error_set,
            "FleetInstanceSet": fleet_instance_set,
        }

        return response


    def delete_fleets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        fleet_ids = params.get("FleetId.N")
        terminate_instances = params.get("TerminateInstances")
        if not fleet_ids:
            raise ValueError("FleetId.N is required")
        if terminate_instances is None:
            raise ValueError("TerminateInstances is required")

        dry_run = params.get("DryRun", False)
        request_id = self.generate_request_id()

        successful_fleet_deletion_set = []
        unsuccessful_fleet_deletion_set = []

        for fleet_id in fleet_ids:
            fleet = self.state.ec2_fleet.get(fleet_id)
            if not fleet:
                # Fleet does not exist
                error_item = {
                    "Error": {
                        "Code": "fleetIdDoesNotExist",
                        "Message": f"Fleet ID {fleet_id} does not exist",
                    },
                    "FleetId": fleet_id,
                }
                unsuccessful_fleet_deletion_set.append(error_item)
                continue

            # Check if fleet is in deletable state
            deletable_states = {"submitted", "active", "modifying"}
            current_state = fleet.get("State", "active")
            if current_state not in deletable_states:
                error_item = {
                    "Error": {
                        "Code": "fleetNotInDeletableState",
                        "Message": f"Fleet ID {fleet_id} is not in a deletable state",
                    },
                    "FleetId": fleet_id,
                }
                unsuccessful_fleet_deletion_set.append(error_item)
                continue

            # Update fleet state based on terminate_instances
            previous_state = current_state
            if terminate_instances:
                fleet["State"] = "deleted_terminating"
                # Simulate terminating instances
                fleet["Instances"] = []
            else:
                fleet["State"] = "deleted_running"
                # Instances continue to run

            successful_fleet_deletion_set.append({
                "CurrentFleetState": fleet["State"],
                "FleetId": fleet_id,
                "PreviousFleetState": previous_state,
            })

        response = {
            "RequestId": request_id,
            "SuccessfulFleetDeletionSet": successful_fleet_deletion_set,
            "UnsuccessfulFleetDeletionSet": unsuccessful_fleet_deletion_set,
        }
        return response


    def describe_fleet_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        fleet_id = params.get("FleetId")
        start_time = params.get("StartTime")
        if not fleet_id:
            raise ValueError("FleetId is required")
        if not start_time:
            raise ValueError("StartTime is required")

        dry_run = params.get("DryRun", False)
        event_type = params.get("EventType")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        request_id = self.generate_request_id()

        fleet = self.state.ec2_fleet.get(fleet_id)
        if not fleet:
            raise ValueError(f"Fleet ID {fleet_id} does not exist")

        # For simplicity, simulate empty history as no events stored
        # In real implementation, would track events with timestamps and types
        history_record_set = []

        # lastEvaluatedTime is the latest event time returned, here None as no events
        last_evaluated_time = None
        next_token_out = None

        response = {
            "FleetId": fleet_id,
            "HistoryRecordSet": history_record_set,
            "LastEvaluatedTime": last_evaluated_time,
            "NextToken": next_token_out,
            "RequestId": request_id,
            "StartTime": start_time,
        }
        return response


    def describe_fleet_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        fleet_id = params.get("FleetId")
        if not fleet_id:
            raise ValueError("FleetId is required")

        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        request_id = self.generate_request_id()

        fleet = self.state.ec2_fleet.get(fleet_id)
        if not fleet:
            raise ValueError(f"Fleet ID {fleet_id} does not exist")

        # Currently, DescribeFleetInstances does not support instant fleets
        if fleet.get("Type") == "instant":
            raise ValueError("DescribeFleetInstances does not support fleets of type 'instant'")

        # Get running instances from fleet
        instances = fleet.get("Instances", [])

        # Apply filters if any
        def instance_matches_filters(instance):
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name == "instance-type":
                    if instance.get("InstanceType") not in values:
                        return False
                # Add other filters as needed
            return True

        filtered_instances = [inst for inst in instances if instance_matches_filters(inst)]

        # Pagination support (not fully implemented, just simulate)
        if max_results is not None:
            filtered_instances = filtered_instances[:max_results]
            next_token_out = None  # No pagination token implemented
        else:
            next_token_out = None

        # Prepare activeInstanceSet response
        active_instance_set = []
        for inst in filtered_instances:
            active_instance_set.append({
                "InstanceId": inst.get("InstanceId"),
                "InstanceType": inst.get("InstanceType"),
                "InstanceHealth": "healthy",  # Simulate healthy
                "SpotInstanceRequestId": None,  # Not simulated
            })

        response = {
            "ActiveInstanceSet": active_instance_set,
            "FleetId": fleet_id,
            "NextToken": next_token_out,
            "RequestId": request_id,
        }
        return response


    def describe_fleets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        fleet_ids = params.get("FleetId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        request_id = self.generate_request_id()

        # Collect fleets to describe
        if fleet_ids:
            fleets_to_describe = [self.state.ec2_fleet.get(fid) for fid in fleet_ids if fid in self.state.ec2_fleet]
        else:
            fleets_to_describe = list(self.state.ec2_fleet.values())

        # Apply filters
        def fleet_matches_filters(fleet):
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name == "activity-status":
                    # Map fleet state to activity status
                    state = fleet.get("State", "active")
                    # Map states to activity status
                    state_map = {
                        "error": "error",
                        "submitted": "pending_fulfillment",
                        "active": "fulfilled",
                        "deleted": "deleted",
                        "deleted_running": "deleted_running",
                        "deleted_terminating": "deleted_terminating",
                        "modifying": "modifying",
                    }
                    activity_status = state_map.get(state, "pending_fulfillment")
                    if activity_status not in values:
                        return False
                elif name == "excess-capacity-termination-policy":
                    if fleet.get("ExcessCapacityTerminationPolicy") not in values:
                        return False
                elif name == "fleet-state":
                    if fleet.get("State") not in values:
                        return False
                elif name == "replace-unhealthy-instances":
                    val = fleet.get("ReplaceUnhealthyInstances", False)
                    str_val = "true" if val else "false"
                    if str_val not in values:
                        return False
                elif name == "type":
                    if fleet.get("Type") not in values:
                        return False
                # Add other filters as needed
            return True

        filtered_fleets = [f for f in fleets_to_describe if f and fleet_matches_filters(f)]

        # Pagination support (not fully implemented)
        if max_results is not None:
            filtered_fleets = filtered_fleets[:max_results]
            next_token_out = None
        else:
            next_token_out = None

        # Prepare fleetSet response
        fleet_set = []
        for fleet in filtered_fleets:
            # Compose fleet data response
            fleet_info = {
                "ActivityStatus": None,
                "ClientToken": fleet.get("ClientToken"),
                "Context": fleet.get("Context"),
                "CreateTime": fleet.get("CreateTime"),
                "ErrorSet": fleet.get("Errors", []),
                "ExcessCapacityTerminationPolicy": fleet.get("ExcessCapacityTerminationPolicy"),
                "FleetId": fleet.get("FleetId"),
                "FleetInstanceSet": [],  # For instant fleets, instances info
                "FleetState": fleet.get("State"),
                "FulfilledCapacity": None,
                "FulfilledOnDemandCapacity": None,
                "LaunchTemplateConfigs": fleet.get("LaunchTemplateConfigs"),
                "OnDemandOptions": fleet.get("OnDemandOptions"),
                "ReplaceUnhealthyInstances": fleet.get("ReplaceUnhealthyInstances"),
                "SpotOptions": fleet.get("SpotOptions"),
                "TagSet": fleet.get("Tags"),
                "TargetCapacitySpecification": fleet.get("TargetCapacitySpecification"),
                "TerminateInstancesWithExpiration": fleet.get("TerminateInstancesWithExpiration"),
                "Type": fleet.get("Type"),
                "ValidFrom": fleet.get("ValidFrom"),
                "ValidUntil": fleet.get("ValidUntil"),
            }
            # Map fleet state to activity status
            state = fleet.get("State", "active")
            state_map = {
                "error": "error",
                "submitted": "pending_fulfillment",
                "active": "fulfilled",
                "deleted": "deleted",
                "deleted_running": "deleted_running",
                "deleted_terminating": "deleted_terminating",
                "modifying": "modifying",
            }
            fleet_info["ActivityStatus"] = state_map.get(state, "pending_fulfillment")

            # For instant fleets, include fleetInstanceSet
            if fleet.get("Type") == "instant":
                instances = fleet.get("Instances", [])
                fleet_instance_set = []
                for inst in instances:
                    fleet_instance_set.append({
                        "InstanceIds": [inst.get("InstanceId")],
                        "InstanceType": inst.get("InstanceType"),
                        "LaunchTemplateAndOverrides": None,
                        "Lifecycle": inst.get("Lifecycle"),
                        "Platform": inst.get("Platform"),
                    })
                fleet_info["FleetInstanceSet"] = fleet_instance_set

            fleet_set.append(fleet_info)

        response = {
            "FleetSet": fleet_set,
            "NextToken": next_token_out,
            "RequestId": request_id,
        }
        return response

    def modify_fleet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        fleet_id = params.get("FleetId")
        if not fleet_id:
            raise Exception("Missing required parameter FleetId")

        # Retrieve the fleet from state
        fleet = self.state.ec2_fleet.get(fleet_id)
        if not fleet:
            raise Exception(f"Fleet with id {fleet_id} not found")

        # Only fleets of type 'maintain' can be modified
        if fleet.get("Type") != "maintain":
            raise Exception("Only fleets of type 'maintain' can be modified")

        # If fleet is currently modifying, reject concurrent modification
        if fleet.get("State") == "modifying":
            raise Exception("Fleet is currently in modifying state")

        # Validate DryRun parameter
        dry_run = params.get("DryRun", False)
        if dry_run:
            # Here we would check permissions, but for emulator just raise DryRunOperation
            raise Exception("DryRunOperation")

        # Begin modification: set state to modifying
        fleet["State"] = "modifying"

        # Update ExcessCapacityTerminationPolicy if provided
        excess_policy = params.get("ExcessCapacityTerminationPolicy")
        if excess_policy is not None:
            if excess_policy not in ["no-termination", "termination"]:
                raise Exception("Invalid ExcessCapacityTerminationPolicy value")
            fleet["ExcessCapacityTerminationPolicy"] = excess_policy

        # Update LaunchTemplateConfig if provided
        launch_template_configs = params.get("LaunchTemplateConfig.N")
        if launch_template_configs is not None:
            if not isinstance(launch_template_configs, list):
                raise Exception("LaunchTemplateConfig.N must be a list")
            if len(launch_template_configs) > 50:
                raise Exception("LaunchTemplateConfig.N cannot have more than 50 items")

            # Validate each FleetLaunchTemplateConfigRequest object
            validated_configs = []
            for config in launch_template_configs:
                validated_config = {}

                # Validate LaunchTemplateSpecification if present
                lts = config.get("LaunchTemplateSpecification")
                if lts is not None:
                    if not isinstance(lts, dict):
                        raise Exception("LaunchTemplateSpecification must be a dict")
                    lt_id = lts.get("LaunchTemplateId")
                    lt_name = lts.get("LaunchTemplateName")
                    if lt_id and lt_name:
                        raise Exception("Specify either LaunchTemplateId or LaunchTemplateName, not both")
                    if not lt_id and not lt_name:
                        # According to docs, not required, but if present must specify one
                        pass
                    version = lts.get("Version")
                    # Version can be None, $Latest, $Default or a string number
                    if version is not None and not isinstance(version, str):
                        raise Exception("Version must be a string if specified")
                    validated_config["LaunchTemplateSpecification"] = {
                        "LaunchTemplateId": lt_id,
                        "LaunchTemplateName": lt_name,
                        "Version": version,
                    }

                # Validate Overrides if present
                overrides = config.get("Overrides")
                if overrides is not None:
                    if not isinstance(overrides, list):
                        raise Exception("Overrides must be a list")
                    if len(overrides) > 300:
                        raise Exception("Overrides cannot have more than 300 items across all launch templates")
                    validated_overrides = []
                    for override in overrides:
                        if not isinstance(override, dict):
                            raise Exception("Each override must be a dict")
                        validated_override = {}

                        # Validate fields in override
                        # AvailabilityZone
                        az = override.get("AvailabilityZone")
                        if az is not None and not isinstance(az, str):
                            raise Exception("AvailabilityZone must be a string")

                        # BlockDeviceMappings
                        bdm = override.get("BlockDeviceMappings")
                        if bdm is not None:
                            if not isinstance(bdm, list):
                                raise Exception("BlockDeviceMappings must be a list")
                            validated_bdms = []
                            for bdm_item in bdm:
                                if not isinstance(bdm_item, dict):
                                    raise Exception("Each BlockDeviceMapping must be a dict")
                                validated_bdm = {}

                                device_name = bdm_item.get("DeviceName")
                                if device_name is not None and not isinstance(device_name, str):
                                    raise Exception("DeviceName must be a string")
                                validated_bdm["DeviceName"] = device_name

                                ebs = bdm_item.get("Ebs")
                                if ebs is not None:
                                    if not isinstance(ebs, dict):
                                        raise Exception("Ebs must be a dict")
                                    # Validate Ebs fields
                                    validated_ebs = {}
                                    for key in [
                                        "DeleteOnTermination",
                                        "Encrypted",
                                        "Iops",
                                        "KmsKeyId",
                                        "SnapshotId",
                                        "Throughput",
                                        "VolumeSize",
                                        "VolumeType",
                                    ]:
                                        val = ebs.get(key)
                                        if val is not None:
                                            validated_ebs[key] = val
                                    validated_bdm["Ebs"] = validated_ebs

                                no_device = bdm_item.get("NoDevice")
                                if no_device is not None and not isinstance(no_device, str):
                                    raise Exception("NoDevice must be a string")
                                validated_bdm["NoDevice"] = no_device

                                virtual_name = bdm_item.get("VirtualName")
                                if virtual_name is not None and not isinstance(virtual_name, str):
                                    raise Exception("VirtualName must be a string")
                                validated_bdm["VirtualName"] = virtual_name

                                validated_bdms.append(validated_bdm)
                            validated_override["BlockDeviceMappings"] = validated_bdms

                        # ImageId
                        image_id = override.get("ImageId")
                        if image_id is not None and not isinstance(image_id, str):
                            raise Exception("ImageId must be a string")
                        validated_override["ImageId"] = image_id

                        # InstanceRequirements
                        inst_req = override.get("InstanceRequirements")
                        if inst_req is not None:
                            if not isinstance(inst_req, dict):
                                raise Exception("InstanceRequirements must be a dict")
                            # For brevity, accept as is (deep validation can be added if needed)
                            validated_override["InstanceRequirements"] = inst_req

                        # InstanceType
                        inst_type = override.get("InstanceType")
                        if inst_type is not None and not isinstance(inst_type, str):
                            raise Exception("InstanceType must be a string")
                        validated_override["InstanceType"] = inst_type

                        # MaxPrice
                        max_price = override.get("MaxPrice")
                        if max_price is not None and not isinstance(max_price, str):
                            raise Exception("MaxPrice must be a string")
                        validated_override["MaxPrice"] = max_price

                        # Placement
                        placement = override.get("Placement")
                        if placement is not None:
                            if not isinstance(placement, dict):
                                raise Exception("Placement must be a dict")
                            validated_override["Placement"] = placement

                        # Priority
                        priority = override.get("Priority")
                        if priority is not None:
                            if not (isinstance(priority, float) or isinstance(priority, int)):
                                raise Exception("Priority must be a number")
                            validated_override["Priority"] = float(priority)

                        # SubnetId
                        subnet_id = override.get("SubnetId")
                        if subnet_id is not None and not isinstance(subnet_id, str):
                            raise Exception("SubnetId must be a string")
                        validated_override["SubnetId"] = subnet_id

                        # WeightedCapacity
                        weighted_capacity = override.get("WeightedCapacity")
                        if weighted_capacity is not None:
                            if not (isinstance(weighted_capacity, float) or isinstance(weighted_capacity, int)):
                                raise Exception("WeightedCapacity must be a number")
                            validated_override["WeightedCapacity"] = float(weighted_capacity)

                        # AvailabilityZone
                        validated_override["AvailabilityZone"] = az

                        validated_overrides.append(validated_override)
                    validated_config["Overrides"] = validated_overrides

                validated_configs.append(validated_config)
            fleet["LaunchTemplateConfig"] = validated_configs

        # Update TargetCapacitySpecification if provided
        target_capacity_spec = params.get("TargetCapacitySpecification")
        if target_capacity_spec is not None:
            if not isinstance(target_capacity_spec, dict):
                raise Exception("TargetCapacitySpecification must be a dict")
            # Validate required TotalTargetCapacity
            total_target_capacity = target_capacity_spec.get("TotalTargetCapacity")
            if total_target_capacity is None or not isinstance(total_target_capacity, int):
                raise Exception("TargetCapacitySpecification.TotalTargetCapacity is required and must be int")
            # Validate optional fields
            default_target_capacity_type = target_capacity_spec.get("DefaultTargetCapacityType")
            if default_target_capacity_type is not None and default_target_capacity_type not in ["spot", "on-demand", "capacity-block"]:
                raise Exception("Invalid DefaultTargetCapacityType value")
            on_demand_target_capacity = target_capacity_spec.get("OnDemandTargetCapacity")
            if on_demand_target_capacity is not None and not isinstance(on_demand_target_capacity, int):
                raise Exception("OnDemandTargetCapacity must be int if specified")
            spot_target_capacity = target_capacity_spec.get("SpotTargetCapacity")
            if spot_target_capacity is not None and not isinstance(spot_target_capacity, int):
                raise Exception("SpotTargetCapacity must be int if specified")
            target_capacity_unit_type = target_capacity_spec.get("TargetCapacityUnitType")
            if target_capacity_unit_type is not None and target_capacity_unit_type not in ["vcpu", "memory-mib", "units"]:
                raise Exception("Invalid TargetCapacityUnitType value")

            # Update fleet target capacity specification
            fleet["TargetCapacitySpecification"] = {
                "TotalTargetCapacity": total_target_capacity,
                "DefaultTargetCapacityType": default_target_capacity_type,
                "OnDemandTargetCapacity": on_demand_target_capacity,
                "SpotTargetCapacity": spot_target_capacity,
                "TargetCapacityUnitType": target_capacity_unit_type,
            }

        # Modification complete, set state back to active
        fleet["State"] = "active"

        # Save updated fleet back to state
        self.state.ec2_fleet[fleet_id] = fleet

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class EC2FleetGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateFleet", self.create_fleet)
        self.register_action("DeleteFleets", self.delete_fleets)
        self.register_action("DescribeFleetHistory", self.describe_fleet_history)
        self.register_action("DescribeFleetInstances", self.describe_fleet_instances)
        self.register_action("DescribeFleets", self.describe_fleets)
        self.register_action("ModifyFleet", self.modify_fleet)

    def create_fleet(self, params):
        return self.backend.create_fleet(params)

    def delete_fleets(self, params):
        return self.backend.delete_fleets(params)

    def describe_fleet_history(self, params):
        return self.backend.describe_fleet_history(params)

    def describe_fleet_instances(self, params):
        return self.backend.describe_fleet_instances(params)

    def describe_fleets(self, params):
        return self.backend.describe_fleets(params)

    def modify_fleet(self, params):
        return self.backend.modify_fleet(params)
