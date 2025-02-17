import os
import shutil
import torch
from uuid import uuid4
from datetime import datetime
from fastapi import UploadFile, HTTPException
from transformers import pipeline
from pydub import AudioSegment
from pydub.utils import make_chunks
from api.v1.services.lamma_service import LammaService

import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the parent directory where audio files should be stored
BASE_UPLOAD_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "audio_uploads"))
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)  # Ensure the base directory exists

# Creating audio object to store in Mongodb
format = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of questions (string) asked by the interviewer."
        },
    },
    "required": ["questions"]
}

class AudioService:
    def __init__(self, language="en"):
        self.language = language
        self.asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        self.lamma_service = LammaService()
        self.audio_path = None
        self.unique_directory_path = None


    def set_audio_path(self, audio_path):
        """Validates and sets the audio file path."""
        if not audio_path.endswith(".mp3"):
            raise HTTPException(status_code=400, detail="Invalid file format. Only MP3 is supported.")
        self.audio_path = audio_path

    def load_audio(self,path):
        """Loads the audio file using pydub."""
        return AudioSegment.from_file(path)
    
    def save_file(self, content: bytes, filename: str) -> str:
        save_dir = "uploads"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        with open(save_path, "wb") as file:
            file.write(content)
        return save_path
    
    def remove_file(self, path):
        os.remove(path)

    def split_audio_into_chunks(self, audio, chunk_length_ms=180000):
        """Splits the audio into smaller chunks and saves them."""
        chunk_folder = os.path.join("","chunks")
        os.makedirs(chunk_folder, exist_ok=True)

        chunks = make_chunks(audio, chunk_length_ms)
        chunk_paths = []

        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(chunk_folder, f"chunk_{i}.wav")
            chunk.export(chunk_path, format="wav")
            chunk_paths.append(chunk_path)

        return chunk_paths

    def transcribe_chunk(self, chunk_path):
        """Transcribes an audio chunk."""
        try:
            transcription = self.asr_pipeline(inputs=chunk_path, return_timestamps=True)
            return transcription["text"]
        except Exception as e:
            logger.error(f"Error transcribing chunk {chunk_path}: {e}")
            return ""

    def extract_questions(self, transcribed_text):
        """Extracts interview questions using Llama Service."""
        sys_msg = "You are an advanced AI designed to analyze text."
        user_msg = f"""
        Extract and list all the questions explicitly asked by the interviewer during a job interview in the software industry from the provided context. 
            Focus exclusively on interviewer-posed questions, excluding any candidate answers or unrelated text.
            If no interviewer questions are found, return an empty array. 
            Combine and rephrase similar questions to avoid duplication while preserving their original intent.
            
        INPUT: {transcribed_text}
        Respond using JSON format:
        ["question 1", "question 2"]
        """
        try:
            response = self.lamma_service.send_message_to_llama_chat(sys_msg=sys_msg, user_msg=user_msg,format=format)
            return response.get("questions", [])
        except Exception as e:
            logger.error(f"Error extracting questions: {e}")
            return []

    def convert_mp4_to_mp3(self, mp4_path: str) -> str:
        """Converts an MP4 file to MP3 and returns the MP3 file path."""
        mp3_path = os.path.splitext(mp4_path)[0] + ".mp3"  # Change extension to .mp3
        audio = AudioSegment.from_file(mp4_path, format="mp4")
        audio.export(mp3_path, format="mp3")
        return mp3_path
   

    
