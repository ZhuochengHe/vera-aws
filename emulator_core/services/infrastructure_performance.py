from typing import Dict, Any, List, Optional
from datetime import datetime
from emulator_core.backend import BaseBackend
from emulator_core.state import ErrorCode


class InfrastructurePerformanceBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # Use self.state.infrastructure_performance as dict storage for subscriptions
        # Key: subscription_id (str), Value: subscription dict

    def DescribeAwsNetworkPerformanceMetricSubscriptions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        # Validate Filters
        filters = params.get("Filter", [])
        if filters is not None and not isinstance(filters, list):
            raise ErrorCode.InvalidParameterValue("Filter must be a list")

        # Validate MaxResults
        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode.InvalidParameterValue("MaxResults must be an integer")
            if max_results < 0 or max_results > 100:
                raise ErrorCode.InvalidParameterValue("MaxResults must be between 0 and 100")

        # Validate NextToken
        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode.InvalidParameterValue("NextToken must be a string")

        # DryRun check
        if dry_run:
            # Assume user has permission for simplicity
            raise ErrorCode.DryRunOperation()

        # Filtering logic
        # Supported filter names are not explicitly defined, so we support filtering by keys in subscription dict
        # Filters are OR within values, AND between filters
        def subscription_matches_filters(sub: Dict[str, Any], filters: List[Dict[str, Any]]) -> bool:
            for f in filters:
                name = f.get("Name")
                values = f.get("Values", [])
                if name is None or not isinstance(name, str):
                    raise ErrorCode.InvalidParameterValue("Filter Name must be a string")
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                    raise ErrorCode.InvalidParameterValue("Filter Values must be list of strings")
                # If subscription does not have the attribute or value not in values, fail this filter
                sub_value = sub.get(name)
                if sub_value is None:
                    return False
                # Values are OR joined, so if any value matches sub_value, filter passes
                if str(sub_value) not in values:
                    return False
            return True

        # Collect all subscriptions
        all_subs = list(self.state.infrastructure_performance.values())

        # Apply filters if any
        if filters:
            filtered_subs = [sub for sub in all_subs if subscription_matches_filters(sub, filters)]
        else:
            filtered_subs = all_subs

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken")

        end_index = start_index + max_results if max_results is not None else len(filtered_subs)
        page_subs = filtered_subs[start_index:end_index]

        # Prepare subscriptionSet response
        subscription_set = []
        for sub in page_subs:
            subscription_set.append({
                "destination": sub.get("Destination"),
                "metric": sub.get("Metric"),
                "period": sub.get("Period"),
                "source": sub.get("Source"),
                "statistic": sub.get("Statistic"),
            })

        # Prepare nextToken for pagination
        new_next_token = str(end_index) if end_index < len(filtered_subs) else None

        return {
            "subscriptionSet": subscription_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def DisableAwsNetworkPerformanceMetricSubscription(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        destination = params.get("Destination")
        metric = params.get("Metric")
        source = params.get("Source")
        statistic = params.get("Statistic")

        # Validate string types if provided
        if destination is not None and not isinstance(destination, str):
            raise ErrorCode.InvalidParameterValue("Destination must be a string")
        if metric is not None and not isinstance(metric, str):
            raise ErrorCode.InvalidParameterValue("Metric must be a string")
        if source is not None and not isinstance(source, str):
            raise ErrorCode.InvalidParameterValue("Source must be a string")
        if statistic is not None and not isinstance(statistic, str):
            raise ErrorCode.InvalidParameterValue("Statistic must be a string")

        # DryRun check
        if dry_run:
            # Assume user has permission for simplicity
            raise ErrorCode.DryRunOperation()

        # Find matching subscription(s) to disable
        # We consider a subscription matches if all non-None parameters match exactly
        to_remove_keys = []
        for sub_id, sub in self.state.infrastructure_performance.items():
            if destination is not None and sub.get("Destination") != destination:
                continue
            if metric is not None and sub.get("Metric") != metric:
                continue
            if source is not None and sub.get("Source") != source:
                continue
            if statistic is not None and sub.get("Statistic") != statistic:
                continue
            to_remove_keys.append(sub_id)

        # Remove subscriptions
        for key in to_remove_keys:
            del self.state.infrastructure_performance[key]

        # If no matching subscription found, still return success (AWS behavior)
        return {
            "output": True,
            "requestId": self.generate_request_id(),
        }

    def EnableAwsNetworkPerformanceMetricSubscription(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        destination = params.get("Destination")
        metric = params.get("Metric")
        source = params.get("Source")
        statistic = params.get("Statistic")

        # Validate string types if provided
        if destination is not None and not isinstance(destination, str):
            raise ErrorCode.InvalidParameterValue("Destination must be a string")
        if metric is not None and not isinstance(metric, str):
            raise ErrorCode.InvalidParameterValue("Metric must be a string")
        if source is not None and not isinstance(source, str):
            raise ErrorCode.InvalidParameterValue("Source must be a string")
        if statistic is not None and not isinstance(statistic, str):
            raise ErrorCode.InvalidParameterValue("Statistic must be a string")

        # DryRun check
        if dry_run:
            # Assume user has permission for simplicity
            raise ErrorCode.DryRunOperation()

        # Validate required fields for subscription? The API doc says all are optional, so allow partial subscriptions

        # Check if subscription already exists (exact match)
        for sub in self.state.infrastructure_performance.values():
            if sub.get("Destination") == destination and sub.get("Metric") == metric and sub.get("Source") == source and sub.get("Statistic") == statistic:
                # Already subscribed, return success
                return {
                    "output": True,
                    "requestId": self.generate_request_id(),
                }

        # Create new subscription id
        subscription_id = f"sub-{self.generate_unique_id()}"

        # Period is not a parameter here, so default to None
        subscription = {
            "Destination": destination,
            "Metric": metric,
            "Period": None,
            "Source": source,
            "Statistic": statistic,
        }

        self.state.infrastructure_performance[subscription_id] = subscription

        return {
            "output": True,
            "requestId": self.generate_request_id(),
        }

    def GetAwsNetworkPerformanceData(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Validate DryRun
        dry_run = params.get("DryRun")
        if dry_run is not None and not isinstance(dry_run, bool):
            raise ErrorCode.InvalidParameterValue("DryRun must be a boolean")

        data_queries = params.get("DataQuery", [])
        if data_queries is not None and not isinstance(data_queries, list):
            raise ErrorCode.InvalidParameterValue("DataQuery must be a list")

        max_results = params.get("MaxResults")
        if max_results is not None:
            if not isinstance(max_results, int):
                raise ErrorCode.InvalidParameterValue("MaxResults must be an integer")
            if max_results < 0:
                raise ErrorCode.InvalidParameterValue("MaxResults must be >= 0")

        next_token = params.get("NextToken")
        if next_token is not None and not isinstance(next_token, str):
            raise ErrorCode.InvalidParameterValue("NextToken must be a string")

        start_time_str = params.get("StartTime")
        end_time_str = params.get("EndTime")

        # Parse timestamps if provided
        def parse_timestamp(ts: Optional[str]) -> Optional[datetime]:
            if ts is None:
                return None
            if not isinstance(ts, str):
                raise ErrorCode.InvalidParameterValue("Timestamp must be a string")
            try:
                # Accept ISO8601 format with optional milliseconds and Z
                # Example: 2022-06-12T12:00:00.000Z
                # Remove trailing Z if present
                ts_clean = ts.rstrip("Z")
                # Try parsing with microseconds
                dt = datetime.strptime(ts_clean, "%Y-%m-%dT%H:%M:%S.%f")
                return dt
            except ValueError:
                try:
                    # Try without microseconds
                    dt = datetime.strptime(ts_clean, "%Y-%m-%dT%H:%M:%S")
                    return dt
                except ValueError:
                    raise ErrorCode.InvalidParameterValue(f"Invalid timestamp format: {ts}")

        start_time = parse_timestamp(start_time_str)
        end_time = parse_timestamp(end_time_str)

        # Validate time range if both provided
        if start_time and end_time and start_time > end_time:
            raise ErrorCode.InvalidParameterValue("StartTime must be before EndTime")

        # DryRun check
        if dry_run:
            # Assume user has permission for simplicity
            raise ErrorCode.DryRunOperation()

        # For each DataQuery, generate dummy dataResponse
        data_response_set = []

        # Pagination support: we will paginate over data_queries if max_results is set
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                raise ErrorCode.InvalidParameterValue("Invalid NextToken")

        end_index = start_index + max_results if max_results is not None else len(data_queries)
        page_queries = data_queries[start_index:end_index]

        for query in page_queries:
            if not isinstance(query, dict):
                raise ErrorCode.InvalidParameterValue("Each DataQuery must be a dict")

            destination = query.get("Destination")
            qid = query.get("Id")
            metric = query.get("Metric")
            period = query.get("Period")
            source = query.get("Source")
            statistic = query.get("Statistic")

            # Validate types if present
            if destination is not None and not isinstance(destination, str):
                raise ErrorCode.InvalidParameterValue("DataQuery.Destination must be a string")
            if qid is not None and not isinstance(qid, str):
                raise ErrorCode.InvalidParameterValue("DataQuery.Id must be a string")
            if metric is not None and not isinstance(metric, str):
                raise ErrorCode.InvalidParameterValue("DataQuery.Metric must be a string")
            if period is not None and not isinstance(period, str):
                raise ErrorCode.InvalidParameterValue("DataQuery.Period must be a string")
            if source is not None and not isinstance(source, str):
                raise ErrorCode.InvalidParameterValue("DataQuery.Source must be a string")
            if statistic is not None and not isinstance(statistic, str):
                raise ErrorCode.InvalidParameterValue("DataQuery.Statistic must be a string")

            # Generate dummy metricPointSet with 3 points between start_time and end_time or now
            metric_point_set = []
            now = datetime.utcnow()
            base_start = start_time or (now.replace(minute=0, second=0, microsecond=0))
            base_end = end_time or now

            # If start > end, no points
            if base_start > base_end:
                metric_point_set = []
            else:
                # Generate 3 points evenly spaced
                total_seconds = (base_end - base_start).total_seconds()
                intervals = [0, total_seconds / 2, total_seconds]
                for offset in intervals:
                    point_start = base_start + timedelta(seconds=offset)
                    point_end = point_start + timedelta(minutes=5)  # 5 minutes duration for example
                    metric_point_set.append({
                        "startDate": point_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z",
                        "endDate": point_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z",
                        "status": "OK",
                        "value": 10.0 + offset  # dummy value
                    })

            data_response_set.append({
                "destination": destination,
                "id": qid,
                "metric": metric,
                "metricPointSet": metric_point_set,
                "period": period,
                "source": source,
                "statistic": statistic,
            })

        new_next_token = str(end_index) if end_index < len(data_queries) else None

        return {
            "dataResponseSet": data_response_set,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

from emulator_core.gateway.base import BaseGateway

class InfrastructurePerformanceGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("DescribeAwsNetworkPerformanceMetricSubscriptions", self.describe_aws_network_performance_metric_subscriptions)
        self.register_action("DisableAwsNetworkPerformanceMetricSubscription", self.disable_aws_network_performance_metric_subscription)
        self.register_action("EnableAwsNetworkPerformanceMetricSubscription", self.enable_aws_network_performance_metric_subscription)
        self.register_action("GetAwsNetworkPerformanceData", self.get_aws_network_performance_data)

    def describe_aws_network_performance_metric_subscriptions(self, params):
        return self.backend.describe_aws_network_performance_metric_subscriptions(params)

    def disable_aws_network_performance_metric_subscription(self, params):
        return self.backend.disable_aws_network_performance_metric_subscription(params)

    def enable_aws_network_performance_metric_subscription(self, params):
        return self.backend.enable_aws_network_performance_metric_subscription(params)

    def get_aws_network_performance_data(self, params):
        return self.backend.get_aws_network_performance_data(params)
