import pandas
from sklearn.metrics import mean_squared_error as MeanSquaredError
from sklearn.preprocessing import MinMaxScaler
from providers.databaseConnection import getAvaliableTikers, getTickerData, saveMSEOnDatabase

def calculateMSE():
    tickers = getAvaliableTikers('CLEAR')
    for ticker in tickers:
        for predictionType in [1, 2]:
            dataframe = getTickerData(ticker, "CLEAR")
            predictions = getTickerData(ticker, "PREV")
            predictions = predictions[predictions['PredictionType'] == predictionType]
            dataframe = dataframe[int(len(dataframe) * 0.8):]
            predictionType = 'daily' if predictionType == 1 else 'period'

            scaler = MinMaxScaler()

            dataframe[['Close']] = scaler.fit_transform(dataframe[['Close']])

            results = []
            for model in ['LSTM', 'Prophet', 'RandomForest']:
                predictionsModel = predictions[predictions['Model'] == model]

                predictionsModel.loc[:, 'Close'] = scaler.transform(predictionsModel[['Close']])

                meanSquaredError = MeanSquaredError(dataframe['Close'], predictionsModel['Close'])

                results.append({
                    "Model": model,
                    "Ticker": ticker,
                    "PredictionType": predictionType,
                    "MSE": meanSquaredError * 100
                })

            saveMSEOnDatabase(pandas.DataFrame(results))
