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
class InstanceSetting:
    fingerprint: str = ""
    zone: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.fingerprint is not None and self.fingerprint != "":
            d["fingerprint"] = self.fingerprint
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.name is not None and self.name != "":
            d["name"] = self.name
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["metadata"] = self.metadata
        d["kind"] = "compute#instancesetting"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class InstanceSetting_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.instance_settings  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "instance-setting") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Instance settings."""
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

        resource = self.resources.get(zone)
        if not resource:
            resource = next(
                (
                    value
                    for value in self.resources.values()
                    if getattr(value, "zone", "") == zone
                ),
                None,
            )
        if not resource:
            return create_gcp_error(
                404,
                f"The resource {zone!r} was not found",
                "NOT_FOUND",
            )

        return resource.to_dict()

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patch Instance settings"""
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
        body = params.get("InstanceSettings") or {}
        if not body:
            return create_gcp_error(
                400,
                "Required field 'InstanceSettings' not found",
                "INVALID_ARGUMENT",
            )

        resource_key = zone
        resource = self.resources.get(resource_key)
        if not resource:
            for key, value in self.resources.items():
                if getattr(value, "zone", "") == zone:
                    resource = value
                    resource_key = key
                    break
        if not resource:
            return create_gcp_error(
                404,
                f"The resource {zone!r} was not found",
                "NOT_FOUND",
            )

        if not resource.name:
            resource.name = resource_key
        if not resource.id:
            resource.id = self._generate_id()
        resource.zone = zone

        if "fingerprint" in body:
            resource.fingerprint = body.get("fingerprint") or ""
        if "metadata" in body:
            resource.metadata = body.get("metadata") or {}

        resource_link = (
            f"projects/{project}/zones/{zone}/InstanceSettings/{resource.name}"
        )
        return make_operation(
            operation_type="patch",
            resource_link=resource_link,
            params=params,
        )


class instance_setting_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': instance_setting_RequestParser._parse_get,
            'patch': instance_setting_RequestParser._parse_patch,
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
        if 'updateMask' in query_params:
            params['updateMask'] = query_params['updateMask']
        # Body params
        params['InstanceSettings'] = body.get('InstanceSettings')
        return params


class instance_setting_ResponseSerializer:
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
            'get': instance_setting_ResponseSerializer._serialize_get,
            'patch': instance_setting_ResponseSerializer._serialize_patch,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

