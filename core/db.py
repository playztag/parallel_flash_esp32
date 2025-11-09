"""Database management for tracking flash operations."""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import csv


class FlashDatabase:
    """SQLite database for tracking flash operations and metrics."""

    def __init__(self, db_path: str = "static/flash_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database with required tables."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flash_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                port TEXT NOT NULL,
                mac TEXT,
                chip_type TEXT,
                status TEXT NOT NULL,
                duration REAL,
                firmware TEXT,
                log_path TEXT,
                error_msg TEXT
            )
        """)
        self.conn.commit()

    def add_record(
        self,
        port: str,
        status: str,
        mac: Optional[str] = None,
        chip_type: Optional[str] = None,
        duration: Optional[float] = None,
        firmware: Optional[str] = None,
        log_path: Optional[str] = None,
        error_msg: Optional[str] = None
    ) -> int:
        """Add a flash operation record."""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO flash_history
            (timestamp, port, mac, chip_type, status, duration, firmware, log_path, error_msg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, port, mac, chip_type, status, duration, firmware, log_path, error_msg))

        self.conn.commit()
        return cursor.lastrowid

    def get_recent_records(self, limit: int = 100) -> List[Dict]:
        """Get recent flash records."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM flash_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self, since: Optional[datetime] = None) -> Dict:
        """Get flash statistics."""
        cursor = self.conn.cursor()

        if since:
            query = "SELECT status, COUNT(*) as count FROM flash_history WHERE timestamp >= ? GROUP BY status"
            cursor.execute(query, (since.isoformat(),))
        else:
            query = "SELECT status, COUNT(*) as count FROM flash_history GROUP BY status"
            cursor.execute(query)

        stats = {row['status']: row['count'] for row in cursor.fetchall()}

        return {
            'success': stats.get('success', 0),
            'fail': stats.get('fail', 0),
            'total': sum(stats.values())
        }

    def export_to_csv(self, output_path: str, since: Optional[datetime] = None) -> None:
        """Export records to CSV file."""
        cursor = self.conn.cursor()

        if since:
            cursor.execute("""
                SELECT * FROM flash_history
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (since.isoformat(),))
        else:
            cursor.execute("SELECT * FROM flash_history ORDER BY timestamp DESC")

        rows = cursor.fetchall()
        if not rows:
            return

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows([dict(row) for row in rows])

    def reset_statistics(self) -> None:
        """Clear all flash history records."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM flash_history")
        self.conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
