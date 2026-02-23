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
class ImageFamilyView:
    image: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["image"] = self.image
        d["kind"] = "compute#imagefamilyview"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class ImageFamilyView_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.image_family_views  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "image-family-view") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the latest image that is part of an image family, is not
deprecated and is rolled out in the specified zone."""
        required_fields = ["project", "zone", "family"]
        for field_name in required_fields:
            if not params.get(field_name):
                return create_gcp_error(
                    400,
                    f"Required field '{field_name}' is missing",
                    "INVALID_ARGUMENT",
                )

        family = params.get("family")
        resource = self.resources.get(family)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource {family!r} was not found",
                "NOT_FOUND",
            )

        return resource.to_dict()


class image_family_view_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'get': image_family_view_RequestParser._parse_get,
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


class image_family_view_ResponseSerializer:
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
            'get': image_family_view_ResponseSerializer._serialize_get,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

