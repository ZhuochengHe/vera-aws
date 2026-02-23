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
class PublicAdvertisedPrefixe:
    name: str = ""
    ip_cidr_range: str = ""
    pdp_scope: str = ""
    public_delegated_prefixs: List[Any] = field(default_factory=list)
    description: str = ""
    ipv6_access_type: str = ""
    shared_secret: str = ""
    creation_timestamp: str = ""
    status: str = ""
    dns_verification_ip: str = ""
    byoip_api_version: str = ""
    fingerprint: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.ip_cidr_range is not None and self.ip_cidr_range != "":
            d["ipCidrRange"] = self.ip_cidr_range
        if self.pdp_scope is not None and self.pdp_scope != "":
            d["pdpScope"] = self.pdp_scope
        d["publicDelegatedPrefixs"] = self.public_delegated_prefixs
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.ipv6_access_type is not None and self.ipv6_access_type != "":
            d["ipv6AccessType"] = self.ipv6_access_type
        if self.shared_secret is not None and self.shared_secret != "":
            d["sharedSecret"] = self.shared_secret
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        if self.status is not None and self.status != "":
            d["status"] = self.status
        if self.dns_verification_ip is not None and self.dns_verification_ip != "":
            d["dnsVerificationIp"] = self.dns_verification_ip
        if self.byoip_api_version is not None and self.byoip_api_version != "":
            d["byoipApiVersion"] = self.byoip_api_version
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#publicadvertisedprefixe"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class PublicAdvertisedPrefixe_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.public_advertised_prefixes  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "public-advertised-prefixe") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Any:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(404, f"The resource '{name}' was not found", "NOT_FOUND")
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a PublicAdvertisedPrefix in the specified project
using the parameters that are included in the request."""
        project = params.get("project")
        body = params.get("PublicAdvertisedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'PublicAdvertisedPrefix' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"PublicAdvertisedPrefix '{name}' already exists", "ALREADY_EXISTS")
        resource = PublicAdvertisedPrefixe(
            name=name,
            ip_cidr_range=body.get("ipCidrRange", ""),
            pdp_scope=body.get("pdpScope", ""),
            public_delegated_prefixs=body.get("publicDelegatedPrefixs", []) or [],
            description=body.get("description", ""),
            ipv6_access_type=body.get("ipv6AccessType", ""),
            shared_secret=body.get("sharedSecret", ""),
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            status=body.get("status", ""),
            dns_verification_ip=body.get("dnsVerificationIp", ""),
            byoip_api_version=body.get("byoipApiVersion", ""),
            fingerprint=body.get("fingerprint", ""),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/publicAdvertisedPrefixes/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified PublicAdvertisedPrefix resource."""
        project = params.get("project")
        public_advertised_prefix = params.get("publicAdvertisedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not public_advertised_prefix:
            return create_gcp_error(400, "Required field 'publicAdvertisedPrefix' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(public_advertised_prefix)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the PublicAdvertisedPrefixes for a project."""
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
            "kind": "compute#publicadvertisedprefixeList",
            "id": f"projects/{project}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified Router resource with the data included in the
request. This method supportsPATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        public_advertised_prefix = params.get("publicAdvertisedPrefix")
        body = params.get("PublicAdvertisedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not public_advertised_prefix:
            return create_gcp_error(400, "Required field 'publicAdvertisedPrefix' not specified", "INVALID_ARGUMENT")
        if body is None:
            return create_gcp_error(400, "Required field 'PublicAdvertisedPrefix' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(public_advertised_prefix)
        if is_error_response(resource):
            return resource
        if "ipCidrRange" in body:
            resource.ip_cidr_range = body.get("ipCidrRange") or ""
        if "pdpScope" in body:
            resource.pdp_scope = body.get("pdpScope") or ""
        if "publicDelegatedPrefixs" in body:
            resource.public_delegated_prefixs = body.get("publicDelegatedPrefixs") or []
        if "description" in body:
            resource.description = body.get("description") or ""
        if "ipv6AccessType" in body:
            resource.ipv6_access_type = body.get("ipv6AccessType") or ""
        if "sharedSecret" in body:
            resource.shared_secret = body.get("sharedSecret") or ""
        if "status" in body:
            resource.status = body.get("status") or ""
        if "dnsVerificationIp" in body:
            resource.dns_verification_ip = body.get("dnsVerificationIp") or ""
        if "byoipApiVersion" in body:
            resource.byoip_api_version = body.get("byoipApiVersion") or ""
        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/global/publicAdvertisedPrefixes/{resource.name}",
            params=params,
        )

    def announce(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Announces the specified PublicAdvertisedPrefix"""
        project = params.get("project")
        public_advertised_prefix = params.get("publicAdvertisedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not public_advertised_prefix:
            return create_gcp_error(400, "Required field 'publicAdvertisedPrefix' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(public_advertised_prefix)
        if is_error_response(resource):
            return resource
        resource.status = "ANNOUNCED"
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="announce",
            resource_link=f"projects/{project}/global/publicAdvertisedPrefixes/{resource.name}",
            params=params,
        )

    def withdraw(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Withdraws the specified PublicAdvertisedPrefix"""
        project = params.get("project")
        public_advertised_prefix = params.get("publicAdvertisedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not public_advertised_prefix:
            return create_gcp_error(400, "Required field 'publicAdvertisedPrefix' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(public_advertised_prefix)
        if is_error_response(resource):
            return resource
        resource.status = "WITHDRAWN"
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="withdraw",
            resource_link=f"projects/{project}/global/publicAdvertisedPrefixes/{resource.name}",
            params=params,
        )

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified PublicAdvertisedPrefix"""
        project = params.get("project")
        public_advertised_prefix = params.get("publicAdvertisedPrefix")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        if not public_advertised_prefix:
            return create_gcp_error(400, "Required field 'publicAdvertisedPrefix' not specified", "INVALID_ARGUMENT")
        resource = self._get_resource_or_error(public_advertised_prefix)
        if is_error_response(resource):
            return resource
        del self.resources[resource.name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/publicAdvertisedPrefixes/{resource.name}",
            params=params,
        )


class public_advertised_prefixe_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'patch': public_advertised_prefixe_RequestParser._parse_patch,
            'announce': public_advertised_prefixe_RequestParser._parse_announce,
            'get': public_advertised_prefixe_RequestParser._parse_get,
            'insert': public_advertised_prefixe_RequestParser._parse_insert,
            'withdraw': public_advertised_prefixe_RequestParser._parse_withdraw,
            'list': public_advertised_prefixe_RequestParser._parse_list,
            'delete': public_advertised_prefixe_RequestParser._parse_delete,
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
        params['PublicAdvertisedPrefix'] = body.get('PublicAdvertisedPrefix')
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
        params['PublicAdvertisedPrefix'] = body.get('PublicAdvertisedPrefix')
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


class public_advertised_prefixe_ResponseSerializer:
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
            'patch': public_advertised_prefixe_ResponseSerializer._serialize_patch,
            'announce': public_advertised_prefixe_ResponseSerializer._serialize_announce,
            'get': public_advertised_prefixe_ResponseSerializer._serialize_get,
            'insert': public_advertised_prefixe_ResponseSerializer._serialize_insert,
            'withdraw': public_advertised_prefixe_ResponseSerializer._serialize_withdraw,
            'list': public_advertised_prefixe_ResponseSerializer._serialize_list,
            'delete': public_advertised_prefixe_ResponseSerializer._serialize_delete,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_announce(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
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
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

