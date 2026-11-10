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

symbol = "NZDJPY"
exchange = "OANDA"
interval = "D"

info = instrument(symbol, exchange, interval)
df = info.data

from signals.core.registry import get_signal

# #### To back test
atr = get_signal("atr")(period=14)
df = atr.calculate(df)

ssl = get_signal("ssl")()
# Calculate SSL values
df = ssl.calculate(df)

results = ssl.test(df)
results["trades_detail"].to_csv("backtest_indicator.csv", index=False)
print(results)