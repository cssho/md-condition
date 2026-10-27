from typing import Any

from md_condition.extension import ConditionExtension
from md_condition.preprocessor import ConditionSyntaxError

__all__ = ["ConditionExtension", "ConditionSyntaxError", "makeExtension"]


def makeExtension(**kwargs: Any) -> ConditionExtension:
    return ConditionExtension(**kwargs)
