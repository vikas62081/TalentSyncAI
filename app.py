from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from bson.errors import InvalidId
from fastapi.middleware.cors import CORSMiddleware
from exceptions.not_found_exception import NotFoundException
from api.v1.services.scheduler_service import SchedulerService
from exceptions.global_exception_handler import already_exists_exception_handler, bad_request_exception_handler, generic_exception_handler, invalid_id_exception_handler, not_found_exception_handler, unauthorized_exception_handler
from exceptions.unauthorized_exception import UnauthorizedException
from exceptions.already_exists_exception import AlreadyExistsException
from exceptions.bad_request_exception import BadRequestException
from api.v1.routes.insight_router import insight_router
from api.v1.routes.process_interview_router import process_interview_router
from config.mongo_db import MongoDBManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

is_prod = os.getenv("ENV", 'dev') == "prod"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting background task on app startup.")
    mongo_manager = MongoDBManager()
    yield
    logger.info("Shutting down scheduler service...")
    mongo_manager.close_connection()
  
    
app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def check_health():
    return {"status": "ThinkAI is running..."}

app.include_router(insight_router,prefix= "/insights")
app.include_router(process_interview_router, prefix="/process_interviews")


# Global Exception handlers
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(BadRequestException, bad_request_exception_handler)
app.add_exception_handler(AlreadyExistsException, already_exists_exception_handler)
app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
app.add_exception_handler(InvalidId, invalid_id_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)