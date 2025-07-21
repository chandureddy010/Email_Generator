"""
Email templates and fallback content for different email types.
"""

class EmailTemplates:
    """
    Email templates manager for different email types.
    """
    
    def __init__(self):
        """
        Initialize email templates with comprehensive guidelines.
        """
        self.templates = {
            'professional': {
                'description': 'Write a professional, formal business email with proper greeting and closing. Use formal language, clear structure, and maintain a respectful tone.',
                'tone': 'formal, respectful, clear',
                'structure': 'formal greeting, clear purpose, detailed content, professional closing'
            },
            'comedy': {
                'description': 'Write a humorous, light-hearted email that brings a smile while maintaining respect. Use appropriate humor, wordplay, or funny observations.',
                'tone': 'humorous, light, respectful, entertaining',
                'structure': 'engaging opener, humorous content, respectful closing'
            },
            'friendly': {
                'description': 'Write a warm, casual email as if writing to a good friend. Use conversational language and friendly tone.',
                'tone': 'warm, casual, conversational, friendly',
                'structure': 'casual greeting, friendly conversation, warm closing'
            },
            'formal': {
                'description': 'Write a very formal, official email with proper business etiquette. Use traditional formal language and structure.',
                'tone': 'highly formal, official, traditional',
                'structure': 'formal salutation, official content, traditional closing'
            },
            'casual': {
                'description': 'Write a relaxed, informal email with a conversational tone. Keep it simple and easy-going.',
                'tone': 'relaxed, informal, easy-going',
                'structure': 'simple greeting, casual content, relaxed closing'
            },
            'marketing': {
                'description': 'Write a persuasive marketing email that engages and motivates action. Include compelling content and clear call-to-action.',
                'tone': 'persuasive, engaging, motivational',
                'structure': 'attention-grabbing subject, compelling content, clear CTA'
            },
            'apology': {
                'description': 'Write a sincere apology email that acknowledges fault and seeks forgiveness. Be genuine and take responsibility.',
                'tone': 'sincere, apologetic, responsible',
                'structure': 'acknowledgment, sincere apology, corrective action, request for forgiveness'
            },
            'thank_you': {
                'description': 'Write a heartfelt thank you email expressing genuine gratitude. Be specific about what you\'re thankful for.',
                'tone': 'grateful, appreciative, warm',
                'structure': 'warm greeting, specific thanks, appreciation details, grateful closing'
            },
            'invitation': {
                'description': 'Write an inviting email that makes the recipient excited to participate. Include all necessary details.',
                'tone': 'inviting, exciting, informative',
                'structure': 'exciting opener, event details, benefits, clear RSVP'
            },
            'follow_up': {
                'description': 'Write a polite follow-up email that gently reminds without being pushy. Reference previous communication.',
                'tone': 'polite, gentle, persistent but respectful',
                'structure': 'reference to previous contact, gentle reminder, next steps'
            }
        }
        
        # Fallback content for when AI generation fails
        self.fallback_content = {
            'professional': {
                'subject': 'Professional Communication',
                'body': '''
                <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <p>Dear Recipient,</p>
                    <p>I hope this email finds you well. I am writing to communicate with you regarding an important matter.</p>
                    <p>Please let me know if you have any questions or if there is anything I can assist you with.</p>
                    <p>Thank you for your time and consideration.</p>
                    <p>Best regards,<br>Sender</p>
                </div>
                '''
            },
            'friendly': {
                'subject': 'Hello from a Friend!',
                'body': '''
                <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <p>Hey there!</p>
                    <p>Hope you're doing well! I wanted to reach out and connect with you.</p>
                    <p>Looking forward to hearing from you soon!</p>
                    <p>Take care,<br>Your Friend</p>
                </div>
                '''
            },
            'marketing': {
                'subject': 'Exciting Opportunity Just for You!',
                'body': '''
                <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <h2 style="color: #007bff;">Don't Miss Out!</h2>
                    <p>We have something special just for you.</p>
                    <p>This is an opportunity you won't want to miss.</p>
                    <p><strong>Take action today!</strong></p>
                    <p>Best regards,<br>The Team</p>
                </div>
                '''
            }
        }
    
    def get_template(self, email_type):
        """
        Get template guidelines for a specific email type.
        
        Args:
            email_type (str): Type of email
            
        Returns:
            str: Template description
        """
        template = self.templates.get(email_type, self.templates['professional'])
        return template['description']
    
    def get_template_details(self, email_type):
        """
        Get detailed template information including tone and structure.
        
        Args:
            email_type (str): Type of email
            
        Returns:
            dict: Complete template details
        """
        return self.templates.get(email_type, self.templates['professional'])
    
    def get_fallback_content(self, email_type, recipient_email=""):
        """
        Get fallback content when AI generation fails.
        
        Args:
            email_type (str): Type of email
            recipient_email (str): Recipient's email address
            
        Returns:
            dict: Fallback email content
        """
        # Use specific fallback if available, otherwise use professional
        fallback = self.fallback_content.get(email_type, self.fallback_content['professional'])
        
        # Personalize if recipient email is provided
        if recipient_email and '@' in recipient_email:
            name = recipient_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            fallback['body'] = fallback['body'].replace('Recipient', name)
        
        return fallback
    
    def get_all_types(self):
        """
        Get all available email types.
        
        Returns:
            list: List of email type names
        """
        return list(self.templates.keys())
    
    def get_type_description(self, email_type):
        """
        Get human-readable description of an email type.
        
        Args:
            email_type (str): Email type
            
        Returns:
            str: Human-readable description
        """
        descriptions = {
            'professional': 'Professional business communication',
            'comedy': 'Humorous and entertaining content',
            'friendly': 'Warm and casual conversation',
            'formal': 'Official and traditional format',
            'casual': 'Relaxed and informal tone',
            'marketing': 'Persuasive promotional content',
            'apology': 'Sincere apology and responsibility',
            'thank_you': 'Grateful appreciation message',
            'invitation': 'Event invitation and details',
            'follow_up': 'Gentle reminder and follow-up'
        }
        return descriptions.get(email_type, 'Email communication')
