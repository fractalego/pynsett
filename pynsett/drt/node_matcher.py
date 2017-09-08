from parvusdb.utils.node_matcher import StringNodeMatcher


class VectorNodeMatcher(StringNodeMatcher):
    """
    Checks whether one dict is contained into another one.
    The word within each node is compared according to vector distance.
    """

    threshold = 5.8

    def __init__(self, metric):
        self.metric = metric

    def _match(self, key, lhs, rhs):
        if key == 'entity':
            return lhs == rhs

        if key == 'compound':
            return True

        if key == 'tag':
            if lhs == '*' or rhs == '*':
                return True

        if key == 'word':
            if lhs == '*' or rhs == '*':
                return True
            return self.metric.similarity(lhs, rhs) < self.threshold

        return StringNodeMatcher._match(self, key, lhs, rhs)
