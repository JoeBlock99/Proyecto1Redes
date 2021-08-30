from node import build_demo_nodes, build_nodes


_nodes = build_demo_nodes()

nodes = {}
for node in _nodes:
    nodes[node.name] = node

all_valid = False
while(not all_valid):
    all_valid_holder = True
    for node_key in nodes:
        node = nodes[node_key]
        payload = node.create_destinations_payload()
        adyacents = node.adyacents
        for adyacent in adyacents:
            nodes[adyacent["node"]].recieve_from_adyacent(payload)

        all_valid_holder = node.is_ready and all_valid_holder
    all_valid = all_valid_holder

print("\nResultados")
for node_key in nodes:
    node = nodes[node_key]
    print(node.name)
    print(node.get_next_node("user2"))
