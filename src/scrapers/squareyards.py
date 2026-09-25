import uuid
from typing import List
from bs4 import BeautifulSoup
import re

from src.scrapers.base import BaseScraper
from src.models import RawListing

class SquareYardsScraper(BaseScraper):
    def __init__(self, locality: str = "Mumbai"):
        super().__init__()
        self.source_name = "squareyards"
        self.locality = locality

    def parse(self, html: str, source_url: str) -> List[RawListing]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        # Find unit-cards which correspond to individual properties inside a project
        unit_cards = soup.select('.unit-card')

        for card in unit_cards:
            try:
                # Find parent project banner to get the main title (e.g., Kalpataru Vian)
                # But it's easier to just use the unit title inside the card
                title_el = card.select_one('.unit-title')
                title = title_el.text.strip() if title_el else ""

                if not title:
                    continue

                price_el = card.select_one('.unit-price')
                price = price_el.text.strip() if price_el else ""

                # Extract area from the div
                area_value_el = card.select_one('.avail-area')
                area_value = area_value_el.get('data-area') if area_value_el else ""

                area_label_el = card.select_one('.unit-label')
                area_label = area_label_el.text.strip() if area_label_el else "Sq. Ft"

                area = f"{area_value} {area_label}" if area_value else ""

                # Try to get project title if we can traverse up
                parent_project = card.find_parent(class_=re.compile('projectBanner|boxSet|project'))
                if parent_project:
                    project_title_el = parent_project.select_one('.project-name, h2, h3, strong')
                    if project_title_el:
                        title = project_title_el.text.strip() + " - " + title

                if not price or not area_value:
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
                print(f"Error parsing SquareYards item: {e}")
                continue

        return listings
