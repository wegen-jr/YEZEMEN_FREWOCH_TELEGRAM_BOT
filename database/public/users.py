
from database.postgres_connection import get_postgres_connection


user_insert_query = """
    INSERT INTO users (
        user_id, username, first_name, last_seen_at
    )
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET
        username = EXCLUDED.username,
        first_name = EXCLUDED.first_name,
        last_seen_at = EXCLUDED.last_seen_at
"""

user_fetch_query = """
    SELECT * FROM users
"""

user_fetch_by_id = """
    SELECT username, first_name, last_seen_at, is_banned
    FROM users
    WHERE user_id = %s
"""

user_profile_update_query = """
    UPDATE users
    SET username = %s, first_name = %s
    WHERE user_id = %s
"""

delete_user_query = """
    DELETE FROM users
    WHERE user_id = %s
"""


def is_user_banned(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT is_banned FROM users WHERE user_id = %s",
                (user_id,)
            )

            result = cursor.fetchone()

        return bool(result and result[0])

    finally:
        conn.close()


def create_or_update_user(user_id, username, first_name, last_seen_at):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                user_insert_query,
                (user_id, username, first_name, last_seen_at)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def fetch_users_data():
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(user_fetch_query)
            data = cursor.fetchall()

        return data

    finally:
        conn.close()


def fetch_specific_user_data(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(user_fetch_by_id, (user_id,))
            data = cursor.fetchone()

        return data

    finally:
        conn.close()


def update_profile(user_id, username, first_name):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                user_profile_update_query,
                (username, first_name, user_id)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_user(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(delete_user_query, (user_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
