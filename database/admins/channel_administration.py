
from psycopg import Error, errors

from database.postgres_connection import get_postgres_connection


def fetch_publication(content_id, channel_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM channel_publications
                WHERE content_id = %s
                  AND channel_id = %s
                """,
                (content_id, channel_id)
            )
            return cursor.fetchone()

    except Error as error:
        print("Error fetching publication:", error)
        return None

    finally:
        if conn is not None:
            conn.close()


def fetch_all_publications(channel_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM channel_publications
                WHERE channel_id = %s
                ORDER BY posted_at DESC NULLS LAST
                """,
                (channel_id,)
            )
            return cursor.fetchall()

    except Error as error:
        print("Error fetching channel publications:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def create_publication(content_id, channel_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO channel_publications (
                    content_id,
                    channel_id,
                    status
                )
                VALUES (%s, %s, 'pending')
                RETURNING publication_id
                """,
                (content_id, channel_id)
            )

            publication_id = cursor.fetchone()[0]

        conn.commit()
        return True, publication_id

    except errors.UniqueViolation as error:
        if conn is not None:
            conn.rollback()

        return False, str(error)

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error creating publication:", error)
        return False, str(error)

    finally:
        if conn is not None:
            conn.close()


def update_publication(
    publication_id,
    message_id,
    status,
    content_hash,
    last_error=None
):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE channel_publications
                SET message_id = %s,
                    status = %s,
                    content_hash = %s,
                    last_error = %s,
                    posted_at = CASE
                        WHEN %s = 'posted' AND posted_at IS NULL
                        THEN CURRENT_TIMESTAMP
                        ELSE posted_at
                    END,
                    last_synced_at = CURRENT_TIMESTAMP
                WHERE publication_id = %s
                """,
                (
                    message_id,
                    status,
                    content_hash,
                    last_error,
                    status,
                    publication_id
                )
            )

            updated = cursor.rowcount > 0

        conn.commit()
        return updated

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error updating publication:", error)
        return False

    finally:
        if conn is not None:
            conn.close()


def delete_publication(content_id, channel_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM channel_publications
                WHERE content_id = %s
                  AND channel_id = %s
                """,
                (content_id, channel_id)
            )

            deleted = cursor.rowcount > 0

        conn.commit()
        return deleted

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error deleting publication:", error)
        return False

    finally:
        if conn is not None:
            conn.close()


def fetch_pending_publications(channel_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM channel_publications
                WHERE channel_id = %s
                  AND status IN ('pending', 'failed')
                ORDER BY publication_id ASC
                """,
                (channel_id,)
            )
            return cursor.fetchall()

    except Error as error:
        print("Error fetching pending publications:", error)
        return []

    finally:
        if conn is not None:
            conn.close()
