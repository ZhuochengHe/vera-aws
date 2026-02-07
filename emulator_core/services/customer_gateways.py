from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class CustomerGateway:
    customer_gateway_id: str
    type: str
    ip_address: Optional[str] = None
    bgp_asn: Optional[int] = None
    bgp_asn_extended: Optional[int] = None
    certificate_arn: Optional[str] = None
    device_name: Optional[str] = None
    state: ResourceState = ResourceState.PENDING
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # Compose tagSet as list of dicts
        tag_set = [{"Key": k, "Value": v} for k, v in self.tags.items()]
        # Compose bgpAsn and bgpAsnExtended as strings if present
        bgp_asn_str = str(self.bgp_asn) if self.bgp_asn is not None else None
        bgp_asn_extended_str = str(self.bgp_asn_extended) if self.bgp_asn_extended is not None else None

        return {
            "customerGatewayId": self.customer_gateway_id,
            "state": self.state.value,
            "type": self.type,
            "ipAddress": self.ip_address,
            "bgpAsn": bgp_asn_str,
            "bgpAsnExtended": bgp_asn_extended_str,
            "certificateArn": self.certificate_arn,
            "deviceName": self.device_name,
            "tagSet": tag_set,
        }


class CustomerGatewayBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.customer_gateways dict for storage

    def _validate_tags(self, tag_specifications: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Validate and parse TagSpecification.N parameter.
        Return dict of tags.
        """
        tags: Dict[str, str] = {}

        for tag_spec in tag_specifications:
            # Validate ResourceType if present
            resource_type = tag_spec.get("ResourceType")
            if resource_type is not None and resource_type != "customer-gateway":
                raise Exception(
                    "InvalidParameterValue",
                    f"Invalid ResourceType '{resource_type}' in TagSpecification. Must be 'customer-gateway' or omitted.",
                )
            # Tags is optional
            tag_list = tag_spec.get("Tags", [])
            if not isinstance(tag_list, list):
                raise Exception("InvalidParameterValue", "Tags must be a list of Tag objects.")

            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is None:
                    raise Exception("InvalidParameterValue", "Tag Key is required.")
                if not isinstance(key, str):
                    raise Exception("InvalidParameterValue", "Tag Key must be a string.")
                if key.lower().startswith("aws:"):
                    raise Exception("InvalidParameterValue", "Tag Key may not begin with 'aws:'.")
                if len(key) > 127:
                    raise Exception("InvalidParameterValue", "Tag Key must be at most 127 characters.")
                if value is not None and not isinstance(value, str):
                    raise Exception("InvalidParameterValue", "Tag Value must be a string if provided.")
                if value is not None and len(value) > 256:
                    raise Exception("InvalidParameterValue", "Tag Value must be at most 256 characters.")
                tags[key] = value if value is not None else ""
        return tags

    def create_customer_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter Type
        vpn_type = params.get("Type")
        if vpn_type is None:
            raise Exception("MissingParameter", "Type is required.")
        if vpn_type != "ipsec.1":
            raise Exception("InvalidParameterValue", "Type must be 'ipsec.1'.")

        # Validate BgpAsn and BgpAsnExtended presence rules
        bgp_asn = params.get("BgpAsn")
        bgp_asn_extended = params.get("BgpAsnExtended")
        if bgp_asn is None and bgp_asn_extended is None:
            raise Exception(
                "MissingParameter",
                "You must specify either BgpAsn or BgpAsnExtended when creating the customer gateway.",
            )
        if bgp_asn is not None and bgp_asn_extended is not None:
            raise Exception(
                "InvalidParameterCombination",
                "You cannot specify both BgpAsn and BgpAsnExtended when creating the customer gateway.",
            )

        # Validate BgpAsn range if present
        if bgp_asn is not None:
            try:
                bgp_asn = int(bgp_asn)
            except (ValueError, TypeError):
                raise Exception("InvalidParameterValue: BgpAsn must be an integer.")
            if not (1 <= bgp_asn <= 2147483647):
                raise Exception(
                    "InvalidParameterValue: BgpAsn must be between 1 and 2,147,483,647 inclusive."
                )

        # Validate BgpAsnExtended range if present
        if bgp_asn_extended is not None:
            try:
                bgp_asn_extended = int(bgp_asn_extended)
            except (ValueError, TypeError):
                raise Exception("InvalidParameterValue: BgpAsnExtended must be an integer.")
            if not (2147483648 <= bgp_asn_extended <= 4294967295):
                raise Exception(
                    "InvalidParameterValue: BgpAsnExtended must be between 2,147,483,648 and 4,294,967,295 inclusive."
                )

        # Validate IpAddress or PublicIp (PublicIp is deprecated)
        ip_address = params.get("IpAddress")
        public_ip = params.get("PublicIp")
        if ip_address is None and public_ip is None:
            raise Exception(
                "MissingParameter",
                "You must specify either IpAddress or PublicIp (deprecated) for the customer gateway device's outside interface.",
            )
        if ip_address is not None and not isinstance(ip_address, str):
            raise Exception("InvalidParameterValue", "IpAddress must be a string.")
        if public_ip is not None:
            # Accept but prefer IpAddress if both present
            if not isinstance(public_ip, str):
                raise Exception("InvalidParameterValue", "PublicIp must be a string.")
            if ip_address is None:
                ip_address = public_ip

        # Validate DeviceName length if present
        device_name = params.get("DeviceName")
        if device_name is not None:
            if not isinstance(device_name, str):
                raise Exception("InvalidParameterValue", "DeviceName must be a string.")
            if len(device_name) > 255:
                raise Exception("InvalidParameterValue", "DeviceName must be at most 255 characters.")

        # Validate CertificateArn if present
        certificate_arn = params.get("CertificateArn")
        if certificate_arn is not None and not isinstance(certificate_arn, str):
            raise Exception("InvalidParameterValue", "CertificateArn must be a string.")

        # Validate TagSpecification.N if present
        tag_specifications = []
        # TagSpecification.N is expected as a list of dicts under key "TagSpecification.N"
        # or "TagSpecification" or "TagSpecification.N" keys - we check keys starting with "TagSpecification"
        # but per example, assume "TagSpecification.N" is passed as list of dicts
        # We accept "TagSpecification.N" or "TagSpecification" keys
        # We try to find any keys starting with "TagSpecification"
        for key in params:
            if key.startswith("TagSpecification"):
                val = params[key]
                if isinstance(val, list):
                    tag_specifications = val
                    break
        # Validate tags
        tags = self._validate_tags(tag_specifications) if tag_specifications else {}

        # Generate unique customer gateway id
        customer_gateway_id = f"cgw-{self.generate_unique_id()}"

        # Create CustomerGateway object
        customer_gateway = CustomerGateway(
            customer_gateway_id=customer_gateway_id,
            type=vpn_type,
            ip_address=ip_address,
            bgp_asn=bgp_asn,
            bgp_asn_extended=bgp_asn_extended,
            certificate_arn=certificate_arn,
            device_name=device_name,
            state=ResourceState.PENDING,
            tags=tags,
        )

        # Store in shared state dict
        self.state.customer_gateways[customer_gateway_id] = customer_gateway

        return {
            "customerGateway": customer_gateway.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def delete_customer_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter CustomerGatewayId
        customer_gateway_id = params.get("CustomerGatewayId")
        if customer_gateway_id is None:
            raise Exception("MissingParameter", "CustomerGatewayId is required.")

        # Check if customer gateway exists
        customer_gateway = self.state.customer_gateways.get(customer_gateway_id)
        if customer_gateway is None:
            raise Exception("InvalidCustomerGatewayID.NotFound", f"CustomerGatewayId {customer_gateway_id} does not exist.")

        # Check if any VPN connection references this customer gateway
        # We must check all resources for vpn connections referencing this customer gateway
        # We do not have vpn connections resource here, but per rules, we can access other resources via self.state.get_resource(id)
        # But we don't have a list of vpn connections, so we check all resources in self.state.resources for vpn connections referencing this cgw
        # We assume vpn connections have attribute customer_gateway_id
        for resource in self.state.resources.values():
            # We check if resource has attribute customer_gateway_id and if it matches
            if hasattr(resource, "customer_gateway_id") and resource.customer_gateway_id == customer_gateway_id:
                raise Exception(
                    "DependencyViolation",
                    f"Cannot delete customer gateway {customer_gateway_id} because it is associated with a VPN connection.",
                )

        # Mark state as DELETED and remove from state dict
        # AWS deletes immediately, but we mark state as DELETED for consistency
        customer_gateway.state = ResourceState.DELETED
        del self.state.customer_gateways[customer_gateway_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def describe_customer_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Optional filters:
        # CustomerGatewayId.N - list of IDs to filter by
        # Filter.N.Name and Filter.N.Value.N - filters by attributes
        # Supported filters:
        # - bgp-asn (string)
        # - customer-gateway-id (string)
        # - ip-address (string)
        # - state (string)
        # - type (string)
        # - tag:<key> (string)
        # - tag-key (string)

        # Extract CustomerGatewayId.N list
        customer_gateway_ids: Optional[List[str]] = None
        # CustomerGatewayId.N keys are like CustomerGatewayId.1, CustomerGatewayId.2, ...
        customer_gateway_ids = []
        for key, value in params.items():
            if key.startswith("CustomerGatewayId."):
                if isinstance(value, str):
                    customer_gateway_ids.append(value)
                elif isinstance(value, list):
                    customer_gateway_ids.extend(value)
        if len(customer_gateway_ids) == 0:
            customer_gateway_ids = None  # means no filter by id

        # Extract filters
        # Filters are passed as Filter.N.Name and Filter.N.Value.M
        # We parse filters into dict: filter_name -> set of values
        filters: Dict[str, List[str]] = {}
        # Collect filter names and values
        filter_names: Dict[int, str] = {}
        filter_values: Dict[int, Dict[int, str]] = {}
        for key, value in params.items():
            if key.startswith("Filter."):
                # key format: Filter.N.Name or Filter.N.Value.M
                parts = key.split(".")
                if len(parts) < 3:
                    continue
                try:
                    filter_index = int(parts[1])
                except Exception:
                    continue
                if parts[2] == "Name":
                    filter_names[filter_index] = value
                elif parts[2] == "Value":
                    # Value without index? unlikely, skip
                    continue
                elif parts[2].startswith("Value"):
                    # Value.M
                    try:
                        value_index = int(parts[3])
                    except Exception:
                        continue
                    if filter_index not in filter_values:
                        filter_values[filter_index] = {}
                    filter_values[filter_index][value_index] = value

        # Compose filters dict
        for idx, name in filter_names.items():
            values_dict = filter_values.get(idx, {})
            # Sort values by index
            values = [v for _, v in sorted(values_dict.items())]
            filters[name] = values

        # Now filter customer gateways
        result_cgs: List[CustomerGateway] = []

        # Start with all or filtered by IDs
        if customer_gateway_ids is not None:
            for cgid in customer_gateway_ids:
                cg = self.state.customer_gateways.get(cgid)
                if cg is not None:
                    result_cgs.append(cg)
        else:
            result_cgs = list(self.state.customer_gateways.values())

        # Apply filters
        def matches_filter(cg: CustomerGateway, name: str, values: List[str]) -> bool:
            # Support filters:
            # bgp-asn, customer-gateway-id, ip-address, state, type, tag:<key>, tag-key
            if name == "bgp-asn":
                # cg.bgp_asn as string
                if cg.bgp_asn is None:
                    return False
                return str(cg.bgp_asn) in values
            elif name == "customer-gateway-id":
                return cg.customer_gateway_id in values
            elif name == "ip-address":
                if cg.ip_address is None:
                    return False
                return cg.ip_address in values
            elif name == "state":
                return cg.state.value in values
            elif name == "type":
                return cg.type in values
            elif name.startswith("tag:"):
                # tag:<key>
                tag_key = name[4:]
                tag_value = cg.tags.get(tag_key)
                if tag_value is None:
                    return False
                return tag_value in values
            elif name == "tag-key":
                # Check if any tag key matches any value
                for v in values:
                    if v in cg.tags:
                        return True
                return False
            else:
                # Unknown filter name, ignore filter (AWS ignores unknown filters)
                return True

        # Filter result_cgs by all filters (AND)
        filtered_cgs = []
        for cg in result_cgs:
            if all(matches_filter(cg, fname, fvalues) for fname, fvalues in filters.items()):
                filtered_cgs.append(cg)

        # Compose response list of dicts
        customer_gateway_set = [cg.to_dict() for cg in filtered_cgs]

        return {
            "customerGatewaySet": customer_gateway_set,
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class CustomergatewaysGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateCustomerGateway", self.create_customer_gateway)
        self.register_action("DeleteCustomerGateway", self.delete_customer_gateway)
        self.register_action("DescribeCustomerGateways", self.describe_customer_gateways)

    def create_customer_gateway(self, params):
        return self.backend.create_customer_gateway(params)

    def delete_customer_gateway(self, params):
        return self.backend.delete_customer_gateway(params)

    def describe_customer_gateways(self, params):
        return self.backend.describe_customer_gateways(params)
