import json
import pandas as pd

from plotting.plotter import plot

import matplotlib as plt
%matplotlib auto

with open("data.json") as f:
    data = json.load(f)

df = pd.DataFrame(data["GLD"]["bars"])
df = df.iloc[:-3]
df["time"] = pd.to_datetime(df["time"], unit="s")
df.set_index("time", inplace=True)
#print(df)

from signals.core.registry import SIGNALS
from signals.core.registry import get_signal

# ####To plot
# indicators = {
#     "atr": {"period": 14},
#     "ichimoku_cross": {},
#     "ssl": {},
#     "absolute_strength":{},
#     "aroon": {},
#     "wae": {},
# }
# signals = []
# for name, params in indicators.items():
#     signal = get_signal(name)(**params)
#     df = signal.calculate(df)
#     signals.append(signal)
# df.to_csv("data_with_indicators.csv")
# plot(df, signals)

# ####Signals on current candle
# signals = {
#     "ssl": get_signal("ssl")(),
#     "aroon": get_signal("aroon")(),
#     "absolute_strength": get_signal("absolute_strength")(),
# }

# for name, signal in signals.items():
#     df = signal.calculate(df)
#     result = signal.analyze(df)
#     print(f"{name}: {result}")

# # #### To back test
# atr = get_signal("atr")(period=14)
# df = atr.calculate(df)

# ssl = get_signal("ichimoku_cross")()
# # Calculate SSL values
# df = ssl.calculate(df)
# df.to_csv("data_with_indicators.csv")
# results = ssl.test(df)
# results["trades_detail"].to_csv("ssl_results.csv", index=False)
# print(results)