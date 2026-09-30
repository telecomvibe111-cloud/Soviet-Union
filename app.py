import threading
import time
from flask import Flask, redirect, render_template, request, url_for

import books_scraper
import laptops_scraper

app = Flask(__name__)

CACHE_TTL = 10 * 60  # секунд

# Чтобы добавить ещё один сайт: напишите парсер с функцией fetch_products()
# и добавьте запись сюда.
SOURCES = {
    "books": {
        "label": "Книги",
        "title": "Цены на книги",
        "site": "books.toscrape.com",
        "currency": "£",
        "shape": "portrait",
        "fetch": books_scraper.fetch_products,
    },
    "laptops": {
        "label": "Ноутбуки",
        "title": "Цены на ноутбуки",
        "site": "webscraper.io (тестовый магазин)",
        "currency": "$",
        "shape": "square",
        "fetch": laptops_scraper.fetch_products,
    },
}
DEFAULT_SOURCE = "books"

_lock = threading.Lock()
_cache = {}  # ключ источника -> {"products", "updated", "error", "ts"}


def get_data(key: str, force: bool = False) -> dict:
    with _lock:
        entry = _cache.setdefault(
            key, {"products": [], "updated": None, "error": None, "ts": 0}
        )
        fresh = time.time() - entry["ts"] < CACHE_TTL
        if force or not (fresh and entry["products"]):
            try:
                entry["products"] = SOURCES[key]["fetch"]()
                entry["error"] = None
                entry["updated"] = time.strftime("%d.%m.%Y %H:%M:%S")
            except Exception as e:  # noqa: BLE001
                entry["error"] = f"Не удалось получить данные: {e}"
            entry["ts"] = time.time()
        return dict(entry)


def current_source() -> str:
    key = request.args.get("source", DEFAULT_SOURCE)
    return key if key in SOURCES else DEFAULT_SOURCE


@app.route("/")
def index():
    key = current_source()
    src = SOURCES[key]
    return render_template(
        "index.html",
        source=key,
        sources=[{"key": k, "label": v["label"]} for k, v in SOURCES.items()],
        title=src["title"],
        site=src["site"],
        currency=src["currency"],
        shape=src["shape"],
        **get_data(key),
    )


@app.route("/refresh")
def refresh():
    key = current_source()
    get_data(key, force=True)
    return redirect(url_for("index", source=key))


if __name__ == "__main__":
    app.run(debug=False, port=5000)
