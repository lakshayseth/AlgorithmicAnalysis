from signals.core.registry import get_signal
from strategies.nnfx import NNFX
import pandas as pd

####
#### EDIT THIS 
import json
with open("data.json") as f:
    data = json.load(f)
df = pd.DataFrame(data["GLD"]["bars"])
df = df.iloc[:-3]
####
####

df["time"] = pd.to_datetime(df["time"], unit="s")
df.set_index("time", inplace=True)

c1 = get_signal("ssl")()
c2 = get_signal("absolute_strength")()
volume = get_signal("wae")()
baseline = get_signal("kijunsen")()
atr = get_signal("atr")(period=14)

nnfx = NNFX(
    c1=c1,
    c2=c2,
    volume=volume,
    baseline=baseline,
    atr=atr
)

result = nnfx.analyze(df)

print(result)