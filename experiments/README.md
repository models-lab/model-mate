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

Generate derived datasets adapted to the tasks to be evaluated:
```shell
python parse_test_dataset.py --mode token-id --n 5 --parsed_test data/temp/modelset_token/test_parsed_token-id.json
python parse_test_dataset.py --mode token --n 20 --parsed_test data/temp/modelset_token/test_parsed_token.json
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


### Inference and results

Token-id:
```shell
python run_inference.py
python report_results.py
```

Token:
```shell
python run_inference.py --mode token --n 5 --parsed_test data/temp/modelset_token/test_parsed_token.json --results data/temp/modelset_token/results_token_gpt2.csv
python report_results.py --mode token --results data/temp/modelset_token/results_token_gpt2.csv
```