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
class CarrierGateway:
    carrier_gateway_id: str = ""
    owner_id: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    vpc_id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "carrierGatewayId": self.carrier_gateway_id,
            "ownerId": self.owner_id,
            "state": self.state,
            "tagSet": self.tag_set,
            "vpcId": self.vpc_id,
        }

class CarrierGateway_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.carrier_gateways  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.vpcs.get(params['vpc_id']).carrier_gateway_ids.append(new_id)
    #   Delete: self.state.vpcs.get(resource.vpc_id).carrier_gateway_ids.remove(resource_id)


    def CreateCarrierGateway(self, params: Dict[str, Any]):
        """Creates a carrier gateway.   For more information about carrier gateways, seeCarrier gatewaysin theAWS Wavelength Developer Guide."""

        if not params.get("VpcId"):
            return create_error_response("MissingParameter", "Missing required parameter: VpcId")

        vpc_id = params.get("VpcId")
        vpc = self.state.vpcs.get(vpc_id)
        if not vpc:
            return create_error_response("InvalidVpcID.NotFound", f"VPC '{vpc_id}' does not exist.")

        carrier_gateway_id = self._generate_id("cagw")
        tags: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tags.extend(spec.get("Tags", []) or [])

        resource = CarrierGateway(
            carrier_gateway_id=carrier_gateway_id,
            owner_id=getattr(vpc, "owner_id", ""),
            state=ResourceState.AVAILABLE.value,
            tag_set=tags,
            vpc_id=vpc_id,
        )
        self.resources[carrier_gateway_id] = resource

        if hasattr(vpc, "carrier_gateway_ids"):
            vpc.carrier_gateway_ids.append(carrier_gateway_id)

        return {
            'carrierGateway': resource.to_dict(),
            }

    def DeleteCarrierGateway(self, params: Dict[str, Any]):
        """Deletes a carrier gateway. If you do not delete the route that contains the carrier gateway as the
                Target, the route is a blackhole route. For information about how to delete a route, seeDeleteRoute."""

        if not params.get("CarrierGatewayId"):
            return create_error_response("MissingParameter", "Missing required parameter: CarrierGatewayId")

        carrier_gateway_id = params.get("CarrierGatewayId")
        resource = self.resources.get(carrier_gateway_id)
        if not resource:
            return create_error_response(
                "InvalidCarrierGatewayID.NotFound",
                f"The ID '{carrier_gateway_id}' does not exist",
            )

        vpc = self.state.vpcs.get(resource.vpc_id)
        if vpc and hasattr(vpc, "carrier_gateway_ids") and carrier_gateway_id in vpc.carrier_gateway_ids:
            vpc.carrier_gateway_ids.remove(carrier_gateway_id)

        del self.resources[carrier_gateway_id]

        return {
            'carrierGateway': resource.to_dict(),
            }

    def DescribeCarrierGateways(self, params: Dict[str, Any]):
        """Describes one or more of your carrier gateways."""

        carrier_gateway_ids = params.get("CarrierGatewayId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if carrier_gateway_ids:
            resources: List[CarrierGateway] = []
            for carrier_gateway_id in carrier_gateway_ids:
                resource = self.resources.get(carrier_gateway_id)
                if not resource:
                    return create_error_response(
                        "InvalidCarrierGatewayID.NotFound",
                        f"The ID '{carrier_gateway_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        carrier_gateways = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'carrierGatewaySet': carrier_gateways,
            'nextToken': None,
            }

    def _generate_id(self, prefix: str = 'cagw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class carriergateway_RequestParser:
    @staticmethod
    def parse_create_carrier_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VpcId": get_scalar(md, "VpcId"),
        }

    @staticmethod
    def parse_delete_carrier_gateway_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CarrierGatewayId": get_scalar(md, "CarrierGatewayId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_carrier_gateways_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CarrierGatewayId.N": get_indexed_list(md, "CarrierGatewayId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateCarrierGateway": carriergateway_RequestParser.parse_create_carrier_gateway_request,
            "DeleteCarrierGateway": carriergateway_RequestParser.parse_delete_carrier_gateway_request,
            "DescribeCarrierGateways": carriergateway_RequestParser.parse_describe_carrier_gateways_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class carriergateway_ResponseSerializer:
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
                xml_parts.extend(carriergateway_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(carriergateway_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(carriergateway_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(carriergateway_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(carriergateway_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(carriergateway_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_carrier_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateCarrierGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize carrierGateway
        _carrierGateway_key = None
        if "carrierGateway" in data:
            _carrierGateway_key = "carrierGateway"
        elif "CarrierGateway" in data:
            _carrierGateway_key = "CarrierGateway"
        if _carrierGateway_key:
            param_data = data[_carrierGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<carrierGateway>')
            xml_parts.extend(carriergateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</carrierGateway>')
        xml_parts.append(f'</CreateCarrierGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_carrier_gateway_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteCarrierGatewayResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize carrierGateway
        _carrierGateway_key = None
        if "carrierGateway" in data:
            _carrierGateway_key = "carrierGateway"
        elif "CarrierGateway" in data:
            _carrierGateway_key = "CarrierGateway"
        if _carrierGateway_key:
            param_data = data[_carrierGateway_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<carrierGateway>')
            xml_parts.extend(carriergateway_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</carrierGateway>')
        xml_parts.append(f'</DeleteCarrierGatewayResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_carrier_gateways_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCarrierGatewaysResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize carrierGatewaySet
        _carrierGatewaySet_key = None
        if "carrierGatewaySet" in data:
            _carrierGatewaySet_key = "carrierGatewaySet"
        elif "CarrierGatewaySet" in data:
            _carrierGatewaySet_key = "CarrierGatewaySet"
        elif "CarrierGateways" in data:
            _carrierGatewaySet_key = "CarrierGateways"
        if _carrierGatewaySet_key:
            param_data = data[_carrierGatewaySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<carrierGatewaySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(carriergateway_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</carrierGatewaySet>')
            else:
                xml_parts.append(f'{indent_str}<carrierGatewaySet/>')
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
        xml_parts.append(f'</DescribeCarrierGatewaysResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateCarrierGateway": carriergateway_ResponseSerializer.serialize_create_carrier_gateway_response,
            "DeleteCarrierGateway": carriergateway_ResponseSerializer.serialize_delete_carrier_gateway_response,
            "DescribeCarrierGateways": carriergateway_ResponseSerializer.serialize_describe_carrier_gateways_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

