from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class RouteTableAssociationStateCode(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"
    FAILED = "failed"


class RouteOrigin(str, Enum):
    CREATE_ROUTE_TABLE = "CreateRouteTable"
    CREATE_ROUTE = "CreateRoute"
    ENABLE_VGW_ROUTE_PROPAGATION = "EnableVgwRoutePropagation"
    ADVERTISEMENT = "Advertisement"


class RouteState(str, Enum):
    ACTIVE = "active"
    BLACKHOLE = "blackhole"


@dataclass
class RouteTableAssociationState:
    state: Optional[RouteTableAssociationStateCode] = None
    status_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "State": self.state.value if self.state else None,
            "StatusMessage": self.status_message,
        }


@dataclass
class RouteTableAssociation:
    route_table_association_id: Optional[str] = None
    route_table_id: Optional[str] = None
    subnet_id: Optional[str] = None
    gateway_id: Optional[str] = None
    public_ipv4_pool: Optional[str] = None
    main: Optional[bool] = None
    association_state: Optional[RouteTableAssociationState] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "RouteTableAssociationId": self.route_table_association_id,
            "RouteTableId": self.route_table_id,
            "SubnetId": self.subnet_id,
            "GatewayId": self.gateway_id,
            "PublicIpv4Pool": self.public_ipv4_pool,
            "Main": self.main,
        }
        if self.association_state:
            d["AssociationState"] = self.association_state.to_dict()
        return d


@dataclass
class PropagatingVgw:
    gateway_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "GatewayId": self.gateway_id,
        }


@dataclass
class Route:
    destination_cidr_block: Optional[str] = None
    destination_ipv6_cidr_block: Optional[str] = None
    destination_prefix_list_id: Optional[str] = None
    carrier_gateway_id: Optional[str] = None
    core_network_arn: Optional[str] = None
    egress_only_internet_gateway_id: Optional[str] = None
    gateway_id: Optional[str] = None
    instance_id: Optional[str] = None
    instance_owner_id: Optional[str] = None
    ip_address: Optional[str] = None
    local_gateway_id: Optional[str] = None
    nat_gateway_id: Optional[str] = None
    network_interface_id: Optional[str] = None
    odb_network_arn: Optional[str] = None
    origin: Optional[RouteOrigin] = None
    state: Optional[RouteState] = None
    transit_gateway_id: Optional[str] = None
    vpc_peering_connection_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "DestinationCidrBlock": self.destination_cidr_block,
            "DestinationIpv6CidrBlock": self.destination_ipv6_cidr_block,
            "DestinationPrefixListId": self.destination_prefix_list_id,
            "CarrierGatewayId": self.carrier_gateway_id,
            "CoreNetworkArn": self.core_network_arn,
            "EgressOnlyInternetGatewayId": self.egress_only_internet_gateway_id,
            "GatewayId": self.gateway_id,
            "InstanceId": self.instance_id,
            "InstanceOwnerId": self.instance_owner_id,
            "IpAddress": self.ip_address,
            "LocalGatewayId": self.local_gateway_id,
            "NatGatewayId": self.nat_gateway_id,
            "NetworkInterfaceId": self.network_interface_id,
            "OdbNetworkArn": self.odb_network_arn,
            "Origin": self.origin.value if self.origin else None,
            "State": self.state.value if self.state else None,
            "TransitGatewayId": self.transit_gateway_id,
            "VpcPeeringConnectionId": self.vpc_peering_connection_id,
        }
        # Remove keys with None values
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


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
class RouteTable:
    route_table_id: str
    vpc_id: Optional[str] = None
    owner_id: Optional[str] = None
    route_set: List[Route] = field(default_factory=list)
    association_set: List[RouteTableAssociation] = field(default_factory=list)
    propagating_vgw_set: List[PropagatingVgw] = field(default_factory=list)
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RouteTableId": self.route_table_id,
            "VpcId": self.vpc_id,
            "OwnerId": self.owner_id,
            "RouteSet": [route.to_dict() for route in self.route_set],
            "AssociationSet": [assoc.to_dict() for assoc in self.association_set],
            "PropagatingVgwSet": [vgw.to_dict() for vgw in self.propagating_vgw_set],
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


class RoutetablesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.route_tables or similar

    def associate_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_table_id = params.get("RouteTableId")
        subnet_id = params.get("SubnetId")
        gateway_id = params.get("GatewayId")
        public_ipv4_pool = params.get("PublicIpv4Pool")

        if not route_table_id:
            raise Exception("Missing required parameter RouteTableId")

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            raise Exception(f"RouteTable {route_table_id} does not exist")

        # Validate that only one of subnet_id, gateway_id, public_ipv4_pool is specified
        specified = [x for x in [subnet_id, gateway_id, public_ipv4_pool] if x is not None]
        if len(specified) == 0:
            raise Exception("One of SubnetId, GatewayId, or PublicIpv4Pool must be specified")
        if len(specified) > 1:
            raise Exception("Only one of SubnetId, GatewayId, or PublicIpv4Pool can be specified")

        # Check if subnet exists if subnet_id is specified
        if subnet_id:
            subnet = self.state.get_resource(subnet_id)
            if not subnet:
                raise Exception(f"Subnet {subnet_id} does not exist")

        # Check if gateway exists if gateway_id is specified
        if gateway_id:
            gateway = self.state.get_resource(gateway_id)
            if not gateway:
                raise Exception(f"Gateway {gateway_id} does not exist")

        # Check if public_ipv4_pool is specified, no validation here as it's a string id

        # Create a new association id
        association_id = self.generate_unique_id("rtbassoc")

        # Create association state
        association_state = RouteTableAssociationState(
            state=RouteTableAssociationStateCode.ASSOCIATING,
            status_message=None,
        )

        # Create the association object
        association = RouteTableAssociation(
            route_table_association_id=association_id,
            route_table_id=route_table_id,
            subnet_id=subnet_id,
            gateway_id=gateway_id,
            public_ipv4_pool=public_ipv4_pool,
            main=False,
            association_state=association_state,
        )

        # Add association to route table
        route_table.association_set.append(association)

        # Save updated route table in state
        self.state.route_tables[route_table_id] = route_table

        return {
            "associationId": association_id,
            "associationState": association_state.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_table_id = params.get("RouteTableId")
        if not route_table_id:
            raise Exception("Missing required parameter RouteTableId")

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            raise Exception(f"RouteTable {route_table_id} does not exist")

        # Destination identifiers
        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_ipv6_cidr_block = params.get("DestinationIpv6CidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")

        # Validate that exactly one destination is specified
        destinations = [destination_cidr_block, destination_ipv6_cidr_block, destination_prefix_list_id]
        if sum(1 for d in destinations if d is not None) != 1:
            raise Exception("Exactly one of DestinationCidrBlock, DestinationIpv6CidrBlock, or DestinationPrefixListId must be specified")

        # Resource identifiers (exactly one of these must be specified)
        resource_ids = [
            params.get("CarrierGatewayId"),
            params.get("CoreNetworkArn"),
            params.get("EgressOnlyInternetGatewayId"),
            params.get("GatewayId"),
            params.get("InstanceId"),
            params.get("LocalGatewayId"),
            params.get("NatGatewayId"),
            params.get("NetworkInterfaceId"),
            params.get("OdbNetworkArn"),
            params.get("TransitGatewayId"),
            params.get("VpcEndpointId"),
            params.get("VpcPeeringConnectionId"),
        ]
        # Count how many resource ids are specified (non-None)
        resource_count = sum(1 for r in resource_ids if r is not None)
        if resource_count != 1:
            raise Exception("Exactly one resource identifier must be specified among CarrierGatewayId, CoreNetworkArn, EgressOnlyInternetGatewayId, GatewayId, InstanceId, LocalGatewayId, NatGatewayId, NetworkInterfaceId, OdbNetworkArn, TransitGatewayId, VpcEndpointId, VpcPeeringConnectionId")

        # Check if route already exists with the same destination, remove it to replace
        def route_matches(route: Route) -> bool:
            if destination_cidr_block and route.destination_cidr_block == destination_cidr_block:
                return True
            if destination_ipv6_cidr_block and route.destination_ipv6_cidr_block == destination_ipv6_cidr_block:
                return True
            if destination_prefix_list_id and route.destination_prefix_list_id == destination_prefix_list_id:
                return True
            return False

        # Remove existing route with same destination if any
        route_table.route_set = [r for r in route_table.route_set if not route_matches(r)]

        # Create new route object
        route = Route(
            destination_cidr_block=destination_cidr_block,
            destination_ipv6_cidr_block=destination_ipv6_cidr_block,
            destination_prefix_list_id=destination_prefix_list_id,
            carrier_gateway_id=params.get("CarrierGatewayId"),
            core_network_arn=params.get("CoreNetworkArn"),
            egress_only_internet_gateway_id=params.get("EgressOnlyInternetGatewayId"),
            gateway_id=params.get("GatewayId"),
            instance_id=params.get("InstanceId"),
            local_gateway_id=params.get("LocalGatewayId"),
            nat_gateway_id=params.get("NatGatewayId"),
            network_interface_id=params.get("NetworkInterfaceId"),
            odb_network_arn=params.get("OdbNetworkArn"),
            origin=RouteOrigin.CREATE_ROUTE,
            state=RouteState.ACTIVE,
            transit_gateway_id=params.get("TransitGatewayId"),
            vpc_peering_connection_id=params.get("VpcPeeringConnectionId"),
            ip_address=None,
            instance_owner_id=None,
        )

        # Add route to route table
        route_table.route_set.append(route)

        # Save updated route table in state
        self.state.route_tables[route_table_id] = route_table

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def create_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_id = params.get("VpcId")
        if not vpc_id:
            raise Exception("Missing required parameter VpcId")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise Exception(f"VPC {vpc_id} does not exist")

        client_token = params.get("ClientToken")

        # Generate unique route table id
        route_table_id = self.generate_unique_id("rtb")

        # Create local route for the VPC CIDR block(s)
        route_set = []
        # Add local route for IPv4 CIDR blocks of the VPC
        for cidr_block in getattr(vpc, "cidr_block_associations", []):
            route_set.append(Route(
                destination_cidr_block=cidr_block,
                gateway_id="local",
                state=RouteState.ACTIVE,
                origin=RouteOrigin.CREATE_ROUTE_TABLE,
                destination_ipv6_cidr_block=None,
                destination_prefix_list_id=None,
                carrier_gateway_id=None,
                core_network_arn=None,
                egress_only_internet_gateway_id=None,
                instance_id=None,
                instance_owner_id=None,
                ip_address=None,
                local_gateway_id=None,
                nat_gateway_id=None,
                network_interface_id=None,
                odb_network_arn=None,
                transit_gateway_id=None,
                vpc_peering_connection_id=None,
            ))
        # Add local route for IPv6 CIDR blocks of the VPC if any
        for ipv6_cidr_block in getattr(vpc, "ipv6_cidr_block_associations", []):
            route_set.append(Route(
                destination_ipv6_cidr_block=ipv6_cidr_block,
                gateway_id="local",
                state=RouteState.ACTIVE,
                origin=RouteOrigin.CREATE_ROUTE_TABLE,
                destination_cidr_block=None,
                destination_prefix_list_id=None,
                carrier_gateway_id=None,
                core_network_arn=None,
                egress_only_internet_gateway_id=None,
                instance_id=None,
                instance_owner_id=None,
                ip_address=None,
                local_gateway_id=None,
                nat_gateway_id=None,
                network_interface_id=None,
                odb_network_arn=None,
                transit_gateway_id=None,
                vpc_peering_connection_id=None,
            ))

        # Parse tags from TagSpecification.N if present
        tag_set = []
        tag_specifications = []
        for key, value in params.items():
            if key.startswith("TagSpecification."):
                tag_specifications.append((key, value))
        # We expect keys like TagSpecification.N.ResourceType and TagSpecification.N.Tags.member.M.Key/Value
        # For simplicity, parse tags if present under TagSpecification.N.Tags
        # We'll parse all tags from params keys starting with TagSpecification.
        # But since no helper is provided, we skip complex parsing and just ignore tags for now.

        # Create route table object
        route_table = RouteTable(
            route_table_id=route_table_id,
            vpc_id=vpc_id,
            owner_id=self.get_owner_id(),
            route_set=route_set,
            association_set=[],
            propagating_vgw_set=[],
            tag_set=tag_set,
        )

        # Save route table in state
        self.state.route_tables[route_table_id] = route_table
        self.state.resources[route_table_id] = route_table

        response = {
            "requestId": self.generate_request_id(),
            "routeTable": route_table.to_dict(),
        }
        if client_token:
            response["clientToken"] = client_token
        return response


    def delete_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        route_table_id = params.get("RouteTableId")
        if not route_table_id:
            raise Exception("Missing required parameter RouteTableId")

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            raise Exception(f"RouteTable {route_table_id} does not exist")

        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_ipv6_cidr_block = params.get("DestinationIpv6CidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")

        # Validate that exactly one destination is specified
        destinations = [destination_cidr_block, destination_ipv6_cidr_block, destination_prefix_list_id]
        if sum(1 for d in destinations if d is not None) != 1:
            raise Exception("Exactly one of DestinationCidrBlock, DestinationIpv6CidrBlock, or DestinationPrefixListId must be specified")

        # Find and remove the route matching the destination
        def route_matches(route: Route) -> bool:
            if destination_cidr_block and route.destination_cidr_block == destination_cidr_block:
                return True
            if destination_ipv6_cidr_block and route.destination_ipv6_cidr_block == destination_ipv6_cidr_block:
                return True
            if destination_prefix_list_id and route.destination_prefix_list_id == destination_prefix_list_id:
                return True
            return False

        original_len = len(route_table.route_set)
        route_table.route_set = [r for r in route_table.route_set if not route_matches(r)]

        if len(route_table.route_set) == original_len:
            # No route was deleted
            raise Exception("The specified route does not exist")

        # Save updated route table in state
        self.state.route_tables[route_table_id] = route_table

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def delete_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        DeleteRouteTable API - LocalStack compatible behavior.

        LocalStack pattern: Catches ClientError and returns success (idempotent delete).
        Also handles the case where route table doesn't exist gracefully.
        """
        route_table_id = params.get("RouteTableId")
        if not route_table_id:
            raise Exception("Missing required parameter RouteTableId")

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            # LocalStack pattern: Return success even if not found (idempotent)
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Check if route table is main route table for the VPC
        # Main route table is the one with an association with main=True
        for assoc in route_table.association_set:
            if assoc.main:
                raise Exception("Cannot delete the main route table")

        # Check if route table has any non-main associations
        non_main_associations = [a for a in route_table.association_set if not a.main]
        if len(non_main_associations) > 0:
            raise Exception("You must disassociate the route table from all subnets before deleting it")

        # Remove route table from state
        del self.state.route_tables[route_table_id]
        if route_table_id in self.state.resources:
            del self.state.resources[route_table_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_route_tables(self, params: dict) -> dict:
        # Validate DryRun parameter if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Extract filters
        filters = []
        # Filters come as Filter.N.Name and Filter.N.Value.M
        # Collect filters by index N
        filter_prefix = "Filter."
        filter_dict = {}
        for key, value in params.items():
            if key.startswith(filter_prefix):
                # key example: Filter.1.Name or Filter.1.Value.1
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    subkey = parts[2]
                    if idx not in filter_dict:
                        filter_dict[idx] = {"Name": None, "Values": []}
                    if subkey == "Name":
                        filter_dict[idx]["Name"] = value
                    elif subkey == "Value" and len(parts) == 4:
                        filter_dict[idx]["Values"].append(value)
                    elif subkey == "Values":
                        # Defensive: if Values is used instead of Value.N
                        if isinstance(value, list):
                            filter_dict[idx]["Values"].extend(value)
                        else:
                            filter_dict[idx]["Values"].append(value)
        # Convert filter_dict to list of dicts
        for f in filter_dict.values():
            if f["Name"] is not None:
                filters.append(f)

        # Extract MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
            except Exception:
                raise ValueError("MaxResults must be an integer")
            if max_results < 5 or max_results > 100:
                raise ValueError("MaxResults must be between 5 and 100")

        next_token = params.get("NextToken")
        # Extract RouteTableId.N parameters
        route_table_ids = []
        for key, value in params.items():
            if key.startswith("RouteTableId."):
                route_table_ids.append(value)

        # Start with all route tables
        all_route_tables = list(self.state.route_tables.values())

        # Filter by RouteTableId if specified
        if route_table_ids:
            all_route_tables = [rt for rt in all_route_tables if rt.route_table_id in route_table_ids]

        # Helper function to match a single filter on a route table
        def match_filter(rt, filter_name, filter_values):
            # filter_values is a list of strings
            # filter_name is case sensitive
            # Implement all filter names as per spec
            # association.gateway-id
            if filter_name == "association.gateway-id":
                for assoc in rt.association_set:
                    if assoc.gateway_id and assoc.gateway_id in filter_values:
                        return True
                return False
            # association.route-table-association-id
            if filter_name == "association.route-table-association-id":
                for assoc in rt.association_set:
                    if assoc.route_table_association_id and assoc.route_table_association_id in filter_values:
                        return True
                return False
            # association.route-table-id
            if filter_name == "association.route-table-id":
                for assoc in rt.association_set:
                    if assoc.route_table_id and assoc.route_table_id in filter_values:
                        return True
                return False
            # association.subnet-id
            if filter_name == "association.subnet-id":
                for assoc in rt.association_set:
                    if assoc.subnet_id and assoc.subnet_id in filter_values:
                        return True
                return False
            # association.main
            if filter_name == "association.main":
                # filter_values expected to be ["true"] or ["false"]
                for assoc in rt.association_set:
                    if assoc.main is not None and str(assoc.main).lower() in [v.lower() for v in filter_values]:
                        return True
                return False
            # owner-id
            if filter_name == "owner-id":
                if rt.owner_id and rt.owner_id in filter_values:
                    return True
                return False
            # route-table-id
            if filter_name == "route-table-id":
                if rt.route_table_id and rt.route_table_id in filter_values:
                    return True
                return False
            # route.destination-cidr-block
            if filter_name == "route.destination-cidr-block":
                for route in rt.route_set:
                    if route.destination_cidr_block and route.destination_cidr_block in filter_values:
                        return True
                return False
            # route.destination-ipv6-cidr-block
            if filter_name == "route.destination-ipv6-cidr-block":
                for route in rt.route_set:
                    if route.destination_ipv6_cidr_block and route.destination_ipv6_cidr_block in filter_values:
                        return True
                return False
            # route.destination-prefix-list-id
            if filter_name == "route.destination-prefix-list-id":
                for route in rt.route_set:
                    if route.destination_prefix_list_id and route.destination_prefix_list_id in filter_values:
                        return True
                return False
            # route.egress-only-internet-gateway-id
            if filter_name == "route.egress-only-internet-gateway-id":
                for route in rt.route_set:
                    if route.egress_only_internet_gateway_id and route.egress_only_internet_gateway_id in filter_values:
                        return True
                return False
            # route.gateway-id
            if filter_name == "route.gateway-id":
                for route in rt.route_set:
                    if route.gateway_id and route.gateway_id in filter_values:
                        return True
                return False
            # route.instance-id
            if filter_name == "route.instance-id":
                for route in rt.route_set:
                    if route.instance_id and route.instance_id in filter_values:
                        return True
                return False
            # route.nat-gateway-id
            if filter_name == "route.nat-gateway-id":
                for route in rt.route_set:
                    if route.nat_gateway_id and route.nat_gateway_id in filter_values:
                        return True
                return False
            # route.transit-gateway-id
            if filter_name == "route.transit-gateway-id":
                for route in rt.route_set:
                    if route.transit_gateway_id and route.transit_gateway_id in filter_values:
                        return True
                return False
            # route.origin
            if filter_name == "route.origin":
                for route in rt.route_set:
                    if route.origin and route.origin.value in filter_values:
                        return True
                return False
            # route.state
            if filter_name == "route.state":
                for route in rt.route_set:
                    if route.state and route.state.value in filter_values:
                        return True
                return False
            # route.vpc-peering-connection-id
            if filter_name == "route.vpc-peering-connection-id":
                for route in rt.route_set:
                    if route.vpc_peering_connection_id and route.vpc_peering_connection_id in filter_values:
                        return True
                return False
            # tag:<key>
            if filter_name.startswith("tag:"):
                tag_key = filter_name[4:]
                tag_set = getattr(rt, "tag_set", []) or []
                for tag in tag_set:
                    # Handle both Tag objects and dicts
                    if hasattr(tag, "key"):
                        t_key, t_value = tag.key, tag.value
                    elif isinstance(tag, dict):
                        t_key = tag.get("Key") or tag.get("key")
                        t_value = tag.get("Value") or tag.get("value")
                    else:
                        continue
                    if t_key == tag_key and t_value in filter_values:
                        return True
                return False
            # tag-key
            if filter_name == "tag-key":
                tag_set = getattr(rt, "tag_set", []) or []
                for tag in tag_set:
                    if hasattr(tag, "key"):
                        t_key = tag.key
                    elif isinstance(tag, dict):
                        t_key = tag.get("Key") or tag.get("key")
                    else:
                        continue
                    if t_key in filter_values:
                        return True
                return False
            # vpc-id
            if filter_name == "vpc-id":
                if rt.vpc_id and rt.vpc_id in filter_values:
                    return True
                return False
            # Unknown filter: ignore (AWS returns empty)
            return False

        # Apply filters: all filters must match (AND)
        filtered_route_tables = []
        for rt in all_route_tables:
            if all(match_filter(rt, f["Name"], f["Values"]) for f in filters):
                filtered_route_tables.append(rt)

        # Pagination: use NextToken as index offset (string token is index)
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Apply MaxResults limit
        if max_results is not None:
            end_index = start_index + max_results
            page_route_tables = filtered_route_tables[start_index:end_index]
            new_next_token = str(end_index) if end_index < len(filtered_route_tables) else None
        else:
            page_route_tables = filtered_route_tables[start_index:]
            new_next_token = None

        # Build response routeTableSet list
        route_table_set = [rt.to_dict() for rt in page_route_tables]

        response = {
            "requestId": self.generate_request_id(),
            "routeTableSet": route_table_set,
            "nextToken": new_next_token,
        }
        return response


    def disassociate_route_table(self, params: dict) -> dict:
        association_id = params.get("AssociationId")
        if not association_id:
            raise ValueError("AssociationId is required")

        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Find the route table association by association_id
        found = False
        for rt in self.state.route_tables.values():
            for assoc in rt.association_set:
                if assoc.route_table_association_id == association_id:
                    # Remove this association from the route table
                    rt.association_set.remove(assoc)
                    found = True
                    break
            if found:
                break

        if not found:
            # AWS returns an error if association not found
            raise ValueError(f"AssociationId {association_id} not found")

        # Return success
        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def replace_route(self, params: dict) -> dict:
        route_table_id = params.get("RouteTableId")
        if not route_table_id:
            raise ValueError("RouteTableId is required")

        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Find route table
        rt = self.state.route_tables.get(route_table_id)
        if not rt:
            raise ValueError(f"RouteTableId {route_table_id} not found")

        # Determine destination key and value
        dest_cidr_block = params.get("DestinationCidrBlock")
        dest_ipv6_cidr_block = params.get("DestinationIpv6CidrBlock")
        dest_prefix_list_id = params.get("DestinationPrefixListId")

        dest_keys = [bool(dest_cidr_block), bool(dest_ipv6_cidr_block), bool(dest_prefix_list_id)]
        if sum(dest_keys) != 1:
            raise ValueError("Exactly one of DestinationCidrBlock, DestinationIpv6CidrBlock, or DestinationPrefixListId must be specified")

        # Find existing route to replace
        existing_route = None
        for route in rt.route_set:
            if dest_cidr_block and route.destination_cidr_block == dest_cidr_block:
                existing_route = route
                break
            if dest_ipv6_cidr_block and route.destination_ipv6_cidr_block == dest_ipv6_cidr_block:
                existing_route = route
                break
            if dest_prefix_list_id and route.destination_prefix_list_id == dest_prefix_list_id:
                existing_route = route
                break

        if not existing_route:
            raise ValueError("No existing route matches the specified destination")

        # Determine new target parameters
        # Only one of these should be specified or LocalTarget true
        target_params = [
            "CarrierGatewayId",
            "CoreNetworkArn",
            "EgressOnlyInternetGatewayId",
            "GatewayId",
            "InstanceId",
            "LocalGatewayId",
            "NatGatewayId",
            "NetworkInterfaceId",
            "OdbNetworkArn",
            "TransitGatewayId",
            "VpcEndpointId",
            "VpcPeeringConnectionId",
        ]
        specified_targets = [p for p in target_params if params.get(p) is not None]
        local_target = params.get("LocalTarget", False)

        if local_target:
            if specified_targets:
                raise ValueError("LocalTarget cannot be specified with other target parameters")
        else:
            if len(specified_targets) != 1:
                raise ValueError("Exactly one target parameter must be specified if LocalTarget is not true")

        # Update existing route with new target and origin/state
        # Clear all target fields first
        existing_route.carrier_gateway_id = None
        existing_route.core_network_arn = None
        existing_route.egress_only_internet_gateway_id = None
        existing_route.gateway_id = None
        existing_route.instance_id = None
        existing_route.local_gateway_id = None
        existing_route.nat_gateway_id = None
        existing_route.network_interface_id = None
        existing_route.odb_network_arn = None
        existing_route.transit_gateway_id = None
        existing_route.vpc_peering_connection_id = None
        # VpcEndpointId is not a field on Route class per given structure, ignore

        if local_target:
            # Reset local route to default target "local"
            existing_route.gateway_id = "local"
            existing_route.origin = RouteOrigin.CREATE_ROUTE_TABLE
            existing_route.state = RouteState.ACTIVE
        else:
            # Set the specified target
            for target in specified_targets:
                value = params.get(target)
                # Map param name to attribute name in Route
                attr_name = {
                    "CarrierGatewayId": "carrier_gateway_id",
                    "CoreNetworkArn": "core_network_arn",
                    "EgressOnlyInternetGatewayId": "egress_only_internet_gateway_id",
                    "GatewayId": "gateway_id",
                    "InstanceId": "instance_id",
                    "LocalGatewayId": "local_gateway_id",
                    "NatGatewayId": "nat_gateway_id",
                    "NetworkInterfaceId": "network_interface_id",
                    "OdbNetworkArn": "odb_network_arn",
                    "TransitGatewayId": "transit_gateway_id",
                    "VpcPeeringConnectionId": "vpc_peering_connection_id",
                }[target]
                setattr(existing_route, attr_name, value)
            existing_route.origin = RouteOrigin.CREATE_ROUTE
            existing_route.state = RouteState.ACTIVE

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def replace_route_table_association(self, params: dict) -> dict:
        association_id = params.get("AssociationId")
        new_route_table_id = params.get("RouteTableId")
        if not association_id:
            raise ValueError("AssociationId is required")
        if not new_route_table_id:
            raise ValueError("RouteTableId is required")

        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Find current association and route table
        current_rt = None
        current_assoc = None
        for rt in self.state.route_tables.values():
            for assoc in rt.association_set:
                if assoc.route_table_association_id == association_id:
                    current_rt = rt
                    current_assoc = assoc
                    break
            if current_assoc:
                break

        if not current_assoc:
            raise ValueError(f"AssociationId {association_id} not found")

        # Find new route table
        new_rt = self.state.route_tables.get(new_route_table_id)
        if not new_rt:
            raise ValueError(f"RouteTableId {new_route_table_id} not found")

        # Remove association from current route table
        current_rt.association_set.remove(current_assoc)

        # Create new association id
        new_association_id = self.generate_unique_id(prefix="rtbassoc-")

        # Create new association object with same subnet_id, gateway_id, public_ipv4_pool, main, association_state
        new_assoc = RouteTableAssociation(
            route_table_association_id=new_association_id,
            route_table_id=new_route_table_id,
            subnet_id=current_assoc.subnet_id,
            gateway_id=current_assoc.gateway_id,
            public_ipv4_pool=current_assoc.public_ipv4_pool,
            main=current_assoc.main,
            association_state=RouteTableAssociationState(
                state=RouteTableAssociationStateCode.ASSOCIATED,
                status_message=None,
            ),
        )

        # Add new association to new route table
        new_rt.association_set.append(new_assoc)

        return {
            "requestId": self.generate_request_id(),
            "newAssociationId": new_association_id,
            "associationState": new_assoc.association_state.to_dict() if new_assoc.association_state else None,
        }

    

from emulator_core.gateway.base import BaseGateway

class RoutetablesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateRouteTable", self.associate_route_table)
        self.register_action("CreateRoute", self.create_route)
        self.register_action("CreateRouteTable", self.create_route_table)
        self.register_action("DeleteRoute", self.delete_route)
        self.register_action("DeleteRouteTable", self.delete_route_table)
        self.register_action("DescribeRouteTables", self.describe_route_tables)
        self.register_action("DisassociateRouteTable", self.disassociate_route_table)
        self.register_action("ReplaceRoute", self.replace_route)
        self.register_action("ReplaceRouteTableAssociation", self.replace_route_table_association)

    def associate_route_table(self, params):
        return self.backend.associate_route_table(params)

    def create_route(self, params):
        return self.backend.create_route(params)

    def create_route_table(self, params):
        return self.backend.create_route_table(params)

    def delete_route(self, params):
        return self.backend.delete_route(params)

    def delete_route_table(self, params):
        return self.backend.delete_route_table(params)

    def describe_route_tables(self, params):
        return self.backend.describe_route_tables(params)

    def disassociate_route_table(self, params):
        return self.backend.disassociate_route_table(params)

    def replace_route(self, params):
        return self.backend.replace_route(params)

    def replace_route_table_association(self, params):
        return self.backend.replace_route_table_association(params)
