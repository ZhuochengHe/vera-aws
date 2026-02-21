from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
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
class ClientConnection:
    client_ip: str = ""
    client_ipv6_address: str = ""
    client_vpn_endpoint_id: str = ""
    common_name: str = ""
    connection_end_time: str = ""
    connection_established_time: str = ""
    connection_id: str = ""
    egress_bytes: str = ""
    egress_packets: str = ""
    ingress_bytes: str = ""
    ingress_packets: str = ""
    posture_compliance_status_set: List[Any] = field(default_factory=list)
    status: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    username: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
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
            "postureComplianceStatusSet": self.posture_compliance_status_set,
            "status": self.status,
            "timestamp": self.timestamp,
            "username": self.username,
        }

class ClientConnection_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.client_connections  # alias to shared store


    def _get_client_vpn_endpoint(self, client_vpn_endpoint_id: str):
        endpoint = self.state.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )
        return endpoint


    def DescribeClientVpnConnections(self, params: Dict[str, Any]):
        """Describes active client connections and connections that have been terminated within the last 60 
			minutes for the specified Client VPN endpoint."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        filters = params.get("Filter.N") or []
        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")

        now = datetime.now(timezone.utc)
        connections = []
        for connection in self.resources.values():
            if connection.client_vpn_endpoint_id != client_vpn_endpoint_id:
                continue
            if connection.connection_end_time:
                try:
                    end_time = datetime.fromisoformat(connection.connection_end_time)
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=timezone.utc)
                    if now - end_time > timedelta(minutes=60):
                        continue
                except ValueError:
                    pass
            connections.append(connection)

        if filters:
            connections = apply_filters(connections, filters)

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except ValueError:
                start_index = 0
        paginated = connections[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(connections):
            new_next_token = str(start_index + max_results)

        return {
            'connections': [conn.to_dict() for conn in paginated],
            'nextToken': new_next_token,
            }

    def TerminateClientVpnConnections(self, params: Dict[str, Any]):
        """Terminates active Client VPN endpoint connections. This action can be used to terminate a specific client connection, or up to five connections established by a specific user."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        connection_id = params.get("ConnectionId")
        username = params.get("Username")
        if not connection_id and not username:
            return create_error_response(
                "MissingParameter",
                "ConnectionId or Username is required.",
            )

        matching_connections = []
        for connection in self.resources.values():
            if connection.client_vpn_endpoint_id != client_vpn_endpoint_id:
                continue
            if connection_id and connection.connection_id != connection_id:
                continue
            if username and connection.username != username:
                continue
            matching_connections.append(connection)

        if connection_id and not matching_connections:
            return create_error_response(
                "InvalidClientVpnConnectionId.NotFound",
                f"The connection ID '{connection_id}' does not exist",
            )

        if username and not connection_id:
            matching_connections = matching_connections[:5]

        connection_statuses = []
        now = datetime.now(timezone.utc).isoformat()
        for connection in matching_connections:
            previous_status = dict(connection.status) if connection.status else {}
            connection.status = {"code": "terminated", "message": "terminated"}
            connection.connection_end_time = now
            connection.timestamp = now
            connection_statuses.append({
                "connectionId": connection.connection_id,
                "currentStatus": connection.status,
                "previousStatus": previous_status,
            })

        return {
            'clientVpnEndpointId': client_vpn_endpoint_id,
            'connectionStatuses': connection_statuses,
            'username': username,
            }

    def _generate_id(self, prefix: str = 'client') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class clientconnection_RequestParser:
    @staticmethod
    def parse_describe_client_vpn_connections_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_terminate_client_vpn_connections_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "ConnectionId": get_scalar(md, "ConnectionId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Username": get_scalar(md, "Username"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeClientVpnConnections": clientconnection_RequestParser.parse_describe_client_vpn_connections_request,
            "TerminateClientVpnConnections": clientconnection_RequestParser.parse_terminate_client_vpn_connections_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class clientconnection_ResponseSerializer:
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
                xml_parts.extend(clientconnection_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(clientconnection_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(clientconnection_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(clientconnection_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(clientconnection_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(clientconnection_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_client_vpn_connections_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeClientVpnConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize connections
        _connections_key = None
        if "connections" in data:
            _connections_key = "connections"
        elif "Connections" in data:
            _connections_key = "Connections"
        if _connections_key:
            param_data = data[_connections_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<connectionsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(clientconnection_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</connectionsSet>')
            else:
                xml_parts.append(f'{indent_str}<connectionsSet/>')
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
        xml_parts.append(f'</DescribeClientVpnConnectionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_terminate_client_vpn_connections_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<TerminateClientVpnConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientVpnEndpointId
        _clientVpnEndpointId_key = None
        if "clientVpnEndpointId" in data:
            _clientVpnEndpointId_key = "clientVpnEndpointId"
        elif "ClientVpnEndpointId" in data:
            _clientVpnEndpointId_key = "ClientVpnEndpointId"
        if _clientVpnEndpointId_key:
            param_data = data[_clientVpnEndpointId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientVpnEndpointId>{esc(str(param_data))}</clientVpnEndpointId>')
        # Serialize connectionStatuses
        _connectionStatuses_key = None
        if "connectionStatuses" in data:
            _connectionStatuses_key = "connectionStatuses"
        elif "ConnectionStatuses" in data:
            _connectionStatuses_key = "ConnectionStatuses"
        if _connectionStatuses_key:
            param_data = data[_connectionStatuses_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<connectionStatusesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(clientconnection_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</connectionStatusesSet>')
            else:
                xml_parts.append(f'{indent_str}<connectionStatusesSet/>')
        # Serialize username
        _username_key = None
        if "username" in data:
            _username_key = "username"
        elif "Username" in data:
            _username_key = "Username"
        if _username_key:
            param_data = data[_username_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<username>{esc(str(param_data))}</username>')
        xml_parts.append(f'</TerminateClientVpnConnectionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeClientVpnConnections": clientconnection_ResponseSerializer.serialize_describe_client_vpn_connections_response,
            "TerminateClientVpnConnections": clientconnection_ResponseSerializer.serialize_terminate_client_vpn_connections_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

