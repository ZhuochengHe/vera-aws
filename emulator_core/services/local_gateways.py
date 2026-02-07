from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class StateReason:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Code": self.code,
            "Message": self.message,
        }


class LocalGatewayRouteState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    BLACKHOLE = "blackhole"
    DELETING = "deleting"
    DELETED = "deleted"


class LocalGatewayRouteType(str, Enum):
    STATIC = "static"
    PROPAGATED = "propagated"


@dataclass
class LocalGatewayRoute:
    coip_pool_id: Optional[str] = None
    destination_cidr_block: Optional[str] = None
    destination_prefix_list_id: Optional[str] = None
    local_gateway_route_table_arn: Optional[str] = None
    local_gateway_route_table_id: Optional[str] = None
    local_gateway_virtual_interface_group_id: Optional[str] = None
    network_interface_id: Optional[str] = None
    owner_id: Optional[str] = None
    state: Optional[LocalGatewayRouteState] = None
    subnet_id: Optional[str] = None
    type: Optional[LocalGatewayRouteType] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CoipPoolId": self.coip_pool_id,
            "DestinationCidrBlock": self.destination_cidr_block,
            "DestinationPrefixListId": self.destination_prefix_list_id,
            "LocalGatewayRouteTableArn": self.local_gateway_route_table_arn,
            "LocalGatewayRouteTableId": self.local_gateway_route_table_id,
            "LocalGatewayVirtualInterfaceGroupId": self.local_gateway_virtual_interface_group_id,
            "NetworkInterfaceId": self.network_interface_id,
            "OwnerId": self.owner_id,
            "State": self.state.value if self.state else None,
            "SubnetId": self.subnet_id,
            "Type": self.type.value if self.type else None,
        }


class LocalGatewayRouteTableMode(str, Enum):
    DIRECT_VPC_ROUTING = "direct-vpc-routing"
    COIP = "coip"


@dataclass
class LocalGatewayRouteTable:
    local_gateway_id: Optional[str] = None
    local_gateway_route_table_arn: Optional[str] = None
    local_gateway_route_table_id: Optional[str] = None
    mode: Optional[LocalGatewayRouteTableMode] = None
    outpost_arn: Optional[str] = None
    owner_id: Optional[str] = None
    state: Optional[str] = None
    state_reason: Optional[StateReason] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "LocalGatewayId": self.local_gateway_id,
            "LocalGatewayRouteTableArn": self.local_gateway_route_table_arn,
            "LocalGatewayRouteTableId": self.local_gateway_route_table_id,
            "Mode": self.mode.value if self.mode else None,
            "OutpostArn": self.outpost_arn,
            "OwnerId": self.owner_id,
            "State": self.state,
            "StateReason": self.state_reason.to_dict() if self.state_reason else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


class LocalGatewayRouteTableVirtualInterfaceGroupAssociationState(str, Enum):
    # No explicit enum values given, so keep as string
    pass


@dataclass
class LocalGatewayRouteTableVirtualInterfaceGroupAssociation:
    local_gateway_id: Optional[str] = None
    local_gateway_route_table_arn: Optional[str] = None
    local_gateway_route_table_id: Optional[str] = None
    local_gateway_route_table_virtual_interface_group_association_id: Optional[str] = None
    local_gateway_virtual_interface_group_id: Optional[str] = None
    owner_id: Optional[str] = None
    state: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "LocalGatewayId": self.local_gateway_id,
            "LocalGatewayRouteTableArn": self.local_gateway_route_table_arn,
            "LocalGatewayRouteTableId": self.local_gateway_route_table_id,
            "LocalGatewayRouteTableVirtualInterfaceGroupAssociationId": self.local_gateway_route_table_virtual_interface_group_association_id,
            "LocalGatewayVirtualInterfaceGroupId": self.local_gateway_virtual_interface_group_id,
            "OwnerId": self.owner_id,
            "State": self.state,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


class LocalGatewayVirtualInterfaceConfigurationState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


@dataclass
class LocalGatewayVirtualInterface:
    configuration_state: Optional[LocalGatewayVirtualInterfaceConfigurationState] = None
    local_address: Optional[str] = None
    local_bgp_asn: Optional[int] = None
    local_gateway_id: Optional[str] = None
    local_gateway_virtual_interface_arn: Optional[str] = None
    local_gateway_virtual_interface_group_id: Optional[str] = None
    local_gateway_virtual_interface_id: Optional[str] = None
    outpost_lag_id: Optional[str] = None
    owner_id: Optional[str] = None
    peer_address: Optional[str] = None
    peer_bgp_asn: Optional[int] = None
    peer_bgp_asn_extended: Optional[int] = None
    tag_set: List[Tag] = field(default_factory=list)
    vlan: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ConfigurationState": self.configuration_state.value if self.configuration_state else None,
            "LocalAddress": self.local_address,
            "LocalBgpAsn": self.local_bgp_asn,
            "LocalGatewayId": self.local_gateway_id,
            "LocalGatewayVirtualInterfaceArn": self.local_gateway_virtual_interface_arn,
            "LocalGatewayVirtualInterfaceGroupId": self.local_gateway_virtual_interface_group_id,
            "LocalGatewayVirtualInterfaceId": self.local_gateway_virtual_interface_id,
            "OutpostLagId": self.outpost_lag_id,
            "OwnerId": self.owner_id,
            "PeerAddress": self.peer_address,
            "PeerBgpAsn": self.peer_bgp_asn,
            "PeerBgpAsnExtended": self.peer_bgp_asn_extended,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "Vlan": self.vlan,
        }


class LocalGatewayVirtualInterfaceGroupConfigurationState(str, Enum):
    PENDING = "pending"
    INCOMPLETE = "incomplete"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


@dataclass
class LocalGatewayVirtualInterfaceGroup:
    configuration_state: Optional[LocalGatewayVirtualInterfaceGroupConfigurationState] = None
    local_bgp_asn: Optional[int] = None
    local_bgp_asn_extended: Optional[int] = None
    local_gateway_id: Optional[str] = None
    local_gateway_virtual_interface_group_arn: Optional[str] = None
    local_gateway_virtual_interface_group_id: Optional[str] = None
    local_gateway_virtual_interface_id_set: List[str] = field(default_factory=list)
    owner_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ConfigurationState": self.configuration_state.value if self.configuration_state else None,
            "LocalBgpAsn": self.local_bgp_asn,
            "LocalBgpAsnExtended": self.local_bgp_asn_extended,
            "LocalGatewayId": self.local_gateway_id,
            "LocalGatewayVirtualInterfaceGroupArn": self.local_gateway_virtual_interface_group_arn,
            "LocalGatewayVirtualInterfaceGroupId": self.local_gateway_virtual_interface_group_id,
            "LocalGatewayVirtualInterfaceIdSet": self.local_gateway_virtual_interface_id_set,
            "OwnerId": self.owner_id,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


class LocalGatewayState(str, Enum):
    # No explicit enum values given, so keep as string
    pass


@dataclass
class LocalGateway:
    local_gateway_id: Optional[str] = None
    outpost_arn: Optional[str] = None
    owner_id: Optional[str] = None
    state: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "LocalGatewayId": self.local_gateway_id,
            "OutpostArn": self.outpost_arn,
            "OwnerId": self.owner_id,
            "State": self.state,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


class LocalgatewaysBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)

    def create_local_gateway_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self.generate_request_id()
        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")
        local_gateway_virtual_interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        network_interface_id = params.get("NetworkInterfaceId")
        dry_run = params.get("DryRun", False)

        # Validate required parameter
        if not local_gateway_route_table_id:
            raise Exception("Missing required parameter LocalGatewayRouteTableId")

        # Validate that exactly one of LocalGatewayVirtualInterfaceGroupId or NetworkInterfaceId is specified
        if (local_gateway_virtual_interface_group_id is None and network_interface_id is None) or \
           (local_gateway_virtual_interface_group_id is not None and network_interface_id is not None):
            raise Exception("You must specify exactly one of LocalGatewayVirtualInterfaceGroupId or NetworkInterfaceId")

        # Validate that DestinationCidrBlock and DestinationPrefixListId are not both specified
        if destination_cidr_block and destination_prefix_list_id:
            raise Exception("You cannot specify both DestinationCidrBlock and DestinationPrefixListId")

        # DryRun check (simulate permission check)
        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Retrieve the local gateway route table
        local_gateway_route_table = self.state.local_gateways.get(local_gateway_route_table_id)
        if not local_gateway_route_table:
            raise Exception(f"LocalGatewayRouteTable {local_gateway_route_table_id} not found")

        # Create route id (not explicitly required but we need to store route)
        route_id = self.generate_unique_id()

        # Determine route type: static (since this is CreateLocalGatewayRoute)
        route_type = LocalGatewayRouteType.static

        # Create route object
        route = LocalGatewayRoute()
        route.coip_pool_id = None
        route.destination_cidr_block = destination_cidr_block
        route.destination_prefix_list_id = destination_prefix_list_id
        route.local_gateway_route_table_arn = local_gateway_route_table.local_gateway_route_table_arn
        route.local_gateway_route_table_id = local_gateway_route_table_id
        route.local_gateway_virtual_interface_group_id = local_gateway_virtual_interface_group_id
        route.network_interface_id = network_interface_id
        route.owner_id = self.get_owner_id()
        route.state = LocalGatewayRouteState.active
        route.subnet_id = None
        route.type = route_type

        # Store route in state resources keyed by route_id
        self.state.resources[route_id] = route

        # Return response
        return {
            "requestId": request_id,
            "route": route.to_dict(),
        }


    def create_local_gateway_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self.generate_request_id()
        local_gateway_id = params.get("LocalGatewayId")
        mode_str = params.get("Mode")
        tag_specifications = params.get("TagSpecification.N", [])

        # Validate required parameter
        if not local_gateway_id:
            raise Exception("Missing required parameter LocalGatewayId")

        # DryRun check
        if params.get("DryRun", False):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate local gateway exists
        local_gateway = self.state.local_gateways.get(local_gateway_id)
        if not local_gateway:
            raise Exception(f"LocalGateway {local_gateway_id} not found")

        # Validate mode if provided
        mode = None
        if mode_str:
            try:
                mode = LocalGatewayRouteTableMode(mode_str)
            except Exception:
                raise Exception(f"Invalid Mode value: {mode_str}")

        # Generate unique id and arn for route table
        local_gateway_route_table_id = self.generate_unique_id()
        local_gateway_route_table_arn = f"arn:aws:ec2:::local-gateway-route-table/{local_gateway_route_table_id}"

        # Create tag set from tag specifications
        tag_set = []
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tag_set.append(Tag(key=key, value=value))

        # Create local gateway route table object
        local_gateway_route_table = LocalGatewayRouteTable()
        local_gateway_route_table.local_gateway_id = local_gateway_id
        local_gateway_route_table.local_gateway_route_table_arn = local_gateway_route_table_arn
        local_gateway_route_table.local_gateway_route_table_id = local_gateway_route_table_id
        local_gateway_route_table.mode = mode
        local_gateway_route_table.outpost_arn = local_gateway.outpost_arn
        local_gateway_route_table.owner_id = self.get_owner_id()
        local_gateway_route_table.state = "available"
        local_gateway_route_table.state_reason = None
        local_gateway_route_table.tag_set = tag_set

        # Store in state resources
        self.state.resources[local_gateway_route_table_id] = local_gateway_route_table

        return {
            "localGatewayRouteTable": local_gateway_route_table.to_dict(),
            "requestId": request_id,
        }


    def create_local_gateway_route_table_virtual_interface_group_association(self, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self.generate_request_id()
        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        local_gateway_virtual_interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        tag_specifications = params.get("TagSpecification.N", [])

        # Validate required parameters
        if not local_gateway_route_table_id:
            raise Exception("Missing required parameter LocalGatewayRouteTableId")
        if not local_gateway_virtual_interface_group_id:
            raise Exception("Missing required parameter LocalGatewayVirtualInterfaceGroupId")

        # DryRun check
        if params.get("DryRun", False):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate local gateway route table exists
        local_gateway_route_table = self.state.local_gateways.get(local_gateway_route_table_id)
        if not local_gateway_route_table:
            raise Exception(f"LocalGatewayRouteTable {local_gateway_route_table_id} not found")

        # Validate local gateway virtual interface group exists
        local_gateway_virtual_interface_group = self.state.resources.get(local_gateway_virtual_interface_group_id)
        if not local_gateway_virtual_interface_group:
            raise Exception(f"LocalGatewayVirtualInterfaceGroup {local_gateway_virtual_interface_group_id} not found")

        # Generate association id and arn
        association_id = self.generate_unique_id()
        local_gateway_route_table_arn = local_gateway_route_table.local_gateway_route_table_arn

        # Create tag set from tag specifications
        tag_set = []
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tag_set.append(Tag(key=key, value=value))

        # Create association object
        association = LocalGatewayRouteTableVirtualInterfaceGroupAssociation()
        association.local_gateway_id = local_gateway_route_table.local_gateway_id
        association.local_gateway_route_table_arn = local_gateway_route_table_arn
        association.local_gateway_route_table_id = local_gateway_route_table_id
        association.local_gateway_route_table_virtual_interface_group_association_id = association_id
        association.local_gateway_virtual_interface_group_id = local_gateway_virtual_interface_group_id
        association.owner_id = self.get_owner_id()
        association.state = "available"
        association.tag_set = tag_set

        # Store association in state resources
        self.state.resources[association_id] = association

        return {
            "localGatewayRouteTableVirtualInterfaceGroupAssociation": association.to_dict(),
            "requestId": request_id,
        }


    def create_local_gateway_virtual_interface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self.generate_request_id()
        local_address = params.get("LocalAddress")
        local_gateway_virtual_interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        outpost_lag_id = params.get("OutpostLagId")
        peer_address = params.get("PeerAddress")
        peer_bgp_asn = params.get("PeerBgpAsn")
        peer_bgp_asn_extended = params.get("PeerBgpAsnExtended")
        vlan = params.get("Vlan")
        tag_specifications = params.get("TagSpecification.N", [])

        # Validate required parameters
        missing_params = []
        if not local_address:
            missing_params.append("LocalAddress")
        if not local_gateway_virtual_interface_group_id:
            missing_params.append("LocalGatewayVirtualInterfaceGroupId")
        if not outpost_lag_id:
            missing_params.append("OutpostLagId")
        if not peer_address:
            missing_params.append("PeerAddress")
        if vlan is None:
            missing_params.append("Vlan")
        if missing_params:
            raise Exception(f"Missing required parameter(s): {', '.join(missing_params)}")

        # DryRun check
        if params.get("DryRun", False):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate local gateway virtual interface group exists
        local_gateway_virtual_interface_group = self.state.resources.get(local_gateway_virtual_interface_group_id)
        if not local_gateway_virtual_interface_group:
            raise Exception(f"LocalGatewayVirtualInterfaceGroup {local_gateway_virtual_interface_group_id} not found")

        # Generate unique id and arn
        local_gateway_virtual_interface_id = self.generate_unique_id()
        local_gateway_virtual_interface_arn = f"arn:aws:ec2:::local-gateway-virtual-interface/{local_gateway_virtual_interface_id}"

        # Create tag set from tag specifications
        tag_set = []
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tag_set.append(Tag(key=key, value=value))

        # Create virtual interface object
        virtual_interface = LocalGatewayVirtualInterface()
        virtual_interface.configuration_state = LocalGatewayVirtualInterfaceConfigurationState.available
        virtual_interface.local_address = local_address
        virtual_interface.local_bgp_asn = local_gateway_virtual_interface_group.local_bgp_asn
        virtual_interface.local_gateway_id = local_gateway_virtual_interface_group.local_gateway_id
        virtual_interface.local_gateway_virtual_interface_arn = local_gateway_virtual_interface_arn
        virtual_interface.local_gateway_virtual_interface_group_id = local_gateway_virtual_interface_group_id
        virtual_interface.local_gateway_virtual_interface_id = local_gateway_virtual_interface_id
        virtual_interface.outpost_lag_id = outpost_lag_id
        virtual_interface.owner_id = self.get_owner_id()
        virtual_interface.peer_address = peer_address
        virtual_interface.peer_bgp_asn = peer_bgp_asn
        virtual_interface.peer_bgp_asn_extended = peer_bgp_asn_extended
        virtual_interface.tag_set = tag_set
        virtual_interface.vlan = vlan

        # Store in state resources
        self.state.resources[local_gateway_virtual_interface_id] = virtual_interface

        return {
            "localGatewayVirtualInterface": virtual_interface.to_dict(),
            "requestId": request_id,
        }


    def create_local_gateway_route_table_vpc_association(self, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self.generate_request_id()
        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        vpc_id = params.get("VpcId")
        tag_specifications = params.get("TagSpecification.N", [])

        # Validate required parameters
        if not local_gateway_route_table_id:
            raise Exception("Missing required parameter LocalGatewayRouteTableId")
        if not vpc_id:
            raise Exception("Missing required parameter VpcId")

        # DryRun check
        if params.get("DryRun", False):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate local gateway route table exists
        local_gateway_route_table = self.state.local_gateways.get(local_gateway_route_table_id)
        if not local_gateway_route_table:
            raise Exception(f"LocalGatewayRouteTable {local_gateway_route_table_id} not found")

        # Validate VPC exists
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise Exception(f"VPC {vpc_id} not found")

        # Generate association id and arn
        association_id = self.generate_unique_id()
        local_gateway_route_table_arn = local_gateway_route_table.local_gateway_route_table_arn

        # Create tag set from tag specifications
        tag_set = []
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tag_set.append(Tag(key=key, value=value))

        # Create association object
        association = LocalGatewayRouteTableVpcAssociation()
        association.local_gateway_id = local_gateway_route_table.local_gateway_id
        association.local_gateway_route_table_arn = local_gateway_route_table_arn
        association.local_gateway_route_table_id = local_gateway_route_table_id
        association.local_gateway_route_table_vpc_association_id = association_id
        association.owner_id = self.get_owner_id()
        association.state = "available"
        association.tag_set = tag_set
        association.vpc_id = vpc_id

        # Store association in state resources
        self.state.resources[association_id] = association

        return {
            "localGatewayRouteTableVpcAssociation": association.to_dict(),
            "requestId": request_id,
        }

    def create_local_gateway_virtual_interface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        required_params = [
            "LocalAddress",
            "LocalGatewayVirtualInterfaceGroupId",
            "OutpostLagId",
            "PeerAddress",
            "Vlan",
        ]
        for param in required_params:
            if not params.get(param):
                raise Exception(f"Missing required parameter: {param}")

        # DryRun check
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate LocalGatewayVirtualInterfaceGroupId exists
        group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        group = self.state.local_gateway_virtual_interface_groups.get(group_id)
        if not group:
            raise Exception(f"Invalid LocalGatewayVirtualInterfaceGroupId: {group_id}")

        # Validate OutpostLagId exists
        outpost_lag_id = params.get("OutpostLagId")
        outpost_lag = self.state.outpost_lags.get(outpost_lag_id)
        if not outpost_lag:
            raise Exception(f"Invalid OutpostLagId: {outpost_lag_id}")

        # Generate unique ID for the virtual interface
        local_gateway_virtual_interface_id = self.generate_unique_id(prefix="lgvi-")

        # Owner ID
        owner_id = self.get_owner_id()

        # Compose ARN (simplified)
        local_gateway_virtual_interface_arn = f"arn:aws:ec2:{owner_id}:local-gateway-virtual-interface/{local_gateway_virtual_interface_id}"

        # Compose local gateway ID from group if available
        local_gateway_id = group.get("localGatewayId")

        # Compose tag set from TagSpecification.N if provided
        tag_set = []
        tag_specifications = []
        # TagSpecification.N is an array of TagSpecification objects
        # Each TagSpecification has ResourceType and Tags (array of Key/Value)
        for key in params:
            if key.startswith("TagSpecification."):
                tag_specifications.append(params[key])
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and not key.lower().startswith("aws:"):
                    tag_set.append({"Key": key, "Value": value})

        # Compose the virtual interface object
        local_gateway_virtual_interface = {
            "configurationState": "available",
            "localAddress": params.get("LocalAddress"),
            "localBgpAsn": group.get("localBgpAsn"),
            "localGatewayId": local_gateway_id,
            "localGatewayVirtualInterfaceArn": local_gateway_virtual_interface_arn,
            "localGatewayVirtualInterfaceGroupId": group_id,
            "localGatewayVirtualInterfaceId": local_gateway_virtual_interface_id,
            "outpostLagId": outpost_lag_id,
            "ownerId": owner_id,
            "peerAddress": params.get("PeerAddress"),
            "peerBgpAsn": params.get("PeerBgpAsn"),
            "peerBgpAsnExtended": params.get("PeerBgpAsnExtended"),
            "tagSet": tag_set,
            "vlan": params.get("Vlan"),
        }

        # Store the virtual interface in state
        self.state.local_gateway_virtual_interfaces[local_gateway_virtual_interface_id] = local_gateway_virtual_interface

        # Add the virtual interface ID to the group
        if "localGatewayVirtualInterfaceIdSet" not in group:
            group["localGatewayVirtualInterfaceIdSet"] = []
        if local_gateway_virtual_interface_id not in group["localGatewayVirtualInterfaceIdSet"]:
            group["localGatewayVirtualInterfaceIdSet"].append(local_gateway_virtual_interface_id)

        # Compose response
        response = {
            "localGatewayVirtualInterface": local_gateway_virtual_interface,
            "requestId": self.generate_request_id(),
        }
        return response


    def create_local_gateway_virtual_interface_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        if not params.get("LocalGatewayId"):
            raise Exception("Missing required parameter: LocalGatewayId")

        # DryRun check
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        local_gateway_id = params.get("LocalGatewayId")

        # Validate local gateway exists
        local_gateway = self.state.local_gateways.get(local_gateway_id)
        if not local_gateway:
            raise Exception(f"Invalid LocalGatewayId: {local_gateway_id}")

        # Generate unique ID for the virtual interface group
        local_gateway_virtual_interface_group_id = self.generate_unique_id(prefix="lgvig-")

        # Owner ID
        owner_id = self.get_owner_id()

        # Compose ARN (simplified)
        local_gateway_virtual_interface_group_arn = f"arn:aws:ec2:{owner_id}:local-gateway-virtual-interface-group/{local_gateway_virtual_interface_group_id}"

        # Compose tag set from TagSpecification.N if provided
        tag_set = []
        tag_specifications = []
        for key in params:
            if key.startswith("TagSpecification."):
                tag_specifications.append(params[key])
        for tag_spec in tag_specifications:
            tags = tag_spec.get("Tags", [])
            for tag in tags:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and not key.lower().startswith("aws:"):
                    tag_set.append({"Key": key, "Value": value})

        # Compose the virtual interface group object
        local_gateway_virtual_interface_group = {
            "configurationState": "available",
            "localBgpAsn": params.get("LocalBgpAsn"),
            "localBgpAsnExtended": params.get("LocalBgpAsnExtended"),
            "localGatewayId": local_gateway_id,
            "localGatewayVirtualInterfaceGroupArn": local_gateway_virtual_interface_group_arn,
            "localGatewayVirtualInterfaceGroupId": local_gateway_virtual_interface_group_id,
            "localGatewayVirtualInterfaceIdSet": [],
            "ownerId": owner_id,
            "tagSet": tag_set,
        }

        # Store the virtual interface group in state
        self.state.local_gateway_virtual_interface_groups[local_gateway_virtual_interface_group_id] = local_gateway_virtual_interface_group

        # Compose response
        response = {
            "localGatewayVirtualInterfaceGroup": local_gateway_virtual_interface_group,
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_local_gateway_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        if not params.get("LocalGatewayRouteTableId"):
            raise Exception("Missing required parameter: LocalGatewayRouteTableId")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")

        # Validate that either DestinationCidrBlock or DestinationPrefixListId is provided but not both
        if destination_cidr_block and destination_prefix_list_id:
            raise Exception("Cannot specify both DestinationCidrBlock and DestinationPrefixListId")

        if not destination_cidr_block and not destination_prefix_list_id:
            raise Exception("Must specify either DestinationCidrBlock or DestinationPrefixListId")

        # Validate local gateway route table exists
        route_table = self.state.local_gateway_route_tables.get(local_gateway_route_table_id)
        if not route_table:
            raise Exception(f"Invalid LocalGatewayRouteTableId: {local_gateway_route_table_id}")

        # Find the route to delete
        route_to_delete = None
        for route_id, route in self.state.local_gateway_routes.items():
            if route.get("localGatewayRouteTableId") == local_gateway_route_table_id:
                if destination_cidr_block and route.get("destinationCidrBlock") == destination_cidr_block:
                    route_to_delete = route
                    break
                if destination_prefix_list_id and route.get("destinationPrefixListId") == destination_prefix_list_id:
                    route_to_delete = route
                    break

        if not route_to_delete:
            # Route not found, return empty route info
            route_to_delete = {
                "coipPoolId": None,
                "destinationCidrBlock": destination_cidr_block,
                "destinationPrefixListId": destination_prefix_list_id,
                "localGatewayRouteTableArn": route_table.get("localGatewayRouteTableArn"),
                "localGatewayRouteTableId": local_gateway_route_table_id,
                "localGatewayVirtualInterfaceGroupId": None,
                "networkInterfaceId": None,
                "ownerId": self.get_owner_id(),
                "state": None,
                "subnetId": None,
                "type": None,
            }
        else:
            # Remove route from state
            route_id_to_remove = None
            for rid, r in self.state.local_gateway_routes.items():
                if r == route_to_delete:
                    route_id_to_remove = rid
                    break
            if route_id_to_remove:
                del self.state.local_gateway_routes[route_id_to_remove]

        response = {
            "requestId": self.generate_request_id(),
            "route": route_to_delete,
        }
        return response


    def delete_local_gateway_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        if not params.get("LocalGatewayRouteTableId"):
            raise Exception("Missing required parameter: LocalGatewayRouteTableId")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")

        # Validate local gateway route table exists
        route_table = self.state.local_gateway_route_tables.get(local_gateway_route_table_id)
        if not route_table:
            raise Exception(f"Invalid LocalGatewayRouteTableId: {local_gateway_route_table_id}")

        # Remove the route table from state
        del self.state.local_gateway_route_tables[local_gateway_route_table_id]

        # Compose response
        response = {
            "localGatewayRouteTable": route_table,
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_local_gateway_route_table_virtual_interface_group_association(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        if not params.get("LocalGatewayRouteTableVirtualInterfaceGroupAssociationId"):
            raise Exception("Missing required parameter: LocalGatewayRouteTableVirtualInterfaceGroupAssociationId")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        association_id = params.get("LocalGatewayRouteTableVirtualInterfaceGroupAssociationId")

        # Validate association exists
        association = self.state.local_gateway_route_table_virtual_interface_group_associations.get(association_id)
        if not association:
            raise Exception(f"Invalid LocalGatewayRouteTableVirtualInterfaceGroupAssociationId: {association_id}")

        # Remove association from state
        del self.state.local_gateway_route_table_virtual_interface_group_associations[association_id]

        # Compose response
        response = {
            "localGatewayRouteTableVirtualInterfaceGroupAssociation": association,
            "requestId": self.generate_request_id(),
        }
        return response

    def delete_local_gateway_route_table_vpc_association(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        association_id = params.get("LocalGatewayRouteTableVpcAssociationId")
        if not association_id:
            raise Exception("Missing required parameter LocalGatewayRouteTableVpcAssociationId")

        association = self.state.local_gateway_route_table_vpc_associations.get(association_id)
        if not association:
            # According to AWS behavior, if resource not found, raise error
            raise Exception(f"LocalGatewayRouteTableVpcAssociationId {association_id} not found")

        if dry_run:
            # Check permissions simulation
            # For emulator, assume permission granted
            raise Exception("DryRunOperation")

        # Delete the association
        del self.state.local_gateway_route_table_vpc_associations[association_id]

        response = {
            "localGatewayRouteTableVpcAssociation": {
                "localGatewayId": association.get("localGatewayId"),
                "localGatewayRouteTableArn": association.get("localGatewayRouteTableArn"),
                "localGatewayRouteTableId": association.get("localGatewayRouteTableId"),
                "localGatewayRouteTableVpcAssociationId": association.get("localGatewayRouteTableVpcAssociationId"),
                "ownerId": association.get("ownerId"),
                "state": "deleted",
                "tagSet": association.get("tagSet", []),
                "vpcId": association.get("vpcId"),
            },
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_local_gateway_virtual_interface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        interface_id = params.get("LocalGatewayVirtualInterfaceId")
        if not interface_id:
            raise Exception("Missing required parameter LocalGatewayVirtualInterfaceId")

        interface = self.state.local_gateway_virtual_interfaces.get(interface_id)
        if not interface:
            raise Exception(f"LocalGatewayVirtualInterfaceId {interface_id} not found")

        if dry_run:
            raise Exception("DryRunOperation")

        # Mark interface as deleted and remove from state
        deleted_interface = interface.copy()
        deleted_interface["configurationState"] = "deleted"
        del self.state.local_gateway_virtual_interfaces[interface_id]

        response = {
            "localGatewayVirtualInterface": {
                "configurationState": deleted_interface.get("configurationState"),
                "localAddress": deleted_interface.get("localAddress"),
                "localBgpAsn": deleted_interface.get("localBgpAsn"),
                "localGatewayId": deleted_interface.get("localGatewayId"),
                "localGatewayVirtualInterfaceArn": deleted_interface.get("localGatewayVirtualInterfaceArn"),
                "localGatewayVirtualInterfaceGroupId": deleted_interface.get("localGatewayVirtualInterfaceGroupId"),
                "localGatewayVirtualInterfaceId": deleted_interface.get("localGatewayVirtualInterfaceId"),
                "outpostLagId": deleted_interface.get("outpostLagId"),
                "ownerId": deleted_interface.get("ownerId"),
                "peerAddress": deleted_interface.get("peerAddress"),
                "peerBgpAsn": deleted_interface.get("peerBgpAsn"),
                "peerBgpAsnExtended": deleted_interface.get("peerBgpAsnExtended"),
                "tagSet": deleted_interface.get("tagSet", []),
                "vlan": deleted_interface.get("vlan"),
            },
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_local_gateway_virtual_interface_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        if not group_id:
            raise Exception("Missing required parameter LocalGatewayVirtualInterfaceGroupId")

        group = self.state.local_gateway_virtual_interface_groups.get(group_id)
        if not group:
            raise Exception(f"LocalGatewayVirtualInterfaceGroupId {group_id} not found")

        if dry_run:
            raise Exception("DryRunOperation")

        # Mark group as deleted and remove from state
        deleted_group = group.copy()
        deleted_group["configurationState"] = "deleted"
        del self.state.local_gateway_virtual_interface_groups[group_id]

        response = {
            "localGatewayVirtualInterfaceGroup": {
                "configurationState": deleted_group.get("configurationState"),
                "localBgpAsn": deleted_group.get("localBgpAsn"),
                "localBgpAsnExtended": deleted_group.get("localBgpAsnExtended"),
                "localGatewayId": deleted_group.get("localGatewayId"),
                "localGatewayVirtualInterfaceGroupArn": deleted_group.get("localGatewayVirtualInterfaceGroupArn"),
                "localGatewayVirtualInterfaceGroupId": deleted_group.get("localGatewayVirtualInterfaceGroupId"),
                "localGatewayVirtualInterfaceIdSet": deleted_group.get("localGatewayVirtualInterfaceIdSet", []),
                "ownerId": deleted_group.get("ownerId"),
                "tagSet": deleted_group.get("tagSet", []),
            },
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_local_gateway_route_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        route_table_ids = params.get("LocalGatewayRouteTableId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            raise Exception("DryRunOperation")

        # Collect all route tables
        all_route_tables = list(self.state.local_gateway_route_tables.values())

        # Filter by IDs if provided
        if route_table_ids:
            all_route_tables = [rt for rt in all_route_tables if rt.get("localGatewayRouteTableId") in route_table_ids]

        # Apply filters if provided
        def match_filter(rt, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to route table keys or special handling
            if name == "local-gateway-id":
                return rt.get("localGatewayId") in values
            if name == "local-gateway-route-table-arn":
                return rt.get("localGatewayRouteTableArn") in values
            if name == "local-gateway-route-table-id":
                return rt.get("localGatewayRouteTableId") in values
            if name == "outpost-arn":
                return rt.get("outpostArn") in values
            if name == "owner-id":
                return rt.get("ownerId") in values
            if name == "state":
                return rt.get("state") in values
            return True

        if filters:
            filtered_route_tables = []
            for rt in all_route_tables:
                if all(match_filter(rt, f) for f in filters):
                    filtered_route_tables.append(rt)
            all_route_tables = filtered_route_tables

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        paged_route_tables = all_route_tables[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(all_route_tables):
            new_next_token = str(start_index + max_results)

        response = {
            "localGatewayRouteTableSet": paged_route_tables,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_local_gateway_route_table_virtual_interface_group_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        association_ids = params.get("LocalGatewayRouteTableVirtualInterfaceGroupAssociationId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            raise Exception("DryRunOperation")

        all_associations = list(self.state.local_gateway_route_table_virtual_interface_group_associations.values())

        # Filter by IDs if provided
        if association_ids:
            all_associations = [assoc for assoc in all_associations if assoc.get("localGatewayRouteTableVirtualInterfaceGroupAssociationId") in association_ids]

        # Apply filters
        def match_filter(assoc, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "local-gateway-id":
                return assoc.get("localGatewayId") in values
            if name == "local-gateway-route-table-arn":
                return assoc.get("localGatewayRouteTableArn") in values
            if name == "local-gateway-route-table-id":
                return assoc.get("localGatewayRouteTableId") in values
            if name == "local-gateway-route-table-virtual-interface-group-association-id":
                return assoc.get("localGatewayRouteTableVirtualInterfaceGroupAssociationId") in values
            if name == "local-gateway-route-table-virtual-interface-group-id":
                return assoc.get("localGatewayVirtualInterfaceGroupId") in values
            if name == "owner-id":
                return assoc.get("ownerId") in values
            if name == "state":
                return assoc.get("state") in values
            return True

        if filters:
            filtered_associations = []
            for assoc in all_associations:
                if all(match_filter(assoc, f) for f in filters):
                    filtered_associations.append(assoc)
            all_associations = filtered_associations

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        paged_associations = all_associations[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(all_associations):
            new_next_token = str(start_index + max_results)

        response = {
            "localGatewayRouteTableVirtualInterfaceGroupAssociationSet": paged_associations,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response

    def describe_local_gateway_route_table_vpc_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        association_ids = params.get("LocalGatewayRouteTableVpcAssociationId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # DryRun check
        if dry_run:
            # Assume permission granted for emulator
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Collect all associations from state
        all_associations = list(self.state.local_gateway_route_table_vpc_associations.values())

        # Filter by association IDs if provided
        if association_ids:
            all_associations = [assoc for assoc in all_associations if assoc.local_gateway_route_table_vpc_association_id in association_ids]

        # Apply filters if provided
        def match_filter(assoc, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to association attributes
            if name == "local-gateway-id":
                return assoc.local_gateway_id in values
            elif name == "local-gateway-route-table-arn":
                return assoc.local_gateway_route_table_arn in values
            elif name == "local-gateway-route-table-id":
                return assoc.local_gateway_route_table_id in values
            elif name == "local-gateway-route-table-vpc-association-id":
                return assoc.local_gateway_route_table_vpc_association_id in values
            elif name == "owner-id":
                return assoc.owner_id in values
            elif name == "state":
                return assoc.state in values
            elif name == "vpc-id":
                return assoc.vpc_id in values
            return True

        if filters:
            filtered_associations = []
            for assoc in all_associations:
                if all(match_filter(assoc, f) for f in filters):
                    filtered_associations.append(assoc)
            all_associations = filtered_associations

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        paged_associations = all_associations[start_index : start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_associations) else None

        # Build response
        response_associations = []
        for assoc in paged_associations:
            tag_set = []
            if assoc.tags:
                for k, v in assoc.tags.items():
                    tag_set.append({"Key": k, "Value": v})
            response_associations.append({
                "localGatewayId": assoc.local_gateway_id,
                "localGatewayRouteTableArn": assoc.local_gateway_route_table_arn,
                "localGatewayRouteTableId": assoc.local_gateway_route_table_id,
                "localGatewayRouteTableVpcAssociationId": assoc.local_gateway_route_table_vpc_association_id,
                "ownerId": assoc.owner_id,
                "state": assoc.state,
                "tagSet": tag_set,
                "vpcId": assoc.vpc_id,
            })

        return {
            "localGatewayRouteTableVpcAssociationSet": response_associations,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_local_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        local_gateway_ids = params.get("LocalGatewayId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # DryRun check
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        all_local_gateways = list(self.state.local_gateways.values())

        # Filter by IDs if provided
        if local_gateway_ids:
            all_local_gateways = [lgw for lgw in all_local_gateways if lgw.local_gateway_id in local_gateway_ids]

        # Apply filters
        def match_filter(lgw, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "local-gateway-id":
                return lgw.local_gateway_id in values
            elif name == "outpost-arn":
                return lgw.outpost_arn in values
            elif name == "owner-id":
                return lgw.owner_id in values
            elif name == "state":
                return lgw.state in values
            return True

        if filters:
            filtered_lgws = []
            for lgw in all_local_gateways:
                if all(match_filter(lgw, f) for f in filters):
                    filtered_lgws.append(lgw)
            all_local_gateways = filtered_lgws

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        paged_lgws = all_local_gateways[start_index : start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_local_gateways) else None

        response_lgws = []
        for lgw in paged_lgws:
            tag_set = []
            if lgw.tags:
                for k, v in lgw.tags.items():
                    tag_set.append({"Key": k, "Value": v})
            response_lgws.append({
                "localGatewayId": lgw.local_gateway_id,
                "outpostArn": lgw.outpost_arn,
                "ownerId": lgw.owner_id,
                "state": lgw.state,
                "tagSet": tag_set,
            })

        return {
            "localGatewaySet": response_lgws,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_local_gateway_virtual_interface_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        group_ids = params.get("LocalGatewayVirtualInterfaceGroupId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        all_groups = list(self.state.local_gateway_virtual_interface_groups.values())

        if group_ids:
            all_groups = [g for g in all_groups if g.local_gateway_virtual_interface_group_id in group_ids]

        def match_filter(group, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "local-gateway-id":
                return group.local_gateway_id in values
            elif name == "local-gateway-virtual-interface-group-id":
                return group.local_gateway_virtual_interface_group_id in values
            elif name == "local-gateway-virtual-interface-id":
                # group.local_gateway_virtual_interface_id_set is list of strings
                return any(vif_id in values for vif_id in group.local_gateway_virtual_interface_id_set)
            elif name == "owner-id":
                return group.owner_id in values
            return True

        if filters:
            filtered_groups = []
            for group in all_groups:
                if all(match_filter(group, f) for f in filters):
                    filtered_groups.append(group)
            all_groups = filtered_groups

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        paged_groups = all_groups[start_index : start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_groups) else None

        response_groups = []
        for group in paged_groups:
            tag_set = []
            if group.tags:
                for k, v in group.tags.items():
                    tag_set.append({"Key": k, "Value": v})
            response_groups.append({
                "configurationState": group.configuration_state,
                "localBgpAsn": group.local_bgp_asn,
                "localBgpAsnExtended": group.local_bgp_asn_extended,
                "localGatewayId": group.local_gateway_id,
                "localGatewayVirtualInterfaceGroupArn": group.local_gateway_virtual_interface_group_arn,
                "localGatewayVirtualInterfaceGroupId": group.local_gateway_virtual_interface_group_id,
                "localGatewayVirtualInterfaceIdSet": group.local_gateway_virtual_interface_id_set,
                "ownerId": group.owner_id,
                "tagSet": tag_set,
            })

        return {
            "localGatewayVirtualInterfaceGroupSet": response_groups,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_local_gateway_virtual_interfaces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        interface_ids = params.get("LocalGatewayVirtualInterfaceId.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        all_interfaces = list(self.state.local_gateway_virtual_interfaces.values())

        if interface_ids:
            all_interfaces = [iface for iface in all_interfaces if iface.local_gateway_virtual_interface_id in interface_ids]

        def match_filter(iface, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "local-address":
                return iface.local_address in values
            elif name == "local-bgp-asn":
                return str(iface.local_bgp_asn) in values
            elif name == "local-gateway-id":
                return iface.local_gateway_id in values
            elif name == "local-gateway-virtual-interface-id":
                return iface.local_gateway_virtual_interface_id in values
            elif name == "owner-id":
                return iface.owner_id in values
            elif name == "peer-address":
                return iface.peer_address in values
            elif name == "peer-bgp-asn":
                return str(iface.peer_bgp_asn) in values
            elif name == "vlan":
                return str(iface.vlan) in values
            return True

        if filters:
            filtered_ifaces = []
            for iface in all_interfaces:
                if all(match_filter(iface, f) for f in filters):
                    filtered_ifaces.append(iface)
            all_interfaces = filtered_ifaces

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        paged_ifaces = all_interfaces[start_index : start_index + max_results]
        new_next_token = str(start_index + max_results) if start_index + max_results < len(all_interfaces) else None

        response_ifaces = []
        for iface in paged_ifaces:
            tag_set = []
            if iface.tags:
                for k, v in iface.tags.items():
                    tag_set.append({"Key": k, "Value": v})
            response_ifaces.append({
                "configurationState": iface.configuration_state,
                "localAddress": iface.local_address,
                "localBgpAsn": iface.local_bgp_asn,
                "localGatewayId": iface.local_gateway_id,
                "localGatewayVirtualInterfaceArn": iface.local_gateway_virtual_interface_arn,
                "localGatewayVirtualInterfaceGroupId": iface.local_gateway_virtual_interface_group_id,
                "localGatewayVirtualInterfaceId": iface.local_gateway_virtual_interface_id,
                "outpostLagId": iface.outpost_lag_id,
                "ownerId": iface.owner_id,
                "peerAddress": iface.peer_address,
                "peerBgpAsn": iface.peer_bgp_asn,
                "peerBgpAsnExtended": iface.peer_bgp_asn_extended,
                "tagSet": tag_set,
                "vlan": iface.vlan,
            })

        return {
            "localGatewayVirtualInterfaceSet": response_ifaces,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def modify_local_gateway_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_prefix_list_id = params.get("DestinationPrefixListId")
        dry_run = params.get("DryRun", False)
        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        local_gateway_virtual_interface_group_id = params.get("LocalGatewayVirtualInterfaceGroupId")
        network_interface_id = params.get("NetworkInterfaceId")

        # Validate required parameter
        if not local_gateway_route_table_id:
            raise Exception("Missing required parameter LocalGatewayRouteTableId")

        # Validate mutually exclusive parameters
        if destination_cidr_block and destination_prefix_list_id:
            raise Exception("Cannot specify both DestinationCidrBlock and DestinationPrefixListId")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Find the route table
        route_table = self.state.local_gateway_route_tables.get(local_gateway_route_table_id)
        if not route_table:
            raise Exception(f"LocalGatewayRouteTable {local_gateway_route_table_id} not found")

        # Find the route to modify
        # The route must match either destination_cidr_block or destination_prefix_list_id
        route_to_modify = None
        for route in route_table.routes:
            if destination_cidr_block and route.destination_cidr_block == destination_cidr_block:
                route_to_modify = route
                break
            if destination_prefix_list_id and route.destination_prefix_list_id == destination_prefix_list_id:
                route_to_modify = route
                break

        if not route_to_modify:
            raise Exception("No matching route found to modify")

        # Modify the route fields if provided
        if local_gateway_virtual_interface_group_id is not None:
            route_to_modify.local_gateway_virtual_interface_group_id = local_gateway_virtual_interface_group_id
        if network_interface_id is not None:
            route_to_modify.network_interface_id = network_interface_id

        # Build response route dict
        tag_set = []
        if hasattr(route_to_modify, "tags") and route_to_modify.tags:
            for k, v in route_to_modify.tags.items():
                tag_set.append({"Key": k, "Value": v})

        response_route = {
            "coipPoolId": getattr(route_to_modify, "coip_pool_id", None),
            "destinationCidrBlock": getattr(route_to_modify, "destination_cidr_block", None),
            "destinationPrefixListId": getattr(route_to_modify, "destination_prefix_list_id", None),
            "localGatewayRouteTableArn": getattr(route_to_modify, "local_gateway_route_table_arn", None),
            "localGatewayRouteTableId": getattr(route_to_modify, "local_gateway_route_table_id", None),
            "localGatewayVirtualInterfaceGroupId": getattr(route_to_modify, "local_gateway_virtual_interface_group_id", None),
            "networkInterfaceId": getattr(route_to_modify, "network_interface_id", None),
            "ownerId": getattr(route_to_modify, "owner_id", None),
            "state": getattr(route_to_modify, "state", None),
            "subnetId": getattr(route_to_modify, "subnet_id", None),
            "type": getattr(route_to_modify, "type", None),
        }

        return {
            "requestId": self.generate_request_id(),
            "route": response_route,
        }

    def search_local_gateway_routes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        if not local_gateway_route_table_id:
            raise ValueError("LocalGatewayRouteTableId is required")

        # Validate MaxResults if provided
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int) or max_results <= 0:
                raise ValueError("MaxResults must be a positive integer")

        next_token = params.get("NextToken")

        # DryRun check
        dry_run = params.get("DryRun", False)
        if dry_run:
            # Check permissions - for emulator, assume always allowed
            # Return DryRunOperation error if not allowed, else raise exception
            # Here we simulate allowed
            raise Exception("DryRunOperation")

        # Retrieve the local gateway route table
        route_table = self.state.local_gateways.get(local_gateway_route_table_id)
        if route_table is None:
            # AWS returns InvalidLocalGatewayRouteTableID.NotFound error, here raise ValueError
            raise ValueError(f"LocalGatewayRouteTableId {local_gateway_route_table_id} not found")

        # The routes are stored in route_table['routes'] or similar, but we must check structure
        # Assume route_table has attribute or key 'routes' which is a dict of route_id -> route_obj
        # If not, fallback to empty list
        routes = []
        if isinstance(route_table, dict):
            # Try keys 'routes' or 'routeSet'
            if "routes" in route_table:
                routes = list(route_table["routes"].values()) if isinstance(route_table["routes"], dict) else list(route_table["routes"])
            elif "routeSet" in route_table:
                routes = list(route_table["routeSet"].values()) if isinstance(route_table["routeSet"], dict) else list(route_table["routeSet"])
            else:
                # fallback: try to find routes in state.resources by filtering local gateway route table id
                routes = []
                for r in self.state.resources.values():
                    if isinstance(r, dict) and r.get("localGatewayRouteTableId") == local_gateway_route_table_id:
                        routes.append(r)
        else:
            routes = []

        # Parse filters
        filters = params.get("Filter.N", [])
        # Filters is expected to be a list of dicts with keys "Name" and "Values"
        # If single filter dict is passed, convert to list
        if isinstance(filters, dict):
            filters = [filters]
        elif filters is None:
            filters = []

        def route_matches_filter(route, filter):
            name = filter.get("Name")
            values = filter.get("Values", [])
            if not name or not values:
                return True  # no filter or empty values means no filtering on this filter

            # Implement filter logic based on filter name
            # Supported filters from doc:
            # prefix-list-id, route-search.exact-match, route-search.longest-prefix-match,
            # route-search.subnet-of-match, route-search.supernet-of-match, state, type

            # Helper for CIDR matching
            import ipaddress

            def cidr_match_exact(route_cidr, filter_cidr):
                return route_cidr == filter_cidr

            def cidr_match_longest_prefix(route_cidr, filter_cidr):
                # longest prefix match means route_cidr is the longest prefix that matches filter_cidr
                # i.e. filter_cidr is subnet of route_cidr
                try:
                    route_net = ipaddress.ip_network(route_cidr)
                    filter_net = ipaddress.ip_network(filter_cidr)
                    return filter_net.subnet_of(route_net)
                except Exception:
                    return False

            def cidr_match_subnet_of(route_cidr, filter_cidr):
                # route_cidr is subnet of filter_cidr
                try:
                    route_net = ipaddress.ip_network(route_cidr)
                    filter_net = ipaddress.ip_network(filter_cidr)
                    return route_net.subnet_of(filter_net)
                except Exception:
                    return False

            def cidr_match_supernet_of(route_cidr, filter_cidr):
                # route_cidr is supernet of filter_cidr
                try:
                    route_net = ipaddress.ip_network(route_cidr)
                    filter_net = ipaddress.ip_network(filter_cidr)
                    return route_net.supernet_of(filter_net)
                except Exception:
                    return False

            # Now check each filter name
            if name == "prefix-list-id":
                # route.destinationPrefixListId must be in values
                return route.get("destinationPrefixListId") in values
            elif name == "route-search.exact-match":
                # exact match of route destinationCidrBlock or destinationPrefixListId
                # check if any value matches exactly destinationCidrBlock or destinationPrefixListId
                for val in values:
                    if val == route.get("destinationCidrBlock") or val == route.get("destinationPrefixListId"):
                        return True
                return False
            elif name == "route-search.longest-prefix-match":
                # The longest prefix that matches the route
                # We interpret as route destinationCidrBlock is supernet of filter value
                for val in values:
                    if route.get("destinationCidrBlock") and cidr_match_longest_prefix(route.get("destinationCidrBlock"), val):
                        return True
                return False
            elif name == "route-search.subnet-of-match":
                # routes with subnet that match the specified CIDR filter
                for val in values:
                    if route.get("destinationCidrBlock") and cidr_match_subnet_of(route.get("destinationCidrBlock"), val):
                        return True
                return False
            elif name == "route-search.supernet-of-match":
                # routes with CIDR that encompass the CIDR filter
                for val in values:
                    if route.get("destinationCidrBlock") and cidr_match_supernet_of(route.get("destinationCidrBlock"), val):
                        return True
                return False
            elif name == "state":
                # route.state in values (case sensitive)
                return route.get("state") in values
            elif name == "type":
                # route.type in values (case sensitive)
                return route.get("type") in values
            else:
                # Unknown filter, ignore (AWS ignores unknown filters)
                return True

        # Filter routes
        filtered_routes = []
        for route in routes:
            if all(route_matches_filter(route, f) for f in filters):
                filtered_routes.append(route)

        # Pagination
        # next_token is expected to be a string token representing an index offset
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index >= len(filtered_routes):
                    start_index = 0
            except Exception:
                start_index = 0

        end_index = len(filtered_routes)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_routes))

        page_routes = filtered_routes[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(filtered_routes):
            new_next_token = str(end_index)

        # Compose response routeSet
        # Each route is a dict with keys as per LocalGatewayRoute object
        # We must include keys: coipPoolId, destinationCidrBlock, destinationPrefixListId,
        # localGatewayRouteTableArn, localGatewayRouteTableId, localGatewayVirtualInterfaceGroupId,
        # networkInterfaceId, ownerId, state, subnetId, type
        # Some may be missing, fill with None or omit

        route_set = []
        for r in page_routes:
            route_set.append({
                "coipPoolId": r.get("coipPoolId"),
                "destinationCidrBlock": r.get("destinationCidrBlock"),
                "destinationPrefixListId": r.get("destinationPrefixListId"),
                "localGatewayRouteTableArn": r.get("localGatewayRouteTableArn"),
                "localGatewayRouteTableId": r.get("localGatewayRouteTableId"),
                "localGatewayVirtualInterfaceGroupId": r.get("localGatewayVirtualInterfaceGroupId"),
                "networkInterfaceId": r.get("networkInterfaceId"),
                "ownerId": r.get("ownerId"),
                "state": r.get("state"),
                "subnetId": r.get("subnetId"),
                "type": r.get("type"),
            })

        response = {
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "routeSet": route_set,
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class LocalGatewaysGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateLocalGatewayRoute", self.create_local_gateway_route)
        self.register_action("CreateLocalGatewayRouteTable", self.create_local_gateway_route_table)
        self.register_action("CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociation", self.create_local_gateway_route_table_virtual_interface_group_association)
        self.register_action("CreateLocalGatewayVirtualInterface", self.create_local_gateway_virtual_interface)
        self.register_action("CreateLocalGatewayRouteTableVpcAssociation", self.create_local_gateway_route_table_vpc_association)
        self.register_action("CreateLocalGatewayVirtualInterface", self.create_local_gateway_virtual_interface)
        self.register_action("CreateLocalGatewayVirtualInterfaceGroup", self.create_local_gateway_virtual_interface_group)
        self.register_action("DeleteLocalGatewayRoute", self.delete_local_gateway_route)
        self.register_action("DeleteLocalGatewayRouteTable", self.delete_local_gateway_route_table)
        self.register_action("DeleteLocalGatewayRouteTableVirtualInterfaceGroupAssociation", self.delete_local_gateway_route_table_virtual_interface_group_association)
        self.register_action("DeleteLocalGatewayRouteTableVpcAssociation", self.delete_local_gateway_route_table_vpc_association)
        self.register_action("DeleteLocalGatewayVirtualInterface", self.delete_local_gateway_virtual_interface)
        self.register_action("DeleteLocalGatewayVirtualInterfaceGroup", self.delete_local_gateway_virtual_interface_group)
        self.register_action("DescribeLocalGatewayRouteTables", self.describe_local_gateway_route_tables)
        self.register_action("DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociations", self.describe_local_gateway_route_table_virtual_interface_group_associations)
        self.register_action("DescribeLocalGatewayRouteTableVpcAssociations", self.describe_local_gateway_route_table_vpc_associations)
        self.register_action("DescribeLocalGateways", self.describe_local_gateways)
        self.register_action("DescribeLocalGatewayVirtualInterfaceGroups", self.describe_local_gateway_virtual_interface_groups)
        self.register_action("DescribeLocalGatewayVirtualInterfaces", self.describe_local_gateway_virtual_interfaces)
        self.register_action("ModifyLocalGatewayRoute", self.modify_local_gateway_route)
        self.register_action("SearchLocalGatewayRoutes", self.search_local_gateway_routes)

    def create_local_gateway_route(self, params):
        return self.backend.create_local_gateway_route(params)

    def create_local_gateway_route_table(self, params):
        return self.backend.create_local_gateway_route_table(params)

    def create_local_gateway_route_table_virtual_interface_group_association(self, params):
        return self.backend.create_local_gateway_route_table_virtual_interface_group_association(params)

    def create_local_gateway_virtual_interface(self, params):
        return self.backend.create_local_gateway_virtual_interface(params)

    def create_local_gateway_route_table_vpc_association(self, params):
        return self.backend.create_local_gateway_route_table_vpc_association(params)

    def create_local_gateway_virtual_interface(self, params):
        return self.backend.create_local_gateway_virtual_interface(params)

    def create_local_gateway_virtual_interface_group(self, params):
        return self.backend.create_local_gateway_virtual_interface_group(params)

    def delete_local_gateway_route(self, params):
        return self.backend.delete_local_gateway_route(params)

    def delete_local_gateway_route_table(self, params):
        return self.backend.delete_local_gateway_route_table(params)

    def delete_local_gateway_route_table_virtual_interface_group_association(self, params):
        return self.backend.delete_local_gateway_route_table_virtual_interface_group_association(params)

    def delete_local_gateway_route_table_vpc_association(self, params):
        return self.backend.delete_local_gateway_route_table_vpc_association(params)

    def delete_local_gateway_virtual_interface(self, params):
        return self.backend.delete_local_gateway_virtual_interface(params)

    def delete_local_gateway_virtual_interface_group(self, params):
        return self.backend.delete_local_gateway_virtual_interface_group(params)

    def describe_local_gateway_route_tables(self, params):
        return self.backend.describe_local_gateway_route_tables(params)

    def describe_local_gateway_route_table_virtual_interface_group_associations(self, params):
        return self.backend.describe_local_gateway_route_table_virtual_interface_group_associations(params)

    def describe_local_gateway_route_table_vpc_associations(self, params):
        return self.backend.describe_local_gateway_route_table_vpc_associations(params)

    def describe_local_gateways(self, params):
        return self.backend.describe_local_gateways(params)

    def describe_local_gateway_virtual_interface_groups(self, params):
        return self.backend.describe_local_gateway_virtual_interface_groups(params)

    def describe_local_gateway_virtual_interfaces(self, params):
        return self.backend.describe_local_gateway_virtual_interfaces(params)

    def modify_local_gateway_route(self, params):
        return self.backend.modify_local_gateway_route(params)

    def search_local_gateway_routes(self, params):
        return self.backend.search_local_gateway_routes(params)
