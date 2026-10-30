
import sqlite3
from database.connection import get_connection


# 1. Fetch one publication record
fetch_publication_query = """
    SELECT *
    FROM channel_publications
    WHERE content_id = ? AND channel_id = ?
"""


# 2. Fetch all publication records for a channel
fetch_all_publications_query = """
    SELECT *
    FROM channel_publications
    WHERE channel_id = ?
    ORDER BY posted_at DESC
"""


# 3. Create a publication tracking record
create_publication_query = """
    INSERT INTO channel_publications (
        content_id, channel_id, status
    )
    VALUES (?, ?, 'pending')
"""


# 4. Update a publication record
update_publication_query = """
    UPDATE channel_publications
    SET
        message_id = ?,
        status = ?,
        content_hash = ?,
        last_error = ?,
        posted_at = CASE
            WHEN ? = 'posted' AND posted_at IS NULL
            THEN CURRENT_TIMESTAMP
            ELSE posted_at
        END,
        last_synced_at = CURRENT_TIMESTAMP
    WHERE publication_id = ?
"""


# 5. Delete a publication tracking record
delete_publication_query = """
    DELETE FROM channel_publications
    WHERE content_id = ? AND channel_id = ?
"""


# 6. Fetch records requiring synchronization
fetch_pending_publications_query = """
    SELECT *
    FROM channel_publications
    WHERE channel_id = ?
    AND status IN ('pending', 'failed')
    ORDER BY publication_id ASC
"""


def fetch_publication(content_id, channel_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            fetch_publication_query,
            (content_id, channel_id)
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def fetch_all_publications(channel_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            fetch_all_publications_query,
            (channel_id,)
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def create_publication(content_id, channel_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            create_publication_query,
            (content_id, channel_id)
        )

        conn.commit()

        return True, cursor.lastrowid

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def update_publication(
    publication_id,
    message_id,
    status,
    content_hash,
    last_error=None
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            update_publication_query,
            (
                message_id,
                status,
                content_hash,
                last_error,
                status,
                publication_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def delete_publication(content_id, channel_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            delete_publication_query,
            (content_id, channel_id)
        )

        conn.commit()

        return cursor.rowcount > 0

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def fetch_pending_publications(channel_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            fetch_pending_publications_query,
            (channel_id,)
        )
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
