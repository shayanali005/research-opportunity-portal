# Verification report

Date: 2026-10-11

## Passed

- 36 API checks using the Flask test client with a SQLite-backed adapter for MySQL cursor operations. This exercises route validation and SQL CRUD logic, but does not verify MySQL-specific behavior.
- Browser automation in Chrome: desktop rendering, search, status filter, create, edit, close, delete confirmation, required-field validation, text escaping, mobile overflow, no JavaScript exceptions.
- Desktop (1440 px) and mobile (390 px) screenshots visually reviewed.

## Limits

An isolated MySQL 8.4 instance initialized and started, but client connections timed out in this execution environment. Live MySQL integration and the actual Postman runner have NOT been verified. Run the supplied Postman collection against your local MySQL setup before submission. Browser checks used intercepted API fixtures; the production frontend loads records only through the real REST API.

The preview images contain test fixtures, not preloaded application records.

## Checks

- Create 0
- Create 1
- Create 2
- List
- Get one
- Date
- Update
- Close
- Filter
- Search
- SQL injection search treated as data
- Invalid filter
- Reject empty
- Reject array
- Reject zero
- Reject boolean
- Reject fraction
- Reject bad date
- Reject whitespace
- Reject long title
- Reject unknown
- Reject unicode oversized description
- Description byte limit
- Malformed JSON
- Invalid update
- Preserve data
- Delete
- Deleted 404
- Delete 404
- Update 404
- Static /
- Static /atlas.css
- Static /atlas.js
- Unknown route
- Database 500
- Error redacted
