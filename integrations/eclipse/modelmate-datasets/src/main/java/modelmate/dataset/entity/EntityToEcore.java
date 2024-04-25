package modelmate.dataset.entity;

import java.io.File;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;

import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EEnum;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EOperation;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EParameter;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.resource.Resource;

import com.google.common.base.Preconditions;

import mar.indexer.common.configuration.ModelLoader;
import mar.validation.IFileProvider;
import modelset.process.DuplicationDatabase;
import modelset.process.textual.AbstractSyntaxPrinter;
import modelset.process.textual.CodeXGlueOutput;
import modelset.process.textual.CodeXGlueOutput.Mode;
import modelset.process.textual.CodeXGlueOutput.PieceOfCode;

public class EntityToEcore extends AbstractSyntaxPrinter<Resource> {

	private boolean originalTypeStyle;

	/**
	 * 
	 * @param originalTypeStyle true to use List<Type> for multivalued or Type [*]
	 */
	public EntityToEcore(boolean originalTypeStyle) {
		this.originalTypeStyle = originalTypeStyle;
	}
	
	@Override
	public void generateTokenization(IFileProvider provider, File outputFile, Mode mode, DuplicationDatabase dupDb)
			throws SQLException, IOException {
		// TODO Auto-generated method stub
		super.generateTokenization(provider, outputFile, mode, dupDb);
	}

	@Override
	protected void unload(Resource r) {
		r.unload();
	}

	@Override
	protected List<Resource> getElements(File f) throws IOException {
		Resource r = ModelLoader.DEFAULT.load(f);
		return Collections.singletonList(r);
	}

	@Override
	protected void convertToTokens(Resource m, CodeXGlueOutput output) {
		try (PieceOfCode c = output.start()) {
			TreeIterator<EObject> it = m.getAllContents();
			while (it.hasNext()) {
				EObject obj = it.next();
				if (obj instanceof EPackage) {
					convertPackage((EPackage) obj, output);
					break;
				}
			}
		}
	}

	private void convertPackage(EPackage m, CodeXGlueOutput output) {
		output.token("package").w().token(toName(m.getName())).w();
		output.token("{").newLine();
		output.indent();

		for (EClassifier element : m.getEClassifiers()) {
			if (element instanceof EClass) {
				convertClass((EClass) element, output);
			} else if (element instanceof EPackage) {
				convertPackage((EPackage) element, output);
			}
		}

		output.unindent();
		output.token("}").newLine();
	}

	public void convertClass(EClass element, CodeXGlueOutput output) {
		output.token("entity").token(toName(element.getName())).w();

		if (element.getESuperTypes().size() > 0) {
			output.token("extends").w();
			output.token(toName(element.getESuperTypes().get(0).getName())).w();
		}
		output.token("{").newLine();
		output.indent();

		for (EStructuralFeature property : element.getEStructuralFeatures()) {
			// if (property.isAttribute())
			String name = property.getName();
			if (name == null || name.isEmpty())
				continue;

			EClassifier type = property.getEType();
			if (type == null)
				continue;

			// name=ValidID ':' type=JvmTypeReference;
			String typeName = toTypeName(type);
			if (typeName == null)
				continue;
			output.token(toName(name)).w().token(":").w();

			if (property.isMany() && originalTypeStyle) {
				output.token("List").token("<");
				output.token(typeName);
				output.token(">");
			} else if (property.isMany() && !originalTypeStyle) {
				output.token(typeName);
				output.token("[*]");	
			} else {
				output.token(typeName);
			}

			output.newLine();
		}

		for (EOperation operation : element.getEOperations()) {
			try {
				convertOperation(operation, output);
			} catch (IllegalArgumentException e) {
				// Ignore
			}
		}

		output.unindent();
		output.token("}").newLine();
	}

	private void convertOperation(EOperation operation, CodeXGlueOutput output) {
		String name = operation.getName();
		if (name == null || name.isEmpty())
			throw new IllegalArgumentException();

		EClassifier returnType = operation.getEType();
		if (returnType != null && toTypeName(returnType) == null)
			throw new IllegalArgumentException();

		for (EParameter parameter : operation.getEParameters()) {
			EClassifier type = parameter.getEType();
			if (type == null)
				throw new IllegalArgumentException();
			String typeName = toTypeName(type);
			String pname = parameter.getName();
			if (pname == null || pname.isEmpty())
				throw new IllegalArgumentException();
			if (typeName == null)
				throw new IllegalArgumentException();
		}

		output.token("op").w().token(name).token("(");
		String separator = null;
		for (EParameter parameter : operation.getEParameters()) {
			if (separator != null) {
				output.token(separator);
				output.w();
			}

			output.token(toTypeName(parameter.getEType()));
			output.w();
			output.token(toName(parameter.getName()));

			separator = ",";
		}
		output.token(")").w();

		if (returnType != null) {
			String returnTypeName = toTypeName(returnType);

			output.token(":").w();
			output.token(returnTypeName);
		}

		output.token("{").newLine();
		output.indent();
		output.token("// Default implementation").newLine();
		if (returnType != null)
			output.token("return").w().token(getDefaultValue(returnType)).token(";").newLine();
		output.unindent();
		output.token("}").newLine();

		/**
		 * 'op' name=ValidID '(' (params+=FullJvmFormalParameter (','
		 * params+=FullJvmFormalParameter)*)? ')' (':' type=JvmTypeReference)?
		 * body=XBlockExpression;
		 */
	}

	private String toTypeName(EClassifier type) {
		if (type instanceof EClass || type instanceof EEnum) {
			String name = type.getName();
			return toName(name);
		}
		String name = type.getName();
		if (name != null && name.matches("[A-Za-z]+")) {
			String low = name.toLowerCase();
			if (low.contains("int"))
				return "int";
			else if (low.contains("string")) 
				return "String";
			else if (low.contains("float"))
				return "float";
			else if (low.contains("double"))
				return "double";
			return name;
		}
		return null;
	}

	private String toName(String name) {
		// This is a trick to generate tokens...
		return toCamelCase(name).replaceAll("\\.", " . ");
	}

	public static String toCamelCase(String s) {
		Preconditions.checkArgument(s != null && !s.isEmpty());
		return s.replaceAll("\\s", "").replaceAll("-", "");
	}

	public String getDefaultValue(EClassifier returnType) {
		String name = toTypeName(returnType);
		// String name = returnType.getName();
		if (name.toLowerCase().contains("int"))
			return "0";
		if (name.toLowerCase().contains("string"))
			return "\"\"";
		if (name.toLowerCase().contains("float"))
			return "0.0";
		if (name.toLowerCase().contains("double"))
			return "0.0";

		return "null";
	}

}
