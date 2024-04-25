package modelmate.dataset;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.concurrent.Callable;

import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.resource.Resource;

import mar.indexer.common.configuration.ModelLoader;
import mar.validation.AnalyserRegistry;
import mar.validation.ResourceAnalyser.Factory;
import modelset.database.MarAnalysisFileProvider;
import modelset.process.DuplicationDatabase;
import modelset.process.textual.AbstractSyntaxPrinter;
import modelset.process.textual.CodeXGlueOutput;
import modelset.process.textual.CodeXGlueOutput.Mode;
import modelset.process.textual.ComputeEmfatic;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "generate-ecore-dataset", mixinStandardHelpOptions = true, description = "Generates an Xtext dataset")
public class GenerateEcoreDataset extends AbstractSyntaxPrinter<Resource> implements Callable<Integer> {
	
    @Option(required = true, names = { "-r", "--repo-data" }, description = "Data repository folder")
    private File repoRoot;

    @Option(required = true, names = { "-d", "--db" }, description = "Crawler database folder")
    private File crawlerDb;

    @Option(required = true, names = { "-o", "--output" }, description = "Output file for the dataset")
    private File output;

    @Option(required = true, names = { "-m", "--mode" }, description = "Mode: token, line, full")
    private String modeStr;

    @Option(required = false, names = { "--dup" }, description = "Duplication database")
    private File duplicationDbFile = null;

    @Option(required = false, names = { "--shuffle-classes" }, description = "Shuffle or not")
    private double shuffleClasses = -1;

    @Option(required = false, names = { "--shuffle-features" }, description = "Shuffle or not")
    private double shuffleFeatures = -1;

    public static void main(String[] args) {
        int exitCode = new CommandLine(new GenerateEcoreDataset()).execute(args);
        System.exit(exitCode);
    }

	@Override
	public Integer call() throws Exception {
		Mode mode = getMode(modeStr);

		DuplicationDatabase dupDb = null;
		if (duplicationDbFile != null) {
			dupDb = new DuplicationDatabase(duplicationDbFile);
		}

		Factory factory = AnalyserRegistry.INSTANCE.getFactory("ecore");
		factory.configureEnvironment();
		
		MarAnalysisFileProvider fileProvider = new MarAnalysisFileProvider(crawlerDb, repoRoot, "ecore");
		
		generateTokenization(fileProvider, output, mode, dupDb);
	
		return 0;
	}
	
	
	@Override
	protected List<Resource> getElements(File f) throws IOException {
		if (shuffleFeatures > 0 || shuffleClasses > 0) {
			List<Resource> result = shuffle(f);
			System.out.println("Number of shuffles: " + result.size());
			return result;
		} else {
			Resource r = ModelLoader.DEFAULT.load(f);
			return Collections.singletonList(r);
		}
	}
	
	@Override
	protected void unload(Resource r) {
		r.unload();
	}
	
	private List<Resource> shuffle(File f) throws IOException {
		Resource r = ModelLoader.DEFAULT.load(f);
		Content content = getResourceContents(r);
		r.unload();
		
		int numClasses  = (int) Math.ceil(content.classes.size() * shuffleClasses);
		int numFeatures = (int) Math.ceil(content.features.size() * shuffleFeatures);

		numClasses  = Math.min(numClasses, 2);
		numFeatures = Math.min(numClasses, 2);
		
		
		List<Resource> result = new ArrayList<>();
		Random random = new Random(123);
		for (int i = 0; i < numClasses; i++) {
			for(int j = 0; j < numClasses; j++) {
				Resource r1 = ModelLoader.DEFAULT.load(f);
				Content c1 = getResourceContents(r1);
				
				for (EPackage ePackage : c1.packages) {
					List<EClassifier> classifiers = new ArrayList<EClassifier>(ePackage.getEClassifiers());
					Collections.shuffle(classifiers, random);
					ePackage.getEClassifiers().clear();
					ePackage.getEClassifiers().addAll(classifiers);
				}

				for(int k = 0; k < numFeatures; k++) {
					EClass eClass = c1.classes.get(random.nextInt(c1.classes.size()));

					List<EStructuralFeature> features = new ArrayList<>(eClass.getEStructuralFeatures());
					Collections.shuffle(features, random);
					eClass.getEStructuralFeatures().clear();
					eClass.getEStructuralFeatures().addAll(features);
				}
				
				result.add(r1);
			}
		}
		
		return result;
	}

	private Content getResourceContents(Resource r) {
		Content c = new Content();
		TreeIterator<EObject> it = r.getAllContents();
		while (it.hasNext()) {
			EObject o = it.next();
			if (o instanceof EClass) {
				c.classes.add((EClass) o);
			} else if (o instanceof EStructuralFeature) {
				c.features.add((EStructuralFeature) o);
			} else if (o instanceof EPackage) {
				c.packages.add((EPackage) o);
			}
		}
		return c;
	}
	
	private static class Content {
		List<EClass> classes = new ArrayList<>();
		List<EPackage> packages = new ArrayList<>();
		List<EStructuralFeature> features = new ArrayList<>();
	}
	
	@Override
	protected void convertToTokens(Resource r, CodeXGlueOutput output) {
		ComputeEmfatic.toTokens(r, output);
	}


}
