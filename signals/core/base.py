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
    
    def plot(self, ax, df):
        return []

    @property
    def plot_panel(self):
        return "below"
    
    def test(self, df):
        return None
    
    def backtest(self, df, bull_signal, bear_signal):
        atr_start = df["atr"].first_valid_index()
    
        if atr_start is None:
            return {"trades": 0, "wins": 0, "losses": 0, "ties": 0, "win_percentage": 0.0, "trades_detail": pd.DataFrame()}
    
        test_df = df.loc[atr_start:].copy()
    
        # Make sure signals are aligned with test_df
        bull_signal = bull_signal.loc[test_df.index].fillna(False)
        bear_signal = bear_signal.loc[test_df.index].fillna(False)

        # Make sure they are Series, not DataFrames
        bull_signal = bull_signal.squeeze().astype(bool)
        bear_signal = bear_signal.squeeze().astype(bool)

        signal_indices = test_df.index[bull_signal | bear_signal]

        trades = []
        for entry_idx in signal_indices:
            entry_position = test_df.index.get_loc(entry_idx)
            # Determine direction
            if bull_signal.loc[entry_idx]:
                direction = 1
            else:
                direction = -1
            # Entry values
            entry_price = test_df.loc[entry_idx, "close"]
            atr = test_df.loc[entry_idx, "atr"]
        
            if pd.isna(atr) or atr <= 0:
                continue
            # --------------------------------------------------
            # ATR targets
            # --------------------------------------------------
            if direction == 1:
                # Long
                win_price = entry_price + atr
                loss_price = entry_price - (1.5 * atr)
        
            else:
                # Short
                win_price = entry_price - atr
                loss_price = entry_price + (1.5 * atr)
        
            result = None
            exit_idx = None
        
            for i in range(entry_position + 1, len(test_df)):
        
                idx = test_df.index[i]
        
                high = test_df.loc[idx, "high"]
                low = test_df.loc[idx, "low"]
                # ----------------------------------------------
                # Check ATR targets
                # ----------------------------------------------
                if direction == 1:
                    # Long
                    hit_win = high >= win_price
                    hit_loss = low <= loss_price
                else:
                    # Short
                    hit_win = low <= win_price
                    hit_loss = high >= loss_price
                # ----------------------------------------------
                # Check opposite signal
                # ----------------------------------------------
                if direction == 1:
                    opposite_signal = bear_signal.loc[idx]
                else:
                    opposite_signal = bull_signal.loc[idx]
                # ----------------------------------------------
                # Determine result
                # ----------------------------------------------
                # Both targets touched in same candle
                if hit_win and hit_loss:
                    result = "loss"
                    exit_idx = idx
                    break
                # Win
                elif hit_win:
                    result = "win"
                    exit_idx = idx
                    break
                # Loss
                elif hit_loss:
                    result = "loss"
                    exit_idx = idx
                    break
                # Signal flipped
                elif opposite_signal:
                    result = "tie"
                    exit_idx = idx
                    break
            # --------------------------------------------------
            # No result before end of dataframe
            # --------------------------------------------------
            if result is None:
                result = "tie"
                exit_idx = test_df.index[-1]
            # --------------------------------------------------
            # Store trade
            # --------------------------------------------------
            trades.append({"entry": entry_idx, "exit": exit_idx,
                "direction": ("long" if direction == 1 else "short"),
                "entry_price": entry_price, "atr": atr, "win_target": win_price, "loss_target": loss_price, "result": result})
        # --------------------------------------------------
        # Create trade DataFrame
        # --------------------------------------------------
        trades_df = pd.DataFrame(trades)
        if trades_df.empty:
            return {"trades": 0, "wins": 0, "losses": 0, "ties": 0, "win_percentage": 0.0, "trades_detail": trades_df}
        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------
        wins = (trades_df["result"] == "win").sum()
        losses = (trades_df["result"] == "loss").sum()
        ties = (trades_df["result"] == "tie").sum()
        decided = wins + losses
        
        if decided > 0:
            win_percentage = (wins / decided) * 100
        else:
            win_percentage = 0.0
        
        # --------------------------------------------------
        # Return results
        # --------------------------------------------------
        
        return {"trades": len(trades_df), "wins": wins, "losses": losses, "ties": ties, "win_percentage": win_percentage, "trades_detail": trades_df}