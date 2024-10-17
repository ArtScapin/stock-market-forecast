import pandas
from providers.databaseConnection import openDatabaseConnection
from workalendar.america import Brazil
from sklearn.preprocessing import MinMaxScaler


def clearData(ticker):
    dataframe = getTickerRawData(ticker)
    dataframe = removeDuplicates(dataframe)
    dataframe = dataImputationForNullData(dataframe)
    dataframe = applyMinMaxScaling(dataframe)

    return dataframe

def getTickerRawData(ticker):
    connection = openDatabaseConnection()
    sql = f'SELECT * FROM "{ticker}_RAW" ORDER BY "Date" ASC'
    data = pandas.read_sql(sql, connection)

    return data

def removeDuplicates(tickerDataframe):
    return tickerDataframe.drop_duplicates(subset=['Date'], keep='first')

def dataImputationForNullData(tickerDataframe):
    dateStart = tickerDataframe.Date.min()
    dateEnd = tickerDataframe.Date.max()
    workingDays = getB3WorkingDays(dateStart, dateEnd)

    for day in workingDays:
        if not tickerDataframe['Date'].isin([day]).any():
            previousData = tickerDataframe[tickerDataframe['Date'] < day].iloc[-1]
            nextData = tickerDataframe[tickerDataframe['Date'] > day].iloc[0]

            newRegister = pandas.DataFrame({
                'Date': [day],
                'Open': [(previousData['Open'] + nextData['Open']) / 2],
                'High': [(previousData['High'] + nextData['High']) / 2],
                'Low': [(previousData['Low'] + nextData['Low']) / 2],
                'Close': [(previousData['Close'] + nextData['Close']) / 2],
                'Adj Close': [(previousData['Adj Close'] + nextData['Adj Close']) / 2],
                'Volume': [(previousData['Volume'] + nextData['Volume']) / 2]
            })

            tickerDataframe = pandas.concat([tickerDataframe, newRegister]).sort_values('Date').reset_index(drop=True)

    return tickerDataframe

def getB3WorkingDays(startDate, endDate):
    businessDays = pandas.date_range(start=startDate, end=endDate, freq='B')
    cal = Brazil()
    workingDays = [day for day in businessDays if cal.is_working_day(day)]

    return pandas.to_datetime(workingDays)

def applyMinMaxScaling(tickerDataframe):
    columnsToScale = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    scaler = MinMaxScaler()

    tickerDataframe[columnsToScale] = scaler.fit_transform(tickerDataframe[columnsToScale])

    return tickerDataframe

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