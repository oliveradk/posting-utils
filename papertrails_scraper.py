"""
Paper Trails Scraper

Fetches reviews and ratings from a Paper Trails user profile.
"""

import re
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from bs4 import BeautifulSoup


@dataclass
class PaperReview:
    """Represents a paper review from Paper Trails."""
    paper_title: str
    authors: list[str]
    year: Optional[str]
    journal: Optional[str]
    rating: Optional[float]
    review_text: Optional[str]
    paper_url: Optional[str]  # Original paper URL (arxiv, doi, etc.)
    paper_id: Optional[str]


STORAGE_STATE_PATH = Path(__file__).parent / ".pt_browser_state.json"
BASE_URL = "https://www.papertrailshq.com"


def login_interactive():
    """Open browser for manual login, save session."""
    from playwright.sync_api import sync_playwright

    print("Opening browser for Paper Trails login...")
    print("Log in, then press Enter here when done.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(f"{BASE_URL}/sign-in")

        input("\nPress Enter after you've logged in...")

        context.storage_state(path=str(STORAGE_STATE_PATH))
        print(f"Session saved.")
        browser.close()


def get_profile_reviews(profile_id: str) -> list[PaperReview]:
    """Fetch reviews from a Paper Trails profile."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        if STORAGE_STATE_PATH.exists():
            context = browser.new_context(storage_state=str(STORAGE_STATE_PATH))
        else:
            context = browser.new_context()

        page = context.new_page()
        page.goto(f"{BASE_URL}/profile/{profile_id}", timeout=20000)
        page.wait_for_timeout(3000)

        html = page.content()
        browser.close()

    return parse_reviews_from_html(html)


def parse_reviews_from_html(html: str) -> list[PaperReview]:
    """Parse reviews from profile HTML."""
    soup = BeautifulSoup(html, "html.parser")
    reviews = []

    # Extract review texts from links to #reviews
    review_texts = {}
    for link in soup.find_all("a", href=re.compile(r"#reviews$")):
        href = link.get("href", "")
        paper_id_match = re.search(r"/papers/([^#]+)", href)
        if paper_id_match:
            paper_id = paper_id_match.group(1)
            review_text = link.get_text(strip=True)
            if review_text and len(review_text) > 10:
                review_texts[paper_id] = review_text

    # Extract external URLs (arxiv, doi, etc.)
    external_urls = {}
    for link in soup.find_all("a", href=re.compile(r"https?://(?:arxiv|doi\.org|www\.anthropic)")):
        href = link.get("href", "").rstrip("\\")
        # Find nearby paper ID
        parent = link.find_parent(class_=lambda c: c and "card" in str(c))
        if parent:
            paper_link = parent.find("a", href=re.compile(r"/papers/"))
            if paper_link:
                match = re.search(r"/papers/([^#\?/]+)", paper_link.get("href", ""))
                if match:
                    paper_id = match.group(1)
                    # Prefer non-PDF links
                    if paper_id not in external_urls or ".pdf" not in href:
                        external_urls[paper_id] = href

    # Also search raw HTML for external URLs near paper IDs
    for match in re.finditer(r'/papers/([^#\?/\"]+).*?(https?://(?:arxiv\.org/abs|doi\.org|www\.anthropic\.com)[^\s\"\\<>]+)', html, re.DOTALL):
        paper_id = match.group(1)
        url = match.group(2).rstrip("\\")
        if paper_id not in external_urls:
            external_urls[paper_id] = url

    # Parse paper cards
    cards = soup.find_all("div", class_=lambda c: c and "card-lift" in c)

    for card in cards:
        review = parse_card(card, review_texts, external_urls)
        if review:
            reviews.append(review)

    return reviews


def parse_card(card, review_texts: dict, external_urls: dict) -> Optional[PaperReview]:
    """Parse a paper card element."""
    text = card.get_text(separator=" ", strip=True)

    # Find title
    title = None
    title_elem = card.find(["h3", "h4"]) or card.find("a")
    if title_elem:
        title = title_elem.get_text(strip=True)

    if not title or len(title) < 5:
        return None

    # Find paper ID from link
    paper_id = None
    link = card.find("a", href=re.compile(r"/papers/"))
    if link:
        href = link.get("href", "")
        match = re.search(r"/papers/([^#\?/]+)", href)
        if match:
            paper_id = match.group(1)

    # Find authors
    authors = []
    author_elem = card.find(class_=lambda c: c and "text-sm" in str(c))
    if author_elem:
        author_text = author_elem.get_text(strip=True)
        if not any(x in author_text.lower() for x in ["abstract", "view", "save", "★"]):
            authors = [a.strip() for a in author_text.split(",") if a.strip()]

    # Find rating
    rating = None
    rating_match = re.search(r"★\s*(\d+\.?\d*)", text)
    if rating_match:
        rating = float(rating_match.group(1))

    # Find journal/source
    journal = None
    for elem in card.find_all(class_=lambda c: c and "text-xs" in str(c)):
        elem_text = elem.get_text(strip=True)
        if elem_text and "★" not in elem_text and len(elem_text) < 100:
            journal = elem_text
            break

    # Get external URL if available, otherwise use Paper Trails URL
    paper_url = external_urls.get(paper_id) if paper_id else None
    if not paper_url and link:
        href = link.get("href", "")
        if href.startswith("/"):
            paper_url = f"{BASE_URL}{href}"

    # Get review text
    review_text = review_texts.get(paper_id) if paper_id else None

    return PaperReview(
        paper_title=title,
        authors=authors[:5],
        year=None,
        journal=journal,
        rating=rating,
        review_text=review_text,
        paper_url=paper_url,
        paper_id=paper_id,
    )


def extract_profile_id(url: str) -> str:
    """Extract profile ID from URL."""
    match = re.search(r"/profile/([^/\?]+)", url)
    if match:
        return match.group(1)
    return url


class PaperTrailsScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def login_interactive(self):
        login_interactive()

    def get_profile_reviews(self, profile_id: str) -> list[PaperReview]:
        return get_profile_reviews(profile_id)
