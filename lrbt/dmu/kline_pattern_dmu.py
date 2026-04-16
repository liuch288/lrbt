from collections import deque

from rbt.dmu import DecisionMakingUnit


class KlinePatternDMU(DecisionMakingUnit):
    """K线模式DMU。

    追踪过去N根已完成K线的收盘价，计算相邻K线之间的涨跌关系，
    输出价格方向模式字符串（如 "ud" 表示先涨后跌）。

    算法：过去N根K线两两之间的相邻涨跌比较
    - close[i] > close[i-1] → "u" (up)
    - close[i] < close[i-1] → "d" (down)
    - close[i] == close[i-1] → "h" (hold/horizontal)
    """

    version = "v2"

    def __init__(self, interval: int = 1, window_size: int = 3):
        """初始化KlinePatternDMU。

        参数:
            interval (int): K线时间间隔，单位为分钟，默认为1。
            window_size (int): 追踪的K线数量，默认为3根。
        """
        super().__init__()
        self.interval = interval
        self.window_size = window_size
        self.close_prices = deque(maxlen=window_size + 1)
        self.pattern = ""
        self._key_completed = f"KlineDMU_v0_{interval}min__completed"
        self._key_close = f"KlineDMU_v0_{interval}min__close"

    def get_param_str(self) -> str:
        return f"{self.interval}min_{self.window_size}"

    def dependencies(self) -> list:
        return [f"KlineDMU_v0_{self.interval}min"]

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        """根据上游 KlineDMU 的输出，追踪已完成K线的收盘价并计算模式。

        参数:
            new_data: 原始行情数据（未直接使用）。
            previous_result (dict): 上游 DMU 输出，需包含 KlineDMU 的 close 和 completed 字段。

        Returns:
            dict: {"pattern": 模式字符串}。
        """
        completed = previous_result.get(self._key_completed, False)

        if not completed:
            return {"pattern": self.pattern}

        close_price = previous_result.get(self._key_close)
        if close_price is None:
            return {"pattern": self.pattern}

        self.close_prices.append(close_price)

        if len(self.close_prices) < self.window_size + 1:
            return {"pattern": self.pattern}

        # 计算相邻K线的涨跌关系
        pattern = ""
        for i in range(1, len(self.close_prices)):
            if self.close_prices[i] > self.close_prices[i - 1]:
                pattern += "u"
            elif self.close_prices[i] < self.close_prices[i - 1]:
                pattern += "d"
            else:
                pattern += "h"

        self.pattern = pattern
        return {"pattern": self.pattern}

    def on_end_of_day(self):
        """日终重置。"""
        self.close_prices.clear()
        self.pattern = ""
