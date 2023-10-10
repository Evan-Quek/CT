import uvicorn, os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from download_youtube_audio import get_youtube_channel_links, download_audio
from transcribe_and_translate import decode_audio, find_key


app = FastAPI()


class Channel(BaseModel):
    channel_url: str

class Decode(BaseModel):
    youtube_url: str
    output_path: str
    language: Optional[str]
    task: Optional[str]

class Transcribe_or_Translate(BaseModel):
    audio: str #TODO
    language: Optional[str]
    output_path: str
    task: str

class Download(BaseModel):
    youtube_url: str
    output_path: str
    
    
@app.post("/api/youtube/get_youtube_channel_video_links")
async def get_youtube_channel_video_links(channel: Channel):
    '''
    POST http://localhost:8000/api/youtube/get_youtube_channel_video_links HTTP/1.1
    {
        "channel_url": "https://www.youtube.com/@elliottchong/videos" Go to the videos page...
    }
    '''   
    channel_url = channel.channel_url
    print(f"Fetching youtube urls from {channel_url}...")
    results = get_youtube_channel_links(channel_url)
    print(f"Fetching complete...")
    
    return results

#TODO
@app.post("/api/youtube/download")
async def download_youtube_audio(download: Download):
    '''
    POST http://localhost:8000/api/youtube/download HTTP/1.1
    {
        "youtube_url": "https://www.youtube.com/watch?v=uC6VBDJlm4w"
    }
    '''   
    youtube_url = download.youtube_url
    output_path = download.output_path
    download_audio(youtube_url, output_path)
    return


@app.post("/api/youtube/download_transcribe_translate")
async def download_transcribe_translate(decode: Decode):
    '''
    POST http://localhost:8000/api/youtube/download_transcribe_translate HTTP/1.1
    {
        "youtube_url": "https://www.youtube.com/watch?v=b0BBrjTXqsk&t=11s",
        "output_path": "C:/Users/evanq/Documents/EAS_Work/CTIA/main/youtube_download_transcribe_translate",
        "language": "Indonesian"
    }
    '''       
    youtube_url = decode.youtube_url
    output_path = decode.output_path
    language = decode.language

    audio_path = download_audio(youtube_url, output_path)

    if language:
        input_language = find_key(language)
        file_paths = decode_audio(path=audio_path, output_dir=output_path, language=input_language)
    else:
        print("No language selected. Model will autodetect language.")
        file_paths = decode_audio(path=audio_path, output_dir=output_path)

    return file_paths



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


