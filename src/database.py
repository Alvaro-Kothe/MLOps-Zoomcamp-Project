import sqlite3

from src.mushroom import MUSHROOM_CHARACTERISTICS

DATABASE_FILE = "mushroom_data.db"


def create_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    return conn


def create_table(conn: sqlite3.Connection):
    table_columns = (k + " TEXT" for k in MUSHROOM_CHARACTERISTICS)
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS mushrooms (
    id INTEGER PRIMARY KEY,
    class TEXT,
    {', '.join(table_columns)}
    )
    """

    cursor = conn.cursor()
    cursor.execute(create_table_query)


# https://stackoverflow.com/questions/10913080/python-how-to-insert-a-dictionary-to-a-sqlite-database
def get_insert_query():
    table_columns = [":" + k for k in MUSHROOM_CHARACTERISTICS]
    insert_query = f"""
    INSERT INTO mushrooms VALUES (
            :id,
            :class, {", ".join(table_columns)}
    )
    """

    return insert_query
