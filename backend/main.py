from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from openai import OpenAI
from dotenv import load_dotenv

from agent import ask_saqr

import os
import requests

# تحميل المتغيرات
load_dotenv()

# إنشاء التطبيق
app = FastAPI()

# ملفات الصوت
app.mount(
    "/audio",
    StaticFiles(directory="."),
    name="audio"
)

# OpenAI Client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# الصفحة الرئيسية
@app.get("/")
def home():

    return {
        "message":
        "Saudi AI Voice Assistant Running"
    }

# رفع الصوت
@app.post("/upload-audio")
async def upload_audio(
    audio: UploadFile = File(...)
):

    # حفظ الملف مؤقتًا
    file_location = (
        f"temp_{audio.filename}"
    )

    with open(
        file_location,
        "wb"
    ) as buffer:

        buffer.write(
            await audio.read()
        )

    # فتح الملف الصوتي
    audio_file = open(
        file_location,
        "rb"
    )

    # تحويل الصوت إلى نص
    transcript = (
        client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ar"
        )
    )

    print(
        "TRANSCRIPT:",
        transcript.text
    )

    # رد صقر
    reply = ask_saqr(
        transcript.text
    )

    print(
        "AI RESPONSE:",
        reply
    )

    # اسم الملف الصوتي
    speech_file_path = (
        "reply.mp3"
    )

    # ElevenLabs API
    url = (
    "https://api.elevenlabs.io/v1/text-to-speech/"
    "EXAVITQu4vr4xnSDxMaL"
)

    headers = {

        "xi-api-key":
        os.getenv(
            "ELEVENLABS_API_KEY"
        ),

        "Content-Type":
        "application/json"
    }

    data = {
        "text": reply,
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }

    # إرسال الطلب
    response = requests.post(
        url,
        json=data,
        headers=headers
    )
    print(response.text)

    # حفظ الصوت
    with open(
        speech_file_path,
        "wb"
    ) as f:

        f.write(response.content)

    print("VOICE FILE SAVED")
    print(response.headers)
    print(len(response.content))

    # إرسال الرد للفرونت
    return {
        "transcript": transcript.text,
        "reply": reply,
        "audio_url": "http://127.0.0.1:8000/audio/reply.mp3"
    }

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):

    reply = ask_saqr(
        request.message
    )

    return {
        "reply": reply
    }