from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re
from ..utils import (get_scalar, get_int, get_indexed_list, parse_filters, apply_filters,
                    parse_tags, str2bool, esc, create_error_response,
                    is_error_response, serialize_error_response)
from ..state import EC2State

class ResourceState(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    RUNNING = 'running'
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    NONEXISTENT = 'non-existent'
    FAILED = 'failed'
    SHUTTING_DOWN = 'shutting-down'
    STOPPING = 'stopping'
    STARTING = 'starting'
    REBOOTING = 'rebooting'
    ATTACHED = 'attached'
    IN_USE = 'in-use'
    CREATING = 'creating'

class ErrorCode(Enum):
    INVALID_PARAMETER_VALUE = 'InvalidParameterValue'
    RESOURCE_NOT_FOUND = 'ResourceNotFound'
    INVALID_STATE_TRANSITION = 'InvalidStateTransition'
    DEPENDENCY_VIOLATION = 'DependencyViolation'

@dataclass
class AFI:
    fpga_image_global_id: str = ""
    fpga_image_id: str = ""

    description: str = ""
    name: str = ""
    create_time: str = ""
    update_time: str = ""
    owner_id: str = ""
    owner_alias: str = ""
    public: bool = False
    state: str = ""
    data_retention_support: bool = False
    instance_types: List[str] = field(default_factory=list)
    pci_id: str = ""
    shell_version: str = ""
    tags: List[Dict[str, Any]] = field(default_factory=list)
    load_permissions: List[Dict[str, Any]] = field(default_factory=list)
    product_codes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fpgaImageGlobalId": self.fpga_image_global_id,
            "fpgaImageId": self.fpga_image_id,
            "createTime": self.create_time,
            "dataRetentionSupport": self.data_retention_support,
            "description": self.description,
            "instanceTypes": self.instance_types,
            "loadPermissions": self.load_permissions,
            "name": self.name,
            "ownerAlias": self.owner_alias,
            "ownerId": self.owner_id,
            "pciId": self.pci_id,
            "productCodes": self.product_codes,
            "public": self.public,
            "shellVersion": self.shell_version,
            "state": self.state,
            "tags": self.tags,
            "updateTime": self.update_time,
        }

class AFI_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.afis  # alias to shared store

    def _get_afi_or_error(self, fpga_image_id: str, message: Optional[str] = None) -> Any:
        afi = self.resources.get(fpga_image_id)
        if not afi:
            error_message = message or f"The ID '{fpga_image_id}' does not exist"
            return create_error_response("InvalidFpgaImageID.NotFound", error_message)
        return afi

    def _build_fpga_image_attribute(self, afi: AFI) -> Dict[str, Any]:
        return {
            "description": afi.description,
            "fpgaImageId": afi.fpga_image_id,
            "loadPermissions": afi.load_permissions,
            "name": afi.name,
            "productCodes": afi.product_codes,
        }

    def CopyFpgaImage(self, params: Dict[str, Any]):
        """Copies the specified Amazon FPGA Image (AFI) to the current Region."""

        if not params.get("SourceFpgaImageId"):
            return create_error_response("MissingParameter", "Missing required parameter: SourceFpgaImageId")
        if not params.get("SourceRegion"):
            return create_error_response("MissingParameter", "Missing required parameter: SourceRegion")

        source_fpga_image_id = params.get("SourceFpgaImageId")
        source_afi = self._get_afi_or_error(source_fpga_image_id)
        if is_error_response(source_afi):
            return source_afi

        fpga_image_id = self._generate_id("fpga")
        fpga_image_global_id = self._generate_id("agfi")
        now = datetime.now(timezone.utc).isoformat()

        resource = AFI(
            fpga_image_global_id=fpga_image_global_id,
            fpga_image_id=fpga_image_id,
            description=params.get("Description") or source_afi.description,
            name=params.get("Name") or source_afi.name,
            create_time=now,
            update_time=now,
            owner_id=source_afi.owner_id,
            owner_alias=source_afi.owner_alias,
            public=source_afi.public,
            state=ResourceState.AVAILABLE.value,
            data_retention_support=source_afi.data_retention_support,
            instance_types=list(source_afi.instance_types),
            pci_id=source_afi.pci_id,
            shell_version=source_afi.shell_version,
            tags=list(source_afi.tags),
            load_permissions=list(source_afi.load_permissions),
            product_codes=list(source_afi.product_codes),
        )
        self.resources[fpga_image_id] = resource

        return {
            'fpgaImageId': resource.fpga_image_id,
            }

    def CreateFpgaImage(self, params: Dict[str, Any]):
        """Creates an Amazon FPGA Image (AFI) from the specified design checkpoint (DCP). The create operation is asynchronous. To verify that the AFI was successfully 
         created and is ready for use, check the output logs. An AFI contains the FPGA bitstream that is ready to download to an FPGA. 
      """

        if not params.get("InputStorageLocation"):
            return create_error_response("MissingParameter", "Missing required parameter: InputStorageLocation")

        fpga_image_id = self._generate_id("fpga")
        fpga_image_global_id = self._generate_id("agfi")
        now = datetime.now(timezone.utc).isoformat()
        tags: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tags.extend(spec.get("Tags", []) or [])

        resource = AFI(
            fpga_image_global_id=fpga_image_global_id,
            fpga_image_id=fpga_image_id,
            description=params.get("Description") or "",
            name=params.get("Name") or "",
            create_time=now,
            update_time=now,
            state=ResourceState.AVAILABLE.value,
            tags=tags,
        )
        self.resources[fpga_image_id] = resource

        return {
            'fpgaImageGlobalId': resource.fpga_image_global_id,
            'fpgaImageId': resource.fpga_image_id,
            }

    def DeleteFpgaImage(self, params: Dict[str, Any]):
        """Deletes the specified Amazon FPGA Image (AFI)."""

        if not params.get("FpgaImageId"):
            return create_error_response("MissingParameter", "Missing required parameter: FpgaImageId")

        fpga_image_id = params.get("FpgaImageId")
        afi = self._get_afi_or_error(fpga_image_id)
        if is_error_response(afi):
            return afi

        del self.resources[fpga_image_id]

        return {
            'return': True,
            }

    def DescribeFpgaImageAttribute(self, params: Dict[str, Any]):
        """Describes the specified attribute of the specified Amazon FPGA Image (AFI)."""

        if not params.get("Attribute"):
            return create_error_response("MissingParameter", "Missing required parameter: Attribute")
        if not params.get("FpgaImageId"):
            return create_error_response("MissingParameter", "Missing required parameter: FpgaImageId")

        fpga_image_id = params.get("FpgaImageId")
        afi = self._get_afi_or_error(fpga_image_id)
        if is_error_response(afi):
            return afi

        return {
            'fpgaImageAttribute': self._build_fpga_image_attribute(afi),
            }

    def DescribeFpgaImages(self, params: Dict[str, Any]):
        """Describes the Amazon FPGA Images (AFIs) available to you. These include public AFIs,
			private AFIs that you own, and AFIs owned by other AWS accounts for which you have load
			permissions."""

        fpga_image_ids = params.get("FpgaImageId.N", []) or []
        owners = params.get("Owner.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if fpga_image_ids:
            resources = []
            for fpga_image_id in fpga_image_ids:
                afi = self.resources.get(fpga_image_id)
                if not afi:
                    return create_error_response(
                        "InvalidFpgaImageID.NotFound",
                        f"The ID '{fpga_image_id}' does not exist",
                    )
                resources.append(afi)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        if owners:
            resources = [
                afi for afi in resources
                if afi.owner_id in owners or afi.owner_alias in owners
            ]

        fpga_images = [afi.to_dict() for afi in resources[:max_results]]

        return {
            'fpgaImageSet': fpga_images,
            'nextToken': None,
            }

    def ModifyFpgaImageAttribute(self, params: Dict[str, Any]):
        """Modifies the specified attribute of the specified Amazon FPGA Image (AFI)."""

        if not params.get("FpgaImageId"):
            return create_error_response("MissingParameter", "Missing required parameter: FpgaImageId")

        fpga_image_id = params.get("FpgaImageId")
        afi = self._get_afi_or_error(fpga_image_id)
        if is_error_response(afi):
            return afi

        if params.get("Description") is not None:
            afi.description = params.get("Description") or ""
        if params.get("Name") is not None:
            afi.name = params.get("Name") or ""

        operation = (params.get("OperationType") or "add").lower()
        user_ids = params.get("UserId.N", []) or []
        user_groups = params.get("UserGroup.N", []) or []
        if user_ids or user_groups or params.get("LoadPermission"):
            additions = []
            for user_id in user_ids:
                additions.append({"userId": user_id})
            for group in user_groups:
                additions.append({"group": group})

            if operation == "remove":
                afi.load_permissions = [
                    entry for entry in afi.load_permissions
                    if entry not in additions
                ]
            else:
                for entry in additions:
                    if entry not in afi.load_permissions:
                        afi.load_permissions.append(entry)

        product_codes = params.get("ProductCode.N", []) or []
        if product_codes:
            if operation == "remove":
                afi.product_codes = [
                    code for code in afi.product_codes
                    if code.get("productCode") not in product_codes
                ]
            else:
                for code in product_codes:
                    entry = {"productCode": code, "type": "marketplace"}
                    if entry not in afi.product_codes:
                        afi.product_codes.append(entry)

        afi.update_time = datetime.now(timezone.utc).isoformat()

        return {
            'fpgaImageAttribute': self._build_fpga_image_attribute(afi),
            }

    def ResetFpgaImageAttribute(self, params: Dict[str, Any]):
        """Resets the specified attribute of the specified Amazon FPGA Image (AFI) to its default value.
		    You can only reset the load permission attribute."""

        if not params.get("FpgaImageId"):
            return create_error_response("MissingParameter", "Missing required parameter: FpgaImageId")

        fpga_image_id = params.get("FpgaImageId")
        afi = self._get_afi_or_error(fpga_image_id)
        if is_error_response(afi):
            return afi

        attribute = params.get("Attribute")
        if attribute and attribute != "loadPermission":
            return create_error_response(
                "InvalidParameterValue",
                "Only the loadPermission attribute can be reset",
            )

        afi.load_permissions = []
        afi.update_time = datetime.now(timezone.utc).isoformat()

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'fpga') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class afi_RequestParser:
    @staticmethod
    def parse_copy_fpga_image_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Name": get_scalar(md, "Name"),
            "SourceFpgaImageId": get_scalar(md, "SourceFpgaImageId"),
            "SourceRegion": get_scalar(md, "SourceRegion"),
        }

    @staticmethod
    def parse_create_fpga_image_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InputStorageLocation": get_scalar(md, "InputStorageLocation"),
            "LogsStorageLocation": get_scalar(md, "LogsStorageLocation"),
            "Name": get_scalar(md, "Name"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_fpga_image_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FpgaImageId": get_scalar(md, "FpgaImageId"),
        }

    @staticmethod
    def parse_describe_fpga_image_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Attribute": get_scalar(md, "Attribute"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FpgaImageId": get_scalar(md, "FpgaImageId"),
        }

    @staticmethod
    def parse_describe_fpga_images_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "FpgaImageId.N": get_indexed_list(md, "FpgaImageId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "Owner.N": get_indexed_list(md, "Owner"),
        }

    @staticmethod
    def parse_modify_fpga_image_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Attribute": get_scalar(md, "Attribute"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FpgaImageId": get_scalar(md, "FpgaImageId"),
            "LoadPermission": get_scalar(md, "LoadPermission"),
            "Name": get_scalar(md, "Name"),
            "OperationType": get_scalar(md, "OperationType"),
            "ProductCode.N": get_indexed_list(md, "ProductCode"),
            "UserGroup.N": get_indexed_list(md, "UserGroup"),
            "UserId.N": get_indexed_list(md, "UserId"),
        }

    @staticmethod
    def parse_reset_fpga_image_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Attribute": get_scalar(md, "Attribute"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FpgaImageId": get_scalar(md, "FpgaImageId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CopyFpgaImage": afi_RequestParser.parse_copy_fpga_image_request,
            "CreateFpgaImage": afi_RequestParser.parse_create_fpga_image_request,
            "DeleteFpgaImage": afi_RequestParser.parse_delete_fpga_image_request,
            "DescribeFpgaImageAttribute": afi_RequestParser.parse_describe_fpga_image_attribute_request,
            "DescribeFpgaImages": afi_RequestParser.parse_describe_fpga_images_request,
            "ModifyFpgaImageAttribute": afi_RequestParser.parse_modify_fpga_image_attribute_request,
            "ResetFpgaImageAttribute": afi_RequestParser.parse_reset_fpga_image_attribute_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class afi_ResponseSerializer:
    @staticmethod
    def _serialize_dict_to_xml(d: Dict[str, Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a dictionary to XML elements."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(afi_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(afi_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def _serialize_list_to_xml(lst: List[Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a list to XML elements with <tagName> wrapper and <item> children."""
        xml_parts = []
        indent = '    ' * indent_level
        xml_parts.append(f'{indent}<{tag_name}>')
        for item in lst:
            if isinstance(item, dict):
                xml_parts.append(f'{indent}    <item>')
                xml_parts.extend(afi_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(afi_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
            else:
                xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
        xml_parts.append(f'{indent}</{tag_name}>')
        return xml_parts

    @staticmethod
    def _serialize_nested_fields(d: Dict[str, Any], indent_level: int) -> List[str]:
        """Serialize nested fields from a dictionary."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(afi_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(afi_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
                        xml_parts.append(f'{indent}    </item>')
                    else:
                        xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def serialize_copy_fpga_image_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CopyFpgaImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fpgaImageId
        _fpgaImageId_key = None
        if "fpgaImageId" in data:
            _fpgaImageId_key = "fpgaImageId"
        elif "FpgaImageId" in data:
            _fpgaImageId_key = "FpgaImageId"
        if _fpgaImageId_key:
            param_data = data[_fpgaImageId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fpgaImageId>{esc(str(param_data))}</fpgaImageId>')
        xml_parts.append(f'</CopyFpgaImageResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_fpga_image_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateFpgaImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fpgaImageGlobalId
        _fpgaImageGlobalId_key = None
        if "fpgaImageGlobalId" in data:
            _fpgaImageGlobalId_key = "fpgaImageGlobalId"
        elif "FpgaImageGlobalId" in data:
            _fpgaImageGlobalId_key = "FpgaImageGlobalId"
        if _fpgaImageGlobalId_key:
            param_data = data[_fpgaImageGlobalId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fpgaImageGlobalId>{esc(str(param_data))}</fpgaImageGlobalId>')
        # Serialize fpgaImageId
        _fpgaImageId_key = None
        if "fpgaImageId" in data:
            _fpgaImageId_key = "fpgaImageId"
        elif "FpgaImageId" in data:
            _fpgaImageId_key = "FpgaImageId"
        if _fpgaImageId_key:
            param_data = data[_fpgaImageId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fpgaImageId>{esc(str(param_data))}</fpgaImageId>')
        xml_parts.append(f'</CreateFpgaImageResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_fpga_image_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteFpgaImageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</DeleteFpgaImageResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_fpga_image_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeFpgaImageAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fpgaImageAttribute
        _fpgaImageAttribute_key = None
        if "fpgaImageAttribute" in data:
            _fpgaImageAttribute_key = "fpgaImageAttribute"
        elif "FpgaImageAttribute" in data:
            _fpgaImageAttribute_key = "FpgaImageAttribute"
        if _fpgaImageAttribute_key:
            param_data = data[_fpgaImageAttribute_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fpgaImageAttribute>')
            xml_parts.extend(afi_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</fpgaImageAttribute>')
        xml_parts.append(f'</DescribeFpgaImageAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_fpga_images_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeFpgaImagesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fpgaImageSet
        _fpgaImageSet_key = None
        if "fpgaImageSet" in data:
            _fpgaImageSet_key = "fpgaImageSet"
        elif "FpgaImageSet" in data:
            _fpgaImageSet_key = "FpgaImageSet"
        elif "FpgaImages" in data:
            _fpgaImageSet_key = "FpgaImages"
        if _fpgaImageSet_key:
            param_data = data[_fpgaImageSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<fpgaImageSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(afi_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</fpgaImageSet>')
            else:
                xml_parts.append(f'{indent_str}<fpgaImageSet/>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        xml_parts.append(f'</DescribeFpgaImagesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_fpga_image_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyFpgaImageAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fpgaImageAttribute
        _fpgaImageAttribute_key = None
        if "fpgaImageAttribute" in data:
            _fpgaImageAttribute_key = "fpgaImageAttribute"
        elif "FpgaImageAttribute" in data:
            _fpgaImageAttribute_key = "FpgaImageAttribute"
        if _fpgaImageAttribute_key:
            param_data = data[_fpgaImageAttribute_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fpgaImageAttribute>')
            xml_parts.extend(afi_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</fpgaImageAttribute>')
        xml_parts.append(f'</ModifyFpgaImageAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reset_fpga_image_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ResetFpgaImageAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</ResetFpgaImageAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CopyFpgaImage": afi_ResponseSerializer.serialize_copy_fpga_image_response,
            "CreateFpgaImage": afi_ResponseSerializer.serialize_create_fpga_image_response,
            "DeleteFpgaImage": afi_ResponseSerializer.serialize_delete_fpga_image_response,
            "DescribeFpgaImageAttribute": afi_ResponseSerializer.serialize_describe_fpga_image_attribute_response,
            "DescribeFpgaImages": afi_ResponseSerializer.serialize_describe_fpga_images_response,
            "ModifyFpgaImageAttribute": afi_ResponseSerializer.serialize_modify_fpga_image_attribute_response,
            "ResetFpgaImageAttribute": afi_ResponseSerializer.serialize_reset_fpga_image_attribute_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

