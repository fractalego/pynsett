import re
import sys
import logging

from pynsett.drt import Drs, DrsRule
from pynsett.metric import Metric

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
    p = re.compile('MATCH.*\"(.*)\"')
    lst = p.findall(text)
    if not lst:
        p = re.compile('MATCH.*\'(.*)\'')
        lst = p.findall(text)
    for item in lst:
        drs = Drs.create_from_natural_language(item)
        text = text.replace('"' + item + '"', str(drs))
    return text


def _get_substition_rule(line):
    p = re.compile('DEFINE(.*)AS(.*)')
    lst = p.findall(line)
    for item1, item2 in lst:
        return item1, item2


def _create_list_from_string(string):
    string = string.strip()
    if not string or len(string) < 2:
        return []
    string = string[1:-1]
    lst = string.split(',')
    lst = [item.strip() for item in lst]
    return lst


def _looks_like_list(string):
    string = string.strip()
    if string[0] == '[' and string[-1] == ']':
        return True
    return False


def _substitute_list_into_metric(metric, substitution):
    subst_name = substitution[0].strip()
    if _looks_like_list(substitution[1]):
        subst_list = _create_list_from_string(substitution[1])
        metric.add_substitution(subst_name, subst_list)
    return metric


def _substitute_string_into_rule(rule_str, substitution):
    subst_from = substitution[0].strip()
    subst_to = substitution[1].strip()
    rule_str = rule_str.replace(subst_from, subst_to)
    return rule_str


class Knowledge:
    def __init__(self, metric=Metric()):
        self._rules = []
        self._metric = metric
        self._substitution_list = []

    def add_drs(self, drs, sentence_number=None):
        pass

    def add_rule(self, rule, weight=1.0):
        self._rules.append((rule, weight))

    def add_rules(self, text):
        from ..auxiliary import LineFinder
        line_finder = LineFinder(text)

        rules_lines = _get_list_of_rules_from_text(text)
        for rule_text in rules_lines:
            original_rule_text = rule_text
            if not rule_text.strip():
                continue
            for s in self._substitution_list:
                rule_text = _substitute_string_into_rule(rule_text, s)
            rule_text = _substitute_text_with_graph(rule_text)
            substitution = _get_substition_rule(rule_text)
            if substitution:
                self.metric = _substitute_list_into_metric(self._metric, substitution)
                if not _looks_like_list(substitution[1]):
                    self._substitution_list.append(substitution)
                continue
            try:
                rule = DrsRule(rule_text, self._metric)
                rule.test()
                self.add_rule(rule)
            except SyntaxError:
                sys.stderr.write('Error in line ' + str(line_finder.get_line_number(original_rule_text)) + ':\n')
                sys.stderr.write(original_rule_text + '\n')
                sys.stderr.flush()
            finally:
                pass

    def ask_drs(self, drs):
        pass

    def ask_rule(self, drs):
        return self._rules

    def ask_rule_fw(self, drs):
        return self._rules

    def ask_rule_bw(self, drs):
        return self._rules