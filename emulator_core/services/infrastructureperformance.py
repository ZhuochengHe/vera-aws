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
class InfrastructurePerformance:
    destination: str = ""
    metric: str = ""
    period: str = ""
    source: str = ""
    statistic: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "destination": self.destination,
            "metric": self.metric,
            "period": self.period,
            "source": self.source,
            "statistic": self.statistic,
        }

class InfrastructurePerformance_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.infrastructure_performance  # alias to shared store


    def _find_subscription(self, destination: str, metric: str, source: str, statistic: str) -> Optional[tuple]:
        for subscription_id, subscription in self.resources.items():
            if (subscription.destination == destination
                and subscription.metric == metric
                and subscription.source == source
                and subscription.statistic == statistic):
                return subscription_id, subscription
        return None

    def _subscription_exists(self, destination: str, metric: str, source: str, statistic: str) -> bool:
        return self._find_subscription(destination, metric, source, statistic) is not None


    def DescribeAwsNetworkPerformanceMetricSubscriptions(self, params: Dict[str, Any]):
        """Describes the current Infrastructure Performance metric subscriptions."""
        filters = params.get("Filter.N", [])
        resources = list(self.resources.values())
        if filters:
            resources = apply_filters(resources, filters)

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = int(next_token or 0) if next_token else 0
        page = resources[start_index:start_index + max_results]
        new_token = str(start_index + max_results) if start_index + max_results < len(resources) else None
        subscription_set = [resource.to_dict() for resource in page]

        return {
            'nextToken': new_token,
            'subscriptionSet': subscription_set,
            }

    def DisableAwsNetworkPerformanceMetricSubscription(self, params: Dict[str, Any]):
        """Disables Infrastructure Performance metric subscriptions."""
        destination = params.get("Destination") or ""
        metric = params.get("Metric") or ""
        source = params.get("Source") or ""
        statistic = params.get("Statistic") or ""

        if not destination:
            return create_error_response("MissingParameter", "Missing required parameter: Destination")
        if not metric:
            return create_error_response("MissingParameter", "Missing required parameter: Metric")
        if not source:
            return create_error_response("MissingParameter", "Missing required parameter: Source")
        if not statistic:
            return create_error_response("MissingParameter", "Missing required parameter: Statistic")

        subscription_match = self._find_subscription(destination, metric, source, statistic)
        if not subscription_match:
            return create_error_response(
                "InvalidInfrastructurePerformanceMetricSubscription.NotFound",
                "The specified subscription does not exist",
            )

        subscription_id, _ = subscription_match
        if subscription_id in self.resources:
            del self.resources[subscription_id]

        return {
            'output': True,
            }

    def EnableAwsNetworkPerformanceMetricSubscription(self, params: Dict[str, Any]):
        """Enables Infrastructure Performance subscriptions."""
        destination = params.get("Destination") or ""
        metric = params.get("Metric") or ""
        source = params.get("Source") or ""
        statistic = params.get("Statistic") or ""

        if not destination:
            return create_error_response("MissingParameter", "Missing required parameter: Destination")
        if not metric:
            return create_error_response("MissingParameter", "Missing required parameter: Metric")
        if not source:
            return create_error_response("MissingParameter", "Missing required parameter: Source")
        if not statistic:
            return create_error_response("MissingParameter", "Missing required parameter: Statistic")

        if not self._subscription_exists(destination, metric, source, statistic):
            subscription_id = self._generate_id("inf")
            subscription = InfrastructurePerformance(
                destination=destination,
                metric=metric,
                period="",
                source=source,
                statistic=statistic,
            )
            self.resources[subscription_id] = subscription

        return {
            'output': True,
            }

    def GetAwsNetworkPerformanceData(self, params: Dict[str, Any]):
        """Gets network performance data."""
        data_queries = params.get("DataQuery.N", [])
        data_responses: List[Dict[str, Any]] = []

        if data_queries:
            for query in data_queries:
                if isinstance(query, dict):
                    destination = query.get("Destination") or ""
                    metric = query.get("Metric") or ""
                    source = query.get("Source") or ""
                    statistic = query.get("Statistic") or ""
                    period = query.get("Period") or ""
                    query_id = query.get("Id") or query.get("id") or ""
                    subscription_match = None
                    if destination or metric or source or statistic:
                        subscription_match = self._find_subscription(destination, metric, source, statistic)
                    if subscription_match:
                        subscription_id, subscription = subscription_match
                        destination = destination or subscription.destination
                        metric = metric or subscription.metric
                        source = source or subscription.source
                        statistic = statistic or subscription.statistic
                        period = period or subscription.period
                        if not query_id:
                            query_id = subscription_id
                    if not query_id:
                        query_id = self._generate_id("inf")
                else:
                    query_id = query or self._generate_id("inf")
                    destination = ""
                    metric = ""
                    source = ""
                    statistic = ""
                    period = ""

                data_responses.append({
                    "destination": destination,
                    "id": query_id,
                    "metric": metric,
                    "metricPointSet": [],
                    "period": period,
                    "source": source,
                    "statistic": statistic,
                })
        else:
            for subscription_id, subscription in self.resources.items():
                data_responses.append({
                    "destination": subscription.destination,
                    "id": subscription_id,
                    "metric": subscription.metric,
                    "metricPointSet": [],
                    "period": subscription.period,
                    "source": subscription.source,
                    "statistic": subscription.statistic,
                })

        max_results = int(params.get("MaxResults") or 100)
        next_token = params.get("NextToken")
        start_index = int(next_token or 0) if next_token else 0
        page = data_responses[start_index:start_index + max_results]
        new_token = str(start_index + max_results) if start_index + max_results < len(data_responses) else None

        return {
            'dataResponseSet': page,
            'nextToken': new_token,
            }

    def _generate_id(self, prefix: str = 'inf') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class infrastructureperformance_RequestParser:
    @staticmethod
    def parse_describe_aws_network_performance_metric_subscriptions_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_disable_aws_network_performance_metric_subscription_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Destination": get_scalar(md, "Destination"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Metric": get_scalar(md, "Metric"),
            "Source": get_scalar(md, "Source"),
            "Statistic": get_scalar(md, "Statistic"),
        }

    @staticmethod
    def parse_enable_aws_network_performance_metric_subscription_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Destination": get_scalar(md, "Destination"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Metric": get_scalar(md, "Metric"),
            "Source": get_scalar(md, "Source"),
            "Statistic": get_scalar(md, "Statistic"),
        }

    @staticmethod
    def parse_get_aws_network_performance_data_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DataQuery.N": get_indexed_list(md, "DataQuery"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndTime": get_scalar(md, "EndTime"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "StartTime": get_scalar(md, "StartTime"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "DescribeAwsNetworkPerformanceMetricSubscriptions": infrastructureperformance_RequestParser.parse_describe_aws_network_performance_metric_subscriptions_request,
            "DisableAwsNetworkPerformanceMetricSubscription": infrastructureperformance_RequestParser.parse_disable_aws_network_performance_metric_subscription_request,
            "EnableAwsNetworkPerformanceMetricSubscription": infrastructureperformance_RequestParser.parse_enable_aws_network_performance_metric_subscription_request,
            "GetAwsNetworkPerformanceData": infrastructureperformance_RequestParser.parse_get_aws_network_performance_data_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class infrastructureperformance_ResponseSerializer:
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
                xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_describe_aws_network_performance_metric_subscriptions_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeAwsNetworkPerformanceMetricSubscriptionsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize subscriptionSet
        _subscriptionSet_key = None
        if "subscriptionSet" in data:
            _subscriptionSet_key = "subscriptionSet"
        elif "SubscriptionSet" in data:
            _subscriptionSet_key = "SubscriptionSet"
        elif "Subscriptions" in data:
            _subscriptionSet_key = "Subscriptions"
        if _subscriptionSet_key:
            param_data = data[_subscriptionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<subscriptionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</subscriptionSet>')
            else:
                xml_parts.append(f'{indent_str}<subscriptionSet/>')
        xml_parts.append(f'</DescribeAwsNetworkPerformanceMetricSubscriptionsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_disable_aws_network_performance_metric_subscription_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DisableAwsNetworkPerformanceMetricSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize output
        _output_key = None
        if "output" in data:
            _output_key = "output"
        elif "Output" in data:
            _output_key = "Output"
        if _output_key:
            param_data = data[_output_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<output>{esc(str(param_data))}</output>')
        xml_parts.append(f'</DisableAwsNetworkPerformanceMetricSubscriptionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_enable_aws_network_performance_metric_subscription_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<EnableAwsNetworkPerformanceMetricSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize output
        _output_key = None
        if "output" in data:
            _output_key = "output"
        elif "Output" in data:
            _output_key = "Output"
        if _output_key:
            param_data = data[_output_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<output>{esc(str(param_data))}</output>')
        xml_parts.append(f'</EnableAwsNetworkPerformanceMetricSubscriptionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_aws_network_performance_data_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetAwsNetworkPerformanceDataResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize dataResponseSet
        _dataResponseSet_key = None
        if "dataResponseSet" in data:
            _dataResponseSet_key = "dataResponseSet"
        elif "DataResponseSet" in data:
            _dataResponseSet_key = "DataResponseSet"
        elif "DataResponses" in data:
            _dataResponseSet_key = "DataResponses"
        if _dataResponseSet_key:
            param_data = data[_dataResponseSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<dataResponseSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(infrastructureperformance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</dataResponseSet>')
            else:
                xml_parts.append(f'{indent_str}<dataResponseSet/>')
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
        xml_parts.append(f'</GetAwsNetworkPerformanceDataResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "DescribeAwsNetworkPerformanceMetricSubscriptions": infrastructureperformance_ResponseSerializer.serialize_describe_aws_network_performance_metric_subscriptions_response,
            "DisableAwsNetworkPerformanceMetricSubscription": infrastructureperformance_ResponseSerializer.serialize_disable_aws_network_performance_metric_subscription_response,
            "EnableAwsNetworkPerformanceMetricSubscription": infrastructureperformance_ResponseSerializer.serialize_enable_aws_network_performance_metric_subscription_response,
            "GetAwsNetworkPerformanceData": infrastructureperformance_ResponseSerializer.serialize_get_aws_network_performance_data_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

