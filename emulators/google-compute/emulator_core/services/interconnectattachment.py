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
class InterconnectAttachment:
    customer_router_ipv6_interface_id: str = ""
    edge_availability_domain: str = ""
    creation_timestamp: str = ""
    customer_router_ipv6_address: str = ""
    partner_metadata: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    ipsec_internal_addresses: List[Any] = field(default_factory=list)
    label_fingerprint: str = ""
    l2_forwarding: Dict[str, Any] = field(default_factory=dict)
    type: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    customer_router_ip_address: str = ""
    vlan_tag8021q: int = 0
    stack_type: str = ""
    private_interconnect_info: Dict[str, Any] = field(default_factory=dict)
    satisfies_pzs: bool = False
    admin_enabled: bool = False
    configuration_constraints: Dict[str, Any] = field(default_factory=dict)
    operational_status: str = ""
    candidate_cloud_router_ip_address: str = ""
    subnet_length: int = 0
    attachment_group: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    candidate_customer_router_ip_address: str = ""
    candidate_ipv6_subnets: List[Any] = field(default_factory=list)
    interconnect: str = ""
    cloud_router_ipv6_address: str = ""
    pairing_key: str = ""
    dataplane_version: int = 0
    cloud_router_ipv6_interface_id: str = ""
    state: str = ""
    router: str = ""
    remote_service: str = ""
    region: str = ""
    candidate_customer_router_ipv6_address: str = ""
    bandwidth: str = ""
    name: str = ""
    candidate_subnets: List[Any] = field(default_factory=list)
    candidate_cloud_router_ipv6_address: str = ""
    partner_asn: str = ""
    cloud_router_ip_address: str = ""
    google_reference_id: str = ""
    mtu: int = 0
    encryption: str = ""
    id: str = ""

    # Internal dependency tracking — not in API response
    interconnect_name: str = ""  # parent Interconnect name
    router_name: str = ""  # associated Router name


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.customer_router_ipv6_interface_id is not None and self.customer_router_ipv6_interface_id != "":
            d["customerRouterIpv6InterfaceId"] = self.customer_router_ipv6_interface_id
        if self.edge_availability_domain is not None and self.edge_availability_domain != "":
            d["edgeAvailabilityDomain"] = self.edge_availability_domain
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.customer_router_ipv6_address is not None and self.customer_router_ipv6_address != "":
            d["customerRouterIpv6Address"] = self.customer_router_ipv6_address
        d["partnerMetadata"] = self.partner_metadata
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["ipsecInternalAddresses"] = self.ipsec_internal_addresses
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        d["l2Forwarding"] = self.l2_forwarding
        if self.type is not None and self.type != "":
            d["type"] = self.type
        d["params"] = self.params
        if self.customer_router_ip_address is not None and self.customer_router_ip_address != "":
            d["customerRouterIpAddress"] = self.customer_router_ip_address
        if self.vlan_tag8021q is not None and self.vlan_tag8021q != 0:
            d["vlanTag8021q"] = self.vlan_tag8021q
        if self.stack_type is not None and self.stack_type != "":
            d["stackType"] = self.stack_type
        d["privateInterconnectInfo"] = self.private_interconnect_info
        d["satisfiesPzs"] = self.satisfies_pzs
        d["adminEnabled"] = self.admin_enabled
        d["configurationConstraints"] = self.configuration_constraints
        if self.operational_status is not None and self.operational_status != "":
            d["operationalStatus"] = self.operational_status
        if self.candidate_cloud_router_ip_address is not None and self.candidate_cloud_router_ip_address != "":
            d["candidateCloudRouterIpAddress"] = self.candidate_cloud_router_ip_address
        if self.subnet_length is not None and self.subnet_length != 0:
            d["subnetLength"] = self.subnet_length
        if self.attachment_group is not None and self.attachment_group != "":
            d["attachmentGroup"] = self.attachment_group
        d["labels"] = self.labels
        if self.candidate_customer_router_ip_address is not None and self.candidate_customer_router_ip_address != "":
            d["candidateCustomerRouterIpAddress"] = self.candidate_customer_router_ip_address
        d["candidateIpv6Subnets"] = self.candidate_ipv6_subnets
        if self.interconnect is not None and self.interconnect != "":
            d["interconnect"] = self.interconnect
        if self.cloud_router_ipv6_address is not None and self.cloud_router_ipv6_address != "":
            d["cloudRouterIpv6Address"] = self.cloud_router_ipv6_address
        if self.pairing_key is not None and self.pairing_key != "":
            d["pairingKey"] = self.pairing_key
        if self.dataplane_version is not None and self.dataplane_version != 0:
            d["dataplaneVersion"] = self.dataplane_version
        if self.cloud_router_ipv6_interface_id is not None and self.cloud_router_ipv6_interface_id != "":
            d["cloudRouterIpv6InterfaceId"] = self.cloud_router_ipv6_interface_id
        if self.state is not None and self.state != "":
            d["state"] = self.state
        if self.router is not None and self.router != "":
            d["router"] = self.router
        if self.remote_service is not None and self.remote_service != "":
            d["remoteService"] = self.remote_service
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.candidate_customer_router_ipv6_address is not None and self.candidate_customer_router_ipv6_address != "":
            d["candidateCustomerRouterIpv6Address"] = self.candidate_customer_router_ipv6_address
        if self.bandwidth is not None and self.bandwidth != "":
            d["bandwidth"] = self.bandwidth
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["candidateSubnets"] = self.candidate_subnets
        if self.candidate_cloud_router_ipv6_address is not None and self.candidate_cloud_router_ipv6_address != "":
            d["candidateCloudRouterIpv6Address"] = self.candidate_cloud_router_ipv6_address
        if self.partner_asn is not None and self.partner_asn != "":
            d["partnerAsn"] = self.partner_asn
        if self.cloud_router_ip_address is not None and self.cloud_router_ip_address != "":
            d["cloudRouterIpAddress"] = self.cloud_router_ip_address
        if self.google_reference_id is not None and self.google_reference_id != "":
            d["googleReferenceId"] = self.google_reference_id
        if self.mtu is not None and self.mtu != 0:
            d["mtu"] = self.mtu
        if self.encryption is not None and self.encryption != "":
            d["encryption"] = self.encryption
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#interconnectattachment"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InterconnectAttachment_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.interconnect_attachments  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "interconnect-attachment") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an InterconnectAttachment in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("InterconnectAttachment")
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InterconnectAttachment' not specified",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"InterconnectAttachment {name!r} already exists", "ALREADY_EXISTS")

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        interconnect_ref = body.get("interconnect") or ""
        interconnect_name = normalize_name(interconnect_ref)
        if interconnect_name and interconnect_name not in self.state.interconnects:
            return create_gcp_error(
                404,
                f"Interconnect {interconnect_name!r} not found",
                "NOT_FOUND",
            )
        router_ref = body.get("router") or ""
        router_name = normalize_name(router_ref)
        if router_name and router_name not in self.state.routers:
            return create_gcp_error(404, f"Router {router_name!r} not found", "NOT_FOUND")

        resource = InterconnectAttachment(
            customer_router_ipv6_interface_id=body.get("customerRouterIpv6InterfaceId", ""),
            edge_availability_domain=body.get("edgeAvailabilityDomain", ""),
            creation_timestamp=body.get("creationTimestamp") or datetime.now(timezone.utc).isoformat(),
            customer_router_ipv6_address=body.get("customerRouterIpv6Address", ""),
            partner_metadata=body.get("partnerMetadata", {}),
            description=body.get("description", ""),
            ipsec_internal_addresses=body.get("ipsecInternalAddresses", []),
            label_fingerprint=str(uuid.uuid4())[:8],
            l2_forwarding=body.get("l2Forwarding", {}),
            type=body.get("type", ""),
            params=body.get("params", {}),
            customer_router_ip_address=body.get("customerRouterIpAddress", ""),
            vlan_tag8021q=body.get("vlanTag8021q") or 0,
            stack_type=body.get("stackType", ""),
            private_interconnect_info=body.get("privateInterconnectInfo", {}),
            satisfies_pzs=bool(body.get("satisfiesPzs")) if "satisfiesPzs" in body else False,
            admin_enabled=bool(body.get("adminEnabled")) if "adminEnabled" in body else False,
            configuration_constraints=body.get("configurationConstraints", {}),
            operational_status=body.get("operationalStatus", ""),
            candidate_cloud_router_ip_address=body.get("candidateCloudRouterIpAddress", ""),
            subnet_length=body.get("subnetLength") or 0,
            attachment_group=body.get("attachmentGroup", ""),
            labels=body.get("labels", {}),
            candidate_customer_router_ip_address=body.get("candidateCustomerRouterIpAddress", ""),
            candidate_ipv6_subnets=body.get("candidateIpv6Subnets", []),
            interconnect=body.get("interconnect", ""),
            cloud_router_ipv6_address=body.get("cloudRouterIpv6Address", ""),
            pairing_key=body.get("pairingKey", ""),
            dataplane_version=body.get("dataplaneVersion") or 0,
            cloud_router_ipv6_interface_id=body.get("cloudRouterIpv6InterfaceId", ""),
            state=body.get("state", ""),
            router=body.get("router", ""),
            remote_service=body.get("remoteService", ""),
            region=region,
            candidate_customer_router_ipv6_address=body.get("candidateCustomerRouterIpv6Address", ""),
            bandwidth=body.get("bandwidth", ""),
            name=name,
            candidate_subnets=body.get("candidateSubnets", []),
            candidate_cloud_router_ipv6_address=body.get("candidateCloudRouterIpv6Address", ""),
            partner_asn=body.get("partnerAsn", ""),
            cloud_router_ip_address=body.get("cloudRouterIpAddress", ""),
            google_reference_id=body.get("googleReferenceId", ""),
            mtu=body.get("mtu") or 0,
            encryption=body.get("encryption", ""),
            id=self._generate_id(),
            interconnect_name=interconnect_name,
            router_name=router_name,
        )
        if not params.get("validateOnly"):
            self.resources[resource.name] = resource

        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/interconnectAttachments/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified interconnect attachment."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("interconnectAttachment")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'interconnectAttachment' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of interconnect attachments.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]

        region = params.get("region")
        if region:
            resources = [r for r in resources if r.region == region]
        scope_key = f"regions/{region or 'us-central1'}"
        if not resources:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items = {scope_key: {"InterconnectAttachments": [r.to_dict() for r in resources]}}

        return {
            "kind": "compute#interconnectattachmentAggregatedList",
            "id": f"projects/{project}/aggregated/interconnectAttachments",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of interconnect attachments contained within
the specified region."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]

        return {
            "kind": "compute#interconnectattachmentList",
            "id": f"projects/{project}/regions/{region}",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on an InterconnectAttachment. To learn more about labels,
read the Labeling
Resources documentation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("RegionSetLabelsRequest")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'RegionSetLabelsRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(404, f"The resource {resource_name!r} was not found", "NOT_FOUND")
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {resource_name!r} was not found", "NOT_FOUND")
        resource.labels = body.get("labels", {}) or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        return make_operation(
            operation_type="setLabels",
            resource_link=f"projects/{project}/regions/{region}/interconnectAttachments/{resource.name}",
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified interconnect attachment with the data included in the
request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        attachment_name = params.get("interconnectAttachment")
        if not attachment_name:
            return create_gcp_error(
                400,
                "Required field 'interconnectAttachment' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("InterconnectAttachment")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'InterconnectAttachment' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(attachment_name)
        if not resource:
            return create_gcp_error(404, f"The resource {attachment_name!r} was not found", "NOT_FOUND")
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {attachment_name!r} was not found", "NOT_FOUND")
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "Resource name cannot be changed", "INVALID_ARGUMENT")
        if "region" in body and body.get("region") and body.get("region") != region:
            return create_gcp_error(400, "Region cannot be changed", "INVALID_ARGUMENT")

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        if "customerRouterIpv6InterfaceId" in body:
            resource.customer_router_ipv6_interface_id = body.get("customerRouterIpv6InterfaceId") or ""
        if "edgeAvailabilityDomain" in body:
            resource.edge_availability_domain = body.get("edgeAvailabilityDomain") or ""
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""
        if "customerRouterIpv6Address" in body:
            resource.customer_router_ipv6_address = body.get("customerRouterIpv6Address") or ""
        if "partnerMetadata" in body:
            resource.partner_metadata = body.get("partnerMetadata") or {}
        if "description" in body:
            resource.description = body.get("description") or ""
        if "ipsecInternalAddresses" in body:
            resource.ipsec_internal_addresses = body.get("ipsecInternalAddresses") or []
        if "l2Forwarding" in body:
            resource.l2_forwarding = body.get("l2Forwarding") or {}
        if "type" in body:
            resource.type = body.get("type") or ""
        if "params" in body:
            resource.params = body.get("params") or {}
        if "customerRouterIpAddress" in body:
            resource.customer_router_ip_address = body.get("customerRouterIpAddress") or ""
        if "vlanTag8021q" in body:
            resource.vlan_tag8021q = body.get("vlanTag8021q") or 0
        if "stackType" in body:
            resource.stack_type = body.get("stackType") or ""
        if "privateInterconnectInfo" in body:
            resource.private_interconnect_info = body.get("privateInterconnectInfo") or {}
        if "satisfiesPzs" in body:
            resource.satisfies_pzs = bool(body.get("satisfiesPzs"))
        if "adminEnabled" in body:
            resource.admin_enabled = bool(body.get("adminEnabled"))
        if "configurationConstraints" in body:
            resource.configuration_constraints = body.get("configurationConstraints") or {}
        if "operationalStatus" in body:
            resource.operational_status = body.get("operationalStatus") or ""
        if "candidateCloudRouterIpAddress" in body:
            resource.candidate_cloud_router_ip_address = body.get("candidateCloudRouterIpAddress") or ""
        if "subnetLength" in body:
            resource.subnet_length = body.get("subnetLength") or 0
        if "attachmentGroup" in body:
            resource.attachment_group = body.get("attachmentGroup") or ""
        if "labels" in body:
            resource.labels = body.get("labels") or {}
            resource.label_fingerprint = str(uuid.uuid4())[:8]
        if "candidateCustomerRouterIpAddress" in body:
            resource.candidate_customer_router_ip_address = body.get("candidateCustomerRouterIpAddress") or ""
        if "candidateIpv6Subnets" in body:
            resource.candidate_ipv6_subnets = body.get("candidateIpv6Subnets") or []
        if "interconnect" in body:
            interconnect_ref = body.get("interconnect") or ""
            interconnect_name = normalize_name(interconnect_ref)
            if interconnect_name and interconnect_name not in self.state.interconnects:
                return create_gcp_error(
                    404,
                    f"Interconnect {interconnect_name!r} not found",
                    "NOT_FOUND",
                )
            resource.interconnect = interconnect_ref
            resource.interconnect_name = interconnect_name
        if "cloudRouterIpv6Address" in body:
            resource.cloud_router_ipv6_address = body.get("cloudRouterIpv6Address") or ""
        if "pairingKey" in body:
            resource.pairing_key = body.get("pairingKey") or ""
        if "dataplaneVersion" in body:
            resource.dataplane_version = body.get("dataplaneVersion") or 0
        if "cloudRouterIpv6InterfaceId" in body:
            resource.cloud_router_ipv6_interface_id = body.get("cloudRouterIpv6InterfaceId") or ""
        if "state" in body:
            resource.state = body.get("state") or ""
        if "router" in body:
            router_ref = body.get("router") or ""
            router_name = normalize_name(router_ref)
            if router_name and router_name not in self.state.routers:
                return create_gcp_error(404, f"Router {router_name!r} not found", "NOT_FOUND")
            resource.router = router_ref
            resource.router_name = router_name
        if "remoteService" in body:
            resource.remote_service = body.get("remoteService") or ""
        if "candidateCustomerRouterIpv6Address" in body:
            resource.candidate_customer_router_ipv6_address = body.get("candidateCustomerRouterIpv6Address") or ""
        if "bandwidth" in body:
            resource.bandwidth = body.get("bandwidth") or ""
        if "candidateSubnets" in body:
            resource.candidate_subnets = body.get("candidateSubnets") or []
        if "candidateCloudRouterIpv6Address" in body:
            resource.candidate_cloud_router_ipv6_address = body.get("candidateCloudRouterIpv6Address") or ""
        if "partnerAsn" in body:
            resource.partner_asn = body.get("partnerAsn") or ""
        if "cloudRouterIpAddress" in body:
            resource.cloud_router_ip_address = body.get("cloudRouterIpAddress") or ""
        if "googleReferenceId" in body:
            resource.google_reference_id = body.get("googleReferenceId") or ""
        if "mtu" in body:
            resource.mtu = body.get("mtu") or 0
        if "encryption" in body:
            resource.encryption = body.get("encryption") or ""

        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/regions/{region}/interconnectAttachments/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified interconnect attachment."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        attachment_name = params.get("interconnectAttachment")
        if not attachment_name:
            return create_gcp_error(
                400,
                "Required field 'interconnectAttachment' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(attachment_name)
        if not resource:
            return create_gcp_error(404, f"The resource {attachment_name!r} was not found", "NOT_FOUND")
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {attachment_name!r} was not found", "NOT_FOUND")
        self.resources.pop(attachment_name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/interconnectAttachments/{attachment_name}",
            params=params,
        )


class interconnect_attachment_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setLabels': interconnect_attachment_RequestParser._parse_setLabels,
            'aggregatedList': interconnect_attachment_RequestParser._parse_aggregatedList,
            'list': interconnect_attachment_RequestParser._parse_list,
            'delete': interconnect_attachment_RequestParser._parse_delete,
            'insert': interconnect_attachment_RequestParser._parse_insert,
            'get': interconnect_attachment_RequestParser._parse_get,
            'patch': interconnect_attachment_RequestParser._parse_patch,
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
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['RegionSetLabelsRequest'] = body.get('RegionSetLabelsRequest')
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
        if 'validateOnly' in query_params:
            params['validateOnly'] = query_params['validateOnly']
        # Body params
        params['InterconnectAttachment'] = body.get('InterconnectAttachment')
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
        params['InterconnectAttachment'] = body.get('InterconnectAttachment')
        return params


class interconnect_attachment_ResponseSerializer:
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
            'setLabels': interconnect_attachment_ResponseSerializer._serialize_setLabels,
            'aggregatedList': interconnect_attachment_ResponseSerializer._serialize_aggregatedList,
            'list': interconnect_attachment_ResponseSerializer._serialize_list,
            'delete': interconnect_attachment_ResponseSerializer._serialize_delete,
            'insert': interconnect_attachment_ResponseSerializer._serialize_insert,
            'get': interconnect_attachment_ResponseSerializer._serialize_get,
            'patch': interconnect_attachment_ResponseSerializer._serialize_patch,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

