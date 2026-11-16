import pandas as pd
import mplfinance as mpf
from ..core.base import Signal

class ICHIMOKU_CROSS(Signal):

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
        return df

    @property
    def plot_panel(self):
        return "price"
    
    def plot(self, df, panel):
        return [mpf.make_addplot(df["Tankan_sen"], panel=panel, color='purple', width=1),
            mpf.make_addplot(df["Kijun_sen"], panel=panel, color="blue", width=1),]
    
    def get_state(self, df):
        diff = df["Tankan_sen"] - df["Kijun_sen"]
        state = pd.Series(float("nan"), index=df.index)
        state.loc[diff > 0] = 1
        state.loc[diff < 0] = -1
        state.loc[diff == 0] = 0
        return state
    
    def backtest(self, df):
        return self.test(df)
    
    def value(self, df):
        return df["Tankan_sen"].iloc[-1], df["Kijun_sen"].iloc[-1]