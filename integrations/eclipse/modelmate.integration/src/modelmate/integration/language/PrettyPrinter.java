package modelmate.integration.language;

public interface PrettyPrinter {

	static PrettyPrinter EMPTY = new PrettyPrinter() {

		@Override
		public String prettyPrint(String fragment) {
			return fragment;
		}
		
	};

	String prettyPrint(String fragment);

}
