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
class TargetNetwork:
    association_id: str = ""
    client_vpn_endpoint_id: str = ""
    security_groups: List[Any] = field(default_factory=list)
    status: Dict[str, Any] = field(default_factory=dict)
    target_network_id: str = ""
    vpc_id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "associationId": self.association_id,
            "clientVpnEndpointId": self.client_vpn_endpoint_id,
            "securityGroups": self.security_groups,
            "status": self.status,
            "targetNetworkId": self.target_network_id,
            "vpcId": self.vpc_id,
        }

class TargetNetwork_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.target_networks  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.routes.get(params['client_vpn_endpoint_id']).target_network_ids.append(new_id)
    #   Delete: self.state.routes.get(resource.client_vpn_endpoint_id).target_network_ids.remove(resource_id)
    #   Create: self.state.vpcs.get(params['vpc_id']).target_network_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).target_network_ids.remove(resource_id)


    def _get_client_vpn_endpoint(self, client_vpn_endpoint_id: str):
        endpoint = self.state.client_vpn_endpoints.get(client_vpn_endpoint_id)
        if not endpoint:
            return create_error_response(
                "InvalidClientVpnEndpointId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' does not exist.",
            )
        return endpoint

    def _list_target_networks(self, client_vpn_endpoint_id: str) -> List[TargetNetwork]:
        return [
            network
            for network in self.resources.values()
            if network.client_vpn_endpoint_id == client_vpn_endpoint_id
        ]

    def _get_target_network_by_association_id(self, association_id: str) -> Optional[TargetNetwork]:
        for network in self.resources.values():
            if network.association_id == association_id:
                return network
        return None


    def ApplySecurityGroupsToClientVpnTargetNetwork(self, params: Dict[str, Any]):
        """Applies a security group to the association between the target network and the Client VPN endpoint. This action replaces the existing 
			security groups with the specified security groups."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        security_group_ids = params.get("SecurityGroupId.N", []) or []
        vpc_id = params.get("VpcId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")
        if not security_group_ids:
            return create_error_response("MissingParameter", "SecurityGroupId.N is required.")
        if not vpc_id:
            return create_error_response("MissingParameter", "VpcId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response(
                "InvalidVpcID.NotFound",
                f"VPC '{vpc_id}' does not exist.",
            )

        for security_group_id in security_group_ids:
            security_group = self.state.security_groups.get(security_group_id)
            if not security_group:
                return create_error_response(
                    "InvalidGroup.NotFound",
                    f"Security group '{security_group_id}' does not exist.",
                )

        networks = [
            network
            for network in self._list_target_networks(client_vpn_endpoint_id)
            if network.vpc_id == vpc_id
        ]
        if not networks:
            return create_error_response(
                "InvalidClientVpnTargetNetworkAssociationId.NotFound",
                f"Client VPN endpoint '{client_vpn_endpoint_id}' has no target network in VPC '{vpc_id}'.",
            )

        for network in networks:
            network.security_groups = list(security_group_ids)

        return {
            'securityGroupIds': list(security_group_ids),
            }

    def AssociateClientVpnTargetNetwork(self, params: Dict[str, Any]):
        """Associates a target network with a Client VPN endpoint. A target network is a subnet in a VPC. You can associate multiple subnets from the same VPC with a Client VPN endpoint. You can associate only one subnet in each Availability Zone. We recommend that you associate at least two subnets to provide"""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        subnet_id = params.get("SubnetId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")
        if not subnet_id:
            return create_error_response("MissingParameter", "SubnetId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        subnet = self.state.subnets.get(subnet_id)
        if not subnet:
            return create_error_response(
                "InvalidSubnetID.NotFound",
                f"Subnet '{subnet_id}' does not exist.",
            )

        vpc_id = getattr(subnet, "vpc_id", "") or ""
        vpc = self.state.vpcs.get(vpc_id) if vpc_id else None
        if not vpc:
            return create_error_response(
                "InvalidVpcID.NotFound",
                f"VPC '{vpc_id}' does not exist.",
            )

        existing = next(
            (
                network
                for network in self.resources.values()
                if network.client_vpn_endpoint_id == client_vpn_endpoint_id
                and network.target_network_id == subnet_id
            ),
            None,
        )
        if existing:
            status = existing.status or {"code": "associated", "message": "Association established"}
            if not existing.status:
                existing.status = status
            if hasattr(endpoint, "associated_target_network"):
                if existing.association_id not in endpoint.associated_target_network:
                    endpoint.associated_target_network.append(existing.association_id)
            return {
                'associationId': existing.association_id,
                'status': status,
                }

        association_id = self._generate_id("target")
        status = {"code": "associated", "message": "Association established"}
        security_groups = getattr(endpoint, "security_group_id_set", []) or []
        resource = TargetNetwork(
            association_id=association_id,
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            security_groups=security_groups,
            status=status,
            target_network_id=subnet_id,
            vpc_id=vpc_id,
        )
        self.resources[association_id] = resource

        if hasattr(endpoint, "associated_target_network"):
            endpoint.associated_target_network.append(association_id)

        parent = self.state.routes.get(client_vpn_endpoint_id)
        if parent and hasattr(parent, 'target_network_ids'):
            parent.target_network_ids.append(association_id)

        parent_vpc = self.state.vpcs.get(vpc_id)
        if parent_vpc and hasattr(parent_vpc, 'target_network_ids'):
            parent_vpc.target_network_ids.append(association_id)

        return {
            'associationId': association_id,
            'status': status,
            }

    def DescribeClientVpnTargetNetworks(self, params: Dict[str, Any]):
        """Describes the target networks associated with the specified Client VPN endpoint."""

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        networks = self._list_target_networks(client_vpn_endpoint_id)
        association_ids = params.get("AssociationIds.N", []) or []
        if association_ids:
            selected_networks: List[TargetNetwork] = []
            for association_id in association_ids:
                resource = self._get_target_network_by_association_id(association_id)
                if not resource or resource.client_vpn_endpoint_id != client_vpn_endpoint_id:
                    return create_error_response(
                        "InvalidClientVpnTargetNetworkAssociationId.NotFound",
                        f"The ID '{association_id}' does not exist",
                    )
                selected_networks.append(resource)
            networks = selected_networks

        filters = params.get("Filter.N", []) or []
        if filters:
            networks = apply_filters(networks, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = int(next_token or 0)
        paged_networks = networks[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(networks):
            new_next_token = str(start_index + max_results)

        return {
            'clientVpnTargetNetworks': [network.to_dict() for network in paged_networks],
            'nextToken': new_next_token,
            }

    def DisassociateClientVpnTargetNetwork(self, params: Dict[str, Any]):
        """Disassociates a target network from the specified Client VPN endpoint. When you disassociate the 
			last target network from a Client VPN, the following happens: The route that was automatically added for the VPC is deleted All active client connections are terminated"""

        association_id = params.get("AssociationId")
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if not association_id:
            return create_error_response("MissingParameter", "AssociationId is required.")
        if not client_vpn_endpoint_id:
            return create_error_response("MissingParameter", "ClientVpnEndpointId is required.")

        endpoint = self._get_client_vpn_endpoint(client_vpn_endpoint_id)
        if is_error_response(endpoint):
            return endpoint

        resource = self._get_target_network_by_association_id(association_id)
        if not resource or resource.client_vpn_endpoint_id != client_vpn_endpoint_id:
            return create_error_response(
                "InvalidClientVpnTargetNetworkAssociationId.NotFound",
                f"The ID '{association_id}' does not exist",
            )

        self.resources.pop(association_id, None)

        if hasattr(endpoint, "associated_target_network"):
            if association_id in endpoint.associated_target_network:
                endpoint.associated_target_network.remove(association_id)

        parent = self.state.routes.get(resource.client_vpn_endpoint_id)
        if parent and hasattr(parent, 'target_network_ids') and association_id in parent.target_network_ids:
            parent.target_network_ids.remove(association_id)

        parent_vpc = self.state.vpcs.get(resource.vpc_id)
        if parent_vpc and hasattr(parent_vpc, 'target_network_ids') and association_id in parent_vpc.target_network_ids:
            parent_vpc.target_network_ids.remove(association_id)

        status = {"code": "disassociated", "message": "Association disassociated"}
        return {
            'associationId': association_id,
            'status': status,
            }

    def _generate_id(self, prefix: str = 'target') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class targetnetwork_RequestParser:
    @staticmethod
    def parse_apply_security_groups_to_client_vpn_target_network_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_associate_client_vpn_target_network_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SubnetId": get_scalar(md, "SubnetId"),
        }

    @staticmethod
    def parse_describe_client_vpn_target_networks_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationIds.N": get_indexed_list(md, "AssociationIds"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disassociate_client_vpn_target_network_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
            "ClientVpnEndpointId": get_scalar(md, "ClientVpnEndpointId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "ApplySecurityGroupsToClientVpnTargetNetwork": targetnetwork_RequestParser.parse_apply_security_groups_to_client_vpn_target_network_request,
            "AssociateClientVpnTargetNetwork": targetnetwork_RequestParser.parse_associate_client_vpn_target_network_request,
            "DescribeClientVpnTargetNetworks": targetnetwork_RequestParser.parse_describe_client_vpn_target_networks_request,
            "DisassociateClientVpnTargetNetwork": targetnetwork_RequestParser.parse_disassociate_client_vpn_target_network_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class targetnetwork_ResponseSerializer:
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
                xml_parts.extend(targetnetwork_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(targetnetwork_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(targetnetwork_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(targetnetwork_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(targetnetwork_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(targetnetwork_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_apply_security_groups_to_client_vpn_target_network_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ApplySecurityGroupsToClientVpnTargetNetworkResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize securityGroupIds
        _securityGroupIds_key = None
        if "securityGroupIds" in data:
            _securityGroupIds_key = "securityGroupIds"
        elif "SecurityGroupIds" in data:
            _securityGroupIds_key = "SecurityGroupIds"
        if _securityGroupIds_key:
            param_data = data[_securityGroupIds_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<securityGroupIdsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</securityGroupIdsSet>')
            else:
                xml_parts.append(f'{indent_str}<securityGroupIdsSet/>')
        xml_parts.append(f'</ApplySecurityGroupsToClientVpnTargetNetworkResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_associate_client_vpn_target_network_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateClientVpnTargetNetworkResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associationId
        _associationId_key = None
        if "associationId" in data:
            _associationId_key = "associationId"
        elif "AssociationId" in data:
            _associationId_key = "AssociationId"
        if _associationId_key:
            param_data = data[_associationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associationId>{esc(str(param_data))}</associationId>')
        # Serialize status
        _status_key = None
        if "status" in data:
            _status_key = "status"
        elif "Status" in data:
            _status_key = "Status"
        if _status_key:
            param_data = data[_status_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(targetnetwork_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</AssociateClientVpnTargetNetworkResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_client_vpn_target_networks_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeClientVpnTargetNetworksResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientVpnTargetNetworks
        _clientVpnTargetNetworks_key = None
        if "clientVpnTargetNetworks" in data:
            _clientVpnTargetNetworks_key = "clientVpnTargetNetworks"
        elif "ClientVpnTargetNetworks" in data:
            _clientVpnTargetNetworks_key = "ClientVpnTargetNetworks"
        if _clientVpnTargetNetworks_key:
            param_data = data[_clientVpnTargetNetworks_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<clientVpnTargetNetworksSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(targetnetwork_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</clientVpnTargetNetworksSet>')
            else:
                xml_parts.append(f'{indent_str}<clientVpnTargetNetworksSet/>')
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
        xml_parts.append(f'</DescribeClientVpnTargetNetworksResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_client_vpn_target_network_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateClientVpnTargetNetworkResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associationId
        _associationId_key = None
        if "associationId" in data:
            _associationId_key = "associationId"
        elif "AssociationId" in data:
            _associationId_key = "AssociationId"
        if _associationId_key:
            param_data = data[_associationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associationId>{esc(str(param_data))}</associationId>')
        # Serialize status
        _status_key = None
        if "status" in data:
            _status_key = "status"
        elif "Status" in data:
            _status_key = "Status"
        if _status_key:
            param_data = data[_status_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<statusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(targetnetwork_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</statusSet>')
            else:
                xml_parts.append(f'{indent_str}<statusSet/>')
        xml_parts.append(f'</DisassociateClientVpnTargetNetworkResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "ApplySecurityGroupsToClientVpnTargetNetwork": targetnetwork_ResponseSerializer.serialize_apply_security_groups_to_client_vpn_target_network_response,
            "AssociateClientVpnTargetNetwork": targetnetwork_ResponseSerializer.serialize_associate_client_vpn_target_network_response,
            "DescribeClientVpnTargetNetworks": targetnetwork_ResponseSerializer.serialize_describe_client_vpn_target_networks_response,
            "DisassociateClientVpnTargetNetwork": targetnetwork_ResponseSerializer.serialize_disassociate_client_vpn_target_network_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

