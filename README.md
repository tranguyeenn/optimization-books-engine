# TBR Engine

A modular book recommendation and management engine built in Python.
This project ingests a StoryGraph export, performs data cleaning and feature engineering, and provides both ranked and random book recommendations from a user's TBR (To Be Read) list. It also supports persistent updates such as marking books as finished, DNF, or adding new entries.

## Features
- CSV ingestion and structured preprocessing
- Data cleaning and normalization
- Recency-based scoring
- Weighted ranking system
- Author-preference recommendation logic
- Exploration via controlled randomness
- Deduplication and optional diversity filtering
- CLI-based interaction
- Persistent state management using CSV storage

## Project Structure
``` txt
tbr-engine/
│
├── data/
│   ├── raw/
│   │   └── storyGraph_export.csv
│   └── processed/
│       └── books.csv
│
├── ingest/
│   └── load_csv.py
│
├── preprocess/
│   ├── clean_books.py
│   └── normalize.py
│
├── ranking/
│   └── score.py
│
├── cli/
│   └── manage_books.py
│
├── main.py
└── README.md
```

## How It Works
### 1. Ingestion
Loads a StoryGraph CSV export from data/raw.

### 2. Cleaning
- Normalizes categorical fields
- Handles missing ratings
- Ensures date formatting
- Preserves all reading statuses

### 3. Feature Engineering
- Min-max normalization of ratings
- Recency scoring based on days since read

### 4. Ranking Logic
- Read books scored using weighted rating and recency
- TBR books ranked using author preference learned from past ratings
- Slight randomness added for exploration
- Author diversity constraint

### 5. CLI Interaction
Users can:
- Generate a smart recommendation
- Mark a book as finished (auto sets today's date)
- Mark a book as DNF
- Add a new book to TBR
- Persist changes to CSV

## Installation
Clone the repository:
``` bash
git clone https://github.com/tranguyeenn/optimization-books-engine
```

Create and activate a virtual environment:
``` bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:
``` bash
pip install pandas numpy
```

## Usage
Run the application:
``` bash
python main.py
```

You will be prompted with a menu:
``` txt
1 - Smart recommendation
2 - Mark book as finished
3 - Mark book as DNF
4 - Add book to TBR
5 - Exit
```

Changes are automatically saved to:
``` txt
data/processed/books.csv
```

## Design Principles
- Separation of concerns
- Modular architecture
- Clean pipeline orchestration
- Persistent state management

## Future Improvements
- Web-based UI (Streamlit or Flask)
- REST API layer
- Recommendation diversity controls
- Collaborative filtering extensions
- SQLite or database backend
- Unit testing and CI integration

## Author
Trang Nguyen

## License
MIT License
