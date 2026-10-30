
import sqlite3
from database.connection import get_connection


insert_log_query = """
    INSERT INTO moderation_logs(
        group_id, moderator_id, target_user_id,
        action, reason, message_id
    )
    VALUES(?, ?, ?, ?, ?, ?)
"""

fetch_all_logs_query = """
    SELECT * FROM moderation_logs
    ORDER BY created_at DESC
"""

fetch_group_logs_query = """
    SELECT * FROM moderation_logs
    WHERE group_id = ?
    ORDER BY created_at DESC
"""

fetch_user_logs_query = """
    SELECT * FROM moderation_logs
    WHERE target_user_id = ?
    ORDER BY created_at DESC
"""

fetch_moderator_logs_query = """
    SELECT * FROM moderation_logs
    WHERE moderator_id = ?
    ORDER BY created_at DESC
"""


def record_moderation_action(
    group_id, moderator_id, target_user_id,
    action, reason=None, message_id=None
):
    allowed_actions = ("warn", "ban", "unban", "delete_message")

    if action not in allowed_actions:
        return False, "Invalid moderation action."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            insert_log_query,
            (
                group_id, moderator_id, target_user_id,
                action, reason, message_id
            )
        )
        conn.commit()
        return True, cursor.lastrowid

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def fetch_all_logs():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_all_logs_query)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def fetch_group_logs(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_group_logs_query, (group_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def fetch_user_logs(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_user_logs_query, (user_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def fetch_moderator_logs(moderator_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_moderator_logs_query, (moderator_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
