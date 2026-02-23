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
class Reservation:
    advanced_deployment_control: Dict[str, Any] = field(default_factory=dict)
    specific_reservation: Dict[str, Any] = field(default_factory=dict)
    linked_commitments: List[Any] = field(default_factory=list)
    delete_at_time: str = ""
    aggregate_reservation: Dict[str, Any] = field(default_factory=dict)
    satisfies_pzs: bool = False
    scheduling_type: str = ""
    resource_status: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    share_settings: Dict[str, Any] = field(default_factory=dict)
    protection_tier: str = ""
    specific_reservation_required: bool = False
    commitment: str = ""
    enable_emergent_maintenance: bool = False
    name: str = ""
    reservation_sharing_policy: Dict[str, Any] = field(default_factory=dict)
    delete_after_duration: Dict[str, Any] = field(default_factory=dict)
    deployment_type: str = ""
    resource_policies: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    creation_timestamp: str = ""
    early_access_maintenance: str = ""
    zone: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["advancedDeploymentControl"] = self.advanced_deployment_control
        d["specificReservation"] = self.specific_reservation
        d["linkedCommitments"] = self.linked_commitments
        if self.delete_at_time is not None and self.delete_at_time != "":
            d["deleteAtTime"] = self.delete_at_time
        d["aggregateReservation"] = self.aggregate_reservation
        d["satisfiesPzs"] = self.satisfies_pzs
        if self.scheduling_type is not None and self.scheduling_type != "":
            d["schedulingType"] = self.scheduling_type
        d["resourceStatus"] = self.resource_status
        if self.status is not None and self.status != "":
            d["status"] = self.status
        d["shareSettings"] = self.share_settings
        if self.protection_tier is not None and self.protection_tier != "":
            d["protectionTier"] = self.protection_tier
        d["specificReservationRequired"] = self.specific_reservation_required
        if self.commitment is not None and self.commitment != "":
            d["commitment"] = self.commitment
        d["enableEmergentMaintenance"] = self.enable_emergent_maintenance
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["reservationSharingPolicy"] = self.reservation_sharing_policy
        d["deleteAfterDuration"] = self.delete_after_duration
        if self.deployment_type is not None and self.deployment_type != "":
            d["deploymentType"] = self.deployment_type
        d["resourcePolicies"] = self.resource_policies
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.early_access_maintenance is not None and self.early_access_maintenance != "":
            d["earlyAccessMaintenance"] = self.early_access_maintenance
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        d["iamPolicy"] = self.iam_policy
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#reservation"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Reservation_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.reservations  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "reservation") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new reservation. For more information, readReserving zonal
resources."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("Reservation") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Reservation' not specified",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'name' not specified",
                "INVALID_ARGUMENT",
            )
        if name in self.resources:
            return create_gcp_error(409, f"Reservation {name!r} already exists", "ALREADY_EXISTS")
        creation_timestamp = body.get("creationTimestamp") or datetime.now(timezone.utc).isoformat()
        resource = Reservation(
            advanced_deployment_control=body.get("advancedDeploymentControl", {}),
            specific_reservation=body.get("specificReservation", {}),
            linked_commitments=body.get("linkedCommitments", []),
            delete_at_time=body.get("deleteAtTime", ""),
            aggregate_reservation=body.get("aggregateReservation", {}),
            satisfies_pzs=body.get("satisfiesPzs", False),
            scheduling_type=body.get("schedulingType", ""),
            resource_status=body.get("resourceStatus", {}),
            status=body.get("status", ""),
            share_settings=body.get("shareSettings", {}),
            protection_tier=body.get("protectionTier", ""),
            specific_reservation_required=body.get("specificReservationRequired", False),
            commitment=body.get("commitment", ""),
            enable_emergent_maintenance=body.get("enableEmergentMaintenance", False),
            name=name,
            reservation_sharing_policy=body.get("reservationSharingPolicy", {}),
            delete_after_duration=body.get("deleteAfterDuration", {}),
            deployment_type=body.get("deploymentType", ""),
            resource_policies=body.get("resourcePolicies", {}),
            description=body.get("description", ""),
            creation_timestamp=creation_timestamp,
            early_access_maintenance=body.get("earlyAccessMaintenance", ""),
            zone=zone,
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/zones/{zone}/reservations/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves information about the specified reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        reservation_name = params.get("reservation")
        if not reservation_name:
            return create_gcp_error(
                400,
                "Required field 'reservation' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(reservation_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{reservation_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A list of all the reservations that have been configured for the
specified project in specified zone."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        if zone:
            resources = [resource for resource in resources if resource.zone == zone]
        return {
            "kind": "compute#reservationList",
            "id": f"projects/{project}/zones/{zone}/reservations",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of reservations.

To prevent failure, it is recommended that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        zone = params.get("zone")
        if zone:
            resources = [resource for resource in resources if resource.zone == zone]
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if resources:
            items = {scope_key: {"Reservations": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#reservationAggregatedList",
            "id": f"projects/{project}/aggregated/Reservations",
            "items": items,
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update share settings of the reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        reservation_name = params.get("reservation")
        if not reservation_name:
            return create_gcp_error(
                400,
                "Required field 'reservation' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("Reservation") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Reservation' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(reservation_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{reservation_name}' was not found",
                "NOT_FOUND",
            )
        if "shareSettings" in body:
            resource.share_settings = body.get("shareSettings", {})
        if "reservationSharingPolicy" in body:
            resource.reservation_sharing_policy = body.get("reservationSharingPolicy", {})
        resource_link = f"projects/{project}/zones/{zone}/reservations/{resource.name}"
        return make_operation(
            operation_type="update",
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
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("ZoneSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ZoneSetPolicyRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        policy = body.get("policy", {})
        resource.iam_policy = policy
        return policy

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TestPermissionsRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        permissions = body.get("permissions", [])
        return {"permissions": permissions}

    def resize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resizes the reservation (applicable to standalone reservations only). For
more information, readModifying
reservations."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        reservation_name = params.get("reservation")
        if not reservation_name:
            return create_gcp_error(
                400,
                "Required field 'reservation' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("ReservationsResizeRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ReservationsResizeRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(reservation_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{reservation_name}' was not found",
                "NOT_FOUND",
            )
        new_count = body.get("specificReservationCount")
        if new_count is None:
            new_count = body.get("count")
        if new_count is not None:
            try:
                new_count_value = int(new_count)
            except (TypeError, ValueError):
                return create_gcp_error(
                    400,
                    "Invalid field 'specificReservationCount'",
                    "INVALID_ARGUMENT",
                )
            if new_count_value < 0:
                return create_gcp_error(
                    400,
                    "Invalid field 'specificReservationCount'",
                    "INVALID_ARGUMENT",
                )
            if resource.specific_reservation is None:
                resource.specific_reservation = {}
            resource.specific_reservation["count"] = new_count_value
        resource_link = f"projects/{project}/zones/{zone}/reservations/{resource.name}"
        return make_operation(
            operation_type="resize",
            resource_link=resource_link,
            params=params,
        )

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        return resource.iam_policy or {}

    def performMaintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform maintenance on an extended reservation"""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        reservation_name = params.get("reservation")
        if not reservation_name:
            return create_gcp_error(
                400,
                "Required field 'reservation' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("ReservationsPerformMaintenanceRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ReservationsPerformMaintenanceRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(reservation_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{reservation_name}' was not found",
                "NOT_FOUND",
            )
        if "maintenanceStatus" in body:
            resource.resource_status = resource.resource_status or {}
            resource.resource_status["maintenanceStatus"] = body.get("maintenanceStatus")
        resource_link = f"projects/{project}/zones/{zone}/reservations/{resource.name}"
        return make_operation(
            operation_type="performMaintenance",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not specified",
                "INVALID_ARGUMENT",
            )
        reservation_name = params.get("reservation")
        if not reservation_name:
            return create_gcp_error(
                400,
                "Required field 'reservation' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(reservation_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{reservation_name}' was not found",
                "NOT_FOUND",
            )
        del self.resources[reservation_name]
        resource_link = f"projects/{project}/zones/{zone}/reservations/{reservation_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class reservation_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'insert': reservation_RequestParser._parse_insert,
            'testIamPermissions': reservation_RequestParser._parse_testIamPermissions,
            'update': reservation_RequestParser._parse_update,
            'resize': reservation_RequestParser._parse_resize,
            'list': reservation_RequestParser._parse_list,
            'getIamPolicy': reservation_RequestParser._parse_getIamPolicy,
            'delete': reservation_RequestParser._parse_delete,
            'setIamPolicy': reservation_RequestParser._parse_setIamPolicy,
            'get': reservation_RequestParser._parse_get,
            'aggregatedList': reservation_RequestParser._parse_aggregatedList,
            'performMaintenance': reservation_RequestParser._parse_performMaintenance,
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
        params['Reservation'] = body.get('Reservation')
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
        params['Reservation'] = body.get('Reservation')
        return params

    @staticmethod
    def _parse_resize(
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
        params['ReservationsResizeRequest'] = body.get('ReservationsResizeRequest')
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
        params['ZoneSetPolicyRequest'] = body.get('ZoneSetPolicyRequest')
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
    def _parse_performMaintenance(
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
        params['ReservationsPerformMaintenanceRequest'] = body.get('ReservationsPerformMaintenanceRequest')
        return params


class reservation_ResponseSerializer:
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
            'insert': reservation_ResponseSerializer._serialize_insert,
            'testIamPermissions': reservation_ResponseSerializer._serialize_testIamPermissions,
            'update': reservation_ResponseSerializer._serialize_update,
            'resize': reservation_ResponseSerializer._serialize_resize,
            'list': reservation_ResponseSerializer._serialize_list,
            'getIamPolicy': reservation_ResponseSerializer._serialize_getIamPolicy,
            'delete': reservation_ResponseSerializer._serialize_delete,
            'setIamPolicy': reservation_ResponseSerializer._serialize_setIamPolicy,
            'get': reservation_ResponseSerializer._serialize_get,
            'aggregatedList': reservation_ResponseSerializer._serialize_aggregatedList,
            'performMaintenance': reservation_ResponseSerializer._serialize_performMaintenance,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_resize(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_performMaintenance(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

