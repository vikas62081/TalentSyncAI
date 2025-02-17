from fastapi import status

class AlreadyExistsException(Exception):
    def __init__(self,message:str ):
        self.message=message
        self.status_code=status.HTTP_409_CONFLICT