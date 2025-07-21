import requests
import json
import time
from .email_templates import EmailTemplates

class EmailGenerator:
    """
    AI-powered email generator using OpenRouter API.
    """
    
    def __init__(self, api_key):
        """
        Initialize EmailGenerator with OpenRouter API key.
        
        Args:
            api_key (str): OpenRouter API key
        """
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.templates = EmailTemplates()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "AI Email Generator"
        }
    
    def generate_email(self, email_type, recipient_email, custom_instructions="", sender_name=""):
        """
        Generate an email using AI.
        
        Args:
            email_type (str): Type of email to generate
            recipient_email (str): Recipient's email address
            custom_instructions (str): Additional instructions for AI
            sender_name (str): Name of the sender
            
        Returns:
            dict: Generated email with subject and body
        """
        try:
            template = self.templates.get_template(email_type)
            
            # Create comprehensive prompt
            prompt = self._create_email_prompt(
                email_type, 
                recipient_email, 
                template, 
                custom_instructions, 
                sender_name
            )
            
            # Make API request
            response = self._make_api_request(prompt)
            
            if response:
                return self._parse_response(response, email_type)
            else:
                return self._fallback_email(email_type, recipient_email)
                
        except Exception as e:
            print(f"Error generating email: {str(e)}")
            return self._fallback_email(email_type, recipient_email, str(e))
    
    def generate_bulk_emails(self, email_type, email_list, custom_instructions="", sender_name=""):
        """
        Generate multiple emails for different recipients.
        
        Args:
            email_type (str): Type of email to generate
            email_list (list): List of recipient email addresses
            custom_instructions (str): Additional instructions for AI
            sender_name (str): Name of the sender
            
        Returns:
            list: List of generated emails
        """
        generated_emails = []
        
        for recipient_email in email_list:
            try:
                email_content = self.generate_email(
                    email_type, 
                    recipient_email, 
                    custom_instructions, 
                    sender_name
                )
                
                generated_emails.append({
                    'recipient': recipient_email,
                    'subject': email_content['subject'],
                    'body': email_content['body'],
                    'email_type': email_type
                })
                
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error generating email for {recipient_email}: {str(e)}")
                fallback = self._fallback_email(email_type, recipient_email, str(e))
                generated_emails.append({
                    'recipient': recipient_email,
                    'subject': fallback['subject'],
                    'body': fallback['body'],
                    'email_type': email_type
                })
        
        return generated_emails
    
    def _create_email_prompt(self, email_type, recipient_email, template, custom_instructions, sender_name):
        """
        Create a comprehensive prompt for email generation.
        """
        recipient_name = self._extract_name_from_email(recipient_email)
        
        prompt = f"""
        You are a professional email writing assistant. Generate a {email_type} email with the following specifications:

        **Email Type**: {email_type}
        **Template Guidelines**: {template}
        **Recipient Email**: {recipient_email}
        **Recipient Name**: {recipient_name if recipient_name else "there"}
        **Sender Name**: {sender_name if sender_name else "the sender"}
        
        **Additional Instructions**: {custom_instructions if custom_instructions else "None"}
        
        **Requirements**:
        1. Create an engaging and appropriate subject line
        2. Write a well-structured email body in HTML format
        3. Include proper greetings and closings
        4. Make it personalized and relevant
        5. Ensure the tone matches the email type
        6. Keep it professional yet engaging
        7. Make sure the HTML is clean and renders well in email clients
        
        **Response Format** (JSON only):
        {{
            "subject": "compelling subject line here",
            "body": "well-formatted HTML email body here"
        }}
        
        Generate the email now:
        """
        
        return prompt
    
    def _make_api_request(self, prompt):
        """
        Make API request to OpenRouter.
        """
        try:
            data = {
                "model": "anthropic/claude-3-sonnet",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional email writing assistant. Always respond with valid JSON containing 'subject' and 'body' fields. The body should be in HTML format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = requests.post(
                self.base_url, 
                json=data, 
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error in API request: {str(e)}")
            return None
    
    def _parse_response(self, response, email_type):
        """
        Parse the API response and extract email content.
        """
        try:
            content = response['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                parsed_content = json.loads(content)
                return {
                    'subject': parsed_content.get('subject', f'{email_type.title()} Email'),
                    'body': parsed_content.get('body', content)
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract content manually
                return self._extract_content_manually(content, email_type)
                
        except (KeyError, IndexError) as e:
            print(f"Error parsing API response: {str(e)}")
            return self._fallback_email(email_type, "")
    
    def _extract_content_manually(self, content, email_type):
        """
        Extract email content when JSON parsing fails.
        """
        try:
            lines = content.split('\n')
            subject = f'{email_type.title()} Email'
            body = content
            
            # Look for subject line patterns
            for line in lines:
                if 'subject' in line.lower() and ':' in line:
                    potential_subject = line.split(':', 1)[1].strip()
                    if potential_subject:
                        subject = potential_subject.strip('"\'')
                    break
            
            # Clean up body content
            body = content.replace(f'Subject: {subject}', '').strip()
            if not body.startswith('<'):
                body = f'<p>{body.replace(chr(10), "</p><p>")}</p>'
            
            return {
                'subject': subject,
                'body': body
            }
            
        except Exception as e:
            print(f"Error in manual content extraction: {str(e)}")
            return self._fallback_email(email_type, "")
    
    def _extract_name_from_email(self, email):
        """
        Extract a name from email address for personalization.
        """
        try:
            if '@' in email:
                local_part = email.split('@')[0]
                # Replace common separators and capitalize
                name = local_part.replace('.', ' ').replace('_', ' ').replace('-', ' ')
                return ' '.join(word.capitalize() for word in name.split())
            return None
        except:
            return None
    
    def _fallback_email(self, email_type, recipient_email, error_msg=""):
        """
        Generate a fallback email when AI generation fails.
        """
        fallback_content = self.templates.get_fallback_content(email_type, recipient_email)
        
        return {
            'subject': fallback_content['subject'],
            'body': fallback_content['body'] + (
                f"<p><small><em>Note: This is a fallback email due to generation error: {error_msg}</em></small></p>"
                if error_msg else ""
            )
        }
    
    def test_api_connection(self):
        """
        Test the OpenRouter API connection.
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            test_prompt = "Generate a simple test response in JSON format with 'subject' and 'body' fields."
            response = self._make_api_request(test_prompt)
            return response is not None and 'choices' in response
        except:
            return False
