package modelmate.integration.xtext.generate;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.antlr.runtime.ANTLRInputStream;
import org.antlr.runtime.Token;
import org.eclipse.xtext.XtextStandaloneSetup;
import org.eclipse.xtext.parser.antlr.Lexer;

import com.google.inject.Injector;

import modelmate.integration.generators.CodeXGlueOutput;
import modelmate.integration.generators.CodeXGlueOutput.Mode;
import modelmate.integration.generators.CodeXGlueOutput.PieceOfCode;

public class Generator {

	private static Injector injector = null;

	private static Injector getInjector() {
		if (injector == null) {
			injector = new XtextStandaloneSetup().createInjectorAndDoEMFRegistration();
		}
		return injector;
	}

	protected List<String> getTokens(String s) throws IOException {
		Lexer x = getInjector().getInstance(Lexer.class);
		x.setCharStream(new ANTLRInputStream(new ByteArrayInputStream(s.getBytes())));

		List<String> tokens = new ArrayList<String>();
		while (true) {
			Token t = x.nextToken();
			if (t == Token.EOF_TOKEN)
				break;
			tokens.add(t.getText());
		}

		return tokens;
	}

	public String toTokens(String s) {
		CodeXGlueOutput output = new CodeXGlueOutput(Mode.TOKEN);
		convertToTokens(s, output);
		return output.getText();
	}
	
	protected void convertToTokens(String s, CodeXGlueOutput output) {
		try (PieceOfCode c = output.startWithNoEnd()) {
			List<String> tokens = this.getTokens(s);
			for (String string : tokens) {
				String trimmed = string.trim();
				if (trimmed.equals("\n")) {
					output.newLine();
				} else if (trimmed.isEmpty()) {
					// TODO: We should imitate the kind of spaces
					output.w();
				} else if (trimmed.startsWith("//") || trimmed.startsWith("/*")) {
					// Ignore comments
				} else {
					// System.out.println("[" + string + "]");
					output.token(string);
				}
			}
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}

}
