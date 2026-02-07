from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class InternetGatewayExclusionMode(str, Enum):
    ALLOW_BIDIRECTIONAL = "allow-bidirectional"
    ALLOW_EGRESS = "allow-egress"


class VpcBlockPublicAccessExclusionState(str, Enum):
    CREATE_IN_PROGRESS = "create-in-progress"
    CREATE_COMPLETE = "create-complete"
    CREATE_FAILED = "create-failed"
    UPDATE_IN_PROGRESS = "update-in-progress"
    UPDATE_COMPLETE = "update-complete"
    UPDATE_FAILED = "update-failed"
    DELETE_IN_PROGRESS = "delete-in-progress"
    DELETE_COMPLETE = "delete-complete"
    DISABLE_IN_PROGRESS = "disable-in-progress"
    DISABLE_COMPLETE = "disable-complete"


class ExclusionsAllowed(str, Enum):
    ALLOWED = "allowed"
    NOT_ALLOWED = "not-allowed"


class InternetGatewayBlockMode(str, Enum):
    OFF = "off"
    BLOCK_BIDIRECTIONAL = "block-bidirectional"
    BLOCK_INGRESS = "block-ingress"


class ManagedBy(str, Enum):
    ACCOUNT = "account"
    DECLARATIVE_POLICY = "declarative-policy"


class VpcBlockPublicAccessOptionsState(str, Enum):
    DEFAULT_STATE = "default-state"
    UPDATE_IN_PROGRESS = "update-in-progress"
    UPDATE_COMPLETE = "update-complete"


@dataclass
class Tag:
    Key: str
    Value: str

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
class Filter:
    Name: Optional[str] = None
    Values: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Values": self.Values,
        }


@dataclass
class VpcBlockPublicAccessExclusion:
    exclusion_id: Optional[str] = None
    internet_gateway_exclusion_mode: Optional[InternetGatewayExclusionMode] = None
    creation_timestamp: Optional[datetime] = None
    deletion_timestamp: Optional[datetime] = None
    last_update_timestamp: Optional[datetime] = None
    reason: Optional[str] = None
    resource_arn: Optional[str] = None
    state: Optional[VpcBlockPublicAccessExclusionState] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exclusionId": self.exclusion_id,
            "internetGatewayExclusionMode": self.internet_gateway_exclusion_mode.value if self.internet_gateway_exclusion_mode else None,
            "creationTimestamp": self.creation_timestamp.isoformat() if self.creation_timestamp else None,
            "deletionTimestamp": self.deletion_timestamp.isoformat() if self.deletion_timestamp else None,
            "lastUpdateTimestamp": self.last_update_timestamp.isoformat() if self.last_update_timestamp else None,
            "reason": self.reason,
            "resourceArn": self.resource_arn,
            "state": self.state.value if self.state else None,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
        }


@dataclass
class VpcBlockPublicAccessOptions:
    aws_account_id: Optional[str] = None
    aws_region: Optional[str] = None
    exclusions_allowed: Optional[ExclusionsAllowed] = None
    internet_gateway_block_mode: Optional[InternetGatewayBlockMode] = None
    last_update_timestamp: Optional[datetime] = None
    managed_by: Optional[ManagedBy] = None
    reason: Optional[str] = None
    state: Optional[VpcBlockPublicAccessOptionsState] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "awsAccountId": self.aws_account_id,
            "awsRegion": self.aws_region,
            "exclusionsAllowed": self.exclusions_allowed.value if self.exclusions_allowed else None,
            "internetGatewayBlockMode": self.internet_gateway_block_mode.value if self.internet_gateway_block_mode else None,
            "lastUpdateTimestamp": self.last_update_timestamp.isoformat() if self.last_update_timestamp else None,
            "managedBy": self.managed_by.value if self.managed_by else None,
            "reason": self.reason,
            "state": self.state.value if self.state else None,
        }


class BlockpublicaccessBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.vpc_block_public_access_exclusions and self.state.vpc_block_public_access_options

    def create_vpc_block_public_access_exclusion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from datetime import datetime
        # Validate required parameter InternetGatewayExclusionMode
        internet_gateway_exclusion_mode = params.get("InternetGatewayExclusionMode")
        if internet_gateway_exclusion_mode is None:
            raise Exception("Missing required parameter InternetGatewayExclusionMode")
        if internet_gateway_exclusion_mode not in ("allow-bidirectional", "allow-egress"):
            raise Exception("Invalid InternetGatewayExclusionMode value")

        # Optional parameters
        subnet_id = params.get("SubnetId")
        vpc_id = params.get("VpcId")
        tag_specifications = params.get("TagSpecification.N", [])

        # Generate unique exclusion ID and request ID
        exclusion_id = self.generate_unique_id()
        request_id = self.generate_request_id()
        now = datetime.utcnow()

        # Compose resource ARN based on VPC or Subnet
        resource_arn = None
        owner_id = self.get_owner_id()
        region = self.state.region if hasattr(self.state, "region") else "us-east-1"
        if vpc_id:
            resource_arn = f"arn:aws:ec2:{region}:{owner_id}:vpc/{vpc_id}"
        elif subnet_id:
            resource_arn = f"arn:aws:ec2:{region}:{owner_id}:subnet/{subnet_id}"

        # Parse tags from tag_specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Create exclusion object
        exclusion = VpcBlockPublicAccessExclusion(
            exclusion_id=exclusion_id,
            internet_gateway_exclusion_mode=InternetGatewayExclusionMode(internet_gateway_exclusion_mode),
            creation_timestamp=now,
            deletion_timestamp=None,
            last_update_timestamp=now,
            reason=None,
            resource_arn=resource_arn,
            state=VpcBlockPublicAccessExclusionState.create_in_progress,
            tag_set=tags,
        )

        # Store exclusion in state dictionary
        self.state.block_public_access[exclusion_id] = exclusion

        # Update state to create-complete (simulate immediate completion)
        exclusion.state = VpcBlockPublicAccessExclusionState.create_complete
        exclusion.last_update_timestamp = datetime.utcnow()

        return {
            "requestId": request_id,
            "vpcBlockPublicAccessExclusion": exclusion.to_dict(),
        }


    def delete_vpc_block_public_access_exclusion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from datetime import datetime
        exclusion_id = params.get("ExclusionId")
        if exclusion_id is None:
            raise Exception("Missing required parameter ExclusionId")

        request_id = self.generate_request_id()

        exclusion = self.state.block_public_access.get(exclusion_id)
        if exclusion is None:
            # According to AWS behavior, deleting a non-existent exclusion might be a no-op or error.
            # Here we raise an error.
            raise Exception(f"VpcBlockPublicAccessExclusion with ID {exclusion_id} not found")

        # Mark deletion in progress
        exclusion.state = VpcBlockPublicAccessExclusionState.delete_in_progress
        exclusion.last_update_timestamp = datetime.utcnow()

        # Mark deletion complete and set deletion timestamp
        exclusion.state = VpcBlockPublicAccessExclusionState.delete_complete
        exclusion.deletion_timestamp = datetime.utcnow()
        exclusion.last_update_timestamp = exclusion.deletion_timestamp

        # Remove from state dictionary
        del self.state.block_public_access[exclusion_id]

        return {
            "requestId": request_id,
            "vpcBlockPublicAccessExclusion": exclusion.to_dict(),
        }


    def describe_vpc_block_public_access_exclusions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Extract filters and parameters
        exclusion_ids = params.get("ExclusionId.N", [])
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Convert max_results to int and validate
        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 5 or max_results > 1000:
                    raise Exception("MaxResults must be between 5 and 1000")
            except Exception:
                raise Exception("Invalid MaxResults value")

        # Prepare list of exclusions to filter
        exclusions = list(self.state.block_public_access.values())

        # Filter by exclusion IDs if provided
        if exclusion_ids:
            exclusions = [ex for ex in exclusions if ex.exclusion_id in exclusion_ids]

        # Apply filters
        def matches_filter(exclusion: VpcBlockPublicAccessExclusion, filter_obj: Filter) -> bool:
            name = filter_obj.Name
            values = filter_obj.Values
            if not name or not values:
                return True
            if name == "resource-arn":
                return exclusion.resource_arn in values
            if name == "internet-gateway-exclusion-mode":
                return exclusion.internet_gateway_exclusion_mode.value in values
            if name == "state":
                return exclusion.state.value in values
            if name.startswith("tag:"):
                tag_key = name[4:]
                for tag in exclusion.tag_set:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False
            if name == "tag-key":
                for tag in exclusion.tag_set:
                    if tag.Key in values:
                        return True
                return False
            if name == "tag-value":
                for tag in exclusion.tag_set:
                    if tag.Value in values:
                        return True
                return False
            return True

        for filter_obj in filters:
            exclusions = [ex for ex in exclusions if matches_filter(ex, filter_obj)]

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(exclusions)
        if max_results is not None:
            end_index = min(start_index + max_results, len(exclusions))

        page = exclusions[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(exclusions) else None

        request_id = self.generate_request_id()

        return {
            "nextToken": new_next_token,
            "requestId": request_id,
            "vpcBlockPublicAccessExclusionSet": [ex.to_dict() for ex in page],
        }


    def describe_vpc_block_public_access_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        request_id = self.generate_request_id()

        # Assume only one options object per account/region
        # If not present, create a default one
        options = getattr(self.state, "vpc_block_public_access_options", None)
        if options is None:
            options = VpcBlockPublicAccessOptions(
                aws_account_id=self.get_owner_id(),
                aws_region=getattr(self.state, "region", "us-east-1"),
                exclusions_allowed=ExclusionsAllowed.allowed,
                internet_gateway_block_mode=InternetGatewayBlockMode.off,
                last_update_timestamp=None,
                managed_by=ManagedBy.account,
                reason=None,
                state=VpcBlockPublicAccessOptionsState.default_state,
            )
            self.state.vpc_block_public_access_options = options

        return {
            "requestId": request_id,
            "vpcBlockPublicAccessOptions": options.to_dict(),
        }


    def modify_vpc_block_public_access_exclusion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from datetime import datetime
        exclusion_id = params.get("ExclusionId")
        internet_gateway_exclusion_mode = params.get("InternetGatewayExclusionMode")

        if exclusion_id is None:
            raise Exception("Missing required parameter ExclusionId")
        if internet_gateway_exclusion_mode is None:
            raise Exception("Missing required parameter InternetGatewayExclusionMode")
        if internet_gateway_exclusion_mode not in ("allow-bidirectional", "allow-egress"):
            raise Exception("Invalid InternetGatewayExclusionMode value")

        exclusion = self.state.block_public_access.get(exclusion_id)
        if exclusion is None:
            raise Exception(f"VpcBlockPublicAccessExclusion with ID {exclusion_id} not found")

        # Mark update in progress
        exclusion.state = VpcBlockPublicAccessExclusionState.update_in_progress
        exclusion.last_update_timestamp = datetime.utcnow()

        # Update the exclusion mode
        exclusion.internet_gateway_exclusion_mode = InternetGatewayExclusionMode(internet_gateway_exclusion_mode)

        # Mark update complete
        exclusion.state = VpcBlockPublicAccessExclusionState.update_complete
        exclusion.last_update_timestamp = datetime.utcnow()

        request_id = self.generate_request_id()

        return {
            "requestId": request_id,
            "vpcBlockPublicAccessExclusion": exclusion.to_dict(),
        }

    def modify_vpc_block_public_access_options(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from datetime import datetime
        # Validate required parameter InternetGatewayBlockMode
        internet_gateway_block_mode = params.get("InternetGatewayBlockMode")
        if internet_gateway_block_mode is None:
            raise ValueError("Missing required parameter InternetGatewayBlockMode")
        valid_modes = {"off", "block-bidirectional", "block-ingress"}
        if internet_gateway_block_mode not in valid_modes:
            raise ValueError(f"Invalid InternetGatewayBlockMode: {internet_gateway_block_mode}")

        # DryRun parameter handling
        dry_run = params.get("DryRun", False)
        if dry_run:
            # Simulate permission check: always allow in this emulator
            # Return DryRunOperation error if permissions are missing (not implemented here)
            return {
                "Error": {
                    "Code": "DryRunOperation",
                    "Message": "Request would have succeeded, but DryRun flag is set."
                },
                "ResponseMetadata": {
                    "RequestId": self.generate_request_id()
                }
            }

        # Access the current VPC Block Public Access options from state
        bpa_options: VpcBlockPublicAccessOptions = self.state.block_public_access.get("default")
        if bpa_options is None:
            # Initialize if not present
            bpa_options = VpcBlockPublicAccessOptions()
            self.state.block_public_access["default"] = bpa_options

        # Update the internet_gateway_block_mode enum member
        # Map string to InternetGatewayBlockMode enum member
        # Assuming InternetGatewayBlockMode enum has members named exactly as the strings but uppercase and underscores
        # e.g. "off" -> InternetGatewayBlockMode.OFF
        # We need to find the enum member matching the string ignoring case and dashes replaced by underscores
        def map_mode_to_enum(mode_str: str):
            normalized = mode_str.replace("-", "_").upper()
            for member in InternetGatewayBlockMode:
                if member.name == normalized:
                    return member
            raise ValueError(f"Invalid InternetGatewayBlockMode enum value: {mode_str}")

        bpa_options.internet_gateway_block_mode = map_mode_to_enum(internet_gateway_block_mode)
        bpa_options.last_update_timestamp = datetime.utcnow()

        # The other fields remain unchanged

        # Prepare response dictionary
        response = {
            "requestId": self.generate_request_id(),
            "vpcBlockPublicAccessOptions": bpa_options.to_dict()
        }
        return response

    

from emulator_core.gateway.base import BaseGateway

class BlockpublicaccessGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateVpcBlockPublicAccessExclusion", self.create_vpc_block_public_access_exclusion)
        self.register_action("DeleteVpcBlockPublicAccessExclusion", self.delete_vpc_block_public_access_exclusion)
        self.register_action("DescribeVpcBlockPublicAccessExclusions", self.describe_vpc_block_public_access_exclusions)
        self.register_action("DescribeVpcBlockPublicAccessOptions", self.describe_vpc_block_public_access_options)
        self.register_action("ModifyVpcBlockPublicAccessExclusion", self.modify_vpc_block_public_access_exclusion)
        self.register_action("ModifyVpcBlockPublicAccessOptions", self.modify_vpc_block_public_access_options)

    def create_vpc_block_public_access_exclusion(self, params):
        return self.backend.create_vpc_block_public_access_exclusion(params)

    def delete_vpc_block_public_access_exclusion(self, params):
        return self.backend.delete_vpc_block_public_access_exclusion(params)

    def describe_vpc_block_public_access_exclusions(self, params):
        return self.backend.describe_vpc_block_public_access_exclusions(params)

    def describe_vpc_block_public_access_options(self, params):
        return self.backend.describe_vpc_block_public_access_options(params)

    def modify_vpc_block_public_access_exclusion(self, params):
        return self.backend.modify_vpc_block_public_access_exclusion(params)

    def modify_vpc_block_public_access_options(self, params):
        return self.backend.modify_vpc_block_public_access_options(params)
