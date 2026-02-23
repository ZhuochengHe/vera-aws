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
class VpcEndpointService:
    acceptance_required: bool = False
    availability_zone_id_set: List[Any] = field(default_factory=list)
    availability_zone_set: List[Any] = field(default_factory=list)
    base_endpoint_dns_name_set: List[Any] = field(default_factory=list)
    manages_vpc_endpoints: bool = False
    owner: str = ""
    payer_responsibility: str = ""
    private_dns_name: str = ""
    private_dns_name_set: List[Any] = field(default_factory=list)
    private_dns_name_verification_state: str = ""
    service_id: str = ""
    service_name: str = ""
    service_region: str = ""
    service_type: List[Any] = field(default_factory=list)
    supported_ip_address_type_set: List[Any] = field(default_factory=list)
    tag_set: List[Any] = field(default_factory=list)
    vpc_endpoint_policy_supported: bool = False

    gateway_load_balancer_arn_set: List[Any] = field(default_factory=list)
    network_load_balancer_arn_set: List[Any] = field(default_factory=list)
    supported_region_set: List[Any] = field(default_factory=list)
    service_state: str = ""
    remote_access_enabled: bool = False
    private_dns_name_configuration: Dict[str, Any] = field(default_factory=dict)
    allowed_principals: List[Dict[str, Any]] = field(default_factory=list)
    connection_states: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "acceptanceRequired": self.acceptance_required,
            "availabilityZoneIdSet": self.availability_zone_id_set,
            "availabilityZoneSet": self.availability_zone_set,
            "baseEndpointDnsNameSet": self.base_endpoint_dns_name_set,
            "managesVpcEndpoints": self.manages_vpc_endpoints,
            "owner": self.owner,
            "payerResponsibility": self.payer_responsibility,
            "privateDnsName": self.private_dns_name,
            "privateDnsNameSet": self.private_dns_name_set,
            "privateDnsNameVerificationState": self.private_dns_name_verification_state,
            "serviceId": self.service_id,
            "serviceName": self.service_name,
            "serviceRegion": self.service_region,
            "serviceType": self.service_type,
            "supportedIpAddressTypeSet": self.supported_ip_address_type_set,
            "tagSet": self.tag_set,
            "vpcEndpointPolicySupported": self.vpc_endpoint_policy_supported,
            "gatewayLoadBalancerArnSet": self.gateway_load_balancer_arn_set,
            "networkLoadBalancerArnSet": self.network_load_balancer_arn_set,
            "supportedRegionSet": self.supported_region_set,
            "serviceState": self.service_state,
            "remoteAccessEnabled": self.remote_access_enabled,
            "privateDnsNameConfiguration": self.private_dns_name_configuration,
        }

class VpcEndpointService_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.vpc_endpoint_services  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            value = params.get(key)
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                return create_error_response("MissingParameter", f"The request must contain the parameter {key}")
        return None

    def _get_service_or_error(self, service_id: str) -> (Optional[VpcEndpointService], Optional[Dict[str, Any]]):
        service = self.resources.get(service_id)
        if not service:
            return None, create_error_response(
                "InvalidVpcEndpointServiceId.NotFound",
                f"The VpcEndpointService '{service_id}' does not exist."
            )
        return service, None

    def _build_private_dns_name_configuration(self, service: VpcEndpointService) -> Dict[str, Any]:
        if not service.private_dns_name:
            return {}
        config = service.private_dns_name_configuration or {}
        return {
            "name": config.get("name") or service.private_dns_name,
            "state": config.get("state") or service.private_dns_name_verification_state or "unverified",
            "type": config.get("type") or "TXT",
            "value": config.get("value") or "",
        }

    def _serialize_service_configuration(self, service: VpcEndpointService) -> Dict[str, Any]:
        return {
            "acceptanceRequired": service.acceptance_required,
            "availabilityZoneIdSet": service.availability_zone_id_set,
            "availabilityZoneSet": service.availability_zone_set,
            "baseEndpointDnsNameSet": service.base_endpoint_dns_name_set,
            "gatewayLoadBalancerArnSet": service.gateway_load_balancer_arn_set,
            "managesVpcEndpoints": service.manages_vpc_endpoints,
            "networkLoadBalancerArnSet": service.network_load_balancer_arn_set,
            "payerResponsibility": service.payer_responsibility,
            "privateDnsName": service.private_dns_name,
            "privateDnsNameConfiguration": self._build_private_dns_name_configuration(service),
            "remoteAccessEnabled": service.remote_access_enabled,
            "serviceId": service.service_id,
            "serviceName": service.service_name,
            "serviceState": service.service_state,
            "serviceType": service.service_type,
            "supportedIpAddressTypeSet": service.supported_ip_address_type_set,
            "supportedRegionSet": service.supported_region_set,
            "tagSet": service.tag_set,
        }

    def AcceptVpcEndpointConnections(self, params: Dict[str, Any]):
        """Accepts connection requests to your VPC endpoint service."""

        error = self._require_params(params, ["ServiceId", "VpcEndpointId.N"])
        if error:
            return error

        service_id = params.get("ServiceId")
        service, error = self._get_service_or_error(service_id)
        if error:
            return error

        endpoint_ids = params.get("VpcEndpointId.N", [])
        unsuccessful = []

        for endpoint_id in endpoint_ids:
            endpoint = self.state.vpc_endpoints.get(endpoint_id)
            if not endpoint:
                unsuccessful.append({
                    "error": {
                        "code": "InvalidVpcEndpointId.NotFound",
                        "message": f"The VpcEndpoint '{endpoint_id}' does not exist.",
                    },
                    "resourceId": endpoint_id,
                })
                continue

            service.connection_states[endpoint_id] = "available"
            endpoint.state = "available"

        return {
            'unsuccessful': unsuccessful,
            }

    def CreateVpcEndpointServiceConfiguration(self, params: Dict[str, Any]):
        """Creates a VPC endpoint service to which service consumers (AWS accounts,
            users, and IAM roles) can connect. Before you create an endpoint service, you must create one of the following for your service: ANetwork Load Balancer. 
                    Service consumers connect to your service"""

        error = self._require_params(params, [])
        if error:
            return error

        gateway_lb_arns = params.get("GatewayLoadBalancerArn.N", [])
        network_lb_arns = params.get("NetworkLoadBalancerArn.N", [])
        supported_ip_types = params.get("SupportedIpAddressType.N", [])
        supported_regions = params.get("SupportedRegion.N", [])
        private_dns_name = params.get("PrivateDnsName") or ""
        acceptance_required = str2bool(params.get("AcceptanceRequired"))
        client_token = params.get("ClientToken") or ""

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []):
            tag_set.extend(spec.get("Tags", []) or [])

        service_id = self._generate_id("vpce-svc")
        service_region = supported_regions[0] if supported_regions else "us-east-1"
        service_name = f"com.amazonaws.vpce.{service_region}.{service_id}"
        service_type_value = "Gateway" if gateway_lb_arns else "Interface"

        service = VpcEndpointService(
            acceptance_required=acceptance_required,
            availability_zone_id_set=[],
            availability_zone_set=[],
            base_endpoint_dns_name_set=[],
            manages_vpc_endpoints=False,
            owner="",
            payer_responsibility="ServiceOwner",
            private_dns_name=private_dns_name,
            private_dns_name_set=[{"privateDnsName": private_dns_name}] if private_dns_name else [],
            private_dns_name_verification_state="unverified" if private_dns_name else "",
            service_id=service_id,
            service_name=service_name,
            service_region=service_region,
            service_type=[{"serviceType": service_type_value}],
            supported_ip_address_type_set=[{"supportedIpAddressType": ip_type} for ip_type in supported_ip_types],
            tag_set=tag_set,
            vpc_endpoint_policy_supported=False,
            gateway_load_balancer_arn_set=list(gateway_lb_arns),
            network_load_balancer_arn_set=list(network_lb_arns),
            supported_region_set=[{"region": region, "serviceState": "Available"} for region in supported_regions],
            service_state="Available",
            remote_access_enabled=False,
            private_dns_name_configuration={
                "name": private_dns_name,
                "state": "unverified" if private_dns_name else "",
                "type": "TXT",
                "value": "",
            } if private_dns_name else {},
        )
        service.tags = tag_set
        self.resources[service_id] = service

        return {
            'clientToken': client_token,
            'serviceConfiguration': self._serialize_service_configuration(service),
            }

    def DeleteVpcEndpointServiceConfigurations(self, params: Dict[str, Any]):
        """Deletes the specified VPC endpoint service configurations. Before you can delete
            an endpoint service configuration, you must reject anyAvailableorPendingAcceptanceinterface endpoint connections that are attached to
            the service."""

        error = self._require_params(params, ["ServiceId.N"])
        if error:
            return error

        service_ids = params.get("ServiceId.N", [])
        unsuccessful = []

        for service_id in service_ids:
            service = self.resources.get(service_id)
            if not service:
                unsuccessful.append({
                    "error": {
                        "code": "InvalidVpcEndpointServiceId.NotFound",
                        "message": f"The VpcEndpointService '{service_id}' does not exist.",
                    },
                    "resourceId": service_id,
                })
                continue

            if service.connection_states:
                unsuccessful.append({
                    "error": {
                        "code": "DependencyViolation",
                        "message": f"The VpcEndpointService '{service_id}' has existing endpoint connections.",
                    },
                    "resourceId": service_id,
                })
                continue

            del self.resources[service_id]

        return {
            'unsuccessful': unsuccessful,
            }

    def DescribeVpcEndpointServiceConfigurations(self, params: Dict[str, Any]):
        """Describes the VPC endpoint service configurations in your account (your services)."""

        error = self._require_params(params, [])
        if error:
            return error

        service_ids = params.get("ServiceId.N", [])
        if service_ids:
            for service_id in service_ids:
                if service_id not in self.resources:
                    return create_error_response(
                        "InvalidVpcEndpointServiceId.NotFound",
                        f"The VpcEndpointService '{service_id}' does not exist."
                    )
            services = [self.resources[service_id] for service_id in service_ids]
        else:
            services = list(self.resources.values())

        services = apply_filters(services, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or 100)
        service_configuration_set = [
            self._serialize_service_configuration(service)
            for service in services[:max_results]
        ]

        return {
            'nextToken': None,
            'serviceConfigurationSet': service_configuration_set,
            }

    def DescribeVpcEndpointServicePermissions(self, params: Dict[str, Any]):
        """Describes the principals (service consumers) that are permitted to discover your VPC
            endpoint service. Principal ARNs with path components aren't supported."""

        error = self._require_params(params, ["ServiceId"])
        if error:
            return error

        service_id = params.get("ServiceId")
        service, error = self._get_service_or_error(service_id)
        if error:
            return error

        allowed_principals = []
        for entry in service.allowed_principals:
            allowed_principals.append({
                "principal": entry.get("principal"),
                "principalType": entry.get("principalType") or "AWS",
                "serviceId": entry.get("serviceId") or service_id,
                "servicePermissionId": entry.get("servicePermissionId") or entry.get("id"),
                "tagSet": entry.get("tagSet", []),
            })

        allowed_principals = apply_filters(allowed_principals, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or 100)

        return {
            'allowedPrincipals': allowed_principals[:max_results],
            'nextToken': None,
            }

    def DescribeVpcEndpointServices(self, params: Dict[str, Any]):
        """Describes available services to which you can create a VPC endpoint. When the service provider and the consumer have different accounts in multiple
            Availability Zones, and the consumer views the VPC endpoint service information, the
            response only includes the common Availabil"""

        error = self._require_params(params, [])
        if error:
            return error

        service_names = params.get("ServiceName.N", [])
        service_regions = params.get("ServiceRegion.N", [])

        services = list(self.resources.values())
        if service_names:
            services = [service for service in services if service.service_name in service_names]
        if service_regions:
            services = [service for service in services if service.service_region in service_regions]

        services = apply_filters(services, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or 100)
        selected_services = services[:max_results]

        service_detail_set = [service.to_dict() for service in selected_services]
        service_name_set = [service.service_name for service in selected_services]

        return {
            'nextToken': None,
            'serviceDetailSet': service_detail_set,
            'serviceNameSet': service_name_set,
            }

    def ModifyVpcEndpointServiceConfiguration(self, params: Dict[str, Any]):
        """Modifies the attributes of the specified VPC endpoint service configuration. If you set or modify the private DNS name, you must prove that you own the private DNS
            domain name."""

        error = self._require_params(params, ["ServiceId"])
        if error:
            return error

        service_id = params.get("ServiceId")
        service, error = self._get_service_or_error(service_id)
        if error:
            return error

        acceptance_required = params.get("AcceptanceRequired")
        if acceptance_required is not None:
            service.acceptance_required = str2bool(acceptance_required)

        add_gateway_lb_arns = params.get("AddGatewayLoadBalancerArn.N", [])
        remove_gateway_lb_arns = params.get("RemoveGatewayLoadBalancerArn.N", [])
        if add_gateway_lb_arns or remove_gateway_lb_arns:
            current_gateway = list(service.gateway_load_balancer_arn_set)
            for arn in add_gateway_lb_arns:
                if arn not in current_gateway:
                    current_gateway.append(arn)
            for arn in remove_gateway_lb_arns:
                if arn in current_gateway:
                    current_gateway.remove(arn)
            service.gateway_load_balancer_arn_set = current_gateway

        add_network_lb_arns = params.get("AddNetworkLoadBalancerArn.N", [])
        remove_network_lb_arns = params.get("RemoveNetworkLoadBalancerArn.N", [])
        if add_network_lb_arns or remove_network_lb_arns:
            current_network = list(service.network_load_balancer_arn_set)
            for arn in add_network_lb_arns:
                if arn not in current_network:
                    current_network.append(arn)
            for arn in remove_network_lb_arns:
                if arn in current_network:
                    current_network.remove(arn)
            service.network_load_balancer_arn_set = current_network

        add_supported_ip_types = params.get("AddSupportedIpAddressType.N", [])
        remove_supported_ip_types = params.get("RemoveSupportedIpAddressType.N", [])
        if add_supported_ip_types or remove_supported_ip_types:
            current_ip_types = [
                entry.get("supportedIpAddressType")
                for entry in service.supported_ip_address_type_set
                if isinstance(entry, dict)
            ]
            for ip_type in add_supported_ip_types:
                if ip_type not in current_ip_types:
                    current_ip_types.append(ip_type)
            for ip_type in remove_supported_ip_types:
                if ip_type in current_ip_types:
                    current_ip_types.remove(ip_type)
            service.supported_ip_address_type_set = [
                {"supportedIpAddressType": ip_type}
                for ip_type in current_ip_types
            ]

        add_supported_regions = params.get("AddSupportedRegion.N", [])
        remove_supported_regions = params.get("RemoveSupportedRegion.N", [])
        if add_supported_regions or remove_supported_regions:
            current_regions = [
                entry.get("region")
                for entry in service.supported_region_set
                if isinstance(entry, dict)
            ]
            for region in add_supported_regions:
                if region not in current_regions:
                    current_regions.append(region)
            for region in remove_supported_regions:
                if region in current_regions:
                    current_regions.remove(region)
            service.supported_region_set = [
                {"region": region, "serviceState": "Available"}
                for region in current_regions
            ]
            if current_regions:
                service.service_region = current_regions[0]

        private_dns_name = params.get("PrivateDnsName")
        if private_dns_name:
            service.private_dns_name = private_dns_name
            service.private_dns_name_set = [{"privateDnsName": private_dns_name}]
            service.private_dns_name_verification_state = "unverified"
            service.private_dns_name_configuration = {
                "name": private_dns_name,
                "state": "unverified",
                "type": "TXT",
                "value": "",
            }

        remove_private_dns_name = str2bool(params.get("RemovePrivateDnsName"))
        if remove_private_dns_name:
            service.private_dns_name = ""
            service.private_dns_name_set = []
            service.private_dns_name_verification_state = ""
            service.private_dns_name_configuration = {}

        return {
            'return': True,
            }

    def ModifyVpcEndpointServicePayerResponsibility(self, params: Dict[str, Any]):
        """Modifies the payer responsibility for your VPC endpoint service."""

        error = self._require_params(params, ["PayerResponsibility", "ServiceId"])
        if error:
            return error

        service_id = params.get("ServiceId")
        service, error = self._get_service_or_error(service_id)
        if error:
            return error

        payer_responsibility = params.get("PayerResponsibility") or ""
        service.payer_responsibility = payer_responsibility

        return {
            'return': True,
            }

    def ModifyVpcEndpointServicePermissions(self, params: Dict[str, Any]):
        """Modifies the permissions for your VPC endpoint service. You can add or remove permissions
            for service consumers (AWS accounts, users, and IAM roles) to connect to
            your endpoint service. Principal ARNs with path components aren't supported. If you grant permissions to all prin"""

        error = self._require_params(params, ["ServiceId"])
        if error:
            return error

        service_id = params.get("ServiceId")
        service, error = self._get_service_or_error(service_id)
        if error:
            return error

        add_principals = params.get("AddAllowedPrincipals.N", [])
        remove_principals = params.get("RemoveAllowedPrincipals.N", [])

        existing = list(service.allowed_principals)
        existing_map = {entry.get("principal"): entry for entry in existing if entry.get("principal")}

        added_principal_set = []
        for principal in add_principals:
            if principal in existing_map:
                continue
            permission_id = self._generate_id("vpce-svc-perm")
            entry = {
                "principal": principal,
                "principalType": "AWS",
                "serviceId": service_id,
                "servicePermissionId": permission_id,
                "tagSet": [],
            }
            existing.append(entry)
            existing_map[principal] = entry
            added_principal_set.append({
                "principal": principal,
                "principalType": "AWS",
                "serviceId": service_id,
                "servicePermissionId": permission_id,
            })

        if remove_principals:
            existing = [entry for entry in existing if entry.get("principal") not in remove_principals]

        service.allowed_principals = existing

        return {
            'addedPrincipalSet': added_principal_set,
            'return': True,
            }

    def RejectVpcEndpointConnections(self, params: Dict[str, Any]):
        """Rejects VPC endpoint connection requests to your VPC endpoint service."""

        error = self._require_params(params, ["ServiceId", "VpcEndpointId.N"])
        if error:
            return error

        service_id = params.get("ServiceId")
        service, error = self._get_service_or_error(service_id)
        if error:
            return error

        endpoint_ids = params.get("VpcEndpointId.N", [])
        unsuccessful = []

        for endpoint_id in endpoint_ids:
            endpoint = self.state.vpc_endpoints.get(endpoint_id)
            if not endpoint:
                unsuccessful.append({
                    "error": {
                        "code": "InvalidVpcEndpointId.NotFound",
                        "message": f"The VpcEndpoint '{endpoint_id}' does not exist.",
                    },
                    "resourceId": endpoint_id,
                })
                continue

            service.connection_states[endpoint_id] = "rejected"
            endpoint.state = "rejected"

        return {
            'unsuccessful': unsuccessful,
            }

    def StartVpcEndpointServicePrivateDnsVerification(self, params: Dict[str, Any]):
        """Initiates the verification process to prove that the service provider owns the private
            DNS name domain for the endpoint service. The service provider must successfully perform the verification before the consumer can use the name to access the service. Before the service provider runs th"""

        error = self._require_params(params, ["ServiceId"])
        if error:
            return error

        service_id = params.get("ServiceId")
        service, error = self._get_service_or_error(service_id)
        if error:
            return error

        if not service.private_dns_name:
            return create_error_response(
                "InvalidParameterValue",
                "PrivateDnsName is not configured for this service."
            )

        service.private_dns_name_verification_state = "verified"
        service.private_dns_name_configuration = {
            "name": service.private_dns_name,
            "state": "verified",
            "type": "TXT",
            "value": "",
        }

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'service') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class vpcendpointservice_RequestParser:
    @staticmethod
    def parse_accept_vpc_endpoint_connections_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ServiceId": get_scalar(md, "ServiceId"),
            "VpcEndpointId.N": get_indexed_list(md, "VpcEndpointId"),
        }

    @staticmethod
    def parse_create_vpc_endpoint_service_configuration_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AcceptanceRequired": get_scalar(md, "AcceptanceRequired"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "GatewayLoadBalancerArn.N": get_indexed_list(md, "GatewayLoadBalancerArn"),
            "NetworkLoadBalancerArn.N": get_indexed_list(md, "NetworkLoadBalancerArn"),
            "PrivateDnsName": get_scalar(md, "PrivateDnsName"),
            "SupportedIpAddressType.N": get_indexed_list(md, "SupportedIpAddressType"),
            "SupportedRegion.N": get_indexed_list(md, "SupportedRegion"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_vpc_endpoint_service_configurations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ServiceId.N": get_indexed_list(md, "ServiceId"),
        }

    @staticmethod
    def parse_describe_vpc_endpoint_service_configurations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ServiceId.N": get_indexed_list(md, "ServiceId"),
        }

    @staticmethod
    def parse_describe_vpc_endpoint_service_permissions_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ServiceId": get_scalar(md, "ServiceId"),
        }

    @staticmethod
    def parse_describe_vpc_endpoint_services_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ServiceName.N": get_indexed_list(md, "ServiceName"),
            "ServiceRegion.N": get_indexed_list(md, "ServiceRegion"),
        }

    @staticmethod
    def parse_modify_vpc_endpoint_service_configuration_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AcceptanceRequired": get_scalar(md, "AcceptanceRequired"),
            "AddGatewayLoadBalancerArn.N": get_indexed_list(md, "AddGatewayLoadBalancerArn"),
            "AddNetworkLoadBalancerArn.N": get_indexed_list(md, "AddNetworkLoadBalancerArn"),
            "AddSupportedIpAddressType.N": get_indexed_list(md, "AddSupportedIpAddressType"),
            "AddSupportedRegion.N": get_indexed_list(md, "AddSupportedRegion"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PrivateDnsName": get_scalar(md, "PrivateDnsName"),
            "RemoveGatewayLoadBalancerArn.N": get_indexed_list(md, "RemoveGatewayLoadBalancerArn"),
            "RemoveNetworkLoadBalancerArn.N": get_indexed_list(md, "RemoveNetworkLoadBalancerArn"),
            "RemovePrivateDnsName": get_scalar(md, "RemovePrivateDnsName"),
            "RemoveSupportedIpAddressType.N": get_indexed_list(md, "RemoveSupportedIpAddressType"),
            "RemoveSupportedRegion.N": get_indexed_list(md, "RemoveSupportedRegion"),
            "ServiceId": get_scalar(md, "ServiceId"),
        }

    @staticmethod
    def parse_modify_vpc_endpoint_service_payer_responsibility_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PayerResponsibility": get_scalar(md, "PayerResponsibility"),
            "ServiceId": get_scalar(md, "ServiceId"),
        }

    @staticmethod
    def parse_modify_vpc_endpoint_service_permissions_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddAllowedPrincipals.N": get_indexed_list(md, "AddAllowedPrincipals"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "RemoveAllowedPrincipals.N": get_indexed_list(md, "RemoveAllowedPrincipals"),
            "ServiceId": get_scalar(md, "ServiceId"),
        }

    @staticmethod
    def parse_reject_vpc_endpoint_connections_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ServiceId": get_scalar(md, "ServiceId"),
            "VpcEndpointId.N": get_indexed_list(md, "VpcEndpointId"),
        }

    @staticmethod
    def parse_start_vpc_endpoint_service_private_dns_verification_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ServiceId": get_scalar(md, "ServiceId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AcceptVpcEndpointConnections": vpcendpointservice_RequestParser.parse_accept_vpc_endpoint_connections_request,
            "CreateVpcEndpointServiceConfiguration": vpcendpointservice_RequestParser.parse_create_vpc_endpoint_service_configuration_request,
            "DeleteVpcEndpointServiceConfigurations": vpcendpointservice_RequestParser.parse_delete_vpc_endpoint_service_configurations_request,
            "DescribeVpcEndpointServiceConfigurations": vpcendpointservice_RequestParser.parse_describe_vpc_endpoint_service_configurations_request,
            "DescribeVpcEndpointServicePermissions": vpcendpointservice_RequestParser.parse_describe_vpc_endpoint_service_permissions_request,
            "DescribeVpcEndpointServices": vpcendpointservice_RequestParser.parse_describe_vpc_endpoint_services_request,
            "ModifyVpcEndpointServiceConfiguration": vpcendpointservice_RequestParser.parse_modify_vpc_endpoint_service_configuration_request,
            "ModifyVpcEndpointServicePayerResponsibility": vpcendpointservice_RequestParser.parse_modify_vpc_endpoint_service_payer_responsibility_request,
            "ModifyVpcEndpointServicePermissions": vpcendpointservice_RequestParser.parse_modify_vpc_endpoint_service_permissions_request,
            "RejectVpcEndpointConnections": vpcendpointservice_RequestParser.parse_reject_vpc_endpoint_connections_request,
            "StartVpcEndpointServicePrivateDnsVerification": vpcendpointservice_RequestParser.parse_start_vpc_endpoint_service_private_dns_verification_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class vpcendpointservice_ResponseSerializer:
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
                xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_accept_vpc_endpoint_connections_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AcceptVpcEndpointConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</AcceptVpcEndpointConnectionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_vpc_endpoint_service_configuration_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpcEndpointServiceConfigurationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize serviceConfiguration
        _serviceConfiguration_key = None
        if "serviceConfiguration" in data:
            _serviceConfiguration_key = "serviceConfiguration"
        elif "ServiceConfiguration" in data:
            _serviceConfiguration_key = "ServiceConfiguration"
        if _serviceConfiguration_key:
            param_data = data[_serviceConfiguration_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<serviceConfiguration>')
            xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</serviceConfiguration>')
        xml_parts.append(f'</CreateVpcEndpointServiceConfigurationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpc_endpoint_service_configurations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpcEndpointServiceConfigurationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</DeleteVpcEndpointServiceConfigurationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_endpoint_service_configurations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcEndpointServiceConfigurationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize serviceConfigurationSet
        _serviceConfigurationSet_key = None
        if "serviceConfigurationSet" in data:
            _serviceConfigurationSet_key = "serviceConfigurationSet"
        elif "ServiceConfigurationSet" in data:
            _serviceConfigurationSet_key = "ServiceConfigurationSet"
        elif "ServiceConfigurations" in data:
            _serviceConfigurationSet_key = "ServiceConfigurations"
        if _serviceConfigurationSet_key:
            param_data = data[_serviceConfigurationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<serviceConfigurationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</serviceConfigurationSet>')
            else:
                xml_parts.append(f'{indent_str}<serviceConfigurationSet/>')
        xml_parts.append(f'</DescribeVpcEndpointServiceConfigurationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_endpoint_service_permissions_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcEndpointServicePermissionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize allowedPrincipals
        _allowedPrincipals_key = None
        if "allowedPrincipals" in data:
            _allowedPrincipals_key = "allowedPrincipals"
        elif "AllowedPrincipals" in data:
            _allowedPrincipals_key = "AllowedPrincipals"
        if _allowedPrincipals_key:
            param_data = data[_allowedPrincipals_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<allowedPrincipalsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</allowedPrincipalsSet>')
            else:
                xml_parts.append(f'{indent_str}<allowedPrincipalsSet/>')
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
        xml_parts.append(f'</DescribeVpcEndpointServicePermissionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_endpoint_services_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcEndpointServicesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize serviceDetailSet
        _serviceDetailSet_key = None
        if "serviceDetailSet" in data:
            _serviceDetailSet_key = "serviceDetailSet"
        elif "ServiceDetailSet" in data:
            _serviceDetailSet_key = "ServiceDetailSet"
        elif "ServiceDetails" in data:
            _serviceDetailSet_key = "ServiceDetails"
        if _serviceDetailSet_key:
            param_data = data[_serviceDetailSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<serviceDetailSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</serviceDetailSet>')
            else:
                xml_parts.append(f'{indent_str}<serviceDetailSet/>')
        # Serialize serviceNameSet
        _serviceNameSet_key = None
        if "serviceNameSet" in data:
            _serviceNameSet_key = "serviceNameSet"
        elif "ServiceNameSet" in data:
            _serviceNameSet_key = "ServiceNameSet"
        elif "ServiceNames" in data:
            _serviceNameSet_key = "ServiceNames"
        if _serviceNameSet_key:
            param_data = data[_serviceNameSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<serviceNameSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</serviceNameSet>')
            else:
                xml_parts.append(f'{indent_str}<serviceNameSet/>')
        xml_parts.append(f'</DescribeVpcEndpointServicesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpc_endpoint_service_configuration_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpcEndpointServiceConfigurationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyVpcEndpointServiceConfigurationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpc_endpoint_service_payer_responsibility_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpcEndpointServicePayerResponsibilityResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyVpcEndpointServicePayerResponsibilityResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpc_endpoint_service_permissions_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpcEndpointServicePermissionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize addedPrincipalSet
        _addedPrincipalSet_key = None
        if "addedPrincipalSet" in data:
            _addedPrincipalSet_key = "addedPrincipalSet"
        elif "AddedPrincipalSet" in data:
            _addedPrincipalSet_key = "AddedPrincipalSet"
        elif "AddedPrincipals" in data:
            _addedPrincipalSet_key = "AddedPrincipals"
        if _addedPrincipalSet_key:
            param_data = data[_addedPrincipalSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<addedPrincipalSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</addedPrincipalSet>')
            else:
                xml_parts.append(f'{indent_str}<addedPrincipalSet/>')
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
        xml_parts.append(f'</ModifyVpcEndpointServicePermissionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reject_vpc_endpoint_connections_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RejectVpcEndpointConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpointservice_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</RejectVpcEndpointConnectionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_start_vpc_endpoint_service_private_dns_verification_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<StartVpcEndpointServicePrivateDnsVerificationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</StartVpcEndpointServicePrivateDnsVerificationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AcceptVpcEndpointConnections": vpcendpointservice_ResponseSerializer.serialize_accept_vpc_endpoint_connections_response,
            "CreateVpcEndpointServiceConfiguration": vpcendpointservice_ResponseSerializer.serialize_create_vpc_endpoint_service_configuration_response,
            "DeleteVpcEndpointServiceConfigurations": vpcendpointservice_ResponseSerializer.serialize_delete_vpc_endpoint_service_configurations_response,
            "DescribeVpcEndpointServiceConfigurations": vpcendpointservice_ResponseSerializer.serialize_describe_vpc_endpoint_service_configurations_response,
            "DescribeVpcEndpointServicePermissions": vpcendpointservice_ResponseSerializer.serialize_describe_vpc_endpoint_service_permissions_response,
            "DescribeVpcEndpointServices": vpcendpointservice_ResponseSerializer.serialize_describe_vpc_endpoint_services_response,
            "ModifyVpcEndpointServiceConfiguration": vpcendpointservice_ResponseSerializer.serialize_modify_vpc_endpoint_service_configuration_response,
            "ModifyVpcEndpointServicePayerResponsibility": vpcendpointservice_ResponseSerializer.serialize_modify_vpc_endpoint_service_payer_responsibility_response,
            "ModifyVpcEndpointServicePermissions": vpcendpointservice_ResponseSerializer.serialize_modify_vpc_endpoint_service_permissions_response,
            "RejectVpcEndpointConnections": vpcendpointservice_ResponseSerializer.serialize_reject_vpc_endpoint_connections_response,
            "StartVpcEndpointServicePrivateDnsVerification": vpcendpointservice_ResponseSerializer.serialize_start_vpc_endpoint_service_private_dns_verification_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

