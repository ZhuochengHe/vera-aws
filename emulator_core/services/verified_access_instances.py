from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class VerifiedAccessInstanceCustomSubDomain:
    sub_domain: Optional[str] = None
    nameserver_set: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.sub_domain is not None:
            d["subDomain"] = self.sub_domain
        if self.nameserver_set is not None:
            d["nameserverSet"] = self.nameserver_set
        return d


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class VerifiedAccessTrustProviderCondensed:
    verified_access_trust_provider_id: Optional[str] = None
    description: Optional[str] = None
    trust_provider_type: Optional[str] = None  # user | device
    user_trust_provider_type: Optional[str] = None  # iam-identity-center | oidc
    device_trust_provider_type: Optional[str] = None  # jamf | crowdstrike | jumpcloud

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.description is not None:
            d["description"] = self.description
        if self.device_trust_provider_type is not None:
            d["deviceTrustProviderType"] = self.device_trust_provider_type
        if self.trust_provider_type is not None:
            d["trustProviderType"] = self.trust_provider_type
        if self.user_trust_provider_type is not None:
            d["userTrustProviderType"] = self.user_trust_provider_type
        if self.verified_access_trust_provider_id is not None:
            d["verifiedAccessTrustProviderId"] = self.verified_access_trust_provider_id
        return d


@dataclass
class VerifiedAccessInstance:
    verified_access_instance_id: str
    description: Optional[str] = None
    fips_enabled: Optional[bool] = None
    creation_time: Optional[str] = None
    last_updated_time: Optional[str] = None
    cidr_endpoints_custom_sub_domain: Optional[VerifiedAccessInstanceCustomSubDomain] = None
    tags: Dict[str, str] = field(default_factory=dict)
    verified_access_trust_provider_set: List[VerifiedAccessTrustProviderCondensed] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "verifiedAccessInstanceId": self.verified_access_instance_id,
            "description": self.description,
            "fipsEnabled": self.fips_enabled,
            "creationTime": self.creation_time,
            "lastUpdatedTime": self.last_updated_time,
            "tagSet": [{"Key": k, "Value": v} for k, v in self.tags.items()],
            "verifiedAccessTrustProviderSet": [v.to_dict() for v in self.verified_access_trust_provider_set],
        }
        if self.cidr_endpoints_custom_sub_domain is not None:
            d["cidrEndpointsCustomSubDomain"] = self.cidr_endpoints_custom_sub_domain.to_dict()
        else:
            d["cidrEndpointsCustomSubDomain"] = None
        return d


class VerifiedAccessInstanceBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.verified_access_instances dict for storage

    def _validate_tags(self, tag_specifications: Optional[List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Validate and extract tags from TagSpecification.N parameter.
        Returns dict of tags.
        """
        tags: Dict[str, str] = {}
        if tag_specifications is None:
            return tags
        if not isinstance(tag_specifications, list):
            raise ErrorCode("InvalidParameterValue", "TagSpecification.N must be a list if provided")
        for tag_spec in tag_specifications:
            if not isinstance(tag_spec, dict):
                raise ErrorCode("InvalidParameterValue", "Each TagSpecification must be a dict")
            resource_type = tag_spec.get("ResourceType")
            # ResourceType is optional, but if present must be string
            if resource_type is not None and not isinstance(resource_type, str):
                raise ErrorCode("InvalidParameterValue", "ResourceType in TagSpecification must be a string")
            # We do not enforce resource type here, but could check if needed
            tag_list = tag_spec.get("Tags")
            if tag_list is None:
                continue
            if not isinstance(tag_list, list):
                raise ErrorCode("InvalidParameterValue", "Tags in TagSpecification must be a list")
            for tag in tag_list:
                if not isinstance(tag, dict):
                    raise ErrorCode("InvalidParameterValue", "Each Tag must be a dict")
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None or not isinstance(key, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Key must be a string and not None")
                if key.lower().startswith("aws:"):
                    raise ErrorCode("InvalidParameterValue", "Tag keys may not begin with aws:")
                if len(key) > 127:
                    raise ErrorCode("InvalidParameterValue", "Tag key length must be <= 127 characters")
                if value is not None and not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Value must be a string if provided")
                if value is not None and len(value) > 256:
                    raise ErrorCode("InvalidParameterValue", "Tag value length must be <= 256 characters")
                tags[key] = value if value is not None else ""
        return tags

    def create_verified_access_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        # Validate optional parameters
        cidr_subdomain = params.get("CidrEndpointsCustomSubDomain")
        if cidr_subdomain is not None and not isinstance(cidr_subdomain, str):
            raise ErrorCode("InvalidParameterValue", "CidrEndpointsCustomSubDomain must be a string if provided")

        description = params.get("Description")
        if description is not None and not isinstance(description, str):
            raise ErrorCode("InvalidParameterValue", "Description must be a string if provided")

        fips_enabled = params.get("FIPSEnabled")
        if fips_enabled is not None and not isinstance(fips_enabled, bool):
            raise ErrorCode("InvalidParameterValue", "FIPSEnabled must be a boolean if provided")

        tag_specifications = params.get("TagSpecification.N")
        tags = self._validate_tags(tag_specifications)

        # Generate ID and timestamps
        instance_id = f"vai-{self.generate_unique_id()}"
        now_iso = datetime.utcnow().isoformat() + "Z"

        # Create custom subdomain object if provided
        custom_subdomain_obj = None
        if cidr_subdomain is not None:
            # We only have a string for subdomain, no nameserverSet on create
            custom_subdomain_obj = VerifiedAccessInstanceCustomSubDomain(sub_domain=cidr_subdomain, nameserver_set=None)

        instance = VerifiedAccessInstance(
            verified_access_instance_id=instance_id,
            description=description,
            fips_enabled=fips_enabled,
            creation_time=now_iso,
            last_updated_time=now_iso,
            cidr_endpoints_custom_sub_domain=custom_subdomain_obj,
            tags=tags,
            verified_access_trust_provider_set=[],
        )

        self.state.verified_access_instances[instance_id] = instance

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessInstance": instance.to_dict(),
        }

    def delete_verified_access_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        instance_id = params.get("VerifiedAccessInstanceId")
        if not instance_id or not isinstance(instance_id, str):
            raise ErrorCode("MissingParameter", "VerifiedAccessInstanceId is required and must be a string")

        instance = self.state.verified_access_instances.get(instance_id)
        if instance is None:
            raise ErrorCode("InvalidVerifiedAccessInstanceId.NotFound", f"VerifiedAccessInstanceId {instance_id} does not exist")

        # Remove instance from state
        del self.state.verified_access_instances[instance_id]

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessInstance": instance.to_dict(),
        }

    def describe_verified_access_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        # Filters are not fully specified in detail, so we implement basic filtering by VerifiedAccessInstanceId.N
        instance_ids = params.get("VerifiedAccessInstanceId.N")
        if instance_ids is not None:
            if not isinstance(instance_ids, list) or not all(isinstance(i, str) for i in instance_ids):
                raise ErrorCode("InvalidParameterValue", "VerifiedAccessInstanceId.N must be a list of strings if provided")

        # MaxResults validation
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer if provided")
            if max_results < 5 or max_results > 200:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 5 and 200")

        # NextToken is not implemented fully (pagination), but we accept it as string or None
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string if provided")

        # Filter param is ignored for now as no detailed filter implementation is specified
        # We return all or filtered by instance_ids

        instances = list(self.state.verified_access_instances.values())
        if instance_ids is not None:
            instances = [inst for inst in instances if inst.verified_access_instance_id in instance_ids]

        # Apply MaxResults if specified
        if max_results is not None:
            instances = instances[:max_results]

        return {
            "requestId": self.generate_request_id(),
            "nextToken": None,
            "verifiedAccessInstanceSet": [inst.to_dict() for inst in instances],
        }

    def export_verified_access_instance_client_configuration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        instance_id = params.get("VerifiedAccessInstanceId")
        if not instance_id or not isinstance(instance_id, str):
            raise ErrorCode("MissingParameter", "VerifiedAccessInstanceId is required and must be a string")

        instance = self.state.verified_access_instances.get(instance_id)
        if instance is None:
            raise ErrorCode("InvalidVerifiedAccessInstanceId.NotFound", f"VerifiedAccessInstanceId {instance_id} does not exist")

        # For the purpose of the emulator, we return empty or dummy data for the client configuration
        # DeviceTrustProviderSet: list of strings (valid values: jamf | crowdstrike | jumpcloud)
        device_trust_provider_set = ["jamf", "crowdstrike", "jumpcloud"]

        # OpenVpnConfigurationSet: list of dicts with config and routeSet
        open_vpn_configuration_set = [
            {
                "config": "base64-encoded-config-placeholder",
                "routeSet": [
                    {"cidr": "0.0.0.0/0"},
                ],
            }
        ]

        # UserTrustProvider: dummy data
        user_trust_provider = {
            "authorizationEndpoint": "https://example.com/auth",
            "clientId": "client-id-placeholder",
            "clientSecret": "client-secret-placeholder",
            "issuer": "https://example.com/",
            "pkceEnabled": True,
            "publicSigningKeyEndpoint": "https://example.com/keys",
            "scopes": "openid profile email",
            "tokenEndpoint": "https://example.com/token",
            "type": "oidc",
            "userInfoEndpoint": "https://example.com/userinfo",
        }

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessInstanceId": instance_id,
            "deviceTrustProviderSet": device_trust_provider_set,
            "openVpnConfigurationSet": open_vpn_configuration_set,
            "region": self.state.region if hasattr(self.state, "region") else "us-east-1",
            "userTrustProvider": user_trust_provider,
            "version": "1.0",
        }

    def modify_verified_access_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if provided")

        instance_id = params.get("VerifiedAccessInstanceId")
        if not instance_id or not isinstance(instance_id, str):
            raise ErrorCode("MissingParameter", "VerifiedAccessInstanceId is required and must be a string")

        instance = self.state.verified_access_instances.get(instance_id)
        if instance is None:
            raise ErrorCode("InvalidVerifiedAccessInstanceId.NotFound", f"VerifiedAccessInstanceId {instance_id} does not exist")

        # Optional parameters to modify
        cidr_subdomain = params.get("CidrEndpointsCustomSubDomain")
        if cidr_subdomain is not None and not isinstance(cidr_subdomain, str):
            raise ErrorCode("InvalidParameterValue", "CidrEndpointsCustomSubDomain must be a string if provided")

        description = params.get("Description")
        if description is not None and not isinstance(description, str):
            raise ErrorCode("InvalidParameterValue", "Description must be a string if provided")

        # We do not allow modifying FIPSEnabled per API doc (not in modify params)

        # Update fields if provided
        updated = False
        if cidr_subdomain is not None:
            if instance.cidr_endpoints_custom_sub_domain is None:
                instance.cidr_endpoints_custom_sub_domain = VerifiedAccessInstanceCustomSubDomain(sub_domain=cidr_subdomain)
            else:
                instance.cidr_endpoints_custom_sub_domain.sub_domain = cidr_subdomain
            updated = True

        if description is not None:
            instance.description = description
            updated = True

        if updated:
            instance.last_updated_time = datetime.utcnow().isoformat() + "Z"

        # Save back to state (dict assignment)
        self.state.verified_access_instances[instance_id] = instance

        return {
            "requestId": self.generate_request_id(),
            "verifiedAccessInstance": instance.to_dict(),
        }

from emulator_core.gateway.base import BaseGateway

class VerifiedAccessinstancesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateVerifiedAccessInstance", self.create_verified_access_instance)
        self.register_action("DeleteVerifiedAccessInstance", self.delete_verified_access_instance)
        self.register_action("DescribeVerifiedAccessInstances", self.describe_verified_access_instances)
        self.register_action("ExportVerifiedAccessInstanceClientConfiguration", self.export_verified_access_instance_client_configuration)
        self.register_action("ModifyVerifiedAccessInstance", self.modify_verified_access_instance)

    def create_verified_access_instance(self, params):
        return self.backend.create_verified_access_instance(params)

    def delete_verified_access_instance(self, params):
        return self.backend.delete_verified_access_instance(params)

    def describe_verified_access_instances(self, params):
        return self.backend.describe_verified_access_instances(params)

    def export_verified_access_instance_client_configuration(self, params):
        return self.backend.export_verified_access_instance_client_configuration(params)

    def modify_verified_access_instance(self, params):
        return self.backend.modify_verified_access_instance(params)
