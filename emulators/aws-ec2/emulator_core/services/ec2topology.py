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
class Ec2Topology:
    availability_zone: str = ""
    availability_zone_id: str = ""
    capacity_block_id: str = ""
    capacity_reservation_id: str = ""
    group_name: str = ""
    instance_type: str = ""
    network_node_set: List[Any] = field(default_factory=list)
    state: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "capacityBlockId": self.capacity_block_id,
            "capacityReservationId": self.capacity_reservation_id,
            "groupName": self.group_name,
            "instanceType": self.instance_type,
            "networkNodeSet": self.network_node_set,
            "state": self.state,
        }

class Ec2Topology_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.ec2_topology  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.capacity_reservations.get(params['capacity_reservation_id']).ec2_topology_ids.append(new_id)
    #   Delete: self.state.capacity_reservations.get(resource.capacity_reservation_id).ec2_topology_ids.remove(resource_id)


    def DescribeCapacityReservationTopology(self, params: Dict[str, Any]):
        """Describes a tree-based hierarchy that represents the physical host placement of your
            pending or active Capacity Reservations within an Availability Zone or Local Zone. You
            can use this information to determine the relative proximity of your capacity within the
            AWS"""

        capacity_reservation_ids = params.get("CapacityReservationId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if capacity_reservation_ids:
            for capacity_reservation_id in capacity_reservation_ids:
                if capacity_reservation_id not in self.state.capacity_reservations:
                    return create_error_response(
                        "InvalidCapacityReservationId.NotFound",
                        f"The ID '{capacity_reservation_id}' does not exist",
                    )

        resources = [
            resource for resource in self.resources.values()
            if resource.capacity_reservation_id
        ]
        if capacity_reservation_ids:
            resources = [
                resource for resource in resources
                if resource.capacity_reservation_id in capacity_reservation_ids
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))
        capacity_reservation_set = [
            resource.to_dict() for resource in resources[:max_results]
        ]

        return {
            'capacityReservationSet': capacity_reservation_set,
            'nextToken': None,
            }

    def DescribeInstanceTopology(self, params: Dict[str, Any]):
        """Describes a tree-based hierarchy that represents the physical host placement of your
            EC2 instances within an Availability Zone or Local Zone. You can use this information to
            determine the relative proximity of your EC2 instances within the AWS network to
            support y"""

        instance_ids = params.get("InstanceId.N", []) or []
        group_names = params.get("GroupName.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if instance_ids:
            for instance_id in instance_ids:
                if instance_id not in self.state.instances:
                    return create_error_response(
                        "InvalidInstanceID.NotFound",
                        f"The ID '{instance_id}' does not exist",
                    )

        resources = []
        for resource_id, resource in self.resources.items():
            instance_id = getattr(resource, "instance_id", resource_id)
            if instance_id not in self.state.instances:
                continue
            if instance_ids and instance_id not in instance_ids:
                continue
            if group_names and resource.group_name not in group_names:
                continue
            if not hasattr(resource, "instance_id"):
                setattr(resource, "instance_id", instance_id)
            if not hasattr(resource, "zone_id"):
                setattr(resource, "zone_id", resource.availability_zone_id)
            resources.append(resource)

        resources = apply_filters(resources, params.get("Filter.N", []))
        instance_set = []
        for resource in resources[:max_results]:
            instance_set.append({
                "availabilityZone": resource.availability_zone,
                "capacityBlockId": resource.capacity_block_id,
                "groupName": resource.group_name,
                "instanceId": getattr(resource, "instance_id", ""),
                "instanceType": resource.instance_type,
                "networkNodeSet": resource.network_node_set,
                "zoneId": getattr(resource, "zone_id", resource.availability_zone_id),
            })

        return {
            'instanceSet': instance_set,
            'nextToken': None,
            }

    def _generate_id(self, prefix: str = 'availability') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class ec2topology_RequestParser:
    @staticmethod
    def parse_describe_capacity_reservation_topology_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CapacityReservationId.N": get_indexed_list(md, "CapacityReservationId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_instance_topology_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "GroupName.N": get_indexed_list(md, "GroupName"),
            "InstanceId.N": get_indexed_list(md, "InstanceId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeCapacityReservationTopology": ec2topology_RequestParser.parse_describe_capacity_reservation_topology_request,
            "DescribeInstanceTopology": ec2topology_RequestParser.parse_describe_instance_topology_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class ec2topology_ResponseSerializer:
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
                xml_parts.extend(ec2topology_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(ec2topology_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(ec2topology_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(ec2topology_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(ec2topology_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(ec2topology_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_capacity_reservation_topology_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCapacityReservationTopologyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize capacityReservationSet
        _capacityReservationSet_key = None
        if "capacityReservationSet" in data:
            _capacityReservationSet_key = "capacityReservationSet"
        elif "CapacityReservationSet" in data:
            _capacityReservationSet_key = "CapacityReservationSet"
        elif "CapacityReservations" in data:
            _capacityReservationSet_key = "CapacityReservations"
        if _capacityReservationSet_key:
            param_data = data[_capacityReservationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<capacityReservationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2topology_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</capacityReservationSet>')
            else:
                xml_parts.append(f'{indent_str}<capacityReservationSet/>')
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
        xml_parts.append(f'</DescribeCapacityReservationTopologyResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_instance_topology_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeInstanceTopologyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceSet
        _instanceSet_key = None
        if "instanceSet" in data:
            _instanceSet_key = "instanceSet"
        elif "InstanceSet" in data:
            _instanceSet_key = "InstanceSet"
        elif "Instances" in data:
            _instanceSet_key = "Instances"
        if _instanceSet_key:
            param_data = data[_instanceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2topology_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</instanceSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceSet/>')
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
        xml_parts.append(f'</DescribeInstanceTopologyResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeCapacityReservationTopology": ec2topology_ResponseSerializer.serialize_describe_capacity_reservation_topology_response,
            "DescribeInstanceTopology": ec2topology_ResponseSerializer.serialize_describe_instance_topology_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

