from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend


@dataclass
class Tag:
    Key: str
    Value: str


@dataclass
class TagSpecification:
    ResourceType: str
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class UserIdGroupPair:
    Description: Optional[str] = None
    GroupId: Optional[str] = None
    GroupName: Optional[str] = None
    PeeringStatus: Optional[str] = None
    UserId: Optional[str] = None
    VpcId: Optional[str] = None
    VpcPeeringConnectionId: Optional[str] = None


@dataclass
class IpRange:
    CidrIp: Optional[str] = None
    Description: Optional[str] = None


@dataclass
class Ipv6Range:
    CidrIpv6: Optional[str] = None
    Description: Optional[str] = None


@dataclass
class PrefixListId:
    Description: Optional[str] = None
    PrefixListId: Optional[str] = None


@dataclass
class IpPermission:
    FromPort: Optional[int] = None
    ToPort: Optional[int] = None
    IpProtocol: Optional[str] = None
    UserIdGroupPairs: List[UserIdGroupPair] = field(default_factory=list)
    IpRanges: List[IpRange] = field(default_factory=list)
    Ipv6Ranges: List[Ipv6Range] = field(default_factory=list)
    PrefixListIds: List[PrefixListId] = field(default_factory=list)


@dataclass
class ReferencedSecurityGroup:
    groupId: Optional[str] = None
    peeringStatus: Optional[str] = None
    userId: Optional[str] = None
    vpcId: Optional[str] = None
    vpcPeeringConnectionId: Optional[str] = None


@dataclass
class SecurityGroupRule:
    cidrIpv4: Optional[str] = None
    cidrIpv6: Optional[str] = None
    description: Optional[str] = None
    fromPort: Optional[int] = None
    groupId: Optional[str] = None
    groupOwnerId: Optional[str] = None
    ipProtocol: Optional[str] = None
    isEgress: Optional[bool] = None
    prefixListId: Optional[str] = None
    referencedGroupInfo: Optional[ReferencedSecurityGroup] = None
    securityGroupRuleArn: Optional[str] = None
    securityGroupRuleId: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    toPort: Optional[int] = None


@dataclass
class SecurityGroupRuleRequest:
    CidrIpv4: Optional[str] = None
    CidrIpv6: Optional[str] = None
    Description: Optional[str] = None
    FromPort: Optional[int] = None
    IpProtocol: Optional[str] = None
    PrefixListId: Optional[str] = None
    ReferencedGroupId: Optional[str] = None
    ToPort: Optional[int] = None


@dataclass
class SecurityGroupRuleUpdate:
    SecurityGroupRuleId: str
    SecurityGroupRule: Optional[SecurityGroupRuleRequest] = None


@dataclass
class SecurityGroupRuleDescription:
    Description: Optional[str] = None
    SecurityGroupRuleId: Optional[str] = None


@dataclass
class RevokedSecurityGroupRule:
    cidrIpv4: Optional[str] = None
    cidrIpv6: Optional[str] = None
    description: Optional[str] = None
    fromPort: Optional[int] = None
    groupId: Optional[str] = None
    ipProtocol: Optional[str] = None
    isEgress: Optional[bool] = None
    prefixListId: Optional[str] = None
    referencedGroupId: Optional[str] = None
    securityGroupRuleId: Optional[str] = None
    toPort: Optional[int] = None


@dataclass
class SecurityGroupReference:
    groupId: Optional[str] = None
    referencingVpcId: Optional[str] = None
    transitGatewayId: Optional[str] = None
    vpcPeeringConnectionId: Optional[str] = None


@dataclass
class SecurityGroupVpcAssociation:
    groupId: Optional[str] = None
    groupOwnerId: Optional[str] = None
    state: Optional[str] = None  # associating | associated | association-failed | disassociating | disassociated | disassociation-failed
    stateReason: Optional[str] = None
    vpcId: Optional[str] = None
    vpcOwnerId: Optional[str] = None


@dataclass
class StaleIpPermission:
    fromPort: Optional[int] = None
    groups: List[UserIdGroupPair] = field(default_factory=list)
    ipProtocol: Optional[str] = None
    ipRanges: List[str] = field(default_factory=list)
    prefixListIds: List[str] = field(default_factory=list)
    toPort: Optional[int] = None


@dataclass
class StaleSecurityGroup:
    description: Optional[str] = None
    groupId: Optional[str] = None
    groupName: Optional[str] = None
    staleIpPermissions: List[StaleIpPermission] = field(default_factory=list)
    staleIpPermissionsEgress: List[StaleIpPermission] = field(default_factory=list)
    vpcId: Optional[str] = None


@dataclass
class SecurityGroupForVpc:
    description: Optional[str] = None
    groupId: Optional[str] = None
    groupName: Optional[str] = None
    ownerId: Optional[str] = None
    primaryVpcId: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)


@dataclass
class SecurityGroup:
    groupDescription: Optional[str] = None
    groupId: Optional[str] = None
    groupName: Optional[str] = None
    ipPermissions: List[IpPermission] = field(default_factory=list)
    ipPermissionsEgress: List[IpPermission] = field(default_factory=list)
    ownerId: Optional[str] = None
    securityGroupArn: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)
    vpcId: Optional[str] = None


class SecuritygroupsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.security_groups or similar

    def _validate_port_range(self, from_port: int, to_port: int, protocol: str) -> None:
        """Validate port range for TCP/UDP protocols (0-65535)."""
        if protocol in ("tcp", "udp"):
            if from_port < 0 or from_port > 65535:
                raise Exception(f"InvalidParameterValue: Invalid value for FromPort. Must be between 0 and 65535.")
            if to_port < 0 or to_port > 65535:
                raise Exception(f"InvalidParameterValue: Invalid value for ToPort. Must be between 0 and 65535.")
            if from_port > to_port:
                raise Exception(f"InvalidParameterValue: FromPort ({from_port}) cannot be greater than ToPort ({to_port}).")

    def _validate_cidr_ip(self, cidr_ip: str) -> None:
        """Validate IPv4 CIDR format."""
        import re
        import ipaddress
        # CIDR pattern: x.x.x.x/prefix
        cidr_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$'
        match = re.match(cidr_pattern, cidr_ip)
        if not match:
            raise Exception(f"InvalidParameterValue: Value ({cidr_ip}) for parameter cidrIp is invalid. Invalid CIDR format.")
        # Validate octets
        octets = [int(match.group(i)) for i in range(1, 5)]
        for octet in octets:
            if octet > 255:
                raise Exception(f"InvalidParameterValue: Value ({cidr_ip}) for parameter cidrIp is invalid. Invalid IP address.")
        # Validate prefix
        prefix = int(match.group(5))
        if prefix > 32:
            raise Exception(f"InvalidParameterValue: Value ({cidr_ip}) for parameter cidrIp is invalid. Prefix must be between 0 and 32.")
        # Try to parse as network to catch other issues
        try:
            ipaddress.ip_network(cidr_ip, strict=False)
        except ValueError as e:
            raise Exception(f"InvalidParameterValue: Value ({cidr_ip}) for parameter cidrIp is invalid. {str(e)}")

    def _is_duplicate_rule(self, existing_rules: list, new_rule_attrs: dict, is_egress: bool) -> bool:
        """Check if a rule with the same attributes already exists."""
        for rule in existing_rules:
            if getattr(rule, "isEgress", False) != is_egress:
                continue
            # Compare key attributes
            if (getattr(rule, "ipProtocol", None) == new_rule_attrs.get("ip_protocol") and
                getattr(rule, "fromPort", None) == new_rule_attrs.get("from_port") and
                getattr(rule, "toPort", None) == new_rule_attrs.get("to_port") and
                getattr(rule, "cidrIpv4", None) == new_rule_attrs.get("cidr_ipv4") and
                getattr(rule, "cidrIpv6", None) == new_rule_attrs.get("cidr_ipv6") and
                getattr(rule, "prefixListId", None) == new_rule_attrs.get("prefix_list_id")):
                # Check referenced group info
                rule_ref = getattr(rule, "referencedGroupInfo", None)
                new_ref = new_rule_attrs.get("referenced_group_id")
                if rule_ref is None and new_ref is None:
                    return True
                if rule_ref and new_ref and getattr(rule_ref, "groupId", None) == new_ref:
                    return True
        return False

    def authorize_security_group_egress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_id = params.get("GroupId")
        ip_permissions = params.get("IpPermissions", [])
        dry_run = params.get("DryRun", False)

        if not group_id:
            raise Exception("Missing required parameter GroupId")

        security_group = self.state.security_groups.get(group_id)
        if not security_group:
            raise Exception(f"SecurityGroupNotFound: The security group '{group_id}' does not exist")

        if dry_run:
            # For simplicity, assume permission granted
            return {"requestId": self.generate_request_id(), "return": True}

        # Validate and add each ip permission as egress rule
        added_rules = []

        for perm in ip_permissions:
            ip_protocol = perm.get("IpProtocol")
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            user_id_group_pairs = perm.get("UserIdGroupPairs", [])
            ip_ranges = perm.get("IpRanges", [])
            ipv6_ranges = perm.get("Ipv6Ranges", [])
            prefix_list_ids = perm.get("PrefixListIds", [])

            # Validate protocol and ports according to AWS rules
            if ip_protocol is None:
                raise Exception("IpProtocol is required in IpPermissions")

            # For tcp, udp: from_port and to_port required
            if ip_protocol in ("tcp", "udp"):
                if from_port is None or to_port is None:
                    raise Exception("FromPort and ToPort are required for tcp/udp protocols")
                # Validate port range (0-65535)
                self._validate_port_range(from_port, to_port, ip_protocol)
            # For icmp, icmpv6: from_port and to_port can be -1 or specific type/code
            elif ip_protocol in ("icmp", "icmpv6"):
                if from_port is None:
                    from_port = -1
                if to_port is None:
                    to_port = -1
            # For -1 (all protocols) or other protocols, ports are ignored

            # Validate CIDR formats for IpRanges
            for ip_range in ip_ranges:
                cidr_ip = ip_range.get("CidrIp")
                if cidr_ip:
                    self._validate_cidr_ip(cidr_ip)

            # For each user_id_group_pair, ip_range, ipv6_range, prefix_list_id, create a rule
            # We create one SecurityGroupRule per combination

            # Helper to create tags from TagSpecification.N if present
            tag_specifications = params.get("TagSpecification.N", [])
            rule_tags = []
            for tag_spec in tag_specifications:
                if tag_spec.get("ResourceType") == "security-group-rule":
                    tags = tag_spec.get("Tags", [])
                    for tag in tags:
                        key = tag.get("Key")
                        value = tag.get("Value")
                        if key and not key.lower().startswith("aws:"):
                            rule_tags.append(Tag(Key=key, Value=value))

            # Add rules for UserIdGroupPairs
            for ugp in user_id_group_pairs:
                description = ugp.get("Description")
                group_id_ref = ugp.get("GroupId")
                group_name_ref = ugp.get("GroupName")
                peering_status = ugp.get("PeeringStatus")
                user_id_ref = ugp.get("UserId")
                vpc_id_ref = ugp.get("VpcId")
                vpc_peering_connection_id = ugp.get("VpcPeeringConnectionId")

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": None,
                    "cidr_ipv6": None,
                    "prefix_list_id": None,
                    "referenced_group_id": group_id_ref,
                }
                if self._is_duplicate_rule(security_group.ipPermissionsEgress, rule_attrs, is_egress=True):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                referenced_group_info = None
                if group_id_ref or group_name_ref:
                    referenced_group_info = ReferencedSecurityGroup(
                        groupId=group_id_ref,
                        peeringStatus=peering_status,
                        userId=user_id_ref,
                        vpcId=vpc_id_ref,
                        vpcPeeringConnectionId=vpc_peering_connection_id,
                    )

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"

                rule = SecurityGroupRule(
                    cidrIpv4=None,
                    cidrIpv6=None,
                    description=description,
                    fromPort=from_port,
                    groupId=group_id,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=True,
                    prefixListId=None,
                    referencedGroupInfo=referenced_group_info,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                # Add rule to security group egress rules
                security_group.ipPermissionsEgress.append(rule)
                added_rules.append(rule)

            # Add rules for IpRanges (IPv4)
            for ip_range in ip_ranges:
                cidr_ip = ip_range.get("CidrIp")
                description = ip_range.get("Description")
                if not cidr_ip:
                    continue

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": cidr_ip,
                    "cidr_ipv6": None,
                    "prefix_list_id": None,
                    "referenced_group_id": None,
                }
                if self._is_duplicate_rule(security_group.ipPermissionsEgress, rule_attrs, is_egress=True):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"
                rule = SecurityGroupRule(
                    cidrIpv4=cidr_ip,
                    cidrIpv6=None,
                    description=description,
                    fromPort=from_port,
                    groupId=group_id,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=True,
                    prefixListId=None,
                    referencedGroupInfo=None,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                security_group.ipPermissionsEgress.append(rule)
                added_rules.append(rule)

            # Add rules for Ipv6Ranges
            for ipv6_range in ipv6_ranges:
                cidr_ipv6 = ipv6_range.get("CidrIpv6")
                description = ipv6_range.get("Description")
                if not cidr_ipv6:
                    continue

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": None,
                    "cidr_ipv6": cidr_ipv6,
                    "prefix_list_id": None,
                    "referenced_group_id": None,
                }
                if self._is_duplicate_rule(security_group.ipPermissionsEgress, rule_attrs, is_egress=True):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"
                rule = SecurityGroupRule(
                    cidrIpv4=None,
                    cidrIpv6=cidr_ipv6,
                    description=description,
                    fromPort=from_port,
                    groupId=group_id,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=True,
                    prefixListId=None,
                    referencedGroupInfo=None,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                security_group.ipPermissionsEgress.append(rule)
                added_rules.append(rule)

            # Add rules for PrefixListIds
            for prefix_list in prefix_list_ids:
                prefix_list_id = prefix_list.get("PrefixListId")
                description = prefix_list.get("Description")
                if not prefix_list_id:
                    continue

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": None,
                    "cidr_ipv6": None,
                    "prefix_list_id": prefix_list_id,
                    "referenced_group_id": None,
                }
                if self._is_duplicate_rule(security_group.ipPermissionsEgress, rule_attrs, is_egress=True):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"
                rule = SecurityGroupRule(
                    cidrIpv4=None,
                    cidrIpv6=None,
                    description=description,
                    fromPort=from_port,
                    groupId=group_id,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=True,
                    prefixListId=prefix_list_id,
                    referencedGroupInfo=None,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                security_group.ipPermissionsEgress.append(rule)
                added_rules.append(rule)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
            "securityGroupRuleSet": added_rules,
        }


    def authorize_security_group_ingress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        ip_permissions = params.get("IpPermissions", [])
        dry_run = params.get("DryRun", False)

        # Determine security group by GroupId or GroupName
        security_group = None
        if group_id:
            security_group = self.state.security_groups.get(group_id)
        elif group_name:
            # Search for security group by name (case-insensitive)
            for sg in self.state.security_groups.values():
                if sg.groupName and sg.groupName.lower() == group_name.lower():
                    security_group = sg
                    break

        if not security_group:
            raise Exception("SecurityGroupNotFound: The specified security group does not exist")

        if dry_run:
            # For simplicity, assume permission granted
            return {"requestId": self.generate_request_id(), "return": True}

        added_rules = []

        for perm in ip_permissions:
            ip_protocol = perm.get("IpProtocol")
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            user_id_group_pairs = perm.get("UserIdGroupPairs", [])
            ip_ranges = perm.get("IpRanges", [])
            ipv6_ranges = perm.get("Ipv6Ranges", [])
            prefix_list_ids = perm.get("PrefixListIds", [])

            if ip_protocol is None:
                raise Exception("IpProtocol is required in IpPermissions")

            if ip_protocol in ("tcp", "udp"):
                if from_port is None or to_port is None:
                    raise Exception("FromPort and ToPort are required for tcp/udp protocols")
                # Validate port range (0-65535)
                self._validate_port_range(from_port, to_port, ip_protocol)
            elif ip_protocol in ("icmp", "icmpv6"):
                if from_port is None:
                    from_port = -1
                if to_port is None:
                    to_port = -1

            # Validate CIDR formats for IpRanges
            for ip_range in ip_ranges:
                cidr_ip = ip_range.get("CidrIp")
                if cidr_ip:
                    self._validate_cidr_ip(cidr_ip)

            tag_specifications = params.get("TagSpecification.N", [])
            rule_tags = []
            for tag_spec in tag_specifications:
                if tag_spec.get("ResourceType") == "security-group-rule":
                    tags = tag_spec.get("Tags", [])
                    for tag in tags:
                        key = tag.get("Key")
                        value = tag.get("Value")
                        if key and not key.lower().startswith("aws:"):
                            rule_tags.append(Tag(Key=key, Value=value))

            for ugp in user_id_group_pairs:
                description = ugp.get("Description")
                group_id_ref = ugp.get("GroupId")
                group_name_ref = ugp.get("GroupName")
                peering_status = ugp.get("PeeringStatus")
                user_id_ref = ugp.get("UserId")
                vpc_id_ref = ugp.get("VpcId")
                vpc_peering_connection_id = ugp.get("VpcPeeringConnectionId")

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": None,
                    "cidr_ipv6": None,
                    "prefix_list_id": None,
                    "referenced_group_id": group_id_ref,
                }
                if self._is_duplicate_rule(security_group.ipPermissions, rule_attrs, is_egress=False):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                referenced_group_info = None
                if group_id_ref or group_name_ref:
                    referenced_group_info = ReferencedSecurityGroup(
                        groupId=group_id_ref,
                        peeringStatus=peering_status,
                        userId=user_id_ref,
                        vpcId=vpc_id_ref,
                        vpcPeeringConnectionId=vpc_peering_connection_id,
                    )

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"

                rule = SecurityGroupRule(
                    cidrIpv4=None,
                    cidrIpv6=None,
                    description=description,
                    fromPort=from_port,
                    groupId=security_group.groupId,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=False,
                    prefixListId=None,
                    referencedGroupInfo=referenced_group_info,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                security_group.ipPermissions.append(rule)
                added_rules.append(rule)

            for ip_range in ip_ranges:
                cidr_ip = ip_range.get("CidrIp")
                description = ip_range.get("Description")
                if not cidr_ip:
                    continue

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": cidr_ip,
                    "cidr_ipv6": None,
                    "prefix_list_id": None,
                    "referenced_group_id": None,
                }
                if self._is_duplicate_rule(security_group.ipPermissions, rule_attrs, is_egress=False):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"
                rule = SecurityGroupRule(
                    cidrIpv4=cidr_ip,
                    cidrIpv6=None,
                    description=description,
                    fromPort=from_port,
                    groupId=security_group.groupId,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=False,
                    prefixListId=None,
                    referencedGroupInfo=None,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                security_group.ipPermissions.append(rule)
                added_rules.append(rule)

            for ipv6_range in ipv6_ranges:
                cidr_ipv6 = ipv6_range.get("CidrIpv6")
                description = ipv6_range.get("Description")
                if not cidr_ipv6:
                    continue

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": None,
                    "cidr_ipv6": cidr_ipv6,
                    "prefix_list_id": None,
                    "referenced_group_id": None,
                }
                if self._is_duplicate_rule(security_group.ipPermissions, rule_attrs, is_egress=False):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"
                rule = SecurityGroupRule(
                    cidrIpv4=None,
                    cidrIpv6=cidr_ipv6,
                    description=description,
                    fromPort=from_port,
                    groupId=security_group.groupId,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=False,
                    prefixListId=None,
                    referencedGroupInfo=None,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                security_group.ipPermissions.append(rule)
                added_rules.append(rule)

            for prefix_list in prefix_list_ids:
                prefix_list_id = prefix_list.get("PrefixListId")
                description = prefix_list.get("Description")
                if not prefix_list_id:
                    continue

                # Check for duplicate rule
                rule_attrs = {
                    "ip_protocol": ip_protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr_ipv4": None,
                    "cidr_ipv6": None,
                    "prefix_list_id": prefix_list_id,
                    "referenced_group_id": None,
                }
                if self._is_duplicate_rule(security_group.ipPermissions, rule_attrs, is_egress=False):
                    raise Exception(f"InvalidPermission.Duplicate: The specified rule already exists")

                rule_id = self.generate_unique_id()
                rule_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{rule_id}"
                rule = SecurityGroupRule(
                    cidrIpv4=None,
                    cidrIpv6=None,
                    description=description,
                    fromPort=from_port,
                    groupId=security_group.groupId,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol=ip_protocol,
                    isEgress=False,
                    prefixListId=prefix_list_id,
                    referencedGroupInfo=None,
                    securityGroupRuleArn=rule_arn,
                    securityGroupRuleId=rule_id,
                    tagSet=rule_tags.copy(),
                    toPort=to_port,
                )
                security_group.ipPermissions.append(rule)
                added_rules.append(rule)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
            "securityGroupRuleSet": added_rules,
        }


    def create_security_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_description = params.get("GroupDescription")
        group_name = params.get("GroupName")
        vpc_id = params.get("VpcId")
        dry_run = params.get("DryRun", False)
        tag_specifications = params.get("TagSpecification.N", [])

        if not group_description:
            raise Exception("Missing required parameter GroupDescription")
        if not group_name:
            raise Exception("Missing required parameter GroupName")

        # Validate GroupDescription length (max 255 characters)
        if len(group_description) > 255:
            raise Exception("InvalidParameterValue: GroupDescription exceeds maximum length of 255 characters")

        # Validate GroupName constraints
        if len(group_name) > 255:
            raise Exception("InvalidParameterValue: GroupName exceeds maximum length of 255 characters")
        if group_name.lower().startswith("sg-"):
            raise Exception("InvalidGroup.Duplicate: GroupName cannot start with 'sg-'")
        # GroupName must be alphanumeric characters, spaces, dots, dashes, and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9\s._-]+$', group_name):
            raise Exception("InvalidParameterValue: GroupName contains invalid characters")

        # Validate VPC exists if VpcId is provided
        if vpc_id:
            vpc = self.state.vpcs.get(vpc_id) if hasattr(self.state, "vpcs") else None
            if not vpc:
                raise Exception(f"InvalidVpcID.NotFound: The vpc ID '{vpc_id}' does not exist")

        # Check for duplicate group name in the same VPC
        for sg in self.state.security_groups.values():
            if sg.groupName and sg.groupName.lower() == group_name.lower():
                if (vpc_id is None and sg.vpcId is None) or (vpc_id == sg.vpcId):
                    raise Exception("InvalidGroup.Duplicate: Security group with this name already exists in the VPC")

        if dry_run:
            # For simplicity, assume permission granted
            return {"requestId": self.generate_request_id(), "return": True}

        # Generate new security group ID
        new_group_id = self.generate_unique_id()

        # Process tags from tag_specifications
        tags = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") == "security-group":
                for tag in tag_spec.get("Tags", []):
                    key = tag.get("Key")
                    value = tag.get("Value")
                    if key and not key.lower().startswith("aws:"):
                        tags.append(Tag(Key=key, Value=value))

        # Create security group object
        # VPC security groups get a default egress rule allowing all outbound traffic
        default_egress_rules = []
        if vpc_id:
            egress_rule_id = self.generate_unique_id()
            default_egress_rules = [
                SecurityGroupRule(
                    cidrIpv4="0.0.0.0/0",
                    cidrIpv6=None,
                    description=None,
                    fromPort=None,
                    groupId=new_group_id,
                    groupOwnerId=self.get_owner_id(),
                    ipProtocol="-1",
                    isEgress=True,
                    prefixListId=None,
                    referencedGroupInfo=None,
                    securityGroupRuleArn=f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group-rule/{egress_rule_id}",
                    securityGroupRuleId=egress_rule_id,
                    tagSet=[],
                    toPort=None,
                )
            ]

        security_group = SecurityGroup(
            groupDescription=group_description,
            groupId=new_group_id,
            groupName=group_name,
            ipPermissions=[],
            ipPermissionsEgress=default_egress_rules,
            ownerId=self.get_owner_id(),
            securityGroupArn=f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:security-group/{new_group_id}",
            tagSet=tags,
            vpcId=vpc_id,
        )

        # Store in state
        self.state.security_groups[new_group_id] = security_group
        self.state.resources[new_group_id] = security_group

        return {
            "groupId": new_group_id,
            "requestId": self.generate_request_id(),
            "securityGroupArn": security_group.securityGroupArn,
            "tagSet": tags,
        }


    def delete_security_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        dry_run = params.get("DryRun", False)

        # Determine security group by GroupId or GroupName
        security_group = None
        if group_id:
            security_group = self.state.security_groups.get(group_id)
        elif group_name:
            for sg in self.state.security_groups.values():
                if sg.groupName and sg.groupName.lower() == group_name.lower():
                    security_group = sg
                    break

        if not security_group:
            # LocalStack compatibility: Return success if not found (idempotent delete)
            return {"requestId": self.generate_request_id(), "return": True}

        if dry_run:
            # For simplicity, assume permission granted
            return {"requestId": self.generate_request_id(), "return": True}

        # Check for dependencies:
        # 1. Associated with instance or network interface (not modeled here, so skip)
        # 2. Referenced by another security group in the same VPC
        for sg in self.state.security_groups.values():
            if sg.groupId == security_group.groupId:
                continue
            # Check ingress rules referencing this group
            for rule in sg.ipPermissions:
                if rule.referencedGroupInfo and rule.referencedGroupInfo.groupId == security_group.groupId:
                    raise Exception("DependencyViolation: Security group is referenced by another security group")
            # Check egress rules referencing this group
            for rule in sg.ipPermissionsEgress:
                if rule.referencedGroupInfo and rule.referencedGroupInfo.groupId == security_group.groupId:
                    raise Exception("DependencyViolation: Security group is referenced by another security group")

        # 3. Has a VPC association (if VPC association means anything else, skip as no other resource modeled)

        # Delete security group
        del self.state.security_groups[security_group.groupId]
        if security_group.groupId in self.state.resources:
            del self.state.resources[security_group.groupId]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_security_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Describes the specified security groups or all of your security groups.
        """
        # Validate DryRun parameter
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        # Extract filters
        filters = []
        # Filters are passed as Filter.N.Name and Filter.N.Value.M
        # Collect filters from params keys
        filter_prefix = "Filter."
        filter_name_suffix = ".Name"
        filter_value_prefix = ".Value."
        filter_dict = {}
        for key, value in params.items():
            if key.startswith(filter_prefix) and key.endswith(filter_name_suffix):
                # Extract filter number
                filter_num = key[len(filter_prefix): -len(filter_name_suffix)]
                filter_dict.setdefault(filter_num, {})["Name"] = value
            elif key.startswith(filter_prefix):
                # Check if key is Filter.N.Value.M
                # Extract filter number and value index
                remainder = key[len(filter_prefix):]
                if ".Value." in remainder:
                    filter_num, value_index = remainder.split(".Value.", 1)
                    filter_dict.setdefault(filter_num, {}).setdefault("Values", []).append(value)

        for f in filter_dict.values():
            filters.append(f)

        # Extract GroupId.N and GroupName.N
        group_ids = []
        group_names = []
        for key, value in params.items():
            if key.startswith("GroupId."):
                group_ids.append(value)
            elif key.startswith("GroupName."):
                group_names.append(value)

        # Extract MaxResults and NextToken
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise ValueError("MaxResults must be between 5 and 1000")
            except Exception:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        next_token = params.get("NextToken")
        # next_token is a string token for pagination, we will ignore pagination for now (return all)

        # Prepare list of security groups to describe
        all_sgs = list(self.state.security_groups.values())

        # Helper to get attribute from SecurityGroup (works with both dataclass and dict)
        def get_sg_attr(sg, attr, default=None):
            if hasattr(sg, attr):
                return getattr(sg, attr, default)
            elif isinstance(sg, dict):
                return sg.get(attr, default)
            return default

        # Filter by group_ids if specified
        if group_ids:
            all_sgs = [sg for sg in all_sgs if get_sg_attr(sg, "groupId") in group_ids]

        # Filter by group_names if specified
        if group_names:
            all_sgs = [sg for sg in all_sgs if get_sg_attr(sg, "groupName") in group_names]

        # Apply filters
        def match_filter(sg, filter_obj: Dict[str, Any]) -> bool:
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # no filter or empty values means no filtering

            # Implement filter matching according to AWS docs
            # The filter names can be complex, e.g. ip-permission.protocol, group-id, tag:key, etc.

            # Helper to check if any value matches (supports wildcards)
            def any_match(val_list, target):
                import fnmatch
                if target is None:
                    return False
                target_str = str(target)
                for v in val_list:
                    v_str = str(v)
                    # Check for wildcard pattern
                    if '*' in v_str or '?' in v_str:
                        if fnmatch.fnmatch(target_str, v_str):
                            return True
                    elif v_str == target_str:
                        return True
                return False

            # Handle tag filters
            if name.startswith("tag:"):
                tag_key = name[4:]
                # Check if sg has tag with key tag_key and value in values
                tags = get_sg_attr(sg, "tagSet", []) or []
                for tag in tags:
                    tag_k = getattr(tag, "Key", None) if hasattr(tag, "Key") else tag.get("Key") if isinstance(tag, dict) else None
                    tag_v = getattr(tag, "Value", None) if hasattr(tag, "Value") else tag.get("Value") if isinstance(tag, dict) else None
                    if tag_k == tag_key and any_match(values, tag_v):
                        return True
                return False
            if name == "tag-key":
                # Check if sg has any tag with key in values
                tags = get_sg_attr(sg, "tagSet", []) or []
                for tag in tags:
                    tag_k = getattr(tag, "Key", None) if hasattr(tag, "Key") else tag.get("Key") if isinstance(tag, dict) else None
                    if any_match(values, tag_k):
                        return True
                return False

            # Other filters
            # group-id
            if name == "group-id":
                return any_match(values, get_sg_attr(sg, "groupId"))

            # group-name
            if name == "group-name":
                return any_match(values, get_sg_attr(sg, "groupName"))

            # description
            if name == "description":
                return any_match(values, get_sg_attr(sg, "groupDescription"))

            # owner-id
            if name == "owner-id":
                return any_match(values, get_sg_attr(sg, "ownerId"))

            # vpc-id
            if name == "vpc-id":
                return any_match(values, get_sg_attr(sg, "vpcId"))

            # ip-permission.* and egress.ip-permission.* filters
            # These filters apply to ipPermissions (ingress) and ipPermissionsEgress (egress)
            # We need to check if any rule matches the filter

            def ip_permission_match(ip_permissions, filter_name, filter_values):
                # filter_name is like ip-permission.protocol, ip-permission.from-port, etc.
                # or egress.ip-permission.protocol, etc.
                # We remove the prefix and check the attribute
                prefix = "ip-permission."
                if filter_name.startswith("egress.ip-permission."):
                    prefix = "egress.ip-permission."
                attr = filter_name[len(prefix):]

                for perm in (ip_permissions or []):
                    perm_get = lambda a, d=None: getattr(perm, a, d) if hasattr(perm, a) else perm.get(a, d) if isinstance(perm, dict) else d
                    # For group-id and group-name inside UserIdGroupPairs
                    if attr.startswith("group-id"):
                        # Check UserIdGroupPairs groupId
                        pairs = perm_get("UserIdGroupPairs", []) or []
                        for pair in pairs:
                            pair_get = lambda a, d=None: getattr(pair, a, d) if hasattr(pair, a) else pair.get(a, d) if isinstance(pair, dict) else d
                            if any_match(filter_values, pair_get("GroupId")):
                                return True
                        continue
                    if attr.startswith("group-name"):
                        pairs = perm_get("UserIdGroupPairs", []) or []
                        for pair in pairs:
                            pair_get = lambda a, d=None: getattr(pair, a, d) if hasattr(pair, a) else pair.get(a, d) if isinstance(pair, dict) else d
                            if any_match(filter_values, pair_get("GroupName")):
                                return True
                        continue
                    if attr.startswith("user-id"):
                        pairs = perm_get("UserIdGroupPairs", []) or []
                        for pair in pairs:
                            pair_get = lambda a, d=None: getattr(pair, a, d) if hasattr(pair, a) else pair.get(a, d) if isinstance(pair, dict) else d
                            if any_match(filter_values, pair_get("UserId")):
                                return True
                        continue
                    if attr == "cidr":
                        # This is ambiguous, but likely means ip-permission.cidr (IPv4)
                        ip_ranges = perm_get("IpRanges", []) or []
                        for ipr in ip_ranges:
                            ipr_get = lambda a, d=None: getattr(ipr, a, d) if hasattr(ipr, a) else ipr.get(a, d) if isinstance(ipr, dict) else d
                            if any_match(filter_values, ipr_get("CidrIp")):
                                return True
                        continue
                    if attr == "ipv6-cidr":
                        ipv6_ranges = perm_get("Ipv6Ranges", []) or []
                        for ipr in ipv6_ranges:
                            ipr_get = lambda a, d=None: getattr(ipr, a, d) if hasattr(ipr, a) else ipr.get(a, d) if isinstance(ipr, dict) else d
                            if any_match(filter_values, ipr_get("CidrIpv6")):
                                return True
                        continue
                    if attr == "prefix-list-id":
                        prefix_list_ids = perm_get("PrefixListIds", []) or []
                        for pl in prefix_list_ids:
                            pl_get = lambda a, d=None: getattr(pl, a, d) if hasattr(pl, a) else pl.get(a, d) if isinstance(pl, dict) else d
                            if any_match(filter_values, pl_get("PrefixListId")):
                                return True
                        continue
                    # For other attributes, direct match
                    val = perm_get(attr)
                    if val is not None:
                        # val can be int or string, convert to string for comparison
                        if any_match(filter_values, val):
                            return True
                return False

            # Check ingress ipPermissions
            if name.startswith("ip-permission."):
                if ip_permission_match(get_sg_attr(sg, "ipPermissions", []), name, values):
                    return True
                return False

            # Check egress ipPermissionsEgress
            if name.startswith("egress.ip-permission."):
                if ip_permission_match(get_sg_attr(sg, "ipPermissionsEgress", []), name, values):
                    return True
                return False

            # If filter name not recognized, ignore filter (return True)
            return True

        # Apply all filters: all filters must match (AND)
        filtered_sgs = []
        for sg in all_sgs:
            if all(match_filter(sg, f) for f in filters):
                filtered_sgs.append(sg)

        # Pagination: if max_results specified, slice the list
        # next_token is ignored for simplicity, always return all or max_results
        if max_results is not None:
            filtered_sgs = filtered_sgs[:max_results]
            # No next_token support implemented, so always None
            next_token_out = None
        else:
            next_token_out = None

        # Compose response
        response = {
            "requestId": self.generate_request_id(),
            "securityGroupInfo": filtered_sgs,
            "nextToken": next_token_out,
        }
        return response

    def describe_security_group_rules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Describes the specified security group rules or all rules for a security group.
        """
        # Extract SecurityGroupRuleId.N
        security_group_rule_ids = []
        for key, value in params.items():
            if key.startswith("SecurityGroupRuleId."):
                security_group_rule_ids.append(value)

        # Extract GroupId - required if no rule IDs specified
        group_id = params.get("GroupId")

        # Extract Filters
        filters = []
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter.") and ".Name" in key:
                filter_num = key.split(".")[1]
                filter_dict.setdefault(filter_num, {})["Name"] = value
            elif key.startswith("Filter.") and ".Value." in key:
                parts = key.split(".")
                filter_num = parts[1]
                filter_dict.setdefault(filter_num, {}).setdefault("Values", []).append(value)
        for f in filter_dict.values():
            filters.append(f)
            # If "group-id" filter is specified, use it as the GroupId
            if f.get("Name") == "group-id" and not group_id:
                values = f.get("Values", [])
                if values:
                    group_id = values[0]

        # Extract pagination
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect all rules
        all_rules = []

        if security_group_rule_ids:
            # Find rules by ID across all security groups
            for sg in self.state.security_groups.values():
                for rule in getattr(sg, "ipPermissions", []) or []:
                    rule_id = getattr(rule, "securityGroupRuleId", None)
                    if rule_id in security_group_rule_ids:
                        all_rules.append(rule)
                for rule in getattr(sg, "ipPermissionsEgress", []) or []:
                    rule_id = getattr(rule, "securityGroupRuleId", None)
                    if rule_id in security_group_rule_ids:
                        all_rules.append(rule)
        elif group_id:
            # Find rules for specific group
            sg = self.state.security_groups.get(group_id)
            if sg:
                for rule in getattr(sg, "ipPermissions", []) or []:
                    all_rules.append(rule)
                for rule in getattr(sg, "ipPermissionsEgress", []) or []:
                    all_rules.append(rule)
            # If group not found, return empty list (matches LocalStack behavior)
        elif filters:
            # If only filters are provided, search all security groups
            for sg in self.state.security_groups.values():
                for rule in getattr(sg, "ipPermissions", []) or []:
                    all_rules.append(rule)
                for rule in getattr(sg, "ipPermissionsEgress", []) or []:
                    all_rules.append(rule)
        else:
            raise Exception("MissingParameter: You must specify either GroupId or SecurityGroupRuleId")

        # Apply filters
        def match_filter(rule, f):
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                return True
            if name == "group-id":
                return getattr(rule, "groupId", None) in values
            if name == "security-group-rule-id":
                return getattr(rule, "securityGroupRuleId", None) in values
            return True  # Unknown filter, ignore

        filtered_rules = [r for r in all_rules if all(match_filter(r, f) for f in filters)]

        # Pagination
        if max_results:
            try:
                max_results = int(max_results)
                filtered_rules = filtered_rules[:max_results]
            except:
                pass

        # Format response
        return {
            "requestId": self.generate_request_id(),
            "securityGroupRuleSet": filtered_rules,
        }


    def modify_security_group_rules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifies the rules of a security group.
        """
        # Validate DryRun parameter
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        group_id = params.get("GroupId")
        if not group_id:
            raise ValueError("GroupId is required")

        # Get the security group
        sg = self.state.security_groups.get(group_id)
        if not sg:
            raise ValueError(f"Security group {group_id} not found")

        # SecurityGroupRule.N is an array of SecurityGroupRuleUpdate objects
        # Parse SecurityGroupRule.N from params
        # The keys are like SecurityGroupRule.1.SecurityGroupRuleId, SecurityGroupRule.1.SecurityGroupRule.CidrIpv4, etc.
        # We need to collect all SecurityGroupRule.N entries
        rule_updates = {}
        for key, value in params.items():
            if key.startswith("SecurityGroupRule."):
                # Extract index and field
                remainder = key[len("SecurityGroupRule."):]
                if "." in remainder:
                    idx, field = remainder.split(".", 1)
                    rule_updates.setdefault(idx, {})[field] = value
                else:
                    # Should not happen, ignore
                    pass

        # Validate that at least one rule update is present
        if not rule_updates:
            raise ValueError("SecurityGroupRule.N is required and must have at least one entry")

        # For each rule update, apply changes
        # Each rule update must have SecurityGroupRuleId
        # SecurityGroupRule is optional, if present, contains fields to update
        # We will find the rule by SecurityGroupRuleId in ingress and egress rules and update accordingly

        # Helper to find rule by rule id in ipPermissions and ipPermissionsEgress
        def find_rule_by_id(sg_obj, rule_id):
            for perm in sg_obj.get("ipPermissions", []):
                if perm.get("securityGroupRuleId") == rule_id:
                    return perm, "ingress"
            for perm in sg_obj.get("ipPermissionsEgress", []):
                if perm.get("securityGroupRuleId") == rule_id:
                    return perm, "egress"
            return None, None

        for idx, update in rule_updates.items():
            rule_id = update.get("SecurityGroupRuleId")
            if not rule_id:
                raise ValueError(f"SecurityGroupRuleId is required for SecurityGroupRule.{idx}")

            rule_obj, direction = find_rule_by_id(sg, rule_id)
            if not rule_obj:
                raise ValueError(f"Security group rule {rule_id} not found in security group {group_id}")

            # If SecurityGroupRule field present, update fields accordingly
            rule_fields = update.get("SecurityGroupRule")
            if rule_fields:
                # rule_fields is a dict with keys like CidrIpv4, CidrIpv6, Description, FromPort, IpProtocol, PrefixListId, ReferencedGroupId, ToPort
                # Update the rule_obj accordingly
                # Note: The rule_obj structure may have nested lists for IpRanges, Ipv6Ranges, UserIdGroupPairs, PrefixListIds
                # We will update the description and CIDRs if present, and other fields

                # Update IpProtocol
                if "IpProtocol" in rule_fields:
                    rule_obj["ipProtocol"] = rule_fields["IpProtocol"]

                # Update FromPort
                if "FromPort" in rule_fields:
                    try:
                        rule_obj["fromPort"] = int(rule_fields["FromPort"])
                    except Exception:
                        raise ValueError("FromPort must be an integer")

                # Update ToPort
                if "ToPort" in rule_fields:
                    try:
                        rule_obj["toPort"] = int(rule_fields["ToPort"])
                    except Exception:
                        raise ValueError("ToPort must be an integer")

                # Update Description and CIDRs in IpRanges (IPv4)
                cidr_ipv4 = rule_fields.get("CidrIpv4")
                description = rule_fields.get("Description")
                if cidr_ipv4 is not None:
                    # Find matching IpRange with this CIDR and update description or add new
                    ip_ranges = rule_obj.get("IpRanges", [])
                    found = False
                    for ipr in ip_ranges:
                        if ipr.get("CidrIp") == cidr_ipv4:
                            if description is not None:
                                ipr["Description"] = description
                            found = True
                            break
                    if not found:
                        # Add new IpRange entry
                        new_ipr = {"CidrIp": cidr_ipv4}
                        if description is not None:
                            new_ipr["Description"] = description
                        ip_ranges.append(new_ipr)
                        rule_obj["IpRanges"] = ip_ranges

                # Update Description and CIDRs in Ipv6Ranges (IPv6)
                cidr_ipv6 = rule_fields.get("CidrIpv6")
                if cidr_ipv6 is not None:
                    ipv6_ranges = rule_obj.get("Ipv6Ranges", [])
                    found = False
                    for ipr in ipv6_ranges:
                        if ipr.get("CidrIpv6") == cidr_ipv6:
                            if description is not None:
                                ipr["Description"] = description
                            found = True
                            break
                    if not found:
                        new_ipr = {"CidrIpv6": cidr_ipv6}
                        if description is not None:
                            new_ipr["Description"] = description
                        ipv6_ranges.append(new_ipr)
                        rule_obj["Ipv6Ranges"] = ipv6_ranges

                # Update Description and PrefixListIds
                prefix_list_id = rule_fields.get("PrefixListId")
                if prefix_list_id is not None:
                    prefix_list_ids = rule_obj.get("PrefixListIds", [])
                    found = False
                    for pl in prefix_list_ids:
                        if pl.get("PrefixListId") == prefix_list_id:
                            if description is not None:
                                pl["Description"] = description
                            found = True
                            break
                    if not found:
                        new_pl = {"PrefixListId": prefix_list_id}
                        if description is not None:
                            new_pl["Description"] = description
                        prefix_list_ids.append(new_pl)
                        rule_obj["PrefixListIds"] = prefix_list_ids

                # Update ReferencedGroupId in UserIdGroupPairs
                referenced_group_id = rule_fields.get("ReferencedGroupId")
                if referenced_group_id is not None:
                    user_id_group_pairs = rule_obj.get("UserIdGroupPairs", [])
                    # We assume only one pair to update or add
                    if user_id_group_pairs:
                        # Update first pair's GroupId
                        user_id_group_pairs[0]["GroupId"] = referenced_group_id
                        if description is not None:
                            user_id_group_pairs[0]["Description"] = description
                    else:
                        new_pair = {"GroupId": referenced_group_id}
                        if description is not None:
                            new_pair["Description"] = description
                        user_id_group_pairs.append(new_pair)
                    rule_obj["UserIdGroupPairs"] = user_id_group_pairs

                # Update Description if no CIDR or other fields specified
                if description is not None and cidr_ipv4 is None and cidr_ipv6 is None and prefix_list_id is None and referenced_group_id is None:
                    # Update description at rule level if exists
                    rule_obj["Description"] = description

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def revoke_security_group_egress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Removes the specified outbound (egress) rules from the specified security group.
        """
        # Validate DryRun parameter
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ValueError("DryRun must be a boolean if specified")

        group_id = params.get("GroupId")
        if not group_id:
            raise ValueError("GroupId is required")

        sg = self.state.security_groups.get(group_id)
        if not sg:
            raise ValueError(f"Security group {group_id} not found")

        # We can specify rules by SecurityGroupRuleId.N or by IpPermissions.N
        # Parse SecurityGroupRuleId.N
        rule_ids = []
        for key, value in params.items():
            if key.startswith("SecurityGroupRuleId."):
                rule_ids.append(value)

        # Parse IpPermissions.N
        ip_permissions = {}
        for key, value in params.items():
            if key.startswith("IpPermissions."):
                # Format: IpPermissions.N.Field or IpPermissions.N.SubField.M.Field
                remainder = key[len("IpPermissions."):]
                parts = remainder.split(".")
                if len(parts) >= 2:
                    idx = parts[0]
                    field = parts[1]
                    if idx not in ip_permissions:
                        ip_permissions[idx] = {}
                    if field not in ip_permissions[idx]:
                        ip_permissions[idx][field] = value
                    # Handle nested fields like IpPermissions.N.IpRanges.M.CidrIp
                    if len(parts) > 2:
                        # Nested fields
                        # e.g. IpPermissions.1.IpRanges.1.CidrIp
                        # We will parse nested dicts accordingly
                        # Build nested structure
                        current = ip_permissions[idx]
                        for p in parts[1:-1]:
                            if p.isdigit():
                                p = int(p)
                            if p not in current:
                                current[p] = {}
                            current = current[p]
                        current[parts[-1]] = value

        # We will remove matching rules from ipPermissionsEgress list in sg
        revoked_rules = []
        unknown_ip_permission_set = []

        # Helper to match a rule with an ipPermission spec
        def ip_permission_matches(rule, ip_perm_spec):
            # Match IpProtocol
            if "IpProtocol" in ip_perm_spec:
                if str(rule.get("ipProtocol")) != str(ip_perm_spec["IpProtocol"]):
                    return False
            # Match FromPort
            if "FromPort" in ip_perm_spec:
                try:
                    if int(rule.get("fromPort", -9999)) != int(ip_perm_spec["FromPort"]):
                        return False
                except Exception:
                    return False
            # Match ToPort
            if "ToPort" in ip_perm_spec:
                try:
                    if int(rule.get("toPort", -9999)) != int(ip_perm_spec["ToPort"]):
                        return False
                except Exception:
                    return False
            # Match IpRanges
            if "IpRanges" in ip_perm_spec:
                # Check if any IpRange matches
                pass # Placeholder for complex matching logic
            return True

    def update_security_group_rule_descriptions_ingress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        ip_permissions = params.get("IpPermissions.N", [])
        rule_descriptions = params.get("SecurityGroupRuleDescription.N", [])

        # Validate that either GroupId or GroupName is provided
        if not group_id and not group_name:
            raise Exception("InvalidParameterCombination: You must specify either GroupId or GroupName")

        # Find the security group
        security_group = None
        if group_id:
            security_group = self.state.security_groups.get(group_id)
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")
        else:
            # GroupName specified, find in default VPC only
            for sg in self.state.security_groups.values():
                if sg.get("group_name") == group_name and (not sg.get("vpc_id") or sg.get("vpc_id") == "default"):
                    security_group = sg
                    break
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_name}' does not exist")

        # Helper to canonicalize CIDR blocks (IPv4 and IPv6)
        def canonicalize_cidr(cidr: str) -> str:
            # For simplicity, just return the input. Real implementation would canonicalize.
            return cidr

        # Helper to find matching ingress rule in security group
        def find_matching_ingress_rule(sg, perm):
            # Match by ipProtocol, fromPort, toPort, and referenced groups or CIDRs
            for rule in sg.get("ingress_rules", []):
                if rule.get("ip_protocol") != perm.get("IpProtocol"):
                    continue
                if rule.get("from_port") != perm.get("FromPort"):
                    continue
                if rule.get("to_port") != perm.get("ToPort"):
                    continue

                # Check UserIdGroupPairs match
                perm_pairs = perm.get("UserIdGroupPairs", [])
                rule_pairs = rule.get("user_id_group_pairs", [])
                if len(perm_pairs) != len(rule_pairs):
                    continue
                pairs_match = True
                for p_pair in perm_pairs:
                    found = False
                    for r_pair in rule_pairs:
                        if p_pair.get("GroupId") == r_pair.get("group_id") and p_pair.get("UserId") == r_pair.get("user_id"):
                            found = True
                            break
                    if not found:
                        pairs_match = False
                        break
                if not pairs_match:
                    continue

                # Check IpRanges match
                perm_ipranges = perm.get("IpRanges", [])
                rule_ipranges = rule.get("ip_ranges", [])
                if len(perm_ipranges) != len(rule_ipranges):
                    continue
                ipranges_match = True
                for p_range in perm_ipranges:
                    p_cidr = canonicalize_cidr(p_range.get("CidrIp", ""))
                    found = False
                    for r_range in rule_ipranges:
                        r_cidr = canonicalize_cidr(r_range.get("cidr_ip", ""))
                        if p_cidr == r_cidr:
                            found = True
                            break
                    if not found:
                        ipranges_match = False
                        break
                if not ipranges_match:
                    continue

                # Check Ipv6Ranges match
                perm_ipv6ranges = perm.get("Ipv6Ranges", [])
                rule_ipv6ranges = rule.get("ipv6_ranges", [])
                if len(perm_ipv6ranges) != len(rule_ipv6ranges):
                    continue
                ipv6ranges_match = True
                for p_range in perm_ipv6ranges:
                    p_cidr6 = canonicalize_cidr(p_range.get("CidrIpv6", ""))
                    found = False
                    for r_range in rule_ipv6ranges:
                        r_cidr6 = canonicalize_cidr(r_range.get("cidr_ipv6", ""))
                        if p_cidr6 == r_cidr6:
                            found = True
                            break
                    if not found:
                        ipv6ranges_match = False
                        break
                if not ipv6ranges_match:
                    continue

                # Check PrefixListIds match
                perm_prefixlistids = perm.get("PrefixListIds", [])
                rule_prefixlistids = rule.get("prefix_list_ids", [])
                if len(perm_prefixlistids) != len(rule_prefixlistids):
                    continue
                prefixlistids_match = True
                for p_pl in perm_prefixlistids:
                    p_id = p_pl.get("PrefixListId")
                    found = False
                    for r_pl in rule_prefixlistids:
                        if p_id == r_pl.get("prefix_list_id"):
                            found = True
                            break
                    if not found:
                        prefixlistids_match = False
                        break
                if not prefixlistids_match:
                    continue

                return rule
            return None

        # Update descriptions for rules specified by IpPermissions.N
        if ip_permissions:
            for perm in ip_permissions:
                rule = find_matching_ingress_rule(security_group, perm)
                if not rule:
                    raise Exception("InvalidPermission.NotFound: The specified rule does not exist")
                # Update descriptions in UserIdGroupPairs
                perm_pairs = perm.get("UserIdGroupPairs", [])
                for p_pair in perm_pairs:
                    p_desc = p_pair.get("Description")
                    p_gid = p_pair.get("GroupId")
                    # Find matching pair in rule
                    for r_pair in rule.get("user_id_group_pairs", []):
                        if r_pair.get("group_id") == p_gid:
                            if p_desc is None:
                                r_pair.pop("description", None)
                            else:
                                r_pair["description"] = p_desc
                # Update descriptions in IpRanges
                perm_ipranges = perm.get("IpRanges", [])
                for p_range in perm_ipranges:
                    p_desc = p_range.get("Description")
                    p_cidr = canonicalize_cidr(p_range.get("CidrIp", ""))
                    for r_range in rule.get("ip_ranges", []):
                        r_cidr = canonicalize_cidr(r_range.get("cidr_ip", ""))
                        if r_cidr == p_cidr:
                            if p_desc is None:
                                r_range.pop("description", None)
                            else:
                                r_range["description"] = p_desc
                # Update descriptions in Ipv6Ranges
                perm_ipv6ranges = perm.get("Ipv6Ranges", [])
                for p_range in perm_ipv6ranges:
                    p_desc = p_range.get("Description")
                    p_cidr6 = canonicalize_cidr(p_range.get("CidrIpv6", ""))
                    for r_range in rule.get("ipv6_ranges", []):
                        r_cidr6 = canonicalize_cidr(r_range.get("cidr_ipv6", ""))
                        if r_cidr6 == p_cidr6:
                            if p_desc is None:
                                r_range.pop("description", None)
                            else:
                                r_range["description"] = p_desc
                # Update descriptions in PrefixListIds
                perm_prefixlistids = perm.get("PrefixListIds", [])
                for p_pl in perm_prefixlistids:
                    p_desc = p_pl.get("Description")
                    p_id = p_pl.get("PrefixListId")
                    for r_pl in rule.get("prefix_list_ids", []):
                        if r_pl.get("prefix_list_id") == p_id:
                            if p_desc is None:
                                r_pl.pop("description", None)
                            else:
                                r_pl["description"] = p_desc

        # Update descriptions for rules specified by SecurityGroupRuleDescription.N
        if rule_descriptions:
            for desc_obj in rule_descriptions:
                rule_id = desc_obj.get("SecurityGroupRuleId")
                description = desc_obj.get("Description")
                if not rule_id:
                    raise Exception("InvalidParameter: SecurityGroupRuleId is required in SecurityGroupRuleDescription.N")
                # Find rule by rule_id in ingress rules
                found_rule = None
                for rule in security_group.get("ingress_rules", []):
                    if rule.get("security_group_rule_id") == rule_id:
                        found_rule = rule
                        break
                if not found_rule:
                    raise Exception(f"InvalidSecurityGroupRuleId.NotFound: The security group rule '{rule_id}' does not exist")
                if description is None:
                    found_rule.pop("description", None)
                else:
                    found_rule["description"] = description

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def associate_security_group_vpc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_id = params.get("GroupId")
        vpc_id = params.get("VpcId")

        if not group_id:
            raise Exception("MissingParameter: GroupId is required")
        if not vpc_id:
            raise Exception("MissingParameter: VpcId is required")

        security_group = self.state.security_groups.get(group_id)
        if not security_group:
            raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise Exception(f"InvalidVpcID.NotFound: The VPC '{vpc_id}' does not exist")

        # Check if the VPC is in the same region as the security group
        # Assuming all resources are in the same region in this emulator

        # Check ownership or sharing - simplified: assume user owns both or sharing allowed

        # Associate the security group with the new VPC
        # This means the security group can be used with network interfaces and instances in the specified VPC
        # We emulate this by adding the vpc_id to a list of associated VPCs on the security group

        associated_vpcs = security_group.setdefault("associated_vpcs", set())
        if vpc_id in associated_vpcs:
            state = "associated"
        else:
            associated_vpcs.add(vpc_id)
            state = "associated"

        return {
            "requestId": self.generate_request_id(),
            "state": state,
        }


    def authorize_security_group_egress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_id = params.get("GroupId")
        ip_permissions = params.get("IpPermissions.N", [])

        if not group_id:
            raise Exception("MissingParameter: GroupId is required")

        security_group = self.state.security_groups.get(group_id)
        if not security_group:
            raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")

        if not ip_permissions:
            raise Exception("MissingParameter: IpPermissions.N is required")

        # Helper to generate unique rule id
        def generate_rule_id():
            return self.generate_unique_id(prefix="sgr-")

        # Helper to canonicalize CIDR blocks (IPv4 and IPv6)
        def canonicalize_cidr(cidr: str) -> str:
            # For simplicity, just return the input. Real implementation would canonicalize.
            return cidr

        # Add each ip_permission as an egress rule
        added_rules = []
        for perm in ip_permissions:
            ip_protocol = perm.get("IpProtocol")
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            user_id_group_pairs = perm.get("UserIdGroupPairs", [])
            ip_ranges = perm.get("IpRanges", [])
            ipv6_ranges = perm.get("Ipv6Ranges", [])
            prefix_list_ids = perm.get("PrefixListIds", [])

            # Validate protocol and ports according to AWS rules (simplified)
            if ip_protocol is None:
                raise Exception("InvalidParameter: IpProtocol is required in IpPermissions")

            # Check for duplicate rules - simplified: do not add if exact same rule exists
            def rule_equals(r1, r2):
                if r1.get("ip_protocol") != r2.get("ip_protocol"):
                    return False
                if r1.get("from_port") != r2.get("from_port"):
                    return False
                if r1.get("to_port") != r2.get("to_port"):
                    return False
                if r1.get("user_id_group_pairs") != r2.get("user_id_group_pairs"):
                    return False
                if r1.get("ip_ranges") != r2.get("ip_ranges"):
                    return False
                if r1.get("ipv6_ranges") != r2.get("ipv6_ranges"):
                    return False
                if r1.get("prefix_list_ids") != r2.get("prefix_list_ids"):
                    return False
                return True

            new_rule = {
                "security_group_rule_id": generate_rule_id(),
                "ip_protocol": ip_protocol,
                "from_port": from_port,
                "to_port": to_port,
                "user_id_group_pairs": [],
                "ip_ranges": [],
                "ipv6_ranges": [],
                "prefix_list_ids": [],
                "is_egress": True,
                "description": None,
                "tag_set": [],
            }

            # Process user_id_group_pairs
            for pair in user_id_group_pairs:
                new_pair = {
                    "description": pair.get("Description"),
                    "group_id": pair.get("GroupId"),
                    "group_name": pair.get("GroupName"),
                    "peering_status": pair.get("PeeringStatus"),
                    "user_id": pair.get("UserId"),
                    "vpc_id": pair.get("VpcId"),
                    "vpc_peering_connection_id": pair.get("VpcPeeringConnectionId"),
                }
                new_rule["user_id_group_pairs"].append(new_pair)

            # Process ip_ranges
            for ipr in ip_ranges:
                new_ipr = {
                    "cidr_ip": canonicalize_cidr(ipr.get("CidrIp")),
                    "description": ipr.get("Description"),
                }
                new_rule["ip_ranges"].append(new_ipr)

            # Process ipv6_ranges
            for ip6r in ipv6_ranges:
                new_ip6r = {
                    "cidr_ipv6": canonicalize_cidr(ip6r.get("CidrIpv6")),
                    "description": ip6r.get("Description"),
                }
                new_rule["ipv6_ranges"].append(new_ip6r)

            # Process prefix_list_ids
            for plid in prefix_list_ids:
                new_plid = {
                    "description": plid.get("Description"),
                    "prefix_list_id": plid.get("PrefixListId"),
                }
                new_rule["prefix_list_ids"].append(new_plid)

            # Check for duplicates
            duplicate = False
            for existing_rule in security_group.get("egress_rules", []):
                if rule_equals(existing_rule, new_rule):
                    duplicate = True
                    break
            if duplicate:
                continue  # Skip adding duplicate rule

            # Add the new rule
            security_group.setdefault("egress_rules", []).append(new_rule)
            added_rules.append(new_rule)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
            "securityGroupRuleSet": added_rules,
        }


    def authorize_security_group_ingress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        ip_permissions = params.get("IpPermissions.N", [])

        # Validate that either GroupId or GroupName is provided
        if not group_id and not group_name:
            raise Exception("InvalidParameterCombination: You must specify either GroupId or GroupName")

        # Find the security group
        security_group = None
        if group_id:
            security_group = self.state.security_groups.get(group_id)
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")
        else:
            # GroupName specified, find in default VPC only
            for sg in self.state.security_groups.values():
                if sg.get("group_name") == group_name and (not sg.get("vpc_id") or sg.get("vpc_id") == "default"):
                    security_group = sg
                    break
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_name}' does not exist")

        if not ip_permissions:
            raise Exception("MissingParameter: IpPermissions.N is required")

        # Helper to generate unique rule id
        def generate_rule_id():
            return self.generate_unique_id(prefix="sgr-")

        # Helper to canonicalize CIDR blocks (IPv4 and IPv6)
        def canonicalize_cidr(cidr: str) -> str:
            # For simplicity, just return the input. Real implementation would canonicalize.
            return cidr

        # Add each ip_permission as an ingress rule
        added_rules = []
        for perm in ip_permissions:
            ip_protocol = perm.get("IpProtocol")
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            user_id_group_pairs = perm.get("UserIdGroupPairs", [])
            ip_ranges = perm.get("IpRanges", [])
            ipv6_ranges = perm.get("Ipv6Ranges", [])
            prefix_list_ids = perm.get("PrefixListIds", [])

            # Validate protocol and ports according to AWS rules (simplified)
            if ip_protocol is None:
                raise Exception("InvalidParameter: IpProtocol is required in IpPermissions")

            # Check for duplicate rules - simplified: do not add if exact same rule exists
            def rule_equals(r1, r2):
                if r1.get("ip_protocol") != r2.get("ip_protocol"):
                    return False
                if r1.get("from_port") != r2.get("from_port"):
                    return False
                if r1.get("to_port") != r2.get("to_port"):
                    return False
                if r1.get("user_id_group_pairs") != r2.get("user_id_group_pairs"):
                    return False
                if r1.get("ip_ranges") != r2.get("ip_ranges"):
                    return False
                if r1.get("ipv6_ranges") != r2.get("ipv6_ranges"):
                    return False
                if r1.get("prefix_list_ids") != r2.get("prefix_list_ids"):
                    return False
                return True

            new_rule = {
                "security_group_rule_id": generate_rule_id(),
                "ip_protocol": ip_protocol,
                "from_port": from_port,
                "to_port": to_port,
                "user_id_group_pairs": [],
                "ip_ranges": [],
                "ipv6_ranges": [],
                "prefix_list_ids": [],
                "is_egress": False,
                "description": None,
                "tag_set": [],
            }

            # Process user_id_group_pairs
            for pair in user_id_group_pairs:
                new_pair = {
                    "description": pair.get("Description"),
                    "group_id": pair.get("GroupId"),
                    "group_name": pair.get("GroupName"),
                    "peering_status": pair.get("PeeringStatus"),
                    "user_id": pair.get("UserId"),
                    "vpc_id": pair.get("VpcId"),
                    "vpc_peering_connection_id": pair.get("VpcPeeringConnectionId"),
                }
                new_rule["user_id_group_pairs"].append

    def delete_security_group(self, params: dict) -> dict:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        dry_run = params.get("DryRun", False)

        # Validate input: must specify either GroupId or GroupName (but not both)
        if not group_id and not group_name:
            raise Exception("InvalidParameterCombination: You must specify either GroupId or GroupName")

        # Find the security group
        sg = None
        if group_id:
            sg = self.state.security_groups.get(group_id)
            if not sg:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")
        else:
            # GroupName specified, only allowed for default VPC security groups
            # Find security group by name in default VPCs
            for sg_obj in self.state.security_groups.values():
                if sg_obj.get("groupName") == group_name:
                    # Check if VPC is default or None (default VPC)
                    vpc_id = sg_obj.get("vpcId")
                    if vpc_id is None:
                        sg = sg_obj
                        break
                    else:
                        # For non-default VPCs, must specify GroupId, so error
                        continue
            if not sg:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_name}' does not exist")

        # DryRun check
        if dry_run:
            # Assume user has permission for this emulation
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__error__": "DryRunOperation"
            }

        # Check for dependencies that prevent deletion:
        # 1. Associated with instance or network interface
        # 2. Referenced by another security group in the same VPC
        # 3. Has a VPC association (if applicable)
        sg_id = sg.get("groupId")
        vpc_id = sg.get("vpcId")

        # Check if associated with any instance or network interface
        # We assume self.state.instances and self.state.network_interfaces exist and are dicts
        for instance in getattr(self.state, "instances", {}).values():
            if instance.get("securityGroupIds") and sg_id in instance.get("securityGroupIds"):
                raise Exception("DependencyViolation: The security group is associated with an instance")

        for ni in getattr(self.state, "network_interfaces", {}).values():
            if ni.get("groups") and sg_id in ni.get("groups"):
                raise Exception("DependencyViolation: The security group is associated with a network interface")

        # Check if referenced by another security group in the same VPC
        for other_sg in self.state.security_groups.values():
            if other_sg.get("groupId") == sg_id:
                continue
            if other_sg.get("vpcId") != vpc_id:
                continue
            # Check ingress rules referencing this sg
            for perm in other_sg.get("ipPermissions", []):
                for user_group_pair in perm.get("UserIdGroupPairs", []):
                    if user_group_pair.get("GroupId") == sg_id:
                        raise Exception("DependencyViolation: The security group is referenced by another security group in the same VPC")
            # Check egress rules referencing this sg
            for perm in other_sg.get("ipPermissionsEgress", []):
                for user_group_pair in perm.get("UserIdGroupPairs", []):
                    if user_group_pair.get("GroupId") == sg_id:
                        raise Exception("DependencyViolation: The security group is referenced by another security group in the same VPC")

        # Check if has a VPC association (if this is a secondary association)
        # We assume self.state.security_group_vpc_associations is a dict keyed by association id or groupId
        # If any association exists for this groupId, prevent deletion
        for assoc in getattr(self.state, "security_group_vpc_associations", {}).values():
            if assoc.get("groupId") == sg_id:
                raise Exception("DependencyViolation: The security group has a VPC association")

        # Passed all checks, delete the security group
        del self.state.security_groups[sg_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
            "groupId": sg_id,
        }


    def describe_security_group_references(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        # Collect GroupId.N parameters
        group_ids = []
        for key, value in params.items():
            if key.startswith("GroupId."):
                group_ids.append(value)
        if not group_ids:
            raise Exception("MissingParameter: At least one GroupId.N parameter is required")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "securityGroupReferenceSet": [],
                "__error__": "DryRunOperation"
            }

        # For each groupId, find referencing VPCs (simulate)
        # Since this is an emulator, we will scan all security groups and find those referencing the given groupIds
        # We will build a list of references with groupId, referencingVpcId, transitGatewayId, vpcPeeringConnectionId
        references = []
        for group_id in group_ids:
            # Validate group exists
            if group_id not in self.state.security_groups:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")

            # Find referencing security groups in other VPCs
            for sg in self.state.security_groups.values():
                # Skip if same group
                if sg.get("groupId") == group_id:
                    continue
                # Check ingress rules referencing group_id
                for perm in sg.get("ipPermissions", []):
                    for user_group_pair in perm.get("UserIdGroupPairs", []):
                        if user_group_pair.get("GroupId") == group_id:
                            referencing_vpc_id = sg.get("vpcId")
                            # For this emulator, we do not have transitGatewayId or vpcPeeringConnectionId details,
                            # so we set them to None or empty string
                            references.append({
                                "groupId": group_id,
                                "referencingVpcId": referencing_vpc_id,
                                "transitGatewayId": None,
                                "vpcPeeringConnectionId": None,
                            })
                # Check egress rules referencing group_id
                for perm in sg.get("ipPermissionsEgress", []):
                    for user_group_pair in perm.get("UserIdGroupPairs", []):
                        if user_group_pair.get("GroupId") == group_id:
                            referencing_vpc_id = sg.get("vpcId")
                            references.append({
                                "groupId": group_id,
                                "referencingVpcId": referencing_vpc_id,
                                "transitGatewayId": None,
                                "vpcPeeringConnectionId": None,
                            })

        # Remove duplicates
        unique_refs = []
        seen = set()
        for ref in references:
            key = (ref["groupId"], ref["referencingVpcId"], ref["transitGatewayId"], ref["vpcPeeringConnectionId"])
            if key not in seen:
                seen.add(key)
                unique_refs.append(ref)

        return {
            "requestId": self.generate_request_id(),
            "securityGroupReferenceSet": unique_refs,
        }


    def describe_security_groups(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect GroupId.N and GroupName.N parameters
        group_ids = []
        group_names = []
        for key, value in params.items():
            if key.startswith("GroupId."):
                group_ids.append(value)
            elif key.startswith("GroupName."):
                group_names.append(value)

        # Collect filters
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                # Filter.N.Name and Filter.N.Value.M
                # Parse filter index
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    # Find or create filter dict
                    while len(filters) < int(filter_index):
                        filters.append({"Name": None, "Values": []})
                    filter_obj = filters[int(filter_index) - 1]
                    if filter_key == "Name":
                        filter_obj["Name"] = value
                    elif filter_key.startswith("Value"):
                        filter_obj["Values"].append(value)

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "securityGroupInfo": [],
                "nextToken": None,
                "__error__": "DryRunOperation"
            }

        # Helper to get attribute from SecurityGroup (works with both dataclass and dict)
        def get_sg_attr(sg, attr, default=None):
            if hasattr(sg, attr):
                return getattr(sg, attr, default)
            elif isinstance(sg, dict):
                return sg.get(attr, default)
            return default

        # Filter security groups by group_ids or group_names if specified
        sgs = list(self.state.security_groups.values())
        if group_ids:
            sgs = [sg for sg in sgs if get_sg_attr(sg, "groupId") in group_ids]
        if group_names:
            sgs = [sg for sg in sgs if get_sg_attr(sg, "groupName") in group_names]

        # Apply filters
        def match_filter(sg, filter_obj):
            import fnmatch
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True

            # Helper to check with wildcard support
            def any_match(val_list, target):
                if target is None:
                    return False
                target_str = str(target)
                for v in val_list:
                    v_str = str(v)
                    if '*' in v_str or '?' in v_str:
                        if fnmatch.fnmatch(target_str, v_str):
                            return True
                    elif v_str == target_str:
                        return True
                return False

            # Implement some common filters based on AWS docs
            # For brevity, implement a subset of filters:
            # group-id, group-name, description, vpc-id, owner-id, tag:<key>, tag-key
            if name == "group-id":
                return any_match(values, get_sg_attr(sg, "groupId"))
            if name == "group-name":
                return any_match(values, get_sg_attr(sg, "groupName"))
            if name == "description":
                return any_match(values, get_sg_attr(sg, "groupDescription"))
            if name == "vpc-id":
                return any_match(values, get_sg_attr(sg, "vpcId"))
            if name == "owner-id":
                return any_match(values, get_sg_attr(sg, "ownerId"))
            if name.startswith("tag:"):
                tag_key = name[4:]
                tags = get_sg_attr(sg, "tagSet", []) or []
                for tag in tags:
                    tag_k = getattr(tag, "Key", None) if hasattr(tag, "Key") else tag.get("Key") if isinstance(tag, dict) else None
                    tag_v = getattr(tag, "Value", None) if hasattr(tag, "Value") else tag.get("Value") if isinstance(tag, dict) else None
                    if tag_k == tag_key and any_match(values, tag_v):
                        return True
                return False
            if name == "tag-key":
                tags = get_sg_attr(sg, "tagSet", []) or []
                for tag in tags:
                    tag_k = getattr(tag, "Key", None) if hasattr(tag, "Key") else tag.get("Key") if isinstance(tag, dict) else None
                    if any_match(values, tag_k):
                        return True
                return False
            # For ip-permission.* filters, we skip detailed implementation for brevity
            # Return True to not filter out
            return True

        filtered_sgs = []
        for sg in sgs:
            if all(match_filter(sg, f) for f in filters):
                filtered_sgs.append(sg)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5:
                    max_results = 5
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = None

        end_index = start_index + max_results if max_results else None
        page_sgs = filtered_sgs[start_index:end_index]

        new_next_token = str(end_index) if end_index and end_index < len(filtered_sgs) else None

        return {
            "requestId": self.generate_request_id(),
            "securityGroupInfo": page_sgs,
            "nextToken": new_next_token,
        }


    def describe_security_group_vpc_associations(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect filters
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    while len(filters) < int(filter_index):
                        filters.append({"Name": None, "Values": []})
                    filter_obj = filters[int(filter_index) - 1]
                    if filter_key == "Name":
                        filter_obj["Name"] = value
                    elif filter_key.startswith("Value"):
                        filter_obj["Values"].append(value)

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "securityGroupVpcAssociationSet": [],
                "nextToken": None,
                "__error__": "DryRunOperation"
            }

        # Get all associations
        associations = list(getattr(self.state, "security_group_vpc_associations", {}).values())

        # Apply filters
        def match_filter(assoc, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "group-id":
                return assoc.get("groupId") in values
            if name == "group-owner-id":
                return assoc.get("groupOwnerId") in values
            if name == "state":
                return assoc.get("state") in values
            if name == "vpc-id":
                return assoc.get("vpcId") in values
            if name == "vpc-owner-id":
                return assoc.get("vpcOwnerId") in values
            return True

        filtered_assocs = [assoc for assoc in associations if all(match_filter(assoc, f) for f in filters)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5:
                    max_results = 5
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = None

        end_index = start_index + max_results if max_results else None
        page_assocs = filtered_assocs[start_index:end_index]

        new_next_token = str(end_index) if end_index and end_index < len(filtered_assocs) else None

        return {
            "requestId": self.generate_request_id(),
            "securityGroupVpcAssociationSet": page_assocs,
            "nextToken": new_next_token,
        }


    def describe_stale_security_groups(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        vpc_id = params.get("VpcId")

        if not vpc_id:
            raise Exception("MissingParameter: VpcId is required")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "staleSecurityGroupSet": [],
                "nextToken": None,
                "__error__": "DryRunOperation"
            }

        # For this emulator, we simulate stale security groups as those that have rules referencing deleted security groups
        # in the specified VPC.

        # Collect all security groups in the VPC
        sgs_in_vpc = [sg for sg in self.state.security_groups.values() if sg.get("vpcId") == vpc_id]

        stale_sgs = []

        def is_group_deleted(group_id):
            return group_id not in self.state.security_groups

        def build_stale_ip_permission(perm):
            # Build stale ip permission dict with required fields
            stale_perm = {
                "fromPort": perm.get("FromPort"),
                "toPort": perm.get("ToPort"),
                "ipProtocol": perm.get("IpProtocol"),
                "groups": [],
                "ipRanges": perm.get("IpRanges", []),
                "prefixListIds": perm.get("PrefixListIds", []),
            }
            # Check groups for stale references
            for ugp in perm.get("UserIdGroupPairs", []):
                group_id = ugp.get("GroupId")
                if is_group_deleted(group_id):
                    stale_group = {
                        "Description": ugp.get("Description"),
                        "GroupId": group_id,
                        "GroupName": ugp.get("GroupName"),
                        "PeeringStatus": ugp.get("PeeringStatus"),
                        "UserId": ugp.get("UserId"),
                        "VpcId": ugp.get("VpcId"),
                        "VpcPeeringConnectionId": ugp.get("VpcPeeringConnectionId"),
                    }
                    stale_perm["groups"].append(stale_group)
            return stale_perm

        for sg in sgs_in_vpc:
            stale_ingress = []
            stale_egress = []

            # Check ingress rules
            for perm in sg.get("ipPermissions", []):
                stale_perm = build_stale_ip_permission(perm)
                if stale_perm["groups"]:
                    stale_ingress.append(stale_perm)

            # Check egress rules
            for perm in sg.get("ipPermissionsEgress", []):
                stale_perm = build_stale_ip_permission(perm)
                if stale_perm["groups"]:
                    stale_egress.append(stale_perm)

            if stale_ingress or stale_egress:
                stale_sgs.append({
                    "description": sg.get("groupDescription"),
                    "groupId": sg.get("groupId"),
                    "groupName": sg.get("groupName"),
                    "staleIpPermissions": stale_ingress,
                    "staleIpPermissionsEgress": stale_egress,
                    "vpcId": vpc_id,
                })

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5:
                    max_results = 5
                elif max_results > 255:
                    max_results = 255
            except Exception:
                max_results = None

        end_index = start_index + max_results if max_results else None
        page_stale_sgs = stale_sgs[start_index:end_index]

        new_next_token = str(end_index) if end_index and end_index < len(stale_sgs) else None

        return {
            "requestId": self.generate_request_id(),
            "staleSecurityGroupSet": page_stale_sgs,
            "nextToken": new_next_token,
        }

    def disassociate_security_group_vpc(self, params: dict) -> dict:
        group_id = params.get("GroupId")
        vpc_id = params.get("VpcId")
        dry_run = params.get("DryRun", False)

        if not group_id:
            raise Exception("Missing required parameter GroupId")
        if not vpc_id:
            raise Exception("Missing required parameter VpcId")

        # DryRun check
        if dry_run:
            # Here we assume permission is granted for simplicity
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        sg = self.state.security_groups.get(group_id)
        if not sg:
            raise Exception(f"SecurityGroup {group_id} not found")

        # Check if the security group is associated with the given VPC
        if sg.get("VpcId") != vpc_id:
            raise Exception(f"SecurityGroup {group_id} is not associated with VPC {vpc_id}")

        # Check if any ENIs in the VPC are associated with this security group
        for eni in self.state.network_interfaces.values():
            if eni.get("VpcId") == vpc_id and group_id in eni.get("Groups", []):
                raise Exception("Cannot disassociate security group while it is associated with network interfaces")

        # Disassociate security group from VPC asynchronously
        # For emulator, we simulate immediate disassociation
        sg["VpcId"] = None

        return {
            "requestId": self.generate_request_id(),
            "state": "disassociated"
        }


    def get_security_groups_for_vpc(self, params: dict) -> dict:
        vpc_id = params.get("VpcId")
        dry_run = params.get("DryRun", False)
        filters = []
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if not vpc_id:
            raise Exception("Missing required parameter VpcId")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Parse filters
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                # Filter.N.Name and Filter.N.Value.M
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_index = parts[1]
                    filter_key = parts[2]
                    # Collect filters by index
                    while len(filters) < int(filter_index):
                        filters.append({"Name": None, "Values": []})
                    if filter_key == "Name":
                        filters[int(filter_index) - 1]["Name"] = value
                    elif filter_key.startswith("Value"):
                        filters[int(filter_index) - 1]["Values"].append(value)

        # Filter security groups by VPC and filters
        matched_sgs = []
        for sg in self.state.security_groups.values():
            if sg.get("VpcId") != vpc_id:
                continue
            # Apply filters
            match = True
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not name or not values:
                    continue
                if name == "group-id":
                    if sg.get("GroupId") not in values:
                        match = False
                        break
                elif name == "description":
                    if sg.get("Description") not in values:
                        match = False
                        break
                elif name == "group-name":
                    if sg.get("GroupName") not in values:
                        match = False
                        break
                elif name == "owner-id":
                    if sg.get("OwnerId") not in values:
                        match = False
                        break
                elif name == "primary-vpc-id":
                    if sg.get("VpcId") not in values:
                        match = False
                        break
                else:
                    # Unknown filter, ignore or fail? We ignore
                    pass
            if match:
                matched_sgs.append(sg)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5:
                    max_results = 5
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = None

        end_index = start_index + max_results if max_results else None
        page_sgs = matched_sgs[start_index:end_index]

        # Prepare response security groups
        security_group_for_vpc_set = []
        for sg in page_sgs:
            tags = []
            for k, v in sg.get("Tags", {}).items():
                if k.startswith("aws:"):
                    continue
                tags.append({"Key": k, "Value": v})
            security_group_for_vpc_set.append({
                "description": sg.get("Description"),
                "groupId": sg.get("GroupId"),
                "groupName": sg.get("GroupName"),
                "ownerId": sg.get("OwnerId"),
                "primaryVpcId": sg.get("VpcId"),
                "tagSet": tags
            })

        # Next token for pagination
        new_next_token = str(end_index) if end_index and end_index < len(matched_sgs) else None

        return {
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "securityGroupForVpcSet": security_group_for_vpc_set
        }


    def modify_security_group_rules(self, params: dict) -> dict:
        group_id = params.get("GroupId")
        dry_run = params.get("DryRun", False)

        if not group_id:
            raise Exception("Missing required parameter GroupId")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        sg = self.state.security_groups.get(group_id)
        if not sg:
            raise Exception(f"SecurityGroup {group_id} not found")

        # Collect SecurityGroupRule.N updates
        updates = []
        # Find keys like SecurityGroupRule.1.SecurityGroupRuleId, SecurityGroupRule.1.SecurityGroupRule.*
        for key, value in params.items():
            if key.startswith("SecurityGroupRule."):
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                index = parts[1]
                field = parts[2]
                while len(updates) < int(index):
                    updates.append({})
                if field == "SecurityGroupRuleId":
                    updates[int(index) - 1]["SecurityGroupRuleId"] = value
                elif field == "SecurityGroupRule":
                    # Nested fields for SecurityGroupRule
                    # e.g. SecurityGroupRule.1.SecurityGroupRule.CidrIpv4
                    nested_field = ".".join(parts[3:])
                    if nested_field:
                        if "SecurityGroupRule" not in updates[int(index) - 1]:
                            updates[int(index) - 1]["SecurityGroupRule"] = {}
                        updates[int(index) - 1]["SecurityGroupRule"][nested_field] = value

        if not updates:
            raise Exception("Missing required parameter SecurityGroupRule.N")

        # Modify rules in the security group
        # We assume sg has a "Rules" dict keyed by rule id
        rules = sg.get("Rules", {})
        for update in updates:
            rule_id = update.get("SecurityGroupRuleId")
            if not rule_id:
                raise Exception("SecurityGroupRuleId is required in SecurityGroupRule.N")
            if rule_id not in rules:
                raise Exception(f"SecurityGroupRuleId {rule_id} not found in security group {group_id}")
            rule = rules[rule_id]
            rule_update = update.get("SecurityGroupRule", {})
            # Update fields if present
            for k, v in rule_update.items():
                # Convert types if needed
                if k in ("FromPort", "ToPort"):
                    try:
                        v = int(v)
                    except Exception:
                        pass
                rule[k] = v

        return {
            "requestId": self.generate_request_id(),
            "return": True
        }


    def revoke_security_group_egress(self, params: dict) -> dict:
        group_id = params.get("GroupId")
        dry_run = params.get("DryRun", False)

        if not group_id:
            raise Exception("Missing required parameter GroupId")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        sg = self.state.security_groups.get(group_id)
        if not sg:
            raise Exception(f"SecurityGroup {group_id} not found")

        # Collect rules to revoke by SecurityGroupRuleId.N or IpPermissions.N
        rule_ids = []
        for key, value in params.items():
            if key.startswith("SecurityGroupRuleId."):
                rule_ids.append(value)

        ip_permissions = []
        # Parse IpPermissions.N.* parameters
        # We will parse IpPermissions.N.IpProtocol, IpPermissions.N.FromPort, IpPermissions.N.ToPort, IpPermissions.N.IpRanges, etc.
        ip_permissions_map = {}
        for key, value in params.items():
            if key.startswith("IpPermissions."):
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                index = parts[1]
                field = parts[2]
                if index not in ip_permissions_map:
                    ip_permissions_map[index] = {}
                if field == "IpProtocol":
                    ip_permissions_map[index]["IpProtocol"] = value
                elif field == "FromPort":
                    try:
                        ip_permissions_map[index]["FromPort"] = int(value)
                    except Exception:
                        ip_permissions_map[index]["FromPort"] = value
                elif field == "ToPort":
                    try:
                        ip_permissions_map[index]["ToPort"] = int(value)
                    except Exception:
                        ip_permissions_map[index]["ToPort"] = value
                elif field == "IpRanges":
                    # Collect IpRanges.M.CidrIp and IpRanges.M.Description
                    # We need to collect all IpRanges for this permission
                    if "IpRanges" not in ip_permissions_map[index]:
                        ip_permissions_map[index]["IpRanges"] = []
                    # We will collect all IpRanges.M.* keys later
                elif field == "Ipv6Ranges":
                    if "Ipv6Ranges" not in ip_permissions_map[index]:
                        ip_permissions_map[index]["Ipv6Ranges"] = []
                elif field == "UserIdGroupPairs":
                    if "UserIdGroupPairs" not in ip_permissions_map[index]:
                        ip_permissions_map[index]["UserIdGroupPairs"] = []

        # Now parse IpRanges, Ipv6Ranges, UserIdGroupPairs for each IpPermissions.N
        for key, value in params.items():
            if key.startswith("IpPermissions."):
                parts = key.split(".")
                if len(parts) < 5:
                    continue
                perm_index = parts[1]
                group = parts[2]
                sub_index = parts[3]
                sub_field = parts[4]
                if perm_index not in ip_permissions_map:
                    continue
                if group == "IpRanges":
                    while len(ip_permissions_map[perm_index].setdefault("IpRanges", [])) < int(sub_index):
                        ip_permissions_map[perm_index]["IpRanges"].append({})
                    ip_range = ip_permissions_map[perm_index]["IpRanges"][int(sub_index) - 1]
                    if sub_field == "CidrIp":
                        ip_range["CidrIp"] = value
                    elif sub_field == "Description":
                        ip_range["Description"] = value
                elif group == "Ipv6Ranges":
                    while len(ip_permissions_map[perm_index].setdefault("Ipv6Ranges", [])) < int(sub_index):
                        ip_permissions_map[perm_index]["Ipv6Ranges"].append({})
                    ipv6_range = ip_permissions_map[perm_index]["Ipv6Ranges"][int(sub_index) - 1]
                    if sub_field == "CidrIpv6":
                        ipv6_range["CidrIpv6"] = value
                    elif sub_field == "Description":
                        ipv6_range["Description"] = value
                elif group == "UserIdGroupPairs":
                    while len(ip_permissions_map[perm_index].setdefault("UserIdGroupPairs", [])) < int(sub_index):
                        ip_permissions_map[perm_index]["UserIdGroupPairs"].append({})
                    user_group_pair = ip_permissions_map[perm_index]["UserIdGroupPairs"][int(sub_index) - 1]
                    user_group_pair[sub_field] = value

        ip_permissions = list(ip_permissions_map.values())

        # Revoke rules by rule_ids or by matching ip_permissions
        revoked_rules = []
        unknown_ip_permission_set = []

        rules = sg.get("Rules", {})
        # We only revoke egress rules (isEgress=True)
        to_remove_rule_ids = set()

        # Revoke by rule IDs
        for rid in rule_ids:
            if rid in rules and rules[rid].get("IsEgress", False):
                revoked_rules.append(rules[rid].copy())
                to_remove_rule_ids.add(rid)

        # Revoke by ip_permissions
        def rule_matches_permission(rule, perm):
            # Match protocol
            if "IpProtocol" in perm and perm["IpProtocol"] != rule.get("IpProtocol"):
                return False
            # Match FromPort and ToPort if present
            if "FromPort" in perm and perm["FromPort"] != rule.get("FromPort"):
                return False
            if "ToPort" in perm and perm["ToPort"] != rule.get("ToPort"):
                return False
            # Match IpRanges
            if "IpRanges" in perm:
                perm_cidrs = {r.get("CidrIp") for r in perm["IpRanges"] if "CidrIp" in r}
                rule_cidrs = {rule.get("CidrIpv4")} if rule.get("CidrIpv4") else set()
                if not perm_cidrs.intersection(rule_cidrs):
                    return False
            # Match Ipv6Ranges
            if "Ipv6Ranges" in perm:
                perm_cidrs6 = {r.get("CidrIpv6") for r in perm["Ipv6Ranges"] if "CidrIpv6" in r}
                rule_cidrs6 = {rule.get("CidrIpv6")} if rule.get("CidrIpv6") else set()
                if not perm_cidrs6.intersection(rule_cidrs6):
                    return False
            # Match UserIdGroupPairs
            if "UserIdGroupPairs" in perm:
                perm_group_ids = {p.get("GroupId") for p in perm["UserIdGroupPairs"] if "GroupId" in p}
                rule_group_id = rule.get("ReferencedGroupId")
                if rule_group_id not in perm_group_ids:
                    return False
            return True

        for rid, rule in rules.items():
            if not rule.get("IsEgress", False):
                continue
            if rid in to_remove_rule_ids:
                continue
            matched = False
            for perm in ip_permissions:
                if rule_matches_permission(rule, perm):
                    revoked_rules.append(rule.copy())
                    to_remove_rule_ids.add(rid)
                    matched = True
                    break
            if not matched and ip_permissions:
                unknown_ip_permission_set.append(rule.copy())

        # Remove revoked rules
        for rid in to_remove_rule_ids:
            rules.pop(rid, None)

        # Prepare revokedSecurityGroupRuleSet response
        revoked_security_group_rule_set = []
        for r in revoked_rules:
            revoked_security_group_rule_set.append({
                "cidrIpv4": r.get("CidrIpv4"),
                "cidrIpv6": r.get("CidrIpv6"),
                "description": r.get("Description"),
                "fromPort": r.get("FromPort"),
                "groupId": group_id,
                "ipProtocol": r.get("IpProtocol"),
                "isEgress": True,
                "prefixListId": r.get("PrefixListId"),
                "referencedGroupId": r.get("ReferencedGroupId"),
                "securityGroupRuleId": r.get("RuleId"),
                "toPort": r.get("ToPort"),
            })

        return {
            "requestId": self.generate_request_id(),
            "return": True,
            "revokedSecurityGroupRuleSet": revoked_security_group_rule_set,
            "unknownIpPermissionSet": unknown_ip_permission_set
        }


    def revoke_security_group_ingress(self, params: dict) -> dict:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        dry_run = params.get("DryRun", False)

        if not group_id and not group_name:
            raise Exception("Must specify either GroupId or GroupName")

        # DryRun check
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                }
            }

        # Find security group by ID or name
        sg = None
        if group_id:
            sg = self.state.security_groups.get(group_id)
        else:
            # Search by group name in default VPCs only
            for s in self.state.security_groups.values():
                if s.get("GroupName") == group_name:
                    sg = s
                    break

        if not sg:
            raise Exception("Security group not found")

        # Collect rules to revoke by SecurityGroupRuleId.N or IpPermissions.N
        rule_ids = []
        for key, value in params.items():
            if key.startswith("SecurityGroupRuleId."):
                rule_ids.append(value)

        ip_permissions = []
        ip_permissions_map = {}
        for key, value in params.items():
            if key.startswith("IpPermissions."):
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                index = parts[1]
                field = parts[2]
                if index not in ip_permissions_map:
                    ip_permissions_map[index] = {}
                if field == "IpProtocol":
                    ip_permissions_map[index]["IpProtocol"] = value
                elif field == "FromPort":
                    try:
                        ip_permissions_map[index]["FromPort"] = int(value)
                    except Exception:
                        ip_permissions_map[index]["FromPort"] = value
                elif field == "ToPort":
                    try:
                        ip_permissions_map[index]["ToPort"] = int(value)
                    except Exception:
                        ip_permissions_map[index]["ToPort"] = value
                elif field == "IpRanges":
                    if "IpRanges" not in ip_permissions_map[index]:
                        ip_permissions_map[index]["IpRanges"] = []
                elif field == "Ipv6Ranges":
                    if "Ipv6Ranges" not in ip_permissions_map[index]:
                        ip_permissions_map[index]["Ipv6Ranges"] = []
                elif field == "UserIdGroupPairs":
                    if "UserIdGroupPairs" not in ip_permissions_map[index]:
                        ip_permissions_map[index]["UserIdGroupPairs"] = []

    def update_security_group_rule_descriptions_egress(self, params: dict) -> dict:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        ip_permissions = params.get("IpPermissions.N", [])
        sg_rule_descriptions = params.get("SecurityGroupRuleDescription.N", [])

        # Validate that either GroupId or GroupName is provided
        if not group_id and not group_name:
            raise Exception("InvalidParameterCombination: You must specify either GroupId or GroupName")

        # Find the security group
        security_group = None
        if group_id:
            security_group = self.state.security_groups.get(group_id)
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")
        elif group_name:
            # Search by name in default VPC only
            for sg in self.state.security_groups.values():
                if sg.get("GroupName") == group_name:
                    security_group = sg
                    break
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_name}' does not exist")

        # If no IP permissions and no descriptions provided, error
        if not ip_permissions and not sg_rule_descriptions:
            raise Exception("InvalidParameterCombination: You must specify either IpPermissions or SecurityGroupRuleDescription")

        # Helper to find matching egress rule in security group
        def find_matching_egress_rule(ip_perm):
            for rule in security_group.get("IpPermissionsEgress", []):
                # Match protocol
                if rule.get("IpProtocol") != ip_perm.get("IpProtocol"):
                    continue
                # Match FromPort and ToPort (both can be None)
                if rule.get("FromPort") != ip_perm.get("FromPort"):
                    continue
                if rule.get("ToPort") != ip_perm.get("ToPort"):
                    continue
                # Match UserIdGroupPairs
                def normalize_pairs(pairs):
                    if not pairs:
                        return []
                    normalized = []
                    for p in pairs:
                        # Only consider GroupId and UserId for matching
                        normalized.append((p.get("GroupId"), p.get("UserId")))
                    return sorted(normalized)
                if normalize_pairs(rule.get("UserIdGroupPairs")) != normalize_pairs(ip_perm.get("UserIdGroupPairs")):
                    continue
                # Match IpRanges
                def normalize_ipranges(ranges):
                    if not ranges:
                        return []
                    normalized = []
                    for r in ranges:
                        normalized.append(r.get("CidrIp"))
                    return sorted(normalized)
                if normalize_ipranges(rule.get("IpRanges")) != normalize_ipranges(ip_perm.get("IpRanges")):
                    continue
                # Match Ipv6Ranges
                def normalize_ipv6ranges(ranges):
                    if not ranges:
                        return []
                    normalized = []
                    for r in ranges:
                        normalized.append(r.get("CidrIpv6"))
                    return sorted(normalized)
                if normalize_ipv6ranges(rule.get("Ipv6Ranges")) != normalize_ipv6ranges(ip_perm.get("Ipv6Ranges")):
                    continue
                # Match PrefixListIds
                def normalize_prefixlistids(plists):
                    if not plists:
                        return []
                    normalized = []
                    for p in plists:
                        normalized.append(p.get("PrefixListId"))
                    return sorted(normalized)
                if normalize_prefixlistids(rule.get("PrefixListIds")) != normalize_prefixlistids(ip_perm.get("PrefixListIds")):
                    continue
                return rule
            return None

        # Update descriptions by IpPermissions
        for ip_perm in ip_permissions:
            rule = find_matching_egress_rule(ip_perm)
            if not rule:
                raise Exception("InvalidPermission.NotFound: The specified rule does not exist")
            # Update description fields in UserIdGroupPairs
            if "UserIdGroupPairs" in ip_perm:
                for idx, pair in enumerate(ip_perm["UserIdGroupPairs"]):
                    # Find matching pair in rule by GroupId and UserId
                    found = False
                    for rule_pair in rule.get("UserIdGroupPairs", []):
                        if (rule_pair.get("GroupId") == pair.get("GroupId") and
                            rule_pair.get("UserId") == pair.get("UserId")):
                            # Update or remove description
                            if "Description" in pair:
                                rule_pair["Description"] = pair["Description"]
                            else:
                                rule_pair.pop("Description", None)
                            found = True
                            break
                    if not found:
                        # If pair not found, ignore (AWS does not error)
                        pass
            # Update description fields in IpRanges
            if "IpRanges" in ip_perm:
                for ip_range in ip_perm["IpRanges"]:
                    cidr = ip_range.get("CidrIp")
                    if not cidr:
                        continue
                    found = False
                    for rule_range in rule.get("IpRanges", []):
                        if rule_range.get("CidrIp") == cidr:
                            if "Description" in ip_range:
                                rule_range["Description"] = ip_range["Description"]
                            else:
                                rule_range.pop("Description", None)
                            found = True
                            break
                    if not found:
                        pass
            # Update description fields in Ipv6Ranges
            if "Ipv6Ranges" in ip_perm:
                for ip6_range in ip_perm["Ipv6Ranges"]:
                    cidr6 = ip6_range.get("CidrIpv6")
                    if not cidr6:
                        continue
                    found = False
                    for rule_range in rule.get("Ipv6Ranges", []):
                        if rule_range.get("CidrIpv6") == cidr6:
                            if "Description" in ip6_range:
                                rule_range["Description"] = ip6_range["Description"]
                            else:
                                rule_range.pop("Description", None)
                            found = True
                            break
                    if not found:
                        pass
            # Update description fields in PrefixListIds
            if "PrefixListIds" in ip_perm:
                for prefix in ip_perm["PrefixListIds"]:
                    prefix_id = prefix.get("PrefixListId")
                    if not prefix_id:
                        continue
                    found = False
                    for rule_prefix in rule.get("PrefixListIds", []):
                        if rule_prefix.get("PrefixListId") == prefix_id:
                            if "Description" in prefix:
                                rule_prefix["Description"] = prefix["Description"]
                            else:
                                rule_prefix.pop("Description", None)
                            found = True
                            break
                    if not found:
                        pass

        # Update descriptions by SecurityGroupRuleDescription.N
        for desc in sg_rule_descriptions:
            rule_id = desc.get("SecurityGroupRuleId")
            description = desc.get("Description")
            if not rule_id:
                continue
            # Find rule by rule id in egress rules
            found_rule = None
            for rule in security_group.get("IpPermissionsEgress", []):
                if rule.get("SecurityGroupRuleId") == rule_id:
                    found_rule = rule
                    break
            if not found_rule:
                raise Exception(f"InvalidSecurityGroupRuleId.NotFound: The security group rule '{rule_id}' does not exist")
            if description is not None:
                found_rule["Description"] = description
            else:
                found_rule.pop("Description", None)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def update_security_group_rule_descriptions_ingress(self, params: dict) -> dict:
        group_id = params.get("GroupId")
        group_name = params.get("GroupName")
        ip_permissions = params.get("IpPermissions.N", [])
        sg_rule_descriptions = params.get("SecurityGroupRuleDescription.N", [])

        # Validate that either GroupId or GroupName is provided
        if not group_id and not group_name:
            raise Exception("InvalidParameterCombination: You must specify either GroupId or GroupName")

        # Find the security group
        security_group = None
        if group_id:
            security_group = self.state.security_groups.get(group_id)
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_id}' does not exist")
        elif group_name:
            # Search by name in default VPC only
            for sg in self.state.security_groups.values():
                if sg.get("GroupName") == group_name:
                    security_group = sg
                    break
            if not security_group:
                raise Exception(f"InvalidGroup.NotFound: The security group '{group_name}' does not exist")

        # If no IP permissions and no descriptions provided, error
        if not ip_permissions and not sg_rule_descriptions:
            raise Exception("InvalidParameterCombination: You must specify either IpPermissions or SecurityGroupRuleDescription")

        # Helper to find matching ingress rule in security group
        def find_matching_ingress_rule(ip_perm):
            for rule in security_group.get("IpPermissions", []):
                # Match protocol
                if rule.get("IpProtocol") != ip_perm.get("IpProtocol"):
                    continue
                # Match FromPort and ToPort (both can be None)
                if rule.get("FromPort") != ip_perm.get("FromPort"):
                    continue
                if rule.get("ToPort") != ip_perm.get("ToPort"):
                    continue
                # Match UserIdGroupPairs
                def normalize_pairs(pairs):
                    if not pairs:
                        return []
                    normalized = []
                    for p in pairs:
                        # Only consider GroupId and UserId for matching
                        normalized.append((p.get("GroupId"), p.get("UserId")))
                    return sorted(normalized)
                if normalize_pairs(rule.get("UserIdGroupPairs")) != normalize_pairs(ip_perm.get("UserIdGroupPairs")):
                    continue
                # Match IpRanges
                def normalize_ipranges(ranges):
                    if not ranges:
                        return []
                    normalized = []
                    for r in ranges:
                        normalized.append(r.get("CidrIp"))
                    return sorted(normalized)
                if normalize_ipranges(rule.get("IpRanges")) != normalize_ipranges(ip_perm.get("IpRanges")):
                    continue
                # Match Ipv6Ranges
                def normalize_ipv6ranges(ranges):
                    if not ranges:
                        return []
                    normalized = []
                    for r in ranges:
                        normalized.append(r.get("CidrIpv6"))
                    return sorted(normalized)
                if normalize_ipv6ranges(rule.get("Ipv6Ranges")) != normalize_ipv6ranges(ip_perm.get("Ipv6Ranges")):
                    continue
                # Match PrefixListIds
                def normalize_prefixlistids(plists):
                    if not plists:
                        return []
                    normalized = []
                    for p in plists:
                        normalized.append(p.get("PrefixListId"))
                    return sorted(normalized)
                if normalize_prefixlistids(rule.get("PrefixListIds")) != normalize_prefixlistids(ip_perm.get("PrefixListIds")):
                    continue
                return rule
            return None

        # Update descriptions by IpPermissions
        for ip_perm in ip_permissions:
            rule = find_matching_ingress_rule(ip_perm)
            if not rule:
                raise Exception("InvalidPermission.NotFound: The specified rule does not exist")
            # Update description fields in UserIdGroupPairs
            if "UserIdGroupPairs" in ip_perm:
                for idx, pair in enumerate(ip_perm["UserIdGroupPairs"]):
                    # Find matching pair in rule by GroupId and UserId
                    found = False
                    for rule_pair in rule.get("UserIdGroupPairs", []):
                        if (rule_pair.get("GroupId") == pair.get("GroupId") and
                            rule_pair.get("UserId") == pair.get("UserId")):
                            # Update or remove description
                            if "Description" in pair:
                                rule_pair["Description"] = pair["Description"]
                            else:
                                rule_pair.pop("Description", None)
                            found = True
                            break
                    if not found:
                        # If pair not found, ignore (AWS does not error)
                        pass
            # Update description fields in IpRanges
            if "IpRanges" in ip_perm:
                for ip_range in ip_perm["IpRanges"]:
                    cidr = ip_range.get("CidrIp")
                    if not cidr:
                        continue
                    found = False
                    for rule_range in rule.get("IpRanges", []):
                        if rule_range.get("CidrIp") == cidr:
                            if "Description" in ip_range:
                                rule_range["Description"] = ip_range["Description"]
                            else:
                                rule_range.pop("Description", None)
                            found = True
                            break
                    if not found:
                        pass
            # Update description fields in Ipv6Ranges
            if "Ipv6Ranges" in ip_perm:
                for ip6_range in ip_perm["Ipv6Ranges"]:
                    cidr6 = ip6_range.get("CidrIpv6")
                    if not cidr6:
                        continue
                    found = False
                    for rule_range in rule.get("Ipv6Ranges", []):
                        if rule_range.get("CidrIpv6") == cidr6:
                            if "Description" in ip6_range:
                                rule_range["Description"] = ip6_range["Description"]
                            else:
                                rule_range.pop("Description", None)
                            found = True
                            break
                    if not found:
                        pass
            # Update description fields in PrefixListIds
            if "PrefixListIds" in ip_perm:
                for prefix in ip_perm["PrefixListIds"]:
                    prefix_id = prefix.get("PrefixListId")
                    if not prefix_id:
                        continue
                    found = False
                    for rule_prefix in rule.get("PrefixListIds", []):
                        if rule_prefix.get("PrefixListId") == prefix_id:
                            if "Description" in prefix:
                                rule_prefix["Description"] = prefix["Description"]
                            else:
                                rule_prefix.pop("Description", None)
                            found = True
                            break
                    if not found:
                        pass

        # Update descriptions by SecurityGroupRuleDescription.N
        for desc in sg_rule_descriptions:
            rule_id = desc.get("SecurityGroupRuleId")
            description = desc.get("Description")
            if not rule_id:
                continue
            # Find rule by rule id in ingress rules
            found_rule = None
            for rule in security_group.get("IpPermissions", []):
                if rule.get("SecurityGroupRuleId") == rule_id:
                    found_rule = rule
                    break
            if not found_rule:
                raise Exception(f"InvalidSecurityGroupRuleId.NotFound: The security group rule '{rule_id}' does not exist")
            if description is not None:
                found_rule["Description"] = description
            else:
                found_rule.pop("Description", None)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class SecuritygroupsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AuthorizeSecurityGroupEgress", self.authorize_security_group_egress)
        self.register_action("AuthorizeSecurityGroupIngress", self.authorize_security_group_ingress)
        self.register_action("CreateSecurityGroup", self.create_security_group)
        self.register_action("DeleteSecurityGroup", self.delete_security_group)
        self.register_action("DescribeSecurityGroupRules", self.describe_security_group_rules)
        self.register_action("DescribeSecurityGroups", self.describe_security_groups)
        self.register_action("ModifySecurityGroupRules", self.modify_security_group_rules)
        self.register_action("RevokeSecurityGroupEgress", self.revoke_security_group_egress)
        self.register_action("RevokeSecurityGroupIngress", self.revoke_security_group_ingress)
        self.register_action("UpdateSecurityGroupRuleDescriptionsEgress", self.update_security_group_rule_descriptions_egress)
        self.register_action("UpdateSecurityGroupRuleDescriptionsIngress", self.update_security_group_rule_descriptions_ingress)
        self.register_action("AssociateSecurityGroupVpc", self.associate_security_group_vpc)
        self.register_action("AuthorizeSecurityGroupEgress", self.authorize_security_group_egress)
        self.register_action("AuthorizeSecurityGroupIngress", self.authorize_security_group_ingress)
        self.register_action("CreateSecurityGroup", self.create_security_group)
        self.register_action("DeleteSecurityGroup", self.delete_security_group)
        self.register_action("DescribeSecurityGroupReferences", self.describe_security_group_references)
        self.register_action("DescribeSecurityGroups", self.describe_security_groups)
        self.register_action("DescribeSecurityGroupVpcAssociations", self.describe_security_group_vpc_associations)
        self.register_action("DescribeStaleSecurityGroups", self.describe_stale_security_groups)
        self.register_action("DisassociateSecurityGroupVpc", self.disassociate_security_group_vpc)
        self.register_action("GetSecurityGroupsForVpc", self.get_security_groups_for_vpc)
        self.register_action("ModifySecurityGroupRules", self.modify_security_group_rules)
        self.register_action("RevokeSecurityGroupEgress", self.revoke_security_group_egress)
        self.register_action("RevokeSecurityGroupIngress", self.revoke_security_group_ingress)
        self.register_action("UpdateSecurityGroupRuleDescriptionsEgress", self.update_security_group_rule_descriptions_egress)
        self.register_action("UpdateSecurityGroupRuleDescriptionsIngress", self.update_security_group_rule_descriptions_ingress)

    def authorize_security_group_egress(self, params):
        return self.backend.authorize_security_group_egress(params)

    def authorize_security_group_ingress(self, params):
        return self.backend.authorize_security_group_ingress(params)

    def create_security_group(self, params):
        return self.backend.create_security_group(params)

    def delete_security_group(self, params):
        return self.backend.delete_security_group(params)

    def describe_security_group_rules(self, params):
        return self.backend.describe_security_group_rules(params)

    def describe_security_groups(self, params):
        return self.backend.describe_security_groups(params)

    def modify_security_group_rules(self, params):
        return self.backend.modify_security_group_rules(params)

    def revoke_security_group_egress(self, params):
        return self.backend.revoke_security_group_egress(params)

    def revoke_security_group_ingress(self, params):
        return self.backend.revoke_security_group_ingress(params)

    def update_security_group_rule_descriptions_egress(self, params):
        return self.backend.update_security_group_rule_descriptions_egress(params)

    def update_security_group_rule_descriptions_ingress(self, params):
        return self.backend.update_security_group_rule_descriptions_ingress(params)

    def associate_security_group_vpc(self, params):
        return self.backend.associate_security_group_vpc(params)

    def authorize_security_group_egress(self, params):
        return self.backend.authorize_security_group_egress(params)

    def authorize_security_group_ingress(self, params):
        return self.backend.authorize_security_group_ingress(params)

    def create_security_group(self, params):
        return self.backend.create_security_group(params)

    def delete_security_group(self, params):
        return self.backend.delete_security_group(params)

    def describe_security_group_references(self, params):
        return self.backend.describe_security_group_references(params)

    def describe_security_groups(self, params):
        return self.backend.describe_security_groups(params)

    def describe_security_group_vpc_associations(self, params):
        return self.backend.describe_security_group_vpc_associations(params)

    def describe_stale_security_groups(self, params):
        return self.backend.describe_stale_security_groups(params)

    def disassociate_security_group_vpc(self, params):
        return self.backend.disassociate_security_group_vpc(params)

    def get_security_groups_for_vpc(self, params):
        return self.backend.get_security_groups_for_vpc(params)

    def modify_security_group_rules(self, params):
        return self.backend.modify_security_group_rules(params)

    def revoke_security_group_egress(self, params):
        return self.backend.revoke_security_group_egress(params)

    def revoke_security_group_ingress(self, params):
        return self.backend.revoke_security_group_ingress(params)

    def update_security_group_rule_descriptions_egress(self, params):
        return self.backend.update_security_group_rule_descriptions_egress(params)

    def update_security_group_rule_descriptions_ingress(self, params):
        return self.backend.update_security_group_rule_descriptions_ingress(params)
