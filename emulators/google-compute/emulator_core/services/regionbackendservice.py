from __future__ import annotations
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid
import random
import json as _json

from ..utils import (
    create_gcp_error, is_error_response,
    make_operation, parse_labels, get_body_param,
)
from ..state import GCPState

@dataclass
class RegionBackendService:
    enable_cdn: bool = False
    edge_security_policy: str = ""
    port_name: str = ""
    outlier_detection: Dict[str, Any] = field(default_factory=dict)
    security_policy: str = ""
    fingerprint: str = ""
    cdn_policy: Dict[str, Any] = field(default_factory=dict)
    protocol: str = ""
    region: str = ""
    external_managed_migration_state: str = ""
    tls_settings: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    custom_request_headers: List[Any] = field(default_factory=list)
    service_bindings: List[Any] = field(default_factory=list)
    session_affinity: str = ""
    circuit_breakers: Dict[str, Any] = field(default_factory=dict)
    connection_tracking_policy: Dict[str, Any] = field(default_factory=dict)
    custom_response_headers: List[Any] = field(default_factory=list)
    metadatas: Dict[str, Any] = field(default_factory=dict)
    health_checks: List[Any] = field(default_factory=list)
    description: str = ""
    affinity_cookie_ttl_sec: int = 0
    locality_lb_policies: List[Any] = field(default_factory=list)
    security_settings: Dict[str, Any] = field(default_factory=dict)
    strong_session_affinity_cookie: Dict[str, Any] = field(default_factory=dict)
    connection_draining: Dict[str, Any] = field(default_factory=dict)
    iap: Dict[str, Any] = field(default_factory=dict)
    backends: List[Any] = field(default_factory=list)
    failover_policy: Dict[str, Any] = field(default_factory=dict)
    network: str = ""
    service_lb_policy: str = ""
    ha_policy: Dict[str, Any] = field(default_factory=dict)
    log_config: Dict[str, Any] = field(default_factory=dict)
    port: int = 0
    used_by: List[Any] = field(default_factory=list)
    timeout_sec: int = 0
    locality_lb_policy: str = ""
    consistent_hash: Dict[str, Any] = field(default_factory=dict)
    load_balancing_scheme: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    ip_address_selection_policy: str = ""
    network_pass_through_lb_traffic_policy: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    external_managed_migration_testing_percentage: Any = None
    custom_metrics: List[Any] = field(default_factory=list)
    compression_mode: str = ""
    subsetting: Dict[str, Any] = field(default_factory=dict)
    max_stream_duration: Dict[str, Any] = field(default_factory=dict)
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["enableCDN"] = self.enable_cdn
        if self.edge_security_policy is not None and self.edge_security_policy != "":
            d["edgeSecurityPolicy"] = self.edge_security_policy
        if self.port_name is not None and self.port_name != "":
            d["portName"] = self.port_name
        d["outlierDetection"] = self.outlier_detection
        if self.security_policy is not None and self.security_policy != "":
            d["securityPolicy"] = self.security_policy
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        d["cdnPolicy"] = self.cdn_policy
        if self.protocol is not None and self.protocol != "":
            d["protocol"] = self.protocol
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.external_managed_migration_state is not None and self.external_managed_migration_state != "":
            d["externalManagedMigrationState"] = self.external_managed_migration_state
        d["tlsSettings"] = self.tls_settings
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["customRequestHeaders"] = self.custom_request_headers
        d["serviceBindings"] = self.service_bindings
        if self.session_affinity is not None and self.session_affinity != "":
            d["sessionAffinity"] = self.session_affinity
        d["circuitBreakers"] = self.circuit_breakers
        d["connectionTrackingPolicy"] = self.connection_tracking_policy
        d["customResponseHeaders"] = self.custom_response_headers
        d["metadatas"] = self.metadatas
        d["healthChecks"] = self.health_checks
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.affinity_cookie_ttl_sec is not None and self.affinity_cookie_ttl_sec != 0:
            d["affinityCookieTtlSec"] = self.affinity_cookie_ttl_sec
        d["localityLbPolicies"] = self.locality_lb_policies
        d["securitySettings"] = self.security_settings
        d["strongSessionAffinityCookie"] = self.strong_session_affinity_cookie
        d["connectionDraining"] = self.connection_draining
        d["iap"] = self.iap
        d["backends"] = self.backends
        d["failoverPolicy"] = self.failover_policy
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.service_lb_policy is not None and self.service_lb_policy != "":
            d["serviceLbPolicy"] = self.service_lb_policy
        d["haPolicy"] = self.ha_policy
        d["logConfig"] = self.log_config
        if self.port is not None and self.port != 0:
            d["port"] = self.port
        d["usedBy"] = self.used_by
        if self.timeout_sec is not None and self.timeout_sec != 0:
            d["timeoutSec"] = self.timeout_sec
        if self.locality_lb_policy is not None and self.locality_lb_policy != "":
            d["localityLbPolicy"] = self.locality_lb_policy
        d["consistentHash"] = self.consistent_hash
        if self.load_balancing_scheme is not None and self.load_balancing_scheme != "":
            d["loadBalancingScheme"] = self.load_balancing_scheme
        d["params"] = self.params
        if self.ip_address_selection_policy is not None and self.ip_address_selection_policy != "":
            d["ipAddressSelectionPolicy"] = self.ip_address_selection_policy
        d["networkPassThroughLbTrafficPolicy"] = self.network_pass_through_lb_traffic_policy
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.external_managed_migration_testing_percentage is not None and self.external_managed_migration_testing_percentage != None:
            d["externalManagedMigrationTestingPercentage"] = self.external_managed_migration_testing_percentage
        d["customMetrics"] = self.custom_metrics
        if self.compression_mode is not None and self.compression_mode != "":
            d["compressionMode"] = self.compression_mode
        d["subsetting"] = self.subsetting
        d["maxStreamDuration"] = self.max_stream_duration
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regionbackendservice"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionBackendService_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_backend_services  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-backend-service") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a regional BackendService resource in the specified project using
the data included in the request. For more information, see
Backend services overview."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("BackendService") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'BackendService' not found",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )
        if name in self.resources:
            return create_gcp_error(
                409,
                f"BackendService '{name}' already exists",
                "ALREADY_EXISTS",
            )

        network = body.get("network") or ""
        if network and not self.state.networks.get(network):
            return create_gcp_error(
                404,
                f"Network '{network}' not found",
                "NOT_FOUND",
            )
        security_policy = body.get("securityPolicy") or ""
        if security_policy and not (
            self.state.security_policies.get(security_policy)
            or self.state.region_security_policies.get(security_policy)
        ):
            return create_gcp_error(
                404,
                f"Security policy '{security_policy}' not found",
                "NOT_FOUND",
            )
        edge_security_policy = body.get("edgeSecurityPolicy") or ""
        if edge_security_policy and not (
            self.state.security_policies.get(edge_security_policy)
            or self.state.region_security_policies.get(edge_security_policy)
        ):
            return create_gcp_error(
                404,
                f"Security policy '{edge_security_policy}' not found",
                "NOT_FOUND",
            )
        health_checks = body.get("healthChecks") or []
        for health_check in health_checks:
            if not (
                self.state.health_checks.get(health_check)
                or self.state.region_health_checks.get(health_check)
                or self.state.http_health_checks.get(health_check)
                or self.state.https_health_checks.get(health_check)
                or self.state.region_health_check_services.get(health_check)
            ):
                return create_gcp_error(
                    404,
                    f"Health check '{health_check}' not found",
                    "NOT_FOUND",
                )

        resource = RegionBackendService(
            enable_cdn=body.get("enableCDN") or False,
            edge_security_policy=edge_security_policy,
            port_name=body.get("portName") or "",
            outlier_detection=body.get("outlierDetection") or {},
            security_policy=security_policy,
            fingerprint=body.get("fingerprint") or "",
            cdn_policy=body.get("cdnPolicy") or {},
            protocol=body.get("protocol") or "",
            region=region,
            external_managed_migration_state=body.get("externalManagedMigrationState")
            or "",
            tls_settings=body.get("tlsSettings") or {},
            name=name,
            custom_request_headers=body.get("customRequestHeaders") or [],
            service_bindings=body.get("serviceBindings") or [],
            session_affinity=body.get("sessionAffinity") or "",
            circuit_breakers=body.get("circuitBreakers") or {},
            connection_tracking_policy=body.get("connectionTrackingPolicy") or {},
            custom_response_headers=body.get("customResponseHeaders") or [],
            metadatas=body.get("metadatas") or {},
            health_checks=health_checks,
            description=body.get("description") or "",
            affinity_cookie_ttl_sec=body.get("affinityCookieTtlSec") or 0,
            locality_lb_policies=body.get("localityLbPolicies") or [],
            security_settings=body.get("securitySettings") or {},
            strong_session_affinity_cookie=body.get("strongSessionAffinityCookie")
            or {},
            connection_draining=body.get("connectionDraining") or {},
            iap=body.get("iap") or {},
            backends=body.get("backends") or [],
            failover_policy=body.get("failoverPolicy") or {},
            network=network,
            service_lb_policy=body.get("serviceLbPolicy") or "",
            ha_policy=body.get("haPolicy") or {},
            log_config=body.get("logConfig") or {},
            port=body.get("port") or 0,
            used_by=body.get("usedBy") or [],
            timeout_sec=body.get("timeoutSec") or 0,
            locality_lb_policy=body.get("localityLbPolicy") or "",
            consistent_hash=body.get("consistentHash") or {},
            load_balancing_scheme=body.get("loadBalancingScheme") or "",
            params=body.get("params") or {},
            ip_address_selection_policy=body.get("ipAddressSelectionPolicy") or "",
            network_pass_through_lb_traffic_policy=body.get(
                "networkPassThroughLbTrafficPolicy"
            )
            or {},
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            external_managed_migration_testing_percentage=body.get(
                "externalManagedMigrationTestingPercentage"
            ),
            custom_metrics=body.get("customMetrics") or [],
            compression_mode=body.get("compressionMode") or "",
            subsetting=body.get("subsetting") or {},
            max_stream_duration=body.get("maxStreamDuration") or {},
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = (
            f"projects/{project}/regions/{region}/backendServices/{resource.name}"
        )
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified regional BackendService resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        backend_service_name = params.get("backendService")
        if not backend_service_name:
            return create_gcp_error(
                400,
                "Required field 'backendService' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(backend_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of regional BackendService resources available to the
specified project in the given region."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]
        return {
            "kind": "compute#regionbackendserviceList",
            "id": f"projects/{project}/regions/{region}/backendServices",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified regional BackendService resource with the data
included in the request. For more information,
see 
Backend services overview."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        backend_service_name = params.get("backendService")
        if not backend_service_name:
            return create_gcp_error(
                400,
                "Required field 'backendService' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("BackendService") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'BackendService' not found",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name") or backend_service_name

        resource = self.resources.get(backend_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        if body_name != backend_service_name and body_name in self.resources:
            return create_gcp_error(
                409,
                f"BackendService '{body_name}' already exists",
                "ALREADY_EXISTS",
            )

        network = body.get("network") or ""
        if network and not self.state.networks.get(network):
            return create_gcp_error(
                404,
                f"Network '{network}' not found",
                "NOT_FOUND",
            )
        security_policy = body.get("securityPolicy") or ""
        if security_policy and not (
            self.state.security_policies.get(security_policy)
            or self.state.region_security_policies.get(security_policy)
        ):
            return create_gcp_error(
                404,
                f"Security policy '{security_policy}' not found",
                "NOT_FOUND",
            )
        edge_security_policy = body.get("edgeSecurityPolicy") or ""
        if edge_security_policy and not (
            self.state.security_policies.get(edge_security_policy)
            or self.state.region_security_policies.get(edge_security_policy)
        ):
            return create_gcp_error(
                404,
                f"Security policy '{edge_security_policy}' not found",
                "NOT_FOUND",
            )
        health_checks = body.get("healthChecks") or []
        for health_check in health_checks:
            if not (
                self.state.health_checks.get(health_check)
                or self.state.region_health_checks.get(health_check)
                or self.state.http_health_checks.get(health_check)
                or self.state.https_health_checks.get(health_check)
                or self.state.region_health_check_services.get(health_check)
            ):
                return create_gcp_error(
                    404,
                    f"Health check '{health_check}' not found",
                    "NOT_FOUND",
                )

        resource.enable_cdn = body.get("enableCDN") or False
        resource.edge_security_policy = edge_security_policy
        resource.port_name = body.get("portName") or ""
        resource.outlier_detection = body.get("outlierDetection") or {}
        resource.security_policy = security_policy
        resource.fingerprint = body.get("fingerprint") or ""
        resource.cdn_policy = body.get("cdnPolicy") or {}
        resource.protocol = body.get("protocol") or ""
        resource.region = body.get("region") or region
        resource.external_managed_migration_state = body.get(
            "externalManagedMigrationState"
        ) or ""
        resource.tls_settings = body.get("tlsSettings") or {}
        resource.name = body_name
        resource.custom_request_headers = body.get("customRequestHeaders") or []
        resource.service_bindings = body.get("serviceBindings") or []
        resource.session_affinity = body.get("sessionAffinity") or ""
        resource.circuit_breakers = body.get("circuitBreakers") or {}
        resource.connection_tracking_policy = body.get("connectionTrackingPolicy") or {}
        resource.custom_response_headers = body.get("customResponseHeaders") or []
        resource.metadatas = body.get("metadatas") or {}
        resource.health_checks = health_checks
        resource.description = body.get("description") or ""
        resource.affinity_cookie_ttl_sec = body.get("affinityCookieTtlSec") or 0
        resource.locality_lb_policies = body.get("localityLbPolicies") or []
        resource.security_settings = body.get("securitySettings") or {}
        resource.strong_session_affinity_cookie = body.get(
            "strongSessionAffinityCookie"
        ) or {}
        resource.connection_draining = body.get("connectionDraining") or {}
        resource.iap = body.get("iap") or {}
        resource.backends = body.get("backends") or []
        resource.failover_policy = body.get("failoverPolicy") or {}
        resource.network = network
        resource.service_lb_policy = body.get("serviceLbPolicy") or ""
        resource.ha_policy = body.get("haPolicy") or {}
        resource.log_config = body.get("logConfig") or {}
        resource.port = body.get("port") or 0
        resource.used_by = body.get("usedBy") or []
        resource.timeout_sec = body.get("timeoutSec") or 0
        resource.locality_lb_policy = body.get("localityLbPolicy") or ""
        resource.consistent_hash = body.get("consistentHash") or {}
        resource.load_balancing_scheme = body.get("loadBalancingScheme") or ""
        resource.params = body.get("params") or {}
        resource.ip_address_selection_policy = body.get("ipAddressSelectionPolicy") or ""
        resource.network_pass_through_lb_traffic_policy = body.get(
            "networkPassThroughLbTrafficPolicy"
        ) or {}
        resource.creation_timestamp = body.get("creationTimestamp") or (
            resource.creation_timestamp or datetime.now(timezone.utc).isoformat()
        )
        resource.external_managed_migration_testing_percentage = body.get(
            "externalManagedMigrationTestingPercentage"
        )
        resource.custom_metrics = body.get("customMetrics") or []
        resource.compression_mode = body.get("compressionMode") or ""
        resource.subsetting = body.get("subsetting") or {}
        resource.max_stream_duration = body.get("maxStreamDuration") or {}

        if body_name != backend_service_name:
            self.resources.pop(backend_service_name, None)
            self.resources[body_name] = resource

        resource_link = (
            f"projects/{project}/regions/{region}/backendServices/{resource.name}"
        )
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified regional BackendService resource with the data
included in the request. For more information, see 
Understanding backend services This method
supports PATCH semantics and uses..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        backend_service_name = params.get("backendService")
        if not backend_service_name:
            return create_gcp_error(
                400,
                "Required field 'backendService' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("BackendService") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'BackendService' not found",
                "INVALID_ARGUMENT",
            )
        body_name = body.get("name")
        if body_name:
            backend_service_name = body_name

        resource = self.resources.get(backend_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )

        if "network" in body:
            network = body.get("network") or ""
            if network and not self.state.networks.get(network):
                return create_gcp_error(
                    404,
                    f"Network '{network}' not found",
                    "NOT_FOUND",
                )
            resource.network = network
        if "securityPolicy" in body:
            security_policy = body.get("securityPolicy") or ""
            if security_policy and not (
                self.state.security_policies.get(security_policy)
                or self.state.region_security_policies.get(security_policy)
            ):
                return create_gcp_error(
                    404,
                    f"Security policy '{security_policy}' not found",
                    "NOT_FOUND",
                )
            resource.security_policy = security_policy
        if "edgeSecurityPolicy" in body:
            edge_security_policy = body.get("edgeSecurityPolicy") or ""
            if edge_security_policy and not (
                self.state.security_policies.get(edge_security_policy)
                or self.state.region_security_policies.get(edge_security_policy)
            ):
                return create_gcp_error(
                    404,
                    f"Security policy '{edge_security_policy}' not found",
                    "NOT_FOUND",
                )
            resource.edge_security_policy = edge_security_policy
        if "healthChecks" in body:
            health_checks = body.get("healthChecks") or []
            for health_check in health_checks:
                if not (
                    self.state.health_checks.get(health_check)
                    or self.state.region_health_checks.get(health_check)
                    or self.state.http_health_checks.get(health_check)
                    or self.state.https_health_checks.get(health_check)
                    or self.state.region_health_check_services.get(health_check)
                ):
                    return create_gcp_error(
                        404,
                        f"Health check '{health_check}' not found",
                        "NOT_FOUND",
                    )
            resource.health_checks = health_checks

        if "enableCDN" in body:
            resource.enable_cdn = body.get("enableCDN") or False
        if "portName" in body:
            resource.port_name = body.get("portName") or ""
        if "outlierDetection" in body:
            resource.outlier_detection = body.get("outlierDetection") or {}
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "cdnPolicy" in body:
            resource.cdn_policy = body.get("cdnPolicy") or {}
        if "protocol" in body:
            resource.protocol = body.get("protocol") or ""
        if "region" in body:
            resource.region = body.get("region") or ""
        if "externalManagedMigrationState" in body:
            resource.external_managed_migration_state = body.get(
                "externalManagedMigrationState"
            ) or ""
        if "tlsSettings" in body:
            resource.tls_settings = body.get("tlsSettings") or {}
        if "name" in body:
            resource.name = backend_service_name
        if "customRequestHeaders" in body:
            resource.custom_request_headers = body.get("customRequestHeaders") or []
        if "serviceBindings" in body:
            resource.service_bindings = body.get("serviceBindings") or []
        if "sessionAffinity" in body:
            resource.session_affinity = body.get("sessionAffinity") or ""
        if "circuitBreakers" in body:
            resource.circuit_breakers = body.get("circuitBreakers") or {}
        if "connectionTrackingPolicy" in body:
            resource.connection_tracking_policy = body.get(
                "connectionTrackingPolicy"
            ) or {}
        if "customResponseHeaders" in body:
            resource.custom_response_headers = body.get("customResponseHeaders") or []
        if "metadatas" in body:
            resource.metadatas = body.get("metadatas") or {}
        if "description" in body:
            resource.description = body.get("description") or ""
        if "affinityCookieTtlSec" in body:
            resource.affinity_cookie_ttl_sec = body.get("affinityCookieTtlSec") or 0
        if "localityLbPolicies" in body:
            resource.locality_lb_policies = body.get("localityLbPolicies") or []
        if "securitySettings" in body:
            resource.security_settings = body.get("securitySettings") or {}
        if "strongSessionAffinityCookie" in body:
            resource.strong_session_affinity_cookie = body.get(
                "strongSessionAffinityCookie"
            ) or {}
        if "connectionDraining" in body:
            resource.connection_draining = body.get("connectionDraining") or {}
        if "iap" in body:
            resource.iap = body.get("iap") or {}
        if "backends" in body:
            resource.backends = body.get("backends") or []
        if "failoverPolicy" in body:
            resource.failover_policy = body.get("failoverPolicy") or {}
        if "serviceLbPolicy" in body:
            resource.service_lb_policy = body.get("serviceLbPolicy") or ""
        if "haPolicy" in body:
            resource.ha_policy = body.get("haPolicy") or {}
        if "logConfig" in body:
            resource.log_config = body.get("logConfig") or {}
        if "port" in body:
            resource.port = body.get("port") or 0
        if "usedBy" in body:
            resource.used_by = body.get("usedBy") or []
        if "timeoutSec" in body:
            resource.timeout_sec = body.get("timeoutSec") or 0
        if "localityLbPolicy" in body:
            resource.locality_lb_policy = body.get("localityLbPolicy") or ""
        if "consistentHash" in body:
            resource.consistent_hash = body.get("consistentHash") or {}
        if "loadBalancingScheme" in body:
            resource.load_balancing_scheme = body.get("loadBalancingScheme") or ""
        if "params" in body:
            resource.params = body.get("params") or {}
        if "ipAddressSelectionPolicy" in body:
            resource.ip_address_selection_policy = (
                body.get("ipAddressSelectionPolicy") or ""
            )
        if "networkPassThroughLbTrafficPolicy" in body:
            resource.network_pass_through_lb_traffic_policy = body.get(
                "networkPassThroughLbTrafficPolicy"
            ) or {}
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "externalManagedMigrationTestingPercentage" in body:
            resource.external_managed_migration_testing_percentage = body.get(
                "externalManagedMigrationTestingPercentage"
            )
        if "customMetrics" in body:
            resource.custom_metrics = body.get("customMetrics") or []
        if "compressionMode" in body:
            resource.compression_mode = body.get("compressionMode") or ""
        if "subsetting" in body:
            resource.subsetting = body.get("subsetting") or {}
        if "maxStreamDuration" in body:
            resource.max_stream_duration = body.get("maxStreamDuration") or {}

        if body_name and body_name != params.get("backendService"):
            existing = self.resources.get(params.get("backendService", ""))
            if existing is resource:
                self.resources.pop(params.get("backendService"), None)
                self.resources[backend_service_name] = resource

        resource_link = (
            f"projects/{project}/regions/{region}/backendServices/{resource.name}"
        )
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
        )

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("RegionSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'RegionSetPolicyRequest' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )

        policy = body.get("policy") or {}
        resource.iam_policy = policy
        resource_link = (
            f"projects/{project}/regions/{region}/backendServices/{resource.name}"
        )
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=resource_link,
            params=params,
        )

    def listUsable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of all usable backend services in the specified project in
the given region."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]
        return {
            "kind": "compute#regionbackendserviceList",
            "id": f"projects/{project}/regions/{region}/backendServices/listUsable",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def getHealth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the most recent health check results for this
regional BackendService."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        backend_service_name = params.get("backendService")
        if not backend_service_name:
            return create_gcp_error(
                400,
                "Required field 'backendService' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("ResourceGroupReference") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ResourceGroupReference' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(backend_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )

        return {
            "kind": "compute#backendServiceGroupHealth",
            "healthStatus": [],
            "group": body.get("group") or "",
        }

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        return getattr(resource, "iam_policy", {}) or {}

    def setSecurityPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the Google Cloud Armor security policy for the specified backend
service. For more information, seeGoogle
Cloud Armor Overview"""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        backend_service_name = params.get("backendService")
        if not backend_service_name:
            return create_gcp_error(
                400,
                "Required field 'backendService' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SecurityPolicyReference") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SecurityPolicyReference' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(backend_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )

        security_policy = body.get("securityPolicy") or ""
        if security_policy and not (
            self.state.security_policies.get(security_policy)
            or self.state.region_security_policies.get(security_policy)
        ):
            return create_gcp_error(
                404,
                f"Security policy '{security_policy}' not found",
                "NOT_FOUND",
            )
        resource.security_policy = security_policy

        resource_link = (
            f"projects/{project}/regions/{region}/backendServices/{resource.name}"
        )
        return make_operation(
            operation_type="setSecurityPolicy",
            resource_link=resource_link,
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TestPermissionsRequest' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )

        return {
            "permissions": body.get("permissions") or [],
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified regional BackendService resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
                "INVALID_ARGUMENT",
            )
        backend_service_name = params.get("backendService")
        if not backend_service_name:
            return create_gcp_error(
                400,
                "Required field 'backendService' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(backend_service_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{backend_service_name}' was not found",
                "NOT_FOUND",
            )

        self.resources.pop(backend_service_name, None)
        resource_link = (
            f"projects/{project}/regions/{region}/backendServices/{backend_service_name}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class region_backend_service_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'update': region_backend_service_RequestParser._parse_update,
            'get': region_backend_service_RequestParser._parse_get,
            'patch': region_backend_service_RequestParser._parse_patch,
            'setIamPolicy': region_backend_service_RequestParser._parse_setIamPolicy,
            'listUsable': region_backend_service_RequestParser._parse_listUsable,
            'list': region_backend_service_RequestParser._parse_list,
            'delete': region_backend_service_RequestParser._parse_delete,
            'getHealth': region_backend_service_RequestParser._parse_getHealth,
            'insert': region_backend_service_RequestParser._parse_insert,
            'getIamPolicy': region_backend_service_RequestParser._parse_getIamPolicy,
            'setSecurityPolicy': region_backend_service_RequestParser._parse_setSecurityPolicy,
            'testIamPermissions': region_backend_service_RequestParser._parse_testIamPermissions,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_update(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['BackendService'] = body.get('BackendService')
        return params

    @staticmethod
    def _parse_get(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        return params

    @staticmethod
    def _parse_patch(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['BackendService'] = body.get('BackendService')
        return params

    @staticmethod
    def _parse_setIamPolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Body params
        params['RegionSetPolicyRequest'] = body.get('RegionSetPolicyRequest')
        return params

    @staticmethod
    def _parse_listUsable(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_list(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_delete(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        return params

    @staticmethod
    def _parse_getHealth(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Body params
        params['ResourceGroupReference'] = body.get('ResourceGroupReference')
        return params

    @staticmethod
    def _parse_insert(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['BackendService'] = body.get('BackendService')
        return params

    @staticmethod
    def _parse_getIamPolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'optionsRequestedPolicyVersion' in query_params:
            params['optionsRequestedPolicyVersion'] = query_params['optionsRequestedPolicyVersion']
        return params

    @staticmethod
    def _parse_setSecurityPolicy(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['SecurityPolicyReference'] = body.get('SecurityPolicyReference')
        return params

    @staticmethod
    def _parse_testIamPermissions(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Body params
        params['TestPermissionsRequest'] = body.get('TestPermissionsRequest')
        return params


class region_backend_service_ResponseSerializer:
    @staticmethod
    def serialize(
        method_name: str,
        data: Dict[str, Any],
        request_id: str,
    ) -> str:
        if is_error_response(data):
            from ..utils import serialize_gcp_error
            return serialize_gcp_error(data)
        serializers = {
            'update': region_backend_service_ResponseSerializer._serialize_update,
            'get': region_backend_service_ResponseSerializer._serialize_get,
            'patch': region_backend_service_ResponseSerializer._serialize_patch,
            'setIamPolicy': region_backend_service_ResponseSerializer._serialize_setIamPolicy,
            'listUsable': region_backend_service_ResponseSerializer._serialize_listUsable,
            'list': region_backend_service_ResponseSerializer._serialize_list,
            'delete': region_backend_service_ResponseSerializer._serialize_delete,
            'getHealth': region_backend_service_ResponseSerializer._serialize_getHealth,
            'insert': region_backend_service_ResponseSerializer._serialize_insert,
            'getIamPolicy': region_backend_service_ResponseSerializer._serialize_getIamPolicy,
            'setSecurityPolicy': region_backend_service_ResponseSerializer._serialize_setSecurityPolicy,
            'testIamPermissions': region_backend_service_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listUsable(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getHealth(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setSecurityPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

