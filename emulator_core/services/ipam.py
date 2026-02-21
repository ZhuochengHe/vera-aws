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
class IPAM:
    default_resource_discovery_association_id: str = ""
    default_resource_discovery_id: str = ""
    description: str = ""
    enable_private_gua: bool = False
    ipam_arn: str = ""
    ipam_id: str = ""
    ipam_region: str = ""
    metered_account: str = ""
    operating_region_set: List[Any] = field(default_factory=list)
    owner_id: str = ""
    private_default_scope_id: str = ""
    public_default_scope_id: str = ""
    resource_discovery_association_count: int = 0
    scope_count: int = 0
    state: str = ""
    state_message: str = ""
    tag_set: List[Any] = field(default_factory=list)
    tier: str = ""

    # Internal dependency tracking — not in API response
    resource_discovery_ids: List[str] = field(default_factory=list)  # tracks ResourceDiscovery children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "defaultResourceDiscoveryAssociationId": self.default_resource_discovery_association_id,
            "defaultResourceDiscoveryId": self.default_resource_discovery_id,
            "description": self.description,
            "enablePrivateGua": self.enable_private_gua,
            "ipamArn": self.ipam_arn,
            "ipamId": self.ipam_id,
            "ipamRegion": self.ipam_region,
            "meteredAccount": self.metered_account,
            "operatingRegionSet": self.operating_region_set,
            "ownerId": self.owner_id,
            "privateDefaultScopeId": self.private_default_scope_id,
            "publicDefaultScopeId": self.public_default_scope_id,
            "resourceDiscoveryAssociationCount": self.resource_discovery_association_count,
            "scopeCount": self.scope_count,
            "state": self.state,
            "stateMessage": self.state_message,
            "tagSet": self.tag_set,
            "tier": self.tier,
        }

class IPAM_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.ipams  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_ipam_or_error(self, ipam_id: str) -> Any:
        ipam = self.resources.get(ipam_id)
        if not ipam:
            return create_error_response("InvalidIpamID.NotFound", f"IPAM '{ipam_id}' does not exist.")
        return ipam


    def CreateIpam(self, params: Dict[str, Any]):
        """Create an IPAM. Amazon VPC IP Address Manager (IPAM) is a VPC feature that you can use
         to automate your IP address management workflows including assigning, tracking,
         troubleshooting, and auditing IP addresses across AWS Regions and accounts
         throughout your AWS Organizatio"""

        enable_private_gua = str2bool(params.get("EnablePrivateGua"))
        ipam_id = self._generate_id("ipam")
        ipam_region = "us-east-1"
        ipam_arn = f"arn:aws:ec2:{ipam_region}::ipam/{ipam_id}"
        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            for tag in spec.get("Tags", []) or []:
                tag_set.append({"Key": tag.get("Key", ""), "Value": tag.get("Value", "")})

        operating_region_set: List[Dict[str, Any]] = []
        for region in params.get("OperatingRegion.N", []) or []:
            if isinstance(region, dict):
                region_name = region.get("RegionName") or region.get("regionName") or region.get("Region")
            else:
                region_name = region
            if region_name:
                operating_region_set.append({"regionName": region_name})
        if not operating_region_set:
            operating_region_set = [{"regionName": ipam_region}]

        private_default_scope_id = self._generate_id("ipam-scope")
        public_default_scope_id = self._generate_id("ipam-scope")

        resource = IPAM(
            description=params.get("Description") or "",
            enable_private_gua=enable_private_gua,
            ipam_arn=ipam_arn,
            ipam_id=ipam_id,
            ipam_region=ipam_region,
            metered_account=params.get("MeteredAccount") or "",
            operating_region_set=operating_region_set,
            owner_id="",
            private_default_scope_id=private_default_scope_id,
            public_default_scope_id=public_default_scope_id,
            resource_discovery_association_count=0,
            scope_count=2,
            state="create-complete",
            state_message="",
            tag_set=tag_set,
            tier=params.get("Tier") or "",
        )
        self.resources[ipam_id] = resource

        return {
            'ipam': resource.to_dict(),
            }

    def DeleteIpam(self, params: Dict[str, Any]):
        """Delete an IPAM. Deleting an IPAM removes all monitored data associated with the IPAM including the historical data for CIDRs. For more information, seeDelete an IPAMin theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["IpamId"])
        if error:
            return error

        ipam_id = params.get("IpamId")
        resource = self._get_ipam_or_error(ipam_id)
        if is_error_response(resource):
            return resource

        if getattr(resource, "resource_discovery_ids", []):
            return create_error_response(
                "DependencyViolation",
                "IPAM has dependent ResourceDiscovery(s) and cannot be deleted.",
            )

        ipam_data = resource.to_dict()
        del self.resources[ipam_id]

        return {
            'ipam': ipam_data,
            }

    def DescribeIpams(self, params: Dict[str, Any]):
        """Get information about your IPAM pools. For more information, seeWhat is IPAM?in theAmazon VPC IPAM User Guide."""

        ipam_ids = params.get("IpamId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if ipam_ids:
            resources: List[IPAM] = []
            for ipam_id in ipam_ids:
                ipam = self.resources.get(ipam_id)
                if not ipam:
                    return create_error_response(
                        "InvalidIpamID.NotFound",
                        f"The ID '{ipam_id}' does not exist",
                    )
                resources.append(ipam)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        ipam_entries = [ipam.to_dict() for ipam in resources[:max_results]]

        return {
            'ipamSet': ipam_entries,
            'nextToken': None,
            }

    def DisableIpamOrganizationAdminAccount(self, params: Dict[str, Any]):
        """Disable the IPAM account. For more information, seeEnable integration with AWS Organizationsin theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["DelegatedAdminAccountId"])
        if error:
            return error

        delegated_admin_account_id = params.get("DelegatedAdminAccountId")
        setattr(self.state, "ipam_org_admin_account_id", None)

        return {
            'success': [delegated_admin_account_id],
            }

    def EnableIpamOrganizationAdminAccount(self, params: Dict[str, Any]):
        """Enable an AWS Organizations member account as the IPAM admin account. You cannot select the AWS Organizations management account as the IPAM admin account. For more information, seeEnable integration with AWS Organizationsin theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["DelegatedAdminAccountId"])
        if error:
            return error

        delegated_admin_account_id = params.get("DelegatedAdminAccountId")
        setattr(self.state, "ipam_org_admin_account_id", delegated_admin_account_id)

        return {
            'success': [delegated_admin_account_id],
            }

    def GetIpamAddressHistory(self, params: Dict[str, Any]):
        """Retrieve historical information about a CIDR within an IPAM scope. For more information, seeView the history of IP addressesin theAmazon VPC IPAM User Guide."""

        error = self._require_params(params, ["Cidr", "IpamScopeId"])
        if error:
            return error

        ipam_scope_id = params.get("IpamScopeId")
        scope = self.state.scopes.get(ipam_scope_id)
        if not scope:
            return create_error_response(
                "InvalidIpamScopeId.NotFound",
                f"The ID '{ipam_scope_id}' does not exist",
            )

        vpc_id = params.get("VpcId")
        if vpc_id:
            vpc = self.state.vpcs.get(vpc_id)
            if not vpc:
                return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        max_results = int(params.get("MaxResults") or 100)
        history_records = getattr(scope, "address_history", [])

        return {
            'historyRecordSet': list(history_records)[:max_results],
            'nextToken': None,
            }

    def ModifyIpam(self, params: Dict[str, Any]):
        """Modify the configurations of an IPAM."""

        error = self._require_params(params, ["IpamId"])
        if error:
            return error

        ipam_id = params.get("IpamId")
        ipam = self._get_ipam_or_error(ipam_id)
        if is_error_response(ipam):
            return ipam

        if params.get("Description") is not None:
            ipam.description = params.get("Description") or ""
        if params.get("EnablePrivateGua") is not None:
            ipam.enable_private_gua = str2bool(params.get("EnablePrivateGua"))
        if params.get("MeteredAccount") is not None:
            ipam.metered_account = params.get("MeteredAccount") or ""
        if params.get("Tier") is not None:
            ipam.tier = params.get("Tier") or ""

        operating_regions = list(ipam.operating_region_set or [])
        if params.get("AddOperatingRegion.N"):
            for region in params.get("AddOperatingRegion.N", []) or []:
                if isinstance(region, dict):
                    region_name = region.get("RegionName") or region.get("regionName") or region.get("Region")
                else:
                    region_name = region
                if region_name and not any(entry.get("regionName") == region_name for entry in operating_regions):
                    operating_regions.append({"regionName": region_name})

        if params.get("RemoveOperatingRegion.N"):
            for region in params.get("RemoveOperatingRegion.N", []) or []:
                if isinstance(region, dict):
                    region_name = region.get("RegionName") or region.get("regionName") or region.get("Region")
                else:
                    region_name = region
                if region_name:
                    operating_regions = [entry for entry in operating_regions if entry.get("regionName") != region_name]

        ipam.operating_region_set = operating_regions

        return {
            'ipam': ipam.to_dict(),
            }

    def MoveByoipCidrToIpam(self, params: Dict[str, Any]):
        """Move a BYOIPv4 CIDR to IPAM from a public IPv4 pool. If you already have a BYOIPv4 CIDR with AWS, you can move the CIDR to IPAM from a public IPv4 pool. You cannot move an IPv6 CIDR to IPAM. If you are bringing a new IP address to AWS for the first time, complete the steps inTutorial: BYOIP address """

        error = self._require_params(params, ["Cidr", "IpamPoolId", "IpamPoolOwner"])
        if error:
            return error

        cidr = params.get("Cidr")
        ipam_pool_id = params.get("IpamPoolId")

        pool = self.state.pools.get(ipam_pool_id)
        if not pool:
            for resource in self.state.byoip.values():
                if getattr(resource, "pool_id", None) == ipam_pool_id:
                    pool = resource
                    break
        if not pool:
            return create_error_response(
                "InvalidIpamPoolId.NotFound",
                f"The ID '{ipam_pool_id}' does not exist",
            )

        byoip_resource = None
        for resource in self.state.byoip.values():
            if getattr(resource, "resource_type", "") != "byoip-cidr":
                continue
            if getattr(resource, "cidr", None) == cidr:
                byoip_resource = resource
                break
        if not byoip_resource:
            return create_error_response(
                "InvalidByoipCidr.NotFound",
                f"The CIDR '{cidr}' does not exist",
            )

        byoip_resource.pool_id = ipam_pool_id
        byoip_resource.status_message = ""

        return {
            'byoipCidr': {
                'advertisementType': byoip_resource.advertisement_type,
                'asnAssociationSet': byoip_resource.asn_association_set,
                'cidr': byoip_resource.cidr,
                'description': byoip_resource.description,
                'networkBorderGroup': byoip_resource.network_border_group,
                'state': byoip_resource.state,
                'statusMessage': byoip_resource.status_message,
                },
            }

    def _generate_id(self, prefix: str = 'ipam') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class ipam_RequestParser:
    @staticmethod
    def parse_create_ipam_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EnablePrivateGua": get_scalar(md, "EnablePrivateGua"),
            "MeteredAccount": get_scalar(md, "MeteredAccount"),
            "OperatingRegion.N": get_indexed_list(md, "OperatingRegion"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Tier": get_scalar(md, "Tier"),
        }

    @staticmethod
    def parse_delete_ipam_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cascade": get_scalar(md, "Cascade"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamId": get_scalar(md, "IpamId"),
        }

    @staticmethod
    def parse_describe_ipams_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IpamId.N": get_indexed_list(md, "IpamId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disable_ipam_organization_admin_account_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DelegatedAdminAccountId": get_scalar(md, "DelegatedAdminAccountId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_enable_ipam_organization_admin_account_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DelegatedAdminAccountId": get_scalar(md, "DelegatedAdminAccountId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_get_ipam_address_history_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndTime": get_scalar(md, "EndTime"),
            "IpamScopeId": get_scalar(md, "IpamScopeId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "StartTime": get_scalar(md, "StartTime"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_modify_ipam_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddOperatingRegion.N": get_indexed_list(md, "AddOperatingRegion"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EnablePrivateGua": get_scalar(md, "EnablePrivateGua"),
            "IpamId": get_scalar(md, "IpamId"),
            "MeteredAccount": get_scalar(md, "MeteredAccount"),
            "RemoveOperatingRegion.N": get_indexed_list(md, "RemoveOperatingRegion"),
            "Tier": get_scalar(md, "Tier"),
        }

    @staticmethod
    def parse_move_byoip_cidr_to_ipam_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "IpamPoolOwner": get_scalar(md, "IpamPoolOwner"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateIpam": ipam_RequestParser.parse_create_ipam_request,
            "DeleteIpam": ipam_RequestParser.parse_delete_ipam_request,
            "DescribeIpams": ipam_RequestParser.parse_describe_ipams_request,
            "DisableIpamOrganizationAdminAccount": ipam_RequestParser.parse_disable_ipam_organization_admin_account_request,
            "EnableIpamOrganizationAdminAccount": ipam_RequestParser.parse_enable_ipam_organization_admin_account_request,
            "GetIpamAddressHistory": ipam_RequestParser.parse_get_ipam_address_history_request,
            "ModifyIpam": ipam_RequestParser.parse_modify_ipam_request,
            "MoveByoipCidrToIpam": ipam_RequestParser.parse_move_byoip_cidr_to_ipam_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class ipam_ResponseSerializer:
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
                xml_parts.extend(ipam_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(ipam_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(ipam_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(ipam_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_ipam_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateIpamResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipam
        _ipam_key = None
        if "ipam" in data:
            _ipam_key = "ipam"
        elif "Ipam" in data:
            _ipam_key = "Ipam"
        if _ipam_key:
            param_data = data[_ipam_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipam>')
            xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipam>')
        xml_parts.append(f'</CreateIpamResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_ipam_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteIpamResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipam
        _ipam_key = None
        if "ipam" in data:
            _ipam_key = "ipam"
        elif "Ipam" in data:
            _ipam_key = "Ipam"
        if _ipam_key:
            param_data = data[_ipam_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipam>')
            xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipam>')
        xml_parts.append(f'</DeleteIpamResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipams_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpamsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipamSet
        _ipamSet_key = None
        if "ipamSet" in data:
            _ipamSet_key = "ipamSet"
        elif "IpamSet" in data:
            _ipamSet_key = "IpamSet"
        elif "Ipams" in data:
            _ipamSet_key = "Ipams"
        if _ipamSet_key:
            param_data = data[_ipamSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipamSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipamSet>')
            else:
                xml_parts.append(f'{indent_str}<ipamSet/>')
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
        xml_parts.append(f'</DescribeIpamsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disable_ipam_organization_admin_account_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableIpamOrganizationAdminAccountResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize success
        _success_key = None
        if "success" in data:
            _success_key = "success"
        elif "Success" in data:
            _success_key = "Success"
        if _success_key:
            param_data = data[_success_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</successSet>')
            else:
                xml_parts.append(f'{indent_str}<successSet/>')
        xml_parts.append(f'</DisableIpamOrganizationAdminAccountResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_ipam_organization_admin_account_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableIpamOrganizationAdminAccountResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize success
        _success_key = None
        if "success" in data:
            _success_key = "success"
        elif "Success" in data:
            _success_key = "Success"
        if _success_key:
            param_data = data[_success_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</successSet>')
            else:
                xml_parts.append(f'{indent_str}<successSet/>')
        xml_parts.append(f'</EnableIpamOrganizationAdminAccountResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_ipam_address_history_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetIpamAddressHistoryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize historyRecordSet
        _historyRecordSet_key = None
        if "historyRecordSet" in data:
            _historyRecordSet_key = "historyRecordSet"
        elif "HistoryRecordSet" in data:
            _historyRecordSet_key = "HistoryRecordSet"
        elif "HistoryRecords" in data:
            _historyRecordSet_key = "HistoryRecords"
        if _historyRecordSet_key:
            param_data = data[_historyRecordSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<historyRecordSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</historyRecordSet>')
            else:
                xml_parts.append(f'{indent_str}<historyRecordSet/>')
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
        xml_parts.append(f'</GetIpamAddressHistoryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_ipam_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyIpamResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipam
        _ipam_key = None
        if "ipam" in data:
            _ipam_key = "ipam"
        elif "Ipam" in data:
            _ipam_key = "Ipam"
        if _ipam_key:
            param_data = data[_ipam_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<ipam>')
            xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</ipam>')
        xml_parts.append(f'</ModifyIpamResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_move_byoip_cidr_to_ipam_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<MoveByoipCidrToIpamResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoipCidr
        _byoipCidr_key = None
        if "byoipCidr" in data:
            _byoipCidr_key = "byoipCidr"
        elif "ByoipCidr" in data:
            _byoipCidr_key = "ByoipCidr"
        if _byoipCidr_key:
            param_data = data[_byoipCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<byoipCidr>')
            xml_parts.extend(ipam_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</byoipCidr>')
        xml_parts.append(f'</MoveByoipCidrToIpamResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateIpam": ipam_ResponseSerializer.serialize_create_ipam_response,
            "DeleteIpam": ipam_ResponseSerializer.serialize_delete_ipam_response,
            "DescribeIpams": ipam_ResponseSerializer.serialize_describe_ipams_response,
            "DisableIpamOrganizationAdminAccount": ipam_ResponseSerializer.serialize_disable_ipam_organization_admin_account_response,
            "EnableIpamOrganizationAdminAccount": ipam_ResponseSerializer.serialize_enable_ipam_organization_admin_account_response,
            "GetIpamAddressHistory": ipam_ResponseSerializer.serialize_get_ipam_address_history_response,
            "ModifyIpam": ipam_ResponseSerializer.serialize_modify_ipam_response,
            "MoveByoipCidrToIpam": ipam_ResponseSerializer.serialize_move_byoip_cidr_to_ipam_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

