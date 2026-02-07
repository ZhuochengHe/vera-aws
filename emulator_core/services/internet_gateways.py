from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


class AttachmentState(str, Enum):
    ATTACHING = "attaching"
    ATTACHED = "attached"
    DETACHING = "detaching"
    DETACHED = "detached"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class InternetGatewayAttachment:
    state: AttachmentState
    vpc_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "vpcId": self.vpc_id,
        }


@dataclass
class InternetGateway:
    internet_gateway_id: str
    owner_id: Optional[str] = None
    attachment_set: List[InternetGatewayAttachment] = field(default_factory=list)
    tag_set: List[Tag] = field(default_factory=list)
    state: ResourceState = ResourceState.AVAILABLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "internetGatewayId": self.internet_gateway_id,
            "ownerId": self.owner_id,
            "attachmentSet": [att.to_dict() for att in self.attachment_set],
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "state": self.state.value,
        }


@dataclass
class EgressOnlyInternetGatewayAttachment:
    state: AttachmentState
    vpc_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "vpcId": self.vpc_id,
        }


@dataclass
class EgressOnlyInternetGateway:
    egress_only_internet_gateway_id: str
    attachment_set: List[EgressOnlyInternetGatewayAttachment] = field(default_factory=list)
    tag_set: List[Tag] = field(default_factory=list)
    state: ResourceState = ResourceState.AVAILABLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "egressOnlyInternetGatewayId": self.egress_only_internet_gateway_id,
            "attachmentSet": [att.to_dict() for att in self.attachment_set],
            "tagSet": [tag.to_dict() for tag in self.tag_set],
            "state": self.state.value,
        }


class InternetgatewaysBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.internet_gateways and self.state.egress_only_internet_gateways

    def attach_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        internet_gateway_id = params.get("InternetGatewayId")
        vpc_id = params.get("VpcId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            # For simplicity, assume permission is always granted
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        if not internet_gateway_id:
            raise ValueError("InternetGatewayId is required")
        if not vpc_id:
            raise ValueError("VpcId is required")

        internet_gateway = self.state.internet_gateways.get(internet_gateway_id)
        if not internet_gateway:
            raise ValueError(f"InternetGateway {internet_gateway_id} does not exist")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # Check if the internet gateway is already attached to this VPC
        for attachment in internet_gateway.attachment_set:
            if attachment.vpc_id == vpc_id and attachment.state == AttachmentState.ATTACHED:
                # Already attached, return success
                return {
                    "requestId": self.generate_request_id(),
                    "return": True,
                }
            if attachment.vpc_id == vpc_id and attachment.state == AttachmentState.ATTACHING:
                # Already attaching, return success
                return {
                    "requestId": self.generate_request_id(),
                    "return": True,
                }

        # Check if the internet gateway is attached to another VPC
        for attachment in internet_gateway.attachment_set:
            if attachment.state == AttachmentState.ATTACHED:
                raise ValueError(f"InternetGateway {internet_gateway_id} is already attached to another VPC")

        # Attach the internet gateway to the VPC
        new_attachment = InternetGatewayAttachment(
            state=AttachmentState.ATTACHED,
            vpc_id=vpc_id,
        )
        internet_gateway.attachment_set.append(new_attachment)

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def create_egress_only_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        vpc_id = params.get("VpcId")
        dry_run = params.get("DryRun", False)
        client_token = params.get("ClientToken")
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        if not vpc_id:
            raise ValueError("VpcId is required")

        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            raise ValueError(f"VPC {vpc_id} does not exist")

        # Idempotency: if client_token is provided, check if an egress-only IGW with this token exists
        if client_token:
            for eigw in self.state.egress_only_internet_gateways.values():
                if getattr(eigw, "client_token", None) == client_token:
                    # Return existing resource
                    return {
                        "clientToken": client_token,
                        "egressOnlyInternetGateway": eigw.to_dict(),
                        "requestId": self.generate_request_id(),
                    }

        egress_only_internet_gateway_id = self.generate_unique_id("eigw")

        # Parse tags from tag_specifications
        tags = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags
            if tag_spec.get("ResourceType") != "egress-only-internet-gateway":
                continue
            for tag in tag_spec.get("Tags", []):
                key = tag.get("Key")
                value = tag.get("Value")
                if key and (not key.startswith("aws:")):
                    tags.append(Tag(Key=key, Value=value))

        attachment = EgressOnlyInternetGatewayAttachment(
            state=AttachmentState.ATTACHED,
            vpc_id=vpc_id,
        )
        egress_only_igw = EgressOnlyInternetGateway(
            egress_only_internet_gateway_id=egress_only_internet_gateway_id,
            attachment_set=[attachment],
            tag_set=tags,
            state=ResourceState.AVAILABLE,
        )
        # Store client_token for idempotency
        if client_token:
            setattr(egress_only_igw, "client_token", client_token)

        self.state.egress_only_internet_gateways[egress_only_internet_gateway_id] = egress_only_igw
        self.state.resources[egress_only_internet_gateway_id] = egress_only_igw

        return {
            "clientToken": client_token,
            "egressOnlyInternetGateway": egress_only_igw.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        internet_gateway_id = self.generate_unique_id("igw")

        tags = []
        for tag_spec in tag_specifications:
            if tag_spec.get("ResourceType") != "internet-gateway":
                continue
            for tag in tag_spec.get("Tags", []):
                key = tag.get("Key")
                value = tag.get("Value")
                if key and (not key.startswith("aws:")):
                    tags.append(Tag(Key=key, Value=value))

        internet_gateway = InternetGateway(
            internet_gateway_id=internet_gateway_id,
            owner_id=self.get_owner_id(),
            attachment_set=[],
            tag_set=tags,
            state=ResourceState.AVAILABLE,
        )

        self.state.internet_gateways[internet_gateway_id] = internet_gateway
        self.state.resources[internet_gateway_id] = internet_gateway

        return {
            "internetGateway": internet_gateway.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_egress_only_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        egress_only_internet_gateway_id = params.get("EgressOnlyInternetGatewayId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        if not egress_only_internet_gateway_id:
            raise ValueError("EgressOnlyInternetGatewayId is required")

        egress_only_igw = self.state.egress_only_internet_gateways.get(egress_only_internet_gateway_id)
        if not egress_only_igw:
            raise ValueError(f"EgressOnlyInternetGateway {egress_only_internet_gateway_id} does not exist")

        # Remove from state
        del self.state.egress_only_internet_gateways[egress_only_internet_gateway_id]
        if egress_only_internet_gateway_id in self.state.resources:
            del self.state.resources[egress_only_internet_gateway_id]

        return {
            "requestId": self.generate_request_id(),
            "returnCode": True,
        }


    def delete_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        internet_gateway_id = params.get("InternetGatewayId")
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                }
            }

        if not internet_gateway_id:
            raise ValueError("InternetGatewayId is required")

        internet_gateway = self.state.internet_gateways.get(internet_gateway_id)
        if not internet_gateway:
            # LocalStack compatibility: Return success if not found (idempotent delete)
            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        # Detach from all VPCs before deletion (as per LocalStack behavior)
        for attachment in internet_gateway.attachment_set[:]:  # Copy list to avoid modification during iteration
            if attachment.state == AttachmentState.ATTACHED:
                # Detach the gateway from the VPC
                attachment.state = AttachmentState.DETACHED
                # Remove attachment from the list
                internet_gateway.attachment_set.remove(attachment)

        # Remove from state
        del self.state.internet_gateways[internet_gateway_id]
        if internet_gateway_id in self.state.resources:
            del self.state.resources[internet_gateway_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_egress_only_internet_gateways(self, params: dict) -> dict:
        egress_only_igw_ids = params.get("EgressOnlyInternetGatewayId.N", [])
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate MaxResults if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 255:
                raise ValueError("MaxResults must be an integer between 5 and 255")

        # Collect all egress-only internet gateways
        all_eigws = list(self.state.egress_only_internet_gateways.values())

        # Filter by IDs if provided
        if egress_only_igw_ids:
            all_eigws = [eigw for eigw in all_eigws if eigw.egress_only_internet_gateway_id in egress_only_igw_ids]

        # Helper to match tags filter
        def match_tags(eigw, filter_name, filter_values):
            if filter_name == "tag-key":
                # filter_values are tag keys
                return any(tag.Key in filter_values for tag in eigw.tag_set)
            elif filter_name.startswith("tag:"):
                # filter_name is like "tag:Owner"
                tag_key = filter_name[4:]
                return any(tag.Key == tag_key and tag.Value in filter_values for tag in eigw.tag_set)
            return False

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            if name == "egress-only-internet-gateway-id":
                all_eigws = [eigw for eigw in all_eigws if eigw.egress_only_internet_gateway_id in values]
            elif name.startswith("tag") or name == "tag-key":
                all_eigws = [eigw for eigw in all_eigws if match_tags(eigw, name, values)]

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_eigws)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_eigws))

        page_items = all_eigws[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(all_eigws):
            new_next_token = str(end_index)

        # Build response
        response = {
            "egressOnlyInternetGatewaySet": [eigw.to_dict() for eigw in page_items],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def describe_internet_gateways(self, params: dict) -> dict:
        internet_gateway_ids = params.get("InternetGatewayId.N", [])
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Validate MaxResults if provided
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 5 and 1000")

        # Collect all internet gateways
        all_igws = list(self.state.internet_gateways.values())

        # Filter by IDs if provided
        if internet_gateway_ids:
            all_igws = [igw for igw in all_igws if igw.internet_gateway_id in internet_gateway_ids]

        # Helper to match tags filter
        def match_tags(igw, filter_name, filter_values):
            if filter_name == "tag-key":
                return any(tag.Key in filter_values for tag in igw.tag_set)
            elif filter_name.startswith("tag:"):
                tag_key = filter_name[4:]
                return any(tag.Key == tag_key and tag.Value in filter_values for tag in igw.tag_set)
            return False

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            if name == "attachment.state":
                # Filter by attachment state
                filtered_igws = []
                for igw in all_igws:
                    if any(att.state.name.lower() in [v.lower() for v in values] for att in igw.attachment_set):
                        filtered_igws.append(igw)
                all_igws = filtered_igws
            elif name == "attachment.vpc-id":
                filtered_igws = []
                for igw in all_igws:
                    if any(att.vpc_id in values for att in igw.attachment_set):
                        filtered_igws.append(igw)
                all_igws = filtered_igws
            elif name == "internet-gateway-id":
                all_igws = [igw for igw in all_igws if igw.internet_gateway_id in values]
            elif name == "owner-id":
                all_igws = [igw for igw in all_igws if igw.owner_id in values]
            elif name.startswith("tag") or name == "tag-key":
                all_igws = [igw for igw in all_igws if match_tags(igw, name, values)]

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(all_igws)
        if max_results is not None:
            end_index = min(start_index + max_results, len(all_igws))

        page_items = all_igws[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(all_igws):
            new_next_token = str(end_index)

        # Build response
        response = {
            "internetGatewaySet": [igw.to_dict() for igw in page_items],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }
        return response


    def detach_internet_gateway(self, params: dict) -> dict:
        internet_gateway_id = params.get("InternetGatewayId")
        vpc_id = params.get("VpcId")

        if not internet_gateway_id:
            raise ValueError("InternetGatewayId is required")
        if not vpc_id:
            raise ValueError("VpcId is required")

        igw = self.state.internet_gateways.get(internet_gateway_id)
        if igw is None:
            raise ValueError(f"InternetGateway {internet_gateway_id} does not exist")

        # Find attachment to the specified VPC
        attachment_to_remove = None
        for att in igw.attachment_set:
            if att.vpc_id == vpc_id:
                attachment_to_remove = att
                break

        if attachment_to_remove is None:
            raise ValueError(f"InternetGateway {internet_gateway_id} is not attached to VPC {vpc_id}")

        # Detach: remove the attachment from the internet gateway
        igw.attachment_set.remove(attachment_to_remove)

        # Also update the state.resources if needed (not specified but consistent)
        # No direct VPC object modification here as per instructions

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    

from emulator_core.gateway.base import BaseGateway

class InternetgatewaysGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AttachInternetGateway", self.attach_internet_gateway)
        self.register_action("CreateEgressOnlyInternetGateway", self.create_egress_only_internet_gateway)
        self.register_action("CreateInternetGateway", self.create_internet_gateway)
        self.register_action("DeleteEgressOnlyInternetGateway", self.delete_egress_only_internet_gateway)
        self.register_action("DeleteInternetGateway", self.delete_internet_gateway)
        self.register_action("DescribeEgressOnlyInternetGateways", self.describe_egress_only_internet_gateways)
        self.register_action("DescribeInternetGateways", self.describe_internet_gateways)
        self.register_action("DetachInternetGateway", self.detach_internet_gateway)

    def attach_internet_gateway(self, params):
        return self.backend.attach_internet_gateway(params)

    def create_egress_only_internet_gateway(self, params):
        return self.backend.create_egress_only_internet_gateway(params)

    def create_internet_gateway(self, params):
        return self.backend.create_internet_gateway(params)

    def delete_egress_only_internet_gateway(self, params):
        return self.backend.delete_egress_only_internet_gateway(params)

    def delete_internet_gateway(self, params):
        return self.backend.delete_internet_gateway(params)

    def describe_egress_only_internet_gateways(self, params):
        return self.backend.describe_egress_only_internet_gateways(params)

    def describe_internet_gateways(self, params):
        return self.backend.describe_internet_gateways(params)

    def detach_internet_gateway(self, params):
        return self.backend.detach_internet_gateway(params)
