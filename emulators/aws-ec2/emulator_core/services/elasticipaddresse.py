from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import re
from ..utils import (get_scalar, get_int, get_indexed_list, parse_filters, apply_filters,
                    parse_tags, str2bool, esc, create_error_response,
                    is_error_response, serialize_error_response)
from ..state import EC2State

class ResourceState(Enum):
    PENDING = 'pending'
    AVAILABLE = 'available'
    RUNNING = 'running'
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    NONEXISTENT = 'non-existent'
    FAILED = 'failed'
    SHUTTING_DOWN = 'shutting-down'
    STOPPING = 'stopping'
    STARTING = 'starting'
    REBOOTING = 'rebooting'
    ATTACHED = 'attached'
    IN_USE = 'in-use'
    CREATING = 'creating'

class ErrorCode(Enum):
    INVALID_PARAMETER_VALUE = 'InvalidParameterValue'
    RESOURCE_NOT_FOUND = 'ResourceNotFound'
    INVALID_STATE_TRANSITION = 'InvalidStateTransition'
    DEPENDENCY_VIOLATION = 'DependencyViolation'

@dataclass
class ElasticIpAddresse:
    allocation_id: str = ""
    association_id: str = ""
    carrier_ip: str = ""
    customer_owned_ip: str = ""
    customer_owned_ipv4_pool: str = ""
    domain: str = ""
    instance_id: str = ""
    network_border_group: str = ""
    network_interface_id: str = ""
    network_interface_owner_id: str = ""
    private_ip_address: str = ""
    public_ip: str = ""
    public_ipv4_pool: str = ""
    service_managed: str = ""
    subnet_id: str = ""
    tag_set: List[Any] = field(default_factory=list)

    ptr_record: str = ""
    ptr_record_update: Dict[str, Any] = field(default_factory=dict)
    address_transfer_status: str = ""
    transfer_account_id: str = ""
    transfer_offer_accepted_timestamp: Optional[str] = None
    transfer_offer_expiration_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allocationId": self.allocation_id,
            "associationId": self.association_id,
            "carrierIp": self.carrier_ip,
            "customerOwnedIp": self.customer_owned_ip,
            "customerOwnedIpv4Pool": self.customer_owned_ipv4_pool,
            "domain": self.domain,
            "instanceId": self.instance_id,
            "networkBorderGroup": self.network_border_group,
            "networkInterfaceId": self.network_interface_id,
            "networkInterfaceOwnerId": self.network_interface_owner_id,
            "privateIpAddress": self.private_ip_address,
            "publicIp": self.public_ip,
            "publicIpv4Pool": self.public_ipv4_pool,
            "serviceManaged": self.service_managed,
            "subnetId": self.subnet_id,
            "tagSet": self.tag_set,
            "ptrRecord": self.ptr_record,
            "ptrRecordUpdate": self.ptr_record_update,
            "addressTransferStatus": self.address_transfer_status,
            "transferAccountId": self.transfer_account_id,
            "transferOfferAcceptedTimestamp": self.transfer_offer_accepted_timestamp,
            "transferOfferExpirationTimestamp": self.transfer_offer_expiration_timestamp,
        }

class ElasticIpAddresse_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.elastic_ip_addresses  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.instances.get(params['instance_id']).elastic_ip_addresse_ids.append(new_id)
    #   Delete: self.state.instances.get(resource.instance_id).elastic_ip_addresse_ids.remove(resource_id)
    #   Create: self.state.transit_gateway_multicast.get(params['network_interface_id']).elastic_ip_addresse_ids.append(new_id)
    #   Delete: self.state.transit_gateway_multicast.get(resource.network_interface_id).elastic_ip_addresse_ids.remove(resource_id)
    #   Create: self.state.subnets.get(params['subnet_id']).elastic_ip_addresse_ids.append(new_id)
    #   Delete: self.state.subnets.get(resource.subnet_id).elastic_ip_addresse_ids.remove(resource_id)

    def _find_by_allocation_id(self, allocation_id: str) -> Optional[ElasticIpAddresse]:
        if not allocation_id:
            return None
        return self.resources.get(allocation_id)

    def _find_by_public_ip(self, public_ip: str) -> Optional[ElasticIpAddresse]:
        if not public_ip:
            return None
        for resource in self.resources.values():
            if resource.public_ip == public_ip:
                return resource
        return None

    def _find_by_association_id(self, association_id: str) -> Optional[ElasticIpAddresse]:
        if not association_id:
            return None
        for resource in self.resources.values():
            if resource.association_id == association_id:
                return resource
        return None

    def _build_address_transfer_dict(self, resource: ElasticIpAddresse) -> Dict[str, Any]:
        return {
            "addressTransferStatus": resource.address_transfer_status,
            "allocationId": resource.allocation_id,
            "publicIp": resource.public_ip,
            "transferAccountId": resource.transfer_account_id,
            "transferOfferAcceptedTimestamp": resource.transfer_offer_accepted_timestamp,
            "transferOfferExpirationTimestamp": resource.transfer_offer_expiration_timestamp,
        }

    def _build_address_attribute_dict(self, resource: ElasticIpAddresse) -> Dict[str, Any]:
        return {
            "allocationId": resource.allocation_id,
            "ptrRecord": resource.ptr_record,
            "ptrRecordUpdate": resource.ptr_record_update,
            "publicIp": resource.public_ip,
        }

    def _register_parent_links(self, resource_id: str, resource: ElasticIpAddresse) -> None:
        if resource.instance_id:
            parent = self.state.instances.get(resource.instance_id)
            if parent and hasattr(parent, "elastic_ip_addresse_ids"):
                if resource_id not in parent.elastic_ip_addresse_ids:
                    parent.elastic_ip_addresse_ids.append(resource_id)
        if resource.network_interface_id:
            parent = self.state.transit_gateway_multicast.get(resource.network_interface_id)
            if parent and hasattr(parent, "elastic_ip_addresse_ids"):
                if resource_id not in parent.elastic_ip_addresse_ids:
                    parent.elastic_ip_addresse_ids.append(resource_id)
        if resource.subnet_id:
            parent = self.state.subnets.get(resource.subnet_id)
            if parent and hasattr(parent, "elastic_ip_addresse_ids"):
                if resource_id not in parent.elastic_ip_addresse_ids:
                    parent.elastic_ip_addresse_ids.append(resource_id)

    def _deregister_parent_links(self, resource_id: str, resource: ElasticIpAddresse) -> None:
        if resource.instance_id:
            parent = self.state.instances.get(resource.instance_id)
            if parent and hasattr(parent, "elastic_ip_addresse_ids"):
                if resource_id in parent.elastic_ip_addresse_ids:
                    parent.elastic_ip_addresse_ids.remove(resource_id)
        if resource.network_interface_id:
            parent = self.state.transit_gateway_multicast.get(resource.network_interface_id)
            if parent and hasattr(parent, "elastic_ip_addresse_ids"):
                if resource_id in parent.elastic_ip_addresse_ids:
                    parent.elastic_ip_addresse_ids.remove(resource_id)
        if resource.subnet_id:
            parent = self.state.subnets.get(resource.subnet_id)
            if parent and hasattr(parent, "elastic_ip_addresse_ids"):
                if resource_id in parent.elastic_ip_addresse_ids:
                    parent.elastic_ip_addresse_ids.remove(resource_id)

    def _utc_now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def AcceptAddressTransfer(self, params: Dict[str, Any]):
        """Accepts an Elastic IP address transfer. For more information, seeAccept a transferred Elastic IP addressin theAmazon VPC User Guide."""

        address = params.get("Address")
        if not address:
            return create_error_response("MissingParameter", "Missing required parameter: Address")

        resource = self._find_by_public_ip(address)
        if not resource:
            return create_error_response("InvalidAddress.NotFound", f"The ID '{address}' does not exist")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "elastic-ip":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)
        if tag_set:
            resource.tag_set = tag_set

        resource.address_transfer_status = "accepted"
        resource.transfer_offer_accepted_timestamp = self._utc_now_iso()

        return {
            'addressTransfer': self._build_address_transfer_dict(resource),
            }

    def AllocateAddress(self, params: Dict[str, Any]):
        """Allocates an Elastic IP address to your AWS account. After you allocate the Elastic IP address you can associate  
         it with an instance or network interface. After you release an Elastic IP address, it is released to the IP address 
         pool and can be allocated to a different AWS accou"""

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "elastic-ip":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        allocation_id = self._generate_id("eipalloc")
        public_ip = params.get("Address") or f"198.51.100.{(uuid.uuid4().int % 250) + 1}"
        resource = ElasticIpAddresse(
            allocation_id=allocation_id,
            carrier_ip="",
            customer_owned_ip="",
            customer_owned_ipv4_pool=params.get("CustomerOwnedIpv4Pool") or "",
            domain=params.get("Domain") or "vpc",
            network_border_group=params.get("NetworkBorderGroup") or "",
            public_ip=public_ip,
            public_ipv4_pool=params.get("PublicIpv4Pool") or "",
            tag_set=tag_set,
        )
        self.resources[allocation_id] = resource

        return {
            'allocationId': allocation_id,
            'carrierIp': resource.carrier_ip,
            'customerOwnedIp': resource.customer_owned_ip,
            'customerOwnedIpv4Pool': resource.customer_owned_ipv4_pool,
            'domain': resource.domain,
            'networkBorderGroup': resource.network_border_group,
            'publicIp': resource.public_ip,
            'publicIpv4Pool': resource.public_ipv4_pool,
            }

    def AssociateAddress(self, params: Dict[str, Any]):
        """Associates an Elastic IP address, or carrier IP address (for instances that are in
      subnets in Wavelength Zones) with an instance or a network interface. Before you can use an
      Elastic IP address, you must allocate it to your account. If the Elastic IP address is already
      associated w"""

        allocation_id = params.get("AllocationId")
        public_ip = params.get("PublicIp")
        if not allocation_id and not public_ip:
            return create_error_response("MissingParameter", "Missing required parameter: AllocationId or PublicIp")

        instance_id = params.get("InstanceId")
        network_interface_id = params.get("NetworkInterfaceId")
        if not instance_id and not network_interface_id:
            return create_error_response("MissingParameter", "Missing required parameter: InstanceId or NetworkInterfaceId")

        if allocation_id:
            resource = self.resources.get(allocation_id)
            if not resource:
                return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")
        else:
            resource = self._find_by_public_ip(public_ip)
            if not resource:
                return create_error_response("InvalidAddress.NotFound", f"The ID '{public_ip}' does not exist")

        if instance_id:
            instance = self.state.instances.get(instance_id)
            if not instance:
                return create_error_response("InvalidInstanceID.NotFound", f"The ID '{instance_id}' does not exist")
        if network_interface_id:
            network_interface = self.state.elastic_network_interfaces.get(network_interface_id)
            if not network_interface:
                return create_error_response("InvalidNetworkInterfaceID.NotFound", f"The ID '{network_interface_id}' does not exist")

        allow_reassociation = str2bool(params.get("AllowReassociation"))
        if resource.association_id and not allow_reassociation:
            return create_error_response("InvalidParameterValue", "Address is already associated")

        if resource.association_id and allow_reassociation:
            self._deregister_parent_links(resource.allocation_id, resource)

        resource.association_id = self._generate_id("eipassoc")
        resource.instance_id = instance_id or ""
        resource.network_interface_id = network_interface_id or ""
        resource.private_ip_address = params.get("PrivateIpAddress") or ""
        self._register_parent_links(resource.allocation_id, resource)

        return {
            'associationId': resource.association_id,
            }

    def DescribeAddresses(self, params: Dict[str, Any]):
        """Describes the specified Elastic IP addresses or all of your Elastic IP addresses."""

        allocation_ids = params.get("AllocationId.N", []) or []
        public_ips = params.get("PublicIp.N", []) or []
        filters = params.get("Filter.N", []) or []

        resources: List[ElasticIpAddresse] = []
        if allocation_ids:
            for allocation_id in allocation_ids:
                resource = self.resources.get(allocation_id)
                if not resource:
                    return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")
                resources.append(resource)
        elif public_ips:
            for public_ip in public_ips:
                resource = self._find_by_public_ip(public_ip)
                if not resource:
                    return create_error_response("InvalidAddress.NotFound", f"The ID '{public_ip}' does not exist")
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        if filters:
            resources = apply_filters(resources, filters)

        return {
            'addressesSet': [resource.to_dict() for resource in resources],
            }

    def DescribeAddressesAttribute(self, params: Dict[str, Any]):
        """Describes the attributes of the specified Elastic IP addresses. For requirements, seeUsing reverse DNS for email applications."""

        allocation_ids = params.get("AllocationId.N", []) or []
        if allocation_ids:
            resources: List[ElasticIpAddresse] = []
            for allocation_id in allocation_ids:
                resource = self.resources.get(allocation_id)
                if not resource:
                    return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        address_set = [self._build_address_attribute_dict(resource) for resource in resources]

        return {
            'addressSet': address_set,
            'nextToken': None,
            }

    def DescribeAddressTransfers(self, params: Dict[str, Any]):
        """Describes an Elastic IP address transfer. For more information, seeTransfer Elastic IP addressesin theAmazon VPC User Guide. When you transfer an Elastic IP address, there is a two-step handshake
      between the source and transfer AWS accounts. When the source account starts the transfer,
      t"""

        allocation_ids = params.get("AllocationId.N", []) or []
        if allocation_ids:
            resources: List[ElasticIpAddresse] = []
            for allocation_id in allocation_ids:
                resource = self.resources.get(allocation_id)
                if not resource:
                    return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        address_transfer_set = [self._build_address_transfer_dict(resource) for resource in resources]

        return {
            'addressTransferSet': address_transfer_set,
            'nextToken': None,
            }

    def DisableAddressTransfer(self, params: Dict[str, Any]):
        """Disables Elastic IP address transfer. For more information, seeTransfer Elastic IP addressesin theAmazon VPC User Guide."""

        allocation_id = params.get("AllocationId")
        if not allocation_id:
            return create_error_response("MissingParameter", "Missing required parameter: AllocationId")

        resource = self.resources.get(allocation_id)
        if not resource:
            return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")

        resource.address_transfer_status = "disabled"
        resource.transfer_account_id = ""
        resource.transfer_offer_accepted_timestamp = None
        resource.transfer_offer_expiration_timestamp = None

        return {
            'addressTransfer': self._build_address_transfer_dict(resource),
            }

    def DisassociateAddress(self, params: Dict[str, Any]):
        """Disassociates an Elastic IP address from the instance or network interface it's associated with. This is an idempotent operation. If you perform the operation more than once, Amazon EC2 doesn't return an error. An address cannot be disassociated if the all of the following conditions are met:"""

        association_id = params.get("AssociationId")
        public_ip = params.get("PublicIp")
        if not association_id and not public_ip:
            return create_error_response("MissingParameter", "Missing required parameter: AssociationId or PublicIp")

        if association_id:
            resource = self._find_by_association_id(association_id)
            if not resource:
                return create_error_response("InvalidAssociationID.NotFound", f"The ID '{association_id}' does not exist")
        else:
            resource = self._find_by_public_ip(public_ip)
            if not resource:
                return create_error_response("InvalidAddress.NotFound", f"The ID '{public_ip}' does not exist")

        if resource.association_id:
            self._deregister_parent_links(resource.allocation_id, resource)
            resource.association_id = ""
            resource.instance_id = ""
            resource.network_interface_id = ""
            resource.private_ip_address = ""

        return {
            'return': True,
            }

    def EnableAddressTransfer(self, params: Dict[str, Any]):
        """Enables Elastic IP address transfer. For more information, seeTransfer Elastic IP addressesin theAmazon VPC User Guide."""

        allocation_id = params.get("AllocationId")
        transfer_account_id = params.get("TransferAccountId")
        if not allocation_id:
            return create_error_response("MissingParameter", "Missing required parameter: AllocationId")
        if not transfer_account_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransferAccountId")

        resource = self.resources.get(allocation_id)
        if not resource:
            return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")

        resource.address_transfer_status = "enabled"
        resource.transfer_account_id = transfer_account_id
        resource.transfer_offer_accepted_timestamp = None
        resource.transfer_offer_expiration_timestamp = self._utc_now_iso()

        return {
            'addressTransfer': self._build_address_transfer_dict(resource),
            }

    def ModifyAddressAttribute(self, params: Dict[str, Any]):
        """Modifies an attribute of the specified Elastic IP address. For requirements, seeUsing reverse DNS for email applications."""

        allocation_id = params.get("AllocationId")
        if not allocation_id:
            return create_error_response("MissingParameter", "Missing required parameter: AllocationId")

        resource = self.resources.get(allocation_id)
        if not resource:
            return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")

        domain_name = params.get("DomainName") or ""
        resource.ptr_record = domain_name
        resource.ptr_record_update = {
            "reason": "",
            "status": "succeeded",
            "value": domain_name,
        }

        return {
            'address': {
                'allocationId': resource.allocation_id,
                'ptrRecord': resource.ptr_record,
                'ptrRecordUpdate': resource.ptr_record_update,
                'publicIp': resource.public_ip,
                },
            }

    def ReleaseAddress(self, params: Dict[str, Any]):
        """Releases the specified Elastic IP address. [Default VPC] Releasing an Elastic IP address automatically disassociates it
				from any instance that it's associated with. Alternatively, you can disassociate an Elastic IP address without
				releasing it. [Nondefault VPC] You must disassociate the Elas"""

        allocation_id = params.get("AllocationId")
        public_ip = params.get("PublicIp")
        if not allocation_id and not public_ip:
            return create_error_response("MissingParameter", "Missing required parameter: AllocationId or PublicIp")

        if allocation_id:
            resource = self.resources.get(allocation_id)
            if not resource:
                return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")
        else:
            resource = self._find_by_public_ip(public_ip)
            if not resource:
                return create_error_response("InvalidAddress.NotFound", f"The ID '{public_ip}' does not exist")

        if resource.association_id:
            self._deregister_parent_links(resource.allocation_id, resource)

        if resource.allocation_id in self.resources:
            del self.resources[resource.allocation_id]

        return {
            'return': True,
            }

    def ResetAddressAttribute(self, params: Dict[str, Any]):
        """Resets the attribute of the specified IP address. For requirements, seeUsing reverse DNS for email applications."""

        allocation_id = params.get("AllocationId")
        attribute = params.get("Attribute")
        if not allocation_id:
            return create_error_response("MissingParameter", "Missing required parameter: AllocationId")
        if not attribute:
            return create_error_response("MissingParameter", "Missing required parameter: Attribute")

        resource = self.resources.get(allocation_id)
        if not resource:
            return create_error_response("InvalidAllocationID.NotFound", f"The ID '{allocation_id}' does not exist")

        resource.ptr_record = ""
        resource.ptr_record_update = {
            "reason": "",
            "status": "succeeded",
            "value": "",
        }

        return {
            'address': {
                'allocationId': resource.allocation_id,
                'ptrRecord': resource.ptr_record,
                'ptrRecordUpdate': resource.ptr_record_update,
                'publicIp': resource.public_ip,
                },
            }

    def _generate_id(self, prefix: str = 'allocation') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class elasticipaddresse_RequestParser:
    @staticmethod
    def parse_accept_address_transfer_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Address": get_scalar(md, "Address"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_allocate_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Address": get_scalar(md, "Address"),
            "CustomerOwnedIpv4Pool": get_scalar(md, "CustomerOwnedIpv4Pool"),
            "Domain": get_scalar(md, "Domain"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "IpamPoolId": get_scalar(md, "IpamPoolId"),
            "NetworkBorderGroup": get_scalar(md, "NetworkBorderGroup"),
            "PublicIpv4Pool": get_scalar(md, "PublicIpv4Pool"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_associate_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId": get_scalar(md, "AllocationId"),
            "AllowReassociation": get_scalar(md, "AllowReassociation"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceId": get_scalar(md, "InstanceId"),
            "NetworkInterfaceId": get_scalar(md, "NetworkInterfaceId"),
            "PrivateIpAddress": get_scalar(md, "PrivateIpAddress"),
            "PublicIp": get_scalar(md, "PublicIp"),
        }

    @staticmethod
    def parse_describe_addresses_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId.N": get_indexed_list(md, "AllocationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "PublicIp.N": get_indexed_list(md, "PublicIp"),
        }

    @staticmethod
    def parse_describe_addresses_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId.N": get_indexed_list(md, "AllocationId"),
            "Attribute": get_scalar(md, "Attribute"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_address_transfers_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId.N": get_indexed_list(md, "AllocationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disable_address_transfer_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId": get_scalar(md, "AllocationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_disassociate_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AssociationId": get_scalar(md, "AssociationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PublicIp": get_scalar(md, "PublicIp"),
        }

    @staticmethod
    def parse_enable_address_transfer_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId": get_scalar(md, "AllocationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransferAccountId": get_scalar(md, "TransferAccountId"),
        }

    @staticmethod
    def parse_modify_address_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId": get_scalar(md, "AllocationId"),
            "DomainName": get_scalar(md, "DomainName"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_release_address_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId": get_scalar(md, "AllocationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkBorderGroup": get_scalar(md, "NetworkBorderGroup"),
            "PublicIp": get_scalar(md, "PublicIp"),
        }

    @staticmethod
    def parse_reset_address_attribute_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AllocationId": get_scalar(md, "AllocationId"),
            "Attribute": get_scalar(md, "Attribute"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AcceptAddressTransfer": elasticipaddresse_RequestParser.parse_accept_address_transfer_request,
            "AllocateAddress": elasticipaddresse_RequestParser.parse_allocate_address_request,
            "AssociateAddress": elasticipaddresse_RequestParser.parse_associate_address_request,
            "DescribeAddresses": elasticipaddresse_RequestParser.parse_describe_addresses_request,
            "DescribeAddressesAttribute": elasticipaddresse_RequestParser.parse_describe_addresses_attribute_request,
            "DescribeAddressTransfers": elasticipaddresse_RequestParser.parse_describe_address_transfers_request,
            "DisableAddressTransfer": elasticipaddresse_RequestParser.parse_disable_address_transfer_request,
            "DisassociateAddress": elasticipaddresse_RequestParser.parse_disassociate_address_request,
            "EnableAddressTransfer": elasticipaddresse_RequestParser.parse_enable_address_transfer_request,
            "ModifyAddressAttribute": elasticipaddresse_RequestParser.parse_modify_address_attribute_request,
            "ReleaseAddress": elasticipaddresse_RequestParser.parse_release_address_request,
            "ResetAddressAttribute": elasticipaddresse_RequestParser.parse_reset_address_attribute_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class elasticipaddresse_ResponseSerializer:
    @staticmethod
    def _serialize_dict_to_xml(d: Dict[str, Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a dictionary to XML elements."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def _serialize_list_to_xml(lst: List[Any], tag_name: str, indent_level: int) -> List[str]:
        """Serialize a list to XML elements with <tagName> wrapper and <item> children."""
        xml_parts = []
        indent = '    ' * indent_level
        xml_parts.append(f'{indent}<{tag_name}>')
        for item in lst:
            if isinstance(item, dict):
                xml_parts.append(f'{indent}    <item>')
                xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
            else:
                xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
        xml_parts.append(f'{indent}</{tag_name}>')
        return xml_parts

    @staticmethod
    def _serialize_nested_fields(d: Dict[str, Any], indent_level: int) -> List[str]:
        """Serialize nested fields from a dictionary."""
        xml_parts = []
        indent = '    ' * indent_level
        for key, value in d.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                xml_parts.append(f'{indent}<{key}>')
                xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
                        xml_parts.append(f'{indent}    </item>')
                    else:
                        xml_parts.append(f'{indent}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, bool):
                xml_parts.append(f'{indent}<{key}>{str(value).lower()}</{key}>')
            else:
                xml_parts.append(f'{indent}<{key}>{esc(str(value))}</{key}>')
        return xml_parts

    @staticmethod
    def serialize_accept_address_transfer_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AcceptAddressTransferResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize addressTransfer
        _addressTransfer_key = None
        if "addressTransfer" in data:
            _addressTransfer_key = "addressTransfer"
        elif "AddressTransfer" in data:
            _addressTransfer_key = "AddressTransfer"
        if _addressTransfer_key:
            param_data = data[_addressTransfer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<addressTransfer>')
            xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</addressTransfer>')
        xml_parts.append(f'</AcceptAddressTransferResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_allocate_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AllocateAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize allocationId
        _allocationId_key = None
        if "allocationId" in data:
            _allocationId_key = "allocationId"
        elif "AllocationId" in data:
            _allocationId_key = "AllocationId"
        if _allocationId_key:
            param_data = data[_allocationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<allocationId>{esc(str(param_data))}</allocationId>')
        # Serialize carrierIp
        _carrierIp_key = None
        if "carrierIp" in data:
            _carrierIp_key = "carrierIp"
        elif "CarrierIp" in data:
            _carrierIp_key = "CarrierIp"
        if _carrierIp_key:
            param_data = data[_carrierIp_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<carrierIp>{esc(str(param_data))}</carrierIp>')
        # Serialize customerOwnedIp
        _customerOwnedIp_key = None
        if "customerOwnedIp" in data:
            _customerOwnedIp_key = "customerOwnedIp"
        elif "CustomerOwnedIp" in data:
            _customerOwnedIp_key = "CustomerOwnedIp"
        if _customerOwnedIp_key:
            param_data = data[_customerOwnedIp_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<customerOwnedIp>{esc(str(param_data))}</customerOwnedIp>')
        # Serialize customerOwnedIpv4Pool
        _customerOwnedIpv4Pool_key = None
        if "customerOwnedIpv4Pool" in data:
            _customerOwnedIpv4Pool_key = "customerOwnedIpv4Pool"
        elif "CustomerOwnedIpv4Pool" in data:
            _customerOwnedIpv4Pool_key = "CustomerOwnedIpv4Pool"
        if _customerOwnedIpv4Pool_key:
            param_data = data[_customerOwnedIpv4Pool_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<customerOwnedIpv4Pool>{esc(str(param_data))}</customerOwnedIpv4Pool>')
        # Serialize domain
        _domain_key = None
        if "domain" in data:
            _domain_key = "domain"
        elif "Domain" in data:
            _domain_key = "Domain"
        if _domain_key:
            param_data = data[_domain_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<domain>{esc(str(param_data))}</domain>')
        # Serialize networkBorderGroup
        _networkBorderGroup_key = None
        if "networkBorderGroup" in data:
            _networkBorderGroup_key = "networkBorderGroup"
        elif "NetworkBorderGroup" in data:
            _networkBorderGroup_key = "NetworkBorderGroup"
        if _networkBorderGroup_key:
            param_data = data[_networkBorderGroup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkBorderGroup>{esc(str(param_data))}</networkBorderGroup>')
        # Serialize publicIp
        _publicIp_key = None
        if "publicIp" in data:
            _publicIp_key = "publicIp"
        elif "PublicIp" in data:
            _publicIp_key = "PublicIp"
        if _publicIp_key:
            param_data = data[_publicIp_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<publicIp>{esc(str(param_data))}</publicIp>')
        # Serialize publicIpv4Pool
        _publicIpv4Pool_key = None
        if "publicIpv4Pool" in data:
            _publicIpv4Pool_key = "publicIpv4Pool"
        elif "PublicIpv4Pool" in data:
            _publicIpv4Pool_key = "PublicIpv4Pool"
        if _publicIpv4Pool_key:
            param_data = data[_publicIpv4Pool_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<publicIpv4Pool>{esc(str(param_data))}</publicIpv4Pool>')
        xml_parts.append(f'</AllocateAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_associate_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associationId
        _associationId_key = None
        if "associationId" in data:
            _associationId_key = "associationId"
        elif "AssociationId" in data:
            _associationId_key = "AssociationId"
        if _associationId_key:
            param_data = data[_associationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<associationId>{esc(str(param_data))}</associationId>')
        xml_parts.append(f'</AssociateAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_addresses_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeAddressesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize addressesSet
        _addressesSet_key = None
        if "addressesSet" in data:
            _addressesSet_key = "addressesSet"
        elif "AddressesSet" in data:
            _addressesSet_key = "AddressesSet"
        elif "Addressess" in data:
            _addressesSet_key = "Addressess"
        if _addressesSet_key:
            param_data = data[_addressesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<addressesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</addressesSet>')
            else:
                xml_parts.append(f'{indent_str}<addressesSet/>')
        xml_parts.append(f'</DescribeAddressesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_addresses_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeAddressesAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize addressSet
        _addressSet_key = None
        if "addressSet" in data:
            _addressSet_key = "addressSet"
        elif "AddressSet" in data:
            _addressSet_key = "AddressSet"
        elif "Addresss" in data:
            _addressSet_key = "Addresss"
        if _addressSet_key:
            param_data = data[_addressSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<addressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</addressSet>')
            else:
                xml_parts.append(f'{indent_str}<addressSet/>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        xml_parts.append(f'</DescribeAddressesAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_address_transfers_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeAddressTransfersResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize addressTransferSet
        _addressTransferSet_key = None
        if "addressTransferSet" in data:
            _addressTransferSet_key = "addressTransferSet"
        elif "AddressTransferSet" in data:
            _addressTransferSet_key = "AddressTransferSet"
        elif "AddressTransfers" in data:
            _addressTransferSet_key = "AddressTransfers"
        if _addressTransferSet_key:
            param_data = data[_addressTransferSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<addressTransferSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</addressTransferSet>')
            else:
                xml_parts.append(f'{indent_str}<addressTransferSet/>')
        # Serialize nextToken
        _nextToken_key = None
        if "nextToken" in data:
            _nextToken_key = "nextToken"
        elif "NextToken" in data:
            _nextToken_key = "NextToken"
        if _nextToken_key:
            param_data = data[_nextToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<nextToken>{esc(str(param_data))}</nextToken>')
        xml_parts.append(f'</DescribeAddressTransfersResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disable_address_transfer_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableAddressTransferResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize addressTransfer
        _addressTransfer_key = None
        if "addressTransfer" in data:
            _addressTransfer_key = "addressTransfer"
        elif "AddressTransfer" in data:
            _addressTransfer_key = "AddressTransfer"
        if _addressTransfer_key:
            param_data = data[_addressTransfer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<addressTransfer>')
            xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</addressTransfer>')
        xml_parts.append(f'</DisableAddressTransferResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</DisassociateAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_address_transfer_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableAddressTransferResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize addressTransfer
        _addressTransfer_key = None
        if "addressTransfer" in data:
            _addressTransfer_key = "addressTransfer"
        elif "AddressTransfer" in data:
            _addressTransfer_key = "AddressTransfer"
        if _addressTransfer_key:
            param_data = data[_addressTransfer_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<addressTransfer>')
            xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</addressTransfer>')
        xml_parts.append(f'</EnableAddressTransferResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_address_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyAddressAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize address
        _address_key = None
        if "address" in data:
            _address_key = "address"
        elif "Address" in data:
            _address_key = "Address"
        if _address_key:
            param_data = data[_address_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<addressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</addressSet>')
            else:
                xml_parts.append(f'{indent_str}<addressSet/>')
        xml_parts.append(f'</ModifyAddressAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_release_address_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ReleaseAddressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize return
        _return_key = None
        if "return" in data:
            _return_key = "return"
        elif "Return" in data:
            _return_key = "Return"
        if _return_key:
            param_data = data[_return_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<return>{esc(str(param_data))}</return>')
        xml_parts.append(f'</ReleaseAddressResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_reset_address_attribute_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ResetAddressAttributeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize address
        _address_key = None
        if "address" in data:
            _address_key = "address"
        elif "Address" in data:
            _address_key = "Address"
        if _address_key:
            param_data = data[_address_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<addressSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(elasticipaddresse_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</addressSet>')
            else:
                xml_parts.append(f'{indent_str}<addressSet/>')
        xml_parts.append(f'</ResetAddressAttributeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AcceptAddressTransfer": elasticipaddresse_ResponseSerializer.serialize_accept_address_transfer_response,
            "AllocateAddress": elasticipaddresse_ResponseSerializer.serialize_allocate_address_response,
            "AssociateAddress": elasticipaddresse_ResponseSerializer.serialize_associate_address_response,
            "DescribeAddresses": elasticipaddresse_ResponseSerializer.serialize_describe_addresses_response,
            "DescribeAddressesAttribute": elasticipaddresse_ResponseSerializer.serialize_describe_addresses_attribute_response,
            "DescribeAddressTransfers": elasticipaddresse_ResponseSerializer.serialize_describe_address_transfers_response,
            "DisableAddressTransfer": elasticipaddresse_ResponseSerializer.serialize_disable_address_transfer_response,
            "DisassociateAddress": elasticipaddresse_ResponseSerializer.serialize_disassociate_address_response,
            "EnableAddressTransfer": elasticipaddresse_ResponseSerializer.serialize_enable_address_transfer_response,
            "ModifyAddressAttribute": elasticipaddresse_ResponseSerializer.serialize_modify_address_attribute_response,
            "ReleaseAddress": elasticipaddresse_ResponseSerializer.serialize_release_address_response,
            "ResetAddressAttribute": elasticipaddresse_ResponseSerializer.serialize_reset_address_attribute_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

