# WineDashboard

Streamlit dashboard for exploring the UCI Wine dataset (178 wines, 13 variables, 3 classes).

## Run locally

Requirements: `git` and Docker Desktop. Python is not needed on the host: the app runs in a
Python 3.12 container, and the dataset ships inside scikit-learn, so no database or download
is involved.

```bash
git clone https://github.com/JuanD-1117/WineDashboard.git
cd WineDashboard
./instalar.sh
```

The script builds the image, starts the app, waits until it answers, and opens
**http://localhost:8501**. If Docker Desktop is closed on macOS, the script opens it and waits.
If port 8501 is taken, it uses the next free port and prints the URL.

| Command | Effect |
|---|---|
| `./instalar.sh` | Build and start. Safe to repeat |
| `WINE_PORT=8600 ./instalar.sh` | Use another port |
| `docker compose down` | Stop the app |
| `./limpiar.sh` | Remove this project's container and image, and nothing else |

### Without Docker

Needs Python 3.12 or newer, because the pinned versions in `requirements.txt` require it.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

## Features

- Sidebar: variables, chart type, wine class, and an extra range filter.
- Charts: histogram, scatter plot, boxplot by class, correlation matrix.
- Indicators: number of rows, classes, variables, and variable means.
