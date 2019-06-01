import re
import sys
import logging

from pynsett.discourse import Discourse
from pynsett.drt import Drs, DrsRule
from pynsett.knowledge.drs_ner_cleaner import DrsNERCleaner
from pynsett.metric import MetricFactory

_logger = logging.getLogger(__name__)


def _get_list_of_rules_from_text(text):
    lines = []
    for line in text.split('\n'):
        if not line.strip() or line.strip()[0] == '#':
            continue
        lines.append(line)
    lines = '\n'.join(lines).split(';')
    return lines


def _substitute_text_in_match_statement_with_graph(text, substitution_triggers):
    drs_cleaner = DrsNERCleaner(substitution_triggers)
    p = re.compile('MATCH.*\"(.*)\"')
    lst = p.findall(text)
    if not lst:
        p = re.compile('MATCH.*\'(.*)\'')
        lst = p.findall(text)
    for item in lst:
        try:
            drs = Discourse(item).connected_components[0]
        except IndexError:
            _logger.warning('Cannot use Discourse on %s' % item[:200])
            drs = Drs.create_from_natural_language(item)
        drs = drs.apply(drs_cleaner)
        text = text.replace('"' + item + '"', str(drs))
    return text


def _substitute_relationship_code_in_create_statement_with_graph(text):
    matching_variables = []
    p = re.compile('CREATE.*\((.*)\)')
    lst = p.findall(text)
    for item in lst:
        try:
            elements = item.split()
            relation_name = elements[0]
            source = elements[1]
            target = elements[2]
            matching_variables += [source, target]
            new_text = "{}(%s), {'type': 'relation', 'text': '%s'}(%s,%s), {}(%s)" \
                       % (source, relation_name, source, target, target)
            text = text.replace('(' + item + ')', new_text)
        except:
            _logger.warning('Text ' + text + " cannot parse to a relation")
    return text, matching_variables


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
    def __init__(self, metric=MetricFactory.get_best_available_metric()):
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
        substitution_triggers = []
        rules_lines = _get_list_of_rules_from_text(text)
        for rule_text in rules_lines:
            original_rule_text = rule_text
            if not rule_text.strip():
                continue
            for s in self._substitution_list:
                rule_text = _substitute_string_into_rule(rule_text, s)
            rule_text = _substitute_text_in_match_statement_with_graph(rule_text, substitution_triggers)
            rule_text, matching_variables = _substitute_relationship_code_in_create_statement_with_graph(rule_text)
            substitution = _get_substition_rule(rule_text)
            if substitution:
                self.metric = _substitute_list_into_metric(self._metric, substitution)
                substitution_triggers.append(substitution[0].strip())
                if not _looks_like_list(substitution[1]):
                    self._substitution_list.append(substitution)
                continue
            try:
                rule = DrsRule(rule_text, self._metric, matching_variables)
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
