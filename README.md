# Research Atlas

A redesigned university research opportunity workspace with a Flask REST API, MySQL persistence and a responsive HTML/CSS/JavaScript interface.

Prepared for: **Shayan Ali — 24P-0573**. Course context: Computer Networks, CS-5B, Fall 2026.

## Provenance

This is an AI-assisted redesign of the Research Opportunity Portal supplied by Sohrab (24P-0604). Field definitions and input validation are adapted from that project. The interface, API application structure, persistence module, collection and documentation were rewritten for this version. This statement identifies the actual sources of the work; the recipient line above is not a claim of sole authorship. Review and understand the code and follow your instructor's rules on reused work and AI assistance.

## What changed

- Forest-green sidebar, light dashboard, live statistics and opportunity cards replace the original table layout.
- Search, status filters, deadline/title/newest sorting, modal editor and detail view.
- Separate application factory, validation and transactional storage modules.
- Parameterized MySQL queries, row locking during updates, rollback on failures and consistent JSON errors.
- Standalone Postman collection with response assertions and automatically captured record ID.
- No database credentials, private database files, old virtual environments or old test reports are included.

## Prerequisites

Python 3.11 or later, MySQL 8.0.16 or later, and Postman for the required API demonstration. Internet access is needed once to install the Python dependencies. The frontend uses no CDN, fonts or JavaScript dependencies.

## Setup on Windows

Open a terminal in the extracted `research-atlas` directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open MySQL Workbench with an administrator connection, open `database/schema.sql`, and execute it. Alternatively, use the MySQL command-line client:

```text
mysql -u root -p
SOURCE C:/full/path/to/research-atlas/database/schema.sql;
```

Create a local application user in the MySQL client. Replace the sample password before executing:

```sql
CREATE USER 'atlas_app'@'localhost' IDENTIFIED BY 'CHOOSE_A_PRIVATE_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE ON research_atlas.* TO 'atlas_app'@'localhost';
```

Edit `.env` with that password and your actual MySQL host and port. Do not commit `.env`.

```powershell
.\.venv\Scripts\python.exe run.py
```

Open **http://127.0.0.1:5050**. Keep the terminal open. Start with an empty database and use **New opportunity** to add a call. The frontend must be opened through this server, not by double-clicking its HTML file.

For macOS/Linux, use `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, `cp .env.example .env`, then `.venv/bin/python run.py`.

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

## Postman demonstration

Import `postman/Research-Atlas.postman_collection.json` and run its requests in order. `base_url` defaults to port 5050. The collection creates three records, retrieves them, updates/closes/deletes the first, verifies its 404 and sends invalid data to verify 400. It leaves the other two records for review. Repeat runs create more records; use a disposable database for testing. The collection contains test definitions; importing it does not mean the tests have been run in Postman.

## Project structure

```text
run.py                 Local server entry point
server/__init__.py     REST routes and application configuration
server/storage.py      MySQL queries and transactions
server/validation.py   Field validation
web/                   Browser UI
database/schema.sql    Empty database and table setup
postman/               Importable API collection
docs/                  Verification and demonstration guidance
```

## Remaining submission items

**GitHub repository link: NOT PROVIDED.** Create your own repository, make meaningful commits as you review and develop the work, and replace this line with its real URL. Do not fabricate a development history.

**Demonstration video/link: NOT PROVIDED.** Record your own demonstration (maximum one minute); see `docs/DEMO.md`. A written guide is included, not a recording.

The assignment's filename pattern is `P24_0000_NAME_CLASS.zip`; confirm the class and filename convention with your instructor. The supplied archive uses a descriptive project name because the GitHub/video deliverables are still outstanding.

## Scope and troubleshooting

This is a local coursework application without authentication; any user who can reach it can manage its records. The development server binds to loopback. Do not expose it publicly as a faculty system without adding authentication and production hosting.

- Database unavailable: ensure MySQL is running, execute the schema and verify `.env` credentials/port.
- Port already in use: set `PORT` in `.env` and change Postman's `base_url` to match.
- Empty dashboard: normal on first use; add records with the form or Postman.
- A dependency error: install requirements using the same virtual-environment Python used to run the app.

See `docs/VERIFICATION.md` for the checks actually performed on this package.
