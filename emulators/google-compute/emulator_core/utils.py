"""
GCP Compute emulator shared utilities.

Key differences from EC2 utils:
- Resources are identified by "name" (string) not prefixed IDs
- IDs are large numeric strings, not "vpc-xxx"
- Labels replace Tags (plain dict, not Tag.N.Key/Value)
- Errors use GCP JSON format (not AWS XML)
- Responses are JSON (not XML)
- All mutating operations return Operation objects (faked as DONE)
"""
from __future__ import annotations
import uuid
import random
import json as _json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


# ============================================================================
# Error helpers
# ============================================================================

def create_gcp_error(
    http_code: int,
    message: str,
    reason: str = "invalid",
    domain: str = "global",
    status: str = "INVALID_ARGUMENT",
) -> Dict[str, Any]:
    """Return a structured GCP error dict (detected by is_error_response)."""
    return {
        "Error": {
            "http_code": http_code,
            "message": message,
            "errors": [{"message": message, "domain": domain, "reason": reason}],
            "status": status,
        }
    }


def create_not_found(resource_type: str, name: str, project: str = "project") -> Dict[str, Any]:
    msg = f"The resource '{resource_type}/{name}' was not found"
    return create_gcp_error(404, msg, reason="notFound", status="NOT_FOUND")


def create_already_exists(resource_type: str, name: str) -> Dict[str, Any]:
    msg = f"The resource '{resource_type}/{name}' already exists"
    return create_gcp_error(409, msg, reason="alreadyExists", status="ALREADY_EXISTS")


def create_invalid_param(message: str) -> Dict[str, Any]:
    return create_gcp_error(400, message, reason="invalid", status="INVALID_ARGUMENT")


def is_error_response(data: Any) -> bool:
    return isinstance(data, dict) and "Error" in data


def serialize_gcp_error(data: Dict[str, Any]) -> str:
    """Serialize a GCP error dict to JSON response body."""
    err = data["Error"]
    http_code = err.get("http_code", 400)
    body = {
        "error": {
            "code": http_code,
            "message": err.get("message", "Unknown error"),
            "errors": err.get("errors", []),
            "status": err.get("status", "INVALID_ARGUMENT"),
        }
    }
    return _json.dumps(body)


def get_error_http_code(data: Dict[str, Any]) -> int:
    return data.get("Error", {}).get("http_code", 400)


# ============================================================================
# Operation helper (fake synchronous — always DONE)
# ============================================================================

def make_operation(
    operation_type: str,
    resource_link: Optional[str],
    params: Dict[str, Any],
    zone: Optional[str] = None,
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a fake GCP Operation that is immediately DONE."""
    import re as _re
    project = params.get("project", "emulated-project")
    op_id = str(random.randint(10**17, 10**18 - 1))
    op_name = f"operation-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    now = datetime.now(timezone.utc).isoformat()

    # Auto-extract zone/region from resource_link if not explicitly provided
    if resource_link and not zone and not region:
        zm = _re.search(r"zones/([^/]+)", resource_link)
        rm = _re.search(r"regions/([^/]+)", resource_link)
        if zm:
            zone = zm.group(1)
        elif rm:
            region = rm.group(1)

    if zone:
        scope = f"projects/{project}/zones/{zone}"
        kind = "compute#operation"
    elif region:
        scope = f"projects/{project}/regions/{region}"
        kind = "compute#operation"
    else:
        scope = f"projects/{project}/global"
        kind = "compute#operation"

    op = {
        "kind": kind,
        "id": op_id,
        "name": op_name,
        "operationType": operation_type,
        "status": "DONE",
        "progress": 100,
        "insertTime": now,
        "startTime": now,
        "endTime": now,
        "selfLink": f"https://www.googleapis.com/compute/v1/{scope}/operations/{op_name}",
        "user": "user@example.com",
    }
    # gcloud parses these URI fields to determine zone/region for operation polling
    if zone:
        op["zone"] = f"https://www.googleapis.com/compute/v1/projects/{project}/zones/{zone}"
    if region:
        op["region"] = f"https://www.googleapis.com/compute/v1/projects/{project}/regions/{region}"
    if resource_link:
        op["targetLink"] = resource_link
    return op


# ============================================================================
# Label helpers (GCP equivalent of EC2 tags)
# ============================================================================

def parse_labels(body: Dict[str, Any], key: str = "labels") -> Dict[str, str]:
    """Extract labels dict from a request body."""
    raw = body.get(key, {})
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    return {}


# ============================================================================
# Body param helpers
# ============================================================================

def get_body_param(body: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safe extraction from request body."""
    return body.get(key, default)


def get_query_param(query: Dict[str, Any], key: str, default: Any = None) -> Any:
    return query.get(key, default)


# ============================================================================
# Filter helpers (GCP uses ?filter= with comparisons like "name = foo*")
# ============================================================================

def apply_gcp_filter(items: List[Dict[str, Any]], filter_expr: Optional[str]) -> List[Dict[str, Any]]:
    """Apply a simple GCP filter expression to a list of resource dicts.

    Supports basic equality and prefix matching:
      name = "foo"
      status = "RUNNING"
      name = "foo*"
    """
    if not filter_expr:
        return items

    import re as _re
    # Match: field op value  (op is = or !=)
    m = _re.match(r"""(\w+)\s*(=|!=)\s*["']?([^"'\s]*)["']?""", filter_expr.strip())
    if not m:
        return items

    field, op, value = m.group(1), m.group(2), m.group(3)
    wildcard = value.endswith("*")
    if wildcard:
        value = value[:-1]

    result = []
    for item in items:
        item_val = str(item.get(field, ""))
        if wildcard:
            matches = item_val.startswith(value)
        else:
            matches = item_val == value
        if op == "=" and matches:
            result.append(item)
        elif op == "!=" and not matches:
            result.append(item)
    return result


# ============================================================================
# Pagination
# ============================================================================

def paginate(
    items: List[Any],
    max_results: Optional[int],
    page_token: Optional[str],
) -> tuple:
    """Simple offset-based pagination. Returns (page_items, next_page_token)."""
    if page_token:
        try:
            offset = int(page_token)
        except ValueError:
            offset = 0
    else:
        offset = 0

    if max_results:
        page = items[offset:offset + max_results]
        next_token = str(offset + max_results) if offset + max_results < len(items) else None
    else:
        page = items[offset:]
        next_token = None

    return page, next_token
