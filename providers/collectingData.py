import yfinance
from providers.databaseConnection import openDatabaseConnection


def downloadStockMarketData(tickers, start, end):
    tickers =  [ticker + '.SA' for ticker in tickers]
    for ticker in tickers:
        if isB3Ticker(ticker):
            data = yfinance.download(ticker, start, end)
            ticker = ticker.replace('.SA', '')
            if not data.empty:
                saveStockMarketDataOnDatabase(data, ticker)
            else:
                print(f'Sem dados para {ticker}.')
        else:
            print(f'{ticker} não encontrado na listagem de ativos da B3.')

def saveStockMarketDataOnDatabase(data, ticker):
    con = openDatabaseConnection()
    tableName = ticker.replace(' ', '_') + '_RAW'
    data.to_sql(tableName, con, if_exists='replace', index=True)
    print(f'Dados de {ticker} salvos na tabela {tableName}.')

def isB3Ticker(ticker):
    tickerInfo = yfinance.Ticker(ticker)
    try:
        return tickerInfo.info['exchange'] == 'SAO'
    except KeyError:
        return False
