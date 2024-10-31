import uuid
from datetime import datetime
from typing import Dict, Optional

# Mock reservation data storage
reservations: Dict[str, dict] = {}

def validate_date_time(date_str: str, time_str: str) -> bool:
    try:
        datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def validate_phone_number(phone_number: str) -> bool:
    return phone_number.startswith("+") and len(phone_number) >= 10

def create_reservation(data: dict) -> dict:
    try:
        name = data["name"]
        party_size = int(data["party_size"])
        date = data["date"]
        time = data["time"]
        phone_number = data["phone_number"]

        if not validate_phone_number(phone_number):
            return {"response": "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."}

        if party_size < 1:
            return {"response": "Party size must be at least 1 person."}

        if not validate_date_time(date, time):
            return {"response": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."}

        if phone_number in reservations:
            return {"response": "A reservation already exists for this phone number."}

        reservations[phone_number] = {
            "name": name,
            "party_size": party_size,
            "date": date,
            "time": time
        }

        return {
            "response": f"Reservation successfully created."
        }

    except KeyError as e:
        return {"response": f"Missing required field: {str(e)}"}
    except Exception as e:
        return {"response": f"Error creating reservation: {str(e)}"}

def get_reservation(data: dict) -> dict:
    try:
        phone_number = data["phone_number"]
        
        if not validate_phone_number(phone_number):
            return {"response": "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."}

        reservation = reservations.get(phone_number)
        if reservation:
            return {
                "response": f"Reservation found: {reservation['name']} for {reservation['party_size']} people on {reservation['date']} at {reservation['time']}. Contact: {phone_number}"
            }
        return {"response": "No reservation found for this phone number."}

    except KeyError:
        return {"response": "Phone number is required."}
    except Exception as e:
        return {"response": f"Error retrieving reservation: {str(e)}"}

def update_reservation(data: dict) -> dict:
    try:
        phone_number = data["phone_number"]
        
        if not validate_phone_number(phone_number):
            return {"response": "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."}

        if phone_number not in reservations:
            return {"response": "No reservation found for this phone number."}

        current_reservation = reservations[phone_number]
        
        if "date" in data and "time" in data:
            if not validate_date_time(data["date"], data["time"]):
                return {"response": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."}

        if "party_size" in data and int(data["party_size"]) < 1:
            return {"response": "Party size must be at least 1 person."}

        updated_reservation = {
            "name": data.get("name", current_reservation["name"]),
            "party_size": int(data.get("party_size", current_reservation["party_size"])),
            "date": data.get("date", current_reservation["date"]),
            "time": data.get("time", current_reservation["time"])
        }

        reservations[phone_number] = updated_reservation
        return {
            "response": f"Reservation updated: {updated_reservation['name']} for {updated_reservation['party_size']} people on {updated_reservation['date']} at {updated_reservation['time']}. Contact: {phone_number}"
        }

    except KeyError:
        return {"response": "Phone number is required."}
    except Exception as e:
        return {"response": f"Error updating reservation: {str(e)}"}

def cancel_reservation(data: dict) -> dict:
    try:
        phone_number = data["phone_number"]
        
        if not validate_phone_number(phone_number):
            return {"response": "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."}

        if phone_number in reservations:
            reservation = reservations[phone_number]
            del reservations[phone_number]
            return {
                "response": f"Reservation canceled successfully."
            }
        return {"response": "No reservation found for this phone number."}

    except KeyError:
        return {"response": "Phone number is required."}
    except Exception as e:
        return {"response": f"Error canceling reservation: {str(e)}"}

def move_reservation(data: dict) -> dict:
    try:
        phone_number = data["phone_number"]
        new_date = data["new_date"]
        new_time = data["new_time"]
        
        if not validate_phone_number(phone_number):
            return {"response": "Invalid phone number format. Please use E.164 format (e.g., +19185551234)."}

        if not validate_date_time(new_date, new_time):
            return {"response": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."}

        if phone_number in reservations:
            reservation = reservations[phone_number]
            old_date = reservation["date"]
            old_time = reservation["time"]
            
            reservation["date"] = new_date
            reservation["time"] = new_time
            
            return {
                "response": f"Reservation moved successfully."
            }
        return {"response": "No reservation found for this phone number."}

    except KeyError as e:
        return {"response": f"Missing required field: {str(e)}"}
    except Exception as e:
        return {"response": f"Error moving reservation: {str(e)}"} 