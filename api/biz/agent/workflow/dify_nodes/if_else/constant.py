from typing import List

# 定义每个 case 内多个条件之间的逻辑关系
LOGICAL_OPERATORS: List[str] = [
    "and",
    "or",
]

# 定义支持的条件比较操作符
COMPARISON_OPERATORS: List[str] = [
    "contains",
    "not contains",
    "start with",
    "end with",
    "is",
    "is not",
    "empty",
    "not empty",
]
