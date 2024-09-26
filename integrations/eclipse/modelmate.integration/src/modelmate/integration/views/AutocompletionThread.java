package modelmate.integration.views;

import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

import modelmate.integration.API;
import modelmate.integration.API.SingleResult;
import modelmate.integration.extensions.LanguageExtension;

public class AutocompletionThread extends Thread {
	private static long SLEEP_TIME = 2 * 1_000;

	private static AutocompletionThread instance;

	public static AutocompletionThread get() {
		if (instance == null) {
			instance = new AutocompletionThread();
			//instance.start();
		}
		return instance;
	}

	private long lastScheduling = 0;
	private boolean recommendationInProgress = false;

	private String lastFragment;
	
	@Override
	public void run() {
		while (true) {
			try {
				sleep(SLEEP_TIME);
				
				recommendationInProgress  = true;
				doRecommendation();
			} catch (InterruptedException e) {
				e.printStackTrace();
			} finally {				
				recommendationInProgress = false;
			}
		}
	}

	private void doRecommendation() {
		// TODO Auto-generated method stub
		
	}
	
	private List<ScheduledFuture<Void>> futures = new LinkedList<>();

	public void scheduleRecommendation(String fragment, LanguageExtension lang, Consumer<SingleResult> consumer) {
		if (Objects.equals(lastFragment, fragment))
			return;
		
		this.lastFragment = fragment;

		ListIterator<ScheduledFuture<Void>> it = futures.listIterator();
		while (it.hasNext()) {
			ScheduledFuture<Void> future = it.next();
			if (! future.isDone() && ! future.isCancelled()) {
				future.cancel(false);
				it.remove();
			}
		}
		
		ScheduledExecutorService executorService = Executors.newSingleThreadScheduledExecutor();
		ScheduledFuture<Void> resultFuture = executorService.schedule(new RecommendationTask(fragment, lang, consumer), SLEEP_TIME, TimeUnit.MILLISECONDS);
		
		futures.add(resultFuture);
	}
	
	private static class RecommendationTask implements Callable<Void> {

		private String fragment;
		private LanguageExtension lang;
		private Consumer<SingleResult> consumer;

		public RecommendationTask(String fragment, LanguageExtension lang, Consumer<SingleResult> consumer) {
			this.fragment = fragment;
			this.lang = lang;
			this.consumer = consumer;
		}

		@Override
		public Void call() throws Exception {
			String tokenized = lang.getTokenizer().tokenize(fragment);
			String url = lang.getModelMateServerURL();
			SingleResult result = new API(url).recommendFragment(tokenized);
			consumer.accept(result);
			return null;
		}
		
	}
	
}
