package modelmate.integration.xtext;

import modelmate.integration.language.Tokenizer;
import modelmate.integration.xtext.generate.Generator;

public class XtextTokenizer implements Tokenizer {

	private Generator generator = new Generator();
	
	@Override
	public String tokenize(String fragment) {
		return generator.toTokens(fragment);
	}

}
