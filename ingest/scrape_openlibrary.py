import requests
import json
from uuid import uuid4
from pathlib import Path
from time import sleep

BASE_URL = "https://openlibrary.org/search.json"
OUTPUT_DIR = Path("data/raw/books")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def search_books(query: str, limit: int=20) -> list[dict]:
    params = {
        "q": query,
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()["docs"]

def normalize_raw_book(raw: dict) -> dict:
    return {
        "book_id": str(uuid4()),
        "title": raw.get("title"),
        "author": raw.get("author_name", [None])[0],
        "author_key": raw.get("author_key", [None])[0],
        "year": raw.get("first_publish_year"),
        "isbn": raw.get("isbn", [None])[0],
        "subjects": raw.get("subject", []),
        "edition_count": raw.get("edition_count"),
        "raw_source": "openlibrary"
    }

def save_book(book: dict) -> None:
    file_path = OUTPUT_DIR/f"{book['book_id']}.json"

    with open(file_path, "w", encoding="utf-8") as f:
            json.dump(book, f, indent=2, ensure_ascii=False)


def scrape_and_store(query: str, limit: int = 20) -> None:
    print(f"🔎 Searching Open Library for: '{query}'")
    raw_books = search_books(query, limit)

    print(f"📚 Found {len(raw_books)} books. Saving raw data...")
    for raw in raw_books:
        book = normalize_raw_book(raw)
        save_book(book)
        sleep(0.2)  

    print("Done.")


if __name__ == "__main__":
    scrape_and_store(query="classic literature", limit=25)