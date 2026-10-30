
from database.postgres_connection import get_postgres_connection


insert_favourite_query = """
    INSERT INTO favourite (user_id, content_id)
    VALUES (%s, %s)
    ON CONFLICT (user_id, content_id) DO NOTHING
"""

fetch_favourite_query = """
    SELECT
        c.content_id,
        c.content_type,
        c.title,
        c.body,
        c.author_name,
        c.source,
        c.category,
        c.status,
        c.is_published,
        f.saved_at
    FROM favourite AS f
    JOIN contents AS c
        ON f.content_id = c.content_id
    WHERE f.user_id = %s
      AND c.content_type = %s
      AND c.status = %s
      AND c.is_published = %s
    ORDER BY f.saved_at DESC
"""

fetch_all_favourite_query = """
    SELECT
        c.content_id,
        c.title,
        c.body,
        c.author_name,
        c.source,
        c.category,
        c.status,
        c.is_published,
        f.saved_at
    FROM favourite AS f
    JOIN contents AS c
        ON f.content_id = c.content_id
    WHERE f.user_id = %s
      AND c.status = %s
      AND c.is_published = %s
    ORDER BY f.saved_at DESC
"""

is_favourite_query = """
    SELECT *
    FROM favourite
    WHERE content_id = %s
      AND user_id = %s
"""

delete_favourite_query = """
    DELETE FROM favourite
    WHERE content_id = %s
      AND user_id = %s
"""


def create_favourite(user_id, content_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_favourite_query,
                (user_id, content_id)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def fetch_favourite(user_id, content_type):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                fetch_favourite_query,
                (user_id, content_type, "approved", 1)
            )

            return cursor.fetchall()

    finally:
        conn.close()


def fetch_all_favourites(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                fetch_all_favourite_query,
                (user_id, "approved", 1)
            )

            return cursor.fetchall()

    finally:
        conn.close()


def is_favourite(content_id, user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                is_favourite_query,
                (content_id, user_id)
            )

            return cursor.fetchall()

    finally:
        conn.close()


def delete_favourite(content_id, user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                delete_favourite_query,
                (content_id, user_id)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
