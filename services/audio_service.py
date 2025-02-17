import os
import torch
from transformers import pipeline
from pydub import AudioSegment
from pydub.utils import make_chunks
from services.lamma_service import LammaService

# JSON format for validation of Llama service responses
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
    def __init__(self, audio_path, language="en"):
        self.audio_path = audio_path
        self.language = language  # Language parameter for Whisper
        self.asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )

    def process_audio(self):
        lamma_service = LammaService()
        
        # Load audio file using pydub
        try:
            audio = AudioSegment.from_file(self.audio_path)
        except Exception as e:
            raise Exception(f"Error loading audio file: {e}")

        # Split audio into 2-minute chunks
        chunk_length_ms = 180 * 1000  # 3 minutes
        chunks = make_chunks(audio, chunk_length_ms)

        questions = []
        full_transcript = ""

        # Create a directory for temporary audio chunks
        os.makedirs("audio_chunk", exist_ok=True)

        # Process each chunk sequentially
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}...")

            # Export chunk to WAV format
            chunk_path = f"audio_chunk/chunk_{i}.wav"
            try:
                chunk.export(chunk_path, format="wav")
            except Exception as e:
                print(f"Error exporting chunk {i + 1}: {e}")
                continue

            # Transcribe the chunk using Whisper
            try:
                transcription = self.asr_pipeline(inputs=chunk_path, return_timestamps=True)
                transcribed_text = transcription["text"]
                full_transcript += f" {transcribed_text}"
            except Exception as e:
                print(f"Error transcribing chunk {i + 1}: {e}")
                continue
            finally:
                # Clean up the chunk file
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)

            # Send transcription to Llama service for question extraction
            sys_msg = "You are an advanced AI designed to analyze text."
            user_msg = f"""
            Extract and list all the questions explicitly asked by the interviewer during a job interview in the software industry from the provided context. 
            Focus exclusively on interviewer-posed questions, excluding any candidate answers or unrelated text.
            If no interviewer questions are found, return an empty array. 
            Combine and rephrase similar questions to avoid duplication while preserving their original intent.

            INPUT: {transcribed_text}
            Respond using JSON format:
            """
            try:
                response = lamma_service.send_message_to_llama_chat(sys_msg=sys_msg, user_msg=user_msg, format=format)
                print(response["questions"])
                questions.extend(response["questions"])  # Add the returned questions to the list
            except Exception as e:
                print(f"Error processing chunk {i + 1}: {e}")
            print(transcribed_text)

        print("Full Transcr ipt:", full_transcript)
        return self.sanitize_questions(questions)

    def sanitize_questions(self, questions):
        """
        Filter out invalid or redundant questions.
        """
        # Remove empty or very short questions
        filtered_questions = [question for question in questions if len(question.split()) >= 3]
        return filtered_questions
