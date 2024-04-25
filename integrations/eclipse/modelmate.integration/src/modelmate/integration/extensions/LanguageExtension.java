package modelmate.integration.extensions;

import modelmate.integration.language.PrettyPrinter;
import modelmate.integration.language.Tokenizer;

public class LanguageExtension {

	private final String extension;
	private final Tokenizer tokenizer;
	private final PrettyPrinter pretty;

	public LanguageExtension(String extension, Tokenizer tokenizer, PrettyPrinter pretty) {
		this.extension = extension;
		this.tokenizer = tokenizer;
		this.pretty = pretty;
	}

	public String getExtension() {
		return extension;
	}
	
	public Tokenizer getTokenizer() {
		return tokenizer;
	}
	
	public PrettyPrinter getPrettyPrinter() {
		return pretty;
	}
}
