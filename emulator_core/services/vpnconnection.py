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
class VpnConnection:
    category: str = ""
    core_network_arn: str = ""
    core_network_attachment_arn: str = ""
    customer_gateway_configuration: str = ""
    customer_gateway_id: str = ""
    gateway_association_state: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    pre_shared_key_arn: str = ""
    routes: List[Any] = field(default_factory=list)
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    transit_gateway_id: str = ""
    type: str = ""
    vgw_telemetry: List[Any] = field(default_factory=list)
    vpn_concentrator_id: str = ""
    vpn_connection_id: str = ""
    vpn_gateway_id: str = ""

    active_tunnel_statuses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tunnel_replacement_statuses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tunnel_certificate_arns: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "coreNetworkArn": self.core_network_arn,
            "coreNetworkAttachmentArn": self.core_network_attachment_arn,
            "customerGatewayConfiguration": self.customer_gateway_configuration,
            "customerGatewayId": self.customer_gateway_id,
            "gatewayAssociationState": self.gateway_association_state,
            "options": self.options,
            "preSharedKeyArn": self.pre_shared_key_arn,
            "routes": self.routes,
            "state": self.state,
            "tagSet": self.tag_set,
            "transitGatewayId": self.transit_gateway_id,
            "type": self.type,
            "vgwTelemetry": self.vgw_telemetry,
            "vpnConcentratorId": self.vpn_concentrator_id,
            "vpnConnectionId": self.vpn_connection_id,
            "vpnGatewayId": self.vpn_gateway_id,
        }

class VpnConnection_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.vpn_connections  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.customer_gateways.get(params['customer_gateway_id']).vpn_connection_ids.append(new_id)
    #   Delete: self.state.customer_gateways.get(resource.customer_gateway_id).vpn_connection_ids.remove(resource_id)
    #   Create: self.state.transit_gateways.get(params['transit_gateway_id']).vpn_connection_ids.append(new_id)
    #   Delete: self.state.transit_gateways.get(resource.transit_gateway_id).vpn_connection_ids.remove(resource_id)
    #   Create: self.state.vpn_concentrators.get(params['vpn_concentrator_id']).vpn_connection_ids.append(new_id)
    #   Delete: self.state.vpn_concentrators.get(resource.vpn_concentrator_id).vpn_connection_ids.remove(resource_id)
    #   Create: self.state.virtual_private_gateways.get(params['vpn_gateway_id']).vpn_connection_ids.append(new_id)
    #   Delete: self.state.virtual_private_gateways.get(resource.vpn_gateway_id).vpn_connection_ids.remove(resource_id)

    def _validate_required_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            if not params.get(key):
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _get_vpn_connection(self, vpn_connection_id: str) -> (Optional[VpnConnection], Optional[Dict[str, Any]]):
        resource = self.resources.get(vpn_connection_id)
        if not resource:
            return None, create_error_response(
                "InvalidVpnConnectionID.NotFound",
                f"The VPN connection '{vpn_connection_id}' does not exist."
            )
        return resource, None

    def _register_with_parents(self, resource_id: str, resource: VpnConnection) -> None:
        if resource.customer_gateway_id:
            parent = self.state.customer_gateways.get(resource.customer_gateway_id)
            if parent and hasattr(parent, "vpn_connection_ids"):
                parent.vpn_connection_ids.append(resource_id)
        if resource.transit_gateway_id:
            parent = self.state.transit_gateways.get(resource.transit_gateway_id)
            if parent and hasattr(parent, "vpn_connection_ids"):
                parent.vpn_connection_ids.append(resource_id)
        if resource.vpn_concentrator_id:
            parent = self.state.vpn_concentrators.get(resource.vpn_concentrator_id)
            if parent and hasattr(parent, "vpn_connection_ids"):
                parent.vpn_connection_ids.append(resource_id)
        if resource.vpn_gateway_id:
            parent = self.state.virtual_private_gateways.get(resource.vpn_gateway_id)
            if parent and hasattr(parent, "vpn_connection_ids"):
                parent.vpn_connection_ids.append(resource_id)

    def _deregister_from_parents(self, resource_id: str, resource: VpnConnection) -> None:
        if resource.customer_gateway_id:
            parent = self.state.customer_gateways.get(resource.customer_gateway_id)
            if parent and hasattr(parent, "vpn_connection_ids") and resource_id in parent.vpn_connection_ids:
                parent.vpn_connection_ids.remove(resource_id)
        if resource.transit_gateway_id:
            parent = self.state.transit_gateways.get(resource.transit_gateway_id)
            if parent and hasattr(parent, "vpn_connection_ids") and resource_id in parent.vpn_connection_ids:
                parent.vpn_connection_ids.remove(resource_id)
        if resource.vpn_concentrator_id:
            parent = self.state.vpn_concentrators.get(resource.vpn_concentrator_id)
            if parent and hasattr(parent, "vpn_connection_ids") and resource_id in parent.vpn_connection_ids:
                parent.vpn_connection_ids.remove(resource_id)
        if resource.vpn_gateway_id:
            parent = self.state.virtual_private_gateways.get(resource.vpn_gateway_id)
            if parent and hasattr(parent, "vpn_connection_ids") and resource_id in parent.vpn_connection_ids:
                parent.vpn_connection_ids.remove(resource_id)

    def _get_or_init_tunnel_status(self, resource: VpnConnection, outside_ip: str) -> Dict[str, Any]:
        status = resource.active_tunnel_statuses.get(outside_ip)
        if not status:
            status = {
                "ikeVersion": None,
                "phase1DHGroup": None,
                "phase1EncryptionAlgorithm": None,
                "phase1IntegrityAlgorithm": None,
                "phase2DHGroup": None,
                "phase2EncryptionAlgorithm": None,
                "phase2IntegrityAlgorithm": None,
                "provisioningStatus": None,
                "provisioningStatusReason": None,
            }
            resource.active_tunnel_statuses[outside_ip] = status
        return status

    def _get_or_init_replacement_status(self, resource: VpnConnection, outside_ip: str) -> Dict[str, Any]:
        status = resource.tunnel_replacement_statuses.get(outside_ip)
        if not status:
            status = {
                "lastMaintenanceApplied": None,
                "maintenanceAutoAppliedAfter": None,
                "pendingMaintenance": None,
            }
            resource.tunnel_replacement_statuses[outside_ip] = status
        return status

    def CreateVpnConnection(self, params: Dict[str, Any]):
        """Creates a VPN connection between an existing virtual private gateway or transit
            gateway and a customer gateway. The supported connection type isipsec.1. The response includes information that you need to give to your network administrator
            to configure your customer gateway. W"""

        error = self._validate_required_params(params, ["CustomerGatewayId", "Type"])
        if error:
            return error

        customer_gateway_id = params.get("CustomerGatewayId")
        if not self.state.customer_gateways.get(customer_gateway_id):
            return create_error_response(
                "InvalidCustomerGatewayID.NotFound",
                f"Customer gateway '{customer_gateway_id}' does not exist."
            )

        transit_gateway_id = params.get("TransitGatewayId") or ""
        vpn_gateway_id = params.get("VpnGatewayId") or ""
        vpn_concentrator_id = params.get("VpnConcentratorId") or ""
        if not (transit_gateway_id or vpn_gateway_id or vpn_concentrator_id):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: TransitGatewayId or VpnGatewayId or VpnConcentratorId"
            )
        if transit_gateway_id and not self.state.transit_gateways.get(transit_gateway_id):
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"Transit Gateway '{transit_gateway_id}' does not exist."
            )
        if vpn_gateway_id and not self.state.virtual_private_gateways.get(vpn_gateway_id):
            return create_error_response(
                "InvalidVpnGatewayID.NotFound",
                f"VPN gateway '{vpn_gateway_id}' does not exist."
            )
        if vpn_concentrator_id and not self.state.vpn_concentrators.get(vpn_concentrator_id):
            return create_error_response(
                "InvalidVpnConcentratorID.NotFound",
                f"VPN concentrator '{vpn_concentrator_id}' does not exist."
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        vpn_connection_id = self._generate_id("vpn")
        gateway_association_state = "associated" if (transit_gateway_id or vpn_gateway_id or vpn_concentrator_id) else ""
        resource = VpnConnection(
            customer_gateway_id=customer_gateway_id,
            options=params.get("Options") or {},
            pre_shared_key_arn=params.get("PreSharedKeyStorage") or "",
            routes=[],
            state=ResourceState.AVAILABLE.value,
            tag_set=tag_set,
            transit_gateway_id=transit_gateway_id,
            type=params.get("Type") or "",
            vgw_telemetry=[],
            vpn_concentrator_id=vpn_concentrator_id,
            vpn_connection_id=vpn_connection_id,
            vpn_gateway_id=vpn_gateway_id,
            gateway_association_state=gateway_association_state,
        )
        self.resources[vpn_connection_id] = resource
        self._register_with_parents(vpn_connection_id, resource)

        return {
            'vpnConnection': resource.to_dict(),
            }

    def CreateVpnConnectionRoute(self, params: Dict[str, Any]):
        """Creates a static route associated with a VPN connection between an existing virtual
            private gateway and a VPN customer gateway. The static route allows traffic to be routed
            from the virtual private gateway to the VPN customer gateway. For more information, seeAWS Site-to-Site"""

        error = self._validate_required_params(params, ["DestinationCidrBlock", "VpnConnectionId"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        destination_cidr = params.get("DestinationCidrBlock")
        existing = next(
            (route for route in resource.routes if route.get("destinationCidrBlock") == destination_cidr),
            None,
        )
        if not existing:
            resource.routes.append({
                "destinationCidrBlock": destination_cidr,
                "source": "static",
                "state": "available",
            })

        return {
            'return': True,
            }

    def DeleteVpnConnection(self, params: Dict[str, Any]):
        """Deletes the specified VPN connection. If you're deleting the VPC and its associated components, we recommend that you detach
            the virtual private gateway from the VPC and delete the VPC before deleting the VPN
            connection. If you believe that the tunnel credentials for your VPN"""

        error = self._validate_required_params(params, ["VpnConnectionId"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        self._deregister_from_parents(vpn_connection_id, resource)
        del self.resources[vpn_connection_id]

        return {
            'return': True,
            }

    def DeleteVpnConnectionRoute(self, params: Dict[str, Any]):
        """Deletes the specified static route associated with a VPN connection between an
            existing virtual private gateway and a VPN customer gateway. The static route allows
            traffic to be routed from the virtual private gateway to the VPN customer
            gateway."""

        error = self._validate_required_params(params, ["DestinationCidrBlock", "VpnConnectionId"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        destination_cidr = params.get("DestinationCidrBlock")
        resource.routes = [
            route for route in resource.routes
            if route.get("destinationCidrBlock") != destination_cidr
        ]

        return {
            'return': True,
            }

    def DescribeVpnConnections(self, params: Dict[str, Any]):
        """Describes one or more of your VPN connections. For more information, seeAWS Site-to-Site VPNin theAWS Site-to-Site VPN
                User Guide."""

        vpn_connection_ids = params.get("VpnConnectionId.N", []) or []
        if vpn_connection_ids:
            resources: List[VpnConnection] = []
            for vpn_connection_id in vpn_connection_ids:
                resource = self.resources.get(vpn_connection_id)
                if not resource:
                    return create_error_response(
                        "InvalidVpnConnectionID.NotFound",
                        f"The ID '{vpn_connection_id}' does not exist"
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        filtered = apply_filters(resources, params.get("Filter.N", []) or [])
        return {
            'vpnConnectionSet': [resource.to_dict() for resource in filtered],
            }

    def GetActiveVpnTunnelStatus(self, params: Dict[str, Any]):
        """Returns the currently negotiated security parameters for an active VPN tunnel, including IKE version, DH groups, encryption algorithms, and integrity algorithms."""

        error = self._validate_required_params(params, ["VpnConnectionId", "VpnTunnelOutsideIpAddress"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        outside_ip = params.get("VpnTunnelOutsideIpAddress")
        status = self._get_or_init_tunnel_status(resource, outside_ip)

        return {
            'activeVpnTunnelStatus': dict(status),
            }

    def GetVpnConnectionDeviceSampleConfiguration(self, params: Dict[str, Any]):
        """Download an AWS-provided sample configuration file to be used with the customer
            gateway device specified for your Site-to-Site VPN connection."""

        error = self._validate_required_params(params, ["VpnConnectionDeviceTypeId", "VpnConnectionId"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        device_type_id = params.get("VpnConnectionDeviceTypeId")
        ike_version = params.get("InternetKeyExchangeVersion") or ""
        sample_type = params.get("SampleType") or ""
        config_text = (
            f"Sample configuration for {vpn_connection_id} ({resource.type or 'ipsec.1'}) "
            f"device {device_type_id} {ike_version} {sample_type}".strip()
        )

        return {
            'vpnConnectionDeviceSampleConfiguration': config_text,
            }

    def GetVpnConnectionDeviceTypes(self, params: Dict[str, Any]):
        """Obtain a list of customer gateway devices for which sample configuration
            files can be provided. The request has no additional parameters. You can also see the
            list of device types with sample configuration files available underYour customer gateway
                devicein th"""

        device_types = [
            {
                "platform": "generic",
                "software": "any",
                "vendor": "aws",
                "vpnConnectionDeviceTypeId": "device-1",
            },
            {
                "platform": "generic",
                "software": "any",
                "vendor": "aws",
                "vpnConnectionDeviceTypeId": "device-2",
            },
        ]

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = int(next_token or 0)
        end_index = start_index + max_results
        items = device_types[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(device_types) else None

        return {
            'nextToken': new_next_token,
            'vpnConnectionDeviceTypeSet': items,
            }

    def GetVpnTunnelReplacementStatus(self, params: Dict[str, Any]):
        """Get details of available tunnel endpoint maintenance."""

        error = self._validate_required_params(params, ["VpnConnectionId", "VpnTunnelOutsideIpAddress"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        outside_ip = params.get("VpnTunnelOutsideIpAddress")
        maintenance = self._get_or_init_replacement_status(resource, outside_ip)

        return {
            'customerGatewayId': resource.customer_gateway_id,
            'maintenanceDetails': dict(maintenance),
            'transitGatewayId': resource.transit_gateway_id,
            'vpnConnectionId': resource.vpn_connection_id,
            'vpnGatewayId': resource.vpn_gateway_id,
            'vpnTunnelOutsideIpAddress': outside_ip,
            }

    def ModifyVpnConnection(self, params: Dict[str, Any]):
        """Modifies the customer gateway or the target gateway of an AWS Site-to-Site VPN connection. To
            modify the target gateway, the following migration options are available: An existing virtual private gateway to a new virtual private gateway An existing virtual private gateway to a transit ga"""

        error = self._validate_required_params(params, ["VpnConnectionId"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        new_customer_gateway_id = params.get("CustomerGatewayId") or ""
        if new_customer_gateway_id and not self.state.customer_gateways.get(new_customer_gateway_id):
            return create_error_response(
                "InvalidCustomerGatewayID.NotFound",
                f"Customer gateway '{new_customer_gateway_id}' does not exist."
            )

        new_transit_gateway_id = params.get("TransitGatewayId") or ""
        if new_transit_gateway_id and not self.state.transit_gateways.get(new_transit_gateway_id):
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"Transit Gateway '{new_transit_gateway_id}' does not exist."
            )

        new_vpn_gateway_id = params.get("VpnGatewayId") or ""
        if new_vpn_gateway_id and not self.state.virtual_private_gateways.get(new_vpn_gateway_id):
            return create_error_response(
                "InvalidVpnGatewayID.NotFound",
                f"VPN gateway '{new_vpn_gateway_id}' does not exist."
            )

        if new_customer_gateway_id and new_customer_gateway_id != resource.customer_gateway_id:
            old_parent = self.state.customer_gateways.get(resource.customer_gateway_id)
            if old_parent and hasattr(old_parent, "vpn_connection_ids") and vpn_connection_id in old_parent.vpn_connection_ids:
                old_parent.vpn_connection_ids.remove(vpn_connection_id)
            resource.customer_gateway_id = new_customer_gateway_id
            new_parent = self.state.customer_gateways.get(new_customer_gateway_id)
            if new_parent and hasattr(new_parent, "vpn_connection_ids"):
                new_parent.vpn_connection_ids.append(vpn_connection_id)

        if new_transit_gateway_id and new_transit_gateway_id != resource.transit_gateway_id:
            old_parent = self.state.transit_gateways.get(resource.transit_gateway_id)
            if old_parent and hasattr(old_parent, "vpn_connection_ids") and vpn_connection_id in old_parent.vpn_connection_ids:
                old_parent.vpn_connection_ids.remove(vpn_connection_id)
            resource.transit_gateway_id = new_transit_gateway_id
            new_parent = self.state.transit_gateways.get(new_transit_gateway_id)
            if new_parent and hasattr(new_parent, "vpn_connection_ids"):
                new_parent.vpn_connection_ids.append(vpn_connection_id)

        if new_vpn_gateway_id and new_vpn_gateway_id != resource.vpn_gateway_id:
            old_parent = self.state.virtual_private_gateways.get(resource.vpn_gateway_id)
            if old_parent and hasattr(old_parent, "vpn_connection_ids") and vpn_connection_id in old_parent.vpn_connection_ids:
                old_parent.vpn_connection_ids.remove(vpn_connection_id)
            resource.vpn_gateway_id = new_vpn_gateway_id
            new_parent = self.state.virtual_private_gateways.get(new_vpn_gateway_id)
            if new_parent and hasattr(new_parent, "vpn_connection_ids"):
                new_parent.vpn_connection_ids.append(vpn_connection_id)

        return {
            'vpnConnection': resource.to_dict(),
            }

    def ModifyVpnConnectionOptions(self, params: Dict[str, Any]):
        """Modifies the connection options for your Site-to-Site VPN connection. When you modify the VPN connection options, the VPN endpoint IP addresses on the
                AWS side do not change, and the tunnel options do not change. Your
            VPN connection will be temporarily unavailable for a b"""

        error = self._validate_required_params(params, ["VpnConnectionId"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        if not resource.options:
            resource.options = {}
        if params.get("LocalIpv4NetworkCidr"):
            resource.options["localIpv4NetworkCidr"] = params.get("LocalIpv4NetworkCidr")
        if params.get("LocalIpv6NetworkCidr"):
            resource.options["localIpv6NetworkCidr"] = params.get("LocalIpv6NetworkCidr")
        if params.get("RemoteIpv4NetworkCidr"):
            resource.options["remoteIpv4NetworkCidr"] = params.get("RemoteIpv4NetworkCidr")
        if params.get("RemoteIpv6NetworkCidr"):
            resource.options["remoteIpv6NetworkCidr"] = params.get("RemoteIpv6NetworkCidr")

        return {
            'vpnConnection': resource.to_dict(),
            }

    def ModifyVpnTunnelCertificate(self, params: Dict[str, Any]):
        """Modifies the VPN tunnel endpoint certificate."""

        error = self._validate_required_params(params, ["VpnConnectionId", "VpnTunnelOutsideIpAddress"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        outside_ip = params.get("VpnTunnelOutsideIpAddress")
        resource.tunnel_certificate_arns[outside_ip] = resource.tunnel_certificate_arns.get(outside_ip) or ""

        return {
            'vpnConnection': resource.to_dict(),
            }

    def ModifyVpnTunnelOptions(self, params: Dict[str, Any]):
        """Modifies the options for a VPN tunnel in an AWS Site-to-Site VPN connection. You can modify
            multiple options for a tunnel in a single request, but you can only modify one tunnel at
            a time. For more information, seeSite-to-Site VPN tunnel options for your Site-to-Site VPN
    """

        error = self._validate_required_params(
            params,
            ["TunnelOptions", "VpnConnectionId", "VpnTunnelOutsideIpAddress"],
        )
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        tunnel_options = params.get("TunnelOptions") or {}
        outside_ip = params.get("VpnTunnelOutsideIpAddress")

        if not resource.options:
            resource.options = {}
        tunnel_option_set = resource.options.get("tunnelOptionSet") or []
        existing = next(
            (item for item in tunnel_option_set if item.get("outsideIpAddress") == outside_ip),
            None,
        )
        if existing:
            existing.update(tunnel_options)
        else:
            new_entry = dict(tunnel_options)
            new_entry.setdefault("outsideIpAddress", outside_ip)
            tunnel_option_set.append(new_entry)
        resource.options["tunnelOptionSet"] = tunnel_option_set

        pre_shared_key = params.get("PreSharedKeyStorage")
        if pre_shared_key:
            resource.pre_shared_key_arn = pre_shared_key

        return {
            'vpnConnection': resource.to_dict(),
            }

    def ReplaceVpnTunnel(self, params: Dict[str, Any]):
        """Trigger replacement of specified VPN tunnel."""

        error = self._validate_required_params(params, ["VpnConnectionId", "VpnTunnelOutsideIpAddress"])
        if error:
            return error

        vpn_connection_id = params.get("VpnConnectionId")
        resource, error = self._get_vpn_connection(vpn_connection_id)
        if error:
            return error

        outside_ip = params.get("VpnTunnelOutsideIpAddress")
        maintenance = self._get_or_init_replacement_status(resource, outside_ip)
        if str2bool(params.get("ApplyPendingMaintenance")):
            maintenance["lastMaintenanceApplied"] = datetime.now(timezone.utc).isoformat()
            maintenance["pendingMaintenance"] = None
        else:
            maintenance["pendingMaintenance"] = "replacement-requested"

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'vpn') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class vpnconnection_RequestParser:
    @staticmethod
    def parse_create_vpn_connection_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CustomerGatewayId": get_scalar(md, "CustomerGatewayId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "PreSharedKeyStorage": get_scalar(md, "PreSharedKeyStorage"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
            "Type": get_scalar(md, "Type"),
            "VpnConcentratorId": get_scalar(md, "VpnConcentratorId"),
            "VpnGatewayId": get_scalar(md, "VpnGatewayId"),
        }

    @staticmethod
    def parse_create_vpn_connection_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
        }

    @staticmethod
    def parse_delete_vpn_connection_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
        }

    @staticmethod
    def parse_delete_vpn_connection_route_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": get_scalar(md, "DestinationCidrBlock"),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
        }

    @staticmethod
    def parse_describe_vpn_connections_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "VpnConnectionId.N": get_indexed_list(md, "VpnConnectionId"),
        }

    @staticmethod
    def parse_get_active_vpn_tunnel_status_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
            "VpnTunnelOutsideIpAddress": get_indexed_list(md, "VpnTunnelOutsideIpAddress"),
        }

    @staticmethod
    def parse_get_vpn_connection_device_sample_configuration_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InternetKeyExchangeVersion": get_scalar(md, "InternetKeyExchangeVersion"),
            "SampleType": get_scalar(md, "SampleType"),
            "VpnConnectionDeviceTypeId": get_scalar(md, "VpnConnectionDeviceTypeId"),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
        }

    @staticmethod
    def parse_get_vpn_connection_device_types_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_vpn_tunnel_replacement_status_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
            "VpnTunnelOutsideIpAddress": get_indexed_list(md, "VpnTunnelOutsideIpAddress"),
        }

    @staticmethod
    def parse_modify_vpn_connection_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CustomerGatewayId": get_scalar(md, "CustomerGatewayId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
            "VpnGatewayId": get_scalar(md, "VpnGatewayId"),
        }

    @staticmethod
    def parse_modify_vpn_connection_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalIpv4NetworkCidr": get_scalar(md, "LocalIpv4NetworkCidr"),
            "LocalIpv6NetworkCidr": get_scalar(md, "LocalIpv6NetworkCidr"),
            "RemoteIpv4NetworkCidr": get_scalar(md, "RemoteIpv4NetworkCidr"),
            "RemoteIpv6NetworkCidr": get_scalar(md, "RemoteIpv6NetworkCidr"),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
        }

    @staticmethod
    def parse_modify_vpn_tunnel_certificate_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
            "VpnTunnelOutsideIpAddress": get_indexed_list(md, "VpnTunnelOutsideIpAddress"),
        }

    @staticmethod
    def parse_modify_vpn_tunnel_options_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PreSharedKeyStorage": get_scalar(md, "PreSharedKeyStorage"),
            "SkipTunnelReplacement": get_scalar(md, "SkipTunnelReplacement"),
            "TunnelOptions": get_scalar(md, "TunnelOptions"),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
            "VpnTunnelOutsideIpAddress": get_indexed_list(md, "VpnTunnelOutsideIpAddress"),
        }

    @staticmethod
    def parse_replace_vpn_tunnel_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ApplyPendingMaintenance": get_scalar(md, "ApplyPendingMaintenance"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VpnConnectionId": get_scalar(md, "VpnConnectionId"),
            "VpnTunnelOutsideIpAddress": get_indexed_list(md, "VpnTunnelOutsideIpAddress"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateVpnConnection": vpnconnection_RequestParser.parse_create_vpn_connection_request,
            "CreateVpnConnectionRoute": vpnconnection_RequestParser.parse_create_vpn_connection_route_request,
            "DeleteVpnConnection": vpnconnection_RequestParser.parse_delete_vpn_connection_request,
            "DeleteVpnConnectionRoute": vpnconnection_RequestParser.parse_delete_vpn_connection_route_request,
            "DescribeVpnConnections": vpnconnection_RequestParser.parse_describe_vpn_connections_request,
            "GetActiveVpnTunnelStatus": vpnconnection_RequestParser.parse_get_active_vpn_tunnel_status_request,
            "GetVpnConnectionDeviceSampleConfiguration": vpnconnection_RequestParser.parse_get_vpn_connection_device_sample_configuration_request,
            "GetVpnConnectionDeviceTypes": vpnconnection_RequestParser.parse_get_vpn_connection_device_types_request,
            "GetVpnTunnelReplacementStatus": vpnconnection_RequestParser.parse_get_vpn_tunnel_replacement_status_request,
            "ModifyVpnConnection": vpnconnection_RequestParser.parse_modify_vpn_connection_request,
            "ModifyVpnConnectionOptions": vpnconnection_RequestParser.parse_modify_vpn_connection_options_request,
            "ModifyVpnTunnelCertificate": vpnconnection_RequestParser.parse_modify_vpn_tunnel_certificate_request,
            "ModifyVpnTunnelOptions": vpnconnection_RequestParser.parse_modify_vpn_tunnel_options_request,
            "ReplaceVpnTunnel": vpnconnection_RequestParser.parse_replace_vpn_tunnel_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class vpnconnection_ResponseSerializer:
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
                xml_parts.extend(vpnconnection_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(vpnconnection_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(vpnconnection_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(vpnconnection_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_vpn_connection_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpnConnectionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConnection
        _vpnConnection_key = None
        if "vpnConnection" in data:
            _vpnConnection_key = "vpnConnection"
        elif "VpnConnection" in data:
            _vpnConnection_key = "VpnConnection"
        if _vpnConnection_key:
            param_data = data[_vpnConnection_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConnection>')
            xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpnConnection>')
        xml_parts.append(f'</CreateVpnConnectionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_vpn_connection_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVpnConnectionRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CreateVpnConnectionRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpn_connection_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpnConnectionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteVpnConnectionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_vpn_connection_route_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVpnConnectionRouteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteVpnConnectionRouteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_vpn_connections_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVpnConnectionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConnectionSet
        _vpnConnectionSet_key = None
        if "vpnConnectionSet" in data:
            _vpnConnectionSet_key = "vpnConnectionSet"
        elif "VpnConnectionSet" in data:
            _vpnConnectionSet_key = "VpnConnectionSet"
        elif "VpnConnections" in data:
            _vpnConnectionSet_key = "VpnConnections"
        if _vpnConnectionSet_key:
            param_data = data[_vpnConnectionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpnConnectionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpnConnectionSet>')
            else:
                xml_parts.append(f'{indent_str}<vpnConnectionSet/>')
        xml_parts.append(f'</DescribeVpnConnectionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_active_vpn_tunnel_status_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetActiveVpnTunnelStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize activeVpnTunnelStatus
        _activeVpnTunnelStatus_key = None
        if "activeVpnTunnelStatus" in data:
            _activeVpnTunnelStatus_key = "activeVpnTunnelStatus"
        elif "ActiveVpnTunnelStatus" in data:
            _activeVpnTunnelStatus_key = "ActiveVpnTunnelStatus"
        if _activeVpnTunnelStatus_key:
            param_data = data[_activeVpnTunnelStatus_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<activeVpnTunnelStatusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</activeVpnTunnelStatusSet>')
            else:
                xml_parts.append(f'{indent_str}<activeVpnTunnelStatusSet/>')
        xml_parts.append(f'</GetActiveVpnTunnelStatusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_vpn_connection_device_sample_configuration_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetVpnConnectionDeviceSampleConfigurationResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConnectionDeviceSampleConfiguration
        _vpnConnectionDeviceSampleConfiguration_key = None
        if "vpnConnectionDeviceSampleConfiguration" in data:
            _vpnConnectionDeviceSampleConfiguration_key = "vpnConnectionDeviceSampleConfiguration"
        elif "VpnConnectionDeviceSampleConfiguration" in data:
            _vpnConnectionDeviceSampleConfiguration_key = "VpnConnectionDeviceSampleConfiguration"
        if _vpnConnectionDeviceSampleConfiguration_key:
            param_data = data[_vpnConnectionDeviceSampleConfiguration_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConnectionDeviceSampleConfiguration>{esc(str(param_data))}</vpnConnectionDeviceSampleConfiguration>')
        xml_parts.append(f'</GetVpnConnectionDeviceSampleConfigurationResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_vpn_connection_device_types_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetVpnConnectionDeviceTypesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize vpnConnectionDeviceTypeSet
        _vpnConnectionDeviceTypeSet_key = None
        if "vpnConnectionDeviceTypeSet" in data:
            _vpnConnectionDeviceTypeSet_key = "vpnConnectionDeviceTypeSet"
        elif "VpnConnectionDeviceTypeSet" in data:
            _vpnConnectionDeviceTypeSet_key = "VpnConnectionDeviceTypeSet"
        elif "VpnConnectionDeviceTypes" in data:
            _vpnConnectionDeviceTypeSet_key = "VpnConnectionDeviceTypes"
        if _vpnConnectionDeviceTypeSet_key:
            param_data = data[_vpnConnectionDeviceTypeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpnConnectionDeviceTypeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</vpnConnectionDeviceTypeSet>')
            else:
                xml_parts.append(f'{indent_str}<vpnConnectionDeviceTypeSet/>')
        xml_parts.append(f'</GetVpnConnectionDeviceTypesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_vpn_tunnel_replacement_status_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetVpnTunnelReplacementStatusResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize customerGatewayId
        _customerGatewayId_key = None
        if "customerGatewayId" in data:
            _customerGatewayId_key = "customerGatewayId"
        elif "CustomerGatewayId" in data:
            _customerGatewayId_key = "CustomerGatewayId"
        if _customerGatewayId_key:
            param_data = data[_customerGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<customerGatewayId>{esc(str(param_data))}</customerGatewayId>')
        # Serialize maintenanceDetails
        _maintenanceDetails_key = None
        if "maintenanceDetails" in data:
            _maintenanceDetails_key = "maintenanceDetails"
        elif "MaintenanceDetails" in data:
            _maintenanceDetails_key = "MaintenanceDetails"
        if _maintenanceDetails_key:
            param_data = data[_maintenanceDetails_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<maintenanceDetailsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</maintenanceDetailsSet>')
            else:
                xml_parts.append(f'{indent_str}<maintenanceDetailsSet/>')
        # Serialize transitGatewayId
        _transitGatewayId_key = None
        if "transitGatewayId" in data:
            _transitGatewayId_key = "transitGatewayId"
        elif "TransitGatewayId" in data:
            _transitGatewayId_key = "TransitGatewayId"
        if _transitGatewayId_key:
            param_data = data[_transitGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayId>{esc(str(param_data))}</transitGatewayId>')
        # Serialize vpnConnectionId
        _vpnConnectionId_key = None
        if "vpnConnectionId" in data:
            _vpnConnectionId_key = "vpnConnectionId"
        elif "VpnConnectionId" in data:
            _vpnConnectionId_key = "VpnConnectionId"
        if _vpnConnectionId_key:
            param_data = data[_vpnConnectionId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConnectionId>{esc(str(param_data))}</vpnConnectionId>')
        # Serialize vpnGatewayId
        _vpnGatewayId_key = None
        if "vpnGatewayId" in data:
            _vpnGatewayId_key = "vpnGatewayId"
        elif "VpnGatewayId" in data:
            _vpnGatewayId_key = "VpnGatewayId"
        if _vpnGatewayId_key:
            param_data = data[_vpnGatewayId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnGatewayId>{esc(str(param_data))}</vpnGatewayId>')
        # Serialize vpnTunnelOutsideIpAddress
        _vpnTunnelOutsideIpAddress_key = None
        if "vpnTunnelOutsideIpAddress" in data:
            _vpnTunnelOutsideIpAddress_key = "vpnTunnelOutsideIpAddress"
        elif "VpnTunnelOutsideIpAddress" in data:
            _vpnTunnelOutsideIpAddress_key = "VpnTunnelOutsideIpAddress"
        if _vpnTunnelOutsideIpAddress_key:
            param_data = data[_vpnTunnelOutsideIpAddress_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<vpnTunnelOutsideIpAddressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</vpnTunnelOutsideIpAddressSet>')
            else:
                xml_parts.append(f'{indent_str}<vpnTunnelOutsideIpAddressSet/>')
        xml_parts.append(f'</GetVpnTunnelReplacementStatusResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpn_connection_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpnConnectionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConnection
        _vpnConnection_key = None
        if "vpnConnection" in data:
            _vpnConnection_key = "vpnConnection"
        elif "VpnConnection" in data:
            _vpnConnection_key = "VpnConnection"
        if _vpnConnection_key:
            param_data = data[_vpnConnection_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConnection>')
            xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpnConnection>')
        xml_parts.append(f'</ModifyVpnConnectionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpn_connection_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpnConnectionOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConnection
        _vpnConnection_key = None
        if "vpnConnection" in data:
            _vpnConnection_key = "vpnConnection"
        elif "VpnConnection" in data:
            _vpnConnection_key = "VpnConnection"
        if _vpnConnection_key:
            param_data = data[_vpnConnection_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConnection>')
            xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpnConnection>')
        xml_parts.append(f'</ModifyVpnConnectionOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpn_tunnel_certificate_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpnTunnelCertificateResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConnection
        _vpnConnection_key = None
        if "vpnConnection" in data:
            _vpnConnection_key = "vpnConnection"
        elif "VpnConnection" in data:
            _vpnConnection_key = "VpnConnection"
        if _vpnConnection_key:
            param_data = data[_vpnConnection_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConnection>')
            xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpnConnection>')
        xml_parts.append(f'</ModifyVpnTunnelCertificateResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_vpn_tunnel_options_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVpnTunnelOptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize vpnConnection
        _vpnConnection_key = None
        if "vpnConnection" in data:
            _vpnConnection_key = "vpnConnection"
        elif "VpnConnection" in data:
            _vpnConnection_key = "VpnConnection"
        if _vpnConnection_key:
            param_data = data[_vpnConnection_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<vpnConnection>')
            xml_parts.extend(vpnconnection_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</vpnConnection>')
        xml_parts.append(f'</ModifyVpnTunnelOptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_replace_vpn_tunnel_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReplaceVpnTunnelResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ReplaceVpnTunnelResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateVpnConnection": vpnconnection_ResponseSerializer.serialize_create_vpn_connection_response,
            "CreateVpnConnectionRoute": vpnconnection_ResponseSerializer.serialize_create_vpn_connection_route_response,
            "DeleteVpnConnection": vpnconnection_ResponseSerializer.serialize_delete_vpn_connection_response,
            "DeleteVpnConnectionRoute": vpnconnection_ResponseSerializer.serialize_delete_vpn_connection_route_response,
            "DescribeVpnConnections": vpnconnection_ResponseSerializer.serialize_describe_vpn_connections_response,
            "GetActiveVpnTunnelStatus": vpnconnection_ResponseSerializer.serialize_get_active_vpn_tunnel_status_response,
            "GetVpnConnectionDeviceSampleConfiguration": vpnconnection_ResponseSerializer.serialize_get_vpn_connection_device_sample_configuration_response,
            "GetVpnConnectionDeviceTypes": vpnconnection_ResponseSerializer.serialize_get_vpn_connection_device_types_response,
            "GetVpnTunnelReplacementStatus": vpnconnection_ResponseSerializer.serialize_get_vpn_tunnel_replacement_status_response,
            "ModifyVpnConnection": vpnconnection_ResponseSerializer.serialize_modify_vpn_connection_response,
            "ModifyVpnConnectionOptions": vpnconnection_ResponseSerializer.serialize_modify_vpn_connection_options_response,
            "ModifyVpnTunnelCertificate": vpnconnection_ResponseSerializer.serialize_modify_vpn_tunnel_certificate_response,
            "ModifyVpnTunnelOptions": vpnconnection_ResponseSerializer.serialize_modify_vpn_tunnel_options_response,
            "ReplaceVpnTunnel": vpnconnection_ResponseSerializer.serialize_replace_vpn_tunnel_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

