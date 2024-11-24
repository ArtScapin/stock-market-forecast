import math
import matplotlib.pyplot as plt
from providers.databaseConnection import getTickerData

def dayTradeSimulator(ticker):
    dataframe = getTickerData(ticker, "CLEAR")
    dataframe = dataframe[round(len(dataframe) * 0.8):].reset_index(drop=True)

    models = ["LSTM", "RandomForest", "Prophet"]
    percentages = {}
    all_balances = {}
    all_stock_options = {}

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
        total_predictions = 0
        daily_balance = [100000]
        daily_stock_options = [stockOptions]

        for i in range(1, len(dataframe) - 1):
            date = dataframe.loc[i, 'Date']
            nextDate = dataframe.loc[i + 1, 'Date']

            realCurrentValue = dataframe.loc[dataframe['Date'] == date, 'Close'].values[0]
            realNextValue = dataframe.loc[dataframe['Date'] == nextDate, 'Close'].values[0]

            predictionCurrent = predictions[predictions['Date'] == date]
            predictionNext = predictions[predictions['Date'] == nextDate]

            if not predictionCurrent.empty and not predictionNext.empty:
                predictionNextValue = predictionNext['Close'].values[0]

                hasRealValorized = realNextValue > realCurrentValue
                hasPredictionValorized = predictionNextValue > realCurrentValue

                total_predictions += 1
                if hasRealValorized == hasPredictionValorized:
                    green += 1
                else:
                    red += 1

                hasBigValorization = (predictionNextValue - realCurrentValue) / realCurrentValue > 0.025
                hasBigDisvalorization = (predictionNextValue - realCurrentValue) / realCurrentValue < -0.025

                if hasPredictionValorized and hasBigValorization:
                    newStockOptions = math.floor((balance / realCurrentValue) * 0.25)
                    stockOptions += newStockOptions
                    balance -= newStockOptions * realCurrentValue
                elif not hasPredictionValorized and hasBigDisvalorization:
                    stocksToSell = math.floor(stockOptions * 0.25)
                    balance += stocksToSell * realCurrentValue
                    stockOptions -= stocksToSell

            daily_balance.append(balance + stockOptions * realCurrentValue)
            daily_stock_options.append(stockOptions)

        finalValue = dataframe.loc[len(dataframe) - 1, 'Close']
        balance += stockOptions * finalValue

        accuracy = (green / total_predictions) * 100 if total_predictions > 0 else 0
        error_rate = (red / total_predictions) * 100 if total_predictions > 0 else 0
        percentages[model] = {"accuracy": accuracy, "error_rate": error_rate}
        all_balances[model] = daily_balance
        all_stock_options[model] = daily_stock_options

        print(f"Modelo: {model}, Balance final: {balance}, Acertos: {accuracy:.2f}%, Erros: {error_rate:.2f}%")

    x = range(len(models))
    width = 0.1
    fig, ax = plt.subplots(figsize=(12, 6))

    accuracy_values = [percentages[model]["accuracy"] for model in models]
    error_values = [percentages[model]["error_rate"] for model in models]

    ax.bar([p - width / 2 for p in x], accuracy_values, width=width, label='Acertos', color='green')
    ax.bar([p + width / 2 for p in x], error_values, width=width, label='Erros', color='red')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_xlabel('Modelos')
    ax.set_ylabel('Porcentagem (%)')
    ax.set_title(f'Comparação de Acertos e Erros por Modelo ({ticker})')
    ax.legend()

    plt.show()

    plt.figure(figsize=(12, 6))
    for model, daily_balance in all_balances.items():
        color = "green" if model == 'LSTM' else "red" if model == 'Prophet' else "orange"
        plt.plot(daily_balance, label=model, color=color)

    plt.xlabel('Dias')
    plt.ylabel('Saldo')
    plt.title(f'Variação do Saldo Diário por Modelo ({ticker})')
    plt.legend()
    plt.show()
