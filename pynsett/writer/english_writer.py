class EnglishWriter:
    def __init__(self, drs):
        self.drs = drs

    def write(self):
        g = self.drs.graph.g
        verbs = g.vs.select(tag_eq="v")
        return_items = []
        for verb in verbs:
            return_items.append(verb)
        for pos, item in enumerate(return_items):
            for neighbor in g.vs[g.neighbors(item, mode="out")]:
                word = neighbor['word']
                tag = neighbor['tag']
                if tag != 'IN':
                    continue

                if word == 'NSUBJ' or word == 'ADJECTIVE':
                    next_neighbors = g.vs[g.neighbors(neighbor, mode="out")]
                    for nn in next_neighbors:
                        try:
                            return_items.index(nn)
                            continue
                        except:
                            if nn != item:
                                return_items.insert(pos, nn)
                                break
                else:
                    if word != 'DOBJ' and word != 'DATIVE' and word != 'ATTR':
                        try:
                            return_items.index(neighbor)
                        except:
                            return_items.append(neighbor)
                    next_neighbors = g.vs[g.neighbors(neighbor, mode="out")]
                for nn in next_neighbors:
                    try:
                        return_items.index(nn)
                        continue
                    except:
                        if nn != item:
                            return_items.append(nn)
                            break

        return str([item['word'] for item in return_items])
