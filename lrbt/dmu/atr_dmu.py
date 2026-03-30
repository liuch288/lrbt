from rbt.ic import MeanIC
from rbt.dmu import DecisionMakingUnit
import numpy as np

from rbt.ic import MinMaxIC


class AtrDMU(DecisionMakingUnit):
    version = "v0"

    def __init__(self, n, mds_per_unit):
        """
        初始化ATRDMU。

        参数:
            n (int): ATR窗口大小。
        """
        super().__init__()
        self.n = n
        self.mds_per_unit = mds_per_unit
        self.counted_mds = 0
        self.tr_mean = MeanIC(n)
        self.minmax = MinMaxIC()
        self.tr = 0
        self.atr = 0
        self.update_unit_name()  # 更新单元名称

    def get_param_str(self) -> str:
        """
        生成参数信息，用于更新单元名称。

        Returns:
            str: 载明参数的字符串。
        """
        return f"{self.n}_{self.mds_per_unit}"

    def make_decision(self, new_data, previous_result: dict = {}) -> dict:
        """
        计算ATR指标值。

        参数:
            new_data (float): 新的行情数据。
            previous_result (dict): 上一次的计算结果，包含ATR值。

        Returns:
            dict: 包含ATR值的决策结果。
        """
        mid = previous_result["MdDMU_v0_mid"]
        mm_res = self.minmax.update(mid)
        self.counted_mds += 1
        if self.counted_mds >= self.mds_per_unit:
            self.tr = mm_res["max"] - mm_res["min"]
            self.atr = self.tr_mean.update(self.tr)
            self.minmax.reset()
            self.counted_mds = 0
        return {"atr": self.atr, "tr": self.tr, "diff": self.tr - self.atr}
