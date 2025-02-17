from fastapi import status

class BadRequestException(Exception):
    def __init__(self,message:str ):
        self.message=message
        self.status_code=status.HTTP_400_BAD_REQUEST