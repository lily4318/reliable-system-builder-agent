"""Local synthetic academic booking example with a durable simulated LINE receipt."""
import json
import sqlite3
from contextlib import closing
from urllib.parse import parse_qs

from src.b002_equipment import Equipment


class AcademicBooking:
    def __init__(self, directory):
        self.reservations = Equipment(directory / "reservations.sqlite3")
        self.receipts = directory / "notices.sqlite3"

    @classmethod
    def create(cls, directory):
        directory.mkdir()
        app = cls(directory)
        Equipment.create(app.reservations.path, stock=1)
        with closing(sqlite3.connect(app.receipts)) as db, db:
            db.execute("CREATE TABLE notifications (request TEXT PRIMARY KEY)")
        return app

    def notice(self, request):
        with closing(sqlite3.connect(self.receipts)) as db, db:
            db.execute("INSERT OR IGNORE INTO notifications VALUES (?)", (request,))

    def status(self, request):
        result = self.reservations.reconcile(request)
        uri = self.receipts.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as db:
            count, = db.execute(
                "SELECT COUNT(*) FROM notifications WHERE request=?", (request,)
            ).fetchone()
        return {**result, "synthetic_notice_count": count}

    def __call__(self, environ, start_response):
        path, method = environ["PATH_INFO"], environ["REQUEST_METHOD"]
        code, media = "200 OK", "application/json"
        try:
            if method == "GET" and path == "/":
                media = "text/html; charset=utf-8"
                body = (
                    '<!doctype html><html lang="zh-Hant"><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width, initial-scale=1">'
                    '<title>合成研究預約</title><h1>合成研究預約</h1>'
                    '<p>本機示範。使用合成預約代碼。</p>'
                    '<form action="/book" method="post">'
                    '<label>預約代碼 <input name="request" required maxlength="44"></label>'
                    '<button>預約測試場次</button></form></html>'
                ).encode("utf-8")
            elif method == "POST" and path == "/book":
                length = int(environ.get("CONTENT_LENGTH") or "0")
                if not 0 < length <= 256:
                    raise ValueError("invalid request size")
                raw = environ["wsgi.input"].read(length)
                fields = parse_qs(raw.decode("utf-8"), strict_parsing=True, max_num_fields=1)
                request, = fields["request"]
                result = self.reservations.reserve(request, 1)
                if result == "RESERVED":
                    try:
                        self.notice(request)
                    except sqlite3.OperationalError:
                        code = "503 Service Unavailable"
                else:
                    code = "409 Conflict"
                body = json.dumps(self.status(request)).encode("utf-8")
            elif method == "GET" and path == "/status":
                fields = parse_qs(environ.get("QUERY_STRING", ""), strict_parsing=True,
                                  max_num_fields=1)
                request, = fields["request"]
                body = json.dumps(self.status(request)).encode("utf-8")
            else:
                code, body = "404 Not Found", b'{"error":"route"}'
        except (ValueError, KeyError):
            code, body = "400 Bad Request", b'{"error":"invalid synthetic request"}'
        start_response(code, [("Content-Type", media), ("Content-Length", str(len(body)))])
        return [body]
