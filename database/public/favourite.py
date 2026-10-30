import sqlite3
from database.connection import get_connection

insert_favourite_query="""
    INSERT INTO favourite(user_id, content_id)
    VALUES(?,?)
"""

fetch_favourite_query="""
    SELECT c.content_id,c.content_type,c.title,c.body,c.author_name,c.source,c.category,c.status,c.is_published,f.saved_at
    FROM favourite AS f
    JOIN contents AS c ON f.content_id=c.content_id
    WHERE f.user_id=? AND content_type=? AND status=? AND is_published=? ORDER BY f.saved_at DESC
"""
fetch_all_favourite_query="""
    SELECT c.content_id,c.title,c.body,c.author_name,c.source,c.category,c.status,c.is_published, f.saved_at
    FROM favourite AS f
    JOIN contents AS c ON f.content_id=c.content_id
    WHERE f.user_id=? AND status=? AND is_published=? ORDER BY f.saved_at DESC
"""
is_favourite_query="""
    SELECT * FROM favourite WHERE content_id=? AND user_id=?
"""
delete_favourite_query="""
    DELETE FROM favourite WHERE content_id=? AND user_id=?
"""

def create_favourite(user_id,content_id):
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(insert_favourite_query,(user_id,content_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        return "sqlite integrity error"

def fetch_favourite(user_id,content_type):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(fetch_favourite_query,(user_id,content_type,"approved",1,))
    data=cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return data
def fetch_all_favourites(user_id):
     conn=get_connection()
     cursor=conn.cursor()
     cursor.execute(fetch_all_favourite_query,(user_id,"approved",1,))
     data=cursor.fetchall()
     
     conn.commit()
     cursor.close()
     conn.close()
     
     return data

def is_favourite(content_id,user_id):
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute(is_favourite_query,(content_id,user_id,))
        data=cursor.fetchall()
    
        conn.commit()
        cursor.close()
        conn.close()
        return data
        
def delete_favourite(content_id,user_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(delete_favourite_query,(content_id,user_id,))
    
    conn.commit()
    cursor.close
    conn.close()

