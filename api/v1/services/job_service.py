from email.utils import parsedate_to_datetime
import logging
from email.utils import parsedate_to_datetime

from api.v1.services.gmail_service import GmailEmailFetcherService
from api.v1.services.lamma_service import LammaService
from api.v1.services.sanitize_job_service import SenitizeJobService
from api.v1.services.metadata_service import MetadataService
from api.v1.services.insight_service import InsightService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
           "description": "Technologies, programming languages, frameworks, tools, or platforms mentioned in job description (e.g., ['Python', 'AWS', 'JavaScript'])."
        },
        "primary_skill": {
            "type": "string",
            "description": "Primary (main) skill required for the job (e.g. Python, Java, Cloud Computing, AWS, Azure, React.js)"
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
            "description": "Should be a string of the city name for the job location."
        },
        "state": {
            "type": "string",
            "description": "Should be two letters of the state code representing the job's location."
        },
        "category": {
            "type": "string",
            "enum": ["Frontend", "Backend", "Data Engineer", "Cloud", "FullStack", "QA", "Mobile Development", "DevOps", "AI", "Others"],
            "description": "Based on the job description provided below, classify the job into one of the enum mentioned categories"
            
        }
    },
    "required": ["name", "email", "phone", "company", "title", "job_description", "skills","primary_skill","location","city","state","additional_info","education_requirements","category"]
}

class JobService:
    """
    A service for processing job descriptions extracted from email messages.
    """
    SYSTEM_MESSAGE = """You are a system designed to parse job descriptions into a structured JSON format. 
    For each job description provided, extract explicit or clearly inferred information into the corresponding fields.
    If any field is missing or cannot be reasonably inferred, set its value to null or an empty array (as appropriate)."""

    def __init__(self):
        self.gmail_service = GmailEmailFetcherService()
        self.sanitize_service = SenitizeJobService()
        self.llama_service = LammaService()
        self.metadata_service=MetadataService()
        self.insight_service=InsightService()
        
    def prepare_message(self, job_description):
        """
        Prepare a message to send to the LLaMA model for processing.

        Args:
            job_description (str): The job description content.

        Returns:
            str: Formatted message for the LLaMA model.
        """
        return f"""Extract the following structured JSON from the job description. Only include explicit or clearly inferred information. 
            If a field is missing or cannot be inferred, set its value to null or an empty array, as appropriate:
            
            Guidelines:\n Return only the category name\n
            **Input:**  {job_description}\n
            **Output:**  
            Respond in the format JSON structure."""

    def process_email_job(self, message):
        """
        Process the email to extract metadata, body content, and sender details.

        Args:
            message (email.message.Message): The email message object.

        Returns:
            dict: Extracted email details including plain text, HTML body, and metadata.
        """
        name, company, sender_email = self.gmail_service.extract_name_and_email(message["Reply-To"])
        subject = message["Subject"]
        from_addr = message["From"]
        to_addr = message["To"]
        date = parsedate_to_datetime(message["Date"])

        plain_text, html_body = self._extract_email_body(message)
        return {
            "subject": subject,
            "from": from_addr,
            "name": name.capitalize(),
            "email": sender_email,
            "vendor":company.title(),
            "to": to_addr,
            "plain_text": f"""Subject:{subject}\n{plain_text}""",
            "html_body": html_body,
            "date": date,
        }

    def process_emails(self):
        """
        Process unread emails, sanitize their content, and extract job descriptions.
        """
        
        start_uid=self.metadata_service.get_metadata("start_email_id") or 16
        # Fetch unread emails
        email_ids = self.gmail_service.search_unread_emails(start_uid)
        if not email_ids:
            logger.info("No new emails to process.")
            return
        logging.info(f"Processing unread emails, Total: {len(email_ids)}")
        # Process each email
        for email_id in email_ids:  # Process the last two emails for demonstration
            msg = self.gmail_service.fetch_email(email_id)
            email_id_int=int(email_id)
            try:
                email_data = self.process_email_job(msg)
               
                
                if self.insight_service.is_insight_already_exsit(sender_email=email_data['email'],email_subject=email_data['subject']):
                    logger.warning(f"Duplicate insight: Id: {email_id_int}, subject: {email_data['subject']}, email: {email_data['email']}")
                    continue
                logger.info(f"Processing started for email: {email_id_int}")

                # Sanitizing(Cleaning) content
                plain_text = self.sanitize_service.sanitize_text_content(email_data["plain_text"])
                html_text = self.sanitize_service.sanitize_html_content(email_data["html_body"])
                # Extract strctured data from job description
                response = self.extract_job_description(plain_text)
                if response is None:
                    logger.warning(f"Something went wrong with the LLM model while processing email ID: {email_id_int}. Skipping this opportunity")
                    continue
                logger.info(f"Processing completed email: {email_id_int}")
                # Formatting response to json 
                insight=self.format_response(email_data,response,html_text)
                self.insight_service.add_insight(insight=insight)
                self.metadata_service.set_metadata("start_email_id",email_id_int)
            except Exception as e:
                logger.error(f"Something went wrong while processing email ID: {email_id_int}.error: {e}")
        
        
    def extract_job_description(self, job_description):
        """
        Extract structured JSON data from the job description.

        Args:
            job_description (str): The job description text.

        Returns:
            dict: Structured JSON data extracted from the job description.
        """
        message = self.prepare_message(job_description)
        return self.llama_service.send_message_to_llama_chat(user_msg=message,sys_msg=self.SYSTEM_MESSAGE,format=format)


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
            if response is not None:
                value = response.get(key, default)
                return None if value == "null" else value
            return default

        formatted_response= {
                            "subject": email_data.get("subject", None),
                            "sourceType": "GMAIL",
                            "sender": {
                                "from": email_data.get("email", extract_value("email"))
                            },
                            "category":extract_value("category","Others"),
                            "contact": {
                                "name": email_data.get("name",extract_value("name")),
                                "email": email_data.get("email",extract_value("email")),
                                "phone": extract_value("phone"),
                                "company": email_data.get("vendor",extract_value("company"))
                            },
                            "jobDetails": {
                                "title": extract_value("title"),
                                "location": extract_value("location"),
                                "state": extract_value("state"),
                                "city": extract_value("city"),
                                "type": extract_value("type", "Contract"), 
                                "company": extract_value("client_company"),
                                "rate": extract_value("rate"),
                                "jobDescription": extract_value("job_description"),
                                "primarySkill": extract_value("primary_skill"),
                                "skills": extract_value("skills", []),
                                "educationRequirements": extract_value("education_requirements"),
                                "additionalInfo": extract_value("additional_info") 
                            },
                            "rawContent": str(html_text),  
                            "date": email_data.get("date")
                        }
        return formatted_response