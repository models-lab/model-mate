package modelmate.modelxglue;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;

public class Main {

    public static void main(String[] args) throws IOException, ParseException {
        // set up emf
        Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap( ).put("*", new XMIResourceFactoryImpl());

        // Options
        Options options = setUpOptions();
        CommandLineParser parser = new DefaultParser();
        CommandLine cmd = parser.parse(options, args);
        
        String root = cmd.getOptionValue("root");
 
        ObjectMapper objectMapper = new ObjectMapper();
        	
    	String file = root + File.separator + "X.json";
    	String transformFile = root + File.separator + "transformed.json";
    	
    	JsonNode rootNode = objectMapper.readTree(new File(file));

    	
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
    		
    		if (isValid(m)) {
    			result.add(jsonNode);
    		} else {
    			System.out.println("Filter out because no validate: " + id);
    		}
    		
    		m.getResource().unload();
		}
    	
    	objectMapper.writer().writeValue(new FileWriter(transformFile), result);
    
    }
    

    private static boolean isValid(Model m) {    	
    	TreeIterator<EObject> it = m.getResource().getAllContents();
    	while (it.hasNext()) {
    		EObject obj = it.next();
    		if (obj instanceof EStructuralFeature) {
    			if (((EStructuralFeature) obj).getEType() == null)
    				return false;

    			if (((EStructuralFeature) obj).getName() == null)
    				return false;
    		}
    		
    		if (obj instanceof EClassifier) {
    			if (((EClassifier) obj).getName() == null)
    				return false;
    		}
    		
    	}
    	return true;
	}

	private static Options setUpOptions(){
        Options options = new Options();

        Option rootFolder = new Option("r", "root", true,
                "Root folder");
        options.addOption(rootFolder);
        return options;
    }

}