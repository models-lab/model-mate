package modelmate.integration.handlers;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.TextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.editors.text.TextEditor;
import org.eclipse.ui.texteditor.IDocumentProvider;

import modelmate.integration.API.SingleResult;
import modelmate.integration.extensions.LanguageExtension;
import modelmate.integration.utils.Utils;
import modelmate.integration.views.AutocompletionStore;

public class ApplyAutocompletion extends AbstractHandler {

	@Override
	public Object execute(ExecutionEvent event) throws ExecutionException {
	    IEditorPart editor = ((IWorkbenchPage) PlatformUI.getWorkbench()
	            .getActiveWorkbenchWindow().getActivePage()).getActiveEditor();
	    
	    if (!(editor instanceof TextEditor)) 
	    	return null;
	   
		LanguageExtension lang = Utils.getLanguageExtensionForEditor((TextEditor) editor);
		if (lang == null)
			return null;

	    
	    SingleResult result = AutocompletionStore.getInstance().autocompletionFor(editor);
	    if (result != null) {
	    	ISelection selection = ((TextEditor) editor).getSelectionProvider().getSelection();
		    if (! (selection instanceof TextSelection s)) {
		    	return null;
		    }
		    
		    int offset = s.getOffset();
		    
	    	IDocumentProvider doc = ((TextEditor) editor).getDocumentProvider();
			IDocument document = doc.getDocument(editor.getEditorInput());
		
			String pretty = lang.getPrettyPrinter().prettyPrint(result.toNormalizedText());

			fillDocument(document, pretty, offset);
	    }
		
		return null;
	}
	
	private void fillDocument(IDocument document, String result, int offset) {
		try {
			document.replace(offset, 0, result);
		} catch (BadLocationException e) {
			e.printStackTrace();
		}
	}
}
