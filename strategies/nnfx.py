import pandas as pd

class NNFX:

    def __init__(self, c1, c2, volume, baseline, atr):
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

        if (
            c1_signal == "BUY"
            and baseline_state == "BUY"
            and c2_state == "BUY"
            and volume_state == "BUY"
            and self.within_atr(df, "BUY")
        ):
            return "NNFX Standard - Buy"

        if (
            c1_signal == "SELL"
            and baseline_state == "SELL"
            and c2_state == "SELL"
            and volume_state == "SELL"
            and self.within_atr(df, "SELL")
        ):
            return "NNFX Standard - Sell"

        if self.standard_cr(df, "BUY"):
            return "NNFX Standard CR Buy"

        if self.standard_cr(df, "SELL"):
            return "NNFX Standard CR Sell"

        if (
            baseline_signal == "BUY"
            and c1_state == "BUY"
            and c2_state == "BUY"
            and volume_state == "BUY"
            and self.within_atr(df, "BUY")
            and self.c1_signal_within(df, "BUY", 7)
        ):
            return "NNFX Baseline - Buy"

        if (
            baseline_signal == "SELL"
            and c1_state == "SELL"
            and c2_state == "SELL"
            and volume_state == "SELL"
            and self.within_atr(df, "SELL")
            and self.c1_signal_within(df, "SELL", 7)
        ):
            return "NNFX Baseline - Sell"

        if self.baseline_cr(df, "BUY"):
            return "NNFX Baseline CR Buy"

        if self.baseline_cr(df, "SELL"):
            return "NNFX Baseline CR Sell"

        if self.pullback_entry(df, "BUY"): 
            return "NNFX Pullback - Buy" 
        if self.pullback_entry(df, "SELL"): 
            return "NNFX Pullback - Sell"

        if self.continuation_entry(df, "BUY"):
            return "NNFX Continuation Buy"
        
        if self.continuation_entry(df, "SELL"):
            return "NNFX Continuation Sell"
        
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