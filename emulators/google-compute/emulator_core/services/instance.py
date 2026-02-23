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
class Instance:
    params: Dict[str, Any] = field(default_factory=dict)
    confidential_instance_config: Dict[str, Any] = field(default_factory=dict)
    network_interfaces: List[Any] = field(default_factory=list)
    name: str = ""
    key_revocation_action_type: str = ""
    zone: str = ""
    resource_status: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    display_device: Dict[str, Any] = field(default_factory=dict)
    machine_type: str = ""
    instance_encryption_key: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    last_suspended_timestamp: str = ""
    shielded_instance_config: Dict[str, Any] = field(default_factory=dict)
    source_machine_image: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    advanced_machine_features: Dict[str, Any] = field(default_factory=dict)
    hostname: str = ""
    status_message: str = ""
    deletion_protection: bool = False
    satisfies_pzi: bool = False
    min_cpu_platform: str = ""
    disks: List[Any] = field(default_factory=list)
    satisfies_pzs: bool = False
    label_fingerprint: str = ""
    network_performance_config: Dict[str, Any] = field(default_factory=dict)
    guest_accelerators: List[Any] = field(default_factory=list)
    can_ip_forward: bool = False
    source_machine_image_encryption_key: Dict[str, Any] = field(default_factory=dict)
    reservation_affinity: Dict[str, Any] = field(default_factory=dict)
    fingerprint: str = ""
    resource_policies: List[Any] = field(default_factory=list)
    tags: Dict[str, Any] = field(default_factory=dict)
    service_accounts: List[Any] = field(default_factory=list)
    cpu_platform: str = ""
    last_stop_timestamp: str = ""
    start_restricted: bool = False
    scheduling: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    private_ipv6_google_access: str = ""
    last_start_timestamp: str = ""
    shielded_instance_integrity_policy: Dict[str, Any] = field(default_factory=dict)
    workload_identity_config: Dict[str, Any] = field(default_factory=dict)
    id: str = ""

    # Internal dependency tracking — not in API response
    attached_disk_names: List[str] = field(default_factory=list)  # tracks attached Disk names

    iam_policy: Dict[str, Any] = field(default_factory=dict)
    shielded_instance_identity: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["params"] = self.params
        d["confidentialInstanceConfig"] = self.confidential_instance_config
        d["networkInterfaces"] = self.network_interfaces
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.key_revocation_action_type is not None and self.key_revocation_action_type != "":
            d["keyRevocationActionType"] = self.key_revocation_action_type
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        d["resourceStatus"] = self.resource_status
        d["labels"] = self.labels
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["displayDevice"] = self.display_device
        if self.machine_type is not None and self.machine_type != "":
            d["machineType"] = self.machine_type
        d["instanceEncryptionKey"] = self.instance_encryption_key
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.last_suspended_timestamp is not None and self.last_suspended_timestamp != "":
            d["lastSuspendedTimestamp"] = self.last_suspended_timestamp
        d["shieldedInstanceConfig"] = self.shielded_instance_config
        if self.source_machine_image is not None and self.source_machine_image != "":
            d["sourceMachineImage"] = self.source_machine_image
        d["metadata"] = self.metadata
        d["advancedMachineFeatures"] = self.advanced_machine_features
        if self.hostname is not None and self.hostname != "":
            d["hostname"] = self.hostname
        if self.status_message is not None and self.status_message != "":
            d["statusMessage"] = self.status_message
        d["deletionProtection"] = self.deletion_protection
        d["satisfiesPzi"] = self.satisfies_pzi
        if self.min_cpu_platform is not None and self.min_cpu_platform != "":
            d["minCpuPlatform"] = self.min_cpu_platform
        d["disks"] = self.disks
        d["satisfiesPzs"] = self.satisfies_pzs
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        d["networkPerformanceConfig"] = self.network_performance_config
        d["guestAccelerators"] = self.guest_accelerators
        d["canIpForward"] = self.can_ip_forward
        d["sourceMachineImageEncryptionKey"] = self.source_machine_image_encryption_key
        d["reservationAffinity"] = self.reservation_affinity
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        d["resourcePolicies"] = self.resource_policies
        d["tags"] = self.tags
        d["serviceAccounts"] = self.service_accounts
        if self.cpu_platform is not None and self.cpu_platform != "":
            d["cpuPlatform"] = self.cpu_platform
        if self.last_stop_timestamp is not None and self.last_stop_timestamp != "":
            d["lastStopTimestamp"] = self.last_stop_timestamp
        d["startRestricted"] = self.start_restricted
        d["scheduling"] = self.scheduling
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.private_ipv6_google_access is not None and self.private_ipv6_google_access != "":
            d["privateIpv6GoogleAccess"] = self.private_ipv6_google_access
        if self.last_start_timestamp is not None and self.last_start_timestamp != "":
            d["lastStartTimestamp"] = self.last_start_timestamp
        d["shieldedInstanceIntegrityPolicy"] = self.shielded_instance_integrity_policy
        d["workloadIdentityConfig"] = self.workload_identity_config
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#instance"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class Instance_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.instances  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "instance") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource

    def _filter_resources(self, params: Dict[str, Any]) -> List[Instance]:
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                name = match.group(1)
                resources = [resource for resource in resources if resource.name == name]
        zone = params.get("zone")
        region = params.get("region")
        if zone:
            resources = [resource for resource in resources if getattr(resource, "zone", None) == zone]
        if region:
            resources = [resource for resource in resources if getattr(resource, "region", None) == region]
        return resources

    def _utcnow(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an instance resource in the specified project using the data
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
        body = params.get("Instance") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Instance' not found",
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
                f"Instance '{name}' already exists",
                "ALREADY_EXISTS",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        source_instance_template_ref = params.get("sourceInstanceTemplate") or body.get(
            "sourceInstanceTemplate"
        )
        source_instance_template_name = normalize_name(source_instance_template_ref)
        if source_instance_template_name and source_instance_template_name not in self.state.instance_templates:
            return create_gcp_error(
                404,
                f"Instance template '{source_instance_template_name}' not found",
                "NOT_FOUND",
            )
        source_machine_image_ref = params.get("sourceMachineImage") or body.get("sourceMachineImage")
        source_machine_image_name = normalize_name(source_machine_image_ref)
        if source_machine_image_name and source_machine_image_name not in self.state.machine_images:
            return create_gcp_error(
                404,
                f"Machine image '{source_machine_image_name}' not found",
                "NOT_FOUND",
            )

        network_interfaces = body.get("networkInterfaces") or []
        for interface in network_interfaces:
            network_ref = (interface or {}).get("network") or ""
            network_name = normalize_name(network_ref)
            if network_name and network_name not in self.state.networks:
                return create_gcp_error(
                    404,
                    f"Network '{network_name}' not found",
                    "NOT_FOUND",
                )
            subnetwork_ref = (interface or {}).get("subnetwork") or ""
            subnetwork_name = normalize_name(subnetwork_ref)
            if subnetwork_name and subnetwork_name not in self.state.subnetworks:
                return create_gcp_error(
                    404,
                    f"Subnetwork '{subnetwork_name}' not found",
                    "NOT_FOUND",
                )

        disks = body.get("disks") or []
        attached_disk_names: List[str] = []
        for disk in disks:
            source_ref = (disk or {}).get("source") or ""
            source_name = normalize_name(source_ref)
            if source_name:
                if source_name not in self.state.disks:
                    return create_gcp_error(
                        404,
                        f"Disk '{source_name}' not found",
                        "NOT_FOUND",
                    )
                attached_disk_names.append(source_name)

        resource_policies = body.get("resourcePolicies") or []
        for policy in resource_policies:
            policy_name = normalize_name(policy)
            if policy_name and policy_name not in self.state.resource_policies:
                return create_gcp_error(
                    404,
                    f"Resource policy '{policy_name}' not found",
                    "NOT_FOUND",
                )

        resource = Instance(
            params=body.get("params") or {},
            confidential_instance_config=body.get("confidentialInstanceConfig") or {},
            network_interfaces=network_interfaces,
            name=name,
            key_revocation_action_type=body.get("keyRevocationActionType") or "",
            zone=zone,
            resource_status=body.get("resourceStatus") or {},
            labels=body.get("labels") or {},
            creation_timestamp=body.get("creationTimestamp") or self._utcnow(),
            display_device=body.get("displayDevice") or {},
            machine_type=body.get("machineType") or "",
            instance_encryption_key=body.get("instanceEncryptionKey") or {},
            status=body.get("status") or "RUNNING",
            last_suspended_timestamp=body.get("lastSuspendedTimestamp") or "",
            shielded_instance_config=body.get("shieldedInstanceConfig") or {},
            source_machine_image=source_machine_image_ref or "",
            metadata=body.get("metadata") or {},
            advanced_machine_features=body.get("advancedMachineFeatures") or {},
            hostname=body.get("hostname") or "",
            status_message=body.get("statusMessage") or "",
            deletion_protection=bool(body.get("deletionProtection"))
            if "deletionProtection" in body
            else False,
            satisfies_pzi=bool(body.get("satisfiesPzi")) if "satisfiesPzi" in body else False,
            min_cpu_platform=body.get("minCpuPlatform") or "",
            disks=disks,
            satisfies_pzs=bool(body.get("satisfiesPzs")) if "satisfiesPzs" in body else False,
            label_fingerprint=body.get("labelFingerprint") or "",
            network_performance_config=body.get("networkPerformanceConfig") or {},
            guest_accelerators=body.get("guestAccelerators") or [],
            can_ip_forward=bool(body.get("canIpForward")) if "canIpForward" in body else False,
            source_machine_image_encryption_key=body.get("sourceMachineImageEncryptionKey")
            or {},
            reservation_affinity=body.get("reservationAffinity") or {},
            fingerprint=body.get("fingerprint") or "",
            resource_policies=resource_policies,
            tags=body.get("tags") or {},
            service_accounts=body.get("serviceAccounts") or [],
            cpu_platform=body.get("cpuPlatform") or "",
            last_stop_timestamp=body.get("lastStopTimestamp") or "",
            start_restricted=bool(body.get("startRestricted")) if "startRestricted" in body else False,
            scheduling=body.get("scheduling") or {},
            description=body.get("description") or "",
            private_ipv6_google_access=body.get("privateIpv6GoogleAccess") or "",
            last_start_timestamp=body.get("lastStartTimestamp") or "",
            shielded_instance_integrity_policy=body.get("shieldedInstanceIntegrityPolicy") or {},
            workload_identity_config=body.get("workloadIdentityConfig") or {},
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
            shielded_instance_identity=body.get("shieldedInstanceIdentity") or {},
            attached_disk_names=attached_disk_names,
        )
        resource.label_fingerprint = str(uuid.uuid4())[:8]
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/zones/{zone}/instances/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def bulkInsert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates multiple instances. Count specifies the number of instances to
create. For more information, seeAbout bulk
creation of VMs."""
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
        body = params.get("BulkInsertInstanceResource") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'BulkInsertInstanceResource' not found",
                "INVALID_ARGUMENT",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        instances_payload = body.get("instances") or body.get("items") or []
        if isinstance(instances_payload, dict):
            instance_entries = list(instances_payload.items())
        elif isinstance(instances_payload, list):
            instance_entries = [(instance.get("name"), instance) for instance in instances_payload]
        else:
            instance_entries = []

        if not instance_entries:
            instance_props = body.get("instanceProperties") or {}
            if not instance_props:
                return create_gcp_error(
                    400,
                    "Required field 'instanceProperties' not found",
                    "INVALID_ARGUMENT",
                )
            count_value = body.get("count")
            if count_value is None:
                count_value = 1
            try:
                count = int(count_value)
            except (TypeError, ValueError):
                count = 0
            if count <= 0:
                return create_gcp_error(
                    400,
                    "Required field 'count' not found",
                    "INVALID_ARGUMENT",
                )
            base_name = instance_props.get("name") or "instance"
            instance_entries = []
            for idx in range(count):
                instance_body = dict(instance_props)
                if count > 1:
                    instance_body["name"] = f"{base_name}-{idx + 1}"
                else:
                    instance_body["name"] = base_name
                instance_entries.append((instance_body.get("name"), instance_body))

        default_instance_template_ref = body.get("sourceInstanceTemplate") or ""
        default_instance_template_name = normalize_name(default_instance_template_ref)
        if default_instance_template_name and default_instance_template_name not in self.state.instance_templates:
            return create_gcp_error(
                404,
                f"Instance template '{default_instance_template_name}' not found",
                "NOT_FOUND",
            )
        default_machine_image_ref = body.get("sourceMachineImage") or ""
        default_machine_image_name = normalize_name(default_machine_image_ref)
        if default_machine_image_name and default_machine_image_name not in self.state.machine_images:
            return create_gcp_error(
                404,
                f"Machine image '{default_machine_image_name}' not found",
                "NOT_FOUND",
            )

        names_in_batch: set[str] = set()
        for key, instance_body in instance_entries:
            instance_body = instance_body or {}
            name = instance_body.get("name") or key or self._generate_name()
            if name in self.resources or name in names_in_batch:
                return create_gcp_error(
                    409,
                    f"Instance '{name}' already exists",
                    "ALREADY_EXISTS",
                )
            names_in_batch.add(name)

            source_instance_template_ref = instance_body.get("sourceInstanceTemplate") or default_instance_template_ref
            source_instance_template_name = normalize_name(source_instance_template_ref)
            if source_instance_template_name and source_instance_template_name not in self.state.instance_templates:
                return create_gcp_error(
                    404,
                    f"Instance template '{source_instance_template_name}' not found",
                    "NOT_FOUND",
                )
            source_machine_image_ref = instance_body.get("sourceMachineImage") or default_machine_image_ref
            source_machine_image_name = normalize_name(source_machine_image_ref)
            if source_machine_image_name and source_machine_image_name not in self.state.machine_images:
                return create_gcp_error(
                    404,
                    f"Machine image '{source_machine_image_name}' not found",
                    "NOT_FOUND",
                )

            network_interfaces = instance_body.get("networkInterfaces") or []
            for interface in network_interfaces:
                network_ref = (interface or {}).get("network") or ""
                network_name = normalize_name(network_ref)
                if network_name and network_name not in self.state.networks:
                    return create_gcp_error(
                        404,
                        f"Network '{network_name}' not found",
                        "NOT_FOUND",
                    )
                subnetwork_ref = (interface or {}).get("subnetwork") or ""
                subnetwork_name = normalize_name(subnetwork_ref)
                if subnetwork_name and subnetwork_name not in self.state.subnetworks:
                    return create_gcp_error(
                        404,
                        f"Subnetwork '{subnetwork_name}' not found",
                        "NOT_FOUND",
                    )

            disks = instance_body.get("disks") or []
            attached_disk_names: List[str] = []
            for disk in disks:
                source_ref = (disk or {}).get("source") or ""
                source_name = normalize_name(source_ref)
                if source_name:
                    if source_name not in self.state.disks:
                        return create_gcp_error(
                            404,
                            f"Disk '{source_name}' not found",
                            "NOT_FOUND",
                        )
                    attached_disk_names.append(source_name)

            resource_policies = instance_body.get("resourcePolicies") or []
            for policy in resource_policies:
                policy_name = normalize_name(policy)
                if policy_name and policy_name not in self.state.resource_policies:
                    return create_gcp_error(
                        404,
                        f"Resource policy '{policy_name}' not found",
                        "NOT_FOUND",
                    )

            resource = Instance(
                params=instance_body.get("params") or {},
                confidential_instance_config=instance_body.get("confidentialInstanceConfig") or {},
                network_interfaces=network_interfaces,
                name=name,
                key_revocation_action_type=instance_body.get("keyRevocationActionType") or "",
                zone=zone,
                resource_status=instance_body.get("resourceStatus") or {},
                labels=instance_body.get("labels") or {},
                creation_timestamp=instance_body.get("creationTimestamp") or self._utcnow(),
                display_device=instance_body.get("displayDevice") or {},
                machine_type=instance_body.get("machineType") or "",
                instance_encryption_key=instance_body.get("instanceEncryptionKey") or {},
                status=instance_body.get("status") or "RUNNING",
                last_suspended_timestamp=instance_body.get("lastSuspendedTimestamp") or "",
                shielded_instance_config=instance_body.get("shieldedInstanceConfig") or {},
                source_machine_image=source_machine_image_ref or "",
                metadata=instance_body.get("metadata") or {},
                advanced_machine_features=instance_body.get("advancedMachineFeatures") or {},
                hostname=instance_body.get("hostname") or "",
                status_message=instance_body.get("statusMessage") or "",
                deletion_protection=bool(instance_body.get("deletionProtection"))
                if "deletionProtection" in instance_body
                else False,
                satisfies_pzi=bool(instance_body.get("satisfiesPzi")) if "satisfiesPzi" in instance_body else False,
                min_cpu_platform=instance_body.get("minCpuPlatform") or "",
                disks=disks,
                satisfies_pzs=bool(instance_body.get("satisfiesPzs")) if "satisfiesPzs" in instance_body else False,
                label_fingerprint=instance_body.get("labelFingerprint") or "",
                network_performance_config=instance_body.get("networkPerformanceConfig") or {},
                guest_accelerators=instance_body.get("guestAccelerators") or [],
                can_ip_forward=bool(instance_body.get("canIpForward")) if "canIpForward" in instance_body else False,
                source_machine_image_encryption_key=instance_body.get("sourceMachineImageEncryptionKey")
                or {},
                reservation_affinity=instance_body.get("reservationAffinity") or {},
                fingerprint=instance_body.get("fingerprint") or "",
                resource_policies=resource_policies,
                tags=instance_body.get("tags") or {},
                service_accounts=instance_body.get("serviceAccounts") or [],
                cpu_platform=instance_body.get("cpuPlatform") or "",
                last_stop_timestamp=instance_body.get("lastStopTimestamp") or "",
                start_restricted=bool(instance_body.get("startRestricted"))
                if "startRestricted" in instance_body
                else False,
                scheduling=instance_body.get("scheduling") or {},
                description=instance_body.get("description") or "",
                private_ipv6_google_access=instance_body.get("privateIpv6GoogleAccess") or "",
                last_start_timestamp=instance_body.get("lastStartTimestamp") or "",
                shielded_instance_integrity_policy=instance_body.get("shieldedInstanceIntegrityPolicy") or {},
                workload_identity_config=instance_body.get("workloadIdentityConfig") or {},
                id=self._generate_id(),
                iam_policy=instance_body.get("iamPolicy") or {},
                shielded_instance_identity=instance_body.get("shieldedInstanceIdentity") or {},
                attached_disk_names=attached_disk_names,
            )
            resource.label_fingerprint = str(uuid.uuid4())[:8]
            self.resources[resource.name] = resource

        resource_link = f"projects/{project}/zones/{zone}/instances"
        return make_operation(
            operation_type="bulkInsert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified Instance resource."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(instance_name)
        if not resource or resource.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def listReferrers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of resources that refer to the VM instance specified in
the request. For example, if the VM instance is part of a managed or
unmanaged instance group, the referrers list includes t..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        resource = self.resources.get(instance_name)
        if not resource or resource.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return {
            "kind": "compute#instanceList",
            "id": f"projects/{project}/zones/{zone}/instances/{instance_name}/referrers",
            "items": [],
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of instances contained within
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
        resources = self._filter_resources(params)
        return {
            "kind": "compute#instanceList",
            "id": f"projects/{project}/zones/{zone}/instances",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of all of the instances in your project
across all regions and zones.

The performance of this method degrades when a filter is specified on a
project that has a very l..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        resources = self._filter_resources(params)
        zone = params.get("zone") or "us-central1-a"
        scope_key = f"zones/{zone}"
        items: Dict[str, Any]
        if resources:
            items = {scope_key: {"instances": [resource.to_dict() for resource in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#instanceAggregatedList",
            "id": f"projects/{project}/aggregated/instances",
            "items": items,
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an instance only if the necessary resources are available. This
method can update only a specific set of instance properties. See
Updating a running instance for a list of updatable instanc..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("Instance") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'Instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        body_name = body.get("name")
        if body_name and body_name != instance.name:
            return create_gcp_error(
                400,
                "Instance name cannot be changed",
                "INVALID_ARGUMENT",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        if "sourceMachineImage" in body:
            source_machine_image_ref = body.get("sourceMachineImage") or ""
            source_machine_image_name = normalize_name(source_machine_image_ref)
            if source_machine_image_name and source_machine_image_name not in self.state.machine_images:
                return create_gcp_error(
                    404,
                    f"Machine image '{source_machine_image_name}' not found",
                    "NOT_FOUND",
                )
            instance.source_machine_image = source_machine_image_ref
        if "networkInterfaces" in body:
            network_interfaces = body.get("networkInterfaces") or []
            for interface in network_interfaces:
                network_ref = (interface or {}).get("network") or ""
                network_name = normalize_name(network_ref)
                if network_name and network_name not in self.state.networks:
                    return create_gcp_error(
                        404,
                        f"Network '{network_name}' not found",
                        "NOT_FOUND",
                    )
                subnetwork_ref = (interface or {}).get("subnetwork") or ""
                subnetwork_name = normalize_name(subnetwork_ref)
                if subnetwork_name and subnetwork_name not in self.state.subnetworks:
                    return create_gcp_error(
                        404,
                        f"Subnetwork '{subnetwork_name}' not found",
                        "NOT_FOUND",
                    )
            instance.network_interfaces = network_interfaces
        if "disks" in body:
            disks = body.get("disks") or []
            attached_disk_names: List[str] = []
            for disk in disks:
                source_ref = (disk or {}).get("source") or ""
                source_name = normalize_name(source_ref)
                if source_name:
                    if source_name not in self.state.disks:
                        return create_gcp_error(
                            404,
                            f"Disk '{source_name}' not found",
                            "NOT_FOUND",
                        )
                    attached_disk_names.append(source_name)
            instance.disks = disks
            instance.attached_disk_names = attached_disk_names
        if "resourcePolicies" in body:
            resource_policies = body.get("resourcePolicies") or []
            for policy in resource_policies:
                policy_name = normalize_name(policy)
                if policy_name and policy_name not in self.state.resource_policies:
                    return create_gcp_error(
                        404,
                        f"Resource policy '{policy_name}' not found",
                        "NOT_FOUND",
                    )
            instance.resource_policies = resource_policies
        if "labels" in body:
            instance.labels = body.get("labels") or {}
            instance.label_fingerprint = str(uuid.uuid4())[:8]
        if "params" in body:
            instance.params = body.get("params") or {}
        if "confidentialInstanceConfig" in body:
            instance.confidential_instance_config = body.get("confidentialInstanceConfig") or {}
        if "keyRevocationActionType" in body:
            instance.key_revocation_action_type = body.get("keyRevocationActionType") or ""
        if "resourceStatus" in body:
            instance.resource_status = body.get("resourceStatus") or {}
        if "creationTimestamp" in body:
            instance.creation_timestamp = body.get("creationTimestamp") or ""
        if "displayDevice" in body:
            instance.display_device = body.get("displayDevice") or {}
        if "machineType" in body:
            instance.machine_type = body.get("machineType") or ""
        if "instanceEncryptionKey" in body:
            instance.instance_encryption_key = body.get("instanceEncryptionKey") or {}
        if "status" in body:
            instance.status = body.get("status") or ""
        if "lastSuspendedTimestamp" in body:
            instance.last_suspended_timestamp = body.get("lastSuspendedTimestamp") or ""
        if "shieldedInstanceConfig" in body:
            instance.shielded_instance_config = body.get("shieldedInstanceConfig") or {}
        if "metadata" in body:
            instance.metadata = body.get("metadata") or {}
        if "advancedMachineFeatures" in body:
            instance.advanced_machine_features = body.get("advancedMachineFeatures") or {}
        if "hostname" in body:
            instance.hostname = body.get("hostname") or ""
        if "statusMessage" in body:
            instance.status_message = body.get("statusMessage") or ""
        if "deletionProtection" in body:
            instance.deletion_protection = bool(body.get("deletionProtection"))
        if "satisfiesPzi" in body:
            instance.satisfies_pzi = bool(body.get("satisfiesPzi"))
        if "minCpuPlatform" in body:
            instance.min_cpu_platform = body.get("minCpuPlatform") or ""
        if "satisfiesPzs" in body:
            instance.satisfies_pzs = bool(body.get("satisfiesPzs"))
        if "networkPerformanceConfig" in body:
            instance.network_performance_config = body.get("networkPerformanceConfig") or {}
        if "guestAccelerators" in body:
            instance.guest_accelerators = body.get("guestAccelerators") or []
        if "canIpForward" in body:
            instance.can_ip_forward = bool(body.get("canIpForward"))
        if "sourceMachineImageEncryptionKey" in body:
            instance.source_machine_image_encryption_key = body.get("sourceMachineImageEncryptionKey") or {}
        if "reservationAffinity" in body:
            instance.reservation_affinity = body.get("reservationAffinity") or {}
        if "fingerprint" in body:
            instance.fingerprint = body.get("fingerprint") or ""
        if "tags" in body:
            instance.tags = body.get("tags") or {}
        if "serviceAccounts" in body:
            instance.service_accounts = body.get("serviceAccounts") or []
        if "cpuPlatform" in body:
            instance.cpu_platform = body.get("cpuPlatform") or ""
        if "lastStopTimestamp" in body:
            instance.last_stop_timestamp = body.get("lastStopTimestamp") or ""
        if "startRestricted" in body:
            instance.start_restricted = bool(body.get("startRestricted"))
        if "scheduling" in body:
            instance.scheduling = body.get("scheduling") or {}
        if "description" in body:
            instance.description = body.get("description") or ""
        if "privateIpv6GoogleAccess" in body:
            instance.private_ipv6_google_access = body.get("privateIpv6GoogleAccess") or ""
        if "lastStartTimestamp" in body:
            instance.last_start_timestamp = body.get("lastStartTimestamp") or ""
        if "shieldedInstanceIntegrityPolicy" in body:
            instance.shielded_instance_integrity_policy = body.get("shieldedInstanceIntegrityPolicy") or {}
        if "workloadIdentityConfig" in body:
            instance.workload_identity_config = body.get("workloadIdentityConfig") or {}
        if "iamPolicy" in body:
            instance.iam_policy = body.get("iamPolicy") or {}
        if "shieldedInstanceIdentity" in body:
            instance.shielded_instance_identity = body.get("shieldedInstanceIdentity") or {}

        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="update",
            resource_link=resource_link,
            params=params,
        )

    def setMetadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets metadata for the specified instance to the data included
in the request."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        metadata = params.get("Metadata") or {}
        if not metadata:
            return create_gcp_error(
                400,
                "Required field 'Metadata' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.metadata = metadata
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setMetadata",
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
        body = params.get("ZoneSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ZoneSetPolicyRequest' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(resource_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{resource_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.iam_policy = body.get("policy") or {}
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=resource_link,
            params=params,
        )

    def setTags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets network tags
for the specified instance to the data included in the request."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        tags = params.get("Tags") or {}
        if not tags:
            return create_gcp_error(
                400,
                "Required field 'Tags' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.tags = tags
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setTags",
            resource_link=resource_link,
            params=params,
        )

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets labels on an instance.  To learn more about labels, read theLabeling
Resources documentation."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesSetLabelsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesSetLabelsRequest' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.labels = body.get("labels") or {}
        instance.label_fingerprint = str(uuid.uuid4())[:8]
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setLabels",
            resource_link=resource_link,
            params=params,
        )

    def setDeletionProtection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets deletion protection on the instance."""
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
        instance = self.resources.get(resource_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{resource_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        deletion_protection = params.get("deletionProtection")
        if deletion_protection is not None:
            instance.deletion_protection = bool(deletion_protection)
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setDeletionProtection",
            resource_link=resource_link,
            params=params,
        )

    def startWithEncryptionKey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Starts an instance that was stopped using theinstances().stop
method. For more information, seeRestart an
instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesStartWithEncryptionKeyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesStartWithEncryptionKeyRequest' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.status = "RUNNING"
        instance.last_start_timestamp = self._utcnow()
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="startWithEncryptionKey",
            resource_link=resource_link,
            params=params,
        )

    def setScheduling(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets an instance's scheduling options. You can only call this method on astopped instance,
that is, a VM instance that is in a `TERMINATED` state. SeeInstance Life
Cycle for more information on the..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        scheduling = params.get("Scheduling") or {}
        if not scheduling:
            return create_gcp_error(
                400,
                "Required field 'Scheduling' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.status and instance.status.upper() != "TERMINATED":
            return create_gcp_error(
                400,
                "Instance must be in TERMINATED state",
                "FAILED_PRECONDITION",
            )
        instance.scheduling = scheduling
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setScheduling",
            resource_link=resource_link,
            params=params,
        )

    def updateDisplayDevice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the Display config for a VM instance. You can
only use this method on a stopped VM instance. This method supportsPATCH
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        display_device = params.get("DisplayDevice") or {}
        if not display_device:
            return create_gcp_error(
                400,
                "Required field 'DisplayDevice' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.status and instance.status.upper() != "TERMINATED":
            return create_gcp_error(
                400,
                "Instance must be in TERMINATED state",
                "FAILED_PRECONDITION",
            )
        instance.display_device.update(display_device)
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="updateDisplayDevice",
            resource_link=resource_link,
            params=params,
        )

    def reset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a reset on the instance. This is a hard reset. The VM
does not do a graceful shutdown. For more information, seeResetting
an instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.status = "RUNNING"
        instance.last_start_timestamp = self._utcnow()
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="reset",
            resource_link=resource_link,
            params=params,
        )

    def setServiceAccount(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the service account on the instance. For more information,
readChanging
the service account and access scopes for an instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesSetServiceAccountRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesSetServiceAccountRequest' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        email = body.get("email")
        scopes = body.get("scopes") or []
        if email:
            instance.service_accounts = [{"email": email, "scopes": scopes}]
        else:
            instance.service_accounts = []
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setServiceAccount",
            resource_link=resource_link,
            params=params,
        )

    def resume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resumes an instance that was suspended using theinstances().suspend
method."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.status = "RUNNING"
        instance.last_start_timestamp = self._utcnow()
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="resume",
            resource_link=resource_link,
            params=params,
        )

    def detachDisk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detaches a disk from an instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        device_name = params.get("deviceName")
        if not device_name:
            return create_gcp_error(
                400,
                "Required field 'deviceName' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        disks = instance.disks or []
        updated_disks = [disk for disk in disks if (disk or {}).get("deviceName") != device_name]
        if len(updated_disks) == len(disks):
            return create_gcp_error(
                404,
                f"Disk '{device_name}' not found",
                "NOT_FOUND",
            )
        instance.disks = updated_disks
        instance.attached_disk_names = [
            name for name in instance.attached_disk_names if name != device_name
        ]
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="detachDisk",
            resource_link=resource_link,
            params=params,
        )

    def getShieldedInstanceIdentity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the Shielded Instance Identity of an instance"""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return instance.shielded_instance_identity or {}

    def setName(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets name of an instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesSetNameRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesSetNameRequest' not found",
                "INVALID_ARGUMENT",
            )
        new_name = body.get("name")
        if not new_name:
            return create_gcp_error(
                400,
                "Required field 'name' not found",
                "INVALID_ARGUMENT",
            )
        if new_name in self.resources:
            return create_gcp_error(
                409,
                f"Instance '{new_name}' already exists",
                "ALREADY_EXISTS",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        self.resources.pop(instance_name, None)
        instance.name = new_name
        self.resources[new_name] = instance
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setName",
            resource_link=resource_link,
            params=params,
        )

    def addAccessConfig(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds an access config to an instance's network interface."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        network_interface_name = params.get("networkInterface")
        if not network_interface_name:
            return create_gcp_error(
                400,
                "Required field 'networkInterface' not found",
                "INVALID_ARGUMENT",
            )
        access_config = params.get("AccessConfig") or {}
        if not access_config:
            return create_gcp_error(
                400,
                "Required field 'AccessConfig' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        interfaces = instance.network_interfaces or []
        target_interface = None
        for interface in interfaces:
            if (interface or {}).get("name") == network_interface_name:
                target_interface = interface
                break
        if not target_interface:
            return create_gcp_error(
                404,
                f"Network interface '{network_interface_name}' not found",
                "NOT_FOUND",
            )
        access_configs = target_interface.get("accessConfigs") or []
        access_configs.append(access_config)
        target_interface["accessConfigs"] = access_configs
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="addAccessConfig",
            resource_link=resource_link,
            params=params,
        )

    def addNetworkInterface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds one dynamic network interface to an active instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        network_interface = params.get("NetworkInterface") or {}
        if not network_interface:
            return create_gcp_error(
                400,
                "Required field 'NetworkInterface' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        network_ref = network_interface.get("network") or ""
        network_name = normalize_name(network_ref)
        if network_name and network_name not in self.state.networks:
            return create_gcp_error(
                404,
                f"Network '{network_name}' not found",
                "NOT_FOUND",
            )
        subnetwork_ref = network_interface.get("subnetwork") or ""
        subnetwork_name = normalize_name(subnetwork_ref)
        if subnetwork_name and subnetwork_name not in self.state.subnetworks:
            return create_gcp_error(
                404,
                f"Subnetwork '{subnetwork_name}' not found",
                "NOT_FOUND",
            )

        instance.network_interfaces = instance.network_interfaces or []
        instance.network_interfaces.append(network_interface)
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="addNetworkInterface",
            resource_link=resource_link,
            params=params,
        )

    def getScreenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the screenshot from the specified instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return {
            "kind": "compute#screenshot",
            "contents": "",
        }

    def suspend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """This method suspends a running instance, saving its state to persistent
storage, and allows you to resume the instance at a later time. Suspended
instances have no compute costs (cores or RAM), and..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.status = "SUSPENDED"
        instance.last_suspended_timestamp = self._utcnow()
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="suspend",
            resource_link=resource_link,
            params=params,
        )

    def getSerialPortOutput(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the last 1 MB of serial port output from the specified instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return {
            "kind": "compute#serialPortOutput",
            "contents": "",
            "start": params.get("start") or "0",
        }

    def deleteAccessConfig(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes an access config from an instance's network interface."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        access_config_name = params.get("accessConfig")
        if not access_config_name:
            return create_gcp_error(
                400,
                "Required field 'accessConfig' not found",
                "INVALID_ARGUMENT",
            )
        network_interface_name = params.get("networkInterface")
        if not network_interface_name:
            return create_gcp_error(
                400,
                "Required field 'networkInterface' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        interfaces = instance.network_interfaces or []
        target_interface = None
        for interface in interfaces:
            if (interface or {}).get("name") == network_interface_name:
                target_interface = interface
                break
        if not target_interface:
            return create_gcp_error(
                404,
                f"Network interface '{network_interface_name}' not found",
                "NOT_FOUND",
            )
        access_configs = target_interface.get("accessConfigs") or []
        filtered_configs = [
            config
            for config in access_configs
            if (config or {}).get("name") != access_config_name
        ]
        if len(filtered_configs) == len(access_configs):
            return create_gcp_error(
                404,
                f"Access config '{access_config_name}' not found",
                "NOT_FOUND",
            )
        target_interface["accessConfigs"] = filtered_configs
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="deleteAccessConfig",
            resource_link=resource_link,
            params=params,
        )

    def updateShieldedInstanceConfig(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the Shielded Instance config for an instance. You can
only use this method on a stopped instance. This method supportsPATCH
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        shielded_config = params.get("ShieldedInstanceConfig") or {}
        if not shielded_config:
            return create_gcp_error(
                400,
                "Required field 'ShieldedInstanceConfig' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.status and instance.status.upper() != "TERMINATED":
            return create_gcp_error(
                400,
                "Instance must be in TERMINATED state",
                "FAILED_PRECONDITION",
            )
        instance.shielded_instance_config.update(shielded_config)
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="updateShieldedInstanceConfig",
            resource_link=resource_link,
            params=params,
        )

    def attachDisk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Attaches an existing Disk resource to an instance. You must first
create the disk before you can attach it. It is not possible to create
and attach a disk at the same time. For more information, re..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        attached_disk = params.get("AttachedDisk") or {}
        if not attached_disk:
            return create_gcp_error(
                400,
                "Required field 'AttachedDisk' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        source_ref = attached_disk.get("source") or ""
        source_name = normalize_name(source_ref)
        if source_name and source_name not in self.state.disks:
            return create_gcp_error(
                404,
                f"Disk '{source_name}' not found",
                "NOT_FOUND",
            )
        instance.disks = instance.disks or []
        instance.disks.append(attached_disk)
        if source_name:
            instance.attached_disk_names.append(source_name)
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="attachDisk",
            resource_link=resource_link,
            params=params,
        )

    def setDiskAutoDelete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the auto-delete flag for a disk attached to an instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        if "autoDelete" not in params:
            return create_gcp_error(
                400,
                "Required field 'autoDelete' not found",
                "INVALID_ARGUMENT",
            )
        device_name = params.get("deviceName")
        if not device_name:
            return create_gcp_error(
                400,
                "Required field 'deviceName' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        disks = instance.disks or []
        updated = False
        for disk in disks:
            if (disk or {}).get("deviceName") == device_name:
                disk["autoDelete"] = bool(params.get("autoDelete"))
                updated = True
                break
        if not updated:
            return create_gcp_error(
                404,
                f"Disk '{device_name}' not found",
                "NOT_FOUND",
            )
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setDiskAutoDelete",
            resource_link=resource_link,
            params=params,
        )

    def reportHostAsFaulty(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mark the host as faulty and try to restart the instance on a new host."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesReportHostAsFaultyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesReportHostAsFaultyRequest' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.status = "RUNNING"
        instance.last_start_timestamp = self._utcnow()
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="reportHostAsFaulty",
            resource_link=resource_link,
            params=params,
        )

    def sendDiagnosticInterrupt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sends diagnostic interrupt to the instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return {
            "kind": "compute#sendDiagnosticInterrupt",
        }

    def addResourcePolicies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds existing resource policies to an instance. You can only add one
policy right now which will be applied to this instance for scheduling live
migrations."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesAddResourcePoliciesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesAddResourcePoliciesRequest' not found",
                "INVALID_ARGUMENT",
            )
        policies = body.get("resourcePolicies") or []
        if not policies:
            return create_gcp_error(
                400,
                "Required field 'resourcePolicies' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        for policy in policies:
            policy_name = normalize_name(policy)
            if policy_name and policy_name not in self.state.resource_policies:
                return create_gcp_error(
                    404,
                    f"Resource policy '{policy_name}' not found",
                    "NOT_FOUND",
                )
        instance.resource_policies = list({*instance.resource_policies, *policies})
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="addResourcePolicies",
            resource_link=resource_link,
            params=params,
        )

    def setShieldedInstanceIntegrityPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the Shielded Instance integrity policy for an instance. You can
only use this method on a running instance. This method
supports PATCH semantics and uses the JSON merge
patch format and proces..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        policy = params.get("ShieldedInstanceIntegrityPolicy") or {}
        if not policy:
            return create_gcp_error(
                400,
                "Required field 'ShieldedInstanceIntegrityPolicy' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.status and instance.status.upper() != "RUNNING":
            return create_gcp_error(
                400,
                "Instance must be in RUNNING state",
                "FAILED_PRECONDITION",
            )
        instance.shielded_instance_integrity_policy.update(policy)
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setShieldedInstanceIntegrityPolicy",
            resource_link=resource_link,
            params=params,
        )

    def performMaintenance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a manual maintenance on the instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="performMaintenance",
            resource_link=resource_link,
            params=params,
        )

    def updateNetworkInterface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an instance's network interface. This method can only update an
interface's alias IP range and attached network. See Modifying
alias IP ranges for an existing instance for instructions on
c..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        network_interface_name = params.get("networkInterface")
        if not network_interface_name:
            return create_gcp_error(
                400,
                "Required field 'networkInterface' not found",
                "INVALID_ARGUMENT",
            )
        network_interface = params.get("NetworkInterface") or {}
        if not network_interface:
            return create_gcp_error(
                400,
                "Required field 'NetworkInterface' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        network_ref = network_interface.get("network")
        if network_ref is not None:
            network_name = normalize_name(network_ref)
            if network_name and network_name not in self.state.networks:
                return create_gcp_error(
                    404,
                    f"Network '{network_name}' not found",
                    "NOT_FOUND",
                )
        subnetwork_ref = network_interface.get("subnetwork")
        if subnetwork_ref is not None:
            subnetwork_name = normalize_name(subnetwork_ref)
            if subnetwork_name and subnetwork_name not in self.state.subnetworks:
                return create_gcp_error(
                    404,
                    f"Subnetwork '{subnetwork_name}' not found",
                    "NOT_FOUND",
                )
        interfaces = instance.network_interfaces or []
        target_interface = None
        for interface in interfaces:
            if (interface or {}).get("name") == network_interface_name:
                target_interface = interface
                break
        if not target_interface:
            return create_gcp_error(
                404,
                f"Network interface '{network_interface_name}' not found",
                "NOT_FOUND",
            )
        target_interface.update(network_interface)
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="updateNetworkInterface",
            resource_link=resource_link,
            params=params,
        )

    def deleteNetworkInterface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes one dynamic network interface from an active instance.
InstancesDeleteNetworkInterfaceRequest indicates:
- instance from which to delete, using project+zone+resource_id fields;
- dynamic ne..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        network_interface_name = params.get("networkInterfaceName")
        if not network_interface_name:
            return create_gcp_error(
                400,
                "Required field 'networkInterfaceName' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        interfaces = instance.network_interfaces or []
        updated_interfaces = [
            interface
            for interface in interfaces
            if (interface or {}).get("name") != network_interface_name
        ]
        if len(updated_interfaces) == len(interfaces):
            return create_gcp_error(
                404,
                f"Network interface '{network_interface_name}' not found",
                "NOT_FOUND",
            )
        instance.network_interfaces = updated_interfaces
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="deleteNetworkInterface",
            resource_link=resource_link,
            params=params,
        )

    def setMachineType(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the machine type for a stopped instance to the machine
type specified in the request."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesSetMachineTypeRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesSetMachineTypeRequest' not found",
                "INVALID_ARGUMENT",
            )
        machine_type = body.get("machineType")
        if not machine_type:
            return create_gcp_error(
                400,
                "Required field 'machineType' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.status and instance.status.upper() != "TERMINATED":
            return create_gcp_error(
                400,
                "Instance must be in TERMINATED state",
                "FAILED_PRECONDITION",
            )
        instance.machine_type = machine_type
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setMachineType",
            resource_link=resource_link,
            params=params,
        )

    def updateAccessConfig(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified access config from an instance's network interface
with the data included in the request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processin..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        network_interface_name = params.get("networkInterface")
        if not network_interface_name:
            return create_gcp_error(
                400,
                "Required field 'networkInterface' not found",
                "INVALID_ARGUMENT",
            )
        access_config = params.get("AccessConfig") or {}
        if not access_config:
            return create_gcp_error(
                400,
                "Required field 'AccessConfig' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        interfaces = instance.network_interfaces or []
        target_interface = None
        for interface in interfaces:
            if (interface or {}).get("name") == network_interface_name:
                target_interface = interface
                break
        if not target_interface:
            return create_gcp_error(
                404,
                f"Network interface '{network_interface_name}' not found",
                "NOT_FOUND",
            )
        access_configs = target_interface.get("accessConfigs") or []
        updated = False
        access_config_name = access_config.get("name")
        for idx, config in enumerate(access_configs):
            if access_config_name and (config or {}).get("name") == access_config_name:
                access_configs[idx] = {**config, **access_config}
                updated = True
                break
        if not updated:
            access_configs.append(access_config)
        target_interface["accessConfigs"] = access_configs
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="updateAccessConfig",
            resource_link=resource_link,
            params=params,
        )

    def setSecurityPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the Google Cloud Armor security policy for the specified instance.
For more information, seeGoogle
Cloud Armor Overview"""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesSetSecurityPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesSetSecurityPolicyRequest' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.resource_status = instance.resource_status or {}
        instance.resource_status["securityPolicy"] = body.get("securityPolicy")
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setSecurityPolicy",
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
        instance = self.resources.get(resource_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{resource_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return instance.iam_policy or {}

    def getGuestAttributes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified guest attributes entry."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return {
            "kind": "compute#guestAttributes",
            "queryPath": params.get("queryPath") or "",
            "variableKey": params.get("variableKey") or "",
            "items": {},
        }

    def removeResourcePolicies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Removes resource policies from an instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesRemoveResourcePoliciesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesRemoveResourcePoliciesRequest' not found",
                "INVALID_ARGUMENT",
            )
        policies = body.get("resourcePolicies") or []
        if not policies:
            return create_gcp_error(
                400,
                "Required field 'resourcePolicies' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        for policy in policies:
            policy_name = normalize_name(policy)
            if policy_name and policy_name not in self.state.resource_policies:
                return create_gcp_error(
                    404,
                    f"Resource policy '{policy_name}' not found",
                    "NOT_FOUND",
                )
        instance.resource_policies = [
            policy for policy in instance.resource_policies if policy not in policies
        ]
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="removeResourcePolicies",
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
        instance = self.resources.get(resource_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{resource_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        permissions = body.get("permissions") or []
        return {
            "permissions": permissions,
        }

    def start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Starts an instance that was stopped using theinstances().stop
method. For more information, seeRestart an
instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.status = "RUNNING"
        instance.last_start_timestamp = self._utcnow()
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="start",
            resource_link=resource_link,
            params=params,
        )

    def simulateMaintenanceEvent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates a host maintenance event on a VM. For more information, see
Simulate a host maintenance event."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="simulateMaintenanceEvent",
            resource_link=resource_link,
            params=params,
        )

    def setMachineResources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the number and/or type of accelerator for a stopped instance to the
values specified in the request."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesSetMachineResourcesRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesSetMachineResourcesRequest' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.status and instance.status.upper() != "TERMINATED":
            return create_gcp_error(
                400,
                "Instance must be in TERMINATED state",
                "FAILED_PRECONDITION",
            )
        if "guestAccelerators" in body:
            instance.guest_accelerators = body.get("guestAccelerators") or []
        if "machineType" in body:
            instance.machine_type = body.get("machineType") or instance.machine_type
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setMachineResources",
            resource_link=resource_link,
            params=params,
        )

    def stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stops a running instance, shutting it down cleanly, and allows
you to restart the instance at a later time. Stopped instances do not incur
VM usage charges while they are stopped. However, resource..."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        instance.status = "TERMINATED"
        instance.last_stop_timestamp = self._utcnow()
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="stop",
            resource_link=resource_link,
            params=params,
        )

    def setMinCpuPlatform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Changes the minimum CPU platform that this instance should use.
This method can only
be called on a stopped instance. For more information, readSpecifying a
Minimum CPU Platform."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("InstancesSetMinCpuPlatformRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstancesSetMinCpuPlatformRequest' not found",
                "INVALID_ARGUMENT",
            )
        min_cpu_platform = body.get("minCpuPlatform")
        if not min_cpu_platform:
            return create_gcp_error(
                400,
                "Required field 'minCpuPlatform' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.status and instance.status.upper() != "TERMINATED":
            return create_gcp_error(
                400,
                "Instance must be in TERMINATED state",
                "FAILED_PRECONDITION",
            )
        instance.min_cpu_platform = min_cpu_platform
        resource_link = f"projects/{project}/zones/{zone}/instances/{instance.name}"
        return make_operation(
            operation_type="setMinCpuPlatform",
            resource_link=resource_link,
            params=params,
        )

    def getEffectiveFirewalls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns effective firewalls applied to an interface of the instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        network_interface_name = params.get("networkInterface")
        if not network_interface_name:
            return create_gcp_error(
                400,
                "Required field 'networkInterface' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        interfaces = instance.network_interfaces or []
        interface_found = any(
            (interface or {}).get("name") == network_interface_name
            for interface in interfaces
        )
        if not interface_found:
            return create_gcp_error(
                404,
                f"Network interface '{network_interface_name}' not found",
                "NOT_FOUND",
            )
        return {
            "kind": "compute#instancesGetEffectiveFirewallsResponse",
            "firewalls": [],
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified Instance resource. For more information, seeDeleting
an instance."""
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
        instance_name = params.get("instance")
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        instance = self.resources.get(instance_name)
        if not instance or instance.zone != zone:
            resource_path = f"projects/{project}/zones/{zone}/instances/{instance_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        if instance.deletion_protection:
            return create_gcp_error(
                400,
                "Instance has deletion protection enabled",
                "FAILED_PRECONDITION",
            )
        self.resources.pop(instance_name, None)
        resource_link = f"projects/{project}/zones/{zone}/Instances/{instance_name}"
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class instance_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setDeletionProtection': instance_RequestParser._parse_setDeletionProtection,
            'startWithEncryptionKey': instance_RequestParser._parse_startWithEncryptionKey,
            'setScheduling': instance_RequestParser._parse_setScheduling,
            'insert': instance_RequestParser._parse_insert,
            'updateDisplayDevice': instance_RequestParser._parse_updateDisplayDevice,
            'get': instance_RequestParser._parse_get,
            'reset': instance_RequestParser._parse_reset,
            'setServiceAccount': instance_RequestParser._parse_setServiceAccount,
            'resume': instance_RequestParser._parse_resume,
            'detachDisk': instance_RequestParser._parse_detachDisk,
            'getShieldedInstanceIdentity': instance_RequestParser._parse_getShieldedInstanceIdentity,
            'setName': instance_RequestParser._parse_setName,
            'update': instance_RequestParser._parse_update,
            'addAccessConfig': instance_RequestParser._parse_addAccessConfig,
            'addNetworkInterface': instance_RequestParser._parse_addNetworkInterface,
            'getScreenshot': instance_RequestParser._parse_getScreenshot,
            'suspend': instance_RequestParser._parse_suspend,
            'delete': instance_RequestParser._parse_delete,
            'getSerialPortOutput': instance_RequestParser._parse_getSerialPortOutput,
            'listReferrers': instance_RequestParser._parse_listReferrers,
            'deleteAccessConfig': instance_RequestParser._parse_deleteAccessConfig,
            'updateShieldedInstanceConfig': instance_RequestParser._parse_updateShieldedInstanceConfig,
            'attachDisk': instance_RequestParser._parse_attachDisk,
            'setDiskAutoDelete': instance_RequestParser._parse_setDiskAutoDelete,
            'reportHostAsFaulty': instance_RequestParser._parse_reportHostAsFaulty,
            'list': instance_RequestParser._parse_list,
            'bulkInsert': instance_RequestParser._parse_bulkInsert,
            'sendDiagnosticInterrupt': instance_RequestParser._parse_sendDiagnosticInterrupt,
            'addResourcePolicies': instance_RequestParser._parse_addResourcePolicies,
            'aggregatedList': instance_RequestParser._parse_aggregatedList,
            'setShieldedInstanceIntegrityPolicy': instance_RequestParser._parse_setShieldedInstanceIntegrityPolicy,
            'performMaintenance': instance_RequestParser._parse_performMaintenance,
            'updateNetworkInterface': instance_RequestParser._parse_updateNetworkInterface,
            'setMetadata': instance_RequestParser._parse_setMetadata,
            'deleteNetworkInterface': instance_RequestParser._parse_deleteNetworkInterface,
            'setMachineType': instance_RequestParser._parse_setMachineType,
            'updateAccessConfig': instance_RequestParser._parse_updateAccessConfig,
            'setSecurityPolicy': instance_RequestParser._parse_setSecurityPolicy,
            'getIamPolicy': instance_RequestParser._parse_getIamPolicy,
            'getGuestAttributes': instance_RequestParser._parse_getGuestAttributes,
            'removeResourcePolicies': instance_RequestParser._parse_removeResourcePolicies,
            'setIamPolicy': instance_RequestParser._parse_setIamPolicy,
            'testIamPermissions': instance_RequestParser._parse_testIamPermissions,
            'start': instance_RequestParser._parse_start,
            'simulateMaintenanceEvent': instance_RequestParser._parse_simulateMaintenanceEvent,
            'setMachineResources': instance_RequestParser._parse_setMachineResources,
            'stop': instance_RequestParser._parse_stop,
            'setTags': instance_RequestParser._parse_setTags,
            'setLabels': instance_RequestParser._parse_setLabels,
            'setMinCpuPlatform': instance_RequestParser._parse_setMinCpuPlatform,
            'getEffectiveFirewalls': instance_RequestParser._parse_getEffectiveFirewalls,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_setDeletionProtection(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'deletionProtection' in query_params:
            params['deletionProtection'] = query_params['deletionProtection']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_startWithEncryptionKey(
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
        params['InstancesStartWithEncryptionKeyRequest'] = body.get('InstancesStartWithEncryptionKeyRequest')
        return params

    @staticmethod
    def _parse_setScheduling(
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
        params['Scheduling'] = body.get('Scheduling')
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
        if 'sourceInstanceTemplate' in query_params:
            params['sourceInstanceTemplate'] = query_params['sourceInstanceTemplate']
        if 'sourceMachineImage' in query_params:
            params['sourceMachineImage'] = query_params['sourceMachineImage']
        # Body params
        params['Instance'] = body.get('Instance')
        return params

    @staticmethod
    def _parse_updateDisplayDevice(
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
        params['DisplayDevice'] = body.get('DisplayDevice')
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
    def _parse_reset(
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
    def _parse_setServiceAccount(
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
        params['InstancesSetServiceAccountRequest'] = body.get('InstancesSetServiceAccountRequest')
        return params

    @staticmethod
    def _parse_resume(
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
    def _parse_detachDisk(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'deviceName' in query_params:
            params['deviceName'] = query_params['deviceName']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_getShieldedInstanceIdentity(
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
    def _parse_setName(
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
        params['InstancesSetNameRequest'] = body.get('InstancesSetNameRequest')
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
        if 'minimalAction' in query_params:
            params['minimalAction'] = query_params['minimalAction']
        if 'mostDisruptiveAllowedAction' in query_params:
            params['mostDisruptiveAllowedAction'] = query_params['mostDisruptiveAllowedAction']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['Instance'] = body.get('Instance')
        return params

    @staticmethod
    def _parse_addAccessConfig(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'networkInterface' in query_params:
            params['networkInterface'] = query_params['networkInterface']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['AccessConfig'] = body.get('AccessConfig')
        return params

    @staticmethod
    def _parse_addNetworkInterface(
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
        params['NetworkInterface'] = body.get('NetworkInterface')
        return params

    @staticmethod
    def _parse_getScreenshot(
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
    def _parse_suspend(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'discardLocalSsd' in query_params:
            params['discardLocalSsd'] = query_params['discardLocalSsd']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
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
    def _parse_getSerialPortOutput(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'port' in query_params:
            params['port'] = query_params['port']
        if 'start' in query_params:
            params['start'] = query_params['start']
        return params

    @staticmethod
    def _parse_listReferrers(
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
    def _parse_deleteAccessConfig(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'accessConfig' in query_params:
            params['accessConfig'] = query_params['accessConfig']
        if 'networkInterface' in query_params:
            params['networkInterface'] = query_params['networkInterface']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_updateShieldedInstanceConfig(
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
        params['ShieldedInstanceConfig'] = body.get('ShieldedInstanceConfig')
        return params

    @staticmethod
    def _parse_attachDisk(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'forceAttach' in query_params:
            params['forceAttach'] = query_params['forceAttach']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['AttachedDisk'] = body.get('AttachedDisk')
        return params

    @staticmethod
    def _parse_setDiskAutoDelete(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'autoDelete' in query_params:
            params['autoDelete'] = query_params['autoDelete']
        if 'deviceName' in query_params:
            params['deviceName'] = query_params['deviceName']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_reportHostAsFaulty(
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
        params['InstancesReportHostAsFaultyRequest'] = body.get('InstancesReportHostAsFaultyRequest')
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
    def _parse_bulkInsert(
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
        params['BulkInsertInstanceResource'] = body.get('BulkInsertInstanceResource')
        return params

    @staticmethod
    def _parse_sendDiagnosticInterrupt(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_addResourcePolicies(
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
        params['InstancesAddResourcePoliciesRequest'] = body.get('InstancesAddResourcePoliciesRequest')
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
    def _parse_setShieldedInstanceIntegrityPolicy(
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
        params['ShieldedInstanceIntegrityPolicy'] = body.get('ShieldedInstanceIntegrityPolicy')
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
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_updateNetworkInterface(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'networkInterface' in query_params:
            params['networkInterface'] = query_params['networkInterface']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['NetworkInterface'] = body.get('NetworkInterface')
        return params

    @staticmethod
    def _parse_setMetadata(
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
    def _parse_deleteNetworkInterface(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'networkInterfaceName' in query_params:
            params['networkInterfaceName'] = query_params['networkInterfaceName']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_setMachineType(
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
        params['InstancesSetMachineTypeRequest'] = body.get('InstancesSetMachineTypeRequest')
        return params

    @staticmethod
    def _parse_updateAccessConfig(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'networkInterface' in query_params:
            params['networkInterface'] = query_params['networkInterface']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['AccessConfig'] = body.get('AccessConfig')
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
        params['InstancesSetSecurityPolicyRequest'] = body.get('InstancesSetSecurityPolicyRequest')
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
    def _parse_getGuestAttributes(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'queryPath' in query_params:
            params['queryPath'] = query_params['queryPath']
        if 'variableKey' in query_params:
            params['variableKey'] = query_params['variableKey']
        return params

    @staticmethod
    def _parse_removeResourcePolicies(
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
        params['InstancesRemoveResourcePoliciesRequest'] = body.get('InstancesRemoveResourcePoliciesRequest')
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
    def _parse_start(
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
        if 'withExtendedNotifications' in query_params:
            params['withExtendedNotifications'] = query_params['withExtendedNotifications']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_setMachineResources(
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
        params['InstancesSetMachineResourcesRequest'] = body.get('InstancesSetMachineResourcesRequest')
        return params

    @staticmethod
    def _parse_stop(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'discardLocalSsd' in query_params:
            params['discardLocalSsd'] = query_params['discardLocalSsd']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_setTags(
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
        params['Tags'] = body.get('Tags')
        return params

    @staticmethod
    def _parse_setLabels(
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
        params['InstancesSetLabelsRequest'] = body.get('InstancesSetLabelsRequest')
        return params

    @staticmethod
    def _parse_setMinCpuPlatform(
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
        params['InstancesSetMinCpuPlatformRequest'] = body.get('InstancesSetMinCpuPlatformRequest')
        return params

    @staticmethod
    def _parse_getEffectiveFirewalls(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'networkInterface' in query_params:
            params['networkInterface'] = query_params['networkInterface']
        return params


class instance_ResponseSerializer:
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
            'setDeletionProtection': instance_ResponseSerializer._serialize_setDeletionProtection,
            'startWithEncryptionKey': instance_ResponseSerializer._serialize_startWithEncryptionKey,
            'setScheduling': instance_ResponseSerializer._serialize_setScheduling,
            'insert': instance_ResponseSerializer._serialize_insert,
            'updateDisplayDevice': instance_ResponseSerializer._serialize_updateDisplayDevice,
            'get': instance_ResponseSerializer._serialize_get,
            'reset': instance_ResponseSerializer._serialize_reset,
            'setServiceAccount': instance_ResponseSerializer._serialize_setServiceAccount,
            'resume': instance_ResponseSerializer._serialize_resume,
            'detachDisk': instance_ResponseSerializer._serialize_detachDisk,
            'getShieldedInstanceIdentity': instance_ResponseSerializer._serialize_getShieldedInstanceIdentity,
            'setName': instance_ResponseSerializer._serialize_setName,
            'update': instance_ResponseSerializer._serialize_update,
            'addAccessConfig': instance_ResponseSerializer._serialize_addAccessConfig,
            'addNetworkInterface': instance_ResponseSerializer._serialize_addNetworkInterface,
            'getScreenshot': instance_ResponseSerializer._serialize_getScreenshot,
            'suspend': instance_ResponseSerializer._serialize_suspend,
            'delete': instance_ResponseSerializer._serialize_delete,
            'getSerialPortOutput': instance_ResponseSerializer._serialize_getSerialPortOutput,
            'listReferrers': instance_ResponseSerializer._serialize_listReferrers,
            'deleteAccessConfig': instance_ResponseSerializer._serialize_deleteAccessConfig,
            'updateShieldedInstanceConfig': instance_ResponseSerializer._serialize_updateShieldedInstanceConfig,
            'attachDisk': instance_ResponseSerializer._serialize_attachDisk,
            'setDiskAutoDelete': instance_ResponseSerializer._serialize_setDiskAutoDelete,
            'reportHostAsFaulty': instance_ResponseSerializer._serialize_reportHostAsFaulty,
            'list': instance_ResponseSerializer._serialize_list,
            'bulkInsert': instance_ResponseSerializer._serialize_bulkInsert,
            'sendDiagnosticInterrupt': instance_ResponseSerializer._serialize_sendDiagnosticInterrupt,
            'addResourcePolicies': instance_ResponseSerializer._serialize_addResourcePolicies,
            'aggregatedList': instance_ResponseSerializer._serialize_aggregatedList,
            'setShieldedInstanceIntegrityPolicy': instance_ResponseSerializer._serialize_setShieldedInstanceIntegrityPolicy,
            'performMaintenance': instance_ResponseSerializer._serialize_performMaintenance,
            'updateNetworkInterface': instance_ResponseSerializer._serialize_updateNetworkInterface,
            'setMetadata': instance_ResponseSerializer._serialize_setMetadata,
            'deleteNetworkInterface': instance_ResponseSerializer._serialize_deleteNetworkInterface,
            'setMachineType': instance_ResponseSerializer._serialize_setMachineType,
            'updateAccessConfig': instance_ResponseSerializer._serialize_updateAccessConfig,
            'setSecurityPolicy': instance_ResponseSerializer._serialize_setSecurityPolicy,
            'getIamPolicy': instance_ResponseSerializer._serialize_getIamPolicy,
            'getGuestAttributes': instance_ResponseSerializer._serialize_getGuestAttributes,
            'removeResourcePolicies': instance_ResponseSerializer._serialize_removeResourcePolicies,
            'setIamPolicy': instance_ResponseSerializer._serialize_setIamPolicy,
            'testIamPermissions': instance_ResponseSerializer._serialize_testIamPermissions,
            'start': instance_ResponseSerializer._serialize_start,
            'simulateMaintenanceEvent': instance_ResponseSerializer._serialize_simulateMaintenanceEvent,
            'setMachineResources': instance_ResponseSerializer._serialize_setMachineResources,
            'stop': instance_ResponseSerializer._serialize_stop,
            'setTags': instance_ResponseSerializer._serialize_setTags,
            'setLabels': instance_ResponseSerializer._serialize_setLabels,
            'setMinCpuPlatform': instance_ResponseSerializer._serialize_setMinCpuPlatform,
            'getEffectiveFirewalls': instance_ResponseSerializer._serialize_getEffectiveFirewalls,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setDeletionProtection(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_startWithEncryptionKey(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setScheduling(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_updateDisplayDevice(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_reset(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setServiceAccount(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_resume(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_detachDisk(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getShieldedInstanceIdentity(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setName(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addAccessConfig(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addNetworkInterface(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getScreenshot(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_suspend(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getSerialPortOutput(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listReferrers(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_deleteAccessConfig(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_updateShieldedInstanceConfig(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_attachDisk(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setDiskAutoDelete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_reportHostAsFaulty(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_bulkInsert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_sendDiagnosticInterrupt(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addResourcePolicies(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setShieldedInstanceIntegrityPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_performMaintenance(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_updateNetworkInterface(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setMetadata(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_deleteNetworkInterface(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setMachineType(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_updateAccessConfig(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setSecurityPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getGuestAttributes(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_removeResourcePolicies(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_start(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_simulateMaintenanceEvent(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setMachineResources(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_stop(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setTags(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setMinCpuPlatform(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getEffectiveFirewalls(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

