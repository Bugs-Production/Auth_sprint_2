from authlib.integrations.httpx_client import AsyncOAuth2Client

google_client: AsyncOAuth2Client | None = None


async def get_google_client() -> AsyncOAuth2Client:
    return google_client
