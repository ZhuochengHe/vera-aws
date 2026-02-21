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
class TransitGatewayConnect:
    creation_time: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    transit_gateway_attachment_id: str = ""
    transit_gateway_id: str = ""
    transport_transit_gateway_attachment_id: str = ""

    # Internal dependency tracking — not in API response
    transit_gateway_multicast_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayMulticast children
    transit_gateway_peering_attachment_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayPeeringAttachment children
    vpn_concentrator_ids: List[str] = field(default_factory=list)  # tracks VpnConcentrator children

    transit_gateway_connect_peer_ids: List[str] = field(default_factory=list)  # tracks TransitGatewayConnectPeer children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTime": self.creation_time,
            "options": self.options,
            "state": self.state,
            "tagSet": self.tag_set,
            "transitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "transitGatewayId": self.transit_gateway_id,
            "transportTransitGatewayAttachmentId": self.transport_transit_gateway_attachment_id,
        }

class TransitGatewayConnect_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.transit_gateway_connect  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.transit_gateways.get(params['transit_gateway_id']).transit_gateway_connect_ids.append(new_id)
    #   Delete: self.state.transit_gateways.get(resource.transit_gateway_id).transit_gateway_connect_ids.remove(resource_id)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(self, store: Dict[str, Any], resource_id: str, error_code: str, message: Optional[str] = None):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message or f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources: List[Any] = []
        for resource_id in resource_ids:
            resource = store.get(resource_id)
            if not resource:
                return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
            resources.append(resource)
        return resources, None

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: str) -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def _get_connect_peer_store(self) -> Dict[str, Any]:
        if not hasattr(self.state, "transit_gateway_connect_peers"):
            setattr(self.state, "transit_gateway_connect_peers", {})
        return self.state.transit_gateway_connect_peers


    # Add any helper functions needed by the API methods below.
    # These helpers can be used by multiple API methods.

    def CreateTransitGatewayConnect(self, params: Dict[str, Any]):
        """Creates a Connect attachment from a specified transit gateway attachment. A Connect attachment is a GRE-based tunnel attachment that you can use to establish a connection between a transit gateway and an appliance. A Connect attachment uses an existing VPC or AWS Direct Connect attachment as the und"""

        error = self._require_params(params, ["Options", "TransportTransitGatewayAttachmentId"])
        if error:
            return error

        transport_attachment_id = params.get("TransportTransitGatewayAttachmentId")
        transport_attachment = None
        attachment_store = getattr(self.state, "transit_gateway_attachments", None)
        if attachment_store is not None:
            transport_attachment = attachment_store.get(transport_attachment_id)
        if not transport_attachment:
            transport_attachment = self.state.transit_gateways.get(transport_attachment_id)
        if not transport_attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{transport_attachment_id}' does not exist",
            )

        if isinstance(transport_attachment, dict):
            transit_gateway_id = transport_attachment.get("transitGatewayId") or transport_attachment.get("transit_gateway_id")
        else:
            transit_gateway_id = getattr(transport_attachment, "transit_gateway_id", None)
        transit_gateway_id = transit_gateway_id or transport_attachment_id

        options = params.get("Options") or {}
        protocol = None
        if isinstance(options, dict):
            protocol = options.get("protocol") or options.get("Protocol")
        if not protocol:
            protocol = "gre"
        connect_options = {"protocol": protocol}

        transit_gateway_attachment_id = self._generate_id("tgw")
        tag_set = self._extract_tags(params.get("TagSpecification.N", []), "transit-gateway-attachment")
        resource = TransitGatewayConnect(
            creation_time=self._utc_now(),
            options=connect_options,
            state="available",
            tag_set=tag_set,
            transit_gateway_attachment_id=transit_gateway_attachment_id,
            transit_gateway_id=transit_gateway_id,
            transport_transit_gateway_attachment_id=transport_attachment_id,
        )
        self.resources[transit_gateway_attachment_id] = resource

        parent = self.state.transit_gateways.get(transit_gateway_id)
        if parent and hasattr(parent, "transit_gateway_connect_ids"):
            parent.transit_gateway_connect_ids.append(transit_gateway_attachment_id)

        return {
            "transitGatewayConnect": resource.to_dict(),
        }

    def CreateTransitGatewayConnectPeer(self, params: Dict[str, Any]):
        """Creates a Connect peer for a specified transit gateway Connect attachment between a
            transit gateway and an appliance. The peer address and transit gateway address must be the same IP address family (IPv4 or IPv6). For more information, seeConnect peersin theAWS Transit Gateways Guide."""

        error = self._require_params(params, ["InsideCidrBlocks.N", "PeerAddress", "TransitGatewayAttachmentId"])
        if error:
            return error

        connect_attachment_id = params.get("TransitGatewayAttachmentId")
        connect_resource, error = self._get_resource_or_error(
            self.resources,
            connect_attachment_id,
            "InvalidTransitGatewayAttachmentID.NotFound",
        )
        if error:
            return error

        transit_gateway_connect_peer_id = self._generate_id("tgw")
        inside_cidr_blocks = params.get("InsideCidrBlocks.N", [])
        peer_address = params.get("PeerAddress")
        transit_gateway_address = params.get("TransitGatewayAddress")
        bgp_options = params.get("BgpOptions") or {}

        protocol = None
        if isinstance(connect_resource.options, dict):
            protocol = connect_resource.options.get("protocol") or connect_resource.options.get("Protocol")
        if not protocol:
            protocol = "gre"

        bgp_configurations: List[Dict[str, Any]] = []
        if isinstance(bgp_options, dict) and bgp_options:
            bgp_configurations.append({
                "bgpStatus": "up",
                "peerAddress": peer_address,
                "peerAsn": bgp_options.get("PeerAsn") or bgp_options.get("peerAsn"),
                "transitGatewayAddress": transit_gateway_address,
                "transitGatewayAsn": bgp_options.get("TransitGatewayAsn") or bgp_options.get("transitGatewayAsn"),
            })

        connect_peer_configuration = {
            "bgpConfigurations": bgp_configurations,
            "insideCidrBlocks": inside_cidr_blocks,
            "peerAddress": peer_address,
            "protocol": protocol,
            "transitGatewayAddress": transit_gateway_address,
        }

        peer_data = {
            "connectPeerConfiguration": connect_peer_configuration,
            "creationTime": self._utc_now(),
            "state": "available",
            "tagSet": self._extract_tags(params.get("TagSpecification.N", []), "transit-gateway-connect-peer"),
            "transitGatewayAttachmentId": connect_attachment_id,
            "transitGatewayConnectPeerId": transit_gateway_connect_peer_id,
        }

        peer_store = self._get_connect_peer_store()
        peer_store[transit_gateway_connect_peer_id] = peer_data
        if hasattr(connect_resource, "transit_gateway_connect_peer_ids"):
            connect_resource.transit_gateway_connect_peer_ids.append(transit_gateway_connect_peer_id)

        return {
            "transitGatewayConnectPeer": peer_data,
        }

    def DeleteTransitGatewayConnect(self, params: Dict[str, Any]):
        """Deletes the specified Connect attachment. You must first delete any Connect peers for
            the attachment."""

        error = self._require_params(params, ["TransitGatewayAttachmentId"])
        if error:
            return error

        attachment_id = params.get("TransitGatewayAttachmentId")
        resource, error = self._get_resource_or_error(
            self.resources,
            attachment_id,
            "InvalidTransitGatewayAttachmentID.NotFound",
        )
        if error:
            return error

        if getattr(resource, "transit_gateway_connect_peer_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGatewayConnect has dependent TransitGatewayConnectPeer(s) and cannot be deleted.",
            )
        if getattr(resource, "transit_gateway_multicast_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGatewayConnect has dependent TransitGatewayMulticast(s) and cannot be deleted.",
            )
        if getattr(resource, "transit_gateway_peering_attachment_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGatewayConnect has dependent TransitGatewayPeeringAttachment(s) and cannot be deleted.",
            )
        if getattr(resource, "vpn_concentrator_ids", []):
            return create_error_response(
                "DependencyViolation",
                "TransitGatewayConnect has dependent VpnConcentrator(s) and cannot be deleted.",
            )

        self.resources.pop(attachment_id, None)

        parent = self.state.transit_gateways.get(resource.transit_gateway_id)
        if parent and hasattr(parent, "transit_gateway_connect_ids") and attachment_id in parent.transit_gateway_connect_ids:
            parent.transit_gateway_connect_ids.remove(attachment_id)

        return {
            "transitGatewayConnect": resource.to_dict(),
        }

    def DeleteTransitGatewayConnectPeer(self, params: Dict[str, Any]):
        """Deletes the specified Connect peer."""

        error = self._require_params(params, ["TransitGatewayConnectPeerId"])
        if error:
            return error

        peer_id = params.get("TransitGatewayConnectPeerId")
        peer_store = self._get_connect_peer_store()
        peer_data, error = self._get_resource_or_error(
            peer_store,
            peer_id,
            "InvalidTransitGatewayConnectPeerID.NotFound",
        )
        if error:
            return error

        peer_store.pop(peer_id, None)

        attachment_id = None
        if isinstance(peer_data, dict):
            attachment_id = peer_data.get("transitGatewayAttachmentId")
        if attachment_id:
            connect_resource = self.resources.get(attachment_id)
            if connect_resource and hasattr(connect_resource, "transit_gateway_connect_peer_ids"):
                if peer_id in connect_resource.transit_gateway_connect_peer_ids:
                    connect_resource.transit_gateway_connect_peer_ids.remove(peer_id)

        return {
            "transitGatewayConnectPeer": peer_data,
        }

    def DescribeTransitGatewayConnects(self, params: Dict[str, Any]):
        """Describes one or more Connect attachments."""

        attachment_ids = params.get("TransitGatewayAttachmentIds.N", [])
        if attachment_ids:
            resources, error = self._get_resources_by_ids(
                self.resources,
                attachment_ids,
                "InvalidTransitGatewayAttachmentID.NotFound",
            )
            if error:
                return error
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        response_items = [resource.to_dict() for resource in resources]

        return {
            "nextToken": None,
            "transitGatewayConnectSet": response_items,
        }

    def DescribeTransitGatewayConnectPeers(self, params: Dict[str, Any]):
        """Describes one or more Connect peers."""

        peer_store = self._get_connect_peer_store()
        peer_ids = params.get("TransitGatewayConnectPeerIds.N", [])
        if peer_ids:
            peers, error = self._get_resources_by_ids(
                peer_store,
                peer_ids,
                "InvalidTransitGatewayConnectPeerID.NotFound",
            )
            if error:
                return error
        else:
            peers = list(peer_store.values())

        peers = apply_filters(peers, params.get("Filter.N", []))

        return {
            "nextToken": None,
            "transitGatewayConnectPeerSet": peers,
        }

    def _generate_id(self, prefix: str = 'tgw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class transitgatewayconnect_RequestParser:
    @staticmethod
    def parse_create_transit_gateway_connect_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Options": get_scalar(md, "Options"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TransportTransitGatewayAttachmentId": get_scalar(md, "TransportTransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_create_transit_gateway_connect_peer_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "BgpOptions": get_scalar(md, "BgpOptions"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InsideCidrBlocks.N": get_indexed_list(md, "InsideCidrBlocks"),
            "PeerAddress": get_scalar(md, "PeerAddress"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TransitGatewayAddress": get_scalar(md, "TransitGatewayAddress"),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_connect_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_connect_peer_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayConnectPeerId": get_scalar(md, "TransitGatewayConnectPeerId"),
        }

    @staticmethod
    def parse_describe_transit_gateway_connects_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayAttachmentIds.N": get_indexed_list(md, "TransitGatewayAttachmentIds"),
        }

    @staticmethod
    def parse_describe_transit_gateway_connect_peers_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayConnectPeerIds.N": get_indexed_list(md, "TransitGatewayConnectPeerIds"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateTransitGatewayConnect": transitgatewayconnect_RequestParser.parse_create_transit_gateway_connect_request,
            "CreateTransitGatewayConnectPeer": transitgatewayconnect_RequestParser.parse_create_transit_gateway_connect_peer_request,
            "DeleteTransitGatewayConnect": transitgatewayconnect_RequestParser.parse_delete_transit_gateway_connect_request,
            "DeleteTransitGatewayConnectPeer": transitgatewayconnect_RequestParser.parse_delete_transit_gateway_connect_peer_request,
            "DescribeTransitGatewayConnects": transitgatewayconnect_RequestParser.parse_describe_transit_gateway_connects_request,
            "DescribeTransitGatewayConnectPeers": transitgatewayconnect_RequestParser.parse_describe_transit_gateway_connect_peers_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class transitgatewayconnect_ResponseSerializer:
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
                xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_transit_gateway_connect_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayConnectResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayConnect
        _transitGatewayConnect_key = None
        if "transitGatewayConnect" in data:
            _transitGatewayConnect_key = "transitGatewayConnect"
        elif "TransitGatewayConnect" in data:
            _transitGatewayConnect_key = "TransitGatewayConnect"
        if _transitGatewayConnect_key:
            param_data = data[_transitGatewayConnect_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayConnect>')
            xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayConnect>')
        xml_parts.append(f'</CreateTransitGatewayConnectResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_connect_peer_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayConnectPeerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayConnectPeer
        _transitGatewayConnectPeer_key = None
        if "transitGatewayConnectPeer" in data:
            _transitGatewayConnectPeer_key = "transitGatewayConnectPeer"
        elif "TransitGatewayConnectPeer" in data:
            _transitGatewayConnectPeer_key = "TransitGatewayConnectPeer"
        if _transitGatewayConnectPeer_key:
            param_data = data[_transitGatewayConnectPeer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayConnectPeer>')
            xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayConnectPeer>')
        xml_parts.append(f'</CreateTransitGatewayConnectPeerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_connect_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayConnectResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayConnect
        _transitGatewayConnect_key = None
        if "transitGatewayConnect" in data:
            _transitGatewayConnect_key = "transitGatewayConnect"
        elif "TransitGatewayConnect" in data:
            _transitGatewayConnect_key = "TransitGatewayConnect"
        if _transitGatewayConnect_key:
            param_data = data[_transitGatewayConnect_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayConnect>')
            xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayConnect>')
        xml_parts.append(f'</DeleteTransitGatewayConnectResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_connect_peer_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayConnectPeerResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayConnectPeer
        _transitGatewayConnectPeer_key = None
        if "transitGatewayConnectPeer" in data:
            _transitGatewayConnectPeer_key = "transitGatewayConnectPeer"
        elif "TransitGatewayConnectPeer" in data:
            _transitGatewayConnectPeer_key = "TransitGatewayConnectPeer"
        if _transitGatewayConnectPeer_key:
            param_data = data[_transitGatewayConnectPeer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayConnectPeer>')
            xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayConnectPeer>')
        xml_parts.append(f'</DeleteTransitGatewayConnectPeerResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_connects_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayConnectsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayConnectSet
        _transitGatewayConnectSet_key = None
        if "transitGatewayConnectSet" in data:
            _transitGatewayConnectSet_key = "transitGatewayConnectSet"
        elif "TransitGatewayConnectSet" in data:
            _transitGatewayConnectSet_key = "TransitGatewayConnectSet"
        elif "TransitGatewayConnects" in data:
            _transitGatewayConnectSet_key = "TransitGatewayConnects"
        if _transitGatewayConnectSet_key:
            param_data = data[_transitGatewayConnectSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayConnectSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayConnectSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayConnectSet/>')
        xml_parts.append(f'</DescribeTransitGatewayConnectsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_connect_peers_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayConnectPeersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize transitGatewayConnectPeerSet
        _transitGatewayConnectPeerSet_key = None
        if "transitGatewayConnectPeerSet" in data:
            _transitGatewayConnectPeerSet_key = "transitGatewayConnectPeerSet"
        elif "TransitGatewayConnectPeerSet" in data:
            _transitGatewayConnectPeerSet_key = "TransitGatewayConnectPeerSet"
        elif "TransitGatewayConnectPeers" in data:
            _transitGatewayConnectPeerSet_key = "TransitGatewayConnectPeers"
        if _transitGatewayConnectPeerSet_key:
            param_data = data[_transitGatewayConnectPeerSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayConnectPeerSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewayconnect_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayConnectPeerSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayConnectPeerSet/>')
        xml_parts.append(f'</DescribeTransitGatewayConnectPeersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateTransitGatewayConnect": transitgatewayconnect_ResponseSerializer.serialize_create_transit_gateway_connect_response,
            "CreateTransitGatewayConnectPeer": transitgatewayconnect_ResponseSerializer.serialize_create_transit_gateway_connect_peer_response,
            "DeleteTransitGatewayConnect": transitgatewayconnect_ResponseSerializer.serialize_delete_transit_gateway_connect_response,
            "DeleteTransitGatewayConnectPeer": transitgatewayconnect_ResponseSerializer.serialize_delete_transit_gateway_connect_peer_response,
            "DescribeTransitGatewayConnects": transitgatewayconnect_ResponseSerializer.serialize_describe_transit_gateway_connects_response,
            "DescribeTransitGatewayConnectPeers": transitgatewayconnect_ResponseSerializer.serialize_describe_transit_gateway_connect_peers_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

