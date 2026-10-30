import sqlite3
from database.connection import get_connection
user_fetch_query="""
    SELECT * FROM users
"""
user_fetch_by_id="""
    SELECT  user_id,username, first_name, last_seen_at, is_banned FROM users WHERE user_id=?
"""
user_profile_update_query="""
    UPDATE users SET username=?, first_name=? WHERE user_id=?
"""
delete_user_query="""
    DELETE FROM users WHERE user_id=?
"""
fetch_admins_query="""
    SELECT u.user_id, u.first_name, u.username r.
"""
import sqlite3
from database.connection import get_connection


def find_user_by_username(username):
    print(username)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, first_name, is_banned
            FROM users
            WHERE username = ?
        """, (username,))
        return cursor.fetchone()
    except sqlite3.Error as error:
        print("Error finding user:", error)
        return None
    finally:
        conn.close()

def unban_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET is_banned = 0 WHERE user_id = ? AND is_banned = 1",
        (user_id,)
    )

    success = cursor.rowcount > 0

    conn.commit()
    cursor.close()
    conn.close()

    return success

def ensure_owner_admin(owner_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Register the owner if they are not already registered
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, first_name)
            VALUES (?, ?)
        """, (owner_id, "Bot Owner"))

        # Ensure the owner has the admin role
        cursor.execute("""
            INSERT OR IGNORE INTO bot_roles (user_id, role)
            VALUES (?, 'admin')
        """, (owner_id,))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def get_user_roles(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role
            FROM bot_roles
            WHERE user_id = ?
        """, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as error:
        print("Error fetching user roles:", error)
        return []
    finally:
        conn.close()


def assign_role(user_id, role, granted_by):
    if role not in ("admin", "moderator"):
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bot_roles (user_id, role, granted_by)
            VALUES (?, ?, ?)
        """, (user_id, role, granted_by))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    except sqlite3.Error as error:
        conn.rollback()
        print("Error assigning role:", error)
        return False
    finally:
        conn.close()


def remove_role(user_id, role):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM bot_roles
            WHERE user_id = ? AND role = ?
        """, (user_id, role))

        removed = cursor.rowcount > 0
        conn.commit()
        return removed
    except sqlite3.Error as error:
        conn.rollback()
        print("Error removing role:", error)
        return False
    finally:
        conn.close()


def ban_user(user_id):

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
                UPDATE users
                SET is_banned = 1
                WHERE user_id = ? AND is_banned = 0
            """, (user_id,))

        updated = cursor.rowcount > 0
        conn.commit()
        return updated
    except sqlite3.Error as error:
        conn.rollback()
        print("Error banning user:", error)
        return False
    finally:
        conn.close()


def fetch_banned_users():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, first_name
            FROM users
            WHERE is_banned = 1
            ORDER BY first_name
        """)
        return cursor.fetchall()
    except sqlite3.Error as error:
        print("Error fetching banned users:", error)
        return []
    finally:
        conn.close()


def fetch_users_data():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(user_fetch_query)
    data=cursor.fetchall()
    cursor.close()
    conn.close()

    return data

def fetch_specific_user_data(user_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(user_fetch_by_id,(user_id,))
    data=cursor.fetchone()
    print(data,"from")
    cursor.close()
    conn.close()

    return data


def update_profile(user_id,username,first_name):
    data=[
        username,
        first_name,
        user_id
    ]
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(user_profile_update_query,data)

    conn.commit()
    cursor.close()
    conn.close()

def delete_user(user_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(delete_user_query,(user_id,))

    conn.commit()
    cursor.close()
    conn.close()

