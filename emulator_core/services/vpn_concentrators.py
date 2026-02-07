from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class VpnConcentratorState(Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


@dataclass
class Tag:
    Key: str
    Value: str

    def __post_init__(self):
        # Validate Key constraints
        if not isinstance(self.Key, str):
            raise ErrorCode("InvalidParameterValue", "Tag Key must be a string")
        if len(self.Key) > 127:
            raise ErrorCode("InvalidParameterValue", "Tag Key length must be <= 127")
        if self.Key.lower().startswith("aws:"):
            raise ErrorCode("InvalidParameterValue", "Tag Key may not begin with aws:")
        # Validate Value constraints
        if not isinstance(self.Value, str):
            raise ErrorCode("InvalidParameterValue", "Tag Value must be a string")
        if len(self.Value) > 256:
            raise ErrorCode("InvalidParameterValue", "Tag Value length must be <= 256")

    def to_dict(self) -> Dict[str, str]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: str
    Tags: List[Tag] = field(default_factory=list)

    def __post_init__(self):
        # Validate ResourceType is string and allowed values
        if not isinstance(self.ResourceType, str):
            raise ErrorCode("InvalidParameterValue", "ResourceType must be a string")
        # Allowed resource types are many, but we only accept "vpn-concentrator" here
        if self.ResourceType != "vpn-concentrator":
            raise ErrorCode(
                "InvalidParameterValue",
                f"Invalid ResourceType '{self.ResourceType}' for TagSpecification. Must be 'vpn-concentrator'",
            )
        # Tags already validated in Tag class

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class VpnConcentrator:
    vpn_concentrator_id: str
    state: VpnConcentratorState = VpnConcentratorState.PENDING
    transit_gateway_id: Optional[str] = None
    transit_gateway_attachment_id: Optional[str] = None
    type: str = "ipsec.1"
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tag_set = [{"Key": k, "Value": v} for k, v in self.tags.items()]
        return {
            "vpnConcentratorId": self.vpn_concentrator_id,
            "state": self.state.value,
            "transitGatewayId": self.transit_gateway_id,
            "transitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "type": self.type,
            "tagSet": tag_set,
        }


class VpnConcentratorBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.vpn_concentrators dict for storage

    def _validate_tags(self, tag_specifications: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Validate and parse TagSpecification.N parameters.
        Returns a dict of tags {Key: Value}.
        """
        tags: Dict[str, str] = {}
        if not isinstance(tag_specifications, list):
            raise ErrorCode("InvalidParameterValue", "TagSpecification must be a list")

        for tag_spec in tag_specifications:
            if not isinstance(tag_spec, dict):
                raise ErrorCode("InvalidParameterValue", "Each TagSpecification must be a dict")
            resource_type = tag_spec.get("ResourceType")
            if resource_type != "vpn-concentrator":
                raise ErrorCode(
                    "InvalidParameterValue",
                    f"TagSpecification ResourceType must be 'vpn-concentrator', got '{resource_type}'",
                )
            tag_list = tag_spec.get("Tags", [])
            if not isinstance(tag_list, list):
                raise ErrorCode("InvalidParameterValue", "Tags must be a list")
            for tag in tag_list:
                if not isinstance(tag, dict):
                    raise ErrorCode("InvalidParameterValue", "Each Tag must be a dict")
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None or not isinstance(key, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Key must be a non-empty string")
                if key.lower().startswith("aws:"):
                    raise ErrorCode("InvalidParameterValue", "Tag Key may not begin with aws:")
                if len(key) > 127:
                    raise ErrorCode("InvalidParameterValue", "Tag Key length must be <= 127")
                if value is None:
                    value = ""
                if not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Value must be a string")
                if len(value) > 256:
                    raise ErrorCode("InvalidParameterValue", "Tag Value length must be <= 256")
                # AWS allows duplicate keys? Usually no, so overwrite
                tags[key] = value
        return tags

    def _validate_transit_gateway_id(self, transit_gateway_id: Optional[str]) -> Optional[str]:
        """
        Validate TransitGatewayId if provided.
        If provided, must exist in state.
        """
        if transit_gateway_id is None:
            return None
        if not isinstance(transit_gateway_id, str):
            raise ErrorCode("InvalidParameterValue", "TransitGatewayId must be a string")
        # Validate existence of transit gateway resource
        transit_gateway = self.state.get_resource(transit_gateway_id)
        if transit_gateway is None:
            raise ErrorCode("InvalidTransitGatewayID.NotFound", f"TransitGatewayId {transit_gateway_id} does not exist")
        # We do not simulate transit gateway attachments creation here, but we generate an attachment id
        return transit_gateway_id

    def create_vpn_concentrator(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Validate Type param (required)
        vpn_type = params.get("Type")
        if vpn_type is None:
            raise ErrorCode("MissingParameter", "Type is required")
        if not isinstance(vpn_type, str):
            raise ErrorCode("InvalidParameterValue", "Type must be a string")
        if vpn_type != "ipsec.1":
            raise ErrorCode("InvalidParameterValue", "Type must be 'ipsec.1'")

        # Validate TransitGatewayId (optional)
        transit_gateway_id = params.get("TransitGatewayId")
        transit_gateway_id = self._validate_transit_gateway_id(transit_gateway_id)

        # Validate TagSpecification.N (optional)
        tag_specifications = params.get("TagSpecification.N", [])
        tags = self._validate_tags(tag_specifications) if tag_specifications else {}

        # DryRun check (simulate permission check)
        if dry_run:
            # We assume user has permission for this example
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Generate VPN Concentrator ID
        vpn_concentrator_id = f"vcn-{self.generate_unique_id()}"

        # Generate TransitGatewayAttachmentId if transit_gateway_id provided
        transit_gateway_attachment_id = None
        if transit_gateway_id:
            transit_gateway_attachment_id = f"tgw-attach-{self.generate_unique_id()}"

        # Create VPN Concentrator object
        vpn_concentrator = VpnConcentrator(
            vpn_concentrator_id=vpn_concentrator_id,
            state=VpnConcentratorState.PENDING,
            transit_gateway_id=transit_gateway_id,
            transit_gateway_attachment_id=transit_gateway_attachment_id,
            type=vpn_type,
            tags=tags,
        )

        # Store in shared state dict
        self.state.vpn_concentrators[vpn_concentrator_id] = vpn_concentrator

        # Return response dict
        return {
            "requestId": self.generate_request_id(),
            "vpnConcentrator": vpn_concentrator.to_dict(),
        }

    def delete_vpn_concentrator(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Validate VpnConcentratorId param (required)
        vpn_concentrator_id = params.get("VpnConcentratorId")
        if vpn_concentrator_id is None:
            raise ErrorCode("MissingParameter", "VpnConcentratorId is required")
        if not isinstance(vpn_concentrator_id, str):
            raise ErrorCode("InvalidParameterValue", "VpnConcentratorId must be a string")

        # DryRun check
        if dry_run:
            # We assume user has permission
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Check existence
        vpn_concentrator = self.state.vpn_concentrators.get(vpn_concentrator_id)
        if vpn_concentrator is None:
            raise ErrorCode("InvalidVpnConcentratorID.NotFound", f"VpnConcentratorId {vpn_concentrator_id} does not exist")

        # Mark as deleting
        vpn_concentrator.state = VpnConcentratorState.DELETING

        # For simplicity, immediately mark as deleted and remove from state
        vpn_concentrator.state = VpnConcentratorState.DELETED
        del self.state.vpn_concentrators[vpn_concentrator_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_vpn_concentrators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Validate MaxResults if present
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 200 or max_results > 1000:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 200 and 1000")

        # Validate NextToken if present (for pagination)
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string")

        # Validate VpnConcentratorId.N (optional list of IDs)
        vpn_concentrator_ids = params.get("VpnConcentratorId.N", [])
        if vpn_concentrator_ids is not None and not isinstance(vpn_concentrator_ids, list):
            raise ErrorCode("InvalidParameterValue", "VpnConcentratorId.N must be a list of strings")
        if vpn_concentrator_ids:
            for vcn_id in vpn_concentrator_ids:
                if not isinstance(vcn_id, str):
                    raise ErrorCode("InvalidParameterValue", "Each VpnConcentratorId must be a string")

        # Validate Filter.N (optional)
        filters = params.get("Filter.N", [])
        if filters is not None and not isinstance(filters, list):
            raise ErrorCode("InvalidParameterValue", "Filter.N must be a list of filters")
        # Each filter is dict with Name and Values (list of strings)
        filter_map = {}
        if filters:
            for f in filters:
                if not isinstance(f, dict):
                    raise ErrorCode("InvalidParameterValue", "Each filter must be a dict")
                name = f.get("Name")
                values = f.get("Values")
                if not isinstance(name, str):
                    raise ErrorCode("InvalidParameterValue", "Filter Name must be a string")
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                    raise ErrorCode("InvalidParameterValue", "Filter Values must be a list of strings")
                filter_map[name] = values

        # DryRun check
        if dry_run:
            # Assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Collect vpn concentrators to return
        concentrators = list(self.state.vpn_concentrators.values())

        # Filter by VpnConcentratorId.N if provided
        if vpn_concentrator_ids:
            concentrators = [c for c in concentrators if c.vpn_concentrator_id in vpn_concentrator_ids]

        # Apply filters
        for filter_name, filter_values in filter_map.items():
            if filter_name == "state":
                # Filter by state string values
                filter_states = set(filter_values)
                concentrators = [c for c in concentrators if c.state.value in filter_states]
            elif filter_name == "transit-gateway-id":
                concentrators = [c for c in concentrators if c.transit_gateway_id in filter_values]
            elif filter_name == "type":
                concentrators = [c for c in concentrators if c.type in filter_values]
            else:
                # Unknown filter: ignore or raise? AWS usually ignores unknown filters
                pass

        # Pagination: simulate with NextToken as index string
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "NextToken is invalid")

        # Apply MaxResults with default 1000 (max)
        max_results = max_results or 1000
        end_index = start_index + max_results
        page = concentrators[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(concentrators):
            new_next_token = str(end_index)

        # Build response vpnConcentratorSet list
        vpn_concentrator_set = [c.to_dict() for c in page]

        return {
            "requestId": self.generate_request_id(),
            "vpnConcentratorSet": vpn_concentrator_set,
            "nextToken": new_next_token,
        }

from emulator_core.gateway.base import BaseGateway

class VPNConcentratorsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateVpnConcentrator", self.create_vpn_concentrator)
        self.register_action("DeleteVpnConcentrator", self.delete_vpn_concentrator)
        self.register_action("DescribeVpnConcentrators", self.describe_vpn_concentrators)

    def create_vpn_concentrator(self, params):
        return self.backend.create_vpn_concentrator(params)

    def delete_vpn_concentrator(self, params):
        return self.backend.delete_vpn_concentrator(params)

    def describe_vpn_concentrators(self, params):
        return self.backend.describe_vpn_concentrators(params)
