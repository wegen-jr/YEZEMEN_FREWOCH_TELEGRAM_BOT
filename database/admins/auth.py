import sqlite3
from database.connection import get_connection

check_role_query = """
    SELECT 1 FROM bot_roles
    WHERE user_id = ? AND role IN ('admin','moderator') 
"""

def check_role(user_id):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(check_role_query,(user_id,))
        data=cursor.fetchone()

        return data is not None

    except sqlite3.Error as error:
        print("Error checking admin access:", error)
        return False
    finally:
        conn.close()
