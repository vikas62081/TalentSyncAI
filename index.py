

import os
from services.job_service import JobService
from services.resume_analyser import ResumeAnalyser
from services.resume_updater import ResumeUpdater

from dotenv import load_dotenv

default_env_file_name=".env"

BASEDIR = os.path.abspath(os.path.dirname(__file__)) 
load_dotenv(os.path.join(BASEDIR, default_env_file_name))

def read_txt_file(file_path:str):
        """
        Reads the content of a text file.

        Args:
            file_path (str): Path to the text file.

        Returns:
            str: Content of the file if successful, otherwise None.
        """
        try:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                if not content:
                    raise ValueError(f"File {file_path} is empty.")
                return content
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
        except ValueError as ve:
            print(f"Error: {ve}")
        return None

def main():
    resume_file = "./data/resume.txt"
    job_description_file = "./data/job_description.txt"
    resume = read_txt_file(resume_file)
    job_description = read_txt_file(job_description_file)
    
    # Analyser 
    #   ResumeAnalyser().analyze_resume_for_job(resume, job_description)

    # Job insights 
    # job_service=JobService()
    # print(job_service.process_emails())
    
    # update resume 
    resume_updater_service = ResumeUpdater()
    print(resume_updater_service.update_resume_based_on_job_description(resume,job_description))
    
    
      # job_description_service = JobDescriptionService(format_json_file_path="format.json")
      # job_description = job_description_service.read_txt_file(file_path="job_description.txt")
      # response = job_description_service.extract_job_description(job_description)
      # json_response = job_description_service.parse_json_response(response)
      # if json_response:
      #   print(json.dumps(json_response, indent=4))


if __name__ == "__main__":
    main()