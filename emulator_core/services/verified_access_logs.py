from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class VerifiedAccessLogDeliveryStatusCode(Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class VerifiedAccessLogDeliveryStatus:
    code: Optional[VerifiedAccessLogDeliveryStatusCode] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value if self.code else None,
            "message": self.message,
        }


@dataclass
class VerifiedAccessLogCloudWatchLogsDestination:
    deliveryStatus: Optional[VerifiedAccessLogDeliveryStatus] = None
    enabled: Optional[bool] = None
    logGroup: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deliveryStatus": self.deliveryStatus.to_dict() if self.deliveryStatus else None,
            "enabled": self.enabled,
            "logGroup": self.logGroup,
        }


@dataclass
class VerifiedAccessLogKinesisDataFirehoseDestination:
    deliveryStatus: Optional[VerifiedAccessLogDeliveryStatus] = None
    deliveryStream: Optional[str] = None
    enabled: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deliveryStatus": self.deliveryStatus.to_dict() if self.deliveryStatus else None,
            "deliveryStream": self.deliveryStream,
            "enabled": self.enabled,
        }


@dataclass
class VerifiedAccessLogS3Destination:
    bucketName: Optional[str] = None
    bucketOwner: Optional[str] = None
    deliveryStatus: Optional[VerifiedAccessLogDeliveryStatus] = None
    enabled: Optional[bool] = None
    prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bucketName": self.bucketName,
            "bucketOwner": self.bucketOwner,
            "deliveryStatus": self.deliveryStatus.to_dict() if self.deliveryStatus else None,
            "enabled": self.enabled,
            "prefix": self.prefix,
        }


@dataclass
class VerifiedAccessLogs:
    cloudWatchLogs: Optional[VerifiedAccessLogCloudWatchLogsDestination] = None
    includeTrustContext: Optional[bool] = None
    kinesisDataFirehose: Optional[VerifiedAccessLogKinesisDataFirehoseDestination] = None
    logVersion: Optional[str] = None
    s3: Optional[VerifiedAccessLogS3Destination] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cloudWatchLogs": self.cloudWatchLogs.to_dict() if self.cloudWatchLogs else None,
            "includeTrustContext": self.includeTrustContext,
            "kinesisDataFirehose": self.kinesisDataFirehose.to_dict() if self.kinesisDataFirehose else None,
            "logVersion": self.logVersion,
            "s3": self.s3.to_dict() if self.s3 else None,
        }


@dataclass
class VerifiedAccessInstanceLoggingConfiguration:
    accessLogs: Optional[VerifiedAccessLogs] = None
    verifiedAccessInstanceId: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessLogs": self.accessLogs.to_dict() if self.accessLogs else None,
            "verifiedAccessInstanceId": self.verifiedAccessInstanceId,
        }


class VerifiedAccessLogsBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.verified_access_logs dict for storage

    def _validate_delivery_status(self, data: Dict[str, Any]) -> VerifiedAccessLogDeliveryStatus:
        if not isinstance(data, dict):
            raise ErrorCode("InvalidParameterValue", "DeliveryStatus must be an object")
        code = data.get("code")
        message = data.get("message")
        if code is not None:
            if code not in (VerifiedAccessLogDeliveryStatusCode.SUCCESS.value, VerifiedAccessLogDeliveryStatusCode.FAILED.value):
                raise ErrorCode("InvalidParameterValue", f"Invalid delivery status code: {code}")
            code_enum = VerifiedAccessLogDeliveryStatusCode(code)
        else:
            code_enum = None
        if message is not None and not isinstance(message, str):
            raise ErrorCode("InvalidParameterValue", "DeliveryStatus message must be a string")
        return VerifiedAccessLogDeliveryStatus(code=code_enum, message=message)

    def _validate_cloudwatch_logs_destination(self, data: Dict[str, Any]) -> VerifiedAccessLogCloudWatchLogsDestination:
        if not isinstance(data, dict):
            raise ErrorCode("InvalidParameterValue", "CloudWatchLogs must be an object")
        delivery_status = None
        if "deliveryStatus" in data:
            delivery_status = self._validate_delivery_status(data["deliveryStatus"])
        enabled = data.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            raise ErrorCode("InvalidParameterValue", "CloudWatchLogs enabled must be a boolean")
        log_group = data.get("logGroup")
        if log_group is not None and not isinstance(log_group, str):
            raise ErrorCode("InvalidParameterValue", "CloudWatchLogs logGroup must be a string")
        return VerifiedAccessLogCloudWatchLogsDestination(
            deliveryStatus=delivery_status,
            enabled=enabled,
            logGroup=log_group,
        )

    def _validate_kinesis_data_firehose_destination(self, data: Dict[str, Any]) -> VerifiedAccessLogKinesisDataFirehoseDestination:
        if not isinstance(data, dict):
            raise ErrorCode("InvalidParameterValue", "KinesisDataFirehose must be an object")
        delivery_status = None
        if "deliveryStatus" in data:
            delivery_status = self._validate_delivery_status(data["deliveryStatus"])
        delivery_stream = data.get("deliveryStream")
        if delivery_stream is not None and not isinstance(delivery_stream, str):
            raise ErrorCode("InvalidParameterValue", "KinesisDataFirehose deliveryStream must be a string")
        enabled = data.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            raise ErrorCode("InvalidParameterValue", "KinesisDataFirehose enabled must be a boolean")
        return VerifiedAccessLogKinesisDataFirehoseDestination(
            deliveryStatus=delivery_status,
            deliveryStream=delivery_stream,
            enabled=enabled,
        )

    def _validate_s3_destination(self, data: Dict[str, Any]) -> VerifiedAccessLogS3Destination:
        if not isinstance(data, dict):
            raise ErrorCode("InvalidParameterValue", "S3 must be an object")
        bucket_name = data.get("bucketName")
        if bucket_name is not None and not isinstance(bucket_name, str):
            raise ErrorCode("InvalidParameterValue", "S3 bucketName must be a string")
        bucket_owner = data.get("bucketOwner")
        if bucket_owner is not None and not isinstance(bucket_owner, str):
            raise ErrorCode("InvalidParameterValue", "S3 bucketOwner must be a string")
        delivery_status = None
        if "deliveryStatus" in data:
            delivery_status = self._validate_delivery_status(data["deliveryStatus"])
        enabled = data.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            raise ErrorCode("InvalidParameterValue", "S3 enabled must be a boolean")
        prefix = data.get("prefix")
        if prefix is not None and not isinstance(prefix, str):
            raise ErrorCode("InvalidParameterValue", "S3 prefix must be a string")
        return VerifiedAccessLogS3Destination(
            bucketName=bucket_name,
            bucketOwner=bucket_owner,
            deliveryStatus=delivery_status,
            enabled=enabled,
            prefix=prefix,
        )

    def _validate_access_logs(self, data: Dict[str, Any]) -> VerifiedAccessLogs:
        if not isinstance(data, dict):
            raise ErrorCode("InvalidParameterValue", "AccessLogs must be an object")
        cloudwatch_logs = None
        if "CloudWatchLogs" in data:
            cloudwatch_logs = self._validate_cloudwatch_logs_destination(data["CloudWatchLogs"])
        include_trust_context = data.get("IncludeTrustContext")
        if include_trust_context is not None and not isinstance(include_trust_context, bool):
            raise ErrorCode("InvalidParameterValue", "IncludeTrustContext must be a boolean")
        kinesis_data_firehose = None
        if "KinesisDataFirehose" in data:
            kinesis_data_firehose = self._validate_kinesis_data_firehose_destination(data["KinesisDataFirehose"])
        log_version = data.get("LogVersion")
        if log_version is not None and not isinstance(log_version, str):
            raise ErrorCode("InvalidParameterValue", "LogVersion must be a string")
        s3 = None
        if "S3" in data:
            s3 = self._validate_s3_destination(data["S3"])
        return VerifiedAccessLogs(
            cloudWatchLogs=cloudwatch_logs,
            includeTrustContext=include_trust_context,
            kinesisDataFirehose=kinesis_data_firehose,
            logVersion=log_version,
            s3=s3,
        )

    def _filter_logging_configurations(
        self,
        configs: List[VerifiedAccessInstanceLoggingConfiguration],
        filters: Optional[List[Dict[str, Any]]],
        verified_access_instance_ids: Optional[List[str]],
    ) -> List[VerifiedAccessInstanceLoggingConfiguration]:
        # Filters are case-sensitive, filter names and values
        # Supported filters are not explicitly defined in the spec, so we support filtering by verifiedAccessInstanceId only
        filtered = configs
        if verified_access_instance_ids is not None:
            filtered = [c for c in filtered if c.verifiedAccessInstanceId in verified_access_instance_ids]
        if filters:
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if not isinstance(name, str):
                    raise ErrorCode("InvalidParameterValue", "Filter Name must be a string")
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                    raise ErrorCode("InvalidParameterValue", "Filter Values must be a list of strings")
                # Only support filter on verifiedAccessInstanceId for now
                if name == "verifiedAccessInstanceId":
                    filtered = [c for c in filtered if c.verifiedAccessInstanceId in values]
                else:
                    # Unknown filter name: no results
                    filtered = []
        return filtered

    def DescribeVerifiedAccessInstanceLoggingConfigurations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Validate Filters if present
        filters = params.get("Filter.N")
        if filters is not None:
            if not isinstance(filters, list):
                raise ErrorCode("InvalidParameterValue", "Filter.N must be a list")
            for f in filters:
                if not isinstance(f, dict):
                    raise ErrorCode("InvalidParameterValue", "Each filter must be an object")
                # Name and Values are optional but if present must be correct type
                if "Name" in f and not isinstance(f["Name"], str):
                    raise ErrorCode("InvalidParameterValue", "Filter Name must be a string")
                if "Values" in f:
                    if not isinstance(f["Values"], list) or not all(isinstance(v, str) for v in f["Values"]):
                        raise ErrorCode("InvalidParameterValue", "Filter Values must be a list of strings")

        # Validate MaxResults if present
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 1 or max_results > 10:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 1 and 10")

        # Validate NextToken if present
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string")

        # Validate VerifiedAccessInstanceId.N if present
        verified_access_instance_ids = params.get("VerifiedAccessInstanceId.N")
        if verified_access_instance_ids is not None:
            if not isinstance(verified_access_instance_ids, list) or not all(isinstance(v, str) for v in verified_access_instance_ids):
                raise ErrorCode("InvalidParameterValue", "VerifiedAccessInstanceId.N must be a list of strings")

        # Collect all logging configurations from state
        all_configs = list(self.state.verified_access_logs.values())

        # Filter by VerifiedAccessInstanceId.N and Filters
        filtered_configs = self._filter_logging_configurations(all_configs, filters, verified_access_instance_ids)

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "Invalid NextToken value")

        end_index = start_index + max_results if max_results else None
        page_configs = filtered_configs[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index is not None and end_index < len(filtered_configs):
            new_next_token = str(end_index)

        # Build response list
        logging_configuration_set = [c.to_dict() for c in page_configs]

        return {
            "loggingConfigurationSet": logging_configuration_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def ModifyVerifiedAccessInstanceLoggingConfiguration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        if "AccessLogs" not in params:
            raise ErrorCode("MissingParameter", "AccessLogs is required")
        if "VerifiedAccessInstanceId" not in params:
            raise ErrorCode("MissingParameter", "VerifiedAccessInstanceId is required")

        access_logs_data = params["AccessLogs"]
        verified_access_instance_id = params["VerifiedAccessInstanceId"]

        if not isinstance(access_logs_data, dict):
            raise ErrorCode("InvalidParameterValue", "AccessLogs must be an object")
        if not isinstance(verified_access_instance_id, str):
            raise ErrorCode("InvalidParameterValue", "VerifiedAccessInstanceId must be a string")

        # Validate DryRun if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")

        # Validate ClientToken if present
        client_token = params.get("ClientToken")
        if client_token is not None and not isinstance(client_token, str):
            raise ErrorCode("InvalidParameterValue", "ClientToken must be a string")

        # Validate AccessLogs subfields
        # CloudWatchLogs, KinesisDataFirehose, S3 have required Enabled fields if present
        # Validate CloudWatchLogs
        if "CloudWatchLogs" in access_logs_data:
            cwl = access_logs_data["CloudWatchLogs"]
            if not isinstance(cwl, dict):
                raise ErrorCode("InvalidParameterValue", "CloudWatchLogs must be an object")
            if "Enabled" not in cwl:
                raise ErrorCode("MissingParameter", "CloudWatchLogs Enabled is required")
            if not isinstance(cwl["Enabled"], bool):
                raise ErrorCode("InvalidParameterValue", "CloudWatchLogs Enabled must be a boolean")
            # Validate optional LogGroup
            if "LogGroup" in cwl and not isinstance(cwl["LogGroup"], str):
                raise ErrorCode("InvalidParameterValue", "CloudWatchLogs LogGroup must be a string")

        # Validate KinesisDataFirehose
        if "KinesisDataFirehose" in access_logs_data:
            kdf = access_logs_data["KinesisDataFirehose"]
            if not isinstance(kdf, dict):
                raise ErrorCode("InvalidParameterValue", "KinesisDataFirehose must be an object")
            if "Enabled" not in kdf:
                raise ErrorCode("MissingParameter", "KinesisDataFirehose Enabled is required")
            if not isinstance(kdf["Enabled"], bool):
                raise ErrorCode("InvalidParameterValue", "KinesisDataFirehose Enabled must be a boolean")
            if "DeliveryStream" in kdf and not isinstance(kdf["DeliveryStream"], str):
                raise ErrorCode("InvalidParameterValue", "KinesisDataFirehose DeliveryStream must be a string")

        # Validate S3
        if "S3" in access_logs_data:
            s3 = access_logs_data["S3"]
            if not isinstance(s3, dict):
                raise ErrorCode("InvalidParameterValue", "S3 must be an object")
            if "Enabled" not in s3:
                raise ErrorCode("MissingParameter", "S3 Enabled is required")
            if not isinstance(s3["Enabled"], bool):
                raise ErrorCode("InvalidParameterValue", "S3 Enabled must be a boolean")
            if "BucketName" in s3 and not isinstance(s3["BucketName"], str):
                raise ErrorCode("InvalidParameterValue", "S3 BucketName must be a string")
            if "BucketOwner" in s3 and not isinstance(s3["BucketOwner"], str):
                raise ErrorCode("InvalidParameterValue", "S3 BucketOwner must be a string")
            if "Prefix" in s3 and not isinstance(s3["Prefix"], str):
                raise ErrorCode("InvalidParameterValue", "S3 Prefix must be a string")

        # Validate IncludeTrustContext if present
        if "IncludeTrustContext" in access_logs_data:
            if not isinstance(access_logs_data["IncludeTrustContext"], bool):
                raise ErrorCode("InvalidParameterValue", "IncludeTrustContext must be a boolean")

        # Validate LogVersion if present
        if "LogVersion" in access_logs_data:
            if not isinstance(access_logs_data["LogVersion"], str):
                raise ErrorCode("InvalidParameterValue", "LogVersion must be a string")
            # Valid values: ocsf-0.1 | ocsf-1.0.0-rc.2
            if access_logs_data["LogVersion"] not in ("ocsf-0.1", "ocsf-1.0.0-rc.2"):
                raise ErrorCode("InvalidParameterValue", "Invalid LogVersion value")

        # Check if VerifiedAccessInstanceId exists in state
        # We do not have VerifiedAccessInstance resource here, so just check if logging config exists or create new
        existing_config = self.state.verified_access_logs.get(verified_access_instance_id)

        # Build VerifiedAccessLogs object from AccessLogs data
        access_logs_obj = self._validate_access_logs(access_logs_data)

        # Create or update logging configuration
        config = VerifiedAccessInstanceLoggingConfiguration(
            accessLogs=access_logs_obj,
            verifiedAccessInstanceId=verified_access_instance_id,
        )
        self.state.verified_access_logs[verified_access_instance_id] = config

        return {
            "loggingConfiguration": config.to_dict(),
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class VerifiedAccessLogsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeVerifiedAccessInstanceLoggingConfigurations", self.describe_verified_access_instance_logging_configurations)
        self.register_action("ModifyVerifiedAccessInstanceLoggingConfiguration", self.modify_verified_access_instance_logging_configuration)

    def describe_verified_access_instance_logging_configurations(self, params):
        return self.backend.describe_verified_access_instance_logging_configurations(params)

    def modify_verified_access_instance_logging_configuration(self, params):
        return self.backend.modify_verified_access_instance_logging_configuration(params)
