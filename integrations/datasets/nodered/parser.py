import json
from metamodel import Node, Root
from pyecore.resources import ResourceSet

def load_node_red_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_node_red_file(file_path):
    data = load_node_red_file(file_path)
    model = Root()
    for node in data:
        print(node)
        new_node = Node()
        new_node.type = node['type']
        print(model)

        model.nodes.append(new_node)

    rset = ResourceSet()
    resource = rset.create_resource('/tmp/example.xmi')
    resource.append(model)
    resource.save()


if __name__ == '__main__':
    parse_node_red_file('/tmp/example.json')
