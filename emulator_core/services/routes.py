from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class RouteOrigin(Enum):
    ASSOCIATE = "associate"
    ADD_ROUTE = "add-route"


class RouteStatusCode(Enum):
    CREATING = "creating"
    ACTIVE = "active"
    FAILED = "failed"
    DELETING = "deleting"


@dataclass
class ClientVpnRouteStatus:
    code: RouteStatusCode
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"code": self.code.value}
        if self.message is not None:
            d["message"] = self.message
        return d


@dataclass
class ClientVpnRoute:
    client_vpn_endpoint_id: str
    destination_cidr: str
    target_subnet: str
    origin: RouteOrigin
    status: ClientVpnRouteStatus
    description: Optional[str] = None
    type: Optional[str] = None  # The resource JSON shows "type" but no details, keep optional

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "destinationCidr": self.destination_cidr,
            "targetSubnet": self.target_subnet,
            "origin": self.origin.value,
            "status": self.status.to_dict(),
        }
        if self.description is not None:
            d["description"] = self.description
        if self.type is not None:
            d["type"] = self.type
        return d


class RoutesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.routes dict for storage

    def _validate_cidr(self, cidr: str) -> None:
        # Basic validation for CIDR format (IPv4)
        import ipaddress
        try:
            network = ipaddress.IPv4Network(cidr, strict=False)
        except Exception:
            raise ErrorCode.InvalidParameterValue(f"Invalid CIDR block: {cidr}")

    def _validate_client_vpn_endpoint(self, client_vpn_endpoint_id: str) -> None:
        # Validate existence of Client VPN Endpoint resource
        endpoint = self.state.get_resource(client_vpn_endpoint_id)
        if endpoint is None:
            raise ErrorCode.ClientVpnEndpointNotFound(f"ClientVpnEndpointId {client_vpn_endpoint_id} does not exist")

    def _validate_subnet(self, subnet_id: str) -> None:
        # Validate existence of subnet resource
        subnet = self.state.get_resource(subnet_id)
        if subnet is None:
            raise ErrorCode.SubnetNotFound(f"Subnet {subnet_id} does not exist")

    def _find_route_key(self, client_vpn_endpoint_id: str, destination_cidr: str, target_subnet: str) -> Optional[str]:
        # Routes are stored in self.state.routes keyed by a unique route id.
        # We need to find a route matching these three keys.
        for route_id, route in self.state.routes.items():
            if (
                route.client_vpn_endpoint_id == client_vpn_endpoint_id
                and route.destination_cidr == destination_cidr
                and route.target_subnet == target_subnet
            ):
                return route_id
        return None

    def create_client_vpn_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        destination_cidr_block = params.get("DestinationCidrBlock")
        target_vpc_subnet_id = params.get("TargetVpcSubnetId")
        description = params.get("Description")
        # ClientToken and DryRun are optional, but DryRun is not implemented here (would raise error if needed)

        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")
        if destination_cidr_block is None:
            raise ErrorCode.MissingParameter("DestinationCidrBlock is required")
        if target_vpc_subnet_id is None:
            raise ErrorCode.MissingParameter("TargetVpcSubnetId is required")

        # Validate CIDR format
        self._validate_cidr(destination_cidr_block)

        # Validate Client VPN Endpoint existence
        self._validate_client_vpn_endpoint(client_vpn_endpoint_id)

        # Validate subnet existence or special "local" value
        if target_vpc_subnet_id != "local":
            self._validate_subnet(target_vpc_subnet_id)

        # Check if route already exists (idempotency)
        existing_route_id = self._find_route_key(client_vpn_endpoint_id, destination_cidr_block, target_vpc_subnet_id)
        if existing_route_id is not None:
            # Return existing route status as active (simulate)
            existing_route = self.state.routes[existing_route_id]
            return {
                "requestId": self.generate_request_id(),
                "status": existing_route.status.to_dict(),
            }

        # Create new route
        route_id = f"route-{self.generate_unique_id()}"
        route_status = ClientVpnRouteStatus(code=RouteStatusCode.CREATING)
        route = ClientVpnRoute(
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            destination_cidr=destination_cidr_block,
            target_subnet=target_vpc_subnet_id,
            origin=RouteOrigin.ADD_ROUTE,
            status=route_status,
            description=description,
            type=None,
        )

        self.state.routes[route_id] = route

        return {
            "requestId": self.generate_request_id(),
            "status": route_status.to_dict(),
        }

    def delete_client_vpn_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        destination_cidr_block = params.get("DestinationCidrBlock")
        target_vpc_subnet_id = params.get("TargetVpcSubnetId")  # optional

        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")
        if destination_cidr_block is None:
            raise ErrorCode.MissingParameter("DestinationCidrBlock is required")

        # Validate Client VPN Endpoint existence
        self._validate_client_vpn_endpoint(client_vpn_endpoint_id)

        # Validate CIDR format
        self._validate_cidr(destination_cidr_block)

        # If TargetVpcSubnetId provided, validate subnet existence
        if target_vpc_subnet_id is not None and target_vpc_subnet_id != "local":
            self._validate_subnet(target_vpc_subnet_id)

        # Find route to delete
        # If TargetVpcSubnetId is None, try to find any route with matching clientVpnEndpointId and destinationCidr
        route_id_to_delete = None
        if target_vpc_subnet_id is not None:
            route_id_to_delete = self._find_route_key(client_vpn_endpoint_id, destination_cidr_block, target_vpc_subnet_id)
        else:
            # Search for any route with matching clientVpnEndpointId and destinationCidr
            for route_id, route in self.state.routes.items():
                if (
                    route.client_vpn_endpoint_id == client_vpn_endpoint_id
                    and route.destination_cidr == destination_cidr_block
                ):
                    route_id_to_delete = route_id
                    break

        if route_id_to_delete is None:
            raise ErrorCode.ClientVpnRouteNotFound("The specified route does not exist or cannot be deleted")

        route = self.state.routes[route_id_to_delete]

        # Only routes with origin add-route can be deleted
        if route.origin != RouteOrigin.ADD_ROUTE:
            raise ErrorCode.ClientVpnRouteNotDeletable("Cannot delete routes that were not manually added")

        # Mark route as deleting
        route.status = ClientVpnRouteStatus(code=RouteStatusCode.DELETING)
        # Remove route from state (simulate immediate deletion)
        del self.state.routes[route_id_to_delete]

        return {
            "requestId": self.generate_request_id(),
            "status": route.status.to_dict(),
        }

    def describe_client_vpn_routes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")

        # Validate Client VPN Endpoint existence
        self._validate_client_vpn_endpoint(client_vpn_endpoint_id)

        # Validate MaxResults if provided
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode.InvalidParameterValue("MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode.InvalidParameterValue("MaxResults must be between 5 and 1000")

        # Parse filters
        # Filters supported:
        # destination-cidr-, origin-, target-subnet-
        # Filters param is expected as a list of dicts with keys "Name" and "Values"
        filter_destination_cidr = None
        filter_origin = None
        filter_target_subnet = None

        if filters:
            if not isinstance(filters, list):
                raise ErrorCode.InvalidParameterValue("Filter must be a list")
            for f in filters:
                if not isinstance(f, dict):
                    raise ErrorCode.InvalidParameterValue("Each filter must be a dict")
                name = f.get("Name")
                values = f.get("Values")
                if name is None or values is None:
                    raise ErrorCode.InvalidParameterValue("Filter must have Name and Values")
                if not isinstance(values, list):
                    raise ErrorCode.InvalidParameterValue("Filter Values must be a list")
                if name == "destination-cidr":
                    filter_destination_cidr = set(values)
                elif name == "origin":
                    # Validate origin values
                    for v in values:
                        if v not in (RouteOrigin.ASSOCIATE.value, RouteOrigin.ADD_ROUTE.value):
                            raise ErrorCode.InvalidParameterValue(f"Invalid origin filter value: {v}")
                    filter_origin = set(values)
                elif name == "target-subnet":
                    filter_target_subnet = set(values)
                else:
                    # Unknown filter name, ignore or raise error? AWS usually ignores unknown filters.
                    pass

        # Collect routes matching clientVpnEndpointId
        matching_routes = [
            route for route in self.state.routes.values()
            if route.client_vpn_endpoint_id == client_vpn_endpoint_id
        ]

        # Apply filters
        if filter_destination_cidr is not None:
            matching_routes = [r for r in matching_routes if r.destination_cidr in filter_destination_cidr]
        if filter_origin is not None:
            matching_routes = [r for r in matching_routes if r.origin.value in filter_origin]
        if filter_target_subnet is not None:
            matching_routes = [r for r in matching_routes if r.target_subnet in filter_target_subnet]

        # Pagination
        # next_token is expected to be a string representing an integer offset
        start_index = 0
        if next_token is not None:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index > len(matching_routes):
                    raise ValueError()
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken")

        end_index = len(matching_routes)
        if max_results is not None:
            end_index = min(start_index + max_results, len(matching_routes))

        paged_routes = matching_routes[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(matching_routes):
            new_next_token = str(end_index)

        return {
            "requestId": self.generate_request_id(),
            "routes": [route.to_dict() for route in paged_routes],
            "nextToken": new_next_token,
        }

from emulator_core.gateway.base import BaseGateway

class RoutesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateClientVpnRoute", self.create_client_vpn_route)
        self.register_action("DeleteClientVpnRoute", self.delete_client_vpn_route)
        self.register_action("DescribeClientVpnRoutes", self.describe_client_vpn_routes)

    def create_client_vpn_route(self, params):
        return self.backend.create_client_vpn_route(params)

    def delete_client_vpn_route(self, params):
        return self.backend.delete_client_vpn_route(params)

    def describe_client_vpn_routes(self, params):
        return self.backend.describe_client_vpn_routes(params)
