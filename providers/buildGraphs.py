import pandas
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error as MeanSquaredError

from providers.databaseConnection import getTickerData, saveMSEOnDatabase


def buildGraph(ticker, predictionType, models):
    dataframe = getTickerData(ticker, "CLEAR")
    predictions = getTickerData(ticker, "PREV")
    predictions = predictions[predictions['PredictionType'] == predictionType]
    dataframe = dataframe[int(len(dataframe) * 0.8):]
    predictionType = 'daily' if predictionType == 1 else 'period'

    plt.figure(figsize=(12, 6))
    results = []
    for model in models:
        predictionsModel = predictions[predictions['Model'] == model]
        dataframeMergedWithPredictions = pandas.merge(dataframe, predictionsModel, on='Date', suffixes=('Real', 'Prev'))
        meanSquaredError = MeanSquaredError(dataframeMergedWithPredictions['CloseReal'], dataframeMergedWithPredictions['ClosePrev'])
        results.append({
            "Model": model,
            "Ticker": ticker,
            "PredictionType": predictionType,
            "MSE": meanSquaredError
        })
        color = "green" if model == 'LSTM' else "red" if model == 'Prophet' else "orange"
        plt.plot(predictionsModel['Date'], predictionsModel['Close'], color=f'{color}', label=f'{model}')
    plt.plot(dataframe['Date'], dataframe['Close'], color='blue', label='Dados reais')
    plt.title(f'Previsão do Preço da Ação {ticker} usando IA ({predictionType})')
    plt.xlabel('Dias (Sequência)')
    plt.ylabel('Preço de Fechamento (R$)')
    plt.legend()
    plt.show()

    saveMSEOnDatabase(pandas.DataFrame(results))
