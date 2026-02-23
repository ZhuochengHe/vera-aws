"""
Centralized emulator state store shared across all resource backends.

Generated from the dependency graph — one store per resource spec.
All backends reference this singleton so cross-resource lookups and
dependency validation work correctly.
"""

from typing import Dict, Any, Optional


class EC2State:
    """Singleton state store for all resource backends."""

    _instance: Optional["EC2State"] = None

    @classmethod
    def get(cls) -> "EC2State":
        """Return the shared singleton, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Destroy the singleton (for testing / gateway restart)."""
        cls._instance = None

    def __init__(self) -> None:
        self.account_attributes: Dict[str, Any] = {}
        self.afis: Dict[str, Any] = {}
        self.amis: Dict[str, Any] = {}
        self.authorization_rules: Dict[str, Any] = {}
        self.aws_marketplace: Dict[str, Any] = {}
        self.block_public_access: Dict[str, Any] = {}
        self.bundle_tasks: Dict[str, Any] = {}
        self.byoasn: Dict[str, Any] = {}
        self.byoip: Dict[str, Any] = {}
        self.capacity_reservations: Dict[str, Any] = {}
        self.carrier_gateways: Dict[str, Any] = {}
        self.certificate_revocation_lists: Dict[str, Any] = {}
        self.client_connections: Dict[str, Any] = {}
        self.client_vpn_endpoints: Dict[str, Any] = {}
        self.configuration_files: Dict[str, Any] = {}
        self.customer_gateways: Dict[str, Any] = {}
        self.customer_owned_ip_addresses: Dict[str, Any] = {}
        self.declarative_policies_account_status_report: Dict[str, Any] = {}
        self.dedicated_hosts: Dict[str, Any] = {}
        self.dep_graph_overrides: Dict[str, Any] = {}
        self.dhcp_options: Dict[str, Any] = {}
        self.ec2_fleet: Dict[str, Any] = {}
        self.ec2_instance_connect_endpoints: Dict[str, Any] = {}
        self.ec2_topology: Dict[str, Any] = {}
        self.elastic_graphics: Dict[str, Any] = {}
        self.elastic_ip_addresses: Dict[str, Any] = {}
        self.elastic_network_interfaces: Dict[str, Any] = {}
        self.encryption: Dict[str, Any] = {}
        self.event_notifications: Dict[str, Any] = {}
        self.event_windows_for_scheduled_events: Dict[str, Any] = {}
        self.fast_snapshot_restores: Dict[str, Any] = {}
        self.infrastructure_performance: Dict[str, Any] = {}
        self.instance_types: Dict[str, Any] = {}
        self.instances: Dict[str, Any] = {}
        self.internet_gateways: Dict[str, Any] = {}
        self.ipams: Dict[str, Any] = {}
        self.key_pairs: Dict[str, Any] = {}
        self.launch_templates: Dict[str, Any] = {}
        self.link_aggregation_groups: Dict[str, Any] = {}
        self.local_gateways: Dict[str, Any] = {}
        self.managed_prefix_lists: Dict[str, Any] = {}
        self.nat_gateways: Dict[str, Any] = {}
        self.network_access_analyzer: Dict[str, Any] = {}
        self.network_acls: Dict[str, Any] = {}
        self.nitro_tpm: Dict[str, Any] = {}
        self.placement_groups: Dict[str, Any] = {}
        self.pools: Dict[str, Any] = {}
        self.reachability_analyzer: Dict[str, Any] = {}
        self.regions_and_zones: Dict[str, Any] = {}
        self.reserved_instances: Dict[str, Any] = {}
        self.resource_discoveries: Dict[str, Any] = {}
        self.resource_ids: Dict[str, Any] = {}
        self.route_servers: Dict[str, Any] = {}
        self.route_tables: Dict[str, Any] = {}
        self.routes: Dict[str, Any] = {}
        self.scheduled_instances: Dict[str, Any] = {}
        self.scopes: Dict[str, Any] = {}
        self.security_groups: Dict[str, Any] = {}
        self.serial_console: Dict[str, Any] = {}
        self.service_links: Dict[str, Any] = {}
        self.snapshots: Dict[str, Any] = {}
        self.spot_fleet: Dict[str, Any] = {}
        self.spot_instances: Dict[str, Any] = {}
        self.subnets: Dict[str, Any] = {}
        self.tags: Dict[str, Any] = {}
        self.target_networks: Dict[str, Any] = {}
        self.traffic_mirroring: Dict[str, Any] = {}
        self.transit_gateway_connect: Dict[str, Any] = {}
        self.transit_gateway_multicast: Dict[str, Any] = {}
        self.transit_gateway_peering_attachments: Dict[str, Any] = {}
        self.transit_gateway_policy_tables: Dict[str, Any] = {}
        self.transit_gateway_route_tables: Dict[str, Any] = {}
        self.transit_gateways: Dict[str, Any] = {}
        self.verified_access_endpoints: Dict[str, Any] = {}
        self.verified_access_groups: Dict[str, Any] = {}
        self.verified_access_instances: Dict[str, Any] = {}
        self.verified_access_logs: Dict[str, Any] = {}
        self.verified_access_trust_providers: Dict[str, Any] = {}
        self.virtual_private_gateway_routes: Dict[str, Any] = {}
        self.virtual_private_gateways: Dict[str, Any] = {}
        self.vm_export: Dict[str, Any] = {}
        self.vm_import: Dict[str, Any] = {}
        self.volumes: Dict[str, Any] = {}
        self.vpc_endpoint_services: Dict[str, Any] = {}
        self.vpc_endpoints: Dict[str, Any] = {}
        self.vpc_flow_logs: Dict[str, Any] = {}
        self.vpc_peering: Dict[str, Any] = {}
        self.vpcs: Dict[str, Any] = {}
        self.vpn_concentrators: Dict[str, Any] = {}
        self.vpn_connections: Dict[str, Any] = {}

