from pathlib import Path
from ingest.load_csv import load_csv
from preprocess.clean_books import clean_books
import pandas as pd

PATH = Path('data/raw/storyGraph_export.csv')
df = load_csv(PATH)
df = clean_books(df)

def normalize_rating(df):
    min_rating = df["Star Rating"].min()
    max_rating = df["Star Rating"].max()

    if max_rating == min_rating:
        df["rating_norm"] = 1.0
    else:
        df["rating_norm"] = (
            (df["Star Rating"] - min_rating) /
            (max_rating - min_rating)
        )

    today = pd.Timestamp.today().normalize()
    df["days_since_read"] = (
        today - df["Last Date Read"]
    ).dt.days

    min_days = df["days_since_read"].min()
    max_days = df["days_since_read"].max()

    if max_days == min_days:
        df["recency_norm"] = 1.0
    else:
        df["recency_norm"] = 1 - (
            (df["days_since_read"] - min_days) /
            (max_days - min_days)
        )

    return df

df = normalize_rating(df)
print(df.columns)