import pandas as pd
import sqlalchemy as sql

def get_sql_data(query,
                 server = '10.14.3.5', # 'VS-SQL9-1'
                 database = 'DycoPlanEx',
                 trusted_connection = 'yes',
                 username = 'DWH_MAReader',
                 password = 'Dyconex1',
                ):
    """

    :param query: the query as a string
    :param server: server ip adress
    :param database: which database should be accessed
    :param driver: SQL Driver 17
    :param trusted_connection: yes enables Windows Authentication
    :param username: SQL Server username
    :param password: SQL Server password
    :return: pandas Dataframe
    """
    driver = 'ODBC Driver 17 for SQL Server'
    # Create the connection string using SQL Server Authentication
    connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
    # open up engine
    engine = sql.create_engine(connection_string)
    with open(query, 'r') as f:
        return pd.read_sql(f.read(), engine)

