from fastapi import APIRouter, File, UploadFile, BackgroundTasks

from api.v1.services.process_interview_service import ProcessInterviewService
from models.success_response import SuccessResponse

process_interview_router = APIRouter(tags=["Process Interview"])
process_interview_service = ProcessInterviewService()

@process_interview_router.get("/", summary="Get all interviews")
async def get_all_interviews():
    return process_interview_service.get_audio_extracts()

@process_interview_router.get("/{id}", summary="Get interview by ID")
async def get_interview_by_id(id: str):
    return process_interview_service.get_audio_extract_by_id(id)

@process_interview_router.post("/{id}/questions", summary="Extract questions from interview")
async def extract_questions(id: str):
    return {"message": f"Extracted questions from interview {id}"}

@process_interview_router.post("/upload", summary="Upload interview audio")
async def upload_audio(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    id=process_interview_service.process_audio_file(file,background_tasks=background_tasks)
    return SuccessResponse(data=id,message="Processing audio file")
    
@process_interview_router.put("/{id}/questions", summary="Update extracted questions")
async def update_questions(id: str):
    return {"message": f"Updated questions for interview {id}"} 