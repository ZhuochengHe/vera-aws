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
class VerifiedAccessEndpoint:
    application_domain: str = ""
    attachment_type: str = ""
    cidr_options: Dict[str, Any] = field(default_factory=dict)
    creation_time: str = ""
    deletion_time: str = ""
    description: str = ""
    device_validation_domain: str = ""
    domain_certificate_arn: str = ""
    endpoint_domain: str = ""
    endpoint_type: str = ""
    last_updated_time: str = ""
    load_balancer_options: Dict[str, Any] = field(default_factory=dict)
    network_interface_options: Dict[str, Any] = field(default_factory=dict)
    rds_options: Dict[str, Any] = field(default_factory=dict)
    security_group_id_set: List[Any] = field(default_factory=list)
    sse_specification: Dict[str, Any] = field(default_factory=dict)
    status: Dict[str, Any] = field(default_factory=dict)
    tag_set: List[Any] = field(default_factory=list)
    verified_access_endpoint_id: str = ""
    verified_access_group_id: str = ""
    verified_access_instance_id: str = ""

    policy_document: str = ""
    policy_enabled: Optional[bool] = None
    endpoint_target_set: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applicationDomain": self.application_domain,
            "attachmentType": self.attachment_type,
            "cidrOptions": self.cidr_options,
            "creationTime": self.creation_time,
            "deletionTime": self.deletion_time,
            "description": self.description,
            "deviceValidationDomain": self.device_validation_domain,
            "domainCertificateArn": self.domain_certificate_arn,
            "endpointDomain": self.endpoint_domain,
            "endpointType": self.endpoint_type,
            "lastUpdatedTime": self.last_updated_time,
            "loadBalancerOptions": self.load_balancer_options,
            "networkInterfaceOptions": self.network_interface_options,
            "rdsOptions": self.rds_options,
            "securityGroupIdSet": self.security_group_id_set,
            "sseSpecification": self.sse_specification,
            "status": self.status,
            "tagSet": self.tag_set,
            "verifiedAccessEndpointId": self.verified_access_endpoint_id,
            "verifiedAccessGroupId": self.verified_access_group_id,
            "verifiedAccessInstanceId": self.verified_access_instance_id,
            "policyDocument": self.policy_document,
            "policyEnabled": self.policy_enabled,
            "endpointTargetSet": self.endpoint_target_set,
        }

class VerifiedAccessEndpoint_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.verified_access_endpoints  # alias to shared store

    # Cross-resource parent registration (do this in Create/Delete methods):
    #   Create: self.state.verified_access_groups.get(params['verified_access_group_id']).verified_access_endpoint_ids.append(new_id)
    #   Delete: self.state.verified_access_groups.get(resource.verified_access_group_id).verified_access_endpoint_ids.remove(resource_id)
    #   Create: self.state.verified_access_logs.get(params['verified_access_instance_id']).verified_access_endpoint_ids.append(new_id)
    #   Delete: self.state.verified_access_logs.get(resource.verified_access_instance_id).verified_access_endpoint_ids.remove(resource_id)

    def _get_endpoint_or_error(self, endpoint_id: str):
        resource = self.resources.get(endpoint_id)
        if not resource:
            return create_error_response(
                "InvalidVerifiedAccessEndpointId.NotFound",
                f"The ID '{endpoint_id}' does not exist",
            )
        return resource

    def _register_with_parents(self, endpoint_id: str, group_id: Optional[str], instance_id: Optional[str]) -> None:
        parent = self.state.verified_access_groups.get(group_id)
        if parent and hasattr(parent, "verified_access_endpoint_ids"):
            if endpoint_id not in parent.verified_access_endpoint_ids:
                parent.verified_access_endpoint_ids.append(endpoint_id)
        parent = self.state.verified_access_logs.get(instance_id)
        if parent and hasattr(parent, "verified_access_endpoint_ids"):
            if endpoint_id not in parent.verified_access_endpoint_ids:
                parent.verified_access_endpoint_ids.append(endpoint_id)

    def _deregister_from_parents(self, resource: VerifiedAccessEndpoint) -> None:
        parent = self.state.verified_access_groups.get(resource.verified_access_group_id)
        if parent and hasattr(parent, "verified_access_endpoint_ids"):
            if resource.verified_access_endpoint_id in parent.verified_access_endpoint_ids:
                parent.verified_access_endpoint_ids.remove(resource.verified_access_endpoint_id)
        parent = self.state.verified_access_logs.get(resource.verified_access_instance_id)
        if parent and hasattr(parent, "verified_access_endpoint_ids"):
            if resource.verified_access_endpoint_id in parent.verified_access_endpoint_ids:
                parent.verified_access_endpoint_ids.remove(resource.verified_access_endpoint_id)

    def CreateVerifiedAccessEndpoint(self, params: Dict[str, Any]):
        """An AWS Verified Access endpoint is where you define your application along with an optional endpoint-level access policy."""

        for name in ["AttachmentType", "EndpointType", "VerifiedAccessGroupId"]:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")

        group_id = params.get("VerifiedAccessGroupId")
        group = self.state.verified_access_groups.get(group_id)
        if not group:
            return create_error_response(
                "InvalidVerifiedAccessGroupId.NotFound",
                f"The ID '{group_id}' does not exist",
            )

        instance_id = group.verified_access_instance_id
        if instance_id and not self.state.verified_access_instances.get(instance_id):
            return create_error_response(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The ID '{instance_id}' does not exist",
            )

        security_group_ids = params.get("SecurityGroupId.N", []) or []
        for security_group_id in security_group_ids:
            if not self.state.security_groups.get(security_group_id):
                return create_error_response(
                    "InvalidGroup.NotFound",
                    f"Security group '{security_group_id}' does not exist.",
                )

        tag_set: List[Dict[str, Any]] = []
        for spec in params.get("TagSpecification.N", []) or []:
            tag_set.extend(spec.get("Tags", []) or [])

        endpoint_id = self._generate_id("vae")
        timestamp = datetime.now(timezone.utc).isoformat()
        policy_document = params.get("PolicyDocument") or ""
        status = {"code": "active", "message": "Active"}

        resource = VerifiedAccessEndpoint(
            application_domain=params.get("ApplicationDomain") or "",
            attachment_type=params.get("AttachmentType") or "",
            cidr_options=params.get("CidrOptions") or {},
            creation_time=timestamp,
            deletion_time="",
            description=params.get("Description") or "",
            device_validation_domain="",
            domain_certificate_arn=params.get("DomainCertificateArn") or "",
            endpoint_domain=params.get("EndpointDomainPrefix") or "",
            endpoint_type=params.get("EndpointType") or "",
            last_updated_time=timestamp,
            load_balancer_options=params.get("LoadBalancerOptions") or {},
            network_interface_options=params.get("NetworkInterfaceOptions") or {},
            rds_options=params.get("RdsOptions") or {},
            security_group_id_set=security_group_ids,
            sse_specification=params.get("SseSpecification") or {},
            status=status,
            tag_set=tag_set,
            verified_access_endpoint_id=endpoint_id,
            verified_access_group_id=group_id,
            verified_access_instance_id=instance_id or "",
            policy_document=policy_document,
            policy_enabled=bool(policy_document),
        )

        self.resources[endpoint_id] = resource
        self._register_with_parents(endpoint_id, group_id, instance_id)

        return {
            'verifiedAccessEndpoint': resource.to_dict(),
            }

    def DeleteVerifiedAccessEndpoint(self, params: Dict[str, Any]):
        """Delete an AWS Verified Access endpoint."""

        if not params.get("VerifiedAccessEndpointId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessEndpointId",
            )

        endpoint_id = params.get("VerifiedAccessEndpointId")
        resource = self._get_endpoint_or_error(endpoint_id)
        if is_error_response(resource):
            return resource

        self._deregister_from_parents(resource)
        resource.deletion_time = datetime.now(timezone.utc).isoformat()
        resource.status = {"code": "deleted", "message": "Deleted"}
        del self.resources[endpoint_id]

        return {
            'verifiedAccessEndpoint': resource.to_dict(),
            }

    def DescribeVerifiedAccessEndpoints(self, params: Dict[str, Any]):
        """Describes the specified AWS Verified Access endpoints."""

        endpoint_ids = params.get("VerifiedAccessEndpointId.N", []) or []
        max_results = int(params.get("MaxResults") or 100)
        group_id = params.get("VerifiedAccessGroupId")
        instance_id = params.get("VerifiedAccessInstanceId")

        if group_id and not self.state.verified_access_groups.get(group_id):
            return create_error_response(
                "InvalidVerifiedAccessGroupId.NotFound",
                f"The ID '{group_id}' does not exist",
            )

        if instance_id and not self.state.verified_access_instances.get(instance_id):
            return create_error_response(
                "InvalidVerifiedAccessInstanceId.NotFound",
                f"The ID '{instance_id}' does not exist",
            )

        if endpoint_ids:
            resources: List[VerifiedAccessEndpoint] = []
            for endpoint_id in endpoint_ids:
                resource = self._get_endpoint_or_error(endpoint_id)
                if is_error_response(resource):
                    return resource
                resources.append(resource)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))
        if group_id:
            resources = [res for res in resources if res.verified_access_group_id == group_id]
        if instance_id:
            resources = [res for res in resources if res.verified_access_instance_id == instance_id]

        endpoint_set = [resource.to_dict() for resource in resources[:max_results]]

        return {
            'nextToken': None,
            'verifiedAccessEndpointSet': endpoint_set,
            }

    def GetVerifiedAccessEndpointPolicy(self, params: Dict[str, Any]):
        """Get the Verified Access policy associated with the endpoint."""

        if not params.get("VerifiedAccessEndpointId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessEndpointId",
            )

        endpoint_id = params.get("VerifiedAccessEndpointId")
        resource = self._get_endpoint_or_error(endpoint_id)
        if is_error_response(resource):
            return resource

        policy_enabled = resource.policy_enabled
        if policy_enabled is None:
            policy_enabled = False

        return {
            'policyDocument': resource.policy_document,
            'policyEnabled': policy_enabled,
            }

    def GetVerifiedAccessEndpointTargets(self, params: Dict[str, Any]):
        """Gets the targets for the specified network CIDR endpoint for Verified Access."""

        if not params.get("VerifiedAccessEndpointId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessEndpointId",
            )

        endpoint_id = params.get("VerifiedAccessEndpointId")
        resource = self._get_endpoint_or_error(endpoint_id)
        if is_error_response(resource):
            return resource

        max_results = int(params.get("MaxResults") or 100)
        target_set = resource.endpoint_target_set or []

        return {
            'nextToken': None,
            'verifiedAccessEndpointTargetSet': target_set[:max_results],
            }

    def ModifyVerifiedAccessEndpoint(self, params: Dict[str, Any]):
        """Modifies the configuration of the specified AWS Verified Access endpoint."""

        if not params.get("VerifiedAccessEndpointId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessEndpointId",
            )

        endpoint_id = params.get("VerifiedAccessEndpointId")
        resource = self._get_endpoint_or_error(endpoint_id)
        if is_error_response(resource):
            return resource

        new_group_id = params.get("VerifiedAccessGroupId")
        if new_group_id:
            new_group = self.state.verified_access_groups.get(new_group_id)
            if not new_group:
                return create_error_response(
                    "InvalidVerifiedAccessGroupId.NotFound",
                    f"The ID '{new_group_id}' does not exist",
                )
            new_instance_id = new_group.verified_access_instance_id
            if new_instance_id and not self.state.verified_access_instances.get(new_instance_id):
                return create_error_response(
                    "InvalidVerifiedAccessInstanceId.NotFound",
                    f"The ID '{new_instance_id}' does not exist",
                )
            if new_group_id != resource.verified_access_group_id:
                self._deregister_from_parents(resource)
                resource.verified_access_group_id = new_group_id
                resource.verified_access_instance_id = new_instance_id or ""
                self._register_with_parents(endpoint_id, new_group_id, new_instance_id)

        if params.get("CidrOptions") is not None:
            resource.cidr_options = params.get("CidrOptions") or {}
        if params.get("Description") is not None:
            resource.description = params.get("Description") or ""
        if params.get("LoadBalancerOptions") is not None:
            resource.load_balancer_options = params.get("LoadBalancerOptions") or {}
        if params.get("NetworkInterfaceOptions") is not None:
            resource.network_interface_options = params.get("NetworkInterfaceOptions") or {}
        if params.get("RdsOptions") is not None:
            resource.rds_options = params.get("RdsOptions") or {}

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()

        return {
            'verifiedAccessEndpoint': resource.to_dict(),
            }

    def ModifyVerifiedAccessEndpointPolicy(self, params: Dict[str, Any]):
        """Modifies the specified AWS Verified Access endpoint policy."""

        if not params.get("VerifiedAccessEndpointId"):
            return create_error_response(
                "MissingParameter",
                "Missing required parameter: VerifiedAccessEndpointId",
            )

        endpoint_id = params.get("VerifiedAccessEndpointId")
        resource = self._get_endpoint_or_error(endpoint_id)
        if is_error_response(resource):
            return resource

        if params.get("PolicyDocument") is not None:
            resource.policy_document = params.get("PolicyDocument") or ""
        if params.get("PolicyEnabled") is not None:
            resource.policy_enabled = str2bool(params.get("PolicyEnabled"))
        if params.get("SseSpecification") is not None:
            resource.sse_specification = params.get("SseSpecification") or {}

        resource.last_updated_time = datetime.now(timezone.utc).isoformat()

        policy_enabled = resource.policy_enabled
        if policy_enabled is None:
            policy_enabled = False

        return {
            'policyDocument': resource.policy_document,
            'policyEnabled': policy_enabled,
            'sseSpecification': resource.sse_specification,
            }

    def _generate_id(self, prefix: str = 'verified') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class verifiedaccessendpoint_RequestParser:
    @staticmethod
    def parse_create_verified_access_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ApplicationDomain": get_scalar(md, "ApplicationDomain"),
            "AttachmentType": get_scalar(md, "AttachmentType"),
            "CidrOptions": get_int(md, "CidrOptions"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DomainCertificateArn": get_scalar(md, "DomainCertificateArn"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "EndpointDomainPrefix": get_scalar(md, "EndpointDomainPrefix"),
            "EndpointType": get_scalar(md, "EndpointType"),
            "LoadBalancerOptions": get_int(md, "LoadBalancerOptions"),
            "NetworkInterfaceOptions": get_int(md, "NetworkInterfaceOptions"),
            "PolicyDocument": get_scalar(md, "PolicyDocument"),
            "RdsOptions": get_int(md, "RdsOptions"),
            "SecurityGroupId.N": get_indexed_list(md, "SecurityGroupId"),
            "SseSpecification": get_scalar(md, "SseSpecification"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
            "VerifiedAccessGroupId": get_scalar(md, "VerifiedAccessGroupId"),
        }

    @staticmethod
    def parse_delete_verified_access_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessEndpointId": get_scalar(md, "VerifiedAccessEndpointId"),
        }

    @staticmethod
    def parse_describe_verified_access_endpoints_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VerifiedAccessEndpointId.N": get_indexed_list(md, "VerifiedAccessEndpointId"),
            "VerifiedAccessGroupId": get_scalar(md, "VerifiedAccessGroupId"),
            "VerifiedAccessInstanceId": get_scalar(md, "VerifiedAccessInstanceId"),
        }

    @staticmethod
    def parse_get_verified_access_endpoint_policy_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "VerifiedAccessEndpointId": get_scalar(md, "VerifiedAccessEndpointId"),
        }

    @staticmethod
    def parse_get_verified_access_endpoint_targets_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "MaxResults": get_int(md, "MaxResults"),
            "NextToken": get_scalar(md, "NextToken"),
            "VerifiedAccessEndpointId": get_scalar(md, "VerifiedAccessEndpointId"),
        }

    @staticmethod
    def parse_modify_verified_access_endpoint_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "CidrOptions": get_int(md, "CidrOptions"),
            "ClientToken": get_scalar(md, "ClientToken"),
            "Description": get_scalar(md, "Description"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "LoadBalancerOptions": get_int(md, "LoadBalancerOptions"),
            "NetworkInterfaceOptions": get_int(md, "NetworkInterfaceOptions"),
            "RdsOptions": get_int(md, "RdsOptions"),
            "VerifiedAccessEndpointId": get_scalar(md, "VerifiedAccessEndpointId"),
            "VerifiedAccessGroupId": get_scalar(md, "VerifiedAccessGroupId"),
        }

    @staticmethod
    def parse_modify_verified_access_endpoint_policy_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ClientToken": get_scalar(md, "ClientToken"),
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "PolicyDocument": get_scalar(md, "PolicyDocument"),
            "PolicyEnabled": get_scalar(md, "PolicyEnabled"),
            "SseSpecification": get_scalar(md, "SseSpecification"),
            "VerifiedAccessEndpointId": get_scalar(md, "VerifiedAccessEndpointId"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateVerifiedAccessEndpoint": verifiedaccessendpoint_RequestParser.parse_create_verified_access_endpoint_request,
            "DeleteVerifiedAccessEndpoint": verifiedaccessendpoint_RequestParser.parse_delete_verified_access_endpoint_request,
            "DescribeVerifiedAccessEndpoints": verifiedaccessendpoint_RequestParser.parse_describe_verified_access_endpoints_request,
            "GetVerifiedAccessEndpointPolicy": verifiedaccessendpoint_RequestParser.parse_get_verified_access_endpoint_policy_request,
            "GetVerifiedAccessEndpointTargets": verifiedaccessendpoint_RequestParser.parse_get_verified_access_endpoint_targets_request,
            "ModifyVerifiedAccessEndpoint": verifiedaccessendpoint_RequestParser.parse_modify_verified_access_endpoint_request,
            "ModifyVerifiedAccessEndpointPolicy": verifiedaccessendpoint_RequestParser.parse_modify_verified_access_endpoint_policy_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class verifiedaccessendpoint_ResponseSerializer:
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
                xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_verified_access_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateVerifiedAccessEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessEndpoint
        _verifiedAccessEndpoint_key = None
        if "verifiedAccessEndpoint" in data:
            _verifiedAccessEndpoint_key = "verifiedAccessEndpoint"
        elif "VerifiedAccessEndpoint" in data:
            _verifiedAccessEndpoint_key = "VerifiedAccessEndpoint"
        if _verifiedAccessEndpoint_key:
            param_data = data[_verifiedAccessEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessEndpoint>')
            xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessEndpoint>')
        xml_parts.append(f'</CreateVerifiedAccessEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_verified_access_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteVerifiedAccessEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessEndpoint
        _verifiedAccessEndpoint_key = None
        if "verifiedAccessEndpoint" in data:
            _verifiedAccessEndpoint_key = "verifiedAccessEndpoint"
        elif "VerifiedAccessEndpoint" in data:
            _verifiedAccessEndpoint_key = "VerifiedAccessEndpoint"
        if _verifiedAccessEndpoint_key:
            param_data = data[_verifiedAccessEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessEndpoint>')
            xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessEndpoint>')
        xml_parts.append(f'</DeleteVerifiedAccessEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_verified_access_endpoints_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeVerifiedAccessEndpointsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize verifiedAccessEndpointSet
        _verifiedAccessEndpointSet_key = None
        if "verifiedAccessEndpointSet" in data:
            _verifiedAccessEndpointSet_key = "verifiedAccessEndpointSet"
        elif "VerifiedAccessEndpointSet" in data:
            _verifiedAccessEndpointSet_key = "VerifiedAccessEndpointSet"
        elif "VerifiedAccessEndpoints" in data:
            _verifiedAccessEndpointSet_key = "VerifiedAccessEndpoints"
        if _verifiedAccessEndpointSet_key:
            param_data = data[_verifiedAccessEndpointSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<verifiedAccessEndpointSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</verifiedAccessEndpointSet>')
            else:
                xml_parts.append(f'{indent_str}<verifiedAccessEndpointSet/>')
        xml_parts.append(f'</DescribeVerifiedAccessEndpointsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_verified_access_endpoint_policy_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetVerifiedAccessEndpointPolicyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize policyDocument
        _policyDocument_key = None
        if "policyDocument" in data:
            _policyDocument_key = "policyDocument"
        elif "PolicyDocument" in data:
            _policyDocument_key = "PolicyDocument"
        if _policyDocument_key:
            param_data = data[_policyDocument_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyDocument>{esc(str(param_data))}</policyDocument>')
        # Serialize policyEnabled
        _policyEnabled_key = None
        if "policyEnabled" in data:
            _policyEnabled_key = "policyEnabled"
        elif "PolicyEnabled" in data:
            _policyEnabled_key = "PolicyEnabled"
        if _policyEnabled_key:
            param_data = data[_policyEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyEnabled>{esc(str(param_data))}</policyEnabled>')
        xml_parts.append(f'</GetVerifiedAccessEndpointPolicyResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_get_verified_access_endpoint_targets_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<GetVerifiedAccessEndpointTargetsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
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
        # Serialize verifiedAccessEndpointTargetSet
        _verifiedAccessEndpointTargetSet_key = None
        if "verifiedAccessEndpointTargetSet" in data:
            _verifiedAccessEndpointTargetSet_key = "verifiedAccessEndpointTargetSet"
        elif "VerifiedAccessEndpointTargetSet" in data:
            _verifiedAccessEndpointTargetSet_key = "VerifiedAccessEndpointTargetSet"
        elif "VerifiedAccessEndpointTargets" in data:
            _verifiedAccessEndpointTargetSet_key = "VerifiedAccessEndpointTargets"
        if _verifiedAccessEndpointTargetSet_key:
            param_data = data[_verifiedAccessEndpointTargetSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<verifiedAccessEndpointTargetSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</verifiedAccessEndpointTargetSet>')
            else:
                xml_parts.append(f'{indent_str}<verifiedAccessEndpointTargetSet/>')
        xml_parts.append(f'</GetVerifiedAccessEndpointTargetsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_verified_access_endpoint_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVerifiedAccessEndpointResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize verifiedAccessEndpoint
        _verifiedAccessEndpoint_key = None
        if "verifiedAccessEndpoint" in data:
            _verifiedAccessEndpoint_key = "verifiedAccessEndpoint"
        elif "VerifiedAccessEndpoint" in data:
            _verifiedAccessEndpoint_key = "VerifiedAccessEndpoint"
        if _verifiedAccessEndpoint_key:
            param_data = data[_verifiedAccessEndpoint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<verifiedAccessEndpoint>')
            xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</verifiedAccessEndpoint>')
        xml_parts.append(f'</ModifyVerifiedAccessEndpointResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_modify_verified_access_endpoint_policy_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ModifyVerifiedAccessEndpointPolicyResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize policyDocument
        _policyDocument_key = None
        if "policyDocument" in data:
            _policyDocument_key = "policyDocument"
        elif "PolicyDocument" in data:
            _policyDocument_key = "PolicyDocument"
        if _policyDocument_key:
            param_data = data[_policyDocument_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyDocument>{esc(str(param_data))}</policyDocument>')
        # Serialize policyEnabled
        _policyEnabled_key = None
        if "policyEnabled" in data:
            _policyEnabled_key = "policyEnabled"
        elif "PolicyEnabled" in data:
            _policyEnabled_key = "PolicyEnabled"
        if _policyEnabled_key:
            param_data = data[_policyEnabled_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<policyEnabled>{esc(str(param_data))}</policyEnabled>')
        # Serialize sseSpecification
        _sseSpecification_key = None
        if "sseSpecification" in data:
            _sseSpecification_key = "sseSpecification"
        elif "SseSpecification" in data:
            _sseSpecification_key = "SseSpecification"
        if _sseSpecification_key:
            param_data = data[_sseSpecification_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<sseSpecification>')
            xml_parts.extend(verifiedaccessendpoint_ResponseSerializer._serialize_nested_fields(param_data, 2))
            xml_parts.append(f'{indent_str}</sseSpecification>')
        xml_parts.append(f'</ModifyVerifiedAccessEndpointPolicyResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateVerifiedAccessEndpoint": verifiedaccessendpoint_ResponseSerializer.serialize_create_verified_access_endpoint_response,
            "DeleteVerifiedAccessEndpoint": verifiedaccessendpoint_ResponseSerializer.serialize_delete_verified_access_endpoint_response,
            "DescribeVerifiedAccessEndpoints": verifiedaccessendpoint_ResponseSerializer.serialize_describe_verified_access_endpoints_response,
            "GetVerifiedAccessEndpointPolicy": verifiedaccessendpoint_ResponseSerializer.serialize_get_verified_access_endpoint_policy_response,
            "GetVerifiedAccessEndpointTargets": verifiedaccessendpoint_ResponseSerializer.serialize_get_verified_access_endpoint_targets_response,
            "ModifyVerifiedAccessEndpoint": verifiedaccessendpoint_ResponseSerializer.serialize_modify_verified_access_endpoint_response,
            "ModifyVerifiedAccessEndpointPolicy": verifiedaccessendpoint_ResponseSerializer.serialize_modify_verified_access_endpoint_policy_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

