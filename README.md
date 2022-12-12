# emfatic-gpt
## Emfatic token prediction

```shell
conda env create --file=conda_venv.yml
conda activate emfatic-gpt
```

Train tokenizer:
```shell
python train_tokenizer.py
```

Train gpt:
```shell
python train_transformer.py --output_path_model test_gpt2_random --model_dir gpt2-enfatic --schedule constant
python train_transformer.py --output_path_model test_java_gpt2 --huggingface_model microsoft/CodeGPT-small-java --schedule linear
python train_transformer.py --output_path_model test_gpt2 --huggingface_model gpt2 --schedule linear
```
