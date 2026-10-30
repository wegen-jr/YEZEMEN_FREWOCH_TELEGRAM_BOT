
import sqlite3
from database.connection import get_connection


insert_group_query = """
    INSERT INTO groups(
        group_id, group_title, welcome_enabled,
        rules_text, moderation_enabled
    )
    VALUES(?, ?, ?, ?, ?)
"""

fetch_all_groups_query = """
    SELECT * FROM groups
    ORDER BY added_at DESC
"""

fetch_group_by_id_query = """
    SELECT * FROM groups
    WHERE group_id = ?
"""

update_group_query = """
    UPDATE groups
    SET group_title = ?,
        welcome_enabled = ?,
        rules_text = ?,
        moderation_enabled = ?
    WHERE group_id = ?
"""

delete_group_query = """
    DELETE FROM groups
    WHERE group_id = ?
"""


def register_group(
    group_id, group_title,
    welcome_enabled=1, rules_text=None, moderation_enabled=1
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            insert_group_query,
            (
                group_id, group_title, welcome_enabled,
                rules_text, moderation_enabled
            )
        )
        conn.commit()
        return True, "Group registered successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def fetch_all_groups():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_all_groups_query)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def fetch_group_by_id(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_group_by_id_query, (group_id,))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def update_group(
    group_id, group_title,
    welcome_enabled, rules_text, moderation_enabled
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            update_group_query,
            (
                group_title, welcome_enabled, rules_text,
                moderation_enabled, group_id
            )
        )
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Group not found."

        return True, "Group settings updated successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def delete_group(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(delete_group_query, (group_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Group not found."

        return True, "Group registration deleted successfully."

    finally:
        cursor.close()
        conn.close()
