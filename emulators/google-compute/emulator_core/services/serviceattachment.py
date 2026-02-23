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
class ServiceAttachment:
    name: str = ""
    propagated_connection_limit: int = 0
    creation_timestamp: str = ""
    psc_service_attachment_id: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    nat_subnets: List[Any] = field(default_factory=list)
    consumer_accept_lists: List[Any] = field(default_factory=list)
    enable_proxy_protocol: bool = False
    connection_preference: str = ""
    consumer_reject_lists: List[Any] = field(default_factory=list)
    target_service: str = ""
    reconcile_connections: bool = False
    fingerprint: str = ""
    domain_names: List[Any] = field(default_factory=list)
    producer_forwarding_rule: str = ""
    connected_endpoints: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    region: str = ""
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.propagated_connection_limit is not None and self.propagated_connection_limit != 0:
            d["propagatedConnectionLimit"] = self.propagated_connection_limit
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["pscServiceAttachmentId"] = self.psc_service_attachment_id
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["natSubnets"] = self.nat_subnets
        d["consumerAcceptLists"] = self.consumer_accept_lists
        d["enableProxyProtocol"] = self.enable_proxy_protocol
        if self.connection_preference is not None and self.connection_preference != "":
            d["connectionPreference"] = self.connection_preference
        d["consumerRejectLists"] = self.consumer_reject_lists
        if self.target_service is not None and self.target_service != "":
            d["targetService"] = self.target_service
        d["reconcileConnections"] = self.reconcile_connections
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        d["domainNames"] = self.domain_names
        if self.producer_forwarding_rule is not None and self.producer_forwarding_rule != "":
            d["producerForwardingRule"] = self.producer_forwarding_rule
        d["connectedEndpoints"] = self.connected_endpoints
        d["metadata"] = self.metadata
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["iamPolicy"] = self.iam_policy
        d["kind"] = "compute#serviceattachment"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class ServiceAttachment_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.service_attachments  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "service-attachment") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str, region: Optional[str] = None) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if region and resource.region and resource.region != region:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a ServiceAttachment in the specified project in the given scope
using the parameters that are included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("ServiceAttachment")
        if not body:
            return create_gcp_error(400, "Required field 'ServiceAttachment' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"ServiceAttachment {name!r} already exists", "ALREADY_EXISTS")
        target_service = body.get("targetService", "")
        if target_service and not self.state.forwarding_rules.get(target_service):
            return create_gcp_error(404, f"ForwardingRule {target_service!r} not found", "NOT_FOUND")
        producer_forwarding_rule = body.get("producerForwardingRule", "")
        if producer_forwarding_rule and not self.state.forwarding_rules.get(producer_forwarding_rule):
            return create_gcp_error(404, f"ForwardingRule {producer_forwarding_rule!r} not found", "NOT_FOUND")
        nat_subnets = body.get("natSubnets") or []
        for nat_subnet in nat_subnets:
            if isinstance(nat_subnet, dict):
                subnet_name = nat_subnet.get("subnetwork") or nat_subnet.get("name") or nat_subnet.get("selfLink")
            else:
                subnet_name = nat_subnet
            if subnet_name and not self.state.subnetworks.get(subnet_name):
                return create_gcp_error(404, f"Subnetwork {subnet_name!r} not found", "NOT_FOUND")
        resource = ServiceAttachment(
            name=name,
            propagated_connection_limit=body.get("propagatedConnectionLimit", 0),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            psc_service_attachment_id=body.get("pscServiceAttachmentId") or {},
            description=body.get("description", ""),
            nat_subnets=nat_subnets,
            consumer_accept_lists=body.get("consumerAcceptLists", []),
            enable_proxy_protocol=body.get("enableProxyProtocol", False),
            connection_preference=body.get("connectionPreference", ""),
            consumer_reject_lists=body.get("consumerRejectLists", []),
            target_service=target_service,
            reconcile_connections=body.get("reconcileConnections", False),
            fingerprint=body.get("fingerprint", ""),
            domain_names=body.get("domainNames", []),
            producer_forwarding_rule=producer_forwarding_rule,
            connected_endpoints=body.get("connectedEndpoints", []),
            metadata=body.get("metadata", {}),
            region=region,
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/serviceAttachments/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified ServiceAttachment resource in the given scope."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("serviceAttachment")
        if not name:
            return create_gcp_error(400, "Required field 'serviceAttachment' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the ServiceAttachments for a project in the given scope."""
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
            "kind": "compute#serviceattachmentList",
            "id": f"projects/{project}/regions/{region}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of all ServiceAttachment resources,
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
            else {scope_key: {"ServiceAttachments": [r.to_dict() for r in resources]}}
        )
        return {
            "kind": "compute#serviceattachmentAggregatedList",
            "id": f"projects/{project}/aggregated/ServiceAttachments",
            "items": items,
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified ServiceAttachment resource with the data included in
the request. This method supports PATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("serviceAttachment")
        if not name:
            return create_gcp_error(400, "Required field 'serviceAttachment' not specified", "INVALID_ARGUMENT")
        body = params.get("ServiceAttachment")
        if not body:
            return create_gcp_error(400, "Required field 'ServiceAttachment' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        if "propagatedConnectionLimit" in body:
            resource.propagated_connection_limit = body.get("propagatedConnectionLimit", 0)
        if "pscServiceAttachmentId" in body:
            resource.psc_service_attachment_id = body.get("pscServiceAttachmentId") or {}
        if "description" in body:
            resource.description = body.get("description", "")
        if "natSubnets" in body:
            nat_subnets = body.get("natSubnets") or []
            for nat_subnet in nat_subnets:
                if isinstance(nat_subnet, dict):
                    subnet_name = nat_subnet.get("subnetwork") or nat_subnet.get("name") or nat_subnet.get("selfLink")
                else:
                    subnet_name = nat_subnet
                if subnet_name and not self.state.subnetworks.get(subnet_name):
                    return create_gcp_error(404, f"Subnetwork {subnet_name!r} not found", "NOT_FOUND")
            resource.nat_subnets = nat_subnets
        if "consumerAcceptLists" in body:
            resource.consumer_accept_lists = body.get("consumerAcceptLists") or []
        if "enableProxyProtocol" in body:
            resource.enable_proxy_protocol = body.get("enableProxyProtocol", False)
        if "connectionPreference" in body:
            resource.connection_preference = body.get("connectionPreference", "")
        if "consumerRejectLists" in body:
            resource.consumer_reject_lists = body.get("consumerRejectLists") or []
        if "targetService" in body:
            target_service = body.get("targetService", "")
            if target_service and not self.state.forwarding_rules.get(target_service):
                return create_gcp_error(404, f"ForwardingRule {target_service!r} not found", "NOT_FOUND")
            resource.target_service = target_service
        if "reconcileConnections" in body:
            resource.reconcile_connections = body.get("reconcileConnections", False)
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint", "")
        if "domainNames" in body:
            resource.domain_names = body.get("domainNames") or []
        if "producerForwardingRule" in body:
            producer_forwarding_rule = body.get("producerForwardingRule", "")
            if producer_forwarding_rule and not self.state.forwarding_rules.get(producer_forwarding_rule):
                return create_gcp_error(404, f"ForwardingRule {producer_forwarding_rule!r} not found", "NOT_FOUND")
            resource.producer_forwarding_rule = producer_forwarding_rule
        if "connectedEndpoints" in body:
            resource.connected_endpoints = body.get("connectedEndpoints") or []
        if "metadata" in body:
            resource.metadata = body.get("metadata") or {}
        if "iamPolicy" in body:
            resource.iam_policy = body.get("iamPolicy") or {}
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/regions/{region}/serviceAttachments/{resource.name}",
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
            resource_link=f"projects/{project}/regions/{region}/serviceAttachments/{resource.name}",
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
        """Deletes the specified ServiceAttachment in the given scope"""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("serviceAttachment")
        if not name:
            return create_gcp_error(400, "Required field 'serviceAttachment' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(name, region)
        if is_error_response(resource):
            return resource
        self.resources.pop(name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/serviceAttachments/{name}",
            params=params,
        )


class service_attachment_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'patch': service_attachment_RequestParser._parse_patch,
            'setIamPolicy': service_attachment_RequestParser._parse_setIamPolicy,
            'testIamPermissions': service_attachment_RequestParser._parse_testIamPermissions,
            'getIamPolicy': service_attachment_RequestParser._parse_getIamPolicy,
            'list': service_attachment_RequestParser._parse_list,
            'aggregatedList': service_attachment_RequestParser._parse_aggregatedList,
            'delete': service_attachment_RequestParser._parse_delete,
            'get': service_attachment_RequestParser._parse_get,
            'insert': service_attachment_RequestParser._parse_insert,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['ServiceAttachment'] = body.get('ServiceAttachment')
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
    def _parse_get(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'showNatIps' in query_params:
            params['showNatIps'] = query_params['showNatIps']
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
        params['ServiceAttachment'] = body.get('ServiceAttachment')
        return params


class service_attachment_ResponseSerializer:
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
            'patch': service_attachment_ResponseSerializer._serialize_patch,
            'setIamPolicy': service_attachment_ResponseSerializer._serialize_setIamPolicy,
            'testIamPermissions': service_attachment_ResponseSerializer._serialize_testIamPermissions,
            'getIamPolicy': service_attachment_ResponseSerializer._serialize_getIamPolicy,
            'list': service_attachment_ResponseSerializer._serialize_list,
            'aggregatedList': service_attachment_ResponseSerializer._serialize_aggregatedList,
            'delete': service_attachment_ResponseSerializer._serialize_delete,
            'get': service_attachment_ResponseSerializer._serialize_get,
            'insert': service_attachment_ResponseSerializer._serialize_insert,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

