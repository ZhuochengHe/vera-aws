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
class BlockPublicAccess:
    creation_timestamp: str = ""
    deletion_timestamp: str = ""
    exclusion_id: str = ""
    internet_gateway_exclusion_mode: str = ""
    last_update_timestamp: str = ""
    reason: str = ""
    resource_arn: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)

    vpc_id: str = ""
    subnet_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTimestamp": self.creation_timestamp,
            "deletionTimestamp": self.deletion_timestamp,
            "exclusionId": self.exclusion_id,
            "internetGatewayExclusionMode": self.internet_gateway_exclusion_mode,
            "lastUpdateTimestamp": self.last_update_timestamp,
            "reason": self.reason,
            "resourceArn": self.resource_arn,
            "state": self.state,
            "tagSet": self.tag_set,
            "vpcId": self.vpc_id,
            "subnetId": self.subnet_id,
        }

class BlockPublicAccess_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.block_public_access  # alias to shared store

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            if not params.get(key):
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _get_exclusion_or_error(self, exclusion_id: str, error_code: str) -> Any:
        resource = self.resources.get(exclusion_id)
        if not resource:
            return create_error_response(error_code, f"The ID '{exclusion_id}' does not exist")
        return resource

    def CreateVpcBlockPublicAccessExclusion(self, params: Dict[str, Any]):
        """Create a VPC Block Public Access (BPA) exclusion. A VPC BPA exclusion is a mode that can be applied to a single VPC or subnet that exempts it from the accountâs BPA mode and will allow bidirectional or egress-only access. You can create BPA exclusions for VPCs and subnets even when BPA is not enab"""

        error = self._require_params(params, ["InternetGatewayExclusionMode"])
        if error:
            return error

        vpc_id = params.get("VpcId")
        subnet_id = params.get("SubnetId")
        if vpc_id and not self.state.vpcs.get(vpc_id):
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")
        if subnet_id and not self.state.subnets.get(subnet_id):
            return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")

        tag_set: List[Dict[str, Any]] = []
        for tag_spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(tag_spec.get("Tags", []) or [])

        exclusion_id = self._generate_id("exclusion")
        timestamp = self._now()
        resource_arn = f"arn:aws:ec2:::vpc-block-public-access-exclusion/{exclusion_id}"
        resource = BlockPublicAccess(
            creation_timestamp=timestamp,
            deletion_timestamp="",
            exclusion_id=exclusion_id,
            internet_gateway_exclusion_mode=params.get("InternetGatewayExclusionMode") or "",
            last_update_timestamp=timestamp,
            reason="",
            resource_arn=resource_arn,
            state=ResourceState.AVAILABLE.value,
            tag_set=tag_set,
            vpc_id=vpc_id or "",
            subnet_id=subnet_id or "",
        )
        self.resources[exclusion_id] = resource

        return {
            'vpcBlockPublicAccessExclusion': resource.to_dict(),
            }

    def DeleteVpcBlockPublicAccessExclusion(self, params: Dict[str, Any]):
        """Delete a VPC Block Public Access (BPA) exclusion. A VPC BPA exclusion is a mode that can be applied to a single VPC or subnet that exempts it from the accountâs BPA mode and will allow bidirectional or egress-only access. You can create BPA exclusions for VPCs and subnets even when BPA is not enab"""

        error = self._require_params(params, ["ExclusionId"])
        if error:
            return error

        exclusion_id = params.get("ExclusionId")
        resource = self._get_exclusion_or_error(
            exclusion_id,
            "InvalidVpcBlockPublicAccessExclusionID.NotFound",
        )
        if is_error_response(resource):
            return resource

        resource.deletion_timestamp = self._now()
        resource.last_update_timestamp = resource.deletion_timestamp
        resource.state = ResourceState.DELETED.value
        self.resources.pop(exclusion_id, None)

        return {
            'vpcBlockPublicAccessExclusion': resource.to_dict(),
            }

    def DescribeVpcBlockPublicAccessExclusions(self, params: Dict[str, Any]):
        """Describe VPC Block Public Access (BPA) exclusions. A VPC BPA exclusion is a mode that can be applied to a single VPC or subnet that exempts it from the accountâs BPA mode and will allow bidirectional or egress-only access. You can create BPA exclusions for VPCs and subnets even when BPA is not ena"""

        exclusion_ids = params.get("ExclusionId.N", []) or []
        if exclusion_ids:
            resources: List[BlockPublicAccess] = []
            for exclusion_id in exclusion_ids:
                resource = self._get_exclusion_or_error(
                    exclusion_id,
                    "InvalidVpcBlockPublicAccessExclusionID.NotFound",
                )
                if is_error_response(resource):
                    return resource
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resource_dicts = [resource.to_dict() for resource in resources]
        filtered = apply_filters(resource_dicts, params.get("Filter.N", []))

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except (TypeError, ValueError):
                start_index = 0

        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None

        return {
            'nextToken': new_next_token,
            'vpcBlockPublicAccessExclusionSet': page,
            }

    def DescribeVpcBlockPublicAccessOptions(self, params: Dict[str, Any]):
        """Describe VPC Block Public Access (BPA) options. VPC Block Public Access (BPA) enables you to block resources in VPCs and subnets that you own in a Region from reaching or being reached from the internet through internet gateways and egress-only internet gateways. To learn more about VPC BPA, seeBloc"""

        if not hasattr(self.state, "block_public_access_options"):
            setattr(self.state, "block_public_access_options", {
                "awsAccountId": "",
                "awsRegion": "",
                "exclusionsAllowed": True,
                "internetGatewayBlockMode": "off",
                "lastUpdateTimestamp": self._now(),
                "managedBy": "",
                "reason": "",
                "state": ResourceState.AVAILABLE.value,
            })

        options = self.state.block_public_access_options
        return {
            'vpcBlockPublicAccessOptions': {
                'awsAccountId': options.get("awsAccountId", ""),
                'awsRegion': options.get("awsRegion", ""),
                'exclusionsAllowed': options.get("exclusionsAllowed"),
                'internetGatewayBlockMode': options.get("internetGatewayBlockMode", ""),
                'lastUpdateTimestamp': options.get("lastUpdateTimestamp", ""),
                'managedBy': options.get("managedBy", ""),
                'reason': options.get("reason", ""),
                'state': options.get("state", ""),
                },
            }

    def ModifyVpcBlockPublicAccessExclusion(self, params: Dict[str, Any]):
        """Modify VPC Block Public Access (BPA) exclusions. A VPC BPA exclusion is a mode that can be applied to a single VPC or subnet that exempts it from the accountâs BPA mode and will allow bidirectional or egress-only access. You can create BPA exclusions for VPCs and subnets even when BPA is not enabl"""

        error = self._require_params(params, ["ExclusionId", "InternetGatewayExclusionMode"])
        if error:
            return error

        exclusion_id = params.get("ExclusionId")
        resource = self._get_exclusion_or_error(
            exclusion_id,
            "InvalidVpcBlockPublicAccessExclusionID.NotFound",
        )
        if is_error_response(resource):
            return resource

        resource.internet_gateway_exclusion_mode = params.get("InternetGatewayExclusionMode") or ""
        resource.last_update_timestamp = self._now()

        return {
            'vpcBlockPublicAccessExclusion': resource.to_dict(),
            }

    def ModifyVpcBlockPublicAccessOptions(self, params: Dict[str, Any]):
        """Modify VPC Block Public Access (BPA) options. VPC Block Public Access (BPA) enables you to block resources in VPCs and subnets that you own in a Region from reaching or being reached from the internet through internet gateways and egress-only internet gateways. To learn more about VPC BPA, seeBlock """

        error = self._require_params(params, ["InternetGatewayBlockMode"])
        if error:
            return error

        if not hasattr(self.state, "block_public_access_options"):
            setattr(self.state, "block_public_access_options", {
                "awsAccountId": "",
                "awsRegion": "",
                "exclusionsAllowed": True,
                "internetGatewayBlockMode": "off",
                "lastUpdateTimestamp": self._now(),
                "managedBy": "",
                "reason": "",
                "state": ResourceState.AVAILABLE.value,
            })

        options = self.state.block_public_access_options
        options["internetGatewayBlockMode"] = params.get("InternetGatewayBlockMode") or ""
        options["lastUpdateTimestamp"] = self._now()

        return {
            'vpcBlockPublicAccessOptions': {
                'awsAccountId': options.get("awsAccountId", ""),
                'awsRegion': options.get("awsRegion", ""),
                'exclusionsAllowed': options.get("exclusionsAllowed"),
                'internetGatewayBlockMode': options.get("internetGatewayBlockMode", ""),
                'lastUpdateTimestamp': options.get("lastUpdateTimestamp", ""),
                'managedBy': options.get("managedBy", ""),
                'reason': options.get("reason", ""),
                'state': options.get("state", ""),
                },
            }

    def _generate_id(self, prefix: str = 'exclusion') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class blockpublicaccess_RequestParser:
    @staticmethod
    def parse_create_vpc_block_public_access_exclusion_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InternetGatewayExclusionMode": get_scalar(md, "InternetGatewayExclusionMode"),
            "SubnetId": get_scalar(md, "SubnetId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_delete_vpc_block_public_access_exclusion_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExclusionId": get_scalar(md, "ExclusionId"),
        }

    @staticmethod
    def parse_describe_vpc_block_public_access_exclusions_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExclusionId.N": get_indexed_list(md, "ExclusionId"),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_vpc_block_public_access_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_modify_vpc_block_public_access_exclusion_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExclusionId": get_scalar(md, "ExclusionId"),
            "InternetGatewayExclusionMode": get_scalar(md, "InternetGatewayExclusionMode"),
        }

    @staticmethod
    def parse_modify_vpc_block_public_access_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InternetGatewayBlockMode": get_scalar(md, "InternetGatewayBlockMode"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateVpcBlockPublicAccessExclusion": blockpublicaccess_RequestParser.parse_create_vpc_block_public_access_exclusion_request,
            "DeleteVpcBlockPublicAccessExclusion": blockpublicaccess_RequestParser.parse_delete_vpc_block_public_access_exclusion_request,
            "DescribeVpcBlockPublicAccessExclusions": blockpublicaccess_RequestParser.parse_describe_vpc_block_public_access_exclusions_request,
            "DescribeVpcBlockPublicAccessOptions": blockpublicaccess_RequestParser.parse_describe_vpc_block_public_access_options_request,
            "ModifyVpcBlockPublicAccessExclusion": blockpublicaccess_RequestParser.parse_modify_vpc_block_public_access_exclusion_request,
            "ModifyVpcBlockPublicAccessOptions": blockpublicaccess_RequestParser.parse_modify_vpc_block_public_access_options_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class blockpublicaccess_ResponseSerializer:
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
                xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_vpc_block_public_access_exclusion_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpcBlockPublicAccessExclusionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpcBlockPublicAccessExclusion
        _vpcBlockPublicAccessExclusion_key = None
        if "vpcBlockPublicAccessExclusion" in data:
            _vpcBlockPublicAccessExclusion_key = "vpcBlockPublicAccessExclusion"
        elif "VpcBlockPublicAccessExclusion" in data:
            _vpcBlockPublicAccessExclusion_key = "VpcBlockPublicAccessExclusion"
        if _vpcBlockPublicAccessExclusion_key:
            param_data = data[_vpcBlockPublicAccessExclusion_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpcBlockPublicAccessExclusion>')
            xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpcBlockPublicAccessExclusion>')
        xml_parts.append(f'</CreateVpcBlockPublicAccessExclusionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpc_block_public_access_exclusion_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpcBlockPublicAccessExclusionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpcBlockPublicAccessExclusion
        _vpcBlockPublicAccessExclusion_key = None
        if "vpcBlockPublicAccessExclusion" in data:
            _vpcBlockPublicAccessExclusion_key = "vpcBlockPublicAccessExclusion"
        elif "VpcBlockPublicAccessExclusion" in data:
            _vpcBlockPublicAccessExclusion_key = "VpcBlockPublicAccessExclusion"
        if _vpcBlockPublicAccessExclusion_key:
            param_data = data[_vpcBlockPublicAccessExclusion_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpcBlockPublicAccessExclusion>')
            xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpcBlockPublicAccessExclusion>')
        xml_parts.append(f'</DeleteVpcBlockPublicAccessExclusionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_block_public_access_exclusions_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcBlockPublicAccessExclusionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize vpcBlockPublicAccessExclusionSet
        _vpcBlockPublicAccessExclusionSet_key = None
        if "vpcBlockPublicAccessExclusionSet" in data:
            _vpcBlockPublicAccessExclusionSet_key = "vpcBlockPublicAccessExclusionSet"
        elif "VpcBlockPublicAccessExclusionSet" in data:
            _vpcBlockPublicAccessExclusionSet_key = "VpcBlockPublicAccessExclusionSet"
        elif "VpcBlockPublicAccessExclusions" in data:
            _vpcBlockPublicAccessExclusionSet_key = "VpcBlockPublicAccessExclusions"
        if _vpcBlockPublicAccessExclusionSet_key:
            param_data = data[_vpcBlockPublicAccessExclusionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpcBlockPublicAccessExclusionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpcBlockPublicAccessExclusionSet>')
            else:
                xml_parts.append(f'{indent_str}<vpcBlockPublicAccessExclusionSet/>')
        xml_parts.append(f'</DescribeVpcBlockPublicAccessExclusionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_block_public_access_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcBlockPublicAccessOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpcBlockPublicAccessOptions
        _vpcBlockPublicAccessOptions_key = None
        if "vpcBlockPublicAccessOptions" in data:
            _vpcBlockPublicAccessOptions_key = "vpcBlockPublicAccessOptions"
        elif "VpcBlockPublicAccessOptions" in data:
            _vpcBlockPublicAccessOptions_key = "VpcBlockPublicAccessOptions"
        if _vpcBlockPublicAccessOptions_key:
            param_data = data[_vpcBlockPublicAccessOptions_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpcBlockPublicAccessOptionsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpcBlockPublicAccessOptionsSet>')
            else:
                xml_parts.append(f'{indent_str}<vpcBlockPublicAccessOptionsSet/>')
        xml_parts.append(f'</DescribeVpcBlockPublicAccessOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpc_block_public_access_exclusion_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpcBlockPublicAccessExclusionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpcBlockPublicAccessExclusion
        _vpcBlockPublicAccessExclusion_key = None
        if "vpcBlockPublicAccessExclusion" in data:
            _vpcBlockPublicAccessExclusion_key = "vpcBlockPublicAccessExclusion"
        elif "VpcBlockPublicAccessExclusion" in data:
            _vpcBlockPublicAccessExclusion_key = "VpcBlockPublicAccessExclusion"
        if _vpcBlockPublicAccessExclusion_key:
            param_data = data[_vpcBlockPublicAccessExclusion_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpcBlockPublicAccessExclusion>')
            xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpcBlockPublicAccessExclusion>')
        xml_parts.append(f'</ModifyVpcBlockPublicAccessExclusionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpc_block_public_access_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpcBlockPublicAccessOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpcBlockPublicAccessOptions
        _vpcBlockPublicAccessOptions_key = None
        if "vpcBlockPublicAccessOptions" in data:
            _vpcBlockPublicAccessOptions_key = "vpcBlockPublicAccessOptions"
        elif "VpcBlockPublicAccessOptions" in data:
            _vpcBlockPublicAccessOptions_key = "VpcBlockPublicAccessOptions"
        if _vpcBlockPublicAccessOptions_key:
            param_data = data[_vpcBlockPublicAccessOptions_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpcBlockPublicAccessOptionsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(blockpublicaccess_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpcBlockPublicAccessOptionsSet>')
            else:
                xml_parts.append(f'{indent_str}<vpcBlockPublicAccessOptionsSet/>')
        xml_parts.append(f'</ModifyVpcBlockPublicAccessOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateVpcBlockPublicAccessExclusion": blockpublicaccess_ResponseSerializer.serialize_create_vpc_block_public_access_exclusion_response,
            "DeleteVpcBlockPublicAccessExclusion": blockpublicaccess_ResponseSerializer.serialize_delete_vpc_block_public_access_exclusion_response,
            "DescribeVpcBlockPublicAccessExclusions": blockpublicaccess_ResponseSerializer.serialize_describe_vpc_block_public_access_exclusions_response,
            "DescribeVpcBlockPublicAccessOptions": blockpublicaccess_ResponseSerializer.serialize_describe_vpc_block_public_access_options_response,
            "ModifyVpcBlockPublicAccessExclusion": blockpublicaccess_ResponseSerializer.serialize_modify_vpc_block_public_access_exclusion_response,
            "ModifyVpcBlockPublicAccessOptions": blockpublicaccess_ResponseSerializer.serialize_modify_vpc_block_public_access_options_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

