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
class Route:
    client_vpn_endpoint_id: str = ""
    description: str = ""
    destination_cidr: str = ""
    origin: str = ""
    status: Dict[str, Any] = field(default_factory=dict)
    target_subnet: str = ""
    type: str = ""

    # Internal dependency tracking — not in API response
    target_network_ids: List[str] = field(default_factory=list)  # tracks TargetNetwork children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "description": self.description,
            "destinationCidr": self.destination_cidr,
            "origin": self.origin,
            "status": self.status,
            "targetSubnet": self.target_subnet,
            "type": self.type,
        }

class Route_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.routes  # alias to shared store

    def _find_route(self, client_vpn_endpoint_id: str, destination_cidr: str) -> Optional[Route]:
        for route in self.resources.values():
            if (route.client_vpn_endpoint_id == client_vpn_endpoint_id
                    and route.destination_cidr == destination_cidr):
                return route
        return None

    def _filter_routes_by_endpoint(self, client_vpn_endpoint_id: str) -> List[Route]:
        return [
            route for route in self.resources.values()
            if route.client_vpn_endpoint_id == client_vpn_endpoint_id
        ]


    def CreateClientVpnRoute(self, params: Dict[str, Any]):
        """Adds a route to a network to a Client VPN endpoint. Each Client VPN endpoint has a route table that describes the 
			available destination network routes. Each route in the route table specifies the path for traï¬c to speciï¬c resources or networks."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        destination_cidr = params.get("DestinationCidrBlock")
        target_subnet_id = params.get("TargetVpcSubnetId")

        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")
        if not destination_cidr:
            return create_error_response("MissingParameter", "DestinationCidrBlock is required.")
        if not target_subnet_id:
            return create_error_response("MissingParameter", "TargetVpcSubnetId is required.")

        endpoint = self.state.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )

        if not self.state.subnets.get(target_subnet_id):
            return create_error_response(
                "InvalidSubnetID.NotFound",
                f"Subnet '{target_subnet_id}' does not exist.",
            )

        existing = self._find_route(client_vpn_endpoint_id, destination_cidr)
        if existing:
            status = existing.status or {"code": "active", "message": "Route is active"}
            return {
                'status': [status],
                }

        status = {"code": "active", "message": "Route is active"}
        resource = Route(
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            description=params.get("Description") or "",
            destination_cidr=destination_cidr,
            origin="add-route",
            status=status,
            target_subnet=target_subnet_id,
            type="nat",
        )
        resource_id = destination_cidr
        self.resources[resource_id] = resource

        return {
            'status': [status],
            }

    def DeleteClientVpnRoute(self, params: Dict[str, Any]):
        """Deletes a route from a Client VPN endpoint. You can only delete routes that you manually added using 
			theCreateClientVpnRouteaction. You cannot delete routes that were 
			automatically added when associating a subnet. To remove routes that have been automatically added, 
			disassociate the targ"""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        destination_cidr = params.get("DestinationCidrBlock")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")
        if not destination_cidr:
            return create_error_response("MissingParameter", "DestinationCidrBlock is required.")

        endpoint = self.state.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )

        resource_id = None
        route = None
        for candidate_id, candidate in self.resources.items():
            if (candidate.client_vpn_endpoint_id == client_vpn_endpoint_id
                    and candidate.destination_cidr == destination_cidr):
                resource_id = candidate_id
                route = candidate
                break

        if not route:
            return create_error_response(
                "InvalidClientVpnRoute.NotFound",
                "The specified route does not exist.",
            )

        if getattr(route, "target_network_ids", []):
            return create_error_response(
                "DependencyViolation",
                "Route has dependent TargetNetwork(s) and cannot be deleted.",
            )

        if resource_id is not None:
            self.resources.pop(resource_id, None)

        status = {"code": "deleted", "message": "Route deleted"}
        return {
            'status': [status],
            }

    def DescribeClientVpnRoutes(self, params: Dict[str, Any]):
        """Describes the routes for the specified Client VPN endpoint."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")

        endpoint = self.state.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )

        routes = self._filter_routes_by_endpoint(client_vpn_endpoint_id)
        filters = params.get("Filter.N") or []
        if filters:
            routes = apply_filters(routes, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = int(next_token or 0)
        paged_routes = routes[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(routes):
            new_next_token = str(start_index + max_results)

        return {
            'nextToken': new_next_token,
            'routes': [route.to_dict() for route in paged_routes],
            }

    def _generate_id(self, prefix: str = 'client') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class route_RequestParser:
    @staticmethod
    def parse_create_client_vpn_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "Description": get_scalar(md, "Description"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TargetVpcSubnetId": get_scalar(md, "TargetVpcSubnetId"),
        }

    @staticmethod
    def parse_delete_client_vpn_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TargetVpcSubnetId": get_scalar(md, "TargetVpcSubnetId"),
        }

    @staticmethod
    def parse_describe_client_vpn_routes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateClientVpnRoute": route_RequestParser.parse_create_client_vpn_route_request,
            "DeleteClientVpnRoute": route_RequestParser.parse_delete_client_vpn_route_request,
            "DescribeClientVpnRoutes": route_RequestParser.parse_describe_client_vpn_routes_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class route_ResponseSerializer:
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
                xml_parts.extend(route_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(route_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(route_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(route_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(route_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(route_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_client_vpn_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateClientVpnRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize status
        _status_key = None
        if "status" in data:
            _status_key = "status"
        elif "Status" in data:
            _status_key = "Status"
        if _status_key:
            param_data = data[_status_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(route_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</CreateClientVpnRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_client_vpn_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteClientVpnRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize status
        _status_key = None
        if "status" in data:
            _status_key = "status"
        elif "Status" in data:
            _status_key = "Status"
        if _status_key:
            param_data = data[_status_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(route_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</DeleteClientVpnRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_client_vpn_routes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeClientVpnRoutesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        # Serialize routes
        _routes_key = None
        if "routes" in data:
            _routes_key = "routes"
        elif "Routes" in data:
            _routes_key = "Routes"
        if _routes_key:
            param_data = data[_routes_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<routesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(route_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</routesSet>')
            else:
                xml_parts.append(f'{indent_str}<routesSet/>')
        xml_parts.append(f'</DescribeClientVpnRoutesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateClientVpnRoute": route_ResponseSerializer.serialize_create_client_vpn_route_response,
            "DeleteClientVpnRoute": route_ResponseSerializer.serialize_delete_client_vpn_route_response,
            "DescribeClientVpnRoutes": route_ResponseSerializer.serialize_describe_client_vpn_routes_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

