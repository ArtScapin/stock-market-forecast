import numpy as np
import pandas
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential

from providers.databaseConnection import getTickerData, saveStockMarketPredictionsOnDatabase


def analyzingDataWithLSTM(ticker, predictionType):
    dataframe = getTickerData(ticker)
    closingPrices = dataframe[['Close']].values

    scaledData, scaler = applyMinMaxScaling(closingPrices)

    lstm, XTest, yTest = createAndTrainModel(scaledData)

    predictedPrices, realPrices = makePredictions(lstm, XTest, yTest, scaler, predictionType)

    predictedDates = dataframe[['Date']].values
    predictedDates = predictedDates[len(predictedDates)-len(predictedPrices):]
    save(predictedPrices, predictedDates, predictionType, ticker)


def applyMinMaxScaling(dataframe):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaledData = scaler.fit_transform(dataframe)
    return scaledData, scaler


def createSequences(data, lookBack):
    sequences, values = [], []
    for i in range(lookBack, len(data)):
        sequences.append(data[i - lookBack:i])
        values.append(data[i])
    return np.array(sequences), np.array(values)


def createAndTrainModel(dataframe):
    lookBack = 60
    sequences, values = createSequences(dataframe, lookBack)

    trainSize = int(len(sequences) * 0.8)
    sequencesTrain, sequencesTest = sequences[:trainSize], sequences[trainSize:]
    valuesTrain, valuesTest = values[:trainSize], values[trainSize:]

    lstm = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(sequencesTrain.shape[1], sequencesTrain.shape[2])),
        Dropout(0.3),
        LSTM(units=50, return_sequences=False),
        Dropout(0.3),
        Dense(units=1)
    ])

    lstm.compile(optimizer='adam', loss='mean_squared_error')

    lstm.fit(sequencesTrain, valuesTrain, epochs=50, batch_size=32)

    return lstm, sequencesTest, valuesTest


def makePredictions(model, XTest, yTest, scaler, predictionType):
    predictedPrices = []
    if predictionType == 1:
        sequence = XTest[0]
        for _ in range(len(yTest)):
            prediction = model.predict(sequence.reshape(1, sequence.shape[0], sequence.shape[1]))
            predictedPrices.append(prediction[0])
            sequence = np.roll(sequence, -1, axis=0)
            sequence[-1] = prediction
    else:
        predictedPrices = model.predict(XTest)

    predictedPricesFull = scaler.inverse_transform(predictedPrices)
    yTestFull = scaler.inverse_transform(yTest)

    return predictedPricesFull, yTestFull


def save(predictedPrices, predictedDates, predictionType, ticker):
    dataframe = pandas.DataFrame({
        'Date': list(map(lambda x: x[0], predictedDates)),
        'Close': list(map(lambda x: x[0], predictedPrices)),
        'Model': "LSTM",
        'PredictionType': predictionType
    })
    saveStockMarketPredictionsOnDatabase(dataframe, ticker)
