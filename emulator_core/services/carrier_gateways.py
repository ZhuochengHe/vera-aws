from typing import Dict, Any, List, Optional
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
class CarrierGateway:
    carrier_gateway_id: str
    owner_id: str
    state: ResourceState
    tags: Dict[str, str] = field(default_factory=dict)
    vpc_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "carrierGatewayId": self.carrier_gateway_id,
            "ownerId": self.owner_id,
            "state": self.state.value,
            "tagSet": [{"Key": k, "Value": v} for k, v in self.tags.items()],
            "vpcId": self.vpc_id,
        }


class CarrierGatewayBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.carrier_gateways dict for storage

    def _validate_tags(self, tag_specifications: Optional[List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Validate and extract tags from TagSpecification.N parameter.
        Only tags with ResourceType == "carrier-gateway" are allowed.
        Return dict of tags.
        """
        tags: Dict[str, str] = {}
        if not tag_specifications:
            return tags

        if not isinstance(tag_specifications, list):
            raise ErrorCode.InvalidParameterValue("TagSpecification must be a list")

        for tag_spec in tag_specifications:
            if not isinstance(tag_spec, dict):
                raise ErrorCode.InvalidParameterValue("Each TagSpecification must be a dict")
            resource_type = tag_spec.get("ResourceType")
            if resource_type != "carrier-gateway":
                raise ErrorCode.InvalidParameterValue(
                    f"Invalid ResourceType in TagSpecification: {resource_type}. Must be 'carrier-gateway'"
                )
            tag_list = tag_spec.get("Tags", [])
            if not isinstance(tag_list, list):
                raise ErrorCode.InvalidParameterValue("Tags must be a list")
            for tag in tag_list:
                if not isinstance(tag, dict):
                    raise ErrorCode.InvalidParameterValue("Each tag must be a dict")
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None or not isinstance(key, str):
                    raise ErrorCode.InvalidParameterValue("Tag Key must be a string")
                if key.lower().startswith("aws:"):
                    raise ErrorCode.InvalidParameterValue("Tag Key may not begin with 'aws:'")
                if len(key) > 127:
                    raise ErrorCode.InvalidParameterValue("Tag Key must be at most 127 Unicode characters")
                if value is not None and not isinstance(value, str):
                    raise ErrorCode.InvalidParameterValue("Tag Value must be a string or None")
                if value is not None and len(value) > 256:
                    raise ErrorCode.InvalidParameterValue("Tag Value must be at most 256 Unicode characters")
                tags[key] = value if value is not None else ""
        return tags

    def create_carrier_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter VpcId
        vpc_id = params.get("VpcId")
        if not vpc_id or not isinstance(vpc_id, str):
            raise ErrorCode.MissingParameter("VpcId is required and must be a string")

        # Validate VPC existence
        vpc = self.state.get_resource(vpc_id)
        if not vpc:
            raise ErrorCode.InvalidVpcIDNotFound(f"The vpc ID '{vpc_id}' does not exist")

        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        # Validate ClientToken if present (no specific validation needed here)

        # Validate TagSpecification.N
        tag_specifications = params.get("TagSpecification.N")
        tags = self._validate_tags(tag_specifications)

        # Generate carrier gateway id
        carrier_gateway_id = f"cgw-{self.generate_unique_id()}"
        owner_id = self.get_owner_id()

        # Create CarrierGateway object with state PENDING initially
        carrier_gateway = CarrierGateway(
            carrier_gateway_id=carrier_gateway_id,
            owner_id=owner_id,
            state=ResourceState.PENDING,
            tags=tags,
            vpc_id=vpc_id,
        )

        # Store in shared state dict
        self.state.carrier_gateways[carrier_gateway_id] = carrier_gateway

        # Transition state to AVAILABLE (simulate creation)
        carrier_gateway.state = ResourceState.AVAILABLE

        return {
            "carrierGateway": carrier_gateway.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def delete_carrier_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        carrier_gateway_id = params.get("CarrierGatewayId")
        if not carrier_gateway_id or not isinstance(carrier_gateway_id, str):
            raise ErrorCode.MissingParameter("CarrierGatewayId is required and must be a string")

        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        carrier_gateway = self.state.carrier_gateways.get(carrier_gateway_id)
        if not carrier_gateway:
            raise ErrorCode.InvalidCarrierGatewayIDNotFound(f"The carrier gateway ID '{carrier_gateway_id}' does not exist")

        # Mark state as DELETING then DELETED (simulate deletion)
        carrier_gateway.state = ResourceState.DELETING
        carrier_gateway.state = ResourceState.DELETED

        # Remove from state dict
        del self.state.carrier_gateways[carrier_gateway_id]

        return {
            "carrierGateway": carrier_gateway.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def describe_carrier_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        # Extract CarrierGatewayId.N list if present
        carrier_gateway_ids: Optional[List[str]] = None
        # The param keys for multiple IDs are CarrierGatewayId.1, CarrierGatewayId.2, ... or CarrierGatewayId.N as list
        # We support CarrierGatewayId.N as list per spec
        # Defensive: accept both list or dict keys with suffixes
        if "CarrierGatewayId.N" in params:
            carrier_gateway_ids = params.get("CarrierGatewayId.N")
            if not isinstance(carrier_gateway_ids, list):
                raise ErrorCode.InvalidParameterValue("CarrierGatewayId.N must be a list of strings")
            for cid in carrier_gateway_ids:
                if not isinstance(cid, str):
                    raise ErrorCode.InvalidParameterValue("Each CarrierGatewayId must be a string")
        else:
            # Also support keys like CarrierGatewayId.1, CarrierGatewayId.2, ...
            carrier_gateway_ids = []
            for key in params:
                if key.startswith("CarrierGatewayId."):
                    val = params[key]
                    if not isinstance(val, str):
                        raise ErrorCode.InvalidParameterValue(f"{key} must be a string")
                    carrier_gateway_ids.append(val)
            if not carrier_gateway_ids:
                carrier_gateway_ids = None  # no filter by id

        # Extract filters Filter.N if present
        filters: Dict[str, List[str]] = {}
        # Filters come as Filter.N.Name and Filter.N.Values.M
        # We parse all Filter.N groups
        filter_prefix = "Filter."
        filter_name_key = ".Name"
        filter_values_prefix = ".Values."
        # Collect filter groups by N
        filter_groups: Dict[str, Dict[str, Any]] = {}
        for key, value in params.items():
            if key.startswith(filter_prefix):
                # key example: Filter.1.Name or Filter.1.Values.1
                remainder = key[len(filter_prefix):]  # e.g. "1.Name" or "1.Values.1"
                parts = remainder.split(".")
                if len(parts) >= 2:
                    group_num = parts[0]
                    field = parts[1]
                    if group_num not in filter_groups:
                        filter_groups[group_num] = {"Name": None, "Values": []}
                    if field == "Name":
                        if not isinstance(value, str):
                            raise ErrorCode.InvalidParameterValue("Filter Name must be a string")
                        filter_groups[group_num]["Name"] = value
                    elif field == "Values":
                        # Values can have multiple indices: Filter.1.Values.1, Filter.1.Values.2, ...
                        # We collect all values for this group
                        if not isinstance(value, str):
                            raise ErrorCode.InvalidParameterValue("Filter Value must be a string")
                        filter_groups[group_num]["Values"].append(value)
                    else:
                        # Unexpected field under Filter.N
                        pass
                else:
                    # Unexpected filter key format
                    pass

        # Build filters dict from filter_groups
        for group in filter_groups.values():
            name = group["Name"]
            values = group["Values"]
            if name is not None:
                filters[name] = values

        # Validate MaxResults if present
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode.InvalidParameterValue("MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode.InvalidParameterValue("MaxResults must be between 5 and 1000")

        # NextToken is not implemented (pagination) - just ignore or return None

        # Filter carrier gateways by IDs if provided
        carrier_gateways: List[CarrierGateway] = []
        if carrier_gateway_ids is not None:
            for cid in carrier_gateway_ids:
                cg = self.state.carrier_gateways.get(cid)
                if cg:
                    carrier_gateways.append(cg)
        else:
            # No ID filter, get all
            carrier_gateways = list(self.state.carrier_gateways.values())

        # Apply filters
        def matches_filter(cg: CarrierGateway, filters: Dict[str, List[str]]) -> bool:
            for fname, fvalues in filters.items():
                # Supported filters:
                # carrier-gateway-id, state, owner-id, tag:<key>, tag-key, vpc-id
                if fname == "carrier-gateway-id":
                    if cg.carrier_gateway_id not in fvalues:
                        return False
                elif fname == "state":
                    # State values are strings like "pending", "available", "deleting", "deleted"
                    if cg.state.value not in fvalues:
                        return False
                elif fname == "owner-id":
                    if cg.owner_id not in fvalues:
                        return False
                elif fname.startswith("tag:"):
                    tag_key = fname[4:]
                    # Match if tag key exists and value in fvalues
                    tag_val = cg.tags.get(tag_key)
                    if tag_val is None or tag_val not in fvalues:
                        return False
                elif fname == "tag-key":
                    # Match if any tag key in fvalues
                    if not any(k in fvalues for k in cg.tags.keys()):
                        return False
                elif fname == "vpc-id":
                    if cg.vpc_id not in fvalues:
                        return False
                else:
                    # Unknown filter name - ignore or reject? Spec does not say error, so ignore
                    pass
            return True

        filtered_cgs = [cg for cg in carrier_gateways if matches_filter(cg, filters)]

        # Apply MaxResults limit if specified
        if max_results is not None:
            filtered_cgs = filtered_cgs[:max_results]

        # No pagination token support, so nextToken is always None
        next_token = None

        return {
            "carrierGatewaySet": [cg.to_dict() for cg in filtered_cgs],
            "nextToken": next_token,
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class CarriergatewaysGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateCarrierGateway", self.create_carrier_gateway)
        self.register_action("DeleteCarrierGateway", self.delete_carrier_gateway)
        self.register_action("DescribeCarrierGateways", self.describe_carrier_gateways)

    def create_carrier_gateway(self, params):
        return self.backend.create_carrier_gateway(params)

    def delete_carrier_gateway(self, params):
        return self.backend.delete_carrier_gateway(params)

    def describe_carrier_gateways(self, params):
        return self.backend.describe_carrier_gateways(params)
