from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


# Enums for Client VPN Endpoint States
class ClientVpnEndpointState(Enum):
    PENDING_ASSOCIATE = "pending-associate"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


# Enums for Authentication Types
class AuthenticationType(Enum):
    CERTIFICATE_AUTHENTICATION = "certificate-authentication"
    DIRECTORY_SERVICE_AUTHENTICATION = "directory-service-authentication"
    FEDERATED_AUTHENTICATION = "federated-authentication"


# Enums for IP Address Types
class IpAddressType(Enum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    DUAL_STACK = "dual-stack"


# Enums for Transport Protocol
class TransportProtocol(Enum):
    TCP = "tcp"
    UDP = "udp"


# Enums for SelfServicePortal
class SelfServicePortal(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


# Enums for ClientVpnEndpointAttributeStatus code
class AttributeStatusCode(Enum):
    APPLYING = "applying"
    APPLIED = "applied"


@dataclass
class DirectoryServiceAuthentication:
    directory_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "directoryId": self.directory_id
        }


@dataclass
class FederatedAuthentication:
    saml_provider_arn: Optional[str] = None
    self_service_saml_provider_arn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "samlProviderArn": self.saml_provider_arn,
            "selfServiceSamlProviderArn": self.self_service_saml_provider_arn,
        }


@dataclass
class CertificateAuthentication:
    client_root_certificate_chain: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clientRootCertificateChain": self.client_root_certificate_chain
        }


@dataclass
class ClientVpnAuthentication:
    active_directory: Optional[DirectoryServiceAuthentication] = None
    federated_authentication: Optional[FederatedAuthentication] = None
    mutual_authentication: Optional[CertificateAuthentication] = None
    type: Optional[AuthenticationType] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.active_directory:
            d["activeDirectory"] = self.active_directory.to_dict()
        if self.federated_authentication:
            d["federatedAuthentication"] = self.federated_authentication.to_dict()
        if self.mutual_authentication:
            d["mutualAuthentication"] = self.mutual_authentication.to_dict()
        if self.type:
            d["type"] = self.type.value
        return d


@dataclass
class ClientConnectOptions:
    enabled: Optional[bool] = False
    lambda_function_arn: Optional[str] = None
    status_code: Optional[AttributeStatusCode] = None
    status_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "enabled": self.enabled,
            "lambdaFunctionArn": self.lambda_function_arn,
        }
        if self.status_code:
            d["status"] = {
                "code": self.status_code.value,
                "message": self.status_message,
            }
        return d


@dataclass
class ClientLoginBannerOptions:
    banner_text: Optional[str] = None
    enabled: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bannerText": self.banner_text,
            "enabled": self.enabled,
        }


@dataclass
class ClientRouteEnforcementOptions:
    enforced: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enforced": self.enforced,
        }


@dataclass
class ConnectionLogOptions:
    cloudwatch_log_group: Optional[str] = None
    cloudwatch_log_stream: Optional[str] = None
    enabled: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CloudwatchLogGroup": self.cloudwatch_log_group,
            "CloudwatchLogStream": self.cloudwatch_log_stream,
            "Enabled": self.enabled,
        }


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class TagSpecification:
    resource_type: str
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class ClientVpnEndpoint:
    client_vpn_endpoint_id: str
    authentication_options: List[ClientVpnAuthentication]
    client_cidr_block: Optional[str]
    client_connect_options: Optional[ClientConnectOptions]
    client_login_banner_options: Optional[ClientLoginBannerOptions]
    client_route_enforcement_options: Optional[ClientRouteEnforcementOptions]
    connection_log_options: ConnectionLogOptions
    description: Optional[str]
    disconnect_on_session_timeout: Optional[bool]
    dns_servers: List[str]
    endpoint_ip_address_type: IpAddressType
    security_group_ids: List[str]
    self_service_portal: Optional[SelfServicePortal]
    server_certificate_arn: str
    session_timeout_hours: int
    split_tunnel: Optional[bool]
    status: ClientVpnEndpointState
    tags: List[Tag]
    traffic_ip_address_type: IpAddressType
    transport_protocol: TransportProtocol
    vpc_id: Optional[str]
    vpn_port: int
    creation_time: str
    deletion_time: Optional[str] = None
    dns_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "authenticationOptions": [auth.to_dict() for auth in self.authentication_options],
            "clientCidrBlock": self.client_cidr_block,
            "clientConnectOptions": self.client_connect_options.to_dict() if self.client_connect_options else None,
            "clientLoginBannerOptions": self.client_login_banner_options.to_dict() if self.client_login_banner_options else None,
            "clientRouteEnforcementOptions": self.client_route_enforcement_options.to_dict() if self.client_route_enforcement_options else None,
            "connectionLogOptions": self.connection_log_options.to_dict(),
            "description": self.description,
            "disconnectOnSessionTimeout": self.disconnect_on_session_timeout,
            "dnsServer": self.dns_servers,
            "endpointIpAddressType": self.endpoint_ip_address_type.value,
            "securityGroupIdSet": self.security_group_ids,
            "selfServicePortalUrl": self._self_service_portal_url(),
            "serverCertificateArn": self.server_certificate_arn,
            "sessionTimeoutHours": self.session_timeout_hours,
            "splitTunnel": self.split_tunnel,
            "status": {
                "code": self.status.value,
                "message": None,
            },
            "tagSet": [tag.to_dict() for tag in self.tags],
            "trafficIpAddressType": self.traffic_ip_address_type.value,
            "transportProtocol": self.transport_protocol.value,
            "vpcId": self.vpc_id,
            "vpnPort": self.vpn_port,
            "creationTime": self.creation_time,
            "deletionTime": self.deletion_time,
            "dnsName": self.dns_name,
            "vpnProtocol": "openvpn",
        }

    def _self_service_portal_url(self) -> Optional[str]:
        if self.self_service_portal == SelfServicePortal.ENABLED:
            # Construct a fake URL for self-service portal
            return f"https://selfservice.clientvpn.{self.client_vpn_endpoint_id}.amazonaws.com"
        return None


class ClientVpnEndpointBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.client_vpn_endpoints dict for storage

    def _validate_authentication_options(self, auth_options: List[Dict[str, Any]]) -> List[ClientVpnAuthentication]:
        if not auth_options or not isinstance(auth_options, list):
            raise ErrorCode("InvalidParameterValue", "Authentication must be a non-empty list")

        result = []
        for auth in auth_options:
            if not isinstance(auth, dict):
                raise ErrorCode("InvalidParameterValue", "Each Authentication option must be a dict")

            # Validate Type
            auth_type_str = auth.get("Type")
            if not auth_type_str:
                raise ErrorCode("MissingParameter", "Authentication Type is required")
            try:
                auth_type = AuthenticationType(auth_type_str)
            except ValueError:
                raise ErrorCode("InvalidParameterValue", f"Invalid Authentication Type: {auth_type_str}")

            active_directory = None
            federated_authentication = None
            mutual_authentication = None

            if auth_type == AuthenticationType.DIRECTORY_SERVICE_AUTHENTICATION:
                ad = auth.get("ActiveDirectory")
                if ad is None or not isinstance(ad, dict):
                    raise ErrorCode("MissingParameter", "ActiveDirectory must be provided for directory-service-authentication")
                directory_id = ad.get("DirectoryId")
                # DirectoryId is optional, but if provided must be string
                if directory_id is not None and not isinstance(directory_id, str):
                    raise ErrorCode("InvalidParameterValue", "DirectoryId must be a string")
                active_directory = DirectoryServiceAuthentication(directory_id=directory_id)

            elif auth_type == AuthenticationType.FEDERATED_AUTHENTICATION:
                fed = auth.get("FederatedAuthentication")
                if fed is None or not isinstance(fed, dict):
                    raise ErrorCode("MissingParameter", "FederatedAuthentication must be provided for federated-authentication")
                saml_arn = fed.get("SAMLProviderArn")
                self_service_arn = fed.get("SelfServiceSAMLProviderArn")
                if saml_arn is not None and not isinstance(saml_arn, str):
                    raise ErrorCode("InvalidParameterValue", "SAMLProviderArn must be a string")
                if self_service_arn is not None and not isinstance(self_service_arn, str):
                    raise ErrorCode("InvalidParameterValue", "SelfServiceSAMLProviderArn must be a string")
                federated_authentication = FederatedAuthentication(
                    saml_provider_arn=saml_arn,
                    self_service_saml_provider_arn=self_service_arn,
                )

            elif auth_type == AuthenticationType.CERTIFICATE_AUTHENTICATION:
                mutual = auth.get("MutualAuthentication")
                if mutual is None or not isinstance(mutual, dict):
                    raise ErrorCode("MissingParameter", "MutualAuthentication must be provided for certificate-authentication")
                client_cert_arn = mutual.get("ClientRootCertificateChainArn")
                if client_cert_arn is not None and not isinstance(client_cert_arn, str):
                    raise ErrorCode("InvalidParameterValue", "ClientRootCertificateChainArn must be a string")
                mutual_authentication = CertificateAuthentication(client_root_certificate_chain=client_cert_arn)

            else:
                # Should not happen due to enum validation
                raise ErrorCode("InvalidParameterValue", f"Unsupported Authentication Type: {auth_type_str}")

            result.append(ClientVpnAuthentication(
                active_directory=active_directory,
                federated_authentication=federated_authentication,
                mutual_authentication=mutual_authentication,
                type=auth_type,
            ))
        return result

    def _validate_client_cidr_block(self, cidr: Optional[str]) -> Optional[str]:
        if cidr is None:
            return None
        if not isinstance(cidr, str):
            raise ErrorCode("InvalidParameterValue", "ClientCidrBlock must be a string")
        # Basic CIDR validation: must be IPv4 CIDR with mask between /12 and /22 inclusive
        import ipaddress
        try:
            net = ipaddress.IPv4Network(cidr, strict=True)
        except Exception:
            raise ErrorCode("InvalidParameterValue", "ClientCidrBlock must be a valid IPv4 CIDR block")
        prefix_len = net.prefixlen
        if prefix_len < 12 or prefix_len > 22:
            raise ErrorCode("InvalidParameterValue", "ClientCidrBlock prefix length must be between /12 and /22")
        return cidr

    def _validate_client_connect_options(self, options: Optional[Dict[str, Any]]) -> Optional[ClientConnectOptions]:
        if options is None:
            return None
        if not isinstance(options, dict):
            raise ErrorCode("InvalidParameterValue", "ClientConnectOptions must be a dict")
        enabled = options.get("Enabled", False)
        if not isinstance(enabled, bool):
            raise ErrorCode("InvalidParameterValue", "ClientConnectOptions.Enabled must be a boolean")
        lambda_arn = options.get("LambdaFunctionArn")
        if lambda_arn is not None and not isinstance(lambda_arn, str):
            raise ErrorCode("InvalidParameterValue", "ClientConnectOptions.LambdaFunctionArn must be a string")
        return ClientConnectOptions(enabled=enabled, lambda_function_arn=lambda_arn)

    def _validate_client_login_banner_options(self, options: Optional[Dict[str, Any]]) -> Optional[ClientLoginBannerOptions]:
        if options is None:
            return None
        if not isinstance(options, dict):
            raise ErrorCode("InvalidParameterValue", "ClientLoginBannerOptions must be a dict")
        banner_text = options.get("BannerText")
        if banner_text is not None:
            if not isinstance(banner_text, str):
                raise ErrorCode("InvalidParameterValue", "ClientLoginBannerOptions.BannerText must be a string")
            if len(banner_text.encode("utf-8")) > 1400:
                raise ErrorCode("InvalidParameterValue", "ClientLoginBannerOptions.BannerText must be at most 1400 UTF-8 bytes")
        enabled = options.get("Enabled", False)
        if not isinstance(enabled, bool):
            raise ErrorCode("InvalidParameterValue", "ClientLoginBannerOptions.Enabled must be a boolean")
        return ClientLoginBannerOptions(banner_text=banner_text, enabled=enabled)

    def _validate_client_route_enforcement_options(self, options: Optional[Dict[str, Any]]) -> Optional[ClientRouteEnforcementOptions]:
        if options is None:
            return None
        if not isinstance(options, dict):
            raise ErrorCode("InvalidParameterValue", "ClientRouteEnforcementOptions must be a dict")
        enforced = options.get("Enforced", False)
        if not isinstance(enforced, bool):
            raise ErrorCode("InvalidParameterValue", "ClientRouteEnforcementOptions.Enforced must be a boolean")
        return ClientRouteEnforcementOptions(enforced=enforced)

    def _validate_connection_log_options(self, options: Dict[str, Any]) -> ConnectionLogOptions:
        if not isinstance(options, dict):
            raise ErrorCode("InvalidParameterValue", "ConnectionLogOptions must be a dict")
        enabled = options.get("Enabled", False)
        if not isinstance(enabled, bool):
            raise ErrorCode("InvalidParameterValue", "ConnectionLogOptions.Enabled must be a boolean")
        cloudwatch_log_group = options.get("CloudwatchLogGroup")
        if cloudwatch_log_group is not None and not isinstance(cloudwatch_log_group, str):
            raise ErrorCode("InvalidParameterValue", "ConnectionLogOptions.CloudwatchLogGroup must be a string")
        cloudwatch_log_stream = options.get("CloudwatchLogStream")
        if cloudwatch_log_stream is not None and not isinstance(cloudwatch_log_stream, str):
            raise ErrorCode("InvalidParameterValue", "ConnectionLogOptions.CloudwatchLogStream must be a string")
        # If enabled is True, CloudwatchLogGroup must be provided
        if enabled and not cloudwatch_log_group:
            raise ErrorCode("InvalidParameterValue", "ConnectionLogOptions.CloudwatchLogGroup is required when Enabled is true")
        return ConnectionLogOptions(
            cloudwatch_log_group=cloudwatch_log_group,
            cloudwatch_log_stream=cloudwatch_log_stream,
            enabled=enabled,
        )

    def _validate_dns_servers(self, dns_servers: Optional[List[str]]) -> List[str]:
        if dns_servers is None:
            return []
        if not isinstance(dns_servers, list):
            raise ErrorCode("InvalidParameterValue", "DnsServers must be a list of strings")
        if len(dns_servers) > 2:
            raise ErrorCode("InvalidParameterValue", "A Client VPN endpoint can have up to two DNS servers")
        for dns in dns_servers:
            if not isinstance(dns, str):
                raise ErrorCode("InvalidParameterValue", "Each DNS server must be a string")
            # Could add IP validation here if desired
        return dns_servers

    def _validate_endpoint_ip_address_type(self, ip_type: Optional[str]) -> IpAddressType:
        if ip_type is None:
            return IpAddressType.IPV4
        try:
            return IpAddressType(ip_type)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid EndpointIpAddressType: {ip_type}")

    def _validate_traffic_ip_address_type(self, ip_type: Optional[str]) -> IpAddressType:
        if ip_type is None:
            return IpAddressType.IPV4
        try:
            return IpAddressType(ip_type)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid TrafficIpAddressType: {ip_type}")

    def _validate_transport_protocol(self, protocol: Optional[str]) -> TransportProtocol:
        if protocol is None:
            return TransportProtocol.UDP
        try:
            return TransportProtocol(protocol)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid TransportProtocol: {protocol}")

    def _validate_self_service_portal(self, portal: Optional[str]) -> Optional[SelfServicePortal]:
        if portal is None:
            return None
        try:
            return SelfServicePortal(portal)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid SelfServicePortal value: {portal}")

    def _validate_security_group_ids(self, sg_ids: Optional[List[str]]) -> List[str]:
        if sg_ids is None:
            return []
        if not isinstance(sg_ids, list):
            raise ErrorCode("InvalidParameterValue", "SecurityGroupId.N must be a list of strings")
        for sg in sg_ids:
            if not isinstance(sg, str):
                raise ErrorCode("InvalidParameterValue", "Each SecurityGroupId must be a string")
        return sg_ids

    def _validate_session_timeout_hours(self, hours: Optional[int]) -> int:
        if hours is None:
            return 24
        if not isinstance(hours, int):
            raise ErrorCode("InvalidParameterValue", "SessionTimeoutHours must be an integer")
        if hours not in (8, 10, 12, 24):
            raise ErrorCode("InvalidParameterValue", "SessionTimeoutHours must be one of 8, 10, 12, 24")
        return hours

    def _validate_vpn_port(self, port: Optional[int]) -> int:
        if port is None:
            return 443
        if not isinstance(port, int):
            raise ErrorCode("InvalidParameterValue", "VpnPort must be an integer")
        if port not in (443, 1194):
             raise ErrorCode("InvalidParameterValue", "VpnPort must be 443 or 1194")
        return port

    def create_client_vpn_endpoint(self, params): return {}
    def delete_client_vpn_endpoint(self, params): return {}
    def describe_client_vpn_endpoints(self, params): return {}
    def modify_client_vpn_endpoint(self, params): return {}

from emulator_core.gateway.base import BaseGateway

class ClientVPNendpointsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateClientVpnEndpoint", self.create_client_vpn_endpoint)
        self.register_action("DeleteClientVpnEndpoint", self.delete_client_vpn_endpoint)
        self.register_action("DescribeClientVpnEndpoints", self.describe_client_vpn_endpoints)
        self.register_action("ModifyClientVpnEndpoint", self.modify_client_vpn_endpoint)

    def create_client_vpn_endpoint(self, params):
        return self.backend.create_client_vpn_endpoint(params)

    def delete_client_vpn_endpoint(self, params):
        return self.backend.delete_client_vpn_endpoint(params)

    def describe_client_vpn_endpoints(self, params):
        return self.backend.describe_client_vpn_endpoints(params)

    def modify_client_vpn_endpoint(self, params):
        return self.backend.modify_client_vpn_endpoint(params)
