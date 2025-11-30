# MyToDo_App

A small, minimal ToDo web application built with Flask and Bootstrap. This project demonstrates basic CRUD operations, form handling, templating with Jinja2, and persistence using Flask-SQLAlchemy with a local SQLite database.

---

## Features
- Add new todos (title + description)
- List existing todos
- Update and delete todos
- Simple responsive UI using Bootstrap

## Tech Stack
- Python 3.10+
- Flask
- Flask-SQLAlchemy (SQLite)
- Jinja2 templates
- Bootstrap 5 (CDN)

## Repository Structure

```
e:/VSCode/Python_flask/
├─ app.py                # Flask application and routes
├─ requirements.txt      # (optional) pinned dependencies
├─ .gitignore
├─ templates/            # Jinja2 templates (base.html, index.html, about.html)
├─ static/               # static files (styles, images) — create if needed
└─ venu/                 # local virtualenv (ignored)
```

## Prerequisites
- Python 3.10 or newer
- Git (optional)

## Setup (PowerShell)

1. Clone the repository (if not already local):

```powershell
git clone <repo-url>
cd Python_flask
```

2. Create a virtual environment (you already created `venu`) and activate it:

```powershell
python -m venv venu
E:\VSCode\Python_flask\venu\Scripts\Activate.ps1
```

3. Install dependencies (recommended to create a `requirements.txt` first):

```powershell
# If you have a requirements.txt
pip install -r requirements.txt

# Or install required packages manually
pip install Flask Flask-SQLAlchemy
```

Tip: To generate a `requirements.txt` that captures your current environment, run:

```powershell
pip freeze > requirements.txt
```

## Initialize the database

This project includes a Flask CLI command `init-db` that will create the SQLite database and tables.

From PowerShell with the venv activated:

```powershell
$env:FLASK_APP = 'app.py'
flask init-db
```

Alternatively, you can create the tables from a Python REPL:

```powershell
python
# inside the python prompt:
from app import app, db
with app.app_context():
    db.create_all()
```

The default database file is `ToDoList.db` (created in the project root).

## Run the app

With venv activated and `FLASK_APP` set:

```powershell
$env:FLASK_APP = 'app.py'
flask run
```

Or run directly (development mode):

```powershell
python app.py
```

Open http://127.0.0.1:5000/ in your browser. Visit `/about` for the project/about page.

## Development notes
- Templates live in `templates/`.
- Static assets (images, CSS) should go in `static/`. If you add custom CSS, reference it from `base.html` as `/static/style.css`.
- The project currently uses Bootstrap via CDN for quick styling.

## Common tasks
- Add a new todo: use the form on the homepage and submit.
- Edit a todo: click 'Update' next to an item and submit the update form.
- Delete a todo: click 'Delete' next to an item.

## Git
Add and commit files as usual. The repository includes a `.gitignore` that excludes virtual environments, the SQLite DB file, and editor/OS artifacts.

If you accidentally committed the virtualenv or DB, remove them from the repo and commit the removal:

```powershell
git rm -r --cached venu
git rm --cached ToDoList.db
git commit -m "Remove venv and DB from repository"
```

## Deployment (notes)
- For simple deployments you can use any WSGI-compatible host. Common steps:
  - Create a `requirements.txt` (see above)
  - Add a `Procfile` and use a WSGI server (e.g., `gunicorn`) for Heroku-like environments.

Example `Procfile` (Heroku):

```
web: gunicorn app:app
```

Heroku-specific notes: Heroku requires `requirements.txt`, a `Procfile`, and optional `runtime.txt`. Also set environment variables (e.g., `FLASK_ENV`, `DATABASE_URL`) as needed on the host.

## Enhancements & Roadmap
- Add user accounts and authentication
- Add due dates and filtering/sorting
- Add better form validation and flash messages
- Add tests and CI integration

## Contact
If you'd like help extending this project, open an issue or email: santoshsunadholi13@gmail.com

---

Thank you for using MyToDo_App — a small, extendable Flask learning project.
