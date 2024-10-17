import pandas
from providers.databaseConnection import openDatabaseConnection


def clearData(ticker):
    dataframe = getTickerRawData(ticker)
    dataframe = removeDuplicates(dataframe)

    return dataframe

def getTickerRawData(ticker):
    connection = openDatabaseConnection()
    sql = f'SELECT * FROM "{ticker}_RAW" ORDER BY "Date" ASC'
    data = pandas.read_sql(sql, connection)

    return data

def removeDuplicates(tickerDataframe):
    return tickerDataframe.drop_duplicates(subset=['Date'], keep='last')

def getAvaliableTikers():
    connection = openDatabaseConnection()
    sql = """
        SELECT table_name as name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        AND table_name LIKE '%%_RAW'
    """
    tables = pandas.read_sql(sql, connection)
    data = tables['name'].tolist()

    return [ticker.replace('_RAW', '') for ticker in data]
