def find_existing_playlist(ytmusic, title):
    playlists = ytmusic.get_library_playlists(100)
    for pl in playlists:
        if pl.get('title') == title:
            return pl.get('playlistId')
    return None 