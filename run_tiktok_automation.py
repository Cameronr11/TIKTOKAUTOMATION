import os
from search_videos import get_authenticated_service, search_videos, get_top_videos_by_view_count, download_youtube_video
from transcribe import transcribe_videos_in_folder
from clip import load_transcripts, split_into_chunks, rate_chunks_with_gpt2, map_chunks_to_timestamps, clip_interesting_segments
from create_tiktok import create_tiktok_videos

# Define directories
BASE_DIR = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project"
VIDEOS_DIR = os.path.join(BASE_DIR, 'Videos')
CLIPS_DIR = os.path.join(BASE_DIR, 'Clips')
GAMEPLAY_DIR = os.path.join(BASE_DIR, 'NCGameplay')
TIKTOKS_DIR = os.path.join(BASE_DIR, 'TikToks')
COOKIES_PATH = os.path.join(BASE_DIR, 'cookies.txt')  # Path to your exported cookies
METADATA_PATH = os.path.join(BASE_DIR, 'metadata_with_hashtags.json')

# Step 1: Download videos
def download_videos():
    query = "funniest shane gillis"
    max_results = 400
    category_id = None
    published_after = "2023-01-01T00:00:00Z"
    
    youtube_client = get_authenticated_service()
    videos = search_videos(youtube_client, query, max_results, category_id, 'viewCount', published_after)
    
    if videos:
        top_videos = get_top_videos_by_view_count(videos, top_n=5)
        for video in top_videos:
            video_id = video['video_id']
            download_youtube_video(video_id, VIDEOS_DIR, COOKIES_PATH)

# Step 2: Transcribe videos
def transcribe_videos():
    transcribe_videos_in_folder(VIDEOS_DIR)

# Step 3: Clip videos
def clip_videos():
    transcripts = load_transcripts(VIDEOS_DIR)
    processed_transcripts = {}
    for video_id, transcript in transcripts.items():
        chunks = split_into_chunks(transcript, chunk_size=100)
        scores = rate_chunks_with_gpt2(chunks)
        processed_transcripts[video_id] = (chunks, scores)
    
    interesting_chunks_with_timestamps = map_chunks_to_timestamps(VIDEOS_DIR, processed_transcripts)
    clip_interesting_segments(interesting_chunks_with_timestamps, VIDEOS_DIR, CLIPS_DIR)

# Step 4: Create TikTok posts
def create_tiktok_posts():
    create_tiktok_videos(CLIPS_DIR, GAMEPLAY_DIR, TIKTOKS_DIR)

if __name__ == "__main__":
    download_videos()
    transcribe_videos()
    clip_videos()
    create_tiktok_posts()

