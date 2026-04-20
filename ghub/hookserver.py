import hashlib
import hmac
import json

from fastapi import APIRouter, Request, Response

import config
from database.store import DataStore
from ghub.payloads import dispatch
from helpers.logger import LOGGER

router = APIRouter()


def _verify_sig(secret: str, payload: bytes, sig_header: str) -> bool:
    if not sig_header or not sig_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header)


@router.post("/webhook/{token}")
async def github_webhook(token: str, request: Request):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")

    if not _verify_sig(config.HOOK_SECRET, body, sig):
        LOGGER.warning("Webhook signature mismatch — rejected.")
        return Response(content="Forbidden", status_code=403)

    try:
        from crypto.vault import unseal
        chat_id = int(unseal(token))
    except Exception as e:
        LOGGER.error(f"Failed to decode webhook token: {e}")
        return Response(content="Bad Token", status_code=400)

    event = request.headers.get("X-GitHub-Event", "ping")
    payload = json.loads(body)

    LOGGER.info(f"Webhook received: event={event} chat={chat_id}")

    try:
        await dispatch(chat_id, event, payload)
    except Exception as e:
        LOGGER.exception(f"Webhook dispatch error: {e}")

    return Response(content="OK", status_code=200)


@router.get("/auth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state", "")

    if not code:
        return Response(content="Missing code", status_code=400)

    try:
        handle_oauth = request.app.state.handle_oauth
        await handle_oauth(code, state)
    except Exception as e:
        LOGGER.exception(f"OAuth callback error: {e}")
        return Response(content="OAuth Error", status_code=500)

    return Response(
        content="<html><body><h2>GitHub connected! Return to Telegram.</h2></body></html>",
        media_type="text/html",
    )
