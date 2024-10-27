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
        prophet, testData = createAndTrainModel(dataframe)
        predictions = makePredictions(prophet, testData, scaler)
        totalPredictions = len(testData)
        predictionsDates = [predictions[['ds', 'yhat']].loc[0].values[0]]
        predictionsPrices = [predictions[['ds', 'yhat']].loc[0].values[1]]
        while len(predictionsDates) < totalPredictions:
            step = len(predictionsDates)
            prophet, testData = createAndTrainModel(dataframe, step)
            prediction = makePredictions(prophet, testData, scaler)
            predictionsDates.append(prediction[['ds', 'yhat']].loc[0].values[0])
            predictionsPrices.append(prediction[['ds', 'yhat']].loc[0].values[1])

        predictions = pandas.DataFrame({
            'ds': list(predictionsDates),
            'yhat': list(predictionsPrices)
        })
    else:
        prophet, testData = createAndTrainModel(dataframe)
        predictions = makePredictions(prophet, testData, scaler)

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

    return prophet, testData


def makePredictions(prophet, testData, scaler):
    predictDates = pandas.DataFrame({'ds': testData['ds']})

    predictedPrices = prophet.predict(predictDates)

    predictedPrices['yhat'] = scaler.inverse_transform(predictedPrices[['yhat']].values)

    return predictedPrices


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
