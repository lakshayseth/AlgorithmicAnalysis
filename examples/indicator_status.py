import json
import pandas as pd

with open("../data.json") as f:
    data = json.load(f)
df = pd.DataFrame(data["GLD"]["bars"])
df = df.iloc[:-3]
df["time"] = pd.to_datetime(df["time"], unit="s")
df.set_index("time", inplace=True)

from signals.core.registry import get_signal

####Signals on current candle
signals = {
    "ssl": get_signal("ssl")(),
    "absolute_strength": get_signal("absolute_strength")(),
    "aroon": get_signal("aroon")(),
    "ichimoku_cross": get_signal("ichimoku_cross")(),
    "ichimoku_cloud": get_signal("ichimoku_cloud")(),
}

for name, signal in signals.items():
    df = signal.calculate(df)
    result = signal.analyze(df)
    print(f"{name}: {result}")