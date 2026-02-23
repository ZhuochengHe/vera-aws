from __future__ import annotations
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import uuid
import random
import json as _json

from ..utils import (
    create_gcp_error, is_error_response,
    make_operation, parse_labels, get_body_param,
)
from ..state import GCPState

@dataclass
class GlobalNetworkEndpointGroup:
    psc_data: Dict[str, Any] = field(default_factory=dict)
    cloud_function: Dict[str, Any] = field(default_factory=dict)
    region: str = ""
    network: str = ""
    zone: str = ""
    subnetwork: str = ""
    psc_target_service: str = ""
    default_port: int = 0
    size: int = 0
    creation_timestamp: str = ""
    app_engine: Dict[str, Any] = field(default_factory=dict)
    name: str = ""
    annotations: Dict[str, Any] = field(default_factory=dict)
    network_endpoint_type: str = ""
    cloud_run: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    id: str = ""

    network_endpoints: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        d["pscData"] = self.psc_data
        d["cloudFunction"] = self.cloud_function
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.network is not None and self.network != "":
            d["network"] = self.network
        if self.zone is not None and self.zone != "":
            d["zone"] = self.zone
        if self.subnetwork is not None and self.subnetwork != "":
            d["subnetwork"] = self.subnetwork
        if self.psc_target_service is not None and self.psc_target_service != "":
            d["pscTargetService"] = self.psc_target_service
        if self.default_port is not None and self.default_port != 0:
            d["defaultPort"] = self.default_port
        if self.size is not None and self.size != 0:
            d["size"] = self.size
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["appEngine"] = self.app_engine
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["annotations"] = self.annotations
        if self.network_endpoint_type is not None and self.network_endpoint_type != "":
            d["networkEndpointType"] = self.network_endpoint_type
        d["cloudRun"] = self.cloud_run
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#globalnetworkendpointgroup"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class GlobalNetworkEndpointGroup_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.global_network_endpoint_groups  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "global-network-endpoint-group") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _get_resource_or_error(self, name: str) -> Dict[str, Any] | GlobalNetworkEndpointGroup:
        resource = self.resources.get(name)
        if not resource:
            return create_gcp_error(
                404,
                f"The resource '{name}' was not found",
                "NOT_FOUND",
            )
        return resource

    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a network endpoint group in the specified project using the
parameters that are included in the request.

Note: Use the following APIs to manage network endpoint groups:
   
   - 
   To man..."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("NetworkEndpointGroup")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'NetworkEndpointGroup' not specified",
                "INVALID_ARGUMENT",
            )
        name = body.get("name")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'name' not specified",
                "INVALID_ARGUMENT",
            )
        if name in self.resources:
            return create_gcp_error(
                409,
                f"GlobalNetworkEndpointGroup '{name}' already exists",
                "ALREADY_EXISTS",
            )
        network = body.get("network", "") or ""
        if network and not self.state.networks.get(network):
            return create_gcp_error(404, f"Network '{network}' not found", "NOT_FOUND")
        subnetwork = body.get("subnetwork", "") or ""
        if subnetwork and not self.state.subnetworks.get(subnetwork):
            return create_gcp_error(
                404,
                f"Subnetwork '{subnetwork}' not found",
                "NOT_FOUND",
            )
        psc_target_service = body.get("pscTargetService", "") or ""
        if psc_target_service and not self.state.service_attachments.get(psc_target_service):
            return create_gcp_error(
                404,
                f"Service attachment '{psc_target_service}' not found",
                "NOT_FOUND",
            )
        resource = GlobalNetworkEndpointGroup(
            psc_data=body.get("pscData", {}) or {},
            cloud_function=body.get("cloudFunction", {}) or {},
            region=body.get("region", "") or "",
            network=network,
            zone=body.get("zone", "") or "",
            subnetwork=subnetwork,
            psc_target_service=psc_target_service,
            default_port=body.get("defaultPort", 0) or 0,
            size=body.get("size", 0) or 0,
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            app_engine=body.get("appEngine", {}) or {},
            name=name,
            annotations=body.get("annotations", {}) or {},
            network_endpoint_type=body.get("networkEndpointType", "") or "",
            cloud_run=body.get("cloudRun", {}) or {},
            description=body.get("description", "") or "",
            id=self._generate_id(),
            network_endpoints=[],
        )
        self.resources[name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/global/networkEndpointGroups/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified network endpoint group."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        name = params.get("networkEndpointGroup")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEndpointGroup' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves the list of network endpoint groups that are located in the
specified project."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [
                    resource
                    for resource in resources
                    if resource.name == match.group(1)
                ]
        zone = params.get("zone")
        if zone and hasattr(resources[0] if resources else object(), "zone"):
            resources = [resource for resource in resources if resource.zone == zone]
        region = params.get("region")
        if region:
            resources = [resource for resource in resources if resource.region == region]
        return {
            "kind": "compute#globalnetworkendpointgroupList",
            "id": f"projects/{project}/global/networkEndpointGroups",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def detachNetworkEndpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detach the network endpoint from the specified network endpoint group."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        name = params.get("networkEndpointGroup")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEndpointGroup' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("GlobalNetworkEndpointGroupsDetachEndpointsRequest")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'GlobalNetworkEndpointGroupsDetachEndpointsRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        endpoints = body.get("networkEndpoints") or []
        if endpoints:
            resource.network_endpoints = [
                endpoint
                for endpoint in resource.network_endpoints
                if endpoint not in endpoints
            ]
        return make_operation(
            operation_type="detachNetworkEndpoints",
            resource_link=f"projects/{project}/global/networkEndpointGroups/{resource.name}",
            params=params,
        )

    def attachNetworkEndpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Attach a network endpoint to the specified network endpoint group."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        name = params.get("networkEndpointGroup")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEndpointGroup' not specified",
                "INVALID_ARGUMENT",
            )
        body = params.get("GlobalNetworkEndpointGroupsAttachEndpointsRequest")
        if body is None:
            return create_gcp_error(
                400,
                "Required field 'GlobalNetworkEndpointGroupsAttachEndpointsRequest' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        endpoints = body.get("networkEndpoints") or []
        if endpoints:
            existing = resource.network_endpoints
            for endpoint in endpoints:
                if endpoint not in existing:
                    existing.append(endpoint)
        return make_operation(
            operation_type="attachNetworkEndpoints",
            resource_link=f"projects/{project}/global/networkEndpointGroups/{resource.name}",
            params=params,
        )

    def listNetworkEndpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lists the network endpoints in the specified network endpoint group."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        name = params.get("networkEndpointGroup")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEndpointGroup' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        endpoints = list(resource.network_endpoints)
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re

            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                endpoints = [
                    endpoint
                    for endpoint in endpoints
                    if isinstance(endpoint, dict)
                    and endpoint.get("name") == match.group(1)
                ]
        return {
            "kind": "compute#networkEndpointGroupsListNetworkEndpoints",
            "id": f"projects/{project}/global/networkEndpointGroups/{resource.name}/listNetworkEndpoints",
            "items": endpoints,
            "selfLink": "",
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified network endpoint group.Note that the NEG cannot be
deleted if there are backend services referencing it."""
        project = params.get("project")
        if not project:
            return create_gcp_error(
                400,
                "Required field 'project' not specified",
                "INVALID_ARGUMENT",
            )
        name = params.get("networkEndpointGroup")
        if not name:
            return create_gcp_error(
                400,
                "Required field 'networkEndpointGroup' not specified",
                "INVALID_ARGUMENT",
            )
        resource = self._get_resource_or_error(name)
        if is_error_response(resource):
            return resource
        backend_services = list(self.state.backend_services.values()) + list(
            self.state.region_backend_services.values()
        )
        for backend_service in backend_services:
            for backend in backend_service.backends:
                if not isinstance(backend, dict):
                    continue
                group = backend.get("group") or backend.get("groupLink") or ""
                if group == name or group.endswith(f"/{name}"):
                    return create_gcp_error(
                        400,
                        "GlobalNetworkEndpointGroup is in use by backend services",
                        "FAILED_PRECONDITION",
                    )
        self.resources.pop(name, None)
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/global/networkEndpointGroups/{name}",
            params=params,
        )


class global_network_endpoint_group_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'detachNetworkEndpoints': global_network_endpoint_group_RequestParser._parse_detachNetworkEndpoints,
            'attachNetworkEndpoints': global_network_endpoint_group_RequestParser._parse_attachNetworkEndpoints,
            'list': global_network_endpoint_group_RequestParser._parse_list,
            'insert': global_network_endpoint_group_RequestParser._parse_insert,
            'get': global_network_endpoint_group_RequestParser._parse_get,
            'listNetworkEndpoints': global_network_endpoint_group_RequestParser._parse_listNetworkEndpoints,
            'delete': global_network_endpoint_group_RequestParser._parse_delete,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

    @staticmethod
    def _parse_detachNetworkEndpoints(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['GlobalNetworkEndpointGroupsDetachEndpointsRequest'] = body.get('GlobalNetworkEndpointGroupsDetachEndpointsRequest')
        return params

    @staticmethod
    def _parse_attachNetworkEndpoints(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['GlobalNetworkEndpointGroupsAttachEndpointsRequest'] = body.get('GlobalNetworkEndpointGroupsAttachEndpointsRequest')
        return params

    @staticmethod
    def _parse_list(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        return params

    @staticmethod
    def _parse_insert(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        # Body params
        params['NetworkEndpointGroup'] = body.get('NetworkEndpointGroup')
        return params

    @staticmethod
    def _parse_get(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        return params

    @staticmethod
    def _parse_listNetworkEndpoints(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'filter' in query_params:
            params['filter'] = query_params['filter']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        # Full request body (resource representation)
        params["body"] = body
        return params

    @staticmethod
    def _parse_delete(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        if 'requestId' in query_params:
            params['requestId'] = query_params['requestId']
        return params


class global_network_endpoint_group_ResponseSerializer:
    @staticmethod
    def serialize(
        method_name: str,
        data: Dict[str, Any],
        request_id: str,
    ) -> str:
        if is_error_response(data):
            from ..utils import serialize_gcp_error
            return serialize_gcp_error(data)
        serializers = {
            'detachNetworkEndpoints': global_network_endpoint_group_ResponseSerializer._serialize_detachNetworkEndpoints,
            'attachNetworkEndpoints': global_network_endpoint_group_ResponseSerializer._serialize_attachNetworkEndpoints,
            'list': global_network_endpoint_group_ResponseSerializer._serialize_list,
            'insert': global_network_endpoint_group_ResponseSerializer._serialize_insert,
            'get': global_network_endpoint_group_ResponseSerializer._serialize_get,
            'listNetworkEndpoints': global_network_endpoint_group_ResponseSerializer._serialize_listNetworkEndpoints,
            'delete': global_network_endpoint_group_ResponseSerializer._serialize_delete,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_detachNetworkEndpoints(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_attachNetworkEndpoints(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_listNetworkEndpoints(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

