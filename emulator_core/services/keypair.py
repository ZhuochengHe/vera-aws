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
class KeyPair:
    create_time: str = ""
    key_fingerprint: str = ""
    key_name: str = ""
    key_pair_id: str = ""
    key_type: str = ""
    public_key: str = ""
    tag_set: List[Any] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
        return {
            "createTime": self.create_time,
            "keyFingerprint": self.key_fingerprint,
            "keyName": self.key_name,
            "keyPairId": self.key_pair_id,
            "keyType": self.key_type,
            "publicKey": self.public_key,
            "tagSet": self.tag_set,
        }

class KeyPair_Backend:
    def __init__(self):
        self.state = EC2State.get()
        self.resources = self.state.key_pairs  # alias to shared store

    def _require_params(self, params: Dict[str, Any], required: List[str]):
        for name in required:
            if not params.get(name):
                return create_error_response("MissingParameter", f"Missing required parameter: {name}")
        return None

    def _extract_tags(self, tag_specs: List[Dict[str, Any]], resource_type: str = "key-pair") -> List[Dict[str, Any]]:
        tags: List[Dict[str, Any]] = []
        for spec in tag_specs or []:
            spec_type = spec.get("ResourceType")
            if spec_type and spec_type != resource_type:
                continue
            for tag in spec.get("Tag") or spec.get("Tags") or []:
                if tag:
                    tags.append(tag)
        return tags

    def _find_keypair(self, key_pair_id: Optional[str] = None, key_name: Optional[str] = None) -> Optional[KeyPair]:
        if key_pair_id:
            return self.resources.get(key_pair_id)
        if key_name:
            for keypair in self.resources.values():
                if keypair.key_name == key_name:
                    return keypair
        return None

    def CreateKeyPair(self, params: Dict[str, Any]):
        """Creates an ED25519 or 2048-bit RSA key pair with the specified name and in the
            specified format. Amazon EC2 stores the public key and displays the private
            key for you to save to a file. The private key is returned as an unencrypted PEM encoded
            PKCS#1 private key o"""

        error = self._require_params(params, ["KeyName"])
        if error:
            return error

        key_name = params.get("KeyName")
        existing = self._find_keypair(key_name=key_name)
        if existing:
            return create_error_response("InvalidKeyPair.Duplicate", f"Key pair '{key_name}' already exists.")

        key_pair_id = self._generate_id("key")
        key_type = params.get("KeyType") or "rsa"
        key_fingerprint = uuid.uuid4().hex
        key_material = f"private-key-{uuid.uuid4().hex}"
        create_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        tag_set = self._extract_tags(params.get("TagSpecification.N", []))

        resource = KeyPair(
            create_time=create_time,
            key_fingerprint=key_fingerprint,
            key_name=key_name,
            key_pair_id=key_pair_id,
            key_type=key_type,
            public_key="",
            tag_set=tag_set,
        )
        self.resources[key_pair_id] = resource

        return {
            'keyFingerprint': key_fingerprint,
            'keyMaterial': key_material,
            'keyName': key_name,
            'keyPairId': key_pair_id,
            'tagSet': tag_set,
            }

    def DeleteKeyPair(self, params: Dict[str, Any]):
        """Deletes the specified key pair, by removing the public key from Amazon EC2."""

        key_pair_id = params.get("KeyPairId")
        key_name = params.get("KeyName")

        if not key_pair_id and not key_name:
            return create_error_response("MissingParameter", "Missing required parameter: KeyName")

        keypair = self._find_keypair(key_pair_id=key_pair_id, key_name=key_name)
        if not keypair:
            missing_id = key_pair_id or key_name
            return create_error_response("InvalidKeyPair.NotFound", f"The ID '{missing_id}' does not exist")

        self.resources.pop(keypair.key_pair_id, None)

        return {
            'keyPairId': keypair.key_pair_id,
            'return': True,
            }

    def DescribeKeyPairs(self, params: Dict[str, Any]):
        """Describes the specified key pairs or all of your key pairs. For more information about key pairs, seeAmazon EC2 key pairsin theAmazon EC2 User Guide."""

        key_pair_ids = params.get("KeyPairId.N", []) or []
        key_names = params.get("KeyName.N", []) or []

        resources: List[KeyPair] = []
        if key_pair_ids or key_names:
            seen_ids = set()
            for key_pair_id in key_pair_ids:
                keypair = self.resources.get(key_pair_id)
                if not keypair:
                    return create_error_response("InvalidKeyPair.NotFound", f"The ID '{key_pair_id}' does not exist")
                if keypair.key_pair_id not in seen_ids:
                    resources.append(keypair)
                    seen_ids.add(keypair.key_pair_id)
            for key_name in key_names:
                keypair = self._find_keypair(key_name=key_name)
                if not keypair:
                    return create_error_response("InvalidKeyPair.NotFound", f"The ID '{key_name}' does not exist")
                if keypair.key_pair_id not in seen_ids:
                    resources.append(keypair)
                    seen_ids.add(keypair.key_pair_id)
        else:
            resources = list(self.resources.values())

        resources = apply_filters(resources, params.get("Filter.N", []))

        include_public_key = str2bool(params.get("IncludePublicKey"))
        key_set = []
        for keypair in resources:
            data = keypair.to_dict()
            if not include_public_key:
                data["publicKey"] = None
            key_set.append(data)

        return {
            'keySet': key_set,
            }

    def ImportKeyPair(self, params: Dict[str, Any]):
        """Imports the public key from an RSA or ED25519 key pair that you created using a third-party tool. 
        You give AWS only the public key. The private key is never transferred between you and AWS. For more information about the requirements for importing a key pair, seeCreate a key pair and import"""

        error = self._require_params(params, ["KeyName", "PublicKeyMaterial"])
        if error:
            return error

        key_name = params.get("KeyName")
        existing = self._find_keypair(key_name=key_name)
        if existing:
            return create_error_response("InvalidKeyPair.Duplicate", f"Key pair '{key_name}' already exists.")

        key_pair_id = self._generate_id("key")
        public_key = params.get("PublicKeyMaterial")
        key_fingerprint = uuid.uuid4().hex
        create_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        tag_set = self._extract_tags(params.get("TagSpecification.N", []))

        resource = KeyPair(
            create_time=create_time,
            key_fingerprint=key_fingerprint,
            key_name=key_name,
            key_pair_id=key_pair_id,
            key_type="",
            public_key=public_key,
            tag_set=tag_set,
        )
        self.resources[key_pair_id] = resource

        return {
            'keyFingerprint': key_fingerprint,
            'keyName': key_name,
            'keyPairId': key_pair_id,
            'tagSet': tag_set,
            }

    def _generate_id(self, prefix: str = 'key') -> str:
        return f'{prefix}-{uuid.uuid4().hex[:17]}'

from typing import Dict, List, Any, Optional
from ..utils import get_scalar, get_int, get_indexed_list, parse_filters, parse_tags, str2bool, esc
from ..utils import is_error_response, serialize_error_response

class keypair_RequestParser:
    @staticmethod
    def parse_create_key_pair_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "KeyFormat": get_scalar(md, "KeyFormat"),
            "KeyName": get_scalar(md, "KeyName"),
            "KeyType": get_scalar(md, "KeyType"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_delete_key_pair_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "KeyName": get_scalar(md, "KeyName"),
            "KeyPairId": get_scalar(md, "KeyPairId"),
        }

    @staticmethod
    def parse_describe_key_pairs_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "Filter.N": parse_filters(md, "Filter"),
            "IncludePublicKey": get_scalar(md, "IncludePublicKey"),
            "KeyName.N": get_indexed_list(md, "KeyName"),
            "KeyPairId.N": get_indexed_list(md, "KeyPairId"),
        }

    @staticmethod
    def parse_import_key_pair_request(md: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "DryRun": str2bool(get_scalar(md, "DryRun")),
            "KeyName": get_scalar(md, "KeyName"),
            "PublicKeyMaterial": get_scalar(md, "PublicKeyMaterial"),
            "TagSpecification.N": parse_tags(md, "TagSpecification"),
        }

    @staticmethod
    def parse_request(action: str, md: Dict[str, Any]) -> Dict[str, Any]:
        parsers = {
            "CreateKeyPair": keypair_RequestParser.parse_create_key_pair_request,
            "DeleteKeyPair": keypair_RequestParser.parse_delete_key_pair_request,
            "DescribeKeyPairs": keypair_RequestParser.parse_describe_key_pairs_request,
            "ImportKeyPair": keypair_RequestParser.parse_import_key_pair_request,
        }
        if action not in parsers:
            raise ValueError(f"Unknown action: {action}")
        return parsers[action](md)

class keypair_ResponseSerializer:
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
                xml_parts.extend(keypair_ResponseSerializer._serialize_dict_to_xml(value, key, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.extend(keypair_ResponseSerializer._serialize_list_to_xml(value, key, indent_level))
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
                xml_parts.extend(keypair_ResponseSerializer._serialize_dict_to_xml(item, 'item', indent_level + 2))
                xml_parts.append(f'{indent}    </item>')
            elif isinstance(item, list):
                xml_parts.extend(keypair_ResponseSerializer._serialize_list_to_xml(item, tag_name, indent_level + 1))
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
                xml_parts.extend(keypair_ResponseSerializer._serialize_nested_fields(value, indent_level + 1))
                xml_parts.append(f'{indent}</{key}>')
            elif isinstance(value, list):
                xml_parts.append(f'{indent}<{key}>')
                for item in value:
                    if isinstance(item, dict):
                        xml_parts.append(f'{indent}    <item>')
                        xml_parts.extend(keypair_ResponseSerializer._serialize_nested_fields(item, indent_level + 2))
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
    def serialize_create_key_pair_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<CreateKeyPairResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize keyFingerprint
        _keyFingerprint_key = None
        if "keyFingerprint" in data:
            _keyFingerprint_key = "keyFingerprint"
        elif "KeyFingerprint" in data:
            _keyFingerprint_key = "KeyFingerprint"
        if _keyFingerprint_key:
            param_data = data[_keyFingerprint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyFingerprint>{esc(str(param_data))}</keyFingerprint>')
        # Serialize keyMaterial
        _keyMaterial_key = None
        if "keyMaterial" in data:
            _keyMaterial_key = "keyMaterial"
        elif "KeyMaterial" in data:
            _keyMaterial_key = "KeyMaterial"
        if _keyMaterial_key:
            param_data = data[_keyMaterial_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyMaterial>{esc(str(param_data))}</keyMaterial>')
        # Serialize keyName
        _keyName_key = None
        if "keyName" in data:
            _keyName_key = "keyName"
        elif "KeyName" in data:
            _keyName_key = "KeyName"
        if _keyName_key:
            param_data = data[_keyName_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyName>{esc(str(param_data))}</keyName>')
        # Serialize keyPairId
        _keyPairId_key = None
        if "keyPairId" in data:
            _keyPairId_key = "keyPairId"
        elif "KeyPairId" in data:
            _keyPairId_key = "KeyPairId"
        if _keyPairId_key:
            param_data = data[_keyPairId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyPairId>{esc(str(param_data))}</keyPairId>')
        # Serialize tagSet
        _tagSet_key = None
        if "tagSet" in data:
            _tagSet_key = "tagSet"
        elif "TagSet" in data:
            _tagSet_key = "TagSet"
        elif "Tags" in data:
            _tagSet_key = "Tags"
        if _tagSet_key:
            param_data = data[_tagSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<tagSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(keypair_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        xml_parts.append(f'</CreateKeyPairResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_delete_key_pair_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DeleteKeyPairResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize keyPairId
        _keyPairId_key = None
        if "keyPairId" in data:
            _keyPairId_key = "keyPairId"
        elif "KeyPairId" in data:
            _keyPairId_key = "KeyPairId"
        if _keyPairId_key:
            param_data = data[_keyPairId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyPairId>{esc(str(param_data))}</keyPairId>')
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
        xml_parts.append(f'</DeleteKeyPairResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_describe_key_pairs_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<DescribeKeyPairsResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize keySet
        _keySet_key = None
        if "keySet" in data:
            _keySet_key = "keySet"
        elif "KeySet" in data:
            _keySet_key = "KeySet"
        elif "Keys" in data:
            _keySet_key = "Keys"
        if _keySet_key:
            param_data = data[_keySet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<keySet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(keypair_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</keySet>')
            else:
                xml_parts.append(f'{indent_str}<keySet/>')
        xml_parts.append(f'</DescribeKeyPairsResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize_import_key_pair_response(data: Dict[str, Any], request_id: str) -> str:
        xml_parts = []
        xml_parts.append(f'<ImportKeyPairResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">')
        xml_parts.append(f'    <requestId>{esc(request_id)}</requestId>')
        # Serialize keyFingerprint
        _keyFingerprint_key = None
        if "keyFingerprint" in data:
            _keyFingerprint_key = "keyFingerprint"
        elif "KeyFingerprint" in data:
            _keyFingerprint_key = "KeyFingerprint"
        if _keyFingerprint_key:
            param_data = data[_keyFingerprint_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyFingerprint>{esc(str(param_data))}</keyFingerprint>')
        # Serialize keyName
        _keyName_key = None
        if "keyName" in data:
            _keyName_key = "keyName"
        elif "KeyName" in data:
            _keyName_key = "KeyName"
        if _keyName_key:
            param_data = data[_keyName_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyName>{esc(str(param_data))}</keyName>')
        # Serialize keyPairId
        _keyPairId_key = None
        if "keyPairId" in data:
            _keyPairId_key = "keyPairId"
        elif "KeyPairId" in data:
            _keyPairId_key = "KeyPairId"
        if _keyPairId_key:
            param_data = data[_keyPairId_key]
            indent_str = "    " * 1
            xml_parts.append(f'{indent_str}<keyPairId>{esc(str(param_data))}</keyPairId>')
        # Serialize tagSet
        _tagSet_key = None
        if "tagSet" in data:
            _tagSet_key = "tagSet"
        elif "TagSet" in data:
            _tagSet_key = "TagSet"
        elif "Tags" in data:
            _tagSet_key = "Tags"
        if _tagSet_key:
            param_data = data[_tagSet_key]
            indent_str = "    " * 1
            if param_data:
                xml_parts.append(f'{indent_str}<tagSet>')
                for item in param_data:
                    xml_parts.append(f'{indent_str}    <item>')
                    xml_parts.extend(keypair_ResponseSerializer._serialize_nested_fields(item, 2))
                    xml_parts.append(f'{indent_str}    </item>')
                xml_parts.append(f'{indent_str}</tagSet>')
            else:
                xml_parts.append(f'{indent_str}<tagSet/>')
        xml_parts.append(f'</ImportKeyPairResponse>')
        return "\n".join(xml_parts)

    @staticmethod
    def serialize(action: str, data: Dict[str, Any], request_id: str) -> str:
        # Check for error response from backend
        if is_error_response(data):
            return serialize_error_response(data, request_id)
        
        serializers = {
            "CreateKeyPair": keypair_ResponseSerializer.serialize_create_key_pair_response,
            "DeleteKeyPair": keypair_ResponseSerializer.serialize_delete_key_pair_response,
            "DescribeKeyPairs": keypair_ResponseSerializer.serialize_describe_key_pairs_response,
            "ImportKeyPair": keypair_ResponseSerializer.serialize_import_key_pair_response,
        }
        if action not in serializers:
            raise ValueError(f"Unknown action: {action}")
        return serializers[action](data, request_id)

