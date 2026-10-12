"""MySQL persistence. Each request owns its connection and transaction."""
from contextlib import contextmanager
import mysql.connector
from flask import current_app
from .validation import ALL_FIELDS, to_json

@contextmanager
def database():
    connection = mysql.connector.connect(**current_app.config['DATABASE'])
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

def find(cursor, identifier, lock=False):
    cursor.execute('SELECT * FROM opportunities WHERE id = %s' + (' FOR UPDATE' if lock else ''), (identifier,))
    return to_json(cursor.fetchone())

def listing(cursor, search='', status=''):
    conditions, values = [], []
    if search:
        conditions.append('(research_title LIKE %s OR research_area LIKE %s OR faculty_name LIKE %s OR department LIKE %s)')
        values.extend(['%' + search + '%'] * 4)
    if status:
        conditions.append('status = %s')
        values.append(status)
    sql = 'SELECT * FROM opportunities'
    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)
    cursor.execute(sql + ' ORDER BY application_deadline ASC, id DESC', tuple(values))
    return [to_json(row) for row in cursor.fetchall()]

def create(cursor, data):
    columns = ', '.join(ALL_FIELDS)
    placeholders = ', '.join(['%s'] * len(ALL_FIELDS))
    cursor.execute(f'INSERT INTO opportunities ({columns}) VALUES ({placeholders})', tuple(data[key] for key in ALL_FIELDS))
    return find(cursor, cursor.lastrowid)

def update(cursor, identifier, data):
    assignments = ', '.join(key + ' = %s' for key in ALL_FIELDS)
    cursor.execute(f'UPDATE opportunities SET {assignments} WHERE id = %s', tuple(data[key] for key in ALL_FIELDS) + (identifier,))
    return find(cursor, identifier)
