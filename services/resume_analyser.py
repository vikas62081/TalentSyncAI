

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
        Output the results in the following JSON structure:
        {{
            "skills":"List of skills (job_description_required_skills) and the skills listed in the resume (candidate_skills)",
            "job_skills_required":"List of job_description_required_skills",
            "resume_skills:"List of candidate_skills",
            "matching_skills": "List of matching technical skills resume vs job description (e.g., Python, React.js).",
            "missing_skills": "List of missing technical skills."
            "experience_percentage_in_number": "Percentage match number for experience based on job description required experience.",
            "technical_skills_percentage_in_number": "Percentage number of technical skills explicitly matching between the resume and the job description.",
            "soft_skills_percentage_in_number": "Percentage match number of soft skills explicitly mentioned in both the resume and job description.",
            "overall_percentage_in_number": "Overall percentage match number between resume and job description, considering all factors.",
        }}
        
        Input:
            Resume:
            {resume_chunk.strip().lower()}

            Job Description:
            {job_description.strip().lower()}

        Respond strictly in JSON format without additional explanations.
        """

    def calculate_resume_match(self,resume:str, job_description:str, chunk_size=6000):
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
            'skills_required':[]
        }

        # Process each chunk
        for chunk in resume_chunks:
            message = self.prepare_message(chunk, job_description)
            response_data = lamma_service.send_message_to_llama_chat(user_msg= message)
            if not response_data:
                print("Error: Failed to process a chunk.")
                continue
            print(response_data["skills"])
            # Aggregate results
            aggregated_results['overall'] = max(aggregated_results['overall'], int(response_data.get('overall_percentage_in_number', 0)))
            aggregated_results['soft_skills_match'] = max(aggregated_results['soft_skills_match'], response_data.get('soft_skills_percentage_in_number', 0))
            aggregated_results['technical_match'] = max(aggregated_results['technical_match'], response_data.get('technical_skills_percentage_in_number', 0))
            aggregated_results['experience_match'] = max(aggregated_results['experience_match'], response_data.get('experience_percentage_in_number', 0))
            aggregated_results['matching_skills'].extend(response_data.get('matching_skills', []))
            aggregated_results['missing_skills'].extend(response_data.get('missing_skills', []))
            aggregated_results["skills_required"].extend(response_data.get('job_skills_required', []))
            
            

        # Remove duplicate skills
        matching_skills=self.remove_duplicates_case_insensitive(aggregated_results['matching_skills'])
        missing_skills=self.remove_duplicates_case_insensitive(aggregated_results['missing_skills'])
        skills_required=self.remove_duplicates_case_insensitive(aggregated_results['skills_required'])
        
        missing_skills=self.compare_and_filter_skills(matching_skills,missing_skills)
        
        aggregated_results['matching_skills'] = matching_skills
        aggregated_results['missing_skills'] = missing_skills
        aggregated_results["skills_required"]=skills_required

        return aggregated_results
    def analyze_resume_for_job(self,resume, job_description):

        if resume and job_description:
            match_result = self.calculate_resume_match(resume, job_description)

            if match_result:
                return match_result
            else:
                print("Failed to calculate resume match.")
                
    def compare_and_filter_skills(self,matching_skills, missing_skills):
        matching_skills_lower = {skill.lower() for skill in matching_skills}
        filtered_missing_skills = [skill for skill in missing_skills if skill.lower() not in matching_skills_lower]
        return filtered_missing_skills
    
    def remove_duplicates_case_insensitive(self,skills):
    # Use a set to keep track of skills in lowercase (case insensitive)
        unique_skills = set()
        
        # Create a new list that only includes skills that have not been seen yet
        result = []
        for skill in skills:
            # Convert skill to lowercase for case-insensitive comparison
            lower_skill = skill.lower()
            
            # Add to the result only if it hasn't been seen yet
            if lower_skill not in unique_skills:
                result.append(skill)
                unique_skills.add(lower_skill)
        
        return result