from rbt.dmu import DecisionMakingUnit
from rbt.ic import MeanIC, VarianceIC


class MeanRevertDMU(DecisionMakingUnit):
    """Mean reversion DMU using Bollinger Band logic."""

    version = "v0"

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__()
        self.mean_ic = MeanIC(period)
        self.var_ic = VarianceIC(period)
        self.period = period
        self.std_dev = std_dev

    def get_param_str(self):
        return f"{self.period}_{self.std_dev}"

    def make_decision(self, new_data, prev_result) -> dict:
        mid = (new_data["bid_px1"] + new_data["ask_px1"]) / 2

        mean = self.mean_ic.update(mid)
        variance = self.var_ic.update(mid)
        std = variance ** 0.5

        # Bollinger Bands
        upper = mean + self.std_dev * std
        lower = mean - self.std_dev * std

        # Generate mean reversion signals
        z_score = (mid - mean) / std if std > 0 else 0
        signal = 0
        if z_score > self.std_dev:
            signal = -1  # Overbought, expect reversal down
        elif z_score < -self.std_dev:
            signal = 1   # Oversold, expect reversal up

        return {
            "signal": signal,
            "z_score": z_score,
            "mean": mean,
            "upper": upper,
            "lower": lower,
            "std": std,
        }
