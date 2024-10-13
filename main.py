from providers.collectingData import downloadStockMarketData

option = 1
while option != 0:
    print("--------Serviços--------")
    print("1- Download de dados pela API Yahoo Finance.")
    print("0- Sair.")
    option = int(input("Número do serviço: "))

    if option == 1:
        print("\n--------------------------------------------------------------------------------\n")
        print("Quais são os tickers que deseja baixar dados?")
        print("É possível baixar dados de mais de um ticker por vez, separando-os com vírgula.")
        tickers = input("Tickers: ")

        tickers = tickers.replace(" ", "").split(",")
        dateStart = input("\nQual é a data inicial do período que deseja baixar os dados? (YYYY-MM-DD): ")
        dateEnd = input("Qual é a data final do período que deseja baixar os dados? (YYYY-MM-DD): ")

        downloadStockMarketData(tickers, dateStart, dateEnd)

        print("\n--------------------------------------------------------------------------------\n")