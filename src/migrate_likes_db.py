import os
import sqlite3

MIGRATIONS = [
    # (version, SQL statements)
    (1, [
        '''CREATE TABLE IF NOT EXISTS liked_songs (
            video_id TEXT,
            liked_date TEXT,
            PRIMARY KEY (video_id, liked_date)
        )''',
        '''CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )''',
        '''INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', '1')''',
    ]),
    # Future migrations can be added here as (2, [...]), (3, [...]), etc.
]

DB_PATH = os.path.join(os.path.dirname(__file__), 'liked_songs.db')

def get_schema_version(conn):
    try:
        cur = conn.execute("SELECT value FROM meta WHERE key='schema_version'")
        row = cur.fetchone()
        if row:
            return int(row[0])
        return 0
    except sqlite3.OperationalError:
        return 0

def set_schema_version(conn, version):
    conn.execute("UPDATE meta SET value=? WHERE key='schema_version'", (str(version),))
    conn.commit()

def apply_migrations(db_path=DB_PATH):
    with sqlite3.connect(db_path) as conn:
        current_version = get_schema_version(conn)
        print(f"Current schema version: {current_version}")
        for version, statements in MIGRATIONS:
            if version > current_version:
                print(f"Applying migration {version}...")
                for stmt in statements:
                    conn.execute(stmt)
                set_schema_version(conn, version)
                print(f"Migration {version} applied.")
        print("All migrations complete.")

if __name__ == "__main__":
    apply_migrations() 