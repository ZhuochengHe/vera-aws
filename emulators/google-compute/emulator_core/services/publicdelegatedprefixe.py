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
class PublicDelegatedPrefixe:
    parent_prefix: str = ""
    enable_enhanced_ipv4_allocation: bool = False
    name: str = ""
    allocatable_prefix_length: int = 0
    public_delegated_sub_prefixs: List[Any] = field(default_factory=list)
    is_live_migration: bool = False
    mode: str = ""
    ip_cidr_range: str = ""
    creation_timestamp: str = ""
    ipv6_access_type: str = ""
    fingerprint: str = ""
    status: str = ""
    region: str = ""
    byoip_api_version: str = ""
    description: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.parent_prefix is not None and self.parent_prefix != "":
            d["parentPrefix"] = self.parent_prefix
        d["enableEnhancedIpv4Allocation"] = self.enable_enhanced_ipv4_allocation
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.allocatable_prefix_length is not None and self.allocatable_prefix_length != 0:
            d["allocatablePrefixLength"] = self.allocatable_prefix_length
        d["publicDelegatedSubPrefixs"] = self.public_delegated_sub_prefixs
        d["isLiveMigration"] = self.is_live_migration
        if self.mode is not None and self.mode != "":
            d["mode"] = self.mode
        if self.ip_cidr_range is not None and self.ip_cidr_range != "":
            d["ipCidrRange"] = self.ip_cidr_range
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.ipv6_access_type is not None and self.ipv6_access_type != "":
            d["ipv6AccessType"] = self.ipv6_access_type
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.byoip_api_version is not None and self.byoip_api_version != "":
            d["byoipApiVersion"] = self.byoip_api_version
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#publicdelegatedprefixe"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class PublicDelegatedPrefixe_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.public_delegated_prefixes  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "public-delegated-prefixe") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(
        self, name: str
    ) -> tuple[Optional[PublicDelegatedPrefixe], Optional[Dict[str, Any]]]:
        resource = self.resources.get(name)
        if not resource:
            return None, create_gcp_error(
                404, f"The resource {name!r} was not found", "NOT_FOUND"
            )
        return resource, None

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a PublicDelegatedPrefix in the specified project in the given
region using the parameters that are included in the request."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' is missing", "INVALID_ARGUMENT")
        body = params.get("PublicDelegatedPrefix") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'PublicDelegatedPrefix' is missing",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' is missing", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(
                409,
                f"PublicDelegatedPrefix {name!r} already exists",
                "ALREADY_EXISTS",
            )
        creation_timestamp = body.get("creationTimestamp")
        if not creation_timestamp:
            creation_timestamp = datetime.now(timezone.utc).isoformat()
        resource = PublicDelegatedPrefixe(
            parent_prefix=body.get("parentPrefix", ""),
            enable_enhanced_ipv4_allocation=body.get("enableEnhancedIpv4Allocation", False),
            name=name,
            allocatable_prefix_length=body.get("allocatablePrefixLength", 0),
            public_delegated_sub_prefixs=body.get("publicDelegatedSubPrefixs", []),
            is_live_migration=body.get("isLiveMigration", False),
            mode=body.get("mode", ""),
            ip_cidr_range=body.get("ipCidrRange", ""),
            creation_timestamp=creation_timestamp,
            ipv6_access_type=body.get("ipv6AccessType", ""),
            fingerprint=body.get("fingerprint", ""),
            status=body.get("status", ""),
            region=region,
            byoip_api_version=body.get("byoipApiVersion", ""),
            description=body.get("description", ""),
            id=self._generate_id(),
        )
        self.resources[name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/publicDelegatedPrefixes/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified PublicDelegatedPrefix resource in the given region."""
        project = params.get("project")
        region = params.get("region")
        public_delegated_prefix = params.get("publicDelegatedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' is missing", "INVALID_ARGUMENT")
        if not public_delegated_prefix:
            return create_gcp_error(
                400,
                "Required field 'publicDelegatedPrefix' is missing",
                "INVALID_ARGUMENT",
            )
        resource, error = self._get_resource_or_error(public_delegated_prefix)
        if error:
            return error
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource {public_delegated_prefix!r} was not found",
                "NOT_FOUND",
            )
        return resource.to_dict()

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists all PublicDelegatedPrefix resources owned by the specific project
across all scopes.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        if not resources:
            scope_key = "regions/us-central1"
            items = {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
        else:
            items = {}
            for resource in resources:
                scope_key = f"regions/{resource.region or 'us-central1'}"
                bucket = items.setdefault(scope_key, {"PublicDelegatedPrefixes": []})
                bucket["PublicDelegatedPrefixes"].append(resource.to_dict())
        return {
            "kind": "compute#publicdelegatedprefixeAggregatedList",
            "id": f"projects/{project}/aggregated/publicDelegatedPrefixes",
            "items": items,
            "selfLink": "",
        }

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the PublicDelegatedPrefixes for a project in the given region."""
        project = params.get("project")
        region = params.get("region")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' is missing", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [resource for resource in resources if resource.region == region]
        return {
            "kind": "compute#publicdelegatedprefixeList",
            "id": f"projects/{project}/regions/{region}/publicDelegatedPrefixes",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified PublicDelegatedPrefix resource with the data included
in the request. This method supportsPATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        region = params.get("region")
        public_delegated_prefix = params.get("publicDelegatedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' is missing", "INVALID_ARGUMENT")
        if not public_delegated_prefix:
            return create_gcp_error(
                400,
                "Required field 'publicDelegatedPrefix' is missing",
                "INVALID_ARGUMENT",
            )
        body = params.get("PublicDelegatedPrefix") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'PublicDelegatedPrefix' is missing",
                "INVALID_ARGUMENT",
            )
        resource, error = self._get_resource_or_error(public_delegated_prefix)
        if error:
            return error
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource {public_delegated_prefix!r} was not found",
                "NOT_FOUND",
            )
        if "parentPrefix" in body:
            resource.parent_prefix = body.get("parentPrefix") or ""
        if "enableEnhancedIpv4Allocation" in body:
            resource.enable_enhanced_ipv4_allocation = body.get(
                "enableEnhancedIpv4Allocation", False
            )
        if "name" in body and body.get("name"):
            new_name = body.get("name")
            if new_name != resource.name and new_name in self.resources:
                return create_gcp_error(
                    409,
                    f"PublicDelegatedPrefix {new_name!r} already exists",
                    "ALREADY_EXISTS",
                )
            if new_name != resource.name:
                del self.resources[resource.name]
                resource.name = new_name
                self.resources[resource.name] = resource
        if "allocatablePrefixLength" in body:
            resource.allocatable_prefix_length = body.get("allocatablePrefixLength", 0)
        if "publicDelegatedSubPrefixs" in body:
            resource.public_delegated_sub_prefixs = body.get("publicDelegatedSubPrefixs", [])
        if "isLiveMigration" in body:
            resource.is_live_migration = body.get("isLiveMigration", False)
        if "mode" in body:
            resource.mode = body.get("mode", "")
        if "ipCidrRange" in body:
            resource.ip_cidr_range = body.get("ipCidrRange", "")
        if "creationTimestamp" in body:
            resource.creation_timestamp = body.get("creationTimestamp", "")
        if "ipv6AccessType" in body:
            resource.ipv6_access_type = body.get("ipv6AccessType", "")
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint", "")
        if "status" in body:
            resource.status = body.get("status", "")
        if "region" in body:
            resource.region = body.get("region", "")
        if "byoipApiVersion" in body:
            resource.byoip_api_version = body.get("byoipApiVersion", "")
        if "description" in body:
            resource.description = body.get("description", "")
        return make_operation(
            operation_type="patch",
            resource_link=(
                f"projects/{project}/regions/{region}/publicDelegatedPrefixes/{resource.name}"
            ),
            params=params,
        )

    def withdraw(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Withdraws the specified PublicDelegatedPrefix in the given region."""
        project = params.get("project")
        region = params.get("region")
        public_delegated_prefix = params.get("publicDelegatedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' is missing", "INVALID_ARGUMENT")
        if not public_delegated_prefix:
            return create_gcp_error(
                400,
                "Required field 'publicDelegatedPrefix' is missing",
                "INVALID_ARGUMENT",
            )
        resource, error = self._get_resource_or_error(public_delegated_prefix)
        if error:
            return error
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource {public_delegated_prefix!r} was not found",
                "NOT_FOUND",
            )
        return make_operation(
            operation_type="withdraw",
            resource_link=(
                f"projects/{project}/regions/{region}/publicDelegatedPrefixes/{resource.name}"
            ),
            params=params,
        )

    def announce(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Announces the specified PublicDelegatedPrefix in the given region."""
        project = params.get("project")
        region = params.get("region")
        public_delegated_prefix = params.get("publicDelegatedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' is missing", "INVALID_ARGUMENT")
        if not public_delegated_prefix:
            return create_gcp_error(
                400,
                "Required field 'publicDelegatedPrefix' is missing",
                "INVALID_ARGUMENT",
            )
        resource, error = self._get_resource_or_error(public_delegated_prefix)
        if error:
            return error
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource {public_delegated_prefix!r} was not found",
                "NOT_FOUND",
            )
        return make_operation(
            operation_type="announce",
            resource_link=(
                f"projects/{project}/regions/{region}/publicDelegatedPrefixes/{resource.name}"
            ),
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified PublicDelegatedPrefix in the given region."""
        project = params.get("project")
        region = params.get("region")
        public_delegated_prefix = params.get("publicDelegatedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' is missing", "INVALID_ARGUMENT")
        if not region:
            return create_gcp_error(400, "Required field 'region' is missing", "INVALID_ARGUMENT")
        if not public_delegated_prefix:
            return create_gcp_error(
                400,
                "Required field 'publicDelegatedPrefix' is missing",
                "INVALID_ARGUMENT",
            )
        resource, error = self._get_resource_or_error(public_delegated_prefix)
        if error:
            return error
        if resource.region and resource.region != region:
            return create_gcp_error(
                404,
                f"The resource {public_delegated_prefix!r} was not found",
                "NOT_FOUND",
            )
        del self.resources[public_delegated_prefix]
        return make_operation(
            operation_type="delete",
            resource_link=(
                f"projects/{project}/regions/{region}/publicDelegatedPrefixes/{resource.name}"
            ),
            params=params,
        )


class public_delegated_prefixe_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'delete': public_delegated_prefixe_RequestParser._parse_delete,
            'aggregatedList': public_delegated_prefixe_RequestParser._parse_aggregatedList,
            'insert': public_delegated_prefixe_RequestParser._parse_insert,
            'withdraw': public_delegated_prefixe_RequestParser._parse_withdraw,
            'list': public_delegated_prefixe_RequestParser._parse_list,
            'get': public_delegated_prefixe_RequestParser._parse_get,
            'announce': public_delegated_prefixe_RequestParser._parse_announce,
            'patch': public_delegated_prefixe_RequestParser._parse_patch,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['PublicDelegatedPrefix'] = body.get('PublicDelegatedPrefix')
        return params

    @staticmethod
    def _parse_withdraw(
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
    def _parse_announce(
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
        params['PublicDelegatedPrefix'] = body.get('PublicDelegatedPrefix')
        return params


class public_delegated_prefixe_ResponseSerializer:
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
            'delete': public_delegated_prefixe_ResponseSerializer._serialize_delete,
            'aggregatedList': public_delegated_prefixe_ResponseSerializer._serialize_aggregatedList,
            'insert': public_delegated_prefixe_ResponseSerializer._serialize_insert,
            'withdraw': public_delegated_prefixe_ResponseSerializer._serialize_withdraw,
            'list': public_delegated_prefixe_ResponseSerializer._serialize_list,
            'get': public_delegated_prefixe_ResponseSerializer._serialize_get,
            'announce': public_delegated_prefixe_ResponseSerializer._serialize_announce,
            'patch': public_delegated_prefixe_ResponseSerializer._serialize_patch,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_withdraw(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_announce(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

