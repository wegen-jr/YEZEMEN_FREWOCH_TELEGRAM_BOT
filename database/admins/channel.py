
from database.connection import get_connection


def fetch_channel_statistics(channel_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*),
                SUM(CASE WHEN status = 'posted' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'removed' THEN 1 ELSE 0 END)
            FROM channel_publications
            WHERE channel_id = ?
        """, (str(channel_id),))

        result = cursor.fetchone()

        return {
            "total": result[0] or 0,
            "posted": result[1] or 0,
            "pending": result[2] or 0,
            "failed": result[3] or 0,
            "removed": result[4] or 0
        }

    finally:
        conn.close()
