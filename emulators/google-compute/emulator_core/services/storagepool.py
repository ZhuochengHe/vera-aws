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
class StoragePool:
    storage_pool_type: str = ""
    status: Dict[str, Any] = field(default_factory=dict)
    performance_provisioning_type: str = ""
    self_link_with_id: str = ""
    description: str = ""
    creation_timestamp: str = ""
    pool_provisioned_throughput: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    state: str = ""
    resource_status: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    capacity_provisioning_type: str = ""
    name: str = ""
    pool_provisioned_iops: str = ""
    exapool_provisioned_capacity_gb: Dict[str, Any] = field(default_factory=dict)
    label_fingerprint: str = ""
    zone: str = ""
    pool_provisioned_capacity_gb: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.storage_pool_type is not None and self.storage_pool_type != "":
            d["storagePoolType"] = self.storage_pool_type
        d["status"] = self.status
        if self.performance_provisioning_type is not None and self.performance_provisioning_type != "":
            d["performanceProvisioningType"] = self.performance_provisioning_type
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.pool_provisioned_throughput is not None and self.pool_provisioned_throughput != "":
            d["poolProvisionedThroughput"] = self.pool_provisioned_throughput
        d["labels"] = self.labels
        if self.state is not None and self.state != "":
            d["state"] = self.state
        d["resourceStatus"] = self.resource_status
        d["params"] = self.params
        if self.capacity_provisioning_type is not None and self.capacity_provisioning_type != "":
            d["capacityProvisioningType"] = self.capacity_provisioning_type
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.pool_provisioned_iops is not None and self.pool_provisioned_iops != "":
            d["poolProvisionedIops"] = self.pool_provisioned_iops
        d["exapoolProvisionedCapacityGb"] = self.exapool_provisioned_capacity_gb
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.pool_provisioned_capacity_gb is not None and self.pool_provisioned_capacity_gb != "":
            d["poolProvisionedCapacityGb"] = self.pool_provisioned_capacity_gb
        if self.id is not None and self.id != "":
            d["id"] = self.id
        if self.iam_policy:
            d["iamPolicy"] = self.iam_policy
        d["kind"] = "compute#storagepool"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class StoragePool_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.storage_pools  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "storage-pool") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a storage pool in the specified project using the data
in the request."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("StoragePool"):
            return create_gcp_error(400, "Required field 'StoragePool' is missing", "INVALID_ARGUMENT")

        body = params.get("StoragePool") or {}
        name = body.get("name") or params.get("name") or self._generate_name()
        if name in self.resources:
            return create_gcp_error(400, f"Resource {name!r} already exists", "FAILED_PRECONDITION")

        now = datetime.now(timezone.utc).isoformat()
        resource = StoragePool(
            storage_pool_type=body.get("storagePoolType", ""),
            status=body.get("status", {}),
            performance_provisioning_type=body.get("performanceProvisioningType", ""),
            self_link_with_id=body.get("selfLinkWithId", ""),
            description=body.get("description", ""),
            creation_timestamp=body.get("creationTimestamp", now),
            pool_provisioned_throughput=body.get("poolProvisionedThroughput", ""),
            labels=body.get("labels", {}) or {},
            state=body.get("state", ""),
            resource_status=body.get("resourceStatus", {}) or {},
            params=body.get("params", {}) or {},
            capacity_provisioning_type=body.get("capacityProvisioningType", ""),
            name=name,
            pool_provisioned_iops=body.get("poolProvisionedIops", ""),
            exapool_provisioned_capacity_gb=body.get("exapoolProvisionedCapacityGb", {}) or {},
            label_fingerprint=str(uuid.uuid4())[:8],
            zone=params.get("zone", ""),
            pool_provisioned_capacity_gb=body.get("poolProvisionedCapacityGb", ""),
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy", {}) or {},
        )
        self.resources[resource.name] = resource

        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{params.get('project')}/zones/{params.get('zone')}/StoragePools/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns a specified storage pool. Gets a list of available
storage pools by making a list() request."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("storagePool"):
            return create_gcp_error(400, "Required field 'storagePool' is missing", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params.get("storagePool"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(
                404,
                f"The resource '{params.get('storagePool')}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of storage pools contained within
the specified zone."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        zone = params.get("zone")
        resources = [r for r in resources if r.zone == zone]

        return {
            "kind": "compute#storagepoolList",
            "id": f"projects/{params.get('project', '')}/zones/{params.get('zone', '')}/storagePools",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of storage pools.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]

        items: Dict[str, Any] = {}
        for resource in resources:
            scope_key = f"zones/{resource.zone or params.get('zone', 'us-central1-a')}"
            bucket = items.setdefault(scope_key, {})
            bucket.setdefault("StoragePools", []).append(resource.to_dict())

        if not items:
            scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}

        return {
            "kind": "compute#storagepoolAggregatedList",
            "id": f"projects/{params.get('project', '')}/aggregated/storagePools",
            "items": items,
            "selfLink": "",
        }

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("resource"):
            return create_gcp_error(400, "Required field 'resource' is missing", "INVALID_ARGUMENT")
        body = params.get("ZoneSetPolicyRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ZoneSetPolicyRequest' is missing",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(params.get("resource"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(
                404,
                f"The resource '{params.get('resource')}' was not found",
                "NOT_FOUND",
            )

        resource.iam_policy = body.get("policy") or {}
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=(
                f"projects/{params.get('project')}/zones/"
                f"{params.get('zone')}/StoragePools/{resource.name}"
            ),
            params=params,
        )

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified storagePool with the data included in the request.
The update is performed only on selected fields included as part
of update-mask. Only the following fields can be modified:
..."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("storagePool"):
            return create_gcp_error(400, "Required field 'storagePool' is missing", "INVALID_ARGUMENT")
        body = params.get("StoragePool") or {}
        if not body:
            return create_gcp_error(400, "Required field 'StoragePool' is missing", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params.get("storagePool"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(
                404,
                f"The resource '{params.get('storagePool')}' was not found",
                "NOT_FOUND",
            )

        body_name = body.get("name")
        if body_name and body_name != resource.name:
            return create_gcp_error(400, "StoragePool name cannot be changed", "INVALID_ARGUMENT")

        update_mask = params.get("updateMask") or ""
        update_fields = {field.strip() for field in update_mask.split(",") if field.strip()}
        if not update_fields:
            update_fields = None

        field_map = {
            "storagePoolType": "storage_pool_type",
            "status": "status",
            "performanceProvisioningType": "performance_provisioning_type",
            "selfLinkWithId": "self_link_with_id",
            "description": "description",
            "poolProvisionedThroughput": "pool_provisioned_throughput",
            "labels": "labels",
            "state": "state",
            "resourceStatus": "resource_status",
            "params": "params",
            "capacityProvisioningType": "capacity_provisioning_type",
            "poolProvisionedIops": "pool_provisioned_iops",
            "exapoolProvisionedCapacityGb": "exapool_provisioned_capacity_gb",
            "poolProvisionedCapacityGb": "pool_provisioned_capacity_gb",
        }

        for api_field, attr_name in field_map.items():
            if update_fields is not None and api_field not in update_fields:
                continue
            if api_field in body:
                setattr(resource, attr_name, body.get(api_field))
                if api_field == "labels":
                    resource.labels = body.get("labels", {}) or {}
                    resource.label_fingerprint = str(uuid.uuid4())[:8]

        return make_operation(
            operation_type="update",
            resource_link=(
                f"projects/{params.get('project')}/zones/"
                f"{params.get('zone')}/StoragePools/{resource.name}"
            ),
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("resource"):
            return create_gcp_error(400, "Required field 'resource' is missing", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TestPermissionsRequest' is missing",
                "INVALID_ARGUMENT",
            )

        resource = self._get_resource_or_error(params.get("resource"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(
                404,
                f"The resource '{params.get('resource')}' was not found",
                "NOT_FOUND",
            )

        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("resource"):
            return create_gcp_error(400, "Required field 'resource' is missing", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params.get("resource"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(
                404,
                f"The resource '{params.get('resource')}' was not found",
                "NOT_FOUND",
            )

        return resource.iam_policy or {}

    def listDisks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the disks in a specified storage pool."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("storagePool"):
            return create_gcp_error(400, "Required field 'storagePool' is missing", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params.get("storagePool"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(
                404,
                f"The resource '{params.get('storagePool')}' was not found",
                "NOT_FOUND",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        disks = [disk for disk in self.state.disks.values() if disk.zone == params.get("zone")]
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                disks = [disk for disk in disks if disk.name == match.group(1)]

        storage_pool_name = params.get("storagePool")
        disks = [
            disk
            for disk in disks
            if normalize_name(disk.storage_pool) == storage_pool_name
        ]

        return {
            "kind": "compute#storagePoolListDisks",
            "id": (
                f"projects/{params.get('project', '')}/zones/{params.get('zone', '')}/"
                f"storagePools/{storage_pool_name}/listDisks"
            ),
            "items": [disk.to_dict() for disk in disks],
            "selfLink": "",
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified storage pool. Deleting a storagePool
removes its data permanently and is irreversible. However, deleting a
storagePool does not delete any snapshots previously
made from the s..."""
        if not params.get("project"):
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not params.get("zone"):
            return create_gcp_error(400, "Required field 'zone' is missing", "INVALID_ARGUMENT")
        if not params.get("storagePool"):
            return create_gcp_error(400, "Required field 'storagePool' is missing", "INVALID_ARGUMENT")

        resource = self._get_resource_or_error(params.get("storagePool"))
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != params.get("zone"):
            return create_gcp_error(
                404,
                f"The resource '{params.get('storagePool')}' was not found",
                "NOT_FOUND",
            )

        self.resources.pop(resource.name, None)
        return make_operation(
            operation_type="delete",
            resource_link=(
                f"projects/{params.get('project')}/zones/"
                f"{params.get('zone')}/StoragePools/{resource.name}"
            ),
            params=params,
        )


class storage_pool_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'list': storage_pool_RequestParser._parse_list,
            'aggregatedList': storage_pool_RequestParser._parse_aggregatedList,
            'testIamPermissions': storage_pool_RequestParser._parse_testIamPermissions,
            'get': storage_pool_RequestParser._parse_get,
            'getIamPolicy': storage_pool_RequestParser._parse_getIamPolicy,
            'setIamPolicy': storage_pool_RequestParser._parse_setIamPolicy,
            'insert': storage_pool_RequestParser._parse_insert,
            'update': storage_pool_RequestParser._parse_update,
            'delete': storage_pool_RequestParser._parse_delete,
            'listDisks': storage_pool_RequestParser._parse_listDisks,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['StoragePool'] = body.get('StoragePool')
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
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['StoragePool'] = body.get('StoragePool')
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
    def _parse_listDisks(
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


class storage_pool_ResponseSerializer:
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
            'list': storage_pool_ResponseSerializer._serialize_list,
            'aggregatedList': storage_pool_ResponseSerializer._serialize_aggregatedList,
            'testIamPermissions': storage_pool_ResponseSerializer._serialize_testIamPermissions,
            'get': storage_pool_ResponseSerializer._serialize_get,
            'getIamPolicy': storage_pool_ResponseSerializer._serialize_getIamPolicy,
            'setIamPolicy': storage_pool_ResponseSerializer._serialize_setIamPolicy,
            'insert': storage_pool_ResponseSerializer._serialize_insert,
            'update': storage_pool_ResponseSerializer._serialize_update,
            'delete': storage_pool_ResponseSerializer._serialize_delete,
            'listDisks': storage_pool_ResponseSerializer._serialize_listDisks,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listDisks(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

