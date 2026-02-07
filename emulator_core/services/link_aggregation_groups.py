from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class OutpostLag:
    outpost_lag_id: str
    outpost_arn: Optional[str] = None
    owner_id: Optional[str] = None
    state: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    local_gateway_virtual_interface_id_set: List[str] = field(default_factory=list)
    service_link_virtual_interface_id_set: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outpostLagId": self.outpost_lag_id,
            "outpostArn": self.outpost_arn,
            "ownerId": self.owner_id,
            "state": self.state,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "localGatewayVirtualInterfaceIdSet": self.local_gateway_virtual_interface_id_set,
            "serviceLinkVirtualInterfaceIdSet": self.service_link_virtual_interface_id_set,
        }


class LinkAggregationGroupsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.link_aggregation_groups dict for storage

    def describe_outpost_lags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun parameter
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean if provided")

        # Validate MaxResults parameter
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode.InvalidParameterValue("MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode.InvalidParameterValue("MaxResults must be between 5 and 1000")

        # Validate NextToken parameter
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode.InvalidParameterValue("NextToken must be a string if provided")

        # Validate OutpostLagId.N parameter (list of strings)
        outpost_lag_ids = params.get("OutpostLagId.N")
        if outpost_lag_ids is not None:
            if not isinstance(outpost_lag_ids, list):
                raise ErrorCode.InvalidParameterValue("OutpostLagId.N must be a list of strings")
            for lag_id in outpost_lag_ids:
                if not isinstance(lag_id, str):
                    raise ErrorCode.InvalidParameterValue("Each OutpostLagId must be a string")

        # Validate Filters parameter
        filters = params.get("Filter.N")
        if filters is not None:
            if not isinstance(filters, list):
                raise ErrorCode.InvalidParameterValue("Filter.N must be a list of filter objects")
            for f in filters:
                if not isinstance(f, dict):
                    raise ErrorCode.InvalidParameterValue("Each filter must be a dict")
                if "Name" not in f:
                    raise ErrorCode.InvalidParameterValue("Filter missing required 'Name' field")
                if not isinstance(f["Name"], str):
                    raise ErrorCode.InvalidParameterValue("Filter Name must be a string")
                if "Values" in f:
                    if not isinstance(f["Values"], list):
                        raise ErrorCode.InvalidParameterValue("Filter Values must be a list of strings")
                    for v in f["Values"]:
                        if not isinstance(v, str):
                            raise ErrorCode.InvalidParameterValue("Filter Values must be strings")

        # DryRun permission check simulation
        if dry_run:
            # For emulation, assume permission granted
            raise ErrorCode.DryRunOperation("DryRunOperation")

        # Collect all OutpostLags from state
        all_lags: List[OutpostLag] = list(self.state.link_aggregation_groups.values())

        # Filter by OutpostLagId.N if provided
        if outpost_lag_ids is not None:
            all_lags = [lag for lag in all_lags if lag.outpost_lag_id in outpost_lag_ids]

        # Apply filters if provided
        if filters is not None:
            for f in filters:
                name = f["Name"]
                values = f.get("Values", [])
                if not values:
                    continue  # no values means no filtering for this filter

                # Supported filters:
                # service-link-virtual-interface-id
                # service-link-virtual-interface-arn
                # outpost-id
                # outpost-arn
                # owner-id
                # vlan
                # local-address
                # peer-address
                # peer-bgp-asn
                # outpost-lag-id
                # configuration-state

                # We only have some fields in OutpostLag, so we filter accordingly.
                # For unsupported filters, no matches.

                if name == "service-link-virtual-interface-id":
                    all_lags = [
                        lag for lag in all_lags
                        if any(sid in values for sid in lag.service_link_virtual_interface_id_set)
                    ]
                elif name == "service-link-virtual-interface-arn":
                    # We do not have ARNs for service link virtual interfaces in our model, so no matches
                    all_lags = []
                elif name == "outpost-id":
                    # outpost-id is not directly stored, but outpostArn may contain it
                    all_lags = [
                        lag for lag in all_lags
                        if lag.outpost_arn and any(val in lag.outpost_arn for val in values)
                    ]
                elif name == "outpost-arn":
                    all_lags = [
                        lag for lag in all_lags
                        if lag.outpost_arn and any(val == lag.outpost_arn for val in values)
                    ]
                elif name == "owner-id":
                    all_lags = [
                        lag for lag in all_lags
                        if lag.owner_id and lag.owner_id in values
                    ]
                elif name == "vlan":
                    # VLAN is not modeled, so no matches
                    all_lags = []
                elif name == "local-address":
                    # Not modeled, no matches
                    all_lags = []
                elif name == "peer-address":
                    # Not modeled, no matches
                    all_lags = []
                elif name == "peer-bgp-asn":
                    # Not modeled, no matches
                    all_lags = []
                elif name == "outpost-lag-id":
                    all_lags = [
                        lag for lag in all_lags
                        if lag.outpost_lag_id in values
                    ]
                elif name == "configuration-state":
                    all_lags = [
                        lag for lag in all_lags
                        if lag.state and lag.state in values
                    ]
                else:
                    # Unknown filter name - no matches
                    all_lags = []

                if not all_lags:
                    break  # no need to continue filtering if empty

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken value")

        # Apply MaxResults limit
        if max_results is None:
            max_results = 1000  # default max

        end_index = start_index + max_results
        paged_lags = all_lags[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(all_lags):
            new_next_token = str(end_index)

        # Build response
        response = {
            "outpostLagSet": [lag.to_dict() for lag in paged_lags],
            "requestId": self.generate_request_id(),
            "nextToken": new_next_token,
        }

        return response

from emulator_core.gateway.base import BaseGateway

class LinkaggregationgroupsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeOutpostLags", self.describe_outpost_lags)

    def describe_outpost_lags(self, params):
        return self.backend.describe_outpost_lags(params)
