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
class License:
    allowed_replacement_licenses: List[Any] = field(default_factory=list)
    os_license: bool = False
    required_coattached_licenses: List[Any] = field(default_factory=list)
    update_timestamp: str = ""
    incompatible_licenses: List[Any] = field(default_factory=list)
    minimum_retention: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    appendable_to_disk: bool = False
    sole_tenant_only: bool = False
    license_code: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    removable_from_disk: bool = False
    description: str = ""
    self_link_with_id: str = ""
    transferable: bool = False
    charges_use_fee: bool = False
    creation_timestamp: str = ""
    multi_tenant_only: bool = False
    id: str = ""

    iam_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["allowedReplacementLicenses"] = self.allowed_replacement_licenses
        d["osLicense"] = self.os_license
        d["requiredCoattachedLicenses"] = self.required_coattached_licenses
        if self.update_timestamp is not None and self.update_timestamp != "":
            d["updateTimestamp"] = self.update_timestamp
        d["incompatibleLicenses"] = self.incompatible_licenses
        d["minimumRetention"] = self.minimum_retention
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["appendableToDisk"] = self.appendable_to_disk
        d["soleTenantOnly"] = self.sole_tenant_only
        if self.license_code is not None and self.license_code != "":
            d["licenseCode"] = self.license_code
        d["params"] = self.params
        d["resourceRequirements"] = self.resource_requirements
        d["removableFromDisk"] = self.removable_from_disk
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.self_link_with_id is not None and self.self_link_with_id != "":
            d["selfLinkWithId"] = self.self_link_with_id
        d["transferable"] = self.transferable
        d["chargesUseFee"] = self.charges_use_fee
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["multiTenantOnly"] = self.multi_tenant_only
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#license"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class License_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.licenses  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "license") -> str:
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
        """Create a License resource in the specified project.
 *Caution* This resource is intended
for use only by third-party partners who are creatingCloud Marketplace
images."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        body = params.get("License")
        if not body:
            return create_gcp_error(400, "Required field 'License' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"License {name!r} already exists", "ALREADY_EXISTS")
        resource = License(
            allowed_replacement_licenses=body.get("allowedReplacementLicenses", []),
            os_license=body.get("osLicense", False),
            required_coattached_licenses=body.get("requiredCoattachedLicenses", []),
            update_timestamp=body.get("updateTimestamp", ""),
            incompatible_licenses=body.get("incompatibleLicenses", []),
            minimum_retention=body.get("minimumRetention", {}),
            name=name,
            appendable_to_disk=body.get("appendableToDisk", False),
            sole_tenant_only=body.get("soleTenantOnly", False),
            license_code=body.get("licenseCode", ""),
            params=body.get("params", {}),
            resource_requirements=body.get("resourceRequirements", {}),
            removable_from_disk=body.get("removableFromDisk", False),
            description=body.get("description", ""),
            self_link_with_id=body.get("selfLinkWithId", ""),
            transferable=body.get("transferable", False),
            charges_use_fee=body.get("chargesUseFee", False),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            multi_tenant_only=body.get("multiTenantOnly", False),
            id=self._generate_id(),
            iam_policy=body.get("iamPolicy") or {},
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/licenses/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified License resource.
 *Caution* This resource is intended
for use only by third-party partners who are creatingCloud Marketplace
images."""
        project = params.get("project")
        license_name = params.get("license")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not license_name:
            return create_gcp_error(400, "Required field 'license' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(license_name)
        if is_error_response(resource):
            resource_path = f"projects/{project}/global/licenses/{license_name}"
            return create_gcp_error(
                404,
                f"The resource '{resource_path}' was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of licenses
available in the specified project. This method does not
get any licenses that belong to other projects, including licenses attached
to publicly-available images, lik..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [resource for resource in resources if resource.name == match.group(1)]
        return {
            "kind": "compute#licenseList",
            "id": f"projects/{project}/global/licenses",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a License resource in the specified project.
 *Caution* This resource is intended
for use only by third-party partners who are creatingCloud Marketplace
images."""
        project = params.get("project")
        license_name = params.get("license")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not license_name:
            return create_gcp_error(400, "Required field 'license' not specified", "INVALID_ARGUMENT")
        body = params.get("License")
        if not body:
            return create_gcp_error(400, "Required field 'License' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(license_name)
        if not resource:
            return create_gcp_error(404, f"The resource {license_name!r} was not found", "NOT_FOUND")
        resource.allowed_replacement_licenses = body.get("allowedReplacementLicenses", [])
        resource.os_license = body.get("osLicense", False)
        resource.required_coattached_licenses = body.get("requiredCoattachedLicenses", [])
        resource.update_timestamp = datetime.now(timezone.utc).isoformat()
        resource.incompatible_licenses = body.get("incompatibleLicenses", [])
        resource.minimum_retention = body.get("minimumRetention", {})
        resource.appendable_to_disk = body.get("appendableToDisk", False)
        resource.sole_tenant_only = body.get("soleTenantOnly", False)
        resource.license_code = body.get("licenseCode", "")
        resource.params = body.get("params", {})
        resource.resource_requirements = body.get("resourceRequirements", {})
        resource.removable_from_disk = body.get("removableFromDisk", False)
        resource.description = body.get("description", "")
        resource.self_link_with_id = body.get("selfLinkWithId", "")
        resource.transferable = body.get("transferable", False)
        resource.charges_use_fee = body.get("chargesUseFee", False)
        resource.multi_tenant_only = body.get("multiTenantOnly", False)
        if "iamPolicy" in body:
            resource.iam_policy = body.get("iamPolicy") or {}
        return make_operation(
            operation_type="update",
            resource_link=f"projects/{project}/global/licenses/{resource.name}",
            params=params,
        )

    def setIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sets the access control policy on the specified resource.
Replaces any existing policy.
 *Caution* This resource is intended
for use only by third-party partners who are creatingCloud Marketplace
i..."""
        project = params.get("project")
        name = params.get("resource")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
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
            resource_path = f"projects/{project}/global/licenses/{resource_name}"
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

    def getIamPolicy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gets the access control policy for a resource. May be empty if no such
policy or resource exists.
 *Caution* This resource is intended
for use only by third-party partners who are creatingCloud Mar..."""
        project = params.get("project")
        name = params.get("resource")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.iam_policy or {}

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified license.
 *Caution* This resource is intended
for use only by third-party partners who are creatingCloud Marketplace
images."""
        project = params.get("project")
        license_name = params.get("license")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not license_name:
            return create_gcp_error(400, "Required field 'license' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(license_name)
        if not resource:
            return create_gcp_error(404, f"The resource {license_name!r} was not found", "NOT_FOUND")
        del self.resources[license_name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/licenses/{license_name}",
            params=params,
        )


class license_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': license_RequestParser._parse_get,
            'delete': license_RequestParser._parse_delete,
            'list': license_RequestParser._parse_list,
            'update': license_RequestParser._parse_update,
            'testIamPermissions': license_RequestParser._parse_testIamPermissions,
            'insert': license_RequestParser._parse_insert,
            'getIamPolicy': license_RequestParser._parse_getIamPolicy,
            'setIamPolicy': license_RequestParser._parse_setIamPolicy,
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
        params['License'] = body.get('License')
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
        params['License'] = body.get('License')
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
        params['GlobalSetPolicyRequest'] = body.get('GlobalSetPolicyRequest')
        return params


class license_ResponseSerializer:
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
            'get': license_ResponseSerializer._serialize_get,
            'delete': license_ResponseSerializer._serialize_delete,
            'list': license_ResponseSerializer._serialize_list,
            'update': license_ResponseSerializer._serialize_update,
            'testIamPermissions': license_ResponseSerializer._serialize_testIamPermissions,
            'insert': license_ResponseSerializer._serialize_insert,
            'getIamPolicy': license_ResponseSerializer._serialize_getIamPolicy,
            'setIamPolicy': license_ResponseSerializer._serialize_setIamPolicy,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_update(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_getIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_setIamPolicy(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

