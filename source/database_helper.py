# source/database_helper.py
import pymysql
import configparser


def read_db_config(filename='source/config.ini', section='Database'):
    # create a parser
    parser = configparser.ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to Database
    db_config = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db_config[item[0]] = item[1]
    else:
        raise Exception(f'{section} not found in the {filename} file')

    return db_config


def connect_to_database():
    # Read database configuration
    db_config = read_db_config()

    # Connect to MySQL database
    return pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def execute_query(query, conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except pymysql.Error as e:
        # Attempt to reconnect if the error indicates a lost connection
        if e.args[0] == 2006:
            print("Reconnecting to the database...")
            conn.ping(reconnect=True)
            return execute_query(query, conn)  # Retry the query
        else:
            print(f"Error executing query: {e}")
            raise
            return []


def execute_query_with_status(query, conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            conn.commit()  # Commit the changes
            return True, cursor.fetchall()
    except pymysql.Error as e:
        # Attempt to reconnect if the error indicates a lost connection
        if e.args[0] == 2006:
            print("Reconnecting to the database...")
            conn.ping(reconnect=True)
            return execute_query_with_status(query, conn)  # Retry the query
        else:
            print(f"Error executing query: {e}")
            return False, []


def close_database_connection(conn):
    # Close the database connection
    if conn:
        conn.close()
