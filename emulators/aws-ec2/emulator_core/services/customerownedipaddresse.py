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
class CustomerOwnedIpAddresse:
    local_gateway_route_table_id: str = ""
    pool_arn: str = ""
    pool_cidr_set: List[Any] = field(default_factory=list)
    pool_id: str = ""
    tag_set: List[Any] = field(default_factory=list)
    coip_address_usage_set: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "localGatewayRouteTableId": self.local_gateway_route_table_id,
            "poolArn": self.pool_arn,
            "poolCidrSet": self.pool_cidr_set,
            "poolId": self.pool_id,
            "tagSet": self.tag_set,
            "coipAddressUsageSet": self.coip_address_usage_set,
        }

class CustomerOwnedIpAddresse_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.customer_owned_ip_addresses  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]) -> Optional[Dict[str, Any]]:
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _get_pool_or_error(self, pool_id: str) -> (Optional[CustomerOwnedIpAddresse], Optional[Dict[str, Any]]):
        pool = self.resources.get(pool_id)
        if not pool:
            return None, create_error_response(
                "InvalidCoipPoolId.NotFound",
                f"The ID '{pool_id}' does not exist",
            )
        return pool, None

    def _find_cidr_entry(self, pool: CustomerOwnedIpAddresse, cidr: str) -> Optional[Dict[str, Any]]:
        for entry in pool.pool_cidr_set:
            if entry.get("cidr") == cidr:
                return entry
        return None

    def CreateCoipCidr(self, params: Dict[str, Any]):
        """Creates a range of customer-owned IP addresses."""

        error = self._require_params(params, ["Cidr", "CoipPoolId"])
        if error:
            return error

        cidr = params.get("Cidr")
        pool_id = params.get("CoipPoolId")
        pool, error = self._get_pool_or_error(pool_id)
        if error:
            return error

        if self._find_cidr_entry(pool, cidr):
            return create_error_response(
                "InvalidParameterValue",
                f"CIDR '{cidr}' already exists in pool '{pool_id}'",
            )

        cidr_entry = {
            "cidr": cidr,
            "coipPoolId": pool_id,
            "localGatewayRouteTableId": pool.local_gateway_route_table_id,
        }
        pool.pool_cidr_set.append(cidr_entry)

        return {
            'coipCidr': {
                'cidr': cidr,
                'coipPoolId': pool_id,
                'localGatewayRouteTableId': pool.local_gateway_route_table_id,
                },
            }

    def CreateCoipPool(self, params: Dict[str, Any]):
        """Creates a pool of customer-owned IP (CoIP) addresses."""

        error = self._require_params(params, ["LocalGatewayRouteTableId"])
        if error:
            return error

        local_gateway_route_table_id = params.get("LocalGatewayRouteTableId")
        lgw_route_table_store = getattr(self.state, "local_gateway_route_tables", None)
        if lgw_route_table_store is not None and local_gateway_route_table_id not in lgw_route_table_store:
            return create_error_response(
                "InvalidLocalGatewayRouteTableId.NotFound",
                f"Local gateway route table '{local_gateway_route_table_id}' does not exist.",
            )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        pool_id = self._generate_id("coip-pool")
        pool_arn = f"arn:aws:ec2:::coip-pool/{pool_id}"
        resource = CustomerOwnedIpAddresse(
            local_gateway_route_table_id=local_gateway_route_table_id,
            pool_arn=pool_arn,
            pool_cidr_set=[],
            pool_id=pool_id,
            tag_set=tag_set,
        )
        self.resources[pool_id] = resource

        return {
            'coipPool': resource.to_dict(),
            }

    def DeleteCoipCidr(self, params: Dict[str, Any]):
        """Deletes a range of customer-owned IP addresses."""

        error = self._require_params(params, ["Cidr", "CoipPoolId"])
        if error:
            return error

        cidr = params.get("Cidr")
        pool_id = params.get("CoipPoolId")
        pool, error = self._get_pool_or_error(pool_id)
        if error:
            return error

        entry = self._find_cidr_entry(pool, cidr)
        if not entry:
            return create_error_response(
                "InvalidParameterValue",
                f"CIDR '{cidr}' does not exist in pool '{pool_id}'",
            )

        pool.pool_cidr_set = [item for item in pool.pool_cidr_set if item.get("cidr") != cidr]

        return {
            'coipCidr': {
                'cidr': cidr,
                'coipPoolId': pool_id,
                'localGatewayRouteTableId': pool.local_gateway_route_table_id,
                },
            }

    def DeleteCoipPool(self, params: Dict[str, Any]):
        """Deletes a pool of customer-owned IP (CoIP) addresses."""

        error = self._require_params(params, ["CoipPoolId"])
        if error:
            return error

        pool_id = params.get("CoipPoolId")
        pool, error = self._get_pool_or_error(pool_id)
        if error:
            return error

        if pool.pool_cidr_set or pool.coip_address_usage_set:
            return create_error_response(
                "DependencyViolation",
                f"CoIP pool '{pool_id}' has allocated CIDRs or addresses.",
            )

        pool_data = pool.to_dict()
        del self.resources[pool_id]

        return {
            'coipPool': pool_data,
            }

    def DescribeCoipPools(self, params: Dict[str, Any]):
        """Describes the specified customer-owned address pools or all of your customer-owned address pools."""

        pool_ids = params.get("PoolId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if pool_ids:
            resources: List[CustomerOwnedIpAddresse] = []
            for pool_id in pool_ids:
                pool = self.resources.get(pool_id)
                if not pool:
                    return create_error_response(
                        "InvalidCoipPoolId.NotFound",
                        f"The ID '{pool_id}' does not exist",
                    )
                resources.append(pool)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        pool_set = [pool.to_dict() for pool in resources[:max_results]]

        return {
            'coipPoolSet': pool_set,
            'nextToken': None,
            }

    def GetCoipPoolUsage(self, params: Dict[str, Any]):
        """Describes the allocations from the specified customer-owned address pool."""

        error = self._require_params(params, ["PoolId"])
        if error:
            return error

        pool_id = params.get("PoolId")
        pool, error = self._get_pool_or_error(pool_id)
        if error:
            return error

        usage_set = apply_filters(pool.coip_address_usage_set, params.get("Filter.N", []))
        max_results = int(params.get("MaxResults") or 100)

        return {
            'coipAddressUsageSet': usage_set[:max_results],
            'coipPoolId': pool.pool_id,
            'localGatewayRouteTableId': pool.local_gateway_route_table_id,
            'nextToken': None,
            }

    def _generate_id(self, prefix: str = 'lgw') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class customerownedipaddresse_RequestParser:
    @staticmethod
    def parse_create_coip_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "CoipPoolId": get_scalar(md, "CoipPoolId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_create_coip_pool_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LocalGatewayRouteTableId": get_scalar(md, "LocalGatewayRouteTableId"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_coip_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "CoipPoolId": get_scalar(md, "CoipPoolId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_delete_coip_pool_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CoipPoolId": get_scalar(md, "CoipPoolId"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_coip_pools_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PoolId.N": get_indexed_list(md, "PoolId"),
        }

    @staticmethod
    def parse_get_coip_pool_usage_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PoolId": get_scalar(md, "PoolId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateCoipCidr": customerownedipaddresse_RequestParser.parse_create_coip_cidr_request,
            "CreateCoipPool": customerownedipaddresse_RequestParser.parse_create_coip_pool_request,
            "DeleteCoipCidr": customerownedipaddresse_RequestParser.parse_delete_coip_cidr_request,
            "DeleteCoipPool": customerownedipaddresse_RequestParser.parse_delete_coip_pool_request,
            "DescribeCoipPools": customerownedipaddresse_RequestParser.parse_describe_coip_pools_request,
            "GetCoipPoolUsage": customerownedipaddresse_RequestParser.parse_get_coip_pool_usage_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class customerownedipaddresse_ResponseSerializer:
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
                xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_coip_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateCoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize coipCidr
        _coipCidr_key = None
        if "coipCidr" in data:
            _coipCidr_key = "coipCidr"
        elif "CoipCidr" in data:
            _coipCidr_key = "CoipCidr"
        if _coipCidr_key:
            param_data = data[_coipCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<coipCidr>')
            xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</coipCidr>')
        xml_parts.append(f'</CreateCoipCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_create_coip_pool_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateCoipPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize coipPool
        _coipPool_key = None
        if "coipPool" in data:
            _coipPool_key = "coipPool"
        elif "CoipPool" in data:
            _coipPool_key = "CoipPool"
        if _coipPool_key:
            param_data = data[_coipPool_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<coipPool>')
            xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</coipPool>')
        xml_parts.append(f'</CreateCoipPoolResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_coip_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteCoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize coipCidr
        _coipCidr_key = None
        if "coipCidr" in data:
            _coipCidr_key = "coipCidr"
        elif "CoipCidr" in data:
            _coipCidr_key = "CoipCidr"
        if _coipCidr_key:
            param_data = data[_coipCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<coipCidr>')
            xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</coipCidr>')
        xml_parts.append(f'</DeleteCoipCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_coip_pool_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteCoipPoolResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize coipPool
        _coipPool_key = None
        if "coipPool" in data:
            _coipPool_key = "coipPool"
        elif "CoipPool" in data:
            _coipPool_key = "CoipPool"
        if _coipPool_key:
            param_data = data[_coipPool_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<coipPool>')
            xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</coipPool>')
        xml_parts.append(f'</DeleteCoipPoolResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_coip_pools_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeCoipPoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize coipPoolSet
        _coipPoolSet_key = None
        if "coipPoolSet" in data:
            _coipPoolSet_key = "coipPoolSet"
        elif "CoipPoolSet" in data:
            _coipPoolSet_key = "CoipPoolSet"
        elif "CoipPools" in data:
            _coipPoolSet_key = "CoipPools"
        if _coipPoolSet_key:
            param_data = data[_coipPoolSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<coipPoolSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</coipPoolSet>')
            else:
                xml_parts.append(f'{indent_str}<coipPoolSet/>')
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
        xml_parts.append(f'</DescribeCoipPoolsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_coip_pool_usage_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetCoipPoolUsageResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize coipAddressUsageSet
        _coipAddressUsageSet_key = None
        if "coipAddressUsageSet" in data:
            _coipAddressUsageSet_key = "coipAddressUsageSet"
        elif "CoipAddressUsageSet" in data:
            _coipAddressUsageSet_key = "CoipAddressUsageSet"
        elif "CoipAddressUsages" in data:
            _coipAddressUsageSet_key = "CoipAddressUsages"
        if _coipAddressUsageSet_key:
            param_data = data[_coipAddressUsageSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<coipAddressUsageSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(customerownedipaddresse_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</coipAddressUsageSet>')
            else:
                xml_parts.append(f'{indent_str}<coipAddressUsageSet/>')
        # Serialize coipPoolId
        _coipPoolId_key = None
        if "coipPoolId" in data:
            _coipPoolId_key = "coipPoolId"
        elif "CoipPoolId" in data:
            _coipPoolId_key = "CoipPoolId"
        if _coipPoolId_key:
            param_data = data[_coipPoolId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<coipPoolId>{esc(str(param_data))}</coipPoolId>')
        # Serialize localGatewayRouteTableId
        _localGatewayRouteTableId_key = None
        if "localGatewayRouteTableId" in data:
            _localGatewayRouteTableId_key = "localGatewayRouteTableId"
        elif "LocalGatewayRouteTableId" in data:
            _localGatewayRouteTableId_key = "LocalGatewayRouteTableId"
        if _localGatewayRouteTableId_key:
            param_data = data[_localGatewayRouteTableId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<localGatewayRouteTableId>{esc(str(param_data))}</localGatewayRouteTableId>')
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
        xml_parts.append(f'</GetCoipPoolUsageResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateCoipCidr": customerownedipaddresse_ResponseSerializer.serialize_create_coip_cidr_response,
            "CreateCoipPool": customerownedipaddresse_ResponseSerializer.serialize_create_coip_pool_response,
            "DeleteCoipCidr": customerownedipaddresse_ResponseSerializer.serialize_delete_coip_cidr_response,
            "DeleteCoipPool": customerownedipaddresse_ResponseSerializer.serialize_delete_coip_pool_response,
            "DescribeCoipPools": customerownedipaddresse_ResponseSerializer.serialize_describe_coip_pools_response,
            "GetCoipPoolUsage": customerownedipaddresse_ResponseSerializer.serialize_get_coip_pool_usage_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

