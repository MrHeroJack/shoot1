# 基于 http.server 的简易 API 服务
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
from .appointments import add_appointment, get_appointments_on_date, load_appointments
from .reminders import set_reminder, check_reminders


class SimpleAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        response = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/appointments':
            query = parse_qs(parsed.query)
            date = query.get('date', [None])[0]
            if date:
                data = get_appointments_on_date(date)
            else:
                data = load_appointments()
            self._send_json(data)
        elif parsed.path == '/api/reminders/due':
            data = check_reminders()
            self._send_json(data)
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON'}, 400)
            return

        if parsed.path == '/api/appointments':
            required = {'title', 'date', 'time'}
            if not required.issubset(data):
                self._send_json({'error': 'Missing fields'}, 400)
                return
            new_appt = add_appointment(
                data['title'],
                data['date'],
                data['time'],
                data.get('description', ''),
                data.get('location', '')
            )
            self._send_json(new_appt, 201)
        elif parsed.path == '/api/reminders':
            if 'appointment_id' not in data or 'reminder_time' not in data:
                self._send_json({'error': 'Missing fields'}, 400)
                return
            success = set_reminder(data['appointment_id'], data['reminder_time'])
            if success:
                self._send_json({'status': 'ok'})
            else:
                self._send_json({'error': 'Failed to set reminder'}, 400)
        else:
            self._send_json({'error': 'Not Found'}, 404)


def run(server_class=HTTPServer, handler_class=SimpleAPIHandler, host='0.0.0.0', port=8000):
    server = server_class((host, port), handler_class)
    print(f"API server listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    run()
