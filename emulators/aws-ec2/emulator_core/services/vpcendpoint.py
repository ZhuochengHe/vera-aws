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
class VpcEndpoint:
    creation_timestamp: str = ""
    dns_entry_set: List[Any] = field(default_factory=list)
    dns_options: Dict[str, Any] = field(default_factory=dict)
    failure_reason: str = ""
    group_set: List[Any] = field(default_factory=list)
    ip_address_type: str = ""
    ipv4_prefix_set: List[Any] = field(default_factory=list)
    ipv6_prefix_set: List[Any] = field(default_factory=list)
    last_error: Dict[str, Any] = field(default_factory=dict)
    network_interface_id_set: List[Any] = field(default_factory=list)
    owner_id: str = ""
    policy_document: str = ""
    private_dns_enabled: bool = False
    requester_managed: bool = False
    resource_configuration_arn: str = ""
    route_table_id_set: List[Any] = field(default_factory=list)
    service_name: str = ""
    service_network_arn: str = ""
    service_region: str = ""
    state: str = ""
    subnet_id_set: List[Any] = field(default_factory=list)
    tag_set: List[Any] = field(default_factory=list)
    vpc_endpoint_id: str = ""
    vpc_endpoint_type: str = ""
    vpc_id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTimestamp": self.creation_timestamp,
            "dnsEntrySet": self.dns_entry_set,
            "dnsOptions": self.dns_options,
            "failureReason": self.failure_reason,
            "groupSet": self.group_set,
            "ipAddressType": self.ip_address_type,
            "ipv4PrefixSet": self.ipv4_prefix_set,
            "ipv6PrefixSet": self.ipv6_prefix_set,
            "lastError": self.last_error,
            "networkInterfaceIdSet": self.network_interface_id_set,
            "ownerId": self.owner_id,
            "policyDocument": self.policy_document,
            "privateDnsEnabled": self.private_dns_enabled,
            "requesterManaged": self.requester_managed,
            "resourceConfigurationArn": self.resource_configuration_arn,
            "routeTableIdSet": self.route_table_id_set,
            "serviceName": self.service_name,
            "serviceNetworkArn": self.service_network_arn,
            "serviceRegion": self.service_region,
            "state": self.state,
            "subnetIdSet": self.subnet_id_set,
            "tagSet": self.tag_set,
            "vpcEndpointId": self.vpc_endpoint_id,
            "vpcEndpointType": self.vpc_endpoint_type,
            "vpcId": self.vpc_id,
        }

class VpcEndpoint_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.vpc_endpoints  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.vpcs.get(params['vpc_id']).vpc_endpoint_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).vpc_endpoint_ids.remove(resource_id)

    def _require_params(self, params: Dict[str, Any], names: List[str]):
        for name in names:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(
        self,
        store: Dict[str, Any],
        resource_id: str,
        error_code: str,
        message: Optional[str] = None,
    ):
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

    def _get_connection_notification_store(self) -> Dict[str, Dict[str, Any]]:
        if not hasattr(self.state, "vpc_endpoint_connection_notifications"):
            setattr(self.state, "vpc_endpoint_connection_notifications", {})
        return getattr(self.state, "vpc_endpoint_connection_notifications")

    def CreateVpcEndpoint(self, params: Dict[str, Any]):
        """Creates a VPC endpoint. A VPC endpoint provides a private connection between the
            specified VPC and the specified endpoint service. You can use an endpoint service
            provided by AWS, an AWS Marketplace Partner, or another
            AWS account. For more information, see theAWS"""

        error = self._require_params(params, ["VpcId"])
        if error:
            return error

        vpc_id = params.get("VpcId")
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        route_table_ids = params.get("RouteTableId.N") or []
        for route_table_id in route_table_ids:
            if route_table_id not in self.state.route_tables:
                return create_error_response("InvalidRouteTableID.NotFound", f"The ID '{route_table_id}' does not exist")

        security_group_ids = params.get("SecurityGroupId.N") or []
        for group_id in security_group_ids:
            if group_id not in self.state.security_groups:
                return create_error_response("InvalidSecurityGroupID.NotFound", f"The ID '{group_id}' does not exist")

        subnet_ids = params.get("SubnetId.N") or []
        for subnet_id in subnet_ids:
            if subnet_id not in self.state.subnets:
                return create_error_response("InvalidSubnetID.NotFound", f"The ID '{subnet_id}' does not exist")

        for subnet_config in params.get("SubnetConfiguration.N") or []:
            subnet_id = subnet_config.get("SubnetId")
            if subnet_id and subnet_id not in self.state.subnets:
                return create_error_response("InvalidSubnetID.NotFound", f"The ID '{subnet_id}' does not exist")

        tag_set: List[Dict[str, Any]] = []
        for tag_spec in params.get("TagSpecification.N") or []:
            spec_type = tag_spec.get("ResourceType")
            if spec_type and spec_type != "vpc-endpoint":
                continue
            for tag in tag_spec.get("Tag") or tag_spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        group_set = []
        for group_id in security_group_ids:
            group = self.state.security_groups.get(group_id)
            group_set.append({
                "groupId": group_id,
                "groupName": getattr(group, "group_name", "") if group else "",
            })

        endpoint_id = self._generate_id("vpce")
        timestamp = datetime.now(timezone.utc).isoformat()
        resource = VpcEndpoint(
            creation_timestamp=timestamp,
            dns_entry_set=[],
            dns_options=params.get("DnsOptions") or {},
            failure_reason="",
            group_set=group_set,
            ip_address_type=params.get("IpAddressType") or "",
            ipv4_prefix_set=[],
            ipv6_prefix_set=[],
            last_error={},
            network_interface_id_set=[],
            owner_id=getattr(vpc, "owner_id", ""),
            policy_document=params.get("PolicyDocument") or "",
            private_dns_enabled=str2bool(params.get("PrivateDnsEnabled")),
            requester_managed=False,
            resource_configuration_arn=params.get("ResourceConfigurationArn") or "",
            route_table_id_set=route_table_ids,
            service_name=params.get("ServiceName") or "",
            service_network_arn=params.get("ServiceNetworkArn") or "",
            service_region=params.get("ServiceRegion") or "",
            state=ResourceState.AVAILABLE.value,
            subnet_id_set=subnet_ids,
            tag_set=tag_set,
            vpc_endpoint_id=endpoint_id,
            vpc_endpoint_type=params.get("VpcEndpointType") or "",
            vpc_id=vpc_id,
        )
        self.resources[endpoint_id] = resource

        if vpc and hasattr(vpc, "vpc_endpoint_ids"):
            if endpoint_id not in vpc.vpc_endpoint_ids:
                vpc.vpc_endpoint_ids.append(endpoint_id)

        return {
            "clientToken": params.get("ClientToken") or "",
            "vpcEndpoint": resource.to_dict(),
        }

    def CreateVpcEndpointConnectionNotification(self, params: Dict[str, Any]):
        """Creates a connection notification for a specified VPC endpoint or VPC endpoint
            service. A connection notification notifies you of specific endpoint events. You must
            create an SNS topic to receive notifications. For more information, seeCreating an Amazon SNS topicin
         """

        error = self._require_params(params, ["ConnectionEvents.N", "ConnectionNotificationArn"])
        if error:
            return error

        vpc_endpoint_id = params.get("VpcEndpointId")
        if vpc_endpoint_id:
            _, error = self._get_resource_or_error(
                self.resources,
                vpc_endpoint_id,
                "InvalidVpcEndpointId.NotFound",
                f"The VpcEndpoint '{vpc_endpoint_id}' does not exist.",
            )
            if error:
                return error

        service_id = params.get("ServiceId")
        if service_id:
            _, error = self._get_resource_or_error(
                self.state.vpc_endpoint_services,
                service_id,
                "InvalidVpcEndpointServiceId.NotFound",
                f"The VpcEndpointService '{service_id}' does not exist.",
            )
            if error:
                return error

        connection_notification_id = self._generate_id("cnot")
        connection_notification_type = ""
        if vpc_endpoint_id:
            connection_notification_type = "VpcEndpoint"
        elif service_id:
            connection_notification_type = "VpcEndpointService"

        connection_notification = {
            "connectionEvents": params.get("ConnectionEvents.N") or [],
            "connectionNotificationArn": params.get("ConnectionNotificationArn") or "",
            "connectionNotificationId": connection_notification_id,
            "connectionNotificationState": "Enabled",
            "connectionNotificationType": connection_notification_type,
            "serviceId": service_id or "",
            "serviceRegion": "",
            "vpcEndpointId": vpc_endpoint_id or "",
        }

        store = self._get_connection_notification_store()
        store[connection_notification_id] = connection_notification

        return {
            "clientToken": params.get("ClientToken") or "",
            "connectionNotification": connection_notification,
        }

    def DeleteVpcEndpointConnectionNotifications(self, params: Dict[str, Any]):
        """Deletes the specified VPC endpoint connection notifications."""

        error = self._require_params(params, ["ConnectionNotificationId.N"])
        if error:
            return error

        connection_notification_ids = params.get("ConnectionNotificationId.N") or []
        store = self._get_connection_notification_store()

        for notification_id in connection_notification_ids:
            if notification_id not in store:
                return create_error_response(
                    "InvalidConnectionNotificationId.NotFound",
                    f"The ID '{notification_id}' does not exist",
                )

        for notification_id in connection_notification_ids:
            store.pop(notification_id, None)

        return {
            "unsuccessful": [],
        }

    def DeleteVpcEndpoints(self, params: Dict[str, Any]):
        """Deletes the specified VPC endpoints. When you delete a gateway endpoint, we delete the endpoint routes in the route tables for the endpoint. When you delete a Gateway Load Balancer endpoint, we delete its endpoint network interfaces. 
          You can only delete Gateway Load Balancer endpoints whe"""

        error = self._require_params(params, ["VpcEndpointId.N"])
        if error:
            return error

        vpc_endpoint_ids = params.get("VpcEndpointId.N") or []

        for endpoint_id in vpc_endpoint_ids:
            if endpoint_id not in self.resources:
                return create_error_response(
                    "InvalidVpcEndpointId.NotFound",
                    f"The ID '{endpoint_id}' does not exist",
                )

        for endpoint_id in vpc_endpoint_ids:
            resource = self.resources.pop(endpoint_id, None)
            if not resource:
                continue
            parent = self.state.vpcs.get(resource.vpc_id)
            if parent and hasattr(parent, "vpc_endpoint_ids") and endpoint_id in parent.vpc_endpoint_ids:
                parent.vpc_endpoint_ids.remove(endpoint_id)

        return {
            "unsuccessful": [],
        }

    def DescribeVpcEndpointAssociations(self, params: Dict[str, Any]):
        """Describes the VPC resources, VPC endpoint services, Amazon Lattice services, or service networks
         associated with the VPC endpoint."""

        vpc_endpoint_ids = params.get("VpcEndpointId.N") or []
        max_results = int(params.get("MaxResults") or 100)

        if vpc_endpoint_ids:
            resources, error = self._get_resources_by_ids(
                self.resources,
                vpc_endpoint_ids,
                "InvalidVpcEndpointId.NotFound",
            )
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N") or [])

        association_set = []
        for endpoint in resources[:max_results]:
            association_set.append({
                "associatedResourceAccessibility": "",
                "associatedResourceArn": endpoint.resource_configuration_arn or "",
                "dnsEntry": endpoint.dns_entry_set or [],
                "failureCode": "",
                "failureReason": endpoint.failure_reason or "",
                "id": endpoint.vpc_endpoint_id,
                "privateDnsEntry": {},
                "resourceConfigurationGroupArn": "",
                "serviceNetworkArn": endpoint.service_network_arn or "",
                "serviceNetworkName": "",
                "tagSet": endpoint.tag_set or [],
                "vpcEndpointId": endpoint.vpc_endpoint_id,
            })

        return {
            "nextToken": None,
            "vpcEndpointAssociationSet": association_set,
        }

    def DescribeVpcEndpointConnectionNotifications(self, params: Dict[str, Any]):
        """Describes the connection notifications for VPC endpoints and VPC endpoint
            services."""

        connection_notification_id = params.get("ConnectionNotificationId")
        max_results = int(params.get("MaxResults") or 100)
        store = self._get_connection_notification_store()

        if connection_notification_id:
            notification = store.get(connection_notification_id)
            if not notification:
                return create_error_response(
                    "InvalidConnectionNotificationId.NotFound",
                    f"The ID '{connection_notification_id}' does not exist",
                )
            notifications = [notification]
        else:
            notifications = list(store.values())

        notifications = apply_filters(notifications, params.get("Filter.N") or [])

        return {
            "connectionNotificationSet": notifications[:max_results],
            "nextToken": None,
        }

    def DescribeVpcEndpointConnections(self, params: Dict[str, Any]):
        """Describes the VPC endpoint connections to your VPC endpoint services, including any
            endpoints that are pending your acceptance."""

        max_results = int(params.get("MaxResults") or 100)

        resources = apply_filters(list(self.resources.values()), params.get("Filter.N") or [])

        connection_set = []
        for endpoint in resources[:max_results]:
            connection_set.append({
                "creationTimestamp": endpoint.creation_timestamp,
                "dnsEntrySet": endpoint.dns_entry_set or [],
                "gatewayLoadBalancerArnSet": [],
                "ipAddressType": endpoint.ip_address_type or "",
                "networkLoadBalancerArnSet": [],
                "serviceId": "",
                "tagSet": endpoint.tag_set or [],
                "vpcEndpointConnectionId": endpoint.vpc_endpoint_id,
                "vpcEndpointId": endpoint.vpc_endpoint_id,
                "vpcEndpointOwner": endpoint.owner_id or "",
                "vpcEndpointRegion": endpoint.service_region or "",
                "vpcEndpointState": endpoint.state or "",
            })

        return {
            "nextToken": None,
            "vpcEndpointConnectionSet": connection_set,
        }

    def DescribeVpcEndpoints(self, params: Dict[str, Any]):
        """Describes your VPC endpoints. The default is to describe all your VPC endpoints. 
            Alternatively, you can specify specific VPC endpoint IDs or filter the results to
            include only the VPC endpoints that match specific criteria."""

        vpc_endpoint_ids = params.get("VpcEndpointId.N") or []
        max_results = int(params.get("MaxResults") or 100)

        if vpc_endpoint_ids:
            resources, error = self._get_resources_by_ids(
                self.resources,
                vpc_endpoint_ids,
                "InvalidVpcEndpointId.NotFound",
            )
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N") or [])
        endpoint_set = [resource.to_dict() for resource in resources[:max_results]]

        return {
            "nextToken": None,
            "vpcEndpointSet": endpoint_set,
        }

    def ModifyVpcEndpoint(self, params: Dict[str, Any]):
        """Modifies attributes of a specified VPC endpoint. The attributes that you can modify
            depend on the type of VPC endpoint (interface, gateway, or Gateway Load Balancer). For more information, 
            see theAWS PrivateLink 
                Guide."""

        error = self._require_params(params, ["VpcEndpointId"])
        if error:
            return error

        vpc_endpoint_id = params.get("VpcEndpointId")
        endpoint, error = self._get_resource_or_error(
            self.resources,
            vpc_endpoint_id,
            "InvalidVpcEndpointId.NotFound",
            f"The VpcEndpoint '{vpc_endpoint_id}' does not exist.",
        )
        if error:
            return error

        add_route_table_ids = params.get("AddRouteTableId.N") or []
        remove_route_table_ids = params.get("RemoveRouteTableId.N") or []
        add_security_group_ids = params.get("AddSecurityGroupId.N") or []
        remove_security_group_ids = params.get("RemoveSecurityGroupId.N") or []
        add_subnet_ids = params.get("AddSubnetId.N") or []
        remove_subnet_ids = params.get("RemoveSubnetId.N") or []

        for route_table_id in add_route_table_ids + remove_route_table_ids:
            if route_table_id and route_table_id not in self.state.route_tables:
                return create_error_response("InvalidRouteTableID.NotFound", f"The ID '{route_table_id}' does not exist")

        for group_id in add_security_group_ids + remove_security_group_ids:
            if group_id and group_id not in self.state.security_groups:
                return create_error_response("InvalidSecurityGroupID.NotFound", f"The ID '{group_id}' does not exist")

        for subnet_id in add_subnet_ids + remove_subnet_ids:
            if subnet_id and subnet_id not in self.state.subnets:
                return create_error_response("InvalidSubnetID.NotFound", f"The ID '{subnet_id}' does not exist")

        for subnet_config in params.get("SubnetConfiguration.N") or []:
            subnet_id = subnet_config.get("SubnetId")
            if subnet_id and subnet_id not in self.state.subnets:
                return create_error_response("InvalidSubnetID.NotFound", f"The ID '{subnet_id}' does not exist")

        if params.get("DnsOptions") is not None:
            endpoint.dns_options = params.get("DnsOptions") or {}
        if params.get("IpAddressType") is not None:
            endpoint.ip_address_type = params.get("IpAddressType") or ""
        if params.get("PolicyDocument") is not None:
            endpoint.policy_document = params.get("PolicyDocument") or ""
        if params.get("ResetPolicy") is not None and str2bool(params.get("ResetPolicy")):
            endpoint.policy_document = ""
        if params.get("PrivateDnsEnabled") is not None:
            endpoint.private_dns_enabled = str2bool(params.get("PrivateDnsEnabled"))

        if add_route_table_ids:
            for route_table_id in add_route_table_ids:
                if route_table_id not in endpoint.route_table_id_set:
                    endpoint.route_table_id_set.append(route_table_id)
        if remove_route_table_ids:
            endpoint.route_table_id_set = [
                route_table_id
                for route_table_id in endpoint.route_table_id_set
                if route_table_id not in remove_route_table_ids
            ]

        if add_security_group_ids or remove_security_group_ids:
            group_ids = [group.get("groupId") for group in endpoint.group_set]
            for group_id in add_security_group_ids:
                if group_id not in group_ids:
                    group = self.state.security_groups.get(group_id)
                    endpoint.group_set.append({
                        "groupId": group_id,
                        "groupName": getattr(group, "group_name", "") if group else "",
                    })
            if remove_security_group_ids:
                endpoint.group_set = [
                    group
                    for group in endpoint.group_set
                    if group.get("groupId") not in remove_security_group_ids
                ]

        if add_subnet_ids:
            for subnet_id in add_subnet_ids:
                if subnet_id not in endpoint.subnet_id_set:
                    endpoint.subnet_id_set.append(subnet_id)
        if remove_subnet_ids:
            endpoint.subnet_id_set = [
                subnet_id
                for subnet_id in endpoint.subnet_id_set
                if subnet_id not in remove_subnet_ids
            ]

        return {
            "return": True,
        }

    def ModifyVpcEndpointConnectionNotification(self, params: Dict[str, Any]):
        """Modifies a connection notification for VPC endpoint or VPC endpoint service. You
            can change the SNS topic for the notification, or the events for which to be notified."""

        error = self._require_params(params, ["ConnectionNotificationId"])
        if error:
            return error

        connection_notification_id = params.get("ConnectionNotificationId")
        store = self._get_connection_notification_store()
        notification = store.get(connection_notification_id)
        if not notification:
            return create_error_response(
                "InvalidConnectionNotificationId.NotFound",
                f"The ID '{connection_notification_id}' does not exist",
            )

        if params.get("ConnectionEvents.N") is not None:
            notification["connectionEvents"] = params.get("ConnectionEvents.N") or []
        if params.get("ConnectionNotificationArn") is not None:
            notification["connectionNotificationArn"] = params.get("ConnectionNotificationArn") or ""

        store[connection_notification_id] = notification

        return {
            "return": True,
        }

    def _generate_id(self, prefix: str = 'vpc') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class vpcendpoint_RequestParser:
    @staticmethod
    def parse_create_vpc_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DnsOptions": get_scalar(md, "DnsOptions"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpAddressType": get_scalar(md, "IpAddressType"),
            "PolicyDocument": get_scalar(md, "PolicyDocument"),
            "PrivateDnsEnabled": get_scalar(md, "PrivateDnsEnabled"),
            "ResourceConfigurationArn": get_scalar(md, "ResourceConfigurationArn"),
            "RouteTableId.N": get_indexed_list(md, "RouteTableId"),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
            "ServiceName": get_scalar(md, "ServiceName"),
            "ServiceNetworkArn": get_scalar(md, "ServiceNetworkArn"),
            "ServiceRegion": get_scalar(md, "ServiceRegion"),
            "SubnetConfiguration.N": get_indexed_list(md, "SubnetConfiguration"),
            "SubnetId.N": get_indexed_list(md, "SubnetId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcEndpointType": get_scalar(md, "VpcEndpointType"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_create_vpc_endpoint_connection_notification_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "ConnectionEvents.N": get_indexed_list(md, "ConnectionEvents"),
            "ConnectionNotificationArn": get_scalar(md, "ConnectionNotificationArn"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ServiceId": get_scalar(md, "ServiceId"),
            "VpcEndpointId": get_scalar(md, "VpcEndpointId"),
        }

    @staticmethod
    def parse_delete_vpc_endpoint_connection_notifications_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ConnectionNotificationId.N": get_indexed_list(md, "ConnectionNotificationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_delete_vpc_endpoints_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpcEndpointId.N": get_indexed_list(md, "VpcEndpointId"),
        }

    @staticmethod
    def parse_describe_vpc_endpoint_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VpcEndpointId.N": get_indexed_list(md, "VpcEndpointId"),
        }

    @staticmethod
    def parse_describe_vpc_endpoint_connection_notifications_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ConnectionNotificationId": get_scalar(md, "ConnectionNotificationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_vpc_endpoint_connections_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_vpc_endpoints_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VpcEndpointId.N": get_indexed_list(md, "VpcEndpointId"),
        }

    @staticmethod
    def parse_modify_vpc_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddRouteTableId.N": get_indexed_list(md, "AddRouteTableId"),
            "AddSecurityGroupId.N": get_indexed_list(md, "AddSecurityGroupId"),
            "AddSubnetId.N": get_indexed_list(md, "AddSubnetId"),
            "DnsOptions": get_scalar(md, "DnsOptions"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpAddressType": get_scalar(md, "IpAddressType"),
            "PolicyDocument": get_scalar(md, "PolicyDocument"),
            "PrivateDnsEnabled": get_scalar(md, "PrivateDnsEnabled"),
            "RemoveRouteTableId.N": get_indexed_list(md, "RemoveRouteTableId"),
            "RemoveSecurityGroupId.N": get_indexed_list(md, "RemoveSecurityGroupId"),
            "RemoveSubnetId.N": get_indexed_list(md, "RemoveSubnetId"),
            "ResetPolicy": get_scalar(md, "ResetPolicy"),
            "SubnetConfiguration.N": get_indexed_list(md, "SubnetConfiguration"),
            "VpcEndpointId": get_scalar(md, "VpcEndpointId"),
        }

    @staticmethod
    def parse_modify_vpc_endpoint_connection_notification_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ConnectionEvents.N": get_indexed_list(md, "ConnectionEvents"),
            "ConnectionNotificationArn": get_scalar(md, "ConnectionNotificationArn"),
            "ConnectionNotificationId": get_scalar(md, "ConnectionNotificationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateVpcEndpoint": vpcendpoint_RequestParser.parse_create_vpc_endpoint_request,
            "CreateVpcEndpointConnectionNotification": vpcendpoint_RequestParser.parse_create_vpc_endpoint_connection_notification_request,
            "DeleteVpcEndpointConnectionNotifications": vpcendpoint_RequestParser.parse_delete_vpc_endpoint_connection_notifications_request,
            "DeleteVpcEndpoints": vpcendpoint_RequestParser.parse_delete_vpc_endpoints_request,
            "DescribeVpcEndpointAssociations": vpcendpoint_RequestParser.parse_describe_vpc_endpoint_associations_request,
            "DescribeVpcEndpointConnectionNotifications": vpcendpoint_RequestParser.parse_describe_vpc_endpoint_connection_notifications_request,
            "DescribeVpcEndpointConnections": vpcendpoint_RequestParser.parse_describe_vpc_endpoint_connections_request,
            "DescribeVpcEndpoints": vpcendpoint_RequestParser.parse_describe_vpc_endpoints_request,
            "ModifyVpcEndpoint": vpcendpoint_RequestParser.parse_modify_vpc_endpoint_request,
            "ModifyVpcEndpointConnectionNotification": vpcendpoint_RequestParser.parse_modify_vpc_endpoint_connection_notification_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class vpcendpoint_ResponseSerializer:
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
                xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_vpc_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpcEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize vpcEndpoint
        _vpcEndpoint_key = None
        if "vpcEndpoint" in data:
            _vpcEndpoint_key = "vpcEndpoint"
        elif "VpcEndpoint" in data:
            _vpcEndpoint_key = "VpcEndpoint"
        if _vpcEndpoint_key:
            param_data = data[_vpcEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpcEndpoint>')
            xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpcEndpoint>')
        xml_parts.append(f'</CreateVpcEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_vpc_endpoint_connection_notification_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpcEndpointConnectionNotificationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize connectionNotification
        _connectionNotification_key = None
        if "connectionNotification" in data:
            _connectionNotification_key = "connectionNotification"
        elif "ConnectionNotification" in data:
            _connectionNotification_key = "ConnectionNotification"
        if _connectionNotification_key:
            param_data = data[_connectionNotification_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<connectionNotification>')
            xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</connectionNotification>')
        xml_parts.append(f'</CreateVpcEndpointConnectionNotificationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpc_endpoint_connection_notifications_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpcEndpointConnectionNotificationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</DeleteVpcEndpointConnectionNotificationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpc_endpoints_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpcEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</DeleteVpcEndpointsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_endpoint_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcEndpointAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize vpcEndpointAssociationSet
        _vpcEndpointAssociationSet_key = None
        if "vpcEndpointAssociationSet" in data:
            _vpcEndpointAssociationSet_key = "vpcEndpointAssociationSet"
        elif "VpcEndpointAssociationSet" in data:
            _vpcEndpointAssociationSet_key = "VpcEndpointAssociationSet"
        elif "VpcEndpointAssociations" in data:
            _vpcEndpointAssociationSet_key = "VpcEndpointAssociations"
        if _vpcEndpointAssociationSet_key:
            param_data = data[_vpcEndpointAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpcEndpointAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpcEndpointAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<vpcEndpointAssociationSet/>')
        xml_parts.append(f'</DescribeVpcEndpointAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_endpoint_connection_notifications_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcEndpointConnectionNotificationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize connectionNotificationSet
        _connectionNotificationSet_key = None
        if "connectionNotificationSet" in data:
            _connectionNotificationSet_key = "connectionNotificationSet"
        elif "ConnectionNotificationSet" in data:
            _connectionNotificationSet_key = "ConnectionNotificationSet"
        elif "ConnectionNotifications" in data:
            _connectionNotificationSet_key = "ConnectionNotifications"
        if _connectionNotificationSet_key:
            param_data = data[_connectionNotificationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<connectionNotificationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</connectionNotificationSet>')
            else:
                xml_parts.append(f'{indent_str}<connectionNotificationSet/>')
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
        xml_parts.append(f'</DescribeVpcEndpointConnectionNotificationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_endpoint_connections_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcEndpointConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize vpcEndpointConnectionSet
        _vpcEndpointConnectionSet_key = None
        if "vpcEndpointConnectionSet" in data:
            _vpcEndpointConnectionSet_key = "vpcEndpointConnectionSet"
        elif "VpcEndpointConnectionSet" in data:
            _vpcEndpointConnectionSet_key = "VpcEndpointConnectionSet"
        elif "VpcEndpointConnections" in data:
            _vpcEndpointConnectionSet_key = "VpcEndpointConnections"
        if _vpcEndpointConnectionSet_key:
            param_data = data[_vpcEndpointConnectionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpcEndpointConnectionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpcEndpointConnectionSet>')
            else:
                xml_parts.append(f'{indent_str}<vpcEndpointConnectionSet/>')
        xml_parts.append(f'</DescribeVpcEndpointConnectionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpc_endpoints_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpcEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize vpcEndpointSet
        _vpcEndpointSet_key = None
        if "vpcEndpointSet" in data:
            _vpcEndpointSet_key = "vpcEndpointSet"
        elif "VpcEndpointSet" in data:
            _vpcEndpointSet_key = "VpcEndpointSet"
        elif "VpcEndpoints" in data:
            _vpcEndpointSet_key = "VpcEndpoints"
        if _vpcEndpointSet_key:
            param_data = data[_vpcEndpointSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpcEndpointSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpcEndpointSet>')
            else:
                xml_parts.append(f'{indent_str}<vpcEndpointSet/>')
        xml_parts.append(f'</DescribeVpcEndpointsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpc_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpcEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyVpcEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpc_endpoint_connection_notification_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpcEndpointConnectionNotificationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyVpcEndpointConnectionNotificationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateVpcEndpoint": vpcendpoint_ResponseSerializer.serialize_create_vpc_endpoint_response,
            "CreateVpcEndpointConnectionNotification": vpcendpoint_ResponseSerializer.serialize_create_vpc_endpoint_connection_notification_response,
            "DeleteVpcEndpointConnectionNotifications": vpcendpoint_ResponseSerializer.serialize_delete_vpc_endpoint_connection_notifications_response,
            "DeleteVpcEndpoints": vpcendpoint_ResponseSerializer.serialize_delete_vpc_endpoints_response,
            "DescribeVpcEndpointAssociations": vpcendpoint_ResponseSerializer.serialize_describe_vpc_endpoint_associations_response,
            "DescribeVpcEndpointConnectionNotifications": vpcendpoint_ResponseSerializer.serialize_describe_vpc_endpoint_connection_notifications_response,
            "DescribeVpcEndpointConnections": vpcendpoint_ResponseSerializer.serialize_describe_vpc_endpoint_connections_response,
            "DescribeVpcEndpoints": vpcendpoint_ResponseSerializer.serialize_describe_vpc_endpoints_response,
            "ModifyVpcEndpoint": vpcendpoint_ResponseSerializer.serialize_modify_vpc_endpoint_response,
            "ModifyVpcEndpointConnectionNotification": vpcendpoint_ResponseSerializer.serialize_modify_vpc_endpoint_connection_notification_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

