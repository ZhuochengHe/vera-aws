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
class RegionInstance:
    error: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    target_id: str = ""
    operation_group_id: str = ""
    client_operation_id: str = ""
    warnings: List[Any] = field(default_factory=list)
    name: str = ""
    creation_timestamp: str = ""
    http_error_status_code: int = 0
    status_message: str = ""
    zone: str = ""
    target_link: str = ""
    user: str = ""
    end_time: str = ""
    set_common_instance_metadata_operation_metadata: Dict[str, Any] = field(default_factory=dict)
    operation_type: str = ""
    http_error_message: str = ""
    instances_bulk_insert_operation_metadata: Dict[str, Any] = field(default_factory=dict)
    insert_time: str = ""
    region: str = ""
    progress: int = 0
    description: str = ""
    start_time: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["error"] = self.error
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.target_id is not None and self.target_id != "":
            d["targetId"] = self.target_id
        if self.operation_group_id is not None and self.operation_group_id != "":
            d["operationGroupId"] = self.operation_group_id
        if self.client_operation_id is not None and self.client_operation_id != "":
            d["clientOperationId"] = self.client_operation_id
        d["warnings"] = self.warnings
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.http_error_status_code is not None and self.http_error_status_code != 0:
            d["httpErrorStatusCode"] = self.http_error_status_code
        if self.status_message is not None and self.status_message != "":
            d["statusMessage"] = self.status_message
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.target_link is not None and self.target_link != "":
            d["targetLink"] = self.target_link
        if self.user is not None and self.user != "":
            d["user"] = self.user
        if self.end_time is not None and self.end_time != "":
            d["endTime"] = self.end_time
        d["setCommonInstanceMetadataOperationMetadata"] = self.set_common_instance_metadata_operation_metadata
        if self.operation_type is not None and self.operation_type != "":
            d["operationType"] = self.operation_type
        if self.http_error_message is not None and self.http_error_message != "":
            d["httpErrorMessage"] = self.http_error_message
        d["instancesBulkInsertOperationMetadata"] = self.instances_bulk_insert_operation_metadata
        if self.insert_time is not None and self.insert_time != "":
            d["insertTime"] = self.insert_time
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.progress is not None and self.progress != 0:
            d["progress"] = self.progress
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.start_time is not None and self.start_time != "":
            d["startTime"] = self.start_time
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#regioninstance"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class RegionInstance_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.region_instances  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "region-instance") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def bulkInsert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates multiple instances in a given region. Count specifies the number of
instances to create."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )
        region = params.get("region")
        if not region:
            return create_gcp_error(
                400,
                "Required field 'region' not found",
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
            instance_entries = [
                (instance.get("name"), instance) for instance in instances_payload
            ]
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
        if (
            default_instance_template_name
            and default_instance_template_name not in self.state.instance_templates
        ):
            return create_gcp_error(
                404,
                f"Instance template '{default_instance_template_name}' not found",
                "NOT_FOUND",
            )
        default_machine_image_ref = body.get("sourceMachineImage") or ""
        default_machine_image_name = normalize_name(default_machine_image_ref)
        if (
            default_machine_image_name
            and default_machine_image_name not in self.state.machine_images
        ):
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

            source_instance_template_ref = (
                instance_body.get("sourceInstanceTemplate")
                or default_instance_template_ref
            )
            source_instance_template_name = normalize_name(source_instance_template_ref)
            if (
                source_instance_template_name
                and source_instance_template_name not in self.state.instance_templates
            ):
                return create_gcp_error(
                    404,
                    f"Instance template '{source_instance_template_name}' not found",
                    "NOT_FOUND",
                )
            source_machine_image_ref = (
                instance_body.get("sourceMachineImage") or default_machine_image_ref
            )
            source_machine_image_name = normalize_name(source_machine_image_ref)
            if (
                source_machine_image_name
                and source_machine_image_name not in self.state.machine_images
            ):
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
            for disk in disks:
                source_ref = (disk or {}).get("source") or ""
                source_name = normalize_name(source_ref)
                if source_name and source_name not in self.state.disks:
                    return create_gcp_error(
                        404,
                        f"Disk '{source_name}' not found",
                        "NOT_FOUND",
                    )

            resource_policies = instance_body.get("resourcePolicies") or []
            for policy in resource_policies:
                policy_name = normalize_name(policy)
                if policy_name and policy_name not in self.state.resource_policies:
                    return create_gcp_error(
                        404,
                        f"Resource policy '{policy_name}' not found",
                        "NOT_FOUND",
                    )

            resource = RegionInstance(
                name=name,
                region=region,
                zone=instance_body.get("zone") or "",
                status=instance_body.get("status") or "RUNNING",
                description=instance_body.get("description") or "",
                creation_timestamp=instance_body.get("creationTimestamp")
                or datetime.now(timezone.utc).isoformat(),
                id=self._generate_id(),
            )
            self.resources[resource.name] = resource

        resource_link = f"projects/{project}/regions/{region}/instances"
        return make_operation(
            operation_type="bulkInsert",
            resource_link=resource_link,
            params=params,
        )


class region_instance_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'bulkInsert': region_instance_RequestParser._parse_bulkInsert,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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


class region_instance_ResponseSerializer:
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
            'bulkInsert': region_instance_ResponseSerializer._serialize_bulkInsert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_bulkInsert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

