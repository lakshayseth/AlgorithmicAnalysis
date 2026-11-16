from data.instrument import instrument

symbol = "USDJPY"
exchange = "OANDA"
interval = "D"

info = instrument(symbol, exchange, interval)
df = info.data

from signals.core.registry import get_signal

atr = get_signal("atr")(period=14)
df = atr.calculate(df)

signal = get_signal("ichimoku_cloud")()
# Calculate SSL values
data = signal.calculate(df)

results = signal.backtest(data)
results["trades_detail"].to_csv("backtest_indicator.csv", index=False)
print(results)
