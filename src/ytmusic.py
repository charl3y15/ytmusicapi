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
    played_counts = {}
    played_count = 0
    disliked_count = 0
    for item in history:
        played = item.get('played')
        video_id = item.get('videoId')
        like_status = item.get('likeStatus', 'INDIFFERENT')
        if debug_mode:
            logger.info(f"History item: played={played}, video_id={video_id}, like_status={like_status}")
        if played and video_id:
            if like_status == 'DISLIKE':
                disliked_count += 1
                continue
            played_date, matches = parse_played_date(played, start.year, start.month)
            if played_date is None:
                if debug_mode:
                    logger.warning(f"Failed to parse played date '{played}' for video_id {video_id}")
                continue
            if matches:
                played_counts[video_id] = played_counts.get(video_id, 0) + 1
                played_count += 1
    # Only include songs played at least twice, unless they are liked
    played_multiple_times_ids = {vid for vid, count in played_counts.items() if count >= 2 and vid not in liked_ids}
    logger.info(f"Played IDs in month (played >=2, not liked): {len(played_multiple_times_ids)}")
    logger.info(f"Liked IDs in month: {len(liked_ids)}")
    logger.info(f"Disliked songs in month: {disliked_count}")
    logger.info(f"Total unique songs for playlist (played >=2 or liked, not disliked): {len(played_multiple_times_ids) + len(liked_ids)}")
    return {
        "played_multiple_times": list(played_multiple_times_ids),
        "liked": list(liked_ids)
    } 