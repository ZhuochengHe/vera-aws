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
class Ec2InstanceConnectEndpoint:
    availability_zone: str = ""
    availability_zone_id: str = ""
    created_at: str = ""
    dns_name: str = ""
    fips_dns_name: str = ""
    instance_connect_endpoint_arn: str = ""
    instance_connect_endpoint_id: str = ""
    ip_address_type: str = ""
    network_interface_id_set: List[Any] = field(default_factory=list)
    owner_id: str = ""
    preserve_client_ip: bool = False
    public_dns_names: Dict[str, Any] = field(default_factory=dict)
    security_group_id_set: List[Any] = field(default_factory=list)
    state: str = ""
    state_message: str = ""
    subnet_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    vpc_id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "createdAt": self.created_at,
            "dnsName": self.dns_name,
            "fipsDnsName": self.fips_dns_name,
            "instanceConnectEndpointArn": self.instance_connect_endpoint_arn,
            "instanceConnectEndpointId": self.instance_connect_endpoint_id,
            "ipAddressType": self.ip_address_type,
            "networkInterfaceIdSet": self.network_interface_id_set,
            "ownerId": self.owner_id,
            "preserveClientIp": self.preserve_client_ip,
            "publicDnsNames": self.public_dns_names,
            "securityGroupIdSet": self.security_group_id_set,
            "state": self.state,
            "stateMessage": self.state_message,
            "subnetId": self.subnet_id,
            "tagSet": self.tag_set,
            "vpcId": self.vpc_id,
        }

class Ec2InstanceConnectEndpoint_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.ec2_instance_connect_endpoints  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.subnets.get(params['subnet_id']).ec2_instance_connect_endpoint_ids.append(new_id)
    #   Delete: self.state.subnets.get(resource.subnet_id).ec2_instance_connect_endpoint_ids.remove(resource_id)
    #   Create: self.state.vpcs.get(params['vpc_id']).ec2_instance_connect_endpoint_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).ec2_instance_connect_endpoint_ids.remove(resource_id)

    def _get_resource_or_error(self, endpoint_id: str, error_code: str, message: str) -> Any:
        resource = self.resources.get(endpoint_id)
        if not resource:
            return create_error_response(error_code, message)
        return resource

    def _register_with_parents(self, endpoint_id: str, subnet_id: str, vpc_id: str) -> None:
        subnet = self.state.subnets.get(subnet_id)
        if subnet and hasattr(subnet, 'ec2_instance_connect_endpoint_ids'):
            subnet.ec2_instance_connect_endpoint_ids.append(endpoint_id)
        vpc = self.state.vpcs.get(vpc_id)
        if vpc and hasattr(vpc, 'ec2_instance_connect_endpoint_ids'):
            vpc.ec2_instance_connect_endpoint_ids.append(endpoint_id)

    def _deregister_from_parents(self, endpoint_id: str, subnet_id: str, vpc_id: str) -> None:
        subnet = self.state.subnets.get(subnet_id)
        if subnet and hasattr(subnet, 'ec2_instance_connect_endpoint_ids') and endpoint_id in subnet.ec2_instance_connect_endpoint_ids:
            subnet.ec2_instance_connect_endpoint_ids.remove(endpoint_id)
        vpc = self.state.vpcs.get(vpc_id)
        if vpc and hasattr(vpc, 'ec2_instance_connect_endpoint_ids') and endpoint_id in vpc.ec2_instance_connect_endpoint_ids:
            vpc.ec2_instance_connect_endpoint_ids.remove(endpoint_id)

    def CreateInstanceConnectEndpoint(self, params: Dict[str, Any]):
        """Creates an EC2 Instance Connect Endpoint. An EC2 Instance Connect Endpoint allows you to connect to an instance, without
            requiring the instance to have a public IPv4 or public IPv6 address. For more
            information, seeConnect to your instances using EC2 Instance Connect Endpoint"""

        if not params.get("SubnetId"):
            return create_error_response("MissingParameter", "Missing required parameter: SubnetId")

        subnet_id = params.get("SubnetId")
        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            return create_error_response(
                "InvalidSubnetID.NotFound",
                f"Subnet '{subnet_id}' does not exist.",
            )

        vpc_id = getattr(subnet, "vpc_id", "") or ""
        if vpc_id and not self.state.vpcs.get(vpc_id):
            return create_error_response(
                "InvalidVpcID.NotFound",
                f"VPC '{vpc_id}' does not exist.",
            )

        security_group_ids = params.get("SecurityGroupId.N", []) or []
        for security_group_id in security_group_ids:
            if not self.state.security_groups.get(security_group_id):
                return create_error_response(
                    "InvalidGroup.NotFound",
                    f"Security group '{security_group_id}' does not exist.",
                )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        endpoint_id = self._generate_id("eice")
        created_at = datetime.now(timezone.utc).isoformat()
        dns_name = f"{endpoint_id}.ec2-instance-connect.amazonaws.com"
        fips_dns_name = f"fips.{dns_name}"
        public_dns_names = {
            "dualstack": {"dnsName": dns_name, "fipsDnsName": fips_dns_name},
            "ipv4": {"dnsName": dns_name, "fipsDnsName": fips_dns_name},
        }

        resource = Ec2InstanceConnectEndpoint(
            availability_zone=getattr(subnet, "availability_zone", "") or "",
            availability_zone_id=getattr(subnet, "availability_zone_id", "") or "",
            created_at=created_at,
            dns_name=dns_name,
            fips_dns_name=fips_dns_name,
            instance_connect_endpoint_arn=(
                f"arn:aws:ec2:::instance-connect-endpoint/{endpoint_id}"
            ),
            instance_connect_endpoint_id=endpoint_id,
            ip_address_type=params.get("IpAddressType") or "ipv4",
            network_interface_id_set=[],
            owner_id="",
            preserve_client_ip=str2bool(params.get("PreserveClientIp")),
            public_dns_names=public_dns_names,
            security_group_id_set=security_group_ids,
            state="available",
            state_message="Available",
            subnet_id=subnet_id,
            tag_set=tag_set,
            vpc_id=vpc_id,
        )
        self.resources[endpoint_id] = resource
        self._register_with_parents(endpoint_id, subnet_id, vpc_id)

        return {
            'clientToken': params.get("ClientToken"),
            'instanceConnectEndpoint': resource.to_dict(),
            }

    def DeleteInstanceConnectEndpoint(self, params: Dict[str, Any]):
        """Deletes the specified EC2 Instance Connect Endpoint."""

        if not params.get("InstanceConnectEndpointId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: InstanceConnectEndpointId",
            )

        endpoint_id = params.get("InstanceConnectEndpointId")
        resource = self.resources.get(endpoint_id)
        if not resource:
            return create_error_response(
                "InvalidInstanceConnectEndpointId.NotFound",
                f"The ID '{endpoint_id}' does not exist",
            )

        self._deregister_from_parents(endpoint_id, resource.subnet_id, resource.vpc_id)
        del self.resources[endpoint_id]

        return {
            'instanceConnectEndpoint': resource.to_dict(),
            }

    def DescribeInstanceConnectEndpoints(self, params: Dict[str, Any]):
        """Describes the specified EC2 Instance Connect Endpoints or all EC2 Instance Connect Endpoints."""

        instance_connect_endpoint_ids = params.get("InstanceConnectEndpointId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if instance_connect_endpoint_ids:
            resources: List[Ec2InstanceConnectEndpoint] = []
            for endpoint_id in instance_connect_endpoint_ids:
                resource = self.resources.get(endpoint_id)
                if not resource:
                    return create_error_response(
                        "InvalidInstanceConnectEndpointId.NotFound",
                        f"The ID '{endpoint_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        endpoint_set = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'instanceConnectEndpointSet': endpoint_set,
            'nextToken': None,
            }

    def ModifyInstanceConnectEndpoint(self, params: Dict[str, Any]):
        """Modifies the specified EC2 Instance Connect Endpoint. For more information, seeModify an
                EC2 Instance Connect Endpointin theAmazon EC2 User Guide."""

        if not params.get("InstanceConnectEndpointId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: InstanceConnectEndpointId",
            )

        endpoint_id = params.get("InstanceConnectEndpointId")
        resource = self.resources.get(endpoint_id)
        if not resource:
            return create_error_response(
                "InvalidInstanceConnectEndpointId.NotFound",
                f"The ID '{endpoint_id}' does not exist",
            )

        security_group_ids = params.get("SecurityGroupId.N", []) or []
        for security_group_id in security_group_ids:
            if not self.state.security_groups.get(security_group_id):
                return create_error_response(
                    "InvalidGroup.NotFound",
                    f"Security group '{security_group_id}' does not exist.",
                )

        if params.get("IpAddressType"):
            resource.ip_address_type = params.get("IpAddressType") or resource.ip_address_type
        if params.get("PreserveClientIp") is not None:
            resource.preserve_client_ip = str2bool(params.get("PreserveClientIp"))
        if security_group_ids:
            resource.security_group_id_set = security_group_ids

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'availability') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class ec2instanceconnectendpoint_RequestParser:
    @staticmethod
    def parse_create_instance_connect_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpAddressType": get_scalar(md, "IpAddressType"),
            "PreserveClientIp": get_scalar(md, "PreserveClientIp"),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
            "SubnetId": get_scalar(md, "SubnetId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_instance_connect_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceConnectEndpointId": get_scalar(md, "InstanceConnectEndpointId"),
        }

    @staticmethod
    def parse_describe_instance_connect_endpoints_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "InstanceConnectEndpointId.N": get_indexed_list(md, "InstanceConnectEndpointId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_modify_instance_connect_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceConnectEndpointId": get_scalar(md, "InstanceConnectEndpointId"),
            "IpAddressType": get_scalar(md, "IpAddressType"),
            "PreserveClientIp": get_scalar(md, "PreserveClientIp"),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateInstanceConnectEndpoint": ec2instanceconnectendpoint_RequestParser.parse_create_instance_connect_endpoint_request,
            "DeleteInstanceConnectEndpoint": ec2instanceconnectendpoint_RequestParser.parse_delete_instance_connect_endpoint_request,
            "DescribeInstanceConnectEndpoints": ec2instanceconnectendpoint_RequestParser.parse_describe_instance_connect_endpoints_request,
            "ModifyInstanceConnectEndpoint": ec2instanceconnectendpoint_RequestParser.parse_modify_instance_connect_endpoint_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class ec2instanceconnectendpoint_ResponseSerializer:
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
                xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_instance_connect_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateInstanceConnectEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize instanceConnectEndpoint
        _instanceConnectEndpoint_key = None
        if "instanceConnectEndpoint" in data:
            _instanceConnectEndpoint_key = "instanceConnectEndpoint"
        elif "InstanceConnectEndpoint" in data:
            _instanceConnectEndpoint_key = "InstanceConnectEndpoint"
        if _instanceConnectEndpoint_key:
            param_data = data[_instanceConnectEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceConnectEndpoint>')
            xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceConnectEndpoint>')
        xml_parts.append(f'</CreateInstanceConnectEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_instance_connect_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteInstanceConnectEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceConnectEndpoint
        _instanceConnectEndpoint_key = None
        if "instanceConnectEndpoint" in data:
            _instanceConnectEndpoint_key = "instanceConnectEndpoint"
        elif "InstanceConnectEndpoint" in data:
            _instanceConnectEndpoint_key = "InstanceConnectEndpoint"
        if _instanceConnectEndpoint_key:
            param_data = data[_instanceConnectEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<instanceConnectEndpoint>')
            xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</instanceConnectEndpoint>')
        xml_parts.append(f'</DeleteInstanceConnectEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_connect_endpoints_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceConnectEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceConnectEndpointSet
        _instanceConnectEndpointSet_key = None
        if "instanceConnectEndpointSet" in data:
            _instanceConnectEndpointSet_key = "instanceConnectEndpointSet"
        elif "InstanceConnectEndpointSet" in data:
            _instanceConnectEndpointSet_key = "InstanceConnectEndpointSet"
        elif "InstanceConnectEndpoints" in data:
            _instanceConnectEndpointSet_key = "InstanceConnectEndpoints"
        if _instanceConnectEndpointSet_key:
            param_data = data[_instanceConnectEndpointSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceConnectEndpointSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2instanceconnectendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceConnectEndpointSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceConnectEndpointSet/>')
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
        xml_parts.append(f'</DescribeInstanceConnectEndpointsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_instance_connect_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyInstanceConnectEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyInstanceConnectEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateInstanceConnectEndpoint": ec2instanceconnectendpoint_ResponseSerializer.serialize_create_instance_connect_endpoint_response,
            "DeleteInstanceConnectEndpoint": ec2instanceconnectendpoint_ResponseSerializer.serialize_delete_instance_connect_endpoint_response,
            "DescribeInstanceConnectEndpoints": ec2instanceconnectendpoint_ResponseSerializer.serialize_describe_instance_connect_endpoints_response,
            "ModifyInstanceConnectEndpoint": ec2instanceconnectendpoint_ResponseSerializer.serialize_modify_instance_connect_endpoint_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

