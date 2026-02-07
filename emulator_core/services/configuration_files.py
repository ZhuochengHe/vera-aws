from typing import Dict, Any
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class ConfigurationFilesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.configuration_files dict for storage

    def export_client_vpn_client_configuration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter ClientVpnEndpointId
        if "ClientVpnEndpointId" not in params:
            raise ErrorCode("MissingParameter", "The request must contain the parameter ClientVpnEndpointId.")

        client_vpn_endpoint_id = params["ClientVpnEndpointId"]
        if not isinstance(client_vpn_endpoint_id, str) or not client_vpn_endpoint_id.strip():
            raise ErrorCode("InvalidParameterValue", "ClientVpnEndpointId must be a non-empty string.")

        # Validate optional DryRun parameter
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if specified.")

        # Check if the ClientVpnEndpoint resource exists
        client_vpn_endpoint = self.state.get_resource(client_vpn_endpoint_id)
        if client_vpn_endpoint is None:
            raise ErrorCode("InvalidClientVpnEndpointId.NotFound", f"The Client VPN endpoint ID '{client_vpn_endpoint_id}' does not exist.")

        # DryRun permission check simulation
        if dry_run:
            # Here we simulate permission check, assume user has permission
            # If no permission, raise ErrorCode("UnauthorizedOperation", ...)
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set.")

        # Generate the client configuration content
        # The example response shows a typical OpenVPN client config with embedded CA cert
        # We will simulate a config string with the endpoint id embedded
        client_configuration = (
            f"client\n"
            f"dev tun\n"
            f"proto udp\n"
            f"remote {client_vpn_endpoint_id}.clientvpn.us-east-1.amazonaws.com 443\n"
            f"remote-random-hostname\n"
            f"resolv-retry infinite\n"
            f"nobind\n"
            f"persist-key\n"
            f"persist-tun\n"
            f"remote-cert-tls server\n"
            f"cipher AES-256-CBC\n"
            f"verb 3\n"
            f"<ca>\n"
            f"-----BEGIN CERTIFICATE-----\n"
            f"EXAMPLECAgmgAwIBAgIJAOjnW3hL6o+7MA0GCSqGSIb3DQEBCwUAMBAxDEXAMPLE\n"
            f"-----END CERTIFICATE-----\n"
            f"\n"
            f"</ca>"
        )

        # Generate request ID
        request_id = self.generate_request_id()

        # Store the configuration file content in state for this endpoint id
        self.state.configuration_files[client_vpn_endpoint_id] = client_configuration

        return {
            "clientConfiguration": client_configuration,
            "requestId": request_id,
        }

from emulator_core.gateway.base import BaseGateway

class ConfigurationfilesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("ExportClientVpnClientConfiguration", self.export_client_vpn_client_configuration)

    def export_client_vpn_client_configuration(self, params):
        return self.backend.export_client_vpn_client_configuration(params)
