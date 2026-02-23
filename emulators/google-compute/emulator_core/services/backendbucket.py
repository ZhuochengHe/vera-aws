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
class BackendBucket:
    params: Dict[str, Any] = field(default_factory=dict)
    enable_cdn: bool = False
    used_by: List[Any] = field(default_factory=list)
    name: str = ""
    description: str = ""
    edge_security_policy: str = ""
    creation_timestamp: str = ""
    compression_mode: str = ""
    bucket_name: str = ""
    load_balancing_scheme: str = ""
    custom_response_headers: List[Any] = field(default_factory=list)
    cdn_policy: Dict[str, Any] = field(default_factory=dict)
    id: str = ""

    signed_url_key_names: List[str] = field(default_factory=list)
    signed_url_keys: Dict[str, Any] = field(default_factory=dict)
    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["params"] = self.params
        d["enableCdn"] = self.enable_cdn
        d["usedBy"] = self.used_by
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.edge_security_policy is not None and self.edge_security_policy != "":
            d["edgeSecurityPolicy"] = self.edge_security_policy
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.compression_mode is not None and self.compression_mode != "":
            d["compressionMode"] = self.compression_mode
        if self.bucket_name is not None and self.bucket_name != "":
            d["bucketName"] = self.bucket_name
        if self.load_balancing_scheme is not None and self.load_balancing_scheme != "":
            d["loadBalancingScheme"] = self.load_balancing_scheme
        d["customResponseHeaders"] = self.custom_response_headers
        d["cdnPolicy"] = self.cdn_policy
        d["signedUrlKeyNames"] = self.signed_url_key_names
        d["signedUrlKeys"] = self.signed_url_keys
        d["iamPolicy"] = self.iam_policy
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#backendbucket"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class BackendBucket_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.backend_buckets  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "backend-bucket") -> str:
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
        """Creates a BackendBucket resource in the specified project using
the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("BackendBucket")
        if not body:
            return create_gcp_error(400, "Required field 'BackendBucket' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"BackendBucket {name!r} already exists", "ALREADY_EXISTS")
        resource = BackendBucket(
            params=params,
            enable_cdn=body.get("enableCdn", False),
            used_by=body.get("usedBy", []),
            name=name,
            description=body.get("description", ""),
            edge_security_policy=body.get("edgeSecurityPolicy", ""),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            compression_mode=body.get("compressionMode", ""),
            bucket_name=body.get("bucketName", ""),
            load_balancing_scheme=body.get("loadBalancingScheme", ""),
            custom_response_headers=body.get("customResponseHeaders", []),
            cdn_policy=body.get("cdnPolicy", {}),
            id=self._generate_id(),
            signed_url_key_names=body.get("signedUrlKeyNames", []),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/backendBuckets/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified BackendBucket resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("backendBucket")
        if not name:
            return create_gcp_error(400, "Required field 'backendBucket' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of BackendBucket resources available to the specified
project."""
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
        return {
            "kind": "compute#backendbucketList",
            "id": f"projects/{project}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified BackendBucket resource with the data included in the
request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("backendBucket")
        if not name:
            return create_gcp_error(400, "Required field 'backendBucket' not specified", "INVALID_ARGUMENT")
        body = params.get("BackendBucket")
        if not body:
            return create_gcp_error(400, "Required field 'BackendBucket' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        resource.params = params
        resource.enable_cdn = body.get("enableCdn", False)
        resource.used_by = body.get("usedBy", [])
        resource.description = body.get("description", "")
        resource.edge_security_policy = body.get("edgeSecurityPolicy", "")
        resource.compression_mode = body.get("compressionMode", "")
        resource.bucket_name = body.get("bucketName", "")
        resource.load_balancing_scheme = body.get("loadBalancingScheme", "")
        resource.custom_response_headers = body.get("customResponseHeaders", [])
        resource.cdn_policy = body.get("cdnPolicy", {})
        resource.signed_url_key_names = body.get("signedUrlKeyNames", [])
        return make_operation(
            operation_type="update",
            resource_link=f"projects/{project}/global/backendBuckets/{resource.name}",
            params=params,
        )

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("GlobalSetPolicyRequest")
        if not body:
            return create_gcp_error(400, "Required field 'GlobalSetPolicyRequest' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        policy = body.get("policy", {})
        resource.iam_policy = policy
        return policy

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the specified BackendBucket resource with the data included in the
request. This method supportsPATCH
semantics and uses theJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("backendBucket")
        if not name:
            return create_gcp_error(400, "Required field 'backendBucket' not specified", "INVALID_ARGUMENT")
        body = params.get("BackendBucket")
        if not body:
            return create_gcp_error(400, "Required field 'BackendBucket' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        resource.params = params
        if "enableCdn" in body:
            resource.enable_cdn = body.get("enableCdn", False)
        if "usedBy" in body:
            resource.used_by = body.get("usedBy", [])
        if "description" in body:
            resource.description = body.get("description", "")
        if "edgeSecurityPolicy" in body:
            resource.edge_security_policy = body.get("edgeSecurityPolicy", "")
        if "compressionMode" in body:
            resource.compression_mode = body.get("compressionMode", "")
        if "bucketName" in body:
            resource.bucket_name = body.get("bucketName", "")
        if "loadBalancingScheme" in body:
            resource.load_balancing_scheme = body.get("loadBalancingScheme", "")
        if "customResponseHeaders" in body:
            resource.custom_response_headers = body.get("customResponseHeaders", [])
        if "cdnPolicy" in body:
            resource.cdn_policy = body.get("cdnPolicy", {})
        if "signedUrlKeyNames" in body:
            resource.signed_url_key_names = body.get("signedUrlKeyNames", [])
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/backendBuckets/{resource.name}",
            params=params,
        )

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.iam_policy or {}

    def addSignedUrlKey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adds a key for validating requests with signed URLs for this backend
bucket."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("backendBucket")
        if not name:
            return create_gcp_error(400, "Required field 'backendBucket' not specified", "INVALID_ARGUMENT")
        body = params.get("SignedUrlKey")
        if not body:
            return create_gcp_error(400, "Required field 'SignedUrlKey' not specified", "INVALID_ARGUMENT")
        key_name = body.get("keyName")
        if not key_name:
            return create_gcp_error(400, "Required field 'keyName' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if key_name in resource.signed_url_keys:
            return create_gcp_error(409, f"SignedUrlKey {key_name!r} already exists", "ALREADY_EXISTS")
        resource.signed_url_keys[key_name] = body
        if key_name not in resource.signed_url_key_names:
            resource.signed_url_key_names.append(key_name)
        return make_operation(
            operation_type="addSignedUrlKey",
            resource_link=f"projects/{project}/global/backendBuckets/{resource.name}",
            params=params,
        )

    def deleteSignedUrlKey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes a key for validating requests with signed URLs for this backend
bucket."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("backendBucket")
        if not name:
            return create_gcp_error(400, "Required field 'backendBucket' not specified", "INVALID_ARGUMENT")
        key_name = params.get("keyName")
        if not key_name:
            return create_gcp_error(400, "Required field 'keyName' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if key_name not in resource.signed_url_keys:
            return create_gcp_error(404, f"SignedUrlKey {key_name!r} was not found", "NOT_FOUND")
        del resource.signed_url_keys[key_name]
        if key_name in resource.signed_url_key_names:
            resource.signed_url_key_names.remove(key_name)
        return make_operation(
            operation_type="deleteSignedUrlKey",
            resource_link=f"projects/{project}/global/backendBuckets/{resource.name}",
            params=params,
        )

    def setEdgeSecurityPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the edge security policy for the specified backend bucket."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("backendBucket")
        if not name:
            return create_gcp_error(400, "Required field 'backendBucket' not specified", "INVALID_ARGUMENT")
        body = params.get("SecurityPolicyReference")
        if not body:
            return create_gcp_error(400, "Required field 'SecurityPolicyReference' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        resource.edge_security_policy = body.get("securityPolicy", "")
        return make_operation(
            operation_type="setEdgeSecurityPolicy",
            resource_link=f"projects/{project}/global/backendBuckets/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest")
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        permissions = body.get("permissions", [])
        return {
            "permissions": permissions,
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified BackendBucket resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        name = params.get("backendBucket")
        if not name:
            return create_gcp_error(400, "Required field 'backendBucket' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if resource.used_by:
            return create_gcp_error(400, "BackendBucket is in use", "FAILED_PRECONDITION")
        del self.resources[name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/backendBuckets/{name}",
            params=params,
        )


class backend_bucket_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'insert': backend_bucket_RequestParser._parse_insert,
            'getIamPolicy': backend_bucket_RequestParser._parse_getIamPolicy,
            'addSignedUrlKey': backend_bucket_RequestParser._parse_addSignedUrlKey,
            'delete': backend_bucket_RequestParser._parse_delete,
            'list': backend_bucket_RequestParser._parse_list,
            'deleteSignedUrlKey': backend_bucket_RequestParser._parse_deleteSignedUrlKey,
            'update': backend_bucket_RequestParser._parse_update,
            'setIamPolicy': backend_bucket_RequestParser._parse_setIamPolicy,
            'patch': backend_bucket_RequestParser._parse_patch,
            'setEdgeSecurityPolicy': backend_bucket_RequestParser._parse_setEdgeSecurityPolicy,
            'testIamPermissions': backend_bucket_RequestParser._parse_testIamPermissions,
            'get': backend_bucket_RequestParser._parse_get,
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
        params['BackendBucket'] = body.get('BackendBucket')
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
    def _parse_addSignedUrlKey(
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
        params['SignedUrlKey'] = body.get('SignedUrlKey')
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
    def _parse_deleteSignedUrlKey(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'keyName' in query_params:
            params['keyName'] = query_params['keyName']
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Full request body (resource representation)
        params["body"] = body
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
        # Body params
        params['BackendBucket'] = body.get('BackendBucket')
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
        params['GlobalSetPolicyRequest'] = body.get('GlobalSetPolicyRequest')
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
        params['BackendBucket'] = body.get('BackendBucket')
        return params

    @staticmethod
    def _parse_setEdgeSecurityPolicy(
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


class backend_bucket_ResponseSerializer:
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
            'insert': backend_bucket_ResponseSerializer._serialize_insert,
            'getIamPolicy': backend_bucket_ResponseSerializer._serialize_getIamPolicy,
            'addSignedUrlKey': backend_bucket_ResponseSerializer._serialize_addSignedUrlKey,
            'delete': backend_bucket_ResponseSerializer._serialize_delete,
            'list': backend_bucket_ResponseSerializer._serialize_list,
            'deleteSignedUrlKey': backend_bucket_ResponseSerializer._serialize_deleteSignedUrlKey,
            'update': backend_bucket_ResponseSerializer._serialize_update,
            'setIamPolicy': backend_bucket_ResponseSerializer._serialize_setIamPolicy,
            'patch': backend_bucket_ResponseSerializer._serialize_patch,
            'setEdgeSecurityPolicy': backend_bucket_ResponseSerializer._serialize_setEdgeSecurityPolicy,
            'testIamPermissions': backend_bucket_ResponseSerializer._serialize_testIamPermissions,
            'get': backend_bucket_ResponseSerializer._serialize_get,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_addSignedUrlKey(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_deleteSignedUrlKey(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setEdgeSecurityPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

