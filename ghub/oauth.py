import aiohttp

import config
from helpers.logger import LOGGER


def build_auth_url(state: str = "connect") -> str:
    params = (
        f"client_id={config.GH_CLIENT_ID}"
        f"&scope=repo,admin:repo_hook,read:user"
        f"&state={state}"
    )
    return f"https://github.com/login/oauth/authorize?{params}"


async def exchange_code(code: str) -> str:
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": config.GH_CLIENT_ID,
        "client_secret": config.GH_CLIENT_SECRET,
        "code": code,
    }
    async with aiohttp.ClientSession() as sess:
        async with sess.post(url, json=payload, headers=headers) as resp:
            data = await resp.json(content_type=None)
            LOGGER.debug(f"OAuth exchange response: {data}")
            token = data.get("access_token")
            if not token:
                raise ValueError(f"OAuth exchange failed: {data}")
            return token
