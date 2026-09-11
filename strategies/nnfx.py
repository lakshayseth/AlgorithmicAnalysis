import pandas as pd

class NNFX:

    def __init__(self, baseline, c1, c2, volume, atr):
        self.c1 = c1
        self.c2 = c2
        self.volume = volume
        self.baseline = baseline
        self.atr = atr

    def calculate(self, df):
        df = self.c1.calculate(df)
        df = self.c2.calculate(df)
        df = self.volume.calculate(df)
        df = self.baseline.calculate(df)
        df = self.atr.calculate(df)
        return df

    def analyze(self, df):
        if len(df) < 2:
            return None
    
        df = self.calculate(df)
    
        c1_signal = self.c1.analyze(df)
        baseline_signal = self.baseline.analyze(df)
    
        c1_state = self.c1.state(df)
        c2_state = self.c2.state(df)
        volume_state = self.volume.state(df)
        baseline_state = self.baseline.state(df)
    
        # Standard
        if (
            c1_signal == "BUY"
            and baseline_state == "BUY"
            and c2_state == "BUY"
            and volume_state == "BUY"
            and self.within_atr(df, "BUY")
        ):
            return self.trade_result(df, "NNFX Standard - Buy", "BUY")
    
        if (
            c1_signal == "SELL"
            and baseline_state == "SELL"
            and c2_state == "SELL"
            and volume_state == "SELL"
            and self.within_atr(df, "SELL")
        ):
            return self.trade_result(df, "NNFX Standard - Sell", "SELL")
    
        # Standard CR
        if self.standard_cr(df, "BUY"):
            return self.trade_result(df, "NNFX Standard CR Buy", "BUY")
    
        if self.standard_cr(df, "SELL"):
            return self.trade_result(df, "NNFX Standard CR Sell", "SELL")
    
        # Baseline
        if (
            baseline_signal == "BUY"
            and c1_state == "BUY"
            and c2_state == "BUY"
            and volume_state == "BUY"
            and self.within_atr(df, "BUY")
            and self.c1_signal_within(df, "BUY", 7)
        ):
            return self.trade_result(df, "NNFX Baseline - Buy", "BUY")
    
        if (
            baseline_signal == "SELL"
            and c1_state == "SELL"
            and c2_state == "SELL"
            and volume_state == "SELL"
            and self.within_atr(df, "SELL")
            and self.c1_signal_within(df, "SELL", 7)
        ):
            return self.trade_result(df, "NNFX Baseline - Sell", "SELL")
    
        # Baseline CR
        if self.baseline_cr(df, "BUY"):
            return self.trade_result(df, "NNFX Baseline CR Buy", "BUY")
    
        if self.baseline_cr(df, "SELL"):
            return self.trade_result(df, "NNFX Baseline CR Sell", "SELL")
    
        # Pullback
        if self.pullback_entry(df, "BUY"):
            return self.trade_result(df, "NNFX Pullback - Buy", "BUY")
    
        if self.pullback_entry(df, "SELL"):
            return self.trade_result(df, "NNFX Pullback - Sell", "SELL")
    
        # Continuation
        if self.continuation_entry(df, "BUY"):
            return self.trade_result(df, "NNFX Continuation - Buy", "BUY")
    
        if self.continuation_entry(df, "SELL"):
            return self.trade_result(df, "NNFX Continuation - Sell", "SELL")
    
        return None


    def standard_cr(self, df, direction):
        if len(df) < 2:
            return False
    
        previous = df.iloc[:-1]
    
        # Previous candle: C1 signal + baseline agreement + within ATR
        if (
            self.c1.analyze(previous) != direction
            or self.baseline.state(previous) != direction
            or not self.within_atr(previous, direction)
        ):
            return False
    
        # Current candle: all confirmations agree
        return (
            self.baseline.state(df) == direction
            and self.c1.state(df) == direction
            and self.c2.state(df) == direction
            and self.volume.state(df) == direction
            and self.within_atr(df, direction)
        )

    def baseline_cr(self, df, direction):
        if len(df) < 2:
            return False
    
        previous = df.iloc[:-1]
    
        # Previous candle: baseline signal + C1 agreement + within ATR
        if (
            self.baseline.analyze(previous) != direction
            or self.c1.state(previous) != direction
            or not self.within_atr(previous, direction)
            or not self.c1_signal_within(previous, direction, 7)
        ):
            return False
    
        # Current candle: all confirmations agree
        return (
            self.baseline.state(df) == direction
            and self.c1.state(df) == direction
            and self.c2.state(df) == direction
            and self.volume.state(df) == direction
            and self.within_atr(df, direction)
        )

    def pullback_entry(self, df, direction):
        if len(df) < 2:
            return False
    
        previous = df.iloc[:-1]
    
        # Previous candle: baseline signal + C1 agreement
        if self.baseline.analyze(previous) != direction:
            return False
    
        if self.c1.state(previous) != direction:
            return False
    
        # Previous candle must be beyond 1 ATR
        if self.within_atr(previous, direction):
            return False
    
        # Current candle: all confirmations agree
        return (
            self.baseline.state(df) == direction
            and self.c1.state(df) == direction
            and self.c2.state(df) == direction
            and self.volume.state(df) == direction
            and self.within_atr(df, direction)
        )

    def continuation_entry(self, df, direction):
        if len(df) < 3 or self.c1.analyze(df) != direction or self.c2.state(df) != direction:
            return False
    
        opposite = "SELL" if direction == "BUY" else "BUY"
    
        opp_idx = next(
            (i for i in range(len(df) - 2, 0, -1)
             if self.c1.analyze(df.iloc[:i + 1]) == opposite), None
        )
        if opp_idx is None:
            return False
    
        prev_idx = next(
            (i for i in range(opp_idx - 1, 0, -1)
             if self.c1.analyze(df.iloc[:i + 1]) == direction), None
        )
        if prev_idx is None:
            return False
    
        close = df["close"].iloc[prev_idx:]
        baseline = self.baseline.value(df.iloc[prev_idx:])
    
        return (close > baseline).all() if direction == "BUY" else (close < baseline).all()

    def within_atr(self, df, direction):
        price = df["close"].iloc[-1]
        baseline = self.baseline.value(df)
        atr = self.atr.value(df)

        if any(pd.isna(x) for x in [price, baseline, atr]):
            return False

        if direction == "BUY":
            return price <= baseline + atr

        if direction == "SELL":
            return price >= baseline - atr

        return False

    def c1_signal_within(self, df, direction, candles=7):
        if len(df) < 2:
            return False

        start = max(1, len(df) - candles)

        for i in range(start, len(df) - 1):
            if self.c1.analyze(df.iloc[:i + 1]) == direction:
                return True

        return False

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
            "price": round(price,2),
            "atr": round(atr,2),
            "take_profit": round(take_profit,2),
            "stop_loss": round(stop_loss,2),
        }

    def status(self, df):
        df = self.calculate(df)

        return {
            "C1 Signal": self.c1.analyze(df),
            "C1 State": self.c1.state(df),
            "C2 State": self.c2.state(df),
            "Volume State": self.volume.state(df),
            "Baseline Signal": self.baseline.analyze(df),
            "Baseline State": self.baseline.state(df),
            "C1 Buy <7": self.c1_signal_within(df, "BUY", 7),
            "C1 Sell <7": self.c1_signal_within(df, "SELL", 7),
            "Within ATR Buy": self.within_atr(df, "BUY"),
            "Within ATR Sell": self.within_atr(df, "SELL"),
            "Standard CR Buy": self.standard_cr(df, "BUY"),
            "Standard CR Sell": self.standard_cr(df, "SELL"),
            "Baseline CR Buy": self.baseline_cr(df, "BUY"),
            "Baseline CR Sell": self.baseline_cr(df, "SELL"),
            "RESULT": self.analyze(df),
        }

    def trade_invalidated(self, df, direction):

        reasons = []

        if direction == "BUY":
            if self.c1.state(df) == "SELL":
                reasons.append("C1 flipped")
            if self.c2.state(df) == "SELL":
                reasons.append("C2 flipped")
            if self.baseline.state(df) == "SELL":
                reasons.append("Baseline flipped")
            if not self.within_atr(df, "BUY"):
                reasons.append("ATR exceeded")

        elif direction == "SELL":
            if self.c1.state(df) == "BUY":
                reasons.append("C1 flipped")
            if self.c2.state(df) == "BUY":
                reasons.append("C2 flipped")
            if self.baseline.state(df) == "BUY":
                reasons.append("Baseline flipped")
            if not self.within_atr(df, "SELL"):
                reasons.append("ATR exceeded")

        return reasons

    def backtest(self, df):
        trades_detail = []
        i = 1
        while i < len(df):
            current_df = df.iloc[:i + 1].copy()
            result = self.analyze(current_df)
            if result is None:
                i += 1
                continue

            entry = df.index[i]
            entry_price = result["price"]
            atr = result["atr"]
            direction = result["direction"]

            if direction == "BUY":
                direction_name = "LONG"
                win_target = entry_price + atr
                loss_target = entry_price - (atr * 1.5)
            else:
                direction_name = "SHORT"
                win_target = entry_price - atr
                loss_target = entry_price + (atr * 1.5)

            exit_time = None
            exit_price = None
            trade_result = "TIE"
            tie_reason = None
            exit_index = None

            # Check candles after entry
            for j in range(i + 1, len(df)):
                high = df["high"].iloc[j]
                low = df["low"].iloc[j]
                # --------------------------------
                # BUY
                # --------------------------------
                if direction == "BUY":
                    # Both TP and SL hit on same candle
                    if high >= win_target and low <= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break

                    # Take profit
                    if high >= win_target:
                        trade_result = "WIN"
                        exit_price = win_target
                        exit_time = df.index[j]
                        exit_index = j
                        break

                    # Stop loss
                    if low <= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break

                # --------------------------------
                # SELL
                # --------------------------------
                else:

                    # Both TP and SL hit on same candle
                    if low <= win_target and high >= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break

                    # Take profit
                    if low <= win_target:
                        trade_result = "WIN"
                        exit_price = win_target
                        exit_time = df.index[j]
                        exit_index = j
                        break

                    # Stop loss
                    if high >= loss_target:
                        trade_result = "LOSS"
                        exit_price = loss_target
                        exit_time = df.index[j]
                        exit_index = j
                        break
                # --------------------------------
                # SIGNAL INVALIDATION = TIE
                # --------------------------------
                candle_df = df.iloc[:j + 1].copy()
                tie_reasons = self.trade_invalidated(candle_df, direction)

                if tie_reasons:
                    trade_result = "TIE"
                    tie_reason = ", ".join(tie_reasons)
                    exit_price = df["close"].iloc[j]
                    exit_time = df.index[j]
                    exit_index = j

                    break

            trades_detail.append({
                "entry": entry,
                "exit": exit_time,
                "direction": direction_name,
                "entry_price": entry_price,
                "atr": atr,
                "win_target": win_target,
                "loss_target": loss_target,
                "exit_price": exit_price,
                "result": trade_result,
                "tie_reason": tie_reason,
            })

            # If trade finished, skip forward to after the exit
            if exit_index is not None:
                i = exit_index + 1
            else:
                # No TP/SL or invalidation before end of data
                i = len(df)

        wins = sum(t["result"] == "WIN" for t in trades_detail)
        losses = sum(t["result"] == "LOSS" for t in trades_detail)
        ties = sum(t["result"] == "TIE" for t in trades_detail)
        trades = len(trades_detail)

        win_percentage = (wins / (wins + losses) * 100 if wins + losses > 0 else 0)

        return {
            "trades": trades,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_percentage": win_percentage,
            "trades_detail": trades_detail,
        }