package modelmate.integration;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import kong.unirest.HttpResponse;
import kong.unirest.JsonNode;
import kong.unirest.JsonObjectMapper;
import kong.unirest.ObjectMapper;
import kong.unirest.Unirest;
import kong.unirest.json.JSONObject;

public class API {
	private String url;
	
	public API() {
		this("http://127.0.0.1:8080");
	}
	
	public API(String url) {
		this.url = url;
	}

	public SingleResult recommendFragment(String text) {
		Map<String, String> value = new HashMap<>();
		value.put("context", text);
		
		ObjectMapper mapper = new JsonObjectMapper();
		String json = mapper.writeValue(value);
		
		int max = 5;
		HttpResponse<JsonNode> jsonResponse = Unirest.post(getURL("recommend/fragment?max="+max))
				.header("Content-Type", "application/json")
				.accept("application/json")
				.body(json)
				.asJson();
		
		JSONObject obj = jsonResponse.getBody().getObject();
		// String result = obj.getJSONArray("fragment").;
		String result = obj.getString("text");
		System.out.println("Result: " + result);
		double time = Double.parseDouble(obj.getString("time"));
		
		return new SingleResult(result, time);
	}

	public SuggestionResult recommendNextToken(String text) {
		Map<String, String> value = new HashMap<>();
		value.put("context", text);
		
		ObjectMapper mapper = new JsonObjectMapper();
		String json = mapper.writeValue(value);
		
		int max = 5;
		HttpResponse<JsonNode> jsonResponse = Unirest.post(getURL("recommend/token?max="+max))
				.header("Content-Type", "application/json")
				.accept("application/json")
				.body(json)
				.asJson();
		
		JSONObject obj = jsonResponse.getBody().getObject();
		List<String> suggestions = new ArrayList<>();
		for(Object v : obj.getJSONArray("suggestions")) {
			suggestions.add(v.toString());
		}
		
		double time = Double.parseDouble(obj.getString("time"));
				
		return new SuggestionResult(suggestions, time);
	}
	
	public SuggestionResult recommendNextLine(String text) {
		Map<String, String> value = new HashMap<>();
		value.put("context", text);
		
		ObjectMapper mapper = new JsonObjectMapper();
		String json = mapper.writeValue(value);
		
		int max = 5;
		HttpResponse<JsonNode> jsonResponse = Unirest.post(getURL("recommend/line?max="+max))
				.header("Content-Type", "application/json")
				.accept("application/json")
				.body(json)
				.asJson();
		
		JSONObject obj = jsonResponse.getBody().getObject();
		List<String> suggestions = new ArrayList<>();
		for(Object v : obj.getJSONArray("suggestions")) {
			suggestions.add(v.toString());
		}
		
		double time = Double.parseDouble(obj.getString("time"));
				
		return new SuggestionResult(suggestions, time);
	}

	
	private String getURL(String str) {
		return url + "/" + str;
	}
	
	public static final class SingleResult {

		private final String text;
		private final double time;

		public SingleResult(String text, double time) {
			this.text = text;
			this.time = time;
		}
		
		public String getText() {
			return text;
		}
		
		public double getTime() {
			return time;
		}
		
		public String toNormalizedText() {
			return text.replace("<EOL>", "\n");
		}
		
	}
	
	public static final class SuggestionResult {

		private final List<String> suggestions;
		private final double time;

		public SuggestionResult(List<String> suggestions, double time) {
			this.suggestions = suggestions;
			this.time = time;
		}
		
		public List<String> getSuggestions() {
			return suggestions;
		}
		
		public double getTime() {
			return time;
		}
		
	}
}
