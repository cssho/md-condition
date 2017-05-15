from markdown.extensions import Extension
from md_condition.preprocessor import ConditionPreprocessor


class ConditionExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'condition': ['', 'Condition syombol'],
        }
        super(ConditionExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        md.preprocessor.add('condition',
            ConditionProcessor(md),
            '>html_block')
        md.registerExtension(self)

def makeExtension(**kwargs):
    return ConditionExtension(**kwargs)