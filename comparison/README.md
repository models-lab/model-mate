
# Configuring the benchmark

```shell
export PYTHONPATH="/path/to/modelxglue/"
export MODELMATE_COMPONENTS="/path/to/model-mate/comparison/components"
export COMPONENTS="/path/to/model-mate/comparison/components"
```

Checkout https://github.com/models-lab/modelxglue-mde-components

```
cd comparison/components
ln -s /path/to/modelxglue/components/recommendation
```

Execute:

```
python3 -m modelxglue.main --config-dir benchmark-features/ task=feature_recommendation model=modelmate_classdiagram dataset=mar_ecore_deduplicated 
```
