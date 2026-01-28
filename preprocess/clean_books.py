import json
from pathlib import Path
from typing import Optional

from ingest.openlibrary_work import (
    fetch_work,
    extract_description_and_genres
)

RAW_BOOKS_DIR = Path("data/raw/books")
OUTPUT_FILE = Path("data/processed/books.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

GENRE_KEYWORDS = {
    "historical": [
        "historical",
        "history",
        "medieval",
        "crusades",
        "plantagenets",
    ],
    "romance": [
        "romance",
        "love",
        "love stories",
        "courtship",
    ],
    "adventure": [
        "adventure",
        "knights",
        "chivalry",
        "quests",
        "journeys",
    ],
    "fantasy": [
        "fantasy",
        "magic",
        "myth",
        "legend",
    ],
    "philosophical": [
        "philosophy",
        "psychological",
        "existential",
        "moral",
    ],
    "children": [
        "juvenile fiction",
        "children's fiction",
        "children",
        "readers",
    ],
    "classic": [
        "classic",
        "classics",
        "english literature",
        "british literature",
        "great britain, fiction",
    ],
}


def normalize_genres(subjects: list[str]) -> list[str]:
    if not subjects:
        return []

    subjects_lower = [s.lower() for s in subjects]
    genres = set()

    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            if any(kw in subject for subject in subjects_lower):
                genres.add(genre)
                break

    return sorted(genres)

def load_openlibrary_books() -> list[dict]:
    books = []
    for file in RAW_BOOKS_DIR.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            books.append(json.load(f))
    return books

def clean_book(open_book: dict) -> dict:
    work_key = open_book.get("work_key")
    work_data = fetch_work(work_key) if work_key else None

    description, raw_subjects = extract_description_and_genres(work_data)
    genres = normalize_genres(raw_subjects)

    return {
        "book_id": open_book["book_id"],
        "title": open_book["title"],
        "author": open_book["author"],
        "author_key": open_book["author_key"],
        "work_key": work_key,
        "year": open_book.get("first_publish_year"),
        "edition_count": open_book.get("edition_count"),
        "description": description,
        "genres": genres,
        "raw_subjects": raw_subjects,

        "sources": {
            "openlibrary": True
        }
    }


def process_books(limit: Optional[int] = None) -> list[dict]:
    raw_books = load_openlibrary_books()
    cleaned = []

    total = len(raw_books)

    for i, book in enumerate(raw_books):
        if limit and i >= limit:
            break

        print(f"\n📘 Processing {i+1}/{total}")
        print(f"   {book['title']} — {book['author']}")

        clean = clean_book(book)
        cleaned.append(clean)

    return cleaned

def save_books(books: list[dict]) -> None:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    books = process_books(limit=None)
    save_books(books)

    print(f"\n✅ Saved {len(books)} books to {OUTPUT_FILE}")
