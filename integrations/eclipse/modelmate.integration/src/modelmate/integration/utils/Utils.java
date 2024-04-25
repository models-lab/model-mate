package modelmate.integration.utils;

import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.editors.text.TextEditor;
import org.eclipse.ui.part.FileEditorInput;

import modelmate.integration.Activator;
import modelmate.integration.extensions.LanguageExtension;

public class Utils {

	public static LanguageExtension getLanguageExtensionForEditor(TextEditor editor) {
		String extension = getExtension(editor);
		if (extension == null) {
			return null;
		}
		
		LanguageExtension lang = Activator.getDefault().getLanguageExtension(extension);
		if (lang == null)
			return null;
		
		return lang;
	}
	

	private static String getExtension(TextEditor editor) {
		IEditorInput input = editor.getEditorInput();
		if (input instanceof FileEditorInput f) {
			return f.getFile().getFileExtension();
		}
		return null;
	}

	
}
