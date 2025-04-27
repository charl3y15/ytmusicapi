# YouTube Music Monthly Playlist Docker

This Docker container automatically creates or updates a YouTube Music playlist for the previous month, containing all songs you've played or liked (excluding disliked songs). It runs on a schedule based on the `RUN_EVERY` environment variable (in days).

## Environment Variables

- `YTMUSIC_AUTH_FILE` (required): Path to your YouTube Music API auth headers JSON file (mount this file into the container).
- `RUN_EVERY` (optional): How often to run the script, in days. Default: `30`.
- `PLAYLIST_PRIVACY` (optional): Playlist privacy (`PRIVATE`, `PUBLIC`, or `UNLISTED`). Default: `PRIVATE`.

## Build the Docker Image

```sh
# From the project root
docker build -t ytmusic-monthly-playlist .
```

## Run the Container

```sh
docker run -d \
  -e YTMUSIC_AUTH_FILE=/auth/headers_auth.json \
  -e RUN_EVERY=30 \
  -e PLAYLIST_PRIVACY=PRIVATE \
  -v /path/to/your/headers_auth.json:/auth/headers_auth.json:ro \
  --name ytmusic-monthly-playlist \
  ytmusic-monthly-playlist
```

- Replace `/path/to/your/headers_auth.json` with the path to your YouTube Music auth file.
- The container will run in the background and check every `RUN_EVERY` days.

## Notes
- The script will create a playlist named like `May 2025` for the previous month, or add to it if it already exists.
- Only songs you've played or liked (but not disliked) are included.
- You must generate your auth file using the ytmusicapi setup process before running the container. 