
from psycopg import Error, errors

from database.postgres_connection import get_postgres_connection


user_fetch_query = """
    SELECT
        user_id,
        username,
        first_name,
        created_at,
        last_seen_at,
        is_banned
    FROM users
    ORDER BY created_at DESC
"""

user_fetch_by_id = """
    SELECT
        user_id,
        username,
        first_name,
        last_seen_at,
        is_banned
    FROM users
    WHERE user_id = %s
"""

user_profile_update_query = """
    UPDATE users
    SET username = %s,
        first_name = %s
    WHERE user_id = %s
"""

delete_user_query = """
    DELETE FROM users
    WHERE user_id = %s
"""


def find_user_by_username(username):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, username, first_name, is_banned
                FROM users
                WHERE username = %s
                """,
                (username,)
            )
            return cursor.fetchone()

    except Error as error:
        print("Error finding user:", error)
        return None

    finally:
        conn.close()


def unban_user(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET is_banned = 0
                WHERE user_id = %s AND is_banned = 1
                """,
                (user_id,)
            )

            success = cursor.rowcount > 0

        conn.commit()
        return success

    except Error as error:
        conn.rollback()
        print("Error unbanning user:", error)
        return False

    finally:
        conn.close()


def ensure_owner_admin(owner_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:

            # Register the owner only if they do not already exist.
            cursor.execute(
                """
                INSERT INTO users (user_id, first_name)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO NOTHING
                """,
                (owner_id, "Bot Owner")
            )

            # Ensure the owner has the admin role.
            cursor.execute(
                """
                INSERT INTO bot_roles (user_id, role)
                VALUES (%s, %s)
                ON CONFLICT (user_id, role) DO NOTHING
                """,
                (owner_id, "admin")
            )

        conn.commit()
        return True

    except Error:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_user_roles(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT role
                FROM bot_roles
                WHERE user_id = %s
                """,
                (user_id,)
            )
            return cursor.fetchall()

    except Error as error:
        print("Error fetching user roles:", error)
        return []

    finally:
        conn.close()


def assign_role(user_id, role, granted_by):
    if role not in ("admin", "moderator"):
        return False

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO bot_roles (user_id, role, granted_by)
                VALUES (%s, %s, %s)
                """,
                (user_id, role, granted_by)
            )

        conn.commit()
        return True

    except errors.UniqueViolation:
        conn.rollback()
        return False

    except Error as error:
        conn.rollback()
        print("Error assigning role:", error)
        return False

    finally:
        conn.close()


def remove_role(user_id, role):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM bot_roles
                WHERE user_id = %s AND role = %s
                """,
                (user_id, role)
            )

            removed = cursor.rowcount > 0

        conn.commit()
        return removed

    except Error as error:
        conn.rollback()
        print("Error removing role:", error)
        return False

    finally:
        conn.close()


def ban_user(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET is_banned = 1
                WHERE user_id = %s AND is_banned = 0
                """,
                (user_id,)
            )

            updated = cursor.rowcount > 0

        conn.commit()
        return updated

    except Error as error:
        conn.rollback()
        print("Error banning user:", error)
        return False

    finally:
        conn.close()


def fetch_banned_users():
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, username, first_name
                FROM users
                WHERE is_banned = 1
                ORDER BY first_name
                """
            )
            return cursor.fetchall()

    except Error as error:
        print("Error fetching banned users:", error)
        return []

    finally:
        conn.close()


def fetch_users_data():
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(user_fetch_query)
            return cursor.fetchall()

    finally:
        conn.close()


def fetch_specific_user_data(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(user_fetch_by_id, (user_id,))
            return cursor.fetchone()

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

    except Error:
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

    except Error:
        conn.rollback()
        raise

    finally:
        conn.close()
