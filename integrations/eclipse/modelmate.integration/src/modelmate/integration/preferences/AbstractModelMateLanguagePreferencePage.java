package modelmate.integration.preferences;

import org.eclipse.jface.preference.*;
import org.eclipse.ui.IWorkbenchPreferencePage;
import org.eclipse.ui.IWorkbench;
import modelmate.integration.Activator;

public abstract class AbstractModelMateLanguagePreferencePage
	extends FieldEditorPreferencePage
	implements IWorkbenchPreferencePage {

	public AbstractModelMateLanguagePreferencePage(String language) {
		super(GRID);
		setPreferenceStore(Activator.getDefault().getPreferenceStore());
		setDescription("Language preferences for " + language);
	}
	
	public void createFieldEditors() {
		addField(
				new BooleanFieldEditor(
					PreferenceConstants.P_RUN_MANUALLY,
					"&Run ModelMate server manually",
					getFieldEditorParent()));

		addField(
			new StringFieldEditor(PreferenceConstants.P_URL, "Server URL:", getFieldEditorParent()));
	}

	public void init(IWorkbench workbench) {
	}
	
}