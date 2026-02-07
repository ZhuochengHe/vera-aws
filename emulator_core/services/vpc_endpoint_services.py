from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class ServiceState(Enum):
    PENDING = "Pending"
    AVAILABLE = "Available"
    DELETING = "Deleting"
    DELETED = "Deleted"
    FAILED = "Failed"


class PrivateDnsNameVerificationState(Enum):
    PENDING_VERIFICATION = "pendingVerification"
    VERIFIED = "verified"
    FAILED = "failed"


class ServiceTypeEnum(Enum):
    INTERFACE = "Interface"
    GATEWAY = "Gateway"
    GATEWAY_LOAD_BALANCER = "GatewayLoadBalancer"


class PrincipalTypeEnum(Enum):
    ALL = "All"
    SERVICE = "Service"
    ORGANIZATION_UNIT = "OrganizationUnit"
    ACCOUNT = "Account"
    USER = "User"
    ROLE = "Role"


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
class UnsuccessfulItemError:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.code is not None:
            d["Code"] = self.code
        if self.message is not None:
            d["Message"] = self.message
        return d


@dataclass
class UnsuccessfulItem:
    error: Optional[UnsuccessfulItemError] = None
    resourceId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.error is not None:
            d["Error"] = self.error.to_dict()
        if self.resourceId is not None:
            d["ResourceId"] = self.resourceId
        return d


@dataclass
class ServiceTypeDetail:
    serviceType: Optional[ServiceTypeEnum] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ServiceType": self.serviceType.value if self.serviceType else None
        }


@dataclass
class PrivateDnsNameConfiguration:
    name: Optional[str] = None
    state: Optional[PrivateDnsNameVerificationState] = None
    type: Optional[str] = None
    value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.name is not None:
            d["Name"] = self.name
        if self.state is not None:
            d["State"] = self.state.value
        if self.type is not None:
            d["Type"] = self.type
        if self.value is not None:
            d["Value"] = self.value
        return d


@dataclass
class SupportedRegionDetail:
    region: Optional[str] = None
    serviceState: Optional[ServiceState] = None  # includes Closed state not in enum

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.region is not None:
            d["Region"] = self.region
        if self.serviceState is not None:
            d["ServiceState"] = self.serviceState.value
        return d


@dataclass
class ServiceConfiguration:
    acceptanceRequired: Optional[bool] = None
    availabilityZoneIdSet: List[str] = field(default_factory=list)
    availabilityZoneSet: List[str] = field(default_factory=list)
    baseEndpointDnsNameSet: List[str] = field(default_factory=list)
    gatewayLoadBalancerArnSet: List[str] = field(default_factory=list)
    managesVpcEndpoints: Optional[bool] = None
    networkLoadBalancerArnSet: List[str] = field(default_factory=list)
    payerResponsibility: Optional[str] = None  # Valid Values: ServiceOwner
    privateDnsName: Optional[str] = None
    privateDnsNameConfiguration: Optional[PrivateDnsNameConfiguration] = None
    remoteAccessEnabled: Optional[bool] = None
    serviceId: Optional[str] = None
    serviceName: Optional[str] = None
    serviceState: Optional[ServiceState] = None
    serviceType: List[ServiceTypeDetail] = field(default_factory=list)
    supportedIpAddressTypeSet: List[str] = field(default_factory=list)  # ipv4, ipv6
    supportedRegionSet: List[SupportedRegionDetail] = field(default_factory=list)
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.acceptanceRequired is not None:
            d["AcceptanceRequired"] = self.acceptanceRequired
        if self.availabilityZoneIdSet:
            d["AvailabilityZoneIdSet"] = self.availabilityZoneIdSet
        if self.availabilityZoneSet:
            d["AvailabilityZoneSet"] = self.availabilityZoneSet
        if self.baseEndpointDnsNameSet:
            d["BaseEndpointDnsNameSet"] = self.baseEndpointDnsNameSet
        if self.gatewayLoadBalancerArnSet:
            d["GatewayLoadBalancerArnSet"] = self.gatewayLoadBalancerArnSet
        if self.managesVpcEndpoints is not None:
            d["ManagesVpcEndpoints"] = self.managesVpcEndpoints
        if self.networkLoadBalancerArnSet:
            d["NetworkLoadBalancerArnSet"] = self.networkLoadBalancerArnSet
        if self.payerResponsibility is not None:
            d["PayerResponsibility"] = self.payerResponsibility
        if self.privateDnsName is not None:
            d["PrivateDnsName"] = self.privateDnsName
        if self.privateDnsNameConfiguration is not None:
            d["PrivateDnsNameConfiguration"] = self.privateDnsNameConfiguration.to_dict()
        if self.remoteAccessEnabled is not None:
            d["RemoteAccessEnabled"] = self.remoteAccessEnabled
        if self.serviceId is not None:
            d["ServiceId"] = self.serviceId
        if self.serviceName is not None:
            d["ServiceName"] = self.serviceName
        if self.serviceState is not None:
            d["ServiceState"] = self.serviceState.value
        if self.serviceType:
            d["ServiceType"] = [st.to_dict() for st in self.serviceType]
        if self.supportedIpAddressTypeSet:
            d["SupportedIpAddressTypeSet"] = self.supportedIpAddressTypeSet
        if self.supportedRegionSet:
            d["SupportedRegionSet"] = [sr.to_dict() for sr in self.supportedRegionSet]
        if self.tagSet:
            d["TagSet"] = [tag.to_dict() for tag in self.tagSet]
        return d


@dataclass
class AllowedPrincipal:
    principal: Optional[str] = None
    principalType: Optional[PrincipalTypeEnum] = None
    serviceId: Optional[str] = None
    servicePermissionId: Optional[str] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.principal is not None:
            d["Principal"] = self.principal
        if self.principalType is not None:
            d["PrincipalType"] = self.principalType.value
        if self.serviceId is not None:
            d["ServiceId"] = self.serviceId
        if self.servicePermissionId is not None:
            d["ServicePermissionId"] = self.servicePermissionId
        if self.tagSet:
            d["TagSet"] = [tag.to_dict() for tag in self.tagSet]
        return d


@dataclass
class AddedPrincipal:
    principal: Optional[str] = None
    principalType: Optional[PrincipalTypeEnum] = None
    serviceId: Optional[str] = None
    servicePermissionId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.principal is not None:
            d["Principal"] = self.principal
        if self.principalType is not None:
            d["PrincipalType"] = self.principalType.value
        if self.serviceId is not None:
            d["ServiceId"] = self.serviceId
        if self.servicePermissionId is not None:
            d["ServicePermissionId"] = self.servicePermissionId
        return d


@dataclass
class PrivateDnsDetails:
    privateDnsName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.privateDnsName is not None:
            d["PrivateDnsName"] = self.privateDnsName
        return d


@dataclass
class ServiceDetail:
    acceptanceRequired: Optional[bool] = None
    availabilityZoneIdSet: List[str] = field(default_factory=list)
    availabilityZoneSet: List[str] = field(default_factory=list)
    baseEndpointDnsNameSet: List[str] = field(default_factory=list)
    managesVpcEndpoints: Optional[bool] = None
    owner: Optional[str] = None
    payerResponsibility: Optional[str] = None
    privateDnsName: Optional[str] = None
    privateDnsNameSet: List[PrivateDnsDetails] = field(default_factory=list)
    privateDnsNameVerificationState: Optional[PrivateDnsNameVerificationState] = None
    serviceId: Optional[str] = None
    serviceName: Optional[str] = None
    serviceRegion: Optional[str] = None
    serviceType: List[ServiceTypeDetail] = field(default_factory=list)
    supportedIpAddressTypeSet: List[str] = field(default_factory=list)
    tagSet: List[Tag] = field(default_factory=list)
    vpcEndpointPolicySupported: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.acceptanceRequired is not None:
            d["AcceptanceRequired"] = self.acceptanceRequired
        if self.availabilityZoneIdSet:
            d["AvailabilityZoneIdSet"] = self.availabilityZoneIdSet
        if self.availabilityZoneSet:
            d["AvailabilityZoneSet"] = self.availabilityZoneSet
        if self.baseEndpointDnsNameSet:
            d["BaseEndpointDnsNameSet"] = self.baseEndpointDnsNameSet
        if self.managesVpcEndpoints is not None:
            d["ManagesVpcEndpoints"] = self.managesVpcEndpoints
        if self.owner is not None:
            d["Owner"] = self.owner
        if self.payerResponsibility is not None:
            d["PayerResponsibility"] = self.payerResponsibility
        if self.privateDnsName is not None:
            d["PrivateDnsName"] = self.privateDnsName
        if self.privateDnsNameSet:
            d["PrivateDnsNameSet"] = [pd.to_dict() for pd in self.privateDnsNameSet]
        if self.privateDnsNameVerificationState is not None:
            d["PrivateDnsNameVerificationState"] = self.privateDnsNameVerificationState.value
        if self.serviceId is not None:
            d["ServiceId"] = self.serviceId
        if self.serviceName is not None:
            d["ServiceName"] = self.serviceName
        if self.serviceRegion is not None:
            d["ServiceRegion"] = self.serviceRegion
        if self.serviceType:
            d["ServiceType"] = [st.to_dict() for st in self.serviceType]
        if self.supportedIpAddressTypeSet:
            d["SupportedIpAddressTypeSet"] = self.supportedIpAddressTypeSet
        if self.tagSet:
            d["TagSet"] = [tag.to_dict() for tag in self.tagSet]
        if self.vpcEndpointPolicySupported is not None:
            d["VpcEndpointPolicySupported"] = self.vpcEndpointPolicySupported
        return d


@dataclass
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"Name": self.Name, "Values": self.Values}


class VPCendpointservicesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state for persistent data storage.

    def accept_vpc_endpoint_connections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        service_id = params.get("ServiceId")
        vpc_endpoint_ids = []
        # Collect VpcEndpointId.N keys
        for key in params:
            if key.startswith("VpcEndpointId."):
                vpc_endpoint_ids.append(params[key])
        unsuccessful = []

        # Validate required parameters
        if not service_id:
            # Missing required parameter ServiceId
            # According to AWS API, this would raise an error, but here we just return empty unsuccessful
            return {
                "requestId": self.generate_request_id(),
                "unsuccessful": unsuccessful,
            }
        if not vpc_endpoint_ids:
            # Missing required VpcEndpointId.N
            return {
                "requestId": self.generate_request_id(),
                "unsuccessful": unsuccessful,
            }

        # Get the service from state
        service = self.state.vpc_endpoint_services.get(service_id)
        if not service:
            # Service not found, all endpoints unsuccessful with error
            for vpce_id in vpc_endpoint_ids:
                error = UnsuccessfulItemError(
                    code="InvalidServiceId",
                    message=f"The service ID '{service_id}' does not exist."
                )
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=error,
                        resourceId=vpce_id
                    )
                )
            return {
                "requestId": self.generate_request_id(),
                "unsuccessful": unsuccessful,
            }

        # For each VPC endpoint id, check if it exists and is in pending acceptance state
        for vpce_id in vpc_endpoint_ids:
            vpce = self.state.get_resource(vpce_id)
            if not vpce:
                error = UnsuccessfulItemError(
                    code="InvalidVpcEndpointId",
                    message=f"The VPC endpoint ID '{vpce_id}' does not exist."
                )
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=error,
                        resourceId=vpce_id
                    )
                )
                continue

            # Check if the endpoint is associated with the service
            if vpce.service_id != service_id:
                error = UnsuccessfulItemError(
                    code="InvalidVpcEndpointId",
                    message=f"The VPC endpoint ID '{vpce_id}' is not associated with service '{service_id}'."
                )
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=error,
                        resourceId=vpce_id
                    )
                )
                continue

            # Check if the endpoint is in pending acceptance state
            # Assuming vpce has attribute 'state' and enum ServiceState.PENDING_ACCEPTANCE or similar
            # Since ServiceState enum is not fully detailed, assume 'PENDING' means pending acceptance
            if vpce.state != ServiceState.PENDING:
                error = UnsuccessfulItemError(
                    code="IncorrectState",
                    message=f"The VPC endpoint ID '{vpce_id}' is not in a state that can be accepted."
                )
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=error,
                        resourceId=vpce_id
                    )
                )
                continue

            # Accept the connection: set state to Available or Accepted
            vpce.state = ServiceState.AVAILABLE

        return {
            "requestId": self.generate_request_id(),
            "unsuccessful": unsuccessful,
        }


    def create_vpc_endpoint_service_configuration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        acceptance_required = params.get("AcceptanceRequired")
        client_token = params.get("ClientToken")
        gateway_load_balancer_arns = []
        network_load_balancer_arns = []
        private_dns_name = params.get("PrivateDnsName")
        supported_ip_address_types = []
        supported_regions = []
        tag_specifications = []

        # Collect GatewayLoadBalancerArn.N
        for key in params:
            if key.startswith("GatewayLoadBalancerArn."):
                gateway_load_balancer_arns.append(params[key])
        # Collect NetworkLoadBalancerArn.N
        for key in params:
            if key.startswith("NetworkLoadBalancerArn."):
                network_load_balancer_arns.append(params[key])
        # Collect SupportedIpAddressType.N
        for key in params:
            if key.startswith("SupportedIpAddressType."):
                supported_ip_address_types.append(params[key])
        # Collect SupportedRegion.N
        for key in params:
            if key.startswith("SupportedRegion."):
                supported_regions.append(params[key])
        # Collect TagSpecification.N
        # TagSpecification.N.ResourceType and TagSpecification.N.Tags
        # Tags are nested, so we need to parse them carefully
        # We'll parse all TagSpecification.N.ResourceType and TagSpecification.N.Tags.M.Key/Value
        tag_specifications_dict = {}
        for key in params:
            if key.startswith("TagSpecification."):
                # key format: TagSpecification.N.ResourceType or TagSpecification.N.Tags.M.Key/Value
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                tag_spec_index = parts[1]
                if tag_spec_index not in tag_specifications_dict:
                    tag_specifications_dict[tag_spec_index] = {"ResourceType": None, "Tags": []}
                if parts[2] == "ResourceType":
                    tag_specifications_dict[tag_spec_index]["ResourceType"] = params[key]
                elif parts[2] == "Tags":
                    # parts[3] = M, parts[4] = Key or Value
                    if len(parts) < 5:
                        continue
                    tag_index = parts[3]
                    while len(tag_specifications_dict[tag_spec_index]["Tags"]) <= int(tag_index) - 1:
                        tag_specifications_dict[tag_spec_index]["Tags"].append(Tag(Key=None, Value=None))
                    tag_obj = tag_specifications_dict[tag_spec_index]["Tags"][int(tag_index) - 1]
                    if parts[4] == "Key":
                        tag_obj.Key = params[key]
                    elif parts[4] == "Value":
                        tag_obj.Value = params[key]
        # Convert to TagSpecification objects
        for ts in tag_specifications_dict.values():
            # Remove tags with None Key (incomplete)
            tags = [tag for tag in ts["Tags"] if tag.Key is not None]
            tag_specifications.append(TagSpecification(ResourceType=ts["ResourceType"], Tags=tags))

        # Validate that at least one load balancer ARN is provided
        if not gateway_load_balancer_arns and not network_load_balancer_arns:
            # According to AWS, must specify at least one load balancer ARN
            # Return error or empty response? Here we return empty with requestId
            return {
                "clientToken": client_token,
                "requestId": self.generate_request_id(),
                "serviceConfiguration": None,
            }

        # Generate service ID and name
        service_id = self.generate_unique_id(prefix="vpce-svc-")
        region = self.state.region if hasattr(self.state, "region") else "us-east-1"
        service_name = f"com.amazonaws.vpce.{region}.{service_id}"

        # Determine service type
        service_type_list = []
        if network_load_balancer_arns:
            service_type_list.append(ServiceTypeDetail(serviceType=ServiceTypeEnum.INTERFACE))
        if gateway_load_balancer_arns:
            service_type_list.append(ServiceTypeDetail(serviceType=ServiceTypeEnum.GATEWAY_LOAD_BALANCER))

        # Build supported region details
        supported_region_details = []
        for reg in supported_regions:
            supported_region_details.append(SupportedRegionDetail(region=reg, serviceState=ServiceState.AVAILABLE))

        # Compose service configuration object
        service_configuration = ServiceConfiguration(
            acceptanceRequired=acceptance_required if acceptance_required is not None else False,
            availabilityZoneIdSet=[],
            availabilityZoneSet=[],
            baseEndpointDnsNameSet=[f"{service_id}.{region}.vpce.amazonaws.com"],
            gatewayLoadBalancerArnSet=gateway_load_balancer_arns,
            managesVpcEndpoints=False,
            networkLoadBalancerArnSet=network_load_balancer_arns,
            payerResponsibility="ServiceOwner",
            privateDnsName=private_dns_name,
            privateDnsNameConfiguration=None,
            remoteAccessEnabled=False,
            serviceId=service_id,
            serviceName=service_name,
            serviceState=ServiceState.AVAILABLE,
            serviceType=service_type_list,
            supportedIpAddressTypeSet=supported_ip_address_types,
            supportedRegionSet=supported_region_details,
            tagSet=[tag for ts in tag_specifications for tag in ts.Tags] if tag_specifications else [],
        )

        # Store the service configuration in state
        self.state.vpc_endpoint_services[service_id] = service_configuration
        self.state.resources[service_id] = service_configuration

        return {
            "clientToken": client_token,
            "requestId": self.generate_request_id(),
            "serviceConfiguration": service_configuration.to_dict(),
        }


    def delete_vpc_endpoint_service_configurations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        service_ids = []
        for key in params:
            if key.startswith("ServiceId."):
                service_ids.append(params[key])
        unsuccessful = []

        if not service_ids:
            # No service IDs provided, return empty unsuccessful
            return {
                "requestId": self.generate_request_id(),
                "unsuccessful": unsuccessful,
            }

        for service_id in service_ids:
            service = self.state.vpc_endpoint_services.get(service_id)
            if not service:
                error = UnsuccessfulItemError(
                    code="InvalidServiceId",
                    message=f"The service ID '{service_id}' does not exist."
                )
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=error,
                        resourceId=service_id
                    )
                )
                continue

            # Check if there are any interface endpoint connections in Available or PendingAcceptance state attached to the service
            # We assume self.state.resources contains VPC endpoints and they have attributes service_id and state
            has_pending_or_available_connections = False
            for resource_id, resource in self.state.resources.items():
                # We only check VPC endpoints (assuming they have attribute 'service_id')
                if hasattr(resource, "service_id") and resource.service_id == service_id:
                    if resource.state in (ServiceState.PENDING, ServiceState.AVAILABLE):
                        has_pending_or_available_connections = True
                        break
            if has_pending_or_available_connections:
                error = UnsuccessfulItemError(
                    code="DependencyViolation",
                    message=f"Service '{service_id}' has available or pending acceptance endpoint connections."
                )
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=error,
                        resourceId=service_id
                    )
                )
                continue

            # Delete the service configuration
            self.state.vpc_endpoint_services.pop(service_id, None)
            self.state.resources.pop(service_id, None)

        return {
            "requestId": self.generate_request_id(),
            "unsuccessful": unsuccessful,
        }


    def describe_vpc_endpoint_service_configurations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = []
        for key in params:
            if key.startswith("Filter."):
                # Filter.N.Name and Filter.N.Values.M
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                filter_index = parts[1]
                if len(filters) < int(filter_index):
                    # Extend filters list
                    while len(filters) < int(filter_index):
                        filters.append(Filter(Name=None, Values=[]))
                filter_obj = filters[int(filter_index) - 1]
                if parts[2] == "Name":
                    filter_obj.Name = params[key]
                elif parts[2] == "Values":
                    # Values.M
                    if len(parts) < 4:
                        continue
                    value_index = int(parts[3])
                    while len(filter_obj.Values) < value_index:
                        filter_obj.Values.append("")
                    filter_obj.Values[value_index - 1] = params[key]

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results > 1000:
                    max_results = 1000
                elif max_results < 5:
                    max_results = 5
            except Exception:
                max_results = None
        next_token = params.get("NextToken")

        service_ids = []
        for key in params:
            if key.startswith("ServiceId."):
                service_ids.append(params[key])

        # Filter services
        services = list(self.state.vpc_endpoint_services.values())

        # Filter by service_ids if provided
        if service_ids:
            services = [s for s in services if s.serviceId in service_ids]

        # Apply filters
        def service_matches_filter(service: ServiceConfiguration, filter_obj: Filter) -> bool:
            if not filter_obj.Name or not filter_obj.Values:
                return True
            name = filter_obj.Name
            values = filter_obj.Values
            # Handle tag:<key> filter
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in service.tagSet:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False
            elif name == "tag-key":
                for tag in service.tagSet:
                    if tag.Key in values:
                        return True
                return False
            elif name == "service-name":
                return any(service.serviceName == v for v in values)
            elif name == "service-id":
                return any(service.serviceId == v for v in values)
            elif name == "service-state":
                return any(service.serviceState.value == v for v in values)
            elif name == "supported-ip-address-types":
                return any(ip_type in service.supportedIpAddressTypeSet for ip_type in values)
            else:
                # Unknown filter, ignore
                return True

        for filter_obj in filters:
            services = [s for s in services if service_matches_filter(s, filter_obj)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else None
        paged_services = services[start_index:end_index]

        new_next_token = str(end_index) if end_index and end_index < len(services) else None

        service_configuration_set = [s.to_dict() for s in paged_services]

        return {
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "serviceConfigurationSet": service_configuration_set,
        }


    def describe_vpc_endpoint_service_permissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        service_id = params.get("ServiceId")
        filters = []
        for key in params:
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                filter_index = parts[1]
                if len(filters) < int(filter_index):
                    while len(filters) < int(filter_index):
                        filters.append(Filter(Name=None, Values=[]))
                filter_obj = filters[int(filter_index) - 1]
                if parts[2] == "Name":
                    filter_obj.Name = params[key]
                elif parts[2] == "Values":
                    if len(parts) < 4:
                        continue
                    value_index = int(parts[3])
                    while len(filter_obj.Values) < value_index:
                        filter_obj.Values.append("")
                    filter_obj.Values[value_index - 1] = params[key]

        max_results = params.get("MaxResults")
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results > 1000:
                    max_results = 1000
                elif max_results < 5:
                    max_results = 5
            except Exception:
                max_results = None
        next_token = params.get("NextToken")

        if not service_id:
            # Missing required parameter
            return {
                "allowedPrincipals": [],
                "nextToken": None,
                "requestId": self.generate_request_id(),
            }

        # Get allowed principals for the service
        # Assuming self.state.vpc_endpoint_service_permissions is a dict keyed by service_id
        # Each value is a list of AllowedPrincipal objects
        allowed_principals_all = []
        if hasattr(self.state, "vpc_endpoint_service_permissions"):
            allowed_principals_all = self.state.vpc_endpoint_service_permissions.get(service_id, [])
        else:
            allowed_principals_all = []

        # Apply filters
        def principal_matches_filter(principal: AllowedPrincipal, filter_obj: Filter) -> bool:
            if not filter_obj.Name or not filter_obj.Values:
                return True
            name = filter_obj.Name
            values = filter_obj.Values
            if name == "principal":
                return any(principal.principal == v for v in values)
            elif name == "principal-type":
                return any(principal.principalType.value == v for v in values if principal.principalType)
            else:
                return True

        for filter_obj in filters:
            allowed_principals_all = [p for p in allowed_principals_all if principal_matches_filter(p, filter_obj)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else None
        paged_principals = allowed_principals_all[start_index:end_index]

        new_next_token = str(end_index) if end_index and end_index < len(allowed_principals_all) else None

        allowed_principals_dicts = [p.to_dict() for p in paged_principals]

        return {
            "allowedPrincipals": allowed_principals_dicts,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def describe_vpc_endpoint_services(self, params: dict) -> dict:
        # Validate DryRun param if present (not implemented here, just placeholder)
        # Filters supported:
        # owner, service-name, service-region, service-type, supported-ip-address-types,
        # tag:<key>, tag-key
        filters = params.get("Filter", [])
        if not isinstance(filters, list):
            filters = [filters]
        service_names = params.get("ServiceName", [])
        if not isinstance(service_names, list):
            service_names = [service_names]
        service_regions = params.get("ServiceRegion", [])
        if not isinstance(service_regions, list):
            service_regions = [service_regions]
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect all services from state
        all_services = list(self.state.vpc_endpoint_services.values())

        # Apply filters
        def service_matches_filter(service, filter_obj):
            name = filter_obj.Name
            values = filter_obj.Values
            if name is None or not values:
                return True
            # Handle tag:<key> and tag-key filters
            if name.startswith("tag:"):
                tag_key = name[4:]
                # Match if any tag with key=tag_key and value in values
                for tag in service.tagSet:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False
            if name == "tag-key":
                # Match if any tag key in values
                for tag in service.tagSet:
                    if tag.Key in values:
                        return True
                return False
            # Other filters
            if name == "owner":
                return service.owner in values
            if name == "service-name":
                return service.serviceName in values
            if name == "service-region":
                return service.serviceRegion in values
            if name == "service-type":
                # service.serviceType is list of ServiceTypeDetail
                service_type_values = [std.serviceType.value if std.serviceType else None for std in service.serviceType]
                for v in values:
                    if v in service_type_values:
                        return True
                return False
            if name == "supported-ip-address-types":
                for v in values:
                    if v in service.supportedIpAddressTypeSet:
                        return True
                return False
            # Unknown filter, ignore
            return True

        # Filter services by filters
        filtered_services = []
        for svc in all_services:
            if filters:
                if not all(service_matches_filter(svc, f) for f in filters):
                    continue
            if service_names and svc.serviceName not in service_names:
                continue
            if service_regions and svc.serviceRegion not in service_regions:
                continue
            filtered_services.append(svc)

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0
        if max_results is None:
            max_results = 1000
        else:
            max_results = min(int(max_results), 1000)
        end_index = start_index + max_results
        page_services = filtered_services[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered_services) else ""

        # Prepare response
        service_detail_set = [svc.to_dict() for svc in page_services]
        service_name_set = list({svc.serviceName for svc in filtered_services})

        return {
            "requestId": self.generate_request_id(),
            "serviceDetailSet": service_detail_set,
            "serviceNameSet": service_name_set,
            "nextToken": new_next_token,
        }


    def modify_vpc_endpoint_service_configuration(self, params: dict) -> dict:
        service_id = params.get("ServiceId")
        if not service_id:
            raise Exception("ServiceId is required")

        service = self.state.vpc_endpoint_services.get(service_id)
        if not service:
            raise Exception(f"Service {service_id} not found")

        # AcceptanceRequired
        if "AcceptanceRequired" in params:
            acceptance_required = params.get("AcceptanceRequired")
            if acceptance_required is not None:
                service.acceptanceRequired = bool(acceptance_required)

        # AddGatewayLoadBalancerArn.N
        add_gwlb_arns = []
        for key, value in params.items():
            if key.startswith("AddGatewayLoadBalancerArn."):
                add_gwlb_arns.append(value)
        for arn in add_gwlb_arns:
            if arn not in service.gatewayLoadBalancerArnSet:
                service.gatewayLoadBalancerArnSet.append(arn)

        # AddNetworkLoadBalancerArn.N
        add_nlb_arns = []
        for key, value in params.items():
            if key.startswith("AddNetworkLoadBalancerArn."):
                add_nlb_arns.append(value)
        for arn in add_nlb_arns:
            if arn not in service.networkLoadBalancerArnSet:
                service.networkLoadBalancerArnSet.append(arn)

        # AddSupportedIpAddressType.N
        add_ip_types = []
        for key, value in params.items():
            if key.startswith("AddSupportedIpAddressType."):
                add_ip_types.append(value)
        for ip_type in add_ip_types:
            if ip_type not in service.supportedIpAddressTypeSet:
                service.supportedIpAddressTypeSet.append(ip_type)

        # AddSupportedRegion.N
        add_regions = []
        for key, value in params.items():
            if key.startswith("AddSupportedRegion."):
                add_regions.append(value)
        for region in add_regions:
            # Check if region already in supportedRegionSet by region name
            if not any(r.region == region for r in service.supportedRegionSet):
                new_region_detail = SupportedRegionDetail(region=region, serviceState=service.serviceState)
                service.supportedRegionSet.append(new_region_detail)

        # RemoveGatewayLoadBalancerArn.N
        remove_gwlb_arns = []
        for key, value in params.items():
            if key.startswith("RemoveGatewayLoadBalancerArn."):
                remove_gwlb_arns.append(value)
        service.gatewayLoadBalancerArnSet = [arn for arn in service.gatewayLoadBalancerArnSet if arn not in remove_gwlb_arns]

        # RemoveNetworkLoadBalancerArn.N
        remove_nlb_arns = []
        for key, value in params.items():
            if key.startswith("RemoveNetworkLoadBalancerArn."):
                remove_nlb_arns.append(value)
        service.networkLoadBalancerArnSet = [arn for arn in service.networkLoadBalancerArnSet if arn not in remove_nlb_arns]

        # RemoveSupportedIpAddressType.N
        remove_ip_types = []
        for key, value in params.items():
            if key.startswith("RemoveSupportedIpAddressType."):
                remove_ip_types.append(value)
        service.supportedIpAddressTypeSet = [ip for ip in service.supportedIpAddressTypeSet if ip not in remove_ip_types]

        # RemoveSupportedRegion.N
        remove_regions = []
        for key, value in params.items():
            if key.startswith("RemoveSupportedRegion."):
                remove_regions.append(value)
        service.supportedRegionSet = [r for r in service.supportedRegionSet if r.region not in remove_regions]

        # PrivateDnsName
        if "PrivateDnsName" in params:
            private_dns_name = params.get("PrivateDnsName")
            if private_dns_name:
                service.privateDnsName = private_dns_name
                # Update privateDnsNameConfiguration and privateDnsNameVerificationState accordingly
                service.privateDnsNameVerificationState = PrivateDnsNameVerificationState.VERIFIED
                service.privateDnsNameConfiguration = PrivateDnsNameConfiguration(
                    name=private_dns_name,
                    state=PrivateDnsNameVerificationState.VERIFIED,
                    type="TXT",
                    value=None,
                )
            else:
                # If empty string or None, remove private DNS name
                service.privateDnsName = None
                service.privateDnsNameVerificationState = None
                service.privateDnsNameConfiguration = None

        # RemovePrivateDnsName
        if params.get("RemovePrivateDnsName"):
            service.privateDnsName = None
            service.privateDnsNameVerificationState = None
            service.privateDnsNameConfiguration = None

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def modify_vpc_endpoint_service_payer_responsibility(self, params: dict) -> dict:
        service_id = params.get("ServiceId")
        payer_responsibility = params.get("PayerResponsibility")
        if not service_id:
            raise Exception("ServiceId is required")
        if not payer_responsibility:
            raise Exception("PayerResponsibility is required")

        service = self.state.vpc_endpoint_services.get(service_id)
        if not service:
            raise Exception(f"Service {service_id} not found")

        # Only valid value is "ServiceOwner"
        if payer_responsibility != "ServiceOwner":
            raise Exception("Invalid PayerResponsibility value")

        # Once set to ServiceOwner, cannot revert to endpoint owner
        if service.payerResponsibility == "ServiceOwner" and payer_responsibility != "ServiceOwner":
            raise Exception("Cannot revert PayerResponsibility from ServiceOwner to endpoint owner")

        service.payerResponsibility = payer_responsibility

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def modify_vpc_endpoint_service_permissions(self, params: dict) -> dict:
        service_id = params.get("ServiceId")
        if not service_id:
            raise Exception("ServiceId is required")

        service = self.state.vpc_endpoint_services.get(service_id)
        if not service:
            raise Exception(f"Service {service_id} not found")

        add_allowed_principals = []
        remove_allowed_principals = []

        for key, value in params.items():
            if key.startswith("AddAllowedPrincipals."):
                add_allowed_principals.append(value)
            elif key.startswith("RemoveAllowedPrincipals."):
                remove_allowed_principals.append(value)

        # service.allowedPrincipals is not defined in the given classes, so we assume it exists as a list of AllowedPrincipal
        if not hasattr(service, "allowedPrincipals"):
            service.allowedPrincipals = []

        # Remove principals
        service.allowedPrincipals = [p for p in service.allowedPrincipals if p.principal not in remove_allowed_principals]

        # Add principals
        added_principal_set = []
        for principal_arn in add_allowed_principals:
            # Check if already present
            if any(p.principal == principal_arn for p in service.allowedPrincipals):
                continue
            # Create AllowedPrincipal object
            new_principal = AllowedPrincipal(
                principal=principal_arn,
                principalType=None,
                serviceId=service_id,
                servicePermissionId=self.generate_unique_id(),
                tagSet=[],
            )
            service.allowedPrincipals.append(new_principal)
            added_principal_set.append(new_principal.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "return": True,
            "addedPrincipalSet": added_principal_set,
        }


    def reject_vpc_endpoint_connections(self, params: dict) -> dict:
        service_id = params.get("ServiceId")
        vpc_endpoint_ids = []
        for key, value in params.items():
            if key.startswith("VpcEndpointId."):
                vpc_endpoint_ids.append(value)

        if not service_id:
            raise Exception("ServiceId is required")
        if not vpc_endpoint_ids:
            raise Exception("VpcEndpointId.N is required")

        service = self.state.vpc_endpoint_services.get(service_id)
        if not service:
            raise Exception(f"Service {service_id} not found")

        unsuccessful = []

        # We assume service has a dict or list of connection requests keyed by vpc_endpoint_id
        # For this emulation, we assume service has attribute 'pendingConnections' dict: vpc_endpoint_id -> state
        if not hasattr(service, "pendingConnections"):
            service.pendingConnections = {}

        for vpc_endpoint_id in vpc_endpoint_ids:
            if vpc_endpoint_id not in service.pendingConnections:
                # Not found or already processed
                unsuccessful.append(
                    UnsuccessfulItem(
                        error=UnsuccessfulItemError(
                            code="InvalidVpcEndpointId.NotFound",
                            message=f"VpcEndpointId {vpc_endpoint_id} not found or not pending",
                        ),
                        resourceId=vpc_endpoint_id,
                    ).to_dict()
                )
                continue
            # Reject the connection request
            # Remove from pendingConnections
            del service.pendingConnections[vpc_endpoint_id]

        return {
            "requestId": self.generate_request_id(),
            "unsuccessful": unsuccessful,
        }

    def start_vpc_endpoint_service_private_dns_verification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        service_id = params.get("ServiceId")
        dry_run = params.get("DryRun", False)

        if service_id is None:
            raise ValueError("ServiceId is required")

        # DryRun check
        if dry_run:
            # Here we simulate permission check; assume always allowed in this emulator
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation"
            }

        service = self.state.vpc_endpoint_services.get(service_id)
        if service is None:
            raise ValueError(f"Service with id {service_id} does not exist")

        # The verification process: 
        # According to AWS docs, the service provider must add a DNS record before calling this.
        # Here we simulate that the verification is started by setting the privateDnsNameConfiguration.state to PENDING or IN_PROGRESS.
        # We assume the privateDnsNameConfiguration exists.
        if service.service_configuration is None:
            raise ValueError(f"Service {service_id} has no service_configuration")

        pdns_config = service.service_configuration.privateDnsNameConfiguration
        if pdns_config is None:
            raise ValueError(f"Service {service_id} has no privateDnsNameConfiguration")

        # Set the state to PENDING verification
        from enum import Enum
        # We assume PrivateDnsNameVerificationState enum has a member PENDING or PENDING_VERIFICATION
        # Since we don't have the exact enum members, we try PENDING
        try:
            pdns_config.state = PrivateDnsNameVerificationState.PENDING
        except Exception:
            # fallback to string if enum member not found
            pdns_config.state = "pending"

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class VPCendpointservicesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptVpcEndpointConnections", self.accept_vpc_endpoint_connections)
        self.register_action("CreateVpcEndpointServiceConfiguration", self.create_vpc_endpoint_service_configuration)
        self.register_action("DeleteVpcEndpointServiceConfigurations", self.delete_vpc_endpoint_service_configurations)
        self.register_action("DescribeVpcEndpointServiceConfigurations", self.describe_vpc_endpoint_service_configurations)
        self.register_action("DescribeVpcEndpointServicePermissions", self.describe_vpc_endpoint_service_permissions)
        self.register_action("DescribeVpcEndpointServices", self.describe_vpc_endpoint_services)
        self.register_action("ModifyVpcEndpointServiceConfiguration", self.modify_vpc_endpoint_service_configuration)
        self.register_action("ModifyVpcEndpointServicePayerResponsibility", self.modify_vpc_endpoint_service_payer_responsibility)
        self.register_action("ModifyVpcEndpointServicePermissions", self.modify_vpc_endpoint_service_permissions)
        self.register_action("RejectVpcEndpointConnections", self.reject_vpc_endpoint_connections)
        self.register_action("StartVpcEndpointServicePrivateDnsVerification", self.start_vpc_endpoint_service_private_dns_verification)

    def accept_vpc_endpoint_connections(self, params):
        return self.backend.accept_vpc_endpoint_connections(params)

    def create_vpc_endpoint_service_configuration(self, params):
        return self.backend.create_vpc_endpoint_service_configuration(params)

    def delete_vpc_endpoint_service_configurations(self, params):
        return self.backend.delete_vpc_endpoint_service_configurations(params)

    def describe_vpc_endpoint_service_configurations(self, params):
        return self.backend.describe_vpc_endpoint_service_configurations(params)

    def describe_vpc_endpoint_service_permissions(self, params):
        return self.backend.describe_vpc_endpoint_service_permissions(params)

    def describe_vpc_endpoint_services(self, params):
        return self.backend.describe_vpc_endpoint_services(params)

    def modify_vpc_endpoint_service_configuration(self, params):
        return self.backend.modify_vpc_endpoint_service_configuration(params)

    def modify_vpc_endpoint_service_payer_responsibility(self, params):
        return self.backend.modify_vpc_endpoint_service_payer_responsibility(params)

    def modify_vpc_endpoint_service_permissions(self, params):
        return self.backend.modify_vpc_endpoint_service_permissions(params)

    def reject_vpc_endpoint_connections(self, params):
        return self.backend.reject_vpc_endpoint_connections(params)

    def start_vpc_endpoint_service_private_dns_verification(self, params):
        return self.backend.start_vpc_endpoint_service_private_dns_verification(params)
