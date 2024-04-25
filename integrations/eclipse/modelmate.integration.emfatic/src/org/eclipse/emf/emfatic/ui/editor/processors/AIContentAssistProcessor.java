package org.eclipse.emf.emfatic.ui.editor.processors;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.ITextViewer;
import org.eclipse.jface.text.contentassist.CompletionProposal;
import org.eclipse.jface.text.contentassist.ICompletionProposal;
import org.eclipse.jface.text.contentassist.IContentAssistProcessor;
import org.eclipse.jface.text.contentassist.IContextInformation;
import org.eclipse.jface.text.contentassist.IContextInformationValidator;

import modelmate.integration.API;
import modelmate.integration.API.SuggestionResult;
import modelmate.integration.emfatic.EmfaticTokenizer;

public class AIContentAssistProcessor implements IContentAssistProcessor {

	private Mode mode;
	private String kind;
	
	public AIContentAssistProcessor(Mode mode, String kind) {
		this.mode = mode;
		this.kind = kind;
	}
	
	public AIContentAssistProcessor() {
		this(Mode.TOKEN, "default");
	}
	
	
	@Override
	public String getErrorMessage() {
		return null;
	}

	@Override
	public IContextInformationValidator getContextInformationValidator() {
		System.out.println("AIContentAssistProcessor.getContextInformationValidator()");
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public char[] getContextInformationAutoActivationCharacters() {
		System.out.println("AIContentAssistProcessor.getContextInformationAutoActivationCharacters()");
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public char[] getCompletionProposalAutoActivationCharacters() {
		System.out.println("AIContentAssistProcessor.getCompletionProposalAutoActivationCharacters()");
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public IContextInformation[] computeContextInformation(ITextViewer viewer, int offset) {
		System.out.println("AIContentAssistProcessor.computeContextInformation()");
		return null;
	}

	@Override
	public ICompletionProposal[] computeCompletionProposals(ITextViewer viewer, int offset) {
		String previous;
		try {
			previous = viewer.getDocument().get(0, offset);
			String trimmed = previous.trim();
			if (trimmed.endsWith("class") || trimmed.endsWith("attr") || trimmed.endsWith("ref") || trimmed.endsWith("val")) {
				mode = Mode.TOKEN;
			} else {
				mode = Mode.LINE;
			}
			
		} catch (BadLocationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
		
		API api = new API();
		EmfaticTokenizer tokenizer = new EmfaticTokenizer();
		
		String context = tokenizer.tokenize(previous);
		
		List<String> suggestions;		
		if (mode == Mode.TOKEN) {
			SuggestionResult result = api.recommendNextToken(context);
			suggestions = result.getSuggestions();
		} else {
			SuggestionResult result = api.recommendNextLine(context);
			suggestions = result.getSuggestions();			
		}
		
		List<String> dedupSuggestions = new ArrayList<>();
		for (String string : suggestions) {
			if (dedupSuggestions.contains(string))
				continue;
			dedupSuggestions.add(string);
		}
		
		ICompletionProposal[] proposals = new ICompletionProposal[dedupSuggestions.size()];
		for (int i = 0; i < dedupSuggestions.size(); i++) {
			String string = dedupSuggestions.get(i);
			proposals[i] = new CompletionProposal(string, offset, 0, string.length());
		}
		
		return proposals;
	}
	
	public static enum Mode {
		TOKEN,
		LINE,
		FRAGMENT
	}
}
