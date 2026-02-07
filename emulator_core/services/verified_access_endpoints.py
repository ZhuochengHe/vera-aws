from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class VerifiedAccessEndpointAttachmentType(str, Enum):
    VPC = "vpc"


class VerifiedAccessEndpointType(str, Enum):
    LOAD_BALANCER = "load-balancer"
    NETWORK_INTERFACE = "network-interface"
    RDS = "rds"
    CIDR = "cidr"


class VerifiedAccessEndpointProtocol(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"


class VerifiedAccessEndpointStatusCode(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    UPDATING = "updating"
    DELETING = "deleting"
    DELETED = "deleted"


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
class VerifiedAccessEndpointPortRange:
    FromPort: Optional[int] = None
    ToPort: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "FromPort": self.FromPort,
            "ToPort": self.ToPort,
        }


@dataclass
class VerifiedAccessEndpointCidrOptions:
    Cidr: Optional[str] = None
    PortRanges: List[VerifiedAccessEndpointPortRange] = field(default_factory=list)
    Protocol: Optional[VerifiedAccessEndpointProtocol] = None
    SubnetIds: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Cidr": self.Cidr,
            "PortRangeSet": [pr.to_dict() for pr in self.PortRanges],
            "Protocol": self.Protocol.value if self.Protocol else None,
            "SubnetIdSet": self.SubnetIds,
        }


@dataclass
class VerifiedAccessEndpointLoadBalancerOptions:
    LoadBalancerArn: Optional[str] = None
    Port: Optional[int] = None
    PortRanges: List[VerifiedAccessEndpointPortRange] = field(default_factory=list)
    Protocol: Optional[VerifiedAccessEndpointProtocol] = None
    SubnetIds: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "LoadBalancerArn": self.LoadBalancerArn,
            "Port": self.Port,
            "PortRangeSet": [pr.to_dict() for pr in self.PortRanges],
            "Protocol": self.Protocol.value if self.Protocol else None,
            "SubnetIdSet": self.SubnetIds,
        }


@dataclass
class VerifiedAccessEndpointEniOptions:
    NetworkInterfaceId: Optional[str] = None
    Port: Optional[int] = None
    PortRanges: List[VerifiedAccessEndpointPortRange] = field(default_factory=list)
    Protocol: Optional[VerifiedAccessEndpointProtocol] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "NetworkInterfaceId": self.NetworkInterfaceId,
            "Port": self.Port,
            "PortRangeSet": [pr.to_dict() for pr in self.PortRanges],
            "Protocol": self.Protocol.value if self.Protocol else None,
        }


@dataclass
class VerifiedAccessEndpointRdsOptions:
    Port: Optional[int] = None
    Protocol: Optional[VerifiedAccessEndpointProtocol] = None
    RdsDbClusterArn: Optional[str] = None
    RdsDbInstanceArn: Optional[str] = None
    RdsDbProxyArn: Optional[str] = None
    RdsEndpoint: Optional[str] = None
    SubnetIds: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Port": self.Port,
            "Protocol": self.Protocol.value if self.Protocol else None,
            "RdsDbClusterArn": self.RdsDbClusterArn,
            "RdsDbInstanceArn": self.RdsDbInstanceArn,
            "RdsDbProxyArn": self.RdsDbProxyArn,
            "RdsEndpoint": self.RdsEndpoint,
            "SubnetIdSet": self.SubnetIds,
        }


@dataclass
class VerifiedAccessSseSpecificationRequest:
    CustomerManagedKeyEnabled: Optional[bool] = None
    KmsKeyArn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CustomerManagedKeyEnabled": self.CustomerManagedKeyEnabled,
            "KmsKeyArn": self.KmsKeyArn,
        }


@dataclass
class VerifiedAccessSseSpecificationResponse:
    CustomerManagedKeyEnabled: Optional[bool] = None
    KmsKeyArn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CustomerManagedKeyEnabled": self.CustomerManagedKeyEnabled,
            "KmsKeyArn": self.KmsKeyArn,
        }


@dataclass
class VerifiedAccessEndpointStatus:
    Code: Optional[VerifiedAccessEndpointStatusCode] = None
    Message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Code": self.Code.value if self.Code else None,
            "Message": self.Message,
        }


@dataclass
class VerifiedAccessEndpointTarget:
    VerifiedAccessEndpointId: Optional[str] = None
    VerifiedAccessEndpointTargetDns: Optional[str] = None
    VerifiedAccessEndpointTargetIpAddress: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "VerifiedAccessEndpointId": self.VerifiedAccessEndpointId,
            "VerifiedAccessEndpointTargetDns": self.VerifiedAccessEndpointTargetDns,
            "VerifiedAccessEndpointTargetIpAddress": self.VerifiedAccessEndpointTargetIpAddress,
        }


@dataclass
class VerifiedAccessEndpoint:
    applicationDomain: Optional[str] = None
    attachmentType: Optional[VerifiedAccessEndpointAttachmentType] = None
    cidrOptions: Optional[VerifiedAccessEndpointCidrOptions] = None
    creationTime: Optional[str] = None
    deletionTime: Optional[str] = None
    description: Optional[str] = None
    deviceValidationDomain: Optional[str] = None
    domainCertificateArn: Optional[str] = None
    endpointDomain: Optional[str] = None
    endpointType: Optional[VerifiedAccessEndpointType] = None
    lastUpdatedTime: Optional[str] = None
    loadBalancerOptions: Optional[VerifiedAccessEndpointLoadBalancerOptions] = None
    networkInterfaceOptions: Optional[VerifiedAccessEndpointEniOptions] = None
    rdsOptions: Optional[VerifiedAccessEndpointRdsOptions] = None
    securityGroupIdSet: List[str] = field(default_factory=list)
    sseSpecification: Optional[VerifiedAccessSseSpecificationResponse] = None
    status: Optional[VerifiedAccessEndpointStatus] = None
    tagSet: List[Tag] = field(default_factory=list)
    verifiedAccessEndpointId: Optional[str] = None
    verifiedAccessGroupId: Optional[str] = None
    verifiedAccessInstanceId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applicationDomain": self.applicationDomain,
            "attachmentType": self.attachmentType.value if self.attachmentType else None,
            "cidrOptions": self.cidrOptions.to_dict() if self.cidrOptions else None,
            "creationTime": self.creationTime,
            "deletionTime": self.deletionTime,
            "description": self.description,
            "deviceValidationDomain": self.deviceValidationDomain,
            "domainCertificateArn": self.domainCertificateArn,
            "endpointDomain": self.endpointDomain,
            "endpointType": self.endpointType.value if self.endpointType else None,
            "lastUpdatedTime": self.lastUpdatedTime,
            "loadBalancerOptions": self.loadBalancerOptions.to_dict() if self.loadBalancerOptions else None,
            "networkInterfaceOptions": self.networkInterfaceOptions.to_dict() if self.networkInterfaceOptions else None,
            "rdsOptions": self.rdsOptions.to_dict() if self.rdsOptions else None,
            "securityGroupIdSet": self.securityGroupIdSet,
            "sseSpecification": self.sseSpecification.to_dict() if self.sseSpecification else None,
            "status": self.status.to_dict() if self.status else None,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "verifiedAccessEndpointId": self.verifiedAccessEndpointId,
            "verifiedAccessGroupId": self.verifiedAccessGroupId,
            "verifiedAccessInstanceId": self.verifiedAccessInstanceId,
        }


class VerifiedAccessendpointsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.verified_access_endpoints

    def create_verified_access_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Validate required parameters
        attachment_type = params.get("AttachmentType")
        if not attachment_type:
            raise ValueError("AttachmentType is required")
        endpoint_type = params.get("EndpointType")
        if not endpoint_type:
            raise ValueError("EndpointType is required")
        verified_access_group_id = params.get("VerifiedAccessGroupId")
        if not verified_access_group_id:
            raise ValueError("VerifiedAccessGroupId is required")

        # Validate AttachmentType value
        if attachment_type != "vpc":
            raise ValueError("Invalid AttachmentType, valid value is 'vpc'")

        # Validate EndpointType value
        valid_endpoint_types = {"load-balancer", "network-interface", "rds", "cidr"}
        if endpoint_type not in valid_endpoint_types:
            raise ValueError(f"Invalid EndpointType, valid values are {valid_endpoint_types}")

        # Validate SecurityGroupId.N if AttachmentType is vpc
        security_group_ids = params.get("SecurityGroupId.N", [])
        if attachment_type == "vpc" and not security_group_ids:
            raise ValueError("SecurityGroupId.N is required when AttachmentType is 'vpc'")

        # Helper function to parse port ranges
        def parse_port_ranges(port_ranges_param):
            port_ranges = []
            if port_ranges_param:
                for pr in port_ranges_param:
                    from_port = pr.get("FromPort")
                    to_port = pr.get("ToPort")
                    if from_port is not None:
                        if not (1 <= from_port <= 65535):
                            raise ValueError("FromPort must be between 1 and 65535")
                    if to_port is not None:
                        if not (1 <= to_port <= 65535):
                            raise ValueError("ToPort must be between 1 and 65535")
                    port_ranges.append(VerifiedAccessEndpointPortRange(FromPort=from_port, ToPort=to_port))
            return port_ranges

        # Parse CidrOptions if present
        cidr_options_param = params.get("CidrOptions")
        cidr_options = None
        if cidr_options_param:
            cidr = cidr_options_param.get("Cidr")
            port_ranges = parse_port_ranges(cidr_options_param.get("PortRanges"))
            protocol = cidr_options_param.get("Protocol")
            if protocol and protocol not in {"http", "https", "tcp"}:
                raise ValueError("Invalid protocol in CidrOptions, valid values are http, https, tcp")
            subnet_ids = cidr_options_param.get("SubnetIds", [])
            cidr_options = VerifiedAccessEndpointCidrOptions(
                Cidr=cidr,
                PortRanges=port_ranges,
                Protocol=VerifiedAccessEndpointProtocol(protocol) if protocol else None,
                SubnetIds=subnet_ids,
            )

        # Parse LoadBalancerOptions if present
        load_balancer_options_param = params.get("LoadBalancerOptions")
        load_balancer_options = None
        if load_balancer_options_param:
            lb_arn = load_balancer_options_param.get("LoadBalancerArn")
            port = load_balancer_options_param.get("Port")
            if port is not None and not (1 <= port <= 65535):
                raise ValueError("Port in LoadBalancerOptions must be between 1 and 65535")
            port_ranges = parse_port_ranges(load_balancer_options_param.get("PortRanges"))
            protocol = load_balancer_options_param.get("Protocol")
            if protocol and protocol not in {"http", "https", "tcp"}:
                raise ValueError("Invalid protocol in LoadBalancerOptions, valid values are http, https, tcp")
            subnet_ids = load_balancer_options_param.get("SubnetIds", [])
            load_balancer_options = VerifiedAccessEndpointLoadBalancerOptions(
                LoadBalancerArn=lb_arn,
                Port=port,
                PortRanges=port_ranges,
                Protocol=VerifiedAccessEndpointProtocol(protocol) if protocol else None,
                SubnetIds=subnet_ids,
            )

        # Parse NetworkInterfaceOptions if present
        network_interface_options_param = params.get("NetworkInterfaceOptions")
        network_interface_options = None
        if network_interface_options_param:
            network_interface_id = network_interface_options_param.get("NetworkInterfaceId")
            port = network_interface_options_param.get("Port")
            if port is not None and not (1 <= port <= 65535):
                raise ValueError("Port in NetworkInterfaceOptions must be between 1 and 65535")
            port_ranges = parse_port_ranges(network_interface_options_param.get("PortRanges"))
            protocol = network_interface_options_param.get("Protocol")
            if protocol and protocol not in {"http", "https", "tcp"}:
                raise ValueError("Invalid protocol in NetworkInterfaceOptions, valid values are http, https, tcp")
            network_interface_options = VerifiedAccessEndpointEniOptions(
                NetworkInterfaceId=network_interface_id,
                Port=port,
                PortRanges=port_ranges,
                Protocol=VerifiedAccessEndpointProtocol(protocol) if protocol else None,
            )

        # Parse RdsOptions if present
        rds_options_param = params.get("RdsOptions")
        rds_options = None
        if rds_options_param:
            port = rds_options_param.get("Port")
            if port is not None and not (1 <= port <= 65535):
                raise ValueError("Port in RdsOptions must be between 1 and 65535")
            protocol = rds_options_param.get("Protocol")
            if protocol and protocol not in {"http", "https", "tcp"}:
                raise ValueError("Invalid protocol in RdsOptions, valid values are http, https, tcp")
            rds_db_cluster_arn = rds_options_param.get("RdsDbClusterArn")
            rds_db_instance_arn = rds_options_param.get("RdsDbInstanceArn")
            rds_db_proxy_arn = rds_options_param.get("RdsDbProxyArn")
            rds_endpoint = rds_options_param.get("RdsEndpoint")
            subnet_ids = rds_options_param.get("SubnetIds", [])
            rds_options = VerifiedAccessEndpointRdsOptions(
                Port=port,
                Protocol=VerifiedAccessEndpointProtocol(protocol) if protocol else None,
                RdsDbClusterArn=rds_db_cluster_arn,
                RdsDbInstanceArn=rds_db_instance_arn,
                RdsDbProxyArn=rds_db_proxy_arn,
                RdsEndpoint=rds_endpoint,
                SubnetIds=subnet_ids,
            )

        # Parse SSE Specification if present
        sse_spec_param = params.get("SseSpecification")
        sse_specification = None
        if sse_spec_param:
            customer_managed_key_enabled = sse_spec_param.get("CustomerManagedKeyEnabled")
            kms_key_arn = sse_spec_param.get("KmsKeyArn")
            sse_specification = VerifiedAccessSseSpecificationResponse(
                CustomerManagedKeyEnabled=customer_managed_key_enabled,
                KmsKeyArn=kms_key_arn,
            )

        # Parse TagSpecification.N if present
        tag_specifications_param = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications_param:
            # Only process if ResourceType is 'verified-access-endpoint'
            resource_type = tag_spec.get("ResourceType")
            if resource_type != "verified-access-endpoint":
                continue
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Generate unique VerifiedAccessEndpointId and requestId
        verified_access_endpoint_id = self.generate_unique_id()
        request_id = self.generate_request_id()

        # Current time in ISO8601 format
        now_iso = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        # Compose endpointDomain using EndpointDomainPrefix if provided
        endpoint_domain_prefix = params.get("EndpointDomainPrefix")
        endpoint_domain = None
        if endpoint_domain_prefix:
            # Compose endpoint domain as prefix + some domain suffix (simulate)
            endpoint_domain = f"{endpoint_domain_prefix}.verified-access-endpoint.aws"

        # Compose VerifiedAccessEndpointStatus with code 'pending' and message None initially
        status = VerifiedAccessEndpointStatus(Code=VerifiedAccessEndpointStatusCode.PENDING, Message=None)

        # Create VerifiedAccessEndpoint object
        endpoint = VerifiedAccessEndpoint(
            applicationDomain=params.get("ApplicationDomain"),
            attachmentType=VerifiedAccessEndpointAttachmentType(attachment_type),
            cidrOptions=cidr_options,
            creationTime=now_iso,
            deletionTime=None,
            description=params.get("Description"),
            deviceValidationDomain=None,
            domainCertificateArn=params.get("DomainCertificateArn"),
            endpointDomain=endpoint_domain,
            endpointType=VerifiedAccessEndpointType(endpoint_type),
            lastUpdatedTime=now_iso,
            loadBalancerOptions=load_balancer_options,
            networkInterfaceOptions=network_interface_options,
            rdsOptions=rds_options,
            securityGroupIdSet=security_group_ids,
            sseSpecification=sse_specification,
            status=status,
            tagSet=tags,
            verifiedAccessEndpointId=verified_access_endpoint_id,
            verifiedAccessGroupId=verified_access_group_id,
            verifiedAccessInstanceId=None,
        )

        # Store in state
        self.state.verified_access_endpoints[verified_access_endpoint_id] = endpoint
        self.state.resources[verified_access_endpoint_id] = endpoint

        return {
            "requestId": request_id,
            "verifiedAccessEndpoint": endpoint.to_dict(),
        }


    def delete_verified_access_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        verified_access_endpoint_id = params.get("VerifiedAccessEndpointId")
        if not verified_access_endpoint_id:
            raise ValueError("VerifiedAccessEndpointId is required")

        request_id = self.generate_request_id()

        endpoint = self.state.verified_access_endpoints.get(verified_access_endpoint_id)
        if not endpoint:
            # According to AWS behavior, deleting a non-existent resource is not an error, just return empty or None
            return {
                "requestId": request_id,
                "verifiedAccessEndpoint": None,
            }

        # Mark deletion time and status
        now_iso = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        endpoint.deletionTime = now_iso
        endpoint.status = VerifiedAccessEndpointStatus(
            Code=VerifiedAccessEndpointStatusCode.DELETING,
            Message="Deletion in progress",
        )
        endpoint.lastUpdatedTime = now_iso

        # Remove from state to simulate deletion
        del self.state.verified_access_endpoints[verified_access_endpoint_id]
        if verified_access_endpoint_id in self.state.resources:
            del self.state.resources[verified_access_endpoint_id]

        return {
            "requestId": request_id,
            "verifiedAccessEndpoint": endpoint.to_dict(),
        }


    def describe_verified_access_endpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Filters and pagination
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        verified_access_endpoint_ids = params.get("VerifiedAccessEndpointId.N", [])
        verified_access_group_id = params.get("VerifiedAccessGroupId")
        verified_access_instance_id = params.get("VerifiedAccessInstanceId")

        request_id = self.generate_request_id()

        # Collect all endpoints
        endpoints = list(self.state.verified_access_endpoints.values())

        # Filter by VerifiedAccessEndpointId.N if provided
        if verified_access_endpoint_ids:
            endpoints = [ep for ep in endpoints if ep.verifiedAccessEndpointId in verified_access_endpoint_ids]

        # Filter by VerifiedAccessGroupId if provided
        if verified_access_group_id:
            endpoints = [ep for ep in endpoints if ep.verifiedAccessGroupId == verified_access_group_id]

        # Filter by VerifiedAccessInstanceId if provided
        if verified_access_instance_id:
            endpoints = [ep for ep in endpoints if ep.verifiedAccessInstanceId == verified_access_instance_id]

        # Apply filters if any
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            # Support some common filters by name
            if name == "verified-access-endpoint-id":
                endpoints = [ep for ep in endpoints if ep.verifiedAccessEndpointId in values]
            elif name == "verified-access-group-id":
                endpoints = [ep for ep in endpoints if ep.verifiedAccessGroupId in values]
            elif name == "attachment-type":
                endpoints = [ep for ep in endpoints if ep.attachmentType and ep.attachmentType.value in values]
            elif name == "endpoint-type":
                endpoints = [ep for ep in endpoints if ep.endpointType and ep.endpointType.value in values]
            elif name == "status-code":
                endpoints = [ep for ep in endpoints if ep.status and ep.status.Code and ep.status.Code.value in values]
            # Add more filters as needed

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        end_index = start_index + max_results
        paged_endpoints = endpoints[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(endpoints) else None

        return {
            "nextToken": new_next_token,
            "requestId": request_id,
            "verifiedAccessEndpointSet": [ep.to_dict() for ep in paged_endpoints],
        }


    def get_verified_access_endpoint_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        verified_access_endpoint_id = params.get("VerifiedAccessEndpointId")
        if not verified_access_endpoint_id:
            raise ValueError("VerifiedAccessEndpointId is required")

        request_id = self.generate_request_id()

        endpoint = self.state.verified_access_endpoints.get(verified_access_endpoint_id)
        if not endpoint:
            # Return empty policy and disabled if endpoint not found
            return {
                "policyDocument": None,
                "policyEnabled": False,
                "requestId": request_id,
            }

        # Assume policyDocument is stored as attribute on endpoint, else None
        policy_document = getattr(endpoint, "policyDocument", None)
        policy_enabled = bool(policy_document)

        return {
            "policyDocument": policy_document,
            "policyEnabled": policy_enabled,
            "requestId": request_id,
        }


    def get_verified_access_endpoint_targets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        verified_access_endpoint_id = params.get("VerifiedAccessEndpointId")
        if not verified_access_endpoint_id:
            raise ValueError("VerifiedAccessEndpointId is required")

        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        request_id = self.generate_request_id()

        # For this emulator, assume targets are stored in state as dict keyed by endpoint id
        # If not present, empty list
        targets_all = self.state.verified_access_endpoint_targets.get(verified_access_endpoint_id, [])

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(1000, int(max_results)))

        end_index = start_index + max_results
        paged_targets = targets_all[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(targets_all) else None

        return {
            "nextToken": new_next_token,
            "requestId": request_id,
            "verifiedAccessEndpointTargetSet": [t.to_dict() for t in paged_targets],
        }

    def modify_verified_access_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
        verified_access_endpoint_id = params.get("VerifiedAccessEndpointId")
        if not verified_access_endpoint_id:
            raise ValueError("VerifiedAccessEndpointId is required")

        endpoint = self.state.verified_access_endpoints.get(verified_access_endpoint_id)
        if not endpoint:
            raise ValueError(f"VerifiedAccessEndpoint with id {verified_access_endpoint_id} does not exist")

        # DryRun check
        if params.get("DryRun"):
            # For emulator, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Update Description
        description = params.get("Description")
        if description is not None:
            if not isinstance(description, str):
                raise ValueError("Description must be a string")
            endpoint.description = description

        # Update VerifiedAccessGroupId
        verified_access_group_id = params.get("VerifiedAccessGroupId")
        if verified_access_group_id is not None:
            if not isinstance(verified_access_group_id, str):
                raise ValueError("VerifiedAccessGroupId must be a string")
            endpoint.verifiedAccessGroupId = verified_access_group_id

        # Update CidrOptions
        cidr_options_param = params.get("CidrOptions")
        if cidr_options_param is not None:
            # Validate and update cidrOptions
            port_ranges_param = cidr_options_param.get("PortRanges", [])
            port_ranges = []
            for pr in port_ranges_param:
                from_port = pr.get("FromPort")
                to_port = pr.get("ToPort")
                if from_port is not None:
                    if not (1 <= from_port <= 65535):
                        raise ValueError("FromPort must be between 1 and 65535")
                if to_port is not None:
                    if not (1 <= to_port <= 65535):
                        raise ValueError("ToPort must be between 1 and 65535")
                port_ranges.append(VerifiedAccessEndpointPortRange(FromPort=from_port, ToPort=to_port))
            cidr = cidr_options_param.get("Cidr")
            protocol_str = cidr_options_param.get("Protocol")
            protocol = None
            if protocol_str is not None:
                try:
                    protocol = VerifiedAccessEndpointProtocol(protocol_str)
                except Exception:
                    raise ValueError(f"Invalid Protocol value: {protocol_str}")
            subnet_ids = cidr_options_param.get("SubnetIds", [])
            if not isinstance(subnet_ids, list):
                raise ValueError("SubnetIds must be a list of strings")
            endpoint.cidrOptions = VerifiedAccessEndpointCidrOptions(
                Cidr=cidr,
                PortRanges=port_ranges,
                Protocol=protocol,
                SubnetIds=subnet_ids,
            )

        # Update LoadBalancerOptions
        lb_options_param = params.get("LoadBalancerOptions")
        if lb_options_param is not None:
            port = lb_options_param.get("Port")
            if port is not None and not (1 <= port <= 65535):
                raise ValueError("LoadBalancerOptions Port must be between 1 and 65535")
            port_ranges_param = lb_options_param.get("PortRanges", [])
            port_ranges = []
            for pr in port_ranges_param:
                from_port = pr.get("FromPort")
                to_port = pr.get("ToPort")
                if from_port is not None:
                    if not (1 <= from_port <= 65535):
                        raise ValueError("LoadBalancerOptions PortRanges FromPort must be between 1 and 65535")
                if to_port is not None:
                    if not (1 <= to_port <= 65535):
                        raise ValueError("LoadBalancerOptions PortRanges ToPort must be between 1 and 65535")
                port_ranges.append(VerifiedAccessEndpointPortRange(FromPort=from_port, ToPort=to_port))
            protocol_str = lb_options_param.get("Protocol")
            protocol = None
            if protocol_str is not None:
                try:
                    protocol = VerifiedAccessEndpointProtocol(protocol_str)
                except Exception:
                    raise ValueError(f"Invalid LoadBalancerOptions Protocol value: {protocol_str}")
            subnet_ids = lb_options_param.get("SubnetIds", [])
            if not isinstance(subnet_ids, list):
                raise ValueError("LoadBalancerOptions SubnetIds must be a list of strings")
            load_balancer_arn = lb_options_param.get("LoadBalancerArn")
            endpoint.loadBalancerOptions = VerifiedAccessEndpointLoadBalancerOptions(
                LoadBalancerArn=load_balancer_arn,
                Port=port,
                PortRanges=port_ranges,
                Protocol=protocol,
                SubnetIds=subnet_ids,
            )

        # Update NetworkInterfaceOptions
        eni_options_param = params.get("NetworkInterfaceOptions")
        if eni_options_param is not None:
            port = eni_options_param.get("Port")
            if port is not None and not (1 <= port <= 65535):
                raise ValueError("NetworkInterfaceOptions Port must be between 1 and 65535")
            port_ranges_param = eni_options_param.get("PortRanges", [])
            port_ranges = []
            for pr in port_ranges_param:
                from_port = pr.get("FromPort")
                to_port = pr.get("ToPort")
                if from_port is not None:
                    if not (1 <= from_port <= 65535):
                        raise ValueError("NetworkInterfaceOptions PortRanges FromPort must be between 1 and 65535")
                if to_port is not None:
                    if not (1 <= to_port <= 65535):
                        raise ValueError("NetworkInterfaceOptions PortRanges ToPort must be between 1 and 65535")
                port_ranges.append(VerifiedAccessEndpointPortRange(FromPort=from_port, ToPort=to_port))
            protocol_str = eni_options_param.get("Protocol")
            protocol = None
            if protocol_str is not None:
                try:
                    protocol = VerifiedAccessEndpointProtocol(protocol_str)
                except Exception:
                    raise ValueError(f"Invalid NetworkInterfaceOptions Protocol value: {protocol_str}")
            network_interface_id = eni_options_param.get("NetworkInterfaceId")
            endpoint.networkInterfaceOptions = VerifiedAccessEndpointEniOptions(
                NetworkInterfaceId=network_interface_id,
                Port=port,
                PortRanges=port_ranges,
                Protocol=protocol,
            )

        # Update RdsOptions
        rds_options_param = params.get("RdsOptions")
        if rds_options_param is not None:
            port = rds_options_param.get("Port")
            if port is not None and not (1 <= port <= 65535):
                raise ValueError("RdsOptions Port must be between 1 and 65535")
            rds_endpoint = rds_options_param.get("RdsEndpoint")
            subnet_ids = rds_options_param.get("SubnetIds", [])
            if not isinstance(subnet_ids, list):
                raise ValueError("RdsOptions SubnetIds must be a list of strings")
            # Protocol is not in request param but is in response, so keep existing or None
            protocol = None
            # We do not have protocol in request param, so keep existing if any
            if endpoint.rdsOptions is not None:
                protocol = endpoint.rdsOptions.Protocol
            endpoint.rdsOptions = VerifiedAccessEndpointRdsOptions(
                Port=port,
                Protocol=protocol,
                RdsDbClusterArn=None,
                RdsDbInstanceArn=None,
                RdsDbProxyArn=None,
                RdsEndpoint=rds_endpoint,
                SubnetIds=subnet_ids,
            )

        # Update lastUpdatedTime to current ISO8601 string
        from datetime import datetime, timezone
        endpoint.lastUpdatedTime = datetime.now(timezone.utc).isoformat()

        # Save updated endpoint back to state
        self.state.verified_access_endpoints[verified_access_endpoint_id] = endpoint

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessEndpoint": endpoint.to_dict(),
        }


    def modify_verified_access_endpoint_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        verified_access_endpoint_id = params.get("VerifiedAccessEndpointId")
        if not verified_access_endpoint_id:
            raise ValueError("VerifiedAccessEndpointId is required")

        endpoint = self.state.verified_access_endpoints.get(verified_access_endpoint_id)
        if not endpoint:
            raise ValueError(f"VerifiedAccessEndpoint with id {verified_access_endpoint_id} does not exist")

        # DryRun check
        if params.get("DryRun"):
            # For emulator, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Update policy document and enabled status
        policy_document = params.get("PolicyDocument")
        policy_enabled = params.get("PolicyEnabled")

        # Update SSE specification if provided
        sse_spec_param = params.get("SseSpecification")
        sse_spec_response = None
        if sse_spec_param is not None:
            customer_managed_key_enabled = sse_spec_param.get("CustomerManagedKeyEnabled")
            kms_key_arn = sse_spec_param.get("KmsKeyArn")
            sse_spec_response = VerifiedAccessSseSpecificationResponse(
                CustomerManagedKeyEnabled=customer_managed_key_enabled,
                KmsKeyArn=kms_key_arn,
            )
        else:
            # If no update, keep existing if any
            sse_spec_response = getattr(endpoint, "sseSpecification", None)

        # Store policy and policy enabled status on endpoint object
        # We add attributes to endpoint for policyDocument and policyEnabled for emulator state
        setattr(endpoint, "policyDocument", policy_document)
        setattr(endpoint, "policyEnabled", policy_enabled)
        endpoint.sseSpecification = sse_spec_response

        # Save updated endpoint back to state
        self.state.verified_access_endpoints[verified_access_endpoint_id] = endpoint

        return {
            "requestId": self.generate_request_id(),
            "policyDocument": policy_document,
            "policyEnabled": policy_enabled,
            "sseSpecification": sse_spec_response.to_dict() if sse_spec_response else None,
        }

    

from emulator_core.gateway.base import BaseGateway

class VerifiedAccessendpointsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateVerifiedAccessEndpoint", self.create_verified_access_endpoint)
        self.register_action("DeleteVerifiedAccessEndpoint", self.delete_verified_access_endpoint)
        self.register_action("DescribeVerifiedAccessEndpoints", self.describe_verified_access_endpoints)
        self.register_action("GetVerifiedAccessEndpointPolicy", self.get_verified_access_endpoint_policy)
        self.register_action("GetVerifiedAccessEndpointTargets", self.get_verified_access_endpoint_targets)
        self.register_action("ModifyVerifiedAccessEndpoint", self.modify_verified_access_endpoint)
        self.register_action("ModifyVerifiedAccessEndpointPolicy", self.modify_verified_access_endpoint_policy)

    def create_verified_access_endpoint(self, params):
        return self.backend.create_verified_access_endpoint(params)

    def delete_verified_access_endpoint(self, params):
        return self.backend.delete_verified_access_endpoint(params)

    def describe_verified_access_endpoints(self, params):
        return self.backend.describe_verified_access_endpoints(params)

    def get_verified_access_endpoint_policy(self, params):
        return self.backend.get_verified_access_endpoint_policy(params)

    def get_verified_access_endpoint_targets(self, params):
        return self.backend.get_verified_access_endpoint_targets(params)

    def modify_verified_access_endpoint(self, params):
        return self.backend.modify_verified_access_endpoint(params)

    def modify_verified_access_endpoint_policy(self, params):
        return self.backend.modify_verified_access_endpoint_policy(params)
