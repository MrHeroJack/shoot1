# Calendar Reminder Service

A simple command-line application for managing appointments and reminders.

## Features

*   Add new appointments with a title, date, time, and description.
*   View appointments scheduled for a specific date.
*   Set reminders for appointments at a specific date and time.
*   Check for due reminders.
*   Appointment data is stored locally in a JSON file (`data/appointments.json`).

## Project Structure

```
calendar_reminder_service/
├── data/
│   └── appointments.json       # Storage for appointment data
├── src/
│   ├── __init__.py
│   ├── app.py                  # Main application CLI
│   ├── appointments.py         # Appointment management logic
│   ├── calendar_utils.py       # (Currently unused, for future calendar-related functions)
│   └── reminders.py            # Reminder management logic
├── tests/
│   ├── __init__.py
│   ├── test_appointments.py    # Unit tests for appointments
│   └── test_reminders.py       # Unit tests for reminders
└── README.md                   # This file
```

## Prerequisites

*   Python 3.x

## Setup

No special setup is required beyond having Python 3 installed. The application uses only standard Python libraries.

## How to Run the Application

1.  Navigate to the `src` directory from the project root:
    ```bash
    cd calendar_reminder_service/src
    ```
2.  Run the main application script:
    ```bash
    python app.py
    ```
    This will start the command-line interface where you can interact with the service.

## How to Run Unit Tests

1.  Navigate to the project root directory (`calendar_reminder_service/`).
2.  Run the following command to discover and execute all unit tests:
    ```bash
    python -m unittest discover tests
    ```
    Or, to run a specific test file:
    ```bash
    python -m unittest tests.test_appointments
    python -m unittest tests.test_reminders
    ```

## Future Enhancements (Examples)

*   Persistent storage using a database (e.g., SQLite).
*   More sophisticated reminder notification (e.g., email, system notifications).
*   Recurring appointments.
*   Web interface using Flask/Django.
*   Calendar view.
```
