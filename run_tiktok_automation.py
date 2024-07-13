import os
from search_videos import get_authenticated_service, search_videos, get_top_videos_by_view_count, download_youtube_video
from transcribe import transcribe_videos_in_folder
from clip import load_transcripts, split_into_chunks, rate_chunks_with_gpt3, map_chunks_to_timestamps, clip_interesting_segments
from create_tiktok import create_tiktok_video, generate_caption_and_hashtags, save_caption_and_hashtags, load_metadata
import random
import shutil
import time

# Define directories
BASE_DIR = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project"
VIDEOS_DIR = os.path.join(BASE_DIR, 'Videos')
CLIPS_DIR = os.path.join(BASE_DIR, 'Clips')
GAMEPLAY_DIR = os.path.join(BASE_DIR, 'NCGameplay')
TIKTOKS_DIR = os.path.join(BASE_DIR, 'TikToks')
COOKIES_PATH = os.path.join(BASE_DIR, 'cookies.txt')  # Path to your exported cookies
METADATA_PATH = os.path.join(VIDEOS_DIR, 'metadata.json')

# Step 1: Download videos
def download_videos():
    query = "best of mesut ozil"
    max_results = 400
    category_id = None
    published_after = "2023-01-01T00:00:00Z"
    
    youtube_client = get_authenticated_service()
    videos = search_videos(youtube_client, query, max_results, category_id, 'viewCount', published_after)
    
    if videos:
        top_videos = get_top_videos_by_view_count(videos, top_n=2)
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
        scores = rate_chunks_with_gpt3(chunks)
        processed_transcripts[video_id] = (chunks, scores)
    
    interesting_chunks_with_timestamps = map_chunks_to_timestamps(VIDEOS_DIR, processed_transcripts)
    clip_interesting_segments(interesting_chunks_with_timestamps, VIDEOS_DIR, CLIPS_DIR)

# Step 4: Create TikTok posts
def create_tiktok_posts():
    metadata = load_metadata(METADATA_PATH)
    tiktok_count = 1

    for video_id, clips in metadata.items():
        for clip_info in clips:
            tiktok_folder = os.path.join(TIKTOKS_DIR, f"TIKTOK {tiktok_count}")
            os.makedirs(tiktok_folder, exist_ok=True)

            clip_path = clip_info['clip_path']
            chunk = clip_info['chunk']
            caption_and_hashtags = generate_caption_and_hashtags(chunk)

            video_output_path = os.path.join(tiktok_folder, f"TIKTOK_{tiktok_count}.mp4")
            gameplay_path = os.path.join(GAMEPLAY_DIR, random.choice(os.listdir(GAMEPLAY_DIR)))
            create_tiktok_video(clip_path, gameplay_path, video_output_path)
            
            save_caption_and_hashtags(tiktok_folder, caption_and_hashtags)
            
            print(f"Caption: {caption_and_hashtags['caption']}")
            print(f"Hashtags: {' '.join(caption_and_hashtags['hashtags'])}")

            tiktok_count += 1


# Cleanup function
def clean_up():
    time.sleep(5)
    # Delete Videos folder and its contents
    if os.path.exists(VIDEOS_DIR):
        shutil.rmtree(VIDEOS_DIR)
    
    # Delete Clips folder and its contents
    if os.path.exists(CLIPS_DIR):
        shutil.rmtree(CLIPS_DIR)
    
    # Delete Metadata file
    if os.path.exists(METADATA_PATH):
        os.remove(METADATA_PATH)

if __name__ == "__main__":
    download_videos()
    transcribe_videos()
    clip_videos()
    create_tiktok_posts()
    clean_up()

