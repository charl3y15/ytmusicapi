FROM python:3.11-slim

WORKDIR /app

# Install pip and build dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy only necessary files
COPY pyproject.toml ./
COPY ytmusicapi ./ytmusicapi

# Install dependencies (using pip for simplicity)
RUN pip install --upgrade pip && pip install .

# Copy the script
COPY ytmusicapi/monthly_playlist.py ./monthly_playlist.py

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "./monthly_playlist.py"] 