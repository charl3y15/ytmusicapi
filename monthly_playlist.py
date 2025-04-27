import os
import time
from datetime import datetime, timedelta
from ytmusicapi import YTMusic
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from like_tracker import LikeTracker
from ytmusicapi.utils.logger import get_logger

load_dotenv()

logger = get_logger()

def get_env_var(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def get_debug_mode():
    return os.getenv('DEBUG_MODE', 'false').lower() in ('1', 'true', 'yes')

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

def get_month_range(year: int, month: int):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(days=1)
    return start, end

def get_previous_month_range():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    start = last_month.replace(day=1)
    end = last_month.replace(day=last_month.day)
    return start, end

def parse_played_date(played_str, target_year, target_month):
    today = datetime.today()
    if played_str == "Today":
        return today, (today.year == target_year and today.month == target_month)
    elif played_str == "Yesterday":
        dt = today - timedelta(days=1)
        return dt, (dt.year == target_year and dt.month == target_month)
    elif played_str == "Last week":
        dt = today - timedelta(days=7)
        return dt, (dt.year == target_year and dt.month == target_month)
    # Try full month and year (e.g., 'February 2025')
    try:
        dt = datetime.strptime(played_str, "%B %Y")
        return dt, (dt.year == target_year and dt.month == target_month)
    except Exception:
        pass
    # Try abbreviated month, day, year (e.g., 'Mar 15, 2025')
    try:
        dt = datetime.strptime(played_str, "%b %d, %Y")
        return dt, (dt.year == target_year and dt.month == target_month)
    except Exception:
        return None, False

def get_songs_for_month(ytmusic, like_tracker, start, end):
    debug_mode = get_debug_mode()
    liked = ytmusic.get_liked_songs(5000)
    like_tracker.update_likes(liked.get('tracks', []))
    liked_ids = set(like_tracker.get_liked_in_month(start.year, start.month))
    logger.info(f"Liked IDs in month: {len(liked_ids)}")
    history = ytmusic.get_history()
    played_ids = set()
    played_count = 0
    for item in history:
        played = item.get('played')
        video_id = item.get('videoId')
        like_status = item.get('likeStatus', 'INDIFFERENT')
        if debug_mode:
            logger.info(f"History item: played={played}, video_id={video_id}, like_status={like_status}")
        if played and video_id and like_status != 'DISLIKE':
            played_date, matches = parse_played_date(played, start.year, start.month)
            if played_date is None:
                if debug_mode:
                    logger.warning(f"Failed to parse played date '{played}' for video_id {video_id}")
                continue
            if matches:
                played_ids.add(video_id)
                played_count += 1
    logger.info(f"Played IDs in month: {played_count}")
    all_ids = liked_ids.union(played_ids)
    logger.info(f"Total unique songs for playlist: {len(all_ids)}")
    return list(all_ids)

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
    run_for = get_env_var('RUN_FOR', None)
    ytmusic = YTMusic(auth_file)
    like_tracker = LikeTracker()

    while True:
        if run_for:
            # Parse MM/YYYY
            try:
                month_str, year_str = run_for.split('/')
                month = int(month_str)
                year = int(year_str)
                start, end = get_month_range(year, month)
            except Exception:
                raise RuntimeError("RUN_FOR must be in MM/YYYY format, e.g. 05/2025 for May 2025")
        else:
            start, end = get_previous_month_range()
            month = start.month
            year = start.year
        logger.info(f"RUN_FOR: {run_for}, Running for month: {month} year: {year}")
        month_name = start.strftime('%B')
        playlist_title = f"{month_name} {year}"
        playlist_desc = f"Songs played or liked in {month_name} {year} (auto-generated)"
        logger.info(f"Collecting songs for {playlist_title}")
        video_ids = get_songs_for_month(ytmusic, like_tracker, start, end)
        if not video_ids:
            logger.info("No songs found for selected month. Skipping playlist creation.")
        else:
            playlist_id = find_existing_playlist(ytmusic, playlist_title)
            if playlist_id:
                logger.info(f"Playlist '{playlist_title}' exists. Adding songs...")
                ytmusic.add_playlist_items(playlist_id, video_ids)
            else:
                logger.info(f"Creating playlist '{playlist_title}' with {len(video_ids)} songs...")
                ytmusic.create_playlist(playlist_title, playlist_desc, playlist_privacy, video_ids=video_ids)
        if run_for:
            break  # Only run once if RUN_FOR is set
        logger.info(f"Sleeping for {run_every} days...")
        time.sleep(run_every * 24 * 60 * 60)

if __name__ == "__main__":
    main() 