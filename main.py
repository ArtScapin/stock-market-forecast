from providers.collectingData import downloadStockMarketData

def getInputWithDefault(prompt, default):
    userInput = input(prompt)
    return userInput if userInput else default

option = 1
while option != 0:
    print("--------Serviços--------")
    print("1- Download de dados.")
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

    print("\n--------------------------------------------------------------------------------\n")
