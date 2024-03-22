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


## Comparison against GPT 3.5

To avoid the bias that GPT 3.5. has been tested only on a sample of the original dataset, the same sampled datasets are used to re-evaluate the models.

### Generating sampled datasets

```bash
python sample_test_set.py --mode line --parsed_test data/temp/ecore_line/parsed_test_line.json --output data/temp/ecore_line/parsed_test_line-sample-1000.json

python sample_test_set.py --mode token-id --parsed_test data/temp/ecore_line/parsed_test_token-id.json --output data/temp/ecore_line/parsed_test_token-id-sample-200.json --num_samples 200

python sample_test_set.py --mode block --parsed_test data/temp/ecore_line/parsed_test_block.json --output data/temp/ecore_line/parsed_test_block-sample-1000.json
```

### Evaluation

```
# Token-id
python run_inference.py --multirun dataset=ecore_line model=codegen_multi,codeparrot_multi,gpt2-large evaluation.mode=token-id evaluation.max_new_tokens=8 params.context_length=512 evaluation.sampled_test=data/temp/ecore_line/parsed_test_token-id-sample-200.json language=emfatic

# Line
python run_inference.py --multirun dataset=ecore_line model=codegen_multi,codeparrot_multi,gpt2-large evaluation.mode=line evaluation.max_new_tokens=32 params.context_length=512 evaluation.sampled_test=data/temp/ecore_line/parsed_test_line-sample-1000.json language=emfatic
```

### Reporting results

```bash
# Token-id

python report_results.py --mode token-id --results data/temp/ecore_line/codeparrot/codeparrot-small-multi/results_sampled_token-id.csv,data/temp/ecore_line/Salesforce/codegen-350M-multi/results_sampled_token-id.csv,data/temp/ecore_line/gpt2-large/results_sampled_token-id.csv  --language=conf/language/emfatic.yaml

```

# Line

python report_results.py --mode line --results data/temp/ecore_line/codeparrot/codeparrot-small-multi/results_sampled_line.csv,data/temp/ecore_line/Salesforce/codegen-350M-multi/results_sampled_line.csv,data/temp/ecore_line/gpt2-large/results_sampled_line.csv  --language=conf/language/emfatic.yaml
