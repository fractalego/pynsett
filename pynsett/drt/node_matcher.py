from parvusdb.utils.node_matcher import StringNodeMatcher


class VectorNodeMatcher(StringNodeMatcher):
    """
    Checks whether one dict is contained into another one.
    The word within each node is compared according to vector distance.
    """

    _threshold = 5

    def __init__(self, metric):
        self._metric = metric

    def _match(self, key, lhs, rhs):
        if key == 'gender_guess':
            return True

        if key == 'refers_to':
            return True

        if key == 'is_head_token':
            return True

        if key == 'negated':
            return lhs == rhs

        if key == 'entity':
            return lhs == rhs

        if key == 'type':
            return lhs == rhs

        if key == 'compound':
            return True

        if key == 'tag':
            if lhs == '*' or rhs == '*':
                return True
            return lhs == rhs

        if key == 'word':
            return True

        if key == 'lemma':
            if lhs == '*' or rhs == '*':
                return True
            return self._metric.similarity(lhs, rhs) < self._threshold

        return StringNodeMatcher._match(self, key, lhs, rhs)
