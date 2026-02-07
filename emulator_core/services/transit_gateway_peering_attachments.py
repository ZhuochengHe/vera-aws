from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class State(Enum):
    INITIATING = "initiating"
    INITIATING_REQUEST = "initiatingRequest"
    PENDING_ACCEPTANCE = "pendingAcceptance"
    ROLLING_BACK = "rollingBack"
    PENDING = "pending"
    AVAILABLE = "available"
    MODIFYING = "modifying"
    DELETING = "deleting"
    DELETED = "deleted"
    FAILED = "failed"
    REJECTED = "rejected"
    REJECTING = "rejecting"
    FAILING = "failing"


class DynamicRouting(Enum):
    ENABLE = "enable"
    DISABLE = "disable"


@dataclass
class PeeringTgwInfo:
    coreNetworkId: Optional[str] = None
    ownerId: Optional[str] = None
    region: Optional[str] = None
    transitGatewayId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.coreNetworkId is not None:
            d["coreNetworkId"] = self.coreNetworkId
        if self.ownerId is not None:
            d["ownerId"] = self.ownerId
        if self.region is not None:
            d["region"] = self.region
        if self.transitGatewayId is not None:
            d["transitGatewayId"] = self.transitGatewayId
        return d


@dataclass
class TransitGatewayPeeringAttachmentOptions:
    dynamicRouting: Optional[DynamicRouting] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.dynamicRouting is not None:
            d["dynamicRouting"] = self.dynamicRouting.value
        return d


@dataclass
class PeeringAttachmentStatus:
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.code is not None:
            d["code"] = self.code
        if self.message is not None:
            d["message"] = self.message
        return d


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TransitGatewayPeeringAttachment:
    transitGatewayAttachmentId: str
    creationTime: datetime
    state: State
    requesterTgwInfo: PeeringTgwInfo
    accepterTgwInfo: PeeringTgwInfo
    options: TransitGatewayPeeringAttachmentOptions = field(default_factory=TransitGatewayPeeringAttachmentOptions)
    status: PeeringAttachmentStatus = field(default_factory=PeeringAttachmentStatus)
    tagSet: List[Tag] = field(default_factory=list)
    accepterTransitGatewayAttachmentId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "transitGatewayAttachmentId": self.transitGatewayAttachmentId,
            "creationTime": self.creationTime.isoformat(timespec='milliseconds') + "Z",
            "state": self.state.value,
            "requesterTgwInfo": self.requesterTgwInfo.to_dict(),
            "accepterTgwInfo": self.accepterTgwInfo.to_dict(),
            "options": self.options.to_dict(),
            "status": self.status.to_dict(),
            "tagSet": [tag.to_dict() for tag in self.tagSet],
        }
        if self.accepterTransitGatewayAttachmentId is not None:
            d["accepterTransitGatewayAttachmentId"] = self.accepterTransitGatewayAttachmentId
        return d


class TransitGatewayPeeringAttachmentBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.transit_gateway_peering_attachments dict for storage

    def _validate_tag_key(self, key: str):
        if key.lower().startswith("aws:"):
            raise ErrorCode.InvalidParameterValue(f"Tag key '{key}' may not begin with 'aws:'")

        if len(key) > 127:
            raise ErrorCode.InvalidParameterValue(f"Tag key '{key}' exceeds maximum length of 127 characters")

    def _validate_tag_value(self, value: str):
        if len(value) > 256:
            raise ErrorCode.InvalidParameterValue(f"Tag value '{value}' exceeds maximum length of 256 characters")

    def _parse_tags(self, tag_specifications: Optional[List[Dict[str, Any]]]) -> List[Tag]:
        tags: List[Tag] = []
        if not tag_specifications:
            return tags
        for tag_spec in tag_specifications:
            # Validate ResourceType if present (not strictly required here, but we check if present)
            resource_type = tag_spec.get("ResourceType")
            # We do not enforce resource type here because AWS allows many types, but we can skip if not transit-gateway-attachment
            # But since this is for transit gateway peering attachment, we only accept tags for this resource type or None
            # We'll accept tags anyway as AWS does not error on unknown resource types in tag spec for this API
            tag_list = tag_spec.get("Tags", [])
            if not isinstance(tag_list, list):
                raise ErrorCode.InvalidParameterValue("Tags must be a list")
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None or value is None:
                    raise ErrorCode.InvalidParameterValue("Tag must have both Key and Value")
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ErrorCode.InvalidParameterValue("Tag Key and Value must be strings")
                self._validate_tag_key(key)
                self._validate_tag_value(value)
                tags.append(Tag(Key=key, Value=value))
        return tags

    def _get_transit_gateway(self, tgw_id: str):
        # Use self.state.get_resource to get transit gateway resource
        tgw = self.state.get_resource(tgw_id)
        if tgw is None:
            raise ErrorCode.InvalidTransitGatewayID.NotFound(f"Transit Gateway {tgw_id} does not exist")
        return tgw

    def _get_transit_gateway_peering_attachment(self, attachment_id: str) -> TransitGatewayPeeringAttachment:
        tgwpa = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if tgwpa is None:
            raise ErrorCode.InvalidTransitGatewayAttachmentID.NotFound(f"Transit Gateway Attachment {attachment_id} does not exist")
        return tgwpa

    def _check_dry_run(self, params: Dict[str, Any]):
        dry_run = params.get("DryRun", False)
        if dry_run:
            # We simulate permission check success by raising DryRunOperation error
            raise ErrorCode.DryRunOperation()

    def create_transit_gateway_peering_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        peer_account_id = params.get("PeerAccountId")
        peer_region = params.get("PeerRegion")
        peer_tgw_id = params.get("PeerTransitGatewayId")
        transit_gateway_id = params.get("TransitGatewayId")
        options = params.get("Options", {})
        tag_specifications = params.get("TagSpecification.N", [])

        if peer_account_id is None or not isinstance(peer_account_id, str) or not peer_account_id.strip():
            raise ErrorCode.MissingParameter("PeerAccountId is required and must be a non-empty string")
        if peer_region is None or not isinstance(peer_region, str) or not peer_region.strip():
            raise ErrorCode.MissingParameter("PeerRegion is required and must be a non-empty string")
        if peer_tgw_id is None or not isinstance(peer_tgw_id, str) or not peer_tgw_id.strip():
            raise ErrorCode.MissingParameter("PeerTransitGatewayId is required and must be a non-empty string")
        if transit_gateway_id is None or not isinstance(transit_gateway_id, str) or not transit_gateway_id.strip():
            raise ErrorCode.MissingParameter("TransitGatewayId is required and must be a non-empty string")

        self._check_dry_run(params)

        # Validate transit gateways exist
        requester_tgw = self._get_transit_gateway(transit_gateway_id)
        accepter_tgw = self._get_transit_gateway(peer_tgw_id)

        # Validate options
        dynamic_routing_str = options.get("DynamicRouting")
        dynamic_routing_enum = None
        if dynamic_routing_str is not None:
            if dynamic_routing_str not in (DynamicRouting.ENABLE.value, DynamicRouting.DISABLE.value):
                raise ErrorCode.InvalidParameterValue(f"Invalid DynamicRouting value: {dynamic_routing_str}")
            dynamic_routing_enum = DynamicRouting(dynamic_routing_str)

        # Validate tags
        tags = self._parse_tags(tag_specifications)

        # Generate attachment ID and request ID
        attachment_id = f"tgw-attach-{self.generate_unique_id()}"
        request_id = self.generate_request_id()

        # Compose PeeringTgwInfo for requester and accepter
        requester_info = PeeringTgwInfo(
            ownerId=self.get_owner_id(),
            region=getattr(requester_tgw, "region", None),
            transitGatewayId=transit_gateway_id,
            coreNetworkId=None,
        )
        accepter_info = PeeringTgwInfo(
            ownerId=peer_account_id,
            region=peer_region,
            transitGatewayId=peer_tgw_id,
            coreNetworkId=None,
        )

        # Create the attachment object
        attachment = TransitGatewayPeeringAttachment(
            transitGatewayAttachmentId=attachment_id,
            creationTime=datetime.now(timezone.utc),
            state=State.INITIATING_REQUEST,
            requesterTgwInfo=requester_info,
            accepterTgwInfo=accepter_info,
            options=TransitGatewayPeeringAttachmentOptions(dynamicRouting=dynamic_routing_enum),
            status=PeeringAttachmentStatus(code="initiatingRequest", message="Transit gateway peering attachment is initiating request"),
            tagSet=tags,
            accepterTransitGatewayAttachmentId=None,
        )

        # Store in shared state dict
        self.state.transit_gateway_peering_attachments[attachment_id] = attachment

        return {
            "requestId": request_id,
            "transitGatewayPeeringAttachment": attachment.to_dict(),
        }

    def accept_transit_gateway_peering_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        if attachment_id is None or not isinstance(attachment_id, str) or not attachment_id.strip():
            raise ErrorCode.MissingParameter("TransitGatewayAttachmentId is required and must be a non-empty string")

        self._check_dry_run(params)

        attachment = self._get_transit_gateway_peering_attachment(attachment_id)

        # Only attachments in pendingAcceptance state can be accepted
        if attachment.state != State.PENDING_ACCEPTANCE:
            raise ErrorCode.InvalidTransitGatewayAttachmentState(f"Transit Gateway Attachment {attachment_id} is not in pendingAcceptance state")

        # Change state to available
        attachment.state = State.AVAILABLE
        attachment.status = PeeringAttachmentStatus(code="available", message="Transit gateway peering attachment is available")

        # Set accepterTransitGatewayAttachmentId to a generated ID (simulate accepter side attachment)
        accepter_attachment_id = f"tgw-attach-{self.generate_unique_id()}"
        attachment.accepterTransitGatewayAttachmentId = accepter_attachment_id

        # Update creationTime to now (simulate acceptance time)
        attachment.creationTime = datetime.now(timezone.utc)

        request_id = self.generate_request_id()

        return {
            "requestId": request_id,
            "transitGatewayPeeringAttachment": attachment.to_dict(),
        }

    def delete_transit_gateway_peering_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        if attachment_id is None or not isinstance(attachment_id, str) or not attachment_id.strip():
            raise ErrorCode.MissingParameter("TransitGatewayAttachmentId is required and must be a non-empty string")

        self._check_dry_run(params)

        attachment = self._get_transit_gateway_peering_attachment(attachment_id)

        # If already deleted, just return the attachment with deleted state
        if attachment.state == State.DELETED:
            request_id = self.generate_request_id()
            return {
                "requestId": request_id,
                "transitGatewayPeeringAttachment": attachment.to_dict(),
            }

        # Change state to deleting then deleted
        attachment.state = State.DELETING
        attachment.status = PeeringAttachmentStatus(code="deleting", message="Transit gateway peering attachment is deleting")

        # Simulate immediate deletion
        attachment.state = State.DELETED
        attachment.status = PeeringAttachmentStatus(code="deleted", message="Transit gateway peering attachment is deleted")

        request_id = self.generate_request_id()

        return {
            "requestId": request_id,
            "transitGatewayPeeringAttachment": attachment.to_dict(),
        }

    def describe_transit_gateway_peering_attachments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._check_dry_run(params)

        # Filters: Filter.N with Name and Values
        filters = params.get("Filter.N", [])
        # TransitGatewayAttachmentIds.N: list of IDs to filter by
        attachment_ids = params.get("TransitGatewayAttachmentIds.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate max_results if present
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode.InvalidParameterValue("MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode.InvalidParameterValue("MaxResults must be between 5 and 1000")

        # Collect all attachments
        attachments = list(self.state.transit_gateway_peering_attachments.values())

        # Filter by attachment IDs if provided
        if attachment_ids:
            attachments = [att for att in attachments if att.transitGatewayAttachmentId in attachment_ids]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            # Filter names are case-sensitive
            if name == "transit-gateway-attachment-id":
                attachments = [att for att in attachments if att.transitGatewayAttachmentId in values]
            elif name == "local-owner-id":
                attachments = [att for att in attachments if att.requesterTgwInfo.ownerId in values]
            elif name == "remote-owner-id":
                attachments = [att for att in attachments if att.accepterTgwInfo.ownerId in values]
            elif name == "state":
                # values are strings of states
                valid_states = set(s.value for s in State)
                for v in values:
                    if v not in valid_states:
                        raise ErrorCode.InvalidParameterValue(f"Invalid state filter value: {v}")
                attachments = [att for att in attachments if att.state.value in values]
            elif name.startswith("tag:"):
                tag_key = name[4:]
                attachments = [
                    att for att in attachments
                    if any(tag.Key == tag_key and tag.Value in values for tag in att.tagSet)
                ]
            elif name == "tag-key":
                attachments = [
                    att for att in attachments
                    if any(tag.Key in values for tag in att.tagSet)
                ]
            elif name == "transit-gateway-id":
                attachments = [
                    att for att in attachments
                    if att.requesterTgwInfo.transitGatewayId in values or att.accepterTgwInfo.transitGatewayId in values
                ]
            else:
                # Unknown filter name: ignore or raise? AWS ignores unknown filters silently
                pass

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken")

        end_index = start_index + max_results if max_results else None
        page = attachments[start_index:end_index]

        new_next_token = str(end_index) if end_index is not None and end_index < len(attachments) else None

        request_id = self.generate_request_id()

        return {
            "requestId": request_id,
            "transitGatewayPeeringAttachments": [att.to_dict() for att in page],
            "nextToken": new_next_token,
        }

    def reject_transit_gateway_peering_attachment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        attachment_id = params.get("TransitGatewayAttachmentId")
        if attachment_id is None or not isinstance(attachment_id, str) or not attachment_id.strip():
            raise ErrorCode.MissingParameter("TransitGatewayAttachmentId is required and must be a non-empty string")

        self._check_dry_run(params)

        attachment = self._get_transit_gateway_peering_attachment(attachment_id)

        # Only attachments in pendingAcceptance state can be rejected
        if attachment.state != State.PENDING_ACCEPTANCE:
            raise ErrorCode.InvalidTransitGatewayAttachmentState(f"Transit Gateway Attachment {attachment_id} is not in pendingAcceptance state")

        # Change state to rejected
        attachment.state = State.REJECTED
        attachment.status = PeeringAttachmentStatus(code="rejected", message="Transit gateway peering attachment request rejected")

        request_id = self.generate_request_id()

        return {
            "requestId": request_id,
            "transitGatewayPeeringAttachment": attachment.to_dict(),
        }

from emulator_core.gateway.base import BaseGateway

class TransitGatewayPeeringAttachmentsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptTransitGatewayPeeringAttachment", self.accept_transit_gateway_peering_attachment)
        self.register_action("CreateTransitGatewayPeeringAttachment", self.create_transit_gateway_peering_attachment)
        self.register_action("DeleteTransitGatewayPeeringAttachment", self.delete_transit_gateway_peering_attachment)
        self.register_action("DescribeTransitGatewayPeeringAttachments", self.describe_transit_gateway_peering_attachments)
        self.register_action("RejectTransitGatewayPeeringAttachment", self.reject_transit_gateway_peering_attachment)

    def accept_transit_gateway_peering_attachment(self, params):
        return self.backend.accept_transit_gateway_peering_attachment(params)

    def create_transit_gateway_peering_attachment(self, params):
        return self.backend.create_transit_gateway_peering_attachment(params)

    def delete_transit_gateway_peering_attachment(self, params):
        return self.backend.delete_transit_gateway_peering_attachment(params)

    def describe_transit_gateway_peering_attachments(self, params):
        return self.backend.describe_transit_gateway_peering_attachments(params)

    def reject_transit_gateway_peering_attachment(self, params):
        return self.backend.reject_transit_gateway_peering_attachment(params)
