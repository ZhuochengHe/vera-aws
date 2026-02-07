import importlib
import os
import logging
from flask import Flask, request, jsonify
from emulator_core.state import EmulatorState
from emulator_core.backend import BaseBackend
from emulator_core.gateway.base import BaseGateway

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EC2Emulator")

app = Flask(__name__)

# Initialize Singleton State
state = EmulatorState()

# Registry of Gateways
gateways = {}

def load_services():
    """Dynamically load all service modules from emulator_core/services/"""
    services_dir = "emulator_core/services"
    
    # Auto-populate state attributes from service module names
    # This ensures that if we load 'elastic_ip_addresses.py', we have state.elastic_ip_addresses
    for filename in os.listdir(services_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            if not hasattr(state, module_name):
                setattr(state, module_name, {})

    # Ensure critical legacy/specific attributes exist if they don't match module names exactly
    # (Though most should match now if we stick to snake_case module names matching state attributes)
    extra_attrs = ["vpcs", "subnets", "instances", "security_groups", "resources"]
    for attr in extra_attrs:
        if not hasattr(state, attr):
            setattr(state, attr, {})

    # Populate default regions if empty
    if not hasattr(state, "regions_and_zones") or not state.regions_and_zones:
        try:
            from emulator_core.services.regions_and_zones import Region, OptInStatus, AvailabilityZone, ZoneState, ZoneType
            
            # Default Regions
            default_regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1"]
            for region_name in default_regions:
                region = Region(
                    region_name=region_name,
                    region_endpoint=f"ec2.{region_name}.amazonaws.com",
                    opt_in_status=OptInStatus.OPT_IN_NOT_REQUIRED
                )
                state.regions_and_zones[region_name] = region
                
                # Default AZs for us-east-1
                if region_name == "us-east-1":
                    for zone_suffix in ["a", "b", "c", "d", "e", "f"]:
                        zone_name = f"{region_name}{zone_suffix}"
                        zone_id = f"use1-az{ord(zone_suffix) - ord('a') + 1}"
                        az = AvailabilityZone(
                            zone_name=zone_name,
                            zone_id=zone_id,
                            region_name=region_name,
                            zone_state=ZoneState.AVAILABLE,
                            opt_in_status=OptInStatus.OPT_IN_NOT_REQUIRED,
                            zone_type=ZoneType.AVAILABILITY_ZONE,
                            group_name=region_name,
                            network_border_group=region_name
                        )
                        state.regions_and_zones[zone_name] = az
                        
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Failed to populate default regions: {e}")

    for filename in os.listdir(services_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"emulator_core.services.{module_name}")
                
                # Find Backend and Gateway classes
                backend_cls = None
                gateway_cls = None
                
                for attr_name in dir(module):
                    if attr_name.endswith("Backend") and attr_name != "BaseBackend":
                        backend_cls = getattr(module, attr_name)
                    if attr_name.endswith("Gateway") and attr_name != "BaseGateway":
                        cls = getattr(module, attr_name)
                        if isinstance(cls, type) and issubclass(cls, BaseGateway):
                            gateway_cls = cls
                        
                if backend_cls and gateway_cls:
                    # Instantiate
                    backend = backend_cls(state)
                    gateway = gateway_cls(backend)
                    
                    # Register actions
                    for action in gateway.actions.keys():
                        gateways[action] = gateway
                        
                    logger.info(f"Loaded service: {module_name} ({len(gateway.actions)} actions)")
                    
            except Exception as e:
                logger.error(f"Failed to load service {module_name}: {e}")

@app.route("/", methods=["POST", "GET"])
def handle_request():
    # Parse AWS Query Parameters (Action, Version, etc.)
    if request.method == "POST":
        params = request.form.to_dict()
    else:
        params = request.args.to_dict()
        
    action = params.get("Action")
    if not action:
        return jsonify({"Error": "Missing Action parameter"}), 400
        
    gateway = gateways.get(action)
    if not gateway:
        return jsonify({"Error": f"Unknown Action: {action}"}), 400
        
    try:
        # Pass all params to the handler
        response = gateway.dispatch(action, params)
        
        # XML Conversion Logic
        request_id = response.get("requestId", f"req-{os.urandom(8).hex()}")
        # Remove requestId from response dict if present, as it goes into header or root
        if "requestId" in response:
            del response["requestId"]
            
        def dict_to_xml(tag, d):
            parts = [f"<{tag}>"]
            if isinstance(d, dict):
                for key, val in d.items():
                    # EC2 conventions: 
                    # Keys starting with lowercase are usually converted to TitleCase in XML?
                    # Actually, our backend returns mixed keys.
                    # Standard EC2 responses use UpperCamelCase for tags.
                    # We will capitalize the first letter of keys if they are lowercase.
                    
                    # Heuristic: capitalize first letter if it looks like a field name
                    xml_key = key

                    if isinstance(val, list):
                        # List handling: 
                        # Usually <SetName><item>...</item><item>...</item></SetName>
                        # OR flattened list?
                        # EC2 usually wraps list items in <item>
                        parts.append(f"<{xml_key}>")
                        for item in val:
                            parts.append(dict_to_xml("item", item))
                        parts.append(f"</{xml_key}>")
                    else:
                        parts.append(dict_to_xml(xml_key, val))
            elif isinstance(d, list):
                # Should not happen if called correctly from dict loop, but handle just in case
                for item in d:
                    parts.append(dict_to_xml("item", item))
            elif d is None:
                # Empty tag or omit? Omit usually.
                pass
            else:
                parts.append(str(d))
            
            # Close tag only if we opened it (which we did at start)
            # But wait, for leaf nodes (str), we don't want nested <tag>val</tag> inside the recursion?
            # Re-structure:
            # Recursive function should return XML string content.
            # But the tag wrapping is cleaner.
            
            # Let's use a simpler recursive approach
            return "".join(parts) + f"</{tag}>"

        def to_xml_recursive(key, value):
            xml_key = key

            if value is None:
                return ""
            
            if isinstance(value, list):
                # EC2 list convention: <Key><item>...</item>...</Key>
                items_xml = ""
                for item in value:
                    if isinstance(item, dict) or isinstance(item, list):
                        items_xml += f"<item>{''.join(to_xml_recursive(k, v) for k, v in item.items()) if isinstance(item, dict) else to_xml_recursive('item', item)}</item>"
                    else:
                        items_xml += f"<item>{str(item)}</item>"
                return f"<{xml_key}>{items_xml}</{xml_key}>"
            
            elif isinstance(value, dict):
                content = "".join(to_xml_recursive(k, v) for k, v in value.items())
                return f"<{xml_key}>{content}</{xml_key}>"
            
            elif isinstance(value, bool):
                return f"<{xml_key}>{'true' if value else 'false'}</{xml_key}>"

            else:
                return f"<{xml_key}>{str(value)}</{xml_key}>"

        # Construct Root Response
        root_content = "".join(to_xml_recursive(k, v) for k, v in response.items())
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<{action}Response xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
    <requestId>{request_id}</requestId>
{root_content}
</{action}Response>"""

        return xml_body, 200, {'Content-Type': 'application/xml'}

    except Exception as e:
        logger.error(f"Error handling {action}: {e}")
        # Return XML error response to mimic EC2 behavior
        error_code = "InternalError"
        error_message = str(e)
        if hasattr(e, "code"): # Assuming ErrorCode exception
             error_code = e.code
        elif ":" in str(e): # Try to parse "Code: Message" format
             parts = str(e).split(":", 1)
             if len(parts) == 2 and " " not in parts[0]:
                 error_code = parts[0]
                 error_message = parts[1].strip()

        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Errors>
        <Error>
            <Code>{error_code}</Code>
            <Message>{error_message}</Message>
        </Error>
    </Errors>
    <RequestID>req-{os.urandom(4).hex()}</RequestID>
</Response>"""
        return xml_response, 400, {'Content-Type': 'application/xml'}

if __name__ == "__main__":
    logger.info("Starting EC2 Emulator...")
    load_services()
    app.run(port=5003, debug=True)
