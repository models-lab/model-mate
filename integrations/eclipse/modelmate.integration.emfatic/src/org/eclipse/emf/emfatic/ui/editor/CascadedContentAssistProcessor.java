package org.eclipse.emf.emfatic.ui.editor;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.jface.text.ITextViewer;
import org.eclipse.jface.text.contentassist.ICompletionProposal;
import org.eclipse.jface.text.contentassist.IContentAssistProcessor;
import org.eclipse.jface.text.contentassist.IContextInformation;
import org.eclipse.jface.text.contentassist.IContextInformationValidator;

public class CascadedContentAssistProcessor implements IContentAssistProcessor {

	//private ProposalsComparator proposalsComparator = new ProposalsComparator();

	public ICompletionProposal[] computeCompletionProposals(ITextViewer viewer,
			int offset) {
		List<ICompletionProposal> res = new ArrayList<ICompletionProposal>();
		for (IContentAssistProcessor cap : caps) {
			ICompletionProposal[] oneCap = cap.computeCompletionProposals(
					viewer, offset);
			if (oneCap != null) {
				for (ICompletionProposal cp : oneCap) {
					if (!res.contains(cp)) {
						res.add(cp);
					}
				}
			}
		}
		ICompletionProposal[] res2 = new ICompletionProposal[res.size()];
		res.toArray(res2);
		// Arrays.sort(res2, proposalsComparator);
		return res2;
	}

	public IContextInformation[] computeContextInformation(ITextViewer viewer,
			int offset) {
		return null;
	}

	public char[] getCompletionProposalAutoActivationCharacters() {
		List<Character> res = new ArrayList<Character>();
		for (IContentAssistProcessor cap : caps) {
			char[] capAct = cap.getCompletionProposalAutoActivationCharacters();
			
			// TODO: Done by jesusc, not sure...
			if (capAct == null)
				continue;
			
			for (char c : capAct) {
				if (!res.contains(c)) {
					res.add(c);
				}
			}
		}
		char[] res2 = new char[res.size()];
		int i = 0;
		for (Character c : res) {
			res2[i] = c;
			i++;
		}
		return res2;
	}

	public char[] getContextInformationAutoActivationCharacters() {
		return null;
	}

	public IContextInformationValidator getContextInformationValidator() {
		return null;
	}

	public String getErrorMessage() {
		return null;
	}

	List<IContentAssistProcessor> caps = new ArrayList<IContentAssistProcessor>();

	public void add(IContentAssistProcessor cap) {
		caps.add(cap);
	}

}
