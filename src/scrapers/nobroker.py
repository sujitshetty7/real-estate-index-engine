import re
import uuid
from typing import List
from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper
from src.models import RawListing

class NoBrokerScraper(BaseScraper):
    def __init__(self, locality: str = "Mumbai"):
        super().__init__()
        self.source_name = "nobroker"
        self.locality = locality

    def parse(self, html: str, source_url: str) -> List[RawListing]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        cards = soup.select('article')

        for card in cards:
            try:
                title_el = card.select_one('h2')
                title = title_el.text.strip() if title_el else ""

                if not title:
                    continue

                # In NoBroker, pricing and area are usually in .font-semi-bold.heading-6
                # Index 1: Price (e.g., â¹1.69 Crores)
                # Index 2: EMI/Month (e.g., â¹96,861/Month)
                # Index 3: Area (e.g., 838 sqft)
                elements = card.select('.font-semi-bold.heading-6')

                price = ""
                area = ""

                if len(elements) >= 3:
                    # On some loads NoBroker structure has 4 elements, some 3
                    # Usually price is at index 1 and area is at the last index
                    price_text = elements[1].text.strip()
                    area_text = elements[-1].text.strip()

                    # Clean the price text (remove unusual characters)
                    price = re.sub(r'[^\d\.\sA-Za-z]', '', price_text).strip()
                    area = area_text
                else:
                    # Fallback logic if needed
                    area_el = card.select_one('#minRent')
                    if area_el:
                        area = area_el.text.strip()

                    price_el = card.select_one('#roomType')
                    if price_el:
                        price = re.sub(r'[^\d\.\sA-Za-z]', '', price_el.text.strip()).strip()

                if not price or not area:
                    continue

                listings.append(
                    RawListing(
                        id=str(uuid.uuid4()),
                        source=self.source_name,
                        raw_title=title,
                        raw_area_text=area,
                        raw_price_text=price,
                        locality=self.locality,
                        image_phash=None,
                        source_url=source_url
                    )
                )
            except Exception as e:
                print(f"Error parsing NoBroker item: {e}")
                continue

        return listings
