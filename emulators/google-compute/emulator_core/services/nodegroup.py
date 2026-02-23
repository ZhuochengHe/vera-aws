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
class NodeGroup:
    description: str = ""
    maintenance_window: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    maintenance_interval: str = ""
    zone: str = ""
    creation_timestamp: str = ""
    size: int = 0
    maintenance_policy: str = ""
    name: str = ""
    location_hint: str = ""
    autoscaling_policy: Dict[str, Any] = field(default_factory=dict)
    share_settings: Dict[str, Any] = field(default_factory=dict)
    fingerprint: str = ""
    node_template: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)
    node_names: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["maintenanceWindow"] = self.maintenance_window
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.maintenance_interval is not None and self.maintenance_interval != "":
            d["maintenanceInterval"] = self.maintenance_interval
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.size is not None and self.size != 0:
            d["size"] = self.size
        if self.maintenance_policy is not None and self.maintenance_policy != "":
            d["maintenancePolicy"] = self.maintenance_policy
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.location_hint is not None and self.location_hint != "":
            d["locationHint"] = self.location_hint
        d["autoscalingPolicy"] = self.autoscaling_policy
        d["shareSettings"] = self.share_settings
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.node_template is not None and self.node_template != "":
            d["nodeTemplate"] = self.node_template
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#nodegroup"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class NodeGroup_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.node_groups  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "node-group") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_node_group_or_error(self, params: Dict[str, Any], name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            project = params.get("project", "")
            zone = params.get("zone", "")
            resource_path = f"projects/{project}/zones/{zone}/nodeGroups/{name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return resource

    def _filter_resources(self, resources: List[NodeGroup], params: Dict[str, Any]) -> List[NodeGroup]:
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
        """Creates a NodeGroup resource in the specified project using the data
included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        zone = params.get("zone")
        if not zone:
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        initial_node_count = params.get("initialNodeCount")
        if initial_node_count is None:
            return create_gcp_error(400, "Required field 'initialNodeCount' is missing", "INVALID_ARGUMENT")
        body = params.get("NodeGroup") or {}
        if not body:
            return create_gcp_error(400, "Required field 'NodeGroup' is missing", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' is missing", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"NodeGroup '{name}' already exists", "ALREADY_EXISTS")
        node_template_ref = body.get("nodeTemplate") or ""
        node_template_name = node_template_ref.split("/")[-1] if node_template_ref else ""
        if node_template_name and not self.state.node_templates.get(node_template_name):
            return create_gcp_error(404, f"NodeTemplate {node_template_name!r} not found", "NOT_FOUND")
        try:
            size = int(initial_node_count)
        except (TypeError, ValueError):
            return create_gcp_error(400, "Required field 'initialNodeCount' is invalid", "INVALID_ARGUMENT")
        node_names = [f"{name}-node-{index + 1}" for index in range(size)]
        resource = NodeGroup(
            description=body.get("description") or "",
            maintenance_window=body.get("maintenanceWindow") or {},
            status=body.get("status") or "",
            maintenance_interval=body.get("maintenanceInterval") or "",
            zone=zone,
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            size=size,
            maintenance_policy=body.get("maintenancePolicy") or "",
            name=name,
            location_hint=body.get("locationHint") or "",
            autoscaling_policy=body.get("autoscalingPolicy") or {},
            share_settings=body.get("shareSettings") or {},
            fingerprint=body.get("fingerprint") or str(uuid.uuid4())[:8],
            node_template=node_template_ref,
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
            node_names=node_names,
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified NodeGroup. Get a list of available NodeGroups
by making a list() request.
Note: the "nodes" field should not be used. Use nodeGroups.listNodes
instead."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of node groups.
Note: use nodeGroups.listNodes for more details about each group.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` paramet..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        resources = self._filter_resources(list(self.resources.values()), params)
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if resources:
            items: Dict[str, Any] = {scope_key: {"NodeGroups": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#nodegroupAggregatedList",
            "id": f"projects/{project}/aggregated/nodeGroups",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of node groups available to the specified project.
Note: use nodeGroups.listNodes for more details about each group."""
        for field_name in ["project", "zone"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        resources = self._filter_resources(list(self.resources.values()), params)
        return {
            "kind": "compute#nodegroupList",
            "id": f"projects/{project}/zones/{zone}/nodeGroups",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified node group."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("NodeGroup") or {}
        if not body:
            return create_gcp_error(400, "Required field 'NodeGroup' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        if "description" in body:
            resource.description = body.get("description") or ""
        if "maintenanceWindow" in body:
            resource.maintenance_window = body.get("maintenanceWindow") or {}
        if "status" in body:
            resource.status = body.get("status") or ""
        if "maintenanceInterval" in body:
            resource.maintenance_interval = body.get("maintenanceInterval") or ""
        if "maintenancePolicy" in body:
            resource.maintenance_policy = body.get("maintenancePolicy") or ""
        if "locationHint" in body:
            resource.location_hint = body.get("locationHint") or ""
        if "autoscalingPolicy" in body:
            resource.autoscaling_policy = body.get("autoscalingPolicy") or {}
        if "shareSettings" in body:
            resource.share_settings = body.get("shareSettings") or {}
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "nodeTemplate" in body:
            node_template_ref = body.get("nodeTemplate") or ""
            node_template_name = node_template_ref.split("/")[-1] if node_template_ref else ""
            if node_template_name and not self.state.node_templates.get(node_template_name):
                return create_gcp_error(404, f"NodeTemplate {node_template_name!r} not found", "NOT_FOUND")
            resource.node_template = node_template_ref
        if "iamPolicy" in body:
            resource.iam_policy = body.get("iamPolicy") or {}
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        for field_name in ["project", "zone", "resource"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("ZoneSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'ZoneSetPolicyRequest' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        resource_name = params.get("resource")
        resource = self._get_node_group_or_error(params, resource_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{resource_name}' was not found",
                "NOT_FOUND",
            )
        resource.iam_policy = body.get("policy") or {}
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def simulateMaintenanceEvent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates maintenance event on specified nodes from the node group."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("NodeGroupsSimulateMaintenanceEventRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NodeGroupsSimulateMaintenanceEventRequest' is missing",
                "INVALID_ARGUMENT",
            )
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        nodes = body.get("nodes") or body.get("nodeNames") or []
        for node in nodes:
            if isinstance(node, dict):
                node_ref = node.get("node") or node.get("name") or ""
            else:
                node_ref = str(node)
            node_name = node_ref.split("/")[-1] if node_ref else ""
            if not node_name:
                return create_gcp_error(400, "Node reference is missing", "INVALID_ARGUMENT")
            if node_name not in resource.node_names:
                return create_gcp_error(404, f"Node {node_name!r} not found", "NOT_FOUND")
        return make_operation(
            operation_type="simulateMaintenanceEvent",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        for field_name in ["project", "zone", "resource"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        resource_name = params.get("resource")
        resource = self._get_node_group_or_error(params, resource_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{resource_name}' was not found",
                "NOT_FOUND",
            )
        return resource.iam_policy or {}

    def setNodeTemplate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the node template of the node group."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("NodeGroupsSetNodeTemplateRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NodeGroupsSetNodeTemplateRequest' is missing",
                "INVALID_ARGUMENT",
            )
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        node_template_ref = body.get("nodeTemplate") or body.get("nodeTemplateId") or ""
        if not node_template_ref:
            return create_gcp_error(400, "Required field 'nodeTemplate' is missing", "INVALID_ARGUMENT")
        node_template_name = node_template_ref.split("/")[-1]
        if node_template_name and not self.state.node_templates.get(node_template_name):
            return create_gcp_error(404, f"NodeTemplate {node_template_name!r} not found", "NOT_FOUND")
        resource.node_template = node_template_ref
        return make_operation(
            operation_type="setNodeTemplate",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def deleteNodes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes specified nodes from the node group."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("NodeGroupsDeleteNodesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NodeGroupsDeleteNodesRequest' is missing",
                "INVALID_ARGUMENT",
            )
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        nodes = body.get("nodes") or body.get("nodeNames") or []
        node_names: List[str] = []
        for node in nodes:
            if isinstance(node, dict):
                node_ref = node.get("node") or node.get("name") or ""
            else:
                node_ref = str(node)
            node_name = node_ref.split("/")[-1] if node_ref else ""
            if not node_name:
                return create_gcp_error(400, "Node reference is missing", "INVALID_ARGUMENT")
            if node_name not in resource.node_names:
                return create_gcp_error(404, f"Node {node_name!r} not found", "NOT_FOUND")
            node_names.append(node_name)
        if node_names:
            resource.node_names = [n for n in resource.node_names if n not in set(node_names)]
            resource.size = len(resource.node_names)
        return make_operation(
            operation_type="deleteNodes",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def performMaintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform maintenance on a subset of nodes in the node group."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("NodeGroupsPerformMaintenanceRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'NodeGroupsPerformMaintenanceRequest' is missing",
                "INVALID_ARGUMENT",
            )
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        nodes = body.get("nodes") or body.get("nodeNames") or []
        for node in nodes:
            if isinstance(node, dict):
                node_ref = node.get("node") or node.get("name") or ""
            else:
                node_ref = str(node)
            node_name = node_ref.split("/")[-1] if node_ref else ""
            if not node_name:
                return create_gcp_error(400, "Node reference is missing", "INVALID_ARGUMENT")
            if node_name not in resource.node_names:
                return create_gcp_error(404, f"Node {node_name!r} not found", "NOT_FOUND")
        return make_operation(
            operation_type="performMaintenance",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        for field_name in ["project", "zone", "resource"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        resource_name = params.get("resource")
        resource = self._get_node_group_or_error(params, resource_name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{resource_name}' was not found",
                "NOT_FOUND",
            )
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def addNodes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds specified number of nodes to the node group."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        body = params.get("NodeGroupsAddNodesRequest") or {}
        if not body:
            return create_gcp_error(400, "Required field 'NodeGroupsAddNodesRequest' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        additional_count = body.get("additionalNodeCount")
        if additional_count is None:
            return create_gcp_error(400, "Required field 'additionalNodeCount' is missing", "INVALID_ARGUMENT")
        try:
            count = int(additional_count)
        except (TypeError, ValueError):
            return create_gcp_error(400, "Required field 'additionalNodeCount' is invalid", "INVALID_ARGUMENT")
        if count < 0:
            return create_gcp_error(400, "Required field 'additionalNodeCount' is invalid", "INVALID_ARGUMENT")
        start_index = len(resource.node_names)
        for index in range(count):
            node_name = f"{resource.name}-node-{start_index + index + 1}"
            resource.node_names.append(node_name)
        resource.size = len(resource.node_names)
        return make_operation(
            operation_type="addNodes",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{resource.name}",
            params=params,
        )

    def listNodes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists nodes in the node group."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        items = []
        for node_name in resource.node_names:
            node_link = (
                f"https://www.googleapis.com/compute/v1/projects/{project}/zones/{zone}/nodeGroups/{resource.name}/nodes/{node_name}"
            )
            items.append({"node": node_link})
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r"(node|name)\s*(eq|ne|=)\s*\"?([^\"\s]+)\"?", filter_expr)
            if match:
                value = match.group(3)
                if match.group(1) == "node":
                    def matches(item: Dict[str, Any]) -> bool:
                        return item.get("node", "").endswith(f"/{value}") or item.get("node") == value
                else:
                    def matches(item: Dict[str, Any]) -> bool:
                        return item.get("node", "").endswith(f"/{value}")
                if match.group(2) == "ne":
                    items = [item for item in items if not matches(item)]
                else:
                    items = [item for item in items if matches(item)]
        return {
            "kind": "compute#nodeGroupsListNodes",
            "id": f"projects/{project}/zones/{zone}/nodeGroups/{resource.name}/listNodes",
            "items": items,
            "selfLink": "",
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified NodeGroup resource."""
        for field_name in ["project", "zone", "nodeGroup"]:
            if not params.get(field_name):
                return create_gcp_error(400, f"Required field '{field_name}' is missing", "INVALID_ARGUMENT")
        project = params.get("project")
        zone = params.get("zone")
        name = params.get("nodeGroup")
        resource = self._get_node_group_or_error(params, name)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/nodeGroups/{name}' was not found",
                "NOT_FOUND",
            )
        if name in self.resources:
            del self.resources[name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/zones/{zone}/NodeGroups/{name}",
            params=params,
        )


class node_group_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'insert': node_group_RequestParser._parse_insert,
            'simulateMaintenanceEvent': node_group_RequestParser._parse_simulateMaintenanceEvent,
            'getIamPolicy': node_group_RequestParser._parse_getIamPolicy,
            'setNodeTemplate': node_group_RequestParser._parse_setNodeTemplate,
            'patch': node_group_RequestParser._parse_patch,
            'aggregatedList': node_group_RequestParser._parse_aggregatedList,
            'deleteNodes': node_group_RequestParser._parse_deleteNodes,
            'setIamPolicy': node_group_RequestParser._parse_setIamPolicy,
            'performMaintenance': node_group_RequestParser._parse_performMaintenance,
            'get': node_group_RequestParser._parse_get,
            'testIamPermissions': node_group_RequestParser._parse_testIamPermissions,
            'addNodes': node_group_RequestParser._parse_addNodes,
            'listNodes': node_group_RequestParser._parse_listNodes,
            'delete': node_group_RequestParser._parse_delete,
            'list': node_group_RequestParser._parse_list,
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
        if 'initialNodeCount' in query_params:
            params['initialNodeCount'] = query_params['initialNodeCount']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['NodeGroup'] = body.get('NodeGroup')
        return params

    @staticmethod
    def _parse_simulateMaintenanceEvent(
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
        params['NodeGroupsSimulateMaintenanceEventRequest'] = body.get('NodeGroupsSimulateMaintenanceEventRequest')
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
    def _parse_setNodeTemplate(
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
        params['NodeGroupsSetNodeTemplateRequest'] = body.get('NodeGroupsSetNodeTemplateRequest')
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
        params['NodeGroup'] = body.get('NodeGroup')
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
    def _parse_deleteNodes(
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
        params['NodeGroupsDeleteNodesRequest'] = body.get('NodeGroupsDeleteNodesRequest')
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
        params['NodeGroupsPerformMaintenanceRequest'] = body.get('NodeGroupsPerformMaintenanceRequest')
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
    def _parse_addNodes(
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
        params['NodeGroupsAddNodesRequest'] = body.get('NodeGroupsAddNodesRequest')
        return params

    @staticmethod
    def _parse_listNodes(
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
        # Full request body (resource representation)
        params["body"] = body
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


class node_group_ResponseSerializer:
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
            'insert': node_group_ResponseSerializer._serialize_insert,
            'simulateMaintenanceEvent': node_group_ResponseSerializer._serialize_simulateMaintenanceEvent,
            'getIamPolicy': node_group_ResponseSerializer._serialize_getIamPolicy,
            'setNodeTemplate': node_group_ResponseSerializer._serialize_setNodeTemplate,
            'patch': node_group_ResponseSerializer._serialize_patch,
            'aggregatedList': node_group_ResponseSerializer._serialize_aggregatedList,
            'deleteNodes': node_group_ResponseSerializer._serialize_deleteNodes,
            'setIamPolicy': node_group_ResponseSerializer._serialize_setIamPolicy,
            'performMaintenance': node_group_ResponseSerializer._serialize_performMaintenance,
            'get': node_group_ResponseSerializer._serialize_get,
            'testIamPermissions': node_group_ResponseSerializer._serialize_testIamPermissions,
            'addNodes': node_group_ResponseSerializer._serialize_addNodes,
            'listNodes': node_group_ResponseSerializer._serialize_listNodes,
            'delete': node_group_ResponseSerializer._serialize_delete,
            'list': node_group_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_simulateMaintenanceEvent(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setNodeTemplate(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_deleteNodes(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_performMaintenance(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addNodes(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listNodes(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

