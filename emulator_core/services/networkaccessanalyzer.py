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
class NetworkAccessAnalyzer:
    analyzed_eni_count: int = 0
    end_date: str = ""
    findings_found: str = ""
    network_insights_access_scope_analysis_arn: str = ""
    network_insights_access_scope_analysis_id: str = ""
    network_insights_access_scope_id: str = ""
    start_date: str = ""
    status: str = ""
    status_message: str = ""
    tag_set: List[Any] = field(default_factory=list)
    warning_message: str = ""

    resource_type: str = ""
    created_date: str = ""
    updated_date: str = ""
    network_insights_access_scope_arn: str = ""
    exclude_path_set: List[Any] = field(default_factory=list)
    match_path_set: List[Any] = field(default_factory=list)
    analysis_findings: List[Dict[str, Any]] = field(default_factory=list)
    analysis_status: List[str] = field(default_factory=list)
    client_token: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analyzedEniCount": self.analyzed_eni_count,
            "endDate": self.end_date,
            "findingsFound": self.findings_found,
            "networkInsightsAccessScopeAnalysisArn": self.network_insights_access_scope_analysis_arn,
            "networkInsightsAccessScopeAnalysisId": self.network_insights_access_scope_analysis_id,
            "networkInsightsAccessScopeId": self.network_insights_access_scope_id,
            "startDate": self.start_date,
            "status": self.status,
            "statusMessage": self.status_message,
            "tagSet": self.tag_set,
            "warningMessage": self.warning_message,
            "createdDate": self.created_date,
            "updatedDate": self.updated_date,
            "networkInsightsAccessScopeArn": self.network_insights_access_scope_arn,
            "excludePathSet": self.exclude_path_set,
            "matchPathSet": self.match_path_set,
            "analysisFindingSet": self.analysis_findings,
            "analysisStatus": self.analysis_status,
        }

class NetworkAccessAnalyzer_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.network_access_analyzer  # alias to shared store

    def _now_isoformat(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _build_access_scope_arn(self, scope_id: str) -> str:
        return f"arn:aws:ec2:::network-insights-access-scope/{scope_id}"

    def _build_access_scope_analysis_arn(self, analysis_id: str) -> str:
        return f"arn:aws:ec2:::network-insights-access-scope-analysis/{analysis_id}"

    def _get_scope_or_error(self, scope_id: str):
        scope = self.resources.get(scope_id)
        if not scope or scope.resource_type != "scope":
            return create_error_response(
                "InvalidNetworkInsightsAccessScopeId.NotFound",
                f"The ID '{scope_id}' does not exist",
            )
        return scope

    def _get_analysis_or_error(self, analysis_id: str):
        analysis = self.resources.get(analysis_id)
        if not analysis or analysis.resource_type != "analysis":
            return create_error_response(
                "InvalidNetworkInsightsAccessScopeAnalysisId.NotFound",
                f"The ID '{analysis_id}' does not exist",
            )
        return analysis

    def CreateNetworkInsightsAccessScope(self, params: Dict[str, Any]):
        """Creates a Network Access Scope. AWS Network Access Analyzer enables cloud networking and cloud operations teams 
         to verify that their networks on AWS conform to their network security and governance 
         objectives. For more information, see theAWS Network Access Analyzer Guide."""

        client_token = params.get("ClientToken")
        if not client_token:
            return create_error_response("MissingParameter", "Missing required parameter: ClientToken")

        tag_set = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "network-insights-access-scope":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        exclude_path_set = params.get("ExcludePath.N", []) or []
        match_path_set = params.get("MatchPath.N", []) or []
        now = self._now_isoformat()
        scope_id = self._generate_id("nisa")
        scope_arn = self._build_access_scope_arn(scope_id)

        resource = NetworkAccessAnalyzer(
            resource_type="scope",
            network_insights_access_scope_id=scope_id,
            network_insights_access_scope_arn=scope_arn,
            created_date=now,
            updated_date=now,
            exclude_path_set=exclude_path_set,
            match_path_set=match_path_set,
            tag_set=tag_set,
            client_token=client_token,
        )
        self.resources[scope_id] = resource

        return {
            'networkInsightsAccessScope': {
                'createdDate': now,
                'networkInsightsAccessScopeArn': scope_arn,
                'networkInsightsAccessScopeId': scope_id,
                'tagSet': tag_set,
                'updatedDate': now,
                },
            'networkInsightsAccessScopeContent': {
                'excludePathSet': exclude_path_set,
                'matchPathSet': match_path_set,
                'networkInsightsAccessScopeId': scope_id,
                },
            }

    def DeleteNetworkInsightsAccessScope(self, params: Dict[str, Any]):
        """Deletes the specified Network Access Scope."""

        scope_id = params.get("NetworkInsightsAccessScopeId")
        if not scope_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: NetworkInsightsAccessScopeId",
            )

        scope = self._get_scope_or_error(scope_id)
        if is_error_response(scope):
            return scope

        del self.resources[scope_id]

        return {
            'networkInsightsAccessScopeId': scope_id,
            }

    def DeleteNetworkInsightsAccessScopeAnalysis(self, params: Dict[str, Any]):
        """Deletes the specified Network Access Scope analysis."""

        analysis_id = params.get("NetworkInsightsAccessScopeAnalysisId")
        if not analysis_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: NetworkInsightsAccessScopeAnalysisId",
            )

        analysis = self._get_analysis_or_error(analysis_id)
        if is_error_response(analysis):
            return analysis

        del self.resources[analysis_id]

        return {
            'networkInsightsAccessScopeAnalysisId': analysis_id,
            }

    def DescribeNetworkInsightsAccessScopeAnalyses(self, params: Dict[str, Any]):
        """Describes the specified Network Access Scope analyses."""

        analysis_ids = params.get("NetworkInsightsAccessScopeAnalysisId.N", []) or []
        scope_id = params.get("NetworkInsightsAccessScopeId")
        max_results = int(params.get("MaxResults") or 100)

        if scope_id:
            scope = self._get_scope_or_error(scope_id)
            if is_error_response(scope):
                return scope

        if analysis_ids:
            resources = []
            for analysis_id in analysis_ids:
                analysis = self._get_analysis_or_error(analysis_id)
                if is_error_response(analysis):
                    return analysis
                resources.append(analysis)
        else:
            resources = [
                resource for resource in self.resources.values()
                if resource.resource_type == "analysis"
            ]

        if scope_id:
            resources = [
                analysis for analysis in resources
                if analysis.network_insights_access_scope_id == scope_id
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))

        analysis_start_time_begin = params.get("AnalysisStartTimeBegin")
        analysis_start_time_end = params.get("AnalysisStartTimeEnd")
        if analysis_start_time_begin or analysis_start_time_end:
            def _parse_dt(value: str):
                try:
                    return datetime.fromisoformat(value)
                except Exception:
                    return None

            begin_dt = _parse_dt(analysis_start_time_begin) if analysis_start_time_begin else None
            end_dt = _parse_dt(analysis_start_time_end) if analysis_start_time_end else None
            filtered = []
            for analysis in resources:
                start_dt = _parse_dt(analysis.start_date) if analysis.start_date else None
                if start_dt is None:
                    continue
                if begin_dt and start_dt < begin_dt:
                    continue
                if end_dt and start_dt > end_dt:
                    continue
                filtered.append(analysis)
            resources = filtered

        analysis_set = []
        for analysis in resources[:max_results]:
            analysis_set.append({
                'analyzedEniCount': analysis.analyzed_eni_count,
                'endDate': analysis.end_date,
                'findingsFound': analysis.findings_found,
                'networkInsightsAccessScopeAnalysisArn': analysis.network_insights_access_scope_analysis_arn,
                'networkInsightsAccessScopeAnalysisId': analysis.network_insights_access_scope_analysis_id,
                'networkInsightsAccessScopeId': analysis.network_insights_access_scope_id,
                'startDate': analysis.start_date,
                'status': analysis.status,
                'statusMessage': analysis.status_message,
                'tagSet': analysis.tag_set,
                'warningMessage': analysis.warning_message,
            })

        return {
            'networkInsightsAccessScopeAnalysisSet': analysis_set,
            'nextToken': None,
            }

    def DescribeNetworkInsightsAccessScopes(self, params: Dict[str, Any]):
        """Describes the specified Network Access Scopes."""

        scope_ids = params.get("NetworkInsightsAccessScopeId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if scope_ids:
            resources = []
            for scope_id in scope_ids:
                scope = self._get_scope_or_error(scope_id)
                if is_error_response(scope):
                    return scope
                resources.append(scope)
        else:
            resources = [
                resource for resource in self.resources.values()
                if resource.resource_type == "scope"
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))

        scope_set = []
        for scope in resources[:max_results]:
            scope_set.append({
                'createdDate': scope.created_date,
                'networkInsightsAccessScopeArn': scope.network_insights_access_scope_arn,
                'networkInsightsAccessScopeId': scope.network_insights_access_scope_id,
                'tagSet': scope.tag_set,
                'updatedDate': scope.updated_date,
            })

        return {
            'networkInsightsAccessScopeSet': scope_set,
            'nextToken': None,
            }

    def GetNetworkInsightsAccessScopeAnalysisFindings(self, params: Dict[str, Any]):
        """Gets the findings for the specified Network Access Scope analysis."""

        analysis_id = params.get("NetworkInsightsAccessScopeAnalysisId")
        if not analysis_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: NetworkInsightsAccessScopeAnalysisId",
            )

        analysis = self._get_analysis_or_error(analysis_id)
        if is_error_response(analysis):
            return analysis

        max_results = int(params.get("MaxResults") or 100)
        findings = list(analysis.analysis_findings or [])

        return {
            'analysisFindingSet': findings[:max_results],
            'analysisStatus': list(analysis.analysis_status or []),
            'networkInsightsAccessScopeAnalysisId': analysis.network_insights_access_scope_analysis_id,
            'nextToken': None,
            }

    def GetNetworkInsightsAccessScopeContent(self, params: Dict[str, Any]):
        """Gets the content for the specified Network Access Scope."""

        scope_id = params.get("NetworkInsightsAccessScopeId")
        if not scope_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: NetworkInsightsAccessScopeId",
            )

        scope = self._get_scope_or_error(scope_id)
        if is_error_response(scope):
            return scope

        return {
            'networkInsightsAccessScopeContent': {
                'excludePathSet': list(scope.exclude_path_set or []),
                'matchPathSet': list(scope.match_path_set or []),
                'networkInsightsAccessScopeId': scope.network_insights_access_scope_id,
                },
            }

    def StartNetworkInsightsAccessScopeAnalysis(self, params: Dict[str, Any]):
        """Starts analyzing the specified Network Access Scope."""

        client_token = params.get("ClientToken")
        if not client_token:
            return create_error_response("MissingParameter", "Missing required parameter: ClientToken")

        scope_id = params.get("NetworkInsightsAccessScopeId")
        if not scope_id:
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: NetworkInsightsAccessScopeId",
            )

        scope = self._get_scope_or_error(scope_id)
        if is_error_response(scope):
            return scope

        tag_set = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "network-insights-access-scope-analysis":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        start_date = self._now_isoformat()
        analysis_id = self._generate_id("nisaa")
        analysis_arn = self._build_access_scope_analysis_arn(analysis_id)

        resource = NetworkAccessAnalyzer(
            resource_type="analysis",
            network_insights_access_scope_analysis_id=analysis_id,
            network_insights_access_scope_analysis_arn=analysis_arn,
            network_insights_access_scope_id=scope_id,
            start_date=start_date,
            end_date=start_date,
            status="succeeded",
            status_message="",
            findings_found="false",
            warning_message="",
            analyzed_eni_count=0,
            tag_set=tag_set,
            analysis_findings=[],
            analysis_status=["succeeded"],
            client_token=client_token,
        )
        self.resources[analysis_id] = resource

        return {
            'networkInsightsAccessScopeAnalysis': {
                'analyzedEniCount': resource.analyzed_eni_count,
                'endDate': resource.end_date,
                'findingsFound': resource.findings_found,
                'networkInsightsAccessScopeAnalysisArn': resource.network_insights_access_scope_analysis_arn,
                'networkInsightsAccessScopeAnalysisId': resource.network_insights_access_scope_analysis_id,
                'networkInsightsAccessScopeId': resource.network_insights_access_scope_id,
                'startDate': resource.start_date,
                'status': resource.status,
                'statusMessage': resource.status_message,
                'tagSet': resource.tag_set,
                'warningMessage': resource.warning_message,
                },
            }

    def _generate_id(self, prefix: str = 'eni') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class networkaccessanalyzer_RequestParser:
    @staticmethod
    def parse_create_network_insights_access_scope_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ExcludePath.N": get_indexed_list(md, "ExcludePath"),
            "MatchPath.N": get_indexed_list(md, "MatchPath"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_network_insights_access_scope_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkInsightsAccessScopeId": get_scalar(md, "NetworkInsightsAccessScopeId"),
        }

    @staticmethod
    def parse_delete_network_insights_access_scope_analysis_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkInsightsAccessScopeAnalysisId": get_scalar(md, "NetworkInsightsAccessScopeAnalysisId"),
        }

    @staticmethod
    def parse_describe_network_insights_access_scope_analyses_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AnalysisStartTimeBegin": get_scalar(md, "AnalysisStartTimeBegin"),
            "AnalysisStartTimeEnd": get_scalar(md, "AnalysisStartTimeEnd"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NetworkInsightsAccessScopeAnalysisId.N": get_indexed_list(md, "NetworkInsightsAccessScopeAnalysisId"),
            "NetworkInsightsAccessScopeId": get_scalar(md, "NetworkInsightsAccessScopeId"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_network_insights_access_scopes_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NetworkInsightsAccessScopeId.N": get_indexed_list(md, "NetworkInsightsAccessScopeId"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_network_insights_access_scope_analysis_findings_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NetworkInsightsAccessScopeAnalysisId": get_scalar(md, "NetworkInsightsAccessScopeAnalysisId"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_get_network_insights_access_scope_content_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkInsightsAccessScopeId": get_scalar(md, "NetworkInsightsAccessScopeId"),
        }

    @staticmethod
    def parse_start_network_insights_access_scope_analysis_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkInsightsAccessScopeId": get_scalar(md, "NetworkInsightsAccessScopeId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateNetworkInsightsAccessScope": networkaccessanalyzer_RequestParser.parse_create_network_insights_access_scope_request,
            "DeleteNetworkInsightsAccessScope": networkaccessanalyzer_RequestParser.parse_delete_network_insights_access_scope_request,
            "DeleteNetworkInsightsAccessScopeAnalysis": networkaccessanalyzer_RequestParser.parse_delete_network_insights_access_scope_analysis_request,
            "DescribeNetworkInsightsAccessScopeAnalyses": networkaccessanalyzer_RequestParser.parse_describe_network_insights_access_scope_analyses_request,
            "DescribeNetworkInsightsAccessScopes": networkaccessanalyzer_RequestParser.parse_describe_network_insights_access_scopes_request,
            "GetNetworkInsightsAccessScopeAnalysisFindings": networkaccessanalyzer_RequestParser.parse_get_network_insights_access_scope_analysis_findings_request,
            "GetNetworkInsightsAccessScopeContent": networkaccessanalyzer_RequestParser.parse_get_network_insights_access_scope_content_request,
            "StartNetworkInsightsAccessScopeAnalysis": networkaccessanalyzer_RequestParser.parse_start_network_insights_access_scope_analysis_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class networkaccessanalyzer_ResponseSerializer:
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
                xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_network_insights_access_scope_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateNetworkInsightsAccessScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAccessScope
        _networkInsightsAccessScope_key = None
        if "networkInsightsAccessScope" in data:
            _networkInsightsAccessScope_key = "networkInsightsAccessScope"
        elif "NetworkInsightsAccessScope" in data:
            _networkInsightsAccessScope_key = "NetworkInsightsAccessScope"
        if _networkInsightsAccessScope_key:
            param_data = data[_networkInsightsAccessScope_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsAccessScope>')
            xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</networkInsightsAccessScope>')
        # Serialize networkInsightsAccessScopeContent
        _networkInsightsAccessScopeContent_key = None
        if "networkInsightsAccessScopeContent" in data:
            _networkInsightsAccessScopeContent_key = "networkInsightsAccessScopeContent"
        elif "NetworkInsightsAccessScopeContent" in data:
            _networkInsightsAccessScopeContent_key = "NetworkInsightsAccessScopeContent"
        if _networkInsightsAccessScopeContent_key:
            param_data = data[_networkInsightsAccessScopeContent_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsAccessScopeContent>')
            xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</networkInsightsAccessScopeContent>')
        xml_parts.append(f'</CreateNetworkInsightsAccessScopeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_network_insights_access_scope_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteNetworkInsightsAccessScopeResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAccessScopeId
        _networkInsightsAccessScopeId_key = None
        if "networkInsightsAccessScopeId" in data:
            _networkInsightsAccessScopeId_key = "networkInsightsAccessScopeId"
        elif "NetworkInsightsAccessScopeId" in data:
            _networkInsightsAccessScopeId_key = "NetworkInsightsAccessScopeId"
        if _networkInsightsAccessScopeId_key:
            param_data = data[_networkInsightsAccessScopeId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsAccessScopeId>{esc(str(param_data))}</networkInsightsAccessScopeId>')
        xml_parts.append(f'</DeleteNetworkInsightsAccessScopeResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_network_insights_access_scope_analysis_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteNetworkInsightsAccessScopeAnalysisResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAccessScopeAnalysisId
        _networkInsightsAccessScopeAnalysisId_key = None
        if "networkInsightsAccessScopeAnalysisId" in data:
            _networkInsightsAccessScopeAnalysisId_key = "networkInsightsAccessScopeAnalysisId"
        elif "NetworkInsightsAccessScopeAnalysisId" in data:
            _networkInsightsAccessScopeAnalysisId_key = "NetworkInsightsAccessScopeAnalysisId"
        if _networkInsightsAccessScopeAnalysisId_key:
            param_data = data[_networkInsightsAccessScopeAnalysisId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsAccessScopeAnalysisId>{esc(str(param_data))}</networkInsightsAccessScopeAnalysisId>')
        xml_parts.append(f'</DeleteNetworkInsightsAccessScopeAnalysisResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_network_insights_access_scope_analyses_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeNetworkInsightsAccessScopeAnalysesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAccessScopeAnalysisSet
        _networkInsightsAccessScopeAnalysisSet_key = None
        if "networkInsightsAccessScopeAnalysisSet" in data:
            _networkInsightsAccessScopeAnalysisSet_key = "networkInsightsAccessScopeAnalysisSet"
        elif "NetworkInsightsAccessScopeAnalysisSet" in data:
            _networkInsightsAccessScopeAnalysisSet_key = "NetworkInsightsAccessScopeAnalysisSet"
        elif "NetworkInsightsAccessScopeAnalysiss" in data:
            _networkInsightsAccessScopeAnalysisSet_key = "NetworkInsightsAccessScopeAnalysiss"
        if _networkInsightsAccessScopeAnalysisSet_key:
            param_data = data[_networkInsightsAccessScopeAnalysisSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<networkInsightsAccessScopeAnalysisSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</networkInsightsAccessScopeAnalysisSet>')
            else:
                xml_parts.append(f'{indent_str}<networkInsightsAccessScopeAnalysisSet/>')
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
        xml_parts.append(f'</DescribeNetworkInsightsAccessScopeAnalysesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_network_insights_access_scopes_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeNetworkInsightsAccessScopesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAccessScopeSet
        _networkInsightsAccessScopeSet_key = None
        if "networkInsightsAccessScopeSet" in data:
            _networkInsightsAccessScopeSet_key = "networkInsightsAccessScopeSet"
        elif "NetworkInsightsAccessScopeSet" in data:
            _networkInsightsAccessScopeSet_key = "NetworkInsightsAccessScopeSet"
        elif "NetworkInsightsAccessScopes" in data:
            _networkInsightsAccessScopeSet_key = "NetworkInsightsAccessScopes"
        if _networkInsightsAccessScopeSet_key:
            param_data = data[_networkInsightsAccessScopeSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<networkInsightsAccessScopeSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</networkInsightsAccessScopeSet>')
            else:
                xml_parts.append(f'{indent_str}<networkInsightsAccessScopeSet/>')
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
        xml_parts.append(f'</DescribeNetworkInsightsAccessScopesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_network_insights_access_scope_analysis_findings_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetNetworkInsightsAccessScopeAnalysisFindingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize analysisFindingSet
        _analysisFindingSet_key = None
        if "analysisFindingSet" in data:
            _analysisFindingSet_key = "analysisFindingSet"
        elif "AnalysisFindingSet" in data:
            _analysisFindingSet_key = "AnalysisFindingSet"
        elif "AnalysisFindings" in data:
            _analysisFindingSet_key = "AnalysisFindings"
        if _analysisFindingSet_key:
            param_data = data[_analysisFindingSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<analysisFindingSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</analysisFindingSet>')
            else:
                xml_parts.append(f'{indent_str}<analysisFindingSet/>')
        # Serialize analysisStatus
        _analysisStatus_key = None
        if "analysisStatus" in data:
            _analysisStatus_key = "analysisStatus"
        elif "AnalysisStatus" in data:
            _analysisStatus_key = "AnalysisStatus"
        if _analysisStatus_key:
            param_data = data[_analysisStatus_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<analysisStatusSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>{esc(str(item))}</item>')
                xml_parts.append(f'{indent_str}</analysisStatusSet>')
            else:
                xml_parts.append(f'{indent_str}<analysisStatusSet/>')
        # Serialize networkInsightsAccessScopeAnalysisId
        _networkInsightsAccessScopeAnalysisId_key = None
        if "networkInsightsAccessScopeAnalysisId" in data:
            _networkInsightsAccessScopeAnalysisId_key = "networkInsightsAccessScopeAnalysisId"
        elif "NetworkInsightsAccessScopeAnalysisId" in data:
            _networkInsightsAccessScopeAnalysisId_key = "NetworkInsightsAccessScopeAnalysisId"
        if _networkInsightsAccessScopeAnalysisId_key:
            param_data = data[_networkInsightsAccessScopeAnalysisId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsAccessScopeAnalysisId>{esc(str(param_data))}</networkInsightsAccessScopeAnalysisId>')
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
        xml_parts.append(f'</GetNetworkInsightsAccessScopeAnalysisFindingsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_network_insights_access_scope_content_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetNetworkInsightsAccessScopeContentResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAccessScopeContent
        _networkInsightsAccessScopeContent_key = None
        if "networkInsightsAccessScopeContent" in data:
            _networkInsightsAccessScopeContent_key = "networkInsightsAccessScopeContent"
        elif "NetworkInsightsAccessScopeContent" in data:
            _networkInsightsAccessScopeContent_key = "NetworkInsightsAccessScopeContent"
        if _networkInsightsAccessScopeContent_key:
            param_data = data[_networkInsightsAccessScopeContent_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsAccessScopeContent>')
            xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</networkInsightsAccessScopeContent>')
        xml_parts.append(f'</GetNetworkInsightsAccessScopeContentResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_start_network_insights_access_scope_analysis_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<StartNetworkInsightsAccessScopeAnalysisResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAccessScopeAnalysis
        _networkInsightsAccessScopeAnalysis_key = None
        if "networkInsightsAccessScopeAnalysis" in data:
            _networkInsightsAccessScopeAnalysis_key = "networkInsightsAccessScopeAnalysis"
        elif "NetworkInsightsAccessScopeAnalysis" in data:
            _networkInsightsAccessScopeAnalysis_key = "NetworkInsightsAccessScopeAnalysis"
        if _networkInsightsAccessScopeAnalysis_key:
            param_data = data[_networkInsightsAccessScopeAnalysis_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<networkInsightsAccessScopeAnalysisSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(networkaccessanalyzer_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</networkInsightsAccessScopeAnalysisSet>')
            else:
                xml_parts.append(f'{indent_str}<networkInsightsAccessScopeAnalysisSet/>')
        xml_parts.append(f'</StartNetworkInsightsAccessScopeAnalysisResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateNetworkInsightsAccessScope": networkaccessanalyzer_ResponseSerializer.serialize_create_network_insights_access_scope_response,
            "DeleteNetworkInsightsAccessScope": networkaccessanalyzer_ResponseSerializer.serialize_delete_network_insights_access_scope_response,
            "DeleteNetworkInsightsAccessScopeAnalysis": networkaccessanalyzer_ResponseSerializer.serialize_delete_network_insights_access_scope_analysis_response,
            "DescribeNetworkInsightsAccessScopeAnalyses": networkaccessanalyzer_ResponseSerializer.serialize_describe_network_insights_access_scope_analyses_response,
            "DescribeNetworkInsightsAccessScopes": networkaccessanalyzer_ResponseSerializer.serialize_describe_network_insights_access_scopes_response,
            "GetNetworkInsightsAccessScopeAnalysisFindings": networkaccessanalyzer_ResponseSerializer.serialize_get_network_insights_access_scope_analysis_findings_response,
            "GetNetworkInsightsAccessScopeContent": networkaccessanalyzer_ResponseSerializer.serialize_get_network_insights_access_scope_content_response,
            "StartNetworkInsightsAccessScopeAnalysis": networkaccessanalyzer_ResponseSerializer.serialize_start_network_insights_access_scope_analysis_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

