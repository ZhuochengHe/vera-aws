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
class FutureReservation:
    reservation_mode: str = ""
    creation_timestamp: str = ""
    self_link_with_id: str = ""
    specific_reservation_required: bool = False
    aggregate_reservation: Dict[str, Any] = field(default_factory=dict)
    zone: str = ""
    specific_sku_properties: Dict[str, Any] = field(default_factory=dict)
    auto_delete_auto_created_reservations: bool = False
    reservation_name: str = ""
    name_prefix: str = ""
    enable_emergent_maintenance: bool = False
    deployment_type: str = ""
    scheduling_type: str = ""
    auto_created_reservations_delete_time: str = ""
    description: str = ""
    auto_created_reservations_duration: Dict[str, Any] = field(default_factory=dict)
    commitment_info: Dict[str, Any] = field(default_factory=dict)
    time_window: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    share_settings: Dict[str, Any] = field(default_factory=dict)
    status: Dict[str, Any] = field(default_factory=dict)
    planning_status: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.reservation_mode is not None and self.reservation_mode != "":
            d["reservationMode"] = self.reservation_mode
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        d["specificReservationRequired"] = self.specific_reservation_required
        d["aggregateReservation"] = self.aggregate_reservation
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        d["specificSkuProperties"] = self.specific_sku_properties
        d["autoDeleteAutoCreatedReservations"] = self.auto_delete_auto_created_reservations
        if self.reservation_name is not None and self.reservation_name != "":
            d["reservationName"] = self.reservation_name
        if self.name_prefix is not None and self.name_prefix != "":
            d["namePrefix"] = self.name_prefix
        d["enableEmergentMaintenance"] = self.enable_emergent_maintenance
        if self.deployment_type is not None and self.deployment_type != "":
            d["deploymentType"] = self.deployment_type
        if self.scheduling_type is not None and self.scheduling_type != "":
            d["schedulingType"] = self.scheduling_type
        if self.auto_created_reservations_delete_time is not None and self.auto_created_reservations_delete_time != "":
            d["autoCreatedReservationsDeleteTime"] = self.auto_created_reservations_delete_time
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["autoCreatedReservationsDuration"] = self.auto_created_reservations_duration
        d["commitmentInfo"] = self.commitment_info
        d["timeWindow"] = self.time_window
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["shareSettings"] = self.share_settings
        d["status"] = self.status
        if self.planning_status is not None and self.planning_status != "":
            d["planningStatus"] = self.planning_status
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#futurereservation"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class FutureReservation_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.future_reservations  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "future-reservation") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new Future Reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("FutureReservation") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'FutureReservation' not found",
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
                f"Future reservation '{name}' already exists",
                "ALREADY_EXISTS",
            )

        creation_timestamp = body.get("creationTimestamp") or datetime.now(
            timezone.utc
        ).isoformat()
        resource = FutureReservation(
            reservation_mode=body.get("reservationMode", ""),
            creation_timestamp=creation_timestamp,
            self_link_with_id=body.get("selfLinkWithId", ""),
            specific_reservation_required=body.get(
                "specificReservationRequired", False
            ),
            aggregate_reservation=body.get("aggregateReservation", {}),
            zone=zone,
            specific_sku_properties=body.get("specificSkuProperties", {}),
            auto_delete_auto_created_reservations=body.get(
                "autoDeleteAutoCreatedReservations", False
            ),
            reservation_name=body.get("reservationName", ""),
            name_prefix=body.get("namePrefix", ""),
            enable_emergent_maintenance=body.get(
                "enableEmergentMaintenance", False
            ),
            deployment_type=body.get("deploymentType", ""),
            scheduling_type=body.get("schedulingType", ""),
            auto_created_reservations_delete_time=body.get(
                "autoCreatedReservationsDeleteTime", ""
            ),
            description=body.get("description", ""),
            auto_created_reservations_duration=body.get(
                "autoCreatedReservationsDuration", {}
            ),
            commitment_info=body.get("commitmentInfo", {}),
            time_window=body.get("timeWindow", {}),
            name=name,
            share_settings=body.get("shareSettings", {}),
            status=body.get("status", {}),
            planning_status=body.get("planningStatus", ""),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = (
            f"projects/{project}/zones/{zone}/futureReservations/{resource.name}"
        )
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves information about the specified future reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not found",
                "INVALID_ARGUMENT",
            )
        future_reservation_name = params.get("futureReservation")
        if not future_reservation_name:
            return create_gcp_error(
                400,
                "Required field 'futureReservation' not found",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(future_reservation_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """A list of all the future reservations that have been configured for the
specified project in specified zone."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [
                    resource for resource in resources if resource.name == match.group(1)
                ]
        if zone:
            resources = [resource for resource in resources if resource.zone == zone]

        return {
            "kind": "compute#futurereservationList",
            "id": f"projects/{project}/zones/{zone}/futureReservations",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of future reservations.

To prevent failure, it is recommended that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [
                    resource for resource in resources if resource.name == match.group(1)
                ]
        zone = params.get("zone")
        if zone:
            resources = [resource for resource in resources if resource.zone == zone]

        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if resources:
            items = {
                scope_key: {
                    "FutureReservations": [
                        resource.to_dict() for resource in resources
                    ]
                }
            }
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#futurereservationAggregatedList",
            "id": f"projects/{project}/aggregated/FutureReservations",
            "items": items,
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified future reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("FutureReservation") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'FutureReservation' not found",
                "INVALID_ARGUMENT",
            )
        future_reservation_name = body.get("name") or params.get(
            "futureReservation"
        )
        if not future_reservation_name:
            return create_gcp_error(
                400,
                "Required field 'futureReservation' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(future_reservation_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )

        resource.reservation_mode = body.get("reservationMode", "")
        resource.creation_timestamp = body.get("creationTimestamp") or (
            resource.creation_timestamp or datetime.now(timezone.utc).isoformat()
        )
        resource.self_link_with_id = body.get("selfLinkWithId", "")
        resource.specific_reservation_required = body.get(
            "specificReservationRequired", False
        )
        resource.aggregate_reservation = body.get("aggregateReservation", {})
        resource.zone = zone
        resource.specific_sku_properties = body.get("specificSkuProperties", {})
        resource.auto_delete_auto_created_reservations = body.get(
            "autoDeleteAutoCreatedReservations", False
        )
        resource.reservation_name = body.get("reservationName", "")
        resource.name_prefix = body.get("namePrefix", "")
        resource.enable_emergent_maintenance = body.get(
            "enableEmergentMaintenance", False
        )
        resource.deployment_type = body.get("deploymentType", "")
        resource.scheduling_type = body.get("schedulingType", "")
        resource.auto_created_reservations_delete_time = body.get(
            "autoCreatedReservationsDeleteTime", ""
        )
        resource.description = body.get("description", "")
        resource.auto_created_reservations_duration = body.get(
            "autoCreatedReservationsDuration", {}
        )
        resource.commitment_info = body.get("commitmentInfo", {})
        resource.time_window = body.get("timeWindow", {})
        resource.name = future_reservation_name
        resource.share_settings = body.get("shareSettings", {})
        resource.status = body.get("status", {})
        resource.planning_status = body.get("planningStatus", "")

        resource_link = (
            f"projects/{project}/zones/{zone}/futureReservations/{resource.name}"
        )
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )

    def cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel the specified future reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not found",
                "INVALID_ARGUMENT",
            )
        future_reservation_name = params.get("futureReservation")
        if not future_reservation_name:
            return create_gcp_error(
                400,
                "Required field 'futureReservation' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(future_reservation_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )

        resource.status = {"state": "CANCELLED"}
        resource.planning_status = "CANCELLED"
        resource_link = (
            f"projects/{project}/zones/{zone}/futureReservations/{future_reservation_name}"
        )
        return make_operation(
            operation_type="cancel",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified future reservation."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not found",
                "INVALID_ARGUMENT",
            )
        future_reservation_name = params.get("futureReservation")
        if not future_reservation_name:
            return create_gcp_error(
                400,
                "Required field 'futureReservation' not found",
                "INVALID_ARGUMENT",
            )

        resource = self.resources.get(future_reservation_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{future_reservation_name}' was not found",
                "NOT_FOUND",
            )

        del self.resources[future_reservation_name]
        resource_link = (
            f"projects/{project}/zones/{zone}/futureReservations/{future_reservation_name}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class future_reservation_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'list': future_reservation_RequestParser._parse_list,
            'delete': future_reservation_RequestParser._parse_delete,
            'get': future_reservation_RequestParser._parse_get,
            'insert': future_reservation_RequestParser._parse_insert,
            'update': future_reservation_RequestParser._parse_update,
            'cancel': future_reservation_RequestParser._parse_cancel,
            'aggregatedList': future_reservation_RequestParser._parse_aggregatedList,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['FutureReservation'] = body.get('FutureReservation')
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
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['FutureReservation'] = body.get('FutureReservation')
        return params

    @staticmethod
    def _parse_cancel(
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
        # Full request body (resource representation)
        params["body"] = body
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


class future_reservation_ResponseSerializer:
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
            'list': future_reservation_ResponseSerializer._serialize_list,
            'delete': future_reservation_ResponseSerializer._serialize_delete,
            'get': future_reservation_ResponseSerializer._serialize_get,
            'insert': future_reservation_ResponseSerializer._serialize_insert,
            'update': future_reservation_ResponseSerializer._serialize_update,
            'cancel': future_reservation_ResponseSerializer._serialize_cancel,
            'aggregatedList': future_reservation_ResponseSerializer._serialize_aggregatedList,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_cancel(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

