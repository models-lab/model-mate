package modelmate.modelxglue;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.emf.ecore.EAttribute;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EDataType;
import org.eclipse.emf.ecore.EEnum;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EReference;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;

import modelmate.modelxglue.classdiagram.GenerateClassDiagramDataset;
import modelmate.modelxglue.emfatic.AbstractSyntaxPrinter.InvalidModelException;
import modelmate.modelxglue.emfatic.CodeXGlueOutput;
import modelmate.modelxglue.emfatic.CodeXGlueOutput.Mode;
import modelmate.modelxglue.emfatic.ComputeEmfatic;

public class GenerateClassDiagramTestCases {

	public static void main(String[] args) throws IOException {		
		String root = args[0];
		String file = root + File.separator + "X.json";
		String transformFile = root + File.separator + "transformed.json";

		ObjectMapper objectMapper = new ObjectMapper();
		JsonNode rootNode = objectMapper.readTree(new File(file));

		Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put("*", new XMIResourceFactoryImpl());

		List<TestElement> result = new ArrayList<>();
		ArrayNode list = (ArrayNode) rootNode;
		for (JsonNode jsonNode : list) {
			String id = jsonNode.get("ids").textValue();
			String xmiPath = jsonNode.get("xmi_path").textValue();
			
			Model m;
			if (jsonNode.has("xmi_path")) {
				//String xmiPath = jsonNode.get("xmi_path").textValue();
				xmiPath = root + File.separator + xmiPath;
				m = Model.fromFile(id, xmiPath);
				System.out.println("Processing " + xmiPath);
			} else {
				String xmi = jsonNode.get("xmi").textValue();
				m = Model.fromContent(id, xmi);
			}

			try {
				String owner = jsonNode.get("owner").textValue();
				String targetFeatureName = jsonNode.get("target").textValue();
				//String emfatic = new EmfaticTransformerCutSoon(owner, targetFeatureName).generate(m);
				//String emfatic = new EmfaticTransformer(owner, targetFeatureName).generate(m);

				System.out.println("Finding " + owner);
				String emfatic = new EmfaticTransformerAll(owner, targetFeatureName).generate(m);
				System.out.println(emfatic);
				result.add(new TestElement(id, owner, targetFeatureName, emfatic));
				
			} catch (InvalidModelException e) {
				e.printStackTrace();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}

		objectMapper.writer().writeValue(new FileWriter(transformFile), result);
	}
	
	public static class EmfaticTransformer extends GenerateClassDiagramDataset  {

		private final String owner;
		private final String targetFeatureName;
		private boolean generatingTargetFeature = false;
		
		public EmfaticTransformer(String owner, String targetFeatureName) {
			this.owner = owner;
			this.targetFeatureName = targetFeatureName;
		}
		
		public String generate(Model m) {
			FragmentedCodeXGlueOutput output = new FragmentedCodeXGlueOutput(Mode.LINE);
			convertToTokens(m.getResource(), output);
			return output.toString();
		}
		

		@Override
		protected void convertClassContents(EClass c, CodeXGlueOutput output) {
			if (! generatingTargetFeature ) {
				super.convertClassContents(c, output);
				return;
			}
			
			// Same as in super but skipping the feature
			for (EStructuralFeature feature : c.getEStructuralFeatures()) {
				// Actually, the feature doesn't exist in the model, so this doesn't make any sense
				//if (targetFeatureName.equals(feature.getName()))
				//	continue;
				if (feature instanceof EAttribute) {
					convertAttribute((EAttribute) feature, output);
				} else {
					convertReference((EReference) feature, output);
				}
			}
			
			((FragmentedCodeXGlueOutput) output).setIgnoreGeneration();
		}
		
		@Override
		protected void convertPackageContents(EPackage obj, CodeXGlueOutput output) {
			for (EPackage pkg : obj.getESubpackages()) {
				convertPackage(pkg, output);
			}
			
			EClass ownerClass = null;
			for (EClassifier classifier : obj.getEClassifiers()) {
				if (classifier instanceof EClass) {
					if (owner.equals(classifier.getName())) {
						ownerClass = (EClass) classifier;
						continue;
					}
					convertClass((EClass) classifier, output);
				} else if (classifier instanceof EEnum) {
					convertEnum((EEnum) classifier, output);
				} else if (classifier instanceof EDataType) {
					convertDataType((EDataType) classifier, output);				
				}
			}
			
			if (ownerClass != null) { 
				// This assumes that class names are unique among packages
				generatingTargetFeature = true;
				convertClass(ownerClass, output);
			}			
		}		
	}

	public static class EmfaticTransformerAll extends GenerateClassDiagramDataset  {

		private final String owner;
		private final String targetFeatureName;
		private EClass foundClass;
		
		private boolean generatingTargetFeature = false;
		
		public EmfaticTransformerAll(String owner, String targetFeatureName) {
			this.owner = owner;
			this.targetFeatureName = targetFeatureName;
		}
		
		public String generate(Model m) {
			FragmentedCodeXGlueOutput output = new FragmentedCodeXGlueOutput(Mode.LINE);
			convertToTokens(m.getResource(), output);
			return output.toString();
		}
		
		@Override
		protected void convertRootPackage(EPackage obj, CodeXGlueOutput output) {
			super.convertRootPackage(obj, output);
			generatingTargetFeature = true;
			convertClass(foundClass, output);
		}
		

		@Override
		protected void convertClassContents(EClass c, CodeXGlueOutput output) {
			super.convertClassContents(c, output);
			if (generatingTargetFeature ) {
				((FragmentedCodeXGlueOutput) output).setIgnoreGeneration();
			}
		}
		
		@Override
		protected void convertPackageContents(EPackage obj, CodeXGlueOutput output) {
			for (EPackage pkg : obj.getESubpackages()) {
				convertPackage(pkg, output);
			}
			
			for (EClassifier classifier : obj.getEClassifiers()) {
				if (classifier instanceof EClass) {
					if (owner.equals(classifier.getName())) {
						foundClass = (EClass) classifier;
						continue;
					}
					convertClass((EClass) classifier, output);
				} else if (classifier instanceof EEnum) {
					convertEnum((EEnum) classifier, output);
				} else if (classifier instanceof EDataType) {
					convertDataType((EDataType) classifier, output);				
				}
			}
		}		
	}

	public static class EmfaticTransformerCutSoon extends ComputeEmfatic  {

		private final String owner;
		private final String targetFeatureName;
		private boolean generatingTargetFeature = false;
		
		public EmfaticTransformerCutSoon(String owner, String targetFeatureName) {
			this.owner = owner;
			this.targetFeatureName = targetFeatureName;
		}
		
		public String generate(Model m) {
			FragmentedCodeXGlueOutput output = new FragmentedCodeXGlueOutput(Mode.LINE);
			convertToTokens(m.getResource(), output);
			return output.toString();
		}
		
		
		@Override
		protected void convertClassContents(EClass c, CodeXGlueOutput output) {
			if (! owner.equals(c.getName()) ) {
				super.convertClassContents(c, output);
				return;
			}
			
			((FragmentedCodeXGlueOutput) output).setIgnoreGeneration();
		}
		
		
		/*
		@Override
		protected void convertClassContents(EClass c, CodeXGlueOutput output) {
			if (! generatingTargetFeature ) {
				super.convertClassContents(c, output);
				return;
			}
			
			// Same as in super but skipping the feature
			for (EStructuralFeature feature : c.getEStructuralFeatures()) {
				if (targetFeatureName.equals(feature.getName()) && feature.getEContainingClass().getName().equals(owner)) {
					generatingTargetFeature = true;
					break;
				}

				if (feature instanceof EAttribute) {
					convertAttribute((EAttribute) feature, output);
				} else {
					convertReference((EReference) feature, output);				
				}
			}
			
			((FragmentedCodeXGlueOutput) output).setIgnoreGeneration();
		}
		*/

	}

	
	public static class FragmentedCodeXGlueOutput extends CodeXGlueOutput {
		private String result = null;
		
		public FragmentedCodeXGlueOutput(Mode mode) {
			super(mode);
		}

		public void setIgnoreGeneration() {
			result = this.toString();
		}
		
		@Override
		public String toString() {
			if (result == null)
				return super.toString();
			else
				return result;
		}
		
	}
}
