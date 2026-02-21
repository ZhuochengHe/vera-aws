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
class TransitGatewayPolicyTable:
    creation_time: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    transit_gateway_id: str = ""
    transit_gateway_policy_table_id: str = ""

    associations: List[Dict[str, Any]] = field(default_factory=list)
    entries: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTime": self.creation_time,
            "state": self.state,
            "tagSet": self.tag_set,
            "transitGatewayId": self.transit_gateway_id,
            "transitGatewayPolicyTableId": self.transit_gateway_policy_table_id,
        }

class TransitGatewayPolicyTable_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.transit_gateway_policy_tables  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.transit_gateways.get(params['transit_gateway_id']).transit_gateway_policy_table_ids.append(new_id)
    #   Delete: self.state.transit_gateways.get(resource.transit_gateway_id).transit_gateway_policy_table_ids.remove(resource_id)

    def _get_policy_table_or_error(self, policy_table_id: str):
        resource = self.resources.get(policy_table_id)
        if not resource:
            return None, create_error_response(
                "InvalidTransitGatewayPolicyTableID.NotFound",
                f"The ID '{policy_table_id}' does not exist",
            )
        return resource, None

    def _find_association(self, policy_table: TransitGatewayPolicyTable, attachment_id: str) -> Optional[Dict[str, Any]]:
        for association in policy_table.associations:
            if association.get("transitGatewayAttachmentId") == attachment_id:
                return association
        return None

    def AssociateTransitGatewayPolicyTable(self, params: Dict[str, Any]):
        """Associates the specified transit gateway attachment with a transit gateway policy table."""

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not policy_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayPolicyTableId")

        policy_table, error = self._get_policy_table_or_error(policy_table_id)
        if error:
            return error

        attachment = self.state.transit_gateway_connect.get(attachment_id)
        if not attachment:
            attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if not attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )

        association = self._find_association(policy_table, attachment_id)
        if not association:
            association = {
                "resourceId": attachment_id,
                "resourceType": "transit-gateway-attachment",
                "state": "associated",
                "transitGatewayAttachmentId": attachment_id,
                "transitGatewayPolicyTableId": policy_table_id,
            }
            policy_table.associations.append(association)
        else:
            association.update({
                "resourceId": association.get("resourceId") or attachment_id,
                "resourceType": association.get("resourceType") or "transit-gateway-attachment",
                "state": "associated",
                "transitGatewayAttachmentId": attachment_id,
                "transitGatewayPolicyTableId": policy_table_id,
            })

        return {
            'association': association,
            }

    def CreateTransitGatewayPolicyTable(self, params: Dict[str, Any]):
        """Creates a transit gateway policy table."""

        transit_gateway_id = params.get("TransitGatewayId")
        if not transit_gateway_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayId")

        parent = self.state.transit_gateways.get(transit_gateway_id)
        if not parent:
            return create_error_response("InvalidTransitGatewayID.NotFound", f"The ID '{transit_gateway_id}' does not exist")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "transit-gateway-policy-table":
                continue
            for tag in spec.get("Tags") or spec.get("Tag") or []:
                if tag:
                    tag_set.append(tag)

        policy_table_id = self._generate_id("tgw-ptb")
        now = datetime.now(timezone.utc).isoformat()
        resource = TransitGatewayPolicyTable(
            creation_time=now,
            state=ResourceState.AVAILABLE.value,
            tag_set=tag_set,
            transit_gateway_id=transit_gateway_id,
            transit_gateway_policy_table_id=policy_table_id,
        )
        self.resources[policy_table_id] = resource

        if hasattr(parent, "transit_gateway_policy_table_ids"):
            parent.transit_gateway_policy_table_ids.append(policy_table_id)

        return {
            'transitGatewayPolicyTable': resource.to_dict(),
            }

    def DeleteTransitGatewayPolicyTable(self, params: Dict[str, Any]):
        """Deletes the specified transit gateway policy table."""

        policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not policy_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayPolicyTableId")

        resource, error = self._get_policy_table_or_error(policy_table_id)
        if error:
            return error

        if resource.associations:
            return create_error_response(
                "DependencyViolation",
                "Transit gateway policy table has existing associations",
            )

        parent = self.state.transit_gateways.get(resource.transit_gateway_id)
        if parent and hasattr(parent, "transit_gateway_policy_table_ids"):
            if policy_table_id in parent.transit_gateway_policy_table_ids:
                parent.transit_gateway_policy_table_ids.remove(policy_table_id)

        self.resources.pop(policy_table_id, None)

        return {
            'transitGatewayPolicyTable': resource.to_dict(),
            }

    def DescribeTransitGatewayPolicyTables(self, params: Dict[str, Any]):
        """Describes one or more transit gateway route policy tables."""

        policy_table_ids = params.get("TransitGatewayPolicyTableIds.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if policy_table_ids:
            resources: List[TransitGatewayPolicyTable] = []
            for policy_table_id in policy_table_ids:
                resource, error = self._get_policy_table_or_error(policy_table_id)
                if error:
                    return error
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        policy_tables = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'nextToken': None,
            'transitGatewayPolicyTables': policy_tables,
            }

    def DisassociateTransitGatewayPolicyTable(self, params: Dict[str, Any]):
        """Removes the association between an an attachment and a policy table."""

        attachment_id = params.get("TransitGatewayAttachmentId")
        if not attachment_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayAttachmentId")

        policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not policy_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayPolicyTableId")

        policy_table, error = self._get_policy_table_or_error(policy_table_id)
        if error:
            return error

        attachment = self.state.transit_gateway_connect.get(attachment_id)
        if not attachment:
            attachment = self.state.transit_gateway_peering_attachments.get(attachment_id)
        if not attachment:
            return create_error_response(
                "InvalidTransitGatewayAttachmentID.NotFound",
                f"The ID '{attachment_id}' does not exist",
            )

        association = self._find_association(policy_table, attachment_id)
        if not association:
            return create_error_response(
                "InvalidAssociationID.NotFound",
                f"The association for '{attachment_id}' does not exist",
            )

        response_association = dict(association)
        response_association["state"] = "disassociated"

        if association in policy_table.associations:
            policy_table.associations.remove(association)

        return {
            'association': response_association,
            }

    def GetTransitGatewayPolicyTableAssociations(self, params: Dict[str, Any]):
        """Gets a list of the transit gateway policy table associations."""

        policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not policy_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayPolicyTableId")

        policy_table, error = self._get_policy_table_or_error(policy_table_id)
        if error:
            return error

        max_results = int(params.get("MaxResults") or 100)
        associations = list(policy_table.associations or [])
        associations = apply_filters(associations, params.get("Filter.N", []))
        associations = associations[:max_results]

        return {
            'associations': associations,
            'nextToken': None,
            }

    def GetTransitGatewayPolicyTableEntries(self, params: Dict[str, Any]):
        """Returns a list of transit gateway policy table entries."""

        policy_table_id = params.get("TransitGatewayPolicyTableId")
        if not policy_table_id:
            return create_error_response("MissingParameter", "Missing required parameter: TransitGatewayPolicyTableId")

        policy_table, error = self._get_policy_table_or_error(policy_table_id)
        if error:
            return error

        max_results = int(params.get("MaxResults") or 100)
        entries = list(policy_table.entries or [])
        entries = apply_filters(entries, params.get("Filter.N", []))
        entries = entries[:max_results]

        return {
            'transitGatewayPolicyTableEntries': entries,
            }

    def _generate_id(self, prefix: str = 'tgw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class transitgatewaypolicytable_RequestParser:
    @staticmethod
    def parse_associate_transit_gateway_policy_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayPolicyTableId": get_scalar(md, "TransitGatewayPolicyTableId"),
        }

    @staticmethod
    def parse_create_transit_gateway_policy_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecifications.N": parse_tags(md, "TagSpecifications"),
            "TransitGatewayId": get_scalar(md, "TransitGatewayId"),
        }

    @staticmethod
    def parse_delete_transit_gateway_policy_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayPolicyTableId": get_scalar(md, "TransitGatewayPolicyTableId"),
        }

    @staticmethod
    def parse_describe_transit_gateway_policy_tables_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayPolicyTableIds.N": get_indexed_list(md, "TransitGatewayPolicyTableIds"),
        }

    @staticmethod
    def parse_disassociate_transit_gateway_policy_table_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TransitGatewayAttachmentId": get_scalar(md, "TransitGatewayAttachmentId"),
            "TransitGatewayPolicyTableId": get_scalar(md, "TransitGatewayPolicyTableId"),
        }

    @staticmethod
    def parse_get_transit_gateway_policy_table_associations_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayPolicyTableId": get_scalar(md, "TransitGatewayPolicyTableId"),
        }

    @staticmethod
    def parse_get_transit_gateway_policy_table_entries_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "TransitGatewayPolicyTableId": get_scalar(md, "TransitGatewayPolicyTableId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AssociateTransitGatewayPolicyTable": transitgatewaypolicytable_RequestParser.parse_associate_transit_gateway_policy_table_request,
            "CreateTransitGatewayPolicyTable": transitgatewaypolicytable_RequestParser.parse_create_transit_gateway_policy_table_request,
            "DeleteTransitGatewayPolicyTable": transitgatewaypolicytable_RequestParser.parse_delete_transit_gateway_policy_table_request,
            "DescribeTransitGatewayPolicyTables": transitgatewaypolicytable_RequestParser.parse_describe_transit_gateway_policy_tables_request,
            "DisassociateTransitGatewayPolicyTable": transitgatewaypolicytable_RequestParser.parse_disassociate_transit_gateway_policy_table_request,
            "GetTransitGatewayPolicyTableAssociations": transitgatewaypolicytable_RequestParser.parse_get_transit_gateway_policy_table_associations_request,
            "GetTransitGatewayPolicyTableEntries": transitgatewaypolicytable_RequestParser.parse_get_transit_gateway_policy_table_entries_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class transitgatewaypolicytable_ResponseSerializer:
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
                xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_associate_transit_gateway_policy_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AssociateTransitGatewayPolicyTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize association
        _association_key = None
        if "association" in data:
            _association_key = "association"
        elif "Association" in data:
            _association_key = "Association"
        if _association_key:
            param_data = data[_association_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<association>')
            xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</association>')
        xml_parts.append(f'</AssociateTransitGatewayPolicyTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_transit_gateway_policy_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateTransitGatewayPolicyTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPolicyTable
        _transitGatewayPolicyTable_key = None
        if "transitGatewayPolicyTable" in data:
            _transitGatewayPolicyTable_key = "transitGatewayPolicyTable"
        elif "TransitGatewayPolicyTable" in data:
            _transitGatewayPolicyTable_key = "TransitGatewayPolicyTable"
        if _transitGatewayPolicyTable_key:
            param_data = data[_transitGatewayPolicyTable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPolicyTable>')
            xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPolicyTable>')
        xml_parts.append(f'</CreateTransitGatewayPolicyTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_transit_gateway_policy_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteTransitGatewayPolicyTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPolicyTable
        _transitGatewayPolicyTable_key = None
        if "transitGatewayPolicyTable" in data:
            _transitGatewayPolicyTable_key = "transitGatewayPolicyTable"
        elif "TransitGatewayPolicyTable" in data:
            _transitGatewayPolicyTable_key = "TransitGatewayPolicyTable"
        if _transitGatewayPolicyTable_key:
            param_data = data[_transitGatewayPolicyTable_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<transitGatewayPolicyTable>')
            xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</transitGatewayPolicyTable>')
        xml_parts.append(f'</DeleteTransitGatewayPolicyTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_transit_gateway_policy_tables_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeTransitGatewayPolicyTablesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
        # Serialize transitGatewayPolicyTables
        _transitGatewayPolicyTables_key = None
        if "transitGatewayPolicyTables" in data:
            _transitGatewayPolicyTables_key = "transitGatewayPolicyTables"
        elif "TransitGatewayPolicyTables" in data:
            _transitGatewayPolicyTables_key = "TransitGatewayPolicyTables"
        if _transitGatewayPolicyTables_key:
            param_data = data[_transitGatewayPolicyTables_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayPolicyTablesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayPolicyTablesSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayPolicyTablesSet/>')
        xml_parts.append(f'</DescribeTransitGatewayPolicyTablesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disassociate_transit_gateway_policy_table_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisassociateTransitGatewayPolicyTableResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize association
        _association_key = None
        if "association" in data:
            _association_key = "association"
        elif "Association" in data:
            _association_key = "Association"
        if _association_key:
            param_data = data[_association_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<association>')
            xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</association>')
        xml_parts.append(f'</DisassociateTransitGatewayPolicyTableResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_transit_gateway_policy_table_associations_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetTransitGatewayPolicyTableAssociationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize associations
        _associations_key = None
        if "associations" in data:
            _associations_key = "associations"
        elif "Associations" in data:
            _associations_key = "Associations"
        if _associations_key:
            param_data = data[_associations_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<associationsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</associationsSet>')
            else:
                xml_parts.append(f'{indent_str}<associationsSet/>')
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
        xml_parts.append(f'</GetTransitGatewayPolicyTableAssociationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_transit_gateway_policy_table_entries_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetTransitGatewayPolicyTableEntriesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize transitGatewayPolicyTableEntries
        _transitGatewayPolicyTableEntries_key = None
        if "transitGatewayPolicyTableEntries" in data:
            _transitGatewayPolicyTableEntries_key = "transitGatewayPolicyTableEntries"
        elif "TransitGatewayPolicyTableEntries" in data:
            _transitGatewayPolicyTableEntries_key = "TransitGatewayPolicyTableEntries"
        if _transitGatewayPolicyTableEntries_key:
            param_data = data[_transitGatewayPolicyTableEntries_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<transitGatewayPolicyTableEntriesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(transitgatewaypolicytable_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</transitGatewayPolicyTableEntriesSet>')
            else:
                xml_parts.append(f'{indent_str}<transitGatewayPolicyTableEntriesSet/>')
        xml_parts.append(f'</GetTransitGatewayPolicyTableEntriesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AssociateTransitGatewayPolicyTable": transitgatewaypolicytable_ResponseSerializer.serialize_associate_transit_gateway_policy_table_response,
            "CreateTransitGatewayPolicyTable": transitgatewaypolicytable_ResponseSerializer.serialize_create_transit_gateway_policy_table_response,
            "DeleteTransitGatewayPolicyTable": transitgatewaypolicytable_ResponseSerializer.serialize_delete_transit_gateway_policy_table_response,
            "DescribeTransitGatewayPolicyTables": transitgatewaypolicytable_ResponseSerializer.serialize_describe_transit_gateway_policy_tables_response,
            "DisassociateTransitGatewayPolicyTable": transitgatewaypolicytable_ResponseSerializer.serialize_disassociate_transit_gateway_policy_table_response,
            "GetTransitGatewayPolicyTableAssociations": transitgatewaypolicytable_ResponseSerializer.serialize_get_transit_gateway_policy_table_associations_response,
            "GetTransitGatewayPolicyTableEntries": transitgatewaypolicytable_ResponseSerializer.serialize_get_transit_gateway_policy_table_entries_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

