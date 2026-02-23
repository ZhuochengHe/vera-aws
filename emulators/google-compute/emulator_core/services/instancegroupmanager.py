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
class InstanceGroupManager:
    all_instances_config: Dict[str, Any] = field(default_factory=dict)
    target_size: int = 0
    instance_lifecycle_policy: Dict[str, Any] = field(default_factory=dict)
    satisfies_pzs: bool = False
    region: str = ""
    current_actions: Dict[str, Any] = field(default_factory=dict)
    instance_template: str = ""
    zone: str = ""
    target_suspended_size: int = 0
    instance_flexibility_policy: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    instance_group: str = ""
    name: str = ""
    description: str = ""
    update_policy: Dict[str, Any] = field(default_factory=dict)
    target_stopped_size: int = 0
    versions: List[Any] = field(default_factory=list)
    status: Dict[str, Any] = field(default_factory=dict)
    satisfies_pzi: bool = False
    distribution_policy: Dict[str, Any] = field(default_factory=dict)
    list_managed_instances_results: str = ""
    named_ports: List[Any] = field(default_factory=list)
    stateful_policy: Dict[str, Any] = field(default_factory=dict)
    resource_policies: Dict[str, Any] = field(default_factory=dict)
    standby_policy: Dict[str, Any] = field(default_factory=dict)
    base_instance_name: str = ""
    fingerprint: str = ""
    auto_healing_policies: List[Any] = field(default_factory=list)
    target_pools: List[Any] = field(default_factory=list)
    id: str = ""

    # Internal dependency tracking — not in API response
    instance_group_name: str = ""  # managed InstanceGroup name

    per_instance_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    managed_instances: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    instance_errors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["allInstancesConfig"] = self.all_instances_config
        if self.target_size is not None and self.target_size != 0:
            d["targetSize"] = self.target_size
        d["instanceLifecyclePolicy"] = self.instance_lifecycle_policy
        d["satisfiesPzs"] = self.satisfies_pzs
        if self.region is not None and self.region != "":
            d["region"] = self.region
        d["currentActions"] = self.current_actions
        if self.instance_template is not None and self.instance_template != "":
            d["instanceTemplate"] = self.instance_template
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.target_suspended_size is not None and self.target_suspended_size != 0:
            d["targetSuspendedSize"] = self.target_suspended_size
        d["instanceFlexibilityPolicy"] = self.instance_flexibility_policy
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.instance_group is not None and self.instance_group != "":
            d["instanceGroup"] = self.instance_group
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["updatePolicy"] = self.update_policy
        if self.target_stopped_size is not None and self.target_stopped_size != 0:
            d["targetStoppedSize"] = self.target_stopped_size
        d["versions"] = self.versions
        d["status"] = self.status
        d["satisfiesPzi"] = self.satisfies_pzi
        d["distributionPolicy"] = self.distribution_policy
        if self.list_managed_instances_results is not None and self.list_managed_instances_results != "":
            d["listManagedInstancesResults"] = self.list_managed_instances_results
        d["namedPorts"] = self.named_ports
        d["statefulPolicy"] = self.stateful_policy
        d["resourcePolicies"] = self.resource_policies
        d["standbyPolicy"] = self.standby_policy
        if self.base_instance_name is not None and self.base_instance_name != "":
            d["baseInstanceName"] = self.base_instance_name
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        d["autoHealingPolicies"] = self.auto_healing_policies
        d["targetPools"] = self.target_pools
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#instancegroupmanager"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InstanceGroupManager_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.instance_group_managers  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "instance-group-manager") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def _filter_resources(
        self,
        params: Dict[str, Any],
        resources: List[InstanceGroupManager],
    ) -> List[InstanceGroupManager]:
        filter_expr = params.get("filter", "")
        if filter_expr:
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        zone = params.get("zone")
        region = params.get("region")
        if zone:
            resources = [r for r in resources if r.zone == zone]
        if region:
            resources = [r for r in resources if r.region == region]
        return resources

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a managed instance group using the information that you specify
in the request. After the group is created, instances in the group are
created using the specified instance template.
This op..."""
        body = params.get("InstanceGroupManager") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field InstanceGroupManager is missing", "INVALID_ARGUMENT")
        name = body.get("name") or params.get("name")
        if not name:
            return create_gcp_error(400, "Required field name is missing", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(400, f"InstanceGroupManager '{name}' already exists", "INVALID_ARGUMENT")
        instance_group = body.get("instanceGroup") or ""
        if instance_group:
            instance_group_name = instance_group.split("/")[-1]
            if not self.state.instance_groups.get(instance_group_name):
                return create_gcp_error(404, f"InstanceGroup {instance_group_name!r} not found", "NOT_FOUND")
        resource = InstanceGroupManager(
            all_instances_config=body.get("allInstancesConfig", {}),
            target_size=body.get("targetSize", 0),
            instance_lifecycle_policy=body.get("instanceLifecyclePolicy", {}),
            satisfies_pzs=body.get("satisfiesPzs", False),
            region=body.get("region", ""),
            current_actions=body.get("currentActions", {}),
            instance_template=body.get("instanceTemplate", ""),
            zone=zone,
            target_suspended_size=body.get("targetSuspendedSize", 0),
            instance_flexibility_policy=body.get("instanceFlexibilityPolicy", {}),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            instance_group=instance_group,
            name=name,
            description=body.get("description", ""),
            update_policy=body.get("updatePolicy", {}),
            target_stopped_size=body.get("targetStoppedSize", 0),
            versions=body.get("versions", []),
            status=body.get("status", {}),
            satisfies_pzi=body.get("satisfiesPzi", False),
            distribution_policy=body.get("distributionPolicy", {}),
            list_managed_instances_results=body.get("listManagedInstancesResults", ""),
            named_ports=body.get("namedPorts", []),
            stateful_policy=body.get("statefulPolicy", {}),
            resource_policies=body.get("resourcePolicies", {}),
            standby_policy=body.get("standbyPolicy", {}),
            base_instance_name=body.get("baseInstanceName", ""),
            fingerprint=body.get("fingerprint", ""),
            auto_healing_policies=body.get("autoHealingPolicies", []),
            target_pools=body.get("targetPools", []),
            id=self._generate_id(),
            instance_group_name=instance_group.split("/")[-1] if instance_group else "",
        )
        self.resources[name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns all of the details about the specified managed instance group."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of managed instance groups that are contained within the
specified project and zone."""
        project = params.get("project")
        zone = params.get("zone")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        resources = self._filter_resources(params, list(self.resources.values()))
        return {
            "kind": "compute#instancegroupmanagerList",
            "id": f"projects/{project}/zones/{zone}/instanceGroupManagers",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def listManagedInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all of the instances in the managed instance group. Each instance
in the list has a currentAction, which indicates the action
that the managed instance group is performing on the instance. Fo..."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = list(resource.managed_instances.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                name_value = match.group(1)
                instances = [
                    instance
                    for instance in instances
                    if instance.get("name") == name_value
                    or instance.get("instance", "").split("/")[-1] == name_value
                ]
        return {
            "kind": "compute#instancegroupmanagerList",
            "id": f"projects/{project}/zones/{zone}/instanceGroupManagers/{instance_group_manager}",
            "items": instances,
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of managed instance groups and groups them by zone.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        resources = self._filter_resources(params, list(self.resources.values()))
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if not resources:
            items: Dict[str, Any] = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items = {scope_key: {"InstanceGroupManagers": [r.to_dict() for r in resources]}}
        return {
            "kind": "compute#instancegroupmanagerAggregatedList",
            "id": f"projects/{project}/aggregated/InstanceGroupManagers",
            "items": items,
            "selfLink": "",
        }

    def listPerInstanceConfigs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all of the per-instance configurations defined for the managed
instance group. The orderBy query parameter is not supported."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        configs = list(resource.per_instance_configs.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                name_value = match.group(1)
                configs = [config for config in configs if config.get("name") == name_value]
        return {
            "kind": "compute#instancegroupmanagerList",
            "id": f"projects/{project}/zones/{zone}/instanceGroupManagers/{instance_group_manager}",
            "items": configs,
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a managed instance group using the information that you specify
in the request.
This operation is marked as DONE when the group is patched
even if the instances in the group are still in th..."""
        body = params.get("InstanceGroupManager") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field InstanceGroupManager is missing", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instance_group = body.get("instanceGroup")
        if instance_group:
            instance_group_name = instance_group.split("/")[-1]
            if not self.state.instance_groups.get(instance_group_name):
                return create_gcp_error(404, f"InstanceGroup {instance_group_name!r} not found", "NOT_FOUND")
            resource.instance_group = instance_group
            resource.instance_group_name = instance_group_name
        if "allInstancesConfig" in body:
            resource.all_instances_config = body.get("allInstancesConfig") or {}
        if "targetSize" in body:
            resource.target_size = body.get("targetSize")
        if "instanceLifecyclePolicy" in body:
            resource.instance_lifecycle_policy = body.get("instanceLifecyclePolicy") or {}
        if "satisfiesPzs" in body:
            resource.satisfies_pzs = body.get("satisfiesPzs", False)
        if "region" in body:
            resource.region = body.get("region", "")
        if "currentActions" in body:
            resource.current_actions = body.get("currentActions") or {}
        if "instanceTemplate" in body:
            resource.instance_template = body.get("instanceTemplate", "")
        if "targetSuspendedSize" in body:
            resource.target_suspended_size = body.get("targetSuspendedSize")
        if "instanceFlexibilityPolicy" in body:
            resource.instance_flexibility_policy = body.get("instanceFlexibilityPolicy") or {}
        if "description" in body:
            resource.description = body.get("description", "")
        if "updatePolicy" in body:
            resource.update_policy = body.get("updatePolicy") or {}
        if "targetStoppedSize" in body:
            resource.target_stopped_size = body.get("targetStoppedSize")
        if "versions" in body:
            resource.versions = body.get("versions") or []
        if "status" in body:
            resource.status = body.get("status") or {}
        if "satisfiesPzi" in body:
            resource.satisfies_pzi = body.get("satisfiesPzi", False)
        if "distributionPolicy" in body:
            resource.distribution_policy = body.get("distributionPolicy") or {}
        if "listManagedInstancesResults" in body:
            resource.list_managed_instances_results = body.get("listManagedInstancesResults", "")
        if "namedPorts" in body:
            resource.named_ports = body.get("namedPorts") or []
        if "statefulPolicy" in body:
            resource.stateful_policy = body.get("statefulPolicy") or {}
        if "resourcePolicies" in body:
            resource.resource_policies = body.get("resourcePolicies") or {}
        if "standbyPolicy" in body:
            resource.standby_policy = body.get("standbyPolicy") or {}
        if "baseInstanceName" in body:
            resource.base_instance_name = body.get("baseInstanceName", "")
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint", "")
        if "autoHealingPolicies" in body:
            resource.auto_healing_policies = body.get("autoHealingPolicies") or []
        if "targetPools" in body:
            resource.target_pools = body.get("targetPools") or []
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def deletePerInstanceConfigs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes selected per-instance configurations for the managed instance
group."""
        body = params.get("InstanceGroupManagersDeletePerInstanceConfigsReq") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersDeletePerInstanceConfigsReq is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        names = body.get("names") or []
        if not names:
            return create_gcp_error(400, "Required field names is missing", "INVALID_ARGUMENT")
        for name in names:
            resource.per_instance_configs.pop(name, None)
        return make_operation(
            operation_type="deletePerInstanceConfigs",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def resumeInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flags the specified instances in the managed instance group to be
resumed. This method increases thetargetSize and decreases the targetSuspendedSize
of the managed instance group by the number of i..."""
        body = params.get("InstanceGroupManagersResumeInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersResumeInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            details = resource.managed_instances.get(instance_name) or {"instance": instance}
            details["currentAction"] = "RESUMING"
            resource.managed_instances[instance_name] = details
        resource.target_size += len(instances)
        resource.target_suspended_size = max(0, resource.target_suspended_size - len(instances))
        return make_operation(
            operation_type="resumeInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def suspendInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flags the specified instances in the managed instance group to be
immediately suspended. You can only specify instances that are running in
this request. This method reduces thetargetSize and incre..."""
        body = params.get("InstanceGroupManagersSuspendInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersSuspendInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            details = resource.managed_instances.get(instance_name) or {"instance": instance}
            details["currentAction"] = "SUSPENDING"
            resource.managed_instances[instance_name] = details
        resource.target_size = max(0, resource.target_size - len(instances))
        resource.target_suspended_size += len(instances)
        return make_operation(
            operation_type="suspendInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def patchPerInstanceConfigs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inserts or patches per-instance configurations for the managed instance
group. perInstanceConfig.name serves as a key used to
distinguish whether to perform insert or patch."""
        body = params.get("InstanceGroupManagersPatchPerInstanceConfigsReq") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersPatchPerInstanceConfigsReq is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        configs = body.get("perInstanceConfigs") or []
        if not configs:
            return create_gcp_error(400, "Required field perInstanceConfigs is missing", "INVALID_ARGUMENT")
        for config in configs:
            name = config.get("name")
            if not name:
                return create_gcp_error(400, "Required field perInstanceConfigs.name is missing", "INVALID_ARGUMENT")
            existing = resource.per_instance_configs.get(name, {})
            merged = {**existing, **config}
            resource.per_instance_configs[name] = merged
        return make_operation(
            operation_type="patchPerInstanceConfigs",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def stopInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flags the specified instances in the managed instance group to be
immediately stopped. You can only specify instances that are running in
this request. This method reduces thetargetSize and increas..."""
        body = params.get("InstanceGroupManagersStopInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersStopInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            details = resource.managed_instances.get(instance_name) or {"instance": instance}
            details["currentAction"] = "STOPPING"
            resource.managed_instances[instance_name] = details
        resource.target_size = max(0, resource.target_size - len(instances))
        resource.target_stopped_size += len(instances)
        return make_operation(
            operation_type="stopInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def recreateInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flags the specified VM instances in the managed instance group to be
immediately recreated. Each instance is recreated using the group's current
configuration. This operation is marked as DONE when..."""
        body = params.get("InstanceGroupManagersRecreateInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersRecreateInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            details = resource.managed_instances.get(instance_name) or {"instance": instance}
            details["currentAction"] = "RECREATING"
            resource.managed_instances[instance_name] = details
        return make_operation(
            operation_type="recreateInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def setInstanceTemplate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Specifies the instance template to use when creating new instances in this
group. The templates for existing instances in the group do not change
unless you run recreateInstances, runapplyUpdatesTo..."""
        body = params.get("InstanceGroupManagersSetInstanceTemplateRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersSetInstanceTemplateRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instance_template = body.get("instanceTemplate")
        if not instance_template:
            return create_gcp_error(400, "Required field instanceTemplate is missing", "INVALID_ARGUMENT")
        resource.instance_template = instance_template
        return make_operation(
            operation_type="setInstanceTemplate",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def setTargetPools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modifies the target pools to which all instances in this managed instance
group are assigned. The target pools automatically apply to all of the
instances in the managed instance group. This operat..."""
        body = params.get("InstanceGroupManagersSetTargetPoolsRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersSetTargetPoolsRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        target_pools = body.get("targetPools") or []
        resource.target_pools = target_pools
        return make_operation(
            operation_type="setTargetPools",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def createInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates instances with per-instance configurations in this managed instance
group. Instances are created using the current instance template. Thecreate instances operation is marked DONE if thecrea..."""
        body = params.get("InstanceGroupManagersCreateInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersCreateInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            name = instance.get("name") if isinstance(instance, dict) else None
            if not name:
                return create_gcp_error(400, "Required field instances.name is missing", "INVALID_ARGUMENT")
            resource.managed_instances[name] = {
                "instance": name,
                "name": name,
                "currentAction": "CREATING",
            }
            if name in resource.per_instance_configs:
                resource.per_instance_configs[name].update(instance)
            else:
                resource.per_instance_configs[name] = dict(instance)
        resource.target_size += len(instances)
        return make_operation(
            operation_type="createInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def listErrors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all errors thrown by actions on instances for a given managed
instance group. The filter and orderBy query
parameters are not supported."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        return {
            "kind": "compute#instancegroupmanagerList",
            "id": f"projects/{project}/zones/{zone}/instanceGroupManagers/{instance_group_manager}/listErrors",
            "items": list(resource.instance_errors),
            "selfLink": "",
        }

    def updatePerInstanceConfigs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inserts or updates per-instance configurations for the managed instance
group. perInstanceConfig.name serves as a key used to
distinguish whether to perform insert or patch."""
        body = params.get("InstanceGroupManagersUpdatePerInstanceConfigsReq") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersUpdatePerInstanceConfigsReq is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        configs = body.get("perInstanceConfigs") or []
        if not configs:
            return create_gcp_error(400, "Required field perInstanceConfigs is missing", "INVALID_ARGUMENT")
        for config in configs:
            name = config.get("name")
            if not name:
                return create_gcp_error(400, "Required field perInstanceConfigs.name is missing", "INVALID_ARGUMENT")
            resource.per_instance_configs[name] = dict(config)
        return make_operation(
            operation_type="updatePerInstanceConfigs",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def applyUpdatesToInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Applies changes to selected instances on the managed instance group.
This method can be used to apply new overrides and/or new versions."""
        body = params.get("InstanceGroupManagersApplyUpdatesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersApplyUpdatesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            details = resource.managed_instances.get(instance_name) or {"instance": instance}
            details["currentAction"] = "APPLYING_UPDATES"
            resource.managed_instances[instance_name] = details
        return make_operation(
            operation_type="applyUpdatesToInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def abandonInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flags the specified instances to be removed from the
managed instance group. Abandoning an instance does not delete the
instance, but it does remove the instance from any target pools that are
appl..."""
        body = params.get("InstanceGroupManagersAbandonInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersAbandonInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            resource.managed_instances.pop(instance_name, None)
        resource.target_size = max(0, resource.target_size - len(instances))
        return make_operation(
            operation_type="abandonInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def resize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resizes the managed instance group. If you increase the size, the group
creates new instances using the current instance template. If you decrease
the size, the group deletes instances. The resize ..."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        size = params.get("size")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if size is None:
            return create_gcp_error(400, "Required field size is missing", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        try:
            new_size = int(size)
        except (TypeError, ValueError):
            return create_gcp_error(400, "Invalid value for size", "INVALID_ARGUMENT")
        resource.target_size = max(0, new_size)
        return make_operation(
            operation_type="resize",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def startInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flags the specified instances in the managed instance group to be
started. This method increases thetargetSize and decreases the targetStoppedSize
of the managed instance group by the number of ins..."""
        body = params.get("InstanceGroupManagersStartInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersStartInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            details = resource.managed_instances.get(instance_name) or {"instance": instance}
            details["currentAction"] = "STARTING"
            resource.managed_instances[instance_name] = details
        resource.target_size += len(instances)
        resource.target_stopped_size = max(0, resource.target_stopped_size - len(instances))
        return make_operation(
            operation_type="startInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def deleteInstances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flags the specified instances in the managed instance group for immediate
deletion. The instances are also removed from any target
pools of which they were a member. This method reduces thetargetSi..."""
        body = params.get("InstanceGroupManagersDeleteInstancesRequest") or params.get("body") or {}
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(
                400,
                "Required field InstanceGroupManagersDeleteInstancesRequest is missing",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        instances = body.get("instances") or []
        if not instances:
            return create_gcp_error(400, "Required field instances is missing", "INVALID_ARGUMENT")
        for instance in instances:
            instance_name = instance.split("/")[-1]
            resource.managed_instances.pop(instance_name, None)
            resource.per_instance_configs.pop(instance_name, None)
        resource.target_size = max(0, resource.target_size - len(instances))
        return make_operation(
            operation_type="deleteInstances",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified managed instance group and all of the instances
in that group. Note that the instance group must not belong to a
backend service. Read
Deleting an instance group for more info..."""
        project = params.get("project")
        zone = params.get("zone")
        instance_group_manager = params.get("instanceGroupManager")
        if not project:
            return create_gcp_error(400, "Required field project is missing", "INVALID_ARGUMENT")
        if not zone:
            return create_gcp_error(400, "Required field zone is missing", "INVALID_ARGUMENT")
        if not instance_group_manager:
            return create_gcp_error(400, "Required field instanceGroupManager is missing", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(instance_group_manager)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            return create_gcp_error(404, f"The resource '{instance_group_manager}' was not found", "NOT_FOUND")
        self.resources.pop(instance_group_manager, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/zones/{zone}/InstanceGroupManagers/{instance_group_manager}",
            params=params,
        )


class instance_group_manager_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'deletePerInstanceConfigs': instance_group_manager_RequestParser._parse_deletePerInstanceConfigs,
            'resumeInstances': instance_group_manager_RequestParser._parse_resumeInstances,
            'patch': instance_group_manager_RequestParser._parse_patch,
            'suspendInstances': instance_group_manager_RequestParser._parse_suspendInstances,
            'patchPerInstanceConfigs': instance_group_manager_RequestParser._parse_patchPerInstanceConfigs,
            'stopInstances': instance_group_manager_RequestParser._parse_stopInstances,
            'recreateInstances': instance_group_manager_RequestParser._parse_recreateInstances,
            'list': instance_group_manager_RequestParser._parse_list,
            'setInstanceTemplate': instance_group_manager_RequestParser._parse_setInstanceTemplate,
            'setTargetPools': instance_group_manager_RequestParser._parse_setTargetPools,
            'listManagedInstances': instance_group_manager_RequestParser._parse_listManagedInstances,
            'createInstances': instance_group_manager_RequestParser._parse_createInstances,
            'listErrors': instance_group_manager_RequestParser._parse_listErrors,
            'aggregatedList': instance_group_manager_RequestParser._parse_aggregatedList,
            'get': instance_group_manager_RequestParser._parse_get,
            'updatePerInstanceConfigs': instance_group_manager_RequestParser._parse_updatePerInstanceConfigs,
            'applyUpdatesToInstances': instance_group_manager_RequestParser._parse_applyUpdatesToInstances,
            'abandonInstances': instance_group_manager_RequestParser._parse_abandonInstances,
            'deleteInstances': instance_group_manager_RequestParser._parse_deleteInstances,
            'resize': instance_group_manager_RequestParser._parse_resize,
            'delete': instance_group_manager_RequestParser._parse_delete,
            'insert': instance_group_manager_RequestParser._parse_insert,
            'startInstances': instance_group_manager_RequestParser._parse_startInstances,
            'listPerInstanceConfigs': instance_group_manager_RequestParser._parse_listPerInstanceConfigs,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_deletePerInstanceConfigs(
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
        params['InstanceGroupManagersDeletePerInstanceConfigsReq'] = body.get('InstanceGroupManagersDeletePerInstanceConfigsReq')
        return params

    @staticmethod
    def _parse_resumeInstances(
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
        params['InstanceGroupManagersResumeInstancesRequest'] = body.get('InstanceGroupManagersResumeInstancesRequest')
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
        params['InstanceGroupManager'] = body.get('InstanceGroupManager')
        return params

    @staticmethod
    def _parse_suspendInstances(
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
        params['InstanceGroupManagersSuspendInstancesRequest'] = body.get('InstanceGroupManagersSuspendInstancesRequest')
        return params

    @staticmethod
    def _parse_patchPerInstanceConfigs(
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
        params['InstanceGroupManagersPatchPerInstanceConfigsReq'] = body.get('InstanceGroupManagersPatchPerInstanceConfigsReq')
        return params

    @staticmethod
    def _parse_stopInstances(
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
        params['InstanceGroupManagersStopInstancesRequest'] = body.get('InstanceGroupManagersStopInstancesRequest')
        return params

    @staticmethod
    def _parse_recreateInstances(
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
        params['InstanceGroupManagersRecreateInstancesRequest'] = body.get('InstanceGroupManagersRecreateInstancesRequest')
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
    def _parse_setInstanceTemplate(
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
        params['InstanceGroupManagersSetInstanceTemplateRequest'] = body.get('InstanceGroupManagersSetInstanceTemplateRequest')
        return params

    @staticmethod
    def _parse_setTargetPools(
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
        params['InstanceGroupManagersSetTargetPoolsRequest'] = body.get('InstanceGroupManagersSetTargetPoolsRequest')
        return params

    @staticmethod
    def _parse_listManagedInstances(
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
    def _parse_createInstances(
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
        params['InstanceGroupManagersCreateInstancesRequest'] = body.get('InstanceGroupManagersCreateInstancesRequest')
        return params

    @staticmethod
    def _parse_listErrors(
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
    def _parse_updatePerInstanceConfigs(
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
        params['InstanceGroupManagersUpdatePerInstanceConfigsReq'] = body.get('InstanceGroupManagersUpdatePerInstanceConfigsReq')
        return params

    @staticmethod
    def _parse_applyUpdatesToInstances(
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
        params['InstanceGroupManagersApplyUpdatesRequest'] = body.get('InstanceGroupManagersApplyUpdatesRequest')
        return params

    @staticmethod
    def _parse_abandonInstances(
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
        params['InstanceGroupManagersAbandonInstancesRequest'] = body.get('InstanceGroupManagersAbandonInstancesRequest')
        return params

    @staticmethod
    def _parse_deleteInstances(
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
        params['InstanceGroupManagersDeleteInstancesRequest'] = body.get('InstanceGroupManagersDeleteInstancesRequest')
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
        if 'size' in query_params:
            params['size'] = query_params['size']
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
        params['InstanceGroupManager'] = body.get('InstanceGroupManager')
        return params

    @staticmethod
    def _parse_startInstances(
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
        params['InstanceGroupManagersStartInstancesRequest'] = body.get('InstanceGroupManagersStartInstancesRequest')
        return params

    @staticmethod
    def _parse_listPerInstanceConfigs(
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


class instance_group_manager_ResponseSerializer:
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
            'deletePerInstanceConfigs': instance_group_manager_ResponseSerializer._serialize_deletePerInstanceConfigs,
            'resumeInstances': instance_group_manager_ResponseSerializer._serialize_resumeInstances,
            'patch': instance_group_manager_ResponseSerializer._serialize_patch,
            'suspendInstances': instance_group_manager_ResponseSerializer._serialize_suspendInstances,
            'patchPerInstanceConfigs': instance_group_manager_ResponseSerializer._serialize_patchPerInstanceConfigs,
            'stopInstances': instance_group_manager_ResponseSerializer._serialize_stopInstances,
            'recreateInstances': instance_group_manager_ResponseSerializer._serialize_recreateInstances,
            'list': instance_group_manager_ResponseSerializer._serialize_list,
            'setInstanceTemplate': instance_group_manager_ResponseSerializer._serialize_setInstanceTemplate,
            'setTargetPools': instance_group_manager_ResponseSerializer._serialize_setTargetPools,
            'listManagedInstances': instance_group_manager_ResponseSerializer._serialize_listManagedInstances,
            'createInstances': instance_group_manager_ResponseSerializer._serialize_createInstances,
            'listErrors': instance_group_manager_ResponseSerializer._serialize_listErrors,
            'aggregatedList': instance_group_manager_ResponseSerializer._serialize_aggregatedList,
            'get': instance_group_manager_ResponseSerializer._serialize_get,
            'updatePerInstanceConfigs': instance_group_manager_ResponseSerializer._serialize_updatePerInstanceConfigs,
            'applyUpdatesToInstances': instance_group_manager_ResponseSerializer._serialize_applyUpdatesToInstances,
            'abandonInstances': instance_group_manager_ResponseSerializer._serialize_abandonInstances,
            'deleteInstances': instance_group_manager_ResponseSerializer._serialize_deleteInstances,
            'resize': instance_group_manager_ResponseSerializer._serialize_resize,
            'delete': instance_group_manager_ResponseSerializer._serialize_delete,
            'insert': instance_group_manager_ResponseSerializer._serialize_insert,
            'startInstances': instance_group_manager_ResponseSerializer._serialize_startInstances,
            'listPerInstanceConfigs': instance_group_manager_ResponseSerializer._serialize_listPerInstanceConfigs,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_deletePerInstanceConfigs(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_resumeInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_suspendInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patchPerInstanceConfigs(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_stopInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_recreateInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setInstanceTemplate(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setTargetPools(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listManagedInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_createInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listErrors(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_updatePerInstanceConfigs(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_applyUpdatesToInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_abandonInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_deleteInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_resize(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_startInstances(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listPerInstanceConfigs(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

