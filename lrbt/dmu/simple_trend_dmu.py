from rbt.dmu import DecisionMakingUnit
from rbt.ic import MeanIC, SmoothIC


class SimpleTrendDMU(DecisionMakingUnit):
    """Simple trend following DMU using moving average crossover."""

    version = "v0"

    def __init__(self, fast_period: int = 10, slow_period: int = 30):
        super().__init__()
        self.fast_ma = MeanIC(fast_period)
        self.slow_ma = MeanIC(slow_period)
        self.smoother = SmoothIC()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.last_signal = 0

    def get_param_str(self):
        return f"{self.fast_period}_{self.slow_period}"

    def make_decision(self, new_data, prev_result) -> dict:
        mid = (new_data["bid_px1"] + new_data["ask_px1"]) / 2
        mid_smo = self.smoother.update(mid)

        fast_ma = self.fast_ma.update(mid_smo)
        slow_ma = self.slow_ma.update(mid_smo)

        # Generate crossover signals
        signal = 0
        if fast_ma > slow_ma:
            signal = 1
        elif fast_ma < slow_ma:
            signal = -1

        # Detect crossover
        hits = (signal - self.last_signal) // 2
        self.last_signal = signal

        return {
            "signal": signal,
            "hits": hits,
            "fast_ma": fast_ma,
            "slow_ma": slow_ma,
            "diff": fast_ma - slow_ma,
        }
