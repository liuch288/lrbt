# lrbt

Private factors and units built on top of the [RBT](https://github.com/your/rbt) framework.

## Structure

```
lrbt/
├── lrbt/
│   ├── factors/      # 私有因子（FactorBase 子类）
│   ├── units/        # 私有 Unit（rbt.unit.Unit 子类）
│   ├── util/        # 工具函数
│   ├── md/           # Market data extensions
│   ├── peu/          # Position & execution unit extensions
│   ├── ic/           # IC calculator extensions
│   ├── result_db/    # Result DB extensions
│   └── dmu/          # Decision making unit extensions
├── test_lrbt/        # 测试
├── setup.py
└── README.md
```

## 安装

```bash
pip install -e .
```
