package modelmate.modelxglue;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.Character.UnicodeScript;
import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.ENamedElement;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.github.pemistahl.lingua.api.Language;
import com.github.pemistahl.lingua.api.LanguageDetector;
import com.github.pemistahl.lingua.api.LanguageDetectorBuilder;

public class Main {

    public static void main(String[] args) throws IOException, ParseException {
        // set up emf
        Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap( ).put("*", new XMIResourceFactoryImpl());

        // Options
        Options options = setUpOptions();
        CommandLineParser parser = new DefaultParser();
        CommandLine cmd = parser.parse(options, args);

        String language = cmd.getOptionValue("language");
        
        System.out.println("Filtering with: \n\t " + "language: " + language+ "\n");
        
        String root = cmd.getOptionValue("root");
 
        ObjectMapper objectMapper = new ObjectMapper();
        	
    	String file = root + File.separator + "X.json";
    	String transformFile = root + File.separator + "transformed.json";
    	
    	JsonNode rootNode = objectMapper.readTree(new File(file));
    	
    	
    	Language lang = Language.valueOf(language.toUpperCase());
    	LanguageDetector detector = LanguageDetectorBuilder.
    			fromAllLanguages().
    			//withLowAccuracyMode().
    			build();

    	
    	Validator validator = new Validator();
    	List<JsonNode> result = new ArrayList<>();
    	ArrayNode list = (ArrayNode) rootNode;
    	for (JsonNode jsonNode : list) {
    		String id = jsonNode.get("ids").textValue();
    		
    		Model m;
    		if (jsonNode.has("xmi_path")) {
    			String xmiPath = root + File.separator + jsonNode.get("xmi_path").textValue();
    			m = Model.fromFile(id, xmiPath);
    		} else {
    			String xmi = jsonNode.get("xmi").textValue();
    			m = Model.fromContent(id, xmi);
    		}
    		
			//if (id.contains("d0440e9e-445b-462a-9edb-02d38ad3577c")) {
			//	System.out.println(id);
			//}
			
    		if (validator.isValid(m, lang, detector)) {
    			result.add(jsonNode);
    		} else {
    			System.out.println("Filter out because language: " + id);
    		}
    		
    		m.getResource().unload();
		}
    	
    	objectMapper.writer().writeValue(new FileWriter(transformFile), result);
    
    }
    
    public static class Validator {
    
	    private final static int MIN_OCC = 5;
	    private final static float MIN_CONFIDENCE = 0.85f;
	
	    private boolean onlyIDChars = true;
	    
	    public boolean isValid(Model m, Language target, LanguageDetector language) {    	
	    	int count = 0;
	    	TreeIterator<EObject> it = m.getResource().getAllContents();
	    	while (it.hasNext()) {
	    		EObject obj = it.next();
	    		if (obj instanceof ENamedElement) {
	    			ENamedElement e = (ENamedElement) obj;
	    			String v = e.getName();
	    			if (v == null)
	    				continue;
	    			SortedMap<Language, Double> map = language.computeLanguageConfidenceValues((String) v);
    				if (map.containsKey(target) && map.get(target) > MIN_CONFIDENCE) {
    					count++;
    				}
    				
    				if (invalidChars((String) v)) {
    					return false;
    				}
	    		}
	    		
    			if (count >= MIN_OCC) { 
    				return true;
    			}
    			
	    		/*
	    		EStructuralFeature f = obj.eClass().getEStructuralFeature("name");
	    		if (f instanceof EAttribute && ((EAttribute) f).getEAttributeType().getName().contains("String")) {
	    			Object v = obj.eGet(f);
	    			if (v instanceof String && !(((String) v).trim().isEmpty())) {
	    				SortedMap<Language, Double> map = language.computeLanguageConfidenceValues((String) v);
	    				if (map.containsKey(target) && map.get(target) > MIN_CONFIDENCE) {
	    					count++;
	    				}
	    				
	    				if (invalidChars((String) v)) {
	    					return false;
	    				}
	    			}
	
	    			if (count >= MIN_OCC) { 
	    				return true;
	    			}
	    		}
	    		*/
	    	}
	    	return false;
		}
	
		private boolean invalidChars(String v) {
			char[] array = v.toCharArray();
			for (int i = 0; i < array.length; i++) {
				char c = array[i];
				UnicodeScript x = Character.UnicodeScript.of(c);
				if (x == Character.UnicodeScript.LATIN || x == Character.UnicodeScript.COMMON)
					return false;

				if (onlyIDChars && ! Character.isJavaIdentifierPart(c)) {
					return false;
				}
			}
			return true;
		}
    }

	private static Options setUpOptions(){
        Options options = new Options();

        Option lang = new Option("language", "language", true,
                "Allowed language");
        lang.setOptionalArg(true);
        options.addOption(lang);
        
        Option rootFolder = new Option("r", "root", true,
                "Root folder");
        options.addOption(rootFolder);
        return options;
    }

}