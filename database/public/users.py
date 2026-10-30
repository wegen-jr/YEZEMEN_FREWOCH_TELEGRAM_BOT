import sqlite3
from database.connection import get_connection

user_insert_query="""
    INSERT INTO users(user_id, username, first_name, last_seen_at)
    VALUES(?, ?, ?, ?)
    ON CONFLICT(user_id)
    DO UPDATE SET 
        username=excluded.username,
        first_name=excluded.first_name, 
        last_seen_at=excluded.last_seen_at
"""
user_fetch_query="""
    SELECT * FROM users
"""
user_fetch_by_id="""
    SELECT username, first_name, last_seen_at, is_banned FROM users WHERE user_id=?
"""
user_profile_update_query="""
    UPDATE users SET username=?, first_name=? WHERE user_id=?
"""
delete_user_query="""
    DELETE FROM users WHERE user_id=?
"""

def is_user_banned(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_banned FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return bool(result and result[0])

def create_or_update_user(user_id,username,first_name,last_seen_at):
    data=[
        user_id,
        username,
        first_name,
        last_seen_at
    ]
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(user_insert_query,data)
    conn.commit()
    cursor.close()
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

