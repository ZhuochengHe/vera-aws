"""
Centralized GCP Compute emulator state — shared across all resource backends.
"""
from __future__ import annotations
from typing import Dict, Any, Optional


class GCPState:
    _instance: Optional["GCPState"] = None

    @classmethod
    def get(cls) -> "GCPState":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:  # for testing
        cls._instance = None

    def __init__(self) -> None:
        self.addresses: Dict[str, Any] = {}
        self.autoscalers: Dict[str, Any] = {}
        self.backend_buckets: Dict[str, Any] = {}
        self.backend_services: Dict[str, Any] = {}
        self.disks: Dict[str, Any] = {}
        self.external_vpn_gatewaies: Dict[str, Any] = {}
        self.firewall_policies: Dict[str, Any] = {}
        self.firewalls: Dict[str, Any] = {}
        self.forwarding_rules: Dict[str, Any] = {}
        self.future_reservations: Dict[str, Any] = {}
        self.global_addresses: Dict[str, Any] = {}
        self.global_forwarding_rules: Dict[str, Any] = {}
        self.global_network_endpoint_groups: Dict[str, Any] = {}
        self.global_public_delegated_prefixes: Dict[str, Any] = {}
        self.health_checks: Dict[str, Any] = {}
        self.http_health_checks: Dict[str, Any] = {}
        self.https_health_checks: Dict[str, Any] = {}
        self.image_family_views: Dict[str, Any] = {}
        self.images: Dict[str, Any] = {}
        self.instance_group_manager_resize_requests: Dict[str, Any] = {}
        self.instance_group_managers: Dict[str, Any] = {}
        self.instance_groups: Dict[str, Any] = {}
        self.instance_settings: Dict[str, Any] = {}
        self.instance_templates: Dict[str, Any] = {}
        self.instances: Dict[str, Any] = {}
        self.instant_snapshots: Dict[str, Any] = {}
        self.interconnect_attachment_groups: Dict[str, Any] = {}
        self.interconnect_attachments: Dict[str, Any] = {}
        self.interconnect_groups: Dict[str, Any] = {}
        self.interconnects: Dict[str, Any] = {}
        self.license_codes: Dict[str, Any] = {}
        self.licenses: Dict[str, Any] = {}
        self.machine_images: Dict[str, Any] = {}
        self.network_attachments: Dict[str, Any] = {}
        self.network_edge_security_services: Dict[str, Any] = {}
        self.network_endpoint_groups: Dict[str, Any] = {}
        self.network_firewall_policies: Dict[str, Any] = {}
        self.networks: Dict[str, Any] = {}
        self.node_groups: Dict[str, Any] = {}
        self.node_templates: Dict[str, Any] = {}
        self.operations: Dict[str, Any] = {}
        self.packet_mirrorings: Dict[str, Any] = {}
        self.projects: Dict[str, Any] = {}
        self.public_advertised_prefixes: Dict[str, Any] = {}
        self.public_delegated_prefixes: Dict[str, Any] = {}
        self.region_autoscalers: Dict[str, Any] = {}
        self.region_backend_services: Dict[str, Any] = {}
        self.region_commitments: Dict[str, Any] = {}
        self.region_disks: Dict[str, Any] = {}
        self.region_health_check_services: Dict[str, Any] = {}
        self.region_health_checks: Dict[str, Any] = {}
        self.region_instance_group_managers: Dict[str, Any] = {}
        self.region_instance_groups: Dict[str, Any] = {}
        self.region_instance_templates: Dict[str, Any] = {}
        self.region_instances: Dict[str, Any] = {}
        self.region_instant_snapshots: Dict[str, Any] = {}
        self.region_network_endpoint_groups: Dict[str, Any] = {}
        self.region_network_firewall_policies: Dict[str, Any] = {}
        self.region_notification_endpoints: Dict[str, Any] = {}
        self.region_security_policies: Dict[str, Any] = {}
        self.region_ssl_certificates: Dict[str, Any] = {}
        self.region_ssl_policies: Dict[str, Any] = {}
        self.region_target_http_proxies: Dict[str, Any] = {}
        self.region_target_https_proxies: Dict[str, Any] = {}
        self.region_target_tcp_proxies: Dict[str, Any] = {}
        self.region_url_maps: Dict[str, Any] = {}
        self.region_zones: Dict[str, Any] = {}
        self.regions: Dict[str, Any] = {}
        self.reservations: Dict[str, Any] = {}
        self.resource_policies: Dict[str, Any] = {}
        self.routers: Dict[str, Any] = {}
        self.routes: Dict[str, Any] = {}
        self.security_policies: Dict[str, Any] = {}
        self.service_attachments: Dict[str, Any] = {}
        self.snapshot_settings: Dict[str, Any] = {}
        self.snapshots: Dict[str, Any] = {}
        self.ssl_certificates: Dict[str, Any] = {}
        self.ssl_policies: Dict[str, Any] = {}
        self.storage_pools: Dict[str, Any] = {}
        self.subnetworks: Dict[str, Any] = {}
        self.target_grpc_proxies: Dict[str, Any] = {}
        self.target_http_proxies: Dict[str, Any] = {}
        self.target_https_proxies: Dict[str, Any] = {}
        self.target_instances: Dict[str, Any] = {}
        self.target_pools: Dict[str, Any] = {}
        self.target_ssl_proxies: Dict[str, Any] = {}
        self.target_tcp_proxies: Dict[str, Any] = {}
        self.target_vpn_gatewaies: Dict[str, Any] = {}
        self.url_maps: Dict[str, Any] = {}
        self.vpn_gatewaies: Dict[str, Any] = {}
        self.vpn_tunnels: Dict[str, Any] = {}
        self.zones: Dict[str, Any] = {}

