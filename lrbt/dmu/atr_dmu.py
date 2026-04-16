from rbt.dmu import DecisionMakingUnit
from rbt.ic import MeanIC, MinMaxIC


class AtrDMU(DecisionMakingUnit):
    """ATR（Average True Range，平均真实波幅）决策单元。

    将行情数据按固定条数（mds_per_unit）划分为若干单元，
    在每个单元内通过 MinMaxIC 追踪中间价的最高/最低值，
    计算单元振幅 TR = max - min，再对 TR 取 n 周期均值得到 ATR。

    输出:
        atr: 平均真实波幅。
        tr: 当前单元的真实波幅。
        diff: tr - atr，当前波幅与均值的偏离。
    """

    version = "v0"

    def __init__(self, n, mds_per_unit, reset_on_eod: bool = True):
        """初始化 AtrDMU。

        参数:
            n (int): ATR 均值窗口大小，即对多少个单元的 TR 取平均。
            mds_per_unit (int): 每个单元包含的行情数据条数。
            reset_on_eod (bool): 是否日终重置，默认为 True。
        """
        super().__init__()
        self.n = n
        self.mds_per_unit = mds_per_unit
        self.reset_on_eod = reset_on_eod
        self.counted_mds = 0
        self.tr_mean = MeanIC(n)
        self.minmax = MinMaxIC()
        self.tr = 0
        self.atr = 0

    def get_param_str(self) -> str:
        """
        生成参数信息，用于更新单元名称。

        Returns:
            str: 载明参数的字符串。
        """
        return f"{self.n}_{self.mds_per_unit}_{'r' if self.reset_on_eod else 'c'}"

    def on_end_of_day(self):
        """日终重置，清除日内累积状态。"""
        if not self.reset_on_eod:
            return
        self.counted_mds = 0
        self.tr_mean = MeanIC(self.n)
        self.minmax = MinMaxIC()
        self.tr = 0
        self.atr = 0

    def dependencies(self) -> list:
        return ["MdDMU_v0"]

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        """根据新行情数据更新并计算 ATR。

        每收到一条数据，更新当前单元的 min/max。当累积满 mds_per_unit 条后，
        计算该单元的 TR 并更新 ATR 均值，然后重置进入下一个单元。

        参数:
            new_data: 新的行情数据（未直接使用，通过 previous_result 获取中间价）。
            previous_result (dict): 上游 DMU 的输出，需包含 "MdDMU_v0__mid" 键。

        Returns:
            dict: {"atr": 平均真实波幅, "tr": 当前单元振幅, "diff": tr - atr}。
        """
        mid = previous_result["MdDMU_v0__mid"]
        mm_res = self.minmax.update(mid)
        self.counted_mds += 1
        if self.counted_mds >= self.mds_per_unit:
            self.tr = mm_res["max"] - mm_res["min"]
            self.atr = self.tr_mean.update(self.tr)
            self.minmax.reset()
            self.counted_mds = 0
        return {"atr": self.atr, "tr": self.tr, "diff": self.tr - self.atr}
