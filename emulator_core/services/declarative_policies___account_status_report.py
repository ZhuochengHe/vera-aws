from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class ReportStatus(Enum):
    RUNNING = "running"
    CANCELLED = "cancelled"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class DeclarativePoliciesReport:
    report_id: str
    s3_bucket: Optional[str] = None
    s3_prefix: Optional[str] = None
    target_id: Optional[str] = None
    status: ReportStatus = ReportStatus.RUNNING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reportId": self.report_id,
            "s3Bucket": self.s3_bucket,
            "s3Prefix": self.s3_prefix,
            "targetId": self.target_id,
            "status": self.status.value,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "tagSet": [Tag(k, v).to_dict() for k, v in self.tags.items()] if self.tags else [],
        }


@dataclass
class AttributeSummary:
    attributeName: Optional[str] = None
    mostFrequentValue: Optional[str] = None
    numberOfMatchedAccounts: Optional[int] = None
    numberOfUnmatchedAccounts: Optional[int] = None
    regionalSummarySet: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attributeName": self.attributeName,
            "mostFrequentValue": self.mostFrequentValue,
            "numberOfMatchedAccounts": self.numberOfMatchedAccounts,
            "numberOfUnmatchedAccounts": self.numberOfUnmatchedAccounts,
            "regionalSummarySet": self.regionalSummarySet or [],
        }


class DeclarativePoliciesAccountStatusReportBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.declarative_policies_account_status_report dict for storage

    def _validate_tags(self, tags: List[Dict[str, Any]]) -> Dict[str, str]:
        validated_tags = {}
        for tag in tags:
            if not isinstance(tag, dict):
                raise ErrorCode("InvalidParameterValue", "Each tag must be a dictionary")
            key = tag.get("Key")
            value = tag.get("Value")
            if key is None or not isinstance(key, str):
                raise ErrorCode("InvalidParameterValue", "Tag Key must be a string and cannot be None")
            if key.lower().startswith("aws:"):
                raise ErrorCode("InvalidParameterValue", "Tag keys may not begin with 'aws:'")
            if len(key) > 127:
                raise ErrorCode("InvalidParameterValue", "Tag keys accept a maximum of 127 Unicode characters")
            if value is not None and not isinstance(value, str):
                raise ErrorCode("InvalidParameterValue", "Tag Value must be a string if provided")
            if value is not None and len(value) > 256:
                raise ErrorCode("InvalidParameterValue", "Tag values accept a maximum of 256 Unicode characters")
            validated_tags[key] = value if value is not None else ""
        return validated_tags

    def _validate_tag_specifications(self, tag_specifications: List[Dict[str, Any]]) -> Dict[str, str]:
        # Only accept tags for resource type 'declarative-policies-report'
        tags: Dict[str, str] = {}
        for spec in tag_specifications:
            if not isinstance(spec, dict):
                raise ErrorCode("InvalidParameterValue", "Each TagSpecification must be a dictionary")
            resource_type = spec.get("ResourceType")
            if resource_type != "declarative-policies-report":
                raise ErrorCode("InvalidParameterValue", "TagSpecification ResourceType must be 'declarative-policies-report'")
            tags_list = spec.get("Tags", [])
            if not isinstance(tags_list, list):
                raise ErrorCode("InvalidParameterValue", "Tags must be a list")
            tags.update(self._validate_tags(tags_list))
        return tags

    def _get_report_by_id(self, report_id: str) -> DeclarativePoliciesReport:
        if not isinstance(report_id, str) or not report_id:
            raise ErrorCode("InvalidParameterValue", "ReportId must be a non-empty string")
        report = self.state.declarative_policies_account_status_report.get(report_id)
        if not report:
            raise ErrorCode("InvalidReportId.NotFound", f"Report with ID {report_id} not found")
        return report

    def CancelDeclarativePoliciesReport(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun param if present
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a Boolean if provided")

        report_id = params.get("ReportId")
        if report_id is None:
            raise ErrorCode("MissingParameter", "ReportId is required")
        if not isinstance(report_id, str):
            raise ErrorCode("InvalidParameterValue", "ReportId must be a string")

        report = self.state.declarative_policies_account_status_report.get(report_id)
        if not report:
            raise ErrorCode("InvalidReportId.NotFound", f"Report with ID {report_id} not found")

        # DryRun behavior: simulate permission check
        if dry_run:
            # For simplicity, assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Only cancel if status is running
        if report.status != ReportStatus.RUNNING:
            # Cannot cancel if status is complete, cancelled, or error
            raise ErrorCode("IncorrectReportStatus", f"Cannot cancel report with status {report.status.value}")

        # Cancel the report
        report.status = ReportStatus.CANCELLED
        report.end_time = datetime.utcnow()

        # Store updated report
        self.state.declarative_policies_account_status_report[report_id] = report

        return {
            "requestId": self.generate_request_id(),
            "return": True,
        }

    def DescribeDeclarativePoliciesReports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a Boolean if provided")

        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode("InvalidParameterValue", "MaxResults must be an integer")
            if max_results < 1 or max_results > 1000:
                raise ErrorCode("InvalidParameterValue", "MaxResults must be between 1 and 1000")

        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode("InvalidParameterValue", "NextToken must be a string if provided")

        report_ids = params.get("ReportId.N")
        if report_ids is not None:
            if not isinstance(report_ids, list):
                raise ErrorCode("InvalidParameterValue", "ReportId.N must be a list of strings")
            for rid in report_ids:
                if not isinstance(rid, str):
                    raise ErrorCode("InvalidParameterValue", "Each ReportId.N must be a string")

        # DryRun behavior
        if dry_run:
            # Assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Filter reports by ReportId.N if provided
        reports: List[DeclarativePoliciesReport] = []
        if report_ids:
            for rid in report_ids:
                report = self.state.declarative_policies_-_account_status_report.get(rid)
                if report:
                    reports.append(report)
        else:
            reports = list(self.state.declarative_policies_account_status_report.values())

        # Pagination logic
        # Use next_token as an index string (e.g. "5") for simplicity
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode("InvalidParameterValue", "NextToken is invalid")

        # Apply max_results limit
        end_index = len(reports)
        if max_results is not None:
            end_index = min(start_index + max_results, len(reports))

        paged_reports = reports[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = None
        if end_index < len(reports):
            new_next_token = str(end_index)

        return {
            "requestId": self.generate_request_id(),
            "reportSet": [r.to_dict() for r in paged_reports],
            "nextToken": new_next_token,
        }

    def GetDeclarativePoliciesReportSummary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a Boolean if provided")

        report_id = params.get("ReportId")
        if report_id is None:
            raise ErrorCode("MissingParameter", "ReportId is required")
        if not isinstance(report_id, str):
            raise ErrorCode("InvalidParameterValue", "ReportId must be a string")

        # DryRun behavior
        if dry_run:
            # Assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        report = self.state.declarative_policies_account_status_report.get(report_id)
        if not report:
            raise ErrorCode("InvalidReportId.NotFound", f"Report with ID {report_id} not found")

        # Only complete reports have summaries
        if report.status != ReportStatus.COMPLETE:
            raise ErrorCode("ReportNotComplete", "Report summary is only available for reports with status 'complete'")

        # For simplicity, we return empty attributeSummarySet and zero counts
        # since no detailed data is provided in the spec
        attribute_summary_set: List[Dict[str, Any]] = []

        return {
            "requestId": self.generate_request_id(),
            "reportId": report.report_id,
            "s3Bucket": report.s3_bucket,
            "s3Prefix": report.s3_prefix,
            "targetId": report.target_id,
            "startTime": report.start_time.isoformat() if report.start_time else None,
            "endTime": report.end_time.isoformat() if report.end_time else None,
            "numberOfAccounts": 0,
            "numberOfFailedAccounts": 0,
            "attributeSummarySet": attribute_summary_set,
        }

    def StartDeclarativePoliciesReport(self, params: Dict[str, Any]) -> Dict[str, Any]:
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode("InvalidParameterValue", "DryRun must be a Boolean if provided")

        s3_bucket = params.get("S3Bucket")
        if s3_bucket is None:
            raise ErrorCode("MissingParameter", "S3Bucket is required")
        if not isinstance(s3_bucket, str) or not s3_bucket.strip():
            raise ErrorCode("InvalidParameterValue", "S3Bucket must be a non-empty string")

        s3_prefix = params.get("S3Prefix")
        if s3_prefix is not None and not isinstance(s3_prefix, str):
            raise ErrorCode("InvalidParameterValue", "S3Prefix must be a string if provided")

        tag_specifications = params.get("TagSpecification.N")
        tags: Dict[str, str] = {}
        if tag_specifications is not None:
            if not isinstance(tag_specifications, list):
                raise ErrorCode("InvalidParameterValue", "TagSpecification.N must be a list if provided")
            tags = self._validate_tag_specifications(tag_specifications)

        target_id = params.get("TargetId")
        if target_id is None:
            raise ErrorCode("MissingParameter", "TargetId is required")
        if not isinstance(target_id, str) or not target_id.strip():
            raise ErrorCode("InvalidParameterValue", "TargetId must be a non-empty string")

        # DryRun behavior
        if dry_run:
            # Assume permission granted
            raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

        # Create new report
        report_id = f"report-{self.generate_unique_id()}"
        now = datetime.utcnow()
        report = DeclarativePoliciesReport(
            report_id=report_id,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            target_id=target_id,
            status=ReportStatus.RUNNING,
            start_time=now,
            end_time=None,
            tags=tags,
        )

        # Store in shared state dict
        self.state.declarative_policies_account_status_report[report_id] = report

        return {
            "requestId": self.generate_request_id(),
            "reportId": report_id,
        }

from emulator_core.gateway.base import BaseGateway

class DeclarativePoliciesAccountStatusReportGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CancelDeclarativePoliciesReport", self.cancel_declarative_policies_report)
        self.register_action("DescribeDeclarativePoliciesReports", self.describe_declarative_policies_reports)
        self.register_action("GetDeclarativePoliciesReportSummary", self.get_declarative_policies_report_summary)
        self.register_action("StartDeclarativePoliciesReport", self.start_declarative_policies_report)

    def cancel_declarative_policies_report(self, params):
        return self.backend.cancel_declarative_policies_report(params)

    def describe_declarative_policies_reports(self, params):
        return self.backend.describe_declarative_policies_reports(params)

    def get_declarative_policies_report_summary(self, params):
        return self.backend.get_declarative_policies_report_summary(params)

    def start_declarative_policies_report(self, params):
        return self.backend.start_declarative_policies_report(params)
