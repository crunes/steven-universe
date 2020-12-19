'''
STEVEN UNIVERSE: Scrape Steven Universe Wiki and analyze transcripts

Author: Charmaine Runes

This files creates a connection to the Gems database.
'''

import sqlite3
from sqlite3 import Error
import pandas as pd
import re

def create_connection(db_file):
    '''
    Create a database connection to the Postgres database specified by db_file

    Inputs:
        - db_file (str): database name (see config file)

    Returns Connection object or None
    '''
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, table_name, columns):
    '''
    Creates a table

    Inputs:
        - conn: Connection object
        - table_name (str): name of the table which also corresponds to csv
                            e.g., 'seasons', 'episodes', 'transcripts'
        - columns (list): column names from the csv

    Returns None, creates table in database
    '''

    try:
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS {};'.format(table_name))

        create_sql_str = 'CREATE TABLE IF NOT EXISTS {} ({});'
        create_command = create_sql_str.format(table_name, columns)

        c.execute(create_command)

    except Error as e:
        print(e)


def extract_data(table_data):
    '''
    Extracts tuples from data

    Inputs:
        - table_data: pandas DataFrame

    Returns: list of tuples to use in insert_records function
    '''
    return list(table_data.itertuples(index=False, name=None))


def insert_records(conn, table, columns, records):
    '''
    Insert multiple records of data into table

    Inputs:
        - conn: Connection object
        - table (str): name of the table / csv e.g. INMT4AA1
        - columns (str): column names from the csv
        - records (list): tuples from extract_data to insert into table

    Returns: None (updates table in database)
    '''
    try:
        c = conn.cursor()
        multiplier = len(columns.split(", "))
        sql = 'INSERT INTO {} VALUES '.format(table, columns)
        values = '?' + (', ?' * (multiplier-1))
        sql += '({});'.format(values)
        c.executemany(sql, records)

    except Error as e:
        print(e)


def main():
    '''
    Note: just for testing
    '''
    conn = create_connection(config.database_name)
    table_name = 'test'
    test_df = pd.DataFrame({'name': ['John', 'Karen'], 'age': [41, 32]})
    columns = test_df.columns
    columns = ', '.join(columns)

    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS test;")
    c.execute("CREATE TABLE IF NOT EXISTS test (name,age);")

    records = extract_data(test_df)
    insert_records(conn,table_name,columns,records)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
