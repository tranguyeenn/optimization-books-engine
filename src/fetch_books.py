import requests


def safe_get(url: str, params: dict | None = None) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def search_books(query: str, max_results: int = 10) -> list[dict]:
    url = "https://www.googleapis.com/books/v1/volumes"

    smart_query = f'intitle:"{query}"'

    params = {
        "q": smart_query,
        "maxResults": max_results,
        "printType": "books",
        "orderBy": "relevance",
        "langRestrict": "en",
    }

    data = safe_get(url, params=params)
    items = data.get("items", [])

    books = []

    for item in items:
        info = item.get("volumeInfo", {})

        title = info.get("title", "Unknown Title")
        authors = info.get("authors", [])
        pages = info.get("pageCount", None)
        categories = info.get("categories", [])
        language = info.get("language", "unknown")
        description = info.get("description", "")

        if language != "en":
            continue

        if pages is not None and pages < 50:
            continue

        if query.lower() not in title.lower():
            continue

        if not categories and not description:
            continue

        books.append(
            {
                "title": title,
                "authors": authors,
                "pages": pages,
                "categories": categories,
                "description": description,
            }
        )

    return books


def dedupe_books(books: list[dict]) -> list[dict]:
    best = {}

    for b in books:
        title = (b.get("title") or "").strip().lower()
        authors = b.get("authors") or []
        first_author = authors[0].strip().lower() if authors else ""

        key = (title, first_author)

        desc_len = len(b.get("description") or "")
        if key not in best or desc_len > len(best[key].get("description") or ""):
            best[key] = b

    return list(best.values())


def normalize_genres(categories: list[str]) -> list[str]:
    if not categories:
        return []
    return [c.strip().lower() for c in categories if isinstance(c, str) and c.strip()]


def filter_books_by_genre(books: list[dict], genre: str) -> list[dict]:
    genre = genre.strip().lower()
    if not genre:
        return books

    filtered = []
    for b in books:
        genres = normalize_genres(b.get("categories", []))
        if any(genre in g for g in genres):
            filtered.append(b)
    return filtered


def pretty_print_books(books: list[dict]):
    if not books:
        print("\nNo books found.\n")
        return

    print("\nResults:\n")

    for i, b in enumerate(books, start=1):
        title = b.get("title", "Unknown Title")

        authors = b.get("authors", [])
        authors_str = ", ".join(authors) if authors else "Unknown Author"

        pages = b.get("pages")
        pages_str = pages if pages is not None else "N/A"

        categories = b.get("categories", [])
        categories_str = ", ".join(categories) if categories else "N/A"

        print(f"{i}. {title}")
        print(f"   Author(s): {authors_str}")
        print(f"   Pages: {pages_str}")
        print(f"   Genre(s): {categories_str}")
        print("-" * 60)


def main():
    print("\n📚 TBR Chooser (Genre-Based)\n")

    while True:
        query = input('Search book title (or type "q" to quit): ').strip()

        if query.lower() in ["q", "quit", "exit"]:
            print("\nBye.\n")
            break

        max_results_str = input("How many results? (default: 10): ").strip()
        max_results = 10

        if max_results_str:
            try:
                max_results = int(max_results_str)
                if max_results < 1 or max_results > 40:
                    max_results = 10
            except ValueError:
                max_results = 10

        books = search_books(query=query, max_results=max_results)
        books = dedupe_books(books)

        print(f"\nBooks found: {len(books)}")

        genre = input("Optional: filter by genre (press Enter to skip): ").strip().lower()
        if genre:
            books = filter_books_by_genre(books, genre)
            print(f"Books after genre filter ({genre}): {len(books)}")

        pretty_print_books(books)


if __name__ == "__main__":
    main()
