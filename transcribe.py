import os
from moviepy.editor import VideoFileClip
from google.cloud import speech
from pydub import AudioSegment
import wave
import io
import concurrent.futures

# Set the environment variable for Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Cameron\\OneDrive\\Desktop\\TikTok Project\\service-account-file.json"

# Function to extract audio from video
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')

# Function to split audio into smaller chunks
def split_audio(audio_path, chunk_length_ms=30000):
    audio = AudioSegment.from_wav(audio_path)
    chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    return chunks

# Function to get the sample rate of an audio file
def get_sample_rate(audio_path):
    with wave.open(audio_path, 'r') as wav_file:
        return wav_file.getframerate()

# Function to convert audio to mono
def convert_to_mono(audio_path, mono_path):
    audio = AudioSegment.from_wav(audio_path)
    mono_audio = audio.set_channels(1)
    mono_audio.export(mono_path, format="wav")

# Function to transcribe audio using Google Cloud Speech-to-Text
def transcribe_audio_chunk(chunk, sample_rate_hertz):
    client = speech.SpeechClient()

    with io.BytesIO() as audio_file:
        chunk.export(audio_file, format="wav")
        audio_file.seek(0)
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate_hertz,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "
    return transcript

# Main function to transcribe all videos in the "Videos" folder
def transcribe_videos_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            video_path = os.path.join(folder_path, filename)
            audio_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.wav")
            mono_audio_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_mono.wav")
            transcript_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_transcript.txt")
            
            # Extract audio
            extract_audio(video_path, audio_path)
            
            # Convert audio to mono
            convert_to_mono(audio_path, mono_audio_path)

            # Get the sample rate of the audio file
            sample_rate_hertz = get_sample_rate(mono_audio_path)
            
            # Split audio into chunks
            audio_chunks = split_audio(mono_audio_path)

            # Transcribe audio chunks in parallel
            full_transcript = ""
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(transcribe_audio_chunk, chunk, sample_rate_hertz) for chunk in audio_chunks]
                for future in concurrent.futures.as_completed(futures):
                    full_transcript += future.result()

            # Save the full transcript to a file
            with open(transcript_path, "w") as transcript_file:
                transcript_file.write(full_transcript)
            
            print(f"Transcribed {filename}")






