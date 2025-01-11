

from services.lamma_service import LammaService


lamma_service=LammaService()

class ResumeAnalyser:
    
    sys_msg="You are a resume analyzer."

    def split_into_chunks(self,text:str, max_length:int):
        """
        Splits the text into chunks of a specified maximum length.

        Args:
            text (str): The input text.
            max_length (int): Maximum length of each chunk.

        Returns:
            list: List of text chunks.
        """
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            # Check if adding the current word exceeds the chunk size
            if len(" ".join(current_chunk + [word])) > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
            current_chunk.append(word)

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
    
    def prepare_message(self,resume_chunk:str, job_description:str):
        """
        Prepares the message to send to the LLaMA model.

        Args:
            resume_chunk (str): A chunk of the resume content.
            job_description (str): The job description content.

        Returns:
            str: Formatted message.
        """
        return f"""
        Compare the following resume chunk and job description. Provide a structured JSON response with the requested fields. Focus on providing consistent and concise results based only on explicit matches and clearly inferred insights from the content. Use the following format:

        {{
            "overall": "Overall percentage match number between resume and job description, considering all factors.",
            "experience": "Percentage match number for experience based on job description required experience.",
            "technical_skills": "Percentage number of technical skills explicitly matching between the resume and the job description.",
            "soft_skills": "Percentage match number of soft skills explicitly mentioned in both the resume and job description.",
            "matching_skills": "List of skills technical matching explicitly between the resume and job description.",
            "missing_skills": "List of technical skills missing in resume "
        }}

        Resume Chunk: {resume_chunk}\n
        Job Description: {job_description}\n
        Respond using JSON.

        **Guidelines**:
        - Be precise and consistent in evaluating skills and experience.
        - Use explicit text matches and clearly inferred data to populate the JSON fields.
        - For percentages, calculate based on the number of matches relative to the total number of requirements in the job description.
        - Avoid redundant or vague information.
        - Respond in strict JSON format without any additional explanation.
        - All percentage values should be integers (no floating points) and should not include % symbols.
        """

    def calculate_resume_match(self,resume:str, job_description:str, chunk_size=3000):
        """
        Calculates the resume match percentage using LLaMA, handling large resumes by chunking.

        Args:
            resume (str): The resume content.
            job_description (str): The job description content.
            chunk_size (int): Maximum character length for each chunk of the resume.

        Returns:
            dict: Aggregated results from all chunks.
        """
        if not resume or not job_description:
            print("Error: Resume or Job Description is missing.")
            return None

        # Split resume into chunks
        resume_chunks = self.split_into_chunks(resume, chunk_size)

        aggregated_results = {
            'overall': 0,
            'soft_skills_match': 0,
            'technical_match': 0,
            'experience_match': 0,
            'matching_skills': [],
            'missing_skills': [],
        }

        # Process each chunk
        for chunk in resume_chunks:
            message = self.prepare_message(chunk, job_description)
            response_data = lamma_service.send_message_to_llama(user_msg= message)
            if not response_data:
                print("Error: Failed to process a chunk.")
                continue

            # Aggregate results
            aggregated_results['overall'] += response_data.get('overall', 0)
            aggregated_results['soft_skills_match'] += response_data.get('soft_skills', 0)
            aggregated_results['technical_match'] += response_data.get('technical_skills', 0) #Need to work on aggregate results
            aggregated_results['experience_match'] += response_data.get('experience', 0)
            aggregated_results['matching_skills'].extend(response_data.get('matching_skills', []))
            aggregated_results['missing_skills'].extend(response_data.get('missing_skills', []))

        # Normalize aggregated results
        num_chunks = len(resume_chunks)
        if num_chunks > 0:
            aggregated_results['overall'] //= num_chunks
            aggregated_results['soft_skills_match'] //= num_chunks
            aggregated_results['technical_match'] //= num_chunks
            aggregated_results['experience_match'] //= num_chunks

        # Remove duplicate skills
        aggregated_results['matching_skills'] = list(set(aggregated_results['matching_skills']))
        aggregated_results['missing_skills'] = list(set(aggregated_results['missing_skills']))

        return aggregated_results
    def analyze_resume_for_job(self,resume, job_description):

        if resume and job_description:
            match_result = self.calculate_resume_match(resume, job_description)

            if match_result:
                return match_result
            else:
                print("Failed to calculate resume match.")