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
class TargetPool:
    instances: List[Any] = field(default_factory=list)
    creation_timestamp: str = ""
    failover_ratio: Any = None
    description: str = ""
    health_checks: List[Any] = field(default_factory=list)
    region: str = ""
    security_policy: str = ""
    backup_pool: str = ""
    name: str = ""
    session_affinity: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["instances"] = self.instances
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.failover_ratio is not None and self.failover_ratio != None:
            d["failoverRatio"] = self.failover_ratio
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["healthChecks"] = self.health_checks
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.security_policy is not None and self.security_policy != "":
            d["securityPolicy"] = self.security_policy
        if self.backup_pool is not None and self.backup_pool != "":
            d["backupPool"] = self.backup_pool
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.id is not None and self.id != "":
            d["id"] = self.id
        if self.session_affinity is not None and self.session_affinity != "":
            d["sessionAffinity"] = self.session_affinity
        d["kind"] = "compute#targetpool"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class TargetPool_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.target_pools  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "target-pool") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_target_pool_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource {name!r} was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a target pool in the specified project and region using
the data included in the request."""
        project = params.get("project")
        region = params.get("region")
        body = params.get("TargetPool") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'TargetPool' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"TargetPool '{name}' already exists", "ALREADY_EXISTS")
        instances = body.get("instances") or []
        for instance in instances:
            instance_name = instance.split("/")[-1] if instance else ""
            instance_found = (
                self.state.instances.get(instance_name)
                or self.state.instances.get(instance)
                or self.state.region_instances.get(instance_name)
                or self.state.region_instances.get(instance)
            )
            if instance_name and not instance_found:
                return create_gcp_error(404, f"Instance '{instance_name}' not found", "NOT_FOUND")
        health_checks = body.get("healthChecks") or []
        for health_check in health_checks:
            health_check_name = health_check.split("/")[-1] if health_check else ""
            if health_check_name and not (
                self.state.health_checks.get(health_check_name)
                or self.state.health_checks.get(health_check)
                or self.state.region_health_checks.get(health_check_name)
                or self.state.region_health_checks.get(health_check)
                or self.state.http_health_checks.get(health_check_name)
                or self.state.http_health_checks.get(health_check)
                or self.state.https_health_checks.get(health_check_name)
                or self.state.https_health_checks.get(health_check)
                or self.state.region_health_check_services.get(health_check_name)
                or self.state.region_health_check_services.get(health_check)
            ):
                return create_gcp_error(
                    404,
                    f"Health check '{health_check_name}' not found",
                    "NOT_FOUND",
                )
        security_policy = body.get("securityPolicy") or ""
        if security_policy and not (
            self.state.security_policies.get(security_policy)
            or self.state.security_policies.get(security_policy.split("/")[-1])
            or self.state.region_security_policies.get(security_policy)
            or self.state.region_security_policies.get(security_policy.split("/")[-1])
        ):
            return create_gcp_error(
                404,
                f"Security policy '{security_policy.split('/')[-1]}' not found",
                "NOT_FOUND",
            )
        backup_pool = body.get("backupPool") or ""
        if backup_pool:
            backup_name = backup_pool.split("/")[-1]
            if not (
                self.resources.get(backup_name)
                or self.resources.get(backup_pool)
            ):
                return create_gcp_error(
                    404,
                    f"Target pool '{backup_name}' not found",
                    "NOT_FOUND",
                )
        resource = TargetPool(
            instances=instances,
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            failover_ratio=body.get("failoverRatio"),
            description=body.get("description") or "",
            health_checks=health_checks,
            region=region,
            security_policy=security_policy,
            backup_pool=backup_pool,
            name=name,
            session_affinity=body.get("sessionAffinity") or "",
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified target pool."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of target pools available to the specified
project and region."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]
        return {
            "kind": "compute#targetpoolList",
            "id": f"projects/{project}/regions/{region}/targetPools",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of target pools.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        if not resources:
            scope_key = "regions/us-central1"
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items: Dict[str, Any] = {}
            for resource in resources:
                scope_key = f"regions/{resource.region or 'us-central1'}"
                bucket = items.setdefault(scope_key, {"TargetPools": []})
                bucket["TargetPools"].append(resource.to_dict())
        return {
            "kind": "compute#targetpoolAggregatedList",
            "id": f"projects/{project}/aggregated/targetPools",
            "items": items,
            "selfLink": "",
        }

    def getHealth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the most recent health check results for each IP for the
instance that is referenced by the given target pool."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        body = params.get("InstanceReference") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'InstanceReference' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        instance_ref = body.get("instance") or body.get("name") or ""
        if not instance_ref:
            return create_gcp_error(400, "Required field 'instance' not specified", "INVALID_ARGUMENT")
        instance_name = instance_ref.split("/")[-1]
        instance_found = (
            self.state.instances.get(instance_name)
            or self.state.instances.get(instance_ref)
            or self.state.region_instances.get(instance_name)
            or self.state.region_instances.get(instance_ref)
        )
        if not instance_found:
            return create_gcp_error(404, f"Instance '{instance_name}' not found", "NOT_FOUND")
        return {
            "kind": "compute#targetPoolInstanceHealth",
            "healthStatus": [
                {
                    "instance": instance_ref,
                    "healthState": "HEALTHY",
                }
            ],
        }

    def setSecurityPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the Google Cloud Armor security policy for the specified target pool.
For more information, seeGoogle
Cloud Armor Overview"""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        body = params.get("SecurityPolicyReference") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'SecurityPolicyReference' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        security_policy = body.get("securityPolicy") or body.get("name") or ""
        if not security_policy:
            return create_gcp_error(400, "Required field 'securityPolicy' not specified", "INVALID_ARGUMENT")
        policy_name = security_policy.split("/")[-1]
        policy_found = (
            self.state.security_policies.get(security_policy)
            or self.state.security_policies.get(policy_name)
            or self.state.region_security_policies.get(security_policy)
            or self.state.region_security_policies.get(policy_name)
        )
        if not policy_found:
            return create_gcp_error(404, f"Security policy '{policy_name}' not found", "NOT_FOUND")
        resource.security_policy = security_policy
        return make_operation(
            operation_type="setSecurityPolicy",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )

    def addInstance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds an instance to a target pool."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        body = params.get("TargetPoolsAddInstanceRequest") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'TargetPoolsAddInstanceRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        instances = body.get("instances")
        if not instances:
            return create_gcp_error(400, "Required field 'instances' not specified", "INVALID_ARGUMENT")
        updated_instances = list(resource.instances)
        for instance_entry in instances:
            if isinstance(instance_entry, dict):
                instance_ref = instance_entry.get("instance") or instance_entry.get("name") or ""
            else:
                instance_ref = instance_entry
            if not instance_ref:
                return create_gcp_error(400, "Required field 'instance' not specified", "INVALID_ARGUMENT")
            instance_name = instance_ref.split("/")[-1]
            instance_found = (
                self.state.instances.get(instance_name)
                or self.state.instances.get(instance_ref)
                or self.state.region_instances.get(instance_name)
                or self.state.region_instances.get(instance_ref)
            )
            if not instance_found:
                return create_gcp_error(404, f"Instance '{instance_name}' not found", "NOT_FOUND")
            if instance_ref not in updated_instances:
                updated_instances.append(instance_ref)
        resource.instances = updated_instances
        return make_operation(
            operation_type="addInstance",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        region = params.get("region")
        resource_name = params.get("resource")
        body = params.get("TestPermissionsRequest") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(resource_name)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{resource_name}' was not found", "NOT_FOUND")
        permissions = body.get("permissions") or []
        return {
            "kind": "compute#testIamPermissionsResponse",
            "permissions": permissions,
        }

    def addHealthCheck(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds health check URLs to a target pool."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        body = params.get("TargetPoolsAddHealthCheckRequest") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'TargetPoolsAddHealthCheckRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        health_checks = body.get("healthChecks")
        if not health_checks:
            return create_gcp_error(400, "Required field 'healthChecks' not specified", "INVALID_ARGUMENT")
        updated_health_checks = list(resource.health_checks)
        for health_check_entry in health_checks:
            if isinstance(health_check_entry, dict):
                health_check_ref = (
                    health_check_entry.get("healthCheck")
                    or health_check_entry.get("name")
                    or ""
                )
            else:
                health_check_ref = health_check_entry
            if not health_check_ref:
                return create_gcp_error(400, "Required field 'healthCheck' not specified", "INVALID_ARGUMENT")
            health_check_name = health_check_ref.split("/")[-1]
            if not (
                self.state.health_checks.get(health_check_name)
                or self.state.health_checks.get(health_check_ref)
                or self.state.region_health_checks.get(health_check_name)
                or self.state.region_health_checks.get(health_check_ref)
                or self.state.http_health_checks.get(health_check_name)
                or self.state.http_health_checks.get(health_check_ref)
                or self.state.https_health_checks.get(health_check_name)
                or self.state.https_health_checks.get(health_check_ref)
                or self.state.region_health_check_services.get(health_check_name)
                or self.state.region_health_check_services.get(health_check_ref)
            ):
                return create_gcp_error(
                    404,
                    f"Health check '{health_check_name}' not found",
                    "NOT_FOUND",
                )
            if health_check_ref not in updated_health_checks:
                updated_health_checks.append(health_check_ref)
        resource.health_checks = updated_health_checks
        return make_operation(
            operation_type="addHealthCheck",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )

    def removeInstance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes instance URL from a target pool."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        body = params.get("TargetPoolsRemoveInstanceRequest") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'TargetPoolsRemoveInstanceRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        instances = body.get("instances")
        if not instances:
            return create_gcp_error(400, "Required field 'instances' not specified", "INVALID_ARGUMENT")
        updated_instances = list(resource.instances)
        for instance_entry in instances:
            if isinstance(instance_entry, dict):
                instance_ref = instance_entry.get("instance") or instance_entry.get("name") or ""
            else:
                instance_ref = instance_entry
            if not instance_ref:
                return create_gcp_error(400, "Required field 'instance' not specified", "INVALID_ARGUMENT")
            instance_name = instance_ref.split("/")[-1]
            instance_found = (
                self.state.instances.get(instance_name)
                or self.state.instances.get(instance_ref)
                or self.state.region_instances.get(instance_name)
                or self.state.region_instances.get(instance_ref)
            )
            if not instance_found:
                return create_gcp_error(404, f"Instance '{instance_name}' not found", "NOT_FOUND")
            if instance_ref in updated_instances:
                updated_instances.remove(instance_ref)
        resource.instances = updated_instances
        return make_operation(
            operation_type="removeInstance",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )

    def setBackup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes a backup target pool's configurations."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        body = params.get("TargetReference") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'TargetReference' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        backup_ref = body.get("target") or body.get("name") or ""
        if not backup_ref:
            return create_gcp_error(400, "Required field 'target' not specified", "INVALID_ARGUMENT")
        backup_name = backup_ref.split("/")[-1]
        backup_resource = self.resources.get(backup_ref) or self.resources.get(backup_name)
        if not backup_resource:
            return create_gcp_error(404, f"Target pool '{backup_name}' not found", "NOT_FOUND")
        failover_ratio = params.get("failoverRatio")
        if failover_ratio is not None:
            resource.failover_ratio = failover_ratio
        resource.backup_pool = backup_ref
        return make_operation(
            operation_type="setBackup",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )

    def removeHealthCheck(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes health check URL from a target pool."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        body = params.get("TargetPoolsRemoveHealthCheckRequest") or {}
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        if not body:
            return create_gcp_error(400, "Required field 'TargetPoolsRemoveHealthCheckRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        health_checks = body.get("healthChecks")
        if not health_checks:
            return create_gcp_error(400, "Required field 'healthChecks' not specified", "INVALID_ARGUMENT")
        updated_health_checks = list(resource.health_checks)
        for health_check_entry in health_checks:
            if isinstance(health_check_entry, dict):
                health_check_ref = (
                    health_check_entry.get("healthCheck")
                    or health_check_entry.get("name")
                    or ""
                )
            else:
                health_check_ref = health_check_entry
            if not health_check_ref:
                return create_gcp_error(400, "Required field 'healthCheck' not specified", "INVALID_ARGUMENT")
            health_check_name = health_check_ref.split("/")[-1]
            if not (
                self.state.health_checks.get(health_check_name)
                or self.state.health_checks.get(health_check_ref)
                or self.state.region_health_checks.get(health_check_name)
                or self.state.region_health_checks.get(health_check_ref)
                or self.state.http_health_checks.get(health_check_name)
                or self.state.http_health_checks.get(health_check_ref)
                or self.state.https_health_checks.get(health_check_name)
                or self.state.https_health_checks.get(health_check_ref)
                or self.state.region_health_check_services.get(health_check_name)
                or self.state.region_health_check_services.get(health_check_ref)
            ):
                return create_gcp_error(
                    404,
                    f"Health check '{health_check_name}' not found",
                    "NOT_FOUND",
                )
            if health_check_ref in updated_health_checks:
                updated_health_checks.remove(health_check_ref)
        resource.health_checks = updated_health_checks
        return make_operation(
            operation_type="removeHealthCheck",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified target pool."""
        project = params.get("project")
        region = params.get("region")
        target_pool = params.get("targetPool")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        if not target_pool:
            return create_gcp_error(400, "Required field 'targetPool' not specified", "INVALID_ARGUMENT")
        resource = self._get_target_pool_or_error(target_pool)
        if is_error_response(resource):
            return resource
        if resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource '{target_pool}' was not found", "NOT_FOUND")
        self.resources.pop(resource.name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/targetPools/{resource.name}",
            params=params,
        )


class target_pool_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'getHealth': target_pool_RequestParser._parse_getHealth,
            'setSecurityPolicy': target_pool_RequestParser._parse_setSecurityPolicy,
            'addInstance': target_pool_RequestParser._parse_addInstance,
            'get': target_pool_RequestParser._parse_get,
            'insert': target_pool_RequestParser._parse_insert,
            'testIamPermissions': target_pool_RequestParser._parse_testIamPermissions,
            'list': target_pool_RequestParser._parse_list,
            'addHealthCheck': target_pool_RequestParser._parse_addHealthCheck,
            'removeInstance': target_pool_RequestParser._parse_removeInstance,
            'delete': target_pool_RequestParser._parse_delete,
            'setBackup': target_pool_RequestParser._parse_setBackup,
            'aggregatedList': target_pool_RequestParser._parse_aggregatedList,
            'removeHealthCheck': target_pool_RequestParser._parse_removeHealthCheck,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_getHealth(
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
        params['InstanceReference'] = body.get('InstanceReference')
        return params

    @staticmethod
    def _parse_setSecurityPolicy(
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
        params['SecurityPolicyReference'] = body.get('SecurityPolicyReference')
        return params

    @staticmethod
    def _parse_addInstance(
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
        params['TargetPoolsAddInstanceRequest'] = body.get('TargetPoolsAddInstanceRequest')
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
        params['TargetPool'] = body.get('TargetPool')
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
    def _parse_addHealthCheck(
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
        params['TargetPoolsAddHealthCheckRequest'] = body.get('TargetPoolsAddHealthCheckRequest')
        return params

    @staticmethod
    def _parse_removeInstance(
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
        params['TargetPoolsRemoveInstanceRequest'] = body.get('TargetPoolsRemoveInstanceRequest')
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
    def _parse_setBackup(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'failoverRatio' in query_params:
            params['failoverRatio'] = query_params['failoverRatio']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['TargetReference'] = body.get('TargetReference')
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
    def _parse_removeHealthCheck(
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
        params['TargetPoolsRemoveHealthCheckRequest'] = body.get('TargetPoolsRemoveHealthCheckRequest')
        return params


class target_pool_ResponseSerializer:
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
            'getHealth': target_pool_ResponseSerializer._serialize_getHealth,
            'setSecurityPolicy': target_pool_ResponseSerializer._serialize_setSecurityPolicy,
            'addInstance': target_pool_ResponseSerializer._serialize_addInstance,
            'get': target_pool_ResponseSerializer._serialize_get,
            'insert': target_pool_ResponseSerializer._serialize_insert,
            'testIamPermissions': target_pool_ResponseSerializer._serialize_testIamPermissions,
            'list': target_pool_ResponseSerializer._serialize_list,
            'addHealthCheck': target_pool_ResponseSerializer._serialize_addHealthCheck,
            'removeInstance': target_pool_ResponseSerializer._serialize_removeInstance,
            'delete': target_pool_ResponseSerializer._serialize_delete,
            'setBackup': target_pool_ResponseSerializer._serialize_setBackup,
            'aggregatedList': target_pool_ResponseSerializer._serialize_aggregatedList,
            'removeHealthCheck': target_pool_ResponseSerializer._serialize_removeHealthCheck,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_getHealth(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setSecurityPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addInstance(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addHealthCheck(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeInstance(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setBackup(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeHealthCheck(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

