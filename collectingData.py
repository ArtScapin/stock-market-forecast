import yfinance
from databaseConnection import openDatabaseConnection

def downloadStockMarketData(tickers, start, end):
    for ticker in tickers:
        data = yfinance.download(ticker, start, end)
        if not data.empty:
            saveStockMarketDataOnDatabase(data, ticker)
        else:
            print(f'No data for {ticker}')

def saveStockMarketDataOnDatabase(data, ticker):
    con = openDatabaseConnection()
    tableName = ticker.replace(' ', '_')
    data.to_sql(tableName, con, if_exists='replace', index=True)
    print(f'Data from {ticker} saved in table {tableName}')

stockMarketTickers = ['AAPL', 'MSFT', 'GOOGL']
dateStart = '2023-01-01'
dateEnd = '2023-12-31'

downloadStockMarketData(stockMarketTickers, dateStart, dateEnd)
