from services.lamma_service import LammaService


class ResumeUpdater:
    SYSTEM_MESSAGE = "You are a resume updater. Align the resume with the given job description, enhancing both technical and soft skills where needed."
    llama_service = None

    def __init__(self):
        """
        Initializes the ResumeUpdater with an instance of LammaService.
        """
        self.llama_service = LammaService()

    def prepare_message(self, resume_chunk: str, job_description: str) -> str:
        """
        Prepares the message to send to the LLaMA model.

        Args:
            resume_chunk (str): A chunk of the resume content.
            job_description (str): The job description content.

        Returns:
            str: Formatted message with instructions and input data.
        """
        return f"""
            **Guidelines**:
            - **Do not remove** any points from the resume.
	        - **Add new points** missing technical skills in Resume from the job description in their respective sections like Summary, Experience, Skills.
	        - **Integrate the new skills seamlessly** while maintaining the flow and structure of the resume.
	        - Strictly adhere to the above guidelines and modify resume according to job description.

            Job Description:
            {job_description.strip()}

            Resume:
            {resume_chunk.strip()}\n
         
            """
        #       {{
        #     "resume": "keep updated resume here",
        #     "modified_point": "a list of points (string) which were added while modifying",
        # }}
        #     Respond using JSON.

    def update_resume_based_on_job_description(self, resume_chunk: str, job_description: str) -> dict:
        """
        Sends the prepared message to the LLaMA model and returns the updated resume.

        Args:
            resume_chunk (str): The portion of the resume to be updated.
            job_description (str): The job description used for alignment.

        Returns:
            dict: The JSON response from the LLaMA model containing the updated resume chunk.
        """
        # Prepare the input message for the LLaMA model
        message = self.prepare_message(resume_chunk, job_description)

        # Send the message to the LammaService
        response = self.llama_service.send_message_to_llama_text(self.SYSTEM_MESSAGE, message)
        return response

    def update_entire_resume(self, resume: str, job_description: str) -> str:
        """
        Updates the entire resume based on the job description by processing it in chunks.

        Args:
            resume (str): The full resume content.
            job_description (str): The job description.

        Returns:
            str: The updated resume.
        """
        # Example of processing the resume in chunks
        updated_resume_chunks = []
        chunks = self.split_resume_into_chunks(resume)

        for chunk in chunks:
            updated_chunk = self.update_resume_based_on_job_description(chunk, job_description)
            updated_resume_chunks.append(updated_chunk)

        return "\n".join(updated_resume_chunks)

    def split_resume_into_chunks(self, resume: str, chunk_size: int = 3000) -> list:
        """
        Splits the resume into manageable chunks for processing.

        Args:
            resume (str): The full resume content.
            chunk_size (int): Maximum size of each chunk. Default is 500 characters.

        Returns:
            list: List of resume chunks.
        """
        return [resume[i:i + chunk_size] for i in range(0, len(resume), chunk_size)]