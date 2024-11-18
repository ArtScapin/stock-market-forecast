import math
import matplotlib.pyplot as plt
from providers.databaseConnection import getTickerData

def dayTradeSimulator(ticker):
    dataframe = getTickerData(ticker, "CLEAR")
    dataframe = dataframe[round(len(dataframe) * 0.8):].reset_index(drop=True)

    models = ["LSTM", "RandomForest", "Prophet"]
    greens = []
    reds = []
    all_balances = {}

    for model in models:
        predictions = getTickerData(ticker, "PREV")
        predictions = predictions[(predictions['PredictionType'] == 1) & (predictions['Model'] == model)].reset_index(
            drop=True)

        balance = 100000
        initialValue = dataframe.loc[0, 'Close']
        stockOptions = math.floor(balance / initialValue)
        balance -= stockOptions * initialValue

        green = 0
        red = 0
        daily_balance = [100000]

        for i in range(1, len(dataframe) - 1):
            date = dataframe.loc[i, 'Date']
            nextDate = dataframe.loc[i + 1, 'Date']

            realCurrentValue = dataframe.loc[dataframe['Date'] == date, 'Close'].values[0]
            realNextValue = dataframe.loc[dataframe['Date'] == nextDate, 'Close'].values[0]

            predictionCurrent = predictions[predictions['Date'] == date]
            predictionNext = predictions[predictions['Date'] == nextDate]

            if not predictionCurrent.empty and not predictionNext.empty:
                predictionNextValue = predictionNext['Close'].values[0]
                predictionNextValue = predictionNext['Close'].values[0]

                hasRealValorized = realNextValue > realCurrentValue
                hasPredictionValorized = predictionNextValue > realCurrentValue

                if hasRealValorized == hasPredictionValorized:
                    green += 1
                else:
                    red += 1

                hasBigValorization = (predictionNextValue - realCurrentValue) / realCurrentValue > 0.05
                hasBigDisvalorization = (predictionNextValue - realCurrentValue) / realCurrentValue < -0.05

                if hasPredictionValorized and hasBigValorization:
                    newStockOptions = math.floor(balance / realCurrentValue)
                    stockOptions += newStockOptions
                    balance -= newStockOptions * realCurrentValue
                elif not hasPredictionValorized and hasBigDisvalorization:
                    balance += stockOptions * realCurrentValue
                    stockOptions = 0

            daily_balance.append(balance + stockOptions * realCurrentValue)

        finalValue = dataframe.loc[len(dataframe) - 1, 'Close']
        balance += stockOptions * finalValue

        greens.append(green)
        reds.append(red)
        all_balances[model] = daily_balance

        print(f"Modelo: {model}, Balance final: {balance}, Green: {green}, Red: {red}")

    x = range(len(models))
    width = 0.4
    fig, ax = plt.subplots()
    ax.bar([p - width / 2 for p in x], greens, width=width, label='Green', color='green')
    ax.bar([p + width / 2 for p in x], reds, width=width, label='Red', color='red')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_xlabel('Modelos')
    ax.set_ylabel('Contagem')
    ax.set_title(f'Comparação de Green e Red por Modelo ({ticker})')
    ax.legend()

    plt.figure()
    for model, daily_balance in all_balances.items():
        color = "green" if model == 'LSTM' else "red" if model == 'Prophet' else "orange"
        plt.plot(daily_balance, label=model, color=color)

    plt.xlabel('Dias')
    plt.ylabel('Saldo')
    plt.title(f'Variação do Saldo Diário por Modelo ({ticker})')
    plt.legend()
    plt.show()
