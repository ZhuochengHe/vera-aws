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
class SpotFleet:
    activity_status: str = ""
    create_time: str = ""
    spot_fleet_request_config: Dict[str, Any] = field(default_factory=dict)
    spot_fleet_request_id: str = ""
    spot_fleet_request_state: str = ""
    tag_set: List[Any] = field(default_factory=list)

    instances: List[Dict[str, Any]] = field(default_factory=list)
    history_records: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activityStatus": self.activity_status,
            "createTime": self.create_time,
            "spotFleetRequestConfig": self.spot_fleet_request_config,
            "spotFleetRequestId": self.spot_fleet_request_id,
            "spotFleetRequestState": self.spot_fleet_request_state,
            "tagSet": self.tag_set,
        }

class SpotFleet_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.spot_fleet  # alias to shared store

    def _get_spot_fleet_or_error(self, spot_fleet_request_id: str):
        spot_fleet = self.resources.get(spot_fleet_request_id)
        if not spot_fleet:
            return None, create_error_response(
                "InvalidSpotFleetRequestId.NotFound",
                f"The Spot Fleet request ID '{spot_fleet_request_id}' does not exist",
            )
        return spot_fleet, None

    def _record_history(self, spot_fleet: SpotFleet, event_type: str, information: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        spot_fleet.history_records.append(
            {
                "eventInformation": information,
                "eventType": event_type,
                "timestamp": timestamp,
            }
        )

    def CancelSpotFleetRequests(self, params: Dict[str, Any]):
        """Cancels the specified Spot Fleet requests. After you cancel a Spot Fleet request, the Spot Fleet launches no new instances. You must also specify whether a canceled Spot Fleet request should terminate its instances. If you
            choose to terminate the instances, the Spot Fleet request enters """

        request_ids = params.get("SpotFleetRequestId.N", []) or []
        if not request_ids:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: SpotFleetRequestId.N",
            )
        terminate_instances = params.get("TerminateInstances")
        if terminate_instances is None:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: TerminateInstances",
            )

        for request_id in request_ids:
            if request_id not in self.resources:
                return create_error_response(
                    "InvalidSpotFleetRequestId.NotFound",
                    f"The Spot Fleet request ID '{request_id}' does not exist",
                )

        successful = []
        for request_id in request_ids:
            spot_fleet = self.resources[request_id]
            previous_state = spot_fleet.spot_fleet_request_state
            spot_fleet.spot_fleet_request_state = "cancelled"
            spot_fleet.activity_status = "cancelled"
            if terminate_instances:
                spot_fleet.instances = []
                self._record_history(
                    spot_fleet,
                    "information",
                    "Spot Fleet request cancelled and instances terminated",
                )
            else:
                self._record_history(
                    spot_fleet,
                    "information",
                    "Spot Fleet request cancelled",
                )
            successful.append(
                {
                    "currentSpotFleetRequestState": spot_fleet.spot_fleet_request_state,
                    "previousSpotFleetRequestState": previous_state,
                    "spotFleetRequestId": request_id,
                }
            )

        return {
            'successfulFleetRequestSet': successful,
            'unsuccessfulFleetRequestSet': [],
            }

    def DescribeSpotFleetInstances(self, params: Dict[str, Any]):
        """Describes the running instances for the specified Spot Fleet."""

        spot_fleet_request_id = params.get("SpotFleetRequestId")
        if not spot_fleet_request_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: SpotFleetRequestId",
            )

        spot_fleet, error = self._get_spot_fleet_or_error(spot_fleet_request_id)
        if error:
            return error

        instances = spot_fleet.instances or []
        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token) if next_token else 0
        except (TypeError, ValueError):
            start_index = 0
        if start_index < 0:
            start_index = 0
        end_index = start_index + max_results
        page = instances[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(instances) else None

        return {
            'activeInstanceSet': page,
            'nextToken': new_next_token,
            'spotFleetRequestId': spot_fleet_request_id,
            }

    def DescribeSpotFleetRequestHistory(self, params: Dict[str, Any]):
        """Describes the events for the specified Spot Fleet request during the specified
            time. Spot Fleet events are delayed by up to 30 seconds before they can be described. This
            ensures that you can query by the last evaluated time and not miss a recorded event.
            Spot Flee"""

        spot_fleet_request_id = params.get("SpotFleetRequestId")
        if not spot_fleet_request_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: SpotFleetRequestId",
            )
        start_time = params.get("StartTime")
        if not start_time:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: StartTime",
            )

        spot_fleet, error = self._get_spot_fleet_or_error(spot_fleet_request_id)
        if error:
            return error

        event_type = params.get("EventType")
        history = spot_fleet.history_records or []
        try:
            start_dt = datetime.fromisoformat(str(start_time).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            start_dt = None

        filtered = []
        for record in history:
            if event_type and record.get("eventType") != event_type:
                continue
            if start_dt is None:
                filtered.append(record)
                continue
            record_time = record.get("timestamp")
            try:
                record_dt = datetime.fromisoformat(str(record_time).replace("Z", "+00:00"))
            except (TypeError, ValueError):
                record_dt = None
            if record_dt and record_dt < start_dt:
                continue
            filtered.append(record)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token) if next_token else 0
        except (TypeError, ValueError):
            start_index = 0
        if start_index < 0:
            start_index = 0
        end_index = start_index + max_results
        page = filtered[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(filtered) else None
        last_evaluated_time = page[-1]["timestamp"] if page else start_time

        return {
            'historyRecordSet': page,
            'lastEvaluatedTime': last_evaluated_time,
            'nextToken': new_next_token,
            'spotFleetRequestId': spot_fleet_request_id,
            'startTime': start_time,
            }

    def DescribeSpotFleetRequests(self, params: Dict[str, Any]):
        """Describes your Spot Fleet requests. Spot Fleet requests are deleted 48 hours after they are canceled and their instances
            are terminated."""

        request_ids = params.get("SpotFleetRequestId.N", []) or []
        if request_ids:
            for request_id in request_ids:
                if request_id not in self.resources:
                    return create_error_response(
                        "InvalidSpotFleetRequestId.NotFound",
                        f"The ID '{request_id}' does not exist",
                    )
            resources = [self.resources[request_id] for request_id in request_ids]
        else:
            resources = list(self.resources.values())

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        try:
            start_index = int(next_token) if next_token else 0
        except (TypeError, ValueError):
            start_index = 0
        if start_index < 0:
            start_index = 0
        end_index = start_index + max_results
        page = resources[start_index:end_index]
        new_next_token = str(end_index) if end_index < len(resources) else None

        return {
            'nextToken': new_next_token,
            'spotFleetRequestConfigSet': [resource.to_dict() for resource in page],
            }

    def ModifySpotFleetRequest(self, params: Dict[str, Any]):
        """Modifies the specified Spot Fleet request. You can only modify a Spot Fleet request of typemaintain. While the Spot Fleet request is being modified, it is in themodifyingstate."""

        spot_fleet_request_id = params.get("SpotFleetRequestId")
        if not spot_fleet_request_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: SpotFleetRequestId",
            )

        spot_fleet, error = self._get_spot_fleet_or_error(spot_fleet_request_id)
        if error:
            return error

        config = spot_fleet.spot_fleet_request_config or {}
        if params.get("Context") is not None:
            config["Context"] = params.get("Context")
        if params.get("ExcessCapacityTerminationPolicy") is not None:
            config["ExcessCapacityTerminationPolicy"] = params.get("ExcessCapacityTerminationPolicy")
        if params.get("OnDemandTargetCapacity") is not None:
            config["OnDemandTargetCapacity"] = params.get("OnDemandTargetCapacity")
        if params.get("TargetCapacity") is not None:
            config["TargetCapacity"] = params.get("TargetCapacity")
        launch_template_configs = params.get("LaunchTemplateConfig.N")
        if launch_template_configs:
            config["LaunchTemplateConfigs"] = launch_template_configs
        spot_fleet.spot_fleet_request_config = config
        spot_fleet.spot_fleet_request_state = "modifying"
        self._record_history(spot_fleet, "information", "Spot Fleet request modified")

        return {
            'return': True,
            }

    def RequestSpotFleet(self, params: Dict[str, Any]):
        """Creates a Spot Fleet request. The Spot Fleet request specifies the total target capacity and the On-Demand target
            capacity. Amazon EC2 calculates the difference between the total capacity and On-Demand
            capacity, and launches the difference as Spot capacity. You can submit a s"""

        spot_fleet_request_config = params.get("SpotFleetRequestConfig")
        if not spot_fleet_request_config:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: SpotFleetRequestConfig",
            )

        spot_fleet_request_id = self._generate_id("spot")
        create_time = datetime.now(timezone.utc).isoformat()
        tag_set = spot_fleet_request_config.get("TagSpecifications")
        if tag_set is None:
            tag_set = spot_fleet_request_config.get("TagSpecification") or []

        spot_fleet = SpotFleet(
            activity_status="fulfilled",
            create_time=create_time,
            spot_fleet_request_config=spot_fleet_request_config,
            spot_fleet_request_id=spot_fleet_request_id,
            spot_fleet_request_state="active",
            tag_set=tag_set,
        )
        self.resources[spot_fleet_request_id] = spot_fleet
        self._record_history(spot_fleet, "information", "Spot Fleet request created")

        return {
            'spotFleetRequestId': spot_fleet_request_id,
            }

    def _generate_id(self, prefix: str = 'spot') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class spotfleet_RequestParser:
    @staticmethod
    def parse_cancel_spot_fleet_requests_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SpotFleetRequestId.N": get_indexed_list(md, "SpotFleetRequestId"),
            "TerminateInstances": get_scalar(md, "TerminateInstances"),
        }

    @staticmethod
    def parse_describe_spot_fleet_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "SpotFleetRequestId": get_scalar(md, "SpotFleetRequestId"),
        }

    @staticmethod
    def parse_describe_spot_fleet_request_history_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EventType": get_scalar(md, "EventType"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "SpotFleetRequestId": get_scalar(md, "SpotFleetRequestId"),
            "StartTime": get_scalar(md, "StartTime"),
        }

    @staticmethod
    def parse_describe_spot_fleet_requests_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "SpotFleetRequestId.N": get_indexed_list(md, "SpotFleetRequestId"),
        }

    @staticmethod
    def parse_modify_spot_fleet_request_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Context": get_scalar(md, "Context"),
            "ExcessCapacityTerminationPolicy": get_scalar(md, "ExcessCapacityTerminationPolicy"),
            "LaunchTemplateConfig.N": get_indexed_list(md, "LaunchTemplateConfig"),
            "OnDemandTargetCapacity": get_int(md, "OnDemandTargetCapacity"),
            "SpotFleetRequestId": get_scalar(md, "SpotFleetRequestId"),
            "TargetCapacity": get_int(md, "TargetCapacity"),
        }

    @staticmethod
    def parse_request_spot_fleet_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SpotFleetRequestConfig": get_scalar(md, "SpotFleetRequestConfig"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CancelSpotFleetRequests": spotfleet_RequestParser.parse_cancel_spot_fleet_requests_request,
            "DescribeSpotFleetInstances": spotfleet_RequestParser.parse_describe_spot_fleet_instances_request,
            "DescribeSpotFleetRequestHistory": spotfleet_RequestParser.parse_describe_spot_fleet_request_history_request,
            "DescribeSpotFleetRequests": spotfleet_RequestParser.parse_describe_spot_fleet_requests_request,
            "ModifySpotFleetRequest": spotfleet_RequestParser.parse_modify_spot_fleet_request_request,
            "RequestSpotFleet": spotfleet_RequestParser.parse_request_spot_fleet_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class spotfleet_ResponseSerializer:
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
                xml_parts.extend(spotfleet_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(spotfleet_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(spotfleet_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(spotfleet_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(spotfleet_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(spotfleet_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_cancel_spot_fleet_requests_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelSpotFleetRequestsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize successfulFleetRequestSet
        _successfulFleetRequestSet_key = None
        if "successfulFleetRequestSet" in data:
            _successfulFleetRequestSet_key = "successfulFleetRequestSet"
        elif "SuccessfulFleetRequestSet" in data:
            _successfulFleetRequestSet_key = "SuccessfulFleetRequestSet"
        elif "SuccessfulFleetRequests" in data:
            _successfulFleetRequestSet_key = "SuccessfulFleetRequests"
        if _successfulFleetRequestSet_key:
            param_data = data[_successfulFleetRequestSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulFleetRequestSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotfleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</successfulFleetRequestSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulFleetRequestSet/>')
        # Serialize unsuccessfulFleetRequestSet
        _unsuccessfulFleetRequestSet_key = None
        if "unsuccessfulFleetRequestSet" in data:
            _unsuccessfulFleetRequestSet_key = "unsuccessfulFleetRequestSet"
        elif "UnsuccessfulFleetRequestSet" in data:
            _unsuccessfulFleetRequestSet_key = "UnsuccessfulFleetRequestSet"
        elif "UnsuccessfulFleetRequests" in data:
            _unsuccessfulFleetRequestSet_key = "UnsuccessfulFleetRequests"
        if _unsuccessfulFleetRequestSet_key:
            param_data = data[_unsuccessfulFleetRequestSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulFleetRequestSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotfleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulFleetRequestSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulFleetRequestSet/>')
        xml_parts.append(f'</CancelSpotFleetRequestsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_spot_fleet_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeSpotFleetInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
                    xml_parts.extend(spotfleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</activeInstanceSet>')
            else:
                xml_parts.append(f'{indent_str}<activeInstanceSet/>')
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
        # Serialize spotFleetRequestId
        _spotFleetRequestId_key = None
        if "spotFleetRequestId" in data:
            _spotFleetRequestId_key = "spotFleetRequestId"
        elif "SpotFleetRequestId" in data:
            _spotFleetRequestId_key = "SpotFleetRequestId"
        if _spotFleetRequestId_key:
            param_data = data[_spotFleetRequestId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<spotFleetRequestId>{esc(str(param_data))}</spotFleetRequestId>')
        xml_parts.append(f'</DescribeSpotFleetInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_spot_fleet_request_history_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeSpotFleetRequestHistoryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
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
                    xml_parts.extend(spotfleet_ResponseSerializer._serialize_nested_fields(item, 2))
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
        # Serialize spotFleetRequestId
        _spotFleetRequestId_key = None
        if "spotFleetRequestId" in data:
            _spotFleetRequestId_key = "spotFleetRequestId"
        elif "SpotFleetRequestId" in data:
            _spotFleetRequestId_key = "SpotFleetRequestId"
        if _spotFleetRequestId_key:
            param_data = data[_spotFleetRequestId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<spotFleetRequestId>{esc(str(param_data))}</spotFleetRequestId>')
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
        xml_parts.append(f'</DescribeSpotFleetRequestHistoryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_spot_fleet_requests_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeSpotFleetRequestsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize spotFleetRequestConfigSet
        _spotFleetRequestConfigSet_key = None
        if "spotFleetRequestConfigSet" in data:
            _spotFleetRequestConfigSet_key = "spotFleetRequestConfigSet"
        elif "SpotFleetRequestConfigSet" in data:
            _spotFleetRequestConfigSet_key = "SpotFleetRequestConfigSet"
        elif "SpotFleetRequestConfigs" in data:
            _spotFleetRequestConfigSet_key = "SpotFleetRequestConfigs"
        if _spotFleetRequestConfigSet_key:
            param_data = data[_spotFleetRequestConfigSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<spotFleetRequestConfigSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotfleet_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</spotFleetRequestConfigSet>')
            else:
                xml_parts.append(f'{indent_str}<spotFleetRequestConfigSet/>')
        xml_parts.append(f'</DescribeSpotFleetRequestsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_spot_fleet_request_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifySpotFleetRequestResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</ModifySpotFleetRequestResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_request_spot_fleet_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RequestSpotFleetResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize spotFleetRequestId
        _spotFleetRequestId_key = None
        if "spotFleetRequestId" in data:
            _spotFleetRequestId_key = "spotFleetRequestId"
        elif "SpotFleetRequestId" in data:
            _spotFleetRequestId_key = "SpotFleetRequestId"
        if _spotFleetRequestId_key:
            param_data = data[_spotFleetRequestId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<spotFleetRequestId>{esc(str(param_data))}</spotFleetRequestId>')
        xml_parts.append(f'</RequestSpotFleetResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CancelSpotFleetRequests": spotfleet_ResponseSerializer.serialize_cancel_spot_fleet_requests_response,
            "DescribeSpotFleetInstances": spotfleet_ResponseSerializer.serialize_describe_spot_fleet_instances_response,
            "DescribeSpotFleetRequestHistory": spotfleet_ResponseSerializer.serialize_describe_spot_fleet_request_history_response,
            "DescribeSpotFleetRequests": spotfleet_ResponseSerializer.serialize_describe_spot_fleet_requests_response,
            "ModifySpotFleetRequest": spotfleet_ResponseSerializer.serialize_modify_spot_fleet_request_response,
            "RequestSpotFleet": spotfleet_ResponseSerializer.serialize_request_spot_fleet_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

