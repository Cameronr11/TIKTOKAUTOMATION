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
