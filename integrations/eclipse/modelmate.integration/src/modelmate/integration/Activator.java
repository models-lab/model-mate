package modelmate.integration;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

import modelmate.integration.extensions.ExtensionPointUtils;
import modelmate.integration.extensions.LanguageExtension;

/**
 * The activator class controls the plug-in life cycle
 */
public class Activator extends AbstractUIPlugin {

	// The plug-in ID
	public static final String PLUGIN_ID = "modelmate.integration"; //$NON-NLS-1$

	// The shared instance
	private static Activator plugin;
	
	public static final String LANGUAGE_EXTENSION_POINT = "modelmate.integration.language";
	
	/**
	 * The constructor
	 */
	public Activator() {
	}

	@Override
	public void start(BundleContext context) throws Exception {
		super.start(context);
		plugin = this;
	}

	@Override
	public void stop(BundleContext context) throws Exception {
		plugin = null;
		super.stop(context);
	}

	/**
	 * Returns the shared instance
	 *
	 * @return the shared instance
	 */
	public static Activator getDefault() {
		return plugin;
	}
	
	private Map<String, LanguageExtension> languageExtensions = null;

	public LanguageExtension getLanguageExtension(String extension) {
		if (languageExtensions == null) 
			this.languageExtensions = ExtensionPointUtils.getLanguageExtensions().stream().collect(Collectors.toMap(l -> l.getExtension(), l -> l));

		return languageExtensions.get(extension);
	}
	
}
