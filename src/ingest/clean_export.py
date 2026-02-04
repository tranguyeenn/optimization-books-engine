import pandas as pd
from pathlib import Path

PATH = Path("data/raw/sample_export.csv")

def clean_export(path):
    df = pd.read_csv(path)

    #normalize blank and turn it into NA
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    #clean columns
    df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_"))
    df = df.drop_duplicates()

    #clean author
    if "title" in df.columns:
        df["author"] = (df["author"].str.strip().str.title())

    #clean my_rating
    if "my_rating" in df.columns:
       df["my_rating"] = pd.to_numeric(df["my_rating"], errors="coerce")

    #clean avg_rating
    if "average_rating" in df.columns:
        df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce")

    #clean publisher
    if "publisher" in df.columns:
        df["publisher"] = (df["publisher"].str.strip().str.title())

    #clean binding
    if "binding" in df.columns:
        df["binding"] = (df["binding"].str.strip().str.title())

    #clean year_published
    if "year_published" in df.columns:
        df["year_published"] = (pd.to_numeric(df["year_published"], errors="coerce").astype("Int64"))

    #clean original_pub_yr
    if "original_publication_year" in df.columns:
        df["original_publication_year"] = (pd.to_numeric(df["original_publication_year"], errors="coerce").astype("Int64"))

    #clean date_read
    if "date_read" in df.columns:
        df["date_read"] = pd.to_datetime(df["date_read"], errors="coerce")

    #clean date_added
    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")

    #checking date_read and date_added logic
    if {'date_read', 'date_added'}.issubset(df.columns):
        df.loc[df['date_read'] < df['date_added'], 'date_read'] = pd.NA
    
    #clean shelves
    if "shelves" in df.columns:
        df["shelves"] = (df["shelves"].str.strip().str.title())

    #clean bookshelves
    if "bookshelves" in df.columns:
        df["bookshelves"] = (df["bookshelves"].str.strip().str.title())

    #clean isbn
    if "isbn" in df.columns:
        df["isbn"] = df["isbn"].astype(str).str.replace(r"[^0-9X]", "", regex=True)

    #language normalization
    if "language_code" in df.columns:
        df["language_code"] = df["language_code"].str.lower()

    #clean review
    if "my_review" in df.columns:
        df = df.drop(columns=["my_review"], errors="ignore")
    
    return df
