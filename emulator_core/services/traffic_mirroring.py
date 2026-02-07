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
class TagSpecification:
    resource_type: str
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


class RuleAction(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"


class TrafficDirection(str, Enum):
    INGRESS = "ingress"
    EGRESS = "egress"


class TrafficMirrorTargetType(str, Enum):
    NETWORK_INTERFACE = "network-interface"
    NETWORK_LOAD_BALANCER = "network-load-balancer"
    GATEWAY_LOAD_BALANCER_ENDPOINT = "gateway-load-balancer-endpoint"


@dataclass
class TrafficMirrorPortRange:
    from_port: Optional[int] = None
    to_port: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.from_port is not None:
            d["FromPort"] = self.from_port
        if self.to_port is not None:
            d["ToPort"] = self.to_port
        return d


@dataclass
class TrafficMirrorFilterRule:
    traffic_mirror_filter_rule_id: str
    traffic_mirror_filter_id: str
    rule_number: Optional[int] = None
    rule_action: Optional[RuleAction] = None
    direction: Optional[TrafficDirection] = None
    source_cidr_block: Optional[str] = None
    destination_cidr_block: Optional[str] = None
    source_port_range: Optional[TrafficMirrorPortRange] = None
    destination_port_range: Optional[TrafficMirrorPortRange] = None
    protocol: Optional[int] = None
    description: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TrafficMirrorFilterRuleId": self.traffic_mirror_filter_rule_id,
            "TrafficMirrorFilterId": self.traffic_mirror_filter_id,
            "RuleNumber": self.rule_number,
            "RuleAction": self.rule_action.value if self.rule_action else None,
            "TrafficDirection": self.direction.value if self.direction else None,
            "SourceCidrBlock": self.source_cidr_block,
            "DestinationCidrBlock": self.destination_cidr_block,
            "SourcePortRange": self.source_port_range.to_dict() if self.source_port_range else None,
            "DestinationPortRange": self.destination_port_range.to_dict() if self.destination_port_range else None,
            "Protocol": self.protocol,
            "Description": self.description,
            "TagSet": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class TrafficMirrorFilter:
    traffic_mirror_filter_id: str
    description: Optional[str] = None
    egress_filter_rule_set: List[TrafficMirrorFilterRule] = field(default_factory=list)
    ingress_filter_rule_set: List[TrafficMirrorFilterRule] = field(default_factory=list)
    network_service_set: List[str] = field(default_factory=list)  # e.g. ["amazon-dns"]
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TrafficMirrorFilterId": self.traffic_mirror_filter_id,
            "Description": self.description,
            "EgressFilterRuleSet": [rule.to_dict() for rule in self.egress_filter_rule_set],
            "IngressFilterRuleSet": [rule.to_dict() for rule in self.ingress_filter_rule_set],
            "NetworkServiceSet": self.network_service_set,
            "TagSet": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class TrafficMirrorTarget:
    traffic_mirror_target_id: str
    type: Optional[TrafficMirrorTargetType] = None
    description: Optional[str] = None
    network_interface_id: Optional[str] = None
    network_load_balancer_arn: Optional[str] = None
    gateway_load_balancer_endpoint_id: Optional[str] = None
    owner_id: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TrafficMirrorTargetId": self.traffic_mirror_target_id,
            "Type": self.type.value if self.type else None,
            "Description": self.description,
            "NetworkInterfaceId": self.network_interface_id,
            "NetworkLoadBalancerArn": self.network_load_balancer_arn,
            "GatewayLoadBalancerEndpointId": self.gateway_load_balancer_endpoint_id,
            "OwnerId": self.owner_id,
            "TagSet": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class TrafficMirrorSession:
    traffic_mirror_session_id: str
    traffic_mirror_filter_id: Optional[str] = None
    traffic_mirror_target_id: Optional[str] = None
    network_interface_id: Optional[str] = None
    session_number: Optional[int] = None
    virtual_network_id: Optional[int] = None
    packet_length: Optional[int] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TrafficMirrorSessionId": self.traffic_mirror_session_id,
            "TrafficMirrorFilterId": self.traffic_mirror_filter_id,
            "TrafficMirrorTargetId": self.traffic_mirror_target_id,
            "NetworkInterfaceId": self.network_interface_id,
            "SessionNumber": self.session_number,
            "VirtualNetworkId": self.virtual_network_id,
            "PacketLength": self.packet_length,
            "Description": self.description,
            "OwnerId": self.owner_id,
            "TagSet": [tag.to_dict() for tag in self.tags],
        }


class TrafficMirroringBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state.traffic_mirror_filters, self.state.traffic_mirror_filter_rules,
        # self.state.traffic_mirror_targets, self.state.traffic_mirror_sessions

    def create_traffic_mirror_filter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        description = params.get("Description")
        tag_specifications = params.get("TagSpecification.N", [])

        # Generate unique ID for the filter
        traffic_mirror_filter_id = self.generate_unique_id("tmf")

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # Only add tags if resource type is traffic-mirror-filter or not specified
            resource_type = tag_spec.get("ResourceType")
            if resource_type and resource_type != "traffic-mirror-filter":
                continue
            for tag_dict in tag_spec.get("Tags", []):
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None:
                    tags.append(Tag(key=key, value=value))

        # Create TrafficMirrorFilter object
        traffic_mirror_filter = TrafficMirrorFilter(
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            description=description,
            egress_filter_rule_set=[],
            ingress_filter_rule_set=[],
            network_service_set=[],
            tags=tags,
        )

        # Store in state
        self.state.traffic_mirroring[traffic_mirror_filter_id] = traffic_mirror_filter

        return {
            "clientToken": client_token,
            "requestId": self.generate_request_id(),
            "trafficMirrorFilter": traffic_mirror_filter.to_dict(),
        }


    def create_traffic_mirror_filter_rule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        description = params.get("Description")
        destination_cidr_block = params.get("DestinationCidrBlock")
        destination_port_range_req = params.get("DestinationPortRange")
        protocol = params.get("Protocol")
        rule_action_str = params.get("RuleAction")
        rule_number = params.get("RuleNumber")
        source_cidr_block = params.get("SourceCidrBlock")
        source_port_range_req = params.get("SourcePortRange")
        tag_specifications = params.get("TagSpecification.N", [])
        traffic_direction_str = params.get("TrafficDirection")
        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")

        # Validate required parameters
        if destination_cidr_block is None:
            raise ValueError("DestinationCidrBlock is required")
        if rule_action_str is None:
            raise ValueError("RuleAction is required")
        if rule_number is None:
            raise ValueError("RuleNumber is required")
        if source_cidr_block is None:
            raise ValueError("SourceCidrBlock is required")
        if traffic_direction_str is None:
            raise ValueError("TrafficDirection is required")
        if traffic_mirror_filter_id is None:
            raise ValueError("TrafficMirrorFilterId is required")

        # Validate traffic mirror filter exists
        traffic_mirror_filter = self.state.traffic_mirroring.get(traffic_mirror_filter_id)
        if traffic_mirror_filter is None:
            raise ValueError(f"TrafficMirrorFilter {traffic_mirror_filter_id} does not exist")

        # Validate rule_action enum
        try:
            rule_action = RuleAction(rule_action_str)
        except Exception:
            raise ValueError(f"Invalid RuleAction: {rule_action_str}")

        # Validate traffic_direction enum
        try:
            traffic_direction = TrafficDirection(traffic_direction_str)
        except Exception:
            raise ValueError(f"Invalid TrafficDirection: {traffic_direction_str}")

        # Parse port ranges
        def parse_port_range(port_range_req: Optional[Dict[str, Any]]) -> Optional[TrafficMirrorPortRange]:
            if port_range_req is None:
                return None
            from_port = port_range_req.get("FromPort")
            to_port = port_range_req.get("ToPort")
            return TrafficMirrorPortRange(from_port=from_port, to_port=to_port)

        destination_port_range = parse_port_range(destination_port_range_req)
        source_port_range = parse_port_range(source_port_range_req)

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if resource_type and resource_type != "traffic-mirror-filter-rule":
                continue
            for tag_dict in tag_spec.get("Tags", []):
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None:
                    tags.append(Tag(key=key, value=value))

        # Generate unique ID for the rule
        traffic_mirror_filter_rule_id = self.generate_unique_id("tmfr")

        # Create TrafficMirrorFilterRule object
        rule = TrafficMirrorFilterRule(
            traffic_mirror_filter_rule_id=traffic_mirror_filter_rule_id,
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            rule_number=rule_number,
            rule_action=rule_action,
            direction=traffic_direction,
            source_cidr_block=source_cidr_block,
            destination_cidr_block=destination_cidr_block,
            source_port_range=source_port_range,
            destination_port_range=destination_port_range,
            protocol=protocol,
            description=description,
            tags=tags,
        )

        # Add rule to the appropriate filter rule set
        if traffic_direction == TrafficDirection.INGRESS:
            # Check for duplicate rule number in ingress rules
            for existing_rule in traffic_mirror_filter.ingress_filter_rule_set:
                if existing_rule.rule_number == rule_number:
                    raise ValueError(f"RuleNumber {rule_number} already exists in ingress rules")
            traffic_mirror_filter.ingress_filter_rule_set.append(rule)
        else:
            # Egress
            for existing_rule in traffic_mirror_filter.egress_filter_rule_set:
                if existing_rule.rule_number == rule_number:
                    raise ValueError(f"RuleNumber {rule_number} already exists in egress rules")
            traffic_mirror_filter.egress_filter_rule_set.append(rule)

        # Update the filter in state
        self.state.traffic_mirroring[traffic_mirror_filter_id] = traffic_mirror_filter

        return {
            "clientToken": client_token,
            "requestId": self.generate_request_id(),
            "trafficMirrorFilterRule": rule.to_dict(),
        }


    def create_traffic_mirror_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        description = params.get("Description")
        network_interface_id = params.get("NetworkInterfaceId")
        packet_length = params.get("PacketLength")
        session_number = params.get("SessionNumber")
        tag_specifications = params.get("TagSpecification.N", [])
        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")
        traffic_mirror_target_id = params.get("TrafficMirrorTargetId")
        virtual_network_id = params.get("VirtualNetworkId")

        # Validate required parameters
        if network_interface_id is None:
            raise ValueError("NetworkInterfaceId is required")
        if session_number is None:
            raise ValueError("SessionNumber is required")
        if traffic_mirror_filter_id is None:
            raise ValueError("TrafficMirrorFilterId is required")
        if traffic_mirror_target_id is None:
            raise ValueError("TrafficMirrorTargetId is required")

        # Validate session_number range
        if not (1 <= session_number <= 32766):
            raise ValueError("SessionNumber must be between 1 and 32766")

        # Validate packet_length if specified
        if packet_length is not None:
            if not (1 <= packet_length <= 8500):
                raise ValueError("PacketLength must be between 1 and 8500")

        # Validate filter exists
        traffic_mirror_filter = self.state.traffic_mirroring.get(traffic_mirror_filter_id)
        if traffic_mirror_filter is None:
            raise ValueError(f"TrafficMirrorFilter {traffic_mirror_filter_id} does not exist")

        # Validate target exists
        traffic_mirror_target = self.state.traffic_mirroring.get(traffic_mirror_target_id)
        if traffic_mirror_target is None:
            raise ValueError(f"TrafficMirrorTarget {traffic_mirror_target_id} does not exist")

        # Generate unique ID for session
        traffic_mirror_session_id = self.generate_unique_id("tms")

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if resource_type and resource_type != "traffic-mirror-session":
                continue
            for tag_dict in tag_spec.get("Tags", []):
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None:
                    tags.append(Tag(key=key, value=value))

        # Owner ID
        owner_id = self.get_owner_id()

        # If virtual_network_id not specified, generate random unique
        if virtual_network_id is None:
            import random
            virtual_network_id = random.randint(1, 16777215)  # VXLAN ID range

        # Create TrafficMirrorSession object
        session = TrafficMirrorSession(
            traffic_mirror_session_id=traffic_mirror_session_id,
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            traffic_mirror_target_id=traffic_mirror_target_id,
            network_interface_id=network_interface_id,
            session_number=session_number,
            virtual_network_id=virtual_network_id,
            packet_length=packet_length,
            description=description,
            owner_id=owner_id,
            tags=tags,
        )

        # Store in state
        self.state.traffic_mirroring[traffic_mirror_session_id] = session

        return {
            "clientToken": client_token,
            "requestId": self.generate_request_id(),
            "trafficMirrorSession": session.to_dict(),
        }


    def create_traffic_mirror_target(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        description = params.get("Description")
        gateway_load_balancer_endpoint_id = params.get("GatewayLoadBalancerEndpointId")
        network_interface_id = params.get("NetworkInterfaceId")
        network_load_balancer_arn = params.get("NetworkLoadBalancerArn")
        tag_specifications = params.get("TagSpecification.N", [])

        # Validate that exactly one of the target identifiers is specified
        target_ids = [
            gateway_load_balancer_endpoint_id,
            network_interface_id,
            network_load_balancer_arn,
        ]
        specified_targets = [t for t in target_ids if t is not None]
        if len(specified_targets) != 1:
            raise ValueError("Exactly one of GatewayLoadBalancerEndpointId, NetworkInterfaceId, or NetworkLoadBalancerArn must be specified")

        # Determine type
        if network_interface_id is not None:
            target_type = TrafficMirrorTargetType.NETWORK_INTERFACE
        elif network_load_balancer_arn is not None:
            target_type = TrafficMirrorTargetType.NETWORK_LOAD_BALANCER
        else:
            target_type = TrafficMirrorTargetType.GATEWAY_LOAD_BALANCER_ENDPOINT

        # Generate unique ID for target
        traffic_mirror_target_id = self.generate_unique_id("tmt")

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if resource_type and resource_type != "traffic-mirror-target":
                continue
            for tag_dict in tag_spec.get("Tags", []):
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None:
                    tags.append(Tag(key=key, value=value))

        # Owner ID
        owner_id = self.get_owner_id()

        # Create TrafficMirrorTarget object
        target = TrafficMirrorTarget(
            traffic_mirror_target_id=traffic_mirror_target_id,
            type=target_type,
            description=description,
            network_interface_id=network_interface_id,
            network_load_balancer_arn=network_load_balancer_arn,
            gateway_load_balancer_endpoint_id=gateway_load_balancer_endpoint_id,
            owner_id=owner_id,
            tags=tags,
        )

        # Store in state
        self.state.traffic_mirroring[traffic_mirror_target_id] = target

        return {
            "clientToken": client_token,
            "requestId": self.generate_request_id(),
            "trafficMirrorTarget": target.to_dict(),
        }


    def delete_traffic_mirror_filter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")

        if traffic_mirror_filter_id is None:
            raise ValueError("TrafficMirrorFilterId is required")

        # Check if filter exists
        traffic_mirror_filter = self.state.traffic_mirroring.get(traffic_mirror_filter_id)
        if traffic_mirror_filter is None:
            raise ValueError(f"TrafficMirrorFilter {traffic_mirror_filter_id} does not exist")

        # Check if filter is in use by any session
        for resource in self.state.traffic_mirroring.values():
            if isinstance(resource, TrafficMirrorSession):
                if resource.traffic_mirror_filter_id == traffic_mirror_filter_id:
                    raise ValueError(f"TrafficMirrorFilter {traffic_mirror_filter_id} is in use by a TrafficMirrorSession and cannot be deleted")

        # Delete the filter
        del self.state.traffic_mirroring[traffic_mirror_filter_id]

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorFilterId": traffic_mirror_filter_id,
        }

    def delete_traffic_mirror_filter_rule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        traffic_mirror_filter_rule_id = params.get("TrafficMirrorFilterRuleId")
        if not traffic_mirror_filter_rule_id:
            raise ValueError("TrafficMirrorFilterRuleId is required")

        # DryRun check
        dry_run = params.get("DryRun", False)
        if dry_run:
            # In a real implementation, check permissions here
            # For emulator, assume permission granted
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Find the rule in the state
        rule = self.state.traffic_mirroring.get(traffic_mirror_filter_rule_id)
        if not rule or not isinstance(rule, TrafficMirrorFilterRule):
            # AWS returns an error if the rule does not exist, but no error specified here
            # For emulator, just return empty or raise error
            raise ValueError(f"TrafficMirrorFilterRuleId {traffic_mirror_filter_rule_id} does not exist")

        # Remove the rule from the filter's ingress or egress list
        filter_id = rule.traffic_mirror_filter_id
        if not filter_id:
            # Defensive: rule must have filter id
            raise ValueError(f"TrafficMirrorFilterRuleId {traffic_mirror_filter_rule_id} has no associated filter")

        traffic_filter = self.state.traffic_mirroring.get(filter_id)
        if not traffic_filter or not isinstance(traffic_filter, TrafficMirrorFilter):
            raise ValueError(f"TrafficMirrorFilterId {filter_id} does not exist")

        # Remove rule from ingress or egress list
        removed = False
        if rule.direction == TrafficDirection.INGRESS:
            new_ingress = [r for r in traffic_filter.ingress_filter_rule_set if r.traffic_mirror_filter_rule_id != traffic_mirror_filter_rule_id]
            if len(new_ingress) != len(traffic_filter.ingress_filter_rule_set):
                traffic_filter.ingress_filter_rule_set = new_ingress
                removed = True
        elif rule.direction == TrafficDirection.EGRESS:
            new_egress = [r for r in traffic_filter.egress_filter_rule_set if r.traffic_mirror_filter_rule_id != traffic_mirror_filter_rule_id]
            if len(new_egress) != len(traffic_filter.egress_filter_rule_set):
                traffic_filter.egress_filter_rule_set = new_egress
                removed = True
        else:
            # If direction is None or unknown, try removing from both lists defensively
            new_ingress = [r for r in traffic_filter.ingress_filter_rule_set if r.traffic_mirror_filter_rule_id != traffic_mirror_filter_rule_id]
            new_egress = [r for r in traffic_filter.egress_filter_rule_set if r.traffic_mirror_filter_rule_id != traffic_mirror_filter_rule_id]
            if len(new_ingress) != len(traffic_filter.ingress_filter_rule_set):
                traffic_filter.ingress_filter_rule_set = new_ingress
                removed = True
            if len(new_egress) != len(traffic_filter.egress_filter_rule_set):
                traffic_filter.egress_filter_rule_set = new_egress
                removed = True

        if not removed:
            # Rule was not found in filter's rule sets
            raise ValueError(f"TrafficMirrorFilterRuleId {traffic_mirror_filter_rule_id} not found in associated filter")

        # Remove from global state
        del self.state.traffic_mirroring[traffic_mirror_filter_rule_id]

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorFilterRuleId": traffic_mirror_filter_rule_id,
        }


    def delete_traffic_mirror_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        traffic_mirror_session_id = params.get("TrafficMirrorSessionId")
        if not traffic_mirror_session_id:
            raise ValueError("TrafficMirrorSessionId is required")

        dry_run = params.get("DryRun", False)
        if dry_run:
            # Assume permission granted for emulator
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        session = self.state.traffic_mirroring.get(traffic_mirror_session_id)
        if not session or not isinstance(session, TrafficMirrorSession):
            raise ValueError(f"TrafficMirrorSessionId {traffic_mirror_session_id} does not exist")

        del self.state.traffic_mirroring[traffic_mirror_session_id]

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorSessionId": traffic_mirror_session_id,
        }


    def delete_traffic_mirror_target(self, params: Dict[str, Any]) -> Dict[str, Any]:
        traffic_mirror_target_id = params.get("TrafficMirrorTargetId")
        if not traffic_mirror_target_id:
            raise ValueError("TrafficMirrorTargetId is required")

        dry_run = params.get("DryRun", False)
        if dry_run:
            # Assume permission granted for emulator
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        target = self.state.traffic_mirroring.get(traffic_mirror_target_id)
        if not target or not isinstance(target, TrafficMirrorTarget):
            raise ValueError(f"TrafficMirrorTargetId {traffic_mirror_target_id} does not exist")

        # Check if target is in use by any session
        for resource in self.state.traffic_mirroring.values():
            if isinstance(resource, TrafficMirrorSession):
                if resource.traffic_mirror_target_id == traffic_mirror_target_id:
                    raise ValueError(f"Cannot delete TrafficMirrorTargetId {traffic_mirror_target_id} because it is in use by a TrafficMirrorSession")

        del self.state.traffic_mirroring[traffic_mirror_target_id]

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorTargetId": traffic_mirror_target_id,
        }


    def describe_traffic_mirror_filters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        if dry_run:
            # Assume permission granted for emulator
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Filters can be specified as Filter.N or TrafficMirrorFilterId.N
        # Collect filters from params
        filters = []
        # Collect Filter.N filters
        i = 1
        while True:
            filter_name = f"Filter.{i}.Name"
            filter_values_key = f"Filter.{i}.Value"
            if filter_name not in params:
                break
            name = params.get(filter_name)
            # AWS uses Filter.N.Value or Filter.N.Values, but here we have Filter.N.Values as array of strings
            # We will check for Filter.N.Values or Filter.N.Value
            values = params.get(f"Filter.{i}.Values") or params.get(f"Filter.{i}.Value") or []
            if isinstance(values, str):
                values = [values]
            filters.append({"Name": name, "Values": values})
            i += 1

        # Collect TrafficMirrorFilterId.N filters
        filter_ids = []
        i = 1
        while True:
            key = f"TrafficMirrorFilterId.{i}"
            if key not in params:
                break
            filter_ids.append(params.get(key))
            i += 1

        # MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Collect all TrafficMirrorFilter objects from state
        all_filters = [res for res in self.state.traffic_mirroring.values() if isinstance(res, TrafficMirrorFilter)]

        # Filter by TrafficMirrorFilterId.N if specified
        if filter_ids:
            all_filters = [f for f in all_filters if f.traffic_mirror_filter_id in filter_ids]

        # Apply filters (description, traffic-mirror-filter-id)
        def matches_filter(filt: TrafficMirrorFilter, filter_obj: Dict[str, Any]) -> bool:
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "description":
                return any((filt.description == v) for v in values)
            if name == "traffic-mirror-filter-id":
                return any((filt.traffic_mirror_filter_id == v) for v in values)
            return True

        for filter_obj in filters:
            all_filters = [f for f in all_filters if matches_filter(f, filter_obj)]

        # Pagination
        filtered_count = len(all_filters)
        if max_results is not None:
            end_index = start_index + max_results
            page_filters = all_filters[start_index:end_index]
            next_token_out = str(end_index) if end_index < filtered_count else None
        else:
            page_filters = all_filters
            next_token_out = None

        # Prepare response filter sets
        def filter_to_dict(filt: TrafficMirrorFilter) -> Dict[str, Any]:
            return {
                "description": filt.description,
                "egressFilterRuleSet": [rule.to_dict() for rule in filt.egress_filter_rule_set],
                "ingressFilterRuleSet": [rule.to_dict() for rule in filt.ingress_filter_rule_set],
                "networkServiceSet": filt.network_service_set,
                "tagSet": [tag.to_dict() for tag in filt.tags],
                "trafficMirrorFilterId": filt.traffic_mirror_filter_id,
            }

        response_filters = [filter_to_dict(f) for f in page_filters]

        return {
            "nextToken": next_token_out,
            "requestId": self.generate_request_id(),
            "trafficMirrorFilterSet": response_filters,
        }


    def describe_traffic_mirror_filter_rules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Filters: Filter.N, TrafficMirrorFilterRuleId.N, TrafficMirrorFilterId
        filters = []
        i = 1
        while True:
            filter_name = f"Filter.{i}.Name"
            if filter_name not in params:
                break
            name = params.get(filter_name)
            values = params.get(f"Filter.{i}.Values") or params.get(f"Filter.{i}.Value") or []
            if isinstance(values, str):
                values = [values]
            filters.append({"Name": name, "Values": values})
            i += 1

        filter_rule_ids = []
        i = 1
        while True:
            key = f"TrafficMirrorFilterRuleId.{i}"
            if key not in params:
                break
            filter_rule_ids.append(params.get(key))
            i += 1

        filter_filter_id = params.get("TrafficMirrorFilterId")

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Collect all TrafficMirrorFilterRule objects from state
        all_rules = [res for res in self.state.traffic_mirroring.values() if isinstance(res, TrafficMirrorFilterRule)]

        # Filter by TrafficMirrorFilterRuleId.N if specified
        if filter_rule_ids:
            all_rules = [r for r in all_rules if r.traffic_mirror_filter_rule_id in filter_rule_ids]

        # Filter by TrafficMirrorFilterId if specified
        if filter_filter_id:
            all_rules = [r for r in all_rules if r.traffic_mirror_filter_id == filter_filter_id]

        # Apply filters
        def matches_filter(rule: TrafficMirrorFilterRule, filter_obj: Dict[str, Any]) -> bool:
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            for v in values:
                if name == "traffic-mirror-filter-rule-id" and rule.traffic_mirror_filter_rule_id == v:
                    return True
                if name == "traffic-mirror-filter-id" and rule.traffic_mirror_filter_id == v:
                    return True
                if name == "rule-number" and rule.rule_number is not None and str(rule.rule_number) == v:
                    return True
                if name == "rule-action" and rule.rule_action is not None and rule.rule_action.name == v:
                    return True
                if name == "traffic-direction" and rule.direction is not None and rule.direction.name == v:
                    return True
                if name == "protocol" and rule.protocol is not None and str(rule.protocol) == v:
                    return True
                if name == "source-cidr-block" and rule.source_cidr_block == v:
                    return True
                if name == "destination-cidr-block" and rule.destination_cidr_block == v:
                    return True
                if name == "description" and rule.description == v:
                    return True
            return False

        for filter_obj in filters:
            all_rules = [r for r in all_rules if matches_filter(r, filter_obj)]

        filtered_count = len(all_rules)
        if max_results is not None:
            end_index = start_index + max_results
            page_rules = all_rules[start_index:end_index]
            next_token_out = str(end_index) if end_index < filtered_count else None
        else:
            page_rules = all_rules
            next_token_out = None

        def rule_to_dict(rule: TrafficMirrorFilterRule) -> Dict[str, Any]:
            return {
                "description": rule.description,
                "destinationCidrBlock": rule.destination_cidr_block,
                "destinationPortRange": rule.destination_port_range.to_dict() if rule.destination_port_range else None,
                "protocol": rule.protocol,
                "ruleAction": rule.rule_action.name if rule.rule_action else None,
                "ruleNumber": rule.rule_number,
                "sourceCidrBlock": rule.source_cidr_block,
                "sourcePortRange": rule.source_port_range.to_dict() if rule.source_port_range else None,
                "tagSet": [tag.to_dict() for tag in rule.tags],
                "trafficDirection": rule.direction.name if rule.direction else None,
                "trafficMirrorFilterId": rule.traffic_mirror_filter_id,
                "trafficMirrorFilterRuleId": rule.traffic_mirror_filter_rule_id,
            }

        response_rules = [rule_to_dict(r) for r in page_rules]

        return {
            "nextToken": next_token_out,
            "requestId": self.generate_request_id(),
            "trafficMirrorFilterRuleSet": response_rules,
        }

    def describe_traffic_mirror_sessions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        session_ids = params.get("TrafficMirrorSessionId", [])

        # Validate MaxResults if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Prepare all sessions from state
        all_sessions = list(self.state.traffic_mirroring.get("sessions", {}).values()) if self.state.traffic_mirroring else []
        # If no sessions dict, fallback to empty list

        # Filter by session IDs if provided
        if session_ids:
            all_sessions = [s for s in all_sessions if s.traffic_mirror_session_id in session_ids]

        # Apply filters if provided
        def session_matches_filter(session: TrafficMirrorSession, filter_obj: Dict[str, Any]) -> bool:
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # No filter criteria, match all

            # Map filter names to session attributes
            # AWS filter names are case-sensitive
            for value in values:
                if name == "description" and session.description == value:
                    return True
                elif name == "network-interface-id" and session.network_interface_id == value:
                    return True
                elif name == "owner-id" and session.owner_id == value:
                    return True
                elif name == "packet-length":
                    try:
                        if session.packet_length is not None and int(value) == session.packet_length:
                            return True
                    except Exception:
                        pass
                elif name == "session-number":
                    try:
                        if session.session_number is not None and int(value) == session.session_number:
                            return True
                    except Exception:
                        pass
                elif name == "traffic-mirror-filter-id" and session.traffic_mirror_filter_id == value:
                    return True
                elif name == "traffic-mirror-session-id" and session.traffic_mirror_session_id == value:
                    return True
                elif name == "traffic-mirror-target-id" and session.traffic_mirror_target_id == value:
                    return True
                elif name == "virtual-network-id":
                    try:
                        if session.virtual_network_id is not None and int(value) == session.virtual_network_id:
                            return True
                    except Exception:
                        pass
            return False

        if filters:
            filtered_sessions = []
            for session in all_sessions:
                # For each filter, session must match at least one value
                # AWS filters are OR within values, AND across filters
                if all(session_matches_filter(session, f) for f in filters):
                    filtered_sessions.append(session)
            all_sessions = filtered_sessions

        # Pagination logic
        # next_token is a string token representing the index offset
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_sessions)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_sessions))

        paged_sessions = all_sessions[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(all_sessions):
            new_next_token = str(end_index)

        # Build response session list
        response_sessions = []
        for session in paged_sessions:
            response_sessions.append(session.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorSessionSet": response_sessions,
            "nextToken": new_next_token,
        }


    def describe_traffic_mirror_targets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        target_ids = params.get("TrafficMirrorTargetId", [])

        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        all_targets = list(self.state.traffic_mirroring.get("targets", {}).values()) if self.state.traffic_mirroring else []

        if target_ids:
            all_targets = [t for t in all_targets if t.traffic_mirror_target_id in target_ids]

        def target_matches_filter(target: TrafficMirrorTarget, filter_obj: Dict[str, Any]) -> bool:
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True

            for value in values:
                if name == "description" and target.description == value:
                    return True
                elif name == "network-interface-id" and target.network_interface_id == value:
                    return True
                elif name == "network-load-balancer-arn" and target.network_load_balancer_arn == value:
                    return True
                elif name == "owner-id" and target.owner_id == value:
                    return True
                elif name == "traffic-mirror-target-id" and target.traffic_mirror_target_id == value:
                    return True
            return False

        if filters:
            filtered_targets = []
            for target in all_targets:
                if all(target_matches_filter(target, f) for f in filters):
                    filtered_targets.append(target)
            all_targets = filtered_targets

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_targets)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_targets))

        paged_targets = all_targets[start_index:end_index]

        new_next_token = None
        if end_index < len(all_targets):
            new_next_token = str(end_index)

        response_targets = []
        for target in paged_targets:
            response_targets.append(target.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorTargetSet": response_targets,
            "nextToken": new_next_token,
        }


    def modify_traffic_mirror_filter_network_services(self, params: Dict[str, Any]) -> Dict[str, Any]:
        add_services = params.get("AddNetworkService", [])
        remove_services = params.get("RemoveNetworkService", [])
        filter_id = params.get("TrafficMirrorFilterId")
        dry_run = params.get("DryRun")

        if not filter_id:
            raise ValueError("TrafficMirrorFilterId is required")

        filters = self.state.traffic_mirroring.get("filters", {})
        filter_obj = filters.get(filter_id)
        if not filter_obj:
            raise ValueError(f"TrafficMirrorFilter {filter_id} not found")

        # Validate services values
        valid_services = {"amazon-dns"}
        for svc in add_services:
            if svc not in valid_services:
                raise ValueError(f"Invalid AddNetworkService value: {svc}")
        for svc in remove_services:
            if svc not in valid_services:
                raise ValueError(f"Invalid RemoveNetworkService value: {svc}")

        # Initialize network_service_set if None
        if filter_obj.network_service_set is None:
            filter_obj.network_service_set = []

        # Add services
        for svc in add_services:
            if svc not in filter_obj.network_service_set:
                filter_obj.network_service_set.append(svc)

        # Remove services
        for svc in remove_services:
            if svc in filter_obj.network_service_set:
                filter_obj.network_service_set.remove(svc)

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorFilter": filter_obj.to_dict(),
        }


    def modify_traffic_mirror_filter_rule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        rule_id = params.get("TrafficMirrorFilterRuleId")
        if not rule_id:
            raise ValueError("TrafficMirrorFilterRuleId is required")

        filters = self.state.traffic_mirroring.get("filters", {})
        # Search for rule in all filters
        rule_obj = None
        for filter_obj in filters.values():
            for rule in filter_obj.egress_filter_rule_set + filter_obj.ingress_filter_rule_set:
                if rule.traffic_mirror_filter_rule_id == rule_id:
                    rule_obj = rule
                    break
            if rule_obj:
                break

        if not rule_obj:
            raise ValueError(f"TrafficMirrorFilterRule {rule_id} not found")

        # RemoveField processing
        remove_fields = params.get("RemoveField", [])

        # Update fields if not removed
        if "description" not in remove_fields and "Description" in params:
            rule_obj.description = params["Description"]
        elif "description" in remove_fields:
            rule_obj.description = None

        if "destination-port-range" not in remove_fields and "DestinationPortRange" in params:
            dpr = params["DestinationPortRange"]
            from_port = dpr.get("FromPort")
            to_port = dpr.get("ToPort")
            rule_obj.destination_port_range = TrafficMirrorPortRange(from_port=from_port, to_port=to_port)
        elif "destination-port-range" in remove_fields:
            rule_obj.destination_port_range = None

        if "source-port-range" not in remove_fields and "SourcePortRange" in params:
            spr = params["SourcePortRange"]
            from_port = spr.get("FromPort")
            to_port = spr.get("ToPort")
            rule_obj.source_port_range = TrafficMirrorPortRange(from_port=from_port, to_port=to_port)
        elif "source-port-range" in remove_fields:
            rule_obj.source_port_range = None

        if "protocol" not in remove_fields and "Protocol" in params:
            rule_obj.protocol = params["Protocol"]
        elif "protocol" in remove_fields:
            rule_obj.protocol = None

        if "RuleAction" in params:
            rule_obj.rule_action = params["RuleAction"]

        if "RuleNumber" in params:
            rule_obj.rule_number = params["RuleNumber"]

        if "SourceCidrBlock" in params:
            rule_obj.source_cidr_block = params["SourceCidrBlock"]

        if "DestinationCidrBlock" in params:
            rule_obj.destination_cidr_block = params["DestinationCidrBlock"]

        if "TrafficDirection" in params:
            rule_obj.direction = params["TrafficDirection"]

        # Tags are not returned for ModifyTrafficMirrorFilterRule per spec

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorFilterRule": rule_obj.to_dict(),
        }


    def modify_traffic_mirror_session(self, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = params.get("TrafficMirrorSessionId")
        if not session_id:
            raise ValueError("TrafficMirrorSessionId is required")

        sessions = self.state.traffic_mirroring.get("sessions", {})
        session_obj = sessions.get(session_id)
        if not session_obj:
            raise ValueError(f"TrafficMirrorSession {session_id} not found")

        remove_fields = params.get("RemoveField", [])

        if "description" not in remove_fields and "Description" in params:
            session_obj.description = params["Description"]
        elif "description" in remove_fields:
            session_obj.description = None

        if "packet-length" not in remove_fields and "PacketLength" in params:
            packet_length = params["PacketLength"]
            if packet_length is not None:
                if not (1 <= packet_length <= 8500):
                    raise ValueError("PacketLength must be between 1 and 8500")
            session_obj.packet_length = packet_length
        elif "packet-length" in remove_fields:
            session_obj.packet_length = None

        if "session-number" not in remove_fields and "SessionNumber" in params:
            session_obj.session_number = params["SessionNumber"]
        elif "session-number" in remove_fields:
            session_obj.session_number = None

        if "virtual-network-id" not in remove_fields and "VirtualNetworkId" in params:
            session_obj.virtual_network_id = params["VirtualNetworkId"]
        elif "virtual-network-id" in remove_fields:
            session_obj.virtual_network_id = None

        if "TrafficMirrorFilterId" in params:
            session_obj.traffic_mirror_filter_id = params["TrafficMirrorFilterId"]

        if "TrafficMirrorTargetId" in params:
            session_obj.traffic_mirror_target_id = params["TrafficMirrorTargetId"]

        # Tags are not modified here

        return {
            "requestId": self.generate_request_id(),
            "trafficMirrorSession": session_obj.to_dict(),
        }

    

from emulator_core.gateway.base import BaseGateway

class TrafficMirroringGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateTrafficMirrorFilter", self.create_traffic_mirror_filter)
        self.register_action("CreateTrafficMirrorFilterRule", self.create_traffic_mirror_filter_rule)
        self.register_action("CreateTrafficMirrorSession", self.create_traffic_mirror_session)
        self.register_action("CreateTrafficMirrorTarget", self.create_traffic_mirror_target)
        self.register_action("DeleteTrafficMirrorFilter", self.delete_traffic_mirror_filter)
        self.register_action("DeleteTrafficMirrorFilterRule", self.delete_traffic_mirror_filter_rule)
        self.register_action("DeleteTrafficMirrorSession", self.delete_traffic_mirror_session)
        self.register_action("DeleteTrafficMirrorTarget", self.delete_traffic_mirror_target)
        self.register_action("DescribeTrafficMirrorFilters", self.describe_traffic_mirror_filters)
        self.register_action("DescribeTrafficMirrorFilterRules", self.describe_traffic_mirror_filter_rules)
        self.register_action("DescribeTrafficMirrorSessions", self.describe_traffic_mirror_sessions)
        self.register_action("DescribeTrafficMirrorTargets", self.describe_traffic_mirror_targets)
        self.register_action("ModifyTrafficMirrorFilterNetworkServices", self.modify_traffic_mirror_filter_network_services)
        self.register_action("ModifyTrafficMirrorFilterRule", self.modify_traffic_mirror_filter_rule)
        self.register_action("ModifyTrafficMirrorSession", self.modify_traffic_mirror_session)

    def create_traffic_mirror_filter(self, params):
        return self.backend.create_traffic_mirror_filter(params)

    def create_traffic_mirror_filter_rule(self, params):
        return self.backend.create_traffic_mirror_filter_rule(params)

    def create_traffic_mirror_session(self, params):
        return self.backend.create_traffic_mirror_session(params)

    def create_traffic_mirror_target(self, params):
        return self.backend.create_traffic_mirror_target(params)

    def delete_traffic_mirror_filter(self, params):
        return self.backend.delete_traffic_mirror_filter(params)

    def delete_traffic_mirror_filter_rule(self, params):
        return self.backend.delete_traffic_mirror_filter_rule(params)

    def delete_traffic_mirror_session(self, params):
        return self.backend.delete_traffic_mirror_session(params)

    def delete_traffic_mirror_target(self, params):
        return self.backend.delete_traffic_mirror_target(params)

    def describe_traffic_mirror_filters(self, params):
        return self.backend.describe_traffic_mirror_filters(params)

    def describe_traffic_mirror_filter_rules(self, params):
        return self.backend.describe_traffic_mirror_filter_rules(params)

    def describe_traffic_mirror_sessions(self, params):
        return self.backend.describe_traffic_mirror_sessions(params)

    def describe_traffic_mirror_targets(self, params):
        return self.backend.describe_traffic_mirror_targets(params)

    def modify_traffic_mirror_filter_network_services(self, params):
        return self.backend.modify_traffic_mirror_filter_network_services(params)

    def modify_traffic_mirror_filter_rule(self, params):
        return self.backend.modify_traffic_mirror_filter_rule(params)

    def modify_traffic_mirror_session(self, params):
        return self.backend.modify_traffic_mirror_session(params)
