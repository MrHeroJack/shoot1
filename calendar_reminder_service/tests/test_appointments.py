import unittest
import os
import json
from unittest.mock import patch

# Assuming tests are run from the project root: `python -m unittest discover calendar_reminder_service/tests`
# This means 'calendar_reminder_service' is the top-level package.
from calendar_reminder_service.src import appointments

class TestAppointments(unittest.TestCase):

    def setUp(self):
        # Define a directory for test data files within the tests directory
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        self.test_data_file = os.path.join(self.test_data_dir, "test_appointments.json")

        # Patch DATA_FILE in the appointments module
        self.data_file_patcher = patch('calendar_reminder_service.src.appointments.DATA_FILE', self.test_data_file)
        self.mock_data_file = self.data_file_patcher.start()

        # Clean up test data file before each test
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        with open(self.test_data_file, 'w') as f:
            json.dump([], f)

    def tearDown(self):
        # Stop patching
        self.data_file_patcher.stop()
        # Clean up test data file after each test
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        if os.path.exists(self.test_data_dir) and not os.listdir(self.test_data_dir):
            os.rmdir(self.test_data_dir)


    def test_add_appointment(self):
        # Add an appointment
        added_appt = appointments.add_appointment("Test Event", "2024-01-01", "10:00", "Test Description")
        
        # Verify returned appointment
        self.assertEqual(added_appt["title"], "Test Event")
        self.assertEqual(added_appt["date"], "2024-01-01")
        self.assertEqual(added_appt["time"], "10:00")
        self.assertEqual(added_appt["description"], "Test Description")
        self.assertIn("id", added_appt)
        self.assertFalse(added_appt["reminder_set"]) # Check default reminder fields
        self.assertEqual(added_appt["reminder_time"], "")

        # Load data directly from the test file and verify
        with open(self.test_data_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Test Event")
        self.assertEqual(data[0]["id"], added_appt["id"])

    def test_get_appointments_on_date(self):
        # Add a few appointments
        appt1 = appointments.add_appointment("Event 1", "2024-01-01", "10:00")
        appt2 = appointments.add_appointment("Event 2", "2024-01-02", "11:00")
        appt3 = appointments.add_appointment("Event 3", "2024-01-01", "12:00")

        # Test retrieving for a specific date with multiple appointments
        on_date_01 = appointments.get_appointments_on_date("2024-01-01")
        self.assertEqual(len(on_date_01), 2)
        self.assertTrue(any(a["id"] == appt1["id"] for a in on_date_01))
        self.assertTrue(any(a["id"] == appt3["id"] for a in on_date_01))

        # Test retrieving for a date with one appointment
        on_date_02 = appointments.get_appointments_on_date("2024-01-02")
        self.assertEqual(len(on_date_02), 1)
        self.assertEqual(on_date_02[0]["id"], appt2["id"])

        # Test retrieving for a date with no appointments
        on_date_03 = appointments.get_appointments_on_date("2024-01-03")
        self.assertEqual(len(on_date_03), 0)

    def test_load_appointments(self):
        # 1. Test loading from a non-existent file (mocked DATA_FILE is initially empty or non-existent before save)
        #    Our setUp ensures DATA_FILE is created as an empty list, so this case is covered by empty file.
        #    To truly test non-existent, we'd remove it and then load.
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        loaded_from_non_existent = appointments.load_appointments()
        self.assertEqual(loaded_from_non_existent, [])
        # Recreate for other tests if needed, or rely on setUp for next test
        with open(self.test_data_file, 'w') as f:
            json.dump([], f)


        # 2. Test loading from an empty file (file contains "[]")
        with open(self.test_data_file, 'w') as f:
            json.dump([], f)
        loaded_from_empty_list = appointments.load_appointments()
        self.assertEqual(loaded_from_empty_list, [])

        # 3. Test loading from an empty file (file is literally empty, 0 bytes)
        with open(self.test_data_file, 'w') as f:
            pass # Creates an empty file
        loaded_from_truly_empty = appointments.load_appointments()
        self.assertEqual(loaded_from_truly_empty, [])


        # 4. Test loading from a file with valid JSON
        sample_data = [
            {"id": "1", "title": "Event A", "date": "2024-02-01", "time": "13:00", "description": "", "reminder_set": False, "reminder_time": ""},
            {"id": "2", "title": "Event B", "date": "2024-02-02", "time": "14:00", "description": "Desc", "reminder_set": True, "reminder_time": "2024-02-02 10:00"}
        ]
        with open(self.test_data_file, 'w') as f:
            json.dump(sample_data, f)
        
        loaded_data = appointments.load_appointments()
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data, sample_data)

        # 5. Test loading from a file with invalid JSON
        with open(self.test_data_file, 'w') as f:
            f.write("this is not json")
        loaded_from_invalid = appointments.load_appointments()
        self.assertEqual(loaded_from_invalid, [])


    def test_save_appointments(self):
        sample_appointments = [
            {"id": "s1", "title": "Save Test 1", "date": "2024-03-01", "time": "15:00", "description": "Save Desc 1", "reminder_set": False, "reminder_time": ""},
            {"id": "s2", "title": "Save Test 2", "date": "2024-03-02", "time": "16:00", "description": "Save Desc 2", "reminder_set": True, "reminder_time": "2024-03-02 12:00"}
        ]
        
        appointments.save_appointments(sample_appointments)
        
        # Load data directly using json.load and verify
        with open(self.test_data_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 2)
        self.assertEqual(saved_data, sample_appointments)

        # Test saving an empty list
        appointments.save_appointments([])
        with open(self.test_data_file, 'r') as f:
            saved_data_empty = json.load(f)
        self.assertEqual(saved_data_empty, [])

if __name__ == '__main__':
    # This allows running the tests directly from this file
    # It's better to run with `python -m unittest discover ...` from project root
    unittest.main()
