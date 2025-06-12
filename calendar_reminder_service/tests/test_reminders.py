import unittest
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch

# 假设在项目根目录运行：`python -m unittest discover calendar_reminder_service/tests`
from calendar_reminder_service.src import reminders
from calendar_reminder_service.src import appointments # 用于测试数据的创建

class TestReminders(unittest.TestCase):

    def setUp(self):
        # 在 tests 目录下创建用于测试数据的子目录
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # 使用不同的数据文件避免并行运行时冲突（unittest 通常串行）
        self.test_reminders_data_file = os.path.join(self.test_data_dir, "test_reminders_appointments.json")

        # 将 appointments 模块中的 DATA_FILE 指向测试文件，供 appointments 与 reminders 使用
        self.data_file_patcher = patch('calendar_reminder_service.src.appointments.DATA_FILE', self.test_reminders_data_file)
        self.mock_data_file = self.data_file_patcher.start()

        # 在每个测试开始前保存空列表清理文件
        appointments.save_appointments([])

    def tearDown(self):
        self.data_file_patcher.stop()
        if os.path.exists(self.test_reminders_data_file):
            os.remove(self.test_reminders_data_file)
        if os.path.exists(self.test_data_dir) and not os.listdir(self.test_data_dir):
            os.rmdir(self.test_data_dir)

    def test_set_reminder_success(self):
        # 新增一条约会
        appt = appointments.add_appointment("Test Event for Reminder", "2024-09-01", "10:00")
        self.assertFalse(appt["reminder_set"]) # 初始状态为 False

        reminder_time_str = "2024-09-01 08:00"
        result = reminders.set_reminder(appt["id"], reminder_time_str)
        self.assertTrue(result)

        # 加载约会并检查
        updated_appts = appointments.load_appointments()
        found_appt = next((a for a in updated_appts if a["id"] == appt["id"]), None)
        
        self.assertIsNotNone(found_appt)
        self.assertTrue(found_appt["reminder_set"])
        self.assertEqual(found_appt["reminder_time"], reminder_time_str)

    def test_set_reminder_invalid_datetime_format(self):
        appt = appointments.add_appointment("Test Event Format", "2024-09-02", "10:00")
        result = reminders.set_reminder(appt["id"], "2024/09/02 08:00AM") # 时间格式无效
        self.assertFalse(result)
        updated_appts = appointments.load_appointments()
        found_appt = next((a for a in updated_appts if a["id"] == appt["id"]), None)
        self.assertFalse(found_appt["reminder_set"]) # 状态不应改变

    def test_set_reminder_non_existent_appointment(self):
        result = reminders.set_reminder("non-existent-id", "2024-09-01 08:00")
        self.assertFalse(result)

    def test_check_reminders(self):
        # 定义多个模拟当前时间以测试不同场景
        mock_now_past_all = datetime(2024, 1, 1, 10, 0, 0) # 很早以前的时间
        mock_now_due_for_appt1 = datetime(2024, 8, 15, 13, 0, 0) # appt1 的提醒应到期，事件仍在未来
        mock_now_after_appt1_reminder_before_event = datetime(2024, 8, 15, 15, 0, 0) # 提醒已过但事件未到
        mock_now_after_appt1_event = datetime(2024, 8, 16, 10, 0, 0) # appt1 事件已过去
        mock_now_before_any_reminders = datetime(2024, 8, 1, 12, 0, 0)


        # 场景1：约会在未来，提醒时间在过去（应到期）
        appt1 = appointments.add_appointment("Future Event, Past Reminder", "2024-08-15", "14:00") # 事件时间
        reminders.set_reminder(appt1["id"], "2024-08-15 12:00") # 提前两小时

        # 场景2：约会在未来，提醒时间也在未来（不应到期）
        appt2 = appointments.add_appointment("Future Event, Future Reminder", "2024-08-20", "10:00")
        reminders.set_reminder(appt2["id"], "2024-08-20 08:00") # appt2 的提醒

        # 场景3：约会和提醒均在过去（不应到期）
        appt3 = appointments.add_appointment("Past Event, Past Reminder", "2024-07-01", "10:00") # 事件时间
        reminders.set_reminder(appt3["id"], "2024-07-01 08:00") # 提醒时间

        # 场景4：设置了提醒但提醒时间为空（不应报错，也不应到期）
        appt4 = appointments.add_appointment("Event No Reminder Time", "2024-08-25", "11:00")
        # 手动修改数据使 reminder_set=True 但 reminder_time 为空（set_reminder 正常情况下不会这样）
        loaded_appts = appointments.load_appointments()
        for a in loaded_appts:
            if a['id'] == appt4['id']:
                a['reminder_set'] = True
                a['reminder_time'] = "" # Explicitly empty
        appointments.save_appointments(loaded_appts)


        # --- 使用 mock_now_due_for_appt1 测试 ---
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_due_for_appt1
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs) # 保持 strptime 正常

            due = reminders.check_reminders()
            self.assertEqual(len(due), 1)
            self.assertEqual(due[0]["id"], appt1["id"])

        # --- 使用 mock_now_before_any_reminders 测试 ---
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_before_any_reminders
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            due = reminders.check_reminders()
            self.assertEqual(len(due), 0)

        # --- 使用 mock_now_after_appt1_event 测试 ---
        # （appt1 的提醒已到，但事件也已过去）
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_after_appt1_event
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)
            
            due = reminders.check_reminders()
            # appt1 的事件已过，因此不应提示
            self.assertFalse(any(d["id"] == appt1["id"] for d in due))
            self.assertEqual(len(due), 0) # Assuming appt2, appt3 also not due

        # --- 使用 mock_now_past_all 测试（更直接覆盖 appt3 情况） ---
        with patch('calendar_reminder_service.src.reminders.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now_past_all # 非常早的时间
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)
            
            # 此时所有事件都在未来，因此不会有提醒到期
            # 与 "before_any_reminders" 类似，用于验证在早于所有事件和提醒的时间点逻辑仍然成立
            due = reminders.check_reminders()
            self.assertEqual(len(due), 0)


if __name__ == '__main__':
    unittest.main()
