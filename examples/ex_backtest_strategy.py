from data.instrument import instrument
from data.tickers import *

from signals.core.registry import get_signal
from strategies.ichimoku import ICHIMOKU
from strategies.nnfx import NNFX 
import pandas as pd

forex = ["USDJPY"]

for symbol in forex:
    print(symbol)

    exchange = "OANDA"
    interval = "D"
    
    info = instrument(symbol, exchange, interval)
    df = info.data#.iloc[:-1].copy()
    df.to_csv('data.csv')
    atr = get_signal("atr")(period=14)
    ichm = get_signal("ichimoku_cloud")()
    ichimoku = ICHIMOKU(ichm, atr)
    
    res1 = ichimoku.backtest(df)
    trades_df = pd.json_normalize(res1["trades_detail"])
    # Export to CSV
    trades_df.to_csv(f"ichimoku_strategy_{symbol}.csv", index=False)
    print(f"Ichimoku: {res1}")
    
    # baseline = get_signal("kijunsen")()
    # c1 = get_signal("ssl")()
    # c2 = get_signal("absolute_strength")()
    # volume = get_signal("wae")()
    # nnfx = NNFX(
    #     baseline=baseline,
    #     c1=c1,
    #     c2=c2,
    #     volume=volume,
    #     atr=atr
    # )
    # res2 = nnfx.backtest(df)
    # trades_df = pd.json_normalize(res2["trades_detail"])
    # # Export to CSV
    # trades_df.to_csv(f"nnfx_strategy_{symbol}.csv", index=False)
    # #print(res2)