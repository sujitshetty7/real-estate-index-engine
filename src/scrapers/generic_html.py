from src.scrapers.base import BaseScraper
from src.models import RawListing
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import uuid

class GenericHTMLScraper(BaseScraper):
    def __init__(self, source_name: str, selectors: Dict[str, str], locality: str):
        super().__init__()
        self.source_name = source_name
        self.selectors = selectors
        self.locality = locality

    def parse(self, html: str, source_url: str) -> List[RawListing]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        # Expecting a list of item containers
        container_selector = self.selectors.get("container")
        items = soup.select(container_selector)

        for item in items:
            try:
                title_el = item.select_one(self.selectors.get("title"))
                area_el = item.select_one(self.selectors.get("area"))
                price_el = item.select_one(self.selectors.get("price"))

                title = title_el.get_text(strip=True) if title_el else ""
                area = area_el.get_text(strip=True) if area_el else ""
                price = price_el.get_text(strip=True) if price_el else ""

                if not title or not price:
                    continue

                listings.append(
                    RawListing(
                        id=str(uuid.uuid4()),
                        source=self.source_name,
                        raw_title=title,
                        raw_area_text=area,
                        raw_price_text=price,
                        locality=self.locality,
                        image_phash=None, # Could extract image and hash it if needed
                        source_url=source_url
                    )
                )
            except Exception as e:
                print(f"Error parsing item: {e}")
                continue

        return listings
