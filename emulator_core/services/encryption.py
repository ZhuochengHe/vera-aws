from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend

@dataclass
class EncryptionStatus:
    ebs_encryption_by_default: bool
    request_id: str
    sse_type: Optional[str] = None  # Valid values: sse-ebs | sse-kms | none

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "ebsEncryptionByDefault": self.ebs_encryption_by_default,
            "requestId": self.request_id,
        }
        if self.sse_type is not None:
            result["sseType"] = self.sse_type
        return result

@dataclass
class KmsKeyIdResponse:
    kms_key_id: str
    request_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kmsKeyId": self.kms_key_id,
            "requestId": self.request_id,
        }

@dataclass
class EbsEncryptionByDefaultResponse:
    ebs_encryption_by_default: bool
    request_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ebsEncryptionByDefault": self.ebs_encryption_by_default,
            "requestId": self.request_id,
        }

class EncryptionBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Store encryption by default status per region/account
        # Example structure: {region: bool}
        self._encryption_by_default: bool = False
        self._default_kms_key_id: Optional[str] = None

    def disable_ebs_encryption_by_default(self, params: dict) -> dict:
        # DryRun parameter check (not implemented: permission check simulation)
        dry_run = params.get("DryRun", False)
        if dry_run:
            # In a real implementation, would check permissions and raise DryRunOperation or UnauthorizedOperation
            # Here, just simulate success for DryRun
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        # Disable encryption by default
        self.state.encryption["ebs_encryption_by_default"] = False

        return EbsEncryptionByDefaultResponse(
            ebs_encryption_by_default=False,
            request_id=self.generate_request_id()
        ).to_dict()


    def enable_ebs_encryption_by_default(self, params: dict) -> dict:
        # DryRun parameter check
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        # Enable encryption by default
        self.state.encryption["ebs_encryption_by_default"] = True

        return EbsEncryptionByDefaultResponse(
            ebs_encryption_by_default=True,
            request_id=self.generate_request_id()
        ).to_dict()


    def get_ebs_default_kms_key_id(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        kms_key_id = self.state.encryption.get("default_kms_key_id")
        if not kms_key_id:
            # If no default KMS key id set, simulate AWS managed key ARN for the region/account
            region = self.state.region if hasattr(self.state, "region") else "us-east-1"
            account_id = self.get_owner_id()
            kms_key_id = f"arn:aws:kms:{region}:{account_id}:alias/aws/ebs"

        return KmsKeyIdResponse(
            kms_key_id=kms_key_id,
            request_id=self.generate_request_id()
        ).to_dict()


    def get_ebs_encryption_by_default(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        ebs_encryption_by_default = self.state.encryption.get("ebs_encryption_by_default", False)
        # sseType reserved for future use, valid values: sse-ebs | sse-kms | none
        # We simulate sse-kms if encryption by default is enabled, else none
        sse_type = "sse-kms" if ebs_encryption_by_default else "none"

        return EncryptionStatus(
            ebs_encryption_by_default=ebs_encryption_by_default,
            request_id=self.generate_request_id(),
            sse_type=sse_type
        ).to_dict()


    def modify_ebs_default_kms_key_id(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        kms_key_id = params.get("KmsKeyId")
        if not kms_key_id:
            # Required parameter missing
            return {
                "Error": {
                    "Code": "MissingParameter",
                    "Message": "The request must contain the parameter KmsKeyId."
                }
            }

        # Validate kms_key_id format minimally (must be non-empty string)
        if not isinstance(kms_key_id, str) or not kms_key_id.strip():
            return {
                "Error": {
                    "Code": "InvalidParameterValue",
                    "Message": "The parameter KmsKeyId is invalid."
                }
            }

        # Check if encryption by default is enabled, if not, error (AWS requires encryption enabled to set KMS key)
        if not self.state.encryption.get("ebs_encryption_by_default", False):
            return {
                "Error": {
                    "Code": "InvalidParameterCombination",
                    "Message": "Encryption by default must be enabled to modify the default KMS key."
                }
            }

        # Set the default KMS key id
        self.state.encryption["default_kms_key_id"] = kms_key_id

        return KmsKeyIdResponse(
            kms_key_id=kms_key_id,
            request_id=self.generate_request_id()
        ).to_dict()

    def reset_ebs_default_kms_key_id(self, params: dict) -> dict:
        dry_run = params.get("DryRun", False)
        # Check permissions if DryRun is True
        if dry_run:
            # In a real implementation, check permissions here
            # For emulator, assume permission granted and raise DryRunOperation error
            return {
                "__type": "DryRunOperation",
                "message": "Request would have succeeded, but DryRun flag is set."
            }
        # Reset the default KMS key ID to AWS managed key
        # AWS managed key ARN format for EBS is:
        # arn:aws:kms:<region>:<account-id>:alias/aws/ebs
        region = self.state.region
        account_id = self.get_owner_id()
        aws_managed_kms_key_arn = f"arn:aws:kms:{region}:{account_id}:alias/aws/ebs"
        self.state.encryption["default_kms_key_id"] = aws_managed_kms_key_arn
        request_id = self.generate_request_id()
        return {
            "kmsKeyId": aws_managed_kms_key_arn,
            "requestId": request_id,
        }

    

from emulator_core.gateway.base import BaseGateway

class EncryptionGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DisableEbsEncryptionByDefault", self.disable_ebs_encryption_by_default)
        self.register_action("EnableEbsEncryptionByDefault", self.enable_ebs_encryption_by_default)
        self.register_action("GetEbsDefaultKmsKeyId", self.get_ebs_default_kms_key_id)
        self.register_action("GetEbsEncryptionByDefault", self.get_ebs_encryption_by_default)
        self.register_action("ModifyEbsDefaultKmsKeyId", self.modify_ebs_default_kms_key_id)
        self.register_action("ResetEbsDefaultKmsKeyId", self.reset_ebs_default_kms_key_id)

    def disable_ebs_encryption_by_default(self, params):
        return self.backend.disable_ebs_encryption_by_default(params)

    def enable_ebs_encryption_by_default(self, params):
        return self.backend.enable_ebs_encryption_by_default(params)

    def get_ebs_default_kms_key_id(self, params):
        return self.backend.get_ebs_default_kms_key_id(params)

    def get_ebs_encryption_by_default(self, params):
        return self.backend.get_ebs_encryption_by_default(params)

    def modify_ebs_default_kms_key_id(self, params):
        return self.backend.modify_ebs_default_kms_key_id(params)

    def reset_ebs_default_kms_key_id(self, params):
        return self.backend.reset_ebs_default_kms_key_id(params)
