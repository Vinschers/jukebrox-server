import pyodbc

class Database():
    def __init__(self, server, db, user, password):
        cnxn = pyodbc.connect(f'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={server};DATABASE={db};UID={user};PWD={password}')
        self.cursor = cnxn.cursor()

    def create_table(self, name, columns):
        sql_str = f'CREATE TABLE {name} ('

        for key in columns:
            sql_str += f'{key} {columns[key]}, '

        sql_str = sql_str[:-2] + ');'
        self.cursor.execute(sql_str)
        self.cursor.commit()
        return 'ok'

    def select(self, table, where):
        sql = f"select * from {table}"
        if where:
            sql += " " + where
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def insert(self, table, values: list):
        sql_str = f"INSERT INTO {table} VALUES ({', '.join(values)});"
        self.cursor.execute(sql_str)
        return self.cursor.commit()

    def get_tags_from_files(self, ids: list):
        ids = [f"'{id}'" for id in ids]
        ids_str = ', '.join(ids)
        sql = f"select Tag.*, MusicTag.musicId from Tag inner join MusicTag on Tag.id = MusicTag.tagId and MusicTag.musicId in ({ids_str})"

        self.cursor.execute(sql)

        columns = [column[0] for column in self.cursor.description]
        results = {}

        for row in self.cursor.fetchall():
            row_dict = dict(zip(columns, row))
            if not row_dict['musicId'] in results:
                results[row_dict['musicId']] = []
            results[row_dict['musicId']].append(row_dict)
        
        return results