# TIKTOKAUTOMATION

TIKTOKAUTOMATION is a project designed to fully automate the TikTok content creation process by clipping and editing popular YouTube videos to 
generate engaging TikToks. The system aims to grow TikTok accounts and monetize content by leveraging Google Text-to-Speech and OpenAI's 
GPT models for content selection and enhancement.

## Features

- **Automated YouTube Video Search:** Finds popular YouTube videos based on a user-provided query.
- **Transcription with Google Text-to-Speech:** Converts video audio into text for further processing.
- **Content Analysis with OpenAI GPT:** Identifies the most engaging segments of transcriptions using GPT models.
- **Video Clipping and Editing:** Clips selected segments, applies edits, and prepares videos for TikTok.
- **TikTok Formatting:** Adds hashtags, captions, and gameplay overlays to comply with TikTok’s content guidelines.

## Project Structure

The project is organized into five main Python files:

1. **`Search_Videos.py`**
   - Utilizes `yt_dlp` to search and download YouTube videos based on a user query.

2. **`Transcribe.py`**
   - Contains functions to transcribe downloaded videos using Google Text-to-Speech API.

3. **`Clip.py`**
   - Analyzes transcripts to find high-value content segments with OpenAI GPT. Clips these segments and prepares them for TikTok.

4. **`Create_Tiktok.py`**
   - Finalizes the videos by adding hashtags, captions, and overlays, ensuring content is TikTok-ready.

5. **`run_tiktok_automation.py`**
   - Main script to run the full automation pipeline.

## How It Works

1. **Video Search:** The system searches YouTube for popular videos based on a query.
2. **Transcription:** Videos are transcribed using Google Text-to-Speech.
3. **Content Clipping:** GPT evaluates transcripts to find entertaining segments, which are then clipped from the video.
4. **Final Edits:** Clips are formatted with gameplay overlays and captions, creating a polished TikTok video.
5. **Posting:** The ready-to-post video is optimized for TikTok growth.

## Outcome

- **Results:** Successfully grew a TikTok account to 11,000 followers with over 3 million views in just 30 days.

## Future Improvements

- **Alternative Video Formats:** Develop new editing styles that use filtering effects instead of gameplay to diversify content while avoiding unoriginal content bans on TikTok.
- **Enhanced Content Selection:** Explore improved methods for identifying engaging, complete thought segments in videos.



