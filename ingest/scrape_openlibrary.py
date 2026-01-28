import requests
import json
from uuid import uuid4
from pathlib import Path
from time import sleep

BASE_URL = "https://openlibrary.org/search.json"
OUTPUT_DIR = Path("data/raw/books")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def search_openlibrary(query: str, limit: int = 25) -> list[dict]:
    params = {
        "q": query,
        "limit": limit
    }
    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("docs", [])

def normalize_search_result(raw: dict) -> dict:
    return {
        "book_id": str(uuid4()),
        "title": raw.get("title"),
        "author": (raw.get("author_name") or [None])[0],
        "author_key": (raw.get("author_key") or [None])[0],
        "work_key": raw.get("key"),  
        "first_publish_year": raw.get("first_publish_year"),
        "edition_count": raw.get("edition_count"),
        "isbn": (raw.get("isbn") or [None])[0],
        "raw_source": "openlibrary_search"
    }


def save_book(book: dict) -> None:
    path = OUTPUT_DIR / f"{book['book_id']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=2, ensure_ascii=False)


def scrape_and_store(query: str, limit: int = 25) -> None:
    print(f"Open Library search: '{query}'")
    results = search_openlibrary(query, limit)
    print(f"Found {len(results)} works")
    for i, raw in enumerate(results):
        book = normalize_search_result(raw)
        save_book(book)
        print(f"   [{i+1}/{len(results)}] {book['title']}")
        sleep(0.15)  
    print("Open Library scraping complete.")


if __name__ == "__main__":
    scrape_and_store(
        query="classic literature",
        limit=25
    )