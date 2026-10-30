
from psycopg import Error
from database.postgres_connection import get_postgres_connection


def fetch_published_works():
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT content_id, title
                FROM contents
                WHERE is_published = 1
                ORDER BY published_at DESC NULLS LAST, content_id DESC
            """)

            return cursor.fetchall()

    except Error as error:
        print("Error fetching published works:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def fetch_published_works_to_sync():
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT content_id, title, body, author_name,
                       content_type, category
                FROM contents
                WHERE is_published = 1
                ORDER BY published_at DESC NULLS LAST, content_id DESC
            """)

            return cursor.fetchall()

    except Error as error:
        print("Error fetching published works for sync:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def search_published_works(keyword, limit=10):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT content_id, title
                FROM contents
                WHERE is_published = 1
                  AND (
                      title ILIKE %s
                      OR author_name ILIKE %s
                  )
                ORDER BY published_at DESC NULLS LAST, content_id DESC
                LIMIT %s
            """, (f"%{keyword}%", f"%{keyword}%", limit))

            return cursor.fetchall()

    except Error as error:
        print("Error searching published works:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def fetch_published_work(content_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT content_id, title, body, content_type,
                       author_name, source, category, published_at
                FROM contents
                WHERE content_id = %s
                  AND is_published = 1
            """, (content_id,))

            return cursor.fetchone()

    except Error as error:
        print("Error fetching published work:", error)
        return None

    finally:
        if conn is not None:
            conn.close()


def update_published_work(content_id, title, body):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE contents
                SET title = %s,
                    body = %s
                WHERE content_id = %s
                  AND is_published = 1
            """, (title, body, content_id))

            updated = cursor.rowcount > 0

        conn.commit()
        return updated

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error updating published work:", error)
        return False

    finally:
        if conn is not None:
            conn.close()


def unpublish_work(content_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE contents
                SET is_published = 0
                WHERE content_id = %s
                  AND is_published = 1
            """, (content_id,))

            updated = cursor.rowcount > 0

        conn.commit()
        return updated

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error unpublishing work:", error)
        return False

    finally:
        if conn is not None:
            conn.close()


def delete_published_work(content_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM contents
                WHERE content_id = %s
                  AND is_published = 1
            """, (content_id,))

            deleted = cursor.rowcount > 0

        conn.commit()
        return deleted

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error deleting published work:", error)
        return False

    finally:
        if conn is not None:
            conn.close()


def fetch_unpublished_works(limit=10):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT content_id, title
                FROM contents
                WHERE is_published = 0
                ORDER BY content_id DESC
                LIMIT %s
            """, (limit,))

            return cursor.fetchall()

    except Error as error:
        print("Error fetching unpublished works:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def fetch_unpublished_work(content_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT content_id, title, body, content_type,
                       author_name, source, category, published_at
                FROM contents
                WHERE content_id = %s
                  AND is_published = 0
            """, (content_id,))

            return cursor.fetchone()

    except Error as error:
        print("Error fetching unpublished work:", error)
        return None

    finally:
        if conn is not None:
            conn.close()


def republish_work(content_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE contents
                SET is_published = 1,
                    published_at = CURRENT_TIMESTAMP
                WHERE content_id = %s
                  AND is_published = 0
                  AND status = 'approved'
            """, (content_id,))

            updated = cursor.rowcount > 0

        conn.commit()
        return updated

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error republishing work:", error)
        return False

    finally:
        if conn is not None:
            conn.close()


def delete_unpublished_work(content_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM contents
                WHERE content_id = %s
                  AND is_published = 0
            """, (content_id,))

            deleted = cursor.rowcount > 0

        conn.commit()
        return deleted

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error deleting unpublished work:", error)
        return False

    finally:
        if conn is not None:
            conn.close()
