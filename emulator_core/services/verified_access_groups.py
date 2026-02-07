from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Key": self.key,
            "Value": self.value,
        }


@dataclass
class TagSpecification:
    resource_type: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class VerifiedAccessSseSpecificationRequest:
    customer_managed_key_enabled: Optional[bool] = None
    kms_key_arn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CustomerManagedKeyEnabled": self.customer_managed_key_enabled,
            "KmsKeyArn": self.kms_key_arn,
        }


@dataclass
class VerifiedAccessSseSpecificationResponse:
    customer_managed_key_enabled: Optional[bool] = None
    kms_key_arn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CustomerManagedKeyEnabled": self.customer_managed_key_enabled,
            "KmsKeyArn": self.kms_key_arn,
        }


@dataclass
class VerifiedAccessGroup:
    creation_time: Optional[str] = None
    deletion_time: Optional[str] = None
    description: Optional[str] = None
    last_updated_time: Optional[str] = None
    owner: Optional[str] = None
    sse_specification: Optional[VerifiedAccessSseSpecificationResponse] = None
    tag_set: List[Tag] = field(default_factory=list)
    verified_access_group_arn: Optional[str] = None
    verified_access_group_id: Optional[str] = None
    verified_access_instance_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CreationTime": self.creation_time,
            "DeletionTime": self.deletion_time,
            "Description": self.description,
            "LastUpdatedTime": self.last_updated_time,
            "Owner": self.owner,
            "SseSpecification": self.sse_specification.to_dict() if self.sse_specification else None,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "VerifiedAccessGroupArn": self.verified_access_group_arn,
            "VerifiedAccessGroupId": self.verified_access_group_id,
            "VerifiedAccessInstanceId": self.verified_access_instance_id,
        }


@dataclass
class Filter:
    name: str
    values: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.name,
            "Values": self.values,
        }


class VerifiedAccessgroupsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.verified_access_groups

    def create_verified_access_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        client_token = params.get("ClientToken")
        description = params.get("Description")
        dry_run = params.get("DryRun")
        policy_document = params.get("PolicyDocument")
        sse_spec = params.get("SseSpecification")
        tag_specifications = params.get("TagSpecification.N", [])
        verified_access_instance_id = params.get("VerifiedAccessInstanceId")

        # Validate required parameters
        if not verified_access_instance_id:
            raise ValueError("VerifiedAccessInstanceId is required")

        # DryRun check (simulate permission check)
        if dry_run:
            # For emulator, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Generate unique ID and ARN for the Verified Access Group
        verified_access_group_id = self.generate_unique_id(prefix="vag-")
        verified_access_group_arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:verified-access-group/{verified_access_group_id}"

        # Prepare SSE specification response object
        sse_spec_response = None
        if sse_spec:
            customer_managed_key_enabled = sse_spec.get("CustomerManagedKeyEnabled")
            kms_key_arn = sse_spec.get("KmsKeyArn")
            sse_spec_response = VerifiedAccessSseSpecificationResponse(
                customer_managed_key_enabled=customer_managed_key_enabled,
                kms_key_arn=kms_key_arn,
            )
        else:
            sse_spec_response = VerifiedAccessSseSpecificationResponse(
                customer_managed_key_enabled=None,
                kms_key_arn=None,
            )

        # Prepare tags from tag specifications
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(key=key, value=value))

        now = datetime.datetime.utcnow().isoformat() + "Z"

        # Create VerifiedAccessGroup object
        verified_access_group = VerifiedAccessGroup(
            creation_time=now,
            deletion_time=None,
            description=description,
            last_updated_time=now,
            owner=self.get_owner_id(),
            sse_specification=sse_spec_response,
            tag_set=tags,
            verified_access_group_arn=verified_access_group_arn,
            verified_access_group_id=verified_access_group_id,
            verified_access_instance_id=verified_access_instance_id,
        )

        # Store in state
        self.state.verified_access_groups[verified_access_group_id] = verified_access_group
        self.state.resources[verified_access_group_id] = verified_access_group

        # Store policy document if provided
        if policy_document is not None:
            # Store policy document in a separate dict keyed by group id
            if not hasattr(self.state, "verified_access_group_policies"):
                self.state.verified_access_group_policies = {}
            self.state.verified_access_group_policies[verified_access_group_id] = {
                "PolicyDocument": policy_document,
                "PolicyEnabled": True,
            }

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessGroup": verified_access_group.to_dict(),
        }


    def delete_verified_access_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        client_token = params.get("ClientToken")
        dry_run = params.get("DryRun")
        verified_access_group_id = params.get("VerifiedAccessGroupId")

        if not verified_access_group_id:
            raise ValueError("VerifiedAccessGroupId is required")

        # DryRun check
        if dry_run:
            # For emulator, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        group = self.state.verified_access_groups.get(verified_access_group_id)
        if not group:
            # For emulator, raise error or return empty? AWS returns error, but no errors specified here.
            raise ValueError(f"VerifiedAccessGroupId {verified_access_group_id} does not exist")

        # Mark deletion time
        now = datetime.datetime.utcnow().isoformat() + "Z"
        group.deletion_time = now
        group.last_updated_time = now

        # Remove from state dicts
        del self.state.verified_access_groups[verified_access_group_id]
        if verified_access_group_id in self.state.resources:
            del self.state.resources[verified_access_group_id]

        # Remove policy if exists
        if hasattr(self.state, "verified_access_group_policies"):
            self.state.verified_access_group_policies.pop(verified_access_group_id, None)

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessGroup": group.to_dict(),
        }


    def describe_verified_access_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        filters = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        verified_access_group_ids = params.get("VerifiedAccessGroupId.N", [])
        verified_access_instance_id = params.get("VerifiedAccessInstanceId")

        # DryRun check
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        # Collect all groups
        groups = list(self.state.verified_access_groups.values())

        # Filter by VerifiedAccessGroupId if provided
        if verified_access_group_ids:
            groups = [g for g in groups if g.verified_access_group_id in verified_access_group_ids]

        # Filter by VerifiedAccessInstanceId if provided
        if verified_access_instance_id:
            groups = [g for g in groups if g.verified_access_instance_id == verified_access_instance_id]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue
            # Supported filters based on AWS docs (not exhaustive here, but implement common ones)
            # For example: "verified-access-group-id", "verified-access-instance-id", "owner", "tag:key"
            if name == "verified-access-group-id":
                groups = [g for g in groups if g.verified_access_group_id in values]
            elif name == "verified-access-instance-id":
                groups = [g for g in groups if g.verified_access_instance_id in values]
            elif name == "owner":
                groups = [g for g in groups if g.owner in values]
            elif name.startswith("tag:"):
                tag_key = name[4:]
                groups = [
                    g for g in groups
                    if any(t.key == tag_key and t.value in values for t in g.tag_set)
                ]
            # Other filters can be added as needed

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is None:
            max_results = 1000
        else:
            max_results = max(5, min(int(max_results), 1000))

        end_index = start_index + max_results
        page_groups = groups[start_index:end_index]

        new_next_token = str(end_index) if end_index < len(groups) else None

        return {
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "verifiedAccessGroupSet": [g.to_dict() for g in page_groups],
        }


    def get_verified_access_group_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        verified_access_group_id = params.get("VerifiedAccessGroupId")

        if not verified_access_group_id:
            raise ValueError("VerifiedAccessGroupId is required")

        # DryRun check
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        group = self.state.verified_access_groups.get(verified_access_group_id)
        if not group:
            raise ValueError(f"VerifiedAccessGroupId {verified_access_group_id} does not exist")

        policy_document = None
        policy_enabled = False
        if hasattr(self.state, "verified_access_group_policies"):
            policy_info = self.state.verified_access_group_policies.get(verified_access_group_id)
            if policy_info:
                policy_document = policy_info.get("PolicyDocument")
                policy_enabled = policy_info.get("PolicyEnabled", False)

        return {
            "policyDocument": policy_document,
            "policyEnabled": policy_enabled,
            "requestId": self.generate_request_id(),
        }


    def modify_verified_access_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        client_token = params.get("ClientToken")
        description = params.get("Description")
        dry_run = params.get("DryRun")
        verified_access_group_id = params.get("VerifiedAccessGroupId")
        verified_access_instance_id = params.get("VerifiedAccessInstanceId")

        if not verified_access_group_id:
            raise ValueError("VerifiedAccessGroupId is required")

        # DryRun check
        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set"}}

        group = self.state.verified_access_groups.get(verified_access_group_id)
        if not group:
            raise ValueError(f"VerifiedAccessGroupId {verified_access_group_id} does not exist")

        # Modify description if provided
        if description is not None:
            group.description = description

        # Modify VerifiedAccessInstanceId if provided
        if verified_access_instance_id is not None:
            group.verified_access_instance_id = verified_access_instance_id

        # Update last updated time
        now = datetime.datetime.utcnow().isoformat() + "Z"
        group.last_updated_time = now

        # Save back to state (dict reference already updated)
        self.state.verified_access_groups[verified_access_group_id] = group
        self.state.resources[verified_access_group_id] = group

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessGroup": group.to_dict(),
        }

    def modify_verified_access_group_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        verified_access_group_id = params.get("VerifiedAccessGroupId")
        if not verified_access_group_id:
            raise ValueError("VerifiedAccessGroupId is required")

        group = self.state.verified_access_groups.get(verified_access_group_id)
        if not group:
            raise ValueError(f"VerifiedAccessGroup with id {verified_access_group_id} does not exist")

        # DryRun check (not implemented fully, just simulate permission check)
        if params.get("DryRun"):
            # In real AWS, this would check permissions and raise DryRunOperation or UnauthorizedOperation
            # Here we just simulate success
            return {}

        # Update policy document and enabled status if provided
        policy_document = params.get("PolicyDocument")
        policy_enabled = params.get("PolicyEnabled")

        if policy_document is not None:
            group.policy_document = policy_document
        if policy_enabled is not None:
            group.policy_enabled = policy_enabled

        # Update SSE specification if provided
        sse_spec = params.get("SseSpecification")
        if sse_spec is not None:
            customer_managed_key_enabled = sse_spec.get("CustomerManagedKeyEnabled")
            kms_key_arn = sse_spec.get("KmsKeyArn")

            # Update or create sse_specification response object
            if group.sse_specification is None:
                group.sse_specification = VerifiedAccessSseSpecificationResponse(
                    customer_managed_key_enabled=customer_managed_key_enabled,
                    kms_key_arn=kms_key_arn,
                )
            else:
                if customer_managed_key_enabled is not None:
                    group.sse_specification.customer_managed_key_enabled = customer_managed_key_enabled
                if kms_key_arn is not None:
                    group.sse_specification.kms_key_arn = kms_key_arn

        request_id = self.generate_request_id()

        return {
            "policyDocument": getattr(group, "policy_document", None),
            "policyEnabled": getattr(group, "policy_enabled", None),
            "requestId": request_id,
            "sseSpecification": group.sse_specification.to_dict() if group.sse_specification else None,
        }

    

from emulator_core.gateway.base import BaseGateway

class VerifiedAccessgroupsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateVerifiedAccessGroup", self.create_verified_access_group)
        self.register_action("DeleteVerifiedAccessGroup", self.delete_verified_access_group)
        self.register_action("DescribeVerifiedAccessGroups", self.describe_verified_access_groups)
        self.register_action("GetVerifiedAccessGroupPolicy", self.get_verified_access_group_policy)
        self.register_action("ModifyVerifiedAccessGroup", self.modify_verified_access_group)
        self.register_action("ModifyVerifiedAccessGroupPolicy", self.modify_verified_access_group_policy)

    def create_verified_access_group(self, params):
        return self.backend.create_verified_access_group(params)

    def delete_verified_access_group(self, params):
        return self.backend.delete_verified_access_group(params)

    def describe_verified_access_groups(self, params):
        return self.backend.describe_verified_access_groups(params)

    def get_verified_access_group_policy(self, params):
        return self.backend.get_verified_access_group_policy(params)

    def modify_verified_access_group(self, params):
        return self.backend.modify_verified_access_group(params)

    def modify_verified_access_group_policy(self, params):
        return self.backend.modify_verified_access_group_policy(params)
