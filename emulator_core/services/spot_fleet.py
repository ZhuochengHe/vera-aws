from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class SpotFleetRequestState(str, Enum):
    SUBMITTED = "submitted"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    FAILED = "failed"
    CANCELLED_RUNNING = "cancelled_running"
    CANCELLED_TERMINATING = "cancelled_terminating"
    MODIFYING = "modifying"


class SpotFleetRequestActivityStatus(str, Enum):
    ERROR = "error"
    PENDING_FULFILLMENT = "pending_fulfillment"
    PENDING_TERMINATION = "pending_termination"
    FULFILLED = "fulfilled"


class SpotFleetRequestType(str, Enum):
    REQUEST = "request"
    MAINTAIN = "maintain"
    INSTANT = "instant"  # Listed but not used by Spot Fleet


class SpotInstanceInterruptionBehavior(str, Enum):
    HIBERNATE = "hibernate"
    STOP = "stop"
    TERMINATE = "terminate"


class SpotAllocationStrategy(str, Enum):
    LOWEST_PRICE = "lowestPrice"
    DIVERSIFIED = "diversified"
    CAPACITY_OPTIMIZED = "capacityOptimized"
    CAPACITY_OPTIMIZED_PRIORITIZED = "capacityOptimizedPrioritized"
    PRICE_CAPACITY_OPTIMIZED = "priceCapacityOptimized"


class OnDemandAllocationStrategy(str, Enum):
    LOWEST_PRICE = "lowestPrice"
    PRIORITIZED = "prioritized"


class ExcessCapacityTerminationPolicy(str, Enum):
    NO_TERMINATION = "noTermination"
    DEFAULT = "default"


class SpotFleetReplacementStrategy(str, Enum):
    LAUNCH = "launch"
    LAUNCH_BEFORE_TERMINATE = "launch-before-terminate"


class SpotFleetEventType(str, Enum):
    INSTANCE_CHANGE = "instanceChange"
    FLEET_REQUEST_CHANGE = "fleetRequestChange"
    ERROR = "error"
    INFORMATION = "information"


@dataclass
class CancelSpotFleetRequestsError:
    code: Optional[str] = None  # Valid Values: fleetRequestIdDoesNotExist | fleetRequestIdMalformed | fleetRequestNotInCancellableState | unexpectedError
    message: Optional[str] = None


@dataclass
class CancelSpotFleetRequestsErrorItem:
    error: Optional[CancelSpotFleetRequestsError] = None
    spot_fleet_request_id: Optional[str] = None


@dataclass
class CancelSpotFleetRequestsSuccessItem:
    current_spot_fleet_request_state: Optional[SpotFleetRequestState] = None
    previous_spot_fleet_request_state: Optional[SpotFleetRequestState] = None
    spot_fleet_request_id: Optional[str] = None


@dataclass
class ActiveInstance:
    instance_health: Optional[str] = None  # healthy | unhealthy
    instance_id: Optional[str] = None
    instance_type: Optional[str] = None
    spot_instance_request_id: Optional[str] = None


@dataclass
class EventInformation:
    event_description: Optional[str] = None
    event_sub_type: Optional[str] = None  # see detailed valid values in resource JSON
    instance_id: Optional[str] = None


@dataclass
class HistoryRecord:
    event_information: Optional[EventInformation] = None
    event_type: Optional[SpotFleetEventType] = None
    timestamp: Optional[datetime] = None


@dataclass
class Tag:
    Key: Optional[str] = None
    Value: Optional[str] = None


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class SpotFleetTagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class GroupIdentifier:
    GroupId: Optional[str] = None
    GroupName: Optional[str] = None


@dataclass
class IamInstanceProfileSpecification:
    Arn: Optional[str] = None
    Name: Optional[str] = None


@dataclass
class EbsBlockDevice:
    AvailabilityZone: Optional[str] = None
    AvailabilityZoneId: Optional[str] = None
    DeleteOnTermination: Optional[bool] = None
    Encrypted: Optional[bool] = None
    Iops: Optional[int] = None
    KmsKeyId: Optional[str] = None
    OutpostArn: Optional[str] = None
    SnapshotId: Optional[str] = None
    Throughput: Optional[int] = None
    VolumeInitializationRate: Optional[int] = None
    VolumeSize: Optional[int] = None
    VolumeType: Optional[str] = None


@dataclass
class BlockDeviceMapping:
    DeviceName: Optional[str] = None
    Ebs: Optional[EbsBlockDevice] = None
    NoDevice: Optional[str] = None
    VirtualName: Optional[str] = None


@dataclass
class SpotFleetMonitoring:
    Enabled: Optional[bool] = False


@dataclass
class InstanceIpv6Address:
    Ipv6Address: Optional[str] = None
    IsPrimaryIpv6: Optional[bool] = None


@dataclass
class Ipv4PrefixSpecificationRequest:
    Ipv4Prefix: Optional[str] = None


@dataclass
class Ipv6PrefixSpecificationRequest:
    Ipv6Prefix: Optional[str] = None


@dataclass
class PrivateIpAddressSpecification:
    Primary: Optional[bool] = None
    PrivateIpAddress: Optional[str] = None


@dataclass
class EnaSrdUdpSpecificationRequest:
    # Placeholder for fields if needed
    pass


@dataclass
class EnaSrdSpecificationRequest:
    EnaSrdEnabled: Optional[bool] = None
    EnaSrdUdpSpecification: Optional[EnaSrdUdpSpecificationRequest] = None


@dataclass
class InstanceNetworkInterfaceSpecification:
    AssociateCarrierIpAddress: Optional[bool] = None
    AssociatePublicIpAddress: Optional[bool] = None
    ConnectionTrackingSpecification: Optional[Dict[str, Any]] = None  # Simplified
    DeleteOnTermination: Optional[bool] = None
    Description: Optional[str] = None
    DeviceIndex: Optional[int] = None
    EnaQueueCount: Optional[int] = None
    EnaSrdSpecification: Optional[EnaSrdSpecificationRequest] = None
    InterfaceType: Optional[str] = None  # interface|efa|efa-only
    Ipv4Prefixes: List[Ipv4PrefixSpecificationRequest] = field(default_factory=list)
    Ipv4PrefixCount: Optional[int] = None
    Ipv6AddressCount: Optional[int] = None
    Ipv6Addresses: List[InstanceIpv6Address] = field(default_factory=list)
    Ipv6Prefixes: List[Ipv6PrefixSpecificationRequest] = field(default_factory=list)
    Ipv6PrefixCount: Optional[int] = None
    NetworkCardIndex: Optional[int] = None
    NetworkInterfaceId: Optional[str] = None
    PrimaryIpv6: Optional[bool] = None
    PrivateIpAddress: Optional[str] = None
    PrivateIpAddresses: List[PrivateIpAddressSpecification] = field(default_factory=list)
    SecondaryPrivateIpAddressCount: Optional[int] = None
    Groups: List[str] = field(default_factory=list)
    SubnetId: Optional[str] = None


@dataclass
class SpotPlacement:
    AvailabilityZone: Optional[str] = None
    GroupName: Optional[str] = None
    Tenancy: Optional[str] = None  # default | dedicated | host


@dataclass
class SpotFleetTagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class SpotFleetLaunchSpecification:
    AddressingType: Optional[str] = None
    BlockDeviceMappings: List[BlockDeviceMapping] = field(default_factory=list)
    EbsOptimized: Optional[bool] = False
    SecurityGroups: List[GroupIdentifier] = field(default_factory=list)
    IamInstanceProfile: Optional[IamInstanceProfileSpecification] = None
    ImageId: Optional[str] = None
    InstanceRequirements: Optional[Dict[str, Any]] = None  # Simplified
    InstanceType: Optional[str] = None
    KernelId: Optional[str] = None
    KeyName: Optional[str] = None
    Monitoring: Optional[SpotFleetMonitoring] = None
    NetworkInterfaces: List[InstanceNetworkInterfaceSpecification] = field(default_factory=list)
    Placement: Optional[SpotPlacement] = None
    RamdiskId: Optional[str] = None
    SpotPrice: Optional[str] = None
    SubnetId: Optional[str] = None
    TagSpecifications: List[SpotFleetTagSpecification] = field(default_factory=list)
    UserData: Optional[str] = None
    WeightedCapacity: Optional[float] = None


@dataclass
class ClassicLoadBalancer:
    Name: Optional[str] = None


@dataclass
class ClassicLoadBalancersConfig:
    ClassicLoadBalancers: List[ClassicLoadBalancer] = field(default_factory=list)


@dataclass
class TargetGroup:
    Arn: Optional[str] = None


@dataclass
class TargetGroupsConfig:
    TargetGroups: List[TargetGroup] = field(default_factory=list)


@dataclass
class LoadBalancersConfig:
    ClassicLoadBalancersConfig: Optional[ClassicLoadBalancersConfig] = None
    TargetGroupsConfig: Optional[TargetGroupsConfig] = None


@dataclass
class FleetLaunchTemplateSpecification:
    LaunchTemplateId: Optional[str] = None
    LaunchTemplateName: Optional[str] = None
    Version: Optional[str] = None


@dataclass
class LaunchTemplateOverrides:
    AvailabilityZone: Optional[str] = None
    InstanceRequirements: Optional[Dict[str, Any]] = None  # Simplified
    InstanceType: Optional[str] = None
    Priority: Optional[float] = None
    SpotPrice: Optional[str] = None
    SubnetId: Optional[str] = None
    WeightedCapacity: Optional[float] = None


@dataclass
class LaunchTemplateConfig:
    LaunchTemplateSpecification: Optional[FleetLaunchTemplateSpecification] = None
    Overrides: List[LaunchTemplateOverrides] = field(default_factory=list)


@dataclass
class SpotCapacityRebalance:
    ReplacementStrategy: Optional[SpotFleetReplacementStrategy] = None
    TerminationDelay: Optional[int] = None  # seconds


@dataclass
class SpotMaintenanceStrategies:
    CapacityRebalance: Optional[SpotCapacityRebalance] = None


@dataclass
class SpotFleetRequestConfigData:
    IamFleetRole: str
    TargetCapacity: int
    AllocationStrategy: Optional[SpotAllocationStrategy] = None
    ClientToken: Optional[str] = None
    Context: Optional[str] = None
    ExcessCapacityTerminationPolicy: Optional[ExcessCapacityTerminationPolicy] = None
    FulfilledCapacity: Optional[float] = None
    InstanceInterruptionBehavior: Optional[SpotInstanceInterruptionBehavior] = None
    InstancePoolsToUseCount: Optional[int] = None
    LaunchSpecifications: List[SpotFleetLaunchSpecification] = field(default_factory=list)
    LaunchTemplateConfigs: List[LaunchTemplateConfig] = field(default_factory=list)
    LoadBalancersConfig: Optional[LoadBalancersConfig] = None
    OnDemandAllocationStrategy: Optional[OnDemandAllocationStrategy] = None
    OnDemandFulfilledCapacity: Optional[float] = None
    OnDemandMaxTotalPrice: Optional[str] = None
    OnDemandTargetCapacity: Optional[int] = None
    ReplaceUnhealthyInstances: Optional[bool] = None
    SpotMaintenanceStrategies: Optional[SpotMaintenanceStrategies] = None
    SpotMaxTotalPrice: Optional[str] = None
    SpotPrice: Optional[str] = None
    TagSpecifications: List[TagSpecification] = field(default_factory=list)
    TargetCapacityUnitType: Optional[str] = None  # vcpu | memory-mib | units
    TerminateInstancesWithExpiration: Optional[bool] = None
    Type: Optional[SpotFleetRequestType] = None
    ValidFrom: Optional[datetime] = None
    ValidUntil: Optional[datetime] = None


@dataclass
class SpotFleetRequestConfig:
    activity_status: Optional[SpotFleetRequestActivityStatus] = None
    create_time: Optional[datetime] = None
    spot_fleet_request_config: Optional[SpotFleetRequestConfigData] = None
    spot_fleet_request_id: Optional[str] = None
    spot_fleet_request_state: Optional[SpotFleetRequestState] = None
    tag_set: List[Tag] = field(default_factory=list)


@dataclass
class SpotFleetRequest:
    spot_fleet_request_id: str
    config: SpotFleetRequestConfigData
    state: SpotFleetRequestState = SpotFleetRequestState.SUBMITTED
    create_time: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)


class SpotFleetBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.spot_fleet_requests

    def cancel_spot_fleet_requests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        spot_fleet_request_ids = params.get("SpotFleetRequestId.N")
        terminate_instances = params.get("TerminateInstances")
        dry_run = params.get("DryRun", False)

        response = {
            "requestId": self.generate_request_id(),
            "successfulFleetRequestSet": [],
            "unsuccessfulFleetRequestSet": [],
        }

        if dry_run:
            # For dry run, we simulate permission check by always raising DryRunOperation error
            # unless we want to simulate UnauthorizedOperation, but here we assume permission granted
            raise Exception("DryRunOperation")

        if not spot_fleet_request_ids or not isinstance(spot_fleet_request_ids, list):
            # SpotFleetRequestId.N is required and must be a list
            raise Exception("InvalidParameterValue: SpotFleetRequestId.N must be a non-empty list")

        if terminate_instances is None:
            # TerminateInstances is required
            raise Exception("MissingParameter: TerminateInstances is required")

        # Limit to 100 IDs as per constraint
        if len(spot_fleet_request_ids) > 100:
            raise Exception("InvalidParameterValue: Cannot specify more than 100 SpotFleetRequestIds")

        for sfr_id in spot_fleet_request_ids:
            spot_fleet = self.state.spot_fleet.get(sfr_id)
            if spot_fleet is None:
                error = CancelSpotFleetRequestsError(
                    code="fleetRequestIdDoesNotExist",
                    message=f"Spot Fleet request ID {sfr_id} does not exist"
                )
                error_item = CancelSpotFleetRequestsErrorItem(
                    error=error,
                    spot_fleet_request_id=sfr_id
                )
                response["unsuccessfulFleetRequestSet"].append(error_item)
                continue

            # Check if current state allows cancellation
            if spot_fleet.state in [
                SpotFleetRequestState.CANCELLED,
                SpotFleetRequestState.CANCELLED_RUNNING,
                SpotFleetRequestState.CANCELLED_TERMINATING,
                SpotFleetRequestState.FAILED,
            ]:
                error = CancelSpotFleetRequestsError(
                    code="fleetRequestNotInCancellableState",
                    message=f"Spot Fleet request ID {sfr_id} is not in a cancellable state"
                )
                error_item = CancelSpotFleetRequestsErrorItem(
                    error=error,
                    spot_fleet_request_id=sfr_id
                )
                response["unsuccessfulFleetRequestSet"].append(error_item)
                continue

            previous_state = spot_fleet.state

            # Update state based on terminate_instances flag
            if terminate_instances:
                spot_fleet.state = SpotFleetRequestState.CANCELLED_TERMINATING
                # Terminate all instances associated with this spot fleet
                # We assume instances are tracked in spot_fleet.instances as a dict or list
                # Since no instance tracking is specified, we simulate by clearing instances
                # If instances are stored in self.state.resources, we should find and terminate them
                # But no instance resource management is specified here, so we skip actual termination
            else:
                spot_fleet.state = SpotFleetRequestState.CANCELLED_RUNNING
                # Instances continue to run, no termination

            success_item = CancelSpotFleetRequestsSuccessItem(
                current_spot_fleet_request_state=spot_fleet.state,
                previous_spot_fleet_request_state=previous_state,
                spot_fleet_request_id=sfr_id
            )
            response["successfulFleetRequestSet"].append(success_item)

        return response


    def describe_spot_fleet_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        spot_fleet_request_id = params.get("SpotFleetRequestId")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        dry_run = params.get("DryRun", False)

        response = {
            "requestId": self.generate_request_id(),
            "spotFleetRequestId": spot_fleet_request_id,
            "activeInstanceSet": [],
            "nextToken": None,
        }

        if dry_run:
            raise Exception("DryRunOperation")

        if not spot_fleet_request_id:
            raise Exception("MissingParameter: SpotFleetRequestId is required")

        spot_fleet = self.state.spot_fleet.get(spot_fleet_request_id)
        if spot_fleet is None:
            raise Exception(f"InvalidSpotFleetRequestId.NotFound: Spot Fleet request ID {spot_fleet_request_id} does not exist")

        # We assume spot_fleet has attribute 'instances' which is a list of instance objects or dicts
        # Each instance should have instance_id, instance_type, spot_instance_request_id, and instance_health
        # Since no instance tracking is specified, we simulate empty list if not present
        instances = getattr(spot_fleet, "instances", [])

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except ValueError:
                raise Exception("InvalidNextToken: NextToken must be an integer string")

        if max_results is None:
            max_results = 1000
        else:
            try:
                max_results = int(max_results)
            except ValueError:
                raise Exception("InvalidParameterValue: MaxResults must be an integer")
            if max_results < 1 or max_results > 1000:
                raise Exception("InvalidParameterValue: MaxResults must be between 1 and 1000")

        end_index = start_index + max_results
        paged_instances = instances[start_index:end_index]

        for inst in paged_instances:
            active_instance = ActiveInstance(
                instance_id=getattr(inst, "instance_id", None),
                instance_type=getattr(inst, "instance_type", None),
                spot_instance_request_id=getattr(inst, "spot_instance_request_id", None),
                instance_health=getattr(inst, "instance_health", None),
            )
            response["activeInstanceSet"].append(active_instance)

        if end_index < len(instances):
            response["nextToken"] = str(end_index)
        else:
            response["nextToken"] = None

        return response


    def describe_spot_fleet_request_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        spot_fleet_request_id = params.get("SpotFleetRequestId")
        start_time = params.get("StartTime")
        event_type = params.get("EventType")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        dry_run = params.get("DryRun", False)

        response = {
            "requestId": self.generate_request_id(),
            "spotFleetRequestId": spot_fleet_request_id,
            "startTime": start_time,
            "historyRecordSet": [],
            "lastEvaluatedTime": None,
            "nextToken": None,
        }

        if dry_run:
            raise Exception("DryRunOperation")

        if not spot_fleet_request_id:
            raise Exception("MissingParameter: SpotFleetRequestId is required")

        if not start_time:
            raise Exception("MissingParameter: StartTime is required")

        spot_fleet = self.state.spot_fleet.get(spot_fleet_request_id)
        if spot_fleet is None:
            raise Exception(f"InvalidSpotFleetRequestId.NotFound: Spot Fleet request ID {spot_fleet_request_id} does not exist")

        # We assume spot_fleet has attribute 'history' which is a list of HistoryRecord objects
        # If not present, simulate empty list
        history = getattr(spot_fleet, "history", [])

        # Filter by event_type if specified
        if event_type:
            filtered_history = [h for h in history if h.event_type == event_type]
        else:
            filtered_history = history

        # Filter by start_time (only events on or after start_time)
        # start_time is expected to be a datetime object or ISO8601 string
        from datetime import datetime
        if isinstance(start_time, str):
            try:
                start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise Exception("InvalidParameterValue: StartTime must be in ISO8601 format YYYY-MM-DDTHH:MM:SSZ")
        elif isinstance(start_time, datetime):
            start_time_dt = start_time
        else:
            raise Exception("InvalidParameterValue: StartTime must be a string or datetime")

        filtered_history = [h for h in filtered_history if h.timestamp and h.timestamp >= start_time_dt]

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except ValueError:
                raise Exception("InvalidNextToken: NextToken must be an integer string")

        if max_results is None:
            max_results = 1000
        else:
            try:
                max_results = int(max_results)
            except ValueError:
                raise Exception("InvalidParameterValue: MaxResults must be an integer")
            if max_results < 1 or max_results > 1000:
                raise Exception("InvalidParameterValue: MaxResults must be between 1 and 1000")

        end_index = start_index + max_results
        paged_history = filtered_history[start_index:end_index]

        response["historyRecordSet"] = paged_history

        if end_index < len(filtered_history):
            response["nextToken"] = str(end_index)
            # lastEvaluatedTime is not present if nextToken is present
            response["lastEvaluatedTime"] = None
        else:
            response["nextToken"] = None
            if paged_history:
                # lastEvaluatedTime is the timestamp of the last returned event
                response["lastEvaluatedTime"] = paged_history[-1].timestamp
            else:
                response["lastEvaluatedTime"] = None

        return response


    def describe_spot_fleet_requests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        spot_fleet_request_ids = params.get("SpotFleetRequestId.N")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        dry_run = params.get("DryRun", False)

        response = {
            "requestId": self.generate_request_id(),
            "spotFleetRequestConfigSet": [],
            "nextToken": None,
        }

        if dry_run:
            raise Exception("DryRunOperation")

        # Collect all spot fleet requests if no IDs specified
        all_spot_fleets = list(self.state.spot_fleet.values())

        # Filter by IDs if provided
        if spot_fleet_request_ids:
            if not isinstance(spot_fleet_request_ids, list):
                raise Exception("InvalidParameterValue: SpotFleetRequestId.N must be a list")
            filtered_fleets = []
            for sfr_id in spot_fleet_request_ids:
                spot_fleet = self.state.spot_fleet.get(sfr_id)
                if spot_fleet:
                    filtered_fleets.append(spot_fleet)
            spot_fleets = filtered_fleets
        else:
            spot_fleets = all_spot_fleets

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except ValueError:
                raise Exception("InvalidNextToken: NextToken must be an integer string")

        if max_results is None:
            max_results = 1000
        else:
            try:
                max_results = int(max_results)
            except ValueError:
                raise Exception("InvalidParameterValue: MaxResults must be an integer")
            if max_results < 1:
                raise Exception("InvalidParameterValue: MaxResults must be at least 1")

        end_index = start_index + max_results
        paged_fleets = spot_fleets[start_index:end_index]

        for spot_fleet in paged_fleets:
            # Compose SpotFleetRequestConfig object for response
            config = SpotFleetRequestConfig(
                spot_fleet_request_id=spot_fleet.spot_fleet_request_id,
                spot_fleet_request_state=spot_fleet.state,
                create_time=spot_fleet.create_time,
                spot_fleet_request_config=spot_fleet.config,
                activity_status=None,  # Not specified how to get activity_status, set None
                tag_set=[Tag(Key=k, Value=v) for k, v in spot_fleet.tags.items()] if spot_fleet.tags else [],
            )
            response["spotFleetRequestConfigSet"].append(config)

        if end_index < len(spot_fleets):
            response["nextToken"] = str(end_index)
        else:
            response["nextToken"] = None

        return response


    def modify_spot_fleet_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        spot_fleet_request_id = params.get("SpotFleetRequestId")
        target_capacity = params.get("TargetCapacity")
        on_demand_target_capacity = params.get("OnDemandTargetCapacity")
        excess_capacity_termination_policy = params.get("ExcessCapacityTerminationPolicy")
        launch_template_configs = params.get("LaunchTemplateConfig.N")
        context = params.get("Context")
        dry_run = params.get("DryRun", False)  # DryRun param is not specified but commonly supported

        response = {
            "requestId": self.generate_request_id(),
            "return": False,
        }

        if dry_run:
            raise Exception("DryRunOperation")

        if not spot_fleet_request_id:
            raise Exception("MissingParameter: SpotFleetRequestId is required")

        spot_fleet = self.state.spot_fleet.get(spot_fleet_request_id)
        if spot_fleet is None:
            raise Exception(f"InvalidSpotFleetRequestId.NotFound: Spot Fleet request ID {spot_fleet_request_id} does not exist")

        # Only fleets of type maintain can be modified
        if spot_fleet.config.Type != SpotFleetRequestType.MAINTAIN:
            raise Exception("UnsupportedOperation: Only Spot Fleet requests of type 'maintain' can be modified")

        # Set state to modifying
        spot_fleet.state = SpotFleetRequestState.MODIFYING

        # Update fields if provided
        if target_capacity is not None:
            try:
                target_capacity_int = int(target_capacity)
                if target_capacity_int < 0:
                    raise Exception("InvalidParameterValue: TargetCapacity must be non-negative")
                spot_fleet.config.TargetCapacity = target_capacity_int
            except ValueError:
                raise Exception("InvalidParameterValue: TargetCapacity must be an integer")

        if on_demand_target_capacity is not None:
            try:
                on_demand_target_capacity_int = int(on_demand_target_capacity)
                if on_demand_target_capacity_int < 0:
                    raise Exception("InvalidParameterValue: OnDemandTargetCapacity must be non-negative")
                spot_fleet.config.OnDemandTargetCapacity = on_demand_target_capacity_int
            except ValueError:
                raise Exception("InvalidParameterValue: OnDemandTargetCapacity must be an integer")

        if excess_capacity_termination_policy is not None:
            # Validate value
            valid_values = [ExcessCapacityTerminationPolicy.NO_TERMINATION, ExcessCapacityTerminationPolicy.DEFAULT]
            if excess_capacity_termination_policy not in valid_values and \
               excess_capacity_termination_policy not in [v.value for v in valid_values]:
                raise Exception("InvalidParameterValue: ExcessCapacityTerminationPolicy must be 'noTermination' or 'default'")
            # Assign enum member if string
            if isinstance(excess_capacity_termination_policy, str):
                if excess_capacity_termination_policy == "noTermination":
                    spot_fleet.config.ExcessCapacityTerminationPolicy = ExcessCapacityTerminationPolicy.NO_TERMINATION
                elif excess_capacity_termination_policy == "default":
                    spot_fleet.config.ExcessCapacityTerminationPolicy = ExcessCapacityTerminationPolicy.DEFAULT
            else:
                spot_fleet.config.ExcessCapacityTerminationPolicy = excess_capacity_termination_policy

        if launch_template_configs is not None:
            # launch_template_configs is expected to be a list of LaunchTemplateConfig objects or dicts
            # We replace the existing LaunchTemplateConfigs with the new ones
            # Validate type
            if not isinstance(launch_template_configs, list):
                raise Exception("InvalidParameterValue: LaunchTemplateConfig.N must be a list")
            spot_fleet.config.LaunchTemplateConfigs = launch_template_configs

        # Context is reserved, we can store it if needed
        if context is not None:
            spot_fleet.config.Context = context

        # After modification, set state back to active (simulate immediate success)
        spot_fleet.state = SpotFleetRequestState.ACTIVE

        response["return"] = True
        return response

    def request_spot_fleet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Validate required parameter SpotFleetRequestConfig
        config = params.get("SpotFleetRequestConfig")
        if not config:
            raise Exception("Missing required parameter SpotFleetRequestConfig")

        # Validate required fields inside SpotFleetRequestConfig
        iam_fleet_role = config.get("IamFleetRole")
        if not iam_fleet_role:
            raise Exception("Missing required field IamFleetRole in SpotFleetRequestConfig")
        target_capacity = config.get("TargetCapacity")
        if target_capacity is None:
            raise Exception("Missing required field TargetCapacity in SpotFleetRequestConfig")

        # Validate mutually exclusive LaunchSpecifications and LaunchTemplateConfigs
        launch_specifications = config.get("LaunchSpecifications")
        launch_template_configs = config.get("LaunchTemplateConfigs")
        if launch_specifications and launch_template_configs:
            raise Exception("Cannot specify both LaunchSpecifications and LaunchTemplateConfigs")

        # Validate that if On-Demand capacity is included, LaunchTemplateConfigs must be used
        on_demand_target_capacity = config.get("OnDemandTargetCapacity")
        if on_demand_target_capacity and not launch_template_configs:
            raise Exception("If OnDemandTargetCapacity is specified, LaunchTemplateConfigs must be used")

        # Validate TagSpecifications resource type if present
        tag_specifications = config.get("TagSpecifications", [])
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if resource_type != "spot-fleet-request":
                raise Exception("TagSpecifications ResourceType must be 'spot-fleet-request'")

        # Generate unique SpotFleetRequestId and requestId
        spot_fleet_request_id = self.generate_unique_id(prefix="sfr-")
        request_id = self.generate_request_id()

        # Prepare tags dictionary from TagSpecifications for the SpotFleetRequest itself
        tags = {}
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") == "spot-fleet-request":
                for tag in tag_spec.get("Tags", []):
                    key = tag.get("Key")
                    value = tag.get("Value")
                    if key:
                        tags[key] = value

        # Create SpotFleetRequestConfigData object
        # We assume SpotFleetRequestConfigData can be instantiated with the dict keys as kwargs
        # For lists, we pass empty list if not present
        spot_fleet_request_config_data = SpotFleetRequestConfigData(
            IamFleetRole=iam_fleet_role,
            TargetCapacity=target_capacity,
            AllocationStrategy=config.get("AllocationStrategy"),
            ClientToken=config.get("ClientToken"),
            Context=config.get("Context"),
            ExcessCapacityTerminationPolicy=config.get("ExcessCapacityTerminationPolicy"),
            FulfilledCapacity=config.get("FulfilledCapacity"),
            InstanceInterruptionBehavior=config.get("InstanceInterruptionBehavior"),
            InstancePoolsToUseCount=config.get("InstancePoolsToUseCount"),
            LaunchSpecifications=launch_specifications or [],
            LaunchTemplateConfigs=launch_template_configs or [],
            LoadBalancersConfig=config.get("LoadBalancersConfig"),
            OnDemandAllocationStrategy=config.get("OnDemandAllocationStrategy"),
            OnDemandFulfilledCapacity=config.get("OnDemandFulfilledCapacity"),
            OnDemandMaxTotalPrice=config.get("OnDemandMaxTotalPrice"),
            OnDemandTargetCapacity=on_demand_target_capacity,
            ReplaceUnhealthyInstances=config.get("ReplaceUnhealthyInstances"),
            SpotMaintenanceStrategies=config.get("SpotMaintenanceStrategies"),
            SpotMaxTotalPrice=config.get("SpotMaxTotalPrice"),
            SpotPrice=config.get("SpotPrice"),
            TagSpecifications=tag_specifications,
            TargetCapacityUnitType=config.get("TargetCapacityUnitType"),
            TerminateInstancesWithExpiration=config.get("TerminateInstancesWithExpiration"),
            Type=config.get("Type"),
            ValidFrom=config.get("ValidFrom"),
            ValidUntil=config.get("ValidUntil"),
        )

        # Create SpotFleetRequest object
        spot_fleet_request = SpotFleetRequest(
            spot_fleet_request_id=spot_fleet_request_id,
            config=spot_fleet_request_config_data,
            state=SpotFleetRequestState.ACTIVE,
            create_time=datetime.datetime.utcnow(),
            tags=tags,
        )

        # Store the SpotFleetRequest in the shared state dictionary
        self.state.spot_fleet[spot_fleet_request_id] = spot_fleet_request
        self.state.resources[spot_fleet_request_id] = spot_fleet_request

        # Return response dictionary
        return {
            "requestId": request_id,
            "spotFleetRequestId": spot_fleet_request_id,
        }

    

from emulator_core.gateway.base import BaseGateway

class SpotFleetGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CancelSpotFleetRequests", self.cancel_spot_fleet_requests)
        self.register_action("DescribeSpotFleetInstances", self.describe_spot_fleet_instances)
        self.register_action("DescribeSpotFleetRequestHistory", self.describe_spot_fleet_request_history)
        self.register_action("DescribeSpotFleetRequests", self.describe_spot_fleet_requests)
        self.register_action("ModifySpotFleetRequest", self.modify_spot_fleet_request)
        self.register_action("RequestSpotFleet", self.request_spot_fleet)

    def cancel_spot_fleet_requests(self, params):
        return self.backend.cancel_spot_fleet_requests(params)

    def describe_spot_fleet_instances(self, params):
        return self.backend.describe_spot_fleet_instances(params)

    def describe_spot_fleet_request_history(self, params):
        return self.backend.describe_spot_fleet_request_history(params)

    def describe_spot_fleet_requests(self, params):
        return self.backend.describe_spot_fleet_requests(params)

    def modify_spot_fleet_request(self, params):
        return self.backend.modify_spot_fleet_request(params)

    def request_spot_fleet(self, params):
        return self.backend.request_spot_fleet(params)
