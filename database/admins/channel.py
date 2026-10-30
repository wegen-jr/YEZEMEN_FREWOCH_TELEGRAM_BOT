
from psycopg import Error
from database.postgres_connection import get_postgres_connection


def fetch_channel_statistics(channel_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(*) FILTER (WHERE status = 'posted'),
                    COUNT(*) FILTER (WHERE status = 'pending'),
                    COUNT(*) FILTER (WHERE status = 'failed'),
                    COUNT(*) FILTER (WHERE status = 'removed')
                FROM channel_publications
                WHERE channel_id = %s
                """,
                (str(channel_id),)
            )

            publication_stats = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM contents
                WHERE is_published = 1
                """
            )

            published_count = cursor.fetchone()[0]

            return {
                "total": publication_stats[0] or 0,
                "posted": publication_stats[1] or 0,
                "published": published_count or 0,
                "pending": publication_stats[2] or 0,
                "failed": publication_stats[3] or 0,
                "removed": publication_stats[4] or 0
            }

    except Error as error:
        print("Error fetching channel statistics:", error)
        raise

    finally:
        if conn is not None:
            conn.close()
