import sqlite3
from database.connection import get_connection
from datetime import datetime
insert_content_query = """
    INSERT INTO contents (
        title,
        body,
        content_type,
        author_name,
        source,
        category,
        submitted_by,
        is_published,
        status,
        published_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?)
"""
is_admin_query="""
    SELECT user_id FROM bot_roles WHERE user_id=?
"""
fetch_pending_contents_query = """
    SELECT
        content_id,
        title,
        content_type,
        body,
        author_name,
        source,
        category,
        status
    FROM contents WHERE status=?
"""

fetch_contents_by_id_query = """
    SELECT
        content_id,
        title,
        body,
        author_name,
        source,
        category
        
    FROM contents WHERE content_id=?
"""
update_status_query="""
    UPDATE contents
    SET status=?,
        approved_by=?,
        is_published=?,
        published_at=?
    WHERE content_id=?
"""
def fetch_pendings(status):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(fetch_pending_contents_query,(status,))
        data=cursor.fetchall()

        return data
    finally:
        cursor.close()
        conn.close()

def fetch_contents_by_id(content_id):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(fetch_contents_by_id_query,(content_id,))
        data=cursor.fetchone()

        return data
    finally:
        cursor.close()
        conn.close()

def is_admin(user_id):
    conn=get_connection()
    cursor=conn.cursor()
    
    try:
            cursor.execute(is_admin_query,(user_id,))
            data=cursor.fetchone()
    
            return data
    finally:
            cursor.close()
            conn.close()

def create_content(
    title,
    body,
    content_type,
    author_name,
    source,
    category,
    submitted_by
):
    is_it_admin=is_admin(submitted_by)
    if is_it_admin is not None:
         is_published=1
         status="approved"
         published_at=datetime.now()
         data = (
            title,
            body,
            content_type,
            author_name,
            source,
            category,
            submitted_by,
            is_published,
            status,
            published_at,
        )

    conn = get_connection()
    cursor = conn.cursor()
    try:
        
        cursor.execute(insert_content_query, data)
        conn.commit()

        return  "✅ Content inserted successfully."

    except sqlite3.IntegrityError as error:
        conn.rollback()

        if "UNIQUE constraint failed" in str(error):
            return False, "Content with this title and body already exists."


    finally:
        cursor.close()
        conn.close()

def update_status(status,approved_by,is_published,published_at,content_id,):
    conn=get_connection()
    cursor=conn.cursor()
    if not is_published:
        published_at=None
    try:
            cursor.execute(update_status_query,(status,approved_by,is_published,published_at,content_id,))
            conn.commit()    
            return True, "status updated successfully"
    finally:
            cursor.close()
            conn.close()
