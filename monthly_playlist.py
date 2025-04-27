import os
import time
from datetime import datetime, timedelta
from ytmusicapi import YTMusic
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

def get_env_var(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def resolve_auth_file(auth_file):
    # If absolute path or file exists as given, use it
    if os.path.isabs(auth_file) and os.path.exists(auth_file):
        return auth_file
    # Try relative to current working directory
    if os.path.exists(auth_file):
        return auth_file
    # Try in 'auth' directory relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    auth_path = os.path.join(script_dir, 'auth', os.path.basename(auth_file))
    if os.path.exists(auth_path):
        return auth_path
    raise RuntimeError(f"Auth file not found: {auth_file}")

def get_previous_month_range():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    start = last_month.replace(day=1)
    end = last_month.replace(day=last_month.day)
    return start, end

def get_songs_for_month(ytmusic, start, end):
    # Get all liked songs (no date info, so just for status)
    liked = ytmusic.get_liked_songs(5000)
    liked_ids = set()
    for track in liked.get('tracks', []):
        video_id = track.get('videoId')
        like_status = track.get('likeStatus', 'INDIFFERENT')
        if video_id and like_status == 'LIKE':
            liked_ids.add(video_id)
    # Get play history (with played date)
    history = ytmusic.get_history()
    played_ids = set()
    for item in history:
        played = item.get('played')
        video_id = item.get('videoId')
        like_status = item.get('likeStatus', 'INDIFFERENT')
        if played and video_id and like_status != 'DISLIKE':
            try:
                played_date = datetime.strptime(played, "%b %d, %Y")
                if start <= played_date <= end:
                    played_ids.add(video_id)
            except Exception:
                continue
    # Union of liked and played (excluding any disliked)
    return list(liked_ids.union(played_ids))

def find_existing_playlist(ytmusic, title):
    playlists = ytmusic.get_library_playlists(100)
    for pl in playlists:
        if pl.get('title') == title:
            return pl.get('playlistId')
    return None

def main():
    auth_file_env = get_env_var('YTMUSIC_AUTH_FILE', required=True)
    auth_file = resolve_auth_file(auth_file_env)
    run_every = int(get_env_var('RUN_EVERY', 30))
    playlist_privacy = get_env_var('PLAYLIST_PRIVACY', 'PRIVATE')
    ytmusic = YTMusic(auth_file)

    while True:
        start, end = get_previous_month_range()
        month_name = start.strftime('%B')
        year = start.year
        playlist_title = f"{month_name} {year}"
        playlist_desc = f"Songs played or liked in {month_name} {year} (auto-generated)"
        logging.info(f"Collecting songs for {playlist_title}")
        video_ids = get_songs_for_month(ytmusic, start, end)
        if not video_ids:
            logging.info("No songs found for previous month. Skipping playlist creation.")
        else:
            playlist_id = find_existing_playlist(ytmusic, playlist_title)
            if playlist_id:
                logging.info(f"Playlist '{playlist_title}' exists. Adding songs...")
                ytmusic.add_playlist_items(playlist_id, video_ids)
            else:
                logging.info(f"Creating playlist '{playlist_title}' with {len(video_ids)} songs...")
                ytmusic.create_playlist(playlist_title, playlist_desc, playlist_privacy, video_ids=video_ids)
        logging.info(f"Sleeping for {run_every} days...")
        time.sleep(run_every * 24 * 60 * 60)

if __name__ == "__main__":
    main() 