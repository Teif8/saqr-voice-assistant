from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from openai import OpenAI
from dotenv import load_dotenv

from pydantic import BaseModel

from agent import ask_saqr

import os

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

    # تحويل النص إلى صوت باستخدام OpenAI
    speech_response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input=reply
    )

    # حفظ الملف الصوتي
    with open(
        speech_file_path,
        "wb"
    ) as f:

        f.write(
            speech_response.content
        )

    print("VOICE FILE SAVED")

    # إرسال الرد
    return {

        "transcript":
        transcript.text,

        "reply":
        reply,

        "audio_url":
        "https://saqr-voice-assistant-production.up.railway.app/audio/reply.mp3"

    }


# شات عادي
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
