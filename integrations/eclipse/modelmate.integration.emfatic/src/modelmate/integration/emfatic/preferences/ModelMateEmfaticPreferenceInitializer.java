package modelmate.integration.emfatic.preferences;

import modelmate.integration.preferences.AbstractModelMateLanguagePreferenceInitializer;

public class ModelMateEmfaticPreferenceInitializer extends AbstractModelMateLanguagePreferenceInitializer {

	public ModelMateEmfaticPreferenceInitializer() {
		super(modelmate.integration.emfatic.Activator.getDefault().getPreferenceStore());
	}

}
