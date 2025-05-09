package modelmate.modelxglue.emfatic;

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
import org.eclipse.emf.ecore.ETypedElement;
import org.eclipse.emf.ecore.EcorePackage;
import org.eclipse.emf.ecore.resource.Resource;

import modelmate.modelxglue.emfatic.CodeXGlueOutput.Mode;
import modelmate.modelxglue.emfatic.CodeXGlueOutput.PieceOfCode;

public class ComputeEmfatic extends AbstractSyntaxPrinter<Resource> {
	

	@Override
	protected List<Resource> getElements(File f) throws IOException {
		throw new IllegalStateException();
	}
	
	@Override
	protected void convertToTokens(Resource r, CodeXGlueOutput output) {
		try(PieceOfCode c = output.start()) {
			for (EObject obj : r.getContents()) {
				if (obj instanceof EPackage) {
					convertRootPackage((EPackage) obj, output);
				}
			}
		}
	}
	
	/**
	 * This is intended to be called by clients which wants to generate Emfatic files outside ModelSet
	 */
	public static void toTokens(Resource r, CodeXGlueOutput output) {
		new ComputeEmfatic().convertToTokens(r, output);
	}
	
	protected void convertRootPackage(EPackage obj, CodeXGlueOutput output) {
		//@namespace(uri="AnURI", prefix="uri-name")
		//package ecore;
		convertNamespace(obj, output);
		output.token("package").w().token(obj.getName()).token(";").newLine();
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
			output.token(nonNull(l.getName())).w().token("=").w().token(Integer.toString(l.getValue())).token(";");
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
			token(";");
	}


	protected void convertNamespace(EPackage obj, CodeXGlueOutput output) {
		output.token("@").token("namespace").token("(").
			token("uri").token("=").stringToken(obj.getNsURI()).token(",").w().
			token("prefix").token("=").stringToken(obj.getNsPrefix()).token(")").
			newLine();
	}

	protected void convertPackage(EPackage pkg, CodeXGlueOutput output) {
		convertNamespace(pkg, output);
		output.token("package").w().token(pkg.getName()).w().token("{").newLine().indent();
			convertPackageContents(pkg, output);
		output.unindent().token("}").newLine();
	}

	// (abstract?) class A { }
	protected void convertClass(EClass c, CodeXGlueOutput output) {
		convertClassHeader(c, output);
		output.token("{").newLine().indent();
		convertClassContents(c, output);
		output.unindent().token("}").newLine();
	}


	protected void convertClassHeader(EClass c, CodeXGlueOutput output) {
		if (c.isAbstract())
			output.token("abstract").w();
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
		String type = toEmfaticType(dt);
		String card = applyMode(output.mode, toEmfaticCardinality(attr));

		output.token("attr").w();
		output.token(type);
		output.token(card).w();
		output.token(attr.getName());
		output.token(";");
		output.newLine();
	}

	protected void convertReference(EReference ref, CodeXGlueOutput output) {
		EClass referenced = ref.getEReferenceType();
		// TODO: This needs to check whether this is an imported package or a subpackage...
		
		String referencedName = nonNull(referenced.getName());
		String refType = ref.isContainment() ? "val" : "ref";
		String card = applyMode(output.mode, toEmfaticCardinality(ref));
		
		output.token(refType).w();
		output.token(referencedName);
		output.token(card).w();
		output.token(ref.getName());
		output.token(";");
		output.newLine();		
	}

	protected String toEmfaticType(EDataType dt) {
		if (dt instanceof EEnum) {
			EEnum e = (EEnum) dt;
			// FIXME: Todo check, packages
			return nonNull(e.getName());
		}
		
		if (dt == EcorePackage.Literals.EBOOLEAN)
			return "boolean";
		else if (dt == EcorePackage.Literals.EBOOLEAN_OBJECT) {
			return "Boolean";
		} else if (dt == EcorePackage.Literals.EBYTE) {
			return "byte";
		} else if (dt == EcorePackage.Literals.EBYTE_OBJECT) {
			return "Byte";
		} else if (dt == EcorePackage.Literals.ECHAR) {
			return "char";
		} else if (dt == EcorePackage.Literals.ECHARACTER_OBJECT) {
			return "Character";
		} else if (dt == EcorePackage.Literals.EDOUBLE) {
			return "double";
		} else if (dt == EcorePackage.Literals.EDOUBLE_OBJECT) {
			return "Double";
		} else if (dt == EcorePackage.Literals.EINT) {
			return "int";
		} else if (dt == EcorePackage.Literals.EINTEGER_OBJECT) {
			return "Integer";
		} else if (dt == EcorePackage.Literals.ELONG) {
			return "long";
		} else if (dt == EcorePackage.Literals.ELONG_OBJECT) {
			return "Long";
		} else if (dt == EcorePackage.Literals.ESHORT) {
			return "short";
		} else if (dt == EcorePackage.Literals.ESHORT_OBJECT) {
			return "Short";
		} else if (dt == EcorePackage.Literals.EDATE) {
			return "Date";
		} else if (dt == EcorePackage.Literals.ESTRING) {
			return "String";
		} else if (dt == EcorePackage.Literals.EJAVA_OBJECT) {
			return "Object";
		} else if (dt == EcorePackage.Literals.EJAVA_CLASS) {
			return "Class";
		} else if (dt == EcorePackage.Literals.EOBJECT) {
			// This doesn't look correct, because EObject is an EClass
			return "EObject";
		} else if (dt == EcorePackage.Literals.ECLASS) {
			// This doesn't look correct, because EClass is an EClass
			return "EClass";
		}
		
		String typeName = dt.getInstanceTypeName();
		String name = dt.getName();
		if (typeName != null) {
			if ("org.eclipse.emf.ecore.EObject".equals(typeName))
				return "EObject";
			if ("org.eclipse.emf.ecore.EClass".equals(typeName))
				return "EClass";
			
			if (typeName.startsWith("org.eclipse.emf.ecore")) {
				String[] parts = typeName.split("\\.");			
				return "ecore." + parts[parts.length - 1];
			}
			// FIXME: Not sure about this
			return typeName;
		} else if ("String".equals(name)) {
			return "String";
		} else if ("Integer".equals(name)) {
			return "Integer";			
		} else if ("Double".equals(name)) {
			return "Double";			
		} else if ("Boolean".equals(name)) {
			return "Boolean";			
		} else {
			if (dt.eIsProxy())
				throw new InvalidModelException("Proxy");
			
			throw new UnsupportedOperationException(dt.toString());
		}
		
	}

	protected String toEmfaticCardinality(ETypedElement t) {
		if (t.getLowerBound() == 0 && t.getUpperBound() == 1)
			return "[ ? ]"; // Could be empty string
		else if (t.getLowerBound() == 0 && t.getUpperBound() == -1)
			return "[ * ]";
		else if (t.getLowerBound() == 1 && t.getUpperBound() == -1)
			return "[ + ]";
		else if (t.getLowerBound() == 1 && t.getUpperBound() == 1)
			return "[ 1 ]";
		else if (t.getLowerBound() >= 0 && t.getUpperBound() == -1)
			return "[ " + t.getLowerBound() + " .. * ]";
		else if (t.getLowerBound() >= 0 && t.getUpperBound() == -2)
			return "[ " + t.getLowerBound() + " .. ? ]";
		else if (t.getLowerBound() >= 0 && t.getLowerBound() == t.getUpperBound())
			return "[ " + t.getLowerBound() + " ]";
		else if (t.getLowerBound() >= 0 && t.getUpperBound() > 0)
			return "[ " + t.getLowerBound() + " .. " + t.getUpperBound() + " ]";
		throw new UnsupportedOperationException(t.toString());
	}

	protected String applyMode(Mode mode, String cardinalityString) {
		return mode == Mode.FULL ? cardinalityString.replace(" ", "") : cardinalityString;
	}
	
}
