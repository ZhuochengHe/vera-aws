from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re
from ..utils import (get_scalar, get_int, get_indexed_list, parse_filters, apply_filters,
                    parse_tags, str2bool, esc, create_error_response,
                    is_error_response, serialize_error_response)
from ..state import EC2State

class ResourceState(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    RUNNING = 'running'
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    NONEXISTENT = 'non-existent'
    FAILED = 'failed'
    SHUTTING_DOWN = 'shutting-down'
    STOPPING = 'stopping'
    STARTING = 'starting'
    REBOOTING = 'rebooting'
    ATTACHED = 'attached'
    IN_USE = 'in-use'
    CREATING = 'creating'

class ErrorCode(Enum):
    INVALID_PARAMETER_VALUE = 'InvalidParameterValue'
    RESOURCE_NOT_FOUND = 'ResourceNotFound'
    INVALID_STATE_TRANSITION = 'InvalidStateTransition'
    DEPENDENCY_VIOLATION = 'DependencyViolation'

@dataclass
class VirtualPrivateGatewayRoute:
    gateway_id: str = ""
    route_table_id: str = ""
    state: str = "enabled"
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatewayId": self.gateway_id,
            "routeTableId": self.route_table_id,
            "state": self.state,
            "enabled": self.enabled,
        }

class VirtualPrivateGatewayRoute_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.virtual_private_gateway_routes  # alias to shared store


    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            value = params.get(name)
            if value is None or value == "":
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _find_propagation(self, gateway_id: str, route_table_id: str):
        for resource_id, resource in self.resources.items():
            if resource.gateway_id == gateway_id and resource.route_table_id == route_table_id:
                return resource_id, resource
        return None, None


    def DisableVgwRoutePropagation(self, params: Dict[str, Any]):
        """Disables a virtual private gateway (VGW) from propagating routes to a specified route
            table of a VPC."""

        error = self._require_params(params, ["GatewayId", "RouteTableId"])
        if error:
            return error

        gateway_id = params.get("GatewayId")
        route_table_id = params.get("RouteTableId")

        gateway = self.state.virtual_private_gateways.get(gateway_id)
        if not gateway:
            return create_error_response(
                "InvalidVpnGatewayID.NotFound",
                f"The VPN gateway '{gateway_id}' does not exist",
            )

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidRouteTableID.NotFound",
                f"The ID '{route_table_id}' does not exist",
            )

        if route_table.propagating_vgw_set is None:
            route_table.propagating_vgw_set = []

        route_table.propagating_vgw_set = [
            item for item in route_table.propagating_vgw_set
            if item.get("gatewayId") != gateway_id
        ]

        resource_id, _ = self._find_propagation(gateway_id, route_table_id)
        if resource_id:
            del self.resources[resource_id]

        return {
            'return': True,
            }

    def EnableVgwRoutePropagation(self, params: Dict[str, Any]):
        """Enables a virtual private gateway (VGW) to propagate routes to the specified route
            table of a VPC."""

        error = self._require_params(params, ["GatewayId", "RouteTableId"])
        if error:
            return error

        gateway_id = params.get("GatewayId")
        route_table_id = params.get("RouteTableId")

        gateway = self.state.virtual_private_gateways.get(gateway_id)
        if not gateway:
            return create_error_response(
                "InvalidVpnGatewayID.NotFound",
                f"The VPN gateway '{gateway_id}' does not exist",
            )

        route_table = self.state.route_tables.get(route_table_id)
        if not route_table:
            return create_error_response(
                "InvalidRouteTableID.NotFound",
                f"The ID '{route_table_id}' does not exist",
            )

        if route_table.propagating_vgw_set is None:
            route_table.propagating_vgw_set = []

        existing = next(
            (item for item in route_table.propagating_vgw_set if item.get("gatewayId") == gateway_id),
            None,
        )
        if not existing:
            route_table.propagating_vgw_set.append({"gatewayId": gateway_id})

        resource_id, resource = self._find_propagation(gateway_id, route_table_id)
        if resource:
            resource.enabled = True
            resource.state = "enabled"
        else:
            resource_id = self._generate_id("vir")
            self.resources[resource_id] = VirtualPrivateGatewayRoute(
                gateway_id=gateway_id,
                route_table_id=route_table_id,
                state="enabled",
                enabled=True,
            )

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'vir') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class virtualprivategatewayroute_RequestParser:
    @staticmethod
    def parse_disable_vgw_route_propagation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GatewayId": get_scalar(md, "GatewayId"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_enable_vgw_route_propagation_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GatewayId": get_scalar(md, "GatewayId"),
            "RouteTableId": get_scalar(md, "RouteTableId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DisableVgwRoutePropagation": virtualprivategatewayroute_RequestParser.parse_disable_vgw_route_propagation_request,
            "EnableVgwRoutePropagation": virtualprivategatewayroute_RequestParser.parse_enable_vgw_route_propagation_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class virtualprivategatewayroute_ResponseSerializer:
    @staticmethod
    def _serialize_dict_to_xml(d: Dict[str, Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a dictionary to XML elements."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(virtualprivategatewayroute_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(virtualprivategatewayroute_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def _serialize_list_to_xml(lst: List[Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a list to XML elements with <tagName> wrapper and <item> children."""
        xml_parts = []
        indent = '    ' * indent_level
        xml_parts.append(f'{indent}<{tag_name}>')
        for item in lst:
            if isinstance(item, dict):
                xml_parts.append(f'{indent}    <item>')
                xml_parts.extend(virtualprivategatewayroute_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(virtualprivategatewayroute_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
            else:
                xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
        xml_parts.append(f'{indent}</{tag_name}>')
        return xml_parts

    @staticmethod
    def _serialize_nested_fields(d: Dict[str, Any], indent_level: int) -> List[str]:
        """Serialize nested fields from a dictionary."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(virtualprivategatewayroute_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(virtualprivategatewayroute_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
                        xml_parts.append(f'{indent}    </item>')
                    else:
                        xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def serialize_disable_vgw_route_propagation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableVgwRoutePropagationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</DisableVgwRoutePropagationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_vgw_route_propagation_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableVgwRoutePropagationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</EnableVgwRoutePropagationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DisableVgwRoutePropagation": virtualprivategatewayroute_ResponseSerializer.serialize_disable_vgw_route_propagation_response,
            "EnableVgwRoutePropagation": virtualprivategatewayroute_ResponseSerializer.serialize_enable_vgw_route_propagation_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

