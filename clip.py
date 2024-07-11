import os
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from moviepy.editor import VideoFileClip

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

# Function to rate chunks with GPT-2
def rate_chunks_with_gpt2(chunks, prompt="Identify the segments of the following text that are the most entertaining, engaging, emotional, and attention-grabbing. These segments should be suitable for creating short, impactful TikTok clips:"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "gpt2"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
    
    scores = []
    for chunk in chunks:
        input_text = f"{prompt}\n\n{chunk}"
        inputs = tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits[:, -1, :]
        score = torch.mean(logits).item()
        normalized_score = (score - logits.min().item()) / (logits.max().item() - logits.min().item()) * 100
        scores.append(normalized_score)
        print(f"Rated chunk with normalized score: {normalized_score}")

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
        
        # Sort chunks by score in descending order and take the top 5
        top_chunks_with_scores = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)[:5]
        
        interesting_chunks_with_timestamps[video_id] = []
        
        for chunk, score in top_chunks_with_scores:
            if score >= threshold:
                start_pos = transcript.find(chunk)
                if start_pos == -1:
                    print(f"Error: Chunk not found in transcript for video {video_id}. Skipping chunk...")
                    continue
                
                start_time = start_pos / len(transcript) * duration
                end_time = start_time + (len(chunk.split()) / len(transcript.split())) * duration
                
                # Ensure end_time does not exceed video's duration
                end_time = min(end_time, duration)
                
                # Check if the clip length is between 30 seconds and 4 minutes
                if 30 <= (end_time - start_time) <= 240:
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
            except OSError as e:
                print(f"Error processing clip {video_id}_clip_{idx+1}: {e}")

# Main function to run the entire process
if __name__ == "__main__":
    transcripts_folder = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Videos"
    videos_folder = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Videos"
    output_folder = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\Clips"

    print("Loading transcripts...")
    transcripts = load_transcripts(transcripts_folder)
    
    processed_transcripts = {}
    for video_id, transcript in transcripts.items():
        chunks = split_into_chunks(transcript, chunk_size=100)
        print(f"Processed transcript for video ID: {video_id} into {len(chunks)} chunks")
        scores = rate_chunks_with_gpt2(chunks)
        processed_transcripts[video_id] = (chunks, scores)
    
    print("Mapping chunks to timestamps...")
    interesting_chunks_with_timestamps = map_chunks_to_timestamps(transcripts_folder, processed_transcripts)
    
    print("Clipping interesting segments...")
    clip_interesting_segments(interesting_chunks_with_timestamps, videos_folder, output_folder)
    
    print(f"Clipped the top 5 highest-rated segments from each video.")
