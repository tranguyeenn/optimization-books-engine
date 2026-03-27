import numpy as np

def _resolve_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def score_read_books(df, rating_weight=0.7, recency_weight=0.3):
    status_col = _resolve_column(df, ["read_status", "Read Status"])
    if status_col is None:
        return df.iloc[0:0].copy()

    read_df = df[df[status_col].astype(str).str.strip().str.lower() == "read"].copy()
    if "rating_norm" not in read_df.columns:
        read_df["rating_norm"] = 0.5
    if "recency_norm" not in read_df.columns:
        read_df["recency_norm"] = 0.5

    read_df["score"] = (
        rating_weight * read_df["rating_norm"] +
        recency_weight * read_df["recency_norm"]
    )

    read_df["score"] = read_df["score"].clip(0, 1)

    read_df = read_df.sort_values(
        by="score",
        ascending=False
    )

    return read_df

def score_tbr_books(df, randomness_strength=0.05, diverse_authors=True):
    status_col = _resolve_column(df, ["read_status", "Read Status"])
    author_col = _resolve_column(df, ["author", "Authors"])
    title_col = _resolve_column(df, ["title", "Title"])
    if status_col is None:
        return df.iloc[0:0].copy()
    if author_col is None:
        author_col = "author"
        df = df.copy()
        df[author_col] = "unknown"
    if title_col is None:
        title_col = "title"
        df = df.copy()
        df[title_col] = ""
    if "rating_norm" not in df.columns:
        df = df.copy()
        df["rating_norm"] = 0.5

    status_series = df[status_col].astype(str).str.strip().str.lower()
    read_df = df[status_series == "read"].copy()
    tbr_df = df[status_series == "to-read"].copy()

    # Remove duplicate books
    tbr_df = tbr_df.drop_duplicates(
        subset=[title_col, author_col]
    )

    author_pref = (
        read_df
        .groupby(author_col)["rating_norm"]
        .mean()
        .reset_index()
    )

    author_pref.rename(
        columns={"rating_norm": "author_score"},
        inplace=True
    )

    tbr_df = tbr_df.merge(
        author_pref,
        on=author_col,
        how="left"
    )

    global_avg = read_df["rating_norm"].mean() if not read_df.empty else 0.5

    tbr_df["author_score"] = (
        tbr_df["author_score"]
        .fillna(global_avg)
    )

    noise = np.random.uniform(
        -randomness_strength,
        randomness_strength,
        len(tbr_df)
    )

    tbr_df["score"] = tbr_df["author_score"] + noise

    # Keep score in clean range
    tbr_df["score"] = tbr_df["score"].clip(0, 1)

    tbr_df = tbr_df.sort_values(
        by="score",
        ascending=False
    )

    # Optional diversity: only 1 book per author
    if diverse_authors:
        tbr_df = tbr_df.drop_duplicates(
            subset=[author_col]
        )

    return tbr_df

def recommend_one(tbr_ranked):

    if len(tbr_ranked) == 0:
        return None

    # Pick randomly from top 5
    top_slice = tbr_ranked.head(5)
    recommendation = top_slice.sample(1)

    return recommendation