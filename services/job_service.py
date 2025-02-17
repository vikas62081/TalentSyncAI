from email.utils import parsedate_to_datetime
import json

from services.gmail_service import GmailEmailFetcherService
from services.lamma_service import LammaService
from services.sanitize_job_service import SenitizeJobService



import json
from email.utils import parsedate_to_datetime

format={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Extract the name of the contact person if mentioned. Look for phrases like 'Contact', 'Recruiter', or 'Hiring Manager'."
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "The email address associated with the contact person or company, typically found near the contact section."
        },
        "phone": {
            "type": "string",
            "description": "The phone number of the contact person. Search for numeric patterns or terms like 'Call' or 'Contact'."
        },
        "company": {
            "type": "string",
            "description": "The organization explicitly mentioned as hiring. Focus on employer details."
        },
        "title": {
            "type": "string",
            "description": "Designation for the job, such as 'Software Engineer' or 'Data Analyst'. Look for key phrases like 'Position' or 'Role'."
        },
        "client_company": {
            "type": "string",
            "description": "If a staffing company is hiring on behalf of another client, extract the client company's name."
        },
        "rate": {
            "type": "string",
            "description": "The hourly or annual compensation (e.g., $50/hour or $120,000/year) if specified."
        },
        "job_description": {
            "type": "string",
            "description": "A summary of the responsibilities, tasks, and expectations explicitly listed."
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "string"
            },
           "description": "Extract and list all mentioned technologies, programming languages, frameworks, tools, or platforms required for the job (e.g., ['Python', 'AWS', 'JavaScript'])."
        },
        "primary_skill": {
            "type": "string",
            "description": "Identify and extract primary skill required for the job (e.g. Python, Java, Cloud Computing, AWS, Azure, React.js)"
        },
        "education_requirements": {
            "type": "string",
            "description": "The minimum education level (e.g., 'Bachelor's Degree', 'Master's Degree')."
        },
        "additional_info": {
            "type": "string",
            "description": "Any extra details like perks, work conditions, or preferences explicitly mentioned."
        },
        "location": {
            "type": "string",
            "description": "Extract and return the job location in 'City, State' format if it is a US-based position (e.g., 'San Francisco, CA'). If the job is remote, return 'Remote'. If no location is specified or if it is outside the US, return an empty string."
        },
        "city": {
            "type": "string",
            "description": "City name of the job location, it is a US-based position (e.g. 'San Francisco'). If multiple cities are mentioned, return only the first explicitly listed."
        },
        "state": {
            "type": "string",
            "description": "State code  of job location, it is a US-based position (e.g. 'NJ','TX','FL', 'AZ'), If multiple states are mentioned, return only the first explicitly listed."
        }
    },
    "required": ["name", "email", "phone", "company", "title", "type", "job_description", "skills","primary_skill","location","city","state","additional_info","education_requirements"]
}


class JobService:
    """
    A service for processing job descriptions extracted from email messages.
    """
    SYSTEM_MESSAGE = "You are a job description analyzer."

    def __init__(self):
        self.gmail_service = GmailEmailFetcherService()
        self.sanitize_service = SenitizeJobService()
        self.llama_service = LammaService()
        
    def prepare_message(self, job_description):
        """
        Prepare a message to send to the LLaMA model for processing.

        Args:
            job_description (str): The job description content.

        Returns:
            str: Formatted message for the LLaMA model.
        """
        return f"""
        You are an expert in extracting structured information from unstructured text. Your task is to analyze the following job description and output the information in the following JSON structure:

        {{
            "name": "The name of the contact person. Look for the recruiter or hiring manager's name mentioned at the start or end.",
            "email": "The email address of the contact person.",
            "phone": "The phone number of the contact person. Look for numeric patterns or phrases like 'Call' or 'Contact'.",
            "company": "The name of the company associated with the contact person. Look for references to the employer or organization explicitly mentioned in the description.",
            "title": "Title of the job (e.g., Software Engineer, Data Analyst). Use explicit headings or key phrases like ``Position`` or ``Role``.",
            "location": "The location of the job, format should like `city,state`.",
            "type": "The type of job (e.g., Contract, Full-time, Part-time). If the duration is mentioned, it typically indicates a contract position.",
            "client_company": "The client's or employer organization's name. Look for explicit references, which could differ from the contact person's company.",
            "rate": "The hourly or annual rate for the position (e.g., $50/hour, $120,000/year).",
            "job_description": "A summary or detailed description of the job responsibilities, tasks, and expectations.",
            "skills": "A list of skills or technologies required for the job (e.g., Python, Java, Cloud Computing, AWS). Parse this into an array of strings.",
            "primary_skill":"Primary Skill required for the job (e.g. Python, Java, Cloud Computing, AWS, Azure, React.js)"
            "education_requirements": "The minimum education requirements (e.g., Bachelor's degree, Master's degree).",
            "additional_info": "Any extra information, such as special preferences, perks, or conditions."
        }}

        **Guidelines**:
        - If any field is missing from the job description, set its value to `null` or an empty array, as appropriate

        Job Description: {job_description}
        Respond using JSON.
        """


    def process_email_job(self, message):
        """
        Process the email to extract metadata, body content, and sender details.

        Args:
            message (email.message.Message): The email message object.

        Returns:
            dict: Extracted email details including plain text, HTML body, and metadata.
        """
        name, sender_email = self.gmail_service.extract_name_and_email(message["From"])
        subject = message["Subject"]
        from_addr = message["From"]
        to_addr = message["To"]
        date = parsedate_to_datetime(message["Date"])

        plain_text, html_body = self._extract_email_body(message)

        return {
            "subject": subject,
            "from": from_addr,
            "name": name,
            "email": sender_email,
            "to": to_addr,
            "plain_text": plain_text,
            "html_body": html_body,
            "date": date,
        }

    def process_emails(self):
        """
        Process unread emails, sanitize their content, and extract job descriptions.
        """

        # Fetch unread emails
        email_ids = self.gmail_service.search_unread_emails()
        if not email_ids:
            print("No new emails to process.")
            return

        # Process each email
        for email_id in [email_ids[-1]]:  # Process the last two emails for demonstration
            msg = self.gmail_service.fetch_email(email_id)
            email_data = self.process_email_job(msg)

            # Sanitizing(Cleaning) content
            plain_text = self.sanitize_service.sanitize_text_content(email_data["plain_text"])
            html_text = self.sanitize_service.sanitize_html_content(email_data["html_body"])

            # Extract strctured data from job description
            response = self.extract_job_description(plain_text)
            
            # Formatting response to json 
            return self.format_response(email_data,response,html_text)


    def extract_job_description(self, job_description):
        """
        Extract structured JSON data from the job description.

        Args:
            job_description (str): The job description text.

        Returns:
            dict: Structured JSON data extracted from the job description.
        """
        message = self.prepare_message(job_description)
        return self.llama_service.send_message_to_llama_generate(user_msg=message)


    def _extract_email_body(self, message):
        """
        Extract the plain text and HTML body from the email.

        Args:
            message (email.message.Message): The email message object.

        Returns:
            tuple: Plain text content and HTML body content.
        """
        plain_text = ""
        html_body = ""

        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    plain_text = part.get_payload(decode=True).decode()
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    html_body = part.get_payload(decode=True).decode()
        else:
            plain_text = message.get_payload(decode=True).decode()

        return plain_text, html_body
    
    def format_response(self, email_data, response, html_text):
        def extract_value(key, default=None):
            """Utility to extract values from response with a fallback."""
            return response.get(key, default)

        formatted_response= {
            "subject": email_data.get("subject",None),
            "sourceType": "GMAIL",
            "sender": {
                "from": email_data.get("email",None) 
            },
            "contact": {
                "name": email_data.get("name") or extract_value("name"),
                "email": extract_value("email"),
                "phone": extract_value("phone"),
                "company": extract_value("company")
            },
            "jobDetails": {
                "title": extract_value("title"),
                "location": extract_value("location"),
                "type": extract_value("type","Contract"),
                "company": extract_value("client_company"),
                "rate": extract_value("rate"),
                "jobDescription": extract_value("job_description"),
                "primarySkill": extract_value("primary_skill"),
                "skills": extract_value("skills", []),
                "educationRequirements": extract_value("education_requirements"),
                "additionalInfo": extract_value("additional_info")
            },
            "rawContent": str(html_text),
            "date": str(email_data.get("date"))
        }
        return json.dumps(formatted_response, indent=4)
