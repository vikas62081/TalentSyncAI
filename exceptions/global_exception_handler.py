# api/v1/exceptions/global_exception_handler.py

from fastapi import Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from bson.errors import InvalidId
from models.error_response import ErrorResponse
from exceptions.not_found_exception import NotFoundException
from exceptions.bad_request_exception import BadRequestException
from exceptions.already_exists_exception import AlreadyExistsException
from exceptions.unauthorized_exception import UnauthorizedException

async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = exc.errors()[0]
    message = str(error_details['loc'][1]) + " " + error_details['msg']
    try:
        message = message.split(",")[1]
    except IndexError:
        pass
    return ErrorResponse(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY).send()


async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return ErrorResponse(message=exc.message, status_code=exc.status_code).send()


async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return ErrorResponse(message=exc.message, status_code=exc.status_code).send()


async def already_exists_exception_handler(request: Request, exc: AlreadyExistsException):
    return ErrorResponse(message=exc.message, status_code=exc.status_code).send()


async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return ErrorResponse(message=exc.message, status_code=exc.status_code).send()


async def invalid_id_exception_handler(request: Request, exc: InvalidId):
    return ErrorResponse(message=str(exc), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY).send()


async def http_exception_handler(request: Request, exc: HTTPException):
    return ErrorResponse(message=str(exc.detail), status_code=exc.status_code).send()


async def generic_exception_handler(request: Request, exc: Exception):
    return ErrorResponse(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR).send()