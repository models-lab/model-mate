# Emfatic token prediction

## Requirements
```shell
conda env create --file=conda_venv.yml
conda activate emfatic-gpt
# install pytorch
```

## Dataset
Download datasets:
```shell
./download_modelset.sh
```

Preprocess dataset:
```shell
python preprocess_dataset.py dataset=modelset_token
python preprocess_dataset.py dataset=modelset_line
```

## Training models

### Fine-tuning existing model (best option)

Fine-tuning existing models:
```shell
python train_transformer.py dataset=modelset_token model=gpt2
python train_transformer.py dataset=modelset_line model=gpt2
```

### Training tokenizer + model (not recommended)

Train tokenizer from scratch:
```shell
python train_tokenizer.py dataset=modelset_token
python train_tokenizer.py dataset=modelset_line
```

Train gpt from scratch:
```shell
python train_transformer.py dataset=modelset_token model=gpt2rand
python train_transformer.py dataset=modelset_line model=gpt2rand
```
