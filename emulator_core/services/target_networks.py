from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class AssociationStatusCode(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    ASSOCIATION_FAILED = "association-failed"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"


@dataclass
class AssociationStatus:
    code: AssociationStatusCode
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"Code": self.code.value}
        if self.message is not None:
            d["Message"] = self.message
        return d


@dataclass
class TargetNetwork:
    association_id: str
    client_vpn_endpoint_id: str
    target_network_id: str  # subnet id
    vpc_id: str
    security_groups: List[str] = field(default_factory=list)
    status: AssociationStatus = field(
        default_factory=lambda: AssociationStatus(AssociationStatusCode.ASSOCIATING)
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AssociationId": self.association_id,
            "ClientVpnEndpointId": self.client_vpn_endpoint_id,
            "TargetNetworkId": self.target_network_id,
            "VpcId": self.vpc_id,
            "SecurityGroups": self.security_groups.copy(),
            "Status": self.status.to_dict(),
        }


class TargetNetworksBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.target_networks dict for storage

    def _validate_client_vpn_endpoint(self, client_vpn_endpoint_id: str):
        # Validate existence of ClientVpnEndpoint resource
        client_vpn_endpoint = self.state.get_resource(client_vpn_endpoint_id)
        if client_vpn_endpoint is None:
            raise ErrorCode.ClientVpnEndpointNotFound(
                f"ClientVpnEndpoint {client_vpn_endpoint_id} does not exist"
            )
        return client_vpn_endpoint

    def _validate_vpc(self, vpc_id: str):
        vpc = self.state.get_resource(vpc_id)
        if vpc is None:
            raise ErrorCode.VpcNotFound(f"VPC {vpc_id} does not exist")
        return vpc

    def _validate_subnet(self, subnet_id: str):
        subnet = self.state.get_resource(subnet_id)
        if subnet is None:
            raise ErrorCode.SubnetNotFound(f"Subnet {subnet_id} does not exist")
        return subnet

    def _validate_security_groups(self, security_group_ids: List[str], vpc_id: str):
        if not security_group_ids:
            raise ErrorCode.InvalidParameterValue("SecurityGroupIds cannot be empty")
        if len(security_group_ids) > 5:
            raise ErrorCode.InvalidParameterValue(
                "Up to 5 security groups can be applied to an associated target network"
            )
        # Validate each security group exists and belongs to the VPC
        for sg_id in security_group_ids:
            sg = self.state.get_resource(sg_id)
            if sg is None:
                raise ErrorCode.InvalidSecurityGroupIDNotFound(
                    f"Security group {sg_id} does not exist"
                )
            if getattr(sg, "vpc_id", None) != vpc_id:
                raise ErrorCode.InvalidSecurityGroupIDNotFound(
                    f"Security group {sg_id} does not belong to VPC {vpc_id}"
                )

    def ApplySecurityGroupsToClientVpnTargetNetwork(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Required params: ClientVpnEndpointId, SecurityGroupId.N (list), VpcId
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        vpc_id = params.get("VpcId")
        # SecurityGroupId.N is an array of strings, but param keys are like SecurityGroupId.1, SecurityGroupId.2, ...
        # We must collect all keys starting with "SecurityGroupId."
        security_group_ids = []
        for key in params:
            if key.startswith("SecurityGroupId"):
                # Accept keys like SecurityGroupId, SecurityGroupId.1, SecurityGroupId.2, etc.
                val = params[key]
                if isinstance(val, list):
                    security_group_ids.extend(val)
                else:
                    security_group_ids.append(val)
        # Flatten and unique
        security_group_ids = list(dict.fromkeys(security_group_ids))

        # Validate required parameters presence
        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")
        if vpc_id is None:
            raise ErrorCode.MissingParameter("VpcId is required")
        if not security_group_ids:
            raise ErrorCode.MissingParameter("At least one SecurityGroupId is required")

        # Validate types
        if not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode.InvalidParameterValue("ClientVpnEndpointId must be a string")
        if not isinstance(vpc_id, str):
            raise ErrorCode.InvalidParameterValue("VpcId must be a string")
        if not all(isinstance(sg, str) for sg in security_group_ids):
            raise ErrorCode.InvalidParameterValue("SecurityGroupIds must be strings")

        # Validate existence of ClientVpnEndpoint and VPC
        self._validate_client_vpn_endpoint(client_vpn_endpoint_id)
        self._validate_vpc(vpc_id)
        # Validate security groups exist and belong to VPC
        self._validate_security_groups(security_group_ids, vpc_id)

        # Find all target networks associated with this ClientVpnEndpointId and VpcId
        # Apply security groups to all matching target networks
        found_any = False
        for tn in self.state.target_networks.values():
            if (
                tn.client_vpn_endpoint_id == client_vpn_endpoint_id
                and tn.vpc_id == vpc_id
            ):
                tn.security_groups = security_group_ids.copy()
                found_any = True

        if not found_any:
            # According to AWS docs, if no association exists, this call is a no-op and returns the security groups anyway
            # But we raise error for invalid association? The docs do not specify error.
            # We will allow no error and return the security groups anyway.
            pass

        return {
            "requestId": self.generate_request_id(),
            "securityGroupIds": security_group_ids,
        }

    def AssociateClientVpnTargetNetwork(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Required: ClientVpnEndpointId, SubnetId
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        subnet_id = params.get("SubnetId")
        client_token = params.get("ClientToken")  # optional

        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")
        if subnet_id is None:
            raise ErrorCode.MissingParameter("SubnetId is required")

        if not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode.InvalidParameterValue("ClientVpnEndpointId must be a string")
        if not isinstance(subnet_id, str):
            raise ErrorCode.InvalidParameterValue("SubnetId must be a string")
        if client_token is not None and not isinstance(client_token, str):
            raise ErrorCode.InvalidParameterValue("ClientToken must be a string")

        # Validate ClientVpnEndpoint and Subnet existence
        client_vpn_endpoint = self._validate_client_vpn_endpoint(client_vpn_endpoint_id)
        subnet = self._validate_subnet(subnet_id)

        # Validate that subnet's VPC matches ClientVpnEndpoint's VPC if ClientVpnEndpoint has a VPC set
        # We assume client_vpn_endpoint has attribute vpc_id
        vpc_id = getattr(subnet, "vpc_id", None)
        if vpc_id is None:
            raise ErrorCode.InvalidParameterValue(
                f"Subnet {subnet_id} does not have a VPC association"
            )
        client_vpn_vpc_id = getattr(client_vpn_endpoint, "vpc_id", None)
        if client_vpn_vpc_id is not None and client_vpn_vpc_id != vpc_id:
            raise ErrorCode.InvalidParameterValue(
                "Subnet must be in the same VPC as the Client VPN endpoint"
            )

        # Check if subnet is already associated with this ClientVpnEndpoint
        for tn in self.state.target_networks.values():
            if (
                tn.client_vpn_endpoint_id == client_vpn_endpoint_id
                and tn.target_network_id == subnet_id
            ):
                # Already associated, return existing association
                return {
                    "associationId": tn.association_id,
                    "requestId": self.generate_request_id(),
                    "status": tn.status.to_dict(),
                }

        # Check if subnet's AZ is already associated with this ClientVpnEndpoint
        # We assume subnet has attribute availability_zone
        subnet_az = getattr(subnet, "availability_zone", None)
        if subnet_az is None:
            raise ErrorCode.InvalidParameterValue(
                f"Subnet {subnet_id} does not have an availability zone"
            )
        for tn in self.state.target_networks.values():
            if tn.client_vpn_endpoint_id == client_vpn_endpoint_id:
                # Get subnet of this association
                assoc_subnet = self.state.get_resource(tn.target_network_id)
                if assoc_subnet is None:
                    continue
                assoc_az = getattr(assoc_subnet, "availability_zone", None)
                if assoc_az == subnet_az:
                    raise ErrorCode.InvalidParameterValue(
                        "Only one subnet per Availability Zone can be associated"
                    )

        # Create new association
        association_id = f"cvpn-assoc-{self.generate_unique_id()}"
        target_network = TargetNetwork(
            association_id=association_id,
            client_vpn_endpoint_id=client_vpn_endpoint_id,
            target_network_id=subnet_id,
            vpc_id=vpc_id,
            security_groups=[],
            status=AssociationStatus(AssociationStatusCode.ASSOCIATING),
        )
        self.state.target_networks[association_id] = target_network

        return {
            "associationId": association_id,
            "requestId": self.generate_request_id(),
            "status": target_network.status.to_dict(),
        }

    def DescribeClientVpnTargetNetworks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Required: ClientVpnEndpointId
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")
        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")
        if not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode.InvalidParameterValue("ClientVpnEndpointId must be a string")

        # Validate ClientVpnEndpoint existence
        self._validate_client_vpn_endpoint(client_vpn_endpoint_id)

        # Optional filters: AssociationIds.N (list), Filter.N (list of dicts), MaxResults, NextToken
        association_ids = []
        for key in params:
            if key.startswith("AssociationIds"):
                val = params[key]
                if isinstance(val, list):
                    association_ids.extend(val)
                else:
                    association_ids.append(val)
        association_ids = list(dict.fromkeys(association_ids))  # unique

        filters = []
        for key in params:
            if key.startswith("Filter"):
                # Filter.N.Name and Filter.N.Values.M
                # We need to parse filters from params keys
                # We'll collect filters by index N
                # Example keys: Filter.1.Name, Filter.1.Values.1, Filter.1.Values.2, Filter.2.Name, ...
                # We'll parse all filters and build list of dicts {Name: str, Values: List[str]}
                pass  # We'll parse below

        # Parse filters
        # Collect filter indices
        filter_indices = set()
        for key in params:
            if key.startswith("Filter."):
                parts = key.split(".")
                if len(parts) >= 2 and parts[1].isdigit():
                    filter_indices.add(int(parts[1]))
        filters = []
        for idx in sorted(filter_indices):
            name_key = f"Filter.{idx}.Name"
            values_prefix = f"Filter.{idx}.Values"
            name = params.get(name_key)
            if name is None:
                continue
            # Collect values
            values = []
            for key in params:
                if key.startswith(values_prefix):
                    # keys like Filter.1.Values.1, Filter.1.Values.2
                    parts = key.split(".")
                    if len(parts) == 4 and parts[0] == "Filter" and parts[1] == str(idx) and parts[2] == "Values":
                        val = params[key]
                        if isinstance(val, list):
                            values.extend(val)
                        else:
                            values.append(val)
            filters.append({"Name": name, "Values": values})

        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode.InvalidParameterValue("MaxResults must be an integer")
            if max_results < 5 or max_results > 1000:
                raise ErrorCode.InvalidParameterValue(
                    "MaxResults must be between 5 and 1000"
                )

        # Filter target networks by ClientVpnEndpointId first
        filtered = [
            tn
            for tn in self.state.target_networks.values()
            if tn.client_vpn_endpoint_id == client_vpn_endpoint_id
        ]

        # Filter by AssociationIds if provided
        if association_ids:
            filtered = [tn for tn in filtered if tn.association_id in association_ids]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not values:
                continue
            if name == "association-id":
                filtered = [tn for tn in filtered if tn.association_id in values]
            elif name == "target-network-id":
                filtered = [tn for tn in filtered if tn.target_network_id in values]
            elif name == "vpc-id":
                filtered = [tn for tn in filtered if tn.vpc_id in values]
            else:
                # Unknown filter name: ignore or raise error? AWS ignores unknown filters.
                pass

        # Pagination
        start_index = 0
        if next_token is not None:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken")

        end_index = len(filtered)
        if max_results is not None:
            end_index = min(start_index + max_results, len(filtered))

        page = filtered[start_index:end_index]

        new_next_token = None
        if end_index < len(filtered):
            new_next_token = str(end_index)

        # Build response list
        client_vpn_target_networks = []
        for tn in page:
            d = {
                "AssociationId": tn.association_id,
                "ClientVpnEndpointId": tn.client_vpn_endpoint_id,
                "TargetNetworkId": tn.target_network_id,
                "VpcId": tn.vpc_id,
                "SecurityGroups": tn.security_groups.copy(),
                "Status": tn.status.to_dict(),
            }
            client_vpn_target_networks.append(d)

        return {
            "requestId": self.generate_request_id(),
            "clientVpnTargetNetworks": client_vpn_target_networks,
            "nextToken": new_next_token,
        }

    def DisassociateClientVpnTargetNetwork(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Required: AssociationId, ClientVpnEndpointId
        association_id = params.get("AssociationId")
        client_vpn_endpoint_id = params.get("ClientVpnEndpointId")

        if association_id is None:
            raise ErrorCode.MissingParameter("AssociationId is required")
        if client_vpn_endpoint_id is None:
            raise ErrorCode.MissingParameter("ClientVpnEndpointId is required")

        if not isinstance(association_id, str):
            raise ErrorCode.InvalidParameterValue("AssociationId must be a string")
        if not isinstance(client_vpn_endpoint_id, str):
            raise ErrorCode.InvalidParameterValue("ClientVpnEndpointId must be a string")

        # Validate ClientVpnEndpoint existence
        self._validate_client_vpn_endpoint(client_vpn_endpoint_id)

        # Validate association exists
        target_network = self.state.target_networks.get(association_id)
        if target_network is None:
            raise ErrorCode.InvalidAssociationIDNotFound(
                f"Association {association_id} does not exist"
            )

        # Validate association belongs to ClientVpnEndpointId
        if target_network.client_vpn_endpoint_id != client_vpn_endpoint_id:
            raise ErrorCode.InvalidParameterValue(
                "AssociationId does not belong to the specified ClientVpnEndpointId"
            )

        # Update status to disassociating
        target_network.status = AssociationStatus(AssociationStatusCode.DISASSOCIATING)

        # In real AWS, disassociation is async, but here we simulate immediate disassociation
        # Remove association from state
        del self.state.target_networks[association_id]

        return {
            "associationId": association_id,
            "requestId": self.generate_request_id(),
            "status": {"Code": AssociationStatusCode.DISASSOCIATING.value},
        }

from emulator_core.gateway.base import BaseGateway

class TargetnetworksGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("ApplySecurityGroupsToClientVpnTargetNetwork", self.apply_security_groups_to_client_vpn_target_network)
        self.register_action("AssociateClientVpnTargetNetwork", self.associate_client_vpn_target_network)
        self.register_action("DescribeClientVpnTargetNetworks", self.describe_client_vpn_target_networks)
        self.register_action("DisassociateClientVpnTargetNetwork", self.disassociate_client_vpn_target_network)

    def apply_security_groups_to_client_vpn_target_network(self, params):
        return self.backend.apply_security_groups_to_client_vpn_target_network(params)

    def associate_client_vpn_target_network(self, params):
        return self.backend.associate_client_vpn_target_network(params)

    def describe_client_vpn_target_networks(self, params):
        return self.backend.describe_client_vpn_target_networks(params)

    def disassociate_client_vpn_target_network(self, params):
        return self.backend.disassociate_client_vpn_target_network(params)
