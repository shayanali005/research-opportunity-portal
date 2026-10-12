"""Application factory for Research Atlas."""
import os
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from . import storage
from .validation import validate, ALL_FIELDS

ROOT = Path(__file__).resolve().parents[1]

def create_app(config=None):
    load_dotenv(ROOT / '.env')
    app = Flask(__name__, static_folder=str(ROOT / 'web'), static_url_path='')
    app.config.update(MAX_CONTENT_LENGTH=128 * 1024, DATABASE={
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'atlas_app'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'research_atlas'),
        'charset': 'utf8mb4', 'connection_timeout': 5,
    })
    if config:
        app.config.update(config)

    @app.get('/')
    def home():
        return app.send_static_file('index.html')

    @app.errorhandler(mysql.connector.Error)
    def database_error(error):
        app.logger.error('Database operation failed (%s)', type(error).__name__)
        return jsonify(error='Database unavailable. Check the server database configuration.'), 500

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.error('Unexpected server error (%s)', type(error).__name__)
        return jsonify(error='An unexpected server error occurred.'), 500

    @app.get('/api/opportunities')
    def list_opportunities():
        status = request.args.get('status', '')
        if status not in ('', 'Open', 'Closed'):
            return jsonify(error='Status must be Open or Closed.'), 400
        with storage.database() as cursor:
            rows = storage.listing(cursor, request.args.get('q', '').strip(), status)
        return jsonify(data=rows, count=len(rows))

    @app.get('/api/opportunities/<int:identifier>')
    def get_opportunity(identifier):
        with storage.database() as cursor:
            row = storage.find(cursor, identifier)
        if row is None:
            return jsonify(error='Opportunity not found.'), 404
        return jsonify(data=row)

    def parse_body():
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not body:
            return None, (jsonify(error='Send a non-empty JSON object.'), 400)
        unknown = set(body) - set(ALL_FIELDS)
        if unknown:
            return None, (jsonify(error='Unknown fields.', details=sorted(unknown)), 400)
        return body, None

    @app.post('/api/opportunities')
    def post_opportunity():
        body, error = parse_body()
        if error is not None:
            return error
        clean, errors = validate(body)
        if errors:
            return jsonify(error='Please correct the submitted fields.', details=errors), 400
        with storage.database() as cursor:
            row = storage.create(cursor, clean)
        return jsonify(data=row, message='Opportunity published.'), 201, {'Location': '/api/opportunities/' + str(row['id'])}

    @app.put('/api/opportunities/<int:identifier>')
    def put_opportunity(identifier):
        body, error = parse_body()
        if error is not None:
            return error
        with storage.database() as cursor:
            existing = storage.find(cursor, identifier, lock=True)
            if existing is None:
                return jsonify(error='Opportunity not found.'), 404
            clean, errors = validate({**existing, **body})
            if errors:
                return jsonify(error='Please correct the submitted fields.', details=errors), 400
            row = storage.update(cursor, identifier, clean)
        return jsonify(data=row, message='Changes saved.')

    @app.delete('/api/opportunities/<int:identifier>')
    def delete_opportunity(identifier):
        with storage.database() as cursor:
            cursor.execute('DELETE FROM opportunities WHERE id = %s', (identifier,))
            if cursor.rowcount == 0:
                return jsonify(error='Opportunity not found.'), 404
        return jsonify(message='Opportunity deleted.', data={'id': identifier})

    return app
