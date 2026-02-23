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
class NetworkACL:
    association_set: List[Any] = field(default_factory=list)
    default: bool = False
    entry_set: List[Any] = field(default_factory=list)
    network_acl_id: str = ""
    owner_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    vpc_id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "associationSet": self.association_set,
            "default": self.default,
            "entrySet": self.entry_set,
            "networkAclId": self.network_acl_id,
            "ownerId": self.owner_id,
            "tagSet": self.tag_set,
            "vpcId": self.vpc_id,
        }

class NetworkACL_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.network_acls  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.vpcs.get(params['vpc_id']).network_acl_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).network_acl_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], names: List[str]):
        for name in names:
            value = params.get(name)
            if value is None or value == "":
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(self, store: Dict[str, Any], resource_id: str, error_code: str, message: Optional[str] = None):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message or f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources = []
        for resource_id in resource_ids:
            resource = store.get(resource_id)
            if not resource:
                return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
            resources.append(resource)
        return resources, None

    def _build_entry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        rule_number_value = params.get("RuleNumber")
        rule_number: Any = None
        if rule_number_value is not None and rule_number_value != "":
            try:
                rule_number = int(rule_number_value)
            except (TypeError, ValueError):
                rule_number = rule_number_value
        egress_value = params.get("Egress")
        egress = str2bool(egress_value) if egress_value is not None else False
        return {
            "cidrBlock": params.get("CidrBlock"),
            "egress": egress,
            "icmpTypeCode": params.get("Icmp"),
            "ipv6CidrBlock": params.get("Ipv6CidrBlock"),
            "portRange": params.get("PortRange"),
            "protocol": params.get("Protocol"),
            "ruleAction": params.get("RuleAction"),
            "ruleNumber": rule_number,
        }

    def _find_entry_index(self, entries: List[Dict[str, Any]], egress: Any, rule_number: Any) -> Optional[int]:
        normalized_egress = egress if isinstance(egress, bool) else str2bool(egress)
        for idx, entry in enumerate(entries or []):
            if entry.get("egress") == normalized_egress and entry.get("ruleNumber") == rule_number:
                return idx
        return None

    def CreateNetworkAcl(self, params: Dict[str, Any]):
        """Creates a network ACL in a VPC. Network ACLs provide an optional layer of security (in addition to security groups) for the instances in your VPC. For more information, seeNetwork ACLsin theAmazon VPC User Guide."""

        error = self._require_params(params, ["VpcId"])
        if error:
            return error

        vpc_id = params.get("VpcId")
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            resource_type = spec.get("ResourceType")
            if resource_type and resource_type != "network-acl":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        network_acl_id = self._generate_id("acl")
        resource = NetworkACL(
            association_set=[],
            default=False,
            entry_set=[],
            network_acl_id=network_acl_id,
            owner_id=getattr(vpc, "owner_id", ""),
            tag_set=tag_set,
            vpc_id=vpc_id,
        )
        self.resources[network_acl_id] = resource

        if hasattr(vpc, "network_acl_ids"):
            vpc.network_acl_ids.append(network_acl_id)

        return {
            'clientToken': params.get("ClientToken"),
            'networkAcl': resource.to_dict(),
            }

    def CreateNetworkAclEntry(self, params: Dict[str, Any]):
        """Creates an entry (a rule) in a network ACL with the specified rule number. Each network ACL has a set of numbered ingress rules 
		        and a separate set of numbered egress rules. When determining whether a packet should be allowed in or out of a subnet associated 
		        with the ACL, we pro"""

        error = self._require_params(params, ["Egress", "NetworkAclId", "Protocol", "RuleAction", "RuleNumber"])
        if error:
            return error

        network_acl_id = params.get("NetworkAclId")
        resource, error = self._get_resource_or_error(
            self.resources,
            network_acl_id,
            "InvalidNetworkAclID.NotFound",
            f"The ID '{network_acl_id}' does not exist",
        )
        if error:
            return error

        entry = self._build_entry(params)
        existing_index = self._find_entry_index(resource.entry_set, entry.get("egress"), entry.get("ruleNumber"))
        if existing_index is not None:
            return create_error_response("InvalidParameterValue", "Network ACL entry already exists")

        resource.entry_set.append(entry)

        return {
            'return': True,
            }

    def DeleteNetworkAcl(self, params: Dict[str, Any]):
        """Deletes the specified network ACL. You can't delete the ACL if it's associated with any subnets. You can't delete the default network ACL."""

        error = self._require_params(params, ["NetworkAclId"])
        if error:
            return error

        network_acl_id = params.get("NetworkAclId")
        resource, error = self._get_resource_or_error(
            self.resources,
            network_acl_id,
            "InvalidNetworkAclID.NotFound",
            f"The ID '{network_acl_id}' does not exist",
        )
        if error:
            return error

        if resource.default:
            return create_error_response("DependencyViolation", "The default network ACL cannot be deleted")

        if resource.association_set:
            return create_error_response("DependencyViolation", "Network ACL is associated with one or more subnets")

        vpc = self.state.vpcs.get(resource.vpc_id)
        if vpc and hasattr(vpc, "network_acl_ids") and network_acl_id in vpc.network_acl_ids:
            vpc.network_acl_ids.remove(network_acl_id)

        del self.resources[network_acl_id]

        return {
            'return': True,
            }

    def DeleteNetworkAclEntry(self, params: Dict[str, Any]):
        """Deletes the specified ingress or egress entry (rule) from the specified network ACL."""

        error = self._require_params(params, ["Egress", "NetworkAclId", "RuleNumber"])
        if error:
            return error

        network_acl_id = params.get("NetworkAclId")
        resource, error = self._get_resource_or_error(
            self.resources,
            network_acl_id,
            "InvalidNetworkAclID.NotFound",
            f"The ID '{network_acl_id}' does not exist",
        )
        if error:
            return error

        rule_number = params.get("RuleNumber")
        try:
            rule_number = int(rule_number)
        except (TypeError, ValueError):
            pass

        egress_value = params.get("Egress")
        egress = str2bool(egress_value) if egress_value is not None else False
        entry_index = self._find_entry_index(resource.entry_set, egress, rule_number)
        if entry_index is None:
            return create_error_response("InvalidParameterValue", "Network ACL entry not found")

        resource.entry_set.pop(entry_index)

        return {
            'return': True,
            }

    def DescribeNetworkAcls(self, params: Dict[str, Any]):
        """Describes your network ACLs. The default is to describe all your network ACLs. 
           Alternatively, you can specify specific network ACL IDs or filter the results to
           include only the network ACLs that match specific criteria. For more information, seeNetwork ACLsin theAmazon VPC Use"""

        network_acl_ids = params.get("NetworkAclId.N", [])
        if network_acl_ids:
            resources, error = self._get_resources_by_ids(
                self.resources,
                network_acl_ids,
                "InvalidNetworkAclID.NotFound",
            )
            if error:
                return error
        else:
            resources = list(self.resources.values())

        filters = params.get("Filter.N", [])
        resources = apply_filters(resources, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        page = resources[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(resources):
            new_next_token = str(start_index + max_results)

        return {
            'networkAclSet': [resource.to_dict() for resource in page],
            'nextToken': new_next_token,
            }

    def ReplaceNetworkAclAssociation(self, params: Dict[str, Any]):
        """Changes which network ACL a subnet is associated with. By default when you create a
			subnet, it's automatically associated with the default network ACL. For more
			information, seeNetwork ACLsin theAmazon VPC User Guide. This is an idempotent operation."""

        error = self._require_params(params, ["AssociationId", "NetworkAclId"])
        if error:
            return error

        association_id = params.get("AssociationId")
        network_acl_id = params.get("NetworkAclId")

        target_acl, error = self._get_resource_or_error(
            self.resources,
            network_acl_id,
            "InvalidNetworkAclID.NotFound",
            f"The ID '{network_acl_id}' does not exist",
        )
        if error:
            return error

        current_acl = None
        association = None
        for acl in self.resources.values():
            for assoc in acl.association_set:
                if assoc.get("networkAclAssociationId") == association_id:
                    current_acl = acl
                    association = assoc
                    break
            if association:
                break

        if not association:
            return create_error_response("InvalidAssociationID.NotFound", f"The ID '{association_id}' does not exist")

        if current_acl and current_acl.network_acl_id == target_acl.network_acl_id:
            return {
                'newAssociationId': association_id,
                }

        if current_acl and association in current_acl.association_set:
            current_acl.association_set.remove(association)

        new_association_id = self._generate_id("aclassoc")
        new_association = {
            "networkAclAssociationId": new_association_id,
            "networkAclId": network_acl_id,
            "subnetId": association.get("subnetId"),
        }
        target_acl.association_set.append(new_association)

        subnet_id = association.get("subnetId")
        subnet = self.state.subnets.get(subnet_id) if subnet_id else None
        if subnet is not None and hasattr(subnet, "network_acl_id"):
            subnet.network_acl_id = network_acl_id

        return {
            'newAssociationId': new_association_id,
            }

    def ReplaceNetworkAclEntry(self, params: Dict[str, Any]):
        """Replaces an entry (rule) in a network ACL. For more information, seeNetwork ACLsin theAmazon VPC User Guide."""

        error = self._require_params(params, ["Egress", "NetworkAclId", "Protocol", "RuleAction", "RuleNumber"])
        if error:
            return error

        network_acl_id = params.get("NetworkAclId")
        resource, error = self._get_resource_or_error(
            self.resources,
            network_acl_id,
            "InvalidNetworkAclID.NotFound",
            f"The ID '{network_acl_id}' does not exist",
        )
        if error:
            return error

        entry = self._build_entry(params)
        existing_index = self._find_entry_index(resource.entry_set, entry.get("egress"), entry.get("ruleNumber"))
        if existing_index is not None:
            resource.entry_set[existing_index] = entry
        else:
            resource.entry_set.append(entry)

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'eni') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class networkacl_RequestParser:
    @staticmethod
    def parse_create_network_acl_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_create_network_acl_entry_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CidrBlock": get_scalar(md, "CidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Egress": get_scalar(md, "Egress"),
            "Icmp": get_scalar(md, "Icmp"),
            "Ipv6CidrBlock": get_scalar(md, "Ipv6CidrBlock"),
            "NetworkAclId": get_scalar(md, "NetworkAclId"),
            "PortRange": get_scalar(md, "PortRange"),
            "Protocol": get_scalar(md, "Protocol"),
            "RuleAction": get_scalar(md, "RuleAction"),
            "RuleNumber": get_int(md, "RuleNumber"),
        }

    @staticmethod
    def parse_delete_network_acl_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkAclId": get_scalar(md, "NetworkAclId"),
        }

    @staticmethod
    def parse_delete_network_acl_entry_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Egress": get_scalar(md, "Egress"),
            "NetworkAclId": get_scalar(md, "NetworkAclId"),
            "RuleNumber": get_int(md, "RuleNumber"),
        }

    @staticmethod
    def parse_describe_network_acls_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NetworkAclId.N": get_indexed_list(md, "NetworkAclId"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_replace_network_acl_association_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkAclId": get_scalar(md, "NetworkAclId"),
        }

    @staticmethod
    def parse_replace_network_acl_entry_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CidrBlock": get_scalar(md, "CidrBlock"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Egress": get_scalar(md, "Egress"),
            "Icmp": get_scalar(md, "Icmp"),
            "Ipv6CidrBlock": get_scalar(md, "Ipv6CidrBlock"),
            "NetworkAclId": get_scalar(md, "NetworkAclId"),
            "PortRange": get_scalar(md, "PortRange"),
            "Protocol": get_scalar(md, "Protocol"),
            "RuleAction": get_scalar(md, "RuleAction"),
            "RuleNumber": get_int(md, "RuleNumber"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateNetworkAcl": networkacl_RequestParser.parse_create_network_acl_request,
            "CreateNetworkAclEntry": networkacl_RequestParser.parse_create_network_acl_entry_request,
            "DeleteNetworkAcl": networkacl_RequestParser.parse_delete_network_acl_request,
            "DeleteNetworkAclEntry": networkacl_RequestParser.parse_delete_network_acl_entry_request,
            "DescribeNetworkAcls": networkacl_RequestParser.parse_describe_network_acls_request,
            "ReplaceNetworkAclAssociation": networkacl_RequestParser.parse_replace_network_acl_association_request,
            "ReplaceNetworkAclEntry": networkacl_RequestParser.parse_replace_network_acl_entry_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class networkacl_ResponseSerializer:
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
                xml_parts.extend(networkacl_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(networkacl_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(networkacl_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(networkacl_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(networkacl_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(networkacl_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_network_acl_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateNetworkAclResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize networkAcl
        _networkAcl_key = None
        if "networkAcl" in data:
            _networkAcl_key = "networkAcl"
        elif "NetworkAcl" in data:
            _networkAcl_key = "NetworkAcl"
        if _networkAcl_key:
            param_data = data[_networkAcl_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkAcl>')
            xml_parts.extend(networkacl_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</networkAcl>')
        xml_parts.append(f'</CreateNetworkAclResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_network_acl_entry_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateNetworkAclEntryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CreateNetworkAclEntryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_network_acl_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteNetworkAclResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteNetworkAclResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_network_acl_entry_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteNetworkAclEntryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteNetworkAclEntryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_network_acls_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeNetworkAclsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkAclSet
        _networkAclSet_key = None
        if "networkAclSet" in data:
            _networkAclSet_key = "networkAclSet"
        elif "NetworkAclSet" in data:
            _networkAclSet_key = "NetworkAclSet"
        elif "NetworkAcls" in data:
            _networkAclSet_key = "NetworkAcls"
        if _networkAclSet_key:
            param_data = data[_networkAclSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<networkAclSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(networkacl_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</networkAclSet>')
            else:
                xml_parts.append(f'{indent_str}<networkAclSet/>')
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
        xml_parts.append(f'</DescribeNetworkAclsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_replace_network_acl_association_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReplaceNetworkAclAssociationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize newAssociationId
        _newAssociationId_key = None
        if "newAssociationId" in data:
            _newAssociationId_key = "newAssociationId"
        elif "NewAssociationId" in data:
            _newAssociationId_key = "NewAssociationId"
        if _newAssociationId_key:
            param_data = data[_newAssociationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<newAssociationId>{esc(str(param_data))}</newAssociationId>')
        xml_parts.append(f'</ReplaceNetworkAclAssociationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_replace_network_acl_entry_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReplaceNetworkAclEntryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ReplaceNetworkAclEntryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateNetworkAcl": networkacl_ResponseSerializer.serialize_create_network_acl_response,
            "CreateNetworkAclEntry": networkacl_ResponseSerializer.serialize_create_network_acl_entry_response,
            "DeleteNetworkAcl": networkacl_ResponseSerializer.serialize_delete_network_acl_response,
            "DeleteNetworkAclEntry": networkacl_ResponseSerializer.serialize_delete_network_acl_entry_response,
            "DescribeNetworkAcls": networkacl_ResponseSerializer.serialize_describe_network_acls_response,
            "ReplaceNetworkAclAssociation": networkacl_ResponseSerializer.serialize_replace_network_acl_association_response,
            "ReplaceNetworkAclEntry": networkacl_ResponseSerializer.serialize_replace_network_acl_entry_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

