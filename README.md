# DC Legends WarehouseOS

DC Legends WarehouseOS is a mobile-first Flask warehouse operating system,
formerly called QR Legends. It supports receiving, directed putaway, inventory
control, replenishment, cycle counting, zone picking, shipping, labor, safety,
reporting, QR workflows, role-based access, and ERP-related modules.

## Important: GitHub Pages

GitHub Pages cannot run this application. It only hosts static files and cannot
execute Flask routes, Python code, sessions, or JSON-backed APIs.

Use GitHub as the source repository, then deploy the Flask app to Render,
Railway, Fly.io, or another Python web host.

Correct architecture:

```text
GitHub repository -> Render/Railway/Fly.io -> live Flask URL
```

## Local Installation

Python 3.11 or newer is recommended.

```bash
git clone https://github.com/ZaspDragon/QR-LEGENDS.git
cd QR-LEGENDS
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set a strong `SECRET_KEY`. Environment
variables may also be set directly in the shell or hosting dashboard.

## Run Locally

PowerShell:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-value"
$env:PORT = "5000"
python main.py
```

Open `http://127.0.0.1:5000/company_login`.

## Production Command

```bash
gunicorn main:app
```

Gunicorn is intended for Linux deployment environments. On Windows, use
`python main.py` for local development.

## Deploy To Render

1. Create a new **Web Service** in Render.
2. Connect `ZaspDragon/QR-LEGENDS`.
3. Select the branch to deploy.
4. Runtime: **Python 3**.
5. Build command: `pip install -r requirements.txt`.
6. Start command: `gunicorn main:app`.
7. Add `SECRET_KEY` as a secret environment variable.
8. Add `FLASK_ENV=production`.
9. Deploy and open `/company_login`.

`render.yaml` contains equivalent defaults.

## Deploy To Railway

1. Create a Railway project and choose **Deploy from GitHub repo**.
2. Select `ZaspDragon/QR-LEGENDS`.
3. Railway detects Python from `requirements.txt`.
4. Set the start command to `gunicorn main:app`.
5. Add `SECRET_KEY` and `FLASK_ENV=production`.
6. Generate a public domain and open `/company_login`.

Railway supplies `PORT` automatically.

## Data Safety

Runtime files under `data/*.json` and uploaded files are ignored by Git.
Only sanitized `data/example_*.json` files belong in the repository. A fresh
clone creates missing runtime JSON files safely when the application starts.

The current JSON storage is suitable for development and single-instance
deployments. For durable multi-instance production use, migrate operational
data to a managed database or attach a persistent disk.
