from .appointments import add_appointment, get_appointments_on_date, load_appointments # 用于设置提醒时加载数据
from .reminders import set_reminder, check_reminders
from datetime import datetime # 输入校验与格式化

def print_appointment(appt: dict):
    """辅助函数：统一格式打印约会详情"""
    print(f"  ID: {appt.get('id')}")
    print(f"  Title: {appt.get('title')}")
    print(f"  Date: {appt.get('date')}")
    print(f"  Time: {appt.get('time')}")
    print(f"  Location: {appt.get('location', 'N/A')}")
    print(f"  Description: {appt.get('description', 'N/A')}")
    print(f"  Reminder Set: {'Yes' if appt.get('reminder_set') else 'No'}")
    if appt.get('reminder_set'):
        print(f"  Reminder Time: {appt.get('reminder_time')}")
    print("-" * 20)

def handle_add_appointment():
    """处理新增约会"""
    print("\n--- Add New Appointment ---")
    title = input("Enter appointment title: ")
    while not title:
        print("Title cannot be empty.")
        title = input("Enter appointment title: ")

    date_str = input("Enter date (YYYY-MM-DD): ")
    # 基本日期格式校验
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    time_str = input("Enter time (HH:MM): ")
    # 基本时间格式校验
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        print("Invalid time format. Please use HH:MM.")
        return
        
    location = input("Enter location (optional): ")
    description = input("Enter description (optional): ")

    new_appt = add_appointment(title, date_str, time_str, description, location)
    print("\nAppointment added successfully:")
    print_appointment(new_appt)

def handle_view_appointments():
    """查看指定日期的约会"""
    print("\n--- View Appointments for a Date ---")
    date_str = input("Enter date to view (YYYY-MM-DD): ")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    appointments_on_date = get_appointments_on_date(date_str)
    if appointments_on_date:
        print(f"\nAppointments on {date_str}:")
        for appt in appointments_on_date:
            print_appointment(appt)
    else:
        print(f"No appointments found on {date_str}.")

def handle_set_reminder():
    """为约会设置提醒"""
    print("\n--- Set Reminder for an Appointment ---")
    # 展示现有约会供用户选择 ID
    all_appointments = load_appointments()
    if not all_appointments:
        print("No appointments available to set reminders for.")
        return
        
    print("Available appointments:")
    for appt in all_appointments:
        print(f"  ID: {appt['id']}, Title: {appt['title']}, Date: {appt['date']}, Time: {appt['time']}")
    
    appointment_id = input("Enter appointment ID to set reminder for: ")
    if not any(appt['id'] == appointment_id for appt in all_appointments):
        print("Invalid appointment ID.")
        return

    reminder_datetime_str = input("Enter reminder date and time (YYYY-MM-DD HH:MM): ")
    try:
        # 校验提醒时间格式
        reminder_dt_obj = datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M")
        
        # 可选：检查提醒时间是否早于约会时间
        selected_appt = next((appt for appt in all_appointments if appt['id'] == appointment_id), None)
        if selected_appt:
            appointment_dt_str = f"{selected_appt['date']} {selected_appt['time']}"
            appointment_dt_obj = datetime.strptime(appointment_dt_str, "%Y-%m-%d %H:%M")
            if reminder_dt_obj >= appointment_dt_obj:
                print("Reminder time must be before the appointment time. Please try again.")
                return
        else: # 理论上不会发生，作为安全检查
            print("Could not retrieve appointment details for validation.")
            return

    except ValueError:
        print("Invalid datetime format for reminder. Please use YYYY-MM-DD HH:MM.")
        return

    if set_reminder(appointment_id, reminder_datetime_str):
        print("Reminder set successfully!")
        # 显示更新后的约会信息
        updated_appointments = load_appointments()
        for appt in updated_appointments:
            if appt['id'] == appointment_id:
                print("\nUpdated appointment details:")
                print_appointment(appt)
                break
    else:
        print("Failed to set reminder. Ensure the appointment ID is correct and datetime format is valid.")

def handle_check_reminders():
    """检查并显示到期提醒"""
    print("\n--- Check Due Reminders ---")
    due_reminders = check_reminders()
    if due_reminders:
        print(f"You have {len(due_reminders)} due reminder(s):")
        for appt in due_reminders:
            print(f"\nREMINDER: Appointment '{appt.get('title')}' at {appt.get('date')} {appt.get('time')}")
            print_appointment(appt)
    else:
        print("No reminders are currently due.")

def main_cli():
    """主命令行循环"""
    print("Welcome to the Calendar Reminder Service!")
    while True:
        print("\nMenu:")
        print("1. Add new appointment")
        print("2. View appointments for a date")
        print("3. Set a reminder for an appointment")
        print("4. Check for due reminders")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            handle_add_appointment()
        elif choice == '2':
            handle_view_appointments()
        elif choice == '3':
            handle_set_reminder()
        elif choice == '4':
            handle_check_reminders()
        elif choice == '5':
            print("Exiting Calendar Reminder Service. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main_cli()
