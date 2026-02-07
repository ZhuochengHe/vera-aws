from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class CidrBlock:
    cidrBlock: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"cidrBlock": self.cidrBlock}


@dataclass
class Ipv6CidrBlock:
    ipv6CidrBlock: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"ipv6CidrBlock": self.ipv6CidrBlock}


@dataclass
class VpcPeeringConnectionOptionsDescription:
    allowDnsResolutionFromRemoteVpc: Optional[bool] = None
    allowEgressFromLocalClassicLinkToRemoteVpc: Optional[bool] = None  # Deprecated
    allowEgressFromLocalVpcToRemoteClassicLink: Optional[bool] = None  # Deprecated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowDnsResolutionFromRemoteVpc": self.allowDnsResolutionFromRemoteVpc,
            "allowEgressFromLocalClassicLinkToRemoteVpc": self.allowEgressFromLocalClassicLinkToRemoteVpc,
            "allowEgressFromLocalVpcToRemoteClassicLink": self.allowEgressFromLocalVpcToRemoteClassicLink,
        }


@dataclass
class VpcPeeringConnectionVpcInfo:
    cidrBlock: Optional[str] = None
    cidrBlockSet: List[CidrBlock] = field(default_factory=list)
    ipv6CidrBlockSet: List[Ipv6CidrBlock] = field(default_factory=list)
    ownerId: Optional[str] = None
    peeringOptions: Optional[VpcPeeringConnectionOptionsDescription] = None
    region: Optional[str] = None
    vpcId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cidrBlock": self.cidrBlock,
            "cidrBlockSet": [c.to_dict() for c in self.cidrBlockSet],
            "ipv6CidrBlockSet": [i.to_dict() for i in self.ipv6CidrBlockSet],
            "ownerId": self.ownerId,
            "peeringOptions": self.peeringOptions.to_dict() if self.peeringOptions else None,
            "region": self.region,
            "vpcId": self.vpcId,
        }


class VpcPeeringConnectionStateCode(str, Enum):
    INITIATING_REQUEST = "initiating-request"
    PENDING_ACCEPTANCE = "pending-acceptance"
    ACTIVE = "active"
    DELETED = "deleted"
    REJECTED = "rejected"
    FAILED = "failed"
    EXPIRED = "expired"
    PROVISIONING = "provisioning"
    DELETING = "deleting"


@dataclass
class VpcPeeringConnectionStateReason:
    code: Optional[VpcPeeringConnectionStateCode] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value if self.code else None,
            "message": self.message,
        }


@dataclass
class VpcPeeringConnection:
    vpcPeeringConnectionId: str
    accepterVpcInfo: Optional[VpcPeeringConnectionVpcInfo] = None
    expirationTime: Optional[datetime] = None
    requesterVpcInfo: Optional[VpcPeeringConnectionVpcInfo] = None
    status: Optional[VpcPeeringConnectionStateReason] = None
    tagSet: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vpcPeeringConnectionId": self.vpcPeeringConnectionId,
            "accepterVpcInfo": self.accepterVpcInfo.to_dict() if self.accepterVpcInfo else None,
            "expirationTime": self.expirationTime.isoformat() if self.expirationTime else None,
            "requesterVpcInfo": self.requesterVpcInfo.to_dict() if self.requesterVpcInfo else None,
            "status": self.status.to_dict() if self.status else None,
            "tagSet": [tag.to_dict() for tag in self.tagSet],
        }


@dataclass
class PeeringConnectionOptionsRequest:
    AllowDnsResolutionFromRemoteVpc: Optional[bool] = None
    AllowEgressFromLocalClassicLinkToRemoteVpc: Optional[bool] = None  # Deprecated
    AllowEgressFromLocalVpcToRemoteClassicLink: Optional[bool] = None  # Deprecated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllowDnsResolutionFromRemoteVpc": self.AllowDnsResolutionFromRemoteVpc,
            "AllowEgressFromLocalClassicLinkToRemoteVpc": self.AllowEgressFromLocalClassicLinkToRemoteVpc,
            "AllowEgressFromLocalVpcToRemoteClassicLink": self.AllowEgressFromLocalVpcToRemoteClassicLink,
        }


@dataclass
class PeeringConnectionOptions:
    allowDnsResolutionFromRemoteVpc: Optional[bool] = None
    allowEgressFromLocalClassicLinkToRemoteVpc: Optional[bool] = None  # Deprecated
    allowEgressFromLocalVpcToRemoteClassicLink: Optional[bool] = None  # Deprecated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowDnsResolutionFromRemoteVpc": self.allowDnsResolutionFromRemoteVpc,
            "allowEgressFromLocalClassicLinkToRemoteVpc": self.allowEgressFromLocalClassicLinkToRemoteVpc,
            "allowEgressFromLocalVpcToRemoteClassicLink": self.allowEgressFromLocalVpcToRemoteClassicLink,
        }


class VPCpeeringBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state.vpc_peering_connections or similar

    def accept_vpc_peering_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_peering_connection_id = params.get("VpcPeeringConnectionId")
        if not vpc_peering_connection_id:
            raise ValueError("VpcPeeringConnectionId is required")

        vpc_peering = self.state.vpc_peering.get(vpc_peering_connection_id)
        if not vpc_peering:
            raise ValueError(f"VpcPeeringConnection {vpc_peering_connection_id} does not exist")

        # Only allow accept if status is pending-acceptance
        if not vpc_peering.status or vpc_peering.status.code != VpcPeeringConnectionStateCode.PENDING_ACCEPTANCE:
            raise ValueError("VpcPeeringConnection must be in pending-acceptance state to accept")

        # Only the owner of the accepter VPC can accept
        accepter_owner_id = None
        if vpc_peering.accepterVpcInfo and vpc_peering.accepterVpcInfo.ownerId:
            accepter_owner_id = vpc_peering.accepterVpcInfo.ownerId
        else:
            raise ValueError("Accepter VPC info or ownerId missing")

        if accepter_owner_id != self.get_owner_id():
            raise ValueError("You must be the owner of the accepter VPC to accept the peering connection")

        # Change status to active
        vpc_peering.status.code = VpcPeeringConnectionStateCode.ACTIVE
        vpc_peering.status.message = "Active"

        # Clear expiration time since accepted
        vpc_peering.expirationTime = None

        # Save updated resource
        self.state.vpc_peering[vpc_peering_connection_id] = vpc_peering

        return {
            "requestId": self.generate_request_id(),
            "vpcPeeringConnection": vpc_peering.to_dict(),
        }


    def create_vpc_peering_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_id = params.get("VpcId")
        peer_vpc_id = params.get("PeerVpcId")
        peer_owner_id = params.get("PeerOwnerId", self.get_owner_id())
        peer_region = params.get("PeerRegion")

        if not vpc_id:
            raise ValueError("VpcId is required")
        if not peer_vpc_id:
            raise ValueError("PeerVpcId is required")

        # Validate requester VPC exists
        requester_vpc = self.state.vpcs.get(vpc_id)
        if not requester_vpc:
            raise ValueError(f"Requester VPC {vpc_id} does not exist")

        # Validate accepter VPC exists
        accepter_vpc = self.state.vpcs.get(peer_vpc_id)
        if not accepter_vpc:
            raise ValueError(f"Accepter VPC {peer_vpc_id} does not exist")

        # Validate no overlapping CIDR blocks between requester and accepter
        def cidr_blocks(vpc):
            blocks = []
            if vpc.cidrBlock:
                blocks.append(vpc.cidrBlock)
            if hasattr(vpc, "cidrBlockSet") and vpc.cidrBlockSet:
                blocks.extend([cb.cidrBlock for cb in vpc.cidrBlockSet if cb.cidrBlock])
            return blocks

        requester_cidrs = cidr_blocks(requester_vpc)
        accepter_cidrs = cidr_blocks(accepter_vpc)
        for r_cidr in requester_cidrs:
            for a_cidr in accepter_cidrs:
                if r_cidr == a_cidr:
                    raise ValueError("Requester and Accepter VPC CIDR blocks cannot overlap")

        # Generate unique VPC peering connection ID
        vpc_peering_connection_id = self.generate_unique_id(prefix="pcx-")

        # Build VpcPeeringConnectionVpcInfo for requester and accepter
        def build_vpc_info(vpc, owner_id, region=None):
            cidr_block_set = []
            if hasattr(vpc, "cidrBlockSet") and vpc.cidrBlockSet:
                cidr_block_set = [CidrBlock(cidrBlock=cb.cidrBlock) for cb in vpc.cidrBlockSet]
            ipv6_cidr_block_set = []
            if hasattr(vpc, "ipv6CidrBlockSet") and vpc.ipv6CidrBlockSet:
                ipv6_cidr_block_set = [Ipv6CidrBlock(ipv6CidrBlock=cb.ipv6CidrBlock) for cb in vpc.ipv6CidrBlockSet]
            peering_options = VpcPeeringConnectionOptionsDescription(
                allowDnsResolutionFromRemoteVpc=False,
                allowEgressFromLocalClassicLinkToRemoteVpc=False,
                allowEgressFromLocalVpcToRemoteClassicLink=False,
            )
            return VpcPeeringConnectionVpcInfo(
                cidrBlock=getattr(vpc, "cidrBlock", None),
                cidrBlockSet=cidr_block_set,
                ipv6CidrBlockSet=ipv6_cidr_block_set,
                ownerId=owner_id,
                peeringOptions=peering_options,
                region=region,
                vpcId=getattr(vpc, "vpcId", None) or getattr(vpc, "id", None),
            )

        requester_owner_id = self.get_owner_id()
        requester_vpc_info = build_vpc_info(requester_vpc, requester_owner_id)
        accepter_vpc_info = build_vpc_info(accepter_vpc, peer_owner_id, peer_region)

        # Status is initiating-request
        status = VpcPeeringConnectionStateReason(
            code=VpcPeeringConnectionStateCode.INITIATING_REQUEST,
            message=f"Initiating Request to {peer_owner_id}",
        )

        # Expiration time is 7 days from now
        from datetime import datetime, timedelta, timezone
        expiration_time = datetime.now(timezone.utc) + timedelta(days=7)

        # Tags from TagSpecification.N if provided
        tag_set = []
        tag_specifications = []
        for key in params:
            if key.startswith("TagSpecification."):
                tag_specifications.append(params[key])
        # TagSpecification.N is an array of dicts with ResourceType and Tags
        # We only assign tags if ResourceType is vpc-peering-connection
        for tag_spec in tag_specifications:
            if isinstance(tag_spec, dict):
                resource_type = tag_spec.get("ResourceType")
                if resource_type == "vpc-peering-connection":
                    tags = tag_spec.get("Tags", [])
                    for tag in tags:
                        if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                            tag_set.append(Tag(Key=tag["Key"], Value=tag["Value"]))

        vpc_peering_connection = VpcPeeringConnection(
            vpcPeeringConnectionId=vpc_peering_connection_id,
            accepterVpcInfo=accepter_vpc_info,
            expirationTime=expiration_time,
            requesterVpcInfo=requester_vpc_info,
            status=status,
            tagSet=tag_set,
        )

        # Store in state
        self.state.vpc_peering[vpc_peering_connection_id] = vpc_peering_connection
        self.state.resources[vpc_peering_connection_id] = vpc_peering_connection

        return {
            "requestId": self.generate_request_id(),
            "vpcPeeringConnection": vpc_peering_connection.to_dict(),
        }


    def delete_vpc_peering_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_peering_connection_id = params.get("VpcPeeringConnectionId")
        if not vpc_peering_connection_id:
            raise ValueError("VpcPeeringConnectionId is required")

        vpc_peering = self.state.vpc_peering.get(vpc_peering_connection_id)
        if not vpc_peering:
            raise ValueError(f"VpcPeeringConnection {vpc_peering_connection_id} does not exist")

        # Check current status
        if vpc_peering.status:
            code = vpc_peering.status.code
            if code in (VpcPeeringConnectionStateCode.FAILED, VpcPeeringConnectionStateCode.REJECTED):
                raise ValueError("Cannot delete a VPC peering connection in failed or rejected state")

        # Only owner of requester or accepter VPC can delete if active
        owner_id = self.get_owner_id()
        requester_owner = None
        accepter_owner = None
        if vpc_peering.requesterVpcInfo and vpc_peering.requesterVpcInfo.ownerId:
            requester_owner = vpc_peering.requesterVpcInfo.ownerId
        if vpc_peering.accepterVpcInfo and vpc_peering.accepterVpcInfo.ownerId:
            accepter_owner = vpc_peering.accepterVpcInfo.ownerId

        if owner_id != requester_owner and owner_id != accepter_owner:
            raise ValueError("You must be the owner of the requester or accepter VPC to delete the peering connection")

        # If status is pending-acceptance, only requester owner can delete
        if vpc_peering.status and vpc_peering.status.code == VpcPeeringConnectionStateCode.PENDING_ACCEPTANCE:
            if owner_id != requester_owner:
                raise ValueError("Only the owner of the requester VPC can delete a pending-acceptance peering connection")

        # Mark as deleted
        vpc_peering.status.code = VpcPeeringConnectionStateCode.DELETED
        vpc_peering.status.message = "Deleted"

        # Remove from state
        del self.state.vpc_peering[vpc_peering_connection_id]
        if vpc_peering_connection_id in self.state.resources:
            del self.state.resources[vpc_peering_connection_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def describe_vpc_peering_connections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filters = []
        # Filters can be Filter.N.Name and Filter.N.Value or Filter.N.Values
        # Collect filters from params keys
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                # key format: Filter.N.Name or Filter.N.Value or Filter.N.Value.M
                parts = key.split(".")
                if len(parts) >= 3:
                    filter_num = parts[1]
                    filter_key = parts[2]
                    if filter_num not in filter_dict:
                        filter_dict[filter_num] = {"Name": None, "Values": []}
                    if filter_key == "Name":
                        filter_dict[filter_num]["Name"] = value
                    elif filter_key.startswith("Value"):
                        filter_dict[filter_num]["Values"].append(value)
        for f in filter_dict.values():
            if f["Name"]:
                filters.append({"Name": f["Name"], "Values": f["Values"]})

        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        vpc_peering_connection_ids = []
        # Collect VpcPeeringConnectionId.N keys
        for key, value in params.items():
            if key.startswith("VpcPeeringConnectionId."):
                vpc_peering_connection_ids.append(value)

        # Filter vpc peering connections
        all_peering = list(self.state.vpc_peering.values())

        # Filter by IDs if provided
        if vpc_peering_connection_ids:
            all_peering = [p for p in all_peering if p.vpcPeeringConnectionId in vpc_peering_connection_ids]

        def match_filter(peering, filter_name, filter_values):
            # Support filter names as per docs
            # Examples:
            # accepter-vpc-info.cidr-block
            # accepter-vpc-info.owner-id
            # accepter-vpc-info.vpc-id
            # expiration-time
            # requester-vpc-info.cidr-block
            # requester-vpc-info.owner-id
            # requester-vpc-info.vpc-id
            # status-code
            # status-message
            # tag:<key>
            # tag-key
            # vpc-peering-connection-id

            if filter_name == "vpc-peering-connection-id":
                return peering.vpcPeeringConnectionId in filter_values

            if filter_name.startswith("accepter-vpc-info."):
                attr = filter_name[len("accepter-vpc-info."):]
                accepter_info = peering.accepterVpcInfo
                if not accepter_info:
                    return False
                if attr == "cidr-block":
                    return accepter_info.cidrBlock in filter_values
                if attr == "owner-id":
                    return accepter_info.ownerId in filter_values
                if attr == "vpc-id":
                    return accepter_info.vpcId in filter_values
                return False

            if filter_name.startswith("requester-vpc-info."):
                attr = filter_name[len("requester-vpc-info."):]
                requester_info = peering.requesterVpcInfo
                if not requester_info:
                    return False
                if attr == "cidr-block":
                    return requester_info.cidrBlock in filter_values
                if attr == "owner-id":
                    return requester_info.ownerId in filter_values
                if attr == "vpc-id":
                    return requester_info.vpcId in filter_values
                return False

            if filter_name == "expiration-time":
                if not peering.expirationTime:
                    return False
                # Filter values are strings, compare string representation ISO8601
                return peering.expirationTime.isoformat() in filter_values

            if filter_name == "status-code":
                if not peering.status or not peering.status.code:
                    return False
                return peering.status.code.value in filter_values or peering.status.code in filter_values

            if filter_name == "status-message":
                if not peering.status or not peering.status.message:
                    return False
                return peering.status.message in filter_values

            if filter_name.startswith("tag:"):
                tag_key = filter_name[len("tag:"):]
                for tag in peering.tagSet:
                    if tag.Key == tag_key and tag.Value in filter_values:
                        return True
                return False

            if filter_name == "tag-key":
                for tag in peering.tagSet:
                    if tag.Key in filter_values:
                        return True
                return False

            return False

        filtered_peering = []
        for peering in all_peering:
            if not filters:
                filtered_peering.append(peering)
                continue
            # All filters must match (AND)
            if all(match_filter(peering, f["Name"], f["Values"]) for f in filters):
                filtered_peering.append(peering)

        # Pagination
        # NextToken is opaque string, we can treat as index offset encoded as string
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        max_results_int = 1000
        if max_results:
            try:
                max_results_int = max(5, min(1000, int(max_results)))
            except Exception:
                max_results_int = 1000

        end_index = start_index + max_results_int
        page = filtered_peering[start_index:end_index]

        new_next_token = None
        if end_index < len(filtered_peering):
            new_next_token = str(end_index)

        return {
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "vpcPeeringConnectionSet": [p.to_dict() for p in page],
        }


    def modify_vpc_peering_connection_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_peering_connection_id = params.get("VpcPeeringConnectionId")
        if not vpc_peering_connection_id:
            raise ValueError("VpcPeeringConnectionId is required")

        vpc_peering = self.state.vpc_peering.get(vpc_peering_connection_id)
        if not vpc_peering:
            raise ValueError(f"VpcPeeringConnection {vpc_peering_connection_id} does not exist")

        # Parse AccepterPeeringConnectionOptions
        accepter_opts = params.get("AccepterPeeringConnectionOptions", {})
        if not isinstance(accepter_opts, dict):
            accepter_opts = {}
        # Parse RequesterPeeringConnectionOptions
        requester_opts = params.get("RequesterPeeringConnectionOptions", {})
        if not isinstance(requester_opts, dict):
            requester_opts = {}

        # Update accepter options if provided
        if accepter_opts:
            if not vpc_peering.accepterVpcInfo:
                vpc_peering.accepterVpcInfo = VpcPeeringConnectionVpcInfo()
            if not vpc_peering.accepterVpcInfo.peeringOptions:
                vpc_peering.accepterVpcInfo.peeringOptions = VpcPeeringConnectionOptionsDescription()
            po = vpc_peering.accepterVpcInfo.peeringOptions
            if "AllowDnsResolutionFromRemoteVpc" in accepter_opts:
                po.allowDnsResolutionFromRemoteVpc = bool(accepter_opts["AllowDnsResolutionFromRemoteVpc"])
            if "AllowEgressFromLocalClassicLinkToRemoteVpc" in accepter_opts:
                po.allowEgressFromLocalClassicLinkToRemoteVpc = bool(accepter_opts["AllowEgressFromLocalClassicLinkToRemoteVpc"])
            if "AllowEgressFromLocalVpcToRemoteClassicLink" in accepter_opts:
                po.allowEgressFromLocalVpcToRemoteClassicLink = bool(accepter_opts["AllowEgressFromLocalVpcToRemoteClassicLink"])

        # Update requester options if provided
        if requester_opts:
            if not vpc_peering.requesterVpcInfo:
                vpc_peering.requesterVpcInfo = VpcPeeringConnectionVpcInfo()
            if not vpc_peering.requesterVpcInfo.peeringOptions:
                vpc_peering.requesterVpcInfo.peeringOptions = VpcPeeringConnectionOptionsDescription()
            po = vpc_peering.requesterVpcInfo.peeringOptions
            if "AllowDnsResolutionFromRemoteVpc" in requester_opts:
                po.allowDnsResolutionFromRemoteVpc = bool(requester_opts["AllowDnsResolutionFromRemoteVpc"])
            if "AllowEgressFromLocalClassicLinkToRemoteVpc" in requester_opts:
                po.allowEgressFromLocalClassicLinkToRemoteVpc = bool(requester_opts["AllowEgressFromLocalClassicLinkToRemoteVpc"])
            if "AllowEgressFromLocalVpcToRemoteClassicLink" in requester_opts:
                po.allowEgressFromLocalVpcToRemoteClassicLink = bool(requester_opts["AllowEgressFromLocalVpcToRemoteClassicLink"])

        # Save updated resource
        self.state.vpc_peering[vpc_peering_connection_id] = vpc_peering

        accepter_peering_options = None
        if vpc_peering.accepterVpcInfo and vpc_peering.accepterVpcInfo.peeringOptions:
            po = vpc_peering.accepterVpcInfo.peeringOptions
            accepter_peering_options = {
                "allowDnsResolutionFromRemoteVpc": po.allowDnsResolutionFromRemoteVpc,
                "allowEgressFromLocalClassicLinkToRemoteVpc": po.allowEgressFromLocalClassicLinkToRemoteVpc,
                "allowEgressFromLocalVpcToRemoteClassicLink": po.allowEgressFromLocalVpcToRemoteClassicLink,
            }

        requester_peering_options = None
        if vpc_peering.requesterVpcInfo and vpc_peering.requesterVpcInfo.peeringOptions:
            po = vpc_peering.requesterVpcInfo.peeringOptions
            requester_peering_options = {
                "allowDnsResolutionFromRemoteVpc": po.allowDnsResolutionFromRemoteVpc,
                "allowEgressFromLocalClassicLinkToRemoteVpc": po.allowEgressFromLocalClassicLinkToRemoteVpc,
                "allowEgressFromLocalVpcToRemoteClassicLink": po.allowEgressFromLocalVpcToRemoteClassicLink,
            }

    def reject_vpc_peering_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_peering_connection_id = params.get("VpcPeeringConnectionId")
        dry_run = params.get("DryRun", False)

        if not vpc_peering_connection_id:
            raise ValueError("VpcPeeringConnectionId is required")

        vpc_peering = self.state.vpc_peering.get(vpc_peering_connection_id)
        if not vpc_peering:
            # According to AWS behavior, if the VPC peering connection does not exist, it returns an error
            raise ValueError(f"VpcPeeringConnectionId {vpc_peering_connection_id} does not exist")

        if dry_run:
            # Check permissions - for emulator, assume always allowed
            # Return DryRunOperation error if not allowed, else raise exception or return error dict
            # Here we simulate allowed
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set"
                },
                "RequestId": self.generate_request_id()
            }

        # The VPC peering connection must be in the pending-acceptance state to reject
        # Use Enum for state check
        from enum import Enum

        class State(Enum):
            PENDING_ACCEPTANCE = "pending-acceptance"
            ACTIVE = "active"
            DELETED = "deleted"
            REJECTED = "rejected"

        current_state = vpc_peering.get("Status", {}).get("Code")
        if current_state != State.PENDING_ACCEPTANCE.value:
            # AWS returns an error if the state is not pending-acceptance
            raise ValueError(f"VpcPeeringConnection {vpc_peering_connection_id} is not in pending-acceptance state")

        # Update the state to rejected
        vpc_peering["Status"]["Code"] = State.REJECTED.value
        vpc_peering["Status"]["Message"] = "The VPC peering connection request was rejected."

        return {
            "requestId": self.generate_request_id(),
            "return": True
        }

    

from emulator_core.gateway.base import BaseGateway

class VPCpeeringGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptVpcPeeringConnection", self.accept_vpc_peering_connection)
        self.register_action("CreateVpcPeeringConnection", self.create_vpc_peering_connection)
        self.register_action("DeleteVpcPeeringConnection", self.delete_vpc_peering_connection)
        self.register_action("DescribeVpcPeeringConnections", self.describe_vpc_peering_connections)
        self.register_action("ModifyVpcPeeringConnectionOptions", self.modify_vpc_peering_connection_options)
        self.register_action("RejectVpcPeeringConnection", self.reject_vpc_peering_connection)

    def accept_vpc_peering_connection(self, params):
        return self.backend.accept_vpc_peering_connection(params)

    def create_vpc_peering_connection(self, params):
        return self.backend.create_vpc_peering_connection(params)

    def delete_vpc_peering_connection(self, params):
        return self.backend.delete_vpc_peering_connection(params)

    def describe_vpc_peering_connections(self, params):
        return self.backend.describe_vpc_peering_connections(params)

    def modify_vpc_peering_connection_options(self, params):
        return self.backend.modify_vpc_peering_connection_options(params)

    def reject_vpc_peering_connection(self, params):
        return self.backend.reject_vpc_peering_connection(params)
