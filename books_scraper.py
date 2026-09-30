"""Парсер цен с учебного сайта https://books.toscrape.com"""
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch_products(pages: int = 3) -> list[dict]:
    """Собирает книги с первых `pages` страниц (по 20 книг на странице)."""
    products = []
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (learning scraper)"

    for page_num in range(1, pages + 1):
        url = PAGE_URL.format(page_num)
        resp = session.get(url, timeout=15)
        if resp.status_code == 404:  # страницы закончились
            break
        resp.raise_for_status()
        resp.encoding = "utf-8"  # иначе знак £ превращается в «Â£»

        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select("article.product_pod"):
            link = card.select_one("h3 a")
            price_el = card.select_one("p.price_color")
            rating_el = card.select_one("p.star-rating")
            if not link or not price_el:
                continue

            price = float(re.sub(r"[^\d.]", "", price_el.get_text()))
            rating_word = next(
                (c for c in rating_el.get("class", []) if c in RATINGS), None
            ) if rating_el else None

            img = card.select_one("img")
            products.append({
                "name": link.get("title", link.get_text(strip=True)),
                "image": urljoin(url, img["src"]) if img else "",
                "price": price,
                "rating": RATINGS.get(rating_word, 0),
                "url": urljoin(url, link["href"]),
            })
    return products


if __name__ == "__main__":
    for item in fetch_products(pages=1)[:5]:
        print(item)
