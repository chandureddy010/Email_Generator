import re
from urllib.parse import urlparse

class EmailValidator:
    """
    Email validation utilities with comprehensive validation rules.
    """
    
    # RFC 5322 compliant email regex (simplified but robust)
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
    )
    
    # Common disposable email domains to flag
    DISPOSABLE_DOMAINS = {
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'throwaway.email', 'temp-mail.org'
    }
    
    # Common invalid patterns
    INVALID_PATTERNS = [
        r'test@test\.com',
        r'example@example\.com',
        r'user@domain\.com',
        r'admin@admin\.com'
    ]
    
    @classmethod
    def is_valid(cls, email):
        """
        Validate email address format.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email is valid
        """
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip().lower()
        
        # Check basic format
        if not cls.EMAIL_PATTERN.match(email):
            return False
        
        # Additional validations
        return (
            cls._check_length(email) and
            cls._check_local_part(email) and
            cls._check_domain_part(email) and
            not cls._is_invalid_pattern(email)
        )
    
    @classmethod
    def is_disposable(cls, email):
        """
        Check if email is from a disposable email service.
        
        Args:
            email (str): Email address to check
            
        Returns:
            bool: True if email is from disposable service
        """
        if not email:
            return False
        
        domain = email.split('@')[-1].lower()
        return domain in cls.DISPOSABLE_DOMAINS
    
    @classmethod
    def validate_bulk_emails(cls, emails):
        """
        Validate a list of email addresses.
        
        Args:
            emails (list): List of email addresses to validate
            
        Returns:
            dict: Validation results with valid, invalid, and disposable emails
        """
        results = {
            'valid_emails': [],
            'invalid_emails': [],
            'disposable_emails': [],
            'duplicate_emails': [],
            'total_count': len(emails) if emails else 0,
            'valid_count': 0,
            'invalid_count': 0,
            'disposable_count': 0,
            'duplicate_count': 0
        }
        
        if not emails:
            return results
        
        seen_emails = set()
        
        for email in emails:
            email_lower = str(email).strip().lower()
            
            # Check for duplicates
            if email_lower in seen_emails:
                results['duplicate_emails'].append(email)
                results['duplicate_count'] += 1
                continue
            
            seen_emails.add(email_lower)
            
            # Validate email
            if cls.is_valid(email):
                if cls.is_disposable(email):
                    results['disposable_emails'].append(email)
                    results['disposable_count'] += 1
                else:
                    results['valid_emails'].append(email)
                    results['valid_count'] += 1
            else:
                results['invalid_emails'].append(email)
                results['invalid_count'] += 1
        
        return results
    
    @classmethod
    def _check_length(cls, email):
        """
        Check email length constraints.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if length is valid
        """
        if len(email) > 254:  # RFC 5321 limit
            return False
        
        local, domain = email.split('@')
        if len(local) > 64:  # RFC 5321 limit for local part
            return False
        
        return True
    
    @classmethod
    def _check_local_part(cls, email):
        """
        Validate the local part (before @) of email.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if local part is valid
        """
        local = email.split('@')[0]
        
        # Cannot start or end with dot
        if local.startswith('.') or local.endswith('.'):
            return False
        
        # Cannot have consecutive dots
        if '..' in local:
            return False
        
        return True
    
    @classmethod
    def _check_domain_part(cls, email):
        """
        Validate the domain part (after @) of email.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if domain part is valid
        """
        domain = email.split('@')[1]
        
        # Domain cannot start or end with dash
        if domain.startswith('-') or domain.endswith('-'):
            return False
        
        # Check if domain has at least one dot
        if '.' not in domain:
            return False
        
        # Split domain into parts
        parts = domain.split('.')
        
        # Each part should be valid
        for part in parts:
            if not part:  # Empty part
                return False
            if len(part) > 63:  # RFC limit for domain labels
                return False
            if part.startswith('-') or part.endswith('-'):
                return False
        
        # Last part (TLD) should be at least 2 characters
        if len(parts[-1]) < 2:
            return False
        
        return True
    
    @classmethod
    def _is_invalid_pattern(cls, email):
        """
        Check if email matches known invalid patterns.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if email matches invalid pattern
        """
        for pattern in cls.INVALID_PATTERNS:
            if re.match(pattern, email):
                return True
        return False
    
    @classmethod
    def suggest_correction(cls, email):
        """
        Suggest corrections for common email typos.
        
        Args:
            email (str): Email with potential typos
            
        Returns:
            str or None: Suggested correction or None
        """
        if not email:
            return None
        
        email = email.strip().lower()
        
        # Common domain corrections
        domain_corrections = {
            'gmail.co': 'gmail.com',
            'gmail.cm': 'gmail.com',
            'gmial.com': 'gmail.com',
            'yahoo.co': 'yahoo.com',
            'yahoo.cm': 'yahoo.com',
            'hotmail.co': 'hotmail.com',
            'hotmail.cm': 'hotmail.com',
            'outlook.co': 'outlook.com',
            'outlook.cm': 'outlook.com'
        }
        
        if '@' in email:
            local, domain = email.split('@', 1)
            
            if domain in domain_corrections:
                return f"{local}@{domain_corrections[domain]}"
        
        return None
    
    @classmethod
    def get_domain_info(cls, email):
        """
        Extract domain information from email.
        
        Args:
            email (str): Email address
            
        Returns:
            dict: Domain information
        """
        if not email or '@' not in email:
            return None
        
        domain = email.split('@')[1].lower()
        
        return {
            'domain': domain,
            'is_common': domain in [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'aol.com', 'icloud.com', 'protonmail.com'
            ],
            'is_disposable': cls.is_disposable(email),
            'tld': domain.split('.')[-1] if '.' in domain else '',
        }
