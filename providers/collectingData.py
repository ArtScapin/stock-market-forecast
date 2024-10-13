import yfinance

from providers.databaseConnection import openDatabaseConnection


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
