# lrbt

Private factors and units built on top of the [RBT](https://github.com/liuch288/rbt) framework.

## Structure

```
lrbt/
├── lrbt/
│   ├── dmu/          # Decision making unit extensions
│   ├── ic/           # IC (Information Coefficient) calculator extensions
│   ├── peu/          # Position & execution unit extensions
│   └── util/         # Utility functions
├── test_lrbt/        # Tests
├── setup.py
└── README.md
```

## 安装

```bash
pip install -e .
```

## DMU (Decision Making Unit)

### AtrDMU
ATR（Average True Range，平均真实波幅）决策单元。将行情按固定条数划分单元，计算每个单元的振幅 TR，再取均值得到 ATR。

```python
from lrbt.dmu import AtrDMU

# n: TR 均值窗口大小, mds_per_unit: 每单元行情条数, reset_on_eod: 是否日终重置
dmu = AtrDMU(n=14, mds_per_unit=60, reset_on_eod=True)
```

依赖: `MdDMU_v0`

输出:
- `atr`: 平均真实波幅
- `tr`: 当前单元振幅
- `diff`: tr - atr

### KlinePatternDMU
K线模式决策单元。追踪过去 N 根已完成 K 线的收盘价，输出相邻涨跌方向模式字符串。

```python
from lrbt.dmu import KlinePatternDMU

# interval: K线分钟间隔, window_size: 追踪K线数量, reset_on_eod: 是否日终重置
dmu = KlinePatternDMU(interval=1, window_size=3, reset_on_eod=True)
```

依赖: `KlineDMU_v0_{interval}min`

输出:
- `pattern`: 方向模式字符串，如 `"udu"`（u=涨, d=跌, h=平）
