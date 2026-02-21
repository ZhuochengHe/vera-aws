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
class TransitGateway:
    creation_time: str = ""
    description: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    owner_id: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    transit_gateway_arn: str = ""
    transit_gateway_id: str = ""

    # Internal dependency tracking — not in API response
    route_table_ids: List[str] = field(default_factory=list)  # tracks RouteTable children
    transit_gateway_connect_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayConnect children
    transit_gateway_policy_table_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayPolicyTable children
    transit_gateway_route_table_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayRouteTable children
    vpn_concentrator_ids: List[str] = field(default_factory=list)  # tracks VpnConcentrator children
    vpn_connection_ids: List[str] = field(default_factory=list)  # tracks VpnConnection children

    tags: List[Dict[str, Any]] = field(default_factory=list)
    transit_gateway_vpc_attachment_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTime": self.creation_time,
            "description": self.description,
            "options": self.options,
            "ownerId": self.owner_id,
            "state": self.state,
            "tagSet": self.tag_set,
            "transitGatewayArn": self.transit_gateway_arn,
            "transitGatewayId": self.transit_gateway_id,
        }

class TransitGateway_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.transit_gateways  # alias to shared store

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            value = params.get(name)
            if value is None or value == "":
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_or_error(self, store: Dict[str, Any], resource_id: str, code: str, message: str):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(code, message)
        return resource, None

    def _get_transit_gateway(self, transit_gateway_id: str):
        return self._get_or_error(
            self.resources,
            transit_gateway_id,
            "InvalidTransitGatewayID.NotFound",
            f"The ID '{transit_gateway_id}' does not exist",
        )

    def _get_vpc(self, vpc_id: str):
        return self._get_or_error(
            self.state.vpcs,
            vpc_id,
            "InvalidVpcID.NotFound",
            f"VPC '{vpc_id}' does not exist.",
        )

    def _get_transit_gateway_vpc_attachments_store(self) -> Dict[str, Any]:
        if not hasattr(self.state, "transit_gateway_vpc_attachments"):
            setattr(self.state, "transit_gateway_vpc_attachments", {})
        return self.state.transit_gateway_vpc_attachments

    def _get_transit_gateway_vpc_attachment(self, attachment_id: str):
        store = self._get_transit_gateway_vpc_attachments_store()
        return self._get_or_error(
            store,
            attachment_id,
            "InvalidTransitGatewayAttachmentID.NotFound",
            f"The ID '{attachment_id}' does not exist",
        )

    def _extract_tag_set(self, tag_specs: List[Dict[str, Any]], resource_type: str) -> List[Dict[str, Any]]:
        for spec in tag_specs or []:
            if spec.get("ResourceType") == resource_type:
                return spec.get("Tags", []) or []
        return []

    def AcceptTransitGatewayVpcAttachment(self, params: Dict[str, Any]):
        """Accepts a request to attach a VPC to a transit gateway. The VPC attachment must be in thependingAcceptancestate.
         UseDescribeTransitGatewayVpcAttachmentsto view your pending VPC attachment requests.
         UseRejectTransitGatewayVpcAttachmentto reject a VPC attachment request."""

        error = self._require_params(params, ["TransitGatewayAttachmentId"])
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment, error = self._get_transit_gateway_vpc_attachment(attachment_id)
        if error:
            return error

        if attachment.get("state") == "pendingAcceptance":
            attachment["state"] = "available"

        return {
            'transitGatewayVpcAttachment': {
                'creationTime': attachment.get("creationTime"),
                'options': attachment.get("options", {}),
                'state': attachment.get("state"),
                'subnetIds': attachment.get("subnetIds", []),
                'tagSet': attachment.get("tagSet", []),
                'transitGatewayAttachmentId': attachment.get("transitGatewayAttachmentId"),
                'transitGatewayId': attachment.get("transitGatewayId"),
                'vpcId': attachment.get("vpcId"),
                'vpcOwnerId': attachment.get("vpcOwnerId"),
                },
            }

    def CreateTransitGateway(self, params: Dict[str, Any]):
        """Creates a transit gateway. You can use a transit gateway to interconnect your virtual private clouds (VPC) and on-premises networks.
          After the transit gateway enters theavailablestate, you can attach your VPCs and VPN
          connections to the transit gateway. To attach your VPCs, useCr"""

        description = params.get("Description") or ""
        options_input = params.get("Options") or {}
        tag_set = self._extract_tag_set(params.get("TagSpecification.N", []), "transit-gateway")
        owner_id = getattr(self.state, "account_id", "000000000000")

        encryption_support = options_input.get("EncryptionSupport") or options_input.get("encryptionSupport") or {}
        options = {
            "amazonSideAsn": options_input.get("AmazonSideAsn") or options_input.get("amazonSideAsn") or 64512,
            "associationDefaultRouteTableId": options_input.get("AssociationDefaultRouteTableId")
            or options_input.get("associationDefaultRouteTableId")
            or "",
            "autoAcceptSharedAttachments": options_input.get("AutoAcceptSharedAttachments")
            or options_input.get("autoAcceptSharedAttachments")
            or "disable",
            "defaultRouteTableAssociation": options_input.get("DefaultRouteTableAssociation")
            or options_input.get("defaultRouteTableAssociation")
            or "enable",
            "defaultRouteTablePropagation": options_input.get("DefaultRouteTablePropagation")
            or options_input.get("defaultRouteTablePropagation")
            or "enable",
            "dnsSupport": options_input.get("DnsSupport") or options_input.get("dnsSupport") or "enable",
            "encryptionSupport": {
                "encryptionState": encryption_support.get("EncryptionState")
                or encryption_support.get("encryptionState")
                or "disabled",
                "stateMessage": encryption_support.get("StateMessage")
                or encryption_support.get("stateMessage")
                or "",
            },
            "multicastSupport": options_input.get("MulticastSupport")
            or options_input.get("multicastSupport")
            or "disable",
            "propagationDefaultRouteTableId": options_input.get("PropagationDefaultRouteTableId")
            or options_input.get("propagationDefaultRouteTableId")
            or "",
            "securityGroupReferencingSupport": options_input.get("SecurityGroupReferencingSupport")
            or options_input.get("securityGroupReferencingSupport")
            or "disable",
            "transitGatewayCidrBlocks": options_input.get("TransitGatewayCidrBlocks")
            or options_input.get("transitGatewayCidrBlocks")
            or [],
            "vpnEcmpSupport": options_input.get("VpnEcmpSupport") or options_input.get("vpnEcmpSupport") or "enable",
        }

        transit_gateway_id = self._generate_id("tgw")
        creation_time = self._now()
        transit_gateway_arn = f"arn:aws:ec2:::transit-gateway/{transit_gateway_id}"
        resource = TransitGateway(
            creation_time=creation_time,
            description=description,
            options=options,
            owner_id=owner_id,
            state="available",
            tag_set=tag_set,
            transit_gateway_arn=transit_gateway_arn,
            transit_gateway_id=transit_gateway_id,
            tags=tag_set,
        )
        self.resources[transit_gateway_id] = resource

        return {
            'transitGateway': {
                'creationTime': resource.creation_time,
                'description': resource.description,
                'options': resource.options,
                'ownerId': resource.owner_id,
                'state': resource.state,
                'tagSet': resource.tag_set,
                'transitGatewayArn': resource.transit_gateway_arn,
                'transitGatewayId': resource.transit_gateway_id,
            },
        }

    def CreateTransitGatewayVpcAttachment(self, params: Dict[str, Any]):
        """Attaches the specified VPC to the specified transit gateway. If you attach a VPC with a CIDR range that overlaps the CIDR range of a VPC that is already attached,
         the new VPC CIDR range is not propagated to the default propagation route table. To send VPC traffic to an attached transit gate"""

        error = self._require_params(params, ["SubnetIds.N", "TransitGatewayId", "VpcId"])
        if error:
            return error

        subnet_ids = params.get("SubnetIds.N", []) or []
        if not subnet_ids:
            return create_error_response("MissingParameter", "Missing required parameter: SubnetIds.N")

        transit_gateway_id = params.get("TransitGatewayId")
        transit_gateway, error = self._get_transit_gateway(transit_gateway_id)
        if error:
            return error

        vpc_id = params.get("VpcId")
        vpc, error = self._get_vpc(vpc_id)
        if error:
            return error

        for subnet_id in subnet_ids:
            subnet = self.state.subnets.get(subnet_id)
            if not subnet:
                return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")
            if hasattr(subnet, "vpc_id") and subnet.vpc_id and subnet.vpc_id != vpc_id:
                return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")

        options_input = params.get("Options") or {}
        options = {
            "applianceModeSupport": options_input.get("ApplianceModeSupport")
            or options_input.get("applianceModeSupport")
            or "disable",
            "dnsSupport": options_input.get("DnsSupport") or options_input.get("dnsSupport") or "enable",
            "ipv6Support": options_input.get("Ipv6Support") or options_input.get("ipv6Support") or "disable",
            "securityGroupReferencingSupport": options_input.get("SecurityGroupReferencingSupport")
            or options_input.get("securityGroupReferencingSupport")
            or "disable",
        }
        tag_set = self._extract_tag_set(params.get("TagSpecifications.N", []), "transit-gateway-attachment")
        creation_time = self._now()
        attachment_id = self._generate_id("tgw-attach")
        vpc_owner_id = getattr(vpc, "owner_id", getattr(self.state, "account_id", "000000000000"))
        auto_accept = transit_gateway.options.get("autoAcceptSharedAttachments")
        if auto_accept is True:
            auto_accept = "enable"
        attachment_state = "available" if vpc_owner_id == transit_gateway.owner_id or auto_accept == "enable" else "pendingAcceptance"

        attachment = {
            "creationTime": creation_time,
            "options": options,
            "state": attachment_state,
            "subnetIds": list(subnet_ids),
            "tagSet": tag_set,
            "transitGatewayAttachmentId": attachment_id,
            "transitGatewayId": transit_gateway_id,
            "vpcId": vpc_id,
            "vpcOwnerId": vpc_owner_id,
        }

        attachments_store = self._get_transit_gateway_vpc_attachments_store()
        attachments_store[attachment_id] = attachment
        transit_gateway.transit_gateway_vpc_attachment_ids.append(attachment_id)

        return {
            'transitGatewayVpcAttachment': attachment,
        }

    def DeleteTransitGateway(self, params: Dict[str, Any]):
        """Deletes the specified transit gateway."""

        error = self._require_params(params, ["TransitGatewayId"])
        if error:
            return error

        transit_gateway_id = params.get("TransitGatewayId")
        resource, error = self._get_transit_gateway(transit_gateway_id)
        if error:
            return error

        if getattr(resource, "route_table_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGateway has dependent RouteTable(s) and cannot be deleted.",
            )
        if getattr(resource, "transit_gateway_connect_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGateway has dependent TransitGatewayConnect(s) and cannot be deleted.",
            )
        if getattr(resource, "transit_gateway_policy_table_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGateway has dependent TransitGatewayPolicyTable(s) and cannot be deleted.",
            )
        if getattr(resource, "transit_gateway_route_table_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGateway has dependent TransitGatewayRouteTable(s) and cannot be deleted.",
            )
        if getattr(resource, "vpn_concentrator_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGateway has dependent VpnConcentrator(s) and cannot be deleted.",
            )
        if getattr(resource, "vpn_connection_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGateway has dependent VpnConnection(s) and cannot be deleted.",
            )
        if getattr(resource, "transit_gateway_vpc_attachment_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGateway has dependent TransitGatewayVpcAttachment(s) and cannot be deleted.",
            )

        resource.state = "deleted"
        response = resource.to_dict()
        self.resources.pop(transit_gateway_id, None)

        return {
            'transitGateway': response,
            }

    def DeleteTransitGatewayVpcAttachment(self, params: Dict[str, Any]):
        """Deletes the specified VPC attachment."""

        error = self._require_params(params, ["TransitGatewayAttachmentId"])
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment, error = self._get_transit_gateway_vpc_attachment(attachment_id)
        if error:
            return error

        transit_gateway_id = attachment.get("transitGatewayId")
        transit_gateway = self.resources.get(transit_gateway_id)
        if transit_gateway and attachment_id in getattr(transit_gateway, "transit_gateway_vpc_attachment_ids", []):
            transit_gateway.transit_gateway_vpc_attachment_ids.remove(attachment_id)

        attachment["state"] = "deleted"
        response = {
            'creationTime': attachment.get("creationTime"),
            'options': attachment.get("options", {}),
            'state': attachment.get("state"),
            'subnetIds': attachment.get("subnetIds", []),
            'tagSet': attachment.get("tagSet", []),
            'transitGatewayAttachmentId': attachment.get("transitGatewayAttachmentId"),
            'transitGatewayId': attachment.get("transitGatewayId"),
            'vpcId': attachment.get("vpcId"),
            'vpcOwnerId': attachment.get("vpcOwnerId"),
        }

        attachments_store = self._get_transit_gateway_vpc_attachments_store()
        attachments_store.pop(attachment_id, None)

        return {
            'transitGatewayVpcAttachment': response,
            }

    def DescribeTransitGatewayAttachments(self, params: Dict[str, Any]):
        """Describes one or more attachments between resources and transit gateways. By default, all attachments are described.
         Alternatively, you can filter the results by attachment ID, attachment state, resource ID, or resource owner."""

        attachment_ids = params.get("TransitGatewayAttachmentIds.N", []) or []
        max_results = int(params.get("MaxResults") or 100)
        attachments_store = self._get_transit_gateway_vpc_attachments_store()

        if attachment_ids:
            attachments = []
            for attachment_id in attachment_ids:
                attachment = attachments_store.get(attachment_id)
                if not attachment:
                    return create_error_response(
                        "InvalidTransitGatewayAttachmentID.NotFound",
                        f"The ID '{attachment_id}' does not exist",
                    )
                attachments.append(attachment)
        else:
            attachments = list(attachments_store.values())

        attachments = apply_filters(attachments, params.get("Filter.N", []))
        response_items = []
        for attachment in attachments[:max_results]:
            transit_gateway_id = attachment.get("transitGatewayId")
            transit_gateway = self.resources.get(transit_gateway_id)
            transit_gateway_owner_id = transit_gateway.owner_id if transit_gateway else ""
            response_items.append({
                "association": attachment.get("association") or {},
                "creationTime": attachment.get("creationTime"),
                "resourceId": attachment.get("vpcId"),
                "resourceOwnerId": attachment.get("vpcOwnerId"),
                "resourceType": "vpc",
                "state": attachment.get("state"),
                "tagSet": attachment.get("tagSet", []),
                "transitGatewayAttachmentId": attachment.get("transitGatewayAttachmentId"),
                "transitGatewayId": transit_gateway_id,
                "transitGatewayOwnerId": transit_gateway_owner_id,
            })

        return {
            'nextToken': None,
            'transitGatewayAttachments': response_items,
            }

    def DescribeTransitGateways(self, params: Dict[str, Any]):
        """Describes one or more transit gateways. By default, all transit gateways are described. Alternatively, you can
         filter the results."""

        transit_gateway_ids = params.get("TransitGatewayIds.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if transit_gateway_ids:
            resources: List[TransitGateway] = []
            for transit_gateway_id in transit_gateway_ids:
                resource = self.resources.get(transit_gateway_id)
                if not resource:
                    return create_error_response(
                        "InvalidTransitGatewayID.NotFound",
                        f"The ID '{transit_gateway_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        transit_gateways = []
        for resource in resources[:max_results]:
            transit_gateways.append(resource.to_dict())

        return {
            'nextToken': None,
            'transitGatewaySet': transit_gateways,
            }

    def DescribeTransitGatewayVpcAttachments(self, params: Dict[str, Any]):
        """Describes one or more VPC attachments. By default, all VPC attachments are described.
         Alternatively, you can filter the results."""

        attachment_ids = params.get("TransitGatewayAttachmentIds.N", []) or []
        max_results = int(params.get("MaxResults") or 100)
        attachments_store = self._get_transit_gateway_vpc_attachments_store()

        if attachment_ids:
            attachments = []
            for attachment_id in attachment_ids:
                attachment = attachments_store.get(attachment_id)
                if not attachment:
                    return create_error_response(
                        "InvalidTransitGatewayAttachmentID.NotFound",
                        f"The ID '{attachment_id}' does not exist",
                    )
                attachments.append(attachment)
        else:
            attachments = list(attachments_store.values())

        attachments = apply_filters(attachments, params.get("Filter.N", []))
        response_items = []
        for attachment in attachments[:max_results]:
            response_items.append({
                "creationTime": attachment.get("creationTime"),
                "options": attachment.get("options", {}),
                "state": attachment.get("state"),
                "subnetIds": attachment.get("subnetIds", []),
                "tagSet": attachment.get("tagSet", []),
                "transitGatewayAttachmentId": attachment.get("transitGatewayAttachmentId"),
                "transitGatewayId": attachment.get("transitGatewayId"),
                "vpcId": attachment.get("vpcId"),
                "vpcOwnerId": attachment.get("vpcOwnerId"),
            })

        return {
            'nextToken': None,
            'transitGatewayVpcAttachments': response_items,
            }

    def ModifyTransitGateway(self, params: Dict[str, Any]):
        """Modifies the specified transit gateway. When you modify a transit gateway, the modified options are applied to new transit gateway attachments only. Your existing transit gateway attachments are not modified."""

        error = self._require_params(params, ["TransitGatewayId"])
        if error:
            return error

        transit_gateway_id = params.get("TransitGatewayId")
        resource, error = self._get_transit_gateway(transit_gateway_id)
        if error:
            return error

        description = params.get("Description")
        if description is not None:
            resource.description = description

        options_input = params.get("Options") or {}
        if options_input:
            encryption_support = options_input.get("EncryptionSupport") or options_input.get("encryptionSupport")
            if encryption_support is not None:
                resource.options.setdefault("encryptionSupport", {})
                if encryption_support.get("EncryptionState") is not None or encryption_support.get("encryptionState") is not None:
                    resource.options["encryptionSupport"]["encryptionState"] = (
                        encryption_support.get("EncryptionState")
                        if encryption_support.get("EncryptionState") is not None
                        else encryption_support.get("encryptionState")
                    )
                if encryption_support.get("StateMessage") is not None or encryption_support.get("stateMessage") is not None:
                    resource.options["encryptionSupport"]["stateMessage"] = (
                        encryption_support.get("StateMessage")
                        if encryption_support.get("StateMessage") is not None
                        else encryption_support.get("stateMessage")
                    )

            option_map = {
                "amazonSideAsn": ["AmazonSideAsn", "amazonSideAsn"],
                "associationDefaultRouteTableId": ["AssociationDefaultRouteTableId", "associationDefaultRouteTableId"],
                "autoAcceptSharedAttachments": ["AutoAcceptSharedAttachments", "autoAcceptSharedAttachments"],
                "defaultRouteTableAssociation": ["DefaultRouteTableAssociation", "defaultRouteTableAssociation"],
                "defaultRouteTablePropagation": ["DefaultRouteTablePropagation", "defaultRouteTablePropagation"],
                "dnsSupport": ["DnsSupport", "dnsSupport"],
                "multicastSupport": ["MulticastSupport", "multicastSupport"],
                "propagationDefaultRouteTableId": ["PropagationDefaultRouteTableId", "propagationDefaultRouteTableId"],
                "securityGroupReferencingSupport": ["SecurityGroupReferencingSupport", "securityGroupReferencingSupport"],
                "transitGatewayCidrBlocks": ["TransitGatewayCidrBlocks", "transitGatewayCidrBlocks"],
                "vpnEcmpSupport": ["VpnEcmpSupport", "vpnEcmpSupport"],
            }
            for option_key, candidates in option_map.items():
                for candidate in candidates:
                    if candidate in options_input and options_input.get(candidate) is not None:
                        resource.options[option_key] = options_input.get(candidate)
                        break

        return {
            'transitGateway': {
                'creationTime': resource.creation_time,
                'description': resource.description,
                'options': resource.options,
                'ownerId': resource.owner_id,
                'state': resource.state,
                'tagSet': resource.tag_set,
                'transitGatewayArn': resource.transit_gateway_arn,
                'transitGatewayId': resource.transit_gateway_id,
                },
            }

    def ModifyTransitGatewayVpcAttachment(self, params: Dict[str, Any]):
        """Modifies the specified VPC attachment."""

        error = self._require_params(params, ["TransitGatewayAttachmentId"])
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment, error = self._get_transit_gateway_vpc_attachment(attachment_id)
        if error:
            return error

        add_subnet_ids = params.get("AddSubnetIds.N", []) or []
        remove_subnet_ids = params.get("RemoveSubnetIds.N", []) or []
        vpc_id = attachment.get("vpcId")

        for subnet_id in add_subnet_ids:
            subnet = self.state.subnets.get(subnet_id)
            if not subnet:
                return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")
            if hasattr(subnet, "vpc_id") and subnet.vpc_id and subnet.vpc_id != vpc_id:
                return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")

        subnet_ids = list(attachment.get("subnetIds", []) or [])
        for subnet_id in add_subnet_ids:
            if subnet_id not in subnet_ids:
                subnet_ids.append(subnet_id)
        for subnet_id in remove_subnet_ids:
            if subnet_id in subnet_ids:
                subnet_ids.remove(subnet_id)

        options_input = params.get("Options") or {}
        if options_input:
            options = attachment.get("options", {})
            option_map = {
                "applianceModeSupport": ["ApplianceModeSupport", "applianceModeSupport"],
                "dnsSupport": ["DnsSupport", "dnsSupport"],
                "ipv6Support": ["Ipv6Support", "ipv6Support"],
                "securityGroupReferencingSupport": ["SecurityGroupReferencingSupport", "securityGroupReferencingSupport"],
            }
            for option_key, candidates in option_map.items():
                for candidate in candidates:
                    if candidate in options_input and options_input.get(candidate) is not None:
                        options[option_key] = options_input.get(candidate)
                        break
            attachment["options"] = options

        attachment["subnetIds"] = subnet_ids

        return {
            'transitGatewayVpcAttachment': {
                'creationTime': attachment.get("creationTime"),
                'options': attachment.get("options", {}),
                'state': attachment.get("state"),
                'subnetIds': attachment.get("subnetIds", []),
                'tagSet': attachment.get("tagSet", []),
                'transitGatewayAttachmentId': attachment.get("transitGatewayAttachmentId"),
                'transitGatewayId': attachment.get("transitGatewayId"),
                'vpcId': attachment.get("vpcId"),
                'vpcOwnerId': attachment.get("vpcOwnerId"),
                },
            }

    def RejectTransitGatewayVpcAttachment(self, params: Dict[str, Any]):
        """Rejects a request to attach a VPC to a transit gateway. The VPC attachment must be in thependingAcceptancestate.
         UseDescribeTransitGatewayVpcAttachmentsto view your pending VPC attachment requests.
         UseAcceptTransitGatewayVpcAttachmentto accept a VPC attachment request."""

        error = self._require_params(params, ["TransitGatewayAttachmentId"])
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        attachment, error = self._get_transit_gateway_vpc_attachment(attachment_id)
        if error:
            return error

        if attachment.get("state") == "pendingAcceptance":
            attachment["state"] = "rejected"

        return {
            'transitGatewayVpcAttachment': {
                'creationTime': attachment.get("creationTime"),
                'options': attachment.get("options", {}),
                'state': attachment.get("state"),
                'subnetIds': attachment.get("subnetIds", []),
                'tagSet': attachment.get("tagSet", []),
                'transitGatewayAttachmentId': attachment.get("transitGatewayAttachmentId"),
                'transitGatewayId': attachment.get("transitGatewayId"),
                'vpcId': attachment.get("vpcId"),
                'vpcOwnerId': attachment.get("vpcOwnerId"),
                },
            }

    def _generate_id(self, prefix: str = 'tgw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class transitgateway_RequestParser:
    @staticmethod
    def parse_accept_transit_gateway_vpc_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_create_transit_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_create_transit_gateway_vpc_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "SubnetIds.N": get_indexed_list(md, "SubnetIds"),
            "TagSpecifications.N": parse_tags(md, "TagSpecifications"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_vpc_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_describe_transit_gateway_attachments_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayAttachmentIds.N": get_indexed_list(md, "TransitGatewayAttachmentIds"),
        }

    @staticmethod
    def parse_describe_transit_gateways_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayIds.N": get_indexed_list(md, "TransitGatewayIds"),
        }

    @staticmethod
    def parse_describe_transit_gateway_vpc_attachments_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayAttachmentIds.N": get_indexed_list(md, "TransitGatewayAttachmentIds"),
        }

    @staticmethod
    def parse_modify_transit_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
        }

    @staticmethod
    def parse_modify_transit_gateway_vpc_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AddSubnetIds.N": get_indexed_list(md, "AddSubnetIds"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "RemoveSubnetIds.N": get_indexed_list(md, "RemoveSubnetIds"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_reject_transit_gateway_vpc_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AcceptTransitGatewayVpcAttachment": transitgateway_RequestParser.parse_accept_transit_gateway_vpc_attachment_request,
            "CreateTransitGateway": transitgateway_RequestParser.parse_create_transit_gateway_request,
            "CreateTransitGatewayVpcAttachment": transitgateway_RequestParser.parse_create_transit_gateway_vpc_attachment_request,
            "DeleteTransitGateway": transitgateway_RequestParser.parse_delete_transit_gateway_request,
            "DeleteTransitGatewayVpcAttachment": transitgateway_RequestParser.parse_delete_transit_gateway_vpc_attachment_request,
            "DescribeTransitGatewayAttachments": transitgateway_RequestParser.parse_describe_transit_gateway_attachments_request,
            "DescribeTransitGateways": transitgateway_RequestParser.parse_describe_transit_gateways_request,
            "DescribeTransitGatewayVpcAttachments": transitgateway_RequestParser.parse_describe_transit_gateway_vpc_attachments_request,
            "ModifyTransitGateway": transitgateway_RequestParser.parse_modify_transit_gateway_request,
            "ModifyTransitGatewayVpcAttachment": transitgateway_RequestParser.parse_modify_transit_gateway_vpc_attachment_request,
            "RejectTransitGatewayVpcAttachment": transitgateway_RequestParser.parse_reject_transit_gateway_vpc_attachment_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class transitgateway_ResponseSerializer:
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
                xml_parts.extend(transitgateway_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(transitgateway_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(transitgateway_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(transitgateway_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_accept_transit_gateway_vpc_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AcceptTransitGatewayVpcAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayVpcAttachment
        _transitGatewayVpcAttachment_key = None
        if "transitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "transitGatewayVpcAttachment"
        elif "TransitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "TransitGatewayVpcAttachment"
        if _transitGatewayVpcAttachment_key:
            param_data = data[_transitGatewayVpcAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayVpcAttachment>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayVpcAttachment>')
        xml_parts.append(f'</AcceptTransitGatewayVpcAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGateway
        _transitGateway_key = None
        if "transitGateway" in data:
            _transitGateway_key = "transitGateway"
        elif "TransitGateway" in data:
            _transitGateway_key = "TransitGateway"
        if _transitGateway_key:
            param_data = data[_transitGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGateway>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGateway>')
        xml_parts.append(f'</CreateTransitGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_vpc_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayVpcAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayVpcAttachment
        _transitGatewayVpcAttachment_key = None
        if "transitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "transitGatewayVpcAttachment"
        elif "TransitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "TransitGatewayVpcAttachment"
        if _transitGatewayVpcAttachment_key:
            param_data = data[_transitGatewayVpcAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayVpcAttachment>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayVpcAttachment>')
        xml_parts.append(f'</CreateTransitGatewayVpcAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGateway
        _transitGateway_key = None
        if "transitGateway" in data:
            _transitGateway_key = "transitGateway"
        elif "TransitGateway" in data:
            _transitGateway_key = "TransitGateway"
        if _transitGateway_key:
            param_data = data[_transitGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGateway>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGateway>')
        xml_parts.append(f'</DeleteTransitGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_vpc_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayVpcAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayVpcAttachment
        _transitGatewayVpcAttachment_key = None
        if "transitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "transitGatewayVpcAttachment"
        elif "TransitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "TransitGatewayVpcAttachment"
        if _transitGatewayVpcAttachment_key:
            param_data = data[_transitGatewayVpcAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayVpcAttachment>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayVpcAttachment>')
        xml_parts.append(f'</DeleteTransitGatewayVpcAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_attachments_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayAttachmentsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayAttachments
        _transitGatewayAttachments_key = None
        if "transitGatewayAttachments" in data:
            _transitGatewayAttachments_key = "transitGatewayAttachments"
        elif "TransitGatewayAttachments" in data:
            _transitGatewayAttachments_key = "TransitGatewayAttachments"
        if _transitGatewayAttachments_key:
            param_data = data[_transitGatewayAttachments_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayAttachmentsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayAttachmentsSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayAttachmentsSet/>')
        xml_parts.append(f'</DescribeTransitGatewayAttachmentsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateways_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewaysResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewaySet
        _transitGatewaySet_key = None
        if "transitGatewaySet" in data:
            _transitGatewaySet_key = "transitGatewaySet"
        elif "TransitGatewaySet" in data:
            _transitGatewaySet_key = "TransitGatewaySet"
        elif "TransitGateways" in data:
            _transitGatewaySet_key = "TransitGateways"
        if _transitGatewaySet_key:
            param_data = data[_transitGatewaySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewaySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewaySet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewaySet/>')
        xml_parts.append(f'</DescribeTransitGatewaysResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_vpc_attachments_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayVpcAttachmentsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayVpcAttachments
        _transitGatewayVpcAttachments_key = None
        if "transitGatewayVpcAttachments" in data:
            _transitGatewayVpcAttachments_key = "transitGatewayVpcAttachments"
        elif "TransitGatewayVpcAttachments" in data:
            _transitGatewayVpcAttachments_key = "TransitGatewayVpcAttachments"
        if _transitGatewayVpcAttachments_key:
            param_data = data[_transitGatewayVpcAttachments_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayVpcAttachmentsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayVpcAttachmentsSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayVpcAttachmentsSet/>')
        xml_parts.append(f'</DescribeTransitGatewayVpcAttachmentsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_transit_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyTransitGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGateway
        _transitGateway_key = None
        if "transitGateway" in data:
            _transitGateway_key = "transitGateway"
        elif "TransitGateway" in data:
            _transitGateway_key = "TransitGateway"
        if _transitGateway_key:
            param_data = data[_transitGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGateway>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGateway>')
        xml_parts.append(f'</ModifyTransitGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_transit_gateway_vpc_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyTransitGatewayVpcAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayVpcAttachment
        _transitGatewayVpcAttachment_key = None
        if "transitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "transitGatewayVpcAttachment"
        elif "TransitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "TransitGatewayVpcAttachment"
        if _transitGatewayVpcAttachment_key:
            param_data = data[_transitGatewayVpcAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayVpcAttachment>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayVpcAttachment>')
        xml_parts.append(f'</ModifyTransitGatewayVpcAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reject_transit_gateway_vpc_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RejectTransitGatewayVpcAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayVpcAttachment
        _transitGatewayVpcAttachment_key = None
        if "transitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "transitGatewayVpcAttachment"
        elif "TransitGatewayVpcAttachment" in data:
            _transitGatewayVpcAttachment_key = "TransitGatewayVpcAttachment"
        if _transitGatewayVpcAttachment_key:
            param_data = data[_transitGatewayVpcAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayVpcAttachment>')
            xml_parts.extend(transitgateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayVpcAttachment>')
        xml_parts.append(f'</RejectTransitGatewayVpcAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AcceptTransitGatewayVpcAttachment": transitgateway_ResponseSerializer.serialize_accept_transit_gateway_vpc_attachment_response,
            "CreateTransitGateway": transitgateway_ResponseSerializer.serialize_create_transit_gateway_response,
            "CreateTransitGatewayVpcAttachment": transitgateway_ResponseSerializer.serialize_create_transit_gateway_vpc_attachment_response,
            "DeleteTransitGateway": transitgateway_ResponseSerializer.serialize_delete_transit_gateway_response,
            "DeleteTransitGatewayVpcAttachment": transitgateway_ResponseSerializer.serialize_delete_transit_gateway_vpc_attachment_response,
            "DescribeTransitGatewayAttachments": transitgateway_ResponseSerializer.serialize_describe_transit_gateway_attachments_response,
            "DescribeTransitGateways": transitgateway_ResponseSerializer.serialize_describe_transit_gateways_response,
            "DescribeTransitGatewayVpcAttachments": transitgateway_ResponseSerializer.serialize_describe_transit_gateway_vpc_attachments_response,
            "ModifyTransitGateway": transitgateway_ResponseSerializer.serialize_modify_transit_gateway_response,
            "ModifyTransitGatewayVpcAttachment": transitgateway_ResponseSerializer.serialize_modify_transit_gateway_vpc_attachment_response,
            "RejectTransitGatewayVpcAttachment": transitgateway_ResponseSerializer.serialize_reject_transit_gateway_vpc_attachment_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

