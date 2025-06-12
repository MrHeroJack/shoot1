# API 使用指南

本文档介绍如何通过 HTTP 接口操作日程提醒服务。

## 启动 API 服务器

在项目根目录下执行以下命令：
```bash
cd calendar_reminder_service/src
python -m calendar_reminder_service.src.api_server
```
服务器默认监听 `0.0.0.0:8000`，启动后即可发送请求。

## 接口列表

### 获取所有约会
`GET /api/appointments`

返回 JSON 格式的约会列表。

### 根据日期查询约会
`GET /api/appointments?date=YYYY-MM-DD`

传入 `date` 参数可只获取指定日期的约会。

示例：
```bash
curl "http://localhost:8000/api/appointments?date=2025-01-01"
```

### 新增约会
`POST /api/appointments`

请求体为 JSON，必须包含 `title`、`date`、`time`，可选字段有 `description` 和 `location`。

示例：
```bash
curl -X POST http://localhost:8000/api/appointments \
     -H "Content-Type: application/json" \
     -d '{"title": "会议", "date": "2025-01-02", "time": "15:00", "location": "会议室"}'
```

成功时返回新建的约会对象。

### 为约会设置提醒
`POST /api/reminders`

请求体需包含 `appointment_id` 与 `reminder_time`（格式 `YYYY-MM-DD HH:MM`）。

示例：
```bash
curl -X POST http://localhost:8000/api/reminders \
     -H "Content-Type: application/json" \
     -d '{"appointment_id": "<ID>", "reminder_time": "2025-01-02 14:00"}'
```

返回 `{"status": "ok"}` 表示设置成功。

### 查看到期提醒
`GET /api/reminders/due`

返回已到提醒时间、但约会尚未开始的约会列表。

## 其他说明

本服务仅用于演示，未做用户认证及错误处理等高级功能，可按需拓展。
