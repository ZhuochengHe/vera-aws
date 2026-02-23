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
class InstantSnapshot:
    source_disk_id: str = ""
    zone: str = ""
    status: str = ""
    disk_size_gb: str = ""
    labels: Dict[str, Any] = field(default_factory=dict)
    satisfies_pzi: bool = False
    architecture: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = ""
    label_fingerprint: str = ""
    source_disk: str = ""
    resource_status: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    self_link_with_id: str = ""
    region: str = ""
    description: str = ""
    satisfies_pzs: bool = False
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.source_disk_id is not None and self.source_disk_id != "":
            d["sourceDiskId"] = self.source_disk_id
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.disk_size_gb is not None and self.disk_size_gb != "":
            d["diskSizeGb"] = self.disk_size_gb
        d["labels"] = self.labels
        d["satisfiesPzi"] = self.satisfies_pzi
        if self.architecture is not None and self.architecture != "":
            d["architecture"] = self.architecture
        d["params"] = self.params
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.label_fingerprint is not None and self.label_fingerprint != "":
            d["labelFingerprint"] = self.label_fingerprint
        if self.source_disk is not None and self.source_disk != "":
            d["sourceDisk"] = self.source_disk
        d["resourceStatus"] = self.resource_status
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["satisfiesPzs"] = self.satisfies_pzs
        d["iamPolicy"] = self.iam_policy
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#instantsnapshot"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InstantSnapshot_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.instant_snapshots  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "instant-snapshot") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_instant_snapshot_or_error(
        self,
        params: Dict[str, Any],
        snapshot_name: str,
    ) -> Any:
        snapshot = self.resources.get(snapshot_name)
        if not snapshot:
            project = params.get("project", "")
            zone = params.get("zone", "")
            resource_path = (
                f"projects/{project}/zones/{zone}/instantSnapshots/{snapshot_name}"
            )
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return snapshot

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an instant snapshot in the specified zone."""
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
        body = params.get("InstantSnapshot") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstantSnapshot' not found",
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
                f"InstantSnapshot '{name}' already exists",
                "ALREADY_EXISTS",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        source_disk_ref = body.get("sourceDisk") or ""
        source_disk_name = normalize_name(source_disk_ref)
        if source_disk_name and source_disk_name not in self.state.disks:
            return create_gcp_error(
                404,
                f"Source disk '{source_disk_name}' not found",
                "NOT_FOUND",
            )

        labels = body.get("labels", {})
        label_fingerprint = str(uuid.uuid4())[:8] if labels is not None else ""
        disk_size_value = body.get("diskSizeGb")
        disk_size_gb = str(disk_size_value) if disk_size_value is not None else ""
        resource = InstantSnapshot(
            source_disk_id=body.get("sourceDiskId") or "",
            zone=zone,
            status=body.get("status") or "",
            disk_size_gb=disk_size_gb,
            labels=labels or {},
            satisfies_pzi=bool(body.get("satisfiesPzi"))
            if "satisfiesPzi" in body
            else False,
            architecture=body.get("architecture") or "",
            params=body.get("params") or {},
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            label_fingerprint=label_fingerprint,
            source_disk=source_disk_ref,
            resource_status=body.get("resourceStatus") or {},
            name=name,
            self_link_with_id=body.get("selfLinkWithId") or "",
            region=body.get("region") or "",
            description=body.get("description") or "",
            satisfies_pzs=bool(body.get("satisfiesPzs"))
            if "satisfiesPzs" in body
            else False,
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        resource_link = f"projects/{project}/zones/{zone}/InstantSnapshots/{resource.name}"
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified InstantSnapshot resource in the specified zone."""
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
        snapshot_name = params.get("instantSnapshot")
        if not snapshot_name:
            return create_gcp_error(
                400,
                "Required field 'instantSnapshot' not found",
                "INVALID_ARGUMENT",
            )
        snapshot = self._get_instant_snapshot_or_error(params, snapshot_name)
        if is_error_response(snapshot):
            return snapshot
        if snapshot.zone and snapshot.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/instantSnapshots/{snapshot_name}' was not found",
                "NOT_FOUND",
            )
        return snapshot.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of instantSnapshots.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not found",
                "INVALID_ARGUMENT",
            )

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]

        zone = params.get("zone")
        if zone:
            resources = [r for r in resources if r.zone == zone]
        scope_key = f"zones/{zone or 'us-central1-a'}"
        if not resources:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items = {scope_key: {"InstantSnapshots": [r.to_dict() for r in resources]}}
        return {
            "kind": "compute#instantsnapshotAggregatedList",
            "id": f"projects/{project}/aggregated/instantSnapshots",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of InstantSnapshot resources contained within
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

        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.zone == zone]
        return {
            "kind": "compute#instantsnapshotList",
            "id": f"projects/{project}/zones/{zone}/instantSnapshots",
            "items": [r.to_dict() for r in resources],
            "selfLink": "",
        }

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
        snapshot = self._get_instant_snapshot_or_error(params, resource_name)
        if is_error_response(snapshot):
            return snapshot
        if snapshot.zone and snapshot.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/instantSnapshots/{resource_name}' was not found",
                "NOT_FOUND",
            )
        snapshot.iam_policy = body.get("policy") or {}
        resource_link = (
            f"projects/{project}/zones/{zone}/InstantSnapshots/{snapshot.name}"
        )
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=resource_link,
            params=params,
        )

    def setLabels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the labels on a instantSnapshot in the given zone. To learn more about
labels, read the Labeling
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
        resource_name = params.get("resource")
        if not resource_name:
            return create_gcp_error(
                400,
                "Required field 'resource' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("ZoneSetLabelsRequest") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'ZoneSetLabelsRequest' not found",
                "INVALID_ARGUMENT",
            )
        snapshot = self._get_instant_snapshot_or_error(params, resource_name)
        if is_error_response(snapshot):
            return snapshot
        if snapshot.zone and snapshot.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/instantSnapshots/{resource_name}' was not found",
                "NOT_FOUND",
            )
        snapshot.labels = body.get("labels") or {}
        snapshot.label_fingerprint = str(uuid.uuid4())[:8]
        resource_link = (
            f"projects/{project}/zones/{zone}/InstantSnapshots/{snapshot.name}"
        )
        return make_operation(
            operation_type="setLabels",
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
        snapshot = self._get_instant_snapshot_or_error(params, resource_name)
        if is_error_response(snapshot):
            return snapshot
        if snapshot.zone and snapshot.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/instantSnapshots/{resource_name}' was not found",
                "NOT_FOUND",
            )
        return snapshot.iam_policy or {}

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
        snapshot = self._get_instant_snapshot_or_error(params, resource_name)
        if is_error_response(snapshot):
            return snapshot
        if snapshot.zone and snapshot.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/instantSnapshots/{resource_name}' was not found",
                "NOT_FOUND",
            )
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified InstantSnapshot resource. Keep in mind that deleting
a single instantSnapshot might not necessarily delete all the data on that
instantSnapshot. If any data on the instantSnap..."""
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
        snapshot_name = params.get("instantSnapshot")
        if not snapshot_name:
            return create_gcp_error(
                400,
                "Required field 'instantSnapshot' not found",
                "INVALID_ARGUMENT",
            )
        snapshot = self._get_instant_snapshot_or_error(params, snapshot_name)
        if is_error_response(snapshot):
            return snapshot
        if snapshot.zone and snapshot.zone != zone:
            return create_gcp_error(
                404,
                f"The resource 'projects/{project}/zones/{zone}/instantSnapshots/{snapshot_name}' was not found",
                "NOT_FOUND",
            )
        del self.resources[snapshot_name]
        resource_link = (
            f"projects/{project}/zones/{zone}/InstantSnapshots/{snapshot_name}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class instant_snapshot_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'setIamPolicy': instant_snapshot_RequestParser._parse_setIamPolicy,
            'aggregatedList': instant_snapshot_RequestParser._parse_aggregatedList,
            'setLabels': instant_snapshot_RequestParser._parse_setLabels,
            'get': instant_snapshot_RequestParser._parse_get,
            'getIamPolicy': instant_snapshot_RequestParser._parse_getIamPolicy,
            'insert': instant_snapshot_RequestParser._parse_insert,
            'delete': instant_snapshot_RequestParser._parse_delete,
            'testIamPermissions': instant_snapshot_RequestParser._parse_testIamPermissions,
            'list': instant_snapshot_RequestParser._parse_list,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['ZoneSetLabelsRequest'] = body.get('ZoneSetLabelsRequest')
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
        params['InstantSnapshot'] = body.get('InstantSnapshot')
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


class instant_snapshot_ResponseSerializer:
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
            'setIamPolicy': instant_snapshot_ResponseSerializer._serialize_setIamPolicy,
            'aggregatedList': instant_snapshot_ResponseSerializer._serialize_aggregatedList,
            'setLabels': instant_snapshot_ResponseSerializer._serialize_setLabels,
            'get': instant_snapshot_ResponseSerializer._serialize_get,
            'getIamPolicy': instant_snapshot_ResponseSerializer._serialize_getIamPolicy,
            'insert': instant_snapshot_ResponseSerializer._serialize_insert,
            'delete': instant_snapshot_ResponseSerializer._serialize_delete,
            'testIamPermissions': instant_snapshot_ResponseSerializer._serialize_testIamPermissions,
            'list': instant_snapshot_ResponseSerializer._serialize_list,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setLabels(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

