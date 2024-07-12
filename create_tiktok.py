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
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Using the latest chat model
    messages=[{"role": "user", "content": prompt}],
    max_tokens=max_tokens,
    temperature=temperature)
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

# Function to create TikTok video by combining the clipped content and gameplay
def create_tiktok_video(clipped_content_path, gameplay_path, output_path):
    clipped_content = VideoFileClip(clipped_content_path)
    gameplay = VideoFileClip(gameplay_path).without_audio()  # Mute the gameplay audio

    # Resize gameplay to fit the bottom half of the TikTok frame
    gameplay_resized = gameplay.resize(width=clipped_content.size[0])
    gameplay_resized = gameplay_resized.set_position(("center", "bottom"))

    # Create a blank canvas with the TikTok aspect ratio
    width, height = clipped_content.size[0], clipped_content.size[1] * 2
    blank_clip = CompositeVideoClip([clipped_content.set_position("top"), gameplay_resized], size=(width, height))

    final_clip = blank_clip.set_duration(clipped_content.duration)

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
    for video_id, clips in metadata.items():
        for clip_info in clips:
            clip_path = clip_info['clip_path']
            chunk = clip_info['chunk']
            caption_and_hashtags = generate_caption_and_hashtags(chunk)
            output_path = os.path.join(output_folder, os.path.basename(clip_path))
            gameplay_path = os.path.join(gameplay_folder, random.choice(os.listdir(gameplay_folder)))
            create_tiktok_video(clip_path, gameplay_path, output_path)
            print(f"Caption: {caption_and_hashtags['caption']}")
            print(f"Hashtags: {' '.join(caption_and_hashtags['hashtags'])}")

    print(f"TikTok posts created and saved to {output_folder}.")
