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
class LicenseCode:
    name: str = ""
    creation_timestamp: str = ""
    description: str = ""
    license_alias: List[Any] = field(default_factory=list)
    state: str = ""
    transferable: bool = False
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.description is not None and self.description != "":
            d["description"] = self.description
        d["licenseAlias"] = self.license_alias
        if self.state is not None and self.state != "":
            d["state"] = self.state
        d["transferable"] = self.transferable
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#licensecode"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class LicenseCode_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.license_codes  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "license-code") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a specified license code. License codes are mirrored across
all projects that have permissions to read the License Code.
 *Caution* This resource is intended
for use only by third-party part..."""
        project = params.get("project")
        license_code = params.get("licenseCode")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not license_code:
            return create_gcp_error(400, "Required field 'licenseCode' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(license_code)
        if not resource:
            resource_path = f"projects/{project}/global/licenseCodes/{license_code}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource.
 *Caution* This resource is intended
for use only by third-party partners who are creatingCloud Marketplace
images."""
        project = params.get("project")
        resource_name = params.get("resource")
        body = params.get("TestPermissionsRequest")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not resource_name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(resource_name)
        if not resource:
            resource_path = f"projects/{project}/global/licenseCodes/{resource_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        permissions = body.get("permissions", []) or []
        return {
            "kind": "compute#testPermissionsResponse",
            "permissions": permissions,
        }


class license_code_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': license_code_RequestParser._parse_get,
            'testIamPermissions': license_code_RequestParser._parse_testIamPermissions,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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


class license_code_ResponseSerializer:
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
            'get': license_code_ResponseSerializer._serialize_get,
            'testIamPermissions': license_code_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

