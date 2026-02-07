from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from emulator_core.backend import BaseBackend


@dataclass
class Tag:
    key: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.key, "Value": self.value}


@dataclass
class TagSpecification:
    resource_type: Optional[str] = None
    tags: List[Tag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceType": self.resource_type,
            "Tags": [tag.to_dict() for tag in self.tags],
        }


@dataclass
class PortRange:
    From: Optional[int] = None
    To: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"From": self.From, "To": self.To}


@dataclass
class PacketHeaderStatement:
    destination_addresses: List[str] = field(default_factory=list)
    destination_ports: List[str] = field(default_factory=list)
    destination_prefix_lists: List[str] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)  # Valid Values: tcp | udp
    source_addresses: List[str] = field(default_factory=list)
    source_ports: List[str] = field(default_factory=list)
    source_prefix_lists: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "DestinationAddresses": self.destination_addresses,
            "DestinationPorts": self.destination_ports,
            "DestinationPrefixLists": self.destination_prefix_lists,
            "Protocols": self.protocols,
            "SourceAddresses": self.source_addresses,
            "SourcePorts": self.source_ports,
            "SourcePrefixLists": self.source_prefix_lists,
        }


@dataclass
class ResourceStatement:
    resources: List[str] = field(default_factory=list)
    resource_types: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Resources": self.resources,
            "ResourceTypes": self.resource_types,
        }


@dataclass
class PathStatement:
    packet_header_statement: Optional[PacketHeaderStatement] = None
    resource_statement: Optional[ResourceStatement] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "PacketHeaderStatement": self.packet_header_statement.to_dict() if self.packet_header_statement else None,
            "ResourceStatement": self.resource_statement.to_dict() if self.resource_statement else None,
        }


@dataclass
class ThroughResourcesStatement:
    resource_statement: Optional[ResourceStatement] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ResourceStatement": self.resource_statement.to_dict() if self.resource_statement else None,
        }


@dataclass
class AccessScopePath:
    destination: Optional[PathStatement] = None
    source: Optional[PathStatement] = None
    through_resources: List[ThroughResourcesStatement] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Destination": self.destination.to_dict() if self.destination else None,
            "Source": self.source.to_dict() if self.source else None,
            "ThroughResources": [tr.to_dict() for tr in self.through_resources],
        }


@dataclass
class NetworkInsightsAccessScope:
    created_date: Optional[datetime] = None
    network_insights_access_scope_arn: Optional[str] = None
    network_insights_access_scope_id: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    updated_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "CreatedDate": self.created_date.isoformat() if self.created_date else None,
            "NetworkInsightsAccessScopeArn": self.network_insights_access_scope_arn,
            "NetworkInsightsAccessScopeId": self.network_insights_access_scope_id,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "UpdatedDate": self.updated_date.isoformat() if self.updated_date else None,
        }


@dataclass
class NetworkInsightsAccessScopeContent:
    exclude_path_set: List[AccessScopePath] = field(default_factory=list)
    match_path_set: List[AccessScopePath] = field(default_factory=list)
    network_insights_access_scope_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ExcludePathSet": [path.to_dict() for path in self.exclude_path_set],
            "MatchPathSet": [path.to_dict() for path in self.match_path_set],
            "NetworkInsightsAccessScopeId": self.network_insights_access_scope_id,
        }


class NetworkInsightsAccessScopeAnalysisFindingsFindingStatus(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class NetworkInsightsAccessScopeAnalysisStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class NetworkInsightsAccessScopeAnalysis:
    analyzed_eni_count: Optional[int] = None
    end_date: Optional[datetime] = None
    findings_found: Optional[NetworkInsightsAccessScopeAnalysisFindingsFindingStatus] = None
    network_insights_access_scope_analysis_arn: Optional[str] = None
    network_insights_access_scope_analysis_id: Optional[str] = None
    network_insights_access_scope_id: Optional[str] = None
    start_date: Optional[datetime] = None
    status: Optional[NetworkInsightsAccessScopeAnalysisStatus] = None
    status_message: Optional[str] = None
    tag_set: List[Tag] = field(default_factory=list)
    warning_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "AnalyzedEniCount": self.analyzed_eni_count,
            "EndDate": self.end_date.isoformat() if self.end_date else None,
            "FindingsFound": self.findings_found.value if self.findings_found else None,
            "NetworkInsightsAccessScopeAnalysisArn": self.network_insights_access_scope_analysis_arn,
            "NetworkInsightsAccessScopeAnalysisId": self.network_insights_access_scope_analysis_id,
            "NetworkInsightsAccessScopeId": self.network_insights_access_scope_id,
            "StartDate": self.start_date.isoformat() if self.start_date else None,
            "Status": self.status.value if self.status else None,
            "StatusMessage": self.status_message,
            "TagSet": [tag.to_dict() for tag in self.tag_set],
            "WarningMessage": self.warning_message,
        }


class NetworkAccessAnalyzerBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state for persistence

    def create_network_insights_access_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        def parse_packet_header_statement(data: Dict[str, Any]) -> PacketHeaderStatement:
            if data is None:
                return None
            return PacketHeaderStatement(
                destination_addresses=data.get("DestinationAddresses", []),
                destination_ports=data.get("DestinationPorts", []),
                destination_prefix_lists=data.get("DestinationPrefixLists", []),
                protocols=data.get("Protocols", []),
                source_addresses=data.get("SourceAddresses", []),
                source_ports=data.get("SourcePorts", []),
                source_prefix_lists=data.get("SourcePrefixLists", []),
            )

        def parse_resource_statement(data: Dict[str, Any]) -> ResourceStatement:
            if data is None:
                return None
            return ResourceStatement(
                resources=data.get("Resources", []),
                resource_types=data.get("ResourceTypes", []),
            )

        def parse_path_statement(data: Dict[str, Any]) -> PathStatement:
            if data is None:
                return None
            packet_header_statement = parse_packet_header_statement(data.get("PacketHeaderStatement"))
            resource_statement = parse_resource_statement(data.get("ResourceStatement"))
            return PathStatement(
                packet_header_statement=packet_header_statement,
                resource_statement=resource_statement,
            )

        def parse_through_resources_statement(data: Dict[str, Any]) -> ThroughResourcesStatement:
            if data is None:
                return None
            resource_statement = parse_resource_statement(data.get("ResourceStatement"))
            return ThroughResourcesStatement(resource_statement=resource_statement)

        def parse_access_scope_path(data: Dict[str, Any]) -> AccessScopePath:
            if data is None:
                return None
            destination = parse_path_statement(data.get("Destination"))
            source = parse_path_statement(data.get("Source"))
            through_resources_data = data.get("ThroughResources", [])
            through_resources = []
            for tr in through_resources_data:
                trs = parse_through_resources_statement(tr)
                if trs is not None:
                    through_resources.append(trs)
            return AccessScopePath(
                destination=destination,
                source=source,
                through_resources=through_resources,
            )

        def parse_tag(data: Dict[str, Any]) -> Tag:
            if data is None:
                return None
            return Tag(
                key=data.get("Key"),
                value=data.get("Value"),
            )

        def parse_tag_specification(data: Dict[str, Any]) -> TagSpecification:
            if data is None:
                return None
            tags_data = data.get("Tags", [])
            tags = []
            for tag_data in tags_data:
                tag = parse_tag(tag_data)
                if tag is not None:
                    tags.append(tag)
            return TagSpecification(
                resource_type=data.get("ResourceType"),
                tags=tags,
            )

        # Validate required parameters
        client_token = params.get("ClientToken")
        if not client_token or not isinstance(client_token, str):
            raise ValueError("ClientToken is required and must be a string")

        # Check for idempotency: if a scope with this client token exists, return it
        for scope in self.state.network_access_analyzer.values():
            if getattr(scope, "client_token", None) == client_token:
                # Return existing scope info
                return {
                    "networkInsightsAccessScope": scope.to_dict(),
                    "networkInsightsAccessScopeContent": self.state.network_access_analyzer_content.get(scope.network_insights_access_scope_id, NetworkInsightsAccessScopeContent([], [], None)).to_dict(),
                    "requestId": self.generate_request_id(),
                }

        # Parse exclude paths
        exclude_paths_data = params.get("ExcludePath.N", [])
        exclude_path_set = []
        for ep in exclude_paths_data:
            asp = parse_access_scope_path(ep)
            if asp is not None:
                exclude_path_set.append(asp)

        # Parse match paths
        match_paths_data = params.get("MatchPath.N", [])
        match_path_set = []
        for mp in match_paths_data:
            asp = parse_access_scope_path(mp)
            if asp is not None:
                match_path_set.append(asp)

        # Parse tags
        tag_specifications_data = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec_data in tag_specifications_data:
            tag_spec = parse_tag_specification(tag_spec_data)
            if tag_spec is not None:
                tags.extend(tag_spec.tags)

        # Generate unique ID and ARN
        scope_id = self.generate_unique_id()
        arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:network-insights-access-scope/{scope_id}"
        now = datetime.datetime.utcnow()

        # Create NetworkInsightsAccessScope object
        scope = NetworkInsightsAccessScope(
            created_date=now,
            network_insights_access_scope_arn=arn,
            network_insights_access_scope_id=scope_id,
            tag_set=tags,
            updated_date=now,
        )
        # Store client token for idempotency
        setattr(scope, "client_token", client_token)

        # Store in state
        self.state.network_access_analyzer[scope_id] = scope

        # Create and store NetworkInsightsAccessScopeContent
        content = NetworkInsightsAccessScopeContent(
            exclude_path_set=exclude_path_set,
            match_path_set=match_path_set,
            network_insights_access_scope_id=scope_id,
        )
        if not hasattr(self.state, "network_access_analyzer_content"):
            self.state.network_access_analyzer_content = {}
        self.state.network_access_analyzer_content[scope_id] = content

        return {
            "networkInsightsAccessScope": scope.to_dict(),
            "networkInsightsAccessScopeContent": content.to_dict(),
            "requestId": self.generate_request_id(),
        }


    def delete_network_insights_access_scope(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        scope_id = params.get("NetworkInsightsAccessScopeId")
        if not scope_id or not isinstance(scope_id, str):
            raise ValueError("NetworkInsightsAccessScopeId is required and must be a string")

        # Check if scope exists
        scope = self.state.network_access_analyzer.get(scope_id)
        if scope is None:
            # According to AWS behavior, deleting a non-existent resource is not an error, just return success with id
            pass
        else:
            # Delete scope and associated content
            del self.state.network_access_analyzer[scope_id]
            if hasattr(self.state, "network_access_analyzer_content"):
                self.state.network_access_analyzer_content.pop(scope_id, None)

        return {
            "networkInsightsAccessScopeId": scope_id,
            "requestId": self.generate_request_id(),
        }


    def delete_network_insights_access_scope_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameter
        analysis_id = params.get("NetworkInsightsAccessScopeAnalysisId")
        if not analysis_id or not isinstance(analysis_id, str):
            raise ValueError("NetworkInsightsAccessScopeAnalysisId is required and must be a string")

        # Check if analysis exists
        analysis = self.state.network_access_analyzer_analyses.get(analysis_id) if hasattr(self.state, "network_access_analyzer_analyses") else None
        if analysis is None:
            # Deleting non-existent analysis is not an error, just return success with id
            pass
        else:
            # Delete analysis
            del self.state.network_access_analyzer_analyses[analysis_id]

        return {
            "networkInsightsAccessScopeAnalysisId": analysis_id,
            "requestId": self.generate_request_id(),
        }


    def describe_network_insights_access_scope_analyses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Prepare filters
        analysis_start_time_begin = params.get("AnalysisStartTimeBegin")
        analysis_start_time_end = params.get("AnalysisStartTimeEnd")
        filter_list = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        analysis_ids = params.get("NetworkInsightsAccessScopeAnalysisId.N", [])
        scope_id = params.get("NetworkInsightsAccessScopeId")
        next_token = params.get("NextToken")

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
                raise ValueError("MaxResults must be an integer between 1 and 100")

        # Get all analyses
        analyses_dict = getattr(self.state, "network_access_analyzer_analyses", {})
        analyses = list(analyses_dict.values())

        # Filter by analysis IDs if provided
        if analysis_ids:
            analyses = [a for a in analyses if a.network_insights_access_scope_analysis_id in analysis_ids]

        # Filter by scope ID if provided
        if scope_id:
            analyses = [a for a in analyses if a.network_insights_access_scope_id == scope_id]

        # Filter by start time begin
        if analysis_start_time_begin:
            if not isinstance(analysis_start_time_begin, datetime.datetime):
                raise ValueError("AnalysisStartTimeBegin must be a datetime")
            analyses = [a for a in analyses if a.start_date and a.start_date >= analysis_start_time_begin]

        # Filter by start time end
        if analysis_start_time_end:
            if not isinstance(analysis_start_time_end, datetime.datetime):
                raise ValueError("AnalysisStartTimeEnd must be a datetime")
            analyses = [a for a in analyses if a.start_date and a.start_date <= analysis_start_time_end]

        # No supported filters, so ignore filter_list

        # Pagination handling
        # next_token is expected to be an index string
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Apply max_results limit
        end_index = len(analyses)
        if max_results is not None:
            end_index = min(start_index + max_results, len(analyses))

        page_analyses = analyses[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(analyses):
            new_next_token = str(end_index)

        # Convert to dicts
        analysis_set = [a.to_dict() for a in page_analyses]

        return {
            "networkInsightsAccessScopeAnalysisSet": analysis_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def describe_network_insights_access_scopes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        filter_list = params.get("Filter.N", [])
        max_results = params.get("MaxResults")
        scope_ids = params.get("NetworkInsightsAccessScopeId.N", [])
        next_token = params.get("NextToken")

        # Validate max_results
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
                raise ValueError("MaxResults must be an integer between 1 and 100")

        # Get all scopes
        scopes = list(self.state.network_access_analyzer.values())

        # Filter by scope IDs if provided
        if scope_ids:
            scopes = [s for s in scopes if s.network_insights_access_scope_id in scope_ids]

        # No supported filters, so ignore filter_list

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = len(scopes)
        if max_results is not None:
            end_index = min(start_index + max_results, len(scopes))

        page_scopes = scopes[start_index:end_index]

        # Prepare next token
        new_next_token = None
        if end_index < len(scopes):
            new_next_token = str(end_index)

        # Convert to dicts
        scope_set = [s.to_dict() for s in page_scopes]

        return {
            "networkInsightsAccessScopeSet": scope_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def get_network_insights_access_scope_analysis_findings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        analysis_id = params.get("NetworkInsightsAccessScopeAnalysisId")
        if not analysis_id:
            raise ValueError("NetworkInsightsAccessScopeAnalysisId is required")

        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int) or max_results < 1 or max_results > 1000:
                raise ValueError("MaxResults must be an integer between 1 and 1000")

        next_token = params.get("NextToken")

        # Retrieve the analysis from state
        analysis = self.state.network_access_analyzer.get(analysis_id)
        if not analysis:
            # Return empty findings and status if analysis not found
            return {
                "analysisFindingSet": [],
                "analysisStatus": None,
                "networkInsightsAccessScopeAnalysisId": analysis_id,
                "nextToken": None,
                "requestId": self.generate_request_id(),
            }

        # For this emulator, we assume findings are stored in analysis.findings (list)
        # If not present, empty list
        findings = getattr(analysis, "findings", [])

        # Pagination logic
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        end_index = start_index + max_results if max_results else len(findings)
        paged_findings = findings[start_index:end_index]

        # Prepare next token if more results exist
        new_next_token = str(end_index) if end_index < len(findings) else None

        # Convert findings to dicts
        analysis_finding_set = [finding.to_dict() for finding in paged_findings]

        return {
            "analysisFindingSet": analysis_finding_set,
            "analysisStatus": analysis.status.name if analysis.status else None,
            "networkInsightsAccessScopeAnalysisId": analysis_id,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }


    def get_network_insights_access_scope_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        scope_id = params.get("NetworkInsightsAccessScopeId")
        if not scope_id:
            raise ValueError("NetworkInsightsAccessScopeId is required")

        # Retrieve the NetworkInsightsAccessScopeContent from state
        content = self.state.network_access_analyzer.get(scope_id)
        if not content:
            # Return empty content if not found
            return {
                "networkInsightsAccessScopeContent": {
                    "excludePathSet": [],
                    "matchPathSet": [],
                    "networkInsightsAccessScopeId": scope_id,
                },
                "requestId": self.generate_request_id(),
            }

        # If content is a NetworkInsightsAccessScopeContent object, convert to dict
        if hasattr(content, "to_dict"):
            content_dict = content.to_dict()
        else:
            # If content is NetworkInsightsAccessScope, try to get content attribute
            content_obj = getattr(content, "content", None)
            if content_obj and hasattr(content_obj, "to_dict"):
                content_dict = content_obj.to_dict()
            else:
                # Fallback empty content
                content_dict = {
                    "excludePathSet": [],
                    "matchPathSet": [],
                    "networkInsightsAccessScopeId": scope_id,
                }

        return {
            "networkInsightsAccessScopeContent": content_dict,
            "requestId": self.generate_request_id(),
        }


    def start_network_insights_access_scope_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        client_token = params.get("ClientToken")
        if not client_token:
            raise ValueError("ClientToken is required")

        scope_id = params.get("NetworkInsightsAccessScopeId")
        if not scope_id:
            raise ValueError("NetworkInsightsAccessScopeId is required")

        # Check if scope exists
        scope = self.state.network_access_analyzer.get(scope_id)
        if not scope:
            raise ValueError(f"NetworkInsightsAccessScope with id {scope_id} not found")

        # Check for idempotency: if an analysis with this client_token exists, return it
        for analysis in self.state.network_access_analyzer.values():
            if getattr(analysis, "client_token", None) == client_token:
                return {
                    "networkInsightsAccessScopeAnalysis": analysis.to_dict(),
                    "requestId": self.generate_request_id(),
                }

        # Create new analysis object
        from datetime import datetime

        analysis_id = self.generate_unique_id()
        arn = f"arn:aws:ec2:{self.state.region}:{self.get_owner_id()}:network-insights-access-scope-analysis/{analysis_id}"

        tag_specifications = params.get("TagSpecification.N", [])
        tags = []
        for tag_spec in tag_specifications:
            tag_list = tag_spec.get("Tags", [])
            for tag in tag_list:
                key = tag.get("Key")
                value = tag.get("Value")
                if key is not None and value is not None:
                    tags.append(Tag(key=key, value=value))

        # Create NetworkInsightsAccessScopeAnalysis object
        analysis = NetworkInsightsAccessScopeAnalysis()
        analysis.network_insights_access_scope_analysis_id = analysis_id
        analysis.network_insights_access_scope_analysis_arn = arn
        analysis.network_insights_access_scope_id = scope_id
        analysis.start_date = datetime.utcnow()
        analysis.status = NetworkInsightsAccessScopeAnalysisStatus.RUNNING if hasattr(NetworkInsightsAccessScopeAnalysisStatus, "RUNNING") else None
        analysis.findings_found = None
        analysis.analyzed_eni_count = 0
        analysis.tag_set = tags
        analysis.status_message = None
        analysis.warning_message = None
        analysis.client_token = client_token  # store client token for idempotency

        # Store analysis in state
        self.state.network_access_analyzer[analysis_id] = analysis

        return {
            "networkInsightsAccessScopeAnalysis": analysis.to_dict(),
            "requestId": self.generate_request_id(),
        }

    

from emulator_core.gateway.base import BaseGateway

class NetworkAccessAnalyzerGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateNetworkInsightsAccessScope", self.create_network_insights_access_scope)
        self.register_action("DeleteNetworkInsightsAccessScope", self.delete_network_insights_access_scope)
        self.register_action("DeleteNetworkInsightsAccessScopeAnalysis", self.delete_network_insights_access_scope_analysis)
        self.register_action("DescribeNetworkInsightsAccessScopeAnalyses", self.describe_network_insights_access_scope_analyses)
        self.register_action("DescribeNetworkInsightsAccessScopes", self.describe_network_insights_access_scopes)
        self.register_action("GetNetworkInsightsAccessScopeAnalysisFindings", self.get_network_insights_access_scope_analysis_findings)
        self.register_action("GetNetworkInsightsAccessScopeContent", self.get_network_insights_access_scope_content)
        self.register_action("StartNetworkInsightsAccessScopeAnalysis", self.start_network_insights_access_scope_analysis)

    def create_network_insights_access_scope(self, params):
        return self.backend.create_network_insights_access_scope(params)

    def delete_network_insights_access_scope(self, params):
        return self.backend.delete_network_insights_access_scope(params)

    def delete_network_insights_access_scope_analysis(self, params):
        return self.backend.delete_network_insights_access_scope_analysis(params)

    def describe_network_insights_access_scope_analyses(self, params):
        return self.backend.describe_network_insights_access_scope_analyses(params)

    def describe_network_insights_access_scopes(self, params):
        return self.backend.describe_network_insights_access_scopes(params)

    def get_network_insights_access_scope_analysis_findings(self, params):
        return self.backend.get_network_insights_access_scope_analysis_findings(params)

    def get_network_insights_access_scope_content(self, params):
        return self.backend.get_network_insights_access_scope_content(params)

    def start_network_insights_access_scope_analysis(self, params):
        return self.backend.start_network_insights_access_scope_analysis(params)
