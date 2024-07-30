import os
import yt_dlp

def download_youtube_video(url, output_path):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    # Replace this URL with the URL of the video you want to download
    video_url = 'https://www.youtube.com/watch?v=b2QFKIwQFpc'
    
    # Specify the exact output path
    output_folder = "C:\\Users\\Cameron\\OneDrive\\Desktop\\"
    
    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    download_youtube_video(video_url, output_folder)

