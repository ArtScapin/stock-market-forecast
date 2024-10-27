import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from providers.databaseConnection import getTickerData, saveStockMarketPredictionsOnDatabase


def analyzingDataWithRandomForest(ticker, predictionType):
    dataframe = getTickerData(ticker)
    closingPrices = dataframe[['Close']].values

    scaledData, scaler = applyMinMaxScaling(closingPrices)

    model, X_test = createAndTrainModel(scaledData)

    predictedPrices = makePredictions(model, X_test, scaler, predictionType)

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

    X_train, X_test, y_train, y_test = train_test_split(sequences, values, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model, X_test


def makePredictions(model, X_test, scaler, predictionType):
    predictedPrices = model.predict(X_test)

    if predictionType == 1:
        for i in range(1, len(X_test)):
            next_pred = model.predict([X_test[i]])
            predictedPrices = np.append(predictedPrices, next_pred)

    predictedPrices = predictedPrices.reshape(-1, 1)
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