from matplotlib import pyplot as plt

from providers.databaseConnection import getTickerData


def buildGraph(ticker, predictionType, models):
    dataframe = getTickerData(ticker, "CLEAR")
    predictions = getTickerData(ticker, "PREV")
    predictions = predictions[predictions['PredictionType'] == predictionType]
    dataframe = dataframe[round(len(dataframe) * 0.8):]
    predictionType = 'daily' if predictionType == 1 else 'period'

    plt.figure(figsize=(12, 6))

    for model in models:
        color = "green" if model == 'LSTM' else "red" if model == 'Prophet' else "pink"
        predictionsModel = predictions[predictions['Model'] == model]
        plt.plot(predictionsModel['Date'], predictionsModel['Close'], color=f'{color}', label=f'{model}')
    plt.plot(dataframe['Date'], dataframe['Close'], color='blue', label='Dados reais')
    plt.title(f'Previsão do Preço da Ação {ticker} usando IA ({predictionType})')
    plt.xlabel('Dias (Sequência)')
    plt.ylabel('Preço de Fechamento (R$)')
    plt.legend()
    plt.show()