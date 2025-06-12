# 日程提醒服务

一个用于管理约会和提醒的简易命令行应用。

## 功能

*   新增约会（标题、日期、时间、地点及描述）。
*   查看指定日期的约会。
*   为约会设置在指定时间的提醒。
*   检查哪些提醒已到期。
*   所有约会数据保存在本地 JSON 文件 `data/appointments.json` 中。

## 项目结构

```
calendar_reminder_service/
├── data/
│   └── appointments.json       # Storage for appointment data
├── src/
│   ├── __init__.py
│   ├── app.py                  # 主命令行入口
│   ├── appointments.py         # 约会管理逻辑
│   ├── calendar_utils.py       # 预留的日历工具模块
│   └── reminders.py            # 提醒管理逻辑
├── tests/
│   ├── __init__.py
│   ├── test_appointments.py    # 约会单元测试
│   └── test_reminders.py       # 提醒单元测试
└── README.md                   # This file
```

## 环境要求

*   Python 3.x

## 安装

除安装 Python 3 外无需额外配置，项目仅依赖标准库。

## 如何运行

1.  进入 `src` 目录：
    ```bash
    cd calendar_reminder_service/src
    ```
2.  执行主程序：
    ```bash
    python app.py
    ```
    运行后即可通过命令行与服务交互。

## 如何运行单元测试

1.  进入项目根目录 (`calendar_reminder_service/`)
2.  运行以下命令执行全部测试：
    ```bash
    python -m unittest discover tests
    ```
    或执行指定测试文件：
    ```bash
    python -m unittest tests.test_appointments
    python -m unittest tests.test_reminders
    ```

## 未来可扩展方向（示例）

*   使用数据库（如 SQLite）进行持久化存储。
*   提供邮件或系统通知等更丰富的提醒方式。
*   支持周期性约会。
*   提供基于 Flask/Django 的网页界面。
*   日历视图展示。
```
