from more_itertools import unique_everseen


def transform_triplets_into_api_edges_and_nodes(triplets):
    data = {'nodes': [], 'edges': []}
    for i, triplet in enumerate(triplets):
        from_node = triplet[0]
        to_node = triplet[2]
        relation = triplet[1]
        data['nodes'].append({'id': from_node, 'label': from_node})
        data['nodes'].append({'id': to_node, 'label': to_node})
        data['edges'].append({'from': from_node, 'to': to_node, 'label': relation, 'arrows': 'to'})

    data['nodes'] = list(unique_everseen(data['nodes'], key=dict))
    data['edges'] = list(unique_everseen(data['edges'], key=dict))

    return data
