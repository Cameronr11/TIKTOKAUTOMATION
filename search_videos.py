import os
import yt_dlp as youtube_dl #install in venv
from auth import get_authenticated_service
import time
import isodate #install in venv

def fetch_video_statistics(youtube, video_id):
    video_response = youtube.videos().list(part="statistics", id=video_id).execute()
    return int(video_response['items'][0]['statistics']['viewCount'])

def fetch_video_duration(youtube, video_id):
    video_response = youtube.videos().list(part="contentDetails", id=video_id).execute()
    duration = video_response['items'][0]['contentDetails']['duration']
    return duration

def is_video_short(duration):
    try:
        duration_seconds = isodate.parse_duration(duration).total_seconds()
        print(f"Duration: {duration}, Seconds: {duration_seconds}")
        return duration_seconds < 300
    except Exception as e:
        print(f"Error parsing duration {duration}: {e}")
        return True  # Treat parsing errors as short videos to exclude them
    
def search_videos(youtube, query, max_results=10, category_id=None, order='viewCount', published_after=None):
    request = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        type="video",
        order=order,
        videoCategoryId=category_id,
        relevanceLanguage='en',
        publishedAfter=published_after
    )
    response = request.execute()
    if response:
        print("good response")
    videos = []
    for item in response['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        channel_title = item['snippet']['channelTitle']
        view_count = fetch_video_statistics(youtube, video_id)
        duration = fetch_video_duration(youtube, video_id)
        if not is_video_short(duration):  # Filter out shorts
            videos.append({
                'video_id': video_id,
                'title': title,
                'description': description,
                'channel_title': channel_title,
                'view_count': view_count,
                'duration': duration
            })
    return videos

def get_top_videos_by_view_count(videos, top_n=5):
    sorted_videos = sorted(videos, key=lambda x: x['view_count'], reverse=True)
    return sorted_videos[:top_n]

def download_youtube_video(video_id, output_dir, cookies_path):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_dir, f'{video_id}.%(ext)s'),
        'noplaylist': True,
        'cookiefile': cookies_path
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    query = "best of shane gillis"
    max_results = 400
    category_id = None
    published_after = "2023-01-01T00:00:00Z"

    youtube_client = get_authenticated_service()
    print("Authenticated YouTube client")

    videos = search_videos(youtube_client, query, max_results, category_id, 'viewCount', published_after)
    print(f"Found {len(videos)} videos")

    if videos:
        top_videos = get_top_videos_by_view_count(videos, top_n=5)
        print(f"Top {len(top_videos)} videos by view count")

        project_dir = os.path.dirname(os.path.abspath(__file__))
        DOWNLOAD_DIR = os.path.join(project_dir, 'Videos')
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        COOKIES_PATH = os.path.join(project_dir, 'cookies.txt')  # Path to your exported cookies

        for video in top_videos:
            video_id = video['video_id']
            video_title = video['title']
            print(f"Downloading: {video_title} with {video['view_count']} views.")

            start_time = time.time()
            download_youtube_video(video_id, DOWNLOAD_DIR, COOKIES_PATH)
            end_time = time.time()

            duration = end_time - start_time
            print(f"Downloaded {video_title} to {DOWNLOAD_DIR} in {duration:.2f} seconds")
    else:
        print("No videos found")
