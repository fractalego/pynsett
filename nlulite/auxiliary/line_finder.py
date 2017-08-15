class LineFinder:
    def __init__(self, text):
        self.text = text

    def get_line_number(self, string):
        position = self.text.find(string)
        if position == -1:
            return -1
        return self.text[:position + 1].count('\n') + 1
