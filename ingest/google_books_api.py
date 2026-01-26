import requests
import json
import re
from pathlib import Path
from time import sleep
from difflib import SequenceMatcher

BASE_URL = "https://www.googleapis.com/books/v1/volumes"
OUTPUT_DIR = Path("data/raw/google_books")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_RATINGS = 50
MIN_ACCEPT_SCORE = 0.55

CLASSIC_PUBLISHERS = {
    "penguin",
    "oxford university press",
    "everyman's library",
    "modern library",
    "vintage",
}

def _clean(s: str | None) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, _clean(a), _clean(b)).ratio()


def _extract_year(published_date: str | None) -> int | None:
    if not published_date:
        return None
    m = re.match(r"^(\d{4})", published_date)
    return int(m.group(1)) if m else None


def is_classic_candidate(info: dict) -> bool:
    year = _extract_year(info.get("publishedDate"))
    publisher = _clean(info.get("publisher"))

    if year and year <= 1950:
        return True

    if publisher in CLASSIC_PUBLISHERS:
        return True

    return False

def search_google_books_candidates(
    title: str,
    author: str | None = None,
    max_results: int = 10
) -> list[dict]:

    query = f'intitle:{title}'
    if author:
        query += f'+inauthor:{author}'

    params = {
        "q": query,
        "maxResults": max_results,
        "printType": "books"
    }

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json().get("items", [])

def score_candidate(item: dict, target_title: str, target_author: str | None) -> float:
    info = item.get("volumeInfo", {})

    title = info.get("title", "")
    authors = info.get("authors", []) or []
    rating = info.get("averageRating")
    rating_count = info.get("ratingsCount", 0)

    classic = is_classic_candidate(info)

    if not classic:
        if rating is None or rating_count < MIN_RATINGS:
            return -1.0

    title_score = _ratio(title, target_title)

    author_score = 0.0
    if target_author and authors:
        author_score = max(_ratio(a, target_author) for a in authors)

    popularity_bonus = 0.0
    if rating_count:
        popularity_bonus = min(1.0, (rating_count ** 0.5) / 100.0)

    classic_bonus = 0.15 if classic else 0.0

    score = (
        0.45 * title_score +
        0.35 * author_score +
        0.10 * ((rating or 0.0) / 5.0) +
        0.10 * popularity_bonus +
        classic_bonus
    )

    return score


def pick_best_candidate(
    items: list[dict],
    title: str,
    author: str | None
) -> dict | None:

    scored = []
    for item in items:
        s = score_candidate(item, title, author)
        if s >= 0:
            scored.append((s, item))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_item = scored[0]

    if best_score < MIN_ACCEPT_SCORE:
        return None

    return best_item

def normalize_google_book(item: dict) -> dict:
    info = item.get("volumeInfo", {})

    return {
        "google_id": item.get("id"),
        "title": info.get("title"),
        "authors": info.get("authors", []),
        "published_year": _extract_year(info.get("publishedDate")),
        "rating": info.get("averageRating"),
        "rating_count": info.get("ratingsCount"),
        "categories": info.get("categories", []),
        "description": info.get("description"),
        "page_count": info.get("pageCount"),
        "language": info.get("language"),
        "publisher": info.get("publisher"),
        "preview_link": info.get("previewLink"),
        "raw_source": "google_books"
    }

def save_json(path: Path, payload: dict | list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def enrich_book(
    title: str,
    author: str | None = None,
    save_candidates: bool = True
) -> dict | None:

    print(f"🔍 Google Books lookup: {title} — {author or 'UNKNOWN AUTHOR'}")

    items = search_google_books_candidates(title, author)

    if save_candidates:
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", _clean(f"{title}_{author or ''}"))[:80]
        save_json(OUTPUT_DIR / f"_candidates_{safe}.json", items)

    best = pick_best_candidate(items, title, author)

    if not best:
        print("⚠️  No acceptable Google Books match found.")
        return None

    book = normalize_google_book(best)
    save_json(OUTPUT_DIR / f"{book['google_id']}.json", book)

    print(
        f"✅ Picked: {book['title']} | "
        f"publisher={book['publisher']} | "
        f"rating={book['rating']} | "
        f"count={book['rating_count']} | "
        f"year={book['published_year']}"
    )

    sleep(0.2)
    return book

if __name__ == "__main__":
    enrich_book(
        title="Crime and Punishment",
        author="Fyodor Dostoyevsky"
    )
