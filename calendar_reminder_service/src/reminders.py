from datetime import datetime
from .appointments import load_appointments, save_appointments, DATA_FILE # 测试时需要 DATA_FILE
import os # 用于测试

def set_reminder(appointment_id: str, reminder_datetime_str: str) -> bool:
    """
    为指定的约会设置提醒。

    参数:
        appointment_id (str): 需要设置提醒的约会 ID。
        reminder_datetime_str (str): 提醒时间，格式为 "YYYY-MM-DD HH:MM"。

    返回值:
        bool: 设置成功返回 True，否则为 False。
    """
    appointments = load_appointments()
    appointment_found = False
    for appt in appointments:
        if appt.get("id") == appointment_id:
            try:
                # 校验提醒时间格式
                datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M")
                appt["reminder_time"] = reminder_datetime_str
                appt["reminder_set"] = True
                appointment_found = True
                break
            except ValueError:
                # 时间格式不正确
                return False
    
    if appointment_found:
        save_appointments(appointments)
        return True
    return False

def check_reminders() -> list:
    """
    检查提醒时间已到的约会。

    返回值:
        list: 需要提醒的约会字典列表。
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

                # 如果提醒时间已过而约会时间未过，则加入待提醒列表
                if reminder_time_obj <= now and appointment_time_obj >= now:
                    due_reminders.append(appt)
                # 如有需要可以增加更老的提醒条件或约会已过期的情况
                # 目前只检查 reminder_time 是否已过
                # 简单的检查例如：
                # if reminder_time_obj <= now:
                #     due_reminders.append(appt)

            except ValueError:
                # 存储数据格式不正确，跳过该约会
                continue
    return due_reminders

if __name__ == '__main__':
    # 初始化：确保测试时数据文件为空
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    
    # 通过 appointments.py 中的函数添加测试数据
    from .appointments import add_appointment

    print("Initial appointments:", load_appointments())

    # 添加一些约会
    appt1 = add_appointment("Dentist Checkup", "2024-08-15", "09:00", "Routine cleaning.")
    appt2 = add_appointment("Project Deadline", "2024-08-10", "17:00", "Submit phase 1.")
    appt3 = add_appointment("Birthday Party", "2024-08-12", "18:00", "Alice's birthday.")
    
    print(f"Appointments after adding: {load_appointments()}")

    # 设置提醒
    print("\n--- Setting Reminders ---")
    # 给 appt1（牙医）设置有效提醒
    reminder_dt_appt1 = (datetime.strptime(appt1['date'] + ' ' + appt1['time'], "%Y-%m-%d %H:%M") - \
                         timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
    print(f"Setting reminder for appt1 ({appt1['id']}) at {reminder_dt_appt1}")
    if set_reminder(appt1["id"], reminder_dt_appt1):
        print(f"Reminder set for appt1: {load_appointments()}")
    else:
        print(f"Failed to set reminder for appt1.")

    # 给 appt2（项目）设置提醒，时间设在过去以测试 check_reminders
    past_reminder_time = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    print(f"Setting reminder for appt2 ({appt2['id']}) at {past_reminder_time} (this should be due)")
    if set_reminder(appt2["id"], past_reminder_time):
        print(f"Reminder set for appt2: {load_appointments()}")
    else:
        print(f"Failed to set reminder for appt2.")

    # 给 appt3（生日）设置未来的提醒
    future_reminder_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    # 确保提醒时间早于事件发生时间
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


    # 尝试为不存在的约会设置提醒
    print(f"\nAttempting to set reminder for non-existent ID 'invalid-id':")
    if not set_reminder("invalid-id", "2024-08-01 10:00"):
        print("Correctly failed to set reminder for non-existent appointment.")
    
    # 尝试使用无效的时间格式设置提醒
    print(f"\nAttempting to set reminder for appt1 with invalid datetime format:")
    if not set_reminder(appt1["id"], "2024/08/15 10am"):
        print(f"Correctly failed to set reminder with invalid format. Current appt1: {[a for a in load_appointments() if a['id'] == appt1['id']][0]}")


    # 检查到期提醒
    print("\n--- Checking Reminders ---")
    # 引入 timedelta 以便定义测试场景
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

    # 情景：约会已过期，提醒也在过去
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

    # 情景：未来的约会但提醒时间在过去，且提醒时间晚于约会时间（边界情况）
    print("\n--- Test: Future Appointment, Reminder in Past (but after appointment time) ---")
    # 正常情况下不应出现此情况，因为提醒应设置在事件之前
    # 但 check_reminders 应在 appointment_time < reminder_time_obj 时忽略它
    # 因此手动构造提醒晚于事件时间的约会来测试
    # 现有 set_reminder 函数无法做到这一点，只能直接修改数据
    
    # 先创建一条有效约会
    edge_appt = add_appointment("Edge Case Event", "2024-09-01", "10:00")
    # 手动设置一个晚于事件但相对现在已过去的提醒时间
    # 目的是测试 `appointment_time_obj >= now` 的逻辑
    # 假设当前时间为 2024-08-15
    # 事件：2024-09-01 10:00，提醒：2024-08-14 10:00（已过，应触发）
    # 但检查条件是 appointment_time_obj >= now
    # 假设当前是 2024-09-02 12:00（事件已过）
    # 提醒时间为 2024-09-01 08:00（在事件之前，但事件已过去）
    
    # 通过直接修改数据来模拟上述情况
    all_appts = load_appointments()
    for a in all_appts:
        if a['id'] == edge_appt['id']:
            a['reminder_set'] = True
            # 提醒时间早于事件，但假设当前时间已晚于事件
            a['reminder_time'] = (datetime.strptime(a['date'] + ' ' + a['time'], "%Y-%m-%d %H:%M") - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M") # 例：2024-09-01 08:00
            # 若要完全模拟事件已过，需要在 check_reminders 中控制当前时间
            # 或直接使用实际过去的事件，"Old Event" 测试更清楚
            break
    save_appointments(all_appts)
    # 由于依赖真实当前时间，此测试稍显复杂
    # "Old Event" 测试更能说明事件已过期的情况
    # 现有逻辑 `reminder_time_obj <= now and appointment_time_obj >= now`
    # 意味着若约会时间已过去则不会提示

    print(f"\nFinal appointments state: {load_appointments()}")
