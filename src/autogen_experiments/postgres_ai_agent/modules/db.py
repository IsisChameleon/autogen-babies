import psycopg2
from psycopg2 import sql

class PostgresDB:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

    def connect_with_url(self, url):
        self.conn = psycopg2.connect(url)

    def upsert(self, table_name, _dict):
        columns = _dict.keys()
        values = list(_dict.values())
        update_columns = [f"{col}=EXCLUDED.{col}" for col in columns]
        placeholders = ', '.join(['%s' for _ in values])

        query = sql.SQL(
            f"INSERT INTO {{}} ({{}}) VALUES ({placeholders}) ON CONFLICT (id) DO UPDATE SET {{}}"
        ).format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(map(sql.SQL, update_columns))
        )

        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
        self.conn.commit()

    def delete(self, table_name, _id):
        query = sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(table_name))
        with self.conn.cursor() as cursor:
            cursor.execute(query, (_id,))
        self.conn.commit()

    def get(self, table_name, _id):
        query = sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(table_name))
        with self.conn.cursor() as cursor:
            cursor.execute(query, (_id,))
            return cursor.fetchone()

    def get_all(self, table_name):
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def run_sql(self, sql_statement):
        with self.conn.cursor() as cursor:
            cursor.execute(sql_statement)
        self.conn.commit()

    def get_table_definition(self, table_name):
        query = "pg_dump -s -t {} -U {} {}".format(
            table_name,
            self.conn.info.user,
            self.conn.info.dbname
        )
        return query  # You would typically run this in a shell to get the create table statement

    def get_all_table_names(self):
        query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]

    def get_table_definition_for_prompt(self):
        table_names = self.get_all_table_names()
        table_definitions = []
        for table in table_names:
            table_definitions.append(self.get_table_definition(table))
        return "\n".join(table_definitions)
