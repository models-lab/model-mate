# emfatic-gpt
## Emfatic token prediction

```shell
conda env create --file=conda_venv.yml
conda activate emfatic-gpt
# install pytorch
```

Download datasets:
```shell
./download_modelset.sh
```

Preprocess dataset:
```shell
python preprocess_dataset.py dataset=modelset_token
python preprocess_dataset.py dataset=modelset_line
```


Train tokenizer:
```shell
python train_tokenizer.py dataset=modelset_token
python train_tokenizer.py dataset=modelset_line
```

Train gpt token level:
```shell
python train_transformer.py dataset=modelset_token model=gpt2
python train_transformer.py dataset=modelset_token model=gpt2rand
python train_transformer.py dataset=modelset_token model=gpt2rand2 params.scheduler=constant
```

Train gpt line level:
```shell
python train_transformer.py dataset=modelset_line model=gpt2
python train_transformer.py dataset=modelset_line model=gpt2rand params.scheduler=constant params.epochs=25
python train_transformer.py dataset=modelset_line model=gpt2rand2 params.scheduler=constant params.epochs=25
```
