import json

from integrations.datasets.nodered.metamodel import nodered_package
from metamodel import Node, Root
from pyecore.resources import ResourceSet
import os

def load_node_red_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_node_red_github_dataset(folder, output_folder):
    for path, folders, files in os.walk(folder):
        for filename in files:
            if filename.endswith('.json'):
                try:
                    print("Parsing {}".format(os.path.join(path, filename)))
                    full_path = os.path.join(path, filename)
                    xmi_name = filename.replace('.json', '.xmi')
                    target_path = os.path.join(output_folder, path, xmi_name)
                    target_path = target_path.replace(folder, '')
                    parse_node_red_file(full_path, save_to=target_path)

                except Exception as e:
                    print("Cannot parse {}".format(os.path.join(path, filename)), str(e))

def parse_node_red_scrapped_dataset(file_path, output_folder):
    "This refers to the dataset extracted from the NodeRED website, as a single json file"
    all_data = load_node_red_file(file_path)
    count = 1
    for data in all_data:
        model = process_node_red_node(data['flow'])
        if model is None:
            continue

        rset = ResourceSet()
        resource = rset.create_resource(os.path.join(output_folder, 'model_' + str(count) + '.xmi'))
        resource.append(model)
        resource.save()
        
        count = count + 1
    
def parse_node_red_file(file_path, save_to='example.xmi'):
    data = load_node_red_file(file_path)
    model = process_node_red_node(data)

    if save_to is not None:
        os.makedirs(os.path.dirname(save_to), exist_ok=True)
        rset = ResourceSet()
        resource = rset.create_resource(save_to)
        resource.append(model)
        resource.save()

def process_node_red_node(data):
    model = Root()
    created_nodes = {}
    for node in data:
        #assert 'id' in node, "No id found in " + str(node)
        #assert 'type' in node, "No type found in " + str(node)
        if 'id' not in node:
            print("Missing 'id' in node: " + str(node))
            return None

        if 'type' not in node:
            print("No type found in " + str(node))
            return None

        type = node['type']
        if type == 'tab':
            continue

        name = node['name'] if 'name' in node else ''

        new_node = Node()
        new_node.type = type
        new_node.name = name

        created_nodes[node['id']] = new_node

        model.nodes.append(new_node)

    for node in data:
        if not 'wires' in node:
            continue

        tranformed_node = created_nodes[node['id']]
        wired_nodes = node['wires']
        # This is probably not fully correct.
        # The thing is that 'wires' is a list of list of ids
        # What is the meaning of this? For the moment we flatten the
        # nested list of ids, but this is probably "semantically incorrect"
        wired_nodes = sum(wired_nodes, [])

        for next_node_id in wired_nodes:
            if next_node_id in created_nodes:
                next_node = created_nodes[next_node_id]
                tranformed_node.next.append(next_node)

    return model

if __name__ == '__main__':
#    parse_node_red_file('/tmp/example.json')
#    parse_node_red_scrapped_dataset('data/nodered_flows.json', output_folder='output/web')
    parse_node_red_github_dataset('data/nodered-github', output_folder='output/github')

    # Serialize the metamodel, so that it can be used to load the generated XMIs generically
    rset = ResourceSet()
    resource = rset.create_resource("nodered.ecore")
    resource.append(nodered_package)
    resource.save()