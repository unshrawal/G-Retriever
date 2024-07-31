#!/bin/bash

# Install PyTorch
#conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.8 -c pytorch -c nvidia
conda install pytorch==2.3.0 torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Check PyTorch version
python -c "import torch; print(torch.__version__)"

# Check CUDA version
python -c "import torch; print(torch.version.cuda)"

# Install PyTorch Geometric and other packages
#pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.0.1+cu118.html
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.3.0+cu118.html

pip install peft pandas ogb transformers wandb sentencepiece torch_geometric datasets pcst_fast gensim
pip install scipy==1.10.1
pip install python-Levenshtein
