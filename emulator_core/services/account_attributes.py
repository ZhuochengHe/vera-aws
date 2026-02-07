from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


@dataclass
class AccountAttributeValue:
    attribute_value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"attributeValue": self.attribute_value}


@dataclass
class AccountAttribute:
    attribute_name: str
    attribute_value_set: List[AccountAttributeValue] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attributeName": self.attribute_name,
            "attributeValueSet": [v.to_dict() for v in self.attribute_value_set],
        }


class AccountAttributesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage, use self.state.account_attributes dict

    def describe_account_attributes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun parameter if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean if specified")

        # Validate AttributeName.N parameters
        # AttributeName.N is an array of strings, keys like AttributeName.1, AttributeName.2, ...
        # Collect all keys starting with "AttributeName."
        attribute_names = []
        for key in params:
            if key.startswith("AttributeName."):
                val = params[key]
                if not isinstance(val, str):
                    raise ErrorCode(
                        "InvalidParameterValue",
                        f"Value for {key} must be a string",
                    )
                attribute_names.append(val)

        # Validate attribute names if provided
        valid_attribute_names = {"supported-platforms", "default-vpc"}
        for name in attribute_names:
            if name not in valid_attribute_names:
                raise ErrorCode(
                    "InvalidParameterValue",
                    f"Invalid attribute name '{name}'. Valid values: supported-platforms | default-vpc",
                )

        # DryRun behavior: if DryRun is True, raise DryRunOperation error
        if dry_run:
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Prepare the account attributes to return
        # According to AWS docs:
        # - supported-platforms: ["EC2", "VPC"]
        # - default-vpc: the ID of the default VPC for your account, or "none"
        # We must get default-vpc from state if possible, else "none"
        # max-instances is no longer supported and should not be returned

        # Determine default VPC ID from state
        default_vpc_id = "none"
        # The default VPC is the one with attribute 'IsDefault' == True in VPCs
        # We must scan self.state.vpcs for a VPC with IsDefault attribute True
        # But we must not call self methods, only access state directly
        # So we iterate self.state.vpcs dict values
        for vpc in self.state.vpcs.values():
            # We expect vpc to have an attribute 'is_default' or similar
            # But since no Vpc class details given here, we check attribute 'is_default' if exists
            # If not present, assume no default VPC
            if hasattr(vpc, "is_default") and vpc.is_default:
                default_vpc_id = vpc.vpc_id
                break

        # Build the full list of attributes to return
        # If attribute_names is empty, return all supported attributes
        # Else return only those requested

        def make_supported_platforms_attribute() -> AccountAttribute:
            return AccountAttribute(
                attribute_name="supported-platforms",
                attribute_value_set=[
                    AccountAttributeValue("EC2"),
                    AccountAttributeValue("VPC"),
                ],
            )

        def make_default_vpc_attribute() -> AccountAttribute:
            return AccountAttribute(
                attribute_name="default-vpc",
                attribute_value_set=[AccountAttributeValue(default_vpc_id)],
            )

        all_attributes = {
            "supported-platforms": make_supported_platforms_attribute(),
            "default-vpc": make_default_vpc_attribute(),
        }

        if attribute_names:
            # Return only requested attributes
            attributes_to_return = []
            for name in attribute_names:
                # Defensive: if name not in all_attributes, skip (should not happen due to validation)
                attr = all_attributes.get(name)
                if attr:
                    attributes_to_return.append(attr)
        else:
            # Return all supported attributes
            attributes_to_return = list(all_attributes.values())

        # Store in shared state for possible future use (not strictly required here)
        # We store by attribute_name key
        for attr in attributes_to_return:
            self.state.account_attributes[attr.attribute_name] = attr

        return {
            "accountAttributeSet": [attr.to_dict() for attr in attributes_to_return],
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class AccountattributesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeAccountAttributes", self.describe_account_attributes)

    def describe_account_attributes(self, params):
        return self.backend.describe_account_attributes(params)
