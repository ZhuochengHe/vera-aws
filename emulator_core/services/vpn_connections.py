from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class GatewayAssociationState(str, Enum):
    ASSOCIATED = "associated"
    NOT_ASSOCIATED = "not-associated"
    ASSOCIATING = "associating"
    DISASSOCIATING = "disassociating"


class VpnConnectionState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


class VpnTunnelStatus(str, Enum):
    UP = "UP"
    DOWN = "DOWN"


class TunnelDpdTimeoutAction(str, Enum):
    CLEAR = "clear"
    NONE = "none"
    RESTART = "restart"


class TunnelStartupAction(str, Enum):
    ADD = "add"
    START = "start"


class TunnelBandwidth(str, Enum):
    STANDARD = "standard"
    LARGE = "large"


class OutsideIpAddressType(str, Enum):
    PRIVATE_IPV4 = "PrivateIpv4"
    PUBLIC_IPV4 = "PublicIpv4"
    IPV6 = "Ipv6"


class IKEVersion(str, Enum):
    IKEV1 = "ikev1"
    IKEV2 = "ikev2"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: str
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class VpnStaticRoute:
    destination_cidr_block: str
    source: Optional[str] = None  # e.g. "Static"
    state: Optional[str] = None  # pending | available | deleting | deleted

    def to_dict(self) -> Dict[str, Any]:
        d = {"DestinationCidrBlock": self.destination_cidr_block}
        if self.source is not None:
            d["Source"] = self.source
        if self.state is not None:
            d["State"] = self.state
        return d


@dataclass
class CloudWatchLogOptionsSpecification:
    BgpLogEnabled: Optional[bool] = None
    BgpLogGroupArn: Optional[str] = None
    BgpLogOutputFormat: Optional[str] = None  # json|text
    LogEnabled: Optional[bool] = None
    LogGroupArn: Optional[str] = None
    LogOutputFormat: Optional[str] = None  # json|text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "BgpLogEnabled": self.BgpLogEnabled,
            "BgpLogGroupArn": self.BgpLogGroupArn,
            "BgpLogOutputFormat": self.BgpLogOutputFormat,
            "LogEnabled": self.LogEnabled,
            "LogGroupArn": self.LogGroupArn,
            "LogOutputFormat": self.LogOutputFormat,
        }


@dataclass
class VpnTunnelLogOptionsSpecification:
    CloudWatchLogOptions: Optional[CloudWatchLogOptionsSpecification] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CloudWatchLogOptions": self.CloudWatchLogOptions.to_dict()
            if self.CloudWatchLogOptions
            else None
        }


@dataclass
class IKEVersionsRequestListValue:
    Value: Optional[str] = None  # ikev1|ikev2

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class Phase1DHGroupNumbersRequestListValue:
    Value: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class Phase1EncryptionAlgorithmsRequestListValue:
    Value: Optional[str] = None  # AES128|AES256|AES128-GCM-16|AES256-GCM-16

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class Phase1IntegrityAlgorithmsRequestListValue:
    Value: Optional[str] = None  # SHA1|SHA2-256|SHA2-384|SHA2-512

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class Phase2DHGroupNumbersRequestListValue:
    Value: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class Phase2EncryptionAlgorithmsRequestListValue:
    Value: Optional[str] = None  # AES128|AES256|AES128-GCM-16|AES256-GCM-16

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class Phase2IntegrityAlgorithmsRequestListValue:
    Value: Optional[str] = None  # SHA1|SHA2-256|SHA2-384|SHA2-512

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class VpnTunnelOptionsSpecification:
    DPDTimeoutAction: Optional[str] = None  # clear|none|restart
    DPDTimeoutSeconds: Optional[int] = None
    EnableTunnelLifecycleControl: Optional[bool] = None
    IKEVersions: List[IKEVersionsRequestListValue] = field(default_factory=list)
    LogOptions: Optional[VpnTunnelLogOptionsSpecification] = None
    OutsideIpAddress: Optional[str] = None
    Phase1DHGroupNumbers: List[Phase1DHGroupNumbersRequestListValue] = field(default_factory=list)
    Phase1EncryptionAlgorithms: List[Phase1EncryptionAlgorithmsRequestListValue] = field(default_factory=list)
    Phase1IntegrityAlgorithms: List[Phase1IntegrityAlgorithmsRequestListValue] = field(default_factory=list)
    Phase1LifetimeSeconds: Optional[int] = None
    Phase2DHGroupNumbers: List[Phase2DHGroupNumbersRequestListValue] = field(default_factory=list)
    Phase2EncryptionAlgorithms: List[Phase2EncryptionAlgorithmsRequestListValue] = field(default_factory=list)
    Phase2IntegrityAlgorithms: List[Phase2IntegrityAlgorithmsRequestListValue] = field(default_factory=list)
    Phase2LifetimeSeconds: Optional[int] = None
    PreSharedKey: Optional[str] = None
    RekeyFuzzPercentage: Optional[int] = None
    RekeyMarginTimeSeconds: Optional[int] = None
    ReplayWindowSize: Optional[int] = None
    StartupAction: Optional[str] = None  # add|start
    TunnelInsideCidr: Optional[str] = None
    TunnelInsideIpv6Cidr: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DPDTimeoutAction": self.DPDTimeoutAction,
            "DPDTimeoutSeconds": self.DPDTimeoutSeconds,
            "EnableTunnelLifecycleControl": self.EnableTunnelLifecycleControl,
            "IKEVersions": [v.to_dict() for v in self.IKEVersions] if self.IKEVersions else [],
            "LogOptions": self.LogOptions.to_dict() if self.LogOptions else None,
            "OutsideIpAddress": self.OutsideIpAddress,
            "Phase1DHGroupNumbers": [v.to_dict() for v in self.Phase1DHGroupNumbers] if self.Phase1DHGroupNumbers else [],
            "Phase1EncryptionAlgorithms": [v.to_dict() for v in self.Phase1EncryptionAlgorithms] if self.Phase1EncryptionAlgorithms else [],
            "Phase1IntegrityAlgorithms": [v.to_dict() for v in self.Phase1IntegrityAlgorithms] if self.Phase1IntegrityAlgorithms else [],
            "Phase1LifetimeSeconds": self.Phase1LifetimeSeconds,
            "Phase2DHGroupNumbers": [v.to_dict() for v in self.Phase2DHGroupNumbers] if self.Phase2DHGroupNumbers else [],
            "Phase2EncryptionAlgorithms": [v.to_dict() for v in self.Phase2EncryptionAlgorithms] if self.Phase2EncryptionAlgorithms else [],
            "Phase2IntegrityAlgorithms": [v.to_dict() for v in self.Phase2IntegrityAlgorithms] if self.Phase2IntegrityAlgorithms else [],
            "Phase2LifetimeSeconds": self.Phase2LifetimeSeconds,
            "PreSharedKey": self.PreSharedKey,
            "RekeyFuzzPercentage": self.RekeyFuzzPercentage,
            "RekeyMarginTimeSeconds": self.RekeyMarginTimeSeconds,
            "ReplayWindowSize": self.ReplayWindowSize,
            "StartupAction": self.StartupAction,
            "TunnelInsideCidr": self.TunnelInsideCidr,
            "TunnelInsideIpv6Cidr": self.TunnelInsideIpv6Cidr,
        }


@dataclass
class VpnConnectionOptionsSpecification:
    EnableAcceleration: Optional[bool] = None
    LocalIpv4NetworkCidr: Optional[str] = None
    LocalIpv6NetworkCidr: Optional[str] = None
    OutsideIpAddressType: Optional[str] = None  # PrivateIpv4|PublicIpv4|Ipv6
    RemoteIpv4NetworkCidr: Optional[str] = None
    RemoteIpv6NetworkCidr: Optional[str] = None
    StaticRoutesOnly: Optional[bool] = None
    TransportTransitGatewayAttachmentId: Optional[str] = None
    TunnelBandwidth: Optional[str] = None  # standard | large
    TunnelInsideIpVersion: Optional[str] = None  # ipv4 | ipv6
    TunnelOptions: List[VpnTunnelOptionsSpecification] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EnableAcceleration": self.EnableAcceleration,
            "LocalIpv4NetworkCidr": self.LocalIpv4NetworkCidr,
            "LocalIpv6NetworkCidr": self.LocalIpv6NetworkCidr,
            "OutsideIpAddressType": self.OutsideIpAddressType,
            "RemoteIpv4NetworkCidr": self.RemoteIpv4NetworkCidr,
            "RemoteIpv6NetworkCidr": self.RemoteIpv6NetworkCidr,
            "StaticRoutesOnly": self.StaticRoutesOnly,
            "TransportTransitGatewayAttachmentId": self.TransportTransitGatewayAttachmentId,
            "TunnelBandwidth": self.TunnelBandwidth,
            "TunnelInsideIpVersion": self.TunnelInsideIpVersion,
            "TunnelOptions": [t.to_dict() for t in self.TunnelOptions],
        }


@dataclass
class VpnTunnelLogOptions:
    CloudWatchLogOptions: Optional[CloudWatchLogOptionsSpecification] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CloudWatchLogOptions": self.CloudWatchLogOptions.to_dict() if self.CloudWatchLogOptions else None
        }


@dataclass
class IKEVersionsListValue:
    value: Optional[str] = None  # ikev1|ikev2

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}


@dataclass
class Phase1DHGroupNumbersListValue:
    value: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}


@dataclass
class Phase1EncryptionAlgorithmsListValue:
    value: Optional[str] = None  # AES128|AES256|AES128-GCM-16|AES256-GCM-16

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}


@dataclass
class Phase1IntegrityAlgorithmsListValue:
    value: Optional[str] = None  # SHA1|SHA2-256|SHA2-384|SHA2-512

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}


@dataclass
class Phase2DHGroupNumbersListValue:
    value: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}


@dataclass
class Phase2EncryptionAlgorithmsListValue:
    value: Optional[str] = None  # AES128|AES256|AES128-GCM-16|AES256-GCM-16

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}


@dataclass
class Phase2IntegrityAlgorithmsListValue:
    value: Optional[str] = None  # SHA1|SHA2-256|SHA2-384|SHA2-512

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}


@dataclass
class TunnelOption:
    dpdTimeoutAction: Optional[str] = None  # clear|none|restart
    dpdTimeoutSeconds: Optional[int] = None
    enableTunnelLifecycleControl: Optional[bool] = None
    ikeVersionSet: List[IKEVersionsListValue] = field(default_factory=list)
    logOptions: Optional[VpnTunnelLogOptions] = None
    outsideIpAddress: Optional[str] = None
    phase1DHGroupNumberSet: List[Phase1DHGroupNumbersListValue] = field(default_factory=list)
    phase1EncryptionAlgorithmSet: List[Phase1EncryptionAlgorithmsListValue] = field(default_factory=list)
    phase1IntegrityAlgorithmSet: List[Phase1IntegrityAlgorithmsListValue] = field(default_factory=list)
    phase1LifetimeSeconds: Optional[int] = None
    phase2DHGroupNumberSet: List[Phase2DHGroupNumbersListValue] = field(default_factory=list)
    phase2EncryptionAlgorithmSet: List[Phase2EncryptionAlgorithmsListValue] = field(default_factory=list)
    phase2IntegrityAlgorithmSet: List[Phase2IntegrityAlgorithmsListValue] = field(default_factory=list)
    phase2LifetimeSeconds: Optional[int] = None
    preSharedKey: Optional[str] = None
    rekeyFuzzPercentage: Optional[int] = None
    rekeyMarginTimeSeconds: Optional[int] = None
    replayWindowSize: Optional[int] = None
    startupAction: Optional[str] = None  # add|start
    tunnelInsideCidr: Optional[str] = None
    tunnelInsideIpv6Cidr: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dpdTimeoutAction": self.dpdTimeoutAction,
            "dpdTimeoutSeconds": self.dpdTimeoutSeconds,
            "enableTunnelLifecycleControl": self.enableTunnelLifecycleControl,
            "ikeVersionSet": [v.to_dict() for v in self.ikeVersionSet] if self.ikeVersionSet else [],
            "logOptions": self.logOptions.to_dict() if self.logOptions else None,
            "outsideIpAddress": self.outsideIpAddress,
            "phase1DHGroupNumberSet": [v.to_dict() for v in self.phase1DHGroupNumberSet] if self.phase1DHGroupNumberSet else [],
            "phase1EncryptionAlgorithmSet": [v.to_dict() for v in self.phase1EncryptionAlgorithmSet] if self.phase1EncryptionAlgorithmSet else [],
            "phase1IntegrityAlgorithmSet": [v.to_dict() for v in self.phase1IntegrityAlgorithmSet] if self.phase1IntegrityAlgorithmSet else [],
            "phase1LifetimeSeconds": self.phase1LifetimeSeconds,
            "phase2DHGroupNumberSet": [v.to_dict() for v in self.phase2DHGroupNumberSet] if self.phase2DHGroupNumberSet else [],
            "phase2EncryptionAlgorithmSet": [v.to_dict() for v in self.phase2EncryptionAlgorithmSet] if self.phase2EncryptionAlgorithmSet else [],
            "phase2IntegrityAlgorithmSet": [v.to_dict() for v in self.phase2IntegrityAlgorithmSet] if self.phase2IntegrityAlgorithmSet else [],
            "phase2LifetimeSeconds": self.phase2LifetimeSeconds,
            "preSharedKey": self.preSharedKey,
            "rekeyFuzzPercentage": self.rekeyFuzzPercentage,
            "rekeyMarginTimeSeconds": self.rekeyMarginTimeSeconds,
            "replayWindowSize": self.replayWindowSize,
            "startupAction": self.startupAction,
            "tunnelInsideCidr": self.tunnelInsideCidr,
            "tunnelInsideIpv6Cidr": self.tunnelInsideIpv6Cidr,
        }


@dataclass
class VgwTelemetry:
    acceptedRouteCount: Optional[int] = None
    certificateArn: Optional[str] = None
    lastStatusChange: Optional[datetime] = None
    outsideIpAddress: Optional[str] = None
    status: Optional[str] = None  # UP | DOWN
    statusMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.acceptedRouteCount is not None:
            d["AcceptedRouteCount"] = self.acceptedRouteCount
        if self.certificateArn is not None:
            d["CertificateArn"] = self.certificateArn
        if self.lastStatusChange is not None:
            d["LastStatusChange"] = self.lastStatusChange.isoformat()
        if self.outsideIpAddress is not None:
            d["OutsideIpAddress"] = self.outsideIpAddress
        if self.status is not None:
            d["Status"] = self.status
        if self.statusMessage is not None:
            d["StatusMessage"] = self.statusMessage
        return d


@dataclass
class VpnConnection:
    vpn_connection_id: str
    state: Optional[str] = None  # pending | available | deleting | deleted
    customerGatewayConfiguration: Optional[str] = None
    customerGatewayId: Optional[str] = None
    vpnGatewayId: Optional[str] = None
    transitGatewayId: Optional[str] = None
    vpnConcentratorId: Optional[str] = None
    category: Optional[str] = None  # VPN | VPN-Classic
    coreNetworkArn: Optional[str] = None
    coreNetworkAttachmentArn: Optional[str] = None
    gatewayAssociationState: Optional[GatewayAssociationState] = None
    options: Optional[VpnConnectionOptionsSpecification] = None
    preSharedKeyArn: Optional[str] = None
    routes: List[VpnStaticRoute] = field(default_factory=list)
    tagSet: List[Tag] = field(default_factory=list)
    type: Optional[str] = None  # ipsec.1
    vgwTelemetry: List[VgwTelemetry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "VpnConnectionId": self.vpn_connection_id,
            "State": self.state,
            "CustomerGatewayConfiguration": self.customerGatewayConfiguration,
            "CustomerGatewayId": self.customerGatewayId,
            "VpnGatewayId": self.vpnGatewayId,
            "TransitGatewayId": self.transitGatewayId,
            "VpnConcentratorId": self.vpnConcentratorId,
            "Category": self.category,
            "CoreNetworkArn": self.coreNetworkArn,
            "CoreNetworkAttachmentArn": self.coreNetworkAttachmentArn,
            "GatewayAssociationState": self.gatewayAssociationState.value if self.gatewayAssociationState else None,
        }
        return d


class VpnConnectionsBackend(BaseBackend):
    def create_vpn_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        customer_gateway_id = params.get("CustomerGatewayId")
        vpn_type = params.get("Type")
        if not customer_gateway_id:
            raise Exception("Missing required parameter CustomerGatewayId")
        if not vpn_type:
            raise Exception("Missing required parameter Type")
        if vpn_type != "ipsec.1":
            raise Exception("Invalid Type parameter, only 'ipsec.1' is supported")

        # Validate mutually exclusive parameters: TransitGatewayId and VpnGatewayId
        transit_gateway_id = params.get("TransitGatewayId")
        vpn_gateway_id = params.get("VpnGatewayId")
        if transit_gateway_id and vpn_gateway_id:
            raise Exception("TransitGatewayId and VpnGatewayId cannot both be specified")

        # Validate existence of referenced resources
        customer_gateway = self.state.customer_gateways.get(customer_gateway_id)
        if not customer_gateway:
            raise Exception(f"CustomerGatewayId {customer_gateway_id} does not exist")

        if vpn_gateway_id:
            vpn_gateway = self.state.vpn_gateways.get(vpn_gateway_id)
            if not vpn_gateway:
                raise Exception(f"VpnGatewayId {vpn_gateway_id} does not exist")
        else:
            vpn_gateway = None

        if transit_gateway_id:
            transit_gateway = self.state.transit_gateways.get(transit_gateway_id)
            if not transit_gateway:
                raise Exception(f"TransitGatewayId {transit_gateway_id} does not exist")
        else:
            transit_gateway = None

        # DryRun check
        if params.get("DryRun"):
            # Here we assume permission check is always successful for emulator
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Generate VPN Connection ID
        vpn_connection_id = self.generate_unique_id("vpn")

        # Parse Options if present
        options_param = params.get("Options", {})
        # Options defaults
        enable_acceleration = options_param.get("EnableAcceleration", False)
        local_ipv4_network_cidr = options_param.get("LocalIpv4NetworkCidr", "0.0.0.0/0")
        local_ipv6_network_cidr = options_param.get("LocalIpv6NetworkCidr", "::/0")
        outside_ip_address_type = options_param.get("OutsideIpAddressType", "PublicIpv4")
        remote_ipv4_network_cidr = options_param.get("RemoteIpv4NetworkCidr", "0.0.0.0/0")
        remote_ipv6_network_cidr = options_param.get("RemoteIpv6NetworkCidr", "::/0")
        static_routes_only = options_param.get("StaticRoutesOnly", False)
        transport_tgw_attachment_id = options_param.get("TransportTransitGatewayAttachmentId")
        tunnel_bandwidth = options_param.get("TunnelBandwidth", "standard")
        tunnel_inside_ip_version = options_param.get("TunnelInsideIpVersion", "ipv4")
        tunnel_options_param = options_param.get("TunnelOptions", [])

        # Validate tunnel_bandwidth
        if tunnel_bandwidth not in ("standard", "large"):
            raise Exception("Invalid TunnelBandwidth value, must be 'standard' or 'large'")

        # Validate tunnel_inside_ip_version
        if tunnel_inside_ip_version not in ("ipv4", "ipv6"):
            raise Exception("Invalid TunnelInsideIpVersion value, must be 'ipv4' or 'ipv6'")

        # PreSharedKeyStorage param
        pre_shared_key_storage = params.get("PreSharedKeyStorage")

        # TagSpecification parsing
        tag_specifications = params.get("TagSpecification.N", [])
        tags: List[Dict[str, str]] = []
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            if resource_type and resource_type != "vpn-connection":
                # Only apply tags for vpn-connection resource type
                continue
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key and value:
                    tags.append({"Key": key, "Value": value})

        # VpnConcentratorId param
        vpn_concentrator_id = params.get("VpnConcentratorId")

        # Build customer gateway configuration XML (escaped)
        # This is a simplified placeholder XML configuration string
        # In real AWS, this is a complex XML with tunnel info, keys, etc.
        # We'll generate a minimal example with escaped XML
        customer_gateway_configuration = (
            f"<vpn_connection>"
            f"<vpn_connection_id>{vpn_connection_id}</vpn_connection_id>"
            f"<customer_gateway_id>{customer_gateway_id}</customer_gateway_id>"
            f"<vpn_gateway_id>{vpn_gateway_id if vpn_gateway_id else ''}</vpn_gateway_id>"
            f"<transit_gateway_id>{transit_gateway_id if transit_gateway_id else ''}</transit_gateway_id>"
            f"</vpn_connection>"
        )
        escaped_customer_gateway_configuration = saxutils.escape(customer_gateway_configuration)

        # Build tunnel options list for response
        tunnel_option_set = []
        # If no tunnel options specified, create two default empty tunnel options (AWS default)
        if not tunnel_options_param:
            tunnel_option_set = [{}, {}]
        else:
            # Map each tunnel option dict to response format
            for tunnel_opt in tunnel_options_param:
                # Map IKEVersions from list of dicts with "Value" key to list of dicts with "value" key
                ike_versions_in = tunnel_opt.get("IKEVersions", [])
                ike_version_set = []
                for ikev in ike_versions_in:
                    val = ikev.get("Value")
                    if val:
                        ike_version_set.append({"value": val})

                # Map Phase1DHGroupNumbers
                phase1_dh_in = tunnel_opt.get("Phase1DHGroupNumbers", [])
                phase1_dh_set = []
                for dh in phase1_dh_in:
                    v = dh.get("Value")
                    if v is not None:
                        phase1_dh_set.append({"value": v})

                # Map Phase1EncryptionAlgorithms
                phase1_enc_in = tunnel_opt.get("Phase1EncryptionAlgorithms", [])
                phase1_enc_set = []
                for enc in phase1_enc_in:
                    v = enc.get("Value")
                    if v:
                        phase1_enc_set.append({"value": v})

                # Map Phase1IntegrityAlgorithms
                phase1_int_in = tunnel_opt.get("Phase1IntegrityAlgorithms", [])
                phase1_int_set = []
                for intg in phase1_int_in:
                    v = intg.get("Value")
                    if v:
                        phase1_int_set.append({"value": v})

                # Map Phase2DHGroupNumbers
                phase2_dh_in = tunnel_opt.get("Phase2DHGroupNumbers", [])
                phase2_dh_set = []
                for dh in phase2_dh_in:
                    v = dh.get("Value")
                    if v is not None:
                        phase2_dh_set.append({"value": v})

                # Map Phase2EncryptionAlgorithms
                phase2_enc_in = tunnel_opt.get("Phase2EncryptionAlgorithms", [])
                phase2_enc_set = []
                for enc in phase2_enc_in:
                    v = enc.get("Value")
                    if v:
                        phase2_enc_set.append({"value": v})

                # Map Phase2IntegrityAlgorithms
                phase2_int_in = tunnel_opt.get("Phase2IntegrityAlgorithms", [])
                phase2_int_set = []
                for intg in phase2_int_in:
                    v = intg.get("Value")
                    if v:
                        phase2_int_set.append({"value": v})

                # Map LogOptions and CloudWatchLogOptions
                log_options_in = tunnel_opt.get("LogOptions", {})
                cloudwatch_log_options_in = log_options_in.get("CloudWatchLogOptions", {})
                cloudwatch_log_options = {
                    "bgpLogEnabled": cloudwatch_log_options_in.get("BgpLogEnabled", False),
                    "bgpLogGroupArn": cloudwatch_log_options_in.get("BgpLogGroupArn"),
                    "bgpLogOutputFormat": cloudwatch_log_options_in.get("BgpLogOutputFormat", "json"),
                    "logEnabled": cloudwatch_log_options_in.get("LogEnabled", False),
                    "logGroupArn": cloudwatch_log_options_in.get("LogGroupArn"),
                    "logOutputFormat": cloudwatch_log_options_in.get("LogOutputFormat", "json"),
                } if cloudwatch_log_options_in else None

                log_options = {
                    "cloudWatchLogOptions": cloudwatch_log_options
                } if cloudwatch_log_options else None

                tunnel_option = {
                    "dpdTimeoutAction": tunnel_opt.get("DPDTimeoutAction"),
                    "dpdTimeoutSeconds": tunnel_opt.get("DPDTimeoutSeconds"),
                    "enableTunnelLifecycleControl": tunnel_opt.get("EnableTunnelLifecycleControl"),
                    "ikeVersionSet": ike_version_set if ike_version_set else None,
                    "logOptions": log_options,
                    "outsideIpAddress": None,  # Not specified in create request
                    "phase1DHGroupNumberSet": phase1_dh_set if phase1_dh_set else None,
                    "phase1EncryptionAlgorithmSet": phase1_enc_set if phase1_enc_set else None,
                    "phase1IntegrityAlgorithmSet": phase1_int_set if phase1_int_set else None,
                    "phase1LifetimeSeconds": tunnel_opt.get("Phase1LifetimeSeconds"),
                    "phase2DHGroupNumberSet": phase2_dh_set if phase2_dh_set else None,
                    "phase2EncryptionAlgorithmSet": phase2_enc_set if phase2_enc_set else None,
                    "phase2IntegrityAlgorithmSet": phase2_int_set if phase2_int_set else None,
                    "phase2LifetimeSeconds": tunnel_opt.get("Phase2LifetimeSeconds"),
                    "preSharedKey": tunnel_opt.get("PreSharedKey"),
                    "rekeyFuzzPercentage": tunnel_opt.get("RekeyFuzzPercentage"),
                    "rekeyMarginTimeSeconds": tunnel_opt.get("RekeyMarginTimeSeconds"),
                    "replayWindowSize": tunnel_opt.get("ReplayWindowSize"),
                    "startupAction": tunnel_opt.get("StartupAction"),
                    "tunnelInsideCidr": tunnel_opt.get("TunnelInsideCidr"),
                    "tunnelInsideIpv6Cidr": tunnel_opt.get("TunnelInsideIpv6Cidr"),
                }
                # Remove keys with None values
                tunnel_option = {k: v for k, v in tunnel_option.items() if v is not None}
                tunnel_option_set.append(tunnel_option)

        # Build VPN connection options for response
        options_response = {
            "enableAcceleration": enable_acceleration,
            "localIpv4NetworkCidr": local_ipv4_network_cidr,
            "localIpv6NetworkCidr": local_ipv6_network_cidr,
            "outsideIpAddressType": outside_ip_address_type,
            "remoteIpv4NetworkCidr": remote_ipv4_network_cidr,
            "remoteIpv6NetworkCidr": remote_ipv6_network_cidr,
            "staticRoutesOnly": static_routes_only,
            "transportTransitGatewayAttachmentId": transport_tgw_attachment_id,
            "tunnelBandwidth": tunnel_bandwidth,
            "tunnelInsideIpVersion": tunnel_inside_ip_version,
            "tunnelOptionSet": tunnel_option_set,
        }

        # Build initial VPN connection object
        vpn_connection_obj = {
            "vpnConnectionId": vpn_connection_id,
            "state": "pending",
            "customerGatewayConfiguration": escaped_customer_gateway_configuration,
            "customerGatewayId": customer_gateway_id,
            "vpnGatewayId": vpn_gateway_id,
            "transitGatewayId": transit_gateway_id,
            "vpnConcentratorId": vpn_concentrator_id,
            "type": vpn_type,
            "options": options_response,
            "routes": [],
            "tagSet": tags,
            "category": "VPN",
            "vgwTelemetry": [
                {
                    "outsideIpAddress": "203.0.113.1",
                    "status": "UP",
                    "lastStatusChange": datetime.now(timezone.utc).isoformat(),
                    "statusMessage": "",
                    "acceptedRouteCount": 0,
                    "certificateArn": None,
                },
                {
                    "outsideIpAddress": "203.0.113.2",
                    "status": "UP",
                    "lastStatusChange": datetime.now(timezone.utc).isoformat(),
                    "statusMessage": "",
                    "acceptedRouteCount": 0,
                    "certificateArn": None,
                },
            ],
            "gatewayAssociationState": "associated",
            "preSharedKeyArn": None,
            "coreNetworkArn": None,
            "coreNetworkAttachmentArn": None,
        }

        # Store the VPN connection in state
        self.state.vpn_connections[vpn_connection_id] = vpn_connection_obj
        self.state.resources[vpn_connection_id] = vpn_connection_obj

        # Build response
        response = {
            "requestId": self.generate_request_id(),
            "vpnConnection": vpn_connection_obj,
        }
        return response


    def create_vpn_connection_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        destination_cidr_block = params.get("DestinationCidrBlock")
        vpn_connection_id = params.get("VpnConnectionId")

        if not destination_cidr_block:
            raise Exception("Missing required parameter DestinationCidrBlock")
        if not vpn_connection_id:
            raise Exception("Missing required parameter VpnConnectionId")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise Exception(f"VpnConnectionId {vpn_connection_id} does not exist")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Check if route already exists
        for route in vpn_connection.get("routes", []):
            if route.get("destinationCidrBlock") == destination_cidr_block and route.get("state") != "deleted":
                # Route already exists, do nothing
                return {
                    "requestId": self.generate_request_id(),
                    "return": True,
                }

        # Add new static route
        new_route = {
            "destinationCidrBlock": destination_cidr_block,
            "source": "Static",
            "state": "available",
        }
        vpn_connection.setdefault("routes", []).append(new_route)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def delete_vpn_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpn_connection_id = params.get("VpnConnectionId")
        if not vpn_connection_id:
            raise Exception("Missing required parameter VpnConnectionId")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            # According to AWS behavior, deleting a non-existent resource returns success
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Mark VPN connection as deleted
        vpn_connection["state"] = "deleted"

        # Optionally, remove from resources dict or keep for history
        # Here we keep it but mark as deleted

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def delete_vpn_connection_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        destination_cidr_block = params.get("DestinationCidrBlock")
        vpn_connection_id = params.get("VpnConnectionId")

        if not destination_cidr_block:
            raise Exception("Missing required parameter DestinationCidrBlock")
        if not vpn_connection_id:
            raise Exception("Missing required parameter VpnConnectionId")

        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise Exception(f"VpnConnectionId {vpn_connection_id} does not exist")

        routes = vpn_connection.get("routes", [])
        route_found = False
        for route in routes:
            if route.get("destinationCidrBlock") == destination_cidr_block and route.get("state") != "deleted":
                route["state"] = "deleted"
                route_found = True
                break

        if not route_found:
            # AWS returns success even if route does not exist
            pass

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def describe_vpn_connections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        if params.get("DryRun"):
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Filters parsing
        filters = []
        # Filters come as Filter.N.Name and Filter.N.Value.M
        # We'll parse all Filter.N.Name and Filter.N.Value.M keys
        # Collect filters in a list of dicts: {"Name": str, "Values": [str]}
        i = 1
        while True:
            filter_name_key = f"Filter.{i}.Name"
            filter_values_prefix = f"Filter.{i}.Value."
            filter_name = params.get(filter_name_key)
            if not filter_name:
                break
            values = []
            j = 1
            while True:
                val = params.get(f"{filter_values_prefix}{j}")
                if not val:
                    break
                values.append(val)
                j += 1
            filters.append({"Name": filter_name, "Values": values})
            i += 1

        # VpnConnectionId.N parsing
        vpn_connection_ids = []
        i = 1
        while True:
            vpn_id = params.get(f"VpnConnectionId.{i}")
            if not vpn_id:
                break
            vpn_connection_ids.append(vpn_id)
            i += 1

        # Collect vpn connections to describe
        vpn_connections_to_describe = []
        if vpn_connection_ids:
            for vpn_id in vpn_connection_ids:
                vpn_conn = self.state.vpn_connections.get(vpn_id)
                if vpn_conn and vpn_conn.get("state") != "deleted":
                    vpn_connections_to_describe.append(vpn_conn)
        else:
            # No specific IDs, describe all non-deleted vpn connections
            vpn_connections_to_describe = [
                vpn for vpn in self.state.vpn_connections.values() if vpn.get("state") != "deleted"
            ]

        # Apply filters
        def matches_filter(vpn_conn: Dict[str, Any], filter_: Dict[str, Any]) -> bool:
            name = filter_.get("Name", "")
            values = filter_.get("Values", [])
            if not name or not values:
                return True
            name_lower = name.lower()
            if name_lower == "state":
                return vpn_conn.get("state") in values
            elif name_lower == "vpn-connection-id":
                return vpn_conn.get("vpnConnectionId") in values
            elif name_lower == "vpn-gateway-id":
                return vpn_conn.get("vpnGatewayId") in values
            elif name_lower == "customer-gateway-id":
                return vpn_conn.get("customerGatewayId") in values
            elif name_lower == "type":
                return vpn_conn.get("type") in values
            elif name_lower == "transit-gateway-id":
                return vpn_conn.get("transitGatewayId") in values
            elif name_lower.startswith("tag:"):
                tag_key = name[4:]
                tags = vpn_conn.get("tagSet", [])
                for tag in tags:
                    if isinstance(tag, dict):
                        if tag.get("Key") == tag_key and tag.get("Value") in values:
                            return True
                    elif hasattr(tag, "Key"):
                        if tag.Key == tag_key and tag.Value in values:
                            return True
                return False
            return True  # Unknown filter, pass through

        # Filter vpn connections
        filtered_vpn_connections = []
        for vpn_conn in vpn_connections_to_describe:
            if all(matches_filter(vpn_conn, f) for f in filters):
                filtered_vpn_connections.append(vpn_conn)

        # Build response
        vpn_connection_set = []
        for vpn_conn in filtered_vpn_connections:
            vpn_connection_set.append(vpn_conn)

        return {
            "requestId": self.generate_request_id(),
            "vpnConnectionSet": vpn_connection_set,
        }

    def get_active_vpn_tunnel_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpn_connection_id = params.get("VpnConnectionId")
        vpn_tunnel_outside_ip = params.get("VpnTunnelOutsideIpAddress")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # DryRun check: assume permission granted for simplicity
            return {"requestId": self.generate_request_id(), "DryRun": True}

        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")
        if not vpn_tunnel_outside_ip:
            raise ValueError("VpnTunnelOutsideIpAddress is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # Find the tunnel matching the outside IP address
        tunnel_status = None
        for telemetry in vpn_connection.get("vgwTelemetry", []):
            if telemetry.get("outsideIpAddress") == vpn_tunnel_outside_ip:
                # Compose activeVpnTunnelStatus object
                tunnel_status = {
                    "ikeVersion": telemetry.get("ikeVersion"),
                    "phase1DHGroup": telemetry.get("phase1DHGroup"),
                    "phase1EncryptionAlgorithm": telemetry.get("phase1EncryptionAlgorithm"),
                    "phase1IntegrityAlgorithm": telemetry.get("phase1IntegrityAlgorithm"),
                    "phase2DHGroup": telemetry.get("phase2DHGroup"),
                    "phase2EncryptionAlgorithm": telemetry.get("phase2EncryptionAlgorithm"),
                    "phase2IntegrityAlgorithm": telemetry.get("phase2IntegrityAlgorithm"),
                    "provisioningStatus": telemetry.get("provisioningStatus"),
                    "provisioningStatusReason": telemetry.get("provisioningStatusReason"),
                }
                break

        if tunnel_status is None:
            # If no matching tunnel found, return empty or raise error
            raise ValueError(f"No active tunnel found for IP {vpn_tunnel_outside_ip} in VPN Connection {vpn_connection_id}")

        return {
            "activeVpnTunnelStatus": tunnel_status,
            "requestId": self.generate_request_id(),
        }


    def get_vpn_connection_device_sample_configuration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        internet_key_exchange_version = params.get("InternetKeyExchangeVersion")
        sample_type = params.get("SampleType")
        device_type_id = params.get("VpnConnectionDeviceTypeId")
        vpn_connection_id = params.get("VpnConnectionId")

        if dry_run:
            # DryRun check: assume permission granted for simplicity
            return {"requestId": self.generate_request_id(), "DryRun": True}

        if not device_type_id:
            raise ValueError("VpnConnectionDeviceTypeId is required")
        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # For the sample configuration, we simulate a sample config string.
        # In real AWS, this would be a device-specific config file content.
        # We will create a simple string with some placeholders.

        # Validate InternetKeyExchangeVersion if provided
        if internet_key_exchange_version and internet_key_exchange_version not in ("ikev1", "ikev2"):
            raise ValueError("InternetKeyExchangeVersion must be 'ikev1' or 'ikev2' if specified")

        # Validate SampleType if provided
        if sample_type and sample_type not in ("compatibility", "recommended"):
            raise ValueError("SampleType must be 'compatibility' or 'recommended' if specified")

        # Check device type exists in device types list
        device_types = getattr(self.state, "vpn_connection_device_types", {})
        device_type = device_types.get(device_type_id)
        if not device_type:
            raise ValueError(f"VpnConnectionDeviceTypeId {device_type_id} does not exist")

        # Compose a sample configuration string
        sample_config = (
            f"# Sample VPN Configuration for device type {device_type_id}\n"
            f"# VPN Connection ID: {vpn_connection_id}\n"
            f"# IKE Version: {internet_key_exchange_version or 'default'}\n"
            f"# Sample Type: {sample_type or 'default'}\n"
            f"# Vendor: {device_type.get('vendor', 'unknown')}\n"
            f"# Platform: {device_type.get('platform', 'unknown')}\n"
            f"# Software: {device_type.get('software', 'unknown')}\n"
            "\n"
            "set vpn ... # This is a placeholder configuration\n"
        )

        return {
            "requestId": self.generate_request_id(),
            "vpnConnectionDeviceSampleConfiguration": sample_config,
        }


    def get_vpn_connection_device_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            # DryRun check: assume permission granted for simplicity
            return {"requestId": self.generate_request_id(), "DryRun": True}

        # Retrieve all device types from state
        device_types_dict = getattr(self.state, "vpn_connection_device_types", {})

        # Sort device types by vpnConnectionDeviceTypeId for consistent pagination
        sorted_device_types = sorted(device_types_dict.values(), key=lambda d: d.get("vpnConnectionDeviceTypeId", ""))

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ValueError("Invalid NextToken")

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ValueError("MaxResults must be an integer")
            if max_results < 200 or max_results > 1000:
                raise ValueError("MaxResults must be between 200 and 1000")

        # Default max_results to all if not specified
        max_results = max_results or len(sorted_device_types)

        # Slice the list for pagination
        paged_device_types = sorted_device_types[start_index : start_index + max_results]

        # Determine new next token
        new_next_token = None
        if start_index + max_results < len(sorted_device_types):
            new_next_token = str(start_index + max_results)

        return {
            "vpnConnectionDeviceTypeSet": paged_device_types,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def get_vpn_tunnel_replacement_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        vpn_connection_id = params.get("VpnConnectionId")
        vpn_tunnel_outside_ip = params.get("VpnTunnelOutsideIpAddress")

        if dry_run:
            # DryRun check: assume permission granted for simplicity
            return {"requestId": self.generate_request_id(), "DryRun": True}

        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")
        if not vpn_tunnel_outside_ip:
            raise ValueError("VpnTunnelOutsideIpAddress is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # Find the tunnel matching the outside IP address
        maintenance_details = None
        for telemetry in vpn_connection.get("vgwTelemetry", []):
            if telemetry.get("outsideIpAddress") == vpn_tunnel_outside_ip:
                # Compose maintenanceDetails object
                maintenance_details = telemetry.get("maintenanceDetails", {})
                break

        if maintenance_details is None:
            # If no matching tunnel found, return empty or raise error
            raise ValueError(f"No tunnel found for IP {vpn_tunnel_outside_ip} in VPN Connection {vpn_connection_id}")

        return {
            "customerGatewayId": vpn_connection.get("customerGatewayId"),
            "maintenanceDetails": {
                "lastMaintenanceApplied": maintenance_details.get("lastMaintenanceApplied"),
                "maintenanceAutoAppliedAfter": maintenance_details.get("maintenanceAutoAppliedAfter"),
                "pendingMaintenance": maintenance_details.get("pendingMaintenance"),
            },
            "requestId": self.generate_request_id(),
            "transitGatewayId": vpn_connection.get("transitGatewayId"),
            "vpnConnectionId": vpn_connection_id,
            "vpnGatewayId": vpn_connection.get("vpnGatewayId"),
            "vpnTunnelOutsideIpAddress": vpn_tunnel_outside_ip,
        }


    def modify_vpn_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        customer_gateway_id = params.get("CustomerGatewayId")
        dry_run = params.get("DryRun", False)
        transit_gateway_id = params.get("TransitGatewayId")
        vpn_connection_id = params.get("VpnConnectionId")
        vpn_gateway_id = params.get("VpnGatewayId")

        if dry_run:
            # DryRun check: assume permission granted for simplicity
            return {"requestId": self.generate_request_id(), "DryRun": True}

        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # Modify customer gateway id if provided
        if customer_gateway_id is not None:
            # Validate customer gateway exists
            customer_gateway = self.state.get_resource(customer_gateway_id)
            if customer_gateway is None:
                raise ValueError(f"CustomerGatewayId {customer_gateway_id} does not exist")
            vpn_connection["customerGatewayId"] = customer_gateway_id

        # Modify transit gateway id if provided
        if transit_gateway_id is not None:
            # Validate transit gateway exists
            transit_gateway = self.state.get_resource(transit_gateway_id)
            if transit_gateway is None:
                raise ValueError(f"TransitGatewayId {transit_gateway_id} does not exist")
            vpn_connection["transitGatewayId"] = transit_gateway_id
            # If transit gateway is set, clear vpnGatewayId (AWS behavior)
            vpn_connection["vpnGatewayId"] = None

        # Modify vpn gateway id if provided
        if vpn_gateway_id is not None:
            # Validate vpn gateway exists
            vpn_gateway = self.state.get_resource(vpn_gateway_id)
            if vpn_gateway is None:
                raise ValueError(f"VpnGatewayId {vpn_gateway_id} does not exist")
            vpn_connection["vpnGatewayId"] = vpn_gateway_id
            # If vpn gateway is set, clear transitGatewayId (AWS behavior)
            vpn_connection["transitGatewayId"] = None

        # Update state
        self.state.vpn_connections[vpn_connection_id] = vpn_connection

        return {
            "requestId": self.generate_request_id(),
            "vpnConnection": vpn_connection,
        }

    def modify_vpn_connection_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpn_connection_id = params.get("VpnConnectionId")
        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # DryRun check
        if params.get("DryRun"):
            # In real AWS, this would check permissions; here we simulate success
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Update options fields if provided
        options = vpn_connection.get("options", {})
        # Update local IPv4 CIDR
        if "LocalIpv4NetworkCidr" in params:
            options["localIpv4NetworkCidr"] = params["LocalIpv4NetworkCidr"]
        # Update local IPv6 CIDR
        if "LocalIpv6NetworkCidr" in params:
            options["localIpv6NetworkCidr"] = params["LocalIpv6NetworkCidr"]
        # Update remote IPv4 CIDR
        if "RemoteIpv4NetworkCidr" in params:
            options["remoteIpv4NetworkCidr"] = params["RemoteIpv4NetworkCidr"]
        # Update remote IPv6 CIDR
        if "RemoteIpv6NetworkCidr" in params:
            options["remoteIpv6NetworkCidr"] = params["RemoteIpv6NetworkCidr"]

        vpn_connection["options"] = options

        # Simulate temporary unavailability by setting state to pending then back to available
        vpn_connection["state"] = "pending"
        # In a real async environment, this would be delayed; here we immediately set back
        vpn_connection["state"] = "available"

        request_id = self.generate_request_id()
        return {
            "requestId": request_id,
            "vpnConnection": vpn_connection,
        }


    def modify_vpn_tunnel_certificate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpn_connection_id = params.get("VpnConnectionId")
        vpn_tunnel_outside_ip = params.get("VpnTunnelOutsideIpAddress")

        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")
        if not vpn_tunnel_outside_ip:
            raise ValueError("VpnTunnelOutsideIpAddress is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Find the tunnel telemetry matching the outside IP address
        vgw_telemetry = vpn_connection.get("vgwTelemetry", [])
        tunnel_found = False
        for tunnel in vgw_telemetry:
            if tunnel.get("outsideIpAddress") == vpn_tunnel_outside_ip:
                # Simulate certificate modification by updating certificateArn to a new dummy ARN
                tunnel["certificateArn"] = f"arn:aws:acm:region:account:certificate/{self.generate_unique_id()}"
                tunnel_found = True
                break

        if not tunnel_found:
            raise ValueError(f"VPN Tunnel with outside IP {vpn_tunnel_outside_ip} not found in VPN Connection {vpn_connection_id}")

        request_id = self.generate_request_id()
        return {
            "requestId": request_id,
            "vpnConnection": vpn_connection,
        }


    def modify_vpn_tunnel_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpn_connection_id = params.get("VpnConnectionId")
        vpn_tunnel_outside_ip = params.get("VpnTunnelOutsideIpAddress")
        tunnel_options = params.get("TunnelOptions")

        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")
        if not vpn_tunnel_outside_ip:
            raise ValueError("VpnTunnelOutsideIpAddress is required")
        if not tunnel_options:
            raise ValueError("TunnelOptions is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Find the tunnel telemetry matching the outside IP address
        vgw_telemetry = vpn_connection.get("vgwTelemetry", [])
        tunnel = None
        for t in vgw_telemetry:
            if t.get("outsideIpAddress") == vpn_tunnel_outside_ip:
                tunnel = t
                break

        if not tunnel:
            raise ValueError(f"VPN Tunnel with outside IP {vpn_tunnel_outside_ip} not found in VPN Connection {vpn_connection_id}")

        # Update tunnel options according to the specification
        # Map input keys to lower camel case keys used in telemetry tunnel dict
        # We will update only keys present in tunnel_options
        # The keys in tunnel_options are PascalCase or camelCase, we normalize keys to lower camel case for internal use

        def normalize_key(key: str) -> str:
            # Convert PascalCase or camelCase to lowerCamelCase (mostly same)
            # For example: DPDTimeoutAction -> dpdTimeoutAction
            if not key:
                return key
            return key[0].lower() + key[1:]

        for key, value in tunnel_options.items():
            if key == "LogOptions" and isinstance(value, dict):
                # LogOptions is nested
                log_options = tunnel.get("logOptions", {})
                cloudwatch_opts = value.get("CloudWatchLogOptions")
                if cloudwatch_opts:
                    cw_opts = log_options.get("cloudWatchLogOptions", {})
                    for cw_key, cw_value in cloudwatch_opts.items():
                        # Normalize keys for cloudwatch options
                        cw_key_norm = cw_key[0].lower() + cw_key[1:] if cw_key else cw_key
                        cw_opts[cw_key_norm] = cw_value
                    log_options["cloudWatchLogOptions"] = cw_opts
                tunnel["logOptions"] = log_options
            elif isinstance(value, list):
                # For lists of objects with 'Value' keys, convert to list of values
                if all(isinstance(item, dict) and "Value" in item for item in value):
                    tunnel[normalize_key(key)] = [item["Value"] for item in value]
                else:
                    tunnel[normalize_key(key)] = value
            else:
                tunnel[normalize_key(key)] = value

        # Also update options in vpn_connection.options if relevant keys are present in TunnelOptions
        options = vpn_connection.get("options", {})
        # Some keys in TunnelOptions may correspond to options keys
        # For example, PreSharedKey, StaticRoutesOnly, EnableAcceleration, TunnelBandwidth, TunnelInsideIpVersion, etc.
        # We update options keys if present in TunnelOptions

        # Map of TunnelOptions keys to options keys (lower camel case)
        options_keys_map = {
            "EnableAcceleration": "enableAcceleration",
            "LocalIpv4NetworkCidr": "localIpv4NetworkCidr",
            "LocalIpv6NetworkCidr": "localIpv6NetworkCidr",
            "OutsideIpAddressType": "outsideIpAddressType",
            "RemoteIpv4NetworkCidr": "remoteIpv4NetworkCidr",
            "RemoteIpv6NetworkCidr": "remoteIpv6NetworkCidr",
            "StaticRoutesOnly": "staticRoutesOnly",
            "TransportTransitGatewayAttachmentId": "transportTransitGatewayAttachmentId",
            "TunnelBandwidth": "tunnelBandwidth",
            "TunnelInsideIpVersion": "tunnelInsideIpVersion",
        }
        for key, opt_key in options_keys_map.items():
            if key in tunnel_options:
                options[opt_key] = tunnel_options[key]

        vpn_connection["options"] = options

        request_id = self.generate_request_id()
        return {
            "requestId": request_id,
            "vpnConnection": vpn_connection,
        }


    def replace_vpn_tunnel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpn_connection_id = params.get("VpnConnectionId")
        vpn_tunnel_outside_ip = params.get("VpnTunnelOutsideIpAddress")

        if not vpn_connection_id:
            raise ValueError("VpnConnectionId is required")
        if not vpn_tunnel_outside_ip:
            raise ValueError("VpnTunnelOutsideIpAddress is required")

        vpn_connection = self.state.vpn_connections.get(vpn_connection_id)
        if not vpn_connection:
            raise ValueError(f"VPN Connection {vpn_connection_id} does not exist")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Find the tunnel telemetry matching the outside IP address
        vgw_telemetry = vpn_connection.get("vgwTelemetry", [])
        tunnel = None
        for t in vgw_telemetry:
            if t.get("outsideIpAddress") == vpn_tunnel_outside_ip:
                tunnel = t
                break

        if not tunnel:
            raise ValueError(f"VPN Tunnel with outside IP {vpn_tunnel_outside_ip} not found in VPN Connection {vpn_connection_id}")

        # Simulate tunnel replacement by updating lastStatusChange and statusMessage
        from datetime import datetime
        tunnel["lastStatusChange"] = datetime.utcnow().isoformat() + "Z"
        tunnel["statusMessage"] = "Tunnel replacement triggered"
        tunnel["status"] = "pending"

        # In a real environment, replacement would be asynchronous; here we simulate immediate success
        tunnel["status"] = "up"
        tunnel["statusMessage"] = "Tunnel replaced successfully"

        request_id = self.generate_request_id()
        return {
            "requestId": request_id,
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class VPNconnectionsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateVpnConnection", self.create_vpn_connection)
        self.register_action("CreateVpnConnectionRoute", self.create_vpn_connection_route)
        self.register_action("DeleteVpnConnection", self.delete_vpn_connection)
        self.register_action("DeleteVpnConnectionRoute", self.delete_vpn_connection_route)
        self.register_action("DescribeVpnConnections", self.describe_vpn_connections)
        self.register_action("GetActiveVpnTunnelStatus", self.get_active_vpn_tunnel_status)
        self.register_action("GetVpnConnectionDeviceSampleConfiguration", self.get_vpn_connection_device_sample_configuration)
        self.register_action("GetVpnConnectionDeviceTypes", self.get_vpn_connection_device_types)
        self.register_action("GetVpnTunnelReplacementStatus", self.get_vpn_tunnel_replacement_status)
        self.register_action("ModifyVpnConnection", self.modify_vpn_connection)
        self.register_action("ModifyVpnConnectionOptions", self.modify_vpn_connection_options)
        self.register_action("ModifyVpnTunnelCertificate", self.modify_vpn_tunnel_certificate)
        self.register_action("ModifyVpnTunnelOptions", self.modify_vpn_tunnel_options)
        self.register_action("ReplaceVpnTunnel", self.replace_vpn_tunnel)

    def create_vpn_connection(self, params):
        return self.backend.create_vpn_connection(params)

    def create_vpn_connection_route(self, params):
        return self.backend.create_vpn_connection_route(params)

    def delete_vpn_connection(self, params):
        return self.backend.delete_vpn_connection(params)

    def delete_vpn_connection_route(self, params):
        return self.backend.delete_vpn_connection_route(params)

    def describe_vpn_connections(self, params):
        return self.backend.describe_vpn_connections(params)

    def get_active_vpn_tunnel_status(self, params):
        return self.backend.get_active_vpn_tunnel_status(params)

    def get_vpn_connection_device_sample_configuration(self, params):
        return self.backend.get_vpn_connection_device_sample_configuration(params)

    def get_vpn_connection_device_types(self, params):
        return self.backend.get_vpn_connection_device_types(params)

    def get_vpn_tunnel_replacement_status(self, params):
        return self.backend.get_vpn_tunnel_replacement_status(params)

    def modify_vpn_connection(self, params):
        return self.backend.modify_vpn_connection(params)

    def modify_vpn_connection_options(self, params):
        return self.backend.modify_vpn_connection_options(params)

    def modify_vpn_tunnel_certificate(self, params):
        return self.backend.modify_vpn_tunnel_certificate(params)

    def modify_vpn_tunnel_options(self, params):
        return self.backend.modify_vpn_tunnel_options(params)

    def replace_vpn_tunnel(self, params):
        return self.backend.replace_vpn_tunnel(params)
