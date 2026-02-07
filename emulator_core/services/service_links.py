from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class ServiceLinkVirtualInterfaceState(Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


@dataclass
class Tag:
    Key: str
    Value: str


@dataclass
class ServiceLinkVirtualInterface:
    service_link_virtual_interface_id: str
    configuration_state: ServiceLinkVirtualInterfaceState = ServiceLinkVirtualInterfaceState.PENDING
    local_address: Optional[str] = None
    outpost_arn: Optional[str] = None
    outpost_id: Optional[str] = None
    outpost_lag_id: Optional[str] = None
    owner_id: Optional[str] = None
    peer_address: Optional[str] = None
    peer_bgp_asn: Optional[int] = None
    service_link_virtual_interface_arn: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    vlan: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "configurationState": self.configuration_state.value,
            "localAddress": self.local_address,
            "outpostArn": self.outpost_arn,
            "outpostId": self.outpost_id,
            "outpostLagId": self.outpost_lag_id,
            "ownerId": self.owner_id,
            "peerAddress": self.peer_address,
            "peerBgpAsn": self.peer_bgp_asn,
            "serviceLinkVirtualInterfaceArn": self.service_link_virtual_interface_arn,
            "serviceLinkVirtualInterfaceId": self.service_link_virtual_interface_id,
            "tagSet": [{"Key": tag.Key, "Value": tag.Value} for tag in self.tag_set],
            "vlan": self.vlan,
        }


class ServiceLinksBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.service_links dict for storage

    def describe_service_link_virtual_interfaces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun parameter
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if specified")

        # Validate MaxResults parameter
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 1000")

        # Validate NextToken parameter
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string if specified")

        # Validate ServiceLinkVirtualInterfaceId.N parameter
        service_link_virtual_interface_ids = params.get("ServiceLinkVirtualInterfaceId.N")
        if service_link_virtual_interface_ids is not None:
            if not isinstance(service_link_virtual_interface_ids, list):
                raise ErrorCode("InvalidParameterValue", "ServiceLinkVirtualInterfaceId.N must be a list of strings")
            for id_ in service_link_virtual_interface_ids:
                if not isinstance(id_, str):
                    raise ErrorCode("InvalidParameterValue", "Each ServiceLinkVirtualInterfaceId must be a string")

        # Validate Filters parameter
        filters = params.get("Filter.N")
        if filters is not None:
            if not isinstance(filters, list):
                raise ErrorCode("InvalidParameterValue", "Filter.N must be a list of filter objects")
            for f in filters:
                if not isinstance(f, dict):
                    raise ErrorCode("InvalidParameterValue", "Each filter must be a dictionary")
                if "Name" not in f or not isinstance(f["Name"], str):
                    raise ErrorCode("InvalidParameterValue", "Filter Name must be a string")
                if "Values" not in f or not isinstance(f["Values"], list):
                    raise ErrorCode("InvalidParameterValue", "Filter Values must be a list of strings")
                for v in f["Values"]:
                    if not isinstance(v, str):
                        raise ErrorCode("InvalidParameterValue", "Filter Values must be strings")

        # If DryRun is True, simulate permission check
        if dry_run:
            # For simplicity, assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Collect all service link virtual interfaces from state
        all_interfaces: List[ServiceLinkVirtualInterface] = list(self.state.service_links.values())

        # Filter by ServiceLinkVirtualInterfaceId.N if provided
        if service_link_virtual_interface_ids is not None:
            all_interfaces = [
                sli for sli in all_interfaces if sli.service_link_virtual_interface_id in service_link_virtual_interface_ids
            ]

        # Apply filters if provided
        if filters is not None:
            for f in filters:
                name = f["Name"]
                values = f["Values"]
                # Supported filters:
                # outpost-lag-id, outpost-arn, owner-id, state, vlan,
                # service-link-virtual-interface-id, local-gateway-virtual-interface-id (not present in resource, ignore)
                # We will ignore local-gateway-virtual-interface-id as no data for it.
                if name == "outpost-lag-id":
                    all_interfaces = [sli for sli in all_interfaces if sli.outpost_lag_id in values]
                elif name == "outpost-arn":
                    all_interfaces = [sli for sli in all_interfaces if sli.outpost_arn in values]
                elif name == "owner-id":
                    all_interfaces = [sli for sli in all_interfaces if sli.owner_id in values]
                elif name == "state":
                    # values are strings like "pending", "available", etc.
                    valid_states = {state.value for state in ServiceLinkVirtualInterfaceState}
                    for v in values:
                        if v not in valid_states:
                            raise ErrorCode("InvalidParameterValue", f"Invalid state filter value: {v}")
                    all_interfaces = [sli for sli in all_interfaces if sli.configuration_state.value in values]
                elif name == "vlan":
                    # vlan is integer, but filter values are strings, convert to int
                    try:
                        vlan_values = set(int(v) for v in values)
                    except Exception:
                        raise ErrorCode("InvalidParameterValue", "VLAN filter values must be integers")
                    all_interfaces = [sli for sli in all_interfaces if sli.vlan in vlan_values]
                elif name == "service-link-virtual-interface-id":
                    all_interfaces = [sli for sli in all_interfaces if sli.service_link_virtual_interface_id in values]
                elif name == "local-gateway-virtual-interface-id":
                    # No data for this field, so filter results to empty
                    all_interfaces = []
                else:
                    # Unknown filter name
                    raise ErrorCode("InvalidParameterValue", f"Unsupported filter name: {name}")

        # Pagination logic
        # We will use next_token as an index string representing the start index in all_interfaces
        start_index = 0
        if next_token is not None:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "NextToken is invalid")

        # Determine max_results or default to 1000
        max_results = max_results or 1000

        # Slice the results for pagination
        paged_interfaces = all_interfaces[start_index : start_index + max_results]

        # Determine next token for pagination
        new_next_token = None
        if start_index + max_results < len(all_interfaces):
            new_next_token = str(start_index + max_results)

        # Build response
        response = {
            "requestId": self.generate_request_id(),
            "serviceLinkVirtualInterfaceSet": [sli.to_dict() for sli in paged_interfaces],
            "nextToken": new_next_token,
        }

        return response

from emulator_core.gateway.base import BaseGateway

class ServicelinksGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeServiceLinkVirtualInterfaces", self.describe_service_link_virtual_interfaces)

    def describe_service_link_virtual_interfaces(self, params):
        return self.backend.describe_service_link_virtual_interfaces(params)
