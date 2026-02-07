from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class AddressTransferStatus(str, Enum):
    PENDING = "pending"
    DISABLED = "disabled"
    ACCEPTED = "accepted"


class DomainType(str, Enum):
    VPC = "vpc"
    STANDARD = "standard"


class ServiceManagedType(str, Enum):
    ALB = "alb"
    NLB = "nlb"
    RNAT = "rnat"
    RDS = "rds"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class TagSpecification:
    ResourceType: Optional[str] = None  # See valid values in resource JSON description
    Tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.ResourceType,
            "Tags": [tag.to_dict() for tag in self.Tags],
        }


@dataclass
class AddressTransfer:
    address_transfer_status: Optional[AddressTransferStatus] = None
    allocation_id: Optional[str] = None
    public_ip: Optional[str] = None
    transfer_account_id: Optional[str] = None
    transfer_offer_accepted_timestamp: Optional[datetime] = None
    transfer_offer_expiration_timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AddressTransferStatus": self.address_transfer_status.value if self.address_transfer_status else None,
            "AllocationId": self.allocation_id,
            "PublicIp": self.public_ip,
            "TransferAccountId": self.transfer_account_id,
            "TransferOfferAcceptedTimestamp": self.transfer_offer_accepted_timestamp.isoformat() if self.transfer_offer_accepted_timestamp else None,
            "TransferOfferExpirationTimestamp": self.transfer_offer_expiration_timestamp.isoformat() if self.transfer_offer_expiration_timestamp else None,
        }


@dataclass
class PtrUpdateStatus:
    reason: Optional[str] = None
    status: Optional[str] = None
    value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Reason": self.reason,
            "Status": self.status,
            "Value": self.value,
        }


@dataclass
class AddressAttribute:
    allocation_id: Optional[str] = None
    ptr_record: Optional[str] = None
    ptr_record_update: Optional[PtrUpdateStatus] = None
    public_ip: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationId": self.allocation_id,
            "PtrRecord": self.ptr_record,
            "PtrRecordUpdate": self.ptr_record_update.to_dict() if self.ptr_record_update else None,
            "PublicIp": self.public_ip,
        }


@dataclass
class Address:
    allocation_id: Optional[str] = None
    association_id: Optional[str] = None
    carrier_ip: Optional[str] = None
    customer_owned_ip: Optional[str] = None
    customer_owned_ipv4_pool: Optional[str] = None
    domain: Optional[DomainType] = None
    instance_id: Optional[str] = None
    network_border_group: Optional[str] = None
    network_interface_id: Optional[str] = None
    network_interface_owner_id: Optional[str] = None
    private_ip_address: Optional[str] = None
    public_ip: Optional[str] = None
    public_ipv4_pool: Optional[str] = None
    service_managed: Optional[ServiceManagedType] = None
    subnet_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AllocationId": self.allocation_id,
            "AssociationId": self.association_id,
            "CarrierIp": self.carrier_ip,
            "CustomerOwnedIp": self.customer_owned_ip,
            "CustomerOwnedIpv4Pool": self.customer_owned_ipv4_pool,
            "Domain": self.domain.value if self.domain else None,
            "InstanceId": self.instance_id,
            "NetworkBorderGroup": self.network_border_group,
            "NetworkInterfaceId": self.network_interface_id,
            "NetworkInterfaceOwnerId": self.network_interface_owner_id,
            "PrivateIpAddress": self.private_ip_address,
            "PublicIp": self.public_ip,
            "PublicIpv4Pool": self.public_ipv4_pool,
            "ServiceManaged": self.service_managed.value if self.service_managed else None,
            "SubnetId": self.subnet_id,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
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


class ElasticIPaddressesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # NO local storage. Use self.state.elastic_ip_addresses or similar

    def accept_address_transfer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        address = params.get("Address")
        dry_run = params.get("DryRun", False)
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            # For simplicity, assume permission granted
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not address:
            raise ValueError("Address parameter is required")

        # Find the address transfer by public IP
        transfer = None
        for transfer_obj in self.state.elastic_ip_addresses.values():
            if hasattr(transfer_obj, "address_transfer_status") and transfer_obj.public_ip == address:
                transfer = transfer_obj
                break

        if not transfer:
            # No transfer found for this address
            raise ValueError(f"No transfer found for address {address}")

        # Accept the transfer if it is pending
        if transfer.address_transfer_status is None or transfer.address_transfer_status.name != "pending":
            raise ValueError(f"Address transfer for {address} is not pending and cannot be accepted")

        # Update transfer status to accepted
        from datetime import datetime
        transfer.address_transfer_status = AddressTransferStatus.accepted
        transfer.transfer_offer_accepted_timestamp = datetime.utcnow()

        # Apply tags if provided
        if tag_specifications:
            for tag_spec in tag_specifications:
                resource_type = tag_spec.get("ResourceType")
                tags = tag_spec.get("Tags", [])
                if resource_type == "elastic-ip":
                    for tag_dict in tags:
                        key = tag_dict.get("Key")
                        value = tag_dict.get("Value")
                        if key and value:
                            transfer.tag_set.append(Tag(Key=key, Value=value))

        request_id = self.generate_request_id()
        return {
            "addressTransfer": transfer.to_dict(),
            "requestId": request_id,
        }


    def allocate_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        address = params.get("Address")
        customer_owned_ipv4_pool = params.get("CustomerOwnedIpv4Pool")
        domain = params.get("Domain")
        dry_run = params.get("DryRun", False)
        ipam_pool_id = params.get("IpamPoolId")
        network_border_group = params.get("NetworkBorderGroup")
        public_ipv4_pool = params.get("PublicIpv4Pool")
        tag_specifications = params.get("TagSpecification.N", [])

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Validate domain
        if domain and domain not in ("vpc", "standard"):
            raise ValueError("Domain must be 'vpc' or 'standard' if specified")

        # Generate allocation ID and public IP if not provided
        allocation_id = self.generate_unique_id(prefix="eipalloc-")
        public_ip = address
        if not public_ip:
            # Generate a dummy public IP for allocation
            # For simplicity, generate a fake IP in 198.51.100.x range
            used_ips = {addr.public_ip for addr in self.state.elastic_ip_addresses.values() if addr.public_ip}
            for i in range(1, 255):
                candidate_ip = f"198.51.100.{i}"
                if candidate_ip not in used_ips:
                    public_ip = candidate_ip
                    break
            if not public_ip:
                raise RuntimeError("No available IP addresses to allocate")

        # Create Address object
        new_address = Address(
            allocation_id=allocation_id,
            association_id=None,
            carrier_ip=None,
            customer_owned_ip=None,
            customer_owned_ipv4_pool=customer_owned_ipv4_pool,
            domain=DomainType(domain) if domain else None,
            instance_id=None,
            network_border_group=network_border_group,
            network_interface_id=None,
            network_interface_owner_id=None,
            private_ip_address=None,
            public_ip=public_ip,
            public_ipv4_pool=public_ipv4_pool,
            service_managed=None,
            subnet_id=None,
            tag_set=[],
        )

        # Apply tags if provided
        if tag_specifications:
            for tag_spec in tag_specifications:
                resource_type = tag_spec.get("ResourceType")
                tags = tag_spec.get("Tags", [])
                if resource_type == "elastic-ip":
                    for tag_dict in tags:
                        key = tag_dict.get("Key")
                        value = tag_dict.get("Value")
                        if key and value:
                            new_address.tag_set.append(Tag(Key=key, Value=value))

        # Store the new address in state
        self.state.elastic_ip_addresses[allocation_id] = new_address
        self.state.resources[allocation_id] = new_address

        request_id = self.generate_request_id()
        return {
            "allocationId": allocation_id,
            "carrierIp": None,
            "customerOwnedIp": None,
            "customerOwnedIpv4Pool": customer_owned_ipv4_pool,
            "domain": domain,
            "networkBorderGroup": network_border_group,
            "publicIp": public_ip,
            "publicIpv4Pool": public_ipv4_pool,
            "requestId": request_id,
        }


    def associate_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        allocation_id = params.get("AllocationId")
        allow_reassociation = params.get("AllowReassociation", False)
        dry_run = params.get("DryRun", False)
        instance_id = params.get("InstanceId")
        network_interface_id = params.get("NetworkInterfaceId")
        private_ip_address = params.get("PrivateIpAddress")
        public_ip = params.get("PublicIp")  # Deprecated

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        if not allocation_id:
            raise ValueError("AllocationId is required")

        if (instance_id and network_interface_id) or (not instance_id and not network_interface_id):
            raise ValueError("Specify either InstanceId or NetworkInterfaceId, but not both or neither")

        # Find the address by allocation_id
        address = self.state.elastic_ip_addresses.get(allocation_id)
        if not address:
            raise ValueError(f"AllocationId {allocation_id} not found")

        # Check if address is already associated
        if address.association_id:
            if not allow_reassociation:
                raise ValueError("Address is already associated and AllowReassociation is not set")

        # Generate association ID if not associated
        if not address.association_id:
            association_id = self.generate_unique_id(prefix="eipassoc-")
            address.association_id = association_id
        else:
            association_id = address.association_id

        # Associate with instance or network interface
        address.instance_id = instance_id
        address.network_interface_id = network_interface_id
        address.private_ip_address = private_ip_address

        # For network_interface_owner_id, we do not have info, so leave None

        request_id = self.generate_request_id()
        return {
            "associationId": association_id,
            "requestId": request_id,
        }


    def describe_addresses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        allocation_ids = params.get("AllocationId.N", [])
        filters = params.get("Filter.N", [])
        public_ips = params.get("PublicIp.N", [])
        dry_run = params.get("DryRun", False)

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Collect addresses to describe
        addresses = list(self.state.elastic_ip_addresses.values())

        # Filter by allocation_ids if provided
        if allocation_ids:
            addresses = [addr for addr in addresses if addr.allocation_id in allocation_ids]

        # Filter by public_ips if provided
        if public_ips:
            addresses = [addr for addr in addresses if addr.public_ip in public_ips]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not values:
                continue

            def match_filter(addr: Address) -> bool:
                # Handle tag:<key> filter
                if name.startswith("tag:"):
                    tag_key = name[4:]
                    for tag in addr.tag_set:
                        if tag.Key == tag_key and tag.Value in values:
                            return True
                    return False
                # Handle tag-key filter
                if name == "tag-key":
                    for tag in addr.tag_set:
                        if tag.Key in values:
                            return True
                    return False
                # Other filters by attribute names
                attr_map = {
                    "allocation-id": "allocation_id",
                    "association-id": "association_id",
                    "instance-id": "instance_id",
                    "network-border-group": "network_border_group",
                    "network-interface-id": "network_interface_id",
                    "network-interface-owner-id": "network_interface_owner_id",
                    "private-ip-address": "private_ip_address",
                    "public-ip": "public_ip",
                }
                attr = attr_map.get(name)
                if not attr:
                    return False
                val = getattr(addr, attr, None)
                if val is None:
                    return False
                return val in values

            addresses = [addr for addr in addresses if match_filter(addr)]

        request_id = self.generate_request_id()
        return {
            "addressesSet": [addr.to_dict() for addr in addresses],
            "requestId": request_id,
        }


    def describe_addresses_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        allocation_ids = params.get("AllocationId.N", [])
        attribute = params.get("Attribute")
        dry_run = params.get("DryRun", False)
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            return {"Error": {"Code": "DryRunOperation", "Message": "Request would have succeeded, but DryRun flag is set."}}

        # Filter addresses by allocation_ids if provided
        addresses = list(self.state.elastic_ip_addresses.values())
        if allocation_ids:
            addresses = [addr for addr in addresses if addr.allocation_id in allocation_ids]

        # Pagination support (simple)
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results is not None:
            try:
                max_results = int(max_results)
                if max_results < 1:
                    max_results = 1
                elif max_results > 1000:
                    max_results = 1000
            except Exception:
                max_results = None

        end_index = start_index + max_results if max_results else None
        paged_addresses = addresses[start_index:end_index]

        # Build addressSet with AddressAttribute objects
        address_set = []
        for addr in paged_addresses:
            ptr_record = None
            ptr_record_update = None
            # For now, no real PTR record management, so leave None
            address_attr = AddressAttribute(
                allocation_id=addr.allocation_id,
                ptr_record=ptr_record,
                ptr_record_update=ptr_record_update,
                public_ip=addr.public_ip,
            )
            address_set.append(address_attr.to_dict())

        # Determine next token
        new_next_token = None
        if end_index is not None and end_index < len(addresses):
            new_next_token = str(end_index)

        request_id = self.generate_request_id()
        return {
            "addressSet": address_set,
            "nextToken": new_next_token,
            "requestId": request_id,
        }

    from typing import Any, Dict, List, Optional
    from datetime import datetime, timedelta
    from enum import Enum

    class AddressTransferStatus(Enum):
        PENDING = "pending"
        DISABLED = "disabled"
        ACCEPTED = "accepted"

    class ElasticIPaddressesBackend:
        def __init__(self, state):
            self.state = state

        def describe_address_transfers(self, params: Dict[str, Any]) -> Dict[str, Any]:
            allocation_ids: Optional[List[str]] = params.get("AllocationId.N")
            dry_run: Optional[bool] = params.get("DryRun")
            max_results: Optional[int] = params.get("MaxResults")
            next_token: Optional[str] = params.get("NextToken")

            # DryRun check (not implemented here, assume always allowed)
            if dry_run:
                # In real implementation, check permissions and raise error if unauthorized
                return {"Error": "DryRunOperation"}

            # Validate max_results if provided
            if max_results is not None:
                if not (5 <= max_results <= 1000):
                    raise ValueError("MaxResults must be between 5 and 1000")

            # Collect all address transfers from state
            all_transfers: List[AddressTransfer] = []
            for transfer in self.state.elastic_ip_addresses.get("address_transfers", {}).values():
                all_transfers.append(transfer)

            # Filter by allocation_ids if provided
            if allocation_ids:
                filtered_transfers = [t for t in all_transfers if t.allocation_id in allocation_ids]
            else:
                filtered_transfers = all_transfers

            # Pagination logic
            start_index = 0
            if next_token:
                try:
                    start_index = int(next_token)
                except ValueError:
                    start_index = 0

            end_index = start_index + max_results if max_results else len(filtered_transfers)
            paged_transfers = filtered_transfers[start_index:end_index]

            # Prepare next token if more results exist
            new_next_token = str(end_index) if end_index < len(filtered_transfers) else None

            # Convert to dicts
            address_transfer_set = [t.to_dict() for t in paged_transfers]

            response = {
                "addressTransferSet": address_transfer_set,
                "nextToken": new_next_token,
                "requestId": self.generate_request_id(),
            }
            return response

        def disable_address_transfer(self, params: Dict[str, Any]) -> Dict[str, Any]:
            allocation_id: Optional[str] = params.get("AllocationId")
            dry_run: Optional[bool] = params.get("DryRun")

            if not allocation_id:
                raise ValueError("AllocationId is required")

            if dry_run:
                return {"Error": "DryRunOperation"}

            transfers = self.state.elastic_ip_addresses.get("address_transfers", {})
            transfer = transfers.get(allocation_id)
            if not transfer:
                # In real AWS, this would raise an error
                raise ValueError(f"Address transfer with AllocationId {allocation_id} not found")

            # Disable the transfer if it is pending
            if transfer.address_transfer_status == AddressTransferStatus.PENDING:
                transfer.address_transfer_status = AddressTransferStatus.DISABLED
                # Clear expiration and accepted timestamps
                transfer.transfer_offer_accepted_timestamp = None
                transfer.transfer_offer_expiration_timestamp = None

            response = {
                "addressTransfer": transfer.to_dict(),
                "requestId": self.generate_request_id(),
            }
            return response

        def disassociate_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
            association_id: Optional[str] = params.get("AssociationId")
            dry_run: Optional[bool] = params.get("DryRun")
            public_ip: Optional[str] = params.get("PublicIp")  # Deprecated

            if dry_run:
                return {"Error": "DryRunOperation"}

            if not association_id and not public_ip:
                raise ValueError("AssociationId or PublicIp is required")

            # Find the address by association_id or public_ip
            address = None
            for addr in self.state.elastic_ip_addresses.values():
                if association_id and addr.association_id == association_id:
                    address = addr
                    break
                if public_ip and addr.public_ip == public_ip:
                    address = addr
                    break

            if not address:
                # Idempotent: if not found, return success
                return {
                    "requestId": self.generate_request_id(),
                    "return": True,
                }

            # Disassociate the address
            address.association_id = None
            address.instance_id = None
            address.network_interface_id = None
            address.private_ip_address = None
            address.network_interface_owner_id = None

            return {
                "requestId": self.generate_request_id(),
                "return": True,
            }

        def enable_address_transfer(self, params: Dict[str, Any]) -> Dict[str, Any]:
            allocation_id: Optional[str] = params.get("AllocationId")
            dry_run: Optional[bool] = params.get("DryRun")
            transfer_account_id: Optional[str] = params.get("TransferAccountId")

            if not allocation_id:
                raise ValueError("AllocationId is required")
            if not transfer_account_id:
                raise ValueError("TransferAccountId is required")

            if dry_run:
                return {"Error": "DryRunOperation"}

            transfers = self.state.elastic_ip_addresses.get("address_transfers", {})
            transfer = transfers.get(allocation_id)
            if not transfer:
                # Create new transfer if not exists
                transfer = AddressTransfer()
                transfer.allocation_id = allocation_id
                # Find public IP from addresses
                address = self.state.elastic_ip_addresses.get(allocation_id)
                if address:
                    transfer.public_ip = address.public_ip
                transfers[allocation_id] = transfer
                self.state.elastic_ip_addresses["address_transfers"] = transfers

            # Enable transfer: set status to pending, set transfer account id, set expiration timestamp
            transfer.address_transfer_status = AddressTransferStatus.PENDING
            transfer.transfer_account_id = transfer_account_id
            transfer.transfer_offer_accepted_timestamp = None
            transfer.transfer_offer_expiration_timestamp = datetime.utcnow() + timedelta(days=7)

            response = {
                "addressTransfer": transfer.to_dict(),
                "requestId": self.generate_request_id(),
            }
            return response

        def modify_address_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
            allocation_id: Optional[str] = params.get("AllocationId")
            domain_name: Optional[str] = params.get("DomainName")
            dry_run: Optional[bool] = params.get("DryRun")

            if not allocation_id:
                raise ValueError("AllocationId is required")

            if dry_run:
                return {"Error": "DryRunOperation"}

            address = self.state.elastic_ip_addresses.get(allocation_id)
            if not address:
                raise ValueError(f"Address with AllocationId {allocation_id} not found")

            # Modify domain name attribute (PTR record)
            if domain_name is not None:
                # For simplicity, assume domain_name is the PTR record
                address.ptr_record = domain_name
                # Update ptr_record_update status
                ptr_update = PtrUpdateStatus()
                ptr_update.status = "successful"
                ptr_update.reason = None
                ptr_update.value = domain_name
                address.ptr_record_update = ptr_update

            response = {
                "address": AddressAttribute(
                    allocation_id=address.allocation_id,
                    ptr_record=address.ptr_record,
                    ptr_record_update=address.ptr_record_update,
                    public_ip=address.public_ip,
                ).to_dict(),
                "requestId": self.generate_request_id(),
            }
            return response

        # Helpers assumed to be available in the class:
        def generate_unique_id(self) -> str:
            # Placeholder for unique ID generation
            import uuid
            return str(uuid.uuid4())

        def generate_request_id(self) -> str:
            # Placeholder for request ID generation
            import uuid
            return str(uuid.uuid4())

        def get_owner_id(self) -> str:
            # Placeholder for owner ID retrieval
            return "123456789012"

    def release_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        allocation_id = params.get("AllocationId")
        public_ip = params.get("PublicIp")
        network_border_group = params.get("NetworkBorderGroup")
        dry_run = params.get("DryRun", False)

        # Validate input: Either AllocationId or PublicIp must be provided
        if not allocation_id and not public_ip:
            raise Exception("MissingParameter", "You must specify either AllocationId or PublicIp")

        # Find the address to release
        address = None
        if allocation_id:
            address = self.state.elastic_ip_addresses.get(allocation_id)
            if not address:
                raise Exception("InvalidAllocationID.NotFound", f"The allocation ID '{allocation_id}' does not exist")
            # If NetworkBorderGroup is provided, validate it matches
            if network_border_group and address.network_border_group != network_border_group:
                raise Exception("InvalidAddress.NotFound", "The specified network border group is incorrect")
        else:
            # Search by PublicIp
            for addr in self.state.elastic_ip_addresses.values():
                if addr.public_ip == public_ip:
                    address = addr
                    break
            if not address:
                raise Exception("InvalidAddress.NotFound", f"The public IP '{public_ip}' does not exist")
            # If NetworkBorderGroup is provided, validate it matches
            if network_border_group and address.network_border_group != network_border_group:
                raise Exception("InvalidAddress.NotFound", "The specified network border group is incorrect")
            allocation_id = address.allocation_id

        # DryRun check
        if dry_run:
            # Assume permission check passed for this emulator
            return {
                "requestId": self.generate_request_id(),
                "return": False,
                "__type": "DryRunOperation"
            }

        # Check if address is associated
        if address.association_id:
            # For default VPC, releasing automatically disassociates
            # For nondefault VPC, must disassociate first
            # We assume domain attribute indicates default or nondefault VPC
            # domain == 'vpc' means nondefault VPC
            if address.domain == "vpc":
                # Nondefault VPC: must disassociate first
                raise Exception("InvalidIPAddress.InUse", "You must disassociate the Elastic IP address before releasing it")
            else:
                # Default VPC: disassociate automatically
                # Remove association
                address.association_id = None
                address.instance_id = None
                address.network_interface_id = None
                address.private_ip_address = None

        # Remove the address from state
        del self.state.elastic_ip_addresses[allocation_id]
        if allocation_id in self.state.resources:
            del self.state.resources[allocation_id]

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }


    def reset_address_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        allocation_id = params.get("AllocationId")
        attribute = params.get("Attribute")
        dry_run = params.get("DryRun", False)

        if not allocation_id:
            raise Exception("MissingParameter", "AllocationId is required")
        if not attribute:
            raise Exception("MissingParameter", "Attribute is required")

        # Validate attribute value
        if attribute != "domain-name":
            raise Exception("InvalidParameterValue", f"Invalid attribute value '{attribute}'. Valid value is 'domain-name'")

        # DryRun check
        if dry_run:
            return {
                "requestId": self.generate_request_id(),
                "address": None,
                "__type": "DryRunOperation"
            }

        address = self.state.elastic_ip_addresses.get(allocation_id)
        if not address:
            raise Exception("InvalidAllocationID.NotFound", f"The allocation ID '{allocation_id}' does not exist")

        # Reset the attribute: domain-name attribute reset means clearing PTR record and update status
        address_attribute = AddressAttribute(
            allocation_id=allocation_id,
            ptr_record=None,
            ptr_record_update=PtrUpdateStatus(reason=None, status=None, value=None),
            public_ip=address.public_ip,
        )

        # Update the address in state to clear PTR record and update status
        # Assuming Address class has ptr_record and ptr_record_update attributes (not shown in original)
        # If not, we just return the reset attribute object
        # For safety, we do not modify the Address object itself here, just return the reset attribute

        return {
            "requestId": self.generate_request_id(),
            "address": address_attribute.to_dict(),
        }

    

from emulator_core.gateway.base import BaseGateway

class ElasticIPaddressesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AcceptAddressTransfer", self.accept_address_transfer)
        self.register_action("AllocateAddress", self.allocate_address)
        self.register_action("AssociateAddress", self.associate_address)
        self.register_action("DescribeAddresses", self.describe_addresses)
        self.register_action("DescribeAddressesAttribute", self.describe_addresses_attribute)
        self.register_action("DescribeAddressTransfers", self.describe_address_transfers)
        self.register_action("DisableAddressTransfer", self.disable_address_transfer)
        self.register_action("DisassociateAddress", self.disassociate_address)
        self.register_action("EnableAddressTransfer", self.enable_address_transfer)
        self.register_action("ModifyAddressAttribute", self.modify_address_attribute)
        self.register_action("ReleaseAddress", self.release_address)
        self.register_action("ResetAddressAttribute", self.reset_address_attribute)

    def accept_address_transfer(self, params):
        return self.backend.accept_address_transfer(params)

    def allocate_address(self, params):
        return self.backend.allocate_address(params)

    def associate_address(self, params):
        return self.backend.associate_address(params)

    def describe_addresses(self, params):
        return self.backend.describe_addresses(params)

    def describe_addresses_attribute(self, params):
        return self.backend.describe_addresses_attribute(params)

    def describe_address_transfers(self, params):
        return self.backend.describe_address_transfers(params)

    def disable_address_transfer(self, params):
        return self.backend.disable_address_transfer(params)

    def disassociate_address(self, params):
        return self.backend.disassociate_address(params)

    def enable_address_transfer(self, params):
        return self.backend.enable_address_transfer(params)

    def modify_address_attribute(self, params):
        return self.backend.modify_address_attribute(params)

    def release_address(self, params):
        return self.backend.release_address(params)

    def reset_address_attribute(self, params):
        return self.backend.reset_address_attribute(params)
