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
class Interconnect:
    creation_timestamp: str = ""
    requested_features: List[Any] = field(default_factory=list)
    link_type: str = ""
    interconnect_groups: List[Any] = field(default_factory=list)
    provisioned_link_count: int = 0
    state: str = ""
    customer_name: str = ""
    location: str = ""
    macsec: Dict[str, Any] = field(default_factory=dict)
    requested_link_count: int = 0
    available_features: List[Any] = field(default_factory=list)
    remote_location: str = ""
    expected_outages: List[Any] = field(default_factory=list)
    name: str = ""
    wire_groups: List[Any] = field(default_factory=list)
    noc_contact_email: str = ""
    google_ip_address: str = ""
    admin_enabled: bool = False
    application_aware_interconnect: Dict[str, Any] = field(default_factory=dict)
    operational_status: str = ""
    satisfies_pzs: bool = False
    subzone: str = ""
    macsec_enabled: bool = False
    description: str = ""
    interconnect_attachments: List[Any] = field(default_factory=list)
    circuit_infos: List[Any] = field(default_factory=list)
    aai_enabled: bool = False
    interconnect_type: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    google_reference_id: str = ""
    label_fingerprint: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    peer_ip_address: str = ""
    id: str = ""

    # Internal dependency tracking — not in API response
    attachment_names: List[str] = field(default_factory=list)  # tracks InterconnectAttachment children


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["requestedFeatures"] = self.requested_features
        if self.link_type is not None and self.link_type != "":
            d["linkType"] = self.link_type
        d["interconnectGroups"] = self.interconnect_groups
        if self.provisioned_link_count is not None and self.provisioned_link_count != 0:
            d["provisionedLinkCount"] = self.provisioned_link_count
        if self.state is not None and self.state != "":
            d["state"] = self.state
        if self.customer_name is not None and self.customer_name != "":
            d["customerName"] = self.customer_name
        if self.location is not None and self.location != "":
            d["location"] = self.location
        d["macsec"] = self.macsec
        if self.requested_link_count is not None and self.requested_link_count != 0:
            d["requestedLinkCount"] = self.requested_link_count
        d["availableFeatures"] = self.available_features
        if self.remote_location is not None and self.remote_location != "":
            d["remoteLocation"] = self.remote_location
        d["expectedOutages"] = self.expected_outages
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["wireGroups"] = self.wire_groups
        if self.noc_contact_email is not None and self.noc_contact_email != "":
            d["nocContactEmail"] = self.noc_contact_email
        if self.google_ip_address is not None and self.google_ip_address != "":
            d["googleIpAddress"] = self.google_ip_address
        d["adminEnabled"] = self.admin_enabled
        d["applicationAwareInterconnect"] = self.application_aware_interconnect
        if self.operational_status is not None and self.operational_status != "":
            d["operationalStatus"] = self.operational_status
        d["satisfiesPzs"] = self.satisfies_pzs
        if self.subzone is not None and self.subzone != "":
            d["subzone"] = self.subzone
        d["macsecEnabled"] = self.macsec_enabled
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["interconnectAttachments"] = self.interconnect_attachments
        d["circuitInfos"] = self.circuit_infos
        d["aaiEnabled"] = self.aai_enabled
        if self.interconnect_type is not None and self.interconnect_type != "":
            d["interconnectType"] = self.interconnect_type
        d["labels"] = self.labels
        if self.google_reference_id is not None and self.google_reference_id != "":
            d["googleReferenceId"] = self.google_reference_id
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        d["params"] = self.params
        if self.peer_ip_address is not None and self.peer_ip_address != "":
            d["peerIpAddress"] = self.peer_ip_address
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#interconnect"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Interconnect_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.interconnects  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "interconnect") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an Interconnect in the specified project using
the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("Interconnect")
        if not body:
            return create_gcp_error(400, "Required field 'Interconnect' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"Interconnect {name!r} already exists", "ALREADY_EXISTS")

        resource = Interconnect(
            creation_timestamp=body.get("creationTimestamp") or datetime.now(timezone.utc).isoformat(),
            requested_features=body.get("requestedFeatures", []),
            link_type=body.get("linkType", ""),
            interconnect_groups=body.get("interconnectGroups", []),
            provisioned_link_count=body.get("provisionedLinkCount") or 0,
            state=body.get("state", ""),
            customer_name=body.get("customerName", ""),
            location=body.get("location", ""),
            macsec=body.get("macsec", {}),
            requested_link_count=body.get("requestedLinkCount") or 0,
            available_features=body.get("availableFeatures", []),
            remote_location=body.get("remoteLocation", ""),
            expected_outages=body.get("expectedOutages", []),
            name=name,
            wire_groups=body.get("wireGroups", []),
            noc_contact_email=body.get("nocContactEmail", ""),
            google_ip_address=body.get("googleIpAddress", ""),
            admin_enabled=bool(body.get("adminEnabled")) if "adminEnabled" in body else False,
            application_aware_interconnect=body.get("applicationAwareInterconnect", {}),
            operational_status=body.get("operationalStatus", ""),
            satisfies_pzs=bool(body.get("satisfiesPzs")) if "satisfiesPzs" in body else False,
            subzone=body.get("subzone", ""),
            macsec_enabled=bool(body.get("macsecEnabled")) if "macsecEnabled" in body else False,
            description=body.get("description", ""),
            interconnect_attachments=body.get("interconnectAttachments", []),
            circuit_infos=body.get("circuitInfos", []),
            aai_enabled=bool(body.get("aaiEnabled")) if "aaiEnabled" in body else False,
            interconnect_type=body.get("interconnectType", ""),
            labels=body.get("labels", {}),
            google_reference_id=body.get("googleReferenceId", ""),
            label_fingerprint=body.get("labelFingerprint") or str(uuid.uuid4())[:8],
            params=body.get("params", {}),
            peer_ip_address=body.get("peerIpAddress", ""),
            id=self._generate_id(),
        )
        if not params.get("validateOnly"):
            self.resources[resource.name] = resource

        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/interconnects/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified Interconnect. Get a list of available Interconnects
by making a list() request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("interconnect")
        if not name:
            return create_gcp_error(400, "Required field 'interconnect' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of Interconnects available to the specified project."""
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
            "kind": "compute#interconnectList",
            "id": f"projects/{project}/global/interconnects",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified Interconnect with the data included in the request.
This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("interconnect")
        if not name:
            return create_gcp_error(400, "Required field 'interconnect' not specified", "INVALID_ARGUMENT")
        body = params.get("Interconnect")
        if not body:
            return create_gcp_error(400, "Required field 'Interconnect' not specified", "INVALID_ARGUMENT")

        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")

        if "requestedFeatures" in body:
            resource.requested_features = body.get("requestedFeatures") or []
        if "linkType" in body:
            resource.link_type = body.get("linkType") or ""
        if "interconnectGroups" in body:
            resource.interconnect_groups = body.get("interconnectGroups") or []
        if "provisionedLinkCount" in body:
            resource.provisioned_link_count = body.get("provisionedLinkCount") or 0
        if "state" in body:
            resource.state = body.get("state") or ""
        if "customerName" in body:
            resource.customer_name = body.get("customerName") or ""
        if "location" in body:
            resource.location = body.get("location") or ""
        if "macsec" in body:
            resource.macsec = body.get("macsec") or {}
        if "requestedLinkCount" in body:
            resource.requested_link_count = body.get("requestedLinkCount") or 0
        if "availableFeatures" in body:
            resource.available_features = body.get("availableFeatures") or []
        if "remoteLocation" in body:
            resource.remote_location = body.get("remoteLocation") or ""
        if "expectedOutages" in body:
            resource.expected_outages = body.get("expectedOutages") or []
        if "wireGroups" in body:
            resource.wire_groups = body.get("wireGroups") or []
        if "nocContactEmail" in body:
            resource.noc_contact_email = body.get("nocContactEmail") or ""
        if "googleIpAddress" in body:
            resource.google_ip_address = body.get("googleIpAddress") or ""
        if "adminEnabled" in body:
            resource.admin_enabled = bool(body.get("adminEnabled"))
        if "applicationAwareInterconnect" in body:
            resource.application_aware_interconnect = body.get("applicationAwareInterconnect") or {}
        if "operationalStatus" in body:
            resource.operational_status = body.get("operationalStatus") or ""
        if "satisfiesPzs" in body:
            resource.satisfies_pzs = bool(body.get("satisfiesPzs"))
        if "subzone" in body:
            resource.subzone = body.get("subzone") or ""
        if "macsecEnabled" in body:
            resource.macsec_enabled = bool(body.get("macsecEnabled"))
        if "description" in body:
            resource.description = body.get("description") or ""
        if "interconnectAttachments" in body:
            resource.interconnect_attachments = body.get("interconnectAttachments") or []
        if "circuitInfos" in body:
            resource.circuit_infos = body.get("circuitInfos") or []
        if "aaiEnabled" in body:
            resource.aai_enabled = bool(body.get("aaiEnabled"))
        if "interconnectType" in body:
            resource.interconnect_type = body.get("interconnectType") or ""
        if "labels" in body:
            resource.labels = body.get("labels") or {}
            resource.label_fingerprint = str(uuid.uuid4())[:8]
        if "googleReferenceId" in body:
            resource.google_reference_id = body.get("googleReferenceId") or ""
        if "labelFingerprint" in body:
            resource.label_fingerprint = body.get("labelFingerprint") or resource.label_fingerprint
        if "params" in body:
            resource.params = body.get("params") or {}
        if "peerIpAddress" in body:
            resource.peer_ip_address = body.get("peerIpAddress") or ""

        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/interconnects/{resource.name}",
            params=params,
        )

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on an Interconnect. To learn more about labels,
read the Labeling
Resources documentation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("GlobalSetLabelsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'GlobalSetLabelsRequest' not specified",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(404, f"The resource {resource_name!r} was not found", "NOT_FOUND")

        resource.labels = body.get("labels") or {}
        resource.label_fingerprint = str(uuid.uuid4())[:8]

        return make_operation(
            operation_type="setLabels",
            resource_link=f"projects/{project}/global/interconnects/{resource.name}",
            params=params,
        )

    def getDiagnostics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the interconnectDiagnostics for the specified
Interconnect.

In the event of a
global outage, do not use this API to make decisions about where to
redirect your network traffic.

Unlike a V..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("interconnect")
        if not name:
            return create_gcp_error(400, "Required field 'interconnect' not specified", "INVALID_ARGUMENT")

        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")

        return {
            "kind": "compute#interconnectDiagnostics",
            "interconnect": resource.to_dict(),
        }

    def getMacsecConfig(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the interconnectMacsecConfig for the specified
Interconnect."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("interconnect")
        if not name:
            return create_gcp_error(400, "Required field 'interconnect' not specified", "INVALID_ARGUMENT")

        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")

        return {
            "kind": "compute#interconnectMacsecConfig",
            "macsec": resource.macsec,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified Interconnect."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("interconnect")
        if not name:
            return create_gcp_error(400, "Required field 'interconnect' not specified", "INVALID_ARGUMENT")

        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if resource.attachment_names:
            return create_gcp_error(
                400,
                "Cannot delete interconnect with active attachments",
                "FAILED_PRECONDITION",
            )

        del self.resources[name]

        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/interconnects/{resource.name}",
            params=params,
        )


class interconnect_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'patch': interconnect_RequestParser._parse_patch,
            'list': interconnect_RequestParser._parse_list,
            'setLabels': interconnect_RequestParser._parse_setLabels,
            'getDiagnostics': interconnect_RequestParser._parse_getDiagnostics,
            'get': interconnect_RequestParser._parse_get,
            'insert': interconnect_RequestParser._parse_insert,
            'getMacsecConfig': interconnect_RequestParser._parse_getMacsecConfig,
            'delete': interconnect_RequestParser._parse_delete,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['Interconnect'] = body.get('Interconnect')
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
    def _parse_getDiagnostics(
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
        params['Interconnect'] = body.get('Interconnect')
        return params

    @staticmethod
    def _parse_getMacsecConfig(
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


class interconnect_ResponseSerializer:
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
            'patch': interconnect_ResponseSerializer._serialize_patch,
            'list': interconnect_ResponseSerializer._serialize_list,
            'setLabels': interconnect_ResponseSerializer._serialize_setLabels,
            'getDiagnostics': interconnect_ResponseSerializer._serialize_getDiagnostics,
            'get': interconnect_ResponseSerializer._serialize_get,
            'insert': interconnect_ResponseSerializer._serialize_insert,
            'getMacsecConfig': interconnect_ResponseSerializer._serialize_getMacsecConfig,
            'delete': interconnect_ResponseSerializer._serialize_delete,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getDiagnostics(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getMacsecConfig(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

