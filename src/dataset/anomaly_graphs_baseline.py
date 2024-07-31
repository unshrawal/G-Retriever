import pandas as pd
import torch
from torch.utils.data import Dataset


model_name = 'sbert'
path = 'dataset/anomaly_graphs'

class AnomalyGraphsBaselineDataset(Dataset):
    def __init__(self, use_ood=False):

        super().__init__()
        self.prompt = "Answer the question"
        self.graph = None
        self.graph_type = 'Anomaly Graph'
        self.use_ood = use_ood

        if use_ood:
            self.questions = pd.read_csv(f'{path}/OODQuestions.csv')
            self.cached_graph = f'{path}/cached_ood_graphs'
            self.cached_desc = f'{path}/cached_ood_desc'
            self.path_nodes = f'{path}/nodes_ood'
            self.path_edges = f'{path}/edges_ood'
            self.path_graphs = f'{path}/graphs_ood'
        else:
            self.questions = pd.read_csv(f'{path}/questions.csv')
            self.cached_graph = f'{path}/cached_graphs'
            self.cached_desc = f'{path}/cached_desc'
            self.path_nodes = f'{path}/nodes'
            self.path_edges = f'{path}/edges'
            self.path_graphs = f'{path}/graphs'

    def __len__(self):
        """Return the len of the dataset."""
        return len(self.questions)

    def __getitem__(self, index):
        data = self.questions.iloc[index]
        image_id = data['image_id']
        question = f'Question: {data["question"]}\n\nAnswer:'
        nodes = pd.read_csv(f'{self.path_nodes}/{image_id}.csv')
        edges = pd.read_csv(f'{self.path_edges}/{image_id}.csv')
        graph = torch.load(f'{self.path_graphs}/{image_id}.pt')
        desc = nodes.to_csv(index=False)+'\n'+edges.to_csv(index=False, columns=['src', 'edge_attr', 'dst'])

        return {
            'id': index,
            'question': question,
            'label': data['answer'],
            'desc': desc,
            'graph': graph,
        }

    def get_idx_split(self):

        # Load the saved indices
        with open(f'{path}/split/train_indices.txt', 'r') as file:
            train_indices = [int(line.strip()) for line in file]
        with open(f'{path}/split/val_indices.txt', 'r') as file:
            val_indices = [int(line.strip()) for line in file]
        with open(f'{path}/split/test_indices.txt', 'r') as file:
            test_indices = [int(line.strip()) for line in file]

        return {'train': train_indices, 'val': val_indices, 'test': test_indices}


if __name__ == '__main__':
    dataset = AnomalyGraphsBaselineDataset()

    data = dataset[0]
    for k, v in data.items():
        print(f'{k}: {v}')

    split_ids = dataset.get_idx_split()
    for k, v in split_ids.items():
        print(f'# {k}: {len(v)}')

    ood_dataset = AnomalyGraphsBaselineDataset(use_ood=True)
    ood_data = ood_dataset[0]
    for k, v in ood_data.items():
        print(f'{k}: {v}')