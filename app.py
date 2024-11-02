from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import os
from signalwire_swaig.core import SWAIG, Parameter

from reservation_system import (
    create_reservation,
    get_reservation,
    update_reservation,
    cancel_reservation,
    move_reservation,
    reservations
)
import random

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.static_folder = os.path.abspath('static')

load_dotenv()

# Authentication setup
auth = HTTPBasicAuth()
HTTP_USERNAME = os.getenv("HTTP_USERNAME")
HTTP_PASSWORD = os.getenv("HTTP_PASSWORD")

@auth.verify_password
def verify_password(username, password):
    return username == HTTP_USERNAME and password == HTTP_PASSWORD

# Initialize SWAIG
swaig = SWAIG(app, auth=(HTTP_USERNAME, HTTP_PASSWORD))

@swaig.endpoint(
    description="Create a new reservation for a customer",
    name=Parameter(type="string", description="The name of the person making the reservation"),
    party_size=Parameter(type="integer", description="Number of people in the party"),
    date=Parameter(type="string", description="Date of reservation in YYYY-MM-DD format"),
    time=Parameter(type="string", description="Time of reservation in HH:MM format (24-hour)"),
    phone_number=Parameter(type="string", description="Contact phone number in E.164 format (e.g., +19185551234)")
)
def create_reservation_endpoint(name, party_size, date, time, phone_number):
    return create_reservation({
        "name": name,
        "party_size": party_size,
        "date": date,
        "time": time,
        "phone_number": phone_number
    })

@swaig.endpoint(
    description="Retrieve an existing reservation",
    phone_number=Parameter(type="string", description="Phone number used for the reservation in E.164 format")
)
def get_reservation_endpoint(phone_number):
    return get_reservation({"phone_number": phone_number})

@swaig.endpoint(
    description="Update an existing reservation",
    phone_number=Parameter(type="string", description="Phone number of the existing reservation"),
    name=Parameter(type="string", description="Updated name (optional)", required=False),
    party_size=Parameter(type="integer", description="Updated party size (optional)", required=False),
    date=Parameter(type="string", description="Updated date in YYYY-MM-DD format (optional)", required=False),
    time=Parameter(type="string", description="Updated time in HH:MM format (optional)", required=False)
)
def update_reservation_endpoint(phone_number, name=None, party_size=None, date=None, time=None):
    return update_reservation({
        "phone_number": phone_number,
        "name": name,
        "party_size": party_size,
        "date": date,
        "time": time
    })

@swaig.endpoint(
    description="Cancel an existing reservation",
    phone_number=Parameter(type="string", description="Phone number of the reservation to cancel")
)
def cancel_reservation_endpoint(phone_number):
    return cancel_reservation({"phone_number": phone_number})

@swaig.endpoint(
    description="Move an existing reservation to a new date and time",
    phone_number=Parameter(type="string", description="Phone number of the existing reservation"),
    new_date=Parameter(type="string", description="New date in YYYY-MM-DD format"),
    new_time=Parameter(type="string", description="New time in HH:MM format")
)
def move_reservation_endpoint(phone_number, new_date, new_time):
    return move_reservation({
        "phone_number": phone_number,
        "new_date": new_date,
        "new_time": new_time
    })

def scramble_phone_number(phone):
    if not phone or len(phone) < 6:
        return phone
    return phone[:-6] + ''.join(random.choices('0123456789', k=6))

def get_reservations_table_html():
    if not reservations:
        return "<p>No reservations yet.</p>"
    
    table_html = """
    <table border="1">
        <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Date</th>
            <th>Time</th>
            <th>Party Size</th>
        </tr>
    """
    
    for phone, details in reservations.items():
        scrambled = scramble_phone_number(phone)
        table_html += f"""
        <tr>
            <td>{details['name']}</td>
            <td>{scrambled}</td>
            <td>{details['date']}</td>
            <td>{details['time']}</td>
            <td>{details['party_size']}</td>
        </tr>
        """
    
    table_html += "</table>"
    return table_html

@app.route('/', methods=['GET'])
def serve_reservation_html():
    try:
        with open('static/reservation.html', 'r') as file:
            html_content = file.read()
        
        reservations_table = get_reservations_table_html()
        
        # Replace placeholders with actual data
        html_content = html_content.replace("{{reservations_table}}", reservations_table)
        
        # Insert Google Tag Manager script if the tag is available
        GOOGLE_TAG = os.getenv("GOOGLE_TAG")
        if GOOGLE_TAG:
            gtm_script = f"""
            <script async src="https://www.googletagmanager.com/gtag/js?id={GOOGLE_TAG}"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){{dataLayer.push(arguments);}}
              gtag('js', new Date());
              gtag('config', '{GOOGLE_TAG}');
            </script>
            """
            # Insert the GTM script before the closing </head> tag
            html_content = html_content.replace("</head>", f"{gtm_script}</head>")
        
        return html_content
    except Exception as e:
        return jsonify({"error": "Failed to serve HTML"}), 500

if __name__ == "__main__":
    port = os.getenv("PORT", 5001)
    app.run(host="0.0.0.0", port=port, debug=True)
