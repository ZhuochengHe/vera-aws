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
class Subnetwork:
    reserved_internal_range: str = ""
    private_ip_google_access: bool = False
    ipv6_access_type: str = ""
    enable_flow_logs: bool = False
    stack_type: str = ""
    private_ipv6_google_access: str = ""
    system_reserved_external_ipv6_ranges: List[Any] = field(default_factory=list)
    internal_ipv6_prefix: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    network: str = ""
    allow_subnet_cidr_routes_overlap: bool = False
    purpose: str = ""
    region: str = ""
    description: str = ""
    utilization_details: Dict[str, Any] = field(default_factory=dict)
    gateway_address: str = ""
    state: str = ""
    ipv6_gce_endpoint: str = ""
    ip_cidr_range: str = ""
    secondary_ip_ranges: List[Any] = field(default_factory=list)
    name: str = ""
    creation_timestamp: str = ""
    resolve_subnet_mask: str = ""
    ipv6_cidr_range: str = ""
    role: str = ""
    log_config: Dict[str, Any] = field(default_factory=dict)
    system_reserved_internal_ipv6_ranges: List[Any] = field(default_factory=list)
    external_ipv6_prefix: str = ""
    ip_collection: str = ""
    fingerprint: str = ""
    id: str = ""

    # Internal dependency tracking — not in API response
    network_name: str = ""  # parent Network name
    instance_names: List[str] = field(default_factory=list)  # tracks Instance children

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.reserved_internal_range is not None and self.reserved_internal_range != "":
            d["reservedInternalRange"] = self.reserved_internal_range
        d["privateIpGoogleAccess"] = self.private_ip_google_access
        if self.ipv6_access_type is not None and self.ipv6_access_type != "":
            d["ipv6AccessType"] = self.ipv6_access_type
        d["enableFlowLogs"] = self.enable_flow_logs
        if self.stack_type is not None and self.stack_type != "":
            d["stackType"] = self.stack_type
        if self.private_ipv6_google_access is not None and self.private_ipv6_google_access != "":
            d["privateIpv6GoogleAccess"] = self.private_ipv6_google_access
        d["systemReservedExternalIpv6Ranges"] = self.system_reserved_external_ipv6_ranges
        if self.internal_ipv6_prefix is not None and self.internal_ipv6_prefix != "":
            d["internalIpv6Prefix"] = self.internal_ipv6_prefix
        d["params"] = self.params
        if self.network is not None and self.network != "":
            d["network"] = self.network
        d["allowSubnetCidrRoutesOverlap"] = self.allow_subnet_cidr_routes_overlap
        if self.purpose is not None and self.purpose != "":
            d["purpose"] = self.purpose
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["utilizationDetails"] = self.utilization_details
        if self.gateway_address is not None and self.gateway_address != "":
            d["gatewayAddress"] = self.gateway_address
        if self.state is not None and self.state != "":
            d["state"] = self.state
        if self.ipv6_gce_endpoint is not None and self.ipv6_gce_endpoint != "":
            d["ipv6GceEndpoint"] = self.ipv6_gce_endpoint
        if self.ip_cidr_range is not None and self.ip_cidr_range != "":
            d["ipCidrRange"] = self.ip_cidr_range
        d["secondaryIpRanges"] = self.secondary_ip_ranges
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.resolve_subnet_mask is not None and self.resolve_subnet_mask != "":
            d["resolveSubnetMask"] = self.resolve_subnet_mask
        if self.ipv6_cidr_range is not None and self.ipv6_cidr_range != "":
            d["ipv6CidrRange"] = self.ipv6_cidr_range
        if self.role is not None and self.role != "":
            d["role"] = self.role
        d["logConfig"] = self.log_config
        d["systemReservedInternalIpv6Ranges"] = self.system_reserved_internal_ipv6_ranges
        if self.external_ipv6_prefix is not None and self.external_ipv6_prefix != "":
            d["externalIpv6Prefix"] = self.external_ipv6_prefix
        if self.ip_collection is not None and self.ip_collection != "":
            d["ipCollection"] = self.ip_collection
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#subnetwork"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Subnetwork_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.subnetworks  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "subnetwork") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(
        self,
        params: Dict[str, Any],
        name: str,
        region: Optional[str] = None,
    ) -> Any:
        resource = self.resources.get(name)
        if not resource:
            project = params.get("project", "")
            region_name = region or params.get("region", "")
            resource_path = f"projects/{project}/regions/{region_name}/subnetworks/{name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        region_name = region or params.get("region")
        if region_name and resource.region and resource.region != region_name:
            resource_path = f"projects/{params.get('project', '')}/regions/{region_name}/subnetworks/{name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return resource

    def _filter_resources(self, params: Dict[str, Any]) -> List[Subnetwork]:
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [
                    resource
                    for resource in resources
                    if resource.name == match.group(1)
                ]
        region = params.get("region")
        if region:
            resources = [resource for resource in resources if resource.region == region]
        zone = params.get("zone")
        if zone and hasattr(resources[0] if resources else object(), "zone"):
            resources = [resource for resource in resources if resource.zone == zone]
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a subnetwork in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("Subnetwork") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Subnetwork' not specified", "INVALID_ARGUMENT")
        name = body.get("name") or params.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"Subnetwork {name!r} already exists", "ALREADY_EXISTS")

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        network_ref = body.get("network") or ""
        network_name = normalize_name(network_ref)
        if not network_name:
            return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
        network = self.state.networks.get(network_name)
        if not network:
            return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")

        resource = Subnetwork(
            reserved_internal_range=body.get("reservedInternalRange", ""),
            private_ip_google_access=body.get("privateIpGoogleAccess", False),
            ipv6_access_type=body.get("ipv6AccessType", ""),
            enable_flow_logs=body.get("enableFlowLogs", False),
            stack_type=body.get("stackType", ""),
            private_ipv6_google_access=body.get("privateIpv6GoogleAccess", ""),
            system_reserved_external_ipv6_ranges=body.get(
                "systemReservedExternalIpv6Ranges"
            )
            or [],
            internal_ipv6_prefix=body.get("internalIpv6Prefix", ""),
            params=body.get("params") or {},
            network=network_ref,
            allow_subnet_cidr_routes_overlap=body.get(
                "allowSubnetCidrRoutesOverlap", False
            ),
            purpose=body.get("purpose", ""),
            region=region,
            description=body.get("description", ""),
            utilization_details=body.get("utilizationDetails") or {},
            gateway_address=body.get("gatewayAddress", ""),
            state=body.get("state", ""),
            ipv6_gce_endpoint=body.get("ipv6GceEndpoint", ""),
            ip_cidr_range=body.get("ipCidrRange", ""),
            secondary_ip_ranges=body.get("secondaryIpRanges") or [],
            name=name,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            resolve_subnet_mask=body.get("resolveSubnetMask", ""),
            ipv6_cidr_range=body.get("ipv6CidrRange", ""),
            role=body.get("role", ""),
            log_config=body.get("logConfig") or {},
            system_reserved_internal_ipv6_ranges=body.get(
                "systemReservedInternalIpv6Ranges"
            )
            or [],
            external_ipv6_prefix=body.get("externalIpv6Prefix", ""),
            ip_collection=body.get("ipCollection", ""),
            fingerprint=body.get("fingerprint", ""),
            id=self._generate_id(),
            network_name=network_name,
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        if resource.name not in network.subnetwork_names:
            network.subnetwork_names.append(resource.name)

        resource_link = f"projects/{project}/regions/{region}/subnetworks/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
            region=region,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified subnetwork."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        subnetwork_name = params.get("subnetwork")
        if not subnetwork_name:
            return create_gcp_error(400, "Required field 'subnetwork' not specified", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params, subnetwork_name, region)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of subnetworks.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")

        resources = self._filter_resources(params)
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        items: Dict[str, Any]
        if resources:
            items = {scope_key: {"Subnetworks": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#subnetworkAggregatedList",
            "id": f"projects/{project}/aggregated/Subnetworks",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of subnetworks available to the specified
project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")

        resources = self._filter_resources(params)
        return {
            "kind": "compute#subnetworkList",
            "id": f"projects/{project}/regions/{region}/subnetworks",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified subnetwork with the data included in the request.
Only certain fields can be updated with a patch request
as indicated in the field descriptions.
You must specify the current ..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        subnetwork_name = params.get("subnetwork")
        if not subnetwork_name:
            return create_gcp_error(400, "Required field 'subnetwork' not specified", "INVALID_ARGUMENT")
        body = params.get("Subnetwork") or {}
        if not body:
            return create_gcp_error(400, "Required field 'Subnetwork' not specified", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params, subnetwork_name, region)
        if is_error_response(resource):
            return resource
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "Subnetwork name cannot be changed", "INVALID_ARGUMENT")

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        if "network" in body:
            network_ref = body.get("network") or ""
            network_name = normalize_name(network_ref)
            if not network_name:
                return create_gcp_error(400, "Required field 'network' not specified", "INVALID_ARGUMENT")
            new_network = self.state.networks.get(network_name)
            if not new_network:
                return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
            old_network = None
            if resource.network_name:
                old_network = self.state.networks.get(resource.network_name)
            if old_network and resource.name in old_network.subnetwork_names:
                old_network.subnetwork_names.remove(resource.name)
            if resource.name not in new_network.subnetwork_names:
                new_network.subnetwork_names.append(resource.name)
            resource.network = network_ref
            resource.network_name = network_name
        if "reservedInternalRange" in body:
            resource.reserved_internal_range = body.get("reservedInternalRange") or ""
        if "privateIpGoogleAccess" in body:
            resource.private_ip_google_access = bool(body.get("privateIpGoogleAccess"))
        if "ipv6AccessType" in body:
            resource.ipv6_access_type = body.get("ipv6AccessType") or ""
        if "enableFlowLogs" in body:
            resource.enable_flow_logs = bool(body.get("enableFlowLogs"))
        if "stackType" in body:
            resource.stack_type = body.get("stackType") or ""
        if "privateIpv6GoogleAccess" in body:
            resource.private_ipv6_google_access = body.get("privateIpv6GoogleAccess") or ""
        if "systemReservedExternalIpv6Ranges" in body:
            resource.system_reserved_external_ipv6_ranges = body.get(
                "systemReservedExternalIpv6Ranges"
            ) or []
        if "internalIpv6Prefix" in body:
            resource.internal_ipv6_prefix = body.get("internalIpv6Prefix") or ""
        if "params" in body:
            resource.params = body.get("params") or {}
        if "allowSubnetCidrRoutesOverlap" in body:
            resource.allow_subnet_cidr_routes_overlap = bool(
                body.get("allowSubnetCidrRoutesOverlap")
            )
        if "purpose" in body:
            resource.purpose = body.get("purpose") or ""
        if "region" in body:
            resource.region = body.get("region") or ""
        if "description" in body:
            resource.description = body.get("description") or ""
        if "utilizationDetails" in body:
            resource.utilization_details = body.get("utilizationDetails") or {}
        if "gatewayAddress" in body:
            resource.gateway_address = body.get("gatewayAddress") or ""
        if "state" in body:
            resource.state = body.get("state") or ""
        if "ipv6GceEndpoint" in body:
            resource.ipv6_gce_endpoint = body.get("ipv6GceEndpoint") or ""
        if "ipCidrRange" in body:
            resource.ip_cidr_range = body.get("ipCidrRange") or ""
        if "secondaryIpRanges" in body:
            resource.secondary_ip_ranges = body.get("secondaryIpRanges") or []
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "resolveSubnetMask" in body:
            resource.resolve_subnet_mask = body.get("resolveSubnetMask") or ""
        if "ipv6CidrRange" in body:
            resource.ipv6_cidr_range = body.get("ipv6CidrRange") or ""
        if "role" in body:
            resource.role = body.get("role") or ""
        if "logConfig" in body:
            resource.log_config = body.get("logConfig") or {}
        if "systemReservedInternalIpv6Ranges" in body:
            resource.system_reserved_internal_ipv6_ranges = body.get(
                "systemReservedInternalIpv6Ranges"
            ) or []
        if "externalIpv6Prefix" in body:
            resource.external_ipv6_prefix = body.get("externalIpv6Prefix") or ""
        if "ipCollection" in body:
            resource.ip_collection = body.get("ipCollection") or ""
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "iamPolicy" in body:
            resource.iam_policy = body.get("iamPolicy") or {}

        resource_link = f"projects/{project}/regions/{region}/subnetworks/{resource.name}"
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
            region=region,
        )

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("RegionSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'RegionSetPolicyRequest' not specified", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params, name, region)
        if is_error_response(resource):
            return resource
        resource.iam_policy = body.get("policy") or {}
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=f"projects/{project}/regions/{region}/subnetworks/{resource.name}",
            params=params,
        )

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params, name, region)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

    def setPrivateIpGoogleAccess(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set whether VMs in this subnet can access Google services without assigning
external IP addresses through Private Google Access."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        subnetwork_name = params.get("subnetwork")
        if not subnetwork_name:
            return create_gcp_error(400, "Required field 'subnetwork' not specified", "INVALID_ARGUMENT")
        body = params.get("SubnetworksSetPrivateIpGoogleAccessRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SubnetworksSetPrivateIpGoogleAccessRequest' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(params, subnetwork_name, region)
        if is_error_response(resource):
            return resource
        access = body.get("privateIpGoogleAccess")
        if access is None:
            return create_gcp_error(400, "Required field 'privateIpGoogleAccess' not specified", "INVALID_ARGUMENT")
        resource.private_ip_google_access = bool(access)
        resource_link = f"projects/{project}/regions/{region}/subnetworks/{resource.name}"
        return make_operation(
            operation_type="setPrivateIpGoogleAccess",
            resource_link=resource_link,
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params, name, region)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def expandIpCidrRange(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Expands the IP CIDR range of the subnetwork to a specified value."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        subnetwork_name = params.get("subnetwork")
        if not subnetwork_name:
            return create_gcp_error(400, "Required field 'subnetwork' not specified", "INVALID_ARGUMENT")
        body = params.get("SubnetworksExpandIpCidrRangeRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SubnetworksExpandIpCidrRangeRequest' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(params, subnetwork_name, region)
        if is_error_response(resource):
            return resource
        new_range = body.get("ipCidrRange") or ""
        if not new_range:
            return create_gcp_error(400, "Required field 'ipCidrRange' not specified", "INVALID_ARGUMENT")
        resource.ip_cidr_range = new_range
        resource_link = f"projects/{project}/regions/{region}/subnetworks/{resource.name}"
        return make_operation(
            operation_type="expandIpCidrRange",
            resource_link=resource_link,
            params=params,
        )

    def listUsable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of all usable subnetworks in the project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")

        resources = self._filter_resources(params)
        return {
            "kind": "compute#subnetworkList",
            "id": f"projects/{project}/aggregated/subnetworks/listUsable",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified subnetwork."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        subnetwork_name = params.get("subnetwork")
        if not subnetwork_name:
            return create_gcp_error(400, "Required field 'subnetwork' not specified", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params, subnetwork_name, region)
        if is_error_response(resource):
            return resource
        if resource.instance_names:
            return create_gcp_error(400, "Subnetwork is currently in use", "FAILED_PRECONDITION")

        network = None
        if resource.network_name:
            network = self.state.networks.get(resource.network_name)
        if network and resource.name in network.subnetwork_names:
            network.subnetwork_names.remove(resource.name)
        self.resources.pop(resource.name, None)

        resource_link = f"projects/{project}/regions/{region}/subnetworks/{subnetwork_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class subnetwork_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'insert': subnetwork_RequestParser._parse_insert,
            'get': subnetwork_RequestParser._parse_get,
            'getIamPolicy': subnetwork_RequestParser._parse_getIamPolicy,
            'setPrivateIpGoogleAccess': subnetwork_RequestParser._parse_setPrivateIpGoogleAccess,
            'delete': subnetwork_RequestParser._parse_delete,
            'testIamPermissions': subnetwork_RequestParser._parse_testIamPermissions,
            'aggregatedList': subnetwork_RequestParser._parse_aggregatedList,
            'patch': subnetwork_RequestParser._parse_patch,
            'expandIpCidrRange': subnetwork_RequestParser._parse_expandIpCidrRange,
            'listUsable': subnetwork_RequestParser._parse_listUsable,
            'setIamPolicy': subnetwork_RequestParser._parse_setIamPolicy,
            'list': subnetwork_RequestParser._parse_list,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['Subnetwork'] = body.get('Subnetwork')
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
        if 'views' in query_params:
            params['views'] = query_params['views']
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
    def _parse_setPrivateIpGoogleAccess(
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
        params['SubnetworksSetPrivateIpGoogleAccessRequest'] = body.get('SubnetworksSetPrivateIpGoogleAccessRequest')
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

    @staticmethod
    def _parse_aggregatedList(
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
        if 'includeAllScopes' in query_params:
            params['includeAllScopes'] = query_params['includeAllScopes']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        if 'serviceProjectNumber' in query_params:
            params['serviceProjectNumber'] = query_params['serviceProjectNumber']
        if 'views' in query_params:
            params['views'] = query_params['views']
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
        if 'drainTimeoutSeconds' in query_params:
            params['drainTimeoutSeconds'] = query_params['drainTimeoutSeconds']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Subnetwork'] = body.get('Subnetwork')
        return params

    @staticmethod
    def _parse_expandIpCidrRange(
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
        params['SubnetworksExpandIpCidrRangeRequest'] = body.get('SubnetworksExpandIpCidrRangeRequest')
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
        if 'serviceProject' in query_params:
            params['serviceProject'] = query_params['serviceProject']
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
        if 'views' in query_params:
            params['views'] = query_params['views']
        return params


class subnetwork_ResponseSerializer:
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
            'insert': subnetwork_ResponseSerializer._serialize_insert,
            'get': subnetwork_ResponseSerializer._serialize_get,
            'getIamPolicy': subnetwork_ResponseSerializer._serialize_getIamPolicy,
            'setPrivateIpGoogleAccess': subnetwork_ResponseSerializer._serialize_setPrivateIpGoogleAccess,
            'delete': subnetwork_ResponseSerializer._serialize_delete,
            'testIamPermissions': subnetwork_ResponseSerializer._serialize_testIamPermissions,
            'aggregatedList': subnetwork_ResponseSerializer._serialize_aggregatedList,
            'patch': subnetwork_ResponseSerializer._serialize_patch,
            'expandIpCidrRange': subnetwork_ResponseSerializer._serialize_expandIpCidrRange,
            'listUsable': subnetwork_ResponseSerializer._serialize_listUsable,
            'setIamPolicy': subnetwork_ResponseSerializer._serialize_setIamPolicy,
            'list': subnetwork_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setPrivateIpGoogleAccess(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_expandIpCidrRange(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listUsable(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

