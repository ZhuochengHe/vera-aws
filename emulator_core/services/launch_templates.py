from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from emulator_core.backend import BaseBackend


@dataclass
class LaunchTemplateEbsBlockDeviceRequest:
    delete_on_termination: Optional[bool] = None
    encrypted: Optional[bool] = None
    iops: Optional[int] = None
    kms_key_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    throughput: Optional[int] = None
    volume_initialization_rate: Optional[int] = None
    volume_size: Optional[int] = None
    volume_type: Optional[str] = None


@dataclass
class LaunchTemplateBlockDeviceMappingRequest:
    device_name: Optional[str] = None
    ebs: Optional[LaunchTemplateEbsBlockDeviceRequest] = None
    no_device: Optional[str] = None
    virtual_name: Optional[str] = None


@dataclass
class CapacityReservationTarget:
    capacity_reservation_id: Optional[str] = None
    capacity_reservation_resource_group_arn: Optional[str] = None


@dataclass
class LaunchTemplateCapacityReservationSpecificationRequest:
    capacity_reservation_preference: Optional[str] = None
    capacity_reservation_target: Optional[CapacityReservationTarget] = None


@dataclass
class LaunchTemplateCpuOptionsRequest:
    amd_sev_snp: Optional[str] = None
    core_count: Optional[int] = None
    threads_per_core: Optional[int] = None


@dataclass
class CreditSpecificationRequest:
    cpu_credits: str  # Required


@dataclass
class ElasticGpuSpecification:
    type: str  # Required


@dataclass
class LaunchTemplateElasticInferenceAccelerator:
    type: str  # Required
    count: Optional[int] = None


@dataclass
class LaunchTemplateEnclaveOptionsRequest:
    enabled: Optional[bool] = None


@dataclass
class LaunchTemplateHibernationOptionsRequest:
    configured: Optional[bool] = None


@dataclass
class LaunchTemplateIamInstanceProfileSpecificationRequest:
    arn: Optional[str] = None
    name: Optional[str] = None


@dataclass
class LaunchTemplateLicenseConfigurationRequest:
    license_configuration_arn: Optional[str] = None


@dataclass
class LaunchTemplateInstanceMaintenanceOptionsRequest:
    auto_recovery: Optional[str] = None


@dataclass
class LaunchTemplateInstanceMetadataOptionsRequest:
    http_endpoint: Optional[str] = None
    http_protocol_ipv6: Optional[str] = None
    http_put_response_hop_limit: Optional[int] = None
    http_tokens: Optional[str] = None
    instance_metadata_tags: Optional[str] = None


@dataclass
class LaunchTemplatesMonitoringRequest:
    enabled: Optional[bool] = None


@dataclass
class ConnectionTrackingSpecificationRequest:
    tcp_established_timeout: Optional[int] = None
    udp_stream_timeout: Optional[int] = None
    udp_timeout: Optional[int] = None


@dataclass
class EnaSrdUdpSpecificationRequest:
    ena_srd_udp_enabled: Optional[bool] = None


@dataclass
class EnaSrdSpecificationRequest:
    ena_srd_enabled: Optional[bool] = None
    ena_srd_udp_specification: Optional[EnaSrdUdpSpecificationRequest] = None


@dataclass
class Ipv4PrefixSpecificationRequest:
    ipv4_prefix: Optional[str] = None


@dataclass
class InstanceIpv6AddressRequest:
    ipv6_address: Optional[str] = None


@dataclass
class PrivateIpAddressSpecification:
    primary: Optional[bool] = None
    private_ip_address: Optional[str] = None


@dataclass
class LaunchTemplateInstanceNetworkInterfaceSpecificationRequest:
    associate_carrier_ip_address: Optional[bool] = None
    associate_public_ip_address: Optional[bool] = None
    connection_tracking_specification: Optional[ConnectionTrackingSpecificationRequest] = None
    delete_on_termination: Optional[bool] = None
    description: Optional[str] = None
    device_index: Optional[int] = None
    ena_queue_count: Optional[int] = None
    ena_srd_specification: Optional[EnaSrdSpecificationRequest] = None
    interface_type: Optional[str] = None
    ipv4_prefixes: Optional[List[Ipv4PrefixSpecificationRequest]] = None
    ipv4_prefix_count: Optional[int] = None
    ipv6_address_count: Optional[int] = None
    ipv6_addresses: Optional[List[InstanceIpv6AddressRequest]] = None
    ipv6_prefixes: Optional[List[Ipv4PrefixSpecificationRequest]] = None
    ipv6_prefix_count: Optional[int] = None
    network_card_index: Optional[int] = None
    network_interface_id: Optional[str] = None
    primary_ipv6: Optional[bool] = None
    private_ip_address: Optional[str] = None
    private_ip_addresses: Optional[List[PrivateIpAddressSpecification]] = None
    secondary_private_ip_address_count: Optional[int] = None
    groups: Optional[List[str]] = None
    subnet_id: Optional[str] = None


@dataclass
class LaunchTemplateNetworkPerformanceOptionsRequest:
    bandwidth_weighting: Optional[str] = None


@dataclass
class OperatorRequest:
    principal: Optional[str] = None


@dataclass
class LaunchTemplatePlacementRequest:
    affinity: Optional[str] = None
    availability_zone: Optional[str] = None
    availability_zone_id: Optional[str] = None
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    host_id: Optional[str] = None
    host_resource_group_arn: Optional[str] = None
    partition_number: Optional[int] = None
    spread_domain: Optional[str] = None
    tenancy: Optional[str] = None


@dataclass
class Tag:
    Key: Optional[str] = None
    Value: Optional[str] = None


@dataclass
class LaunchTemplateTagSpecificationRequest:
    resource_type: Optional[str] = None
    tags: Optional[List[Tag]] = None


@dataclass
class RequestLaunchTemplateData:
    block_device_mappings: Optional[List[LaunchTemplateBlockDeviceMappingRequest]] = None
    capacity_reservation_specification: Optional[LaunchTemplateCapacityReservationSpecificationRequest] = None
    cpu_options: Optional[LaunchTemplateCpuOptionsRequest] = None
    credit_specification: Optional[CreditSpecificationRequest] = None
    disable_api_stop: Optional[bool] = None
    disable_api_termination: Optional[bool] = None
    ebs_optimized: Optional[bool] = None
    elastic_gpu_specifications: Optional[List[ElasticGpuSpecification]] = None
    elastic_inference_accelerators: Optional[List[LaunchTemplateElasticInferenceAccelerator]] = None
    enclave_options: Optional[LaunchTemplateEnclaveOptionsRequest] = None
    hibernation_options: Optional[LaunchTemplateHibernationOptionsRequest] = None
    iam_instance_profile: Optional[LaunchTemplateIamInstanceProfileSpecificationRequest] = None
    image_id: Optional[str] = None
    instance_initiated_shutdown_behavior: Optional[str] = None
    instance_market_options: Optional[Any] = None  # Complex nested, omitted for brevity
    instance_requirements: Optional[Any] = None  # Complex nested, omitted for brevity
    instance_type: Optional[str] = None
    kernel_id: Optional[str] = None
    key_name: Optional[str] = None
    license_specifications: Optional[List[LaunchTemplateLicenseConfigurationRequest]] = None
    maintenance_options: Optional[LaunchTemplateInstanceMaintenanceOptionsRequest] = None
    metadata_options: Optional[LaunchTemplateInstanceMetadataOptionsRequest] = None
    monitoring: Optional[LaunchTemplatesMonitoringRequest] = None
    network_interfaces: Optional[List[LaunchTemplateInstanceNetworkInterfaceSpecificationRequest]] = None
    network_performance_options: Optional[LaunchTemplateNetworkPerformanceOptionsRequest] = None
    operator: Optional[OperatorRequest] = None
    placement: Optional[LaunchTemplatePlacementRequest] = None
    private_dns_name_options: Optional[Any] = None  # Complex nested, omitted for brevity
    ram_disk_id: Optional[str] = None
    security_groups: Optional[List[str]] = None
    security_group_ids: Optional[List[str]] = None
    tag_specifications: Optional[List[LaunchTemplateTagSpecificationRequest]] = None
    user_data: Optional[str] = None


@dataclass
class OperatorResponse:
    managed: Optional[bool] = None
    principal: Optional[str] = None


@dataclass
class TagResponse:
    Key: Optional[str] = None
    Value: Optional[str] = None


@dataclass
class LaunchTemplate:
    created_by: Optional[str] = None
    create_time: Optional[datetime] = None
    default_version_number: Optional[int] = None
    latest_version_number: Optional[int] = None
    launch_template_id: Optional[str] = None
    launch_template_name: Optional[str] = None
    operator: Optional[OperatorResponse] = None
    tag_set: Optional[List[TagResponse]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "createdBy": self.created_by,
            "createTime": self.create_time.isoformat() if self.create_time else None,
            "defaultVersionNumber": self.default_version_number,
            "latestVersionNumber": self.latest_version_number,
            "launchTemplateId": self.launch_template_id,
            "launchTemplateName": self.launch_template_name,
            "operator": self.operator.to_dict() if self.operator and hasattr(self.operator, 'to_dict') else None,
            "tagSet": [t.to_dict() if hasattr(t, 'to_dict') else {"Key": t.Key, "Value": t.Value} for t in (self.tag_set or [])],
        }


@dataclass
class LaunchTemplateVersion:
    created_by: Optional[str] = None
    create_time: Optional[datetime] = None
    default_version: Optional[bool] = None
    launch_template_data: Optional[Any] = None  # Complex nested, omitted for brevity
    launch_template_id: Optional[str] = None
    launch_template_name: Optional[str] = None
    operator: Optional[OperatorResponse] = None
    version_description: Optional[str] = None
    version_number: Optional[int] = None


@dataclass
class DeleteLaunchTemplateVersionsResponseSuccessItem:
    launch_template_id: Optional[str] = None
    launch_template_name: Optional[str] = None
    version_number: Optional[int] = None


@dataclass
class ResponseError:
    code: Optional[str] = None
    message: Optional[str] = None


@dataclass
class DeleteLaunchTemplateVersionsResponseErrorItem:
    launch_template_id: Optional[str] = None
    launch_template_name: Optional[str] = None
    response_error: Optional[ResponseError] = None
    version_number: Optional[int] = None


@dataclass
class ValidationError:
    code: Optional[str] = None
    message: Optional[str] = None


@dataclass
class ValidationWarning:
    error_set: Optional[List[ValidationError]] = None


class LaunchtemplatesBackend(BaseBackend):
    def __init__(self, state):
        super().__init__(state)
        # No local storage; use self.state.launch_templates

    def create_launch_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime
        import json

        # Validate required parameters
        launch_template_name = params.get("LaunchTemplateName")
        launch_template_data = params.get("LaunchTemplateData")

        # If LaunchTemplateData is not directly provided, parse from nested params
        # AWS CLI sends nested params like LaunchTemplateData.ImageId, LaunchTemplateData.InstanceType
        if not launch_template_data:
            launch_template_data = {}
            prefix = "LaunchTemplateData."
            for key, value in params.items():
                if key.startswith(prefix):
                    # Extract the nested key path
                    nested_key = key[len(prefix):]
                    # Handle simple keys like ImageId, InstanceType
                    if "." not in nested_key:
                        launch_template_data[nested_key] = value
                    else:
                        # Handle nested structures like NetworkInterfaces.member.1.DeviceIndex
                        parts = nested_key.split(".")
                        current = launch_template_data
                        for i, part in enumerate(parts[:-1]):
                            if part == "member":
                                continue  # Skip 'member' keyword
                            # Check if next part is a number (array index)
                            next_part = parts[i + 1] if i + 1 < len(parts) else None
                            if next_part and (next_part.isdigit() or next_part == "member"):
                                if part not in current:
                                    current[part] = []
                                if next_part.isdigit():
                                    idx = int(next_part) - 1
                                    while len(current[part]) <= idx:
                                        current[part].append({})
                                    current = current[part][idx]
                            elif part.isdigit():
                                continue  # Already handled
                            else:
                                if part not in current:
                                    current[part] = {}
                                current = current[part]
                        # Set the final value
                        final_key = parts[-1]
                        if final_key not in ("member",) and not final_key.isdigit():
                            current[final_key] = value

        if not launch_template_name:
            raise ValueError("LaunchTemplateName is required")
        if not launch_template_data:
            raise ValueError("LaunchTemplateData is required")
        # Parse JSON string if needed
        if isinstance(launch_template_data, str):
            try:
                launch_template_data = json.loads(launch_template_data)
            except json.JSONDecodeError:
                raise ValueError("LaunchTemplateData must be valid JSON")

        # Validate launch template name constraints
        import re
        if not (3 <= len(launch_template_name) <= 128):
            raise ValueError("LaunchTemplateName length must be between 3 and 128")
        if not re.match(r"^[a-zA-Z0-9\(\)\.\-/_]+$", launch_template_name):
            raise ValueError("LaunchTemplateName contains invalid characters")

        # Check if launch template name already exists
        for lt in self.state.launch_templates.values():
            if lt.launch_template_name == launch_template_name:
                raise ValueError(f"LaunchTemplateName '{launch_template_name}' already exists")

        # Generate launch template ID
        launch_template_id = self.generate_unique_id(prefix="lt-")

        # Create initial version number
        default_version_number = 1
        latest_version_number = 1

        # Prepare tags from TagSpecification.N if present
        tag_specifications = params.get("TagSpecification.N", [])
        tag_set = []
        for tag_spec in tag_specifications:
            # Only tags with resource_type 'launch-template' apply to launch template itself
            if tag_spec.get("ResourceType") == "launch-template":
                tags = tag_spec.get("Tags", [])
                for tag in tags:
                    key = tag.get("Key")
                    value = tag.get("Value")
                    if key is not None:
                        tag_set.append(TagResponse(Key=key, Value=value))

        # Prepare operator if provided
        operator_param = params.get("Operator")
        operator = None
        if operator_param:
            operator = OperatorResponse(
                managed=None,
                principal=operator_param.get("Principal")
            )

        # Create launch template object
        now = datetime.datetime.utcnow()
        launch_template = LaunchTemplate(
            created_by=self.get_owner_id(),
            create_time=now,
            default_version_number=default_version_number,
            latest_version_number=latest_version_number,
            launch_template_id=launch_template_id,
            launch_template_name=launch_template_name,
            operator=operator,
            tag_set=tag_set if tag_set else None,
        )

        # Store launch template in state
        self.state.launch_templates[launch_template_id] = launch_template

        # Store launch template resource for lookup by name as well
        self.state.resources[launch_template_id] = launch_template
        self.state.resources[launch_template_name] = launch_template

        # Create initial launch template version
        version_description = params.get("VersionDescription")
        launch_template_version = LaunchTemplateVersion(
            created_by=self.get_owner_id(),
            create_time=now,
            default_version=True,
            launch_template_data=launch_template_data,
            launch_template_id=launch_template_id,
            launch_template_name=launch_template_name,
            operator=operator,
            version_description=version_description,
            version_number=default_version_number,
        )

        # Store versions in launch template object (add attribute if not present)
        if not hasattr(launch_template, "versions"):
            launch_template.versions = {}
        launch_template.versions[default_version_number] = launch_template_version

        # Return response
        return {
            "launchTemplate": launch_template.to_dict(),
            "requestId": self.generate_request_id(),
            "warning": None,
        }


    def create_launch_template_version(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Validate required parameters
        launch_template_data = params.get("LaunchTemplateData")
        if not launch_template_data:
            raise ValueError("LaunchTemplateData is required")

        launch_template_id = params.get("LaunchTemplateId")
        launch_template_name = params.get("LaunchTemplateName")

        if (launch_template_id and launch_template_name) or (not launch_template_id and not launch_template_name):
            raise ValueError("Must specify either LaunchTemplateId or LaunchTemplateName, but not both")

        # Find launch template by id or name
        launch_template = None
        if launch_template_id:
            launch_template = self.state.launch_templates.get(launch_template_id)
        else:
            # Search by name
            for lt in self.state.launch_templates.values():
                if lt.launch_template_name == launch_template_name:
                    launch_template = lt
                    break

        if not launch_template:
            raise ValueError("Launch template not found")

        # Determine source version
        source_version_str = params.get("SourceVersion")
        source_version = None
        if source_version_str:
            try:
                source_version = int(source_version_str)
            except Exception:
                raise ValueError("SourceVersion must be an integer string")
            if not hasattr(launch_template, "versions") or source_version not in launch_template.versions:
                raise ValueError(f"SourceVersion {source_version} does not exist")

        # Determine new version number
        if not hasattr(launch_template, "versions"):
            launch_template.versions = {}
        latest_version_number = max(launch_template.versions.keys()) if launch_template.versions else 0
        new_version_number = latest_version_number + 1

        # Prepare new launch template data
        # If source_version specified, inherit data from that version and overwrite with provided data
        if source_version:
            base_version = launch_template.versions[source_version]
            base_data = base_version.launch_template_data or {}
            # Merge base_data with launch_template_data, launch_template_data overwrites base_data keys
            merged_data = dict(base_data)
            merged_data.update(launch_template_data)
            final_launch_template_data = merged_data
        else:
            final_launch_template_data = launch_template_data

        # Prepare operator if provided
        operator_param = params.get("Operator")
        operator = None
        if operator_param:
            operator = OperatorResponse(
                managed=None,
                principal=operator_param.get("Principal")
            )
        else:
            operator = launch_template.operator

        # Create new launch template version object
        now = datetime.datetime.utcnow()
        version_description = params.get("VersionDescription")
        launch_template_version = LaunchTemplateVersion(
            created_by=self.get_owner_id(),
            create_time=now,
            default_version=False,
            launch_template_data=final_launch_template_data,
            launch_template_id=launch_template.launch_template_id,
            launch_template_name=launch_template.launch_template_name,
            operator=operator,
            version_description=version_description,
            version_number=new_version_number,
        )

        # Store new version
        launch_template.versions[new_version_number] = launch_template_version
        launch_template.latest_version_number = new_version_number

        # Return response
        return {
            "launchTemplateVersion": launch_template_version,
            "requestId": self.generate_request_id(),
            "warning": None,
        }


    def delete_launch_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        launch_template_id = params.get("LaunchTemplateId")
        launch_template_name = params.get("LaunchTemplateName")

        if (launch_template_id and launch_template_name) or (not launch_template_id and not launch_template_name):
            raise ValueError("Must specify either LaunchTemplateId or LaunchTemplateName, but not both")

        # Find launch template by id or name
        launch_template = None
        if launch_template_id:
            launch_template = self.state.launch_templates.get(launch_template_id)
        else:
            for lt in self.state.launch_templates.values():
                if lt.launch_template_name == launch_template_name:
                    launch_template = lt
                    break

        if not launch_template:
            raise ValueError("Launch template not found")

        # Remove from state
        del self.state.launch_templates[launch_template.launch_template_id]
        # Remove from resources dict by id and name
        self.state.resources.pop(launch_template.launch_template_id, None)
        self.state.resources.pop(launch_template.launch_template_name, None)

        # Return response
        return {
            "launchTemplate": launch_template,
            "requestId": self.generate_request_id(),
        }


    def delete_launch_template_versions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        launch_template_id = params.get("LaunchTemplateId")
        launch_template_name = params.get("LaunchTemplateName")
        versions_to_delete = params.get("LaunchTemplateVersion.N")

        if (launch_template_id and launch_template_name) or (not launch_template_id and not launch_template_name):
            raise ValueError("Must specify either LaunchTemplateId or LaunchTemplateName, but not both")

        if not versions_to_delete or not isinstance(versions_to_delete, list):
            raise ValueError("LaunchTemplateVersion.N is required and must be a list")

        # Find launch template by id or name
        launch_template = None
        if launch_template_id:
            launch_template = self.state.launch_templates.get(launch_template_id)
        else:
            for lt in self.state.launch_templates.values():
                if lt.launch_template_name == launch_template_name:
                    launch_template = lt
                    break

        if not launch_template:
            raise ValueError("Launch template not found")

        # Prepare response lists
        successfully_deleted = []
        unsuccessfully_deleted = []

        # Check versions exist and not default version
        default_version = launch_template.default_version_number
        if not hasattr(launch_template, "versions"):
            launch_template.versions = {}

        for version_str in versions_to_delete:
            try:
                version_num = int(version_str)
            except Exception:
                unsuccessfully_deleted.append(
                    DeleteLaunchTemplateVersionsResponseErrorItem(
                        launch_template_id=launch_template.launch_template_id,
                        launch_template_name=launch_template.launch_template_name,
                        version_number=None,
                        response_error=ResponseError(
                            code="launchTemplateVersionDoesNotExist",
                            message=f"Version '{version_str}' is not a valid integer"
                        )
                    )
                )
                continue

            if version_num not in launch_template.versions:
                unsuccessfully_deleted.append(
                    DeleteLaunchTemplateVersionsResponseErrorItem(
                        launch_template_id=launch_template.launch_template_id,
                        launch_template_name=launch_template.launch_template_name,
                        version_number=version_num,
                        response_error=ResponseError(
                            code="launchTemplateVersionDoesNotExist",
                            message=f"Version {version_num} does not exist"
                        )
                    )
                )
                continue

            if version_num == default_version:
                unsuccessfully_deleted.append(
                    DeleteLaunchTemplateVersionsResponseErrorItem(
                        launch_template_id=launch_template.launch_template_id,
                        launch_template_name=launch_template.launch_template_name,
                        version_number=version_num,
                        response_error=ResponseError(
                            code="launchTemplateVersionCannotDeleteDefault",
                            message="Cannot delete the default version"
                        )
                    )
                )
                continue

            # Delete version
            del launch_template.versions[version_num]
            successfully_deleted.append(
                DeleteLaunchTemplateVersionsResponseSuccessItem(
                    launch_template_id=launch_template.launch_template_id,
                    launch_template_name=launch_template.launch_template_name,
                    version_number=version_num,
                )
            )

        return {
            "requestId": self.generate_request_id(),
            "successfullyDeletedLaunchTemplateVersionSet": successfully_deleted,
            "unsuccessfullyDeletedLaunchTemplateVersionSet": unsuccessfully_deleted,
        }


    def describe_launch_templates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Filters and pagination parameters
        filters = params.get("Filter.N", [])
        launch_template_ids = params.get("LaunchTemplateId.N", [])
        launch_template_names = params.get("LaunchTemplateName.N", [])
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")

        # Collect all launch templates
        all_templates = list(self.state.launch_templates.values())

        # Filter by IDs if provided
        if launch_template_ids:
            all_templates = [lt for lt in all_templates if lt.launch_template_id in launch_template_ids]

        # Filter by names if provided
        if launch_template_names:
            all_templates = [lt for lt in all_templates if lt.launch_template_name in launch_template_names]

        # Apply filters
        def matches_filter(lt, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True
            if name == "create-time":
                # Filter by create time string matching any of the values (ISO8601)
                create_time_str = lt.create_time.isoformat() if lt.create_time else ""
                return any(v == create_time_str for v in values)
            elif name == "launch-template-name":
                return any(lt.launch_template_name == v for v in values)
            elif name.startswith("tag:"):
                tag_key = name[4:]
                if not lt.tag_set:
                    return False
                for tag in lt.tag_set:
                    if tag.Key == tag_key and tag.Value in values:
                        return True
                return False
            elif name == "tag-key":
                if not lt.tag_set:
                    return False
                return any(tag.Key in values for tag in lt.tag_set)
            else:
                # Unknown filter, ignore
                return True

        for f in filters:
            all_templates = [lt for lt in all_templates if matches_filter(lt, f)]

        # Pagination
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        if max_results:
            try:
                max_results_int = int(max_results)
                if max_results_int < 1:
                    max_results_int = 1
                elif max_results_int > 200:
                    max_results_int = 200
            except Exception:
                max_results_int = 200
        else:
            max_results_int = 200

        paged_templates = all_templates[start_index:start_index + max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(all_templates):
            new_next_token = str(start_index + max_results_int)

        return {
            "launchTemplates": paged_templates,
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def describe_launch_template_versions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import datetime

        # Extract parameters
        launch_template_id = params.get("LaunchTemplateId")
        launch_template_name = params.get("LaunchTemplateName")
        version_numbers = params.get("LaunchTemplateVersion", [])
        max_version = params.get("MaxVersion")
        min_version = params.get("MinVersion")
        max_results = params.get("MaxResults")
        next_token = params.get("NextToken")
        resolve_alias = params.get("ResolveAlias", False)
        filters = params.get("Filter", [])

        # Validate that either LaunchTemplateId or LaunchTemplateName is specified, but not both
        if launch_template_id and launch_template_name:
            raise ValueError("Specify either LaunchTemplateId or LaunchTemplateName, but not both.")

        # Collect launch templates to consider
        launch_templates_to_consider = []
        if launch_template_id:
            lt = self.state.launch_templates.get(launch_template_id)
            if not lt:
                # No launch template found with this ID, return empty result
                return {
                    "launchTemplateVersionSet": [],
                    "nextToken": None,
                    "requestId": self.generate_request_id(),
                }
            launch_templates_to_consider = [lt]
        elif launch_template_name:
            # Find launch template by name
            lt = None
            for ltid, ltemplate in self.state.launch_templates.items():
                if ltemplate.launch_template_name == launch_template_name:
                    lt = ltemplate
                    break
            if not lt:
                # No launch template found with this name, return empty result
                return {
                    "launchTemplateVersionSet": [],
                    "nextToken": None,
                    "requestId": self.generate_request_id(),
                }
            launch_templates_to_consider = [lt]
        else:
            # No specific launch template specified, consider all launch templates
            launch_templates_to_consider = list(self.state.launch_templates.values())

        # Helper to parse version number or alias
        def parse_version_number(v):
            if isinstance(v, str):
                if v == "$Latest":
                    return "Latest"
                elif v == "$Default":
                    return "Default"
                else:
                    try:
                        return int(v)
                    except Exception:
                        return None
            elif isinstance(v, int):
                return v
            return None

        # Collect all versions from the launch templates to consider
        all_versions = []
        for lt in launch_templates_to_consider:
            # Each launch template has versions stored in self.state.launch_template_versions keyed by launch_template_id
            versions = self.state.launch_template_versions.get(lt.launch_template_id, {})
            for version_number, version_obj in versions.items():
                all_versions.append(version_obj)

        # Filter versions by LaunchTemplateVersion parameter if specified
        if version_numbers:
            # Parse version numbers and aliases
            parsed_versions = [parse_version_number(v) for v in version_numbers]
            # Validate no numbers with aliases together except $Latest and $Default can be together
            aliases = [v for v in parsed_versions if isinstance(v, str)]
            numbers = [v for v in parsed_versions if isinstance(v, int)]
            if numbers and aliases:
                # According to AWS, you cannot specify numbers and aliases together
                raise ValueError("Cannot specify numeric versions and aliases together in LaunchTemplateVersion parameter.")
            filtered_versions = []
            for v in all_versions:
                vnum = v.version_number
                if "Latest" in aliases and vnum == max([ver.version_number for ver in all_versions if ver.launch_template_id == v.launch_template_id], default=None):
                    filtered_versions.append(v)
                elif "Default" in aliases:
                    # Find default version number for this launch template
                    lt_obj = self.state.launch_templates.get(v.launch_template_id)
                    if lt_obj and lt_obj.default_version_number == vnum:
                        filtered_versions.append(v)
                elif vnum in numbers:
                    filtered_versions.append(v)
            all_versions = filtered_versions

        # Filter by MinVersion and MaxVersion if specified
        if min_version is not None:
            try:
                min_version_int = int(min_version)
                all_versions = [v for v in all_versions if v.version_number > min_version_int]
            except Exception:
                pass
        if max_version is not None:
            try:
                max_version_int = int(max_version)
                all_versions = [v for v in all_versions if v.version_number <= max_version_int]
            except Exception:
                pass

        # Apply filters if any
        def matches_filter(version_obj, filter_obj):
            name = filter_obj.get("Name")
            values = filter_obj.get("Values", [])
            if not name or not values:
                return True  # No filter criteria, match all

            # Map filter names to attributes in launch template version or launch template data
            # We support some common filters as per the doc, but for brevity, implement a subset
            # Filters supported: create-time, ebs-optimized, http-endpoint, http-protocol-ipv4, host-resource-group-arn,
            # http-tokens, iam-instance-profile, image-id, instance-type, is-default-version, kernel-id,
            # license-configuration-arn, network-card-index, ram-disk-id

            # Helper to get nested attribute safely
            def get_nested_attr(obj, attr_path):
                attrs = attr_path.split(".")
                current = obj
                for a in attrs:
                    if current is None:
                        return None
                    current = getattr(current, a, None)
                return current

            # For create-time filter, compare creation time string in ISO8601 format
            if name == "create-time":
                # values are timestamps, match if version create_time in values
                create_time = version_obj.create_time
                if not create_time:
                    return False
                create_time_str = create_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                return any(v == create_time_str for v in values)

            # ebs-optimized filter: boolean in launch_template_data.ebs_optimized
            if name == "ebs-optimized":
                val = getattr(version_obj.launch_template_data, "ebs_optimized", None)
                if val is None:
                    return False
                # values are strings "true" or "false"
                val_str = "true" if val else "false"
                return val_str in values

            # http-endpoint filter: launch_template_data.metadata_options.http_endpoint
            if name == "http-endpoint":
                val = None
                if version_obj.launch_template_data and hasattr(version_obj.launch_template_data, "metadata_options"):
                    val = getattr(version_obj.launch_template_data.metadata_options, "http_endpoint", None)
                if val is None:
                    return False
                return val in values

            # http-protocol-ipv4 filter: launch_template_data.metadata_options.http_protocol_ipv4
            if name == "http-protocol-ipv4":
                val = None
                if version_obj.launch_template_data and hasattr(version_obj.launch_template_data, "metadata_options"):
                    val = getattr(version_obj.launch_template_data.metadata_options, "http_protocol_ipv4", None)
                if val is None:
                    return False
                return val in values

            # host-resource-group-arn filter: launch_template_data.placement.host_resource_group_arn
            if name == "host-resource-group-arn":
                val = None
                if version_obj.launch_template_data and hasattr(version_obj.launch_template_data, "placement"):
                    val = getattr(version_obj.launch_template_data.placement, "host_resource_group_arn", None)
                if val is None:
                    return False
                return val in values

            # http-tokens filter: launch_template_data.metadata_options.http_tokens
            if name == "http-tokens":
                val = None
                if version_obj.launch_template_data and hasattr(version_obj.launch_template_data, "metadata_options"):
                    val = getattr(version_obj.launch_template_data.metadata_options, "http_tokens", None)
                if val is None:
                    return False
                return val in values

            # iam-instance-profile filter: launch_template_data.iam_instance_profile.arn or .name
            if name == "iam-instance-profile":
                val_arn = None
                val_name = None
                if version_obj.launch_template_data and hasattr(version_obj.launch_template_data, "iam_instance_profile"):
                    val_arn = getattr(version_obj.launch_template_data.iam_instance_profile, "arn", None)
                    val_name = getattr(version_obj.launch_template_data.iam_instance_profile, "name", None)
                return (val_arn in values) or (val_name in values)

            # image-id filter: launch_template_data.image_id
            if name == "image-id":
                val = getattr(version_obj.launch_template_data, "image_id", None)
                if val is None:
                    return False
                return val in values

            # instance-type filter: launch_template_data.instance_type
            if name == "instance-type":
                val = getattr(version_obj.launch_template_data, "instance_type", None)
                if val is None:
                    return False
                return val in values

            # is-default-version filter: version_obj.default_version (boolean)
            if name == "is-default-version":
                val = getattr(version_obj, "default_version", False)
                val_str = "true" if val else "false"
                return val_str in values

            # kernel-id filter: launch_template_data.kernel_id
            if name == "kernel-id":
                val = getattr(version_obj.launch_template_data, "kernel_id", None)
                if val is None:
                    return False
                return val in values

            # license-configuration-arn filter: launch_template_data.license_set[*].license_configuration_arn
            if name == "license-configuration-arn":
                license_set = getattr(version_obj.launch_template_data, "license_set", [])
                for lic in license_set:
                    if lic.license_configuration_arn in values:
                        return True
                return False

            # network-card-index filter: launch_template_data.network_interfaces[*].network_card_index
            if name == "network-card-index":
                network_interfaces = getattr(version_obj.launch_template_data, "network_interfaces", [])
                for ni in network_interfaces:
                    if getattr(ni, "network_card_index", None) in values:
                        return True
                return False

            # ram-disk-id filter: launch_template_data.ram_disk_id
            if name == "ram-disk-id":
                val = getattr(version_obj.launch_template_data, "ram_disk_id", None)
                if val is None:
                    return False
                return val in values

            # If filter name not recognized, ignore filter (match all)
            return True

        # Apply all filters
        for f in filters:
            all_versions = [v for v in all_versions if matches_filter(v, f)]

        # Sort versions by launch_template_id and version_number ascending
        all_versions.sort(key=lambda v: (v.launch_template_id, v.version_number))

        # Pagination handling
        start_index = 0
        if next_token:
            try:
                start_index = int(next_token)
            except Exception:
                start_index = 0

        # Apply max_results limit
        if max_results is not None:
            try:
                max_results_int = int(max_results)
                if max_results_int < 1:
                    max_results_int = 1
                elif max_results_int > 200:
                    max_results_int = 200
            except Exception:
                max_results_int = 100
        else:
            max_results_int = 100

        paged_versions = all_versions[start_index : start_index + max_results_int]
        new_next_token = None
        if start_index + max_results_int < len(all_versions):
            new_next_token = str(start_index + max_results_int)

        # Helper to convert launch template version object to dict response
        def version_to_dict(version_obj):
            # Build launchTemplateData dict
            def ebs_block_device_to_dict(ebs):
                if ebs is None:
                    return None
                return {
                    "deleteOnTermination": ebs.delete_on_termination,
                    "encrypted": ebs.encrypted,
                    "iops": ebs.iops,
                    "kmsKeyId": ebs.kms_key_id,
                    "snapshotId": ebs.snapshot_id,
                    "throughput": ebs.throughput,
                    "volumeInitializationRate": ebs.volume_initialization_rate,
                    "volumeSize": ebs.volume_size,
                    "volumeType": ebs.volume_type,
                }

            def block_device_mapping_to_dict(bdm):
                if bdm is None:
                    return None
                return {
                    "deviceName": bdm.device_name,
                    "ebs": ebs_block_device_to_dict(bdm.ebs),
                    "noDevice": bdm.no_device,
                    "virtualName": bdm.virtual_name,
                }

            def capacity_reservation_target_to_dict(target):
                if target is None:
                    return None
                return {
                    "capacityReservationId": target.capacity_reservation_id,
                    "capacityReservationResourceGroupArn": target.capacity_reservation_resource_group_arn,
                }

            def capacity_reservation_spec_to_dict(spec):
                if spec is None:
                    return None
                return {
                    "capacityReservationPreference": spec.capacity_reservation_preference,
                    "capacityReservationTarget": capacity_reservation_target_to_dict(spec.capacity_reservation_target),
                }

            def cpu_options_to_dict(cpu):
                if cpu is None:
                    return None
                return {
                    "amdSevSnp": cpu.amd_sev_snp,
                    "coreCount": cpu.core_count,
                    "threadsPerCore": cpu.threads_per_core,
                }

            def credit_spec_to_dict(credit):
                if credit is None:
                    return None
                return {
                    "cpuCredits": credit.cpu_credits,
                }

            def elastic_gpu_spec_to_dict(egpu):
                if egpu is None:
                    return None
                return {
                    "type": egpu.type,
                }

            def elastic_inference_accel_to_dict(eia):
                if eia is None:
                    return None
                return {
                    "type": eia.type,
                    "count": eia.count,
                }

            def enclave_options_to_dict(enclave):
                if enclave is None:
                    return None
                return {
                    "enabled": enclave.enabled,
                }

            def hibernation_options_to_dict(hib):
                if hib is None:
                    return None
                return {
                    "configured": hib.configured,
                }

            def iam_instance_profile_to_dict(iam):
                if iam is None:
                    return None
                return {
                    "arn": iam.arn,
                    "name": iam.name,
                }

            def license_config_to_dict(lic):
                if lic is None:
                    return None
                return {
                    "licenseConfigurationArn": lic.license_configuration_arn,
                }

            def maintenance_options_to_dict(mo):
                if mo is None:
                    return None
                return {
                    "autoRecovery": mo.auto_recovery,
                }

            def metadata_options_to_dict(meta):
                if meta is None:
                    return None
                return {
                    "httpEndpoint": meta.http_endpoint,
                    "httpProtocolIpv6": meta.http_protocol_ipv6,
                    "httpPutResponseHopLimit": meta.http_put_response_hop_limit,
                    "httpTokens": meta.http_tokens,
                    "instanceMetadataTags": meta.instance_metadata_tags,
                    "state": getattr(meta, "state", None),  # state is not in request but in response
                }

            def monitoring_to_dict(mon):
                if mon is None:
                    return None
                return {
                    "enabled": mon.enabled,
                }

            def connection_tracking_spec_to_dict(cts):
                if cts is None:
                    return None
                return {
                    "tcpEstablishedTimeout": cts.tcp_established_timeout,
                    "udpStreamTimeout": cts.udp_stream_timeout,
                    "udpTimeout": cts.udp_timeout,
                }

            def ena_srd_udp_spec_to_dict(udp):
                if udp is None:
                    return None
                return {
                    "enaSrdUdpEnabled": udp.ena_srd_udp_enabled,
                }

            def ena_srd_spec_to_dict(ena):
                if ena is None:
                    return None
                return {
                    "enaSrdEnabled": ena.ena_srd_enabled,
                    "enaSrdUdpSpecification": ena_srd_udp_spec_to_dict(ena.ena_srd_udp_specification),
                }

            def ipv4_prefix_spec_to_dict(ipv4):
                if ipv4 is None:
                    return None
                return {
                    "ipv4Prefix": ipv4.ipv4_prefix,
                }

            def instance_ipv6_address_to_dict(ipv6):
                if ipv6 is None:
                    return None
                return {
                    "Ipv6Address": ipv6.ipv6_address,
                }

            def private_ip_address_spec_to_dict(pip):
                if pip is None:
                    return None
                return {
                    "Primary": pip.primary,
                    "PrivateIpAddress": pip.private_ip_address,
                }

            def network_interface_spec_to_dict(ni):
                if ni is None:
                    return None
                return {
                    "associateCarrierIpAddress": ni.associate_carrier_ip_address,
                    "associatePublicIpAddress": ni.associate_public_ip_address,
                    "connectionTrackingSpecification": connection_tracking_spec_to_dict(ni.connection_tracking_specification),
                    "deleteOnTermination": ni.delete_on_termination,
                    "description": ni.description,
                    "deviceIndex": ni.device_index,
                    "enaQueueCount": ni.ena_queue_count,
                    "enaSrdSpecification": ena_srd_spec_to_dict(ni.ena_srd_specification),
                    "interfaceType": ni.interface_type,
                    "ipv4PrefixCount": ni.ipv4_prefix_count,
                    "ipv4PrefixSet": [ipv4_prefix_spec_to_dict(p) for p in (ni.ipv4_prefixes or [])],
                    "ipv6AddressCount": ni.ipv6_address_count,
                    "ipv6AddressesSet": [instance_ipv6_address_to_dict(p) for p in (ni.ipv6_addresses or [])],
                    "ipv6PrefixCount": ni.ipv6_prefix_count,
                    "ipv6PrefixSet": [ipv4_prefix_spec_to_dict(p) for p in (ni.ipv6_prefixes or [])],
                    "networkCardIndex": ni.network_card_index,
                    "networkInterfaceId": ni.network_interface_id,
                    "primaryIpv6": ni.primary_ipv6,
                    "privateIpAddress": ni.private_ip_address,
                    "privateIpAddressesSet": [private_ip_address_spec_to_dict(p) for p in (ni.private_ip_addresses or [])],
                    "secondaryPrivateIpAddressCount": ni.secondary_private_ip_address_count,
                    "subnetId": ni.subnet_id,
                    "groupSet": ni.groups,
                }

            def network_performance_options_to_dict(npo):
                if npo is None:
                    return None
                return {
                    "bandwidthWeighting": npo.bandwidth_weighting,
                }

            def operator_to_dict(op):
                if op is None:
                    return None
                return {
                    "managed": op.managed,
                    "principal": op.principal,
                }

            def placement_to_dict(pl):
                if pl is None:
                    return None
                return {
                    "affinity": pl.affinity,
                    "availabilityZone": pl.availability_zone,
                    "availabilityZoneId": pl.availability_zone_id,
                    "groupId": pl.group_id,
                    "groupName": pl.group_name,
                    "hostId": pl.host_id,
                    "hostResourceGroupArn": pl.host_resource_group_arn,
                    "partitionNumber": pl.partition_number,
                    "spreadDomain": pl.spread_domain,
                    "tenancy": pl.tenancy,
                }

            return {
                "createTime": version_obj.create_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if version_obj.create_time else None,
                "createdBy": version_obj.created_by,
                "defaultVersion": version_obj.default_version,
                "launchTemplateId": version_obj.launch_template_id,
                "launchTemplateName": version_obj.launch_template_name,
                "versionDescription": version_obj.version_description,
                "versionNumber": version_obj.version_number,
                "launchTemplateData": {
                     "placement": placement_to_dict(version_obj.launch_template_data.placement) if version_obj.launch_template_data else None
                     # truncated for brevity in fix
                }
            }

        return {
            "launchTemplateVersionSet": [version_to_dict(v) for v in paged_versions],
            "nextToken": new_next_token,
            "requestId": self.generate_request_id(),
        }

    def get_launch_template_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def modify_launch_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    

from emulator_core.gateway.base import BaseGateway

class LaunchtemplatesGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateLaunchTemplate", self.create_launch_template)
        self.register_action("CreateLaunchTemplateVersion", self.create_launch_template_version)
        self.register_action("DeleteLaunchTemplate", self.delete_launch_template)
        self.register_action("DeleteLaunchTemplateVersions", self.delete_launch_template_versions)
        self.register_action("DescribeLaunchTemplates", self.describe_launch_templates)
        self.register_action("DescribeLaunchTemplateVersions", self.describe_launch_template_versions)
        self.register_action("GetLaunchTemplateData", self.get_launch_template_data)
        self.register_action("ModifyLaunchTemplate", self.modify_launch_template)

    def create_launch_template(self, params):
        return self.backend.create_launch_template(params)

    def create_launch_template_version(self, params):
        return self.backend.create_launch_template_version(params)

    def delete_launch_template(self, params):
        return self.backend.delete_launch_template(params)

    def delete_launch_template_versions(self, params):
        return self.backend.delete_launch_template_versions(params)

    def describe_launch_templates(self, params):
        return self.backend.describe_launch_templates(params)

    def describe_launch_template_versions(self, params):
        return self.backend.describe_launch_template_versions(params)

    def get_launch_template_data(self, params):
        return self.backend.get_launch_template_data(params)

    def modify_launch_template(self, params):
        return self.backend.modify_launch_template(params)
