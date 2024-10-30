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

# Mock reservation data storage
reservations = {}

def generate_reservation_id():
    return str(uuid.uuid4())

def create_reservation(data):
    reservation_id = generate_reservation_id()
    reservations[reservation_id] = {
        "name": data["name"],
        "party_size": data["party_size"],
        "date": data["date"],
        "time": data["time"],
        "phone_number": data["phone_number"]
    }
    return {"response": f"Reservation successfully created for {data['party_size']} people on {data['date']} at {data['time']}. Contact: {data['phone_number']}. Reservation ID: {reservation_id}"}

def get_reservation(data):
    reservation_id = data["reservation_id"]
    reservation = reservations.get(reservation_id)
    if reservation:
        return {"response": f"Reservation found: {reservation['name']} for {reservation['party_size']} people on {reservation['date']} at {reservation['time']}. Contact: {reservation['phone_number']}"}
    return {"response": "Reservation not found."}

def update_reservation(data):
    reservation_id = data["reservation_id"]
    if reservation_id in reservations:
        reservations[reservation_id].update({
            "name": data.get("name", reservations[reservation_id]["name"]),
            "party_size": data.get("party_size", reservations[reservation_id]["party_size"]),
            "date": data.get("date", reservations[reservation_id]["date"]),
            "time": data.get("time", reservations[reservation_id]["time"]),
            "phone_number": data.get("phone_number", reservations[reservation_id]["phone_number"])
        })
        return {"response": f"Reservation for {reservation_id} successfully updated."}
    return {"response": "Reservation not found."}

def cancel_reservation(data):
    reservation_id = data["reservation_id"]
    if reservation_id in reservations:
        del reservations[reservation_id]
        return {"response": f"Reservation for {reservation_id} successfully canceled."}
    return {"response": "Reservation not found."}

def move_reservation(data):
    reservation_id = data["reservation_id"]
    if reservation_id in reservations:
        reservations[reservation_id].update({
            "date": data["new_date"],
            "time": data["new_time"]
        })
        return {"response": f"Reservation moved to {data['new_date']} at {data['new_time']}. Contact: {reservations[reservation_id]['phone_number']}"}
    return {"response": "Reservation not found."}
```

---

## 6. Cursor Compose System Prompt

**Cursor Compose System Prompt**:

"Build a Python application named *Bobby’s Table* that uses SWAIG functions for a restaurant reservation system. Implement five functions:

1. **`create_reservation`**: Creates a reservation, returning a unique ID and confirmation.
2. **`get_reservation`**: Retrieves a reservation by ID, returning details in a human-readable format

.
3. **`update_reservation`**: Updates a reservation, confirming the changes.
4. **`cancel_reservation`**: Cancels a reservation and provides a confirmation message.
5. **`move_reservation`**: Moves a reservation to a new date and time.

Each function should:
- Return a `response` field with human-readable statements for LLM consumption.
- Use in-memory storage with no database.
- Generate reservation IDs with Python’s `uuid`.

Ensure error handling is included for each function to provide user-friendly responses." 

