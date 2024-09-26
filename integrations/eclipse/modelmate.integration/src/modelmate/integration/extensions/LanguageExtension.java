package modelmate.integration.extensions;

import java.net.URL;

import org.eclipse.jface.preference.IPreferenceStore;

import modelmate.integration.language.PrettyPrinter;
import modelmate.integration.language.Tokenizer;
import modelmate.integration.preferences.PreferenceConstants;

public class LanguageExtension {

	private final String extension;
	private final Tokenizer tokenizer;
	private final PrettyPrinter pretty;
	private final IPreferenceStore preferenceStore;

	public LanguageExtension(String extension, Tokenizer tokenizer, PrettyPrinter pretty, IPreferenceStore preferenceStore) {
		this.extension = extension;
		this.tokenizer = tokenizer;
		this.pretty = pretty;
		this.preferenceStore = preferenceStore;
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
	
	public String getModelMateServerURL() {
		String url = preferenceStore.getString(PreferenceConstants.P_URL);
		return url;
	}
}
