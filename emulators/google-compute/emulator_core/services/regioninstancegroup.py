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
class RegionInstanceGroup:
    creation_timestamp: str = ""
    fingerprint: str = ""
    description: str = ""
    name: str = ""
    named_ports: List[Any] = field(default_factory=list)
    subnetwork: str = ""
    size: int = 0
    zone: str = ""
    region: str = ""
    network: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["namedPorts"] = self.named_ports
        if self.subnetwork is not None and self.subnetwork != "":
            d["subnetwork"] = self.subnetwork
        if self.size is not None and self.size != 0:
            d["size"] = self.size
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regioninstancegroup"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionInstanceGroup_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_instance_groups  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-instance-group") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(
        self,
        resource_name: Optional[str],
        field_name: str,
    ) -> Dict[str, Any] | RegionInstanceGroup:
        if not resource_name:
            return create_gcp_error(
                400,
                f"Required field '{field_name}' missing",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(resource_name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified instance group resource."""
        project = params.get("project")
        region = params.get("region")
        instance_group = params.get("instanceGroup")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' missing",
                "INVALID_ARGUMENT",
            )
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group, "instanceGroup")
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{instance_group}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of instance group resources contained within
the specified region."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' missing",
                "INVALID_ARGUMENT",
            )
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' missing",
                "INVALID_ARGUMENT",
            )
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            m = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if m:
                resources = [r for r in resources if r.name == m.group(1)]
        if resources:
            resources = [r for r in resources if r.region == region]
        else:
            resources = []
        return {
            "kind": "compute#regioninstancegroupList",
            "id": f"projects/{project}/regions/{region}/instanceGroups",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        region = params.get("region")
        resource_name = params.get("resource")
        permissions_request = params.get("TestPermissionsRequest")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' missing",
                "INVALID_ARGUMENT",
            )
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' missing",
                "INVALID_ARGUMENT",
            )
        if permissions_request is None:
            return create_gcp_error(
                400,
                "Required field 'TestPermissionsRequest' missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(resource_name, "resource")
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{resource_name}' was not found",
                "NOT_FOUND",
            )
        permissions = permissions_request.get("permissions", [])
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }

    def setNamedPorts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the named ports for the specified regional instance group."""
        project = params.get("project")
        region = params.get("region")
        instance_group = params.get("instanceGroup")
        request = params.get("RegionInstanceGroupsSetNamedPortsRequest")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' missing",
                "INVALID_ARGUMENT",
            )
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' missing",
                "INVALID_ARGUMENT",
            )
        if request is None:
            return create_gcp_error(
                400,
                "Required field 'RegionInstanceGroupsSetNamedPortsRequest' missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group, "instanceGroup")
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{instance_group}' was not found",
                "NOT_FOUND",
            )
        resource.named_ports = request.get("namedPorts", [])
        return make_operation(
            operation_type="setNamedPorts",
            resource_link=f"projects/{project}/regions/{region}/instanceGroups/{resource.name}",
            params=params,
        )

    def listInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the instances in the specified instance group and displays
information about the named ports. Depending on the specified options, this
method can list all instances or only the instances that..."""
        project = params.get("project")
        region = params.get("region")
        instance_group = params.get("instanceGroup")
        request = params.get("RegionInstanceGroupsListInstancesRequest")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' missing",
                "INVALID_ARGUMENT",
            )
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' missing",
                "INVALID_ARGUMENT",
            )
        if request is None:
            return create_gcp_error(
                400,
                "Required field 'RegionInstanceGroupsListInstancesRequest' missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group, "instanceGroup")
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource '{instance_group}' was not found",
                "NOT_FOUND",
            )
        return {
            "kind": "compute#regionInstanceGroupsListInstances",
            "id": (
                f"projects/{project}/regions/{region}/instanceGroups/"
                f"{resource.name}/listInstances"
            ),
            "items": [],
            "selfLink": "",
        }


class region_instance_group_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'testIamPermissions': region_instance_group_RequestParser._parse_testIamPermissions,
            'setNamedPorts': region_instance_group_RequestParser._parse_setNamedPorts,
            'list': region_instance_group_RequestParser._parse_list,
            'get': region_instance_group_RequestParser._parse_get,
            'listInstances': region_instance_group_RequestParser._parse_listInstances,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
    def _parse_setNamedPorts(
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
        params['RegionInstanceGroupsSetNamedPortsRequest'] = body.get('RegionInstanceGroupsSetNamedPortsRequest')
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
    def _parse_listInstances(
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
        # Body params
        params['RegionInstanceGroupsListInstancesRequest'] = body.get('RegionInstanceGroupsListInstancesRequest')
        return params


class region_instance_group_ResponseSerializer:
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
            'testIamPermissions': region_instance_group_ResponseSerializer._serialize_testIamPermissions,
            'setNamedPorts': region_instance_group_ResponseSerializer._serialize_setNamedPorts,
            'list': region_instance_group_ResponseSerializer._serialize_list,
            'get': region_instance_group_ResponseSerializer._serialize_get,
            'listInstances': region_instance_group_ResponseSerializer._serialize_listInstances,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setNamedPorts(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

