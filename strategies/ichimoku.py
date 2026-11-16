import pandas as pd

class ICHIMOKU:

    def __init__(self, ich, atr):
        self.ich = ich
        self.atr = atr
        
    def calculate(self, df):
        df = df.copy()
        df = self.ich.calculate(df)
        df = self.atr.calculate(df)
        return df
    
    def execute(self, df):
        if len(df) < 2:
            return None
        df = self.calculate(df)
        state = self.ich.get_state(df)
        previous_state = state.shift(1)

        signals = pd.Series(None, index=df.index, dtype=object)

        bullish = (state == 1) & (previous_state != 1) & previous_state.notna()
        bearish = (state == -1) & (previous_state != -1) & previous_state.notna()
        
        signals.loc[bullish] = "Buy"
        signals.loc[bearish] = "Sell"
        result = signals.iloc[-1]
        return None if pd.isna(result) else result
    
    def backtest(self, df):
        trades_detail = []
        i = 1
        while i < len(df) - 1:
            current_df = self.calculate(df.iloc[:i + 1].copy())
            result = self.execute(current_df)
            if result is None:
                i += 1
                continue
            direction = result
            entry_time = current_df.index[-1]
            entry_price = current_df["close"].iloc[-1]
            atr_value = self.atr.value(current_df)
            if pd.isna(atr_value) or atr_value <= 0:
                i += 1
                continue
            if direction == "Buy":
                take_profit = entry_price + atr_value
                stop_loss = entry_price - (1.5 * atr_value)
            else:
                take_profit = entry_price - atr_value
                stop_loss = entry_price + (1.5 * atr_value)
            exit_time = None
            exit_price = None
            trade_result = None
            net = 0
            for j in range(i + 1, len(df)):
                candle = df.iloc[j]
                high = candle["high"]
                low = candle["low"]
                # Check TP and SL
                if direction == "Buy":
                    tp_hit = high >= take_profit
                    sl_hit = low <= stop_loss
                else:
                    tp_hit = low <= take_profit
                    sl_hit = high >= stop_loss
                # Both TP and SL hit
                if tp_hit and sl_hit:
                    exit_time = df.index[j]
                    exit_price = stop_loss
                    trade_result = "LOSS"
                    net = -1.5
                    break
                # Take profit
                elif tp_hit:
                    exit_time = df.index[j]
                    exit_price = take_profit
                    trade_result = "WIN"
                    net = 1
                    break
                # Stop loss
                elif sl_hit:
                    exit_time = df.index[j]
                    exit_price = stop_loss
                    trade_result = "LOSS"
                    net = -1.5
                    break
                # Check Ichimoku state change
                candle_df = self.calculate(df.iloc[:j + 1].copy())
                state = self.ich.get_state(candle_df).iloc[-1]
                if pd.isna(state):
                    continue
                if direction == "Buy" and state != 1:
                    exit_time = df.index[j]
                    exit_price = candle["close"]
                    trade_result = "TIE"
                    net = 0
                    break
                elif direction == "Sell" and state != -1:
                    exit_time = df.index[j]
                    exit_price = candle["close"]
                    trade_result = "TIE"
                    net = 0
                    break
            trades_detail.append({
                "entry_time": entry_time,
                "exit_time": exit_time,
                "direction": direction,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "result": trade_result,
                "net": net
            })
            if exit_time is not None:
                i = df.index.get_loc(exit_time) + 1
            else:
                # Trade remains active at the end of available data
                break

        # Statistics
        wins = sum(t["result"] == "WIN" for t in trades_detail)
        losses = sum(t["result"] == "LOSS" for t in trades_detail)
        ties = sum(t["result"] == "TIE" for t in trades_detail)
    
        total_trades = wins + losses + ties
    
        win_rate = (
            (wins / total_trades) * 100
            if total_trades > 0 else 0
        )
    
        return {
            "trades": total_trades,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": round(win_rate, 2),
            "net": sum(t["net"] for t in trades_detail),
            "trades_detail": trades_detail
        }