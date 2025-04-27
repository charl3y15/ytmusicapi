import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class LikeTracker:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'liked_songs.db')
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS liked_songs (
                    video_id TEXT,
                    liked_date TEXT,
                    PRIMARY KEY (video_id, liked_date)
                )
            ''')

    def update_likes(self, liked_songs: List[Dict]):
        """
        Add new liked songs to the database with the current date if not already present for that date.
        liked_songs: list of dicts with at least 'videoId' key
        """
        now = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            for song in liked_songs:
                video_id = song.get('videoId')
                if not video_id:
                    continue
                # Insert if not exists for this date
                conn.execute('''
                    INSERT OR IGNORE INTO liked_songs (video_id, liked_date)
                    VALUES (?, ?)
                ''', (video_id, now))

    def get_liked_in_month(self, year: int, month: int) -> List[str]:
        """
        Return videoIds of songs liked in the given year and month.
        """
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute('''
                SELECT DISTINCT video_id FROM liked_songs
                WHERE liked_date >= ? AND liked_date < ?
            ''', (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
            return [row[0] for row in cur.fetchall()] 