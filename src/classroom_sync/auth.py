import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# logging configuration
logger = logging.getLogger(__name__)

# defining scopes for classroom and drive access
SCOPES = [
    "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
    "https://www.googleapis.com/auth/classroom.rosters.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

class GoogleAuthManager:
    """handles oauth2 authentication flow and token persistence."""
    
    def __init__(self, credentials_path: Path, token_path: Path):
        self.credentials_path = credentials_path
        self.token_path = token_path

    def get_credentials(self) -> Credentials:
        """loads or initiates the oauth2 flow to return valid credentials."""
        creds = None
        
        # loading existing token if it already exists
        if self.token_path.exists():
            logger.info(f"loading token from {self.token_path}")
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
        # refreshing or authenticating if necessary
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("refreshing expired credentials")
                creds.refresh(Request())
            else:
                logger.info("starting new authentication flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # saving the token for future use
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())
                logger.info(f"token saved to {self.token_path}")
                
        return creds