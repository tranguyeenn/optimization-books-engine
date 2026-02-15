from pathlib import Path
import pandas as pd

from ingest.load_csv import load_csv
from preprocess.clean_books import clean_books
from preprocess.normalize import normalize_rating, compute_recency
from ranking.score import score_read_books, score_tbr_books, recommend_one


RAW_PATH = Path("data/raw/storyGraph_export.csv")
PROCESSED_PATH = Path("data/processed/books.csv")

if PROCESSED_PATH.exists():
    df = pd.read_csv(PROCESSED_PATH)
    df["Last Date Read"] = pd.to_datetime(df["Last Date Read"], errors="coerce")
else:
    df = load_csv(RAW_PATH)
    df = clean_books(df)
    df.to_csv(PROCESSED_PATH, index=False)

required_columns = [
    "Progress (%)",
    "Pages Read",
    "Total Pages",
    "Star Rating"
]

for col in required_columns:
    if col not in df.columns:
        df[col] = None

print("\nWhat would you like to do?")
print("1 - Smart recommendation")
print("2 - Mark book as finished")
print("3 - Mark book as DNF")
print("4 - Add book to TBR")
print("5 - Update reading progress")

choice = input("Enter choice: ")

if choice == "1":

    df = normalize_rating(df)
    df = compute_recency(df)

    read_ranked = score_read_books(df)
    tbr_ranked = score_tbr_books(df)

    print("\nTop Read Books:")
    print(read_ranked[["Title", "score"]].head(5))

    print("\nRecommended From TBR:")
    print(tbr_ranked[["Title", "Authors", "score"]].head(5))

    recommendation = recommend_one(tbr_ranked)

    print("\nTonight You Read:")
    print(recommendation[["Title", "Authors", "score"]])

elif choice == "2":

    title = input("Enter exact book title: ")

    if title not in df["Title"].values:
        print("Book not found.")
    else:
        manual_date = input("Enter completion date (YYYY-MM-DD) or leave blank for today: ")

        if manual_date:
            today = pd.to_datetime(manual_date)
        else:
            today = pd.Timestamp.today().normalize()

        while True:
            rating_input = input("Enter rating (1-5): ")
            try:
                rating = float(rating_input)
                if 1 <= rating <= 5:
                    break
                else:
                    print("Rating must be between 1 and 5.")
            except ValueError:
                print("Enter a valid number.")

        df.loc[df["Title"] == title, "Read Status"] = "read"
        df.loc[df["Title"] == title, "Last Date Read"] = today
        df.loc[df["Title"] == title, "Progress (%)"] = 100
        df.loc[df["Title"] == title, "Star Rating"] = rating

        print(f"{title} marked as finished on {today.date()} with rating {rating}.")

        df.to_csv(PROCESSED_PATH, index=False)

elif choice == "3":

    title = input("Enter exact book title: ")

    if title not in df["Title"].values:
        print("Book not found.")
    else:
        manual_date = input("Enter DNF date (YYYY-MM-DD) or leave blank for today: ")

        if manual_date:
            today = pd.to_datetime(manual_date)
        else:
            today = pd.Timestamp.today().normalize()

        df.loc[df["Title"] == title, "Read Status"] = "dnf"
        df.loc[df["Title"] == title, "Last Date Read"] = today
        df.loc[df["Title"] == title, "Star Rating"] = 1  # default DNF rating

        print(f"{title} marked as DNF on {today.date()} with default rating 1.")

        df.to_csv(PROCESSED_PATH, index=False)

elif choice == "4":

    new_title = input("Enter book title: ")
    new_author = input("Enter author: ")

    new_row = {
        "Title": new_title,
        "Authors": new_author,
        "ISBN/UID": str(pd.Timestamp.now().timestamp()),
        "Read Status": "to-read",
        "Star Rating": None,
        "Last Date Read": None,
        "Progress (%)": 0,
        "Pages Read": 0,
        "Total Pages": None
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(PROCESSED_PATH, index=False)

    print(f"{new_title} added to TBR.")

elif choice == "5":

    title = input("Enter exact book title: ")

    if title not in df["Title"].values:
        print("Book not found.")
    else:

        total_pages_input = input("Enter total pages (leave blank if unchanged): ")
        pages_read_input = input("Enter pages read: ")

        if total_pages_input:
            df.loc[df["Title"] == title, "Total Pages"] = int(total_pages_input)

        current_total = df.loc[df["Title"] == title, "Total Pages"].values[0]

        if not current_total:
            print("Total pages not set. Please set total pages first.")
        else:
            pages_read = int(pages_read_input)

            if pages_read > current_total:
                pages_read = current_total

            progress = round((pages_read / current_total) * 100, 2)

            df.loc[df["Title"] == title, "Pages Read"] = pages_read
            df.loc[df["Title"] == title, "Progress (%)"] = progress

            if progress >= 100:
                df.loc[df["Title"] == title, "Read Status"] = "read"
            else:
                df.loc[df["Title"] == title, "Read Status"] = "currently-reading"

            print(f"Progress updated to {progress}%.")

            df.to_csv(PROCESSED_PATH, index=False)

else:
    print("Goodbye.")
