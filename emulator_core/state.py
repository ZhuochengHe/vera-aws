from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class ResourceState(Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    DELETING = "deleting"
    DELETED = "deleted"
    NONEXISTENT = "non-existent"
    # ... add others

class ErrorCode(Enum):
    INVALID_PARAMETER_VALUE = "InvalidParameterValue"
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    DEPENDENCY_VIOLATION = "DependencyViolation"
    # ... add others

@dataclass
class EmulatorState:
    """
    Singleton-like state container holding all resources.
    Passed to every backend service.
    """
    # Region configuration
    region: str = "us-east-1"

    # Network
    vpcs: Dict[str, Any] = field(default_factory=dict)
    subnets: Dict[str, Any] = field(default_factory=dict)
    security_groups: Dict[str, Any] = field(default_factory=dict)
    route_tables: Dict[str, Any] = field(default_factory=dict)
    internet_gateways: Dict[str, Any] = field(default_factory=dict)
    nat_gateways: Dict[str, Any] = field(default_factory=dict)
    network_acls: Dict[str, Any] = field(default_factory=dict)
    vpc_endpoints: Dict[str, Any] = field(default_factory=dict)
    vpc_flow_logs: Dict[str, Any] = field(default_factory=dict)
    vpn_connections: Dict[str, Any] = field(default_factory=dict)
    vpn_gateways: Dict[str, Any] = field(default_factory=dict)
    customer_gateways: Dict[str, Any] = field(default_factory=dict)
    elastic_network_interfaces: Dict[str, Any] = field(default_factory=dict)
    egress_only_internet_gateways: Dict[str, Any] = field(default_factory=dict)

    # Compute
    instances: Dict[str, Any] = field(default_factory=dict)
    images: Dict[str, Any] = field(default_factory=dict)
    amis: Dict[str, Any] = field(default_factory=dict)
    volumes: Dict[str, Any] = field(default_factory=dict)
    snapshots: Dict[str, Any] = field(default_factory=dict)
    key_pairs: Dict[str, Any] = field(default_factory=dict)
    launch_templates: Dict[str, Any] = field(default_factory=dict)
    placement_groups: Dict[str, Any] = field(default_factory=dict)

    # IAM integration
    iam_instance_profile_associations: Dict[str, Any] = field(default_factory=dict)

    # Transit
    transit_gateways: Dict[str, Any] = field(default_factory=dict)
    transit_gateway_attachments: Dict[str, Any] = field(default_factory=dict)
    transit_gateway_route_tables: Dict[str, Any] = field(default_factory=dict)

    # Addresses
    addresses: Dict[str, Any] = field(default_factory=dict)
    elastic_ips: Dict[str, Any] = field(default_factory=dict)

    # Regions and Zones
    regions_and_zones: Dict[str, Any] = field(default_factory=dict)

    # Tags
    tags: Dict[str, Any] = field(default_factory=dict)

    # ... expands for all 89 resources

    def get_resource(self, resource_id: str) -> Optional[Any]:
        """Generic lookup for any resource ID"""
        if resource_id.startswith("vpc-"): return self.vpcs.get(resource_id)
        if resource_id.startswith("subnet-"): return self.subnets.get(resource_id)
        if resource_id.startswith("i-"): return self.instances.get(resource_id)
        return None
