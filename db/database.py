"""SQLite database layer for caching, audit logs, and delta tracking."""
import sqlite3
import os
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """Manages SQLite database for transfer order records and audit trails."""

    def __init__(self, db_path: str = None):
        if not db_path:
            db_path = os.path.join(r"C:\Saikumar\Projects\PDF Consolidator", "data", "consolidator.db")
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_schema()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS consignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consignment_code TEXT UNIQUE,
                    store_name TEXT,
                    destination TEXT,
                    dispatch_date TEXT,
                    total_bags INTEGER,
                    total_pieces INTEGER,
                    total_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consignment_id INTEGER,
                    order_number TEXT UNIQUE,
                    order_date TEXT,
                    source_warehouse TEXT,
                    destination_warehouse TEXT,
                    total_quantity INTEGER,
                    grand_total REAL,
                    file_path TEXT,
                    FOREIGN KEY(consignment_id) REFERENCES consignments(id)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    def log_action(self, action: str, details: str):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", (action, details))
            conn.commit()
