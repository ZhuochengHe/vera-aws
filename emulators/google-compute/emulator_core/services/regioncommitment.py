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
class RegionCommitment:
    creation_timestamp: str = ""
    region: str = ""
    category: str = ""
    resources: List[Any] = field(default_factory=list)
    merge_source_commitments: List[Any] = field(default_factory=list)
    description: str = ""
    reservations: List[Any] = field(default_factory=list)
    name: str = ""
    plan: str = ""
    auto_renew: bool = False
    status: str = ""
    status_message: str = ""
    existing_reservations: List[Any] = field(default_factory=list)
    end_timestamp: str = ""
    license_resource: Dict[str, Any] = field(default_factory=dict)
    resource_status: Dict[str, Any] = field(default_factory=dict)
    custom_end_timestamp: str = ""
    start_timestamp: str = ""
    type: str = ""
    split_source_commitment: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.category is not None and self.category != "":
            d["category"] = self.category
        d["resources"] = self.resources
        d["mergeSourceCommitments"] = self.merge_source_commitments
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["reservations"] = self.reservations
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.plan is not None and self.plan != "":
            d["plan"] = self.plan
        d["autoRenew"] = self.auto_renew
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.status_message is not None and self.status_message != "":
            d["statusMessage"] = self.status_message
        d["existingReservations"] = self.existing_reservations
        if self.end_timestamp is not None and self.end_timestamp != "":
            d["endTimestamp"] = self.end_timestamp
        d["licenseResource"] = self.license_resource
        d["resourceStatus"] = self.resource_status
        if self.custom_end_timestamp is not None and self.custom_end_timestamp != "":
            d["customEndTimestamp"] = self.custom_end_timestamp
        if self.start_timestamp is not None and self.start_timestamp != "":
            d["startTimestamp"] = self.start_timestamp
        if self.type is not None and self.type != "":
            d["type"] = self.type
        if self.split_source_commitment is not None and self.split_source_commitment != "":
            d["splitSourceCommitment"] = self.split_source_commitment
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regioncommitment"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionCommitment_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_commitments  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-commitment") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_commitment_or_error(
        self,
        commitment: str,
        project: str,
        region: str,
    ) -> Any:
        resource = self.resources.get(commitment)
        if not resource:
            return create_gcp_error(
                404,
                (
                    "The resource 'projects/"
                    f"{project}/regions/{region}/commitments/{commitment}' was not found"
                ),
                "NOT_FOUND",
            )
        return resource

    def _filter_resources(self, params: Dict[str, Any]) -> List[RegionCommitment]:
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
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a commitment in the specified project using the data
included in the request."""
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
        body = params.get("Commitment") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Commitment' not found",
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
                f"Commitment '{name}' already exists",
                "ALREADY_EXISTS",
            )
        merge_source_commitments = body.get("mergeSourceCommitments") or []
        for merge_commitment in merge_source_commitments:
            if merge_commitment not in self.resources:
                return create_gcp_error(
                    404,
                    f"Commitment '{merge_commitment}' not found",
                    "NOT_FOUND",
                )
        split_source_commitment = body.get("splitSourceCommitment") or ""
        if split_source_commitment and split_source_commitment not in self.resources:
            return create_gcp_error(
                404,
                f"Commitment '{split_source_commitment}' not found",
                "NOT_FOUND",
            )

        resource = RegionCommitment(
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            region=region,
            category=body.get("category") or "",
            resources=body.get("resources") or [],
            merge_source_commitments=merge_source_commitments,
            description=body.get("description") or "",
            reservations=body.get("reservations") or [],
            name=name,
            plan=body.get("plan") or "",
            auto_renew=body.get("autoRenew") or False,
            status=body.get("status") or "",
            status_message=body.get("statusMessage") or "",
            existing_reservations=body.get("existingReservations") or [],
            end_timestamp=body.get("endTimestamp") or "",
            license_resource=body.get("licenseResource") or {},
            resource_status=body.get("resourceStatus") or {},
            custom_end_timestamp=body.get("customEndTimestamp") or "",
            start_timestamp=body.get("startTimestamp") or "",
            type=body.get("type") or "",
            split_source_commitment=split_source_commitment,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/regions/{region}/commitments/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified commitment resource."""
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
        commitment = params.get("commitment")
        if not commitment:
            return create_gcp_error(
                400,
                "Required field 'commitment' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_commitment_or_error(commitment, project, region)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of commitments by region.

To prevent failure, it is recommended that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        resources = self._filter_resources(params)
        scope_key = f"regions/{params.get('region', 'us-central1')}"
        if resources:
            items = {scope_key: {"RegionCommitments": [r.to_dict() for r in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#regioncommitmentAggregatedList",
            "id": f"projects/{project}/aggregated/commitments",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of commitments contained within
the specified region."""
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
        resources = self._filter_resources(params)
        return {
            "kind": "compute#regioncommitmentList",
            "id": f"projects/{project}/regions/{region}/commitments",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified commitment with the data included in the request.
Update is performed only on selected fields included as part of
update-mask. Only the following fields can be updated: auto_r..."""
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
        commitment = params.get("commitment")
        if not commitment:
            return create_gcp_error(
                400,
                "Required field 'commitment' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Commitment") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Commitment' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_commitment_or_error(commitment, project, region)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            resource_path = f"projects/{project}/regions/{region}/commitments/{commitment}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(
                400,
                "Commitment name cannot be changed",
                "INVALID_ARGUMENT",
            )
        body_region = body.get("region")
        if body_region and body_region != resource.region:
            return create_gcp_error(
                400,
                "Commitment region cannot be changed",
                "INVALID_ARGUMENT",
            )
        if "mergeSourceCommitments" in body:
            merge_source_commitments = body.get("mergeSourceCommitments") or []
            for merge_commitment in merge_source_commitments:
                if merge_commitment not in self.resources:
                    return create_gcp_error(
                        404,
                        f"Commitment '{merge_commitment}' not found",
                        "NOT_FOUND",
                    )
            resource.merge_source_commitments = merge_source_commitments
        if "splitSourceCommitment" in body:
            split_source_commitment = body.get("splitSourceCommitment") or ""
            if split_source_commitment and split_source_commitment not in self.resources:
                return create_gcp_error(
                    404,
                    f"Commitment '{split_source_commitment}' not found",
                    "NOT_FOUND",
                )
            resource.split_source_commitment = split_source_commitment
        if "category" in body:
            resource.category = body.get("category") or ""
        if "resources" in body:
            resource.resources = body.get("resources") or []
        if "description" in body:
            resource.description = body.get("description") or ""
        if "reservations" in body:
            resource.reservations = body.get("reservations") or []
        if "plan" in body:
            resource.plan = body.get("plan") or ""
        if "autoRenew" in body:
            resource.auto_renew = body.get("autoRenew") or False
        if "status" in body:
            resource.status = body.get("status") or ""
        if "statusMessage" in body:
            resource.status_message = body.get("statusMessage") or ""
        if "existingReservations" in body:
            resource.existing_reservations = body.get("existingReservations") or []
        if "endTimestamp" in body:
            resource.end_timestamp = body.get("endTimestamp") or ""
        if "licenseResource" in body:
            resource.license_resource = body.get("licenseResource") or {}
        if "resourceStatus" in body:
            resource.resource_status = body.get("resourceStatus") or {}
        if "customEndTimestamp" in body:
            resource.custom_end_timestamp = body.get("customEndTimestamp") or ""
        if "startTimestamp" in body:
            resource.start_timestamp = body.get("startTimestamp") or ""
        if "type" in body:
            resource.type = body.get("type") or ""
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp") or ""

        resource_link = f"projects/{project}/regions/{region}/commitments/{resource.name}"
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )


class region_commitment_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'update': region_commitment_RequestParser._parse_update,
            'aggregatedList': region_commitment_RequestParser._parse_aggregatedList,
            'get': region_commitment_RequestParser._parse_get,
            'insert': region_commitment_RequestParser._parse_insert,
            'list': region_commitment_RequestParser._parse_list,
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
        if 'paths' in query_params:
            params['paths'] = query_params['paths']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['Commitment'] = body.get('Commitment')
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
        params['Commitment'] = body.get('Commitment')
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


class region_commitment_ResponseSerializer:
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
            'update': region_commitment_ResponseSerializer._serialize_update,
            'aggregatedList': region_commitment_ResponseSerializer._serialize_aggregatedList,
            'get': region_commitment_ResponseSerializer._serialize_get,
            'insert': region_commitment_ResponseSerializer._serialize_insert,
            'list': region_commitment_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

