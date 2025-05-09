package modelmate.modelxglue.classdiagram;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.eclipse.emf.ecore.EAttribute;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EDataType;
import org.eclipse.emf.ecore.EEnum;
import org.eclipse.emf.ecore.EEnumLiteral;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EReference;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.resource.Resource;

import modelmate.modelxglue.emfatic.AbstractSyntaxPrinter;
import modelmate.modelxglue.emfatic.CodeXGlueOutput;
import modelmate.modelxglue.emfatic.CodeXGlueOutput.PieceOfCode;
import modelmate.modelxglue.emfatic.TextUtils;

public class GenerateClassDiagramDataset extends AbstractSyntaxPrinter<Resource> {
	
	protected void convertToTokens(Resource r, CodeXGlueOutput output) {
		try(PieceOfCode c = output.start()) {
			for (EObject obj : r.getContents()) {
				if (obj instanceof EPackage) {
					convertRootPackage((EPackage) obj, output);
				}
			}
		}
	}

	protected void convertRootPackage(EPackage obj, CodeXGlueOutput output) {
		convertPackageContents(obj, output);
	}

	protected void convertPackageContents(EPackage obj, CodeXGlueOutput output) {
		for (EPackage pkg : obj.getESubpackages()) {
			convertPackage(pkg, output);
		}
		
		for (EClassifier classifier : obj.getEClassifiers()) {
			if (classifier instanceof EClass) {
				convertClass((EClass) classifier, output);
			} else if (classifier instanceof EEnum) {
				convertEnum((EEnum) classifier, output);
			} else if (classifier instanceof EDataType) {
				convertDataType((EDataType) classifier, output);				
			}
		}
	}

	protected void convertEnum(EEnum c, CodeXGlueOutput output) {
		output.token("enum").w().token(nonNull(c.getName())).w();
		output.token("{").newLine().indent();
		for (EEnumLiteral l : c.getELiterals()) {
			output.token(nonNull(l.getName())).token(";");
		}
		output.unindent().token("}").newLine();
	}


	protected void convertDataType(EDataType c, CodeXGlueOutput output) {
		if (c.getInstanceTypeName() == null)
			return;
		
		output.
			token("datatype").w().token(nonNull(c.getName())).w().
			token(":").w().
			token(c.getInstanceTypeName()).
			token(";").newLine();
	}

	protected void convertPackage(EPackage pkg, CodeXGlueOutput output) {
		convertPackageContents(pkg, output);
	}

	protected void convertClass(EClass c, CodeXGlueOutput output) {
		convertClassHeader(c, output);
		output.token("{").newLine().indent();
		convertClassContents(c, output);
		output.unindent().token("}").newLine();
	}


	protected void convertClassHeader(EClass c, CodeXGlueOutput output) {
		output.token("class").w().token(nonNull(c.getName())).w();
		
		if (c.getESuperTypes().size() > 0) {
			output.token("extends").w();
			for (int i = 0, len = c.getESuperTypes().size(); i < len; i++) {
				EClass sup = c.getESuperTypes().get(i);
				output.token(nonNull(sup.getName()));
				if (i + 1 != len)
					output.token(",").w();
			}
		}
	}

	protected void convertClassContents(EClass c, CodeXGlueOutput output) {
		for (EStructuralFeature feature : c.getEStructuralFeatures()) {
			if (feature instanceof EAttribute) {
				convertAttribute((EAttribute) feature, output);
			} else {
				convertReference((EReference) feature, output);				
			}
		}
	}

	protected void convertAttribute(EAttribute attr, CodeXGlueOutput output) {
		EDataType dt = attr.getEAttributeType();
		String type = TextUtils.toEmfaticType(dt);
		String card = TextUtils.toEmfaticCardinality(attr, output.getMode());

		output.token(attr.getName()).w();
		output.token(":").w();
		output.token(type).token(card);
		output.token(";").newLine();
	}

	protected void convertReference(EReference ref, CodeXGlueOutput output) {
		EClass referenced = ref.getEReferenceType();
		String type = nonNull(referenced.getName());		
		String card = TextUtils.toEmfaticCardinality(ref, output.getMode());

		output.token(ref.getName()).w();
		output.token(":").w();
		output.token(type).token(card);
		// TODO: Check if this is String refType = ref.isContainment() ? "val" : "ref";
		output.token(";").newLine();
	}

	@Override
	protected List<Resource> getElements(File f) throws IOException {
		throw new UnsupportedOperationException();
	}


}
