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
class NetworkAttachment:
    name: str = ""
    region: str = ""
    subnetworks: List[Any] = field(default_factory=list)
    producer_accept_lists: List[Any] = field(default_factory=list)
    fingerprint: str = ""
    description: str = ""
    creation_timestamp: str = ""
    producer_reject_lists: List[Any] = field(default_factory=list)
    connection_endpoints: List[Any] = field(default_factory=list)
    connection_preference: str = ""
    self_link_with_id: str = ""
    network: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.region is not None and self.region != "":
            d["region"] = self.region
        d["subnetworks"] = self.subnetworks
        d["producerAcceptLists"] = self.producer_accept_lists
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["producerRejectLists"] = self.producer_reject_lists
        d["connectionEndpoints"] = self.connection_endpoints
        if self.connection_preference is not None and self.connection_preference != "":
            d["connectionPreference"] = self.connection_preference
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["iamPolicy"] = self.iam_policy
        d["kind"] = "compute#networkattachment"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class NetworkAttachment_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.network_attachments  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "network-attachment") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str, region: Optional[str] = None) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if region and resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a NetworkAttachment in the specified project in the given scope
using the parameters that are included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("NetworkAttachment")
        if not body:
            return create_gcp_error(400, "Required field 'NetworkAttachment' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"NetworkAttachment {name!r} already exists", "ALREADY_EXISTS")
        network_name = body.get("network", "")
        if network_name:
            network = self.state.networks.get(network_name)
            if not network:
                return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
        subnetworks = body.get("subnetworks") or []
        for subnetwork in subnetworks:
            if isinstance(subnetwork, dict):
                subnetwork_name = subnetwork.get("subnetwork") or subnetwork.get("name") or subnetwork.get("selfLink")
            else:
                subnetwork_name = subnetwork
            if subnetwork_name and not self.state.subnetworks.get(subnetwork_name):
                return create_gcp_error(404, f"Subnetwork {subnetwork_name!r} not found", "NOT_FOUND")
        resource = NetworkAttachment(
            name=name,
            region=region,
            subnetworks=subnetworks,
            producer_accept_lists=body.get("producerAcceptLists", []),
            fingerprint=body.get("fingerprint", ""),
            description=body.get("description", ""),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            producer_reject_lists=body.get("producerRejectLists", []),
            connection_endpoints=body.get("connectionEndpoints", []),
            connection_preference=body.get("connectionPreference", ""),
            self_link_with_id=body.get("selfLinkWithId", ""),
            network=network_name,
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/networkAttachments/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified NetworkAttachment resource in the given scope."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("networkAttachment")
        if not name:
            return create_gcp_error(400, "Required field 'networkAttachment' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of all NetworkAttachment resources,
regional and global, available to the specified project.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parame..."""
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
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        items = (
            {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
            if not resources
            else {scope_key: {"NetworkAttachments": [r.to_dict() for r in resources]}}
        )
        return {
            "kind": "compute#networkattachmentAggregatedList",
            "id": f"projects/{project}/aggregated/NetworkAttachments",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the NetworkAttachments for a project in the given scope."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
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
            "kind": "compute#networkattachmentList",
            "id": f"projects/{project}/regions/{region}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified NetworkAttachment resource with the data included in
the request. This method supports PATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("networkAttachment")
        if not name:
            return create_gcp_error(400, "Required field 'networkAttachment' not specified", "INVALID_ARGUMENT")
        body = params.get("NetworkAttachment")
        if not body:
            return create_gcp_error(400, "Required field 'NetworkAttachment' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        if "network" in body:
            network_name = body.get("network", "")
            if network_name:
                network = self.state.networks.get(network_name)
                if not network:
                    return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
            resource.network = network_name
        if "subnetworks" in body:
            subnetworks = body.get("subnetworks") or []
            for subnetwork in subnetworks:
                if isinstance(subnetwork, dict):
                    subnetwork_name = subnetwork.get("subnetwork") or subnetwork.get("name") or subnetwork.get("selfLink")
                else:
                    subnetwork_name = subnetwork
                if subnetwork_name and not self.state.subnetworks.get(subnetwork_name):
                    return create_gcp_error(404, f"Subnetwork {subnetwork_name!r} not found", "NOT_FOUND")
            resource.subnetworks = subnetworks
        if "producerAcceptLists" in body:
            resource.producer_accept_lists = body.get("producerAcceptLists") or []
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint", "")
        if "description" in body:
            resource.description = body.get("description", "")
        if "producerRejectLists" in body:
            resource.producer_reject_lists = body.get("producerRejectLists") or []
        if "connectionEndpoints" in body:
            resource.connection_endpoints = body.get("connectionEndpoints") or []
        if "connectionPreference" in body:
            resource.connection_preference = body.get("connectionPreference", "")
        if "selfLinkWithId" in body:
            resource.self_link_with_id = body.get("selfLinkWithId", "")
        if "iamPolicy" in body:
            resource.iam_policy = body.get("iamPolicy") or {}
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/regions/{region}/networkAttachments/{resource.name}",
            params=params,
        )

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("RegionSetPolicyRequest")
        if not body:
            return create_gcp_error(400, "Required field 'RegionSetPolicyRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        resource.iam_policy = body.get("policy") or {}
        return make_operation(
            operation_type="setIamPolicy",
            resource_link=f"projects/{project}/regions/{region}/networkAttachments/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest")
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions") or []
        return {"permissions": permissions}

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        return resource.iam_policy or {}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified NetworkAttachment in the given scope"""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("networkAttachment")
        if not name:
            return create_gcp_error(400, "Required field 'networkAttachment' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        self.resources.pop(name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/networkAttachments/{name}",
            params=params,
        )


class network_attachment_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'insert': network_attachment_RequestParser._parse_insert,
            'aggregatedList': network_attachment_RequestParser._parse_aggregatedList,
            'list': network_attachment_RequestParser._parse_list,
            'get': network_attachment_RequestParser._parse_get,
            'testIamPermissions': network_attachment_RequestParser._parse_testIamPermissions,
            'getIamPolicy': network_attachment_RequestParser._parse_getIamPolicy,
            'patch': network_attachment_RequestParser._parse_patch,
            'delete': network_attachment_RequestParser._parse_delete,
            'setIamPolicy': network_attachment_RequestParser._parse_setIamPolicy,
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
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['NetworkAttachment'] = body.get('NetworkAttachment')
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
        params['NetworkAttachment'] = body.get('NetworkAttachment')
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
        params['RegionSetPolicyRequest'] = body.get('RegionSetPolicyRequest')
        return params


class network_attachment_ResponseSerializer:
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
            'insert': network_attachment_ResponseSerializer._serialize_insert,
            'aggregatedList': network_attachment_ResponseSerializer._serialize_aggregatedList,
            'list': network_attachment_ResponseSerializer._serialize_list,
            'get': network_attachment_ResponseSerializer._serialize_get,
            'testIamPermissions': network_attachment_ResponseSerializer._serialize_testIamPermissions,
            'getIamPolicy': network_attachment_ResponseSerializer._serialize_getIamPolicy,
            'patch': network_attachment_ResponseSerializer._serialize_patch,
            'delete': network_attachment_ResponseSerializer._serialize_delete,
            'setIamPolicy': network_attachment_ResponseSerializer._serialize_setIamPolicy,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

