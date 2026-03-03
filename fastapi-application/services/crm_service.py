import logging
import asyncio
import random
import httpx

from core.config import settings

logger = logging.getLogger("crm")


class CRMClient:
    def __init__(self):
        self.base_url = settings.crm.api_url.rstrip("/")
        self.api_key = settings.crm.api_key
        self.timeout = httpx.Timeout(settings.crm.timeout_seconds, connect=5)
        self.retries = settings.crm.retries

    async def get_application_status(self, crm_id: str) -> str:
        return random.choice(["in_progress", "completed", "rejected"])

    async def send_application(self, payload: dict):
        # заглушка
        if self.base_url == "stub":
            logger.info("crm stub used")
            return {"success": True, "crm_id": "stub-001", "message": "stub"}

        url = f"{settings.crm.api_url}/v1/applications"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for attempt in range(1, self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    logger.info(
                        "crm success (attempt %s): %s", attempt, response.status_code
                    )
                    return response.json()
            except Exception as e:
                logger.warning("crm attempt %s failed: %s", attempt, e)
                if attempt == self.retries:
                    raise
                await asyncio.sleep(2 ** (attempt - 1))


crm_client = CRMClient()
