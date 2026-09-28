import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "Meta Chatbot"
    facebook_app_id: str = os.getenv("FACEBOOK_APP_ID", "")
    facebook_app_secret: str = os.getenv("FACEBOOK_APP_SECRET", "")
    facebook_redirect_uri: str = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/auth/facebook/callback")
    facebook_graph_version: str = os.getenv("FACEBOOK_GRAPH_VERSION", "v26.0")
    facebook_login_scope: str = os.getenv("FACEBOOK_LOGIN_SCOPE", "pages_messaging")
    facebook_verify_token: str = os.getenv("FACEBOOK_VERIFY_TOKEN", "demo-token")
    facebook_page_access_token: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")


settings = Settings()
