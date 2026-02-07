from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: str
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
class AttributeValue:
    Value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class LaunchPermission:
    Group: Optional[str] = None
    OrganizationalUnitArn: Optional[str] = None
    OrganizationArn: Optional[str] = None
    UserId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Group": self.Group,
            "OrganizationalUnitArn": self.OrganizationalUnitArn,
            "OrganizationArn": self.OrganizationArn,
            "UserId": self.UserId,
        }


@dataclass
class LaunchPermissionModifications:
    Add: List[LaunchPermission] = field(default_factory=list)
    Remove: List[LaunchPermission] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Add": [perm.to_dict() for perm in self.Add],
            "Remove": [perm.to_dict() for perm in self.Remove],
        }


@dataclass
class ProductCode:
    productCode: Optional[str] = None
    type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"productCode": self.productCode, "type": self.type}


@dataclass
class StateReason:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message}


@dataclass
class Image:
    architecture: Optional[str] = None
    blockDeviceMapping: List[BlockDeviceMapping] = field(default_factory=list)
    bootMode: Optional[str] = None
    creationDate: Optional[str] = None
    deprecationTime: Optional[str] = None
    deregistrationProtection: Optional[str] = None
    description: Optional[str] = None
    enaSupport: Optional[bool] = None
    freeTierEligible: Optional[bool] = None
    hypervisor: Optional[str] = None
    imageAllowed: Optional[bool] = None
    imageId: Optional[str] = None
    imageLocation: Optional[str] = None
    imageOwnerAlias: Optional[str] = None
    imageOwnerId: Optional[str] = None
    imageState: Optional[str] = None
    imageType: Optional[str] = None
    imdsSupport: Optional[str] = None
    isPublic: Optional[bool] = None
    kernelId: Optional[str] = None
    lastLaunchedTime: Optional[str] = None
    name: Optional[str] = None
    platform: Optional[str] = None
    platformDetails: Optional[str] = None
    productCodes: List[ProductCode] = field(default_factory=list)
    ramdiskId: Optional[str] = None
    rootDeviceName: Optional[str] = None
    rootDeviceType: Optional[str] = None
    sourceImageId: Optional[str] = None
    sourceImageRegion: Optional[str] = None
    sourceInstanceId: Optional[str] = None
    sriovNetSupport: Optional[str] = None
    stateReason: Optional[StateReason] = None
    tagSet: List[Tag] = field(default_factory=list)
    tpmSupport: Optional[str] = None
    usageOperation: Optional[str] = None
    virtualizationType: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "architecture": self.architecture,
            "blockDeviceMapping": [bdm.to_dict() for bdm in self.blockDeviceMapping],
            "bootMode": self.bootMode,
            "creationDate": self.creationDate,
            "deprecationTime": self.deprecationTime,
            "deregistrationProtection": self.deregistrationProtection,
            "description": self.description,
            "enaSupport": self.enaSupport,
            "freeTierEligible": self.freeTierEligible,
            "hypervisor": self.hypervisor,
            "imageAllowed": self.imageAllowed,
            "imageId": self.imageId,
            "imageLocation": self.imageLocation,
            "imageOwnerAlias": self.imageOwnerAlias,
            "imageOwnerId": self.imageOwnerId,
            "imageState": self.imageState,
            "imageType": self.imageType,
            "imdsSupport": self.imdsSupport,
            "isPublic": self.isPublic,
            "kernelId": self.kernelId,
            "lastLaunchedTime": self.lastLaunchedTime,
            "name": self.name,
            "platform": self.platform,
            "platformDetails": self.platformDetails,
            "productCodes": [pc.to_dict() for pc in self.productCodes],
            "ramdiskId": self.ramdiskId,
            "rootDeviceName": self.rootDeviceName,
            "rootDeviceType": self.rootDeviceType,
            "sourceImageId": self.sourceImageId,
            "sourceImageRegion": self.sourceImageRegion,
            "sourceInstanceId": self.sourceInstanceId,
            "sriovNetSupport": self.sriovNetSupport,
            "stateReason": self.stateReason.to_dict() if self.stateReason else None,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "tpmSupport": self.tpmSupport,
            "usageOperation": self.usageOperation,
            "virtualizationType": self.virtualizationType,
            "hypervisor": self.hypervisor,
        }


@dataclass
class ImageRecycleBinInfo:
    description: Optional[str] = None
    imageId: Optional[str] = None
    name: Optional[str] = None
    recycleBinEnterTime: Optional[str] = None
    recycleBinExitTime: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "imageId": self.imageId,
            "name": self.name,
            "recycleBinEnterTime": self.recycleBinEnterTime,
            "recycleBinExitTime": self.recycleBinExitTime,
        }


@dataclass
class ImageAncestryEntry:
    creationDate: Optional[str] = None
    imageId: Optional[str] = None
    imageOwnerAlias: Optional[str] = None
    sourceImageId: Optional[str] = None
    sourceImageRegion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationDate": self.creationDate,
            "imageId": self.imageId,
            "imageOwnerAlias": self.imageOwnerAlias,
            "sourceImageId": self.sourceImageId,
            "sourceImageRegion": self.sourceImageRegion,
        }


@dataclass
class ImageUsageResourceTypeOption:
    OptionName: Optional[str] = None
    OptionValues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "OptionName": self.OptionName,
            "OptionValues": self.OptionValues,
        }


@dataclass
class ImageUsageResourceTypeRequest:
    ResourceType: Optional[str] = None
    ResourceTypeOptions: List[ImageUsageResourceTypeOption] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "ResourceTypeOptions": [opt.to_dict() for opt in self.ResourceTypeOptions],
        }


@dataclass
class ImageUsageResourceType:
    resourceType: Optional[str] = None
    resourceTypeOptionSet: List[ImageUsageResourceTypeOption] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resourceType": self.resourceType,
            "resourceTypeOptionSet": [opt.to_dict() for opt in self.resourceTypeOptionSet],
        }


@dataclass
class ImageUsageReportEntry:
    accountId: Optional[str] = None
    imageId: Optional[str] = None
    reportCreationTime: Optional[str] = None
    reportId: Optional[str] = None
    resourceType: Optional[str] = None
    usageCount: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountId": self.accountId,
            "imageId": self.imageId,
            "reportCreationTime": self.reportCreationTime,
            "reportId": self.reportId,
            "resourceType": self.resourceType,
            "usageCount": self.usageCount,
        }


@dataclass
class ImageUsageReport:
    accountIdSet: List[str] = field(default_factory=list)
    creationTime: Optional[str] = None
    expirationTime: Optional[str] = None
    imageId: Optional[str] = None
    reportId: Optional[str] = None
    resourceTypeSet: List[ImageUsageResourceType] = field(default_factory=list)
    state: Optional[str] = None
    stateReason: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountIdSet": self.accountIdSet,
            "creationTime": self.creationTime,
            "expirationTime": self.expirationTime,
            "imageId": self.imageId,
            "reportId": self.reportId,
            "resourceTypeSet": [rts.to_dict() for rts in self.resourceTypeSet],
            "state": self.state,
            "stateReason": self.stateReason,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
        }


@dataclass
class InstanceState:
    code: Optional[int] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "name": self.name}


@dataclass
class OperatorResponse:
    managed: Optional[bool] = None
    principal: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"managed": self.managed, "principal": self.principal}


@dataclass
class ImageMetadata:
    creationDate: Optional[str] = None
    deprecationTime: Optional[str] = None
    imageAllowed: Optional[bool] = None
    imageId: Optional[str] = None
    imageOwnerAlias: Optional[str] = None
    imageOwnerId: Optional[str] = None
    imageState: Optional[str] = None
    isPublic: Optional[bool] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationDate": self.creationDate,
            "deprecationTime": self.deprecationTime,
            "imageAllowed": self.imageAllowed,
            "imageId": self.imageId,
            "imageOwnerAlias": self.imageOwnerAlias,
            "imageOwnerId": self.imageOwnerId,
            "imageState": self.imageState,
            "isPublic": self.isPublic,
            "name": self.name,
        }


@dataclass
class InstanceImageMetadata:
    availabilityZone: Optional[str] = None
    imageMetadata: Optional[ImageMetadata] = None
    instanceId: Optional[str] = None
    instanceOwnerId: Optional[str] = None
    instanceState: Optional[InstanceState] = None
    instanceType: Optional[str] = None
    launchTime: Optional[str] = None
    operator: Optional[OperatorResponse] = None
    tagSet: List[Tag] = field(default_factory=list)
    zoneId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availabilityZone,
            "imageMetadata": self.imageMetadata.to_dict() if self.imageMetadata else None,
            "instanceId": self.instanceId,
            "instanceOwnerId": self.instanceOwnerId,
            "instanceState": self.instanceState.to_dict() if self.instanceState else None,
            "instanceType": self.instanceType,
            "launchTime": self.launchTime,
            "operator": self.operator.to_dict() if self.operator else None,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "zoneId": self.zoneId,
        }


@dataclass
class StoreImageTaskResult:
    amiId: Optional[str] = None
    bucket: Optional[str] = None
    progressPercentage: Optional[int] = None
    s3objectKey: Optional[str] = None
    storeTaskFailureReason: Optional[str] = None
    storeTaskState: Optional[str] = None
    taskStartTime: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amiId": self.amiId,
            "bucket": self.bucket,
            "progressPercentage": self.progressPercentage,
            "s3objectKey": self.s3objectKey,
            "storeTaskFailureReason": self.storeTaskFailureReason,
            "storeTaskState": self.storeTaskState,
            "taskStartTime": self.taskStartTime,
        }


@dataclass
class FastLaunchLaunchTemplateSpecificationResponse:
    launchTemplateId: Optional[str] = None
    launchTemplateName: Optional[str] = None
    version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "launchTemplateId": self.launchTemplateId,
            "launchTemplateName": self.launchTemplateName,
            "version": self.version,
        }


@dataclass
class FastLaunchSnapshotConfigurationResponse:
    targetResourceCount: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"targetResourceCount": self.targetResourceCount}


@dataclass
class FastLaunchLaunchTemplateSpecificationRequest:
    Version: str
    LaunchTemplateId: Optional[str] = None
    LaunchTemplateName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Version": self.Version,
            "LaunchTemplateId": self.LaunchTemplateId,
            "LaunchTemplateName": self.LaunchTemplateName,
        }


@dataclass
class FastLaunchSnapshotConfigurationRequest:
    TargetResourceCount: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"TargetResourceCount": self.TargetResourceCount}


class AMIsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for shared resources

    def cancel_image_launch_permission(self, params: Dict[str, Any]) -> Dict[str, Any]:
        image_id = params.get("ImageId")
        if not image_id:
            raise ValueError("ImageId is required")

        # DryRun check
        if params.get("DryRun"):
            # For simplicity, assume permission is always granted in this emulator
            return {"requestId": self.generate_request_id(), "return": True}

        image = self.state.amis.get(image_id)
        if not image:
            # In real AWS, this would raise an error; here we return False
            return {"requestId": self.generate_request_id(), "return": False}

        # Remove this account from launch permissions if present
        owner_id = self.get_owner_id()
        if hasattr(image, "launchPermissions") and image.launchPermissions:
            # launchPermissions is not defined in the classes, but we emulate it as a list of user IDs
            if owner_id in image.launchPermissions:
                image.launchPermissions.remove(owner_id)
        else:
            # If no launchPermissions attribute, create empty list
            image.launchPermissions = []

        return {"requestId": self.generate_request_id(), "return": True}


    def copy_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Required params
        source_image_id = params.get("SourceImageId")
        source_region = params.get("SourceRegion")
        name = params.get("Name")

        if not source_image_id:
            raise ValueError("SourceImageId is required")
        if not source_region:
            raise ValueError("SourceRegion is required")
        if not name:
            raise ValueError("Name is required")

        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id(), "imageId": None}

        # Find source image in source region
        # For emulator, assume source_region is current region or ignore region check
        source_image = self.state.amis.get(source_image_id)
        if not source_image:
            raise ValueError(f"Source image {source_image_id} not found")

        # Create new image ID
        new_image_id = self.generate_unique_id(prefix="ami-")

        # Copy tags if requested
        copy_tags = params.get("CopyImageTags", False)
        new_tag_set = []
        if copy_tags and source_image.tagSet:
            # Copy user-defined tags only (exclude aws: prefixed)
            for tag in source_image.tagSet:
                if not tag.Key.startswith("aws:"):
                    new_tag_set.append(Tag(Key=tag.Key, Value=tag.Value))

        # Override description if provided
        description = params.get("Description", source_image.description)

        # Build new Image object
        new_image = Image(
            architecture=source_image.architecture,
            blockDeviceMapping=source_image.blockDeviceMapping.copy() if source_image.blockDeviceMapping else [],
            bootMode=source_image.bootMode,
            creationDate=None,  # will be set to now or left None
            deprecationTime=None,
            deregistrationProtection=None,
            description=description,
            enaSupport=source_image.enaSupport,
            freeTierEligible=source_image.freeTierEligible,
            hypervisor=source_image.hypervisor,
            imageAllowed=source_image.imageAllowed,
            imageId=new_image_id,
            imageLocation=None,
            imageOwnerAlias=None,
            imageOwnerId=self.get_owner_id(),
            imageState="available",
            imageType=source_image.imageType,
            imdsSupport=source_image.imdsSupport,
            isPublic=False,
            kernelId=source_image.kernelId,
            lastLaunchedTime=None,
            name=name,
            platform=source_image.platform,
            platformDetails=source_image.platformDetails,
            productCodes=source_image.productCodes.copy() if source_image.productCodes else [],
            ramdiskId=source_image.ramdiskId,
            rootDeviceName=source_image.rootDeviceName,
            rootDeviceType=source_image.rootDeviceType,
            sourceImageId=source_image_id,
            sourceImageRegion=source_region,
            sourceInstanceId=None,
            sriovNetSupport=source_image.sriovNetSupport,
            stateReason=None,
            tagSet=new_tag_set,
            tpmSupport=source_image.tpmSupport,
            usageOperation=source_image.usageOperation,
            virtualizationType=source_image.virtualizationType,
        )

        # Save new image in state
        self.state.amis[new_image_id] = new_image
        self.state.resources[new_image_id] = new_image

        return {"requestId": self.generate_request_id(), "imageId": new_image_id}


    def create_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        instance_id = params.get("InstanceId")
        name = params.get("Name")
        if not instance_id:
            raise ValueError("InstanceId is required")
        if not name:
            raise ValueError("Name is required")

        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id(), "imageId": None}

        # Find instance
        instance = self.state.get_resource(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        # Compose new image ID
        new_image_id = self.generate_unique_id(prefix="ami-")

        # Description
        description = params.get("Description")

        # NoReboot flag (ignored in emulator, but accepted)
        no_reboot = params.get("NoReboot", False)

        # SnapshotLocation (only for Local Zones, ignored here)
        snapshot_location = params.get("SnapshotLocation")

        # BlockDeviceMapping.N - override or use instance block device mapping
        block_device_mappings = []
        if any(k.startswith("BlockDeviceMapping.") for k in params):
            # Parse block device mappings from params keys
            # For simplicity, assume params keys like BlockDeviceMapping.1.DeviceName, BlockDeviceMapping.1.Ebs.VolumeSize, etc.
            # We will parse all BlockDeviceMapping.N entries
            # Collect indices
            indices = set()
            for key in params:
                if key.startswith("BlockDeviceMapping."):
                    parts = key.split(".")
                    if len(parts) > 1 and parts[1].isdigit():
                        indices.add(parts[1])
            for idx in sorted(indices, key=int):
                prefix = f"BlockDeviceMapping.{idx}"
                device_name = params.get(f"{prefix}.DeviceName")
                no_device = params.get(f"{prefix}.NoDevice")
                virtual_name = params.get(f"{prefix}.VirtualName")
                ebs = None
                # Parse Ebs block device if present
                ebs_prefix = f"{prefix}.Ebs"
                if any(k.startswith(ebs_prefix) for k in params):
                    ebs = EbsBlockDevice(
                        AvailabilityZone=params.get(f"{ebs_prefix}.AvailabilityZone"),
                        AvailabilityZoneId=params.get(f"{ebs_prefix}.AvailabilityZoneId"),
                        DeleteOnTermination=params.get(f"{ebs_prefix}.DeleteOnTermination"),
                        Encrypted=params.get(f"{ebs_prefix}.Encrypted"),
                        Iops=params.get(f"{ebs_prefix}.Iops"),
                        KmsKeyId=params.get(f"{ebs_prefix}.KmsKeyId"),
                        OutpostArn=params.get(f"{ebs_prefix}.OutpostArn"),
                        SnapshotId=params.get(f"{ebs_prefix}.SnapshotId"),
                        Throughput=params.get(f"{ebs_prefix}.Throughput"),
                        VolumeInitializationRate=params.get(f"{ebs_prefix}.VolumeInitializationRate"),
                        VolumeSize=params.get(f"{ebs_prefix}.VolumeSize"),
                        VolumeType=params.get(f"{ebs_prefix}.VolumeType"),
                    )
                block_device_mappings.append(
                    BlockDeviceMapping(
                        DeviceName=device_name,
                        Ebs=ebs,
                        NoDevice=no_device,
                        VirtualName=virtual_name,
                    )
                )
        else:
            # Use instance block device mapping if available
            block_device_mappings = getattr(instance, "blockDeviceMapping", []) or []

        # TagSpecification.N - parse tags for image and snapshots
        tag_specifications = []
        tag_spec_indices = set()
        for key in params:
            if key.startswith("TagSpecification."):
                parts = key.split(".")
                if len(parts) > 1 and parts[1].isdigit():
                    tag_spec_indices.add(parts[1])
        for idx in sorted(tag_spec_indices, key=int):
            prefix = f"TagSpecification.{idx}"
            resource_type = params.get(f"{prefix}.ResourceType")
            tags = []
            # Parse tags
            tag_indices = set()
            for key in params:
                if key.startswith(f"{prefix}.Tag."):
                    parts = key.split(".")
                    if len(parts) > 3 and parts[3].isdigit():
                        tag_indices.add(parts[3])
            for t_idx in sorted(tag_indices, key=int):
                tag_key = params.get(f"{prefix}.Tag.{t_idx}.Key")
                tag_value = params.get(f"{prefix}.Tag.{t_idx}.Value")
                if tag_key is not None and tag_value is not None:
                    tags.append(Tag(Key=tag_key, Value=tag_value))
            tag_specifications.append(TagSpecification(ResourceType=resource_type, Tags=tags))

        # Compose tagSet for image and snapshots
        image_tags = []
        snapshot_tags = []
        for ts in tag_specifications:
            if ts.ResourceType == "image":
                image_tags.extend(ts.Tags)
            elif ts.ResourceType == "snapshot":
                snapshot_tags.extend(ts.Tags)
            else:
                # Invalid resource type for tagging on creation
                raise ValueError(f"Invalid ResourceType in TagSpecification: {ts.ResourceType}")

        # Compose new Image object
        new_image = Image(
            architecture=getattr(instance, "architecture", None),
            blockDeviceMapping=block_device_mappings,
            bootMode=getattr(instance, "bootMode", None),
            creationDate=None,
            deprecationTime=None,
            deregistrationProtection=None,
            description=description,
            enaSupport=getattr(instance, "enaSupport", None),
            freeTierEligible=None,
            hypervisor=getattr(instance, "hypervisor", None),
            imageAllowed=None,
            imageId=new_image_id,
            imageLocation=None,
            imageOwnerAlias=None,
            imageOwnerId=self.get_owner_id(),
            imageState="available",
            imageType="machine",
            imdsSupport=None,
            isPublic=False,
            kernelId=getattr(instance, "kernelId", None),
            lastLaunchedTime=None,
            name=name,
            platform=getattr(instance, "platform", None),
            platformDetails=None,
            productCodes=[],
            ramdiskId=getattr(instance, "ramdiskId", None),
            rootDeviceName=getattr(instance, "rootDeviceName", None),
            rootDeviceType=getattr(instance, "rootDeviceType", None),
            sourceImageId=None,
            sourceImageRegion=None,
            sourceInstanceId=instance_id,
            sriovNetSupport=None,
            stateReason=None,
            tagSet=image_tags,
            tpmSupport=None,
            usageOperation=None,
            virtualizationType=getattr(instance, "virtualizationType", None),
        )

        # Save new image in state
        self.state.amis[new_image_id] = new_image
        self.state.resources[new_image_id] = new_image

        # Snapshot tags are not stored here because snapshots are not modeled in this emulator

        return {"requestId": self.generate_request_id(), "imageId": new_image_id}


    def create_image_usage_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        image_id = params.get("ImageId")
        resource_types = params.get("ResourceType.N")
        if not image_id:
            raise ValueError("ImageId is required")
        if not resource_types:
            raise ValueError("ResourceType.N is required")

        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id(), "reportId": None}

        # Validate image exists
        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        # Generate report ID
        report_id = self.generate_unique_id(prefix="iur-")

        # Parse AccountId.N if present
        account_ids = params.get("AccountId.N", [])

        # Parse TagSpecification.N for image-usage-report resource type
        tag_specifications = []
        tag_spec_indices = set()
        for key in params:
            if key.startswith("TagSpecification."):
                parts = key.split(".")
                if len(parts) > 1 and parts[1].isdigit():
                    tag_spec_indices.add(parts[1])
        for idx in sorted(tag_spec_indices, key=int):
            prefix = f"TagSpecification.{idx}"
            resource_type = params.get(f"{prefix}.ResourceType")
            tags = []
            tag_indices = set()
            for key in params:
                if key.startswith(f"{prefix}.Tag."):
                    parts = key.split(".")
                    if len(parts) > 3 and parts[3].isdigit():
                        tag_indices.add(parts[3])
            for t_idx in sorted(tag_indices, key=int):
                tag_key = params.get(f"{prefix}.Tag.{t_idx}.Key")
                tag_value = params.get(f"{prefix}.Tag.{t_idx}.Value")
                if tag_key is not None and tag_value is not None:
                    tags.append(Tag(Key=tag_key, Value=tag_value))
            tag_specifications.append(TagSpecification(ResourceType=resource_type, Tags=tags))

        # Validate that if tags are specified, ResourceType must be image-usage-report
        for ts in tag_specifications:
            if ts.ResourceType != "image-usage-report":
                raise ValueError("TagSpecification ResourceType must be 'image-usage-report' for image usage report")

        # Compose ImageUsageResourceType list from resource_types param
        resource_type_objs = []
        for rt in resource_types:
            # rt is expected to be dict with ResourceType and ResourceTypeOptions
            resource_type_name = rt.get("ResourceType")
            options = []
            for opt in rt.get("ResourceTypeOptions", []):
                option_name = opt.get("OptionName")
                option_values = opt.get("OptionValues", [])
                options.append(ImageUsageResourceTypeOption(OptionName=option_name, OptionValues=option_values))
            resource_type_objs.append(ImageUsageResourceType(resourceType=resource_type_name, resourceTypeOptionSet=options))

        # Compose ImageUsageReport object (not stored in state for emulator)
        report = ImageUsageReport(
            accountIdSet=account_ids,
            creationTime=None,
            expirationTime=None,
            imageId=image_id,
            reportId=report_id,
            resourceTypeSet=resource_type_objs,
            state="pending",
            stateReason=None,
            tagSet=tag_specifications[0].Tags if tag_specifications else [],
        )

        # For emulator, we do not store the report, just return reportId and requestId
        return {"requestId": self.generate_request_id(), "reportId": report_id}


    def create_restore_image_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        bucket = params.get("Bucket")
        object_key = params.get("ObjectKey")
        if not bucket:
            raise ValueError("Bucket is required")
        if not object_key:
            raise ValueError("ObjectKey is required")

        # DryRun check
        if params.get("DryRun"):
            return {"requestId": self.generate_request_id(), "imageId": None}

        # Name for restored AMI
        name = params.get("Name")

        # Compose new image ID
        new_image_id = self.generate_unique_id(prefix="ami-")

        # TagSpecification.N - parse tags for image and snapshots
        tag_specifications = []
        tag_spec_indices = set()
        for key in params:
            if key.startswith("TagSpecification."):
                parts = key.split(".")
                if len(parts) > 1 and parts[1].isdigit():
                    tag_spec_indices.add(parts[1])
        for idx in sorted(tag_spec_indices, key=int):
            prefix = f"TagSpecification.{idx}"
            resource_type = params.get(f"{prefix}.ResourceType")
            tags = []
            tag_indices = set()
            for key in params:
                if key.startswith(f"{prefix}.Tag."):
                    parts = key.split(".")
                    if len(parts) > 3 and parts[3].isdigit():
                        tag_indices.add(parts[3])
            for t_idx in sorted(tag_indices, key=int):
                tag_key = params.get(f"{prefix}.Tag.{t_idx}.Key")
                tag_value = params.get(f"{prefix}.Tag.{t_idx}.Value")
                if tag_key is not None and tag_value is not None:
                    tags.append(Tag(Key=tag_key, Value=tag_value))
            tag_specifications.append(TagSpecification(ResourceType=resource_type, Tags=tags))

        # Compose tagSet for image and snapshots
        image_tags = []
        snapshot_tags = []
        for ts in tag_specifications:
            if ts.ResourceType == "image":
                image_tags.extend(ts.Tags)
            elif ts.ResourceType == "snapshot":
                snapshot_tags.extend(ts.Tags)
            else:
                # Invalid resource type for tagging on restoration
                raise ValueError(f"Invalid ResourceType in TagSpecification: {ts.ResourceType}")

        # Compose new Image object
        new_image = Image(
            architecture=None,
            blockDeviceMapping=[],
            bootMode=None,
            creationDate=None,
            deprecationTime=None,
            deregistrationProtection=None,
            description=None,
            enaSupport=None,
            freeTierEligible=None,
            hypervisor=None,
            imageAllowed=None,
            imageId=new_image_id,
            imageLocation=None,
            imageOwnerAlias=None,
            imageOwnerId=self.get_owner_id(),
            imageState="available",
            imageType=None,
            imdsSupport=None,
            isPublic=False,
            kernelId=None,
            lastLaunchedTime=None,
            name=name,
            platform=None,
            platformDetails=None,
            productCodes=[],
            ramdiskId=None,
            rootDeviceName=None,
            rootDeviceType=None,
            sourceImageId=None,
            sourceImageRegion=None,
            sourceInstanceId=None,
            sriovNetSupport=None,
            stateReason=None,
            tagSet=image_tags,
            tpmSupport=None,
            usageOperation=None,
            virtualizationType=None,
        )

        # Save new image in state
        self.state.amis[new_image_id] = new_image
        self.state.resources[new_image_id] = new_image

        return {"requestId": self.generate_request_id(), "imageId": new_image_id}

    def create_store_image_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        bucket = params.get("Bucket")
        image_id = params.get("ImageId")
        dry_run = params.get("DryRun", False)
        s3_object_tags = params.get("S3ObjectTag.N", [])

        if dry_run:
            # For dry run, check permissions - here we assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        if not bucket:
            raise ValueError("Bucket parameter is required")
        if not image_id:
            raise ValueError("ImageId parameter is required")

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"AMI {image_id} does not exist")

        # Simulate storing the AMI as a single object in S3 bucket
        # Generate a unique object key for the stored AMI object
        object_key = f"{image_id}-stored-image"

        # Store tags for the S3 object if provided
        tags = []
        for tag_dict in s3_object_tags:
            key = tag_dict.get("Key")
            value = tag_dict.get("Value")
            if key is not None and value is not None:
                tags.append(Tag(Key=key, Value=value))

        # We do not have actual S3 storage, so just simulate storing metadata
        # Save store image task result in state for possible future reference
        store_task = StoreImageTaskResult(
            amiId=image_id,
            bucket=bucket,
            progressPercentage=100,
            s3objectKey=object_key,
            storeTaskFailureReason=None,
            storeTaskState="completed",
            taskStartTime=None,
        )
        self.state.resources[object_key] = store_task

        return {
            "objectKey": object_key,
            "requestId": self.generate_request_id(),
        }


    def delete_image_usage_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        report_id = params.get("ReportId")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        if not report_id:
            raise ValueError("ReportId parameter is required")

        # The image usage reports are stored in self.state.resources keyed by reportId
        report = self.state.resources.get(report_id)
        if not report or not isinstance(report, ImageUsageReport):
            # If report does not exist, AWS returns success anyway
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Delete the report
        del self.state.resources[report_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def deregister_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        delete_associated_snapshots = params.get("DeleteAssociatedSnapshots", False)
        dry_run = params.get("DryRun", False)
        image_id = params.get("ImageId")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        if not image_id:
            raise ValueError("ImageId parameter is required")

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"AMI {image_id} does not exist")

        # Deregister the AMI: remove from self.state.amis and move to recycle bin if applicable
        # For simplicity, we simulate Recycle Bin behavior by storing in a recycle bin dict
        # Check if image matches a recycle bin retention rule (not implemented here, so assume no)
        # If no retention rule, delete immediately

        # Collect snapshot IDs associated with the AMI
        snapshot_ids = []
        for bdm in image.blockDeviceMapping:
            if bdm.Ebs and bdm.Ebs.SnapshotId:
                snapshot_ids.append(bdm.Ebs.SnapshotId)

        delete_snapshot_result_set = []
        for snapshot_id in snapshot_ids:
            # Check if snapshot is associated with multiple AMIs
            associated_amis = []
            for ami in self.state.amis.values():
                for bdm in ami.blockDeviceMapping:
                    if bdm.Ebs and bdm.Ebs.SnapshotId == snapshot_id:
                        associated_amis.append(ami.imageId)
            if len(associated_amis) > 1:
                # Snapshot associated with multiple AMIs, skip deletion
                delete_snapshot_result_set.append({
                    "returnCode": "skipped",
                    "snapshotId": snapshot_id,
                })
            else:
                if delete_associated_snapshots:
                    # Simulate snapshot deletion success
                    # Remove snapshot from state.resources if exists
                    if snapshot_id in self.state.resources:
                        del self.state.resources[snapshot_id]
                    delete_snapshot_result_set.append({
                        "returnCode": "success",
                        "snapshotId": snapshot_id,
                    })
                else:
                    # Not deleting snapshot
                    delete_snapshot_result_set.append({
                        "returnCode": "skipped",
                        "snapshotId": snapshot_id,
                    })

        # Remove the AMI from state.amis and state.resources
        if image_id in self.state.amis:
            del self.state.amis[image_id]
        if image_id in self.state.resources:
            del self.state.resources[image_id]

        return {
            "deleteSnapshotResultSet": delete_snapshot_result_set,
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def describe_fast_launch_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        image_ids = params.get("ImageId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # For simplicity, we simulate fast launch images as a dict keyed by imageId in state.resources
        # Filter fast launch images by imageId and filters

        # Collect all fast launch images from state.resources
        fast_launch_images = []
        for resource in self.state.resources.values():
            # We assume fast launch images are stored as dicts with keys matching response parameters
            # We check for presence of 'imageId' and 'state' keys to identify fast launch images
            if isinstance(resource, dict) and "imageId" in resource:
                fast_launch_images.append(resource)

        # Filter by image_ids if provided
        if image_ids:
            fast_launch_images = [fli for fli in fast_launch_images if fli.get("imageId") in image_ids]

        # Apply filters if provided
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            if name == "resource-type":
                fast_launch_images = [fli for fli in fast_launch_images if fli.get("resourceType") in values]
            elif name == "owner-id":
                fast_launch_images = [fli for fli in fast_launch_images if fli.get("ownerId") in values]
            elif name == "state":
                fast_launch_images = [fli for fli in fast_launch_images if fli.get("state") in values]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000  # default max results

        end_index = start_index + max_results
        page_items = fast_launch_images[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(fast_launch_images) else None

        return {
            "fastLaunchImageSet": page_items,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_image_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attribute = params.get("Attribute")
        dry_run = params.get("DryRun", False)
        image_id = params.get("ImageId")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        if not attribute:
            raise ValueError("Attribute parameter is required")
        if not image_id:
            raise ValueError("ImageId parameter is required")

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"AMI {image_id} does not exist")

        # Prepare response dict
        response = {
            "requestId": self.generate_request_id(),
            "imageId": image_id,
        }

        # Map attribute to image properties
        if attribute == "description":
            response["description"] = AttributeValue(Value=image.description)
        elif attribute == "kernel":
            response["kernel"] = AttributeValue(Value=image.kernelId)
        elif attribute == "ramdisk":
            response["ramdisk"] = AttributeValue(Value=image.ramdiskId)
        elif attribute == "launchPermission":
            response["launchPermission"] = image.launchPermission if hasattr(image, "launchPermission") else []
            # If launchPermission is not a list, convert to list
            if not isinstance(response["launchPermission"], list):
                response["launchPermission"] = [response["launchPermission"]]
        elif attribute == "productCodes":
            response["productCodes"] = image.productCodes
        elif attribute == "blockDeviceMapping":
            # Deprecated attribute, return error per docs
            return {"Error": {"Code": "Client.AuthFailure", "Message": "The blockDeviceMapping attribute is deprecated"}}
        elif attribute == "sriovNetSupport":
            response["sriovNetSupport"] = AttributeValue(Value=image.sriovNetSupport)
        elif attribute == "bootMode":
            response["bootMode"] = AttributeValue(Value=image.bootMode)
        elif attribute == "tpmSupport":
            response["tpmSupport"] = AttributeValue(Value=image.tpmSupport)
        elif attribute == "uefiData":
            response["uefiData"] = AttributeValue(Value=None)  # No data available
        elif attribute == "lastLaunchedTime":
            response["lastLaunchedTime"] = AttributeValue(Value=image.lastLaunchedTime)
        elif attribute == "imdsSupport":
            response["imdsSupport"] = AttributeValue(Value=image.imdsSupport)
        elif attribute == "deregistrationProtection":
            response["deregistrationProtection"] = AttributeValue(Value=image.deregistrationProtection)
        else:
            # Unknown attribute, return empty or error
            response[attribute] = None

        return response

    from typing import Any, Dict, List, Optional, Set, Tuple
    from datetime import datetime
    import re

    def describe_image_references(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter ImageId.N
        image_ids = []
        for key in params:
            if key.startswith("ImageId."):
                image_ids.append(params[key])
        if not image_ids:
            raise Exception("Missing required parameter ImageId.N")
        if len(image_ids) > 10:
            raise Exception("Maximum 10 ImageId.N allowed")

        include_all_resource_types = params.get("IncludeAllResourceTypes", False)
        resource_types_param = []
        for key in params:
            if key.startswith("ResourceType."):
                # ResourceType.N.ResourceType or ResourceType.N.ResourceTypeOptions
                # We need to parse ResourceType.N and its nested fields
                # Collect all ResourceType.N groups
                pass
        # Parse ResourceType.N parameters
        resource_types: List[Dict[str, Any]] = []
        resource_type_pattern = re.compile(r"ResourceType\.(\d+)\.(.+)")
        resource_type_options_pattern = re.compile(r"ResourceType\.(\d+)\.ResourceTypeOptions\.(\d+)\.(.+)")
        # Collect resource types and options
        resource_type_map: Dict[int, Dict[str, Any]] = {}
        resource_type_options_map: Dict[Tuple[int,int], Dict[str, Any]] = {}
        for key, value in params.items():
            m_opt = resource_type_options_pattern.match(key)
            if m_opt:
                rt_idx = int(m_opt.group(1))
                opt_idx = int(m_opt.group(2))
                field = m_opt.group(3)
                resource_type_options_map.setdefault((rt_idx,opt_idx), {})[field] = value
                continue
            m_rt = resource_type_pattern.match(key)
            if m_rt:
                rt_idx = int(m_rt.group(1))
                field = m_rt.group(2)
                resource_type_map.setdefault(rt_idx, {})[field] = value
        # Build resource_types list
        for rt_idx in sorted(resource_type_map.keys()):
            rt_entry = resource_type_map[rt_idx]
            # Collect options for this resource type
            options = []
            for (r_idx, o_idx), opt_fields in resource_type_options_map.items():
                if r_idx == rt_idx:
                    option_name = opt_fields.get("OptionName")
                    option_values = []
                    # OptionValues.N
                    for k,v in opt_fields.items():
                        if k.startswith("OptionValues."):
                            option_values.append(v)
                    options.append({
                        "OptionName": option_name,
                        "OptionValues": option_values,
                    })
            resource_types.append({
                "ResourceType": rt_entry.get("ResourceType"),
                "ResourceTypeOptions": options,
            })

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5:
                    raise Exception("MaxResults must be at least 5")
            except Exception:
                raise Exception("Invalid MaxResults value")

        next_token = params.get("NextToken")

        # Validate that either IncludeAllResourceTypes or ResourceTypes is specified
        if not include_all_resource_types and not resource_types:
            raise Exception("Either IncludeAllResourceTypes or ResourceTypes must be specified")

        # For this emulator, we will simulate image references by scanning resources referencing the images
        # Supported resource types: ec2:Instance, ec2:LaunchTemplate, ssm:Parameter, imagebuilder:ImageRecipe, imagebuilder:ContainerRecipe
        # We will check only ec2:Instance and ec2:LaunchTemplate in this emulator (others not implemented)
        # We will collect references for each image id

        # For pagination, we will flatten all references and then paginate

        references = []
        # For each image id, find references
        for image_id in image_ids:
            # ec2:Instance references
            for instance_id, instance in self.state.instances.items() if hasattr(self.state, "instances") else []:
                # Check if instance references this image
                if getattr(instance, "image_id", None) == image_id:
                    references.append({
                        "arn": f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:instance/{instance_id}",
                        "imageId": image_id,
                        "resourceType": "ec2:Instance",
                    })
            # ec2:LaunchTemplate references
            for lt_id, lt in self.state.launch_templates.items() if hasattr(self.state, "launch_templates") else []:
                # Check if launch template references this image
                # For simplicity, check if lt.default_version or lt.latest_version references image_id
                # This is a simplification; real AWS has versions with launch template data
                if getattr(lt, "image_id", None) == image_id:
                    references.append({
                        "arn": f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:launch-template/{lt_id}",
                        "imageId": image_id,
                        "resourceType": "ec2:LaunchTemplate",
                    })
            # ssm:Parameter, imagebuilder:ImageRecipe, imagebuilder:ContainerRecipe not implemented in this emulator

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = len(references)
        if max_results:
            end_index = min(start_index + max_results, len(references))
        paged_references = references[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(references) else None

        return {
            "imageReferenceSet": paged_references,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def describe_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Parse parameters
        image_ids = []
        for key in params:
            if key.startswith("ImageId."):
                image_ids.append(params[key])
        owners = []
        for key in params:
            if key.startswith("Owner."):
                owners.append(params[key])
        executable_by = []
        for key in params:
            if key.startswith("ExecutableBy."):
                executable_by.append(params[key])
        filters = []
        # Parse filters: Filter.N.Name and Filter.N.Value.M
        filter_name_pattern = re.compile(r"Filter\.(\d+)\.Name")
        filter_value_pattern = re.compile(r"Filter\.(\d+)\.Value\.(\d+)")
        filter_map = {}
        for key, value in params.items():
            m_name = filter_name_pattern.match(key)
            if m_name:
                idx = int(m_name.group(1))
                filter_map.setdefault(idx, {})["Name"] = value
            m_value = filter_value_pattern.match(key)
            if m_value:
                idx = int(m_value.group(1))
                val_idx = int(m_value.group(2))
                filter_map.setdefault(idx, {}).setdefault("Values", []).append(value)
        for idx in sorted(filter_map.keys()):
            filters.append(filter_map[idx])

        include_deprecated = params.get("IncludeDeprecated", False)
        if isinstance(include_deprecated, str):
            include_deprecated = include_deprecated.lower() == "true"
        include_disabled = params.get("IncludeDisabled", False)
        if isinstance(include_disabled, str):
            include_disabled = include_disabled.lower() == "true"
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    raise Exception("MaxResults must be at least 1")
            except Exception:
                raise Exception("Invalid MaxResults value")
        next_token = params.get("NextToken")

        # Collect images to return
        images = list(self.state.amis.values())

        # Filter by image_ids if specified
        if image_ids:
            images = [img for img in images if img.imageId in image_ids]

        # Filter by owners if specified
        if owners:
            def owner_match(img):
                for owner in owners:
                    if owner == "self" and img.imageOwnerId == self.get_owner_id():
                        return True
                    if owner == "amazon" and img.imageOwnerAlias == "amazon":
                        return True
                    if owner == "aws-backup-vault" and img.imageOwnerAlias == "aws-backup-vault":
                        return True
                    if owner == "aws-marketplace" and img.imageOwnerAlias == "aws-marketplace":
                        return True
                    if owner == img.imageOwnerId:
                        return True
                return False
            images = [img for img in images if owner_match(img)]

        # Filter by executable_by - for simplicity, we skip this in emulator

        # Filter by deprecated and disabled
        if not include_deprecated:
            images = [img for img in images if not img.deprecationTime]
        if not include_disabled:
            images = [img for img in images if img.imageState != "disabled"]

        # Apply filters
        def match_filter(img, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            # Support some common filters
            # For tag:<key> and tag-key
            if name.startswith("tag:"):
                tag_key = name[4:]
                tag_values = set(values)
                for tag in img.tagSet:
                    if tag.Key == tag_key and tag.Value in tag_values:
                        return True
                return False
            if name == "tag-key":
                tag_keys = set(values)
                for tag in img.tagSet:
                    if tag.Key in tag_keys:
                        return True
                return False
            # Other filters by attribute
            attr_map = {
                "architecture": img.architecture,
                "block-device-mapping.delete-on-termination": None,  # complex, skip
                "block-device-mapping.device-name": None,
                "block-device-mapping.snapshot-id": None,
                "block-device-mapping.volume-size": None,
                "block-device-mapping.volume-type": None,
                "block-device-mapping.encrypted": None,
                "creation-date": img.creationDate,
                "description": img.description,
                "ena-support": img.enaSupport,
                "free-tier-eligible": img.freeTierEligible,
                "hypervisor": img.hypervisor,
                "image-allowed": img.imageAllowed,
                "image-id": img.imageId,
                "image-type": img.imageType,
                "is-public": img.isPublic,
                "kernel-id": img.kernelId,
                "manifest-location": img.imageLocation,
                "name": img.name,
                "owner-alias": img.imageOwnerAlias,
                "owner-id": img.imageOwnerId,
                "platform": img.platform,
                "product-code": None,  # complex, skip
                "ramdisk-id": img.ramdiskId,
                "root-device-name": img.rootDeviceName,
                "root-device-type": img.rootDeviceType,
                "source-image-id": img.sourceImageId,
                "source-image-region": img.sourceImageRegion,
                "source-instance-id": img.sourceInstanceId,
                "state": img.imageState,
                "state-reason-code": img.stateReason.code if img.stateReason else None,
                "state-reason-message": img.stateReason.message if img.stateReason else None,
                "sriov-net-support": img.sriovNetSupport,
                "virtualization-type": img.virtualizationType,
            }
            val = attr_map.get(name)
            if val is None:
                # For boolean filters, convert string to bool
                if name in ["ena-support", "free-tier-eligible", "image-allowed", "is-public"]:
                    val = False
                else:
                    return False
            # For boolean values, convert to string "true"/"false"
            if isinstance(val, bool):
                val_str = "true" if val else "false"
                return any(v.lower() == val_str for v in values)
            # For string values, support wildcard *
            for v in values:
                if v == "*":
                    return True
                if v.endswith("*"):
                    if val and val.startswith(v[:-1]):
                        return True
                else:
                    if val == v:
                        return True
            return False

        for f in filters:
            images = [img for img in images if match_filter(img, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = len(images)
        if max_results:
            end_index = min(start_index + max_results, len(images))
        paged_images = images[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(images) else None

        # Convert images to dicts
        images_set = [img.to_dict() for img in paged_images]

        return {
            "imagesSet": images_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def describe_image_usage_report_entries(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Parse filters
        filters = []
        filter_name_pattern = re.compile(r"Filter\.(\d+)\.Name")
        filter_value_pattern = re.compile(r"Filter\.(\d+)\.Value\.(\d+)")
        filter_map = {}
        for key, value in params.items():
            m_name = filter_name_pattern.match(key)
            if m_name:
                idx = int(m_name.group(1))
                filter_map.setdefault(idx, {})["Name"] = value
            m_value = filter_value_pattern.match(key)
            if m_value:
                idx = int(m_value.group(1))
                val_idx = int(m_value.group(2))
                filter_map.setdefault(idx, {}).setdefault("Values", []).append(value)
        for idx in sorted(filter_map.keys()):
            filters.append(filter_map[idx])

        image_ids = []
        for key in params:
            if key.startswith("ImageId."):
                image_ids.append(params[key])
        report_ids = []
        for key in params:
            if key.startswith("ReportId."):
                report_ids.append(params[key])
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    raise Exception("MaxResults must be at least 1")
            except Exception:
                raise Exception("Invalid MaxResults value")
        next_token = params.get("NextToken")

        # Collect all usage report entries from state
        entries = []
        for report in self.state.image_usage_reports.values() if hasattr(self.state, "image_usage_reports") else []:
            if report_ids and report.reportId not in report_ids:
                continue
            if image_ids and report.imageId not in image_ids:
                continue
            # Each report has entries? For emulator, assume report has entries attribute
            for entry in getattr(report, "entries", []):
                # Apply filters
                def match_filter_entry(entry_obj, f):
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not name or not values:
                        return True
                    val = getattr(entry_obj, name, None)
                    if val is None:
                        return False
                    for v in values:
                        if v == "*":
                            return True
                        if str(val) == v:
                            return True
                    return False
                if all(match_filter_entry(entry, f) for f in filters):
                    entries.append(entry)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        end_index = len(entries)
        if max_results:
            end_index = min(start_index + max_results, len(entries))
        paged_entries = entries[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(entries) else None

        # Convert entries to dicts
        entries_set = [entry.to_dict() for entry in paged_entries]

        return {
            "imageUsageReportEntrySet": entries_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def describe_image_usage_reports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Parse filters
        filters = []
        filter_name_pattern = re.compile(r"Filter\.(\d+)\.Name")
        filter_value_pattern = re.compile(r"Filter\.(\d+)\.Value\.(\d+)")
        filter_map = {}
        for key, value in params.items():
            m_name = filter_name_pattern.match(key)
            if m_name:
                idx = int(m_name.group(1))
                filter_map.setdefault(idx, {})["Name"] = value
            m_value = filter_value_pattern.match(key)
            if m_value:
                idx = int(m_value.group(1))
                val_idx = int(m_value.group(2))
                filter_map.setdefault(idx, {}).setdefault("Values", []).append(value)
        for idx in sorted(filter_map.keys()):
            filters.append(filter_map[idx])

        image_ids = []
        for key in params:
            if key.startswith("ImageId."):
                image_ids.append(params[key])
        report_ids = []
        for key in params:
            if key.startswith("ReportId."):
                report_ids.append(params[key])
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    raise Exception("MaxResults must be at least 1")
            except Exception:
                raise Exception("Invalid MaxResults value")
        next_token = params.get("NextToken")

        # Collect all usage reports from state
        reports = list(self.state.image_usage_reports.values()) if hasattr(self.state, "image_usage_reports") else []

        # Filter by report_ids and image_ids
        if report_ids:
            reports = [r for r in reports if r.reportId in report_ids]
        if image_ids:
            reports = [r for r in reports if r.imageId in image_ids]

        # Apply filters
        def match_filter_report(report_obj, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            val = getattr(report_obj, name, None)
            if val is None:
                # For tag:<key> and tag-key
                if name.startswith("tag:"):
                    tag_key = name[4:]
                    tag_values = set(values)
                    for tag in getattr(report_obj, "tagSet", []):
                        if tag.Key == tag_key and tag.Value in tag_values:
                            return True
                    return False
                if name == "tag-key":
                    tag_keys = set(values)
                    for tag in getattr(report_obj, "tagSet", []):
                        if tag.Key in tag_keys:
                            return True
                    return False
                return False

    from typing import Any, Dict, List, Optional
    from datetime import datetime, timedelta

    def describe_store_image_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun
        if params.get("DryRun"):
            # Assume permission check passes for this emulator
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Extract filters and parameters
        filters = params.get("Filter", [])
        image_ids = params.get("ImageId", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 200:
                raise ValueError("MaxResults must be an integer between 1 and 200")

        # If ImageId is specified, filters are ignored
        if image_ids and filters:
            filters = []

        # Collect all store image tasks from state
        all_tasks: List[StoreImageTaskResult] = []
        for task in self.state.store_image_tasks.values():
            # If ImageId filter is specified, only include tasks for those AMIs
            if image_ids and task.amiId not in image_ids:
                continue

            # Apply filters if no ImageId filter
            if filters and not image_ids:
                match = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if name == "task-state":
                        if task.storeTaskState not in values:
                            match = False
                            break
                    elif name == "bucket":
                        if task.bucket not in values:
                            match = False
                            break
                    else:
                        # Unknown filter name, ignore or exclude
                        match = False
                        break
                if not match:
                    continue

            all_tasks.append(task)

        # Sort tasks in reverse chronological order by taskStartTime (newest first)
        def parse_time(t: Optional[str]) -> datetime:
            if not t:
                return datetime.min
            try:
                return datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ")
            except Exception:
                try:
                    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")
                except Exception:
                    return datetime.min

        all_tasks.sort(key=lambda t: parse_time(t.taskStartTime), reverse=True)

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_tasks)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_tasks))

        paged_tasks = all_tasks[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(all_tasks):
            new_next_token = str(end_index)

        # Convert tasks to dicts
        store_image_task_result_set = [task.to_dict() for task in paged_tasks]

        return {
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "storeImageTaskResultSet": store_image_task_result_set,
        }


    def disable_allowed_images_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Disable allowed images settings for the account in this region
        self.state.allowed_images_settings_state = "disabled"

        return {
            "allowedImagesSettingsState": "disabled",
            "requestId": self.generate_request_id(),
        }


    def disable_fast_launch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        image_id = params.get("ImageId")
        if not image_id:
            raise ValueError("ImageId is required")

        force = params.get("Force", False)

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        # Check if image is Windows and owned by caller or shared
        # For emulator, assume all images are eligible

        # Disable fast launch settings
        fast_launch_info = self.state.fast_launch_images.get(image_id)
        if not fast_launch_info:
            # No fast launch enabled, return default response
            response = {
                "imageId": image_id,
                "launchTemplate": None,
                "maxParallelLaunches": None,
                "ownerId": image.imageOwnerId or self.get_owner_id(),
                "requestId": self.generate_request_id(),
                "resourceType": None,
                "snapshotConfiguration": None,
                "state": "disabling",
                "stateTransitionReason": "Fast launch disable requested",
                "stateTransitionTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
            return response

        # Simulate cleanup of pre-provisioned snapshots
        # If force is False and cleanup fails, raise error (emulated as always success)
        # Remove fast launch info from state
        del self.state.fast_launch_images[image_id]

        response = {
            "imageId": image_id,
            "launchTemplate": fast_launch_info.get("launchTemplate"),
            "maxParallelLaunches": fast_launch_info.get("maxParallelLaunches"),
            "ownerId": image.imageOwnerId or self.get_owner_id(),
            "requestId": self.generate_request_id(),
            "resourceType": "snapshot",
            "snapshotConfiguration": fast_launch_info.get("snapshotConfiguration"),
            "state": "disabling",
            "stateTransitionReason": "Fast launch disabled",
            "stateTransitionTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        return response


    def disable_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        image_id = params.get("ImageId")
        if not image_id:
            raise ValueError("ImageId is required")

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        # Set AMI state to disabled
        image.imageState = "disabled"

        # Remove all launch permissions
        image.launchPermissions = []

        # Make AMI private if public or shared
        image.isPublic = False

        # Remove sharing with accounts, orgs, OUs - emulate by clearing launchPermissions
        # Already done above

        # Remove from describe images default? For emulator, just keep state

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def disable_image_block_public_access(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Remove block public access restriction from account in this region
        self.state.image_block_public_access_state = "unblocked"

        return {
            "imageBlockPublicAccessState": "unblocked",
            "requestId": self.generate_request_id(),
        }

    def disable_image_deprecation(self, params: dict) -> dict:
        image_id = params.get("ImageId")
        if not image_id:
            raise ValueError("ImageId is required")

        # DryRun check
        if params.get("DryRun"):
            # Here we simulate permission check, assume always allowed for emulator
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"AMI {image_id} does not exist")

        # Cancel deprecation by clearing deprecationTime
        image.deprecationTime = None

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def disable_image_deregistration_protection(self, params: dict) -> dict:
        image_id = params.get("ImageId")
        if not image_id:
            raise ValueError("ImageId is required")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"AMI {image_id} does not exist")

        # Disable deregistration protection
        # According to docs, deregistrationProtection is a string, e.g. "enabled" or None
        image.deregistrationProtection = None

        return {
            "requestId": self.generate_request_id(),
            "return": "true",
        }


    def enable_allowed_images_settings(self, params: dict) -> dict:
        state = params.get("AllowedImagesSettingsState")
        if not state or state not in ("enabled", "audit-mode"):
            raise ValueError("AllowedImagesSettingsState is required and must be 'enabled' or 'audit-mode'")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Save the allowed images settings state in self.state
        self.state.allowed_images_settings_state = state

        return {
            "allowedImagesSettingsState": state,
            "requestId": self.generate_request_id(),
        }


    def enable_fast_launch(self, params: dict) -> dict:
        image_id = params.get("ImageId")
        if not image_id:
            raise ValueError("ImageId is required")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"AMI {image_id} does not exist")

        # Validate LaunchTemplate if provided
        launch_template_param = params.get("LaunchTemplate")
        launch_template_response = None
        if launch_template_param:
            version = launch_template_param.get("Version")
            if not version:
                raise ValueError("LaunchTemplate.Version is required")
            launch_template_id = launch_template_param.get("LaunchTemplateId")
            launch_template_name = launch_template_param.get("LaunchTemplateName")
            # Both LaunchTemplateId and LaunchTemplateName cannot be set simultaneously
            if launch_template_id and launch_template_name:
                raise ValueError("LaunchTemplateId and LaunchTemplateName cannot both be specified")
            launch_template_response = FastLaunchLaunchTemplateSpecificationResponse(
                launchTemplateId=launch_template_id,
                launchTemplateName=launch_template_name,
                version=version,
            )

        max_parallel_launches = params.get("MaxParallelLaunches")
        if max_parallel_launches is not None:
            if not isinstance(max_parallel_launches, int) or max_parallel_launches < 6:
                raise ValueError("MaxParallelLaunches must be an integer >= 6")

        resource_type = params.get("ResourceType", "snapshot")
        if resource_type != "snapshot":
            raise ValueError("ResourceType must be 'snapshot' if specified")

        snapshot_config_param = params.get("SnapshotConfiguration")
        snapshot_configuration_response = None
        if snapshot_config_param:
            target_resource_count = snapshot_config_param.get("TargetResourceCount")
            if target_resource_count is not None and (not isinstance(target_resource_count, int) or target_resource_count < 0):
                raise ValueError("SnapshotConfiguration.TargetResourceCount must be a non-negative integer if specified")
            snapshot_configuration_response = FastLaunchSnapshotConfigurationResponse(
                targetResourceCount=target_resource_count
            )

        # Store fast launch configuration in image metadata or state
        # For emulator, we can store in image.fast_launch attribute (create if not exists)
        if not hasattr(image, "fast_launch"):
            image.fast_launch = {}

        image.fast_launch["launchTemplate"] = launch_template_response
        image.fast_launch["maxParallelLaunches"] = max_parallel_launches
        image.fast_launch["resourceType"] = resource_type
        image.fast_launch["snapshotConfiguration"] = snapshot_configuration_response
        image.fast_launch["state"] = "enabled"
        image.fast_launch["stateTransitionReason"] = None
        image.fast_launch["stateTransitionTime"] = None
        image.fast_launch["ownerId"] = self.get_owner_id()

        return {
            "imageId": image_id,
            "launchTemplate": launch_template_response.to_dict() if launch_template_response else None,
            "maxParallelLaunches": max_parallel_launches,
            "ownerId": self.get_owner_id(),
            "requestId": self.generate_request_id(),
            "resourceType": resource_type,
            "snapshotConfiguration": snapshot_configuration_response.to_dict() if snapshot_configuration_response else None,
            "state": "enabled",
            "stateTransitionReason": None,
            "stateTransitionTime": None,
        }


    def enable_image(self, params: dict) -> dict:
        image_id = params.get("ImageId")
        if not image_id:
            raise ValueError("ImageId is required")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        image = self.state.amis.get(image_id)
        if not image:
            raise ValueError(f"AMI {image_id} does not exist")

        # Re-enable the image by marking it as available
        image.imageState = "available"
        # If there was a disabled flag or similar, clear it
        if hasattr(image, "disabled"):
            image.disabled = False

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    from typing import Any, Dict, List, Optional
    from datetime import datetime, timezone, timedelta

    def enable_image_block_public_access(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        state_value = params.get("ImageBlockPublicAccessState")
        if state_value != "block-new-sharing":
            raise Exception("InvalidParameterValue: ImageBlockPublicAccessState must be 'block-new-sharing'")

        # DryRun check
        if params.get("DryRun"):
            # Here we assume permission is granted for simplicity
            raise Exception("DryRunOperation")

        # Set the state in backend state
        self.state.image_block_public_access_state = "block-new-sharing"

        return {
            "imageBlockPublicAccessState": "block-new-sharing",
            "requestId": self.generate_request_id(),
        }

    def enable_image_deprecation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        image_id = params.get("ImageId")
        deprecate_at = params.get("DeprecateAt")
        if not image_id:
            raise Exception("MissingParameter: ImageId is required")
        if not deprecate_at:
            raise Exception("MissingParameter: DeprecateAt is required")

        # DryRun check
        if params.get("DryRun"):
            raise Exception("DryRunOperation")

        # Validate image exists
        image = self.state.amis.get(image_id)
        if not image:
            raise Exception(f"InvalidAMIID.NotFound: The image id '{image_id}' does not exist")

        # Validate deprecate_at format and value
        try:
            # Parse ISO8601 timestamp
            dt = datetime.strptime(deprecate_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            try:
                dt = datetime.strptime(deprecate_at, "%Y-%m-%dT%H:%M:%SZ")
                dt = dt.replace(tzinfo=timezone.utc)
            except Exception:
                raise Exception("InvalidParameterValue: DeprecateAt must be in ISO8601 format")

        now = datetime.now(timezone.utc)
        if dt <= now:
            raise Exception("InvalidParameterValue: DeprecateAt cannot be in the past")

        # Check upper limit for deprecateAt
        max_years = 2 if image.isPublic else 10
        max_dt = now + timedelta(days=365*max_years)
        if dt > max_dt:
            raise Exception(f"InvalidParameterValue: DeprecateAt cannot be more than {max_years} years from now")

        # Set deprecation time on image
        image.deprecationTime = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"  # Format with milliseconds truncated to 3 digits

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def enable_image_deregistration_protection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        image_id = params.get("ImageId")
        if not image_id:
            raise Exception("MissingParameter: ImageId is required")

        # DryRun check
        if params.get("DryRun"):
            raise Exception("DryRunOperation")

        image = self.state.amis.get(image_id)
        if not image:
            raise Exception(f"InvalidAMIID.NotFound: The image id '{image_id}' does not exist")

        # Enable deregistration protection
        # We store this as a boolean attribute on the image object
        image.deregistrationProtection = True

        # WithCooldown parameter is accepted but no further action needed in this mock
        # (In real AWS, it enforces protection for 24h after disabling)

        return {
            "requestId": self.generate_request_id(),
            "return": "true",
        }

    def get_allowed_images_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        if params.get("DryRun"):
            raise Exception("DryRunOperation")

        # Retrieve allowed images settings from state
        # We assume self.state.allowed_images_settings is a dict with keys:
        # 'imageCriterionSet', 'managedBy', 'state'
        settings = getattr(self.state, "allowed_images_settings", None)
        if not settings:
            # Default values if not set
            settings = {
                "imageCriterionSet": [],
                "managedBy": "account",
                "state": "disabled",
            }

        # Compose response
        # imageCriterionSet is a list of dicts with possible nested fields
        # We must convert objects to dicts if needed
        image_criterion_set = []
        for criterion in settings.get("imageCriterionSet", []):
            # Each criterion is expected to be a dict or object with to_dict()
            if hasattr(criterion, "to_dict"):
                image_criterion_set.append(criterion.to_dict())
            else:
                image_criterion_set.append(criterion)

        return {
            "imageCriterionSet": image_criterion_set,
            "managedBy": settings.get("managedBy"),
            "requestId": self.generate_request_id(),
            "state": settings.get("state"),
        }

    def get_image_ancestry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        image_id = params.get("ImageId")
        if not image_id:
            raise Exception("MissingParameter: ImageId is required")

        # DryRun check
        if params.get("DryRun"):
            raise Exception("DryRunOperation")

        # Validate image exists
        image = self.state.amis.get(image_id)
        if not image:
            raise Exception(f"InvalidAMIID.NotFound: The image id '{image_id}' does not exist")

        # Build ancestry chain from image to root
        ancestry_list = []
        current_image = image
        while current_image:
            entry = {
                "creationDate": current_image.creationDate,
                "imageId": current_image.imageId,
                "imageOwnerAlias": current_image.imageOwnerAlias,
                "sourceImageId": current_image.sourceImageId,
                "sourceImageRegion": current_image.sourceImageRegion,
            }
            ancestry_list.append(entry)
            if not current_image.sourceImageId:
                break
            current_image = self.state.amis.get(current_image.sourceImageId)
            if current_image is None:
                # If source image not found, stop chain
                break

        return {
            "imageAncestryEntrySet": ancestry_list,
            "requestId": self.generate_request_id(),
        }

    def get_image_block_public_access_state(self, params: dict) -> dict:
        # DryRun parameter check
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For simplicity, assume permission granted
            # In real implementation, check permissions and raise DryRunOperation or UnauthorizedOperation
            return {
                "requestId": self.generate_request_id(),
                "imageBlockPublicAccessState": "block-new-sharing",
                "managedBy": "account",
            }

        # Return current state of block public access for AMIs at account level in the region
        # For this emulator, assume state is stored in self.state.image_block_public_access_state
        # If not set, default to "unblocked"
        state = getattr(self.state, "image_block_public_access_state", "unblocked")
        managed_by = getattr(self.state, "image_block_public_access_managed_by", "account")

        return {
            "requestId": self.generate_request_id(),
            "imageBlockPublicAccessState": state,
            "managedBy": managed_by,
        }


    def modify_image_attribute(self, params: dict) -> dict:
        # Validate required parameter ImageId
        image_id = params.get("ImageId")
        if not image_id:
            raise Exception("Missing required parameter ImageId")

        # DryRun parameter check
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Retrieve the image from state
        image = self.state.amis.get(image_id)
        if not image:
            raise Exception(f"InvalidAMIID.NotFound: The image id '{image_id}' does not exist")

        # Validate attribute parameter if present
        attribute = params.get("Attribute")

        # Handle Description attribute
        if attribute == "description" or "Description" in params or "Value" in params:
            # Description can be set via Description.Value or Value parameter
            description_value = None
            if "Description" in params and isinstance(params["Description"], dict):
                description_value = params["Description"].get("Value")
            elif "Value" in params:
                description_value = params["Value"]
            if description_value is not None:
                image.description = description_value

        # Handle ImdsSupport attribute
        if attribute == "imdsSupport" or "ImdsSupport" in params:
            imds_support_value = None
            if "ImdsSupport" in params and isinstance(params["ImdsSupport"], dict):
                imds_support_value = params["ImdsSupport"].get("Value")
            elif "Value" in params:
                imds_support_value = params["Value"]
            if imds_support_value is not None:
                # Only allow setting to "v2.0"
                if imds_support_value != "v2.0":
                    raise Exception("InvalidParameterValue: ImdsSupport value must be 'v2.0'")
                # Once set to v2.0, cannot be undone (emulated by setting attribute)
                image.imdsSupport = imds_support_value

        # Handle LaunchPermission attribute
        if attribute == "launchPermission" or any(k.startswith("LaunchPermission") for k in params.keys()):
            # We expect LaunchPermissionModifications object with Add and Remove lists
            # Parse Add and Remove launch permissions from params
            add_permissions = []
            remove_permissions = []

            # Helper to parse launch permission entries from params
            def parse_launch_permissions(prefix):
                permissions = []
                index = 1
                while True:
                    base_key = f"{prefix}.{index}"
                    # Check if any of the keys exist for this index
                    group = params.get(f"{base_key}.Group")
                    ou_arn = params.get(f"{base_key}.OrganizationalUnitArn")
                    org_arn = params.get(f"{base_key}.OrganizationArn")
                    user_id = params.get(f"{base_key}.UserId")
                    if not any([group, ou_arn, org_arn, user_id]):
                        break
                    perm = LaunchPermission(
                        Group=group,
                        OrganizationalUnitArn=ou_arn,
                        OrganizationArn=org_arn,
                        UserId=user_id,
                    )
                    permissions.append(perm)
                    index += 1
                return permissions

            # Also check if LaunchPermission is passed as a dict with Add and Remove keys
            launch_permission_mods = params.get("LaunchPermission")
            if isinstance(launch_permission_mods, dict):
                # Parse Add list
                add_list = launch_permission_mods.get("Add", [])
                for add_item in add_list:
                    perm = LaunchPermission(
                        Group=add_item.get("Group"),
                        OrganizationalUnitArn=add_item.get("OrganizationalUnitArn"),
                        OrganizationArn=add_item.get("OrganizationArn"),
                        UserId=add_item.get("UserId"),
                    )
                    add_permissions.append(perm)
                # Parse Remove list
                remove_list = launch_permission_mods.get("Remove", [])
                for rem_item in remove_list:
                    perm = LaunchPermission(
                        Group=rem_item.get("Group"),
                        OrganizationalUnitArn=rem_item.get("OrganizationalUnitArn"),
                        OrganizationArn=rem_item.get("OrganizationArn"),
                        UserId=rem_item.get("UserId"),
                    )
                    remove_permissions.append(perm)

            # Also parse legacy params with LaunchPermission.Add.N and LaunchPermission.Remove.N
            add_permissions.extend(parse_launch_permissions("LaunchPermission.Add"))
            remove_permissions.extend(parse_launch_permissions("LaunchPermission.Remove"))

            # OperationType parameter (add or remove)
            operation_type = params.get("OperationType")

            # UserGroup.N, UserId.N, OrganizationalUnitArn.N, OrganizationArn.N parameters
            # These are alternative ways to specify launch permissions
            # Add or Remove depends on OperationType or presence of Add/Remove keys
            def parse_list_param(param_name):
                result = []
                i = 1
                while True:
                    val = params.get(f"{param_name}.{i}")
                    if val is None:
                        break
                    result.append(val)
                    i += 1
                return result

            user_groups = parse_list_param("UserGroup")
            user_ids = parse_list_param("UserId")
            ou_arns = parse_list_param("OrganizationalUnitArn")
            org_arns = parse_list_param("OrganizationArn")

            # If OperationType is add or remove, apply accordingly
            if operation_type == "add":
                for group in user_groups:
                    add_permissions.append(LaunchPermission(Group=group))
                for uid in user_ids:
                    add_permissions.append(LaunchPermission(UserId=uid))
                for ou in ou_arns:
                    add_permissions.append(LaunchPermission(OrganizationalUnitArn=ou))
                for org in org_arns:
                    add_permissions.append(LaunchPermission(OrganizationArn=org))
            elif operation_type == "remove":
                for group in user_groups:
                    remove_permissions.append(LaunchPermission(Group=group))
                for uid in user_ids:
                    remove_permissions.append(LaunchPermission(UserId=uid))
                for ou in ou_arns:
                    remove_permissions.append(LaunchPermission(OrganizationalUnitArn=ou))
                for org in org_arns:
                    remove_permissions.append(LaunchPermission(OrganizationArn=org))

            # ProductCode.N is not supported, but if present, add product codes to image
            product_codes = []
            i = 1
            while True:
                pc = params.get(f"ProductCode.{i}")
                if not pc:
                    break
                product_codes.append(pc)
                i += 1
            for pc in product_codes:
                # Add product code to image.productCodes if not already present
                if not any(pc == p.productCode for p in image.productCodes):
                    image.productCodes.append(ProductCode(productCode=pc))

            # Now apply Add and Remove launch permissions to image
            # For simplicity, image has attribute launchPermissions as list of LaunchPermission
            if not hasattr(image, "launchPermissions") or image.launchPermissions is None:
                image.launchPermissions = []

            # Remove permissions
            def permission_match(p1: LaunchPermission, p2: LaunchPermission) -> bool:
                return (
                    p1.Group == p2.Group and
                    p1.OrganizationalUnitArn == p2.OrganizationalUnitArn and
                    p1.OrganizationArn == p2.OrganizationArn and
                    p1.UserId == p2.UserId
                )

            # Remove matching permissions
            for rem_perm in remove_permissions:
                image.launchPermissions = [
                    p for p in image.launchPermissions if not permission_match(p, rem_perm)
                ]

            # Add permissions if not already present
            for add_perm in add_permissions:
                if not any(permission_match(add_perm, p) for p in image.launchPermissions):
                    image.launchPermissions.append(add_perm)

        # Save updated image back to state (already updated in place)
        self.state.amis[image_id] = image

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def register_image(self, params: dict) -> dict:
        # DryRun parameter check
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For simplicity, assume permission granted
            return {
                "requestId": self.generate_request_id(),
                "imageId": None,
            }

        # Validate required parameter Name
        name = params.get("Name")
        if not name:
            raise Exception("Missing required parameter Name")

        # Generate new AMI ID
        new_ami_id = self.generate_unique_id(prefix="ami-")

        # Parse BlockDeviceMapping.N entries
        block_device_mappings = []
        i = 1
        while True:
            prefix = f"BlockDeviceMapping.{i}"
            device_name = params.get(f"{prefix}.DeviceName")
            if device_name is None:
                break

            # Parse Ebs block device if present
            ebs_prefix = f"{prefix}.Ebs"
            ebs = None
            # Check if any Ebs fields exist
            ebs_fields_present = any(
                params.get(f"{ebs_prefix}.{field}") is not None
                for field in [
                    "AvailabilityZone",
                    "AvailabilityZoneId",
                    "DeleteOnTermination",
                    "Encrypted",
                    "Iops",
                    "KmsKeyId",
                    "OutpostArn",
                    "SnapshotId",
                    "Throughput",
                    "VolumeInitializationRate",
                    "VolumeSize",
                    "VolumeType",
                ]
            )
            if ebs_fields_present:
                ebs = EbsBlockDevice(
                    AvailabilityZone=params.get(f"{ebs_prefix}.AvailabilityZone"),
                    AvailabilityZoneId=params.get(f"{ebs_prefix}.AvailabilityZoneId"),
                    DeleteOnTermination=params.get(f"{ebs_prefix}.DeleteOnTermination"),
                    Encrypted=params.get(f"{ebs_prefix}.Encrypted"),
                    Iops=params.get(f"{ebs_prefix}.Iops"),
                    KmsKeyId=params.get(f"{ebs_prefix}.KmsKeyId"),
                    OutpostArn=params.get(f"{ebs_prefix}.OutpostArn"),
                    SnapshotId=params.get(f"{ebs_prefix}.SnapshotId"),
                    Throughput=params.get(f"{ebs_prefix}.Throughput"),
                    VolumeInitializationRate=params.get(f"{ebs_prefix}.VolumeInitializationRate"),
                    VolumeSize=params.get(f"{ebs_prefix}.VolumeSize"),
                    VolumeType=params.get(f"{ebs_prefix}.VolumeType"),
                )

            no_device = params.get(f"{prefix}.NoDevice")
            virtual_name = params.get(f"{prefix}.VirtualName")

            bdm = BlockDeviceMapping(
                DeviceName=device_name,
                Ebs=ebs,
                NoDevice=no_device,
                VirtualName=virtual_name,
            )
            block_device_mappings.append(bdm)
            i += 1

        # Parse TagSpecification.N entries
        tag_specifications = []
        i = 1
        while True:
            prefix = f"TagSpecification.{i}"
            resource_type = params.get(f"{prefix}.ResourceType")
            if resource_type is None:
                break
            # Parse tags
            tags = []
            j = 1
            while True:
                tag_key = params.get(f"{prefix}.Tags.{j}.Key")
                tag_value = params.get(f"{prefix}.Tags.{j}.Value")
                if tag_key is None and tag_value is None:
                    break
                if tag_key is not None:
                    tags.append(Tag(Key=tag_key, Value=tag_value))
                j += 1
            tag_specifications.append(TagSpecification(ResourceType=resource_type, Tags=tags))
            i += 1

        # Create new Image object
        image = Image(
            architecture=params.get("Architecture"),
            blockDeviceMapping=block_device_mappings,
            bootMode=params.get("BootMode"),
            creationDate=None,  # Could set to current time ISO8601 string
            deprecationTime=None,
            deregistrationProtection=None,
            description=params.get("Description"),
            enaSupport=params.get("EnaSupport"),
            freeTierEligible=None,
            hypervisor=None,
            imageAllowed=None,
            imageId=new_ami_id,
            imageLocation=params.get("ImageLocation"),
            imageOwnerAlias=None,
            imageOwnerId=self.get_owner_id(),
            imageState="available",
            imageType=None,
            imdsSupport=params.get("ImdsSupport"),
            isPublic=False,
            kernelId=params.get("KernelId"),
            lastLaunchedTime=None,
            name=name,
            platform=None,
            platformDetails=None,
            productCodes=[],
            ramdiskId=params.get("RamdiskId"),
            rootDeviceName=params.get("RootDeviceName"),
            rootDeviceType=None,
            sourceImageId=None,
            sourceImageRegion=None,
            sourceInstanceId=None,
            sriovNetSupport=params.get("SriovNetSupport"),
            stateReason=None,
            tagSet=[],
            tpmSupport=params.get("TpmSupport"),
            usageOperation=None,
            virtualizationType=params.get("VirtualizationType"),
        )

        # Apply tags from tag specifications with ResourceType == "image"
        for tag_spec in tag_specifications:
            if tag_spec.ResourceType == "image":
                image.tagSet.extend(tag_spec.Tags)

        # Save image to state
        self.state.amis[new_ami_id] = image

        return {
            "requestId": self.generate_request_id(),
            "imageId": new_ami_id,
        }


    def replace_image_criteria_in_allowed_images_settings(self, params: dict) -> dict:
        # DryRun parameter check
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Parse ImageCriterion.N list
        image_criteria = []
        i = 1
        while True:
            prefix = f"ImageCriterion.{i}"
            # Check if any field exists for this index
            if not any(
                params.get(f"{prefix}.{field}") is not None
                for field in [
                    "CreationDateCondition.MaximumDaysSinceCreated",
                    "DeprecationTimeCondition.MaximumDaysSinceDeprecated",
                    "ImageNames",
                    "ImageProviders",
                    "MarketplaceProductCodes",
                ]
            ):
                break

            # Parse CreationDateCondition
            creation_date_condition = None
            max_days_created = params.get(f"{prefix}.CreationDateCondition.MaximumDaysSinceCreated")
            if max_days_created is not None:
                creation_date_condition = {"MaximumDaysSinceCreated": int(max_days_created)}

            # Parse DeprecationTimeCondition
            deprecation_time_condition = None
            max_days_deprecated = params.get(f"{prefix}.DeprecationTimeCondition.MaximumDaysSinceDeprecated")
            if max_days_deprecated is not None:
                deprecation_time_condition = {"MaximumDaysSinceDeprecated": int(max_days_deprecated)}

            # Parse ImageNames (comma separated or multiple params?)
            image_names = []
            j = 1
            while True:
                val = params.get(f"{prefix}.ImageNames.{j}")
                if val is None:
                    break
                image_names.append(val)
                j += 1
            if not image_names:
                # Try single param as comma separated string
                val = params.get(f"{prefix}.ImageNames")
                if val:
                    image_names = [v.strip() for v in val.split(",") if v.strip()]

            # Parse ImageProviders
            image_providers = []
            j = 1
            while True:
                val = params.get(f"{prefix}.ImageProviders.{j}")
                if val is None:
                    break
                image_providers.append(val)
                j += 1
            if not image_providers:
                val = params.get(f"{prefix}.ImageProviders")
                if val:
                    image_providers = [v.strip() for v in val.split(",") if v.strip()]

            # Parse MarketplaceProductCodes
            marketplace_product_codes = []
            j = 1
            while True:
                val = params.get(f"{prefix}.MarketplaceProductCodes.{j}")
                if val is None:
                    break
                marketplace_product_codes.append(val)
                j += 1
            if not marketplace_product_codes:
                val = params.get(f"{prefix}.MarketplaceProductCodes")
                if val:
                    marketplace_product_codes = [v.strip() for v in val.split(",") if v.strip()]

            # Compose ImageCriterionRequest object (emulated as dict)
            image_criterion = {
                "CreationDateCondition": creation_date_condition,
                "DeprecationTimeCondition": deprecation_time_condition,
                "ImageNames": image_names,
                "ImageProviders": image_providers,
                "MarketplaceProductCodes": marketplace_product_codes,
            }
            image_criteria.append(image_criterion)
            i += 1

        # Save criteria to state (emulated)
        self.state.allowed_images_criteria = image_criteria

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def reset_image_attribute(self, params: dict) -> dict:
        # Validate required parameters
        attribute = params.get("Attribute")
        image_id = params.get("ImageId")
        if not attribute:
            raise Exception("Missing required parameter Attribute")
        if not image_id:
            raise Exception("Missing required parameter ImageId")

        # DryRun parameter check
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Only launchPermission attribute can be reset
        if attribute != "launchPermission":
            raise Exception("InvalidParameterValue: Only 'launchPermission' attribute can be reset")

        # Retrieve image
        image = self.state.amis.get(image_id)
        if not image:
            raise Exception(f"InvalidAMIID.NotFound: The image id '{image_id}' does not exist")

        # Reset launch permissions to default (empty list)
        image.launchPermissions = []

        # Save updated image
        self.state.amis[image_id] = image

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    from typing import Dict, Any, List, Optional
    from datetime import datetime

    def list_images_in_recycle_bin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun parameter
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For simplicity, assume permission is always granted in this emulator
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate ImageId.N parameter (list of image IDs)
        image_ids: Optional[List[str]] = params.get("ImageId.N")
        if image_ids is not None:
            if not isinstance(image_ids, list):
                raise ValueError("ImageId.N must be a list of strings")
            if len(image_ids) > 20:
                raise ValueError("You can specify up to 20 ImageId.N values")

        # Validate MaxResults parameter
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ValueError("MaxResults must be an integer")
            if max_results < 1 or max_results > 1000:
                raise ValueError("MaxResults must be between 1 and 1000")

        # Validate NextToken parameter
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ValueError("NextToken must be a string")

        # Filter images in recycle bin
        # self.state.amis is a dict of imageId -> Image object
        # We assume images in recycle bin have a non-null recycleBinEnterTime attribute in their recycle_bin_info
        # We store recycle bin info in self.state.recycle_bin_images dict keyed by imageId (simulate)
        recycle_bin_images_dict = getattr(self.state, "recycle_bin_images", {})
        # If not present, no images in recycle bin
        if not recycle_bin_images_dict:
            recycle_bin_images_dict = {}

        # Filter by image_ids if provided
        filtered_images = []
        if image_ids is not None:
            for image_id in image_ids:
                info = recycle_bin_images_dict.get(image_id)
                if info is not None:
                    filtered_images.append(info)
        else:
            filtered_images = list(recycle_bin_images_dict.values())

        # Pagination logic
        # NextToken is expected to be an index encoded as string, e.g. "0", "10", etc.
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ValueError("Invalid NextToken value")

        # Apply pagination
        if max_results is None:
            max_results = 1000  # default max

        paged_images = filtered_images[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(filtered_images):
            new_next_token = str(start_index + max_results)

        # Build response imageSet list
        image_set = []
        for info in paged_images:
            # info is an ImageRecycleBinInfo object
            image_set.append({
                "description": info.description,
                "imageId": info.imageId,
                "name": info.name,
                "recycleBinEnterTime": info.recycleBinEnterTime,
                "recycleBinExitTime": info.recycleBinExitTime,
            })

        return {
            "imageSet": image_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def restore_image_from_recycle_bin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun parameter
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For simplicity, assume permission is always granted in this emulator
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate required ImageId parameter
        image_id = params.get("ImageId")
        if not image_id or not isinstance(image_id, str):
            raise ValueError("ImageId is required and must be a string")

        # Check if image is in recycle bin
        recycle_bin_images_dict = getattr(self.state, "recycle_bin_images", {})
        if image_id not in recycle_bin_images_dict:
            # Image not found in recycle bin
            raise ValueError(f"Image {image_id} not found in Recycle Bin")

        # Restore image: remove from recycle bin and mark as enabled in self.state.amis
        info = recycle_bin_images_dict.pop(image_id)

        # Update self.state.recycle_bin_images
        self.state.recycle_bin_images = recycle_bin_images_dict

        # Update image state in self.state.amis
        image = self.state.amis.get(image_id)
        if image is None:
            # Image not found in main AMIs dict, create a new Image object with minimal info
            image = Image()
            image.imageId = image_id
            self.state.amis[image_id] = image

        # Mark image as enabled (simulate by setting imageState to "available")
        image.imageState = "available"

        # Remove recycle bin info from image if stored there
        if hasattr(image, "recycle_bin_info"):
            delattr(image, "recycle_bin_info")

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class AMIsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CancelImageLaunchPermission", self.cancel_image_launch_permission)
        self.register_action("CopyImage", self.copy_image)
        self.register_action("CreateImage", self.create_image)
        self.register_action("CreateImageUsageReport", self.create_image_usage_report)
        self.register_action("CreateRestoreImageTask", self.create_restore_image_task)
        self.register_action("CreateStoreImageTask", self.create_store_image_task)
        self.register_action("DeleteImageUsageReport", self.delete_image_usage_report)
        self.register_action("DeregisterImage", self.deregister_image)
        self.register_action("DescribeFastLaunchImages", self.describe_fast_launch_images)
        self.register_action("DescribeImageAttribute", self.describe_image_attribute)
        self.register_action("DescribeImageReferences", self.describe_image_references)
        self.register_action("DescribeImages", self.describe_images)
        self.register_action("DescribeImageUsageReportEntries", self.describe_image_usage_report_entries)
        self.register_action("DescribeImageUsageReports", self.describe_image_usage_reports)
        self.register_action("DescribeInstanceImageMetadata", self.describe_instance_image_metadata)
        self.register_action("DescribeStoreImageTasks", self.describe_store_image_tasks)
        self.register_action("DisableAllowedImagesSettings", self.disable_allowed_images_settings)
        self.register_action("DisableFastLaunch", self.disable_fast_launch)
        self.register_action("DisableImage", self.disable_image)
        self.register_action("DisableImageBlockPublicAccess", self.disable_image_block_public_access)
        self.register_action("DisableImageDeprecation", self.disable_image_deprecation)
        self.register_action("DisableImageDeregistrationProtection", self.disable_image_deregistration_protection)
        self.register_action("EnableAllowedImagesSettings", self.enable_allowed_images_settings)
        self.register_action("EnableFastLaunch", self.enable_fast_launch)
        self.register_action("EnableImage", self.enable_image)
        self.register_action("EnableImageBlockPublicAccess", self.enable_image_block_public_access)
        self.register_action("EnableImageDeprecation", self.enable_image_deprecation)
        self.register_action("EnableImageDeregistrationProtection", self.enable_image_deregistration_protection)
        self.register_action("GetAllowedImagesSettings", self.get_allowed_images_settings)
        self.register_action("GetImageAncestry", self.get_image_ancestry)
        self.register_action("GetImageBlockPublicAccessState", self.get_image_block_public_access_state)
        self.register_action("ModifyImageAttribute", self.modify_image_attribute)
        self.register_action("RegisterImage", self.register_image)
        self.register_action("ReplaceImageCriteriaInAllowedImagesSettings", self.replace_image_criteria_in_allowed_images_settings)
        self.register_action("ResetImageAttribute", self.reset_image_attribute)
        self.register_action("ListImagesInRecycleBin", self.list_images_in_recycle_bin)
        self.register_action("RestoreImageFromRecycleBin", self.restore_image_from_recycle_bin)

    def cancel_image_launch_permission(self, params):
        return self.backend.cancel_image_launch_permission(params)

    def copy_image(self, params):
        return self.backend.copy_image(params)

    def create_image(self, params):
        return self.backend.create_image(params)

    def create_image_usage_report(self, params):
        return self.backend.create_image_usage_report(params)

    def create_restore_image_task(self, params):
        return self.backend.create_restore_image_task(params)

    def create_store_image_task(self, params):
        return self.backend.create_store_image_task(params)

    def delete_image_usage_report(self, params):
        return self.backend.delete_image_usage_report(params)

    def deregister_image(self, params):
        return self.backend.deregister_image(params)

    def describe_fast_launch_images(self, params):
        return self.backend.describe_fast_launch_images(params)

    def describe_image_attribute(self, params):
        return self.backend.describe_image_attribute(params)

    def describe_image_references(self, params):
        return self.backend.describe_image_references(params)

    def describe_images(self, params):
        return self.backend.describe_images(params)

    def describe_image_usage_report_entries(self, params):
        return self.backend.describe_image_usage_report_entries(params)

    def describe_image_usage_reports(self, params):
        return self.backend.describe_image_usage_reports(params)

    def describe_instance_image_metadata(self, params):
        return self.backend.describe_instance_image_metadata(params)

    def describe_store_image_tasks(self, params):
        return self.backend.describe_store_image_tasks(params)

    def disable_allowed_images_settings(self, params):
        return self.backend.disable_allowed_images_settings(params)

    def disable_fast_launch(self, params):
        return self.backend.disable_fast_launch(params)

    def disable_image(self, params):
        return self.backend.disable_image(params)

    def disable_image_block_public_access(self, params):
        return self.backend.disable_image_block_public_access(params)

    def disable_image_deprecation(self, params):
        return self.backend.disable_image_deprecation(params)

    def disable_image_deregistration_protection(self, params):
        return self.backend.disable_image_deregistration_protection(params)

    def enable_allowed_images_settings(self, params):
        return self.backend.enable_allowed_images_settings(params)

    def enable_fast_launch(self, params):
        return self.backend.enable_fast_launch(params)

    def enable_image(self, params):
        return self.backend.enable_image(params)

    def enable_image_block_public_access(self, params):
        return self.backend.enable_image_block_public_access(params)

    def enable_image_deprecation(self, params):
        return self.backend.enable_image_deprecation(params)

    def enable_image_deregistration_protection(self, params):
        return self.backend.enable_image_deregistration_protection(params)

    def get_allowed_images_settings(self, params):
        return self.backend.get_allowed_images_settings(params)

    def get_image_ancestry(self, params):
        return self.backend.get_image_ancestry(params)

    def get_image_block_public_access_state(self, params):
        return self.backend.get_image_block_public_access_state(params)

    def modify_image_attribute(self, params):
        return self.backend.modify_image_attribute(params)

    def register_image(self, params):
        return self.backend.register_image(params)

    def replace_image_criteria_in_allowed_images_settings(self, params):
        return self.backend.replace_image_criteria_in_allowed_images_settings(params)

    def reset_image_attribute(self, params):
        return self.backend.reset_image_attribute(params)

    def list_images_in_recycle_bin(self, params):
        return self.backend.list_images_in_recycle_bin(params)

    def restore_image_from_recycle_bin(self, params):
        return self.backend.restore_image_from_recycle_bin(params)
