import os
import json
import random
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, CompositeVideoClip
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

print(f"Open_ai_key : {os.getenv('OPEN_AI_API_KEY')}")

# Set up your OpenAI API key
api_key = os.getenv("OPEN_AI_API_KEY")
if not api_key:
    raise ValueError("OPEN_AI_API_KEY environment variable not set")

# Instantiate the OpenAI client
client = OpenAI(api_key=api_key)

# Function to generate text using OpenAI GPT-3.5
def generate_text(prompt, max_tokens=50, temperature=0.7):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using the latest chat model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

# Function to generate caption and hashtags using GPT-3.5
def generate_caption_and_hashtags(chunk):
    hashtags_prompt = f"Generate 5 short and relevant hashtags for the following text segment for the purposes of a TikTok post. Only include the hashtags in your response, separated by spaces:\n\n{chunk}\n\n"
    caption_prompt = f"Create a short, engaging, and relevant caption for the following text segment for the purposes of TikTok. Only include the caption in your response:\n\n{chunk}\n\n"

    hashtags_output = generate_text(hashtags_prompt, max_tokens=20)  # Limit tokens to reduce costs
    caption_output = generate_text(caption_prompt, max_tokens=50)  # Limit tokens to reduce costs

    print(f"Generated caption: {caption_output}")
    print(f"Generated hashtags: {hashtags_output}")

    hashtags = [tag.strip() for tag in hashtags_output.split() if tag.strip().startswith('#')]
    caption = caption_output.strip().split('\n')[0]  # Take the first line as the caption

    return {"caption": caption, "hashtags": hashtags}

# Function to save caption and hashtags to a text file
def save_caption_and_hashtags(tiktok_folder, caption_and_hashtags):
    text_file_path = os.path.join(tiktok_folder, "caption_and_hashtags.txt")
    with open(text_file_path, "w", encoding="utf-8") as file:
        file.write(f"Caption:\n{caption_and_hashtags['caption']}\n\n")
        file.write("Hashtags:\n")
        file.write(" ".join(caption_and_hashtags['hashtags']))
    print(f"Saved caption and hashtags to {text_file_path}")

def create_tiktok_video(clipped_content_path, gameplay_path, output_path):
    # Load the video clips
    clipped_content = VideoFileClip(clipped_content_path)
    gameplay = VideoFileClip(gameplay_path).without_audio()  # Mute the gameplay audio

    # TikTok dimensions
    tiktok_width = 1080
    tiktok_height = 1920
    half_height = tiktok_height // 2  # Each clip will occupy half the height (960 pixels)

    # Resize clips to fit TikTok frame width and half height
    clipped_content_resized = clipped_content.resize(width=tiktok_width).resize(height=half_height)
    gameplay_resized = gameplay.resize(width=tiktok_width).resize(height=half_height)

    # Position the clips
    clipped_content_resized = clipped_content_resized.set_position(("center", "top"))
    gameplay_resized = gameplay_resized.set_position(("center", "bottom"))

    # Create the final composite video
    final_clip = CompositeVideoClip([clipped_content_resized, gameplay_resized], size=(tiktok_width, tiktok_height))

    # Set the duration of the final clip to match the clipped content
    final_clip = final_clip.set_duration(clipped_content.duration)

    # Write the final video to the output file
    final_clip.write_videofile(output_path, codec='libx264')
    print(f"Saved TikTok video: {output_path}")

# Function to load metadata
def load_metadata(metadata_path):
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    return metadata


if __name__ == "__main__":
    clips_folder = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Clips"
    gameplay_folder = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\NCGameplay"
    output_folder = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\TikToks"
    metadata_path = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Videos\\metadata.json"
    
    os.makedirs(output_folder, exist_ok=True)

    print("Loading clips metadata...")
    metadata = load_metadata(metadata_path)

    print("Creating TikTok posts...")
    tiktok_count = 1

    for video_id, clips in metadata.items():
        for clip_info in clips:
            tiktok_folder = os.path.join(output_folder, f"TIKTOK {tiktok_count}")
            os.makedirs(tiktok_folder, exist_ok=True)

            clip_path = clip_info['clip_path']
            chunk = clip_info['chunk']
            caption_and_hashtags = generate_caption_and_hashtags(chunk)

            video_output_path = os.path.join(tiktok_folder, f"TIKTOK_{tiktok_count}.mp4")
            gameplay_path = os.path.join(gameplay_folder, random.choice(os.listdir(gameplay_folder)))
            create_tiktok_video(clip_path, gameplay_path, video_output_path)
            
            save_caption_and_hashtags(tiktok_folder, caption_and_hashtags)
            
            print(f"Caption: {caption_and_hashtags['caption']}")
            print(f"Hashtags: {' '.join(caption_and_hashtags['hashtags'])}")

            tiktok_count += 1

    print(f"TikTok posts created and saved to {output_folder}.")

