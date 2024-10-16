package modelmate.integration.views;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

import org.eclipse.core.commands.ExecutionException;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.preference.PreferenceDialog;
import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.TextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.browser.Browser;
import org.eclipse.swt.browser.BrowserFunction;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.ISelectionListener;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.PreferencesUtil;
import org.eclipse.ui.editors.text.TextEditor;
import org.eclipse.ui.part.FileEditorInput;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.texteditor.IDocumentProvider;

import jakarta.inject.Inject;
import modelmate.integration.API.SingleResult;
import modelmate.integration.Activator;
import modelmate.integration.extensions.LanguageExtension;
import modelmate.integration.handlers.ApplyAutocompletion;
import modelmate.integration.utils.Utils;

/**
 * This sample class demonstrates how to plug-in a new
 * workbench view with html and javascript content. The view 
 * shows how data can be exchanged between Java and JavaScript.
 */

public class AutocompletionView extends ViewPart implements ISelectionListener {

	/**
	 * The ID of the view as specified by the extension.
	 */
	public static final String ID = "modelmate.integration.views.AutocompletionView";

	@Inject
	Shell shell;

	private Action action1 = makeAction1();
	private Action action2 = makeAction2();

	private Browser fBrowser;

	@Override
	public void createPartControl(Composite parent) {
		fBrowser = new Browser(parent, SWT.WEBKIT);
		fBrowser.setText(getContent());
		BrowserFunction prefs = new OpenPreferenceFunction(fBrowser, "openEclipsePreferences", () -> {
			PreferenceDialog dialog = PreferencesUtil.createPreferenceDialogOn(shell, null, null, null);
			dialog.open();
		});
		
		ApplyRecommendation rec = new ApplyRecommendation(fBrowser, "applyBlockRecommendation", () -> {
			try {
				new ApplyAutocompletion().execute(null);
			} catch (ExecutionException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		});


		
		fBrowser.addDisposeListener(e -> prefs.dispose());
		fBrowser.addDisposeListener(e -> rec.dispose());
		
		makeActions();
		contributeToActionBars(getViewSite());
		getSite().getPage().addSelectionListener(this);
		getSite().getPage().addPostSelectionListener(this);
		
        //getSite().getPage().addPartListener(this);

	}

	private void contributeToActionBars(IViewSite viewSite) {
		IActionBars bars = viewSite.getActionBars();
		fillLocalPullDown(bars.getMenuManager());
		fillLocalToolBar(bars.getToolBarManager());
	}

	private void fillLocalPullDown(IMenuManager manager) {
		manager.add(action1);
		manager.add(new Separator());
		manager.add(action2);
	}

	private void fillLocalToolBar(IToolBarManager manager) {
		manager.add(action1);
		manager.add(action2);
	}

	private void makeActions() {
		makeAction1();
		makeAction2();
	}

	private Action makeAction1() {
		Action action = new Action() {
			public void run() {
				InputDialog inputDialog = new InputDialog(shell, null, "What must the browser say: ", null, null);
				inputDialog.open();
				String something = inputDialog.getValue();
				fBrowser.execute("say(\"" + something + "\");");
			}
		};
		action.setText("Say something");
		action.setToolTipText("Say something");
		action.setImageDescriptor(
				PlatformUI.getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_OBJS_INFO_TSK));
		return action;
	}

	private Action makeAction2() {
		Action action = new Action() {
			public void run() {
				fBrowser.execute("changeColor();");
			}
		};
		action.setText("Change Color");
		action.setToolTipText("Change the color");
		action.setImageDescriptor(PlatformUI.getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_ELCL_SYNCED));
		return action;
	}

	@Override
	public void setFocus() {
		fBrowser.setFocus();
	}

	private class OpenPreferenceFunction extends BrowserFunction {
		private Runnable function;

		OpenPreferenceFunction(Browser browser, String name, Runnable function) {
			super(browser, name);
			this.function = function;
		}

		@Override
		public Object function(Object[] arguments) {
			function.run();
			return getName() + " executed!";
		}
	}
	
	private class ApplyRecommendation extends BrowserFunction {
		private Runnable function;

		ApplyRecommendation(Browser browser, String name, Runnable function) {
			super(browser, name);
			this.function = function;
		}

		@Override
		public Object function(Object[] arguments) {
			function.run();
			return getName() + " executed!";
		}
	}

	public String getContent() {
		String js = null;
		try (InputStream inputStream = getClass().getResourceAsStream("AutocompletionView.js")) {
			js = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
		} catch (IOException e) {
		}
		StringBuilder buffer = new StringBuilder();
		buffer.append("<!doctype html>");
		buffer.append("<html lang=\"en\">");
		buffer.append("<head>");
		buffer.append("<meta charset=\"utf-8\">");
		buffer.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
		buffer.append("<title>Sample View</title>");
		buffer.append("<script>" + js + "</script>");
		buffer.append("</script>");
		buffer.append("</head>");
		buffer.append("<body>");
		buffer.append("<h3>Fragment completion</h3>");
		buffer.append("<div style='margin-bottom: 10px'><pre id=\"suggestion\"></pre></div>");
		/*
		buffer.append("<h3>Last Action</h3>");
		buffer.append("<div id=\"lastAction\"></div>");
		buffer.append("<h3>Call to Java</h3>");
		buffer.append("<input id=button type=\"button\" value=\"Open Preferences\" onclick=\"openPreferences();\">");
		*/

		buffer.append("<input id=button type=\"button\" value=\"Apply\" onclick=\"applyBlockRecommendation();\">");

		buffer.append("</body>");
		buffer.append("</html>");
		return buffer.toString();
	}

	@Override
	public void selectionChanged(IWorkbenchPart part, ISelection selection) {
		if (selection.isEmpty()) {
			return;
		}
		if (selection instanceof TextSelection textSelection) {
			if (part instanceof TextEditor) {
				TextEditor editor = (TextEditor) part;
				LanguageExtension lang = Utils.getLanguageExtensionForEditor(editor);
				if (lang == null)
					return;
				
				autocomplete((IEditorPart) part, editor, textSelection, lang);
			}
		}
		
		/*
		if (selection instanceof IStructuredSelection) {
			fBrowser.execute("setSelection(\"" + part.getTitle() + "::"
					+ ((IStructuredSelection) selection).getFirstElement().getClass().getSimpleName() + "\");");
		} else {
			fBrowser.execute("setSelection(\"Something was selected in part " + part.getTitle() + "\");");
		}
		*/
	}

	private void autocomplete(IEditorPart part, TextEditor editor, TextSelection textSelection, LanguageExtension lang) {
		int offset = textSelection.getOffset();

		IDocumentProvider doc = editor.getDocumentProvider();
		IDocument document = doc.getDocument(editor.getEditorInput());
		try {
			String fragment  = document.get(0, offset);			
			AutocompletionThread.get().scheduleRecommendation(fragment, lang, (result) -> {
				AutocompletionStore.getInstance().store(part, result);
				showResult(fragment, result, lang);				
			});
		} catch (BadLocationException e) {
			e.printStackTrace();
		}
	}
	
	private void showResult(String fragment, SingleResult result, LanguageExtension lang) {

		System.out.println(result);			
		Display.getDefault().asyncExec(() -> {
			System.out.println(result.getText());
			String text = result.toNormalizedText();
			
			String pretty = lang.getPrettyPrinter().prettyPrint(text);
			
			pretty = pretty.replace("\n", "\\n");
			System.out.println("Pretty");
			System.out.println(pretty);
			pretty = pretty.replace("\"", "\\\"");
			fBrowser.execute("setSuggestion(\"" + pretty + "\");");
			//fBrowser.execute("setSuggestion(\"" + result.getText() + " | " + result.getTime() + "\");");
		});
	}

	@Override
	public void dispose() {
		getSite().getPage().removeSelectionListener(this);
		super.dispose();
	}
}
