from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


# Enums for various string fields with limited valid values

class IamInstanceProfileAssociationState(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"


class MacModificationTaskState(str, Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    IN_PROGRESS = "in-progress"
    PENDING = "pending"


class MacModificationTaskType(str, Enum):
    SIP_MODIFICATION = "sip-modification"
    VOLUME_OWNERSHIP_DELEGATION = "volume-ownership-delegation"


class MacSystemIntegrityProtectionConfigStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class CpuCreditsOption(str, Enum):
    STANDARD = "standard"
    UNLIMITED = "unlimited"


class InstanceStateName(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting-down"
    TERMINATED = "terminated"
    STOPPING = "stopping"
    STOPPED = "stopped"


class MonitoringState(str, Enum):
    DISABLED = "disabled"
    DISABLING = "disabling"
    ENABLED = "enabled"
    PENDING = "pending"


class InstanceLifecycle(str, Enum):
    SPOT = "spot"
    SCHEDULED = "scheduled"
    CAPACITY_BLOCK = "capacity-block"
    INTERRUPTIBLE_CAPACITY_RESERVATION = "interruptible-capacity-reservation"


class HypervisorType(str, Enum):
    OVM = "ovm"
    XEN = "xen"


class VirtualizationType(str, Enum):
    HVM = "hvm"
    PARAVIRTUAL = "paravirtual"


class InstanceStatusName(str, Enum):
    OK = "ok"
    IMPAIRED = "impaired"
    INITIALIZING = "initializing"
    INSUFFICIENT_DATA = "insufficient-data"
    NOT_APPLICABLE = "not-applicable"


class InstanceStatusDetailName(str, Enum):
    REACHABILITY = "reachability"


class InstanceStatusEventCode(str, Enum):
    INSTANCE_REBOOT = "instance-reboot"
    SYSTEM_REBOOT = "system-reboot"
    SYSTEM_MAINTENANCE = "system-maintenance"
    INSTANCE_RETIREMENT = "instance-retirement"
    INSTANCE_STOP = "instance-stop"


class InstanceStatusEventDescriptionPrefix(str, Enum):
    COMPLETED = "[Completed]"


# Data classes for nested objects

@dataclass
class IamInstanceProfile:
    arn: Optional[str] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "arn": self.arn,
            "id": self.id,
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
class IamInstanceProfileAssociation:
    association_id: Optional[str] = None
    iam_instance_profile: Optional[IamInstanceProfile] = None
    instance_id: Optional[str] = None
    state: Optional[IamInstanceProfileAssociationState] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "associationId": self.association_id,
            "iamInstanceProfile": self.iam_instance_profile.to_dict() if self.iam_instance_profile else None,
            "instanceId": self.instance_id,
            "state": self.state.value if self.state else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class Tag:
    Key: Optional[str] = None
    Value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Key": self.Key,
            "Value": self.Value,
        }


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
class MacSystemIntegrityProtectionConfiguration:
    appleInternal: Optional[MacSystemIntegrityProtectionConfigStatus] = None
    baseSystem: Optional[MacSystemIntegrityProtectionConfigStatus] = None
    debuggingRestrictions: Optional[MacSystemIntegrityProtectionConfigStatus] = None
    dTraceRestrictions: Optional[MacSystemIntegrityProtectionConfigStatus] = None
    filesystemProtections: Optional[MacSystemIntegrityProtectionConfigStatus] = None
    kextSigning: Optional[MacSystemIntegrityProtectionConfigStatus] = None
    nvramProtections: Optional[MacSystemIntegrityProtectionConfigStatus] = None
    status: Optional[MacSystemIntegrityProtectionConfigStatus] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "appleInternal": self.appleInternal.value if self.appleInternal else None,
            "baseSystem": self.baseSystem.value if self.baseSystem else None,
            "debuggingRestrictions": self.debuggingRestrictions.value if self.debuggingRestrictions else None,
            "dTraceRestrictions": self.dTraceRestrictions.value if self.dTraceRestrictions else None,
            "filesystemProtections": self.filesystemProtections.value if self.filesystemProtections else None,
            "kextSigning": self.kextSigning.value if self.kextSigning else None,
            "nvramProtections": self.nvramProtections.value if self.nvramProtections else None,
            "status": self.status.value if self.status else None,
        }


@dataclass
class MacModificationTask:
    instance_id: Optional[str] = None
    mac_modification_task_id: Optional[str] = None
    mac_system_integrity_protection_config: Optional[MacSystemIntegrityProtectionConfiguration] = None
    start_time: Optional[datetime] = None
    tag_set: List[Tag] = field(default_factory=list)
    task_state: Optional[MacModificationTaskState] = None
    task_type: Optional[MacModificationTaskType] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instanceId": self.instance_id,
            "macModificationTaskId": self.mac_modification_task_id,
            "macSystemIntegrityProtectionConfig": self.mac_system_integrity_protection_config.to_dict() if self.mac_system_integrity_protection_config else None,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "taskState": self.task_state.value if self.task_state else None,
            "taskType": self.task_type.value if self.task_type else None,
        }


@dataclass
class InstanceState:
    code: Optional[int] = None
    name: Optional[InstanceStateName] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name.value if self.name else None,
        }


@dataclass
class InstanceStatusDetails:
    impaired_since: Optional[datetime] = None
    name: Optional[InstanceStatusDetailName] = None
    status: Optional[InstanceStatusName] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "impairedSince": self.impaired_since.isoformat() if self.impaired_since else None,
            "name": self.name.value if self.name else None,
            "status": self.status.value if self.status else None,
        }


@dataclass
class InstanceStatusSummary:
    details: List[InstanceStatusDetails] = field(default_factory=list)
    status: Optional[InstanceStatusName] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "details": [detail.to_dict() for detail in self.details],
            "status": self.status.value if self.status else None,
        }


@dataclass
class InstanceStatusEvent:
    code: Optional[InstanceStatusEventCode] = None
    description: Optional[str] = None
    instance_event_id: Optional[str] = None
    not_after: Optional[datetime] = None
    not_before: Optional[datetime] = None
    not_before_deadline: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value if self.code else None,
            "description": self.description,
            "instanceEventId": self.instance_event_id,
            "notAfter": self.not_after.isoformat() if self.not_after else None,
            "notBefore": self.not_before.isoformat() if self.not_before else None,
            "notBeforeDeadline": self.not_before_deadline.isoformat() if self.not_before_deadline else None,
        }


@dataclass
class EbsStatusDetails:
    impaired_since: Optional[datetime] = None
    name: Optional[str] = None  # Only "reachability" is valid
    status: Optional[str] = None  # passed | failed | insufficient-data | initializing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "impairedSince": self.impaired_since.isoformat() if self.impaired_since else None,
            "name": self.name,
            "status": self.status,
        }


@dataclass
class EbsStatusSummary:
    details: List[EbsStatusDetails] = field(default_factory=list)
    status: Optional[str] = None  # ok | impaired | insufficient-data | not-applicable | initializing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "details": [detail.to_dict() for detail in self.details],
            "status": self.status,
        }


@dataclass
class InstanceStatus:
    attached_ebs_status: Optional[EbsStatusSummary] = None
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    events_set: List[InstanceStatusEvent] = field(default_factory=list)
    instance_id: Optional[str] = None
    instance_state: Optional[InstanceState] = None
    instance_status: Optional[InstanceStatusSummary] = None
    operator_managed: Optional[bool] = None
    operator_principal: Optional[str] = None
    outpost_arn: Optional[str] = None
    system_status: Optional[InstanceStatusSummary] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attachedEbsStatus": self.attached_ebs_status.to_dict() if self.attached_ebs_status else None,
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "eventsSet": [event.to_dict() for event in self.events_set],
            "instanceId": self.instance_id,
            "instanceState": self.instance_state.to_dict() if self.instance_state else None,
            "instanceStatus": self.instance_status.to_dict() if self.instance_status else None,
            "operator": {
                "managed": self.operator_managed,
                "principal": self.operator_principal,
            } if self.operator_managed is not None or self.operator_principal is not None else None,
            "outpostArn": self.outpost_arn,
            "systemStatus": self.system_status.to_dict() if self.system_status else None,
        }


# Additional data classes for nested complex types in instance descriptions can be added here as needed.
# For brevity, only key classes are defined above.

@dataclass
class Instance:
    instance_id: str
    image_id: Optional[str] = None
    instance_type: Optional[str] = None
    key_name: Optional[str] = None
    launch_time: Optional[datetime] = None
    monitoring: Optional[Dict[str, str]] = None
    placement: Optional[Dict[str, Any]] = None
    platform: Optional[str] = None
    private_dns_name: Optional[str] = None
    private_ip_address: Optional[str] = None
    product_codes: List[Dict[str, str]] = field(default_factory=list)
    public_dns_name: Optional[str] = None
    public_ip_address: Optional[str] = None
    ramdisk_id: Optional[str] = None
    state: Optional[InstanceState] = None
    state_transition_reason: Optional[str] = None
    subnet_id: Optional[str] = None
    vpc_id: Optional[str] = None
    reservation_id: Optional[str] = None  # Track which reservation this instance belongs to
    owner_id: Optional[str] = None  # Instance owner ID
    architecture: Optional[str] = "x86_64"
    block_device_mappings: List[Any] = field(default_factory=list)
    client_token: Optional[str] = None
    ebs_optimized: bool = False
    ena_support: bool = False
    hypervisor: Optional[str] = "xen"
    iam_instance_profile: Optional[Dict[str, str]] = None
    instance_lifecycle: Optional[str] = None
    network_interfaces: List[Any] = field(default_factory=list)
    root_device_name: Optional[str] = "/dev/sda1"
    root_device_type: Optional[str] = "ebs"
    security_groups: List[Dict[str, str]] = field(default_factory=list)
    source_dest_check: bool = True
    tags: List[Tag] = field(default_factory=list)
    virtualization_type: Optional[str] = "hvm"
    cpu_options: Optional[Dict[str, int]] = None
    capacity_reservation_id: Optional[str] = None
    capacity_reservation_specification: Optional[Dict[str, Any]] = None
    hibernation_options: Optional[Dict[str, bool]] = None
    metadata_options: Optional[Dict[str, Any]] = None
    enclave_options: Optional[Dict[str, bool]] = None
    boot_mode: Optional[str] = None
    platform_details: Optional[str] = None
    usage_operation: Optional[str] = None
    usage_operation_update_time: Optional[datetime] = None
    private_dns_name_options: Optional[Dict[str, Any]] = None
    ipv6_address: Optional[str] = None
    tpm_support: Optional[str] = None
    maintenance_options: Optional[Dict[str, str]] = None
    current_instance_boot_mode: Optional[str] = None
    disable_api_termination: bool = False  # Termination protection
    instance_initiated_shutdown_behavior: Optional[str] = "stop"  # "stop" or "terminate"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instanceId": self.instance_id,
            "imageId": self.image_id,
            "instanceType": self.instance_type,
            "keyName": self.key_name,
            "launchTime": self.launch_time.isoformat() if self.launch_time else None,
            "monitoring": self.monitoring,
            "placement": self.placement,
            "platform": self.platform,
            "privateDnsName": self.private_dns_name,
            "privateIpAddress": self.private_ip_address,
            "productCodes": self.product_codes,
            "publicDnsName": self.public_dns_name,
            "publicIpAddress": self.public_ip_address,
            "ramdiskId": self.ramdisk_id,
            "state": self.state.to_dict() if self.state else None,
            "stateTransitionReason": self.state_transition_reason,
            "subnetId": self.subnet_id,
            "vpcId": self.vpc_id,
            "architecture": self.architecture,
            "blockDeviceMappings": self.block_device_mappings,
            "clientToken": self.client_token,
            "ebsOptimized": self.ebs_optimized,
            "enaSupport": self.ena_support,
            "hypervisor": self.hypervisor,
            "iamInstanceProfile": self.iam_instance_profile,
            "instanceLifecycle": self.instance_lifecycle,
            "networkInterfaces": self.network_interfaces,
            "rootDeviceName": self.root_device_name,
            "rootDeviceType": self.root_device_type,
            "securityGroups": self.security_groups,
            "sourceDestCheck": self.source_dest_check,
            "tagSet": [{"Key": t.Key, "Value": t.Value} for t in self.tags],
            "virtualizationType": self.virtualization_type,
            "cpuOptions": self.cpu_options,
            "capacityReservationId": self.capacity_reservation_id,
            "capacityReservationSpecification": self.capacity_reservation_specification,
            "hibernationOptions": self.hibernation_options,
            "metadataOptions": self.metadata_options,
            "enclaveOptions": self.enclave_options,
            "bootMode": self.boot_mode,
            "platformDetails": self.platform_details,
            "usageOperation": self.usage_operation,
            "usageOperationUpdateTime": self.usage_operation_update_time.isoformat() if self.usage_operation_update_time else None,
            "privateDnsNameOptions": self.private_dns_name_options,
            "ipv6Address": self.ipv6_address,
            "tpmSupport": self.tpm_support,
            "maintenanceOptions": self.maintenance_options,
            "currentInstanceBootMode": self.current_instance_boot_mode,
        }


@dataclass
class Reservation:
    reservation_id: Optional[str] = None
    owner_id: Optional[str] = None
    requester_id: Optional[str] = None
    group_set: List[Any] = field(default_factory=list)  # GroupIdentifier objects
    instances_set: List[Instance] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reservationId": self.reservation_id,
            "ownerId": self.owner_id,
            "requesterId": self.requester_id,
            "groupSet": self.group_set,
            "instancesSet": [instance.to_dict() for instance in self.instances_set],
        }


class InstancesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage. Use self.state.instances or similar shared state dict.

    def _allocate_private_ip(self, subnet_id: str) -> str:
        """Allocate a private IP address from the subnet's CIDR block."""
        subnet = self.state.subnets.get(subnet_id)
        if not subnet or not subnet.cidr_block:
            # Fallback to mock IP if subnet doesn't have CIDR
            return f"10.0.1.{len(self.state.instances) + 10}"
        
        try:
            import ipaddress
            # Parse subnet CIDR
            subnet_net = ipaddress.ip_network(subnet.cidr_block, strict=False)
            # Get all IPs in subnet (excluding network and broadcast)
            available_ips = list(subnet_net.hosts())
            
            # Find used IPs from existing instances in this subnet
            used_ips = set()
            for instance in self.state.instances.values():
                if hasattr(instance, "subnet_id") and instance.subnet_id == subnet_id:
                    if hasattr(instance, "private_ip_address") and instance.private_ip_address:
                        try:
                            used_ips.add(ipaddress.ip_address(instance.private_ip_address))
                        except Exception:
                            pass
            
            # Find first available IP
            for ip in available_ips:
                if ip not in used_ips:
                    return str(ip)
            
            # If all IPs are used, return a mock IP (shouldn't happen in practice)
            return f"10.0.1.{len(self.state.instances) + 10}"
        except Exception:
            # Fallback on any error
            return f"10.0.1.{len(self.state.instances) + 10}"

    def associate_iam_instance_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        iam_instance_profile_spec = params.get("IamInstanceProfile")
        instance_id = params.get("InstanceId")

        if not iam_instance_profile_spec or not instance_id:
            raise ValueError("Both 'IamInstanceProfile' and 'InstanceId' are required parameters")

        # Validate instance exists
        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance with id {instance_id} does not exist")

        # Check if instance already has an IAM instance profile association
        for assoc in self.state.iam_instance_profile_associations.values():
            if assoc.instance_id == instance_id and assoc.state in {
                IamInstanceProfileAssociationState.associating,
                IamInstanceProfileAssociationState.associated,
            }:
                raise ValueError("Instance already has an IAM instance profile associated")

        # Create new association
        association_id = self.generate_unique_id(prefix="iip-assoc-")
        iam_instance_profile = IamInstanceProfile(
            arn=iam_instance_profile_spec.get("Arn"),
            id=None  # ID is not provided in request, can be None or generated if needed
        )
        association = IamInstanceProfileAssociation(
            association_id=association_id,
            iam_instance_profile=iam_instance_profile,
            instance_id=instance_id,
            state=IamInstanceProfileAssociationState.associating,
            timestamp=datetime.utcnow(),
        )
        self.state.iam_instance_profile_associations[association_id] = association

        return {
            "iamInstanceProfileAssociation": association.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_delegate_mac_volume_ownership_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        mac_credentials = params.get("MacCredentials")
        tag_specifications = params.get("TagSpecification.N", [])

        if not instance_id:
            raise ValueError("'InstanceId' is a required parameter")
        if not mac_credentials:
            raise ValueError("'MacCredentials' is a required parameter")

        # Validate instance exists
        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance with id {instance_id} does not exist")

        # Create tags from tag specifications
        tags = []
        for tag_spec in tag_specifications:
            for tag in tag_spec.get("Tags", []):
                tags.append(Tag(Key=tag.get("Key"), Value=tag.get("Value")))

        # Create MacModificationTask for volume ownership delegation
        task_id = self.generate_unique_id(prefix="mmt-")
        task = MacModificationTask(
            instance_id=instance_id,
            mac_modification_task_id=task_id,
            mac_system_integrity_protection_config=None,
            start_time=datetime.utcnow(),
            tag_set=tags,
            task_state=MacModificationTaskState.pending,
            task_type=MacModificationTaskType.volume_ownership_delegation,
        )
        self.state.mac_modification_tasks[task_id] = task

        return {
            "macModificationTask": task.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_mac_system_integrity_protection_modification_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        mac_system_integrity_protection_status = params.get("MacSystemIntegrityProtectionStatus")
        mac_system_integrity_protection_config = params.get("MacSystemIntegrityProtectionConfiguration")
        tag_specifications = params.get("TagSpecification.N", [])

        if not instance_id:
            raise ValueError("'InstanceId' is a required parameter")
        if not mac_system_integrity_protection_status:
            raise ValueError("'MacSystemIntegrityProtectionStatus' is a required parameter")

        # Validate instance exists
        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance with id {instance_id} does not exist")

        # Create tags from tag specifications
        tags = []
        for tag_spec in tag_specifications:
            for tag in tag_spec.get("Tags", []):
                tags.append(Tag(Key=tag.get("Key"), Value=tag.get("Value")))

        # Build MacSystemIntegrityProtectionConfiguration object if config provided
        config_obj = None
        if mac_system_integrity_protection_config:
            config_obj = MacSystemIntegrityProtectionConfiguration(
                appleInternal=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_config.get("AppleInternal")) if mac_system_integrity_protection_config.get("AppleInternal") else None,
                baseSystem=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_config.get("BaseSystem")) if mac_system_integrity_protection_config.get("BaseSystem") else None,
                debuggingRestrictions=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_config.get("DebuggingRestrictions")) if mac_system_integrity_protection_config.get("DebuggingRestrictions") else None,
                dTraceRestrictions=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_config.get("DTraceRestrictions")) if mac_system_integrity_protection_config.get("DTraceRestrictions") else None,
                filesystemProtections=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_config.get("FilesystemProtections")) if mac_system_integrity_protection_config.get("FilesystemProtections") else None,
                kextSigning=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_config.get("KextSigning")) if mac_system_integrity_protection_config.get("KextSigning") else None,
                nvramProtections=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_config.get("NvramProtections")) if mac_system_integrity_protection_config.get("NvramProtections") else None,
                status=MacSystemIntegrityProtectionConfigStatus(mac_system_integrity_protection_status),
            )

        # Create MacModificationTask for SIP modification
        task_id = self.generate_unique_id(prefix="mmt-")
        task = MacModificationTask(
            instance_id=instance_id,
            mac_modification_task_id=task_id,
            mac_system_integrity_protection_config=config_obj,
            start_time=datetime.utcnow(),
            tag_set=tags,
            task_state=MacModificationTaskState.pending,
            task_type=MacModificationTaskType.sip_modification,
        )
        self.state.mac_modification_tasks[task_id] = task

        return {
            "macModificationTask": task.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def describe_iam_instance_profile_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        association_ids = params.get("AssociationId.N", [])
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect all associations
        associations = list(self.state.iam_instance_profile_associations.values())

        # Filter by association ids if provided
        if association_ids:
            associations = [assoc for assoc in associations if assoc.association_id in association_ids]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            if name == "instance-id":
                associations = [assoc for assoc in associations if assoc.instance_id in values]
            elif name == "state":
                associations = [assoc for assoc in associations if assoc.state and assoc.state.value in values]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results = max_results or 1000
        max_results = max(5, min(max_results, 1000))

        paged_associations = associations[start_index : start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(associations) else None

        return {
            "iamInstanceProfileAssociationSet": [assoc.to_dict() for assoc in paged_associations],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_instance_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attribute = params.get("Attribute")
        instance_id = params.get("InstanceId")

        if not attribute or not instance_id:
            raise ValueError("'Attribute' and 'InstanceId' are required parameters")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance with id {instance_id} does not exist")

        # Prepare response dict
        response = {
            "requestId": self.generate_request_id(),
            "instanceId": instance_id,
        }

        # Attributes supported (based on description)
        # For simplicity, we assume instance object has attributes stored in a dict or as attributes
        # We will simulate some attributes with dummy values or from instance if available

        # Helper to build AttributeValue or AttributeBooleanValue dict
        def attr_value(val):
            if isinstance(val, bool):
                return {"Value": val}
            else:
                return {"Value": val}

        # Simulated attributes for demonstration
        # In real implementation, these would be fetched from instance properties
        instance_attributes = getattr(instance, "attributes", {})

        if attribute == "instanceType":
            value = instance_attributes.get("instanceType", "t2.micro")
            response["instanceType"] = {"value": value}
        elif attribute == "kernel":
            value = instance_attributes.get("kernel", None)
            response["kernel"] = {"value": value} if value else {}
        elif attribute == "ramdisk":
            value = instance_attributes.get("ramdisk", None)
            response["ramdisk"] = {"value": value} if value else {}
        elif attribute == "userData":
            value = instance_attributes.get("userData", None)
            response["userData"] = {"value": value} if value else {}
        elif attribute == "disableApiTermination":
            value = instance_attributes.get("disableApiTermination", False)
            response["disableApiTermination"] = attr_value(value)
        elif attribute == "disableApiStop":
            value = instance_attributes.get("disableApiStop", False)
            response["disableApiStop"] = attr_value(value)
        elif attribute == "instanceInitiatedShutdownBehavior":
            value = instance_attributes.get("instanceInitiatedShutdownBehavior", "stop")
            response["instanceInitiatedShutdownBehavior"] = {"value": value}
        elif attribute == "rootDeviceName":
            value = instance_attributes.get("rootDeviceName", "/dev/sda1")
            response["rootDeviceName"] = {"value": value}
        elif attribute == "blockDeviceMapping":
            # For simplicity, return empty list or from instance
            block_devices = instance_attributes.get("blockDeviceMapping", [])
            response["blockDeviceMapping"] = [bd.to_dict() for bd in block_devices]
        elif attribute == "productCodes":
            product_codes = instance_attributes.get("productCodes", [])
            response["productCodes"] = [pc.to_dict() for pc in product_codes]
        elif attribute == "sourceDestCheck":
            value = instance_attributes.get("sourceDestCheck", True)
            response["sourceDestCheck"] = attr_value(value)
        elif attribute == "ebsOptimized":
            value = instance_attributes.get("ebsOptimized", False)
            response["ebsOptimized"] = attr_value(value)
        elif attribute == "enaSupport":
            value = instance_attributes.get("enaSupport", False)
            response["enaSupport"] = attr_value(value)
        elif attribute == "enclaveOptions":
            enclave_enabled = instance_attributes.get("enclaveOptions", {}).get("enabled", False)
            response["enclaveOptions"] = {"enabled": enclave_enabled}
        elif attribute == "groupSet":
            groups = instance_attributes.get("groupSet", [])
            response["groupSet"] = [g.to_dict() for g in groups]
        elif attribute == "sriovNetSupport":
            value = instance_attributes.get("sriovNetSupport", None)
            response["sriovNetSupport"] = {"value": value} if value else {}
        else:
            # Unsupported attribute
            raise ValueError(f"Unsupported attribute: {attribute}")

        return response

    def describe_instance_credit_specifications(self, params: dict) -> dict:
        instance_ids = params.get("InstanceId", [])
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate max_results if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Validate instance_ids count if provided
        if instance_ids and len(instance_ids) > 1000:
            raise ValueError("Maximum 1000 instance IDs can be specified")

        # Filter instances by instance_ids if provided, else all instances
        instances = []
        if instance_ids:
            for instance_id in instance_ids:
                instance = self.state.instances.get(instance_id)
                if instance:
                    instances.append(instance)
        else:
            instances = list(self.state.instances.values())

        # Apply filters if provided
        def matches_filter(instance, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # No filter criteria, match all

            # Only support filter on instance-id for now as per description
            if name == "instance-id":
                return instance.instance_id in values
            # Other filters are not specified for this API, so ignore
            return True

        if filters:
            filtered_instances = []
            for instance in instances:
                if all(matches_filter(instance, f) for f in filters):
                    filtered_instances.append(instance)
            instances = filtered_instances

        # Pagination handling
        # next_token is a string token, we will treat it as an integer offset encoded as string
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Slice instances according to max_results and next_token
        if max_results is None:
            max_results = 1000  # default max

        end_index = start_index + max_results
        paged_instances = instances[start_index:end_index]

        # Prepare response list
        instance_credit_specification_set = []
        for instance in paged_instances:
            # Determine cpuCredits option
            # According to description:
            # - If instance is burstable performance instance (T2, T3, T3a), return its credit option (standard or unlimited)
            # - If instance is not burstable, error is returned if specified in instance_ids, else skip
            # For simplicity, we assume instance has attribute 'instance_type' and we check if it is burstable
            # We will assume instance has attribute 'cpu_credits' which is either 'standard' or 'unlimited'
            # If not present, default to 'standard' for burstable, else skip

            # Define burstable instance types prefixes
            burstable_prefixes = ("t2.", "t3.", "t3a.", "t4g.")
            instance_type = getattr(instance, "instance_type", "").lower()
            is_burstable = any(instance_type.startswith(prefix) for prefix in burstable_prefixes)

            if instance_ids and not is_burstable:
                # If instance id specified and instance is not burstable, error
                raise Exception(f"InvalidInstanceID.NotFound: The instance ID {instance.instance_id} is not a burstable performance instance")

            if is_burstable:
                cpu_credits = getattr(instance, "cpu_credits", "standard")
                if cpu_credits not in ("standard", "unlimited"):
                    cpu_credits = "standard"
                instance_credit_specification_set.append({
                    "instanceId": instance.instance_id,
                    "cpuCredits": cpu_credits,
                })
            else:
                # If instance is not burstable and not specified in instance_ids, skip
                if not instance_ids:
                    # According to description, return burstable instances with unlimited credit option and previously configured as T2, T3, T3a with unlimited
                    # For simplicity, skip non-burstable instances
                    continue

        # Prepare next token if more results
        response_next_token = None
        if end_index < len(instances):
            response_next_token = str(end_index)

        return {
            "instanceCreditSpecificationSet": instance_credit_specification_set,
            "nextToken": response_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_instances(self, params: dict) -> dict:
        instance_ids = params.get("InstanceId", [])
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate max_results if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Filter instances by instance_ids if provided, else all instances
        instances = []
        if instance_ids:
            for instance_id in instance_ids:
                instance = self.state.instances.get(instance_id)
                if instance:
                    instances.append(instance)
        else:
            instances = list(self.state.instances.values())

        # Helper function to check if instance matches a single filter
        def matches_filter(instance, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # no filter criteria, match all

            # Support common filters for DescribeInstances
            # We will implement a subset of filters for demonstration and correctness
            # For full support, more attributes and logic would be needed

            # Normalize filter name to lowercase for matching
            lname = name.lower()

            # Instance ID filter
            if lname == "instance-id":
                return instance.instance_id in values

            # Instance type filter
            if lname == "instance-type":
                return getattr(instance, "instance_type", None) in values

            # Availability zone filter
            if lname == "availability-zone":
                placement = getattr(instance, "placement", None)
                if placement:
                    az = getattr(placement, "availability_zone", None)
                    return az in values
                return False

            # Tag key filter: tag-key
            if lname == "tag-key":
                instance_tags = getattr(instance, "tags", [])
                tag_keys = [tag.Key for tag in instance_tags if tag.Key is not None]
                return any(v in tag_keys for v in values)

            # Tag key and value filter: tag:<key>
            if lname.startswith("tag:"):
                tag_key = name[4:]
                instance_tags = getattr(instance, "tags", [])
                for tag in instance_tags:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False

            # VPC ID filter
            if lname == "vpc-id":
                vpc_id = getattr(instance, "vpc_id", None)
                return vpc_id in values

            # Subnet ID filter
            if lname == "subnet-id":
                subnet_id = getattr(instance, "subnet_id", None)
                return subnet_id in values

            # Instance state name filter
            if lname == "instance-state-name":
                state = getattr(instance, "state", None)
                if state:
                    return state.name in values
                return False

            # Key name filter
            if lname == "key-name":
                key_name = getattr(instance, "key_name", None)
                return key_name in values

            # Platform filter (windows or empty)
            if lname == "platform":
                platform = getattr(instance, "platform", None)
                # platform is "windows" or None
                return (platform or "") in values

            # Default: no match
            return False

        # Apply filters if provided
        if filters:
            filtered_instances = []
            for instance in instances:
                if all(matches_filter(instance, f) for f in filters):
                    filtered_instances.append(instance)
            instances = filtered_instances

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000

        end_index = start_index + max_results
        paged_instances = instances[start_index:end_index]

        # Group instances by reservation_id
        reservations_map = {}
        for instance in paged_instances:
            reservation_id = getattr(instance, "reservation_id", None)
            if reservation_id not in reservations_map:
                reservations_map[reservation_id] = {
                    "reservation_id": reservation_id,
                    "owner_id": getattr(instance, "owner_id", None),
                    "requester_id": getattr(instance, "requester_id", None),
                    "group_set": [],  # Not supported, empty list
                    "instances_set": [],
                }
            reservations_map[reservation_id]["instances_set"].append(instance)

        # Convert reservations to list and to dict form
        reservation_list = []
        for res in reservations_map.values():
            # Convert instances to dict
            instances_dict_list = [inst.to_dict() for inst in res["instances_set"]]
            reservation_list.append({
                "reservationId": res["reservation_id"],
                "ownerId": res["owner_id"],
                "requesterId": res["requester_id"],
                "groupSet": res["group_set"],
                "instancesSet": instances_dict_list,
            })

        # Prepare next token if more results
        response_next_token = None
        if end_index < len(instances):
            response_next_token = str(end_index)

        return {
            "reservationSet": reservation_list,
            "nextToken": response_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_instance_status(self, params: dict) -> dict:
        instance_ids = params.get("InstanceId", [])
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        include_all = params.get("IncludeAllInstances", False)

        # Validate max_results if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 100")

        # Filter instances by instance_ids if provided, else all instances
        instances = []
        if instance_ids:
            for instance_id in instance_ids:
                instance = self.state.instances.get(instance_id)
                if instance:
                    instances.append(instance)
        else:
            instances = list(self.state.instances.values())

        # By default, only running instances are described unless IncludeAllInstances is True
        if not include_all:
            filtered = []
            for instance in instances:
                state = getattr(instance, "state", None)
                if state and state.name == "running":
                    filtered.append(instance)
            instances = filtered

        # Helper function to check if instance status matches a single filter
        def matches_filter(instance, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True

            lname = name.lower()

            # availability-zone filter
            if lname == "availability-zone":
                placement = getattr(instance, "placement", None)
                if placement:
                    az = getattr(placement, "availability_zone", None)
                    return az in values
                return False

            # availability-zone-id filter
            if lname == "availability-zone-id":
                placement = getattr(instance, "placement", None)
                if placement:
                    az_id = getattr(placement, "availability_zone_id", None)
                    return az_id in values
                return False

            # instance-state-code filter
            if lname == "instance-state-code":
                state = getattr(instance, "state", None)
                if state and state.code is not None:
                    return str(state.code) in values or state.code in [int(v) for v in values if v.isdigit()]
                return False

            # instance-state-name filter
            if lname == "instance-state-name":
                state = getattr(instance, "state", None)
                if state:
                    return state.name in values
                return False

            # operator.managed filter
            if lname == "operator.managed":
                operator = getattr(instance, "operator", None)
                if operator:
                    managed = getattr(operator, "managed", None)
                    # values are strings "true" or "false"
                    str_managed = "true" if managed else "false"
                    return str_managed in [v.lower() for v in values]
                return False

            # operator.principal filter
            if lname == "operator.principal":
                operator = getattr(instance, "operator", None)
                if operator:
                    principal = getattr(operator, "principal", None)
                    return principal in values
                return False

            # event.code filter
            if lname == "event.code":
                # instance status events
                status = getattr(instance, "status", None)
                if status:
                    events = getattr(status, "events_set", [])
                    for event in events:
                        if event.code in values:
                            return True
                return False

            # event.description filter
            if lname == "event.description":
                status = getattr(instance, "status", None)
                if status:
                    events = getattr(status, "events_set", [])
                    for event in events:
                        if event.description and any(v in event.description for v in values):
                            return True
                return False

            # attached-ebs-status.status filter
            if lname == "attached-ebs-status.status":
                status = getattr(instance, "status", None)
                if status:
                    ebs_status = getattr(status, "attached_ebs_status", None)
                    if ebs_status and ebs_status.status in values:
                        return True
                return False

            # instance-status.status filter
            if lname == "instance-status.status":
                status = getattr(instance, "status", None)
                if status:
                    inst_status = getattr(status, "instance_status", None)
                    if inst_status and inst_status.status in values:
                        return True
                return False

            # system-status.status filter
            if lname == "system-status.status":
                status = getattr(instance, "status", None)
                if status:
                    sys_status = getattr(status, "system_status", None)
                    if sys_status and sys_status.status in values:
                        return True
                return False

            # instance-status.reachability filter
            if lname == "instance-status.reachability":
                status = getattr(instance, "status", None)
                if status:
                    inst_status = getattr(status, "instance_status", None)
                    if inst_status:
                        for detail in getattr(inst_status, "details", []):
                            if detail.name == "reachability" and detail.status in values:
                                return True
                return False

            # system-status.reachability filter
            if lname == "system-status.reachability":
                status = getattr(instance, "status", None)
                if status:
                    sys_status = getattr(status, "system_status", None)
                    if sys_status:
                        for detail in getattr(sys_status, "details", []):
                            if detail.name == "reachability" and detail.status in values:
                                return True
                return False

            return False

        # Apply filters if provided
        if filters:
            filtered_instances = []
            for instance in instances:
                if all(matches_filter(instance, f) for f in filters):
                    filtered_instances.append(instance)
            instances = filtered_instances

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 100

        end_index = start_index + max_results
        paged_instances = instances[start_index:end_index]

        # Prepare instanceStatusSet response
        instance_status_set = []
        for instance in paged_instances:
            status = getattr(instance, "status", None)
            if not status:
                # Create default InstanceStatus object with minimal info
                from datetime import datetime
                from copy import deepcopy
                instance_state = getattr(instance, "state", None)
                if not instance_state:
                    # Create default state
                    instance_state = InstanceState(code=0, name="pending")
                instance_status_obj = InstanceStatus(
                    attached_ebs_status=None,
                    availability_zone=getattr(instance.placement, "availability_zone", None) if getattr(instance, "placement", None) else None,
                    availability_zone_id=getattr(instance.placement, "availability_zone_id", None) if getattr(instance, "placement", None) else None,
                    events_set=[],
                    instance_id=instance.instance_id,
                    instance_state=instance_state,
                    instance_status=None,
                    operator=getattr(instance, "operator", None),
                    operator_principal=getattr(instance.operator, "principal", None) if getattr(instance, "operator", None) else None,
                    outpost_arn=getattr(instance, "outpost_arn", None),
                    system_status=None,
                )
                status = instance_status_obj

            instance_status_set.append(status.to_dict())

        # Prepare next token if more results
        response_next_token = None
        if end_index < len(instances):
            response_next_token = str(end_index)

        return {
            "instanceStatusSet": instance_status_set,
            "nextToken": response_next_token,
            "requestId": self.generate_request_id(),
        }


    def disassociate_iam_instance_profile(self, params: dict) -> dict:
        association_id = params.get("AssociationId")
        if not association_id:
            raise ValueError("AssociationId is required")

        # Find the association by association_id
        association = None
        for assoc in self.state.iam_instance_profile_associations.values():
            if assoc.association_id == association_id:
                association = assoc
                break

        if not association:
            raise Exception(f"IAMInstanceProfileAssociationNotFound: AssociationId {association_id} not found")

        # Change state to disassociating
        association.state = "disassociating"
        # Update timestamp to now
        from datetime import datetime
        association.timestamp = datetime.utcnow()

        # Save back to state (assuming state.iam_instance_profile_associations is a dict keyed by association_id)
        self.state.iam_instance_profile_associations[association_id] = association

        return {
            "iamInstanceProfileAssociation": association.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def get_console_output(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        if not instance_id:
            raise ValueError("InstanceId is required")

        latest = params.get("Latest", False)

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID {instance_id} does not exist")

        # For simplicity, assume instance has attribute console_output which is a dict with keys:
        # 'output' (base64 string), 'timestamp' (datetime)
        # If not present, return empty output and no

    def get_console_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        dry_run = params.get("DryRun", False)
        wake_up = params.get("WakeUp", False)

        if not instance_id:
            raise ValueError("InstanceId is required")

        # DryRun check
        if dry_run:
            # Here we simulate permission check; in real AWS, it returns error if no permission
            # For emulator, assume permission granted and raise DryRunOperation error
            # But since no error classes are defined, just return error dict or raise Exception
            # We'll raise Exception with message "DryRunOperation"
            raise Exception("DryRunOperation")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        # WakeUp parameter is ignored in this emulator, but could be logged or handled if needed

        # For the emulator, generate a dummy base64-encoded JPG image data string
        # In real AWS, this would be the actual screenshot data
        # We'll use a fixed dummy string for simplicity
        dummy_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAUA" \
                           "AAAFCAYAAACNbyblAAAAHElEQVQI12P4" \
                           "//8/w38GIAXDIBKE0DHxgljNBAAO" \
                           "9TXL0Y4OHwAAAABJRU5ErkJggg=="

        response = {
            "requestId": self.generate_request_id(),
            "imageData": dummy_image_data,
            "instanceId": instance_id,
        }
        return response


    def get_default_credit_specification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        instance_family = params.get("InstanceFamily")

        if not instance_family:
            raise ValueError("InstanceFamily is required")

        valid_families = {"t2", "t3", "t3a", "t4g"}
        if instance_family not in valid_families:
            raise Exception(f"InvalidInstanceFamily: The instance family '{instance_family}' is not valid")

        # DryRun check
        if dry_run:
            raise Exception("DryRunOperation")

        # For the emulator, define default credit specs per family
        # We'll assume 'unlimited' for all valid families as default
        cpu_credits = "unlimited"

        response = {
            "requestId": self.generate_request_id(),
            "instanceFamilyCreditSpecification": {
                "instanceFamily": instance_family,
                "cpuCredits": cpu_credits,
            },
        }
        return response


    def get_instance_metadata_defaults(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)

        # DryRun check
        if dry_run:
            raise Exception("DryRunOperation")

        # For the emulator, provide default IMDS settings at account level
        account_level = {
            "httpEndpoint": "enabled",
            "httpPutResponseHopLimit": 1,
            "httpTokens": "optional",
            "instanceMetadataTags": "enabled",
            "managedBy": "account",
            "managedExceptionMessage": None,
        }

        response = {
            "requestId": self.generate_request_id(),
            "accountLevel": account_level,
        }
        return response


    def get_instance_uefi_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        dry_run = params.get("DryRun", False)

        if not instance_id:
            raise ValueError("InstanceId is required")

        # DryRun check
        if dry_run:
            raise Exception("DryRunOperation")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        # For the emulator, provide dummy base64-encoded UEFI data
        dummy_uefi_data = "UEVHSU5FUl9ERU1PX1VFRkk="  # Base64 for "PEGINER_DEMO_UEFI"

        response = {
            "requestId": self.generate_request_id(),
            "instanceId": instance_id,
            "uefiData": dummy_uefi_data,
        }
        return response


    def get_password_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        dry_run = params.get("DryRun", False)

        if not instance_id:
            raise ValueError("InstanceId is required")

        # DryRun check
        if dry_run:
            raise Exception("DryRunOperation")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        # For the emulator, provide dummy encrypted password data or empty string if not Windows
        # Since we don't have OS info, assume all instances have password data for demo
        dummy_password_data = "VGhpcyBpcyBhIGR1bW15IGVuY3J5cHRlZCBwYXNzd29yZA=="  # Base64 for "This is a dummy encrypted password"

        timestamp = datetime.utcnow()

        response = {
            "requestId": self.generate_request_id(),
            "instanceId": instance_id,
            "passwordData": dummy_password_data,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return response

    def modify_default_credit_specification(self, params: dict) -> dict:
        cpu_credits = params.get("CpuCredits")
        instance_family = params.get("InstanceFamily")
        dry_run = params.get("DryRun", False)

        # Validate required parameters
        if cpu_credits is None:
            raise ValueError("CpuCredits is required")
        if instance_family is None:
            raise ValueError("InstanceFamily is required")

        # Validate CpuCredits values
        valid_cpu_credits = {"standard", "unlimited"}
        if cpu_credits not in valid_cpu_credits:
            raise ValueError(f"Invalid CpuCredits value: {cpu_credits}")

        # Validate InstanceFamily values
        valid_instance_families = {"t2", "t3", "t3a", "t4g"}
        if instance_family not in valid_instance_families:
            raise ValueError(f"Invalid InstanceFamily value: {instance_family}")

        # DryRun check (simulate permission check)
        if dry_run:
            # In real AWS, this would check permissions and raise DryRunOperation or UnauthorizedOperation
            # Here we just simulate success
            return {
                "requestId": self.generate_request_id(),
                "instanceFamilyCreditSpecification": {
                    "cpuCredits": cpu_credits,
                    "instanceFamily": instance_family,
                },
            }

        # Store the default credit specification in state
        if not hasattr(self.state, "default_credit_specifications"):
            self.state.default_credit_specifications = {}

        self.state.default_credit_specifications[instance_family] = cpu_credits

        return {
            "requestId": self.generate_request_id(),
            "instanceFamilyCreditSpecification": {
                "cpuCredits": cpu_credits,
                "instanceFamily": instance_family,
            },
        }


    def modify_instance_attribute(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        if not instance_id:
            raise ValueError("InstanceId is required")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        # DryRun check
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {"requestId": self.generate_request_id(), "return": True}

        # Attributes that can be modified
        # We will handle the attributes as per the AWS API doc
        # Only one attribute can be modified per call

        # Helper to get nested Value field if present
        def get_value(field_name):
            val = params.get(field_name)
            if isinstance(val, dict) and "Value" in val:
                return val["Value"]
            return val

        # DisableApiTermination
        if "DisableApiTermination" in params:
            val = get_value("DisableApiTermination")
            if val is not None:
                instance.disable_api_termination = bool(val)

        # InstanceType
        if "InstanceType" in params:
            val = get_value("InstanceType")
            if val:
                # In real AWS, instance must be stopped to change type
                # Here we just set it
                instance.instance_type = val

        # Kernel
        if "Kernel" in params:
            val = get_value("Kernel")
            if val is not None:
                instance.kernel = val

        # Ramdisk
        if "Ramdisk" in params:
            val = get_value("Ramdisk")
            if val is not None:
                instance.ramdisk = val

        # InstanceInitiatedShutdownBehavior
        if "InstanceInitiatedShutdownBehavior" in params:
            val = get_value("InstanceInitiatedShutdownBehavior")
            if val is not None:
                instance.instance_initiated_shutdown_behavior = val

        # UserData
        if "UserData" in params:
            val = get_value("UserData")
            if val is not None:
                instance.user_data = val

        # DisableApiStop
        if "DisableApiStop" in params:
            val = get_value("DisableApiStop")
            if val is not None:
                instance.disable_api_stop = bool(val)

        # EbsOptimized
        if "EbsOptimized" in params:
            val = get_value("EbsOptimized")
            if val is not None:
                instance.ebs_optimized = bool(val)

        # EnaSupport
        if "EnaSupport" in params:
            val = get_value("EnaSupport")
            if val is not None:
                instance.ena_support = bool(val)

        # SourceDestCheck
        if "SourceDestCheck" in params:
            val = get_value("SourceDestCheck")
            if val is not None:
                instance.source_dest_check = bool(val)

        # SriovNetSupport
        if "SriovNetSupport" in params:
            val = get_value("SriovNetSupport")
            if val is not None:
                instance.sriov_net_support = val

        # GroupId.N (security groups)
        group_ids = []
        for key, value in params.items():
            if key.startswith("GroupId."):
                group_ids.append(value)
        if group_ids:
            instance.security_groups = group_ids

        # BlockDeviceMapping.N
        block_device_mappings = []
        for key, value in params.items():
            if key.startswith("BlockDeviceMapping."):
                block_device_mappings.append(value)
        if block_device_mappings:
            # For simplicity, replace instance block device mappings with new ones
            instance.block_device_mappings = block_device_mappings

        return {"requestId": self.generate_request_id(), "return": True}


    def modify_instance_cpu_options(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        core_count = params.get("CoreCount")
        threads_per_core = params.get("ThreadsPerCore")
        dry_run = params.get("DryRun", False)

        if not instance_id:
            raise ValueError("InstanceId is required")
        if core_count is None:
            raise ValueError("CoreCount is required")
        if threads_per_core is None:
            raise ValueError("ThreadsPerCore is required")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "instanceId": instance_id,
                "coreCount": core_count,
                "threadsPerCore": threads_per_core,
            }

        # Instance must be stopped to modify CPU options
        if getattr(instance, "state", None) and getattr(instance.state, "name", None):
            if instance.state.name != InstanceStateName.STOPPED:
                raise ValueError("Instance must be stopped to modify CPU options")

        # Set CPU options on instance
        instance.cpu_options = {
            "CoreCount": core_count,
            "ThreadsPerCore": threads_per_core,
        }

        return {
            "requestId": self.generate_request_id(),
            "instanceId": instance_id,
            "coreCount": core_count,
            "threadsPerCore": threads_per_core,
        }


    def modify_instance_credit_specification(self, params: dict) -> dict:
        instance_credit_specifications = params.get("InstanceCreditSpecification.N")
        dry_run = params.get("DryRun", False)

        if not instance_credit_specifications:
            raise ValueError("InstanceCreditSpecification.N is required")

        # Prepare response sets
        successful = []
        unsuccessful = []

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "successfulInstanceCreditSpecificationSet": [],
                "unsuccessfulInstanceCreditSpecificationSet": [],
            }

        for spec in instance_credit_specifications:
            instance_id = spec.get("InstanceId")
            cpu_credits = spec.get("CpuCredits")

            if not instance_id:
                unsuccessful.append({
                    "instanceId": None,
                    "error": {
                        "code": "InvalidInstanceID.Malformed",
                        "message": "InstanceId is required",
                    },
                })
                continue

            instance = self.state.instances.get(instance_id)
            if not instance:
                unsuccessful.append({
                    "instanceId": instance_id,
                    "error": {
                        "code": "InvalidInstanceID.NotFound",
                        "message": f"Instance {instance_id} not found",
                    },
                })
                continue

            # Validate cpu_credits if provided
            if cpu_credits is not None:
                if cpu_credits not in {"standard", "unlimited"}:
                    unsuccessful.append({
                        "instanceId": instance_id,
                        "error": {
                            "code": "InstanceCreditSpecification.NotSupported",
                            "message": f"Invalid CpuCredits value: {cpu_credits}",
                        },
                    })
                    continue

            # Update instance credit specification
            instance.cpu_credits = cpu_credits if cpu_credits is not None else "standard"

            successful.append({"instanceId": instance_id})

        return {
            "requestId": self.generate_request_id(),
            "successfulInstanceCreditSpecificationSet": successful,
            "unsuccessfulInstanceCreditSpecificationSet": unsuccessful,
        }


    def modify_instance_event_start_time(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        instance_event_id = params.get("InstanceEventId")
        not_before = params.get("NotBefore")
        dry_run = params.get("DryRun", False)

        if not instance_id:
            raise ValueError("InstanceId is required")
        if not instance_event_id:
            raise ValueError("InstanceEventId is required")
        if not not_before:
            raise ValueError("NotBefore is required")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "event": {},
            }

        # Find the event in instance status events
        if not hasattr(instance, "status") or not instance.status:
            raise ValueError(f"No status information for instance {instance_id}")

        event_to_modify = None
        for event in getattr(instance.status, "events_set", []):
            if event.instance_event_id == instance_event_id:
                event_to_modify = event
                break

        if not event_to_modify:
            raise ValueError(f"Event {instance_event_id} not found for instance {instance_id}")

        # Update the not_before time
        event_to_modify.not_before = not_before

        return {
            "requestId": self.generate_request_id(),
            "event": event_to_modify.to_dict(),
        }

    def modify_instance_maintenance_options(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        if not instance_id:
            raise Exception("Missing required parameter InstanceId")
        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        auto_recovery = params.get("AutoRecovery")
        reboot_migration = params.get("RebootMigration")

        # Validate AutoRecovery if provided
        if auto_recovery is not None:
            if auto_recovery not in ("disabled", "default"):
                raise Exception("InvalidParameterValue: AutoRecovery must be 'disabled' or 'default'")

        # Validate RebootMigration if provided
        if reboot_migration is not None:
            if reboot_migration not in ("disabled", "default"):
                raise Exception("InvalidParameterValue: RebootMigration must be 'disabled' or 'default'")

        # Store or update maintenance options on instance metadata
        # We assume instance has a dict attribute 'maintenance_options' to store these settings
        if not hasattr(instance, "maintenance_options") or instance.maintenance_options is None:
            instance.maintenance_options = {}

        if auto_recovery is not None:
            instance.maintenance_options["AutoRecovery"] = auto_recovery
        else:
            # If not provided, keep existing or default to None
            instance.maintenance_options.setdefault("AutoRecovery", None)

        if reboot_migration is not None:
            instance.maintenance_options["RebootMigration"] = reboot_migration
        else:
            instance.maintenance_options.setdefault("RebootMigration", None)

        response = {
            "autoRecovery": instance.maintenance_options.get("AutoRecovery"),
            "instanceId": instance_id,
            "rebootMigration": instance.maintenance_options.get("RebootMigration"),
            "requestId": self.generate_request_id(),
        }
        return response


    def modify_instance_metadata_defaults(self, params: dict) -> dict:
        # This modifies account-level default instance metadata service (IMDS) settings in the region.
        # We assume self.state.account_metadata_defaults is a dict keyed by region or global.
        # For simplicity, assume global defaults stored in self.state.account_metadata_defaults dict.

        # Validate DryRun if present (not implemented here, just placeholder)
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise Exception("InvalidParameterValue: DryRun must be a boolean")

        # Allowed values for these parameters
        valid_http_endpoint = {"disabled", "enabled", "no-preference"}
        valid_http_tokens = {"optional", "required", "no-preference"}
        valid_instance_metadata_tags = {"disabled", "enabled", "no-preference"}

        http_endpoint = params.get("HttpEndpoint")
        if http_endpoint is not None and http_endpoint not in valid_http_endpoint:
            raise Exception("InvalidParameterValue: HttpEndpoint must be one of disabled, enabled, no-preference")

        http_put_response_hop_limit = params.get("HttpPutResponseHopLimit")
        if http_put_response_hop_limit is not None:
            if not isinstance(http_put_response_hop_limit, int):
                raise Exception("InvalidParameterValue: HttpPutResponseHopLimit must be an integer")
            if http_put_response_hop_limit != -1 and not (1 <= http_put_response_hop_limit <= 64):
                raise Exception("InvalidParameterValue: HttpPutResponseHopLimit must be between 1 and 64 or -1")

        http_tokens = params.get("HttpTokens")
        if http_tokens is not None and http_tokens not in valid_http_tokens:
            raise Exception("InvalidParameterValue: HttpTokens must be one of optional, required, no-preference")

        instance_metadata_tags = params.get("InstanceMetadataTags")
        if instance_metadata_tags is not None and instance_metadata_tags not in valid_instance_metadata_tags:
            raise Exception("InvalidParameterValue: InstanceMetadataTags must be one of disabled, enabled, no-preference")

        # Initialize account metadata defaults dict if not present
        if not hasattr(self.state, "account_metadata_defaults") or self.state.account_metadata_defaults is None:
            self.state.account_metadata_defaults = {}

        # Update the account-level defaults with provided values
        if http_endpoint is not None:
            self.state.account_metadata_defaults["HttpEndpoint"] = http_endpoint
        if http_put_response_hop_limit is not None:
            self.state.account_metadata_defaults["HttpPutResponseHopLimit"] = http_put_response_hop_limit
        if http_tokens is not None:
            self.state.account_metadata_defaults["HttpTokens"] = http_tokens
        if instance_metadata_tags is not None:
            self.state.account_metadata_defaults["InstanceMetadataTags"] = instance_metadata_tags

        response = {
            "requestId": self.generate_request_id(),
            "return": True,
        }
        return response


    def modify_instance_metadata_options(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        if not instance_id:
            raise Exception("Missing required parameter InstanceId")
        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        # Validate parameters
        valid_http_endpoint = {"disabled", "enabled"}
        valid_http_protocol_ipv6 = {"disabled", "enabled"}
        valid_http_tokens = {"optional", "required"}
        valid_instance_metadata_tags = {"disabled", "enabled"}

        http_endpoint = params.get("HttpEndpoint")
        if http_endpoint is not None and http_endpoint not in valid_http_endpoint:
            raise Exception("InvalidParameterValue: HttpEndpoint must be 'disabled' or 'enabled'")

        http_protocol_ipv6 = params.get("HttpProtocolIpv6")
        if http_protocol_ipv6 is not None and http_protocol_ipv6 not in valid_http_protocol_ipv6:
            raise Exception("InvalidParameterValue: HttpProtocolIpv6 must be 'disabled' or 'enabled'")

        http_put_response_hop_limit = params.get("HttpPutResponseHopLimit")
        if http_put_response_hop_limit is not None:
            if not isinstance(http_put_response_hop_limit, int):
                raise Exception("InvalidParameterValue: HttpPutResponseHopLimit must be an integer")
            if not (1 <= http_put_response_hop_limit <= 64):
                raise Exception("InvalidParameterValue: HttpPutResponseHopLimit must be between 1 and 64")

        http_tokens = params.get("HttpTokens")
        if http_tokens is not None and http_tokens not in valid_http_tokens:
            raise Exception("InvalidParameterValue: HttpTokens must be 'optional' or 'required'")

        instance_metadata_tags = params.get("InstanceMetadataTags")
        if instance_metadata_tags is not None and instance_metadata_tags not in valid_instance_metadata_tags:
            raise Exception("InvalidParameterValue: InstanceMetadataTags must be 'disabled' or 'enabled'")

        # We assume instance has attribute 'metadata_options' dict to store these settings
        if not hasattr(instance, "metadata_options") or instance.metadata_options is None:
            instance.metadata_options = {}

        # Update instance metadata options with provided values
        if http_endpoint is not None:
            instance.metadata_options["HttpEndpoint"] = http_endpoint
        if http_protocol_ipv6 is not None:
            instance.metadata_options["HttpProtocolIpv6"] = http_protocol_ipv6
        if http_put_response_hop_limit is not None:
            instance.metadata_options["HttpPutResponseHopLimit"] = http_put_response_hop_limit
        if http_tokens is not None:
            instance.metadata_options["HttpTokens"] = http_tokens
        if instance_metadata_tags is not None:
            instance.metadata_options["InstanceMetadataTags"] = instance_metadata_tags

        # The state of the metadata option changes to "pending" after modification
        instance.metadata_options["State"] = "pending"

        response = {
            "instanceId": instance_id,
            "instanceMetadataOptions": {
                "httpEndpoint": instance.metadata_options.get("HttpEndpoint"),
                "httpProtocolIpv6": instance.metadata_options.get("HttpProtocolIpv6"),
                "httpPutResponseHopLimit": instance.metadata_options.get("HttpPutResponseHopLimit"),
                "httpTokens": instance.metadata_options.get("HttpTokens"),
                "instanceMetadataTags": instance.metadata_options.get("InstanceMetadataTags"),
                "state": instance.metadata_options.get("State"),
            },
            "requestId": self.generate_request_id(),
        }
        return response


    def modify_instance_network_performance_options(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        bandwidth_weighting = params.get("BandwidthWeighting")
        if not instance_id:
            raise Exception("Missing required parameter InstanceId")
        if not bandwidth_weighting:
            raise Exception("Missing required parameter BandwidthWeighting")

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        valid_bandwidth_weighting = {"default", "vpc-1", "ebs-1"}
        if bandwidth_weighting not in valid_bandwidth_weighting:
            raise Exception("InvalidParameterValue: BandwidthWeighting must be one of default, vpc-1, ebs-1")

        # Assume instance has attribute 'network_performance_options' dict to store this setting
        if not hasattr(instance, "network_performance_options") or instance.network_performance_options is None:
            instance.network_performance_options = {}

        instance.network_performance_options["BandwidthWeighting"] = bandwidth_weighting

        response = {
            "bandwidthWeighting": bandwidth_weighting,
            "instanceId": instance_id,
            "requestId": self.generate_request_id(),
        }
        return response


    def modify_private_dns_name_options(self, params: dict) -> dict:
        instance_id = params.get("InstanceId")
        if not instance_id:
            raise Exception("Missing required parameter InstanceId")
        instance = self.state.instances.get(instance_id)
        if not instance:
            raise Exception(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        enable_resource_name_dns_aaaa_record = params.get("EnableResourceNameDnsAAAARecord")
        enable_resource_name_dns_a_record = params.get("EnableResourceNameDnsARecord")
        private_dns_hostname_type = params.get("PrivateDnsHostnameType")

        # Validate booleans if provided
        if enable_resource_name_dns_aaaa_record is not None and not isinstance(enable_resource_name_dns_aaaa_record, bool):
            raise Exception("InvalidParameterValue: EnableResourceNameDnsAAAARecord must be a boolean")
        if enable_resource_name_dns_a_record is not None and not isinstance(enable_resource_name_dns_a_record, bool):
            raise Exception("InvalidParameterValue: EnableResourceNameDnsARecord must be a boolean")

        # Validate PrivateDnsHostnameType if provided
        valid_hostname_types = {"ip-name", "resource-name"}
        if private_dns_hostname_type is not None and private_dns_hostname_type not in valid_hostname_types:
            raise Exception("InvalidParameterValue: PrivateDnsHostnameType must be 'ip-name' or 'resource-name'")

        # Assume instance has attribute 'private_dns_name_options' dict to store these settings
        if not hasattr(instance, "private_dns_name_options") or instance.private_dns_name_options is None:
            instance.private_dns_name_options = {}

        if enable_resource_name_dns_aaaa_record is not None:
            instance.private_dns_name_options["EnableResourceNameDnsAAAARecord"] = enable_resource_name_dns_aaaa_record
        if enable_resource_name_dns_a_record is not None:
            instance.private_dns_name_options["EnableResourceNameDnsARecord"] = enable_resource_name_dns_a_record
        if private_dns_hostname_type is not None:
            instance.private_dns_name_options["PrivateDnsHostnameType"] = private_dns_hostname_type

        response = {
            "requestId": self.generate_request_id(),
            "return": True,
        }
        return response

    def modify_public_ip_dns_name_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        hostname_type = params.get("HostnameType")
        network_interface_id = params.get("NetworkInterfaceId")
        dry_run = params.get("DryRun", False)

        if hostname_type is None:
            raise ValueError("HostnameType is required")
        if network_interface_id is None:
            raise ValueError("NetworkInterfaceId is required")

        # Validate HostnameType values
        valid_hostname_types = {
            "public-dual-stack-dns-name",
            "public-ipv4-dns-name",
            "public-ipv6-dns-name",
        }
        if hostname_type not in valid_hostname_types:
            raise ValueError(f"Invalid HostnameType: {hostname_type}")

        # DryRun check (simulate permission check)
        if dry_run:
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "DryRun operation successful."
            }

        # Access the network interface resource
        network_interface = self.state.network_interfaces.get(network_interface_id)
        if network_interface is None:
            raise ValueError(f"NetworkInterface {network_interface_id} does not exist")

        # Modify the public IP DNS name options on the network interface
        # We assume network_interface has an attribute public_ip_dns_name_options (dict or object)
        # For this emulator, we store the hostname type as a string attribute
        network_interface.public_ip_dns_name_options = {
            "HostnameType": hostname_type
        }

        return {
            "requestId": self.generate_request_id(),
            "successful": True,
        }


    def monitor_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        instance_ids = params.get("InstanceId.N")
        if instance_ids is None:
            raise ValueError("InstanceId.N is required")
        if not isinstance(instance_ids, list):
            raise ValueError("InstanceId.N must be a list of instance IDs")

        # DryRun check
        if dry_run:
            # Assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "DryRun operation successful."
            }

        instances_set = []
        for instance_id in instance_ids:
            instance = self.state.instances.get(instance_id)
            if instance is None:
                # According to AWS behavior, invalid instance IDs are ignored
                continue

            # Enable detailed monitoring for the instance
            # Assume instance has a 'monitoring' attribute with 'state'
            if not hasattr(instance, "monitoring") or instance.monitoring is None:
                # Create monitoring attribute if missing
                instance.monitoring = CpuCreditsOption()  # Using CpuCreditsOption as placeholder for monitoring object
            # Set monitoring state to 'pending' to simulate enabling detailed monitoring
            instance.monitoring.state = MonitoringState.PENDING if hasattr(MonitoringState, "PENDING") else "pending"

            instances_set.append({
                "instanceId": instance_id,
                "monitoring": {
                    "state": instance.monitoring.state if hasattr(instance.monitoring, "state") else instance.monitoring
                }
            })

        return {
            "requestId": self.generate_request_id(),
            "instancesSet": instances_set,
        }


    def reboot_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        instance_ids = params.get("InstanceId.N")
        if instance_ids is None:
            raise ValueError("InstanceId.N is required")
        if not isinstance(instance_ids, list):
            raise ValueError("InstanceId.N must be a list of instance IDs")

        # DryRun check
        if dry_run:
            # Assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "DryRun operation successful."
            }

        for instance_id in instance_ids:
            instance = self.state.instances.get(instance_id)
            if instance is None:
                # Ignore invalid instance IDs
                continue
            # Only reboot if instance is not terminated
            if hasattr(instance, "state") and instance.state is not None:
                # Assuming instance.state.name is an InstanceStateName enum member
                if instance.state.name == InstanceStateName.TERMINATED:
                    continue
            # Simulate reboot by setting instance state to pending or rebooting
            # For emulator, we can set state to pending or keep as is
            if hasattr(instance, "state") and instance.state is not None:
                instance.state.name = InstanceStateName.PENDING if hasattr(InstanceStateName, "PENDING") else "pending"

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def replace_iam_instance_profile_association(self, params: Dict[str, Any]) -> Dict[str, Any]:
        association_id = params.get("AssociationId")
        iam_instance_profile_spec = params.get("IamInstanceProfile")
        if association_id is None:
            raise ValueError("AssociationId is required")
        if iam_instance_profile_spec is None:
            raise ValueError("IamInstanceProfile is required")

        # Validate iam_instance_profile_spec keys
        arn = iam_instance_profile_spec.get("Arn")
        name = iam_instance_profile_spec.get("Name")

        # Find existing association
        association = self.state.iam_instance_profile_associations.get(association_id)
        if association is None:
            raise ValueError(f"IAM instance profile association {association_id} does not exist")

        # Replace the IAM instance profile in the association
        # Create new IamInstanceProfile object
        new_profile = IamInstanceProfile(arn=arn, id=None)
        # If name is provided, try to find the profile id by name in state (not specified, so keep id None)
        # Update association
        association.iam_instance_profile = new_profile
        association.state = IamInstanceProfileAssociationState.ASSOCIATING if hasattr(IamInstanceProfileAssociationState, "ASSOCIATING") else "associating"
        association.timestamp = datetime.utcnow()

        return {
            "requestId": self.generate_request_id(),
            "iamInstanceProfileAssociation": association.to_dict(),
        }


    def report_instance_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        description = params.get("Description")
        dry_run = params.get("DryRun", False)
        end_time = params.get("EndTime")
        instance_ids = params.get("InstanceId.N")
        reason_codes = params.get("ReasonCode.N")
        start_time = params.get("StartTime")
        status = params.get("Status")

        if instance_ids is None:
            raise ValueError("InstanceId.N is required")
        if not isinstance(instance_ids, list):
            raise ValueError("InstanceId.N must be a list of instance IDs")
        if reason_codes is None:
            raise ValueError("ReasonCode.N is required")
        if not isinstance(reason_codes, list):
            raise ValueError("ReasonCode.N must be a list of strings")
        if status is None:
            raise ValueError("Status is required")

        valid_status_values = {"ok", "impaired"}
        if status not in valid_status_values:
            raise ValueError(f"Invalid Status value: {status}")

        # DryRun check
        if dry_run:
            # Assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "DryRun operation successful."
            }

        # For each instance, validate it exists and is running
        for instance_id in instance_ids:
            instance = self.state.instances.get(instance_id)
            if instance is None:
                raise ValueError(f"Instance {instance_id} does not exist")
            # Check instance state is running
            if hasattr(instance, "state") and instance.state is not None:
                if instance.state.name != InstanceStateName.RUNNING:
                    raise ValueError(f"Instance {instance_id} is not in running state")

        # For emulator, just accept the report and do not change state
        # Could store reports if needed, but not required

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def reset_instance_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        attribute = params.get("Attribute")
        dry_run = params.get("DryRun", False)

        # Validate required parameters
        if not instance_id:
            raise ValueError("InstanceId is required")
        if not attribute:
            raise ValueError("Attribute is required")
        if attribute not in ("kernel", "ramdisk", "sourceDestCheck"):
            raise ValueError("Attribute must be one of: kernel, ramdisk, sourceDestCheck")

        # DryRun check (not implemented here, but placeholder)
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} does not exist")

        # For kernel or ramdisk, instance must be stopped
        if attribute in ("kernel", "ramdisk"):
            if instance.state.name != InstanceStateName.stopped:
                raise ValueError(f"Instance {instance_id} must be stopped to reset {attribute}")

        # Reset attribute to default
        if attribute == "sourceDestCheck":
            # Default is True
            instance.source_dest_check = True
        elif attribute == "kernel":
            # Reset kernel to default (None or empty)
            instance.kernel_id = None
        elif attribute == "ramdisk":
            # Reset ramdisk to default (None or empty)
            instance.ramdisk_id = None

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def run_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import base64
        from datetime import datetime

        # Validate required parameters (default to 1 if not provided, matching LocalStack/AWS behavior)
        min_count = int(params.get("MinCount", 1))
        max_count = int(params.get("MaxCount", 1))
        
        if min_count < 1 or max_count < 1 or max_count < min_count:
            raise ValueError("Invalid MinCount or MaxCount values")

        # Determine number of instances to launch
        count = max_count

        # UserData handling
        user_data = params.get("UserData")
        if user_data:
            # Ensure it is base64 encoded string
            try:
                base64.b64decode(user_data)
            except Exception:
                raise ValueError("UserData must be base64 encoded")

        # Validate ImageId or LaunchTemplate presence
        image_id = params.get("ImageId")
        launch_template = params.get("LaunchTemplate")
        if not image_id and not launch_template:
            # For now, we require ImageId as LaunchTemplate logic is complex
            raise ValueError("ImageId is required (LaunchTemplate not fully supported)")

        # Subnet/VPC handling
        subnet_id = params.get("SubnetId")
        vpc_id = None
        if subnet_id:
            subnet = self.state.subnets.get(subnet_id)
            if not subnet:
                raise ValueError(f"Subnet {subnet_id} does not exist")
            vpc_id = subnet.vpc_id

        # Security Groups handling
        security_group_ids = []
        # Collect SecurityGroupId.N parameters
        for key, value in params.items():
            if key.startswith("SecurityGroupId."):
                security_group_ids.append(value)
        # Also check SecurityGroup.N for group names (EC2-Classic style, but also works for VPC)
        security_group_names = []
        for key, value in params.items():
            if key.startswith("SecurityGroup.") and not key.startswith("SecurityGroupId."):
                security_group_names.append(value)

        # Resolve security groups
        resolved_security_groups = []
        if security_group_ids:
            for sg_id in security_group_ids:
                sg = self.state.security_groups.get(sg_id)
                if not sg:
                    raise ValueError(f"InvalidGroup.NotFound: The security group '{sg_id}' does not exist")
                # Validate security group is in same VPC as subnet
                sg_vpc_id = getattr(sg, "vpcId", None)
                if vpc_id and sg_vpc_id and sg_vpc_id != vpc_id:
                    raise ValueError(f"InvalidGroupId.Malformed: Security group '{sg_id}' belongs to a different VPC")
                resolved_security_groups.append({"groupId": sg_id, "groupName": getattr(sg, "groupName", None)})
        elif security_group_names and vpc_id:
            # Resolve by name within VPC
            for sg_name in security_group_names:
                found = False
                for sg in self.state.security_groups.values():
                    if getattr(sg, "groupName", None) == sg_name and getattr(sg, "vpcId", None) == vpc_id:
                        resolved_security_groups.append({"groupId": getattr(sg, "groupId", None), "groupName": sg_name})
                        found = True
                        break
                if not found:
                    raise ValueError(f"InvalidGroup.NotFound: The security group '{sg_name}' does not exist in VPC '{vpc_id}'")

        # If no security groups specified and in a VPC, use default security group
        if not resolved_security_groups and vpc_id and hasattr(self.state, "security_groups"):
            for sg in self.state.security_groups.values():
                if getattr(sg, "vpcId", None) == vpc_id and getattr(sg, "groupName", None) == "default":
                    resolved_security_groups.append({"groupId": getattr(sg, "groupId", None), "groupName": "default"})
                    break

        # Tags
        tag_specifications = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") == "instance":
                for t in tag_spec.get("Tags", []):
                    tags.append(Tag(Key=t.get("Key"), Value=t.get("Value")))

        # Prepare list of instances to return
        instances = []
        owner_id = self.get_owner_id()

        # Generate reservation ID upfront so instances can reference it
        reservation_id = self.generate_unique_id(prefix="r-")
        
        # Placement
        placement = params.get("Placement", {})
        availability_zone = placement.get("AvailabilityZone")
        if subnet_id:
            subnet = self.state.subnets.get(subnet_id)
            if subnet:
                subnet_az = subnet.availability_zone
                # If both placement AZ and subnet AZ are specified, they must match
                if availability_zone and subnet_az and availability_zone != subnet_az:
                    raise ValueError(f"InvalidPlacementGroup: The specified AvailabilityZone '{availability_zone}' does not match the subnet's AvailabilityZone '{subnet_az}'")
                # Inherit from subnet if placement AZ not specified
                if not availability_zone:
                    availability_zone = subnet_az

        for _ in range(count):
            instance_id = self.generate_unique_id(prefix="i-")
            
            # Create instance object
            instance = Instance(
                instance_id=instance_id,
                image_id=image_id,
                instance_type=params.get("InstanceType", "m1.small"),
                key_name=params.get("KeyName"),
                launch_time=datetime.utcnow(),
                state=InstanceState(code=0, name=InstanceStateName.PENDING),
                subnet_id=subnet_id,
                vpc_id=vpc_id,
                tags=tags,
                placement={"AvailabilityZone": availability_zone} if availability_zone else None,
                # Allocate Private IP from subnet CIDR if subnet specified
                private_ip_address=self._allocate_private_ip(subnet_id) if subnet_id else None,
                security_groups=resolved_security_groups,  # Use resolved SGs or default
                client_token=params.get("ClientToken"),
                reservation_id=reservation_id,  # Link instance to reservation
                owner_id=owner_id,
            )

            # Store instance in state
            self.state.instances[instance_id] = instance
            self.state.resources[instance_id] = instance

            # LocalStack compatibility: Transition from pending to running immediately
            # CloudFormation polls for 'running' state before considering creation complete
            instance.state = InstanceState(code=16, name=InstanceStateName.RUNNING)

            instances.append(instance)

        # Create reservation object (reservation_id already generated above)
        reservation = Reservation(
            reservation_id=reservation_id,
            owner_id=owner_id,
            requester_id=None,
            group_set=[],
            instances_set=instances,
        )
        self.state.resources[reservation_id] = reservation

        # Return response dict
        return {
            "groupSet": [],
            "instancesSet": [instance.to_dict() for instance in instances],
            "ownerId": owner_id,
            "requesterId": None,
            "requestId": self.generate_request_id(),
            "reservationId": reservation_id,
        }


    def send_diagnostic_interrupt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        dry_run = params.get("DryRun", False)

        if not instance_id:
            raise ValueError("InstanceId is required")

        # DryRun check placeholder
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        instance = self.state.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} does not exist")

        # Simulate sending diagnostic interrupt (no real effect in emulator)
        # Could log or mark instance as having received interrupt if desired

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def start_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_ids = params.get("InstanceId.N")
        dry_run = params.get("DryRun", False)

        if not instance_ids or not isinstance(instance_ids, list):
            raise ValueError("InstanceId.N is required and must be a list")

        # DryRun check placeholder
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        instances_set = []
        for instance_id in instance_ids:
            instance = self.state.instances.get(instance_id)
            if not instance:
                raise ValueError(f"Instance {instance_id} does not exist")

            previous_state = instance.state
            # Only stopped instances can be started
            if previous_state.name != InstanceStateName.stopped:
                raise ValueError(f"Instance {instance_id} is not in stopped state")

            # Change state to pending (starting)
            instance.state = InstanceState(code=0, name=InstanceStateName.pending)

            instances_set.append({
                "instanceId": instance_id,
                "currentState": instance.state.to_dict(),
                "previousState": previous_state.to_dict(),
            })

        return {
            "instancesSet": instances_set,
            "requestId": self.generate_request_id(),
        }


    def stop_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_ids = params.get("InstanceId.N")
        dry_run = params.get("DryRun", False)
        force = params.get("Force", False)
        hibernate = params.get("Hibernate", False)
        skip_os_shutdown = params.get("SkipOsShutdown", False)

        if not instance_ids or not isinstance(instance_ids, list):
            raise ValueError("InstanceId.N is required and must be a list")

        # DryRun check placeholder
        if dry_run:
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        instances_set = []
        for instance_id in instance_ids:
            instance = self.state.instances.get(instance_id)
            if not instance:
                raise ValueError(f"Instance {instance_id} does not exist")

            previous_state = instance.state
            # Only running instances can be stopped (check both enum forms for safety)
            if previous_state.name not in (InstanceStateName.RUNNING, InstanceStateName.running, "running"):
                raise ValueError(f"Instance {instance_id} is not in running state")

            # Change state to stopping then stopped (LocalStack compatibility)
            instance.state = InstanceState(code=64, name=InstanceStateName.STOPPING)
            # Immediately transition to stopped for emulator
            instance.state = InstanceState(code=80, name=InstanceStateName.STOPPED)

            # In real implementation, handle hibernate, force, skip_os_shutdown options

            instances_set.append({
                "instanceId": instance_id,
                "currentState": instance.state.to_dict(),
                "previousState": previous_state.to_dict(),
            })

        return {
            "instancesSet": instances_set,
            "requestId": self.generate_request_id(),
        }

    def terminate_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_ids = []
        # Collect instance IDs from params keys like "InstanceId.1", "InstanceId.2", ...
        for key, value in params.items():
            if key.startswith("InstanceId."):
                instance_ids.append(value)
        if not instance_ids:
            raise ValueError("At least one InstanceId.N parameter is required")

        dry_run = params.get("DryRun", False)
        force = params.get("Force", False)
        skip_os_shutdown = params.get("SkipOsShutdown", False)

        # Validate instance IDs exist and check for termination protection
        for instance_id in instance_ids:
            if instance_id not in self.state.instances:
                # According to AWS behavior, if instance does not exist, ignore or error?
                # AWS returns error for invalid instance id, but here we raise error for simplicity
                raise ValueError(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

            # Check if instance has termination protection enabled (unless Force=True)
            instance = self.state.instances[instance_id]
            disable_api_termination = getattr(instance, "disable_api_termination", False)
            if disable_api_termination and not force:
                raise Exception(f"OperationNotPermitted: The instance '{instance_id}' may not be terminated. Modify its 'disableApiTermination' instance attribute and try again.")

        # DryRun check: if DryRun is True, check permissions and return error accordingly
        if dry_run:
            # For simplicity, assume user has permission; return DryRunOperation error response
            # In real implementation, would raise an exception or return error dict
            # Here, raise Exception to simulate error response
            raise Exception("DryRunOperation")

        instances_set = []
        for instance_id in instance_ids:
            instance = self.state.instances[instance_id]

            # Determine previous state
            previous_state = instance.state

            # If instance already terminated, AWS returns success with current and previous state both terminated
            if previous_state.name == InstanceStateName.TERMINATED:
                current_state = previous_state
            else:
                # Transition instance state to shutting-down first
                current_state = InstanceState(
                    code=32,
                    name=InstanceStateName.SHUTTING_DOWN,
                )
                # Update instance state in state dict
                instance.state = current_state

                # Simulate immediate termination for emulator: transition to terminated
                terminated_state = InstanceState(
                    code=48,
                    name=InstanceStateName.TERMINATED,
                )
                instance.state = terminated_state
                current_state = terminated_state

                # Remove instance from state.instances to simulate deletion? 
                # AWS still returns instance info after termination, so keep it but mark terminated
                # Also, delete attached EBS volumes marked DeleteOnTermination
                # For simplicity, assume instance has attribute 'block_device_mappings' with EBS volumes
                if hasattr(instance, "block_device_mappings"):
                    for bdm in instance.block_device_mappings:
                        if getattr(bdm, "delete_on_termination", False):
                            # Remove volume from state.volumes if exists
                            volume_id = getattr(bdm, "ebs_volume_id", None)
                            if volume_id and volume_id in self.state.volumes:
                                del self.state.volumes[volume_id]

            instances_set.append({
                "instanceId": instance_id,
                "currentState": {
                    "code": current_state.code,
                    "name": current_state.name.value if hasattr(current_state.name, "value") else current_state.name,
                },
                "previousState": {
                    "code": previous_state.code,
                    "name": previous_state.name.value if hasattr(previous_state.name, "value") else previous_state.name,
                },
            })

        return {
            "instancesSet": instances_set,
            "requestId": self.generate_request_id(),
        }


    def unmonitor_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_ids = []
        for key, value in params.items():
            if key.startswith("InstanceId."):
                instance_ids.append(value)
        if not instance_ids:
            raise ValueError("At least one InstanceId.N parameter is required")

        dry_run = params.get("DryRun", False)

        # Validate instance IDs exist
        for instance_id in instance_ids:
            if instance_id not in self.state.instances:
                raise ValueError(f"InvalidInstanceID.NotFound: The instance ID '{instance_id}' does not exist")

        if dry_run:
            raise Exception("DryRunOperation")

        instances_set = []
        for instance_id in instance_ids:
            instance = self.state.instances[instance_id]

            # Update monitoring state to disabled
            # Assume instance has attribute 'monitoring' with 'state' string
            if hasattr(instance, "monitoring"):
                instance.monitoring.state = "disabled"
            else:
                # If no monitoring attribute, create one
                instance.monitoring = type("Monitoring", (), {})()
                instance.monitoring.state = "disabled"

            instances_set.append({
                "instanceId": instance_id,
                "monitoring": {
                    "state": "disabled"
                }
            })

        return {
            "instancesSet": instances_set,
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class InstancesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateIamInstanceProfile", self.associate_iam_instance_profile)
        self.register_action("CreateDelegateMacVolumeOwnershipTask", self.create_delegate_mac_volume_ownership_task)
        self.register_action("CreateMacSystemIntegrityProtectionModificationTask", self.create_mac_system_integrity_protection_modification_task)
        self.register_action("DescribeIamInstanceProfileAssociations", self.describe_iam_instance_profile_associations)
        self.register_action("DescribeInstanceAttribute", self.describe_instance_attribute)
        self.register_action("DescribeInstanceCreditSpecifications", self.describe_instance_credit_specifications)
        self.register_action("DescribeInstances", self.describe_instances)
        self.register_action("DescribeInstanceStatus", self.describe_instance_status)
        self.register_action("DisassociateIamInstanceProfile", self.disassociate_iam_instance_profile)
        self.register_action("GetConsoleOutput", self.get_console_output)
        self.register_action("GetConsoleScreenshot", self.get_console_screenshot)
        self.register_action("GetDefaultCreditSpecification", self.get_default_credit_specification)
        self.register_action("GetInstanceMetadataDefaults", self.get_instance_metadata_defaults)
        self.register_action("GetInstanceUefiData", self.get_instance_uefi_data)
        self.register_action("GetPasswordData", self.get_password_data)
        self.register_action("ModifyDefaultCreditSpecification", self.modify_default_credit_specification)
        self.register_action("ModifyInstanceAttribute", self.modify_instance_attribute)
        self.register_action("ModifyInstanceCpuOptions", self.modify_instance_cpu_options)
        self.register_action("ModifyInstanceCreditSpecification", self.modify_instance_credit_specification)
        self.register_action("ModifyInstanceEventStartTime", self.modify_instance_event_start_time)
        self.register_action("ModifyInstanceMaintenanceOptions", self.modify_instance_maintenance_options)
        self.register_action("ModifyInstanceMetadataDefaults", self.modify_instance_metadata_defaults)
        self.register_action("ModifyInstanceMetadataOptions", self.modify_instance_metadata_options)
        self.register_action("ModifyInstanceNetworkPerformanceOptions", self.modify_instance_network_performance_options)
        self.register_action("ModifyPrivateDnsNameOptions", self.modify_private_dns_name_options)
        self.register_action("ModifyPublicIpDnsNameOptions", self.modify_public_ip_dns_name_options)
        self.register_action("MonitorInstances", self.monitor_instances)
        self.register_action("RebootInstances", self.reboot_instances)
        self.register_action("ReplaceIamInstanceProfileAssociation", self.replace_iam_instance_profile_association)
        self.register_action("ReportInstanceStatus", self.report_instance_status)
        self.register_action("ResetInstanceAttribute", self.reset_instance_attribute)
        self.register_action("RunInstances", self.run_instances)
        self.register_action("SendDiagnosticInterrupt", self.send_diagnostic_interrupt)
        self.register_action("StartInstances", self.start_instances)
        self.register_action("StopInstances", self.stop_instances)
        self.register_action("TerminateInstances", self.terminate_instances)
        self.register_action("UnmonitorInstances", self.unmonitor_instances)

    def associate_iam_instance_profile(self, params):
        return self.backend.associate_iam_instance_profile(params)

    def create_delegate_mac_volume_ownership_task(self, params):
        return self.backend.create_delegate_mac_volume_ownership_task(params)

    def create_mac_system_integrity_protection_modification_task(self, params):
        return self.backend.create_mac_system_integrity_protection_modification_task(params)

    def describe_iam_instance_profile_associations(self, params):
        return self.backend.describe_iam_instance_profile_associations(params)

    def describe_instance_attribute(self, params):
        return self.backend.describe_instance_attribute(params)

    def describe_instance_credit_specifications(self, params):
        return self.backend.describe_instance_credit_specifications(params)

    def describe_instances(self, params):
        return self.backend.describe_instances(params)

    def describe_instance_status(self, params):
        return self.backend.describe_instance_status(params)

    def disassociate_iam_instance_profile(self, params):
        return self.backend.disassociate_iam_instance_profile(params)

    def get_console_output(self, params):
        return self.backend.get_console_output(params)

    def get_console_screenshot(self, params):
        return self.backend.get_console_screenshot(params)

    def get_default_credit_specification(self, params):
        return self.backend.get_default_credit_specification(params)

    def get_instance_metadata_defaults(self, params):
        return self.backend.get_instance_metadata_defaults(params)

    def get_instance_uefi_data(self, params):
        return self.backend.get_instance_uefi_data(params)

    def get_password_data(self, params):
        return self.backend.get_password_data(params)

    def modify_default_credit_specification(self, params):
        return self.backend.modify_default_credit_specification(params)

    def modify_instance_attribute(self, params):
        return self.backend.modify_instance_attribute(params)

    def modify_instance_cpu_options(self, params):
        return self.backend.modify_instance_cpu_options(params)

    def modify_instance_credit_specification(self, params):
        return self.backend.modify_instance_credit_specification(params)

    def modify_instance_event_start_time(self, params):
        return self.backend.modify_instance_event_start_time(params)

    def modify_instance_maintenance_options(self, params):
        return self.backend.modify_instance_maintenance_options(params)

    def modify_instance_metadata_defaults(self, params):
        return self.backend.modify_instance_metadata_defaults(params)

    def modify_instance_metadata_options(self, params):
        return self.backend.modify_instance_metadata_options(params)

    def modify_instance_network_performance_options(self, params):
        return self.backend.modify_instance_network_performance_options(params)

    def modify_private_dns_name_options(self, params):
        return self.backend.modify_private_dns_name_options(params)

    def modify_public_ip_dns_name_options(self, params):
        return self.backend.modify_public_ip_dns_name_options(params)

    def monitor_instances(self, params):
        return self.backend.monitor_instances(params)

    def reboot_instances(self, params):
        return self.backend.reboot_instances(params)

    def replace_iam_instance_profile_association(self, params):
        return self.backend.replace_iam_instance_profile_association(params)

    def report_instance_status(self, params):
        return self.backend.report_instance_status(params)

    def reset_instance_attribute(self, params):
        return self.backend.reset_instance_attribute(params)

    def run_instances(self, params):
        return self.backend.run_instances(params)

    def send_diagnostic_interrupt(self, params):
        return self.backend.send_diagnostic_interrupt(params)

    def start_instances(self, params):
        return self.backend.start_instances(params)

    def stop_instances(self, params):
        return self.backend.stop_instances(params)

    def terminate_instances(self, params):
        return self.backend.terminate_instances(params)

    def unmonitor_instances(self, params):
        return self.backend.unmonitor_instances(params)
