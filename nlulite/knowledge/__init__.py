import logging
from nlulite.drt import Drs, DrsRule

logging.basicConfig()


def _get_list_of_rules_from_text(text):
    lines = []
    for line in text.split('\n'):
        if not line.strip() or line.strip()[0] == '#':
            continue
        lines.append(line)
    lines = '\n'.join(lines).split(';')
    return lines


def _substitute_text_with_graph(text):
    import re
    p = re.compile('MATCH.\"(.*)\"')
    lst = p.findall(text)
    if not lst:
        p = re.compile('MATCH.\'(.*)\'')
        lst = p.findall(text)
    for item in lst:
        drs = Drs.create_from_natural_language(item)
        text = text.replace('"' + item + '"', str(drs))
    return text


class Knowledge:
    def __init__(self, metric):
        self.rules = []
        self.metric = metric

    def add_drs(self, drs, sentence_number=None):
        pass

    def add_rule(self, rule, weight=1.0):
        self.rules.append((rule, weight))

    def add_rules(self, text):
        rules_lines = _get_list_of_rules_from_text(text)
        for rule_text in rules_lines:
            rule_text = _substitute_text_with_graph(rule_text)
            if not rule_text.strip():
                continue
            self.add_rule(DrsRule(rule_text, self.metric))

    def ask_drs(self, drs):
        pass

    def ask_rule(self, drs):
        return self.rules

    def ask_rule_fw(self, drs):
        return self.rules

    def ask_rule_bw(self, drs):
        return self.rules
