from fastapi import FastAPI, HTTPException, Request, Response

from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.messenger import router as messenger_router

app = FastAPI(title="Meta Chatbot Auth", version="1.0.0")


@app.get("/", response_model=None)
async def root(request: Request):
    params = request.query_params
    mode = params.get("hub.mode") or params.get("hub_mode")
    challenge = params.get("hub.challenge") or params.get("hub_challenge")
    verify_token = params.get("hub.verify_token") or params.get("hub_verify_token")

    if mode == "subscribe":
        if verify_token == settings.facebook_verify_token:
            return Response(content=challenge or "", media_type="text/plain")
        raise HTTPException(status_code=403, detail="Invalid Messenger verification token")

    return {"message": "Meta Chatbot API is running"}


app.include_router(auth_router)
app.include_router(messenger_router)
