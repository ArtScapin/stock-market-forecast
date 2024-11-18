import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split as trainTestSplit
from providers.databaseConnection import getTickerData, saveStockMarketPredictionsOnDatabase


def analyzingDataWithRandomForest(ticker, predictionType):
    dataframe = getTickerData(ticker, "CLEAR")
    closingPrices = dataframe[['Close']].values

    scaledData, scaler = applyMinMaxScaling(closingPrices)

    randomForest, XTest = createAndTrainModel(scaledData)

    predictedPrices = makePredictions(randomForest, XTest, scaler, predictionType)

    predictedDates = dataframe[['Date']].values
    predictedDates = predictedDates[len(predictedDates) - len(predictedPrices):]
    save(predictedPrices, predictedDates, predictionType, ticker)


def applyMinMaxScaling(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaledData = scaler.fit_transform(data)
    return scaledData, scaler


def createSequences(data, lookBack):
    sequences, values = [], []
    for i in range(lookBack, len(data)):
        sequences.append(data[i - lookBack:i].flatten())
        values.append(data[i][0])
    return np.array(sequences), np.array(values)


def createAndTrainModel(data):
    lookBack = 60
    sequences, values = createSequences(data, lookBack)

    XTrain, XTest, yTrain, yTest = trainTestSplit(sequences, values, test_size=0.2, random_state=42)

    randomForest = RandomForestRegressor(n_estimators=100, random_state=42)
    randomForest.fit(XTrain, yTrain)

    return randomForest, XTest


def makePredictions(randomForest, XTest, scaler, predictionType):
    predictedPrices = []

    if predictionType == 1:
        predictedPrices = randomForest.predict(XTest)
    else:
        currentSequence = XTest[0].copy()
        for _ in range(len(XTest)):
            nextPred = randomForest.predict([currentSequence])[0]
            predictedPrices.append(nextPred)

            currentSequence = np.roll(currentSequence, -1)
            currentSequence[-1] = nextPred

    predictedPrices = np.array(predictedPrices).reshape(-1, 1)
    predictedPricesFull = scaler.inverse_transform(predictedPrices)

    return predictedPricesFull


def save(predictedPrices, predictedDates, predictionType, ticker):
    dataframe = pd.DataFrame({
        'Date': list(map(lambda x: x[0], predictedDates)),
        'Close': list(map(lambda x: x[0], predictedPrices)),
        'Model': "RandomForest",
        'PredictionType': predictionType
    })
    saveStockMarketPredictionsOnDatabase(dataframe, ticker)
