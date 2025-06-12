import json
import uuid
import os

# 确定数据文件的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "calendar_reminder_service", "data", "appointments.json")

def load_appointments() -> list:
    """
    从 JSON 文件加载约会信息。

    返回值:
        list: 约会字典的列表。如果文件不存在或者无数据或 JSON 格式错误，则返回空列表。
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
    将约会列表保存到 JSON 文件。

    参数:
        appointments (list): 将要保存的约会字典列表。
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(appointments, f, indent=4)

def add_appointment(title: str, date: str, time: str, description: str = "", location: str = "") -> dict:
    """
    新增一条约会并保存。

    参数:
        title (str): 约会标题。
        date (str): 约会日期（如 "YYYY-MM-DD"）。
        time (str): 约会时间（如 "HH:MM"）。
        description (str, optional): 约会描述，默认为空。
        location (str, optional): 约会地点，默认为空。

    返回值:
        dict: 新建约会的字典。
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
        "location": location,
    }
    appointments.append(new_appointment)
    save_appointments(appointments)
    return new_appointment

def get_appointments_on_date(date: str) -> list:
    """
    获取指定日期的所有约会。

    参数:
        date (str): 用于过滤约会的日期（如 "YYYY-MM-DD"）。

    返回值:
        list: 对应日期的约会列表。
    """
    appointments = load_appointments()
    return [appt for appt in appointments if appt.get("date") == date]

if __name__ == '__main__':
    # 简单的测试用例
    print("Initial appointments:", load_appointments())

    # 添加一条约会
    added_appt = add_appointment("Team Meeting", "2024-07-30", "10:00", "Discuss Q3 goals.")
    print("Added appointment:", added_appt)
    print("Appointments after adding:", load_appointments())

    added_appt_2 = add_appointment("Doctor's Visit", "2024-07-30", "14:30", "Annual check-up.")
    print("Added another appointment:", added_appt_2)
    print("Appointments after adding second appointment:", load_appointments())

    # 获取指定日期的约会
    appointments_on_date = get_appointments_on_date("2024-07-30")
    print(f"Appointments on 2024-07-30: {appointments_on_date}")

    appointments_on_another_date = get_appointments_on_date("2024-07-31")
    print(f"Appointments on 2024-07-31: {appointments_on_another_date}")

    # 测试保存空列表
    save_appointments([])
    print("Appointments after clearing (should be empty):", load_appointments())

    # 如有需要再次添加约会以供后续测试
    added_appt_3 = add_appointment("Lunch with Alex", "2024-08-01", "12:00")
    print("Appointments after adding one back:", load_appointments())
    print("Details of the last added appointment:", added_appt_3)
