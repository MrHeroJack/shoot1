from datetime import datetime
from .appointments import load_appointments, save_appointments, DATA_FILE # Added DATA_FILE for testing
import os # For testing

def set_reminder(appointment_id: str, reminder_datetime_str: str) -> bool:
    """
    Sets a reminder for a specific appointment.

    Args:
        appointment_id (str): The ID of the appointment to set the reminder for.
        reminder_datetime_str (str): The reminder time in "YYYY-MM-DD HH:MM" format.

    Returns:
        bool: True if the reminder was set successfully, False otherwise.
    """
    appointments = load_appointments()
    appointment_found = False
    for appt in appointments:
        if appt.get("id") == appointment_id:
            try:
                # Validate the reminder_datetime_str format
                datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M")
                appt["reminder_time"] = reminder_datetime_str
                appt["reminder_set"] = True
                appointment_found = True
                break
            except ValueError:
                # Invalid datetime format
                return False
    
    if appointment_found:
        save_appointments(appointments)
        return True
    return False

def check_reminders() -> list:
    """
    Checks for appointments whose reminder time has passed.

    Returns:
        list: A list of appointment dictionaries that are due for a reminder.
    """
    appointments = load_appointments()
    due_reminders = []
    now = datetime.now()

    for appt in appointments:
        if appt.get("reminder_set") and appt.get("reminder_time"):
            try:
                reminder_time_obj = datetime.strptime(appt["reminder_time"], "%Y-%m-%d %H:%M")
                appointment_datetime_str = f"{appt.get('date')} {appt.get('time')}"
                appointment_time_obj = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")

                # Check if reminder time is past and appointment time is still in the future (or present)
                if reminder_time_obj <= now and appointment_time_obj >= now:
                    due_reminders.append(appt)
                # Optional: could also add a condition for reminders that are very old,
                # or appointments that are already past their main time.
                # For now, just checking if reminder_time <= now.
                # A simpler check without considering if the appointment itself is past:
                # if reminder_time_obj <= now:
                #     due_reminders.append(appt)

            except ValueError:
                # Invalid date/time format in stored data, skip this appointment
                continue
    return due_reminders

if __name__ == '__main__':
    # Setup: Ensure a clean data file for testing
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    
    # Use functions from appointments.py to add test data
    from .appointments import add_appointment

    print("Initial appointments:", load_appointments())

    # Add some appointments
    appt1 = add_appointment("Dentist Checkup", "2024-08-15", "09:00", "Routine cleaning.")
    appt2 = add_appointment("Project Deadline", "2024-08-10", "17:00", "Submit phase 1.")
    appt3 = add_appointment("Birthday Party", "2024-08-12", "18:00", "Alice's birthday.")
    
    print(f"Appointments after adding: {load_appointments()}")

    # Set reminders
    print("\n--- Setting Reminders ---")
    # Reminder for appt1 (Dentist) - valid
    reminder_dt_appt1 = (datetime.strptime(appt1['date'] + ' ' + appt1['time'], "%Y-%m-%d %H:%M") - \
                         timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
    print(f"Setting reminder for appt1 ({appt1['id']}) at {reminder_dt_appt1}")
    if set_reminder(appt1["id"], reminder_dt_appt1):
        print(f"Reminder set for appt1: {load_appointments()}")
    else:
        print(f"Failed to set reminder for appt1.")

    # Reminder for appt2 (Project) - also valid, set it to a time in the past for testing check_reminders
    past_reminder_time = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    print(f"Setting reminder for appt2 ({appt2['id']}) at {past_reminder_time} (this should be due)")
    if set_reminder(appt2["id"], past_reminder_time):
        print(f"Reminder set for appt2: {load_appointments()}")
    else:
        print(f"Failed to set reminder for appt2.")

    # Reminder for appt3 (Birthday) - future appointment, future reminder
    future_reminder_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    # Ensure this reminder is before the event itself, or it won't make sense
    event_time_appt3 = datetime.strptime(appt3['date'] + ' ' + appt3['time'], "%Y-%m-%d %H:%M")
    parsed_future_reminder = datetime.strptime(future_reminder_time, "%Y-%m-%d %H:%M")
    if parsed_future_reminder < event_time_appt3:
        print(f"Setting reminder for appt3 ({appt3['id']}) at {future_reminder_time}")
        if set_reminder(appt3["id"], future_reminder_time):
            print(f"Reminder set for appt3: {load_appointments()}")
        else:
            print(f"Failed to set reminder for appt3.")
    else:
        print(f"Skipping reminder for appt3 as calculated reminder time {future_reminder_time} is after event time.")


    # Try setting a reminder for a non-existent appointment
    print(f"\nAttempting to set reminder for non-existent ID 'invalid-id':")
    if not set_reminder("invalid-id", "2024-08-01 10:00"):
        print("Correctly failed to set reminder for non-existent appointment.")
    
    # Try setting a reminder with invalid datetime format
    print(f"\nAttempting to set reminder for appt1 with invalid datetime format:")
    if not set_reminder(appt1["id"], "2024/08/15 10am"):
        print(f"Correctly failed to set reminder with invalid format. Current appt1: {[a for a in load_appointments() if a['id'] == appt1['id']][0]}")


    # Check for due reminders
    print("\n--- Checking Reminders ---")
    # Need timedelta for test case definition
    from datetime import timedelta
    
    due = check_reminders()
    print(f"Due reminders now ({datetime.now().strftime('%Y-%m-%d %H:%M')}): {due}")
    if any(d['id'] == appt2['id'] for d in due):
        print(f"SUCCESS: Appt2 (Project Deadline) is correctly listed as due.")
    else:
        print(f"FAILURE: Appt2 (Project Deadline) was expected to be due but is not.")

    if not any(d['id'] == appt1['id'] for d in due):
        print(f"SUCCESS: Appt1 (Dentist) is correctly not listed as due yet (reminder: {appt1.get('reminder_time')}).")
    else:
        print(f"FAILURE: Appt1 (Dentist) was not expected to be due but is.")
        
    if not any(d['id'] == appt3['id'] for d in due):
        print(f"SUCCESS: Appt3 (Birthday) is correctly not listed as due yet (reminder: {appt3.get('reminder_time')}).")
    else:
        print(f"FAILURE: Appt3 (Birthday) was not expected to be due but is.")

    # Test case: appointment past, reminder past
    print("\n--- Test: Past Appointment, Past Reminder ---")
    past_appt = add_appointment("Old Event", "2023-01-01", "10:00")
    past_reminder_for_past_appt = (datetime.strptime(past_appt['date'] + ' ' + past_appt['time'], "%Y-%m-%d %H:%M") - \
                                   timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    set_reminder(past_appt['id'], past_reminder_for_past_appt)
    print(f"Added past appointment with past reminder: {past_appt}")
    due_after_past_appt = check_reminders()
    if not any(d['id'] == past_appt['id'] for d in due_after_past_appt):
        print(f"SUCCESS: Past appointment '{past_appt['title']}' with past reminder is NOT listed as due.")
    else:
        print(f"FAILURE: Past appointment '{past_appt['title']}' with past reminder IS listed as due.")

    # Test case: appointment future, reminder past, but appointment time is also past reminder time (edge case)
    print("\n--- Test: Future Appointment, Reminder in Past (but after appointment time) ---")
    # This scenario should ideally not happen if reminders are set sanely (before event)
    # But check_reminders should handle it by not showing it as due if appointment_time < reminder_time_obj
    # For this, let's manually craft an appointment where reminder_time is after event time
    # This is not possible with current set_reminder logic if we set reminder relative to event time
    # So we'll test the check_reminders logic directly by modifying an appointment
    
    # Create a valid appointment first
    edge_appt = add_appointment("Edge Case Event", "2024-09-01", "10:00")
    # Manually set a reminder time that is *after* the event but in the past relative to now
    # This is to test the `appointment_time_obj >= now` part of the check.
    # Let's assume 'now' is 2024-08-15 for this thought experiment.
    # Event: 2024-09-01 10:00. Reminder: 2024-08-14 10:00 (past, so would trigger)
    # But we are checking if `appointment_time_obj >= now`.
    # Let's assume now is `2024-09-02 12:00` (after the event `2024-09-01 10:00`)
    # And the reminder was set for `2024-09-01 08:00` (before event, but event is now past)
    
    # Let's simulate this by directly modifying the data for check_reminders test
    all_appts = load_appointments()
    for a in all_appts:
        if a['id'] == edge_appt['id']:
            a['reminder_set'] = True
            # Reminder time is before the event, but let's imagine 'now' is after the event.
            a['reminder_time'] = (datetime.strptime(a['date'] + ' ' + a['time'], "%Y-%m-%d %H:%M") - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M") # e.g. 2024-09-01 08:00
            # To simulate the event being in the past, we'd need to control 'now' in check_reminders,
            # or use an event that's actually in the past from real 'now'.
            # The existing "Old Event" test covers this better.
            break
    save_appointments(all_appts)
    # This test case is becoming a bit convoluted due to reliance on actual 'now'.
    # The "Old Event" test is clearer for "event in past".
    # The current logic `reminder_time_obj <= now and appointment_time_obj >= now`
    # means if the appointment time itself is in the past, it won't be reminded.

    print(f"\nFinal appointments state: {load_appointments()}")
