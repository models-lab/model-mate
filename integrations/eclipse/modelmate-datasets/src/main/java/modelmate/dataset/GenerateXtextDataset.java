package modelmate.dataset;

import java.io.File;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;

import mar.models.xtext.XtextTokenizer;
import modelset.database.MarCrawlerFileProvider;
import modelset.process.DuplicationDatabase;
import modelset.process.textual.AbstractSyntaxPrinter;
import modelset.process.textual.CodeXGlueOutput;
import modelset.process.textual.CodeXGlueOutput.Mode;
import modelset.process.textual.CodeXGlueOutput.PieceOfCode;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "generate-xtext-dataset", mixinStandardHelpOptions = true, description = "Generates an Xtext dataset")
public class GenerateXtextDataset extends AbstractSyntaxPrinter<File> implements Callable<Integer> {
	
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

    public static void main(String[] args) {
        int exitCode = new CommandLine(new GenerateXtextDataset()).execute(args);
        System.exit(exitCode);
    }

	@Override
	public Integer call() throws Exception {
		Mode mode = getMode(modeStr);
		//if (mode != Mode.TOKEN)
		//	throw new IllegalArgumentException();
		
		DuplicationDatabase dupDb = null;
		if (duplicationDbFile != null) {
			dupDb = new DuplicationDatabase(duplicationDbFile);
		}

		MarCrawlerFileProvider fileProvider = new MarCrawlerFileProvider(crawlerDb, repoRoot, "xtext");
		
		generateTokenization(fileProvider, output, mode, dupDb);
	
		return 0;
	}
	
	@Override
	protected List<File> getElements(File f) throws IOException {
		return Collections.singletonList(f);
	}
	
	@Override
	protected void convertToTokens(File r, CodeXGlueOutput output) {
		XtextTokenizer tokenizer = new XtextTokenizer();
		try(PieceOfCode c = output.start()) {
			List<String> tokens = tokenizer.getTokens(r.getAbsolutePath());
			for (String string : tokens) {
				String trimmed = string.trim();
				if (string.matches("\n+")) {
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
