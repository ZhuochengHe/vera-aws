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
class ClientVpnEndpoint:
    associated_target_network: List[Any] = field(default_factory=list)
    authentication_options: List[Any] = field(default_factory=list)
    client_cidr_block: str = ""
    client_connect_options: Dict[str, Any] = field(default_factory=dict)
    client_login_banner_options: Dict[str, Any] = field(default_factory=dict)
    client_route_enforcement_options: Dict[str, Any] = field(default_factory=dict)
    client_vpn_endpoint_id: str = ""
    connection_log_options: Dict[str, Any] = field(default_factory=dict)
    creation_time: str = ""
    deletion_time: str = ""
    description: str = ""
    disconnect_on_session_timeout: bool = False
    dns_name: str = ""
    dns_server: List[Any] = field(default_factory=list)
    endpoint_ip_address_type: str = ""
    security_group_id_set: List[Any] = field(default_factory=list)
    self_service_portal_url: str = ""
    server_certificate_arn: str = ""
    session_timeout_hours: int = 0
    split_tunnel: bool = False
    status: Dict[str, Any] = field(default_factory=dict)
    tag_set: List[Any] = field(default_factory=list)
    traffic_ip_address_type: str = ""
    transport_protocol: str = ""
    vpc_id: str = ""
    vpn_port: int = 0
    vpn_protocol: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "associatedTargetNetwork": self.associated_target_network,
            "authenticationOptions": self.authentication_options,
            "clientCidrBlock": self.client_cidr_block,
            "clientConnectOptions": self.client_connect_options,
            "clientLoginBannerOptions": self.client_login_banner_options,
            "clientRouteEnforcementOptions": self.client_route_enforcement_options,
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "connectionLogOptions": self.connection_log_options,
            "creationTime": self.creation_time,
            "deletionTime": self.deletion_time,
            "description": self.description,
            "disconnectOnSessionTimeout": self.disconnect_on_session_timeout,
            "dnsName": self.dns_name,
            "dnsServer": self.dns_server,
            "endpointIpAddressType": self.endpoint_ip_address_type,
            "securityGroupIdSet": self.security_group_id_set,
            "selfServicePortalUrl": self.self_service_portal_url,
            "serverCertificateArn": self.server_certificate_arn,
            "sessionTimeoutHours": self.session_timeout_hours,
            "splitTunnel": self.split_tunnel,
            "status": self.status,
            "tagSet": self.tag_set,
            "trafficIpAddressType": self.traffic_ip_address_type,
            "transportProtocol": self.transport_protocol,
            "vpcId": self.vpc_id,
            "vpnPort": self.vpn_port,
            "vpnProtocol": self.vpn_protocol,
        }

class ClientVpnEndpoint_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.client_vpn_endpoints  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.vpcs.get(params['vpc_id']).client_vpn_endpoint_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).client_vpn_endpoint_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            value = params.get(name)
            if value is None or value == "" or value == [] or value == {}:
                return create_error_response("MissingParameter", f"Missing required parameter '{name}'.")
        return None

    def _get_resource_or_error(
        self,
        resource_id: str,
        code: str = "InvalidClientVpnEndpointId.NotFound",
    ) -> (Optional[ClientVpnEndpoint], Optional[Dict[str, Any]]):
        resource = self.resources.get(resource_id)
        if not resource:
            return None, create_error_response(code, f"The ID '{resource_id}' does not exist")
        return resource, None

    def _update_vpc_reference(self, resource: ClientVpnEndpoint, register: bool) -> None:
        if not resource.vpc_id:
            return
        vpc = self.state.vpcs.get(resource.vpc_id)
        if not vpc or not hasattr(vpc, "client_vpn_endpoint_ids"):
            return
        if register:
            if resource.client_vpn_endpoint_id not in vpc.client_vpn_endpoint_ids:
                vpc.client_vpn_endpoint_ids.append(resource.client_vpn_endpoint_id)
        else:
            if resource.client_vpn_endpoint_id in vpc.client_vpn_endpoint_ids:
                vpc.client_vpn_endpoint_ids.remove(resource.client_vpn_endpoint_id)

    def CreateClientVpnEndpoint(self, params: Dict[str, Any]):
        """Creates a Client VPN endpoint. A Client VPN endpoint is the resource you create and configure to 
			enable and manage client VPN sessions. It is the destination endpoint at which all client VPN sessions 
			are terminated."""

        error = self._require_params(
            params,
            ["Authentication.N", "ConnectionLogOptions", "ServerCertificateArn"],
        )
        if error:
            return error

        vpc_id = params.get("VpcId")
        if vpc_id and not self.state.vpcs.get(vpc_id):
            return create_error_response(
                "InvalidVpcID.NotFound",
                f"VPC '{vpc_id}' does not exist.",
            )

        security_group_ids = params.get("SecurityGroupId.N", []) or []
        for security_group_id in security_group_ids:
            if not self.state.security_groups.get(security_group_id):
                return create_error_response(
                    "InvalidGroup.NotFound",
                    f"Security group '{security_group_id}' does not exist.",
                )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        endpoint_id = self._generate_id("client")
        creation_time = datetime.now(timezone.utc).isoformat()
        dns_name = f"{endpoint_id}.cvpn.amazonaws.com"
        status = {"code": "available", "message": "Available"}

        resource = ClientVpnEndpoint(
            associated_target_network=[],
            authentication_options=params.get("Authentication.N", []) or [],
            client_cidr_block=params.get("ClientCidrBlock") or "",
            client_connect_options=params.get("ClientConnectOptions") or {},
            client_login_banner_options=params.get("ClientLoginBannerOptions") or {},
            client_route_enforcement_options=params.get("ClientRouteEnforcementOptions") or {},
            client_vpn_endpoint_id=endpoint_id,
            connection_log_options=params.get("ConnectionLogOptions") or {},
            creation_time=creation_time,
            deletion_time="",
            description=params.get("Description") or "",
            disconnect_on_session_timeout=str2bool(params.get("DisconnectOnSessionTimeout")),
            dns_name=dns_name,
            dns_server=params.get("DnsServers.N", []) or [],
            endpoint_ip_address_type=params.get("EndpointIpAddressType") or "",
            security_group_id_set=security_group_ids,
            self_service_portal_url=params.get("SelfServicePortal") or "",
            server_certificate_arn=params.get("ServerCertificateArn") or "",
            session_timeout_hours=int(params.get("SessionTimeoutHours") or 0),
            split_tunnel=str2bool(params.get("SplitTunnel")),
            status=status,
            tag_set=tag_set,
            traffic_ip_address_type=params.get("TrafficIpAddressType") or "",
            transport_protocol=params.get("TransportProtocol") or "",
            vpc_id=vpc_id or "",
            vpn_port=int(params.get("VpnPort") or 0),
            vpn_protocol=params.get("TransportProtocol") or "",
        )

        self.resources[endpoint_id] = resource
        self._update_vpc_reference(resource, True)

        return {
            'clientVpnEndpointId': endpoint_id,
            'dnsName': dns_name,
            'status': [status],
            }

    def DeleteClientVpnEndpoint(self, params: Dict[str, Any]):
        """Deletes the specified Client VPN endpoint. You must disassociate all target networks before you 
			can delete a Client VPN endpoint."""

        error = self._require_params(params, ["ClientVpnEndpointId"])
        if error:
            return error

        endpoint_id = params.get("ClientVpnEndpointId")
        resource, error = self._get_resource_or_error(endpoint_id)
        if error:
            return error

        if resource.associated_target_network:
            return create_error_response(
                "DependencyViolation",
                "Cannot delete Client VPN endpoint with associated target networks.",
            )

        self._update_vpc_reference(resource, False)
        resource.deletion_time = datetime.now(timezone.utc).isoformat()
        self.resources.pop(endpoint_id, None)

        status = {"code": "deleted", "message": "Deleted"}
        return {
            'status': [status],
            }

    def DescribeClientVpnEndpoints(self, params: Dict[str, Any]):
        """Describes one or more Client VPN endpoints in the account."""

        endpoint_ids = params.get("ClientVpnEndpointId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if endpoint_ids:
            resources: List[ClientVpnEndpoint] = []
            for endpoint_id in endpoint_ids:
                resource, error = self._get_resource_or_error(endpoint_id)
                if error:
                    return error
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        endpoints = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'clientVpnEndpoint': endpoints,
            'nextToken': None,
            }

    def ModifyClientVpnEndpoint(self, params: Dict[str, Any]):
        """Modifies the specified Client VPN endpoint. Modifying the DNS server resets existing client connections."""

        error = self._require_params(params, ["ClientVpnEndpointId"])
        if error:
            return error

        endpoint_id = params.get("ClientVpnEndpointId")
        resource, error = self._get_resource_or_error(endpoint_id)
        if error:
            return error

        vpc_id = params.get("VpcId")
        if vpc_id is not None and vpc_id != "" and not self.state.vpcs.get(vpc_id):
            return create_error_response(
                "InvalidVpcID.NotFound",
                f"VPC '{vpc_id}' does not exist.",
            )

        security_group_ids = params.get("SecurityGroupId.N", []) or []
        if security_group_ids:
            for security_group_id in security_group_ids:
                if not self.state.security_groups.get(security_group_id):
                    return create_error_response(
                        "InvalidGroup.NotFound",
                        f"Security group '{security_group_id}' does not exist.",
                    )

        if params.get("ClientConnectOptions") is not None:
            resource.client_connect_options = params.get("ClientConnectOptions") or {}
        if params.get("ClientLoginBannerOptions") is not None:
            resource.client_login_banner_options = params.get("ClientLoginBannerOptions") or {}
        if params.get("ClientRouteEnforcementOptions") is not None:
            resource.client_route_enforcement_options = params.get("ClientRouteEnforcementOptions") or {}
        if params.get("ConnectionLogOptions") is not None:
            resource.connection_log_options = params.get("ConnectionLogOptions") or {}
        if params.get("Description") is not None:
            resource.description = params.get("Description") or ""
        if params.get("DisconnectOnSessionTimeout") is not None:
            resource.disconnect_on_session_timeout = str2bool(
                params.get("DisconnectOnSessionTimeout")
            )
        if params.get("DnsServers") is not None:
            dns_value = params.get("DnsServers")
            if isinstance(dns_value, list):
                resource.dns_server = dns_value
            elif dns_value:
                resource.dns_server = [dns_value]
            else:
                resource.dns_server = []
        if security_group_ids:
            resource.security_group_id_set = security_group_ids
        if params.get("SelfServicePortal") is not None:
            resource.self_service_portal_url = params.get("SelfServicePortal") or ""
        if params.get("ServerCertificateArn") is not None:
            resource.server_certificate_arn = params.get("ServerCertificateArn") or ""
        if params.get("SessionTimeoutHours") is not None:
            resource.session_timeout_hours = int(params.get("SessionTimeoutHours") or 0)
        if params.get("SplitTunnel") is not None:
            resource.split_tunnel = str2bool(params.get("SplitTunnel"))
        if params.get("VpnPort") is not None:
            resource.vpn_port = int(params.get("VpnPort") or 0)

        if vpc_id is not None and vpc_id != resource.vpc_id:
            self._update_vpc_reference(resource, False)
            resource.vpc_id = vpc_id or ""
            self._update_vpc_reference(resource, True)

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'client') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class clientvpnendpoint_RequestParser:
    @staticmethod
    def parse_create_client_vpn_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Authentication.N": get_indexed_list(md, "Authentication"),
            "ClientCidrBlock": get_scalar(md, "ClientCidrBlock"),
            "ClientConnectOptions": get_scalar(md, "ClientConnectOptions"),
            "ClientLoginBannerOptions": get_scalar(md, "ClientLoginBannerOptions"),
            "ClientRouteEnforcementOptions": get_scalar(md, "ClientRouteEnforcementOptions"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "ConnectionLogOptions": get_scalar(md, "ConnectionLogOptions"),
            "Description": get_scalar(md, "Description"),
            "DisconnectOnSessionTimeout": get_scalar(md, "DisconnectOnSessionTimeout"),
            "DnsServers.N": get_indexed_list(md, "DnsServers"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndpointIpAddressType": get_scalar(md, "EndpointIpAddressType"),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
            "SelfServicePortal": get_scalar(md, "SelfServicePortal"),
            "ServerCertificateArn": get_scalar(md, "ServerCertificateArn"),
            "SessionTimeoutHours": get_int(md, "SessionTimeoutHours"),
            "SplitTunnel": get_scalar(md, "SplitTunnel"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TrafficIpAddressType": get_scalar(md, "TrafficIpAddressType"),
            "TransportProtocol": get_scalar(md, "TransportProtocol"),
            "VpcId": get_scalar(md, "VpcId"),
            "VpnPort": get_int(md, "VpnPort"),
        }

    @staticmethod
    def parse_delete_client_vpn_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_client_vpn_endpoints_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId.N": get_indexed_list(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_modify_client_vpn_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientConnectOptions": get_scalar(md, "ClientConnectOptions"),
            "ClientLoginBannerOptions": get_scalar(md, "ClientLoginBannerOptions"),
            "ClientRouteEnforcementOptions": get_scalar(md, "ClientRouteEnforcementOptions"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "ConnectionLogOptions": get_scalar(md, "ConnectionLogOptions"),
            "Description": get_scalar(md, "Description"),
            "DisconnectOnSessionTimeout": get_scalar(md, "DisconnectOnSessionTimeout"),
            "DnsServers": get_scalar(md, "DnsServers"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
            "SelfServicePortal": get_scalar(md, "SelfServicePortal"),
            "ServerCertificateArn": get_scalar(md, "ServerCertificateArn"),
            "SessionTimeoutHours": get_int(md, "SessionTimeoutHours"),
            "SplitTunnel": get_scalar(md, "SplitTunnel"),
            "VpcId": get_scalar(md, "VpcId"),
            "VpnPort": get_int(md, "VpnPort"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateClientVpnEndpoint": clientvpnendpoint_RequestParser.parse_create_client_vpn_endpoint_request,
            "DeleteClientVpnEndpoint": clientvpnendpoint_RequestParser.parse_delete_client_vpn_endpoint_request,
            "DescribeClientVpnEndpoints": clientvpnendpoint_RequestParser.parse_describe_client_vpn_endpoints_request,
            "ModifyClientVpnEndpoint": clientvpnendpoint_RequestParser.parse_modify_client_vpn_endpoint_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class clientvpnendpoint_ResponseSerializer:
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
                xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_client_vpn_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateClientVpnEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize dnsName
        _dnsName_key = None
        if "dnsName" in data:
            _dnsName_key = "dnsName"
        elif "DnsName" in data:
            _dnsName_key = "DnsName"
        if _dnsName_key:
            param_data = data[_dnsName_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<dnsName>{esc(str(param_data))}</dnsName>')
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
                    xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</CreateClientVpnEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_client_vpn_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteClientVpnEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</DeleteClientVpnEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_client_vpn_endpoints_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeClientVpnEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientVpnEndpoint
        _clientVpnEndpoint_key = None
        if "clientVpnEndpoint" in data:
            _clientVpnEndpoint_key = "clientVpnEndpoint"
        elif "ClientVpnEndpoint" in data:
            _clientVpnEndpoint_key = "ClientVpnEndpoint"
        if _clientVpnEndpoint_key:
            param_data = data[_clientVpnEndpoint_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<clientVpnEndpointSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(clientvpnendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</clientVpnEndpointSet>')
            else:
                xml_parts.append(f'{indent_str}<clientVpnEndpointSet/>')
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
        xml_parts.append(f'</DescribeClientVpnEndpointsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_client_vpn_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyClientVpnEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyClientVpnEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateClientVpnEndpoint": clientvpnendpoint_ResponseSerializer.serialize_create_client_vpn_endpoint_response,
            "DeleteClientVpnEndpoint": clientvpnendpoint_ResponseSerializer.serialize_delete_client_vpn_endpoint_response,
            "DescribeClientVpnEndpoints": clientvpnendpoint_ResponseSerializer.serialize_describe_client_vpn_endpoints_response,
            "ModifyClientVpnEndpoint": clientvpnendpoint_ResponseSerializer.serialize_modify_client_vpn_endpoint_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

