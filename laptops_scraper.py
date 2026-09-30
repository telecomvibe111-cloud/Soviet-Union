"""Парсер цен с тестового магазина https://webscraper.io/test-sites/e-commerce/static"""
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://webscraper.io"
PAGE_URL = BASE + "/test-sites/e-commerce/static/computers/laptops?page={}"


def fetch_products(pages: int = 5) -> list[dict]:
    """Собирает ноутбуки с первых `pages` страниц (по ~6 штук на странице)."""
    products = []
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (learning scraper)"

    for page_num in range(1, pages + 1):
        url = PAGE_URL.format(page_num)
        resp = session.get(url, timeout=15)
        if resp.status_code == 404:
            break
        resp.raise_for_status()
        resp.encoding = "utf-8"

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.thumbnail")
        if not cards:  # страницы закончились
            break

        for card in cards:
            link = card.select_one("a.title")
            price_el = card.select_one(".price")
            if not link or not price_el:
                continue

            digits = re.sub(r"[^\d.]", "", price_el.get_text())
            if not digits:
                continue
            rating_el = card.select_one("[data-rating]")
            img = card.select_one("img")

            products.append({
                "name": link.get("title") or link.get_text(strip=True),
                "price": float(digits),
                "rating": int(rating_el["data-rating"]) if rating_el else 0,
                "image": urljoin(url, img["src"]) if img and img.get("src") else "",
                "url": urljoin(url, link["href"]),
            })
    return products


if __name__ == "__main__":
    for item in fetch_products(pages=1)[:5]:
        print(item)
