import re

from bs4 import BeautifulSoup

class SenitizeJobService:
   
    def sanitize_text_content(self,email_content):
        """Extracts email content using a regex pattern."""
        # Regex pattern to extract email content after "From:"
        pattern = r"(\*From\*.*?)(?=\*Sign-Up\*)"
        
        # Search for the pattern
        match = re.search(pattern,email_content, re.DOTALL)
        
        # Check if there's a match
        if match:
            self.extracted_email = match.group(1).strip()
            return self.extracted_email
        else:
            return email_content

          
    @staticmethod
    def find_parent_recursive(element, levels):
        """Finds the parent of the element up to the specified number of levels."""
        current_element = element
        for _ in range(levels):
            if current_element:
                current_element = current_element.parent
            else:
                return None
        return current_element

    def sanitize_html_content(self, email_content):
        """Extracts and removes unwanted HTML content using regex and BeautifulSoup."""
        soup = BeautifulSoup(email_content, "html.parser")

        # Remove content related to "Remove/unsubscribe"
        target_text = "Remove/unsubscribe"
        target_element = soup.find(string=target_text)
        if target_element:
            parent_tag = self.find_parent_recursive(target_element, levels=5)
            if parent_tag:
                parent_tag.decompose()  # Remove the parent tag and its content

        # Remove content related to "Sign-Up"
        target_text_trail = "Sign-Up"
        target_element = soup.find(string=target_text_trail)
        if target_element:
            parent_tag = self.find_parent_recursive(target_element, levels=7)
            if parent_tag:
                parent_tag.decompose()  # Remove the parent tag and its content
                
                
        target_style = "margin-left:0px;margin-top:30px;margin-right:0px;margin-bottom:25px"
        target_element = soup.find(attrs={"style": target_style})
        if target_element:
            target_element.decompose()
        clean_content = soup.prettify().replace("\n", "").replace("\r", "").strip()

        return clean_content