from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


# Enums for fixed value sets
class NetworkInterfaceAttachmentStatus(str, Enum):
    ATTACHING = "attaching"
    ATTACHED = "attached"
    DETACHING = "detaching"
    DETACHED = "detached"


class NetworkInterfaceStatus(str, Enum):
    AVAILABLE = "available"
    ASSOCIATED = "associated"
    ATTACHING = "attaching"
    IN_USE = "in-use"
    DETACHING = "detaching"


class NetworkInterfacePermissionType(str, Enum):
    INSTANCE_ATTACH = "INSTANCE-ATTACH"
    EIP_ASSOCIATE = "EIP-ASSOCIATE"


class NetworkInterfacePermissionStateCode(str, Enum):
    PENDING = "pending"
    GRANTED = "granted"
    REVOKING = "revoking"
    REVOKED = "revoked"


class InterfaceType(str, Enum):
    API_GATEWAY_MANAGED = "api_gateway_managed"
    AWS_CODESTAR_CONNECTIONS_MANAGED = "aws_codestar_connections_managed"
    BRANCH = "branch"
    EC2_INSTANCE_CONNECT_ENDPOINT = "ec2_instance_connect_endpoint"
    EFA = "efa"
    EFA_ONLY = "efa-only"
    EFS = "efs"
    EVS = "evs"
    GATEWAY_LOAD_BALANCER = "gateway_load_balancer"
    GATEWAY_LOAD_BALANCER_ENDPOINT = "gateway_load_balancer_endpoint"
    GLOBAL_ACCELERATOR_MANAGED = "global_accelerator_managed"
    INTERFACE = "interface"
    IOT_RULES_MANAGED = "iot_rules_managed"
    LAMBDA = "lambda"
    LOAD_BALANCER = "load_balancer"
    NAT_GATEWAY = "nat_gateway"
    NETWORK_LOAD_BALANCER = "network_load_balancer"
    QUICKSIGHT = "quicksight"
    TRANSIT_GATEWAY = "transit_gateway"
    TRUNK = "trunk"
    VPC_ENDPOINT = "vpc_endpoint"
    # For CreateNetworkInterface InterfaceType valid values also include "efa-only" and "trunk"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class Filter:
    Name: str
    Values: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"Name": self.Name, "Values": self.Values}


@dataclass
class AttributeValue:
    Value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class AttributeBooleanValue:
    Value: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Value": self.Value}


@dataclass
class GroupIdentifier:
    GroupId: Optional[str] = None
    GroupName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"GroupId": self.GroupId, "GroupName": self.GroupName}


@dataclass
class NetworkInterfaceAssociation:
    allocationId: Optional[str] = None
    associationId: Optional[str] = None
    carrierIp: Optional[str] = None
    customerOwnedIp: Optional[str] = None
    ipOwnerId: Optional[str] = None
    publicDnsName: Optional[str] = None
    publicIp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationId": self.allocationId,
            "AssociationId": self.associationId,
            "CarrierIp": self.carrierIp,
            "CustomerOwnedIp": self.customerOwnedIp,
            "IpOwnerId": self.ipOwnerId,
            "PublicDnsName": self.publicDnsName,
            "PublicIp": self.publicIp,
        }


@dataclass
class AttachmentEnaSrdUdpSpecification:
    enaSrdUdpEnabled: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"EnaSrdUdpEnabled": self.enaSrdUdpEnabled}


@dataclass
class AttachmentEnaSrdSpecification:
    enaSrdEnabled: Optional[bool] = None
    enaSrdUdpSpecification: Optional[AttachmentEnaSrdUdpSpecification] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EnaSrdEnabled": self.enaSrdEnabled,
            "EnaSrdUdpSpecification": self.enaSrdUdpSpecification.to_dict()
            if self.enaSrdUdpSpecification
            else None,
        }


@dataclass
class NetworkInterfaceAttachment:
    attachmentId: Optional[str] = None
    attachTime: Optional[datetime] = None
    deleteOnTermination: Optional[bool] = None
    deviceIndex: Optional[int] = None
    enaQueueCount: Optional[int] = None
    enaSrdSpecification: Optional[AttachmentEnaSrdSpecification] = None
    instanceId: Optional[str] = None
    instanceOwnerId: Optional[str] = None
    networkCardIndex: Optional[int] = None
    status: Optional[NetworkInterfaceAttachmentStatus] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AttachmentId": self.attachmentId,
            "AttachTime": self.attachTime.isoformat() if self.attachTime else None,
            "DeleteOnTermination": self.deleteOnTermination,
            "DeviceIndex": self.deviceIndex,
            "EnaQueueCount": self.enaQueueCount,
            "EnaSrdSpecification": self.enaSrdSpecification.to_dict()
            if self.enaSrdSpecification
            else None,
            "InstanceId": self.instanceId,
            "InstanceOwnerId": self.instanceOwnerId,
            "NetworkCardIndex": self.networkCardIndex,
            "Status": self.status.value if self.status else None,
        }


@dataclass
class NetworkInterfaceIpv6Address:
    ipv6Address: Optional[str] = None
    isPrimaryIpv6: Optional[bool] = None
    publicIpv6DnsName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Ipv6Address": self.ipv6Address,
            "IsPrimaryIpv6": self.isPrimaryIpv6,
            "PublicIpv6DnsName": self.publicIpv6DnsName,
        }


@dataclass
class Ipv4PrefixSpecification:
    ipv4Prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Ipv4Prefix": self.ipv4Prefix}


@dataclass
class Ipv4PrefixSpecificationRequest:
    ipv4Prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Ipv4Prefix": self.ipv4Prefix}


@dataclass
class Ipv6PrefixSpecification:
    ipv6Prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Ipv6Prefix": self.ipv6Prefix}


@dataclass
class Ipv6PrefixSpecificationRequest:
    ipv6Prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Ipv6Prefix": self.ipv6Prefix}


@dataclass
class InstanceIpv6Address:
    Ipv6Address: Optional[str] = None
    IsPrimaryIpv6: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Ipv6Address": self.Ipv6Address,
            "IsPrimaryIpv6": self.IsPrimaryIpv6,
        }


@dataclass
class PrivateIpAddressSpecification:
    Primary: Optional[bool] = None
    PrivateIpAddress: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Primary": self.Primary,
            "PrivateIpAddress": self.PrivateIpAddress,
        }


@dataclass
class NetworkInterfacePrivateIpAddress:
    association: Optional[NetworkInterfaceAssociation] = None
    primary: Optional[bool] = None
    privateDnsName: Optional[str] = None
    privateIpAddress: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Association": self.association.to_dict() if self.association else None,
            "Primary": self.primary,
            "PrivateDnsName": self.privateDnsName,
            "PrivateIpAddress": self.privateIpAddress,
        }


@dataclass
class PublicIpDnsNameOptions:
    dnsHostnameType: Optional[str] = None
    publicDualStackDnsName: Optional[str] = None
    publicIpv4DnsName: Optional[str] = None
    publicIpv6DnsName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DnsHostnameType": self.dnsHostnameType,
            "PublicDualStackDnsName": self.publicDualStackDnsName,
            "PublicIpv4DnsName": self.publicIpv4DnsName,
            "PublicIpv6DnsName": self.publicIpv6DnsName,
        }


@dataclass
class OperatorRequest:
    Principal: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Principal": self.Principal}


@dataclass
class OperatorResponse:
    managed: Optional[bool] = None
    principal: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"Managed": self.managed, "Principal": self.principal}


@dataclass
class ConnectionTrackingSpecificationRequest:
    TcpEstablishedTimeout: Optional[int] = None
    UdpStreamTimeout: Optional[int] = None
    UdpTimeout: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TcpEstablishedTimeout": self.TcpEstablishedTimeout,
            "UdpStreamTimeout": self.UdpStreamTimeout,
            "UdpTimeout": self.UdpTimeout,
        }


@dataclass
class ConnectionTrackingConfiguration:
    tcpEstablishedTimeout: Optional[int] = None
    udpStreamTimeout: Optional[int] = None
    udpTimeout: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TcpEstablishedTimeout": self.tcpEstablishedTimeout,
            "UdpStreamTimeout": self.udpStreamTimeout,
            "UdpTimeout": self.udpTimeout,
        }


@dataclass
class NetworkInterfacePermissionState:
    state: Optional[NetworkInterfacePermissionStateCode] = None
    statusMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "State": self.state.value if self.state else None,
            "StatusMessage": self.statusMessage,
        }


@dataclass
class NetworkInterfacePermission:
    awsAccountId: Optional[str] = None
    awsService: Optional[str] = None
    networkInterfaceId: Optional[str] = None
    networkInterfacePermissionId: Optional[str] = None
    permission: Optional[NetworkInterfacePermissionType] = None
    permissionState: Optional[NetworkInterfacePermissionState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AwsAccountId": self.awsAccountId,
            "AwsService": self.awsService,
            "NetworkInterfaceId": self.networkInterfaceId,
            "NetworkInterfacePermissionId": self.networkInterfacePermissionId,
            "Permission": self.permission.value if self.permission else None,
            "PermissionState": self.permissionState.to_dict() if self.permissionState else None,
        }


@dataclass
class NetworkInterfaceAttachmentChanges:
    AttachmentId: Optional[str] = None
    DefaultEnaQueueCount: Optional[bool] = None
    DeleteOnTermination: Optional[bool] = None
    EnaQueueCount: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AttachmentId": self.AttachmentId,
            "DefaultEnaQueueCount": self.DefaultEnaQueueCount,
            "DeleteOnTermination": self.DeleteOnTermination,
            "EnaQueueCount": self.EnaQueueCount,
        }


@dataclass
class EnaSrdUdpSpecification:
    EnaSrdUdpEnabled: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"EnaSrdUdpEnabled": self.EnaSrdUdpEnabled}


@dataclass
class EnaSrdSpecification:
    EnaSrdEnabled: Optional[bool] = None
    EnaSrdUdpSpecification: Optional[EnaSrdUdpSpecification] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "EnaSrdEnabled": self.EnaSrdEnabled,
            "EnaSrdUdpSpecification": self.EnaSrdUdpSpecification.to_dict()
            if self.EnaSrdUdpSpecification
            else None,
        }


@dataclass
class NetworkInterface:
    networkInterfaceId: Optional[str] = None
    subnetId: Optional[str] = None
    vpcId: Optional[str] = None
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    description: Optional[str] = None
    ownerId: Optional[str] = None
    requesterManaged: Optional[bool] = None
    status: Optional[NetworkInterfaceStatus] = None
    macAddress: Optional[str] = None
    privateIpAddress: Optional[str] = None
    privateDnsName: Optional[str] = None
    sourceDestCheck: Optional[bool] = None
    groupSet: List[GroupIdentifier] = field(default_factory=list)
    attachment: Optional[NetworkInterfaceAttachment] = None
    tagSet: List[Tag] = field(default_factory=list)
    privateIpAddressesSet: List[NetworkInterfacePrivateIpAddress] = field(default_factory=list)
    ipv6AddressesSet: List[NetworkInterfaceIpv6Address] = field(default_factory=list)
    interfaceType: Optional[InterfaceType] = None
    ipv4PrefixSet: List[Ipv4PrefixSpecification] = field(default_factory=list)
    ipv6Address: Optional[str] = None
    ipv6PrefixSet: List[Ipv6PrefixSpecification] = field(default_factory=list)
    operator: Optional[OperatorResponse] = None
    outpostArn: Optional[str] = None
    publicDnsName: Optional[str] = None
    publicIpDnsNameOptions: Optional[PublicIpDnsNameOptions] = None
    requesterId: Optional[str] = None
    requesterManaged: Optional[bool] = None
    denyAllIgwTraffic: Optional[bool] = None
    connectionTrackingConfiguration: Optional[ConnectionTrackingConfiguration] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "NetworkInterfaceId": self.networkInterfaceId,
            "SubnetId": self.subnetId,
            "VpcId": self.vpcId,
            "AvailabilityZone": self.availabilityZone,
            "AvailabilityZoneId": self.availabilityZoneId,
            "Description": self.description,
            "OwnerId": self.ownerId,
            "RequesterManaged": self.requesterManaged,
            "Status": self.status.value if self.status else None,
            "MacAddress": self.macAddress,
            "PrivateIpAddress": self.privateIpAddress,
            "PrivateDnsName": self.privateDnsName,
            "SourceDestCheck": self.sourceDestCheck,
            "GroupSet": [g.to_dict() for g in self.groupSet],
            "Attachment": self.attachment.to_dict() if self.attachment else None,
            "TagSet": [t.to_dict() for t in self.tagSet],
            "PrivateIpAddressesSet": [p.to_dict() for p in self.privateIpAddressesSet],
            "Ipv6AddressesSet": [i.to_dict() for i in self.ipv6AddressesSet],
            "InterfaceType": self.interfaceType.value if self.interfaceType else None,
            "Ipv4PrefixSet": [p.to_dict() for p in self.ipv4PrefixSet],
            "Ipv6Address": self.ipv6Address,
            "Ipv6PrefixSet": [p.to_dict() for p in self.ipv6PrefixSet],
            "Operator": self.operator.to_dict() if self.operator else None,
            "OutpostArn": self.outpostArn,
            "PublicDnsName": self.publicDnsName,
            "PublicIpDnsNameOptions": self.publicIpDnsNameOptions.to_dict() if self.publicIpDnsNameOptions else None,
            "RequesterId": self.requesterId,
            "DenyAllIgwTraffic": self.denyAllIgwTraffic,
            "ConnectionTrackingConfiguration": self.connectionTrackingConfiguration.to_dict()
            if self.connectionTrackingConfiguration
            else None,
        }


class ElasticnetworkinterfacesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.elastic_network_interfaces or similar

    def assign_ipv6_addresses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        if not network_interface_id:
            raise ValueError("NetworkInterfaceId is required")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise ValueError(f"NetworkInterface {network_interface_id} does not exist")

        ipv6_address_count = params.get("Ipv6AddressCount")
        ipv6_addresses = []
        # Ipv6Addresses.N keys are like Ipv6Addresses.1, Ipv6Addresses.2, ...
        for key, value in params.items():
            if key.startswith("Ipv6Addresses."):
                ipv6_addresses.append(value)

        ipv6_prefixes = []
        for key, value in params.items():
            if key.startswith("Ipv6Prefix."):
                ipv6_prefixes.append(value)

        ipv6_prefix_count = params.get("Ipv6PrefixCount")

        # Validate mutually exclusive parameters
        if ipv6_address_count and ipv6_addresses:
            raise ValueError("Cannot specify both Ipv6AddressCount and Ipv6Addresses")
        if ipv6_prefix_count and ipv6_prefixes:
            raise ValueError("Cannot specify both Ipv6PrefixCount and Ipv6Prefix")

        assigned_ipv6_addresses = []
        assigned_ipv6_prefixes = []

        # Assign IPv6 addresses
        if ipv6_addresses:
            # Assign specific IPv6 addresses
            for addr in ipv6_addresses:
                # Check if already assigned
                if any(ipv6.ipv6Address == addr for ipv6 in eni.ipv6AddressesSet):
                    continue
                new_ipv6 = NetworkInterfaceIpv6Address(ipv6Address=addr, isPrimaryIpv6=False, publicIpv6DnsName=None)
                eni.ipv6AddressesSet.append(new_ipv6)
                assigned_ipv6_addresses.append(addr)
        elif ipv6_address_count:
            # Assign automatically from subnet's IPv6 CIDR block range
            # For emulation, generate dummy IPv6 addresses
            count = int(ipv6_address_count)
            base_ipv6 = "2001:db8:1234:1a00::"
            existing_addresses = {ipv6.ipv6Address for ipv6 in eni.ipv6AddressesSet}
            next_suffix = 1
            while count > 0:
                candidate = f"{base_ipv6}{next_suffix:x}"
                if candidate not in existing_addresses:
                    new_ipv6 = NetworkInterfaceIpv6Address(ipv6Address=candidate, isPrimaryIpv6=False, publicIpv6DnsName=None)
                    eni.ipv6AddressesSet.append(new_ipv6)
                    assigned_ipv6_addresses.append(candidate)
                    count -= 1
                next_suffix += 1
        # Assign IPv6 prefixes
        if ipv6_prefixes:
            for prefix in ipv6_prefixes:
                if any(p.ipv6Prefix == prefix for p in eni.ipv6PrefixSet):
                    continue
                new_prefix = Ipv6PrefixSpecification(ipv6Prefix=prefix)
                eni.ipv6PrefixSet.append(new_prefix)
                assigned_ipv6_prefixes.append(prefix)
        elif ipv6_prefix_count:
            count = int(ipv6_prefix_count)
            base_prefix = "2001:db8:1234:1a00::/56"
            # For emulation, generate dummy prefixes with incrementing last hex digit
            existing_prefixes = {p.ipv6Prefix for p in eni.ipv6PrefixSet}
            next_suffix = 1
            while count > 0:
                candidate = f"2001:db8:1234:1a{next_suffix:02x}::/56"
                if candidate not in existing_prefixes:
                    new_prefix = Ipv6PrefixSpecification(ipv6Prefix=candidate)
                    eni.ipv6PrefixSet.append(new_prefix)
                    assigned_ipv6_prefixes.append(candidate)
                    count -= 1
                next_suffix += 1

        return {
            "requestId": self.generate_request_id(),
            "networkInterfaceId": network_interface_id,
            "assignedIpv6Addresses": assigned_ipv6_addresses,
            "assignedIpv6PrefixSet": assigned_ipv6_prefixes,
        }


    def assign_private_ip_addresses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        if not network_interface_id:
            raise ValueError("NetworkInterfaceId is required")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise ValueError(f"NetworkInterface {network_interface_id} does not exist")

        allow_reassignment = params.get("AllowReassignment", False)

        ipv4_prefixes = []
        for key, value in params.items():
            if key.startswith("Ipv4Prefix."):
                ipv4_prefixes.append(value)

        ipv4_prefix_count = params.get("Ipv4PrefixCount")

        private_ip_addresses = []
        for key, value in params.items():
            if key.startswith("PrivateIpAddress."):
                private_ip_addresses.append(value)

        secondary_private_ip_address_count = params.get("SecondaryPrivateIpAddressCount")

        # Validate mutually exclusive parameters
        if ipv4_prefixes and ipv4_prefix_count:
            raise ValueError("Cannot specify both Ipv4Prefix and Ipv4PrefixCount")
        if private_ip_addresses and secondary_private_ip_address_count:
            raise ValueError("Cannot specify both PrivateIpAddress and SecondaryPrivateIpAddressCount")

        assigned_ipv4_prefixes = []
        assigned_private_ip_addresses = []

        # Assign IPv4 prefixes
        if ipv4_prefixes:
            for prefix in ipv4_prefixes:
                if any(p.ipv4Prefix == prefix for p in eni.ipv4PrefixSet):
                    continue
                new_prefix = Ipv4PrefixSpecification(ipv4Prefix=prefix)
                eni.ipv4PrefixSet.append(new_prefix)
                assigned_ipv4_prefixes.append(new_prefix)
        elif ipv4_prefix_count:
            count = int(ipv4_prefix_count)
            # For emulation, generate dummy prefixes
            existing_prefixes = {p.ipv4Prefix for p in eni.ipv4PrefixSet}
            next_suffix = 1
            while count > 0:
                candidate = f"10.0.{next_suffix}.0/24"
                if candidate not in existing_prefixes:
                    new_prefix = Ipv4PrefixSpecification(ipv4Prefix=candidate)
                    eni.ipv4PrefixSet.append(new_prefix)
                    assigned_ipv4_prefixes.append(new_prefix)
                    count -= 1
                next_suffix += 1

        # Assign private IP addresses
        if private_ip_addresses:
            for ip in private_ip_addresses:
                # Check if already assigned
                if any(p.privateIpAddress == ip for p in eni.privateIpAddressesSet):
                    continue
                new_private_ip = NetworkInterfacePrivateIpAddress(
                    association=None,
                    primary=False,
                    privateDnsName=None,
                    privateIpAddress=ip,
                )
                eni.privateIpAddressesSet.append(new_private_ip)
                assigned_private_ip_addresses.append(new_private_ip)
        elif secondary_private_ip_address_count:
            count = int(secondary_private_ip_address_count)
            # For emulation, generate dummy IPs in subnet range
            # We try to find subnet CIDR from eni.subnetId
            subnet = self.state.get_resource(eni.subnetId) if eni.subnetId else None
            base_ip_prefix = "10.0.0."
            existing_ips = {p.privateIpAddress for p in eni.privateIpAddressesSet}
            next_suffix = 1
            while count > 0:
                candidate = f"{base_ip_prefix}{100 + next_suffix}"
                if candidate not in existing_ips:
                    new_private_ip = NetworkInterfacePrivateIpAddress(
                        association=None,
                        primary=False,
                        privateDnsName=None,
                        privateIpAddress=candidate,
                    )
                    eni.privateIpAddressesSet.append(new_private_ip)
                    assigned_private_ip_addresses.append(new_private_ip)
                    count -= 1
                next_suffix += 1

        # Return assigned private IP addresses as list of dicts with privateIpAddress key
        assigned_private_ip_addresses_dicts = [
            {"privateIpAddress": ip.privateIpAddress} for ip in assigned_private_ip_addresses
        ]

        assigned_ipv4_prefixes_dicts = [
            {"ipv4Prefix": prefix.ipv4Prefix} for prefix in assigned_ipv4_prefixes
        ]

        return {
            "requestId": self.generate_request_id(),
            "networkInterfaceId": network_interface_id,
            "assignedPrivateIpAddressesSet": assigned_private_ip_addresses_dicts,
            "assignedIpv4PrefixSet": assigned_ipv4_prefixes_dicts,
        }


    def attach_network_interface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        device_index = params.get("DeviceIndex")
        instance_id = params.get("InstanceId")
        network_interface_id = params.get("NetworkInterfaceId")

        if device_index is None:
            raise ValueError("DeviceIndex is required")
        if not instance_id:
            raise ValueError("InstanceId is required")
        if not network_interface_id:
            raise ValueError("NetworkInterfaceId is required")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise ValueError(f"NetworkInterface {network_interface_id} does not exist")

        # Check if already attached
        if eni.attachment and eni.attachment.status != NetworkInterfaceAttachmentStatus.DETACHED:
            raise ValueError(f"NetworkInterface {network_interface_id} is already attached")

        ena_queue_count = params.get("EnaQueueCount")
        ena_srd_spec = params.get("EnaSrdSpecification")
        network_card_index = params.get("NetworkCardIndex", 0)

        # Create attachment id
        attachment_id = self.generate_unique_id(prefix="eni-attach-")

        # Create AttachmentEnaSrdUdpSpecification if present
        attachment_ena_srd_udp_spec = None
        if ena_srd_spec and isinstance(ena_srd_spec, dict):
            ena_srd_udp_spec_dict = ena_srd_spec.get("EnaSrdUdpSpecification")
            if ena_srd_udp_spec_dict:
                attachment_ena_srd_udp_spec = AttachmentEnaSrdUdpSpecification(
                    enaSrdUdpEnabled=ena_srd_udp_spec_dict.get("EnaSrdUdpEnabled")
                )
            ena_srd_enabled = ena_srd_spec.get("EnaSrdEnabled")
            attachment_ena_srd_spec = AttachmentEnaSrdSpecification(
                enaSrdEnabled=ena_srd_enabled,
                enaSrdUdpSpecification=attachment_ena_srd_udp_spec,
            )
        else:
            attachment_ena_srd_spec = None

        # Create attachment object
        attachment = NetworkInterfaceAttachment(
            attachmentId=attachment_id,
            attachTime=datetime.utcnow(),
            deleteOnTermination=False,
            deviceIndex=int(device_index),
            enaQueueCount=ena_queue_count,
            enaSrdSpecification=attachment_ena_srd_spec,
            instanceId=instance_id,
            instanceOwnerId=None,
            networkCardIndex=network_card_index,
            status=NetworkInterfaceAttachmentStatus.ATTACHING,
        )

        eni.attachment = attachment
        eni.status = NetworkInterfaceStatus.IN_USE

        return {
            "requestId": self.generate_request_id(),
            "attachmentId": attachment_id,
            "networkCardIndex": network_card_index,
        }


    def create_network_interface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        subnet_id = params.get("SubnetId")
        if not subnet_id:
            raise ValueError("SubnetId is required")

        # Generate network interface id
        network_interface_id = self.generate_unique_id(prefix="eni-")

        # Owner id
        owner_id = self.get_owner_id()

        # Description
        description = params.get("Description")

        # InterfaceType
        interface_type_str = params.get("InterfaceType")
        interface_type = None
        if interface_type_str:
            try:
                interface_type = InterfaceType(interface_type_str)
            except Exception:
                interface_type = None

        # Security groups
        group_ids = []
        for key, value in params.items():
            if key.startswith("SecurityGroupId."):
                group_ids.append(value)
        group_set = [GroupIdentifier(GroupId=gid, GroupName=None) for gid in group_ids]

        # Tags
        tag_specifications = []
        for key, value in params.items():
            if key.startswith("TagSpecification."):
                # For simplicity, skip detailed parsing of tags here
                pass
        tag_set = []
        # If TagSpecification.N present, parse tags
        # For simplicity, skip detailed parsing here

        # Private IP addresses
        private_ip_addresses = []
        for key, value in params.items():
            if key.startswith("PrivateIpAddresses."):
                # Expect keys like PrivateIpAddresses.1.Primary, PrivateIpAddresses.1.PrivateIpAddress
                # Parse index
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    attr = parts[2]
                    # Find or create dict for this index
                    while len(private_ip_addresses) < int(idx):
                        private_ip_addresses.append({})
                    private_ip_addresses[int(idx) - 1][attr] = value

        # SecondaryPrivateIpAddressCount
        secondary_private_ip_address_count = params.get("SecondaryPrivateIpAddressCount")
        if secondary_private_ip_address_count is not None:
            secondary_private_ip_address_count = int(secondary_private_ip_address_count)

        # PrivateIpAddress (primary)
        primary_private_ip = params.get("PrivateIpAddress")

        # Ipv6Addresses.N
        ipv6_addresses = []
        for key, value in params.items():
            if key.startswith("Ipv6Addresses."):
                # Expect keys like Ipv6Addresses.1.Ipv6Address, Ipv6Addresses.1.IsPrimaryIpv6
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    attr = parts[2]
                    while len(ipv6_addresses) < int(idx):
                        ipv6_addresses.append({})
                    ipv6_addresses[int(idx) - 1][attr] = value

        # Ipv6AddressCount
        ipv6_address_count = params.get("Ipv6AddressCount")
        if ipv6_address_count is not None:
            ipv6_address_count = int(ipv6_address_count)

        # Ipv4Prefix.N
        ipv4_prefixes = []
        for key, value in params.items():
            if key.startswith("Ipv4Prefix."):
                ipv4_prefixes.append(value)

        # Ipv4PrefixCount
        ipv4_prefix_count = params.get("Ipv4PrefixCount")
        if ipv4_prefix_count is not None:
            ipv4_prefix_count = int(ipv4_prefix_count)

        # Ipv6Prefix.N
        ipv6_prefixes = []
        for key, value in params.items():
            if key.startswith("Ipv6Prefix."):
                ipv6_prefixes.append(value)

        # Ipv6PrefixCount
        ipv6_prefix_count = params.get("Ipv6PrefixCount")
        if ipv6_prefix_count is not None:
            ipv6_prefix_count = int(ipv6_prefix_count)

        # Operator
        operator = None
        operator_dict = params.get("Operator")
        if operator_dict and isinstance(operator_dict, dict):
            principal = operator_dict.get("Principal")
            operator = OperatorResponse(managed=None, principal=principal)

        # ConnectionTrackingSpecification
        connection_tracking_spec = params.get("ConnectionTrackingSpecification")
        connection_tracking_configuration = None
        if connection_tracking_spec and isinstance(connection_tracking_spec, dict):
            tcp_timeout = connection_tracking_spec.get("TcpEstablishedTimeout")
            udp_stream_timeout = connection_tracking_spec.get("UdpStreamTimeout")
            udp_timeout = connection_tracking_spec.get("UdpTimeout")
            connection_tracking_configuration = ConnectionTrackingConfiguration(
                tcpEstablishedTimeout=tcp_timeout,
                udpStreamTimeout=udp_stream_timeout,
                udpTimeout=udp_timeout,
            )

        # SourceDestCheck default True
        source_dest_check = params.get("SourceDestCheck", True)
        if isinstance(source_dest_check, str):
            source_dest_check = source_dest_check.lower() == "true"

        # RequesterManaged default False
        requester_managed = params.get("RequesterManaged", False)
        if isinstance(requester_managed, str):
            requester_managed = requester_managed.lower() == "true"

        # DenyAllIgwTraffic default False
        deny_all_igw_traffic = params.get("DenyAllIgwTraffic", False)
        if isinstance(deny_all_igw_traffic, str):
            deny_all_igw_traffic = deny_all_igw_traffic.lower() == "true"

        # AvailabilityZone and AvailabilityZoneId - for emulation, set None
        availability_zone = None
        availability_zone_id = None

        # VPC ID - for emulation, try to get from subnet resource if available
        vpc_id = None
        subnet = self.state.get_resource(subnet_id)
        if subnet and hasattr(subnet, "vpcId"):
            vpc_id = subnet.vpcId

        # MAC address - generate dummy mac address
        mac_address = "02:74:b0:%02x:%02x:%02x" % (
            (len(self.state.elastic_network_interfaces) >> 16) & 0xFF,
            (len(self.state.elastic_network_interfaces) >> 8) & 0xFF,
            len(self.state.elastic_network_interfaces) & 0xFF,
        )

        # Status - pending on creation
        status = NetworkInterfaceStatus.PENDING

        # Private IP addresses set
        private_ip_addresses_set = []

        # If PrivateIpAddresses specified, use them
        if private_ip_addresses:
            for ip_spec in private_ip_addresses:
                primary = ip_spec.get("Primary", False)
                if isinstance(primary, str):
                    primary = primary.lower() == "true"
                private_ip = ip_spec.get("PrivateIpAddress")
                if private_ip:
                    private_ip_addresses_set.append(
                        NetworkInterfacePrivateIpAddress(
                            association=None,
                            primary=primary,
                            privateDnsName=None,
                            privateIpAddress=private_ip,
                        )
                    )
        else:
            # If PrimaryPrivateIp specified, add it as primary
            if primary_private_ip:
                private_ip_addresses_set.append(
                    NetworkInterfacePrivateIpAddress(
                        association=None,
                        primary=True,
                        privateDnsName=None,
                        privateIpAddress=primary_private_ip,
                    )
                )
            else:
                # Assign a dummy primary IP address
                private_ip_addresses_set.append(
                    NetworkInterfacePrivateIpAddress(
                        association=None,
                        primary=True,
                        privateDnsName=None,
                        privateIpAddress="10.0.0.1",
                    )
                )

        # Add secondary private IP addresses if count specified
        if secondary_private_ip_address_count:
            existing_ips = {ip.privateIpAddress for ip in private_ip_addresses_set}
            next_suffix = 2
            while len(private_ip_addresses_set) < secondary_private_ip_address_count + 1:
                candidate = f"10.0.0.{next_suffix}"
                if candidate not in existing_ips:
                    private_ip_addresses_set.append(
                        NetworkInterfacePrivateIpAddress(
                            association=None,
                            primary=False,
                            privateDnsName=None,
                            privateIpAddress=candidate,
                        )
                    )
                next_suffix += 1

    def delete_network_interface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        dry_run = params.get("DryRun", False)

        if not network_interface_id:
            raise Exception("Missing required parameter NetworkInterfaceId")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            # According to AWS behavior, if the network interface does not exist, it returns an error
            raise Exception(f"The network interface '{network_interface_id}' does not exist")

        if dry_run:
            # Check permissions - for emulator, assume always allowed
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        # Must detach before delete
        if eni.get("attachment") and eni["attachment"].get("status") in ["attaching", "attached"]:
            # AWS returns an error if trying to delete attached interface
            raise Exception(f"Cannot delete network interface '{network_interface_id}' while it is attached")

        # Delete the network interface
        del self.state.elastic_network_interfaces[network_interface_id]
        if network_interface_id in self.state.resources:
            del self.state.resources[network_interface_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def delete_network_interface_permission(self, params: Dict[str, Any]) -> Dict[str, Any]:
        permission_id = params.get("NetworkInterfacePermissionId")
        dry_run = params.get("DryRun", False)
        force = params.get("Force", False)

        if not permission_id:
            raise Exception("Missing required parameter NetworkInterfacePermissionId")

        permission = self.state.resources.get(permission_id)
        if not permission:
            raise Exception(f"The network interface permission '{permission_id}' does not exist")

        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        # Check if the permission is attached to an interface that is attached to an instance
        eni_id = permission.get("networkInterfaceId")
        eni = self.state.elastic_network_interfaces.get(eni_id) if eni_id else None
        if eni and eni.get("attachment") and eni["attachment"].get("status") == "attached":
            if not force:
                raise Exception("Cannot delete permission while network interface is attached. Use Force=true to override.")

        # Delete the permission
        del self.state.resources[permission_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def describe_network_interface_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        attribute = params.get("Attribute")
        dry_run = params.get("DryRun", False)

        if not network_interface_id:
            raise Exception("Missing required parameter NetworkInterfaceId")

        if not attribute:
            raise Exception("Missing required parameter Attribute")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise Exception(f"The network interface '{network_interface_id}' does not exist")

        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        response = {
            "requestId": self.generate_request_id(),
            "networkInterfaceId": network_interface_id,
        }

        attr = attribute.lower()
        # Map attribute to response structure
        if attr == "description":
            desc = eni.get("description")
            response["description"] = {"value": desc} if desc is not None else {"value": ""}
        elif attr == "groupset":
            groups = eni.get("groupSet", [])
            response["groupSet"] = []
            for g in groups:
                response["groupSet"].append({
                    "groupId": g.get("GroupId"),
                    "groupName": g.get("GroupName"),
                })
        elif attr == "sourcedestcheck":
            val = eni.get("sourceDestCheck")
            response["sourceDestCheck"] = {"value": bool(val)} if val is not None else {"value": True}
        elif attr == "attachment":
            attach = eni.get("attachment")
            if attach:
                # Copy attachment fields with expected keys and types
                ena_srd_spec = attach.get("enaSrdSpecification")
                ena_srd_udp_spec = None
                if ena_srd_spec:
                    ena_srd_udp_spec_data = ena_srd_spec.get("enaSrdUdpSpecification")
                    ena_srd_udp_spec = {
                        "enaSrdUdpEnabled": ena_srd_udp_spec_data.get("enaSrdUdpEnabled")
                    } if ena_srd_udp_spec_data else None
                    ena_srd_spec = {
                        "enaSrdEnabled": ena_srd_spec.get("enaSrdEnabled"),
                        "enaSrdUdpSpecification": ena_srd_udp_spec
                    }
                response["attachment"] = {
                    "attachmentId": attach.get("attachmentId"),
                    "attachTime": attach.get("attachTime"),
                    "deleteOnTermination": attach.get("deleteOnTermination"),
                    "deviceIndex": attach.get("deviceIndex"),
                    "enaQueueCount": attach.get("enaQueueCount"),
                    "enaSrdSpecification": ena_srd_spec,
                    "instanceId": attach.get("instanceId"),
                    "instanceOwnerId": attach.get("instanceOwnerId"),
                    "networkCardIndex": attach.get("networkCardIndex"),
                    "status": attach.get("status"),
                }
            else:
                response["attachment"] = None
        elif attr == "associatepublicipaddress":
            # This attribute is only for primary interface eth0, emulate as False if not set
            response["associatePublicIpAddress"] = eni.get("associatePublicIpAddress", False)
        else:
            # Unknown attribute requested
            raise Exception(f"Invalid attribute '{attribute}' requested")

        return response


    def describe_network_interface_permissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = []
        # Filters come as Filter.N.Name and Filter.N.Value.M
        # Collect filters from params keys
        for key, value in params.items():
            if key.startswith("Filter."):
                # key format: Filter.N.Name or Filter.N.Value.M
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    field = parts[2]
                    # Find or create filter dict for idx
                    while len(filters) < int(idx):
                        filters.append({"Name": None, "Values": []})
                    if field.lower() == "name":
                        filters[int(idx)-1]["Name"] = value
                    elif field.lower() == "value":
                        filters[int(idx)-1]["Values"].append(value)

        max_results = params.get("MaxResults")
        permission_ids = []
        # Collect NetworkInterfacePermissionId.N
        for key, value in params.items():
            if key.startswith("NetworkInterfacePermissionId."):
                permission_ids.append(value)

        next_token = params.get("NextToken")

        # Gather all permissions from state.resources that are network interface permissions
        # We assume permissions have a type or identifiable by keys
        all_permissions = []
        for res_id, res in self.state.resources.items():
            # Heuristic: permission objects have keys like networkInterfacePermissionId
            if isinstance(res, dict) and "networkInterfacePermissionId" in res:
                all_permissions.append(res)

        # Filter by permission IDs if provided
        if permission_ids:
            all_permissions = [p for p in all_permissions if p.get("networkInterfacePermissionId") in permission_ids]

        # Apply filters
        def match_filter(perm, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            # Map filter names to permission fields
            # Lowercase for case-insensitive matching
            lname = name.lower()
            if lname == "network-interface-permission.network-interface-permission-id":
                return perm.get("networkInterfacePermissionId") in values
            elif lname == "network-interface-permission.network-interface-id":
                return perm.get("networkInterfaceId") in values
            elif lname == "network-interface-permission.aws-account-id":
                return perm.get("awsAccountId") in values
            elif lname == "network-interface-permission.aws-service":
                return perm.get("awsService") in values
            elif lname == "network-interface-permission.permission":
                return perm.get("permission") in values
            else:
                # Unknown filter, ignore
                return True

        for f in filters:
            all_permissions = [p for p in all_permissions if match_filter(p, f)]

        # Pagination
        # For simplicity, NextToken is an index string, MaxResults limits number of items
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results_int = 50
        if max_results:
            try:
                max_results_int = int(max_results)
                if max_results_int < 5:
                    max_results_int = 5
                elif max_results_int > 255:
                    max_results_int = 255
            except Exception:
                max_results_int = 50

        paged_permissions = all_permissions[start_index:start_index+max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(all_permissions):
            new_next_token = str(start_index + max_results_int)

        # Format response permissions
        response_permissions = []
        for perm in paged_permissions:
            perm_state = perm.get("permissionState", {})
            response_permissions.append({
                "awsAccountId": perm.get("awsAccountId"),
                "awsService": perm.get("awsService"),
                "networkInterfaceId": perm.get("networkInterfaceId"),
                "networkInterfacePermissionId": perm.get("networkInterfacePermissionId"),
                "permission": perm.get("permission"),
                "permissionState": {
                    "state": perm_state.get("state"),
                    "statusMessage": perm_state.get("statusMessage"),
                } if perm_state else None,
            })

        return {
            "requestId": self.generate_request_id(),
            "networkInterfacePermissions": response_permissions,
            "nextToken": new_next_token,
        }


    def describe_network_interfaces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)

        # Collect filters
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    idx = parts[1]
                    field = parts[2]
                    while len(filters) < int(idx):
                        filters.append({"Name": None, "Values": []})
                    if field.lower() == "name":
                        filters[int(idx)-1]["Name"] = value
                    elif field.lower().startswith("value"):
                        filters[int(idx)-1]["Values"].append(value)

        max_results = params.get("MaxResults")
        network_interface_ids = []
        for key, value in params.items():
            if key.startswith("NetworkInterfaceId."):
                network_interface_ids.append(value)

        next_token = params.get("NextToken")

        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set"
            }

        # Gather all ENIs or filter by IDs
        if network_interface_ids:
            enis = [self.state.elastic_network_interfaces.get(eni_id) for eni_id in network_interface_ids]
            enis = [eni for eni in enis if eni is not None]
        else:
            enis = list(self.state.elastic_network_interfaces.values())

        # Apply filters
        def match_filter(eni, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            lname = name.lower()

            # Implement common filters from the doc
            if lname == "availability-zone":
                return eni.get("availabilityZone") in values
            elif lname == "availability-zone-id":
                return eni.get("availabilityZoneId") in values
            elif lname == "description":
                return eni.get("description") in values
            elif lname == "group-id":
                group_ids = [g.get("GroupId") for g in eni.get("groupSet", [])]
                return any(v in group_ids for v in values)
            elif lname == "ipv6-addresses.ipv6-address":
                ipv6s = [addr.get("ipv6Address") for addr in eni.get("ipv6AddressesSet", [])]
                return any(v in ipv6s for v in values)
            elif lname == "interface-type":
                return eni.get("interfaceType") in values
            elif lname == "mac-address":
                return eni.get("macAddress") in values
            elif lname == "network-interface-id":
                return eni.get("networkInterfaceId") in values
            elif lname == "owner-id":
                return eni.get("ownerId") in values
            elif lname == "private-dns-name":
                return eni.get("privateDnsName") in values
            elif lname == "private-ip-address":
                # Check primary and secondary private IPs
                if eni.get("privateIpAddress") in values:
                    return True
                for priv in eni.get("privateIpAddressesSet", []):
                    if priv.get("privateIpAddress") in values:
                        return True
                return False
            elif lname == "source-dest-check":
                val = eni.get("sourceDestCheck")
                # AWS expects string "true" or "false" in filter values
                val_str = "true" if val else "false"
                return val_str in [v.lower() for v in values]
            elif lname == "status":
                return eni.get("status") in values
            elif lname == "subnet-id":
                return eni.get("subnetId") in values
            elif lname.startswith("tag:"):
                tag_key = lname[4:]
                tags = eni.get("tagSet", [])
                for tag in tags:
                    if tag.get("Key") == tag_key and tag.get("Value") in values:
                        return True
                return False
            elif lname == "tag-key":
                tags = eni.get("tagSet", [])
                tag_keys = [tag.get("Key") for tag in tags]
                return any(v in tag_keys for v in values)
            elif lname == "vpc-id":
                return eni.get("vpcId") in values
            else:
                # Unknown filter, ignore
                return True

        filtered_enis = [eni for eni in enis if all(match_filter(eni, f) for f in filters)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results_int = 1000
        if max_results:
            try:
                max_results_int = int(max_results)
                if max_results_int < 5:
                    max_results_int = 5
                elif max_results_int > 1000:
                    max_results_int = 1000
            except Exception:
                max_results_int = 1000

        paged_enis = filtered_enis[start_index:start_index+max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(filtered_enis):
            new_next_token = str(start_index + max_results_int)

        # Format response
        def format_eni(eni):
            # Defensive copy and format fields as per response spec
            attachment = eni.get("attachment")
            ena_srd_spec = None
            if attachment:
                ena_srd_spec_data = attachment.get("enaSrdSpecification")
                ena_srd_udp_spec = None
                if ena_srd_spec_data:
                    ena_srd_udp_spec_data = ena_srd_spec_data.get("enaSrdUdpSpecification")
                    ena_srd_udp_spec = {
                        "enaSrdUdpEnabled": ena_srd_udp_spec_data.get("enaSrdUdpEnabled")
                    } if ena_srd_udp_spec_data else None
                    ena_srd_spec = {
                        "enaSrdEnabled": ena_srd_spec_data.get("enaSrdEnabled"),
                        "enaSrdUdpSpecification": ena_srd_udp_spec
                    }
                attachment_formatted = {
                    "attachmentId": attachment.get("attachmentId"),
                    "attachTime": attachment.get("attachTime"),
                    "deleteOnTermination": attachment.get("deleteOnTermination"),
                    "deviceIndex": attachment.get("deviceIndex"),
                    "enaQueueCount": attachment.get("enaQueueCount"),
                    "enaSrdSpecification": ena_srd_spec,
                    "instanceId": attachment.get("instanceId"),
                    "instanceOwnerId": attachment.get("instanceOwnerId"),
                    "networkCardIndex": attachment.get("networkCardIndex"),
                    "status": attachment.get("status"),
                }
            else:
                attachment_formatted = None

            group_set = []
            for g in eni.get("groupSet", []):
                group_set.append({
                    "GroupId": g.get("GroupId"),
                    "GroupName": g.get("GroupName"),
                })

            private_ip_addresses_set = []
            for priv in eni.get("privateIpAddressesSet", []):
                assoc = priv.get("association")
                assoc_formatted = None
                if assoc:
                    assoc_formatted = {
                        "allocationId": assoc.get("allocationId"),
                        "associationId": assoc.get("associationId"),
                        "carrierIp": assoc.get("carrierIp"),
                        "customerOwnedIp": assoc.get("customerOwnedIp"),
                        "ipOwnerId": assoc.get("ipOwnerId"),
                        "publicDnsName": assoc.get("publicDnsName"),
                        "publicIp": assoc.get("publicIp"),
                    }
                private_ip_addresses_set.append({
                    "association": assoc_formatted,
                    "primary": priv.get("primary"),
                    "privateDnsName": priv.get("privateDnsName"),
                    "privateIpAddress": priv.get("privateIpAddress"),
                })

            ipv6_addresses_set = []
            for ipv6 in eni.get("ipv6AddressesSet", []):
                ipv6_addresses_set.append({
                    "ipv6Address": ipv6.get("ipv6Address"),
                    "isPrimaryIpv6": ipv6.get("isPrimaryIpv6"),
                    "publicIpv6DnsName": ipv6.get("publicIpv6DnsName"),
                })

            ipv4_prefix_set = []
            for prefix in eni.get("ipv4PrefixSet", []):
                ipv4_prefix_set.append({
                    "ipv4Prefix": prefix.get("ipv4Prefix")
                })

            ipv6_prefix_set = []
            for prefix in eni.get("ipv6PrefixSet", []):
                ipv6_prefix_set.append({
                    "ipv6Prefix": prefix.get("ipv6Prefix")
                })

            tag_set = []
            for tag in eni.get("tagSet", []):
                tag_set.append({
                    "Key": tag.get("Key"),
                    "Value": tag.get("Value")
                })

            # Return the formatted ENI
            return {
                "networkInterfaceId": eni.get("networkInterfaceId"),
                "subnetId": eni.get("subnetId"),
                "vpcId": eni.get("vpcId"),
                "availabilityZone": eni.get("availabilityZone"),
                "description": eni.get("description"),
                "ownerId": eni.get("ownerId"),
                "requesterId": eni.get("requesterId"),
                "requesterManaged": eni.get("requesterManaged"),
                "status": eni.get("status"),
                "macAddress": eni.get("macAddress"),
                "privateIpAddress": eni.get("privateIpAddress"),
                "privateDnsName": eni.get("privateDnsName"),
                "sourceDestCheck": eni.get("sourceDestCheck"),
                "interfaceType": eni.get("interfaceType"),
                "groupSet": group_set,
                "attachment": attachment_formatted,
                "association": eni.get("association"),
                "privateIpAddressesSet": private_ip_addresses_set,
                "ipv6AddressesSet": ipv6_addresses_set,
                "ipv4PrefixSet": ipv4_prefix_set,
                "ipv6PrefixSet": ipv6_prefix_set,
                "tagSet": tag_set,
            }

        # Build response list
        response_enis = []
        for eni in paged_enis:
            response_enis.append(format_eni(eni))

        return {
            "requestId": self.generate_request_id(),
            "networkInterfaceSet": response_enis,
            "nextToken": new_next_token
        }

    def create_network_interface_permission(self, params):
        # Placeholder
        return {}
    def detach_network_interface(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("AttachmentId")
        dry_run = params.get("DryRun", False)
        force = params.get("Force", False)

        if not attachment_id:
            raise ValueError("AttachmentId is required")

        # DryRun check
        if dry_run:
            # In a real implementation, check permissions here
            # For emulator, assume permission granted
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id()
            }

        # Find the network interface and attachment by attachment_id
        eni_to_detach = None
        for eni_id, eni in self.state.elastic_network_interfaces.items():
            attachment = eni.get("Attachment")
            if attachment and attachment.get("AttachmentId") == attachment_id:
                eni_to_detach = eni
                break

        if not eni_to_detach:
            # Attachment not found
            raise ValueError(f"AttachmentId {attachment_id} not found")

        # Detach logic
        # If force is True, forcibly detach even if instance is failed (emulated)
        # Remove attachment info from the ENI
        eni_to_detach["Attachment"] = None

        # Also update instance metadata if needed (emulated)
        # For emulator, we skip instance metadata update

        return {
            "requestId": self.generate_request_id(),
            "return": True
        }


    def modify_network_interface_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        dry_run = params.get("DryRun", False)

        if not network_interface_id:
            raise ValueError("NetworkInterfaceId is required")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise ValueError(f"NetworkInterfaceId {network_interface_id} not found")

        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id()
            }

        # Only one attribute can be modified at a time, but we will process all provided keys
        # Process Attachment changes
        attachment_changes = params.get("Attachment")
        if attachment_changes:
            attachment = eni.get("Attachment", {})
            # AttachmentId is optional here, but if modifying DeleteOnTermination, AttachmentId must be specified
            attachment_id = attachment_changes.get("AttachmentId")
            if "DeleteOnTermination" in attachment_changes:
                if not attachment_id or attachment.get("AttachmentId") != attachment_id:
                    raise ValueError("AttachmentId must be specified and match current attachment to modify DeleteOnTermination")
                attachment["DeleteOnTermination"] = attachment_changes["DeleteOnTermination"]
            if "EnaQueueCount" in attachment_changes:
                attachment["EnaQueueCount"] = attachment_changes["EnaQueueCount"]
            if "DefaultEnaQueueCount" in attachment_changes:
                attachment["DefaultEnaQueueCount"] = attachment_changes["DefaultEnaQueueCount"]
            eni["Attachment"] = attachment

        # Process Description
        description_obj = params.get("Description")
        if description_obj and isinstance(description_obj, dict):
            value = description_obj.get("Value")
            eni["Description"] = value

        # Process AssociatePublicIpAddress (only applies to primary interface eth0)
        if "AssociatePublicIpAddress" in params:
            # For emulator, just store the flag
            eni["AssociatePublicIpAddress"] = bool(params["AssociatePublicIpAddress"])

        # Process SecurityGroupId.N (array of strings)
        # This replaces the current security groups
        security_groups = []
        for key, value in params.items():
            if key.startswith("SecurityGroupId."):
                security_groups.append(value)
        if security_groups:
            eni["Groups"] = security_groups

        # Process SourceDestCheck (AttributeBooleanValueobject)
        source_dest_check_obj = params.get("SourceDestCheck")
        if source_dest_check_obj and isinstance(source_dest_check_obj, dict):
            val = source_dest_check_obj.get("Value")
            if val is not None:
                eni["SourceDestCheck"] = bool(val)

        # Process EnablePrimaryIpv6
        if "EnablePrimaryIpv6" in params:
            eni["EnablePrimaryIpv6"] = bool(params["EnablePrimaryIpv6"])

        # Process EnaSrdSpecification
        ena_srd_spec = params.get("EnaSrdSpecification")
        if ena_srd_spec and isinstance(ena_srd_spec, dict):
            ena_srd_enabled = ena_srd_spec.get("EnaSrdEnabled")
            if ena_srd_enabled is not None:
                eni["EnaSrdEnabled"] = bool(ena_srd_enabled)
            ena_srd_udp_spec = ena_srd_spec.get("EnaSrdUdpSpecification")
            if ena_srd_udp_spec and isinstance(ena_srd_udp_spec, dict):
                ena_srd_udp_enabled = ena_srd_udp_spec.get("EnaSrdUdpEnabled")
                if ena_srd_udp_enabled is not None:
                    eni["EnaSrdUdpEnabled"] = bool(ena_srd_udp_enabled)

        # Process AssociatedSubnetId.N (array of strings)
        associated_subnet_ids = []
        for key, value in params.items():
            if key.startswith("AssociatedSubnetId."):
                associated_subnet_ids.append(value)
        if associated_subnet_ids:
            eni["AssociatedSubnetIds"] = associated_subnet_ids

        return {
            "requestId": self.generate_request_id(),
            "return": True
        }


    def reset_network_interface_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        dry_run = params.get("DryRun", False)
        source_dest_check = params.get("SourceDestCheck")

        if not network_interface_id:
            raise ValueError("NetworkInterfaceId is required")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise ValueError(f"NetworkInterfaceId {network_interface_id} not found")

        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id()
            }

        # Only one attribute can be reset at a time
        if source_dest_check is not None:
            # Reset source/destination check to True
            eni["SourceDestCheck"] = True
        else:
            raise ValueError("No attribute specified to reset")

        return {
            "requestId": self.generate_request_id(),
            "return": True
        }


    def unassign_ipv6_addresses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        ipv6_addresses = []
        ipv6_prefixes = []

        # Collect Ipv6Addresses.N keys
        for key, value in params.items():
            if key.startswith("Ipv6Addresses."):
                ipv6_addresses.append(value)
            elif key.startswith("Ipv6Prefix."):
                ipv6_prefixes.append(value)

        if not network_interface_id:
            raise ValueError("NetworkInterfaceId is required")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise ValueError(f"NetworkInterfaceId {network_interface_id} not found")

        # Current assigned IPv6 addresses and prefixes
        assigned_ipv6_addresses = eni.get("Ipv6Addresses", [])
        assigned_ipv6_prefixes = eni.get("Ipv6Prefixes", [])

        # Unassign specified IPv6 addresses
        unassigned_ipv6_addresses = []
        for addr in ipv6_addresses:
            if addr in assigned_ipv6_addresses:
                assigned_ipv6_addresses.remove(addr)
                unassigned_ipv6_addresses.append(addr)

        # Unassign specified IPv6 prefixes
        unassigned_ipv6_prefixes = []
        for prefix in ipv6_prefixes:
            if prefix in assigned_ipv6_prefixes:
                assigned_ipv6_prefixes.remove(prefix)
                unassigned_ipv6_prefixes.append(prefix)

        # Update ENI state
        eni["Ipv6Addresses"] = assigned_ipv6_addresses
        eni["Ipv6Prefixes"] = assigned_ipv6_prefixes

        return {
            "requestId": self.generate_request_id(),
            "networkInterfaceId": network_interface_id,
            "unassignedIpv6Addresses": unassigned_ipv6_addresses,
            "unassignedIpv6PrefixSet": unassigned_ipv6_prefixes
        }


    def unassign_private_ip_addresses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_interface_id = params.get("NetworkInterfaceId")
        private_ip_addresses = []
        ipv4_prefixes = []

        # Collect PrivateIpAddress.N keys
        for key, value in params.items():
            if key.startswith("PrivateIpAddress."):
                private_ip_addresses.append(value)
            elif key.startswith("Ipv4Prefix."):
                ipv4_prefixes.append(value)

        if not network_interface_id:
            raise ValueError("NetworkInterfaceId is required")

        eni = self.state.elastic_network_interfaces.get(network_interface_id)
        if not eni:
            raise ValueError(f"NetworkInterfaceId {network_interface_id} not found")

        # Current assigned private IP addresses and IPv4 prefixes
        assigned_private_ips = eni.get("PrivateIpAddresses", [])
        assigned_ipv4_prefixes = eni.get("Ipv4Prefixes", [])

        # Unassign specified private IP addresses
        for ip in private_ip_addresses:
            if ip in assigned_private_ips:
                assigned_private_ips.remove(ip)

        # Unassign specified IPv4 prefixes
        for prefix in ipv4_prefixes:
            if prefix in assigned_ipv4_prefixes:
                assigned_ipv4_prefixes.remove(prefix)

        # Update ENI state
        eni["PrivateIpAddresses"] = assigned_private_ips
        eni["Ipv4Prefixes"] = assigned_ipv4_prefixes

        return {
            "requestId": self.generate_request_id(),
            "return": True
        }

    

from emulator_core.gateway.base import BaseGateway

class ElasticnetworkinterfacesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssignIpv6Addresses", self.assign_ipv6_addresses)
        self.register_action("AssignPrivateIpAddresses", self.assign_private_ip_addresses)
        self.register_action("AttachNetworkInterface", self.attach_network_interface)
        self.register_action("CreateNetworkInterface", self.create_network_interface)
        self.register_action("CreateNetworkInterfacePermission", self.create_network_interface_permission)
        self.register_action("DeleteNetworkInterface", self.delete_network_interface)
        self.register_action("DeleteNetworkInterfacePermission", self.delete_network_interface_permission)
        self.register_action("DescribeNetworkInterfaceAttribute", self.describe_network_interface_attribute)
        self.register_action("DescribeNetworkInterfacePermissions", self.describe_network_interface_permissions)
        self.register_action("DescribeNetworkInterfaces", self.describe_network_interfaces)
        self.register_action("DetachNetworkInterface", self.detach_network_interface)
        self.register_action("ModifyNetworkInterfaceAttribute", self.modify_network_interface_attribute)
        self.register_action("ResetNetworkInterfaceAttribute", self.reset_network_interface_attribute)
        self.register_action("UnassignIpv6Addresses", self.unassign_ipv6_addresses)
        self.register_action("UnassignPrivateIpAddresses", self.unassign_private_ip_addresses)

    def assign_ipv6_addresses(self, params):
        return self.backend.assign_ipv6_addresses(params)

    def assign_private_ip_addresses(self, params):
        return self.backend.assign_private_ip_addresses(params)

    def attach_network_interface(self, params):
        return self.backend.attach_network_interface(params)

    def create_network_interface(self, params):
        return self.backend.create_network_interface(params)

    def create_network_interface_permission(self, params):
        return self.backend.create_network_interface_permission(params)

    def delete_network_interface(self, params):
        return self.backend.delete_network_interface(params)

    def delete_network_interface_permission(self, params):
        return self.backend.delete_network_interface_permission(params)

    def describe_network_interface_attribute(self, params):
        return self.backend.describe_network_interface_attribute(params)

    def describe_network_interface_permissions(self, params):
        return self.backend.describe_network_interface_permissions(params)

    def describe_network_interfaces(self, params):
        return self.backend.describe_network_interfaces(params)

    def detach_network_interface(self, params):
        return self.backend.detach_network_interface(params)

    def modify_network_interface_attribute(self, params):
        return self.backend.modify_network_interface_attribute(params)

    def reset_network_interface_attribute(self, params):
        return self.backend.reset_network_interface_attribute(params)

    def unassign_ipv6_addresses(self, params):
        return self.backend.unassign_ipv6_addresses(params)

    def unassign_private_ip_addresses(self, params):
        return self.backend.unassign_private_ip_addresses(params)
