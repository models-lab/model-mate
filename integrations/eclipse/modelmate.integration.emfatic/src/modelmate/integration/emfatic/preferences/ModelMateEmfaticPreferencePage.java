package modelmate.integration.emfatic.preferences;

import modelmate.integration.emfatic.Activator;
import modelmate.integration.preferences.AbstractModelMateLanguagePreferencePage;

public class ModelMateEmfaticPreferencePage extends AbstractModelMateLanguagePreferencePage {

	public ModelMateEmfaticPreferencePage() {
		super("Emfatic", Activator.getDefault().getPreferenceStore());
	}

}
