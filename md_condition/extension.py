from markdown.extensions import Extension
from md_condition.preprocessor import ConditionPreprocessor


class ConditionExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'symbol': ['', 'Condition syombol'],
        }
        super(ConditionExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            ConditionPreprocessor(md, self),
            'condition',
            50)