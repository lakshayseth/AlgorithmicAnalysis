import pandas as pd


class ICHIMOKU:

    def __init__(self, ichimoku, atr):
        self.ichimoku = ichimoku
        self.atr = atr

    def calculate(self, df):
        df = self.ichimoku.calculate(df)
        df = self.atr.calculate(df)
        return df

    def analyze(self, df):
        if len(df) < 2:
            return None

        df = self.calculate(df)

        signal = self.ichimoku.analyze(df)

        if signal == "BUY":
            return self.trade_result(df, "Ichimoku - Buy", "BUY")

        if signal == "SELL":
            return self.trade_result(df, "Ichimoku - Sell", "SELL")

        return None

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

        signal = self.ichimoku.state(df)

        if direction == "BUY" and signal == "SELL":
            reasons.append("Ichimoku flipped")

        elif direction == "SELL" and signal == "BUY":
            reasons.append("Ichimoku flipped")

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

            for j in range(i + 1, len(df)):
                high = df["high"].iloc[j]
                low = df["low"].iloc[j]

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

                candle_df = df.iloc[:j + 1].copy()
                tie_reasons = self.trade_invalidated(candle_df, direction)

                if tie_reasons:
                    trade_result = "TIE"
                    tie_reason = ", ".join(tie_reasons)
                    exit_price = df["close"].iloc[j]
                    exit_time = df.index[j]
                    exit_index = j
                    break

            if exit_price is not None:
                if direction == "BUY":
                    net = exit_price - entry_price
                else:
                    net = entry_price - exit_price
            else:
                net = None

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
                "net": net,
            })

            if exit_index is not None:
                i = exit_index + 1
            else:
                i = len(df)

        wins = sum(t["result"] == "WIN" for t in trades_detail)
        losses = sum(t["result"] == "LOSS" for t in trades_detail)
        ties = sum(t["result"] == "TIE" for t in trades_detail)
        trades = wins + losses + ties

        win_percentage = (
            wins / (wins + losses) * 100
            if wins + losses > 0
            else 0
        )

        net_profit = sum(
            t["net"] for t in trades_detail
            if t["net"] is not None
        )

        net_wins = sum(
            t["net"] for t in trades_detail
            if t["result"] == "WIN" and t["net"] is not None
        )

        net_losses = sum(
            t["net"] for t in trades_detail
            if t["result"] == "LOSS" and t["net"] is not None
        )

        net_ties = sum(
            t["net"] for t in trades_detail
            if t["result"] == "TIE" and t["net"] is not None
        )

        return {
            "trades": trades,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_percentage": round(win_percentage, 2),
            "net_profit": float(round(net_profit, 4)),
            "net_wins": float(round(net_wins, 4)),
            "net_losses": float(round(net_losses, 4)),
            "net_ties": float(round(net_ties, 4)),
            "trades_detail": trades_detail,
        }