from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# ✅ Configure Gemini API Key
genai.configure("GEMINI_API_KEY")  # Replace with your actual key

app = FastAPI()


# ✅ Manual transcript input model
class TranscriptInput(BaseModel):
    transcript: str


# ✅ Health check route
@app.get("/")
def read_root():
    return {"message": "YouTube Summarizer is running ✅"}


# ✅ Function to fetch transcript
def fetch_transcript(video_id: str) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([f"{entry['start']:.2f}s: {entry['text']}" for entry in transcript])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"❌ Could not fetch transcript: {e}")


# ✅ Function to summarize transcript using Gemini
def summarize_transcript(transcript: str) -> dict:
    prompt = f"""
You will be given a YouTube transcript. Return a JSON in this format only:
{{
  "topic name": "name of topic",
  "topic_summary": "summary of topic"
}}

Transcript:
{transcript}
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


# ✅ Endpoint to summarize a YouTube video by ID
@app.get("/summarize/{video_id}")
def summarize(video_id: str):
    transcript = fetch_transcript(video_id)
    summary = summarize_transcript(transcript)
    return {"video_id": video_id, "summary": summary}


# ✅ Fallback endpoint: Accept transcript manually
@app.post("/summarize/manual")
def summarize_manual(data: TranscriptInput):
    try:
        summary = summarize_transcript(data.transcript)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to summarize: {e}")
