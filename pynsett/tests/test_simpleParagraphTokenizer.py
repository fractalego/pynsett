from unittest import TestCase

from pynsett.discourse.paragraphs import SimpleParagraphTokenizer


class TestSimpleParagraphTokenizer(TestCase):

    def test_splitting(self):
        text = "This is only a test.\n\nAnd this is a new paragraph."

        paragraph_tok = SimpleParagraphTokenizer()
        paragraphs = paragraph_tok.get_paragraphs(text)

        expected_paragraphs = ['This is only a test.', 'And this is a new paragraph.']

        self.assertEqual(paragraphs, expected_paragraphs)

