from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


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
class IcmpTypeCode:
    code: Optional[int] = None  # -1 means all codes for the specified ICMP type
    type: Optional[int] = None  # -1 means all types

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.code is not None:
            d["Code"] = self.code
        if self.type is not None:
            d["Type"] = self.type
        return d


@dataclass
class PortRange:
    from_port: Optional[int] = None
    to_port: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.from_port is not None:
            d["From"] = self.from_port
        if self.to_port is not None:
            d["To"] = self.to_port
        return d


@dataclass
class NetworkAclEntry:
    rule_number: Optional[int] = None
    protocol: Optional[str] = None  # "-1" means all protocols
    rule_action: Optional[str] = None  # "allow" or "deny"
    egress: Optional[bool] = None
    cidr_block: Optional[str] = None
    ipv6_cidr_block: Optional[str] = None
    icmp_type_code: Optional[IcmpTypeCode] = None
    port_range: Optional[PortRange] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.rule_number is not None:
            d["ruleNumber"] = self.rule_number
        if self.protocol is not None:
            d["protocol"] = self.protocol
        if self.rule_action is not None:
            d["ruleAction"] = self.rule_action
        if self.egress is not None:
            d["egress"] = self.egress
        if self.cidr_block is not None:
            d["cidrBlock"] = self.cidr_block
        if self.ipv6_cidr_block is not None:
            d["ipv6CidrBlock"] = self.ipv6_cidr_block
        if self.icmp_type_code is not None:
            d["icmpTypeCode"] = self.icmp_type_code.to_dict()
        if self.port_range is not None:
            d["portRange"] = self.port_range.to_dict()
        return d


@dataclass
class NetworkAclAssociation:
    network_acl_association_id: Optional[str] = None
    network_acl_id: Optional[str] = None
    subnet_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.network_acl_association_id is not None:
            d["networkAclAssociationId"] = self.network_acl_association_id
        if self.network_acl_id is not None:
            d["networkAclId"] = self.network_acl_id
        if self.subnet_id is not None:
            d["subnetId"] = self.subnet_id
        return d


@dataclass
class NetworkAcl:
    network_acl_id: str
    vpc_id: str
    owner_id: Optional[str] = None
    default: Optional[bool] = False
    entry_set: List[NetworkAclEntry] = field(default_factory=list)
    association_set: List[NetworkAclAssociation] = field(default_factory=list)
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "networkAclId": self.network_acl_id,
            "vpcId": self.vpc_id,
            "ownerId": self.owner_id,
            "default": self.default,
            "entrySet": [entry.to_dict() for entry in self.entry_set],
            "associationSet": [assoc.to_dict() for assoc in self.association_set],
            "tagSet": [tag.to_dict() for tag in self.tag_set],
        }


class RuleAction(Enum):
    ALLOW = "allow"
    DENY = "deny"


class NetworkACLsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.network_acls or similar

    def create_network_acl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_id = params.get("VpcId")
        if not vpc_id:
            raise Exception("Missing required parameter VpcId")
        # Validate VPC exists
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise Exception(f"InvalidVpcID.NotFound: The vpc ID '{vpc_id}' does not exist")

        # Idempotency: if ClientToken provided, check if already created
        client_token = params.get("ClientToken")
        if client_token:
            for acl in self.state.network_acls.values():
                if getattr(acl, "client_token", None) == client_token:
                    # Return existing ACL info
                    return {
                        "clientToken": client_token,
                        "networkAcl": acl.to_dict(),
                        "requestId": self.generate_request_id(),
                    }

        # Generate network ACL ID
        network_acl_id = self.generate_unique_id("acl")

        # Parse TagSpecification.N if present
        tag_set = []
        tag_specifications = []
        # TagSpecification.N is an array of TagSpecification objects
        # The input params keys for tag specs are like TagSpecification.1.ResourceType, TagSpecification.1.Tags.1.Key, etc.
        # We need to parse all TagSpecification.N keys
        # We'll collect all keys starting with "TagSpecification."
        tag_spec_prefix = "TagSpecification."
        tag_spec_indices = set()
        for key in params.keys():
            if key.startswith(tag_spec_prefix):
                # Extract index after TagSpecification.
                rest = key[len(tag_spec_prefix):]
                idx_str = rest.split(".", 1)[0]
                if idx_str.isdigit():
                    tag_spec_indices.add(int(idx_str))
        for idx in sorted(tag_spec_indices):
            resource_type = params.get(f"TagSpecification.{idx}.ResourceType")
            if resource_type is None:
                continue
            tags = []
            # Parse tags for this tag spec
            tag_prefix = f"TagSpecification.{idx}.Tags."
            tag_indices = set()
            for key in params.keys():
                if key.startswith(tag_prefix):
                    rest = key[len(tag_prefix):]
                    tag_idx_str = rest.split(".", 1)[0]
                    if tag_idx_str.isdigit():
                        tag_indices.add(int(tag_idx_str))
            for tag_idx in sorted(tag_indices):
                key_tag = params.get(f"{tag_prefix}{tag_idx}.Key")
                value_tag = params.get(f"{tag_prefix}{tag_idx}.Value")
                if key_tag is not None:
                    tags.append(Tag(key=key_tag, value=value_tag if value_tag is not None else ""))
            tag_specifications.append(TagSpecification(resource_type=resource_type, tags=tags))
            if resource_type == "network-acl":
                tag_set.extend(tags)

        # Create default entries for the ACL as per example:
        # IPv4 egress deny rule 32767
        # IPv4 ingress deny rule 32767
        # IPv6 egress deny rule 32768
        # IPv6 ingress deny rule 32768
        entry_set = [
            NetworkAclEntry(
                rule_number=32767,
                protocol="all",
                rule_action="deny",
                egress=True,
                cidr_block="0.0.0.0/0",
                ipv6_cidr_block=None,
                icmp_type_code=None,
                port_range=None,
            ),
            NetworkAclEntry(
                rule_number=32767,
                protocol="all",
                rule_action="deny",
                egress=False,
                cidr_block="0.0.0.0/0",
                ipv6_cidr_block=None,
                icmp_type_code=None,
                port_range=None,
            ),
            NetworkAclEntry(
                rule_number=32768,
                protocol="all",
                rule_action="deny",
                egress=True,
                cidr_block=None,
                ipv6_cidr_block="::/0",
                icmp_type_code=None,
                port_range=None,
            ),
            NetworkAclEntry(
                rule_number=32768,
                protocol="all",
                rule_action="deny",
                egress=False,
                cidr_block=None,
                ipv6_cidr_block="::/0",
                icmp_type_code=None,
                port_range=None,
            ),
        ]

        # Create NetworkAcl object
        owner_id = self.get_owner_id()
        network_acl = NetworkAcl(
            network_acl_id=network_acl_id,
            vpc_id=vpc_id,
            owner_id=owner_id,
            default=False,
            entry_set=entry_set,
            association_set=[],
            tag_set=tag_set,
        )
        # Store client token for idempotency if provided
        if client_token:
            setattr(network_acl, "client_token", client_token)

        # Save to state
        self.state.network_acls[network_acl_id] = network_acl
        self.state.resources[network_acl_id] = network_acl

        return {
            "clientToken": client_token if client_token else None,
            "networkAcl": network_acl.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_network_acl_entry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_acl_id = params.get("NetworkAclId")
        if not network_acl_id:
            raise Exception("Missing required parameter NetworkAclId")
        network_acl = self.state.network_acls.get(network_acl_id)
        if not network_acl:
            raise Exception(f"InvalidNetworkAclID.NotFound: The network ACL ID '{network_acl_id}' does not exist")

        rule_number = params.get("RuleNumber")
        if rule_number is None:
            raise Exception("Missing required parameter RuleNumber")
        if not (1 <= rule_number <= 32766):
            raise Exception("InvalidParameterValue: RuleNumber must be between 1 and 32766")

        protocol = params.get("Protocol")
        if protocol is None:
            raise Exception("Missing required parameter Protocol")

        rule_action = params.get("RuleAction")
        if rule_action not in ("allow", "deny"):
            raise Exception("InvalidParameterValue: RuleAction must be 'allow' or 'deny'")

        egress = params.get("Egress")
        if egress is None:
            raise Exception("Missing required parameter Egress")

        cidr_block = params.get("CidrBlock")
        ipv6_cidr_block = params.get("Ipv6CidrBlock")

        icmp_param = params.get("Icmp")
        icmp_type_code = None
        if icmp_param:
            code = icmp_param.get("Code")
            type_ = icmp_param.get("Type")
            icmp_type_code = IcmpTypeCode(code=code, type=type_)

        port_range_param = params.get("PortRange")
        port_range = None
        if port_range_param:
            from_port = port_range_param.get("From")
            to_port = port_range_param.get("To")
            port_range = PortRange(from_port=from_port, to_port=to_port)

        # Validate protocol and required fields
        # Protocol "-1" means all protocols
        # If protocol is 6 (TCP) or 17 (UDP), PortRange is required
        # If protocol is 1 (ICMP) or 58 (ICMPv6) and IPv6 CIDR block specified, IcmpTypeCode is required
        # If protocol is 58 and IPv4 CIDR block specified, ICMP types and codes allowed regardless of specified

        # Normalize protocol to string for comparison
        protocol_str = str(protocol)
        if protocol_str in ("6", "17"):
            if port_range is None or port_range.from_port is None or port_range.to_port is None:
                raise Exception("Missing required PortRange for protocol TCP or UDP")
        if protocol_str == "58":
            if ipv6_cidr_block:
                if icmp_type_code is None or icmp_type_code.type is None or icmp_type_code.code is None:
                    raise Exception("Missing required ICMP type and code for protocol 58 with IPv6 CIDR block")

        # Check if rule number already exists for this egress/ingress in this ACL
        for entry in network_acl.entry_set:
            if entry.rule_number == rule_number and entry.egress == egress:
                raise Exception(f"NetworkAclEntryAlreadyExists: Rule number {rule_number} for egress={egress} already exists")

        # Create new entry
        new_entry = NetworkAclEntry(
            rule_number=rule_number,
            protocol=protocol_str,
            rule_action=rule_action,
            egress=egress,
            cidr_block=cidr_block,
            ipv6_cidr_block=ipv6_cidr_block,
            icmp_type_code=icmp_type_code,
            port_range=port_range,
        )

        # Add entry to ACL entry_set
        # Since state.network_acls is dict and entry_set is list, we must replace the list with a new list including new entry
        network_acl.entry_set = network_acl.entry_set + [new_entry]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def delete_network_acl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_acl_id = params.get("NetworkAclId")
        if not network_acl_id:
            raise Exception("Missing required parameter NetworkAclId")
        network_acl = self.state.network_acls.get(network_acl_id)
        if not network_acl:
            # LocalStack compatibility: Return success if not found (idempotent delete)
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Cannot delete default network ACL
        if network_acl.default:
            raise Exception("OperationNotPermitted: Cannot delete the default network ACL")

        # Cannot delete if associated with any subnet
        if network_acl.association_set and len(network_acl.association_set) > 0:
            raise Exception("DependencyViolation: The network ACL is associated with one or more subnets and cannot be deleted")

        # Delete from state
        del self.state.network_acls[network_acl_id]
        if network_acl_id in self.state.resources:
            del self.state.resources[network_acl_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def delete_network_acl_entry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        network_acl_id = params.get("NetworkAclId")
        if not network_acl_id:
            raise Exception("Missing required parameter NetworkAclId")
        network_acl = self.state.network_acls.get(network_acl_id)
        if not network_acl:
            raise Exception(f"InvalidNetworkAclID.NotFound: The network ACL ID '{network_acl_id}' does not exist")

        rule_number = params.get("RuleNumber")
        if rule_number is None:
            raise Exception("Missing required parameter RuleNumber")

        egress = params.get("Egress")
        if egress is None:
            raise Exception("Missing required parameter Egress")

        # Find entry to delete
        found = False
        new_entry_set = []
        for entry in network_acl.entry_set:
            if entry.rule_number == rule_number and entry.egress == egress:
                found = True
                continue
            new_entry_set.append(entry)
        if not found:
            # AWS does not error if entry not found, just returns success
            pass

        network_acl.entry_set = new_entry_set

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def describe_network_acls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Filters and pagination
        filters = []
        # Filters are passed as Filter.N.Name and Filter.N.Value.M
        filter_prefix = "Filter."
        filter_indices = set()
        for key in params.keys():
            if key.startswith(filter_prefix):
                rest = key[len(filter_prefix):]
                idx_str = rest.split(".", 1)[0]
                if idx_str.isdigit():
                    filter_indices.add(int(idx_str))
        for idx in sorted(filter_indices):
            name = params.get(f"Filter.{idx}.Name")
            values = []
            value_prefix = f"Filter.{idx}.Value."
            value_indices = set()
            for key in params.keys():
                if key.startswith(value_prefix):
                    rest = key[len(value_prefix):]
                    val_idx_str = rest.split(".", 1)[0]
                    if val_idx_str.isdigit():
                        value_indices.add(int(val_idx_str))
            for val_idx in sorted(value_indices):
                val = params.get(f"{value_prefix}{val_idx}")
                if val is not None:
                    values.append(val)
            if name:
                filters.append({"Name": name, "Values": values})

        # NetworkAclId.N filter
        network_acl_ids = []
        for key, value in params.items():
            if key.startswith("NetworkAclId."):
                network_acl_ids.append(value)

        # MaxResults and NextToken for pagination
        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise Exception("InvalidParameterValue: MaxResults must be between 5 and 1000")
            except Exception:
                raise Exception("InvalidParameterValue: MaxResults must be an integer")
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Collect all network ACLs
        all_acls = list(self.state.network_acls.values())

        # Filter by NetworkAclId if specified
        if network_acl_ids:
            all_acls = [acl for acl in all_acls if acl.network_acl_id in network_acl_ids]

        # Apply filters
        def acl_matches_filter(acl: NetworkAcl, filter_: Dict[str, Any]) -> bool:
            name = filter_["Name"]
            values = filter_["Values"]
            # Support filters as per docs:
            # association.association-id, association.network-acl-id, association.subnet-id,
            # default, entry.cidr, entry.icmp.code, entry.icmp.type, entry.ipv6-cidr,
            # entry.port-range.from, entry.port-range.to, entry.protocol, entry.rule-action,
            # entry.egress, entry.rule-number, network-acl-id, owner-id, tag:, tag-key, vpc-id

            if name == "association.association-id":
                for assoc in acl.association_set:
                    if assoc.network_acl_association_id in values:
                        return True
                return False
            if name == "association.network-acl-id":
                for assoc in acl.association_set:
                    if assoc.network_acl_id in values:
                        return True
                return False
            if name == "association.subnet-id":
                for assoc in acl.association_set:
                    if assoc.subnet_id in values:
                        return True
                return False
            if name == "default":
                # values are strings "true" or "false"
                val_str = "true" if acl.default else "false"
                return val_str in values
            if name.startswith("entry."):
                # entry filters apply to any entry in entry_set
                subname = name[6:]
                for entry in acl.entry_set:
                    if subname == "cidr":
                        if entry.cidr_block in values:
                            return True
                    elif subname == "icmp.code":
                        if entry.icmp_type_code and entry.icmp_type_code.code is not None:
                            if str(entry.icmp_type_code.code) in values:
                                return True
                    elif subname == "icmp.type":
                        if entry.icmp_type_code and entry.icmp_type_code.type is not None:
                            if str(entry.icmp_type_code.type) in values:
                                return True
                    elif subname == "ipv6-cidr":
                        if entry.ipv6_cidr_block in values:
                            return True
                    elif subname == "port-range.from":
                        if entry.port_range and entry.port_range.from_port is not None:
                            if str(entry.port_range.from_port) in values:
                                return True
                    elif subname == "port-range.to":
                        if entry.port_range and entry.port_range.to_port is not None:
                            if str(entry.port_range.to_port) in values:
                                return True
                    elif subname == "protocol":
                        if entry.protocol in values:
                            return True
                    elif subname == "rule-action":
                        if entry.rule_action in values:
                            return True
                    elif subname == "egress":
                        val_str = "true" if entry.egress else "false"
                        if val_str in values:
                            return True
                    elif subname == "rule-number":
                        if entry.rule_number is not None and str(entry.rule_number) in values:
                            return True
                return False
            if name == "network-acl-id":
                return acl.network_acl_id in values
            if name == "owner-id":
                return acl.owner_id in values
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in acl.tag_set:
                    if tag.key == tag_key and tag.value in values:
                        return True
                return False
            if name == "tag-key":
                for tag in acl.tag_set:
                    if tag.key in values:
                        return True
                return False
            if name == "vpc-id":
                return acl.vpc_id in values
            # Unknown filter name: ignore filter (AWS returns no results)
            return False

        filtered_acls = []
        for acl in all_acls:
            if not filters:
                filtered_acls.append(acl)
            else:
                # All filters must match (AND)
                if all(acl_matches_filter(acl, f) for f in filters):
                    filtered_acls.append(acl)

        # Pagination
        end_index = len(filtered_acls)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered_acls))
        page_acls = filtered_acls[start_index:end_index]

        # NextToken for next page
        new_next_token = None
        if end_index < len(filtered_acls):
            new_next_token = str(end_index)

        return {
            "networkAclSet": [acl.to_dict() for acl in page_acls],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def replace_network_acl_association(self, params: dict) -> dict:
        association_id = params.get("AssociationId")
        new_network_acl_id = params.get("NetworkAclId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # DryRun logic: check permissions, here we assume always allowed for simplicity
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not association_id:
            raise ValueError("AssociationId is required")
        if not new_network_acl_id:
            raise ValueError("NetworkAclId is required")

        # Find the current association by association_id
        current_association = None
        current_network_acl = None
        for acl in self.state.network_acls.values():
            for assoc in acl.association_set:
                if assoc.network_acl_association_id == association_id:
                    current_association = assoc
                    current_network_acl = acl
                    break
            if current_association:
                break

        if not current_association:
            raise ValueError(f"AssociationId {association_id} not found")

        # Validate new_network_acl_id exists
        new_network_acl = self.state.network_acls.get(new_network_acl_id)
        if not new_network_acl:
            raise ValueError(f"NetworkAclId {new_network_acl_id} not found")

        # The subnet_id is from the current association
        subnet_id = current_association.subnet_id

        # Remove the association from the old network ACL
        current_network_acl.association_set = [
            assoc for assoc in current_network_acl.association_set if assoc.network_acl_association_id != association_id
        ]

        # Create a new association id
        new_association_id = self.generate_unique_id(prefix="aclassoc-")

        # Create new association object
        new_association = NetworkAclAssociation(
            network_acl_association_id=new_association_id,
            network_acl_id=new_network_acl_id,
            subnet_id=subnet_id,
        )

        # Add new association to the new network ACL
        new_network_acl.association_set.append(new_association)

        # Update state resources for associations if needed
        self.state.resources[new_association_id] = new_association

        return {
            "requestId": self.generate_request_id(),
            "newAssociationId": new_association_id,
        }


    def replace_network_acl_entry(self, params: dict) -> dict:
        network_acl_id = params.get("NetworkAclId")
        rule_number = params.get("RuleNumber")
        protocol = params.get("Protocol")
        rule_action = params.get("RuleAction")
        egress = params.get("Egress")
        cidr_block = params.get("CidrBlock")
        ipv6_cidr_block = params.get("Ipv6CidrBlock")
        icmp = params.get("Icmp")
        port_range = params.get("PortRange")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # DryRun logic: check permissions, here we assume always allowed for simplicity
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate required parameters
        if not network_acl_id:
            raise ValueError("NetworkAclId is required")
        if rule_number is None:
            raise ValueError("RuleNumber is required")
        if protocol is None:
            raise ValueError("Protocol is required")
        if rule_action is None:
            raise ValueError("RuleAction is required")
        if egress is None:
            raise ValueError("Egress is required")

        # Validate rule_action value
        if rule_action not in ("allow", "deny"):
            raise ValueError("RuleAction must be 'allow' or 'deny'")

        # Validate protocol string: it can be "-1" or a number string
        # Accept protocol as string or int, convert to string for storage
        protocol_str = str(protocol)

        # Validate network ACL exists
        network_acl = self.state.network_acls.get(network_acl_id)
        if not network_acl:
            raise ValueError(f"NetworkAclId {network_acl_id} not found")

        # Find the entry to replace by rule_number and egress
        entry_to_replace = None
        for entry in network_acl.entry_set:
            if entry.rule_number == rule_number and entry.egress == egress:
                entry_to_replace = entry
                break

        if not entry_to_replace:
            raise ValueError(f"Entry with RuleNumber {rule_number} and Egress {egress} not found in NetworkAcl {network_acl_id}")

        # Parse IcmpTypeCode if provided
        icmp_type_code = None
        if icmp:
            code = icmp.get("Code")
            type_ = icmp.get("Type")
            icmp_type_code = IcmpTypeCode(code=code, type=type_)

        # Parse PortRange if provided
        port_range_obj = None
        if port_range:
            from_port = port_range.get("From")
            to_port = port_range.get("To")
            port_range_obj = PortRange(from_port=from_port, to_port=to_port)

        # Update the entry fields
        entry_to_replace.protocol = protocol_str
        entry_to_replace.rule_action = rule_action
        entry_to_replace.egress = egress
        entry_to_replace.cidr_block = cidr_block
        entry_to_replace.ipv6_cidr_block = ipv6_cidr_block
        entry_to_replace.icmp_type_code = icmp_type_code
        entry_to_replace.port_range = port_range_obj

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class NetworkACLsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateNetworkAcl", self.create_network_acl)
        self.register_action("CreateNetworkAclEntry", self.create_network_acl_entry)
        self.register_action("DeleteNetworkAcl", self.delete_network_acl)
        self.register_action("DeleteNetworkAclEntry", self.delete_network_acl_entry)
        self.register_action("DescribeNetworkAcls", self.describe_network_acls)
        self.register_action("ReplaceNetworkAclAssociation", self.replace_network_acl_association)
        self.register_action("ReplaceNetworkAclEntry", self.replace_network_acl_entry)

    def create_network_acl(self, params):
        return self.backend.create_network_acl(params)

    def create_network_acl_entry(self, params):
        return self.backend.create_network_acl_entry(params)

    def delete_network_acl(self, params):
        return self.backend.delete_network_acl(params)

    def delete_network_acl_entry(self, params):
        return self.backend.delete_network_acl_entry(params)

    def describe_network_acls(self, params):
        return self.backend.describe_network_acls(params)

    def replace_network_acl_association(self, params):
        return self.backend.replace_network_acl_association(params)

    def replace_network_acl_entry(self, params):
        return self.backend.replace_network_acl_entry(params)
