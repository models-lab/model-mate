# emfatic-gpt
## Emfatic token prediction

```shell
conda env create --file=conda_venv.yml
conda activate emfatic-gpt
```

Download dataset:
```shell
TO DO
```

Preprocess dataset:
```shell
python preprocess_dataset.py --dataset dataset_token_level
python preprocess_dataset.py --dataset dataset_line_level
```


Train tokenizer:
```shell
python train_tokenizer.py --dataset dataset_token_level/ --level token
python train_tokenizer.py --dataset dataset_line_level/ --level line
```

Train gpt token level:
```shell
python train_transformer.py --dataset dataset_token_level/ --output_path_model gpt2-token --huggingface_model gpt2 --is_pretrained
python train_transformer.py --dataset dataset_token_level/ --output_path_model java-gpt2-token --huggingface_model microsoft/CodeGPT-small-java --is_pretrained
python train_transformer.py --dataset dataset_token_level --output_path_model gpt2rand-token --model_dir tokenizers/tokenizer-enfatic-token/ --schedule constant
```

Train gpt line level:
```shell
python train_transformer.py --dataset dataset_line_level/ --output_path_model gpt2-line --huggingface_model gpt2 --is_pretrained
python train_transformer.py --dataset dataset_line_level/ --output_path_model java-gpt2-line --huggingface_model microsoft/CodeGPT-small-java --is_pretrained
python train_transformer.py --dataset dataset_line_level --output_path_model gpt2rand-line --model_dir tokenizers/tokenizer-enfatic-line/ --schedule constant
```
