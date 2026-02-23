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
class InstanceGroup:
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

    # Internal dependency tracking — not in API response
    network_name: str = ""  # parent Network name
    subnetwork_name: str = ""  # parent Subnetwork name
    instance_names: List[str] = field(default_factory=list)  # tracks member Instance names


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
        d["kind"] = "compute#instancegroup"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InstanceGroup_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.instance_groups  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "instance-group") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_instance_group_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def _filter_resources(self, resources: List[InstanceGroup], params: Dict[str, Any]) -> List[InstanceGroup]:
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r"name\s*=\s*\"?([^\"\s]+)\"?", filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        zone = params.get("zone")
        if zone:
            resources = [resource for resource in resources if resource.zone == zone]
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an instance group in the specified project using the
parameters that are included in the request."""
        for field_name in ["project", "zone"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("InstanceGroup") or {}
        if not body:
            return create_gcp_error(400, "Required field 'InstanceGroup' is missing", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' is missing", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"InstanceGroup '{name}' already exists", "ALREADY_EXISTS")
        network_ref = body.get("network") or ""
        subnetwork_ref = body.get("subnetwork") or ""
        network_name = network_ref.split("/")[-1] if network_ref else ""
        subnetwork_name = subnetwork_ref.split("/")[-1] if subnetwork_ref else ""
        if network_name and not self.state.networks.get(network_name):
            return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
        if subnetwork_name and not self.state.subnetworks.get(subnetwork_name):
            return create_gcp_error(404, f"Subnetwork {subnetwork_name!r} not found", "NOT_FOUND")
        resource = InstanceGroup(
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            fingerprint=str(uuid.uuid4())[:8],
            description=body.get("description") or "",
            name=name,
            named_ports=body.get("namedPorts") or [],
            subnetwork=subnetwork_ref,
            size=body.get("size") or 0,
            zone=params.get("zone") or "",
            region=body.get("region") or "",
            network=network_ref,
            id=self._generate_id(),
            network_name=network_name,
            subnetwork_name=subnetwork_name,
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{params.get('project')}/zones/{params.get('zone')}/InstanceGroups/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified zonal instance group. Get a list of available zonal
instance groups by making a list() request.

For managed instance groups, use theinstanceGroupManagers
or regionInstanceGro..."""
        for field_name in ["project", "zone", "instanceGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource = self._get_instance_group_or_error(params.get("instanceGroup"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(404, f"The resource '{params.get('instanceGroup')}' was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of zonal instance group resources contained within the
specified zone.

For managed instance groups, use theinstanceGroupManagers
or regionInstanceGroupManagers
methods instead."""
        for field_name in ["project", "zone"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resources = self._filter_resources(list(self.resources.values()), params)
        return {
            "kind": "compute#instancegroupList",
            "id": f"projects/{params.get('project', '')}/zones/{params.get('zone', '')}/instanceGroups",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of instance groups and sorts them by zone.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        resources = self._filter_resources(list(self.resources.values()), params)
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if resources:
            items: Dict[str, Any] = {scope_key: {"InstanceGroups": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#instancegroupAggregatedList",
            "id": f"projects/{params.get('project', '')}/aggregated/instanceGroups",
            "items": items,
            "selfLink": "",
        }

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        for field_name in ["project", "zone", "resource"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        if not params.get("TestPermissionsRequest"):
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' is missing", "INVALID_ARGUMENT")
        resource = self._get_instance_group_or_error(params.get("resource"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(404, f"The resource '{params.get('resource')}' was not found", "NOT_FOUND")
        permissions = params.get("TestPermissionsRequest", {}).get("permissions") or []
        return {"permissions": permissions}

    def addInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds a list of instances to the specified instance group.  All of the
instances in the instance group must be in the same network/subnetwork.
Read 
Adding instances for more information."""
        for field_name in ["project", "zone", "instanceGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("InstanceGroupsAddInstancesRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'InstanceGroupsAddInstancesRequest' is missing", "INVALID_ARGUMENT")
        resource = self._get_instance_group_or_error(params.get("instanceGroup"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(404, f"The resource '{params.get('instanceGroup')}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        for instance_ref in instances:
            instance_name = (instance_ref.get("instance") or "").split("/")[-1]
            if not instance_name:
                return create_gcp_error(400, "Instance reference is missing", "INVALID_ARGUMENT")
            instance = self.state.instances.get(instance_name)
            if not instance:
                return create_gcp_error(404, f"Instance {instance_name!r} not found", "NOT_FOUND")
            if resource.network_name and getattr(instance, "network_name", "") and instance.network_name != resource.network_name:
                return create_gcp_error(400, "Instance network mismatch", "FAILED_PRECONDITION")
            if resource.subnetwork_name and getattr(instance, "subnetwork_name", "") and instance.subnetwork_name != resource.subnetwork_name:
                return create_gcp_error(400, "Instance subnetwork mismatch", "FAILED_PRECONDITION")
            if instance_name not in resource.instance_names:
                resource.instance_names.append(instance_name)
        resource.size = len(resource.instance_names)
        return make_operation(
            operation_type="addInstances",
            resource_link=f"projects/{params.get('project')}/zones/{params.get('zone')}/InstanceGroups/{resource.name}",
            params=params,
        )

    def setNamedPorts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the named ports for the specified instance group."""
        for field_name in ["project", "zone", "instanceGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("InstanceGroupsSetNamedPortsRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'InstanceGroupsSetNamedPortsRequest' is missing", "INVALID_ARGUMENT")
        resource = self._get_instance_group_or_error(params.get("instanceGroup"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(404, f"The resource '{params.get('instanceGroup')}' was not found", "NOT_FOUND")
        resource.named_ports = body.get("namedPorts") or []
        return make_operation(
            operation_type="setNamedPorts",
            resource_link=f"projects/{params.get('project')}/zones/{params.get('zone')}/InstanceGroups/{resource.name}",
            params=params,
        )

    def listInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the instances in the specified instance group.
The orderBy query parameter is not supported.
The filter query parameter is supported, but only for
expressions that use `eq` (equal) or `ne` (n..."""
        for field_name in ["project", "zone", "instanceGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("InstanceGroupsListInstancesRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'InstanceGroupsListInstancesRequest' is missing", "INVALID_ARGUMENT")
        resource = self._get_instance_group_or_error(params.get("instanceGroup"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(404, f"The resource '{params.get('instanceGroup')}' was not found", "NOT_FOUND")
        items: List[Dict[str, Any]] = []
        project = params.get("project")
        zone = params.get("zone")
        for instance_name in resource.instance_names:
            instance = self.state.instances.get(instance_name)
            if not instance:
                continue
            instance_zone = getattr(instance, "zone", zone) or zone
            instance_link = (
                f"https://www.googleapis.com/compute/v1/projects/{project}/zones/{instance_zone}/instances/{instance_name}"
            )
            items.append({"instance": instance_link})
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r"(instance|name)\s*(eq|ne|=)\s*\"?([^\"\s]+)\"?", filter_expr)
            if match:
                value = match.group(3)
                if match.group(1) == "instance":
                    def matches(item: Dict[str, Any]) -> bool:
                        return item.get("instance", "").endswith(f"/{value}") or item.get("instance") == value
                else:
                    def matches(item: Dict[str, Any]) -> bool:
                        return item.get("instance", "").endswith(f"/{value}")
                if match.group(2) in ["ne"]:
                    items = [item for item in items if not matches(item)]
                else:
                    items = [item for item in items if matches(item)]
        return {
            "kind": "compute#instanceGroupsListInstances",
            "id": f"projects/{project}/zones/{zone}/instanceGroups/{resource.name}/listInstances",
            "items": items,
            "selfLink": "",
        }

    def removeInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes one or more instances from the specified instance group, but does
not delete those instances.

If the group is part of a backend
service that has enabled
connection draining, it can take up..."""
        for field_name in ["project", "zone", "instanceGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("InstanceGroupsRemoveInstancesRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'InstanceGroupsRemoveInstancesRequest' is missing", "INVALID_ARGUMENT")
        resource = self._get_instance_group_or_error(params.get("instanceGroup"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(404, f"The resource '{params.get('instanceGroup')}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        for instance_ref in instances:
            instance_name = (instance_ref.get("instance") or "").split("/")[-1]
            if not instance_name:
                return create_gcp_error(400, "Instance reference is missing", "INVALID_ARGUMENT")
            if not self.state.instances.get(instance_name):
                return create_gcp_error(404, f"Instance {instance_name!r} not found", "NOT_FOUND")
            if instance_name not in resource.instance_names:
                return create_gcp_error(400, "Instance not in instance group", "FAILED_PRECONDITION")
            resource.instance_names.remove(instance_name)
        resource.size = len(resource.instance_names)
        return make_operation(
            operation_type="removeInstances",
            resource_link=f"projects/{params.get('project')}/zones/{params.get('zone')}/InstanceGroups/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified instance group. The instances in the group are not
deleted. Note that instance group must not belong to a backend service.
Read
Deleting an instance group for more information."""
        for field_name in ["project", "zone", "instanceGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        resource = self._get_instance_group_or_error(params.get("instanceGroup"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(404, f"The resource '{params.get('instanceGroup')}' was not found", "NOT_FOUND")
        if resource.instance_names:
            return create_gcp_error(400, "Instance group still has instances", "FAILED_PRECONDITION")
        del self.resources[resource.name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{params.get('project')}/zones/{params.get('zone')}/InstanceGroups/{resource.name}",
            params=params,
        )


class instance_group_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'testIamPermissions': instance_group_RequestParser._parse_testIamPermissions,
            'addInstances': instance_group_RequestParser._parse_addInstances,
            'delete': instance_group_RequestParser._parse_delete,
            'list': instance_group_RequestParser._parse_list,
            'get': instance_group_RequestParser._parse_get,
            'aggregatedList': instance_group_RequestParser._parse_aggregatedList,
            'setNamedPorts': instance_group_RequestParser._parse_setNamedPorts,
            'listInstances': instance_group_RequestParser._parse_listInstances,
            'removeInstances': instance_group_RequestParser._parse_removeInstances,
            'insert': instance_group_RequestParser._parse_insert,
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
    def _parse_addInstances(
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
        params['InstanceGroupsAddInstancesRequest'] = body.get('InstanceGroupsAddInstancesRequest')
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
        params['InstanceGroupsSetNamedPortsRequest'] = body.get('InstanceGroupsSetNamedPortsRequest')
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
        params['InstanceGroupsListInstancesRequest'] = body.get('InstanceGroupsListInstancesRequest')
        return params

    @staticmethod
    def _parse_removeInstances(
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
        params['InstanceGroupsRemoveInstancesRequest'] = body.get('InstanceGroupsRemoveInstancesRequest')
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
        params['InstanceGroup'] = body.get('InstanceGroup')
        return params


class instance_group_ResponseSerializer:
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
            'testIamPermissions': instance_group_ResponseSerializer._serialize_testIamPermissions,
            'addInstances': instance_group_ResponseSerializer._serialize_addInstances,
            'delete': instance_group_ResponseSerializer._serialize_delete,
            'list': instance_group_ResponseSerializer._serialize_list,
            'get': instance_group_ResponseSerializer._serialize_get,
            'aggregatedList': instance_group_ResponseSerializer._serialize_aggregatedList,
            'setNamedPorts': instance_group_ResponseSerializer._serialize_setNamedPorts,
            'listInstances': instance_group_ResponseSerializer._serialize_listInstances,
            'removeInstances': instance_group_ResponseSerializer._serialize_removeInstances,
            'insert': instance_group_ResponseSerializer._serialize_insert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setNamedPorts(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

