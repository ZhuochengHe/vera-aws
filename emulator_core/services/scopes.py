from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class IpamScopeState(Enum):
    CREATE_IN_PROGRESS = "create-in-progress"
    CREATE_COMPLETE = "create-complete"
    CREATE_FAILED = "create-failed"
    MODIFY_IN_PROGRESS = "modify-in-progress"
    MODIFY_COMPLETE = "modify-complete"
    MODIFY_FAILED = "modify-failed"
    DELETE_IN_PROGRESS = "delete-in-progress"
    DELETE_COMPLETE = "delete-complete"
    DELETE_FAILED = "delete-failed"
    ISOLATE_IN_PROGRESS = "isolate-in-progress"
    ISOLATE_COMPLETE = "isolate-complete"
    RESTORE_IN_PROGRESS = "restore-in-progress"


class IpamScopeType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: str
    Tags: List[Tag]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TagSpecification":
        resource_type = data.get("ResourceType")
        tags_data = data.get("Tags", [])
        tags = []
        for tag in tags_data:
            key = tag.get("Key")
            value = tag.get("Value")
            if key is None or value is None:
                raise ErrorCode("InvalidParameterValue", "Tag Key and Value must be provided")
            tags.append(Tag(Key=key, Value=value))
        return TagSpecification(ResourceType=resource_type, Tags=tags)


@dataclass
class ExternalAuthorityConfiguration:
    ExternalResourceIdentifier: Optional[str] = None
    Type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.ExternalResourceIdentifier is not None:
            d["externalResourceIdentifier"] = self.ExternalResourceIdentifier
        if self.Type is not None:
            d["type"] = self.Type
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExternalAuthorityConfiguration":
        if data is None:
            return ExternalAuthorityConfiguration()
        ext_res_id = data.get("ExternalResourceIdentifier")
        typ = data.get("Type")
        if typ is not None and typ != "infoblox":
            raise ErrorCode("InvalidParameterValue", "ExternalAuthorityConfiguration.Type must be 'infoblox' if specified")
        return ExternalAuthorityConfiguration(ExternalResourceIdentifier=ext_res_id, Type=typ)


@dataclass
class IpamScope:
    ipam_scope_id: str
    ipam_id: str
    description: Optional[str] = None
    external_authority_configuration: Optional[ExternalAuthorityConfiguration] = None
    ipam_arn: Optional[str] = None
    ipam_region: Optional[str] = None
    ipam_scope_arn: Optional[str] = None
    ipam_scope_type: Optional[IpamScopeType] = None
    is_default: bool = False
    owner_id: Optional[str] = None
    pool_count: int = 0
    state: IpamScopeState = IpamScopeState.CREATE_IN_PROGRESS
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tag_set = [{"Key": k, "Value": v} for k, v in self.tags.items()]
        return {
            "description": self.description,
            "externalAuthorityConfiguration": self.external_authority_configuration.to_dict() if self.external_authority_configuration else None,
            "ipamArn": self.ipam_arn,
            "ipamRegion": self.ipam_region,
            "ipamScopeArn": self.ipam_scope_arn,
            "ipamScopeId": self.ipam_scope_id,
            "ipamScopeType": self.ipam_scope_type.value if self.ipam_scope_type else None,
            "isDefault": self.is_default,
            "ownerId": self.owner_id,
            "poolCount": self.pool_count,
            "state": self.state.value,
            "tagSet": tag_set,
        }


class ScopesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.scopes dict for storage

    def _validate_dry_run(self, params: Dict[str, Any]) -> None:
        dry_run = params.get("DryRun", False)
        if dry_run:
            # For simplicity, assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

    def _validate_tags(self, tag_specifications: Optional[List[Dict[str, Any]]]) -> Dict[str, str]:
        tags: Dict[str, str] = {}
        if tag_specifications is None:
            return tags
        if not isinstance(tag_specifications, list):
            raise ErrorCode("InvalidParameterValue", "TagSpecification must be a list")
        for tag_spec in tag_specifications:
            if not isinstance(tag_spec, dict):
                raise ErrorCode("InvalidParameterValue", "Each TagSpecification must be a dict")
            resource_type = tag_spec.get("ResourceType")
            if resource_type != "ipam-scope":
                raise ErrorCode("InvalidParameterValue", f"TagSpecification.ResourceType must be 'ipam-scope', got {resource_type}")
            tags_list = tag_spec.get("Tags", [])
            if not isinstance(tags_list, list):
                raise ErrorCode("InvalidParameterValue", "Tags must be a list")
            for tag in tags_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None or value is None:
                    raise ErrorCode("InvalidParameterValue", "Tag Key and Value must be provided")
                if key.lower().startswith("aws:"):
                    raise ErrorCode("InvalidParameterValue", "Tag keys may not begin with 'aws:'")
                if len(key) > 127:
                    raise ErrorCode("InvalidParameterValue", "Tag key length must be <= 127")
                if len(value) > 256:
                    raise ErrorCode("InvalidParameterValue", "Tag value length must be <= 256")
                tags[key] = value
        return tags

    def _generate_arn(self, ipam_id: str, ipam_scope_id: str) -> str:
        # ARN format example: arn:aws:ec2:<region>:<account_id>:ipam-scope/<ipam_scope_id>
        region = "us-east-1"  # For emulator, fixed region or could be dynamic
        account_id = self.get_owner_id()
        return f"arn:aws:ec2:{region}:{account_id}:ipam-scope/{ipam_scope_id}"

    def create_ipam_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        ipam_id = params.get("IpamId")
        if not ipam_id or not isinstance(ipam_id, str):
            raise ErrorCode("MissingParameter", "IpamId is required and must be a string")

        # Validate Ipam exists
        ipam = self.state.get_resource(ipam_id)
        if ipam is None:
            raise ErrorCode("InvalidIpamId.NotFound", f"IPAM {ipam_id} does not exist")

        description = params.get("Description")
        if description is not None and not isinstance(description, str):
            raise ErrorCode("InvalidParameterValue", "Description must be a string")

        external_authority_config_data = params.get("ExternalAuthorityConfiguration")
        external_authority_configuration = None
        if external_authority_config_data is not None:
            if not isinstance(external_authority_config_data, dict):
                raise ErrorCode("InvalidParameterValue", "ExternalAuthorityConfiguration must be an object")
            external_authority_configuration = ExternalAuthorityConfiguration.from_dict(external_authority_config_data)

        tag_specifications = params.get("TagSpecification.N")
        tags = self._validate_tags(tag_specifications)

        # Generate unique scope id
        ipam_scope_id = f"ipam-scope-{self.generate_unique_id()}"

        # Compose ARNs
        ipam_arn = getattr(ipam, "ipam_arn", None)
        ipam_region = getattr(ipam, "region", "us-east-1")
        ipam_scope_arn = self._generate_arn(ipam_id, ipam_scope_id)

        # Determine scope type: AWS default scopes are public or private, but here no param for type is given.
        # The resource JSON does not specify a parameter for scope type on creation, so default to private.
        ipam_scope_type = IpamScopeType.PRIVATE

        # Owner id
        owner_id = self.get_owner_id()

        # Create IpamScope object
        ipam_scope = IpamScope(
            ipam_scope_id=ipam_scope_id,
            ipam_id=ipam_id,
            description=description,
            external_authority_configuration=external_authority_configuration,
            ipam_arn=ipam_arn,
            ipam_region=ipam_region,
            ipam_scope_arn=ipam_scope_arn,
            ipam_scope_type=ipam_scope_type,
            is_default=False,
            owner_id=owner_id,
            pool_count=0,
            state=IpamScopeState.CREATE_COMPLETE,
            tags=tags,
        )

        # Store in shared state dict
        self.state.scopes[ipam_scope_id] = ipam_scope

        return {
            "ipamScope": ipam_scope.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def delete_ipam_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        ipam_scope_id = params.get("IpamScopeId")
        if not ipam_scope_id or not isinstance(ipam_scope_id, str):
            raise ErrorCode("MissingParameter", "IpamScopeId is required and must be a string")

        ipam_scope = self.state.scopes.get(ipam_scope_id)
        if ipam_scope is None:
            raise ErrorCode("InvalidIpamScopeId.NotFound", f"IPAM Scope {ipam_scope_id} does not exist")

        if ipam_scope.is_default:
            raise ErrorCode("OperationNotPermitted", "Cannot delete default IPAM scopes")

        # Mark state as delete-in-progress then delete
        ipam_scope.state = IpamScopeState.DELETE_IN_PROGRESS

        # For emulator, immediately delete
        del self.state.scopes[ipam_scope_id]

        # Return info about deleted scope (simulate as if still exists)
        # We return the last known state with state DELETE_COMPLETE
        ipam_scope.state = IpamScopeState.DELETE_COMPLETE

        return {
            "ipamScope": ipam_scope.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def describe_ipam_scopes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        # Filters: Filter.N is list of dicts with Name and Values
        filters = params.get("Filter.N", [])
        if filters is not None and not isinstance(filters, list):
            raise ErrorCode("InvalidParameterValue", "Filter.N must be a list if specified")

        ipam_scope_ids = params.get("IpamScopeId.N", [])
        if ipam_scope_ids is not None and not isinstance(ipam_scope_ids, list):
            raise ErrorCode("InvalidParameterValue", "IpamScopeId.N must be a list if specified")

        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string")

        # Start with all scopes
        scopes_list = list(self.state.scopes.values())

        # Filter by IpamScopeId.N if provided
        if ipam_scope_ids:
            scopes_list = [s for s in scopes_list if s.ipam_scope_id in ipam_scope_ids]

        # Apply filters
        for f in filters:
            if not isinstance(f, dict):
                raise ErrorCode("InvalidParameterValue", "Each filter must be a dict")
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not isinstance(name, str):
                raise ErrorCode("InvalidParameterValue", "Filter Name must be a string")
            if not isinstance(values, list):
                raise ErrorCode("InvalidParameterValue", "Filter Values must be a list")

            # Supported filters (common ones for ipam scopes):
            # For simplicity, support filtering by:
            # - ipam-scope-id
            # - ipam-id
            # - state
            # - owner-id
            # - tag:key (e.g. tag:Owner)
            # - description
            # - ipam-scope-type

            if name == "ipam-scope-id":
                scopes_list = [s for s in scopes_list if s.ipam_scope_id in values]
            elif name == "ipam-id":
                scopes_list = [s for s in scopes_list if s.ipam_id in values]
            elif name == "state":
                states = set(values)
                scopes_list = [s for s in scopes_list if s.state.value in states]
            elif name == "owner-id":
                scopes_list = [s for s in scopes_list if s.owner_id in values]
            elif name.startswith("tag:"):
                tag_key = name[4:]
                scopes_list = [s for s in scopes_list if s.tags.get(tag_key) in values]
            elif name == "description":
                scopes_list = [s for s in scopes_list if s.description in values]
            elif name == "ipam-scope-type":
                scopes_list = [s for s in scopes_list if s.ipam_scope_type and s.ipam_scope_type.value in values]
            else:
                # Unknown filter name: ignore or raise? AWS usually ignores unknown filters.
                pass

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "NextToken is invalid")

        end_index = len(scopes_list)
        if max_results is not None:
            end_index = min(start_index + max_results, len(scopes_list))

        result_scopes = scopes_list[start_index:end_index]

        new_next_token = None
        if end_index < len(scopes_list):
            new_next_token = str(end_index)

        return {
            "ipamScopeSet": [scope.to_dict() for scope in result_scopes],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def modify_ipam_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_dry_run(params)

        ipam_scope_id = params.get("IpamScopeId")
        if not ipam_scope_id or not isinstance(ipam_scope_id, str):
            raise ErrorCode("MissingParameter", "IpamScopeId is required and must be a string")

        ipam_scope = self.state.scopes.get(ipam_scope_id)
        if ipam_scope is None:
            raise ErrorCode("InvalidIpamScopeId.NotFound", f"IPAM Scope {ipam_scope_id} does not exist")

        description = params.get("Description")
        if description is not None and not isinstance(description, str):
            raise ErrorCode("InvalidParameterValue", "Description must be a string")

        external_authority_config_data = params.get("ExternalAuthorityConfiguration")
        remove_external_authority = params.get("RemoveExternalAuthorityConfiguration", False)
        if remove_external_authority and external_authority_config_data is not None:
            raise ErrorCode("InvalidParameterCombination", "Cannot specify both ExternalAuthorityConfiguration and RemoveExternalAuthorityConfiguration")

        # Update description if provided
        if description is not None:
            ipam_scope.description = description

        # Update external authority configuration
        if remove_external_authority:
            ipam_scope.external_authority_configuration = None
        elif external_authority_config_data is not None:
            if not isinstance(external_authority_config_data, dict):
                raise ErrorCode("InvalidParameterValue", "ExternalAuthorityConfiguration must be an object")
            ipam_scope.external_authority_configuration = ExternalAuthorityConfiguration.from_dict(external_authority_config_data)

        # Mark state as modify-in-progress then complete
        ipam_scope.state = IpamScopeState.MODIFY_IN_PROGRESS
        # For emulator, immediately complete
        ipam_scope.state = IpamScopeState.MODIFY_COMPLETE

        return {
            "ipamScope": ipam_scope.to_dict(),
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class ScopesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateIpamScope", self.create_ipam_scope)
        self.register_action("DeleteIpamScope", self.delete_ipam_scope)
        self.register_action("DescribeIpamScopes", self.describe_ipam_scopes)
        self.register_action("ModifyIpamScope", self.modify_ipam_scope)

    def create_ipam_scope(self, params):
        return self.backend.create_ipam_scope(params)

    def delete_ipam_scope(self, params):
        return self.backend.delete_ipam_scope(params)

    def describe_ipam_scopes(self, params):
        return self.backend.describe_ipam_scopes(params)

    def modify_ipam_scope(self, params):
        return self.backend.modify_ipam_scope(params)
