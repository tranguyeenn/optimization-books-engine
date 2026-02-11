from pathlib import Path
from ingest.load_csv import load_csv
from preprocess.clean_books import clean_books

PATH = Path('data/raw/storyGraph_export.csv')
df = load_csv(PATH)
df = clean_books(df)

def normalize_rating(df):
    min_rating = df["Star Rating"].min()
    max_rating = df["Star Rating"].max()

    df["rating_norm"] = (
        (df["Star Rating"] - min_rating) /
        (max_rating - min_rating)
    )

    return df