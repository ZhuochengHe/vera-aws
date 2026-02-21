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
from .instance import Instance

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
class ScheduledInstance:
    availability_zone: str = ""
    create_date: str = ""
    hourly_price: str = ""
    instance_count: int = 0
    instance_type: str = ""
    network_platform: str = ""
    next_slot_start_time: str = ""
    platform: str = ""
    previous_slot_end_time: str = ""
    recurrence: Dict[str, Any] = field(default_factory=dict)
    scheduled_instance_id: str = ""
    slot_duration_in_hours: int = 0
    term_end_date: str = ""
    term_start_date: str = ""
    total_scheduled_instance_hours: int = 0

    launched_instance_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "createDate": self.create_date,
            "hourlyPrice": self.hourly_price,
            "instanceCount": self.instance_count,
            "instanceType": self.instance_type,
            "networkPlatform": self.network_platform,
            "nextSlotStartTime": self.next_slot_start_time,
            "platform": self.platform,
            "previousSlotEndTime": self.previous_slot_end_time,
            "recurrence": self.recurrence,
            "scheduledInstanceId": self.scheduled_instance_id,
            "slotDurationInHours": self.slot_duration_in_hours,
            "termEndDate": self.term_end_date,
            "termStartDate": self.term_start_date,
            "totalScheduledInstanceHours": self.total_scheduled_instance_hours,
            "launchedInstanceIds": self.launched_instance_ids,
        }

class ScheduledInstance_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.scheduled_instances  # alias to shared store


    def _require_params(self, params: Dict[str, Any], names: List[str]):
        for name in names:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(self, store: Dict[str, Any], resource_id: str, error_code: str, message: Optional[str] = None):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message or f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources = []
        for resource_id in resource_ids:
            resource = store.get(resource_id)
            if not resource:
                return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
            resources.append(resource)
        return resources, None

    def DescribeScheduledInstanceAvailability(self, params: Dict[str, Any]):
        """Finds available schedules that meet the specified criteria. You can search for an available schedule no more than 3 months in advance. You must meet the minimum required duration of 1,200 hours per year. For example, the minimum daily schedule is 4 hours, the minimum weekly schedule is 24 hours, and"""

        error = self._require_params(params, ["FirstSlotStartTimeRange", "Recurrence"])
        if error:
            return error

        resources = list(self.resources.values())
        min_slot_duration = int(params.get("MinSlotDurationInHours") or 0)
        max_slot_duration = int(params.get("MaxSlotDurationInHours") or 0)
        if min_slot_duration:
            resources = [resource for resource in resources if resource.slot_duration_in_hours >= min_slot_duration]
        if max_slot_duration:
            resources = [resource for resource in resources if resource.slot_duration_in_hours <= max_slot_duration]

        filtered = apply_filters(resources, params.get("Filter.N", []))
        first_slot_start_time = params.get("FirstSlotStartTimeRange") or ""
        recurrence_param = params.get("Recurrence") or {}

        availability_set = []
        for resource in filtered:
            recurrence = resource.recurrence or recurrence_param
            availability_set.append({
                "availabilityZone": resource.availability_zone,
                "availableInstanceCount": resource.instance_count,
                "firstSlotStartTime": resource.next_slot_start_time or first_slot_start_time,
                "hourlyPrice": resource.hourly_price,
                "instanceType": resource.instance_type,
                "maxTermDurationInDays": 0,
                "minTermDurationInDays": 0,
                "networkPlatform": resource.network_platform,
                "platform": resource.platform,
                "purchaseToken": resource.scheduled_instance_id,
                "recurrence": recurrence,
                "slotDurationInHours": resource.slot_duration_in_hours,
                "totalScheduledInstanceHours": resource.total_scheduled_instance_hours,
            })

        return {
            'nextToken': None,
            'scheduledInstanceAvailabilitySet': availability_set,
            }

    def DescribeScheduledInstances(self, params: Dict[str, Any]):
        """Describes the specified Scheduled Instances or all your Scheduled Instances."""

        scheduled_instance_ids = params.get("ScheduledInstanceId.N", []) or []
        if scheduled_instance_ids:
            resources, error = self._get_resources_by_ids(
                self.resources,
                scheduled_instance_ids,
                "InvalidScheduledInstanceID.NotFound",
            )
            if error:
                return error
        else:
            resources = list(self.resources.values())

        filtered = apply_filters(resources, params.get("Filter.N", []))
        scheduled_instance_set = [resource.to_dict() for resource in filtered]

        return {
            'nextToken': None,
            'scheduledInstanceSet': scheduled_instance_set,
            }

    def PurchaseScheduledInstances(self, params: Dict[str, Any]):
        """You can no longer purchase Scheduled Instances. Purchases the Scheduled Instances with the specified schedule. Scheduled Instances enable you to purchase Amazon EC2 compute capacity by the hour for a one-year term.
         Before you can purchase a Scheduled Instance, you must callDescribeScheduled"""

        error = self._require_params(params, ["PurchaseRequest.N"])
        if error:
            return error

        purchase_requests = params.get("PurchaseRequest.N", []) or []
        now = datetime.now(timezone.utc).isoformat()
        scheduled_instance_set = []
        for request in purchase_requests:
            request_data = request if isinstance(request, dict) else {}
            instance_count = int(request_data.get("InstanceCount") or request_data.get("instanceCount") or 1)
            if instance_count <= 0:
                instance_count = 1
            recurrence = request_data.get("recurrence") or request_data.get("Recurrence") or {}
            if recurrence and not isinstance(recurrence, dict):
                recurrence = {"recurrence": recurrence}
            scheduled_instance_id = self._generate_id("scheduled")
            resource = ScheduledInstance(
                availability_zone=request_data.get("availabilityZone") or request_data.get("AvailabilityZone") or "",
                create_date=now,
                hourly_price=request_data.get("hourlyPrice") or request_data.get("HourlyPrice") or "",
                instance_count=instance_count,
                instance_type=request_data.get("instanceType") or request_data.get("InstanceType") or "",
                network_platform=request_data.get("networkPlatform") or request_data.get("NetworkPlatform") or "",
                next_slot_start_time=request_data.get("nextSlotStartTime") or request_data.get("NextSlotStartTime") or "",
                platform=request_data.get("platform") or request_data.get("Platform") or "",
                previous_slot_end_time=request_data.get("previousSlotEndTime") or request_data.get("PreviousSlotEndTime") or "",
                recurrence=recurrence if isinstance(recurrence, dict) else {},
                scheduled_instance_id=scheduled_instance_id,
                slot_duration_in_hours=int(request_data.get("slotDurationInHours") or request_data.get("SlotDurationInHours") or 0),
                term_end_date=request_data.get("termEndDate") or request_data.get("TermEndDate") or "",
                term_start_date=request_data.get("termStartDate") or request_data.get("TermStartDate") or "",
                total_scheduled_instance_hours=int(request_data.get("totalScheduledInstanceHours") or request_data.get("TotalScheduledInstanceHours") or 0),
            )
            self.resources[scheduled_instance_id] = resource
            scheduled_instance_set.append(resource.to_dict())

        return {
            'scheduledInstanceSet': scheduled_instance_set,
            }

    def RunScheduledInstances(self, params: Dict[str, Any]):
        """Launches the specified Scheduled Instances. Before you can launch a Scheduled Instance, you must purchase it and obtain an identifier usingPurchaseScheduledInstances. You must launch a Scheduled Instance during its scheduled time period. You can't stop or
         reboot a Scheduled Instance, but yo"""

        error = self._require_params(params, ["LaunchSpecification", "ScheduledInstanceId"])
        if error:
            return error

        scheduled_instance_id = params.get("ScheduledInstanceId") or ""
        scheduled_instance, error = self._get_resource_or_error(
            self.resources,
            scheduled_instance_id,
            "InvalidScheduledInstanceID.NotFound",
        )
        if error:
            return error

        launch_spec = params.get("LaunchSpecification") or {}
        if not isinstance(launch_spec, dict):
            launch_spec = {}

        instance_count = int(params.get("InstanceCount") or 1)
        if instance_count <= 0:
            return create_error_response("InvalidParameterValue", "InstanceCount must be greater than 0")
        if scheduled_instance.instance_count and instance_count > scheduled_instance.instance_count:
            return create_error_response("InvalidParameterValue", "InstanceCount exceeds scheduled instance count")

        image_id = launch_spec.get("ImageId") or ""
        if image_id and image_id not in self.state.amis:
            return create_error_response("InvalidAMIID.NotFound", f"AMI '{image_id}' does not exist.")

        subnet_id = launch_spec.get("SubnetId") or ""
        subnet = None
        if subnet_id:
            subnet = self.state.subnets.get(subnet_id)
            if not subnet:
                return create_error_response("InvalidSubnetID.NotFound", f"Subnet '{subnet_id}' does not exist.")

        key_name = launch_spec.get("KeyName") or ""
        if key_name and key_name not in self.state.key_pairs:
            return create_error_response("InvalidKeyPair.NotFound", f"Key pair '{key_name}' does not exist.")

        security_group_ids = launch_spec.get("SecurityGroupId.N", []) or launch_spec.get("SecurityGroupIds", []) or launch_spec.get("SecurityGroupId", [])
        if isinstance(security_group_ids, str):
            security_group_ids = [security_group_ids]
        group_set = []
        for group_id in security_group_ids:
            group = self.state.security_groups.get(group_id)
            if not group:
                return create_error_response("InvalidSecurityGroupID.NotFound", f"Security group '{group_id}' does not exist.")
            group_set.append({"GroupId": group_id, "GroupName": getattr(group, "group_name", "")})

        placement = launch_spec.get("Placement") or {}
        if not placement and scheduled_instance.availability_zone:
            placement = {"AvailabilityZone": scheduled_instance.availability_zone}
        if placement and not isinstance(placement, dict):
            placement = {}

        now = datetime.now(timezone.utc).isoformat()
        instance_ids = []
        for _ in range(instance_count):
            instance_id = self._generate_id("i")
            instance = Instance(
                instance_id=instance_id,
                instance_state={"code": 16, "name": "running"},
                instance_type=launch_spec.get("InstanceType") or scheduled_instance.instance_type or "",
                image_id=image_id,
                key_name=key_name,
                launch_time=now,
                subnet_id=subnet_id,
                group_set=list(group_set),
                placement=placement,
                platform=scheduled_instance.platform or "",
            )
            self.state.instances[instance_id] = instance
            if subnet and instance_id not in subnet.instance_ids:
                subnet.instance_ids.append(instance_id)
            scheduled_instance.launched_instance_ids.append(instance_id)
            instance_ids.append(instance_id)

        return {
            'instanceIdSet': instance_ids,
            }

    def _generate_id(self, prefix: str = 'scheduled') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class scheduledinstance_RequestParser:
    @staticmethod
    def parse_describe_scheduled_instance_availability_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "FirstSlotStartTimeRange": get_scalar(md, "FirstSlotStartTimeRange"),
            "MaxResults": get_int(md, "MaxResults"),
            "MaxSlotDurationInHours": get_int(md, "MaxSlotDurationInHours"),
            "MinSlotDurationInHours": get_int(md, "MinSlotDurationInHours"),
            "NextToken": get_scalar(md, "NextToken"),
            "Recurrence": get_scalar(md, "Recurrence"),
        }

    @staticmethod
    def parse_describe_scheduled_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ScheduledInstanceId.N": get_indexed_list(md, "ScheduledInstanceId"),
            "SlotStartTimeRange": get_scalar(md, "SlotStartTimeRange"),
        }

    @staticmethod
    def parse_purchase_scheduled_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PurchaseRequest.N": get_indexed_list(md, "PurchaseRequest"),
        }

    @staticmethod
    def parse_run_scheduled_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceCount": get_int(md, "InstanceCount"),
            "LaunchSpecification": get_scalar(md, "LaunchSpecification"),
            "ScheduledInstanceId": get_scalar(md, "ScheduledInstanceId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeScheduledInstanceAvailability": scheduledinstance_RequestParser.parse_describe_scheduled_instance_availability_request,
            "DescribeScheduledInstances": scheduledinstance_RequestParser.parse_describe_scheduled_instances_request,
            "PurchaseScheduledInstances": scheduledinstance_RequestParser.parse_purchase_scheduled_instances_request,
            "RunScheduledInstances": scheduledinstance_RequestParser.parse_run_scheduled_instances_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class scheduledinstance_ResponseSerializer:
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
                xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_scheduled_instance_availability_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeScheduledInstanceAvailabilityResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize scheduledInstanceAvailabilitySet
        _scheduledInstanceAvailabilitySet_key = None
        if "scheduledInstanceAvailabilitySet" in data:
            _scheduledInstanceAvailabilitySet_key = "scheduledInstanceAvailabilitySet"
        elif "ScheduledInstanceAvailabilitySet" in data:
            _scheduledInstanceAvailabilitySet_key = "ScheduledInstanceAvailabilitySet"
        elif "ScheduledInstanceAvailabilitys" in data:
            _scheduledInstanceAvailabilitySet_key = "ScheduledInstanceAvailabilitys"
        if _scheduledInstanceAvailabilitySet_key:
            param_data = data[_scheduledInstanceAvailabilitySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<scheduledInstanceAvailabilitySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</scheduledInstanceAvailabilitySet>')
            else:
                xml_parts.append(f'{indent_str}<scheduledInstanceAvailabilitySet/>')
        xml_parts.append(f'</DescribeScheduledInstanceAvailabilityResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_scheduled_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeScheduledInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize scheduledInstanceSet
        _scheduledInstanceSet_key = None
        if "scheduledInstanceSet" in data:
            _scheduledInstanceSet_key = "scheduledInstanceSet"
        elif "ScheduledInstanceSet" in data:
            _scheduledInstanceSet_key = "ScheduledInstanceSet"
        elif "ScheduledInstances" in data:
            _scheduledInstanceSet_key = "ScheduledInstances"
        if _scheduledInstanceSet_key:
            param_data = data[_scheduledInstanceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<scheduledInstanceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</scheduledInstanceSet>')
            else:
                xml_parts.append(f'{indent_str}<scheduledInstanceSet/>')
        xml_parts.append(f'</DescribeScheduledInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_purchase_scheduled_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<PurchaseScheduledInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize scheduledInstanceSet
        _scheduledInstanceSet_key = None
        if "scheduledInstanceSet" in data:
            _scheduledInstanceSet_key = "scheduledInstanceSet"
        elif "ScheduledInstanceSet" in data:
            _scheduledInstanceSet_key = "ScheduledInstanceSet"
        elif "ScheduledInstances" in data:
            _scheduledInstanceSet_key = "ScheduledInstances"
        if _scheduledInstanceSet_key:
            param_data = data[_scheduledInstanceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<scheduledInstanceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(scheduledinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</scheduledInstanceSet>')
            else:
                xml_parts.append(f'{indent_str}<scheduledInstanceSet/>')
        xml_parts.append(f'</PurchaseScheduledInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_run_scheduled_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RunScheduledInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize instanceIdSet
        _instanceIdSet_key = None
        if "instanceIdSet" in data:
            _instanceIdSet_key = "instanceIdSet"
        elif "InstanceIdSet" in data:
            _instanceIdSet_key = "InstanceIdSet"
        elif "InstanceIds" in data:
            _instanceIdSet_key = "InstanceIds"
        if _instanceIdSet_key:
            param_data = data[_instanceIdSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<instanceIdSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</instanceIdSet>')
            else:
                xml_parts.append(f'{indent_str}<instanceIdSet/>')
        xml_parts.append(f'</RunScheduledInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeScheduledInstanceAvailability": scheduledinstance_ResponseSerializer.serialize_describe_scheduled_instance_availability_response,
            "DescribeScheduledInstances": scheduledinstance_ResponseSerializer.serialize_describe_scheduled_instances_response,
            "PurchaseScheduledInstances": scheduledinstance_ResponseSerializer.serialize_purchase_scheduled_instances_response,
            "RunScheduledInstances": scheduledinstance_ResponseSerializer.serialize_run_scheduled_instances_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

