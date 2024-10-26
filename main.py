import logging
import os
from providers.cleaningData import clearData
from providers.collectingData import downloadStockMarketData
from providers.databaseConnection import getAvaliableTikers
from providers.modelLSTM import analyzingDataWithLSTM

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

def main():
    option = 1
    while option != 0:
        print("--------Serviços--------")
        print("1- Download de dados.")
        print("2- Limpeza de dados.")
        print("3- Análise de dados.")
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

            if ticker != 0:
                clearData(ticker)


        elif option == 3:
            tickers = getAvaliableTikers('CLEAR')
            print("Tikers disponíveis para análise, selecione um:")
            ticker = selectTickerMenu(tickers)

            if ticker != 0:
                print("Deseja analizar com qual modelo:")
                print("1- LSTM")
                print("0- Voltar")
                modelOption = int(input("Modelo: "))

                print("Deseja utilizar que tipo de previsão:")
                print("1- Dia após dia")
                print("2- Periodo inteiro")

                predictionType = int(input("Tipo: "))

                if modelOption == 1:
                    analyzingDataWithLSTM(ticker, predictionType)


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
    return 0

if __name__ == "__main__":
    main()
