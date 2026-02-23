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
class TargetInstance:
    nat_policy: str = ""
    instance: str = ""
    description: str = ""
    zone: str = ""
    creation_timestamp: str = ""
    security_policy: str = ""
    name: str = ""
    network: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.nat_policy is not None and self.nat_policy != "":
            d["natPolicy"] = self.nat_policy
        if self.instance is not None and self.instance != "":
            d["instance"] = self.instance
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.security_policy is not None and self.security_policy != "":
            d["securityPolicy"] = self.security_policy
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#targetinstance"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class TargetInstance_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.target_instances  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "target-instance") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_target_instance_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource {name!r} was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a TargetInstance resource in the specified project and zone using
the data included in the request."""
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
        body = params.get("TargetInstance") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'TargetInstance' not found",
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
                f"TargetInstance '{name}' already exists",
                "ALREADY_EXISTS",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        instance_ref = body.get("instance") or ""
        instance_name = normalize_name(instance_ref)
        if not instance_name:
            return create_gcp_error(
                400,
                "Required field 'instance' not found",
                "INVALID_ARGUMENT",
            )
        if instance_name and instance_name not in self.state.instances:
            return create_gcp_error(
                404,
                f"Instance '{instance_name}' not found",
                "NOT_FOUND",
            )
        network_ref = body.get("network") or ""
        network_name = normalize_name(network_ref)
        if network_name and network_name not in self.state.networks:
            return create_gcp_error(
                404,
                f"Network '{network_name}' not found",
                "NOT_FOUND",
            )
        security_policy_ref = body.get("securityPolicy") or ""
        security_policy_name = normalize_name(security_policy_ref)
        if security_policy_name and security_policy_name not in self.state.security_policies:
            return create_gcp_error(
                404,
                f"SecurityPolicy '{security_policy_name}' not found",
                "NOT_FOUND",
            )

        resource = TargetInstance(
            nat_policy=body.get("natPolicy") or "",
            instance=instance_ref,
            description=body.get("description") or "",
            zone=zone,
            creation_timestamp=body.get("creationTimestamp")
            or datetime.now(timezone.utc).isoformat(),
            security_policy=security_policy_ref,
            name=name,
            network=network_ref,
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        resource_link = (
            f"projects/{project}/zones/{zone}/targetInstances/{resource.name}"
        )
        return make_operation(
            operation_type="insert",
            resource_link=resource_link,
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified TargetInstance resource."""
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
        target_instance = params.get("targetInstance")
        if not target_instance:
            return create_gcp_error(
                400,
                "Required field 'targetInstance' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_target_instance_or_error(target_instance)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of TargetInstance resources available to the specified
project and zone."""
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
                name = match.group(1)
                resources = [resource for resource in resources if resource.name == name]
        if zone:
            resources = [resource for resource in resources if resource.zone == zone]

        return {
            "kind": "compute#targetinstanceList",
            "id": f"projects/{project}/zones/{zone}/targetInstances",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of target instances.

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
                name = match.group(1)
                resources = [resource for resource in resources if resource.name == name]
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        if resources:
            items = {scope_key: {"TargetInstances": [r.to_dict() for r in resources]}}
        else:
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        return {
            "kind": "compute#targetinstanceAggregatedList",
            "id": f"projects/{project}/aggregated/targetInstances",
            "items": items,
            "selfLink": "",
        }

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

        resource = self._get_target_instance_or_error(resource_name)
        if is_error_response(resource):
            return resource
        permissions = body.get("permissions") or []
        return {
            "permissions": permissions,
        }

    def setSecurityPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the Google Cloud Armor security policy for the specified target
instance. For more information, seeGoogle
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
        target_instance = params.get("targetInstance")
        if not target_instance:
            return create_gcp_error(
                400,
                "Required field 'targetInstance' not found",
                "INVALID_ARGUMENT",
            )
        body = params.get("SecurityPolicyReference") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'SecurityPolicyReference' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_target_instance_or_error(target_instance)
        if is_error_response(resource):
            return resource
        if resource.zone and resource.zone != zone:
            resource_path = (
                f"projects/{project}/zones/{zone}/targetInstances/{target_instance}"
            )
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )

        def normalize_name(value: Any) -> str:
            if not isinstance(value, str):
                return ""
            return value.split("/")[-1]

        security_policy_ref = body.get("securityPolicy") or ""
        security_policy_name = normalize_name(security_policy_ref)
        if security_policy_name and not (
            self.state.security_policies.get(security_policy_name)
            or self.state.region_security_policies.get(security_policy_name)
        ):
            return create_gcp_error(
                404,
                f"Security policy '{security_policy_name}' not found",
                "NOT_FOUND",
            )
        resource.security_policy = security_policy_ref
        resource_link = (
            f"projects/{project}/zones/{zone}/targetInstances/{resource.name}"
        )
        return make_operation(
            operation_type="setSecurityPolicy",
            resource_link=resource_link,
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified TargetInstance resource."""
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
        target_instance = params.get("targetInstance")
        if not target_instance:
            return create_gcp_error(
                400,
                "Required field 'targetInstance' not found",
                "INVALID_ARGUMENT",
            )

        resource = self._get_target_instance_or_error(target_instance)
        if is_error_response(resource):
            return resource
        del self.resources[target_instance]
        resource_link = (
            f"projects/{project}/zones/{zone}/targetInstances/{target_instance}"
        )
        return make_operation(
            operation_type="delete",
            resource_link=resource_link,
            params=params,
        )


class target_instance_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'list': target_instance_RequestParser._parse_list,
            'delete': target_instance_RequestParser._parse_delete,
            'aggregatedList': target_instance_RequestParser._parse_aggregatedList,
            'testIamPermissions': target_instance_RequestParser._parse_testIamPermissions,
            'insert': target_instance_RequestParser._parse_insert,
            'get': target_instance_RequestParser._parse_get,
            'setSecurityPolicy': target_instance_RequestParser._parse_setSecurityPolicy,
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
        params['TargetInstance'] = body.get('TargetInstance')
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


class target_instance_ResponseSerializer:
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
            'list': target_instance_ResponseSerializer._serialize_list,
            'delete': target_instance_ResponseSerializer._serialize_delete,
            'aggregatedList': target_instance_ResponseSerializer._serialize_aggregatedList,
            'testIamPermissions': target_instance_ResponseSerializer._serialize_testIamPermissions,
            'insert': target_instance_ResponseSerializer._serialize_insert,
            'get': target_instance_ResponseSerializer._serialize_get,
            'setSecurityPolicy': target_instance_ResponseSerializer._serialize_setSecurityPolicy,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setSecurityPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

