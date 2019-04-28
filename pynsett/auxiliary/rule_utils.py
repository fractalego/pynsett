def _make_names_unique(g, i):
    for v in g.vs:
        v['name'] += str(i)
    for e in g.es:
        e['name'] += str(i)


def _restore_original_names(g, i):
    for v in g.vs:
        v['name'] = v['name'][0:-i]
    for e in g.es:
        e['name'] = e['name'][0:-i]


def repeat_db_rules_n_times(db, rules, n):
    import copy
    old_g = copy.deepcopy(db.get_graph())
    for i in range(n):
        db.query(rules, repeat_n_times=1)
        g = db.get_graph()
        if old_g == g:
            break
        _make_names_unique(db.get_graph(), i)
        old_g = g
    _restore_original_names(g, i)
    return db


