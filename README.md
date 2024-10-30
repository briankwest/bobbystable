# Bobby’s Table Reservation System

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [SWML / SWAIG Functions](#swml--swaig-functions)
   - [Function: `create_reservation`](#function-create_reservation)
   - [Function: `get_reservation`](#function-get_reservation)
   - [Function: `update_reservation`](#function-update_reservation)
   - [Function: `cancel_reservation`](#function-cancel_reservation)
   - [Function: `move_reservation`](#function-move_reservation)
4. [Mock Data Structure](#mock-data-structure)
5. [Python Code Structure with Human-Readable Responses](#python-code-structure-with-human-readable-responses)
6. [Cursor Compose System Prompt](#cursor-compose-system-prompt)

---

## 1. Introduction

This document provides a design for the *Bobby's Table* reservation system using SignalWire AI Gateway (SWAIG). Each function is designed to manage reservations by directly interacting with SWAIG, eliminating the need for endpoint mappings. The system uses in-memory data storage to perform reservation operations, providing human-readable responses for LLM consumption.

---

## 2. System Overview

The *Bobby’s Table* reservation system allows users to perform actions such as creating, retrieving, updating, canceling, and moving reservations. Each function returns a response formatted for human readability, making it easier for LLMs to interpret the output.

---

## 3. SWML / SWAIG Functions

### Function: `create_reservation`

- **Purpose**: Creates a new reservation and generates a unique reservation ID.
- **Function Name**: `create_reservation`
- **Argument Description**:

  ```json
  {
    "function": "create_reservation",
    "description": "Create a new reservation for a user at the restaurant",
    "parameters": {
      "properties": {
        "name": {
          "description": "The name of the person making the reservation.",
          "type": "string"
        },
        "party_size": {
          "description": "The number of people in the reservation.",
          "type": "integer"
        },
        "date": {
          "description": "The date for the reservation in YYYY-MM-DD format.",
          "type": "string"
        },
        "time": {
          "description": "The time for the reservation in HH:MM format (24-hour time).",
          "type": "string"
        },
        "phone_number": {
          "description": "The phone number of the person making the reservation.",
          "type": "string"
        }
      },
      "type": "object"
    }
  }
  ```

### Function: `get_reservation`

- **Purpose**: Retrieves reservation details based on a reservation ID.
- **Function Name**: `get_reservation`
- **Argument Description**:

  ```json
  {
    "function": "get_reservation",
    "description": "Retrieve details of an existing reservation using a reservation ID",
    "parameters": {
      "properties": {
        "reservation_id": {
          "description": "The unique ID of the reservation to retrieve.",
          "type": "string"
        }
      },
      "type": "object"
    }
  }
  ```

### Function: `update_reservation`

- **Purpose**: Updates an existing reservation’s details.
- **Function Name**: `update_reservation`
- **Argument Description**:

  ```json
  {
    "function": "update_reservation",
    "description": "Update the details of an existing reservation",
    "parameters": {
      "properties": {
        "reservation_id": {
          "description": "The unique ID of the reservation to update.",
          "type": "string"
        },
        "name": {
          "description": "The updated name for the reservation, if changed.",
          "type": "string"
        },
        "party_size": {
          "description": "The updated party size for the reservation, if changed.",
          "type": "integer"
        },
        "date": {
          "description": "The updated date for the reservation in YYYY-MM-DD format, if changed.",
          "type": "string"
        },
        "time": {
          "description": "The updated time for the reservation in HH:MM format (24-hour time), if changed.",
          "type": "string"
        },
        "phone_number": {
          "description": "The updated phone number for the reservation, if changed.",
          "type": "string"
        }
      },
      "type": "object"
    }
  }
  ```

### Function: `cancel_reservation`

- **Purpose**: Cancels an existing reservation.
- **Function Name**: `cancel_reservation`
- **Argument Description**:

  ```json
  {
    "function": "cancel_reservation",
    "description": "Cancel an existing reservation",
    "parameters": {
      "properties": {
        "reservation_id": {
          "description": "The unique ID of the reservation to cancel.",
          "type": "string"
        }
      },
      "type": "object"
    }
  }
  ```

### Function: `move_reservation`

- **Purpose**: Moves an existing reservation to a new date and/or time.
- **Function Name**: `move_reservation`
- **Argument Description**:

  ```json
  {
    "function": "move_reservation",
    "description": "Change the date and/or time of an existing reservation",
    "parameters": {
      "properties": {
        "reservation_id": {
          "description": "The unique ID of the reservation to move.",
          "type": "string"
        },
        "new_date": {
          "description": "The new date for the reservation in YYYY-MM-DD format.",
          "type": "string"
        },
        "new_time": {
          "description": "The new time for the reservation in HH:MM format (24-hour time).",
          "type": "string"
        },
        "phone_number": {
          "description": "The phone number of the person making the reservation.",
          "type": "string"
        }
      },
      "type": "object"
    }
  }
  ```

---

## 4. Mock Data Structure

The reservation data will be stored in an in-memory dictionary using the `phone_number` in E.164 format as the key.

### Example Data Structure

```python
reservations = {
    "+19185551234": {
        "name": "John Doe",
        "party_size": 4,
        "date": "2024-11-01",
        "time": "19:00"
    },
    "+19185555678": {
        "name": "Jane Smith",
        "party_size": 2,
        "date": "2024-11-02",
        "time": "18:30"
    }
}
```

---

## 5. Python Code Structure with Human-Readable Responses

Here’s the Python code for each function to provide a `response` field containing a human-readable statement for LLM consumption.

```python
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
            "response": f"Reservation successfully created for {name} - {party_size} people on {date} at {time}. Contact: {phone_number}"
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
                "response": f"Reservation canceled for {reservation['name']} on {reservation['date']} at {reservation['time']}. Contact: {phone_number}"
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
                "response": f"Reservation for {reservation['name']} moved from {old_date} at {old_time} to {new_date} at {new_time}. Contact: {phone_number}"
            }
        return {"response": "No reservation found for this phone number."}

    except KeyError as e:
        return {"response": f"Missing required field: {str(e)}"}
    except Exception as e:
        return {"response": f"Error moving reservation: {str(e)}"} 
```