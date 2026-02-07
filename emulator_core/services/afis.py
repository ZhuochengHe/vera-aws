from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class StorageLocation:
    bucket: Optional[str] = None
    key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Bucket": self.bucket,
            "Key": self.key,
        }


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Key": self.key,
            "Value": self.value,
        }


@dataclass
class TagSpecification:
    resource_type: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class LoadPermission:
    group: Optional[str] = None  # Valid Values: all
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.group is not None:
            d["Group"] = self.group
        if self.user_id is not None:
            d["UserId"] = self.user_id
        return d


@dataclass
class LoadPermissionRequest:
    group: Optional[str] = None  # Valid Values: all
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.group is not None:
            d["Group"] = self.group
        if self.user_id is not None:
            d["UserId"] = self.user_id
        return d


@dataclass
class LoadPermissionModifications:
    add: List[LoadPermissionRequest] = field(default_factory=list)
    remove: List[LoadPermissionRequest] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Add": [perm.to_dict() for perm in self.add],
            "Remove": [perm.to_dict() for perm in self.remove],
        }


@dataclass
class ProductCode:
    product_code: Optional[str] = None
    type: Optional[str] = None  # Valid Values: devpay | marketplace

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.product_code is not None:
            d["ProductCode"] = self.product_code
        if self.type is not None:
            d["Type"] = self.type
        return d


@dataclass
class PciId:
    device_id: Optional[str] = None
    subsystem_id: Optional[str] = None
    subsystem_vendor_id: Optional[str] = None
    vendor_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.device_id is not None:
            d["DeviceId"] = self.device_id
        if self.subsystem_id is not None:
            d["SubsystemId"] = self.subsystem_id
        if self.subsystem_vendor_id is not None:
            d["SubsystemVendorId"] = self.subsystem_vendor_id
        if self.vendor_id is not None:
            d["VendorId"] = self.vendor_id
        return d


class FpgaImageStateCode(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass
class FpgaImageState:
    code: Optional[FpgaImageStateCode] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.code is not None:
            d["Code"] = self.code.value
        if self.message is not None:
            d["Message"] = self.message
        return d


@dataclass
class FpgaImageAttribute:
    description: Optional[str] = None
    fpga_image_id: Optional[str] = None
    load_permissions: List[LoadPermission] = field(default_factory=list)
    name: Optional[str] = None
    product_codes: List[ProductCode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Description": self.description,
            "FpgaImageId": self.fpga_image_id,
            "LoadPermissions": [lp.to_dict() for lp in self.load_permissions],
            "Name": self.name,
            "ProductCodes": [pc.to_dict() for pc in self.product_codes],
        }


@dataclass
class FpgaImage:
    create_time: Optional[datetime] = None
    data_retention_support: Optional[bool] = None
    description: Optional[str] = None
    fpga_image_global_id: Optional[str] = None
    fpga_image_id: Optional[str] = None
    instance_types: List[str] = field(default_factory=list)
    name: Optional[str] = None
    owner_alias: Optional[str] = None  # Possible values: self, amazon, aws-marketplace
    owner_id: Optional[str] = None
    pci_id: Optional[PciId] = None
    product_codes: List[ProductCode] = field(default_factory=list)
    public: Optional[bool] = None
    shell_version: Optional[str] = None
    state: Optional[FpgaImageState] = None
    tags: List[Tag] = field(default_factory=list)
    update_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.create_time is not None:
            d["CreateTime"] = self.create_time.isoformat()
        if self.data_retention_support is not None:
            d["DataRetentionSupport"] = self.data_retention_support
        if self.description is not None:
            d["Description"] = self.description
        if self.fpga_image_global_id is not None:
            d["FpgaImageGlobalId"] = self.fpga_image_global_id
        if self.fpga_image_id is not None:
            d["FpgaImageId"] = self.fpga_image_id
        if self.instance_types:
            d["InstanceTypes"] = self.instance_types
        if self.name is not None:
            d["Name"] = self.name
        if self.owner_alias is not None:
            d["OwnerAlias"] = self.owner_alias
        if self.owner_id is not None:
            d["OwnerId"] = self.owner_id
        if self.pci_id is not None:
            d["PciId"] = self.pci_id.to_dict()
        if self.product_codes:
            d["ProductCodes"] = [pc.to_dict() for pc in self.product_codes]
        if self.public is not None:
            d["Public"] = self.public
        if self.shell_version is not None:
            d["ShellVersion"] = self.shell_version
        if self.state is not None:
            d["State"] = self.state.to_dict()
        if self.tags:
            d["Tags"] = [tag.to_dict() for tag in self.tags]
        if self.update_time is not None:
            d["UpdateTime"] = self.update_time.isoformat()
        return d


class AFIsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage. Use self.state.fpga_images or similar.

    def copy_fpga_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        source_fpga_image_id = params.get("SourceFpgaImageId")
        source_region = params.get("SourceRegion")
        if not source_fpga_image_id:
            raise ValueError("SourceFpgaImageId is required")
        if not source_region:
            raise ValueError("SourceRegion is required")

        # DryRun check (not implemented permissions, so just pass)
        if params.get("DryRun"):
            # In real AWS, would check permissions and raise DryRunOperation or UnauthorizedOperation
            pass

        # Find source AFI in state
        source_afi = self.state.afis.get(source_fpga_image_id)
        if not source_afi:
            # In real AWS, would raise an error for not found
            raise ValueError(f"Source FPGA Image {source_fpga_image_id} not found")

        # Create new AFI as a copy of source with new IDs and updated fields
        new_fpga_image_id = self.generate_unique_id(prefix="afi-")
        new_fpga_image_global_id = self.generate_unique_id(prefix="agfi-")
        now = datetime.utcnow()

        # Copy fields from source, override name and description if provided
        name = params.get("Name") or source_afi.name
        description = params.get("Description") or source_afi.description

        # Copy all other fields from source
        new_afi = FpgaImage(
            create_time=now,
            data_retention_support=source_afi.data_retention_support,
            description=description,
            fpga_image_global_id=new_fpga_image_global_id,
            fpga_image_id=new_fpga_image_id,
            instance_types=list(source_afi.instance_types),
            name=name,
            owner_alias=source_afi.owner_alias,
            owner_id=source_afi.owner_id,
            pci_id=source_afi.pci_id,
            product_codes=list(source_afi.product_codes),
            public=source_afi.public,
            shell_version=source_afi.shell_version,
            state=source_afi.state,
            tags=list(source_afi.tags),
            update_time=now,
        )

        self.state.afis[new_fpga_image_id] = new_afi

        return {
            "fpgaImageId": new_fpga_image_id,
            "requestId": self.generate_request_id(),
        }


    def create_fpga_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        input_storage_location = params.get("InputStorageLocation")
        if not input_storage_location:
            raise ValueError("InputStorageLocation is required")
        if not isinstance(input_storage_location, dict):
            raise ValueError("InputStorageLocation must be a dict")

        # DryRun check (not implemented permissions, so just pass)
        if params.get("DryRun"):
            pass

        # Generate IDs and timestamps
        new_fpga_image_id = self.generate_unique_id(prefix="afi-")
        new_fpga_image_global_id = self.generate_unique_id(prefix="agfi-")
        now = datetime.utcnow()

        # Parse InputStorageLocation
        input_bucket = input_storage_location.get("Bucket")
        input_key = input_storage_location.get("Key")
        input_location = StorageLocation(bucket=input_bucket, key=input_key)

        # Parse LogsStorageLocation if provided
        logs_storage_location = params.get("LogsStorageLocation")
        logs_location = None
        if logs_storage_location and isinstance(logs_storage_location, dict):
            logs_bucket = logs_storage_location.get("Bucket")
            logs_key = logs_storage_location.get("Key")
            logs_location = StorageLocation(bucket=logs_bucket, key=logs_key)

        # Parse TagSpecifications if provided
        tag_specifications = params.get("TagSpecification.N") or []
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            if not isinstance(tag_spec, dict):
                continue
            tag_list = tag_spec.get("Tags") or []
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(key=key, value=value))

        # Create initial state for FPGA image
        state = FpgaImageState(code=None, message=None)

        # Create new FpgaImage object
        new_afi = FpgaImage(
            create_time=now,
            data_retention_support=None,
            description=params.get("Description"),
            fpga_image_global_id=new_fpga_image_global_id,
            fpga_image_id=new_fpga_image_id,
            instance_types=[],
            name=params.get("Name"),
            owner_alias=None,
            owner_id=self.get_owner_id(),
            pci_id=None,
            product_codes=[],
            public=False,
            shell_version=None,
            state=state,
            tags=tags,
            update_time=now,
        )

        self.state.afis[new_fpga_image_id] = new_afi

        return {
            "fpgaImageGlobalId": new_fpga_image_global_id,
            "fpgaImageId": new_fpga_image_id,
            "requestId": self.generate_request_id(),
        }


    def delete_fpga_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        fpga_image_id = params.get("FpgaImageId")
        if not fpga_image_id:
            raise ValueError("FpgaImageId is required")

        # DryRun check (not implemented permissions, so just pass)
        if params.get("DryRun"):
            pass

        if fpga_image_id not in self.state.afis:
            # In real AWS, would raise error for not found
            raise ValueError(f"FPGA Image {fpga_image_id} not found")

        del self.state.afis[fpga_image_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def describe_fpga_image_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attribute = params.get("Attribute")
        fpga_image_id = params.get("FpgaImageId")
        if not attribute:
            raise ValueError("Attribute is required")
        if not fpga_image_id:
            raise ValueError("FpgaImageId is required")

        # DryRun check (not implemented permissions, so just pass)
        if params.get("DryRun"):
            pass

        afi = self.state.afis.get(fpga_image_id)
        if not afi:
            raise ValueError(f"FPGA Image {fpga_image_id} not found")

        # Prepare response attribute object
        attr = FpgaImageAttribute(
            description=None,
            fpga_image_id=fpga_image_id,
            load_permissions=[],
            name=None,
            product_codes=[],
        )

        if attribute == "description":
            attr.description = afi.description
        elif attribute == "name":
            attr.name = afi.name
        elif attribute == "loadPermission":
            # Convert LoadPermission objects from afi.state or afi.load_permissions if exist
            # Here we assume load_permissions are stored in afi.state or afi.load_permissions attribute
            # But from class definition, FpgaImage has no load_permissions attribute, only FpgaImageAttribute has
            # So we try to get from afi.state or empty list
            # For this implementation, we assume afi.state.load_permissions if exists else empty
            # But afi.state is FpgaImageState, no load_permissions attribute
            # So we return empty list
            attr.load_permissions = []
        elif attribute == "productCodes":
            attr.product_codes = afi.product_codes
        else:
            raise ValueError(f"Invalid Attribute value: {attribute}")

        return {
            "fpgaImageAttribute": attr.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def describe_fpga_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check (not implemented permissions, so just pass)
        if params.get("DryRun"):
            pass

        # Filters
        filters = []
        i = 1
        while True:
            filter_name = params.get(f"Filter.{i}.Name")
            if not filter_name:
                break
            values = []
            j = 1
            while True:
                val = params.get(f"Filter.{i}.Value.{j}")
                if val is None:
                    break
                values.append(val)
                j += 1
            filters.append({"Name": filter_name, "Values": values})
            i += 1

        # FpgaImageId.N
        fpga_image_ids = []
        i = 1
        while True:
            afi_id = params.get(f"FpgaImageId.{i}")
            if not afi_id:
                break
            fpga_image_ids.append(afi_id)
            i += 1

        # Owner.N
        owners = []
        i = 1
        while True:
            owner = params.get(f"Owner.{i}")
            if not owner:
                break
            owners.append(owner)
            i += 1

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise ValueError("MaxResults must be between 5 and 1000")
            except Exception:
                raise ValueError("MaxResults must be an integer")

        next_token = params.get("NextToken")
        # For simplicity, we do not implement pagination tokens here

        # Start with all AFIs
        afis = list(self.state.afis.values())

        # Filter by FpgaImageId.N if provided
        if fpga_image_ids:
            afis = [afi for afi in afis if afi.fpga_image_id in fpga_image_ids]

        # Filter by owners if provided
        if owners:
            def owner_match(afi_owner_id, afi_owner_alias):
                for owner in owners:
                    if owner == "self":
                        if afi_owner_id == self.get_owner_id():
                            return True
                    elif owner in ("amazon", "aws-marketplace"):
                        if afi_owner_alias == owner:
                            return True
                    elif afi_owner_id == owner:
                        return True
                return False
            afis = [afi for afi in afis if owner_match(afi.owner_id, afi.owner_alias)]

        # Apply filters
        def matches_filter(afi: FpgaImage, filter: Dict[str, Any]) -> bool:
            name = filter["Name"]
            values = filter["Values"]
            if name == "create-time":
                # Filter by create_time string matching any value
                for val in values:
                    try:
                        val_dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                        if afi.create_time and afi.create_time == val_dt:
                            return True
                    except Exception:
                        continue
                return False
            elif name == "fpga-image-id":
                return afi.fpga_image_id in values
            elif name == "fpga-image-global-id":
                return afi.fpga_image_global_id in values
            elif name == "name":
                return afi.name in values
            elif name == "owner-id":
                return afi.owner_id in values
            elif name == "product-code":
                for pc in afi.product_codes:
                    if pc.product_code in values:
                        return True
                return False
            elif name == "shell-version":
                return afi.shell_version in values
            elif name == "state":
                if afi.state and afi.state.code:
                    return afi.state.code.value in values
                return False
            elif name.startswith("tag:"):
                tag_key = name[4:]
                for tag in afi.tags:
                    if tag.key == tag_key and tag.value in values:
                        return True
                return False
            elif name == "tag-key":
                for tag in afi.tags:
                    if tag.key in values:
                        return True
                return False
            elif name == "update-time":
                for val in values:
                    try:
                        val_dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                        if afi.update_time and afi.update_time == val_dt:
                            return True
                    except Exception:
                        continue
                return False
            else:
                # Unknown filter name, ignore
                return True

        for f in filters:
            afis = [afi for afi in afis if matches_filter(afi, f)]

        # Apply MaxResults
        if max_results is not None:
            afis = afis[:max_results]

        # Prepare response list
        fpga_image_set = [afi.to_dict() for afi in afis]

        return {
            "fpgaImageSet": fpga_image_set,
            "nextToken": None,
            "requestId": self.generate_request_id(),
        }

    def modify_fpga_image_attribute(self, params: dict) -> dict:
        fpga_image_id = params.get("FpgaImageId")
        if not fpga_image_id:
            raise ValueError("FpgaImageId is required")

        afi = self.state.afis.get(fpga_image_id)
        if not afi:
            raise ValueError(f"FpgaImage {fpga_image_id} not found")

        attribute = params.get("Attribute")
        operation_type = params.get("OperationType")
        description = params.get("Description")
        name = params.get("Name")
        load_permission_mods = params.get("LoadPermission")
        product_codes_to_add = params.get("ProductCode.N", [])
        user_groups = params.get("UserGroup.N", [])
        user_ids = params.get("UserId.N", [])

        # Validate Attribute if provided
        valid_attributes = {"description", "name", "loadPermission", "productCodes"}
        if attribute and attribute not in valid_attributes:
            raise ValueError(f"Invalid Attribute value: {attribute}")

        # Modify description
        if (attribute is None or attribute == "description") and description is not None:
            afi.description = description

        # Modify name
        if (attribute is None or attribute == "name") and name is not None:
            afi.name = name

        # Modify loadPermission
        if (attribute is None or attribute == "loadPermission") and (load_permission_mods or user_groups or user_ids):
            # Build add and remove lists from params
            add_permissions = []
            remove_permissions = []

            # If LoadPermission is provided as dict with Add and Remove keys
            if load_permission_mods:
                add_list = load_permission_mods.get("Add", [])
                remove_list = load_permission_mods.get("Remove", [])
                for add_item in add_list:
                    add_permissions.append(LoadPermissionRequest(
                        group=add_item.get("Group"),
                        user_id=add_item.get("UserId"),
                    ))
                for rem_item in remove_list:
                    remove_permissions.append(LoadPermissionRequest(
                        group=rem_item.get("Group"),
                        user_id=rem_item.get("UserId"),
                    ))

            # If UserGroup.N and UserId.N are provided, interpret as add or remove based on OperationType
            if user_groups or user_ids:
                if operation_type not in {"add", "remove"}:
                    raise ValueError("OperationType must be 'add' or 'remove' when modifying loadPermission with UserGroup.N or UserId.N")
                # Compose LoadPermissionRequest objects for add or remove
                # If both user_groups and user_ids are provided, combine them by index
                max_len = max(len(user_groups), len(user_ids))
                for i in range(max_len):
                    group = user_groups[i] if i < len(user_groups) else None
                    user_id = user_ids[i] if i < len(user_ids) else None
                    if operation_type == "add":
                        add_permissions.append(LoadPermissionRequest(group=group, user_id=user_id))
                    else:
                        remove_permissions.append(LoadPermissionRequest(group=group, user_id=user_id))

            # Apply add permissions
            for add_perm in add_permissions:
                # Check if already present
                exists = any(
                    (lp.group == add_perm.group and lp.user_id == add_perm.user_id)
                    for lp in afi.load_permissions
                )
                if not exists:
                    afi.load_permissions.append(LoadPermission(
                        group=add_perm.group,
                        user_id=add_perm.user_id,
                    ))

            # Apply remove permissions
            for rem_perm in remove_permissions:
                afi.load_permissions = [
                    lp for lp in afi.load_permissions
                    if not (lp.group == rem_perm.group and lp.user_id == rem_perm.user_id)
                ]

        # Modify productCodes
        if (attribute is None or attribute == "productCodes") and product_codes_to_add:
            # Adding product codes only, cannot remove
            for pc_str in product_codes_to_add:
                # Check if product code already exists
                exists = any(pc.product_code == pc_str for pc in afi.product_codes)
                if not exists:
                    # Add new product code with type None (type not provided in params)
                    afi.product_codes.append(ProductCode(product_code=pc_str, type=None))

        # Prepare response
        fpga_image_attribute = FpgaImageAttribute(
            description=afi.description,
            fpga_image_id=afi.fpga_image_id,
            load_permissions=afi.load_permissions,
            name=afi.name,
            product_codes=afi.product_codes,
        )

        return {
            "requestId": self.generate_request_id(),
            "fpgaImageAttribute": fpga_image_attribute.to_dict(),
        }


    def reset_fpga_image_attribute(self, params: dict) -> dict:
        fpga_image_id = params.get("FpgaImageId")
        if not fpga_image_id:
            raise ValueError("FpgaImageId is required")

        afi = self.state.afis.get(fpga_image_id)
        if not afi:
            raise ValueError(f"FpgaImage {fpga_image_id} not found")

        attribute = params.get("Attribute")
        if attribute is None:
            raise ValueError("Attribute is required")
        if attribute != "loadPermission":
            raise ValueError("Only 'loadPermission' attribute can be reset")

        # Reset load permissions to empty list
        afi.load_permissions = []

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class AFIsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CopyFpgaImage", self.copy_fpga_image)
        self.register_action("CreateFpgaImage", self.create_fpga_image)
        self.register_action("DeleteFpgaImage", self.delete_fpga_image)
        self.register_action("DescribeFpgaImageAttribute", self.describe_fpga_image_attribute)
        self.register_action("DescribeFpgaImages", self.describe_fpga_images)
        self.register_action("ModifyFpgaImageAttribute", self.modify_fpga_image_attribute)
        self.register_action("ResetFpgaImageAttribute", self.reset_fpga_image_attribute)

    def copy_fpga_image(self, params):
        return self.backend.copy_fpga_image(params)

    def create_fpga_image(self, params):
        return self.backend.create_fpga_image(params)

    def delete_fpga_image(self, params):
        return self.backend.delete_fpga_image(params)

    def describe_fpga_image_attribute(self, params):
        return self.backend.describe_fpga_image_attribute(params)

    def describe_fpga_images(self, params):
        return self.backend.describe_fpga_images(params)

    def modify_fpga_image_attribute(self, params):
        return self.backend.modify_fpga_image_attribute(params)

    def reset_fpga_image_attribute(self, params):
        return self.backend.reset_fpga_image_attribute(params)
