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
class InstanceGroupManagerResizeRequest:
    state: str = ""
    resize_by: int = 0
    creation_timestamp: str = ""
    self_link_with_id: str = ""
    zone: str = ""
    status: Dict[str, Any] = field(default_factory=dict)
    requested_run_duration: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    description: str = ""
    id: str = ""

    instance_group_manager: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.state is not None and self.state != "":
            d["state"] = self.state
        if self.resize_by is not None and self.resize_by != 0:
            d["resizeBy"] = self.resize_by
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        d["status"] = self.status
        d["requestedRunDuration"] = self.requested_run_duration
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.id is not None and self.id != "":
            d["id"] = self.id
        if self.instance_group_manager is not None and self.instance_group_manager != "":
            d["instanceGroupManager"] = self.instance_group_manager
        d["kind"] = "compute#instancegroupmanagerresizerequest"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InstanceGroupManagerResizeRequest_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.instance_group_manager_resize_requests  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "instance-group-manager-resize-request") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resize_request(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new resize request that starts provisioning VMs immediately
or queues VM creation."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        body = params.get("InstanceGroupManagerResizeRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field 'zone' not specified", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field 'instanceGroupManager' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'InstanceGroupManagerResizeRequest' not specified",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"ResizeRequest '{name}' already exists", "ALREADY_EXISTS")
        parent = self.state.instance_group_managers.get(instance_group_manager)
        if not parent:
            return create_gcp_error(
                404,
                f"InstanceGroupManager '{instance_group_manager}' not found",
                "NOT_FOUND",
            )
        resource = InstanceGroupManagerResizeRequest(
            state=body.get("state", ""),
            resize_by=body.get("resizeBy", 0) or 0,
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            self_link_with_id=body.get("selfLinkWithId", ""),
            zone=zone,
            status=body.get("status", {}) or {},
            requested_run_duration=body.get("requestedRunDuration", {}) or {},
            name=name,
            description=body.get("description", ""),
            id=self._generate_id(),
            instance_group_manager=instance_group_manager,
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=(
                f"projects/{project}/zones/{zone}/instanceGroupManagers/"
                f"{instance_group_manager}/resizeRequests/{resource.name}"
            ),
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns all of the details about the specified resize request."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        resize_request = params.get("resizeRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field 'zone' not specified", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field 'instanceGroupManager' not specified", "INVALID_ARGUMENT")
        if not resize_request:
            return create_gcp_error(400, "Required field 'resizeRequest' not specified", "INVALID_ARGUMENT")
        parent = self.state.instance_group_managers.get(instance_group_manager)
        if not parent:
            return create_gcp_error(
                404,
                f"InstanceGroupManager '{instance_group_manager}' not found",
                "NOT_FOUND",
            )
        resource = self._get_resize_request(resize_request)
        if is_error_response(resource):
            return resource
        if (resource.zone and resource.zone != zone) or (
            resource.instance_group_manager and resource.instance_group_manager != instance_group_manager
        ):
            return create_gcp_error(
                404,
                f"The resource '{resize_request}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of resize requests that are contained in the
managed instance group."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field 'zone' not specified", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field 'instanceGroupManager' not specified", "INVALID_ARGUMENT")
        parent = self.state.instance_group_managers.get(instance_group_manager)
        if not parent:
            return create_gcp_error(
                404,
                f"InstanceGroupManager '{instance_group_manager}' not found",
                "NOT_FOUND",
            )
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        if zone:
            resources = [r for r in resources if r.zone == zone]
        resources = [
            r for r in resources if r.instance_group_manager == instance_group_manager
        ]
        return {
            "kind": "compute#instancegroupmanagerresizerequestList",
            "id": f"projects/{project}/zones/{zone}/instanceGroupManagers/{instance_group_manager}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancels the specified resize request and removes it from the queue.
Cancelled resize request does no longer wait for the resources to be
provisioned. Cancel is only possible for requests that are a..."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        resize_request = params.get("resizeRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field 'zone' not specified", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field 'instanceGroupManager' not specified", "INVALID_ARGUMENT")
        if not resize_request:
            return create_gcp_error(400, "Required field 'resizeRequest' not specified", "INVALID_ARGUMENT")
        parent = self.state.instance_group_managers.get(instance_group_manager)
        if not parent:
            return create_gcp_error(
                404,
                f"InstanceGroupManager '{instance_group_manager}' not found",
                "NOT_FOUND",
            )
        resource = self._get_resize_request(resize_request)
        if is_error_response(resource):
            return resource
        if (resource.zone and resource.zone != zone) or (
            resource.instance_group_manager and resource.instance_group_manager != instance_group_manager
        ):
            return create_gcp_error(
                404,
                f"The resource '{resize_request}' was not found",
                "NOT_FOUND",
            )
        if resource.state and resource.state.lower() != "accepted":
            return create_gcp_error(
                400,
                "Resize request cannot be canceled in its current state",
                "FAILED_PRECONDITION",
            )
        resource.state = "CANCELLED"
        return make_operation(
            operation_type="cancel",
            resource_link=(
                f"projects/{project}/zones/{zone}/instanceGroupManagers/"
                f"{instance_group_manager}/resizeRequests/{resource.name}"
            ),
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified, inactive resize request. Requests that are still
active cannot be deleted. Deleting request does not delete instances that
were provisioned previously."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        resize_request = params.get("resizeRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field 'zone' not specified", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field 'instanceGroupManager' not specified", "INVALID_ARGUMENT")
        if not resize_request:
            return create_gcp_error(400, "Required field 'resizeRequest' not specified", "INVALID_ARGUMENT")
        parent = self.state.instance_group_managers.get(instance_group_manager)
        if not parent:
            return create_gcp_error(
                404,
                f"InstanceGroupManager '{instance_group_manager}' not found",
                "NOT_FOUND",
            )
        resource = self._get_resize_request(resize_request)
        if is_error_response(resource):
            return resource
        if (resource.zone and resource.zone != zone) or (
            resource.instance_group_manager and resource.instance_group_manager != instance_group_manager
        ):
            return create_gcp_error(
                404,
                f"The resource '{resize_request}' was not found",
                "NOT_FOUND",
            )
        if resource.state and resource.state.lower() == "active":
            return create_gcp_error(
                400,
                "Resize request is active and cannot be deleted",
                "FAILED_PRECONDITION",
            )
        del self.resources[resource.name]
        return make_operation(
            operation_type="delete",
            resource_link=(
                f"projects/{project}/zones/{zone}/instanceGroupManagers/"
                f"{instance_group_manager}/resizeRequests/{resource.name}"
            ),
            params=params,
        )


class instance_group_manager_resize_request_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': instance_group_manager_resize_request_RequestParser._parse_get,
            'list': instance_group_manager_resize_request_RequestParser._parse_list,
            'delete': instance_group_manager_resize_request_RequestParser._parse_delete,
            'cancel': instance_group_manager_resize_request_RequestParser._parse_cancel,
            'insert': instance_group_manager_resize_request_RequestParser._parse_insert,
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
        params['InstanceGroupManagerResizeRequest'] = body.get('InstanceGroupManagerResizeRequest')
        return params


class instance_group_manager_resize_request_ResponseSerializer:
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
            'get': instance_group_manager_resize_request_ResponseSerializer._serialize_get,
            'list': instance_group_manager_resize_request_ResponseSerializer._serialize_list,
            'delete': instance_group_manager_resize_request_ResponseSerializer._serialize_delete,
            'cancel': instance_group_manager_resize_request_ResponseSerializer._serialize_cancel,
            'insert': instance_group_manager_resize_request_ResponseSerializer._serialize_insert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_cancel(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

