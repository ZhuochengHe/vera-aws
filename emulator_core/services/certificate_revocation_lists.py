from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode, ResourceState


@dataclass
class ClientCertificateRevocationListStatus:
    code: Optional[str] = None  # "pending" or "active"
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.code is not None:
            d["code"] = self.code
        if self.message is not None:
            d["message"] = self.message
        return d


@dataclass
class CertificateRevocationList:
    client_vpn_endpoint_id: str
    certificate_revocation_list: str
    status: ClientCertificateRevocationListStatus = field(
        default_factory=lambda: ClientCertificateRevocationListStatus(code="active")
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificateRevocationList": self.certificate_revocation_list,
            "status": self.status.to_dict(),
        }


class CertificateRevocationListsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.certificate_revocation_lists dict for storage

    def _validate_dry_run(self, params: Dict[str, Any]) -> None:
        # DryRun validation helper
        dry_run = params.get("DryRun")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")
            if dry_run:
                # Check permissions - for emulator, assume always allowed
                # Raise DryRunOperation error to simulate AWS behavior
                raise ErrorCode.DryRunOperation()

    def ExportClientVpnClientCertificateRevocationList(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Validate required parameters
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")
        if not isinstance(client_vpn_endpoint_id, str) or not client_vpn_endpoint_id.strip():
            raise ErrorCode.InvalidParameterValue("ClientVpnEndpointId must be a non-empty string")

        self._validate_dry_run(params)

        # Validate ClientVpnEndpointId exists
        client_vpn_endpoint = self.state.get_resource(client_vpn_endpoint_id)
        if client_vpn_endpoint is None:
            raise ErrorCode.ClientVpnEndpointNotFound(f"ClientVpnEndpoint {client_vpn_endpoint_id} does not exist")

        # Retrieve CRL for this ClientVpnEndpointId
        crl_obj = self.state.certificate_revocation_lists.get(client_vpn_endpoint_id)
        if crl_obj is None:
            # If no CRL uploaded yet, AWS returns empty string and status pending
            crl_obj = CertificateRevocationList(
                client_vpn_endpoint_id=client_vpn_endpoint_id,
                certificate_revocation_list="",
                status=ClientCertificateRevocationListStatus(code="pending"),
            )

        request_id = self.generate_request_id()

        return {
            "certificateRevocationList": crl_obj.certificate_revocation_list,
            "requestId": request_id,
            "status": crl_obj.status.to_dict(),
        }

    def ImportClientVpnClientCertificateRevocationList(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Validate required parameters
        certificate_revocation_list = params.get("CertificateRevocationList")
        if certificate_revocation_list is None:
            raise ErrorCode.MissingParameter("CertificateRevocationList is required")
        if not isinstance(certificate_revocation_list, str) or not certificate_revocation_list.strip():
            raise ErrorCode.InvalidParameterValue("CertificateRevocationList must be a non-empty string")

        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")
        if not isinstance(client_vpn_endpoint_id, str) or not client_vpn_endpoint_id.strip():
            raise ErrorCode.InvalidParameterValue("ClientVpnEndpointId must be a non-empty string")

        self._validate_dry_run(params)

        # Validate ClientVpnEndpointId exists
        client_vpn_endpoint = self.state.get_resource(client_vpn_endpoint_id)
        if client_vpn_endpoint is None:
            raise ErrorCode.ClientVpnEndpointNotFound(f"ClientVpnEndpoint {client_vpn_endpoint_id} does not exist")

        # Overwrite existing CRL or create new
        crl_obj = CertificateRevocationList(
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            certificate_revocation_list=certificate_revocation_list,
            status=ClientCertificateRevocationListStatus(code="active"),
        )
        self.state.certificate_revocation_lists[client_vpn_endpoint_id] = crl_obj

        request_id = self.generate_request_id()

        return {
            "requestId": request_id,
            "return": True,
        }

from emulator_core.gateway.base import BaseGateway

class CertificaterevocationlistsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("ExportClientVpnClientCertificateRevocationList", self.export_client_vpn_client_certificate_revocation_list)
        self.register_action("ImportClientVpnClientCertificateRevocationList", self.import_client_vpn_client_certificate_revocation_list)

    def export_client_vpn_client_certificate_revocation_list(self, params):
        return self.backend.export_client_vpn_client_certificate_revocation_list(params)

    def import_client_vpn_client_certificate_revocation_list(self, params):
        return self.backend.import_client_vpn_client_certificate_revocation_list(params)
