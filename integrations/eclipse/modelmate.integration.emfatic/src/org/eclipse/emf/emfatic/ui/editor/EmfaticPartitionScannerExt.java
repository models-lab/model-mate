package org.eclipse.emf.emfatic.ui.editor;

import org.eclipse.jface.text.IDocument;

public class EmfaticPartitionScannerExt {
	public final static String packagePart = "packagePart";
	public final static String importPart = "importPart";
	public final static String annotationPart = "annotationPart";
	public final static String subPackagePart = "subPackagePart";
	public final static String attrPart = "attrPart";
	public final static String refPart = "refPart";
	public final static String valrPart = "valPart";
	public final static String opPart = "opPart";
	public final static String datatypePart = "datatypePart";
	public final static String enumPart = "enumPart";
	public final static String mapentryPart = "mapentryPart";
	public final static String classHeadingPart = "classHeadingPart";
	public final static String ifaceHeadingPart = "ifaceHeadingPart";
	public final static String multiLineComment = "multiLineComment";
	public final static String singleLineComment = "singleLineComment";

	public static String[] contentTypes() {
		return new String[] { IDocument.DEFAULT_CONTENT_TYPE, packagePart, importPart, annotationPart, subPackagePart,
				attrPart, refPart, valrPart, opPart, datatypePart, enumPart, mapentryPart, classHeadingPart,
				ifaceHeadingPart, multiLineComment, singleLineComment };
	}
}
