import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from providers.databaseConnection import getTickerData


def analyzingDataWithLSTM(ticker):
    dataframe = getTickerData(ticker)
    dataframe = dataframe[['Open', 'High', 'Low', 'Close', 'Volume']].values

    dataframe, scaler = applyMinMaxScaling(dataframe)

    model, XTest, yTest = createAndTrainModel(dataframe)

    predictedClosePrices, realClosePrices = makePredictions(model, XTest, yTest, scaler, dataframe.shape[1])

    plotPredictions(realClosePrices, predictedClosePrices)

    mse = model.evaluate(XTest, yTest)
    print(f'Mean Squared Error: {mse}')


def applyMinMaxScaling(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    return scaled_data, scaler


def createSequences(data, look_back):
    X, y = [], []
    for i in range(look_back, len(data)):
        X.append(data[i - look_back:i])
        y.append(data[i, 3])
    return np.array(X), np.array(y)


def createAndTrainModel(data):
    look_back = 60
    X, y = createSequences(data, look_back)

    train_size = int(len(X) * 0.8)
    XTrain, XTest = X[:train_size], X[train_size:]
    yTrain, yTest = y[:train_size], y[train_size:]

    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(XTrain.shape[1], XTrain.shape[2])),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(XTrain, yTrain, epochs=50, batch_size=32)

    return model, XTest, yTest


def makePredictions(model, XTest, yTest, scaler, n_features):
    predictedPrices = model.predict(XTest)

    predictedPricesFull = np.zeros((predictedPrices.shape[0], n_features))
    predictedPricesFull[:, 3] = predictedPrices.flatten()
    predictedPricesFull = scaler.inverse_transform(predictedPricesFull)
    predictedClosePrices = predictedPricesFull[:, 3]

    yTestFull = np.zeros((yTest.shape[0], n_features))
    yTestFull[:, 3] = yTest
    yTestFull = scaler.inverse_transform(yTestFull)
    realClosePrices = yTestFull[:, 3]

    return predictedClosePrices, realClosePrices


def plotPredictions(real, predicted):
    plt.figure(figsize=(14, 5))
    plt.plot(real, color='blue', label='Preço Real')
    plt.plot(predicted, color='red', label='Preço Previsto')
    plt.title('Comparação entre Preços Reais e Previstos')
    plt.xlabel('Dias')
    plt.ylabel('Preço de Fechamento')
    plt.legend()
    plt.show()
