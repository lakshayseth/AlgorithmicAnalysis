import pandas as pd
import mplfinance as mpf
from ..core.base import Signal


class ICHIMOKU_CLOUD(Signal):

    def __init__(self, conversion_line=9, base_line=26, leading_span_b=52, lagging_span=26, **kwargs):
        super().__init__(conversion_line=conversion_line, base_line=base_line,
                         leading_span_b=leading_span_b, lagging_span=lagging_span, **kwargs)
        self.conversion_line = conversion_line
        self.base_line = base_line
        self.leading_span_b = leading_span_b
        self.lagging_span = lagging_span

    def calculate(self, df):
        df["Tankan_sen"] = (df["high"].rolling(self.conversion_line).max() + df["low"].rolling(self.conversion_line).min()) / 2
        df["Kijun_sen"] = (df["high"].rolling(self.base_line).max() + df["low"].rolling(self.base_line).min()) / 2
        df["Senkou_Span_A"] = ((df["Tankan_sen"] + df["Kijun_sen"]) / 2).shift(self.lagging_span)
        df["Senkou_Span_B"] = ((df["high"].rolling(self.leading_span_b).max() + df["low"].rolling(self.leading_span_b).min()) / 2).shift(self.lagging_span)
        df["Chikou_Span"] = df["close"].shift(-self.lagging_span)
        return df
    
    @property
    def plot_panel(self):
        return "price"
    
    def plot(self, df, panel):
        return [mpf.make_addplot(df["Tankan_sen"], panel=panel, color='purple', width=1),
            mpf.make_addplot(df["Kijun_sen"], panel=panel, color="blue", width=1),
            mpf.make_addplot(df["Chikou_Span"], panel=panel, color='yellow', width=1),
            mpf.make_addplot(df["Senkou_Span_A"], panel=panel, color="black", width=1),
            mpf.make_addplot(df["Senkou_Span_B"], panel=panel, color="black", width=1)]
    
    def test(self, df):
        atr_start = df["atr"].first_valid_index()
    
        if atr_start is None:
            return None
    
        test_df = df.loc[atr_start:].copy()
    
        test_df = test_df.dropna(
            subset=[
                "Tankan_sen",
                "Kijun_sen",
                "Senkou_Span_A",
                "Senkou_Span_B",
                "atr"
            ])
    
        cloud_top = test_df[["Senkou_Span_A", "Senkou_Span_B"]].max(axis=1)
    
        cloud_bottom = test_df[["Senkou_Span_A", "Senkou_Span_B"]].min(axis=1)
    
        # Your bullish condition
        bullish = ((test_df["Tankan_sen"] >= test_df["Kijun_sen"]) & (test_df["close"] >= cloud_top))
    
        # Your bearish condition
        bearish = ((test_df["Tankan_sen"] < test_df["Kijun_sen"]) & (test_df["close"] < cloud_bottom))
    
        # Only trigger when condition FIRST becomes true
        bull_signal = bullish & ~bullish.shift(1, fill_value=False)
        bear_signal = bearish & ~bearish.shift(1, fill_value=False)
    
        return self.backtest(test_df, bull_signal, bear_signal)

    def analyze(self, df):
        if len(df) < 2:
            return None

        c, p = df.iloc[-1], df.iloc[-2]

        cols = ["Tankan_sen", "Kijun_sen", "Senkou_Span_A", "Senkou_Span_B"]
        if any(pd.isna(c[x]) or pd.isna(p[x]) for x in cols):
            return None

        ctop = max(c["Senkou_Span_A"], c["Senkou_Span_B"])
        cbottom = min(c["Senkou_Span_A"], c["Senkou_Span_B"])
        ptop = max(p["Senkou_Span_A"], p["Senkou_Span_B"])
        pbottom = min(p["Senkou_Span_A"], p["Senkou_Span_B"])

        price_up = p["close"] < ptop and c["close"] >= ctop
        price_down = p["close"] >= pbottom and c["close"] < cbottom

        tenkan_up = p["Tankan_sen"] < p["Kijun_sen"] and c["Tankan_sen"] >= c["Kijun_sen"]
        tenkan_down = p["Tankan_sen"] >= p["Kijun_sen"] and c["Tankan_sen"] < c["Kijun_sen"]

        if (price_up and c["Tankan_sen"] >= c["Kijun_sen"]) or \
           (tenkan_up and c["close"] >= ctop):
            return "BUY"

        if (price_down and c["Tankan_sen"] < c["Kijun_sen"]) or \
           (tenkan_down and c["close"] < cbottom):
            return "SELL"

        return None
    
    def state(self, df):
        if len(df) < 1:
            return None
        c = df.iloc[-1]
        cols = ["Tankan_sen", "Kijun_sen", "Senkou_Span_A", "Senkou_Span_B", "close"]
        if any(pd.isna(c[x]) for x in cols):
            return None
        ctop = max(c["Senkou_Span_A"], c["Senkou_Span_B"])
        cbottom = min(c["Senkou_Span_A"],c["Senkou_Span_B"])
        bullish = (c["close"] >= ctop and c["Tankan_sen"] >= c["Kijun_sen"])
        bearish = (c["close"] < cbottom and c["Tankan_sen"] < c["Kijun_sen"])
    
        if bullish:
            return "BUY"
        if bearish:
            return "SELL"
    
        return None

    def value(self, df):
        raise NotImplementedError