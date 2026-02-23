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
class VpcFlowLog:
    creation_time: str = ""
    deliver_cross_account_role: str = ""
    deliver_logs_error_message: str = ""
    deliver_logs_permission_arn: str = ""
    deliver_logs_status: str = ""
    destination_options: Dict[str, Any] = field(default_factory=dict)
    flow_log_id: str = ""
    flow_log_status: str = ""
    log_destination: str = ""
    log_destination_type: str = ""
    log_format: str = ""
    log_group_name: str = ""
    max_aggregation_interval: int = 0
    resource_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    traffic_type: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "creationTime": self.creation_time,
            "deliverCrossAccountRole": self.deliver_cross_account_role,
            "deliverLogsErrorMessage": self.deliver_logs_error_message,
            "deliverLogsPermissionArn": self.deliver_logs_permission_arn,
            "deliverLogsStatus": self.deliver_logs_status,
            "destinationOptions": self.destination_options,
            "flowLogId": self.flow_log_id,
            "flowLogStatus": self.flow_log_status,
            "logDestination": self.log_destination,
            "logDestinationType": self.log_destination_type,
            "logFormat": self.log_format,
            "logGroupName": self.log_group_name,
            "maxAggregationInterval": self.max_aggregation_interval,
            "resourceId": self.resource_id,
            "tagSet": self.tag_set,
            "trafficType": self.traffic_type,
        }

class VpcFlowLog_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.vpc_flow_logs  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.tags.get(params['resource_id']).vpc_flow_log_ids.append(new_id)
    #   Delete: self.state.tags.get(resource.resource_id).vpc_flow_log_ids.remove(resource_id)

    def _register_with_parent(self, flow_log_id: str, resource_id: str) -> None:
        parent = self.state.tags.get(resource_id)
        if parent and hasattr(parent, "vpc_flow_log_ids"):
            if flow_log_id not in parent.vpc_flow_log_ids:
                parent.vpc_flow_log_ids.append(flow_log_id)

    def _deregister_with_parent(self, flow_log_id: str, resource_id: str) -> None:
        parent = self.state.tags.get(resource_id)
        if parent and hasattr(parent, "vpc_flow_log_ids") and flow_log_id in parent.vpc_flow_log_ids:
            parent.vpc_flow_log_ids.remove(flow_log_id)

    def CreateFlowLogs(self, params: Dict[str, Any]):
        """Creates one or more flow logs to capture information about IP traffic for a specific network interface,
            subnet, or VPC. Flow log data for a monitored network interface is recorded as flow log records, which are log events 
            consisting of fields that describe the traffic flow. """

        resource_ids = params.get("ResourceId.N", []) or []
        if not resource_ids:
            return create_error_response("MissingParameter", "Missing required parameter: ResourceId")
        for resource_id in resource_ids:
            if not resource_id:
                return create_error_response("MissingParameter", "Missing required parameter: ResourceId")

        resource_type = params.get("ResourceType")
        if not resource_type:
            return create_error_response("MissingParameter", "Missing required parameter: ResourceType")

        normalized_type = resource_type.replace("-", "").replace("_", "").lower()
        if normalized_type == "vpc":
            store = self.state.vpcs
            error_code = "InvalidVpcID.NotFound"
            label = "VPC"
        elif normalized_type == "subnet":
            store = self.state.subnets
            error_code = "InvalidSubnetID.NotFound"
            label = "Subnet"
        elif normalized_type == "networkinterface":
            store = self.state.elastic_network_interfaces
            error_code = "InvalidNetworkInterfaceID.NotFound"
            label = "Network interface"
        else:
            return create_error_response("InvalidParameterValue", f"Invalid resource type: {resource_type}")

        for resource_id in resource_ids:
            if not store.get(resource_id):
                return create_error_response(error_code, f"{label} '{resource_id}' does not exist.")

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags") or spec.get("Tag") or [])

        creation_time = datetime.now(timezone.utc).isoformat()
        flow_log_ids: List[str] = []
        for resource_id in resource_ids:
            flow_log_id = self._generate_id("fl")
            resource = VpcFlowLog(
                creation_time=creation_time,
                deliver_cross_account_role=params.get("DeliverCrossAccountRole") or "",
                deliver_logs_error_message="",
                deliver_logs_permission_arn=params.get("DeliverLogsPermissionArn") or "",
                deliver_logs_status="SUCCESS",
                destination_options=params.get("DestinationOptions") or {},
                flow_log_id=flow_log_id,
                flow_log_status="ACTIVE",
                log_destination=params.get("LogDestination") or "",
                log_destination_type=params.get("LogDestinationType") or "",
                log_format=params.get("LogFormat") or "",
                log_group_name=params.get("LogGroupName") or "",
                max_aggregation_interval=int(params.get("MaxAggregationInterval") or 0),
                resource_id=resource_id,
                tag_set=list(tag_set),
                traffic_type=params.get("TrafficType") or "",
            )
            self.resources[flow_log_id] = resource
            self._register_with_parent(flow_log_id, resource_id)
            flow_log_ids.append(flow_log_id)

        return {
            'clientToken': params.get("ClientToken") or "",
            'flowLogIdSet': flow_log_ids,
            'unsuccessful': [],
            }

    def DeleteFlowLogs(self, params: Dict[str, Any]):
        """Deletes one or more flow logs."""

        flow_log_ids = params.get("FlowLogId.N", []) or []
        if not flow_log_ids:
            return create_error_response("MissingParameter", "Missing required parameter: FlowLogId")
        for flow_log_id in flow_log_ids:
            if not flow_log_id:
                return create_error_response("MissingParameter", "Missing required parameter: FlowLogId")

        for flow_log_id in flow_log_ids:
            resource = self.resources.get(flow_log_id)
            if not resource:
                return create_error_response(
                    "InvalidFlowLogId.NotFound",
                    f"The ID '{flow_log_id}' does not exist",
                )

        for flow_log_id in flow_log_ids:
            resource = self.resources.get(flow_log_id)
            if resource:
                self._deregister_with_parent(flow_log_id, resource.resource_id)
                del self.resources[flow_log_id]

        return {
            'unsuccessful': [],
            }

    def DescribeFlowLogs(self, params: Dict[str, Any]):
        """Describes one or more flow logs. To view the published flow log records, you must view the log destination. For example, 
            the CloudWatch Logs log group, the Amazon S3 bucket, or the Kinesis Data Firehose delivery stream."""

        flow_log_ids = params.get("FlowLogId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if flow_log_ids:
            resources: List[VpcFlowLog] = []
            for flow_log_id in flow_log_ids:
                resource = self.resources.get(flow_log_id)
                if not resource:
                    return create_error_response(
                        "InvalidFlowLogId.NotFound",
                        f"The ID '{flow_log_id}' does not exist",
                    )
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        flow_logs = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'flowLogSet': flow_logs,
            'nextToken': None,
            }

    def GetFlowLogsIntegrationTemplate(self, params: Dict[str, Any]):
        """Generates a CloudFormation template that streamlines and automates the integration of VPC flow logs 
            with Amazon Athena. This make it easier for you to query and gain insights from VPC flow logs data. 
            Based on the information that you provide, we configure resources in the t"""

        config_destination = params.get("ConfigDeliveryS3DestinationArn")
        if not config_destination:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: ConfigDeliveryS3DestinationArn",
            )

        flow_log_id = params.get("FlowLogId")
        if not flow_log_id:
            return create_error_response("MissingParameter", "Missing required parameter: FlowLogId")

        integrate_service = params.get("IntegrateService")
        if not integrate_service:
            return create_error_response("MissingParameter", "Missing required parameter: IntegrateService")

        resource = self.resources.get(flow_log_id)
        if not resource:
            return create_error_response(
                "InvalidFlowLogId.NotFound",
                f"The ID '{flow_log_id}' does not exist",
            )

        template = (
            f"Integration template for {flow_log_id} with {integrate_service} "
            f"to {config_destination}"
        )

        return {
            'result': template,
            }

    def _generate_id(self, prefix: str = 'flow') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class vpcflowlog_RequestParser:
    @staticmethod
    def parse_create_flow_logs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DeliverCrossAccountRole": get_scalar(md, "DeliverCrossAccountRole"),
            "DeliverLogsPermissionArn": get_scalar(md, "DeliverLogsPermissionArn"),
            "DestinationOptions": get_scalar(md, "DestinationOptions"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LogDestination": get_scalar(md, "LogDestination"),
            "LogDestinationType": get_scalar(md, "LogDestinationType"),
            "LogFormat": get_scalar(md, "LogFormat"),
            "LogGroupName": get_scalar(md, "LogGroupName"),
            "MaxAggregationInterval": get_int(md, "MaxAggregationInterval"),
            "ResourceId.N": get_indexed_list(md, "ResourceId"),
            "ResourceType": get_scalar(md, "ResourceType"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TrafficType": get_scalar(md, "TrafficType"),
        }

    @staticmethod
    def parse_delete_flow_logs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FlowLogId.N": get_indexed_list(md, "FlowLogId"),
        }

    @staticmethod
    def parse_describe_flow_logs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "FlowLogId.N": get_indexed_list(md, "FlowLogId"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_flow_logs_integration_template_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ConfigDeliveryS3DestinationArn": get_scalar(md, "ConfigDeliveryS3DestinationArn"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FlowLogId": get_scalar(md, "FlowLogId"),
            "IntegrateService": get_int(md, "IntegrateService"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateFlowLogs": vpcflowlog_RequestParser.parse_create_flow_logs_request,
            "DeleteFlowLogs": vpcflowlog_RequestParser.parse_delete_flow_logs_request,
            "DescribeFlowLogs": vpcflowlog_RequestParser.parse_describe_flow_logs_request,
            "GetFlowLogsIntegrationTemplate": vpcflowlog_RequestParser.parse_get_flow_logs_integration_template_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class vpcflowlog_ResponseSerializer:
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
                xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_flow_logs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateFlowLogsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize clientToken
        _clientToken_key = None
        if "clientToken" in data:
            _clientToken_key = "clientToken"
        elif "ClientToken" in data:
            _clientToken_key = "ClientToken"
        if _clientToken_key:
            param_data = data[_clientToken_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<clientToken>{esc(str(param_data))}</clientToken>')
        # Serialize flowLogIdSet
        _flowLogIdSet_key = None
        if "flowLogIdSet" in data:
            _flowLogIdSet_key = "flowLogIdSet"
        elif "FlowLogIdSet" in data:
            _flowLogIdSet_key = "FlowLogIdSet"
        elif "FlowLogIds" in data:
            _flowLogIdSet_key = "FlowLogIds"
        if _flowLogIdSet_key:
            param_data = data[_flowLogIdSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<flowLogIdSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</flowLogIdSet>')
            else:
                xml_parts.append(f'{indent_str}<flowLogIdSet/>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</CreateFlowLogsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_flow_logs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteFlowLogsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize unsuccessful
        _unsuccessful_key = None
        if "unsuccessful" in data:
            _unsuccessful_key = "unsuccessful"
        elif "Unsuccessful" in data:
            _unsuccessful_key = "Unsuccessful"
        if _unsuccessful_key:
            param_data = data[_unsuccessful_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<unsuccessfulSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</unsuccessfulSet>')
            else:
                xml_parts.append(f'{indent_str}<unsuccessfulSet/>')
        xml_parts.append(f'</DeleteFlowLogsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_flow_logs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeFlowLogsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize flowLogSet
        _flowLogSet_key = None
        if "flowLogSet" in data:
            _flowLogSet_key = "flowLogSet"
        elif "FlowLogSet" in data:
            _flowLogSet_key = "FlowLogSet"
        elif "FlowLogs" in data:
            _flowLogSet_key = "FlowLogs"
        if _flowLogSet_key:
            param_data = data[_flowLogSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<flowLogSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(vpcflowlog_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</flowLogSet>')
            else:
                xml_parts.append(f'{indent_str}<flowLogSet/>')
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
        xml_parts.append(f'</DescribeFlowLogsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_flow_logs_integration_template_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetFlowLogsIntegrationTemplateResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize result
        _result_key = None
        if "result" in data:
            _result_key = "result"
        elif "Result" in data:
            _result_key = "Result"
        if _result_key:
            param_data = data[_result_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<result>{esc(str(param_data))}</result>')
        xml_parts.append(f'</GetFlowLogsIntegrationTemplateResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateFlowLogs": vpcflowlog_ResponseSerializer.serialize_create_flow_logs_response,
            "DeleteFlowLogs": vpcflowlog_ResponseSerializer.serialize_delete_flow_logs_response,
            "DescribeFlowLogs": vpcflowlog_ResponseSerializer.serialize_describe_flow_logs_response,
            "GetFlowLogsIntegrationTemplate": vpcflowlog_ResponseSerializer.serialize_get_flow_logs_integration_template_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

