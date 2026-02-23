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
class SpotInstance:
    actual_block_hourly_price: str = ""
    availability_zone_group: str = ""
    block_duration_minutes: int = 0
    create_time: str = ""
    fault: Dict[str, Any] = field(default_factory=dict)
    instance_id: str = ""
    instance_interruption_behavior: str = ""
    launched_availability_zone: str = ""
    launched_availability_zone_id: str = ""
    launch_group: str = ""
    launch_specification: Dict[str, Any] = field(default_factory=dict)
    product_description: str = ""
    spot_instance_request_id: str = ""
    spot_price: str = ""
    state: str = ""
    status: Dict[str, Any] = field(default_factory=dict)
    tag_set: List[Any] = field(default_factory=list)
    type: str = ""
    valid_from: str = ""
    valid_until: str = ""

    # Internal dependency tracking — not in API response
    instance_ids: List[str] = field(default_factory=list)  # tracks Instance children


    def to_dict(self) -> Dict[str, Any]:
        return {
            "actualBlockHourlyPrice": self.actual_block_hourly_price,
            "availabilityZoneGroup": self.availability_zone_group,
            "blockDurationMinutes": self.block_duration_minutes,
            "createTime": self.create_time,
            "fault": self.fault,
            "instanceId": self.instance_id,
            "instanceInterruptionBehavior": self.instance_interruption_behavior,
            "launchedAvailabilityZone": self.launched_availability_zone,
            "launchedAvailabilityZoneId": self.launched_availability_zone_id,
            "launchGroup": self.launch_group,
            "launchSpecification": self.launch_specification,
            "productDescription": self.product_description,
            "spotInstanceRequestId": self.spot_instance_request_id,
            "spotPrice": self.spot_price,
            "state": self.state,
            "status": self.status,
            "tagSet": self.tag_set,
            "type": self.type,
            "validFrom": self.valid_from,
            "validUntil": self.valid_until,
        }

class SpotInstance_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.spot_instances  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.instances.get(params['instance_id']).spot_instance_ids.append(new_id)
    #   Delete: self.state.instances.get(resource.instance_id).spot_instance_ids.remove(resource_id)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_resource_or_error(
        self,
        store: Dict[str, Any],
        resource_id: str,
        error_code: str,
        message: Optional[str] = None,
    ):
        resource = store.get(resource_id)
        if not resource:
            return None, create_error_response(error_code, message or f"The ID '{resource_id}' does not exist")
        return resource, None

    def _get_resources_by_ids(self, store: Dict[str, Any], resource_ids: List[str], error_code: str):
        resources = []
        for resource_id in resource_ids:
            resource = store.get(resource_id)
            if not resource:
                return None, create_error_response(error_code, f"The ID '{resource_id}' does not exist")
            resources.append(resource)
        return resources, None

    def _paginate(self, items: List[Any], max_results: int, next_token: Optional[str]) -> Dict[str, Any]:
        try:
            start = int(next_token or 0)
        except (TypeError, ValueError):
            start = 0
        if start < 0:
            start = 0
        end = start + max_results
        sliced = items[start:end]
        new_token = str(end) if end < len(items) else None
        return {"items": sliced, "next_token": new_token}

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if resource_type and spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def _get_datafeed_subscription(self) -> Optional[Dict[str, Any]]:
        return getattr(self.state, "spot_datafeed_subscription", None)

    def _set_datafeed_subscription(self, subscription: Dict[str, Any]) -> None:
        setattr(self.state, "spot_datafeed_subscription", subscription)

    def _clear_datafeed_subscription(self) -> None:
        setattr(self.state, "spot_datafeed_subscription", None)

    def CancelSpotInstanceRequests(self, params: Dict[str, Any]):
        """Cancels one or more Spot Instance requests. Canceling a Spot Instance request does not terminate running Spot Instances
                associated with the request."""

        error = self._require_params(params, ["SpotInstanceRequestId.N"])
        if error:
            return error

        request_ids = params.get("SpotInstanceRequestId.N", []) or []
        resources, error = self._get_resources_by_ids(
            self.resources,
            request_ids,
            "InvalidSpotInstanceRequestID.NotFound",
        )
        if error:
            return error

        for resource in resources:
            resource.state = "cancelled"
            resource.status = {
                "code": "canceled",
                "message": "Your Spot Instance request has been canceled",
                "updateTime": self._utc_now(),
            }

        return {
            'spotInstanceRequestSet': [
                {
                    "spotInstanceRequestId": resource.spot_instance_request_id,
                    "state": resource.state,
                }
                for resource in resources
            ],
            }

    def CreateSpotDatafeedSubscription(self, params: Dict[str, Any]):
        """Creates a data feed for Spot Instances, enabling you to view Spot Instance usage logs.
            You can create one data feed per AWS account. For more information, seeSpot Instance data feedin theAmazon EC2 User Guide."""

        error = self._require_params(params, ["Bucket"])
        if error:
            return error

        existing = self._get_datafeed_subscription()
        if existing:
            return create_error_response(
                "InvalidSpotDatafeedSubscription.Duplicate",
                "Spot datafeed subscription already exists",
            )

        bucket = params.get("Bucket")
        prefix = params.get("Prefix") or ""
        owner_id = getattr(self.state, "account_id", "000000000000")
        subscription = {
            "bucket": bucket,
            "fault": {"code": "", "message": ""},
            "ownerId": owner_id,
            "prefix": prefix,
            "state": "Active",
        }
        self._set_datafeed_subscription(subscription)

        return {
            'spotDatafeedSubscription': subscription,
            }

    def DeleteSpotDatafeedSubscription(self, params: Dict[str, Any]):
        """Deletes the data feed for Spot Instances."""

        subscription = self._get_datafeed_subscription()
        if not subscription:
            return create_error_response(
                "InvalidSpotDatafeedSubscription.NotFound",
                "The ID 'spot-datafeed-subscription' does not exist",
            )

        self._clear_datafeed_subscription()

        return {
            'return': True,
            }

    def DescribeSpotDatafeedSubscription(self, params: Dict[str, Any]):
        """Describes the data feed for Spot Instances. For more information, seeSpot
            Instance data feedin theAmazon EC2 User Guide."""

        subscription = self._get_datafeed_subscription()
        if not subscription:
            return create_error_response(
                "InvalidSpotDatafeedSubscription.NotFound",
                "The ID 'spot-datafeed-subscription' does not exist",
            )

        return {
            'spotDatafeedSubscription': subscription,
            }

    def DescribeSpotInstanceRequests(self, params: Dict[str, Any]):
        """Describes the specified Spot Instance requests. You can useDescribeSpotInstanceRequeststo find a running Spot Instance by
            examining the response. If the status of the Spot Instance isfulfilled, the
            instance ID appears in the response and contains the identifier of the instanc"""

        request_ids = params.get("SpotInstanceRequestId.N", []) or []
        if request_ids:
            resources, error = self._get_resources_by_ids(
                self.resources,
                request_ids,
                "InvalidSpotInstanceRequestID.NotFound",
            )
            if error:
                return error
        else:
            resources = list(self.resources.values())

        filtered = apply_filters(resources, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or 100)
        pagination = self._paginate(filtered, max_results, params.get("NextToken"))
        page = pagination["items"]
        next_token = pagination["next_token"]

        return {
            'nextToken': next_token,
            'spotInstanceRequestSet': [resource.to_dict() for resource in page],
            }

    def DescribeSpotPriceHistory(self, params: Dict[str, Any]):
        """Describes the Spot price history. For more information, seeSpot Instance pricing historyin theAmazon EC2 User Guide. When you specify a start and end time, the operation returns the prices of the
            instance types within that time range. It also returns the last price change before the
    """

        availability_zone = params.get("AvailabilityZone")
        availability_zone_id = params.get("AvailabilityZoneId")
        instance_types = params.get("InstanceType.N", []) or []
        product_descriptions = params.get("ProductDescription.N", []) or []

        history_items: List[Dict[str, Any]] = []
        for resource in self.resources.values():
            instance_type = ""
            if isinstance(resource.launch_specification, dict):
                instance_type = resource.launch_specification.get("InstanceType") or ""
            item = {
                "availabilityZone": resource.launched_availability_zone or availability_zone or "",
                "availabilityZoneId": resource.launched_availability_zone_id or availability_zone_id or "",
                "instanceType": instance_type,
                "productDescription": resource.product_description,
                "spotPrice": resource.spot_price,
                "timestamp": resource.create_time or self._utc_now(),
            }
            history_items.append(item)

        if availability_zone:
            history_items = [item for item in history_items if item["availabilityZone"] == availability_zone]
        if availability_zone_id:
            history_items = [item for item in history_items if item["availabilityZoneId"] == availability_zone_id]
        if instance_types:
            history_items = [item for item in history_items if item["instanceType"] in instance_types]
        if product_descriptions:
            history_items = [item for item in history_items if item["productDescription"] in product_descriptions]

        history_items = apply_filters(history_items, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or 100)
        pagination = self._paginate(history_items, max_results, params.get("NextToken"))

        return {
            'nextToken': pagination["next_token"],
            'spotPriceHistorySet': pagination["items"],
            }

    def GetSpotPlacementScores(self, params: Dict[str, Any]):
        """Calculates the Spot placement score for a Region or Availability Zone based on the
         specified target capacity and compute requirements. You can specify your compute requirements either by usingInstanceRequirementsWithMetadataand letting Amazon EC2 choose the optimal
         instance types t"""

        error = self._require_params(params, ["TargetCapacity"])
        if error:
            return error

        regions = params.get("RegionName.N", []) or []
        if not regions:
            regions = ["us-east-1"]

        single_az = str2bool(params.get("SingleAvailabilityZone"))
        placement_scores: List[Dict[str, Any]] = []
        for region in regions:
            if single_az:
                placement_scores.append(
                    {
                        "availabilityZoneId": f"{region}-az1",
                        "region": region,
                        "score": "10",
                    }
                )
            else:
                placement_scores.append(
                    {
                        "availabilityZoneId": "",
                        "region": region,
                        "score": "10",
                    }
                )

        max_results = int(params.get("MaxResults") or 100)
        pagination = self._paginate(placement_scores, max_results, params.get("NextToken"))

        return {
            'nextToken': pagination["next_token"],
            'spotPlacementScoreSet': pagination["items"],
            }

    def RequestSpotInstances(self, params: Dict[str, Any]):
        """Creates a Spot Instance request. For more information, seeWork with Spot Instancein
            theAmazon EC2 User Guide. We strongly discourage using the RequestSpotInstances API because it is a legacy
                API with no planned investment. For options for requesting Spot Instances, seeWhi"""

        instance_count = int(params.get("InstanceCount") or 1)
        if instance_count <= 0:
            return create_error_response(
                "InvalidParameterValue",
                "InstanceCount must be greater than 0",
            )

        now = self._utc_now()
        availability_zone_group = params.get("AvailabilityZoneGroup") or ""
        block_duration_minutes = int(params.get("BlockDurationMinutes") or 0)
        instance_interruption_behavior = params.get("InstanceInterruptionBehavior") or ""
        launch_group = params.get("LaunchGroup") or ""
        launch_specification = params.get("LaunchSpecification") or {}
        spot_price = params.get("SpotPrice") or ""
        request_type = params.get("Type") or "one-time"
        valid_from = params.get("ValidFrom") or ""
        valid_until = params.get("ValidUntil") or ""
        tag_set = self._extract_tags(params.get("TagSpecification.N", []), "spot-instances-request")

        created = []
        for _ in range(instance_count):
            request_id = self._generate_id("sir")
            resource = SpotInstance(
                actual_block_hourly_price=spot_price,
                availability_zone_group=availability_zone_group,
                block_duration_minutes=block_duration_minutes,
                create_time=now,
                fault={},
                instance_id="",
                instance_interruption_behavior=instance_interruption_behavior,
                launched_availability_zone="",
                launched_availability_zone_id="",
                launch_group=launch_group,
                launch_specification=launch_specification,
                product_description="",
                spot_instance_request_id=request_id,
                spot_price=spot_price,
                state="open",
                status={"code": "pending-evaluation", "message": "Pending evaluation", "updateTime": now},
                tag_set=list(tag_set),
                type=request_type,
                valid_from=valid_from,
                valid_until=valid_until,
            )
            self.resources[request_id] = resource
            if resource.instance_id:
                parent = self.state.instances.get(resource.instance_id)
                if parent and hasattr(parent, "spot_instance_ids"):
                    parent.spot_instance_ids.append(request_id)
            created.append(resource.to_dict())

        return {
            'spotInstanceRequestSet': created,
            }

    def _generate_id(self, prefix: str = 'spot') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class spotinstance_RequestParser:
    @staticmethod
    def parse_cancel_spot_instance_requests_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "SpotInstanceRequestId.N": get_indexed_list(md, "SpotInstanceRequestId"),
        }

    @staticmethod
    def parse_create_spot_datafeed_subscription_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Bucket": get_scalar(md, "Bucket"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Prefix": get_scalar(md, "Prefix"),
        }

    @staticmethod
    def parse_delete_spot_datafeed_subscription_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_spot_datafeed_subscription_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_spot_instance_requests_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "SpotInstanceRequestId.N": get_indexed_list(md, "SpotInstanceRequestId"),
        }

    @staticmethod
    def parse_describe_spot_price_history_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndTime": get_scalar(md, "EndTime"),
            "Filter.N": parse_filters(md, "Filter"),
            "InstanceType.N": get_indexed_list(md, "InstanceType"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "ProductDescription.N": get_indexed_list(md, "ProductDescription"),
            "StartTime": get_scalar(md, "StartTime"),
        }

    @staticmethod
    def parse_get_spot_placement_scores_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceRequirementsWithMetadata": get_scalar(md, "InstanceRequirementsWithMetadata"),
            "InstanceType.N": get_indexed_list(md, "InstanceType"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "RegionName.N": get_indexed_list(md, "RegionName"),
            "SingleAvailabilityZone": get_scalar(md, "SingleAvailabilityZone"),
            "TargetCapacity": get_int(md, "TargetCapacity"),
            "TargetCapacityUnitType": get_scalar(md, "TargetCapacityUnitType"),
        }

    @staticmethod
    def parse_request_spot_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZoneGroup": get_scalar(md, "AvailabilityZoneGroup"),
            "BlockDurationMinutes": get_int(md, "BlockDurationMinutes"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceCount": get_int(md, "InstanceCount"),
            "InstanceInterruptionBehavior": get_scalar(md, "InstanceInterruptionBehavior"),
            "LaunchGroup": get_scalar(md, "LaunchGroup"),
            "LaunchSpecification": get_scalar(md, "LaunchSpecification"),
            "SpotPrice": get_scalar(md, "SpotPrice"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "Type": get_scalar(md, "Type"),
            "ValidFrom": get_scalar(md, "ValidFrom"),
            "ValidUntil": get_scalar(md, "ValidUntil"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CancelSpotInstanceRequests": spotinstance_RequestParser.parse_cancel_spot_instance_requests_request,
            "CreateSpotDatafeedSubscription": spotinstance_RequestParser.parse_create_spot_datafeed_subscription_request,
            "DeleteSpotDatafeedSubscription": spotinstance_RequestParser.parse_delete_spot_datafeed_subscription_request,
            "DescribeSpotDatafeedSubscription": spotinstance_RequestParser.parse_describe_spot_datafeed_subscription_request,
            "DescribeSpotInstanceRequests": spotinstance_RequestParser.parse_describe_spot_instance_requests_request,
            "DescribeSpotPriceHistory": spotinstance_RequestParser.parse_describe_spot_price_history_request,
            "GetSpotPlacementScores": spotinstance_RequestParser.parse_get_spot_placement_scores_request,
            "RequestSpotInstances": spotinstance_RequestParser.parse_request_spot_instances_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class spotinstance_ResponseSerializer:
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
                xml_parts.extend(spotinstance_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(spotinstance_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(spotinstance_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(spotinstance_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_cancel_spot_instance_requests_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelSpotInstanceRequestsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize spotInstanceRequestSet
        _spotInstanceRequestSet_key = None
        if "spotInstanceRequestSet" in data:
            _spotInstanceRequestSet_key = "spotInstanceRequestSet"
        elif "SpotInstanceRequestSet" in data:
            _spotInstanceRequestSet_key = "SpotInstanceRequestSet"
        elif "SpotInstanceRequests" in data:
            _spotInstanceRequestSet_key = "SpotInstanceRequests"
        if _spotInstanceRequestSet_key:
            param_data = data[_spotInstanceRequestSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<spotInstanceRequestSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</spotInstanceRequestSet>')
            else:
                xml_parts.append(f'{indent_str}<spotInstanceRequestSet/>')
        xml_parts.append(f'</CancelSpotInstanceRequestsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_spot_datafeed_subscription_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateSpotDatafeedSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize spotDatafeedSubscription
        _spotDatafeedSubscription_key = None
        if "spotDatafeedSubscription" in data:
            _spotDatafeedSubscription_key = "spotDatafeedSubscription"
        elif "SpotDatafeedSubscription" in data:
            _spotDatafeedSubscription_key = "SpotDatafeedSubscription"
        if _spotDatafeedSubscription_key:
            param_data = data[_spotDatafeedSubscription_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<spotDatafeedSubscription>')
            xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</spotDatafeedSubscription>')
        xml_parts.append(f'</CreateSpotDatafeedSubscriptionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_spot_datafeed_subscription_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteSpotDatafeedSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        xml_parts.append(f'</DeleteSpotDatafeedSubscriptionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_spot_datafeed_subscription_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeSpotDatafeedSubscriptionResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize spotDatafeedSubscription
        _spotDatafeedSubscription_key = None
        if "spotDatafeedSubscription" in data:
            _spotDatafeedSubscription_key = "spotDatafeedSubscription"
        elif "SpotDatafeedSubscription" in data:
            _spotDatafeedSubscription_key = "SpotDatafeedSubscription"
        if _spotDatafeedSubscription_key:
            param_data = data[_spotDatafeedSubscription_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<spotDatafeedSubscription>')
            xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</spotDatafeedSubscription>')
        xml_parts.append(f'</DescribeSpotDatafeedSubscriptionResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_spot_instance_requests_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeSpotInstanceRequestsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize spotInstanceRequestSet
        _spotInstanceRequestSet_key = None
        if "spotInstanceRequestSet" in data:
            _spotInstanceRequestSet_key = "spotInstanceRequestSet"
        elif "SpotInstanceRequestSet" in data:
            _spotInstanceRequestSet_key = "SpotInstanceRequestSet"
        elif "SpotInstanceRequests" in data:
            _spotInstanceRequestSet_key = "SpotInstanceRequests"
        if _spotInstanceRequestSet_key:
            param_data = data[_spotInstanceRequestSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<spotInstanceRequestSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</spotInstanceRequestSet>')
            else:
                xml_parts.append(f'{indent_str}<spotInstanceRequestSet/>')
        xml_parts.append(f'</DescribeSpotInstanceRequestsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_spot_price_history_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeSpotPriceHistoryResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize spotPriceHistorySet
        _spotPriceHistorySet_key = None
        if "spotPriceHistorySet" in data:
            _spotPriceHistorySet_key = "spotPriceHistorySet"
        elif "SpotPriceHistorySet" in data:
            _spotPriceHistorySet_key = "SpotPriceHistorySet"
        elif "SpotPriceHistorys" in data:
            _spotPriceHistorySet_key = "SpotPriceHistorys"
        if _spotPriceHistorySet_key:
            param_data = data[_spotPriceHistorySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<spotPriceHistorySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</spotPriceHistorySet>')
            else:
                xml_parts.append(f'{indent_str}<spotPriceHistorySet/>')
        xml_parts.append(f'</DescribeSpotPriceHistoryResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_spot_placement_scores_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetSpotPlacementScoresResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize spotPlacementScoreSet
        _spotPlacementScoreSet_key = None
        if "spotPlacementScoreSet" in data:
            _spotPlacementScoreSet_key = "spotPlacementScoreSet"
        elif "SpotPlacementScoreSet" in data:
            _spotPlacementScoreSet_key = "SpotPlacementScoreSet"
        elif "SpotPlacementScores" in data:
            _spotPlacementScoreSet_key = "SpotPlacementScores"
        if _spotPlacementScoreSet_key:
            param_data = data[_spotPlacementScoreSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<spotPlacementScoreSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</spotPlacementScoreSet>')
            else:
                xml_parts.append(f'{indent_str}<spotPlacementScoreSet/>')
        xml_parts.append(f'</GetSpotPlacementScoresResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_request_spot_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<RequestSpotInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize spotInstanceRequestSet
        _spotInstanceRequestSet_key = None
        if "spotInstanceRequestSet" in data:
            _spotInstanceRequestSet_key = "spotInstanceRequestSet"
        elif "SpotInstanceRequestSet" in data:
            _spotInstanceRequestSet_key = "SpotInstanceRequestSet"
        elif "SpotInstanceRequests" in data:
            _spotInstanceRequestSet_key = "SpotInstanceRequests"
        if _spotInstanceRequestSet_key:
            param_data = data[_spotInstanceRequestSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<spotInstanceRequestSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(spotinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</spotInstanceRequestSet>')
            else:
                xml_parts.append(f'{indent_str}<spotInstanceRequestSet/>')
        xml_parts.append(f'</RequestSpotInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CancelSpotInstanceRequests": spotinstance_ResponseSerializer.serialize_cancel_spot_instance_requests_response,
            "CreateSpotDatafeedSubscription": spotinstance_ResponseSerializer.serialize_create_spot_datafeed_subscription_response,
            "DeleteSpotDatafeedSubscription": spotinstance_ResponseSerializer.serialize_delete_spot_datafeed_subscription_response,
            "DescribeSpotDatafeedSubscription": spotinstance_ResponseSerializer.serialize_describe_spot_datafeed_subscription_response,
            "DescribeSpotInstanceRequests": spotinstance_ResponseSerializer.serialize_describe_spot_instance_requests_response,
            "DescribeSpotPriceHistory": spotinstance_ResponseSerializer.serialize_describe_spot_price_history_response,
            "GetSpotPlacementScores": spotinstance_ResponseSerializer.serialize_get_spot_placement_scores_response,
            "RequestSpotInstances": spotinstance_ResponseSerializer.serialize_request_spot_instances_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

