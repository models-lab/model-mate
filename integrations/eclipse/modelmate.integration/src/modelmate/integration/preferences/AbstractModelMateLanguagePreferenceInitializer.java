package modelmate.integration.preferences;

import org.eclipse.core.runtime.preferences.AbstractPreferenceInitializer;
import org.eclipse.jface.preference.IPreferenceStore;

/**
 * Class used to initialize default preference values.
 */
public class AbstractModelMateLanguagePreferenceInitializer extends AbstractPreferenceInitializer {

	
	private IPreferenceStore store;

	public AbstractModelMateLanguagePreferenceInitializer(IPreferenceStore store) {
		this.store = store;
	}
	
	
	public void initializeDefaultPreferences() {
		store.setDefault(PreferenceConstants.P_RUN_MANUALLY, true);
		store.setDefault(PreferenceConstants.P_URL, "http://0.0.0.0:8080");
	}

}
