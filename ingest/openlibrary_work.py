import requests

BASE_URL = "https://openlibrary.org"

def fetch_work(work_key: str) -> dict | None:
    if not work_key:
        return None

    url = f"{BASE_URL}{work_key}.json"
    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        return None

    return r.json()


def extract_description_and_genres(work_data: dict) -> tuple[str | None, list[str]]:
    if not work_data:
        return None, []

    description = work_data.get("description")

    if isinstance(description, dict):
        description = description.get("value")
    elif not isinstance(description, str):
        description = None

    subjects = work_data.get("subjects", [])
    if not isinstance(subjects, list):
        subjects = []

    return description, subjects