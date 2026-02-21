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
class BYOIP:
    advertisement_type: str = ""
    asn_association_set: List[Any] = field(default_factory=list)
    cidr: str = ""
    description: str = ""
    network_border_group: str = ""
    state: str = ""
    status_message: str = ""

    resource_type: str = "byoip-cidr"
    pool_id: str = ""
    pool_cidr_block_set: List[Dict[str, Any]] = field(default_factory=list)
    pool_address_range_set: List[Dict[str, Any]] = field(default_factory=list)
    tag_set: List[Dict[str, str]] = field(default_factory=list)
    total_address_count: int = 0
    total_available_address_count: int = 0
    ipv6_cidr_association_set: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "advertisementType": self.advertisement_type,
            "asnAssociationSet": self.asn_association_set,
            "cidr": self.cidr,
            "description": self.description,
            "networkBorderGroup": self.network_border_group,
            "state": self.state,
            "statusMessage": self.status_message,
            "poolId": self.pool_id,
            "poolCidrBlockSet": self.pool_cidr_block_set,
            "poolAddressRangeSet": self.pool_address_range_set,
            "tagSet": self.tag_set,
            "totalAddressCount": self.total_address_count,
            "totalAvailableAddressCount": self.total_available_address_count,
            "ipv6CidrAssociationSet": self.ipv6_cidr_association_set,
        }

class BYOIP_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.byoip  # alias to shared store

    def _find_byoip_by_cidr(self, cidr: str) -> Optional[BYOIP]:
        for resource in self.resources.values():
            if resource.resource_type != "byoip-cidr":
                continue
            if resource.cidr == cidr:
                return resource
        return None

    def _find_pool_by_id(self, pool_id: str, resource_type: Optional[str] = None) -> Optional[BYOIP]:
        for resource in self.resources.values():
            if resource.pool_id != pool_id:
                continue
            if resource_type and resource.resource_type != resource_type:
                continue
            return resource
        return None

    def _list_pools(self, resource_type: str) -> List[BYOIP]:
        return [resource for resource in self.resources.values() if resource.resource_type == resource_type]

    def AdvertiseByoipCidr(self, params: Dict[str, Any]):
        """Advertises an IPv4 or IPv6 address range that is provisioned for use with your AWS resources through 
         bring your own IP addresses (BYOIP). You can perform this operation at most once every 10 seconds, even if you specify different 
         address ranges each time. We recommend that you st"""

        if not params.get("Cidr"):
            return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        cidr = params.get("Cidr")
        resource = self._find_byoip_by_cidr(cidr)
        if not resource:
            return create_error_response(
                "InvalidByoipCidr.NotFound",
                f"The CIDR '{cidr}' does not exist",
            )

        if params.get("NetworkBorderGroup") is not None:
            resource.network_border_group = params.get("NetworkBorderGroup") or resource.network_border_group

        resource.state = "advertised"
        if not resource.advertisement_type:
            resource.advertisement_type = "advertised"

        asn = params.get("Asn")
        if asn:
            association = {
                "asn": asn,
                "cidr": resource.cidr,
                "state": "advertised",
                "statusMessage": "",
            }
            updated = False
            for entry in resource.asn_association_set:
                if entry.get("asn") == asn and entry.get("cidr") == resource.cidr:
                    entry.update(association)
                    updated = True
                    break
            if not updated:
                resource.asn_association_set.append(association)

        return {
            'byoipCidr': resource.to_dict(),
            }

    def DeprovisionByoipCidr(self, params: Dict[str, Any]):
        """Releases the specified address range that you provisioned for use with your AWS resources
         through bring your own IP addresses (BYOIP) and deletes the corresponding address pool. Before you can release an address range, you must stop advertising it and you must not 
          have any IP add"""

        if not params.get("Cidr"):
            return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        cidr = params.get("Cidr")
        resource = self._find_byoip_by_cidr(cidr)
        if not resource:
            return create_error_response(
                "InvalidByoipCidr.NotFound",
                f"The CIDR '{cidr}' does not exist",
            )

        if resource.state == "advertised":
            return create_error_response(
                "DependencyViolation",
                "CIDR is advertised and cannot be deprovisioned.",
            )

        pool_id = resource.pool_id
        for key, value in list(self.resources.items()):
            if value is resource:
                del self.resources[key]
                break

        if pool_id:
            for key, value in list(self.resources.items()):
                if value.pool_id == pool_id and value.resource_type in {"public-ipv4-pool", "ipv6-pool"}:
                    del self.resources[key]

        resource.state = "deprovisioned"

        return {
            'byoipCidr': resource.to_dict(),
            }

    def DescribeByoipCidrs(self, params: Dict[str, Any]):
        """Describes the IP address ranges that were provisioned for use with AWS resources
          through through bring your own IP addresses (BYOIP). To describe the address pools that were created when you provisioned the address
          ranges, useDescribePublicIpv4PoolsorDescribeIpv6Pools."""

        if not params.get("MaxResults"):
            return create_error_response("MissingParameter", "Missing required parameter: MaxResults")

        max_results = int(params.get("MaxResults") or 100)
        resources = [
            resource for resource in self.resources.values()
            if resource.resource_type == "byoip-cidr"
        ]

        byoip_cidrs = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'byoipCidrSet': byoip_cidrs,
            'nextToken': None,
            }

    def DescribeIpv6Pools(self, params: Dict[str, Any]):
        """Describes your IPv6 address pools."""

        pool_ids = params.get("PoolId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if pool_ids:
            resources = []
            for pool_id in pool_ids:
                pool = self._find_pool_by_id(pool_id, resource_type="ipv6-pool")
                if not pool:
                    return create_error_response(
                        "InvalidIpv6PoolID.NotFound",
                        f"The ID '{pool_id}' does not exist",
                    )
                resources.append(pool)
        else:
            resources = self._list_pools("ipv6-pool")

        pool_entries = []
        for resource in resources:
            pool_entries.append({
                "description": resource.description,
                "poolCidrBlockSet": resource.pool_cidr_block_set,
                "poolId": resource.pool_id,
                "pool_id": resource.pool_id,
                "tagSet": resource.tag_set,
            })

        pool_entries = apply_filters(pool_entries, params.get("Filter.N", []))
        for entry in pool_entries:
            entry.pop("pool_id", None)

        return {
            'ipv6PoolSet': pool_entries[:max_results],
            'nextToken': None,
            }

    def DescribePublicIpv4Pools(self, params: Dict[str, Any]):
        """Describes the specified IPv4 address pools."""

        pool_ids = params.get("PoolId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)

        if pool_ids:
            resources = []
            for pool_id in pool_ids:
                pool = self._find_pool_by_id(pool_id, resource_type="public-ipv4-pool")
                if not pool:
                    return create_error_response(
                        "InvalidPublicIpv4PoolID.NotFound",
                        f"The ID '{pool_id}' does not exist",
                    )
                resources.append(pool)
        else:
            resources = self._list_pools("public-ipv4-pool")

        pool_entries = []
        for resource in resources:
            pool_entries.append({
                "description": resource.description,
                "networkBorderGroup": resource.network_border_group,
                "poolAddressRangeSet": resource.pool_address_range_set,
                "poolId": resource.pool_id,
                "pool_id": resource.pool_id,
                "tagSet": resource.tag_set,
                "totalAddressCount": resource.total_address_count,
                "totalAvailableAddressCount": resource.total_available_address_count,
            })

        pool_entries = apply_filters(pool_entries, params.get("Filter.N", []))
        for entry in pool_entries:
            entry.pop("pool_id", None)

        return {
            'nextToken': None,
            'publicIpv4PoolSet': pool_entries[:max_results],
            }

    def GetAssociatedIpv6PoolCidrs(self, params: Dict[str, Any]):
        """Gets information about the IPv6 CIDR block associations for a specified IPv6 address pool."""

        if not params.get("PoolId"):
            return create_error_response("MissingParameter", "Missing required parameter: PoolId")

        pool_id = params.get("PoolId")
        pool = self._find_pool_by_id(pool_id, resource_type="ipv6-pool")
        if not pool:
            return create_error_response(
                "InvalidIpv6PoolID.NotFound",
                f"The ID '{pool_id}' does not exist",
            )

        max_results = int(params.get("MaxResults") or 100)
        association_set = pool.ipv6_cidr_association_set[:max_results]

        return {
            'ipv6CidrAssociationSet': association_set,
            'nextToken': None,
            }

    def ProvisionByoipCidr(self, params: Dict[str, Any]):
        """Provisions an IPv4 or IPv6 address range for use with your AWS resources through bring your own IP 
         addresses (BYOIP) and creates a corresponding address pool. After the address range is
         provisioned, it is ready to be advertised. AWS verifies that you own the address range and are """

        if not params.get("Cidr"):
            return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        cidr = params.get("Cidr")
        if self._find_byoip_by_cidr(cidr):
            return create_error_response(
                "InvalidByoipCidr.Duplicate",
                f"The CIDR '{cidr}' already exists",
            )

        pool_id = self._generate_id("ipv6pool" if ":" in cidr else "ipv4pool")
        tag_specs = params.get("PoolTagSpecification.N", []) or []
        tag_set: List[Dict[str, str]] = []
        if tag_specs:
            matching_tags = None
            for spec in tag_specs:
                if spec.get("ResourceType") in {"ipv6-pool", "public-ipv4-pool"}:
                    matching_tags = spec.get("Tags", [])
                    break
            if matching_tags is None:
                matching_tags = tag_specs[0].get("Tags", [])
            tag_set = matching_tags or []

        byoip_resource = BYOIP(
            advertisement_type="not-advertised",
            asn_association_set=[],
            cidr=cidr,
            description=params.get("Description") or "",
            network_border_group=params.get("NetworkBorderGroup") or "",
            state="provisioned",
            status_message="",
            resource_type="byoip-cidr",
            pool_id=pool_id,
        )

        pool_resource = BYOIP(
            description=byoip_resource.description,
            network_border_group=byoip_resource.network_border_group,
            resource_type="ipv6-pool" if ":" in cidr else "public-ipv4-pool",
            pool_id=pool_id,
            tag_set=tag_set,
        )

        if ":" in cidr:
            pool_resource.pool_cidr_block_set = [{"ipv6Cidr": cidr}]
            pool_resource.ipv6_cidr_association_set = [{
                "associatedResource": "byoip",
                "ipv6Cidr": cidr,
            }]
        else:
            pool_resource.pool_address_range_set = [{"cidr": cidr}]
            pool_resource.total_address_count = 0
            pool_resource.total_available_address_count = 0

        self.resources[self._generate_id("byo")] = byoip_resource
        self.resources[pool_id] = pool_resource

        return {
            'byoipCidr': byoip_resource.to_dict(),
            }

    def WithdrawByoipCidr(self, params: Dict[str, Any]):
        """Stops advertising an address range that is provisioned as an address pool. You can perform this operation at most once every 10 seconds, even if you specify different 
         address ranges each time. It can take a few minutes before traffic to the specified addresses stops routing to AWS
        """

        if not params.get("Cidr"):
            return create_error_response("MissingParameter", "Missing required parameter: Cidr")

        cidr = params.get("Cidr")
        resource = self._find_byoip_by_cidr(cidr)
        if not resource:
            return create_error_response(
                "InvalidByoipCidr.NotFound",
                f"The CIDR '{cidr}' does not exist",
            )

        resource.state = "provisioned"
        resource.advertisement_type = "not-advertised"
        for entry in resource.asn_association_set:
            entry["state"] = "withdrawn"
            entry["statusMessage"] = ""

        return {
            'byoipCidr': resource.to_dict(),
            }

    def _generate_id(self, prefix: str = 'byo') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class byoip_RequestParser:
    @staticmethod
    def parse_advertise_byoip_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Asn": get_scalar(md, "Asn"),
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "NetworkBorderGroup": get_scalar(md, "NetworkBorderGroup"),
        }

    @staticmethod
    def parse_deprovision_byoip_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_describe_byoip_cidrs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
        }

    @staticmethod
    def parse_describe_ipv6_pools_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PoolId.N": get_indexed_list(md, "PoolId"),
        }

    @staticmethod
    def parse_describe_public_ipv4_pools_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PoolId.N": get_indexed_list(md, "PoolId"),
        }

    @staticmethod
    def parse_get_associated_ipv6_pool_cidrs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "PoolId": get_scalar(md, "PoolId"),
        }

    @staticmethod
    def parse_provision_byoip_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "CidrAuthorizationContext": get_scalar(md, "CidrAuthorizationContext"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MultiRegion": get_scalar(md, "MultiRegion"),
            "NetworkBorderGroup": get_scalar(md, "NetworkBorderGroup"),
            "PoolTagSpecification.N": parse_tags(md, "PoolTagSpecification"),
            "PubliclyAdvertisable": get_scalar(md, "PubliclyAdvertisable"),
        }

    @staticmethod
    def parse_withdraw_byoip_cidr_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "Cidr": get_scalar(md, "Cidr"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "AdvertiseByoipCidr": byoip_RequestParser.parse_advertise_byoip_cidr_request,
            "DeprovisionByoipCidr": byoip_RequestParser.parse_deprovision_byoip_cidr_request,
            "DescribeByoipCidrs": byoip_RequestParser.parse_describe_byoip_cidrs_request,
            "DescribeIpv6Pools": byoip_RequestParser.parse_describe_ipv6_pools_request,
            "DescribePublicIpv4Pools": byoip_RequestParser.parse_describe_public_ipv4_pools_request,
            "GetAssociatedIpv6PoolCidrs": byoip_RequestParser.parse_get_associated_ipv6_pool_cidrs_request,
            "ProvisionByoipCidr": byoip_RequestParser.parse_provision_byoip_cidr_request,
            "WithdrawByoipCidr": byoip_RequestParser.parse_withdraw_byoip_cidr_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class byoip_ResponseSerializer:
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
                xml_parts.extend(byoip_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(byoip_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(byoip_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(byoip_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_advertise_byoip_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<AdvertiseByoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoipCidr
        _byoipCidr_key = None
        if "byoipCidr" in data:
            _byoipCidr_key = "byoipCidr"
        elif "ByoipCidr" in data:
            _byoipCidr_key = "ByoipCidr"
        if _byoipCidr_key:
            param_data = data[_byoipCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<byoipCidr>')
            xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</byoipCidr>')
        xml_parts.append(f'</AdvertiseByoipCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_deprovision_byoip_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeprovisionByoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoipCidr
        _byoipCidr_key = None
        if "byoipCidr" in data:
            _byoipCidr_key = "byoipCidr"
        elif "ByoipCidr" in data:
            _byoipCidr_key = "ByoipCidr"
        if _byoipCidr_key:
            param_data = data[_byoipCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<byoipCidr>')
            xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</byoipCidr>')
        xml_parts.append(f'</DeprovisionByoipCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_byoip_cidrs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeByoipCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoipCidrSet
        _byoipCidrSet_key = None
        if "byoipCidrSet" in data:
            _byoipCidrSet_key = "byoipCidrSet"
        elif "ByoipCidrSet" in data:
            _byoipCidrSet_key = "ByoipCidrSet"
        elif "ByoipCidrs" in data:
            _byoipCidrSet_key = "ByoipCidrs"
        if _byoipCidrSet_key:
            param_data = data[_byoipCidrSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<byoipCidrSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</byoipCidrSet>')
            else:
                xml_parts.append(f'{indent_str}<byoipCidrSet/>')
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
        xml_parts.append(f'</DescribeByoipCidrsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_ipv6_pools_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeIpv6PoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipv6PoolSet
        _ipv6PoolSet_key = None
        if "ipv6PoolSet" in data:
            _ipv6PoolSet_key = "ipv6PoolSet"
        elif "Ipv6PoolSet" in data:
            _ipv6PoolSet_key = "Ipv6PoolSet"
        elif "Ipv6Pools" in data:
            _ipv6PoolSet_key = "Ipv6Pools"
        if _ipv6PoolSet_key:
            param_data = data[_ipv6PoolSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipv6PoolSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipv6PoolSet>')
            else:
                xml_parts.append(f'{indent_str}<ipv6PoolSet/>')
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
        xml_parts.append(f'</DescribeIpv6PoolsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_public_ipv4_pools_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribePublicIpv4PoolsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize publicIpv4PoolSet
        _publicIpv4PoolSet_key = None
        if "publicIpv4PoolSet" in data:
            _publicIpv4PoolSet_key = "publicIpv4PoolSet"
        elif "PublicIpv4PoolSet" in data:
            _publicIpv4PoolSet_key = "PublicIpv4PoolSet"
        elif "PublicIpv4Pools" in data:
            _publicIpv4PoolSet_key = "PublicIpv4Pools"
        if _publicIpv4PoolSet_key:
            param_data = data[_publicIpv4PoolSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<publicIpv4PoolSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</publicIpv4PoolSet>')
            else:
                xml_parts.append(f'{indent_str}<publicIpv4PoolSet/>')
        xml_parts.append(f'</DescribePublicIpv4PoolsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_associated_ipv6_pool_cidrs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetAssociatedIpv6PoolCidrsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize ipv6CidrAssociationSet
        _ipv6CidrAssociationSet_key = None
        if "ipv6CidrAssociationSet" in data:
            _ipv6CidrAssociationSet_key = "ipv6CidrAssociationSet"
        elif "Ipv6CidrAssociationSet" in data:
            _ipv6CidrAssociationSet_key = "Ipv6CidrAssociationSet"
        elif "Ipv6CidrAssociations" in data:
            _ipv6CidrAssociationSet_key = "Ipv6CidrAssociations"
        if _ipv6CidrAssociationSet_key:
            param_data = data[_ipv6CidrAssociationSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<ipv6CidrAssociationSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</ipv6CidrAssociationSet>')
            else:
                xml_parts.append(f'{indent_str}<ipv6CidrAssociationSet/>')
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
        xml_parts.append(f'</GetAssociatedIpv6PoolCidrsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_provision_byoip_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ProvisionByoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoipCidr
        _byoipCidr_key = None
        if "byoipCidr" in data:
            _byoipCidr_key = "byoipCidr"
        elif "ByoipCidr" in data:
            _byoipCidr_key = "ByoipCidr"
        if _byoipCidr_key:
            param_data = data[_byoipCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<byoipCidr>')
            xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</byoipCidr>')
        xml_parts.append(f'</ProvisionByoipCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_withdraw_byoip_cidr_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<WithdrawByoipCidrResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize byoipCidr
        _byoipCidr_key = None
        if "byoipCidr" in data:
            _byoipCidr_key = "byoipCidr"
        elif "ByoipCidr" in data:
            _byoipCidr_key = "ByoipCidr"
        if _byoipCidr_key:
            param_data = data[_byoipCidr_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<byoipCidr>')
            xml_parts.extend(byoip_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</byoipCidr>')
        xml_parts.append(f'</WithdrawByoipCidrResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "AdvertiseByoipCidr": byoip_ResponseSerializer.serialize_advertise_byoip_cidr_response,
            "DeprovisionByoipCidr": byoip_ResponseSerializer.serialize_deprovision_byoip_cidr_response,
            "DescribeByoipCidrs": byoip_ResponseSerializer.serialize_describe_byoip_cidrs_response,
            "DescribeIpv6Pools": byoip_ResponseSerializer.serialize_describe_ipv6_pools_response,
            "DescribePublicIpv4Pools": byoip_ResponseSerializer.serialize_describe_public_ipv4_pools_response,
            "GetAssociatedIpv6PoolCidrs": byoip_ResponseSerializer.serialize_get_associated_ipv6_pool_cidrs_response,
            "ProvisionByoipCidr": byoip_ResponseSerializer.serialize_provision_byoip_cidr_response,
            "WithdrawByoipCidr": byoip_ResponseSerializer.serialize_withdraw_byoip_cidr_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

