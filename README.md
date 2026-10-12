# Research Atlas

A university research opportunity workspace with a Flask REST API, MySQL persistence and a responsive HTML/CSS/JavaScript interface. Faculty members can post, view, update, close and delete research opportunities in one place.

Prepared for: **Shayan Ali — 24P-0573**. Course: Computer Networks, CS-5B, Fall 2026 (Assignment 1).

## Submission links

- **GitHub repository:** https://github.com/shayanali005/research-opportunity-portal
- **Demonstration video (about one minute):** https://github.com/shayanali005/research-opportunity-portal/raw/refs/heads/main/assignment-1-cn_cjrlhJmE.webm (the video file is also included in the submission ZIP)

## Provenance

This is an AI-assisted redesign of the Research Opportunity Portal supplied by Sohrab (24P-0604). Field definitions and input validation are adapted from that project. The interface, API application structure, persistence module, collection and documentation were rewritten for this version. This statement identifies the actual sources of the work; the recipient line above is not a claim of sole authorship. Review and understand the code and follow your instructor's rules on reused work and AI assistance.

## Features

- Create, list, view, update and delete research opportunities, all stored in MySQL.
- Close or reopen an opportunity (status Open / Closed).
- Search, status filter and sorting (deadline, title, newest) in the browser.
- Success and error messages, plus required-field validation in the form and on the server.
- Parameterized SQL queries, row locking during updates, rollback on failures and consistent JSON errors.
- Postman collection with response checks, including a 404 and a 400 validation case.

## Prerequisites

Python 3.11 or later, MySQL 8.0.16 or later, and Postman for the API demonstration. Internet access is needed once to install the Python dependencies. The frontend uses no CDN, fonts or JavaScript dependencies.

## Setup on Linux (Ubuntu) / macOS

Open a terminal in the `research-atlas` directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Create the database and a local application user (replace the sample password with your own):

```bash
sudo mysql < database/schema.sql
sudo mysql -e "CREATE USER 'atlas_app'@'localhost' IDENTIFIED BY 'CHOOSE_A_PRIVATE_PASSWORD'; GRANT SELECT, INSERT, UPDATE, DELETE ON research_atlas.* TO 'atlas_app'@'localhost';"
```

If your MySQL root account uses a password, use `mysql -u root -p` instead of `sudo mysql`.

Open `.env` and set `DB_PASSWORD` to the same password. Do not commit `.env`. Then start the server:

```bash
.venv/bin/python run.py
```

Open **http://127.0.0.1:5050** and keep the terminal open. Always run the app with `.venv/bin/python` (not the system `python3`) so the installed packages are found. The frontend must be opened through this server, not by double-clicking its HTML file.

## Setup on Windows

Open a terminal in the `research-atlas` directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open MySQL Workbench with an administrator connection, open `database/schema.sql` and execute it. Alternatively, use the MySQL command-line client:

```text
mysql -u root -p
SOURCE C:/full/path/to/research-atlas/database/schema.sql;
```

Create a local application user in the MySQL client (replace the sample password):

```sql
CREATE USER 'atlas_app'@'localhost' IDENTIFIED BY 'CHOOSE_A_PRIVATE_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE ON research_atlas.* TO 'atlas_app'@'localhost';
```

Edit `.env` with that password and your actual MySQL host and port, then start the server:

```powershell
.\.venv\Scripts\python.exe run.py
```

Open **http://127.0.0.1:5050**.

## API

| Method | Route | Result |
| --- | --- | --- |
| POST | `/api/opportunities` | Create; HTTP 201 |
| GET | `/api/opportunities` | List; HTTP 200 |
| GET | `/api/opportunities/:id` | Details; HTTP 200 or 404 |
| PUT | `/api/opportunities/:id` | Update supplied fields; HTTP 200 |
| DELETE | `/api/opportunities/:id` | Delete; HTTP 200 or 404 |

List supports optional `q` and `status=Open` or `status=Closed`. Successful records are returned under `data`; errors use `error` and optionally `details`. Invalid JSON, unknown fields and failed validation return 400. Database errors return 500 without exposing credentials. PUT accepts a subset of fields, including a status-only update. A status of Open is independent of the deadline; closing is a manual action.

Required fields: `research_title`, `research_description`, `research_area`, `faculty_name`, `department`, `required_skills`, `available_positions`, `application_deadline`. Status defaults to Open. Positions must be a positive integer. Dates must be real dates in YYYY-MM-DD format. Blank strings are rejected.

## Postman testing

Import `postman/Research-Atlas.postman_collection.json` into Postman, start the server, then run the collection in order. `base_url` defaults to port 5050. The collection:

1. creates three opportunities,
2. retrieves all of them and one by ID,
3. updates the first, closes it, then deletes it,
4. requests the deleted record again (404 Not Found),
5. sends one request with missing fields (400 validation error).

It leaves the other two records in the database. Repeat runs create more records, so use a disposable database for testing.

## Project structure

```text
run.py                 Local server entry point
server/__init__.py     REST routes and application configuration
server/storage.py      MySQL queries and transactions
server/validation.py   Field validation
web/                   Browser UI
database/schema.sql    Database and table setup
postman/               Importable API collection
docs/                  Verification and demonstration guidance
```

## Troubleshooting

This is a local coursework application without authentication, so it should not be exposed publicly.

- **Database unavailable:** make sure MySQL is running, the schema has been executed and the `.env` credentials and port are correct.
- **Port already in use:** stop the old server or set `PORT` in `.env`, and change Postman's `base_url` to match.
- **Empty dashboard:** normal on first use; add records with the form or Postman.
- **`ModuleNotFoundError`:** install the requirements and run the app with the same virtual-environment Python (`.venv/bin/python`).

See `docs/VERIFICATION.md` for the checks performed on this package.
