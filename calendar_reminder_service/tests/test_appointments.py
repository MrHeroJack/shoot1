import unittest
import os
import json
from unittest.mock import patch

# 假设在项目根目录运行：`python -m unittest discover calendar_reminder_service/tests`
# 即 'calendar_reminder_service' 为顶层包
from calendar_reminder_service.src import appointments

class TestAppointments(unittest.TestCase):

    def setUp(self):
        # 在 tests 目录下创建用于测试数据的子目录
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        self.test_data_file = os.path.join(self.test_data_dir, "test_appointments.json")

        # 将 appointments 模块中的 DATA_FILE 指向测试文件
        self.data_file_patcher = patch('calendar_reminder_service.src.appointments.DATA_FILE', self.test_data_file)
        self.mock_data_file = self.data_file_patcher.start()

        # 每个测试前清理测试数据文件
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        with open(self.test_data_file, 'w') as f:
            json.dump([], f)

    def tearDown(self):
        # 停止补丁
        self.data_file_patcher.stop()
        # 测试后清理测试数据文件
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        if os.path.exists(self.test_data_dir) and not os.listdir(self.test_data_dir):
            os.rmdir(self.test_data_dir)


    def test_add_appointment(self):
        # 添加一条约会
        added_appt = appointments.add_appointment("Test Event", "2024-01-01", "10:00", "Test Description")
        
        # 验证返回的约会
        self.assertEqual(added_appt["title"], "Test Event")
        self.assertEqual(added_appt["date"], "2024-01-01")
        self.assertEqual(added_appt["time"], "10:00")
        self.assertEqual(added_appt["description"], "Test Description")
        self.assertIn("id", added_appt)
        self.assertFalse(added_appt["reminder_set"]) # 默认未设置提醒
        self.assertEqual(added_appt["reminder_time"], "")
        self.assertEqual(added_appt["location"], "")

        # 直接从测试文件加载数据并验证
        with open(self.test_data_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Test Event")
        self.assertEqual(data[0]["id"], added_appt["id"])

    def test_get_appointments_on_date(self):
        # 添加几条约会
        appt1 = appointments.add_appointment("Event 1", "2024-01-01", "10:00")
        appt2 = appointments.add_appointment("Event 2", "2024-01-02", "11:00")
        appt3 = appointments.add_appointment("Event 3", "2024-01-01", "12:00")

        # 测试同一日期有多条约会的情况
        on_date_01 = appointments.get_appointments_on_date("2024-01-01")
        self.assertEqual(len(on_date_01), 2)
        self.assertTrue(any(a["id"] == appt1["id"] for a in on_date_01))
        self.assertTrue(any(a["id"] == appt3["id"] for a in on_date_01))

        # 测试某日期只有一条约会
        on_date_02 = appointments.get_appointments_on_date("2024-01-02")
        self.assertEqual(len(on_date_02), 1)
        self.assertEqual(on_date_02[0]["id"], appt2["id"])

        # 测试无约会的日期
        on_date_03 = appointments.get_appointments_on_date("2024-01-03")
        self.assertEqual(len(on_date_03), 0)

    def test_load_appointments(self):
        # 1. 测试从不存在的文件加载
        #    setUp 会创建空文件，因此此处先删除再加载
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        loaded_from_non_existent = appointments.load_appointments()
        self.assertEqual(loaded_from_non_existent, [])
        # 如需其他测试可重新创建，或依赖下次 setUp
        with open(self.test_data_file, 'w') as f:
            json.dump([], f)


        # 2. 测试从内容为 "[]" 的文件加载
        with open(self.test_data_file, 'w') as f:
            json.dump([], f)
        loaded_from_empty_list = appointments.load_appointments()
        self.assertEqual(loaded_from_empty_list, [])

        # 3. 测试从真正空文件加载
        with open(self.test_data_file, 'w') as f:
            pass # 创建空文件
        loaded_from_truly_empty = appointments.load_appointments()
        self.assertEqual(loaded_from_truly_empty, [])


        # 4. 测试从包含有效 JSON 的文件加载
        sample_data = [
            {"id": "1", "title": "Event A", "date": "2024-02-01", "time": "13:00", "description": "", "reminder_set": False, "reminder_time": "", "location": ""},
            {"id": "2", "title": "Event B", "date": "2024-02-02", "time": "14:00", "description": "Desc", "reminder_set": True, "reminder_time": "2024-02-02 10:00", "location": "Room"}
        ]
        with open(self.test_data_file, 'w') as f:
            json.dump(sample_data, f)
        
        loaded_data = appointments.load_appointments()
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data, sample_data)

        # 5. 测试从包含非法 JSON 的文件加载
        with open(self.test_data_file, 'w') as f:
            f.write("this is not json")
        loaded_from_invalid = appointments.load_appointments()
        self.assertEqual(loaded_from_invalid, [])


    def test_save_appointments(self):
        sample_appointments = [
            {"id": "s1", "title": "Save Test 1", "date": "2024-03-01", "time": "15:00", "description": "Save Desc 1", "reminder_set": False, "reminder_time": "", "location": ""},
            {"id": "s2", "title": "Save Test 2", "date": "2024-03-02", "time": "16:00", "description": "Save Desc 2", "reminder_set": True, "reminder_time": "2024-03-02 12:00", "location": "Lab"}
        ]
        
        appointments.save_appointments(sample_appointments)
        
        # 使用 json.load 直接读取并验证
        with open(self.test_data_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 2)
        self.assertEqual(saved_data, sample_appointments)

        # 测试保存空列表
        appointments.save_appointments([])
        with open(self.test_data_file, 'r') as f:
            saved_data_empty = json.load(f)
        self.assertEqual(saved_data_empty, [])

if __name__ == '__main__':
    # 允许直接运行此文件中的测试
    # 更推荐在项目根目录使用 `python -m unittest discover ...`
    unittest.main()
