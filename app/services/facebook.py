import secrets
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from app.config import settings

SUPPORTED_FACEBOOK_LOGIN_SCOPES = {
    "public_profile",
    "pages_messaging",
    "email",
    "user_friends",
    "user_age_range",
    "user_gender",
    "user_link",
    "user_hometown",
    "user_location",
    "user_likes",
    "user_photos",
    "user_posts",
    "user_videos",
}


def normalize_facebook_login_scope(scope: str) -> str:
    if not scope:
        return "pages_messaging"

    permissions = [item.strip() for item in scope.split(",") if item.strip()]
    valid_permissions = [permission for permission in permissions if permission in SUPPORTED_FACEBOOK_LOGIN_SCOPES]

    if not valid_permissions:
        return "pages_messaging"

    return ",".join(valid_permissions)


def build_facebook_login_url() -> str:
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": settings.facebook_app_id,
        "redirect_uri": settings.facebook_redirect_uri,
        "scope": normalize_facebook_login_scope(settings.facebook_login_scope),
        "response_type": "code",
        "state": state,
    }
    return f"https://www.facebook.com/{settings.facebook_graph_version}/dialog/oauth?{urlencode(params)}"


async def exchange_facebook_code_for_token(code: str) -> dict:
    if not settings.facebook_app_id or not settings.facebook_app_secret:
        raise HTTPException(
            status_code=500,
            detail="Facebook app credentials are not configured. Set FACEBOOK_APP_ID and FACEBOOK_APP_SECRET.",
        )

    payload = {
        "client_id": settings.facebook_app_id,
        "client_secret": settings.facebook_app_secret,
        "redirect_uri": settings.facebook_redirect_uri,
        "code": code,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"https://graph.facebook.com/{settings.facebook_graph_version}/oauth/access_token",
            params=payload,
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Failed to exchange Facebook code for access token")

    data = response.json()
    if "access_token" not in data:
        raise HTTPException(status_code=502, detail="Facebook did not return an access token")

    return data


async def get_facebook_user(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"https://graph.facebook.com/{settings.facebook_graph_version}/me",
            params={
                "fields": "id,name,email,picture",
                "access_token": access_token,
            },
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Unable to fetch Facebook user profile")

    data = response.json()
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "email": data.get("email"),
        "picture": data.get("picture", {}).get("data", {}).get("url"),
    }
