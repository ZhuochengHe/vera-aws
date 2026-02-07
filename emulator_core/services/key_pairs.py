from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import base64
import hashlib
import re

from emulator_core.backend import BaseBackend
from emulator_core.state import ResourceState, ErrorCode


@dataclass
class Tag:
    Key: str
    Value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"Key": self.Key, "Value": self.Value}


@dataclass
class KeyPair:
    key_pair_id: str
    key_name: str
    key_type: str  # "rsa" or "ed25519"
    key_format: str  # "pem" or "ppk"
    key_material: str  # private key material (PEM or PPK)
    key_fingerprint: str
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self, include_private: bool = False) -> Dict[str, Any]:
        # keyMaterial is private key material, only included on create/import
        d = {
            "keyPairId": self.key_pair_id,
            "keyName": self.key_name,
            "keyFingerprint": self.key_fingerprint,
            "tagSet": [Tag(k, v).to_dict() for k, v in self.tags.items()],
        }
        if include_private:
            d["keyMaterial"] = self.key_material
        return d


class KeyPairsBackend(BaseBackend):
    VALID_KEY_TYPES = {"rsa", "ed25519"}
    VALID_KEY_FORMATS = {"pem", "ppk"}
    MAX_KEY_NAME_LENGTH = 255
    TAG_KEY_RE = re.compile(r"^(?!aws:).{1,127}$", re.IGNORECASE)  # tag keys may not begin with aws:

    def __init__(self, state):
        super().__init__(state)
        # Use self.state.key_pairs dict for storage

    def _validate_tags(self, tag_specifications: Optional[List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Validate and extract tags from TagSpecification.N structure.
        Only tags with ResourceType == "key-pair" are allowed.
        Returns dict of tags.
        """
        tags: Dict[str, str] = {}
        if not tag_specifications:
            return tags

        if not isinstance(tag_specifications, list):
            raise ErrorCode("InvalidParameterValue", "TagSpecification must be a list")

        for tag_spec in tag_specifications:
            if not isinstance(tag_spec, dict):
                raise ErrorCode("InvalidParameterValue", "Each TagSpecification must be a dict")
            resource_type = tag_spec.get("ResourceType")
            if resource_type != "key-pair":
                # According to AWS docs, only key-pair resource type is valid here
                raise ErrorCode("InvalidParameterValue", f"Invalid ResourceType in TagSpecification: {resource_type}")

            tag_list = tag_spec.get("Tags", [])
            if not isinstance(tag_list, list):
                raise ErrorCode("InvalidParameterValue", "Tags must be a list")

            for tag in tag_list:
                if not isinstance(tag, dict):
                    raise ErrorCode("InvalidParameterValue", "Each Tag must be a dict")
                key = tag.get("Key")
                value = tag.get("Value", "")
                if key is None:
                    raise ErrorCode("InvalidParameterValue", "Tag Key is required")
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ErrorCode("InvalidParameterValue", "Tag Key and Value must be strings")
                if not self.TAG_KEY_RE.match(key):
                    raise ErrorCode("InvalidParameterValue", f"Invalid tag key: {key}")
                if len(key) > 127:
                    raise ErrorCode("InvalidParameterValue", f"Tag key too long: {key}")
                if len(value) > 256:
                    raise ErrorCode("InvalidParameterValue", f"Tag value too long for key: {key}")
                tags[key] = value
        return tags

    def _generate_rsa_keypair(self, key_format: str) -> (str, str):
        """
        Generate a dummy RSA private key and fingerprint.
        key_format: "pem" or "ppk"
        Returns (private_key_material, fingerprint)
        """
        # For emulation, generate dummy key material and fingerprint
        # Private key material is a PEM or PPK formatted string (dummy)
        # Fingerprint is SHA-1 digest of DER encoded private key (dummy here)
        dummy_private_key_pem = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIICWwIBAAKBgQC7v+dummykeymaterialdummykeymaterialdummykeymaterial\n"
            "dummykeymaterialdummykeymaterialdummykeymaterialdummykeymaterial\n"
            "-----END RSA PRIVATE KEY-----"
        )
        dummy_private_key_ppk = (
            "PuTTY-User-Key-File-2: ssh-rsa\n"
            "Encryption: none\n"
            "Comment: imported-openssh-key\n"
            "Public-Lines: 4\n"
            "AAAAB3NzaC1yc2EAAAABIwAAAQEArandompublickeydata\n"
            "Private-Lines: 8\n"
            "dummyppkprivatekeymaterialdummyppkprivatekeymaterial\n"
            "Private-MAC: dummy-mac\n"
        )
        if key_format == "pem":
            private_key = dummy_private_key_pem
            # Fingerprint: SHA-1 digest of DER encoded private key (simulate)
            fingerprint_bytes = hashlib.sha1(private_key.encode("utf-8")).digest()
            fingerprint = ":".join(f"{b:02x}" for b in fingerprint_bytes)
        else:  # ppk
            private_key = dummy_private_key_ppk
            # Fingerprint: same as above for dummy
            fingerprint_bytes = hashlib.sha1(private_key.encode("utf-8")).digest()
            fingerprint = ":".join(f"{b:02x}" for b in fingerprint_bytes)
        return private_key, fingerprint

    def _generate_ed25519_keypair(self, key_format: str) -> (str, str):
        """
        Generate a dummy ED25519 private key and fingerprint.
        key_format: "pem" or "ppk"
        Returns (private_key_material, fingerprint)
        """
        # For emulation, generate dummy key material and fingerprint
        dummy_private_key_pem = (
            "-----BEGIN OPENSSH PRIVATE KEY-----\n"
            "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtz\n"
            "c2gtZWQyNTUxOQAAACBdummykeymaterialdummykeymaterialdummykeymaterial\n"
            "dummykeymaterialdummykeymaterialdummykeymaterialdummykeymaterial\n"
            "-----END OPENSSH PRIVATE KEY-----"
        )
        dummy_private_key_ppk = (
            "PuTTY-User-Key-File-2: ssh-ed25519\n"
            "Encryption: none\n"
            "Comment: imported-openssh-key\n"
            "Public-Lines: 4\n"
            "AAAAC3NzaC1lZDI1NTE5AAAAIdummypublickeydata\n"
            "Private-Lines: 8\n"
            "dummyppkprivatekeymaterialdummyppkprivatekeymaterial\n"
            "Private-MAC: dummy-mac\n"
        )
        if key_format == "pem":
            private_key = dummy_private_key_pem
            # Fingerprint: base64-encoded SHA-256 digest of public key (simulate)
            sha256_digest = hashlib.sha256(private_key.encode("utf-8")).digest()
            fingerprint = base64.b64encode(sha256_digest).decode("utf-8")
        else:  # ppk
            private_key = dummy_private_key_ppk
            sha256_digest = hashlib.sha256(private_key.encode("utf-8")).digest()
            fingerprint = base64.b64encode(sha256_digest).decode("utf-8")
        return private_key, fingerprint

    def _validate_key_name(self, key_name: Any) -> str:
        if not isinstance(key_name, str):
            raise ErrorCode("InvalidParameterValue", "KeyName must be a string")
        if len(key_name) == 0 or len(key_name) > self.MAX_KEY_NAME_LENGTH:
            raise ErrorCode("InvalidParameterValue", f"KeyName length must be 1 to {self.MAX_KEY_NAME_LENGTH} characters")
        # AWS allows ASCII characters, but we do not enforce strict ASCII here
        # Could add stricter validation if needed
        return key_name

    def _check_key_name_unique(self, key_name: str) -> None:
        for kp in self.state.key_pairs.values():
            if kp.key_name == key_name:
                raise ErrorCode("InvalidKeyPair.Duplicate", f"Key pair '{key_name}' already exists")

    def _get_keypair_by_name(self, key_name: str) -> Optional[KeyPair]:
        for kp in self.state.key_pairs.values():
            if kp.key_name == key_name:
                return kp
        return None

    def _get_keypair_by_id(self, key_pair_id: str) -> Optional[KeyPair]:
        return self.state.key_pairs.get(key_pair_id)

    def _parse_tag_specifications(self, params: Dict[str, Any]) -> Dict[str, str]:
        # TagSpecification.N is a list of dicts
        # The param keys are like "TagSpecification.N" where N is 1-based index
        # The caller should pass TagSpecification.N as a list of dicts
        # We expect params["TagSpecification.N"] to be a list of dicts or a dict
        # But from the resource JSON, TagSpecification.N is an array of TagSpecification objects
        # So we expect params to have key "TagSpecification" with list of dicts
        # But the resource JSON shows "TagSpecification.N" so we must collect all keys starting with "TagSpecification."
        # For simplicity, assume caller passes "TagSpecification" as list of dicts
        # If not present, return empty dict
        tag_specifications = params.get("TagSpecification") or params.get("TagSpecifications") or params.get("TagSpecification.N")
        if tag_specifications is None:
            # Also check for keys like TagSpecification.1, TagSpecification.2 etc
            tag_specifications = []
            for key in params:
                if key.startswith("TagSpecification."):
                    val = params[key]
                    if isinstance(val, list):
                        tag_specifications.extend(val)
                    elif isinstance(val, dict):
                        tag_specifications.append(val)
            if not tag_specifications:
                return {}
        if not isinstance(tag_specifications, list):
            tag_specifications = [tag_specifications]
        return self._validate_tags(tag_specifications)

    def _validate_dry_run(self, params: Dict[str, Any]) -> None:
        dry_run = params.get("DryRun")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise ErrorCode("InvalidParameterValue", "DryRun must be a boolean")
            if dry_run:
                # For emulation, assume user has permission
                raise ErrorCode("DryRunOperation", "Request would have succeeded, but DryRun flag is set")

    def create_key_pair(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        CreateKeyPair API
        """
        self._validate_dry_run(params)

        key_name = params.get("KeyName")
        if key_name is None:
            raise ErrorCode("MissingParameter", "KeyName is required")
        key_name = self._validate_key_name(key_name)
        self._check_key_name_unique(key_name)

        key_format = params.get("KeyFormat", "pem")
        if not isinstance(key_format, str):
            raise ErrorCode("InvalidParameterValue", "KeyFormat must be a string")
        key_format = key_format.lower()
        if key_format not in self.VALID_KEY_FORMATS:
            raise ErrorCode("InvalidParameterValue", f"Invalid KeyFormat: {key_format}")

        key_type = params.get("KeyType", "rsa")
        if not isinstance(key_type, str):
            raise ErrorCode("InvalidParameterValue", "KeyType must be a string")
        key_type = key_type.lower()
        if key_type not in self.VALID_KEY_TYPES:
            raise ErrorCode("InvalidParameterValue", f"Invalid KeyType: {key_type}")

        # Validate tags
        tags = self._parse_tag_specifications(params)

        # Generate key material and fingerprint
        if key_type == "rsa":
            private_key, fingerprint = self._generate_rsa_keypair(key_format)
        else:  # ed25519
            private_key, fingerprint = self._generate_ed25519_keypair(key_format)

        key_pair_id = f"key-{self.generate_unique_id()}"

        key_pair = KeyPair(
            key_pair_id=key_pair_id,
            key_name=key_name,
            key_type=key_type,
            key_format=key_format,
            key_material=private_key,
            key_fingerprint=fingerprint,
            tags=tags,
        )

        self.state.key_pairs[key_pair_id] = key_pair

        response = {
            "requestId": self.generate_request_id(),
            "keyName": key_pair.key_name,
            "keyPairId": key_pair.key_pair_id,
            "keyFingerprint": key_pair.key_fingerprint,
            "keyMaterial": key_pair.key_material,
            "tagSet": [Tag(k, v).to_dict() for k, v in key_pair.tags.items()],
        }
        return response

    def delete_key_pair(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        DeleteKeyPair API
        """
        self._validate_dry_run(params)

        key_name = params.get("KeyName")
        key_pair_id = params.get("KeyPairId")

        if key_name is None and key_pair_id is None:
            raise ErrorCode("MissingParameter", "Either KeyName or KeyPairId must be specified")

        key_pair: Optional[KeyPair] = None
        if key_pair_id is not None:
            if not isinstance(key_pair_id, str):
                raise Exception("InvalidParameterValue: KeyPairId must be a string")
            key_pair = self._get_keypair_by_id(key_pair_id)
        else:
            if not isinstance(key_name, str):
                raise Exception("InvalidParameterValue: KeyName must be a string")
            key_pair = self._get_keypair_by_name(key_name)

        # Delete key pair if found (idempotent delete - return success even if not found)
        key_pair_id_result = None
        if key_pair is not None:
            key_pair_id_result = key_pair.key_pair_id
            del self.state.key_pairs[key_pair.key_pair_id]

        response = {
            "requestId": self.generate_request_id(),
            "keyPairId": key_pair_id_result,
            "return": True,
        }
        return response

    def describe_key_pairs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        DescribeKeyPairs API
        """
        self._validate_dry_run(params)

        # Filters:
        # KeyName.N: list of key names
        # KeyPairId.N: list of key pair ids
        # Filter.N: list of filters with Name and Values
        # IncludePublicKey: bool (include public key material in response)
        # We must support filtering by:
        # - key-pair-id
        # - fingerprint
        # - key-name
        # - tag-key
        # - tag:<key>

        include_public_key = params.get("IncludePublicKey", False)
        if include_public_key is not None and not isinstance(include_public_key, bool):
            raise ErrorCode("InvalidParameterValue", "IncludePublicKey must be a boolean")

        # Collect key names from KeyName.N or KeyName
        key_names: List[str] = []
        for k, v in params.items():
            if k.startswith("KeyName"):
                if isinstance(v, list):
                    key_names.extend(v)
                elif isinstance(v, str):
                    key_names.append(v)
        # Collect key pair ids from KeyPairId.N or KeyPairId
        key_pair_ids: List[str] = []
        for k, v in params.items():
            if k.startswith("KeyPairId"):
                if isinstance(v, list):
                    key_pair_ids.extend(v)
                elif isinstance(v, str):
                    key_pair_ids.append(v)

        # Collect filters
        filters: List[Dict[str, Any]] = []
        for k, v in params.items():
            if k.startswith("Filter"):
                # Expect v to be dict with Name and Values
                if isinstance(v, dict):
                    filters.append(v)
                elif isinstance(v, list):
                    filters.extend(v)

        # Start with all key pairs
        key_pairs = list(self.state.key_pairs.values())

        # Filter by key names if specified
        if key_names:
            key_names_set = set(key_names)
            key_pairs = [kp for kp in key_pairs if kp.key_name in key_names_set]

        # Filter by key pair ids if specified
        if key_pair_ids:
            key_pair_ids_set = set(key_pair_ids)
            key_pairs = [kp for kp in key_pairs if kp.key_pair_id in key_pair_ids_set]

        # Apply filters
        for f in filters:
            name = f.get("Name")
            values = f.get("Values", [])
            if not name or not isinstance(values, list):
                continue
            name = name.lower()
            values_set = set(values)
            if name == "key-pair-id":
                key_pairs = [kp for kp in key_pairs if kp.key_pair_id in values_set]
            elif name == "fingerprint":
                key_pairs = [kp for kp in key_pairs if kp.key_fingerprint in values_set]
            elif name == "key-name":
                key_pairs = [kp for kp in key_pairs if kp.key_name in values_set]
            elif name == "tag-key":
                key_pairs = [kp for kp in key_pairs if any(k in values_set for k in kp.tags.keys())]
            elif name.startswith("tag:"):
                tag_key = name[4:]
                key_pairs = [kp for kp in key_pairs if kp.tags.get(tag_key) in values_set]

        # Build response keySet
        key_set = []
        for kp in key_pairs:
            d = {
                "keyPairId": kp.key_pair_id,
                "keyName": kp.key_name,
                "keyFingerprint": kp.key_fingerprint,
                "keyType": kp.key_type,
                "tagSet": [Tag(k, v).to_dict() for k, v in kp.tags.items()],
            }
            if include_public_key:
                # Public key material is not stored separately, but for emulation we can provide dummy
                # For RSA, public key is not stored, so provide dummy string
                if kp.key_type == "rsa":
                    d["publicKey"] = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArandompublickeydata"
                else:
                    d["publicKey"] = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIdummypublickeydata"
            key_set.append(d)

        return {
            "requestId": self.generate_request_id(),
            "keySet": key_set
        }

    def import_key_pair(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        ImportKeyPair API - LocalStack compatible behavior.

        LocalStack pattern: Import an existing public key material.
        The fingerprint is computed from the public key.
        """
        self._validate_dry_run(params)

        key_name = params.get("KeyName")
        if key_name is None:
            raise ErrorCode("MissingParameter", "KeyName is required")
        key_name = self._validate_key_name(key_name)
        self._check_key_name_unique(key_name)

        public_key_material = params.get("PublicKeyMaterial")
        if public_key_material is None:
            raise ErrorCode("MissingParameter", "PublicKeyMaterial is required")

        # Decode base64 if needed (AWS expects base64-encoded public key)
        if isinstance(public_key_material, str):
            try:
                # Try to decode if it looks like base64
                decoded = base64.b64decode(public_key_material)
                public_key_material = decoded.decode("utf-8", errors="ignore")
            except Exception:
                # If not base64, use as-is
                pass

        # Validate tags
        tags = self._parse_tag_specifications(params)

        # Determine key type from public key material
        if "ssh-ed25519" in public_key_material:
            key_type = "ed25519"
        else:
            key_type = "rsa"

        # Compute fingerprint from public key (MD5 for RSA, SHA256 for ED25519)
        if key_type == "rsa":
            # RSA fingerprint: MD5 hash of DER-encoded public key, colon-separated
            fingerprint_bytes = hashlib.md5(public_key_material.encode("utf-8")).digest()
            fingerprint = ":".join(f"{b:02x}" for b in fingerprint_bytes)
        else:
            # ED25519 fingerprint: SHA256 hash, base64-encoded
            sha256_digest = hashlib.sha256(public_key_material.encode("utf-8")).digest()
            fingerprint = base64.b64encode(sha256_digest).decode("utf-8")

        key_pair_id = f"key-{self.generate_unique_id()}"

        key_pair = KeyPair(
            key_pair_id=key_pair_id,
            key_name=key_name,
            key_type=key_type,
            key_format="pem",  # Imported keys don't have private material
            key_material="",   # No private key for imported keys
            key_fingerprint=fingerprint,
            tags=tags,
        )

        self.state.key_pairs[key_pair_id] = key_pair

        response = {
            "requestId": self.generate_request_id(),
            "keyName": key_pair.key_name,
            "keyPairId": key_pair.key_pair_id,
            "keyFingerprint": key_pair.key_fingerprint,
            "tagSet": [Tag(k, v).to_dict() for k, v in key_pair.tags.items()],
        }
        return response

from emulator_core.gateway.base import BaseGateway

class KeyPairsGateway(BaseGateway):
    def __init__(self, backend):
        super().__init__(backend)
        self.register_action("CreateKeyPair", self.create_key_pair)
        self.register_action("DeleteKeyPair", self.delete_key_pair)
        self.register_action("DescribeKeyPairs", self.describe_key_pairs)
        self.register_action("ImportKeyPair", self.import_key_pair)

    def create_key_pair(self, params):
        return self.backend.create_key_pair(params)

    def delete_key_pair(self, params):
        return self.backend.delete_key_pair(params)

    def describe_key_pairs(self, params):
        return self.backend.describe_key_pairs(params)

    def import_key_pair(self, params):
        return self.backend.import_key_pair(params)
