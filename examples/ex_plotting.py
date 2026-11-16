from data.instrument import instrument

symbol = "AUDJPY"
exchange = "OANDA"
interval = "D"

info = instrument(symbol, exchange, interval)
df = info.data

indicators = {
    "absolute_strength":{},
    "aroon": {},
    "atr": {},
    #"ichimoku_cross": {},
    "ichimoku_cloud": {},
    #"kijunsen":{},
    "ssl": {},
    "wae": {},
}

from signals.core.registry import get_signal

signals = []
for name, params in indicators.items():
    signal = get_signal(name)(**params)
    df = signal.calculate(df)
    signals.append(signal)

import matplotlib as plt
%matplotlib auto

from graphing.plotter import plot
plot(df, signals, title="Example Plot", save=False, filename=None)