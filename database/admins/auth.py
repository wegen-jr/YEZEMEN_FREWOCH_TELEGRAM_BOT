
from psycopg import Error
from database.postgres_connection import get_postgres_connection


check_role_query = """
    SELECT 1
    FROM bot_roles
    WHERE user_id = %s
      AND role IN ('admin', 'moderator')
"""


def check_role(user_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(check_role_query, (user_id,))
            data = cursor.fetchone()

        return data is not None

    except Error as error:
        print("Error checking admin access:", error)
        return False

    finally:
        if conn is not None:
            conn.close()
