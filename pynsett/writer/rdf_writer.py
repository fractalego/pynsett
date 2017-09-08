class RDFWriter:
    def __init__(self, drs):
        self.drs = drs

    def write(self):
        g = self.drs.graph.g
        verbs = g.vs.select(tag_eq="v")
        return_items = []
        parsing_items = []
        for item in g.vs:
            if item['tag'] == 'IN':
                continue
            parsing_items.append(item)
        for pos, item in enumerate(parsing_items):
            for neighbor in g.vs[g.neighbors(item, mode="out")]:
                word = neighbor['word']
                tag = neighbor['tag']
                if tag != 'IN':
                    continue
                next_neighbors = g.vs[g.neighbors(neighbor, mode="out")]
                for nn in next_neighbors:
                    if nn != item:
                        return_items.append((str(item['word']) + '::' + str(item['name']),
                                             str(neighbor['word']) + '::' + str(neighbor['name']),
                                             str(nn['word']) + '::' + str(nn['name'])))
        return return_items
