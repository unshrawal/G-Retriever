import os
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
import torch
from torch_geometric.data.data import Data
from src.utils.lm_modeling import load_model, load_text2embedding
from sklearn.model_selection import train_test_split


model_name = 'sbert'
path = 'dataset/anomaly_graphs'
path_nodes = f'{path}/nodes'
path_edges = f'{path}/edges'
path_graphs = f'{path}/graphs'

path_nodes_ood = f'{path}/nodes_ood'
path_edges_ood = f'{path}/edges_ood'
path_graphs_ood = f'{path}/graphs_ood'


def textualize_graph(data):
    # mapping from object id to index
    objectid2nodeid = {object_id: idx for idx, object_id in enumerate(data['objects'].keys())}
    nodes = []
    edges = []
    for objectid, object in data['objects'].items():
        # nodes
        node_attr = f'name: {object["name"]}'
        if len(object['attributes']) > 0:
            node_attr = node_attr + '; attribute: ' + (', ').join(object["attributes"])
        if 'anomaly_flag' in object:
            anomaly_reason = object['anomaly_reason']
            node_attr += '; (anomaly_information): there is an anomaly because ' + str(anomaly_reason)
            

        nodes.append({'node_id': objectid2nodeid[objectid], 'node_attr': node_attr})

        # edges
        for rel in object['relations']:
            src = objectid2nodeid[objectid]
            dst = objectid2nodeid[rel['object']]
            edge_attr = rel['name']
            edges.append({'src': src, 'edge_attr': edge_attr, 'dst': dst})

    return nodes, edges


def step_one(dataset_path, _path_nodes, _path_edges):
    dataset = json.load(open(dataset_path))

    os.makedirs(_path_nodes, exist_ok=True)
    os.makedirs(_path_edges, exist_ok=True)

    for imageid, object in tqdm(dataset.items(), total=len(dataset)):
        node_attr, edge_attr = textualize_graph(object)
        pd.DataFrame(node_attr, columns=['node_id', 'node_attr']).to_csv(f'{_path_nodes}/{imageid}.csv', index=False)
        pd.DataFrame(edge_attr, columns=['src', 'edge_attr', 'dst']).to_csv(f'{_path_edges}/{imageid}.csv', index=False)


def step_two(_path, _path_nodes, _path_edges, question_path, _path_graph, q_emb_fn):
    def _encode_questions(_path, q_emb_fn):
        q_embs = text2embedding(model, tokenizer, device, df.question.tolist())
        torch.save(q_embs, f'{_path}/{q_emb_fn}')

    def _encode_graphs(_path_nodes, _path_edges, _path_graph):
        image_ids = df.image_id.unique()
        for i in tqdm(image_ids):
            nodes = pd.read_csv(f'{_path_nodes}/{i}.csv')
            edges = pd.read_csv(f'{_path_edges}/{i}.csv')
            node_attr = text2embedding(model, tokenizer, device, nodes.node_attr.tolist())
            edge_attr = text2embedding(model, tokenizer, device, edges.edge_attr.tolist())
            edge_index = torch.tensor([edges.src, edges.dst]).long()
            pyg_graph = Data(x=node_attr, edge_index=edge_index, edge_attr=edge_attr, num_nodes=len(nodes))
            torch.save(pyg_graph, f'{_path_graph}/{i}.pt')

    df = pd.read_csv(question_path)
    os.makedirs(_path_graph, exist_ok=True)
    model, tokenizer, device = load_model[model_name]()
    text2embedding = load_text2embedding[model_name]

    _encode_questions(_path, q_emb_fn)
    _encode_graphs(_path_nodes, _path_edges, _path_graph)

def generate_split():
    # Load the data
    path = "dataset/anomaly_graphs"
    questions = pd.read_csv(f"{path}/questions.csv")

    # Create a unique list of image IDs
    unique_image_ids = questions['image_id'].unique()

    # Shuffle the image IDs
    np.random.seed(42)  # For reproducibility
    shuffled_image_ids = np.random.permutation(unique_image_ids)

    # Split the image IDs into train, validation, and test sets
    train_ids, temp_ids = train_test_split(shuffled_image_ids, test_size=0.4, random_state=42)  # 60% train, 40% temporary
    val_ids, test_ids = train_test_split(temp_ids, test_size=0.5, random_state=42)  # Split the 40% into two 20% splits

    # Create a mapping from image ID to set label
    id_to_set = {image_id: 'train' for image_id in train_ids}
    id_to_set.update({image_id: 'val' for image_id in val_ids})
    id_to_set.update({image_id: 'test' for image_id in test_ids})

    # Map the sets back to the original DataFrame
    questions['set'] = questions['image_id'].map(id_to_set)

    # Create the final train, validation, and test DataFrames
    train_df = questions[questions['set'] == 'train']
    val_df = questions[questions['set'] == 'val']
    test_df = questions[questions['set'] == 'test']

    # Create a folder for the split
    os.makedirs(f'{path}/split', exist_ok=True)

    # Writing the indices to text files
    train_df.index.to_series().to_csv(f'{path}/split/train_indices.txt', index=False, header=False)
    val_df.index.to_series().to_csv(f'{path}/split/val_indices.txt', index=False, header=False)
    test_df.index.to_series().to_csv(f'{path}/split/test_indices.txt', index=False, header=False)

if __name__ == '__main__':
    step_one("dataset/anomaly_graphs/graph_dataset.json", path_nodes, path_edges)
    step_two(path, path_nodes, path_edges, "dataset/anomaly_graphs/questions.csv", path_graphs, "q_embs.pt")
    generate_split()
    step_one("dataset/anomaly_graphs/cutscenes.json", path_nodes_ood, path_edges_ood)
    step_two(path, path_nodes_ood, path_edges_ood, "dataset/anomaly_graphs/OODQuestions.csv", path_graphs_ood, "q_embs_ood.pt")