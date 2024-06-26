package modelmate.integration.generators;

// https://github.com/microsoft/CodeXGLUE/tree/main/Code-Code/CodeCompletion-token
public class CodeXGlueOutput {

	public static enum Mode {
		TOKEN,
		LINE,
		FULL
	}
	
	final StringBuilder builder = new StringBuilder();
	final Mode mode;
	int indent = 0;
	
	public CodeXGlueOutput(Mode mode) {
		this.mode = mode;
	}
	
	public String getText() {
		return this.builder.toString();
	}
	
	public CodeXGlueOutput w() {
		if (mode == Mode.FULL)
			builder.append(" ");
		return this;
	}

	public void merge(CodeXGlueOutput output) {
		builder.append(output.builder);
	}

	public CodeXGlueOutput newLine() {
		if (mode == Mode.LINE) {
			builder.append(" <EOL>");
		} else if (mode == Mode.FULL) {
			builder.append("\n");
		}
		return this;
	}
	
	public CodeXGlueOutput indent() {
		indent++;
		return this;
	}

	public CodeXGlueOutput unindent() {
		indent--;
		return this;
	}
	public PieceOfCode start() {
		if (mode != Mode.FULL)
			builder.append("<s>");
		return new PieceOfCode(this);
	}

	public PieceOfCode startWithNoEnd() {
		return start().avoidEnd();
	}
	
	public CodeXGlueOutput token(String string) {
		if (string.isEmpty())
			return this;
		
		doIndentIfNeeded();
		
		if (mode != Mode.FULL)
			builder.append(" ");
		builder.append(string);
		return this;
	}

	public CodeXGlueOutput stringToken(String str) {
		doIndentIfNeeded();

		if (mode != Mode.FULL)
			builder.append(" ");
		builder.append("\"");
		builder.append(str);
		builder.append("\"");
		return this;
	}

	private void doIndentIfNeeded() {
		int size = builder.length();
		if (mode == Mode.FULL && size > 0) {
			char last = builder.charAt(size - 1);
			if (last == '\n') {
				for(int i = 0; i < indent; i++)
					builder.append("\t");					
			}
		}
	}		
	

	public static class PieceOfCode implements AutoCloseable {

		private CodeXGlueOutput output;
		private boolean endOnClose = true;

		public PieceOfCode(CodeXGlueOutput output) {
			this.output = output;
		}

		public PieceOfCode avoidEnd() {
			this.endOnClose = false;
			return this;
		}

		@Override
		public void close() {
			if (output.mode != Mode.FULL && endOnClose) {
	 			output.builder.append(" ");
				output.builder.append("</s>\n");
			}
		}
	}

}