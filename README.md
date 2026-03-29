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

### SimpleTrendDMU
Simple trend following using moving average crossover.

**Usage:**
```python
from lrbt.dmu import SimpleTrendDMU

dmu = SimpleTrendDMU(fast_period=10, slow_period=30)
result = dmu.make_decision(new_data, prev_result)
```

**Returns:**
- `signal`: 1 (uptrend), -1 (downtrend), 0 (neutral)
- `hits`: +1 on bullish crossover, -1 on bearish crossover
- `fast_ma`, `slow_ma`: Current moving averages
- `diff`: Difference between fast and slow MAs

### MeanRevertDMU
Mean reversion using Bollinger Band logic.

**Usage:**
```python
from lrbt.dmu import MeanRevertDMU

dmu = MeanRevertDMU(period=20, std_dev=2.0)
result = dmu.make_decision(new_data, prev_result)
```

**Returns:**
- `signal`: 1 (oversold), -1 (overbought), 0 (neutral)
- `z_score`: Standard deviations from mean
- `mean`, `upper`, `lower`: Bollinger Bands
- `std`: Rolling standard deviation

### BreakoutDMU
Detects price channel breakouts.

**Usage:**
```python
from lrbt.dmu import BreakoutDMU

dmu = BreakoutDMU(period=20)
result = dmu.make_decision(new_data, prev_result)
```

**Returns:**
- `signal`: 1 (breakout above), -1 (breakout below), 0 (no breakout)
- `hits`: +1 on upside breakout, -1 on downside breakout
- `max_price`, `min_price`: Rolling high/low
- `channel_width`: Width of the price channel
- `position_pct`: Price position within channel (0-1)
