from utils.logger import get_debug_mode
from utils.dateparser import parse_played_date
from src.database import LikeDatabase
from datetime import datetime

class LikeTracker:
    def __init__(self, db_path=None):
        self.db = LikeDatabase(db_path)

    def update_likes(self, liked_songs):
        now = datetime.now().strftime('%Y-%m-%d')
        for song in liked_songs:
            video_id = song.get('videoId')
            if not video_id:
                continue
            self.db.insert_like(video_id, now)

    def get_liked_in_month(self, year, month):
        return self.db.get_liked_in_month(year, month)

def get_songs_for_month(ytmusic, like_tracker, start, end):
    debug_mode = get_debug_mode()
    liked = ytmusic.get_liked_songs(5000)
    like_tracker.update_likes(liked.get('tracks', []))
    liked_ids = set(like_tracker.get_liked_in_month(start.year, start.month))
    from utils.logger import get_logger
    logger = get_logger()
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
    all_ids = liked_ids.intersection(played_ids)
    logger.info(f"Total unique songs for playlist (played AND liked): {len(all_ids)}")
    return list(all_ids) 