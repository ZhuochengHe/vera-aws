from __future__ import annotations
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid
import random
import json as _json
import re

from ..utils import (
    create_gcp_error, is_error_response,
    make_operation, parse_labels, get_body_param,
)
from ..state import GCPState

@dataclass
class Autoscaler:
    status_details: List[Any] = field(default_factory=list)
    recommended_size: int = 0
    description: str = ""
    name: str = ""
    creation_timestamp: str = ""
    autoscaling_policy: Dict[str, Any] = field(default_factory=dict)
    target: str = ""
    scaling_schedule_status: Dict[str, Any] = field(default_factory=dict)
    zone: str = ""
    status: str = ""
    region: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["statusDetails"] = self.status_details
        if self.recommended_size is not None and self.recommended_size != 0:
            d["recommendedSize"] = self.recommended_size
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["autoscalingPolicy"] = self.autoscaling_policy
        if self.target is not None and self.target != "":
            d["target"] = self.target
        d["scalingScheduleStatus"] = self.scaling_schedule_status
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#autoscaler"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Autoscaler_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.autoscalers  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "autoscaler") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_autoscaler_or_error(self, autoscaler_name: str) -> Any:
        autoscaler = self.resources.get(autoscaler_name)
        if not autoscaler:
            return create_gcp_error(
                404,
                f"The resource '{autoscaler_name}' was not found",
                "NOT_FOUND",
            )
        return autoscaler

    def _filter_resources(
        self,
        resources: List[Autoscaler],
        params: Dict[str, Any],
    ) -> List[Autoscaler]:
        filter_expr = params.get("filter", "")
        if filter_expr:
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        zone = params.get("zone")
        if zone:
            resources = [r for r in resources if r.zone == zone]
        region = params.get("region")
        if region:
            resources = [r for r in resources if r.region == region]
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an autoscaler in the specified project using the data
included in the request."""
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
        body = params.get("Autoscaler") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Autoscaler' not found",
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
                f"Autoscaler '{name}' already exists",
                "ALREADY_EXISTS",
            )

        resource = Autoscaler(
            status_details=body.get("statusDetails") or [],
            recommended_size=body.get("recommendedSize") or 0,
            description=body.get("description") or "",
            name=name,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            autoscaling_policy=body.get("autoscalingPolicy") or {},
            target=body.get("target") or "",
            scaling_schedule_status=body.get("scalingScheduleStatus") or {},
            zone=zone,
            status=body.get("status") or "",
            region=body.get("region") or "",
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = (
            f"projects/{project}/zones/{zone}/Autoscalers/{resource.name}"
        )
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified autoscaler resource."""
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
        autoscaler_name = params.get("autoscaler")
        if not autoscaler_name:
            return create_gcp_error(
                400,
                "Required field 'autoscaler' not found",
                "INVALID_ARGUMENT",
            )

        autoscaler = self._get_autoscaler_or_error(autoscaler_name)
        if is_error_response(autoscaler):
            return autoscaler
        if autoscaler.zone and autoscaler.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{autoscaler_name}' was not found",
                "NOT_FOUND",
            )
        return autoscaler.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of autoscalers.

To prevent failure, it is recommended that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )

        resources = self._filter_resources(list(self.resources.values()), params)
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        items: Dict[str, Any]
        if resources:
            items = {scope_key: {"Autoscalers": [r.to_dict() for r in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#autoscalerAggregatedList",
            "id": f"projects/{project}/aggregated/Autoscalers",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of autoscalers contained within
the specified zone."""
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

        resources = self._filter_resources(list(self.resources.values()), params)
        return {
            "kind": "compute#autoscalerList",
            "id": f"projects/{project}/zones/{zone}/autoscalers",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an autoscaler in the specified project using the data
included in the request."""
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
        body = params.get("Autoscaler") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Autoscaler' not found",
                "INVALID_ARGUMENT",
            )
        autoscaler_name = body.get("name") or params.get("autoscaler")
        if not autoscaler_name:
            return create_gcp_error(
                400,
                "Required field 'autoscaler' not found",
                "INVALID_ARGUMENT",
            )

        autoscaler = self._get_autoscaler_or_error(autoscaler_name)
        if is_error_response(autoscaler):
            return autoscaler
        if autoscaler.zone and autoscaler.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{autoscaler_name}' was not found",
                "NOT_FOUND",
            )

        autoscaler.status_details = body.get("statusDetails") or []
        autoscaler.recommended_size = body.get("recommendedSize") or 0
        autoscaler.description = body.get("description") or ""
        autoscaler.name = autoscaler_name
        autoscaler.creation_timestamp = body.get("creationTimestamp") or (
            autoscaler.creation_timestamp
            or datetime.now(timezone.utc).isoformat()
        )
        autoscaler.autoscaling_policy = body.get("autoscalingPolicy") or {}
        autoscaler.target = body.get("target") or ""
        autoscaler.scaling_schedule_status = (
            body.get("scalingScheduleStatus") or {}
        )
        autoscaler.zone = zone
        autoscaler.status = body.get("status") or ""
        autoscaler.region = body.get("region") or ""

        resource_link = (
            f"projects/{project}/zones/{zone}/Autoscalers/{autoscaler.name}"
        )
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an autoscaler in the specified project using the data
included in the request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules."""
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
        body = params.get("Autoscaler") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Autoscaler' not found",
                "INVALID_ARGUMENT",
            )
        autoscaler_name = body.get("name") or params.get("autoscaler")
        if not autoscaler_name:
            return create_gcp_error(
                400,
                "Required field 'autoscaler' not found",
                "INVALID_ARGUMENT",
            )

        autoscaler = self._get_autoscaler_or_error(autoscaler_name)
        if is_error_response(autoscaler):
            return autoscaler
        if autoscaler.zone and autoscaler.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{autoscaler_name}' was not found",
                "NOT_FOUND",
            )

        if "statusDetails" in body:
            autoscaler.status_details = body.get("statusDetails") or []
        if "recommendedSize" in body:
            autoscaler.recommended_size = body.get("recommendedSize") or 0
        if "description" in body:
            autoscaler.description = body.get("description") or ""
        if "name" in body:
            autoscaler.name = autoscaler_name
        if "creationTimestamp" in body:
            autoscaler.creation_timestamp = body.get("creationTimestamp")
        if "autoscalingPolicy" in body:
            autoscaler.autoscaling_policy = body.get("autoscalingPolicy") or {}
        if "target" in body:
            autoscaler.target = body.get("target") or ""
        if "scalingScheduleStatus" in body:
            autoscaler.scaling_schedule_status = (
                body.get("scalingScheduleStatus") or {}
            )
        autoscaler.zone = zone
        if "status" in body:
            autoscaler.status = body.get("status") or ""
        if "region" in body:
            autoscaler.region = body.get("region") or ""

        resource_link = (
            f"projects/{project}/zones/{zone}/Autoscalers/{autoscaler.name}"
        )
        return make_operation(
            operation_type="patch",
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
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(
                400,
                "Required field 'zone' not found",
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

        autoscaler = self._get_autoscaler_or_error(resource_name)
        if is_error_response(autoscaler):
            return autoscaler
        if autoscaler.zone and autoscaler.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )

        permissions = body.get("permissions") or []
        return {
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified autoscaler."""
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
        autoscaler_name = params.get("autoscaler")
        if not autoscaler_name:
            return create_gcp_error(
                400,
                "Required field 'autoscaler' not found",
                "INVALID_ARGUMENT",
            )

        autoscaler = self._get_autoscaler_or_error(autoscaler_name)
        if is_error_response(autoscaler):
            return autoscaler
        if autoscaler.zone and autoscaler.zone != zone:
            return create_gcp_error(
                404,
                f"The resource '{autoscaler_name}' was not found",
                "NOT_FOUND",
            )

        del self.resources[autoscaler_name]
        resource_link = (
            f"projects/{project}/zones/{zone}/Autoscalers/{autoscaler_name}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class autoscaler_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': autoscaler_RequestParser._parse_get,
            'testIamPermissions': autoscaler_RequestParser._parse_testIamPermissions,
            'update': autoscaler_RequestParser._parse_update,
            'insert': autoscaler_RequestParser._parse_insert,
            'aggregatedList': autoscaler_RequestParser._parse_aggregatedList,
            'patch': autoscaler_RequestParser._parse_patch,
            'list': autoscaler_RequestParser._parse_list,
            'delete': autoscaler_RequestParser._parse_delete,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        if 'autoscaler' in query_params:
            params['autoscaler'] = query_params['autoscaler']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Autoscaler'] = body.get('Autoscaler')
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
        params['Autoscaler'] = body.get('Autoscaler')
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
    def _parse_patch(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'autoscaler' in query_params:
            params['autoscaler'] = query_params['autoscaler']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Autoscaler'] = body.get('Autoscaler')
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


class autoscaler_ResponseSerializer:
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
            'get': autoscaler_ResponseSerializer._serialize_get,
            'testIamPermissions': autoscaler_ResponseSerializer._serialize_testIamPermissions,
            'update': autoscaler_ResponseSerializer._serialize_update,
            'insert': autoscaler_ResponseSerializer._serialize_insert,
            'aggregatedList': autoscaler_ResponseSerializer._serialize_aggregatedList,
            'patch': autoscaler_ResponseSerializer._serialize_patch,
            'list': autoscaler_ResponseSerializer._serialize_list,
            'delete': autoscaler_ResponseSerializer._serialize_delete,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

