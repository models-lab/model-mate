package org.eclipse.emf.emfatic.ui.editor;

import org.eclipse.emf.emfatic.ui.editor.processors.AIContentAssistProcessor;
import org.eclipse.emf.emfatic.ui.editor.processors.AIContentAssistProcessor.Mode;
import org.eclipse.gymnast.runtime.ui.editor.LDTSourceViewerConfiguration;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.contentassist.ContentAssistant;
import org.eclipse.jface.text.contentassist.IContentAssistProcessor;
import org.eclipse.jface.text.contentassist.IContentAssistant;
import org.eclipse.jface.text.source.ISourceViewer;


public class ModelMateEmfaticEditor extends org.eclipse.emf.emfatic.ui.editor.EmfaticEditor { 

	public ModelMateEmfaticEditor() {
	}
	
	protected LDTSourceViewerConfiguration createSourceViewerConfiguration() {
		return new EmfaticSourceViewerConfigurationExt(this);
	}
	
	public static class EmfaticSourceViewerConfigurationExt extends EmfaticSourceViewerConfiguration {

		public EmfaticSourceViewerConfigurationExt(EmfaticEditor editor) {
			super(editor);
		}

		@Override
		public IContentAssistant getContentAssistant(ISourceViewer sourceViewer) {
			ContentAssistant assistant = (ContentAssistant) super.getContentAssistant(sourceViewer);
			IContentAssistProcessor cap = assistant.getContentAssistProcessor(IDocument.DEFAULT_CONTENT_TYPE);
			
			//EmfaticPartitionScannerExt.
			
			//assistant.getContentAssistProcessor(COMMON_EDITOR_CONTEXT_MENU_ID)
			org.eclipse.emf.emfatic.ui.editor.CascadedContentAssistProcessor cascaded = new org.eclipse.emf.emfatic.ui.editor.CascadedContentAssistProcessor();
			cascaded.add(new AIContentAssistProcessor(Mode.LINE, "default"));
			cascaded.add(cap);
			assistant.setContentAssistProcessor(cascaded, IDocument.DEFAULT_CONTENT_TYPE);
			
			
			assistant.setContentAssistProcessor(new AIContentAssistProcessor(Mode.TOKEN, EmfaticPartitionScannerExt.classHeadingPart), EmfaticPartitionScannerExt.classHeadingPart);

			/*
			IContentAssistProcessor cap2 = assistant.getContentAssistProcessor(EmfaticPartitionScannerExt.classHeadingPart);			
			org.eclipse.emf.emfatic.ui.editor.CascadedContentAssistProcessor cascaded2 = new org.eclipse.emf.emfatic.ui.editor.CascadedContentAssistProcessor();
			cascaded2.add(new AIContentAssistProcessor(Mode.TOKEN, EmfaticPartitionScannerExt.classHeadingPart));
			cascaded2.add(cap2);
			assistant.setContentAssistProcessor(cascaded2, EmfaticPartitionScannerExt.classHeadingPart);
			*/

			
			assistant.setContentAssistProcessor(new AIContentAssistProcessor(Mode.TOKEN, EmfaticPartitionScannerExt.attrPart), EmfaticPartitionScannerExt.attrPart);
			assistant.setContentAssistProcessor(new AIContentAssistProcessor(Mode.TOKEN, EmfaticPartitionScannerExt.valrPart), EmfaticPartitionScannerExt.valrPart);
			assistant.setContentAssistProcessor(new AIContentAssistProcessor(Mode.TOKEN, EmfaticPartitionScannerExt.refPart), EmfaticPartitionScannerExt.refPart);
			
			
			// TODO: Use ClassAIContentAssistProcessor when it is properly implemented
			//assistant.setContentAssistProcessor(new ClassAIContentAssistProcessor(), EmfaticPartitionScannerExt.classHeadingPart);
			
			return assistant;
		}
		
	}

}
