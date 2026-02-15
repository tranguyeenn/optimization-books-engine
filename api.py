from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import numpy as np

from preprocess.normalize import normalize_rating, compute_recency
from ranking.score import score_read_books, score_tbr_books, recommend_one


app = FastAPI(title="LibroRank API")

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "books.csv"


def load_data():
    df = pd.read_csv(PROCESSED_PATH)
    df["Read Status"] = df["Read Status"].astype(str).str.strip().str.lower()
    df["Last Date Read"] = pd.to_datetime(df["Last Date Read"], errors="coerce")
    return df


def save_data(df):
    df.to_csv(PROCESSED_PATH, index=False)


def clean_for_json(df):
    return df.replace({np.nan: None})


def parse_date_or_today(date_str):
    try:
        return pd.to_datetime(date_str) if date_str else pd.Timestamp.today().normalize()
    except Exception:
        return pd.Timestamp.today().normalize()


class AddBook(BaseModel):
    title: str
    author: str
    total_pages: int | None = None


class UpdateProgress(BaseModel):
    title: str
    pages_read: int
    total_pages: int | None = None


class FinishBook(BaseModel):
    title: str
    rating: float
    date: str | None = None


class DNFBook(BaseModel):
    title: str
    date: str | None = None


@app.get("/books")
def get_books():
    df = load_data()
    df = clean_for_json(df)
    return df.to_dict(orient="records")


@app.post("/books")
def add_book(book: AddBook):
    df = load_data()

    new_row = {
        "Title": book.title,
        "Authors": book.author,
        "ISBN/UID": str(pd.Timestamp.now().timestamp()),
        "Read Status": "to-read",
        "Star Rating": np.nan,
        "Last Date Read": None,
        "Progress (%)": 0,
        "Pages Read": 0,
        "Total Pages": book.total_pages
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)

    return {"message": "Book added"}


@app.patch("/books/progress")
def update_progress(update: UpdateProgress):
    df = load_data()

    if update.title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")

    if update.total_pages:
        df.loc[df["Title"] == update.title, "Total Pages"] = update.total_pages

    total_pages = df.loc[df["Title"] == update.title, "Total Pages"].values[0]

    if not total_pages:
        raise HTTPException(status_code=400, detail="Total pages not set")

    pages_read = min(update.pages_read, total_pages)
    progress = round((pages_read / total_pages) * 100, 2)

    df.loc[df["Title"] == update.title, "Pages Read"] = pages_read
    df.loc[df["Title"] == update.title, "Progress (%)"] = progress

    save_data(df)

    return {"progress": progress}


@app.patch("/books/finish")
def finish_book(data: FinishBook):
    df = load_data()

    if data.title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")

    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1-5")

    date = parse_date_or_today(data.date)

    df.loc[df["Title"] == data.title, "Read Status"] = "read"
    df.loc[df["Title"] == data.title, "Star Rating"] = data.rating
    df.loc[df["Title"] == data.title, "Progress (%)"] = 100
    df.loc[df["Title"] == data.title, "Last Date Read"] = date

    save_data(df)

    return {"message": "Book marked as finished"}


@app.patch("/books/dnf")
def dnf_book(data: DNFBook):
    df = load_data()

    if data.title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")

    date = parse_date_or_today(data.date)

    df.loc[df["Title"] == data.title, "Read Status"] = "dnf"
    df.loc[df["Title"] == data.title, "Star Rating"] = 1
    df.loc[df["Title"] == data.title, "Progress (%)"] = 0
    df.loc[df["Title"] == data.title, "Last Date Read"] = date

    save_data(df)

    return {"message": "Book marked as DNF"}


@app.get("/recommend")
def recommend():
    df = load_data()

    df = normalize_rating(df)
    df = compute_recency(df)

    tbr_ranked = score_tbr_books(df)
    recommendation = recommend_one(tbr_ranked)

    recommendation = clean_for_json(recommendation)

    return recommendation.to_dict(orient="records")