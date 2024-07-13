import os
import json
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
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

# Function to load transcripts
def load_transcripts(transcripts_folder):
    transcripts = {}
    for filename in os.listdir(transcripts_folder):
        if filename.endswith("_transcript.txt"):
            video_id = filename.split("_")[0]
            with open(os.path.join(transcripts_folder, filename), 'r') as f:
                transcripts[video_id] = f.read()
    return transcripts

# Function to split transcripts into chunks
def split_into_chunks(transcript, chunk_size=100):
    words = transcript.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Function to rate chunks with GPT-3.5
def rate_chunks_with_gpt3(chunks, prompt="Identify the segments of the following text that are the most entertaining, engaging, emotional, and attention-grabbing for the purpose of posting to TikTok. Provide a single overall score for each segment on a scale of 1 to 100. Format the response with each segment and its score on a new line in the following format: 'Segment: [segment text] - Score: [score]'"):
    scores = []
    for chunk in chunks:
        input_text = f"{prompt}\n\nText:\n{chunk}"
        print(f"Sending request to GPT-3.5 for chunk: {chunk[:30]}...")  # Print first 30 characters of the chunk for tracking
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": input_text}],
            max_tokens=150,
            temperature=0.7,
        )
        output_text = response.choices[0].message.content.strip()
        print(f"Received response: {output_text}")  # Print the received response

        # Extract and score each line of the response
        lines = [line for line in output_text.split('\n') if line.strip()]
        if not lines:
            print(f"No valid lines found in response: {output_text}")
            continue

        for line in lines:
            try:
                # Extract the segment and score from the response line
                segment, score_str = line.split(" - Score: ")
                score = int(score_str)
                if 1 <= score <= 100:  # Ensure the score is within the expected range
                    scores.append((chunk, segment.strip(), score))
                    print(f"Rated chunk with score: {score}")
                else:
                    print(f"Invalid score received: {score}")
            except (ValueError, IndexError) as e:
                print(f"Error parsing score from line: {line} - {e}")

    return scores
# Function to map chunks to timestamps
def map_chunks_to_timestamps(transcripts_folder, processed_transcripts, threshold=50):
    interesting_chunks_with_timestamps = {}
    for video_id, (chunks, scores) in processed_transcripts.items():
        if not video_id:  # Check for empty video ID
            print("Error: Empty video ID detected. Skipping...")
            continue

        transcript_path = os.path.join(transcripts_folder, f"{video_id}_transcript.txt")
        video_path = os.path.join(transcripts_folder, f"{video_id}.mp4")
        
        if not os.path.exists(video_path):
            print(f"Error: Video file {video_path} not found. Skipping...")
            continue
        
        video = VideoFileClip(video_path)
        duration = video.duration
        
        transcript = "\n".join(chunks)
        
        # Sort chunks by score in descending order and take the top n with n being reverse=True)[:n]
        top_chunks_with_scores = sorted(scores, key=lambda x: x[2], reverse=True)[:2]
        
        interesting_chunks_with_timestamps[video_id] = []
        
        for chunk, line, score in top_chunks_with_scores:
            if score >= threshold:
                start_pos = transcript.find(chunk)
                if start_pos == -1:
                    print(f"Error: Chunk not found in transcript for video {video_id}. Skipping chunk...")
                    continue
                
                start_time = start_pos / len(transcript) * duration
                end_time = start_time + (len(chunk.split()) / len(transcript.split())) * duration
                
                # Ensure end_time does not exceed video's duration
                end_time = min(end_time, duration)
                
                # change the range to determine how long you want your clips to be
                if 60 <= (end_time - start_time) <= 240:
                    interesting_chunks_with_timestamps[video_id].append((chunk, start_time, end_time, score))
                    print(f"Mapped chunk to timestamps: start={start_time}, end={end_time}, score={score}")
                else:
                    print(f"Skipped chunk due to unreasonable length: start={start_time}, end={end_time}, duration={end_time - start_time}")
    
    return interesting_chunks_with_timestamps

# Function to clip interesting segments from videos
def clip_interesting_segments(interesting_chunks_with_timestamps, videos_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    for video_id, chunks_with_timestamps in interesting_chunks_with_timestamps.items():
        for idx, (chunk, start_time, end_time, score) in enumerate(chunks_with_timestamps):
            video_path = os.path.join(videos_folder, f"{video_id}.mp4")

            if not os.path.exists(video_path):
                print(f"Error: Video file {video_path} not found. Skipping...")
                continue

            try:
                video = VideoFileClip(video_path)
                clip = video.subclip(start_time, end_time)
                output_path = os.path.join(output_folder, f"{video_id}_clip_{idx+1}.mp4")
                clip.write_videofile(output_path, codec='libx264')
                print(f"Saved clip: {output_path}")
                # Save metadata
                save_metadata(video_id, idx, output_path, chunk)
                print("save metadata ran")
            except OSError as e:
                print(f"Error processing clip {video_id}_clip_{idx+1}: {e}")

# Function to save metadata
def save_metadata(video_id, idx, clip_path, chunk):
    metadata_path = os.path.join("C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Videos", "metadata.json")
    print("created metadata path")
    if os.path.exists(metadata_path):
        print("metadata path exists")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    if video_id not in metadata:
        metadata[video_id] = []
    
    metadata[video_id].append({
        "clip_path": clip_path,
        "chunk": chunk
    })
    
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
'''
if __name__ == "__main__":
    TRANSCRIPTS_FOLDER = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Videos"
    CLIPS_FOLDER = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Clips"

    print("Loading transcripts...")
    transcripts = load_transcripts(TRANSCRIPTS_FOLDER)
    processed_transcripts = {}
    for video_id, transcript in transcripts.items():
        print(f"Processing video ID: {video_id}")
        chunks = split_into_chunks(transcript, chunk_size=100)
        scores = rate_chunks_with_gpt3(chunks)
        processed_transcripts[video_id] = (chunks, scores)
    
    print("Mapping chunks to timestamps...")
    interesting_chunks_with_timestamps = map_chunks_to_timestamps(TRANSCRIPTS_FOLDER, processed_transcripts)
    
    print("Clipping interesting segments...")
    clip_interesting_segments(interesting_chunks_with_timestamps, TRANSCRIPTS_FOLDER, CLIPS_FOLDER)
    
    print("Process completed.")
'''
