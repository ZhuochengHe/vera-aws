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
class DeclarativePolicyAccountStatusReport:
    end_time: str = ""
    report_id: str = ""
    s3_bucket: str = ""
    s3_prefix: str = ""
    start_time: str = ""
    status: str = ""
    tag_set: List[Any] = field(default_factory=list)
    target_id: str = ""

    attribute_summary_set: List[Dict[str, Any]] = field(default_factory=list)
    number_of_accounts: List[Any] = field(default_factory=list)
    number_of_failed_accounts: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "endTime": self.end_time,
            "reportId": self.report_id,
            "s3Bucket": self.s3_bucket,
            "s3Prefix": self.s3_prefix,
            "startTime": self.start_time,
            "status": self.status,
            "tagSet": self.tag_set,
            "targetId": self.target_id,
            "attributeSummarySet": self.attribute_summary_set,
            "numberOfAccounts": self.number_of_accounts,
            "numberOfFailedAccounts": self.number_of_failed_accounts,
        }

class DeclarativePolicyAccountStatusReport_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.declarative_policies_account_status_report  # alias to shared store


    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_report_or_error(self, report_id: str, error_code: str = "InvalidReportId.NotFound"):
        report = self.resources.get(report_id)
        if not report:
            return None, create_error_response(error_code, f"The ID '{report_id}' does not exist")
        return report, None

    def _get_reports_by_ids(self, report_ids: List[str], error_code: str = "InvalidReportId.NotFound"):
        reports: List[DeclarativePolicyAccountStatusReport] = []
        for report_id in report_ids:
            report = self.resources.get(report_id)
            if not report:
                return None, create_error_response(error_code, f"The ID '{report_id}' does not exist")
            reports.append(report)
        return reports, None

    def CancelDeclarativePoliciesReport(self, params: Dict[str, Any]):
        """Cancels the generation of an account status report. You can only cancel a report while it has therunningstatus. Reports
            with other statuses (complete,cancelled, orerror) can't be canceled. For more information, seeGenerating the account status report for declarative policiesin theAWS Org"""

        error = self._require_params(params, ["ReportId"])
        if error:
            return error

        report_id = params.get("ReportId")
        report, error = self._get_report_or_error(report_id)
        if error:
            return error

        if report.status != "running":
            return create_error_response("InvalidStateTransition", f"Report '{report_id}' is not in the running state")

        report.status = "cancelled"
        report.end_time = self._utc_now()

        return {
            'return': True,
            }

    def DescribeDeclarativePoliciesReports(self, params: Dict[str, Any]):
        """Describes the metadata of an account status report, including the status of the
            report. To view the full report, download it from the Amazon S3 bucket where it was saved.
            Reports are accessible only when they have thecompletestatus. Reports
            with other statuses (ru"""

        report_ids = params.get("ReportId.N", []) or []

        if report_ids:
            reports, error = self._get_reports_by_ids(report_ids)
            if error:
                return error
        else:
            reports = list(self.resources.values())

        report_set = [report.to_dict() for report in reports]

        return {
            'nextToken': None,
            'reportSet': report_set,
            }

    def GetDeclarativePoliciesReportSummary(self, params: Dict[str, Any]):
        """Retrieves a summary of the account status report. To view the full report, download it from the Amazon S3 bucket where it was saved.
            Reports are accessible only when they have thecompletestatus. Reports
            with other statuses (running,cancelled, orerror) are not available in the"""

        error = self._require_params(params, ["ReportId"])
        if error:
            return error

        report_id = params.get("ReportId")
        report, error = self._get_report_or_error(report_id)
        if error:
            return error

        return {
            'attributeSummarySet': report.attribute_summary_set,
            'endTime': report.end_time,
            'numberOfAccounts': report.number_of_accounts,
            'numberOfFailedAccounts': report.number_of_failed_accounts,
            'reportId': report.report_id,
            's3Bucket': report.s3_bucket,
            's3Prefix': report.s3_prefix,
            'startTime': report.start_time,
            'targetId': report.target_id,
            }

    def StartDeclarativePoliciesReport(self, params: Dict[str, Any]):
        """Generates an account status report. The report is generated asynchronously, and can
            take several hours to complete. The report provides the current status of all attributes supported by declarative
            policies for the accounts within the specified scope. The scope is determined """

        error = self._require_params(params, ["S3Bucket", "TargetId"])
        if error:
            return error

        s3_bucket = params.get("S3Bucket")
        s3_prefix = params.get("S3Prefix") or ""
        target_id = params.get("TargetId")
        tag_specs = params.get("TagSpecification.N", []) or []

        tag_set: List[Dict[str, Any]] = []
        for spec in tag_specs:
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        report_id = self._generate_id("report")
        report = DeclarativePolicyAccountStatusReport(
            end_time="",
            report_id=report_id,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            start_time=self._utc_now(),
            status="running",
            tag_set=tag_set,
            target_id=target_id,
            attribute_summary_set=[],
            number_of_accounts=[],
            number_of_failed_accounts=[],
        )
        self.resources[report_id] = report

        return {
            'reportId': report_id,
            }

    def _generate_id(self, prefix: str = 'report') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class declarativepolicyaccountstatusreport_RequestParser:
    @staticmethod
    def parse_cancel_declarative_policies_report_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ReportId": get_scalar(md, "ReportId"),
        }

    @staticmethod
    def parse_describe_declarative_policies_reports_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ReportId.N": get_indexed_list(md, "ReportId"),
        }

    @staticmethod
    def parse_get_declarative_policies_report_summary_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ReportId": get_scalar(md, "ReportId"),
        }

    @staticmethod
    def parse_start_declarative_policies_report_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "S3Bucket": get_scalar(md, "S3Bucket"),
            "S3Prefix": get_scalar(md, "S3Prefix"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "TargetId": get_scalar(md, "TargetId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CancelDeclarativePoliciesReport": declarativepolicyaccountstatusreport_RequestParser.parse_cancel_declarative_policies_report_request,
            "DescribeDeclarativePoliciesReports": declarativepolicyaccountstatusreport_RequestParser.parse_describe_declarative_policies_reports_request,
            "GetDeclarativePoliciesReportSummary": declarativepolicyaccountstatusreport_RequestParser.parse_get_declarative_policies_report_summary_request,
            "StartDeclarativePoliciesReport": declarativepolicyaccountstatusreport_RequestParser.parse_start_declarative_policies_report_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class declarativepolicyaccountstatusreport_ResponseSerializer:
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
                xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_cancel_declarative_policies_report_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelDeclarativePoliciesReportResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</CancelDeclarativePoliciesReportResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_declarative_policies_reports_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeDeclarativePoliciesReportsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize reportSet
        _reportSet_key = None
        if "reportSet" in data:
            _reportSet_key = "reportSet"
        elif "ReportSet" in data:
            _reportSet_key = "ReportSet"
        elif "Reports" in data:
            _reportSet_key = "Reports"
        if _reportSet_key:
            param_data = data[_reportSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reportSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reportSet>')
            else:
                xml_parts.append(f'{indent_str}<reportSet/>')
        xml_parts.append(f'</DescribeDeclarativePoliciesReportsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_declarative_policies_report_summary_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetDeclarativePoliciesReportSummaryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize attributeSummarySet
        _attributeSummarySet_key = None
        if "attributeSummarySet" in data:
            _attributeSummarySet_key = "attributeSummarySet"
        elif "AttributeSummarySet" in data:
            _attributeSummarySet_key = "AttributeSummarySet"
        elif "AttributeSummarys" in data:
            _attributeSummarySet_key = "AttributeSummarys"
        if _attributeSummarySet_key:
            param_data = data[_attributeSummarySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<attributeSummarySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(declarativepolicyaccountstatusreport_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</attributeSummarySet>')
            else:
                xml_parts.append(f'{indent_str}<attributeSummarySet/>')
        # Serialize endTime
        _endTime_key = None
        if "endTime" in data:
            _endTime_key = "endTime"
        elif "EndTime" in data:
            _endTime_key = "EndTime"
        if _endTime_key:
            param_data = data[_endTime_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<endTime>{esc(str(param_data))}</endTime>')
        # Serialize numberOfAccounts
        _numberOfAccounts_key = None
        if "numberOfAccounts" in data:
            _numberOfAccounts_key = "numberOfAccounts"
        elif "NumberOfAccounts" in data:
            _numberOfAccounts_key = "NumberOfAccounts"
        if _numberOfAccounts_key:
            param_data = data[_numberOfAccounts_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<numberOfAccountsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</numberOfAccountsSet>')
            else:
                xml_parts.append(f'{indent_str}<numberOfAccountsSet/>')
        # Serialize numberOfFailedAccounts
        _numberOfFailedAccounts_key = None
        if "numberOfFailedAccounts" in data:
            _numberOfFailedAccounts_key = "numberOfFailedAccounts"
        elif "NumberOfFailedAccounts" in data:
            _numberOfFailedAccounts_key = "NumberOfFailedAccounts"
        if _numberOfFailedAccounts_key:
            param_data = data[_numberOfFailedAccounts_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<numberOfFailedAccountsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</numberOfFailedAccountsSet>')
            else:
                xml_parts.append(f'{indent_str}<numberOfFailedAccountsSet/>')
        # Serialize reportId
        _reportId_key = None
        if "reportId" in data:
            _reportId_key = "reportId"
        elif "ReportId" in data:
            _reportId_key = "ReportId"
        if _reportId_key:
            param_data = data[_reportId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<reportId>{esc(str(param_data))}</reportId>')
        # Serialize s3Bucket
        _s3Bucket_key = None
        if "s3Bucket" in data:
            _s3Bucket_key = "s3Bucket"
        elif "S3Bucket" in data:
            _s3Bucket_key = "S3Bucket"
        if _s3Bucket_key:
            param_data = data[_s3Bucket_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<s3Bucket>{esc(str(param_data))}</s3Bucket>')
        # Serialize s3Prefix
        _s3Prefix_key = None
        if "s3Prefix" in data:
            _s3Prefix_key = "s3Prefix"
        elif "S3Prefix" in data:
            _s3Prefix_key = "S3Prefix"
        if _s3Prefix_key:
            param_data = data[_s3Prefix_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<s3Prefix>{esc(str(param_data))}</s3Prefix>')
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
        # Serialize targetId
        _targetId_key = None
        if "targetId" in data:
            _targetId_key = "targetId"
        elif "TargetId" in data:
            _targetId_key = "TargetId"
        if _targetId_key:
            param_data = data[_targetId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<targetId>{esc(str(param_data))}</targetId>')
        xml_parts.append(f'</GetDeclarativePoliciesReportSummaryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_start_declarative_policies_report_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<StartDeclarativePoliciesReportResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize reportId
        _reportId_key = None
        if "reportId" in data:
            _reportId_key = "reportId"
        elif "ReportId" in data:
            _reportId_key = "ReportId"
        if _reportId_key:
            param_data = data[_reportId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<reportId>{esc(str(param_data))}</reportId>')
        xml_parts.append(f'</StartDeclarativePoliciesReportResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CancelDeclarativePoliciesReport": declarativepolicyaccountstatusreport_ResponseSerializer.serialize_cancel_declarative_policies_report_response,
            "DescribeDeclarativePoliciesReports": declarativepolicyaccountstatusreport_ResponseSerializer.serialize_describe_declarative_policies_reports_response,
            "GetDeclarativePoliciesReportSummary": declarativepolicyaccountstatusreport_ResponseSerializer.serialize_get_declarative_policies_report_summary_response,
            "StartDeclarativePoliciesReport": declarativepolicyaccountstatusreport_ResponseSerializer.serialize_start_declarative_policies_report_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

