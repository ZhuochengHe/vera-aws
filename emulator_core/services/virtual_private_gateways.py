from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class VpcAttachment:
    vpc_id: str
    state: ResourceState

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vpcId": self.vpc_id,
            "state": self.state.value,
        }


@dataclass
class VpnGateway:
    vpn_gateway_id: str
    type: str
    state: ResourceState = ResourceState.PENDING
    amazon_side_asn: int = 64512
    availability_zone: Optional[str] = None
    attachments: List[VpcAttachment] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vpnGatewayId": self.vpn_gateway_id,
            "state": self.state.value,
            "type": self.type,
            "amazonSideAsn": self.amazon_side_asn,
            "availabilityZone": self.availability_zone or "",
            "attachments": [att.to_dict() for att in self.attachments],
            "tagSet": [{"Key": k, "Value": v} for k, v in self.tags.items()],
        }


class VirtualPrivateGatewayBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.virtual_private_gateways dict for storage

    def _validate_dry_run(self, params: Dict[str, Any]) -> None:
        # DryRun is optional boolean
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if specified")

    def _parse_tags_from_tag_specifications(self, params: Dict[str, Any]) -> Dict[str, str]:
        # TagSpecification.N is an array of TagSpecification objects
        # Each TagSpecification has ResourceType and Tags (array of Key/Value)
        tags: Dict[str, str] = {}
        # Collect all TagSpecification.N keys
        # They come as TagSpecification.1.ResourceType, TagSpecification.1.Tags.1.Key, etc.
        # We'll parse all keys starting with TagSpecification.
        # The params keys are flat, so we parse keys starting with "TagSpecification."
        # Example keys:
        # TagSpecification.1.ResourceType
        # TagSpecification.1.Tags.1.Key
        # TagSpecification.1.Tags.1.Value
        # TagSpecification.2.ResourceType
        # ...
        # We only apply tags if ResourceType == "vpn-gateway"
        # We collect tags from all TagSpecification.N with ResourceType == vpn-gateway

        # Find all TagSpecification.N indices
        tag_spec_indices = set()
        for key in params.keys():
            if key.startswith("TagSpecification."):
                parts = key.split(".")
                if len(parts) > 1 and parts[1].isdigit():
                    tag_spec_indices.add(int(parts[1]))
        for idx in tag_spec_indices:
            prefix = f"TagSpecification.{idx}"
            resource_type = params.get(f"{prefix}.ResourceType")
            if resource_type != "vpn-gateway":
                continue
            # Collect tags for this TagSpecification
            # Find all Tags.M.Key and Tags.M.Value for this TagSpecification
            tag_indices = set()
            for key in params.keys():
                if key.startswith(f"{prefix}.Tags."):
                    parts = key.split(".")
                    # parts example: TagSpecification, 1, Tags, 1, Key
                    if len(parts) > 4 and parts[3].isdigit():
                        tag_indices.add(int(parts[3]))
            for tag_idx in tag_indices:
                key_key = f"{prefix}.Tags.{tag_idx}.Key"
                val_key = f"{prefix}.Tags.{tag_idx}.Value"
                tag_key = params.get(key_key)
                tag_val = params.get(val_key)
                if tag_key is not None:
                    # Validate tag key constraints
                    if not isinstance(tag_key, str):
                        raise ErrorCode("InvalidParameterValue", "Tag key must be a string")
                    if tag_key.lower().startswith("aws:"):
                        raise ErrorCode("InvalidParameterValue", "Tag keys may not begin with aws:")
                    if len(tag_key) > 127:
                        raise ErrorCode("InvalidParameterValue", "Tag key length must be <= 127")
                    if tag_val is not None and not isinstance(tag_val, str):
                        raise ErrorCode("InvalidParameterValue", "Tag value must be a string")
                    if tag_val is not None and len(tag_val) > 256:
                        raise ErrorCode("InvalidParameterValue", "Tag value length must be <= 256")
                    tags[tag_key] = tag_val or ""
        return tags

    def create_vpn_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        # Required: Type (string), must be "ipsec.1"
        vpn_type = params.get("Type")
        if vpn_type is None:
            raise ErrorCode("MissingParameter", "Type is required")
        if not isinstance(vpn_type, str):
            raise ErrorCode("InvalidParameterValue", "Type must be a string")
        if vpn_type != "ipsec.1":
            raise ErrorCode("InvalidParameterValue", "Type must be 'ipsec.1'")

        # Optional: AmazonSideAsn (long)
        amazon_side_asn = params.get("AmazonSideAsn", 64512)
        if amazon_side_asn is not None:
            try:
                amazon_side_asn = int(amazon_side_asn)
            except (ValueError, TypeError):
                raise Exception("InvalidParameterValue: AmazonSideAsn must be an integer")
            # Validate ASN ranges
            if not (64512 <= amazon_side_asn <= 65534 or 4200000000 <= amazon_side_asn <= 4294967294):
                raise Exception(
                    "InvalidParameterValue: AmazonSideAsn must be in 64512-65534 or 4200000000-4294967294 range"
                )

        # Optional: AvailabilityZone (string)
        availability_zone = params.get("AvailabilityZone")
        if availability_zone is not None and not isinstance(availability_zone, str):
            raise ErrorCode("InvalidParameterValue", "AvailabilityZone must be a string")

        # Optional: TagSpecification.N
        tags = self._parse_tags_from_tag_specifications(params)

        # Create vpn gateway object
        vpn_gateway_id = f"vgw-{self.generate_unique_id()}"
        vpn_gateway = VpnGateway(
            vpn_gateway_id=vpn_gateway_id,
            type=vpn_type,
            state=ResourceState.AVAILABLE,
            amazon_side_asn=amazon_side_asn,
            availability_zone=availability_zone,
            attachments=[],
            tags=tags,
        )

        # Store in shared state dict
        self.state.virtual_private_gateways[vpn_gateway_id] = vpn_gateway

        return {
            "requestId": self.generate_request_id(),
            "vpnGateway": vpn_gateway.to_dict(),
        }

    def delete_vpn_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        vpn_gateway_id = params.get("VpnGatewayId")
        if vpn_gateway_id is None:
            raise ErrorCode("MissingParameter", "VpnGatewayId is required")
        if not isinstance(vpn_gateway_id, str):
            raise ErrorCode("InvalidParameterValue", "VpnGatewayId must be a string")

        vpn_gateway = self.state.virtual_private_gateways.get(vpn_gateway_id)
        if vpn_gateway is None:
            raise ErrorCode("InvalidVpnGatewayID.NotFound", f"VpnGateway {vpn_gateway_id} does not exist")

        # Must be detached from all VPCs before deletion
        if any(att.state != ResourceState.DETACHED for att in vpn_gateway.attachments):
            raise ErrorCode(
                "DependencyViolation",
                "Cannot delete VPN Gateway while it is attached to a VPC. Detach it first.",
            )

        # Delete from state
        del self.state.virtual_private_gateways[vpn_gateway_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_vpn_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        # Optional: VpnGatewayId.N (array of strings)
        # The params keys are like VpnGatewayId.1, VpnGatewayId.2, ...
        vpn_gateway_ids = []
        for key, value in params.items():
            if key.startswith("VpnGatewayId."):
                if not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", "VpnGatewayId must be string")
                vpn_gateway_ids.append(value)

        # Optional: Filter.N (array of Filter objects)
        # Filter.N.Name, Filter.N.Value.M
        filters = []
        filter_indices = set()
        for key in params.keys():
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) > 1 and parts[1].isdigit():
                    filter_indices.add(int(parts[1]))
        for idx in filter_indices:
            prefix = f"Filter.{idx}"
            name = params.get(f"{prefix}.Name")
            if name is None:
                continue
            values = []
            # Collect values for this filter
            for key, val in params.items():
                if key.startswith(f"{prefix}.Value."):
                    if isinstance(val, str):
                        values.append(val)
                    elif isinstance(val, list):
                        values.extend(val)
            filters.append({"Name": name, "Values": values})

        # Collect vpn gateways to describe
        if vpn_gateway_ids:
            vpn_gateways = []
            for vgw_id in vpn_gateway_ids:
                vgw = self.state.virtual_private_gateways.get(vgw_id)
                if vgw is None:
                    # AWS behavior: silently ignore unknown IDs? Or error? We'll error.
                    raise ErrorCode("InvalidVpnGatewayID.NotFound", f"VpnGateway {vgw_id} does not exist")
                vpn_gateways.append(vgw)
        else:
            vpn_gateways = list(self.state.virtual_private_gateways.values())

        # Apply filters
        def matches_filter(vgw: VpnGateway, f: Dict[str, Any]) -> bool:
            name = f["Name"]
            values = f["Values"]
            if not values:
                return True  # no values means match all
            # Support filters:
            # amazon-side-asn
            # attachment.state
            # attachment.vpc-id
            # availability-zone
            # state
            # tag:<key>
            # tag-key
            # type
            # vpn-gateway-id
            if name == "amazon-side-asn":
                return str(vgw.amazon_side_asn) in values
            elif name == "attachment.state":
                # Any attachment with matching state
                return any(att.state.value in values for att in vgw.attachments)
            elif name == "attachment.vpc-id":
                return any(att.vpc_id in values for att in vgw.attachments)
            elif name == "availability-zone":
                return (vgw.availability_zone or "") in values
            elif name == "state":
                return vgw.state.value in values
            elif name.startswith("tag:"):
                tag_key = name[4:]
                return any(vgw.tags.get(tag_key) == v for v in values)
            elif name == "tag-key":
                return any(k in values for k in vgw.tags.keys())
            elif name == "type":
                return vgw.type in values
            elif name == "vpn-gateway-id":
                return vgw.vpn_gateway_id in values
            else:
                # Unknown filter: no match
                return False

        filtered_vpn_gateways = []
        for vgw in vpn_gateways:
            if all(matches_filter(vgw, f) for f in filters):
                filtered_vpn_gateways.append(vgw)

        return {
            "requestId": self.generate_request_id(),
            "vpnGatewaySet": [vgw.to_dict() for vgw in filtered_vpn_gateways],
        }

    def attach_vpn_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        vpc_id = params.get("VpcId")
        vpn_gateway_id = params.get("VpnGatewayId")

        if vpc_id is None:
            raise ErrorCode("MissingParameter", "VpcId is required")
        if vpn_gateway_id is None:
            raise ErrorCode("MissingParameter", "VpnGatewayId is required")
        if not isinstance(vpc_id, str):
            raise ErrorCode("InvalidParameterValue", "VpcId must be a string")
        if not isinstance(vpn_gateway_id, str):
            raise ErrorCode("InvalidParameterValue", "VpnGatewayId must be a string")

        # Validate VPC exists
        vpc = self.state.get_resource(vpc_id)
        if vpc is None:
            raise ErrorCode("InvalidVpcID.NotFound", f"Vpc {vpc_id} does not exist")

        # Validate VPN Gateway exists
        vpn_gateway = self.state.virtual_private_gateways.get(vpn_gateway_id)
        if vpn_gateway is None:
            raise ErrorCode("InvalidVpnGatewayID.NotFound", f"VpnGateway {vpn_gateway_id} does not exist")

        # Check if VPN Gateway already attached to a VPC (only one allowed)
        for att in vpn_gateway.attachments:
            if att.state != ResourceState.DETACHED:
                # Already attached or attaching to a VPC
                raise ErrorCode(
                    "IncorrectState",
                    f"VpnGateway {vpn_gateway_id} is already attached to a VPC",
                )

        # Attach: add attachment with state attaching
        attachment = VpcAttachment(vpc_id=vpc_id, state=ResourceState.ATTACHING)
        vpn_gateway.attachments.append(attachment)

        # Update VPN Gateway state if needed
        if vpn_gateway.state == ResourceState.AVAILABLE:
            vpn_gateway.state = ResourceState.AVAILABLE  # no change

        return {
            "requestId": self.generate_request_id(),
            "attachment": attachment.to_dict(),
        }

    def detach_vpn_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        vpc_id = params.get("VpcId")
        vpn_gateway_id = params.get("VpnGatewayId")

        if vpc_id is None:
            raise ErrorCode("MissingParameter", "VpcId is required")
        if vpn_gateway_id is None:
            raise ErrorCode("MissingParameter", "VpnGatewayId is required")
        if not isinstance(vpc_id, str):
            raise ErrorCode("InvalidParameterValue", "VpcId must be a string")
        if not isinstance(vpn_gateway_id, str):
            raise ErrorCode("InvalidParameterValue", "VpnGatewayId must be a string")

        # Validate VPC exists
        vpc = self.state.get_resource(vpc_id)
        if vpc is None:
            raise ErrorCode("InvalidVpcID.NotFound", f"Vpc {vpc_id} does not exist")

        # Validate VPN Gateway exists
        vpn_gateway = self.state.virtual_private_gateways.get(vpn_gateway_id)
        if vpn_gateway is None:
            raise ErrorCode("InvalidVpnGatewayID.NotFound", f"VpnGateway {vpn_gateway_id} does not exist")

        # Find attachment for this VPC
        attachment = None
        for att in vpn_gateway.attachments:
            if att.vpc_id == vpc_id and att.state != ResourceState.DETACHED:
                attachment = att
                break
        if attachment is None:
            raise ErrorCode(
                "IncorrectState",
                f"VpnGateway {vpn_gateway_id} is not attached to Vpc {vpc_id}",
            )

        # Detach: set attachment state to detaching
        attachment.state = ResourceState.DETACHING

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

from emulator_core.gateway.base import BaseGateway

class VirtualprivategatewaysGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AttachVpnGateway", self.attach_vpn_gateway)
        self.register_action("CreateVpnGateway", self.create_vpn_gateway)
        self.register_action("DeleteVpnGateway", self.delete_vpn_gateway)
        self.register_action("DescribeVpnGateways", self.describe_vpn_gateways)
        self.register_action("DetachVpnGateway", self.detach_vpn_gateway)

    def attach_vpn_gateway(self, params):
        return self.backend.attach_vpn_gateway(params)

    def create_vpn_gateway(self, params):
        return self.backend.create_vpn_gateway(params)

    def delete_vpn_gateway(self, params):
        return self.backend.delete_vpn_gateway(params)

    def describe_vpn_gateways(self, params):
        return self.backend.describe_vpn_gateways(params)

    def detach_vpn_gateway(self, params):
        return self.backend.detach_vpn_gateway(params)
