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

## Installing the plug-in

For the moment we do not have an update site, but you can install the sources and test it a new Eclipse instance. For the moment, the plug-in expect to have the server running on port 8080.

### Emfatic plugin

For instance, for `Emfatic` you need to import these two projects.

```
modelmate.integration
modelmate.integration.emfatic
```

### Xtext-based languages

If you have an Xtext based language, you can easily create a plug-in for it reusing the infrastructure provided by these two plugins:

```
modelmate.integration
modelmate.integration.xtext
```

Then, you just create a new plug-in which the following extension point:

```xml
<plugin>
   <extension
         point="modelmate.integration.language">
      <language
            extension="mylang"
            tokenizer="modelmate.mylanguage.MyLanguageTokenizer">
      </language>
   </extension>
</plugin>

```

The tokenizer can be implemented by adapting the code in `modelmate.integration.xtext.XtextTokenizer`, something like:

```java
public class MyLanguageTokenizer implements Tokenizer {

	private Injector injector = /* Get your language injector */;
	private Generator generator = new Generator(injector);

	@Override
	public String tokenize(String fragment) {
		return generator.toTokens(fragment);
	}
}
```

## Building the models

The `experiments` folder contains the source code to pre-process the dataset,
build the ML models and evaluate them.

Checkout the [experiments/README.md](experiments/README.md) for more information about how to build the models.
