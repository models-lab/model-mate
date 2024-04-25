package modelmate.integration.emfatic;

import java.io.StringReader;

import org.eclipse.emf.emfatic.core.lang.gen.parser.ExtEmfaticParserTokenManager;
import org.eclipse.emf.emfatic.core.lang.gen.parser.ExtSimpleCharStream;
import org.eclipse.emf.emfatic.core.lang.gen.parser.Token;

import modelmate.integration.language.Tokenizer;

public class EmfaticTokenizer implements Tokenizer {


	@Override
	public String tokenize(String fragment) {
		String result =  preprocessLine(fragment);
		System.out.println(result);
		return result;
	}

	private static enum TokenizingStates {
		NORMAL,
		IN_NAMESPACE
	}
	
	private String preprocessToken(String text) {
		StringReader reader = new StringReader(text);
		ExtSimpleCharStream stream = new ExtSimpleCharStream(reader);
		ExtEmfaticParserTokenManager tokenManager = new ExtEmfaticParserTokenManager(stream);

		StringBuffer buffer = new StringBuffer();
		buffer.append("<s>");
		
		TokenizingStates state = TokenizingStates.NORMAL;
		
		while (true) {
			Token token = tokenManager.getNextToken();
			String tokenText = token.image;
			
			if (token.kind == ExtEmfaticParserTokenManager.EOF)
				break;
			
			if (state == TokenizingStates.NORMAL) {
				if (token.kind == ExtEmfaticParserTokenManager.ID && tokenText.equals("namespace"))
					state = TokenizingStates.IN_NAMESPACE;
			} else if (state == TokenizingStates.IN_NAMESPACE) {
				if (token.kind == ExtEmfaticParserTokenManager.RPAREN)
					state = TokenizingStates.NORMAL;
				else if (token.kind == ExtEmfaticParserTokenManager.STRING_LITERAL) {
					tokenText = "<URIPRE>";
				}
			}
			
			buffer.append(" " + tokenText);
		}
		
		return buffer.toString();
	}

	private String preprocessLine(String text) {
		text = text.
				replaceAll("(\r\n|\r|\n){2,}", "\n").
				replace("\n", " <EOL>");
		String byToken = preprocessToken(text); 
		return byToken.replace("< EOL >", "<EOL>");
	}

}
