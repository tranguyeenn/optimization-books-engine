# TBR ML Scraper & Recommender

A command-line **book recommendation system** that generates personalized “what should I read next?” suggestions using a user’s reading history (Goodreads-style CSV exports) and a curated Open Library corpus.

This project focuses on **end-to-end system design**: data ingestion, normalization, profiling, ranking, and explainable recommendations, instead of jumping straight to opaque machine learning models.

---

## Features

- Import user reading history from Goodreads-style CSV files  
- Extract **recently read** and **currently reading** books  
- Build a lightweight **user taste profile**  
- Rank books from an Open Library corpus using:
  - genre alignment
  - description similarity
  - psychological / literary biasing
  - popularity fallback  
- Deterministic, explainable recommendations  
- Fully runnable CLI pipeline (no notebooks required)

---

## Design Philosophy

This project intentionally avoids premature machine learning.

Instead, it emphasizes:
- clean data contracts
- modular architecture
- interpretable ranking logic
- graceful fallbacks when personalization fails

The system is designed so that heuristic scoring can later be swapped with an ML model **without changing the pipeline**.

---

## Project Structure

```bash
tbr-ml-scraper/
├── api/ # API stubs (future-facing)
├── data/
│ ├── raw/ # raw scraped Open Library data
│ ├── processed/ # cleaned & enriched corpus
│ └── db/ # optional SQLite storage
│
├── ingest/ # user data ingestion
│ ├── schema.py # UserBook data contract
│ ├── goodreads.py # Goodreads CSV parser
│ └── loader.py # ingestion dispatcher
│
├── recommend/ # recommendation logic
│ ├── profile.py # user taste modeling
│ └── rank.py # scoring & ranking
│
├── ml/ # optional ML experiments
├── preprocess/ # corpus cleaning & enrichment
├── search/ # indexing & retrieval utilities
├── utils/ # shared helpers (text, logging, ids)
├── tests/
├── notebooks/
│
├── main.py # CLI entry point
├── requirements.txt
└── README.md
```


---

## End-to-End Pipeline

```txt
User CSV (Goodreads)
↓
Ingestion & Normalization
↓
Recent Reads Selection
↓
User Taste Profile
↓
Open Library Corpus
↓
Scoring & Ranking
↓
Recommended Books (CLI)
```


---

## Getting Started

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Prepare a user CSV

You can use a real Goodreads export or a mock file:
```csv
Title,Author,Exclusive Shelf,Date Read
Crime and Punishment,Fyodor Dostoevsky,currently-reading,
A Little Life,Hanya Yanagihara,read,2023/11/01
The Bell Jar,Sylvia Plath,read,2023/10/15
```

### 3. Run the recommender
``` bash
python3 main.py
```

Paste the full path to your CSV when prompted.

----
## Example Output
``` yaml
📚 TBR Recommender
----------------------------------------
Recent reads detected:
• Crime and Punishment (currently_reading)
• A Little Life (read)
• The Bell Jar (read)

Recommended reads:
----------------------------------------
1. Villette, a novel
   Author: Charlotte Brontë

2. The Waves
   Author: Virginia Woolf

3. Babbitt
   Author: Sinclair Lewis
```
---
## Recommendation Strategy (Current)

Each candidate book is scored using:

- Genre alignment (primary signal)
- Description keyword overlap
- Author affinity (weak)
- Penalty for children’s literature
- Boosts for philosophical / psychological works

If no personalized matches are found, the system falls back to popular classics using edition count.
All logic is deterministic and explainable.

--- 
## Future Improvements

- Add “why this book” explanations per recommendation
- Swap heuristic scoring for trained ranking models
- Support StoryGraph / Fable exports
- Add embeddings for semantic similarity
- Web or API interface
- Persistent user profiles

---
## Why This Project Exists

Most recommender demos skip the hard parts:

- ingestion
- normalization
- evaluation
- failure modes

This project treats recommendation as a systems problem, not just a modeling one.
---
## Author

Built by Trang as a hands-on exploration of recommender systems, data pipelines, and ML-ready architecture.


