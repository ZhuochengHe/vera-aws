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
class ReachabilityAnalyzer:
    additional_account_set: List[Any] = field(default_factory=list)
    alternate_path_hint_set: List[Any] = field(default_factory=list)
    explanation_set: List[Any] = field(default_factory=list)
    filter_in_arn_set: List[Any] = field(default_factory=list)
    filter_out_arn_set: List[Any] = field(default_factory=list)
    forward_path_component_set: List[Any] = field(default_factory=list)
    network_insights_analysis_arn: str = ""
    network_insights_analysis_id: str = ""
    network_insights_path_id: str = ""
    network_path_found: bool = False
    return_path_component_set: List[Any] = field(default_factory=list)
    start_date: str = ""
    status: str = ""
    status_message: str = ""
    suggested_account_set: List[Any] = field(default_factory=list)
    tag_set: List[Any] = field(default_factory=list)
    warning_message: str = ""

    created_date: str = ""
    destination: str = ""
    destination_arn: str = ""
    destination_ip: str = ""
    destination_port: Optional[int] = None
    filter_at_destination: Dict[str, Any] = field(default_factory=dict)
    filter_at_source: Dict[str, Any] = field(default_factory=dict)
    network_insights_path_arn: str = ""
    protocol: str = ""
    source: str = ""
    source_arn: str = ""
    source_ip: str = ""
    resource_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "additionalAccountSet": self.additional_account_set,
            "alternatePathHintSet": self.alternate_path_hint_set,
            "explanationSet": self.explanation_set,
            "filterInArnSet": self.filter_in_arn_set,
            "filterOutArnSet": self.filter_out_arn_set,
            "forwardPathComponentSet": self.forward_path_component_set,
            "networkInsightsAnalysisArn": self.network_insights_analysis_arn,
            "networkInsightsAnalysisId": self.network_insights_analysis_id,
            "networkInsightsPathId": self.network_insights_path_id,
            "networkPathFound": self.network_path_found,
            "returnPathComponentSet": self.return_path_component_set,
            "startDate": self.start_date,
            "status": self.status,
            "statusMessage": self.status_message,
            "suggestedAccountSet": self.suggested_account_set,
            "tagSet": self.tag_set,
            "warningMessage": self.warning_message,
            "createdDate": self.created_date,
            "destination": self.destination,
            "destinationArn": self.destination_arn,
            "destinationIp": self.destination_ip,
            "destinationPort": self.destination_port,
            "filterAtDestination": self.filter_at_destination,
            "filterAtSource": self.filter_at_source,
            "networkInsightsPathArn": self.network_insights_path_arn,
            "protocol": self.protocol,
            "source": self.source,
            "sourceArn": self.source_arn,
            "sourceIp": self.source_ip,
        }

class ReachabilityAnalyzer_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.reachability_analyzer  # alias to shared store

    def _utcnow(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(
        self,
        resource_id: str,
        error_code: str,
        message: str,
        expected_type: Optional[str] = None,
    ) -> (Optional[ReachabilityAnalyzer], Optional[Dict[str, Any]]):
        resource = self.resources.get(resource_id)
        if not resource or (expected_type and resource.resource_type != expected_type):
            return None, create_error_response(error_code, message)
        return resource, None

    def _build_analysis_dict(self, resource: ReachabilityAnalyzer) -> Dict[str, Any]:
        return {
            "additionalAccountSet": resource.additional_account_set,
            "alternatePathHintSet": resource.alternate_path_hint_set,
            "explanationSet": resource.explanation_set,
            "filterInArnSet": resource.filter_in_arn_set,
            "filterOutArnSet": resource.filter_out_arn_set,
            "forwardPathComponentSet": resource.forward_path_component_set,
            "networkInsightsAnalysisArn": resource.network_insights_analysis_arn,
            "networkInsightsAnalysisId": resource.network_insights_analysis_id,
            "networkInsightsPathId": resource.network_insights_path_id,
            "networkPathFound": resource.network_path_found,
            "returnPathComponentSet": resource.return_path_component_set,
            "startDate": resource.start_date,
            "status": resource.status,
            "statusMessage": resource.status_message,
            "suggestedAccountSet": resource.suggested_account_set,
            "tagSet": resource.tag_set,
            "warningMessage": resource.warning_message,
        }

    def _build_path_dict(self, resource: ReachabilityAnalyzer) -> Dict[str, Any]:
        return {
            "createdDate": resource.created_date,
            "destination": resource.destination,
            "destinationArn": resource.destination_arn,
            "destinationIp": resource.destination_ip,
            "destinationPort": resource.destination_port,
            "filterAtDestination": resource.filter_at_destination,
            "filterAtSource": resource.filter_at_source,
            "networkInsightsPathArn": resource.network_insights_path_arn,
            "networkInsightsPathId": resource.network_insights_path_id,
            "protocol": resource.protocol,
            "source": resource.source,
            "sourceArn": resource.source_arn,
            "sourceIp": resource.source_ip,
            "tagSet": resource.tag_set,
        }

    def CreateNetworkInsightsPath(self, params: Dict[str, Any]):
        """Creates a path to analyze for reachability. Reachability Analyzer enables you to analyze and debug network reachability between
          two resources in your virtual private cloud (VPC). For more information, see theReachability Analyzer Guide."""

        error = self._require_params(params, ["ClientToken", "Protocol", "Source"])
        if error:
            return error

        source = params.get("Source") or ""
        destination = params.get("Destination") or ""

        def _validate_endpoint(endpoint: str, label: str) -> Optional[Dict[str, Any]]:
            if not endpoint:
                return None
            prefix = endpoint.split("-")[0]
            store_map = {
                "i": self.state.instances,
                "eni": self.state.elastic_network_interfaces,
                "subnet": self.state.subnets,
                "vpc": self.state.vpcs,
                "igw": self.state.internet_gateways,
                "nat": self.state.nat_gateways,
                "tgw": self.state.transit_gateways,
                "vgw": self.state.virtual_private_gateways,
                "vpn": self.state.vpn_connections,
                "cgw": self.state.customer_gateways,
                "pcx": self.state.vpc_peering,
                "vpce": self.state.vpc_endpoints,
            }
            error_code_map = {
                "i": "InvalidInstanceID.NotFound",
                "eni": "InvalidNetworkInterfaceID.NotFound",
                "subnet": "InvalidSubnetID.NotFound",
                "vpc": "InvalidVpcID.NotFound",
                "igw": "InvalidInternetGatewayID.NotFound",
                "nat": "InvalidNatGatewayID.NotFound",
                "tgw": "InvalidTransitGatewayID.NotFound",
                "vgw": "InvalidVpnGatewayID.NotFound",
                "vpn": "InvalidVpnConnectionID.NotFound",
                "cgw": "InvalidCustomerGatewayID.NotFound",
                "pcx": "InvalidVpcPeeringConnectionID.NotFound",
                "vpce": "InvalidVpcEndpointID.NotFound",
            }
            store = store_map.get(prefix)
            if store is None:
                return None
            if endpoint not in store:
                return create_error_response(error_code_map[prefix], f"The ID '{endpoint}' does not exist")
            return None

        error = _validate_endpoint(source, "Source")
        if error:
            return error
        error = _validate_endpoint(destination, "Destination")
        if error:
            return error

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "network-insights-path":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        path_id = self._generate_id("nip")
        path_arn = f"arn:aws:ec2:::network-insights-path/{path_id}"
        created_date = self._utcnow()
        source_arn = source if source.startswith("arn:") else ""
        destination_arn = destination if destination.startswith("arn:") else ""

        resource = ReachabilityAnalyzer(
            resource_type="path",
            network_insights_path_id=path_id,
            network_insights_path_arn=path_arn,
            created_date=created_date,
            destination=destination,
            destination_arn=destination_arn,
            destination_ip=params.get("DestinationIp") or "",
            destination_port=params.get("DestinationPort"),
            filter_at_destination=params.get("FilterAtDestination") or {},
            filter_at_source=params.get("FilterAtSource") or {},
            protocol=params.get("Protocol") or "",
            source=source,
            source_arn=source_arn,
            source_ip=params.get("SourceIp") or "",
            tag_set=tag_set,
        )
        self.resources[path_id] = resource

        return {
            "networkInsightsPath": self._build_path_dict(resource),
        }

    def DeleteNetworkInsightsAnalysis(self, params: Dict[str, Any]):
        """Deletes the specified network insights analysis."""

        error = self._require_params(params, ["NetworkInsightsAnalysisId"])
        if error:
            return error

        analysis_id = params.get("NetworkInsightsAnalysisId") or ""
        resource, error = self._get_resource_or_error(
            analysis_id,
            "InvalidNetworkInsightsAnalysisId.NotFound",
            f"The ID '{analysis_id}' does not exist",
            expected_type="analysis",
        )
        if error:
            return error

        if resource:
            self.resources.pop(analysis_id, None)

        return {
            "networkInsightsAnalysisId": analysis_id,
        }

    def DeleteNetworkInsightsPath(self, params: Dict[str, Any]):
        """Deletes the specified path."""

        error = self._require_params(params, ["NetworkInsightsPathId"])
        if error:
            return error

        path_id = params.get("NetworkInsightsPathId") or ""
        resource, error = self._get_resource_or_error(
            path_id,
            "InvalidNetworkInsightsPathId.NotFound",
            f"The ID '{path_id}' does not exist",
            expected_type="path",
        )
        if error:
            return error

        if resource:
            self.resources.pop(path_id, None)

        return {
            "networkInsightsPathId": path_id,
        }

    def DescribeNetworkInsightsAnalyses(self, params: Dict[str, Any]):
        """Describes one or more of your network insights analyses."""

        analysis_ids = params.get("NetworkInsightsAnalysisId.N", []) or []
        path_id = params.get("NetworkInsightsPathId")
        max_results = int(params.get("MaxResults") or 100)

        if path_id:
            _, error = self._get_resource_or_error(
                path_id,
                "InvalidNetworkInsightsPathId.NotFound",
                f"The ID '{path_id}' does not exist",
                expected_type="path",
            )
            if error:
                return error

        if analysis_ids:
            resources = []
            for analysis_id in analysis_ids:
                analysis, error = self._get_resource_or_error(
                    analysis_id,
                    "InvalidNetworkInsightsAnalysisId.NotFound",
                    f"The ID '{analysis_id}' does not exist",
                    expected_type="analysis",
                )
                if error:
                    return error
                resources.append(analysis)
        else:
            resources = [
                resource for resource in self.resources.values()
                if resource.resource_type == "analysis"
            ]

        if path_id:
            resources = [
                resource for resource in resources
                if resource.network_insights_path_id == path_id
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))

        analysis_start_time = params.get("AnalysisStartTime")
        analysis_end_time = params.get("AnalysisEndTime")
        if analysis_start_time or analysis_end_time:
            def _parse_dt(value: str):
                try:
                    return datetime.fromisoformat(value)
                except Exception:
                    return None

            start_dt = _parse_dt(analysis_start_time) if analysis_start_time else None
            end_dt = _parse_dt(analysis_end_time) if analysis_end_time else None
            filtered = []
            for analysis in resources:
                analysis_dt = _parse_dt(analysis.start_date) if analysis.start_date else None
                if analysis_dt is None:
                    continue
                if start_dt and analysis_dt < start_dt:
                    continue
                if end_dt and analysis_dt > end_dt:
                    continue
                filtered.append(analysis)
            resources = filtered

        analysis_set = [
            self._build_analysis_dict(resource)
            for resource in resources[:max_results]
        ]

        return {
            "networkInsightsAnalysisSet": analysis_set,
            "nextToken": None,
        }

    def DescribeNetworkInsightsPaths(self, params: Dict[str, Any]):
        """Describes one or more of your paths."""

        path_ids = params.get("NetworkInsightsPathId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if path_ids:
            resources = []
            for path_id in path_ids:
                resource, error = self._get_resource_or_error(
                    path_id,
                    "InvalidNetworkInsightsPathId.NotFound",
                    f"The ID '{path_id}' does not exist",
                    expected_type="path",
                )
                if error:
                    return error
                resources.append(resource)
        else:
            resources = [
                resource for resource in self.resources.values()
                if resource.resource_type == "path"
            ]

        resources = apply_filters(resources, params.get("Filter.N", []))

        path_set = [
            self._build_path_dict(resource)
            for resource in resources[:max_results]
        ]

        return {
            "networkInsightsPathSet": path_set,
            "nextToken": None,
        }

    def EnableReachabilityAnalyzerOrganizationSharing(self, params: Dict[str, Any]):
        """Establishes a trust relationship between Reachability Analyzer and AWS Organizations.
         This operation must be performed by the management account for the organization. After you establish a trust relationship, a user in the management account or 
         a delegated administrator account ca"""

        if not hasattr(self.state, "reachability_analyzer_org_sharing"):
            setattr(self.state, "reachability_analyzer_org_sharing", False)

        self.state.reachability_analyzer_org_sharing = True

        return {
            "returnValue": True,
        }

    def StartNetworkInsightsAnalysis(self, params: Dict[str, Any]):
        """Starts analyzing the specified path. If the path is reachable, the
         operation returns the shortest feasible path."""

        error = self._require_params(params, ["ClientToken", "NetworkInsightsPathId"])
        if error:
            return error

        path_id = params.get("NetworkInsightsPathId") or ""
        _, error = self._get_resource_or_error(
            path_id,
            "InvalidNetworkInsightsPathId.NotFound",
            f"The ID '{path_id}' does not exist",
            expected_type="path",
        )
        if error:
            return error

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != "network-insights-analysis":
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tag_set.append(tag)

        analysis_id = self._generate_id("nia")
        analysis_arn = f"arn:aws:ec2:::network-insights-analysis/{analysis_id}"
        start_date = self._utcnow()

        resource = ReachabilityAnalyzer(
            resource_type="analysis",
            network_insights_analysis_id=analysis_id,
            network_insights_analysis_arn=analysis_arn,
            network_insights_path_id=path_id,
            additional_account_set=params.get("AdditionalAccount.N", []) or [],
            alternate_path_hint_set=[],
            explanation_set=[],
            filter_in_arn_set=params.get("FilterInArn.N", []) or [],
            filter_out_arn_set=params.get("FilterOutArn.N", []) or [],
            forward_path_component_set=[],
            network_path_found=False,
            return_path_component_set=[],
            start_date=start_date,
            status="succeeded",
            status_message="",
            suggested_account_set=[],
            tag_set=tag_set,
            warning_message="",
        )
        self.resources[analysis_id] = resource

        return {
            "networkInsightsAnalysis": self._build_analysis_dict(resource),
        }

    def _generate_id(self, prefix: str = 'eni') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class reachabilityanalyzer_RequestParser:
    @staticmethod
    def parse_create_network_insights_path_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "Destination": get_scalar(md, "Destination"),
            "DestinationIp": get_scalar(md, "DestinationIp"),
            "DestinationPort": get_int(md, "DestinationPort"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FilterAtDestination": parse_filters(md, "FilterAtDestination"),
            "FilterAtSource": parse_filters(md, "FilterAtSource"),
            "Protocol": get_scalar(md, "Protocol"),
            "Source": get_scalar(md, "Source"),
            "SourceIp": get_scalar(md, "SourceIp"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_network_insights_analysis_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkInsightsAnalysisId": get_scalar(md, "NetworkInsightsAnalysisId"),
        }

    @staticmethod
    def parse_delete_network_insights_path_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkInsightsPathId": get_scalar(md, "NetworkInsightsPathId"),
        }

    @staticmethod
    def parse_describe_network_insights_analyses_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AnalysisEndTime": get_scalar(md, "AnalysisEndTime"),
            "AnalysisStartTime": get_scalar(md, "AnalysisStartTime"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NetworkInsightsAnalysisId.N": get_indexed_list(md, "NetworkInsightsAnalysisId"),
            "NetworkInsightsPathId": get_scalar(md, "NetworkInsightsPathId"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_network_insights_paths_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NetworkInsightsPathId.N": get_indexed_list(md, "NetworkInsightsPathId"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_enable_reachability_analyzer_organization_sharing_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_start_network_insights_analysis_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AdditionalAccount.N": get_indexed_list(md, "AdditionalAccount"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "FilterInArn.N": parse_filters(md, "FilterInArn"),
            "FilterOutArn.N": parse_filters(md, "FilterOutArn"),
            "NetworkInsightsPathId": get_scalar(md, "NetworkInsightsPathId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateNetworkInsightsPath": reachabilityanalyzer_RequestParser.parse_create_network_insights_path_request,
            "DeleteNetworkInsightsAnalysis": reachabilityanalyzer_RequestParser.parse_delete_network_insights_analysis_request,
            "DeleteNetworkInsightsPath": reachabilityanalyzer_RequestParser.parse_delete_network_insights_path_request,
            "DescribeNetworkInsightsAnalyses": reachabilityanalyzer_RequestParser.parse_describe_network_insights_analyses_request,
            "DescribeNetworkInsightsPaths": reachabilityanalyzer_RequestParser.parse_describe_network_insights_paths_request,
            "EnableReachabilityAnalyzerOrganizationSharing": reachabilityanalyzer_RequestParser.parse_enable_reachability_analyzer_organization_sharing_request,
            "StartNetworkInsightsAnalysis": reachabilityanalyzer_RequestParser.parse_start_network_insights_analysis_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class reachabilityanalyzer_ResponseSerializer:
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
                xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_network_insights_path_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateNetworkInsightsPathResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsPath
        _networkInsightsPath_key = None
        if "networkInsightsPath" in data:
            _networkInsightsPath_key = "networkInsightsPath"
        elif "NetworkInsightsPath" in data:
            _networkInsightsPath_key = "NetworkInsightsPath"
        if _networkInsightsPath_key:
            param_data = data[_networkInsightsPath_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsPath>')
            xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</networkInsightsPath>')
        xml_parts.append(f'</CreateNetworkInsightsPathResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_network_insights_analysis_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteNetworkInsightsAnalysisResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAnalysisId
        _networkInsightsAnalysisId_key = None
        if "networkInsightsAnalysisId" in data:
            _networkInsightsAnalysisId_key = "networkInsightsAnalysisId"
        elif "NetworkInsightsAnalysisId" in data:
            _networkInsightsAnalysisId_key = "NetworkInsightsAnalysisId"
        if _networkInsightsAnalysisId_key:
            param_data = data[_networkInsightsAnalysisId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsAnalysisId>{esc(str(param_data))}</networkInsightsAnalysisId>')
        xml_parts.append(f'</DeleteNetworkInsightsAnalysisResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_network_insights_path_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteNetworkInsightsPathResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsPathId
        _networkInsightsPathId_key = None
        if "networkInsightsPathId" in data:
            _networkInsightsPathId_key = "networkInsightsPathId"
        elif "NetworkInsightsPathId" in data:
            _networkInsightsPathId_key = "NetworkInsightsPathId"
        if _networkInsightsPathId_key:
            param_data = data[_networkInsightsPathId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<networkInsightsPathId>{esc(str(param_data))}</networkInsightsPathId>')
        xml_parts.append(f'</DeleteNetworkInsightsPathResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_network_insights_analyses_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeNetworkInsightsAnalysesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAnalysisSet
        _networkInsightsAnalysisSet_key = None
        if "networkInsightsAnalysisSet" in data:
            _networkInsightsAnalysisSet_key = "networkInsightsAnalysisSet"
        elif "NetworkInsightsAnalysisSet" in data:
            _networkInsightsAnalysisSet_key = "NetworkInsightsAnalysisSet"
        elif "NetworkInsightsAnalysiss" in data:
            _networkInsightsAnalysisSet_key = "NetworkInsightsAnalysiss"
        if _networkInsightsAnalysisSet_key:
            param_data = data[_networkInsightsAnalysisSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<networkInsightsAnalysisSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</networkInsightsAnalysisSet>')
            else:
                xml_parts.append(f'{indent_str}<networkInsightsAnalysisSet/>')
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
        xml_parts.append(f'</DescribeNetworkInsightsAnalysesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_network_insights_paths_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeNetworkInsightsPathsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsPathSet
        _networkInsightsPathSet_key = None
        if "networkInsightsPathSet" in data:
            _networkInsightsPathSet_key = "networkInsightsPathSet"
        elif "NetworkInsightsPathSet" in data:
            _networkInsightsPathSet_key = "NetworkInsightsPathSet"
        elif "NetworkInsightsPaths" in data:
            _networkInsightsPathSet_key = "NetworkInsightsPaths"
        if _networkInsightsPathSet_key:
            param_data = data[_networkInsightsPathSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<networkInsightsPathSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</networkInsightsPathSet>')
            else:
                xml_parts.append(f'{indent_str}<networkInsightsPathSet/>')
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
        xml_parts.append(f'</DescribeNetworkInsightsPathsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_reachability_analyzer_organization_sharing_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableReachabilityAnalyzerOrganizationSharingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize returnValue
        _returnValue_key = None
        if "returnValue" in data:
            _returnValue_key = "returnValue"
        elif "ReturnValue" in data:
            _returnValue_key = "ReturnValue"
        if _returnValue_key:
            param_data = data[_returnValue_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<returnValue>{esc(str(param_data))}</returnValue>')
        xml_parts.append(f'</EnableReachabilityAnalyzerOrganizationSharingResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_start_network_insights_analysis_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<StartNetworkInsightsAnalysisResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize networkInsightsAnalysis
        _networkInsightsAnalysis_key = None
        if "networkInsightsAnalysis" in data:
            _networkInsightsAnalysis_key = "networkInsightsAnalysis"
        elif "NetworkInsightsAnalysis" in data:
            _networkInsightsAnalysis_key = "NetworkInsightsAnalysis"
        if _networkInsightsAnalysis_key:
            param_data = data[_networkInsightsAnalysis_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<networkInsightsAnalysisSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reachabilityanalyzer_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</networkInsightsAnalysisSet>')
            else:
                xml_parts.append(f'{indent_str}<networkInsightsAnalysisSet/>')
        xml_parts.append(f'</StartNetworkInsightsAnalysisResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateNetworkInsightsPath": reachabilityanalyzer_ResponseSerializer.serialize_create_network_insights_path_response,
            "DeleteNetworkInsightsAnalysis": reachabilityanalyzer_ResponseSerializer.serialize_delete_network_insights_analysis_response,
            "DeleteNetworkInsightsPath": reachabilityanalyzer_ResponseSerializer.serialize_delete_network_insights_path_response,
            "DescribeNetworkInsightsAnalyses": reachabilityanalyzer_ResponseSerializer.serialize_describe_network_insights_analyses_response,
            "DescribeNetworkInsightsPaths": reachabilityanalyzer_ResponseSerializer.serialize_describe_network_insights_paths_response,
            "EnableReachabilityAnalyzerOrganizationSharing": reachabilityanalyzer_ResponseSerializer.serialize_enable_reachability_analyzer_organization_sharing_response,
            "StartNetworkInsightsAnalysis": reachabilityanalyzer_ResponseSerializer.serialize_start_network_insights_analysis_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

