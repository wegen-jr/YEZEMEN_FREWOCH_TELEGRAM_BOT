
import sqlite3
from pathlib import Path


from database.connection import get_connection



def fetch_published_works():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content_id, title
            FROM contents
            WHERE is_published = 1
            ORDER BY published_at DESC, content_id DESC
        """, )

        return cursor.fetchall()

    finally:
        conn.close()


def fetch_published_works_to_sync():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content_id, title,body,author_name,content_type,category
            FROM contents
            WHERE is_published = 1
            ORDER BY published_at DESC, content_id DESC
        """,)

        return cursor.fetchall()

    finally:
        conn.close()

def search_published_works(keyword, limit=10):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content_id, title
            FROM contents
            WHERE is_published = 1
              AND (title LIKE ? OR author_name LIKE ?)
            ORDER BY published_at DESC, content_id DESC
            LIMIT ?
        """, (f"%{keyword}%", f"%{keyword}%", limit))

        return cursor.fetchall()

    finally:
        conn.close()


def fetch_published_work(content_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content_id, title, body, content_type,
                   author_name, source, category, published_at
            FROM contents
            WHERE content_id = ? AND is_published = 1
        """, (content_id,))

        return cursor.fetchone()

    finally:
        conn.close()


def update_published_work(content_id, title, body):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contents
            SET title = ?, body = ?
            WHERE content_id = ? AND is_published = 1
        """, (title, body, content_id))

        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.IntegrityError:
        conn.rollback()
        return False

    finally:
        conn.close()


def unpublish_work(content_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contents
            SET is_published = 0
            WHERE content_id = ? AND is_published = 1
        """, (content_id,))

        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()


def delete_published_work(content_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM contents
            WHERE content_id = ? AND is_published = 1
        """, (content_id,))

        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()


def fetch_unpublished_works(limit=10):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content_id, title
            FROM contents
            WHERE is_published = 0
            ORDER BY content_id DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

    finally:
        conn.close()


def fetch_unpublished_work(content_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content_id, title, body, content_type,
                   author_name, source, category, published_at
            FROM contents
            WHERE content_id = ? AND is_published = 0
        """, (content_id,))

        return cursor.fetchone()

    finally:
        conn.close()


def republish_work(content_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contents
            SET is_published = 1,
                published_at = CURRENT_TIMESTAMP
            WHERE content_id = ? AND is_published = 0
              AND status = 'approved'
        """, (content_id,))

        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()


def delete_unpublished_work(content_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM contents
            WHERE content_id = ? AND is_published = 0
        """, (content_id,))

        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()
