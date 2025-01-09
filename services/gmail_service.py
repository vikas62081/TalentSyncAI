import email
import imaplib
import logging
import os
import re

# IMAP server settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GmailEmailFetcherService:
    """Service to fetch and process emails from a Gmail account."""
    
    def __init__(self):
        self.mail = None
        email = os.getenv('EMAIL_USER',None)
        password = os.getenv('EMAIL_PASSWORD',None)
        self.login(email,password)

    def login(self, email, password):
        """
        Connects to the Gmail IMAP server and logs in.
        
        Args:
            username (str): Gmail username.
            password (str): Gmail password.
        
        Returns:
            imaplib.IMAP4_SSL: The IMAP connection object.
        """
        if email is None or password is None:
            print("email and password required")
            return None
        self.mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        self.mail.login(email, password)
        logger.info(f"Logged in to gmail with email id:" + email)
        self.mail.select("inbox")
        return self.mail

    def search_unread_emails(self):
        """
        Search for unread emails in the inbox.

        Returns:
            list: A list of email IDs for unread emails.
        """
        status, messages = self.mail.search(None, "SEEN")
        if status == "OK":
            return messages[0].split()  # Return a list of email IDs
        return []

    def fetch_email(self, email_id):
        """
        Fetch an email by its ID.

        Args:
            email_id (bytes): The ID of the email to fetch.
        
        Returns:
            email.message.Message: Parsed email message object.
        """
        status, msg_data = self.mail.fetch(email_id, "(RFC822)")
        if status == "OK":
            raw_message = msg_data[0][1]
            return email.message_from_bytes(raw_message)
        return None

    def extract_name_and_email(self, from_address):
        """
        Extract the sender's name and email address using regex.

        Args:
            from_address (str): The sender's email header (e.g., "John Doe <john@example.com>").
        
        Returns:
            tuple: A tuple containing the sender's name and email address (name, email).
                   If no match is found, returns (None, None).
        """
        pattern = r"([A-Za-z\s\:\-]+)\s<([^>]+)>"
        match = re.search(pattern, from_address)
        if match:
            return match.group(1).strip(), match.group(2)  # Return name and email
        return None, None

    def logout(self):
        """Logs out and closes the IMAP connection."""
        if self.mail:
            self.mail.close()
            self.mail.logout()
            self.mail = None