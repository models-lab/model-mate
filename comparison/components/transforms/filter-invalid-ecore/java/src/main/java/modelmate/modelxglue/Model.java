package modelmate.modelxglue;

import java.io.IOException;

import org.apache.commons.io.IOUtils;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;

public class Model {
	private Resource resource;
	private String id;
	
    public Model(String id, Resource resource) {
        this.id = id;
    	this.resource = resource;
    }

    public String getId() {
		return id;
	}
    
    public Resource getResource() {
        return resource;
    }
    
	public static Model fromContent(String id, String content) throws IOException {
		ResourceSet rs = new ResourceSetImpl();
        Resource resource = rs.createResource(URI.createURI("uri"));
        resource.load(IOUtils.toInputStream(content), null);
        return new Model(id, resource);
	}


	public static Model fromFile(String id, String xmiPath) {
        ResourceSet rs = new ResourceSetImpl();
        Resource resource = rs.getResource(URI.createFileURI(xmiPath), true);
        return new Model(id, resource);
	}

}
