from typing import Dict, Any
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class VirtualPrivateGatewayRoutesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage. Use self.state.virtual_private_gateway_routes

    def disable_vgw_route_propagation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        gateway_id = params.get("GatewayId")
        route_table_id = params.get("RouteTableId")
        dry_run = params.get("DryRun", False)

        if gateway_id is None:
            raise ErrorCode("MissingParameter", "GatewayId is required")
        if not isinstance(gateway_id, str):
            raise ErrorCode("InvalidParameterValue", "GatewayId must be a string")

        if route_table_id is None:
            raise ErrorCode("MissingParameter", "RouteTableId is required")
        if not isinstance(route_table_id, str):
            raise ErrorCode("InvalidParameterValue", "RouteTableId must be a string")

        if not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # DryRun check
        if dry_run:
            # Check permissions - here we simulate permission check
            # If user has permission, raise DryRunOperation error
            # Otherwise UnauthorizedOperation
            # For emulator, assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Validate GatewayId exists and is a virtual private gateway
        gateway = self.state.get_resource(gateway_id)
        if gateway is None:
            raise ErrorCode("InvalidGatewayID.NotFound", f"The virtual private gateway '{gateway_id}' does not exist")

        # Validate RouteTableId exists and is a route table
        route_table = self.state.get_resource(route_table_id)
        if route_table is None:
            raise ErrorCode("InvalidRouteTableID.NotFound", f"The route table '{route_table_id}' does not exist")

        # Validate that the virtual private gateway is attached to a VPC
        if not hasattr(gateway, "vpc_id") or gateway.vpc_id is None:
            raise ErrorCode("InvalidGatewayID.NotAttached", f"The virtual private gateway '{gateway_id}' is not attached to any VPC")

        # Validate that the route table is associated with the same VPC as the gateway
        if not hasattr(route_table, "vpc_id") or route_table.vpc_id != gateway.vpc_id:
            raise ErrorCode(
                "InvalidRouteTableID.NotAssociated",
                f"The route table '{route_table_id}' is not associated with the same VPC as the virtual private gateway '{gateway_id}'"
            )

        # Compose key for propagation entry
        propagation_key = f"{gateway_id}:{route_table_id}"

        # Remove propagation if exists
        if propagation_key in self.state.virtual_private_gateway_routes:
            del self.state.virtual_private_gateway_routes[propagation_key]

        # Return success response
        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def enable_vgw_route_propagation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        gateway_id = params.get("GatewayId")
        route_table_id = params.get("RouteTableId")
        dry_run = params.get("DryRun", False)

        if gateway_id is None:
            raise ErrorCode("MissingParameter", "GatewayId is required")
        if not isinstance(gateway_id, str):
            raise ErrorCode("InvalidParameterValue", "GatewayId must be a string")

        if route_table_id is None:
            raise ErrorCode("MissingParameter", "RouteTableId is required")
        if not isinstance(route_table_id, str):
            raise ErrorCode("InvalidParameterValue", "RouteTableId must be a string")

        if not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # DryRun check
        if dry_run:
            # Check permissions - here we simulate permission check
            # If user has permission, raise DryRunOperation error
            # Otherwise UnauthorizedOperation
            # For emulator, assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Validate GatewayId exists and is a virtual private gateway
        gateway = self.state.get_resource(gateway_id)
        if gateway is None:
            raise ErrorCode("InvalidGatewayID.NotFound", f"The virtual private gateway '{gateway_id}' does not exist")

        # Validate RouteTableId exists and is a route table
        route_table = self.state.get_resource(route_table_id)
        if route_table is None:
            raise ErrorCode("InvalidRouteTableID.NotFound", f"The route table '{route_table_id}' does not exist")

        # Validate that the virtual private gateway is attached to a VPC
        if not hasattr(gateway, "vpc_id") or gateway.vpc_id is None:
            raise ErrorCode("InvalidGatewayID.NotAttached", f"The virtual private gateway '{gateway_id}' is not attached to any VPC")

        # Validate that the route table is associated with the same VPC as the gateway
        if not hasattr(route_table, "vpc_id") or route_table.vpc_id != gateway.vpc_id:
            raise ErrorCode(
                "InvalidRouteTableID.NotAssociated",
                f"The route table '{route_table_id}' is not associated with the same VPC as the virtual private gateway '{gateway_id}'"
            )

        # Compose key for propagation entry
        propagation_key = f"{gateway_id}:{route_table_id}"

        # Add propagation entry
        self.state.virtual_private_gateway_routes[propagation_key] = {
            "GatewayId": gateway_id,
            "RouteTableId": route_table_id,
            "OwnerId": self.get_owner_id(),
        }

        # Return success response
        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

from emulator_core.gateway.base import BaseGateway

class VirtualprivategatewayroutesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DisableVgwRoutePropagation", self.disable_vgw_route_propagation)
        self.register_action("EnableVgwRoutePropagation", self.enable_vgw_route_propagation)

    def disable_vgw_route_propagation(self, params):
        return self.backend.disable_vgw_route_propagation(params)

    def enable_vgw_route_propagation(self, params):
        return self.backend.enable_vgw_route_propagation(params)
