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
class RegionAndZone:
    group_long_name: str = ""
    group_name: str = ""
    message_set: List[Any] = field(default_factory=list)
    network_border_group: str = ""
    opt_in_status: str = ""
    parent_zone_id: str = ""
    parent_zone_name: str = ""
    region_name: str = ""
    zone_id: str = ""
    zone_name: str = ""
    zone_state: str = ""
    zone_type: str = ""

    region_endpoint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "groupLongName": self.group_long_name,
            "groupName": self.group_name,
            "messageSet": self.message_set,
            "networkBorderGroup": self.network_border_group,
            "optInStatus": self.opt_in_status,
            "parentZoneId": self.parent_zone_id,
            "parentZoneName": self.parent_zone_name,
            "regionName": self.region_name,
            "zoneId": self.zone_id,
            "zoneName": self.zone_name,
            "zoneState": self.zone_state,
            "zoneType": self.zone_type,
            "regionEndpoint": self.region_endpoint,
        }

class RegionAndZone_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.regions_and_zones  # alias to shared store


    def DescribeAvailabilityZones(self, params: Dict[str, Any]):
        """Describes the Availability Zones, Local Zones, and Wavelength Zones that are available to
      you. For more information about Availability Zones, Local Zones, and Wavelength Zones, seeRegions and zonesin theAmazon EC2 User Guide. The order of the elements in the response, including those within ne"""

        zone_ids = params.get("ZoneId.N", []) or []
        zone_names = params.get("ZoneName.N", []) or []
        filters = params.get("Filter.N", []) or []

        base_zones = [
            resource for resource in self.resources.values()
            if resource.zone_id or resource.zone_name or resource.zone_type
        ]

        if zone_ids:
            missing = [
                zone_id for zone_id in zone_ids
                if not any(resource.zone_id == zone_id for resource in base_zones)
            ]
            if missing:
                return create_error_response(
                    "InvalidZoneID.NotFound",
                    f"The ID '{missing[0]}' does not exist",
                )
            zones = [
                next(resource for resource in base_zones if resource.zone_id == zone_id)
                for zone_id in zone_ids
            ]
        else:
            zones = list(base_zones)

        if zone_names:
            missing = [
                zone_name for zone_name in zone_names
                if not any(resource.zone_name == zone_name for resource in base_zones)
            ]
            if missing:
                return create_error_response(
                    "InvalidZoneName.NotFound",
                    f"The zone '{missing[0]}' does not exist",
                )
            if zone_ids:
                zones = [resource for resource in zones if resource.zone_name in zone_names]
            else:
                zones = [
                    next(resource for resource in base_zones if resource.zone_name == zone_name)
                    for zone_name in zone_names
                ]

        if filters:
            zones = apply_filters(zones, filters)

        availability_zone_info = [
            {
                "groupLongName": zone.group_long_name,
                "groupName": zone.group_name,
                "messageSet": zone.message_set,
                "networkBorderGroup": zone.network_border_group,
                "optInStatus": zone.opt_in_status,
                "parentZoneId": zone.parent_zone_id,
                "parentZoneName": zone.parent_zone_name,
                "regionName": zone.region_name,
                "zoneId": zone.zone_id,
                "zoneName": zone.zone_name,
                "zoneState": zone.zone_state,
                "zoneType": zone.zone_type,
            }
            for zone in zones
        ]

        return {
            "availabilityZoneInfo": availability_zone_info,
        }

    def DescribeRegions(self, params: Dict[str, Any]):
        """Describes the Regions that are enabled for your account, or all Regions. For a list of the Regions supported by Amazon EC2, seeAmazon EC2 service endpoints. For information about enabling and disabling Regions for your account, seeSpecify which AWS Regions 
      your account can usein theAWS Accoun"""

        region_names = params.get("RegionName.N", []) or []
        filters = params.get("Filter.N", []) or []

        base_regions = [resource for resource in self.resources.values() if resource.region_name]

        if region_names:
            missing = [
                region_name for region_name in region_names
                if not any(resource.region_name == region_name for resource in base_regions)
            ]
            if missing:
                return create_error_response(
                    "InvalidRegionName.NotFound",
                    f"The region '{missing[0]}' does not exist",
                )
            regions = [
                next(resource for resource in base_regions if resource.region_name == region_name)
                for region_name in region_names
            ]
        else:
            regions = list(base_regions)

        if filters:
            regions = apply_filters(regions, filters)

        region_info = [
            {
                "optInStatus": region.opt_in_status,
                "regionEndpoint": region.region_endpoint,
                "regionName": region.region_name,
            }
            for region in regions
        ]

        return {
            "regionInfo": region_info,
        }

    def ModifyAvailabilityZoneGroup(self, params: Dict[str, Any]):
        """Changes the opt-in status of the specified zone group for your account. UseDescribeAvailabilityZonesto view the value forGroupName."""

        group_name = params.get("GroupName")
        opt_in_status = params.get("OptInStatus")

        if not group_name:
            return create_error_response(
                "MissingParameter",
                "The request must contain the parameter GroupName",
            )
        if not opt_in_status:
            return create_error_response(
                "MissingParameter",
                "The request must contain the parameter OptInStatus",
            )

        matching_resources = [
            resource for resource in self.resources.values()
            if resource.group_name == group_name
        ]
        if not matching_resources:
            return create_error_response(
                "InvalidGroup.NotFound",
                f"The group '{group_name}' does not exist",
            )

        for resource in matching_resources:
            resource.opt_in_status = opt_in_status

        return {
            "return": True,
        }

    def _generate_id(self, prefix: str = 'parent') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class regionandzone_RequestParser:
    @staticmethod
    def parse_describe_availability_zones_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllAvailabilityZones": get_scalar(md, "AllAvailabilityZones"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "ZoneId.N": get_indexed_list(md, "ZoneId"),
            "ZoneName.N": get_indexed_list(md, "ZoneName"),
        }

    @staticmethod
    def parse_describe_regions_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllRegions": get_scalar(md, "AllRegions"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "RegionName.N": get_indexed_list(md, "RegionName"),
        }

    @staticmethod
    def parse_modify_availability_zone_group_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GroupName": get_scalar(md, "GroupName"),
            "OptInStatus": get_scalar(md, "OptInStatus"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeAvailabilityZones": regionandzone_RequestParser.parse_describe_availability_zones_request,
            "DescribeRegions": regionandzone_RequestParser.parse_describe_regions_request,
            "ModifyAvailabilityZoneGroup": regionandzone_RequestParser.parse_modify_availability_zone_group_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class regionandzone_ResponseSerializer:
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
                xml_parts.extend(regionandzone_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(regionandzone_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(regionandzone_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(regionandzone_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(regionandzone_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(regionandzone_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_availability_zones_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeAvailabilityZonesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize availabilityZoneInfo
        _availabilityZoneInfo_key = None
        if "availabilityZoneInfo" in data:
            _availabilityZoneInfo_key = "availabilityZoneInfo"
        elif "AvailabilityZoneInfo" in data:
            _availabilityZoneInfo_key = "AvailabilityZoneInfo"
        if _availabilityZoneInfo_key:
            param_data = data[_availabilityZoneInfo_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<availabilityZoneInfoSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(regionandzone_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</availabilityZoneInfoSet>')
            else:
                xml_parts.append(f'{indent_str}<availabilityZoneInfoSet/>')
        xml_parts.append(f'</DescribeAvailabilityZonesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_regions_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeRegionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize regionInfo
        _regionInfo_key = None
        if "regionInfo" in data:
            _regionInfo_key = "regionInfo"
        elif "RegionInfo" in data:
            _regionInfo_key = "RegionInfo"
        if _regionInfo_key:
            param_data = data[_regionInfo_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<regionInfoSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(regionandzone_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</regionInfoSet>')
            else:
                xml_parts.append(f'{indent_str}<regionInfoSet/>')
        xml_parts.append(f'</DescribeRegionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_availability_zone_group_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyAvailabilityZoneGroupResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyAvailabilityZoneGroupResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeAvailabilityZones": regionandzone_ResponseSerializer.serialize_describe_availability_zones_response,
            "DescribeRegions": regionandzone_ResponseSerializer.serialize_describe_regions_response,
            "ModifyAvailabilityZoneGroup": regionandzone_ResponseSerializer.serialize_modify_availability_zone_group_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

