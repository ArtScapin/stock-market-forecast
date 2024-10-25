import logging
import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential

from providers.databaseConnection import getTickerData

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

def analyzingDataWithLSTM(ticker):
    dataframe = getTickerData(ticker)
    dataframe = dataframe[['Open', 'High', 'Low', 'Close', 'Volume']].values

    dataframe, scaler = applyMinMaxScaling(dataframe)

    model, XTest, yTest = createAndTrainModel(dataframe)

    predictedPrices, realPrices = makePredictions(model, XTest, yTest, scaler)

    plotPredictions(realPrices, predictedPrices, ticker)

    mse = model.evaluate(XTest, yTest)
    print(f'Mean Squared Error: {mse}')


def applyMinMaxScaling(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    return scaled_data, scaler


def createSequences(data, lookBack):
    X, y = [], []
    for i in range(lookBack, len(data)):
        X.append(data[i - lookBack:i])
        y.append(data[i])
    return np.array(X), np.array(y)


def createAndTrainModel(data):
    lookBack = round(len(data) * 0.8)
    X, y = createSequences(data, lookBack)

    trainSize = int(len(X) * 0.8)
    XTrain, XTest = X[:trainSize], X[trainSize:]
    yTrain, yTest = y[:trainSize], y[trainSize:]

    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(XTrain.shape[1], XTrain.shape[2])),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=5)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(XTrain, yTrain, epochs=50, batch_size=32)

    return model, XTest, yTest


def makePredictions(model, XTest, yTest, scaler):
    sequence = XTest[0]
    predictedPrices = []

    for _ in range(len(yTest)):
        prediction = model.predict(sequence.reshape(1, sequence.shape[0], sequence.shape[1]))
        predictedPrices.append(prediction[0])
        sequence = np.roll(sequence, -1, axis=0)
        sequence[-1] = prediction

    predictedPricesFull = scaler.inverse_transform(predictedPrices)
    yTestFull = scaler.inverse_transform(yTest)

    return predictedPricesFull, yTestFull


def plotPredictions(real, predicted, ticker):
    labels = ['Open', 'High', 'Low', 'Close', 'Volume']
    numVars = len(labels)

    plt.figure(figsize=(15, 3 * numVars))

    for i in range(numVars):
        plt.subplot(numVars, 1, i + 1)
        plt.plot(real[:, i], color='blue', label='Real')
        plt.plot(predicted[:, i], color='red', label='Previsão')
        plt.title(f'Comparação entre Dados Reais e Previstos com LSTM - {ticker} ({labels[i]})')
        plt.xlabel('Dias')
        plt.ylabel(labels[i])
        plt.legend()

    plt.tight_layout()
    plt.show()
