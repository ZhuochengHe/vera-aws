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
class TransitGatewayPeeringAttachment:
    accepter_tgw_info: Dict[str, Any] = field(default_factory=dict)
    accepter_transit_gateway_attachment_id: str = ""
    creation_time: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    requester_tgw_info: Dict[str, Any] = field(default_factory=dict)
    state: str = ""
    status: Dict[str, Any] = field(default_factory=dict)
    tag_set: List[Any] = field(default_factory=list)
    transit_gateway_attachment_id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "accepterTgwInfo": self.accepter_tgw_info,
            "accepterTransitGatewayAttachmentId": self.accepter_transit_gateway_attachment_id,
            "creationTime": self.creation_time,
            "options": self.options,
            "requesterTgwInfo": self.requester_tgw_info,
            "state": self.state,
            "status": self.status,
            "tagSet": self.tag_set,
            "transitGatewayAttachmentId": self.transit_gateway_attachment_id,
        }

class TransitGatewayPeeringAttachment_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.transit_gateway_peering_attachments  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.transit_gateway_connect.get(params['transit_gateway_attachment_id']).transit_gateway_peering_attachment_ids.append(new_id)
    #   Delete: self.state.transit_gateway_connect.get(resource.transit_gateway_attachment_id).transit_gateway_peering_attachment_ids.remove(resource_id)


    def _get_peering_attachment(self, attachment_id: str) -> Optional[TransitGatewayPeeringAttachment]:
        if not attachment_id:
            return None
        return self.resources.get(attachment_id)

    def _get_peering_attachment_or_error(self, attachment_id: str):
        resource = self._get_peering_attachment(attachment_id)
        if not resource:
            return None, create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )
        return resource, None

    def AcceptTransitGatewayPeeringAttachment(self, params: Dict[str, Any]):
        """Accepts a transit gateway peering attachment request. The peering attachment must be
            in thependingAcceptancestate."""

        if not params.get("TransitGatewayAttachmentId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: TransitGatewayAttachmentId",
            )

        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        resource, error = self._get_peering_attachment_or_error(transit_gateway_attachment_id)
        if error:
            return error

        if resource.state != "pendingAcceptance":
            return create_error_response(
                "InvalidStateTransition",
                "Transit gateway peering attachment must be in pendingAcceptance state",
            )

        resource.state = "available"
        resource.status = {"code": "available", "message": "Available"}
        if not resource.accepter_transit_gateway_attachment_id:
            resource.accepter_transit_gateway_attachment_id = self._generate_id("tgw-attach")

        return {
            'transitGatewayPeeringAttachment': resource.to_dict(),
            }

    def CreateTransitGatewayPeeringAttachment(self, params: Dict[str, Any]):
        """Requests a transit gateway peering attachment between the specified transit gateway
            (requester) and a peer transit gateway (accepter). The peer transit gateway can be in 
            your account or a different AWS account. After you create the peering attachment, the owner of the accept"""

        for name in ["PeerAccountId", "PeerRegion", "PeerTransitGatewayId", "TransitGatewayId"]:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")

        transit_gateway_id = params.get("TransitGatewayId")
        peer_transit_gateway_id = params.get("PeerTransitGatewayId")
        if not self.state.transit_gateways.get(transit_gateway_id):
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"The ID '{transit_gateway_id}' does not exist",
            )
        if not self.state.transit_gateways.get(peer_transit_gateway_id):
            return create_error_response(
                "InvalidTransitGatewayID.NotFound",
                f"The ID '{peer_transit_gateway_id}' does not exist",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        transit_gateway_attachment_id = self._generate_id("tgw-attach")
        accepter_transit_gateway_attachment_id = ""
        creation_time = datetime.now(timezone.utc).isoformat()
        options = params.get("Options") or {}
        resource = TransitGatewayPeeringAttachment(
            accepter_tgw_info={
                "coreNetworkId": "",
                "ownerId": params.get("PeerAccountId") or "",
                "region": params.get("PeerRegion") or "",
                "transitGatewayId": peer_transit_gateway_id,
            },
            accepter_transit_gateway_attachment_id=accepter_transit_gateway_attachment_id,
            creation_time=creation_time,
            options=options,
            requester_tgw_info={
                "coreNetworkId": "",
                "ownerId": "",
                "region": "",
                "transitGatewayId": transit_gateway_id,
            },
            state="pendingAcceptance",
            status={"code": "pendingAcceptance", "message": "Pending acceptance"},
            tag_set=tag_set,
            transit_gateway_attachment_id=transit_gateway_attachment_id,
        )

        self.resources[transit_gateway_attachment_id] = resource

        parent = self.state.transit_gateway_connect.get(transit_gateway_attachment_id)
        if parent and hasattr(parent, "transit_gateway_peering_attachment_ids"):
            parent.transit_gateway_peering_attachment_ids.append(transit_gateway_attachment_id)

        return {
            'transitGatewayPeeringAttachment': resource.to_dict(),
            }

    def DeleteTransitGatewayPeeringAttachment(self, params: Dict[str, Any]):
        """Deletes a transit gateway peering attachment."""

        if not params.get("TransitGatewayAttachmentId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: TransitGatewayAttachmentId",
            )

        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        resource, error = self._get_peering_attachment_or_error(transit_gateway_attachment_id)
        if error:
            return error

        resource.state = "deleted"
        resource.status = {"code": "deleted", "message": "Deleted"}
        response = resource.to_dict()

        parent = self.state.transit_gateway_connect.get(resource.transit_gateway_attachment_id)
        if parent and hasattr(parent, "transit_gateway_peering_attachment_ids"):
            if transit_gateway_attachment_id in parent.transit_gateway_peering_attachment_ids:
                parent.transit_gateway_peering_attachment_ids.remove(transit_gateway_attachment_id)

        del self.resources[transit_gateway_attachment_id]

        return {
            'transitGatewayPeeringAttachment': response,
            }

    def DescribeTransitGatewayPeeringAttachments(self, params: Dict[str, Any]):
        """Describes your transit gateway peering attachments."""

        transit_gateway_attachment_ids = params.get("TransitGatewayAttachmentIds.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if transit_gateway_attachment_ids:
            resources: List[TransitGatewayPeeringAttachment] = []
            for attachment_id in transit_gateway_attachment_ids:
                resource = self.resources.get(attachment_id)
                if not resource:
                    return create_error_response(
                        "InvalidTransitGatewayAttachmentID.NotFound",
                        f"The ID '{attachment_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        attachments = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'nextToken': None,
            'transitGatewayPeeringAttachments': attachments,
            }

    def RejectTransitGatewayPeeringAttachment(self, params: Dict[str, Any]):
        """Rejects a transit gateway peering attachment request."""

        if not params.get("TransitGatewayAttachmentId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: TransitGatewayAttachmentId",
            )

        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        resource, error = self._get_peering_attachment_or_error(transit_gateway_attachment_id)
        if error:
            return error

        if resource.state != "pendingAcceptance":
            return create_error_response(
                "InvalidStateTransition",
                "Transit gateway peering attachment must be in pendingAcceptance state",
            )

        resource.state = "rejected"
        resource.status = {"code": "rejected", "message": "Rejected"}

        return {
            'transitGatewayPeeringAttachment': resource.to_dict(),
            }

    def _generate_id(self, prefix: str = 'accepter') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class transitgatewaypeeringattachment_RequestParser:
    @staticmethod
    def parse_accept_transit_gateway_peering_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_create_transit_gateway_peering_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "PeerAccountId": get_scalar(md, "PeerAccountId"),
            "PeerRegion": get_scalar(md, "PeerRegion"),
            "PeerTransitGatewayId": get_scalar(md, "PeerTransitGatewayId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_peering_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_describe_transit_gateway_peering_attachments_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayAttachmentIds.N": get_indexed_list(md, "TransitGatewayAttachmentIds"),
        }

    @staticmethod
    def parse_reject_transit_gateway_peering_attachment_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AcceptTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_RequestParser.parse_accept_transit_gateway_peering_attachment_request,
            "CreateTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_RequestParser.parse_create_transit_gateway_peering_attachment_request,
            "DeleteTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_RequestParser.parse_delete_transit_gateway_peering_attachment_request,
            "DescribeTransitGatewayPeeringAttachments": transitgatewaypeeringattachment_RequestParser.parse_describe_transit_gateway_peering_attachments_request,
            "RejectTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_RequestParser.parse_reject_transit_gateway_peering_attachment_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class transitgatewaypeeringattachment_ResponseSerializer:
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
                xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_accept_transit_gateway_peering_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AcceptTransitGatewayPeeringAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPeeringAttachment
        _transitGatewayPeeringAttachment_key = None
        if "transitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "transitGatewayPeeringAttachment"
        elif "TransitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "TransitGatewayPeeringAttachment"
        if _transitGatewayPeeringAttachment_key:
            param_data = data[_transitGatewayPeeringAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPeeringAttachment>')
            xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPeeringAttachment>')
        xml_parts.append(f'</AcceptTransitGatewayPeeringAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_peering_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayPeeringAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPeeringAttachment
        _transitGatewayPeeringAttachment_key = None
        if "transitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "transitGatewayPeeringAttachment"
        elif "TransitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "TransitGatewayPeeringAttachment"
        if _transitGatewayPeeringAttachment_key:
            param_data = data[_transitGatewayPeeringAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPeeringAttachment>')
            xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPeeringAttachment>')
        xml_parts.append(f'</CreateTransitGatewayPeeringAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_peering_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayPeeringAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPeeringAttachment
        _transitGatewayPeeringAttachment_key = None
        if "transitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "transitGatewayPeeringAttachment"
        elif "TransitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "TransitGatewayPeeringAttachment"
        if _transitGatewayPeeringAttachment_key:
            param_data = data[_transitGatewayPeeringAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPeeringAttachment>')
            xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPeeringAttachment>')
        xml_parts.append(f'</DeleteTransitGatewayPeeringAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_peering_attachments_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayPeeringAttachmentsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayPeeringAttachments
        _transitGatewayPeeringAttachments_key = None
        if "transitGatewayPeeringAttachments" in data:
            _transitGatewayPeeringAttachments_key = "transitGatewayPeeringAttachments"
        elif "TransitGatewayPeeringAttachments" in data:
            _transitGatewayPeeringAttachments_key = "TransitGatewayPeeringAttachments"
        if _transitGatewayPeeringAttachments_key:
            param_data = data[_transitGatewayPeeringAttachments_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayPeeringAttachmentsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayPeeringAttachmentsSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayPeeringAttachmentsSet/>')
        xml_parts.append(f'</DescribeTransitGatewayPeeringAttachmentsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reject_transit_gateway_peering_attachment_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RejectTransitGatewayPeeringAttachmentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPeeringAttachment
        _transitGatewayPeeringAttachment_key = None
        if "transitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "transitGatewayPeeringAttachment"
        elif "TransitGatewayPeeringAttachment" in data:
            _transitGatewayPeeringAttachment_key = "TransitGatewayPeeringAttachment"
        if _transitGatewayPeeringAttachment_key:
            param_data = data[_transitGatewayPeeringAttachment_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPeeringAttachment>')
            xml_parts.extend(transitgatewaypeeringattachment_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPeeringAttachment>')
        xml_parts.append(f'</RejectTransitGatewayPeeringAttachmentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AcceptTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_ResponseSerializer.serialize_accept_transit_gateway_peering_attachment_response,
            "CreateTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_ResponseSerializer.serialize_create_transit_gateway_peering_attachment_response,
            "DeleteTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_ResponseSerializer.serialize_delete_transit_gateway_peering_attachment_response,
            "DescribeTransitGatewayPeeringAttachments": transitgatewaypeeringattachment_ResponseSerializer.serialize_describe_transit_gateway_peering_attachments_response,
            "RejectTransitGatewayPeeringAttachment": transitgatewaypeeringattachment_ResponseSerializer.serialize_reject_transit_gateway_peering_attachment_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

