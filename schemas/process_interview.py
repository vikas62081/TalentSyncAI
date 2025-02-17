def interview_helper(interview)->dict:
   return {
        "id": str(interview.get("_id", None)),
        "file_name": interview.get("file_name", None),
        "status":interview.get("status", None),
        "completion_percentage": interview.get("completion_percentage", None),
        "is_added_to_portal": interview.get("is_added_to_portal", None),
        "questions": interview.get("questions", None),
        "created_at": interview.get("created_at", None),
        "updated_at": interview.get("updated_at", None),
    }


def interviews_helper(interviews)->list:
    return [interview_helper(interview) for interview in interviews]

