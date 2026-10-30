
from datetime import datetime

from psycopg import errors
from database.postgres_connection import get_postgres_connection


insert_content_query = """
    INSERT INTO contents (
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        submitted_by,
        is_published,
        status,
        published_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

is_admin_query = """
    SELECT user_id
    FROM bot_roles
    WHERE user_id = %s
"""

# Keep this column order aligned with the submission handler.
fetch_pending_contents_query = """
    SELECT
        content_id,
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        status
    FROM contents
    WHERE status = %s
"""

fetch_contents_by_id_query = """
    SELECT
        content_id,
        title,
        body,
        author_name,
        source,
        category
    FROM contents
    WHERE content_id = %s
"""

update_status_query = """
    UPDATE contents
    SET status = %s,
        approved_by = %s,
        is_published = %s,
        published_at = %s
    WHERE content_id = %s
"""


def fetch_pendings(status):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(fetch_pending_contents_query, (status,))
            return cursor.fetchall()

    finally:
        conn.close()


def fetch_contents_by_id(content_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(fetch_contents_by_id_query, (content_id,))
            return cursor.fetchone()

    finally:
        conn.close()


def is_admin(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(is_admin_query, (user_id,))
            return cursor.fetchone()

    finally:
        conn.close()


def create_content(
    title,
    body,
    content_type,
    author_name,
    source,
    category,
    submitted_by
):
    is_it_admin = is_admin(submitted_by)

    if is_it_admin is None:
        return False, "You do not have permission to publish content."

    is_published = 1
    status = "approved"
    published_at = datetime.now()

    data = (
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        submitted_by,
        is_published,
        status,
        published_at
    )

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_content_query, data)

        conn.commit()
        return True, "✅ Content inserted successfully."

    except errors.UniqueViolation:
        conn.rollback()
        return False, "Content with this title and body already exists."

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def update_status(
    status,
    approved_by,
    is_published,
    published_at,
    content_id
):
    if not is_published:
        published_at = None

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                update_status_query,
                (
                    status,
                    approved_by,
                    is_published,
                    published_at,
                    content_id
                )
            )

            updated = cursor.rowcount > 0

        conn.commit()

        if updated:
            return True, "Status updated successfully."

        return False, "Content not found."

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
