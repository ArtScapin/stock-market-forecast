import pandas
from prophet import Prophet
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from providers.databaseConnection import getTickerData, saveStockMarketPredictionsOnDatabase


def analyzingDataWithProphet(ticker, predictionType):
    dataframe = getTickerData(ticker)
    dataframe = dataframe[['Close', 'Date']].reset_index()
    dataframe.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)

    dataframe, scaler = applyMinMaxScaling(dataframe)

    if predictionType == 1:
        prophet, trainData, testData = createAndTrainModel(dataframe)
        predictions = makePredictions(prophet, testData, scaler, predictionType)
        totalPredictions = len(testData)
        predictionsDates = [predictions[['ds', 'yhat']].loc[0].values[0]]
        predictionsPrices = [predictions[['ds', 'yhat']].loc[0].values[1]]
        while len(predictionsDates) < totalPredictions:
            step = len(predictionsDates)
            prophet, trainData, testData = createAndTrainModel(dataframe, step)
            prediction = makePredictions(prophet, testData, scaler, predictionType)
            predictionsDates.append(prediction[['ds', 'yhat']].loc[0].values[0])
            predictionsPrices.append(prediction[['ds', 'yhat']].loc[0].values[1])

        predictions = pandas.DataFrame({
            'ds': list(predictionsDates),
            'yhat': list(predictionsPrices)
        })
    else:
        prophet, trainData, testData = createAndTrainModel(dataframe)
        predictions = makePredictions(prophet, testData, scaler, predictionType)

    save(predictions, ticker, predictionType)


def applyMinMaxScaling(dataframe):
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataframe['y'] = scaler.fit_transform(dataframe[['y']])
    return dataframe, scaler

def createAndTrainModel(dataframe, step = 0):
    trainSize = int(len(dataframe) * 0.8) + step
    trainData = dataframe[:trainSize]
    testData = dataframe[trainSize:].copy()

    prophet = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.5
    )

    prophet.fit(trainData)

    return prophet, trainData, testData

def makePredictions(prophet, testData, scaler, predictionType):
    predictDates = pandas.DataFrame({'ds': testData['ds']})

    predictedPrices = prophet.predict(predictDates)

    predictedPrices['yhat'] = scaler.inverse_transform(predictedPrices[['yhat']].values)

    return predictedPrices

def plotPredictions(historicalData, testData, predictedPrices, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(historicalData['day'], historicalData['y'], color='green', label='Dados Reais (Treino)')
    plt.plot(testData['day'], testData['y'], color='blue', label='Dados Reais (Teste)')
    plt.plot(predictedPrices['day'], predictedPrices['yhat'], color='red', label='Previsões')
    plt.title(f'Previsão do Preço da Ação {ticker} usando Prophet')
    plt.xlabel('Dias (Sequência)')
    plt.ylabel('Preço de Fechamento (R$)')
    plt.legend()
    plt.show()


def save(predictions, ticker, predictionType):
    predictedDates = predictions[['ds']].values
    predictedPrices = predictions[['yhat']].values
    dataframe = pandas.DataFrame({
        'Date': list(map(lambda x: x[0], predictedDates)),
        'Close': list(map(lambda x: x[0], predictedPrices)),
        'Model': "Prophet",
        'PredictionType': predictionType
    })
    saveStockMarketPredictionsOnDatabase(dataframe, ticker)

analyzingDataWithProphet("PETR4", 1)
