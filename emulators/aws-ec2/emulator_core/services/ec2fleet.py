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
class Ec2Fleet:
    event_information: Dict[str, Any] = field(default_factory=dict)
    event_type: str = ""
    timestamp: str = ""

    fleet_id: str = ""
    activity_status: str = ""
    client_token: str = ""
    context: str = ""
    create_time: str = ""
    error_set: List[Dict[str, Any]] = field(default_factory=list)
    excess_capacity_termination_policy: str = ""
    fleet_instance_set: List[Dict[str, Any]] = field(default_factory=list)
    fleet_state: str = ""
    fulfilled_capacity: float = 0.0
    fulfilled_on_demand_capacity: float = 0.0
    launch_template_configs: List[Dict[str, Any]] = field(default_factory=list)
    on_demand_options: Dict[str, Any] = field(default_factory=dict)
    replace_unhealthy_instances: bool = False
    spot_options: Dict[str, Any] = field(default_factory=dict)
    tag_set: List[Dict[str, Any]] = field(default_factory=list)
    target_capacity_specification: Dict[str, Any] = field(default_factory=dict)
    terminate_instances_with_expiration: bool = False
    type: str = ""
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    history_records: List[Dict[str, Any]] = field(default_factory=list)
    active_instance_set: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eventInformation": self.event_information,
            "eventType": self.event_type,
            "timestamp": self.timestamp,
            "activityStatus": self.activity_status,
            "clientToken": self.client_token,
            "context": self.context,
            "createTime": self.create_time,
            "errorSet": self.error_set,
            "excessCapacityTerminationPolicy": self.excess_capacity_termination_policy,
            "fleetId": self.fleet_id,
            "fleetInstanceSet": self.fleet_instance_set,
            "fleetState": self.fleet_state,
            "fulfilledCapacity": self.fulfilled_capacity,
            "fulfilledOnDemandCapacity": self.fulfilled_on_demand_capacity,
            "launchTemplateConfigs": self.launch_template_configs,
            "onDemandOptions": self.on_demand_options,
            "replaceUnhealthyInstances": self.replace_unhealthy_instances,
            "spotOptions": self.spot_options,
            "tagSet": self.tag_set,
            "targetCapacitySpecification": self.target_capacity_specification,
            "terminateInstancesWithExpiration": self.terminate_instances_with_expiration,
            "type": self.type,
            "validFrom": self.valid_from,
            "validUntil": self.valid_until,
            "historyRecords": self.history_records,
            "activeInstanceSet": self.active_instance_set,
        }

class Ec2Fleet_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.ec2_fleet  # alias to shared store

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _get_fleet_or_error(self, fleet_id: str) -> Any:
        fleet = self.resources.get(fleet_id)
        if not fleet:
            return create_error_response("InvalidFleetID.NotFound", f"Fleet '{fleet_id}' does not exist.")
        return fleet

    def _append_history(self, fleet: Ec2Fleet, event_type: str, event_information: Optional[Dict[str, Any]] = None) -> None:
        fleet.history_records.append({
            "eventInformation": event_information or {},
            "eventType": event_type,
            "timestamp": self._now_iso(),
        })

    def CreateFleet(self, params: Dict[str, Any]):
        """Creates an EC2 Fleet that contains the configuration information for On-Demand Instances and Spot Instances.
         Instances are launched immediately if there is available capacity. A single EC2 Fleet can include multiple launch specifications that vary by instance type,
         AMI, Availabilit"""

        launch_template_configs = params.get("LaunchTemplateConfigs.N") or []
        if not launch_template_configs:
            return create_error_response("MissingParameter", "Missing required parameter: LaunchTemplateConfigs.N")
        target_capacity_spec = params.get("TargetCapacitySpecification")
        if not target_capacity_spec:
            return create_error_response("MissingParameter", "Missing required parameter: TargetCapacitySpecification")

        fleet_id = self._generate_id("ec2")
        resource = Ec2Fleet(
            fleet_id=fleet_id,
            client_token=params.get("ClientToken") or "",
            context=params.get("Context") or "",
            create_time=self._now_iso(),
            excess_capacity_termination_policy=params.get("ExcessCapacityTerminationPolicy") or "",
            launch_template_configs=launch_template_configs,
            on_demand_options=params.get("OnDemandOptions") or {},
            replace_unhealthy_instances=str2bool(params.get("ReplaceUnhealthyInstances")),
            spot_options=params.get("SpotOptions") or {},
            tag_set=params.get("TagSpecification.N") or [],
            target_capacity_specification=target_capacity_spec,
            terminate_instances_with_expiration=str2bool(params.get("TerminateInstancesWithExpiration")),
            type=params.get("Type") or "maintain",
            valid_from=params.get("ValidFrom"),
            valid_until=params.get("ValidUntil"),
            activity_status="pending_fulfillment",
            fleet_state="active",
        )
        resource.fulfilled_on_demand_capacity = float(target_capacity_spec.get("OnDemandTargetCapacity") or 0)
        resource.fulfilled_capacity = 0.0
        self._append_history(resource, "fleet_request_created", {"eventDescription": "Fleet created"})
        self.resources[fleet_id] = resource

        return {
            'errorSet': [],
            'fleetId': fleet_id,
            'fleetInstanceSet': resource.fleet_instance_set,
            }

    def DeleteFleets(self, params: Dict[str, Any]):
        """Deletes the specified EC2 Fleet request. After you delete an EC2 Fleet request, it launches no new instances. You must also specify whether a deleted EC2 Fleet request should terminate its instances. If
         you choose to terminate the instances, the EC2 Fleet request enters thedeleted_terminati"""

        fleet_ids = params.get("FleetId.N") or []
        if not fleet_ids:
            return create_error_response("MissingParameter", "Missing required parameter: FleetId.N")
        terminate_instances = params.get("TerminateInstances")
        if terminate_instances is None:
            return create_error_response("MissingParameter", "Missing required parameter: TerminateInstances")

        for fleet_id in fleet_ids:
            if fleet_id not in self.resources:
                return create_error_response("InvalidFleetID.NotFound", f"The ID '{fleet_id}' does not exist")

        terminate_instances_bool = str2bool(terminate_instances)
        successful = []
        for fleet_id in fleet_ids:
            fleet = self.resources.get(fleet_id)
            if not fleet:
                continue
            previous_state = fleet.fleet_state or "active"
            current_state = "deleted_terminating" if terminate_instances_bool else "deleted"
            fleet.fleet_state = current_state
            self._append_history(fleet, "fleet_request_deleted", {"eventDescription": "Fleet deleted"})
            self.resources.pop(fleet_id, None)
            successful.append({
                "currentFleetState": current_state,
                "fleetId": fleet_id,
                "previousFleetState": previous_state,
            })

        return {
            'successfulFleetDeletionSet': successful,
            'unsuccessfulFleetDeletionSet': [],
            }

    def DescribeFleetHistory(self, params: Dict[str, Any]):
        """Describes the events for the specified EC2 Fleet during the specified time. EC2 Fleet events are delayed by up to 30 seconds before they can be described. This ensures
         that you can query by the last evaluated time and not miss a recorded event. EC2 Fleet events
         are available for 48"""

        fleet_id = params.get("FleetId")
        if not fleet_id:
            return create_error_response("MissingParameter", "Missing required parameter: FleetId")
        start_time = params.get("StartTime")
        if not start_time:
            return create_error_response("MissingParameter", "Missing required parameter: StartTime")

        fleet = self._get_fleet_or_error(fleet_id)
        if is_error_response(fleet):
            return fleet

        history_records = list(fleet.history_records)
        event_type = params.get("EventType")
        if event_type:
            history_records = [record for record in history_records if record.get("eventType") == event_type]

        def _parse_time(value: Any) -> Optional[datetime]:
            if isinstance(value, datetime):
                return value
            if not isinstance(value, str):
                return None
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None

        start_dt = _parse_time(start_time)
        if start_dt:
            filtered_records = []
            for record in history_records:
                record_dt = _parse_time(record.get("timestamp"))
                if record_dt and record_dt >= start_dt:
                    filtered_records.append(record)
                elif not record_dt:
                    filtered_records.append(record)
            history_records = filtered_records

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token) if next_token else 0
        except (TypeError, ValueError):
            start_index = 0
        paged_records = history_records[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(history_records):
            new_next_token = str(start_index + max_results)

        last_evaluated_time = paged_records[-1]["timestamp"] if paged_records else start_time

        return {
            'fleetId': fleet_id,
            'historyRecordSet': paged_records,
            'lastEvaluatedTime': last_evaluated_time,
            'nextToken': new_next_token,
            'startTime': start_time,
            }

    def DescribeFleetInstances(self, params: Dict[str, Any]):
        """Describes the running instances for the specified EC2 Fleet. Currently,DescribeFleetInstancesdoes not support fleets of typeinstant. Instead, useDescribeFleets, specifying theinstantfleet ID in the request. For more information, seeDescribe your
            EC2 Fleetin theAmazon EC2 User Guide."""

        fleet_id = params.get("FleetId")
        if not fleet_id:
            return create_error_response("MissingParameter", "Missing required parameter: FleetId")

        fleet = self._get_fleet_or_error(fleet_id)
        if is_error_response(fleet):
            return fleet

        active_instances = list(fleet.active_instance_set)
        filters = params.get("Filter.N", [])
        if filters:
            active_instances = apply_filters(active_instances, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token) if next_token else 0
        except (TypeError, ValueError):
            start_index = 0
        paged_instances = active_instances[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(active_instances):
            new_next_token = str(start_index + max_results)

        return {
            'activeInstanceSet': paged_instances,
            'fleetId': fleet_id,
            'nextToken': new_next_token,
            }

    def DescribeFleets(self, params: Dict[str, Any]):
        """Describes the specified EC2 Fleet or all of your EC2 Fleets. If a fleet is of typeinstant, you must specify the fleet ID in the
            request, otherwise the fleet does not appear in the response. For more information, seeDescribe your
            EC2 Fleetin theAmazon EC2 User Guide."""

        fleet_ids = params.get("FleetId.N") or []
        resources = []
        if fleet_ids:
            for fleet_id in fleet_ids:
                fleet = self.resources.get(fleet_id)
                if not fleet:
                    return create_error_response("InvalidFleetID.NotFound", f"The ID '{fleet_id}' does not exist")
                resources.append(fleet)
        else:
            resources = list(self.resources.values())

        fleet_set = []
        for fleet in resources:
            fleet_set.append({
                "activityStatus": fleet.activity_status,
                "clientToken": fleet.client_token,
                "context": fleet.context,
                "createTime": fleet.create_time,
                "errorSet": fleet.error_set,
                "excessCapacityTerminationPolicy": fleet.excess_capacity_termination_policy,
                "fleetId": fleet.fleet_id,
                "fleetInstanceSet": fleet.fleet_instance_set,
                "fleetState": fleet.fleet_state,
                "fulfilledCapacity": fleet.fulfilled_capacity,
                "fulfilledOnDemandCapacity": fleet.fulfilled_on_demand_capacity,
                "launchTemplateConfigs": fleet.launch_template_configs,
                "onDemandOptions": fleet.on_demand_options,
                "replaceUnhealthyInstances": fleet.replace_unhealthy_instances,
                "spotOptions": fleet.spot_options,
                "tagSet": fleet.tag_set,
                "targetCapacitySpecification": fleet.target_capacity_specification,
                "terminateInstancesWithExpiration": fleet.terminate_instances_with_expiration,
                "type": fleet.type,
                "validFrom": fleet.valid_from,
                "validUntil": fleet.valid_until,
            })

        filters = params.get("Filter.N", [])
        if filters:
            fleet_set = apply_filters(fleet_set, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token) if next_token else 0
        except (TypeError, ValueError):
            start_index = 0
        paged_fleets = fleet_set[start_index:start_index + max_results]
        new_next_token = None
        if start_index + max_results < len(fleet_set):
            new_next_token = str(start_index + max_results)

        return {
            'fleetSet': paged_fleets,
            'nextToken': new_next_token,
            }

    def ModifyFleet(self, params: Dict[str, Any]):
        """Modifies the specified EC2 Fleet. You can only modify an EC2 Fleet request of typemaintain. While the EC2 Fleet is being modified, it is in themodifyingstate."""

        fleet_id = params.get("FleetId")
        if not fleet_id:
            return create_error_response("MissingParameter", "Missing required parameter: FleetId")

        fleet = self._get_fleet_or_error(fleet_id)
        if is_error_response(fleet):
            return fleet

        if fleet.type and fleet.type != "maintain":
            return create_error_response("InvalidParameterValue", "Fleet type must be 'maintain' to modify.")

        if params.get("Context") is not None:
            fleet.context = params.get("Context") or ""
        if params.get("ExcessCapacityTerminationPolicy") is not None:
            fleet.excess_capacity_termination_policy = params.get("ExcessCapacityTerminationPolicy") or ""
        launch_template_configs = params.get("LaunchTemplateConfig.N")
        if launch_template_configs:
            fleet.launch_template_configs = launch_template_configs
        target_capacity_spec = params.get("TargetCapacitySpecification")
        if target_capacity_spec:
            fleet.target_capacity_specification = target_capacity_spec
            fleet.fulfilled_on_demand_capacity = float(target_capacity_spec.get("OnDemandTargetCapacity") or 0)

        fleet.activity_status = "modifying"
        self._append_history(fleet, "fleet_request_modified", {"eventDescription": "Fleet modified"})

        return {
            'return': True,
            }

    def _generate_id(self, prefix: str = 'ec2') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class ec2fleet_RequestParser:
    @staticmethod
    def parse_create_fleet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Context": get_scalar(md, "Context"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExcessCapacityTerminationPolicy": get_scalar(md, "ExcessCapacityTerminationPolicy"),
            "LaunchTemplateConfigs.N": get_indexed_list(md, "LaunchTemplateConfigs"),
            "OnDemandOptions": get_scalar(md, "OnDemandOptions"),
            "ReplaceUnhealthyInstances": get_scalar(md, "ReplaceUnhealthyInstances"),
            "SpotOptions": get_scalar(md, "SpotOptions"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TargetCapacitySpecification": get_scalar(md, "TargetCapacitySpecification"),
            "TerminateInstancesWithExpiration": get_scalar(md, "TerminateInstancesWithExpiration"),
            "Type": get_scalar(md, "Type"),
            "ValidFrom": get_scalar(md, "ValidFrom"),
            "ValidUntil": get_scalar(md, "ValidUntil"),
        }

    @staticmethod
    def parse_delete_fleets_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FleetId.N": get_indexed_list(md, "FleetId"),
            "TerminateInstances": get_scalar(md, "TerminateInstances"),
        }

    @staticmethod
    def parse_describe_fleet_history_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EventType": get_scalar(md, "EventType"),
            "FleetId": get_scalar(md, "FleetId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "StartTime": get_scalar(md, "StartTime"),
        }

    @staticmethod
    def parse_describe_fleet_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "FleetId": get_scalar(md, "FleetId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_fleets_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "FleetId.N": get_indexed_list(md, "FleetId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_modify_fleet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Context": get_scalar(md, "Context"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExcessCapacityTerminationPolicy": get_scalar(md, "ExcessCapacityTerminationPolicy"),
            "FleetId": get_scalar(md, "FleetId"),
            "LaunchTemplateConfig.N": get_indexed_list(md, "LaunchTemplateConfig"),
            "TargetCapacitySpecification": get_scalar(md, "TargetCapacitySpecification"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateFleet": ec2fleet_RequestParser.parse_create_fleet_request,
            "DeleteFleets": ec2fleet_RequestParser.parse_delete_fleets_request,
            "DescribeFleetHistory": ec2fleet_RequestParser.parse_describe_fleet_history_request,
            "DescribeFleetInstances": ec2fleet_RequestParser.parse_describe_fleet_instances_request,
            "DescribeFleets": ec2fleet_RequestParser.parse_describe_fleets_request,
            "ModifyFleet": ec2fleet_RequestParser.parse_modify_fleet_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class ec2fleet_ResponseSerializer:
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
                xml_parts.extend(ec2fleet_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(ec2fleet_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(ec2fleet_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(ec2fleet_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_fleet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateFleetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize errorSet
        _errorSet_key = None
        if "errorSet" in data:
            _errorSet_key = "errorSet"
        elif "ErrorSet" in data:
            _errorSet_key = "ErrorSet"
        elif "Errors" in data:
            _errorSet_key = "Errors"
        if _errorSet_key:
            param_data = data[_errorSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<errorSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</errorSet>')
            else:
                xml_parts.append(f'{indent_str}<errorSet/>')
        # Serialize fleetId
        _fleetId_key = None
        if "fleetId" in data:
            _fleetId_key = "fleetId"
        elif "FleetId" in data:
            _fleetId_key = "FleetId"
        if _fleetId_key:
            param_data = data[_fleetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fleetId>{esc(str(param_data))}</fleetId>')
        # Serialize fleetInstanceSet
        _fleetInstanceSet_key = None
        if "fleetInstanceSet" in data:
            _fleetInstanceSet_key = "fleetInstanceSet"
        elif "FleetInstanceSet" in data:
            _fleetInstanceSet_key = "FleetInstanceSet"
        elif "FleetInstances" in data:
            _fleetInstanceSet_key = "FleetInstances"
        if _fleetInstanceSet_key:
            param_data = data[_fleetInstanceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<fleetInstanceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</fleetInstanceSet>')
            else:
                xml_parts.append(f'{indent_str}<fleetInstanceSet/>')
        xml_parts.append(f'</CreateFleetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_fleets_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteFleetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successfulFleetDeletionSet
        _successfulFleetDeletionSet_key = None
        if "successfulFleetDeletionSet" in data:
            _successfulFleetDeletionSet_key = "successfulFleetDeletionSet"
        elif "SuccessfulFleetDeletionSet" in data:
            _successfulFleetDeletionSet_key = "SuccessfulFleetDeletionSet"
        elif "SuccessfulFleetDeletions" in data:
            _successfulFleetDeletionSet_key = "SuccessfulFleetDeletions"
        if _successfulFleetDeletionSet_key:
            param_data = data[_successfulFleetDeletionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulFleetDeletionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</successfulFleetDeletionSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulFleetDeletionSet/>')
        # Serialize unsuccessfulFleetDeletionSet
        _unsuccessfulFleetDeletionSet_key = None
        if "unsuccessfulFleetDeletionSet" in data:
            _unsuccessfulFleetDeletionSet_key = "unsuccessfulFleetDeletionSet"
        elif "UnsuccessfulFleetDeletionSet" in data:
            _unsuccessfulFleetDeletionSet_key = "UnsuccessfulFleetDeletionSet"
        elif "UnsuccessfulFleetDeletions" in data:
            _unsuccessfulFleetDeletionSet_key = "UnsuccessfulFleetDeletions"
        if _unsuccessfulFleetDeletionSet_key:
            param_data = data[_unsuccessfulFleetDeletionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulFleetDeletionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulFleetDeletionSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulFleetDeletionSet/>')
        xml_parts.append(f'</DeleteFleetsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_fleet_history_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeFleetHistoryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fleetId
        _fleetId_key = None
        if "fleetId" in data:
            _fleetId_key = "fleetId"
        elif "FleetId" in data:
            _fleetId_key = "FleetId"
        if _fleetId_key:
            param_data = data[_fleetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fleetId>{esc(str(param_data))}</fleetId>')
        # Serialize historyRecordSet
        _historyRecordSet_key = None
        if "historyRecordSet" in data:
            _historyRecordSet_key = "historyRecordSet"
        elif "HistoryRecordSet" in data:
            _historyRecordSet_key = "HistoryRecordSet"
        elif "HistoryRecords" in data:
            _historyRecordSet_key = "HistoryRecords"
        if _historyRecordSet_key:
            param_data = data[_historyRecordSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<historyRecordSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</historyRecordSet>')
            else:
                xml_parts.append(f'{indent_str}<historyRecordSet/>')
        # Serialize lastEvaluatedTime
        _lastEvaluatedTime_key = None
        if "lastEvaluatedTime" in data:
            _lastEvaluatedTime_key = "lastEvaluatedTime"
        elif "LastEvaluatedTime" in data:
            _lastEvaluatedTime_key = "LastEvaluatedTime"
        if _lastEvaluatedTime_key:
            param_data = data[_lastEvaluatedTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<lastEvaluatedTime>{esc(str(param_data))}</lastEvaluatedTime>')
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
        # Serialize startTime
        _startTime_key = None
        if "startTime" in data:
            _startTime_key = "startTime"
        elif "StartTime" in data:
            _startTime_key = "StartTime"
        if _startTime_key:
            param_data = data[_startTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<startTime>{esc(str(param_data))}</startTime>')
        xml_parts.append(f'</DescribeFleetHistoryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_fleet_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeFleetInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize activeInstanceSet
        _activeInstanceSet_key = None
        if "activeInstanceSet" in data:
            _activeInstanceSet_key = "activeInstanceSet"
        elif "ActiveInstanceSet" in data:
            _activeInstanceSet_key = "ActiveInstanceSet"
        elif "ActiveInstances" in data:
            _activeInstanceSet_key = "ActiveInstances"
        if _activeInstanceSet_key:
            param_data = data[_activeInstanceSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<activeInstanceSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</activeInstanceSet>')
            else:
                xml_parts.append(f'{indent_str}<activeInstanceSet/>')
        # Serialize fleetId
        _fleetId_key = None
        if "fleetId" in data:
            _fleetId_key = "fleetId"
        elif "FleetId" in data:
            _fleetId_key = "FleetId"
        if _fleetId_key:
            param_data = data[_fleetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<fleetId>{esc(str(param_data))}</fleetId>')
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
        xml_parts.append(f'</DescribeFleetInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_fleets_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeFleetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize fleetSet
        _fleetSet_key = None
        if "fleetSet" in data:
            _fleetSet_key = "fleetSet"
        elif "FleetSet" in data:
            _fleetSet_key = "FleetSet"
        elif "Fleets" in data:
            _fleetSet_key = "Fleets"
        if _fleetSet_key:
            param_data = data[_fleetSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<fleetSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(ec2fleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</fleetSet>')
            else:
                xml_parts.append(f'{indent_str}<fleetSet/>')
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
        xml_parts.append(f'</DescribeFleetsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_fleet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyFleetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifyFleetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateFleet": ec2fleet_ResponseSerializer.serialize_create_fleet_response,
            "DeleteFleets": ec2fleet_ResponseSerializer.serialize_delete_fleets_response,
            "DescribeFleetHistory": ec2fleet_ResponseSerializer.serialize_describe_fleet_history_response,
            "DescribeFleetInstances": ec2fleet_ResponseSerializer.serialize_describe_fleet_instances_response,
            "DescribeFleets": ec2fleet_ResponseSerializer.serialize_describe_fleets_response,
            "ModifyFleet": ec2fleet_ResponseSerializer.serialize_modify_fleet_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

