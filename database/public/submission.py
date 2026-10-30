import sqlite3
from database.connection import get_connection


insert_submission_query = """
    INSERT INTO submissions(
        submitted_by, title, body, content_type,
        author_name, source, category
    )
    VALUES(?, ?, ?, ?, ?, ?, ?)
"""

fetch_submissions_query = """
    SELECT * FROM submissions
    ORDER BY created_at DESC
"""

fetch_submission_by_id_query = """
    SELECT * FROM submissions
    WHERE submission_id = ?
"""

fetch_submissions_by_user_query = """
    SELECT * FROM submissions
    WHERE submitted_by = ?
    ORDER BY created_at DESC
"""

fetch_submissions_by_status_query = """
    SELECT * FROM submissions
    WHERE status = ?
    ORDER BY created_at DESC
"""

update_submission_query = """
    UPDATE submissions
    SET title = ?, body = ?, content_type = ?,
        author_name = ?, source = ?, category = ?
    WHERE submission_id = ? AND status = 'pending'
"""

review_submission_query = """
    UPDATE submissions
    SET status = ?, reviewed_by = ?,
        reviewed_at = CURRENT_TIMESTAMP, review_note = ?
    WHERE submission_id = ? AND status = 'pending'
"""

delete_submission_query = """
    DELETE FROM submissions
    WHERE submission_id = ?
"""


def create_submission(
    submitted_by, title, body, content_type,
    author_name, source, category
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            insert_submission_query,
            (
                submitted_by, title, body, content_type,
                author_name, source, category
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


def fetch_all_submissions():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_submissions_query)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def fetch_submission_by_id(submission_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_submission_by_id_query, (submission_id,))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def fetch_submissions_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_submissions_by_user_query, (user_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def fetch_submissions_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(fetch_submissions_by_status_query, (status,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def update_submission(
    submission_id, title, body, content_type,
    author_name, source, category
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            update_submission_query,
            (
                title, body, content_type, author_name,
                source, category, submission_id
            )
        )
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Submission not found or no longer pending."

        return True, "Submission updated successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def review_submission(submission_id, reviewer_id, status, review_note=None):
    if status not in ("approved", "rejected"):
        return False, "Status must be approved or rejected."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            review_submission_query,
            (status, reviewer_id, review_note, submission_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Submission not found or already reviewed."

        return True, f"Submission {status} successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, str(error)

    finally:
        cursor.close()
        conn.close()


def delete_submission(submission_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(delete_submission_query, (submission_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return False, "Submission not found."

        return True, "Submission deleted successfully."

    finally:
        cursor.close()
        conn.close()
