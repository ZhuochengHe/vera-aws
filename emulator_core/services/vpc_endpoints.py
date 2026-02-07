from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class VpcEndpointType(str, Enum):
    INTERFACE = "Interface"
    GATEWAY = "Gateway"
    GATEWAY_LOAD_BALANCER = "GatewayLoadBalancer"
    RESOURCE = "Resource"
    SERVICE_NETWORK = "ServiceNetwork"


class VpcEndpointState(str, Enum):
    PENDING_ACCEPTANCE = "PendingAcceptance"
    PENDING = "Pending"
    AVAILABLE = "Available"
    DELETING = "Deleting"
    DELETED = "Deleted"
    REJECTED = "Rejected"
    FAILED = "Failed"
    EXPIRED = "Expired"
    PARTIAL = "Partial"


class DnsRecordIpType(str, Enum):
    IPV4 = "ipv4"
    DUALSTACK = "dualstack"
    IPV6 = "ipv6"
    SERVICE_DEFINED = "service-defined"


class PrivateDnsPreference(str, Enum):
    ALL_DOMAINS = "ALL_DOMAINS"
    VERIFIED_DOMAINS_ONLY = "VERIFIED_DOMAINS_ONLY"
    VERIFIED_DOMAINS_AND_SPECIFIED_DOMAINS = "VERIFIED_DOMAINS_AND_SPECIFIED_DOMAINS"
    SPECIFIED_DOMAINS_ONLY = "SPECIFIED_DOMAINS_ONLY"


class ConnectionNotificationState(str, Enum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"


class ConnectionNotificationType(str, Enum):
    TOPIC = "Topic"


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
class DnsOptionsSpecification:
    DnsRecordIpType: Optional[DnsRecordIpType] = None
    PrivateDnsOnlyForInboundResolverEndpoint: Optional[bool] = None
    PrivateDnsPreference: Optional[PrivateDnsPreference] = None
    PrivateDnsSpecifiedDomains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DnsRecordIpType": self.DnsRecordIpType.value if self.DnsRecordIpType else None,
            "PrivateDnsOnlyForInboundResolverEndpoint": self.PrivateDnsOnlyForInboundResolverEndpoint,
            "PrivateDnsPreference": self.PrivateDnsPreference.value if self.PrivateDnsPreference else None,
            "PrivateDnsSpecifiedDomains": self.PrivateDnsSpecifiedDomains,
        }


@dataclass
class DnsOptions:
    dnsRecordIpType: Optional[DnsRecordIpType] = None
    privateDnsOnlyForInboundResolverEndpoint: Optional[bool] = None
    privateDnsPreference: Optional[PrivateDnsPreference] = None
    privateDnsSpecifiedDomainSet: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dnsRecordIpType": self.dnsRecordIpType.value if self.dnsRecordIpType else None,
            "privateDnsOnlyForInboundResolverEndpoint": self.privateDnsOnlyForInboundResolverEndpoint,
            "privateDnsPreference": self.privateDnsPreference.value if self.privateDnsPreference else None,
            "privateDnsSpecifiedDomainSet": self.privateDnsSpecifiedDomainSet,
        }


@dataclass
class DnsEntry:
    dnsName: Optional[str] = None
    hostedZoneId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dnsName": self.dnsName,
            "hostedZoneId": self.hostedZoneId,
        }


@dataclass
class SecurityGroupIdentifier:
    groupId: Optional[str] = None
    groupName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "groupId": self.groupId,
            "groupName": self.groupName,
        }


@dataclass
class SubnetIpPrefixes:
    ipPrefixSet: List[str] = field(default_factory=list)
    subnetId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ipPrefixSet": self.ipPrefixSet,
            "subnetId": self.subnetId,
        }


@dataclass
class LastError:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass
class SubnetConfiguration:
    Ipv4: Optional[str] = None
    Ipv6: Optional[str] = None
    SubnetId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Ipv4": self.Ipv4,
            "Ipv6": self.Ipv6,
            "SubnetId": self.SubnetId,
        }


@dataclass
class VpcEndpoint:
    vpcEndpointId: str
    vpcId: str
    vpcEndpointType: Optional[VpcEndpointType] = None
    serviceName: Optional[str] = None
    state: Optional[VpcEndpointState] = None
    creationTimestamp: Optional[datetime] = None
    dnsEntrySet: List[DnsEntry] = field(default_factory=list)
    dnsOptions: Optional[DnsOptions] = None
    failureReason: Optional[str] = None
    groupSet: List[SecurityGroupIdentifier] = field(default_factory=list)
    ipAddressType: Optional[DnsRecordIpType] = None
    ipv4PrefixSet: List[SubnetIpPrefixes] = field(default_factory=list)
    ipv6PrefixSet: List[SubnetIpPrefixes] = field(default_factory=list)
    lastError: Optional[LastError] = None
    networkInterfaceIdSet: List[str] = field(default_factory=list)
    ownerId: Optional[str] = None
    policyDocument: Optional[str] = None
    privateDnsEnabled: Optional[bool] = None
    requesterManaged: Optional[bool] = None
    resourceConfigurationArn: Optional[str] = None
    routeTableIdSet: List[str] = field(default_factory=list)
    serviceNetworkArn: Optional[str] = None
    serviceRegion: Optional[str] = None
    subnetIdSet: List[str] = field(default_factory=list)
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vpcEndpointId": self.vpcEndpointId,
            "vpcId": self.vpcId,
            "vpcEndpointType": self.vpcEndpointType.value if self.vpcEndpointType else None,
            "serviceName": self.serviceName,
            "state": self.state.value if self.state else None,
            "creationTimestamp": self.creationTimestamp.isoformat() if self.creationTimestamp else None,
            "dnsEntrySet": [dns.to_dict() for dns in self.dnsEntrySet],
            "dnsOptions": self.dnsOptions.to_dict() if self.dnsOptions else None,
            "failureReason": self.failureReason,
            "groupSet": [group.to_dict() for group in self.groupSet],
            "ipAddressType": self.ipAddressType.value if self.ipAddressType else None,
            "ipv4PrefixSet": [prefix.to_dict() for prefix in self.ipv4PrefixSet],
            "ipv6PrefixSet": [prefix.to_dict() for prefix in self.ipv6PrefixSet],
            "lastError": self.lastError.to_dict() if self.lastError else None,
            "networkInterfaceIdSet": self.networkInterfaceIdSet,
            "ownerId": self.ownerId,
            "policyDocument": self.policyDocument,
            "privateDnsEnabled": self.privateDnsEnabled,
            "requesterManaged": self.requesterManaged,
            "resourceConfigurationArn": self.resourceConfigurationArn,
            "routeTableIdSet": self.routeTableIdSet,
            "serviceNetworkArn": self.serviceNetworkArn,
            "serviceRegion": self.serviceRegion,
            "subnetIdSet": self.subnetIdSet,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
        }


@dataclass
class ConnectionNotification:
    connectionNotificationId: Optional[str] = None
    connectionNotificationArn: Optional[str] = None
    connectionEvents: List[str] = field(default_factory=list)
    connectionNotificationState: Optional[ConnectionNotificationState] = None
    connectionNotificationType: Optional[ConnectionNotificationType] = None
    serviceId: Optional[str] = None
    serviceRegion: Optional[str] = None
    vpcEndpointId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connectionNotificationId": self.connectionNotificationId,
            "connectionNotificationArn": self.connectionNotificationArn,
            "connectionEvents": self.connectionEvents,
            "connectionNotificationState": self.connectionNotificationState.value if self.connectionNotificationState else None,
            "connectionNotificationType": self.connectionNotificationType.value if self.connectionNotificationType else None,
            "serviceId": self.serviceId,
            "serviceRegion": self.serviceRegion,
            "vpcEndpointId": self.vpcEndpointId,
        }


@dataclass
class UnsuccessfulItemError:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass
class UnsuccessfulItem:
    error: Optional[UnsuccessfulItemError] = None
    resourceId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error.to_dict() if self.error else None,
            "resourceId": self.resourceId,
        }


@dataclass
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Values": self.Values,
        }


@dataclass
class VpcEndpointAssociation:
    id: Optional[str] = None
    associatedResourceAccessibility: Optional[str] = None
    associatedResourceArn: Optional[str] = None
    dnsEntry: Optional[DnsEntry] = None
    failureCode: Optional[str] = None
    failureReason: Optional[str] = None
    privateDnsEntry: Optional[DnsEntry] = None
    resourceConfigurationGroupArn: Optional[str] = None
    serviceNetworkArn: Optional[str] = None
    serviceNetworkName: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    vpcEndpointId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "associatedResourceAccessibility": self.associatedResourceAccessibility,
            "associatedResourceArn": self.associatedResourceArn,
            "dnsEntry": self.dnsEntry.to_dict() if self.dnsEntry else None,
            "failureCode": self.failureCode,
            "failureReason": self.failureReason,
            "privateDnsEntry": self.privateDnsEntry.to_dict() if self.privateDnsEntry else None,
            "resourceConfigurationGroupArn": self.resourceConfigurationGroupArn,
            "serviceNetworkArn": self.serviceNetworkArn,
            "serviceNetworkName": self.serviceNetworkName,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "vpcEndpointId": self.vpcEndpointId,
        }


@dataclass
class VpcEndpointConnection:
    vpcEndpointConnectionId: Optional[str] = None
    vpcEndpointId: Optional[str] = None
    vpcEndpointOwner: Optional[str] = None
    vpcEndpointRegion: Optional[str] = None
    vpcEndpointState: Optional[VpcEndpointState] = None
    creationTimestamp: Optional[datetime] = None
    dnsEntrySet: List[DnsEntry] = field(default_factory=list)
    gatewayLoadBalancerArnSet: List[str] = field(default_factory=list)
    ipAddressType: Optional[DnsRecordIpType] = None
    networkLoadBalancerArnSet: List[str] = field(default_factory=list)
    serviceId: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vpcEndpointConnectionId": self.vpcEndpointConnectionId,
            "vpcEndpointId": self.vpcEndpointId,
            "vpcEndpointOwner": self.vpcEndpointOwner,
            "vpcEndpointRegion": self.vpcEndpointRegion,
            "vpcEndpointState": self.vpcEndpointState.value if self.vpcEndpointState else None,
            "creationTimestamp": self.creationTimestamp.isoformat() if self.creationTimestamp else None,
            "dnsEntrySet": [dns.to_dict() for dns in self.dnsEntrySet],
            "gatewayLoadBalancerArnSet": self.gatewayLoadBalancerArnSet,
            "ipAddressType": self.ipAddressType.value if self.ipAddressType else None,
            "networkLoadBalancerArnSet": self.networkLoadBalancerArnSet,
            "serviceId": self.serviceId,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
        }


class VPCendpointsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.vpc_endpoints, self.state.connection_notifications, etc.

    def create_vpc_endpoint(self, params: dict) -> dict:
        import datetime

        # Validate required parameters
        vpc_id = params.get("VpcId")
        if not vpc_id:
            raise ValueError("VpcId is required")

        # Validate VPC existence
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # Extract parameters
        client_token = params.get("ClientToken")
        dns_options_param = params.get("DnsOptions", {})
        dry_run = params.get("DryRun", False)
        ip_address_type_str = params.get("IpAddressType")
        policy_document = params.get("PolicyDocument")
        private_dns_enabled = params.get("PrivateDnsEnabled")
        resource_configuration_arn = params.get("ResourceConfigurationArn")
        route_table_ids = []
        # RouteTableId.N keys: collect all keys starting with "RouteTableId."
        for key in params:
            if key.startswith("RouteTableId."):
                route_table_ids.append(params[key])
        security_group_ids = []
        for key in params:
            if key.startswith("SecurityGroupId."):
                security_group_ids.append(params[key])
        service_name = params.get("ServiceName")
        service_network_arn = params.get("ServiceNetworkArn")
        service_region = params.get("ServiceRegion")
        subnet_configurations = []
        for key in params:
            if key.startswith("SubnetConfiguration."):
                # SubnetConfiguration.N.Ipv4, SubnetConfiguration.N.Ipv6, SubnetConfiguration.N.SubnetId
                # Collect all SubnetConfiguration.N keys and parse them
                # We'll parse all SubnetConfiguration.N keys and group by N
                pass
        # Instead, parse SubnetConfiguration.N as list of dicts
        subnet_configuration_list = []
        # Find all keys starting with SubnetConfiguration.
        # They are like SubnetConfiguration.N.Ipv4, SubnetConfiguration.N.Ipv6, SubnetConfiguration.N.SubnetId
        # We need to group by N
        subnet_config_map = {}
        for key, value in params.items():
            if key.startswith("SubnetConfiguration."):
                # key format: SubnetConfiguration.N.Field
                parts = key.split(".")
                if len(parts) == 3:
                    _, index_str, field = parts
                    if index_str not in subnet_config_map:
                        subnet_config_map[index_str] = {}
                    subnet_config_map[index_str][field] = value
        for index in sorted(subnet_config_map.keys()):
            subnet_configuration_list.append(subnet_config_map[index])

        subnet_ids = []
        for key in params:
            if key.startswith("SubnetId."):
                subnet_ids.append(params[key])

        tag_specifications = []
        # TagSpecification.N.ResourceType and TagSpecification.N.Tags
        # Tags are TagSpecification.N.Tags.M.Key and TagSpecification.N.Tags.M.Value
        tag_spec_map = {}
        for key, value in params.items():
            if key.startswith("TagSpecification."):
                # key format: TagSpecification.N.ResourceType or TagSpecification.N.Tags.M.Key or TagSpecification.N.Tags.M.Value
                parts = key.split(".")
                if len(parts) >= 3:
                    _, n_str, rest = parts[0], parts[1], parts[2:]
                    if n_str not in tag_spec_map:
                        tag_spec_map[n_str] = {"ResourceType": None, "Tags": {}}
                    if rest[0] == "ResourceType":
                        tag_spec_map[n_str]["ResourceType"] = value
                    elif rest[0] == "Tags" and len(rest) == 3:
                        # Tags.M.Key or Tags.M.Value
                        tag_index = rest[1]
                        tag_field = rest[2]
                        if tag_index not in tag_spec_map[n_str]["Tags"]:
                            tag_spec_map[n_str]["Tags"][tag_index] = {"Key": None, "Value": None}
                        tag_spec_map[n_str]["Tags"][tag_index][tag_field] = value
        for n_str in sorted(tag_spec_map.keys()):
            resource_type = tag_spec_map[n_str]["ResourceType"]
            tags_dict = tag_spec_map[n_str]["Tags"]
            tags_list = []
            for m_str in sorted(tags_dict.keys()):
                tag = tags_dict[m_str]
                if tag["Key"] is not None:
                    tags_list.append(Tag(Key=tag["Key"], Value=tag["Value"] or ""))
            tag_specifications.append(TagSpecification(ResourceType=resource_type, Tags=tags_list))

        vpc_endpoint_type_str = params.get("VpcEndpointType", "Gateway")

        # Validate and convert enums
        from enum import Enum

        # Helper to convert string to enum member or None
        def to_enum(enum_class, value):
            if value is None:
                return None
            for member in enum_class:
                if member.name.lower() == value.lower():
                    return member
            raise ValueError(f"Invalid value '{value}' for enum {enum_class.__name__}")

        vpc_endpoint_type = None
        if vpc_endpoint_type_str:
            try:
                vpc_endpoint_type = to_enum(VpcEndpointType, vpc_endpoint_type_str)
            except Exception:
                raise ValueError(f"Invalid VpcEndpointType: {vpc_endpoint_type_str}")
        else:
            # Default Gateway
            vpc_endpoint_type = VpcEndpointType.Gateway

        ip_address_type = None
        if ip_address_type_str:
            try:
                ip_address_type = to_enum(DnsRecordIpType, ip_address_type_str)
            except Exception:
                raise ValueError(f"Invalid IpAddressType: {ip_address_type_str}")

        # Parse DnsOptionsSpecification
        dns_record_ip_type = None
        private_dns_only_for_inbound_resolver_endpoint = None
        private_dns_preference = None
        private_dns_specified_domains = []
        if dns_options_param:
            dns_record_ip_type_str = dns_options_param.get("DnsRecordIpType")
            if dns_record_ip_type_str:
                try:
                    dns_record_ip_type = to_enum(DnsRecordIpType, dns_record_ip_type_str)
                except Exception:
                    raise ValueError(f"Invalid DnsRecordIpType: {dns_record_ip_type_str}")
            private_dns_only_for_inbound_resolver_endpoint = dns_options_param.get("PrivateDnsOnlyForInboundResolverEndpoint")
            private_dns_preference_str = dns_options_param.get("PrivateDnsPreference")
            if private_dns_preference_str:
                try:
                    private_dns_preference = to_enum(PrivateDnsPreference, private_dns_preference_str)
                except Exception:
                    raise ValueError(f"Invalid PrivateDnsPreference: {private_dns_preference_str}")
            private_dns_specified_domains = dns_options_param.get("PrivateDnsSpecifiedDomains", [])

        dns_options = None
        if dns_options_param:
            dns_options = DnsOptionsSpecification(
                DnsRecordIpType=dns_record_ip_type,
                PrivateDnsOnlyForInboundResolverEndpoint=private_dns_only_for_inbound_resolver_endpoint,
                PrivateDnsPreference=private_dns_preference,
                PrivateDnsSpecifiedDomains=private_dns_specified_domains,
            )

        # Validate security groups for Interface endpoint
        group_set = []
        if vpc_endpoint_type == VpcEndpointType.Interface:
            if security_group_ids:
                for sg_id in security_group_ids:
                    # We do not validate security group existence here, but could be added
                    group_set.append(SecurityGroupIdentifier(groupId=sg_id, groupName=None))
            else:
                # Use default security group for the VPC if none specified
                # Find default security group in self.state.security_groups for this VPC
                default_sg = None
                for sg in self.state.security_groups.values():
                    if sg.groupName == "default" and sg.vpcId == vpc_id:
                        default_sg = sg
                        break
                if default_sg:
                    group_set.append(SecurityGroupIdentifier(groupId=default_sg.groupId, groupName=default_sg.groupName))
                else:
                    # No default security group found, leave empty
                    pass

        # Prepare subnetIdSet
        subnet_id_set = []
        if subnet_ids:
            subnet_id_set = subnet_ids
        else:
            # If no SubnetId.N specified, but SubnetConfiguration.N specified, use those SubnetIds
            for subnet_conf in subnet_configuration_list:
                if "SubnetId" in subnet_conf:
                    subnet_id_set.append(subnet_conf["SubnetId"])

        # Prepare ipv4PrefixSet and ipv6PrefixSet from SubnetConfiguration.N
        ipv4_prefix_set = []
        ipv6_prefix_set = []
        for subnet_conf in subnet_configuration_list:
            ipv4 = subnet_conf.get("Ipv4")
            ipv6 = subnet_conf.get("Ipv6")
            subnet_id = subnet_conf.get("SubnetId")
            if ipv4 or ipv6:
                if ipv4:
                    ipv4_prefix_set.append(SubnetIpPrefixes(ipPrefixSet=[ipv4], subnetId=subnet_id))
                if ipv6:
                    ipv6_prefix_set.append(SubnetIpPrefixes(ipPrefixSet=[ipv6], subnetId=subnet_id))

        # Prepare tagSet from tag_specifications for resource type "vpc-endpoint"
        tag_set = []
        for tag_spec in tag_specifications:
            if tag_spec.ResourceType and tag_spec.ResourceType.lower() == "vpc-endpoint":
                tag_set.extend(tag_spec.Tags)

        # Generate unique VPC endpoint ID
        vpc_endpoint_id = self.generate_unique_id(prefix="vpce-")

        # Creation timestamp
        creation_timestamp = datetime.datetime.utcnow()

        # Prepare dnsEntrySet for Interface endpoint
        dns_entry_set = []
        network_interface_id_set = []
        if vpc_endpoint_type == VpcEndpointType.Interface:
            # Create dummy network interface id
            eni_id = self.generate_unique_id(prefix="eni-")
            network_interface_id_set.append(eni_id)
            # Create DNS entries for the endpoint
            # For simplicity, create 3 DNS entries as in example 2
            # hostedZoneId is dummy string
            hosted_zone_id_1 = "Z7HUB22UULQXV"
            hosted_zone_id_2 = "Z2THV5YBYUN78V"
            dns_name_base = f"{vpc_endpoint_id}.elasticloadbalancing.{service_region or 'us-east-1'}.vpce.amazonaws.com"
            dns_entry_set.append(DnsEntry(dnsName=dns_name_base, hostedZoneId=hosted_zone_id_1))
            dns_entry_set.append(DnsEntry(dnsName=f"{vpc_endpoint_id}-{(service_region or 'us-east-1')[0]}a.{dns_name_base}", hostedZoneId=hosted_zone_id_1))
            dns_entry_set.append(DnsEntry(dnsName=f"elasticloadbalancing.{service_region or 'us-east-1'}.amazonaws.com", hostedZoneId=hosted_zone_id_2))

        # Prepare routeTableIdSet for Gateway endpoint
        route_table_id_set = []
        if vpc_endpoint_type == VpcEndpointType.Gateway:
            route_table_id_set = route_table_ids

        # Prepare state - LocalStack compatibility: Start pending then transition to available
        # CloudFormation polls for 'available' state before considering creation complete
        state = VpcEndpointState.PENDING

        # Prepare ownerId
        owner_id = self.get_owner_id()

        # requesterManaged default False
        requester_managed = False

        # Create VpcEndpoint object
        vpc_endpoint = VpcEndpoint(
            vpcEndpointId=vpc_endpoint_id,
            vpcId=vpc_id,
            vpcEndpointType=vpc_endpoint_type,
            serviceName=service_name,
            state=state,
            creationTimestamp=creation_timestamp,
            dnsEntrySet=dns_entry_set,
            dnsOptions=dns_options,
            failureReason=None,
            groupSet=group_set,
            ipAddressType=ip_address_type,
            ipv4PrefixSet=ipv4_prefix_set,
            ipv6PrefixSet=ipv6_prefix_set,
            lastError=None,
            networkInterfaceIdSet=network_interface_id_set,
            ownerId=owner_id,
            policyDocument=policy_document,
            privateDnsEnabled=private_dns_enabled,
            requesterManaged=requester_managed,
            resourceConfigurationArn=resource_configuration_arn,
            routeTableIdSet=route_table_id_set,
            serviceNetworkArn=service_network_arn,
            serviceRegion=service_region,
            subnetIdSet=subnet_id_set,
            tagSet=tag_set,
        )

        # Store in state
        self.state.vpc_endpoints[vpc_endpoint_id] = vpc_endpoint
        self.state.resources[vpc_endpoint_id] = vpc_endpoint

        # LocalStack compatibility: Transition from pending to available immediately
        # CloudFormation polls for 'available' state before considering creation complete
        vpc_endpoint.state = VpcEndpointState.AVAILABLE

        # Prepare response
        response = {
            "clientToken": client_token,
            "requestId": self.generate_request_id(),
            "vpcEndpoint": vpc_endpoint.to_dict(),
        }
        return response


    def create_vpc_endpoint_connection_notification(self, params: dict) -> dict:
        # Validate required parameters
        connection_events = []
        # Collect ConnectionEvents.N keys
        for key in params:
            if key.startswith("ConnectionEvents."):
                connection_events.append(params[key])
        if not connection_events:
            raise ValueError("ConnectionEvents.N is required")
        connection_notification_arn = params.get("ConnectionNotificationArn")
        if not connection_notification_arn:
            raise ValueError("ConnectionNotificationArn is required")

        client_token = params.get("ClientToken")
        dry_run = params.get("DryRun", False)
        service_id = params.get("ServiceId")
        vpc_endpoint_id = params.get("VpcEndpointId")

        # Validate VPC endpoint if specified
        if vpc_endpoint_id:
            vpc_endpoint = self.state.vpc_endpoints.get(vpc_endpoint_id)
            if not vpc_endpoint:
                raise ValueError(f"VPC Endpoint {vpc_endpoint_id} does not exist")
            # Only interface endpoints support connection notifications
            if vpc_endpoint.vpcEndpointType != VpcEndpointType.Interface:
                raise ValueError("Connection notifications can be created only for interface endpoints")

        # Generate unique connectionNotificationId
        connection_notification_id = self.generate_unique_id(prefix="vpce-nfn-")

        # Prepare connectionNotification object
        connection_notification = ConnectionNotification(
            connectionNotificationId=connection_notification_id,
            connectionNotificationArn=connection_notification_arn,
            connectionEvents=connection_events,
            connectionNotificationState=ConnectionNotificationState.Enabled,
            connectionNotificationType=ConnectionNotificationType.Topic,
            serviceId=service_id,
            serviceRegion=None,
            vpcEndpointId=vpc_endpoint_id,
        )

        # Store in state
        self.state.vpc_endpoint_connection_notifications[connection_notification_id] = connection_notification
        self.state.resources[connection_notification_id] = connection_notification

        # Prepare response
        response = {
            "clientToken": client_token,
            "connectionNotification": connection_notification.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_vpc_endpoint_connection_notifications(self, params: dict) -> dict:
        # Validate required parameters
        connection_notification_ids = []
        for key in params:
            if key.startswith("ConnectionNotificationId."):
                connection_notification_ids.append(params[key])
        if not connection_notification_ids:
            raise ValueError("ConnectionNotificationId.N is required")

        dry_run = params.get("DryRun", False)

        unsuccessful = []

        for cn_id in connection_notification_ids:
            if cn_id in self.state.vpc_endpoint_connection_notifications:
                # Delete notification
                del self.state.vpc_endpoint_connection_notifications[cn_id]
                if cn_id in self.state.resources:
                    del self.state.resources[cn_id]
            else:
                # Not found, add to unsuccessful
                error = UnsuccessfulItemError(code="InvalidConnectionNotificationId.NotFound", message=f"ConnectionNotificationId {cn_id} not found")
                unsuccessful.append(UnsuccessfulItem(error=error, resourceId=cn_id))

        response = {
            "requestId": self.generate_request_id(),
            "unsuccessful": [item.to_dict() for item in unsuccessful] if unsuccessful else [],
        }
        return response


    def delete_vpc_endpoints(self, params: dict) -> dict:
        # Validate required parameters
        vpc_endpoint_ids = []
        for key in params:
            if key.startswith("VpcEndpointId."):
                vpc_endpoint_ids.append(params[key])
        if not vpc_endpoint_ids:
            raise ValueError("VpcEndpointId.N is required")

        dry_run = params.get("DryRun", False)

        unsuccessful = []

        for vpce_id in vpc_endpoint_ids:
            vpc_endpoint = self.state.vpc_endpoints.get(vpce_id)
            if not vpc_endpoint:
                # LocalStack compatibility: Return success even if not found (idempotent delete)
                continue

            # LocalStack compatibility: Check current state for idempotent behavior
            if vpc_endpoint.state == VpcEndpointState.DELETED:
                # Already deleted, skip
                continue
            if vpc_endpoint.state == VpcEndpointState.DELETING:
                # Already deleting, mark as deleted
                vpc_endpoint.state = VpcEndpointState.DELETED
                continue

            # For Gateway Load Balancer endpoints, check if routes are deleted (not implemented here, assume allowed)
            # LocalStack compatibility: Transition to deleting then deleted state
            # Keep endpoint in state for CloudFormation polling
            vpc_endpoint.state = VpcEndpointState.DELETING
            vpc_endpoint.state = VpcEndpointState.DELETED

        response = {
            "requestId": self.generate_request_id(),
            "unsuccessful": [item.to_dict() for item in unsuccessful] if unsuccessful else [],
        }
        return response


    def describe_vpc_endpoint_associations(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        filters_param = []
        # Collect Filter.N.Name and Filter.N.Values.M
        filter_map = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    _, n_str, rest = parts[0], parts[1], parts[2:]
                    if n_str not in filter_map:
                        filter_map[n_str] = {"Name": None, "Values": []}
                    if rest[0] == "Name":
                        filter_map[n_str]["Name"] = value
                    elif rest[0] == "Values" and len(rest) == 2:
                        filter_map[n_str]["Values"].append(value)
        for n_str in sorted(filter_map.keys()):
            f = filter_map[n_str]
            filter_obj = Filter(Name=f["Name"], Values=f["Values"])
            filters_param.append(filter_obj)

        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        vpc_endpoint_ids = []
        for key in params:
            if key.startswith("VpcEndpointId."):
                vpc_endpoint_ids.append(params[key])

        # Collect all VpcEndpointAssociations from state
        all_associations = list(self.state.vpc_endpoint_associations.values())

        # Filter by VpcEndpointId if specified
        if vpc_endpoint_ids:
            all_associations = [assoc for assoc in all_associations if assoc.vpcEndpointId in vpc_endpoint_ids]

        # Apply filters
        def matches_filter(assoc: VpcEndpointAssociation, filter_obj: Filter) -> bool:
            if not filter_obj.Name:
                return True
            name = filter_obj.Name
            values = filter_obj.Values
            if name == "vpc-endpoint-id":
                return assoc.vpcEndpointId in values
            elif name == "associated-resource-accessibility":
                return assoc

    def describe_vpc_endpoint_connection_notifications(self, params: dict) -> dict:
        connection_notification_id = params.get("ConnectionNotificationId")
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect all connection notifications
        notifications = list(self.state.vpc_endpoint_connection_notifications.values())

        # Filter by ConnectionNotificationId if provided
        if connection_notification_id:
            notifications = [
                n for n in notifications if n.connectionNotificationId == connection_notification_id
            ]

        # Apply filters if provided
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            filtered = []
            for n in notifications:
                if name == "connection-notification-arn":
                    if n.connectionNotificationArn in values:
                        filtered.append(n)
                elif name == "connection-notification-id":
                    if n.connectionNotificationId in values:
                        filtered.append(n)
                elif name == "connection-notification-state":
                    if n.connectionNotificationState and n.connectionNotificationState.value in values:
                        filtered.append(n)
                elif name == "connection-notification-type":
                    if n.connectionNotificationType and n.connectionNotificationType.value in values:
                        filtered.append(n)
                elif name == "service-id":
                    if n.serviceId in values:
                        filtered.append(n)
                elif name == "vpc-endpoint-id":
                    if n.vpcEndpointId in values:
                        filtered.append(n)
            notifications = filtered

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            max_results = int(max_results)
            end_index = start_index + max_results
            page = notifications[start_index:end_index]
            new_next_token = str(end_index) if end_index < len(notifications) else None
        else:
            page = notifications[start_index:]
            new_next_token = None

        response = {
            "requestId": self.generate_request_id(),
            "connectionNotificationSet": [n.to_dict() for n in page],
            "nextToken": new_next_token,
        }
        return response


    def describe_vpc_endpoint_connections(self, params: dict) -> dict:
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        connections = list(self.state.vpc_endpoint_connections.values())

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            filtered = []
            for c in connections:
                if name == "ip-address-type":
                    if c.ipAddressType and c.ipAddressType.value in values:
                        filtered.append(c)
                elif name == "service-id":
                    if c.serviceId in values:
                        filtered.append(c)
                elif name == "vpc-endpoint-owner":
                    if c.vpcEndpointOwner in values:
                        filtered.append(c)
                elif name == "vpc-endpoint-region":
                    if c.vpcEndpointRegion in values:
                        filtered.append(c)
                elif name == "vpc-endpoint-state":
                    if c.vpcEndpointState and c.vpcEndpointState.value in values:
                        filtered.append(c)
                elif name == "vpc-endpoint-id":
                    if c.vpcEndpointId in values:
                        filtered.append(c)
            connections = filtered

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            max_results = int(max_results)
            end_index = start_index + max_results
            page = connections[start_index:end_index]
            new_next_token = str(end_index) if end_index < len(connections) else None
        else:
            page = connections[start_index:]
            new_next_token = None

        response = {
            "requestId": self.generate_request_id(),
            "vpcEndpointConnectionSet": [c.to_dict() for c in page],
            "nextToken": new_next_token,
        }
        return response


    def describe_vpc_endpoints(self, params: dict) -> dict:
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        vpc_endpoint_ids = params.get("VpcEndpointId", [])

        endpoints = list(self.state.vpc_endpoints.values())

        # Filter by VpcEndpointId if provided
        if vpc_endpoint_ids:
            endpoints = [ep for ep in endpoints if ep.vpcEndpointId in vpc_endpoint_ids]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            filtered = []
            for ep in endpoints:
                if name == "ip-address-type":
                    if ep.ipAddressType and ep.ipAddressType.value in values:
                        filtered.append(ep)
                elif name == "service-name":
                    if ep.serviceName in values:
                        filtered.append(ep)
                elif name == "service-region":
                    if ep.serviceRegion in values:
                        filtered.append(ep)
                elif name.startswith("tag:"):
                    tag_key = name[4:]
                    # Match if any tag with key=tag_key and value in values
                    if any(t.Key == tag_key and t.Value in values for t in ep.tagSet):
                        filtered.append(ep)
                elif name == "tag-key":
                    # Match if any tag with key in values
                    if any(t.Key in values for t in ep.tagSet):
                        filtered.append(ep)
                elif name == "vpc-id":
                    if ep.vpcId in values:
                        filtered.append(ep)
                elif name == "vpc-endpoint-id":
                    if ep.vpcEndpointId in values:
                        filtered.append(ep)
                elif name == "vpc-endpoint-state":
                    if ep.state and ep.state.value in values:
                        filtered.append(ep)
                elif name == "vpc-endpoint-type":
                    if ep.vpcEndpointType and ep.vpcEndpointType.value in values:
                        filtered.append(ep)
            endpoints = filtered

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            max_results = int(max_results)
            if max_results > 1000:
                max_results = 1000
            end_index = start_index + max_results
            page = endpoints[start_index:end_index]
            new_next_token = str(end_index) if end_index < len(endpoints) else None
        else:
            page = endpoints[start_index:]
            new_next_token = None

        response = {
            "requestId": self.generate_request_id(),
            "vpcEndpointSet": [ep.to_dict() for ep in page],
            "nextToken": new_next_token,
        }
        return response


    def modify_vpc_endpoint(self, params: dict) -> dict:
        vpc_endpoint_id = params.get("VpcEndpointId")
        if not vpc_endpoint_id:
            raise Exception("VpcEndpointId is required")

        endpoint = self.state.vpc_endpoints.get(vpc_endpoint_id)
        if not endpoint:
            raise Exception(f"VpcEndpoint {vpc_endpoint_id} not found")

        # AddRouteTableId.N
        add_route_table_ids = []
        for key, value in params.items():
            if key.startswith("AddRouteTableId."):
                add_route_table_ids.append(value)

        # RemoveRouteTableId.N
        remove_route_table_ids = []
        for key, value in params.items():
            if key.startswith("RemoveRouteTableId."):
                remove_route_table_ids.append(value)

        # AddSecurityGroupId.N
        add_security_group_ids = []
        for key, value in params.items():
            if key.startswith("AddSecurityGroupId."):
                add_security_group_ids.append(value)

        # RemoveSecurityGroupId.N
        remove_security_group_ids = []
        for key, value in params.items():
            if key.startswith("RemoveSecurityGroupId."):
                remove_security_group_ids.append(value)

        # AddSubnetId.N
        add_subnet_ids = []
        for key, value in params.items():
            if key.startswith("AddSubnetId."):
                add_subnet_ids.append(value)

        # RemoveSubnetId.N
        remove_subnet_ids = []
        for key, value in params.items():
            if key.startswith("RemoveSubnetId."):
                remove_subnet_ids.append(value)

        # SubnetConfiguration.N
        subnet_configurations = []
        # Collect keys like SubnetConfiguration.1.Ipv4, SubnetConfiguration.1.Ipv6, SubnetConfiguration.1.SubnetId
        subnet_config_map = {}
        for key, value in params.items():
            if key.startswith("SubnetConfiguration."):
                # key format: SubnetConfiguration.N.Field
                parts = key.split(".")
                if len(parts) == 3:
                    idx = parts[1]
                    field = parts[2]
                    if idx not in subnet_config_map:
                        subnet_config_map[idx] = {}
                    subnet_config_map[idx][field] = value
        for idx in sorted(subnet_config_map.keys()):
            conf = subnet_config_map[idx]
            subnet_configurations.append(conf)

        # DnsOptions
        dns_options_raw = params.get("DnsOptions")
        dns_options = None
        if dns_options_raw:
            # dns_options_raw is expected to be a dict with keys:
            # DnsRecordIpType, PrivateDnsOnlyForInboundResolverEndpoint, PrivateDnsPreference, PrivateDnsSpecifiedDomains
            dns_record_ip_type = dns_options_raw.get("DnsRecordIpType")
            private_dns_only = dns_options_raw.get("PrivateDnsOnlyForInboundResolverEndpoint")
            private_dns_preference = dns_options_raw.get("PrivateDnsPreference")
            private_dns_specified_domains = dns_options_raw.get("PrivateDnsSpecifiedDomains", [])
            # Construct DnsOptionsSpecification object
            dns_options = DnsOptionsSpecification(
                DnsRecordIpType=dns_record_ip_type,
                PrivateDnsOnlyForInboundResolverEndpoint=private_dns_only,
                PrivateDnsPreference=private_dns_preference,
                PrivateDnsSpecifiedDomains=private_dns_specified_domains,
            )

        # IpAddressType
        ip_address_type_raw = params.get("IpAddressType")
        ip_address_type = None
        if ip_address_type_raw:
            # Convert string to Enum if possible
            try:
                ip_address_type = DnsRecordIpType[ip_address_type_raw.upper()]
            except Exception:
                ip_address_type = None

        # PolicyDocument
        policy_document = params.get("PolicyDocument")

        # PrivateDnsEnabled
        private_dns_enabled = params.get("PrivateDnsEnabled")

        # ResetPolicy
        reset_policy = params.get("ResetPolicy", False)
        if isinstance(reset_policy, str):
            reset_policy = reset_policy.lower() == "true"

        # Update routeTableIdSet for Gateway endpoints
        if endpoint.vpcEndpointType in [VpcEndpointType.GATEWAY, VpcEndpointType.GATEWAY_LOAD_BALANCER]:
            # Add route tables
            for rtb in add_route_table_ids:
                if rtb not in endpoint.routeTableIdSet:
                    endpoint.routeTableIdSet.append(rtb)
            # Remove route tables
            for rtb in remove_route_table_ids:
                if rtb in endpoint.routeTableIdSet:
                    endpoint.routeTableIdSet.remove(rtb)

        # Update groupSet for Interface endpoints
        if endpoint.vpcEndpointType == VpcEndpointType.INTERFACE:
            # Add security groups
            for sg_id in add_security_group_ids:
                if not any(sg.groupId == sg_id for sg in endpoint.groupSet):
                    endpoint.groupSet.append(SecurityGroupIdentifier(groupId=sg_id, groupName=None))
            # Remove security groups
            for sg_id in remove_security_group_ids:
                endpoint.groupSet = [sg for sg in endpoint.groupSet if sg.groupId != sg_id]

        # Update subnetIdSet for Interface and Gateway Load Balancer endpoints
        if endpoint.vpcEndpointType in [VpcEndpointType.INTERFACE, VpcEndpointType.GATEWAY_LOAD_BALANCER]:
            # Add subnets
            for subnet_id in add_subnet_ids:
                if subnet_id not in endpoint.subnetIdSet:
                    endpoint.subnetIdSet.append(subnet_id)
            # Remove subnets
            for subnet_id in remove_subnet_ids:
                if subnet_id in endpoint.subnetIdSet:
                    endpoint.subnetIdSet.remove(subnet_id)

        # Apply subnet configurations - this is complex, we replace existing network interfaces with new ones with specified IPs
        # For simplicity, we do not simulate network interface replacement but update subnetIdSet accordingly
        for conf in subnet_configurations:
            subnet_id = conf.get("SubnetId")
            if subnet_id and subnet_id not in endpoint.subnetIdSet:
                endpoint.subnetIdSet.append(subnet_id)
            # We ignore Ipv4 and Ipv6 IP address assignment simulation here

        # Update DNS options if provided
        if dns_options:
            endpoint.dnsOptions = dns_options

        # Update IP address type if provided
        if ip_address_type:
            endpoint.ipAddressType = ip_address_type

        # Update policy document
        if reset_policy:
            # Reset to default policy (allow full access)
            endpoint.policyDocument = '{"Version":"2008-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"*","Resource":"*"}]}'
        elif policy_document is not None:
            endpoint.policyDocument = policy_document

        # Update private DNS enabled
        if private_dns_enabled is not None:
            endpoint.privateDnsEnabled = private_dns_enabled

        # Save updated endpoint back to state
        self.state.vpc_endpoints[vpc_endpoint_id] = endpoint

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def modify_vpc_endpoint_connection_notification(self, params: dict) -> dict:
        connection_notification_id = params.get("ConnectionNotificationId")
        if not connection_notification_id:
            raise Exception("ConnectionNotificationId is required")

        notification = self.state.vpc_endpoint_connection_notifications.get(connection_notification_id)
        if not notification:
            raise Exception(f"ConnectionNotification {connection_notification_id} not found")

        connection_events = []
        for key, value in params.items():
            if key.startswith("ConnectionEvents."):
                connection_events.append(value)

        connection_notification_arn = params.get("ConnectionNotificationArn")

        # Update fields if provided
        if connection_events:
            notification.connectionEvents = connection_events
        if connection_notification_arn is not None:
            notification.connectionNotificationArn = connection_notification_arn

        # Save updated notification back to state
        self.state.vpc_endpoint_connection_notifications[connection_notification_id] = notification

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class VPCendpointsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateVpcEndpoint", self.create_vpc_endpoint)
        self.register_action("CreateVpcEndpointConnectionNotification", self.create_vpc_endpoint_connection_notification)
        self.register_action("DeleteVpcEndpointConnectionNotifications", self.delete_vpc_endpoint_connection_notifications)
        self.register_action("DeleteVpcEndpoints", self.delete_vpc_endpoints)
        self.register_action("DescribeVpcEndpointAssociations", self.describe_vpc_endpoint_associations)
        self.register_action("DescribeVpcEndpointConnectionNotifications", self.describe_vpc_endpoint_connection_notifications)
        self.register_action("DescribeVpcEndpointConnections", self.describe_vpc_endpoint_connections)
        self.register_action("DescribeVpcEndpoints", self.describe_vpc_endpoints)
        self.register_action("ModifyVpcEndpoint", self.modify_vpc_endpoint)
        self.register_action("ModifyVpcEndpointConnectionNotification", self.modify_vpc_endpoint_connection_notification)

    def create_vpc_endpoint(self, params):
        return self.backend.create_vpc_endpoint(params)

    def create_vpc_endpoint_connection_notification(self, params):
        return self.backend.create_vpc_endpoint_connection_notification(params)

    def delete_vpc_endpoint_connection_notifications(self, params):
        return self.backend.delete_vpc_endpoint_connection_notifications(params)

    def delete_vpc_endpoints(self, params):
        return self.backend.delete_vpc_endpoints(params)

    def describe_vpc_endpoint_associations(self, params):
        return self.backend.describe_vpc_endpoint_associations(params)

    def describe_vpc_endpoint_connection_notifications(self, params):
        return self.backend.describe_vpc_endpoint_connection_notifications(params)

    def describe_vpc_endpoint_connections(self, params):
        return self.backend.describe_vpc_endpoint_connections(params)

    def describe_vpc_endpoints(self, params):
        return self.backend.describe_vpc_endpoints(params)

    def modify_vpc_endpoint(self, params):
        return self.backend.modify_vpc_endpoint(params)

    def modify_vpc_endpoint_connection_notification(self, params):
        return self.backend.modify_vpc_endpoint_connection_notification(params)
