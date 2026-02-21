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
class TrafficMirroring:
    description: str = ""
    egress_filter_rule_set: List[Any] = field(default_factory=list)
    ingress_filter_rule_set: List[Any] = field(default_factory=list)
    network_service_set: List[Any] = field(default_factory=list)
    tag_set: List[Any] = field(default_factory=list)
    traffic_mirror_filter_id: str = ""

    resource_type: str = "filter"
    traffic_mirror_filter_rule_id: str = ""
    traffic_mirror_session_id: str = ""
    traffic_mirror_target_id: str = ""
    traffic_mirror_target_type: str = ""
    destination_cidr_block: str = ""
    destination_port_range: Dict[str, Any] = field(default_factory=dict)
    protocol: Optional[int] = None
    rule_action: str = ""
    rule_number: Optional[int] = None
    source_cidr_block: str = ""
    source_port_range: Dict[str, Any] = field(default_factory=dict)
    traffic_direction: str = ""
    network_interface_id: str = ""
    owner_id: str = ""
    packet_length: Optional[int] = None
    session_number: Optional[int] = None
    virtual_network_id: Optional[int] = None
    gateway_load_balancer_endpoint_id: str = ""
    network_load_balancer_arn: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "egressFilterRuleSet": self.egress_filter_rule_set,
            "ingressFilterRuleSet": self.ingress_filter_rule_set,
            "networkServiceSet": self.network_service_set,
            "tagSet": self.tag_set,
            "trafficMirrorFilterId": self.traffic_mirror_filter_id,
            "resourceType": self.resource_type,
            "trafficMirrorFilterRuleId": self.traffic_mirror_filter_rule_id,
            "trafficMirrorSessionId": self.traffic_mirror_session_id,
            "trafficMirrorTargetId": self.traffic_mirror_target_id,
            "trafficMirrorTargetType": self.traffic_mirror_target_type,
            "destinationCidrBlock": self.destination_cidr_block,
            "destinationPortRange": self.destination_port_range,
            "protocol": self.protocol,
            "ruleAction": self.rule_action,
            "ruleNumber": self.rule_number,
            "sourceCidrBlock": self.source_cidr_block,
            "sourcePortRange": self.source_port_range,
            "trafficDirection": self.traffic_direction,
            "networkInterfaceId": self.network_interface_id,
            "ownerId": self.owner_id,
            "packetLength": self.packet_length,
            "sessionNumber": self.session_number,
            "virtualNetworkId": self.virtual_network_id,
            "gatewayLoadBalancerEndpointId": self.gateway_load_balancer_endpoint_id,
            "networkLoadBalancerArn": self.network_load_balancer_arn,
        }

class TrafficMirroring_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.traffic_mirroring  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            if not params.get(key):
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if resource_type and spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def _get_resource_or_error(
        self,
        resource_id: str,
        error_code: str,
        resource_type: Optional[str] = None,
    ) -> Any:
        resource = self.resources.get(resource_id)
        if not resource or (resource_type and getattr(resource, "resource_type", None) != resource_type):
            return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_type(self, resource_type: str) -> List[TrafficMirroring]:
        return [
            resource
            for resource in self.resources.values()
            if getattr(resource, "resource_type", None) == resource_type
        ]

    def CreateTrafficMirrorFilter(self, params: Dict[str, Any]):
        """Creates a Traffic Mirror filter. A Traffic Mirror filter is a set of rules that defines the traffic to mirror. By default, no traffic is mirrored. To mirror traffic, useCreateTrafficMirrorFilterRuleto add Traffic Mirror rules to the filter. The rules you add define what traffic gets mirrored. 
     """

        traffic_mirror_filter_id = self._generate_id("tmf")
        tag_set = self._extract_tags(params.get("TagSpecification.N", []), "traffic-mirror-filter")
        resource = TrafficMirroring(
            description=params.get("Description") or "",
            egress_filter_rule_set=[],
            ingress_filter_rule_set=[],
            network_service_set=[],
            tag_set=tag_set,
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            resource_type="filter",
        )
        self.resources[traffic_mirror_filter_id] = resource

        return {
            'clientToken': params.get("ClientToken"),
            'trafficMirrorFilter': {
                'description': resource.description,
                'egressFilterRuleSet': resource.egress_filter_rule_set,
                'ingressFilterRuleSet': resource.ingress_filter_rule_set,
                'networkServiceSet': resource.network_service_set,
                'tagSet': resource.tag_set,
                'trafficMirrorFilterId': resource.traffic_mirror_filter_id,
                },
            }

    def CreateTrafficMirrorFilterRule(self, params: Dict[str, Any]):
        """Creates a Traffic Mirror filter rule. A Traffic Mirror rule defines the Traffic Mirror source traffic to mirror. You need the Traffic Mirror filter ID when you create the rule."""

        error = self._require_params(
            params,
            [
                "DestinationCidrBlock",
                "RuleAction",
                "RuleNumber",
                "SourceCidrBlock",
                "TrafficDirection",
                "TrafficMirrorFilterId",
            ],
        )
        if error:
            return error

        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")
        traffic_mirror_filter, error = self._get_resource_or_error(
            traffic_mirror_filter_id,
            "InvalidTrafficMirrorFilterId.NotFound",
            "filter",
        )
        if error:
            return error

        def _normalize_port_range(port_range: Any) -> Dict[str, Any]:
            if not isinstance(port_range, dict):
                return {}
            from_port = port_range.get("fromPort")
            to_port = port_range.get("toPort")
            if from_port is None:
                from_port = port_range.get("FromPort")
            if to_port is None:
                to_port = port_range.get("ToPort")
            result: Dict[str, Any] = {}
            if from_port is not None:
                result["fromPort"] = from_port
            if to_port is not None:
                result["toPort"] = to_port
            return result

        destination_port_range = _normalize_port_range(params.get("DestinationPortRange"))
        source_port_range = _normalize_port_range(params.get("SourcePortRange"))
        rule_id = self._generate_id("tmfr")
        tag_set = self._extract_tags(params.get("TagSpecification.N", []), "traffic-mirror-filter-rule")

        resource = TrafficMirroring(
            description=params.get("Description") or "",
            destination_cidr_block=params.get("DestinationCidrBlock") or "",
            destination_port_range=destination_port_range,
            protocol=params.get("Protocol"),
            rule_action=params.get("RuleAction") or "",
            rule_number=params.get("RuleNumber"),
            source_cidr_block=params.get("SourceCidrBlock") or "",
            source_port_range=source_port_range,
            traffic_direction=params.get("TrafficDirection") or "",
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            traffic_mirror_filter_rule_id=rule_id,
            tag_set=tag_set,
            resource_type="rule",
        )
        self.resources[rule_id] = resource

        rule_data = {
            "description": resource.description,
            "destinationCidrBlock": resource.destination_cidr_block,
            "destinationPortRange": resource.destination_port_range,
            "protocol": resource.protocol,
            "ruleAction": resource.rule_action,
            "ruleNumber": resource.rule_number,
            "sourceCidrBlock": resource.source_cidr_block,
            "sourcePortRange": resource.source_port_range,
            "tagSet": resource.tag_set,
            "trafficDirection": resource.traffic_direction,
            "trafficMirrorFilterId": resource.traffic_mirror_filter_id,
            "trafficMirrorFilterRuleId": resource.traffic_mirror_filter_rule_id,
        }

        direction = (resource.traffic_direction or "").lower()
        if direction == "egress":
            traffic_mirror_filter.egress_filter_rule_set.append(rule_data)
        else:
            traffic_mirror_filter.ingress_filter_rule_set.append(rule_data)

        return {
            'clientToken': params.get("ClientToken"),
            'trafficMirrorFilterRule': rule_data,
            }

    def CreateTrafficMirrorSession(self, params: Dict[str, Any]):
        """Creates a Traffic Mirror session. A Traffic Mirror session actively copies packets from a Traffic Mirror source to a Traffic Mirror target. Create a filter, and then assign it
         to the session to define a subset of the traffic to mirror, for example all TCP
         traffic. The Traffic Mirro"""

        error = self._require_params(
            params,
            [
                "NetworkInterfaceId",
                "SessionNumber",
                "TrafficMirrorFilterId",
                "TrafficMirrorTargetId",
            ],
        )
        if error:
            return error

        network_interface_id = params.get("NetworkInterfaceId")
        if not self.state.elastic_network_interfaces.get(network_interface_id):
            return create_error_response(
                "InvalidNetworkInterfaceID.NotFound",
                f"The networkInterface ID '{network_interface_id}' does not exist.",
            )

        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")
        _, error = self._get_resource_or_error(
            traffic_mirror_filter_id,
            "InvalidTrafficMirrorFilterId.NotFound",
            "filter",
        )
        if error:
            return error

        traffic_mirror_target_id = params.get("TrafficMirrorTargetId")
        _, error = self._get_resource_or_error(
            traffic_mirror_target_id,
            "InvalidTrafficMirrorTargetId.NotFound",
            "target",
        )
        if error:
            return error

        traffic_mirror_session_id = self._generate_id("tms")
        tag_set = self._extract_tags(params.get("TagSpecification.N", []), "traffic-mirror-session")
        resource = TrafficMirroring(
            description=params.get("Description") or "",
            network_interface_id=network_interface_id,
            owner_id="",
            packet_length=params.get("PacketLength"),
            session_number=params.get("SessionNumber"),
            tag_set=tag_set,
            traffic_mirror_filter_id=traffic_mirror_filter_id,
            traffic_mirror_session_id=traffic_mirror_session_id,
            traffic_mirror_target_id=traffic_mirror_target_id,
            virtual_network_id=params.get("VirtualNetworkId"),
            resource_type="session",
        )
        self.resources[traffic_mirror_session_id] = resource

        return {
            'clientToken': params.get("ClientToken"),
            'trafficMirrorSession': {
                'description': resource.description,
                'networkInterfaceId': resource.network_interface_id,
                'ownerId': resource.owner_id,
                'packetLength': resource.packet_length,
                'sessionNumber': resource.session_number,
                'tagSet': resource.tag_set,
                'trafficMirrorFilterId': resource.traffic_mirror_filter_id,
                'trafficMirrorSessionId': resource.traffic_mirror_session_id,
                'trafficMirrorTargetId': resource.traffic_mirror_target_id,
                'virtualNetworkId': resource.virtual_network_id,
                },
            }

    def CreateTrafficMirrorTarget(self, params: Dict[str, Any]):
        """Creates a target for your Traffic Mirror session. A Traffic Mirror target is the destination for mirrored traffic. The Traffic Mirror source and
         the Traffic Mirror target (monitoring appliances) can be in the same VPC, or in
         different VPCs connected via VPC peering or a transit gat"""

        network_interface_id = params.get("NetworkInterfaceId")
        if network_interface_id and not self.state.elastic_network_interfaces.get(network_interface_id):
            return create_error_response(
                "InvalidNetworkInterfaceID.NotFound",
                f"The networkInterface ID '{network_interface_id}' does not exist.",
            )

        traffic_mirror_target_id = self._generate_id("tmt")
        tag_set = self._extract_tags(params.get("TagSpecification.N", []), "traffic-mirror-target")
        gateway_load_balancer_endpoint_id = params.get("GatewayLoadBalancerEndpointId")
        network_load_balancer_arn = params.get("NetworkLoadBalancerArn")
        traffic_mirror_target_type = "eni"
        if gateway_load_balancer_endpoint_id:
            traffic_mirror_target_type = "gateway-load-balancer-endpoint"
        elif network_load_balancer_arn:
            traffic_mirror_target_type = "network-load-balancer"

        resource = TrafficMirroring(
            description=params.get("Description") or "",
            gateway_load_balancer_endpoint_id=gateway_load_balancer_endpoint_id or "",
            network_interface_id=network_interface_id or "",
            network_load_balancer_arn=network_load_balancer_arn or "",
            owner_id="",
            tag_set=tag_set,
            traffic_mirror_target_id=traffic_mirror_target_id,
            traffic_mirror_target_type=traffic_mirror_target_type,
            resource_type="target",
        )
        self.resources[traffic_mirror_target_id] = resource

        return {
            'clientToken': params.get("ClientToken"),
            'trafficMirrorTarget': {
                'description': resource.description,
                'gatewayLoadBalancerEndpointId': resource.gateway_load_balancer_endpoint_id,
                'networkInterfaceId': resource.network_interface_id,
                'networkLoadBalancerArn': resource.network_load_balancer_arn,
                'ownerId': resource.owner_id,
                'tagSet': resource.tag_set,
                'trafficMirrorTargetId': resource.traffic_mirror_target_id,
                'type': resource.traffic_mirror_target_type,
                },
            }

    def DeleteTrafficMirrorFilter(self, params: Dict[str, Any]):
        """Deletes the specified Traffic Mirror filter. You cannot delete a Traffic Mirror filter that is in use by a Traffic Mirror session."""

        error = self._require_params(params, ["TrafficMirrorFilterId"])
        if error:
            return error

        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")
        traffic_mirror_filter, error = self._get_resource_or_error(
            traffic_mirror_filter_id,
            "InvalidTrafficMirrorFilterId.NotFound",
            "filter",
        )
        if error:
            return error

        for session in self._get_resources_by_type("session"):
            if session.traffic_mirror_filter_id == traffic_mirror_filter_id:
                return create_error_response(
                    "DependencyViolation",
                    "The traffic mirror filter is in use by a traffic mirror session.",
                )

        if traffic_mirror_filter_id in self.resources:
            del self.resources[traffic_mirror_filter_id]

        return {
            'trafficMirrorFilterId': traffic_mirror_filter.traffic_mirror_filter_id,
            }

    def DeleteTrafficMirrorFilterRule(self, params: Dict[str, Any]):
        """Deletes the specified Traffic Mirror rule."""

        error = self._require_params(params, ["TrafficMirrorFilterRuleId"])
        if error:
            return error

        rule_id = params.get("TrafficMirrorFilterRuleId")
        rule, error = self._get_resource_or_error(
            rule_id,
            "InvalidTrafficMirrorFilterRuleId.NotFound",
            "rule",
        )
        if error:
            return error

        traffic_mirror_filter, error = self._get_resource_or_error(
            rule.traffic_mirror_filter_id,
            "InvalidTrafficMirrorFilterId.NotFound",
            "filter",
        )
        if error:
            return error

        traffic_mirror_filter.egress_filter_rule_set = [
            entry
            for entry in traffic_mirror_filter.egress_filter_rule_set
            if entry.get("trafficMirrorFilterRuleId") != rule.traffic_mirror_filter_rule_id
        ]
        traffic_mirror_filter.ingress_filter_rule_set = [
            entry
            for entry in traffic_mirror_filter.ingress_filter_rule_set
            if entry.get("trafficMirrorFilterRuleId") != rule.traffic_mirror_filter_rule_id
        ]

        if rule_id in self.resources:
            del self.resources[rule_id]

        return {
            'trafficMirrorFilterRuleId': rule.traffic_mirror_filter_rule_id,
            }

    def DeleteTrafficMirrorSession(self, params: Dict[str, Any]):
        """Deletes the specified Traffic Mirror session."""

        error = self._require_params(params, ["TrafficMirrorSessionId"])
        if error:
            return error

        session_id = params.get("TrafficMirrorSessionId")
        session, error = self._get_resource_or_error(
            session_id,
            "InvalidTrafficMirrorSessionId.NotFound",
            "session",
        )
        if error:
            return error

        if session_id in self.resources:
            del self.resources[session_id]

        return {
            'trafficMirrorSessionId': session.traffic_mirror_session_id,
            }

    def DeleteTrafficMirrorTarget(self, params: Dict[str, Any]):
        """Deletes the specified Traffic Mirror target. You cannot delete a Traffic Mirror target that is in use by a Traffic Mirror session."""

        error = self._require_params(params, ["TrafficMirrorTargetId"])
        if error:
            return error

        target_id = params.get("TrafficMirrorTargetId")
        target, error = self._get_resource_or_error(
            target_id,
            "InvalidTrafficMirrorTargetId.NotFound",
            "target",
        )
        if error:
            return error

        for session in self._get_resources_by_type("session"):
            if session.traffic_mirror_target_id == target_id:
                return create_error_response(
                    "DependencyViolation",
                    "The traffic mirror target is in use by a traffic mirror session.",
                )

        if target_id in self.resources:
            del self.resources[target_id]

        return {
            'trafficMirrorTargetId': target.traffic_mirror_target_id,
            }

    def DescribeTrafficMirrorFilters(self, params: Dict[str, Any]):
        """Describes one or more Traffic Mirror filters."""

        filter_ids = params.get("TrafficMirrorFilterId.N", []) or []
        resources = self._get_resources_by_type("filter")
        if filter_ids:
            selected = []
            for filter_id in filter_ids:
                resource = self.resources.get(filter_id)
                if not resource or getattr(resource, "resource_type", None) != "filter":
                    return create_error_response(
                        "InvalidTrafficMirrorFilterId.NotFound",
                        f"The ID '{filter_id}' does not exist",
                    )
                selected.append(resource)
            resources = selected

        resources = apply_filters(resources, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or len(resources) or 0)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'trafficMirrorFilterSet': [
                {
                    "description": resource.description,
                    "egressFilterRuleSet": resource.egress_filter_rule_set,
                    "ingressFilterRuleSet": resource.ingress_filter_rule_set,
                    "networkServiceSet": resource.network_service_set,
                    "tagSet": resource.tag_set,
                    "trafficMirrorFilterId": resource.traffic_mirror_filter_id,
                }
                for resource in resources
            ],
            }

    def DescribeTrafficMirrorFilterRules(self, params: Dict[str, Any]):
        """Describe traffic mirror filters that determine the traffic that is mirrored."""

        rule_ids = params.get("TrafficMirrorFilterRuleId.N", []) or []
        resources = self._get_resources_by_type("rule")

        if rule_ids:
            selected = []
            for rule_id in rule_ids:
                resource = self.resources.get(rule_id)
                if not resource or getattr(resource, "resource_type", None) != "rule":
                    return create_error_response(
                        "InvalidTrafficMirrorFilterRuleId.NotFound",
                        f"The ID '{rule_id}' does not exist",
                    )
                selected.append(resource)
            resources = selected

        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")
        if traffic_mirror_filter_id:
            resource, error = self._get_resource_or_error(
                traffic_mirror_filter_id,
                "InvalidTrafficMirrorFilterId.NotFound",
                "filter",
            )
            if error:
                return error
            resources = [
                rule
                for rule in resources
                if rule.traffic_mirror_filter_id == resource.traffic_mirror_filter_id
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or len(resources) or 0)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'trafficMirrorFilterRuleSet': [
                {
                    "description": resource.description,
                    "destinationCidrBlock": resource.destination_cidr_block,
                    "destinationPortRange": resource.destination_port_range,
                    "protocol": resource.protocol,
                    "ruleAction": resource.rule_action,
                    "ruleNumber": resource.rule_number,
                    "sourceCidrBlock": resource.source_cidr_block,
                    "sourcePortRange": resource.source_port_range,
                    "tagSet": resource.tag_set,
                    "trafficDirection": resource.traffic_direction,
                    "trafficMirrorFilterId": resource.traffic_mirror_filter_id,
                    "trafficMirrorFilterRuleId": resource.traffic_mirror_filter_rule_id,
                }
                for resource in resources
            ],
            }

    def DescribeTrafficMirrorSessions(self, params: Dict[str, Any]):
        """Describes one or more Traffic Mirror sessions. By default, all Traffic Mirror sessions are described. Alternatively, you can filter the results."""

        session_ids = params.get("TrafficMirrorSessionId.N", []) or []
        resources = self._get_resources_by_type("session")
        if session_ids:
            selected = []
            for session_id in session_ids:
                resource = self.resources.get(session_id)
                if not resource or getattr(resource, "resource_type", None) != "session":
                    return create_error_response(
                        "InvalidTrafficMirrorSessionId.NotFound",
                        f"The ID '{session_id}' does not exist",
                    )
                selected.append(resource)
            resources = selected

        resources = apply_filters(resources, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or len(resources) or 0)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'trafficMirrorSessionSet': [
                {
                    "description": resource.description,
                    "networkInterfaceId": resource.network_interface_id,
                    "ownerId": resource.owner_id,
                    "packetLength": resource.packet_length,
                    "sessionNumber": resource.session_number,
                    "tagSet": resource.tag_set,
                    "trafficMirrorFilterId": resource.traffic_mirror_filter_id,
                    "trafficMirrorSessionId": resource.traffic_mirror_session_id,
                    "trafficMirrorTargetId": resource.traffic_mirror_target_id,
                    "virtualNetworkId": resource.virtual_network_id,
                }
                for resource in resources
            ],
            }

    def DescribeTrafficMirrorTargets(self, params: Dict[str, Any]):
        """Information about one or more Traffic Mirror targets."""

        target_ids = params.get("TrafficMirrorTargetId.N", []) or []
        resources = self._get_resources_by_type("target")
        if target_ids:
            selected = []
            for target_id in target_ids:
                resource = self.resources.get(target_id)
                if not resource or getattr(resource, "resource_type", None) != "target":
                    return create_error_response(
                        "InvalidTrafficMirrorTargetId.NotFound",
                        f"The ID '{target_id}' does not exist",
                    )
                selected.append(resource)
            resources = selected

        resources = apply_filters(resources, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or len(resources) or 0)
        resources = resources[:max_results]

        return {
            'nextToken': None,
            'trafficMirrorTargetSet': [
                {
                    "description": resource.description,
                    "gatewayLoadBalancerEndpointId": resource.gateway_load_balancer_endpoint_id,
                    "networkInterfaceId": resource.network_interface_id,
                    "networkLoadBalancerArn": resource.network_load_balancer_arn,
                    "ownerId": resource.owner_id,
                    "tagSet": resource.tag_set,
                    "trafficMirrorTargetId": resource.traffic_mirror_target_id,
                    "type": resource.traffic_mirror_target_type,
                }
                for resource in resources
            ],
            }

    def ModifyTrafficMirrorFilterNetworkServices(self, params: Dict[str, Any]):
        """Allows or restricts mirroring network services. By default, Amazon DNS network services are not eligible for Traffic Mirror. UseAddNetworkServicesto add network services to a Traffic Mirror filter. When a network service is added to the Traffic Mirror filter, all traffic related to that network serv"""

        error = self._require_params(params, ["TrafficMirrorFilterId"])
        if error:
            return error

        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")
        traffic_mirror_filter, error = self._get_resource_or_error(
            traffic_mirror_filter_id,
            "InvalidTrafficMirrorFilterId.NotFound",
            "filter",
        )
        if error:
            return error

        add_services = params.get("AddNetworkService.N", []) or []
        remove_services = params.get("RemoveNetworkService.N", []) or []

        current_services = list(traffic_mirror_filter.network_service_set or [])
        for service in add_services:
            if service and service not in current_services:
                current_services.append(service)
        for service in remove_services:
            if service in current_services:
                current_services.remove(service)

        traffic_mirror_filter.network_service_set = current_services

        return {
            'trafficMirrorFilter': {
                'description': traffic_mirror_filter.description,
                'egressFilterRuleSet': traffic_mirror_filter.egress_filter_rule_set,
                'ingressFilterRuleSet': traffic_mirror_filter.ingress_filter_rule_set,
                'networkServiceSet': traffic_mirror_filter.network_service_set,
                'tagSet': traffic_mirror_filter.tag_set,
                'trafficMirrorFilterId': traffic_mirror_filter.traffic_mirror_filter_id,
                },
            }

    def ModifyTrafficMirrorFilterRule(self, params: Dict[str, Any]):
        """Modifies the specified Traffic Mirror rule. DestinationCidrBlockandSourceCidrBlockmust both be an IPv4
         range or an IPv6 range."""

        error = self._require_params(params, ["TrafficMirrorFilterRuleId"])
        if error:
            return error

        rule_id = params.get("TrafficMirrorFilterRuleId")
        rule, error = self._get_resource_or_error(
            rule_id,
            "InvalidTrafficMirrorFilterRuleId.NotFound",
            "rule",
        )
        if error:
            return error

        traffic_mirror_filter, error = self._get_resource_or_error(
            rule.traffic_mirror_filter_id,
            "InvalidTrafficMirrorFilterId.NotFound",
            "filter",
        )
        if error:
            return error

        def _normalize_port_range(port_range: Any) -> Dict[str, Any]:
            if not isinstance(port_range, dict):
                return {}
            from_port = port_range.get("fromPort")
            to_port = port_range.get("toPort")
            if from_port is None:
                from_port = port_range.get("FromPort")
            if to_port is None:
                to_port = port_range.get("ToPort")
            result: Dict[str, Any] = {}
            if from_port is not None:
                result["fromPort"] = from_port
            if to_port is not None:
                result["toPort"] = to_port
            return result

        remove_fields = {field for field in (params.get("RemoveField.N", []) or [])}
        if "Description" in remove_fields:
            rule.description = ""
        if "DestinationCidrBlock" in remove_fields:
            rule.destination_cidr_block = ""
        if "DestinationPortRange" in remove_fields:
            rule.destination_port_range = {}
        if "Protocol" in remove_fields:
            rule.protocol = None
        if "RuleAction" in remove_fields:
            rule.rule_action = ""
        if "RuleNumber" in remove_fields:
            rule.rule_number = None
        if "SourceCidrBlock" in remove_fields:
            rule.source_cidr_block = ""
        if "SourcePortRange" in remove_fields:
            rule.source_port_range = {}
        if "TrafficDirection" in remove_fields:
            rule.traffic_direction = ""

        if params.get("Description") is not None:
            rule.description = params.get("Description")
        if params.get("DestinationCidrBlock") is not None:
            rule.destination_cidr_block = params.get("DestinationCidrBlock")
        if params.get("DestinationPortRange") is not None:
            rule.destination_port_range = _normalize_port_range(params.get("DestinationPortRange"))
        if params.get("Protocol") is not None:
            rule.protocol = params.get("Protocol")
        if params.get("RuleAction") is not None:
            rule.rule_action = params.get("RuleAction")
        if params.get("RuleNumber") is not None:
            rule.rule_number = params.get("RuleNumber")
        if params.get("SourceCidrBlock") is not None:
            rule.source_cidr_block = params.get("SourceCidrBlock")
        if params.get("SourcePortRange") is not None:
            rule.source_port_range = _normalize_port_range(params.get("SourcePortRange"))
        if params.get("TrafficDirection") is not None:
            rule.traffic_direction = params.get("TrafficDirection")

        rule_data = {
            "description": rule.description,
            "destinationCidrBlock": rule.destination_cidr_block,
            "destinationPortRange": rule.destination_port_range,
            "protocol": rule.protocol,
            "ruleAction": rule.rule_action,
            "ruleNumber": rule.rule_number,
            "sourceCidrBlock": rule.source_cidr_block,
            "sourcePortRange": rule.source_port_range,
            "tagSet": rule.tag_set,
            "trafficDirection": rule.traffic_direction,
            "trafficMirrorFilterId": rule.traffic_mirror_filter_id,
            "trafficMirrorFilterRuleId": rule.traffic_mirror_filter_rule_id,
        }

        traffic_mirror_filter.egress_filter_rule_set = [
            entry
            for entry in traffic_mirror_filter.egress_filter_rule_set
            if entry.get("trafficMirrorFilterRuleId") != rule.traffic_mirror_filter_rule_id
        ]
        traffic_mirror_filter.ingress_filter_rule_set = [
            entry
            for entry in traffic_mirror_filter.ingress_filter_rule_set
            if entry.get("trafficMirrorFilterRuleId") != rule.traffic_mirror_filter_rule_id
        ]

        direction = (rule.traffic_direction or "").lower()
        if direction == "egress":
            traffic_mirror_filter.egress_filter_rule_set.append(rule_data)
        else:
            traffic_mirror_filter.ingress_filter_rule_set.append(rule_data)

        return {
            'trafficMirrorFilterRule': rule_data,
            }

    def ModifyTrafficMirrorSession(self, params: Dict[str, Any]):
        """Modifies a Traffic Mirror session."""

        error = self._require_params(params, ["TrafficMirrorSessionId"])
        if error:
            return error

        session_id = params.get("TrafficMirrorSessionId")
        session, error = self._get_resource_or_error(
            session_id,
            "InvalidTrafficMirrorSessionId.NotFound",
            "session",
        )
        if error:
            return error

        remove_fields = {field for field in (params.get("RemoveField.N", []) or [])}
        if "Description" in remove_fields:
            session.description = ""
        if "PacketLength" in remove_fields:
            session.packet_length = None
        if "SessionNumber" in remove_fields:
            session.session_number = None
        if "TrafficMirrorFilterId" in remove_fields:
            session.traffic_mirror_filter_id = ""
        if "TrafficMirrorTargetId" in remove_fields:
            session.traffic_mirror_target_id = ""
        if "VirtualNetworkId" in remove_fields:
            session.virtual_network_id = None

        traffic_mirror_filter_id = params.get("TrafficMirrorFilterId")
        if traffic_mirror_filter_id is not None:
            _, error = self._get_resource_or_error(
                traffic_mirror_filter_id,
                "InvalidTrafficMirrorFilterId.NotFound",
                "filter",
            )
            if error:
                return error
            session.traffic_mirror_filter_id = traffic_mirror_filter_id

        traffic_mirror_target_id = params.get("TrafficMirrorTargetId")
        if traffic_mirror_target_id is not None:
            _, error = self._get_resource_or_error(
                traffic_mirror_target_id,
                "InvalidTrafficMirrorTargetId.NotFound",
                "target",
            )
            if error:
                return error
            session.traffic_mirror_target_id = traffic_mirror_target_id

        if params.get("Description") is not None:
            session.description = params.get("Description")
        if params.get("PacketLength") is not None:
            session.packet_length = params.get("PacketLength")
        if params.get("SessionNumber") is not None:
            session.session_number = params.get("SessionNumber")
        if params.get("VirtualNetworkId") is not None:
            session.virtual_network_id = params.get("VirtualNetworkId")

        return {
            'trafficMirrorSession': {
                'description': session.description,
                'networkInterfaceId': session.network_interface_id,
                'ownerId': session.owner_id,
                'packetLength': session.packet_length,
                'sessionNumber': session.session_number,
                'tagSet': session.tag_set,
                'trafficMirrorFilterId': session.traffic_mirror_filter_id,
                'trafficMirrorSessionId': session.traffic_mirror_session_id,
                'trafficMirrorTargetId': session.traffic_mirror_target_id,
                'virtualNetworkId': session.virtual_network_id,
                },
            }

    def _generate_id(self, prefix: str = 'traffic') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class trafficmirroring_RequestParser:
    @staticmethod
    def parse_create_traffic_mirror_filter_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_traffic_mirror_filter_rule_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationPortRange": get_scalar(md, "DestinationPortRange"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Protocol": get_int(md, "Protocol"),
            "RuleAction": get_scalar(md, "RuleAction"),
            "RuleNumber": get_int(md, "RuleNumber"),
            "SourceCidrBlock": get_scalar(md, "SourceCidrBlock"),
            "SourcePortRange": get_scalar(md, "SourcePortRange"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TrafficDirection": get_scalar(md, "TrafficDirection"),
            "TrafficMirrorFilterId": parse_filters(md, "TrafficMirrorFilterId"),
        }

    @staticmethod
    def parse_create_traffic_mirror_session_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
            "PacketLength": get_int(md, "PacketLength"),
            "SessionNumber": get_int(md, "SessionNumber"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TrafficMirrorFilterId": parse_filters(md, "TrafficMirrorFilterId"),
            "TrafficMirrorTargetId": get_scalar(md, "TrafficMirrorTargetId"),
            "VirtualNetworkId": get_int(md, "VirtualNetworkId"),
        }

    @staticmethod
    def parse_create_traffic_mirror_target_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GatewayLoadBalancerEndpointId": get_scalar(md, "GatewayLoadBalancerEndpointId"),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
            "NetworkLoadBalancerArn": get_scalar(md, "NetworkLoadBalancerArn"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_traffic_mirror_filter_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TrafficMirrorFilterId": parse_filters(md, "TrafficMirrorFilterId"),
        }

    @staticmethod
    def parse_delete_traffic_mirror_filter_rule_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TrafficMirrorFilterRuleId": parse_filters(md, "TrafficMirrorFilterRuleId"),
        }

    @staticmethod
    def parse_delete_traffic_mirror_session_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TrafficMirrorSessionId": get_scalar(md, "TrafficMirrorSessionId"),
        }

    @staticmethod
    def parse_delete_traffic_mirror_target_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TrafficMirrorTargetId": get_scalar(md, "TrafficMirrorTargetId"),
        }

    @staticmethod
    def parse_describe_traffic_mirror_filters_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TrafficMirrorFilterId.N": parse_filters(md, "TrafficMirrorFilterId"),
        }

    @staticmethod
    def parse_describe_traffic_mirror_filter_rules_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TrafficMirrorFilterId": parse_filters(md, "TrafficMirrorFilterId"),
            "TrafficMirrorFilterRuleId.N": parse_filters(md, "TrafficMirrorFilterRuleId"),
        }

    @staticmethod
    def parse_describe_traffic_mirror_sessions_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TrafficMirrorSessionId.N": get_indexed_list(md, "TrafficMirrorSessionId"),
        }

    @staticmethod
    def parse_describe_traffic_mirror_targets_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TrafficMirrorTargetId.N": get_indexed_list(md, "TrafficMirrorTargetId"),
        }

    @staticmethod
    def parse_modify_traffic_mirror_filter_network_services_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddNetworkService.N": get_indexed_list(md, "AddNetworkService"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RemoveNetworkService.N": get_indexed_list(md, "RemoveNetworkService"),
            "TrafficMirrorFilterId": parse_filters(md, "TrafficMirrorFilterId"),
        }

    @staticmethod
    def parse_modify_traffic_mirror_filter_rule_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DestinationPortRange": get_scalar(md, "DestinationPortRange"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Protocol": get_int(md, "Protocol"),
            "RemoveField.N": get_indexed_list(md, "RemoveField"),
            "RuleAction": get_scalar(md, "RuleAction"),
            "RuleNumber": get_int(md, "RuleNumber"),
            "SourceCidrBlock": get_scalar(md, "SourceCidrBlock"),
            "SourcePortRange": get_scalar(md, "SourcePortRange"),
            "TrafficDirection": get_scalar(md, "TrafficDirection"),
            "TrafficMirrorFilterRuleId": parse_filters(md, "TrafficMirrorFilterRuleId"),
        }

    @staticmethod
    def parse_modify_traffic_mirror_session_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PacketLength": get_int(md, "PacketLength"),
            "RemoveField.N": get_indexed_list(md, "RemoveField"),
            "SessionNumber": get_int(md, "SessionNumber"),
            "TrafficMirrorFilterId": parse_filters(md, "TrafficMirrorFilterId"),
            "TrafficMirrorSessionId": get_scalar(md, "TrafficMirrorSessionId"),
            "TrafficMirrorTargetId": get_scalar(md, "TrafficMirrorTargetId"),
            "VirtualNetworkId": get_int(md, "VirtualNetworkId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateTrafficMirrorFilter": trafficmirroring_RequestParser.parse_create_traffic_mirror_filter_request,
            "CreateTrafficMirrorFilterRule": trafficmirroring_RequestParser.parse_create_traffic_mirror_filter_rule_request,
            "CreateTrafficMirrorSession": trafficmirroring_RequestParser.parse_create_traffic_mirror_session_request,
            "CreateTrafficMirrorTarget": trafficmirroring_RequestParser.parse_create_traffic_mirror_target_request,
            "DeleteTrafficMirrorFilter": trafficmirroring_RequestParser.parse_delete_traffic_mirror_filter_request,
            "DeleteTrafficMirrorFilterRule": trafficmirroring_RequestParser.parse_delete_traffic_mirror_filter_rule_request,
            "DeleteTrafficMirrorSession": trafficmirroring_RequestParser.parse_delete_traffic_mirror_session_request,
            "DeleteTrafficMirrorTarget": trafficmirroring_RequestParser.parse_delete_traffic_mirror_target_request,
            "DescribeTrafficMirrorFilters": trafficmirroring_RequestParser.parse_describe_traffic_mirror_filters_request,
            "DescribeTrafficMirrorFilterRules": trafficmirroring_RequestParser.parse_describe_traffic_mirror_filter_rules_request,
            "DescribeTrafficMirrorSessions": trafficmirroring_RequestParser.parse_describe_traffic_mirror_sessions_request,
            "DescribeTrafficMirrorTargets": trafficmirroring_RequestParser.parse_describe_traffic_mirror_targets_request,
            "ModifyTrafficMirrorFilterNetworkServices": trafficmirroring_RequestParser.parse_modify_traffic_mirror_filter_network_services_request,
            "ModifyTrafficMirrorFilterRule": trafficmirroring_RequestParser.parse_modify_traffic_mirror_filter_rule_request,
            "ModifyTrafficMirrorSession": trafficmirroring_RequestParser.parse_modify_traffic_mirror_session_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class trafficmirroring_ResponseSerializer:
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
                xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_traffic_mirror_filter_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTrafficMirrorFilterResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize trafficMirrorFilter
        _trafficMirrorFilter_key = None
        if "trafficMirrorFilter" in data:
            _trafficMirrorFilter_key = "trafficMirrorFilter"
        elif "TrafficMirrorFilter" in data:
            _trafficMirrorFilter_key = "TrafficMirrorFilter"
        if _trafficMirrorFilter_key:
            param_data = data[_trafficMirrorFilter_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorFilter>')
            xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</trafficMirrorFilter>')
        xml_parts.append(f'</CreateTrafficMirrorFilterResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_traffic_mirror_filter_rule_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTrafficMirrorFilterRuleResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize trafficMirrorFilterRule
        _trafficMirrorFilterRule_key = None
        if "trafficMirrorFilterRule" in data:
            _trafficMirrorFilterRule_key = "trafficMirrorFilterRule"
        elif "TrafficMirrorFilterRule" in data:
            _trafficMirrorFilterRule_key = "TrafficMirrorFilterRule"
        if _trafficMirrorFilterRule_key:
            param_data = data[_trafficMirrorFilterRule_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorFilterRule>')
            xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</trafficMirrorFilterRule>')
        xml_parts.append(f'</CreateTrafficMirrorFilterRuleResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_traffic_mirror_session_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTrafficMirrorSessionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize trafficMirrorSession
        _trafficMirrorSession_key = None
        if "trafficMirrorSession" in data:
            _trafficMirrorSession_key = "trafficMirrorSession"
        elif "TrafficMirrorSession" in data:
            _trafficMirrorSession_key = "TrafficMirrorSession"
        if _trafficMirrorSession_key:
            param_data = data[_trafficMirrorSession_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorSession>')
            xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</trafficMirrorSession>')
        xml_parts.append(f'</CreateTrafficMirrorSessionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_traffic_mirror_target_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTrafficMirrorTargetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize trafficMirrorTarget
        _trafficMirrorTarget_key = None
        if "trafficMirrorTarget" in data:
            _trafficMirrorTarget_key = "trafficMirrorTarget"
        elif "TrafficMirrorTarget" in data:
            _trafficMirrorTarget_key = "TrafficMirrorTarget"
        if _trafficMirrorTarget_key:
            param_data = data[_trafficMirrorTarget_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorTarget>')
            xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</trafficMirrorTarget>')
        xml_parts.append(f'</CreateTrafficMirrorTargetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_traffic_mirror_filter_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTrafficMirrorFilterResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize trafficMirrorFilterId
        _trafficMirrorFilterId_key = None
        if "trafficMirrorFilterId" in data:
            _trafficMirrorFilterId_key = "trafficMirrorFilterId"
        elif "TrafficMirrorFilterId" in data:
            _trafficMirrorFilterId_key = "TrafficMirrorFilterId"
        if _trafficMirrorFilterId_key:
            param_data = data[_trafficMirrorFilterId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorFilterId>{esc(str(param_data))}</trafficMirrorFilterId>')
        xml_parts.append(f'</DeleteTrafficMirrorFilterResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_traffic_mirror_filter_rule_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTrafficMirrorFilterRuleResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize trafficMirrorFilterRuleId
        _trafficMirrorFilterRuleId_key = None
        if "trafficMirrorFilterRuleId" in data:
            _trafficMirrorFilterRuleId_key = "trafficMirrorFilterRuleId"
        elif "TrafficMirrorFilterRuleId" in data:
            _trafficMirrorFilterRuleId_key = "TrafficMirrorFilterRuleId"
        if _trafficMirrorFilterRuleId_key:
            param_data = data[_trafficMirrorFilterRuleId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorFilterRuleId>{esc(str(param_data))}</trafficMirrorFilterRuleId>')
        xml_parts.append(f'</DeleteTrafficMirrorFilterRuleResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_traffic_mirror_session_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTrafficMirrorSessionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize trafficMirrorSessionId
        _trafficMirrorSessionId_key = None
        if "trafficMirrorSessionId" in data:
            _trafficMirrorSessionId_key = "trafficMirrorSessionId"
        elif "TrafficMirrorSessionId" in data:
            _trafficMirrorSessionId_key = "TrafficMirrorSessionId"
        if _trafficMirrorSessionId_key:
            param_data = data[_trafficMirrorSessionId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorSessionId>{esc(str(param_data))}</trafficMirrorSessionId>')
        xml_parts.append(f'</DeleteTrafficMirrorSessionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_traffic_mirror_target_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTrafficMirrorTargetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize trafficMirrorTargetId
        _trafficMirrorTargetId_key = None
        if "trafficMirrorTargetId" in data:
            _trafficMirrorTargetId_key = "trafficMirrorTargetId"
        elif "TrafficMirrorTargetId" in data:
            _trafficMirrorTargetId_key = "TrafficMirrorTargetId"
        if _trafficMirrorTargetId_key:
            param_data = data[_trafficMirrorTargetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorTargetId>{esc(str(param_data))}</trafficMirrorTargetId>')
        xml_parts.append(f'</DeleteTrafficMirrorTargetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_traffic_mirror_filters_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTrafficMirrorFiltersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize trafficMirrorFilterSet
        _trafficMirrorFilterSet_key = None
        if "trafficMirrorFilterSet" in data:
            _trafficMirrorFilterSet_key = "trafficMirrorFilterSet"
        elif "TrafficMirrorFilterSet" in data:
            _trafficMirrorFilterSet_key = "TrafficMirrorFilterSet"
        elif "TrafficMirrorFilters" in data:
            _trafficMirrorFilterSet_key = "TrafficMirrorFilters"
        if _trafficMirrorFilterSet_key:
            param_data = data[_trafficMirrorFilterSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<trafficMirrorFilterSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</trafficMirrorFilterSet>')
            else:
                xml_parts.append(f'{indent_str}<trafficMirrorFilterSet/>')
        xml_parts.append(f'</DescribeTrafficMirrorFiltersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_traffic_mirror_filter_rules_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTrafficMirrorFilterRulesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize trafficMirrorFilterRuleSet
        _trafficMirrorFilterRuleSet_key = None
        if "trafficMirrorFilterRuleSet" in data:
            _trafficMirrorFilterRuleSet_key = "trafficMirrorFilterRuleSet"
        elif "TrafficMirrorFilterRuleSet" in data:
            _trafficMirrorFilterRuleSet_key = "TrafficMirrorFilterRuleSet"
        elif "TrafficMirrorFilterRules" in data:
            _trafficMirrorFilterRuleSet_key = "TrafficMirrorFilterRules"
        if _trafficMirrorFilterRuleSet_key:
            param_data = data[_trafficMirrorFilterRuleSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<trafficMirrorFilterRuleSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</trafficMirrorFilterRuleSet>')
            else:
                xml_parts.append(f'{indent_str}<trafficMirrorFilterRuleSet/>')
        xml_parts.append(f'</DescribeTrafficMirrorFilterRulesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_traffic_mirror_sessions_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTrafficMirrorSessionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize trafficMirrorSessionSet
        _trafficMirrorSessionSet_key = None
        if "trafficMirrorSessionSet" in data:
            _trafficMirrorSessionSet_key = "trafficMirrorSessionSet"
        elif "TrafficMirrorSessionSet" in data:
            _trafficMirrorSessionSet_key = "TrafficMirrorSessionSet"
        elif "TrafficMirrorSessions" in data:
            _trafficMirrorSessionSet_key = "TrafficMirrorSessions"
        if _trafficMirrorSessionSet_key:
            param_data = data[_trafficMirrorSessionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<trafficMirrorSessionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</trafficMirrorSessionSet>')
            else:
                xml_parts.append(f'{indent_str}<trafficMirrorSessionSet/>')
        xml_parts.append(f'</DescribeTrafficMirrorSessionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_traffic_mirror_targets_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTrafficMirrorTargetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize trafficMirrorTargetSet
        _trafficMirrorTargetSet_key = None
        if "trafficMirrorTargetSet" in data:
            _trafficMirrorTargetSet_key = "trafficMirrorTargetSet"
        elif "TrafficMirrorTargetSet" in data:
            _trafficMirrorTargetSet_key = "TrafficMirrorTargetSet"
        elif "TrafficMirrorTargets" in data:
            _trafficMirrorTargetSet_key = "TrafficMirrorTargets"
        if _trafficMirrorTargetSet_key:
            param_data = data[_trafficMirrorTargetSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<trafficMirrorTargetSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</trafficMirrorTargetSet>')
            else:
                xml_parts.append(f'{indent_str}<trafficMirrorTargetSet/>')
        xml_parts.append(f'</DescribeTrafficMirrorTargetsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_traffic_mirror_filter_network_services_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyTrafficMirrorFilterNetworkServicesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize trafficMirrorFilter
        _trafficMirrorFilter_key = None
        if "trafficMirrorFilter" in data:
            _trafficMirrorFilter_key = "trafficMirrorFilter"
        elif "TrafficMirrorFilter" in data:
            _trafficMirrorFilter_key = "TrafficMirrorFilter"
        if _trafficMirrorFilter_key:
            param_data = data[_trafficMirrorFilter_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorFilter>')
            xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</trafficMirrorFilter>')
        xml_parts.append(f'</ModifyTrafficMirrorFilterNetworkServicesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_traffic_mirror_filter_rule_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyTrafficMirrorFilterRuleResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize trafficMirrorFilterRule
        _trafficMirrorFilterRule_key = None
        if "trafficMirrorFilterRule" in data:
            _trafficMirrorFilterRule_key = "trafficMirrorFilterRule"
        elif "TrafficMirrorFilterRule" in data:
            _trafficMirrorFilterRule_key = "TrafficMirrorFilterRule"
        if _trafficMirrorFilterRule_key:
            param_data = data[_trafficMirrorFilterRule_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorFilterRule>')
            xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</trafficMirrorFilterRule>')
        xml_parts.append(f'</ModifyTrafficMirrorFilterRuleResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_traffic_mirror_session_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyTrafficMirrorSessionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize trafficMirrorSession
        _trafficMirrorSession_key = None
        if "trafficMirrorSession" in data:
            _trafficMirrorSession_key = "trafficMirrorSession"
        elif "TrafficMirrorSession" in data:
            _trafficMirrorSession_key = "TrafficMirrorSession"
        if _trafficMirrorSession_key:
            param_data = data[_trafficMirrorSession_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<trafficMirrorSession>')
            xml_parts.extend(trafficmirroring_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</trafficMirrorSession>')
        xml_parts.append(f'</ModifyTrafficMirrorSessionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateTrafficMirrorFilter": trafficmirroring_ResponseSerializer.serialize_create_traffic_mirror_filter_response,
            "CreateTrafficMirrorFilterRule": trafficmirroring_ResponseSerializer.serialize_create_traffic_mirror_filter_rule_response,
            "CreateTrafficMirrorSession": trafficmirroring_ResponseSerializer.serialize_create_traffic_mirror_session_response,
            "CreateTrafficMirrorTarget": trafficmirroring_ResponseSerializer.serialize_create_traffic_mirror_target_response,
            "DeleteTrafficMirrorFilter": trafficmirroring_ResponseSerializer.serialize_delete_traffic_mirror_filter_response,
            "DeleteTrafficMirrorFilterRule": trafficmirroring_ResponseSerializer.serialize_delete_traffic_mirror_filter_rule_response,
            "DeleteTrafficMirrorSession": trafficmirroring_ResponseSerializer.serialize_delete_traffic_mirror_session_response,
            "DeleteTrafficMirrorTarget": trafficmirroring_ResponseSerializer.serialize_delete_traffic_mirror_target_response,
            "DescribeTrafficMirrorFilters": trafficmirroring_ResponseSerializer.serialize_describe_traffic_mirror_filters_response,
            "DescribeTrafficMirrorFilterRules": trafficmirroring_ResponseSerializer.serialize_describe_traffic_mirror_filter_rules_response,
            "DescribeTrafficMirrorSessions": trafficmirroring_ResponseSerializer.serialize_describe_traffic_mirror_sessions_response,
            "DescribeTrafficMirrorTargets": trafficmirroring_ResponseSerializer.serialize_describe_traffic_mirror_targets_response,
            "ModifyTrafficMirrorFilterNetworkServices": trafficmirroring_ResponseSerializer.serialize_modify_traffic_mirror_filter_network_services_response,
            "ModifyTrafficMirrorFilterRule": trafficmirroring_ResponseSerializer.serialize_modify_traffic_mirror_filter_rule_response,
            "ModifyTrafficMirrorSession": trafficmirroring_ResponseSerializer.serialize_modify_traffic_mirror_session_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

