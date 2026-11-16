from abc import ABC, abstractmethod
import pandas as pd

class Signal(ABC):
    """
    Base class for all trading signals and indicators.
    """
    name: str = ""

    def __init__(self, **params):
        self.params = params

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the signal/indicator.

        Args:
            df: Input market data.

        Returns:
            DataFrame containing the calculated signal/indicator.
        """
        pass
    
    @abstractmethod
    def get_state(self, df):
        """
        Returns:
            1  = Bullish
            -1 = Bearish
            0  = Neutral
        """
        pass
    
    @property
    def plot_panel(self):
        return "below"
    
    def test(self, df: pd.DataFrame) -> dict:
        """
        Generic backtesting method.

        Entry:
            Enter long when state changes to 1.
            Enter short when state changes to -1.

        Exit:
            Long exits when state is no longer 1.
            Short exits when state is no longer -1.

        Targets:
            Long win: entry + ATR
            Long loss: entry - 1.5 * ATR

            Short win: entry - ATR
            Short loss: entry + 1.5 * ATR

        If both targets are touched on the same candle,
        the trade is recorded as a loss.
        """

        # Calculate indicator values
        df = self.calculate(df.copy())
        
        # Find the first valid ATR value
        atr_start = df["atr"].first_valid_index()

        if atr_start is None:
            return {"trades": 0, "wins": 0, "losses": 0, "ties": 0, 
                    "win_percentage": 0.0, "net_profit": 0.0, "trades_detail": []}

        # Start testing once ATR is available
        test_df = df.loc[atr_start:].copy()
        # Get bullish, bearish, and neutral states
        state = self.get_state(test_df)
        state = state.reindex(test_df.index)

        bull_signal = ((state == 1) & (state.shift(1) != 1) & state.shift(1).notna())
        bear_signal = ((state == -1) & (state.shift(1) != -1) & state.shift(1).notna())

        # Exclude the first row
        bull_signal.iloc[0] = False
        bear_signal.iloc[0] = False

        # Find all entry signal indices
        signal_indices = test_df.index[bull_signal | bear_signal]

        trades_detail = []

        # Process each signal independently
        for idx in signal_indices:

            entry_position = test_df.index.get_loc(idx)

            # Determine trade direction
            direction = 1 if bull_signal.loc[idx] else -1

            # Entry information
            entry_price = test_df.loc[idx, "close"]
            atr = test_df.loc[idx, "atr"]

            # Skip entries with invalid ATR
            if pd.isna(atr):
                continue

            # Calculate targets
            if direction == 1:
                win_target = entry_price + atr
                loss_target = entry_price - (1.5 * atr)
            else:
                win_target = entry_price - atr
                loss_target = entry_price + (1.5 * atr)

            result = None
            exit_price = None
            exit_idx = None

            # Check exit conditions starting two candles after entry
            for i in range(entry_position + 1, len(test_df)):

                candle = test_df.iloc[i]
                current_idx = test_df.index[i]

                # Check target hits
                if direction == 1:
                    win_hit = candle["high"] >= win_target
                    loss_hit = candle["low"] <= loss_target
                else:
                    win_hit = candle["low"] <= win_target
                    loss_hit = candle["high"] >= loss_target

                # If both targets are touched, assume loss
                if win_hit and loss_hit:
                    result = "loss"
                    exit_price = loss_target
                    exit_idx = current_idx
                    break

                # Winning target
                elif win_hit:
                    result = "win"
                    exit_price = win_target
                    exit_idx = current_idx
                    break

                # Losing target
                elif loss_hit:
                    result = "loss"
                    exit_price = loss_target
                    exit_idx = current_idx
                    break

                # Check whether the indicator state has changed
                current_state = state.loc[current_idx]

                if direction == 1:
                    opposite_signal = current_state != 1
                else:
                    opposite_signal = current_state != -1

                # Exit at candle close if state is no longer aligned
                if opposite_signal:
                    result = "tie"
                    exit_price = candle["close"]
                    exit_idx = current_idx
                    break

            # If no exit condition was reached, close at final candle
            if result is None:
                exit_idx = test_df.index[-1]
                exit_price = test_df.iloc[-1]["close"]
                result = "tie"

            # Calculate net profit
            if direction == 1:
                net = exit_price - entry_price
            else:
                net = entry_price - exit_price
            
            # Record trade
            trades_detail.append({"entry": idx, "exit": exit_idx, "direction": "Long" if direction == 1 else "Short", "entry_price": entry_price, "atr": atr,
                "win_target": win_target, "loss_target": loss_target, "exit_price": exit_price, "result": result, "net": net})

        # Calculate statistics
        total_trades = len(trades_detail)

        wins = sum(1 for trade in trades_detail if trade["result"] == "win")
        losses = sum(1 for trade in trades_detail if trade["result"] == "loss")
        ties = sum(1 for trade in trades_detail if trade["result"] == "tie")

        decided_trades = wins + losses

        if decided_trades > 0:
            win_percentage = (wins / decided_trades) * 100
        else:
            win_percentage = 0.0

        net_profit = sum(trade["net"] for trade in trades_detail)

        return {"trades": total_trades, "wins": wins, "losses": losses, "ties": ties,
            "win_percentage": win_percentage, "net_profit": net_profit, "trades_detail": pd.DataFrame(trades_detail)}