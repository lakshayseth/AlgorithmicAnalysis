import pandas as pd

class NNFX:

    def __init__(self, baseline, c1, c2, volume, atr):
        self.c1 = c1
        self.c2 = c2
        self.volume = volume
        self.baseline = baseline
        self.atr = atr

    def calculate(self, df):
        df = df.copy()
        df = self.c1.calculate(df)
        df = self.c2.calculate(df)
        df = self.volume.calculate(df)
        df = self.baseline.calculate(df)
        df = self.atr.calculate(df)
        return df

    def get_signal(self, indicator, df):
        states = indicator.get_state(df)

        if len(states) < 2:
            return False

        previous = states.iloc[-2]
        current = states.iloc[-1]

        if pd.isna(previous) or pd.isna(current):
            return False

        return current if current != previous else False
    
    def execute(self, df):
        if len(df) < 2:
            return None
        
        df = self.calculate(df)
        
        c1_signal = self.get_signal(self.c1, df)
        baseline_signal = self.get_signal(self.baseline, df)
        
        c1_state = self.c1.get_state(df).iloc[-1]
        c2_state = self.c2.get_state(df).iloc[-1]
        volume_state = self.volume.get_state(df).iloc[-1]
        baseline_state = self.baseline.get_state(df).iloc[-1]
      
        # Standard
        if (c1_signal == 1 and baseline_state == 1 and c2_state == 1
            and volume_state == 1 and self.within_atr(df, 1)):
            return self.trade_result(df, "NNFX Standard - Buy", "BUY")
        
        if (c1_signal == -1 and baseline_state == -1 and c2_state == -1
            and volume_state == -1 and self.within_atr(df, -1)):
            return self.trade_result(df, "NNFX Standard - Sell", "SELL")
        
        # Standard CR
        if self.standard_cr(df, 1):
            return self.trade_result(df, "NNFX Standard CR Buy", "BUY")
    
        if self.standard_cr(df, -1):
            return self.trade_result(df, "NNFX Standard CR Sell", "SELL")

        # Baseline
        if (baseline_signal == 1 and c1_state == 1 and c2_state == 1
            and volume_state == 1 and self.within_atr(df, 1) and self.c1_signal_within(df, 1, 7)):
            return self.trade_result(df, "NNFX Baseline - Buy", "BUY")
    
        if (baseline_signal == -1 and c1_state == -1 and c2_state == -1
            and volume_state == -1 and self.within_atr(df, -1) and self.c1_signal_within(df, -1, 7)):
            return self.trade_result(df, "NNFX Baseline - Sell", "SELL")

        # Baseline CR
        if self.baseline_cr(df, 1):
            return self.trade_result(df, "NNFX Baseline CR Buy", "BUY")
    
        if self.baseline_cr(df, -1):
            return self.trade_result(df, "NNFX Baseline CR Sell", "SELL")

        # Pullback
        if self.pullback_entry(df, 1):
            return self.trade_result(df, "NNFX Pullback - Buy", "BUY")
    
        if self.pullback_entry(df, -1):
            return self.trade_result(df, "NNFX Pullback - Sell", "SELL")    

        # Continuation
        if self.continuation_entry(df, 1):
            return self.trade_result(df, "NNFX Continuation - Buy", "BUY")
    
        if self.continuation_entry(df, -1):
            return self.trade_result(df, "NNFX Continuation - Sell", "SELL")
    
        return None

    def within_atr(self, df, direction):
        price = df["close"].iloc[-1]
        baseline = self.baseline.value(df)
        atr = self.atr.value(df)

        if any(pd.isna(x) for x in [price, baseline, atr]):
            return False

        if direction == 1:
            return price <= baseline + atr

        if direction == -1:
            return price >= baseline - atr
        
        return False

    def standard_cr(self, df, direction):
        if len(df) < 2:
            return False
        previous = df.iloc[:-1]
        c1_signal = self.get_signal(self.c1, previous)
        baseline_state = self.baseline.get_state(previous).iloc[-1]
        # Previous candle: C1 signal + baseline agreement + within ATR
        if (c1_signal != direction or baseline_state != direction or not self.within_atr(previous, direction)):
            return False
        # Current candle: all confirmations agree
        return (self.baseline.get_state(df).iloc[-1] == direction
            and self.c1.get_state(df).iloc[-1] == direction
            and self.c2.get_state(df).iloc[-1] == direction
            and self.volume.get_state(df).iloc[-1] == direction
            and self.within_atr(df, direction))   

    def c1_signal_within(self, df, direction, candles=7):
        if len(df) < 2:
            return False
        states = self.c1.get_state(df)
        switches = ((states == direction) & (states.shift(1) != direction))
        start = max(1, len(df) - candles)
        return switches.iloc[start:-1].any()

    def baseline_cr(self, df, direction):
        if len(df) < 2:
            return False
        previous = df.iloc[:-1]
        baseline_signal = self.get_signal(self.baseline, previous)
        c1_state = self.c1.get_state(previous).iloc[-1]
        # Previous candle: baseline signal + C1 agreement + within ATR
        if (baseline_signal != direction or c1_state != direction
            or not self.within_atr(previous, direction) or not self.c1_signal_within(previous, direction, 7)):
            return False

        # Current candle: all confirmations agree
        return (
            self.baseline.get_state(df).iloc[-1] == direction
            and self.c1.get_state(df).iloc[-1] == direction
            and self.c2.get_state(df).iloc[-1] == direction
            and self.volume.get_state(df).iloc[-1] == direction
            and self.within_atr(df, direction)
        )

    def pullback_entry(self, df, direction):
        if len(df) < 2:
            return False
        previous = df.iloc[:-1]
        baseline_signal = self.get_signal(self.baseline, previous)
        c1_state = self.c1.get_state(previous).iloc[-1]
        # Previous candle: baseline signal + C1 agreement
        if baseline_signal != direction:
            return False
        if c1_state != direction:
            return False
        # Previous candle must be beyond 1 ATR
        if self.within_atr(previous, direction):
            return False
    
        # Current candle: all confirmations agree
        return (
            self.baseline.get_state(df).iloc[-1] == direction
            and self.c1.get_state(df).iloc[-1] == direction
            and self.c2.get_state(df).iloc[-1] == direction
            and self.volume.get_state(df).iloc[-1] == direction
            and self.within_atr(df, direction)
        )

    def continuation_entry(self, df, direction):
        if len(df) < 3:
            return False

        c1_states = self.c1.get_state(df)
        c2_states = self.c2.get_state(df)

        if (c1_states.iloc[-1] != direction or c1_states.iloc[-2] == direction or c2_states.iloc[-1] != direction):
            return False

        opposite = -direction
        switches = c1_states.ne(c1_states.shift(1))

        opp_indices = [i for i in range(len(df) - 2, 0, -1)
            if switches.iloc[i] and c1_states.iloc[i] == opposite]

        if not opp_indices:
            return False

        opp_idx = opp_indices[0]

        prev_indices = [i for i in range(opp_idx - 1, 0, -1)
            if switches.iloc[i] and c1_states.iloc[i] == direction]

        if not prev_indices:
            return False

        prev_idx = prev_indices[0]

        close = df["close"].iloc[prev_idx:]
        baseline = self.baseline.value(df.iloc[prev_idx:])

        if direction == 1:
            return (close > baseline).all()

        return (close < baseline).all()
    
    def trade_result(self, df, signal, direction):
        price = df["close"].iloc[-1]
        atr = self.atr.value(df)
    
        if pd.isna(price) or pd.isna(atr):
            return None
    
        if direction == "BUY":
            take_profit = price + atr
            stop_loss = price - (atr * 1.5)
        else:
            take_profit = price - atr
            stop_loss = price + (atr * 1.5)
    
        return {
            "signal": signal,
            "direction": direction,
            "price": float(round(price, 4)),
            "atr": float(round(atr, 4)),
            "take_profit": float(round(take_profit, 4)),
            "stop_loss": float(round(stop_loss, 4)),
        }

    def trade_invalidated(self, df, direction):
        reasons = []
    
        c1_state = self.c1.get_state(df).iloc[-1]
        c2_state = self.c2.get_state(df).iloc[-1]
        baseline_state = self.baseline.get_state(df).iloc[-1]
    
        if direction == "BUY":
            if c1_state == -1:
                reasons.append("C1 flipped")
            if c2_state == -1:
                reasons.append("C2 flipped")
            if baseline_state == -1:
                reasons.append("Baseline flipped")
    
        elif direction == "SELL":
            if c1_state == 1:
                reasons.append("C1 flipped")
            if c2_state == 1:
                reasons.append("C2 flipped")
            if baseline_state == 1:
                reasons.append("Baseline flipped")
    
        return reasons
    
    def backtest(self, df):
        trades_detail = []
        i = 1
        while i < len(df):
            current_df = df.iloc[:i + 1].copy()
            result = self.execute(current_df)
            if result is None:
                i += 1
                continue
            entry = df.index[i]
            entry_price = result["price"]
            atr = result["atr"]
            direction = result["direction"]
            signal = result["signal"]
            if direction == "BUY":
                direction_name = "Long"
                win_target = entry_price + atr
                loss_target = entry_price - (atr * 1.5)
            else:
                direction_name = "Short"
                win_target = entry_price - atr
                loss_target = entry_price + (atr * 1.5)
            exit_time = None
            exit_price = None
            trade_result = None
            tie_reason = None
            exit_index = None
            # Check candles after entry
            for j in range(i + 1, len(df)):
                high = df["high"].iloc[j]
                low = df["low"].iloc[j]
                # BUY
                if direction == "BUY":
                    if high >= win_target and low <= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break
                    if high >= win_target:
                        trade_result = "WIN"
                        exit_price = win_target
                        exit_time = df.index[j]
                        exit_index = j
                        break
                    if low <= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break
                # SELL
                else:
                    if low <= win_target and high >= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break
                    if low <= win_target:
                        trade_result = "WIN"
                        exit_price = win_target
                        exit_time = df.index[j]
                        exit_index = j
                        break
                    if high >= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break
                # SIGNAL INVALIDATION
                candle_df = self.calculate(df.iloc[:j + 1].copy())
                tie_reasons = self.trade_invalidated(candle_df, direction)
                if tie_reasons:
                    trade_result = "TIE"
                    tie_reason = ", ".join(tie_reasons)
                    exit_price = df["close"].iloc[j]
                    exit_time = df.index[j]
                    exit_index = j
                    break
            # Calculate net profit
            if exit_price is not None:
                if direction == "BUY":
                    net = exit_price - entry_price
                else:
                    net = entry_price - exit_price
            else:
                net = 0

            trades_detail.append({
                "entry": entry,
                "exit": exit_time,
                "direction": direction_name,
                "signal": signal,
                "entry_price": entry_price,
                "atr": atr,
                "win_target": win_target,
                "loss_target": loss_target,
                "exit_price": exit_price,
                "result": trade_result,
                "tie_reason": tie_reason,
                "net": net,
            })
            # Skip forward after trade closes
            if exit_index is not None:
                i = exit_index + 1
            else:
                i = len(df)
        # Statistics
        wins = sum(t["result"] == "WIN" for t in trades_detail)
        losses = sum(t["result"] == "LOSS" for t in trades_detail)
        ties = sum(t["result"] == "TIE" for t in trades_detail)
        trades = wins + losses + ties
        win_percentage = (wins / (wins + losses) * 100 if wins + losses > 0 else 0)
        net_profit = sum(t["net"] for t in trades_detail)
        net_wins = sum(t["net"] for t in trades_detail if t["result"] == "WIN")
        net_losses = sum(t["net"] for t in trades_detail if t["result"] == "LOSS")
        net_ties = sum(t["net"] for t in trades_detail if t["result"] == "TIE")

        return {
            "trades": trades,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_percentage": win_percentage,
            "net_profit": float(round(net_profit, 4)),
            "net_wins": float(round(net_wins, 4)),
            "net_losses": float(round(net_losses, 4)),
            "net_ties": float(round(net_ties, 4)),
            "trades_detail": trades_detail,
        }