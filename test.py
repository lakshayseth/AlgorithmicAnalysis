from signals.core.registry import get_signal
from strategies.nnfx import NNFX 
from strategies.ichimoku import ICHIMOKU
import pandas as pd

####
#### EDIT THIS 
import json
with open("data.json") as f:
    data = json.load(f)
df = pd.DataFrame(data["GLD"]["bars"])
####
####

df["time"] = pd.to_datetime(df["time"], unit="s")
df.set_index("time", inplace=True)

df = df.iloc[:-3]
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

df = df.iloc[:-4]
ichm = get_signal("ichimoku_cloud")()
ichimoku = ICHIMOKU(ichm, atr)
result = ichimoku.analyze(df)
print(f"ICHIMOKU: {result}")
