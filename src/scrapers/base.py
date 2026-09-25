from abc import ABC, abstractmethod
from typing import List
from src.models import RawListing
import httpx
import asyncio
import random

class BaseScraper(ABC):
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
        ]

    async def fetch_page(self, url: str) -> str:
        # Realistic delay to prevent rate-limiting
        await asyncio.sleep(random.uniform(1.0, 3.0))

        headers = {
            "User-Agent": random.choice(self.user_agents)
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

    @abstractmethod
    def parse(self, html: str, source_url: str) -> List[RawListing]:
        pass
