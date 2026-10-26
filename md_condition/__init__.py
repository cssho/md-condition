from md_condition.extension import ConditionExtension

__all__ = ["ConditionExtension", "makeExtension"]


def makeExtension(**kwargs) -> ConditionExtension:
    return ConditionExtension(**kwargs)
