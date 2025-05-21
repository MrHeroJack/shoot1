import json
import uuid
import os

# Determine the absolute path to the data file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "calendar_reminder_service", "data", "appointments.json")

def load_appointments() -> list:
    """
    Loads appointments from the JSON data file.

    Returns:
        list: A list of appointment dictionaries. Returns an empty list if the file
              doesn't exist, is empty, or contains invalid JSON.
    """
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_appointments(appointments: list):
    """
    Saves the list of appointments to the JSON data file.

    Args:
        appointments (list): A list of appointment dictionaries to save.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(appointments, f, indent=4)

def add_appointment(title: str, date: str, time: str, description: str = "") -> dict:
    """
    Adds a new appointment to the list and saves it.

    Args:
        title (str): The title of the appointment.
        date (str): The date of the appointment (e.g., "YYYY-MM-DD").
        time (str): The time of the appointment (e.g., "HH:MM").
        description (str, optional): A description for the appointment. Defaults to "".

    Returns:
        dict: The newly created appointment dictionary.
    """
    appointments = load_appointments()
    new_appointment = {
        "id": str(uuid.uuid4()),
        "title": title,
        "date": date,
        "time": time,
        "description": description,
        "reminder_set": False,
        "reminder_time": "",
    }
    appointments.append(new_appointment)
    save_appointments(appointments)
    return new_appointment

def get_appointments_on_date(date: str) -> list:
    """
    Retrieves all appointments scheduled for a specific date.

    Args:
        date (str): The date to filter appointments by (e.g., "YYYY-MM-DD").

    Returns:
        list: A list of appointment dictionaries for the given date.
    """
    appointments = load_appointments()
    return [appt for appt in appointments if appt.get("date") == date]

if __name__ == '__main__':
    # Simple test cases
    print("Initial appointments:", load_appointments())

    # Add a new appointment
    added_appt = add_appointment("Team Meeting", "2024-07-30", "10:00", "Discuss Q3 goals.")
    print("Added appointment:", added_appt)
    print("Appointments after adding:", load_appointments())

    added_appt_2 = add_appointment("Doctor's Visit", "2024-07-30", "14:30", "Annual check-up.")
    print("Added another appointment:", added_appt_2)
    print("Appointments after adding second appointment:", load_appointments())

    # Get appointments for a specific date
    appointments_on_date = get_appointments_on_date("2024-07-30")
    print(f"Appointments on 2024-07-30: {appointments_on_date}")

    appointments_on_another_date = get_appointments_on_date("2024-07-31")
    print(f"Appointments on 2024-07-31: {appointments_on_another_date}")

    # Test saving empty list
    save_appointments([])
    print("Appointments after clearing (should be empty):", load_appointments())

    # Add back for further tests if needed
    added_appt_3 = add_appointment("Lunch with Alex", "2024-08-01", "12:00")
    print("Appointments after adding one back:", load_appointments())
    print("Details of the last added appointment:", added_appt_3)
