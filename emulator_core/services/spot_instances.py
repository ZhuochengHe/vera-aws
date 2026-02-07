from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from emulator_core.backend import BaseBackend


class SpotInstanceRequestState(str, Enum):
    OPEN = "open"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"


class SpotInstanceInterruptionBehavior(str, Enum):
    HIBERNATE = "hibernate"
    STOP = "stop"
    TERMINATE = "terminate"


class SpotInstanceRequestType(str, Enum):
    ONE_TIME = "one-time"
    PERSISTENT = "persistent"


class SpotDatafeedSubscriptionState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


@dataclass
class SpotInstanceStateFault:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass
class SpotInstanceStatus:
    code: Optional[str] = None
    message: Optional[str] = None
    update_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "updateTime": self.update_time.isoformat() if self.update_time else None,
        }


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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.AvailabilityZone,
            "AvailabilityZoneId": self.AvailabilityZoneId,
            "DeleteOnTermination": self.DeleteOnTermination,
            "Encrypted": self.Encrypted,
            "Iops": self.Iops,
            "KmsKeyId": self.KmsKeyId,
            "OutpostArn": self.OutpostArn,
            "SnapshotId": self.SnapshotId,
            "Throughput": self.Throughput,
            "VolumeInitializationRate": self.VolumeInitializationRate,
            "VolumeSize": self.VolumeSize,
            "VolumeType": self.VolumeType,
        }


@dataclass
class BlockDeviceMapping:
    DeviceName: Optional[str] = None
    Ebs: Optional[EbsBlockDevice] = None
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
class GroupIdentifier:
    GroupId: Optional[str] = None
    GroupName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "GroupId": self.GroupId,
            "GroupName": self.GroupName,
        }


@dataclass
class IamInstanceProfileSpecification:
    Arn: Optional[str] = None
    Name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Arn": self.Arn,
            "Name": self.Name,
        }


@dataclass
class RunInstancesMonitoringEnabled:
    Enabled: bool

    def to_dict(self) -> Dict[str, Any]:
        return {"Enabled": self.Enabled}


@dataclass
class InstanceIpv6Address:
    Ipv6Address: Optional[str] = None
    IsPrimaryIpv6: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Ipv6Address": self.Ipv6Address,
            "IsPrimaryIpv6": self.IsPrimaryIpv6,
        }


@dataclass
class PrivateIpAddressSpecification:
    Primary: Optional[bool] = None
    PrivateIpAddress: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Primary": self.Primary,
            "PrivateIpAddress": self.PrivateIpAddress,
        }


@dataclass
class EnaSrdUdpSpecificationRequest:
    EnaSrdUdpEnabled: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EnaSrdUdpEnabled": self.EnaSrdUdpEnabled,
        }


@dataclass
class EnaSrdSpecificationRequest:
    EnaSrdEnabled: Optional[bool] = None
    EnaSrdUdpSpecification: Optional[EnaSrdUdpSpecificationRequest] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EnaSrdEnabled": self.EnaSrdEnabled,
            "EnaSrdUdpSpecification": self.EnaSrdUdpSpecification.to_dict() if self.EnaSrdUdpSpecification else None,
        }


@dataclass
class ConnectionTrackingSpecificationRequest:
    TcpEstablishedTimeout: Optional[int] = None
    UdpStreamTimeout: Optional[int] = None
    UdpTimeout: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TcpEstablishedTimeout": self.TcpEstablishedTimeout,
            "UdpStreamTimeout": self.UdpStreamTimeout,
            "UdpTimeout": self.UdpTimeout,
        }


@dataclass
class InstanceNetworkInterfaceSpecification:
    AssociateCarrierIpAddress: Optional[bool] = None
    AssociatePublicIpAddress: Optional[bool] = None
    ConnectionTrackingSpecification: Optional[ConnectionTrackingSpecificationRequest] = None
    DeleteOnTermination: Optional[bool] = None
    Description: Optional[str] = None
    DeviceIndex: Optional[int] = None
    EnaQueueCount: Optional[int] = None
    EnaSrdSpecification: Optional[EnaSrdSpecificationRequest] = None
    InterfaceType: Optional[str] = None
    Ipv4Prefixes: Optional[List[str]] = None  # Simplified as list of strings for Ipv4PrefixSpecificationRequest
    Ipv4PrefixCount: Optional[int] = None
    Ipv6AddressCount: Optional[int] = None
    Ipv6Addresses: Optional[List[InstanceIpv6Address]] = None
    Ipv6Prefixes: Optional[List[str]] = None  # Simplified as list of strings for Ipv6PrefixSpecificationRequest
    Ipv6PrefixCount: Optional[int] = None
    NetworkCardIndex: Optional[int] = None
    NetworkInterfaceId: Optional[str] = None
    PrimaryIpv6: Optional[bool] = None
    PrivateIpAddress: Optional[str] = None
    PrivateIpAddresses: Optional[List[PrivateIpAddressSpecification]] = None
    SecondaryPrivateIpAddressCount: Optional[int] = None
    Groups: Optional[List[str]] = None
    SubnetId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AssociateCarrierIpAddress": self.AssociateCarrierIpAddress,
            "AssociatePublicIpAddress": self.AssociatePublicIpAddress,
            "ConnectionTrackingSpecification": self.ConnectionTrackingSpecification.to_dict() if self.ConnectionTrackingSpecification else None,
            "DeleteOnTermination": self.DeleteOnTermination,
            "Description": self.Description,
            "DeviceIndex": self.DeviceIndex,
            "EnaQueueCount": self.EnaQueueCount,
            "EnaSrdSpecification": self.EnaSrdSpecification.to_dict() if self.EnaSrdSpecification else None,
            "InterfaceType": self.InterfaceType,
            "Ipv4Prefixes": self.Ipv4Prefixes,
            "Ipv4PrefixCount": self.Ipv4PrefixCount,
            "Ipv6AddressCount": self.Ipv6AddressCount,
            "Ipv6Addresses": [addr.to_dict() for addr in self.Ipv6Addresses] if self.Ipv6Addresses else None,
            "Ipv6Prefixes": self.Ipv6Prefixes,
            "Ipv6PrefixCount": self.Ipv6PrefixCount,
            "NetworkCardIndex": self.NetworkCardIndex,
            "NetworkInterfaceId": self.NetworkInterfaceId,
            "PrimaryIpv6": self.PrimaryIpv6,
            "PrivateIpAddress": self.PrivateIpAddress,
            "PrivateIpAddresses": [addr.to_dict() for addr in self.PrivateIpAddresses] if self.PrivateIpAddresses else None,
            "SecondaryPrivateIpAddressCount": self.SecondaryPrivateIpAddressCount,
            "Groups": self.Groups,
            "SubnetId": self.SubnetId,
        }


@dataclass
class SpotPlacement:
    AvailabilityZone: Optional[str] = None
    GroupName: Optional[str] = None
    Tenancy: Optional[str] = None  # default | dedicated | host

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AvailabilityZone": self.AvailabilityZone,
            "GroupName": self.GroupName,
            "Tenancy": self.Tenancy,
        }


@dataclass
class LaunchSpecification:
    addressingType: Optional[str] = None
    blockDeviceMapping: List[BlockDeviceMapping] = field(default_factory=list)
    ebsOptimized: Optional[bool] = None
    groupSet: List[GroupIdentifier] = field(default_factory=list)
    iamInstanceProfile: Optional[IamInstanceProfileSpecification] = None
    imageId: Optional[str] = None
    instanceType: Optional[str] = None
    kernelId: Optional[str] = None
    keyName: Optional[str] = None
    monitoring: Optional[RunInstancesMonitoringEnabled] = None
    networkInterfaceSet: List[InstanceNetworkInterfaceSpecification] = field(default_factory=list)
    placement: Optional[SpotPlacement] = None
    ramdiskId: Optional[str] = None
    subnetId: Optional[str] = None
    userData: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "addressingType": self.addressingType,
            "blockDeviceMapping": [bdm.to_dict() for bdm in self.blockDeviceMapping],
            "ebsOptimized": self.ebsOptimized,
            "groupSet": [group.to_dict() for group in self.groupSet],
            "iamInstanceProfile": self.iamInstanceProfile.to_dict() if self.iamInstanceProfile else None,
            "imageId": self.imageId,
            "instanceType": self.instanceType,
            "kernelId": self.kernelId,
            "keyName": self.keyName,
            "monitoring": self.monitoring.to_dict() if self.monitoring else None,
            "networkInterfaceSet": [ni.to_dict() for ni in self.networkInterfaceSet],
            "placement": self.placement.to_dict() if self.placement else None,
            "ramdiskId": self.ramdiskId,
            "subnetId": self.subnetId,
            "userData": self.userData,
        }


@dataclass
class SpotInstanceRequest:
    actualBlockHourlyPrice: Optional[str] = None  # Deprecated
    availabilityZoneGroup: Optional[str] = None
    blockDurationMinutes: Optional[int] = None  # Deprecated
    createTime: Optional[datetime] = None
    fault: Optional[SpotInstanceStateFault] = None
    instanceId: Optional[str] = None
    instanceInterruptionBehavior: Optional[SpotInstanceInterruptionBehavior] = None
    launchedAvailabilityZone: Optional[str] = None
    launchedAvailabilityZoneId: Optional[str] = None
    launchGroup: Optional[str] = None
    launchSpecification: Optional[LaunchSpecification] = None
    productDescription: Optional[str] = None
    spotInstanceRequestId: Optional[str] = None
    spotPrice: Optional[str] = None
    state: Optional[SpotInstanceRequestState] = None
    status: Optional[SpotInstanceStatus] = None
    tagSet: List[Tag] = field(default_factory=list)
    type: Optional[SpotInstanceRequestType] = None
    validFrom: Optional[datetime] = None
    validUntil: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actualBlockHourlyPrice": self.actualBlockHourlyPrice,
            "availabilityZoneGroup": self.availabilityZoneGroup,
            "blockDurationMinutes": self.blockDurationMinutes,
            "createTime": self.createTime.isoformat() if self.createTime else None,
            "fault": self.fault.to_dict() if self.fault else None,
            "instanceId": self.instanceId,
            "instanceInterruptionBehavior": self.instanceInterruptionBehavior.value if self.instanceInterruptionBehavior else None,
            "launchedAvailabilityZone": self.launchedAvailabilityZone,
            "launchedAvailabilityZoneId": self.launchedAvailabilityZoneId,
            "launchGroup": self.launchGroup,
            "launchSpecification": self.launchSpecification.to_dict() if self.launchSpecification else None,
            "productDescription": self.productDescription,
            "spotInstanceRequestId": self.spotInstanceRequestId,
            "spotPrice": self.spotPrice,
            "state": self.state.value if self.state else None,
            "status": self.status.to_dict() if self.status else None,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "type": self.type.value if self.type else None,
            "validFrom": self.validFrom.isoformat() if self.validFrom else None,
            "validUntil": self.validUntil.isoformat() if self.validUntil else None,
        }


@dataclass
class CancelledSpotInstanceRequest:
    spotInstanceRequestId: Optional[str] = None
    state: Optional[SpotInstanceRequestState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spotInstanceRequestId": self.spotInstanceRequestId,
            "state": self.state.value if self.state else None,
        }


@dataclass
class SpotDatafeedSubscription:
    bucket: Optional[str] = None
    fault: Optional[SpotInstanceStateFault] = None
    ownerId: Optional[str] = None
    prefix: Optional[str] = None
    state: Optional[SpotDatafeedSubscriptionState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bucket": self.bucket,
            "fault": self.fault.to_dict() if self.fault else None,
            "ownerId": self.ownerId,
            "prefix": self.prefix,
            "state": self.state.value if self.state else None,
        }


@dataclass
class SpotPrice:
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    instanceType: Optional[str] = None
    productDescription: Optional[str] = None
    spotPrice: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "instanceType": self.instanceType,
            "productDescription": self.productDescription,
            "spotPrice": self.spotPrice,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class SpotPlacementScore:
    availabilityZoneId: Optional[str] = None
    region: Optional[str] = None
    score: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZoneId": self.availabilityZoneId,
            "region": self.region,
            "score": self.score,
        }


class SpotInstancesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.spot_instance_requests, self.state.spot_datafeed_subscriptions, etc.

    def cancel_spot_instance_requests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        spot_instance_request_ids = []
        # Collect SpotInstanceRequestId.N parameters
        for key, value in params.items():
            if key.startswith("SpotInstanceRequestId."):
                spot_instance_request_ids.append(value)
        if not spot_instance_request_ids:
            raise ValueError("SpotInstanceRequestId.N parameter is required")

        cancelled_requests = []
        for sir_id in spot_instance_request_ids:
            sir = self.state.spot_instances.get(sir_id)
            if sir:
                # Change state to cancelled if not already cancelled or closed or failed
                if sir.state not in [SpotInstanceRequestState.CANCELLED, SpotInstanceRequestState.CLOSED, SpotInstanceRequestState.FAILED]:
                    sir.state = SpotInstanceRequestState.CANCELLED
                cancelled_requests.append(
                    CancelledSpotInstanceRequest(
                        spotInstanceRequestId=sir_id,
                        state=sir.state,
                    )
                )
            else:
                # If not found, still return with state None (AWS behavior is to ignore unknown IDs)
                cancelled_requests.append(
                    CancelledSpotInstanceRequest(
                        spotInstanceRequestId=sir_id,
                        state=None,
                    )
                )

        return {
            "requestId": self.generate_request_id(),
            "spotInstanceRequestSet": [req.to_dict() for req in cancelled_requests],
        }


    def create_spot_datafeed_subscription(self, params: Dict[str, Any]) -> Dict[str, Any]:
        bucket = params.get("Bucket")
        if not bucket:
            raise ValueError("Bucket parameter is required")

        prefix = params.get("Prefix")
        owner_id = self.get_owner_id()

        # Check if subscription already exists
        existing_sub = getattr(self.state, "spot_datafeed_subscription", None)
        if existing_sub:
            # AWS allows only one data feed per account, so overwrite it
            existing_sub.bucket = bucket
            existing_sub.prefix = prefix
            existing_sub.state = SpotDatafeedSubscriptionState.ACTIVE
            existing_sub.fault = None
            existing_sub.ownerId = owner_id
            subscription = existing_sub
        else:
            subscription = SpotDatafeedSubscription(
                bucket=bucket,
                prefix=prefix,
                state=SpotDatafeedSubscriptionState.ACTIVE,
                fault=None,
                ownerId=owner_id,
            )
            self.state.spot_datafeed_subscription = subscription

        return {
            "requestId": self.generate_request_id(),
            "spotDatafeedSubscription": subscription.to_dict(),
        }


    def delete_spot_datafeed_subscription(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Check if subscription exists
        existing_sub = getattr(self.state, "spot_datafeed_subscription", None)
        if existing_sub:
            del self.state.spot_datafeed_subscription
            success = True
        else:
            # AWS returns true even if no subscription exists
            success = True

        return {
            "requestId": self.generate_request_id(),
            "return": success,
        }


    def describe_spot_datafeed_subscription(self, params: Dict[str, Any]) -> Dict[str, Any]:
        subscription = getattr(self.state, "spot_datafeed_subscription", None)
        if subscription:
            subscription_dict = subscription.to_dict()
        else:
            # Return empty subscription object with state Inactive
            subscription_dict = SpotDatafeedSubscription(
                bucket=None,
                prefix=None,
                state=SpotDatafeedSubscriptionState.INACTIVE,
                fault=None,
                ownerId=self.get_owner_id(),
            ).to_dict()

        return {
            "requestId": self.generate_request_id(),
            "spotDatafeedSubscription": subscription_dict,
        }


    def describe_spot_instance_requests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Collect SpotInstanceRequestId.N parameters
        spot_instance_request_ids = []
        for key, value in params.items():
            if key.startswith("SpotInstanceRequestId."):
                spot_instance_request_ids.append(value)

        # Filters parsing
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                # Filter.N.Name and Filter.N.Value.M
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    # Find existing filter or create new
                    filter_obj = next((f for f in filters if f["Name"] == params.get(f"Filter.{filter_index}.Name")), None)
                    if not filter_obj:
                        filter_obj = {"Name": params.get(f"Filter.{filter_index}.Name"), "Values": []}
                        filters.append(filter_obj)
                    if filter_key.startswith("Value"):
                        filter_obj["Values"].append(value)

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results <= 0:
                    max_results = None
            except Exception:
                max_results = None

        next_token = params.get("NextToken")

        # Start with all spot instance requests
        all_requests = list(self.state.spot_instances.values())

        # Filter by SpotInstanceRequestId if provided
        if spot_instance_request_ids:
            all_requests = [sir for sir in all_requests if sir.spotInstanceRequestId in spot_instance_request_ids]

        # Apply filters
        def matches_filter(sir: SpotInstanceRequest, filter_name: str, filter_values: List[str]) -> bool:
            # Implement common filters based on filter_name
            # Support some common filters as per AWS docs
            # For tag filters, handle tag:<key> and tag-key
            # For simplicity, implement main filters and tag filters

            # Lowercase filter name for case-insensitive matching
            fname = filter_name.lower()

            # Helper to check if any value matches
            def any_match(value):
                if value is None:
                    return False
                return any(str(value) == v for v in filter_values)

            # Tag filters
            if fname.startswith("tag:"):
                tag_key = filter_name[4:]
                for tag in sir.tagSet:
                    if tag.Key == tag_key and any(str(tag.Value) == v for v in filter_values):
                        return True
                return False
            if fname == "tag-key":
                for tag in sir.tagSet:
                    if any(tag.Key == v for v in filter_values):
                        return True
                return False

            # Map filter names to sir attributes or nested attributes
            if fname == "availability-zone-group":
                return any_match(sir.availabilityZoneGroup)
            if fname == "create-time":
                # Filter values are timestamps, compare string representation
                if sir.createTime:
                    return any(str(sir.createTime) == v for v in filter_values)
                return False
            if fname == "fault-code":
                if sir.fault and sir.fault.code:
                    return any(str(sir.fault.code) == v for v in filter_values)
                return False
            if fname == "fault-message":
                if sir.fault and sir.fault.message:
                    return any(str(sir.fault.message) == v for v in filter_values)
                return False
            if fname == "instance-id":
                return any_match(sir.instanceId)
            if fname == "launch-group":
                return any_match(sir.launchGroup)
            if fname == "product-description":
                return any_match(sir.productDescription)
            if fname == "spot-instance-request-id":
                return any_match(sir.spotInstanceRequestId)
            if fname == "spot-price":
                return any_match(sir.spotPrice)
            if fname == "state":
                # sir.state is Enum, compare value or name
                return any(str(sir.state) == v or sir.state.name == v for v in filter_values)
            if fname == "status-code":
                if sir.status and sir.status.code:
                    return any(str(sir.status.code) == v for v in filter_values)
                return False
            if fname == "status-message":
                if sir.status and sir.status.message:
                    return any(str(sir.status.message) == v for v in filter_values)
                return False
            if fname == "type":
                return any(str(sir.type) == v or sir.type.name == v for v in filter_values)
            if fname == "valid-from":
                if sir.validFrom:
                    return any(str(sir.validFrom) == v for v in filter_values)
                return False
            if fname == "valid-until":
                if sir.validUntil:
                    return any(str(sir.validUntil) == v for v in filter_values)
                return False

            # For launch.* filters, check launchSpecification attributes
            if sir.launchSpecification:
                ls = sir.launchSpecification
                if fname == "launch.image-id":
                    return any(str(ls.imageId) == v for v in filter_values)
                if fname == "launch.instance-type":
                    return any(str(ls.instanceType) == v for v in filter_values)
                if fname == "launch.key-name":
                    return any(str(ls.keyName) == v for v in filter_values)
                if fname == "launch.kernel-id":
                    return any(str(ls.kernelId) == v for v in filter_values)
                if fname == "launch.ramdisk-id":
                    return any(str(ls.ramdiskId) == v for v in filter_values)
                if fname == "launch.subnet-id":
                    return any(str(ls.subnetId) == v for v in filter_values)
                if fname == "launch.ebs-optimized":
                    if ls.ebsOptimized is not None:
                        return any(str(ls.ebsOptimized).lower() == v.lower() for v in filter_values)
                    return False
                if fname == "launch.monitoring-enabled":
                    if ls.monitoring:
                        return any(str(ls.monitoring.Enabled).lower() == v.lower() for v in filter_values)
                    return False
                if fname == "launch.group-id":
                    # groupSet is list of GroupIdentifier
                    for group in ls.groupSet:
                        if any(str(group.GroupId) == v for v in filter_values):
                            return True
                    return False
                if fname == "launch.group-name":
                    for group in ls.groupSet:
                        if any(str(group.GroupName) == v for v in filter_values):
                            return True
                    return False
                # launch.block-device-mapping.* filters
                if fname.startswith("launch.block-device-mapping."):
                    attr = fname[len("launch.block-device-mapping.") :]
                    for bdm in ls.blockDeviceMapping:
                        if bdm.Ebs:
                            ebs = bdm.Ebs
                            if attr == "delete-on-termination":
                                if ebs.DeleteOnTermination is not None:
                                    if any(str(ebs.DeleteOnTermination).lower() == v.lower() for v in filter_values):
                                        return True
                            elif attr == "device-name":
                                if bdm.DeviceName and any(str(bdm.DeviceName) == v for v in filter_values):
                                    return True
                            elif attr == "snapshot-id":
                                if ebs.SnapshotId and any(str(ebs.SnapshotId) == v for v in filter_values):
                                    return True
                            elif attr == "volume-size":
                                if ebs.VolumeSize is not None and any(str(ebs.VolumeSize) == v for v in filter_values):
                                    return True
                            elif attr == "volume-type":
                                if ebs.VolumeType and any(str(ebs.VolumeType) == v for v in filter_values):
                                    return True
                    return False

            # launched-availability-zone and launched-availability-zone-id filters
            if fname == "launched-availability-zone":
                return any_match(sir.launchedAvailabilityZone)
            if fname == "launched-availability-zone-id":
                return any_match(sir.launchedAvailabilityZoneId)

            # network-interface.* filters are complex, skipping for brevity

            return False

        # Apply all filters
        if filters:
            filtered_requests = []
            for sir in all_requests:
                if all(matches_filter(sir, f["Name"], f["Values"]) for f in filters):
                    filtered_requests.append(sir)
            all_requests = filtered_requests

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_requests)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_requests))

        page_requests = all_requests[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(all_requests):
            new_next_token = str(end_index)

        return {
            "requestId": self.generate_request_id(),
            "spotInstanceRequestSet": [sir.to_dict() for sir in page_requests],
            "nextToken": new_next_token,
        }

    def describe_spot_price_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Try to import dateutil, fall back to datetime.fromisoformat
        def parse_date(date_str):
            try:
                from dateutil.parser import parse as dateutil_parse
                return dateutil_parse(date_str)
            except ImportError:
                # Fall back to datetime parsing
                # Handle common formats: 2014-01-06T07:08:09, 2014-01-06T07:08:09Z
                date_str = date_str.rstrip('Z')
                if 'T' in date_str:
                    return datetime.datetime.fromisoformat(date_str)
                return datetime.datetime.strptime(date_str, "%Y-%m-%d")

        # Validate DryRun parameter (not implemented, just placeholder)
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Parse StartTime and EndTime
        start_time_str = params.get("StartTime")
        end_time_str = params.get("EndTime")
        start_time = None
        end_time = None
        try:
            if start_time_str:
                start_time = parse_date(start_time_str)
            if end_time_str:
                end_time = parse_date(end_time_str)
        except Exception:
            raise ValueError("Invalid StartTime or EndTime format")

        # Validate that start_time <= end_time if both specified
        if start_time and end_time and start_time > end_time:
            raise ValueError("StartTime must be before or equal to EndTime")

        # Validate MaxResults
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int) or max_results <= 0:
                raise ValueError("MaxResults must be a positive integer")

        # NextToken (pagination token) - not implemented, just accept
        next_token = params.get("NextToken")

        # Filters parsing
        filters = []
        # Filters come as Filter.N.Name and Filter.N.Value.M
        # Collect filters by index N
        filter_prefix = "Filter."
        filter_dict = {}
        for key, value in params.items():
            if key.startswith(filter_prefix):
                # key example: Filter.1.Name or Filter.1.Value.1
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    if filter_index not in filter_dict:
                        filter_dict[filter_index] = {"Name": None, "Values": []}
                    if filter_key == "Name":
                        filter_dict[filter_index]["Name"] = value
                    elif filter_key == "Value" or filter_key == "Value" or filter_key.startswith("Value"):
                        # Value can be Value or Value.N
                        filter_dict[filter_index]["Values"].append(value)
        # Convert to list of dicts with Name and Values
        for f in filter_dict.values():
            if f["Name"]:
                filters.append({"Name": f["Name"], "Values": f["Values"]})

        # InstanceType.N and ProductDescription.N parsing
        instance_types = []
        product_descriptions = []
        # InstanceType.N keys
        for key, value in params.items():
            if key.startswith("InstanceType."):
                instance_types.append(value)
            elif key.startswith("ProductDescription."):
                product_descriptions.append(value)

        # AvailabilityZone and AvailabilityZoneId validation
        az = params.get("AvailabilityZone")
        az_id = params.get("AvailabilityZoneId")
        if az and az_id:
            raise ValueError("Specify either AvailabilityZone or AvailabilityZoneId, not both")

        # Prepare spot price history list from self.state.spot_price_history or similar
        # Since no spot price history storage is defined, we simulate with self.state.spot_price_history dict
        # Each entry is a SpotPrice object with attributes: availabilityZone, availabilityZoneId, instanceType, productDescription, spotPrice, timestamp
        spot_price_history = getattr(self.state, "spot_price_history", {})
        # spot_price_history is dict of id -> SpotPrice objects

        # Filter spot price history entries according to parameters
        filtered_spot_prices = []

        def matches_filter(spot_price: "SpotPrice", filter_name: str, filter_values: List[str]) -> bool:
            # Filter names are case-sensitive
            # Supported filter names:
            # availability-zone, availability-zone-id, instance-type, product-description, spot-price, timestamp
            if filter_name == "availability-zone":
                return spot_price.availabilityZone in filter_values
            elif filter_name == "availability-zone-id":
                return spot_price.availabilityZoneId in filter_values
            elif filter_name == "instance-type":
                return spot_price.instanceType in filter_values
            elif filter_name == "product-description":
                return spot_price.productDescription in filter_values
            elif filter_name == "spot-price":
                # spot-price must match exactly or with wildcards (* and ?)
                # We implement simple wildcard matching using fnmatch
                import fnmatch
                for val in filter_values:
                    if fnmatch.fnmatch(spot_price.spotPrice or "", val):
                        return True
                return False
            elif filter_name == "timestamp":
                # timestamp filter supports wildcards (* and ?)
                # spot_price.timestamp is datetime, convert to string format "ddd MMM dd HH:mm:ss UTC YYYY"
                # Example format: Tue Nov 01 01:00:00 UTC 2016
                # We format timestamp accordingly
                if not spot_price.timestamp:
                    return False
                ts_str = spot_price.timestamp.strftime("%a %b %d %H:%M:%S UTC %Y")
                import fnmatch
                for val in filter_values:
                    if fnmatch.fnmatch(ts_str, val):
                        return True
                return False
            else:
                # Unknown filter name, ignore (AWS ignores unknown filters)
                return True

        for spot_price in spot_price_history.values():
            # Filter by AvailabilityZone or AvailabilityZoneId if specified
            if az and spot_price.availabilityZone != az:
                continue
            if az_id and spot_price.availabilityZoneId != az_id:
                continue
            # Filter by InstanceType if specified
            if instance_types and spot_price.instanceType not in instance_types:
                continue
            # Filter by ProductDescription if specified
            if product_descriptions and spot_price.productDescription not in product_descriptions:
                continue
            # Filter by filters
            filter_match = True
            for f in filters:
                if not matches_filter(spot_price, f["Name"], f["Values"]):
                    filter_match = False
                    break
            if not filter_match:
                continue
            # Filter by StartTime and EndTime
            if start_time and spot_price.timestamp and spot_price.timestamp < start_time:
                continue
            if end_time and spot_price.timestamp and spot_price.timestamp > end_time:
                continue
            filtered_spot_prices.append(spot_price)

        # Sort filtered spot prices by timestamp ascending
        filtered_spot_prices.sort(key=lambda sp: sp.timestamp or datetime.datetime.min)

        # Pagination: apply MaxResults and NextToken
        # NextToken is expected to be an index string or empty
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = len(filtered_spot_prices)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_spot_prices))
        page_spot_prices = filtered_spot_prices[start_index:end_index]

        # Prepare next token for pagination
        new_next_token = ""
        if end_index < len(filtered_spot_prices):
            new_next_token = str(end_index)

        # Prepare response dict
        response = {
            "requestId": self.generate_request_id(),
            "spotPriceHistorySet": [sp.to_dict() for sp in page_spot_prices],
            "nextToken": new_next_token or None,
        }
        return response


    def get_spot_placement_scores(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter TargetCapacity
        target_capacity = params.get("TargetCapacity")
        if target_capacity is None:
            raise ValueError("TargetCapacity is required")
        if not isinstance(target_capacity, int) or target_capacity < 1 or target_capacity > 2000000000:
            raise ValueError("TargetCapacity must be an integer between 1 and 2000000000")

        # Validate DryRun parameter (not implemented, just placeholder)
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Validate MaxResults
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 10 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 10 and 1000")

        # NextToken (pagination token) - not implemented, just accept
        next_token = params.get("NextToken")

        # SingleAvailabilityZone boolean
        single_az = params.get("SingleAvailabilityZone")
        if single_az is not None and not isinstance(single_az, bool):
            raise ValueError("SingleAvailabilityZone must be a boolean if specified")

        # RegionName.N list
        region_names = []
        for key, value in params.items():
            if key.startswith("RegionName."):
                region_names.append(value)

        # InstanceType.N list
        instance_types = []
        for key, value in params.items():
            if key.startswith("InstanceType."):
                instance_types.append(value)

        # InstanceRequirementsWithMetadata is complex object, not implemented in detail here
        # We will ignore it for now, as no data source for scores is defined

        # TargetCapacityUnitType validation
        target_capacity_unit_type = params.get("TargetCapacityUnitType")
        if target_capacity_unit_type is not None:
            valid_unit_types = {"vcpu", "memory-mib", "units"}
            if target_capacity_unit_type not in valid_unit_types:
                raise ValueError(f"Invalid TargetCapacityUnitType: {target_capacity_unit_type}")

        # For this emulator, we simulate spot placement scores
        # We assume self.state.spot_placement_scores is a dict of id -> SpotPlacementScore objects
        spot_placement_scores = getattr(self.state, "spot_placement_scores", {})

        # Filter scores by region_names if specified
        filtered_scores = []
        for score in spot_placement_scores.values():
            if region_names and score.region not in region_names:
                continue
            # If SingleAvailabilityZone is True, we only return scores with availabilityZoneId set
            if single_az and not score.availabilityZoneId:
                continue
            # If SingleAvailabilityZone is False or None, we only return scores with region set and no availabilityZoneId
            if not single_az and score.availabilityZoneId:
                continue
            filtered_scores.append(score)

        # Sort scores by score descending (higher score first)
        filtered_scores.sort(key=lambda s: s.score if s.score is not None else 0, reverse=True)

        # Limit to top 10 scores as per docs
        filtered_scores = filtered_scores[:10]

        # Pagination: apply MaxResults and NextToken
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = len(filtered_scores)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_scores))
        page_scores = filtered_scores[start_index:end_index]

        # Prepare next token for pagination
        new_next_token = None
        if end_index < len(filtered_scores):
            new_next_token = str(end_index)

        response = {
            "requestId": self.generate_request_id(),
            "spotPlacementScoreSet": [score.to_dict() for score in page_scores],
            "nextToken": new_next_token,
        }
        return response


    def request_spot_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Validate DryRun parameter (not implemented, just placeholder)
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # InstanceCount default 1
        instance_count = params.get("InstanceCount", 1)
        if not isinstance(instance_count, int) or instance_count < 1:
            raise ValueError("InstanceCount must be a positive integer")

        # Validate Type parameter
        request_type = params.get("Type", "one-time")
        valid_types = {"one-time", "persistent"}
        if request_type not in valid_types:
            raise ValueError(f"Invalid Type: {request_type}")

        # Validate InstanceInterruptionBehavior
        interruption_behavior = params.get("InstanceInterruptionBehavior")
        valid_behaviors = {"hibernate", "stop", "terminate", None}
        if interruption_behavior not in valid_behaviors:
            raise ValueError(f"Invalid InstanceInterruptionBehavior: {interruption_behavior}")

        # Validate BlockDurationMinutes (deprecated, accept if int)
        block_duration_minutes = params.get("BlockDurationMinutes")
        if block_duration_minutes is not None and not isinstance(block_duration_minutes, int):
            raise ValueError("BlockDurationMinutes must be an integer if specified")

        # Validate AvailabilityZoneGroup and LaunchGroup
        availability_zone_group = params.get("AvailabilityZoneGroup")
        launch_group = params.get("LaunchGroup")

        # Validate SpotPrice (string)
        spot_price = params.get("SpotPrice")
        if spot_price is not None and not isinstance(spot_price, str):
            raise ValueError("SpotPrice must be a string if specified")

        # Validate ValidFrom and ValidUntil timestamps
        valid_from_str = params.get("ValidFrom")
        valid_until_str = params.get("ValidUntil")
        valid_from = None
        valid_until = None

        def parse_date(date_str):
            import datetime
            try:
                from dateutil.parser import parse as dateutil_parse
                return dateutil_parse(date_str)
            except ImportError:
                date_str = date_str.rstrip('Z')
                if 'T' in date_str:
                    return datetime.datetime.fromisoformat(date_str)
                return datetime.datetime.strptime(date_str, "%Y-%m-%d")

        try:
            if valid_from_str:
                valid_from = parse_date(valid_from_str)
            if valid_until_str:
                valid_until = parse_date(valid_until_str)
        except Exception:
            raise ValueError("Invalid ValidFrom or ValidUntil format")

        if valid_from and valid_until and valid_from > valid_until:
            raise ValueError("ValidFrom must be before or equal to ValidUntil")

        # Validate LaunchSpecification (complex object)
        launch_spec_params = params.get("LaunchSpecification", {})
        if not isinstance(launch_spec_params, dict):
            raise ValueError("LaunchSpecification must be a dict if specified")

        # Build LaunchSpecification object
        # We assume LaunchSpecification class constructor accepts all fields as kwargs
        # We need to parse nested fields like blockDeviceMapping, groupSet, iamInstanceProfile, monitoring, networkInterfaceSet, placement

        # Helper to parse list of dicts to list of objects
        def parse_list_of_objects(param_list, cls):
            if not param_list:
                return []
            if not isinstance(param_list, list):
                raise ValueError(f"Expected list for {cls.__name__}")
            return [cls(**item) if isinstance(item, dict) else item for item in param_list]

        # Parse blockDeviceMapping
        block_device_mapping_params = launch_spec_params.get("BlockDeviceMappings", [])
        block_device_mappings = []
        for bdm in block_device_mapping_params:
            if not isinstance(bdm, dict):
                raise ValueError("Each BlockDeviceMapping must be a dict")
            ebs_params = bdm.get("Ebs")
            ebs_obj = None
            if ebs_params:
                if not isinstance(ebs_params, dict):
                    raise ValueError("Ebs in BlockDeviceMapping must be a dict")
                ebs_obj = EbsBlockDevice(**ebs_params)
            block_device_mappings.append(BlockDeviceMapping(
                DeviceName=bdm.get("DeviceName"),
                Ebs=ebs_obj,
                NoDevice=bdm.get("NoDevice"),
                VirtualName=bdm.get("VirtualName"),
            ))

        # Parse groupSet (list of GroupIdentifier)
        group_set_params = launch_spec_params.get("GroupSet", [])
        group_set = parse_list_of_objects(group_set_params, GroupIdentifier)

        # Parse iamInstanceProfile
        iam_profile_params = launch_spec_params.get("IamInstanceProfile")
        iam_instance_profile = None
        if iam_profile_params:
            if not isinstance(iam_profile_params, dict):
                raise ValueError("IamInstanceProfile must be a dict")
            iam_instance_profile = IamInstanceProfileSpecification(**iam_profile_params)

        # Parse monitoring
        monitoring_params = launch_spec_params.get("Monitoring")
        monitoring = None
        if monitoring_params:
            if not isinstance(monitoring_params, dict):
                raise ValueError("Monitoring must be a dict")
            monitoring = RunInstancesMonitoringEnabled(**monitoring_params)

        # Parse networkInterfaceSet
        network_interface_params = launch_spec_params.get("NetworkInterfaces", [])
        network_interface_set = []
        for ni in network_interface_params:
            if not isinstance(ni, dict):
                raise ValueError("Each NetworkInterface must be a dict")
            # Parse nested EnaSrdSpecification
            ena_srd_spec_params = ni.get("EnaSrdSpecification")
            ena_srd_spec = None
            if ena_srd_spec_params:
                if not isinstance(ena_srd_spec_params, dict):
                    raise ValueError("EnaSrdSpecification must be a dict")
                ena_srd_udp_spec_params = ena_srd_spec_params.get("EnaSrdUdpSpecification")
                ena_srd_udp_spec = None
                if ena_srd_udp_spec_params:
                    if not isinstance(ena_srd_udp_spec_params, dict):
                        raise ValueError("EnaSrdUdpSpecification must be a dict")
                    ena_srd_udp_spec = EnaSrdUdpSpecificationRequest(**ena_srd_udp_spec_params)
                ena_srd_spec = EnaSrdSpecificationRequest(
                    EnaSrdEnabled=ena_srd_spec_params.get("EnaSrdEnabled"),
                    EnaSrdUdpSpecification=ena_srd_udp_spec,
                )
            # Parse ConnectionTrackingSpecification
            connection_tracking_params = ni.get("ConnectionTrackingSpecification")
            connection_tracking_spec = None
            if connection_tracking_params:
                if not isinstance(connection_tracking_params, dict):
                    raise ValueError("ConnectionTrackingSpecification must be a dict")
                connection_tracking_spec = ConnectionTrackingSpecificationRequest(**connection_tracking_params)
            # Parse Ipv6Addresses
            ipv6_addresses_params = ni.get("Ipv6Addresses", [])
            ipv6_addresses = []
            for ipv6_addr in ipv6_addresses_params:
                if not isinstance(ipv6_addr, dict):
                    raise ValueError("Each Ipv6Address must be a dict")
                ipv6_addresses.append(InstanceIpv6Address(**ipv6_addr))
            # Parse PrivateIpAddresses
            private_ip_addresses_params = ni.get("PrivateIpAddresses", [])
            private_ip_addresses = []
            for private_ip in private_ip_addresses_params:
                if not isinstance(private_ip, dict):
                    raise ValueError("Each PrivateIpAddress must be a dict")
                private_ip_addresses.append(PrivateIpAddressSpecification(**private_ip))
            network_interface_set.append(InstanceNetworkInterfaceSpecification(
                AssociateCarrierIpAddress=ni.get("AssociateCarrierIpAddress"),
                AssociatePublicIpAddress=ni.get("AssociatePublicIpAddress"),
                ConnectionTrackingSpecification=connection_tracking_spec,
                DeleteOnTermination=ni.get("DeleteOnTermination"),
                Description=ni.get("Description"),
                DeviceIndex=ni.get("DeviceIndex"),
                EnaQueueCount=ni.get("EnaQueueCount"),
                EnaSrdSpecification=ena_srd_spec,
                InterfaceType=ni.get("InterfaceType"),
                Ipv4Prefixes=ni.get("Ipv4Prefixes"),
                Ipv4PrefixCount=ni.get("Ipv4PrefixCount"),
                Ipv6AddressCount=ni.get("Ipv6AddressCount"),
                Ipv6Addresses=ipv6_addresses,
                Ipv6Prefixes=ni.get("Ipv6Prefixes"),
                Ipv6PrefixCount=ni.get("Ipv6PrefixCount"),
                NetworkCardIndex=ni.get("NetworkCardIndex"),
                NetworkInterfaceId=ni.get("NetworkInterfaceId"),
                PrimaryIpv6=ni.get("PrimaryIpv6"),
                PrivateIpAddress=ni.get("PrivateIpAddress"),
                PrivateIpAddresses=private_ip_addresses,
                SecondaryPrivateIpAddressCount=ni.get("SecondaryPrivateIpAddressCount"),
                Groups=ni.get("Groups"),
                SubnetId=ni.get("SubnetId"),
            ))
    

from emulator_core.gateway.base import BaseGateway

class SpotInstancesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CancelSpotInstanceRequests", self.cancel_spot_instance_requests)
        self.register_action("CreateSpotDatafeedSubscription", self.create_spot_datafeed_subscription)
        self.register_action("DeleteSpotDatafeedSubscription", self.delete_spot_datafeed_subscription)
        self.register_action("DescribeSpotDatafeedSubscription", self.describe_spot_datafeed_subscription)
        self.register_action("DescribeSpotInstanceRequests", self.describe_spot_instance_requests)
        self.register_action("DescribeSpotPriceHistory", self.describe_spot_price_history)
        self.register_action("GetSpotPlacementScores", self.get_spot_placement_scores)
        self.register_action("RequestSpotInstances", self.request_spot_instances)

    def cancel_spot_instance_requests(self, params):
        return self.backend.cancel_spot_instance_requests(params)

    def create_spot_datafeed_subscription(self, params):
        return self.backend.create_spot_datafeed_subscription(params)

    def delete_spot_datafeed_subscription(self, params):
        return self.backend.delete_spot_datafeed_subscription(params)

    def describe_spot_datafeed_subscription(self, params):
        return self.backend.describe_spot_datafeed_subscription(params)

    def describe_spot_instance_requests(self, params):
        return self.backend.describe_spot_instance_requests(params)

    def describe_spot_price_history(self, params):
        return self.backend.describe_spot_price_history(params)

    def get_spot_placement_scores(self, params):
        return self.backend.get_spot_placement_scores(params)

    def request_spot_instances(self, params):
        return self.backend.request_spot_instances(params)
