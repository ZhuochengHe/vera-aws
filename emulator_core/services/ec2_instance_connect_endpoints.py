from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class InstanceConnectEndpointState(Enum):
    CREATE_IN_PROGRESS = "create-in-progress"
    CREATE_COMPLETE = "create-complete"
    CREATE_FAILED = "create-failed"
    DELETE_IN_PROGRESS = "delete-in-progress"
    DELETE_COMPLETE = "delete-complete"
    DELETE_FAILED = "delete-failed"
    UPDATE_IN_PROGRESS = "update-in-progress"
    UPDATE_COMPLETE = "update-complete"
    UPDATE_FAILED = "update-failed"


class IpAddressType(Enum):
    IPV4 = "ipv4"
    DUALSTACK = "dualstack"
    IPV6 = "ipv6"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class InstanceConnectEndpointDnsNames:
    dnsName: Optional[str] = None
    fipsDnsName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.dnsName is not None:
            d["dnsName"] = self.dnsName
        if self.fipsDnsName is not None:
            d["fipsDnsName"] = self.fipsDnsName
        return d


@dataclass
class InstanceConnectEndpointPublicDnsNames:
    dualstack: Optional[InstanceConnectEndpointDnsNames] = None
    ipv4: Optional[InstanceConnectEndpointDnsNames] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.dualstack is not None:
            d["dualstack"] = self.dualstack.to_dict()
        if self.ipv4 is not None:
            d["ipv4"] = self.ipv4.to_dict()
        return d


@dataclass
class Ec2InstanceConnectEndpoint:
    instanceConnectEndpointId: str
    subnetId: str
    vpcId: str
    ownerId: str
    state: InstanceConnectEndpointState
    stateMessage: Optional[str] = None
    createdAt: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ipAddressType: Optional[IpAddressType] = None
    preserveClientIp: bool = False
    securityGroupIdSet: List[str] = field(default_factory=list)
    networkInterfaceIdSet: List[str] = field(default_factory=list)
    availabilityZone: Optional[str] = None
    availabilityZoneId: Optional[str] = None
    dnsName: Optional[str] = None
    fipsDnsName: Optional[str] = None
    instanceConnectEndpointArn: Optional[str] = None
    publicDnsNames: Optional[InstanceConnectEndpointPublicDnsNames] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "availabilityZone": self.availabilityZone,
            "availabilityZoneId": self.availabilityZoneId,
            "createdAt": self.createdAt.isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
            "dnsName": self.dnsName,
            "fipsDnsName": self.fipsDnsName,
            "instanceConnectEndpointArn": self.instanceConnectEndpointArn,
            "instanceConnectEndpointId": self.instanceConnectEndpointId,
            "ipAddressType": self.ipAddressType.value if self.ipAddressType else None,
            "networkInterfaceIdSet": self.networkInterfaceIdSet,
            "ownerId": self.ownerId,
            "preserveClientIp": self.preserveClientIp,
            "publicDnsNames": self.publicDnsNames.to_dict() if self.publicDnsNames else None,
            "securityGroupIdSet": self.securityGroupIdSet,
            "state": self.state.value,
            "stateMessage": self.stateMessage or "",
            "subnetId": self.subnetId,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "vpcId": self.vpcId,
        }
        # Remove keys with None values to match AWS behavior
        return {k: v for k, v in d.items() if v is not None}


class Ec2InstanceConnectEndpointsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.ec2_instance_connect_endpoints dict for storage

    def _validate_ip_address_type(self, ip_type: Optional[str]) -> Optional[IpAddressType]:
        if ip_type is None:
            return None
        try:
            return IpAddressType(ip_type)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid IpAddressType: {ip_type}")

    def _validate_security_group_ids(self, sg_ids: Optional[List[str]], vpc_id: str) -> List[str]:
        if sg_ids is None:
            # If not specified, use default security group for the VPC
            # Find default security group for the VPC
            default_sg_id = None
            for sg in self.state.security_groups.values():
                if sg.vpc_id == vpc_id and sg.group_name == "default":
                    default_sg_id = sg.group_id
                    break
            if default_sg_id is None:
                # No default security group found, raise error
                raise ErrorCode("InvalidParameterValue", f"No default security group found for VPC {vpc_id}")
            return [default_sg_id]
        if not isinstance(sg_ids, list):
            raise ErrorCode("InvalidParameterValue", "SecurityGroupId.N must be a list of strings")
        if len(sg_ids) > 16:
            raise ErrorCode("InvalidParameterValue", "Maximum number of security groups is 16")
        # Validate each security group exists and belongs to the same VPC
        for sg_id in sg_ids:
            sg = self.state.get_resource(sg_id)
            if sg is None or sg.resource_type != "security-group":
                raise ErrorCode("InvalidGroup.NotFound", f"Security group {sg_id} does not exist")
            if sg.vpc_id != vpc_id:
                raise ErrorCode("InvalidParameterValue", f"Security group {sg_id} does not belong to VPC {vpc_id}")
        return sg_ids

    def _validate_tags(self, tag_specifications: Optional[List[Dict[str, Any]]]) -> List[Tag]:
        tags: List[Tag] = []
        if not tag_specifications:
            return tags
        for tag_spec in tag_specifications:
            resource_type = tag_spec.get("ResourceType")
            # According to AWS docs, ResourceType must be "instance-connect-endpoint" for these tags
            # But AWS allows other resource types, we only accept "instance-connect-endpoint" or None
            if resource_type and resource_type != "instance-connect-endpoint":
                raise ErrorCode("InvalidParameterValue", f"Invalid ResourceType in TagSpecification: {resource_type}")
            tag_list = tag_spec.get("Tags", [])
            if not isinstance(tag_list, list):
                raise ErrorCode("InvalidParameterValue", "Tags must be a list")
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None or not isinstance(key, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Key must be a string")
                if key.lower().startswith("aws:"):
                    raise ErrorCode("InvalidParameterValue", "Tag keys may not begin with 'aws:'")
                if len(key) > 127:
                    raise ErrorCode("InvalidParameterValue", "Tag Key length must be <= 127")
                if value is not None and not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Value must be a string")
                if value is not None and len(value) > 256:
                    raise ErrorCode("InvalidParameterValue", "Tag Value length must be <= 256")
                tags.append(Tag(Key=key, Value=value or ""))
        return tags

    def _generate_arn(self, endpoint_id: str) -> str:
        region = self.state.region or "region"
        account_id = self.get_owner_id()
        return f"arn:aws:ec2:{region}:{account_id}:instance-connect-endpoint/{endpoint_id}"

    def _get_vpc_id_from_subnet(self, subnet_id: str) -> str:
        subnet = self.state.get_resource(subnet_id)
        if subnet is None or subnet.resource_type != "subnet":
            raise ErrorCode("InvalidSubnetID.NotFound", f"Subnet {subnet_id} does not exist")
        return subnet.vpc_id

    def _get_availability_zone_from_subnet(self, subnet_id: str) -> (str, str):
        subnet = self.state.get_resource(subnet_id)
        if subnet is None or subnet.resource_type != "subnet":
            raise ErrorCode("InvalidSubnetID.NotFound", f"Subnet {subnet_id} does not exist")
        # availability_zone and availability_zone_id may be attributes of subnet
        az = getattr(subnet, "availability_zone", None)
        az_id = getattr(subnet, "availability_zone_id", None)
        return az, az_id

    def _validate_preserve_client_ip(self, preserve_client_ip: Optional[bool], ip_address_type: Optional[IpAddressType]) -> bool:
        if preserve_client_ip is None:
            return False
        if preserve_client_ip:
            # PreserveClientIp is only supported on IPv4 endpoints
            if ip_address_type != IpAddressType.IPV4:
                raise ErrorCode("InvalidParameterCombination", "PreserveClientIp is only supported on IPv4 EC2 Instance Connect Endpoints")
        return preserve_client_ip

    def create_instance_connect_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter SubnetId
        subnet_id = params.get("SubnetId")
        if not subnet_id or not isinstance(subnet_id, str):
            raise ErrorCode("MissingParameter", "SubnetId is required and must be a string")

        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Validate ClientToken if present
        client_token = params.get("ClientToken")
        if client_token is not None and not isinstance(client_token, str):
            raise ErrorCode("InvalidParameterValue", "ClientToken must be a string")

        # Validate IpAddressType
        ip_address_type_str = params.get("IpAddressType")
        ip_address_type = self._validate_ip_address_type(ip_address_type_str)

        # Validate PreserveClientIp
        preserve_client_ip = params.get("PreserveClientIp")
        if preserve_client_ip is not None and not isinstance(preserve_client_ip, bool):
            raise ErrorCode("InvalidParameterValue", "PreserveClientIp must be a boolean")
        preserve_client_ip = self._validate_preserve_client_ip(preserve_client_ip, ip_address_type)

        # Validate SecurityGroupId.N (list of strings)
        # AWS param name is SecurityGroupId.N, but in params dict it will be "SecurityGroupId.N" or "SecurityGroupId"
        # We accept "SecurityGroupId.N" as list of strings or "SecurityGroupId" as list of strings
        sg_ids = None
        # Try to find keys starting with "SecurityGroupId."
        sg_ids = []
        for key, value in params.items():
            if key.startswith("SecurityGroupId."):
                if not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                sg_ids.append(value)
        if not sg_ids:
            # Also check if "SecurityGroupId.N" is a list directly
            sg_ids_alt = params.get("SecurityGroupId.N")
            if sg_ids_alt is not None:
                if not isinstance(sg_ids_alt, list):
                    raise ErrorCode("InvalidParameterValue", "SecurityGroupId.N must be a list of strings")
                sg_ids = sg_ids_alt
        if not sg_ids:
            sg_ids = None  # means not specified

        # Validate tags
        tag_specifications = []
        # TagSpecification.N is a list of dicts
        # We expect param keys like "TagSpecification.N" or "TagSpecification"
        # Accept "TagSpecification.N" or "TagSpecification" as list of dicts
        for key, value in params.items():
            if key.startswith("TagSpecification."):
                if not isinstance(value, dict):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a dict")
                tag_specifications.append(value)
        if not tag_specifications:
            tag_specifications_alt = params.get("TagSpecification.N") or params.get("TagSpecification")
            if tag_specifications_alt is not None:
                if not isinstance(tag_specifications_alt, list):
                    raise ErrorCode("InvalidParameterValue", "TagSpecification.N must be a list of dicts")
                tag_specifications = tag_specifications_alt

        tags = self._validate_tags(tag_specifications)

        # Validate subnet exists and get VPC ID
        vpc_id = self._get_vpc_id_from_subnet(subnet_id)

        # Validate security groups
        security_group_ids = self._validate_security_group_ids(sg_ids, vpc_id)

        # If IpAddressType is None, determine default from subnet CIDRs
        # For simplicity, we assume subnet has attribute ip_address_type or cidr_block(s)
        # We'll default to ipv4 if not specified
        if ip_address_type is None:
            # Try to infer from subnet
            subnet = self.state.get_resource(subnet_id)
            # Check if subnet has ipv6_cidr_block or dualstack attribute
            has_ipv4 = hasattr(subnet, "cidr_block") and subnet.cidr_block is not None
            has_ipv6 = hasattr(subnet, "ipv6_cidr_block") and subnet.ipv6_cidr_block is not None
            if has_ipv4 and has_ipv6:
                ip_address_type = IpAddressType.DUALSTACK
            elif has_ipv4:
                ip_address_type = IpAddressType.IPV4
            elif has_ipv6:
                ip_address_type = IpAddressType.IPV6
            else:
                ip_address_type = IpAddressType.IPV4  # fallback default

        # Generate unique ID for endpoint
        endpoint_id = f"eice-{self.generate_unique_id()}"

        # Get availability zone and id from subnet
        availability_zone, availability_zone_id = self._get_availability_zone_from_subnet(subnet_id)

        # Compose ARN
        arn = self._generate_arn(endpoint_id)

        # Create the endpoint object
        endpoint = Ec2InstanceConnectEndpoint(
            instanceConnectEndpointId=endpoint_id,
            subnetId=subnet_id,
            vpcId=vpc_id,
            ownerId=self.get_owner_id(),
            state=InstanceConnectEndpointState.CREATE_IN_PROGRESS,
            stateMessage="",
            ipAddressType=ip_address_type,
            preserveClientIp=preserve_client_ip,
            securityGroupIdSet=security_group_ids,
            networkInterfaceIdSet=[],  # No ENIs created in emulator
            availabilityZone=availability_zone,
            availabilityZoneId=availability_zone_id,
            dnsName=None,
            fipsDnsName=None,
            instanceConnectEndpointArn=arn,
            publicDnsNames=None,
            tagSet=tags,
        )

        # Store in shared state dict
        self.state.ec2_instance_connect_endpoints[endpoint_id] = endpoint

        # Return response dict
        response = {
            "clientToken": client_token,
            "instanceConnectEndpoint": endpoint.to_dict(),
            "requestId": self.generate_request_id(),
        }
        return response

    def delete_instance_connect_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter InstanceConnectEndpointId
        endpoint_id = params.get("InstanceConnectEndpointId")
        if not endpoint_id or not isinstance(endpoint_id, str):
            raise ErrorCode("MissingParameter", "InstanceConnectEndpointId is required and must be a string")

        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        endpoint = self.state.ec2_instance_connect_endpoints.get(endpoint_id)
        if endpoint is None:
            raise ErrorCode("InvalidInstanceConnectEndpointID.NotFound", f"EC2 Instance Connect Endpoint {endpoint_id} does not exist")

        # Mark state as delete-in-progress
        endpoint.state = InstanceConnectEndpointState.DELETE_IN_PROGRESS
        endpoint.stateMessage = ""

        # For emulator, we can immediately mark as delete-complete and remove from state
        # But to simulate AWS, we keep it in delete-in-progress state for now
        # Let's simulate immediate deletion for simplicity
        # Save a copy for response before deletion
        response_endpoint = endpoint.to_dict()
        # Remove from state
        del self.state.ec2_instance_connect_endpoints[endpoint_id]

        response = {
            "instanceConnectEndpoint": response_endpoint,
            "requestId": self.generate_request_id(),
        }
        return response

    def describe_instance_connect_endpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Filters: Filter.N with Name and Values
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                # Expect value to be dict with Name and Values
                if not isinstance(value, dict):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a dict")
                filters.append(value)
        if not filters:
            filters_alt = params.get("Filter.N")
            if filters_alt is not None:
                if not isinstance(filters_alt, list):
                    raise ErrorCode("InvalidParameterValue", "Filter.N must be a list of dicts")
                filters = filters_alt

        # InstanceConnectEndpointId.N - list of strings
        endpoint_ids = []
        for key, value in params.items():
            if key.startswith("InstanceConnectEndpointId."):
                if not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", f"{key} must be a string")
                endpoint_ids.append(value)
        if not endpoint_ids:
            endpoint_ids_alt = params.get("InstanceConnectEndpointId.N")
            if endpoint_ids_alt is not None:
                if not isinstance(endpoint_ids_alt, list):
                    raise ErrorCode("InvalidParameterValue", "InstanceConnectEndpointId.N must be a list of strings")
                endpoint_ids = endpoint_ids_alt

        # MaxResults
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
        return {
             "InstanceConnectEndpoints": [],
             "RequestId": self.generate_request_id()
        }

    def modify_instance_connect_endpoint(self, params):
        # Placeholder
        return {}

from emulator_core.gateway.base import BaseGateway

class EC2InstanceConnectEndpointsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateInstanceConnectEndpoint", self.create_instance_connect_endpoint)
        self.register_action("DeleteInstanceConnectEndpoint", self.delete_instance_connect_endpoint)
        self.register_action("DescribeInstanceConnectEndpoints", self.describe_instance_connect_endpoints)
        self.register_action("ModifyInstanceConnectEndpoint", self.modify_instance_connect_endpoint)

    def create_instance_connect_endpoint(self, params):
        return self.backend.create_instance_connect_endpoint(params)

    def delete_instance_connect_endpoint(self, params):
        return self.backend.delete_instance_connect_endpoint(params)

    def describe_instance_connect_endpoints(self, params):
        return self.backend.describe_instance_connect_endpoints(params)

    def modify_instance_connect_endpoint(self, params):
        return self.backend.modify_instance_connect_endpoint(params)
