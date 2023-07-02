from datetime import date, timedelta
import nsepy
import json

import pandas as pd
import pyfolio as pf

all_data = []

with open('listOfStocks.json') as f:
    data = json.load(f)

    for item in data["data"]["IndexList"]:
        symbol = item["symbol"]
        end_date = date.today()
        start_date = end_date - timedelta(days=3 * 365)
        historical_data = nsepy.get_history(symbol, index=True, start=start_date, end=end_date)
        all_data.append(historical_data)


    data_df = pd.DataFrame(all_data)

    data_df.to_csv("stock_data.csv")



class BacktestStrategy:
    def __init__(self, data, atr_multiplier):
        self.data = data
        self.atr_multiplier = atr_multiplier
        self.portfolio = []

    def get_top5_performers(self, weekly_data):
        rolling_returns = weekly_data.rolling(window=52).apply(lambda x: (x[-1] / x[0]) - 1)
        sorted_returns = rolling_returns.iloc[-1].sort_values(ascending=False)
        top5_performers = sorted_returns[:5].index.tolist()
        return top5_performers

    def calculate_stop_loss(self, weekly_data):
        atr = weekly_data['High'] - weekly_data['Low']
        stop_loss = atr * self.atr_multiplier
        return stop_loss

    def rebalance_portfolio(self, top5_performers):
        self.portfolio = [stock for stock in self.portfolio if stock in top5_performers]
        self.portfolio += top5_performers[len(self.portfolio):]

    def execute_trades(self, weekly_data, stop_loss):
        for stock in self.portfolio:
            entry_price = weekly_data[stock].iloc[-1]
            stop_loss_level = entry_price - stop_loss[stock]

    def run_backtest(self):
        for i in range(52, len(self.data)):
            weekly_data = self.data.iloc[i - 52:i]
            top5_performers = self.get_top5_performers(weekly_data)
            stop_loss = self.calculate_stop_loss(weekly_data)

            self.rebalance_portfolio(top5_performers)
            self.execute_trades(weekly_data, stop_loss)

        returns = pd.Series(self.portfolio).pct_change().fillna(0)
        positions = pd.Series(self.portfolio, index=self.data.index[-len(returns):])
        pf.create_full_tear_sheet(returns, positions=positions)


data = pd.read_csv('stock_data.csv', index_col='Date', parse_dates=True)

strategy = BacktestStrategy(data, atr_multiplier=2)
strategy.run_backtest()