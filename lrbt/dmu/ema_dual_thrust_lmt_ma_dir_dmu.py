from rbt.ic import MeanIC, EmaIC, RangeMaxIC, RangeMinIC
from rbt.dmu import DecisionMakingUnit


class EmaDualThrustLmtMaDirDMU(DecisionMakingUnit):
    version = "v3"

    def __init__(self, ema_w, kl_freq=1, n=20, k1=0.1, k2=0.1, ma_lag=1500, reset_on_eod: bool = True):
        super().__init__()
        self.kl_freq = kl_freq
        self.last_send_position = 0
        self.n = n
        self.ma_lag = ma_lag
        self.k1 = k1
        self.k2 = k2
        self.position = 0
        self.hh = 0.0
        self.hc = 0.0
        self.lc = 0.0
        self.ll = 0.0
        self.hh_ic = RangeMaxIC(n)
        self.ll_ic = RangeMinIC(n)
        self.hc_ic = RangeMaxIC(n)
        self.lc_ic = RangeMinIC(n)
        self.ema_w = ema_w
        self.ema_ic = EmaIC(ema_w, 10000, ema_w)
        self.close_ma = MeanIC(ma_lag)
        self.range = None
        self.kline_count = 0
        self.long_quota = True
        self.short_quota = True
        self.relative_position = 0
        self.kline_dmu_name = f"KlineDMU_v0_{self.kl_freq}min"
        self.reset_on_eod = reset_on_eod

    def on_end_of_day(self):
        """日终重置所有 IC 和状态变量"""
        if not self.reset_on_eod:
            return
        self.hh_ic.reset()
        self.ll_ic.reset()
        self.hc_ic.reset()
        self.lc_ic.reset()
        self.ema_ic.reset()
        self.close_ma.reset()
        self.hh = 0.0
        self.hc = 0.0
        self.lc = 0.0
        self.ll = 0.0
        self.range = None
        self.position = 0
        self.long_quota = True
        self.short_quota = True
        self.relative_position = 0
        self.kline_count = 0

    def get_param_str(self) -> str:
        return f"{self.ema_w}_{self.kl_freq}min_{self.n}_{self.k1}_{self.k2}_{self.ma_lag}_{'r' if self.reset_on_eod else 'c'}"

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        open = previous_result[f"{self.kline_dmu_name}_open"]
        high = previous_result[f"{self.kline_dmu_name}_high"]
        low = previous_result[f"{self.kline_dmu_name}_low"]
        close = previous_result[f"{self.kline_dmu_name}_close"]
        completed = previous_result.get(f"{self.kline_dmu_name}_completed", False)

        if completed:
            self.hh_ic.update(high)
            self.ll_ic.update(low)
            self.hc_ic.update(close)
            self.lc_ic.update(close)

        self.hh = self.hh_ic.result
        self.ll = self.ll_ic.result
        self.hc = self.hc_ic.result
        self.lc = self.lc_ic.result
        self.range = max(self.hh - self.hc, self.ll - self.lc)

        upper_bound = close + self.k1 * self.range
        lower_bound = close - self.k2 * self.range

        self.ema_ic.update(close)
        ema_close = self.ema_ic.result
        self.close_ma.update(close)
        ma_close = self.close_ma.result
        self.relative_position = (close - open) / (open if open != 0 else 1)

        direction = 0
        if close > upper_bound and close > ma_close and self.long_quota:
            direction = 1
            self.position = 1
            self.long_quota = False
            self.short_quota = True
        elif close < lower_bound and close < ma_close and self.short_quota:
            direction = -1
            self.position = -1
            self.long_quota = True
            self.short_quota = False

        if self.position == 0:
            self.long_quota = True
            self.short_quota = True

        return {
            "direction": direction,
            "position": self.position,
            "upper_bound": upper_bound,
            "lower_bound": lower_bound,
            "ema_close": ema_close,
            "ma_close": ma_close,
            "relative_position": self.relative_position,
            "range": self.range,
        }
