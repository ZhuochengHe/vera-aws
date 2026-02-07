from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend


class TransitGatewayConnectState(str, Enum):
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


class TransitGatewayConnectPeerState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


class BgpStatus(str, Enum):
    UP = "up"
    DOWN = "down"


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class TagSpecification:
    resource_type: str
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class TransitGatewayConnectOptions:
    protocol: str  # Expected to be "gre"

    def to_dict(self) -> Dict[str, Any]:
        return {"Protocol": self.protocol}


@dataclass
class TransitGatewayConnect:
    transit_gateway_attachment_id: str
    transit_gateway_id: Optional[str] = None
    transport_transit_gateway_attachment_id: Optional[str] = None
    creation_time: Optional[datetime] = None
    options: Optional[TransitGatewayConnectOptions] = None
    state: Optional[TransitGatewayConnectState] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "TransitGatewayId": self.transit_gateway_id,
            "TransportTransitGatewayAttachmentId": self.transport_transit_gateway_attachment_id,
            "CreationTime": self.creation_time.isoformat() if self.creation_time else None,
            "Options": self.options.to_dict() if self.options else None,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


@dataclass
class TransitGatewayAttachmentBgpConfiguration:
    bgp_status: Optional[BgpStatus] = None
    peer_address: Optional[str] = None
    peer_asn: Optional[int] = None
    transit_gateway_address: Optional[str] = None
    transit_gateway_asn: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "BgpStatus": self.bgp_status.value if self.bgp_status else None,
            "PeerAddress": self.peer_address,
            "PeerAsn": self.peer_asn,
            "TransitGatewayAddress": self.transit_gateway_address,
            "TransitGatewayAsn": self.transit_gateway_asn,
        }


@dataclass
class TransitGatewayConnectPeerConfiguration:
    bgp_configurations: List[TransitGatewayAttachmentBgpConfiguration] = field(default_factory=list)
    inside_cidr_blocks: List[str] = field(default_factory=list)
    peer_address: Optional[str] = None
    protocol: Optional[str] = None  # Expected to be "gre"
    transit_gateway_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "BgpConfigurations": [bgp.to_dict() for bgp in self.bgp_configurations],
            "InsideCidrBlocks": self.inside_cidr_blocks,
            "PeerAddress": self.peer_address,
            "Protocol": self.protocol,
            "TransitGatewayAddress": self.transit_gateway_address,
        }


@dataclass
class TransitGatewayConnectPeer:
    transit_gateway_connect_peer_id: str
    transit_gateway_attachment_id: Optional[str] = None
    creation_time: Optional[datetime] = None
    connect_peer_configuration: Optional[TransitGatewayConnectPeerConfiguration] = None
    state: Optional[TransitGatewayConnectPeerState] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "TransitGatewayConnectPeerId": self.transit_gateway_connect_peer_id,
            "TransitGatewayAttachmentId": self.transit_gateway_attachment_id,
            "CreationTime": self.creation_time.isoformat() if self.creation_time else None,
            "ConnectPeerConfiguration": self.connect_peer_configuration.to_dict() if self.connect_peer_configuration else None,
            "State": self.state.value if self.state else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
        }


class TransitGatewayConnectBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)

    def create_transit_gateway_connect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        options = params.get("Options")
        transport_attachment_id = params.get("TransportTransitGatewayAttachmentId")
        if options is None or not isinstance(options, dict):
            raise ValueError("Missing or invalid required parameter: Options")
        protocol = options.get("Protocol")
        if protocol is None or protocol.lower() != "gre":
            raise ValueError("Options.Protocol must be 'gre'")

        if transport_attachment_id is None:
            raise ValueError("Missing required parameter: TransportTransitGatewayAttachmentId")

        # DryRun check (not implemented, just simulate permission check)
        if params.get("DryRun"):
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Generate unique ID for the new Connect attachment
        connect_attachment_id = self.generate_unique_id(prefix="tgw-connect-attach-")

        # Creation time
        creation_time = datetime.utcnow()

        # Tags
        tag_specifications = params.get("TagSpecification.N", [])
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags (list of dicts)
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and not key.lower().startswith("aws:"):
                    tags.append(Tag(key=key, value=value))

        # Transit Gateway ID: try to get from transport attachment if possible
        transport_attachment = self.state.transit_gateway_attachments.get(transport_attachment_id)
        transit_gateway_id = None
        if transport_attachment:
            transit_gateway_id = transport_attachment.transit_gateway_id

        # Create TransitGatewayConnectOptions object
        connect_options = TransitGatewayConnectOptions(protocol=protocol.lower())

        # Create TransitGatewayConnect object
        connect_attachment = TransitGatewayConnect(
            transit_gateway_attachment_id=connect_attachment_id,
            transit_gateway_id=transit_gateway_id,
            transport_transit_gateway_attachment_id=transport_attachment_id,
            creation_time=creation_time,
            options=connect_options,
            state=TransitGatewayConnectState.AVAILABLE if hasattr(TransitGatewayConnectState, "AVAILABLE") else "available",
            tag_set=tags,
        )

        # Store in state
        self.state.transit_gateway_connect[connect_attachment_id] = connect_attachment
        self.state.resources[connect_attachment_id] = connect_attachment

        # Build response
        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayConnect": connect_attachment.to_dict(),
        }
        return response


    def create_transit_gateway_connect_peer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        inside_cidr_blocks = params.get("InsideCidrBlocks.N")
        peer_address = params.get("PeerAddress")
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")

        if inside_cidr_blocks is None or not isinstance(inside_cidr_blocks, list) or len(inside_cidr_blocks) == 0:
            raise ValueError("Missing or invalid required parameter: InsideCidrBlocks.N")
        if peer_address is None:
            raise ValueError("Missing required parameter: PeerAddress")
        if transit_gateway_attachment_id is None:
            raise ValueError("Missing required parameter: TransitGatewayAttachmentId")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Check that the Connect attachment exists
        connect_attachment = self.state.transit_gateway_connect.get(transit_gateway_attachment_id)
        if connect_attachment is None:
            raise ValueError(f"TransitGatewayConnect attachment {transit_gateway_attachment_id} does not exist")

        # Generate unique ID for the Connect peer
        connect_peer_id = self.generate_unique_id(prefix="tgw-connect-peer-")

        # Creation time
        creation_time = datetime.utcnow()

        # Tags
        tag_specifications = params.get("TagSpecification.N", [])
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and not key.lower().startswith("aws:"):
                    tags.append(Tag(key=key, value=value))

        # BGP options
        bgp_options = params.get("BgpOptions", {})
        peer_asn = None
        if bgp_options and isinstance(bgp_options, dict):
            peer_asn = bgp_options.get("PeerAsn")

        # TransitGatewayAddress (optional)
        transit_gateway_address = params.get("TransitGatewayAddress")

        # Build BGP configuration list
        bgp_configurations: List[TransitGatewayAttachmentBgpConfiguration] = []
        # We create one BGP configuration with the provided peer_asn and addresses
        bgp_config = TransitGatewayAttachmentBgpConfiguration(
            bgp_status=None,
            peer_address=peer_address,
            peer_asn=peer_asn,
            transit_gateway_address=transit_gateway_address,
            transit_gateway_asn=None,
        )
        bgp_configurations.append(bgp_config)

        # Build Connect peer configuration
        connect_peer_configuration = TransitGatewayConnectPeerConfiguration(
            bgp_configurations=bgp_configurations,
            inside_cidr_blocks=inside_cidr_blocks,
            peer_address=peer_address,
            protocol=connect_attachment.options.protocol if connect_attachment.options else None,
            transit_gateway_address=transit_gateway_address,
        )

        # Create TransitGatewayConnectPeer object
        connect_peer = TransitGatewayConnectPeer(
            transit_gateway_connect_peer_id=connect_peer_id,
            transit_gateway_attachment_id=transit_gateway_attachment_id,
            creation_time=creation_time,
            connect_peer_configuration=connect_peer_configuration,
            state=TransitGatewayConnectPeerState.PENDING if hasattr(TransitGatewayConnectPeerState, "PENDING") else "pending",
            tag_set=tags,
        )

        # Store in state
        self.state.transit_gateway_connect_peers[connect_peer_id] = connect_peer
        self.state.resources[connect_peer_id] = connect_peer

        # Build response
        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayConnectPeer": connect_peer.to_dict(),
        }
        return response


    def delete_transit_gateway_connect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        attachment_id = params.get("TransitGatewayAttachmentId")
        if attachment_id is None:
            raise ValueError("Missing required parameter: TransitGatewayAttachmentId")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Check if the Connect attachment exists
        connect_attachment = self.state.transit_gateway_connect.get(attachment_id)
        if connect_attachment is None:
            raise ValueError(f"TransitGatewayConnect attachment {attachment_id} does not exist")

        # Check if there are any Connect peers for this attachment
        for peer in self.state.transit_gateway_connect_peers.values():
            if peer.transit_gateway_attachment_id == attachment_id:
                raise ValueError("Cannot delete Connect attachment with existing Connect peers. Delete peers first.")

        # Mark the attachment as deleting
        connect_attachment.state = TransitGatewayConnectState.DELETING if hasattr(TransitGatewayConnectState, "DELETING") else "deleting"

        # For emulator, we can immediately delete it from state
        del self.state.transit_gateway_connect[attachment_id]
        if attachment_id in self.state.resources:
            del self.state.resources[attachment_id]

        # Build response with the deleted attachment info (state set to deleted)
        deleted_attachment = TransitGatewayConnect(
            transit_gateway_attachment_id=connect_attachment.transit_gateway_attachment_id,
            transit_gateway_id=connect_attachment.transit_gateway_id,
            transport_transit_gateway_attachment_id=connect_attachment.transport_transit_gateway_attachment_id,
            creation_time=connect_attachment.creation_time,
            options=connect_attachment.options,
            state=TransitGatewayConnectState.DELETED if hasattr(TransitGatewayConnectState, "DELETED") else "deleted",
            tag_set=connect_attachment.tag_set,
        )

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayConnect": deleted_attachment.to_dict(),
        }
        return response


    def delete_transit_gateway_connect_peer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        peer_id = params.get("TransitGatewayConnectPeerId")
        if peer_id is None:
            raise ValueError("Missing required parameter: TransitGatewayConnectPeerId")

        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Check if the Connect peer exists
        connect_peer = self.state.transit_gateway_connect_peers.get(peer_id)
        if connect_peer is None:
            raise ValueError(f"TransitGatewayConnectPeer {peer_id} does not exist")

        # Mark the peer as deleting
        connect_peer.state = TransitGatewayConnectPeerState.DELETING if hasattr(TransitGatewayConnectPeerState, "DELETING") else "deleting"

        # For emulator, immediately delete from state
        del self.state.transit_gateway_connect_peers[peer_id]
        if peer_id in self.state.resources:
            del self.state.resources[peer_id]

        # Build response with deleted peer info (state set to deleted)
        deleted_peer = TransitGatewayConnectPeer(
            transit_gateway_connect_peer_id=connect_peer.transit_gateway_connect_peer_id,
            transit_gateway_attachment_id=connect_peer.transit_gateway_attachment_id,
            creation_time=connect_peer.creation_time,
            connect_peer_configuration=connect_peer.connect_peer_configuration,
            state=TransitGatewayConnectPeerState.DELETED if hasattr(TransitGatewayConnectPeerState, "DELETED") else "deleted",
            tag_set=connect_peer.tag_set,
        )

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayConnectPeer": deleted_peer.to_dict(),
        }
        return response


    def describe_transit_gateway_connects(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # DryRun check
        if params.get("DryRun"):
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Filters
        filters = params.get("Filter.N", [])
        filter_map = {}
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if name:
                filter_map[name] = values

        # Filter by IDs if provided
        attachment_ids = params.get("TransitGatewayAttachmentIds.N", [])

        # Collect matching Connect attachments
        results = []
        for connect in self.state.transit_gateway_connect.values():
            # Filter by attachment IDs if specified
            if attachment_ids and connect.transit_gateway_attachment_id not in attachment_ids:
                continue

            # Apply filters
            match = True
            for filter_name, filter_values in filter_map.items():
                if filter_name == "options.protocol":
                    if connect.options is None or connect.options.protocol not in filter_values:
                        match = False
                        break
                elif filter_name == "state":
                    if connect.state is None or connect.state.value not in filter_values:
                        match = False
                        break
                elif filter_name == "transit-gateway-attachment-id":
                    if connect.transit_gateway_attachment_id not in filter_values:
                        match = False
                        break
                elif filter_name == "transit-gateway-id":
                    if connect.transit_gateway_id not in filter_values:
                        match = False
                        break
                elif filter_name == "transport-transit-gateway-attachment-id":
                    if connect.transport_transit_gateway_attachment_id not in filter_values:
                        match = False
                        break
                else:
                    # Unknown filter, ignore or treat as no match
                    match = False
                    break
            if match:
                results.append(connect.to_dict())

        # Pagination parameters
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5:
                    max_results = 5
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = 1000
        else:
            max_results = 1000

        paged_results = results[start_index : start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(results):
            new_next_token = str(start_index + max_results)

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayConnectSet": paged_results,
            "nextToken": new_next_token,
        }
        return response

    def describe_transit_gateway_connect_peers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters
        dry_run = params.get("DryRun", False)
        filters = params.get("Filter", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        peer_ids = params.get("TransitGatewayConnectPeerIds", [])

        # DryRun check - not implemented here, but placeholder for permission check
        if dry_run:
            # In real implementation, check permissions and raise error if unauthorized
            # Here, just simulate success by raising DryRunOperation error or returning
            # For emulator, we can just return error response
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "RequestId": self.generate_request_id(),
            }

        # Validate max_results if provided
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ValueError("MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be between 5 and 1000")

        # Validate filters format
        # Filters is expected to be a list of dicts with keys "Name" and "Values"
        # Normalize filters to list of dicts
        if not isinstance(filters, list):
            raise ValueError("Filter must be a list")

        # Prepare filter criteria
        filter_criteria = {}
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not isinstance(values, list):
                raise ValueError("Filter Values must be a list")
            if name:
                filter_criteria[name] = values

        # Collect all peers from state
        all_peers = list(self.state.transit_gateway_connect_peer.values())

        # Filter by TransitGatewayConnectPeerIds if provided
        if peer_ids:
            all_peers = [p for p in all_peers if p.transit_gateway_connect_peer_id in peer_ids]

        # Apply filters
        def peer_matches_filters(peer: TransitGatewayConnectPeer) -> bool:
            for fname, fvalues in filter_criteria.items():
                if fname == "state":
                    # State is enum, convert filter values to enum for comparison
                    # Acceptable values: pending|available|deleting|deleted
                    # Map string to TransitGatewayConnectPeerState enum members
                    # We assume TransitGatewayConnectPeerState enum has members named PENDING, AVAILABLE, DELETING, DELETED
                    # If peer.state is None, treat as no match
                    if peer.state is None:
                        return False
                    # Convert filter values to uppercase and compare with enum names
                    allowed_states = set()
                    for val in fvalues:
                        try:
                            allowed_states.add(TransitGatewayConnectPeerState[val.upper()])
                        except KeyError:
                            # Invalid state filter value, no match
                            return False
                    if peer.state not in allowed_states:
                        return False
                elif fname == "transit-gateway-attachment-id":
                    # peer.transit_gateway_attachment_id may be None
                    if peer.transit_gateway_attachment_id not in fvalues:
                        return False
                elif fname == "transit-gateway-connect-peer-id":
                    if peer.transit_gateway_connect_peer_id not in fvalues:
                        return False
                else:
                    # Unknown filter name, ignore or treat as no match? AWS ignores unknown filters
                    # So ignore unknown filters
                    pass
            return True

        filtered_peers = [p for p in all_peers if peer_matches_filters(p)]

        # Pagination handling
        # next_token is expected to be a string token representing an index or id
        # For simplicity, we can treat next_token as an integer offset encoded as string
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
                if start_index < 0 or start_index >= len(filtered_peers):
                    start_index = 0
            except Exception:
                start_index = 0

        # Apply max_results limit
        if max_results is None:
            max_results = 1000  # default max

        end_index = start_index + max_results
        page_peers = filtered_peers[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(filtered_peers):
            new_next_token = str(end_index)

        # Convert peers to dicts
        peer_dicts = []
        for peer in page_peers:
            peer_dict = peer.to_dict()
            peer_dicts.append(peer_dict)

        response = {
            "requestId": self.generate_request_id(),
            "transitGatewayConnectPeerSet": peer_dicts,
            "nextToken": new_next_token,
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class TransitGatewayConnectGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateTransitGatewayConnect", self.create_transit_gateway_connect)
        self.register_action("CreateTransitGatewayConnectPeer", self.create_transit_gateway_connect_peer)
        self.register_action("DeleteTransitGatewayConnect", self.delete_transit_gateway_connect)
        self.register_action("DeleteTransitGatewayConnectPeer", self.delete_transit_gateway_connect_peer)
        self.register_action("DescribeTransitGatewayConnects", self.describe_transit_gateway_connects)
        self.register_action("DescribeTransitGatewayConnectPeers", self.describe_transit_gateway_connect_peers)

    def create_transit_gateway_connect(self, params):
        return self.backend.create_transit_gateway_connect(params)

    def create_transit_gateway_connect_peer(self, params):
        return self.backend.create_transit_gateway_connect_peer(params)

    def delete_transit_gateway_connect(self, params):
        return self.backend.delete_transit_gateway_connect(params)

    def delete_transit_gateway_connect_peer(self, params):
        return self.backend.delete_transit_gateway_connect_peer(params)

    def describe_transit_gateway_connects(self, params):
        return self.backend.describe_transit_gateway_connects(params)

    def describe_transit_gateway_connect_peers(self, params):
        return self.backend.describe_transit_gateway_connect_peers(params)
