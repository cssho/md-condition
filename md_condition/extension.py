from markdown import Markdown
from markdown.extensions import Extension

from md_condition.preprocessor import ConditionPreprocessor


class ConditionExtension(Extension):
    def __init__(self, **kwargs) -> None:
        self.config = {
            "symbol": ["", "Condition symbol"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        md.preprocessors.register(ConditionPreprocessor(md, self), "condition", 50)
