import json
import pandas as pd

from graphing.plotter import plot

with open("../data.json") as f:
    data = json.load(f)
df = pd.DataFrame(data["GLD"]["bars"])
df = df.iloc[:-3]
df["time"] = pd.to_datetime(df["time"], unit="s")
df.set_index("time", inplace=True)
# print(df)

plot
indicators = {
    "atr": {"period": 14},
    "ichimoku_cloud": {},
    "ssl": {},
    "absolute_strength":{},
    "aroon": {},
    "wae": {},
}

from signals.core.registry import get_signal

signals = []
for name, params in indicators.items():
    signal = get_signal(name)(**params)
    df = signal.calculate(df)
    signals.append(signal)
# df.to_csv("data_with_indicators.csv")

import matplotlib as plt
%matplotlib auto

plot(df, signals)