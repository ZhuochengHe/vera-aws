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
class Project:
    common_instance_metadata: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    vm_dns_setting: str = ""
    quotas: List[Any] = field(default_factory=list)
    default_service_account: str = ""
    enabled_features: List[Any] = field(default_factory=list)
    cloud_armor_tier: str = ""
    usage_export_location: Dict[str, Any] = field(default_factory=dict)
    xpn_project_status: str = ""
    description: str = ""
    creation_timestamp: str = ""
    default_network_tier: str = ""
    id: str = ""

    xpn_host: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["commonInstanceMetadata"] = self.common_instance_metadata
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.vm_dns_setting is not None and self.vm_dns_setting != "":
            d["vmDnsSetting"] = self.vm_dns_setting
        d["quotas"] = self.quotas
        if self.default_service_account is not None and self.default_service_account != "":
            d["defaultServiceAccount"] = self.default_service_account
        d["enabledFeatures"] = self.enabled_features
        if self.cloud_armor_tier is not None and self.cloud_armor_tier != "":
            d["cloudArmorTier"] = self.cloud_armor_tier
        d["usageExportLocation"] = self.usage_export_location
        if self.xpn_project_status is not None and self.xpn_project_status != "":
            d["xpnProjectStatus"] = self.xpn_project_status
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.default_network_tier is not None and self.default_network_tier != "":
            d["defaultNetworkTier"] = self.default_network_tier
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#project"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Project_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.projects  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "project") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_project_or_error(self, project: str) -> Project | Dict[str, Any]:
        resource = self.resources.get(project)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}' was not found",
                "NOT_FOUND",
            )
        return resource

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified Project resource.

To decrease latency for this method, you can optionally omit any unneeded
information from the response by using a field mask. This practice is
especially r..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def moveInstance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Moves an instance and its attached persistent disks from one zone to
another.
*Note*: Moving VMs or disks by using this method might
 cause unexpected behavior. For more information, see the [known..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstanceMoveRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstanceMoveRequest' not found",
                "INVALID_ARGUMENT",
            )
        project_resource = self._get_project_or_error(project)
        if is_error_response(project_resource):
            return project_resource
        source_instance_ref = body.get("sourceInstance") or body.get("instance") or body.get("source")
        instance_name = ""
        resource_path = ""
        instance = None
        if source_instance_ref:
            if isinstance(source_instance_ref, dict):
                instance_name = source_instance_ref.get("name") or ""
                resource_path = source_instance_ref.get("selfLink") or ""
            else:
                instance_name = str(source_instance_ref).split("/")[-1]
                resource_path = str(source_instance_ref)
            if resource_path.startswith("https://www.googleapis.com/compute/v1/"):
                resource_path = resource_path.split("https://www.googleapis.com/compute/v1/")[-1]
            instance = self.state.instances.get(instance_name) if instance_name else None
            if instance_name and not instance:
                if not resource_path or resource_path == instance_name:
                    zone = ""
                    if isinstance(source_instance_ref, str) and "/zones/" in source_instance_ref:
                        zone = source_instance_ref.split("/zones/")[-1].split("/")[0]
                    zone = zone or body.get("sourceZone") or body.get("zone") or ""
                    if zone:
                        resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
                    else:
                        resource_path = f"projects/{project}/instances/{instance_name}"
                return create_gcp_error(
                    404,
                    f"The resource '{resource_path}' was not found",
                    "NOT_FOUND",
                )
        destination_zone = body.get("destinationZone") or body.get("targetZone") or ""
        if instance and destination_zone:
            instance.zone = destination_zone
            for disk_name in getattr(instance, "attached_disk_names", []):
                disk = self.state.disks.get(disk_name)
                if disk:
                    disk.zone = destination_zone
        resource_link = None
        if instance_name:
            zone_part = destination_zone or (instance.zone if instance else "")
            if zone_part:
                resource_link = f"projects/{project}/zones/{zone_part}/Instances/{instance_name}"
            else:
                resource_link = f"projects/{project}/Instances/{instance_name}"
        return make_operation(
            operation_type="moveInstance",
            resource_link=resource_link,
            params=params,
        )

    def getXpnHost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the shared VPC host project that this project links to. May be empty
if no link exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        if not resource.xpn_host:
            return {}
        host_project = self.resources.get(resource.xpn_host)
        if not host_project:
            return create_gcp_error(
                404,
                f"The resource 'projects/{resource.xpn_host}' was not found",
                "NOT_FOUND",
            )
        return host_project.to_dict()

    def moveDisk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Moves a persistent disk from one zone to another.
*Note*: The moveDisk API will be deprecated on September 29, 2026.

Starting September 29, 2025, you can't use the moveDisk API on new
projects. To..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("DiskMoveRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'DiskMoveRequest' not found",
                "INVALID_ARGUMENT",
            )
        project_resource = self._get_project_or_error(project)
        if is_error_response(project_resource):
            return project_resource
        source_disk_ref = body.get("sourceDisk") or body.get("disk") or body.get("source")
        disk_name = ""
        resource_path = ""
        disk = None
        if source_disk_ref:
            if isinstance(source_disk_ref, dict):
                disk_name = source_disk_ref.get("name") or ""
                resource_path = source_disk_ref.get("selfLink") or ""
            else:
                disk_name = str(source_disk_ref).split("/")[-1]
                resource_path = str(source_disk_ref)
            if resource_path.startswith("https://www.googleapis.com/compute/v1/"):
                resource_path = resource_path.split("https://www.googleapis.com/compute/v1/")[-1]
            disk = self.state.disks.get(disk_name) if disk_name else None
            if disk_name and not disk:
                if not resource_path or resource_path == disk_name:
                    zone = ""
                    if isinstance(source_disk_ref, str) and "/zones/" in source_disk_ref:
                        zone = source_disk_ref.split("/zones/")[-1].split("/")[0]
                    zone = zone or body.get("sourceZone") or body.get("zone") or ""
                    if zone:
                        resource_path = f"projects/{project}/zones/{zone}/disks/{disk_name}"
                    else:
                        resource_path = f"projects/{project}/disks/{disk_name}"
                return create_gcp_error(
                    404,
                    f"The resource '{resource_path}' was not found",
                    "NOT_FOUND",
                )
        destination_zone = body.get("destinationZone") or body.get("targetZone") or ""
        if disk and destination_zone:
            disk.zone = destination_zone
        resource_link = None
        if disk_name:
            zone_part = destination_zone or (disk.zone if disk else "")
            if zone_part:
                resource_link = f"projects/{project}/zones/{zone_part}/Disks/{disk_name}"
            else:
                resource_link = f"projects/{project}/Disks/{disk_name}"
        return make_operation(
            operation_type="moveDisk",
            resource_link=resource_link,
            params=params,
        )

    def setDefaultNetworkTier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the default network tier of the project. The default network tier is
used when an address/forwardingRule/instance is created without specifying
the network tier field."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("ProjectsSetDefaultNetworkTierRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ProjectsSetDefaultNetworkTierRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        network_tier = body.get("networkTier") or body.get("defaultNetworkTier") or ""
        if not network_tier:
            return create_gcp_error(
                400,
                "Required field 'networkTier' not found",
                "INVALID_ARGUMENT",
            )
        resource.default_network_tier = network_tier
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="setDefaultNetworkTier",
            resource_link=resource_link,
            params=params,
        )

    def disableXpnHost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable this project as a shared VPC host project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        resource.xpn_project_status = ""
        for other_project in self.resources.values():
            if other_project.xpn_host == project:
                other_project.xpn_host = ""
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="disableXpnHost",
            resource_link=resource_link,
            params=params,
        )

    def disableXpnResource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable a service resource (also known as service project) associated with
this host project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("ProjectsDisableXpnResourceRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ProjectsDisableXpnResourceRequest' not found",
                "INVALID_ARGUMENT",
            )
        host_project = self._get_project_or_error(project)
        if is_error_response(host_project):
            return host_project
        xpn_resource = body.get("xpnResource") or body.get("xpnResourceId") or body.get("resource")
        if not xpn_resource:
            return create_gcp_error(
                400,
                "Required field 'xpnResource' not found",
                "INVALID_ARGUMENT",
            )
        service_project_name = ""
        if isinstance(xpn_resource, dict):
            service_project_name = (
                xpn_resource.get("id")
                or xpn_resource.get("name")
                or xpn_resource.get("project")
                or ""
            )
        else:
            service_project_name = str(xpn_resource)
        if service_project_name.startswith("projects/"):
            service_project_name = service_project_name.split("/")[-1]
        if not service_project_name:
            return create_gcp_error(
                400,
                "Required field 'xpnResource.id' not found",
                "INVALID_ARGUMENT",
            )
        service_project = self.resources.get(service_project_name)
        if not service_project:
            return create_gcp_error(
                404,
                f"The resource 'projects/{service_project_name}' was not found",
                "NOT_FOUND",
            )
        if service_project.xpn_host != project:
            return create_gcp_error(
                400,
                "Service project is not associated with this host project",
                "FAILED_PRECONDITION",
            )
        service_project.xpn_host = ""
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="disableXpnResource",
            resource_link=resource_link,
            params=params,
        )

    def getXpnResources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets service resources (a.k.a service project) associated with this host
project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        host_project = self._get_project_or_error(project)
        if is_error_response(host_project):
            return host_project
        resources = [
            resource for resource in self.resources.values() if resource.xpn_host == project
        ]
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                name = match.group(1)
                resources = [resource for resource in resources if resource.name == name]
        return {
            "kind": "compute#xpnResourceIdList",
            "id": f"projects/{project}/getXpnResources",
            "items": [
                {"id": resource.name, "type": "PROJECT"} for resource in resources
            ],
            "selfLink": "",
        }

    def setCloudArmorTier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the Cloud Armor tier of the project. To set ENTERPRISE or above the
billing account of the project must be subscribed to Cloud Armor
Enterprise. See Subscribing
to Cloud Armor Enterprise for m..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("ProjectsSetCloudArmorTierRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ProjectsSetCloudArmorTierRequest' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        cloud_armor_tier = body.get("cloudArmorTier") or body.get("tier") or ""
        if not cloud_armor_tier:
            return create_gcp_error(
                400,
                "Required field 'cloudArmorTier' not found",
                "INVALID_ARGUMENT",
            )
        resource.cloud_armor_tier = cloud_armor_tier
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="setCloudArmorTier",
            resource_link=resource_link,
            params=params,
        )

    def enableXpnResource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable service resource (a.k.a service project) for a host project, so that
subnets in the host project can be used by instances in the service
project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("ProjectsEnableXpnResourceRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ProjectsEnableXpnResourceRequest' not found",
                "INVALID_ARGUMENT",
            )
        host_project = self._get_project_or_error(project)
        if is_error_response(host_project):
            return host_project
        xpn_resource = body.get("xpnResource") or body.get("xpnResourceId") or body.get("resource")
        if not xpn_resource:
            return create_gcp_error(
                400,
                "Required field 'xpnResource' not found",
                "INVALID_ARGUMENT",
            )
        service_project_name = ""
        if isinstance(xpn_resource, dict):
            service_project_name = (
                xpn_resource.get("id")
                or xpn_resource.get("name")
                or xpn_resource.get("project")
                or ""
            )
        else:
            service_project_name = str(xpn_resource)
        if service_project_name.startswith("projects/"):
            service_project_name = service_project_name.split("/")[-1]
        if not service_project_name:
            return create_gcp_error(
                400,
                "Required field 'xpnResource.id' not found",
                "INVALID_ARGUMENT",
            )
        service_project = self.resources.get(service_project_name)
        if not service_project:
            return create_gcp_error(
                404,
                f"The resource 'projects/{service_project_name}' was not found",
                "NOT_FOUND",
            )
        if service_project.xpn_host and service_project.xpn_host != project:
            return create_gcp_error(
                400,
                "Service project is already associated with another host project",
                "FAILED_PRECONDITION",
            )
        service_project.xpn_host = project
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="enableXpnResource",
            resource_link=resource_link,
            params=params,
        )

    def setUsageExportBucket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enables the usage export feature and sets theusage export bucket
where reports are stored. If you provide an empty request body using this
method, the usage export feature will be disabled."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        usage_export = params.get("UsageExportLocation")
        if usage_export is None:
            return create_gcp_error(
                400,
                "Required field 'UsageExportLocation' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        resource.usage_export_location = usage_export or {}
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="setUsageExportBucket",
            resource_link=resource_link,
            params=params,
        )

    def setCommonInstanceMetadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets metadata common to all instances within the specified project using
the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        metadata = params.get("Metadata")
        if metadata is None:
            return create_gcp_error(
                400,
                "Required field 'Metadata' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        resource.common_instance_metadata = metadata
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="setCommonInstanceMetadata",
            resource_link=resource_link,
            params=params,
        )

    def listXpnHosts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all shared VPC host projects visible to the user in an organization."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("ProjectsListXpnHostsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ProjectsListXpnHostsRequest' not found",
                "INVALID_ARGUMENT",
            )
        requester = self._get_project_or_error(project)
        if is_error_response(requester):
            return requester
        resources = [
            resource for resource in self.resources.values() if resource.xpn_project_status
        ]
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                name = match.group(1)
                resources = [resource for resource in resources if resource.name == name]
        return {
            "kind": "compute#xpnHostList",
            "id": f"projects/{project}/listXpnHosts",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def enableXpnHost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable this project as a shared VPC host project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        resource = self._get_project_or_error(project)
        if is_error_response(resource):
            return resource
        resource.xpn_project_status = "HOST"
        resource_link = f"projects/{project}"
        return make_operation(
            operation_type="enableXpnHost",
            resource_link=resource_link,
            params=params,
        )


class project_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'moveInstance': project_RequestParser._parse_moveInstance,
            'getXpnHost': project_RequestParser._parse_getXpnHost,
            'moveDisk': project_RequestParser._parse_moveDisk,
            'setDefaultNetworkTier': project_RequestParser._parse_setDefaultNetworkTier,
            'disableXpnHost': project_RequestParser._parse_disableXpnHost,
            'disableXpnResource': project_RequestParser._parse_disableXpnResource,
            'getXpnResources': project_RequestParser._parse_getXpnResources,
            'setCloudArmorTier': project_RequestParser._parse_setCloudArmorTier,
            'enableXpnResource': project_RequestParser._parse_enableXpnResource,
            'setUsageExportBucket': project_RequestParser._parse_setUsageExportBucket,
            'setCommonInstanceMetadata': project_RequestParser._parse_setCommonInstanceMetadata,
            'listXpnHosts': project_RequestParser._parse_listXpnHosts,
            'enableXpnHost': project_RequestParser._parse_enableXpnHost,
            'get': project_RequestParser._parse_get,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_moveInstance(
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
        params['InstanceMoveRequest'] = body.get('InstanceMoveRequest')
        return params

    @staticmethod
    def _parse_getXpnHost(
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
    def _parse_moveDisk(
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
        params['DiskMoveRequest'] = body.get('DiskMoveRequest')
        return params

    @staticmethod
    def _parse_setDefaultNetworkTier(
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
        params['ProjectsSetDefaultNetworkTierRequest'] = body.get('ProjectsSetDefaultNetworkTierRequest')
        return params

    @staticmethod
    def _parse_disableXpnHost(
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
    def _parse_disableXpnResource(
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
        params['ProjectsDisableXpnResourceRequest'] = body.get('ProjectsDisableXpnResourceRequest')
        return params

    @staticmethod
    def _parse_getXpnResources(
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
    def _parse_setCloudArmorTier(
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
        params['ProjectsSetCloudArmorTierRequest'] = body.get('ProjectsSetCloudArmorTierRequest')
        return params

    @staticmethod
    def _parse_enableXpnResource(
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
        params['ProjectsEnableXpnResourceRequest'] = body.get('ProjectsEnableXpnResourceRequest')
        return params

    @staticmethod
    def _parse_setUsageExportBucket(
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
        params['UsageExportLocation'] = body.get('UsageExportLocation')
        return params

    @staticmethod
    def _parse_setCommonInstanceMetadata(
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
        params['Metadata'] = body.get('Metadata')
        return params

    @staticmethod
    def _parse_listXpnHosts(
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
        params['ProjectsListXpnHostsRequest'] = body.get('ProjectsListXpnHostsRequest')
        return params

    @staticmethod
    def _parse_enableXpnHost(
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


class project_ResponseSerializer:
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
            'moveInstance': project_ResponseSerializer._serialize_moveInstance,
            'getXpnHost': project_ResponseSerializer._serialize_getXpnHost,
            'moveDisk': project_ResponseSerializer._serialize_moveDisk,
            'setDefaultNetworkTier': project_ResponseSerializer._serialize_setDefaultNetworkTier,
            'disableXpnHost': project_ResponseSerializer._serialize_disableXpnHost,
            'disableXpnResource': project_ResponseSerializer._serialize_disableXpnResource,
            'getXpnResources': project_ResponseSerializer._serialize_getXpnResources,
            'setCloudArmorTier': project_ResponseSerializer._serialize_setCloudArmorTier,
            'enableXpnResource': project_ResponseSerializer._serialize_enableXpnResource,
            'setUsageExportBucket': project_ResponseSerializer._serialize_setUsageExportBucket,
            'setCommonInstanceMetadata': project_ResponseSerializer._serialize_setCommonInstanceMetadata,
            'listXpnHosts': project_ResponseSerializer._serialize_listXpnHosts,
            'enableXpnHost': project_ResponseSerializer._serialize_enableXpnHost,
            'get': project_ResponseSerializer._serialize_get,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_moveInstance(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getXpnHost(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_moveDisk(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setDefaultNetworkTier(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_disableXpnHost(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_disableXpnResource(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getXpnResources(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setCloudArmorTier(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_enableXpnResource(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setUsageExportBucket(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setCommonInstanceMetadata(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listXpnHosts(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_enableXpnHost(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

