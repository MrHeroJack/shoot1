import unittest
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch

# Assuming tests are run from the project root: `python -m unittest discover calendar_reminder_service/tests`
from calendar_reminder_service.src import reminders
from calendar_reminder_service.src import appointments # For test data setup

class TestReminders(unittest.TestCase):

    def setUp(self):
        # Define a directory for test data files within the tests directory
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Use a different test file for reminder tests to avoid conflicts if run in parallel (though unittest usually serializes)
        self.test_reminders_data_file = os.path.join(self.test_data_dir, "test_reminders_appointments.json")

        # Patch DATA_FILE in the appointments module, as it's used by both appointments and reminders
        self.data_file_patcher = patch('calendar_reminder_service.src.appointments.DATA_FILE', self.test_reminders_data_file)
        self.mock_data_file = self.data_file_patcher.start()

        # Clean up test data file before each test by saving an empty list
        appointments.save_appointments([])

    def tearDown(self):
        self.data_file_patcher.stop()
        if os.path.exists(self.test_reminders_data_file):
            os.remove(self.test_reminders_data_file)
        if os.path.exists(self.test_data_dir) and not os.listdir(self.test_data_dir):
            os.rmdir(self.test_data_dir)

    def test_set_reminder_success(self):
        # Add an appointment
        appt = appointments.add_appointment("Test Event for Reminder", "2024-09-01", "10:00")
        self.assertFalse(appt["reminder_set"]) # Initially false

        reminder_time_str = "2024-09-01 08:00"
        result = reminders.set_reminder(appt["id"], reminder_time_str)
        self.assertTrue(result)

        # Load appointments and check
        updated_appts = appointments.load_appointments()
        found_appt = next((a for a in updated_appts if a["id"] == appt["id"]), None)
        
        self.assertIsNotNone(found_appt)
        self.assertTrue(found_appt["reminder_set"])
        self.assertEqual(found_appt["reminder_time"], reminder_time_str)

    def test_set_reminder_invalid_datetime_format(self):
        appt = appointments.add_appointment("Test Event Format", "2024-09-02", "10:00")
        result = reminders.set_reminder(appt["id"], "2024/09/02 08:00AM") # Invalid format
        self.assertFalse(result)
        updated_appts = appointments.load_appointments()
        found_appt = next((a for a in updated_appts if a["id"] == appt["id"]), None)
        self.assertFalse(found_appt["reminder_set"]) # Should not have changed

    def test_set_reminder_non_existent_appointment(self):
        result = reminders.set_reminder("non-existent-id", "2024-09-01 08:00")
        self.assertFalse(result)

    def test_check_reminders(self):
        # Define mock current times for testing different scenarios
        mock_now_past_all = datetime(2024, 1, 1, 10, 0, 0) # Way in the past
        mock_now_due_for_appt1 = datetime(2024, 8, 15, 13, 0, 0) # Appt1 reminder is due, appt1 event future
        mock_now_after_appt1_reminder_before_event = datetime(2024, 8, 15, 15, 0, 0) # Appt1 reminder still due (as long as event not past)
        mock_now_after_appt1_event = datetime(2024, 8, 16, 10, 0, 0) # Appt1 event is now past
        mock_now_before_any_reminders = datetime(2024, 8, 1, 12, 0, 0)


        # Scenario 1: Appointment event in the future, reminder time in the past (should be due)
        appt1 = appointments.add_appointment("Future Event, Past Reminder", "2024-08-15", "14:00") # Event time
        reminders.set_reminder(appt1["id"], "2024-08-15 12:00") # Reminder time (2 hours before event)

        # Scenario 2: Appointment event in the future, reminder time also in the future (should not be due)
        appt2 = appointments.add_appointment("Future Event, Future Reminder", "2024-08-20", "10:00")
        reminders.set_reminder(appt2["id"], "2024-08-20 08:00") # Reminder time for appt2

        # Scenario 3: Appointment event in the past, reminder time also in the past (should not be due)
        appt3 = appointments.add_appointment("Past Event, Past Reminder", "2024-07-01", "10:00") # Event time
        reminders.set_reminder(appt3["id"], "2024-07-01 08:00") # Reminder time

        # Scenario 4: Appointment with reminder set, but reminder time is empty (should not cause error, not due)
        appt4 = appointments.add_appointment("Event No Reminder Time", "2024-08-25", "11:00")
        # Manually update this to simulate reminder_set=True but empty reminder_time (though set_reminder shouldn't allow this)
        loaded_appts = appointments.load_appointments()
        for a in loaded_appts:
            if a['id'] == appt4['id']:
                a['reminder_set'] = True
                a['reminder_time'] = "" # Explicitly empty
        appointments.save_appointments(loaded_appts)


        # --- Test with mock_now_due_for_appt1 ---
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_due_for_appt1
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs) # Keep strptime working

            due = reminders.check_reminders()
            self.assertEqual(len(due), 1)
            self.assertEqual(due[0]["id"], appt1["id"])

        # --- Test with mock_now_before_any_reminders ---
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_before_any_reminders
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            due = reminders.check_reminders()
            self.assertEqual(len(due), 0)

        # --- Test with mock_now_after_appt1_event ---
        # (Reminder for appt1 was due, but now event itself is past)
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_after_appt1_event
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)
            
            due = reminders.check_reminders()
            # Appt1 should not be due because its main event time is past
            self.assertFalse(any(d["id"] == appt1["id"] for d in due))
            self.assertEqual(len(due), 0) # Assuming appt2, appt3 also not due

        # --- Test with mock_now_past_all (covers appt3 case more directly) ---
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_past_all # Very early date
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)
            
            # At this 'now', all events are in the future, so no reminders should be due
            # This test is a bit redundant with 'before_any_reminders' but checks if logic holds
            # for a 'now' that is before event and reminder times of all sample data.
            due = reminders.check_reminders()
            self.assertEqual(len(due), 0)


if __name__ == '__main__':
    unittest.main()
