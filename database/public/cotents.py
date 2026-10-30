
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
        submitted_by
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

fetch_contents_query = """
    SELECT
        content_id,
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        status,
        is_published
    FROM contents
    WHERE status = %s
      AND is_published = %s
"""

fetch_content_by_category_query = """
    SELECT
        content_id,
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        status,
        is_published
    FROM contents
    WHERE category = %s
      AND content_type = %s
      AND status = %s
      AND is_published = %s
"""

fetch_content_by_author_query = """
    SELECT
        content_id,
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        status,
        is_published
    FROM contents
    WHERE author_name = %s
      AND status = %s
      AND is_published = %s
"""

update_content_query = """
    UPDATE contents
    SET
        title = %s,
        body = %s,
        content_type = %s,
        author_name = %s,
        source = %s,
        category = %s
    WHERE content_id = %s
"""

delete_content_query = """
    DELETE FROM contents
    WHERE content_id = %s
"""


def create_content(
    title,
    body,
    content_type,
    author_name,
    source,
    category,
    submitted_by
):
    data = (
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        submitted_by
    )

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_content_query, data)

        conn.commit()
        return True, "✅ Content submitted successfully."

    except errors.UniqueViolation:
        conn.rollback()
        return False, "Content with this title and body already exists."

    except errors.ForeignKeyViolation:
        conn.rollback()
        return False, "Please register first by using /start."

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def fetch_all_contents():
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(fetch_contents_query, ("approved", 1))
            data = cursor.fetchall()

        return data

    finally:
        conn.close()


def fetch_by_category(category, content_type):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                fetch_content_by_category_query,
                (category, content_type, "approved", 1)
            )

            return cursor.fetchall()

    finally:
        conn.close()


def fetch_by_author(author_name):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                fetch_content_by_author_query,
                (author_name, "approved", 1)
            )

            return cursor.fetchall()

    finally:
        conn.close()


def update_content(
    title,
    body,
    content_type,
    author_name,
    source,
    category,
    content_id
):
    data = (
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        content_id
    )

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(update_content_query, data)

            if cursor.rowcount == 0:
                conn.rollback()
                return False, "Content not found."

        conn.commit()
        return True, "Content updated successfully."

    except errors.UniqueViolation:
        conn.rollback()
        return False, "Another content item already has this title and body."

    except Exception as error:
        conn.rollback()
        return False, f"Database error: {error}"

    finally:
        conn.close()


def delete_content(content_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(delete_content_query, (content_id,))

            if cursor.rowcount == 0:
                conn.rollback()
                return False, "Content not found."

        conn.commit()
        return True, "Content deleted successfully."

    except Exception as error:
        conn.rollback()
        return False, f"Could not delete content: {error}"

    finally:
        conn.close()
