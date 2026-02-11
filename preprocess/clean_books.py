from ingest.load_csv import load_csv
import pandas as pd
from pathlib import Path
import random

PATH = Path('data/raw/storyGraph_export.csv')
df = load_csv(PATH)

def clean_books(df):
    cols_to_keep = ['Title', 'Authors', 'ISBN/UID', 'Read Status', 'Star Rating']
    df = df[cols_to_keep]

    df = df[df["Read Status"].isin(["read", "currently-reading"])]
    mean_rating = df["Star Rating"].mean()

    df["Star Rating"] = df["Star Rating"].fillna(mean_rating)
    df["Star Rating"] = pd.to_numeric(df["Star Rating"], errors="coerce")

    missing_mask = df["ISBN/UID"].isna()
    df.loc[missing_mask, "ISBN/UID"] = [
        str(random.randint(10**12, 10**13 - 1)) for _ in range(missing_mask.sum())
    ]
    return df

