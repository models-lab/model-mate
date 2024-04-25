package modelmate.integration.extensions;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.core.runtime.Platform;

import modelmate.integration.Activator;
import modelmate.integration.language.PrettyPrinter;
import modelmate.integration.language.Tokenizer;

public class ExtensionPointUtils {

	public static List<LanguageExtension> getLanguageExtensions() {
		IExtensionRegistry registry = Platform.getExtensionRegistry();
		IConfigurationElement[] extensions = registry.getConfigurationElementsFor(Activator.LANGUAGE_EXTENSION_POINT);

		List<LanguageExtension> languageExtensions = new ArrayList<>();
		
		for (IConfigurationElement ce : extensions) {
			try {
				String extension = ce.getAttribute("extension");
				Tokenizer tokenizer = (Tokenizer) ce.createExecutableExtension("tokenizer");
				PrettyPrinter printer = PrettyPrinter.EMPTY;
				try {
					printer = (PrettyPrinter) ce.createExecutableExtension("prettyprinter");
				} catch (CoreException e) {
					// Ignore
				}
				languageExtensions.add(new LanguageExtension(extension, tokenizer, printer));
			} catch (CoreException e) {
				e.printStackTrace();
			}
		}

		return languageExtensions;
	}

}
