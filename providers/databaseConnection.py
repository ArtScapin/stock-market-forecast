import os
import pandas
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy import text

def openDatabaseConnection():
    load_dotenv()
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    name = os.getenv('DB_NAME')

    connString = f'postgresql://{user}:{password}@{host}:{port}/{name}'
    engine = create_engine(connString)

    return engine

def saveStockMarketDataOnDatabase(data, ticker, rawData = 0):
    engine = openDatabaseConnection()
    tableName = ticker.replace(' ', '_')
    if rawData == 1:
        tableName += '_RAW'
    data.to_sql(tableName, engine, if_exists='replace', index=True)

    if rawData == 1:
        print(f'Dados de {ticker} salvos na tabela {tableName}.')
    else:
        with engine.connect() as connection:
            connection.execute(text(f'DROP TABLE "{tableName}_RAW";'))
            connection.commit()
        print(f'Dados já tratados de {ticker} salvos na tabela {tableName}.')

def getAvaliableTikers(rawData = 0):
    connection = openDatabaseConnection()
    if rawData == 1:
        sql = """
            SELECT REPLACE(table_name, '_RAW', '') as name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_name LIKE '%%_RAW'
        """
    else:
        sql = """
            SELECT table_name as name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_name NOT LIKE '%%_RAW'
        """
    tables = pandas.read_sql(sql, connection)
    data = tables['name'].tolist()

    return data

def getTickerData(ticker, rawData = 0):
    connection = openDatabaseConnection()
    if rawData == 1:
        sql = f'SELECT * FROM "{ticker}_RAW" ORDER BY "Date" ASC'
    else:
        sql = f'SELECT * FROM "{ticker}" ORDER BY "Date" ASC'
    data = pandas.read_sql(sql, connection)

    return data
