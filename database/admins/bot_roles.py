import sqlite3
from database.connection import get_connection

insert_role_query = """
    INSERT INTO bot_roles(user_id, role, granted_by)
    VALUES(?, ?, ?)
"""

fetch_all_roles_query = """
    SELECT user_id, role, granted_by, granted_at
    FROM bot_roles
    ORDER BY granted_at DESC
"""

fetch_user_roles_query = """
    SELECT role FROM bot_roles
    WHERE user_id = ?
"""

check_role_query = """
    SELECT 1 FROM bot_roles
    WHERE user_id = ? AND role = ?
"""

update_role_query = """
    UPDATE bot_roles
    SET role = ?, granted_by = ?, granted_at = CURRENT_TIMESTAMP
    WHERE user_id = ? AND role = ?
"""

delete_role_query = """
    DELETE FROM bot_roles
    WHERE user_id = ? AND role = ?
"""


def assign_role(user_id, role, granted_by):
    if role not in ("admin", "moderator"):
        return False, "Invalid role."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(insert_role_query, (user_id, role, granted_by))
        conn.commit()
        return True, "Role assigned successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def fetch_all_roles():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_all_roles_query)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def fetch_user_roles(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_user_roles_query, (user_id,))
        return [row[0] for row in cursor.fetchall()]

    finally:
        cursor.close()
        conn.close()


def has_role(user_id, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(check_role_query, (user_id, role))
        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def change_role(user_id, old_role, new_role, granted_by):
    if new_role not in ("admin", "moderator"):
        return False, "Invalid role."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            update_role_query,
            (new_role, granted_by, user_id, old_role)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Role not found."

        return True, "Role changed successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def remove_role(user_id, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(delete_role_query, (user_id, role))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Role not found."

        return True, "Role removed successfully."

    finally:
        cursor.close()
        conn.close()
