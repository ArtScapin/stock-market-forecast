import logging
import os

from providers.buildGraphs import buildGraph
from providers.cleaningData import clearData
from providers.collectingData import downloadStockMarketData
from providers.databaseConnection import getAvaliableTikers
from providers.modelLSTM import analyzingDataWithLSTM
from providers.modelProphet import analyzingDataWithProphet
from providers.modelRandomForest import analyzingDataWithRandomForest
from providers.simulator import dayTradeSimulator

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)


def main():
    option = 1
    while option != 0:
        print("--------Serviços--------")
        print("1- Download de dados.")
        print("2- Limpeza de dados.")
        print("3- Análise de dados.")
        print("4- Gerar gráficos das previsões.")
        print("5- Simulador de DayTrade.")
        print("0- Sair.")
        option = int(input("Número do serviço: "))

        print("\n--------------------------------------------------------------------------------\n")
        if option == 1:
            print("Quais são os tickers que deseja baixar dados?")
            print("É possível baixar dados de mais de um ticker por vez, separando-os com vírgula.")
            tickers = input("Tickers: ")

            tickers = tickers.replace(" ", "").replace(".SA", "").split(",")

            dateStart = getInputWithDefault("\nQual é a data inicial do período que deseja baixar os dados? (YYYY-MM-DD): ", '2020-01-01')
            dateEnd = getInputWithDefault("Qual é a data final do período que deseja baixar os dados? (YYYY-MM-DD): ", '2023-12-31')

            downloadStockMarketData(tickers, dateStart, dateEnd)

        elif option == 2:
            tickers = getAvaliableTikers('RAW')
            print("Tikers disponíveis para limpeza, selecione um:")
            ticker = selectTickerMenu(tickers)

            if ticker != 0 and ticker != -1:
                clearData(ticker)
            elif ticker == -1:
                for ticker in tickers:
                    clearData(ticker)

        elif option == 3:
            tickers = getAvaliableTikers('CLEAR')
            print("Tikers disponíveis para análise, selecione um:")
            ticker = selectTickerMenu(tickers)

            if ticker != 0 and ticker != -1:
                    analyzingDataWithLSTM(ticker,1)
                    analyzingDataWithLSTM(ticker,2)
                    analyzingDataWithProphet(ticker,1)
                    analyzingDataWithProphet(ticker,2)
                    analyzingDataWithRandomForest(ticker,1)
                    analyzingDataWithRandomForest(ticker,2)
            elif ticker == -1:
                for ticker in tickers:
                    analyzingDataWithLSTM(ticker,1)
                    analyzingDataWithLSTM(ticker,2)
                    analyzingDataWithProphet(ticker,1)
                    analyzingDataWithProphet(ticker,2)
                    analyzingDataWithRandomForest(ticker,1)
                    analyzingDataWithRandomForest(ticker,2)

        elif option == 4:
            tickers = getAvaliableTikers('PREV')
            print("Tikers com previsões disponíveis, selecione um:")
            ticker = selectTickerMenu(tickers)
            print("Quais modelos inserir no gráfico? (separe com vírgula para selecionar mais de um)")
            print("-LSTM")
            print("-Prophet")
            print("-RandomForest")
            models = input("Modelos: ")
            if models == "all":
                models = "LSTM, Prophet, RandomForest"
            models = models.replace(" ", "").split(",")


            if ticker != 0 and ticker != -1:
                buildGraph(ticker, 1, models)
                buildGraph(ticker, 2, models)
            elif ticker == -1:
                for ticker in tickers:
                    buildGraph(ticker, 1, models)
                    buildGraph(ticker, 2, models)

        elif option == 5:
            tickers = getAvaliableTikers('PREV')
            print("Tikers com previsões disponíveis para simulação, selecione um:")
            ticker = selectTickerMenu(tickers)

            if ticker != 0 and ticker != -1:
                dayTradeSimulator(ticker)
            elif ticker == -1:
                for ticker in tickers:
                    dayTradeSimulator(ticker)



        if option != 0:
            print("\n--------------------------------------------------------------------------------\n")


def getInputWithDefault(prompt, default):
    userInput = input(prompt)
    return userInput if userInput else default


def selectTickerMenu(tickers):
    for index, ticker in enumerate(tickers, start=1):
        print(f"{index}- {ticker}")
    print("0- Voltar")

    tickerOption = int(input("Ticker: "))

    if 0 < tickerOption <= len(tickers):
        return tickers[tickerOption - 1]
    elif tickerOption == -1:
        return  tickerOption
    return 0


if __name__ == "__main__":
    main()
