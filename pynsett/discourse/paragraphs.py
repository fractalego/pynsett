class BaseParagraphTokenizer:
    def get_paragraphs(self, text):
        raise NotImplementedError('Please implement get_paragraphs(text)')


class SimpleParagraphTokenizer(BaseParagraphTokenizer):
    def get_paragraphs(self, text):
        return text.split('\n\n')
