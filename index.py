

import json
import os
from services.audio_service import AudioService
from services.job_service import JobService
from services.resume_analyser import ResumeAnalyser
from services.resume_updater import ResumeUpdater

from dotenv import load_dotenv

default_env_file_name=".env"
questions=['If they ask to share the screen I will do the coding and everything sequel.', 'How many years?', 'So if they ask like how much year of experience just increase the width, increase the width and height both.', 'At least increase the height first.', 'Increase the height, height means length.', 'Can you do that?', 'How many years of experience do you have in total?', 'What experience do you have with Python and SQL?', 'From your starting of your career', 'You are working on Python and SQL because these Infosys service based company used to ask.', 'What was like in my day to day activity', "If the ask like have you worked on cloud composer you can say that yeah it's the same like air flow we should use our jobs like", 'You have opened it now?', 'Just leave the laptop.', 'Just open your mail, the call and everything, just open it.', 'Have you all down CICD?', 'Where we, you have used Jenkins?', 'Why you are going too far here?', 'Can you just play the YouTube video?', 'Any YouTube video just do that.', 'I just want to check that.', '', '', '', '', "So it's possible", 'we have the terror data source', "it's like a terror data, we have a terror data", 'So we are pulling the data from the terror data and dumping the data into the cloud storage', 'So, what we have in our current project', 'So, what we are doing', 'So, previously what we have everything we have in the terror data', 'So, now what we are doing we are moving from the terror data to the GCP', 'In the terror data what we have we have the data sum of the data source', 'From that we are creating our data pipeline basically a ETL pipeline which include extraction transformation and load', 'What kind of extraction you are doing from terror data?', 'In the transformation, what cleansing operation are you performing?', 'When you say type of transformation?', 'What business logic did you get from the stakeholders?', 'How do we transform those types of logic?', 'When does the subscription end?', 'When should the employee receive an alert based on the subscription?', 'When I say cleansing operation like removing of the duplicate values, so we used to remove the duplicate value based on the primary key.', 'How did you get the primary key from the data model?', 'What is the process for removing null values?', 'Can you explain the transformation process you described earlier?', 'How does the data get loaded from the GCS bucket to BigQuery?', 'How is data transferred from Tara data to the GCS bucket?', 'Is the process of loading data from GCS bucket to BigQuery automated or manual?', 'Can this process be used across the team?', 'To pull the data from the terror data and store that into the cloud storage, basically, what all steps are required?', 'A list of string of question', {'question': 'What can be done in BigQuery optimization?'}, {'question': 'How to reduce data scan?'}, {'question': 'Is it possible to select specific columns?'}, {'question': 'Can you explain partitioning on the data set while creating the data in BigQuery?'}, {'question': 'Why do we make sure to partition the data in BigQuery?'}, {'question': 'How does partitioning affect data scanning?'}, {'question': 'What is the benefit of applying filters while pulling the data?'}, 'Can apply that filter condition so that will be helpful for that.', 'We can use the BigQuery caching function?', 'How can we reuse cache result basically?', 'What is partitioning and how does it divide the data?', 'Can you explain how both optimization techniques, partition and cluster, come into play?', 'How can we apply a filter based on a specific column when partitioning?', "Is there a situation where partition isn't suitable, such as high cardinality?", 'Can you describe how clustering organizes data within each partition by sorting rows based on a specific column?', 'what can we do?', 'We can do that based on the date', 'We can do that based on the date', 'if you are asking clustering or clustering what we can do', 'and clustering on employee ID optimize the filter and grouping for employee related query', 'While pulling the data set, we encode and decode it based on what requirement?', 'How do you handle encoded and decoded datasets in BigQuery?', 'Why are business users sometimes using decoding while your team is using encoding?', 'What hashing method do you use for a specific column?', 'Can we retrieve the table?', 'what we can do', "where basically I'm going to do", 'What can we do?', 'What can we do based on the project?', 'What is the current time stream?', 'What was the date?', 'What is the meaning of this text?', {'text': ''}, {'text': 'Might be the same data is coming twice and in the same time that is why it is not pulling the correct data.'}, '', 'So what we can do', 'from Google Cloud', 'Can define the local file path basically from where we are file', 'And that what we will check the bucket is there or not', 'And then what we do we will call the blob storage to upload the file.', 'the file upload from the file name. ', 'Basically, we will give the file local file path.', '', 'please', 'What will happen if the bucket does not exist?', 'How will the storage client handle a non-existent bucket?', '', '', 'Can you explain how you are using the row number in your query?', 'How does the window function relate to the row number?', 'Is there a specific reason why you chose to use a window function here?', 'How do you get the rank with the window function?', 'What is the significance of 1.5% in this context?', 'A list of string of question', 'So what would be the next round like that?']

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
    audio_file = "./data/Note.mp3"
    resume = read_txt_file(resume_file)
    job_description = read_txt_file(job_description_file)
    
    # Analyser 
    # job_des=ResumeAnalyser().analyze_resume_for_job(resume, job_description)
    # print(json.dumps(job_des, indent=4))

    # Job insights 
    # job_service=JobService()
    # print(job_service.process_emails())
    
    # update resume 
    # resume_updater_service = ResumeUpdater()
    # print(resume_updater_service.update_resume_based_on_job_description(resume,job_description))
    
    #Interview audio processor
    audio_service=AudioService(audio_file)
    print(json.dumps(audio_service.process_audio(),indent=4))
    
    
    
      # job_description_service = JobDescriptionService(format_json_file_path="format.json")
      # job_description = job_description_service.read_txt_file(file_path="job_description.txt")
      # response = job_description_service.extract_job_description(job_description)
      # json_response = job_description_service.parse_json_response(response)
      # if json_response:
      #   print(json.dumps(json_response, indent=4))


if __name__ == "__main__":
    main()