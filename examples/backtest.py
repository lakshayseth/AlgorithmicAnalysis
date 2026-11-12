# ####To import data from JSON:
# import json
# import pandas as pd
# with open("../data.json") as f:
#     data = json.load(f)
# df = pd.DataFrame(data["GLD"]["bars"])
# df["time"] = pd.to_datetime(df["time"], unit="s")
# df.set_index("time", inplace=True)
# ####

from data.instrument import instrument
from data.tickers import *

symbol = "AUDCHF"
exchange = "OANDA"
interval = "D"

info = instrument(symbol, exchange, interval)
df = info.data.iloc[:-1].copy()

from signals.core.registry import get_signal

# #### To back test
atr = get_signal("atr")(period=14)
df = atr.calculate(df)

icloud = get_signal("ichimoku_cross")()
# Calculate SSL values
df = icloud.calculate(df)

results = icloud.test(df)
results["trades_detail"].to_csv("backtest_indicator.csv", index=False)
print(results)