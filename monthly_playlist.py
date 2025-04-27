import os
import time
from ytmusicapi import YTMusic
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.ytmusic import LikeTracker
from src.auth import AuthHelper
from utils.logger import get_logger, get_debug_mode
from utils.dateparser import get_month_range, get_previous_month_range
from src.playlists import find_existing_playlist
from src.ytmusic import get_songs_for_month

load_dotenv()

logger = get_logger()

def get_env_var(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def main():
    auth_file_env = AuthHelper.get_auth_file_env(required=True)
    auth_file = AuthHelper.resolve_auth_file(auth_file_env)
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
        logger.info(f"RUN_FOR: {run_for}")
        month_name = start.strftime('%B')
        playlist_title = f"{month_name} {year}"
        playlist_desc = f"Songs played or liked in {month_name} {year} (auto-generated)"
        logger.info(f"Collecting songs for {playlist_title}")
        video_ids = get_songs_for_month(ytmusic, like_tracker, start, end)

        playlist_id = find_existing_playlist(ytmusic, playlist_title)
        if playlist_id:
            logger.info(f"Playlist '{playlist_title}' exists. Checking for missing songs...")
            playlist = ytmusic.get_playlist(playlist_id, limit=None)
            current_ids = set(str(track['videoId']) for track in playlist.get('tracks', []) if 'videoId' in track)
            to_add = set(str(vid) for vid in video_ids) - current_ids
            logger.info(f"Songs already in playlist: {len(current_ids)}")
            logger.info(f"Songs to add: {len(to_add)}")
            if to_add:
                ytmusic.add_playlist_items(playlist_id, list(to_add))
                logger.info(f"Added {len(to_add)} new songs to playlist '{playlist_title}'.")
            else:
                logger.info("No new songs to add to the playlist.")

            # Remove disliked songs from the playlist
            disliked_tracks = [
                {'videoId': track['videoId'], 'setVideoId': track['setVideoId']}
                for track in playlist.get('tracks', [])
                if track.get('likeStatus') == 'DISLIKE' and 'setVideoId' in track
            ]
            if disliked_tracks:
                logger.info(f"Removing {len(disliked_tracks)} disliked songs from playlist '{playlist_title}'.")
                ytmusic.remove_playlist_items(playlist_id, disliked_tracks)
                logger.info(f"Removed {len(disliked_tracks)} disliked songs from playlist '{playlist_title}'.")
        else:
            if video_ids:
                logger.info(f"Creating playlist '{playlist_title}' with {len(video_ids)} songs...")
                ytmusic.create_playlist(playlist_title, playlist_desc, playlist_privacy, video_ids=video_ids)
            else:
                logger.info("No songs found for selected month. Skipping playlist creation.")
        if run_for:
            break  # Only run once if RUN_FOR is set
        logger.info(f"Sleeping for {run_every} days...")
        time.sleep(run_every * 24 * 60 * 60)

if __name__ == "__main__":
    main() 