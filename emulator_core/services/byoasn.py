from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend


class AsnAssociationState(str, Enum):
    DISASSOCIATED = "disassociated"
    FAILED_DISASSOCIATION = "failed-disassociation"
    FAILED_ASSOCIATION = "failed-association"
    PENDING_DISASSOCIATION = "pending-disassociation"
    PENDING_ASSOCIATION = "pending-association"
    ASSOCIATED = "associated"


@dataclass
class AsnAssociation:
    asn: Optional[str] = None
    cidr: Optional[str] = None
    state: Optional[AsnAssociationState] = None
    statusMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asn": self.asn,
            "cidr": self.cidr,
            "state": self.state.value if self.state else None,
            "statusMessage": self.statusMessage,
        }


class IpamExternalResourceVerificationTokenState(str, Enum):
    CREATE_IN_PROGRESS = "create-in-progress"
    CREATE_COMPLETE = "create-complete"
    CREATE_FAILED = "create-failed"
    DELETE_IN_PROGRESS = "delete-in-progress"
    DELETE_COMPLETE = "delete-complete"
    DELETE_FAILED = "delete-failed"


class IpamExternalResourceVerificationTokenStatus(str, Enum):
    VALID = "valid"
    EXPIRED = "expired"


@dataclass
class Tag:
    Key: Optional[str] = None
    Value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Key": self.Key,
            "Value": self.Value,
        }


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
class IpamExternalResourceVerificationToken:
    ipamArn: Optional[str] = None
    ipamExternalResourceVerificationTokenArn: Optional[str] = None
    ipamExternalResourceVerificationTokenId: Optional[str] = None
    ipamId: Optional[str] = None
    ipamRegion: Optional[str] = None
    notAfter: Optional[datetime] = None
    state: Optional[IpamExternalResourceVerificationTokenState] = None
    status: Optional[IpamExternalResourceVerificationTokenStatus] = None
    tagSet: List[Tag] = field(default_factory=list)
    tokenName: Optional[str] = None
    tokenValue: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ipamArn": self.ipamArn,
            "ipamExternalResourceVerificationTokenArn": self.ipamExternalResourceVerificationTokenArn,
            "ipamExternalResourceVerificationTokenId": self.ipamExternalResourceVerificationTokenId,
            "ipamId": self.ipamId,
            "ipamRegion": self.ipamRegion,
            "notAfter": self.notAfter.isoformat() if self.notAfter else None,
            "state": self.state.value if self.state else None,
            "status": self.status.value if self.status else None,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
            "tokenName": self.tokenName,
            "tokenValue": self.tokenValue,
        }


class ByoasnState(str, Enum):
    DEPROVISIONED = "deprovisioned"
    FAILED_DEPROVISION = "failed-deprovision"
    FAILED_PROVISION = "failed-provision"
    PENDING_DEPROVISION = "pending-deprovision"
    PENDING_PROVISION = "pending-provision"
    PROVISIONED = "provisioned"


@dataclass
class Byoasn:
    asn: Optional[str] = None
    ipamId: Optional[str] = None
    state: Optional[ByoasnState] = None
    statusMessage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asn": self.asn,
            "ipamId": self.ipamId,
            "state": self.state.value if self.state else None,
            "statusMessage": self.statusMessage,
        }


@dataclass
class AsnAuthorizationContext:
    Message: str
    Signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Message": self.Message,
            "Signature": self.Signature,
        }


@dataclass
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Values": self.Values,
        }


class BYOASNBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)

    def associate_ipam_byoasn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        asn = params.get("Asn")
        cidr = params.get("Cidr")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not asn:
            raise ValueError("Asn is required")
        if not cidr:
            raise ValueError("Cidr is required")

        # Find existing association by asn and cidr
        for assoc in self.state.byoasn.values():
            if assoc.asn == asn and assoc.state is not None:
                # If already associated with this cidr, return existing association
                if assoc.state.name == "associated" and assoc.ipamId is not None:
                    return {
                        "asnAssociation": {
                            "asn": assoc.asn,
                            "cidr": cidr,
                            "state": assoc.state.name,
                            "statusMessage": assoc.statusMessage,
                        },
                        "requestId": self.generate_request_id(),
                    }

        # Create new association
        # Use asn+cidr as key for uniqueness
        assoc_id = f"{asn}:{cidr}"
        from enum import Enum

        # Define states enum for AsnAssociationState if not defined
        # But per instructions, use Enum members, assume AsnAssociationState has members
        # We'll simulate with strings here as placeholder
        # But per instructions, use Enum members, so assume AsnAssociationState.ASSOCIATED etc.

        # For this implementation, assume AsnAssociationState has members:
        # ASSOCIATED, DISASSOCIATED, FAILED_ASSOCIATION, FAILED_DISASSOCIATION, PENDING_ASSOCIATION, PENDING_DISASSOCIATION

        # We'll create a new AsnAssociation object
        # But the class AsnAssociation has asn, cidr, state, statusMessage

        # For state, assign AsnAssociationState.ASSOCIATED
        # For statusMessage, assign None or "Association successful"

        # Since we don't have actual Enum members, we will assign string "associated" per the doc
        # But instructions say to use Enum members, so assume AsnAssociationState.ASSOCIATED

        # We'll check if AsnAssociationState has ASSOCIATED member
        # If not, fallback to string "associated"

        try:
            state_enum = AsnAssociationState.ASSOCIATED
        except Exception:
            state_enum = "associated"

        association = AsnAssociation()
        association.asn = asn
        association.cidr = cidr
        association.state = state_enum
        association.statusMessage = "Association successful"

        self.state.byoasn[assoc_id] = association

        return {
            "asnAssociation": {
                "asn": association.asn,
                "cidr": association.cidr,
                "state": association.state.name if hasattr(association.state, "name") else association.state,
                "statusMessage": association.statusMessage,
            },
            "requestId": self.generate_request_id(),
        }


    def create_ipam_external_resource_verification_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        dry_run = params.get("DryRun", False)
        ipam_id = params.get("IpamId")
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not ipam_id:
            raise ValueError("IpamId is required")

        # Generate unique token id and arn
        token_id = self.generate_unique_id()
        token_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:ipam-external-resource-verification-token/{token_id}"
        ipam_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:ipam/{ipam_id}"
        ipam_region = self.state.region

        from datetime import datetime, timedelta
        not_after = datetime.utcnow() + timedelta(days=7)  # Token valid for 7 days

        # State and status enums
        try:
            state_enum = IpamExternalResourceVerificationTokenState.CREATE_COMPLETE
        except Exception:
            state_enum = "create-complete"
        try:
            status_enum = IpamExternalResourceVerificationTokenStatus.VALID
        except Exception:
            status_enum = "valid"

        # Process tags from tag_specifications
        tags = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with ResourceType and Tags
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                tag = Tag()
                tag.Key = tag_dict.get("Key")
                tag.Value = tag_dict.get("Value")
                tags.append(tag)

        token = IpamExternalResourceVerificationToken()
        token.ipamArn = ipam_arn
        token.ipamExternalResourceVerificationTokenArn = token_arn
        token.ipamExternalResourceVerificationTokenId = token_id
        token.ipamId = ipam_id
        token.ipamRegion = ipam_region
        token.notAfter = not_after
        token.state = state_enum
        token.status = status_enum
        token.tagSet = tags
        token.tokenName = None
        token.tokenValue = token_id  # For simplicity, tokenValue is token_id

        self.state.resources[token_id] = token

        return {
            "ipamExternalResourceVerificationToken": token.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_ipam_external_resource_verification_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        token_id = params.get("IpamExternalResourceVerificationTokenId")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not token_id:
            raise ValueError("IpamExternalResourceVerificationTokenId is required")

        token = self.state.resources.get(token_id)
        if not token or not isinstance(token, IpamExternalResourceVerificationToken):
            raise ValueError(f"Verification token with id {token_id} not found")

        # Mark token as deleted
        try:
            token.state = IpamExternalResourceVerificationTokenState.DELETE_COMPLETE
        except Exception:
            token.state = "delete-complete"
        try:
            token.status = IpamExternalResourceVerificationTokenStatus.EXPIRED
        except Exception:
            token.status = "expired"

        # Remove from resources
        del self.state.resources[token_id]

        return {
            "ipamExternalResourceVerificationToken": token.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def deprovision_ipam_byoasn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        asn = params.get("Asn")
        dry_run = params.get("DryRun", False)
        ipam_id = params.get("IpamId")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not asn:
            raise ValueError("Asn is required")
        if not ipam_id:
            raise ValueError("IpamId is required")

        # Find the byoasn by asn and ipam_id
        byoasn_obj = None
        for byoasn in self.state.byoasn.values():
            if byoasn.asn == asn and byoasn.ipamId == ipam_id:
                byoasn_obj = byoasn
                break

        if not byoasn_obj:
            # Create a new byoasn object with deprovisioned state
            byoasn_obj = Byoasn()
            byoasn_obj.asn = asn
            byoasn_obj.ipamId = ipam_id

        # Check if any BYOIP CIDR associations exist for this ASN
        # We check self.state.byoasn for any associations with this asn and state associated
        for assoc in self.state.byoasn.values():
            if assoc.asn == asn and assoc.state is not None:
                # If any association exists, cannot deprovision
                raise ValueError("Cannot deprovision ASN with existing BYOIP CIDR associations. Remove associations first.")

        # Set state to deprovisioned
        try:
            byoasn_obj.state = ByoasnState.DEPROVISIONED
        except Exception:
            byoasn_obj.state = "deprovisioned"
        byoasn_obj.statusMessage = "ASN deprovisioned successfully"

        # Store/update in state
        key = f"{asn}:{ipam_id}"
        self.state.byoasn[key] = byoasn_obj

        return {
            "byoasn": {
                "asn": byoasn_obj.asn,
                "ipamId": byoasn_obj.ipamId,
                "state": byoasn_obj.state.name if hasattr(byoasn_obj.state, "name") else byoasn_obj.state,
                "statusMessage": byoasn_obj.statusMessage,
            },
            "requestId": self.generate_request_id(),
        }


    def describe_ipam_byoasn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ValueError("MaxResults must be an integer")
            if max_results < 1 or max_results > 100:
                raise ValueError("MaxResults must be between 1 and 100")

        # Convert byoasn dict to list sorted by asn for consistent pagination
        byoasn_list = sorted(self.state.byoasn.values(), key=lambda x: (x.asn or "", x.ipamId or ""))

        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ValueError("Invalid NextToken")

        end_index = len(byoasn_list)
        if max_results is not None:
            end_index = min(start_index + max_results, len(byoasn_list))

        result_byoasn = byoasn_list[start_index:end_index]

        # Prepare response list
        byoasn_set = []
        for byoasn_obj in result_byoasn:
            byoasn_set.append(
                {
                    "asn": byoasn_obj.asn,
                    "ipamId": byoasn_obj.ipamId,
                    "state": byoasn_obj.state.name if hasattr(byoasn_obj.state, "name") else byoasn_obj.state,
                    "statusMessage": byoasn_obj.statusMessage,
                }
            )

        new_next_token = None
        if end_index < len(byoasn_list):
            new_next_token = str(end_index)

        return {
            "byoasnSet": byoasn_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def describe_ipam_external_resource_verification_tokens(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters
        filters = params.get("Filter", [])
        token_ids = params.get("IpamExternalResourceVerificationTokenId", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate MaxResults if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Normalize filters to list of Filter objects if dicts
        normalized_filters = []
        for f in filters:
            if isinstance(f, dict):
                name = f.get("Name")
                values = f.get("Values", [])
                normalized_filters.append(Filter(Name=name, Values=values))
            elif isinstance(f, Filter):
                normalized_filters.append(f)
            else:
                raise ValueError("Filter must be a dict or Filter object")

        # Collect all tokens from state
        all_tokens = list(self.state.ipam_external_resource_verification_tokens.values())

        # Filter by token IDs if provided
        if token_ids:
            all_tokens = [t for t in all_tokens if t.ipamExternalResourceVerificationTokenId in token_ids]

        # Apply filters
        def token_matches_filter(token: IpamExternalResourceVerificationToken, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if not name or not values:
                return True
            # Map filter names to token attributes
            attr_map = {
                "ipam-arn": token.ipamArn,
                "ipam-external-resource-verification-token-arn": token.ipamExternalResourceVerificationTokenArn,
                "ipam-external-resource-verification-token-id": token.ipamExternalResourceVerificationTokenId,
                "ipam-id": token.ipamId,
                "ipam-region": token.ipamRegion,
                "state": token.state.name if token.state else None,
                "status": token.status.name if token.status else None,
                "token-name": token.tokenName,
                "token-value": token.tokenValue,
            }
            attr_value = attr_map.get(name)
            if attr_value is None:
                return False
            return any(attr_value == v for v in values)

        for f in normalized_filters:
            all_tokens = [t for t in all_tokens if token_matches_filter(t, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else None
        paged_tokens = all_tokens[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index is not None and end_index < len(all_tokens):
            new_next_token = str(end_index)

        # Build response token dicts
        token_dicts = [t.to_dict() for t in paged_tokens]

        return {
            "ipamExternalResourceVerificationTokenSet": token_dicts,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def disassociate_ipam_byoasn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        asn = params.get("Asn")
        cidr = params.get("Cidr")

        if not asn:
            raise ValueError("Asn is required")
        if not cidr:
            raise ValueError("Cidr is required")

        # Find the association in state.byoasn associations
        # Associations are stored in self.state.byoasn_associations or similar? 
        # But we only have self.state.byoasn (dict keyed by asn?), so we must find association by asn and cidr
        # The problem statement does not specify a separate associations dict, so we assume associations are stored in self.state.byoasn_associations keyed by (asn, cidr) or similar
        # Since no such dict is specified, we must assume self.state.byoasn_associations exists or we must create it
        # But instructions say always use self.state.byoasn (plural) dict for BYOASN resources
        # So likely associations are stored in self.state.byoasn_associations or self.state.byoasn_associations dict
        # Since no such dict is specified, we must assume associations are stored in self.state.byoasn_associations keyed by (asn, cidr)
        # For safety, we check self.state.byoasn_associations dict for the association

        # Let's assume self.state.byoasn_associations is a dict keyed by (asn, cidr) tuple
        # If not found, create a new AsnAssociation with state disassociated

        # If self.state.byoasn_associations does not exist, create it
        if not hasattr(self.state, "byoasn_associations"):
            self.state.byoasn_associations = {}

        key = (asn, cidr)
        association = self.state.byoasn_associations.get(key)

        if association is None:
            # Create a new association with state disassociated
            association = AsnAssociation()
            association.asn = asn
            association.cidr = cidr
            # Set state to disassociated enum member
            # We must find the enum member for disassociated state
            # Assuming AsnAssociationState enum has member DISASSOCIATED
            # If not, fallback to string "disassociated"
            try:
                association.state = AsnAssociationState.DISASSOCIATED
            except Exception:
                association.state = "disassociated"
            association.statusMessage = "Association disassociated"
            self.state.byoasn_associations[key] = association
        else:
            # Update existing association state to disassociated
            try:
                association.state = AsnAssociationState.DISASSOCIATED
            except Exception:
                association.state = "disassociated"
            association.statusMessage = "Association disassociated"

        return {
            "asnAssociation": association.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def provision_ipam_byoasn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        asn = params.get("Asn")
        auth_context = params.get("AsnAuthorizationContext")
        ipam_id = params.get("IpamId")

        if not asn:
            raise ValueError("Asn is required")
        if not auth_context or not isinstance(auth_context, dict):
            raise ValueError("AsnAuthorizationContext is required and must be a dict")
        if not ipam_id:
            raise ValueError("IpamId is required")

        message = auth_context.get("Message")
        signature = auth_context.get("Signature")
        if not message:
            raise ValueError("AsnAuthorizationContext.Message is required")
        if not signature:
            raise ValueError("AsnAuthorizationContext.Signature is required")

        # Check if BYOASN already exists for this ASN
        byoasn = self.state.byoasn.get(asn)
        if byoasn is None:
            byoasn = Byoasn()
            byoasn.asn = asn
            byoasn.ipamId = ipam_id
            # Set state to pending-provision
            try:
                byoasn.state = ByoasnState.PENDING_PROVISION
            except Exception:
                byoasn.state = "pending-provision"
            byoasn.statusMessage = "Provisioning in progress"
            self.state.byoasn[asn] = byoasn
        else:
            # Update existing byoasn
            byoasn.ipamId = ipam_id
            try:
                byoasn.state = ByoasnState.PENDING_PROVISION
            except Exception:
                byoasn.state = "pending-provision"
            byoasn.statusMessage = "Provisioning in progress"

        # For emulator, we can simulate immediate provisioning success
        try:
            byoasn.state = ByoasnState.PROVISIONED
        except Exception:
            byoasn.state = "provisioned"
        byoasn.statusMessage = "Provisioned successfully"

        return {
            "byoasn": byoasn.to_dict(),
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class BYOASNGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateIpamByoasn", self.associate_ipam_byoasn)
        self.register_action("CreateIpamExternalResourceVerificationToken", self.create_ipam_external_resource_verification_token)
        self.register_action("DeleteIpamExternalResourceVerificationToken", self.delete_ipam_external_resource_verification_token)
        self.register_action("DeprovisionIpamByoasn", self.deprovision_ipam_byoasn)
        self.register_action("DescribeIpamByoasn", self.describe_ipam_byoasn)
        self.register_action("DescribeIpamExternalResourceVerificationTokens", self.describe_ipam_external_resource_verification_tokens)
        self.register_action("DisassociateIpamByoasn", self.disassociate_ipam_byoasn)
        self.register_action("ProvisionIpamByoasn", self.provision_ipam_byoasn)

    def associate_ipam_byoasn(self, params):
        return self.backend.associate_ipam_byoasn(params)

    def create_ipam_external_resource_verification_token(self, params):
        return self.backend.create_ipam_external_resource_verification_token(params)

    def delete_ipam_external_resource_verification_token(self, params):
        return self.backend.delete_ipam_external_resource_verification_token(params)

    def deprovision_ipam_byoasn(self, params):
        return self.backend.deprovision_ipam_byoasn(params)

    def describe_ipam_byoasn(self, params):
        return self.backend.describe_ipam_byoasn(params)

    def describe_ipam_external_resource_verification_tokens(self, params):
        return self.backend.describe_ipam_external_resource_verification_tokens(params)

    def disassociate_ipam_byoasn(self, params):
        return self.backend.disassociate_ipam_byoasn(params)

    def provision_ipam_byoasn(self, params):
        return self.backend.provision_ipam_byoasn(params)
