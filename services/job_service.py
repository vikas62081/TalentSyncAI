from email.utils import parsedate_to_datetime
import json

from services.gmail_service import GmailEmailFetcherService
from services.lamma_service import LammaService
from services.sanitize_job_service import SenitizeJobService



import json
from email.utils import parsedate_to_datetime


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
        Extract the following structured JSON from the job description provided. Focus on precise and concise extraction based only on explicit information or clearly inferred insights from the content. Use the following format:

        {{
            "name": "The name of the contact person. Look for the recruiter or hiring manager's name mentioned at the start or end.",
            "email": "The email address of the contact person.",
            "phone": "The phone number of the contact person. Look for numeric patterns or phrases like 'Call' or 'Contact'.",
            "company": "The name of the company associated with the contact person. Look for references to the employer or organization explicitly mentioned in the description.",
            "title": "The title of the job position (e.g., Software Engineer, Data Analyst). Use explicit headings or key phrases like 'Position' or 'Role'.",
            "location": "The location of the job. Include city, state, or mention of 'remote' or 'onsite'.",
            "type": "The type of job (e.g., Contract, Full-time, Part-time). If the duration is mentioned, it typically indicates a contract position.",
            "client_company": "The client's or employer organization's name. Look for explicit references, which could differ from the contact person's company.",
            "rate": "The hourly or annual rate for the position (e.g., $50/hour, $120,000/year).",
            "jobDescription": "A summary or detailed description of the job responsibilities, tasks, and expectations.",
            "skills": "A list of skills or technologies required for the job (e.g., Python, Java, Cloud Computing, AWS). Parse this into an array of strings.",
            "educationRequirements": "The minimum education requirements (e.g., Bachelor's degree, Master's degree).",
            "additionalInfo": "Any extra information, such as special preferences, perks, or conditions."
        }}

        **Guidelines**:
        - If any field is missing from the job description, set its value to `null` or an empty array, as appropriate.
        - Strictly adhere to the provided JSON structure.
        - Validate the JSON structure for accuracy before returning.
        - Ensure all extracted information is precise, concise, and matches explicitly stated content in the job description.
        - Respond in strict JSON format without additional explanations or errors.

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
        return self.llama_service.send_message_to_llama(user_msg=message)


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
                "jobDescription": extract_value("jobDescription"),
                "skills": extract_value("skills", []),
                "educationRequirements": extract_value("educationRequirements"),
                "additionalInfo": extract_value("additionalInfo")
            },
            "rawContent": str(html_text),
            "date": str(email_data.get("date"))
        }
        return json.dumps(formatted_response, indent=4)
