from constants import XMPP_DOMAIN
import json


class Node:
    def __init__(self, adyacents, name):
        self.name = name
        self.adyacents = []
        self.table = {}
        self.counter = 0
        for adyacent in adyacents:
            self.adyacents.append({
                "weight": adyacent["weight"],
                "node": adyacent["node"]
            })

    @property
    def destination_names(self):
        destinations = []
        for destination in self.table:
            if self.table[destination]["weight"] is not None:
                destinations.append(destination)
        return destinations

    @property
    def table_contains_none(self):
        for d in self.table:
            if self.table[d]["weight"] is None:
                return True
        return False

    @property
    def is_ready(self):
        return not self.table_contains_none and self.counter >= 4

    def compute_username(self, name):
        return name.lower() + "@" + XMPP_DOMAIN

    def get_next_node(self, target):
        target = self.table[target]
        if target["next"] is None:
            return None
        else:
            return target["next"]

    def compute_table(self, nodes):
        nodes_names = [node for node in nodes]

        for node in nodes_names:
            self.table[node] = {
                "weight": None,
                "next": None
            }

        self.table[self.name]["weight"] = 0
        self.table[self.name]["next"] = None
        for adyacent in self.adyacents:
            self.table[adyacent["node"]]["weight"] = adyacent["weight"]
            self.table[adyacent["node"]]["next"] = None

    def create_destinations_payload(self):
        payload = {
            "name": self.name,
            "data": []
        }
        for node_destination in self.destination_names:
            destination_info = self.table[node_destination]
            payload["data"].append(
                {"name": node_destination, "info": destination_info}
            )
        return payload

    def recieve_from_adyacent(self, adyacent_info):
        data = adyacent_info["data"]
        name = adyacent_info["name"]
        adyacent_info = self.table[name]
        for destination_dictionary in data:
            destination_name = destination_dictionary["name"]
            destination_info = destination_dictionary["info"]

            if destination_name not in self.destination_names:
                self.table[destination_name]["weight"] = destination_info["weight"] + \
                    adyacent_info["weight"]
                self.table[destination_name]["next"] = name
                self.counter = 0
            else:
                current_weight = self.table[destination_name]["weight"]
                new_weight = destination_info["weight"] + \
                    adyacent_info["weight"]
                if new_weight < current_weight:
                    self.table[destination_name]["weight"] = new_weight
                    self.table[destination_name]["next"] = name
                    self.counter = 0
                else:
                    self.counter += 1


def build_nodes(json_file_name):
    f = open(json_file_name)
    data = json.load(f)
    nodes_names = [_node["name"] for _node in data]
    nodes = []
    for _node in data:
        adyacents = []
        for adyacent in _node["adyacents"]:
            adyacents.append({
                "weight": _node["adyacents"][adyacent],
                "node": adyacent
            })
        node = Node(adyacents, _node["name"])
        node.compute_table(nodes_names)
        nodes.append(node)
    return nodes


def build_prod_nodes():
    return build_nodes("nodes.json")


def build_demo_nodes():
    return build_nodes('nodes_demo.json')
