import yfinance
from providers.databaseConnection import saveStockMarketDataOnDatabase


def downloadStockMarketData(tickers, start, end):
    tickers =  [ticker + '.SA' for ticker in tickers]
    for ticker in tickers:
        if isB3Ticker(ticker):
            data = yfinance.download(ticker, start, end)
            ticker = ticker.replace('.SA', '')
            if not data.empty:
                saveStockMarketDataOnDatabase(data, ticker, 1)
            else:
                print(f'Sem dados para {ticker}.')
        else:
            print(f'{ticker} não encontrado na listagem de ativos da B3.')

def isB3Ticker(ticker):
    tickerInfo = yfinance.Ticker(ticker)
    try:
        return tickerInfo.info['exchange'] == 'SAO'
    except KeyError:
        return False
