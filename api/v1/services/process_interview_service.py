from datetime import datetime
import logging
from typing import List, Optional
from bson import ObjectId
from fastapi import BackgroundTasks
from pymongo.errors import PyMongoError
import pytz

from config.mongo_db import MongoDBManager
from config.collections import AUDIO_EXTRACT
from exceptions.not_found_exception import NotFoundException
from exceptions.bad_request_exception import BadRequestException
from api.v1.services.audio_service import AudioService
from schemas.process_interview import interview_helper, interviews_helper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

audio_service=AudioService()

class ProcessInterviewService:
    def __init__(self):
        manager = MongoDBManager()
        self.collection = manager.get_collection(AUDIO_EXTRACT)
        
    def get_audio_extracts(self):
        extracts = self.collection.find()
        return interviews_helper(extracts)
    
    def get_audio_extract_by_id(self, id: str):
        extract = self.collection.find_one({"_id": ObjectId(id)})
        if not extract:
            raise NotFoundException(f"Audio extract not found with id {id}")
        return interview_helper(extract)
    
    def process_audio_file(self, file,background_tasks: BackgroundTasks = None):
        if background_tasks is None:
            raise BadRequestException("BackgroundTasks instance is required")
    
        if file is None:
            raise BadRequestException("File not found")

        if not (file.filename.endswith(".mp3") or file.filename.endswith(".mp4")):
            raise BadRequestException("Invalid file format. Only MP3 and MP4 are supported.")

        file_content = file.file.read()
        id = self.create_audio_extract(file.filename)
        filename = f"{id}.mp3" if file.filename.endswith(".mp3") else f"{id}.mp4"
        saved_path = audio_service.save_file(file_content, filename)
        background_tasks.add_task(self.process, saved_path, id)
        return id
     
    def process(self,file,id):
        try:
            audio = audio_service.load_audio(file)
            chunk_paths = audio_service.split_audio_into_chunks(audio)
            total_chunks = len(chunk_paths)
            questions=[]
            percentage_for_a_chunk = 70 / total_chunks
            for i, chunk_path in enumerate(chunk_paths):
                    try:
                        logger.info(f"Processing chunk {i + 1}/{total_chunks}...")
                        completion_percentage = int(30 + (i + 1) * percentage_for_a_chunk)
                        self.update_audio_extract(id, {"completion_percentage":completion_percentage})
                        transcribed_text = audio_service.transcribe_chunk(chunk_path)  
                        
                        if not transcribed_text:
                            logger.warning(f"Skipping empty transcription for chunk {i + 1}.")
                            continue
                        extracted_questions = audio_service.extract_questions(transcribed_text)
                        questions.extend(extracted_questions)
                        audio_service.remove_file(chunk_path)
                    except Exception as chunk_error:
                        logger.error(f"Error processing chunk {i + 1}: {chunk_error}")
                        continue
            sanitized_questions = self.sanitize_questions(questions)
            self.update_audio_extract(id, {"questions":sanitized_questions,"status":"Completed","completion_percentage":100})
            audio_service.remove_file(file)
        except Exception as chunk_error:
            self.update_audio_extract(id, {"questions":questions,"status":"Failed"})
        
 
    def create_audio_extract(self, file_name: str):
        now=datetime.now()
        try:
            audio_extract = {
                "file_name": file_name,
                "questions": [],
                "status": "In Progress",
                "completion_percentage": 0,
                "is_added_to_portal": False,
                "created_at": now,
                "updated_at": now
            }
            result = self.collection.insert_one(audio_extract)
            logger.info(f"Audio extract added with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to add audio extract: {e}")
            return None
    
    def update_audio_extract(self, id: str,updated_values:dict={}):
        """
        Update the status and completion percentage of an audio extract.
        """
        result = self.collection.update_one({"_id": ObjectId(id)}, {"$set": updated_values})
        if result.matched_count == 0:
            raise NotFoundException(f"Audio extract not found with id {id}")
        return True

    def delete_audio_extract(self, id: str):
        """
        Delete an audio extract record.
        """
        result = self.collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise NotFoundException(f"Audio extract not found with id {id}")
        return True
    
    def sanitize_questions(self, questions):
        """Filters out invalid or redundant questions."""
        sanitized = [question for question in questions if len(question.split()) >= 3]
        return sanitized
