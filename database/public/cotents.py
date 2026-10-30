import sqlite3
from database.connection import get_connection

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
    VALUES (?, ?, ?, ?, ?, ?, ?)
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
    FROM contents WHERE status=? is_published=?
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
    WHERE category = ?
      AND content_type = ? AND status=? AND is_published=?
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
    WHERE author_name = ? AND status=? AND is_published=?
"""

update_content_query = """
    UPDATE contents
    SET
        title = ?,
        body = ?,
        content_type = ?,
        author_name = ?,
        source = ?,
        category = ?
    WHERE content_id = ?
"""

delete_content_query = """
    DELETE FROM contents
    WHERE content_id = ?
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
        submitted_by,
    )

    conn = get_connection()
    cursor = conn.cursor()
    try:
        
        cursor.execute(insert_content_query, data)
        conn.commit()

        return  "✅ Content inserted successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()

        if "UNIQUE constraint failed" in str(error):
            return False, "Content with this title and body already exists."

        return "register first by /start, before sharing your work."

    finally:
        cursor.close()
        conn.close()



def fetch_all_contents():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_contents_query,("approved",1))
        data= cursor.fetchall()
        return data

    finally:
        cursor.close()
        conn.close()

def fetch_by_category(category, content_type):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            fetch_content_by_category_query,
            (category, content_type,"approved",1)
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def fetch_by_author(author_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            fetch_content_by_author_query,
            (author_name,1)
        )
        return cursor.fetchall()

    finally:
        cursor.close()
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

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(update_content_query, data)

        if cursor.rowcount == 0:
            conn.rollback()
            return False, "Content not found."

        conn.commit()
        return True, "Content updated successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()

        if "UNIQUE constraint failed" in str(error):
            return False, "Another content item already has this title and body."

        return False, f"Database constraint error: {error}"

    finally:
        cursor.close()
        conn.close()


def delete_content(content_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(delete_content_query, (content_id,))

        if cursor.rowcount == 0:
            conn.rollback()
            return False, "Content not found."

        conn.commit()
        return True, "Content deleted successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, f"Could not delete content: {error}"

    finally:
        cursor.close()
        conn.close()
