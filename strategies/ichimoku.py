import pandas as pd


class ICHIMOKU:

    def __init__(self, ichimoku, atr):
        self.ichimoku = ichimoku
        self.atr = atr

    def calculate(self, df):
        df = self.ichimoku.calculate(df)
        df = self.atr.calculate(df)
        return df

    def analyze(self, df):
        if len(df) < 2:
            return None

        df = self.calculate(df)

        signal = self.ichimoku.analyze(df)

        if signal == "BUY":
            return self.trade_result(df, "Ichimoku - Buy", "BUY")

        if signal == "SELL":
            return self.trade_result(df, "Ichimoku - Sell", "SELL")

        return None

    def trade_result(self, df, signal, direction):
        price = df["close"].iloc[-1]
        atr = self.atr.value(df)

        if pd.isna(price) or pd.isna(atr):
            return None

        if direction == "BUY":
            take_profit = price + atr
            stop_loss = price - (atr * 1.5)
        else:
            take_profit = price - atr
            stop_loss = price + (atr * 1.5)

        return {
            "signal": signal,
            "direction": direction,
            "price": round(price,2),
            "atr": round(atr,2),
            "take_profit": round(take_profit,2),
            "stop_loss": round(stop_loss,2),
        }
