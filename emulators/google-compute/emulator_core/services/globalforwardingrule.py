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
class GlobalForwardingRule:
    fingerprint: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    source_ip_ranges: List[Any] = field(default_factory=list)
    external_managed_backend_bucket_migration_state: str = ""
    allow_global_access: bool = False
    ip_address: str = ""
    load_balancing_scheme: str = ""
    allow_psc_global_access: bool = False
    ports: List[Any] = field(default_factory=list)
    service_label: str = ""
    base_forwarding_rule: str = ""
    ip_collection: str = ""
    description: str = ""
    external_managed_backend_bucket_migration_testing_percentage: Any = None
    no_automate_dns_zone: bool = False
    metadata_filters: List[Any] = field(default_factory=list)
    name: str = ""
    is_mirroring_collector: bool = False
    network: str = ""
    ip_version: str = ""
    subnetwork: str = ""
    psc_connection_status: str = ""
    backend_service: str = ""
    target: str = ""
    port_range: str = ""
    label_fingerprint: str = ""
    service_name: str = ""
    region: str = ""
    service_directory_registrations: List[Any] = field(default_factory=list)
    self_link_with_id: str = ""
    ip_protocol: str = ""
    creation_timestamp: str = ""
    all_ports: bool = False
    psc_connection_id: str = ""
    network_tier: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        d["labels"] = self.labels
        d["sourceIpRanges"] = self.source_ip_ranges
        if self.external_managed_backend_bucket_migration_state is not None and self.external_managed_backend_bucket_migration_state != "":
            d["externalManagedBackendBucketMigrationState"] = self.external_managed_backend_bucket_migration_state
        d["allowGlobalAccess"] = self.allow_global_access
        if self.ip_address is not None and self.ip_address != "":
            d["IPAddress"] = self.ip_address
        if self.load_balancing_scheme is not None and self.load_balancing_scheme != "":
            d["loadBalancingScheme"] = self.load_balancing_scheme
        d["allowPscGlobalAccess"] = self.allow_psc_global_access
        d["ports"] = self.ports
        if self.service_label is not None and self.service_label != "":
            d["serviceLabel"] = self.service_label
        if self.base_forwarding_rule is not None and self.base_forwarding_rule != "":
            d["baseForwardingRule"] = self.base_forwarding_rule
        if self.ip_collection is not None and self.ip_collection != "":
            d["ipCollection"] = self.ip_collection
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.external_managed_backend_bucket_migration_testing_percentage is not None and self.external_managed_backend_bucket_migration_testing_percentage != None:
            d["externalManagedBackendBucketMigrationTestingPercentage"] = self.external_managed_backend_bucket_migration_testing_percentage
        d["noAutomateDnsZone"] = self.no_automate_dns_zone
        d["metadataFilters"] = self.metadata_filters
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["isMirroringCollector"] = self.is_mirroring_collector
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.ip_version is not None and self.ip_version != "":
            d["ipVersion"] = self.ip_version
        if self.subnetwork is not None and self.subnetwork != "":
            d["subnetwork"] = self.subnetwork
        if self.psc_connection_status is not None and self.psc_connection_status != "":
            d["pscConnectionStatus"] = self.psc_connection_status
        if self.backend_service is not None and self.backend_service != "":
            d["backendService"] = self.backend_service
        if self.target is not None and self.target != "":
            d["target"] = self.target
        if self.port_range is not None and self.port_range != "":
            d["portRange"] = self.port_range
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.service_name is not None and self.service_name != "":
            d["serviceName"] = self.service_name
        if self.region is not None and self.region != "":
            d["region"] = self.region
        d["serviceDirectoryRegistrations"] = self.service_directory_registrations
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.ip_protocol is not None and self.ip_protocol != "":
            d["IPProtocol"] = self.ip_protocol
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["allPorts"] = self.all_ports
        if self.psc_connection_id is not None and self.psc_connection_id != "":
            d["pscConnectionId"] = self.psc_connection_id
        if self.network_tier is not None and self.network_tier != "":
            d["networkTier"] = self.network_tier
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#globalforwardingrule"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class GlobalForwardingRule_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.global_forwarding_rules  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "global-forwarding-rule") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a GlobalForwardingRule resource in the specified project using
the data included in the request."""
        project = params.get("project")
        body = params.get("ForwardingRule")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'ForwardingRule' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"GlobalForwardingRule '{name}' already exists", "ALREADY_EXISTS")
        network = body.get("network", "")
        network_name = network.split("/")[-1] if network else ""
        if network_name and not self.state.networks.get(network_name):
            return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
        subnetwork = body.get("subnetwork", "")
        subnetwork_name = subnetwork.split("/")[-1] if subnetwork else ""
        if subnetwork:
            if not self.state.subnetworks.get(subnetwork) and not self.state.subnetworks.get(subnetwork_name):
                name_hint = subnetwork_name or subnetwork
                return create_gcp_error(404, f"Subnetwork '{name_hint}' not found", "NOT_FOUND")
        backend_service = body.get("backendService", "")
        if backend_service:
            backend_service_name = backend_service.split("/")[-1]
            if not self.state.backend_services.get(backend_service_name) and not self.state.backend_services.get(backend_service):
                return create_gcp_error(404, f"BackendService '{backend_service_name}' not found", "NOT_FOUND")
        target = body.get("target", "")
        if target:
            target_name = target.split("/")[-1]
            target_stores = [
                self.state.target_pools,
                self.state.target_instances,
                self.state.target_http_proxies,
                self.state.target_https_proxies,
                self.state.target_tcp_proxies,
                self.state.target_ssl_proxies,
                self.state.target_grpc_proxies,
                self.state.region_target_http_proxies,
                self.state.region_target_https_proxies,
                self.state.region_target_tcp_proxies,
            ]
            target_found = any(store.get(target_name) or store.get(target) for store in target_stores)
            if not target_found:
                return create_gcp_error(404, f"Target '{target_name}' not found", "NOT_FOUND")
        labels = body.get("labels", {}) or {}
        label_fingerprint = str(uuid.uuid4())[:8] if labels is not None else ""
        creation_timestamp = datetime.now(timezone.utc).isoformat()
        ip_address = body.get("IPAddress") or body.get("ipAddress", "")
        resource = GlobalForwardingRule(
            fingerprint=body.get("fingerprint", ""),
            labels=labels,
            source_ip_ranges=body.get("sourceIpRanges", []) or [],
            external_managed_backend_bucket_migration_state=body.get(
                "externalManagedBackendBucketMigrationState", ""
            ),
            allow_global_access=body.get("allowGlobalAccess", False),
            ip_address=ip_address or "",
            load_balancing_scheme=body.get("loadBalancingScheme", ""),
            allow_psc_global_access=body.get("allowPscGlobalAccess", False),
            ports=body.get("ports", []) or [],
            service_label=body.get("serviceLabel", ""),
            base_forwarding_rule=body.get("baseForwardingRule", ""),
            ip_collection=body.get("ipCollection", ""),
            description=body.get("description", ""),
            external_managed_backend_bucket_migration_testing_percentage=body.get(
                "externalManagedBackendBucketMigrationTestingPercentage"
            ),
            no_automate_dns_zone=body.get("noAutomateDnsZone", False),
            metadata_filters=body.get("metadataFilters", []) or [],
            name=name,
            is_mirroring_collector=body.get("isMirroringCollector", False),
            network=network,
            ip_version=body.get("ipVersion", ""),
            subnetwork=subnetwork,
            psc_connection_status=body.get("pscConnectionStatus", ""),
            backend_service=backend_service,
            target=target,
            port_range=body.get("portRange", ""),
            label_fingerprint=label_fingerprint,
            service_name=body.get("serviceName", ""),
            region=body.get("region", ""),
            service_directory_registrations=body.get("serviceDirectoryRegistrations", []) or [],
            self_link_with_id=body.get("selfLinkWithId", ""),
            ip_protocol=body.get("IPProtocol") or body.get("ipProtocol", ""),
            creation_timestamp=creation_timestamp,
            all_ports=body.get("allPorts", False),
            psc_connection_id=body.get("pscConnectionId", ""),
            network_tier=body.get("networkTier", ""),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/forwardingRules/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified GlobalForwardingRule resource. Gets a list of
available forwarding rules by making a list() request."""
        project = params.get("project")
        forwarding_rule = params.get("forwardingRule")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not forwarding_rule:
            return create_gcp_error(400, "Required field 'forwardingRule' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(forwarding_rule)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of GlobalForwardingRule resources available to the
specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        return {
            "kind": "compute#globalforwardingruleList",
            "id": f"projects/{project}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on the specified resource. To learn more about labels,
read the 
Labeling resources documentation."""
        project = params.get("project")
        resource_name = params.get("resource")
        body = params.get("GlobalSetLabelsRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'GlobalSetLabelsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        resource.labels = body.get("labels", {}) or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        return make_operation(
            operation_type="setLabels",
            resource_link=f"projects/{project}/global/forwardingRules/{resource.name}",
            params=params,
        )

    def setTarget(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes target URL for the GlobalForwardingRule resource. The new target
should be of the same type as the old target."""
        project = params.get("project")
        forwarding_rule = params.get("forwardingRule")
        body = params.get("TargetReference")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not forwarding_rule:
            return create_gcp_error(400, "Required field 'forwardingRule' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'TargetReference' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(forwarding_rule)
        if is_error_response(resource):
            return resource
        target = body.get("target") or body.get("Target") or ""
        if not target:
            return create_gcp_error(400, "Required field 'target' not specified", "INVALID_ARGUMENT")
        target_name = target.split("/")[-1]
        target_stores = [
            self.state.target_pools,
            self.state.target_instances,
            self.state.target_http_proxies,
            self.state.target_https_proxies,
            self.state.target_tcp_proxies,
            self.state.target_ssl_proxies,
            self.state.target_grpc_proxies,
            self.state.region_target_http_proxies,
            self.state.region_target_https_proxies,
            self.state.region_target_tcp_proxies,
        ]
        target_found = any(store.get(target_name) or store.get(target) for store in target_stores)
        if not target_found:
            return create_gcp_error(404, f"Target '{target_name}' not found", "NOT_FOUND")
        resource.target = target
        return make_operation(
            operation_type="setTarget",
            resource_link=f"projects/{project}/global/forwardingRules/{resource.name}",
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified forwarding rule with the data included in the
request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules. Currently, you can only
pa..."""
        project = params.get("project")
        forwarding_rule = params.get("forwardingRule")
        body = params.get("ForwardingRule")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not forwarding_rule:
            return create_gcp_error(400, "Required field 'forwardingRule' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'ForwardingRule' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(forwarding_rule)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "Resource name cannot be changed", "INVALID_ARGUMENT")
        if "labels" in body:
            resource.labels = body.get("labels") or {}
            resource.label_fingerprint = str(uuid.uuid4())[:8]
        if "allowGlobalAccess" in body:
            resource.allow_global_access = body.get("allowGlobalAccess", False)
        if "allowPscGlobalAccess" in body:
            resource.allow_psc_global_access = body.get("allowPscGlobalAccess", False)
        if "description" in body:
            resource.description = body.get("description", "")
        if "ipVersion" in body:
            resource.ip_version = body.get("ipVersion", "")
        if "loadBalancingScheme" in body:
            resource.load_balancing_scheme = body.get("loadBalancingScheme", "")
        if "metadataFilters" in body:
            resource.metadata_filters = body.get("metadataFilters", []) or []
        if "noAutomateDnsZone" in body:
            resource.no_automate_dns_zone = body.get("noAutomateDnsZone", False)
        if "ports" in body:
            resource.ports = body.get("ports", []) or []
        if "serviceLabel" in body:
            resource.service_label = body.get("serviceLabel", "")
        if "serviceName" in body:
            resource.service_name = body.get("serviceName", "")
        if "sourceIpRanges" in body:
            resource.source_ip_ranges = body.get("sourceIpRanges", []) or []
        if "backendService" in body:
            backend_service = body.get("backendService", "")
            if backend_service:
                backend_service_name = backend_service.split("/")[-1]
                if not self.state.backend_services.get(backend_service_name) and not self.state.backend_services.get(backend_service):
                    return create_gcp_error(404, f"BackendService '{backend_service_name}' not found", "NOT_FOUND")
            resource.backend_service = backend_service
        if "target" in body:
            target = body.get("target", "")
            if target:
                target_name = target.split("/")[-1]
                target_stores = [
                    self.state.target_pools,
                    self.state.target_instances,
                    self.state.target_http_proxies,
                    self.state.target_https_proxies,
                    self.state.target_tcp_proxies,
                    self.state.target_ssl_proxies,
                    self.state.target_grpc_proxies,
                    self.state.region_target_http_proxies,
                    self.state.region_target_https_proxies,
                    self.state.region_target_tcp_proxies,
                ]
                target_found = any(store.get(target_name) or store.get(target) for store in target_stores)
                if not target_found:
                    return create_gcp_error(404, f"Target '{target_name}' not found", "NOT_FOUND")
            resource.target = target
        if "network" in body:
            network = body.get("network", "")
            network_name = network.split("/")[-1] if network else ""
            if network_name and not self.state.networks.get(network_name):
                return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
            resource.network = network
        if "subnetwork" in body:
            subnetwork = body.get("subnetwork", "")
            subnetwork_name = subnetwork.split("/")[-1] if subnetwork else ""
            if subnetwork:
                if not self.state.subnetworks.get(subnetwork) and not self.state.subnetworks.get(subnetwork_name):
                    name_hint = subnetwork_name or subnetwork
                    return create_gcp_error(404, f"Subnetwork '{name_hint}' not found", "NOT_FOUND")
            resource.subnetwork = subnetwork
        if "IPProtocol" in body or "ipProtocol" in body:
            resource.ip_protocol = body.get("IPProtocol") or body.get("ipProtocol", "")
        if "IPAddress" in body or "ipAddress" in body:
            resource.ip_address = body.get("IPAddress") or body.get("ipAddress", "")
        if "portRange" in body:
            resource.port_range = body.get("portRange", "")
        if "allPorts" in body:
            resource.all_ports = body.get("allPorts", False)
        if "networkTier" in body:
            resource.network_tier = body.get("networkTier", "")
        if "serviceDirectoryRegistrations" in body:
            resource.service_directory_registrations = body.get("serviceDirectoryRegistrations", []) or []
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/forwardingRules/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified GlobalForwardingRule resource."""
        project = params.get("project")
        forwarding_rule = params.get("forwardingRule")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not forwarding_rule:
            return create_gcp_error(400, "Required field 'forwardingRule' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(forwarding_rule)
        if is_error_response(resource):
            return resource
        del self.resources[forwarding_rule]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/forwardingRules/{forwarding_rule}",
            params=params,
        )


class global_forwarding_rule_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setLabels': global_forwarding_rule_RequestParser._parse_setLabels,
            'get': global_forwarding_rule_RequestParser._parse_get,
            'delete': global_forwarding_rule_RequestParser._parse_delete,
            'list': global_forwarding_rule_RequestParser._parse_list,
            'insert': global_forwarding_rule_RequestParser._parse_insert,
            'setTarget': global_forwarding_rule_RequestParser._parse_setTarget,
            'patch': global_forwarding_rule_RequestParser._parse_patch,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_setLabels(
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
        params['GlobalSetLabelsRequest'] = body.get('GlobalSetLabelsRequest')
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
        params['ForwardingRule'] = body.get('ForwardingRule')
        return params

    @staticmethod
    def _parse_setTarget(
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
        params['TargetReference'] = body.get('TargetReference')
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
        params['ForwardingRule'] = body.get('ForwardingRule')
        return params


class global_forwarding_rule_ResponseSerializer:
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
            'setLabels': global_forwarding_rule_ResponseSerializer._serialize_setLabels,
            'get': global_forwarding_rule_ResponseSerializer._serialize_get,
            'delete': global_forwarding_rule_ResponseSerializer._serialize_delete,
            'list': global_forwarding_rule_ResponseSerializer._serialize_list,
            'insert': global_forwarding_rule_ResponseSerializer._serialize_insert,
            'setTarget': global_forwarding_rule_ResponseSerializer._serialize_setTarget,
            'patch': global_forwarding_rule_ResponseSerializer._serialize_patch,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setTarget(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

