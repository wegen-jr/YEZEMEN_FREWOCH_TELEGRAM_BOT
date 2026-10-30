import sqlite3

from database.connection import get_connection


user_table_query="""
    CREATE TABLE IF NOT EXISTS users(
        user_id integer primary key,
        username text UNIQUE,
        first_name text,
        created_at text default CURRENT_TIMESTAMP,
        last_seen_at text,
        is_banned boolean default 0
    )
"""

content_table_query="""
    CREATE TABLE IF NOT EXISTS contents(
        content_id integer primary key,
        title text,
        body text,
        content_type text default 'poem'
        check (content_type IN('poem','reflection','lyrics','short_story')),
        author_name text,
        source text,
        category text default 'love'
        check (category IN ('love','nature','philosophy','life_lesson')),
        submitted_by integer not null,
        approved_by integer,
        created_at text default CURRENT_TIMESTAMP,
        published_at text,
        is_published boolean default 0,
        status text default 'pending'
        check(status IN ('pending','approved','rejected')),

        UNIQUE(title,body),
        FOREIGN KEY (submitted_by) REFERENCES users(user_id)
            ON UPDATE CASCADE ,
        FOREIGN KEY (approved_by) REFERENCES users(user_id)
                    ON UPDATE CASCADE 
    )
"""

favourite_contents_query="""
    CREATE TABLE IF NOT EXISTS favourite(
        user_id integer,
        content_id integer,
        saved_at text default CURRENT_TIMESTAMP,

        primary key(user_id, content_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE ,
        FOREIGN KEY (content_id) REFERENCES contents(content_id)
                        ON UPDATE CASCADE ON DELETE CASCADE
    )
"""

submissions_table_query = """
    CREATE TABLE IF NOT EXISTS submissions (
        submission_id INTEGER PRIMARY KEY,
        submitted_by INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        content_type TEXT NOT NULL
            CHECK (content_type IN ('poem', 'reflection', 'quote')),
        author_name TEXT,
        source TEXT,
        category TEXT,
        status TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'approved', 'rejected')),
        reviewed_by INTEGER,
        reviewed_at TEXT,
        review_note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        content_id INTEGER UNIQUE,

        FOREIGN KEY (submitted_by) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (reviewed_by) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE SET NULL,
        FOREIGN KEY (content_id) REFERENCES contents(content_id)
            ON UPDATE CASCADE ON DELETE SET NULL
    )
"""

bot_roles_table_query = """
    CREATE TABLE IF NOT EXISTS bot_roles (
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL
            CHECK (role IN ('admin', 'moderator')),
        granted_by INTEGER,
        granted_at TEXT DEFAULT CURRENT_TIMESTAMP,

        PRIMARY KEY (user_id, role),

        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (granted_by) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE SET NULL
    )
"""

groups_table_query = """
    CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY,
        group_title TEXT NOT NULL,
        welcome_enabled INTEGER DEFAULT 1
            CHECK (welcome_enabled IN (0, 1)),
        rules_text TEXT,
        moderation_enabled INTEGER DEFAULT 1
            CHECK (moderation_enabled IN (0, 1)),
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
"""

moderation_logs_table_query = """
    CREATE TABLE IF NOT EXISTS moderation_logs (
        log_id INTEGER PRIMARY KEY,
        group_id INTEGER NOT NULL,
        moderator_id INTEGER NOT NULL,
        target_user_id INTEGER,
        action TEXT NOT NULL
            CHECK (action IN (
                'warn', 'ban', 'unban', 'delete_message'
            )),
        reason TEXT,
        message_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (group_id) REFERENCES groups(group_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (moderator_id) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (target_user_id) REFERENCES users(user_id)
            ON UPDATE CASCADE ON DELETE SET NULL
    )
"""
create_channel_publications_table_query = """
    CREATE TABLE IF NOT EXISTS channel_publications (
        publication_id INTEGER PRIMARY KEY AUTOINCREMENT,

        content_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        message_id INTEGER,

        status TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'posted', 'failed', 'removed')),

        posted_at TEXT,
        last_synced_at TEXT,
        content_hash TEXT,
        last_error TEXT,

        FOREIGN KEY (content_id)
            REFERENCES contents(content_id)
            ON DELETE CASCADE,

        UNIQUE (content_id, channel_id)
    )
"""

table_queries=[
    user_table_query,
    content_table_query,
    favourite_contents_query,
    submissions_table_query,
    bot_roles_table_query,
    groups_table_query,
    moderation_logs_table_query,
    create_channel_publications_table_query
]

def initialize_db():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        for query in table_queries:
            cursor.execute(query)

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
