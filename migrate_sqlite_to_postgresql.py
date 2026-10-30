
import sqlite3
from pathlib import Path

from psycopg import sql

from database.postgres_connection import get_postgres_connection


DB_PATH = Path(__file__).resolve().parent / "bot.db"

# Stable ordering using each table's primary key.
TABLES = {
    "users": ["user_id"],
    "groups": ["group_id"],
    "contents": ["content_id"],
    "favourite": ["user_id", "content_id"],
    "submissions": ["submission_id"],
    "bot_roles": ["user_id", "role"],
    "moderation_logs": ["log_id"],
    "channel_publications": ["publication_id"],
}


def get_sqlite_columns(cursor, table):
    cursor.execute(f'PRAGMA table_info("{table}")')
    return [row[1] for row in cursor.fetchall()]


def get_postgres_columns(cursor, table):
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        ORDER BY ordinal_position
        """,
        (table,),
    )
    return [row[0] for row in cursor.fetchall()]


def fetch_sqlite_rows(cursor, table, order_columns):
    ordering = ", ".join(f'"{col}"' for col in order_columns)
    cursor.execute(f'SELECT * FROM "{table}" ORDER BY {ordering}')
    return cursor.fetchall()


def fetch_postgres_rows(cursor, table, columns, order_columns):
    query = sql.SQL(
        "SELECT {} FROM {} ORDER BY {}"
    ).format(
        sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, order_columns)),
    )
    cursor.execute(query)
    return cursor.fetchall()


def main():
    sqlite_connection = sqlite3.connect(
        DB_PATH.as_uri() + "?mode=ro",
        uri=True,
    )
    postgres_connection = get_postgres_connection()

    try:
        sqlite_cursor = sqlite_connection.cursor()

        with postgres_connection.cursor() as pg_cursor:
            all_match = True

            for table, order_columns in TABLES.items():
                sqlite_columns = get_sqlite_columns(
                    sqlite_cursor, table
                )
                pg_columns = get_postgres_columns(pg_cursor, table)

                if sqlite_columns != pg_columns:
                    print(f"FAIL: {table} column order differs")
                    print("SQLite:", sqlite_columns)
                    print("PostgreSQL:", pg_columns)
                    all_match = False
                    continue

                sqlite_rows = fetch_sqlite_rows(
                    sqlite_cursor, table, order_columns
                )
                pg_rows = fetch_postgres_rows(
                    pg_cursor, table, pg_columns, order_columns
                )

                if sqlite_rows == pg_rows:
                    print(f"PASS: {table} — exact match")
                else:
                    print(f"FAIL: {table} — data differs")
                    all_match = False

                    for index, (source, target) in enumerate(
                        zip(sqlite_rows, pg_rows)
                    ):
                        if source != target:
                            print(f"  Different row at position {index}")
                            for column, old, new in zip(
                                sqlite_columns, source, target
                            ):
                                if old != new:
                                    print(
                                        f"    {column}: "
                                        f"SQLite={old!r}, "
                                        f"PostgreSQL={new!r}"
                                    )

                    if len(sqlite_rows) != len(pg_rows):
                        print(
                            f"  Row counts differ: "
                            f"{len(sqlite_rows)} vs {len(pg_rows)}"
                        )

            print("\nRESULT:")
            print(
                "ALL DATA MATCHES"
                if all_match
                else "MISMATCHES FOUND — DO NOT SWITCH DATABASES"
            )

    finally:
        sqlite_connection.close()
        postgres_connection.close()


if __name__ == "__main__":
    main()
