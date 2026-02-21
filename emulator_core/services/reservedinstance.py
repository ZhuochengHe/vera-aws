from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
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
class ReservedInstance:
    availability_zone: str = ""
    availability_zone_id: str = ""
    currency_code: str = ""
    duration: int = 0
    end: str = ""
    fixed_price: str = ""
    instance_count: int = 0
    instance_tenancy: str = ""
    instance_type: str = ""
    offering_class: str = ""
    offering_type: str = ""
    product_description: str = ""
    recurring_charges: List[Any] = field(default_factory=list)
    reserved_instances_id: str = ""
    scope: str = ""
    start: str = ""
    state: str = ""
    tag_set: List[Any] = field(default_factory=list)
    usage_price: str = ""


    def to_dict(self) -> Dict[str, Any]:
        return {
            "availabilityZone": self.availability_zone,
            "availabilityZoneId": self.availability_zone_id,
            "currencyCode": self.currency_code,
            "duration": self.duration,
            "end": self.end,
            "fixedPrice": self.fixed_price,
            "instanceCount": self.instance_count,
            "instanceTenancy": self.instance_tenancy,
            "instanceType": self.instance_type,
            "offeringClass": self.offering_class,
            "offeringType": self.offering_type,
            "productDescription": self.product_description,
            "recurringCharges": self.recurring_charges,
            "reservedInstancesId": self.reserved_instances_id,
            "scope": self.scope,
            "start": self.start,
            "state": self.state,
            "tagSet": self.tag_set,
            "usagePrice": self.usage_price,
        }

class ReservedInstance_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.reserved_instances  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.fast_snapshot_restores.get(params['availability_zone_id']).reserved_instance_ids.append(new_id)
    #   Delete: self.state.fast_snapshot_restores.get(resource.availability_zone_id).reserved_instance_ids.remove(resource_id)


    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for key in required:
            value = params.get(key)
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                return create_error_response("MissingParameter", f"Missing required parameter: {key}")
        return None

    def _get_reserved_instance_or_error(self, reserved_instance_id: str, error_code: str = "InvalidReservedInstancesId.NotFound") -> Any:
        resource = self.resources.get(reserved_instance_id)
        if not resource:
            return create_error_response(error_code, f"The ID '{reserved_instance_id}' does not exist")
        return resource

    def _ensure_reserved_instances_exist(self, reserved_instance_ids: List[str], error_code: str = "InvalidReservedInstancesId.NotFound") -> Optional[Dict[str, Any]]:
        for reserved_instance_id in reserved_instance_ids:
            if reserved_instance_id not in self.resources:
                return create_error_response(error_code, f"The ID '{reserved_instance_id}' does not exist")
        return None


    def AcceptReservedInstancesExchangeQuote(self, params: Dict[str, Any]):
        """Accepts the Convertible Reserved Instance exchange quote described in theGetReservedInstancesExchangeQuotecall."""

        error = self._require_params(params, ["ReservedInstanceId.N"])
        if error:
            return error

        reserved_instance_ids = params.get("ReservedInstanceId.N") or []
        error = self._ensure_reserved_instances_exist(reserved_instance_ids)
        if error:
            return error

        target_configurations = params.get("TargetConfiguration.N") or []
        exchange_id = self._generate_id("riex")

        if target_configurations:
            now_dt = datetime.now(timezone.utc)
            for target_config in target_configurations:
                if not isinstance(target_config, dict):
                    continue
                instance_count = int(target_config.get("InstanceCount") or 0)
                if instance_count <= 0:
                    continue

                duration = int(target_config.get("Duration") or 0)
                end_time = (now_dt + timedelta(seconds=duration)).isoformat() if duration else now_dt.isoformat()

                reserved_instance_id = self._generate_id("reserved")
                resource = ReservedInstance(
                    availability_zone=target_config.get("AvailabilityZone", ""),
                    availability_zone_id=target_config.get("AvailabilityZoneId", ""),
                    currency_code=target_config.get("CurrencyCode", ""),
                    duration=duration,
                    end=end_time,
                    fixed_price=str(target_config.get("FixedPrice", "")) if target_config.get("FixedPrice") is not None else "",
                    instance_count=instance_count,
                    instance_tenancy=target_config.get("InstanceTenancy", ""),
                    instance_type=target_config.get("InstanceType", ""),
                    offering_class=target_config.get("OfferingClass", ""),
                    offering_type=target_config.get("OfferingType", ""),
                    product_description=target_config.get("ProductDescription", ""),
                    recurring_charges=target_config.get("RecurringCharges", []) or [],
                    reserved_instances_id=reserved_instance_id,
                    scope=target_config.get("Scope", ""),
                    start=now_dt.isoformat(),
                    state="active",
                    tag_set=target_config.get("TagSet", []) or [],
                    usage_price=str(target_config.get("UsagePrice", "")) if target_config.get("UsagePrice") is not None else "",
                )
                self.resources[reserved_instance_id] = resource

                parent = self.state.fast_snapshot_restores.get(resource.availability_zone_id)
                if parent and hasattr(parent, "reserved_instance_ids"):
                    parent.reserved_instance_ids.append(reserved_instance_id)

        for resource_id in reserved_instance_ids:
            resource = self.resources.get(resource_id)
            if not resource:
                continue
            resource.state = "exchanged"

        return {
            "exchangeId": exchange_id,
        }

    def CancelReservedInstancesListing(self, params: Dict[str, Any]):
        """Cancels the specified Reserved Instance listing in the Reserved Instance
      Marketplace. For more information, seeSell in the Reserved Instance
        Marketplacein theAmazon EC2 User Guide."""

        error = self._require_params(params, ["ReservedInstancesListingId"])
        if error:
            return error

        listing_store = getattr(self.state, "reserved_instances_listings", None)
        if listing_store is None:
            listing_store = {}

        listing_id = params.get("ReservedInstancesListingId")
        listing = listing_store.get(listing_id)
        if not listing:
            return create_error_response("InvalidReservedInstancesListingId.NotFound", f"The ID '{listing_id}' does not exist")

        listing["status"] = "cancelled"
        listing["statusMessage"] = ""
        listing["updateDate"] = datetime.now(timezone.utc).isoformat()
        listing_store[listing_id] = listing

        return {
            "reservedInstancesListingsSet": [listing],
        }

    def CreateReservedInstancesListing(self, params: Dict[str, Any]):
        """Creates a listing for Amazon EC2 Standard Reserved Instances to be sold in the Reserved
      Instance Marketplace. You can submit one Standard Reserved Instance listing at a time. To get
      a list of your Standard Reserved Instances, you can use theDescribeReservedInstancesoperation. Only Standa"""

        error = self._require_params(params, ["ClientToken", "InstanceCount", "PriceSchedules.N", "ReservedInstancesId"])
        if error:
            return error

        reserved_instance_id = params.get("ReservedInstancesId")
        resource = self._get_reserved_instance_or_error(reserved_instance_id)
        if is_error_response(resource):
            return resource

        listing_store = getattr(self.state, "reserved_instances_listings", None)
        if listing_store is None:
            listing_store = {}
            setattr(self.state, "reserved_instances_listings", listing_store)

        now = datetime.now(timezone.utc).isoformat()
        instance_count = int(params.get("InstanceCount") or 0)
        price_schedules = params.get("PriceSchedules.N") or []
        listing_id = self._generate_id("ril")

        listing = {
            "clientToken": params.get("ClientToken"),
            "createDate": now,
            "instanceCounts": [{"instanceCount": instance_count}],
            "priceSchedules": price_schedules,
            "reservedInstancesId": reserved_instance_id,
            "reservedInstancesListingId": listing_id,
            "status": "active",
            "statusMessage": "",
            "tagSet": resource.tag_set or [],
            "updateDate": now,
        }
        listing_store[listing_id] = listing

        return {
            "reservedInstancesListingsSet": [listing],
        }

    def DeleteQueuedReservedInstances(self, params: Dict[str, Any]):
        """Deletes the queued purchases for the specified Reserved Instances."""

        error = self._require_params(params, ["ReservedInstancesId.N"])
        if error:
            return error

        reserved_instance_ids = params.get("ReservedInstancesId.N") or []
        error = self._ensure_reserved_instances_exist(reserved_instance_ids)
        if error:
            return error

        successful = []
        failed = []
        for reserved_instance_id in reserved_instance_ids:
            resource = self.resources.get(reserved_instance_id)
            if not resource:
                failed.append({
                    "error": {
                        "code": "InvalidReservedInstancesId.NotFound",
                        "message": f"The ID '{reserved_instance_id}' does not exist",
                    },
                    "reservedInstancesId": reserved_instance_id,
                })
                continue

            del self.resources[reserved_instance_id]
            parent = self.state.fast_snapshot_restores.get(resource.availability_zone_id)
            if parent and hasattr(parent, "reserved_instance_ids") and reserved_instance_id in parent.reserved_instance_ids:
                parent.reserved_instance_ids.remove(reserved_instance_id)
            successful.append({"reservedInstancesId": reserved_instance_id})

        return {
            "failedQueuedPurchaseDeletionSet": failed,
            "successfulQueuedPurchaseDeletionSet": successful,
        }

    def DescribeReservedInstances(self, params: Dict[str, Any]):
        """Describes one or more of the Reserved Instances that you purchased. For more information about Reserved Instances, seeReserved
        Instancesin theAmazon EC2 User Guide. The order of the elements in the response, including those within nested structures,
        might vary. Applications should no"""

        reserved_instance_ids = params.get("ReservedInstancesId.N") or []
        if reserved_instance_ids:
            error = self._ensure_reserved_instances_exist(reserved_instance_ids)
            if error:
                return error

        resources = list(self.resources.values())
        if reserved_instance_ids:
            resources = [resource for resource in resources if resource.reserved_instances_id in reserved_instance_ids]

        resources = apply_filters(resources, params.get("Filter.N", []))

        offering_class = params.get("OfferingClass")
        if offering_class:
            resources = [resource for resource in resources if resource.offering_class == offering_class]

        offering_type = params.get("OfferingType")
        if offering_type:
            resources = [resource for resource in resources if resource.offering_type == offering_type]

        return {
            "reservedInstancesSet": [resource.to_dict() for resource in resources],
        }

    def DescribeReservedInstancesListings(self, params: Dict[str, Any]):
        """Describes your account's Reserved Instance listings in the Reserved Instance
      Marketplace. The Reserved Instance Marketplace matches sellers who want to resell Reserved Instance
      capacity that they no longer need with buyers who want to purchase additional capacity.
      Reserved Instance"""

        listing_store = getattr(self.state, "reserved_instances_listings", None)
        if listing_store is None:
            listing_store = {}

        reserved_instance_id = params.get("ReservedInstancesId")
        if reserved_instance_id:
            resource = self._get_reserved_instance_or_error(reserved_instance_id)
            if is_error_response(resource):
                return resource

        listing_id = params.get("ReservedInstancesListingId")
        if listing_id and listing_id not in listing_store:
            return create_error_response("InvalidReservedInstancesListingId.NotFound", f"The ID '{listing_id}' does not exist")

        listings = list(listing_store.values())
        if reserved_instance_id:
            listings = [listing for listing in listings if listing.get("reservedInstancesId") == reserved_instance_id]
        if listing_id:
            listings = [listing for listing in listings if listing.get("reservedInstancesListingId") == listing_id]

        listings = apply_filters(listings, params.get("Filter.N", []))

        return {
            "reservedInstancesListingsSet": listings,
        }

    def DescribeReservedInstancesModifications(self, params: Dict[str, Any]):
        """Describes the modifications made to your Reserved Instances. If no parameter is specified,
      information about all your Reserved Instances modification requests is returned. If a
      modification ID is specified, only information about the specific modification is
      returned. For more info"""

        modification_store = getattr(self.state, "reserved_instances_modifications", None)
        if modification_store is None:
            modification_store = {}

        modification_ids = params.get("ReservedInstancesModificationId.N") or []
        if modification_ids:
            for modification_id in modification_ids:
                if modification_id not in modification_store:
                    return create_error_response(
                        "InvalidReservedInstancesModificationId.NotFound",
                        f"The ID '{modification_id}' does not exist",
                    )

        modifications = list(modification_store.values())
        if modification_ids:
            modifications = [item for item in modifications if item.get("reservedInstancesModificationId") in modification_ids]

        modifications = apply_filters(modifications, params.get("Filter.N", []))

        return {
            "nextToken": None,
            "reservedInstancesModificationsSet": modifications,
        }

    def DescribeReservedInstancesOfferings(self, params: Dict[str, Any]):
        """Describes Reserved Instance offerings that are available for purchase. With Reserved
      Instances, you purchase the right to launch instances for a period of time. During that time
      period, you do not receive insufficient capacity errors, and you pay a lower usage rate than
      the rate ch"""

        offering_store = getattr(self.state, "reserved_instances_offerings", None)
        if offering_store is None:
            offering_store = {}

        offering_ids = params.get("ReservedInstancesOfferingId.N") or []
        if offering_ids:
            for offering_id in offering_ids:
                if offering_id not in offering_store:
                    return create_error_response(
                        "InvalidReservedInstancesOfferingId.NotFound",
                        f"The ID '{offering_id}' does not exist",
                    )

        def _offering_value(offer: Any, field: str, api_field: str, default: Any = "") -> Any:
            if isinstance(offer, ReservedInstance):
                return getattr(offer, field, default)
            if isinstance(offer, dict):
                value = offer.get(field)
                if value is None:
                    value = offer.get(api_field, default)
                return value
            return default

        offerings = list(offering_store.values())
        if offering_ids:
            offerings = [offer for offer in offerings if _offering_value(offer, "reserved_instances_offering_id", "reservedInstancesOfferingId", None) in offering_ids]

        availability_zone = params.get("AvailabilityZone")
        if availability_zone:
            offerings = [offer for offer in offerings if _offering_value(offer, "availability_zone", "availabilityZone", "") == availability_zone]

        availability_zone_id = params.get("AvailabilityZoneId")
        if availability_zone_id:
            offerings = [offer for offer in offerings if _offering_value(offer, "availability_zone_id", "availabilityZoneId", "") == availability_zone_id]

        instance_tenancy = params.get("InstanceTenancy")
        if instance_tenancy:
            offerings = [offer for offer in offerings if _offering_value(offer, "instance_tenancy", "instanceTenancy", "") == instance_tenancy]

        instance_type = params.get("InstanceType")
        if instance_type:
            offerings = [offer for offer in offerings if _offering_value(offer, "instance_type", "instanceType", "") == instance_type]

        offering_class = params.get("OfferingClass")
        if offering_class:
            offerings = [offer for offer in offerings if _offering_value(offer, "offering_class", "offeringClass", "") == offering_class]

        offering_type = params.get("OfferingType")
        if offering_type:
            offerings = [offer for offer in offerings if _offering_value(offer, "offering_type", "offeringType", "") == offering_type]

        product_description = params.get("ProductDescription")
        if product_description:
            offerings = [offer for offer in offerings if _offering_value(offer, "product_description", "productDescription", "") == product_description]

        min_duration = params.get("MinDuration")
        if min_duration is not None:
            min_duration = int(min_duration)
            offerings = [offer for offer in offerings if int(_offering_value(offer, "duration", "duration", 0) or 0) >= min_duration]

        max_duration = params.get("MaxDuration")
        if max_duration is not None:
            max_duration = int(max_duration)
            offerings = [offer for offer in offerings if int(_offering_value(offer, "duration", "duration", 0) or 0) <= max_duration]

        max_instance_count = params.get("MaxInstanceCount")
        if max_instance_count is not None:
            max_instance_count = int(max_instance_count)
            offerings = [offer for offer in offerings if int(_offering_value(offer, "instance_count", "instanceCount", 0) or 0) <= max_instance_count]

        offerings = apply_filters(offerings, params.get("Filter.N", []))

        max_results = params.get("MaxResults")
        if max_results is not None:
            max_results = int(max_results)
            offerings = offerings[:max_results]

        formatted_offerings = []
        for offer in offerings:
            if isinstance(offer, dict):
                formatted_offerings.append(offer)
            else:
                formatted_offerings.append({
                    "availabilityZone": offer.availability_zone,
                    "availabilityZoneId": offer.availability_zone_id,
                    "currencyCode": offer.currency_code,
                    "duration": offer.duration,
                    "fixedPrice": offer.fixed_price,
                    "instanceTenancy": offer.instance_tenancy,
                    "instanceType": offer.instance_type,
                    "marketplace": "AWS",
                    "offeringClass": offer.offering_class,
                    "offeringType": offer.offering_type,
                    "pricingDetailsSet": [],
                    "productDescription": offer.product_description,
                    "recurringCharges": offer.recurring_charges,
                    "reservedInstancesOfferingId": offer.reserved_instances_id,
                    "scope": offer.scope,
                    "usagePrice": offer.usage_price,
                })

        return {
            "nextToken": None,
            "reservedInstancesOfferingsSet": formatted_offerings,
        }

    def GetReservedInstancesExchangeQuote(self, params: Dict[str, Any]):
        """Returns a quote and exchange information for exchanging one or more specified Convertible
      Reserved Instances for a new Convertible Reserved Instance. If the exchange cannot be
      performed, the reason is returned in the response. UseAcceptReservedInstancesExchangeQuoteto perform the exchang"""

        error = self._require_params(params, ["ReservedInstanceId.N"])
        if error:
            return error

        reserved_instance_ids = params.get("ReservedInstanceId.N") or []
        error = self._ensure_reserved_instances_exist(reserved_instance_ids)
        if error:
            return error

        def _to_float(value: Any) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        resources = [self.resources[resource_id] for resource_id in reserved_instance_ids]
        currency_code = resources[0].currency_code if resources else ""

        reserved_instance_value_set = []
        total_hourly = 0.0
        total_upfront = 0.0
        for resource in resources:
            hourly = _to_float(resource.usage_price)
            upfront = _to_float(resource.fixed_price)
            total_hourly += hourly
            total_upfront += upfront
            reserved_instance_value_set.append({
                "reservationValue": {
                    "hourlyPrice": hourly,
                    "remainingTotalValue": hourly + upfront,
                    "remainingUpfrontValue": upfront,
                },
                "reservedInstanceId": resource.reserved_instances_id,
            })

        target_configurations = params.get("TargetConfiguration.N") or []
        target_configuration_value_set = []
        target_total_hourly = 0.0
        target_total_upfront = 0.0
        for target_config in target_configurations:
            target_configuration_value_set.append({
                "reservationValue": {
                    "hourlyPrice": 0.0,
                    "remainingTotalValue": 0.0,
                    "remainingUpfrontValue": 0.0,
                },
                "targetConfiguration": target_config,
            })

        output_expiry = max((resource.end for resource in resources if resource.end), default="")

        return {
            "currencyCode": currency_code,
            "isValidExchange": True,
            "outputReservedInstancesWillExpireAt": output_expiry,
            "paymentDue": 0.0,
            "reservedInstanceValueRollup": {
                "hourlyPrice": total_hourly,
                "remainingTotalValue": total_hourly + total_upfront,
                "remainingUpfrontValue": total_upfront,
            },
            "reservedInstanceValueSet": reserved_instance_value_set,
            "targetConfigurationValueRollup": {
                "hourlyPrice": target_total_hourly,
                "remainingTotalValue": target_total_hourly + target_total_upfront,
                "remainingUpfrontValue": target_total_upfront,
            },
            "targetConfigurationValueSet": target_configuration_value_set,
            "validationFailureReason": None,
        }

    def ModifyReservedInstances(self, params: Dict[str, Any]):
        """Modifies the configuration of your Reserved Instances, such as the Availability Zone,
      instance count, or instance type. The Reserved Instances to be modified must be identical,
      except for Availability Zone, network platform, and instance type. For more information, seeModify Reserved Ins"""

        error = self._require_params(params, ["ReservedInstancesConfigurationSetItemType.N", "ReservedInstancesId.N"])
        if error:
            return error

        reserved_instance_ids = params.get("ReservedInstancesId.N") or []
        error = self._ensure_reserved_instances_exist(reserved_instance_ids)
        if error:
            return error

        configurations = params.get("ReservedInstancesConfigurationSetItemType.N") or []
        now = datetime.now(timezone.utc).isoformat()

        def _config_value(config: Any, field: str) -> Any:
            if isinstance(config, dict):
                return config.get(field) or config.get(field[:1].lower() + field[1:])
            return None

        for resource_id in reserved_instance_ids:
            resource = self.resources[resource_id]
            config = configurations[0] if configurations else {}
            availability_zone = _config_value(config, "AvailabilityZone")
            if availability_zone:
                resource.availability_zone = availability_zone
            instance_type = _config_value(config, "InstanceType")
            if instance_type:
                resource.instance_type = instance_type
            instance_count = _config_value(config, "InstanceCount")
            if instance_count is not None:
                resource.instance_count = int(instance_count)

        modification_id = self._generate_id("rimod")
        modification = {
            "clientToken": params.get("ClientToken"),
            "createDate": now,
            "effectiveDate": now,
            "modificationResultSet": [
                {
                    "reservedInstancesId": resource_id,
                    "targetConfiguration": configurations[0] if configurations else {},
                }
                for resource_id in reserved_instance_ids
            ],
            "reservedInstancesModificationId": modification_id,
            "reservedInstancesSet": [self.resources[resource_id].to_dict() for resource_id in reserved_instance_ids],
            "status": "fulfilled",
            "statusMessage": "",
            "updateDate": now,
        }

        modification_store = getattr(self.state, "reserved_instances_modifications", None)
        if modification_store is None:
            modification_store = {}
            setattr(self.state, "reserved_instances_modifications", modification_store)
        modification_store[modification_id] = modification

        return {
            "reservedInstancesModificationId": modification_id,
        }

    def PurchaseReservedInstancesOffering(self, params: Dict[str, Any]):
        """Purchases a Reserved Instance for use with your account. With Reserved Instances, you pay
      a lower hourly rate compared to On-Demand instance pricing. UseDescribeReservedInstancesOfferingsto get a list of Reserved
      Instance offerings that match your specifications. After you've purchased a"""

        error = self._require_params(params, ["InstanceCount", "ReservedInstancesOfferingId"])
        if error:
            return error

        offering_id = params.get("ReservedInstancesOfferingId")
        offering_store = getattr(self.state, "reserved_instances_offerings", None)
        if offering_store is None:
            offering_store = {}
            setattr(self.state, "reserved_instances_offerings", offering_store)

        offering = offering_store.get(offering_id)
        if not offering:
            return create_error_response("InvalidReservedInstancesOfferingId.NotFound", f"The ID '{offering_id}' does not exist")

        def _offering_value(field: str, api_field: str, default: Any = "") -> Any:
            if isinstance(offering, ReservedInstance):
                return getattr(offering, field, default)
            if isinstance(offering, dict):
                value = offering.get(field)
                if value is None:
                    value = offering.get(api_field, default)
                return value
            return default

        instance_count = int(params.get("InstanceCount") or 0)
        reserved_instance_id = self._generate_id("reserved")
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        duration = int(_offering_value("duration", "duration", 0) or 0)
        end_time = (now_dt + timedelta(seconds=duration)).isoformat() if duration else now

        fixed_price = _offering_value("fixed_price", "fixedPrice", "")
        usage_price = _offering_value("usage_price", "usagePrice", "")
        recurring_charges = _offering_value("recurring_charges", "recurringCharges", []) or []
        tag_set = _offering_value("tag_set", "tagSet", []) or []

        resource = ReservedInstance(
            availability_zone=_offering_value("availability_zone", "availabilityZone", ""),
            availability_zone_id=_offering_value("availability_zone_id", "availabilityZoneId", ""),
            currency_code=_offering_value("currency_code", "currencyCode", ""),
            duration=duration,
            end=end_time,
            fixed_price="" if fixed_price is None else str(fixed_price),
            instance_count=instance_count,
            instance_tenancy=_offering_value("instance_tenancy", "instanceTenancy", ""),
            instance_type=_offering_value("instance_type", "instanceType", ""),
            offering_class=_offering_value("offering_class", "offeringClass", ""),
            offering_type=_offering_value("offering_type", "offeringType", ""),
            product_description=_offering_value("product_description", "productDescription", ""),
            recurring_charges=recurring_charges,
            reserved_instances_id=reserved_instance_id,
            scope=_offering_value("scope", "scope", ""),
            start=now,
            state="active",
            tag_set=tag_set,
            usage_price="" if usage_price is None else str(usage_price),
        )
        self.resources[reserved_instance_id] = resource

        parent = self.state.fast_snapshot_restores.get(resource.availability_zone_id)
        if parent and hasattr(parent, "reserved_instance_ids"):
            parent.reserved_instance_ids.append(reserved_instance_id)

        return {
            "reservedInstancesId": reserved_instance_id,
        }

    def _generate_id(self, prefix: str = 'reserved') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class reservedinstance_RequestParser:
    @staticmethod
    def parse_accept_reserved_instances_exchange_quote_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ReservedInstanceId.N": get_indexed_list(md, "ReservedInstanceId"),
            "TargetConfiguration.N": get_indexed_list(md, "TargetConfiguration"),
        }

    @staticmethod
    def parse_cancel_reserved_instances_listing_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ReservedInstancesListingId": get_scalar(md, "ReservedInstancesListingId"),
        }

    @staticmethod
    def parse_create_reserved_instances_listing_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "InstanceCount": get_int(md, "InstanceCount"),
            "PriceSchedules.N": get_indexed_list(md, "PriceSchedules"),
            "ReservedInstancesId": get_scalar(md, "ReservedInstancesId"),
        }

    @staticmethod
    def parse_delete_queued_reserved_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ReservedInstancesId.N": get_indexed_list(md, "ReservedInstancesId"),
        }

    @staticmethod
    def parse_describe_reserved_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "OfferingClass": get_scalar(md, "OfferingClass"),
            "OfferingType": get_scalar(md, "OfferingType"),
            "ReservedInstancesId.N": get_indexed_list(md, "ReservedInstancesId"),
        }

    @staticmethod
    def parse_describe_reserved_instances_listings_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "ReservedInstancesId": get_scalar(md, "ReservedInstancesId"),
            "ReservedInstancesListingId": get_scalar(md, "ReservedInstancesListingId"),
        }

    @staticmethod
    def parse_describe_reserved_instances_modifications_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "NextToken": get_scalar(md, "NextToken"),
            "ReservedInstancesModificationId.N": get_indexed_list(md, "ReservedInstancesModificationId"),
        }

    @staticmethod
    def parse_describe_reserved_instances_offerings_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "AvailabilityZone": get_scalar(md, "AvailabilityZone"),
            "AvailabilityZoneId": get_scalar(md, "AvailabilityZoneId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IncludeMarketplace": get_scalar(md, "IncludeMarketplace"),
            "InstanceTenancy": get_scalar(md, "InstanceTenancy"),
            "InstanceType": get_scalar(md, "InstanceType"),
            "MaxDuration": get_int(md, "MaxDuration"),
            "MaxInstanceCount": get_int(md, "MaxInstanceCount"),
            "MaxResults": get_int(md, "MaxResults"),
            "MinDuration": get_int(md, "MinDuration"),
            "NextToken": get_scalar(md, "NextToken"),
            "OfferingClass": get_scalar(md, "OfferingClass"),
            "OfferingType": get_scalar(md, "OfferingType"),
            "ProductDescription": get_scalar(md, "ProductDescription"),
            "ReservedInstancesOfferingId.N": get_indexed_list(md, "ReservedInstancesOfferingId"),
        }

    @staticmethod
    def parse_get_reserved_instances_exchange_quote_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "ReservedInstanceId.N": get_indexed_list(md, "ReservedInstanceId"),
            "TargetConfiguration.N": get_indexed_list(md, "TargetConfiguration"),
        }

    @staticmethod
    def parse_modify_reserved_instances_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "ReservedInstancesConfigurationSetItemType.N": get_indexed_list(md, "ReservedInstancesConfigurationSetItemType"),
            "ReservedInstancesId.N": get_indexed_list(md, "ReservedInstancesId"),
        }

    @staticmethod
    def parse_purchase_reserved_instances_offering_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "InstanceCount": get_int(md, "InstanceCount"),
            "LimitPrice": get_scalar(md, "LimitPrice"),
            "PurchaseTime": get_scalar(md, "PurchaseTime"),
            "ReservedInstancesOfferingId": get_scalar(md, "ReservedInstancesOfferingId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AcceptReservedInstancesExchangeQuote": reservedinstance_RequestParser.parse_accept_reserved_instances_exchange_quote_request,
            "CancelReservedInstancesListing": reservedinstance_RequestParser.parse_cancel_reserved_instances_listing_request,
            "CreateReservedInstancesListing": reservedinstance_RequestParser.parse_create_reserved_instances_listing_request,
            "DeleteQueuedReservedInstances": reservedinstance_RequestParser.parse_delete_queued_reserved_instances_request,
            "DescribeReservedInstances": reservedinstance_RequestParser.parse_describe_reserved_instances_request,
            "DescribeReservedInstancesListings": reservedinstance_RequestParser.parse_describe_reserved_instances_listings_request,
            "DescribeReservedInstancesModifications": reservedinstance_RequestParser.parse_describe_reserved_instances_modifications_request,
            "DescribeReservedInstancesOfferings": reservedinstance_RequestParser.parse_describe_reserved_instances_offerings_request,
            "GetReservedInstancesExchangeQuote": reservedinstance_RequestParser.parse_get_reserved_instances_exchange_quote_request,
            "ModifyReservedInstances": reservedinstance_RequestParser.parse_modify_reserved_instances_request,
            "PurchaseReservedInstancesOffering": reservedinstance_RequestParser.parse_purchase_reserved_instances_offering_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class reservedinstance_ResponseSerializer:
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
                xml_parts.extend(reservedinstance_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(reservedinstance_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(reservedinstance_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(reservedinstance_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_accept_reserved_instances_exchange_quote_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AcceptReservedInstancesExchangeQuoteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize exchangeId
        _exchangeId_key = None
        if "exchangeId" in data:
            _exchangeId_key = "exchangeId"
        elif "ExchangeId" in data:
            _exchangeId_key = "ExchangeId"
        if _exchangeId_key:
            param_data = data[_exchangeId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<exchangeId>{esc(str(param_data))}</exchangeId>')
        xml_parts.append(f'</AcceptReservedInstancesExchangeQuoteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_cancel_reserved_instances_listing_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CancelReservedInstancesListingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize reservedInstancesListingsSet
        _reservedInstancesListingsSet_key = None
        if "reservedInstancesListingsSet" in data:
            _reservedInstancesListingsSet_key = "reservedInstancesListingsSet"
        elif "ReservedInstancesListingsSet" in data:
            _reservedInstancesListingsSet_key = "ReservedInstancesListingsSet"
        elif "ReservedInstancesListingss" in data:
            _reservedInstancesListingsSet_key = "ReservedInstancesListingss"
        if _reservedInstancesListingsSet_key:
            param_data = data[_reservedInstancesListingsSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservedInstancesListingsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservedInstancesListingsSet>')
            else:
                xml_parts.append(f'{indent_str}<reservedInstancesListingsSet/>')
        xml_parts.append(f'</CancelReservedInstancesListingResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_reserved_instances_listing_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateReservedInstancesListingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize reservedInstancesListingsSet
        _reservedInstancesListingsSet_key = None
        if "reservedInstancesListingsSet" in data:
            _reservedInstancesListingsSet_key = "reservedInstancesListingsSet"
        elif "ReservedInstancesListingsSet" in data:
            _reservedInstancesListingsSet_key = "ReservedInstancesListingsSet"
        elif "ReservedInstancesListingss" in data:
            _reservedInstancesListingsSet_key = "ReservedInstancesListingss"
        if _reservedInstancesListingsSet_key:
            param_data = data[_reservedInstancesListingsSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservedInstancesListingsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservedInstancesListingsSet>')
            else:
                xml_parts.append(f'{indent_str}<reservedInstancesListingsSet/>')
        xml_parts.append(f'</CreateReservedInstancesListingResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_queued_reserved_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteQueuedReservedInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize failedQueuedPurchaseDeletionSet
        _failedQueuedPurchaseDeletionSet_key = None
        if "failedQueuedPurchaseDeletionSet" in data:
            _failedQueuedPurchaseDeletionSet_key = "failedQueuedPurchaseDeletionSet"
        elif "FailedQueuedPurchaseDeletionSet" in data:
            _failedQueuedPurchaseDeletionSet_key = "FailedQueuedPurchaseDeletionSet"
        elif "FailedQueuedPurchaseDeletions" in data:
            _failedQueuedPurchaseDeletionSet_key = "FailedQueuedPurchaseDeletions"
        if _failedQueuedPurchaseDeletionSet_key:
            param_data = data[_failedQueuedPurchaseDeletionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<failedQueuedPurchaseDeletionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</failedQueuedPurchaseDeletionSet>')
            else:
                xml_parts.append(f'{indent_str}<failedQueuedPurchaseDeletionSet/>')
        # Serialize successfulQueuedPurchaseDeletionSet
        _successfulQueuedPurchaseDeletionSet_key = None
        if "successfulQueuedPurchaseDeletionSet" in data:
            _successfulQueuedPurchaseDeletionSet_key = "successfulQueuedPurchaseDeletionSet"
        elif "SuccessfulQueuedPurchaseDeletionSet" in data:
            _successfulQueuedPurchaseDeletionSet_key = "SuccessfulQueuedPurchaseDeletionSet"
        elif "SuccessfulQueuedPurchaseDeletions" in data:
            _successfulQueuedPurchaseDeletionSet_key = "SuccessfulQueuedPurchaseDeletions"
        if _successfulQueuedPurchaseDeletionSet_key:
            param_data = data[_successfulQueuedPurchaseDeletionSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<successfulQueuedPurchaseDeletionSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</successfulQueuedPurchaseDeletionSet>')
            else:
                xml_parts.append(f'{indent_str}<successfulQueuedPurchaseDeletionSet/>')
        xml_parts.append(f'</DeleteQueuedReservedInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_reserved_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeReservedInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize reservedInstancesSet
        _reservedInstancesSet_key = None
        if "reservedInstancesSet" in data:
            _reservedInstancesSet_key = "reservedInstancesSet"
        elif "ReservedInstancesSet" in data:
            _reservedInstancesSet_key = "ReservedInstancesSet"
        elif "ReservedInstancess" in data:
            _reservedInstancesSet_key = "ReservedInstancess"
        if _reservedInstancesSet_key:
            param_data = data[_reservedInstancesSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservedInstancesSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservedInstancesSet>')
            else:
                xml_parts.append(f'{indent_str}<reservedInstancesSet/>')
        xml_parts.append(f'</DescribeReservedInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_reserved_instances_listings_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeReservedInstancesListingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize reservedInstancesListingsSet
        _reservedInstancesListingsSet_key = None
        if "reservedInstancesListingsSet" in data:
            _reservedInstancesListingsSet_key = "reservedInstancesListingsSet"
        elif "ReservedInstancesListingsSet" in data:
            _reservedInstancesListingsSet_key = "ReservedInstancesListingsSet"
        elif "ReservedInstancesListingss" in data:
            _reservedInstancesListingsSet_key = "ReservedInstancesListingss"
        if _reservedInstancesListingsSet_key:
            param_data = data[_reservedInstancesListingsSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservedInstancesListingsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservedInstancesListingsSet>')
            else:
                xml_parts.append(f'{indent_str}<reservedInstancesListingsSet/>')
        xml_parts.append(f'</DescribeReservedInstancesListingsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_reserved_instances_modifications_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeReservedInstancesModificationsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize reservedInstancesModificationsSet
        _reservedInstancesModificationsSet_key = None
        if "reservedInstancesModificationsSet" in data:
            _reservedInstancesModificationsSet_key = "reservedInstancesModificationsSet"
        elif "ReservedInstancesModificationsSet" in data:
            _reservedInstancesModificationsSet_key = "ReservedInstancesModificationsSet"
        elif "ReservedInstancesModificationss" in data:
            _reservedInstancesModificationsSet_key = "ReservedInstancesModificationss"
        if _reservedInstancesModificationsSet_key:
            param_data = data[_reservedInstancesModificationsSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservedInstancesModificationsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservedInstancesModificationsSet>')
            else:
                xml_parts.append(f'{indent_str}<reservedInstancesModificationsSet/>')
        xml_parts.append(f'</DescribeReservedInstancesModificationsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_reserved_instances_offerings_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeReservedInstancesOfferingsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize reservedInstancesOfferingsSet
        _reservedInstancesOfferingsSet_key = None
        if "reservedInstancesOfferingsSet" in data:
            _reservedInstancesOfferingsSet_key = "reservedInstancesOfferingsSet"
        elif "ReservedInstancesOfferingsSet" in data:
            _reservedInstancesOfferingsSet_key = "ReservedInstancesOfferingsSet"
        elif "ReservedInstancesOfferingss" in data:
            _reservedInstancesOfferingsSet_key = "ReservedInstancesOfferingss"
        if _reservedInstancesOfferingsSet_key:
            param_data = data[_reservedInstancesOfferingsSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservedInstancesOfferingsSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservedInstancesOfferingsSet>')
            else:
                xml_parts.append(f'{indent_str}<reservedInstancesOfferingsSet/>')
        xml_parts.append(f'</DescribeReservedInstancesOfferingsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_reserved_instances_exchange_quote_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetReservedInstancesExchangeQuoteResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize currencyCode
        _currencyCode_key = None
        if "currencyCode" in data:
            _currencyCode_key = "currencyCode"
        elif "CurrencyCode" in data:
            _currencyCode_key = "CurrencyCode"
        if _currencyCode_key:
            param_data = data[_currencyCode_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<currencyCode>{esc(str(param_data))}</currencyCode>')
        # Serialize isValidExchange
        _isValidExchange_key = None
        if "isValidExchange" in data:
            _isValidExchange_key = "isValidExchange"
        elif "IsValidExchange" in data:
            _isValidExchange_key = "IsValidExchange"
        if _isValidExchange_key:
            param_data = data[_isValidExchange_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<isValidExchange>{esc(str(param_data))}</isValidExchange>')
        # Serialize outputReservedInstancesWillExpireAt
        _outputReservedInstancesWillExpireAt_key = None
        if "outputReservedInstancesWillExpireAt" in data:
            _outputReservedInstancesWillExpireAt_key = "outputReservedInstancesWillExpireAt"
        elif "OutputReservedInstancesWillExpireAt" in data:
            _outputReservedInstancesWillExpireAt_key = "OutputReservedInstancesWillExpireAt"
        if _outputReservedInstancesWillExpireAt_key:
            param_data = data[_outputReservedInstancesWillExpireAt_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<outputReservedInstancesWillExpireAt>{esc(str(param_data))}</outputReservedInstancesWillExpireAt>')
        # Serialize paymentDue
        _paymentDue_key = None
        if "paymentDue" in data:
            _paymentDue_key = "paymentDue"
        elif "PaymentDue" in data:
            _paymentDue_key = "PaymentDue"
        if _paymentDue_key:
            param_data = data[_paymentDue_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<paymentDue>{esc(str(param_data))}</paymentDue>')
        # Serialize reservedInstanceValueRollup
        _reservedInstanceValueRollup_key = None
        if "reservedInstanceValueRollup" in data:
            _reservedInstanceValueRollup_key = "reservedInstanceValueRollup"
        elif "ReservedInstanceValueRollup" in data:
            _reservedInstanceValueRollup_key = "ReservedInstanceValueRollup"
        if _reservedInstanceValueRollup_key:
            param_data = data[_reservedInstanceValueRollup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<reservedInstanceValueRollup>')
            xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</reservedInstanceValueRollup>')
        # Serialize reservedInstanceValueSet
        _reservedInstanceValueSet_key = None
        if "reservedInstanceValueSet" in data:
            _reservedInstanceValueSet_key = "reservedInstanceValueSet"
        elif "ReservedInstanceValueSet" in data:
            _reservedInstanceValueSet_key = "ReservedInstanceValueSet"
        elif "ReservedInstanceValues" in data:
            _reservedInstanceValueSet_key = "ReservedInstanceValues"
        if _reservedInstanceValueSet_key:
            param_data = data[_reservedInstanceValueSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<reservedInstanceValueSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</reservedInstanceValueSet>')
            else:
                xml_parts.append(f'{indent_str}<reservedInstanceValueSet/>')
        # Serialize targetConfigurationValueRollup
        _targetConfigurationValueRollup_key = None
        if "targetConfigurationValueRollup" in data:
            _targetConfigurationValueRollup_key = "targetConfigurationValueRollup"
        elif "TargetConfigurationValueRollup" in data:
            _targetConfigurationValueRollup_key = "TargetConfigurationValueRollup"
        if _targetConfigurationValueRollup_key:
            param_data = data[_targetConfigurationValueRollup_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<targetConfigurationValueRollup>')
            xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</targetConfigurationValueRollup>')
        # Serialize targetConfigurationValueSet
        _targetConfigurationValueSet_key = None
        if "targetConfigurationValueSet" in data:
            _targetConfigurationValueSet_key = "targetConfigurationValueSet"
        elif "TargetConfigurationValueSet" in data:
            _targetConfigurationValueSet_key = "TargetConfigurationValueSet"
        elif "TargetConfigurationValues" in data:
            _targetConfigurationValueSet_key = "TargetConfigurationValues"
        if _targetConfigurationValueSet_key:
            param_data = data[_targetConfigurationValueSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<targetConfigurationValueSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(reservedinstance_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</targetConfigurationValueSet>')
            else:
                xml_parts.append(f'{indent_str}<targetConfigurationValueSet/>')
        # Serialize validationFailureReason
        _validationFailureReason_key = None
        if "validationFailureReason" in data:
            _validationFailureReason_key = "validationFailureReason"
        elif "ValidationFailureReason" in data:
            _validationFailureReason_key = "ValidationFailureReason"
        if _validationFailureReason_key:
            param_data = data[_validationFailureReason_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<validationFailureReason>{esc(str(param_data))}</validationFailureReason>')
        xml_parts.append(f'</GetReservedInstancesExchangeQuoteResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_reserved_instances_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyReservedInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize reservedInstancesModificationId
        _reservedInstancesModificationId_key = None
        if "reservedInstancesModificationId" in data:
            _reservedInstancesModificationId_key = "reservedInstancesModificationId"
        elif "ReservedInstancesModificationId" in data:
            _reservedInstancesModificationId_key = "ReservedInstancesModificationId"
        if _reservedInstancesModificationId_key:
            param_data = data[_reservedInstancesModificationId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<reservedInstancesModificationId>{esc(str(param_data))}</reservedInstancesModificationId>')
        xml_parts.append(f'</ModifyReservedInstancesResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_purchase_reserved_instances_offering_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<PurchaseReservedInstancesOfferingResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize reservedInstancesId
        _reservedInstancesId_key = None
        if "reservedInstancesId" in data:
            _reservedInstancesId_key = "reservedInstancesId"
        elif "ReservedInstancesId" in data:
            _reservedInstancesId_key = "ReservedInstancesId"
        if _reservedInstancesId_key:
            param_data = data[_reservedInstancesId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<reservedInstancesId>{esc(str(param_data))}</reservedInstancesId>')
        xml_parts.append(f'</PurchaseReservedInstancesOfferingResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AcceptReservedInstancesExchangeQuote": reservedinstance_ResponseSerializer.serialize_accept_reserved_instances_exchange_quote_response,
            "CancelReservedInstancesListing": reservedinstance_ResponseSerializer.serialize_cancel_reserved_instances_listing_response,
            "CreateReservedInstancesListing": reservedinstance_ResponseSerializer.serialize_create_reserved_instances_listing_response,
            "DeleteQueuedReservedInstances": reservedinstance_ResponseSerializer.serialize_delete_queued_reserved_instances_response,
            "DescribeReservedInstances": reservedinstance_ResponseSerializer.serialize_describe_reserved_instances_response,
            "DescribeReservedInstancesListings": reservedinstance_ResponseSerializer.serialize_describe_reserved_instances_listings_response,
            "DescribeReservedInstancesModifications": reservedinstance_ResponseSerializer.serialize_describe_reserved_instances_modifications_response,
            "DescribeReservedInstancesOfferings": reservedinstance_ResponseSerializer.serialize_describe_reserved_instances_offerings_response,
            "GetReservedInstancesExchangeQuote": reservedinstance_ResponseSerializer.serialize_get_reserved_instances_exchange_quote_response,
            "ModifyReservedInstances": reservedinstance_ResponseSerializer.serialize_modify_reserved_instances_response,
            "PurchaseReservedInstancesOffering": reservedinstance_ResponseSerializer.serialize_purchase_reserved_instances_offering_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

