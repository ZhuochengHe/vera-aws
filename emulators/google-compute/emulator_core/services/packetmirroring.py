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
class PacketMirroring:
    name: str = ""
    collector_ilb: Dict[str, Any] = field(default_factory=dict)
    enable: str = ""
    description: str = ""
    region: str = ""
    creation_timestamp: str = ""
    mirrored_resources: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    network: Dict[str, Any] = field(default_factory=dict)
    filter: Dict[str, Any] = field(default_factory=dict)
    id: str = ""


    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.name is not None and self.name != "":
            d["name"] = self.name
        d["collectorIlb"] = self.collector_ilb
        if self.enable is not None and self.enable != "":
            d["enable"] = self.enable
        if self.description is not None and self.description != "":
            d["description"] = self.description
        if self.region is not None and self.region != "":
            d["region"] = self.region
        if self.creation_timestamp is not None and self.creation_timestamp != "":
            d["creationTimestamp"] = self.creation_timestamp
        d["mirroredResources"] = self.mirrored_resources
        if self.priority is not None and self.priority != 0:
            d["priority"] = self.priority
        d["network"] = self.network
        d["filter"] = self.filter
        if self.id is not None and self.id != "":
            d["id"] = self.id
        d["kind"] = "compute#packetmirroring"
        d["selfLink"] = f"https://www.googleapis.com/compute/v1/{self.name}"
        return d

class PacketMirroring_Backend:
    def __init__(self):
        self.state = GCPState.get()
        self.resources = self.state.packet_mirrorings  # alias to shared store

    def _generate_id(self) -> str:
        return str(random.randint(10**17, 10**18 - 1))

    def _generate_name(self, prefix: str = "packet-mirroring") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"


    def insert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a PacketMirroring resource in the specified project and region
using the data included in the request."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        body = params.get("PacketMirroring")
        if not body:
            return create_gcp_error(400, "Required field 'PacketMirroring' not specified", "INVALID_ARGUMENT")
        name = body.get("name")
        if not name:
            return create_gcp_error(400, "Required field 'name' not specified", "INVALID_ARGUMENT")
        if name in self.resources:
            return create_gcp_error(409, f"PacketMirroring {name!r} already exists", "ALREADY_EXISTS")
        network = body.get("network") or {}
        network_name = ""
        if isinstance(network, str):
            network_name = network.split("/")[-1]
        elif isinstance(network, dict):
            network_name = network.get("name") or network.get("selfLink") or network.get("url") or ""
            if network_name:
                network_name = network_name.split("/")[-1]
        if network_name and not self.state.networks.get(network_name):
            return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
        mirrored_resources = body.get("mirroredResources") or {}
        if isinstance(mirrored_resources, dict):
            subnetworks = mirrored_resources.get("subnetworks") or []
            for subnetwork in subnetworks:
                subnetwork_name = subnetwork
                if isinstance(subnetwork, dict):
                    subnetwork_name = subnetwork.get("subnetwork") or subnetwork.get("name") or subnetwork.get("selfLink")
                if subnetwork_name:
                    subnetwork_name = subnetwork_name.split("/")[-1]
                    if not self.state.subnetworks.get(subnetwork_name):
                        return create_gcp_error(404, f"Subnetwork {subnetwork_name!r} not found", "NOT_FOUND")
            instances = mirrored_resources.get("instances") or []
            for instance in instances:
                instance_name = instance
                if isinstance(instance, dict):
                    instance_name = instance.get("instance") or instance.get("name") or instance.get("selfLink")
                if instance_name:
                    instance_name = instance_name.split("/")[-1]
                    if not self.state.instances.get(instance_name):
                        return create_gcp_error(404, f"Instance {instance_name!r} not found", "NOT_FOUND")
        collector_ilb = body.get("collectorIlb") or {}
        collector_name = ""
        if isinstance(collector_ilb, dict):
            collector_name = (
                collector_ilb.get("forwardingRule")
                or collector_ilb.get("selfLink")
                or collector_ilb.get("url")
                or collector_ilb.get("name")
                or ""
            )
        elif isinstance(collector_ilb, str):
            collector_name = collector_ilb
        if collector_name:
            collector_name = collector_name.split("/")[-1]
            if not self.state.forwarding_rules.get(collector_name):
                return create_gcp_error(404, f"ForwardingRule {collector_name!r} not found", "NOT_FOUND")
        resource = PacketMirroring(
            name=name,
            collector_ilb=collector_ilb,
            enable=body.get("enable", ""),
            description=body.get("description", ""),
            region=region,
            creation_timestamp=datetime.now(timezone.utc).isoformat(),
            mirrored_resources=mirrored_resources,
            priority=body.get("priority", 0),
            network=network,
            filter=body.get("filter", {}),
            id=self._generate_id(),
        )
        self.resources[resource.name] = resource
        return make_operation(
            operation_type="insert",
            resource_link=f"projects/{project}/regions/{region}/packetMirrorings/{resource.name}",
            params=params,
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the specified PacketMirroring resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("packetMirroring")
        if not name:
            return create_gcp_error(400, "Required field 'packetMirroring' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        return resource.to_dict()

    def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves a list of PacketMirroring resources available to the specified
project and region."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        resources = [r for r in resources if r.region == region]
        return {
            "kind": "compute#packetmirroringList",
            "id": f"projects/{project}/regions/{region}",
            "items": [resource.to_dict() for resource in resources],
            "selfLink": "",
        }

    def aggregatedList(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves an aggregated list of packetMirrorings.

To prevent failure, Google recommends that you set the
`returnPartialSuccess` parameter to `true`."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        resources = list(self.resources.values())
        filter_expr = params.get("filter", "")
        if filter_expr:
            import re
            match = re.match(r'name\s*=\s*"?([^"\s]+)"?', filter_expr)
            if match:
                resources = [r for r in resources if r.name == match.group(1)]
        scope_key = f"zones/{params.get('zone', 'us-central1-a')}"
        items = (
            {scope_key: {"warning": {"code": "NO_RESULTS_ON_PAGE"}}}
            if not resources
            else {scope_key: {"PacketMirrorings": [r.to_dict() for r in resources]}}
        )
        return {
            "kind": "compute#packetmirroringAggregatedList",
            "id": f"projects/{project}/aggregated/PacketMirrorings",
            "items": items,
            "selfLink": "",
        }

    def patch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Patches the specified PacketMirroring resource with the data included in
the request. This method supportsPATCH
semantics and usesJSON merge
patch format and processing rules."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("packetMirroring")
        if not name:
            return create_gcp_error(400, "Required field 'packetMirroring' not specified", "INVALID_ARGUMENT")
        body = params.get("PacketMirroring")
        if not body:
            return create_gcp_error(400, "Required field 'PacketMirroring' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        if "network" in body:
            network = body.get("network") or {}
            network_name = ""
            if isinstance(network, str):
                network_name = network.split("/")[-1]
            elif isinstance(network, dict):
                network_name = network.get("name") or network.get("selfLink") or network.get("url") or ""
                if network_name:
                    network_name = network_name.split("/")[-1]
            if network_name and not self.state.networks.get(network_name):
                return create_gcp_error(404, f"Network {network_name!r} not found", "NOT_FOUND")
            resource.network = network
        if "mirroredResources" in body:
            mirrored_resources = body.get("mirroredResources") or {}
            if isinstance(mirrored_resources, dict):
                subnetworks = mirrored_resources.get("subnetworks") or []
                for subnetwork in subnetworks:
                    subnetwork_name = subnetwork
                    if isinstance(subnetwork, dict):
                        subnetwork_name = subnetwork.get("subnetwork") or subnetwork.get("name") or subnetwork.get("selfLink")
                    if subnetwork_name:
                        subnetwork_name = subnetwork_name.split("/")[-1]
                        if not self.state.subnetworks.get(subnetwork_name):
                            return create_gcp_error(404, f"Subnetwork {subnetwork_name!r} not found", "NOT_FOUND")
                instances = mirrored_resources.get("instances") or []
                for instance in instances:
                    instance_name = instance
                    if isinstance(instance, dict):
                        instance_name = instance.get("instance") or instance.get("name") or instance.get("selfLink")
                    if instance_name:
                        instance_name = instance_name.split("/")[-1]
                        if not self.state.instances.get(instance_name):
                            return create_gcp_error(404, f"Instance {instance_name!r} not found", "NOT_FOUND")
            resource.mirrored_resources = mirrored_resources
        if "collectorIlb" in body:
            collector_ilb = body.get("collectorIlb") or {}
            collector_name = ""
            if isinstance(collector_ilb, dict):
                collector_name = (
                    collector_ilb.get("forwardingRule")
                    or collector_ilb.get("selfLink")
                    or collector_ilb.get("url")
                    or collector_ilb.get("name")
                    or ""
                )
            elif isinstance(collector_ilb, str):
                collector_name = collector_ilb
            if collector_name:
                collector_name = collector_name.split("/")[-1]
                if not self.state.forwarding_rules.get(collector_name):
                    return create_gcp_error(404, f"ForwardingRule {collector_name!r} not found", "NOT_FOUND")
            resource.collector_ilb = collector_ilb
        if "enable" in body:
            resource.enable = body.get("enable") or ""
        if "description" in body:
            resource.description = body.get("description") or ""
        if "priority" in body:
            resource.priority = body.get("priority") or 0
        if "filter" in body:
            resource.filter = body.get("filter") or {}
        return make_operation(
            operation_type="patch",
            resource_link=f"projects/{project}/regions/{region}/packetMirrorings/{resource.name}",
            params=params,
        )

    def testIamPermissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Returns permissions that a caller has on the specified resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("resource")
        if not name:
            return create_gcp_error(400, "Required field 'resource' not specified", "INVALID_ARGUMENT")
        body = params.get("TestPermissionsRequest")
        if not body:
            return create_gcp_error(400, "Required field 'TestPermissionsRequest' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        permissions = body.get("permissions") or []
        return {
            "permissions": list(permissions),
        }

    def delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deletes the specified PacketMirroring resource."""
        project = params.get("project")
        if not project:
            return create_gcp_error(400, "Required field 'project' not specified", "INVALID_ARGUMENT")
        region = params.get("region")
        if not region:
            return create_gcp_error(400, "Required field 'region' not specified", "INVALID_ARGUMENT")
        name = params.get("packetMirroring")
        if not name:
            return create_gcp_error(400, "Required field 'packetMirroring' not specified", "INVALID_ARGUMENT")
        resource = self.resources.get(name)
        if not resource or (resource.region and resource.region != region):
            return create_gcp_error(404, f"The resource {name!r} was not found", "NOT_FOUND")
        del self.resources[name]
        return make_operation(
            operation_type="delete",
            resource_link=f"projects/{project}/regions/{region}/packetMirrorings/{name}",
            params=params,
        )


class packet_mirroring_RequestParser:
    @staticmethod
    def parse_request(
        method_name: str,
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge path, query, and body params into a flat dict for the backend."""
        parsers = {
            'insert': packet_mirroring_RequestParser._parse_insert,
            'list': packet_mirroring_RequestParser._parse_list,
            'delete': packet_mirroring_RequestParser._parse_delete,
            'get': packet_mirroring_RequestParser._parse_get,
            'patch': packet_mirroring_RequestParser._parse_patch,
            'aggregatedList': packet_mirroring_RequestParser._parse_aggregatedList,
            'testIamPermissions': packet_mirroring_RequestParser._parse_testIamPermissions,
        }
        parser = parsers.get(method_name)
        if parser is None:
            raise ValueError(f"Unknown method: {method_name}")
        return parser(path_params, query_params, body)

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
        params['PacketMirroring'] = body.get('PacketMirroring')
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
    def _parse_patch(
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
        params['PacketMirroring'] = body.get('PacketMirroring')
        return params

    @staticmethod
    def _parse_aggregatedList(
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
        if 'includeAllScopes' in query_params:
            params['includeAllScopes'] = query_params['includeAllScopes']
        if 'maxResults' in query_params:
            params['maxResults'] = query_params['maxResults']
        if 'orderBy' in query_params:
            params['orderBy'] = query_params['orderBy']
        if 'pageToken' in query_params:
            params['pageToken'] = query_params['pageToken']
        if 'returnPartialSuccess' in query_params:
            params['returnPartialSuccess'] = query_params['returnPartialSuccess']
        if 'serviceProjectNumber' in query_params:
            params['serviceProjectNumber'] = query_params['serviceProjectNumber']
        return params

    @staticmethod
    def _parse_testIamPermissions(
        path_params: Dict[str, Any],
        query_params: Dict[str, Any],
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        # Path params
        params.update(path_params)
        # Query params
        params.update(query_params)
        # Body params
        params['TestPermissionsRequest'] = body.get('TestPermissionsRequest')
        return params


class packet_mirroring_ResponseSerializer:
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
            'insert': packet_mirroring_ResponseSerializer._serialize_insert,
            'list': packet_mirroring_ResponseSerializer._serialize_list,
            'delete': packet_mirroring_ResponseSerializer._serialize_delete,
            'get': packet_mirroring_ResponseSerializer._serialize_get,
            'patch': packet_mirroring_ResponseSerializer._serialize_patch,
            'aggregatedList': packet_mirroring_ResponseSerializer._serialize_aggregatedList,
            'testIamPermissions': packet_mirroring_ResponseSerializer._serialize_testIamPermissions,
        }
        fn = serializers.get(method_name)
        if fn is None:
            return _json.dumps(data)
        return fn(data)

    @staticmethod
    def _serialize_insert(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_list(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_delete(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_get(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_patch(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_aggregatedList(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

    @staticmethod
    def _serialize_testIamPermissions(data: Dict[str, Any]) -> str:
        return _json.dumps(data)

