"""bg-scratch singleton: a heartbeat row every 2 s in the same SQLite file as app.py.

Two copies running at once would write twice as many beats: the rehearsal (case G9) counts
running copies, never rows.
"""
import os
import socket
import sqlite3
import time

conn = sqlite3.connect(os.environ.get("BGS_DB", "/data/app.db"), timeout=5)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("CREATE TABLE IF NOT EXISTS beats (ts REAL, hostname TEXT)")
conn.commit()
while True:
    conn.execute("INSERT INTO beats VALUES (?, ?)", (time.time(), socket.gethostname()))
    conn.commit()
    time.sleep(2)
