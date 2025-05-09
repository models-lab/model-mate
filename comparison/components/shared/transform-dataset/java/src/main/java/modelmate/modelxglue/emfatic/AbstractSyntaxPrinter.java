package modelmate.modelxglue.emfatic;

import java.io.File;
import java.io.IOException;
import java.util.List;

public abstract class AbstractSyntaxPrinter<T> {
	
	protected static enum Dataset {
		ECORE,
		UML
	}
		protected abstract List<T> getElements(File f) throws IOException;

	protected abstract void convertToTokens(T r, CodeXGlueOutput output);

	@SuppressWarnings("unused")
	protected
	static <T> T nonNull(T obj) {
		if (obj == null)
			throw new InvalidModelException("Null value");
		return obj;
	}

	public static class InvalidModelException extends RuntimeException {
		public InvalidModelException(String string) {
			super(string);
		}

		private static final long serialVersionUID = 5490556461546321329L;
		
	}
	

}
