# 日程提醒服务示例项目

此仓库包含一个简易的命令行日程提醒应用，完整代码位于 `calendar_reminder_service/` 目录。

主要功能包括：

* 新增约会，可指定标题、日期、时间、地点以及描述。
* 查看某一天的约会清单。
* 为约会设置提醒时间并检查到期提醒。

## 快速开始

1. 进入程序目录并执行主程序：
   ```bash
   cd calendar_reminder_service/src
   python app.py
   ```
   根据界面提示即可管理日程与提醒。

2. 启动簡易 API 服務（可選）：
   ```bash
   python -m calendar_reminder_service.src.api_server
   ```
   服務啟動後，可通過 HTTP 請求管理約會和提醒。
   更詳細的接口示例請參見 `API_GUIDE.md`。

## 运行单元测试

在项目根目录下执行：
```bash
python -m unittest discover calendar_reminder_service/tests
```

本项目仅依赖 Python 标准库，所有数据存储在 `calendar_reminder_service/data/appointments.json`。
