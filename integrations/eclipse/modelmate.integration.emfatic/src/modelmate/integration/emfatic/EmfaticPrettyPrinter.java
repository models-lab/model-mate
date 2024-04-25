package modelmate.integration.emfatic;

import modelmate.integration.language.PrettyPrinter;

public class EmfaticPrettyPrinter implements PrettyPrinter {

	@Override
	public String prettyPrint(String fragment) {
		String indented = doIndentation(fragment);
		String normalized = indented.replaceAll("\\s\\}", "}");
		
		normalized = normalized.replaceAll("\\s\\;", ";");
		normalized = normalized.replace("[ * ]", "[*]");
		normalized = normalized.replace("[ 1 ]", "[1]");
		return normalized;
	}
	
	public String doIndentation(String input) {
        String[] lines = input.split("\n");
        StringBuilder indentedText = new StringBuilder();

        int indentationLevel = 0;
        for (String line : lines) {
            if (line.contains("}")) {
                indentationLevel--;
            }
            appendIndentation(indentedText, indentationLevel);
            indentedText.append(line).append("\n");
            if (line.contains("{")) {
                indentationLevel++;
            }
        }

        return indentedText.toString();
    }

    private void appendIndentation(StringBuilder builder, int level) {
        for (int i = 0; i < level; i++) {
            builder.append("    ");
        }
    }


}
