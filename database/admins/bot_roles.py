
import psycopg
from database.postgres_connection import get_postgres_connection


insert_role_query = """
    INSERT INTO bot_roles (user_id, role, granted_by)
    VALUES (%s, %s, %s)
"""

fetch_all_roles_query = """
    SELECT user_id, role, granted_by, granted_at
    FROM bot_roles
    ORDER BY granted_at DESC
"""

fetch_user_roles_query = """
    SELECT role
    FROM bot_roles
    WHERE user_id = %s
"""

check_role_query = """
    SELECT 1
    FROM bot_roles
    WHERE user_id = %s AND role = %s
"""

update_role_query = """
    UPDATE bot_roles
    SET role = %s,
        granted_by = %s,
        granted_at = CURRENT_TIMESTAMP
    WHERE user_id = %s AND role = %s
"""

delete_role_query = """
    DELETE FROM bot_roles
    WHERE user_id = %s AND role = %s
"""


def assign_role(user_id, role, granted_by):
    if role not in ("admin", "moderator"):
        return False, "Invalid role."

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_role_query,
                (user_id, role, granted_by)
            )

        conn.commit()
        return True, "Role assigned successfully."

    except psycopg.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def fetch_all_roles():
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(fetch_all_roles_query)
            return cursor.fetchall()

    finally:
        conn.close()


def fetch_user_roles(user_id):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(fetch_user_roles_query, (user_id,))
            return [row[0] for row in cursor.fetchall()]

    finally:
        conn.close()


def has_role(user_id, role):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(check_role_query, (user_id, role))
            return cursor.fetchone() is not None

    finally:
        conn.close()


def change_role(user_id, old_role, new_role, granted_by):
    if new_role not in ("admin", "moderator"):
        return False, "Invalid role."

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                update_role_query,
                (new_role, granted_by, user_id, old_role)
            )

            if cursor.rowcount == 0:
                conn.rollback()
                return False, "Role not found."

        conn.commit()
        return True, "Role changed successfully."

    except psycopg.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def remove_role(user_id, role):
    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(delete_role_query, (user_id, role))

            if cursor.rowcount == 0:
                conn.rollback()
                return False, "Role not found."

        conn.commit()
        return True, "Role removed successfully."

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
