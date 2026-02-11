import pandas as pd
from pathlib import Path

PATH = Path("data/raw/storyGraph_export.csv")

def load_csv(csv):
    df = pd.read_csv(csv)
    return df