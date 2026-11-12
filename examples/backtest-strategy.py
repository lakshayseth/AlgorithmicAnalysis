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

symbol = "NZDCHF"
exchange = "OANDA"
interval = "D"

info = instrument(symbol, exchange, interval)
df = info.data.iloc[:-1].copy()

from signals.core.registry import get_signal
from strategies.nnfx import NNFX 
from strategies.ichimoku import ICHIMOKU
import pandas as pd

baseline = get_signal("kijunsen")()
c1 = get_signal("ssl")()
c2 = get_signal("absolute_strength")()
volume = get_signal("wae")()
atr = get_signal("atr")(period=14)
nnfx = NNFX(
    baseline=baseline,
    c1=c1,
    c2=c2,
    volume=volume,
    atr=atr
)
result = nnfx.analyze(df)
print(f"NNFX: {result}")
#print(nnfx.status(df))

results = nnfx.backtest(df)
# Convert trade dictionaries into separate columns
trades_df = pd.json_normalize(results["trades_detail"])
# Export to CSV
trades_df.to_csv("backtest_strategy.csv", index=False)
#print(results)

ichm = get_signal("ichimoku_cloud")()
ichimoku = ICHIMOKU(ichm, atr)
result = ichimoku.analyze(df)
print(f"ICHIMOKU: {result}")
resutls = ichimoku.backtest(df)
# Convert trade dictionaries into separate columns
trades_df = pd.json_normalize(results["trades_detail"])
# Export to CSV
trades_df.to_csv("backtest_strategy.csv", index=False)
print(results)



