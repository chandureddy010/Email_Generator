import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

class GmailService:
    """
    Gmail service for sending emails through Gmail API.
    """
    
    def __init__(self, credentials_dict):
        """
        Initialize Gmail service with credentials.
        
        Args:
            credentials_dict (dict): User's OAuth credentials
        """
        try:
            # Convert credentials dict to Credentials object
            credentials = Credentials(
                token=credentials_dict.get('token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri=credentials_dict.get('token_uri'),
                client_id=credentials_dict.get('client_id'),
                client_secret=credentials_dict.get('client_secret'),
                scopes=credentials_dict.get('scopes')
            )
            
            # Refresh credentials if needed
            if credentials.expired and credentials.refresh_token:
                request = Request()
                credentials.refresh(request)
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=credentials)
            self.credentials = credentials
            
        except Exception as e:
            print(f"Error initializing Gmail service: {str(e)}")
            raise
    
    def send_email(self, to_email, subject, body, from_email=None):
        """
        Send an email through Gmail API.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body (HTML format)
            from_email (str): Sender email (optional, uses authenticated user)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['subject'] = subject
            
            if from_email:
                message['from'] = from_email
            
            # Create HTML part
            html_part = MIMEText(body, 'html', 'utf-8')
            message.attach(html_part)
            
            # Create plain text version for compatibility
            plain_text = self._html_to_text(body)
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            message.attach(text_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully to {to_email}. Message ID: {send_message.get('id')}")
            return True
            
        except HttpError as error:
            print(f"Gmail API error sending email to {to_email}: {error}")
            return False
        except Exception as error:
            print(f"Unexpected error sending email to {to_email}: {str(error)}")
            return False
    
    def send_bulk_emails(self, email_list):
        """
        Send multiple emails in bulk.
        
        Args:
            email_list (list): List of email dictionaries with 'to', 'subject', 'body'
            
        Returns:
            dict: Results with success count and failed emails
        """
        results = {
            'success_count': 0,
            'failed_emails': [],
            'total_count': len(email_list)
        }
        
        for email_data in email_list:
            try:
                success = self.send_email(
                    email_data['to'],
                    email_data['subject'],
                    email_data['body']
                )
                
                if success:
                    results['success_count'] += 1
                else:
                    results['failed_emails'].append(email_data['to'])
                    
            except Exception as e:
                print(f"Error sending bulk email to {email_data['to']}: {str(e)}")
                results['failed_emails'].append(email_data['to'])
        
        return results
    
    def get_user_profile(self):
        """
        Get the authenticated user's Gmail profile.
        
        Returns:
            dict: User profile information
        """
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'email': profile.get('emailAddress'),
                'messages_total': profile.get('messagesTotal'),
                'threads_total': profile.get('threadsTotal'),
                'history_id': profile.get('historyId')
            }
        except HttpError as error:
            print(f"Error getting user profile: {error}")
            return None
        except Exception as error:
            print(f"Unexpected error getting user profile: {str(error)}")
            return None
    
    def _html_to_text(self, html):
        """
        Convert HTML content to plain text.
        
        Args:
            html (str): HTML content
            
        Returns:
            str: Plain text content
        """
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Replace HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def test_connection(self):
        """
        Test the Gmail API connection.
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            profile = self.get_user_profile()
            return profile is not None
        except:
            return False
