package modelmate.dataset.entity;

import java.io.File;
import java.io.IOException;
import java.lang.Character.UnicodeScript;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;

import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.uml2.uml.Class;
import org.eclipse.uml2.uml.DataType;
import org.eclipse.uml2.uml.Element;
import org.eclipse.uml2.uml.Enumeration;
import org.eclipse.uml2.uml.Model;
import org.eclipse.uml2.uml.NamedElement;
import org.eclipse.uml2.uml.Operation;
import org.eclipse.uml2.uml.Package;
import org.eclipse.uml2.uml.Parameter;
import org.eclipse.uml2.uml.PrimitiveType;
import org.eclipse.uml2.uml.Property;
import org.eclipse.uml2.uml.Type;

import com.google.common.base.Preconditions;

import mar.modelling.loader.ILoader;
import mar.validation.AnalyserRegistry;
import mar.validation.IFileInfo;
import mar.validation.IFileProvider;
import mar.validation.ResourceAnalyser.Factory;
import modelset.database.FilterAdapterFileProvider;
import modelset.database.MaxModelsFileProvider;
import modelset.database.ModelSetFileInfo;
import modelset.database.ModelSetFileProvider;
import modelset.process.DuplicationDatabase;
import modelset.process.textual.AbstractSyntaxPrinter;
import modelset.process.textual.CodeXGlueOutput;
import modelset.process.textual.CodeXGlueOutput.Mode;
import modelset.process.textual.CodeXGlueOutput.PieceOfCode;
import modelset.process.util.Utils;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "generate-entity-dataset", mixinStandardHelpOptions = true, description = "Generates a dataset")
public class GenerateEntityDataset implements Callable<Integer> {
	
    @Option(required = true, names = { "-r", "--repo-data" }, description = "Data repository folder")
    private File repoRoot;

    @Option(required = true, names = { "-d", "--db" }, description = "Crawler database folder")
    private File crawlerDb;

    @Option(required = true, names = { "-o", "--output" }, description = "Output file for the dataset")
    private File output;

    @Option(required = true, names = { "-t", "--type" }, description = "Dataset type")
    private String type;

    @Option(required = false, names = { "--dup" }, description = "Duplication database")
    private File duplicationDbFile = null;

    public static void main(String[] args) {
        int exitCode = new CommandLine(new GenerateEntityDataset()).execute(args);
        System.exit(exitCode);
    }

	@Override
	public Integer call() throws Exception {
		//Mode mode = getMode(modeStr);
		//if (mode != Mode.TOKEN)
		//	throw new IllegalArgumentException();
		Mode mode = Mode.LINE;
		
		DuplicationDatabase dupDb = null;
		if (duplicationDbFile != null) {
			dupDb = new DuplicationDatabase(duplicationDbFile);
		}

		// TODO: Find out how to use the MAR modelset
		//MarCrawlerFileProvider fileProvider = new MarCrawlerFileProvider(crawlerDb, repoRoot, "uml");
		//ModelSetFileProvider fileProvider = new ModelSetFileProvider(crawlerDb, repoRoot);
		IFileProvider fileProvider = Utils.loadDatabase(crawlerDb, repoRoot, "uml");
		
		//fileProvider = new MaxModelsFileProvider(fileProvider, 10);
		
		
		boolean originalTypeStyle = false;
		if (type.equals("uml")) {
			new FromUML(originalTypeStyle).generateTokenization(fileProvider, output, mode, dupDb);
		} else if (type.equals("ecore")) {
			Factory factory = AnalyserRegistry.INSTANCE.getFactory("ecore");
			factory.configureEnvironment();
			
			fileProvider = new FilterAdapterFileProvider(fileProvider, this::filterDomainModels);
			new EntityToEcore(originalTypeStyle).generateTokenization(fileProvider, output, mode, dupDb);			
		}
		return 0;
	}
	
	private boolean filterDomainModels(IFileInfo info) {
		if (info instanceof ModelSetFileInfo) {
			ModelSetFileInfo modelset = (ModelSetFileInfo) info;
			List<? extends String> tags = modelset.getMetadata().getValues("tags");
			return tags != null && tags.contains("domainmodel");
		}
		return false;
	}
	
	public static class FromUML extends AbstractSyntaxPrinter<Model> {
		private static final int MIN_OCC = 5;
		private boolean originalTypeStyle;
		
		public FromUML(boolean originalTypeStyle) {
			this.originalTypeStyle = originalTypeStyle;
		}
		
		@Override
		public void generateTokenization(IFileProvider provider, File outputFile, Mode mode,
				DuplicationDatabase dupDb) throws SQLException, IOException {
			// TODO Auto-generated method stub
			super.generateTokenization(provider, outputFile, mode, dupDb);
		}
		
		@Override
		protected void unload(Model t) {
			Resource r = t.eResource();
			if (r != null)
				r.unload();
		}
		
		boolean c = false;
		
		@Override
		protected List<org.eclipse.uml2.uml.Model> getElements(File f) throws IOException {
			//if (! f.getAbsolutePath().contains("data/_eUm1sAiAEeiTXI7G38ZLFQ.xmi"))
			//	return Collections.emptyList();
			
//			if ( f.getAbsolutePath().contains("data/_5qqkMCBlEeqqcaoAsxFIeg.xmi")) {
//				c = true;
//			} else {
//				if (c == false) {
//					return Collections.emptyList();
//				}
//			}
			
			
			Factory factory = AnalyserRegistry.INSTANCE.getFactory("uml");
			factory.configureEnvironment();
			ILoader loader = factory.newLoader();
			Resource r = loader.toEMF(f);
			TreeIterator<EObject> it = r.getAllContents();
			org.eclipse.uml2.uml.Model m = null;
			while (it.hasNext()) {
				EObject obj = it.next();
				if (obj instanceof org.eclipse.uml2.uml.Model) {
					org.eclipse.uml2.uml.Model pkg = (Model) obj;
					
					int count = 0;
					TreeIterator<EObject> inner = pkg.eAllContents();
					while (inner.hasNext()) {
						EObject obj2 = inner.next();

						if (obj2 instanceof NamedElement) {
							String name = ((NamedElement) obj2).getName();
							if (name != null && invalidChars(name))
								return Collections.emptyList(); // This has a non-western language
 						}
						
						if (obj2 instanceof org.eclipse.uml2.uml.Class) {
							count++;
						}
						if (count > MIN_OCC) {
							m = (org.eclipse.uml2.uml.Model) obj;
							break;
						}
					}
				}
			}
			
			if (m == null)
				return Collections.emptyList();
			return Collections.singletonList(m);
		}
		
		@Override
		protected void convertToTokens(Model m, CodeXGlueOutput output) {
			try(PieceOfCode c = output.start()) {
				convertPackage(m, output);
			}
		}

		private void convertPackage(Package m, CodeXGlueOutput output) {
			output.token("package").w().token(toName(m.getName())).w();
			output.token("{").newLine();
			output.indent();
			
			for (Element element : m.getOwnedElements()) {
				if (element instanceof Class) {
					convertClass((Class) element, output);
				} else if (element instanceof Package) {
					convertPackage((Package) element, output);
				}
			}
			
			output.unindent();
			output.token("}").newLine();
		}	

		public void convertClass(Class element, CodeXGlueOutput output) {
			output.token("entity").token(toName(element.getName())).w();
			
			if (element.getGenerals().size() > 0) {
				output.token("extends").w();
				output.token(toName(element.getGenerals().get(0).getName())).w();
			}
			output.token("{").newLine();
			output.indent();
			
			for (Property property : element.getOwnedAttributes()) {
				//if (property.isAttribute())
				String name = property.getName();
				if (name == null || name.isEmpty())
					continue;
				
				Type type = property.getType();
				if (type == null)
					continue;
				
				//name=ValidID ':' type=JvmTypeReference;
				String typeName = toTypeName(type);
				if (typeName == null)
					continue;
				output.token(toName(name)).w().token(":").w();
				
				if (property.isMultivalued() && originalTypeStyle) {
					output.token("List").token("<");
					output.token(typeName);
					output.token(">");
				} else if (property.isMultivalued() && !originalTypeStyle) {
					output.token(typeName);
					output.token("[*]");					
				} else {
					output.token(typeName);						
				}
				
				output.newLine();
			}
			
	
			for (Operation operation : element.getOwnedOperations()) {
				try {
					convertOperation(operation, output);
				} catch (IllegalArgumentException e) {
					// Ignore
				}
			}
			
			output.unindent();
			output.token("}").newLine();
		}

		private void convertOperation(Operation operation, CodeXGlueOutput output) {
			String name = operation.getName();
			if (name == null || name.isEmpty())
				throw new IllegalArgumentException();
			
			Type returnType = operation.getType();
			if (returnType != null && toTypeName(returnType) == null)
				throw new IllegalArgumentException();
				
			for (Parameter parameter : operation.getOwnedParameters()) {
				Type type = parameter.getType();
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
			for (Parameter parameter : operation.getOwnedParameters()) {
				if ("returnParameter".equals(parameter.getName()))
					continue;
				
				if (separator != null) {
					output.token(separator);
					output.w();
				}
					
				output.token(toTypeName(parameter.getType()));
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
			 	'op' name=ValidID '(' (params+=FullJvmFormalParameter (',' params+=FullJvmFormalParameter)*)? ')' (':' type=JvmTypeReference)?
				body=XBlockExpression;
			 */
		}

		private String toTypeName(Type type) {
			
			if (type instanceof Class || type instanceof Enumeration) {
				String name = type.getName();
				return toName(name);
			}
			if (type instanceof PrimitiveType) {
				URI uri = EcoreUtil.getURI(type);
				if (uri.fragment().contains("#//")) {
					String[] parts = uri.fragment().split("//");
					return parts[parts.length - 1];
				}
				
				String name = type.getName();
				return name;
			}
			
			String name = type.getName();
			if (name != null && name.matches("[A-Za-z]+"))
				return name;
			return null;
		}

		private String toName(String name) {
			// This is a trick to generate tokens...
			return toCamelCase(name).replaceAll("\\.", " . ");
		}
		
		public static String toCamelCase(String s) {
			Preconditions.checkArgument(s != null && ! s.isEmpty());
	        return s.replaceAll("\\s", "")
	        		.replaceAll("-", "");
			
			/*
	        StringBuilder camelCase = new StringBuilder();
	        boolean capitalizeNext = false;
	        
	        for (char c : s.toCharArray()) {
	            if (Character.isWhitespace(c)) {
	                capitalizeNext = true;
	            } else {
	                if (capitalizeNext) {
	                    camelCase.append(Character.toUpperCase(c));
	                    capitalizeNext = false;
	                } else {
	                    camelCase.append(Character.toLowerCase(c));
	                }
	            }
	        }
	        return camelCase.toString();
	        */
	    }


		public String getDefaultValue(Type returnType) {
			String name = toTypeName(returnType);
			//String name = returnType.getName();
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

	
	private static boolean invalidChars(String v) {
		char[] array = v.toCharArray();
		for (int i = 0; i < array.length; i++) {
			char c = array[i];
			UnicodeScript x = Character.UnicodeScript.of(c);
			if (x == Character.UnicodeScript.LATIN || x == Character.UnicodeScript.COMMON)
				return false;
					
		}
		return true;
	}

}
