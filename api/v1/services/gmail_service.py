from datetime import datetime, timedelta
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
        self.email = os.getenv('EMAIL_USER',None)
        self.password = os.getenv('EMAIL_PASSWORD',None)
        self.login(self.email,self.password)

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
            logger.error("email and password required")
            return None
        self.mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        self.mail.login(email, password)
        logger.info(f"Logged in to gmail with email id:" + email)
        self.mail.select("inbox")
        return self.mail

    def search_unread_emails(self,start_uid):
        """
        Search for unread emails in the inbox.

        Returns:
            list: A list of email IDs for unread emails.
        """
        # query = f"UID {start_uid}:*"
        today = datetime.now()
        days_ago = today - timedelta(days=3)

        # Format the date in the IMAP format (DD-Mon-YYYY)
        date_string = days_ago.strftime("%d-%b-%Y")

        # Select the inbox

# Construct the search query to get emails from the last 10 days
        query = f'SINCE {date_string}'
        logger.info(f"Email filter query is: {query}")
        logger.info(f"Processing emails starting from UID: {start_uid}")
        try:
            status, messages = self.mail.search(None, query)
        except imaplib.IMAP4.abort:
            logging.info("Re-authenticating IMAP session...")
            self.mail.logout()
            self.mail.login(self.email, self.password) 
            self.search_unread_emails(start_uid)
        if status == "OK": 
            email_ids = messages[0].split()
            filtered_email_ids = [uid for uid in email_ids if int(uid) >= start_uid]
            logger.info(f"Found {len(filtered_email_ids)} unread emails since UID {start_uid}.")
            return filtered_email_ids
        logger.error(f"Failed to search emails. IMAP status: {status}")
        return []

    def fetch_email(self, email_id):
        """
        Fetch an email by its ID.

        Args:
            email_id (bytes): The ID of the email to fetch.
        
        Returns:
            email.message.Message: Parsed email message object.
        """
        try:
            status, msg_data = self.mail.fetch(email_id, "(RFC822)")
            if status == "OK":
                raw_message = msg_data[0][1]
                return email.message_from_bytes(raw_message)
            return None
        except imaplib.IMAP4.abort:
            logging.info("Re-authenticating IMAP session...")
            self.mail.logout() 
            self.mail.login(self.email, self.password)
            self.fetch_email(email_id)
        except Exception as e:
            logging.error(f"Unexpected error while fetching email {email_id}: {e}")
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
        pattern = r'"([^,]+), ([^"]+)" <([^>]+)>'
        if from_address is not None:
            match = re.match(pattern, from_address)
            if match:
                return match.group(1).strip(), match.group(2), match.group(3)
        return None, None, None

    def logout(self):
        """Logs out and closes the IMAP connection."""
        if self.mail:
            self.mail.close()
            self.mail.logout()
            self.mail = None