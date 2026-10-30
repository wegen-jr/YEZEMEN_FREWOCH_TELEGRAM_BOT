
from psycopg import Error
from database.postgres_connection import get_postgres_connection


def create_submission(
    submitted_by, title, body, content_type,
    author_name, source, category
):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO submissions (
                    submitted_by, title, body, content_type,
                    author_name, source, category
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING submission_id
                """,
                (
                    submitted_by, title, body, content_type,
                    author_name, source, category
                )
            )

            submission_id = cursor.fetchone()[0]

        conn.commit()
        return True, submission_id

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error creating submission:", error)
        return False, str(error)

    finally:
        if conn is not None:
            conn.close()


def fetch_all_submissions():
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM submissions
                ORDER BY created_at DESC
                """
            )

            return cursor.fetchall()

    except Error as error:
        print("Error fetching submissions:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def fetch_submission_by_id(submission_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM submissions
                WHERE submission_id = %s
                """,
                (submission_id,)
            )

            return cursor.fetchone()

    except Error as error:
        print("Error fetching submission:", error)
        return None

    finally:
        if conn is not None:
            conn.close()


def fetch_submissions_by_user(user_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM submissions
                WHERE submitted_by = %s
                ORDER BY created_at DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

    except Error as error:
        print("Error fetching user submissions:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def fetch_submissions_by_status(status):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM submissions
                WHERE status = %s
                ORDER BY created_at DESC
                """,
                (status,)
            )

            return cursor.fetchall()

    except Error as error:
        print("Error fetching submissions by status:", error)
        return []

    finally:
        if conn is not None:
            conn.close()


def update_submission(
    submission_id, title, body, content_type,
    author_name, source, category
):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE submissions
                SET title = %s,
                    body = %s,
                    content_type = %s,
                    author_name = %s,
                    source = %s,
                    category = %s
                WHERE submission_id = %s
                  AND status = 'pending'
                """,
                (
                    title, body, content_type,
                    author_name, source, category,
                    submission_id
                )
            )

            updated = cursor.rowcount > 0

        conn.commit()

        if not updated:
            return False, "Submission not found or no longer pending."

        return True, "Submission updated successfully."

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error updating submission:", error)
        return False, str(error)

    finally:
        if conn is not None:
            conn.close()


def review_submission(
    submission_id, reviewer_id, status, review_note=None
):
    if status not in ("approved", "rejected"):
        return False, "Status must be approved or rejected."

    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE submissions
                SET status = %s,
                    reviewed_by = %s,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_note = %s
                WHERE submission_id = %s
                  AND status = 'pending'
                """,
                (status, reviewer_id, review_note, submission_id)
            )

            updated = cursor.rowcount > 0

        conn.commit()

        if not updated:
            return False, "Submission not found or already reviewed."

        return True, f"Submission {status} successfully."

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error reviewing submission:", error)
        return False, str(error)

    finally:
        if conn is not None:
            conn.close()


def delete_submission(submission_id):
    conn = None

    try:
        conn = get_postgres_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM submissions
                WHERE submission_id = %s
                """,
                (submission_id,)
            )

            deleted = cursor.rowcount > 0

        conn.commit()

        if not deleted:
            return False, "Submission not found."

        return True, "Submission deleted successfully."

    except Error as error:
        if conn is not None:
            conn.rollback()

        print("Error deleting submission:", error)
        return False, str(error)

    finally:
        if conn is not None:
            conn.close()
