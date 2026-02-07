from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class ClientVpnConnectionStatusCode(str, Enum):
    ACTIVE = "active"
    FAILED_TO_TERMINATE = "failed-to-terminate"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


@dataclass
class ClientVpnConnectionStatus:
    code: ClientVpnConnectionStatusCode
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"code": self.code.value}
        if self.message is not None:
            d["message"] = self.message
        return d


@dataclass
class ClientVpnConnection:
    connection_id: str
    client_vpn_endpoint_id: str
    client_ip: Optional[str] = None
    client_ipv6_address: Optional[str] = None
    common_name: Optional[str] = None
    connection_end_time: Optional[str] = None  # ISO8601 string
    connection_established_time: Optional[str] = None  # ISO8601 string
    egress_bytes: Optional[str] = None
    egress_packets: Optional[str] = None
    ingress_bytes: Optional[str] = None
    ingress_packets: Optional[str] = None
    posture_compliance_status_set: Optional[List[str]] = field(default_factory=list)
    status: Optional[ClientVpnConnectionStatus] = None
    timestamp: Optional[str] = None  # ISO8601 string
    username: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "clientIp": self.client_ip,
            "clientIpv6Address": self.client_ipv6_address,
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "commonName": self.common_name,
            "connectionEndTime": self.connection_end_time,
            "connectionEstablishedTime": self.connection_established_time,
            "connectionId": self.connection_id,
            "egressBytes": self.egress_bytes,
            "egressPackets": self.egress_packets,
            "ingressBytes": self.ingress_bytes,
            "ingressPackets": self.ingress_packets,
            "postureComplianceStatusSet": self.posture_compliance_status_set if self.posture_compliance_status_set else None,
            "status": self.status.to_dict() if self.status else None,
            "timestamp": self.timestamp,
            "username": self.username,
        }
        # Remove keys with None values
        return {k: v for k, v in d.items() if v is not None}


class ClientConnectionsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.client_connections dict for storage

    def describe_client_vpn_connections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter ClientVpnEndpointId
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id or not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode("InvalidParameterValue", "ClientVpnEndpointId is required and must be a string")

        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        # Validate Filters (Filter.N)
        filters = []
        # Filters come as Filter.1, Filter.2, ... or Filter.N keys
        # We collect all keys starting with "Filter."
        for key, value in params.items():
            if key.startswith("Filter."):
                # value should be a dict with Name and Values keys
                if not isinstance(value, dict):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a dict with Name and Values")
                name = value.get("Name")
                values = value.get("Values")
                if name is not None and not isinstance(name, str):
                    raise ErrorCode("InvalidParameterValue", f"{key}.Name must be a string")
                if values is not None:
                    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                        raise ErrorCode("InvalidParameterValue", f"{key}.Values must be a list of strings")
                filters.append({"Name": name, "Values": values})

        # Validate MaxResults if present
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 1000")

        # Validate NextToken if present
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string")

        # Filter connections by ClientVpnEndpointId
        connections = [
            conn for conn in self.state.client_connections.values()
            if conn.client_vpn_endpoint_id == client_vpn_endpoint_id
        ]

        # Apply filters if any
        for f in filters:
            name = f.get("Name")
            values = f.get("Values")
            if not name or not values:
                continue  # skip empty filters
            # Supported filter names: connection-id, username
            if name == "connection-id":
                connections = [c for c in connections if c.connection_id in values]
            elif name == "username":
                connections = [c for c in connections if c.username in values]
            else:
                # Unknown filter name: ignore or raise? AWS ignores unknown filters silently
                pass

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "NextToken is invalid")

        end_index = start_index + (max_results if max_results is not None else len(connections))
        page_connections = connections[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = str(end_index) if end_index < len(connections) else None

        # Prepare response connections list
        response_connections = [conn.to_dict() for conn in page_connections]

        # Generate requestId
        request_id = self.generate_request_id()

        return {
            "connections": response_connections,
            "nextToken": new_next_token,
            "requestId": request_id,
        }

    def terminate_client_vpn_connections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter ClientVpnEndpointId
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id or not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode("InvalidParameterValue", "ClientVpnEndpointId is required and must be a string")

        # Validate optional parameters
        connection_id = params.get("ConnectionId")
        if connection_id is not None and not isinstance(connection_id, str):
            raise ErrorCode("InvalidParameterValue", "ConnectionId must be a string if provided")

        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        username = params.get("Username")
        if username is not None and not isinstance(username, str):
            raise ErrorCode("InvalidParameterValue", "Username must be a string if provided")

        # Validate that either ConnectionId or Username is provided, but not both None
        if connection_id is None and username is None:
            raise ErrorCode("InvalidParameterCombination", "Either ConnectionId or Username must be provided")

        # If Username is provided, check that user has at most 5 active connections
        if username is not None:
            user_connections = [
                c for c in self.state.client_connections.values()
                if c.client_vpn_endpoint_id == client_vpn_endpoint_id and c.username == username and c.status and c.status.code == ClientVpnConnectionStatusCode.ACTIVE
            ]
            if len(user_connections) > 5:
                raise ErrorCode("InvalidParameterValue", "Username has more than 5 active connections, cannot terminate all")

        # Prepare list of connections to terminate
        to_terminate: List[ClientVpnConnection] = []

        if connection_id is not None:
            # Find connection by ID and endpoint
            conn = self.state.client_connections.get(connection_id)
            if not conn or conn.client_vpn_endpoint_id != client_vpn_endpoint_id:
                raise ErrorCode("InvalidClientVpnConnectionId", f"ConnectionId {connection_id} does not exist for the specified ClientVpnEndpointId")
            to_terminate.append(conn)
        else:
            # Terminate all active connections for the username (up to 5)
            to_terminate = [
                c for c in self.state.client_connections.values()
                if c.client_vpn_endpoint_id == client_vpn_endpoint_id and c.username == username and c.status and c.status.code == ClientVpnConnectionStatusCode.ACTIVE
            ]

        connection_statuses = []

        for conn in to_terminate:
            previous_status = conn.status.code if conn.status else None
            # Only active connections can be terminated
            if previous_status != ClientVpnConnectionStatusCode.ACTIVE:
                # If not active, cannot terminate, mark failed-to-terminate
                current_status_code = ClientVpnConnectionStatusCode.FAILED_TO_TERMINATE
                current_status_message = "Connection is not active and cannot be terminated"
            else:
                # Mark as terminating
                current_status_code = ClientVpnConnectionStatusCode.TERMINATING
                current_status_message = None
                # Update connection status to terminating
                conn.status = ClientVpnConnectionStatus(code=current_status_code, message=current_status_message)
                # Simulate immediate termination for emulator: mark terminated and set end time
                conn.status = ClientVpnConnectionStatus(code=ClientVpnConnectionStatusCode.TERMINATED)
                conn.connection_end_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                conn.timestamp = conn.connection_end_time

            connection_statuses.append({
                "connectionId": conn.connection_id,
                "currentStatus": {
                    "code": current_status_code.value,
                    **({"message": current_status_message} if current_status_message else {})
                },
                "previousStatus": {
                    "code": previous_status.value if previous_status else None
                } if previous_status else None
            })

        # Clean None values in connection_statuses
        for status in connection_statuses:
            if status.get("previousStatus") is None:
                status.pop("previousStatus", None)

        request_id = self.generate_request_id()

        return {
            "clientVpnEndpointId": client_vpn_endpoint_id,
            "connectionStatuses": connection_statuses,
            "requestId": request_id,
            "username": username if username is not None else None,
        }

from emulator_core.gateway.base import BaseGateway

class ClientconnectionsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeClientVpnConnections", self.describe_client_vpn_connections)
        self.register_action("TerminateClientVpnConnections", self.terminate_client_vpn_connections)

    def describe_client_vpn_connections(self, params):
        return self.backend.describe_client_vpn_connections(params)

    def terminate_client_vpn_connections(self, params):
        return self.backend.terminate_client_vpn_connections(params)
