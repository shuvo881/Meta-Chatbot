from fastapi import APIRouter, HTTPException, Query

from app.services.facebook import build_facebook_login_url, exchange_facebook_code_for_token, get_facebook_user

router = APIRouter(prefix="/auth")


@router.get("/facebook/login-url")
async def facebook_login_url() -> dict:
    return {"login_url": build_facebook_login_url()}


@router.get("/facebook/callback")
async def facebook_callback(code: str | None = Query(default=None), state: str | None = Query(default=None)) -> dict:
    if not code:
        raise HTTPException(status_code=400, detail="Missing Facebook authorization code")

    token_data = await exchange_facebook_code_for_token(code)
    user = await get_facebook_user(token_data["access_token"])

    return {
        "message": "Authentication successful",
        "user": user,
        "token": token_data,
        "state": state,
    }
