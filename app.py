from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from urllib.parse import urlsplit, urlunsplit
import os
from reservation_system import (
    create_reservation,
    get_reservation,
    update_reservation,
    cancel_reservation,
    move_reservation
)

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Authentication setup
auth = HTTPBasicAuth()
HTTP_USERNAME = os.getenv("HTTP_USERNAME")
HTTP_PASSWORD = os.getenv("HTTP_PASSWORD")

@auth.verify_password
def verify_password(username, password):
    if username == HTTP_USERNAME and password == HTTP_PASSWORD:
        return True
    return False

# SWAIG function signatures
SWAIG_FUNCTION_SIGNATURES = {
    "create_reservation": {
        "description": "Create a new reservation for a customer",
        "function": "create_reservation",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the person making the reservation"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of people in the party"
                },
                "date": {
                    "type": "string",
                    "description": "Date of reservation in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "description": "Time of reservation in HH:MM format (24-hour)"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Contact phone number in E.164 format (e.g., +19185551234)"
                }
            },
            "required": ["name", "party_size", "date", "time", "phone_number"]
        }
    },
    "get_reservation": {
        "description": "Retrieve an existing reservation",
        "function": "get_reservation",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "Phone number used for the reservation in E.164 format"
                }
            },
            "required": ["phone_number"]
        }
    },
    "update_reservation": {
        "description": "Update an existing reservation",
        "function": "update_reservation",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "Phone number of the existing reservation"
                },
                "name": {
                    "type": "string",
                    "description": "Updated name (optional)"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Updated party size (optional)"
                },
                "date": {
                    "type": "string",
                    "description": "Updated date in YYYY-MM-DD format (optional)"
                },
                "time": {
                    "type": "string",
                    "description": "Updated time in HH:MM format (optional)"
                }
            },
            "required": ["phone_number"]
        }
    },
    "cancel_reservation": {
        "description": "Cancel an existing reservation",
        "function": "cancel_reservation",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "Phone number of the reservation to cancel"
                }
            },
            "required": ["phone_number"]
        }
    },
    "move_reservation": {
        "description": "Move an existing reservation to a new date and time",
        "function": "move_reservation",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "Phone number of the existing reservation"
                },
                "new_date": {
                    "type": "string",
                    "description": "New date in YYYY-MM-DD format"
                },
                "new_time": {
                    "type": "string",
                    "description": "New time in HH:MM format"
                }
            },
            "required": ["phone_number", "new_date", "new_time"]
        }
    }
}

def get_function_signatures(requested_functions, host_url):
    if not requested_functions:
        requested_functions = list(SWAIG_FUNCTION_SIGNATURES.keys())

    split_url = urlsplit(host_url.rstrip('/'))
    
    # Add authentication to URL if credentials exist
    if HTTP_USERNAME and HTTP_PASSWORD:
        netloc = f"{HTTP_USERNAME}:{HTTP_PASSWORD}@{split_url.netloc}"
    else:
        netloc = split_url.netloc

    # Construct webhook URL
    webhook_url = urlunsplit((
        split_url.scheme,
        netloc,
        split_url.path,
        split_url.query,
        split_url.fragment
    ))

    # Add webhook URL to each function signature
    signatures = []
    for func in requested_functions:
        if func in SWAIG_FUNCTION_SIGNATURES:
            signature = SWAIG_FUNCTION_SIGNATURES[func].copy()
            signature["web_hook_url"] = f"{webhook_url}/swaig"
            signatures.append(signature)

    return signatures

def execute_function(function_name: str, params: dict) -> dict:
    function_map = {
        "create_reservation": create_reservation,
        "get_reservation": get_reservation,
        "update_reservation": update_reservation,
        "cancel_reservation": cancel_reservation,
        "move_reservation": move_reservation
    }

    if function_name not in function_map:
        return {"error": "Function not found"}, 404

    try:
        result = function_map[function_name](params)
        return {"response": result["response"]}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/swaig', methods=['POST'])
@auth.login_required
def swaig_handler():
    data = request.json
    action = data.get('action')

    if action == "get_signature":
        requested_functions = data.get("functions", [])
        signatures = get_function_signatures(requested_functions, request.host_url)
        return jsonify(signatures)

    function_name = data.get('function')
    params = data.get('argument', {}).get('parsed', [{}])[0]
    
    result, status_code = execute_function(function_name, params)
    return jsonify(result), status_code

@app.route('/')
@app.route('/swaig', methods=['GET'])
def serve_reservation_html():
    try:
        return """
        <html>
            <head>
                <title>Bobby's Table Reservation System</title>
            </head>
            <body>
                <h1>Bobby's Table Reservation System</h1>
                <p>This is a SWAIG-based reservation system. Please use the API endpoints to interact with the system.</p>
            </body>
        </html>
        """
    except Exception as e:
        return jsonify({"error": "Failed to serve HTML"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True) 