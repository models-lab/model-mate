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
python preprocess_dataset.py dataset=modelset_line
python preprocess_dataset.py dataset=ecore_line
```

Generate derived datasets adapted to the tasks to be evaluated:
```shell
python parse_test_dataset.py dataset=modelset_line evaluation.mode=token
python parse_test_dataset.py dataset=modelset_line evaluation.mode=token-id
python parse_test_dataset.py dataset=modelset_line evaluation.mode=line
python parse_test_dataset.py dataset=modelset_line evaluation.mode=block

python parse_test_dataset.py dataset=ecore_line evaluation.mode=token
python parse_test_dataset.py dataset=ecore_line evaluation.mode=token-id
python parse_test_dataset.py dataset=ecore_line evaluation.mode=line
python parse_test_dataset.py dataset=ecore_line evaluation.mode=block
```


## Training models

### Fine-tuning existing model

Fine-tuning existing models:
```shell
python train_transformer.py dataset=modelset_line model=gpt2
python train_transformer.py dataset=ecore_line model=gpt2
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


### Inference and results

Token-id:
```shell
python run_inference.py dataset=ecore_line model=gpt2 evaluation.mode=token-id
python report_results.py evaluation.mode=token-id dataset=ecore_line model=gpt2
```

Token:
```shell
python run_inference.py dataset=ecore_line model=gpt2 evaluation.mode=token
python report_results.py evaluation.mode=token dataset=ecore_line model=gpt2
```

Line:
```shell
python run_inference.py dataset=ecore_line model=gpt2 evaluation.mode=line
python report_results.py evaluation.mode=line dataset=ecore_line model=gpt2
```

Block:
```shell
python run_inference.py dataset=ecore_line model=gpt2 evaluation.mode=block
python report_results.py evaluation.mode=block dataset=ecore_line model=gpt2
```
