Overview: 

TIKTOKAUTOMATION is a project that attempts to completely automate the tiktok clipping content creation model with the hopes of making money on tiktok.
Essentially the system would search for popular youtube videos based on a query and then use Google text to speech to transcribe the selected videos, 
passing those onto OpenAi's GPT to find interesting segments of the video, and then the system would clip those segments and style/edit them to be posted to 
TikTok. 

Project Organization:

5 Main Python Files - Search_Videos.py, Transcribe.py, Clip.py, Create_Tiktok.py, run_tiktok_automation.py

Search_Videos.py - Utilizes yt_dlp to search and donwload youtube videos based on a query the user provides

Transcribe.py - This file contains helper functions to search through all the downloaded videos gathered by Search_videos.py and transcribe each video for later use using Google Text to Speech API

Clip.py - This file might be the most important and require the most improvement. Clip.py takes all generated transcripts, uses OpenAi's GPT API to rate sections of the transcripts evaluating for 
shock value and entertainment. Once finding the best segments we map the timestamps back to the videos and clip those segments saving them to be later edited/formatted for tiktok.

Create_Tiktok.py - This file adds finishing touches by Creating hashtags and captions for each video using OpenAi's GPT API as well as taking the clips created by Clip.py and stacking those clips on top of
Gameplay (a common tiktok clipping practice to avoid unoriginal content bans by tiktok). Lastly we format the tiktok so that we produce a clean, ready to post video for tiktok

Outcome: 

Using this software I was able to grow an account to 11,000 Followers with over 3 Million views in 30 days.

Future Imrpovements: Right now the system is designed to produce tiktoks with gameplay underneath however I want to create a seperate file that creates tiktoks without the gameplay, but adds filtering effects to
the video as another way to bypass the unorignal content bans by tiktok. I also think that there is a better way to find entertaining chunks of the videos that are complete thoughts. 

