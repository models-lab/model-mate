package modelmate.integration.views;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.ui.IEditorPart;

import modelmate.integration.API.SingleResult;

public class AutocompletionStore {

	private static AutocompletionStore instance;

	public static AutocompletionStore getInstance() {
		if (instance == null) {
			instance = new AutocompletionStore();
		}
		return instance;
	}

	private Map<IEditorPart, SingleResult> results = new HashMap<>();
	
	public SingleResult autocompletionFor(IEditorPart editor) {
		return results.get(editor);
	}

	public void store(IEditorPart part, SingleResult result) {
		results.put(part, result);
		// FIND OUT HOW TO FREE CLOSED PARTS, OR USE IDENTIFIERS
	}

}
