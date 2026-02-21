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
class BYOASN:
    asn: str = ""
    ipam_id: str = ""
    state: str = ""
    status_message: str = ""

    resource_type: str = "byoasn"
    cidr_associations: List[str] = field(default_factory=list)
    asn_authorization_context: Dict[str, Any] = field(default_factory=dict)
    token_id: str = ""
    token_value: str = ""
    token_name: str = ""
    token_arn: str = ""
    ipam_arn: str = ""
    ipam_region: str = ""
    not_after: Optional[str] = None
    token_status: str = ""
    tag_set: List[Dict[str, str]] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "asn": self.asn,
            "ipamId": self.ipam_id,
            "state": self.state,
            "statusMessage": self.status_message,
            "cidrAssociations": self.cidr_associations,
            "asnAuthorizationContext": self.asn_authorization_context,
            "tokenId": self.token_id,
            "tokenValue": self.token_value,
            "tokenName": self.token_name,
            "tokenArn": self.token_arn,
            "ipamArn": self.ipam_arn,
            "ipamRegion": self.ipam_region,
            "notAfter": self.not_after,
            "tokenStatus": self.token_status,
            "tagSet": self.tag_set,
        }

class BYOASN_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.byoasn  # alias to shared store

    def _find_byoasn(self, asn: str, ipam_id: Optional[str] = None) -> Optional[BYOASN]:
        for resource in self.resources.values():
            if resource.resource_type != "byoasn":
                continue
            if resource.asn != asn:
                continue
            if ipam_id and resource.ipam_id != ipam_id:
                continue
            return resource
        return None

    def _find_verification_token(self, token_id: str) -> Optional[BYOASN]:
        for resource in self.resources.values():
            if resource.resource_type != "verification-token":
                continue
            if resource.token_id == token_id:
                return resource
        return None

    def _list_verification_tokens(self) -> List[BYOASN]:
        return [resource for resource in self.resources.values() if resource.resource_type == "verification-token"]


    def AssociateIpamByoasn(self, params: Dict[str, Any]):
        """Associates your Autonomous System Number (ASN) with a BYOIP CIDR that you own in the same AWS Region. 
            For more information, seeTutorial: Bring your ASN to IPAMin theAmazon VPC IPAM guide. After the association succeeds, the ASN is eligible for 
            advertisement. You can view th"""

        asn = params.get("Asn")
        if not asn:
            return create_error_response("MissingParameter", "Missing required parameter: Asn")
        cidr = params.get("Cidr")
        if not cidr:
            return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        resource = self._find_byoasn(asn)
        if not resource:
            return create_error_response("InvalidAsn.NotFound", f"The ASN '{asn}' does not exist")

        if cidr not in resource.cidr_associations:
            resource.cidr_associations.append(cidr)

        return {
            'asnAssociation': {
                'asn': asn,
                'cidr': cidr,
                'state': "associated",
                'statusMessage': resource.status_message,
                },
            }

    def CreateIpamExternalResourceVerificationToken(self, params: Dict[str, Any]):
        """Create a verification token. A verification token is an AWS-generated random value that you can use to prove ownership of an external resource. For example, you can use a verification token to validate that you control a public IP address range when you bring an IP address range to AWS (BYOIP)."""

        ipam_id = params.get("IpamId")
        if not ipam_id:
            return create_error_response("MissingParameter", "Missing required parameter: IpamId")

        ipam = self.state.ipams.get(ipam_id)
        if not ipam:
            return create_error_response("InvalidIpamId.NotFound", f"IPAM '{ipam_id}' does not exist.")

        tag_set = []
        for spec in params.get("TagSpecification.N", []) or []:
            for tag in spec.get("Tags", []) or []:
                tag_set.append({"Key": tag.get("Key", ""), "Value": tag.get("Value", "")})

        token_id = self._generate_id("ipam-ert")
        token_value = uuid.uuid4().hex
        token_name = params.get("ClientToken") or token_id
        not_after = datetime.now(timezone.utc).isoformat()
        ipam_region = getattr(ipam, "region", None) or getattr(ipam, "ipam_region", None) or "us-east-1"
        ipam_arn = getattr(ipam, "arn", None) or getattr(ipam, "ipam_arn", None) or f"arn:aws:ec2:{ipam_region}::ipam/{ipam_id}"
        token_arn = f"arn:aws:ec2:{ipam_region}::ipam-external-resource-verification-token/{token_id}"

        resource = BYOASN(
            asn="",
            ipam_id=ipam_id,
            state="available",
            status_message="",
            resource_type="verification-token",
            token_id=token_id,
            token_value=token_value,
            token_name=token_name,
            token_arn=token_arn,
            ipam_arn=ipam_arn,
            ipam_region=ipam_region,
            not_after=not_after,
            token_status="active",
            tag_set=tag_set,
        )
        self.resources[token_id] = resource

        return {
            'ipamExternalResourceVerificationToken': {
                'ipamArn': resource.ipam_arn,
                'ipamExternalResourceVerificationTokenArn': resource.token_arn,
                'ipamExternalResourceVerificationTokenId': resource.token_id,
                'ipamId': resource.ipam_id,
                'ipamRegion': resource.ipam_region,
                'notAfter': resource.not_after,
                'state': resource.state,
                'status': resource.token_status,
                'tagSet': resource.tag_set,
                'tokenName': resource.token_name,
                'tokenValue': resource.token_value,
                },
            }

    def DeleteIpamExternalResourceVerificationToken(self, params: Dict[str, Any]):
        """Delete a verification token. A verification token is an AWS-generated random value that you can use to prove ownership of an external resource. For example, you can use a verification token to validate that you control a public IP address range when you bring an IP address range to AWS (BYOIP)."""

        token_id = params.get("IpamExternalResourceVerificationTokenId")
        if not token_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: IpamExternalResourceVerificationTokenId",
            )

        resource = self._find_verification_token(token_id)
        if not resource:
            return create_error_response(
                "InvalidIpamExternalResourceVerificationTokenId.NotFound",
                f"The ID '{token_id}' does not exist",
            )

        self.resources.pop(token_id, None)

        return {
            'ipamExternalResourceVerificationToken': {
                'ipamArn': resource.ipam_arn,
                'ipamExternalResourceVerificationTokenArn': resource.token_arn,
                'ipamExternalResourceVerificationTokenId': resource.token_id,
                'ipamId': resource.ipam_id,
                'ipamRegion': resource.ipam_region,
                'notAfter': resource.not_after,
                'state': resource.state,
                'status': resource.token_status,
                'tagSet': resource.tag_set,
                'tokenName': resource.token_name,
                'tokenValue': resource.token_value,
                },
            }

    def DeprovisionIpamByoasn(self, params: Dict[str, Any]):
        """Deprovisions your Autonomous System Number (ASN) from your AWS account. This action can only be called after any BYOIP CIDR associations are removed from your AWS account withDisassociateIpamByoasn.
            For more information, seeTutorial: Bring your ASN to IPAMin theAmazon VPC IPAM guide."""

        asn = params.get("Asn")
        if not asn:
            return create_error_response("MissingParameter", "Missing required parameter: Asn")
        ipam_id = params.get("IpamId")
        if not ipam_id:
            return create_error_response("MissingParameter", "Missing required parameter: IpamId")

        ipam = self.state.ipams.get(ipam_id)
        if not ipam:
            return create_error_response("InvalidIpamId.NotFound", f"IPAM '{ipam_id}' does not exist.")

        resource = self._find_byoasn(asn, ipam_id)
        if not resource:
            return create_error_response("InvalidAsn.NotFound", f"The ASN '{asn}' does not exist")

        if resource.cidr_associations:
            return create_error_response(
                "DependencyViolation",
                "ASN has associated CIDRs and cannot be deprovisioned.",
            )

        for key, value in list(self.resources.items()):
            if value is resource:
                del self.resources[key]
                break

        return {
            'byoasn': {
                'asn': resource.asn,
                'ipamId': resource.ipam_id,
                'state': "deprovisioned",
                'statusMessage': resource.status_message,
                },
            }

    def DescribeIpamByoasn(self, params: Dict[str, Any]):
        """Describes your Autonomous System Numbers (ASNs), their provisioning statuses, and the BYOIP CIDRs with which they are associated. For more information, seeTutorial: Bring your ASN to IPAMin theAmazon VPC IPAM guide."""

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start = 0
        if next_token:
            try:
                start = int(next_token)
            except (TypeError, ValueError):
                start = 0

        byoasn_resources = [resource for resource in self.resources.values() if resource.resource_type == "byoasn"]
        byoasn_dicts = [resource.to_dict() for resource in byoasn_resources]
        sliced = byoasn_dicts[start:start + max_results]
        new_next_token = None
        if start + max_results < len(byoasn_dicts):
            new_next_token = str(start + max_results)

        return {
            'byoasnSet': sliced,
            'nextToken': new_next_token,
            }

    def DescribeIpamExternalResourceVerificationTokens(self, params: Dict[str, Any]):
        """Describe verification tokens. A verification token is an AWS-generated random value that you can use to prove ownership of an external resource. For example, you can use a verification token to validate that you control a public IP address range when you bring an IP address range to AWS (BYOIP)."""

        token_ids = params.get("IpamExternalResourceVerificationTokenId.N", []) or []
        if token_ids:
            for token_id in token_ids:
                if not self._find_verification_token(token_id):
                    return create_error_response(
                        "InvalidIpamExternalResourceVerificationTokenId.NotFound",
                        f"The ID '{token_id}' does not exist",
                    )

        resources = self._list_verification_tokens()
        if token_ids:
            resources = [resource for resource in resources if resource.token_id in token_ids]

        filters = params.get("Filter.N", []) or []
        if filters:
            resources = apply_filters(resources, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start = 0
        if next_token:
            try:
                start = int(next_token)
            except (TypeError, ValueError):
                start = 0

        sliced = resources[start:start + max_results]
        new_next_token = None
        if start + max_results < len(resources):
            new_next_token = str(start + max_results)

        token_set = []
        for resource in sliced:
            token_set.append({
                'ipamArn': resource.ipam_arn,
                'ipamExternalResourceVerificationTokenArn': resource.token_arn,
                'ipamExternalResourceVerificationTokenId': resource.token_id,
                'ipamId': resource.ipam_id,
                'ipamRegion': resource.ipam_region,
                'notAfter': resource.not_after,
                'state': resource.state,
                'status': resource.token_status,
                'tagSet': resource.tag_set,
                'tokenName': resource.token_name,
                'tokenValue': resource.token_value,
            })

        return {
            'ipamExternalResourceVerificationTokenSet': token_set,
            'nextToken': new_next_token,
            }

    def DisassociateIpamByoasn(self, params: Dict[str, Any]):
        """Remove the association between your Autonomous System Number (ASN) and your BYOIP CIDR. You may want to use this action to disassociate an ASN from a CIDR or if you want to swap ASNs. 
            For more information, seeTutorial: Bring your ASN to IPAMin theAmazon VPC IPAM guide."""

        asn = params.get("Asn")
        if not asn:
            return create_error_response("MissingParameter", "Missing required parameter: Asn")
        cidr = params.get("Cidr")
        if not cidr:
            return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        resource = self._find_byoasn(asn)
        if not resource:
            return create_error_response("InvalidAsn.NotFound", f"The ASN '{asn}' does not exist")

        if cidr in resource.cidr_associations:
            resource.cidr_associations.remove(cidr)

        return {
            'asnAssociation': {
                'asn': asn,
                'cidr': cidr,
                'state': "disassociated",
                'statusMessage': resource.status_message,
                },
            }

    def ProvisionIpamByoasn(self, params: Dict[str, Any]):
        """Provisions your Autonomous System Number (ASN) for use in your AWS account. This action requires authorization context for Amazon to bring the ASN to an AWS account. For more information, seeTutorial: Bring your ASN to IPAMin theAmazon VPC IPAM guide."""

        asn = params.get("Asn")
        if not asn:
            return create_error_response("MissingParameter", "Missing required parameter: Asn")
        asn_auth = params.get("AsnAuthorizationContext")
        if not asn_auth:
            return create_error_response("MissingParameter", "Missing required parameter: AsnAuthorizationContext")
        ipam_id = params.get("IpamId")
        if not ipam_id:
            return create_error_response("MissingParameter", "Missing required parameter: IpamId")

        ipam = self.state.ipams.get(ipam_id)
        if not ipam:
            return create_error_response("InvalidIpamId.NotFound", f"IPAM '{ipam_id}' does not exist.")

        resource = self._find_byoasn(asn, ipam_id)
        if not resource:
            resource_id = self._generate_id("ipam")
            resource = BYOASN(
                asn=asn,
                ipam_id=ipam_id,
                state="provisioned",
                status_message="",
                resource_type="byoasn",
                asn_authorization_context=asn_auth,
            )
            self.resources[resource_id] = resource
        else:
            resource.state = "provisioned"
            resource.asn_authorization_context = asn_auth

        return {
            'byoasn': {
                'asn': resource.asn,
                'ipamId': resource.ipam_id,
                'state': resource.state,
                'statusMessage': resource.status_message,
                },
            }

    def _generate_id(self, prefix: str = 'ipam') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class byoasn_RequestParser:
    @staticmethod
    def parse_associate_ipam_byoasn_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Asn": get_scalar(md, "Asn"),
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_create_ipam_external_resource_verification_token_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamId": get_scalar(md, "IpamId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_ipam_external_resource_verification_token_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamExternalResourceVerificationTokenId": get_scalar(md, "IpamExternalResourceVerificationTokenId"),
        }

    @staticmethod
    def parse_deprovision_ipam_byoasn_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Asn": get_scalar(md, "Asn"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamId": get_scalar(md, "IpamId"),
        }

    @staticmethod
    def parse_describe_ipam_byoasn_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_ipam_external_resource_verification_tokens_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamExternalResourceVerificationTokenId.N": get_indexed_list(md, "IpamExternalResourceVerificationTokenId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disassociate_ipam_byoasn_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Asn": get_scalar(md, "Asn"),
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_provision_ipam_byoasn_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Asn": get_scalar(md, "Asn"),
            "AsnAuthorizationContext": get_scalar(md, "AsnAuthorizationContext"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamId": get_scalar(md, "IpamId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateIpamByoasn": byoasn_RequestParser.parse_associate_ipam_byoasn_request,
            "CreateIpamExternalResourceVerificationToken": byoasn_RequestParser.parse_create_ipam_external_resource_verification_token_request,
            "DeleteIpamExternalResourceVerificationToken": byoasn_RequestParser.parse_delete_ipam_external_resource_verification_token_request,
            "DeprovisionIpamByoasn": byoasn_RequestParser.parse_deprovision_ipam_byoasn_request,
            "DescribeIpamByoasn": byoasn_RequestParser.parse_describe_ipam_byoasn_request,
            "DescribeIpamExternalResourceVerificationTokens": byoasn_RequestParser.parse_describe_ipam_external_resource_verification_tokens_request,
            "DisassociateIpamByoasn": byoasn_RequestParser.parse_disassociate_ipam_byoasn_request,
            "ProvisionIpamByoasn": byoasn_RequestParser.parse_provision_ipam_byoasn_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class byoasn_ResponseSerializer:
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
                xml_parts.extend(byoasn_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(byoasn_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(byoasn_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(byoasn_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_ipam_byoasn_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateIpamByoasnResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize asnAssociation
        _asnAssociation_key = None
        if "asnAssociation" in data:
            _asnAssociation_key = "asnAssociation"
        elif "AsnAssociation" in data:
            _asnAssociation_key = "AsnAssociation"
        if _asnAssociation_key:
            param_data = data[_asnAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<asnAssociation>')
            xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</asnAssociation>')
        xml_parts.append(f'</AssociateIpamByoasnResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_ipam_external_resource_verification_token_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateIpamExternalResourceVerificationTokenResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamExternalResourceVerificationToken
        _ipamExternalResourceVerificationToken_key = None
        if "ipamExternalResourceVerificationToken" in data:
            _ipamExternalResourceVerificationToken_key = "ipamExternalResourceVerificationToken"
        elif "IpamExternalResourceVerificationToken" in data:
            _ipamExternalResourceVerificationToken_key = "IpamExternalResourceVerificationToken"
        if _ipamExternalResourceVerificationToken_key:
            param_data = data[_ipamExternalResourceVerificationToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamExternalResourceVerificationToken>')
            xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamExternalResourceVerificationToken>')
        xml_parts.append(f'</CreateIpamExternalResourceVerificationTokenResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_ipam_external_resource_verification_token_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteIpamExternalResourceVerificationTokenResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamExternalResourceVerificationToken
        _ipamExternalResourceVerificationToken_key = None
        if "ipamExternalResourceVerificationToken" in data:
            _ipamExternalResourceVerificationToken_key = "ipamExternalResourceVerificationToken"
        elif "IpamExternalResourceVerificationToken" in data:
            _ipamExternalResourceVerificationToken_key = "IpamExternalResourceVerificationToken"
        if _ipamExternalResourceVerificationToken_key:
            param_data = data[_ipamExternalResourceVerificationToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipamExternalResourceVerificationToken>')
            xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipamExternalResourceVerificationToken>')
        xml_parts.append(f'</DeleteIpamExternalResourceVerificationTokenResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_deprovision_ipam_byoasn_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeprovisionIpamByoasnResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoasn
        _byoasn_key = None
        if "byoasn" in data:
            _byoasn_key = "byoasn"
        elif "Byoasn" in data:
            _byoasn_key = "Byoasn"
        if _byoasn_key:
            param_data = data[_byoasn_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<byoasn>')
            xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</byoasn>')
        xml_parts.append(f'</DeprovisionIpamByoasnResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipam_byoasn_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpamByoasnResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoasnSet
        _byoasnSet_key = None
        if "byoasnSet" in data:
            _byoasnSet_key = "byoasnSet"
        elif "ByoasnSet" in data:
            _byoasnSet_key = "ByoasnSet"
        elif "Byoasns" in data:
            _byoasnSet_key = "Byoasns"
        if _byoasnSet_key:
            param_data = data[_byoasnSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<byoasnSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</byoasnSet>')
            else:
                xml_parts.append(f'{indent_str}<byoasnSet/>')
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
        xml_parts.append(f'</DescribeIpamByoasnResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipam_external_resource_verification_tokens_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpamExternalResourceVerificationTokensResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamExternalResourceVerificationTokenSet
        _ipamExternalResourceVerificationTokenSet_key = None
        if "ipamExternalResourceVerificationTokenSet" in data:
            _ipamExternalResourceVerificationTokenSet_key = "ipamExternalResourceVerificationTokenSet"
        elif "IpamExternalResourceVerificationTokenSet" in data:
            _ipamExternalResourceVerificationTokenSet_key = "IpamExternalResourceVerificationTokenSet"
        elif "IpamExternalResourceVerificationTokens" in data:
            _ipamExternalResourceVerificationTokenSet_key = "IpamExternalResourceVerificationTokens"
        if _ipamExternalResourceVerificationTokenSet_key:
            param_data = data[_ipamExternalResourceVerificationTokenSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamExternalResourceVerificationTokenSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamExternalResourceVerificationTokenSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamExternalResourceVerificationTokenSet/>')
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
        xml_parts.append(f'</DescribeIpamExternalResourceVerificationTokensResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_ipam_byoasn_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateIpamByoasnResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize asnAssociation
        _asnAssociation_key = None
        if "asnAssociation" in data:
            _asnAssociation_key = "asnAssociation"
        elif "AsnAssociation" in data:
            _asnAssociation_key = "AsnAssociation"
        if _asnAssociation_key:
            param_data = data[_asnAssociation_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<asnAssociation>')
            xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</asnAssociation>')
        xml_parts.append(f'</DisassociateIpamByoasnResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_provision_ipam_byoasn_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ProvisionIpamByoasnResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoasn
        _byoasn_key = None
        if "byoasn" in data:
            _byoasn_key = "byoasn"
        elif "Byoasn" in data:
            _byoasn_key = "Byoasn"
        if _byoasn_key:
            param_data = data[_byoasn_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<byoasn>')
            xml_parts.extend(byoasn_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</byoasn>')
        xml_parts.append(f'</ProvisionIpamByoasnResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateIpamByoasn": byoasn_ResponseSerializer.serialize_associate_ipam_byoasn_response,
            "CreateIpamExternalResourceVerificationToken": byoasn_ResponseSerializer.serialize_create_ipam_external_resource_verification_token_response,
            "DeleteIpamExternalResourceVerificationToken": byoasn_ResponseSerializer.serialize_delete_ipam_external_resource_verification_token_response,
            "DeprovisionIpamByoasn": byoasn_ResponseSerializer.serialize_deprovision_ipam_byoasn_response,
            "DescribeIpamByoasn": byoasn_ResponseSerializer.serialize_describe_ipam_byoasn_response,
            "DescribeIpamExternalResourceVerificationTokens": byoasn_ResponseSerializer.serialize_describe_ipam_external_resource_verification_tokens_response,
            "DisassociateIpamByoasn": byoasn_ResponseSerializer.serialize_disassociate_ipam_byoasn_response,
            "ProvisionIpamByoasn": byoasn_ResponseSerializer.serialize_provision_ipam_byoasn_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

