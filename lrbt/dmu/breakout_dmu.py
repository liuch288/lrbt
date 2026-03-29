from rbt.dmu import DecisionMakingUnit
from rbt.ic import MaxIC, MinIC


class BreakoutDMU(DecisionMakingUnit):
    """Breakout DMU detecting price channel breakouts."""

    version = "v0"

    def __init__(self, period: int = 20):
        super().__init__()
        self.max_ic = MaxIC(period)
        self.min_ic = MinIC(period)
        self.period = period
        self.last_position = 0

    def get_param_str(self):
        return str(self.period)

    def make_decision(self, new_data, prev_result) -> dict:
        mid = (new_data["bid_px1"] + new_data["ask_px1"]) / 2

        max_price = self.max_ic.update(mid)
        min_price = self.min_ic.update(mid)

        # Detect breakouts
        signal = 0
        if mid >= max_price:
            signal = 1
        elif mid <= min_price:
            signal = -1

        # Detect breakout events
        hits = (signal - self.last_position) // 2
        self.last_position = signal

        # Calculate channel width and position within channel
        channel_width = max_price - min_price
        position_pct = (mid - min_price) / channel_width if channel_width > 0 else 0.5

        return {
            "signal": signal,
            "hits": hits,
            "max_price": max_price,
            "min_price": min_price,
            "channel_width": channel_width,
            "position_pct": position_pct,
        }
