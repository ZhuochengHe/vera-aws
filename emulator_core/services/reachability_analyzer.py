from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from emulator_core.backend import BaseBackend


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
class RequestFilterPortRange:
    FromPort: Optional[int] = None
    ToPort: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "FromPort": self.FromPort,
            "ToPort": self.ToPort,
        }


@dataclass
class PathRequestFilter:
    DestinationAddress: Optional[str] = None
    DestinationPortRange: Optional[RequestFilterPortRange] = None
    SourceAddress: Optional[str] = None
    SourcePortRange: Optional[RequestFilterPortRange] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DestinationAddress": self.DestinationAddress,
            "DestinationPortRange": self.DestinationPortRange.to_dict() if self.DestinationPortRange else None,
            "SourceAddress": self.SourceAddress,
            "SourcePortRange": self.SourcePortRange.to_dict() if self.SourcePortRange else None,
        }


@dataclass
class FilterPortRange:
    fromPort: Optional[int] = None
    toPort: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fromPort": self.fromPort,
            "toPort": self.toPort,
        }


@dataclass
class PathFilter:
    destinationAddress: Optional[str] = None
    destinationPortRange: Optional[FilterPortRange] = None
    sourceAddress: Optional[str] = None
    sourcePortRange: Optional[FilterPortRange] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destinationAddress": self.destinationAddress,
            "destinationPortRange": self.destinationPortRange.to_dict() if self.destinationPortRange else None,
            "sourceAddress": self.sourceAddress,
            "sourcePortRange": self.sourcePortRange.to_dict() if self.sourcePortRange else None,
        }


@dataclass
class PortRange:
    From: Optional[int] = None
    To: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "From": self.From,
            "To": self.To,
        }


@dataclass
class AnalysisComponent:
    arn: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "arn": self.arn,
            "id": self.id,
            "name": self.name,
        }


@dataclass
class AnalysisAclRule:
    cidr: Optional[str] = None
    egress: Optional[bool] = None
    portRange: Optional[PortRange] = None
    protocol: Optional[str] = None
    ruleAction: Optional[str] = None
    ruleNumber: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cidr": self.cidr,
            "egress": self.egress,
            "portRange": self.portRange.to_dict() if self.portRange else None,
            "protocol": self.protocol,
            "ruleAction": self.ruleAction,
            "ruleNumber": self.ruleNumber,
        }


@dataclass
class AnalysisLoadBalancerListener:
    instancePort: Optional[int] = None
    loadBalancerPort: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instancePort": self.instancePort,
            "loadBalancerPort": self.loadBalancerPort,
        }


@dataclass
class AnalysisLoadBalancerTarget:
    address: Optional[str] = None
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    instance: Optional[AnalysisComponent] = None
    port: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "instance": self.instance.to_dict() if self.instance else None,
            "port": self.port,
        }


@dataclass
class AnalysisRouteTableRoute:
    carrierGatewayId: Optional[str] = None
    coreNetworkArn: Optional[str] = None
    destinationCidr: Optional[str] = None
    destinationPrefixListId: Optional[str] = None
    egressOnlyInternetGatewayId: Optional[str] = None
    gatewayId: Optional[str] = None
    instanceId: Optional[str] = None
    localGatewayId: Optional[str] = None
    natGatewayId: Optional[str] = None
    networkInterfaceId: Optional[str] = None
    origin: Optional[str] = None
    state: Optional[str] = None
    transitGatewayId: Optional[str] = None
    vpcPeeringConnectionId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "carrierGatewayId": self.carrierGatewayId,
            "coreNetworkArn": self.coreNetworkArn,
            "destinationCidr": self.destinationCidr,
            "destinationPrefixListId": self.destinationPrefixListId,
            "egressOnlyInternetGatewayId": self.egressOnlyInternetGatewayId,
            "gatewayId": self.gatewayId,
            "instanceId": self.instanceId,
            "localGatewayId": self.localGatewayId,
            "natGatewayId": self.natGatewayId,
            "networkInterfaceId": self.networkInterfaceId,
            "origin": self.origin,
            "state": self.state,
            "transitGatewayId": self.transitGatewayId,
            "vpcPeeringConnectionId": self.vpcPeeringConnectionId,
        }


@dataclass
class AnalysisSecurityGroupRule:
    cidr: Optional[str] = None
    direction: Optional[str] = None
    portRange: Optional[PortRange] = None
    prefixListId: Optional[str] = None
    protocol: Optional[str] = None
    securityGroupId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cidr": self.cidr,
            "direction": self.direction,
            "portRange": self.portRange.to_dict() if self.portRange else None,
            "prefixListId": self.prefixListId,
            "protocol": self.protocol,
            "securityGroupId": self.securityGroupId,
        }


@dataclass
class FirewallStatefulRule:
    destinationPortSet: List[PortRange] = field(default_factory=list)
    destinationSet: List[str] = field(default_factory=list)
    direction: Optional[str] = None  # FORWARD or ANY
    protocol: Optional[str] = None
    ruleAction: Optional[str] = None  # pass, drop, alert
    ruleGroupArn: Optional[str] = None
    sourcePortSet: List[PortRange] = field(default_factory=list)
    sourceSet: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destinationPortSet": [p.to_dict() for p in self.destinationPortSet],
            "destinationSet": self.destinationSet,
            "direction": self.direction,
            "protocol": self.protocol,
            "ruleAction": self.ruleAction,
            "ruleGroupArn": self.ruleGroupArn,
            "sourcePortSet": [p.to_dict() for p in self.sourcePortSet],
            "sourceSet": self.sourceSet,
        }


@dataclass
class FirewallStatelessRule:
    destinationPortSet: List[PortRange] = field(default_factory=list)
    destinationSet: List[str] = field(default_factory=list)
    priority: Optional[int] = None  # -1 to 65535
    protocolSet: List[int] = field(default_factory=list)  # 0 to 255
    ruleAction: Optional[str] = None  # pass, drop, forward_to_site
    ruleGroupArn: Optional[str] = None
    sourcePortSet: List[PortRange] = field(default_factory=list)
    sourceSet: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destinationPortSet": [p.to_dict() for p in self.destinationPortSet],
            "destinationSet": self.destinationSet,
            "priority": self.priority,
            "protocolSet": self.protocolSet,
            "ruleAction": self.ruleAction,
            "ruleGroupArn": self.ruleGroupArn,
            "sourcePortSet": [p.to_dict() for p in self.sourcePortSet],
            "sourceSet": self.sourceSet,
        }


@dataclass
class AnalysisPacketHeader:
    destinationAddressSet: List[str] = field(default_factory=list)
    destinationPortRangeSet: List[PortRange] = field(default_factory=list)
    protocol: Optional[str] = None
    sourceAddressSet: List[str] = field(default_factory=list)
    sourcePortRangeSet: List[PortRange] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destinationAddressSet": self.destinationAddressSet,
            "destinationPortRangeSet": [p.to_dict() for p in self.destinationPortRangeSet],
            "protocol": self.protocol,
            "sourceAddressSet": self.sourceAddressSet,
            "sourcePortRangeSet": [p.to_dict() for p in self.sourcePortRangeSet],
        }


@dataclass
class AdditionalDetail:
    additionalDetailType: Optional[str] = None
    component: Optional[AnalysisComponent] = None
    loadBalancerSet: List[AnalysisComponent] = field(default_factory=list)
    ruleGroupRuleOptionsPairSet: List["RuleGroupRuleOptionsPair"] = field(default_factory=list)
    ruleGroupTypePairSet: List["RuleGroupTypePair"] = field(default_factory=list)
    ruleOptionSet: List["RuleOption"] = field(default_factory=list)
    serviceName: Optional[str] = None
    vpcEndpointService: Optional[AnalysisComponent] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "additionalDetailType": self.additionalDetailType,
            "component": self.component.to_dict() if self.component else None,
            "loadBalancerSet": [lb.to_dict() for lb in self.loadBalancerSet],
            "ruleGroupRuleOptionsPairSet": [pair.to_dict() for pair in self.ruleGroupRuleOptionsPairSet],
            "ruleGroupTypePairSet": [pair.to_dict() for pair in self.ruleGroupTypePairSet],
            "ruleOptionSet": [opt.to_dict() for opt in self.ruleOptionSet],
            "serviceName": self.serviceName,
            "vpcEndpointService": self.vpcEndpointService.to_dict() if self.vpcEndpointService else None,
        }


@dataclass
class RuleOption:
    keyword: Optional[str] = None
    settingSet: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "settingSet": self.settingSet,
        }


@dataclass
class RuleGroupRuleOptionsPair:
    ruleGroupArn: Optional[str] = None
    ruleOptionSet: List[RuleOption] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ruleGroupArn": self.ruleGroupArn,
            "ruleOptionSet": [opt.to_dict() for opt in self.ruleOptionSet],
        }


@dataclass
class RuleGroupTypePair:
    ruleGroupArn: Optional[str] = None
    ruleGroupType: Optional[str] = None  # Domain List or Suricata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ruleGroupArn": self.ruleGroupArn,
            "ruleGroupType": self.ruleGroupType,
        }


@dataclass
class PathComponent:
    aclRule: Optional[AnalysisAclRule] = None
    additionalDetailSet: List[AdditionalDetail] = field(default_factory=list)
    attachedTo: Optional[AnalysisComponent] = None
    component: Optional[AnalysisComponent] = None
    destinationVpc: Optional[AnalysisComponent] = None
    elasticLoadBalancerListener: Optional[AnalysisComponent] = None
    explanationCode: Optional[str] = None
    firewallStatefulRule: Optional[FirewallStatefulRule] = None
    firewallStatelessRule: Optional[FirewallStatelessRule] = None
    ingressRouteTable: Optional[AnalysisComponent] = None
    internetGateway: Optional[AnalysisComponent] = None
    loadBalancerArn: Optional[str] = None
    loadBalancerListenerPort: Optional[int] = None
    loadBalancerTarget: Optional[AnalysisLoadBalancerTarget] = None
    loadBalancerTargetGroup: Optional[AnalysisComponent] = None
    loadBalancerTargetGroupSet: List[AnalysisComponent] = field(default_factory=list)
    loadBalancerTargetPort: Optional[int] = None
    missingComponent: Optional[str] = None
    natGateway: Optional[AnalysisComponent] = None
    networkInterface: Optional[AnalysisComponent] = None
    packetField: Optional[str] = None
    port: Optional[int] = None
    portRangeSet: List[PortRange] = field(default_factory=list)
    prefixList: Optional[AnalysisComponent] = None
    protocolSet: List[str] = field(default_factory=list)
    routeTable: Optional[AnalysisComponent] = None
    routeTableRoute: Optional[AnalysisRouteTableRoute] = None
    securityGroup: Optional[AnalysisComponent] = None
    securityGroupRule: Optional[AnalysisSecurityGroupRule] = None
    securityGroupSet: List[AnalysisComponent] = field(default_factory=list)
    sourceVpc: Optional[AnalysisComponent] = None
    state: Optional[str] = None
    subnet: Optional[AnalysisComponent] = None
    subnetRouteTable: Optional[AnalysisComponent] = None
    transitGateway: Optional[AnalysisComponent] = None
    transitGatewayAttachment: Optional[AnalysisComponent] = None
    transitGatewayRouteTable: Optional[AnalysisComponent] = None
    transitGatewayRouteTableRoute: Optional["TransitGatewayRouteTableRoute"] = None
    vpc: Optional[AnalysisComponent] = None
    vpcEndpoint: Optional[AnalysisComponent] = None
    vpcPeeringConnection: Optional[AnalysisComponent] = None
    vpnConnection: Optional[AnalysisComponent] = None
    vpnGateway: Optional[AnalysisComponent] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aclRule": self.aclRule.to_dict() if self.aclRule else None,
            "additionalDetailSet": [ad.to_dict() for ad in self.additionalDetailSet],
            "attachedTo": self.attachedTo.to_dict() if self.attachedTo else None,
            "component": self.component.to_dict() if self.component else None,
            "destinationVpc": self.destinationVpc.to_dict() if self.destinationVpc else None,
            "elasticLoadBalancerListener": self.elasticLoadBalancerListener.to_dict() if self.elasticLoadBalancerListener else None,
            "explanationCode": self.explanationCode,
            "firewallStatefulRule": self.firewallStatefulRule.to_dict() if self.firewallStatefulRule else None,
            "firewallStatelessRule": self.firewallStatelessRule.to_dict() if self.firewallStatelessRule else None,
            "ingressRouteTable": self.ingressRouteTable.to_dict() if self.ingressRouteTable else None,
            "internetGateway": self.internetGateway.to_dict() if self.internetGateway else None,
            "loadBalancerArn": self.loadBalancerArn,
            "loadBalancerListenerPort": self.loadBalancerListenerPort,
            "loadBalancerTarget": self.loadBalancerTarget.to_dict() if self.loadBalancerTarget else None,
            "loadBalancerTargetGroup": self.loadBalancerTargetGroup.to_dict() if self.loadBalancerTargetGroup else None,
            "loadBalancerTargetGroupSet": [lg.to_dict() for lg in self.loadBalancerTargetGroupSet],
            "loadBalancerTargetPort": self.loadBalancerTargetPort,
            "missingComponent": self.missingComponent,
            "natGateway": self.natGateway.to_dict() if self.natGateway else None,
            "networkInterface": self.networkInterface.to_dict() if self.networkInterface else None,
            "packetField": self.packetField,
            "port": self.port,
            "portRangeSet": [pr.to_dict() for pr in self.portRangeSet],
            "prefixList": self.prefixList.to_dict() if self.prefixList else None,
            "protocolSet": self.protocolSet,
            "routeTable": self.routeTable.to_dict() if self.routeTable else None,
            "routeTableRoute": self.routeTableRoute.to_dict() if self.routeTableRoute else None,
            "securityGroup": self.securityGroup.to_dict() if self.securityGroup else None,
            "securityGroupRule": self.securityGroupRule.to_dict() if self.securityGroupRule else None,
            "securityGroupSet": [sg.to_dict() for sg in self.securityGroupSet],
            "sourceVpc": self.sourceVpc.to_dict() if self.sourceVpc else None,
            "state": self.state,
            "subnet": self.subnet.to_dict() if self.subnet else None,
            "subnetRouteTable": self.subnetRouteTable.to_dict() if self.subnetRouteTable else None,
            "transitGateway": self.transitGateway.to_dict() if self.transitGateway else None,
            "transitGatewayAttachment": self.transitGatewayAttachment.to_dict() if self.transitGatewayAttachment else None,
            "transitGatewayRouteTable": self.transitGatewayRouteTable.to_dict() if self.transitGatewayRouteTable else None,
            "transitGatewayRouteTableRoute": self.transitGatewayRouteTableRoute.to_dict() if self.transitGatewayRouteTableRoute else None,
            "vpc": self.vpc.to_dict() if self.vpc else None,
            "vpcEndpoint": self.vpcEndpoint.to_dict() if self.vpcEndpoint else None,
            "vpcPeeringConnection": self.vpcPeeringConnection.to_dict() if self.vpcPeeringConnection else None,
            "vpnConnection": self.vpnConnection.to_dict() if self.vpnConnection else None,
            "vpnGateway": self.vpnGateway.to_dict() if self.vpnGateway else None,
        }


@dataclass
class TransitGatewayRouteTableRoute:
    attachmentId: Optional[str] = None
    destinationCidr: Optional[str] = None
    prefixListId: Optional[str] = None
    resourceId: Optional[str] = None


class ReachabilityAnalyzerBackend(BaseBackend):
    def create_network_insights_path(self, params: dict) -> dict:
        import datetime

        client_token = params.get("ClientToken")
        if not client_token or not isinstance(client_token, str):
            raise ValueError("ClientToken is required and must be a string")

        protocol = params.get("Protocol")
        if protocol not in ("tcp", "udp"):
            raise ValueError("Protocol is required and must be 'tcp' or 'udp'")

        source = params.get("Source")
        if not source or not isinstance(source, str):
            raise ValueError("Source is required and must be a string")

        destination = params.get("Destination")
        destination_ip = params.get("DestinationIp")
        destination_port = params.get("DestinationPort")
        source_ip = params.get("SourceIp")

        # Validate IP addresses if provided
        def validate_ip(ip):
            import re
            if ip is None:
                return
            if not isinstance(ip, str):
                raise ValueError("IP address must be a string")
            pattern = r"^([0-9]{1,3}\.){3}[0-9]{1,3}$"
            if not re.match(pattern, ip):
                raise ValueError(f"IP address {ip} does not match pattern {pattern}")

        validate_ip(destination_ip)
        validate_ip(source_ip)

        # Validate ports if provided
        def validate_port(port):
            if port is None:
                return
            if not isinstance(port, int):
                raise ValueError("Port must be an integer")
            if port < 0 or port > 65535:
                raise ValueError("Port must be between 0 and 65535")

        validate_port(destination_port)

        # Validate FilterAtDestination and FilterAtSource
        def validate_port_range(port_range):
            if port_range is None:
                return
            if not isinstance(port_range, dict):
                raise ValueError("PortRange must be a dict")
            from_port = port_range.get("FromPort")
            to_port = port_range.get("ToPort")
            if from_port is not None:
                validate_port(from_port)
            if to_port is not None:
                validate_port(to_port)

        def validate_path_request_filter(filter_obj):
            if filter_obj is None:
                return
            if not isinstance(filter_obj, dict):
                raise ValueError("Filter must be a dict")
            # Validate IP addresses
            validate_ip(filter_obj.get("DestinationAddress"))
            validate_ip(filter_obj.get("SourceAddress"))
            # Validate port ranges
            validate_port_range(filter_obj.get("DestinationPortRange"))
            validate_port_range(filter_obj.get("SourcePortRange"))

        filter_at_destination = params.get("FilterAtDestination")
        filter_at_source = params.get("FilterAtSource")

        # If FilterAtDestination is specified, DestinationIp must not be specified
        if filter_at_destination and destination_ip:
            raise ValueError("Cannot specify both FilterAtDestination and DestinationIp")

        # If FilterAtSource is specified, cannot specify SourceIp or DestinationPort
        if filter_at_source and (source_ip or destination_port is not None):
            raise ValueError("Cannot specify FilterAtSource with SourceIp or DestinationPort")

        validate_path_request_filter(filter_at_destination)
        validate_path_request_filter(filter_at_source)

        # Validate TagSpecification.N
        tag_specifications = params.get("TagSpecification.N", [])
        if not isinstance(tag_specifications, list):
            raise ValueError("TagSpecification.N must be a list if provided")

        # Validate tags inside tag specifications
        for tag_spec in tag_specifications:
            if not isinstance(tag_spec, dict):
                raise ValueError("Each TagSpecification must be a dict")
            resource_type = tag_spec.get("ResourceType")
            if resource_type is not None and not isinstance(resource_type, str):
                raise ValueError("ResourceType in TagSpecification must be a string")
            tags = tag_spec.get("Tags", [])
            if not isinstance(tags, list):
                raise ValueError("Tags in TagSpecification must be a list")
            for tag in tags:
                if not isinstance(tag, dict):
                    raise ValueError("Each tag must be a dict")
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and not isinstance(key, str):
                    raise ValueError("Tag Key must be a string")
                if value is not None and not isinstance(value, str):
                    raise ValueError("Tag Value must be a string")

        # DryRun check (not implemented, just placeholder)
        dry_run = params.get("DryRun", False)
        if dry_run:
            # In real AWS, would check permissions and raise DryRunOperation or UnauthorizedOperation
            # Here, just return an error dict or raise exception
            raise Exception("DryRunOperation")

        # Generate unique ID and ARN for the path
        network_insights_path_id = self.generate_unique_id()
        owner_id = self.get_owner_id()
        region = getattr(self.state, "region", "us-east-1")
        network_insights_path_arn = f"arn:aws:ec2:{region}:{owner_id}:network-insights-path/{network_insights_path_id}"

        created_date = datetime.datetime.utcnow().isoformat() + "Z"

        # Build the path object to store
        path_obj = {
            "createdDate": created_date,
            "destination": destination,
            "destinationArn": None,
            "destinationIp": destination_ip,
            "destinationPort": destination_port,
            "filterAtDestination": None,
            "filterAtSource": None,
            "networkInsightsPathArn": network_insights_path_arn,
            "networkInsightsPathId": network_insights_path_id,
            "protocol": protocol,
            "source": source,
            "sourceArn": None,
            "sourceIp": source_ip,
            "tagSet": [],
        }

        # If destination is an ARN, set destinationArn and clear destination
        if destination and destination.startswith("arn:"):
            path_obj["destinationArn"] = destination
            path_obj["destination"] = None

        # If source is an ARN, set sourceArn and clear source
        if source and source.startswith("arn:"):
            path_obj["sourceArn"] = source
            path_obj["source"] = None

        # Convert FilterAtDestination to PathFilterobject format
        def convert_filter_to_path_filter(filter_obj):
            if not filter_obj:
                return None
            pf = {}
            if "DestinationAddress" in filter_obj:
                pf["destinationAddress"] = filter_obj["DestinationAddress"]
            if "SourceAddress" in filter_obj:
                pf["sourceAddress"] = filter_obj["SourceAddress"]
            if "DestinationPortRange" in filter_obj:
                dpr = filter_obj["DestinationPortRange"]
                pf["destinationPortRange"] = {}
                if "FromPort" in dpr:
                    pf["destinationPortRange"]["fromPort"] = dpr["FromPort"]
                if "ToPort" in dpr:
                    pf["destinationPortRange"]["toPort"] = dpr["ToPort"]
            if "SourcePortRange" in filter_obj:
                spr = filter_obj["SourcePortRange"]
                pf["sourcePortRange"] = {}
                if "FromPort" in spr:
                    pf["sourcePortRange"]["fromPort"] = spr["FromPort"]
                if "ToPort" in spr:
                    pf["sourcePortRange"]["toPort"] = spr["ToPort"]
            return pf

        path_obj["filterAtDestination"] = convert_filter_to_path_filter(filter_at_destination)
        path_obj["filterAtSource"] = convert_filter_to_path_filter(filter_at_source)

        # Convert tags from TagSpecification.N to tagSet (flatten all tags)
        tags = []
        for tag_spec in tag_specifications:
            for tag in tag_spec.get("Tags", []):
                tags.append({"Key": tag.get("Key"), "Value": tag.get("Value")})
        path_obj["tagSet"] = tags

        # Store the path object in the shared state dictionary
        self.state.reachability_analyzer[network_insights_path_id] = path_obj

        response = {
            "networkInsightsPath": path_obj,
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_network_insights_analysis(self, params: dict) -> dict:
        network_insights_analysis_id = params.get("NetworkInsightsAnalysisId")
        if not network_insights_analysis_id or not isinstance(network_insights_analysis_id, str):
            raise ValueError("NetworkInsightsAnalysisId is required and must be a string")

        dry_run = params.get("DryRun", False)
        if dry_run:
            raise Exception("DryRunOperation")

        # Remove the analysis from the shared state if exists
        if network_insights_analysis_id in self.state.reachability_analyzer:
            del self.state.reachability_analyzer[network_insights_analysis_id]
        else:
            # In real AWS, might raise an error if not found
            pass

        response = {
            "networkInsightsAnalysisId": network_insights_analysis_id,
            "requestId": self.generate_request_id(),
        }
        return response


    def delete_network_insights_path(self, params: dict) -> dict:
        network_insights_path_id = params.get("NetworkInsightsPathId")
        if not network_insights_path_id or not isinstance(network_insights_path_id, str):
            raise ValueError("NetworkInsightsPathId is required and must be a string")

        dry_run = params.get("DryRun", False)
        if dry_run:
            raise Exception("DryRunOperation")

        # Remove the path from the shared state if exists
        if network_insights_path_id in self.state.reachability_analyzer:
            del self.state.reachability_analyzer[network_insights_path_id]
        else:
            # In real AWS, might raise an error if not found
            pass

        response = {
            "networkInsightsPathId": network_insights_path_id,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_network_insights_analyses(self, params: dict) -> dict:
        # Extract filters and parameters
        analysis_end_time = params.get("AnalysisEndTime")
        analysis_start_time = params.get("AnalysisStartTime")
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        analysis_ids = params.get("NetworkInsightsAnalysisId.N", [])
        path_id = params.get("NetworkInsightsPathId")
        next_token = params.get("NextToken")

        if dry_run:
            raise Exception("DryRunOperation")

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
                raise ValueError("MaxResults must be an integer between 1 and 100")

        # Validate filters format
        if filters and not isinstance(filters, list):
            raise ValueError("Filter.N must be a list if provided")

        # Prepare list of analyses from state
        analyses = []
        for analysis_id, analysis in self.state.reachability_analyzer.items():
            # We assume that reachability_analyzer dict contains analyses and paths mixed,
            # but in real implementation, analyses and paths would be separate.
            # Here, we filter only analyses by checking if analysis has 'status' key (heuristic)
            if not isinstance(analysis, dict):
                continue
            if "status" not in analysis:
                continue
            # Filter by analysis_ids if provided
            if analysis_ids and analysis_id not in analysis_ids:
                continue
            # Filter by path_id if provided
            if path_id and analysis.get("networkInsightsPathId") != path_id:
                continue
            # Filter by AnalysisStartTime and AnalysisEndTime if provided
            # We assume analysis has 'startDate' and 'endDate' keys as ISO strings
            if analysis_start_time:
                if "startDate" not in analysis or analysis["startDate"] < analysis_start_time:
                    continue
            if analysis_end_time:
                if "endDate" not in analysis or analysis["endDate"] > analysis_end_time:
                    continue
            # Apply filters
            if filters:
                # Each filter is a dict with Name and Values
                match = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not name or not values:
                        continue
                    # Support only 'path-found' and 'status' filters as per doc
                    if name == "path-found":
                        # path-found is boolean, values are strings "true"/"false"
                        val_bool = analysis.get("networkPathFound")
                        if val_bool is None:
                            match = False
                            break
                        if str(val_bool).lower() not in [v.lower() for v in values]:
                            match = False
                            break
                    elif name == "status":
                        status = analysis.get("status")
                        if status is None or status not in values:
                            match = False
                            break
                    else:
                        # Unknown filter name, ignore or fail? Here ignore
                        pass
                if not match:
                    continue
            analyses.append(analysis)

        # Pagination support (simple)
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(analyses)
        if max_results is not None:
            end_index = min(start_index + max_results, len(analyses))

        next_token_out = None
        if end_index < len(analyses):
            next_token_out = str(end_index)

        response = {
            "networkInsightsAnalysisSet": analyses[start_index:end_index],
            "nextToken": next_token_out,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_network_insights_paths(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        path_ids = params.get("NetworkInsightsPathId.N", [])
        next_token = params.get("NextToken")

        if dry_run:
            raise Exception("DryRunOperation")

        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
                raise ValueError("MaxResults must be an integer between 1 and 100")

        if filters and not isinstance(filters, list):
            raise ValueError("Filter.N must be a list if provided")

        # Collect paths from state
        paths = []
        for path_id, path in self.state.reachability_analyzer.items():
            if not isinstance(path, dict):
                continue
            # Heuristic: paths have 'networkInsightsPathId' key
            if "networkInsightsPathId" not in path:
                continue
            if path_ids and path_id not in path_ids:
                continue

            # Apply filters
            if filters:
                match = True
                for f in filters:
                    name = f.get("Name")
                    values = f.get("Values", [])
                    if not name or not values:
                        continue
                    # Support filter names as per doc:
                    # destination, filter-at-source.source-address, filter-at-source.source-port-range,
                    # filter-at-source.destination-address, filter-at-source.destination-port-range,
                    # filter-at-destination.source-address, filter-at-destination.source-port-range,
                    # filter-at-destination.destination-address, filter-at-destination.destination-port-range,
                    # protocol, source
                    # We will check simple string equality for these filters
                    if name == "destination":
                        dest = path.get("destination") or path.get("destinationArn")
                        if dest not in values:
                            match = False
                            break
                    elif name == "protocol":
                        if path.get("protocol") not in values:
                            match = False
                            break
                    elif name == "source":
                        src = path.get("source") or path.get("sourceArn")
                        if src not in values:
                            match = False
                            break
                    else:
                        # For nested filters like filter-at-source.source-address etc,
                        # we parse the name and check accordingly
                        parts = name.split(".")
                        if len(parts) == 2 and parts[0].startswith("filter-at-source"):
                            filter_source = path.get("filterAtSource", {})
                            key = parts[1].replace("-", "")
                            val = filter_source.get(key)
                            if val is None:
                                match = False
                                break
                            # For port ranges, val is dict with fromPort and toPort, so check if any value matches
                            if isinstance(val, dict):
                                # Check if any port in range matches any value in values
                                from_port = val.get("fromPort")
                                to_port = val.get("toPort")
                                # values are strings, convert to int if possible
                                values_int = []
                                for v in values:
                                    try:
                                        values_int.append(int(v))
                                    except Exception:
                                        pass
                                if from_port is not None and to_port is not None:
                                    # Check if any value in values_int is in range
                                    if not any(from_port <= v <= to_port for v in values_int):
                                        match = False
                                        break
                                else:
                                    match = False
                                    break
                            else:
                                if val not in values:
                                    match = False
                                    break
                        elif len(parts) == 2 and parts[0].startswith("filter-at-destination"):
                            filter_dest = path.get("filterAtDestination", {})
                            key = parts[1].replace("-", "")
                            val = filter_dest.get(key)
                            if val is None:
                                match = False
                                break
                            if isinstance(val, dict):
                                from_port = val.get("fromPort")
                                to_port = val.get("toPort")
                                values_int = []
                                for v in values:
                                    try:
                                        values_int.append(int(v))
                                    except Exception:
                                        pass
                                if from_port is not None and to_port is not None:
                                    if not any(from_port <= v <= to_port for v in values_int):
                                        match = False
                                        break
                                else:
                                    match = False
                                    break
                            else:
                                if val not in values:
                                    match = False
                                    break
                        else:
                            # Unknown filter, ignore
                            pass
                if not match:
                    continue

            paths.append(path)

        # Pagination support
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(paths)
        if max_results is not None:
            end_index = min(start_index + max_results, len(paths))

        next_token_out = None
        if end_index < len(paths):
            next_token_out = str(end_index)

        response = {
            "networkInsightsPathSet": paths[start_index:end_index],
            "nextToken": next_token_out,
            "requestId": self.generate_request_id(),
        }
        return response

    def enable_reachability_analyzer_organization_sharing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)

        # DryRun check: simulate permission check
        if dry_run:
            # In a real implementation, check permissions here
            # For emulator, assume permission granted
            return {
                "ResponseMetadata": {
                    "RequestId": self.generate_request_id()
                },
                "Return": True,
                "__type": "DryRunOperation"
            }

        # This operation must be performed by the management account for the organization.
        # For emulator, assume current account is management account.
        # Set a flag in state to indicate organization sharing enabled
        self.state.reachability_analyzer["organization_sharing_enabled"] = True

        return {
            "RequestId": self.generate_request_id(),
            "ReturnValue": True,
        }


    def start_network_insights_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Required parameters
        client_token = params.get("ClientToken")
        network_insights_path_id = params.get("NetworkInsightsPathId")

        if not client_token:
            raise Exception("Missing required parameter ClientToken")
        if not network_insights_path_id:
            raise Exception("Missing required parameter NetworkInsightsPathId")

        dry_run = params.get("DryRun", False)

        if dry_run:
            # Simulate permission check
            return {
                "ResponseMetadata": {
                    "RequestId": self.generate_request_id()
                },
                "Return": True,
                "__type": "DryRunOperation"
            }

        # Validate AdditionalAccount.N (list of strings)
        additional_accounts = []
        for key, value in params.items():
            if key.startswith("AdditionalAccount."):
                additional_accounts.append(value)

        # Validate FilterInArn.N and FilterOutArn.N (list of strings)
        filter_in_arns = []
        filter_out_arns = []
        for key, value in params.items():
            if key.startswith("FilterInArn."):
                filter_in_arns.append(value)
            elif key.startswith("FilterOutArn."):
                filter_out_arns.append(value)

        # Validate TagSpecification.N (list of TagSpecification objects)
        tag_specifications = []
        for key, value in params.items():
            if key.startswith("TagSpecification."):
                tag_specifications.append(value)

        # Generate unique ID for the analysis
        analysis_id = self.generate_unique_id()
        analysis_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:network-insights-analysis/{analysis_id}"

        # Build a minimal networkInsightsAnalysis object for response
        network_insights_analysis = {
            "networkInsightsAnalysisId": analysis_id,
            "networkInsightsAnalysisArn": analysis_arn,
            "networkInsightsPathId": network_insights_path_id,
            "status": "running",
            "startDate": "2024-01-01T00:00:00Z",  # Placeholder timestamp
            "networkPathFound": False,
            "tagSet": [],
            "additionalAccountSet": additional_accounts,
            "filterInArnSet": filter_in_arns,
            "filterOutArnSet": filter_out_arns,
            "returnPathComponentSet": [],
            "forwardPathComponentSet": [],
            "explanationSet": [],
            "suggestedAccountSet": [],
            "warningMessage": None,
            "statusMessage": None,
        }

        # Store the analysis in state
        self.state.reachability_analyzer[analysis_id] = network_insights_analysis

        return {
            "networkInsightsAnalysis": network_insights_analysis,
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class ReachabilityAnalyzerGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateNetworkInsightsPath", self.create_network_insights_path)
        self.register_action("DeleteNetworkInsightsAnalysis", self.delete_network_insights_analysis)
        self.register_action("DeleteNetworkInsightsPath", self.delete_network_insights_path)
        self.register_action("DescribeNetworkInsightsAnalyses", self.describe_network_insights_analyses)
        self.register_action("DescribeNetworkInsightsPaths", self.describe_network_insights_paths)
        self.register_action("EnableReachabilityAnalyzerOrganizationSharing", self.enable_reachability_analyzer_organization_sharing)
        self.register_action("StartNetworkInsightsAnalysis", self.start_network_insights_analysis)

    def create_network_insights_path(self, params):
        return self.backend.create_network_insights_path(params)

    def delete_network_insights_analysis(self, params):
        return self.backend.delete_network_insights_analysis(params)

    def delete_network_insights_path(self, params):
        return self.backend.delete_network_insights_path(params)

    def describe_network_insights_analyses(self, params):
        return self.backend.describe_network_insights_analyses(params)

    def describe_network_insights_paths(self, params):
        return self.backend.describe_network_insights_paths(params)

    def enable_reachability_analyzer_organization_sharing(self, params):
        return self.backend.enable_reachability_analyzer_organization_sharing(params)

    def start_network_insights_analysis(self, params):
        return self.backend.start_network_insights_analysis(params)
