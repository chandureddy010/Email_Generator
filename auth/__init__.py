"""
Authentication module for Google OAuth and Gmail integration.
"""
from .google_auth import GoogleAuth
from .gmail_service import GmailService

__all__ = ['GoogleAuth', 'GmailService']
