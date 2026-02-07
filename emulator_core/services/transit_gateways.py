from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class ApplianceModeSupport(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class DnsSupport(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class Ipv6Support(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class SecurityGroupReferencingSupport(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class VpcAttachmentState(str, Enum):
    INITIATING = "initiating"
    INITIATING_REQUEST = "initiatingRequest"
    PENDING_ACCEPTANCE = "pendingAcceptance"
    ROLLING_BACK = "rollingBack"
    PENDING = "pending"
    AVAILABLE = "available"
    MODIFYING = "modifying"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILED = "failed"
    REJECTED = "rejected"
    REJECTING = "rejecting"
    FAILING = "failing"


class TransitGatewayState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    MODIFYING = "modifying"
    DELETING = "deleting"
    DELETED = "deleted"


class EncryptionState(str, Enum):
    ENABLING = "enabling"
    ENABLED = "enabled"
    DISABLING = "disabling"
    DISABLED = "disabled"


class AutoAcceptSharedAttachments(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class DefaultRouteTableAssociation(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class DefaultRouteTablePropagation(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class MulticastSupport(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class VpnEcmpSupport(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class ResourceType(str, Enum):
    CAPACITY_RESERVATION = "capacity-reservation"
    CLIENT_VPN_ENDPOINT = "client-vpn-endpoint"
    CUSTOMER_GATEWAY = "customer-gateway"
    CARRIER_GATEWAY = "carrier-gateway"
    COIP_POOL = "coip-pool"
    DECLARATIVE_POLICIES_REPORT = "declarative-policies-report"
    DEDICATED_HOST = "dedicated-host"
    DHCP_OPTIONS = "dhcp-options"
    EGRESS_ONLY_INTERNET_GATEWAY = "egress-only-internet-gateway"
    ELASTIC_IP = "elastic-ip"
    ELASTIC_GPU = "elastic-gpu"
    EXPORT_IMAGE_TASK = "export-image-task"
    EXPORT_INSTANCE_TASK = "export-instance-task"
    FLEET = "fleet"
    FPGA_IMAGE = "fpga-image"
    HOST_RESERVATION = "host-reservation"
    IMAGE = "image"
    IMAGE_USAGE_REPORT = "image-usage-report"
    IMPORT_IMAGE_TASK = "import-image-task"
    IMPORT_SNAPSHOT_TASK = "import-snapshot-task"
    INSTANCE = "instance"
    INSTANCE_EVENT_WINDOW = "instance-event-window"
    INTERNET_GATEWAY = "internet-gateway"
    IPAM = "ipam"
    IPAM_POOL = "ipam-pool"
    IPAM_SCOPE = "ipam-scope"
    IPV4POOL_EC2 = "ipv4pool-ec2"
    IPV6POOL_EC2 = "ipv6pool-ec2"
    KEY_PAIR = "key-pair"
    LAUNCH_TEMPLATE = "launch-template"
    LOCAL_GATEWAY = "local-gateway"
    LOCAL_GATEWAY_ROUTE_TABLE = "local-gateway-route-table"
    LOCAL_GATEWAY_VIRTUAL_INTERFACE = "local-gateway-virtual-interface"
    LOCAL_GATEWAY_VIRTUAL_INTERFACE_GROUP = "local-gateway-virtual-interface-group"
    LOCAL_GATEWAY_ROUTE_TABLE_VPC_ASSOCIATION = "local-gateway-route-table-vpc-association"
    LOCAL_GATEWAY_ROUTE_TABLE_VIRTUAL_INTERFACE_GROUP_ASSOCIATION = "local-gateway-route-table-virtual-interface-group-association"
    NATGATEWAY = "natgateway"
    NETWORK_ACL = "network-acl"
    NETWORK_INTERFACE = "network-interface"
    NETWORK_INSIGHTS_ANALYSIS = "network-insights-analysis"
    NETWORK_INSIGHTS_PATH = "network-insights-path"
    NETWORK_INSIGHTS_ACCESS_SCOPE = "network-insights-access-scope"
    NETWORK_INSIGHTS_ACCESS_SCOPE_ANALYSIS = "network-insights-access-scope-analysis"
    OUTPOST_LAG = "outpost-lag"
    PLACEMENT_GROUP = "placement-group"
    PREFIX_LIST = "prefix-list"
    REPLACE_ROOT_VOLUME_TASK = "replace-root-volume-task"
    RESERVED_INSTANCES = "reserved-instances"
    ROUTE_TABLE = "route-table"
    SECURITY_GROUP = "security-group"
    SECURITY_GROUP_RULE = "security-group-rule"
    SERVICE_LINK_VIRTUAL_INTERFACE = "service-link-virtual-interface"
    SNAPSHOT = "snapshot"
    SPOT_FLEET_REQUEST = "spot-fleet-request"
    SPOT_INSTANCES_REQUEST = "spot-instances-request"
    SUBNET = "subnet"
    SUBNET_CIDR_RESERVATION = "subnet-cidr-reservation"
    TRAFFIC_MIRROR_FILTER = "traffic-mirror-filter"
    TRAFFIC_MIRROR_SESSION = "traffic-mirror-session"
    TRAFFIC_MIRROR_TARGET = "traffic-mirror-target"
    TRANSIT_GATEWAY = "transit-gateway"
    TRANSIT_GATEWAY_ATTACHMENT = "transit-gateway-attachment"
    TRANSIT_GATEWAY_CONNECT_PEER = "transit-gateway-connect-peer"
    TRANSIT_GATEWAY_MULTICAST_DOMAIN = "transit-gateway-multicast-domain"
    TRANSIT_GATEWAY_POLICY_TABLE = "transit-gateway-policy-table"
    TRANSIT_GATEWAY_METERING_POLICY = "transit-gateway-metering-policy"
    TRANSIT_GATEWAY_ROUTE_TABLE = "transit-gateway-route-table"
    TRANSIT_GATEWAY_ROUTE_TABLE_ANNOUNCEMENT = "transit-gateway-route-table-announcement"
    VOLUME = "volume"
    VPC = "vpc"
    VPC_ENDPOINT = "vpc-endpoint"
    VPC_ENDPOINT_CONNECTION = "vpc-endpoint-connection"
    VPC_ENDPOINT_SERVICE = "vpc-endpoint-service"
    VPC_ENDPOINT_SERVICE_PERMISSION = "vpc-endpoint-service-permission"
    VPC_PEERING_CONNECTION = "vpc-peering-connection"
    VPN_CONNECTION = "vpn-connection"
    VPN_GATEWAY = "vpn-gateway"
    VPC_FLOW_LOG = "vpc-flow-log"
    CAPACITY_RESERVATION_FLEET = "capacity-reservation-fleet"
    TRAFFIC_MIRROR_FILTER_RULE = "traffic-mirror-filter-rule"
    VPC_ENDPOINT_CONNECTION_DEVICE_TYPE = "vpc-endpoint-connection-device-type"
    VERIFIED_ACCESS_INSTANCE = "verified-access-instance"
    VERIFIED_ACCESS_GROUP = "verified-access-group"
    VERIFIED_ACCESS_ENDPOINT = "verified-access-endpoint"
    VERIFIED_ACCESS_POLICY = "verified-access-policy"
    VERIFIED_ACCESS_TRUST_PROVIDER = "verified-access-trust-provider"
    VPN_CONNECTION_DEVICE_TYPE = "vpn-connection-device-type"
    VPC_BLOCK_PUBLIC_ACCESS_EXCLUSION = "vpc-block-public-access-exclusion"
    VPC_ENCRYPTION_CONTROL = "vpc-encryption-control"
    ROUTE_SERVER = "route-server"
    ROUTE_SERVER_ENDPOINT = "route-server-endpoint"
    ROUTE_SERVER_PEER = "route-server-peer"
    IPAM_RESOURCE_DISCOVERY = "ipam-resource-discovery"
    IPAM_RESOURCE_DISCOVERY_ASSOCIATION = "ipam-resource-discovery-association"
    INSTANCE_CONNECT_ENDPOINT = "instance-connect-endpoint"
    VERIFIED_ACCESS_ENDPOINT_TARGET = "verified-access-endpoint-target"
    IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKEN = "ipam-external-resource-verification-token"
    CAPACITY_BLOCK = "capacity-block"
    MAC_MODIFICATION_TASK = "mac-modification-task"
    IPAM_PREFIX_LIST_RESOLVER = "ipam-prefix-list-resolver"
    IPAM_POLICY = "ipam-policy"
    IPAM_PREFIX_LIST_RESOLVER_TARGET = "ipam-prefix-list-resolver-target"
    CAPACITY_MANAGER_DATA_EXPORT = "capacity-manager-data-export"
    VPN_CONCENTRATOR = "vpn-concentrator"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TransitGatewayVpcAttachmentOptions:
    applianceModeSupport: Optional[ApplianceModeSupport] = None
    dnsSupport: Optional[DnsSupport] = None
    ipv6Support: Optional[Ipv6Support] = None
    securityGroupReferencingSupport: Optional[SecurityGroupReferencingSupport] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.applianceModeSupport is not None:
            result["ApplianceModeSupport"] = self.applianceModeSupport.value
        if self.dnsSupport is not None:
            result["DnsSupport"] = self.dnsSupport.value
        if self.ipv6Support is not None:
            result["Ipv6Support"] = self.ipv6Support.value
        if self.securityGroupReferencingSupport is not None:
            result["SecurityGroupReferencingSupport"] = self.securityGroupReferencingSupport.value
        return result


@dataclass
class TransitGatewayVpcAttachment:
    creationTime: Optional[datetime] = None
    options: Optional[TransitGatewayVpcAttachmentOptions] = None
    state: Optional[VpcAttachmentState] = None
    subnetIds: List[str] = field(default_factory=list)
    tagSet: List[Tag] = field(default_factory=list)
    transitGatewayAttachmentId: Optional[str] = None
    transitGatewayId: Optional[str] = None
    vpcId: Optional[str] = None
    vpcOwnerId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CreationTime": self.creationTime.isoformat() if self.creationTime else None,
            "Options": self.options.to_dict() if self.options else None,
            "State": self.state.value if self.state else None,
            "SubnetIds": self.subnetIds,
            "TagSet": [tag.to_dict() for tag in self.tagSet],
            "TransitGatewayAttachmentId": self.transitGatewayAttachmentId,
            "TransitGatewayId": self.transitGatewayId,
            "VpcId": self.vpcId,
            "VpcOwnerId": self.vpcOwnerId,
        }


@dataclass
class TransitGatewayRequestOptions:
    amazonSideAsn: Optional[int] = None
    autoAcceptSharedAttachments: Optional[AutoAcceptSharedAttachments] = None
    defaultRouteTableAssociation: Optional[DefaultRouteTableAssociation] = None
    defaultRouteTablePropagation: Optional[DefaultRouteTablePropagation] = None
    dnsSupport: Optional[DnsSupport] = None
    multicastSupport: Optional[MulticastSupport] = None
    securityGroupReferencingSupport: Optional[SecurityGroupReferencingSupport] = None
    transitGatewayCidrBlocks: List[str] = field(default_factory=list)
    vpnEcmpSupport: Optional[VpnEcmpSupport] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.amazonSideAsn is not None:
            result["AmazonSideAsn"] = self.amazonSideAsn
        if self.autoAcceptSharedAttachments is not None:
            result["AutoAcceptSharedAttachments"] = self.autoAcceptSharedAttachments.value
        if self.defaultRouteTableAssociation is not None:
            result["DefaultRouteTableAssociation"] = self.defaultRouteTableAssociation.value
        if self.defaultRouteTablePropagation is not None:
            result["DefaultRouteTablePropagation"] = self.defaultRouteTablePropagation.value
        if self.dnsSupport is not None:
            result["DnsSupport"] = self.dnsSupport.value
        if self.multicastSupport is not None:
            result["MulticastSupport"] = self.multicastSupport.value
        if self.securityGroupReferencingSupport is not None:
            result["SecurityGroupReferencingSupport"] = self.securityGroupReferencingSupport.value
        if self.transitGatewayCidrBlocks:
            result["TransitGatewayCidrBlocks"] = self.transitGatewayCidrBlocks
        if self.vpnEcmpSupport is not None:
            result["VpnEcmpSupport"] = self.vpnEcmpSupport.value
        return result


@dataclass
class EncryptionSupport:
    encryptionState: Optional[EncryptionState] = None
    stateMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EncryptionState": self.encryptionState.value if self.encryptionState else None,
            "StateMessage": self.stateMessage,
        }


@dataclass
class TransitGatewayOptions:
    amazonSideAsn: Optional[int] = None
    associationDefaultRouteTableId: Optional[str] = None
    autoAcceptSharedAttachments: Optional[AutoAcceptSharedAttachments] = None
    defaultRouteTableAssociation: Optional[DefaultRouteTableAssociation] = None
    defaultRouteTablePropagation: Optional[DefaultRouteTablePropagation] = None
    dnsSupport: Optional[DnsSupport] = None
    encryptionSupport: Optional[EncryptionSupport] = None
    multicastSupport: Optional[MulticastSupport] = None
    propagationDefaultRouteTableId: Optional[str] = None
    securityGroupReferencingSupport: Optional[SecurityGroupReferencingSupport] = None
    transitGatewayCidrBlocks: List[str] = field(default_factory=list)
    vpnEcmpSupport: Optional[VpnEcmpSupport] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.amazonSideAsn is not None:
            result["AmazonSideAsn"] = self.amazonSideAsn
        if self.associationDefaultRouteTableId is not None:
            result["AssociationDefaultRouteTableId"] = self.associationDefaultRouteTableId
        if self.autoAcceptSharedAttachments is not None:
            result["AutoAcceptSharedAttachments"] = self.autoAcceptSharedAttachments.value
        if self.defaultRouteTableAssociation is not None:
            result["DefaultRouteTableAssociation"] = self.defaultRouteTableAssociation.value
        if self.defaultRouteTablePropagation is not None:
            result["DefaultRouteTablePropagation"] = self.defaultRouteTablePropagation.value
        if self.dnsSupport is not None:
            result["DnsSupport"] = self.dnsSupport.value
        if self.encryptionSupport is not None:
            result["EncryptionSupport"] = self.encryptionSupport.to_dict()
        if self.multicastSupport is not None:
            result["MulticastSupport"] = self.multicastSupport.value
        if self.propagationDefaultRouteTableId is not None:
            result["PropagationDefaultRouteTableId"] = self.propagationDefaultRouteTableId
        if self.securityGroupReferencingSupport is not None:
            result["SecurityGroupReferencingSupport"] = self.securityGroupReferencingSupport.value
        if self.transitGatewayCidrBlocks:
            result["TransitGatewayCidrBlocks"] = self.transitGatewayCidrBlocks
        if self.vpnEcmpSupport is not None:
            result["VpnEcmpSupport"] = self.vpnEcmpSupport.value
        return result


@dataclass
class TagSpecification:
    ResourceType: Optional[ResourceType] = None
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType.value if self.ResourceType else None,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class TransitGateway:
    creationTime: Optional[datetime] = None
    description: Optional[str] = None
    options: Optional[TransitGatewayOptions] = None
    ownerId: Optional[str] = None
    state: Optional[TransitGatewayState] = None
    tagSet: List[Tag] = field(default_factory=list)
    transitGatewayArn: Optional[str] = None
    transitGatewayId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CreationTime": self.creationTime.isoformat() if self.creationTime else None,
            "Description": self.description,
            "Options": self.options.to_dict() if self.options else None,
            "OwnerId": self.ownerId,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tagSet],
            "TransitGatewayArn": self.transitGatewayArn,
            "TransitGatewayId": self.transitGatewayId,
        }


@dataclass
class CreateTransitGatewayVpcAttachmentRequestOptions:
    ApplianceModeSupport: Optional[ApplianceModeSupport] = None
    DnsSupport: Optional[DnsSupport] = None
    Ipv6Support: Optional[Ipv6Support] = None
    SecurityGroupReferencingSupport: Optional[SecurityGroupReferencingSupport] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.ApplianceModeSupport is not None:
            result["ApplianceModeSupport"] = self.ApplianceModeSupport.value
        if self.DnsSupport is not None:
            result["DnsSupport"] = self.DnsSupport.value
        if self.Ipv6Support is not None:
            result["Ipv6Support"] = self.Ipv6Support.value
        if self.SecurityGroupReferencingSupport is not None:
            result["SecurityGroupReferencingSupport"] = self.SecurityGroupReferencingSupport.value
        return result


@dataclass
class ModifyTransitGatewayOptions:
    AddTransitGatewayCidrBlocks: List[str] = field(default_factory=list)
    AmazonSideAsn: Optional[int] = None
    AssociationDefaultRouteTableId: Optional[str] = None
    AutoAcceptSharedAttachments: Optional[AutoAcceptSharedAttachments] = None
    DefaultRouteTableAssociation: Optional[DefaultRouteTableAssociation] = None
    DefaultRouteTablePropagation: Optional[DefaultRouteTablePropagation] = None
    DnsSupport: Optional[DnsSupport] = None
    EncryptionSupport: Optional[str] = None  # enable | disable as string
    PropagationDefaultRouteTableId: Optional[str] = None
    RemoveTransitGatewayCidrBlocks: List[str] = field(default_factory=list)
    SecurityGroupReferencingSupport: Optional[SecurityGroupReferencingSupport] = None
    VpnEcmpSupport: Optional[VpnEcmpSupport] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.AddTransitGatewayCidrBlocks:
            result["AddTransitGatewayCidrBlocks"] = self.AddTransitGatewayCidrBlocks
        if self.AmazonSideAsn is not None:
            result["AmazonSideAsn"] = self.AmazonSideAsn
        if self.AssociationDefaultRouteTableId is not None:
            result["AssociationDefaultRouteTableId"] = self.AssociationDefaultRouteTableId
        if self.AutoAcceptSharedAttachments is not None:
            result["AutoAcceptSharedAttachments"] = self.AutoAcceptSharedAttachments.value
        if self.DefaultRouteTableAssociation is not None:
            result["DefaultRouteTableAssociation"] = self.DefaultRouteTableAssociation.value
        if self.DefaultRouteTablePropagation is not None:
            result["DefaultRouteTablePropagation"] = self.DefaultRouteTablePropagation.value
        if self.DnsSupport is not None:
            result["DnsSupport"] = self.DnsSupport.value
        if self.EncryptionSupport is not None:
            result["EncryptionSupport"] = self.EncryptionSupport
        if self.PropagationDefaultRouteTableId is not None:
            result["PropagationDefaultRouteTableId"] = self.PropagationDefaultRouteTableId
        if self.RemoveTransitGatewayCidrBlocks:
            result["RemoveTransitGatewayCidrBlocks"] = self.RemoveTransitGatewayCidrBlocks
        if self.SecurityGroupReferencingSupport is not None:
            result["SecurityGroupReferencingSupport"] = self.SecurityGroupReferencingSupport.value
        if self.VpnEcmpSupport is not None:
            result["VpnEcmpSupport"] = self.VpnEcmpSupport.value
        return result


class TransitGatewaysBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)

    def accept_transit_gateway_vpc_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            raise Exception("Missing required parameter TransitGatewayAttachmentId")

        attachment = self.state.transit_gateway_vpc_attachments.get(attachment_id)
        if not attachment:
            raise Exception(f"TransitGatewayVpcAttachment {attachment_id} does not exist")

        # Validate DryRun if present
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Only attachments in pendingAcceptance state can be accepted
        if attachment.state != VpcAttachmentState.PENDING_ACCEPTANCE:
            raise Exception(f"TransitGatewayVpcAttachment {attachment_id} is not in pendingAcceptance state")

        # Change state to available
        attachment.state = VpcAttachmentState.AVAILABLE

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayVpcAttachment": attachment.to_dict(),
        }


    def create_transit_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        description = params.get("Description")
        options_param = params.get("Options", {})
        tag_specifications = params.get("TagSpecification.N", [])

        # Parse options
        options = TransitGatewayRequestOptions(
            amazonSideAsn=options_param.get("AmazonSideAsn"),
            autoAcceptSharedAttachments=AutoAcceptSharedAttachments(options_param.get("AutoAcceptSharedAttachments")) if options_param.get("AutoAcceptSharedAttachments") else None,
            defaultRouteTableAssociation=DefaultRouteTableAssociation(options_param.get("DefaultRouteTableAssociation")) if options_param.get("DefaultRouteTableAssociation") else None,
            defaultRouteTablePropagation=DefaultRouteTablePropagation(options_param.get("DefaultRouteTablePropagation")) if options_param.get("DefaultRouteTablePropagation") else None,
            dnsSupport=DnsSupport(options_param.get("DnsSupport")) if options_param.get("DnsSupport") else None,
            multicastSupport=MulticastSupport(options_param.get("MulticastSupport")) if options_param.get("MulticastSupport") else None,
            securityGroupReferencingSupport=SecurityGroupReferencingSupport(options_param.get("SecurityGroupReferencingSupport")) if options_param.get("SecurityGroupReferencingSupport") else None,
            transitGatewayCidrBlocks=options_param.get("TransitGatewayCidrBlocks", []),
            vpnEcmpSupport=VpnEcmpSupport(options_param.get("VpnEcmpSupport")) if options_param.get("VpnEcmpSupport") else None,
        )

        # Generate transit gateway id and arn
        transit_gateway_id = self.generate_unique_id(prefix="tgw-")
        transit_gateway_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:transit-gateway/{transit_gateway_id}"

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") and tag_spec.get("ResourceType") != ResourceType.TRANSIT_GATEWAY:
                continue
            for tag_dict in tag_spec.get("Tags", []):
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key and not key.lower().startswith("aws:"):
                    tags.append(Tag(Key=key, Value=value))

        transit_gateway = TransitGateway(
            creationTime=datetime.utcnow(),
            description=description,
            options=TransitGatewayOptions(
                amazonSideAsn=options.amazonSideAsn,
                associationDefaultRouteTableId=None,
                autoAcceptSharedAttachments=options.autoAcceptSharedAttachments,
                defaultRouteTableAssociation=options.defaultRouteTableAssociation,
                defaultRouteTablePropagation=options.defaultRouteTablePropagation,
                dnsSupport=options.dnsSupport,
                encryptionSupport=None,
                multicastSupport=options.multicastSupport,
                propagationDefaultRouteTableId=None,
                securityGroupReferencingSupport=options.securityGroupReferencingSupport,
                transitGatewayCidrBlocks=options.transitGatewayCidrBlocks,
                vpnEcmpSupport=options.vpnEcmpSupport,
            ),
            ownerId=self.get_owner_id(),
            state=TransitGatewayState.AVAILABLE,
            tagSet=tags,
            transitGatewayArn=transit_gateway_arn,
            transitGatewayId=transit_gateway_id,
        )

        self.state.transit_gateways[transit_gateway_id] = transit_gateway

        return {
            "requestId": self.generate_request_id(),
            "transitGateway": transit_gateway.to_dict(),
        }


    def create_transit_gateway_vpc_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        transit_gateway_id = params.get("TransitGatewayId")
        vpc_id = params.get("VpcId")
        subnet_ids = params.get("SubnetIds.N")
        if not transit_gateway_id:
            raise Exception("Missing required parameter TransitGatewayId")
        if not vpc_id:
            raise Exception("Missing required parameter VpcId")
        if not subnet_ids or not isinstance(subnet_ids, list) or len(subnet_ids) == 0:
            raise Exception("Missing or invalid required parameter SubnetIds.N")

        # Validate DryRun if present
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Validate transit gateway exists
        transit_gateway = self.state.transit_gateways.get(transit_gateway_id)
        if not transit_gateway:
            raise Exception(f"TransitGateway {transit_gateway_id} does not exist")

        # Validate VPC exists
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise Exception(f"VPC {vpc_id} does not exist")

        # Validate subnets exist and belong to the VPC
        for subnet_id in subnet_ids:
            subnet = self.state.subnets.get(subnet_id)
            if not subnet:
                raise Exception(f"Subnet {subnet_id} does not exist")
            if subnet.vpcId != vpc_id:
                raise Exception(f"Subnet {subnet_id} does not belong to VPC {vpc_id}")

        options_param = params.get("Options", {})
        tag_specifications = params.get("TagSpecifications.N", [])

        options = TransitGatewayVpcAttachmentOptions(
            applianceModeSupport=ApplianceModeSupport(options_param.get("ApplianceModeSupport")) if options_param.get("ApplianceModeSupport") else None,
            dnsSupport=DnsSupport(options_param.get("DnsSupport")) if options_param.get("DnsSupport") else None,
            ipv6Support=Ipv6Support(options_param.get("Ipv6Support")) if options_param.get("Ipv6Support") else None,
            securityGroupReferencingSupport=SecurityGroupReferencingSupport(options_param.get("SecurityGroupReferencingSupport")) if options_param.get("SecurityGroupReferencingSupport") else None,
        )

        # Generate attachment id
        attachment_id = self.generate_unique_id(prefix="tgw-attach-")

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") and tag_spec.get("ResourceType") != ResourceType.TRANSIT_GATEWAY_ATTACHMENT:
                continue
            for tag_dict in tag_spec.get("Tags", []):
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key and not key.lower().startswith("aws:"):
                    tags.append(Tag(Key=key, Value=value))

        # Create attachment with state pending
        attachment = TransitGatewayVpcAttachment(
            creationTime=datetime.utcnow(),
            options=options,
            state=VpcAttachmentState.PENDING,
            subnetIds=subnet_ids,
            tagSet=tags,
            transitGatewayAttachmentId=attachment_id,
            transitGatewayId=transit_gateway_id,
            vpcId=vpc_id,
            vpcOwnerId=vpc.ownerId if vpc else None,
        )

        self.state.transit_gateway_vpc_attachments[attachment_id] = attachment

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayVpcAttachment": attachment.to_dict(),
        }


    def delete_transit_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_id = params.get("TransitGatewayId")
        if not transit_gateway_id:
            raise Exception("Missing required parameter TransitGatewayId")

        # Validate DryRun if present
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        transit_gateway = self.state.transit_gateways.get(transit_gateway_id)
        if not transit_gateway:
            raise Exception(f"TransitGateway {transit_gateway_id} does not exist")

        # Mark transit gateway as deleted
        transit_gateway.state = TransitGatewayState.DELETED

        # Optionally, could remove from state, but AWS keeps deleted resources for some time
        # self.state.transit_gateways.pop(transit_gateway_id)

        return {
            "requestId": self.generate_request_id(),
            "transitGateway": transit_gateway.to_dict(),
        }


    def delete_transit_gateway_vpc_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            raise Exception("Missing required parameter TransitGatewayAttachmentId")

        # Validate DryRun if present
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        attachment = self.state.transit_gateway_vpc_attachments.get(attachment_id)
        if not attachment:
            raise Exception(f"TransitGatewayVpcAttachment {attachment_id} does not exist")

        # Mark attachment as deleted
        attachment.state = VpcAttachmentState.DELETED

        # Optionally, could remove from state, but AWS keeps deleted resources for some time
        # self.state.transit_gateway_vpc_attachments.pop(attachment_id)

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayVpcAttachment": attachment.to_dict(),
        }

    def describe_transit_gateway_attachments(self, params: dict) -> dict:
        # Validate DryRun
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For DryRun, check permissions (emulated as always allowed here)
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Extract filters
        filters = params.get("Filter", [])
        # Filters can be passed as Filter.N.Name and Filter.N.Value or as a list of dicts
        # Normalize filters to list of dicts with keys 'Name' and 'Values'
        normalized_filters = []
        if isinstance(filters, dict):
            # If filters is a dict with keys like '1': {...}, convert to list
            for key in sorted(filters.keys()):
                f = filters[key]
                if isinstance(f, dict):
                    normalized_filters.append(f)
        elif isinstance(filters, list):
            normalized_filters = filters

        # Extract TransitGatewayAttachmentIds.N
        attachment_ids = params.get("TransitGatewayAttachmentIds", [])

        # MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")

        # Collect all attachments from state
        all_attachments = list(self.state.transit_gateway_attachments.values()) if hasattr(self.state, "transit_gateway_attachments") else []

        # Filter by attachment IDs if provided
        if attachment_ids:
            all_attachments = [att for att in all_attachments if att.transitGatewayAttachmentId in attachment_ids]

        # Helper function to check if attachment matches filters
        def matches_filters(attachment):
            for f in normalized_filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue
                # Map filter names to attachment attributes or nested attributes
                # Possible filter names:
                # association.state, association.transit-gateway-route-table-id, resource-id, resource-owner-id,
                # resource-type, state, transit-gateway-attachment-id, transit-gateway-id, transit-gateway-owner-id
                if name == "association.state":
                    assoc = getattr(attachment, "association", None)
                    assoc_state = getattr(assoc, "state", None) if assoc else None
                    if assoc_state is None or assoc_state.value not in values:
                        return False
                elif name == "association.transit-gateway-route-table-id":
                    assoc = getattr(attachment, "association", None)
                    assoc_tgw_rt_id = getattr(assoc, "transitGatewayRouteTableId", None) if assoc else None
                    if assoc_tgw_rt_id not in values:
                        return False
                elif name == "resource-id":
                    if attachment.resourceId not in values:
                        return False
                elif name == "resource-owner-id":
                    if attachment.resourceOwnerId not in values:
                        return False
                elif name == "resource-type":
                    if attachment.resourceType not in values:
                        return False
                elif name == "state":
                    if attachment.state is None or attachment.state.value not in values:
                        return False
                elif name == "transit-gateway-attachment-id":
                    if attachment.transitGatewayAttachmentId not in values:
                        return False
                elif name == "transit-gateway-id":
                    if attachment.transitGatewayId not in values:
                        return False
                elif name == "transit-gateway-owner-id":
                    if attachment.transitGatewayOwnerId not in values:
                        return False
                else:
                    # Unknown filter name, ignore or treat as no match
                    return False
            return True

        filtered_attachments = [att for att in all_attachments if matches_filters(att)]

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else None
        paged_attachments = filtered_attachments[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index is not None and end_index < len(filtered_attachments):
            new_next_token = str(end_index)

        # Convert attachments to dicts
        attachments_list = [att.to_dict() for att in paged_attachments]

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayAttachments": attachments_list,
            "nextToken": new_next_token,
        }
        return response


    def describe_transit_gateways(self, params: dict) -> dict:
        # Validate DryRun
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For DryRun, check permissions (emulated as always allowed here)
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Extract filters
        filters = params.get("Filter", [])
        normalized_filters = []
        if isinstance(filters, dict):
            for key in sorted(filters.keys()):
                f = filters[key]
                if isinstance(f, dict):
                    normalized_filters.append(f)
        elif isinstance(filters, list):
            normalized_filters = filters

        # Extract TransitGatewayIds.N
        tgw_ids = params.get("TransitGatewayIds", [])

        # MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")

        # Collect all transit gateways from state
        all_tgws = list(self.state.transit_gateways.values())

        # Filter by IDs if provided
        if tgw_ids:
            all_tgws = [tgw for tgw in all_tgws if tgw.transitGatewayId in tgw_ids]

        # Helper function to check if tgw matches filters
        def matches_filters(tgw):
            for f in normalized_filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue
                # Filter names and mapping:
                # options.propagation-default-route-table-id
                # options.amazon-side-asn
                # options.association-default-route-table-id
                # options.auto-accept-shared-attachments
                # options.default-route-table-association
                # options.default-route-table-propagation
                # options.dns-support
                # options.vpn-ecmp-support
                # owner-id
                # state
                # transit-gateway-id
                # tag-key (key/value combination)
                # tag:<key> (AWS style)
                # For tag-key, the filter name is "tag-key" and values are keys
                # For tag:<key>, filter name is "tag:<key>" and values are values

                if name.startswith("options."):
                    option_name = name[len("options."):]
                    option_value = None
                    if tgw.options:
                        # Some options are strings, some are objects
                        if option_name == "amazon-side-asn":
                            option_value = str(tgw.options.amazonSideAsn) if tgw.options.amazonSideAsn is not None else None
                        elif option_name == "auto-accept-shared-attachments":
                            option_value = tgw.options.autoAcceptSharedAttachments.value if tgw.options.autoAcceptSharedAttachments else None
                        elif option_name == "association-default-route-table-id":
                            option_value = tgw.options.associationDefaultRouteTableId
                        elif option_name == "default-route-table-association":
                            option_value = tgw.options.defaultRouteTableAssociation.value if tgw.options.defaultRouteTableAssociation else None
                        elif option_name == "default-route-table-propagation":
                            option_value = tgw.options.defaultRouteTablePropagation.value if tgw.options.defaultRouteTablePropagation else None
                        elif option_name == "dns-support":
                            option_value = tgw.options.dnsSupport.value if tgw.options.dnsSupport else None
                        elif option_name == "vpn-ecmp-support":
                            option_value = tgw.options.vpnEcmpSupport.value if tgw.options.vpnEcmpSupport else None
                        elif option_name == "propagation-default-route-table-id":
                            option_value = tgw.options.propagationDefaultRouteTableId
                        elif option_name == "security-group-referencing-support":
                            option_value = tgw.options.securityGroupReferencingSupport.value if tgw.options.securityGroupReferencingSupport else None
                        elif option_name == "multicast-support":
                            option_value = tgw.options.multicastSupport.value if tgw.options.multicastSupport else None
                        elif option_name == "encryption-support":
                            if tgw.options.encryptionSupport:
                                option_value = tgw.options.encryptionSupport.encryptionState.value if tgw.options.encryptionSupport.encryptionState else None
                            else:
                                option_value = None
                        else:
                            option_value = None
                    if option_value is None or option_value not in values:
                        return False
                elif name == "owner-id":
                    if tgw.ownerId not in values:
                        return False
                elif name == "state":
                    if tgw.state is None or tgw.state.value not in values:
                        return False
                elif name == "transit-gateway-id":
                    if tgw.transitGatewayId not in values:
                        return False
                elif name == "tag-key":
                    # Check if any tag key matches any of the values
                    tag_keys = [tag.Key for tag in tgw.tagSet]
                    if not any(v in tag_keys for v in values):
                        return False
                elif name.startswith("tag:"):
                    # Filter by tag key and value
                    tag_key = name[4:]
                    # Check if any tag with key=tag_key has value in values
                    found = False
                    for tag in tgw.tagSet:
                        if tag.Key == tag_key and tag.Value in values:
                            found = True
                            break
                    if not found:
                        return False
                else:
                    # Unknown filter name, treat as no match
                    return False
            return True

        filtered_tgws = [tgw for tgw in all_tgws if matches_filters(tgw)]

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else None
        paged_tgws = filtered_tgws[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index is not None and end_index < len(filtered_tgws):
            new_next_token = str(end_index)

        # Convert to dicts
        tgw_list = [tgw.to_dict() for tgw in paged_tgws]

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewaySet": tgw_list,
            "nextToken": new_next_token,
        }
        return response


    def describe_transit_gateway_vpc_attachments(self, params: dict) -> dict:
        # Validate DryRun
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For DryRun, check permissions (emulated as always allowed here)
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Extract filters
        filters = params.get("Filter", [])
        normalized_filters = []
        if isinstance(filters, dict):
            for key in sorted(filters.keys()):
                f = filters[key]
                if isinstance(f, dict):
                    normalized_filters.append(f)
        elif isinstance(filters, list):
            normalized_filters = filters

        # Extract TransitGatewayAttachmentIds.N
        attachment_ids = params.get("TransitGatewayAttachmentIds", [])

        # MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    max_results = None
            except Exception:
                max_results = None
        next_token = params.get("NextToken")

        # Collect all VPC attachments from state
        all_attachments = list(self.state.transit_gateway_vpc_attachments.values()) if hasattr(self.state, "transit_gateway_vpc_attachments") else []

        # Filter by attachment IDs if provided
        if attachment_ids:
            all_attachments = [att for att in all_attachments if att.transitGatewayAttachmentId in attachment_ids]

        # Helper function to check if attachment matches filters
        def matches_filters(attachment):
            for f in normalized_filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue
                # Possible filter names:
                # state, transit-gateway-attachment-id, transit-gateway-id, vpc-id
                if name == "state":
                    if attachment.state is None or attachment.state.value not in values:
                        return False
                elif name == "transit-gateway-attachment-id":
                    if attachment.transitGatewayAttachmentId not in values:
                        return False
                elif name == "transit-gateway-id":
                    if attachment.transitGatewayId not in values:
                        return False
                elif name == "vpc-id":
                    if attachment.vpcId not in values:
                        return False
                else:
                    # Unknown filter name, treat as no match
                    return False
            return True

        filtered_attachments = [att for att in all_attachments if matches_filters(att)]

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else None
        paged_attachments = filtered_attachments[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index is not None and end_index < len(filtered_attachments):
            new_next_token = str(end_index)

        # Convert attachments to dicts
        attachments_list = [att.to_dict() for att in paged_attachments]

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayVpcAttachments": attachments_list,
            "nextToken": new_next_token,
        }
        return response


    def modify_transit_gateway(self, params: dict) -> dict:
        # Validate DryRun
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For DryRun, check permissions (emulated as always allowed here)
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        transit_gateway_id = params.get("TransitGatewayId")
        if not transit_gateway_id:
            raise Exception("Missing required parameter TransitGatewayId")

        transit_gateway = self.state.transit_gateways.get(transit_gateway_id)
        if not transit_gateway:
            raise Exception(f"TransitGateway {transit_gateway_id} not found")

        description = params.get("Description")
        options_param = params.get("Options")

        # Update description if provided
        if description is not None:
            transit_gateway.description = description

        # Update options if provided
        if options_param:
            # options_param is a dict representing ModifyTransitGatewayOptions
            # Update fields accordingly
            # AddTransitGatewayCidrBlocks (list of strings)
            add_cidrs = options_param.get("AddTransitGatewayCidrBlocks", [])
            remove_cidrs = options_param.get("RemoveTransitGatewayCidrBlocks", [])

            # Update amazonSideAsn
            amazon_side_asn = options_param.get("AmazonSideAsn")
            if amazon_side_asn is not None:
                transit_gateway.options.amazonSideAsn = amazon_side_asn

            # Update associationDefaultRouteTableId
            assoc_default_rt_id = options_param.get("AssociationDefaultRouteTableId")
            if assoc_default_rt_id is not None:
                transit_gateway.options.associationDefaultRouteTableId = assoc_default_rt_id

            # Update autoAcceptSharedAttachments
            auto_accept = options_param.get("AutoAcceptSharedAttachments")
            if auto_accept is not None:
                # auto_accept is string "enable" or "disable"
                from enum import Enum
                # We assume AutoAcceptSharedAttachments enum exists
                transit_gateway.options.autoAcceptSharedAttachments = AutoAcceptSharedAttachments(auto_accept)

            # Update defaultRouteTableAssociation
            default_rt_assoc = options_param.get("DefaultRouteTableAssociation")
            if default_rt_assoc is not None:
                transit_gateway.options.defaultRouteTableAssociation = DefaultRouteTableAssociation(default_rt_assoc)

            # Update defaultRouteTablePropagation
            default_rt_prop = options_param.get("DefaultRouteTablePropagation")
            if default_rt_prop is not None:
                transit_gateway.options.defaultRouteTablePropagation = DefaultRouteTablePropagation(default_rt_prop)

            # Update dnsSupport
            dns_support = options_param.get("DnsSupport")
            if dns_support is not None:
                transit_gateway.options.dnsSupport = DnsSupport(dns_support)

            # Update encryptionSupport
            encryption_support = options_param.get("EncryptionSupport")
            if encryption_support is not None:
                # encryptionSupport is string "enable" or "disable"
                # We create or update EncryptionSupport object
                if transit_gateway.options.encryptionSupport is None:
                    transit_gateway.options.encryptionSupport = EncryptionSupport()
                # Map string to EncryptionState enum
                transit_gateway.options.encryptionSupport.encryptionState = EncryptionState(encryption_support)
                # No stateMessage provided here

            # Update propagationDefaultRouteTableId
            propagation_default_rt_id = options_param.get("PropagationDefaultRouteTableId")
            if propagation_default_rt_id is not None:
                transit_gateway.options.propagationDefaultRouteTableId = propagation_default_rt_id

            # Update securityGroupReferencingSupport
            sg_ref_support = options_param.get("SecurityGroupReferencingSupport")
            if sg_ref_support is not None:
                transit_gateway.options.securityGroupReferencingSupport = SecurityGroupReferencingSupport(sg_ref_support)

            # Update vpnEcmpSupport
            vpn_ecmp_support = options_param.get("VpnEcmpSupport")
            if vpn_ecmp_support is not None:
                transit_gateway.options.vpnEcmpSupport = VpnEcmpSupport(vpn_ecmp_support)

            # Update transitGatewayCidrBlocks: add and remove
            # Add CIDRs
            for cidr in add_cidrs:
                if cidr not in transit_gateway.options.transitGatewayCidrBlocks:
                    transit_gateway.options.transitGatewayCidrBlocks.append(cidr)
            # Remove CIDRs
            for cidr in remove_cidrs:
                if cidr in transit_gateway.options.transitGatewayCidrBlocks:
                    transit_gateway.options.transitGatewayCidrBlocks.remove(cidr)

        return {
            "requestId": self.generate_request_id(),
            "transitGateway": transit_gateway.to_dict(),
        }

    def modify_transit_gateway_vpc_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            raise Exception("Missing required parameter TransitGatewayAttachmentId")

        # Validate DryRun if present
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        attachment = self.state.transit_gateway_vpc_attachments.get(attachment_id)
        if not attachment:
            raise Exception(f"TransitGatewayVpcAttachment {attachment_id} does not exist")

        # Parse AddSubnetIds and RemoveSubnetIds
        add_subnet_ids = []
        remove_subnet_ids = []
        for key, value in params.items():
            if key.startswith("AddSubnetIds."):
                add_subnet_ids.append(value)
            elif key.startswith("RemoveSubnetIds."):
                remove_subnet_ids.append(value)

        # Add subnets
        for subnet_id in add_subnet_ids:
            if subnet_id not in attachment.subnetIds:
                attachment.subnetIds.append(subnet_id)

        # Remove subnets
        for subnet_id in remove_subnet_ids:
            if subnet_id in attachment.subnetIds:
                attachment.subnetIds.remove(subnet_id)

        # Update options if provided
        options_param = params.get("Options", {})
        if options_param:
            if options_param.get("ApplianceModeSupport"):
                attachment.options.applianceModeSupport = ApplianceModeSupport(options_param.get("ApplianceModeSupport"))
            if options_param.get("DnsSupport"):
                attachment.options.dnsSupport = DnsSupport(options_param.get("DnsSupport"))
            if options_param.get("Ipv6Support"):
                attachment.options.ipv6Support = Ipv6Support(options_param.get("Ipv6Support"))
            if options_param.get("SecurityGroupReferencingSupport"):
                attachment.options.securityGroupReferencingSupport = SecurityGroupReferencingSupport(options_param.get("SecurityGroupReferencingSupport"))

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayVpcAttachment": attachment.to_dict(),
        }

    def reject_transit_gateway_vpc_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        dry_run = params.get("DryRun", False)

        if not attachment_id:
            raise Exception("Missing required parameter TransitGatewayAttachmentId")

        # DryRun check
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        attachment = self.state.transit_gateway_vpc_attachments.get(attachment_id)
        if not attachment:
            raise Exception(f"InvalidTransitGatewayAttachmentID.NotFound: The attachment ID '{attachment_id}' does not exist")

        # Only attachments in pendingAcceptance state can be rejected
        if attachment.state != VpcAttachmentState.PENDING_ACCEPTANCE:
            raise Exception(f"IncorrectState: The attachment {attachment_id} is not in pendingAcceptance state")

        # Change state to rejected
        attachment.state = VpcAttachmentState.REJECTED

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayVpcAttachment": attachment.to_dict(),
        }

    

from emulator_core.gateway.base import BaseGateway

class TransitgatewaysGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptTransitGatewayVpcAttachment", self.accept_transit_gateway_vpc_attachment)
        self.register_action("CreateTransitGateway", self.create_transit_gateway)
        self.register_action("CreateTransitGatewayVpcAttachment", self.create_transit_gateway_vpc_attachment)
        self.register_action("DeleteTransitGateway", self.delete_transit_gateway)
        self.register_action("DeleteTransitGatewayVpcAttachment", self.delete_transit_gateway_vpc_attachment)
        self.register_action("DescribeTransitGatewayAttachments", self.describe_transit_gateway_attachments)
        self.register_action("DescribeTransitGateways", self.describe_transit_gateways)
        self.register_action("DescribeTransitGatewayVpcAttachments", self.describe_transit_gateway_vpc_attachments)
        self.register_action("ModifyTransitGateway", self.modify_transit_gateway)
        self.register_action("ModifyTransitGatewayVpcAttachment", self.modify_transit_gateway_vpc_attachment)
        self.register_action("RejectTransitGatewayVpcAttachment", self.reject_transit_gateway_vpc_attachment)

    def accept_transit_gateway_vpc_attachment(self, params):
        return self.backend.accept_transit_gateway_vpc_attachment(params)

    def create_transit_gateway(self, params):
        return self.backend.create_transit_gateway(params)

    def create_transit_gateway_vpc_attachment(self, params):
        return self.backend.create_transit_gateway_vpc_attachment(params)

    def delete_transit_gateway(self, params):
        return self.backend.delete_transit_gateway(params)

    def delete_transit_gateway_vpc_attachment(self, params):
        return self.backend.delete_transit_gateway_vpc_attachment(params)

    def describe_transit_gateway_attachments(self, params):
        return self.backend.describe_transit_gateway_attachments(params)

    def describe_transit_gateways(self, params):
        return self.backend.describe_transit_gateways(params)

    def describe_transit_gateway_vpc_attachments(self, params):
        return self.backend.describe_transit_gateway_vpc_attachments(params)

    def modify_transit_gateway(self, params):
        return self.backend.modify_transit_gateway(params)

    def modify_transit_gateway_vpc_attachment(self, params):
        return self.backend.modify_transit_gateway_vpc_attachment(params)

    def reject_transit_gateway_vpc_attachment(self, params):
        return self.backend.reject_transit_gateway_vpc_attachment(params)
