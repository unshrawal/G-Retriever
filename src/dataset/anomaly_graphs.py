import os
import pandas as pd
import torch
from tqdm import tqdm
from torch.utils.data import Dataset
from src.dataset.utils.retrieval import retrieval_via_pcst


model_name = 'sbert'
path = 'dataset/anomaly_graphs'
path_nodes = f'{path}/nodes'
path_edges = f'{path}/edges'
path_graphs = f'{path}/graphs'

path_nodes_ood = f'{path}/nodes_ood'
path_edges_ood = f'{path}/edges_ood'
path_graphs_ood = f'{path}/graphs_ood'

cached_graph = f'{path}/cached_graphs'
cached_desc = f'{path}/cached_desc'


class AnomalyGraphsDataset(Dataset):
    def __init__(self, use_ood=False):
        super().__init__()
        self.prompt = "Answer the question"
        self.graph = None
        self.graph_type = 'Anomaly Graph'
        self.use_ood = use_ood

        if use_ood:
            self.questions = pd.read_csv(f'{path}/OODQuestions.csv')
            self.graphs_path = f'{path}/graphs_ood'
            self.cached_graph = f'{path}/cached_ood_graphs'
            self.cached_desc = f'{path}/cached_ood_desc'
        else:
            self.questions = pd.read_csv(f'{path}/questions.csv')
            self.graphs_path = f'{path}/graphs'
            self.cached_graph = f'{path}/cached_graphs'
            self.cached_desc = f'{path}/cached_desc'

    def __len__(self):
        """Return the len of the dataset."""
        return len(self.questions)

    def __getitem__(self, index):
        data = self.questions.iloc[index]
        question = f'Question: {data["question"]}\n\nAnswer:'
        graph = torch.load(f'{self.cached_graph}/{index}.pt')
        desc = open(f'{self.cached_desc}/{index}.txt', 'r').read()

        return {
            'id': index,
            'image_id': data['image_id'],
            'question': question,
            'label': data['answer'],
            'full_label': data['full_answer'],
            'graph': graph,
            'desc': desc,
        }

    def get_idx_split(self):

        # Load the saved indices
        path_split = f'{path}/split'
        with open(f'{path_split}/train_indices.txt', 'r') as file:
            train_indices = [int(line.strip()) for line in file]
        with open(f'{path_split}/val_indices.txt', 'r') as file:
            val_indices = [int(line.strip()) for line in file]
        with open(f'{path_split}/test_indices.txt', 'r') as file:
            test_indices = [int(line.strip()) for line in file]

        return {'train': train_indices, 'val': val_indices, 'test': test_indices}


def preprocess(graphs_path, path_nodes, path_edges, use_ood=False):
    if use_ood:
        cached_graph = f'{path}/cached_ood_graphs'
        cached_desc = f'{path}/cached_ood_desc'
        questions = pd.read_csv(f'{path}/OODQuestions.csv')
        graphs_path = f'{path}/graphs_ood'
        q_embs = torch.load(f'{path}/q_embs_ood.pt')
    else:
        cached_graph = f'{path}/cached_graphs'
        cached_desc = f'{path}/cached_desc'
        questions = pd.read_csv(f'{path}/questions.csv')
        graphs_path = f'{path}/graphs'
        q_embs = torch.load(f'{path}/q_embs.pt')

    assert len(questions) == q_embs.shape[0], "Mismatch between number of questions and embeddings"

    os.makedirs(cached_desc, exist_ok=True)
    os.makedirs(cached_graph, exist_ok=True)

    for index in tqdm(range(len(questions))):
        if os.path.exists(f'{cached_graph}/{index}.pt'):
            continue
        image_id = questions.iloc[index]['image_id']
        graph = torch.load(f'{graphs_path}/{image_id}.pt')
        nodes = pd.read_csv(f'{path_nodes}/{image_id}.csv')
        edges = pd.read_csv(f'{path_edges}/{image_id}.csv')
        subg, desc = retrieval_via_pcst(graph, q_embs[index], nodes, edges, topk=3, topk_e=3, cost_e=0.5)
        torch.save(subg, f'{cached_graph}/{index}.pt')
        open(f'{cached_desc}/{index}.txt', 'w').write(desc)


if __name__ == '__main__':
    # Process the in-distribution data
    preprocess(path_graphs, path_nodes, path_edges, use_ood=False)

    # Process the OOD data
    preprocess(path_graphs_ood, path_nodes_ood, path_edges_ood, use_ood=True)

    # Initialize and print the in-distribution dataset
    dataset = AnomalyGraphsDataset(use_ood=False)
    data = dataset[0]
    for k, v in data.items():
        print(f'{k}: {v}')

    # Print the data split sizes for in-distribution
    split_ids = dataset.get_idx_split()
    for k, v in split_ids.items():
        print(f'# {k}: {len(v)}')

    # Initialize and print the OOD dataset
    ood_dataset = AnomalyGraphsDataset(use_ood=True)
    ood_data = ood_dataset[0]
    for k, v in ood_data.items():
        print(f'{k}: {v}')