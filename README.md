

# Model-mate: A recommender system for software modeling

## Running the server

The server simply needs to know which model to load. 
By default, the server is run in the port 8080. 
Use the option `--port` to change it, specially if you have
several servers, serving different languages, at once.

```bash
python3 src/mate-serve.py --port 8082 --model <path-or-huggingface-URL>
```

The model can be downloaded manually to some folder, 
it is easier to just use a Huggingface path. For,
instance, for Emfatic you can use the following command:

```bash
python3 src/mate-serve.py --model models-lab/modelmate-emfatic-small 
```



## Building the models

The `experiments` folder contains the source code to pre-process the dataset,
build the ML models and evaluate them.

Checkout the [experiments/README.md](experiments/README.md) for more information about how to
build the models.
