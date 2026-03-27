"use client";

import Papa from "papaparse";
import { ChangeEvent, DragEvent, useMemo, useState } from "react";

type RawRow = Record<string, unknown>;

type RankedBook = {
  title: string;
  author: string;
  score: number;
};

type MappingState = {
  title: string;
  author: string;
  rating: string;
  readStatus: string;
  date: string;
};

const defaultMapping: MappingState = {
  title: "Title",
  author: "Authors",
  rating: "Star Rating",
  readStatus: "Read Status",
  date: "Last Date Read"
};

function toNumber(value: unknown): number | null {
  if (value === null || value === undefined) return null;
  const parsed = Number(String(value).trim());
  return Number.isFinite(parsed) ? parsed : null;
}

function computeMinMax(values: number[]): { min: number; max: number } {
  return {
    min: Math.min(...values),
    max: Math.max(...values)
  };
}

function normalize(value: number, min: number, max: number): number {
  if (max === min) return 1;
  return (value - min) / (max - min);
}

function rankRows(rows: RawRow[], mapping: MappingState, limit: number): RankedBook[] {
  const readRows = rows.filter((row) => {
    const raw = row[mapping.readStatus];
    return String(raw ?? "").trim().toLowerCase() === "read";
  });

  const ratingValues = readRows
    .map((row) => toNumber(row[mapping.rating]))
    .filter((value): value is number => value !== null);

  if (readRows.length === 0 || ratingValues.length === 0) {
    return [];
  }

  const { min, max } = computeMinMax(ratingValues);

  return readRows
    .map((row) => {
      const title = String(row[mapping.title] ?? "Untitled").trim() || "Untitled";
      const author = String(row[mapping.author] ?? "Unknown author").trim() || "Unknown author";
      const rating = toNumber(row[mapping.rating]) ?? (min + max) / 2;
      return {
        title,
        author,
        score: normalize(rating, min, max)
      };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

export default function HomePage() {
  const [csvFileName, setCsvFileName] = useState<string>("");
  const [rows, setRows] = useState<RawRow[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [resultsLimit, setResultsLimit] = useState<number>(5);
  const [error, setError] = useState<string>("");
  const [isDragActive, setIsDragActive] = useState<boolean>(false);
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [mapping, setMapping] = useState<MappingState>(defaultMapping);

  const ranked = useMemo(() => rankRows(rows, mapping, resultsLimit), [rows, mapping, resultsLimit]);

  const parseFile = (file: File) => {
    setError("");
    Papa.parse<RawRow>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        if (result.errors.length > 0) {
          setError("CSV could not be parsed. Check format and headers.");
          return;
        }
        const parsedRows = result.data.filter((item) => Object.keys(item).length > 0);
        const first = parsedRows[0] ?? {};
        const foundHeaders = Object.keys(first);
        setRows(parsedRows);
        setHeaders(foundHeaders);
        setCsvFileName(file.name);
      },
      error: () => {
        setError("Unable to read file.");
      }
    });
  };

  const onInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    parseFile(file);
  };

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragActive(false);
    const file = event.dataTransfer.files?.[0];
    if (!file) return;
    parseFile(file);
  };

  const updateMapping = (key: keyof MappingState, value: string) => {
    setMapping((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <main className="page">
      <section className="card">
        <header className="header">
          <h1 className="title">LibroRank</h1>
          <p className="subtitle">Upload a CSV and get a calm, focused ranked reading list.</p>
        </header>

        <div className="panel">
          <div
            className={`dropzone ${isDragActive ? "dropzone-active" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragActive(true);
            }}
            onDragLeave={() => setIsDragActive(false)}
            onDrop={onDrop}
          >
            <p>Drop CSV here</p>
            <p className="small">or choose a file manually</p>
            <label className="button">
              Choose File
              <input type="file" accept=".csv,text/csv" hidden onChange={onInputChange} />
            </label>
          </div>

          <div className="row">
            <span className="small">{csvFileName ? `Loaded: ${csvFileName}` : "No file selected yet"}</span>
            <div className="row">
              <span className="small muted">Top</span>
              <select
                className="select"
                value={resultsLimit}
                onChange={(event) => setResultsLimit(Number(event.target.value))}
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
              </select>
            </div>
          </div>

          {error ? <p className="small" style={{ color: "#ff9da5" }}>{error}</p> : null}
        </div>

        <div className="panel advanced">
          <div className="row">
            <p className="small">Optional mapping</p>
            <button className="button" onClick={() => setShowAdvanced((prev) => !prev)}>
              {showAdvanced ? "Hide" : "Show"}
            </button>
          </div>

          {showAdvanced ? (
            <div className="grid">
              {[
                { key: "title", label: "Title column" },
                { key: "author", label: "Author column" },
                { key: "rating", label: "Rating column" },
                { key: "readStatus", label: "Status column" },
                { key: "date", label: "Date column" }
              ].map((field) => (
                <label key={field.key} className="field">
                  <span className="label">{field.label}</span>
                  <input
                    className="input"
                    value={mapping[field.key as keyof MappingState]}
                    onChange={(event) =>
                      updateMapping(field.key as keyof MappingState, event.target.value)
                    }
                    list={`headers-${field.key}`}
                  />
                  <datalist id={`headers-${field.key}`}>
                    {headers.map((header) => (
                      <option key={header} value={header} />
                    ))}
                  </datalist>
                </label>
              ))}
            </div>
          ) : null}
        </div>

        <section className="results">
          {ranked.length === 0 ? (
            <div className="panel">
              <p className="small">No ranked results yet. Upload a CSV with read books and ratings.</p>
            </div>
          ) : (
            ranked.map((item, index) => (
              <article key={`${item.title}-${item.author}-${index}`} className="item">
                <span className="rank">#{index + 1}</span>
                <div>
                  <p className="book">{item.title}</p>
                  <p className="meta">{item.author}</p>
                </div>
                <span className="chip">{item.score.toFixed(2)}</span>
              </article>
            ))
          )}
        </section>
      </section>
    </main>
  );
}
