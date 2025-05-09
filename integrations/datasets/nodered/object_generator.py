import os
from io import StringIO

from pyecore.resources import ResourceSet

from metamodel import nodered_package

class Output:
    def __init__(self):
        self.output = StringIO()

    def start(self):
        self.output.write('<s>')
        return self

    def end(self):
        self.output.write('</s>')
        self.output.write('\n')
        return self

    def token(self, str) -> 'Output':
        self.output.write(str)
        self.output.write(' ')
        return self

    def nl(self) -> 'Output':
        # self.output.write('<EOL>')
        return self

    def save_to(self, filename):
        with open(filename, 'w') as f:
            f.write(self.output.getvalue())


def all_nodes(node, processed_nodes: set):
    for next_node in node.next:
        if next_node not in processed_nodes:
            return False
    return True

def generate_root(root, output):
    node_ids = {}
    processed_nodes = set()
    delayed_nodes = {}

    if len(root.nodes) == 0:
        return

    output.start()
    for i, node in enumerate(root.nodes):
        node_ids[node] = i

    for i, node in enumerate(root.nodes):
        print("Processing node: " + str(i))
        gen_node = lambda n: generate_node(n, node_ids, output)

        if all_nodes(node, processed_nodes):
            processed_nodes.add(node)
            gen_node(node)
            for delayed_node in list(delayed_nodes.keys()):
                if all_nodes(delayed_node, processed_nodes):
                    delayed_nodes[delayed_node](delayed_node)
                    processed_nodes.add(delayed_node)
                    delayed_nodes.pop(delayed_node)
        else:
            delayed_nodes[node] = gen_node

    for delayed_node in delayed_nodes.keys():
        delayed_nodes[delayed_node](delayed_node)

    output.end()


def generate_node(node, node_ids, output):
    id = node_ids[node]
    #print("Processing node: " + str(id))

    output.token("create")
    output.token("Node")
    output.token("\"node:" + str(id) + "\"")
    output.token("{")
    output.nl()
    output.token("set").token("type").token("\"" + node.type + "\"").token(";").nl()
    if node.name is not None and node.name.strip() != '':
        output.token("set").token("description").token("\"" + node.name + "\"").token(";").nl()
    for next_node in node.next:
        output.token("ref").token("next").token("\" node:" + str(node_ids[next_node]) + " \"").token(";").nl()

    output.token("}")


def process_files(folder):
    output = Output()
    for path, folders, files in os.walk(folder):
        for filename in files:
            if filename.endswith('.xmi'):
                print("Processing {}".format(os.path.join(path, filename)))

                # Load filename with pyecore
                rset = ResourceSet()
                rset.metamodel_registry[nodered_package.nsURI] = nodered_package
                resource = rset.get_resource(os.path.join(path, filename))
                root = resource.contents[0]
                generate_root(root, output)

    output.save_to('output.txt')

if __name__ == '__main__':
    process_files('output')
