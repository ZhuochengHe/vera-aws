from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend


class TransitGatewayPolicyTableAssociationState(str, Enum):
    ASSOCIATING = "associating"
    ASSOCIATED = "associated"
    DISASSOCIATING = "disassociating"
    DISASSOCIATED = "disassociated"


class TransitGatewayPolicyTableAssociationResourceType(str, Enum):
    VPC = "vpc"
    VPN = "vpn"
    VPN_CONCENTRATOR = "vpn-concentrator"
    DIRECT_CONNECT_GATEWAY = "direct-connect-gateway"
    CONNECT = "connect"
    PEERING = "peering"
    TGW_PEERING = "tgw-peering"


class TransitGatewayPolicyTableState(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETING = "deleting"
    DELETED = "deleted"


@dataclass
class Tag:
    Key: str
    Value: str


@dataclass
class TagSpecification:
    ResourceType: str
    Tags: List[Tag] = field(default_factory=list)


@dataclass
class TransitGatewayPolicyTableAssociation:
    resourceId: Optional[str] = None
    resourceType: Optional[TransitGatewayPolicyTableAssociationResourceType] = None
    state: Optional[TransitGatewayPolicyTableAssociationState] = None
    transitGatewayAttachmentId: Optional[str] = None
    transitGatewayPolicyTableId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceId": self.resourceId,
            "ResourceType": self.resourceType.value if self.resourceType else None,
            "State": self.state.value if self.state else None,
            "TransitGatewayAttachmentId": self.transitGatewayAttachmentId,
            "TransitGatewayPolicyTableId": self.transitGatewayPolicyTableId,
        }


@dataclass
class TransitGatewayPolicyTable:
    creationTime: Optional[datetime] = None
    state: Optional[TransitGatewayPolicyTableState] = None
    tagSet: List[Tag] = field(default_factory=list)
    transitGatewayId: Optional[str] = None
    transitGatewayPolicyTableId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CreationTime": self.creationTime.isoformat() if self.creationTime else None,
            "State": self.state.value if self.state else None,
            "TagSet": [{"Key": tag.Key, "Value": tag.Value} for tag in self.tagSet],
            "TransitGatewayId": self.transitGatewayId,
            "TransitGatewayPolicyTableId": self.transitGatewayPolicyTableId,
        }


@dataclass
class TransitGatewayPolicyRuleMetaData:
    metaDataKey: Optional[str] = None
    metaDataValue: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "MetaDataKey": self.metaDataKey,
            "MetaDataValue": self.metaDataValue,
        }


@dataclass
class TransitGatewayPolicyRule:
    destinationCidrBlock: Optional[str] = None
    destinationPortRange: Optional[str] = None  # Currently always "*"
    metaData: Optional[TransitGatewayPolicyRuleMetaData] = None
    protocol: Optional[str] = None
    sourceCidrBlock: Optional[str] = None
    sourcePortRange: Optional[str] = None  # Currently always "*"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DestinationCidrBlock": self.destinationCidrBlock,
            "DestinationPortRange": self.destinationPortRange,
            "MetaData": self.metaData.to_dict() if self.metaData else None,
            "Protocol": self.protocol,
            "SourceCidrBlock": self.sourceCidrBlock,
            "SourcePortRange": self.sourcePortRange,
        }


@dataclass
class TransitGatewayPolicyTableEntry:
    policyRule: Optional[TransitGatewayPolicyRule] = None
    policyRuleNumber: Optional[str] = None
    targetRouteTableId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "PolicyRule": self.policyRule.to_dict() if self.policyRule else None,
            "PolicyRuleNumber": self.policyRuleNumber,
            "TargetRouteTableId": self.targetRouteTableId,
        }


class TransitgatewaypolicytablesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)

    def associate_transit_gateway_policy_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        transit_gateway_policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not transit_gateway_attachment_id:
            raise ValueError("TransitGatewayAttachmentId is required")
        if not transit_gateway_policy_table_id:
            raise ValueError("TransitGatewayPolicyTableId is required")

        # Check if the policy table exists
        policy_table = self.state.transit_gateway_policy_tables.get(transit_gateway_policy_table_id)
        if not policy_table:
            raise ValueError(f"TransitGatewayPolicyTableId {transit_gateway_policy_table_id} does not exist")

        # Check if the attachment exists in resources
        attachment = self.state.get_resource(transit_gateway_attachment_id)
        if not attachment:
            raise ValueError(f"TransitGatewayAttachmentId {transit_gateway_attachment_id} does not exist")

        # Determine resourceType from attachment resource type if possible
        # Valid Values: vpc | vpn | vpn-concentrator | direct-connect-gateway | connect | peering | tgw-peering
        # We try to infer resourceType from attachment resource type or default to None
        resource_type = None
        if hasattr(attachment, "resource_type"):
            resource_type = attachment.resource_type
        elif hasattr(attachment, "resourceType"):
            resource_type = attachment.resourceType

        # Create association object
        from enum import Enum

        # TransitGatewayPolicyTableAssociationState enum values: associating | associated | disassociating | disassociated
        # We set state to associated immediately for simplicity
        association_state = TransitGatewayPolicyTableAssociationState.associated

        association = TransitGatewayPolicyTableAssociation()
        association.resourceId = transit_gateway_attachment_id
        association.resourceType = resource_type
        association.state = association_state
        association.transitGatewayAttachmentId = transit_gateway_attachment_id
        association.transitGatewayPolicyTableId = transit_gateway_policy_table_id

        # Store association in state resources keyed by a unique id
        association_id = self.generate_unique_id()
        self.state.resources[association_id] = association

        # Return response
        return {
            "association": association.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def create_transit_gateway_policy_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_id = params.get("TransitGatewayId")
        if not transit_gateway_id:
            raise ValueError("TransitGatewayId is required")

        # Parse TagSpecifications if present
        tag_specifications = params.get("TagSpecifications.N", [])
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # tag_spec is expected to be a dict with keys ResourceType and Tags
            tag_list = tag_spec.get("Tags", [])
            for tag_dict in tag_list:
                key = tag_dict.get("Key")
                value = tag_dict.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(Key=key, Value=value))

        # Create new TransitGatewayPolicyTable object
        policy_table = TransitGatewayPolicyTable()
        policy_table.creationTime = datetime.utcnow()
        policy_table.state = TransitGatewayPolicyTableState.available
        policy_table.tagSet = tags
        policy_table.transitGatewayId = transit_gateway_id
        policy_table.transitGatewayPolicyTableId = self.generate_unique_id()

        # Store in state
        self.state.transit_gateway_policy_tables[policy_table.transitGatewayPolicyTableId] = policy_table
        self.state.resources[policy_table.transitGatewayPolicyTableId] = policy_table

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayPolicyTable": policy_table.to_dict(),
        }


    def delete_transit_gateway_policy_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not transit_gateway_policy_table_id:
            raise ValueError("TransitGatewayPolicyTableId is required")

        policy_table = self.state.transit_gateway_policy_tables.get(transit_gateway_policy_table_id)
        if not policy_table:
            raise ValueError(f"TransitGatewayPolicyTableId {transit_gateway_policy_table_id} does not exist")

        # Mark state as deleting then deleted
        policy_table.state = TransitGatewayPolicyTableState.deleting
        # For simplicity, immediately mark as deleted
        policy_table.state = TransitGatewayPolicyTableState.deleted

        # Remove from state dicts
        self.state.transit_gateway_policy_tables.pop(transit_gateway_policy_table_id, None)
        self.state.resources.pop(transit_gateway_policy_table_id, None)

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayPolicyTable": policy_table.to_dict(),
        }


    def describe_transit_gateway_policy_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Optional filters and IDs
        filter_list = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        policy_table_ids = params.get("TransitGatewayPolicyTableIds.N", [])

        # Collect all policy tables
        all_policy_tables = list(self.state.transit_gateway_policy_tables.values())

        # Filter by IDs if provided
        if policy_table_ids:
            all_policy_tables = [pt for pt in all_policy_tables if pt.transitGatewayPolicyTableId in policy_table_ids]

        # Apply filters if provided
        # Filters are dicts with keys Name and Values (list)
        for filter_obj in filter_list:
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                continue
            filtered = []
            for pt in all_policy_tables:
                # Support filtering on common attributes: state, transitGatewayId, tag keys/values
                if name == "state" and pt.state and pt.state.value in values:
                    filtered.append(pt)
                elif name == "transit-gateway-id" and pt.transitGatewayId in values:
                    filtered.append(pt)
                elif name == "tag-key":
                    # Check if any tag key matches
                    if any(tag.Key in values for tag in pt.tagSet):
                        filtered.append(pt)
                elif name == "tag-value":
                    # Check if any tag value matches
                    if any(tag.Value in values for tag in pt.tagSet):
                        filtered.append(pt)
                elif name == "tag:" and name.startswith("tag:"):
                    # tag:<key> filter
                    tag_key = name[4:]
                    if any(tag.Key == tag_key and tag.Value in values for tag in pt.tagSet):
                        filtered.append(pt)
            all_policy_tables = filtered

        # Pagination logic
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
        paged_policy_tables = all_policy_tables[start_index:end_index]

        new_next_token = None
        if end_index < len(all_policy_tables):
            new_next_token = str(end_index)

        return {
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
            "transitGatewayPolicyTables": [pt.to_dict() for pt in paged_policy_tables],
        }


    def disassociate_transit_gateway_policy_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_attachment_id = params.get("TransitGatewayAttachmentId")
        transit_gateway_policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not transit_gateway_attachment_id:
            raise ValueError("TransitGatewayAttachmentId is required")
        if not transit_gateway_policy_table_id:
            raise ValueError("TransitGatewayPolicyTableId is required")

        # Find the association in resources
        association = None
        association_key = None
        for key, resource in self.state.resources.items():
            if (
                isinstance(resource, TransitGatewayPolicyTableAssociation)
                and resource.transitGatewayAttachmentId == transit_gateway_attachment_id
                and resource.transitGatewayPolicyTableId == transit_gateway_policy_table_id
            ):
                association = resource
                association_key = key
                break

        if not association:
            raise ValueError("Association not found for given TransitGatewayAttachmentId and TransitGatewayPolicyTableId")

        # Change state to disassociating then disassociated
        association.state = TransitGatewayPolicyTableAssociationState.disassociating
        association.state = TransitGatewayPolicyTableAssociationState.disassociated

        # Remove association from resources
        if association_key:
            self.state.resources.pop(association_key, None)

        return {
            "association": association.to_dict(),
            "requestId": self.generate_request_id(),
        }

    def get_transit_gateway_policy_table_associations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not transit_gateway_policy_table_id:
            raise ValueError("TransitGatewayPolicyTableId is required")

        # Validate that the transit gateway policy table exists
        tgw_policy_table = self.state.transit_gateway_policy_tables.get(transit_gateway_policy_table_id)
        if not tgw_policy_table:
            raise ValueError(f"TransitGatewayPolicyTableId {transit_gateway_policy_table_id} does not exist")

        # Filters processing
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                filter_index = key.split(".")[1]
                # Collect filter name and values
                filter_name = params.get(f"Filter.{filter_index}.Name")
                filter_values = params.get(f"Filter.{filter_index}.Values", [])
                if filter_name:
                    filters.append({"Name": filter_name, "Values": filter_values})

        # Pagination params
        max_results = params.get("MaxResults")
        if max_results is not None:
            max_results = int(max_results)
            if max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        # next_token is expected to be a string representing an integer index for pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ValueError("Invalid NextToken")

        # Collect all associations for this transit gateway policy table
        all_associations = []
        for assoc in self.state.resources.values():
            if isinstance(assoc, TransitGatewayPolicyTableAssociation):
                if assoc.transitGatewayPolicyTableId == transit_gateway_policy_table_id:
                    all_associations.append(assoc)

        # Apply filters
        def matches_filter(assoc: TransitGatewayPolicyTableAssociation, filters: list) -> bool:
            for f in filters:
                name = f["Name"]
                values = f["Values"]
                # Map filter names to association attributes
                attr_value = None
                if name == "resource-id":
                    attr_value = assoc.resourceId
                elif name == "resource-type":
                    attr_value = assoc.resourceType.name if assoc.resourceType else None
                elif name == "state":
                    attr_value = assoc.state.name if assoc.state else None
                elif name == "transit-gateway-attachment-id":
                    attr_value = assoc.transitGatewayAttachmentId
                elif name == "transit-gateway-policy-table-id":
                    attr_value = assoc.transitGatewayPolicyTableId
                else:
                    # Unknown filter name, skip filtering by it
                    continue
                if attr_value is None or attr_value not in values:
                    return False
            return True

        filtered_associations = [a for a in all_associations if matches_filter(a, filters)]

        # Pagination slice
        end_index = start_index + max_results if max_results else None
        paged_associations = filtered_associations[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index is not None and end_index < len(filtered_associations):
            new_next_token = str(end_index)

        # Build response
        response_associations = []
        for assoc in paged_associations:
            response_associations.append({
                "resourceId": assoc.resourceId,
                "resourceType": assoc.resourceType.name if assoc.resourceType else None,
                "state": assoc.state.name if assoc.state else None,
                "transitGatewayAttachmentId": assoc.transitGatewayAttachmentId,
                "transitGatewayPolicyTableId": assoc.transitGatewayPolicyTableId,
            })

        return {
            "associations": response_associations,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def get_transit_gateway_policy_table_entries(self, params: Dict[str, Any]) -> Dict[str, Any]:
        transit_gateway_policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not transit_gateway_policy_table_id:
            raise ValueError("TransitGatewayPolicyTableId is required")

        # Validate that the transit gateway policy table exists
        tgw_policy_table = self.state.transit_gateway_policy_tables.get(transit_gateway_policy_table_id)
        if not tgw_policy_table:
            raise ValueError(f"TransitGatewayPolicyTableId {transit_gateway_policy_table_id} does not exist")

        # Filters processing
        filters = []
        for key, value in params.items():
            if key.startswith("Filter."):
                filter_index = key.split(".")[1]
                filter_name = params.get(f"Filter.{filter_index}.Name")
                filter_values = params.get(f"Filter.{filter_index}.Values", [])
                if filter_name:
                    filters.append({"Name": filter_name, "Values": filter_values})

        # Pagination params
        max_results = params.get("MaxResults")
        if max_results is not None:
            max_results = int(max_results)
            if max_results < 5 or max_results > 1000:
                raise ValueError("MaxResults must be between 5 and 1000")

        next_token = params.get("NextToken")
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ValueError("Invalid NextToken")

        # Collect all entries for this transit gateway policy table
        all_entries = []
        for entry in self.state.resources.values():
            if isinstance(entry, TransitGatewayPolicyTableEntry):
                # We need to check if the entry belongs to the requested transit gateway policy table
                # The entry itself does not have a direct transitGatewayPolicyTableId attribute,
                # but the policyRule or targetRouteTableId might be linked indirectly.
                # Since no direct link is specified, we assume entries are stored with a reference transitGatewayPolicyTableId attribute
                # If not, we skip entries that do not belong to the requested table.
                # For safety, check if entry has attribute transitGatewayPolicyTableId and matches
                if hasattr(entry, "transitGatewayPolicyTableId") and entry.transitGatewayPolicyTableId == transit_gateway_policy_table_id:
                    all_entries.append(entry)

        # Apply filters
        def matches_filter(entry: TransitGatewayPolicyTableEntry, filters: list) -> bool:
            for f in filters:
                name = f["Name"]
                values = f["Values"]
                attr_value = None
                if name == "policy-rule-number":
                    attr_value = entry.policyRuleNumber
                elif name == "target-route-table-id":
                    attr_value = entry.targetRouteTableId
                elif name == "destination-cidr-block":
                    attr_value = entry.policyRule.destinationCidrBlock if entry.policyRule else None
                elif name == "source-cidr-block":
                    attr_value = entry.policyRule.sourceCidrBlock if entry.policyRule else None
                elif name == "protocol":
                    attr_value = entry.policyRule.protocol if entry.policyRule else None
                elif name == "destination-port-range":
                    attr_value = entry.policyRule.destinationPortRange if entry.policyRule else None
                elif name == "source-port-range":
                    attr_value = entry.policyRule.sourcePortRange if entry.policyRule else None
                elif name == "meta-data-key":
                    attr_value = entry.policyRule.metaData.metaDataKey if entry.policyRule and entry.policyRule.metaData else None
                elif name == "meta-data-value":
                    attr_value = entry.policyRule.metaData.metaDataValue if entry.policyRule and entry.policyRule.metaData else None
                else:
                    continue
                if attr_value is None or attr_value not in values:
                    return False
            return True

        filtered_entries = [e for e in all_entries if matches_filter(e, filters)]

        # Pagination slice
        end_index = start_index + max_results if max_results else None
        paged_entries = filtered_entries[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index is not None and end_index < len(filtered_entries):
            new_next_token = str(end_index)

        # Build response entries
        response_entries = []
        for entry in paged_entries:
            policy_rule = entry.policyRule
            meta_data = policy_rule.metaData if policy_rule else None
            response_entries.append({
                "policyRule": {
                    "destinationCidrBlock": policy_rule.destinationCidrBlock if policy_rule else None,
                    "destinationPortRange": policy_rule.destinationPortRange if policy_rule else None,
                    "metaData": {
                        "metaDataKey": meta_data.metaDataKey if meta_data else None,
                        "metaDataValue": meta_data.metaDataValue if meta_data else None,
                    } if meta_data else None,
                    "protocol": policy_rule.protocol if policy_rule else None,
                    "sourceCidrBlock": policy_rule.sourceCidrBlock if policy_rule else None,
                    "sourcePortRange": policy_rule.sourcePortRange if policy_rule else None,
                } if policy_rule else None,
                "policyRuleNumber": entry.policyRuleNumber,
                "targetRouteTableId": entry.targetRouteTableId,
            })

        return {
            "requestId": self.generate_request_id(),
            "transitGatewayPolicyTableEntries": response_entries,
            "nextToken": new_next_token,
        }

    

from emulator_core.gateway.base import BaseGateway

class TransitgatewaypolicytablesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("AssociateTransitGatewayPolicyTable", self.associate_transit_gateway_policy_table)
        self.register_action("CreateTransitGatewayPolicyTable", self.create_transit_gateway_policy_table)
        self.register_action("DeleteTransitGatewayPolicyTable", self.delete_transit_gateway_policy_table)
        self.register_action("DescribeTransitGatewayPolicyTables", self.describe_transit_gateway_policy_tables)
        self.register_action("DisassociateTransitGatewayPolicyTable", self.disassociate_transit_gateway_policy_table)
        self.register_action("GetTransitGatewayPolicyTableAssociations", self.get_transit_gateway_policy_table_associations)
        self.register_action("GetTransitGatewayPolicyTableEntries", self.get_transit_gateway_policy_table_entries)

    def associate_transit_gateway_policy_table(self, params):
        return self.backend.associate_transit_gateway_policy_table(params)

    def create_transit_gateway_policy_table(self, params):
        return self.backend.create_transit_gateway_policy_table(params)

    def delete_transit_gateway_policy_table(self, params):
        return self.backend.delete_transit_gateway_policy_table(params)

    def describe_transit_gateway_policy_tables(self, params):
        return self.backend.describe_transit_gateway_policy_tables(params)

    def disassociate_transit_gateway_policy_table(self, params):
        return self.backend.disassociate_transit_gateway_policy_table(params)

    def get_transit_gateway_policy_table_associations(self, params):
        return self.backend.get_transit_gateway_policy_table_associations(params)

    def get_transit_gateway_policy_table_entries(self, params):
        return self.backend.get_transit_gateway_policy_table_entries(params)
