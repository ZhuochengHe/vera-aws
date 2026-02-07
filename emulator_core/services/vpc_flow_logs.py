from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


class FlowLogStatus(Enum):
    ACTIVE = "ACTIVE"


class DeliverLogsStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TrafficType(Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    ALL = "ALL"


class LogDestinationType(Enum):
    CLOUD_WATCH_LOGS = "cloud-watch-logs"
    S3 = "s3"
    KINESIS_DATA_FIREHOSE = "kinesis-data-firehose"


class ResourceType(Enum):
    VPC = "VPC"
    SUBNET = "Subnet"
    NETWORK_INTERFACE = "NetworkInterface"
    TRANSIT_GATEWAY = "TransitGateway"
    TRANSIT_GATEWAY_ATTACHMENT = "TransitGatewayAttachment"
    REGIONAL_NAT_GATEWAY = "RegionalNatGateway"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class DestinationOptions:
    FileFormat: Optional[str] = None  # plain-text | parquet
    HiveCompatiblePartitions: Optional[bool] = None
    PerHourPartition: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.FileFormat is not None:
            d["fileFormat"] = self.FileFormat
        if self.HiveCompatiblePartitions is not None:
            d["hiveCompatiblePartitions"] = self.HiveCompatiblePartitions
        if self.PerHourPartition is not None:
            d["perHourPartition"] = self.PerHourPartition
        return d


@dataclass
class FlowLog:
    flow_log_id: str
    creation_time: datetime
    deliver_cross_account_role: Optional[str]
    deliver_logs_error_message: Optional[str]
    deliver_logs_permission_arn: Optional[str]
    deliver_logs_status: Optional[DeliverLogsStatus]
    destination_options: Optional[DestinationOptions]
    flow_log_status: FlowLogStatus
    log_destination: Optional[str]
    log_destination_type: Optional[LogDestinationType]
    log_format: Optional[str]
    log_group_name: Optional[str]
    max_aggregation_interval: int
    resource_id: str
    resource_type: ResourceType
    tag_set: List[Tag]
    traffic_type: Optional[TrafficType]

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "flowLogId": self.flow_log_id,
            "creationTime": self.creation_time.isoformat() + "Z",
            "flowLogStatus": self.flow_log_status.value,
            "resourceId": self.resource_id,
            "resourceType": self.resource_type.value,
            "maxAggregationInterval": self.max_aggregation_interval,
            "tagSet": [tag.to_dict() for tag in self.tag_set],
        }
        if self.deliver_cross_account_role is not None:
            d["deliverCrossAccountRole"] = self.deliver_cross_account_role
        if self.deliver_logs_error_message is not None:
            d["deliverLogsErrorMessage"] = self.deliver_logs_error_message
        if self.deliver_logs_permission_arn is not None:
            d["deliverLogsPermissionArn"] = self.deliver_logs_permission_arn
        if self.deliver_logs_status is not None:
            d["deliverLogsStatus"] = self.deliver_logs_status.value
        if self.destination_options is not None:
            d["destinationOptions"] = self.destination_options.to_dict()
        if self.log_destination is not None:
            d["logDestination"] = self.log_destination
        if self.log_destination_type is not None:
            d["logDestinationType"] = self.log_destination_type.value
        if self.log_format is not None:
            d["logFormat"] = self.log_format
        if self.log_group_name is not None:
            d["logGroupName"] = self.log_group_name
        if self.traffic_type is not None:
            d["trafficType"] = self.traffic_type.value
        return d


class VpcFlowLogsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.vpc_flow_logs dict for storage

    def _validate_tags(self, tag_specifications: List[Dict[str, Any]]) -> List[Tag]:
        tags: List[Tag] = []
        for tag_spec in tag_specifications:
            # Validate ResourceType in tag_spec if present
            if "ResourceType" in tag_spec:
                # Accept any string, no strict validation here as AWS allows many resource types
                if not isinstance(tag_spec["ResourceType"], str):
                    raise ErrorCode("InvalidParameterValue", "TagSpecification.ResourceType must be a string")
            if "Tags" in tag_spec:
                if not isinstance(tag_spec["Tags"], list):
                    raise ErrorCode("InvalidParameterValue", "Tags must be a list")
                for tag in tag_spec["Tags"]:
                    if not isinstance(tag, dict):
                        raise ErrorCode("InvalidParameterValue", "Each tag must be a dict")
                    key = tag.get("Key")
                    value = tag.get("Value")
                    if key is None or not isinstance(key, str):
                        raise ErrorCode("InvalidParameterValue", "Tag Key must be a string")
                    if key.lower().startswith("aws:"):
                        raise ErrorCode("InvalidParameterValue", "Tag Key may not begin with aws:")
                    if len(key) > 127:
                        raise ErrorCode("InvalidParameterValue", "Tag Key length must be <= 127")
                    if value is not None and not isinstance(value, str):
                        raise ErrorCode("InvalidParameterValue", "Tag Value must be a string")
                    if value is not None and len(value) > 256:
                        raise ErrorCode("InvalidParameterValue", "Tag Value length must be <= 256")
                    tags.append(Tag(Key=key, Value=value if value is not None else ""))
        return tags

    def _validate_resource_type(self, resource_type: str) -> ResourceType:
        try:
            return ResourceType(resource_type)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid ResourceType: {resource_type}")

    def _validate_traffic_type(self, traffic_type: Optional[str], resource_type: ResourceType) -> Optional[TrafficType]:
        if resource_type == ResourceType.TRANSIT_GATEWAY or resource_type == ResourceType.TRANSIT_GATEWAY_ATTACHMENT:
            # TrafficType is not supported for transit gateway resource types
            if traffic_type is not None:
                raise ErrorCode("InvalidParameterCombination", "TrafficType is not supported for transit gateway resource types")
            return None
        else:
            if traffic_type is None:
                raise ErrorCode("MissingParameter", "TrafficType is required for resource types other than transit gateway")
            try:
                return TrafficType(traffic_type)
            except ValueError:
                raise ErrorCode("InvalidParameterValue", f"Invalid TrafficType: {traffic_type}")

    def _validate_log_destination_type(self, log_destination_type: Optional[str]) -> LogDestinationType:
        if log_destination_type is None:
            return LogDestinationType.CLOUD_WATCH_LOGS  # default
        try:
            return LogDestinationType(log_destination_type)
        except ValueError:
            raise ErrorCode("InvalidParameterValue", f"Invalid LogDestinationType: {log_destination_type}")

    def _validate_max_aggregation_interval(self, interval: Optional[int], resource_type: ResourceType) -> int:
        if interval is None:
            return 600  # default
        if interval not in (60, 600):
            raise ErrorCode("InvalidParameterValue", "MaxAggregationInterval must be 60 or 600")
        if resource_type == ResourceType.TRANSIT_GATEWAY and interval != 60:
            raise ErrorCode("InvalidParameterValue", "MaxAggregationInterval must be 60 for transit gateway resource types")
        return interval

    def _validate_resource_ids(self, resource_ids: List[str], resource_type: ResourceType):
        if not resource_ids:
            raise ErrorCode("MissingParameter", "ResourceId.N is required and must have at least one ID")
        if not all(isinstance(rid, str) for rid in resource_ids):
            raise ErrorCode("InvalidParameterValue", "All ResourceId.N values must be strings")
        max_allowed = 25 if resource_type in (ResourceType.TRANSIT_GATEWAY, ResourceType.TRANSIT_GATEWAY_ATTACHMENT) else 1000
        if len(resource_ids) > max_allowed:
            raise ErrorCode("InvalidParameterValue", f"Maximum of {max_allowed} resource IDs allowed for resource type {resource_type.value}")
        # Validate existence of each resource id
        for rid in resource_ids:
            res = self.state.get_resource(rid)
            if res is None:
                raise ErrorCode("InvalidParameterValue", f"ResourceId {rid} does not exist")

    def create_flow_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Extract parameters
        client_token = params.get("ClientToken")
        deliver_cross_account_role = params.get("DeliverCrossAccountRole")
        deliver_logs_permission_arn = params.get("DeliverLogsPermissionArn")
        destination_options_param = params.get("DestinationOptions", {})
        dry_run = params.get("DryRun", False)
        log_destination = params.get("LogDestination")
        log_destination_type_str = params.get("LogDestinationType")
        log_format = params.get("LogFormat")
        log_group_name = params.get("LogGroupName")
        max_aggregation_interval = params.get("MaxAggregationInterval")
        resource_ids = []
        # ResourceId.N is an array of strings, keys like ResourceId.1, ResourceId.2, ...
        # The params dict may have keys like "ResourceId.1", "ResourceId.2", ...
        for key in params:
            if key.startswith("ResourceId."):
                resource_ids.append(params[key])
        resource_type_str = params.get("ResourceType")
        tag_specifications = params.get("TagSpecification", [])
        traffic_type_str = params.get("TrafficType")

        # DryRun check
        if dry_run:
            # We do not implement permission checks, so always raise DryRunOperation error
            raise ErrorCode("DryRunOperation", "DryRun operation successful.")

        # Validate required parameters
        if not resource_type_str:
            raise ErrorCode("MissingParameter", "ResourceType is required")
        if not resource_ids:
            raise ErrorCode("MissingParameter", "ResourceId.N is required")

        resource_type = self._validate_resource_type(resource_type_str)
        self._validate_resource_ids(resource_ids, resource_type)
        traffic_type = self._validate_traffic_type(traffic_type_str, resource_type)
        log_destination_type = self._validate_log_destination_type(log_destination_type_str)
        max_aggregation_interval = self._validate_max_aggregation_interval(max_aggregation_interval, resource_type)

        # Validate DeliverLogsPermissionArn required if destination type is cloud-watch-logs or kinesis-data-firehose with cross-account
        if log_destination_type == LogDestinationType.CLOUD_WATCH_LOGS:
            if not deliver_logs_permission_arn:
                raise ErrorCode("MissingParameter", "DeliverLogsPermissionArn is required if LogDestinationType is cloud-watch-logs")
        elif log_destination_type == LogDestinationType.KINESIS_DATA_FIREHOSE:
            # If delivery stream and resources are in different accounts, DeliverLogsPermissionArn is required
            # We cannot check cross-account here, so require if not provided
            if not deliver_logs_permission_arn:
                raise ErrorCode("MissingParameter", "DeliverLogsPermissionArn is required if LogDestinationType is kinesis-data-firehose and cross-account")

        # Validate DestinationOptions
        destination_options = None
        if destination_options_param:
            if not isinstance(destination_options_param, dict):
                raise ErrorCode("InvalidParameterValue", "DestinationOptions must be an object")
            file_format = destination_options_param.get("FileFormat")
            if file_format is not None and file_format not in ("plain-text", "parquet"):
                raise ErrorCode("InvalidParameterValue", "DestinationOptions.FileFormat must be 'plain-text' or 'parquet'")
            hive_compatible_partitions = destination_options_param.get("HiveCompatiblePartitions")
            if hive_compatible_partitions is not None and not isinstance(hive_compatible_partitions, bool):
                raise ErrorCode("InvalidParameterValue", "DestinationOptions.HiveCompatiblePartitions must be boolean")
            per_hour_partition = destination_options_param.get("PerHourPartition")
            if per_hour_partition is not None and not isinstance(per_hour_partition, bool):
                raise ErrorCode("InvalidParameterValue", "DestinationOptions.PerHourPartition must be boolean")
            destination_options = DestinationOptions(
                FileFormat=file_format,
                HiveCompatiblePartitions=hive_compatible_partitions,
                PerHourPartition=per_hour_partition,
            )

        # Validate TagSpecification
        tags = self._validate_tags(tag_specifications)

        # Create flow logs for each resource id
        flow_log_ids: List[str] = []
        unsuccessful: List[Dict[str, Any]] = []
        now = datetime.utcnow()

        for rid in resource_ids:
            # Generate flow log id
            flow_log_id = f"fl-{self.generate_unique_id()}"
            # Create FlowLog object
            flow_log = FlowLog(
                flow_log_id=flow_log_id,
                creation_time=now,
                deliver_cross_account_role=deliver_cross_account_role,
                deliver_logs_error_message=None,
                deliver_logs_permission_arn=deliver_logs_permission_arn,
                deliver_logs_status=DeliverLogsStatus.SUCCESS,
                destination_options=destination_options,
                flow_log_status=FlowLogStatus.ACTIVE,
                log_destination=log_destination,
                log_destination_type=log_destination_type,
                log_format=log_format,
                log_group_name=log_group_name,
                max_aggregation_interval=max_aggregation_interval,
                resource_id=rid,
                resource_type=resource_type,
                tag_set=tags,
                traffic_type=traffic_type,
            )
            # Store in shared state
            self.state.vpc_flow_logs[flow_log_id] = flow_log
            flow_log_ids.append(flow_log_id)

        response = {
            "clientToken": client_token,
            "flowLogIdSet": flow_log_ids,
            "requestId": self.generate_request_id(),
            "unsuccessful": unsuccessful,
        }
        return response

    def delete_flow_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)
        flow_log_ids: List[str] = []
        for key in params:
            if key.startswith("FlowLogId."):
                flow_log_ids.append(params[key])

        if dry_run:
            raise ErrorCode("DryRunOperation", "DryRun operation successful.")

        if not flow_log_ids:
            raise ErrorCode("MissingParameter", "FlowLogId.N is required")

        if len(flow_log_ids) > 1000:
            raise ErrorCode("InvalidParameterValue", "Maximum of 1000 flow log IDs allowed")

        unsuccessful: List[Dict[str, Any]] = []

        for flid in flow_log_ids:
            if flid not in self.state.vpc_flow_logs:
                unsuccessful.append({
                    "resourceId": flid,
                    "error": {
                        "code": "InvalidFlowLogId.NotFound",
                        "message": f"Flow log {flid} does not exist"
                    }
                })
            else:
                del self.state.vpc_flow_logs[flid]

        response = {
            "requestId": self.generate_request_id(),
            "unsuccessful": unsuccessful,
        }
        return response

    def describe_flow_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun", False)

        # Parse filters from Filter.N.Name and Filter.N.Value.M format
        filters = []
        filter_dict = {}
        for key, value in params.items():
            if key.startswith("Filter.") and ".Name" in key:
                filter_num = key.split(".")[1]
                filter_dict.setdefault(filter_num, {})["Name"] = value
            elif key.startswith("Filter.") and ".Value." in key:
                parts = key.split(".")
                filter_num = parts[1]
                filter_dict.setdefault(filter_num, {}).setdefault("Values", []).append(value)
        for f in filter_dict.values():
            if "Name" in f:
                filters.append(f)

        flow_log_ids: List[str] = []
        for key in params:
            if key.startswith("FlowLogId."):
                flow_log_ids.append(params[key])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        if dry_run:
            raise Exception("DryRunOperation: DryRun operation successful.")

        # Filter flow logs
        flow_logs = list(self.state.vpc_flow_logs.values())

        # Filter by flow_log_ids if provided
        if flow_log_ids:
            flow_logs = [fl for fl in flow_logs if fl.flow_log_id in flow_log_ids]

        # Apply filters
        for f in filters:
            if not isinstance(f, dict):
                raise ErrorCode("InvalidParameterValue", "Each filter must be a dict")
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not isinstance(values, list):
                raise ErrorCode("InvalidParameterValue", "Filter must have Name and Values list")
            name_lower = name.lower()
            # Support tag:<key> filters
            if name_lower.startswith("tag:"):
                tag_key = name[4:]
                flow_logs = [
                    fl for fl in flow_logs
                    if any(t.Key == tag_key and t.Value in values for t in fl.tag_set)
                ]
            elif name_lower == "tag-key":
                flow_logs = [
                    fl for fl in flow_logs
                    if any(t.Key in values for t in fl.tag_set)
                ]
            elif name_lower == "deliver-log-status":
                # Values: SUCCESS|FAILED
                valid_values = {v.value for v in DeliverLogsStatus}
                for val in values:
                    if val not in valid_values:
                        raise ErrorCode("InvalidParameterValue", f"Invalid deliver-log-status filter value: {val}")
                flow_logs = [
                    fl for fl in flow_logs
                    if fl.deliver_logs_status and fl.deliver_logs_status.value in values
                ]
            elif name_lower == "log-destination-type":
                valid_values = {v.value for v in LogDestinationType}
                for val in values:
                    if val not in valid_values:
                        raise ErrorCode("InvalidParameterValue", f"Invalid log-destination-type filter value: {val}")
                flow_logs = [
                    fl for fl in flow_logs
                    if fl.log_destination_type and fl.log_destination_type.value in values
                ]
            elif name_lower == "flow-log-id":
                flow_logs = [fl for fl in flow_logs if fl.flow_log_id in values]
            elif name_lower == "log-group-name":
                flow_logs = [fl for fl in flow_logs if fl.log_group_name in values]
            elif name_lower == "resource-id":
                flow_logs = [fl for fl in flow_logs if fl.resource_id in values]
            elif name_lower == "traffic-type":
                valid_values = {v.value for v in TrafficType}
                for val in values:
                    if val not in valid_values:
                        raise ErrorCode("InvalidParameterValue", f"Invalid traffic-type filter value: {val}")
                flow_logs = [
                    fl for fl in flow_logs
                    if fl.traffic_type and fl.traffic_type.value in values
                ]
            else:
                # Unknown filter name - ignore for compatibility
                pass

        # Pagination
        start_idx = 0
        if next_token:
            try:
                start_idx = int(next_token)
            except ValueError:
                start_idx = 0

        max_results_int = 1000
        if max_results:
            try:
                max_results_int = int(max_results)
            except ValueError:
                max_results_int = 1000

        end_idx = start_idx + max_results_int
        paged_flow_logs = flow_logs[start_idx:end_idx]

        new_next_token = None
        if end_idx < len(flow_logs):
            new_next_token = str(end_idx)

        # Build response
        flow_log_set = []
        for fl in paged_flow_logs:
            flow_log_set.append(fl.to_dict())

        return {
            "requestId": self.generate_request_id(),
            "flowLogSet": flow_log_set,
            "nextToken": new_next_token,
        }


from emulator_core.gateway.base import BaseGateway

class VPCflowlogsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateFlowLogs", self.create_flow_logs)
        self.register_action("DeleteFlowLogs", self.delete_flow_logs)
        self.register_action("DescribeFlowLogs", self.describe_flow_logs)
        self.register_action("GetFlowLogsIntegrationTemplate", self.get_flow_logs_integration_template)

    def create_flow_logs(self, params):
        return self.backend.create_flow_logs(params)

    def delete_flow_logs(self, params):
        return self.backend.delete_flow_logs(params)

    def describe_flow_logs(self, params):
        return self.backend.describe_flow_logs(params)

    def get_flow_logs_integration_template(self, params):
        return self.backend.get_flow_logs_integration_template(params)
