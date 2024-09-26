package modelmate.integration.xtext;

import org.eclipse.xtext.XtextStandaloneSetup;

import com.google.inject.Injector;

import modelmate.integration.language.Tokenizer;
import modelmate.integration.xtext.generate.Generator;

public class XtextTokenizer implements Tokenizer {

	private static Injector injector = null;

	private static Injector getInjector() {
		if (injector == null) {
			injector = new XtextStandaloneSetup().createInjectorAndDoEMFRegistration();
		}
		return injector;
	}
	
	private Generator generator = new Generator(getInjector());
	
	@Override
	public String tokenize(String fragment) {
		return generator.toTokens(fragment);
	}
	
}
