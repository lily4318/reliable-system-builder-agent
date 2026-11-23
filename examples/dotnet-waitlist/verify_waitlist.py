"""Run against a previously built Debug Waitlist project using .NET 9."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json
import os
import queue
import re
import sqlite3
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parent
DLL = ROOT / "bin" / "Debug" / os.environ.get("WAITLIST_TARGET_FRAMEWORK", "net9.0") / "Waitlist.dll"


class WaitlistHttpTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(DLL.is_file(), "Build Waitlist.csproj before running the tests")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        database = Path(temporary.name) / "synthetic.sqlite"
        self.db = sqlite3.connect(database)
        self.addCleanup(self.db.close)
        self.db.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))
        self.db.executemany("INSERT INTO booking VALUES (?, ?, ?, ?, ?)", [
            (1, 1, 1, 1, "confirmed"),
            (2, 1, 2, 0, "waiting"),
            (3, 1, 4, 1, "waiting"),
            (4, 1, 3, 1, "waiting"),
            (5, 1, 3, 1, "waiting"),
            (6, 2, 1, 1, "confirmed"),
            (7, 2, 2, 0, "waiting"),
        ])
        self.db.commit()
        process = subprocess.Popen(
            ["dotnet", str(DLL), "--WaitlistDatabase", str(database)],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
        address = queue.Queue()

        def read_logs():
            for line in process.stdout:
                match = re.search(r"Now listening on: (http://127\.0\.0\.1:\d+)", line)
                if match:
                    address.put(match[1])
            address.put(None)

        reader = threading.Thread(target=read_logs, daemon=True)
        reader.start()

        def stop():
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            reader.join(timeout=5)
            process.stdout.close()

        self.addCleanup(stop)
        self.base = address.get(timeout=20)
        self.assertIsNotNone(self.base, "Waitlist server exited before listening")

    def cancel(self, booking_id):
        request = Request(f"{self.base}/bookings/{booking_id}/cancel", method="POST")
        try:
            with urlopen(request, timeout=10) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            with error:
                return error.code, None

    def bookings(self):
        return self.db.execute("SELECT id, status FROM booking ORDER BY id").fetchall()

    def receipts(self):
        return self.db.execute("SELECT * FROM cancellation ORDER BY booking_id").fetchall()

    def test_promotes_eligible_fifo_tiebreak_and_replays(self):
        self.assertEqual(self.cancel(1), (200, {"promotedBookingId": 4}))
        self.assertEqual(self.cancel(1), (200, {"promotedBookingId": 4}))
        self.assertEqual(self.receipts(), [(1, 4)])
        self.assertEqual(self.bookings(), [
            (1, "cancelled"), (2, "waiting"), (3, "waiting"), (4, "confirmed"),
            (5, "waiting"), (6, "confirmed"), (7, "waiting"),
        ])

    def test_no_eligible_candidate_and_replay(self):
        self.assertEqual(self.cancel(6), (200, {"promotedBookingId": None}))
        self.assertEqual(self.cancel(6), (200, {"promotedBookingId": None}))
        self.assertEqual(self.receipts(), [(6, None)])
        self.assertEqual(self.bookings()[-2:], [(6, "cancelled"), (7, "waiting")])

    def test_invalid_missing_and_nonconfirmed_leave_database_unchanged(self):
        before = self.bookings()
        self.assertEqual(self.cancel(0)[0], 400)
        self.assertEqual(self.cancel(999)[0], 404)
        self.assertEqual(self.cancel(2)[0], 409)
        self.assertEqual(self.bookings(), before)
        self.assertEqual(self.receipts(), [])

    def test_concurrent_duplicate_requests_promote_once(self):
        start = Barrier(2)

        def cancel_together():
            start.wait(timeout=5)
            return self.cancel(1)

        with ThreadPoolExecutor(max_workers=2) as workers:
            requests = [workers.submit(cancel_together) for _ in range(2)]
            self.assertEqual([request.result() for request in requests],
                             [(200, {"promotedBookingId": 4})] * 2)
        self.assertEqual(self.receipts(), [(1, 4)])
        self.assertEqual(self.bookings()[1:5],
                         [(2, "waiting"), (3, "waiting"), (4, "confirmed"), (5, "waiting")])

    def test_late_write_failure_rolls_back_and_retry_succeeds(self):
        before = self.bookings()
        self.db.executescript("""
            CREATE TRIGGER reject_receipt BEFORE INSERT ON cancellation
            BEGIN SELECT RAISE(ABORT, 'synthetic receipt failure'); END;
        """)
        self.assertEqual(self.cancel(1)[0], 500)
        self.assertEqual(self.bookings(), before)
        self.assertEqual(self.receipts(), [])
        self.db.execute("DROP TRIGGER reject_receipt")
        self.assertEqual(self.cancel(1), (200, {"promotedBookingId": 4}))
        self.assertEqual(self.receipts(), [(1, 4)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
