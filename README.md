# SAFA — Customer Feedback Analyser

> **SAFA (S**tands for **Customer Feedback Analyser)** — A compact Flask-based web app that transforms customer reviews into actionable business insights using Groq / LangChain prompts. Upload an Excel file containing reviews, get per-review summaries + sentiment tagging, a dashboard with aggregate stats, and longer analysis & suggested improvements.

### Try the tool at [safa](https://safa-mcha.onrender.com) 👈

---

## 1. Project overview

SAFA is a small, easy-to-run customer feedback analyser built with Flask. It relies on prompt-driven LLM calls (Groq via `langchain-groq`) to:

- Summarize each review into a compact statement + a satisfaction number.
- Tag reviews into categories (e.g. product quality, delivery, price).
- Produce an aggregate analysis report and suggested improvements.

The UI is minimal (Flask + simple templates). The app is packaged with a `Dockerfile` so you can run it in a container. The app stores any uploaded Excel file inside the `uploads/` folder as `stored_excel_file.xlsx` and reads the `Text` column to obtain reviews.

---

## 2. Features

- Upload Excel (`.xlsx / .xls`) containing customer reviews and ratings.
- Per-review summarization and sentiment detection.
- Tagging of reviews into categories.
- Dashboard showing average rating, predicted satisfaction score and a table of processed reviews.
- Analysis report (long-form) and suggested improvements (actionable items).
- Several friendly error pages (404, 500, 502, 503).

---

## 3. Quick start (Docker)

> Note: this repo contains a `Dockerfile` so you can build and run the container quickly.

Build and run locally:

```bash
# Build image in the repository root
docker build -t safa_public:latest .

# Run container (example — set the Groq keys as environment variables)
docker run --rm -p 5000:5000 \
  -e summarize_key="<YOUR_GROQ_KEY>" \
  -e tag_key="<YOUR_GROQ_KEY>" \
  -e analysis_key="<YOUR_GROQ_KEY>" \
  -e improvements_key="<YOUR_GROQ_KEY>" \
  safa_public:latest
```

When the container is running, open `http://localhost:5000` in your browser.

**Notes:** the Dockerfile uses `python:3.12-slim` as the base image and creates `/app/uploads` inside the container (so uploaded files persist inside the container file system until removed). See the Dockerfile for exact build steps.

---

## 4. Quick start (local — Python)

Prerequisites:

- Python 3.12 (recommended — the Dockerfile uses `python:3.12-slim`).
- `pip` and a virtual environment (recommended).

Install & run:

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

# Export required env variables (example)
export summarize_key="<YOUR_GROQ_KEY>"
export tag_key="<YOUR_GROQ_KEY>"
export analysis_key="<YOUR_GROQ_KEY>"
export improvements_key="<YOUR_GROQ_KEY>"

python app.py
```

Open `http://localhost:5000`

---

## 5. Environment variables & models

The application expects the following environment variables (used inside `app_functions.py`):

- `summarize_key` — Groq API key used by the summarization prompt.
- `tag_key` — Groq API key used for the tagging prompt.
- `analysis_key` — Groq API key used for the analysis report.
- `improvements_key` — Groq API key used for suggested improvements.

Optional model environment variables (fallback defaults are set in the code):

- `summarize_model` (default: `llama-3.3-70b-versatile`)
- `tag_model` (default: `llama-3.3-70b-versatile`)
- `analysis_model` (default: `qwen/qwen3-32b`)
- `improvements_model` (default: `qwen/qwen3-32b`)

**Important:** Do **not** commit API keys to source control. Use `.env` files excluded by `.gitignore`, Docker secrets, or environment variables in your deployment platform.

---

## 6. Input file format

The app expects an Excel workbook where reviews are stored in a column named exactly **`Text`** and ratings (numerical) are stored in a column named exactly **`Rating`**.

Minimum example (Excel):

| Text                                     | Rating |
|------------------------------------------|--------|
| "Product arrived late but works fine"   | 4      |
| "Battery died in 2 days, very unhappy"  | 1      |

When you upload a file via the UI it is saved as `uploads/stored_excel_file.xlsx` and then processed.

---

## 7. Project layout (file-by-file)

```
├── Dockerfile                # Builds a python:3.12-slim image and installs requirements
├── app.py                    # Flask app (routes, upload, dashboard, error handlers)
├── app_functions.py          # Core logic that calls Groq via langchain-groq (summarize, tag, analyze)
├── requirements.txt          # Python dependencies
├── templates/                # Flask templates (home, upload, dashboard, analysis, suggest, safa, errors)
├── static/                   # static assets (CSS etc — minimal)
└── uploads/                  # runtime uploads (stored_excel_file.xlsx)
```

Short descriptions:

- `app.py` — Hosts the Flask routes: `/` (home), `/upload` (file upload), `/dashboard`, `/analysis`, `/suggest`, `/safa`. It calls helper functions in `app_functions.py` and renders templates. The uploaded file is saved as `uploads/stored_excel_file.xlsx` (see `process_excel()` and `/upload` route).

- `app_functions.py` — Implements:
  - `summarize(text_dict)` — creates a prompt and calls `ChatGroq` to produce CSV text (summaries + satisfaction score + sentiment).
  - `tag_it(text_dict)` — calls `ChatGroq` and returns tags as CSV text.
  - `analysis_report(text_dict)` — returns a long-form analysis of all reviews.
  - `suggested_improvements(text_dict)` — returns actionable improvements.

- `templates/` — Minimal HTML templates for the UI and error pages. A friendly about page (`safa.html`) contains contact information for the author.

- `Dockerfile` — Prepares system deps for `pandas`/`numpy`, installs Python requirements and runs `app.py`.

- `requirements.txt` — List of dependencies (Flask, pandas, numpy, langchain-core, langchain-groq, groq, openpyxl, etc.).

---

## 8. How it works — high-level flow

1. User uploads an Excel file (`/upload`). The file is saved as `uploads/stored_excel_file.xlsx`.
2. `process_excel()` reads the Excel and extracts the `Text` column into a dictionary (`material`) keyed by index.
3. `/dashboard` calls `summarize(material)` and `tag_it(material)`. Those functions are expected to return **raw CSV text** that the code parses into DataFrames.
4. `/analysis` and `/suggest` call `analysis_report(material)` and `suggested_improvements(material)` respectively and render returned markdown/HTML.

Underlying LLM calls are executed through `langchain-groq`'s `ChatGroq` wrapper.

---

## 9. Important implementation notes & gotchas

- **Column name expectations:** uploaded Excel must have `Text` and `Rating` columns (case sensitive) — otherwise the code will raise errors when trying to access these columns.

- **Prompt inconsistency (actionable TODO):** the summarization prompt in `app_functions.py` contains **inconsistent** instructions about CSV column names (the prompt mentions both `Rating` and `Satisfaction Score` in different places). This can cause downstream parsing mismatches. Consider standardizing the prompt to a single header (e.g. `Index,Review,Rating,Sentiment`) and updating the code that parses the CSV accordingly.

- **Environment keys required:** if the Groq keys (`summarize_key`, `tag_key`, etc.) are missing the ChatGroq calls will fail with authentication errors.

- **Template/UI are minimal:** templates are plain HTML placeholders — you may want to improve UX (scripts, CSS) before production use.

- **No license file present:** If you plan to reuse or publish, add a `LICENSE` file to clarify permissions.

- **Uploads are stored on disk inside the container:** Uploaded files will stay in `uploads/` inside the running container. If running in Docker, consider mounting a persistent volume if you want data to survive container restarts.

---

## 10. Troubleshooting & common errors

- `KeyError: 'Text'` or `KeyError: 'Rating'` — uploaded file doesn't contain expected columns. Check the Excel and column names.

- LangChain / Groq errors — check that the environment variable for the corresponding key is set and that you have network access.

- `ModuleNotFoundError` — ensure you installed the packages with `pip install -r requirements.txt` or used the Docker image.

- If the UI shows empty tables, verify that the summarization/tagging functions returned properly-formatted CSV text and that `csv_text_to_dataframe()` successfully parsed it.

---

## 11. Contact

The project includes an about page with contact details for the creator. Use those to reach out if you need help or want collaboration.

(Details are present in `templates/safa.html` — please use the repo contact entry responsibly.)

---

## 12. License

No `LICENSE` file was found in the repository. Add one if you want to make reuse / redistribution explicit.

---

### Final notes

If you want to skip all these and directly jump into the tool, refer the ready-to-use docker image at: [adithya7reddy/safa/](https://hub.docker.com/r/adithya7reddy/safa)
