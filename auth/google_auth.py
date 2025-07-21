import os
import json
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleAuth:
    """
    Google OAuth authentication handler for Gmail API access.
    """
    
    def __init__(self, config):
        """
        Initialize GoogleAuth with configuration.
        
        Args:
            config (dict): Configuration dictionary containing OAuth settings
        """
        # Allow HTTP for development
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        self.client_config = {
            "web": {
                "client_id": config['GOOGLE_CLIENT_ID'],
                "client_secret": config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": config['GOOGLE_AUTH_URI'],
                "token_uri": config['GOOGLE_TOKEN_URI'],
                "redirect_uris": [config['GOOGLE_REDIRECT_URI']]
            }
        }
        self.scopes = [config['GOOGLE_SCOPE']]
        self.redirect_uri = config['GOOGLE_REDIRECT_URI']
    
    def get_authorization_url(self):
        """
        Get the Google OAuth authorization URL.
        
        Returns:
            str: Authorization URL for user to visit
        """
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            flow.redirect_uri = self.redirect_uri
            
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            return auth_url
        except Exception as e:
            print(f"Error getting authorization URL: {str(e)}")
            raise
    
    def handle_callback(self, authorization_response_url):
        """
        Handle the OAuth callback and exchange code for tokens.
        
        Args:
            authorization_response_url (str): Full callback URL with code
            
        Returns:
            dict: Credentials dictionary
        """
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(authorization_response=authorization_response_url)
            credentials = flow.credentials
            
            return {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
        except Exception as e:
            print(f"Error handling OAuth callback: {str(e)}")
            raise
    
    def refresh_credentials(self, credentials_dict):
        """
        Refresh expired credentials.
        
        Args:
            credentials_dict (dict): Existing credentials
            
        Returns:
            dict: Refreshed credentials
        """
        try:
            credentials = Credentials(
                token=credentials_dict.get('token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri=credentials_dict.get('token_uri'),
                client_id=credentials_dict.get('client_id'),
                client_secret=credentials_dict.get('client_secret'),
                scopes=credentials_dict.get('scopes')
            )
            
            request = Request()
            credentials.refresh(request)
            
            return {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
        except Exception as e:
            print(f"Error refreshing credentials: {str(e)}")
            raise
