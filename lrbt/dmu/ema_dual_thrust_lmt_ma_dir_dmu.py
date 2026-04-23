from rbt.dmu import DecisionMakingUnit
from rbt.ic import MeanIC, EmaIC, RangeMaxIC, RangeMinIC


class EmaDualThrustLmtMaDirDMU(DecisionMakingUnit):
    """EMA Dual Thrust 限价均线方向 DMU。

    基于 Dual Thrust 策略变体：
    - 用 EMA 平滑后的价格与开盘价 ± k*range 构成的上下轨比较产生信号
    - 用 EMA 与收盘价均线的关系判断方向，作为平仓条件
    - 每根K线内多/空信号各只触发一次（quota 机制）

    输出:
        ema: EMA 平滑后的最新价
        upper_rail: 上轨价格
        close_ma: 收盘价均线
        lower_rail: 下轨价格
        position: 当前持仓方向 (1=多, -1=空, 0=平)
        signal_direction: position 变化方向 (1=转多, -1=转空, 0=无变化)
    """

    version = "v0"

    def __init__(self, ema_w, kl_freq=1, n=20, k1=0.1, k2=0.1, ma_lag=1500):
        """初始化 EmaDualThrustLmtMaDirDMU。

        参数:
            ema_w (float): EMA 平滑系数 alpha。
            kl_freq (int): K线时间间隔（分钟），默认1。
            n (int): 计算 HH/LL/HC/LC 的滑动窗口大小，默认20。
            k1 (float): 上轨系数，默认0.1。
            k2 (float): 下轨系数，默认0.1。
            ma_lag (int): 收盘价均线窗口大小，默认1500。
        """
        super().__init__()
        self.kl_freq = kl_freq
        self.last_send_position = 0
        self.n = n
        self.ma_lag = ma_lag
        self.k1 = k1
        self.k2 = k2
        self.ema_w = ema_w

        self.position = 0
        self.hh = 0.0
        self.hc = 0.0
        self.lc = 0.0
        self.ll = 0.0

        self.hh_ic = RangeMaxIC(n)
        self.ll_ic = RangeMinIC(n)
        self.hc_ic = RangeMaxIC(n)
        self.lc_ic = RangeMinIC(n)
        self.ema_ic = EmaIC(ema_w, 10000, ema_w)
        self.close_ma = MeanIC(ma_lag)

        self.range = None
        self.kline_count = 0
        self.long_quota = True
        self.short_quota = True
        self.relative_position = 0

        self._kline_dmu_name = f"KlineDMU_v0_{self.kl_freq}min"
        self._key_open = f"{self._kline_dmu_name}__open"
        self._key_high = f"{self._kline_dmu_name}__high"
        self._key_low = f"{self._kline_dmu_name}__low"
        self._key_close = f"{self._kline_dmu_name}__close"
        self._key_completed = f"{self._kline_dmu_name}__completed"
        self.update_unit_name()

    def get_param_str(self) -> str:
        return f"{self.ema_w}_{self.kl_freq}min_{self.n}_{self.k1}_{self.k2}_{self.ma_lag}"

    def dependencies(self) -> list:
        return [self._kline_dmu_name]

    def on_end_of_day(self):
        """日终重置所有状态。"""
        self.last_send_position = 0
        self.position = 0
        self.hh = 0.0
        self.hc = 0.0
        self.lc = 0.0
        self.ll = 0.0
        self.hh_ic = RangeMaxIC(self.n)
        self.ll_ic = RangeMinIC(self.n)
        self.hc_ic = RangeMaxIC(self.n)
        self.lc_ic = RangeMinIC(self.n)
        self.ema_ic = EmaIC(self.ema_w, 10000, self.ema_w)
        self.close_ma = MeanIC(self.ma_lag)
        self.range = None
        self.kline_count = 0
        self.long_quota = True
        self.short_quota = True
        self.relative_position = 0

    def reset(self):
        super().reset()
        self.valid_data = []
        self.result = {}

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        """根据 Dual Thrust 策略计算持仓信号。

        参数:
            new_data: 最新行情数据，需包含 last_px。
            previous_result (dict): 上游 DMU 输出，需包含 KlineDMU 的 OHLC 和 completed。

        Returns:
            dict: ema / upper_rail / close_ma / lower_rail / position / signal_direction。
        """
        open_ = previous_result[self._key_open]
        high = previous_result[self._key_high]
        low = previous_result[self._key_low]
        close = previous_result[self._key_close]
        completed = previous_result[self._key_completed]

        last_px_ema = self.ema_ic.update(new_data["last_px"])
        close_ma = self.close_ma.update(close)

        upper_rail = None
        lower_rail = None

        if self.kline_count >= self.n:
            cur_relative_position = 0
            if last_px_ema > close_ma:
                cur_relative_position = 1
            elif last_px_ema < close_ma:
                cur_relative_position = -1

            range_ = max(self.hh - self.lc, self.hc - self.ll)
            if range_ > 0:
                upper_rail = open_ + self.k1 * range_
                lower_rail = open_ - self.k2 * range_

                cur_signal = 0
                if last_px_ema >= upper_rail and self.long_quota:
                    cur_signal = 1
                    self.long_quota = False
                elif last_px_ema <= lower_rail and self.short_quota:
                    cur_signal = -1
                    self.short_quota = False

                if self.position == 0:
                    self.position = cur_signal
                else:
                    if cur_signal != 0:
                        self.position = cur_signal
                    else:
                        if (self.relative_position != 0
                                and cur_relative_position != self.relative_position):
                            if cur_relative_position == -1 and self.position == 1:
                                self.position = 0
                            if cur_relative_position == 1 and self.position == -1:
                                self.position = 0

            if cur_relative_position != 0:
                self.relative_position = cur_relative_position

        if completed:
            self.hh = self.hh_ic.update(high)
            self.hc = self.hc_ic.update(close)
            self.lc = self.lc_ic.update(close)
            self.ll = self.ll_ic.update(low)
            self.kline_count += 1
            self.long_quota = True
            self.short_quota = True
            self.relative_position = 0

        # 信号方向：position 相对上次的变化方向
        # 1=转多方向, -1=转空方向, 0=无变化
        if self.position > self.last_send_position:
            signal_direction = 1
        elif self.position < self.last_send_position:
            signal_direction = -1
        else:
            signal_direction = 0
        self.last_send_position = self.position

        return {
            "ema": last_px_ema,
            "upper_rail": upper_rail,
            "close_ma": close_ma,
            "lower_rail": lower_rail,
            "position": self.position,
            "signal_direction": signal_direction,
        }
