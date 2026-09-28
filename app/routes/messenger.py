import logging

import httpx
from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks")


@router.get("/messenger")
async def messenger_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
) -> Response:
    if hub_mode == "subscribe" and hub_verify_token == settings.facebook_verify_token:
        return Response(content=hub_challenge or "", media_type="text/plain")

    raise HTTPException(status_code=403, detail="Invalid Messenger verification token")


@router.post("/messenger")
async def messenger_webhook_event(request: Request) -> dict:
    payload = await request.json()
    logger.info("Incoming Messenger payload: %s", payload)
    print("Incoming Messenger payload:", payload)  # Debug print statement
    if payload.get("object") != "page":
        return {"status": "ignored"}

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            if not sender_id:
                continue

            text = event.get("message", {}).get("text")
            if not text:
                logger.info("Message without text received from sender %s: %s", sender_id, event)
                continue

            if not settings.facebook_page_access_token:
                logger.warning("Facebook page access token is empty; cannot reply to sender %s", sender_id)
                continue

            reply_payload = {
                "recipient": {"id": sender_id},
                "message": {"text": f"Echo: {text}"},
            }

            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"https://graph.facebook.com/{settings.facebook_graph_version}/me/messages",
                    params={"access_token": settings.facebook_page_access_token},
                    json=reply_payload,
                )
                logger.info("Reply response status=%s body=%s", response.status_code, response.text)

    return {"status": "ok"}
