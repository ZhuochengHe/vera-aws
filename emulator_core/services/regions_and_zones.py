from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class OptInStatus(Enum):
    OPT_IN_NOT_REQUIRED = "opt-in-not-required"
    OPTED_IN = "opted-in"
    NOT_OPTED_IN = "not-opted-in"


class ZoneState(Enum):
    AVAILABLE = "available"
    INFORMATION = "information"
    IMPAIRED = "impaired"
    UNAVAILABLE = "unavailable"
    CONSTRAINED = "constrained"


class ZoneType(Enum):
    AVAILABILITY_ZONE = "availability-zone"
    LOCAL_ZONE = "local-zone"
    WAVELENGTH_ZONE = "wavelength-zone"


@dataclass
class AvailabilityZoneMessage:
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"message": self.message} if self.message is not None else {}


@dataclass
class AvailabilityZone:
    group_long_name: Optional[str] = None
    group_name: Optional[str] = None
    message_set: List[AvailabilityZoneMessage] = field(default_factory=list)
    network_border_group: Optional[str] = None
    opt_in_status: Optional[OptInStatus] = None
    parent_zone_id: Optional[str] = None
    parent_zone_name: Optional[str] = None
    region_name: Optional[str] = None
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    zone_state: Optional[ZoneState] = None
    zone_type: Optional[ZoneType] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.group_long_name is not None:
            d["GroupLongName"] = self.group_long_name
        if self.group_name is not None:
            d["groupName"] = self.group_name
        d["messageSet"] = [msg.to_dict() for msg in self.message_set] if self.message_set else []
        if self.network_border_group is not None:
            d["NetworkBorderGroup"] = self.network_border_group
        if self.opt_in_status is not None:
            d["optInStatus"] = self.opt_in_status.value
        if self.parent_zone_id is not None:
            d["parentZoneId"] = self.parent_zone_id
        if self.parent_zone_name is not None:
            d["parentZoneName"] = self.parent_zone_name
        if self.region_name is not None:
            d["regionName"] = self.region_name
        if self.zone_id is not None:
            d["zoneId"] = self.zone_id
        if self.zone_name is not None:
            d["zoneName"] = self.zone_name
        if self.zone_state is not None:
            d["zoneState"] = self.zone_state.value
        if self.zone_type is not None:
            d["zoneType"] = self.zone_type.value
        return d


@dataclass
class Region:
    region_name: str
    region_endpoint: str
    opt_in_status: Optional[OptInStatus] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "regionName": self.region_name,
            "regionEndpoint": self.region_endpoint,
        }
        if self.opt_in_status is not None:
            d["optInStatus"] = self.opt_in_status.value
        return d


class RegionsAndZonesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage, use self.state.regions_and_zones dict

    def _parse_filters(self, filters: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Parses filters from the request parameters into a dict of filter_name -> list of values.
        """
        parsed_filters = {}
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not isinstance(name, str):
                raise ErrorCode("InvalidFilterName", f"Filter name must be a string, got {type(name)}")
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                raise ErrorCode("InvalidFilterValue", f"Filter values must be list of strings for filter {name}")
            parsed_filters[name] = values
        return parsed_filters

    def _filter_availability_zones(
        self,
        azs: List[AvailabilityZone],
        filters: Dict[str, List[str]],
        zone_ids: Optional[List[str]],
        zone_names: Optional[List[str]],
        all_availability_zones: bool,
        owner_id: str,
    ) -> List[AvailabilityZone]:
        """
        Filters the availability zones based on filters, zone_ids, zone_names, and opt-in status.
        If all_availability_zones is False, only zones for regions where the owner has opted in are included.
        """
        filtered = []

        # Helper to check if zone matches filters
        def matches_filters(az: AvailabilityZone) -> bool:
            for fname, fvalues in filters.items():
                # Map filter names to AvailabilityZone attributes or special logic
                # Valid filter names from spec:
                # group-long-name, group-name, message, opt-in-status, parent-zone-id, parent-zone-name,
                # region-name, state, zone-id, zone-name, zone-type
                # Note: message filter matches any message in messageSet
                if fname == "group-long-name":
                    if az.group_long_name is None or not any(v == az.group_long_name for v in fvalues):
                        return False
                elif fname == "group-name":
                    if az.group_name is None or not any(v == az.group_name for v in fvalues):
                        return False
                elif fname == "message":
                    # If no messages and filter values exist, no match
                    if not az.message_set and fvalues:
                        return False
                    # Check if any message matches any filter value
                    if not any(
                        msg.message is not None and any(v == msg.message for v in fvalues)
                        for msg in az.message_set
                    ):
                        return False
                elif fname == "opt-in-status":
                    if az.opt_in_status is None or not any(v == az.opt_in_status.value for v in fvalues):
                        return False
                elif fname == "parent-zone-id":
                    if az.parent_zone_id is None or not any(v == az.parent_zone_id for v in fvalues):
                        return False
                elif fname == "parent-zone-name":
                    if az.parent_zone_name is None or not any(v == az.parent_zone_name for v in fvalues):
                        return False
                elif fname == "region-name":
                    if az.region_name is None or not any(v == az.region_name for v in fvalues):
                        return False
                elif fname == "state":
                    if az.zone_state is None or not any(v == az.zone_state.value for v in fvalues):
                        return False
                elif fname == "zone-id":
                    if az.zone_id is None or not any(v == az.zone_id for v in fvalues):
                        return False
                elif fname == "zone-name":
                    if az.zone_name is None or not any(v == az.zone_name for v in fvalues):
                        return False
                elif fname == "zone-type":
                    if az.zone_type is None or not any(v == az.zone_type.value for v in fvalues):
                        return False
                else:
                    # Unknown filter name
                    raise ErrorCode("InvalidFilter", f"Unknown filter name: {fname}")
            return True

        # If all_availability_zones is False, filter zones by opt-in status of their region for this owner
        # We assume self.state.regions_and_zones stores all zones keyed by zone_id or zone_name
        # We also assume regions are keyed by region_name in self.state.regions_and_zones_regions
        # But since only self.state.regions_and_zones is given, we must find region info from zones or state

        # For this implementation, we assume self.state.regions_and_zones contains all zones keyed by zone_id or zone_name
        # and each zone has region_name attribute.

        # We will include zones only if:
        # - all_availability_zones is True, or
        # - the region of the zone has opt_in_status == OPTED_IN or OPT_IN_NOT_REQUIRED for this owner

        # We do not have per-owner opt-in status for regions in the spec, so we assume all zones are visible if all_availability_zones is True
        # Otherwise, only zones with opt_in_status OPTED_IN or OPT_IN_NOT_REQUIRED are included.

        for az in azs:
            # Filter by zone_ids if provided
            if zone_ids is not None and az.zone_id not in zone_ids:
                continue
            # Filter by zone_names if provided
            if zone_names is not None and az.zone_name not in zone_names:
                continue
            # Filter by opt-in status if all_availability_zones is False
            if not all_availability_zones:
                # For availability zones, opt-in status is always opt-in-not-required
                # For local and wavelength zones, opt-in status can be opted-in or not-opted-in
                if az.opt_in_status not in (OptInStatus.OPTED_IN, OptInStatus.OPT_IN_NOT_REQUIRED):
                    continue
            # Filter by filters
            if not matches_filters(az):
                continue
            filtered.append(az)
        return filtered

    def describe_availability_zones(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate parameters
        # Allowed params: AllAvailabilityZones (bool), DryRun (bool), Filter.N (list of filters), ZoneId.N (list of strings), ZoneName.N (list of strings)
        # Extract and validate
        all_availability_zones = params.get("AllAvailabilityZones", False)
        if not isinstance(all_availability_zones, bool):
            raise ErrorCode("InvalidParameterValue", "AllAvailabilityZones must be a boolean")

        dry_run = params.get("DryRun", False)
        if not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Filters: keys like Filter.1, Filter.2, ... or Filter.N as list of dicts
        # We expect Filter.N as list of dicts with Name and Values
        filters_raw = []
        # Collect filters from params keys starting with "Filter."
        # The input param keys might be "Filter.1.Name", "Filter.1.Values", etc.
        # We need to parse them into list of dicts with keys "Name" and "Values"
        # We'll parse keys like Filter.N.Name and Filter.N.Values
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                # key format: Filter.N.Name or Filter.N.Values
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                _, index_str, field = parts[0], parts[1], parts[2]
                if not index_str.isdigit():
                    continue
                idx = int(index_str)
                if idx not in filter_dict:
                    filter_dict[idx] = {}
                filter_dict[idx][field] = value
        # Now convert filter_dict to list
        for idx in sorted(filter_dict.keys()):
            f = filter_dict[idx]
            # Validate filter structure
            if "Name" not in f:
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx} missing Name")
            # Values can be string or list of strings
            values = f.get("Values", [])
            if isinstance(values, str):
                values = [values]
            elif not isinstance(values, list):
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx} Values must be string or list of strings")
            # Validate all values are strings
            if not all(isinstance(v, str) for v in values):
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx} Values must be strings")
            filters_raw.append({"Name": f["Name"], "Values": values})

        filters = self._parse_filters(filters_raw)

        # ZoneId.N and ZoneName.N are lists of strings, keys like ZoneId.1, ZoneId.2, ...
        zone_ids = []
        zone_names = []
        for key, value in params.items():
            if key.startswith("ZoneId."):
                if not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                zone_ids.append(value)
            elif key.startswith("ZoneName."):
                if not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                zone_names.append(value)
        if zone_ids == []:
            zone_ids = None
        if zone_names == []:
            zone_names = None

        # DryRun check
        if dry_run:
            # We simulate permission check, always allow for this emulator
            raise ErrorCode("DryRunOperation", "Request would have succeeded, DryRun flag is set")

        # Collect all availability zones from state
        # self.state.regions_and_zones is a dict keyed by zone_id or zone_name? We assume zone_id keys
        all_zones = list(self.state.regions_and_zones.values())

        # Filter zones
        filtered_zones = self._filter_availability_zones(
            all_zones, filters, zone_ids, zone_names, all_availability_zones, self.get_owner_id()
        )

        # Compose response
        availability_zone_info = [az.to_dict() for az in filtered_zones]

        return {
            "availabilityZoneInfo": availability_zone_info,
            "requestId": self.generate_request_id(),
        }

    def describe_regions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate parameters
        # Allowed params: AllRegions (bool), DryRun (bool), Filter.N (list of filters), RegionName.N (list of strings)
        all_regions = params.get("AllRegions", False)
        if isinstance(all_regions, str):
            all_regions = all_regions.lower() == "true"
        elif not isinstance(all_regions, bool):
            all_regions = False

        dry_run = params.get("DryRun", False)
        if isinstance(dry_run, str):
            dry_run = dry_run.lower() == "true"
        elif not isinstance(dry_run, bool):
            dry_run = False

        # Parse filters similarly to describe_availability_zones
        filters_raw = []
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                _, index_str, field = parts[0], parts[1], parts[2]
                if not index_str.isdigit():
                    continue
                idx = int(index_str)
                if idx not in filter_dict:
                    filter_dict[idx] = {}
                filter_dict[idx][field] = value
        for idx in sorted(filter_dict.keys()):
            f = filter_dict[idx]
            if "Name" not in f:
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx} missing Name")
            values = f.get("Values", [])
            if isinstance(values, str):
                values = [values]
            elif not isinstance(values, list):
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx} Values must be string or list of strings")
            if not all(isinstance(v, str) for v in values):
                raise ErrorCode("InvalidParameterValue", f"Filter.{idx} Values must be strings")
            filters_raw.append({"Name": f["Name"], "Values": values})

        filters = self._parse_filters(filters_raw)

        # RegionName.N keys
        region_names = []
        for key, value in params.items():
            if key.startswith("RegionName."):
                if not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                region_names.append(value)
        if region_names == []:
            region_names = None

        if dry_run:
            raise ErrorCode("DryRunOperation", "Request would have succeeded, DryRun flag is set")

        # Collect all regions from state
        # We assume self.state.regions_and_zones contains regions as well? The spec only mentions self.state.regions_and_zones
        # We will assume self.state.regions_and_zones contains both zones and regions keyed by their IDs or names
        # But we need to separate regions from zones
        # For this implementation, we assume self.state.regions_and_zones contains only zones
        # So we must have a separate dict for regions in state: self.state.regions
        # But spec says only self.state.regions_and_zones
        # So we must store regions in self.state.regions_and_zones keyed by region_name with a special attribute or type
        # To keep consistent, let's assume self.state.regions_and_zones contains both zones and regions keyed by their IDs or names
        # We will filter by presence of region_name attribute and no zone_id attribute to identify regions

        # So we filter self.state.regions_and_zones values for Region objects (have region_name and region_endpoint, no zone_id)
        all_regions_list = []
        for res in self.state.regions_and_zones.values():
            # Identify Region by presence of region_name and region_endpoint and absence of zone_id
            if isinstance(res, Region):
                all_regions_list.append(res)

        # Filter regions by region_names if provided
        filtered_regions = []
        for region in all_regions_list:
            if region_names is not None and region.region_name not in region_names:
                continue
            # Filter by filters
            # Valid filter names: endpoint, opt-in-status, region-name
            # Map filter names to region attributes
            def matches_filters(region: Region) -> bool:
                for fname, fvalues in filters.items():
                    if fname == "endpoint":
                        if not any(region.region_endpoint == v for v in fvalues):
                            return False
                    elif fname == "opt-in-status":
                        if region.opt_in_status is None or not any(region.opt_in_status.value == v for v in fvalues):
                            return False
                    elif fname == "region-name":
                        if not any(region.region_name == v for v in fvalues):
                            return False
                    else:
                        raise ErrorCode("InvalidFilter", f"Unknown filter name: {fname}")
                return True

            if not matches_filters(region):
                continue
            # If all_regions is False, only include regions enabled for the account
            # We assume opt_in_status OPTED_IN or OPT_IN_NOT_REQUIRED means enabled
            if not all_regions:
                if region.opt_in_status not in (OptInStatus.OPTED_IN, OptInStatus.OPT_IN_NOT_REQUIRED):
                    continue
            filtered_regions.append(region)

        region_info = [region.to_dict() for region in filtered_regions]

        return {
            "regionInfo": region_info,
            "requestId": self.generate_request_id(),
        }

    def modify_availability_zone_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate parameters
        # Required: GroupName (str
        return {}

from emulator_core.gateway.base import BaseGateway

class RegionsandZonesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeAvailabilityZones", self.describe_availability_zones)
        self.register_action("DescribeRegions", self.describe_regions)
        self.register_action("ModifyAvailabilityZoneGroup", self.modify_availability_zone_group)

    def describe_availability_zones(self, params):
        return self.backend.describe_availability_zones(params)

    def describe_regions(self, params):
        return self.backend.describe_regions(params)

    def modify_availability_zone_group(self, params):
        return self.backend.modify_availability_zone_group(params)
